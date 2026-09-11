#!/usr/bin/env python3
"""Run ONE real `J-01` judgement call and record it (`DX-64`).

    python3 tools/run_judgement_once.py --dry-run   # ★ free
    python3 tools/run_judgement_once.py --live      # ⚠ SPENDS (~$0.29)

⚠⚠ **Why a separate runner from `run_extraction_once.py`.** `RA-5` splits
extraction (*what does this document say* — ground truth exists) from judgement
(*is this good* — none does), and the two have different contracts end to end:

  · extraction returns ITEMS, each verified by `X-01` against a quoted span.
  · `J-01` returns a CLASSIFICATION from a closed set, plus a runner-up and the
    sentence that would settle it. ⚠ There is no span to check it against —
    `X-01` does not apply, and pretending it did would be the *"two contracts
    wearing one name"* failure `F9` `D1` rejects.

★★ **`view="blind"` is the load-bearing part.** `MP-3`: *"a Stage-A prompt
cannot see price because the bundle handed to it has no price field — 'do not
consider valuation' is a request; an absent field is a guarantee."* This runner
calls `EvidenceBundle.redact()` and the seam checks it BOTH ways (`RA-14`).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.fundamental.prompts.e_blocks import j01_v1  # noqa: E402
from src.fundamental.prompts.envelope import compose_prompt  # noqa: E402
from tools.run_extraction_once import ACCESSION, build_bundle  # noqa: E402

MODEL = "claude-opus-5"
PRICE_IN, PRICE_OUT = 5 / 1_000_000, 25 / 1_000_000
MAX_OUT = 4_000


def judgement_tool(options: tuple[str, ...]) -> dict:
    """`MP-5` — the closed set is declared as an ENUM, never described.

    ⚠⚠ Both of `extraction_tool`'s measured defects were the same mistake:
    *describing* a constraint instead of *declaring* it. `J-01` names seven
    archetypes in its prose; if the schema left `archetype` a free string the
    model could return an eighth, and `RA-17`'s closed set would be a
    suggestion. ★ `insufficient_evidence` is in the enum because `MP-7` says a
    block with no way to say *"I could not"* will always find something to say.
    """
    return {
        "name": "classify_archetype",
        "description": "Return the single archetype this company belongs to.",
        "input_schema": {
            "type": "object",
            "properties": {
                "archetype": {"type": "string", "enum": list(options)},
                "runner_up": {"type": "string", "enum": list(options)},
                # ★ J-01 asks for this explicitly: "state in one sentence what
                #   would settle it". A classification with no falsifier is an
                #   opinion; with one it is a claim.
                "what_would_settle_it": {"type": "string"},
                "why": {"type": "string"},
            },
            "required": ["archetype", "runner_up", "what_would_settle_it", "why"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="⚠ spends money")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ticker", default="MU")
    args = ap.parse_args()
    if not (args.live or args.dry_run):
        ap.print_help()
        return 2

    from tools.run_extraction_once import _select
    _select(args.ticker)

    blk = j01_v1()
    full = build_bundle()
    # ★★ RA-14 / MP-3 — the blind bundle, built by the contract's own method.
    blind = full.redact()
    body = "\n\n".join(p.content for p in blind.parts)
    # ⚠⚠ `DX-67` — the SHARED ENVELOPE. §4.0: *"Composed into every J-block:
    #   S-1…S-6, plus S-7 in Stage A."* The first `J-01` run sent `blk.text`
    #   alone, so its recorded output carries no FACT/INFERENCE/ASSUMPTION tags
    #   — nothing asked for them. ★ `stage_a` is declared from the block's own
    #   `view`, which `STAGE_VIEW` sets to "blind" for Stage A.
    prompt = compose_prompt(blk, stage_a=(blk.view == "blind"))
    payload = f"{prompt}\n\n---\n\n{body}"
    # ⚠ MEASURED 2026-09-10: `//4` predicted 52,912 tokens and the call billed
    # **70,371** — a 33% underestimate on filing text. ★ Filing prose tokenises
    # nearer 3 chars/token than 4 (tables, tickers, numbers), so estimates for
    # THIS corpus use 3.
    est_in = len(payload) // 3

    print("── J-01 · industry archetype (judgement, blind) ──")
    print(f"  ticker     : {args.ticker}   accession {ACCESSION}")
    print(f"  block      : {blk.name} {blk.version}  kind={blk.kind}  view={blk.view}")
    print(f"  hash       : {blk.declared_hash[:20]}…   options={len(blk.options)}")
    print(f"  bundle     : {len(body):,} chars (blind)   ≈ {est_in:,} in tok")
    print(f"  estimate   : ${est_in*PRICE_IN + 1200*PRICE_OUT:.2f}")
    if args.dry_run:
        print("\n  ★ dry run — nothing sent.")
        return 0

    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import traced_transport
    from tools.anthropic_transport import anthropic_transport

    run_id = (f"run-{datetime.now(timezone.utc):%Y-%m-%dT%H%M%S}"
              f"-{args.ticker.lower()}-j01")
    store = TraceStore(REPO / ".state/runs", run_id)
    transport = traced_transport(
        anthropic_transport(tool=judgement_tool(blk.options), max_output=MAX_OUT),
        store, step_id=f"judge:{blk.name}", kind="llm",
        # ⚠⚠ `cost_of(model_id, TOKENS)` receives the NORMALISED `{input,
        # output}` dict, not the raw response. The first version read
        # `tokens_in`/`tokens_out` — absent from that dict — so every lookup
        # returned 0 and the trace recorded **`cost_usd: 0.0` on a $0.37 call**
        # (`DX-65`). ★★ That is `C12` returning through the very argument added
        # to fix it, and it is worse than `None`: `run_extraction_once::_cost_of`
        # returns None when a rate is missing precisely because **an absent cost
        # reads as "unknown" and a zero reads as "free"**.
        cost_of=lambda _m, tokens: (tokens.get("input", 0) * PRICE_IN
                                    + tokens.get("output", 0) * PRICE_OUT),
        prompt_version=blk.version)

    result = transport({"model": MODEL, "max_tokens": MAX_OUT, "payload": payload})
    store.close()

    text = result.get("text") or ""
    try:
        parsed = json.loads(text[text.index("{"):text.rindex("}") + 1])
    except Exception:
        parsed = {"_unparsed": text[:400]}
    tin, tout = result.get("tokens_in", 0), result.get("tokens_out", 0)
    print(f"\n  ✅ {tin:,} in / {tout:,} out   "
          f"${tin*PRICE_IN + tout*PRICE_OUT:.4f}   run_id={run_id}")
    print(json.dumps(parsed, indent=2)[:900])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
