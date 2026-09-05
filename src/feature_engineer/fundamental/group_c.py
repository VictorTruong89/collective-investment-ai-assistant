"""§5.3's two Group-C features, and the market-cap join they share.

★ These are the last two of the declared 61 — and the only ones that need a
**price**, which is why they were left until the panel carried one.

```text
   f_graham_number_ratio   sqrt(22.5 * EPS * BVPS) / price - 1     (value)
   f_moat_quant_score      profitability level + stability + growth  (quality)
   f_market_to_book        market_cap / book equity                (valuation)
```

⚠⚠ **All three are ANCHORS.** They carry the price by construction, so RA-14 and
**RA-151** keep them out of D-01's blind passes — they belong to the `computed`
part kind, which `BLIND_WITHHELD_KINDS` strips. They are legitimate model inputs
and forbidden narrative inputs, which is why §6.2 and §6.3 publish different sets
to the two seats.

★ **Priced on `adj_open(t)`, not on the close at the filing date.** The legacy
joined `adj_close` as of the filing; FE-28 says the day-T row may use the day-T
**open**, and QA-71 says both ends of a ratio belong on one field. Using the open
also makes the feature available at the moment D-08 decides.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.feature_engineer.fundamental.ratios import _col, _ratio

#: Graham's constant — `22.5 = 15 (P/E) × 1.5 (P/B)`. ⚠ A **1949 heuristic**,
#: carried because §5.3 declares the feature, not because it was re-derived.
GRAHAM_CONSTANT = 22.5

#: Trailing filings the moat score looks over. 8 quarters ≈ two years.
MOAT_WINDOW = 8

#: ★ Component weights. ⚠ **An admitted guess inherited verbatim** (CN-10) —
#: nothing measured them, and they are stated here rather than buried in the
#: expression so a reader can see there is no evidence behind 0.5/0.2/0.3.
MOAT_WEIGHTS = {"level": 0.5, "stability": 0.2, "growth": 0.3}

#: ROA level mapped onto `[0, 1]`: −10 % → 0, +15 % → 1.
MOAT_ROA_FLOOR, MOAT_ROA_CAP = -0.10, 0.15


def market_cap(panel: pd.DataFrame, joined: pd.DataFrame) -> pd.Series:
    """`adj_open(t) × diluted_shares` — ⚠ **an anchor** (RA-151).

    ★ Shares come from the **as-of joined filing**, price from the day's own
    open, so both halves are knowable at the decision moment (FE-28).
    """
    if "adj_open_minor" not in panel.columns:
        return pd.Series(np.nan, index=panel.index, dtype="float64")
    price = panel["adj_open_minor"].astype("float64") / 100.0
    shares = _col(joined, "diluted_shares")
    out = price * shares
    out[~(shares > 0)] = np.nan            # FE-14 — unknown, never zero
    return out.astype("float64")


def graham_number(joined: pd.DataFrame) -> pd.Series:
    """`√(22.5 × EPS × BVPS)` — ★ **undefined unless both are positive.**

    ⚠ The legacy clipped the product at zero before the square root, which turns
    *"this company lost money"* into a Graham number of **0.00** — a finite,
    plottable, rankable number for a case where the formula has no answer. FE-14:
    the answer to undefined is null.
    """
    shares = _col(joined, "diluted_shares")
    eps = _ratio(_col(joined, "net_income"), shares)
    equity = _col(joined, "stockholders_equity")
    bvps = _ratio(equity, shares)

    product = GRAHAM_CONSTANT * eps * bvps
    out = np.sqrt(product.where((eps > 0) & (bvps > 0)))
    return out.replace([np.inf, -np.inf], np.nan).astype("float64")


def graham_number_ratio(panel: pd.DataFrame, joined: pd.DataFrame) -> pd.Series:
    """`graham_number ÷ price − 1` — positive means *cheap on Graham's rule*."""
    if "adj_open_minor" not in panel.columns:
        return pd.Series(np.nan, index=panel.index, dtype="float64")
    price = panel["adj_open_minor"].astype("float64") / 100.0
    number = graham_number(joined)
    out = _ratio(number, price) - 1.0
    return out.astype("float64")


def moat_quant_score(canonical: pd.DataFrame) -> pd.Series:
    """Profitability **level + stability + growth consistency**, in `[0, 1]`.

    ⚠⚠ **Two corrections to the inherited formula, both measured:**

    ★ **The stability term was a near-constant carrying a 20 % weight.** The
    legacy computed `c_stab = clip(1 − std(ROA), 0, 1)`. Quarterly ROA standard
    deviation for a large filer runs **0.01–0.05**, so `c_stab` spanned
    **0.95–0.99** — a fifth of the score that could not distinguish anything.
    It is now the **coefficient of variation**, `1 / (1 + std/|mean|)`, which is
    scale-free and uses the company's own history.

    ⚠ *A cross-sectional rank was tried first and abandoned:* **no two filers
    share a fiscal calendar**, so grouping dispersion by `period_end` gave every
    group one member and nulled the entire column. Measured 2026-08-27 —
    NVDA 0.980, WMT 0.633 on the CV form.

    ★ **`fillna` is removed.** The legacy filled missing stability with the
    column **minimum** (the worst value — a judgement disguised as a fill) and
    missing growth with **0.5** (the neutral midpoint). FE-14: *missing is null,
    never a mean.* A component that cannot be computed nulls the score rather
    than scoring the company as average or as worst.

    ⚠ The weights `0.5 / 0.2 / 0.3` are **inherited and unmeasured** (CN-10).
    """
    ordered = canonical.sort_values(["ticker", "period_type", "period_end"],
                                    kind="mergesort")
    roa = _ratio(_col(ordered, "net_income"), _col(ordered, "total_assets"))
    revenue = _col(ordered, "revenue")
    keys = [ordered["ticker"], ordered["period_type"]] \
        if "period_type" in ordered.columns else [ordered["ticker"]]

    level = (roa.groupby(keys, sort=True)
                .rolling(MOAT_WINDOW, min_periods=2).mean()
                .reset_index(level=list(range(len(keys))), drop=True))
    spread = (roa.groupby(keys, sort=True)
                 .rolling(MOAT_WINDOW, min_periods=2).std(ddof=1)
                 .reset_index(level=list(range(len(keys))), drop=True))
    # ⚠ **`fill_method=None`.** Pandas' default forward-fills NAs *before*
    #   differencing, which manufactures a 0 % change across a gap — a silent
    #   imputation of exactly the kind FE-14 forbids.
    change = revenue.groupby(keys, sort=True).pct_change(fill_method=None)
    growth = (change.groupby(keys, sort=True)
                    .rolling(MOAT_WINDOW, min_periods=2)
                    .apply(lambda s: float(np.mean(np.asarray(s) > 0)), raw=True)
                    .reset_index(level=list(range(len(keys))), drop=True))

    c_level = ((level.clip(MOAT_ROA_FLOOR, MOAT_ROA_CAP) - MOAT_ROA_FLOOR)
               / (MOAT_ROA_CAP - MOAT_ROA_FLOOR))
    # ★★ **Coefficient of variation, not a cross-sectional rank.** ⚠ The first
    #   attempt ranked dispersion within `period_end` — and **no two filers share
    #   a fiscal calendar**, so every group had one member and the whole column
    #   was null. A company's own `std/|mean|` needs no peer group at all.
    c_stability = 1.0 / (1.0 + _ratio(spread, level.abs(), allow_negative=False))
    c_growth = growth.clip(0.0, 1.0)

    score = (MOAT_WEIGHTS["level"] * c_level
             + MOAT_WEIGHTS["stability"] * c_stability
             + MOAT_WEIGHTS["growth"] * c_growth)
    return score.clip(0.0, 1.0).reindex(canonical.index).astype("float64")



