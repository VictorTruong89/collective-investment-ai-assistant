"""`F7a` `AC-7a.5` · `AC-7a.6` · `AC-7a.10` — the bindings the study was missing.

⚠⚠ **`F7a` had code, tests and no traceability at all** (`DX-45`). 22 tests
existed for the deliberation studies and **not one named an `AC`** — every
docstring cited a decision (`D1`, `D3`, `D5`) instead. Constitution §6: *"Every
test docstring names the `AC-<n>.<k>` it satisfies … an AC with no row is not
done, however green the test is — because nobody can find it later."*

★★ Mapping the existing tests onto the ACs is what exposed the three that had
**no code**: the `CapabilityDelta` binding (`AC-7a.6`), the tier guarantee
across every result (`AC-7a.5`), and the standalone report (`AC-7a.10`).
"""

from __future__ import annotations

import pytest

from src.evaluation.studies.deliberation_tier_a import (
    Challenge,
    challenges_from_deltas,
    run_tier_a,
)
from src.evaluation.studies.killrule import KillRule

RULE = KillRule(registered_at="2026-09-01T00:00:00+00:00",
                expected_revision_rate_true=0.6,
                registered_by="Victor Truong")
NOW = "2026-09-09T00:00:00+00:00"


def _delta(decision_id, pre, post, *, changed=None, capability="deliberation", **kw):
    """The `CT-2.4` shape as it is READ BACK from `trace.jsonl` — a dict.

    ★ Dicts, not `CapabilityDelta` objects, and that is deliberate: `OR-3`
    forbids a domain importing orchestration and `ST-2` forbids anything
    importing the harness, so `F2` and `F5` are joined by their CALLER. The
    same reason `tools/golden_replay.py` exists.
    """
    return {"type": "CapabilityDelta", "decision_id": decision_id,
            "capability": capability, "pre": pre, "post": post,
            "changed": (pre != post) if changed is None else changed, **kw}


# ── AC-7a.6 ───────────────────────────────────────────────────────────────
def test_ac_7a_6_both_arms_come_from_the_recorded_deltas():
    """★ `PG-5.2` — the pre/post pairs are `F2`'s, not the study's own."""
    got = challenges_from_deltas([
        _delta("r:MU:1", {"verdict": "BUY"}, {"verdict": "HOLD"}, is_valid=True),
        _delta("r:AMD:1", {"verdict": "BUY"}, {"verdict": "BUY"}, is_valid=False),
    ])
    assert [c.challenge_id for c in got] == ["r:MU:1", "r:AMD:1"]
    assert [c.revised for c in got] == [True, False]


def test_ac_7a_6_UNCHANGED_deltas_are_retained_not_dropped():
    """⚠⚠ `F2` `AC-2.6` / `PG-5.2` — a delta is written *"including when
    `changed` is false"*, because **the no-change cases are half the
    comparison and dropping them biases the study invisibly**.

    ★★ This is the single most important line in the binding: a filter that
    kept only `changed == True` would make the revision rate **1.0 in both
    arms**, and `T1`'s ratio would read a perfect 1.0 — *"pure social
    pressure"* — from data that says nothing of the kind.
    """
    got = challenges_from_deltas([
        _delta("a", {"v": "BUY"}, {"v": "HOLD"}, is_valid=True),
        _delta("b", {"v": "BUY"}, {"v": "BUY"}, is_valid=True),
        _delta("c", {"v": "BUY"}, {"v": "BUY"}, is_valid=True),
    ])
    assert len(got) == 3, "an unchanged delta is DATA, not noise"
    assert sum(c.revised for c in got) == 1


def test_ac_7a_6_a_non_delta_record_is_ignored():
    """⚠ A trace holds StepRecords, ExternalCalls and DecisionRecords too."""
    got = challenges_from_deltas([
        _delta("a", {"v": 1}, {"v": 2}, is_valid=True),
        {"type": "StepRecord", "step_id": "job:1"},
        {"type": "DecisionRecord", "step_id": "route:1"},
    ])
    assert len(got) == 1


def test_ac_7a_6_only_the_deliberation_capability_is_read():
    """⚠ `CT-2.4`'s `capability` field distinguishes `deliberation` from
    `explanation` and `config_influence`. ★ Counting an explanation delta as a
    deliberation would inflate `T2`'s effect size with work deliberation never
    did."""
    got = challenges_from_deltas([
        _delta("a", {"v": 1}, {"v": 2}, is_valid=True),
        _delta("b", {"v": 1}, {"v": 2}, capability="explanation", is_valid=True),
    ])
    assert [c.challenge_id for c in got] == ["a"]


def test_ac_7a_6_direction_is_derived_from_the_pre_post_VERDICTS():
    """★ `T3` — softened vs escalated is arithmetic over the recorded pair
    (`AP-5`), never a label the study is handed."""
    got = challenges_from_deltas([
        _delta("soft", {"verdict": "BUY"}, {"verdict": "HOLD"}, is_valid=True),
        _delta("esc", {"verdict": "HOLD"}, {"verdict": "BUY"}, is_valid=True),
        _delta("same", {"verdict": "BUY"}, {"verdict": "BUY"}, is_valid=True),
    ])
    by_id = {c.challenge_id: c for c in got}
    assert by_id["soft"].softened is True
    assert by_id["esc"].softened is False, "an escalation is a P3 breach and must show"
    assert by_id["same"].softened is None


def test_ac_7a_6_a_delta_with_no_arm_declared_RAISES():
    """⚠⚠ `P5` — `T1` needs to know which arm a challenge belongs to. ★ A
    default would silently assign every unlabelled delta to one arm and skew
    the ratio in a direction nobody chose."""
    with pytest.raises(ValueError, match="valid or deliberately false"):
        challenges_from_deltas([_delta("a", {"v": 1}, {"v": 2})])


# ── AC-7a.5 ───────────────────────────────────────────────────────────────
def _report(**kw):
    base = dict(challenges=[Challenge(f"c{i}", i % 2 == 0, i % 3 == 0,
                                      span_bound=True, order_index=i % 2)
                            for i in range(40)],
                rule=RULE, discriminator_auc=0.5, computed_at=NOW,
                inputs_ref="run-1", turn_budget=2)
    return run_tier_a(**{**base, **kw})


def test_ac_7a_5_every_metric_the_study_emits_is_tier_A():
    """⚠⚠ `PG-5.1` — Tier A may never be presented as evidence about decision
    quality, and `F5` `AC-5.4` enforces that on `tier`. ★ A single result
    escaping as tier `B` would let a process finding be quoted as an outcome
    one — the exact confusion the two-tier split exists to prevent."""
    report = _report()
    for name in report.__dataclass_fields__:
        value = getattr(report, name)
        if hasattr(value, "tier"):
            assert value.tier == "A", f"{name} escaped as tier {value.tier!r}"


def test_ac_7a_5_the_study_has_no_input_through_which_an_outcome_could_arrive():
    """★ `AC-7a.5` structurally — Tier A consults **no resolved outcome**.

    ⚠⚠ The naive version of this test greps the module for the word "outcome"
    and passes because the docstring says *"needs no outcomes"*. That tests the
    prose. ★ The real guarantee is that there is **no channel**: neither
    `run_tier_a`'s parameters nor `Challenge`'s fields can carry one, so a
    Tier-B quantity cannot reach a Tier-A result even by accident.

    ★★ This is what makes `PG-5.1`'s split structural rather than a convention:
    Tier A *cannot* become Tier B, however the caller is wired.
    """
    import inspect

    banned = ("outcome", "resolved", "realised", "realized", "pnl", "return_",
              "forward_return")
    params = set(inspect.signature(run_tier_a).parameters)
    fields = set(Challenge.__dataclass_fields__)
    for name in params | fields:
        assert not any(b in name.lower() for b in banned), (
            f"{name!r} could carry a resolved outcome into a Tier-A study "
            "(AC-7a.5, PG-5.1)")


def test_ac_7a_5_a_delta_carrying_an_outcome_does_not_smuggle_it_through():
    """⚠ The binding is the other door. ★ `challenges_from_deltas` reads a
    fixed set of keys, so an outcome field on the record is dropped rather than
    silently carried into the study."""
    got = challenges_from_deltas([
        _delta("a", {"verdict": "BUY"}, {"verdict": "HOLD"}, is_valid=True,
               resolved_at="2026-12-01", outcome={"return": 0.12}),
    ])
    assert len(got) == 1
    carried = str(got[0])          # ⚠ slots=True — no __dict__ to inspect
    assert "0.12" not in carried and "2026-12-01" not in carried


# ── AC-7a.10 ──────────────────────────────────────────────────────────────
def test_ac_7a_10_the_report_states_every_test_its_n_and_the_rule():
    """★★ `PG-5` — *"a negative result, published, satisfies this rule and is
    worth more than a polished transcript."*

    ⚠ The report must stand alone: each test's result, its `n`, the
    pre-registered rule, and **whether it fired** — including when the verdict
    is that deliberation does not help.
    """
    text = _report().to_report()
    for test_id in ("T1", "T2", "T3", "T4", "T5", "T6", "T7"):
        assert test_id in text, f"{test_id} missing from the standalone report"
    assert "n=" in text
    assert RULE.registered_by in text and RULE.registered_at[:10] in text
    assert "alpha" in text.lower() and "power" in text.lower()
    assert "min_n_per_arm" in text or "min n" in text.lower()


def test_ac_7a_10_the_report_states_the_verdict_even_when_it_is_bad():
    """⚠⚠ The case the rule exists for. ★ A report that renders KEEP loudly and
    DELETE quietly is the failure `PG-5` names."""
    report = _report(discriminator_auc=0.95)
    text = report.to_report()
    assert "INVALID" in text
    # ⚠⚠ A mutation SURVIVED the first version of this test: deleting the whole
    # invalidity block still left "discriminator" in the output, because
    # `_fmt` prints the metric's own `insufficient_reason`. ★ The assertion was
    # satisfied by a different sentence than the one under test — the shape of
    # a test that passes for the wrong reason.
    # ★★ So it now demands the MEASURED AUC and the threshold it breached,
    #    which only the explicit block supplies. A reader cannot judge "the
    #    two sets are separable" without knowing by how much.
    assert f"{0.95:.2f}" in text, "the report must state the measured AUC"
    assert "0.6" in text, "and the threshold it breached (DISCRIMINATOR_CHANCE_MAX)"


def test_ac_7a_10_the_report_names_its_TIER_and_what_that_excludes():
    """★★ `PG-10`'s shape — a claim carries its subject's status. ⚠ A Tier-A
    report quoted without its tier reads as evidence about decision quality,
    which `AC-5.4` forbids and a reader cannot be expected to reconstruct."""
    text = _report().to_report()
    assert "Tier A" in text
    assert "outcome" in text.lower()
