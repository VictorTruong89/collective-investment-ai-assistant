"""✏ 2026-10-04 (Victor) — `E-15` declared and the sector ingest moved onto it, with the
schema it needs: `sector.v2` = v1 + `value`, `unit`, `period` (`RA-100`: a column arrives by a
new version, never by editing v1).

★ What `E-15` rows become: one dated `SectorRecord` each. The model supplies the reading
(kind, subject, value, unit, period, a capacity status, a verbatim quote); WHICH source and
WHICH date are derived from the source document the quote resolves into — never asserted.
"""
from datetime import date

import pytest

from src.fundamental.sector.models import SectorFile, SectorRecord
from src.fundamental.sector.schema import (
    RECORD_FIELDS_V1,
    RECORD_FIELDS_V2,
    SCHEMA_V1,
    SCHEMA_V2,
    SCHEMAS,
)

DOC_A = "Samsung: we are adding 40,000 wafers per month of 1c DRAM, online in 2H25, subject to demand."
DOC_B = "SK hynix: no new capacity this quarter; HBM pricing for 2025 is fully booked."


def _file(records=(), version=SCHEMA_V2):
    docs = (SectorRecord(record_id="samsung-ir:2025-04-30", date=date(2025, 4, 30),
                         kind="source_document", subject="Samsung Electronics",
                         source_id="samsung-ir", quote=DOC_A),
            SectorRecord(record_id="skhynix-ir:2025-04-24", date=date(2025, 4, 24),
                         kind="source_document", subject="SK hynix",
                         source_id="skhynix-ir", quote=DOC_B))
    return SectorFile(industry="memory", as_of=date(2025, 6, 26), file_version=1,
                      source_list_version="memory_v1", records=docs + tuple(records),
                      schema_version=version)


# ── the schema ───────────────────────────────────────────────────────────────

def test_v2_is_v1_plus_three_columns_and_v1_is_untouched():
    assert (*RECORD_FIELDS_V1, "value", "unit", "period") == RECORD_FIELDS_V2
    assert SCHEMAS[SCHEMA_V1].record_fields == RECORD_FIELDS_V1
    assert SCHEMAS[SCHEMA_V1].fingerprint != SCHEMAS[SCHEMA_V2].fingerprint


def test_a_v2_file_carries_the_new_columns():
    rec = SectorRecord(record_id="r1", date=date(2025, 4, 30), kind="pricing",
                       subject="SK hynix", source_id="skhynix-ir", quote="HBM pricing",
                       value="fully booked", unit="", period="2025")
    out = _file([rec]).to_json_obj()
    assert out["schema_version"] == SCHEMA_V2
    (mine,) = [r for r in out["records"] if r["record_id"] == "r1"]
    assert mine["period"] == "2025" and mine["value"] == "fully booked"


def test_a_v1_file_REFUSES_a_record_it_has_no_column_for():
    """⚠ Silently dropping `value` on write would be `RA-100`'s defect inverted."""
    rec = SectorRecord(record_id="r1", date=date(2025, 4, 30), kind="pricing",
                       subject="SK hynix", source_id="skhynix-ir", quote="HBM pricing",
                       value="fully booked")
    with pytest.raises(ValueError, match="sector.v1"):
        _file([rec], version=SCHEMA_V1)


def test_the_bundle_rendering_of_a_v1_record_is_byte_identical():
    """★ An existing sector bundle's hash must not move because v2 exists."""
    from src.fundamental.bundle.assemble import sector_file
    v1 = sector_file(_file(version=SCHEMA_V1)).content
    assert v1.splitlines()[0].startswith("2025-04-24  source_document  SK hynix  ")
    assert "value=" not in v1


# ── E-15 ─────────────────────────────────────────────────────────────────────

def test_e15_is_declared_with_its_five_row_kinds():
    from src.fundamental.prompts.e_blocks import BLOCKS
    factory, ids, version = BLOCKS["E-15"]
    assert version == "v1" and factory().kind == "extraction"
    assert ids == ("capacity", "pricing", "inventory", "demand", "policy")


def test_the_answer_schema_can_carry_a_capacity_status():
    from tools.anthropic_transport import extraction_tool
    props = extraction_tool(("capacity",))["input_schema"]["properties"]["items"]["items"]
    assert "status_label" in props["properties"]
    assert "status_label" not in props["required"]


# ── rows → records ───────────────────────────────────────────────────────────

def _row(kind, quote, **kw):
    from src.fundamental.filings.extract import item
    return item(kind, value=kw.pop("value", "x"), unit=kw.pop("unit", ""), quote=quote,
                accession_id="sector:memory:v1", offset=(0, len(quote)),
                qualifier=kw.pop("qualifier", ""), note=kw.pop("note", ""), **kw)


def test_rows_become_records_whose_SOURCE_and_DATE_come_from_the_quoted_document():
    from src.fundamental.sector.rows import records_from_rows
    rows = [_row("capacity", "adding 40,000 wafers per month of 1c DRAM",
                 value="40,000", unit="wafers per month", qualifier="Samsung Electronics",
                 period_end="2025-12-31"),
            _row("pricing", "HBM pricing for 2025 is fully booked", value="fully booked",
                 qualifier="SK hynix")]
    out = records_from_rows(_file(version=SCHEMA_V2), rows,
                            statuses={0: "announced"}, run_id="run-x")
    cap, price = out
    assert (cap.kind, cap.source_id, cap.date, cap.status) == (
        "capacity_transition", "samsung-ir", date(2025, 4, 30), "announced")
    assert (cap.value, cap.unit) == ("40,000", "wafers per month")
    assert (price.kind, price.source_id, price.date) == ("pricing", "skhynix-ir", date(2025, 4, 24))


def test_a_capacity_row_with_no_DECLARED_status_raises():
    from src.fundamental.sector.rows import records_from_rows
    rows = [_row("capacity", "adding 40,000 wafers per month", qualifier="Samsung Electronics")]
    with pytest.raises(ValueError, match="status"):
        records_from_rows(_file(), rows, statuses={0: "probably soon"}, run_id="run-x")


def test_a_quote_found_in_NO_source_document_raises():
    from src.fundamental.sector.rows import records_from_rows
    rows = [_row("pricing", "a sentence nobody wrote", qualifier="SK hynix")]
    with pytest.raises(ValueError, match="no source document"):
        records_from_rows(_file(), rows, statuses={}, run_id="run-x")


def test_ra_98_a_document_with_no_row_and_no_stated_reason_raises():
    """★ *Skipping an item silently is how a file that contains no opinion acquires one.*"""
    from src.fundamental.sector.rows import assert_every_document_accounted
    rows = [_row("pricing", "HBM pricing for 2025 is fully booked", qualifier="SK hynix")]
    with pytest.raises(ValueError, match="samsung-ir:2025-04-30"):
        assert_every_document_accounted(_file(), rows)
    from src.fundamental.filings.extract import not_found
    accounted = rows + [not_found("capacity", note="samsung-ir:2025-04-30 — no row: an outlook only")]
    assert_every_document_accounted(_file(), accounted)


# ── the ingest step: a recorded E-15 answer → the next file version ──────────

def _answer(rows):
    import json
    return json.dumps({"items": rows})


def test_the_ingest_appends_verified_rows_as_the_NEXT_file_version_in_v2():
    from tools.ingest_sector_file import ingest_rows
    base = _file(version=SCHEMA_V1)
    text = _answer([
        {"evidence_id": "capacity", "status": "found", "qualifier": "Samsung Electronics",
         "value": "40,000", "unit": "wafers per month", "status_label": "announced",
         "quote": "adding 40,000 wafers per month of 1c DRAM"},
        {"evidence_id": "pricing", "status": "found", "qualifier": "SK hynix",
         "value": "fully booked", "quote": "HBM pricing for 2025 is fully booked"}])
    new = ingest_rows(base, text, run_id="run-e15")
    assert new.schema_version == SCHEMA_V2 and new.file_version == base.file_version + 1
    kinds = sorted(r.kind for r in new.records)
    assert kinds == ["capacity_transition", "pricing", "source_document", "source_document"]


def test_the_ingest_refuses_a_quote_X01_cannot_find():
    from tools.ingest_sector_file import ingest_rows
    text = _answer([{"evidence_id": "pricing", "status": "found", "qualifier": "SK hynix",
                     "value": "x", "quote": "words the documents never say"}])
    with pytest.raises(ValueError):
        ingest_rows(_file(version=SCHEMA_V1), text, run_id="run-e15")


def test_dx_150c_an_OMITTED_source_is_a_logged_omission_never_a_silent_gap():
    """✏ `DX-150` ⓒ (Victor, 2026-10-04): Samsung does not file in the US and its deck cannot be
    quoted verbatim, so E-15's file skips it — ★ as an `Omission` carrying the reason (`RA-98`),
    with the source list itself unchanged."""
    from src.fundamental.sector.ingest import ingest
    from tools.ingest_sector_file import CONFIG_ROOT, load_source_list, poller

    source_list, _excluded = load_source_list(CONFIG_ROOT / "memory_v1.yaml")
    file = ingest(source_list, as_of=date(2025, 6, 26), file_version=1,
                  poll=poller(date(2025, 6, 26),
                              omit={"samsung-ir": "not a US filer; deck not quotable (DX-150)"}))
    assert not [r for r in file.records if r.source_id == "samsung-ir"]
    (om,) = [o for o in file.omissions if o.source_id == "samsung-ir"]
    assert "DX-150" in om.reason and "omitted by decision" in om.reason
    assert {r.source_id for r in file.records} == {"sndk-edgar", "skhynix-ir"}
