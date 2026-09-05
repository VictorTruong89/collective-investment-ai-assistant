"""D-02 — AC-2.1…2.14, 2.19…2.25, 2.30 (the contract, PIT, missingness, INV-014).

Tier: data contract + invariant/property (constitution §4).
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.data_engine import build_price_panel
from src.data_engine.contracts.envelopes import BLOCK, CalendarCheckReport, Finding
from src.feature_engineer import (
    AnalystDerivedInputError, AsOfRequiredError, B3_MINIMAL_V1, BUILDERS,
    CalendarHaltError, ContractMutatedError, ContractRegistry, ContractUnknownError,
    DuplicateDefinitionError, FeatureContract, FeatureSpec, LabelInContractError,
    MissingFeatureError, RangeViolationError, UndeclaredColumnError, build_panel,
    coverage, validate_panel,
)
from src.feature_engineer.technical.momentum import mom_21, vol_21
from tests_src.data_engine_fixtures import raw_series, split

AS_OF = date(2024, 6, 11)


def clean_report(verdict_findings=()):
    from src.data_engine.calendar.classes import CHECKED, EVENT_CLASSES
    return CalendarCheckReport(
        run_id="run-1", as_of=AS_OF, adj_as_of=AS_OF,
        window_start=date(2024, 1, 1), window_end=date(2024, 12, 31),
        universe_size=1,
        class_status={c.name: CHECKED for c in EVENT_CLASSES},
        findings=tuple(verdict_findings),
    )


def price_panel(n=30, ticker="NVDA"):
    rows = [(date(2024, 5, 1) + pd.Timedelta(days=i).to_pytimedelta(),
             10000 + 50 * i, 10200 + 50 * i, 9900 + 50 * i, 10100 + 50 * i,
             1_000_000 + i) for i in range(n)]
    return build_price_panel(raw_series(ticker, rows), [], None)


def spec(**kw):
    base = dict(name="mom_21", formula_id="momentum.open_to_open_ratio.v1",
                dtype="float64", inputs=("price.adj_open",),
                owner_module="technical.momentum")
    return FeatureSpec(**{**base, **kw})


# --------------------------------------------------------------------------- #
# §5 — the contract
# --------------------------------------------------------------------------- #

def test_ac_2_1_a_column_with_no_featurespec_fails_validation():
    """AC-2.1 — FE-1. An unspecified column is a defect, not a bonus feature."""
    panel = build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(),
                        calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    panel["surprise"] = 1.0
    with pytest.raises(UndeclaredColumnError, match="surprise"):
        validate_panel(panel, B3_MINIMAL_V1)


def test_ac_2_2_a_declared_feature_absent_from_the_panel_fails():
    """AC-2.2 — ★ **checked, not filtered** (PD-18).

    `model_bundle.py:80`'s `[c for c in feature_names if c in df.columns]` is one
    word from correct, and that word is the whole of D-17.
    """
    panel = build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(),
                        calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    with pytest.raises(MissingFeatureError, match="vol_21"):
        validate_panel(panel.drop(columns=["vol_21"]), B3_MINIMAL_V1)


def test_ac_2_3_republishing_a_version_with_different_content_raises():
    """AC-2.3 — FE-2. ★ A version that can mean two things is not a referent."""
    reg = ContractRegistry()
    reg.publish(B3_MINIMAL_V1)
    reg.publish(B3_MINIMAL_V1)                       # idempotent, identical content
    mutated = FeatureContract(name=B3_MINIMAL_V1.name, version=B3_MINIMAL_V1.version,
                              features=(spec(formula_id="momentum.wilder.v9"),))
    with pytest.raises(ContractMutatedError, match="immutable"):
        reg.publish(mutated)
    with pytest.raises(ContractUnknownError):
        reg.get("b3_minimal", 99)


def test_ac_2_4_every_panel_records_contract_name_and_version():
    """AC-2.4 — FE-3. A panel that cannot name its contract cannot be parity-checked."""
    panel = build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(),
                        calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    assert set(panel["contract_name"]) == {"b3_minimal"}
    assert set(panel["contract_version"]) == {1}
    assert set(panel["calendar_check_id"]) == {clean_report().report_id}


def test_ac_2_5_a_value_outside_its_declared_range_raises():
    """AC-2.5 — FE-5 / INV-3. Enforced at emit, not documented."""
    panel = build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(),
                        calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    panel.loc[panel.index[-1], "vol_21"] = 99.0        # declared range is [0, 5]
    with pytest.raises(RangeViolationError, match="vol_21"):
        validate_panel(panel, B3_MINIMAL_V1)


def test_ac_2_6_changing_a_formula_changes_the_content_hash():
    """AC-2.6 — FE-2's mechanism: immutability is checked on CONTENT, not trust."""
    a = FeatureContract("x", 1, (spec(),))
    b = FeatureContract("x", 1, (spec(formula_id="momentum.other.v1"),))
    assert a.content_hash != b.content_hash


def test_ac_2_7_a_deprecated_features_spec_still_resolves():
    """AC-2.7 — FE-6. Deprecation is by TOMBSTONE, so an old model's contract resolves."""
    contract = FeatureContract("x", 2, (spec(), spec(name="old_mom", deprecated_in=2)))
    assert contract.feature_names == ("mom_21",), "tombstones are not live features"
    assert contract.spec("old_mom").deprecated_in == 2


def test_ac_2_25_two_modules_computing_one_formula_id_raises():
    """AC-2.25 — FE-4/FE-25, the defect this domain exists to remove.

    `moat_score` (0-10, blended with an LLM read) and `f_moat_quant_score` (0-1,
    panel-native) are two computations of one concept and **nothing says so**.
    """
    with pytest.raises(DuplicateDefinitionError, match="one owning module"):
        FeatureContract("x", 1, (spec(), spec(name="mom_dup",
                                              owner_module="technical.other")))


# --------------------------------------------------------------------------- #
# §7 — point-in-time and determinism
# --------------------------------------------------------------------------- #

def test_ac_2_8_omitting_as_of_or_adj_as_of_raises():
    """AC-2.8 — FE-7/FE-8, both axes, no default.

    They fail differently: a defaulted `as_of` is INV-1 look-ahead; a defaulted
    `adj_as_of` is INV-2 irreproducibility.
    """
    kw = dict(contract=B3_MINIMAL_V1, price_panel=price_panel(),
              calendar_report=clean_report())
    with pytest.raises(AsOfRequiredError, match="as_of"):
        build_panel(**kw, adj_as_of=None)
    with pytest.raises(AsOfRequiredError, match="adj_as_of"):
        build_panel(**kw, as_of=AS_OF)


def test_ac_2_9_same_inputs_give_byte_identical_output():
    """AC-2.9 — INV-2 (FE-16)."""
    kw = dict(contract=B3_MINIMAL_V1, price_panel=price_panel(),
              calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    pd.testing.assert_frame_equal(build_panel(**kw), build_panel(**kw))


def test_ac_2_10_two_panels_with_different_adj_as_of_are_not_equal():
    """AC-2.10 — FE-8 / DE-30. The two panels are different DATA, not two views."""
    from src.data_engine import build_price_panel
    raw, events = raw_series(), [split()]
    early = build_panel(contract=B3_MINIMAL_V1,
                        price_panel=build_price_panel(raw, events, date(2024, 6, 1)),
                        calendar_report=clean_report(), as_of=AS_OF,
                        adj_as_of=date(2024, 6, 1))
    late = build_panel(contract=B3_MINIMAL_V1,
                       price_panel=build_price_panel(raw, events, date(2024, 8, 1)),
                       calendar_report=clean_report(), as_of=AS_OF,
                       adj_as_of=date(2024, 8, 1))
    assert not early["adj_as_of"].equals(late["adj_as_of"])


def test_ac_2_12_a_calendar_halt_propagates_and_no_panel_is_built():
    """AC-2.12 — FE-10. ★ D-02 never computes "around" a blocking corporate action."""
    halted = CalendarCheckReport(
        run_id="r", as_of=AS_OF, adj_as_of=AS_OF,
        window_start=date(2024, 1, 1), window_end=date(2024, 12, 31), universe_size=1,
        class_status=clean_report().class_status,
        findings=(Finding("NVDA", "split", BLOCK, date(2024, 6, 10),
                          date(2024, 5, 22), {}, "fmp"),),
    )
    assert halted.verdict == "HALT"
    with pytest.raises(CalendarHaltError, match="NVDA"):
        build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(),
                    calendar_report=halted, as_of=AS_OF, adj_as_of=None)
    with pytest.raises(CalendarHaltError, match="no calendar check"):
        build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(),
                    calendar_report=None, as_of=AS_OF, adj_as_of=None)


# --------------------------------------------------------------------------- #
# §7.4 / §7.5 — labels and missingness
# --------------------------------------------------------------------------- #

def test_ac_2_14_a_label_in_a_featurecontract_raises():
    """AC-2.14 — FE-11. ★ *One module is allowed to see the future and it is not
    the one models take inputs from.*"""
    for name in ("fwd_ret_21", "label_up", "target_return", "ret_5d_ahead"):
        with pytest.raises(LabelInContractError):
            spec(name=name)


def test_ac_2_19_missing_is_null_with_no_zero_filling():
    """AC-2.19 — FE-14. ★ *A zero margin and an unknown margin are different facts.*"""
    panel = build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(n=25),
                        calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    head = panel.head(21)
    assert head["mom_21"].isna().all(), "insufficient history is NaN, never 0.0"
    assert (panel["mom_21"] == 0.0).sum() == 0


def test_ac_2_20_coverage_counts_nan_but_present_as_missing():
    """AC-2.20 — CT-2.4, the half a column-name check is structurally blind to (D-17).

    ⚠ A name can be *in* the panel with every column present and every value
    NaN, and nothing in a column-name check will notice.
    """
    panel = build_panel(contract=B3_MINIMAL_V1, price_panel=price_panel(n=25),
                        calendar_report=clean_report(), as_of=AS_OF, adj_as_of=None)
    full = coverage(panel, B3_MINIMAL_V1)["NVDA"]
    assert full["coverage_fraction"] == 1.0

    blanked = panel.copy()
    blanked["vol_21"] = pd.NA
    thin = coverage(blanked, B3_MINIMAL_V1)["NVDA"]
    assert thin["features_usable"] == 1 and thin["missing"] == ["vol_21"]
    assert thin["coverage_fraction"] == 0.5


# --------------------------------------------------------------------------- #
# INV-014
# --------------------------------------------------------------------------- #

def test_ac_2_22_a_featurespec_input_from_an_analytical_domain_raises():
    """AC-2.22 — FE-21. ★ *The determinism is in the transport, not the source.*"""
    for bad in ("thesis.verdict", "rank.score", "profile.moat_type", "risk.beta"):
        with pytest.raises(AnalystDerivedInputError, match="analytical domain"):
            spec(inputs=(bad,))


def test_ac_2_23_and_2_24_no_gateway_and_no_analytical_import():
    """AC-2.23 / AC-2.24 — ST-5 and FE-21, grep-checkable in CI."""
    from tests_src.architecture import fe_21, scan, st_5
    graph = scan()
    assert st_5(graph) == []
    assert fe_21(graph) == []


# --------------------------------------------------------------------------- #
# The feature itself
# --------------------------------------------------------------------------- #

def test_method_known_answer_mom_21():
    """CT-3.3's known-answer test for `momentum.open_to_open_ratio.v1` (AC-3.16)."""
    rows = [(date(2024, 1, 1) + pd.Timedelta(days=i).to_pytimedelta(),
             10000, 10000, 10000, 10000, 1) for i in range(21)]
    rows.append((date(2024, 1, 22), 11000, 11000, 11000, 11000, 1))
    # Through the real derivation: `adj_open_minor` is CT-7.1's, and at
    # adj_as_of=None it equals the raw open (DE-45).
    out = mom_21(build_price_panel(raw_series("X", rows), [], None))
    assert float(out.iloc[-1]) == pytest.approx(0.10, abs=1e-12)
    assert out.head(21).isna().all(), "fewer than 22 rows is NaN, never 0.0"


def test_method_known_answer_vol_21_constant_growth_is_exactly_zero():
    """CT-3.3's known-answer test for `volatility.realised_open_to_open_std.v1`.

    A constant-growth series has identical log returns every day, so its sd is
    **exactly 0.0** — a measured zero, not a missing one.
    """
    rows = [(date(2024, 1, 1) + pd.Timedelta(days=i).to_pytimedelta(),
             10000 * 2 ** i, 10000 * 2 ** i, 10000 * 2 ** i, 10000 * 2 ** i, 1)
            for i in range(25)]
    out = vol_21(build_price_panel(raw_series("X", rows), [], None))
    assert float(out.iloc[-1]) == pytest.approx(0.0, abs=1e-12)
    assert out.head(21).isna().all(), "min_periods — PD-9"


def test_mom_21_refuses_a_cross_currency_ratio():
    """FE-32 — a ratio only means something within one currency."""
    df = build_price_panel(raw_series("X"), [], None)
    df["adj_open_currency"] = ["USD", "CAD", "USD", "USD"]
    with pytest.raises(ValueError, match="currencies"):
        mom_21(df)


def test_every_declared_feature_has_a_builder():
    """FE-1 runs both ways: a spec with no implementation is as broken as the reverse."""
    assert set(B3_MINIMAL_V1.feature_names) <= set(BUILDERS)
