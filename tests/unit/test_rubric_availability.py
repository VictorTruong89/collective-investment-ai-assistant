"""`RA-32` / `DX-82` — which rubric levels a bundle can actually support.

★★★ *A level selected without its evidence present in the bundle is a FAILED
selection, not a low-confidence one.* Until 2026-09-12 the judgement runner
offered all five levels on every rubric call and printed a warning.
"""

from __future__ import annotations

import pytest

from src.fundamental.scorecard.availability import (
    NoAvailableLevel,
    available_levels,
    evidence_ids_in,
    require_levels,
)
from src.fundamental.scorecard.models import Rubric, RubricLevel


def _rubric(*levels) -> Rubric:
    return Rubric(dimension="moat_durability", version=1, note="t", levels=levels)


def test_ra_32_a_level_needs_ALL_of_its_evidence_not_any():
    """⚠ `RA-32` reads *"items are absent"*. A level citing three evidence ids
    is a criterion a reader checks against three things, and two of them is an
    UNCHECKED criterion — which is the thin-evidence answer that reads as a
    considered one."""
    r = _rubric(RubricLevel(4, "needs both", ("a", "b")),
                RubricLevel(0, "needs one", ("a",)))
    assert available_levels(r, frozenset({"a"})) == (0,)
    assert available_levels(r, frozenset({"a", "b"})) == (4, 0)


def test_ra_32_raw_filing_text_carries_NO_evidence_ids():
    """★★★ The finding that made `DX-85` visible.

    ⚠⚠ An evidence id (`seg.revenue`, `cap.action`) is an EXTRACTION OUTPUT
    (`MP-4`). A filing contains the facts one would be extracted FROM; it does
    not contain the extraction. ★ `RA-19` — assembly is mechanical, so a bundle
    that has not been through the E-blocks has not got the evidence, and
    assuming otherwise lets the judging layer supply its own inputs.
    """
    from datetime import date

    from src.fundamental.bundle.models import BundlePart, EvidenceBundle

    bundle = EvidenceBundle(
        ticker="MU", as_of=date(2025, 6, 26),
        parts=(BundlePart(kind="filing", pins={"accession_id": "x"},
                          content="Total revenue was $9,301 million."),))
    assert evidence_ids_in(bundle) == frozenset()


def test_ra_32_a_part_declaring_evidence_ids_is_counted():
    """★ The mechanism works on any part that declares the pin — the gate is
    ready for a bundle that carries extraction output."""
    from datetime import date

    from src.fundamental.bundle.models import BundlePart, EvidenceBundle

    bundle = EvidenceBundle(
        ticker="MU", as_of=date(2025, 6, 26),
        parts=(BundlePart(kind="filing", pins={"accession_id": "x"}, content="f"),
               BundlePart(kind="computed",
                          pins={"contract_name": "c", "contract_version": "1",
                                "evidence_ids": ["seg.revenue", "seg.op_income"]},
                          content="{}")))
    assert evidence_ids_in(bundle) == frozenset({"seg.revenue", "seg.op_income"})


def test_dx_85_the_bundle_contract_has_EXACTLY_ONE_part_kind_for_extraction_OUTPUT():
    """✅ `DX-85`ⓒ CLOSED 2026-09-12 (approved by Victor). This test pinned the
    broken state — *no* kind for the E-blocks' output — and was written to fail
    the moment one was added. Rewritten to assert the fixed state; the
    behaviour lives in `test_extraction_bundle_part.py`.

    ⚠ Exactly one: two kinds carrying extraction output would give one fact
    two pins, and `RA-32` would count whichever a caller happened to use.
    """
    from src.fundamental.bundle.models import PIN_FIELDS

    assert [k for k in PIN_FIELDS if "extract" in k] == ["extraction"]


def test_ra_32_no_available_level_is_NOT_a_score_of_zero():
    """★★★ The distinction the whole module exists for.

    ⚠⚠ A floor score is a JUDGEMENT — the evidence was looked for and found
    wanting. `NoAvailableLevel` is the statement that the rubric could not be
    applied at all. ★ Collapsing them lets a WIRING GAP read as an analytical
    finding, which is exactly what the ungated run's `capital_allocation = 0`
    did on 2026-09-12.
    """
    r = _rubric(RubricLevel(0, "floor", ("cap.action",)))
    assert available_levels(r, frozenset({"seg.revenue"})) == ()
    with pytest.raises(NoAvailableLevel, match="NOT a score of 0"):
        require_levels(r, frozenset({"seg.revenue"}))


def test_dx_98_a_PARTIAL_rubric_is_refused_not_scored():
    """⛔⛔ `DX-98`, decided by Victor 2026-09-12: score only when EVERY level
    is available. ★ Measured shape: higher levels need more evidence, so a
    partial bundle removes levels from the TOP and leaves the floor."""
    from src.fundamental.scorecard.availability import PartialRubricEvidence

    r = _rubric(RubricLevel(4, "top", ("a", "b")),
                RubricLevel(2, "mid", ("a",)),
                RubricLevel(0, "floor", ("a",)))
    assert available_levels(r, frozenset({"a"})) == (2, 0)
    with pytest.raises(PartialRubricEvidence, match=r"Missing: \['b'\]"):
        require_levels(r, frozenset({"a"}))
    assert require_levels(r, frozenset({"a", "b"})) == (4, 2, 0)


def test_dx_98_partial_IS_a_NoAvailableLevel_so_no_caller_can_score_it_by_omission():
    """★ A caller written before `DX-98` catches `NoAvailableLevel` only. The
    subclass makes it refuse a partial rubric too, with no second `except`."""
    from src.fundamental.scorecard.availability import PartialRubricEvidence

    assert issubclass(PartialRubricEvidence, NoAvailableLevel)
    r = _rubric(RubricLevel(4, "top", ("a", "b")), RubricLevel(0, "floor", ("a",)))
    with pytest.raises(NoAvailableLevel, match="NOT a score of 0"):
        require_levels(r, frozenset({"a"}))


def test_dx_98_on_MU_the_measured_bundle_refuses_all_four_dimensions():
    """★★ The measurement that motivated `DX-98`, pinned: the evidence ids the
    four good 2026-09-12 runs plus E-01/E-02 actually found. Before `DX-98`
    this offered J-03 `(3,2,1,0)`, J-05 `(0,)`, J-06 `(0,)`."""
    from src.fundamental.scorecard.rubrics.b43_v2 import B43_V2_RUBRICS

    mu = frozenset({"seg.basis_note", "seg.name", "seg.op_income", "seg.revenue",
                    "gd.language_note", "gd.metric", "gd.period", "gd.stated_on",
                    "gd.value", "dm.covenant", "dm.instrument", "dm.ladder",
                    "dm.revolver", "ca.authorisation", "ca.buyback", "ca.capex",
                    "ca.dividend", "ca.issuance", "ca.rd"})
    for rubric in B43_V2_RUBRICS:
        with pytest.raises(NoAvailableLevel):
            require_levels(rubric, mu)


def test_ra_32_the_refusal_names_what_was_needed_and_what_was_there():
    """`CN-10` — an error that names the shortfall beats one that states it."""
    r = _rubric(RubricLevel(0, "floor", ("cap.action", "cap.stated_priority")))
    with pytest.raises(NoAvailableLevel) as exc:
        require_levels(r, frozenset({"seg.revenue"}))
    assert "cap.action" in str(exc.value) and "seg.revenue" in str(exc.value)


def test_dx_85_the_published_rubrics_cannot_be_scored_from_a_bare_filing():
    """⚠⚠⚠ `DX-85`, pinned as a measured fact rather than left as a surprise.

    ★ Every one of the four published rubrics returns ZERO available levels
    against a bundle carrying no extraction output — which is every Stage-A
    bundle today. The 2026-09-12 run answered all four anyway, for ~$2.6.
    """
    from src.fundamental.scorecard.rubrics.b43_v1 import (
        BALANCE_SHEET_RESILIENCE,
        CAPITAL_ALLOCATION,
        EARNINGS_QUALITY,
        MOAT_DURABILITY,
    )
    for rubric in (MOAT_DURABILITY, EARNINGS_QUALITY,
                   BALANCE_SHEET_RESILIENCE, CAPITAL_ALLOCATION):
        assert available_levels(rubric, frozenset()) == (), rubric.dimension


def test_dx_85_three_of_thirteen_required_evidence_ids_are_emitted_by_any_E_block():
    """★★★ The wiring bug `b43_v1.py`'s own comment predicted.

    ⚠⚠ *"These must match what B4.2's extractors emit, or a level is unavailable
    for a NAMING reason rather than an evidential one — which would read as thin
    evidence and be a wiring bug."* ★ Measured: the rubrics require prefixes
    `con. debt. cap. shr. ngp. acc. cmp.` and **not one of those prefixes exists**
    in the 74 ids the 15 E-blocks emit (`cc. dm. ca. sc. ng. rf. cx.` …).

    ⚠ This test asserts the CURRENT, BROKEN state deliberately. It fails the
    moment the vocabularies are reconciled — at which point it must be rewritten
    to assert the fixed state, and `DX-85` closed.
    """
    import pathlib
    import re

    from src.fundamental.scorecard.rubrics.b43_v1 import E

    doc = pathlib.Path(
        "sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md"
    ).read_text(encoding="utf-8")
    emitted = set()
    for m in re.finditer(r"^## E-\d+ ·.*?\n+```text\n(.*?)```", doc, re.S | re.M):
        emitted.update(re.findall(r"^\s{2,}([a-z]{2,4}\.[a-z_]+)\s", m.group(1), re.M))
    matched = {v for v in E.values() if v in emitted}
    assert matched == {"seg.revenue", "seg.op_income", "gd.metric"}, (
        f"DX-85's measurement has changed: {sorted(matched)} now match. If the "
        f"vocabularies were reconciled, rewrite this test and close DX-85."
    )
