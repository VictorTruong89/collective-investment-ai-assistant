"""D-07's pre-run calendar gate — AC-7.47…7.53 (§6A).

Tier: integration + contract (constitution §4). The gate is a PRECONDITION, so
the behaviour under test is mostly "what does it refuse".
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from src.data_engine.calendar.check import (
    ClassResult, calendar_check, news_status, price_adjustment_status, require_check,
)
from src.data_engine.calendar.classes import CHECKED, EVENT_CLASSES, unchecked
from src.data_engine.calendar.store import CachedEventFeed, EventStore
from src.data_engine.contracts.envelopes import (
    BLOCK, FLAG, Finding, PROCEED, PROCEED_WITH_FLAGS,
)
from src.data_engine.errors import (
    CheckMissingError, ContractViolationError, UnhandledBlockError,
)
from tests_src.data_engine_fixtures import ScriptedFeed

WINDOW = (date(2024, 1, 1), date(2026, 8, 16))
AS_OF = date(2026, 8, 16)
CLEAN = ClassResult(CHECKED)

NVDA_SPLIT = Finding("NVDA", "split", BLOCK, date(2024, 6, 10), date(2024, 5, 22),
                     {"numerator": 10, "denominator": 1}, "fmp:splits")
MSFT_DIV = Finding("MSFT", "dividend", FLAG, date(2024, 5, 16), date(2024, 3, 5),
                   {"dividend": 0.75}, "fmp:dividends")


def run(results=None, tickers=("NVDA", "MSFT"), handled=None, as_of=AS_OF):
    return calendar_check(
        tickers=tickers, start=WINDOW[0], end=WINDOW[1], as_of=as_of,
        adj_as_of=as_of, feed=ScriptedFeed(results or {}, CLEAN),
        run_id="run-1", handled=handled,
    )


def test_ac_7_47_feature_building_without_a_calendar_check_raises():
    """AC-7.47 — DE-31. Not per-ticker, not lazily, not on the actionable subset."""
    with pytest.raises(CheckMissingError, match="before the first feature is built"):
        require_check(None, window=WINDOW, what="D-02 panel build")

    narrow = run()
    ok = require_check(narrow, window=WINDOW, what="D-02 panel build")
    assert ok is narrow

    with pytest.raises(CheckMissingError, match="narrower window clears nothing"):
        require_check(narrow, window=(date(2020, 1, 1), WINDOW[1]), what="backtest")


def test_ac_7_48_the_check_covers_the_universe_not_the_watchlist():
    """AC-7.48 — DE-36.

    A name excluded from the actionable slate still participates in
    cross-sectional normalisation, so its unhandled split contaminates every
    other name's rank.
    """
    seen = {}

    class Recorder:
        def fetch(self, event_class, tickers, start, end, as_of):
            seen[event_class] = tuple(tickers)
            return CLEAN

    report = calendar_check(
        tickers=["nvda", "msft", "arm"], start=WINDOW[0], end=WINDOW[1], as_of=AS_OF,
        adj_as_of=AS_OF, feed=Recorder(), run_id="run-1",
    )
    assert report.universe_size == 3
    assert seen["split"] == ("ARM", "MSFT", "NVDA"), "uppercased and complete (DE-7)"


def test_ac_7_49_an_unhandled_block_halts_and_names_tickers_and_events():
    """AC-7.49 — DE-32. A blocking ticker is never silently dropped."""
    with pytest.raises(UnhandledBlockError) as exc:
        run({"split": ClassResult(CHECKED, (NVDA_SPLIT,))})
    assert exc.value.blocked_tickers == ("NVDA",)
    assert "2024-06-10" in str(exc.value) and "split" in str(exc.value)


def test_ac_7_49_a_block_is_cleared_only_by_a_recorded_handling():
    """AC-7.49 / CT-7.7 — `handled` / `handling`, never a severity downgrade."""
    report = run(
        {"split": ClassResult(CHECKED, (NVDA_SPLIT,))},
        handled={("NVDA", "split", date(2024, 6, 10)):
                 "panel re-derived at the run's adj_as_of (QD-15)"},
    )
    assert report.verdict == PROCEED, "a handled BLOCK stops blocking, and nothing else flags"
    assert report.findings[0].handled is True
    assert "re-derived" in report.findings[0].handling


def test_ac_7_50_all_eighteen_classes_appear_in_class_status():
    """AC-7.50 — DE-35, CT-7.7. A class missing from the map is a DEFECT.

    ```
    Every other rule here fails safe by HALTING. DE-35 fails safe by
    ADMITTING IGNORANCE — and it is the one an implementation is tempted to
    skip, because an empty list is easier to return than a tri-state.
    ```
    """
    report = run()
    # ★ 18 since 2026-08-28 — §6B's `ticker_change` (DE-62).
    assert len(EVENT_CLASSES) == 18
    assert set(report.class_status) == {c.name for c in EVENT_CLASSES}
    assert report.class_status["index_membership"].startswith("UNCHECKED: ")
    for value in report.class_status.values():
        assert value == CHECKED or value.startswith("UNCHECKED: ")


def test_ac_7_50_a_missing_class_fails_the_contract():
    """AC-7.50 — the check FIRES when a class is dropped (L4 IM-3's standard)."""
    from src.data_engine.calendar.check import _assert_every_class_present
    partial = {c.name: CHECKED for c in EVENT_CLASSES if c.name != "delisting"}
    with pytest.raises(ContractViolationError, match="delisting"):
        _assert_every_class_present(partial)


def test_ac_7_50_a_reasonless_unchecked_is_rejected():
    """DE-35 — 'could not look' and 'found nothing' must stay distinguishable."""
    from src.data_engine.calendar.check import _assert_every_class_present
    bad = {c.name: CHECKED for c in EVENT_CLASSES}
    bad["news"] = "UNCHECKED"
    with pytest.raises(ContractViolationError, match="reasonless UNCHECKED"):
        _assert_every_class_present(bad)
    with pytest.raises(ValueError, match="requires a reason"):
        unchecked("")


def test_ac_7_51_news_beyond_92_days_reports_unchecked_never_no_events():
    """AC-7.51 — DE-35, K-8. `news/stock` returns ~92 days regardless of paging."""
    assert news_status(AS_OF - timedelta(days=30), AS_OF) == CHECKED
    deep = news_status(date(2024, 1, 1), AS_OF)
    assert deep.startswith("UNCHECKED: ") and "92d" in deep

    report = run({"news": ClassResult(news_status(WINDOW[0], AS_OF))})
    assert report.class_status["news"].startswith("UNCHECKED: ")


def test_ac_7_52_findings_are_keyed_on_knowability_not_on_the_event_date():
    """AC-7.52 — DE-34. The check is itself point-in-time.

    A split announced after `as_of` is absent from the report **even though it is
    in today's `splits` response**.
    """
    future_announcement = Finding("NVDA", "split", BLOCK, date(2024, 6, 10),
                                  knowable_at=date(2026, 1, 1), detail={}, source="fmp")
    report = run({"split": ClassResult(CHECKED, (future_announcement,))},
                 as_of=date(2025, 1, 1))
    assert report.findings == () and report.verdict == PROCEED


def test_ac_7_53_the_report_is_persisted_and_referenced_by_every_artifact(tmp_path):
    """AC-7.53 — DE-33, AP-6. A past recommendation's context must be reconstructable."""
    from src.data_engine.store.atomic import read_json, write_json

    report = run({"dividend": ClassResult(CHECKED, (MSFT_DIV,))})
    path = tmp_path / "calendar_check.json"
    write_json(report.to_json_obj(), path)
    loaded = read_json(path)

    assert loaded["verdict"] == PROCEED_WITH_FLAGS
    assert loaded["report_id"] == report.report_id
    assert loaded["window"] == {"start": "2024-01-01", "end": "2026-08-16"}
    assert loaded["findings"][0]["knowable_at"] == "2024-03-05", "declaration, not ex-date"
    assert set(loaded["class_status"]) == {c.name for c in EVENT_CLASSES}


def test_price_adjustment_state_blocks_on_a_mismatched_adj_as_of():
    """§6A.2 class 1 — DE-28/DE-30 enforced across the seam, not inside a module."""
    same = price_adjustment_status(date(2026, 8, 16), date(2026, 8, 16), ["NVDA"])
    assert same.findings == ()
    differ = price_adjustment_status(date(2026, 8, 1), date(2026, 8, 16), ["NVDA"])
    assert differ.findings[0].severity == BLOCK


def test_the_cached_feed_reports_staleness_rather_than_serving_it(tmp_path):
    """QD-16 — a cache must not be able to turn UNCHECKED into a clean answer."""
    store = EventStore(tmp_path)
    feed = CachedEventFeed(store, max_age_days=1)

    never = feed.fetch("split", ["NVDA"], *WINDOW, AS_OF)
    assert never.status.startswith("UNCHECKED: ") and "never refreshed" in never.status

    store.upsert([NVDA_SPLIT])
    # ⚠ **Coverage in NAMES, from 2026-08-27.** A refresh that records only a
    #   date window claims nothing about which tickers were fetched, and a
    #   12-name sweep was reading CHECKED for a 510-name universe.
    store.record_refresh("split", WINDOW[0], WINDOW[1], covers_tickers=["NVDA"])
    fresh = feed.fetch("split", ["NVDA"], *WINDOW, AS_OF)
    assert fresh.status == CHECKED and len(fresh.findings) == 1

    narrow = feed.fetch("split", ["NVDA"], date(2020, 1, 1), WINDOW[1], AS_OF)
    assert narrow.status.startswith("UNCHECKED: ") and "store covers" in narrow.status

    # ★ A name outside the swept set is UNCHECKED and is NAMED.
    wider = feed.fetch("split", ["NVDA", "AMD"], *WINDOW, AS_OF)
    assert wider.status.startswith("UNCHECKED: ") and "AMD" in wider.status


def test_the_event_store_round_trips_a_finding(tmp_path):
    """The store is a D-07 artifact (QD-16), so its shape is validated on write."""
    store = EventStore(tmp_path)
    assert store.upsert([NVDA_SPLIT, MSFT_DIV]) == 2
    assert store.upsert([NVDA_SPLIT]) == 0, "upsert on the key, not blind append"
    df = store.read()
    assert sorted(df["ticker"]) == ["MSFT", "NVDA"]
    assert df[df["ticker"] == "NVDA"].iloc[0]["knowable_at"].date() == date(2024, 5, 22)


# --------------------------------------------------------------------------- #
# DE-48 — the trading-day predicate (OR-7's migration). AC-7.65
# --------------------------------------------------------------------------- #

def test_de48_a_holiday_on_a_weekday_is_not_a_trading_day():
    """DE-48 — ★ the legacy `_is_market_open_et` was **weekday-only**: it
    returns `True` on Christmas whenever Christmas falls on a Tuesday."""
    from datetime import date

    from src.data_engine.calendar.trading_day import is_trading_day

    christmas = date(2025, 12, 25)          # a Thursday
    assert christmas.weekday() < 5          # the legacy rule would say True
    assert is_trading_day(christmas) is False
    assert is_trading_day(date(2026, 8, 25)) is True        # an ordinary Tuesday
    assert is_trading_day(date(2026, 8, 29)) is False       # a Saturday


def test_ac_7_65_outside_the_declared_coverage_the_answer_is_unknown():
    """AC-7.65 / DE-48, DE-35 — ⚠ *no holidays found* and *we did not look* are
    **opposite findings**, and a silent wrong `True` runs the pipeline against a
    market that never opened."""
    from datetime import date

    from src.data_engine.calendar.trading_day import is_trading_day

    assert is_trading_day(date(2031, 6, 10)) is None
    assert is_trading_day(date(2019, 6, 10)) is None


def test_d08_blocks_on_an_unknowable_trading_day_rather_than_assuming():
    """DE-48 with OR-6 — ★ *a precondition that cannot be evaluated blocks the
    run and reports why. It never defaults to "probably fine."*"""
    from datetime import date

    import pytest

    from src.data_engine.calendar.trading_day import is_trading_day
    from src.orchestration.errors import PreconditionUnevaluableError
    from src.orchestration.schedule.preconditions import assert_trading_day

    with pytest.raises(PreconditionUnevaluableError, match="no answer"):
        assert_trading_day(date(2031, 6, 10), calendar=is_trading_day)


# --------------------------------------------------------------------------- #
# DE-67 — identity beats a vendor delisting. AC-7.84
# --------------------------------------------------------------------------- #

EQR_DELISTING = Finding("EQR", "delisting", BLOCK, date(2026, 8, 18), date(2026, 8, 18),
                        {"company": "Equity Residential", "exchange": "NYSE"},
                        "fmp:delisted-companies")
EQR_RENAME = Finding("EQR", "ticker_change", BLOCK, date(2026, 8, 28), date(2026, 8, 28),
                     {"cik": "0000906107", "from": "EQR", "to": "VMRK",
                      "candidates": ["VMRK"], "ambiguous": False},
                     "derived:sec:company_tickers.json")
AVB_DELISTING = Finding("AVB", "delisting", BLOCK, date(2026, 8, 17), date(2026, 8, 17),
                        {"company": "AvalonBay Communities, Inc.", "exchange": "NYSE"},
                        "fmp:delisted-companies")


def test_ac_7_84_a_rename_supersedes_a_vendor_delisting(tmp_path):
    """AC-7.84 / DE-67, RC-54 — ⚠ *measured 2026-08-28:* FMP called `EQR` a
    delisting while SEC showed its CIK listing `VMRK`, which **priced 41 bars**.
    ★ The registrant index is the authority on identity; the feed only sees a
    symbol go dark and cannot tell a rebrand from an exit."""
    from src.data_engine.calendar.gate import delisted_names

    store = EventStore(tmp_path)
    store.upsert([EQR_DELISTING, EQR_RENAME, AVB_DELISTING])

    barred = delisted_names(store, as_of=date(2026, 8, 28), tickers=["EQR", "AVB"])

    assert "EQR" not in barred, "a renamed name must not be barred as delisted"
    # ⚠ The converse does NOT hold — AVB has no ticker_change and still stands.
    assert "AVB" in barred


def test_ac_7_84_the_superseded_delisting_is_not_deleted(tmp_path):
    """AC-7.84 / DE-66, QD-15 — ★ the ledger is append-only, so the delisting is
    *superseded*, not erased, and ⚠ the `ticker_change` **BLOCK still stands**:
    the name is un-barred, never declared fine. Suppressing the bar AND the
    BLOCK would be the severity downgrade QD-15 forbids."""
    from src.data_engine.calendar.gate import delisted_names

    store = EventStore(tmp_path)
    store.upsert([EQR_DELISTING, EQR_RENAME])
    delisted_names(store, as_of=date(2026, 8, 28), tickers=["EQR"])

    rows = store.read()
    classes = set(rows[rows["ticker"] == "EQR"]["event_class"])
    assert classes == {"delisting", "ticker_change"}, "the ledger loses nothing"


def test_ac_7_84_a_rename_not_yet_knowable_does_not_supersede(tmp_path):
    """AC-7.84 with DE-34 — ⚠ knowability cuts **both** ways. A rename the run
    could not have known cannot retroactively un-bar a name; acting on it would
    be look-ahead used to *relax* a guard, which is the worse direction."""
    from src.data_engine.calendar.gate import delisted_names

    store = EventStore(tmp_path)
    store.upsert([EQR_DELISTING, EQR_RENAME])

    barred = delisted_names(store, as_of=date(2026, 8, 20), tickers=["EQR"])
    assert "EQR" in barred, "the rename is not knowable until 2026-08-28"
