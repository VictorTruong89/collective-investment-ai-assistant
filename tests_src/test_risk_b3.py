"""D-05 — AC-5.17, 5.21…5.23 and the DN-38 channel (RK-29, RK-30, RK-34, RK-36).

Tier: unit + contract. ⚠ **The B3 slice is a refusal**, so most of what is
tested here is what D-05 declines to do.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.risk import (
    Alert, AlertSet, BlockAttemptedError, COMPLETE, NoBookError,
    SuppressionAttemptedError, daily_pass, emit, refuse_to_block, suppress, unchecked,
)

AS_OF = date(2026, 8, 23)


def test_rk_29_no_reconciled_book_means_no_risk_number():
    """RK-29 — ★★ D-05 never computes on an unreconciled book. It refuses, loudly.

    ```
    The tempting alternative — compute on the last good book — is worse: it
    produces a correct-looking risk report ABOUT YESTERDAY, and nothing on
    the artifact would say so.
    ```
    """
    result = daily_pass(as_of=AS_OF, book=None)
    assert result.alerts == ()
    assert result.status.startswith("UNCHECKED: ")
    assert "RK-29" in result.status

    class Broken:
        reconciled = "break"

    with pytest.raises(NoBookError, match="does not exist"):
        daily_pass(as_of=AS_OF, book=Broken())


def test_rk_30_alerts_are_emitted_only_from_a_complete_pass():
    """RK-30 — ★★ *A partial pass emitting a partial alert set reads as an
    all-clear on everything absent.* Silence from a risk desk is a claim."""
    with pytest.raises(ValueError, match="incomplete pass"):
        AlertSet((Alert("D-05", 2, "theme 61.7%", AS_OF),), unchecked("step 3 failed"))
    ok = emit([Alert("D-05", 2, "theme 61.7%", AS_OF)], complete=True)
    assert ok.status == COMPLETE


def test_rk_36_unchecked_is_first_class_and_requires_a_reason():
    """RK-36 — ⚠ *An exposure that could not be computed must never render as zero.*

    Zero theme exposure and unmeasured theme exposure are **opposite findings**
    and would look identical.
    """
    assert unchecked("no taxonomy").startswith("UNCHECKED: ")
    with pytest.raises(ValueError, match="reasonless"):
        unchecked("")
    with pytest.raises(ValueError, match="COMPLETE"):
        AlertSet((), "probably fine")


def test_ac_5_22_a_request_to_block_raises():
    """AC-5.22 — ★ INV-026, RK-34. *There is no gate step, and its absence is
    deliberate.*

    ⚠ A domain with no `block()` is silently satisfied by a caller who assumes
    one. One that raises names the rule at the moment someone reaches for it.
    """
    with pytest.raises(BlockAttemptedError, match="concentration IS the bet"):
        refuse_to_block("D-12")


def test_ac_5_17_any_attempt_to_suppress_a_flag_raises():
    """AC-5.17 — INV-021, RK-18. ★ *A flag that can be turned off is a flag that
    will be off when it matters.*"""
    with pytest.raises(SuppressionAttemptedError, match="quietly drops the tail"):
        suppress("flag-1")


def test_ac_5_2_every_alert_is_reported_only_and_unsuppressible():
    """AC-5.2 / AC-12.21 — the contract states that no other value exists."""
    a = Alert("D-05", 2, "theme 61.7% vs 40% reporting threshold", AS_OF)
    assert a.blocking is False and a.suppressible is False
    for kw in ({"blocking": True}, {"suppressible": True}):
        with pytest.raises(ValueError, match="never blocking"):
            Alert("D-05", 2, "x", AS_OF, **kw)


def test_ac_5_23_risk_imports_no_gateway_no_d01_and_not_d08():
    """AC-5.23 — RK-28, L0 §4.3's forbidden edge."""
    from tests_src.architecture import or_3, scan, st_5
    graph = scan()
    assert st_5(graph) == [] and or_3(graph) == []
    reaching_d01 = [f for f, mods in graph.items()
                    if f.startswith("src/risk/")
                    and any(m.startswith("src.fundamental") for m in mods)]
    assert reaching_d01 == [], "a thesis is not a risk input (§3)"
