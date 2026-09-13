"""⛔ `DX-97` — an item about ANOTHER company may not name the registrant.

★★★ Measured 2026-09-12: `E-13` returned 37 items that ALL passed `X-01` and
were ALL Micron's own fabs, with `cx.competitor = "Micron Technology, Inc."`.
`X-01` proves the words are in the filing; it cannot prove they answer the item.
"""

from __future__ import annotations

import pathlib
from datetime import date

import pytest

from src.fundamental.bundle.models import BundlePart, EvidenceBundle
from src.fundamental.errors import SubjectIsRegistrantError
from src.fundamental.filings.extract import item, not_found, run_extraction
from src.fundamental.filings.models import ExtractionResult
from src.fundamental.filings.subject import (
    assert_subject_is_not_registrant,
    names_registrant,
    registrant_name,
)
from src.fundamental.prompts.registry import PromptRegistry, block

FIXTURES = pathlib.Path("tests_src/fixtures/filings")
ACC = "0000723125-25-000021"
COVER = ("Commission file number 1-10658\n\nMicron Technology, Inc.\n"
         "(Exact name of registrant as specified in its charter)\n"
         "Samsung Electronics Co., Ltd. announced a new fab.\n")


def _bundle(text: str = COVER) -> EvidenceBundle:
    return EvidenceBundle(ticker="MU", as_of=date(2025, 6, 26),
                          parts=(BundlePart("filing", {"accession_id": ACC}, text),))


def _competitor(value: str):
    start = COVER.index(value)
    return item("cx.competitor", value=value, unit="", quote=value,
                accession_id=ACC, offset=(start, start + len(value)))


@pytest.mark.parametrize(("ticker", "expected"), [
    ("MU", "Micron Technology, Inc."),
    ("AMD", "ADVANCED MICRO DEVICES, INC."),
])
def test_the_registrant_is_read_from_the_REAL_cover_page(ticker, expected):
    text = (FIXTURES / f"{ticker}_FY2025Q3_10Q.txt").read_text(encoding="utf-8")
    assert registrant_name(text) == expected


def test_a_filing_with_no_cover_line_REFUSES_rather_than_guessing():
    with pytest.raises(SubjectIsRegistrantError, match="no cover-page registrant"):
        registrant_name("Total revenue was $9,301 million.")


@pytest.mark.parametrize(("value", "is_self"), [
    ("Micron Technology, Inc.", True),       # ⛔ the measured failure, verbatim
    ("Micron", True),
    ("MICRON TECHNOLOGY", True),
    ("MU", True),
    ("we", True),
    ("Samsung Electronics Co., Ltd.", False),
    ("SK hynix Inc.", False),
    ("Kioxia Holdings Corporation", False),
    ("Micronesia Power Co.", False),         # ⚠ a prefix is not the name
])
def test_names_registrant(value, is_self):
    assert names_registrant(value, "Micron Technology, Inc.", "MU") is is_self


def test_amd_a_different_company_sharing_a_FIRST_word_is_not_the_registrant():
    """⚠ `"Advanced"` alone would be a false positive on half the industry."""
    reg = "ADVANCED MICRO DEVICES, INC."
    assert names_registrant("Advanced Micro Devices", reg, "AMD")
    assert not names_registrant("Advanced Semiconductor Engineering, Inc.", reg, "AMD")


def test_an_E13_result_naming_the_registrant_as_its_competitor_is_REFUSED_whole():
    result = ExtractionResult("E-13", "h", (_competitor("Micron Technology, Inc."),))
    with pytest.raises(SubjectIsRegistrantError, match="1 of 1"):
        assert_subject_is_not_registrant([result], _bundle())


def test_a_real_competitor_and_a_not_found_pass():
    ok = ExtractionResult("E-13", "h", (_competitor("Samsung Electronics Co., Ltd."),
                                        not_found("cx.competitor", note="none")))
    assert_subject_is_not_registrant([ok], _bundle())


def test_a_block_that_names_no_other_company_needs_no_cover_page():
    """★ The guard is not a new precondition on every extraction."""
    no_cover = _bundle("Capital expenditures were $3,000 million.")
    q = "Capital expenditures were $3,000 million."
    e07 = ExtractionResult("E-07", "h", (item("ca.capex", value="3,000", unit="USD m",
                                              quote=q, accession_id=ACC, offset=(0, len(q))),))
    assert_subject_is_not_registrant([e07], no_cover)


class _Seam:
    def __init__(self, registry):
        self._registry = registry

    def call(self, **_kw):
        return "<canned>"


def test_CALLER_run_extraction_aborts_on_it():
    """★ `DX-82`'s lesson — the pure guard is tested above; this proves the
    runner every live extraction goes through actually applies it."""
    reg = PromptRegistry()
    reg.register(block("E-13", "v1", "extraction", "Competitor capacity."))
    with pytest.raises(SubjectIsRegistrantError):
        run_extraction(_Seam(reg), block_ids=[("E-13", "v1")], bundle=_bundle(),
                       run_id="r", parse=lambda _c: [_competitor("Micron Technology, Inc.")])


def test_an_all_not_found_E13_needs_no_cover_page_either():
    """★ Found by mutation: `not_found` names no company, so it must not demand
    a registrant to compare against — an empty E-13 on a bundle without a cover
    page is a correct answer, not a refusal."""
    empty = ExtractionResult("E-13", "h", (not_found("cx.competitor", note="none"),))
    assert_subject_is_not_registrant([empty], _bundle("Capital expenditures were $3,000 million."))
