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

from decimal import Decimal, localcontext

from src.feature_engineer.valuation.assumptions import Assumptions
from src.feature_engineer.valuation.dcf import value_per_share_at
from src.feature_engineer.valuation.types import Implied
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
