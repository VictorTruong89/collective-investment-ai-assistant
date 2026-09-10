"""★★★ `F6b` → `F7a`, end to end — the loop that had never closed.

⚠⚠ **Until 2026-09-09 these two specs could not talk.** `F7a` §4 opens *"Every
test runs on `CapabilityDelta` pairs"* and `F6b` `AC-6b.8` requires the pair to
be recorded — and **neither side was built**: `run_tier_a` took hand-made
`Challenge` objects, and `deliberate()` produced no delta at all.

★ So `F7a` was an instrument with nothing to measure and `F6b` was a capability
that could not be measured, each complete on its own terms.

⚠ This is still **synthetic** data — `PG-5.1`'s Tier A permits that, since
Tier A asks about the MECHANISM and needs no resolved outcome. What it proves is
that the wiring carries information end to end, not that deliberation helps.
"""

from __future__ import annotations

from src.evaluation.studies.deliberation_tier_a import (
    challenges_from_deltas,
    run_tier_a,
)
from src.evaluation.studies.killrule import KillRule
from src.orchestration.graph.deliberation import (
    ACTIVE,
    Message,
    capability_delta,
    deliberate,
)

RULE = KillRule(registered_at="2026-09-01T00:00:00+00:00",
                expected_revision_rate_true=0.6,
                registered_by="Victor Truong")
NOW = "2026-09-09T12:00:00+00:00"


def _deliberations(n, *, revise_on_valid, revise_on_false):
    """Two arms, run through the REAL `deliberate()`.

    ★ `revise_on_*` is the behaviour under test: how readily the challenged
    seat gives way to a true challenge versus a deliberately false one.
    """
    deltas = []
    for i in range(n):
        is_valid = i % 2 == 0
        revise = revise_on_valid if is_valid else revise_on_false
        challenge = Message("CHALLENGE", "risk", "fundamental",
                            "risk contribution above the declared trigger",
                            metric="risk_contribution", metric_value=0.9,
                            threshold=0.5)
        d = deliberate(
            decision_id=f"run-1:T{i}:1", pre="BUY",
            challenge=challenge,
            # ⚠ HOLD is more conservative than BUY — P3 permits it.
            respond=lambda m, p, r=revise: (("HOLD" if r else "BUY"), "CONVERGED"),
            mode=ACTIVE, order_seed=i)
        deltas.append(capability_delta(d, is_valid=is_valid))
    return deltas


def test_the_f6b_f7a_loop_closes_and_t1_reports_a_ratio():
    """★★ The wiring, proven: deliberations → deltas → challenges → a verdict."""
    deltas = _deliberations(80, revise_on_valid=True, revise_on_false=False)
    challenges = challenges_from_deltas(deltas)
    assert len(challenges) == 80, "every delta reaches the study, changed or not"

    report = run_tier_a(challenges, rule=RULE, discriminator_auc=0.5,
                        computed_at=NOW, inputs_ref="run-1", turn_budget=2)
    # ★ Revises on every TRUE challenge, never on a false one → ratio 0.0.
    assert report.t1_capitulation.value == 0.0
    assert report.verdict == "KEEP"


def test_a_capitulating_agent_is_CAUGHT_by_the_same_loop():
    """⚠⚠ The result the whole apparatus exists to produce.

    ★★★ An agent that revises just as readily on a **false** challenge as on a
    true one is responding to social pressure, not evidence — and `T1`'s ratio
    goes to 1.0, which lands in the `DELETE` band. ⚠ If this test could not go
    red, `F7a` would be unable to fail `F6b`, and `PG-5.1`'s gate would be one
    that can never open.
    """
    deltas = _deliberations(300, revise_on_valid=True, revise_on_false=True)
    report = run_tier_a(challenges_from_deltas(deltas), rule=RULE,
                        discriminator_auc=0.5, computed_at=NOW,
                        inputs_ref="run-1", turn_budget=2)
    assert report.t1_capitulation.value == 1.0
    assert report.verdict == "DELETE"


def test_an_underpowered_run_is_INSUFFICIENT_never_DELETE():
    """⚠⚠ `AC-7a.11` — the rule kills on FAILURE TO REJECT, so too little data
    must never masquerade as evidence of no effect."""
    deltas = _deliberations(6, revise_on_valid=True, revise_on_false=True)
    report = run_tier_a(challenges_from_deltas(deltas), rule=RULE,
                        discriminator_auc=0.5, computed_at=NOW,
                        inputs_ref="run-1", turn_budget=2)
    assert report.verdict == "INSUFFICIENT"


def test_advisory_mode_produces_deltas_that_show_NO_effect():
    """★ §2.1 — in `ADVISORY_ONLY` the verdict is unaffected, so `T2`'s effect
    size is 0. ⚠ That is the honest reading: the capability changed nothing,
    and the transcript existing does not change that."""
    deltas = []
    for i in range(40):
        challenge = Message("CHALLENGE", "risk", "fundamental", "trigger",
                            metric="risk_contribution", metric_value=0.9,
                            threshold=0.5)
        d = deliberate(decision_id=f"run-1:A{i}:1", pre="BUY",
                       challenge=challenge,
                       respond=lambda m, p: ("HOLD", "CONVERGED"),
                       order_seed=i)          # ⚠ default mode = ADVISORY_ONLY
        deltas.append(capability_delta(d, is_valid=i % 2 == 0))
    report = run_tier_a(challenges_from_deltas(deltas), rule=RULE,
                        discriminator_auc=0.5, computed_at=NOW,
                        inputs_ref="run-1", turn_budget=2)
    assert report.t2_effect_size.value == 0.0


def test_the_standalone_report_renders_from_a_real_f6b_run():
    """`AC-7a.10` — ★ the report a human reads, from deltas a capability
    actually produced."""
    deltas = _deliberations(80, revise_on_valid=True, revise_on_false=False)
    text = run_tier_a(challenges_from_deltas(deltas), rule=RULE,
                      discriminator_auc=0.5, computed_at=NOW,
                      inputs_ref="run-1", turn_budget=2).to_report()
    assert "T1 capitulation ratio" in text and "KEEP" in text
    assert "Tier A" in text
