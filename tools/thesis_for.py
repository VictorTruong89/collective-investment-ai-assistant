#!/usr/bin/env python3
"""F13 — one thesis, one command: resolve the inputs for a date, then run the chain.

    python tools/thesis_for.py MU --as-of 2026-10-20 --dry-run        # ★ free: the plan
    python tools/thesis_for.py MU --as-of 2026-10-20 --fetch-inputs   # ★ free: EDGAR + FMP
    python tools/thesis_for.py MU --as-of 2026-10-20                  # the chain (~30 calls)

    # ★ the $0 replay of the fourth MU thesis — every step carried, nothing sent (D5)
    python tools/thesis_for.py MU --as-of 2025-06-26 --runs config/thesis_for/MU_2025-06-26.json

The chain: sector file → E-01 E-04 E-06 E-07 E-09 E-10 E-12 E-13 → Stage A (J-01…J-08, J-20)
→ Stages B–D (J-09…J-17) → falsifier check + rule checks. Each step's run id is written to
`.state/thesis_for/<TICKER>_<DATE>/chain.json` BEFORE the next starts; run the same command
again after a failure or a session limit and it resumes where it stopped.

Subscription only: it REFUSES `CIA_LLM_TRANSPORT=anthropic_api` (the paid API stays OFF).

★ The two company-IR documents are saved BY HAND (D11) — `--fetch-inputs` never scrapes them:

  SK hynix (skhynix-ir)
    1. Open https://news.skhynix.com/ → Press Center; find the newest
       "SK hynix Announces <n>Q<yy> Financial Results" dated on or before --as-of.
    2. Copy the release text (title to the last paragraph; leave out the site's
       "AI Summary" box — it is the site's text, not the company's).
    3. Save it as tests_src/fixtures/industry/skhynix-ir/<YYYY-MM-DD>_skhynix-<n>q<yy>-results.txt
       (YYYY-MM-DD = the release's own dateline).
    4. Beside it, <same name>.meta.json — copy the existing 1Q25 one and change: title, url,
       published_date, published_date_source, retrieved_at, chars, sha256, removed.

  Samsung (samsung-ir)
    1. Open https://www.samsung.com/global/ir/ → Financial Information → Earnings Release;
       download the newest quarter's "Earnings Presentation" PDF dated on or before --as-of.
    2. Convert it: pdftotext -layout <file>.pdf <name>.txt
    3. Save it as tests_src/fixtures/industry/samsung-ir/<YYYY-MM-DD>_samsung-<n>q<yy>-earnings-presentation.txt
       (YYYY-MM-DD = the earnings conference date — the deck carries no date line).
    4. Beside it, <same name>.meta.json — copy the existing 1Q25 one and change the same fields.

  Then: python tools/thesis_for.py MU --as-of <DATE> --dry-run   (both should read ✓)
  ⓘ sha256:  python -c "import hashlib,sys;print('sha256:'+hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" FILE
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import pathlib
import sys
from datetime import date, datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.fundamental.on_demand.chain import (  # noqa: E402
    STAGE_A_BLOCKS,
    GivenRuns,
    run_chain,
    thesis_inputs,
)
from src.fundamental.on_demand.inputs import resolve_inputs  # noqa: E402
from src.fundamental.on_demand.manifest import ChainManifest  # noqa: E402
from src.fundamental.on_demand.subjects import NoPeerSetError, load_subject  # noqa: E402

CONFIG = "config/thesis_for.yaml"


def _yaml(path: pathlib.Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


class ToolRunners:
    """The existing runners, called in-process with their own CLI arguments (`D1`)."""

    def __init__(self, repo: pathlib.Path, *, sector_list: str = "memory_v1",
                 ticker: str = "MU") -> None:
        self.repo, self.sector_list, self.ticker = repo, sector_list, ticker
        self.runs = repo / ".state/runs"

    # ── run discovery: a runner names its run from the clock, so the chain diffs ──
    def _call(self, main, argv) -> tuple[int, str | None]:
        before = set(os.listdir(self.runs)) if self.runs.is_dir() else set()
        rc = main(list(argv))
        new = sorted(n for n in (set(os.listdir(self.runs)) - before)
                     if f"-{self.ticker.lower()}-" in n)
        return rc, (new[-1] if new else None)

    def sector_file(self, as_of: date):
        path = self.repo / f".state/sector/{self.sector_list}_{as_of.isoformat()}.json"
        return path if path.exists() else None

    def build_sector(self, as_of: date):
        import tools.ingest_sector_file as ingest

        with _argv(["ingest_sector_file.py", "--list", self.sector_list,
                    "--as-of", as_of.isoformat()]):
            if ingest.main() != 0:
                raise RuntimeError("ingest_sector_file failed")
        path = self.sector_file(as_of)
        if path is None:
            raise RuntimeError("ingest_sector_file wrote no sector file")
        return path

    def extract(self, argv):
        import tools.run_extraction_once as x

        rc, run = self._call(x.main, argv)
        if rc != 0 or run is None:
            raise RuntimeError(f"run_extraction_once exited {rc} (run {run})")
        return run

    def stage_a(self, argv):
        import tools.run_judgement_once as j

        rc, run = self._call(j.main, argv)
        if run is None:
            raise RuntimeError(f"run_judgement_once exited {rc} and recorded no run")
        return run

    def stage_a_block_error(self, run_id, block) -> str | None:
        """None when the block has a usable answer; else WHY not — the call's own error
        first (a session limit is worded there, DX-175), then the loader's refusal."""
        from tools.run_thesis_once import _recorded_call

        trace = self.runs / run_id / "trace.jsonl"
        calls = [json.loads(ln) for ln in trace.read_text(encoding="utf-8").splitlines() if ln]
        errors = [c["error"] for c in calls if c.get("step_id") == f"judge:{block}"
                  and c.get("error")]
        if errors:
            return str(errors[-1])
        try:
            _call, payload = _recorded_call(run_id, block, ticker=self.ticker)
        except (ValueError, FileNotFoundError) as exc:
            return str(exc)
        if (payload["response"].get("stop_reason") or "").lower() == "max_tokens":
            return "truncated at max_tokens (GW-23)"
        return None

    def thesis(self, argv):
        import tools.run_thesis_once as t

        _rc, run = self._call(t.main, argv)
        if run is None:
            raise RuntimeError("run_thesis_once recorded no run (BLOCKED before any call)")
        return run

    def thesis_summary(self, run_id) -> dict:
        return json.loads((self.runs / run_id / "thesis.json").read_text(encoding="utf-8"))

    def base_hash(self, argv) -> str:
        from tools.run_thesis_once import base_for

        return base_for(argv).bundle_hash

    def verify(self, argv) -> str:
        """★ The free dry run re-loads every extraction (X-01) and Stage-A answer."""
        import tools.run_thesis_once as t

        if t.main(list(argv)) != 0:
            raise RuntimeError("the carried runs did not re-verify (run_thesis_once --dry-run)")
        return self.base_hash(argv)

    def thesis_calls(self) -> int:
        from tools.run_thesis_once import metrics_for, stage_plan

        return len(stage_plan(metrics_for(False)))

    def checks(self, thesis_run_id, as_of) -> dict:
        return {"falsifiers": self._falsifiers(thesis_run_id, as_of),
                "rule_checks": self._rule_checks(thesis_run_id)}

    def _falsifiers(self, run_id, as_of) -> dict:
        from src.data_engine.pit.ledger import FactLedger
        from src.data_engine.pit.snapshot import assemble_rows
        from src.fundamental.monitor.falsifier_check import check, summary
        from src.fundamental.thesis.models import Thesis
        from tools.check_falsifiers import tests_for

        path = self.runs / run_id / "thesis.json"
        thesis = Thesis.from_json_obj(json.loads(path.read_text(encoding="utf-8"))["thesis"])
        rows = assemble_rows(FactLedger(self.repo / ".state/facts").read(thesis.ticker), as_of,
                             source="edgar")
        tests = tests_for(path, explicit=None)
        checks = check(thesis, rows[rows["period_type"] == "quarterly"], as_of=as_of,
                       tests={k: v for k, v in tests.items() if not k.startswith("_")})
        return summary(checks)

    def _rule_checks(self, run_id) -> dict:
        import tools.rule_checks as rc

        run_dir = self.runs / run_id
        # ★ The thesis may quote a peer document (E-13); the sector file's text is searched too.
        sectors = []
        sector_path = self.sector_file_for(run_dir)
        if sector_path:
            sectors.append("\n".join(r["quote"] for r in json.loads(
                sector_path.read_text(encoding="utf-8"))["records"]))
        source = rc._source_text(run_dir, sectors)
        payloads = sorted((run_dir / "trace/payloads").glob("*.json"))
        found = []
        for p in payloads:
            found += rc.check_call(run_id, p.stem, json.loads(p.read_text(encoding="utf-8")),
                                   source, rc._default_absences())
        return {"calls": len(payloads),
                "violations": [{"rule": v.rule, "call": v.call, "detail": v.detail,
                                "known": (v.run, v.call, v.rule) in rc.KNOWN} for v in found]}

    def sector_file_for(self, run_dir: pathlib.Path):
        as_of = json.loads((run_dir / "thesis.json").read_text())["as_of"]
        return self.sector_file(date.fromisoformat(as_of))


@contextlib.contextmanager
def _argv(argv):
    saved = sys.argv
    sys.argv = list(argv)
    try:
        yield
    finally:
        sys.argv = saved


def _context(repo: pathlib.Path, ticker: str, as_of: date):
    config = _yaml(repo / CONFIG)
    subject = load_subject(ticker, config)
    sources = _yaml(repo / f"config/sector/{subject.sector_list}.yaml")["sources"]

    def facts_accessions(t):
        from src.data_engine.pit.ledger import FactLedger

        if not (repo / ".state/facts" / f"{t}.parquet").exists():
            return set()
        return set(FactLedger(repo / ".state/facts").read(t)["accession_id"])

    resolution = resolve_inputs(subject, as_of, repo=repo, sources=sources,
                                facts_accessions=facts_accessions,
                                edgar_sources=config.get("edgar_sources") or {},
                                manual_sources=config.get("manual_sources") or {})
    return config, subject, resolution


def replay_argv(repo: pathlib.Path, ticker: str, as_of: date) -> list[str]:
    """AC-F13.8 — the step-4 arguments the chain builds from the recorded runs file."""
    _config, subject, resolution = _context(repo, ticker, as_of)
    given = GivenRuns.from_json(json.loads(
        (repo / f"config/thesis_for/{ticker}_{as_of.isoformat()}.json").read_text()))
    sector = ToolRunners(repo, sector_list=subject.sector_list, ticker=ticker).sector_file(as_of)
    return ["--dry-run", *thesis_inputs(resolution, stage_runs=dict(given.stage_a),
                                        ext_runs=[r for _, r in given.extractions],
                                        sector_path=sector)]


def _fetch(repo, subject, as_of, resolution, config) -> int:
    from src.data_engine.ingest.edgar_facts import ingest_facts
    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.src.edgar.client import EdgarClient
    from src.fundamental.on_demand.fetch import fetch_inputs
    from src.shared.secrets import Secret
    from tools.convert_filing import convert
    from tools.fetch_consensus import _client as fmp_client
    from tools.fetch_consensus import fetch as fetch_consensus

    contact = os.environ.get("EDGAR_CONTACT") or os.environ.get("GMAIL_SMTP_USER")
    if not contact:
        print("  ⛔ EDGAR_CONTACT is not set (SEC requires a contactable User-Agent) — "
              "run `set -a; source .env; set +a` first")
        return 2
    edgar = EdgarClient(Secret("EDGAR_CONTACT", contact))
    needs_fmp = not (resolution.get("price").found and resolution.get("consensus").found)
    report = fetch_inputs(
        subject, as_of, resolution, repo=repo, edgar=edgar,
        fmp=fmp_client() if needs_fmp else None, convert=convert,
        ingest_facts=lambda t, cik: ingest_facts(edgar, FactLedger(repo / ".state/facts"),
                                                 ticker=t, cik=cik),
        fetch_consensus=fetch_consensus, edgar_sources=config.get("edgar_sources") or {},
        manual_sources=config.get("manual_sources") or {},
        today=datetime.now(timezone.utc).date())
    for w in report.written:
        print(f"  ✅ wrote {w}")
    for n in report.notes:
        print(f"  ⓘ {n}")
    for m in report.manual:
        print(f"  ✋ BY HAND: {m}")
    if not (report.written or report.manual or report.notes):
        print("  ⓘ nothing to fetch")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("--as-of", required=True, type=date.fromisoformat)
    ap.add_argument("--dry-run", action="store_true", help="★ free — inputs and plan, no call")
    ap.add_argument("--fetch-inputs", action="store_true",
                    help="★ free — fetch the missing EDGAR/FMP inputs as new fixtures, then "
                         "show the plan (company-IR documents stay manual)")
    ap.add_argument("--runs", default=None, metavar="FILE",
                    help="recorded run ids to carry (e.g. config/thesis_for/MU_2025-06-26.json)")
    ap.add_argument("--run", action="append", default=[], metavar="KEY=RUN_ID",
                    help="carry one recorded run: E-nn=…, J-nn=… or thesis=… (repeatable)")
    ap.add_argument("--check-as-of", default=None, type=date.fromisoformat,
                    help="the date the falsifiers are checked at (default: today, New York)")
    args = ap.parse_args(argv)
    os.chdir(REPO)                    # ★ the runners resolve .state/ paths from here

    from tools.llm_transport import is_paid, transport_label

    print(f"  transport  : {transport_label()}")
    try:
        config, subject, resolution = _context(REPO, args.ticker, args.as_of)
    except NoPeerSetError as exc:
        print(f"  ⛔ REFUSED: {exc}")
        return 2
    dry_run = args.dry_run
    if args.fetch_inputs:
        rc = _fetch(REPO, subject, args.as_of, resolution, config)
        if rc:
            return rc
        config, subject, resolution = _context(REPO, args.ticker, args.as_of)
        dry_run = True                                  # ★ fetching never sends a call
    given = GivenRuns()
    if args.runs:
        given = GivenRuns.from_json(json.loads((REPO / args.runs).read_text(encoding="utf-8")))
    given = given.with_args(args.run)
    if given.stage_a and len(dict(given.stage_a)) not in (0, len(STAGE_A_BLOCKS)):
        print("  ⓘ some Stage-A blocks given; the rest are sent one block per call")
    from zoneinfo import ZoneInfo

    market_date = datetime.now(ZoneInfo("America/New_York")).date()        # MT-56, OR-59
    manifest = ChainManifest.open(REPO / ".state/thesis_for", subject.ticker, args.as_of,
                                  transport="anthropic_api" if is_paid() else "claude_code")
    return run_chain(subject=subject, resolution=resolution, manifest=manifest,
                     runners=ToolRunners(REPO, sector_list=subject.sector_list,
                                         ticker=subject.ticker),
                     given=given, dry_run=dry_run, paid=is_paid(),
                     check_as_of=args.check_as_of or market_date, repo=REPO)


if __name__ == "__main__":
    raise SystemExit(main())
