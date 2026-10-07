"""D-03 §5.3b / §7.2 — rank IC, effective N, and the corrected SE. QA-4, QA-5.

★★ **Overlapping labels are the whole problem.** At horizon `h` with daily
observations, consecutive labels share `h−1` days of return, so `T` dates do not
give `T` independent observations — they give about `T/h`.

```
    SE(mean IC) ≈ √( h / ((n−1)·T) )      MDE(t*) = t* · √( h / ((n−1)·T) )
```

⚠ **MDE is computable BEFORE anything is measured** — it is the bar, not a
prediction. ★ **QA-5**: a 1q RankIC of 0.03 and a 1w RankIC of 0.03 are **not
the same evidence**, because their effective N differs by ~12×.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

FORMULA_RANK_IC = "rank_ic.spearman.v1"
FORMULA_EFFECTIVE_N = "effective_n.overlap_corrected.v1"
FORMULA_MDE = "mde.rank_ic.v1"
#: ★ F12 `D9` / AC-F12.31 — the realised SE the IC gate decides on (closes L6 AB-12).
FORMULA_REALISED_SE = "se.newey_west_bartlett.v1"

NOT_EVALUATED = "NOT_EVALUATED"

#: The multiple-testing threshold §5.3b uses for its published table.
T_MULTIPLE_TESTING = 3.0


@dataclass(frozen=True, slots=True)
class ICResult:
    """★ QA-4 — every reported statistic carries its **effective sample size**
    and an autocorrelation-corrected standard error."""

    horizon_days: int
    mean_ic: float | None
    dates: int
    names_per_date: float
    effective_n: float | None
    corrected_se: float | None
    formula_id: str = FORMULA_RANK_IC
    status: str = "measured"
    why: str = ""
    #: ★ F12 `D9` — the per-date IC series and its REALISED standard error
    #: (Newey-West, `h − 1` lags). The gate decides on this; `corrected_se`
    #: (the NULL SE) stays as the planning figure / MDE.
    per_date: tuple = ()
    realised_se: float | None = None

    @property
    def t_stat_realised(self) -> float | None:
        """`D9` — the t the gate actually uses."""
        if self.mean_ic is None or not self.realised_se:
            return None
        return self.mean_ic / self.realised_se

    @property
    def t_stat(self) -> float | None:
        """⚠ Against the **corrected** SE, never the naive one (QA-4)."""
        if self.mean_ic is None or not self.corrected_se:
            return None
        return self.mean_ic / self.corrected_se

    def mde(self, t_star: float = T_MULTIPLE_TESTING) -> float | None:
        """★ The bar, computable before anything is measured."""
        return None if self.corrected_se is None else t_star * self.corrected_se

    def to_json_obj(self) -> dict:
        return {"horizon_days": self.horizon_days, "mean_ic": self.mean_ic,
                "dates": self.dates, "names_per_date": self.names_per_date,
                "effective_n": self.effective_n,
                "corrected_se": self.corrected_se,
                "t_stat": self.t_stat, "mde_t3": self.mde(),
                "realised_se": self.realised_se,
                "t_stat_realised": self.t_stat_realised,
                "realised_se_formula_id": FORMULA_REALISED_SE,
                "formula_id": self.formula_id, "status": self.status,
                "why": self.why}


def effective_n(*, dates: int, horizon_days: int) -> float:
    """`T / h` — ★ **overlapping labels cut the independent count.**

    ⚠ Using `T` is the error QA-5 exists to prevent: it inflates every t-stat by
    `√h`, which at 1m is **4.6×** and turns noise into a passing gate.
    """
    return dates / horizon_days if horizon_days else 0.0


def corrected_se(*, dates: int, names_per_date: float,
                 horizon_days: int) -> float | None:
    """`√( h / ((n−1)·T) )` — §5.3b, and the denominator of every gate."""
    if dates <= 0 or names_per_date <= 1 or horizon_days <= 0:
        return None
    return math.sqrt(horizon_days / ((names_per_date - 1) * dates))


def newey_west_se(series, *, lags: int) -> float | None:
    """`se.newey_west_bartlett.v1` — the realised SE of a series' MEAN (F12 `D9`).

    ```
    e_t = x_t − x̄ ;  γ_k = (1/T) Σ_{t>k} e_t·e_{t−k} ;  w_k = 1 − k/(L+1)
    Var(x̄) = (γ_0 + 2 Σ_{k=1..L} w_k·γ_k) / T
    ```

    ★ **`L = h − 1`** for per-date ICs of `h`-day labels: consecutive labels share
    `h − 1` days, so their ICs are autocorrelated over that window. The null SE
    assumes per-date IC variance `1/(n−1)` — true only with no skill — and the
    realised spread was 3.5× that on the August 2026 fit (L6 AB-12).
    ⚠ Fewer than `L + 2` observations cannot estimate the window → `None`; a
    non-positive variance (possible with Bartlett weights on tiny samples) → `None`.
    """
    xs = [float(x) for x in series]
    n = len(xs)
    if lags < 0 or n < lags + 2:
        return None
    mean = sum(xs) / n
    e = [x - mean for x in xs]

    def gamma(k):
        return sum(e[t] * e[t - k] for t in range(k, n)) / n

    var = gamma(0) + 2.0 * sum((1.0 - k / (lags + 1.0)) * gamma(k)
                               for k in range(1, lags + 1))
    var /= n
    return math.sqrt(var) if var > 0 else None


def rank_ic(predictions: pd.DataFrame, *, horizon_days: int,
            score_column: str = "score",
            label_column: str = "value") -> ICResult:
    """QA-4 — cross-sectional Spearman IC per date, then its mean.

    ⚠ **Per date, then averaged** — never pooled across dates. A pooled
    correlation mixes the cross-section with the time series and answers a
    question nobody asked.

    ⚠ **QA-17: a statistic that cannot be computed reports `NOT_EVALUATED`, not
    a pass.** A date with fewer than two names has no cross-section, and a
    horizon with no usable dates has no IC.
    """
    per_date, widths = [], []
    for _, group in predictions.groupby("date", sort=True):
        usable = group[[score_column, label_column]].dropna()
        if len(usable) < 2:
            continue                    # no cross-section on this date
        value = usable[score_column].corr(usable[label_column], method="spearman")
        if pd.isna(value):
            continue                    # zero variance — undefined, not zero
        per_date.append(float(value))
        widths.append(len(usable))

    if not per_date:
        return ICResult(
            horizon_days=horizon_days, mean_ic=None, dates=0,
            names_per_date=0.0, effective_n=None, corrected_se=None,
            status=NOT_EVALUATED,
            why=("no date had a usable cross-section of at least two names. "
                 "★ QA-17: a statistic that cannot be computed is NOT_EVALUATED, "
                 "never a pass"))

    dates = len(per_date)
    width = sum(widths) / dates
    return ICResult(
        horizon_days=horizon_days, mean_ic=sum(per_date) / dates, dates=dates,
        names_per_date=round(width, 4),
        effective_n=round(effective_n(dates=dates, horizon_days=horizon_days), 4),
        corrected_se=corrected_se(dates=dates, names_per_date=width,
                                  horizon_days=horizon_days),
        per_date=tuple(per_date),
        realised_se=newey_west_se(per_date, lags=max(horizon_days - 1, 0)))


def assert_comparable(a: ICResult, b: ICResult) -> None:
    """QA-5 — ★ **horizons in one set are never compared on raw metric value.**

    *A 1q RankIC of 0.03 and a 1w RankIC of 0.03 are not the same evidence.*
    """
    from src.quant.errors import QuantError

    if a.horizon_days != b.horizon_days:
        raise QuantError(
            f"comparing a {a.horizon_days}d IC with a {b.horizon_days}d IC on "
            f"raw value. Their effective N differs by "
            f"~{max(a.horizon_days, b.horizon_days) / min(a.horizon_days, b.horizon_days):.1f}x "
            f"— compare t-statistics against corrected SEs instead (QA-5, QA-4)")
