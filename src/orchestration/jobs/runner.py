"""D-08 §11 — `plan · trigger · run · resume · status · history`. OR-9…OR-27.

★ **No method on this surface returns an analytical value.** If one ever does,
OR-1 has been broken — and `tests_src/test_orchestration_b6.py` asserts it.

★★ **OR-16: partial success is failure.** A run where some jobs succeeded and
some failed is `INCOMPLETE`, and **INCOMPLETE never produces a human-facing
artifact** — *the two real incidents in this repo both came from a downstream
consumer treating a degraded upstream as usable.*
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from src.orchestration.contracts.manifest import (
    JobRun, RunManifest, RunOutcome, new_run_id,
)
from src.orchestration.errors import (
    BoundaryError, ManifestMissingError, RunIncompleteError,
)
from src.orchestration.jobs.graph import JobGraph
from src.orchestration.policy.budget import Budgets
from src.orchestration.policy.retry import RetryPolicy
from src.orchestration.schedule.cadence import Cadence, DECISION_ANCHOR
from src.orchestration.schedule.preconditions import (
    BLOCKED, BlockedPrecondition, Precondition, assert_anchor,
    assert_cadence_unclaimed, assert_inputs_fresh, assert_lock,
    assert_open_confirmed, assert_trading_day,
)
from src.orchestration.state.locks import (
    AttemptLog, CadenceClaims, Checkpoints, RunLock,
)

SUCCESS, FAILED, INCOMPLETE, BUDGET_EXCEEDED = (
    "SUCCESS", "FAILED", "INCOMPLETE", "BUDGET_EXCEEDED")
TERMINAL = (SUCCESS, FAILED, INCOMPLETE, BUDGET_EXCEEDED, BLOCKED)

#: OR-45 — ★ what a failure notice may contain. **No analytical content**: a
#: report asserts *"here is the analysis"*, a failure notice asserts *"the run
#: did not complete, here is why"*.
FAILURE_NOTICE_FIELDS = ("run_id", "status", "failed_jobs", "error_codes",
                         "errors", "started_at", "ended_at")


def plan(graph: JobGraph) -> JobGraph:
    """T-2 — ★ **inspectable without executing.** Returns the graph, runs nothing."""
    return graph


@dataclass
class Orchestrator:
    """The in-process job graph (OR-40), invoked by a thin external timer."""

    graph: JobGraph
    cadence: Cadence
    budgets: Budgets = field(default_factory=Budgets)
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    lock: RunLock = field(default_factory=RunLock)
    claims: CadenceClaims = field(default_factory=CadenceClaims)
    checkpoints: Checkpoints = field(default_factory=Checkpoints)
    attempts: AttemptLog = field(default_factory=AttemptLog)
    _manifests: dict = field(default_factory=dict)
    _outcomes: list = field(default_factory=list)

    # ── OR-5: preconditions, before anything ──────────────────────────────
    def trigger(self, *, as_of: date, calendar, inputs=(), day_bar=None,
                model=None, git_sha: str = "", dirty: bool = False,
                config_hash: str = "", seed: int = 42, stubs=(),
                now: datetime | None = None):
        """OR-5 → OR-9. Returns a `RunManifest` **or** a `BlockedPrecondition`.

        ⚠ A blocked run is **not** a failure: a non-trading day is INFO, and so
        is a cadence window a completed run already claimed (OR-42).
        """
        now = now or datetime.now(timezone.utc)
        key = self.cadence.cadence_key(as_of)
        checks = []
        try:
            checks.append(assert_cadence_unclaimed(key, claims=self.claims))
            trading = assert_trading_day(as_of, calendar=calendar)
            checks.append(trading)
            if not trading.ok:
                return BlockedPrecondition(
                    self.graph.job_graph_id, as_of, trading.detail,
                    "ORC.PRECOND.NOT_TRADING_DAY", tuple(checks))
            checks.append(assert_inputs_fresh(inputs, as_of=as_of))
            checks.append(assert_open_confirmed(day_bar, as_of=as_of))
            checks.append(assert_anchor(DECISION_ANCHOR, model))
            checks.append(assert_lock(self.graph.job_graph_id, lock=self.lock))
        except Exception as exc:                          # noqa: BLE001
            return BlockedPrecondition(
                self.graph.job_graph_id, as_of, str(exc),
                getattr(exc, "code", "ORC.PRECOND.UNEVALUABLE"), tuple(checks))

        run_id = new_run_id(self.graph.job_graph_id, now)
        self.lock.acquire(run_id, at=now)
        # ── OR-9: the manifest is written BEFORE any work.
        manifest = RunManifest(
            run_id=run_id, job_graph_id=self.graph.job_graph_id,
            git_sha=git_sha, dirty=dirty, config_hash=config_hash,
            data_as_of=as_of, decision_anchor=DECISION_ANCHOR, seed=seed,
            inputs=tuple(inputs), budgets=self.budgets.to_json_obj(),
            preconditions={c.name: c.ok for c in checks},
            stubs=tuple(stubs), written_at=now)
        self._manifests[run_id] = manifest
        return manifest

    # ── §11 `run` ─────────────────────────────────────────────────────────
    def run(self, run_id: str, *, invoke, clock=None) -> RunOutcome:
        """OR-14…OR-22 — invoke each job in order, classify, retry, budget.

        `invoke(job, manifest)` is the caller's dispatch. ★ **D-08 never calls a
        domain function directly**, which is what keeps OR-1 checkable: nothing
        here can return a derived value because nothing here computes one.
        """
        manifest = self._manifests.get(run_id)
        if manifest is None:
            raise ManifestMissingError(run_id)
        clock = clock or _monotonic
        started = datetime.now(timezone.utc)
        runs, failed, run_elapsed = [], [], 0.0

        for job in self.graph.order():
            digest = _digest(manifest, job.job_id)
            if self.checkpoints.can_skip(job.job_id, inputs_digest=digest):
                runs.append(JobRun(job.job_id, "SKIPPED", 0, 0.0))
                continue
            record = self._run_one(job, manifest, invoke=invoke, clock=clock)
            runs.append(record)
            run_elapsed += record.elapsed_s
            if record.status == SUCCESS:
                self.checkpoints.record(job.job_id, inputs_digest=digest)
            elif not job.optional:
                failed.append(job.job_id)
            # ⚠ OR-18 — an optional job's failure degrades SCOPE and the absence
            #   is reported; it does not fail the run.

        status = SUCCESS if not failed else INCOMPLETE
        for record in runs:
            if record.error_code == "ORC.BUDGET.EXCEEDED":
                status = BUDGET_EXCEEDED
        outcome = RunOutcome(run_id=run_id, status=status, jobs=tuple(runs),
                             started_at=started,
                             ended_at=datetime.now(timezone.utc))
        self._outcomes.append(outcome)
        self.claims.claim(self.cadence.cadence_key(manifest.data_as_of),
                          run_id, status=status)
        self.lock.release(run_id)
        return outcome

    def _run_one(self, job, manifest, *, invoke, clock) -> JobRun:
        attempt, elapsed = 0, 0.0
        while True:
            attempt += 1
            start = clock()
            try:
                invoke(job, manifest)
            except Exception as exc:                      # noqa: BLE001
                elapsed = clock() - start
                code = getattr(exc, "code", type(exc).__name__)
                self.attempts.append(job_id=job.job_id, attempt=attempt,
                                     status=FAILED, error_code=code,
                                     elapsed_s=elapsed)
                try:
                    retryable = self.retry.should_retry(
                        job_id=job.job_id, error_code=code, attempt=attempt)
                except Exception:                         # noqa: BLE001
                    retryable = False       # ★ unclassified or semantic ⇒ stop
                if retryable:
                    continue
                return JobRun(job.job_id, FAILED, attempt, elapsed, code, str(exc))
            elapsed = clock() - start
            self.attempts.append(job_id=job.job_id, attempt=attempt,
                                 status=SUCCESS, error_code=None,
                                 elapsed_s=elapsed)
            try:
                self.budgets.check_job(job.job_id, elapsed)
            except Exception as exc:                      # noqa: BLE001
                return JobRun(job.job_id, FAILED, attempt, elapsed,
                              getattr(exc, "code", "ORC.BUDGET.EXCEEDED"), str(exc))
            return JobRun(job.job_id, SUCCESS, attempt, elapsed)

    def resume(self, run_id: str, *, invoke, clock=None) -> RunOutcome:
        """OR-26 — ★ skips only checkpointed-complete work whose inputs are
        unchanged; **never a failed step.**"""
        return self.run(run_id, invoke=invoke, clock=clock)

    def status(self, run_id: str) -> tuple:
        return tuple(a for a in self.attempts.to_json_obj())

    def history(self, window: int = 30) -> tuple:
        return tuple(self._outcomes[-window:])


def artifact_allowed(outcome: RunOutcome) -> bool:
    """OR-16 / AC-8.19 — ★ **INCOMPLETE never produces a human-facing artifact.**"""
    return outcome.status == SUCCESS


def assert_artifact_allowed(outcome: RunOutcome) -> None:
    if not artifact_allowed(outcome):
        raise RunIncompleteError(
            outcome.run_id,
            [j.job_id for j in outcome.jobs if j.status == FAILED])


def failure_notice(outcome: RunOutcome) -> dict:
    """OR-19 + OR-45 / AC-8.22, AC-8.22a — ★ **a failure notice is not a report.**

    ⚠ *A pipeline that fails quietly is indistinguishable from one that was
    never scheduled*, so this reaches the human by the same channel a success
    would. **It carries no analytical content** — that is the line OR-45 draws,
    and it is what keeps OR-16 from silencing OR-19.
    """
    return {
        "run_id": outcome.run_id, "status": outcome.status,
        "failed_jobs": [j.job_id for j in outcome.jobs if j.status == FAILED],
        "error_codes": sorted({j.error_code for j in outcome.jobs
                               if j.error_code}),
        # ★ OR-61 — the why, per failed job (DX-172)
        "errors": {j.job_id: getattr(j, "error_message", None) or "" for j in outcome.jobs
                   if j.status == FAILED},
        "started_at": outcome.started_at.isoformat(),
        "ended_at": outcome.ended_at.isoformat(),
    }


def assert_no_analysis(notice: dict) -> None:
    """OR-45 — ⚠ *a failure notice that quotes a partial result has become a
    report and is forbidden.*"""
    extra = sorted(set(notice) - set(FAILURE_NOTICE_FIELDS))
    if extra:
        raise BoundaryError(
            f"the failure notice carries {extra!r}, which is analytical content")


def _digest(manifest: RunManifest, job_id: str) -> str:
    payload = f"{manifest.config_hash}|{manifest.data_as_of}|{job_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _monotonic() -> float:
    import time as _time
    return _time.monotonic()
