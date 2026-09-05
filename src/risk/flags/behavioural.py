"""D-05 §7 — the M-3 and M-4 flags. RK-12…RK-19, RK-39.

★ **The part of D-05 with the clearest justification**: these detect
**behaviours Victor has said he wants to curb**, not statistical states.

⚠ **RK-13/RK-18: flagged, never blocked, and never suppressible.** *A flag that
can be turned off is a flag that will be off when it matters.*
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import date

#: L0 §config — M-4's CRA threshold.
REGISTERED_SHORT_HOLD_DAYS = 30

PYRAMIDING, PREMATURE_EXIT, SHORT_HOLD = (
    "pyramiding", "premature_exit", "registered_short_hold")
KINDS = (PYRAMIDING, PREMATURE_EXIT, SHORT_HOLD)


@dataclass(frozen=True, slots=True)
class Flag:
    """CT-5.2 — append-only.

    ★ **`suppressed` is a constant `false`.** It is present so the contract
    states that no other value exists (RK-18) — and `__post_init__` refuses one.
    """

    flag_id: str
    kind: str
    ticker: str
    account: str
    as_of: date
    detail: dict
    trailing_count: int = 0
    acknowledged_at: str | None = None
    suppressed: bool = False

    def __post_init__(self) -> None:
        from src.risk.errors import SuppressionAttemptedError

        if self.kind not in KINDS:
            raise ValueError(f"flag kind {self.kind!r} not in {KINDS}")
        if self.suppressed:
            raise SuppressionAttemptedError(
                f"flag {self.flag_id!r} was constructed with suppressed=True. "
                f"The field exists so the contract can state that no other "
                f"value exists (RK-18, INV-021)")

    def to_json_obj(self) -> dict:
        return {"flag_id": self.flag_id, "kind": self.kind, "ticker": self.ticker,
                "account": self.account, "as_of": self.as_of.isoformat(),
                "detail": dict(self.detail),
                "trailing_count": self.trailing_count,
                "acknowledged_at": self.acknowledged_at, "suppressed": False}


def acknowledge(flag: Flag, *, at: str) -> Flag:
    """RK-19 / AC-5.18 — ★ **acknowledged is not suppressed.**

    It still renders, marked as acknowledged, and the acknowledgement is
    recorded in D-11's journal (RC-24).
    """
    import dataclasses
    return dataclasses.replace(flag, acknowledged_at=at)


# --------------------------------------------------------------------------- #
# M-3 — pyramiding, and its symmetric half
# --------------------------------------------------------------------------- #

def pyramiding_flag(*, ticker: str, account: str, as_of: date,
                    avg_cost_before: float, avg_cost_after: float,
                    added_value: float, trailing_count: int = 0) -> Flag | None:
    """RK-12 / AC-5.12 — ★ a buy that **raises the average cost** (INV-028).

    ⚠ *Adding at ever-higher average cost* is the mandate's stated behavioural
    problem (vision §3), and the before/after pair is the whole evidence.
    """
    if avg_cost_after <= avg_cost_before:
        return None
    return Flag(
        flag_id=f"M3:{ticker}:{account}:{as_of.isoformat()}",
        kind=PYRAMIDING, ticker=ticker, account=account, as_of=as_of,
        detail={"avg_cost_before": avg_cost_before,
                "avg_cost_after": avg_cost_after,
                "added_exposure": added_value,
                "note": "flagged, never blocked — an override is logged and "
                        "visible in D-11's journal (RK-13, RC-24, INV-026)"},
        trailing_count=trailing_count)


@dataclass(frozen=True, slots=True)
class HoldingPeriods:
    """RK-39's distribution — ★ the book's own realised holds, and nothing else.

    ⚠ *A fixed "exited inside N days" repeats the fixed-percentage mistake D-06
    QS-1 rejects*, and the only artifact carrying an **intended** horizon is the
    thesis — which **RK-28 forbids D-05 to import.** So the comparison is
    internal: this exit against how long this book actually holds things.
    """

    days: tuple[int, ...]

    @property
    def n(self) -> int:
        return len(self.days)

    @property
    def median(self) -> float | None:
        return statistics.median(self.days) if self.days else None

    def percentile_of(self, held_days: int) -> float | None:
        """Where this exit sits in the book's own distribution, in [0, 100]."""
        if not self.days:
            return None
        below = sum(1 for d in self.days if d < held_days)
        return round(100.0 * below / self.n, 2)

    def to_json_obj(self) -> dict:
        return {"n": self.n, "median_days": self.median,
                "days": list(self.days)}


def premature_exit_flag(*, ticker: str, account: str, as_of: date,
                        held_days: int, unrealised_gain_pct: float,
                        history: HoldingPeriods, short_tail_pct: float = 25.0
                        ) -> Flag | None:
    """RK-14 / RK-39 / AC-5.13, AC-5.13a — ★ **the symmetric flag.**

    *M-3's fix is "sell less and let winners run"*, so D-05 also surfaces
    premature exits. ⚠ **A domain that flags only scale-ins implements half the
    mandate and silently biases toward selling.**

    ★ No threshold on *days*: the exit is placed in the book's own distribution
    and flagged when it falls in the short tail. `short_tail_pct` names which
    tail, and the flag reports the percentile so a reader can disagree.
    """
    if unrealised_gain_pct <= 0:
        return None                       # not a winner; RK-14 is about winners
    percentile = history.percentile_of(held_days)
    if percentile is None or percentile > short_tail_pct:
        return None
    return Flag(
        flag_id=f"M3s:{ticker}:{account}:{as_of.isoformat()}",
        kind=PREMATURE_EXIT, ticker=ticker, account=account, as_of=as_of,
        detail={"held_days": held_days, "percentile_of_book": percentile,
                "book_median_days": history.median, "book_n": history.n,
                "unrealised_gain_pct": unrealised_gain_pct,
                "basis": "the book's own realised holding periods — no fixed "
                         "threshold and no intended horizon (RK-39, QK-4)"},
        trailing_count=history.n)


# --------------------------------------------------------------------------- #
# M-4 — the registered short hold, and it is book-wide
# --------------------------------------------------------------------------- #

def short_hold_flags(round_trips, *, as_of: date,
                     window_days: int = REGISTERED_SHORT_HOLD_DAYS
                     ) -> tuple[Flag, ...]:
    """RK-15…RK-17 / AC-5.14…5.16 — ★ **there is no exempt account.**

    All four accounts are registered (D-11 §5.5, RC-25), so M-4 applies to the
    **entire book, always** — it is not a subset rule.

    ⚠ **RK-17: the flag reports the trailing count and frequency, not only the
    individual trip.** *CRA's "carrying on a business" test weighs PATTERN; a
    single fast round trip is unremarkable and twenty is the finding.*
    """
    trips = [t for t in round_trips if t["held_days"] < window_days]
    total = len(trips)
    out = []
    for trip in trips:
        out.append(Flag(
            flag_id=f"M4:{trip['ticker']}:{trip['account']}:{trip['closed_on']}",
            kind=SHORT_HOLD, ticker=trip["ticker"], account=trip["account"],
            as_of=as_of,
            detail={"held_days": trip["held_days"],
                    "closed_on": str(trip["closed_on"]),
                    "window_days": window_days,
                    "trailing_frequency": round(total / max(1, len(round_trips)), 4),
                    "cra_rationale": (
                        "CRA's 'carrying on a business' test weighs PATTERN, "
                        "not the individual trip: a single fast round trip is "
                        "unremarkable and twenty is the finding (RK-17)")},
            trailing_count=total))
    return tuple(out)
