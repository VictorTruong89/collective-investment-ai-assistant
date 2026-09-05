"""Panel assembly — the D-07 -> D-02 seam (FE-7, FE-8, FE-10, FE-23).

★ **FE-23: D-02 reaches D-07 only through its public API.** No file reading, no
path construction, no cache peeking. That is why this module takes a
`price_panel` and a `calendar_report` rather than a data directory: the caller
(the composition root) wires D-07, and D-02 receives what it needs (CA-2).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.feature_engineer.contracts.panel import ENVELOPE, validate_panel
from src.feature_engineer.contracts.spec import FeatureContract
from src.feature_engineer.errors import AsOfRequiredError, CalendarHaltError
from src.feature_engineer.technical import price as _price
from src.feature_engineer.technical.momentum import mom_21, vol_21

#: name -> callable(price_panel) -> Series. **One feature, one owning module**
#: (FE-4): this table is the only place a feature name is bound to code, so two
#: implementations of one concept cannot both be registered.
def _of_prices(fn):
    """Adapt a price-only builder to the two-argument protocol."""
    return lambda price_panel, built: fn(price_panel)


def _derived(column: str, *, ascending: bool):
    """★ A builder that reads an EARLIER FEATURE rather than a price column.

    ⚠ `rank_ret_5d` needs `ret_5d`, so the contract's declaration order is load
    bearing. It is checked rather than assumed: an ordering mistake would
    otherwise surface as a column of nulls, which is indistinguishable from a
    genuinely unrankable day (FE-14's own hazard, turned against us).
    """
    def build(price_panel, built):
        from src.feature_engineer.technical.price import cross_sectional_rank

        if column not in built.columns:
            raise KeyError(
                f"a rank feature needs {column!r}, which the contract has not "
                f"declared before it. FE-1's ordering is part of the contract: "
                f"built so far {sorted(c for c in built.columns)}")
        return cross_sectional_rank(price_panel, built[column], ascending=ascending)
    return build


BUILDERS = {
    "mom_21": _of_prices(mom_21), "vol_21": _of_prices(vol_21),
    # ── price_ohlcv@v1 — §5.3's fourteen ───────────────────────────────────
    "ret_1d": _of_prices(lambda p: _price.ret(p, lookback=1)),
    "ret_5d": _of_prices(lambda p: _price.ret(p, lookback=5)),
    "ret_10d": _of_prices(lambda p: _price.ret(p, lookback=10)),
    "ret_20d": _of_prices(lambda p: _price.ret(p, lookback=20)),
    "sma_5_ratio": _of_prices(lambda p: _price.sma_ratio(p, window=5)),
    "sma_20_ratio": _of_prices(lambda p: _price.sma_ratio(p, window=20)),
    "sma_50_ratio": _of_prices(lambda p: _price.sma_ratio(p, window=50)),
    "vol_10d": _of_prices(lambda p: _price.vol(p, window=10)),
    "vol_20d": _of_prices(lambda p: _price.vol(p, window=20)),
    "rsi_14": _of_prices(lambda p: _price.rsi_wilder(p, period=14)),
    "macd_hist": _of_prices(_price.macd_hist),
    "vol_zscore_5d": _of_prices(lambda p: _price.volume_zscore(p, window=5)),
    "rank_ret_5d": _derived("ret_5d", ascending=False),
    "rank_vol_20d": _derived("vol_20d", ascending=True),
}

_UNSET = object()

#: D-07 CT-7.7 verdicts D-02 may proceed on (FE-10).
PROCEEDING_VERDICTS = ("PROCEED", "PROCEED_WITH_FLAGS")


def build_panel(
    *, contract: FeatureContract, price_panel: pd.DataFrame, calendar_report,
    as_of=_UNSET, adj_as_of=_UNSET, fundamentals=None,
) -> pd.DataFrame:
    """CT-2.2 for `contract` over `price_panel`.

    Both PIT axes are required and neither has a default (**FE-7**, **FE-8**).
    They fail differently and that is why both are named: a defaulted `as_of` is
    INV-1 look-ahead; a defaulted `adj_as_of` is INV-2 irreproducibility, where
    the same backtest re-run next year sees different prices.
    """
    if as_of is _UNSET or as_of is None:
        raise AsOfRequiredError("build_panel", "as_of")
    if adj_as_of is _UNSET:
        raise AsOfRequiredError("build_panel", "adj_as_of")
    if not isinstance(as_of, date):
        raise AsOfRequiredError("build_panel", "as_of (a date)")

    _require_cleared_window(calendar_report)

    # PD-14 — never mutate the caller's frame.
    out = pd.DataFrame({
        "ticker": price_panel["ticker"].to_numpy(),
        "date": price_panel["date"].to_numpy(),
    })
    # ★ `f_*` features need D-07 fundamentals, which a price panel does not
    #   carry. They are built as a block because half of them compare filings to
    #   each other — see `fundamental/build.py` for why the order matters.
    fundamental_names = [n for n in contract.feature_names if n.startswith("f_")]
    if fundamental_names:
        out = _attach_fundamentals(out, price_panel, fundamental_names, fundamentals)

    for name in contract.feature_names:
        if name in fundamental_names:
            continue
        builder = BUILDERS.get(name)
        if builder is None:
            raise KeyError(
                f"contract declares {name!r} and no module builds it. FE-1 runs both "
                f"ways: a spec with no implementation is as broken as a column with "
                f"no spec"
            )
        out[name] = builder(price_panel, out).to_numpy()

    assert_ranges(out, contract)                # FE-5 / INV-3 — at emit

    out["contract_name"] = contract.name
    out["contract_version"] = int(contract.version)
    out["as_of"] = pd.Timestamp(as_of)
    out["adj_as_of"] = pd.Timestamp(adj_as_of) if adj_as_of is not None else pd.NaT
    out["calendar_check_id"] = calendar_report.report_id

    out = out[[*ENVELOPE[:2], *contract.feature_names, *ENVELOPE[2:]]]
    return validate_panel(out.reset_index(drop=True), contract)


def _require_cleared_window(report) -> None:
    """FE-10 / AC-2.12 — a HALT propagates and no panel is built.

    ⚠ D-02 never computes "around" a blocking corporate action. A model trained
    across such a window is not wrong at any single point — it is trained on a
    series whose units changed partway through, and nothing in the data says so.
    """
    if report is None:
        raise CalendarHaltError(["<no calendar check supplied>"])
    if report.verdict not in PROCEEDING_VERDICTS:
        raise CalendarHaltError([f.ticker for f in report.blocked] or ["<unnamed>"])


def _attach_fundamentals(out, price_panel, names, fundamentals):
    """Build the `f_*` block. ⚠ **Refuses rather than emitting a null block.**

    ★ A contract that declares 45 fundamental features and is handed no
    fundamentals would otherwise produce 45 columns of null, which validates,
    trains, and is indistinguishable from a filer that reports nothing (FE-14's
    hazard turned against the caller).
    """
    from src.feature_engineer.errors import MissingFeatureError
    from src.feature_engineer.fundamental.build import build as build_fundamentals

    if not fundamentals or not fundamentals.get("rows_by_ticker"):
        # ⚠ `MissingFeatureError` formats the NAMES, so it is handed the list —
        #   a string would be sorted character by character.
        raise MissingFeatureError(names)

    # ⚠ The FULL price panel, not just the keys: `f_market_to_book` and
    #   `f_graham_number_ratio` are priced on `adj_open(t)`, and handing over two
    #   columns would make them silently all-null — the exact shape FE-1's
    #   null-block refusal above exists to catch, arriving one level down.
    block = build_fundamentals(
        price_panel,
        rows_by_ticker=fundamentals["rows_by_ticker"],
        sectors=fundamentals.get("sectors"),
        market_caps=fundamentals.get("market_caps"))
    for name in names:
        out[name] = block[name].to_numpy()
    return out


def assert_ranges(panel, contract) -> None:
    """FE-5 / INV-3 — ★ **a declared range is ENFORCED at emit, not documented.**

    ⚠ *Added 2026-08-27 with `price_ohlcv@v1`:* `RangeViolationError` and AC-2.5
    both existed, `b3_minimal@v1` declared a range on `vol_21`, and **no code
    path evaluated it**. The rule, the error class and the acceptance criterion
    were all in place; the check was not. ★ The failure it catches — a units
    error, a currency mix — is wrong by orders of magnitude, which is exactly
    what a bound catches and a human scanning a panel does not.

    ★ Nulls are skipped: `null_policy` governs those, and a missing value is not
    an out-of-range one (FE-14).
    """
    import pandas as pd

    from src.feature_engineer.errors import RangeViolationError

    for spec in contract.features:
        if spec.range is None or spec.name not in panel.columns:
            continue
        low, high = spec.range
        values = pd.to_numeric(panel[spec.name], errors="coerce")
        present = values[values.notna()]
        if present.empty:
            continue
        worst_low, worst_high = float(present.min()), float(present.max())
        if worst_low < low or worst_high > high:
            raise RangeViolationError(
                spec.name, low, high,
                f"[{worst_low:.6g}, {worst_high:.6g}]")
