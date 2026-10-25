"""AC-1.3c / RA-155 — a competitor's name in a sector file is the record's provenance.

⛔ Measured 2026-10-22 (`run-2026-10-22T211714-sndk-e13`): the first SNDK `E-13` aborted on
`cx.competitor` = "Micron" cited against Micron's own 10-K, which says "we". The value is true;
no span of a first-person document can contain it. ★ X-01 ① (the quote resolves) is untouched.

Tier: structural — over the real `memory_v2` documents at 2026-10-20, no model, no network.
"""
from __future__ import annotations

import json
from datetime import date

import pytest

AS_OF = date(2026, 10, 20)
MICRON_QUOTE = "In January 2026, we broke ground on our first New York fab."


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    from src.fundamental.sector.ingest import ingest
    from tools.ingest_sector_file import CONFIG_ROOT, load_source_list, poller
    from tools.run_extraction_once import sector_bundle

    source_list, _ = load_source_list(CONFIG_ROOT / "memory_v2.yaml")
    sector = ingest(source_list, poll=poller(AS_OF, omit={"sndk-edgar": "the subject itself"}),
                    as_of=AS_OF, file_version=1)
    path = tmp_path_factory.mktemp("sector") / "sector.json"
    path.write_text(json.dumps(sector.to_json_obj()), encoding="utf-8")
    return sector_bundle(path, ticker="SNDK")


def _item(bundle, value, quote, evidence_id="cx.competitor", start=None):
    from src.fundamental.claims.models import sector_citation
    from src.fundamental.filings.extract import item

    text = bundle.parts[0].content
    start = text.index(quote) if start is None else start
    return item(evidence_id, value=value, unit="name", quote=quote,
                accession_id=sector_citation(bundle.parts[0].pins),
                offset=(start, start + len(quote)))


@pytest.mark.parametrize("value", ["Micron", "Micron Technology, Inc.", "micron technology"])
def test_ac_1_3c_a_first_person_peer_is_named_by_its_record(bundle, value):
    """AC-1.3c — the leading words of the record's declared subject pass."""
    from src.fundamental.claims.verify import x01_verify_extraction

    assert MICRON_QUOTE in bundle.parts[0].content
    assert x01_verify_extraction(bundle, [_item(bundle, value, MICRON_QUOTE)]).checked == 1


@pytest.mark.parametrize("value", ["SK hynix", "Technology", "Micron Memory", "Sandisk"])
def test_ac_1_3c_a_name_that_is_not_the_records_still_fails(bundle, value):
    """AC-1.3c — another company, or words that are not the subject's leading words."""
    from src.fundamental.claims.verify import x01_verify_extraction
    from src.fundamental.errors import ValueNotInSpanError

    with pytest.raises(ValueNotInSpanError):
        x01_verify_extraction(bundle, [_item(bundle, value, MICRON_QUOTE)])


def test_ac_1_3c_a_quote_across_two_records_fails(bundle):
    """AC-1.3c — the name must belong to ONE record; a span crossing a boundary has none."""
    from src.fundamental.claims.verify import x01_verify_extraction
    from src.fundamental.errors import ValueNotInSpanError

    text = bundle.parts[0].content
    cut = text.index("[mu-edgar]")
    boundary = text.rindex("\n", 0, cut)            # Samsung's 2Q26 deck ends, Micron's 10-K starts
    start = boundary - 30
    quote = text[start:boundary + 12]
    assert "Samsung" not in quote and "Micron" not in quote
    # ★ The START record is Samsung's, so only the crossing can fail it.
    with pytest.raises(ValueNotInSpanError, match="one record"):
        x01_verify_extraction(bundle, [_item(bundle, "Samsung", quote, start=start)])


def test_ac_1_3c_only_the_attribution_item_is_exempted(bundle):
    """AC-1.3c — `cx.capacity` keeps RA-6 ② in full: it is not a hole for every item."""
    from src.fundamental.claims.verify import x01_verify_extraction
    from src.fundamental.errors import ValueNotInSpanError

    with pytest.raises(ValueNotInSpanError):
        x01_verify_extraction(bundle, [_item(bundle, "Micron", MICRON_QUOTE, "cx.capacity")])
