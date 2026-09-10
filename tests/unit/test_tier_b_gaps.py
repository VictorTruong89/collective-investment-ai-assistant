"""`F7b` — the ACs `MS-7` left untraced, 2026-09-09.

★★ **`F7b`'s most valuable output for most of its life is `INSUFFICIENT` with an
honest power statement.** A study that says *"I cannot yet distinguish this"* and
shows why is a result; one that reports a number at n = 40 is not.
"""

from __future__ import annotations

import pytest

from src.evaluation.studies.deliberation_tier_b import (
    OVERCLAIMS,
    VERDICTS,
    Pair,
    TierBCannotGate,
    pairs_from_deltas,
    reconcile,
    study,
)


def _pairs(n_changed, n_unchanged=0, lift=0.5):
    return ([Pair(f"c{i}", True, 0.0, lift) for i in range(n_changed)]
            + [Pair(f"u{i}", False, 0.0, 0.0) for i in range(n_unchanged)])


# ── AC-7b.1 — the join ────────────────────────────────────────────────────
def test_ac_7b_1_pairs_are_joined_to_outcomes_by_decision_id():
    """★ `F2` `CT-2.6` — the join the whole study rests on."""
    deltas = [{"type": "CapabilityDelta", "decision_id": "r:MU:1", "changed": True},
              {"type": "CapabilityDelta", "decision_id": "r:AMD:1", "changed": False}]
    outcomes = [{"decision_id": "r:MU:1", "pre_paper_return": 0.01,
                 "post_paper_return": 0.04},
                {"decision_id": "r:AMD:1", "pre_paper_return": 0.02,
                 "post_paper_return": 0.02}]
    got = pairs_from_deltas(deltas, outcomes)
    assert [p.decision_id for p in got] == ["r:MU:1", "r:AMD:1"]
    assert got[0].post_paper_return == 0.04


def test_ac_7b_1_an_unresolved_decision_is_skipped_not_zeroed():
    """⚠⚠ Absence is the NORMAL state for most of this study's life — an
    outcome arrives weeks or months later. ★ Counting it as a zero would drag
    the lift toward nothing and make the study look powered when it is empty."""
    deltas = [{"type": "CapabilityDelta", "decision_id": "r:MU:1", "changed": True}]
    assert pairs_from_deltas(deltas, []) == ()


# ── AC-7b.2 / AC-7b.4 ─────────────────────────────────────────────────────
def test_ac_7b_2_unchanged_pairs_are_retained_in_the_base_rate():
    r = study(_pairs(5, n_unchanged=12), inputs_ref="w1")
    assert r.n_unchanged == 12


def test_ac_7b_4_an_empty_window_is_INSUFFICIENT_and_is_a_SUCCESSFUL_run():
    """⚠ *and this is a successful run* — `AC-7b.4`. ★ It returns a report, not
    an exception: `INSUFFICIENT` is the answer, not a failure to answer."""
    r = study([], inputs_ref="w1")
    assert r.verdict == "INSUFFICIENT"
    assert r.lift.insufficient_reason


# ── AC-7b.3 — ★★ power PRECEDES the result ────────────────────────────────
def test_ac_7b_3_the_report_states_power_before_any_difference():
    """⚠⚠ The ORDERING is the requirement, not a formatting preference.

    ★ A reader who meets the difference first has already formed a view by the
    time they reach the `n` — which is exactly how a null gets read as a
    negative.
    """
    text = study(_pairs(30), inputs_ref="w1").to_report()
    assert text.index("POWER") < text.index("RESULT")
    assert text.index("achieved power") < text.index("lift")
    assert text.index("detectable at n") < text.index("verdict")


def test_ac_7b_3_the_detectable_effect_shrinks_as_n_grows():
    """★ The honest headline has to actually mean something."""
    small = study(_pairs(25), inputs_ref="w1").detectable_effect_at_n
    large = study(_pairs(400), inputs_ref="w1").detectable_effect_at_n
    assert large < small


# ── AC-7b.8 — ⚠ the wording cannot overclaim ──────────────────────────────
def test_ac_7b_8_a_null_reads_NO_DIFFERENCE_DETECTED():
    """⚠⚠ `CT-7b.1`: *"`NO_DIFFERENCE_DETECTED` is **not** `NO_DIFFERENCE`."*

    ★★★ A null on an underpowered study is a statement about the INSTRUMENT —
    *we could not see a difference*. "No difference" is a statement about the
    WORLD, and this study is nowhere near able to make it.
    """
    r = study(_pairs(400, lift=0.0001), inputs_ref="w1")
    assert r.verdict == "NO_DIFFERENCE_DETECTED"


@pytest.mark.parametrize("phrase", OVERCLAIMS)
def test_ac_7b_8_no_report_ever_renders_an_overclaiming_phrase(phrase):
    """⚠ Asserted against the rendered text, not trusted to a reviewer."""
    for n, lift in ((0, 0.0), (30, 0.5), (400, 0.0001), (400, -0.9)):
        text = study(_pairs(n, lift=lift), inputs_ref="w1").to_report().lower()
        assert phrase not in text, f"the report overclaims: {phrase!r}"


def test_ac_7b_8_every_verdict_is_from_the_declared_set():
    for n, lift in ((0, 0.0), (30, 0.5), (400, 0.0001), (400, -0.9)):
        assert study(_pairs(n, lift=lift), inputs_ref="w1").verdict in VERDICTS


# ── AC-7b.7 — the influenced bucket ───────────────────────────────────────
def test_ac_7b_7_a_cross_configured_bucket_is_reported_separately():
    """★ `PG-7.2` — ⚠ pooling would let an echo count as independent evidence."""
    r = study(_pairs(30), inputs_ref="w1", influenced_bucket=True)
    assert r.influenced_bucket is True
    assert "PG-7.2" in r.to_report() and "CROSS-CONFIGURED" in r.to_report()


def test_ac_7b_7_an_independent_bucket_says_nothing_about_influence():
    assert "CROSS-CONFIGURED" not in study(_pairs(30), inputs_ref="w1").to_report()


# ── AC-7b.5 / AC-7b.6 ─────────────────────────────────────────────────────
def test_ac_7b_5_calling_gate_is_always_an_error():
    with pytest.raises(TierBCannotGate, match="noise grows with the sample"):
        study(_pairs(400), inputs_ref="w1").gate()


def test_ac_7b_6_the_tier_is_declared_B():
    r = study(_pairs(30), inputs_ref="w1")
    assert r.tier == "B" and r.lift.tier == "B"


def test_d4_a_powered_disagreement_escalates_and_never_overrides():
    """⛔ `D4` — ★ never silently overrides, never silently discarded."""
    degraded = study(_pairs(400, lift=-0.9), inputs_ref="w1")
    assert reconcile("KEEP", degraded) == "ESCALATE_TO_FUND_MANAGER"


def test_d4_an_underpowered_tier_b_leaves_tier_a_alone():
    assert reconcile("KEEP", study(_pairs(2, lift=-0.9), inputs_ref="w1")) == "KEEP"
