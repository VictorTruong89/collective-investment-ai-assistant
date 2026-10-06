"""✏ 2026-10-04 — bundles of SEVERAL documents (`L3` §2.1p row 6: `E-03`, `E-08`).

⚠ `E-03` compares two annual filings whose unchanged risk factors are word-for-word the same,
so a quote cannot be attributed by searching for it: the answer must NAME the document it
quoted, and the quote must resolve in THAT document (`X-01` ①, which already resolves a span
by its accession — `EvidenceSpan.resolve`).
"""
import pytest

import tools.run_extraction_once as r


def _call(rows):
    return {"items": rows}


DOCS = {"acc-new": "Risk: we may lose a customer. Only new text here.",
        "acc-old": "Risk: we may lose a customer."}


def _empty(accession):
    """A `not_found` naming a document as read and empty — `DX-149` ⓒ's other way to count."""
    return {"evidence_id": "rf.removed", "status": "not_found", "quote": "",
            "note": f"{accession} — nothing here"}


def test_a_quote_resolves_in_the_document_it_NAMES():
    it, _nf = r.parse_items(_call([{"evidence_id": "rf.added", "status": "found",
                                    "value": "Only new text here",
                                    "quote": "Only new text here", "accession_id": "acc-new"},
                                   _empty("acc-old")]), documents=DOCS)
    assert it.span.accession_id == "acc-new"


def test_the_same_sentence_in_both_documents_is_cited_where_the_answer_SAYS():
    it, _nf = r.parse_items(_call([{"evidence_id": "rf.reworded", "status": "found",
                                    "value": "we may lose a customer",
                                    "quote": "we may lose a customer", "accession_id": "acc-old"},
                                   _empty("acc-new")]), documents=DOCS)
    assert it.span.accession_id == "acc-old"
    assert DOCS["acc-old"][it.span.start:it.span.end] == "we may lose a customer"


@pytest.mark.parametrize("accession", [None, "acc-elsewhere"])
def test_a_multi_document_answer_that_names_no_KNOWN_document_raises(accession):
    row = {"evidence_id": "rf.added", "status": "found", "value": "x",
           "quote": "Only new text here", **({"accession_id": accession} if accession else {})}
    with pytest.raises(ValueError, match="names no document"):
        r.parse_items(_call([row]), documents=DOCS)


def test_a_quote_not_in_the_NAMED_document_raises_even_if_another_holds_it():
    row = {"evidence_id": "rf.added", "status": "found", "value": "Only new text here",
           "quote": "Only new text here", "accession_id": "acc-old"}
    with pytest.raises(ValueError, match="not in the bundle"):
        r.parse_items(_call([row]), documents=DOCS)


def test_the_answer_schema_lets_an_item_name_its_document():
    from tools.anthropic_transport import extraction_tool
    props = extraction_tool(("rf.added",))["input_schema"]["properties"]["items"]["items"]
    assert "accession_id" in props["properties"]
    assert "accession_id" not in props["required"]          # one-document bundles omit it


def test_the_10k_risk_factor_set_is_cut_at_its_HEADINGS():
    bundle = r.document_set_bundle("mu-10k-risk-factors")
    accs = sorted(p.pins["accession_id"] for p in bundle.parts)
    assert accs == ["0000723125-23-000054", "0000723125-24-000027"]
    for p in bundle.parts:
        assert p.content.startswith("ITEM 1A. RISK FACTORS")
        assert "ITEM 1B. UNRESOLVED STAFF COMMENTS" not in p.content
    assert str(bundle.as_of) == "2025-06-26"


def test_the_form4_set_holds_every_listed_form_and_none_filed_on_the_as_of_day():
    import json
    bundle = r.document_set_bundle("mu-form4-2025q3")
    index = json.loads((r.REPO / r.DOCUMENT_SETS["mu-form4-2025q3"]["index"]).read_text())
    assert len(bundle.parts) == len(index["forms"]) == 20
    assert all(f["filed"] < "2025-06-26" for f in index["forms"])
    assert all(p.pins["form"] == "4" for p in bundle.parts)


def test_dx_148_the_parse_states_the_MAPPED_label_beside_the_verbatim_code():
    (it,) = r.parse_items(_call([{"evidence_id": "in.type", "status": "found", "value": "S(1)",
                                  "quote": "Common Stock | 06/02/2025 | S(1)",
                                  "accession_id": "f4"}]),
                          documents={"f4": "x Common Stock | 06/02/2025 | S(1) | 1,000"})
    assert it.value == "S(1)" and "label: sale" in it.note


def test_the_same_figure_from_two_DOCUMENTS_is_two_items_not_a_collision():
    """✏ 2026-10-04 — two Form 4s for one day (two insiders) gave `in.shares` twice with one
    `(id, qualifier, period)`, and `MP-18` refused the run. ★ A figure from another filing is
    another figure: in a bundle of several documents the cited document is part of identity."""
    docs = {"f4-a": "Common Stock | 03/05/2025 | S | 1,000", "f4-b": "Common Stock | 03/05/2025 | S | 1,000"}
    rows = [{"evidence_id": "in.shares", "status": "found", "value": "1,000",
             "quote": "03/05/2025 | S | 1,000", "accession_id": a, "period_end": "2025-03-05"}
            for a in docs]
    a, b = r.parse_items(_call(rows), documents=docs)
    assert a.identity != b.identity


def test_one_document_still_REFUSES_two_values_for_one_figure_identity():
    """⚠ The `MP-18` guard is unchanged where it matters: within ONE document, two values
    claiming one `(id, qualifier, period)` still collide."""
    from src.fundamental.filings.extract import item
    one = [item("seg.revenue", value=v, unit="USD", quote=v, accession_id="acc", offset=(0, 5),
                period_end="2025-05-29") for v in ("5,069", "5,070")]
    assert one[0].identity == one[1].identity


# ── `DX-149` ⓐ + ⓒ (Victor, 2026-10-04) ──────────────────────────────────────

def test_dx_149c_a_multi_document_answer_that_leaves_a_document_UNCITED_raises():
    """ⓒ — `X-01` proves what is there; this proves nothing was silently left out. A document
    counts as read when an item cites it, or a `not_found` names it with a reason."""
    rows = [{"evidence_id": "rf.added", "status": "found", "value": "Only new text here",
             "quote": "Only new text here", "accession_id": "acc-new"}]
    with pytest.raises(ValueError, match="acc-old"):
        r.parse_items(_call(rows), documents=DOCS)
    named = rows + [{"evidence_id": "rf.removed", "status": "not_found", "quote": "",
                     "note": "acc-old — nothing removed"}]
    r.parse_items(_call(named), documents=DOCS)


def test_dx_149a_one_document_of_a_set_is_its_OWN_single_document_bundle():
    bundle = r.document_set_bundle("mu-form4-2025q3", only="0001562180-25-002125")
    assert [p.pins["accession_id"] for p in bundle.parts] == ["0001562180-25-002125"]
    with pytest.raises(KeyError):
        r.document_set_bundle("mu-form4-2025q3", only="not-in-the-set")


def test_dx_149a_per_document_runs_EVERY_document_once(monkeypatch):
    seen = []
    monkeypatch.setattr(r, "_run_one", lambda argv: seen.append(argv) or 0)
    assert r.main(["--dry-run", "--block", "E-08", "--document-set", "mu-form4-2025q3",
                   "--per-document"]) == 0
    docs = [a[a.index("--document") + 1] for a in seen]
    assert len(docs) == 20 == len(set(docs))
    assert all("--per-document" not in a for a in seen)


def test_dx_149a_one_documents_FAILURE_does_not_stop_the_others(monkeypatch, capsys):
    """⚠ An `X-01` refusal RAISES; uncaught, it would end the loop at that document and leave
    the rest unread — `DX-149` again, one level up. Each failure is named, the run is non-zero."""
    calls = []

    def one(argv):
        calls.append(argv)
        if len(calls) == 3:
            raise ValueError("'in.price': quoted text is not in the bundle")
        return 0
    monkeypatch.setattr(r, "_run_one", lambda argv: r._guarded(one, argv))
    assert r.main(["--dry-run", "--block", "E-08", "--document-set", "mu-form4-2025q3",
                   "--per-document"]) == 1
    assert len(calls) == 20 and "FAILED" in capsys.readouterr().out
