"""D-12 DN-39 — an actionable card needs a complete risk pass and a stability figure."""
import pytest

from src.decision.compose.service import assert_actionable_inputs
from src.decision.errors import DecisionError


class _Alerts:
    def __init__(self, status):
        self.status = status


STABLE = {"k": 3, "modal": "BUY", "agreement": 1.0}


def test_unchecked_risk_pass_refuses_actionable():
    """AC-12.29 (DN-39) — an UNCHECKED alert set is an all-clear D-05 never made."""
    with pytest.raises(DecisionError, match="never ran"):
        assert_actionable_inputs(_Alerts("UNCHECKED: no book"), STABLE)


def test_absent_stability_refuses_actionable():
    """AC-12.29 (DN-39, RA-20) — a verdict may not reach a human as actionable
    before its stability figure exists."""
    with pytest.raises(DecisionError, match="verdict_stability"):
        assert_actionable_inputs(_Alerts("COMPLETE"), None)


def test_both_present_permits_actionable():
    """AC-12.29 — the positive case: a complete pass and a k>=3 result."""
    assert_actionable_inputs(_Alerts("COMPLETE"), STABLE)


def test_refusal_names_the_missing_input_not_a_generic_disclaimer():
    """AC-12.29 / RA-30 — a reader must be able to tell a deliberate hold from a
    broken pipeline, so the reason names which input is missing."""
    from src.orchestration.jobs.wiring import _why_not

    why = _why_not(None, _Alerts("UNCHECKED: no book"))
    assert "verdict stability" in why and "UNCHECKED" in why


def test_missing_status_attribute_is_not_treated_as_complete():
    """AC-12.29 — ★ the defect this rule exists for: an alert set carrying no
    status at all must not read as an all-clear (DN-38)."""
    class _Bare:
        pass

    with pytest.raises(DecisionError, match="never ran"):
        assert_actionable_inputs(_Bare(), STABLE)
