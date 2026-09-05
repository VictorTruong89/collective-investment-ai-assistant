"""D-08 §5 — preconditions. OR-5, OR-6, OR-7, OR-32, OR-33, OR-44, OR-46.

★ **A schedule is not a timer.** *A cadence that fires regardless of state is a
timer, and a timer running an inference job on a market holiday produces a
confident report about a day that did not happen.*

⚠ **OR-6: a precondition that cannot be EVALUATED blocks the run and reports
why. It never defaults to "probably fine."**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.orchestration.errors import (
    AnchorMismatchError, AnchorUndeclaredError, CadenceClaimedError,
    LockHeldError, OpenUnconfirmedError, PreconditionUnevaluableError,
    StaleInputError,
)

BLOCKED = "BLOCKED_PRECONDITION"

#: OR-32's check. ⚠ `main_inference.py:250` sets all five OHLC fields to one
#: spot quote, which makes the day-T **intraday range identically zero** — an
#: INV-4 parity break on the one bar that drives the decision, while every
#: training bar has a real range.
_OHLC = ("open", "high", "low", "close")


@dataclass(frozen=True, slots=True)
class Precondition:
    name: str
    #: ⚠ `None` means **NOT EVALUATED** — never a pass (OR-52, DE-35).
    ok: bool | None
    detail: str = ""

    def to_json_obj(self) -> dict:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class BlockedPrecondition:
    """★ OR-5's outcome when work must not start.

    ⚠ **Not a failure**: a non-trading day is `INFO`, and a claimed cadence
    window is `INFO` too — *OR-42 deliberately prefers redundant firings.*
    """

    job_graph_id: str
    as_of: date
    reason: str
    code: str
    checks: tuple[Precondition, ...] = ()
    status: str = BLOCKED

    def to_json_obj(self) -> dict:
        return {"job_graph_id": self.job_graph_id, "as_of": self.as_of.isoformat(),
                "status": self.status, "reason": self.reason, "code": self.code,
                "checks": [c.to_json_obj() for c in self.checks]}


def assert_trading_day(as_of: date, *, calendar) -> Precondition:
    """OR-5(a)/OR-7 — ★ **the calendar check belongs to D-07.** D-08 asks."""
    try:
        open_today = calendar(as_of)
    except Exception as exc:                              # noqa: BLE001 — OR-6
        raise PreconditionUnevaluableError("trading_day", str(exc)) from exc
    if open_today is None:
        raise PreconditionUnevaluableError(
            "trading_day", "the calendar returned no answer")
    return Precondition("trading_day", bool(open_today),
                        "" if open_today else f"{as_of} is not a trading day")


def assert_inputs_fresh(inputs, *, as_of: date, max_age_days: int = 1
                        ) -> Precondition:
    """OR-5(b) — a stale input blocks the run.

    ⚠⚠ **An empty list is NOT EVALUATED, never `True`** (OR-52).

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  MEASURED 2026-08-27.  Every real run recorded                    ║
    ║      "preconditions": {"inputs_fresh": true, …}                   ║
    ║  having examined ZERO inputs — the entrypoint passed none.        ║
    ║                                                                  ║
    ║  ★★ This is DE-56's shape inside the orchestrator's own guards:   ║
    ║  absence of evidence and evidence of absence are different        ║
    ║  results, and conflating them is how a false assumption becomes   ║
    ║  a silent one (DE-35).                                           ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ★ `ok=None` serialises to `null`, so the manifest states *not evaluated*
    rather than claiming a check that never happened.
    """
    if not inputs:
        return Precondition(
            "inputs_fresh", None,
            "no inputs were declared, so freshness was NOT EVALUATED — it is "
            "not a pass (OR-52, DE-35)")
    stale = [i["artifact"] for i in inputs
             if (as_of - _as_date(i.get("as_of"))).days > max_age_days]
    if stale:
        raise StaleInputError(stale, max_age_days)
    return Precondition("inputs_fresh", True)


def _as_date(value):
    if value is None:
        raise PreconditionUnevaluableError(
            "inputs_fresh", "an input declared no as_of, so its age is unknowable")
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def assert_open_confirmed(bar, *, as_of: date, ticker: str = "") -> Precondition:
    """OR-32/OR-33 — ★ the **settled day-T opening print**, as a real OHLC field.

    ⚠ **Never substituted with the previous close**: that substitution is silent
    and *makes the decision a day stale while looking current* — the
    plausible-looking default P5 forbids. ⚠ And never a **spot quote relabelled
    as an open**: a bar whose OHLC fields are all equal has a zero intraday
    range, which is an INV-4 parity break on the one bar that decides.
    """
    if bar is None:
        raise OpenUnconfirmedError(as_of, ticker, "no day-T bar")
    # ★ OR-47 — the OPEN is what the decision is taken on, and it is the only
    #   field settled at 10:00. ⚠ Demanding a settled close here would block
    #   every run forever: the auction is final at 09:30, the bar at 16:00.
    if bar.get("open") is None:
        raise OpenUnconfirmedError(as_of, ticker, "missing ['open']")
    present = [bar[f] for f in _OHLC if bar.get(f) is not None]
    if len(present) == len(_OHLC) and len(set(present)) == 1:
        raise OpenUnconfirmedError(
            as_of, ticker,
            "open==high==low==close — a spot quote relabelled as a bar. The "
            "day-T intraday range would be identically zero while every "
            "training bar has a real one (OR-32, INV-4)")
    if not bar.get("settled", True):
        raise OpenUnconfirmedError(as_of, ticker, "the open is not settled")
    return Precondition("open_confirmed", True)


def assert_anchor(manifest_anchor: str, model) -> Precondition:
    """OR-35/OR-44 — ★★ the check AC-8.32 asks for, made possible.

    ⚠ *A model trained on close(T) → close(T+h) and deployed to decide at open(T)
    is anchored one session away from the return it was fitted to predict — a
    FULL SESSION of drift on every single prediction, invisible in backtest
    because the backtest shares the training anchor.*
    """
    if model is None:
        return Precondition("decision_anchor", True, "no model in this run")
    trained = (model.get("trained_anchor") if isinstance(model, dict)
               else getattr(model, "trained_anchor", None))
    if not trained:
        raise AnchorUndeclaredError(
            (model.get("artifact_id") if isinstance(model, dict)
             else getattr(model, "artifact_id", "<unknown>")))
    if trained != manifest_anchor:
        raise AnchorMismatchError(manifest_anchor, trained)
    return Precondition("decision_anchor", True, f"both {trained!r}")


def assert_cadence_unclaimed(cadence_key: str, *, claims) -> Precondition:
    """OR-46 / AC-8.37 — ★ one run per window, by key.

    ⚠ **A FAILED run does not claim the key**: re-firing after a failure must be
    able to retry the cadence, or OR-42's redundancy buys nothing exactly when
    it is needed.
    """
    if cadence_key in claims:
        raise CadenceClaimedError(cadence_key, claims[cadence_key])
    return Precondition("cadence_unclaimed", True)


def assert_lock(job_graph_id: str, *, lock) -> Precondition:
    """OR-24 — ★ the holder is **inspectable**: a stuck lock must be
    diagnosable, not mysterious."""
    holder = lock.holder()
    if holder is not None:
        raise LockHeldError(job_graph_id, holder)
    return Precondition("lock_acquired", True)
