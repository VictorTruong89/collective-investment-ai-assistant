"""Growth, margin trend, the Piotroski components and sector-relative z-scores.

★★ **These are computed PER FILING and joined afterwards — never the reverse.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  Measured 2026-08-27, and it is why this module is shaped this    ║
║  way:  a 120-day panel window contains THREE distinct NVDA        ║
║  filings.  A four-filing lag computed on the joined frame is      ║
║  therefore null for every row — not because the history is        ║
║  missing, but because the JOIN threw it away first.               ║
║                                                                  ║
║  So: canonical (one row per reported period, full history)        ║
║      -> growth, trend, Piotroski                                  ║
║      -> as-of join onto the daily panel                           ║
║                                                                  ║
║  The joined frame also repeats one filing's values across every   ║
║  day until the next lands, so a day-window `.diff()` on it        ║
║  measures the FILING CALENDAR rather than the company.            ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **Sorted by `period_end`, compared within `period_type`.** RA-149's lesson in
another domain: one filing carries its own period *and the prior-year
comparative*, so filing order is not period order. PIT visibility is already
settled — `get_fundamentals` filtered on `filing_date` before any of this.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.feature_engineer.fundamental.ratios import (
    _col,
    _ratio,
    gross_margin,
    net_margin,
    operating_margin,
)

#: Compare like with like. ⚠ A four-*filing* lag spans a different length of time
#: for a 10-K than a 10-Q, and CT-7.2 carries both.
_BY = ["ticker", "period_type"]


def _ordered(canonical: pd.DataFrame) -> pd.DataFrame:
    return canonical.sort_values(["ticker", "period_type", "period_end"],
                                 kind="mergesort")


def change(canonical: pd.DataFrame, item: str, *, lag: int) -> pd.Series:
    """Fractional change in `item` versus `lag` reported periods ago.

    ⚠ Denominated on `abs(prior)` so a swing from −100 to +50 reads as a
    *rise*. Dividing by a signed prior flips the sign of every recovery from a
    loss, which is the one case a growth feature most needs to get right.
    """
    ordered = _ordered(canonical)
    values = _col(ordered, item)
    prior = values.groupby([ordered[c] for c in _BY], sort=True).shift(lag)
    out = _ratio(values - prior, prior.abs(), allow_negative=True)
    return out.reindex(canonical.index)


def rolling_change(canonical: pd.DataFrame, item: str, *, periods: int = 4) -> pd.Series:
    """Change in the trailing `periods`-period SUM versus the prior one.

    ★ The trailing sum is what makes a seasonal business comparable — Q4 retail
    against Q4 retail rather than Q4 against Q3.
    """
    ordered = _ordered(canonical)
    values = _col(ordered, item)
    keys = [ordered[c] for c in _BY]
    summed = (values.groupby(keys, sort=True)
                    .rolling(periods, min_periods=periods).sum()
                    .reset_index(level=list(range(len(keys))), drop=True))
    prior = summed.groupby(keys, sort=True).shift(periods)
    out = _ratio(summed - prior, prior.abs(), allow_negative=True)
    return out.reindex(canonical.index)


def margin_trend(canonical: pd.DataFrame, which: str, *, periods: int = 4) -> pd.Series:
    """OLS slope of a margin over the last `periods` reported periods.

    ★ Units are *margin points per period*, so the slope is only comparable
    between filers on the same reporting cadence — which `_BY` enforces.

    ⚠ `min_periods=periods` and any null in the window yields null: **a line
    through two points is a line, not a trend**, and `polyfit` returns one
    without complaint.
    """
    builder = {"net": net_margin, "gross": gross_margin,
               "operating": operating_margin}[which]
    ordered = _ordered(canonical)
    margins = builder(ordered)
    keys = [ordered[c] for c in _BY]

    def slope(window) -> float:
        y = np.asarray(window, dtype="float64")
        if np.isnan(y).any():
            return np.nan
        return float(np.polyfit(np.arange(len(y), dtype="float64"), y, 1)[0])

    out = (margins.groupby(keys, sort=True)
                  .rolling(periods, min_periods=periods).apply(slope, raw=True)
                  .reset_index(level=list(range(len(keys))), drop=True))
    return out.reindex(canonical.index)


# --------------------------------------------------------------------------- #
# Piotroski
# --------------------------------------------------------------------------- #

def piotroski(canonical: pd.DataFrame) -> dict:
    """The F-score and its three sub-scores.

    ★ **The parts are published beside the total.** A 6 built from profitability
    differs from a 6 built from leverage and a single integer cannot say which —
    the argument RA-62 makes for reporting two stability figures rather than one.

    ⚠⚠ **Piotroski's original is nine binary signals; this is seven, and it is
    scored out of seven.** The two omitted need a share count at two dates
    (dilution) and a gross-margin history a bank never reports. ★ Stated rather
    than silently scored out of nine — *7/7 and 7/9 are different claims*.
    """
    from src.feature_engineer.fundamental.ratios import accruals, roa

    profitability = _sum_signals(
        _positive(roa(canonical)),
        _positive(_ratio(_col(canonical, "operating_cash_flow"),
                         _col(canonical, "total_assets"))),
        _positive(change(canonical, "net_income", lag=4)),
        # ★ Sloan's accrual signal, inverted: LOW accruals score.
        _positive(-accruals(canonical)),
    )
    leverage = _sum_signals(
        _negative(change(canonical, "total_liabilities", lag=4)),
        _positive(change(canonical, "current_assets", lag=4)),
    )
    efficiency = _sum_signals(_positive(change(canonical, "revenue", lag=4)))

    return {
        "f_piotroski_profitability": profitability,
        "f_piotroski_leverage": leverage,
        "f_piotroski_efficiency": efficiency,
        "f_piotroski_f": _sum_signals(profitability, leverage, efficiency),
    }


def _sum_signals(*parts: pd.Series) -> pd.Series:
    """Sum, ★ **null if any part is null** — never treating unknown as failure.

    ⚠ `pandas.sum` skips NaN by default, which would score a bank's missing
    margin signals as zeros and report a low F-score for a company that was
    never tested. *"We could not tell"* and *"it failed"* are different facts
    (FE-14), and only one of them should reach a ranking.
    """
    stacked = pd.concat(parts, axis=1)
    out = stacked.sum(axis=1, skipna=False)
    return out.astype("float64")


def _positive(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").astype("float64")
    out = (values > 0).astype("float64")
    out[values.isna()] = np.nan
    return out


def _negative(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").astype("float64")
    out = (values < 0).astype("float64")
    out[values.isna()] = np.nan
    return out


# --------------------------------------------------------------------------- #
# Sector-relative z-scores — ★ computed AFTER the join, on the daily panel
# --------------------------------------------------------------------------- #

def sector_z(panel: pd.DataFrame, values: pd.Series, sectors: pd.Series) -> pd.Series:
    """z-score **within `(date, sector)`**.

    ★★ Two groupings, both load-bearing:

      * **by date** — FE-13's hazard. Pooling dates scores a 2019 row against
        2026's distribution, which is the future leaking backwards.
      * **by sector** — the point of the feature. *A 4 % net margin is poor for
        software and excellent for grocery*, and the un-normalised column makes
        the model rediscover sector membership instead of using it.

    ⚠ Null when the `(date, sector)` cell has **fewer than three names or zero
    spread**: a z-score over two observations is ±0.707 by construction and says
    nothing about the company (CN-10 — say so rather than emit it).

    ★ This is the one feature here that **cannot** be computed per filing: it
    needs the cross-section as it stood on a given day.
    """
    frame = pd.DataFrame({
        "date": pd.to_datetime(panel["date"]).to_numpy(),
        "sector": pd.Series(sectors).astype("object").to_numpy(),
        "_v": pd.to_numeric(values, errors="coerce").to_numpy(),
    })
    grouped = frame.groupby(["date", "sector"], sort=True, dropna=False)["_v"]
    mean = grouped.transform("mean")
    sd = grouped.transform("std")
    count = grouped.transform("count")
    out = (frame["_v"] - mean) / sd
    out[(count < 3) | ~(sd > 0)] = np.nan
    # ★★ FE-41 (DX-160) — an UNKNOWN sector is null, never a bucket of its own.
    #   ⚠ `dropna=False` above pooled every missing sector together: with no map,
    #   all five *_sector_z were market-wide z-scores under sector-relative names.
    unknown = frame["sector"].isna() | (frame["sector"].astype(str).str.strip() == "")
    out[unknown] = np.nan
    return pd.Series(out.to_numpy(), index=panel.index, dtype="float64")
