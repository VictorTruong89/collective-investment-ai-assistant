"""D-04 — MT-54 / AC-4.36: a calendar HALT stops the training run. ✏ Written 2026-10-07 (`DX-158`).

⚠ *Found on Victor's smoke run 2026-10-07:* `_calendar_report` caught **every** exception as
*"calendar check unavailable"* and substituted the `TRAIN-CALENDAR-UNCHECKED` stand-in, so five
unhandled `restatement_amended` BLOCKs (ADM ×3, AES ×2) became `PROCEED_WITH_FLAGS` and the run
went on to build a panel. A never-swept store never needed the stand-in: D-07's check already
returns a real report with every class `UNCHECKED`.

Hermetic: a tmp event store, a fake price fetch, no network.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.data_engine.calendar.store import EventStore
from src.data_engine.contracts.envelopes import BLOCK, Finding
from src.data_engine.errors import UnhandledBlockError

AS_OF = date(2026, 10, 7)
START = date(2016, 10, 7)
#: ⚠ A delisting, not the restatement Victor's run met: since DE-76 (2026-10-07) training
#: handles `restatement_amended` (its fundamentals are replayed per filing date). A
#: delisting has no handling and must still HALT.
AVB_GONE = Finding("AVB", "delisting", BLOCK, date(2026, 8, 17), date(2026, 8, 17),
                   {"reason": "test"}, "fmp:delisted")


def _bars(ticker):
    """A real-shaped raw price frame (as `fetch_prices` returns) — one bar."""
    return pd.DataFrame([{"ticker": ticker, "date": pd.Timestamp("2026-10-06"),
                          "open_minor": 100, "high_minor": 100, "low_minor": 100,
                          "close_minor": 100, "volume": 1, "currency": "USD", "source": "fmp"}])


def _swept_store(root):
    store = EventStore(root / "events")
    store.upsert([AVB_GONE])
    store.record_refresh("delisting", START, AS_OF, covers_tickers=["ADM", "AVB"])
    return store


def test_ac_4_36_an_unhandled_block_is_raised_never_replaced(monkeypatch, tmp_path):
    from src.models.train import __main__ as train

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path))
    _swept_store(tmp_path)
    with pytest.raises(UnhandledBlockError, match="AVB"):
        train._calendar_report(("ADM", "AVB"), START, AS_OF, refresh_events=False,
                               client=None, run_id="train")


def test_ac_4_36_a_never_swept_store_gets_the_real_all_unchecked_report(monkeypatch, tmp_path):
    from src.models.train import __main__ as train

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path))
    report = train._calendar_report(("ADM",), START, AS_OF, refresh_events=False,
                                    client=None, run_id="train")
    assert report.report_id != "TRAIN-CALENDAR-UNCHECKED"
    assert not any(str(v) == "CHECKED" for v in report.class_status.values())
    assert not hasattr(train, "_UncheckedReport"), "MT-54 — no stand-in report exists"


def test_ac_4_36_the_run_stops_naming_the_events_before_any_panel(monkeypatch, tmp_path, capsys):
    from src.models.train import __main__ as train

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path))
    _swept_store(tmp_path)
    monkeypatch.setattr(train, "load_sp500", lambda: ("ADM", "AVB"))
    monkeypatch.setattr(train, "_wire", lambda: (None, None, object(), None, {}))
    monkeypatch.setattr(train, "fetch_prices",
                        lambda client, universe, **k: ({t: _bars(t) for t in universe}, []))

    def _no_panel(**_):
        raise AssertionError("a panel was built past a HALT")

    monkeypatch.setattr(train, "build_training_panel", _no_panel)

    code = train.main(["--as-of", AS_OF.isoformat(), "--skip-facts", "--prepare-only"])
    err = capsys.readouterr().err
    assert code == train.EXIT_FAILED
    assert "HALT" in err and "AVB" in err and "delisting" in err
    assert "calendar check unavailable" not in err


# ── DX-163 — MT-56 / AC-4.38 and MT-57 / AC-4.39 ─────────────────────────────

def test_ac_4_38_late_evening_new_york_is_still_that_day():
    from datetime import datetime, timezone

    from src.models.train.__main__ import market_date

    # 23:27 EDT on 7 Oct is 03:27 UTC on 8 Oct.
    late = datetime(2026, 10, 8, 3, 27, tzinfo=timezone.utc)
    assert market_date(late) == date(2026, 10, 7)
    assert market_date(datetime(2026, 10, 8, 14, 0, tzinfo=timezone.utc)) == date(2026, 10, 8)


def _run_unswept(monkeypatch, tmp_path, *extra):
    from src.models.train import __main__ as train

    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path))      # an empty event store
    monkeypatch.setattr(train, "load_sp500", lambda: ("ADM", "AVB"))
    monkeypatch.setattr(train, "_wire", lambda: (None, None, object(), None, {}))
    monkeypatch.setattr(train, "fetch_prices",
                        lambda client, universe, **k: ({t: _bars(t) for t in universe}, []))
    built = []

    def _panel(**_):
        built.append(True)
        raise RuntimeError("panel reached")

    monkeypatch.setattr(train, "build_training_panel", _panel)
    monkeypatch.setattr(train, "_engine_for", lambda *a: None)
    try:
        code = train.main(["--as-of", AS_OF.isoformat(), "--skip-facts", "--prepare-only",
                           *extra])
    except RuntimeError:
        code = None
    return code, built


def test_ac_4_39_no_class_checked_refuses_before_any_panel(monkeypatch, tmp_path, capsys):
    from src.models.train import __main__ as train

    code, built = _run_unswept(monkeypatch, tmp_path)
    err = capsys.readouterr().err
    assert code == train.EXIT_FAILED and not built
    assert "0/" in err and "--allow-unchecked-calendar" in err


def test_ac_4_39_the_override_proceeds_and_says_so(monkeypatch, tmp_path, capsys):
    code, built = _run_unswept(monkeypatch, tmp_path, "--allow-unchecked-calendar")
    assert built, "the explicit override reaches the panel"
    assert "UNCHECKED CALENDAR" in capsys.readouterr().err
