"""F13 `D15` — more subjects on an industry list (AC-F13.21, AC-F13.22).

★ Victor, 2026-10-22: SNDK on `memory_v2` (Micron · SK hynix · Samsung · Sandisk) with the
subject's own source left out, and MRNA on `vaccines_v1` (Pfizer · Novavax).

Tier: unit — over the real config files, with no network and no model.
"""
import json
import pathlib
from datetime import date

import pytest

from src.fundamental.on_demand.subjects import SUBJECT_ITSELF, Subject, load_subject, own_sources

REPO = pathlib.Path(__file__).resolve().parent.parent
AS_OF = date(2026, 10, 20)


def _config():
    import yaml

    return yaml.safe_load((REPO / "config/thesis_for.yaml").read_text(encoding="utf-8"))


def _sources(name):
    import yaml

    return yaml.safe_load((REPO / f"config/sector/{name}.yaml").read_text(encoding="utf-8"))["sources"]


# ── AC-F13.21 — the subject is not its own peer ─────────────────────────────

def test_ac_f13_21_sndk_leaves_out_its_own_source_and_reads_micron():
    """AC-F13.21 — on `memory_v2`, Sandisk's own filing is not industry evidence for Sandisk."""
    config = _config()
    sndk = load_subject("SNDK", config)
    assert sndk.sector_list == "memory_v2"
    omit = own_sources(sndk, _sources("memory_v2"), config["edgar_sources"])
    assert omit == {"sndk-edgar": SUBJECT_ITSELF}
    assert "mu-edgar" in {s["source_id"] for s in _sources("memory_v2")}


def test_ac_f13_21_mu_on_memory_v1_is_unchanged():
    """AC-F13.21 / AC-F13.9 — a subject not on its own list omits nothing."""
    config = _config()
    mu = load_subject("MU", config)
    assert mu.sector_list == "memory_v1"
    assert own_sources(mu, _sources("memory_v1"), config["edgar_sources"]) == {}


def test_ac_f13_21_a_manual_source_is_never_the_subject():
    """AC-F13.21 — only an EDGAR source carries a CIK to match; IR sources are kept."""
    subject = Subject(ticker="X", name="X", cik="0000000001", sector_list="l")
    sources = [{"source_id": "x-ir"}, {"source_id": "x-edgar"}]
    assert own_sources(subject, sources, {"x-edgar": {"cik": "0000000001"}}) == \
        {"x-edgar": SUBJECT_ITSELF}
    assert own_sources(subject, sources, {}) == {}


def test_ac_f13_21_the_resolved_inputs_hold_no_input_for_the_subjects_own_source():
    """AC-F13.21 — not counted missing, not fetched: it is not an input at all."""
    from tools.thesis_for import _context

    _config_, _subject, resolution = _context(REPO, "SNDK", AS_OF)
    names = {i.name for i in resolution.inputs}
    assert "sector:sndk-edgar" not in names
    assert {"sector:mu-edgar", "sector:skhynix-ir", "sector:samsung-ir"} <= names


def test_ac_f13_21_the_sector_file_declares_the_omission_under_its_own_name(tmp_path):
    """AC-F13.21 (RA-98) — the file says what it left out, and is named for its subject."""
    from tools.thesis_for import ToolRunners

    runners = ToolRunners(tmp_path, sector_list="memory_v2", ticker="SNDK",
                          omit={"sndk-edgar": SUBJECT_ITSELF})
    assert runners.sector_file(AS_OF) is None
    path = runners.build_sector(AS_OF)
    assert path == tmp_path / f".state/sector/memory_v2_{AS_OF}_SNDK.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    (om,) = [o for o in data["omissions"] if o["source_id"] == "sndk-edgar"]
    assert "subject itself" in om["reason"]
    assert all(r["source_id"] != "sndk-edgar" for r in data["records"])
    assert runners.sector_file(AS_OF) == path


def test_ac_f13_21_mu_keeps_its_sector_file_name(tmp_path):
    """AC-F13.21 / AC-F13.9 — no omission, no new name: MU's replays read the same file."""
    from tools.thesis_for import ToolRunners

    path = tmp_path / f".state/sector/memory_v1_{AS_OF}.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    assert ToolRunners(tmp_path, sector_list="memory_v1", ticker="MU").sector_file(AS_OF) == path


def test_ac_f13_21_mrna_reads_its_edgar_peers():
    """AC-F13.21 / `D15` — MRNA on `vaccines_v1`: Pfizer and Novavax, both fetchable."""
    config = _config()
    mrna = load_subject("MRNA", config)
    assert mrna.sector_list == "vaccines_v1"
    ids = [s["source_id"] for s in _sources("vaccines_v1")]
    assert ids == ["pfe-edgar", "nvax-edgar"]
    assert all(i in config["edgar_sources"] for i in ids)
    assert own_sources(mrna, _sources("vaccines_v1"), config["edgar_sources"]) == {}


# ── AC-F13.22 — the declared subject comes from the config ──────────────────

@pytest.mark.parametrize("ticker, name", [("SNDK", "Sandisk Corporation"),
                                          ("MRNA", "Moderna, Inc."),
                                          ("MU", "Micron Technology, Inc.")])
def test_ac_f13_22_the_subject_name_is_the_configs(ticker, name):
    """AC-F13.22 (DX-119) — declared, never inferred."""
    from tools.run_extraction_once import subject_name

    assert subject_name(ticker) == name


def test_ac_f13_22_an_undeclared_ticker_is_refused():
    """AC-F13.22 — no name is guessed for a ticker no one declared."""
    from tools.run_extraction_once import subject_name

    with pytest.raises(SystemExit, match="ZZZZ"):
        subject_name("ZZZZ")


# ── AC-F13.11 — a consensus set is ONE ticker's (found 2026-10-22, DX-186) ──

def test_ac_f13_11_a_second_ticker_on_the_same_date_writes_beside_the_first(tmp_path):
    """AC-F13.11 / `D10` — MU's 2026-10-20 set made SNDK's unwritable; the set is per ticker,
    so another ticker writes beside it and the same ticker again is still refused."""
    from src.fundamental.on_demand.fetch import FixtureExists, _fetch_consensus

    class Report:
        written: list = []

    def fetch(_t, _back, _fmp):
        return {"grades": [], "price_target_news": [], "earnings": [], "_pages": 0}

    folder = tmp_path / "tests_src/fixtures/consensus" / AS_OF.isoformat()
    folder.mkdir(parents=True)
    (folder / "MU.meta.json").write_text("{}", encoding="utf-8")
    _fetch_consensus("SNDK", AS_OF, repo=tmp_path, fmp=None, fetch=fetch, report=Report())
    assert (folder / "SNDK.meta.json").exists()
    assert (folder / "MU.meta.json").read_text(encoding="utf-8") == "{}"
    with pytest.raises(FixtureExists):
        _fetch_consensus("SNDK", AS_OF, repo=tmp_path, fmp=None, fetch=fetch, report=Report())


def test_ac_f13_22_no_runner_reads_the_old_table_directly():
    """AC-F13.22 — found live 2026-10-22: Stage A re-verified SNDK's E-13 through
    `SUBJECT_NAMES[ticker]` and stopped on `KeyError: 'SNDK'`. Every reader goes through
    `subject_name`, so a config-declared subject is declared everywhere."""
    import re

    offenders = [f"{p.relative_to(REPO)}:{n}"
                 for p in (REPO / "tools").glob("*.py")
                 for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                 if re.search(r"SUBJECT_NAMES\[", line) and p.name != "run_extraction_once.py"]
    assert offenders == []
