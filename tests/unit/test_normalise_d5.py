"""`F10` `D5` — `J-20`'s choice becomes a basis in CODE (`VS-4`).

★ The model chooses a method and a window; these tests pin what the code does
with each, and — above all — that a window with an unusable year REFUSES rather
than averaging around it (measured on Micron: the trough FY2023 has a pretax loss).
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from tests.unit.test_valuation_f10 import AS_OF, TAGS, _row, rows, usd

TAGS["revenue"] = "RevenueFromContractWithCustomerExcludingAssessedTax"
PROV = {"prompt_version": "v1", "run_id": "run-x", "stage_commit_hash": "sha256:a",
        "bundle_hash": "sha256:b"}


def _year(fy: int, *, fcff_major: int, revenue_major: int, pretax=4000, tax=None):
    """One fiscal year whose D6 FCFF is `fcff_major` at t = 0.25:
    OCF = fcff + capex + SBC − interest×0.75. ⚠ A loss year (t = 0, `DX-104`) adds 25."""
    start, end = date(fy - 1, 9, 1), date(fy, 8, 30)
    tax = tax if tax is not None else pretax // 4             # t = 0.25 when pretax > 0
    ocf = fcff_major + 1000 + 100 - 75                         # capex 1000, SBC 100, interest 100×0.75
    row = _row(start, end, date(fy, 10, 20), operating_cash_flow=ocf, interest_expense=100,
               income_tax=tax if pretax > 0 else 10, pretax_income=pretax, capex=1000,
               sbc=100, revenue=revenue_major)
    row["period_type"] = "annual"
    return row


def history(overrides: dict | None = None):
    spec = {2019: (3000, 20000), 2020: (-100, 21000), 2021: (2000, 27000),
            2022: (2800, 30000), 2023: (500, 16000), 2024: (-400, 25000)}
    out = []
    for fy, (fcff, rev) in spec.items():
        out.append(_year(fy, fcff_major=fcff, revenue_major=rev, **(overrides or {}).get(fy, {})))
    return pd.DataFrame(out)


def _quarterly_with_revenue():
    frame = rows()
    frame["RevenueFromContractWithCustomerExcludingAssessedTax_minor"] = 7_000 * 100
    frame["RevenueFromContractWithCustomerExcludingAssessedTax_currency"] = "USD"
    return frame


def _bundle(text="evidence"):
    from src.fundamental.bundle.models import BundlePart, EvidenceBundle
    return EvidenceBundle(ticker="XYZ", as_of=AS_OF,
                          parts=(BundlePart("filing", {"accession_id": "acc"}, text),))


_BUNDLE = _bundle()


def _normalise(choice, annual=None):
    from src.fundamental.valuation.normalise import normalise
    return normalise(choice, quarterly_rows=_quarterly_with_revenue(),
                     annual_rows=history() if annual is None else annual,
                     ticker="XYZ", as_of=AS_OF, provenance=PROV, bundle=_BUNDLE)


CYCLE = {"first_fiscal_year": 2019, "last_fiscal_year": 2024, "trough_year": 2020,
         "peak_year": 2019, "exclusions": [], "what_would_change_it": "x", "why": "y"}


def test_cycle_average_fcff_is_the_mean_of_every_year_in_the_window():
    basis = _normalise({**CYCLE, "method": "cycle_average_fcff"})
    assert basis.origin == "judgement"
    assert basis.base_fcff == usd(3000 - 100 + 2000 + 2800 + 500 - 400).div_int(6)
    assert basis.provenance["window"]["start"] == "FY2019"
    assert basis.provenance["computed_by"].startswith("src.feature_engineer.valuation.normalised:")
    assert basis.provenance["block"] == "J-20" and basis.provenance["exclusions_applied"] is False


def test_cycle_average_margin_applies_the_mean_margin_to_TRAILING_revenue():
    from decimal import Decimal
    basis = _normalise({**CYCLE, "method": "cycle_average_fcff_margin"})
    margins = [Decimal(a) / Decimal(b) for a, b in
               ((3000, 20000), (-100, 21000), (2000, 27000), (2800, 30000), (500, 16000),
                (-400, 25000))]
    mean = sum(margins, Decimal(0)) / 6
    assert basis.provenance["trailing_revenue"] == usd(28000).to_json_obj()  # 4 × 7,000
    assert abs(basis.base_fcff.amount_minor - int(Decimal(2_800_000) * mean)) <= 1


def test_reported_ttm_is_the_D02_basis_marked_as_a_judgement():
    from src.feature_engineer.valuation.basis import reported_basis
    basis = _normalise({**CYCLE, "method": "reported_ttm"})
    assert basis.base_fcff == reported_basis(rows(), as_of=AS_OF, ticker="XYZ").base_fcff
    assert basis.origin == "judgement"


def test_insufficient_evidence_is_no_basis_never_a_default():
    from src.fundamental.valuation.normalise import NoNormalisedBasis
    with pytest.raises(NoNormalisedBasis, match="insufficient_evidence"):
        _normalise({**CYCLE, "method": "insufficient_evidence"})


def test_dx_104_a_LOSS_year_takes_a_zero_tax_rate_and_stays_in_the_window():
    """✏ `DX-104` (Victor, 2026-09-14). ⚠⚠ Measured on Micron: FY2023 (the trough)
    has a pretax loss. It used to refuse the window; now `t = 0`, so interest is added
    back in full: 500 + 100 × 0.25 more than at t = 0.25 ⇒ 525."""
    basis = _normalise({**CYCLE, "method": "cycle_average_fcff"},
                       annual=history({2023: {"pretax": -500}}))
    assert basis.base_fcff == usd(3000 - 100 + 2000 + 2800 + 525 - 400).div_int(6)


def test_a_window_containing_an_UNUSABLE_year_refuses_and_names_it():
    """⚠ A garbled rate on a PROFIT (tax 900 on pretax 400) still refuses — never
    averaged around, which would drop the year silently (`AC-F10.19`, `P5`)."""
    from src.fundamental.valuation.normalise import NoNormalisedBasis
    annual = history({2023: {"pretax": 400, "tax": 900}})
    with pytest.raises(NoNormalisedBasis, match=r"FY2023 \(missing tax_rate"):
        _normalise({**CYCLE, "method": "cycle_average_fcff"}, annual=annual)


@pytest.mark.parametrize(("change", "match"), [
    ({"first_fiscal_year": 2022, "last_fiscal_year": 2024, "trough_year": 2024,
      "peak_year": 2022, "method": "cycle_average_fcff"}, None),          # exactly 3 years — ok
    ({"first_fiscal_year": 2023, "last_fiscal_year": 2024, "method": "cycle_average_fcff"}, "at least 3"),
    ({"first_fiscal_year": 2018, "last_fiscal_year": 2021, "method": "cycle_average_fcff"}, "absent"),
    ({"trough_year": 2025, "method": "cycle_average_fcff"}, "trough_year"),
    ({"first_fiscal_year": 2024, "last_fiscal_year": 2019, "method": "cycle_average_fcff"}, "range"),
    ({"method": "median_of_the_good_years"}, "MP-5"),
])
def test_a_choice_the_history_cannot_support_refuses(change, match):
    from src.fundamental.valuation.normalise import NoNormalisedBasis
    choice = {**CYCLE, **change}
    if match is None:
        assert _normalise(choice).base_fcff == usd(2800 + 500 - 400).div_int(3)   # cents, half-up
        return
    with pytest.raises(NoNormalisedBasis, match=match):
        _normalise(choice)


def test_the_judgement_basis_reaches_fv_analyst_through_the_SAME_mechanics(monkeypatch):
    """★ End to end: J-20's choice → D-01 basis → D-02 `value_on_basis` → fv_analyst."""
    from src.feature_engineer.valuation.assumptions import load_published
    from src.feature_engineer.valuation.service import value_on_basis
    from tests.unit.test_valuation_f10 import FakeEngine

    basis = _normalise({**CYCLE, "method": "cycle_average_fcff"})
    out = value_on_basis("XYZ", AS_OF, basis=basis, engine=FakeEngine(rows()),
                         assumptions=load_published("dcf_two_stage", 1))
    assert out.kind == "fv_analyst" and out.basis.provenance["method"] == "cycle_average_fcff"


def test_the_history_part_is_BLIND_VISIBLE_precomputed_and_shows_unusable_years():
    from src.fundamental.bundle.assemble import annual_history_part
    from src.fundamental.bundle.models import BundlePart, EvidenceBundle

    part = annual_history_part(history({2023: {"pretax": 400, "tax": 900},
                                        2020: {"pretax": -500}}), ticker="XYZ", as_of=AS_OF)
    assert part.kind == "operating_ratios"
    assert "FY2019 |" in part.content and "UNAVAILABLE: missing tax_rate" in part.content
    assert "ok (pretax loss: tax rate 0)" in [ln for ln in part.content.splitlines()
                                              if ln.startswith("FY2020")][0]
    assert "fcff.ocf_plus_after_tax_interest_minus_capex_minus_sbc.v2" in part.content
    assert part.pins["contract_version"] == 2
    assert "Do not add, average or rescale them" in part.content
    filing = BundlePart("filing", {"accession_id": "acc"}, "text")
    blind = EvidenceBundle(ticker="XYZ", as_of=AS_OF, parts=(filing, part)).redact()
    assert part in blind.parts, "J-20 runs blind and must see its history"


def test_ac_f10_19_the_averages_are_D02_functions_and_D01_holds_no_series_arithmetic():
    """AC-F10.19 / `RA-45` — ★ the first build averaged in D-01 and the structural
    guard refused it (`DX-105`). The D-02 function is the one computing; D-01 only
    validates the choice."""
    import pathlib

    from src.feature_engineer.valuation.normalised import WindowUnavailable, cycle_average_fcff

    base, years = cycle_average_fcff(history(), 2019, 2024, ticker="XYZ", as_of=AS_OF)
    assert base == usd(3000 - 100 + 2000 + 2800 + 500 - 400).div_int(6) and len(years) == 6
    with pytest.raises(WindowUnavailable) as exc:
        cycle_average_fcff(history({2023: {"pretax": 400, "tax": 900}}), 2019, 2024,
                           ticker="XYZ", as_of=AS_OF)
    assert exc.value.missing == ["FY2023"]
    src = pathlib.Path("src/fundamental/valuation/normalise.py").read_text()
    for forbidden in ("import pandas", "sum(", "Decimal(", "div_int", "mul_rate", "localcontext"):
        assert forbidden not in src, f"D-01 normaliser holds arithmetic: {forbidden}"


def test_ac_f10_19_a_year_filed_after_as_of_is_absent_and_a_mixed_currency_window_refuses():
    """AC-F10.19 / `INV-1` — ★ both guards survived mutation until this test existed."""
    from src.feature_engineer.valuation.normalised import WindowUnavailable, cycle_average_fcff

    early = date(2024, 9, 1)                       # FY2024's 10-K is filed 2024-10-20
    with pytest.raises(WindowUnavailable) as exc:
        cycle_average_fcff(history(), 2022, 2024, ticker="XYZ", as_of=early)
    assert exc.value.missing == ["FY2024"]
    assert cycle_average_fcff(history(), 2021, 2023, ticker="XYZ", as_of=early)[0] == usd(
        2000 + 2800 + 500).div_int(3)

    frame = history()
    mask = frame["period_end"].map(lambda d: pd.Timestamp(d).year) == 2020
    for col in [c for c in frame.columns if c.endswith("_currency")]:
        frame.loc[mask, col] = "CAD"
    with pytest.raises(WindowUnavailable, match="mixes currencies"):
        cycle_average_fcff(frame, 2019, 2021, ticker="XYZ", as_of=AS_OF)


@pytest.mark.parametrize(("quote", "ok"), [
    ("an impairment  of \u201cgoodwill\u201d", True),      # whitespace + typography only
    ("an impairment of goodwill!", False),                 # a changed character
    ("", False),                                           # no quote at all
])
def test_dx_108_an_exclusion_quote_must_be_in_the_bundle(quote, ok):
    """`DX-108`(1) — X-01's comparison rule; ⚠ an unmatched quote refuses the BASIS."""
    from src.fundamental.valuation.normalise import NoNormalisedBasis, normalise

    choice = {**CYCLE, "method": "cycle_average_fcff",
              "exclusions": [{"item": "impairment", "evidence_id": "e", "quote": quote}]}
    kwargs = dict(quarterly_rows=_quarterly_with_revenue(), annual_rows=history(), ticker="XYZ",
                  as_of=AS_OF, provenance=PROV,
                  bundle=_bundle('Note 4: an impairment of "goodwill" was recorded.'))
    if ok:
        assert normalise(choice, **kwargs).provenance["exclusions"][0]["quote"] == quote
    else:
        with pytest.raises(NoNormalisedBasis, match="not in the bundle"):
            normalise(choice, **kwargs)
