"""D-07 — the universe price assembler. DE-13, DE-36, DE-49.

★★ **DE-13 is inherited from a real incident.** A LEFT JOIN silently dropped
**7 of the 13 watchlist names** — the majority of the actionable path — and each
kept its row with every fundamental column present and entirely `NaN`. The
columns existed. Nothing noticed.

★ **DE-36: the panel covers the UNIVERSE, not the watchlist** — *a name excluded
from the actionable slate still participates in cross-sectional normalisation.*

Tier: unit + reality-probe (constitution §4, F3 Tier 1).
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import pytest

from src.data_engine.errors import PlanGatedError, UniverseIncompleteError
from src.data_engine.universe.prices import (
    EMPTY_WINDOW, NO_SOURCE, PLAN_GATED, assemble_universe_panel,
    assert_complete, fetch_universe,
)

START, END = date(2026, 1, 2), date(2026, 5, 1)


def frame(ticker: str, rows: int = 90) -> pd.DataFrame:
    days = pd.bdate_range(START, periods=rows)
    return pd.DataFrame({
        "ticker": ticker, "date": [d.date() for d in days],
        "open_minor": [10000 + i * 5 for i in range(rows)],
        "high_minor": [10100 + i * 5 for i in range(rows)],
        "low_minor": [9900 + i * 5 for i in range(rows)],
        "close_minor": [10050 + i * 5 for i in range(rows)],
        "volume": [1_000_000] * rows, "currency": "USD", "source": "fmp"})


def fetcher(rows_by_ticker: dict, raises: dict | None = None):
    raises = raises or {}
    def fetch(ticker):
        if ticker in raises:
            raise raises[ticker]
        count = rows_by_ticker.get(ticker)
        return None if count is None else frame(ticker, count)
    return fetch


# --------------------------------------------------------------------------- #
# DE-13 — the rule the incident wrote
# --------------------------------------------------------------------------- #

def test_de13_a_ticker_that_does_not_resolve_fails_the_run():
    """★★ DE-13 — ⚠ *it is not dropped, and it does not become a row of NaNs.*"""
    _, report = fetch_universe(
        None, ["AAPL", "GHOST", "MU"], start=START, end=END,
        fetch=fetcher({"AAPL": 90, "MU": 90}))
    assert not report.complete
    assert [f.ticker for f in report.failures] == ["GHOST"]
    assert report.failures[0].reason == EMPTY_WINDOW
    with pytest.raises(UniverseIncompleteError, match="does not become a row of NaNs"):
        assert_complete(report)


def test_every_failure_is_collected_and_reported_once():
    """★ *A 130-name universe with three problems should take one run to
    diagnose, not three.* ⚠ Raising on the first bad ticker tells you about one
    name per run."""
    _, report = fetch_universe(
        None, ["AAPL", "GHOST", "MU", "NOPE", "NVDA"], start=START, end=END,
        fetch=fetcher({"AAPL": 90, "MU": 90, "NVDA": 90}))
    assert sorted(f.ticker for f in report.failures) == ["GHOST", "NOPE"]
    with pytest.raises(UniverseIncompleteError) as caught:
        assert_complete(report)
    assert "GHOST" in str(caught.value) and "NOPE" in str(caught.value)


def test_de49_a_402_is_classified_as_a_subscription_boundary():
    """★★ DE-49 — ⚠ *an absent security is a universe error to correct; a
    plan-gated one is a **declaration** problem.*

    Measured 2026-08-26: **every `.TO`/`.NE` symbol returns 402 on this plan**,
    so Canadian listings and CDRs cannot be in a universe until it changes
    (D-11 RC-58). ★ Discovering that at fetch time is discovering it too late.
    """
    gated = PlanGatedError("historical-price-eod/non-split-adjusted",
                           {"symbol": "BBD.B"}, 3)
    _, report = fetch_universe(
        None, ["AAPL", "BBD.B"], start=START, end=END,
        fetch=fetcher({"AAPL": 90}, raises={"BBD.B": gated}))
    (failure,) = report.failures
    assert failure.reason == PLAN_GATED != NO_SOURCE
    with pytest.raises(UniverseIncompleteError, match="DECLARATION problem"):
        assert_complete(report)


def test_a_complete_universe_assembles_into_one_panel():
    """DE-36 — ★ one panel, every name, and the cross-section is the universe."""
    tickers = ["AAPL", "MU", "NVDA", "AMD"]
    panel, report = assemble_universe_panel(
        None, tickers, start=START, end=END, events=(), adj_as_of=END,
        fetch=fetcher({t: 90 for t in tickers}))
    assert report.complete
    assert sorted(panel["ticker"].unique()) == sorted(tickers)
    assert len(panel) == 4 * 90
    for column in ("adj_open_minor", "adj_factor", "adj_as_of", "is_adjusted"):
        assert column in panel.columns, column


def test_a_name_lost_during_assembly_raises():
    """★ The LEFT-JOIN incident in a new shape — the panel must carry every name
    the fetch claimed."""
    tickers = ["AAPL", "MU"]
    def losing_fetch(ticker):
        # ⚠ MU comes back empty of rows but non-None: it would concat to nothing.
        return frame(ticker, 90) if ticker == "AAPL" else frame(ticker, 90).iloc[0:0]
    with pytest.raises(UniverseIncompleteError):
        assemble_universe_panel(None, tickers, start=START, end=END, events=(),
                                adj_as_of=END, fetch=losing_fetch)


def test_short_history_is_named_rather_than_dropped():
    """★ ⚠ **Not a failure and not ignorable**: a name with 40 rows in a panel
    whose median is 900 carries NaNs in every trailing window, and `coverage()`
    is what decides whether it may be the actionable pick (MT-11)."""
    _, report = fetch_universe(
        None, ["AAPL", "MU", "IPO"], start=START, end=END,
        fetch=fetcher({"AAPL": 200, "MU": 200, "IPO": 12}))
    assert report.complete, "a short history is not a fetch failure"
    assert report.short_history == ("IPO",)
    assert report.to_json_obj()["short_history"] == ["IPO"]


# --------------------------------------------------------------------------- #
# ★ The reality probe — CT-3.2's record
# --------------------------------------------------------------------------- #

@pytest.mark.live
def test_the_real_watchlist_assembles_into_one_panel():
    """★★ **CT-3.2 reality probe.**

    | Field | Value |
    |---|---|
    | **entry point** | `assemble_universe_panel` over the 13-name watchlist |
    | **ground truth** | FMP live, 200 calendar days to 2026-08-25 |
    | **intermediate** | 13/13 fetched, equal row counts, no short history |
    | **verdict** | one CT-7.1 panel, ~1,794 rows |

    ⚠ **CNQ and ENB are Canadian companies on US listings** and resolve on the
    bare ticker — it is the `.TO`/`.NE` *venues* that are plan-gated (DE-49).
    """
    import os

    from src.data_engine.src.fmp import prices as fmp_prices
    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret

    key = os.environ.get("FMP_API_KEY")
    if not key:
        pytest.skip("FMP_API_KEY not set")

    client = FMPClient(Secret("FMP_API_KEY", key))
    end = date(2026, 8, 25)
    start = end - timedelta(days=200)
    watchlist = ["MSFT", "GOOGL", "NVDA", "MU", "SNDK", "ARM", "INTC", "AMD",
                 "MRVL", "CNQ", "ENB", "POWL", "PLTR"]

    panel, report = assemble_universe_panel(
        None, watchlist, start=start, end=end, events=(), adj_as_of=end,
        fetch=lambda t: fmp_prices.raw_prices(client, t, start, end))

    assert report.complete and len(report.fetched) == 13
    assert panel["ticker"].nunique() == 13
    assert report.short_history == ()
    assert len(set(report.rows_by_ticker.values())) == 1, \
        "a common window should give every name the same session count"
