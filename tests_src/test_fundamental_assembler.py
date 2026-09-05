"""D-01 §5 — `ticker + as_of` → `EvidenceBundle`, from real D-07/D-02 reads."""
from datetime import date

import pandas as pd
import pytest

from src.fundamental.bundle.for_ticker import (
    D01_CONSUMER, PROFILE_ANCHORS_STRIPPED, PROFILE_FIELDS, bundle_for,
    observable_fields,
)
from src.fundamental.errors import BundleInconsistentError

AS_OF = date(2026, 8, 25)


def _rows(**over):
    base = {
        "ticker": ["NVDA", "NVDA"],
        "period_end": [date(2025, 4, 27), date(2026, 4, 26)],
        "period_type": ["quarterly", "quarterly"],
        "filing_date": [date(2026, 5, 20), date(2026, 5, 20)],
        "accession_id": ["0001045810-26-000052", "0001045810-26-000052"],
        "source": ["edgar", "edgar"],
        "restated": [False, False],
        "Revenues_minor": [4406200000000, 8161500000000],
        "Revenues_currency": ["USD", "USD"],
    }
    base.update(over)
    return pd.DataFrame(base)


class _Engine:
    def __init__(self, rows=None, observation=None, raises=False):
        self._rows = _rows() if rows is None else rows
        self._observation = observation
        self._raises = raises

    def get_fundamentals(self, ticker, as_of=None):
        return self._rows

    def get_observation(self, ticker, field_set, as_of=None, consumer=None):
        if self._raises:
            raise RuntimeError("live read denied")
        self.seen_consumer = consumer
        return self._observation


def test_ac_1_x_the_newest_period_wins_not_the_newest_filing():
    """★★ RA-3 — ⚠ *one EDGAR filing reports its own quarter AND the prior-year
    comparative*, so ordering by `filing_date` put a year-stale period last and
    a model would read it as current."""
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=_Engine(), periods=1)
    body = next(p for p in bundle.parts if p.kind == "filing").content
    assert "2026-04-26" in body
    assert "2025-04-27" not in body, "the comparative is not the current period"


def test_ac_1_x_a_period_with_no_line_items_is_not_carried():
    """RA-19 — ★ not curation: a period with no reported figure offers nothing
    to reason about, and it would push a period that has figures out."""
    rows = _rows(Revenues_minor=[None, 8161500000000])
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=_Engine(rows), periods=4)
    body = next(p for p in bundle.parts if p.kind == "filing").content
    assert "2025-04-27" not in body and "2026-04-26" in body


def test_ac_1_x_an_unpinnable_filing_refuses_rather_than_substituting_a_date():
    """RA-2 — ⚠ *two runs with the same `bundle_hash` are comparable*; a pin
    that is `None` for an unknowable subset makes that claim untrue."""
    rows = _rows(accession_id=[None, None])
    with pytest.raises(BundleInconsistentError, match="accession_id"):
        bundle_for("NVDA", as_of=AS_OF, engine=_Engine(rows))


def test_ac_1_x_no_fundamentals_raises_rather_than_authoring_on_nothing():
    """P5 / RA-1 — a thesis on an empty evidence set reads as a judgement about
    a company rather than as the absence of one."""
    with pytest.raises(BundleInconsistentError, match="no fundamentals"):
        bundle_for("NVDA", as_of=AS_OF, engine=_Engine(_rows().iloc[0:0]))


def test_ac_1_x_the_profile_part_never_carries_a_price_anchor():
    """★★ RA-14 — **the defect this allowlist exists for.** `profile` is NOT in
    `BLIND_WITHHELD_KINDS`, so it reaches J-11 and J-15 — exactly the passes
    that must run with price, market cap and valuation withheld."""
    vendor = {"companyName": "NVIDIA Corporation", "sector": "Information Technology",
              "price": 210.3, "marketCap": 5093676373917, "beta": 2.215,
              "range": "164.07-236.54", "lastDividend": 0.28}
    bundle = bundle_for("NVDA", as_of=AS_OF,
                        engine=_Engine(observation=vendor))
    body = next(p for p in bundle.parts if p.kind == "profile").content
    assert "NVIDIA Corporation" in body and "Information Technology" in body
    for anchor in PROFILE_ANCHORS_STRIPPED:
        assert anchor not in body, f"{anchor} is an anchor RA-14 withholds"
    assert "210.3" not in body and "5093676373917" not in body


def test_ac_1_x_an_unknown_vendor_field_is_not_carried():
    """★ The allowlist's whole point: ⚠ a denylist leaks whatever the vendor
    adds next, and it would arrive silently on the blind view."""
    vendor = {"companyName": "NVIDIA", "impliedVolatility": 0.42}
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=_Engine(observation=vendor))
    body = next(p for p in bundle.parts if p.kind == "profile").content
    assert "impliedVolatility" not in body and "0.42" not in body


def test_ac_1_x_d01_is_not_a_pit_consumer():
    """★ DE-6.9 — ⚠ `profile` is Class-B and `PIT_CONSUMERS` is
    `{training, backtest, inference}`: authoring under any of those raises
    `LiveReadDeniedError` and **no thesis could ever be written**."""
    from src.data_engine.contracts.ledgers import CLASS_B_FIELD_SETS, PIT_CONSUMERS

    assert "profile" in CLASS_B_FIELD_SETS
    assert D01_CONSUMER not in PIT_CONSUMERS

    engine = _Engine(observation={"companyName": "NVIDIA"})
    bundle_for("NVDA", as_of=AS_OF, engine=engine)
    assert engine.seen_consumer == D01_CONSUMER


def test_ac_1_x_an_absent_profile_weakens_the_bundle_but_does_not_void_it():
    """⚠ Contrast the filing part, whose absence does. A profile is context."""
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=_Engine(raises=True))
    assert [p.kind for p in bundle.parts] == ["filing", "observables"]


def test_ac_1_x_observables_include_fundamental_tags_not_just_features():
    """★★ RA-35 / RA-145 — ⚠ **`b3_minimal` is D-02's only published contract
    and it carries no ratios**, so without the statement tags a *fundamental*
    thesis could be falsified only by momentum and volatility."""
    fields = observable_fields(_Engine(), "NVDA", AS_OF, None)
    assert "Revenues" in fields
    assert all(f.islower() or f[0].isupper() for f in fields)


def test_ac_1_x_the_observable_list_reaches_the_blind_view():
    """RA-146 — ★ it began life as a `computed` part and the blind view stripped
    it, so J-15 was told to choose from a list it was never shown."""
    from src.fundamental.bundle.models import BLIND_WITHHELD_KINDS

    assert "observables" not in BLIND_WITHHELD_KINDS
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=_Engine())
    blind = bundle.redact()
    assert any(p.kind == "observables" for p in blind.parts)


def test_ac_1_x_assembly_is_deterministic():
    """RA-4 / INV-2 — same `as_of` ⇒ same bundle ⇒ same hash."""
    one = bundle_for("NVDA", as_of=AS_OF, engine=_Engine())
    two = bundle_for("NVDA", as_of=AS_OF, engine=_Engine())
    assert one.bundle_hash == two.bundle_hash


def test_ac_1_x_the_allowlist_and_the_stripped_list_do_not_overlap():
    """★ A field in both would mean the strip list is decorative."""
    assert not set(PROFILE_FIELDS) & set(PROFILE_ANCHORS_STRIPPED)


# --------------------------------------------------------------------------- #
# RA-14 — the anchor boundary, now that Class-B ratios reach the bundle
# --------------------------------------------------------------------------- #

RATIOS = {
    "grossProfitMarginTTM": 0.7467, "ebitMarginTTM": 0.759,
    "debtToEquityRatioTTM": 0.1697, "currentRatioTTM": 4.589,
    # ⚠ price-derived, in the SAME vendor payload
    "priceToEarningsRatioTTM": 41.2, "priceToBookRatioTTM": 52.9,
    "enterpriseValueTTM": 5.09e12, "dividendYieldTTM": 0.0005,
}


class _ClassBEngine(_Engine):
    def __init__(self, by_field_set):
        super().__init__()
        self._by_field_set = by_field_set

    def get_observation(self, ticker, field_set, as_of=None, consumer=None):
        payload = self._by_field_set.get(field_set)
        if payload is None:
            raise RuntimeError("nothing observed")
        # ★ The ledger returns an ENVELOPE, not the payload.
        return {"ticker": ticker, "field_set": field_set,
                "payload": payload, "content_hash": "x"}


def _blind_text(engine):
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=engine)
    return "\n".join(p.content for p in bundle.redact().parts)


def test_ac_1_x_a_price_derived_ratio_never_reaches_the_blind_view():
    """★★ RA-14 — ⚠ **26 of `ratios-ttm`'s 62 keys are price-derived.** Handing
    the set over whole leaks the anchor through `priceToEarningsRatioTTM` alone:
    a reader with EPS and a P/E has the price, and RA-14 is defeated **without a
    single price field appearing**."""
    text = _blind_text(_ClassBEngine({"ratios_ttm": RATIOS}))
    assert "grossProfitMargin" in text, "an operating margin is the point"
    for anchor in ("priceToEarnings", "priceToBook", "enterpriseValue",
                   "dividendYield", "41.2", "52.9"):
        assert anchor not in text, f"{anchor} is an anchor RA-14 withholds"


def test_ac_1_x_an_unknown_ratio_defaults_to_withheld():
    """★ **The default must be withheld, not shown.** Wrongly withholding a
    quality metric costs a thinner bundle; wrongly exposing a multiple costs
    RA-14 — so a vendor's next new key is invisible until it is enumerated."""
    engine = _ClassBEngine({"ratios_ttm": dict(
        RATIOS, someNewMultipleTTM=12.5)})
    assert "someNewMultiple" not in _blind_text(engine)


def test_ac_1_x_the_ratio_allowlist_is_enumerated_not_inferred():
    """⚠ A substring probe for `ev` classified `financialLeverageRatioTTM` as
    enterprise-value-derived. ★ **Names are enumerated because a heuristic over
    vendor field names silently misclassifies in both directions.**"""
    from src.fundamental.bundle.for_ticker import OPERATING_RATIOS

    assert not [r for r in OPERATING_RATIOS
                if "price" in r.lower() or "enterpriseValue" in r]


def test_ac_1_x_valuation_field_sets_land_in_the_withheld_kind():
    """★ `BLIND_WITHHELD_KINDS = ("computed",)`, so a multiple placed there is
    invisible to J-11 and J-15 and revealed only at reconciliation."""
    engine = _ClassBEngine({"key_metrics_ttm": {"evToEBITDATTM": 38.4}})
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=engine)
    assert any(p.kind == "computed" for p in bundle.parts)
    assert "evToEBITDA" not in "\n".join(p.content for p in bundle.redact().parts)


def test_ac_1_x_the_ledger_envelope_is_unwrapped():
    """⚠ `ObservationLedger.get()` returns `{ticker, field_set, observed_at,
    payload, …}`. ★ Reading the envelope as the payload finds no allowlisted key
    and the part vanishes **exactly as if nothing had been captured** — a silent
    miss with data on disk."""
    engine = _ClassBEngine({"profile": {"companyName": "NVIDIA Corporation",
                                        "sector": "Information Technology"}})
    bundle = bundle_for("NVDA", as_of=AS_OF, engine=engine)
    body = next(p for p in bundle.parts if p.kind == "profile").content
    assert "NVIDIA Corporation" in body
