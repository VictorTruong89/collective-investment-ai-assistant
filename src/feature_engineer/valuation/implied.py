"""Implied expectations — the stage-1 growth the price requires (`D7`, `AC-F10.10`).

★ It answers *"the price requires X % a year for N years"* — the sentence `J-09`
reasons about — by bisection over the declared bracket, a fixed number of
iterations, so the answer is deterministic (`INV-2`).

⚠ **No root in the bracket is an answer, not a failure to hide** (`P5`): when
the price lies outside the values the bracket can produce, the status says so
and the growth is null — never the nearest bracket end, which would read as a
real, extreme expectation.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext

from src.feature_engineer.valuation.assumptions import Assumptions
from src.feature_engineer.valuation.dcf import discount, value_per_share_at
from src.feature_engineer.valuation.types import DurationRow, Implied
from src.shared.money import Money

#: `AC-3.14` — the method this module implements has a MethodEntry.
FORMULA_ID = "implied.stage1_growth_bisection.v1"
_SOLVES_FOR = "stage1_growth"
#: Stored precision of the solved growth — far finer than one minor unit per share.
_QUANTUM = Decimal("1e-12")


def solve_implied(*, price: Money, base_fcff: Money, net_debt: Money, diluted_shares: int,
                  assumptions: Assumptions) -> Implied:
    def gap(growth: Decimal) -> int:
        vps = value_per_share_at(base_fcff, net_debt, diluted_shares,
                                 discount_rate=assumptions.discount_rate,
                                 stage1_growth=growth,
                                 terminal_growth=assumptions.terminal_growth,
                                 explicit_years=assumptions.explicit_years)
        return (vps - price).amount_minor           # ⚠ raises on a currency mismatch

    low, high = assumptions.implied_low, assumptions.implied_high
    f_low, f_high = gap(low), gap(high)
    if f_low == 0 or f_high == 0:
        growth = low if f_low == 0 else high
        return Implied(_SOLVES_FOR, "SOLVED", growth, Money(0, price.currency))
    if (f_low > 0) == (f_high > 0):
        return Implied(_SOLVES_FOR, "NO_ROOT_IN_BRACKET", None, None)

    with localcontext() as ctx:
        ctx.prec = 40
        for _ in range(assumptions.implied_iterations):
            mid = ((low + high) / 2).quantize(_QUANTUM)
            f_mid = gap(mid)
            if f_mid == 0:
                low = high = mid
                break
            if (f_mid > 0) == (f_low > 0):
                low, f_low = mid, f_mid
            else:
                high = mid
        growth = ((low + high) / 2).quantize(_QUANTUM)
    return Implied(_SOLVES_FOR, "SOLVED", growth, Money(gap(growth), price.currency))


#: `D11` — stored precision of a share of revenue (a ratio of same-currency money, `FE-32`).
_SHARE_QUANTUM = Decimal("1e-6")


def implied_by_duration(*, price: Money, base_fcff: Money, net_debt: Money, diluted_shares: int,
                        assumptions: Assumptions, trailing_revenue: Money | None = None
                        ) -> tuple[DurationRow, ...]:
    """`D10` / `AC-F10.22` — `D7`'s solve at each declared period, ONLY `explicit_years`
    replaced, so the row for the set's own period equals `implied`. `()` when the set
    declares no table. ✏ `D11` / `AC-F10.23` — each solved row also states the final
    explicit-year FCFF of the SAME `discount` trail and it ÷ trailing revenue."""
    rows = []
    for years in assumptions.duration_years:
        at = replace(assumptions, explicit_years=years)
        implied = solve_implied(price=price, base_fcff=base_fcff, net_debt=net_debt,
                                diluted_shares=diluted_shares, assumptions=at)
        if implied.value is None:
            rows.append(DurationRow(years, implied))
            continue
        final = discount(base_fcff, discount_rate=at.discount_rate, stage1_growth=implied.value,
                         terminal_growth=at.terminal_growth, explicit_years=years).flows[-1].fcff
        if trailing_revenue is None or final.currency != trailing_revenue.currency:
            raise ValueError("D11 needs trailing revenue in the valuation's currency (FE-32)")
        with localcontext() as ctx:
            ctx.prec = 40
            share = (Decimal(final.amount_minor) / Decimal(trailing_revenue.amount_minor)
                     ).quantize(_SHARE_QUANTUM)
        rows.append(DurationRow(years, implied, final, share))
    return tuple(rows)
