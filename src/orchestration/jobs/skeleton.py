"""★ The B3 walking-skeleton shim — invokes, computes nothing (L3 BS-12, OR-1).

```
ORCHESTRATION INVOKES WORK. IT NEVER PERFORMS WORK.

No analysis. No computation. No judgement. No model fit, no fold split, no
threshold search, no selection, no rendering, and above all NO WRITE TO THE
BOOK.

The reason is not tidiness. A computation inside an entrypoint has NO SPEC,
NO OWNER and NO ACCEPTANCE CRITERIA — it is invisible to the whole SDD
process by construction.
```

★ **BS-12: this is a SHIM, not D-08.** Building D-08 properly before there is
anything to orchestrate inverts the dependency, and **OR-1 makes the shim
trivially replaceable** — orchestration invokes and never computes, so replacing
it at **B6** (BS-16) changes the wiring and nothing else.

⚠ **What this shim deliberately does NOT do**, all of it B6's: retry
classification (OR-14), time budgets (OR-20…OR-23), the DST-safe 10:00 ET
cadence (OR-30), preconditions (OR-5), locks (OR-24), checkpoints (OR-26).
Listed so the gap is visible rather than looking like an oversight.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date, datetime, timezone

from src.orchestration.contracts.manifest import (
    FAILED, INCOMPLETE, SUCCESS, JobRun, RunManifest, RunOutcome, Stub, config_hash,
    git_state, new_run_id,
)

JOB_GRAPH_ID = "b3_walking_skeleton@v1"

#: T-2 — job dependencies are **declared data**, not control flow buried in a
#: `main()`. The graph is inspectable without running it.
JOB_GRAPH: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("calendar_check", ()),                 # D-07 §6A — before the first feature
    ("prices", ("calendar_check",)),        # D-07 CT-7.1
    ("features", ("prices",)),              # D-02 CT-2.2
    ("rank", ("features",)),                # D-03 CT-3.4
    ("gate", ("rank",)),                    # D-01 CT-1.4  (stub — BS-11)
    ("risk", ("rank",)),                    # D-05 alerts  (refuses — RK-29)
    ("compose", ("gate", "risk")),          # D-12 CT-12.1
    ("render", ("compose",)),               # D-09 CT-9.1
    ("deliver", ("render",)),               # D-09 §9
)


def plan() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """★ Inspectable WITHOUT executing (T-2, §11's API surface)."""
    return JOB_GRAPH


def topological_order() -> list[str]:
    """Kahn's algorithm over `JOB_GRAPH`. Deterministic: ties break on job id."""
    deps = {j: set(d) for j, d in JOB_GRAPH}
    order: list[str] = []
    while deps:
        ready = sorted(j for j, d in deps.items() if not d - set(order))
        if not ready:
            raise ValueError(f"job graph has a cycle among {sorted(deps)}")
        order.append(ready[0])
        deps.pop(ready[0])
    return order


@dataclass
class _Recorder:
    """Times each job. ⚠ Timing is not computation — it records, it decides nothing."""

    runs: list = None

    def __post_init__(self) -> None:
        self.runs = []

    def run(self, job_id: str, fn):
        started = time.monotonic()
        try:
            value = fn()
        except Exception as exc:
            self.runs.append(JobRun(job_id, FAILED, 1, time.monotonic() - started,
                                    getattr(exc, "code", type(exc).__name__), str(exc)))
            raise
        self.runs.append(JobRun(job_id, SUCCESS, 1, time.monotonic() - started))
        return value


def build_manifest(*, data_as_of: date, config: dict, stubs, seed: int = 42,
                   decision_anchor: str = "open", inputs=(), repo_root=None,
                   at: datetime | None = None) -> RunManifest:
    """OR-9 — written BEFORE any work. AC-8.10's precondition."""
    sha, dirty = git_state(repo_root)
    return RunManifest(
        run_id=new_run_id(JOB_GRAPH_ID, at),
        job_graph_id=JOB_GRAPH_ID,
        git_sha=sha, dirty=dirty,
        config_hash=config_hash(config),
        data_as_of=data_as_of,
        decision_anchor=decision_anchor,
        seed=seed,
        inputs=tuple(inputs),
        budgets={},          # ⚠ B6's (OR-20). Empty and visibly so.
        preconditions={"calendar_check": "delegated to D-07 §6A"},
        stubs=tuple(stubs),
        written_at=at or datetime.now(timezone.utc),
    )


#: The stub declaration BS-27 requires in the manifest. Sourced from the stub
#: module itself so the two cannot drift.
def b3_stubs() -> tuple[Stub, ...]:
    from src.fundamental import REPLACED_AT as GATE_REPLACED_AT
    from src.fundamental import GATE_ID
    return (
        Stub(domain="D-01", job=GATE_ID, behaviour="constant PASS, grade empty",
             replaced_at=GATE_REPLACED_AT, rule="L3 BS-11/BS-27/BS-34"),
        Stub(domain="D-05", job="daily_pass",
             behaviour="refuses — no reconciled book exists (RK-29); alerts UNCHECKED",
             replaced_at="with D-11's book", rule="L1-risk-management RK-29/RK-30"),
    )


def finish(manifest: RunManifest, recorder: _Recorder, started: datetime,
           artifacts=()) -> RunOutcome:
    """OR-16 — ★ partial success is failure."""
    failed = [j for j in recorder.runs if j.status == FAILED]
    status = INCOMPLETE if failed else SUCCESS
    return RunOutcome(
        run_id=manifest.run_id, status=status, jobs=tuple(recorder.runs),
        started_at=started, ended_at=datetime.now(timezone.utc),
        artifacts=tuple(artifacts),
    )
