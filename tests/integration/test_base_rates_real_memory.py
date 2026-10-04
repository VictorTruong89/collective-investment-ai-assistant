"""`F11` on REAL data — the `memory@v1` members' recorded EDGAR facts (`AC-F11.9`).

★ Reads ONLY the promoted fixtures (`tools/ingest_reference_class.py`), never `.state/`,
so it runs the same on a fresh clone (`DX-12`).
"""

from __future__ import annotations

import json
import pathlib
from datetime import date

import pandas as pd
import pytest

from src.data_engine.pit.snapshot import assemble_rows

REPO = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests_src/fixtures/edgar/reference_class/memory_v1"
AS_OF = date(2025, 6, 26)
#: MU's v2 trail rows as recorded 2026-10-02 (F10 D10/D11) — the thresholds' source.
TRAIL = {"implied_by_duration": [
    {"explicit_years": 5, "status": "NO_ROOT_IN_BRACKET", "value": None,
     "share_of_trailing_revenue": None},
    {"explicit_years": 7, "status": "SOLVED", "value": "0.390496826172",
     "share_of_trailing_revenue": "0.401108"},
    {"explicit_years": 10, "status": "SOLVED", "value": "0.282629394532",
     "share_of_trailing_revenue": "0.480931"},
    {"explicit_years": 15, "status": "SOLVED", "value": "0.204846191406",
     "share_of_trailing_revenue": "0.653198"}]}


@pytest.fixture(scope="module")
def result():
    from src.feature_engineer.base_rates.config import load_published_class, load_published_table
    from src.feature_engineer.base_rates.service import compute, history_from_rows

    cls = load_published_class("memory", 1)
    rows = {}
    for m in cls.members:
        r = assemble_rows(pd.read_parquet(FIXTURES / f"{m.label}.parquet"), AS_OF, source="edgar")
        rows[m.label] = r[r["period_type"] == "annual"]
    return compute(reference_class=cls, history=history_from_rows(rows, as_of=AS_OF),
                   subject="MU", as_of=AS_OF, trail=TRAIL,
                   published=load_published_table("base_rate_book_2016"))


def test_ac_f11_9_every_member_year_traces_to_an_accession_and_none_is_late(result):
    assert result.member_years, "the fixture produced no usable member-year"
    for y in result.member_years:
        assert y["accession_ids"], y
        assert y["filing_date"] is None or y["filing_date"] <= AS_OF


def test_ac_f11_9_wdc_counts_only_its_flash_years_and_sndk_2025_is_not_yet_filed(result):
    """`D3` — WDC FY2017–FY2025 only; the 2025 Sandisk's first 10-K post-dates the as-of."""
    by = {}
    for y in result.member_years:
        by.setdefault(y["member"], []).append(y["fiscal_year"])
    assert min(by["WDC"]) >= 2017 and max(by["WDC"]) <= 2025
    assert "SNDK" not in by


def test_ac_f11_9_the_result_reproduces_from_the_fixture_alone(result):
    again = json.loads(result.to_json())
    assert again["class"]["name"] == "memory" and again["subject"] == "MU"
    assert [r["periods"] for r in again["margin_reach"]] == [7, 10, 15]
