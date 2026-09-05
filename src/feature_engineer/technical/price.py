"""The 14 price / OHLCV features of §5.3, rebuilt on the open anchor.

★ **Ported from `backups/pipeline/ohlcv/dataset/ohlcv_feature_engineer.py` under
P4, but not carried over verbatim.** Three things in the legacy are defects here,
and each is fixed rather than inherited:

```text
╔══════════════════════════════════════════════════════════════════╗
║  1. LOOK-AHEAD ON THE CLOSE.  Every legacy feature reads         ║
║     adj_close(T).  FE-28: the day-T row may use everything       ║
║     through the T−1 CLOSE plus the settled day-T OPEN — and       ║
║     nothing later in session T.  The close of T is not known at   ║
║     the open of T, and the open of T is when this system decides. ║
║                                                                  ║
║  2. LOOK-AHEAD ON VOLUME.  `vol_zscore_5d` reads volume(T).      ║
║     A day's volume is not knowable at that day's open either —    ║
║     it is the one input where the legacy error is total rather    ║
║     than partial.  Volume here ends at T−1.                       ║
║                                                                  ║
║  3. EPSILON INSTEAD OF NULL.  `avg_loss + 1e-9` and              ║
║     `std + 1e-9` turn an UNDEFINED value into a plausible         ║
║     number.  FE-14: missing is null — never zero, never a mean.   ║
║     A flat 5-day volume window has no z-score, and saying so is   ║
║     the point.                                                    ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **`rsi_14` was also wrong, and it is a REGISTERED defect** — L5 **D-16**: the
legacy smooths with a rolling arithmetic mean where Wilder's RSI uses his own
recursive smoothing. §5.2 gives `formula_id` exactly this job: `rsi.wilder.v1`
versus `rsi.rolling_mean.v1`. This module implements **Wilder's**, so the id
names what the code does.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.feature_engineer.technical.momentum import (
    open_to_open_return, realised_vol,
)

#: ★ Every formula identity in one place. **Changing the maths changes the id**
#: (FE-2), and a `formula_id` with no MethodEntry fails the build (QA-20).
RETURN_FORMULA_ID = "momentum.open_to_open_ratio.v1"
VOL_FORMULA_ID = "volatility.realised_open_to_open_std.v1"
SMA_FORMULA_ID = "trend.open_to_sma_ratio.v1"
RSI_FORMULA_ID = "rsi.wilder.v1"
MACD_FORMULA_ID = "trend.macd_histogram_ewm_normalised.v1"
VOLUME_Z_FORMULA_ID = "volume.split_adjusted_zscore.v1"
RANK_FORMULA_ID = "cross_section.percentile_rank.v1"

#: MACD's three spans, Appel's originals.
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9

#: ⚠ **EWM has no natural start.** `ewm(span=26)` is recursive from the first row
#: it is given, so without a warm-up the same `as_of` over a 200-day window and a
#: 400-day window yields **different** `macd_hist` — an INV-2 concern, not a
#: rounding one, and invisible in any single run.
#:
#: ★ **Measured 2026-08-27, and the warm-up does its job.** The first row's
#: weight after `k` rows is `(1 − 2/27)^k`: `k=35 → 6.8e-2`, `k=78 → 2.5e-3`,
#: `k=156 → 6.1e-6`. At 78 sessions, windows carrying **30, 60, 120 and 240**
#: extra sessions of prior history all produced **the identical value**; only the
#: degenerate case of *no* prior history differed, by `4.3e-5` relative.
#:
#: ⚠ **So the dependence is BOUNDED, not removed** — an EWM never fully forgets.
#: 3× the slow span is the trade: 6× would tighten it to `6e-6` but the daily run
#: fetches ~138 sessions, and a 156-session warm-up would make this column
#: **entirely null in production**.
MACD_WARMUP_SESSIONS = MACD_SLOW * 3


def _assert_columns(panel: pd.DataFrame, needed, who: str) -> None:
    """FE-17 — a feature reads its declared inputs and nothing else."""
    missing = sorted(set(needed) - set(panel.columns))
    if missing:
        raise KeyError(
            f"{who} needs {missing} from CT-7.1. Its inputs are declared in the "
            f"FeatureSpec and it may read nothing else (FE-17)")


def _ordered(panel: pd.DataFrame) -> pd.DataFrame:
    """PD-5/PD-6 — sort explicitly before any shift or rolling window.

    ⚠ A bare `.shift()` on a stacked panel gives each ticker's first rows the
    *previous ticker's* tail, and pandas emits no warning.
    """
    return panel.sort_values(["ticker", "date"], kind="mergesort")


# --------------------------------------------------------------------------- #
# 1-4  returns — one implementation, four lookbacks (FE-4)
# --------------------------------------------------------------------------- #

def ret(panel: pd.DataFrame, *, lookback: int) -> pd.Series:
    """`adj_open(t) / adj_open(t − lookback) − 1`.

    ★ Both ends on `adj_open`: QA-71's rule, because *a ratio of open to close
    carries a systematic intraday drift the model will happily fit* — and the
    open is what is available when D-08 decides.
    """
    return open_to_open_return(panel, lookback=lookback)


# --------------------------------------------------------------------------- #
# 5-7  SMA ratios
# --------------------------------------------------------------------------- #

def sma_ratio(panel: pd.DataFrame, *, window: int) -> pd.Series:
    """`adj_open(t) ÷ mean(adj_open over the window ending at t)`.

    ⚠ **`min_periods=window`** (PD-9). Pandas' default for a fixed window is the
    window itself, but stating it is what stops a later refactor to a
    time-based offset from silently emitting a 50-day mean built from three days.
    """
    _assert_columns(panel, ("ticker", "date", "adj_open_minor"), f"sma_{window}_ratio")
    ordered = _ordered(panel)
    px = ordered["adj_open_minor"].astype("float64")
    mean = (px.groupby(ordered["ticker"], sort=True)
              .rolling(window, min_periods=window).mean()
              .reset_index(level=0, drop=True))
    out = px / mean
    # FE-14 — a zero or absent mean is unknown, never 1.0 and never infinity.
    out[~(mean > 0)] = np.nan
    return out.reindex(panel.index).astype("float64")


# --------------------------------------------------------------------------- #
# 8-9  realised volatility — one implementation, two windows (FE-4)
# --------------------------------------------------------------------------- #

def vol(panel: pd.DataFrame, *, window: int) -> pd.Series:
    """Sample sd of open-to-open log returns over `window` sessions."""
    return realised_vol(panel, window=window)


# --------------------------------------------------------------------------- #
# 10  RSI — ★ Wilder's, which closes L5 D-16
# --------------------------------------------------------------------------- #

def rsi_wilder(panel: pd.DataFrame, *, period: int = 14) -> pd.Series:
    """Wilder's RSI on `adj_open`, in `[0, 100]`.

    ★★ **L5 D-16 — the legacy is not Wilder's.** It averages gains and losses
    with `rolling(14).mean()`, a simple arithmetic mean over a flat window.
    Wilder smooths recursively — `avg = (avg_prev × (n−1) + today) / n`, an EMA
    with `α = 1/n` — which weights recent sessions more and has a longer memory
    than 14 sessions. ⚠ The two agree on trend and disagree on level, so the
    legacy is *plausible everywhere and correct nowhere*, which is why it
    survived: nothing looks wrong.

    ⚠ **No epsilon.** The legacy divides by `avg_loss + 1e-9`, which turns the
    genuinely undefined case into `99.999…`. Here:

      * `avg_loss == 0` with gains ⇒ **exactly 100** — the correct limit, and a
        real state (fourteen sessions without a down move).
      * both zero ⇒ **null** — a perfectly flat window has no RSI, and FE-14
        says the answer to *unknown* is null, not a plausible middle.
    """
    _assert_columns(panel, ("ticker", "date", "adj_open_minor"), "rsi_14")
    ordered = _ordered(panel)
    px = ordered["adj_open_minor"].astype("float64")
    delta = px.groupby(ordered["ticker"], sort=True).diff()

    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    # ★ Wilder's smoothing IS an EWM with alpha = 1/period. `adjust=False` is
    #   what makes it the recursive form rather than the weighted-average one;
    #   with adjust=True the early values differ and the series never converges
    #   to the same recursion.
    avg_gain = (gain.groupby(ordered["ticker"], sort=True)
                    .transform(lambda s: s.ewm(alpha=1 / period, adjust=False,
                                               min_periods=period).mean()))
    avg_loss = (loss.groupby(ordered["ticker"], sort=True)
                    .transform(lambda s: s.ewm(alpha=1 / period, adjust=False,
                                               min_periods=period).mean()))

    out = pd.Series(np.nan, index=ordered.index, dtype="float64")
    both_zero = (avg_gain == 0) & (avg_loss == 0)
    no_loss = (avg_loss == 0) & (avg_gain > 0)
    ordinary = avg_loss > 0

    rs = avg_gain[ordinary] / avg_loss[ordinary]
    out[ordinary] = 100.0 - (100.0 / (1.0 + rs))
    out[no_loss] = 100.0
    out[both_zero] = np.nan               # FE-14 — flat is unknown, not 50

    return out.reindex(panel.index).astype("float64")


# --------------------------------------------------------------------------- #
# 11  MACD histogram
# --------------------------------------------------------------------------- #

def macd_hist(panel: pd.DataFrame, *, fast: int = MACD_FAST, slow: int = MACD_SLOW,
              signal: int = MACD_SIGNAL,
              warmup: int = MACD_WARMUP_SESSIONS) -> pd.Series:
    """`EMA(fast) − EMA(slow)`, less its own `EMA(signal)`, on `adj_open`.

    ⚠ **Nulled until `warmup` sessions have passed** — see `MACD_WARMUP_SESSIONS`.
    An EWM is recursive from whatever row it starts on, so without this the same
    `(ticker, date, as_of)` yields different values depending on how much history
    the caller loaded. **That is INV-2**, and it is invisible in any single run.
    """
    _assert_columns(panel, ("ticker", "date", "adj_open_minor"), "macd_hist")
    ordered = _ordered(panel)
    px = ordered["adj_open_minor"].astype("float64")
    grouped = px.groupby(ordered["ticker"], sort=True)

    ema_fast = grouped.transform(lambda s: s.ewm(span=fast, adjust=False).mean())
    ema_slow = grouped.transform(lambda s: s.ewm(span=slow, adjust=False).mean())
    macd = ema_fast - ema_slow
    line = (macd.groupby(ordered["ticker"], sort=True)
                .transform(lambda s: s.ewm(span=signal, adjust=False).mean()))

    hist = macd - line

    # ★★ **Normalised by the slow EMA, and this is a DEPARTURE from the legacy.**
    #
    # ⚠ The inherited `macd_hist` is a price DIFFERENCE, so it carries the price
    # LEVEL: measured 2026-08-26, `SNDK` (≈ $1 499) emitted **2007** where `AAPL`
    # (≈ $313) emitted **3.1**. ★ Every other feature in `price_ohlcv@v1` is
    # scale-invariant — returns, ratios, z-scores, percentile ranks — and a
    # CROSS-SECTIONAL ranker fed one dollar-denominated column learns *"expensive
    # stocks have big MACD"*, which is true and worthless.
    #
    # ★ `formula_id` exists for exactly this (§5.2: *changing the maths changes
    # this*), so the id says `_normalised` and an old model cannot silently
    # parity-match against the new arithmetic.
    out = hist / ema_slow
    out[~(ema_slow > 0)] = np.nan          # FE-14 — unknown, never 0.0

    seen = grouped.cumcount() + 1
    out[seen < warmup] = np.nan
    return out.reindex(panel.index).astype("float64")


# --------------------------------------------------------------------------- #
# 12  volume z-score
# --------------------------------------------------------------------------- #

def volume_zscore(panel: pd.DataFrame, *, window: int = 5) -> pd.Series:
    """z-score of **split-adjusted** volume over the window ending at **T−1**.

    ⚠⚠ **Two corrections to the legacy, and both are look-ahead or nonsense:**

    ★ **It ends at T−1, not T.** A day's volume is only known once the day is
    over, and this system decides at the **open** (FE-28). Reading `volume(T)` in
    the day-T row is not a partial error like reading the close — the whole
    quantity is unknowable.

    ★ **Volume is split-adjusted** via `adj_factor`. A 10:1 split multiplies
    share volume by ~10 overnight, and a 5-day window straddling it produces a
    z-score of several sigma from an event that moved no value. FE-9 says a
    non-scale-invariant input is computed on the raw series — a *z-score* is
    scale-invariant, but only once the level it normalises is on one scale.

    ⚠ **No epsilon.** A flat window has `sd = 0` and **no z-score**; the legacy's
    `+ 1e-9` reports a number in the millions instead of saying so.
    """
    _assert_columns(panel, ("ticker", "date", "volume", "adj_factor"), "vol_zscore_5d")
    ordered = _ordered(panel)

    factor = ordered["adj_factor"].astype("float64")
    shares = ordered["volume"].astype("float64")
    # ★ `adj_factor` scales price down across a split, so volume scales UP by the
    #   same factor to keep `price × volume` (traded value) invariant.
    adjusted = shares.where(~(factor > 0), shares * factor)

    lagged = adjusted.groupby(ordered["ticker"], sort=True).shift(1)
    grouped = lagged.groupby(ordered["ticker"], sort=True)
    mean = grouped.rolling(window, min_periods=window).mean().reset_index(level=0, drop=True)
    sd = grouped.rolling(window, min_periods=window).std(ddof=1).reset_index(level=0, drop=True)

    out = (lagged - mean) / sd
    out[~(sd > 0)] = np.nan               # FE-14 — a flat window has no z-score
    return out.reindex(panel.index).astype("float64")


# --------------------------------------------------------------------------- #
# 13-14  cross-sectional ranks
# --------------------------------------------------------------------------- #

def cross_sectional_rank(panel: pd.DataFrame, values: pd.Series, *,
                         ascending: bool) -> pd.Series:
    """Percentile rank **within one date only**.

    ★★ FE-13's hazard, one contract out. ⚠ *Ranking over the pooled sample leaks
    the future distribution into the past* — a 2019 row would be scored against
    2026's cross-section. The `groupby("date")` is the whole guard, and it is the
    same defect `_cross_section_rank` exists for, where a `pd.qcut` inside a
    `groupby.transform` silently returned NaN for **77 % of training rows**.

    ⚠ A date with a single rankable name yields `1.0` at any `ascending`, which
    is true and useless; it is left as-is rather than nulled, because *"the
    cross-section has one member"* is a fact about the universe, not about the
    feature.
    """
    frame = pd.DataFrame({"date": panel["date"], "_v": values})
    return (frame.groupby("date", sort=True)["_v"]
                 .rank(pct=True, ascending=ascending)
                 .reindex(panel.index).astype("float64"))
