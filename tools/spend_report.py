#!/usr/bin/env python3
"""What the live runs actually cost — read from `F2`'s traces, not from memory.

    python3 tools/spend_report.py

⚠⚠ **This is a recomputation, not a reading.** `traced_transport` wraps the
TRANSPORT, so its records carry `tokens` but never the gateway's computed cost —
`cost_usd` is null on every one. ★ Until that `F2` gap is closed, the only way
to answer *"what did this cost?"* is tokens x `llm.pricing.*`, which is what
this does. A run whose cost nobody can state is a run nobody can budget for.

⚠ It reports only what a trace survives to record. A call that reached the
vendor and failed to DECODE locally (the `Brotli` incident, `DX-27`) was billed
and left `tokens: {}` — real money this report cannot see. The Anthropic console
is the authority; this is the floor.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RUNS = REPO / ".state/runs"

#: `claude-opus-5`, per 1M tokens. ⚠ Must match `llm.pricing.*` in the job.
PRICE_IN, PRICE_OUT = 5.00 / 1e6, 25.00 / 1e6


def main() -> int:
    if not RUNS.exists():
        print("  no runs recorded")
        return 0

    total = billed_unknown = 0
    rows = []
    for run in sorted(RUNS.iterdir()):
        log = run / "trace.jsonl"
        if not log.exists():
            continue
        # ⚠ Read the WHOLE file first: the sentinel is the LAST line, so
        # attributing it while streaming leaves every call marked "?".
        records = [json.loads(ln) for ln in
                   log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        status = next((r.get("status", "?") for r in records
                       if r.get("type") == "__run_closed__"), "INCOMPLETE")
        for rec in records:
            if rec.get("type") != "ExternalCall":
                continue
            tok = rec.get("tokens") or {}
            tin, tout = tok.get("input", 0), tok.get("output", 0)
            cost = tin * PRICE_IN + tout * PRICE_OUT
            err = rec.get("error")
            if not tin and err:
                # ⚠ Reached the vendor, failed locally — billed, unmeasurable.
                billed_unknown += 1
            total += cost
            rows.append((run.name, tin, tout, rec.get("latency_ms", 0) / 1000,
                         cost, status, (err or "")[:40]))

    print(f"  {'run':<26} {'in':>8} {'out':>7} {'sec':>5} {'cost':>8}  outcome")
    for name, tin, tout, lat, cost, status, err in rows:
        note = f"{status}  {err}" if err else status
        print(f"  {name:<26} {tin:>8,} {tout:>7,} {lat:>5.0f} ${cost:>7.4f}  {note}")

    print(f"\n  ── measured floor: ${total:.2f} over {len(rows)} call(s)")
    if billed_unknown:
        print(f"  ⚠ {billed_unknown} call(s) recorded NO tokens but reached the "
              "vendor — billed, and invisible here. The console is authoritative.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
