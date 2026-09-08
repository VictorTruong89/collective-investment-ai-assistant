"""D-11 §8 — the book, derived. RC-9, RC-10, RC-51.

★ **RC-9: derived from activity and reconciled against the export, never read
from it.** Positions come from the grouped orders plus corporate-action share
adjustments (RC-49); cash comes from every `Total Amount` the activity carries.

```text
╔══════════════════════════════════════════════════════════════════╗
║  RC-51 — A TRANSACTION EXPORT CARRIES NO BALANCE, SO RC-10 HAS   ║
║  NOTHING TO RECONCILE AGAINST.                                   ║
║                                                                  ║
║  positions + cash == NAV is the check. Derive all three from the  ║
║  same rows and it passes by construction — it checks nothing.     ║
║                                                                  ║
║  So a derived book is UNRECONCILED until a reported NAV or cash   ║
║  balance is supplied from outside it. D-05 then refuses it        ║
║  (RK-29), which is correct: a risk number computed on an          ║
║  unreconciled book is a confident statement about a book that is  ║
║  not the book.                                                    ║
╚══════════════════════════════════════════════════════════════════╝
```
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from src.recording.book.models import BREAK, OK, BookState, Position
from src.recording.book.reconcile import compute_breaks

#: RC-51 — what a book with no external balance to check against is called.
#: ⚠ Not a value of `CT-11.4.reconciled`, which has exactly two (RC-10, RK-0).
#: It is carried on the *result of the derivation*, and D-05 refuses it.
UNRECONCILED = "unreconciled"


def derive_cash(activities) -> dict:
    """Every `Total Amount`, by currency. ★ Trades, dividends, tax, fees, FX.

    ⚠ A corporate-action share adjustment carries no cash and contributes
    nothing here (RC-49) — which is exactly why it must be counted on the
    *position* side instead.
    """
    cash: dict = defaultdict(float)
    for row in activities:
        if row.total_amount:
            cash[row.total_currency or "CAD"] += row.total_amount
    return {k: round(v, 2) for k, v in sorted(cash.items())}


def derive_quantities(activities, orders) -> dict:
    """`instrument_id -> shares`, from orders **plus** corporate actions."""
    quantities: dict = defaultdict(float)
    for order in orders:
        quantities[order.instrument_id] += order.quantity
    for row in activities:
        if row.moves_position and not row.is_trade:
            quantities[row.instrument_id] += row.quantity
    return {k: v for k, v in quantities.items() if abs(v) > 1e-9}


def build_book(*, account_id: str, as_of: date, activities, orders, prices,
               account_type: str = "TFSA", base_currency: str = "CAD",
               fx_rate_used=None, reported_nav=None, sectors=None) -> tuple:
    """Assemble `CT-11.4`. Returns `(BookState, reconciliation_status)`.

    `prices` is `{instrument_id: (price, currency)}` from D-07. ⚠ **A position
    with no price makes the book unavailable, not smaller** — the same rule FX-3
    applies to rates, one level up.

    `reported_nav` is the balance read off a statement or the broker's screen.
    ★ **Without it the book is `UNRECONCILED`** (RC-51) and D-05 will refuse it.
    """
    quantities = derive_quantities(activities, orders)
    cash = derive_cash(activities)

    # ⏸ RC-58 — Canadian listings and CDRs are POSTPONED (Victor, 2026-08-25).
    #   Their positions are derived above; only the price lookup waits, because
    #   the FMP plan covers US listings only. ⚠ Until then a caller must supply
    #   prices for them or accept that the book cannot be valued — it is never
    #   valued at a substituted price.
    missing = [i for i in quantities if i not in (prices or {})]
    if missing:
        from src.recording.errors import RecordingError

        raise RecordingError(
            f"{account_id}: no price for {sorted(missing)!r}. A position with "
            f"no price makes the book unavailable, not smaller (RC-10, FX-3)")

    positions = []
    for instrument_id, quantity in sorted(quantities.items()):
        price, currency = prices[instrument_id]
        symbol, wrapper, venue_currency = instrument_id.split("|")
        positions.append(Position(
            instrument_id=instrument_id, analysis_symbol=symbol,
            quantity=quantity, market_value=round(quantity * price, 2),
            currency=currency or venue_currency, account_id=account_id,
            sector=(sectors or {}).get(symbol, "")))

    by_currency: dict = defaultdict(float)
    for position in positions:
        by_currency[position.currency] += position.market_value
    for currency, amount in cash.items():
        by_currency[currency] += amount
    nav = reported_nav if reported_nav is not None else {
        k: round(v, 2) for k, v in by_currency.items()}

    breaks = compute_breaks(positions, cash, nav, account_id=account_id)
    state = BookState(
        account_id=account_id, date=as_of, positions=tuple(positions),
        cash_by_currency=cash, nav_by_currency=dict(nav),
        base_currency=base_currency,
        nav_base=_nav_base(nav, dict(fx_rate_used or {}), base_currency),
        fx_rate_used=dict(fx_rate_used or {}),
        reconciled=BREAK if breaks else OK, breaks=breaks,
        account_type=account_type)
    # ⚠ RC-51 — `ok` here means the arithmetic closes, and with a derived NAV
    #   it closes **by construction**. The status says which happened.
    status = OK if reported_nav is not None else UNRECONCILED
    return state, status


def _nav_base(nav, fx_rate_used, base_currency):
    total = 0.0
    for currency, amount in nav.items():
        if currency == base_currency:
            total += float(amount)
            continue
        rate = fx_rate_used.get(currency)
        if rate is None:
            return None
        total += float(amount) * float(rate)
    return round(total, 2)
