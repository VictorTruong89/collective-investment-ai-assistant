"""D-07 point-in-time — AC-7.7…7.18, AC-7.35…7.42, AC-7.62 (§6, §5C).

Tier: invariant/property (INV-1, INV-2) + data contract (constitution §4).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pandas as pd
import pytest

from src.data_engine.contracts.panels import (
    FUNDAMENTAL_PANEL, validate_fundamental_panel,
)
from src.data_engine.contracts.schema import Column, Schema
from src.data_engine.errors import (
    AppendOnlyError, AsOfRequiredError, ContractViolationError, DerivedNoFilingDateError,
    MissingCurrencyError, NoFilingDateError,
)
from src.data_engine.pit.ledger import FactLedger
from src.data_engine.pit.models import Fact
from src.data_engine.pit.restatement import (
    FORBIDDEN_KNOWABILITY_FIELDS, diff_against_stored, knowability_date, market_cap_at,
    next_session_knowability,
)
from src.data_engine.pit.snapshot import (
    assemble_rows, facts_as_of, inherit_filing_date, restatement_flags,
)
from tests_src.data_engine_fixtures import fact

ORIGINAL = fact(accession="0000-1", value=1_000_00, filed=date(2024, 4, 25))
RESTATED = fact(accession="0000-2", value=900_00, filed=date(2024, 10, 30))


def ledger_frame(*facts) -> pd.DataFrame:
    from src.data_engine.pit.ledger import _to_frame
    return _to_frame(list(facts))


# --------------------------------------------------------------------------- #
# §6.3 resolution
# --------------------------------------------------------------------------- #

def test_ac_7_7_as_of_excludes_every_fact_filed_after_it():
    """AC-7.7 — step 1 of §6.3, and the whole guarantee (INV-1)."""
    df = ledger_frame(ORIGINAL, RESTATED)
    early = facts_as_of(df, date(2024, 6, 1))
    assert len(early) == 1
    assert int(early.iloc[0]["value_minor"]) == 1_000_00


def test_ac_7_8_a_restatement_filed_before_d_is_returned():
    """AC-7.8 — ★ §6.3 step 3, the subtle one.

    "Knowable on D" is NOT "the first thing filed". If a restatement landed on
    or before D, it *was* knowable on D — the filter is on publication, not on
    originality. Getting this backwards is defensibly conservative and quietly
    wrong in the other direction.
    """
    df = ledger_frame(ORIGINAL, RESTATED)
    late = facts_as_of(df, date(2024, 12, 1))
    assert len(late) == 1
    assert int(late.iloc[0]["value_minor"]) == 900_00
    assert late.iloc[0]["accession_id"] == "0000-2"


def test_ac_7_9_a_fact_with_no_filing_date_is_rejected_at_ingest(tmp_path):
    """AC-7.9 — DE-6.3. It cannot be placed in time, so it can never be served."""
    ledger = FactLedger(tmp_path)
    undateable = Fact.__new__(Fact)
    object.__setattr__(undateable, "ticker", "MSFT")
    object.__setattr__(undateable, "tag", "Revenues")
    object.__setattr__(undateable, "period_end", date(2024, 3, 31))
    object.__setattr__(undateable, "filing_date", None)
    with pytest.raises(NoFilingDateError, match="rejected at ingest"):
        ledger.append([undateable])


def test_ac_7_10_omitting_as_of_raises_with_no_default_to_today():
    """AC-7.10 — DE-6.4, the rule most likely to be eroded.

    `as_of=None -> today` is silently CORRECT in production and silently wrong in
    every backtest, and the numbers look right in both cases.
    """
    df = ledger_frame(ORIGINAL)
    with pytest.raises(AsOfRequiredError, match="convenient signature"):
        facts_as_of(df)
    with pytest.raises(AsOfRequiredError):
        facts_as_of(df, None)


def test_ac_7_11_same_ledger_and_as_of_give_byte_identical_output():
    """AC-7.11 — INV-2 determinism (DE-6.6)."""
    df = ledger_frame(ORIGINAL, RESTATED, fact(tag="CostOfRevenue", accession="0000-1"))
    a = facts_as_of(df, date(2024, 12, 1))
    b = facts_as_of(df.sample(frac=1.0, random_state=7), date(2024, 12, 1))
    pd.testing.assert_frame_equal(a, b)


def test_ac_7_12_the_ledger_is_append_only(tmp_path):
    """AC-7.12 — a restatement ADDS a row and changes none (DE-6.2).

    Overwriting destroys the only information that makes look-ahead detectable,
    and it does so invisibly: the resulting ledger is internally consistent.
    """
    ledger = FactLedger(tmp_path)
    assert ledger.append([ORIGINAL]) == 1
    assert ledger.append([RESTATED]) == 1
    stored = ledger.read("MSFT")
    assert len(stored) == 2
    assert sorted(stored["value_minor"]) == [900_00, 1_000_00]

    assert ledger.append([ORIGINAL]) == 0, "re-ingest is idempotent (DE-11)"

    tampered = fact(accession="0000-1", value=1, filed=date(2024, 4, 25))
    with pytest.raises(AppendOnlyError, match="append-only"):
        ledger.append([tampered])


def test_ac_7_13_a_restated_period_is_visibly_marked():
    """AC-7.13 — DE-6.5: restatements are surfaced, not smoothed."""
    df = ledger_frame(ORIGINAL, RESTATED)
    flags = restatement_flags(df, date(2024, 12, 1))
    assert int(flags.iloc[0]["filings"]) == 2

    rows = assemble_rows(df, date(2024, 12, 1))
    assert bool(rows.iloc[0]["restated"]) is True
    assert bool(assemble_rows(df, date(2024, 6, 1)).iloc[0]["restated"]) is False


# --------------------------------------------------------------------------- #
# Contracts & money
# --------------------------------------------------------------------------- #

def test_ac_7_14_a_minor_column_without_its_currency_sibling_fails_validation():
    """AC-7.14 — CT-M.1/INV-001, enforced by the SCHEMA rather than per contract."""
    schema = Schema("CT-test", "t", (Column("price_minor", "int64"),), monetary=("price",))
    with pytest.raises(MissingCurrencyError, match="untagged number"):
        schema.validate(pd.DataFrame({"price_minor": [1]}))


def test_ac_7_16_both_period_start_and_period_end_are_present():
    """AC-7.16 — §5.1. Without both, cumulative-vs-discrete is a guess."""
    rows = assemble_rows(ledger_frame(ORIGINAL), date(2024, 12, 1))
    assert rows["period_start"].notna().all()
    assert rows["period_end"].notna().all()

    missing = rows.drop(columns=["period_start"])
    with pytest.raises(ContractViolationError, match="period_start"):
        validate_fundamental_panel(missing)


def test_ac_7_17_ct_7_2_is_rebuilt_from_ct_7_3_and_matches(tmp_path):
    """AC-7.17 — the ledger is the system of record; the panel is derived from it.

    Rebuilt "byte-for-byte" is asserted at a stated `as_of`, because CT-7.2 has
    no meaning without one — a panel is always a panel AS OF something.
    """
    ledger = FactLedger(tmp_path)
    ledger.append([ORIGINAL, RESTATED])
    first = assemble_rows(ledger.read("MSFT"), date(2024, 12, 1))
    second = assemble_rows(FactLedger(tmp_path).read("MSFT"), date(2024, 12, 1))
    pd.testing.assert_frame_equal(first.drop(columns=["ingested_at"]),
                                  second.drop(columns=["ingested_at"]))


def test_ac_7_62_every_fact_carries_period_type():
    """AC-7.62 — §6.3 step 2 groups on (tag, period_end, period_type) (CT-7.3).

    Added 2026-08-23: the contract had never declared `period_type`, so the PIT
    resolver keyed on a field its own ledger did not have.
    """
    from src.data_engine.contracts.ledgers import FACT_LEDGER
    assert "period_type" in FACT_LEDGER.names
    assert "period_type" in FACT_LEDGER.key

    annual = fact(period_type="annual", start=date(2023, 4, 1), end=date(2024, 3, 31),
                  accession="0000-3", value=4_000_00)
    quarterly = fact(period_type="quarterly", end=date(2024, 3, 31), accession="0000-3")
    resolved = facts_as_of(ledger_frame(annual, quarterly), date(2024, 12, 1))
    assert len(resolved) == 2, "a year and a quarter ending the same day are two Facts"


# --------------------------------------------------------------------------- #
# §5C — the defects measured in the dump
# --------------------------------------------------------------------------- #

def test_ac_7_35_fmp_rows_are_placed_by_accepted_date_never_by_period_end():
    """AC-7.35 — DE-21. The gap is 20-57 days, median 28, measured on MU."""
    row = {"date": "2026-05-28", "filingDate": "2026-06-25",
           "acceptedDate": "2026-06-24 18:59:46"}
    assert knowability_date(row, ticker="MU") == date(2026, 6, 24)

    assert knowability_date({"date": "2026-05-28", "filingDate": "2026-06-25"},
                            ticker="MU") == date(2026, 6, 25)

    with pytest.raises(NoFilingDateError):
        knowability_date({"date": "2026-05-28"}, ticker="MU")


def test_ac_7_36_a_derived_periodic_inherits_its_statement_accepted_date():
    """AC-7.36 — DE-22. With no matching statement it is NOT served PIT."""
    index = {("MU", date(2026, 5, 28), "quarterly"): date(2026, 6, 24)}
    assert inherit_filing_date(("MU", date(2026, 5, 28), "quarterly"), index,
                               "key-metrics") == date(2026, 6, 24)

    with pytest.raises(DerivedNoFilingDateError, match="cannot be placed in time"):
        inherit_filing_date(("MU", date(2026, 8, 28), "quarterly"), index, "ratios")


def test_ac_7_37_last_updated_is_never_a_knowability_date():
    """AC-7.37 — DE-23. It is a BATCH RELOAD STAMP, not a revision axis.

    99 MSFT quarters share 8 distinct `lastUpdated` values and the median row was
    "last updated" eleven years after it was reported.
    """
    assert "lastUpdated" in FORBIDDEN_KNOWABILITY_FIELDS
    row = {"date": "2003-06-30", "lastUpdated": "2025-09-06"}
    with pytest.raises(NoFilingDateError):
        knowability_date(row, ticker="MSFT")


def test_ac_7_38_a_served_artifact_states_which_pit_guarantee_it_carries():
    """AC-7.38 — DE-23. Reconstructed (EDGAR) vs best-effort (FMP)."""
    edgar = assemble_rows(ledger_frame(ORIGINAL), date(2024, 12, 1), source="edgar")
    fmp = assemble_rows(ledger_frame(ORIGINAL), date(2024, 12, 1), source="fmp")
    assert edgar.iloc[0]["pit_guarantee"] == "reconstructed"
    assert fmp.iloc[0]["pit_guarantee"] == "best_effort"
    assert fmp.iloc[0]["accession_id"] is None, "FMP rows carry no accession (CT-7.2)"


def test_ac_7_39_re_ingesting_an_fmp_periodic_diffs_rather_than_overwriting():
    """AC-7.39 — DE-24, the only restatement detection available on the FMP side."""
    key = ["ticker", "period_end"]
    stored = pd.DataFrame({"ticker": ["MU"], "period_end": ["2024-05-30"],
                           "revenue_minor": [6_810_000_00]})
    incoming = pd.DataFrame({"ticker": ["MU"], "period_end": ["2024-05-30"],
                             "revenue_minor": [6_811_000_00]})
    changes = diff_against_stored(stored, incoming, key=key, value_col="revenue_minor")
    assert len(changes) == 1
    assert changes.iloc[0]["code"] == "DATA.RESTATEMENT.VALUE_CHANGED"
    assert int(changes.iloc[0]["stored"]) == 6_810_000_00

    assert len(diff_against_stored(stored, stored, key=key,
                                   value_col="revenue_minor")) == 0


def test_ac_7_40_past_market_cap_is_close_times_shares_at_that_date():
    """AC-7.40 — DE-25. `historical-market-capitalization` leaks ~28 days a quarter.

    The share count it implies steps on the PERIOD END, 21-36 days before the
    filing that disclosed it — so every marketCap in that window is built from a
    number that was not yet public.
    """
    assert market_cap_at(12089, 2_458_000_000) == 12089 * 2_458_000_000
    with pytest.raises(ValueError, match="plausible number with no meaning"):
        market_cap_at(12089, 0)


def test_ac_7_41_scheduled_and_occurred_are_separate_entities():
    """AC-7.41 — DE-18/DE-19. A calendar entry carries both dates, or it is unusable."""
    from src.data_engine.pit.models import CalendarEntry, CorporateEvent

    scheduled = CalendarEntry("MSFT", "earnings", date(2026, 10, 28), None, "fmp")
    assert scheduled.servable_to_model is False, "no knowability axis — DE-18"

    snapshotted = CalendarEntry("MSFT", "earnings", date(2026, 10, 28),
                                date(2026, 9, 1), "ct-7.6")
    assert snapshotted.servable_to_model is True

    occurred = CorporateEvent("MSFT", "dividend", date(2024, 5, 16), date(2024, 3, 5),
                              {"cash_minor": 75}, "fmp:dividends")
    assert type(occurred) is not type(scheduled), "DE-19 — different entities, not a flag"


def test_ac_7_42_a_news_feature_window_starts_at_first_capture(tmp_path):
    """AC-7.42 — DE-26. There is no historical news backfill at any price."""
    from src.data_engine.observation.ledger import ObservationLedger

    ledger = ObservationLedger(tmp_path)
    stamp = datetime(2026, 8, 1, 12, tzinfo=timezone.utc)
    ledger.snapshot(ticker="MSFT", field_set="news_capture", payload={"n": 3},
                    source_endpoint="news/stock", observed_at=stamp)
    assert ledger.first_capture("news_capture", "MSFT") == date(2026, 8, 1)
    assert ledger.first_capture("news_capture", "NVDA") is None


def test_next_session_knowability_after_the_close():
    """§5C.5 — 408 of 437 MSFT filings were accepted at or after 16:00 ET (K-9)."""
    sessions = [date(2026, 6, 24), date(2026, 6, 25), date(2026, 6, 26)]
    after = datetime(2026, 6, 24, 18, 59, 46)
    before = datetime(2026, 6, 24, 9, 15, 0)
    assert next_session_knowability(after, sessions) == date(2026, 6, 25)
    assert next_session_knowability(before, sessions) == date(2026, 6, 24)
