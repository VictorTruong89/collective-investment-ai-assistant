"""DE-80 / AC-7.98 — one retry pass over failed price fetches (`DX-168`). ✏ 2026-10-09.

⚠ The first shadow snapshot lost 9 names (AAPL among them) to empty FMP responses at the start of
the burst; minutes later all were complete. Hermetic: scripted fetchers, no sleeping.
"""

from __future__ import annotations

from datetime import date

import pandas as pd


class _Flaky:
    """Fails the first `fails[t]` calls for ticker t, then serves one row."""

    def __init__(self, fails):
        self.fails = dict(fails)
        self.calls = []

    def __call__(self, ticker):
        self.calls.append(ticker)
        if self.fails.get(ticker, 0) > 0:
            self.fails[ticker] -= 1
            return pd.DataFrame()                    # an empty response
        return pd.DataFrame([{"ticker": ticker, "date": pd.Timestamp("2026-10-08")}])


def test_ac_7_98_fetch_universe_retries_once_and_names_what_still_fails():
    from src.data_engine.universe.prices import fetch_universe

    flaky, pauses = _Flaky({"AAPL": 1, "DEAD": 5}), []
    frames, report = fetch_universe(None, ["AAPL", "MSFT", "DEAD"], start=date(2026, 1, 1),
                                    end=date(2026, 10, 8), fetch=flaky,
                                    retry_pause=7, sleep=pauses.append)
    assert set(frames) == {"AAPL", "MSFT"}
    assert [f.ticker for f in report.failures] == ["DEAD"]
    assert pauses == [7], "one pause, one retry pass"
    assert flaky.calls.count("AAPL") == 2 and flaky.calls.count("MSFT") == 1


def test_ac_7_98_no_failures_no_pause():
    from src.data_engine.universe.prices import fetch_universe

    pauses = []
    fetch_universe(None, ["MSFT"], start=date(2026, 1, 1), end=date(2026, 10, 8),
                   fetch=_Flaky({}), sleep=pauses.append)
    assert pauses == []


def test_ac_7_98_training_fetch_prices_retries_once(monkeypatch):
    from src.data_engine.src.fmp import prices as fmp_prices
    from src.models.train.run import fetch_prices

    flaky = _Flaky({"AAPL": 1, "DEAD": 5})

    def raw(client, ticker, start, end):
        rows = flaky(ticker)
        if rows.empty:
            raise ValueError(f"{ticker}: no raw price rows")
        return rows

    monkeypatch.setattr(fmp_prices, "raw_prices", raw)
    pauses = []
    frames, unresolved = fetch_prices(None, ["AAPL", "MSFT", "DEAD"], start=date(2026, 1, 1),
                                      end=date(2026, 10, 8), retry_pause=3,
                                      sleep=pauses.append)
    assert set(frames) == {"AAPL", "MSFT"} and set(unresolved) == {"DEAD"}
    assert "no raw price rows" in unresolved["DEAD"] and pauses == [3]
