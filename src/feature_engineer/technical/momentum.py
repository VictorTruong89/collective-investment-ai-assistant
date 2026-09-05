"""The one feature B3 builds — `mom_21` (L3 BS-10: one ticker, one feature).

```
FE-28: the day-T feature row uses data available at the DAY-T OPEN —
everything through the T-1 close, plus the settled day-T opening print.
Nothing from later in session T may enter it.
```

★ **Both ends on the same field, and the field is `adj_open`.** That is QA-71's
argument for labels applied to a feature: a ratio of `open` to `close` carries a
systematic intraday drift the model will happily fit, and D-08 §5A decides at the
open, so the open is the anchor available at decision time.

⚠ **This is exactly the column D-07 had to be told to build.** `adj_open` was
assigned to D-07 by three specs and appeared nowhere in its contract until
2026-08-18 (DE-42); `open` *"has never been consumed by any feature or label"*
(FE-30). This feature is the first consumer, so B2's `adj_open_minor` stops being
a column nothing reads.
"""

from __future__ import annotations

import pandas as pd

#: The formula identity. **Changing the maths changes this** (FE-2, §5.2), and a
#: `formula_id` with no MethodEntry fails the build (D-03 QA-20, AC-3.14).
FORMULA_ID = "momentum.open_to_open_ratio.v1"

#: Lookback in trading sessions. 21 = one month, matching HorizonSet v1's h1m —
#: the production horizon (CT-3.1). A POLICY CHOICE, and it is the contract's
#: `note` rather than a bare literal because a reader must be able to see it
#: (CN-1, CN-3).
LOOKBACK_SESSIONS = 21


def open_to_open_return(panel: pd.DataFrame, *, lookback: int) -> pd.Series:
    """`adj_open(t) / adj_open(t − lookback) − 1`, per ticker, aligned to `panel`.

    ★ **FE-32 — this is where the Money type is left.** The inputs are
    `adj_open_minor` (integer minor units, `L2-shared-money` CT-M.1); the output
    is a **dimensionless ratio and is no longer money** (MO-8). The division
    happens once, here, in D-02. ⚠ Cross-currency ratios are forbidden — a ratio
    only means something within one currency — so the currency column is checked
    rather than assumed.

    ⚠ **PD-5/PD-6**: sort explicitly, then `groupby(ticker).shift`. A bare
    `.shift()` on a stacked panel gives each ticker's first rows the *previous
    ticker's* tail, and pandas emits no warning.
    """
    required = {"ticker", "date", "adj_open_minor", "adj_open_currency"}
    missing = sorted(required - set(panel.columns))
    if missing:
        raise KeyError(
            f"mom_21 needs {missing} from CT-7.1. Its inputs are declared in the "
            f"FeatureSpec and it may read nothing else (FE-17)"
        )

    for ticker, grp in panel.groupby("ticker", sort=True):
        codes = set(grp["adj_open_currency"])
        if len(codes) > 1:
            raise ValueError(
                f"{ticker}: adj_open spans currencies {sorted(codes)}. A ratio across "
                f"currencies is dimensionless only by accident and means nothing "
                f"(FE-32, INV-5)"
            )

    ordered = panel.sort_values(["ticker", "date"], kind="mergesort")
    now = ordered["adj_open_minor"].astype("float64")
    then = ordered.groupby("ticker", sort=True)["adj_open_minor"].shift(lookback).astype("float64")

    # DE-14 / FE-14: a zero prior price is not a 0% return and not an infinity —
    # it is unknown, and unknown is null. Never imputed to a plausible middle.
    out = (now / then) - 1.0
    out[then <= 0] = pd.NA
    return out.astype("float64").reindex(panel.index)


#: The second B3 feature. ⚠ **L3's B3 text says "one feature"; this is two, and
#: the reason is a contract, not appetite.** D-03's `ranked_quantity` is the
#: DENORMALISED return `z_hat * sigma_hat * sqrt(h)` (QA-58, QA-119) — publishing
#: only `z` would let a consumer rank on the normalised quantity, which is the
#: low-vol tilt QA-58 exists to remove. That needs a volatility estimate, and
#: **a volatility computed inside D-03 would be a derived number outside D-02**
#: (D-02 §1.2, FE-4). So it is a feature. Two features is not "deep"; an
#: un-denormalised ranking is a seam that would be expensive to move later.
VOL_FORMULA_ID = "volatility.realised_open_to_open_std.v1"
VOL_WINDOW_SESSIONS = 21


def realised_vol(panel: pd.DataFrame, *, window: int) -> pd.Series:
    """Realised daily volatility — the sample sd of open-to-open log returns.

    ⚠ **`min_periods=window`** (PD-9). The pandas default silently emits a value
    computed from fewer observations, so a 21-day sd built from 3 days is
    indistinguishable in the output from a real one.
    """
    import numpy as np

    ordered = panel.sort_values(["ticker", "date"], kind="mergesort")
    px = ordered["adj_open_minor"].astype("float64")
    prev = ordered.groupby("ticker", sort=True)["adj_open_minor"].shift(1).astype("float64")
    log_ret = np.log(px / prev)
    log_ret[(prev <= 0) | (px <= 0)] = np.nan
    out = (log_ret.groupby(ordered["ticker"], sort=True)
                  .rolling(window, min_periods=window).std(ddof=1)
                  .reset_index(level=0, drop=True))
    return out.reindex(panel.index).astype("float64")


# --------------------------------------------------------------------------- #
# Named specs. ★★ **FE-4 — one feature, one owning module.**
#
# `ret_5d` and `mom_21` are the SAME arithmetic at two lookbacks, so they share
# one implementation and differ only in a parameter. ⚠ Writing the ratio twice
# is how a domain acquires two definitions of one concept — *"two
# implementations of one concept is the defect this domain exists to remove"*.
#
# ★ These thin wrappers stay because **`b3_minimal@v1` is published and FE-2
# makes it immutable**: its FeatureSpecs name `owner_module="technical.momentum"`
# and renaming the callable would break a contract that models are parity-checked
# against.
# --------------------------------------------------------------------------- #

def mom_21(panel: pd.DataFrame, *, lookback: int = LOOKBACK_SESSIONS) -> pd.Series:
    """`b3_minimal@v1`'s momentum feature."""
    return open_to_open_return(panel, lookback=lookback)


def vol_21(panel: pd.DataFrame, *, window: int = VOL_WINDOW_SESSIONS) -> pd.Series:
    """`b3_minimal@v1`'s volatility feature."""
    return realised_vol(panel, window=window)
