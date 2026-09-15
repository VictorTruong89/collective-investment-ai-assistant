"""`T3` — the pure two-stage DCF mechanics (`AC-F10.1`, `.2`, `.3`).

★ **One coherent design (`D2`):** free cash flow TO THE FIRM, discounted at a
FIRM rate, gives enterprise value; equity value = enterprise value − net debt;
per share = equity ÷ diluted shares.

⚠⚠ **`D-19`, the inherited defect this module must never repeat:** the old
`DCFCalculator` computed an enterprise value and divided it by shares with no
net-debt subtraction — 455 % of market cap on CHTR. `per_share` takes net debt
as a REQUIRED argument, so the omission cannot be expressed.

★ **Rounding (`MO-5`, `CT-F10.2`):** every monetary intermediate is rounded to
minor units exactly once, and enterprise value is the exact sum of the rounded
present values — the trail adds up to the cent. Rates and discount factors stay
`Decimal` at a fixed 40-digit context, so the result is deterministic (`INV-2`).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext

from src.feature_engineer.errors import NoFiniteValueError
from src.shared.money import Money

#: `AC-3.14` — the method this module implements has a MethodEntry.
FORMULA_ID = "dcf.two_stage_fcff_firm_rate.v1"

#: Decimal precision for rates and factors. ★ Fixed, so a result never depends
#: on a caller's ambient decimal context (`INV-2`).
_PRECISION = 40


@dataclass(frozen=True, slots=True)
class Flow:
    year: int
    fcff: Money
    discount_factor: Decimal
    present_value: Money

    def to_json_obj(self) -> dict:
        return {"year": self.year, "fcff": self.fcff.to_json_obj(),
                "discount_factor": str(self.discount_factor),
                "present_value": self.present_value.to_json_obj()}


@dataclass(frozen=True, slots=True)
class DcfTrail:
    flows: tuple[Flow, ...]
    terminal_fcff: Money
    terminal_value: Money
    terminal_present_value: Money
    enterprise_value: Money


def discount(base_fcff: Money, *, discount_rate: Decimal, stage1_growth: Decimal,
             terminal_growth: Decimal, explicit_years: int) -> DcfTrail:
    """Years `1…N` grow at `stage1_growth`; Gordon growth at `terminal_growth` after.

    Refuses `discount_rate ≤ terminal_growth` (no finite terminal value) and
    `explicit_years < 1` — never clamps (`AC-F10.3`, `P5`).
    """
    for name, value in (("discount_rate", discount_rate), ("stage1_growth", stage1_growth),
                        ("terminal_growth", terminal_growth)):
        if not isinstance(value, Decimal):
            raise TypeError(f"{name} must be Decimal, got {type(value).__name__} (MO-3)")
    if discount_rate <= terminal_growth:
        raise NoFiniteValueError(
            f"discount rate {discount_rate} ≤ terminal growth {terminal_growth}: the terminal "
            f"value has no finite answer (F10 AC-F10.3)")
    if explicit_years < 1:
        raise NoFiniteValueError(f"explicit_years {explicit_years} < 1 (F10 AC-F10.3)")

    with localcontext() as ctx:
        ctx.prec = _PRECISION
        one = Decimal(1)
        flows = []
        for year in range(1, explicit_years + 1):
            fcff = base_fcff.mul_rate((one + stage1_growth) ** year)
            factor = one / (one + discount_rate) ** year
            flows.append(Flow(year, fcff, factor, fcff.mul_rate(factor)))
        terminal_fcff = base_fcff.mul_rate(
            (one + stage1_growth) ** explicit_years * (one + terminal_growth))
        terminal_value = terminal_fcff.mul_rate(one / (discount_rate - terminal_growth))
        terminal_pv = terminal_value.mul_rate(flows[-1].discount_factor)
    enterprise = terminal_pv
    for flow in flows:
        enterprise = enterprise + flow.present_value
    return DcfTrail(tuple(flows), terminal_fcff, terminal_value, terminal_pv, enterprise)


def per_share(enterprise_value: Money, net_debt: Money, diluted_shares: int
              ) -> tuple[Money, Money]:
    """`AC-F10.2` — `(equity, value per share)`. ★ Net debt is required (`D-19`)."""
    if type(diluted_shares) is not int or diluted_shares <= 0:
        raise NoFiniteValueError(
            f"diluted shares {diluted_shares!r} must be a positive integer — a per-share "
            f"value over no shares has no answer (F10 AC-F10.3)")
    equity = enterprise_value - net_debt
    return equity, equity.div_int(diluted_shares)


def value_per_share_at(base_fcff: Money, net_debt: Money, diluted_shares: int, *,
                       discount_rate: Decimal, stage1_growth: Decimal,
                       terminal_growth: Decimal, explicit_years: int) -> Money:
    """The one composition the band and implied expectations reuse."""
    trail = discount(base_fcff, discount_rate=discount_rate, stage1_growth=stage1_growth,
                     terminal_growth=terminal_growth, explicit_years=explicit_years)
    return per_share(trail.enterprise_value, net_debt, diluted_shares)[1]
