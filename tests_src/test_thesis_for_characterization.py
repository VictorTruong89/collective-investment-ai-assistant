"""AC-F13.9 — ★ characterization, written BEFORE the runners' constants became argument
defaults (constitution §5 item 3). Each pins what a runner produces today with no new
argument; the change that follows must leave every one of these green.

⚠ The recorded hashes are FACTS about today's runners, measured 2026-10-20 — not targets.
"""
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
FACTS = REPO / ".state/facts/MU.parquet"
SECTOR = REPO / ".state/sector/memory_v1_2025-06-26.json"

#: The fourth MU thesis (`run-2026-10-04T031717-mu-thesis`, SELL) — its `base_bundle_hash`.
FOURTH_THESIS_BASE = "sha256:ed40721feec11e692af3a446da91b68305c72c761664f6b457203d4d58ecb9cb"
FILING_1 = "sha256:111aa631abad0ffa7263a40d6608e994964554dbb8c1efdf54f3bf19cff27b76"
SECTOR_2025_06_26 = "sha256:1418c0816fd03c6bac967acf8895619422780e2b0fd5148c46541fe31259c77e"


def test_ac_f13_9_the_extraction_runner_still_builds_filing_1():
    from tools import run_extraction_once as x

    x._select("MU")
    bundle = x.build_bundle()
    assert bundle.bundle_hash == FILING_1
    assert str(bundle.as_of) == "2025-06-26"
    assert bundle.parts[0].pins == {"accession_id": "0000723125-25-000021", "form": "10-Q",
                                    "period_end": "2025-05-29"}
    assert x.ACCESSION == "0000723125-25-000021"


def test_ac_f13_9_the_thesis_runner_keeps_its_recorded_defaults():
    from tools import run_thesis_once as t

    assert t.DEFAULT_STAGE_A["J-01"] == "run-2026-09-12T024848-mu-stage-a"
    assert len(t.DEFAULT_STAGE_A) == 9 and len(t.DEFAULT_EXTRACTIONS) == 8
    assert t.DEFAULT_SECTOR.name == "memory_v1_2025-06-26.json"
    assert t.PRICE_FIXTURE.name == "MU_raw_eod_2025-06.json"


@pytest.mark.skipif(not SECTOR.exists(), reason="the 2025-06-26 sector file lives in .state/")
def test_ac_f13_9_the_sector_bundle_is_unchanged():
    from tools import run_extraction_once as x

    assert x.sector_bundle(SECTOR, ticker="MU").bundle_hash == SECTOR_2025_06_26


@pytest.mark.skipif(not (FACTS.exists() and SECTOR.exists()),
                    reason="the MU fact ledger and sector file live in .state/ (not versioned)")
def test_ac_f13_9_the_thesis_base_is_the_fourth_theses():
    """★ The Stage B–D evidence the fourth MU thesis was authored over, rebuilt today."""
    from tools import run_thesis_once as t

    base, *_ = t.build_base("MU", t.DEFAULT_EXTRACTIONS)
    assert base.bundle_hash == FOURTH_THESIS_BASE
