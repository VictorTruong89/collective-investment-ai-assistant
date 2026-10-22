"""DE-81 / AC-7.99 — every refresh record is kept; a check accepts ANY that covers it (`DX-167`).

✏ 2026-10-09, corrected 2026-10-10. ⚠ The first fix merged records and kept the OLDER one when the
names were equal, so a same-day `ingest events --years 1` sweep was discarded and the daily card
(200-day window, max age 1 day) would have read UNCHECKED. Behavioural: asserted through the
calendar feed itself, with the clock pinned.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from src.data_engine.calendar.classes import CHECKED
from src.data_engine.calendar.store import CachedEventFeed, EventStore

FULL = [f"T{i:03d}" for i in range(510)]
TODAY = date(2026, 10, 12)


def _at(monkeypatch, when):
    monkeypatch.setattr("src.data_engine.calendar.store.utcnow",
                        lambda: datetime(*when, tzinfo=timezone.utc))


def _status(store, *, start, max_age, tickers=FULL):
    feed = CachedEventFeed(store, max_age_days=max_age)
    return str(feed.fetch("split", tickers, start, TODAY, TODAY).status)


def test_ac_7_99_a_short_fresh_sweep_serves_the_daily_card_and_keeps_the_long_one(
        tmp_path, monkeypatch):
    store = EventStore(tmp_path / "events")
    _at(monkeypatch, (2026, 10, 8, 4))                                   # the 10-year sweep
    store.record_refresh("split", date(2016, 10, 9), date(2026, 10, 8), covers_tickers=FULL)
    _at(monkeypatch, (2026, 10, 12, 8))                                  # Monday, --years 1
    store.record_refresh("split", date(2025, 10, 12), TODAY, covers_tickers=FULL)
    _at(monkeypatch, (2026, 10, 12, 15))
    assert _status(store, start=date(2026, 3, 26), max_age=1) == CHECKED   # daily, 200 days
    rec = store.freshness()["split"]
    assert rec["covers_from"] == "2025-10-12" and rec["history"][0]["covers_from"] == "2016-10-09"


def test_ac_7_99_the_long_record_still_serves_training_inside_its_window(tmp_path, monkeypatch):
    store = EventStore(tmp_path / "events")
    _at(monkeypatch, (2026, 10, 8, 4))
    store.record_refresh("split", date(2016, 10, 9), TODAY, covers_tickers=FULL)
    _at(monkeypatch, (2026, 10, 12, 8))
    store.record_refresh("split", date(2025, 10, 12), TODAY, covers_tickers=FULL[:20])  # smoke
    _at(monkeypatch, (2026, 10, 12, 15))
    assert _status(store, start=date(2016, 10, 12), max_age=365 * 20) == CHECKED


def test_ac_7_99_no_record_covering_everything_is_still_unchecked(tmp_path, monkeypatch):
    store = EventStore(tmp_path / "events")
    _at(monkeypatch, (2026, 10, 12, 8))
    store.record_refresh("split", date(2025, 10, 12), TODAY, covers_tickers=FULL[:20])
    assert _status(store, start=date(2025, 11, 1), max_age=1) != CHECKED


def test_ac_7_99_history_is_bounded_and_newest_is_on_top(tmp_path, monkeypatch):
    store = EventStore(tmp_path / "events")
    for day in range(1, 26):
        _at(monkeypatch, (2026, 9, day, 8))
        store.record_refresh("split", date(2025, 1, 1), date(2026, 9, day), covers_tickers=FULL)
    rec = store.freshness()["split"]
    assert rec["covers_to"] == "2026-09-25" and len(rec["history"]) == 20
    assert all("history" not in h for h in rec["history"])


@pytest.mark.parametrize("legacy", [True])
def test_ac_7_99_a_legacy_record_without_history_reads_as_before(tmp_path, monkeypatch, legacy):
    import json

    store = EventStore(tmp_path / "events")
    store.freshness_path.parent.mkdir(parents=True, exist_ok=True)
    store.freshness_path.write_text(json.dumps({"split": {
        "refreshed_at": "2026-10-12T08:00:00+00:00", "covers_from": "2016-10-09",
        "covers_to": "2026-10-12", "covers_tickers": FULL}}))
    _at(monkeypatch, (2026, 10, 12, 15))
    assert _status(store, start=date(2016, 10, 12), max_age=1) == CHECKED
