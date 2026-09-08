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

★★ **`traced_transport()` below closes what `traced()` cannot see.** `traced()`
gives **job** granularity; `AC-2.2` needs **call** granularity — the request and
response of every LLM call. The gateway takes its `transport` as a constructor
parameter (`Gateway(config, transport=...)`), so the vendor boundary is injected
exactly like the job dispatch is, and wrapping it needs **no edit to the gateway**.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from src.orchestration.trace.models import ExternalCall, StepRecord
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


# --------------------------------------------------------------------------- #
# AC-2.2 at CALL granularity — the vendor boundary
# --------------------------------------------------------------------------- #
def _tokens_of(response: dict | None) -> dict:
    """⚠⚠ The gateway's transport speaks `tokens_in` / `tokens_out`.

    ★ Found by writing a characterization test **after** building on this
    contract: the first version of this wrapper read
    `response["usage"]["input_tokens"]` — the Anthropic SDK's shape — and would
    have recorded **0 tokens on every real call**. The unit test agreed with the
    wrapper because both encoded the same assumption.

    Both shapes are accepted: `tokens_in`/`tokens_out` is what
    `src/shared/llm/gateway.py` passes through (frozen by
    `tests/test_characterization_gateway.py`); `usage.*` is what a raw SDK
    response carries, for a transport that returns one unwrapped.
    """
    r = response or {}
    if "tokens_in" in r or "tokens_out" in r:
        return {"input": int(r.get("tokens_in", 0)),
                "output": int(r.get("tokens_out", 0))}
    usage = r.get("usage") or {}
    return {"input": int(usage.get("input_tokens", 0)),
            "output": int(usage.get("output_tokens", 0))}


def traced_transport(
    transport: Callable[[dict], dict],
    store: TraceStore,
    *,
    step_id: str,
    kind: str = "llm",
    call_id_of: Callable[[dict], str] | None = None,
) -> Callable[[dict], dict]:
    """Wrap a gateway transport so every vendor call becomes a `CT-2.2` record.

    ★ **Why the transport and not the gateway.** `Gateway.__init__` takes
    `transport: Callable[[dict], dict]` and calls it as `raw = self._transport(
    request)`. That is the same injection seam `traced()` uses on the job
    dispatch, and wrapping it means **zero edits to inherited D-00 code**
    (`AC-2.1`, `P4`).

    ⚠ **This is the half `Gateway._emit` deliberately does not do.** The
    gateway's own log records `LLMCall` — call_id, tokens, cost, outcome — and
    **not the payload**, because upstream `AnalysisRunLog` says *"RECORD THAT IT
    FAILED; NEVER RECORD WHAT IT PRODUCED"* (`RA-111`). ★ That rule protects the
    **output path**: a degraded response must not be persisted and later rendered
    as sound. A trace is **evidence, not output** (§4), so F2 records both halves
    — and `AC-2.9` redaction plus `D4`'s export filter are what keep it out of
    anything published.

    ⚠ A transport that raises is recorded with its `error` and **re-raised**: the
    gateway's own retry logic must still see it (`EH-14` — only orchestration
    retries). A recorder that swallowed it would change which calls are retried.
    """
    seq = {"n": 0}

    def _transport(request: dict) -> dict:
        seq["n"] += 1
        call_id = (call_id_of(request) if call_id_of
                   else f"{step_id}:{kind}:{seq['n']}")
        t0 = time.perf_counter()
        try:
            response = transport(request)
        except BaseException as exc:
            store.append(ExternalCall(
                run_id=store.run_id, step_id=step_id, call_id=call_id, kind=kind,
                request=request, response=None,
                model_id=request.get("model"),
                latency_ms=int((time.perf_counter() - t0) * 1000),
                error=f"{type(exc).__name__}: {exc}"))
            raise                       # ⚠ the gateway's retry must still see it
        store.append(ExternalCall(
            run_id=store.run_id, step_id=step_id, call_id=call_id, kind=kind,
            request=request, response=response,
            model_id=(response or {}).get("model") or request.get("model"),
            tokens=_tokens_of(response),
            latency_ms=int((time.perf_counter() - t0) * 1000)))
        return response

    return _transport
