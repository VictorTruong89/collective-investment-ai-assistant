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
    # ✏ 2026-10-05 — the placeholder's module (`thesis/run.py`) was removed; its basis was
    #   the literal "not_measured".
    d = Derating.of(verdict="HOLD", conviction="Medium", rubrics=_rubrics(),
                    extracted=frozenset(), outputs={}, stage_a=[])
    assert d.confidence["basis"] != "not_measured"
    assert isinstance(d.confidence["value"], float)


# ═══════════════════════════════════════════════════════════════════════════
# DX-140 (Victor, 2026-10-02) — a DECLARED known limit is stated, never a governing absence
# ═══════════════════════════════════════════════════════════════════════════

LIMIT_ROW = {"requirement": "The base must understate owner cash. FACT [D-02 known_limits: "
                            "\"capex is charged GROSS: government-incentive proceeds are not "
                            "credited against it\"]",
             "if_it_holds": "the base rises by an amount D-02 cannot compute",
             "versus_stage_a": "insufficient_evidence"}
CURABLE_ROW = {"requirement": "Implied operating margin.",
               "if_it_holds": "Not derivable: declared absent input.",
               "versus_stage_a": "insufficient_evidence"}
GOVERNS_J09 = {"considerations": [{"from_call": "J-09", "consideration": "price needs 28%"}]}


def _j09(*rows):
    return {"B:J-09": {"consensus_position": "19 buy · 3 hold · 1 sell",
                       "price_requirements": [{"versus_stage_a": "required_more_than_evidenced"},
                                              *rows]},
            "D:J-16": GOVERNS_J09}


def test_dx_140_a_requirement_insufficient_only_by_a_declared_limit_does_not_cap():
    from src.fundamental.thesis.derate import stated_limitations

    outputs = _j09(LIMIT_ROW)
    assert governing_inputs_absent(outputs, []) == ()
    stated = stated_limitations(outputs)
    assert len(stated) == 1 and stated[0].startswith("J-09:") and "GROSS" in stated[0]


def test_dx_140_a_curable_absence_beside_it_still_caps():
    """★ The ruling covers DECLARED limits only: implied margin is curable (an F10 change)."""
    absent = governing_inputs_absent(_j09(LIMIT_ROW, CURABLE_ROW), [])
    assert absent == ("J-09: a price requirement could not be set against Stage A",)


def test_dx_140_the_limitation_is_on_the_artifact_and_conviction_is_not_capped():
    required = frozenset().union(*(r.required_union for r in _rubrics()))
    d = Derating.of(verdict="SELL", conviction="Medium", rubrics=_rubrics(),
                    extracted=required, outputs=_j09(LIMIT_ROW), stage_a=[])
    assert d.conviction == "Medium" and d.confidence["governing_inputs_absent"] == []
    assert d.confidence["limitations_stated"] and "GROSS" in d.confidence["limitations_stated"][0]


def test_dx_140_quoting_the_limit_without_naming_the_field_also_counts():
    row = {**LIMIT_ROW, "requirement": "capex is charged GROSS: government-incentive proceeds "
                                       "are not credited against it (per D-02)"}
    assert governing_inputs_absent(_j09(row), []) == ()


# ═══════════════════════════════════════════════════════════════════════════
# DX-146 (Victor, 2026-10-03) — J-10 caps only on PRICE-REQUIREMENT claims
# ═══════════════════════════════════════════════════════════════════════════

from decimal import Decimal  # noqa: E402

REQ = {"growth": (Decimal("0.390496826172"), Decimal("0.282629394532")), "periods": (7, 10)}
GOVERNS_J10 = {"considerations": [{"from_call": "J-10 base rates", "consideration": "0/21"}]}


def _j10(*claims):
    return {"B:J-10": {"claims": list(claims)}, "D:J-16": GOVERNS_J10}


def test_dx_146_a_secondary_claim_without_a_base_rate_is_stated_not_capped():
    from src.fundamental.thesis.derate import stated_limitations
    out = _j10({"claim": "FCFF compounds at 28.26%/yr for ten years", "base_rate_in_bundle": True},
               {"claim": "FCFF then grows 2.5% in perpetuity at a 9% discount rate",
                "base_rate_in_bundle": False})
    assert governing_inputs_absent(out, [], price_requirement=REQ) == ()
    assert any(s.startswith("J-10:") and "perpetuity" in s
               for s in stated_limitations(out, price_requirement=REQ))


@pytest.mark.parametrize("claim", ["FCFF compounds at 39.05%/yr for seven years",
                                   "FCFF compounds at 28.3% a year",
                                   "FCFF stays positive for seven consecutive years",
                                   "a 10-year run of compounding"])
def test_dx_146_a_price_requirement_claim_without_a_base_rate_still_caps(claim):
    out = _j10({"claim": claim, "base_rate_in_bundle": False})
    assert governing_inputs_absent(out, [], price_requirement=REQ) == (
        "J-10: no reference-class base rate in the bundle",)


def test_dx_146_without_a_price_requirement_the_old_stricter_rule_holds():
    out = _j10({"claim": "FCFF then grows 2.5% in perpetuity", "base_rate_in_bundle": False})
    assert governing_inputs_absent(out, []) == ("J-10: no reference-class base rate in the bundle",)
