"""Steps 1–5 — the chain over the existing runners, recorded step by step (CT-F13.1).

```text
  sector file (free) → E-01 … E-13 (8 runs) → Stage A (J-01…J-08, J-20) → Stages B–D → checks (free)
```

★ Every step hands the next the run ids it reads AS ARGUMENTS (`D1`, AC-F13.6); a step that
is done — recorded in the manifest, or given by the caller — is carried and never re-sent
(AC-F13.7). The runners are injected: this module decides WHAT runs, never HOW (`CA-9`).

⚠ A carried run is re-verified by the step that reads it: the judgement and thesis runners
re-load every extraction through `X-01`, and a carried thesis must have been authored over
the bundle these arguments rebuild (`RA-2`) — or the chain stops.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: `D8` — the 8 E-blocks the thesis reads, in the order a NEW chain runs them.
E_BLOCKS = ("E-01", "E-04", "E-06", "E-07", "E-09", "E-10", "E-12", "E-13")
#: Run over the industry sector file, not the filing (`DX-117`).
SECTOR_BLOCKS = frozenset({"E-13"})
#: ★ `DX-130` — `E-09` completed only at `--effort low` (five truncations at the default).
BLOCK_OPTIONS = {"E-09": ("--effort", "low")}
#: Stage A in its declared order — the same tuple as `run_judgement_once.STAGE_A_ORDER`
#: (a test holds them equal; `src/` does not import `tools/`).
STAGE_A_BLOCKS = ("J-01", "J-02", "J-03", "J-04", "J-05", "J-06", "J-07", "J-08", "J-20")


@dataclass(frozen=True)
class GivenRuns:
    """Run ids the CALLER supplies (`--runs FILE`, `--run KEY=RUN_ID`) — carried, not sent.

    ★ `extractions` keeps its order: the bundle's part order is part of its hash, so a
    replay must pass them in the order the recorded thesis read them (AC-F13.8).
    """

    extractions: tuple[tuple[str, str], ...] = ()
    stage_a: tuple[tuple[str, str], ...] = ()
    thesis: str | None = None

    @classmethod
    def from_json(cls, obj: dict) -> "GivenRuns":
        return cls(extractions=tuple((b, r) for b, r in obj.get("extractions") or ()),
                   stage_a=tuple(sorted((obj.get("stage_a") or {}).items())),
                   thesis=obj.get("thesis"))

    def with_args(self, pairs) -> "GivenRuns":
        """`KEY=RUN_ID` pairs on top — `E-nn`, `J-nn` or `thesis`. Arguments win."""
        ext, stage, thesis = dict(self.extractions), dict(self.stage_a), self.thesis
        for pair in pairs:
            key, _, run = pair.partition("=")
            if not run:
                raise ValueError(f"--run {pair!r} is not KEY=RUN_ID")
            if key in E_BLOCKS:
                ext[key] = run
            elif key in STAGE_A_BLOCKS:
                stage[key] = run
            elif key == "thesis":
                thesis = run
            else:
                raise ValueError(f"--run {key!r} is not one of {E_BLOCKS + STAGE_A_BLOCKS} "
                                 f"or 'thesis'")
        order = [b for b, _ in self.extractions] + [b for b in ext if b not in
                                                    dict(self.extractions)]
        return GivenRuns(extractions=tuple((b, ext[b]) for b in order),
                         stage_a=tuple(sorted(stage.items())), thesis=thesis)


#: ★ AC-F13.14 — how the Claude Code CLI words a usage limit (measured 2026-10-21).
_LIMIT = re.compile(r"hit your (session|usage|weekly|daily) limit\s*·?\s*(resets [^\n]+)?", re.I)


def describe_stop(error: str) -> str:
    """A step's stop in plain words. ★ A usage limit is NOT a fault: say so, and when it ends.

    ⚠ `DX-175` — it printed as a bare `TransportError`; the reason was only in the trace.
    """
    found = _LIMIT.search(error or "")
    if not found:
        return error
    kind, reset = found.group(1).lower(), (found.group(2) or "").strip()
    return (f"the subscription's {kind} limit was hit" + (f", {reset}" if reset else "")
            + " — nothing was lost; run the same command again after that and it resumes here")


def _filing_args(resolution) -> list[str]:
    row = resolution.get("filing").meta
    return ["--ticker", resolution.ticker, "--filing", row["path"],
            "--accession", row["accession"], "--form", row["form"],
            "--period-end", row["period_end"], "--as-of", resolution.as_of.isoformat()]


def thesis_inputs(resolution, *, stage_runs: dict, ext_runs, sector_path) -> list[str]:
    """Step 4's arguments — every run id it reads, the sector file, the price and consensus.

    ★ The one place they are assembled: the live chain and the replay check both call it.
    """
    return [*_filing_args(resolution),
            *[a for b in STAGE_A_BLOCKS for a in ("--stage-a-run", f"{b}={stage_runs[b]}")],
            "--extractions", *ext_runs, "--sector", str(sector_path),
            "--price-fixture", resolution.get("price").path,
            "--consensus-dir", resolution.get("consensus").meta["dir"]]


def run_chain(*, subject, resolution, manifest, runners, given: GivenRuns, dry_run: bool,
              paid: bool, check_as_of, out=print, repo=None) -> int:
    """0 — a thesis, checked · 1 — a step failed (recorded; re-run resumes) · 2 — blocked."""
    as_of = resolution.as_of
    out(f"── THESIS_FOR · {subject.ticker} ({subject.name}) as of {as_of} · industry "
        f"{subject.sector_list} · transport {manifest.data['transport']} ──")
    out("  inputs:")
    for i in resolution.inputs:
        out(f"   {'✓' if i.found else '✗ MISSING'} {i.name:<20} {i.detail}")
        if not i.found:
            out(f"       → {i.supply}")
    if paid and not dry_run:
        # ★ AC-F13.2 — before ANY step, carried or not: the paid API stays OFF (D4).
        out("  ⛔ REFUSED: CIA_LLM_TRANSPORT=anthropic_api selects the PAID API, which stays OFF "
            "(Victor, 2026-10-05; F13 D4). Unset it to use the subscription (claude_code).")
        return 2

    ext_given, stage_given = dict(given.extractions), dict(given.stage_a)
    order = [b for b, _ in given.extractions if b in E_BLOCKS] + \
        [b for b in E_BLOCKS if b not in ext_given]

    def ext_done(block):
        if block in ext_given:
            return ext_given[block]
        entry = manifest.done("extract", block)
        return entry["run_id"] if entry else None

    def stage_done(block):
        if block in stage_given:
            return stage_given[block]
        entry = manifest.done("stage_a", block)
        return entry["run_id"] if entry else None

    thesis_done = given.thesis or (manifest.done("thesis") or {}).get("run_id")
    failed_thesis = manifest.find("thesis")
    resume_from = (failed_thesis["run_id"] if failed_thesis and not thesis_done
                   and failed_thesis["status"] == "failed" and failed_thesis.get("run_id")
                   else None)
    sector_path = runners.sector_file(as_of)

    out("  steps:")
    out(f"   {'✓' if sector_path else '·'} sector file{'' if sector_path else ' (free)'}"
        f"{f'  {sector_path}' if sector_path else ''}")
    for b in order:
        run = ext_done(b)
        out(f"   {'✓ ' + run if run else '· 1 call'}  extract {b}"
            f"{'  (sector file)' if b in SECTOR_BLOCKS else ''}")
    pending_stage = [b for b in STAGE_A_BLOCKS if not stage_done(b)]
    for b in STAGE_A_BLOCKS:
        run = stage_done(b)
        out(f"   {'✓ ' + run if run else '· 1 call'}  stage A {b}")
    thesis_calls = 0 if thesis_done else runners.thesis_calls()
    out(f"   {'✓ ' + thesis_done if thesis_done else f'· ≤{thesis_calls} calls'}  stages B–D"
        f"{f' (resumes {resume_from})' if resume_from else ''}")
    out("   · checks (free): falsifiers · rule checks")
    calls = sum(1 for b in order if not ext_done(b)) + len(pending_stage) + thesis_calls
    out(f"  plan: {calls} model call(s) on the subscription")

    if resolution.missing:
        out(f"  ⛔ STOP — {len(resolution.missing)} input(s) MISSING; nothing is sent (P5). "
            f"Supply them, then run this again.")
        return 2
    if dry_run:
        out("  ★ dry run — nothing was sent, nothing was written.")
        return 0

    manifest.set(inputs=[i.to_json_obj(repo) if repo else {"name": i.name, "path": i.path}
                         for i in resolution.inputs],
                 filing_form=resolution.get("filing").meta["form"])               # D7
    for b, run in ext_given.items():
        manifest.record("extract", b, run_id=run, status="done", given=True)
    for b, run in stage_given.items():
        manifest.record("stage_a", b, run_id=run, status="done", given=True)

    # ── 1 · the sector file (free) ───────────────────────────────────────────
    if not sector_path:
        manifest.record("sector", status="pending")
        sector_path = runners.build_sector(as_of)
    manifest.record("sector", status="done", path=str(sector_path))
    filing = _filing_args(resolution)

    # ── 2 · the extractions ──────────────────────────────────────────────────
    for b in order:
        if ext_done(b):
            continue
        # ★ `D14` — evidence first, so the seven filing extractions share one cached bundle.
        argv = ["--live", "--cache-evidence", "--block", b, *filing,
                *(["--sector", str(sector_path)] if b in SECTOR_BLOCKS else []),
                *BLOCK_OPTIONS.get(b, ())]
        manifest.record("extract", b, status="pending")
        try:
            run = runners.extract(argv)
        except Exception as exc:                          # noqa: BLE001 — recorded, P5
            why = describe_stop(f"{type(exc).__name__}: {exc}")
            manifest.record("extract", b, status="failed", error=why)
            out(f"  ⛔ {b} FAILED: {why} — recorded; run this again to resume from {b}")
            return 1
        manifest.record("extract", b, run_id=run, status="done")
        out(f"   ✅ {b}  {run}")
    ext_runs = [ext_done(b) for b in order]
    reads = ["--extractions", *ext_runs, "--sector", str(sector_path)]

    # ── 3 · Stage A ──────────────────────────────────────────────────────────
    pending_stage = [b for b in STAGE_A_BLOCKS if not stage_done(b)]
    facts_dir = str(_parent(resolution.get("facts").path))
    if pending_stage:
        whole = pending_stage == list(STAGE_A_BLOCKS)
        batches = [("--stage-a",)] if whole else [("--block", b) for b in pending_stage]
        for batch in batches:
            blocks = pending_stage if whole else [batch[1]]
            for b in blocks:
                manifest.record("stage_a", b, status="pending")
            try:
                run = runners.stage_a(["--live", "--cache-evidence", *batch, *filing, *reads,
                                       "--annual-history", facts_dir])
            except Exception as exc:                      # noqa: BLE001
                why = describe_stop(f"{type(exc).__name__}: {exc}")
                for b in blocks:
                    manifest.record("stage_a", b, status="failed", error=why)
                out(f"  ⛔ Stage A stopped: {why}")
                return 1
            for b in blocks:
                error = runners.stage_a_block_error(run, b)
                manifest.record("stage_a", b, run_id=run, status="failed" if error else "done",
                                **({"error": describe_stop(error)} if error else {}))
        bad = [b for b in STAGE_A_BLOCKS if not stage_done(b)]
        if bad:
            out(f"  ⛔ Stage A incomplete: {bad} — recorded; run this again to re-send only those")
            for b in bad:
                out(f"     {b}: {manifest.find('stage_a', b).get('error')}")
            return 1
        out(f"   ✅ Stage A  {sorted({stage_done(b) for b in STAGE_A_BLOCKS})}")

    # ── 4 · Stages B–D ───────────────────────────────────────────────────────
    inputs = thesis_inputs(resolution, stage_runs={b: stage_done(b) for b in STAGE_A_BLOCKS},
                           ext_runs=ext_runs, sector_path=sector_path)
    if thesis_done:
        # ★ Carried: re-verified — the recorded thesis must have read THIS bundle (RA-2).
        base = runners.verify(["--dry-run", *inputs])
        recorded = runners.thesis_summary(thesis_done).get("base_bundle_hash")
        if base != recorded:
            manifest.record("thesis", run_id=thesis_done, status="failed",
                            error=f"carried thesis read {recorded}, these inputs build {base}")
            out(f"  ⛔ the carried thesis {thesis_done} was authored over {recorded}; these "
                f"inputs build {base} — not the same evidence (RA-2)")
            return 1
        manifest.record("thesis", run_id=thesis_done, status="done", verified_base=base,
                        **({"given": True} if given.thesis else {}))
        out(f"   ✓ stages B–D carried: {thesis_done} (base bundle {base[:23]}… re-verified)")
    else:
        manifest.record("thesis", status="pending")
        argv = ["--live", "--budget-usd", "0", *inputs,
                *(["--resume-from", resume_from] if resume_from else [])]
        try:
            run = runners.thesis(argv)
        except Exception as exc:                          # noqa: BLE001
            why = describe_stop(f"{type(exc).__name__}: {exc}")
            manifest.record("thesis", status="failed", error=why)
            out(f"  ⛔ stages B–D stopped: {why}")
            return 1
        summary = runners.thesis_summary(run)
        if not summary.get("thesis"):
            why = describe_stop(" ".join(map(str, summary.get("failed") or ())))
            manifest.record("thesis", run_id=run, status="failed", error=why)
            out(f"  ⛔ NO thesis yet (P5) — {why}. Recorded; run this again to resume from {run}")
            return 1
        manifest.record("thesis", run_id=run, status="done")
        thesis_done = run
    manifest.set(thesis_run_id=thesis_done)

    # ── 5 · the checks (free) ────────────────────────────────────────────────
    result = runners.checks(thesis_done, check_as_of)
    manifest.set(checks={"thesis_run_id": thesis_done, "as_of": str(check_as_of), **result})
    manifest.record("checks", run_id=thesis_done, status="done")
    out(f"  ★ thesis {thesis_done} · checks {result}")
    out(f"  chain → {manifest.path}")
    return 0


def _parent(path: str | None) -> str:
    import pathlib

    return str(pathlib.Path(path).parent) if path else ".state/facts"
