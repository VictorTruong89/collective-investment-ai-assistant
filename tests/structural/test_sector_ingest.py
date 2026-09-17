"""The memory sector file — `RA-98`…`RA-102`, `DX-117`, `DX-119`.

★ The guarantees pinned here: the source list is FIXED and versioned, every source on it is
visited, a source that yields nothing becomes an omission WITH ITS REASON, `INV-1` holds per
document, and the subject guard protects the company being ANALYSED rather than whichever
company happens to have issued the document.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import date

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
CONFIG = REPO / "config/sector/memory_v1.yaml"
INDUSTRY = REPO / "tests_src/fixtures/industry"
AS_OF = date(2025, 6, 26)


def test_the_source_list_is_the_peer_set_victor_decided_and_says_what_it_excludes():
    """★ `RA-98` — the list is the artifact that gets reviewed. ⚠ An exclusion with no reason
    is indistinguishable from an oversight, which is where a view hides."""
    doc = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert doc["source_list_version"] == "memory.v1"
    assert [s["source_id"] for s in doc["sources"]] == ["sndk-edgar", "skhynix-ir", "samsung-ir"]
    excluded = {e["subject"]: e["reason"] for e in doc["excluded"]}
    assert any("Kioxia" in s for s in excluded) and any("YMTC" in s for s in excluded)
    for subject, reason in excluded.items():
        assert len(reason.split()) >= 8, f"{subject} is excluded without a stated reason"


@pytest.mark.parametrize("source_id", ["sndk-edgar", "skhynix-ir", "samsung-ir"])
def test_every_recorded_document_carries_its_provenance_in_a_SIDECAR(source_id):
    """`DX-102`'s rule, one domain over: a provenance header INSIDE the text would be
    quotable as if the company had written it. ★ And the hash proves the text is the one
    whose date and URL are recorded."""
    (meta_path,) = (INDUSTRY / source_id).glob("*.meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    text = meta_path.with_suffix("").with_suffix(".txt").read_text(encoding="utf-8")
    assert meta["sha256"] == "sha256:" + hashlib.sha256(text.encode()).hexdigest()
    for field in ("url", "published_date", "published_date_source", "subject", "converter"):
        assert meta[field], f"{source_id} records no {field}"
    assert date.fromisoformat(meta["published_date"]) <= AS_OF
    assert "PROVENANCE" not in text[:2000] and "do not edit" not in text[:2000].lower()


def test_the_skhynix_document_carries_no_AI_SUMMARY_from_the_site():
    """⚠⚠ Found on the first fetch, 2026-09-15: the newsroom page ships the SITE'S OWN
    generated summary above the release. ★ It is not the company's words, and `X-01` would
    happily verify a quote taken from it — the `DX-102` failure with a different author."""
    (doc,) = (INDUSTRY / "skhynix-ir").glob("*.txt")
    text = doc.read_text(encoding="utf-8")
    assert "AI Summary" not in text
    assert "April 24, 2025" in text and "Capex Discipline" in text     # the release itself
    (meta,) = (INDUSTRY / "skhynix-ir").glob("*.meta.json")
    assert any("AI Summary" in r for r in json.loads(meta.read_text())["removed"])


def _ingest(as_of=AS_OF):
    from src.fundamental.sector.ingest import ingest
    from tools.ingest_sector_file import load_source_list, poller

    source_list, _excluded = load_source_list(CONFIG)
    return ingest(source_list, poll=poller(as_of), as_of=as_of, file_version=1)


def test_ra_98_every_source_is_visited_and_the_records_are_date_sorted():
    sector = _ingest()
    assert {r.source_id for r in sector.records} == {"sndk-edgar", "skhynix-ir", "samsung-ir"}
    assert [r.date for r in sector.records] == sorted(r.date for r in sector.records)
    assert not sector.omissions
    assert all(len(r.quote) > 5_000 for r in sector.records), "the document travels whole"


def test_inv_1_a_document_published_after_the_as_of_is_OMITTED_with_its_reason():
    """⚠ Not dropped: `RA-98` — a skipped source must be expressible only as an omission."""
    sector = _ingest(as_of=date(2025, 4, 25))       # only SK hynix (2025-04-24) is knowable
    assert [r.source_id for r in sector.records] == ["skhynix-ir"]
    omitted = {o.source_id: o.reason for o in sector.omissions}
    assert set(omitted) == {"sndk-edgar", "samsung-ir"}
    assert all("INV-1" in reason for reason in omitted.values())


def test_the_sector_bundle_is_one_pinned_part_carrying_every_document(tmp_path):
    from tools.run_extraction_once import sector_bundle

    sector = _ingest()
    path = tmp_path / "sector.json"
    path.write_text(json.dumps(sector.to_json_obj()), encoding="utf-8")
    bundle = sector_bundle(path, ticker="MU")
    (part,) = bundle.parts
    assert part.kind == "sector_file" and part.pins["industry"] == "memory_semiconductors"
    assert bundle.ticker == "MU" and bundle.as_of == AS_OF
    for marker in ("Flash Ventures", "Capex Discipline", "SAMSUNG"):
        assert marker in part.content
    assert sector_bundle(path, ticker="MU").bundle_hash == bundle.bundle_hash   # RA-4


# ═══════════════════════════════════════════════════════════════════════════
# `DX-119` — the guard protects the SUBJECT, not the document's issuer
# ═══════════════════════════════════════════════════════════════════════════

def _result(value: str):
    from src.fundamental.filings.extract import item
    from src.fundamental.filings.models import ExtractionResult

    return [ExtractionResult("E-13", "sha256:b", (item(
        "cx.competitor", value=value, unit="name", quote=f"{value} announced capacity",
        accession_id="none", offset=[0, 10]),))]


def _sector_only_bundle():
    from src.fundamental.bundle.assemble import sector_file
    from src.fundamental.bundle.models import EvidenceBundle
    return EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(sector_file(_ingest()),))


@pytest.mark.parametrize(("value", "refused"), [
    ("Samsung Electronics Co., Ltd.", False),
    ("SK hynix Inc.", False),
    ("Micron Technology, Inc.", True),          # ⛔ the analysed company is not its own rival
    ("Micron", True),
])
def test_dx_119_over_an_industry_bundle_the_DECLARED_subject_is_what_may_not_be_named(value,
                                                                                      refused):
    from src.fundamental.errors import SubjectIsRegistrantError
    from src.fundamental.filings.subject import assert_subject_is_not_registrant

    bundle = _sector_only_bundle()
    if refused:
        with pytest.raises(SubjectIsRegistrantError):
            assert_subject_is_not_registrant(_result(value), bundle,
                                             subject="Micron Technology, Inc.")
    else:
        assert_subject_is_not_registrant(_result(value), bundle,
                                         subject="Micron Technology, Inc.")


def test_dx_119_without_a_declared_subject_an_industry_bundle_REFUSES_rather_than_guessing():
    """★ `P5` — no cover page and no declared subject means the guard cannot tell a rival
    from the analysed company, and it will not assume (the `DX-97` failure's shape)."""
    from src.fundamental.errors import SubjectIsRegistrantError
    from src.fundamental.filings.subject import assert_subject_is_not_registrant

    with pytest.raises(SubjectIsRegistrantError, match="no subject was declared"):
        assert_subject_is_not_registrant(_result("Samsung Electronics Co., Ltd."),
                                         _sector_only_bundle())


def test_the_runner_declares_a_subject_for_every_ticker_it_can_run():
    """⚠ A ticker with no declared subject would run an industry extraction unguarded."""
    from tools.run_extraction_once import FILINGS, SUBJECT_NAMES

    assert set(SUBJECT_NAMES) >= set(FILINGS)


def test_a_sector_run_DECLARES_its_subject_in_the_plan(monkeypatch, capsys):
    """⚠ Found by mutation: nothing asserted the runner actually passes the subject. A
    `--sector` run that declared none would extract competitors unguarded (`DX-119`)."""
    import sys

    from tools import run_extraction_once as r

    sector = REPO / ".state/sector/memory_v1_2025-06-26.json"
    if not sector.exists():                      # built by tools/ingest_sector_file.py
        pytest.skip("no ingested sector file in .state")
    monkeypatch.setattr(sys, "argv", ["x", "--dry-run", "--block", "E-13",
                                      "--sector", str(sector)])
    assert r.main() == 0
    out = capsys.readouterr().out
    assert "subject    : Micron Technology, Inc. (declared" in out


def test_dx_121_a_quote_from_the_SECTOR_FILE_resolves_and_verifies(tmp_path):
    """⛔ Found by the first live industry E-13 ($0.52): every item was stamped with MICRON's
    accession and spans resolved only against `filing` parts, so a perfectly good industry
    citation could not be checked. ★ The dry run cannot catch this — it never verifies."""
    from types import SimpleNamespace

    from src.fundamental.claims.models import sector_citation
    from src.fundamental.claims.verify import x01_verify_extraction
    from tools.run_extraction_once import parse_items, sector_bundle

    sector = _ingest()
    path = tmp_path / "sector.json"
    path.write_text(json.dumps(sector.to_json_obj()), encoding="utf-8")
    bundle = sector_bundle(path, ticker="MU")
    citation = sector_citation(bundle.parts[0].pins)
    assert citation == "sector:memory_semiconductors:v1"

    # ⚠ X-01 ② — the VALUE must appear in its own quote; the first draft of this test used a
    #   quote that did not contain it, and the guard refused it (correctly).
    quote = "SK hynix Announces 1Q25 Financial Results"
    call = SimpleNamespace(parsed={"items": [
        {"evidence_id": "cx.competitor", "value": "SK hynix", "unit": "name", "quote": quote},
    ]})
    items = parse_items(call, bundle.parts[0].content, accession_id=citation)
    report = x01_verify_extraction(bundle, items)          # ★ would have raised before the fix
    assert report.checked == 1
    assert items[0].span.resolve(bundle) == quote

    # ⚠ And a citation naming the analysed company's filing still does NOT resolve here.
    from src.fundamental.errors import SpanUnresolvableError
    wrong = parse_items(call, bundle.parts[0].content, accession_id="0000723125-25-000021")
    with pytest.raises(SpanUnresolvableError):
        wrong[0].span.resolve(bundle)


# ═══════════════════════════════════════════════════════════════════════════
# `DX-122` — `X-01` ② and a value the document cannot contain
# ═══════════════════════════════════════════════════════════════════════════

def test_dx_122_the_declared_classification_values_are_the_blocks_own_words():
    """`MP-5`/`RA-13` — the closed set is copied from `E-13`'s prompt; a wording change there
    must not leave this exemption describing a set the model was never offered."""
    from src.fundamental.claims.classification import CLASSIFICATION_VALUES
    from src.fundamental.prompts.e_blocks import BLOCKS

    text = " ".join(BLOCKS["E-13"][0]().text.split())
    for evidence_id, values in CLASSIFICATION_VALUES.items():
        assert evidence_id in text, f"{evidence_id} is not an item E-13 asks for"
        for value in values:
            assert value in text, f"{evidence_id}: {value!r} is not in E-13's own list"


def _classified(value: str, quote: str, bundle):
    from src.fundamental.claims.models import sector_citation
    from src.fundamental.filings.extract import item

    text = bundle.parts[0].content
    start = text.index(quote)
    return item("cx.status", value=value, unit="status", quote=quote,
                accession_id=sector_citation(bundle.parts[0].pins),
                offset=(start, start + len(quote)))


def test_dx_122_a_status_label_verifies_on_its_DECLARED_SET_and_an_invented_one_refuses(tmp_path):
    """⛔ Measured: `cx.status` = "under construction" cited a gross-profit sentence and the run
    aborted — the label is not in the document and never will be. ★ ① still holds in full."""
    from src.fundamental.claims.verify import x01_verify_extraction
    from src.fundamental.errors import ValueNotInSpanError
    from tools.run_extraction_once import sector_bundle

    sector = _ingest()
    path = tmp_path / "sector.json"
    path.write_text(json.dumps(sector.to_json_obj()), encoding="utf-8")
    bundle = sector_bundle(path, ticker="MU")
    quote = "Construction of the K1 facility"          # any span that resolves
    quote = next(q for q in ("Flash Ventures", "Capex Discipline") if q in bundle.parts[0].content)

    report = x01_verify_extraction(bundle, [_classified("under construction", quote, bundle)])
    assert report.checked == 1                          # ② replaced by the declared set
    with pytest.raises(ValueNotInSpanError, match="must be one of"):
        x01_verify_extraction(bundle, [_classified("nearly finished", quote, bundle)])


def test_dx_122_a_NON_classification_item_still_needs_its_value_in_the_quote(tmp_path):
    """⚠ The exemption is per declared item — it must not become a hole for every item."""
    from src.fundamental.claims.models import sector_citation
    from src.fundamental.claims.verify import x01_verify_extraction
    from src.fundamental.errors import ValueNotInSpanError
    from src.fundamental.filings.extract import item
    from tools.run_extraction_once import sector_bundle

    sector = _ingest()
    path = tmp_path / "sector.json"
    path.write_text(json.dumps(sector.to_json_obj()), encoding="utf-8")
    bundle = sector_bundle(path, ticker="MU")
    text = bundle.parts[0].content
    quote = "Flash Ventures"
    start = text.index(quote)
    bad = item("cx.capacity", value="300-millimetre wafers", unit="wafers", quote=quote,
               accession_id=sector_citation(bundle.parts[0].pins),
               offset=(start, start + len(quote)))
    with pytest.raises(ValueNotInSpanError):
        x01_verify_extraction(bundle, [bad])
