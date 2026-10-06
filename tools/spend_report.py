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


def _response(run: pathlib.Path, rec: dict) -> dict:
    """The call's response. ⚠ Newer traces keep it only in the payload file
    (`trace/payloads/<payload_ref>.json`); reading the trace line alone missed
    `transport` there and priced every subscription call as API spend (found
    2026-10-05: a $137 "floor" that was mostly $0 subscription calls)."""
    if rec.get("response"):
        return rec["response"]
    ref = rec.get("payload_ref")
    path = run / "trace" / "payloads" / f"{ref}.json"
    if ref and path.is_file():
        return json.loads(path.read_text(encoding="utf-8")).get("response") or {}
    return {}


def tally(runs: pathlib.Path) -> dict:
    """Floor (API dollars), subscription count and notional, and the rows."""
    total = billed_unknown = subscription = 0
    notional = 0.0
    rows = []
    for run in sorted(runs.iterdir()):
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
            err = rec.get("error")
            resp = _response(run, rec)
            # ★ GW-27 — a subscription call is $0 of API money. Its list price is
            #   `notional_usd`, reported apart and never added to the floor.
            if (resp.get("transport") == "claude_code"
                    or "Claude Code" in (err or "")):
                subscription += 1
                notional += float(resp.get("notional_usd") or 0)
                continue
            cost = tin * PRICE_IN + tout * PRICE_OUT
            if not tin and err:
                # ⚠ Reached the vendor, failed locally — billed, unmeasurable.
                billed_unknown += 1
            total += cost
            rows.append((run.name, tin, tout, rec.get("latency_ms", 0) / 1000,
                         cost, status, (err or "")[:40]))

    return {"floor": round(total, 4), "subscription": subscription,
            "notional": round(notional, 4), "billed_unknown": billed_unknown,
            "rows": rows}


def main() -> int:
    if not RUNS.exists():
        print("  no runs recorded")
        return 0
    t = tally(RUNS)
    total, rows = t["floor"], t["rows"]
    subscription, notional = t["subscription"], t["notional"]
    billed_unknown = t["billed_unknown"]
    print(f"  {'run':<26} {'in':>8} {'out':>7} {'sec':>5} {'cost':>8}  outcome")
    for name, tin, tout, lat, cost, status, err in rows:
        note = f"{status}  {err}" if err else status
        print(f"  {name:<26} {tin:>8,} {tout:>7,} {lat:>5.0f} ${cost:>7.4f}  {note}")

    print(f"\n  ── measured floor: ${total:.2f} over {len(rows)} call(s)")
    if subscription:
        print(f"  ── subscription (claude_code): {subscription} call(s), $0 API — "
              f"notional list price ${notional:.2f}, NOT spend")
    if billed_unknown:
        print(f"  ⚠ {billed_unknown} call(s) recorded NO tokens but reached the "
              "vendor — billed, and invisible here. The console is authoritative.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
