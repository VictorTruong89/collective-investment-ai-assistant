"""F5 — the metric contract and the metrics themselves. `MS-4`."""

from __future__ import annotations

import pytest

from src.evaluation.golden.models import CircularGoldenValue, GoldenCase
from src.evaluation.metrics.calibration import (
    Prediction,
    calibrate,
    evidence_coverage,
)
from src.evaluation.metrics.faithfulness import deletion_curve
from src.evaluation.metrics.grounding import Claim, grounding_rate
from src.evaluation.metrics.models import (
    MetricResult,
    insufficient,
    measured,
    minimum_for,
)


# --------------------------------------------------------------------------- #
# AC-5.2 / AC-5.3 — n and selection_count travel with the figure
# --------------------------------------------------------------------------- #
def test_ac_5_2_a_figure_without_n_cannot_be_built():
    with pytest.raises(ValueError, match="n is never optional"):
        MetricResult(metric="ece", n=-1, tier="B", inputs_ref="x", value=0.1)


def test_ac_5_2_value_and_insufficiency_are_mutually_exclusive():
    with pytest.raises(ValueError, match="exactly one"):
        MetricResult(metric="ece", n=5, tier="B", inputs_ref="x",
                     value=0.1, insufficient_reason="too few")
    with pytest.raises(ValueError, match="exactly one"):
        MetricResult(metric="ece", n=5, tier="B", inputs_ref="x")


def test_ac_5_3_selection_count_travels_with_the_figure():
    """QR-19 — a significance figure with an unstated selection count is not
    interpretable. Generalised here to every metric."""
    r = measured("grounding_rate", 0.9, 40, "A", "run-1", selection_count=7)
    assert r.to_json_obj()["selection_count"] == 7


def test_ac_5_3_selection_count_starts_at_one():
    with pytest.raises(ValueError, match="starts at 1"):
        measured("grounding_rate", 0.9, 40, "A", "run-1", selection_count=0)


def test_ac_5_4_tier_must_be_declared_and_valid():
    """PG-5.1 — a result that cannot say which tier it is cannot be placed."""
    with pytest.raises(ValueError, match="tier must be A or B"):
        MetricResult(metric="ece", n=60, tier="C", inputs_ref="x", value=0.1)


# --------------------------------------------------------------------------- #
# AC-5.10 / D3 — admitted floors
# --------------------------------------------------------------------------- #
def test_ac_5_10_below_the_floor_returns_an_insufficiency_not_a_number():
    r = measured("ece", 0.04, n=12, tier="B", inputs_ref="run-1")
    assert r.value is None
    assert "at least 50" in r.insufficient_reason and "got 12" in r.insufficient_reason
    assert "admitted floor" in r.insufficient_reason


def test_ac_5_10_the_floor_is_per_metric_not_global():
    """D3 — ECE with 5 bins needs a different n from a grounding rate."""
    assert minimum_for("ece") != minimum_for("grounding_rate")
    assert measured("grounding_rate", 0.9, n=25, tier="A", inputs_ref="r").is_sufficient
    assert not measured("ece", 0.04, n=25, tier="B", inputs_ref="r").is_sufficient


def test_ac_5_10_the_reason_names_the_shortfall():
    r = insufficient("deletion_curve", 7, "A", "run-1")
    assert "30" in r.insufficient_reason and "7" in r.insufficient_reason


# --------------------------------------------------------------------------- #
# AC-5.6 — grounding
# --------------------------------------------------------------------------- #
def test_ac_5_6_grounding_rate_is_verified_over_factual():
    claims = ([Claim("a", True, "ev1")] * 18 + [Claim("b", True, None)] * 2
              + [Claim("opinion", False, None)] * 5)
    rep = grounding_rate(claims, inputs_ref="run-1")
    assert rep.factual_claim_count == 20, "non-factual claims count on NEITHER side"
    assert rep.unbound_claim_count == 2
    assert rep.result.value == pytest.approx(0.9)
    assert rep.result.n == 20


def test_ac_5_6_unbound_count_is_reported_beside_the_rate():
    """⚠ 90% over 10 claims and over 200 claims are different facts."""
    rep = grounding_rate([Claim("x", True, "e")] * 27 + [Claim("y", True, None)] * 3,
                         inputs_ref="run-1")
    assert rep.unbound_claim_count == 3 and rep.result.n == 30


# --------------------------------------------------------------------------- #
# AC-5.5 — coverage is NOT calibration
# --------------------------------------------------------------------------- #
def test_ac_5_5_coverage_and_calibration_never_share_a_field_name():
    """⚠ Upstream AB-1 — `confidence := evidence_coverage` measures how much the
    system LOOKED AT, not how often it is RIGHT."""
    cov = evidence_coverage(8, 10, inputs_ref="run-1")
    cal = calibrate([Prediction(f"d{i}", 0.8, True) for i in range(60)],
                    inputs_ref="run-1")
    assert cov.metric == "evidence_coverage"
    assert {cal.ece.metric, cal.brier.metric} == {"ece", "brier"}
    assert cov.metric not in {cal.ece.metric, cal.brier.metric}
    assert cov.tier == "A" and cal.ece.tier == "B"


def test_ac_5_5_neither_is_derived_from_the_other():
    cov = evidence_coverage(10, 10, inputs_ref="r")      # perfect coverage
    cal = calibrate([Prediction(f"d{i}", 1.0, False) for i in range(60)],
                    inputs_ref="r")                      # and always wrong
    assert cov.value == 1.0 and cal.ece.value == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# AC-5.8 — calibration joins on decision_id, counting nothing twice
# --------------------------------------------------------------------------- #
def test_ac_5_8_an_outcome_is_never_counted_twice():
    dupes = [Prediction("d1", 0.9, True)] * 3 + [
        Prediction(f"d{i}", 0.9, True) for i in range(2, 61)]
    assert calibrate(dupes, inputs_ref="r").ece.n == 60


def test_ac_5_8_unresolved_predictions_are_excluded():
    preds = ([Prediction(f"d{i}", 0.8, True) for i in range(55)]
             + [Prediction(f"u{i}", 0.8, None) for i in range(20)])
    assert calibrate(preds, inputs_ref="r").ece.n == 55


def test_calibration_is_perfect_when_confidence_matches_reality():
    preds = ([Prediction(f"a{i}", 0.9, i < 45) for i in range(50)]
             + [Prediction(f"b{i}", 0.1, i < 5) for i in range(50)])
    cal = calibrate(preds, inputs_ref="r")
    assert cal.ece.value == pytest.approx(0.0, abs=0.02)
    assert set(cal.brier_decomposition) == {"reliability", "resolution", "uncertainty"}


# --------------------------------------------------------------------------- #
# AC-5.9 — a useless attribution is caught
# --------------------------------------------------------------------------- #
def test_ac_5_9_a_noise_attribution_is_reported_unfaithful():
    """★ Removing top-k attributed features degrades no faster than random."""
    curve = deletion_curve([0.9, 0.8, 0.7], [0.9, 0.8, 0.7],
                           inputs_ref="r", n_features=50)
    assert curve.verdict == "UNFAITHFUL"


def test_ac_5_9_a_real_attribution_is_faithful():
    curve = deletion_curve([0.9, 0.5, 0.2], [0.9, 0.85, 0.8],
                           inputs_ref="r", n_features=50)
    assert curve.verdict == "FAITHFUL" and curve.result.value > 0


def test_ac_5_9_too_few_features_is_insufficient_not_unfaithful():
    curve = deletion_curve([0.9], [0.9], inputs_ref="r", n_features=5)
    assert curve.verdict == "INSUFFICIENT" and curve.result.value is None


# --------------------------------------------------------------------------- #
# AC-5.13 — experimental provenance propagates
# --------------------------------------------------------------------------- #
def test_ac_5_13_experimental_inputs_produce_an_experimental_figure():
    """F1 AC-1.11 / PG-2 — nothing from an experimental variant may read as production."""
    r = measured("grounding_rate", 0.9, 40, "A", "run-1", experimental=True)
    assert r.to_json_obj()["experimental"] is True
    rep = grounding_rate([Claim("x", True, "e")] * 30, inputs_ref="r",
                         experimental=True)
    assert rep.result.experimental is True


# --------------------------------------------------------------------------- #
# AC-5.16 / D4 — a non-recomputable figure says so
# --------------------------------------------------------------------------- #
def test_ac_5_16_a_figure_whose_inputs_expired_is_marked():
    r = MetricResult(metric="ece", n=60, tier="B", inputs_ref="run-1",
                     value=0.04, recomputable=False)
    assert r.to_json_obj()["recomputable"] is False
    assert measured("ece", 0.04, 60, "B", "r").recomputable is True


# --------------------------------------------------------------------------- #
# AC-5.1 / D2 — who may establish a golden value
# --------------------------------------------------------------------------- #
def test_ac_5_1_a_golden_case_needs_a_recorded_source():
    with pytest.raises(ValueError, match="source"):
        GoldenCase(case_id="g1", kind="extraction", input_ref="f1", expected=1,
                   source="  ", established_at="2026-09-04", established_by="Victor")


@pytest.mark.parametrize("who", ["the pipeline", "src.fundamental", "Claude",
                                 "auto-generated", "the LLM gateway"])
def test_ac_5_1_the_system_may_not_establish_its_own_golden_value(who):
    """⚠⚠ D2 — the option that looks BEST is the one that must fail.

    Seeding from the system's own output gives more cases and a permanently green
    suite, while certifying the system against itself: every regression becomes
    the new gold.
    """
    with pytest.raises(CircularGoldenValue):
        GoldenCase(case_id="g1", kind="thesis", input_ref="f1", expected={},
                   source="best run output", established_at="2026-09-04",
                   established_by=who)


def test_ac_5_1_the_fund_manager_may():
    case = GoldenCase(case_id="g1", kind="extraction", input_ref="f1",
                      expected={"revenue": 100},
                      source="read from the 10-K, page 42",
                      established_at="2026-09-04", established_by="Victor Truong")
    assert case.expected == {"revenue": 100}
    assert case.is_judgement is False


def test_ac_5_1_a_thesis_golden_value_is_recorded_as_a_judgement():
    """⚠ D2 — it does not pretend to be ground truth."""
    case = GoldenCase(case_id="t1", kind="thesis", input_ref="f2", expected={"view": "BUY"},
                      source="fund manager's own view, 2026-09-04",
                      established_at="2026-09-04", established_by="Victor Truong")
    assert case.is_judgement is True
