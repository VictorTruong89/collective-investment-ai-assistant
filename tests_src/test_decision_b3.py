"""D-12 — AC-12.1…12.15, 12.19…12.28 (§5 the algebra, §6 measurement, DN-38).

Tier: **invariant/property**, and ★ **exhaustive**. `|V| = 3`, so `V^3` is 27
cases — DN-6: *"the domain is 3 elements, so exhaustive testing is free and
there is no excuse for sampling."*
"""

from __future__ import annotations

from datetime import date
from itertools import product

import pytest

from src.decision import (
    AbsentTreatedAsPassError, AnchorMismatchError, BUY, HOLD, MultipleActionableError,
    PASS, Recommendation, SELL, SellNotHeldError, VETO, apply_gate, attribute, compose,
    conservatism, enforce_inv6, is_no_more_aggressive_than, meet, veto_rate,
)
from src.decision.algebra.verdict import FLAG
from src.decision.contracts.recommendation import GateOutcome
from src.fundamental import Grade, GateVerdict, stub_gate_verdict
from src.quant import Candidate, Nomination
from src.risk import Alert, AlertSet, COMPLETE, unchecked

V = (BUY, HOLD, SELL)
S = (PASS, FLAG, VETO)
AS_OF = date(2026, 8, 23)


def nomination(**kw):
    base = dict(
        as_of=AS_OF, run_id="run-1", decision_anchor="open",
        horizon_set=("production", 1), nominating_horizon="h1m", universe_n=1,
        model_artifact_id="sha256:deadbeef",
        candidates=(Candidate("NVDA", 1, 0.0412, 2.61),),
        contract_version="b3_minimal@v1", adj_as_of=date(2024, 8, 30),
        calendar_check_id="cal:test",
    )
    return Nomination(**{**base, **kw})


def gate(status=PASS, grade=None, gate_id="thesis", stub=None):
    return GateVerdict(gate_id, "NVDA", AS_OF, status, f"{status} for test",
                       grade or Grade(), produced_by_stub=stub)


def alerts(status=COMPLETE, items=()):
    return AlertSet(tuple(items), status)


def composed(**kw):
    base = dict(
        nomination=nomination(), gate_verdicts=[gate()], alert_set=alerts(),
        run_id="run-1", as_of=AS_OF, gate_roster_declared=("thesis",),
        manifest_anchor="open", actionable=True,
        # ★ DN-39 — an actionable card needs both a COMPLETE pass (the default
        #   `alerts()` above) and a stability figure. Tests that want the
        #   informational path override `actionable`.
        top_thesis_stability={"k": 3, "modal": "BUY", "agreement": 1.0},
    )
    return compose(**{**base, **kw})


# --------------------------------------------------------------------------- #
# §5 — the algebra, exhaustively
# --------------------------------------------------------------------------- #

def test_ac_12_1_the_five_laws_hold_exhaustively_over_v3():
    """AC-12.1 — idempotence, commutativity, associativity, identity, absorption.

    ★ 27 cases and no sampling. These five are what make P3 a **type-level**
    guarantee rather than a runtime check (DN-6).
    """
    for v in V:
        assert meet(v, v) == v, "idempotence"
        assert meet(v, BUY) == v, "identity: a passing gate is a no-op"
        assert meet(v, SELL) == SELL, "absorption: once conservative, never recovered"
    for a, b in product(V, V):
        assert meet(a, b) == meet(b, a), "★ gate evaluation order cannot change it"
    for a, b, c in product(V, V, V):
        assert meet(meet(a, b), c) == meet(a, meet(b, c)), "associativity"


def test_ac_12_2_the_composition_is_never_more_aggressive_than_any_input():
    """AC-12.2 — ★ P3, implied by DN-5 rather than enforced.

    ```
    v* = meet(v_i)  ==>  v* <= v_j for every j

    The meet is a lower bound BY DEFINITION, so there is no branch to forget,
    no assertion to omit, and no code path where an upgrade is expressible.
    ```
    """
    for combo in product(V, V, V):
        composed_v = meet(*combo)
        assert all(is_no_more_aggressive_than(composed_v, v) for v in combo)


def test_ac_12_3_phi_is_monotone_in_both_arguments():
    """AC-12.3 — DN-7, all nine cases."""
    for v in V:
        for s_low, s_high in product(S, S):
            if S.index(s_low) > S.index(s_high):
                continue
            assert conservatism(apply_gate(v, s_high)) >= conservatism(apply_gate(v, s_low))
    for s in S:
        for v_agg, v_cons in product(V, V):
            if conservatism(v_agg) > conservatism(v_cons):
                continue
            assert conservatism(apply_gate(v_cons, s)) >= conservatism(apply_gate(v_agg, s))


def test_ac_12_4_flag_leaves_the_verdict_unchanged():
    """AC-12.4 — DN-8. ★ **And it must therefore change the ARTIFACT.**

    *A severity level that alters nothing anywhere trains the reader to skip it,
    which is worse than not having it.* FLAG's obligation is to D-09; the
    artifact half is asserted in `test_reporting_b3.py`.
    """
    for v in V:
        assert apply_gate(v, FLAG) == v
    rec = composed(gate_verdicts=[gate(FLAG)])
    assert rec.verdict_final == BUY
    assert rec.gates[0].status == FLAG, "the FLAG survives into the artifact"


def test_ac_12_5_a_veto_on_a_sell_is_inert():
    """AC-12.5 — ★ §5.4, a CONSEQUENCE and not a choice.

    ```
    phi(SELL, VETO) = SELL meet HOLD = SELL          (absorption)

    THE DISCIPLINE LAYER CAN STOP YOU BUYING. IT CANNOT STOP YOU SELLING.

    A system that could block an exit would be holding a position against
    its owner's instruction.
    ```
    """
    assert apply_gate(SELL, VETO) == SELL
    assert apply_gate(BUY, VETO) == HOLD, "★ VETO maps to HOLD, never to SELL (DN-9)"
    assert apply_gate(HOLD, VETO) == HOLD


def test_ac_12_6_gate_order_never_changes_the_outcome():
    """AC-12.6 — DN-14/DN-15, and it is DN-6's commutativity doing the work."""
    a = composed(gate_verdicts=[gate(VETO, gate_id="thesis"),
                                gate(PASS, gate_id="timing_h1w")],
                 gate_roster_declared=("thesis", "timing_h1w"))
    b = composed(gate_verdicts=[gate(PASS, gate_id="timing_h1w"),
                                gate(VETO, gate_id="thesis")],
                 gate_roster_declared=("thesis", "timing_h1w"))
    assert a.verdict_final == b.verdict_final == HOLD
    assert a.attribution.binding == b.attribution.binding == ("thesis",)


# --------------------------------------------------------------------------- #
# §5.5 — fail loud
# --------------------------------------------------------------------------- #

def test_ac_12_7_a_missing_gate_raises_and_is_never_treated_as_pass():
    """AC-12.7 — ★ DN-10, §5.5. **The identity must not be reachable by omission.**

    ```
    If a missing gate input is treated as PASS, the meet is unchanged and the
    recommendation goes out ungated — looking exactly like one that passed.

    Both real incidents in this repo are this bug.
    ```
    """
    with pytest.raises(AbsentTreatedAsPassError, match="ungated"):
        composed(gate_verdicts=[], gate_roster_declared=("thesis",))


def test_ac_12_7_the_empty_meet_raises_rather_than_returning_the_identity():
    """DN-10 at the algebra level — an empty argument list is the purest omission."""
    with pytest.raises(ValueError, match="identity"):
        meet()


def test_ac_12_8_the_roster_is_declared_before_the_run():
    """AC-12.8 — DN-11. Inferring it from responders makes absence undetectable."""
    from src.decision import GateMissingError
    with pytest.raises((GateMissingError, AbsentTreatedAsPassError)):
        composed(gate_verdicts=[gate(gate_id="thesis")],
                 gate_roster_declared=("thesis", "timing_h1w"))
    rec = composed()
    assert rec.gate_roster_declared == rec.gate_roster_reported == ("thesis",)


def test_ac_12_10_every_binding_gate_appears_in_the_attribution():
    """AC-12.10 — DN-13. ★ **All of them, not the first.**

    *Reporting one of three makes the other two invisible, and the reader fixes
    a third of the problem believing they fixed it.*
    """
    outcomes = [GateOutcome("thesis", VETO, HOLD, "r"),
                GateOutcome("liquidity", VETO, HOLD, "r"),
                GateOutcome("timing_h1w", PASS, BUY, "r")]
    att = attribute(BUY, outcomes)
    assert att.binding == ("liquidity", "thesis"), "both binding gates, sorted"
    assert att.binding_level == HOLD


def test_no_thesis_composes_as_veto_and_keeps_its_own_name():
    """D-01 §11.2 + DN-10 — `NO_THESIS` is a distinct state, never PASS."""
    from src.fundamental import NO_THESIS
    rec = composed(gate_verdicts=[gate(NO_THESIS)])
    assert rec.verdict_final == HOLD, "absence of a thesis moves the verdict"
    assert rec.gates[0].status == NO_THESIS, "and keeps its name in the artifact"


# --------------------------------------------------------------------------- #
# §3 — boundary
# --------------------------------------------------------------------------- #

def test_ac_12_11_every_emitted_verdict_traces_to_an_input():
    """AC-12.11 — DN-1. D-12 originates nothing."""
    for status in S:
        rec = composed(gate_verdicts=[gate(status)])
        inputs = {rec.verdict_nominated, *(g.verdict_after for g in rec.gates)}
        assert rec.verdict_final in inputs


def test_ac_12_13_and_12_12_src_decision_imports_no_gateway_and_no_analyst_seat():
    """AC-12.13 / AC-12.12 — DN-2, DN-3, ST-10, grep-checkable."""
    from tests_src.architecture import scan, st_5, st_10
    graph = scan()
    assert st_5(graph) == []
    assert st_10(graph) == [], "no D-12 output reaches D-01 or D-03 (DN-3)"


def test_ac_12_14_the_api_returns_no_score_size_or_ranking():
    """AC-12.14 — §8. ★ *If one ever does, D-12 has stopped composing.*"""
    import src.decision as d
    forbidden = {"score", "size", "rank", "rank_score", "position_size", "weight"}
    assert not (forbidden & set(d.__all__))


def test_ac_12_15_identical_inputs_produce_an_identical_recommendation():
    """AC-12.15 — INV-2."""
    a, b = composed(), composed()
    assert a.to_json_obj() == b.to_json_obj()


def test_ac_12_27_a_sell_on_an_unheld_name_raises():
    """AC-12.27 — ★ DN-24, §5.4a's precondition.

    The conservatism chain presumes a long-only book. On an unheld name a SELL
    is a **short** — an escalation, not a downgrade — and §5's ordering inverts.
    ⚠ Here the precondition is *guaranteed* rather than assumed: all four
    accounts are registered and CRA rules prohibit shorting in one.
    """
    from src.decision.compose import service
    original = service.NOMINATED_VERDICT
    service.NOMINATED_VERDICT = SELL
    try:
        with pytest.raises(SellNotHeldError, match="long-only"):
            composed(held_tickers=())
        rec = composed(held_tickers=("NVDA",))
        assert rec.verdict_final == SELL
    finally:
        service.NOMINATED_VERDICT = original


def test_ac_12_23_grade_transport_is_complete_not_selective():
    """AC-12.23 / AC-12.23a — ★ DN-32.

    ```
    A field dropped in transport is indistinguishable downstream from a field
    the producer never emitted.
    ```

    And AC-12.23a: RA-20 must be renderable from CT-12.1 alone — `k` and
    `verdict_distribution` are both present, so *"BUY 3 / HOLD 2"* can be produced.
    """
    grade = Grade(verdict=HOLD, conviction="Medium-High", stability_fraction=0.6,
                  k=5, verdict_distribution={"BUY": 3, "HOLD": 2},
                  scorecard={"moat_durability": 3},
                  confidence={"value": 0.62, "basis": "evidence_coverage"})
    rec = composed(gate_verdicts=[gate(VETO, grade)])
    assert grade.keys <= set(rec.grade), "consumer keys are a SUPERSET of producer's"
    assert rec.grade["k"] == 5 and rec.grade["verdict_distribution"] == {"BUY": 3, "HOLD": 2}
    assert rec.to_json_obj()["grade"]["consumed_by_algebra"] is False


def test_ac_12_22_transported_fields_are_byte_identical_to_their_source():
    """AC-12.22 — DN-26. A transported number that differs is a second computation."""
    nom = nomination(candidates=(Candidate("NVDA", 1, 0.041234567891, 2.6134),))
    rec = composed(nomination=nom)
    assert rec.grade["ranked_quantity"] == 0.041234567891
    assert rec.candidate["ranked_quantity"] == 0.041234567891


def test_ac_12_20_exactly_one_actionable_recommendation_per_run():
    """AC-12.20 — INV-6 / DN-22. Informational output is permitted and marked."""
    one, two = composed(), composed(actionable=False,
                                    not_actionable_reason="discovery")
    enforce_inv6([one, two])
    with pytest.raises(MultipleActionableError, match="exactly one"):
        enforce_inv6([one, composed()])


def test_ac_12_21_alerts_are_never_blocking():
    """AC-12.21 — INV-026, and the contract states no other value exists."""
    with pytest.raises(ValueError, match="never blocking"):
        Alert("D-05", 2, "x", AS_OF, blocking=True)


def test_ac_12_28_an_empty_alert_list_carries_a_status():
    """AC-12.28 — ★ DN-38, added building B3.

    ⚠ **A risk desk that correctly refused to run looked exactly like one that
    ran and found nothing.** RK-30 emits alerts only from a complete pass and
    RK-36 makes `UNCHECKED` first-class; CT-12.1 could express neither.
    """
    why = unchecked("no reconciled book (RK-29)")
    # ★ Informational, because DN-39 now forbids the pairing this test used to
    #   build: an UNCHECKED pass can never sit under an actionable card. The
    #   subject here is that the *status is transported*, which is unchanged.
    rec = composed(alert_set=AlertSet((), why), actionable=False,
                   not_actionable_reason="risk pass UNCHECKED (DN-39)")
    assert rec.alerts == () and rec.alerts_status.startswith("UNCHECKED: ")
    assert rec.to_json_obj()["alerts_status"] == why

    clean = composed(alert_set=AlertSet((), COMPLETE))
    assert clean.alerts_status == COMPLETE, "a real all-clear says COMPLETE"


def test_ac_12_19_veto_rate_is_reported_every_run():
    """AC-12.19 — DN-17. ★ Reading it needs no statistical power.

    *A rate near 0 % or 100 % is a STRUCTURAL finding* — decoration, or a ranker
    and an analyst that systematically disagree.
    """
    assert veto_rate([composed(gate_verdicts=[gate(VETO)]), composed()]) == 0.5
    with pytest.raises(ValueError, match="undefined, not 0.0"):
        veto_rate([])


def test_ac_12_23b_anchor_disagreement_with_the_manifest_raises():
    """DN-23 / OR-35 — a full session of drift, invisible in backtest."""
    with pytest.raises(AnchorMismatchError, match="full session of drift"):
        composed(manifest_anchor="close")


def test_the_b3_stub_gate_composes_without_fabricating_a_grade():
    """L3 BS-34 — a stub reports absence as absence.

    ⚠ The tempting alternative is `k=1, distribution={PASS: 1}` — literally true
    and completely misleading, which is D-15's exact shape.
    """
    stub = stub_gate_verdict("NVDA", AS_OF)
    rec = composed(gate_verdicts=[stub], actionable=False,
                   not_actionable_reason="B3 stub")
    assert rec.verdict_final == BUY
    assert rec.grade["k"] is None and rec.grade["verdict_distribution"] is None
    from src.fundamental import REPLACED_AT     # ✏ 2026-10-06: was the passed milestone "B4.4"
    assert rec.gates[0].produced_by_stub == REPLACED_AT


# --------------------------------------------------------------------------- #
# PG-7.3 · F6a AC-6a.10 — a combined verdict may never claim independent
# agreement when one seat configured another. `F6a` D3: enforced HERE, at
# composition, and checked again at rendering (tests/structural/).
# --------------------------------------------------------------------------- #

def test_ac_6a_10_an_uninfluenced_verdict_is_labelled_independent():
    """★ The status travels ALWAYS, including on the good case — a field
    present only when something is wrong is a field readers learn to skip."""
    assert composed().concurrence == "independent"
    assert composed().to_json_obj()["concurrence"] == "independent"


def test_ac_6a_10_a_cross_configured_verdict_is_labelled_not_independent():
    """⚠⚠ `PG-7`: conditioning B's configuration on A's output makes their
    agreement partly an ECHO. The label is what stops a reader counting it as
    two views."""
    rec = composed(influenced_by=("quant",))
    assert rec.concurrence == "cross-configured"
    assert "independent" not in rec.to_json_obj()["concurrence"]


def test_ac_6a_10_claiming_agreement_while_cross_configured_RAISES():
    """⚠⚠ `AC-6a.10` — the claim is REFUSED, not softened.

    ★ `F6a` `D3`: *"if the claim is never built, no renderer can emit it."*
    Guarding only the renderer would leave a true-looking agreement sitting in
    the decision record for `F5`, `F7b` and every future consumer.
    """
    from src.decision.concurrence import IndependenceClaimError

    with pytest.raises(IndependenceClaimError, match="quant"):
        composed(influenced_by=("quant",), claim_independent_agreement=True)


def test_ac_6a_10_claiming_agreement_is_allowed_when_nothing_was_configured():
    """★ The guard must not fire on the honest case, or callers route around it."""
    rec = composed(influenced_by=(), claim_independent_agreement=True)
    assert rec.concurrence == "independent"
