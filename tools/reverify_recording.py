#!/usr/bin/env python3
"""Re-verify a COMPLETE recorded call under fixed verification code (`DX-123`).

    python3 tools/reverify_recording.py run-2026-09-16T070237-mu-e13 \\
        --sector .state/sector/memory_v1_2025-06-26.json      # ★ free: nothing is sent

★★ **Why this exists, and the line it must not cross.** `P5` says a failed run is not
evidence, and that rule is right: a truncated or refused CALL produced nothing trustworthy.
⚠ But two industry `E-13` runs FAILED for a reason that was not the model's — `DX-121` (an
industry quote had no citable id) and `DX-122` (`X-01` ② against a classification label).
The call itself completed: `stop_reason: tool_use`, whole JSON, a verbatim quote per item.
★ **The model's answer is unchanged; our verifier was wrong.** Paying again to receive the
same answer buys nothing but a clean status line (Victor Truong, 2026-09-16).

⚠⚠ **The guard, so this cannot become a way to launder a bad run:**

```text
  ① the recorded call must have COMPLETED          stop_reason == "tool_use"
  ② it must hold exactly one extraction call       one payload, one block
  ③ verification must PASS NOW                     X-01 ① ② + the subject guard
  ④ the new run records WHERE IT CAME FROM         replayed_from + the original run's status
```

★ A run that truncated (`max_tokens`) can never be replayed: its JSON is incomplete, so ①
refuses it — which is exactly what happened to the third attempt.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.fundamental.claims.models import sector_citation  # noqa: E402
from src.fundamental.claims.verify import x01_verify_extraction  # noqa: E402
from src.fundamental.filings.models import ExtractionResult  # noqa: E402
from src.fundamental.filings.subject import assert_subject_is_not_registrant  # noqa: E402
from tools.run_extraction_once import (  # noqa: E402
    SUBJECT_NAMES,
    build_bundle,
    parse_items,
    sector_bundle,
)

RUNS = REPO / ".state/runs"


class _Call:
    def __init__(self, text):
        self.text = self.parsed = text


def recorded_call(run_id: str) -> tuple[dict, dict]:
    """`(ExternalCall record, payload)` for the ONE extraction call of a recorded run."""
    root = RUNS / run_id
    records = [json.loads(ln) for ln in (root / "trace.jsonl").read_text().splitlines() if ln]
    calls = [r for r in records if r.get("type") == "ExternalCall"
             and str(r.get("step_id", "")).startswith("extract:")]
    if len(calls) != 1:
        raise ValueError(f"{run_id} holds {len(calls)} extraction call(s); exactly one replays")
    payload = json.loads((root / "trace/payloads" / f"{calls[0]['payload_ref']}.json")
                         .read_text(encoding="utf-8"))
    stop = (payload["response"].get("stop_reason") or "").lower()
    if stop != "tool_use":
        raise ValueError(
            f"{run_id} stopped at {stop!r} — only a COMPLETED call may be replayed. A "
            f"truncated answer is a failure, not a short one (GW-23, P5)")
    return calls[0], payload


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_id")
    ap.add_argument("--sector", default=None, help="the sector file the call read")
    ap.add_argument("--ticker", default="MU")
    ap.add_argument("--out", default=None, help="new run id (default: <run_id>-replay)")
    args = ap.parse_args(argv)

    call, payload = recorded_call(args.run_id)
    bundle = (sector_bundle(args.sector, ticker=args.ticker) if args.sector
              else build_bundle())
    if call.get("bundle_hash") and call["bundle_hash"] != bundle.bundle_hash:
        raise ValueError(
            f"{args.run_id} read bundle {call['bundle_hash'][:23]}… and this one is "
            f"{bundle.bundle_hash[:23]}… — a replay must verify against the SAME evidence")

    text = payload["response"]["text"]
    items = parse_items(_Call(text), bundle.parts[0].content,
                        accession_id=sector_citation(bundle.parts[0].pins) or None)
    block_id = call["step_id"].split(":", 1)[1]
    result = ExtractionResult(block_id, bundle.bundle_hash, tuple(items))
    report = x01_verify_extraction(bundle, items)                       # ③ — raises on failure
    assert_subject_is_not_registrant([result], bundle,
                                     subject=SUBJECT_NAMES[args.ticker] if args.sector else None)

    run_id = args.out or f"{args.run_id}-replay"
    root = RUNS / run_id
    (root / "trace/payloads").mkdir(parents=True, exist_ok=True)
    shutil.copy(RUNS / args.run_id / "trace/payloads" / f"{call['payload_ref']}.json",
                root / "trace/payloads" / f"{call['payload_ref']}.json")
    original = [json.loads(ln) for ln in
                (RUNS / args.run_id / "trace.jsonl").read_text().splitlines() if ln]
    replayed = {**call, "run_id": run_id,
                # ★ ④ — the provenance IS the point: this run made no call of its own.
                "replayed_from": args.run_id,
                "replayed_because": "verification code was fixed (DX-121, DX-122); the "
                                    "recorded call completed and is unchanged",
                "original_status": [r.get("status") for r in original
                                    if r.get("type") == "__run_closed__"],
                "replayed_at": datetime.now(timezone.utc).isoformat(),
                "cost_usd": 0.0, "tokens": {"input": 0, "output": 0}}
    (root / "trace.jsonl").write_text(
        json.dumps(replayed) + "\n" + json.dumps({"type": "__run_closed__",
                                                  "status": "SUCCESS"}) + "\n",
        encoding="utf-8")
    found = [i for i in items if i.status == "found"]
    print(f"── REPLAY · {args.run_id} → {run_id} (no call made, $0) ──")
    print(f"  {block_id} {call['prompt_version']} · bundle {bundle.bundle_hash[:23]}…")
    print(f"  X-01: {report.checked} checked · {report.not_found} not_found · subject guard ✅")
    for i in found:
        print(f"   {i.evidence_id:16s} {str(i.value)[:52]:52s} | {i.quote[:52]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
