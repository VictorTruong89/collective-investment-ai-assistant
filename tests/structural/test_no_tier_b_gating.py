"""`F7b` `AC-7b.5` — ⛔⛔ **nothing gates on a Tier-B result.**

⚠⚠ The AC says *structurally, not by convention*, and that wording is chosen:
this is the rule most likely to erode by **good intentions**.

★★★ Once `F7b` finally has numbers, they will be the most interesting numbers in
the system — *"did deliberation make us money?"* — and reaching for them at a
promotion decision is the natural move. ⚠ But at ~250 decisions a year against a
signal at **IC 0.0203, t = 1.42**, a Tier-B result is a second-order measurement
on an unestablished first-order one, and **more time does not fix it: the noise
grows with the sample.**
"""

from __future__ import annotations

from tools.check_no_tier_b_gating import (
    GATING_ROOTS,
    tier_b_gating_violations,
)


def test_ac_7b_5_no_gating_module_reads_a_tier_b_result():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert tier_b_gating_violations() == []


def test_ac_7b_5_a_gate_importing_the_study_is_caught(tmp_path):
    """⚠ The check must be able to FAIL, or it is decoration."""
    root = tmp_path / "src" / "quant" / "gates"
    root.mkdir(parents=True)
    (root / "metric_gate.py").write_text(
        "from src.evaluation.studies.deliberation_tier_b import study\n"
        "def promote(m):\n"
        "    return study([]).lift.value > 0\n")
    hits = tier_b_gating_violations(tmp_path)
    assert hits and "AC-7b.5" in hits[0]


def test_ac_7b_5_a_decision_module_touching_the_lift_is_caught(tmp_path):
    """★ D-12 composing on a Tier-B figure would be `PG-6` and `PG-5.1`
    breached at once."""
    root = tmp_path / "src" / "decision"
    root.mkdir(parents=True)
    (root / "compose.py").write_text(
        "def compose(deliberation_lift):\n"
        "    return 'BUY' if deliberation_lift > 0 else 'HOLD'\n")
    assert tier_b_gating_violations(tmp_path)


def test_ac_7b_5_the_study_itself_may_name_its_own_types(tmp_path):
    """★ Otherwise the module could not be written. ⚠ A check that banned the
    name everywhere would forbid the study from existing."""
    root = tmp_path / "src" / "evaluation" / "studies"
    root.mkdir(parents=True)
    (root / "deliberation_tier_b.py").write_text(
        "class TierBReport:\n    pass\n")
    assert tier_b_gating_violations(tmp_path) == []


def test_ac_7b_5_the_gating_roots_cover_where_gates_actually_live():
    """⚠ A structural check pointed at the wrong directories passes forever."""
    for expected in ("src/quant/gates", "src/decision", "src/orchestration/policy"):
        assert expected in GATING_ROOTS
