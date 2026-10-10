"""DE-81 / AC-7.99 — a refresh record is merged, never blindly overwritten (`DX-167`). ✏ 2026-10-09.

⚠ `train --limit 20 --refresh-events` used to leave `split` recorded as covering 20 names; the next
full run then read 490 names unfetched ⇒ UNCHECKED.
"""

from __future__ import annotations

from datetime import date

from src.data_engine.calendar.store import EventStore

FULL = [f"T{i:03d}" for i in range(510)]


def _store(tmp_path):
    store = EventStore(tmp_path / "events")
    store.record_refresh("split", date(2016, 10, 9), date(2026, 10, 8), covers_tickers=FULL)
    return store


def test_ac_7_99_a_narrower_refresh_never_narrows_the_record(tmp_path):
    store = _store(tmp_path)
    before = store.freshness()["split"]
    store.record_refresh("split", date(2025, 7, 15), date(2026, 10, 9), covers_tickers=FULL[:20])
    assert store.freshness()["split"] == before


def test_ac_7_99_a_wider_refresh_replaces_the_record(tmp_path):
    store = _store(tmp_path)
    store.record_refresh("split", date(2016, 10, 1), date(2026, 10, 9),
                         covers_tickers=FULL + ["NEW"])
    rec = store.freshness()["split"]
    assert rec["covers_to"] == "2026-10-09" and "NEW" in rec["covers_tickers"]
    assert len(rec["covers_tickers"]) == 511


def test_ac_7_99_new_names_merge_over_the_common_window_at_the_older_time(tmp_path):
    store = _store(tmp_path)
    old = store.freshness()["split"]["refreshed_at"]
    store.record_refresh("split", date(2020, 1, 1), date(2026, 10, 9), covers_tickers=["NEW"])
    rec = store.freshness()["split"]
    assert len(rec["covers_tickers"]) == 511
    assert rec["covers_from"] == "2020-01-01" and rec["covers_to"] == "2026-10-08"
    assert rec["refreshed_at"] == old


def test_ac_7_99_an_unverifiable_legacy_record_is_replaced(tmp_path):
    store = EventStore(tmp_path / "events")
    store.record_refresh("split", date(2016, 1, 1), date(2026, 1, 1), covers_tickers=None)
    store.record_refresh("split", date(2016, 1, 1), date(2026, 10, 8), covers_tickers=FULL[:20])
    assert len(store.freshness()["split"]["covers_tickers"]) == 20
