"""D-07 — EDGAR companyfacts into the fact ledger. ★ The write nothing did."""
from datetime import date

import pandas as pd

from src.data_engine.ingest.edgar_facts import THESIS_TAGS, load_cik_map


def test_the_cik_map_keeps_its_leading_zeros():
    """⚠ YAML reads an unquoted `0001045810` as the integer `1045810`. ★ The
    zeros are not decoration: a map that has lost them cannot tell a missing
    entry from a mangled one."""
    cik_map = load_cik_map()
    assert cik_map["NVDA"] == "0001045810"
    assert all(len(v) == 10 for v in cik_map.values())


def test_the_map_covers_the_names_the_book_and_the_universe_hold():
    """★ A thesis needs a CIK, so a nominated name without one cannot be
    authored — better to see the gap here than at authoring time."""
    cik_map = load_cik_map()
    for ticker in ("NVDA", "SNDK", "ARM", "PLTR", "DELL"):
        assert ticker in cik_map, f"{ticker} has no CIK"


def test_the_tag_set_is_restricted_on_purpose():
    """⚠ Companyfacts for a large filer runs to hundreds of concepts — MU's
    as-reported quarterly alone spans 536 tags. ★ Ingesting all of them buries
    the figures a reader checks in a bundle nobody can read."""
    assert 5 <= len(THESIS_TAGS) <= 40
    assert "Revenues" in THESIS_TAGS and "GrossProfit" in THESIS_TAGS


def test_ac_7_68_identical_duplicates_collapse():
    """DE-51 — ⚠ 5 of 130 names failed CT-7.3's guard because EDGAR emits one
    fact twice under two unit or frame labels."""
    from src.data_engine.ingest.edgar_facts import _collapse_identical

    class _F:
        def __init__(self, value):
            self.ticker, self.accession_id, self.tag = "WMT", "a-1", "Revenues"
            self.period_start, self.period_end, self.period_type = 1, 2, "quarterly"
            self.value_minor, self.value_currency = value, "USD"

    kept, conflicts = _collapse_identical([_F(100), _F(100)])
    assert len(kept) == 1 and conflicts == []


def test_ac_7_68_a_value_conflict_on_one_key_keeps_neither_value():
    """★★ DE-51 — ⚠ *deduplicating by "keep the first" picks a reported figure
    by ARRIVAL ORDER*, which is the silent choice P5 exists to prevent.

    ✏ DE-85 (`DX-180`, 2026-10-21): it no longer reaches CT-7.3 to refuse the whole
    name — NEITHER value is kept, and the conflict is returned to be reported."""
    from src.data_engine.ingest.edgar_facts import _collapse_identical

    class _F:
        def __init__(self, value):
            self.ticker, self.accession_id, self.tag = "WMT", "a-1", "Revenues"
            self.period_start, self.period_end, self.period_type = 1, 2, "quarterly"
            self.value_minor, self.value_currency = value, "USD"

    kept, conflicts = _collapse_identical([_F(100), _F(101)])
    assert kept == [] and conflicts == [("Revenues", "2")]


def test_ac_7_69_no_per_share_tag_is_ingested_as_monetary():
    """★★ DE-52 — a `0` meaning *"not a monetary quantity"* is indistinguishable
    from a `0` meaning *"the company earned nothing"*."""
    from src.data_engine.ingest.edgar_facts import NOT_MONETARY, THESIS_TAGS

    assert "EarningsPerShareDiluted" in NOT_MONETARY
    assert not (THESIS_TAGS & NOT_MONETARY)


# --------------------------------------------------------------------------- #
# DE-55 — Q_n = YTD_n − YTD_(n−1), the arithmetic EDGAR is chosen for
# --------------------------------------------------------------------------- #

def _ytd(start, ends_and_values, tag="NetCashProvidedByUsedInOperatingActivities"):
    return {"facts": {"us-gaap": {tag: {"units": {"USD": [
        {"start": start, "end": end, "val": val, "accn": f"a-{i}",
         "filed": end, "form": "10-Q", "fy": 2026, "fp": "Q1"}
        for i, (end, val) in enumerate(ends_and_values)]}}}}}


def test_de_55_a_year_to_date_series_yields_discrete_quarters():
    """★★ **The arithmetic EDGAR is chosen for** (CLAUDE.md: *its facts carry
    explicit period start and end, so a discrete quarter is distinguishable from
    a cumulative YTD one by arithmetic*).

    ⚠ `discrete_from_cumulative` has been in `xbrl.py` since B2 and **nothing
    ever called it**: `_one` rejected every cumulative span outright. NVDA's raw
    cash-flow facts carry 38 discrete quarters and **70 year-to-date spans**, so
    roughly two of every three quarters had no cash flow at all — and every
    four-period rolling feature was null, which reads as sparse data.
    """
    from src.data_engine.src.edgar.companyfacts import extract_facts

    payload = _ytd("2025-01-27", [("2025-04-27", 27414), ("2025-07-27", 42779),
                                  ("2025-10-26", 66530), ("2026-01-25", 102718)])
    facts = extract_facts(payload, ticker="NVDA")
    quarters = {f.period_end: f.value_minor / 100
                for f in facts.facts if f.period_type == "quarterly"}
    assert len(quarters) == 4, quarters
    # ★ Self-checking: the four discrete quarters sum to the reported year.
    assert round(sum(quarters.values())) == 102718


def test_de_55_a_repeated_span_is_not_differenced_against_itself():
    """⚠ One `(start, end)` arrives from several accessions — the original filing
    and every later one that restates it. Differencing a span against itself
    yields a **zero-day, zero-value fact that looks like a quarter with no cash
    flow**."""
    from src.data_engine.src.edgar.companyfacts import extract_facts

    payload = _ytd("2025-01-27", [("2025-04-27", 27414), ("2025-07-27", 42779),
                                  ("2025-07-27", 42779)])          # duplicate
    facts = extract_facts(payload, ticker="NVDA")
    values = [f.value_minor for f in facts.facts if f.period_type == "quarterly"]
    assert 0 not in values


def test_de_55_a_missing_operand_yields_no_fact_rather_than_zero():
    """DE-14 — ★ *a subtraction with one operand absent is not zero*."""
    from src.data_engine.src.edgar.companyfacts import extract_facts

    payload = _ytd("2025-01-27", [("2025-04-27", 27414), ("2025-07-27", None)])
    facts = extract_facts(payload, ticker="NVDA")
    assert [f.period_end for f in facts.facts if f.period_type == "quarterly"] \
        == [date(2025, 4, 27)]


def test_ac_7_102_an_average_or_per_share_series_is_never_differenced():
    """AC-7.102 / DE-84 — ★★ *found 2026-10-21 (DX-177):* MU's FY2026 10-K gave a derived
    Q4 diluted share count of 1,000,000 — the year's AVERAGE minus nine months' AVERAGE."""
    from src.data_engine.src.edgar.companyfacts import extract_facts

    def series(unit, tag):
        return {"facts": {"us-gaap": {tag: {"units": {unit: [
            {"start": "2025-08-29", "end": end, "val": val, "accn": "0000723125-26-000023",
             "filed": "2026-10-09", "form": "10-K", "fy": 2026, "fp": "FY"}
            for end, val in (("2026-05-28", 1142000000), ("2026-09-03", 1143000000))]}}}}}

    shares = extract_facts(series("shares", "WeightedAverageNumberOfDilutedSharesOutstanding"),
                           ticker="MU")
    assert not [f for f in shares.facts if f.period_type == "quarterly"]
    eps = extract_facts(series("USD/shares", "EarningsPerShareDiluted"), ticker="MU")
    assert not [f for f in eps.facts if f.period_type == "quarterly"]
    cash = extract_facts(series("USD", "NetCashProvidedByUsedInOperatingActivities"), ticker="MU")
    assert [f.period_end for f in cash.facts if f.period_type == "quarterly"] == [date(2026, 9, 3)]


# --------------------------------------------------------------------------- #
# DE-85 (DX-180) — a defect in one fact never refuses the whole name
# --------------------------------------------------------------------------- #

def _entry(end, val, *, accn="a-1", start="2025-01-01"):
    return {"start": start, "end": end, "val": val, "accn": accn, "filed": "2025-05-01",
            "form": "10-Q", "fy": 2025, "fp": "Q1"}


def test_ac_7_103_an_unsupported_currency_fact_is_refused_and_counted_not_the_name():
    """AC-7.103 — ⚠ CRH, ENB, PEP, SLB and MPWR had NO ledger: one EUR/AFN fact refused them."""
    from src.data_engine.src.edgar.companyfacts import extract_facts

    payload = {"facts": {"us-gaap": {"NetIncomeLoss": {"units": {
        "USD": [_entry("2025-03-31", 100)], "EUR": [_entry("2025-03-31", 90)]}}}}}
    result = extract_facts(payload, ticker="CRH")
    assert [(f.unit, f.value_minor) for f in result.facts] == [("USD", 10000)]
    assert any("unsupported currency" in r and "DE-85" in r for r in result.reasons)


def test_ac_7_103_a_conflicting_duplicate_key_keeps_neither_value(tmp_path):
    """AC-7.103 — VST: one 10-K filed 2018-Q4 capex as both $600M and $1,300M."""
    from src.data_engine.ingest.edgar_facts import ingest_facts
    from src.data_engine.pit.ledger import FactLedger

    tag = "PaymentsToAcquireProductiveAssets"
    payload = {"facts": {"us-gaap": {
        tag: {"units": {"USD": [_entry("2025-03-31", 600), _entry("2025-03-31", 1300)]}},
        "NetIncomeLoss": {"units": {"USD": [_entry("2025-03-31", 50)]}}}}}

    class Client:
        def companyfacts(self, cik):
            return payload

    ledger = FactLedger(tmp_path)
    assert ingest_facts(Client(), ledger, ticker="VST", cik="1", tags=(tag, "NetIncomeLoss")) == 1
    assert list(ledger.read("VST")["tag"]) == ["NetIncomeLoss"]


# --------------------------------------------------------------------------- #
# DE-86 (DX-179) — a share count at the wrong scale is not served
# --------------------------------------------------------------------------- #

def test_ac_7_104_a_share_fact_at_the_wrong_scale_is_refused_never_rescaled(tmp_path):
    """AC-7.104 — GRMN filed 193,597 (thousands) beside 192,885,000."""
    from datetime import datetime, timezone

    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.pit.models import QUARTERLY, Fact
    from src.data_engine.pit.snapshot import assemble_rows

    tag, now = "WeightedAverageNumberOfDilutedSharesOutstanding", datetime.now(timezone.utc)

    def fact(end, value, accn, filed):
        return Fact(ticker="GRMN", accession_id=accn, tag=tag,
                    period_start=date(end.year, end.month, 1) - __import__("datetime").timedelta(days=80),
                    period_end=end, period_type=QUARTERLY, value_minor=value, value_currency="",
                    unit="shares", filing_date=filed, ingested_at=now)

    ledger = FactLedger(tmp_path)
    ledger.append([
        fact(date(2024, 3, 30), 192_000_000, "a-1", date(2024, 5, 1)),
        fact(date(2024, 6, 29), 192_500_000, "a-2", date(2024, 8, 1)),
        fact(date(2024, 9, 28), 192_885_000, "a-3", date(2024, 11, 1)),
        fact(date(2024, 9, 28), 193_597, "a-4", date(2025, 2, 20)),       # newer, wrong scale
        fact(date(2024, 12, 28), 193_597, "a-4", date(2025, 2, 20)),      # only a wrong one
    ])
    rows = assemble_rows(ledger.read("GRMN"), date(2025, 3, 1), source="edgar")
    col = f"{tag}_minor"
    by_end = {r.period_end.date(): r for r in rows.itertuples()}
    assert getattr(by_end[date(2024, 9, 28)], col) == 192_885_000        # the right one served
    q4 = by_end.get(date(2024, 12, 28))
    assert q4 is None or (pd.isna(getattr(q4, col)) and "DE-86" in q4.quality_flags)
