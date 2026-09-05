"""F5 `AC-5.7` / `AC-5.14` — the regression suite and pre-registration."""

from __future__ import annotations

import pytest

from src.evaluation.golden.models import GoldenCase
from src.evaluation.regression.run import LiveCallInRegression, run_regression
from src.evaluation.studies.compare import PreRegistrationError, compare


def _case(cid, expected):
    return GoldenCase(case_id=cid, kind="extraction", input_ref=f"fix/{cid}",
                      expected=expected, source="read from the filing",
                      established_at="2026-09-04", established_by="Victor Truong")


def test_ac_5_7_a_behaviour_change_reds_the_suite_and_names_the_cases():
    cases = [_case("c1", {"rev": 100}), _case("c2", {"rev": 200})]
    recorded = {"fix/c1": {"rev": 100}, "fix/c2": {"rev": 999}}   # prompt changed
    rep = run_regression(cases, lambda ref: recorded[ref])
    assert rep.verdict == "FAIL" and not rep.ok
    assert [d["case_id"] for d in rep.diverged] == ["c2"]
    assert rep.diverged[0]["expected"] == {"rev": 200}
    assert rep.diverged[0]["produced"] == {"rev": 999}


def test_ac_5_7_a_matching_baseline_passes():
    cases = [_case("c1", {"rev": 100})]
    rep = run_regression(cases, lambda ref: {"rev": 100})
    assert rep.ok and rep.passed == ("c1",)


def test_ac_5_7_the_regression_makes_no_live_call():
    """⚠ D5 — replayed responses only. A live call is a violation, not a slow test."""
    def live(_ref):
        raise LiveCallInRegression("reached the vendor")
    with pytest.raises(LiveCallInRegression):
        run_regression([_case("c1", {})], live)


def test_ac_5_7_divergence_names_who_established_the_expectation():
    """★ D2 — so a failing case can be taken back to the person who set it."""
    rep = run_regression([_case("c1", {"rev": 1})], lambda ref: {"rev": 2})
    assert rep.diverged[0]["established_by"] == "Victor Truong"


# --------------------------------------------------------------------------- #
# AC-5.14 — pre-registration
# --------------------------------------------------------------------------- #
def _cmp(**kw):
    base = dict(arm_a="no_deliberation", arm_b="deliberation", metric="grounding_rate",
                value_a=0.80, value_b=0.88, n_a=40, n_b=40,
                pre_registered_rule="delete if grounding_rate does not improve by 0.05",
                pre_registered_at="2026-09-01T00:00:00Z",
                computed_at="2026-09-04T00:00:00Z")
    return compare(**{**base, **kw})


def test_ac_5_14_a_registered_rule_before_the_run_is_accepted():
    r = _cmp()
    assert r.verdict == "PASS" and r.tier == "A"


def test_ac_5_14_a_rule_written_after_the_data_is_refused():
    """⚠ *A threshold chosen after seeing the data is a rationalisation.*"""
    with pytest.raises(PreRegistrationError, match="rationalisation"):
        _cmp(pre_registered_at="2026-09-04T12:00:00Z")


def test_ac_5_14_an_empty_rule_is_refused():
    with pytest.raises(PreRegistrationError, match="required"):
        _cmp(pre_registered_rule="   ")


def test_ac_5_4_an_underpowered_comparison_is_insufficient_never_a_pass():
    """PG-5.1 — INSUFFICIENT is a verdict, and never a silent pass."""
    assert _cmp(n_a=5, n_b=5).verdict == "INSUFFICIENT"
