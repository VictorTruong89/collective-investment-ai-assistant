"""`INV-012` / `INV-013` / `RA-67` wired into authoring — L3 `DX-118`.

★ The decision these tests pin: **no hard cap keyed to an absent input.** A thesis is held
with its limitations stated; the floors may only make it more conservative, and a coverage
cap can never block an exit (`P3`, `DN-9`).
"""

from __future__ import annotations

import pytest

from src.fundamental.scorecard.coverage import ConfidenceAssessment
from src.fundamental.thesis.derate import (
    CAPPED_CONVICTION,
    Derating,
    cap_conviction,
    cap_verdict,
    governing_inputs_absent,
)


def _assessment(value: float) -> ConfidenceAssessment:
    from src.fundamental.scorecard.coverage import assess_confidence
    return assess_confidence(value)


@pytest.mark.parametrize(("verdict", "coverage", "expected"), [
    # ★★ The asymmetry that falls out of P3 (L1-decision §5.4): a cap stops a BUY and
    #    CANNOT stop a SELL — holding a position against its owner on a missing input.
    ("BUY", 0.45, "HOLD"),
    ("SELL", 0.45, "SELL"),
    ("HOLD", 0.45, "HOLD"),
    ("BUY", 0.80, "BUY"),
    ("SELL", 0.80, "SELL"),
    # `INV-012` — below the floor the system declines outright, whichever way it leaned.
    ("BUY", 0.20, "INSUFFICIENT_DATA"),
    ("SELL", 0.20, "INSUFFICIENT_DATA"),
])
def test_inv_012_013_the_floors_only_ever_make_a_verdict_more_conservative(verdict, coverage,
                                                                          expected):
    got, why = cap_verdict(verdict, _assessment(coverage))
    assert got == expected
    assert (why is None) == (got == verdict)


def test_a_thin_evidence_SELL_is_still_a_SELL_and_says_what_was_missing():
    """★ The domain decision (Victor, 2026-09-15): the analyst proceeds with the limitation.
    ⚠ A rule that turned this into INSUFFICIENT_DATA would be an off switch — every bundle
    this system can build today is missing consensus, peers and multiples."""
    got, why = cap_verdict("SELL", _assessment(0.45))
    assert got == "SELL" and why is None


STAGE_A = [{"block_id": "J-08", "answer": {"supply_read": "insufficient_evidence"}}]
OUTPUTS = {
    "B:J-09": {"consensus_position": "INSUFFICIENT_EVIDENCE — no consensus set was fetched",
               "price_requirements": [{"versus_stage_a": "required_more_than_evidenced"}]},
    "B:J-10": {"claims": [{"base_rate_in_bundle": False}, {"base_rate_in_bundle": True}]},
    "D:J-16": {"considerations": [
        {"from_call": "J-09 reconciliation", "consideration": "the price requires 28.3%"},
        {"from_call": "J-13:operating_margin", "consideration": "cyclical position"}]},
}


def test_only_the_absences_a_GOVERNING_consideration_rests_on_are_counted():
    """⚠ An absent input the verdict did not turn on is a data gap (`J-17`), not a de-rating.
    Here J-09 governs (so its missing consensus counts) and J-08/J-10 do not."""
    absent = governing_inputs_absent(OUTPUTS, STAGE_A)
    assert [a.split(":")[0] for a in absent] == ["J-09"]
    assert "no consensus position" in absent[0]

    governs_all = {**OUTPUTS, "D:J-16": {"considerations": [
        {"from_call": "J-08 supply", "consideration": "x"},
        {"from_call": "J-10 base rates", "consideration": "y"}]}}
    assert len(governing_inputs_absent(governs_all, STAGE_A)) == 2


def test_conviction_is_capped_low_by_a_governing_absence_and_the_verdict_is_not():
    capped, why = cap_conviction("High", ("J-09: no consensus position",))
    assert capped == CAPPED_CONVICTION and "capped at Low" in why
    assert cap_conviction("Low", ("J-09: x",)) == ("Low", None)      # already at the floor
    assert cap_conviction("High", ()) == ("High", None)              # nothing absent


def _rubrics():
    from tools.run_thesis_once import emitted_rubrics
    return emitted_rubrics()


def test_the_derating_travels_with_the_thesis_so_a_reader_can_re_derive_it():
    """`AP-2` / `PG-10` — the limitation is ON the artifact, with the numbers behind it."""
    required = frozenset().union(*(r.required_union for r in _rubrics()))
    d = Derating.of(verdict="SELL", conviction="Medium-High", rubrics=_rubrics(),
                    extracted=required, outputs=OUTPUTS, stage_a=STAGE_A)
    assert d.verdict == "SELL"                       # full coverage: nothing capped it
    assert d.confidence["value"] == 1.0 and d.confidence["cap"] == "none"
    assert d.conviction == CAPPED_CONVICTION         # a governing consideration lacks its input
    assert d.confidence["conviction_as_authored"] == "Medium-High"
    assert d.confidence["governing_inputs_absent"] and d.confidence["coverage"]["by_dimension"]
    assert d.confidence["basis"] == "evidence_coverage"      # never self-reported (RA-38)

    empty = Derating.of(verdict="BUY", conviction="High", rubrics=_rubrics(),
                        extracted=frozenset(), outputs={}, stage_a=[])
    assert empty.verdict == "INSUFFICIENT_DATA" and "below the 0.30 floor" in \
        empty.confidence["verdict_capped_by"]


def test_the_thesis_confidence_is_no_longer_the_UNMEASURED_placeholder():
    """⚠ `AB-1` — authoring shipped `{"value": None, "basis": "not_measured"}`, which reads as
    *"coverage was measured and is unknown"*. It is now the measured ratio."""
    from src.fundamental.thesis.run import UNMEASURED_CONFIDENCE

    d = Derating.of(verdict="HOLD", conviction="Medium", rubrics=_rubrics(),
                    extracted=frozenset(), outputs={}, stage_a=[])
    assert d.confidence["basis"] != UNMEASURED_CONFIDENCE["basis"]
    assert isinstance(d.confidence["value"], float)
