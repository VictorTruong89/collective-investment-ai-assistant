"""D-07 — EDGAR companyfacts into the fact ledger. ★ The write nothing did."""
from datetime import date

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

    assert len(_collapse_identical([_F(100), _F(100)])) == 1


def test_ac_7_68_a_value_conflict_on_one_key_still_reaches_ct_7_3():
    """★★ DE-51 — ⚠ *deduplicating by "keep the first" picks a reported figure
    by ARRIVAL ORDER*, which is the silent choice P5 exists to prevent."""
    from src.data_engine.ingest.edgar_facts import _collapse_identical

    class _F:
        def __init__(self, value):
            self.ticker, self.accession_id, self.tag = "WMT", "a-1", "Revenues"
            self.period_start, self.period_end, self.period_type = 1, 2, "quarterly"
            self.value_minor, self.value_currency = value, "USD"

    assert len(_collapse_identical([_F(100), _F(101)])) == 2


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
