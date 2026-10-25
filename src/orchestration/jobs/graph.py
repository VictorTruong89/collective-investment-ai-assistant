"""D-08 §4/§5A.5 — the job graph. OR-40, OR-41, T-2.

★ **`plan()` is inspectable WITHOUT executing** (T-2): a graph you cannot read
without running it is a graph nobody reviews.

⚠ **OR-41: the external timer holds NO policy.** No retry, no dependency order,
no budget, no conditional logic lives in crontab — *policy in a timer is policy
with no manifest, no test and no spec*, which is the same invisibility that
produced §1.5a.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Words that indicate policy has leaked into an external timer definition.
TIMER_POLICY_MARKERS = (
    "retry", "backoff", "timeout", "deadline", "budget", "&&", "||",
    "if ", "for ", "depends", "sleep",
)


@dataclass(frozen=True, slots=True)
class Job:
    """A declared job — ★ *declared, inspectable, no logic* (§4)."""

    job_id: str
    invokes: str                    # the domain entrypoint, as a dotted name
    depends_on: tuple[str, ...] = ()
    budget_s: float | None = None
    optional: bool = False          # OR-18 — its absence degrades scope

    def to_json_obj(self) -> dict:
        return {"job_id": self.job_id, "invokes": self.invokes,
                "depends_on": list(self.depends_on), "budget_s": self.budget_s,
                "optional": self.optional}


@dataclass(frozen=True, slots=True)
class JobGraph:
    job_graph_id: str
    jobs: tuple[Job, ...]

    def __post_init__(self) -> None:
        ids = [j.job_id for j in self.jobs]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.job_graph_id}: duplicate job ids")
        known = set(ids)
        for job in self.jobs:
            missing = [d for d in job.depends_on if d not in known]
            if missing:
                raise ValueError(
                    f"{job.job_id} depends on {missing!r}, which the graph does "
                    f"not declare")

    def order(self) -> tuple[Job, ...]:
        """A deterministic topological order (INV-2).

        ★ Ties break on `job_id`, so the plan is byte-identical run to run — a
        graph whose order depends on dict insertion is not inspectable.
        """
        remaining = {j.job_id: j for j in self.jobs}
        done, out = set(), []
        while remaining:
            ready = sorted(j.job_id for j in remaining.values()
                           if set(j.depends_on) <= done)
            if not ready:
                raise ValueError(
                    f"{self.job_graph_id}: dependency cycle among "
                    f"{sorted(remaining)!r}")
            for job_id in ready:
                out.append(remaining.pop(job_id))
                done.add(job_id)
        return tuple(out)

    def to_json_obj(self) -> dict:
        return {"job_graph_id": self.job_graph_id,
                "jobs": [j.to_json_obj() for j in self.order()]}


def resolve_target(dotted: str):
    """`"module:callable"` → the callable. ★ **The OR-48 seam, reusable.**

    ⚠ Extracted so that a caller with a dotted name but no `Job` — the outcome
    write, which happens *after* the graph and so cannot be a job — reaches a
    domain the same sanctioned way: **invoke by name, never import** (OR-2).
    """
    module_name, _, attr = dotted.partition(":")
    if not attr:
        raise ValueError(f"{dotted!r} must be 'module:callable'")
    import importlib

    target = getattr(importlib.import_module(module_name), attr, None)
    if target is None:
        raise ValueError(f"{dotted!r} does not resolve")
    if not callable(target):
        raise TypeError(f"{dotted!r} is not callable")
    return target


def resolve(job: Job):
    """★ Import `job.invokes` and return the callable it names.

    ⚠ **Added after the drift it exists to prevent.** `Job.invokes` is a dotted
    string, and when B6 declared the graph **five of its nine names pointed at
    functions that did not exist** — `rank` instead of `rank_candidates`,
    `build` instead of `build_panel`. Nothing noticed, because **a declared
    pointer with no check is a comment**.

    ★ Resolution stays out of the runner on purpose: the runner takes `invoke`
    as an argument so it can never call a domain (OR-1). This helper is for the
    *caller* — and for the test that pins every name in the graph.
    """
    import importlib

    module_name, _, attr = job.invokes.partition(":")
    if not attr:
        raise ValueError(f"{job.job_id}: `invokes` must be 'module:callable'")
    module = importlib.import_module(module_name)
    target = module
    for part in attr.split("."):
        target = getattr(target, part, None)
        if target is None:
            raise AttributeError(
                f"{job.job_id}: {job.invokes!r} does not resolve — "
                f"{part!r} is not on {module_name}")
    if not callable(target):
        raise TypeError(f"{job.job_id}: {job.invokes!r} is not callable")
    return target


def assert_graph_resolves(graph: JobGraph) -> None:
    """Every declared job names something that exists. ★ CI-checkable."""
    for job in graph.jobs:
        resolve(job)


def assert_timer_has_no_policy(timer_line: str) -> None:
    """OR-41 / AC-8.36 — ★ the timer's *entire* responsibility is *"call the
    entrypoint at this time"*."""
    from src.orchestration.errors import OrchestrationError

    body = timer_line.split(None, 5)[-1] if timer_line.strip() else ""
    found = [m for m in TIMER_POLICY_MARKERS if m in body.casefold()]
    if found:
        raise OrchestrationError(
            f"the external timer carries {found!r}. Policy in a timer is policy "
            f"with no manifest, no test and no spec (OR-41)")


#: ★ `daily_inference@v3` — the production graph. Declared here so `plan()`
#: returns it without executing anything (T-2).
DAILY_INFERENCE = JobGraph(
    job_graph_id="daily_inference@v9",   # v9: the `flags` job (OR-63, 2026-10-21)
    jobs=(
        Job("calendar_check", "src.data_engine.service:DataEngine.calendar_check_report", budget_s=60),
        Job("prices", "src.data_engine.service:DataEngine.get_prices",
            depends_on=("calendar_check",), budget_s=300),
        Job("features", "src.feature_engineer.ml_features.assemble:build_panel",
            depends_on=("prices",), budget_s=300),
        Job("rank", "src.quant.signals.rank:rank_candidates",
            depends_on=("features",), budget_s=120),
        # ⊘ REMOVED 2026-10-05 (Victor; L3 §2.1s): the `observe` and `thesis` jobs —
        #   the old three-call thesis path (J-11/J-15/J-16 @v1, `author_for`) and the
        #   Class-B capture that existed only to feed it. Theses are authored on
        #   demand by `tools/run_thesis_once.py` (32 blocks, J-15 v3). Restore from
        #   commit ac6e14f or `sdd/archive/2026-10-05_removed_old_thesis_path.patch`.
        # ★ With no thesis in the run the gate falls back to the declared stub and
        #   DN-39 keeps the card informational.
        Job("thesis_gate", "src.fundamental.thesis.gate:evaluate",
            depends_on=("features", "rank"), budget_s=600),
        # ★ D-11's book, INVOKED by dotted name and resolved at run time.
        #   ⚠ OR-2 / AC-8.2: orchestration may invoke a D-11 entrypoint but may
        #   never import one — *an inference run writing positions.json means a
        #   PREDICTION is editing the RECORD*. The string below is the sanctioned
        #   seam; `resolve(job)` turns it into the callable.
        Job("book", "src.recording.book.load:load_books",
            depends_on=("prices",), budget_s=120, optional=True),
        # ★ OR-63 / RK-40 — D-05's behavioural-flag pass, complete on its own from the
        #   trade history (no price, no book), so it runs while R1 keeps `risk` UNCHECKED.
        Job("flags", "src.risk.flags.from_book:flag_pass",
            depends_on=("calendar_check",), budget_s=60, optional=True),
        Job("risk", "src.risk.alerts.daily:daily_book_pass",
            depends_on=("prices", "book", "flags"), budget_s=120, optional=True),
        Job("decide", "src.decision.compose.service:compose",
            depends_on=("rank", "thesis_gate", "risk", "flags"), budget_s=60),
        Job("render", "src.reporting.render.card:build_card",
            depends_on=("decide",), budget_s=60),
        # ★★ CT-11.7 — the record every run leaves behind. ⚠ **Before
        #   `deliver`, deliberately**: P6 says the user's copy must be viewable
        #   later without a live server, so the durable write has to happen
        #   whether or not the send succeeds. A record written after a
        #   successful send is a record that is missing exactly when the send
        #   failed — which is when it is wanted most (RC-59, RC-33, OR-19).
        Job("record", "src.recording.artifacts.store:record_run",
            depends_on=("render", "decide"), budget_s=120),
        Job("deliver", "src.reporting.deliver.email:send",
            depends_on=("render", "record"), budget_s=120),
    ),
)
