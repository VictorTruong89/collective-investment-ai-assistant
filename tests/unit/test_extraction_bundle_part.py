"""★★★ `DX-85`ⓒ — the `extraction` bundle part kind (approved 2026-09-12).

⚠⚠ Before it existed a judgement bundle could not carry `seg.revenue` even in
principle: raw filing text holds the facts, not the extraction (`MP-4`), so
`RA-32` refused every rubric block. These pin what the part may and may not
claim — above all that its declared evidence ids ARE its verified found items.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.fundamental.bundle import models
from src.fundamental.bundle.assemble import extractions
from src.fundamental.bundle.models import BundlePart, EvidenceBundle
from src.fundamental.errors import BundleInconsistentError
from src.fundamental.filings.extract import ExtractionPass, item, not_found
from src.fundamental.filings.models import ExtractionResult
from src.fundamental.scorecard.availability import evidence_ids_in, require_levels

ACC = "0000723125-25-000021"
TEXT = ("Capital expenditures were $3,000 million. "
        "Diluted weighted-average shares were 1,129 million.")


def _filing_bundle() -> EvidenceBundle:
    return EvidenceBundle(ticker="MU", as_of=date(2025, 6, 26),
                          parts=(BundlePart("filing", {"accession_id": ACC}, TEXT),))


def _verified_pass(bundle: EvidenceBundle) -> ExtractionPass:
    """A pass built the way `run_extraction` builds one: results, then X-01."""
    from src.fundamental.claims.verify import x01_verify_extraction

    q1 = "Capital expenditures were $3,000 million."
    q2 = "Diluted weighted-average shares were 1,129 million."
    e07 = ExtractionResult("E-07", bundle.bundle_hash, (
        item("ca.capex", value="3,000", unit="millions of USD", quote=q1,
             accession_id=ACC, offset=(0, len(q1))),
        not_found("ca.buyback", note="no repurchase disclosed"),
    ))
    start = TEXT.index(q2)
    e10 = ExtractionResult("E-10", bundle.bundle_hash, (
        item("sc.diluted", value="1,129", unit="millions of shares", quote=q2,
             accession_id=ACC, offset=(start, start + len(q2))),
    ))
    report = x01_verify_extraction(bundle, [*e07.items, *e10.items])
    return ExtractionPass(results=(e07, e10), report=report)


VERSIONS = {"E-07": "v1", "E-10": "v1"}


def test_dx_85c_the_bundle_contract_declares_an_extraction_kind():
    """✅ Replaces `test_dx_85_the_bundle_contract_has_NO_part_kind…`, which
    pinned the broken state and was written to fail on this change."""
    assert models.PIN_FIELDS["extraction"] == (
        "block_id", "prompt_version", "source_bundle_hash", "run_id", "evidence_ids",
        "searched_ids")


def test_dx_85c_adding_the_kind_moves_NO_existing_bundle_hash(monkeypatch):
    """⚠⚠ The approval rested on this being a hash-contract change. ★ Measured:
    `bundle_hash` covers each part's kind, pins and content — never the table —
    so every bundle without an extraction part hashes exactly as before."""
    bundle = _filing_bundle()
    with_kind = (bundle.bundle_hash, bundle.redact(kinds=("computed",)).bundle_hash)
    without = {k: v for k, v in models.PIN_FIELDS.items() if k != "extraction"}
    monkeypatch.setattr(models, "PIN_FIELDS", without)
    rebuilt = _filing_bundle()
    assert (rebuilt.bundle_hash,
            rebuilt.redact(kinds=("computed",)).bundle_hash) == with_kind


def test_dx_85c_a_verified_pass_becomes_one_part_per_block_carrying_its_FOUND_ids():
    """★ `RA-66` — `not_found` is not evidence: `ca.buyback` is in the content
    (where the model looked) and absent from the declared ids."""
    bundle = _filing_bundle()
    parts = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="run-x")
    assert [p.pins["block_id"] for p in parts] == ["E-07", "E-10"]
    e07 = parts[0]
    assert e07.pins["evidence_ids"] == ["ca.capex"]
    assert e07.pins["source_bundle_hash"] == bundle.bundle_hash
    assert e07.pins["prompt_version"] == "v1" and e07.pins["run_id"] == "run-x"
    assert "ca.buyback" in e07.content
    assert e07.pins["searched_ids"] == ["ca.buyback", "ca.capex"]

    judged = EvidenceBundle(ticker="MU", as_of=bundle.as_of,
                            parts=(*bundle.parts, *parts))
    assert evidence_ids_in(judged) == frozenset(
        {"ca.capex", "sc.diluted",
         "searched:ca.buyback", "searched:ca.capex", "searched:sc.diluted"})


def test_dx_85c_the_part_survives_the_BLIND_view():
    """★ `RA-14` withholds anchors (`computed`), not filing-derived evidence.
    A Stage-A bundle that lost its extraction parts on redaction would refuse
    every rubric block again, silently, one step later."""
    bundle = _filing_bundle()
    parts = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    blind = EvidenceBundle(ticker="MU", as_of=bundle.as_of,
                           parts=(*bundle.parts, *parts)).redact()
    assert {"ca.capex", "sc.diluted", "searched:ca.buyback"} <= evidence_ids_in(blind)


def test_dx_85c_extraction_parts_REACH_the_gate_and_dx_98_refuses_a_partial_rubric():
    """★★★ What `DX-85` was for, end to end — and `DX-98` on top of it.

    `J-06` refused on a bare filing (no level). With `E-07`'s verified
    `ca.capex` the gate SEES the evidence — `available_levels` moves to `(0,)` —
    and `require_levels` still refuses, because a floor-only rubric is a score
    of 0 by construction (`DX-98`, decided 2026-09-12)."""
    from src.fundamental.scorecard.availability import (
        NoAvailableLevel,
        PartialRubricEvidence,
        available_levels,
    )
    from src.fundamental.scorecard.rubrics.b43_v2 import CAPITAL_ALLOCATION_V2

    bundle = _filing_bundle()
    with pytest.raises(NoAvailableLevel):
        require_levels(CAPITAL_ALLOCATION_V2, evidence_ids_in(bundle))
    parts = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    judged = EvidenceBundle(ticker="MU", as_of=bundle.as_of, parts=(*bundle.parts, *parts))
    assert available_levels(CAPITAL_ALLOCATION_V2, evidence_ids_in(judged)) == (0,)
    with pytest.raises(PartialRubricEvidence, match="cp.statement"):
        require_levels(CAPITAL_ALLOCATION_V2, evidence_ids_in(judged))


@pytest.mark.parametrize("declared", [
    ["ca.buyback", "ca.capex"],     # claims a not_found id → opens a level by assertion
    [],                             # omits a found id → closes a level for a naming reason
    ["sc.diluted", "ca.capex"],     # unsorted → one set, two hashes
])
def test_dx_85c_declared_ids_that_disagree_with_the_content_REFUSE(declared):
    bundle = _filing_bundle()
    (good, _e10) = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    with pytest.raises(ValueError, match="evidence_ids|FOUND"):
        BundlePart("extraction", {**good.pins, "evidence_ids": declared}, good.content)


def test_dx_85c_content_that_is_not_an_extraction_result_REFUSES():
    bundle = _filing_bundle()
    (good, _e10) = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    with pytest.raises(ValueError, match="not an extraction result"):
        BundlePart("extraction", good.pins, "Capital expenditures were $3,000 million.")


def test_dx_85c_an_UNVERIFIED_pass_cannot_enter_a_bundle():
    """⚠⚠ `RA-66` — *an item counts as extracted only if X-01 passed.* A pass
    whose report did not check every found item was not built by
    `run_extraction`, and must not reach a rubric."""
    from src.fundamental.claims.verify import VerificationReport

    bundle = _filing_bundle()
    good = _verified_pass(bundle)
    unverified = ExtractionPass(results=good.results, report=VerificationReport(
        checked=0, facts=0, inferences=0, assumptions=0, not_found=1))
    with pytest.raises(BundleInconsistentError, match="RA-66"):
        extractions(unverified, prompt_versions=VERSIONS, run_id="r")


def test_dx_85c_a_part_that_cannot_name_its_prompt_version_REFUSES():
    bundle = _filing_bundle()
    with pytest.raises(BundleInconsistentError, match="E-10"):
        extractions(_verified_pass(bundle), prompt_versions={"E-07": "v1"}, run_id="r")


def test_dx_85c_the_same_pass_yields_the_same_hash():
    """`RA-4` — deterministic content, so K identical passes are one bundle."""
    bundle = _filing_bundle()

    def judged():
        parts = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
        return EvidenceBundle(ticker="MU", as_of=bundle.as_of,
                              parts=(*bundle.parts, *parts)).bundle_hash
    assert judged() == judged()


def test_dx_85c_evidence_ids_given_as_a_STRING_refuses():
    """⚠ `"ca.capex"` iterates as characters; `evidence_ids_in` would then
    declare `c`, `a`, `.` … — a naming failure that reads as missing evidence."""
    bundle = _filing_bundle()
    (good, _e10) = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    with pytest.raises(ValueError, match="must be a list"):
        BundlePart("extraction", {**good.pins, "evidence_ids": "ca.capex"}, good.content)


def test_dx_99_a_NOT_FOUND_item_is_searched_but_is_NOT_evidence():
    """★★ `DX-99` — the two sets stay apart. `ca.buyback` was returned
    `not_found`: it satisfies `searched:ca.buyback` and NOT `ca.buyback`
    (`RA-66` unchanged)."""
    bundle = _filing_bundle()
    parts = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    ids = evidence_ids_in(EvidenceBundle(ticker="MU", as_of=bundle.as_of,
                                         parts=(*bundle.parts, *parts)))
    assert "searched:ca.buyback" in ids and "ca.buyback" not in ids


@pytest.mark.parametrize("searched", [
    ["ca.capex"],                                   # hides the not_found it returned
    ["ca.acquisition", "ca.buyback", "ca.capex"],   # claims a search it never returned
    "ca.capex",                                     # a string, not a list
])
def test_dx_99_searched_ids_that_disagree_with_the_content_REFUSE(searched):
    bundle = _filing_bundle()
    (good, _e10) = extractions(_verified_pass(bundle), prompt_versions=VERSIONS, run_id="r")
    with pytest.raises(ValueError, match="searched"):
        BundlePart("extraction", {**good.pins, "searched_ids": searched}, good.content)
