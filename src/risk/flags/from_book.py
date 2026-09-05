"""D-05 §7 — M-3 and M-4, wired to the real book. RK-12…RK-19, RK-39.

★ **The part of D-05 with the clearest justification**: these detect
**behaviours Victor has said he wants to curb**, not statistical states — and
they are the half of D-05 that needs **no market value**, so they run today
while RC-58 postpones valuation.

⚠ **RK-13/RK-18: flagged, never blocked, and never suppressible.**
"""

from __future__ import annotations

from src.recording.book.lots import cost_changes, round_trips
from src.risk.flags.behavioural import (
    HoldingPeriods, REGISTERED_SHORT_HOLD_DAYS, premature_exit_flag,
    pyramiding_flag, short_hold_flags,
)


def m3_pyramiding(orders, *, as_of) -> tuple:
    """RK-12 / M-3 / INV-028 — ★ *adding at ever-higher average cost.*

    ⚠ The **first** purchase of a name is never pyramiding — there is no prior
    average to raise — which `CostChange.raises_average_cost` encodes so that
    the flag cannot fire on an opening trade.
    """
    out = []
    for change in cost_changes(orders):
        if not change.raises_average_cost:
            continue
        flag = pyramiding_flag(
            ticker=change.symbol, account=change.account_id,
            as_of=change.trade_date, avg_cost_before=change.avg_cost_before,
            avg_cost_after=change.avg_cost_after,
            added_value=change.added_value)
        if flag is not None:
            out.append(flag)
    return tuple(out)


def m4_registered_short_holds(orders, *, as_of,
                              window_days: int = REGISTERED_SHORT_HOLD_DAYS
                              ) -> tuple:
    """RK-15…RK-17 / M-4 — ★ **there is no exempt account.**

    All four are registered (RC-25), so this applies to the **entire book,
    always**. ⚠ **RK-17: the flag reports the trailing count and frequency** —
    *CRA's "carrying on a business" test weighs PATTERN; a single fast round
    trip is unremarkable and twenty is the finding.*
    """
    trips = [{"ticker": t.symbol, "account": t.account_id,
              "held_days": t.held_days, "closed_on": t.closed_on}
             for t in round_trips(orders)]
    return short_hold_flags(trips, as_of=as_of, window_days=window_days)


def m3_premature_exits(orders, *, as_of, short_tail_pct: float = 25.0) -> tuple:
    """RK-14 / RK-39 — ★ **the symmetric flag.**

    *M-3's fix is "sell less and let winners run"*, so D-05 also surfaces
    premature exits. ⚠ **A domain that flags only scale-ins implements half the
    mandate and silently biases toward selling.**

    ★ No threshold on days: each winning exit is placed in **the book's own**
    realised holding-period distribution (RK-39), because the only artifact
    carrying an *intended* horizon is the thesis — which RK-28 forbids D-05 to
    import.
    """
    trips = round_trips(orders)
    history = HoldingPeriods(days=tuple(t.held_days for t in trips))
    out = []
    for trip in trips:
        flag = premature_exit_flag(
            ticker=trip.symbol, account=trip.account_id, as_of=trip.closed_on,
            held_days=trip.held_days, unrealised_gain_pct=trip.gain_pct,
            history=history, short_tail_pct=short_tail_pct)
        if flag is not None:
            out.append(flag)
    return tuple(out)


def behavioural_flags(orders, *, as_of) -> tuple:
    """★ All three, in one pass. **This is the whole of D-05 that runs without a
    market value** — and it is the half the mandate actually asked for."""
    return (m3_pyramiding(orders, as_of=as_of)
            + m3_premature_exits(orders, as_of=as_of)
            + m4_registered_short_holds(orders, as_of=as_of))
