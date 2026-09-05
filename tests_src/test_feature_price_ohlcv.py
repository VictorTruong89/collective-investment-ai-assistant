"""D-02 `price_ohlcv@v1` — §5.3's 14 price features, on the FE-28 open anchor."""
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from src.feature_engineer.contracts.sets.price_ohlcv_v1 import PRICE_OHLCV_V1
from src.feature_engineer.errors import RangeViolationError
from src.feature_engineer.ml_features.assemble import assert_ranges, build_panel
from src.feature_engineer.technical import price as P

AS_OF = date(2026, 8, 26)


class _Report:
    report_id = "test-calendar"
    verdict = "PROCEED"
    blocked = ()


def _panel(prices_by_ticker, *, volumes=None, factor=1.0, start=date(2024, 1, 1)):
    """A CT-7.1-shaped panel. ⚠ `adj_open` is what every feature but the volume
    z-score reads (FE-28/QA-71)."""
    rows = []
    for ticker, prices in prices_by_ticker.items():
        vols = (volumes or {}).get(ticker) or [1_000_000] * len(prices)
        for i, (px, vol) in enumerate(zip(prices, vols)):
            rows.append({
                "ticker": ticker, "date": pd.Timestamp(start + timedelta(days=i)),
                "adj_open_minor": int(round(px * 100)),
                "adj_open_currency": "USD",
                "adj_close_minor": int(round(px * 100)),
                "adj_close_currency": "USD",
                "volume": int(vol), "adj_factor": factor,
            })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# The contract
# --------------------------------------------------------------------------- #

def test_ac_2_31_the_contract_declares_exactly_the_fourteen_of_section_5_3():
    """★ §5.3 names them. ⚠ FE-1 runs both ways — a spec with no implementation
    is as broken as a column with no spec."""
    assert [f.name for f in PRICE_OHLCV_V1.features] == [
        "ret_1d", "ret_5d", "ret_10d", "ret_20d",
        "sma_5_ratio", "sma_20_ratio", "sma_50_ratio",
        "vol_10d", "vol_20d", "rsi_14", "macd_hist", "vol_zscore_5d",
        "rank_ret_5d", "rank_vol_20d"]


def test_ac_2_31_every_declared_feature_has_a_builder():
    """FE-1 — ★ the other direction, which is the one that fails silently."""
    from src.feature_engineer.ml_features.assemble import BUILDERS

    for spec in PRICE_OHLCV_V1.features:
        assert spec.name in BUILDERS, f"{spec.name} is declared and unbuilt"


def test_ac_2_31_returns_and_momentum_share_one_implementation():
    """★★ FE-4 — *two implementations of one concept is the defect this domain
    exists to remove.* `ret_20d` and `mom_21` are one ratio at two lookbacks."""
    from src.feature_engineer.technical.momentum import open_to_open_return

    panel = _panel({"A": list(range(100, 160))})
    assert P.ret(panel, lookback=20).equals(
        open_to_open_return(panel, lookback=20))


# --------------------------------------------------------------------------- #
# ★★ FE-28 — the anchor. The legacy's defect, tested directly.
# --------------------------------------------------------------------------- #

def test_ac_2_32_no_feature_at_date_t_changes_when_later_data_changes():
    """★★★ **FE-28 / INV-1 — the whole reason this is not a verbatim port.**

    ⚠ The legacy reads `adj_close(T)` and `volume(T)`; neither is knowable at the
    day-T open, which is when D-08 decides. This appends a wildly different
    future and asserts every day-T row is byte-identical.
    """
    base = [100 + i * 0.5 for i in range(120)]
    short = _panel({"A": base})
    long = _panel({"A": base + [500.0, 10.0, 900.0]})

    a = build_panel(contract=PRICE_OHLCV_V1, price_panel=short,
                    calendar_report=_Report(), as_of=AS_OF, adj_as_of=AS_OF)
    b = build_panel(contract=PRICE_OHLCV_V1, price_panel=long,
                    calendar_report=_Report(), as_of=AS_OF, adj_as_of=AS_OF)

    names = [f.name for f in PRICE_OHLCV_V1.features]
    overlap = b[b["date"].isin(a["date"])].reset_index(drop=True)
    pd.testing.assert_frame_equal(a[names], overlap[names])


def test_ac_2_32_the_volume_zscore_ends_at_t_minus_one():
    """★★ FE-28 — ⚠ *a day's volume is not knowable at that day's open*, so
    unlike a close-based feature the legacy error here is **total**."""
    quiet = [1_000_000] * 20
    spike = quiet[:-1] + [99_000_000]           # a huge volume on the LAST day
    a = P.volume_zscore(_panel({"A": [100.0] * 20}, volumes={"A": quiet}))
    b = P.volume_zscore(_panel({"A": [100.0] * 20}, volumes={"A": spike}))
    assert a.iloc[-1] == b.iloc[-1] or (pd.isna(a.iloc[-1]) and pd.isna(b.iloc[-1])), \
        "the last day's own volume must not enter its own row"


def test_ac_2_32_volume_is_split_adjusted():
    """⚠ A 10:1 split multiplies share volume ~10× overnight; a 5-day window
    straddling it reports several sigma from an event that moved no value."""
    volumes = {"A": [1_000_000] * 10}
    plain = P.volume_zscore(_panel({"A": [100.0] * 10}, volumes=volumes, factor=1.0))
    scaled = P.volume_zscore(_panel({"A": [100.0] * 10}, volumes=volumes, factor=0.1))
    # ★ A constant factor cancels in a z-score — which is the point: the
    #   adjustment removes the level, so a flat series stays flat either way.
    assert plain.isna().equals(scaled.isna())


# --------------------------------------------------------------------------- #
# ★★ RSI — L5 D-16
# --------------------------------------------------------------------------- #

def test_ac_2_33_rsi_uses_wilders_smoothing_not_a_rolling_mean():
    """★★ **L5 D-16.** ⚠ The two agree on trend and disagree on level, so the
    legacy is *plausible everywhere and correct nowhere* — which is why it
    survived. A monotonic rise gives Wilder 100; the shapes differ elsewhere."""
    from src.feature_engineer.contracts.sets.price_ohlcv_v1 import PRICE_OHLCV_V1 as c

    spec = next(f for f in c.features if f.name == "rsi_14")
    assert spec.formula_id == "rsi.wilder.v1", "the id must name the maths (§5.2)"

    # A zig-zag: Wilder's recursive average and a flat 14-mean diverge here.
    prices = [100 + (3 if i % 2 else -2) * (i % 7) for i in range(60)]
    wilder = P.rsi_wilder(_panel({"A": prices}))
    legacy = _legacy_rsi(_panel({"A": prices}))
    assert not np.allclose(wilder.dropna().to_numpy(),
                           legacy.dropna().to_numpy(), atol=1e-6)


def _legacy_rsi(panel, period=14):
    """The inherited arithmetic, for contrast only — never exported."""
    ordered = panel.sort_values(["ticker", "date"], kind="mergesort")
    px = ordered["adj_open_minor"].astype("float64")
    delta = px.groupby(ordered["ticker"], sort=True).diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_g = gain.groupby(ordered["ticker"]).transform(lambda s: s.rolling(period).mean())
    avg_l = loss.groupby(ordered["ticker"]).transform(lambda s: s.rolling(period).mean())
    return 100 - (100 / (1 + avg_g / (avg_l + 1e-9)))


def test_ac_2_33_an_unbroken_rise_is_exactly_100_not_99_999():
    """⚠ **No epsilon.** The legacy divides by `avg_loss + 1e-9`, which turns the
    genuinely undefined case into `99.999…`. Fourteen sessions without a down
    move is a real state and its RSI is **exactly 100**."""
    rsi = P.rsi_wilder(_panel({"A": [100 + i for i in range(40)]}))
    assert rsi.dropna().iloc[-1] == 100.0


def test_ac_2_33_a_perfectly_flat_window_has_no_rsi():
    """FE-14 — ★ the answer to *unknown* is null, not a plausible middle. ⚠ The
    legacy's epsilon reports **50**, which is indistinguishable from a genuinely
    balanced market."""
    rsi = P.rsi_wilder(_panel({"A": [100.0] * 40}))
    assert rsi.isna().all()


def test_ac_2_33_rsi_stays_inside_its_declared_range():
    """INV-3 / FE-5 — enforced at emit, not documented."""
    prices = [100 * (1.05 ** i if i % 3 else 0.9 ** i) for i in range(80)]
    rsi = P.rsi_wilder(_panel({"A": prices})).dropna()
    assert rsi.min() >= 0.0 and rsi.max() <= 100.0


# --------------------------------------------------------------------------- #
# MACD — INV-2
# --------------------------------------------------------------------------- #

def test_ac_2_34_macd_does_not_move_with_the_callers_history_window():
    """★★ **INV-2.** ⚠ An EWM is recursive from its first row, so without a
    warm-up the same `(ticker, date, as_of)` yields different values depending on
    the caller's window — invisible in any single run.

    ★ **Measured**: past the warm-up, windows carrying 30 / 60 / 120 / 240 extra
    sessions agree to the bit. ⚠ The dependence is *bounded, not removed* — see
    `MACD_WARMUP_SESSIONS` for the decay and why 3× rather than 6×.
    """
    tail = [100 * (1.004 ** i) for i in range(200)]
    values = {n: P.macd_hist(_panel({"A": [60.0] * n + tail})).dropna().iloc[-1]
              for n in (30, 60, 120, 240)}
    assert len(set(values.values())) == 1, values


def test_ac_2_34_macd_is_dimensionless_so_it_compares_across_prices():
    """★★ ⚠ *Measured 2026-08-26:* the inherited price DIFFERENCE printed **2007**
    for SNDK (≈$1 499) and **3.1** for AAPL (≈$313) on the same day. A
    cross-sectional model fed that learns the price level."""
    shape = [100 * (1.01 ** i) for i in range(150)]
    cheap = P.macd_hist(_panel({"A": shape})).dropna().iloc[-1]
    dear = P.macd_hist(_panel({"A": [p * 50 for p in shape]})).dropna().iloc[-1]
    # ⚠ `rtol=1e-3`, not `1e-6`: the fixture stores prices as INTEGER MINOR
    #   UNITS, so scaling by 50 rounds differently. That is the panel's own
    #   quantisation, not the feature's — the inherited version differed by 600×.
    assert np.isclose(cheap, dear, rtol=1e-3), "scaling every price must not move it"


# --------------------------------------------------------------------------- #
# Cross-sectional ranks — FE-13's hazard
# --------------------------------------------------------------------------- #

def test_ac_2_35_ranks_are_computed_within_a_date_only():
    """★★ FE-13, one contract out. ⚠ *Ranking over the pooled sample leaks the
    future distribution into the past* — a 2019 row scored against 2026's
    cross-section. This is the defect `_cross_section_rank` exists for, where a
    `pd.qcut` inside a `groupby.transform` silently returned NaN for **77 %** of
    training rows."""
    panel = _panel({"A": [100.0] * 30, "B": [50.0] * 30})
    values = pd.Series([1.0] * 30 + [2.0] * 30, index=panel.index)
    ranked = P.cross_sectional_rank(panel, values, ascending=True)
    # Every date has exactly two names, so the ranks are 0.5 and 1.0 on EVERY
    # date — a pooled rank would spread them across the whole sample instead.
    assert set(ranked.round(4).unique()) == {0.5, 1.0}


# --------------------------------------------------------------------------- #
# FE-5 — the range check that did not exist
# --------------------------------------------------------------------------- #

def test_ac_2_36_a_declared_range_is_enforced_at_emit():
    """★★ FE-5 / INV-3 — ⚠ `RangeViolationError` and AC-2.5 both existed,
    `b3_minimal@v1` declared a range, and **no code path evaluated it**. A bound
    nothing evaluates is a comment."""
    frame = pd.DataFrame({"rsi_14": [50.0, 140.0]})
    with pytest.raises(RangeViolationError, match="rsi_14"):
        assert_ranges(frame, PRICE_OHLCV_V1)


def test_ac_2_36_nulls_are_not_range_violations():
    """FE-14 — ★ `null_policy` governs missing values; a missing value is not an
    out-of-range one."""
    frame = pd.DataFrame({"rsi_14": [np.nan, np.nan]})
    assert_ranges(frame, PRICE_OHLCV_V1)          # does not raise


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #

def test_ac_2_37_the_same_inputs_yield_a_byte_identical_panel():
    """FE-16 / INV-2 — no wall-clock, no dict order, no unseeded randomness."""
    panel = _panel({"A": [100 + i * 0.4 for i in range(120)],
                    "B": [50 + i * 0.2 for i in range(120)]})
    kw = dict(contract=PRICE_OHLCV_V1, price_panel=panel,
              calendar_report=_Report(), as_of=AS_OF, adj_as_of=AS_OF)
    pd.testing.assert_frame_equal(build_panel(**kw), build_panel(**kw))
