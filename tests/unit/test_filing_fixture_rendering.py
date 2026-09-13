"""`DX-35` / `DX-37` — the FIXTURE is part of the citation contract.

⚠⚠ A filing fixture is not test data that happens to be lying around: it is the
document `X-01` checks every citation against. How it renders decides whether a
**correct** reading can be proved at all — and six of the nine live-run failures
have come from `tools/convert_filing.py`.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.convert_filing import (  # noqa: E402
    _PAGE_FOOTER,
    _PAGE_HEADER,
    strip_page_furniture,
)

FIXTURES = REPO / "tests_src/fixtures/filings"


def test_page_furniture_is_stripped_by_whole_lines_only():
    """★ The strip must be able to remove furniture and NOTHING else."""
    text = ("We have also signed a non-binding term sheet with the State of\n"
            "35 | 2025 Q3 10-Q\n"
            "Table of Contents\n"
            "New York that provides for up to $5.5 billion\n")
    out = strip_page_furniture(text)
    assert "35 | 2025 Q3 10-Q" not in out
    assert _PAGE_HEADER not in out
    assert "with the State of" in out and "New York that provides" in out


def test_the_strip_never_touches_a_line_that_carries_prose():
    """⚠⚠ The guard that keeps this from eating the document.

    ★ `_PAGE_FOOTER` is anchored at BOTH ends, so a sentence that merely
    contains the pattern survives. A substring match here would silently delete
    real text, and the deletion would look exactly like a model hallucination
    when `X-01` later refused the quote.
    """
    keep = "as of page 35 | 2025 Q3 10-Q the balance was $5,069\n"
    assert strip_page_furniture(keep) == keep
    assert not _PAGE_FOOTER.match(keep)
    # ★ A row of a segment table must never match, whatever it holds.
    row = "CNBU | $5,069 | $2,573 | $14,028 | $6,495\n"
    assert strip_page_furniture(row) == row


def test_the_strip_is_idempotent():
    """⚠ It runs on every conversion; a second pass must be a no-op."""
    once = strip_page_furniture("a\n35 | 2025 Q3 10-Q\nTable of Contents\nb\n")
    assert strip_page_furniture(once) == once


@pytest.mark.parametrize("name", ["MU_FY2025Q3_10Q", "AMD_FY2025Q3_10Q"])
def test_the_committed_fixtures_carry_no_page_furniture(name):
    """⛔⛔ `DX-35` — the sentence that a page break cut in half.

    MU's filing reads *"…term sheet with the State of"* / `35 | 2025 Q3 10-Q` /
    `Table of Contents` / *"New York…"*. The model quoted the sentence the way a
    person reads it — correctly — and `X-01` refused the citation because that
    string is not in the document. ★★★ Because `X-01` ABORTS, four dead items
    took the other 47 with them: a $0.6377 call parsed to nothing.

    ⚠ This test FAILS until the fixtures are re-rendered. That is deliberate:
    the converter is fixed, the two `.txt` files are not, and a green suite
    would hide a pending manual step.
    """
    text = (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
    offenders = [ln for ln in text.splitlines()
                 if _PAGE_FOOTER.match(ln) or ln.strip() == _PAGE_HEADER]
    assert not offenders, (
        f"{name}.txt still holds {len(offenders)} lines of page furniture, so a "
        "sentence spanning a page break cannot be quoted (DX-35). Re-render it:\n"
        "    python3 -c \"import sys;sys.path.insert(0,'.');"
        "from tools.convert_filing import strip_page_furniture as f;"
        "import pathlib;p=pathlib.Path('tests_src/fixtures/filings/"
        f"{name}.txt');p.write_text(f(p.read_text()))\""
    )


def test_dx37_the_span_end_comes_from_the_locator_not_the_quote_length():
    """⚠⚠ `DX-37` — `start + len(quote)` is only right for an EXACT match.

    ★★ `_locate` also matches under whitespace normalisation, and there the
    document's span is a DIFFERENT LENGTH from the quote. Using the quote's
    length cuts the span short, and `X-01` ① then rejects a citation that is
    perfectly good — blaming the model for our arithmetic.

    ⚠ It was LATENT until `DX-35`'s strip created the `\\n\\n\\n` runs that
    expose it: measured 0 of MU's 60 and 0 of AMD's 41 recorded spans change.
    ★ One defect's fix uncovered another that had been there all along.
    """
    from tools.run_extraction_once import _locate

    doc = "with the State of\n\n\nNew York that provides for up to $5.5 billion"
    quote = "with the State of\nNew York that provides for"
    start, end = _locate(doc, quote)
    assert start == 0
    assert end != start + len(quote), "the lengths must differ, or this proves nothing"
    assert doc[start:end].split() == quote.split()


# ═══════════════════════════════════════════════════════════════════════════
# ⛔⛔ `DX-102` — the fixture's own annotations were INSIDE every bundle
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("name", ["MU_FY2025Q3_10Q", "AMD_FY2025Q3_10Q"])
def test_dx_102_the_fixture_carries_no_repo_annotation_and_the_sidecar_does(name):
    """★ Moved to `<NAME>.meta.txt` 2026-09-13 (approved). Measured first: 0 of
    1,980 recorded extraction quotes and no judgement answer cited the header."""
    from tools.run_extraction_once import REPO_ANNOTATION_MARKERS

    text = (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
    meta = (FIXTURES / f"{name}.meta.txt").read_text(encoding="utf-8")
    assert not [m for m in REPO_ANNOTATION_MARKERS if m in text]
    assert "PROVENANCE — do not edit below this header" in meta
    first = next(i for i, ln in enumerate(text.split("\n")) if ln.strip())
    assert all(not ln.strip() for ln in text.split("\n")[:first]), "the header's place is whitespace only"
    assert first >= 50, "the whitespace keeps pre-move citations valid"


def test_dx_102_line_citations_made_BEFORE_the_move_still_resolve():
    """★ The golden `source` fields and the L3 log cite these MU line numbers;
    deleting the header would have shifted every one by 57."""
    lines = (FIXTURES / "MU_FY2025Q3_10Q.txt").read_text(encoding="utf-8").split("\n")
    assert lines[1045 - 1].startswith("As of May 29, 2025 and August 29, 2024, customer prepayments")
    assert lines[1229 - 1].startswith("Gross margin | 3,508 | 38%")
    assert lines[882 - 1].startswith("Our Board of Directors has authorized the discretionary repurchase")


def test_dx_102_build_bundle_REFUSES_a_fixture_that_carries_the_header_again(tmp_path, monkeypatch):
    """⚠ The CALLER, not just the marker list (`DX-82`)."""
    import tools.run_extraction_once as rx

    bad = tmp_path / "X.txt"
    bad.write_text("=====\nPROVENANCE — do not edit below this header, and do not edit the body at all.\n"
                   "Total revenue was $9,301 million.\n", encoding="utf-8")
    monkeypatch.setattr(rx, "FILING", bad)
    with pytest.raises(ValueError, match="DX-102"):
        rx.build_bundle()
    assert "PROVENANCE" not in rx.__dict__["FILINGS"]["MU"]["path"]


@pytest.mark.parametrize("name", ["MU_FY2025Q3_10Q", "AMD_FY2025Q3_10Q"])
def test_dx_102_character_OFFSETS_are_preserved_by_the_move(name):
    """⚠⚠ Found the hard way: a first version replaced the header with blank
    LINES, which kept line numbers and shifted every character offset — and an
    AMD golden selector pins `@22633:22914`. ★ The header's place is whitespace
    of EXACTLY its length with EXACTLY its newlines, so the header placed back
    over it restores the pre-move file character for character."""
    header = (FIXTURES / f"{name}.meta.txt").read_text(encoding="utf-8").split("\n\n", 1)[1][:-1]
    text = (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
    blank = text[:len(header)]
    assert blank.strip() == "" and text[len(header):len(header) + 1] == "\n"
    assert blank.count("\n") == header.count("\n")
    assert [len(a) for a in blank.split("\n")] == [len(b) for b in header.split("\n")]
