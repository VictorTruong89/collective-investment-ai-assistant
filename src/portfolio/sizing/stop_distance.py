"""D-06 §5.2 — the stop distance. PS-6, PS-7, PS-23.

★ **A stop picked by eye is an unstated volatility assumption** — and, through
`entry / d`, an unstated **position-size** decision.

    stop_distance = k · σ̂ · √h · entry     ⇒     shares ∝ 1 / σ̂
"""

from __future__ import annotations

import math
from dataclasses import dataclass

FORMULA_ID = "stop_distance_vol_v1"

#: PS-6 — `k` is configuration and is **stated on every answer**.
DEFAULT_K = 1.5

#: HorizonSet v1's holding horizon.
DEFAULT_HORIZON_DAYS = 21

#: PS-23 — ★ **realised volatility is a labelled stand-in, never called a
#: forecast.** ⚠ *The distinction is not pedantry: realised vol is
#: backward-looking and understates exactly when it matters — before an earnings
#: gap.* D-09 renders the label (RP-1).
FORECAST, REALISED = "forecast", "realised"


@dataclass(frozen=True, slots=True)
class StopDistance:
    per_share: float
    k: float
    sigma: float
    sigma_source: str
    sigma_class: str
    horizon_days: int

    def to_json_obj(self) -> dict:
        return {"stop_distance_per_share": round(self.per_share, 6),
                "implied_k": round(self.k, 6), "sigma": self.sigma,
                "sigma_source": self.sigma_source,
                "sigma_class": self.sigma_class,
                "horizon_days": self.horizon_days}


def stop_distance(*, entry: float, sigma: float, sigma_source: str,
                  sigma_class: str = REALISED, k: float = DEFAULT_K,
                  horizon_days: int = DEFAULT_HORIZON_DAYS) -> StopDistance:
    """PS-6 — the principled form, with `k` and `σ̂`'s class on the answer."""
    if sigma_class not in (FORECAST, REALISED):
        raise ValueError(
            f"sigma_class {sigma_class!r} must be {FORECAST!r} or {REALISED!r}. "
            f"★ PS-23: realised volatility is a stand-in and is never called a "
            f"forecast")
    return StopDistance(per_share=k * sigma * math.sqrt(horizon_days) * entry,
                        k=k, sigma=sigma, sigma_source=sigma_source,
                        sigma_class=sigma_class, horizon_days=horizon_days)


def implied_k(*, entry: float, stop: float, sigma: float, sigma_source: str,
              sigma_class: str = REALISED,
              horizon_days: int = DEFAULT_HORIZON_DAYS) -> StopDistance:
    """PS-7 — ★ the human's own stop, with the `k` it implies.

    *A stop at 0.4σ and a stop at 3σ are different decisions and the number
    makes that visible.*
    """
    distance = entry - stop
    scale = sigma * math.sqrt(horizon_days) * entry
    return StopDistance(per_share=distance,
                        k=(distance / scale) if scale else float("inf"),
                        sigma=sigma, sigma_source=sigma_source,
                        sigma_class=sigma_class, horizon_days=horizon_days)
