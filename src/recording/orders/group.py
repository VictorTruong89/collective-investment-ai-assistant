"""D-11 §8 — trades grouped into orders. RC-14, RC-15, H-1, H-7.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A TRANCHE IS NOT A TRADE, AND THE COMMISSION RESIDUAL IS THE    ║
║  EVIDENCE.                                                       ║
║                                                                  ║
║  ENB, RRSP, 2026-04-13 — two rows at the same price:             ║
║     35 x 74.37  total -2605.53  -> residual 2.58                 ║
║    100 x 74.37  total -7444.37  -> residual 7.37                 ║
║                                                                  ║
║  Per tranche the residual is meaningless. Grouped into ONE       ║
║  order:  135 x 74.37  total -10049.90  -> residual 9.95          ║
║                                                                  ║
║  9.95 is what BMO charges. The grouping is not a tidiness        ║
║  preference — it is what makes the fee derivable at all.         ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **RC-14: trades are grouped into orders BEFORE anything counts them.**
★ **RC-15: commission is DERIVED — `Total Amount − (−Q×P)` per order.**
⚠ *A hard-coded fee constant is a modelling assumption wearing the word
"reality".*
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.recording.errors import CommissionImplausibleError

#: L4 CN-2 — a world fact with its source and check date. **BMO InvestorLine
#: flat equity commission, $9.95, confirmed against the 2026 exports.**
#: ⚠ Used only to *sanity-check* a derived value; it is never substituted for
#: one (RC-15).
BMO_FLAT_COMMISSION = 9.95

#: ★ **MEASURED across all 137 orders in the four 2026 exports**, not guessed:
#:
#: | Derived fee | Count | Cause |
#: |---|---|---|
#: | `9.95` exactly | **100** | the flat fee, CAD and USD alike |
#: | `9.93 … 11.30` | 25 | ★ **price rounding**, and the deviation **scales with
#:   quantity** — the statement prints `Price` to 2dp while the fill carried
#:   more, so `Σ|qᵢ|·pᵢ` drifts by ≈ `0.005 × qty` |
#: | `0.00` | 2 | **ZCN** — BMO charges no commission on its own ETFs |
#: | `19.90` | 1 | ★ **two orders merged**: SPCX, 4 tranches, one day. `19.90`
#:   is `2 × 9.95`, and the fee is the only evidence — **the export carries no
#:   order id** |
BMO_ETF_FREE = frozenset({"ZCN", "ZSP", "ZEA", "ZAG", "ZQQ"})

#: The floor absorbs float noise; the slope is the price-rounding term above.
COMMISSION_TOLERANCE_FLOOR = 0.06
COMMISSION_TOLERANCE_PER_SHARE = 0.006

#: ⚠ How many same-day orders the fee may reveal before it is a defect rather
#: than a merge. Measured max: 2.
MAX_MERGED_ORDERS = 4

#: ★ **USD SELLS carry an extra charge above the flat fee, and we do not know
#: what it is.** Measured over the four exports: every order whose residual
#: exceeds `9.95` by more than price-rounding explains is a **USD sell** —
#: `MU −23 → 10.13`, `INTC −115 → 10.39`, `ARM −70 → 10.71`, `ENB −220 → 11.30`.
#: A US regulatory transaction fee (SEC Section 31, sells only) is the obvious
#: candidate and **does not fit the magnitudes**, so it is not asserted.
#: ⚠ **The excess is carried on the order as `residual_unexplained` rather than
#: absorbed into the tolerance** — RA-79's principle applied to fees: *a
#: plausible reason attached to an unexplained residual is strictly worse than
#: the honest gap.*
USD_SELL_ALLOWANCE = 1.60

#: Money is exact; this absorbs float noise in `Q × P` only.
CENT = 0.005


@dataclass(frozen=True, slots=True)
class Order:
    """One order, assembled from one or more tranches (RC-14)."""

    account_id: str
    trade_date: date
    symbol: str
    instrument_id: str
    analysis_symbol: str
    side: str
    quantity: float
    price: float
    currency: str
    total_amount: float
    tranches: int
    commission: float
    is_cdr: bool
    #: ★ The part of the fee no rule here explains — see USD_SELL_ALLOWANCE.
    #: ⚠ Reported, never absorbed.
    residual_unexplained: float = 0.0
    implied_order_count: int = 1

    @property
    def notional(self) -> float:
        return abs(self.quantity) * self.price

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id,
                "trade_date": self.trade_date.isoformat(), "symbol": self.symbol,
                "instrument_id": self.instrument_id,
                "analysis_symbol": self.analysis_symbol, "side": self.side,
                "quantity": self.quantity, "price": self.price,
                "currency": self.currency, "notional": round(self.notional, 4),
                "total_amount": self.total_amount, "tranches": self.tranches,
                "commission": round(self.commission, 4), "is_cdr": self.is_cdr,
                "residual_unexplained": round(self.residual_unexplained, 4),
                "implied_order_count": self.implied_order_count}


def order_key(activity):
    """★ What makes two rows one order: same account, day, instrument, side.

    ⚠ **Price is deliberately NOT in the key, and the data is why.** A first
    attempt included it — one order, one price, seemed obvious. **BMO fills a
    single order at several prices** and charges the fee once:

    ```
    2026-04-29  Buy NVDA CDR  200 @ 47.68   total -9545.48   -> 9.48
    2026-04-29  Buy NVDA CDR   10 @ 47.69   total  -477.37   -> 0.47
                                              grouped        -> 9.95
    ```

    ★ Keying on price splits that into two orders whose residuals are
    meaningless, which is **H-1's defect reproduced by the parser** rather than
    inherited from the vendor.
    """
    return (activity.account_id, activity.trade_date, activity.instrument_id,
            activity.activity)


def group_orders(activities, *, strict: bool = True) -> tuple[Order, ...]:
    """RC-14 → RC-15, in that order and for that reason."""
    buckets: dict = {}
    for a in activities:
        if not a.is_trade:
            continue
        buckets.setdefault(order_key(a), []).append(a)

    out = []
    for key, rows in sorted(buckets.items(), key=lambda kv: (str(kv[0][1]), str(kv[0]))):
        account_id, trade_date, instrument_id, side = key
        quantity = sum(r.quantity or 0.0 for r in rows)
        total = sum(r.total_amount or 0.0 for r in rows)
        first = rows[0]
        # ★ Notional is summed PER TRANCHE — `Σ|qᵢ|·pᵢ`, never `Q_total × p̄`.
        #   The tranches carry different prices, so a blended price would move
        #   the notional and take the derived fee with it.
        notional = sum(abs(r.quantity or 0.0) * (r.price or 0.0) for r in rows)
        # ⚠ RC-12 — **a zero `Total Amount` is a TRANCHE, not an absence.**
        #   Measured: MU RRSP 2026-05-06 books 550 shares' cash on the first row
        #   and leaves the second at 0. Dropping it loses 300 shares from the
        #   book while the cash still balances.
        price = round(notional / abs(quantity), 6) if quantity else 0.0
        commission = derive_commission(notional=notional, total_amount=total)
        if strict:
            assert_plausible(f"{account_id} {trade_date} {instrument_id}",
                             commission, tranches=len(rows), quantity=quantity,
                             symbol=first.symbol)
        out.append(Order(
            account_id=account_id, trade_date=trade_date, symbol=first.symbol,
            instrument_id=instrument_id, analysis_symbol=first.analysis_symbol,
            side=side, quantity=quantity, price=price,
            currency=first.price_currency or first.total_currency or "",
            total_amount=total, tranches=len(rows), commission=commission,
            is_cdr=first.is_cdr,
            residual_unexplained=unexplained(commission, quantity=quantity),
            implied_order_count=implied_orders(
                commission, quantity=quantity, side=side) or 1))
    return tuple(out)


def derive_commission(*, notional: float, total_amount: float) -> float:
    """RC-15 — ★ `Total Amount − (−Q×P)`, and nothing is assumed.

    A buy has negative `Total Amount` and positive quantity; a sell the reverse.
    In both cases the fee is the amount by which cash moved *against* you
    relative to the pure notional.
    """
    if total_amount < 0:
        # BUY — cash leaves; you paid the notional PLUS the fee.
        return round(abs(total_amount) - notional, 4)
    # SELL — cash arrives; you received the notional MINUS the fee.
    return round(notional - total_amount, 4)


def unexplained(commission: float, *, quantity: float) -> float:
    """★ The part of the residual no rule here accounts for.

    ⚠ *A plausible reason attached to an unexplained residual is strictly worse
    than the honest gap* (D-01 RA-79, applied to fees). This number is carried
    onto the artifact so that when the cause is found it can be checked against
    a record, not against a memory.
    """
    nearest = round(commission / BMO_FLAT_COMMISSION) * BMO_FLAT_COMMISSION
    slack = max(COMMISSION_TOLERANCE_FLOOR,
                COMMISSION_TOLERANCE_PER_SHARE * abs(quantity))
    excess = abs(commission - nearest) - slack
    return round(max(0.0, excess), 4)


def implied_orders(commission: float, *, quantity: float,
                   side: str = "") -> int | None:
    """How many flat fees the residual accounts for — ★ the only evidence the
    export gives that two same-day orders were merged (it carries no order id).

    Returns `None` when the residual is not a plausible multiple.
    """
    tolerance = max(COMMISSION_TOLERANCE_FLOOR,
                    COMMISSION_TOLERANCE_PER_SHARE * abs(quantity))
    if side == "Sell":
        tolerance += USD_SELL_ALLOWANCE
    for k in range(0, MAX_MERGED_ORDERS + 1):
        if abs(commission - k * BMO_FLAT_COMMISSION) <= tolerance:
            return k
    return None


def assert_plausible(order_key_text: str, commission: float, *, tranches: int,
                     quantity: float, symbol: str = "") -> None:
    """RC-15 — ⚠ a residual that is not a multiple of the flat fee almost always
    means the tranches were not grouped, not that the fee changed.

    ★ The tolerance **scales with quantity** because the deviation does: the
    statement prints `Price` to 2dp, so `Σ|qᵢ|·pᵢ` drifts by about half a cent
    per share. A fixed tolerance passes small orders and fails large ones for a
    reason that has nothing to do with the fee.
    """
    if commission < -COMMISSION_TOLERANCE_FLOOR:
        raise CommissionImplausibleError(
            order_key_text, commission, "a NEGATIVE fee means cash moved in "
                                        "your favour beyond the notional.")
    if symbol.upper() in BMO_ETF_FREE and abs(commission) <= COMMISSION_TOLERANCE_FLOOR:
        return                       # ★ BMO charges nothing on its own ETFs
    if implied_orders(commission, quantity=quantity,
                      side="Sell" if quantity < 0 else "Buy") is None:
        raise CommissionImplausibleError(
            order_key_text, commission,
            f"it is not within tolerance of any multiple of "
            f"{BMO_FLAT_COMMISSION} (CN-2); {tranches} tranche(s) grouped, "
            f"quantity {quantity:g}.")


def assert_window_covers_positions(orders) -> dict:
    """RC-45 — ★★ **a negative derived quantity is evidence of a truncated
    activity window, not a short position.**

    ⚠ *Measured 2026-08-25:* replaying the four real exports (`From=2026-01-01`)
    yields `PLTR RESP −520`, `GOOG TFSA_2 −30`, `BBD.B RRSP −26`. Those lots
    were opened **before** the window — their sells are in the file and their
    buys are not — so **RC-9's derivation produces the wrong lot while the
    arithmetic looks perfectly healthy.**

    Returns the derived quantities; raises when any is negative.
    """
    from src.recording.errors import TruncatedWindowError

    quantities: dict = {}
    for order in orders:
        key = (order.account_id, order.instrument_id)
        quantities[key] = quantities.get(key, 0.0) + order.quantity
    short = {k: v for k, v in quantities.items() if v < -1e-9}
    if short:
        raise TruncatedWindowError(short)
    return quantities
