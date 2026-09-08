"""`price_ohlcv@v1` — the 14 price features §5.3 declares.

★ **This is the spec's own list, made real.** §5.3 records *"the contract
today — 61 features"* as inherited from `feature_schema.py`; what D-02 actually
published was `b3_minimal@v1`'s two. This closes the price third of that gap.

⚠ **Not a verbatim port.** `technical/price.py` documents four corrections to the
legacy — look-ahead on the close, look-ahead on volume, epsilons where nulls
belong, and **L5 D-16's RSI**. The names and the intent are inherited; the
arithmetic is not.

★ **Declared in Python for the reason `b3_minimal_v1` gives**: FE-2 enforces
immutability on the content hash, and a Python literal is diffed by git and typed
by the dataclass. At fourteen features that argument is weaker than at two — a
YAML set is the right home once the fundamental 45 land — but changing the
declaration format and the feature count in one step would make a contract
regression indistinguishable from a parser one.
"""

from __future__ import annotations

from src.feature_engineer.contracts.spec import FeatureContract, FeatureSpec
from src.feature_engineer.technical.price import (
    MACD_FORMULA_ID,
    MACD_WARMUP_SESSIONS,
    RANK_FORMULA_ID,
    RETURN_FORMULA_ID,
    RSI_FORMULA_ID,
    SMA_FORMULA_ID,
    VOL_FORMULA_ID,
    VOLUME_Z_FORMULA_ID,
)

_OWNER = "technical.price"

#: ⚠ **No range on a return, a ratio or a histogram** — CN-10: *an admitted
#: absence beats a fabricated threshold*. A 21-session return is unbounded above;
#: declaring `[−1, 5]` would fire on a real 6× move and look like a data error.
_UNBOUNDED = None


def _ret(name: str, lookback: int) -> FeatureSpec:
    return FeatureSpec(
        name=name, formula_id=RETURN_FORMULA_ID, dtype="float64",
        inputs=("price.adj_open",), owner_module=_OWNER,
        pit_class="C", null_policy="allow", range=_UNBOUNDED,
        note=(f"adj_open(t)/adj_open(t-{lookback}) - 1. ★ Both ends on the same "
              f"field (QA-71) and both knowable at the day-t open (FE-28)."))


def _sma(name: str, window: int) -> FeatureSpec:
    return FeatureSpec(
        name=name, formula_id=SMA_FORMULA_ID, dtype="float64",
        inputs=("price.adj_open",), owner_module=_OWNER,
        pit_class="C", null_policy="allow",
        # ★ A price over its own mean is positive by construction; 20× would be
        #   a units error, not a market. ⚠ The upper bound is an ADMITTED GUESS
        #   and the lower is arithmetic (CN-10).
        range=(0.0, 20.0),
        note=f"adj_open(t) / mean(adj_open, {window} sessions ending t)")


def _vol(name: str, window: int) -> FeatureSpec:
    return FeatureSpec(
        name=name, formula_id=VOL_FORMULA_ID, dtype="float64",
        inputs=("price.adj_open",), owner_module=_OWNER,
        pit_class="C", null_policy="allow", range=(0.0, 5.0),
        note=(f"sd of {window} open-to-open log returns, ddof=1, "
              f"min_periods={window} (PD-9)"))


PRICE_OHLCV_V1 = FeatureContract(
    name="price_ohlcv",
    version=1,
    created="2026-08-27",
    note=("§5.3's 14 price features, rebuilt on the FE-28 open anchor. ⚠ The "
          "legacy read adj_close(T) and volume(T), neither of which is knowable "
          "at the day-T open; L5 D-16's RSI is fixed to Wilder's here."),
    features=(
        _ret("ret_1d", 1), _ret("ret_5d", 5), _ret("ret_10d", 10),
        _ret("ret_20d", 20),
        _sma("sma_5_ratio", 5), _sma("sma_20_ratio", 20), _sma("sma_50_ratio", 50),
        _vol("vol_10d", 10), _vol("vol_20d", 20),
        FeatureSpec(
            name="rsi_14", formula_id=RSI_FORMULA_ID, dtype="float64",
            inputs=("price.adj_open",), owner_module=_OWNER,
            pit_class="C", null_policy="allow",
            # ★ INV-3 — enforced at emit (FE-5), not documented. RSI is bounded
            #   by its own algebra, so this bound is arithmetic, not a guess.
            range=(0.0, 100.0),
            note=("★★ **Wilder's** smoothing (alpha = 1/14, adjust=False) — "
                  "L5 **D-16** records that the legacy used a rolling arithmetic "
                  "mean and called it RSI. ⚠ No epsilon: a window with no losses "
                  "is exactly 100, and a perfectly flat one is null (FE-14).")),
        FeatureSpec(
            name="macd_hist", formula_id=MACD_FORMULA_ID, dtype="float64",
            inputs=("price.adj_open",), owner_module=_OWNER,
            pit_class="C", null_policy="allow", range=_UNBOUNDED,
            note=(f"(EMA(12)-EMA(26) less its EMA(9) signal) ÷ EMA(26). ★ The "
                  f"division is a DEPARTURE from the legacy, which emitted a "
                  f"price DIFFERENCE: SNDK printed 2007 and AAPL 3.1 on the same "
                  f"day, so a cross-sectional model would learn the price level. "
                  f"⚠ Null for the first "
                  f"{MACD_WARMUP_SESSIONS} sessions: an EWM is recursive from its "
                  f"first row, so without a warm-up the same (ticker, date, as_of) "
                  f"changes with the caller's window — INV-2.")),
        FeatureSpec(
            name="vol_zscore_5d", formula_id=VOLUME_Z_FORMULA_ID, dtype="float64",
            # ⚠ Two inputs, and `adj_factor` is the second on purpose: a raw
            #   share count spans a split and the z-score reports the split.
            inputs=("price.volume", "price.adj_factor"), owner_module=_OWNER,
            pit_class="C", null_policy="allow", range=_UNBOUNDED,
            note=("z-score of split-adjusted volume over 5 sessions ending at "
                  "**T-1**. ★ A day's volume is not knowable at that day's open, "
                  "so unlike a close-based feature the legacy error here is total "
                  "(FE-28).")),
        FeatureSpec(
            name="rank_ret_5d", formula_id=RANK_FORMULA_ID, dtype="float64",
            inputs=("feature.ret_5d",), owner_module=_OWNER,
            pit_class="C", null_policy="allow",
            range=(0.0, 1.0),
            note=("percentile rank of ret_5d **within the date**, descending "
                  "(1.0 = strongest). ⚠ Pooled ranking leaks the future "
                  "distribution into the past — FE-13's hazard.")),
        FeatureSpec(
            name="rank_vol_20d", formula_id=RANK_FORMULA_ID, dtype="float64",
            inputs=("feature.vol_20d",), owner_module=_OWNER,
            pit_class="C", null_policy="allow",
            range=(0.0, 1.0),
            note="percentile rank of vol_20d within the date, ascending "
                 "(1.0 = most volatile)"),
    ),
)
