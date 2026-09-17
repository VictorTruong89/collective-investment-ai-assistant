#!/usr/bin/env python3
"""`RM-13` — lay out what a thesis's falsifiers have done since it was written (free).

    python3 tools/check_falsifiers.py .state/runs/<run>/thesis.json --as-of 2026-09-16

★ Deterministic: D-07's recorded facts only, no model. ⚠ It does not DECIDE a prose condition
(`DX-125`); it puts the evidence where a reader can, which is the step that was done by hand
for Micron's thesis on 2026-09-15.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.data_engine.pit.ledger import FactLedger  # noqa: E402
from src.data_engine.pit.snapshot import assemble_rows  # noqa: E402
from src.fundamental.monitor.falsifier_check import check, summary  # noqa: E402
from src.fundamental.thesis.models import Thesis  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thesis_json")
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--ledger", default=str(REPO / ".state/facts"))
    # ★ `DX-128` — structured tests, hand-written, so `RM-13` can DECIDE without a paid J-15
    #   re-run. ⚠ Each one is a reading of a sentence; the file states its own gaps.
    ap.add_argument("--tests", default=None, metavar="TESTS_JSON")
    args = ap.parse_args(argv)

    payload = json.loads(pathlib.Path(args.thesis_json).read_text(encoding="utf-8"))
    thesis = Thesis.from_json_obj(payload.get("thesis") or payload)
    as_of = date.fromisoformat(args.as_of)
    rows = assemble_rows(FactLedger(pathlib.Path(args.ledger)).read(thesis.ticker), as_of,
                         source="edgar")
    rows = rows[rows["period_type"] == "quarterly"]
    tests = json.loads(pathlib.Path(args.tests).read_text(encoding="utf-8")) if args.tests else {}
    if tests.get("_thesis_run_id") and tests["_thesis_run_id"] != thesis.run_id:
        raise ValueError(
            f"{args.tests} was written for {tests['_thesis_run_id']}, not {thesis.run_id} — a "
            f"test translated from ANOTHER thesis's prose decides nothing about this one")
    checks = check(thesis, rows, as_of=as_of,
                   tests={k: v for k, v in tests.items() if not k.startswith("_")})

    print(f"── FALSIFIERS · {thesis.ticker} thesis of {thesis.as_of} "
          f"({thesis.verdict}/{thesis.conviction}) · checked at {as_of} ──")
    for c in checks:
        print(f"\n  #{c.ordinal} [{c.status}] {c.observable_field} · deadline {c.deadline}")
        print(f"     {c.condition[:150]}")
        for o in c.observations:
            shown = "—" if o.value is None else f"{o.value / 1e6:,.0f}M"
            print(f"       {o.period_end} (filed {o.filing_date})  {shown}")
        print(f"     ⓘ {c.note}")
    print(f"\n  {json.dumps(summary(checks))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
