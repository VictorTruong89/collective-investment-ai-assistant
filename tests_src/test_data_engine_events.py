"""D-07 §6A — corporate actions into the EventStore, and the refresh that lied."""
from datetime import date, datetime, timedelta, timezone

import pytest

from src.data_engine.ingest.events import SOURCED, _class_of, refresh


class _Event:
    def __init__(self, ticker, kind, num, den):
        self.ticker, self.event_type = ticker, kind
        self.event_date = self.knowable_at = date(2024, 6, 10)
        self.detail = {"numerator": num, "denominator": den}
        self.source = "fmp:splits"


def test_a_reverse_split_is_classified_by_the_ratio_not_the_label():
    """⚠ A 1-for-10 reverse split arrives on the **same feed** as a 10-for-1
    forward one and the vendor calls both a split. ★ They have opposite effects
    on the price series and D-07's severity table treats them separately."""
    assert _class_of(_Event("A", "split", 10.0, 1.0)) == "split"
    assert _class_of(_Event("A", "split", 1.0, 10.0)) == "reverse_split"
    assert _class_of(_Event("A", "dividend", 0, 0)) == "dividend"


def test_a_partial_sweep_records_no_refresh(tmp_path):
    """★★ ⚠ A sweep that lost 110 of 510 names leaves those **unchecked**, and
    marking the class `CHECKED` would claim otherwise. DE-36's argument: *a name
    excluded from the actionable slate still participates in cross-sectional
    normalisation, so its unhandled split contaminates every other name's
    rank.*"""
    from src.data_engine.calendar.store import EventStore

    class _Failing:
        def get(self, *a, **k):
            raise RuntimeError("no")

    out = refresh(_Failing(), EventStore(tmp_path), tickers=("A", "B"),
                  start=date(2024, 1, 1), end=date(2024, 12, 31))
    assert out["refreshed"] == []
    assert "no class is recorded as refreshed" in out["why"]


def test_the_classes_this_module_cannot_source_stay_unchecked():
    """★ DE-35 — the rest report `UNCHECKED` **with a reason**, and that is what
    makes the ones it does fetch mean something.

    ⚠ `delisting` joined 2026-08-27 — for the **gate**, not for survivorship:
    the feed reaches ~three weeks and pages 1+ are 402, so INV-017's historical
    correction remains impossible (AB-3).
    """
    assert set(SOURCED) == {"split", "reverse_split", "dividend", "delisting"}


def test_a_refresh_is_never_recorded_for_a_class_that_was_not_fetched(tmp_path):
    """★★★ **The defect this module exists for, 2026-08-27.**

    ⚠ `_calendar` recorded `split`, `reverse_split` and `dividend` as refreshed
    **unconditionally**, and the entrypoint passes `events=()` — so in production
    three classes reported **`CHECKED` having fetched nothing**. DE-35 exists to
    stop exactly that, and the conflation sat inside the code implementing it.

    ★ With no events supplied every class now reports its `UNCHECKED` reason.
    """
    import pandas as pd

    from src.orchestration.jobs.b3_run import _calendar

    report = _calendar(universe=("NVDA",), as_of=date(2026, 8, 26),
                       adj_as_of=date(2026, 8, 26), events=(),
                       root=str(tmp_path), run_id="t",
                       window=(pd.Timestamp("2026-02-01"),
                               pd.Timestamp("2026-08-26")))
    for name in SOURCED:
        assert report.class_status[name].startswith("UNCHECKED"), name


# --------------------------------------------------------------------------- #
# ★★ The gate's handling — one implementation, sourced from the STORE
# --------------------------------------------------------------------------- #

def test_the_handling_covers_blocks_the_run_did_not_seed(tmp_path):
    """AC-7.75 (DE-57) — ★★★ ⚠ The handling used to be built from the events **this run seeded**,
    and the entrypoint seeds none — so the moment `ingest/events.py` populates
    the store, every split in it would be unhandled and the daily run would
    **HALT**.

    ★ The handling is a property of **how the panel is derived**, not of where
    the finding came from.
    """
    from src.data_engine.calendar.gate import check_window
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.contracts import BLOCK, Finding

    store = EventStore(tmp_path)
    store.upsert([Finding("NVDA", "split", BLOCK, date(2024, 6, 10),
                          date(2024, 6, 10), {"numerator": 10.0,
                                              "denominator": 1.0}, "fmp")])
    # ⚠ Coverage is recorded, or the class reads UNCHECKED and there is no
    #   finding to handle — see `test_a_refresh_with_no_recorded_coverage_…`.
    store.record_refresh("split", date(2024, 1, 1), date(2024, 12, 31),
                         covers_tickers=("NVDA",))

    report = check_window(store=store, universe=("NVDA",),
                          start=date(2024, 1, 1), end=date(2024, 12, 31),
                          as_of=date(2026, 8, 26), adj_as_of=date(2026, 8, 26),
                          run_id="t", max_age_days=100000)
    assert report.verdict != "HALT"
    split = next(f for f in report.findings if f.event_class == "split")
    assert split.handled is True and "adj_as_of" in split.handling


def test_an_event_not_yet_knowable_is_not_handled(tmp_path):
    """AC-7.75 (DE-57, DE-34) — DE-34 — ⚠ *a split announced after `as_of` is absent even though it sits
    in today's feed*. ★ Handling something the run could not have known about
    would be look-ahead **inside the guard**."""
    from src.data_engine.calendar.gate import _blocks_in_window
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.contracts import BLOCK, Finding

    store = EventStore(tmp_path)
    store.upsert([Finding("NVDA", "split", BLOCK, date(2024, 6, 10),
                          date(2026, 1, 1), {}, "fmp")])   # knowable LATER
    found = _blocks_in_window(store, date(2024, 1, 1), date(2024, 12, 31),
                              date(2024, 12, 31))
    assert found == []


def test_the_training_run_uses_the_same_gate_as_the_daily_one():
    """AC-7.75 (DE-57, FE-4) — FE-4 — ⚠ *two copies of one idea is where the drift starts*, and the
    training run's copy was **a stub asserting PROCEED without checking**
    (AB-9)."""
    import inspect

    from src.models.train.run import training_calendar_check
    from src.orchestration.jobs import b3_run

    assert "check_window" in inspect.getsource(training_calendar_check)
    assert "check_window" in inspect.getsource(b3_run._calendar)


# --------------------------------------------------------------------------- #
# ★★★ Coverage in NAMES — a refresh may not claim beyond what it fetched
# --------------------------------------------------------------------------- #

def _store_with(tmp_path, *, swept):
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.contracts import BLOCK, Finding

    store = EventStore(tmp_path)
    store.upsert([Finding(swept[0], "split", BLOCK, date(2024, 6, 10),
                          date(2024, 6, 10), {}, "fmp")])
    store.record_refresh("split", date(2024, 1, 1), date(2024, 12, 31),
                         covers_tickers=swept)
    return store


def test_a_class_swept_for_a_subset_is_unchecked_for_the_rest(tmp_path):
    """★★★ **Measured 2026-08-27:** a sweep of **12** names marked `split`
    refreshed and a gate over **510** read `CHECKED` — **498 never fetched.**
    That is DE-56's defect one level up: a refresh recorded beyond what it
    covered.

    ⚠ DE-36 is why it matters — *a name excluded from the actionable slate still
    participates in cross-sectional normalisation, so its unhandled split
    contaminates every other name's rank.*
    """
    from src.data_engine.calendar.gate import check_window

    store = _store_with(tmp_path, swept=("NVDA", "AAPL"))
    report = check_window(store=store, universe=("NVDA", "AAPL", "AMD"),
                          start=date(2024, 1, 1), end=date(2024, 12, 31),
                          as_of=date(2026, 8, 26), adj_as_of=date(2026, 8, 26),
                          run_id="t", max_age_days=100000)
    status = report.class_status["split"]
    assert status.startswith("UNCHECKED")
    assert "AMD" in status, "the unfetched name is NAMED, not merely counted"


def test_the_swept_set_itself_is_checked(tmp_path):
    """★ The positive case, so the negative one is not vacuous."""
    from src.data_engine.calendar.gate import check_window

    store = _store_with(tmp_path, swept=("NVDA", "AAPL"))
    report = check_window(store=store, universe=("NVDA", "AAPL"),
                          start=date(2024, 1, 1), end=date(2024, 12, 31),
                          as_of=date(2026, 8, 26), adj_as_of=date(2026, 8, 26),
                          run_id="t", max_age_days=100000)
    assert report.class_status["split"] == "CHECKED"


def test_a_refresh_with_no_recorded_coverage_is_unverifiable(tmp_path):
    """⚠ An index written before `covers_tickers` existed must **not** read as
    covering everything — *unverifiable is not checked*."""
    from src.data_engine.calendar.gate import check_window
    from src.data_engine.calendar.store import EventStore

    store = EventStore(tmp_path)
    store.record_refresh("split", date(2024, 1, 1), date(2024, 12, 31))
    report = check_window(store=store, universe=("NVDA",),
                          start=date(2024, 1, 1), end=date(2024, 12, 31),
                          as_of=date(2026, 8, 26), adj_as_of=date(2026, 8, 26),
                          run_id="t", max_age_days=100000)
    assert "recorded no ticker coverage" in report.class_status["split"]


# --------------------------------------------------------------------------- #
# ★★★ Delistings — and the handling that must NOT cover them
# --------------------------------------------------------------------------- #

def test_a_delisting_is_not_cleared_by_the_price_adjustment(tmp_path):
    """AC-7.77 (DE-59) — ★★★ ⚠ *Found 2026-08-27 the moment `delisting` was ingested.* The handling
    cleared **every** BLOCK-severity finding, and while the store held only
    splits that read as correct — adding delistings marked the real **AVB and
    EQR `handled=True`**.

    ★ *Re-deriving the panel at `adj_as_of` does nothing for a delisted name*: it
    has no forward price, its label is undefined, and it cannot be traded. QD-15
    — *"a BLOCK may only be cleared by an explicit, recorded handling"* — and a
    blanket one is not explicit, it just looks like it.
    """
    from src.data_engine.calendar.gate import ADJUSTMENT_HANDLES, adjustment_handling
    from src.data_engine.contracts import BLOCK, Finding

    assert "delisting" not in ADJUSTMENT_HANDLES
    findings = [
        Finding("NVDA", "split", BLOCK, date(2024, 6, 10), date(2024, 6, 10), {}, "f"),
        Finding("AVB", "delisting", BLOCK, date(2026, 8, 17), date(2026, 8, 17), {}, "f"),
    ]
    handled = adjustment_handling(findings, adj_as_of=date(2026, 8, 26))
    assert ("NVDA", "split", date(2024, 6, 10)) in handled
    assert ("AVB", "delisting", date(2026, 8, 17)) not in handled


def test_an_unhandled_delisting_halts_the_window(tmp_path):
    """AC-7.77 (DE-59) — ★ The consequence, and it is the right one — *a name that stopped trading
    is something a human should look at*."""
    from src.data_engine.calendar.gate import check_window
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.contracts import BLOCK, Finding
    from src.data_engine.errors import UnhandledBlockError

    store = EventStore(tmp_path)
    store.upsert([Finding("AVB", "delisting", BLOCK, date(2026, 8, 17),
                          date(2026, 8, 17), {}, "fmp")])
    store.record_refresh("delisting", date(2026, 8, 6), date(2026, 8, 26),
                         covers_tickers=("AVB",))
    with pytest.raises(UnhandledBlockError, match="AVB"):
        check_window(store=store, universe=("AVB",), start=date(2026, 8, 6),
                     end=date(2026, 8, 26), as_of=date(2026, 8, 26),
                     adj_as_of=date(2026, 8, 26), run_id="t", max_age_days=100000)


def test_the_delisting_feed_cannot_correct_historical_survivorship():
    """AC-7.77 (DE-60) — ★★ **INV-017 stays UNCORRECTED, and this says why in code.**

    ⚠ Measured 2026-08-27: `delisted-companies` returns 100 rows on page 0 and
    **402 on every page after**. Page 0 spans about three weeks. So the source
    can say *who is delisting now*; it cannot say who delisted in 2019 — and
    that is exactly what survivorship correction needs. **AB-3 stands.**
    """
    import inspect

    from src.data_engine.ingest.events import refresh_delistings

    source = inspect.getsource(refresh_delistings)
    assert "402 on every page after it" in source
    assert "INV-017" in source


# --------------------------------------------------------------------------- #
# Class 12 — ma_announcement. ★ The event that PRECEDES the silence (AB-14)
# --------------------------------------------------------------------------- #

class _MnAClient:
    """⚠ Two pages then empty, so the paging path is exercised, not asserted."""

    PAGES = [[{"symbol": "EQR", "companyName": "Equity Residential",
               "cik": "0000906107", "targetedCompanyName": "AvalonBay Communities",
               "targetedCik": "0000915912", "targetedSymbol": "AVB",
               "transactionDate": "2026-08-18", "acceptedDate": "2026-08-18",
               "link": "https://example.invalid/8-k"},
              {"symbol": "NOTOURS", "companyName": "Someone Else",
               "cik": "0000000001", "targetedCompanyName": "Also Not Ours",
               "targetedCik": "0000000002", "targetedSymbol": "NEITHER",
               "transactionDate": "2026-08-01", "acceptedDate": "2026-08-01",
               "link": ""}],
             [{"symbol": "ACQ", "companyName": "Acquirer Inc",
               "cik": "0000000003", "targetedCompanyName": "Old Target",
               "targetedCik": "0000000004", "targetedSymbol": "HOLX",
               "transactionDate": "2026-04-07", "acceptedDate": "2026-12-31",
               "link": ""}]]

    def get(self, endpoint, **params):
        assert endpoint == "mergers-acquisitions-latest"
        page = params.get("page", 0)
        return self.PAGES[page] if page < len(self.PAGES) else []


def test_the_ma_class_records_the_FILING_role_not_the_deal_role(tmp_path):
    """AB-14 / DE-35 — ⚠⚠ **an S-4 pair is filer vs subject, NOT acquirer vs
    target.** *Measured 2026-08-28 over 3 years of the S&P 500:* six names
    matched and **four were not acquisitions of that name** — `CMI` split off
    Atmus, `AIG` divested Corebridge, `BDX` is the Reverse Morris Trust parent,
    `COF` matched its own preferred class. ★ So the finding says `side`, and a
    consumer that wants "was this name acquired" must still investigate."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh_ma_announcements

    store = EventStore(tmp_path)
    out = refresh_ma_announcements(_MnAClient(), store, tickers=("EQR", "AVB"),
                                   as_of=date(2026, 8, 28))

    rows = {(r["ticker"], r["event_class"]): r for r in store.read().to_dict("records")}
    assert ("AVB", "ma_announcement") in rows
    assert ("EQR", "ma_announcement") in rows
    import json
    avb = json.loads(rows[("AVB", "ma_announcement")]["detail"])
    eqr = json.loads(rows[("EQR", "ma_announcement")]["detail"])
    assert avb["side"] == "subject" and avb["counterparty"] == "EQR"
    assert eqr["side"] == "filer" and eqr["counterparty"] == "AVB"
    # ⚠ "subject" is a candidate to investigate, never a conclusion.
    assert avb["investigate"].endswith("ticker-went-silent/")
    assert out["subjects"] == 1


def test_an_ma_announcement_not_yet_accepted_is_not_knowable(tmp_path):
    """DE-34 — ⚠ `acceptedDate` is the knowability date, `transactionDate` the
    event date. ★ Using the transaction date for both would make an
    announcement knowable **before the filing that announced it**."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh_ma_announcements

    store = EventStore(tmp_path)
    refresh_ma_announcements(_MnAClient(), store, tickers=("HOLX",),
                             as_of=date(2026, 8, 28))

    # ⚠ HOLX's transaction is 2026-04-07 but was accepted 2026-12-31.
    assert store.read().empty or "HOLX" not in set(store.read()["ticker"])


def test_the_ma_refresh_records_the_window_it_REACHED(tmp_path):
    """DE-56 / DE-58 — ⚠⚠ **the third place this mistake was available.**
    Recording the window that was *asked for* from a feed that returned less is
    what made a 12-name sweep report a 510-name universe as CHECKED."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh_ma_announcements

    store = EventStore(tmp_path)
    out = refresh_ma_announcements(_MnAClient(), store, tickers=("EQR",),
                                   as_of=date(2026, 8, 28),
                                   since=date(2000, 1, 1))
    # ★ The feed's own dates, not `since` — it never reached 2000.
    assert out["reached"] == "2026-04-07..2026-08-18"


# --------------------------------------------------------------------------- #
# Class 4 — restatement_amended, from EDGAR. AB-14, DE-69
# --------------------------------------------------------------------------- #

class _EdgarSubs:
    """⚠ A realistic `recent` block: the amendment forms sit among ownership
    amendments that share the `/A` suffix and restate nothing."""

    RECENT = {
        "form": ["10-K/A", "SC 13G/A", "4/A", "8-K", "10-Q/A", "13F-HR/A",
                 "8-K", "10-K"],
        "filingDate": ["2026-03-02", "2026-02-10", "2026-02-11", "2026-04-15",
                       "2026-05-06", "2026-05-10", "2026-06-01", "2025-11-01"],
        "acceptanceDateTime": ["2026-03-02T17:01:00.000Z", "2026-02-10T09:00:00.000Z",
                               "2026-02-11T09:00:00.000Z", "2026-04-15T16:30:00.000Z",
                               "2026-05-06T18:02:00.000Z", "2026-05-10T09:00:00.000Z",
                               "2026-12-31T09:00:00.000Z", "2025-11-01T16:00:00.000Z"],
        "items": ["", "", "", "4.02,9.01", "", "", "4.02", ""],
        "reportDate": ["2025-12-31", "", "", "2026-04-15", "2026-03-31", "",
                       "2026-06-01", "2025-09-30"],
        "accessionNumber": ["a-1", "a-2", "a-3", "a-4", "a-5", "a-6", "a-7", "a-8"],
    }

    def __init__(self, recent=None):
        self._recent = recent if recent is not None else self.RECENT

    def submissions(self, cik):
        return {"filings": {"recent": self._recent}}


def test_the_slash_A_suffix_is_not_the_test_for_a_restatement(tmp_path):
    """DE-69 / DE-35 — ⚠⚠ *measured on five mega-caps:* the `/A` suffix matches
    **63 `SC 13G/A`, 7 `4/A`, 5 `13F-HR/A`** — ownership amendments that restate
    nobody's financial statements. ★ A suffix test would file Apple as having
    restated 63 times, so the module uses an explicit whitelist."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.submissions import refresh_restatements

    store = EventStore(tmp_path)
    refresh_restatements(_EdgarSubs(), store, tickers=("ZZ",),
                         cik_map={"ZZ": "0000000001"}, as_of=date(2026, 8, 28))

    import json
    forms = sorted(json.loads(r["detail"])["form"]
                   for r in store.read().to_dict("records"))
    assert forms == ["10-K/A", "10-Q/A", "8-K"], forms
    assert "SC 13G/A" not in forms and "4/A" not in forms


def test_the_non_reliance_8k_is_caught_and_it_arrives_FIRST(tmp_path):
    """DE-69 — ★★ **8-K Item 4.02 is the ANNOUNCEMENT** of a restatement and
    lands weeks before the amended filing. ⚠ A class that waits for the
    amendment learns last, and FMP exposes no item numbers at all."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.submissions import refresh_restatements

    store = EventStore(tmp_path)
    out = refresh_restatements(_EdgarSubs(), store, tickers=("ZZ",),
                               cik_map={"ZZ": "0000000001"},
                               as_of=date(2026, 8, 28))
    assert out["non_reliance"] == 1 and out["amended"] == 2


def test_a_filing_accepted_after_as_of_is_not_knowable(tmp_path):
    """DE-34 — ⚠ the second 8-K item 4.02 was *filed* 2026-06-01 but **accepted
    2026-12-31**. ★ Acceptance is the knowability axis; a restatement is exactly
    the event a run must not act on early."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.submissions import refresh_restatements

    store = EventStore(tmp_path)
    refresh_restatements(_EdgarSubs(), store, tickers=("ZZ",),
                         cik_map={"ZZ": "0000000001"}, as_of=date(2026, 8, 28))
    assert len(store.read()) == 3, "the 2026-12-31 acceptance is excluded"


def test_a_partial_sweep_is_not_recorded_as_refreshed(tmp_path):
    """DE-58 — ⚠⚠ a class marked `CHECKED` over a universe it did not cover is
    the defect §6A exists to stop. ★ A name with no CIK is a failure, not a
    silent skip."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.submissions import refresh_restatements

    store = EventStore(tmp_path)
    out = refresh_restatements(_EdgarSubs(), store, tickers=("ZZ", "NOCIK"),
                               cik_map={"ZZ": "0000000001"},
                               as_of=date(2026, 8, 28))
    assert out["refreshed"] == [] and "NOCIK" in out["failed"]


def test_the_amended_period_travels_with_the_finding(tmp_path):
    """DE-69 — ★ *"BLOCK only if it amends a period inside the window"* (class 4)
    is undecidable without the period. ⚠ An amendment filed today can restate a
    quarter three years back."""
    import json

    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.submissions import refresh_restatements

    store = EventStore(tmp_path)
    refresh_restatements(_EdgarSubs(), store, tickers=("ZZ",),
                         cik_map={"ZZ": "0000000001"}, as_of=date(2026, 8, 28))
    rows = {json.loads(r["detail"])["form"]: json.loads(r["detail"])
            for r in store.read().to_dict("records")}
    assert rows["10-K/A"]["period"] == "2025-12-31"


# --------------------------------------------------------------------------- #
# Class 5 — restatement_silent. DE-24: we diff ourselves. AC-7.39
# --------------------------------------------------------------------------- #

def _obs(tmp_path, rows):
    """An ObservationLedger holding scripted snapshots."""
    from src.data_engine.observation.ledger import ObservationLedger

    ledger = ObservationLedger(tmp_path)
    for ticker, payload, when in rows:
        ledger.snapshot(ticker=ticker, field_set="ratios_ttm", payload=payload,
                        source_endpoint="fmp:ratios-ttm",
                        observed_at=datetime(when.year, when.month, when.day,
                                             12, 0, tzinfo=timezone.utc))
    return ledger


def test_one_snapshot_is_UNCHECKED_and_never_no_restatements(tmp_path):
    """DE-24 / DE-35 — ⚠⚠ *measured 2026-08-28:* all four field sets hold
    **exactly one snapshot per ticker**, so this class can find nothing. ★ That
    is UNCHECKED with a reason, **not** a clean bill: a diff needs two
    observations, and reporting *"no restatements"* from one would be the
    conflation DE-35 exists to stop."""
    from src.data_engine.ingest.silent import silent_changes

    ledger = _obs(tmp_path, [("ZZ", {"currentRatioTTM": 1.5}, date(2026, 8, 1))])
    findings, status = silent_changes(ledger, field_sets=("ratios_ttm",),
                                      tickers=("ZZ",), as_of=date(2026, 8, 28))

    assert findings == [] and status["comparable"] == []
    assert status["no_prior"] == ["ZZ"]
    assert "UNCHECKED" in status["why"] and "NOT" in status["why"]


def test_a_changed_value_between_two_ingests_is_a_finding(tmp_path):
    """DE-24 / AC-7.39 — ★ FMP serves only today's answer, so **keeping a dated
    earlier value and diffing it is the only detection available**."""
    from src.data_engine.ingest.silent import silent_changes

    ledger = _obs(tmp_path, [
        ("ZZ", {"currentRatioTTM": 1.50, "cashRatioTTM": 0.4}, date(2026, 5, 1)),
        ("ZZ", {"currentRatioTTM": 1.72, "cashRatioTTM": 0.4}, date(2026, 8, 1))])
    findings, status = silent_changes(ledger, field_sets=("ratios_ttm",),
                                      tickers=("ZZ",), as_of=date(2026, 8, 28))

    assert len(findings) == 1
    assert findings[0].detail["field"] == "currentRatioTTM"
    assert findings[0].detail["was"] == 1.50 and findings[0].detail["now"] == 1.72
    assert status["comparable"] == ["ZZ"]


def test_the_change_is_flagged_AMBIGUOUS_because_there_is_no_period_key(tmp_path):
    """DE-24 — ⚠⚠ **a structural limit, not a temporal one.** None of the four
    field sets carries a period key, so a changed TTM value may be a silent
    revision **or simply a new quarter entering the trailing window**. ★ The
    finding says so rather than claiming a restatement it cannot distinguish."""
    from src.data_engine.ingest.silent import silent_changes

    ledger = _obs(tmp_path, [
        ("ZZ", {"currentRatioTTM": 1.50}, date(2026, 5, 1)),
        ("ZZ", {"currentRatioTTM": 1.72}, date(2026, 8, 1))])
    findings, _ = silent_changes(ledger, field_sets=("ratios_ttm",),
                                 tickers=("ZZ",), as_of=date(2026, 8, 28))

    assert findings[0].detail["ambiguous"] is True
    assert "no period key" in findings[0].detail["why_ambiguous"]


def test_float_noise_is_not_a_restatement(tmp_path):
    """CN-10 — ⚠ a vendor re-serialising `0.1 + 0.2` restates nothing. ★ The
    tolerance is an admitted choice and is not zero."""
    from src.data_engine.ingest.silent import silent_changes

    ledger = _obs(tmp_path, [
        ("ZZ", {"currentRatioTTM": 0.30000000000000004}, date(2026, 5, 1)),
        ("ZZ", {"currentRatioTTM": 0.3}, date(2026, 8, 1))])
    findings, _ = silent_changes(ledger, field_sets=("ratios_ttm",),
                                 tickers=("ZZ",), as_of=date(2026, 8, 28))
    assert findings == []


def test_a_price_move_is_the_market_not_a_restatement(tmp_path):
    """⚠ `price` and `marketCap` move on their own. ★ Flagging them would bury
    every real revision under daily noise."""
    from src.data_engine.ingest.silent import silent_changes

    ledger = _obs(tmp_path, [
        ("ZZ", {"price": 100.0, "currentRatioTTM": 1.5}, date(2026, 5, 1)),
        ("ZZ", {"price": 131.0, "currentRatioTTM": 1.5}, date(2026, 8, 1))])
    findings, _ = silent_changes(ledger, field_sets=("ratios_ttm",),
                                 tickers=("ZZ",), as_of=date(2026, 8, 28))
    assert findings == []


def test_nothing_comparable_records_NO_refresh(tmp_path):
    """DE-58 — ⚠⚠ recording the universe would claim a coverage the diff never
    had. ★ With no comparable name the class stays UNCHECKED."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.silent import record, silent_changes

    ledger = _obs(tmp_path / "obs", [("ZZ", {"currentRatioTTM": 1.5}, date(2026, 8, 1))])
    findings, status = silent_changes(ledger, field_sets=("ratios_ttm",),
                                      tickers=("ZZ",), as_of=date(2026, 8, 28))
    store = EventStore(tmp_path / "ev")
    assert record(store, findings, status, as_of=date(2026, 8, 28)) == []


def test_the_refresh_covers_only_the_names_actually_compared(tmp_path):
    """DE-58 — ★ a name with no prior is **excluded from coverage**, so a gate
    over the wider universe reports UNCHECKED rather than inheriting a claim."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.silent import record, silent_changes

    ledger = _obs(tmp_path / "obs", [
        ("AA", {"currentRatioTTM": 1.5}, date(2026, 5, 1)),
        ("AA", {"currentRatioTTM": 1.9}, date(2026, 8, 1)),
        ("BB", {"currentRatioTTM": 2.0}, date(2026, 8, 1))])
    findings, status = silent_changes(ledger, field_sets=("ratios_ttm",),
                                      tickers=("AA", "BB"), as_of=date(2026, 8, 28))
    store = EventStore(tmp_path / "ev")
    assert record(store, findings, status, as_of=date(2026, 8, 28)) == ["restatement_silent"]
    assert status["comparable"] == ["AA"] and status["no_prior"] == ["BB"]


# --------------------------------------------------------------------------- #
# Classes 9 & 10 — earnings_reported / earnings_scheduled. AB-14, DE-23
# --------------------------------------------------------------------------- #

class _EarningsClient:
    """One reported quarter and one future date, in one narrow chunk."""

    ROWS = [{"symbol": "ZZ", "date": "2026-07-30", "epsActual": 2.02,
             "epsEstimated": 1.90, "revenueActual": 1000.0,
             "revenueEstimated": 950.0, "lastUpdated": "2026-08-28"},
            {"symbol": "ZZ", "date": "2026-10-29", "epsActual": None,
             "epsEstimated": 1.98, "revenueActual": None,
             "revenueEstimated": 1100.0, "lastUpdated": "2026-08-28"},
            {"symbol": "NOTOURS", "date": "2026-07-30", "epsActual": 1.0,
             "epsEstimated": 1.0, "revenueActual": None,
             "revenueEstimated": None, "lastUpdated": "2026-08-28"}]

    def __init__(self):
        self.calls = []

    def get(self, endpoint, **params):
        assert endpoint == "earnings-calendar"
        self.calls.append((params["from"], params["to"]))
        lo, hi = params["from"], params["to"]
        return [r for r in self.ROWS if lo <= r["date"] <= hi]


class _CappedClient(_EarningsClient):
    """⚠ Always returns a full page — the silent-truncation shape."""

    def get(self, endpoint, **params):
        from src.data_engine.ingest.earnings import ROW_CAP
        self.calls.append((params["from"], params["to"]))
        return [dict(self.ROWS[0]) for _ in range(ROW_CAP)]


def test_reported_and_scheduled_split_on_eps_actual(tmp_path):
    """AB-14 — ★ `epsActual` present ⇒ reported, absent ⇒ still scheduled."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.earnings import refresh_earnings

    store = EventStore(tmp_path)
    out = refresh_earnings(_EarningsClient(), store, tickers=("ZZ",),
                           as_of=date(2026, 8, 28), since=date(2026, 7, 1))
    assert out["reported"] == 1 and out["scheduled"] == 1
    classes = set(store.read()["event_class"])
    assert classes == {"earnings_reported", "earnings_scheduled"}


def test_a_reported_result_is_knowable_on_its_announcement_date(tmp_path):
    """DE-34 — ⚠ a result announced on the 30th was not knowable on the 29th.
    ★ `date` is the ANNOUNCEMENT date on this feed: Apple's rows fall in late
    Jan/Apr/Jul/Oct, not on period ends."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.earnings import refresh_earnings

    store = EventStore(tmp_path)
    refresh_earnings(_EarningsClient(), store, tickers=("ZZ",),
                     as_of=date(2026, 8, 28), since=date(2026, 7, 1))
    row = store.read().query("event_class == 'earnings_reported'").iloc[0]
    assert row["event_date"].date() == date(2026, 7, 30)
    assert row["knowable_at"].date() == date(2026, 7, 30)


def test_a_scheduled_date_is_knowable_because_we_looked_TODAY(tmp_path):
    """AC-7.88 (DE-71, DE-65) — ⚠⚠ **The knowability axes differ, and conflating them is look-ahead.**
    A future earnings date is not knowable *on that date* — what is knowable is
    that we saw this schedule today. ★ And a scheduled date **moves**, so
    today's calendar cannot answer a historical question (DE-65)."""
    import json

    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.earnings import refresh_earnings

    store = EventStore(tmp_path)
    refresh_earnings(_EarningsClient(), store, tickers=("ZZ",),
                     as_of=date(2026, 8, 28), since=date(2026, 7, 1))
    row = store.read().query("event_class == 'earnings_scheduled'").iloc[0]
    assert row["event_date"].date() == date(2026, 10, 29)
    assert row["knowable_at"].date() == date(2026, 8, 28)
    assert "moves" in json.loads(row["detail"])["caveat"]


def test_lastUpdated_is_never_used_as_a_knowability_date():
    """DE-23 / AC-7.37 — ⚠⚠ the trap is LIVE on this feed. *Measured:* **17 of
    AAPL's 20 quarters share one `lastUpdated`**, `2026-06-04`. It is a batch
    reload stamp, and using it would place a result years from when it was
    reported."""
    import inspect

    from src.data_engine.ingest import earnings

    source = inspect.getsource(earnings)
    assert "FORBIDDEN_KNOWABILITY" in source
    body = source.split("def refresh_earnings", 1)[1]
    assert "lastUpdated" not in body, "lastUpdated must never reach a Finding"


def test_a_capped_chunk_is_SPLIT_rather_than_silently_truncated():
    """DE-58 — ⚠⚠ *measured 2026-08-28:* asking for 2026 returned only
    2026-11-05.. — the cap keeps the LATEST rows and says nothing. ★ A response
    at the cap is treated as truncated and the window is halved."""
    from src.data_engine.ingest.earnings import MAX_SPLIT_DEPTH, _fetch_span

    client = _CappedClient()
    rows, spans, truncated = _fetch_span(client, date(2026, 1, 1),
                                         date(2026, 1, 8), depth=0)
    assert len(client.calls) > 1, "a capped window must be split, not accepted"
    assert truncated, "a window that stays capped is ADMITTED, never hidden"


def test_an_uncoverable_window_records_NO_refresh(tmp_path):
    """DE-58 — ⚠⚠ a capped chunk means unseen names inside the window. ★ Marking
    the class CHECKED would claim them, which is the defect §6A exists to stop."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.earnings import refresh_earnings

    store = EventStore(tmp_path)
    out = refresh_earnings(_CappedClient(), store, tickers=("ZZ",),
                           as_of=date(2026, 8, 28), since=date(2026, 8, 20))
    assert out["refreshed"] == [] and out["truncated"]
    assert "NOT fully covered" in out["why"]
    # ⚠ A cap and a REFUSAL both leave the window uncovered and need different
    #   fixes — saying "the cap" of a 402 sends a reader to the wrong one.
    assert out["truncated"][0]["cause"] == "capped"


def test_the_surprise_travels_not_just_the_level(tmp_path):
    """★ The FLAG-worthy content is actual **against expectation** — an EPS of
    2.02 says nothing without the 1.90 that was expected."""
    import json

    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.earnings import refresh_earnings

    store = EventStore(tmp_path)
    refresh_earnings(_EarningsClient(), store, tickers=("ZZ",),
                     as_of=date(2026, 8, 28), since=date(2026, 7, 1))
    d = json.loads(store.read().query(
        "event_class == 'earnings_reported'").iloc[0]["detail"])
    assert d["surprise"] == round((2.02 - 1.90) / 1.90, 6)


def test_one_submissions_pass_answers_three_classes(tmp_path):
    """AB-14 — ★★ classes 4, 7 and 11 all come from the same `submissions`
    document, so fetching it three times would triple EDGAR's throttled cost
    for nothing."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.submissions import (
        SUBMISSION_CLASSES, refresh_restatements)

    store = EventStore(tmp_path)
    out = refresh_restatements(_EdgarSubs(), store, tickers=("ZZ",),
                               cik_map={"ZZ": "0000000001"},
                               as_of=date(2026, 8, 28),
                               classes=SUBMISSION_CLASSES)
    assert set(out["refreshed"]) == set(SUBMISSION_CLASSES)
    assert out["by_class"]["restatement_amended"] == 3     # 2 amended + 1 4.02
    assert out["by_class"]["filing_mid_window"] == 1       # the plain 10-K
    assert "material_event_8k" not in out["by_class"]      # the only 8-K was 4.02


def test_an_amendment_is_class_4_and_never_also_class_7(tmp_path):
    """⚠⚠ **Order matters.** A filing is emitted under exactly one class — if
    the periodic test ran first, every `10-K/A` would arrive twice and a
    consumer counting periodic filings would double-count restatements."""
    from src.data_engine.ingest.submissions import _classify

    assert _classify("10-K/A", "") == ("restatement_amended", "amended_filing")
    assert _classify("10-K", "") == ("filing_mid_window", "periodic_filing")


def test_a_non_reliance_8k_outranks_an_ordinary_material_event():
    """★★ 8-K item 4.02 is a **restatement announcement**, not routine news —
    it must not be filed as class 11 where it would read as one 8-K among
    hundreds."""
    from src.data_engine.ingest.submissions import _classify

    assert _classify("8-K", "4.02,9.01")[0] == "restatement_amended"
    assert _classify("8-K", "2.02,9.01")[0] == "material_event_8k"


# --------------------------------------------------------------------------- #
# Classes 13/14/15 (disclosures) and 16 (macro). AB-14
# --------------------------------------------------------------------------- #

class _GradesClient:
    """⚠ Mirrors the measured behaviour: **`limit` is ignored entirely.**"""

    def __init__(self, n=1200):
        self.rows = [{"symbol": "ZZ", "date": f"{2012 + (i // 120)}-03-0"
                                              f"{1 + (i % 9)}",
                      "gradingCompany": "Firm", "previousGrade": "Hold",
                      "newGrade": "Buy", "action": "upgrade"} for i in range(n)]

    def get(self, endpoint, **params):
        assert endpoint == "grades"
        return self.rows          # ★ limit is NOT honoured, deliberately


def test_a_feed_that_ignores_limit_is_windowed_client_side(tmp_path):
    """AB-14 — ⚠⚠ *measured 2026-08-28:* `grades` returns the **same 1 791 rows**
    for limit=5, limit=50 and no limit, back to 2012. ★ Across 510 names that is
    ~900 000 findings from one NOTE class, so the window is enforced HERE."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.disclosures import refresh_analyst_actions

    store = EventStore(tmp_path)
    out = refresh_analyst_actions(_GradesClient(), store, tickers=("ZZ",),
                                  as_of=date(2026, 8, 28),
                                  since=date(2026, 1, 1))
    assert out["findings"] < 100, "the window must bite, not the vendor's limit"


def test_the_per_ticker_cap_is_ours_and_is_admitted(tmp_path):
    """CN-10 / DE-35 — ★ a cap that silently drops rows is worse than no cap.
    ⚠ The truncated names are named in the result."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.disclosures import (
        MAX_ROWS_PER_TICKER, refresh_analyst_actions)

    store = EventStore(tmp_path)
    out = refresh_analyst_actions(_GradesClient(n=MAX_ROWS_PER_TICKER + 200),
                                  store, tickers=("ZZ",), as_of=date(2026, 8, 28))
    assert out["capped"] == ["ZZ"] and "cap" in out["why"]


def test_a_failed_name_is_excluded_from_coverage(tmp_path):
    """DE-58 — ⚠ a name that errored was never examined. ★ Including it in
    coverage would let a gate inherit a claim this sweep cannot support."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.disclosures import refresh_analyst_actions

    class Flaky(_GradesClient):
        def get(self, endpoint, **params):
            if params.get("symbol") == "BAD":
                raise RuntimeError("boom")
            return self.rows

    store = EventStore(tmp_path)
    out = refresh_analyst_actions(Flaky(n=10), store, tickers=("ZZ", "BAD"),
                                  as_of=date(2026, 8, 28))
    assert out["reached"] == ("ZZ",) and "BAD" in out["failed"]


class _MacroClient:
    """⚠ Truncating: returns only the LAST 3 days of any window asked for."""

    def __init__(self, truncate=False):
        self.truncate = truncate

    def get(self, endpoint, **params):
        assert endpoint == "economic-calendar"
        lo = date.fromisoformat(params["from"])
        hi = date.fromisoformat(params["to"])
        start = hi - timedelta(days=2) if self.truncate else lo
        out, day = [], start
        while day <= hi:
            out.append({"date": day.isoformat(), "country": "US",
                        "event": "CPI", "impact": "High", "actual": 3.1,
                        "estimate": 3.0, "previous": 2.9, "unit": "%"})
            out.append({"date": day.isoformat(), "country": "JP",
                        "event": "Tankan", "impact": "High", "actual": 1.0,
                        "estimate": 1.0, "previous": 1.0, "unit": "%"})
            day += timedelta(days=1)
        return out


def test_a_macro_release_is_stored_once_not_once_per_ticker(tmp_path):
    """⚠⚠ **The only class with no ticker.** ★ 510 copies of one CPI print would
    make the store's size a function of universe width rather than information."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.macro import MARKET_WIDE, refresh_macro

    store = EventStore(tmp_path)
    refresh_macro(_MacroClient(), store, as_of=date(2026, 8, 10),
                  since=date(2026, 8, 1))
    assert set(store.read()["ticker"]) == {MARKET_WIDE}


def test_only_the_book_s_own_economies_are_kept(tmp_path):
    """INV-5 — ★ the book is USD/CAD; a Japanese print is not an event for it."""
    import json

    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.macro import refresh_macro

    store = EventStore(tmp_path)
    refresh_macro(_MacroClient(), store, as_of=date(2026, 8, 10),
                  since=date(2026, 8, 1))
    countries = {json.loads(r["detail"])["country"]
                 for r in store.read().to_dict("records")}
    assert countries == {"US"}


def test_a_truncated_macro_window_records_NO_refresh(tmp_path):
    """DE-70 / DE-58 — ⚠⚠ *measured:* asking `economic-calendar` for 2026
    returned **only October onward**, and a WIDER request returned FEWER rows.
    ★ The tell is the span, not a row count, so that is what is checked."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.macro import refresh_macro

    store = EventStore(tmp_path)
    out = refresh_macro(_MacroClient(truncate=True), store,
                        as_of=date(2026, 8, 30), since=date(2026, 7, 1),
                        chunk_days=30)
    assert out["refreshed"] == [] and out["short"]
    assert out["short"][0]["cause"] == "truncated"


def test_a_quiet_calendar_is_NOT_reported_as_truncation(tmp_path):
    """CN-10 / DE-35 — ⚠⚠ **a false positive I shipped and the live run caught.**
    A window in the FUTURE is sparse by nature: `2026-11-21..26` returned from
    the 23rd because nothing was scheduled earlier, and the first cut called
    that truncation. ★ The measured real case was **nine months missing from a
    year** — so the threshold is a large head, not any gap."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.macro import refresh_macro

    store = EventStore(tmp_path)
    # ★ A 3-day head gap inside a 30-day chunk — quiet, not truncated.
    out = refresh_macro(_MacroClient(truncate=True), store,
                        as_of=date(2026, 8, 30), since=date(2026, 8, 28),
                        chunk_days=5)
    assert out["short"] == [], "a short quiet stretch must not read as truncation"


# --------------------------------------------------------------------------- #
# AB-14's other half — which classes are DUE. QD-16
# --------------------------------------------------------------------------- #

def test_cadence_follows_severity_not_convenience(tmp_path):
    """QD-16 / CN-10 — ★ a stale **BLOCK** can let a real split through
    unhandled; a stale **NOTE** costs a reader some context. ⚠ One interval for
    both would either hammer the rate limit for news or leave splits unchecked
    for a week."""
    from src.data_engine.calendar.classes import EVENT_CLASSES
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.cadence import due

    store = EventStore(tmp_path)
    # ★ Both refreshed 3 days ago: the BLOCK is due, the NOTE is not.
    for name in ("split", "news"):
        store.record_refresh(name, date(2026, 8, 1), date(2026, 8, 25),
                             covers_tickers=("ZZ",))
    frame = store.freshness()
    frame["split"]["refreshed_at"] = "2026-08-25T00:00:00+00:00"
    frame["news"]["refreshed_at"] = "2026-08-25T00:00:00+00:00"

    class Fixed:
        def freshness(self):
            return frame

    state = due(Fixed(), EVENT_CLASSES, as_of=date(2026, 8, 28))
    assert "split" in state["due"], "a BLOCK stale by 3 days is due"
    assert "news" in state["fresh"], "a NOTE stale by 3 days is not"


def test_a_class_that_can_never_be_swept_is_EXEMPT_not_perpetually_due(tmp_path):
    """DE-35 — ⚠ reporting `index_membership` as overdue **every day** would
    train a reader to ignore the whole report. ★ It has no source at any price,
    which is a different state from *late*."""
    from src.data_engine.calendar.classes import EVENT_CLASSES
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.cadence import due

    state = due(EventStore(tmp_path), EVENT_CLASSES, as_of=date(2026, 8, 28))
    assert "index_membership" in state["exempt"]
    assert "index_membership" not in state["due"]


def test_never_refreshed_is_reported_apart_from_merely_stale(tmp_path):
    """DE-35 — ★ *never* and *late* need different fixes, so they are counted
    separately rather than summed into one 'not fresh'."""
    from src.data_engine.calendar.classes import EVENT_CLASSES
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.cadence import due, report

    state = due(EventStore(tmp_path), EVENT_CLASSES, as_of=date(2026, 8, 28))
    assert state["due"] == [] and len(state["never"]) > 10
    assert "NEVER refreshed" in report(state)


def test_a_derived_class_is_exempt_not_never_refreshed(tmp_path):
    """DE-35 — ⚠ `price_adjustment_state` is computed **at check time** and has
    no refresh to be stale. ★ Reporting it as *never refreshed* would
    contradict the class listing, which calls it finished by construction."""
    from src.data_engine.calendar.classes import EVENT_CLASSES
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.cadence import due

    state = due(EventStore(tmp_path), EVENT_CLASSES, as_of=date(2026, 8, 28),
                derived=("price_adjustment_state",))
    assert "price_adjustment_state" in state["exempt"]
    assert "price_adjustment_state" not in state["never"]


class _DelistingFeed:
    """Three weeks of rows, as the Starter plan serves `delisted-companies`."""

    def get(self, endpoint, **params):
        assert endpoint == "delisted-companies"
        return [{"symbol": "AVB", "exchange": "NYSE", "delistedDate": "2026-08-18",
                 "companyName": "AvalonBay"},
                {"symbol": "OTHR", "exchange": "NASDAQ", "delistedDate": "2026-08-06",
                 "companyName": "Other"},
                {"symbol": "LATE", "exchange": "NYSE", "delistedDate": "2026-08-26",
                 "companyName": "Late"}]


def test_ac_7_77_the_delisting_refresh_records_the_window_REACHED(tmp_path):
    """AC-7.77 (DE-59, DE-60) — *the feed's reachable window is recorded, not the
    requested one.* ✏ Written 2026-10-06 (L9 §8 D4): the other half of AC-7.77 (a
    delisting HALTs, is not cleared) was tested; this half was not. ⚠ Recording a
    ten-year window from a three-week feed would make the class read CHECKED over
    years nobody fetched — DE-56/DE-58's defect again."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh_delistings

    store = EventStore(tmp_path)
    out = refresh_delistings(_DelistingFeed(), store, tickers=("AVB",),
                             as_of=date(2026, 8, 28))
    record = store.freshness()["delisting"]
    assert (record["covers_from"], record["covers_to"]) == ("2026-08-06", "2026-08-26")
    assert record["covers_tickers"] == ["AVB"]
    assert out["findings"] == 1, "only the wanted, US-listed name becomes a finding"


def test_ac_7_77_an_empty_delisting_feed_records_no_refresh(tmp_path):
    """AC-7.77 — no dated rows means nothing was reached, so NO window is recorded
    (the class stays UNCHECKED rather than reading as a clean sweep)."""
    from src.data_engine.calendar.store import EventStore
    from src.data_engine.ingest.events import refresh_delistings

    class _Empty:
        def get(self, endpoint, **params):
            return []

    store = EventStore(tmp_path)
    out = refresh_delistings(_Empty(), store, tickers=("AVB",), as_of=date(2026, 8, 28))
    assert out["refreshed"] == [] and "delisting" not in store.freshness()
