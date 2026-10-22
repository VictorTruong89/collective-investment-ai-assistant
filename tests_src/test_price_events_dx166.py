"""DX-166 — splits and dividends reach every price panel. DE-78 / AC-7.96 · MT-61 / AC-4.43 · OR-57 / AC-8.45.

✏ Written 2026-10-08 (Victor: *"fix DX-166 first"*).

⚠ Measured: training and the daily run both called `build_price_panel(raw, (), adj_as_of)` on FMP's RAW
series. NVDA's 10:1 split (2024-06-10) produced 21 training labels below −50 % (min −89.5 %); a reverse
split reads as a surge. The event store already held every split and dividend — nothing passed them on.

Hermetic: a tmp event store and synthetic raw bars, run through the real builders.
"""

from __future__ import annotations

import inspect
from datetime import date

import pandas as pd
import pytest

from src.data_engine.calendar.store import EventStore
from src.data_engine.contracts.envelopes import BLOCK, FLAG, Finding

ADJ = date(2026, 10, 8)
SPLIT_DAY = pd.Timestamp("2024-06-10")


def _raw(ticker, before, after, *, change=SPLIT_DAY, days=80):
    """Flat raw bars that jump from `before` to `after` (minor units) on `change`."""
    rows = []
    for d in pd.bdate_range("2024-04-01", periods=days):
        px = before if d < change else after
        rows.append({"ticker": ticker, "date": d, "open_minor": px, "high_minor": px,
                     "low_minor": px, "close_minor": px, "volume": 1_000,
                     "currency": "USD", "source": "fmp"})
    return pd.DataFrame(rows)


def _store(tmp_path):
    store = EventStore(tmp_path / "events")
    store.upsert([
        Finding("NVX", "split", BLOCK, SPLIT_DAY.date(), date(2024, 5, 22),
                {"numerator": 10, "denominator": 1}, "fmp:splits"),
        Finding("DDX", "reverse_split", BLOCK, SPLIT_DAY.date(), date(2024, 5, 22),
                {"numerator": 1, "denominator": 3}, "fmp:splits"),
        Finding("NVX", "dividend", FLAG, date(2024, 5, 15), date(2024, 4, 20),
                {"cash_minor": 10, "currency": "USD"}, "fmp:dividends"),
        Finding("NVX", "split", BLOCK, date(2026, 12, 1), date(2026, 11, 1),
                {"numerator": 2, "denominator": 1}, "fmp:splits"),          # after adj_as_of
        Finding("OTH", "split", BLOCK, SPLIT_DAY.date(), date(2024, 5, 22),
                {"numerator": 2, "denominator": 1}, "fmp:splits"),          # not asked for
        Finding("NVX", "earnings_reported", FLAG, date(2024, 5, 22), date(2024, 5, 22),
                {}, "fmp:earnings"),                                         # not a price event
    ])
    return store


# ── AC-7.96 · DE-78 ──────────────────────────────────────────────────────────

def test_ac_7_96_the_store_becomes_the_adjustments_events(tmp_path):
    from src.data_engine.calendar.gate import price_events

    events = price_events(_store(tmp_path), tickers=("NVX", "DDX"), adj_as_of=ADJ)
    got = sorted((e.ticker, e.event_type, e.event_date) for e in events)
    assert got == [("DDX", "split", SPLIT_DAY.date()),
                   ("NVX", "dividend", date(2024, 5, 15)),
                   ("NVX", "split", SPLIT_DAY.date())]
    ddx = next(e for e in events if e.ticker == "DDX")
    assert ddx.detail["numerator"] == 1 and ddx.detail["denominator"] == 3


@pytest.mark.parametrize("ticker, before, after", [("NVX", 100_000, 10_000),   # 10:1 split
                                                   ("DDX", 1_000, 3_000)])     # 1:3 reverse
def test_ac_7_96_a_split_is_not_a_return(tmp_path, ticker, before, after):
    from src.data_engine import build_price_panel
    from src.data_engine.calendar.gate import price_events
    from src.models.train.run import build_training_labels

    raw = _raw(ticker, before, after)
    bare = build_training_labels(build_price_panel(raw, (), ADJ), horizon_days=21, as_of=ADJ)[0]
    assert bare["value"].abs().max() > 0.5, "the DX-166 shape: unadjusted, the split is a move"

    events = price_events(_store(tmp_path), tickers=(ticker,), adj_as_of=ADJ)
    panel = build_price_panel(raw, events, ADJ)
    labels = build_training_labels(panel, horizon_days=21, as_of=ADJ)[0]
    assert labels["value"].abs().max() < 0.05, "adjusted, a flat price is a flat return"


def test_ac_7_96_an_empty_store_gives_no_events(tmp_path):
    from src.data_engine.calendar.gate import price_events

    assert price_events(EventStore(tmp_path / "none"), tickers=("NVX",), adj_as_of=ADJ) == []


# ── AC-4.43 · MT-61 and AC-8.45 · OR-57 — both builders read them ────────────

def test_ac_4_43_training_builds_panel_and_labels_with_the_stored_events():
    from src.models.train import __main__ as train
    from src.models.train import run

    assert "build_price_panel(raw, (), adj_as_of)" not in inspect.getsource(run)
    assert "price_events" in inspect.getsource(run.build_training_panel)
    body = inspect.getsource(train._train)
    assert "price_events(" in body and "events=events" in body


def test_ac_8_45_the_daily_run_never_passes_an_empty_event_list():
    from src.orchestration import entrypoint

    source = inspect.getsource(entrypoint)
    assert "events=()," not in source
    assert "price_events(" in source


def test_ac_4_50_the_printed_count_is_the_events_inside_the_window():
    """AC-4.50 (MT-61 ✏ 2026-10-20) — the line counts splits/dividends that adjust a bar in the
    window, with the total beside. ⚠ It printed "1785 splits", most years before the window."""
    from src.data_engine.pit.models import CorporateEvent
    from src.models.train.__main__ import price_events_line

    def ev(kind, day):
        return CorporateEvent(ticker="X", event_type=kind, event_date=day,
                              knowable_at=day, detail={}, source="test")

    events = [ev("split", date(2010, 6, 1)), ev("split", date(2020, 6, 1)),
              ev("dividend", date(2015, 1, 2)), ev("dividend", date(2016, 10, 20)),
              ev("dividend", date(2026, 10, 1))]
    line = price_events_line(events, start=date(2016, 10, 20), as_of=date(2026, 10, 20))
    assert "1 splits · 1 dividends in the window" in line
    assert "of 2 · 3 supplied" in line
