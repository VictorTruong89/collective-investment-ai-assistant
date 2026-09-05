"""D-07 source routing, catalog and operations — AC-7.1…7.6, 7.19…7.34, 7.60.

Tier: unit + contract + integration (constitution §4).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import pandas as pd
import pytest

from src.data_engine.errors import (
    NoCikError, NoFundamentalSourceError, PlanGateRejected, PlanGatedError,
    SourceUnavailableError,
)
from src.data_engine.observation.ledger import ObservationLedger, deny_live_read
from src.data_engine.pit.ledger import FactLedger
from src.data_engine.src.edgar.companyfacts import extract_facts
from src.data_engine.src.edgar.submissions import filer_class, route
from src.data_engine.src.edgar.xbrl import classify_span, discrete_from_cumulative
from src.data_engine.src.fmp.client import FMPClient
from src.data_engine.src.fmp.gates import FORBIDDEN_ENDPOINT_PREFIXES
from src.data_engine.store.atomic import write_json, write_parquet
from src.data_engine.universe import build_entry, load_universe
from src.data_engine.validation import price_rules, run as run_validation
from src.shared.secrets import Secret
from tests_src.data_engine_fixtures import FakeTransport, fact, raw_series

KEY = Secret("FMP_API_KEY", "not-a-real-key")


def client(script, **kw):
    return FMPClient(KEY, FakeTransport(script), sleep=lambda _s: None, **kw)


# --------------------------------------------------------------------------- #
# §5 source routing
# --------------------------------------------------------------------------- #

def test_ac_7_1_a_10k_10q_filer_routes_to_edgar():
    """AC-7.1 — case A. EDGAR facts carry period start AND end (§5.1)."""
    entry = build_entry("MSFT", cik="789019", form_types=["10-K", "10-Q", "8-K"])
    assert entry.source == "edgar" and entry.filer_class == "10-K/10-Q"


def test_ac_7_2_a_20f_6k_filer_routes_to_fmp():
    """AC-7.2 — case B. K-5: ARM files 20-F and 6-K; no 10-K, no 10-Q."""
    entry = build_entry("ARM", cik=None, form_types=["20-F", "6-K", "SC 13G"])
    assert entry.source == "fmp" and entry.filer_class == "20-F/6-K"


def test_ac_7_3_a_cumulative_6k_span_is_not_ingested_as_quarterly():
    """AC-7.3 — ★ the 1.93x / 2.76x / 3.30x regression (§5.2).

    Only Q1 matches, because for Q1 year-to-date IS the quarter. A six-month
    span classified as `cumulative` is the refusal; the discrete value is
    recovered by SUBTRACTION, which is only possible because EDGAR carries both
    dates.
    """
    assert classify_span(date(2025, 4, 1), date(2025, 6, 30)) == "quarterly"
    assert classify_span(date(2025, 4, 1), date(2025, 9, 30)) == "cumulative"
    assert classify_span(date(2025, 4, 1), date(2025, 12, 31)) == "cumulative"

    payload = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        {"start": "2025-04-01", "end": "2025-09-30", "val": 2188e6,
         "accn": "a", "filed": "2025-10-20", "fp": "Q2"},
    ]}}}}}
    result = extract_facts(payload, ticker="ARM")
    assert result.facts == ()
    assert any("cumulative" in why for why in result.reasons), result.reasons

    ytd = {date(2025, 6, 30): 1_053, date(2025, 9, 30): 2_188}
    assert discrete_from_cumulative(ytd, date(2025, 9, 30), date(2025, 6, 30)) == 1_135


def test_ac_7_4_a_universe_ticker_with_no_source_fails_the_run_named():
    """AC-7.4 — DE-13. It is not dropped, and it does not become a row of NaNs.

    The incident: a LEFT JOIN silently dropped 7 of the 13 watchlist tickers and
    they were scored with all 47 fundamental features NaN.
    """
    with pytest.raises(NoFundamentalSourceError, match="MYSTERY"):
        build_entry("MYSTERY", cik=None, form_types=["S-1"])
    with pytest.raises(NoCikError, match="row of NaNs"):
        build_entry("NOCIK", cik=None, form_types=["10-K"])


def test_ac_7_5_edgar_supplies_the_ttm_line_items_where_both_have_a_period():
    """AC-7.5 — §5.3. Decided by filer class ONCE, not per field (DE-5.1).

    A domestic filer that FMP also covers still routes to EDGAR: period start and
    end are explicit, so cumulative-vs-discrete is decidable rather than guessed.
    FMP guessed wrong on MU by 71 %.
    """
    assert route("MU", ["10-K", "10-Q"], has_cik=True) == "edgar"
    assert filer_class(["10-K", "20-F"]) == "10-K/10-Q", "case A wins where both appear"


def test_ac_7_6_source_is_per_ticker_and_stable_across_a_series(tmp_path):
    """AC-7.6 — DE-5.3. A silent mid-history switch looks like a business event."""
    path = tmp_path / "universe.json"
    write_json([{"ticker": "MSFT", "cik": "789019", "form_types": ["10-K", "10-Q"],
                 "watchlist": True},
                {"ticker": "ARM", "cik": None, "form_types": ["20-F", "6-K"]}], path)
    universe = load_universe(path)

    assert universe.tickers == ["ARM", "MSFT"] and universe.watchlist == ["MSFT"]
    universe.assert_source_stable("MSFT", ["edgar", "edgar"])
    with pytest.raises(NoFundamentalSourceError, match="mixes sources"):
        universe.assert_source_stable("MSFT", ["edgar", "fmp"])


# --------------------------------------------------------------------------- #
# §5A the catalog, and the three meanings of 402
# --------------------------------------------------------------------------- #

def test_ac_7_32_a_402_is_retried_before_being_reported():
    """AC-7.32 — DE-15/DE-46, and §5A.2 cause 3 measured live.

    ```
    A 402 IS NOT EVIDENCE OF A PLAN GATE UNTIL IT HAS BEEN RETRIED.
    key-metrics and ratios came back 402 for all three tickers in a 595-call
    run and returned 40 periods each on retry with identical parameters.
    ```
    """
    c = client({"ratios": [(402, "{}"), (200, [{"period": "FY2024"}])]})
    assert c.get("ratios", symbol="MU", period="annual") == [{"period": "FY2024"}]


def test_ac_7_32_a_persistent_402_fails_loud_with_endpoint_and_parameters():
    """AC-7.32 — never converted into an empty result (P5).

    Had ingest treated 402 as "no data", D-02 would have lost every key metric
    and every ratio for the whole universe — and the frame downstream would have
    looked like a clean empty result, not a failure.
    """
    c = client({"key-metrics": [(402, "{}")] * 3})
    with pytest.raises(PlanGatedError) as exc:
        c.get("key-metrics", symbol="MU", period="annual")
    assert "key-metrics" in str(exc.value)
    assert "'symbol': 'MU'" in str(exc.value), "the parameter is half of what was refused"
    assert exc.value.attempts == 3, "the attempt count reaches the manifest (DE-46)"


def test_ac_7_32_the_api_key_never_appears_in_the_error():
    """AC-7.22 + DE-8 — enforced by the Secret wrapper, not by care at each raise."""
    c = client({"key-metrics": [(402, "{}")] * 3})
    with pytest.raises(PlanGatedError) as exc:
        c.get("key-metrics", symbol="MU")
    assert "not-a-real-key" not in str(exc.value)


def test_ac_7_33_a_known_gated_parameter_is_rejected_at_the_client_boundary():
    """AC-7.33 — DE-16, §5A.2 cause 2: the endpoint works and the ARGUMENTS decide.

    The one that bites in production: the same call succeeds in a probe and
    fails later when a `limit` grows or a backfill widens a date range.
    """
    transport = FakeTransport({})
    c = FMPClient(KEY, transport, sleep=lambda _s: None)
    with pytest.raises(PlanGateRejected, match="period=quarter"):
        c.get("ratios", symbol="MU", period="quarter")
    assert transport.calls == [], "rejected at the boundary means never sent"

    with pytest.raises(PlanGateRejected, match="limit"):
        c.get("analyst-estimates", symbol="MU", limit=20)
    with pytest.raises(PlanGateRejected, match="from/to"):
        c.get("news/stock", symbols="MSFT", **{"from": "2026-01-01"})


def test_ac_7_34_quarterly_ratios_are_computed_not_fetched():
    """AC-7.34 — `period=quarter` is 402 on `ratios` and `key-metrics`.

    That is the right answer anyway (AP-5, INV-2), but it is now a REQUIREMENT
    rather than a preference.
    """
    c = client({"ratios": [(200, [])]})
    with pytest.raises(PlanGateRejected, match="COMPUTED from the quarterly statements"):
        c.get("ratios", symbol="MU", period="quarter")


def test_ac_7_31_no_module_ingests_technical_indicators():
    """AC-7.31 — a vendor RSI is a SECOND definition of a feature we own.

    F0 §12 **D-16** is this exact defect, self-inflicted once already. Two
    checks: the client refuses, and no source module names the endpoint.
    """
    import pathlib
    c = client({"technical-indicators/rsi": [(200, [])]})
    with pytest.raises(PlanGateRejected, match="SECOND definition"):
        c.get("technical-indicators/rsi", symbol="MSFT")

    src = pathlib.Path("src/data_engine")
    offenders = [
        p for p in src.rglob("*.py")
        if any(pref in p.read_text() for pref in FORBIDDEN_ENDPOINT_PREFIXES)
        and p.name not in ("gates.py",)
    ]
    assert offenders == [], f"technical-indicators referenced outside the gate list: {offenders}"


def test_a_404_is_an_absence_and_is_never_retried():
    """§5A.3 — a 404 and a 402 are completely different facts."""
    transport = FakeTransport({"social-sentiments": [(404, "{}")] * 3})
    c = FMPClient(KEY, transport, sleep=lambda _s: None)
    with pytest.raises(SourceUnavailableError, match="no FMP sentiment product"):
        c.get("social-sentiments", symbol="MSFT")
    assert transport.calls == [], "a known-absent endpoint is not even attempted"


# --------------------------------------------------------------------------- #
# §5A.4 Class-B observation
# --------------------------------------------------------------------------- #

def test_ac_7_26_class_b_live_read_by_a_pit_consumer_raises(tmp_path):
    """AC-7.26 — DE-6.9. Written per-CONSUMER, because the field cannot decide it.

    Live consensus is genuinely useful on a report today and genuinely poison in
    a training row. Both are true.
    """
    from src.data_engine.errors import LiveReadDeniedError
    for consumer in ("training", "backtest", "inference"):
        with pytest.raises(LiveReadDeniedError, match="no publication axis"):
            deny_live_read("analyst_estimates", consumer)
    deny_live_read("analyst_estimates", "display")          # D-09 is legal


def test_ac_7_27_observed_at_is_ours_and_never_a_vendor_field(tmp_path):
    """AC-7.27 — DE-6.8. It is the only honest timestamp on Class-B data."""
    ledger = ObservationLedger(tmp_path)
    before = datetime.now(timezone.utc)
    ledger.snapshot(ticker="MSFT", field_set="ratios_ttm",
                    payload={"peRatioTTM": 34.1, "date": "FY2027"},
                    source_endpoint="ratios-ttm")
    row = ledger.get(ticker="MSFT", field_set="ratios_ttm")
    assert row["observed_at"] >= before
    assert row["payload"]["date"] == "FY2027", "the vendor's date survives as PAYLOAD only"


def test_ac_7_28_re_snapshotting_unchanged_data_appends_no_row(tmp_path):
    """AC-7.28 — DE-6.10. The ledger's size tracks information, not uptime."""
    ledger = ObservationLedger(tmp_path)
    assert ledger.snapshot(ticker="MSFT", field_set="ratios_ttm", payload={"pe": 34.1},
                           source_endpoint="ratios-ttm") is True
    assert ledger.snapshot(ticker="MSFT", field_set="ratios_ttm", payload={"pe": 34.1},
                           source_endpoint="ratios-ttm") is False
    assert len(ledger.read("ratios_ttm")) == 1


def test_ac_7_29_the_observation_ledger_is_append_only(tmp_path):
    """AC-7.29 — DE-6.7. A changed consensus ADDS a row and modifies none."""
    ledger = ObservationLedger(tmp_path)
    t0 = datetime(2026, 8, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 8, 8, tzinfo=timezone.utc)
    ledger.snapshot(ticker="MSFT", field_set="price_target_consensus",
                    payload={"target": 500}, source_endpoint="ptc", observed_at=t0)
    ledger.snapshot(ticker="MSFT", field_set="price_target_consensus",
                    payload={"target": 520}, source_endpoint="ptc", observed_at=t1)
    df = ledger.read("price_target_consensus")
    assert len(df) == 2
    assert sorted(json.loads(p)["target"] for p in df["payload"]) == [500, 520]


def test_ac_7_30_analyst_estimates_is_read_at_an_as_of_not_by_its_date_field(tmp_path):
    """AC-7.30 — §5A.4's textbook look-ahead.

    ```
    analyst-estimates has a `date` field. It is the FORECAST target period —
    FY2027 — not the day the estimate was made. Joining it to a 2024 training
    row gives the model a 2026 opinion about 2027.
    ```
    """
    from src.data_engine.errors import AsOfRequiredError
    ledger = ObservationLedger(tmp_path)
    ledger.snapshot(ticker="MSFT", field_set="analyst_estimates",
                    payload={"date": "2027-06-30", "revenueAvg": 3.2e11},
                    source_endpoint="analyst-estimates",
                    observed_at=datetime(2026, 8, 1, tzinfo=timezone.utc))

    with pytest.raises(AsOfRequiredError):
        ledger.get(ticker="MSFT", field_set="analyst_estimates", consumer="training")

    assert ledger.get(ticker="MSFT", field_set="analyst_estimates",
                      as_of=date(2026, 7, 1), consumer="training") is None
    assert ledger.get(ticker="MSFT", field_set="analyst_estimates",
                      as_of=date(2026, 8, 2), consumer="training") is not None


# --------------------------------------------------------------------------- #
# Operational
# --------------------------------------------------------------------------- #

def test_ac_7_19_re_running_ingest_produces_identical_files(tmp_path):
    """AC-7.19 — DE-11 idempotence, byte-for-byte."""
    a, b = tmp_path / "a.parquet", tmp_path / "b.parquet"
    df = raw_series().sort_values("date").reset_index(drop=True)
    write_parquet(df, a)
    write_parquet(df, b)
    assert a.read_bytes() == b.read_bytes()


def test_ac_7_20_a_killed_write_leaves_no_readable_partial_file(tmp_path):
    """AC-7.20 — DE-10. Atomicity is the one property a database gave for free."""
    from src.data_engine.errors import StoreWriteError

    class Exploding(pd.DataFrame):
        def to_parquet(self, *a, **kw):
            raise OSError("disk full mid-write")

    target = tmp_path / "panel.parquet"
    with pytest.raises(StoreWriteError, match="No partial file remains"):
        write_parquet(Exploding(raw_series()), target)
    assert not target.exists()
    assert list(tmp_path.glob("*.tmp")) == [], "the temp file is cleaned up too"


def test_ac_7_21_edgar_requests_carry_a_contactable_user_agent_and_are_throttled():
    """AC-7.21 — DE-9. Being blocked by SEC is a self-inflicted outage."""
    from src.data_engine.src.edgar.client import RATE_LIMIT_PER_SEC, EdgarClient

    seen, slept = [], []

    class Recorder:
        def get(self, url, params, headers, timeout):
            seen.append(headers["User-Agent"])
            return 200, "{}"

    email = Secret("EDGAR_CONTACT", "victor@example.com")
    c = EdgarClient(email, Recorder(), sleep=slept.append, clock=lambda: 0.0)
    for _ in range(RATE_LIMIT_PER_SEC + 1):
        c.submissions("789019")
    assert all("contact:" in ua for ua in seen)
    assert slept, "the in-process throttle actually sleeps at the cap"


def test_ac_7_22_no_key_or_contact_email_appears_in_an_error():
    """AC-7.22 — DE-8, for BOTH secrets. The email is a real person's address."""
    from src.data_engine.src.edgar.client import EdgarClient

    class Failing:
        def get(self, url, params, headers, timeout):
            return 403, "blocked"

    email = Secret("EDGAR_CONTACT", "victor@example.com")
    c = EdgarClient(email, Failing(), sleep=lambda _s: None)
    with pytest.raises(SourceUnavailableError) as exc:
        c.companyfacts("789019")
    assert "victor@example.com" not in str(exc.value)
    assert "victor@example.com" not in repr(email)

    with pytest.raises(TypeError, match="must be a Secret"):
        EdgarClient("victor@example.com")


def test_ac_7_23_the_cache_is_keyed_by_accession_not_by_elapsed_time():
    """AC-7.23 — CT-7.4. A filing is immutable once published; a TTL is meaningless.

    The Fact ledger IS the filing-aware cache in this tree: it is keyed on
    `accession_id`, and a re-append of the same accession is a no-op regardless
    of how much time has passed.
    """
    from src.data_engine.contracts.ledgers import FACT_LEDGER
    assert "accession_id" in FACT_LEDGER.key
    assert not any("ttl" in c.name or "expires" in c.name for c in FACT_LEDGER.columns)


def test_ac_7_23_a_new_filing_invalidates_by_appearing(tmp_path):
    """AC-7.23 — invalidation is a NEW accession arriving, not a clock."""
    ledger = FactLedger(tmp_path)
    ledger.append([fact(accession="0000-1")])
    assert ledger.append([fact(accession="0000-1")]) == 0
    assert ledger.append([fact(accession="0000-2", value=9, filed=date(2024, 10, 1))]) == 1


def test_ac_7_24_no_module_in_data_engine_imports_the_llm_gateway():
    """AC-7.24 — ST-5/AP-5. D-07 never calls a model.

    Also covered by the CI import rules (`tests_src/test_architecture.py`); named
    here so D-07's own AC has a test of its own (constitution §6).
    """
    from tests_src.architecture import scan, st_5
    assert st_5(scan()) == []


def test_ac_7_25_missing_values_are_null_with_no_zero_filling():
    """AC-7.25 — DE-14. A zero revenue and an unknown revenue are different facts."""
    payload = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        {"start": "2024-01-01", "end": "2024-03-31", "val": None,
         "accn": "a", "filed": "2024-04-25", "fp": "Q1"},
    ]}}}}}
    result = extract_facts(payload, ticker="MSFT")
    assert result.facts == ()
    assert any("not stored as zero" in why for why in result.reasons)


def test_ac_7_60_validation_classifies_and_never_modifies():
    """AC-7.60 — DE-12. A FLAG is stored WITH the row; a REJECT is not stored.

    ★ The "never modifies" half is the load-bearing half. Clipping an
    out-of-range value is one line and looks like robustness; it is the same
    move as `fillna(0.0)` on a z-score (PD-1).
    """
    df = raw_series()
    df.loc[0, "volume"] = 0                    # DQ-005, FLAG
    df.loc[2, "close_minor"] = -1              # DQ-001, REJECT
    original = df.copy()

    result = run_validation(df, price_rules())

    # The input frame is untouched — DE-12's "never modifies", asserted directly
    # rather than inferred from the outputs.
    pd.testing.assert_frame_equal(df, original)
    assert result.verdict == "REJECT"
    assert len(result.rejected) == 1 and int(result.rejected.iloc[0]["close_minor"]) == -1
    assert "DQ-005" in result.accepted.iloc[0]["quality_flags"]
    assert int(result.accepted.iloc[0]["volume"]) == 0, "the flagged value is NOT repaired"
    assert set(result.findings["rule_id"]) >= {"DQ-001", "DQ-005"}
