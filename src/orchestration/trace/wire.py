"""F2 — attach the recorder to a real run (`MS-3.8`).

★★ **This wraps `invoke`; it does not modify the runner.**

`Orchestrator.run(run_id, *, invoke, clock)` takes its dispatch as a parameter,
and D-08's own docstring says *"D-08 never calls a domain function directly …
nothing here can return a derived value because nothing here computes one."*
That injection point is the whole integration: a traced run is
`orchestrator.run(run_id, invoke=traced(invoke, store))`.

⚠ **Why not edit `_run_one`.** `AC-2.1` — F2 extends, never duplicates — and `D6`
records at **job and external-call boundaries**, not inside inherited logic.
Editing the runner would put F2 inside D-08's retry/budget path, where a trace
bug could change whether a job is retried. ★ A recorder that can alter the run it
records is not an observer.

⚠ **`ExternalCall` records are NOT emitted here.** They belong at the vendor
boundary — the LLM gateway and the HTTP client — which the dispatch does not see.
`traced()` gives job granularity; call granularity arrives when the gateway is
wrapped, and until then `AC-2.2` is exercised by direct writes rather than by a
real run. **Stated so the gap is visible in the trace, not discovered later.**
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from src.orchestration.trace.models import StepRecord
from src.orchestration.trace.store import TraceStore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def traced(
    invoke: Callable[..., Any],
    store: TraceStore,
    *,
    decision_id_of: Callable[[Any], str | None] = lambda _job: None,
    seat_of: Callable[[Any], int | None] = lambda _job: None,
) -> Callable[..., Any]:
    """Wrap a dispatch so every job invocation writes a `CT-2.1` `StepRecord`.

    ★ `decision_id_of` / `seat_of` are hooks, not requirements: a job that is not
    about one ticker legitimately has **no** `decision_id` (`CT-2.1` nullable),
    and cross-cutting D-00 work has **no seat** (vision §3).
    """

    # ⚠ The signature MIRRORS the dispatch it wraps; unused parameters here are
    # the contract, not dead code. Renaming them would break keyword callers.
    def _invoke(job, manifest, *args, **kwargs):  # noqa: ARG001  (see above)
        job_id = getattr(job, "job_id", str(job))
        started = _now()
        status = "SUCCESS"
        try:
            return invoke(job, manifest, *args, **kwargs)
        except BaseException:
            # ⚠ P5 — a failed job is RECORDED as failed, then re-raised. The
            # recorder never swallows, and never decides.
            status = "FAILED"
            raise
        finally:
            store.append(StepRecord(
                run_id=store.run_id, job_id=job_id, step_id=f"job:{job_id}",
                node=job_id, started_at=started, ended_at=_now(), status=status,
                decision_id=decision_id_of(job), seat=seat_of(job),
            ))

    return _invoke


def replayable_invoke(records: list[dict]) -> Callable[..., Any]:
    """A dispatch that serves each job from the recording, in recorded order.

    ⚠ Used by replay only. It reaches nothing outside the trace — which is what
    `AC-2.3`'s *"no network call is made"* means in practice.
    """
    order = [r for r in records if r.get("type") == "StepRecord"]

    # ⚠ Same interface-mirroring rule as `traced()` above: the signature is the
    # contract, so the unused parameters stay.
    def _invoke(job, manifest, *args, **kwargs):  # noqa: ARG001
        job_id = getattr(job, "job_id", str(job))
        match = next((r for r in order if r["job_id"] == job_id), None)
        if match is None:
            raise KeyError(f"job {job_id!r} is not in the recording — the graph changed")
        return match
    return _invoke
