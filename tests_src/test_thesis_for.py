"""F13 — `thesis_for TICKER --as-of DATE` (AC-F13.1 … AC-F13.12, except AC-F13.9's
characterization, which is `test_thesis_for_characterization.py`).

★ Every chain test runs against FAKE runners over a temporary repo layout: no network, no
model, no `.state/`. The two known-answer checks that need the real recorded evidence skip
when `.state/` does not hold it, and say so.
"""
import json
import pathlib
from datetime import date, timedelta

import pytest

from src.fundamental.on_demand.chain import E_BLOCKS, STAGE_A_BLOCKS, GivenRuns, run_chain
from src.fundamental.on_demand.inputs import STALE_DAYS, resolve_inputs
from src.fundamental.on_demand.manifest import ChainManifest
from src.fundamental.on_demand.subjects import NoPeerSetError, Subject, load_subject

REPO = pathlib.Path(__file__).resolve().parent.parent
AS_OF = date(2026, 10, 20)
MU = Subject(ticker="MU", name="Micron Technology, Inc.", cik="0000723125",
             sector_list="memory_v1")
SOURCES = [{"source_id": "sndk-edgar", "kind": "edgar_filer", "cadence": "quarterly"},
           {"source_id": "skhynix-ir", "kind": "company_ir", "cadence": "quarterly"}]
MANUAL = {"skhynix-ir": {"where": "https://news.skhynix.com/"}}
EDGAR_SOURCES = {"sndk-edgar": {"cik": "0002023554", "subject": "Sandisk Corporation",
                                "slug": "sndk"}}
ACCESSION = "0000723125-26-000023"


# ── a repo layout with every input present at AS_OF ─────────────────────────

def _write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _repo(tmp_path, *, filed=date(2026, 10, 9), doc_dates=None, price_dates=None,
          consensus_fetched=AS_OF):
    fx = tmp_path / "tests_src/fixtures"
    _write(fx / "filings/MU_FY2026_10K.txt", "Micron 10-K body")
    _write(fx / "filings/index.json", json.dumps({"filings": [
        {"ticker": "MU", "form": "10-K", "accession": ACCESSION, "period_end": "2026-09-03",
         "filed": filed.isoformat(), "path": "tests_src/fixtures/filings/MU_FY2026_10K.txt"}]}))
    for source_id, published in (doc_dates or {"sndk-edgar": date(2026, 8, 17),
                                               "skhynix-ir": date(2026, 7, 23)}).items():
        _write(fx / f"industry/{source_id}/{published}_doc.txt", "peer document")
        _write(fx / f"industry/{source_id}/{published}_doc.meta.json",
               json.dumps({"published_date": published.isoformat(), "subject": source_id}))
    days = price_dates or [AS_OF - timedelta(days=1), AS_OF]
    _write(fx / f"prices/MU_raw_eod_{AS_OF}.json", json.dumps({
        "endpoint": "historical-price-eod/non-split-adjusted",
        "params": {"symbol": "MU", "from": min(days).isoformat(), "to": max(days).isoformat()},
        "fetched_on": AS_OF.isoformat(),
        "response": [{"symbol": "MU", "date": d.isoformat(), "adjClose": 1} for d in days]}))
    _write(fx / f"consensus/{consensus_fetched}/MU.meta.json",
           json.dumps({"fetched_at": f"{consensus_fetched}T20:00:00+00:00"}))
    return tmp_path


def _resolve(repo, as_of=AS_OF, facts=frozenset({ACCESSION})):
    return resolve_inputs(MU, as_of, repo=repo, sources=SOURCES,
                          facts_accessions=lambda _t: set(facts),
                          edgar_sources=EDGAR_SOURCES, manual_sources=MANUAL)


# ── fake runners — they record what they were asked, and raise if a dry run asks ──

class FakeRunners:
    def __init__(self, *, fail=(), forbid=False, thesis_ok=True):
        self.calls, self.fail, self.forbid, self.thesis_ok = [], set(fail), forbid, thesis_ok
        self.manifest_path = None
        self.seen_manifests = []
        self.n = 0

    def _new(self, kind, argv):
        if self.forbid:
            raise AssertionError(f"a dry run invoked {kind}")
        if self.manifest_path and self.manifest_path.exists():
            self.seen_manifests.append(json.loads(self.manifest_path.read_text()))
        self.calls.append((kind, list(argv)))
        self.n += 1
        return f"run-fake-{self.n:02d}-mu-{kind}"

    def sector_file(self, as_of):
        return None

    def build_sector(self, as_of):
        if self.forbid:
            raise AssertionError("a dry run built the sector file")
        self.calls.append(("sector", [str(as_of)]))
        return pathlib.Path(f"/tmp/memory_v1_{as_of}.json")

    def extract(self, argv):
        block = argv[argv.index("--block") + 1]
        run = self._new("extract", argv)
        if block in self.fail:
            self.fail.discard(block)
            raise RuntimeError(f"{block} failed")
        return run

    def stage_a(self, argv):
        return self._new("stage_a", argv)

    def stage_a_block_error(self, run_id, block):
        return f"{block} failed" if block in self.fail else None

    def thesis(self, argv):
        run = self._new("thesis", argv)
        self.last_thesis = run
        return run

    def thesis_summary(self, run_id):
        ok = self.thesis_ok
        self.thesis_ok = True                      # a resumed run finishes
        return {"thesis": {"verdict": "SELL"} if ok else None,
                "failed": None if ok else ["C:J-13", "session limit"],
                "base_bundle_hash": "sha256:base"}

    def verify(self, argv):
        self.calls.append(("verify", list(argv)))
        return "sha256:base"

    def thesis_calls(self):
        return 13

    def checks(self, thesis_run_id, as_of):
        self.calls.append(("checks", [thesis_run_id, str(as_of)]))
        return {"falsifiers": {"total": 3}, "rule_checks": {"calls": 13, "violations": []}}


def _chain(repo, runners, *, given=None, dry_run=False, paid=False, out=None):
    resolution = _resolve(repo)
    manifest = ChainManifest.open(repo / ".state/thesis_for", "MU", AS_OF, transport="claude_code")
    runners.manifest_path = manifest.path
    lines = []
    rc = run_chain(subject=MU, resolution=resolution, manifest=manifest, runners=runners,
                   given=given or GivenRuns(), dry_run=dry_run, paid=paid,
                   check_as_of=AS_OF, out=(out or lines.append))
    return rc, manifest, "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════

def test_ac_f13_1_a_dry_run_calls_nothing_and_prints_the_plan(tmp_path):
    rc, _, text = _chain(_repo(tmp_path), FakeRunners(forbid=True), dry_run=True)
    assert rc == 0
    for name in ("filing", "sector:sndk-edgar", "sector:skhynix-ir", "consensus", "price",
                 "facts"):
        assert name in text
    for block in (*E_BLOCKS, *STAGE_A_BLOCKS):
        assert block in text
    assert f"{len(E_BLOCKS) + len(STAGE_A_BLOCKS) + 13} model call(s)" in text


def test_ac_f13_2_the_paid_transport_is_refused_before_anything_runs(tmp_path):
    runners = FakeRunners(forbid=True)
    rc, _, text = _chain(_repo(tmp_path), runners, paid=True)
    assert rc == 2 and "anthropic_api" in text and "OFF" in text
    assert runners.calls == []


def test_ac_f13_3_a_missing_input_stops_before_any_call_and_names_its_supplier(tmp_path):
    repo = _repo(tmp_path)
    (repo / f"tests_src/fixtures/prices/MU_raw_eod_{AS_OF}.json").unlink()
    runners = FakeRunners(forbid=True)
    rc, _, text = _chain(repo, runners)
    assert rc == 2 and runners.calls == []
    assert "MISSING price" in text and "--fetch-inputs" in text
    assert not _resolve(repo).get("price").found


def test_ac_f13_4_nothing_knowable_only_after_as_of_is_used(tmp_path):
    later = AS_OF + timedelta(days=1)
    repo = _repo(tmp_path, filed=later, doc_dates={"sndk-edgar": later,
                                                   "skhynix-ir": date(2026, 7, 23)},
                 price_dates=[later], consensus_fetched=AS_OF - timedelta(days=1))
    r = _resolve(repo)
    for name in ("filing", "sector:sndk-edgar", "price", "consensus"):
        assert not r.get(name).found, name
    assert r.get("sector:skhynix-ir").found


def test_ac_f13_5_a_ticker_with_no_peer_set_is_refused():
    config = {"subjects": {"MU": {"name": "Micron", "cik": "1", "sector_list": "memory_v1"}}}
    assert load_subject("mu", config).sector_list == "memory_v1"
    with pytest.raises(NoPeerSetError, match="Victor"):
        load_subject("AMD", config)


def test_ac_f13_6_each_step_is_recorded_before_the_next_and_reads_run_ids_as_arguments(tmp_path):
    runners = FakeRunners()
    rc, manifest, _ = _chain(_repo(tmp_path), runners)
    assert rc == 0
    extracts = [argv for kind, argv in runners.calls if kind == "extract"]
    assert [a[a.index("--block") + 1] for a in extracts] == list(E_BLOCKS)
    # ★ the manifest on disk already held the previous extraction when the next began
    for i, seen in enumerate(runners.seen_manifests[1:len(E_BLOCKS)], start=1):
        done = [s for s in seen["steps"] if s["step"] == "extract" and s["status"] == "done"]
        assert len(done) == i
    ext_runs = [s["run_id"] for s in manifest.data["steps"] if s["step"] == "extract"]
    (stage_a_argv,) = [a for k, a in runners.calls if k == "stage_a"]
    assert stage_a_argv[stage_a_argv.index("--extractions") + 1:][:len(ext_runs)] == ext_runs
    (thesis_argv,) = [a for k, a in runners.calls if k == "thesis"]
    assert thesis_argv.count("--stage-a-run") == len(STAGE_A_BLOCKS)
    assert "--filing" in thesis_argv and ACCESSION in thesis_argv
    assert manifest.data["thesis_run_id"] == runners.last_thesis


def test_ac_f13_7_a_stopped_chain_resumes_from_the_step_that_stopped(tmp_path):
    repo = _repo(tmp_path)
    first = FakeRunners(fail={"E-06"})
    rc, manifest, text = _chain(repo, first)
    assert rc == 1 and "E-06" in text
    failed = [s for s in manifest.data["steps"] if s.get("block") == "E-06"]
    assert failed[0]["status"] == "failed"

    second = FakeRunners(thesis_ok=False)
    rc, _, _ = _chain(repo, second)
    blocks = [a[a.index("--block") + 1] for k, a in second.calls if k == "extract"]
    assert blocks == list(E_BLOCKS[E_BLOCKS.index("E-06"):]), "nothing completed is re-sent"
    assert rc == 1, "the thesis stopped (a session limit) — no thesis, P5"

    third = FakeRunners()
    rc, manifest, _ = _chain(repo, third)
    assert rc == 0
    (argv,) = [a for k, a in third.calls if k == "thesis"]
    assert argv[argv.index("--resume-from") + 1] == second.last_thesis
    assert not [k for k, _ in third.calls if k in ("extract", "stage_a")]


def test_ac_f13_8_the_recorded_runs_resolve_to_the_fourth_mu_theses_inputs(tmp_path):
    from tools import run_thesis_once as t

    recorded = json.loads((REPO / "config/thesis_for/MU_2025-06-26.json").read_text())
    given = GivenRuns.from_json(recorded)
    assert dict(given.stage_a) == t.DEFAULT_STAGE_A
    assert [run for _, run in given.extractions] == list(t.DEFAULT_EXTRACTIONS)
    runners = FakeRunners()
    rc, manifest, _ = _chain(_repo(tmp_path), runners, given=given)
    assert rc == 0
    assert not [k for k, _ in runners.calls if k in ("extract", "stage_a", "thesis")], \
        "a replay sends nothing"
    (verify_argv,) = [a for k, a in runners.calls if k == "verify"]
    pairs = [verify_argv[i + 1] for i, a in enumerate(verify_argv) if a == "--stage-a-run"]
    assert dict(p.split("=", 1) for p in pairs) == t.DEFAULT_STAGE_A
    i = verify_argv.index("--extractions")
    assert verify_argv[i + 1:i + 1 + len(t.DEFAULT_EXTRACTIONS)] == list(t.DEFAULT_EXTRACTIONS)
    assert manifest.data["thesis_run_id"] == recorded["thesis"]


@pytest.mark.skipif(not (REPO / ".state/facts/MU.parquet").exists()
                    or not (REPO / ".state/sector/memory_v1_2025-06-26.json").exists(),
                    reason="the MU fact ledger and the 2025-06-26 sector file live in .state/")
def test_ac_f13_8_the_replayed_bundle_is_the_fourth_theses():
    """★ Known answer: the arguments `thesis_for` builds rebuild the exact base bundle."""
    from tests_src.test_thesis_for_characterization import FOURTH_THESIS_BASE
    from tools.thesis_for import ToolRunners, replay_argv

    assert ToolRunners(REPO).base_hash(replay_argv(REPO, "MU", date(2025, 6, 26))) \
        == FOURTH_THESIS_BASE


def test_ac_f13_9_explicit_filing_arguments_build_the_same_bundle(monkeypatch):
    import argparse

    import tools.run_extraction_once as x

    monkeypatch.setitem(x.FILINGS, "MU", dict(x.FILINGS["MU"]))
    x._select("MU")
    before = x.build_bundle().bundle_hash
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", default="MU")
    x.add_filing_args(ap)
    args = ap.parse_args(["--filing", str(REPO / "tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt"),
                          "--accession", "0000723125-25-000021", "--form", "10-Q",
                          "--period-end", "2025-05-29", "--as-of", "2025-06-26"])
    assert x.apply_filing_args(args)
    x._select("MU")
    assert x.build_bundle().bundle_hash == before


def test_ac_f13_10_the_checks_run_over_the_new_thesis_and_are_recorded(tmp_path):
    runners = FakeRunners()
    rc, manifest, _ = _chain(_repo(tmp_path), runners)
    assert rc == 0
    (checks,) = [a for k, a in runners.calls if k == "checks"]
    assert checks[0] == manifest.data["thesis_run_id"]
    assert manifest.data["checks"]["thesis_run_id"] == manifest.data["thesis_run_id"]
    assert manifest.data["checks"]["rule_checks"]["violations"] == []


def test_ac_f13_11_fetch_writes_new_fixtures_only_and_leaves_ir_to_the_human(tmp_path):
    from src.fundamental.on_demand.fetch import FixtureExists, fetch_inputs

    repo = _repo(tmp_path, filed=date(2026, 6, 25))           # the 10-K is not yet held
    for p in (repo / "tests_src/fixtures/industry/skhynix-ir").glob("*"):
        p.unlink()
    (repo / "tests_src/fixtures/filings/MU_FY2026_10K.txt").unlink()
    index = json.loads((repo / "tests_src/fixtures/filings/index.json").read_text())
    index["filings"][0].update(path="tests_src/fixtures/filings/MU_FY2026Q3_10Q.txt",
                               accession="0000723125-26-000015", form="10-Q")
    (repo / "tests_src/fixtures/filings/index.json").write_text(json.dumps(index))
    resolution = _resolve(repo, facts={"0000723125-26-000015"})

    class Edgar:
        urls = []

        def submissions(self, cik):
            return {"fiscalYearEnd": "0903", "filings": {"recent": {
                "form": ["10-K"], "filingDate": ["2026-10-09"], "reportDate": ["2026-09-03"],
                "accessionNumber": [ACCESSION], "primaryDocument": ["mu-20260903.htm"]}}}

        def document(self, url):
            self.urls.append(url)
            return "<p>Micron 10-K</p>"

    edgar, ingested = Edgar(), []
    report = fetch_inputs(MU, AS_OF, resolution, repo=repo, edgar=edgar, fmp=None,
                          convert=lambda html: html.replace("<p>", "").replace("</p>", ""),
                          ingest_facts=lambda t, cik: ingested.append((t, cik)),
                          fetch_consensus=None, edgar_sources=EDGAR_SOURCES,
                          manual_sources=MANUAL, today=AS_OF)
    fixture = repo / "tests_src/fixtures/filings/MU_FY2026_10K.txt"
    assert fixture.read_text() == "Micron 10-K"
    assert (repo / "tests_src/fixtures/filings/MU_FY2026_10K.meta.txt").exists()
    rows = json.loads((repo / "tests_src/fixtures/filings/index.json").read_text())["filings"]
    assert rows[-1]["accession"] == ACCESSION and rows[-1]["form"] == "10-K"
    assert ingested == [("MU", "0000723125")]
    assert all("sec.gov/Archives/edgar/" in u for u in edgar.urls)
    assert any("skhynix-ir" in m for m in report.manual), "IR stays manual (D11)"
    with pytest.raises(FixtureExists):                         # ⚠ never overwritten
        fixture.unlink()
        fixture.write_text("someone else's")
        index_path = repo / "tests_src/fixtures/filings/index.json"
        doc = json.loads(index_path.read_text())
        doc["filings"] = doc["filings"][:-1]
        index_path.write_text(json.dumps(doc))
        fetch_inputs(MU, AS_OF, _resolve(repo, facts={"0000723125-26-000015"}), repo=repo,
                     edgar=Edgar(), fmp=None, convert=lambda h: h,
                     ingest_facts=lambda *_: None, fetch_consensus=None,
                     edgar_sources=EDGAR_SOURCES, manual_sources=MANUAL, today=AS_OF)


def test_ac_f13_11_the_fiscal_label_names_the_fixture():
    from src.fundamental.on_demand.fetch import fiscal_label

    assert fiscal_label(date(2026, 9, 3), "0903", "10-K") == "FY2026"
    assert fiscal_label(date(2025, 5, 29), "0828", "10-Q") == "FY2025Q3"
    assert fiscal_label(date(2025, 11, 27), "0828", "10-Q") == "FY2026Q1"


def test_ac_f13_12_a_stale_source_is_missing_not_found(tmp_path):
    old = AS_OF - timedelta(days=STALE_DAYS + 1)
    repo = _repo(tmp_path, filed=old, doc_dates={"sndk-edgar": old,
                                                 "skhynix-ir": AS_OF - timedelta(days=STALE_DAYS)})
    r = _resolve(repo)
    assert not r.get("filing").found and "stale" in r.get("filing").detail
    assert not r.get("sector:sndk-edgar").found
    assert r.get("sector:skhynix-ir").found, "exactly 120 days is still within the cadence"


def test_the_chain_declares_the_runners_stage_a_order():
    from tools.run_judgement_once import STAGE_A_ORDER

    assert tuple(STAGE_A_BLOCKS) == STAGE_A_ORDER


# ── ✏ 2026-10-21 — DX-174 (AC-F13.13) and the session-limit message (AC-F13.14) ──

LIMIT = ("TransportError: Claude Code error: You've hit your session limit · resets 5:20am "
         "(America/Toronto)")


def test_ac_f13_13_a_partial_stage_a_run_says_PARTIAL_never_SUCCESS():
    from tools.run_judgement_once import closing_status

    assert closing_status(answered=8, failed=1) == "PARTIAL"
    assert closing_status(answered=0, failed=9) == "FAILED"
    assert closing_status(answered=9, failed=0) == "SUCCESS"


def test_ac_f13_13_an_answered_block_of_a_PARTIAL_run_still_loads(tmp_path, monkeypatch):
    import tools.run_thesis_once as t
    monkeypatch.setattr(t, "RUN_ROOTS", (tmp_path,))
    _write_trace(tmp_path, "run-x-mu-partial", "PARTIAL", error=None)
    _write_trace(tmp_path, "run-x-mu-failed", "FAILED", error=None)
    call, _payload = t._recorded_call("run-x-mu-partial", "J-01", ticker="MU")
    assert call["step_id"] == "judge:J-01"
    with pytest.raises(ValueError, match="did not close"):
        t._recorded_call("run-x-mu-failed", "J-01", ticker="MU")
    _write_trace(tmp_path, "run-x-mu-partial2", "PARTIAL", error=LIMIT)
    with pytest.raises(ValueError, match="recorded an error"):
        t._recorded_call("run-x-mu-partial2", "J-01", ticker="MU")


def _write_trace(root, run_id, status, *, error):
    run = root / run_id
    (run / "trace/payloads").mkdir(parents=True)
    call = {"type": "ExternalCall", "step_id": "judge:J-01", "payload_ref": "judge:J-01:llm:1",
            "prompt_version": "v1", "error": error}
    (run / "trace.jsonl").write_text(json.dumps(call) + "\n" + json.dumps(
        {"type": "__run_closed__", "status": status}) + "\n")
    (run / "trace/payloads/judge:J-01:llm:1.json").write_text(json.dumps(
        {"request": {}, "response": {"text": "{}", "stop_reason": "tool_use"}}))


def test_ac_f13_14_a_session_limit_is_named_with_its_reset_time():
    from src.fundamental.on_demand.chain import describe_stop

    said = describe_stop(LIMIT)
    assert "session limit" in said and "5:20am (America/Toronto)" in said
    assert "nothing was lost" in said and "same command" in said
    assert describe_stop("ValueError: bad schema") == "ValueError: bad schema"


def test_ac_f13_14_the_chain_reports_a_stage_a_limit_in_words(tmp_path):
    class Limited(FakeRunners):
        def stage_a_block_error(self, run_id, block):
            return LIMIT if block == "J-20" else None

    rc, manifest, text = _chain(_repo(tmp_path), Limited())
    assert rc == 1
    assert "J-20" in text and "session limit" in text and "5:20am" in text
    assert "TransportError" not in text.split("session limit")[0].splitlines()[-1]
    j20 = manifest.find("stage_a", "J-20")
    assert j20["status"] == "failed" and "session limit" in j20["error"]
