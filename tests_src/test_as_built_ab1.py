"""AB-1/AB-2 — the confidence postponement, pinned so it cannot drift silently.

⏸ **Postponed by Victor, 2026-08-27**: wiring B4.2 extraction and B4.3's
scorecard into authoring needs mathematical and algorithmic reconsideration plus
experiment. See `sdd/design/rel6_design/L6-as-built-remaining.md`.
"""
import pytest

from src.fundamental.scorecard.coverage import (
    CONFIDENCE_FLOOR, CONFIDENCE_HOLD_CAP,
)
from src.fundamental.thesis.run import UNMEASURED_CONFIDENCE


def test_ab1_confidence_declares_itself_unmeasured_not_zero():
    """★★ ⚠ `{"value": 0.0, "basis": "evidence_coverage"}` says *coverage was
    measured and came out zero*. **That is a lie by shape** — it makes a company
    with no evidence indistinguishable from a pipeline that never looked."""
    assert UNMEASURED_CONFIDENCE["value"] is None
    assert UNMEASURED_CONFIDENCE["basis"] == "not_measured"
    assert UNMEASURED_CONFIDENCE["reason"]


def test_ab1_the_confidence_floor_is_not_neutralised():
    """★★ **The `-1` proposal, refused on evidence.**

    ⚠ `CONFIDENCE_FLOOR` is **live in the relay path** — `relay/ingest.py` calls
    `assess_confidence`, and AC-1.77 says *"the floors fire on it unchanged"*.
    Setting it negative would disable the relay's only safety mechanism in one
    line, with no error and no failing test.

    ★ RA-38 computes the floor **from** coverage: with no coverage the floor is
    **unreachable, not disabled**, so no constant and no rule had to change.
    """
    assert CONFIDENCE_FLOOR == 0.3, "INV-012's threshold, unchanged"
    assert CONFIDENCE_HOLD_CAP == 0.5, "INV-013's threshold, unchanged"


def test_ab1_the_relay_still_reaches_the_floor():
    """★ The consumer that made `-1` unsafe. ⚠ If this import ever stops
    resolving, the argument above has lost its evidence."""
    from src.fundamental.relay.ingest import confidence_of

    assert callable(confidence_of)


def test_ab1_an_unmeasured_confidence_renders_as_a_declination():
    """RP-14 — ⚠ *never a bare number*. RA-30 gives a monitor one way to decline
    and RA-136 added `not_measurable` for a figure that is uncomputed rather
    than merely late."""
    from datetime import date

    from src.reporting.render.card import _confidence_unit

    # ⚠ RP-2 — freshness is per component, so a unit needs its own as_of.
    unit = _confidence_unit({"confidence": UNMEASURED_CONFIDENCE}, None,
                            date(2026, 8, 27))
    assert unit.value.startswith("not measured — ")
    assert "0.0" not in unit.value


def test_ab1_a_self_reported_confidence_is_still_refused():
    """RA-38 — ★ the postponement must not have widened what is accepted: a
    model-graded confidence *"lets the model raise its own ceiling"*."""
    from src.fundamental.errors import SelfReportedConfidenceError
    from src.fundamental.scorecard.coverage import reject_self_reported

    with pytest.raises(SelfReportedConfidenceError):
        reject_self_reported("self_reported")


def test_ab2_claim_binding_is_recorded_as_not_running():
    """AB-2 / RA-9 — ★ **the hallucination guard for the PROSE.** ⚠ A reader
    would wrongly conclude a passing thesis has had its narrative verified; it
    has had its falsifiers verified and its verdict constrained, not its text."""
    from pathlib import Path

    register = Path("sdd/design/rel6_design/L6-as-built-remaining.md").read_text(
        encoding="utf-8")
    assert "AB-2" in register and "RA-9" in register


def test_the_as_built_register_names_every_open_item():
    """★ BS-40 — the register is the record. ⚠ An entry that exists only in a
    commit message is an entry nobody will find."""
    from pathlib import Path

    register = Path("sdd/design/rel6_design/L6-as-built-remaining.md").read_text(
        encoding="utf-8")
    for item in (f"AB-{n}" for n in range(1, 9)):
        assert item in register, f"{item} is not registered"
