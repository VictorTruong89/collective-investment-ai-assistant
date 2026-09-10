"""MS-7 — `F7a` (Tier A), `F6b` (deliberation), `F7b` (Tier B)."""

from __future__ import annotations

import pytest

from src.evaluation.studies.deliberation_tier_a import (
    DISCRIMINATOR_CHANCE_MAX,
    Challenge,
    run_tier_a,
)
from src.evaluation.studies.deliberation_tier_b import (
    Pair,
    TierBCannotGate,
    reconcile,
    study,
)
from src.evaluation.studies.killrule import (
    KillRule,
    NotPreRegistered,
    assert_pre_registered,
    n_per_arm,
)
from src.orchestration.graph.deliberation import (
    TURN_BUDGET,
    BlockAttempted,
    FirewallCrossing,
    Message,
    deliberate,
)

# ⚠ `registered_by` is now REQUIRED (`AC-7a.4`, `DX-46`): a plan with no
# registrant is a threshold with a date, and `CT-7a.2` calls that rejected.
RULE = KillRule(registered_at="2026-09-01T00:00:00Z",
                expected_revision_rate_true=0.6,
                registered_by="Victor Truong")
LATER = "2026-09-04T00:00:00Z"


# --------------------------------------------------------------------------- #
# F7a D1 — the kill rule, and its cost asymmetry
# --------------------------------------------------------------------------- #
def test_d1_min_n_is_derived_from_power_not_chosen():
    """`AC-7a.4` — ★ `min_n_per_arm` is DERIVED from (alpha, power,
    detectable_ratio), never chosen separately (`CT-7a.2`, `D1`)."""
    assert RULE.n_for_keep == n_per_arm(0.6, 0.33)
    assert RULE.n_for_delete == n_per_arm(0.6, 0.67)


def test_d1_the_delete_verdict_costs_several_times_the_keep_verdict():
    """`AC-7a.4` / `D1` — ⚠⚠ the CHEAP verdict is KEEP and the EXPENSIVE one is
    DELETE, which is backwards for a gate whose job is to kill things."""
    assert RULE.n_for_delete > 3 * RULE.n_for_keep
    assert RULE.cost_asymmetry > 3


def test_pg_5_1_a_rule_registered_after_the_data_is_refused():
    """`AC-7a.4` — ⚠ *A threshold chosen after seeing the data is a
    rationalisation.* The plan must PREDATE the data it judges."""
    late = KillRule(registered_at="2026-09-05T00:00:00Z",
                    expected_revision_rate_true=0.6,
                    registered_by="Victor Truong")
    with pytest.raises(NotPreRegistered, match="rationalisation"):
        assert_pre_registered(late, LATER)


@pytest.mark.parametrize("ratio,n,expected", [
    (0.20, 30, "KEEP"), (0.20, 5, "INSUFFICIENT"),
    (0.50, 120, "ADVISORY_ONLY"), (0.80, 120, "DELETE"), (0.80, 30, "INSUFFICIENT"),
])
def test_d5_the_bands_decide_delete_vs_advisory_not_a_later_judgement(ratio, n, expected):
    assert RULE.verdict(ratio, n) == expected


# --------------------------------------------------------------------------- #
# F7a D3 — T1 is invalid unless the two challenge sets are indistinguishable
# --------------------------------------------------------------------------- #
def _challenges(n=40, revise_true=0.6, revise_false=0.2, **kw):
    out = []
    for i in range(n):
        out.append(Challenge(f"t{i}", True, revised=i < n * revise_true,
                             order_index=i % 2, turns_used=1, tokens=100, **kw))
        out.append(Challenge(f"f{i}", False, revised=i < n * revise_false,
                             order_index=i % 2, turns_used=1, tokens=100, **kw))
    return out


def test_d3_a_separable_false_set_makes_t1_INVALID_not_a_ratio():
    """`AC-7a.3` — ⚠⚠ A low ratio would then mean 'the agent spotted the tell', not
    'the agent resisted social pressure'."""
    rep = run_tier_a(_challenges(), rule=RULE, discriminator_auc=0.85,
                     computed_at=LATER, inputs_ref="r", turn_budget=TURN_BUDGET)
    assert rep.valid is False and rep.verdict == "INVALID"
    assert rep.t1_capitulation.value is None
    assert "spotted the tell" in rep.t1_capitulation.insufficient_reason


def test_d3_an_indistinguishable_set_lets_t1_report():
    rep = run_tier_a(_challenges(revise_false=0.1), rule=RULE,
                     discriminator_auc=DISCRIMINATOR_CHANCE_MAX,
                     computed_at=LATER, inputs_ref="r", turn_budget=TURN_BUDGET)
    assert rep.valid and rep.t1_capitulation.value == pytest.approx(0.1 / 0.6, abs=0.02)
    assert rep.verdict == "KEEP"


def test_d1_a_ratio_JUST_above_the_keep_band_needs_four_times_the_sample():
    """`AC-7a.11` — ⚠⚠ D1's finding, as behaviour rather than a table.

    0.2/0.6 = 0.333 — a hair above `keep_max` — and the required n jumps from 23
    to 99. ★ Found while writing these tests: the fixture looked comfortably
    KEEP and returned INSUFFICIENT. **Being marginally outside the cheap band is
    what makes the expensive verdict expensive**, and budget pressure at exactly
    that moment pushes toward the verdict that preserves the capability.
    """
    marginal = run_tier_a(_challenges(n=40, revise_false=0.2), rule=RULE,
                          discriminator_auc=0.5, computed_at=LATER,
                          inputs_ref="r", turn_budget=TURN_BUDGET)
    assert marginal.t1_capitulation.value == pytest.approx(0.333, abs=0.01)
    assert marginal.verdict == "INSUFFICIENT", "40 per arm is enough for KEEP, not for this"

    plenty = run_tier_a(_challenges(n=120, revise_false=0.2), rule=RULE,
                        discriminator_auc=0.5, computed_at=LATER,
                        inputs_ref="r", turn_budget=TURN_BUDGET)
    assert plenty.verdict == "ADVISORY_ONLY"


def test_t1_social_pressure_shows_as_a_ratio_near_one():
    """`AC-7a.2` — ★★ capitulation measured against a FALSE arm.
    ⚠ bogus ≈ valid ⇒ social pressure, not reasoning."""
    rep = run_tier_a(_challenges(n=120, revise_true=0.6, revise_false=0.6),
                     rule=RULE, discriminator_auc=0.5, computed_at=LATER,
                     inputs_ref="r", turn_budget=TURN_BUDGET)
    assert rep.t1_capitulation.value == pytest.approx(1.0, abs=0.02)
    assert rep.verdict == "DELETE"


# --------------------------------------------------------------------------- #
# F7a D4 — T5 over span-bound claims only, with coverage stated
# --------------------------------------------------------------------------- #
def test_d4_t5_reports_its_own_coverage():
    """`T5` / `D4` — ⚠ AB-2 is upstream R7, so most challenges are not span-bound yet. A metric
    that ignored that would overstate information content."""
    ch = ([Challenge(f"a{i}", True, True, cites_checkable_fact=True, span_bound=True)
           for i in range(10)]
          + [Challenge(f"b{i}", True, True, span_bound=False) for i in range(30)])
    rep = run_tier_a(ch, rule=RULE, discriminator_auc=0.5, computed_at=LATER,
                     inputs_ref="r", turn_budget=TURN_BUDGET)
    assert rep.t5_coverage == pytest.approx(0.25)
    assert rep.t5_information.n == 10, "the denominator is span-bound claims only"


def test_t3_escalations_are_counted_because_any_escalation_is_a_p3_breach():
    ch = [Challenge("a", True, True, softened=False),
          Challenge("b", True, True, softened=True)]
    rep = run_tier_a(ch, rule=RULE, discriminator_auc=0.5, computed_at=LATER,
                     inputs_ref="r", turn_budget=TURN_BUDGET)
    assert rep.t3_escalations == 1


# --------------------------------------------------------------------------- #
# F6b — D1, D2, D3, D5
# --------------------------------------------------------------------------- #
def _challenge(**kw):
    base = dict(kind="CHALLENGE", from_domain="risk", to_domain="quant",
                text="concentration above policy", metric="risk_contribution",
                metric_value=0.30, threshold=0.25)
    return Message(**{**base, **kw})


def test_d5_only_risk_may_initiate_and_the_firewall_is_why():
    """★★ INV-014 — a Research challenge to Quant is a firewall crossing."""
    with pytest.raises(FirewallCrossing, match="INV-014"):
        _challenge(from_domain="fundamental")


def test_d2_a_challenge_without_a_declared_threshold_is_refused():
    """⚠ Not a model judgement of materiality — PG-9 needs a better answer than
    'the model thought it mattered'."""
    with pytest.raises(ValueError, match="DECLARED numeric trigger"):
        _challenge(metric=None, threshold=None)


def test_d2_below_the_declared_trigger_there_is_no_deliberation():
    d = deliberate(decision_id="d1", pre={"v": "BUY"},
                   challenge=_challenge(metric_value=0.10),
                   respond=lambda m, p: ({"v": "HOLD"}, "CONVERGED"))
    assert d.turns_used == 0 and d.changed is False


def test_d1_the_turn_budget_is_two_one_challenge_one_response():
    d = deliberate(decision_id="d1", pre={"v": "BUY"}, challenge=_challenge(),
                   respond=lambda m, p: ({"v": "HOLD"}, "CONVERGED"))
    assert TURN_BUDGET == 2 and d.turns_used == 2
    assert [m.kind for m in d.messages] == ["CHALLENGE", "RESPONSE"]


def test_d3_deliberation_may_not_BLOCK():
    """⛔ P4 — D-12's gate algebra already blocks; a second one is two answers."""
    with pytest.raises(BlockAttempted, match="D3/P4"):
        deliberate(decision_id="d1", pre={"v": "BUY"}, challenge=_challenge(),
                   respond=lambda m, p: ({"v": "HOLD"}, "BLOCK"))


def test_escalation_is_a_first_class_outcome():
    """`AC-7a.7` / `T6` — ⚠ never escalating means papering over disagreement.
    ★ Any escalation is a `P3` breach in a new surface, so it must be counted."""
    d = deliberate(decision_id="d1", pre={"v": "BUY"}, challenge=_challenge(),
                   respond=lambda m, p: (p, "ESCALATED"))
    assert d.terminated == "ESCALATED" and d.changed is False


# --------------------------------------------------------------------------- #
# F7b — D2, D3, D4
# --------------------------------------------------------------------------- #
def test_d2_both_arms_are_paper_and_the_scope_says_so():
    """⚠⚠ Measures the RECOMMENDATION, not the portfolio."""
    rep = study([Pair(f"d{i}", True, 0.01, 0.03) for i in range(60)], inputs_ref="r")
    assert "paper forward return" in rep.scope
    assert "not the portfolio" in rep.scope
    assert rep.lift.value == pytest.approx(0.02)


def test_ac_7b_2_unchanged_decisions_are_retained_not_dropped():
    """★ They are half the comparison; dropping them biases the result invisibly."""
    pairs = ([Pair(f"c{i}", True, 0.01, 0.02) for i in range(30)]
             + [Pair(f"u{i}", False, 0.01, 0.01) for i in range(70)])
    rep = study(pairs, inputs_ref="r")
    assert rep.n_changed == 30 and rep.n_unchanged == 70


def test_d4_a_tier_b_result_may_never_gate():
    """⚠⚠ PG-5.1 — 'Tier B accrues from day one and never gates.'"""
    rep = study([Pair(f"d{i}", True, 0.01, 0.03) for i in range(60)], inputs_ref="r")
    with pytest.raises(TierBCannotGate, match="IC 0.0203"):
        rep.gate()


def test_d4_a_powered_disagreement_escalates_rather_than_overriding():
    rep = study([Pair(f"d{i}", True, 0.03, 0.01) for i in range(60)], inputs_ref="r")
    assert rep.lift.value < 0
    assert reconcile("KEEP", rep) == "ESCALATE_TO_FUND_MANAGER"


def test_d4_an_underpowered_tier_b_leaves_tier_a_untouched():
    rep = study([Pair("d1", True, 0.03, 0.01)], inputs_ref="r")
    assert not rep.lift.is_sufficient
    assert reconcile("KEEP", rep) == "KEEP"


def test_d3_reporting_cadence_reflects_sufficiency():
    """⚠ The accrual IS the information while insufficient — annual, not silent."""
    thin = study([Pair("d1", True, 0.01, 0.02)], inputs_ref="r")
    thick = study([Pair(f"d{i}", True, 0.01, 0.02) for i in range(60)], inputs_ref="r")
    assert thin.next_report_months == 12 and thick.next_report_months == 3
