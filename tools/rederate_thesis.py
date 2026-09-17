#!/usr/bin/env python3
"""Recompute a recorded thesis's COVERAGE and conviction on today's evidence — free.

    python3 tools/rederate_thesis.py .state/runs/<run>/thesis.json     # ★ no model call

★★ **What this may and may not claim.** The `DX-118` ladder is arithmetic over the evidence a
thesis's Stage A carried: coverage, the floors, and the conviction cap. When new extraction
evidence lands (here: the industry `E-13`, which let `J-03` score), that arithmetic changes and
can be redone **without asking the model anything**.

⚠⚠ **It does NOT re-author the thesis.** `J-09`…`J-17` answered over the OLD bundle; they never
saw the moat score or the competitor capacity. So this writes a SEPARATE record — the verdict
and every word of reasoning stay exactly as they were committed, and the file says plainly that
the Stage B–D calls did not read the new evidence. ★ Presenting a re-derated coverage as a
re-authored thesis would be the circularity `D2` forbids, one layer up.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.fundamental.bundle.models import EvidenceBundle  # noqa: E402
from src.fundamental.scorecard.availability import evidence_ids_in  # noqa: E402
from src.fundamental.thesis.derate import Derating  # noqa: E402
from src.fundamental.thesis.models import Thesis  # noqa: E402
from tools.run_extraction_once import build_bundle, sector_bundle  # noqa: E402
from tools.run_judgement_once import load_extraction_parts  # noqa: E402
from tools.run_thesis_once import (  # noqa: E402
    DEFAULT_EXTRACTIONS,
    DEFAULT_SECTOR,
    DEFAULT_STAGE_A,
    STAGE_A_ABSENT,
    emitted_rubrics,
    load_stage_a,
    public,
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thesis_json")
    ap.add_argument("--ticker", default="MU")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    payload = json.loads(pathlib.Path(args.thesis_json).read_text(encoding="utf-8"))
    thesis = Thesis.from_json_obj(payload.get("thesis", payload))
    outputs = payload.get("outputs") or {}

    filing = build_bundle()
    sector = sector_bundle(DEFAULT_SECTOR, ticker=args.ticker) if DEFAULT_SECTOR.exists() else None
    parts = load_extraction_parts(DEFAULT_EXTRACTIONS, filing, ticker=args.ticker, sector=sector)
    blind = EvidenceBundle(ticker=filing.ticker, as_of=filing.as_of,
                           parts=(*filing.parts, *parts)).redact()
    # ★ `J-20`'s frozen answer is re-validated through D-02's own functions, so the annual
    #   history it chose a window from has to be here too (free — the ledger is on disk).
    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.pit.snapshot import assemble_rows

    rows = assemble_rows(FactLedger(REPO / ".state/facts").read(args.ticker.upper()),
                         thesis.as_of, source="edgar")
    stage_a = load_stage_a(DEFAULT_STAGE_A, blind=blind, history_rows=rows,
                           ticker=args.ticker, as_of=thesis.as_of)

    before = dict(thesis.confidence)
    after = Derating.of(verdict=thesis.verdict, conviction=before.get("conviction_as_authored",
                                                                      thesis.conviction),
                        rubrics=emitted_rubrics(), extracted=evidence_ids_in(blind),
                        outputs=outputs, stage_a=stage_a)
    scorecard = {r["block_id"]: r["derived"] for r in stage_a if r["derived"]}
    scorecard.update({b: {"score": None, "outcome": "ABSENT", "reason": why}
                      for b, why in STAGE_A_ABSENT.items()})

    print(f"── RE-DERATION (free, no call) · {thesis.ticker} thesis of {thesis.as_of} ──")
    print(f"  coverage   : {before.get('value')} → {after.confidence['value']:.3f}  "
          f"(cap {before.get('cap')} → {after.confidence['cap']})")
    for d in after.confidence["coverage"]["by_dimension"]:
        print(f"     {d['dimension']:26s} {d['coverage']:.2f}  missing {sorted(d['missing'])}")
    print(f"  verdict    : {thesis.verdict} (unchanged — J-16 is not re-asked)")
    print(f"  conviction : {thesis.conviction} → {after.conviction}")
    print("  scorecard  : " + " · ".join(
        f"{b}={(v or {}).get('score', (v or {}).get('outcome'))}" for b, v in sorted(scorecard.items())))
    for absent in after.confidence["governing_inputs_absent"]:
        print(f"     still absent: {absent}")

    record = {
        "kind": "rederation",
        "ticker": thesis.ticker, "as_of": thesis.as_of.isoformat(),
        "thesis_run_id": thesis.run_id, "rederated_at": date.today().isoformat(),
        # ⚠⚠ The sentence that keeps this honest.
        "limitation": ("Stages B–D were NOT re-run: J-09…J-17 answered over the bundle of "
                       f"{thesis.as_of} without the industry evidence, so the verdict and its "
                       "reasoning are unchanged. Only the coverage arithmetic and the "
                       "conviction cap are recomputed (DX-118)."),
        "confidence_before": before, "confidence_after": after.confidence,
        "scorecard_after": scorecard,
        "stage_a": [public(r) for r in stage_a],
    }
    out = pathlib.Path(args.out or pathlib.Path(args.thesis_json).with_name("rederation.json"))
    out.write_text(json.dumps(record, indent=1, default=str), encoding="utf-8")
    print(f"  → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
