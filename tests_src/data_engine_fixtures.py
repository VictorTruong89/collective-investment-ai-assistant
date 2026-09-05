"""Shared builders for the D-07 suite. Hermetic by construction — no network.

★ The one place a fake is legitimate is the TRANSPORT. Everything above it is
the real code path: the real client, the real adjustment, the real contracts.
DE-37 forbids a fixture only for the LIVE PROBE (§6A.4), which is a separate
file and is skipped loudly rather than faked.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pandas as pd

from src.data_engine.pit.models import CorporateEvent, Fact


class FakeTransport:
    """A scripted transport. `script` maps an endpoint to a list of responses.

    Each call pops the next response for that endpoint, so a test can script
    "402 then 200" — which is the only way to exercise §5A.2's cause 3 without
    a 595-call burst against the live API.
    """

    def __init__(self, script: dict) -> None:
        self.script = {k: list(v) for k, v in script.items()}
        self.calls: list[tuple[str, dict]] = []

    def get(self, url: str, params: dict, headers: dict, timeout: float):
        endpoint = url.split("/stable/", 1)[-1]
        self.calls.append((endpoint, {k: v for k, v in params.items() if k != "apikey"}))
        queue = self.script.get(endpoint)
        if not queue:
            return 404, "[]"
        status, payload = queue.pop(0)
        return status, payload if isinstance(payload, str) else json.dumps(payload)


def fact(ticker="MSFT", tag="Revenues", *, accession="0000-1", start=date(2024, 1, 1),
         end=date(2024, 3, 31), period_type="quarterly", value=1_000_00,
         filed=date(2024, 4, 25), currency="USD", ingested=None) -> Fact:
    return Fact(
        ticker=ticker, accession_id=accession, tag=tag, period_start=start,
        period_end=end, period_type=period_type, value_minor=value,
        value_currency=currency, unit=currency, filing_date=filed,
        ingested_at=ingested or datetime(2024, 4, 26, tzinfo=timezone.utc),
    )


def split(ticker="NVDA", on=date(2024, 6, 10), numerator=10, denominator=1,
          knowable=None) -> CorporateEvent:
    return CorporateEvent(ticker, "split", on, knowable or on,
                          {"numerator": numerator, "denominator": denominator},
                          "fmp:splits")


def dividend(ticker="MSFT", ex=date(2024, 5, 16), cash_minor=75, declared=None
             ) -> CorporateEvent:
    return CorporateEvent(ticker, "dividend", ex, declared or date(2024, 3, 5),
                          {"cash_minor": cash_minor, "currency": "USD"}, "fmp:dividends")


def raw_series(ticker="NVDA", rows=None) -> pd.DataFrame:
    """A raw OHLCV frame in the shape `build_price_panel` consumes."""
    rows = rows or [
        (date(2024, 6, 6), 118000, 121000, 117500, 120000, 40_000_000),
        (date(2024, 6, 7), 119000, 121500, 118500, 120890, 41_238_600),
        (date(2024, 6, 10), 12000, 12300, 11900, 12179, 314_162_650),
        (date(2024, 6, 11), 12200, 12500, 12100, 12400, 300_000_000),
    ]
    return pd.DataFrame([{
        "ticker": ticker, "date": d, "open_minor": o, "high_minor": h, "low_minor": lo,
        "close_minor": c, "volume": v, "currency": "USD", "source": "fmp",
    } for d, o, h, lo, c, v in rows])


class FakePriceSource:
    def __init__(self, raw: pd.DataFrame, events=()) -> None:
        self._raw, self._events = raw, list(events)

    def raw_prices(self, ticker, start, end):
        df = self._raw
        return df[(df["date"] >= start) & (df["date"] <= end)].reset_index(drop=True)

    def splits(self, ticker):
        return [e for e in self._events if e.event_type == "split"]

    def dividends(self, ticker):
        return [e for e in self._events if e.event_type == "dividend"]


class ScriptedFeed:
    """An `EventFeed` returning canned per-class results — for gate tests only."""

    def __init__(self, results: dict, default) -> None:
        self._results, self._default = results, default

    def fetch(self, event_class, tickers, start, end, as_of):
        return self._results.get(event_class, self._default)
