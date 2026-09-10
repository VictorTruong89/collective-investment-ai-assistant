"""`F7a` `AC-7a.1` — ★★ the gate that must exist before `F6b` graduates.

⚠⚠ `PG-5.1` in one sentence: *"a capability graduates when its Tier-A design
exists."* F7a's header makes it concrete — *"this spec is a gate … F7a is
written **before** the thing it measures."*

★★★ **Why this is a check and not a convention.** The gate protects against the
most natural sequence there is: build the interesting thing, measure it later.
`PG-5.1` says why "later" never arrives — `F6b` is the capability **most at risk
of being theatre**, and a convincing transcript is available either way. A gate
that lives only in a spec header is enforced by whoever remembers it at the
moment they are most motivated to forget.
"""

from __future__ import annotations

import pytest

from tools.check_gate_ordering import (
    REQUIRED_PLAN_FIELDS,
    REQUIRED_TESTS,
    gate_violations,
)


def test_ac_7a_1_the_gate_is_in_place():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert gate_violations() == []


def test_ac_7a_1_all_seven_tier_a_tests_are_defined():
    """`CT-7a.1` — ⚠ T1…T7, not "a measurement plan in principle"."""
    assert REQUIRED_TESTS == ("T1", "T2", "T3", "T4", "T5", "T6", "T7")


@pytest.mark.parametrize("field", REQUIRED_PLAN_FIELDS)
def test_ac_7a_4_the_registered_plan_supplies_every_required_field(field):
    """⚠⚠ `AC-7a.4` — *"a rule naming only a bare threshold is rejected."*

    ★ Until 2026-09-09 `KillRule` was exactly that: two band edges and a date
    (`DX-46`). It could not state its own null hypothesis, statistic,
    `detectable_ratio` or `min_n_per_arm`, so the *plan* half of
    pre-registration existed only in the spec's prose.
    """
    from src.evaluation.studies.killrule import KillRule
    rule = KillRule(registered_at="2026-09-01T00:00:00+00:00",
                    expected_revision_rate_true=0.6, registered_by="Victor Truong")
    assert getattr(rule, field) is not None


def test_ac_7a_4_an_unregistered_plan_is_refused_at_construction():
    """★ Completeness is checked when the rule is BUILT, not when it is used.

    ⚠ A plan that is only partly stated is one whose missing half gets filled
    in after the data arrives — which is the thing pre-registration exists to
    stop, so the object must not be constructible in that state.
    """
    from src.evaluation.studies.killrule import IncompletePlan, KillRule
    with pytest.raises(IncompletePlan, match="bare threshold"):
        KillRule(registered_at="2026-09-01T00:00:00+00:00",
                 expected_revision_rate_true=0.6)          # no registered_by


def test_ac_7a_1_the_check_can_FAIL(monkeypatch, tmp_path):
    """⚠ A gate that cannot refuse is decoration."""
    import tools.check_gate_ordering as mod
    missing = tmp_path / "gone.md"
    monkeypatch.setattr(mod, "F7A_SPEC", missing)
    hits = mod.gate_violations()
    assert hits and "may not graduate" in hits[0]


def test_ac_7a_1_widening_the_delete_band_to_make_it_cheaper_is_caught(monkeypatch):
    """⚠⚠ `D1`'s warning, enforced: *"do not quietly widen the DELETE band to
    make it cheaper."*

    ★★ That is `PG-5.1`'s *"a threshold chosen after seeing the data is a
    rationalisation"* arriving one step earlier — chosen after seeing the
    **cost**. The asymmetry (DELETE needs 3–4× the sample of KEEP) is the fact
    that creates the pressure, so it is asserted rather than remembered.
    """
    import tools.check_gate_ordering as mod
    from src.evaluation.studies import killrule as kr

    class _Cheap(kr.KillRule):
        cost_asymmetry = 1.0

    monkeypatch.setattr(mod, "KillRule", _Cheap, raising=False)
    monkeypatch.setitem(
        __import__("sys").modules["src.evaluation.studies.killrule"].__dict__,
        "KillRule", _Cheap)
    hits = mod.gate_violations()
    assert any("chosen after seeing the COST" in h for h in hits)
