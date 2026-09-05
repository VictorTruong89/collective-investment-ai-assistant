"""D-11 §5 — valuing a CDR without CIBC's ratio. RC-27, RC-52, RC-58.

```text
╔══════════════════════════════════════════════════════════════════╗
║  ⏸  POSTPONED — Victor, 2026-08-25 (RC-58)                        ║
║                                                                  ║
║  Canadian-listed stocks and CDRs are NOT VALUED until the rest    ║
║  of the code is complete. Their POSITIONS are still derived,     ║
║  grouped and reconciled — only the market-value step waits.       ║
║                                                                  ║
║  The reason is outside the code: the FMP plan covers US listings  ║
║  only. Every .TO / .NE symbol returns 402, so BBD.B, MDA and BMO  ║
║  have no quote, and MRV / SPCX have no usable underlying.         ║
║                                                                  ║
║  ⚠ A CDR is a SEPARATE STOCK that tracks a US underlying. Its     ║
║    price is NOT the underlying's price, and nothing here may      ║
║    substitute one for the other. The method below tracks the      ║
║    RETURN, never the price — which is why it stays valid while    ║
║    being unexercised.                                            ║
╚══════════════════════════════════════════════════════════════════╝
```


```text
╔══════════════════════════════════════════════════════════════════╗
║  A CDR IS PRICED FROM ITS CAD COST BASIS AND THE UNDERLYING'S    ║
║  USD RETURN — NEVER BY RECONSTRUCTING IT FROM THE RATIO.         ║
║                                                                  ║
║  1. It is RATIO-AGNOSTIC. CIBC's ratio is precisely the number   ║
║     FMP cannot supply, and CIBC adjusts it to pass through hedge ║
║     costs and dividends.                                          ║
║  2. It matches how the programme is BUILT — currency-hedged, so  ║
║     the CDR delivers the USD return without the FX leg.          ║
║  3. It is SELF-CHECKING: every closed round trip yields the true ║
║     CAD exit from the sell row, so the error is observable.      ║
║                                                                  ║
║  Measured over 8 closed round trips: mean signed error -0.08 pts ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **It needs an underlying with a USD price.** `SPCX` (SpaceX) is private — no
US listing, no CIK, no EDGAR (§5.3) — so it has no underlying return.

⚠⚠ **FMP nonetheless answers `SPCX` with "Space Exploration Technologies Cor,
NASDAQ, USD".** The spec says that listing does not exist, so the two disagree
about a fact — and **D-11 does not silently pick the vendor.** `SPCX` is treated
as unpriceable until the disagreement is resolved (§4c: *neither is assumed
right*).
"""


from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: ⚠ Instruments whose vendor quote contradicts what the spec records about the
#: security. **Not a blocklist of bad tickers** — a list of open disagreements.
QUOTE_CONTRADICTS_SPEC = frozenset({"SPCX"})

UNPRICEABLE_NO_UNDERLYING = "no_us_underlying"
UNPRICEABLE_NOT_ON_PLAN = "not_on_fmp_plan"


@dataclass(frozen=True, slots=True)
class Valuation:
    instrument_id: str
    quantity: float
    market_value: float | None
    currency: str
    method: str
    why: str = ""

    @property
    def priced(self) -> bool:
        return self.market_value is not None

    def to_json_obj(self) -> dict:
        return {"instrument_id": self.instrument_id, "quantity": self.quantity,
                "market_value": self.market_value, "currency": self.currency,
                "method": self.method, "why": self.why}


def value_cdr(*, instrument_id: str, quantity: float, cost_basis_cad: float,
              underlying_at_cost: float | None,
              underlying_now: float | None) -> Valuation:
    """RC-52 — ★ `cost_basis × (P_now / P_at_cost)`, in CAD, ratio-free.

    ⚠ Returns **unpriced** rather than a guess when either underlying price is
    missing: *the CDR is designed to deliver the USD return*, and with no return
    there is nothing to deliver.
    """
    if not underlying_at_cost or not underlying_now:
        return Valuation(instrument_id, quantity, None, "CAD",
                         UNPRICEABLE_NO_UNDERLYING,
                         "no US underlying price at cost and/or now — a private "
                         "underlying (SPCX) has neither")
    factor = underlying_now / underlying_at_cost
    return Valuation(instrument_id, quantity, round(cost_basis_cad * factor, 2),
                     "CAD", "cdr_underlying_return",
                     f"CAD cost {cost_basis_cad:.2f} x USD return {factor:.4f}")


#: ⚠ RC-53 — a valuation whose quote currency differs from the venue currency.
UNPRICEABLE_WRONG_VENUE = "quote_currency_mismatch"


def value_direct(*, instrument_id: str, quantity: float, price: float | None,
                 currency: str, quote_currency: str | None = None) -> Valuation:
    """A listing we can quote outright — ⚠ **only if the quote is the same
    listing.**

    ★★ **RC-53, measured 2026-08-25.** A bare ticker is ambiguous across venues
    and FMP answers with the **US** listing:

    | Held | FMP returned | |
    |---|---|---|
    | `MDA` on TSX, CAD | *MDA Space Ltd*, **NYSE, USD** | right company, wrong venue |
    | `BMO` on TSX, CAD | *Bank of Montreal*, **NYSE, USD** | right company, wrong venue |

    ⚠ **This is more dangerous than the 402s.** A plan-gated symbol refuses
    loudly; a same-named US listing returns a **plausible number in the wrong
    currency**, and a CAD book that adds it is wrong by the FX rate — silently.
    ★ So the quote's currency must match the venue's, or the position is
    **unavailable, never converted** (FX-3's shape).
    """
    if price is None:
        return Valuation(instrument_id, quantity, None, currency,
                         UNPRICEABLE_NOT_ON_PLAN,
                         "the vendor plan does not cover this listing (HTTP 402 "
                         "means 'not on your plan', never 'no data' — DE-46)")
    if quote_currency and quote_currency != currency:
        return Valuation(
            instrument_id, quantity, None, currency, UNPRICEABLE_WRONG_VENUE,
            f"the quote is {quote_currency} and the position is held in "
            f"{currency} — a same-named listing on another venue. Unavailable, "
            f"never converted (RC-53, FX-3)")
    return Valuation(instrument_id, quantity, round(quantity * price, 2),
                     currency, "vendor_quote")


def cost_basis(orders, instrument_id: str) -> tuple[float, date | None]:
    """CAD (or native) cash actually paid for the shares still held, and the
    date of the most recent opening trade.

    ⚠ Simplified to the **last opening order**: the CDR method scales a cost
    basis by a return, and mixing lots opened at different underlying prices
    needs per-lot tracking this slice does not have (RC-52's open edge).
    """
    opens = [o for o in orders
             if o.instrument_id == instrument_id and o.quantity > 0]
    if not opens:
        return 0.0, None
    latest = max(opens, key=lambda o: o.trade_date)
    return abs(latest.total_amount), latest.trade_date
