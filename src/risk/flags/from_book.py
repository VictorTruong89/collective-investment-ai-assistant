"""D-05 §7 — M-3 and M-4, wired to the real book. RK-12…RK-19, RK-39.

★ **The part of D-05 with the clearest justification**: these detect
**behaviours Victor has said he wants to curb**, not statistical states — and
they are the half of D-05 that needs **no market value**, so they run today
while RC-58 postpones valuation.

⚠ **RK-13/RK-18: flagged, never blocked, and never suppressible.**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from src.recording.book.lots import cost_changes, round_trips
from src.risk.contracts.alerts import COMPLETE
from src.risk.contracts.alerts import unchecked as unchecked_status
from src.risk.flags.behavioural import (
    KINDS,
    REGISTERED_SHORT_HOLD_DAYS,
    SHORT_HOLD,
    HoldingPeriods,
    premature_exit_flag,
    pyramiding_flag,
    short_hold_flags,
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


# ═══════════════════════════════════════════════════════════════════════════
# RK-40 / CT-5.4 — the flag pass, complete on its own (Victor 2026-10-21, ⓐ)
# ═══════════════════════════════════════════════════════════════════════════

#: RP-57 / Victor 2026-10-21 — the card lists in full the flags of the last 30 days
#: of history; every older one is still counted (RK-18).
RECENT_WINDOW_DAYS = 30

FLAG_PASS_SOURCE = "trade history only — not part of the exposure pass (RK-40)"


@dataclass(frozen=True, slots=True)
class FlagPass:
    """CT-5.4. ★ Its status is ITS OWN — never `alerts_status` (RK-40, RK-30)."""

    status: str
    as_of: date
    history_through: date | None
    accounts: tuple[str, ...]
    flags: tuple
    counts: dict
    short_hold_trailing_frequency: float | None
    recent: tuple[str, ...]

    def to_json_obj(self) -> dict:
        return {"status": self.status, "source": FLAG_PASS_SOURCE,
                "as_of": self.as_of.isoformat(),
                "history_through": (self.history_through.isoformat()
                                    if self.history_through else None),
                "accounts": list(self.accounts), "counts": dict(self.counts),
                "short_hold_trailing_frequency": self.short_hold_trailing_frequency,
                "recent_window_days": RECENT_WINDOW_DAYS, "recent": list(self.recent),
                "flags": [f.to_json_obj() for f in self.flags]}


def _event_date(flag) -> date:
    """A round trip happened when it CLOSED; a buy when it was made (CT-5.4)."""
    closed = flag.detail.get("closed_on")
    return date.fromisoformat(closed) if closed else flag.as_of


def summarise(flags, *, history_through: date) -> dict:
    """AC-5.26 — every kind counted, and `recent` = the flags whose event falls in the
    `RECENT_WINDOW_DAYS` ending `history_through`. ★ The counts are over ALL flags,
    so the card's shorter list is a view, never a filter (RK-18)."""
    counts = {kind: 0 for kind in KINDS}
    for f in flags:
        counts[f.kind] += 1
    start = history_through - timedelta(days=RECENT_WINDOW_DAYS)
    recent = [f.flag_id for f in flags if start < _event_date(f) <= history_through]
    freq = next((f.detail.get("trailing_frequency") for f in flags
                 if f.kind == SHORT_HOLD), None)
    return {"counts": counts, "recent": recent, "short_hold_trailing_frequency": freq}


def flag_pass(*, as_of: date, root: str | None = None) -> FlagPass:
    """RK-40 — the M-3/M-4 flags from D-11's exports, with no price and no book.

    ⚠ All or nothing (AC-5.24): an account that cannot be read withholds every flag,
    because a trailing count over part of the book understates the very pattern
    M-4 looks for. The refusal is a STATUS, never an exception — the card must say it.
    """
    from src.recording.book.load import discover_accounts, export_path, resolve_export_dir
    from src.recording.errors import RecordingError
    from src.recording.orders.group import group_orders
    from src.recording.reconcile.ingest import parse_export

    def unchecked(why: str) -> FlagPass:
        return FlagPass(status=unchecked_status(why), as_of=as_of, history_through=None,
                        accounts=(), flags=(), counts={},
                        short_hold_trailing_frequency=None, recent=())

    root = resolve_export_dir(root)
    try:
        accounts = discover_accounts(root)
    except RecordingError as exc:
        return unchecked(str(exc))
    orders, refused, latest = [], [], None
    for account_id, _type in accounts:
        try:
            activities = parse_export(export_path(root, account_id), account_id=account_id)
        except (RecordingError, OSError) as exc:
            refused.append(f"{account_id}: {exc}")
            continue
        orders += list(group_orders(activities))
        dates = [a.trade_date for a in activities if a.trade_date]
        if dates:
            latest = max(latest or dates[0], max(dates))
    if refused:
        return unchecked("; ".join(refused) + " — one unreadable account withholds every "
                         "flag (RK-40, RK-5)")
    flags = behavioural_flags(orders, as_of=as_of)
    s = summarise(flags, history_through=latest or as_of)
    return FlagPass(status=COMPLETE, as_of=as_of, history_through=latest,
                    accounts=tuple(a for a, _ in accounts), flags=flags,
                    counts=s["counts"],
                    short_hold_trailing_frequency=s["short_hold_trailing_frequency"],
                    recent=tuple(s["recent"]))
