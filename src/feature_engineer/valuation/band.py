"""The sensitivity band — the value over the declared grid (`AC-F10.9`).

★ It reuses `value_per_share_at`, the one composition of the mechanics, so a
band point and the point estimate can never disagree about arithmetic.
"""

from __future__ import annotations

from src.feature_engineer.valuation.assumptions import Assumptions
from src.feature_engineer.valuation.dcf import value_per_share_at
from src.feature_engineer.valuation.types import Band, BandPoint
from src.shared.money import Money


def band(base_fcff: Money, net_debt: Money, diluted_shares: int, *,
         assumptions: Assumptions) -> Band:
    grid = tuple(
        BandPoint(r, g, value_per_share_at(base_fcff, net_debt, diluted_shares,
                                           discount_rate=r,
                                           stage1_growth=assumptions.stage1_growth,
                                           terminal_growth=g,
                                           explicit_years=assumptions.explicit_years))
        for r in assumptions.band_discount for g in assumptions.band_terminal)
    values = [p.value_per_share for p in grid]
    return Band(grid=grid, low=min(values), high=max(values))
