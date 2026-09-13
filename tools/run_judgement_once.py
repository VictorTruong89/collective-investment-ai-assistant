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

from src.fundamental.prompts.e_blocks import (  # noqa: E402
    BLOCKS,
    EMITS_RUBRIC,
    ENUM_ANSWER,
    FIELD_ENUMS,
    PROSE_REQUIRED,
)
from src.fundamental.prompts.envelope import compose_prompt  # noqa: E402
from tools.run_extraction_once import ACCESSION, build_bundle  # noqa: E402

MODEL = "claude-opus-5"
PRICE_IN, PRICE_OUT = 5 / 1_000_000, 25 / 1_000_000
#: ⚠⚠⚠ `DX-84` — 4,000 was a THIRD output budget, smaller than either of the
#: two that already existed, and it silently truncated 7 of 8 Stage-A calls.
#: ★ It now takes `call.py`'s judgement budget, which is the number the
#: extraction path has been using all along. One fact, one place.
from src.fundamental.prompts.call import MAX_TOKENS  # noqa: E402

MAX_OUT = MAX_TOKENS["judgement"]

#: ★ `DX-83` — Stage A in its declared order (`STAGE_BLOCKS["A"]`).
def _rubric_for(block_id: str):
    """The published `Rubric` a block emits (`EMITS_RUBRIC`, `DX-80`, `DX-86`).

    ★ Both versions are published: `v2` is what the blocks emit, `v1` stays
    resolvable so a baseline recorded against it can still be read (`RA-52`).
    """
    from src.fundamental.scorecard.registry import RubricRegistry
    from src.fundamental.scorecard.rubrics.b43_v1 import B43_RUBRICS
    from src.fundamental.scorecard.rubrics.b43_v2 import B43_V2_RUBRICS

    reg = RubricRegistry((*B43_RUBRICS, *B43_V2_RUBRICS))
    dimension, _, version = EMITS_RUBRIC[block_id].partition("@v")
    return reg.get(dimension, int(version))


STAGE_A_ORDER = ("J-01", "J-02", "J-03", "J-04", "J-05", "J-06", "J-07", "J-08")


def answer_shape(block) -> str:
    """`DX-81` — which of THREE answer shapes this judgement block returns.

    ★★ Derived, never declared a second time. `enum` ⟺ the block names an answer
    field in `ENUM_ANSWER`; `rubric` ⟺ it emits a scorecard rubric; `prose`
    otherwise. ⚠ A fourth mapping saying "J-04 is a rubric block" would be a
    second place to keep in step with `EMITS_RUBRIC`, and `DX-80` is what
    happens when two places hold one fact.
    """
    if block.name in ENUM_ANSWER:
        return "enum"
    if block.name in EMITS_RUBRIC:
        return "rubric"
    return "prose"


def judgement_tool(block, *, levels: tuple[int, ...] = ()) -> dict:
    """`MP-5` — the closed set is declared as an ENUM, never described.

    ⚠⚠ Both of `extraction_tool`'s measured defects were the same mistake:
    *describing* a constraint instead of *declaring* it. `J-01` names seven
    archetypes in its prose; if the schema left `archetype` a free string the
    model could return an eighth, and `RA-17`'s closed set would be a
    suggestion. ★ `insufficient_evidence` is in the enum because `MP-7` says a
    block with no way to say *"I could not"* will always find something to say.

    ★★★ **`DX-81`, 2026-09-11 — this used to return ONE schema.** It took a bare
    options tuple, hardcoded the name `classify_archetype` and the field
    `archetype`, and `main()` hardcoded `j01_v1()`. That fits `J-01` and `J-07`;
    for the other six Stage-A blocks it would have demanded an enum answer the
    block never asks for — **and the model would have supplied one**, which is
    exactly the `E-01` failure `MP-5` was learned from.

    ⚠⚠ **What is deliberately NOT captured, so it is not discovered later.**
    `J-03`'s STEP 1 mechanism table (five mechanisms × present/absent/
    insufficient_evidence) and `J-08`'s per-competitor sentences are structured
    answers this schema folds into `why`. ★ They are real fields and they are
    not modelled yet; `DX-81` records that rather than letting the first reader
    assume the schema is complete.
    """
    shape = answer_shape(block)
    if shape == "enum":
        tool_name, field = ENUM_ANSWER[block.name]
        options = list(block.options)
        return {
            "name": tool_name,
            "description": f"Return the single {field} this company belongs to.",
            "input_schema": {
                "type": "object",
                "properties": {
                    field: {"type": "string", "enum": options},
                    "runner_up": {"type": "string", "enum": options},
                    # ★ The block asks for this explicitly: "state in one
                    #   sentence what would settle it". A classification with no
                    #   falsifier is an opinion; with one it is a claim.
                    "what_would_settle_it": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": [field, "runner_up", "what_would_settle_it", "why"],
            },
        }

    if shape == "rubric":
        dimension = EMITS_RUBRIC[block.name].partition("@v")[0]
        if not levels:
            raise ValueError(
                f"{block.name} emits {EMITS_RUBRIC[block.name]} and no levels "
                f"were supplied. ⚠ RA-32 — a level whose `evidence_required` is "
                f"absent from the bundle is UNAVAILABLE, so the enum is a "
                f"property of THIS CALL's bundle, not of the rubric. Passing the "
                f"full 0-4 by default would silently re-offer levels the "
                f"evidence cannot support."
            )
        return {
            "name": f"score_{dimension}",
            "description": f"Select one {dimension} rubric level and justify it.",
            "input_schema": {
                "type": "object",
                "properties": {
                    # ⚠ An INT enum, not a string: the rubric's levels are
                    #   ordered and `MIN_SCORE`/`MAX_SCORE` are numeric. A string
                    #   "3" would compare wrong against the scorecard.
                    "level": {"type": "integer", "enum": list(levels)},
                    "why": {"type": "string"},
                    # ★ Every rubric block ends with the same instruction:
                    #   "Name the observation that would move you down one level."
                    "what_would_move_it_down": {"type": "string"},
                },
                "required": ["level", "why", "what_would_move_it_down"],
            },
        }

    props: dict = {"answer": {"type": "string"}}
    required = ["answer"]
    for name in PROSE_REQUIRED.get(block.name, ()):
        # ★★ `J-02` item 5: "is mandatory and may not be 'nothing'". A REQUIRED
        #    field enforces that; a sentence asks for it.
        props[name] = {"type": "string"}
        required.append(name)
    for name, enum in FIELD_ENUMS.get(block.name, {}).items():
        props[name] = {"type": "string", "enum": list(enum)}
        required.append(name)
    return {
        "name": f"answer_{block.name.replace('-', '_').lower()}",
        "description": f"Answer {block.name}, grounded per S-3.",
        "input_schema": {"type": "object", "properties": props,
                         "required": required},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="⚠ spends money")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ticker", default="MU")
    # ★★ `DX-81` — `blk = j01_v1()` was hardcoded, so this runner could send
    #    exactly one of the eight declared Stage-A blocks. ⚠ Default stays
    #    `J-01` so every existing invocation and recording is unaffected.
    ap.add_argument("--block", default="J-01",
                    choices=[b for b in sorted(BLOCKS)
                             if BLOCKS[b][0]().kind == "judgement"],
                    help="which Stage-A judgement block to run")
    # ★★★ `DX-83` — a STAGE is a unit, not eight unrelated calls. Running the
    #   blocks one invocation at a time produced eight `run_id`s with no record
    #   that they belong together, which is precisely what `F2` exists to stop.
    ap.add_argument("--stage-a", action="store_true",
                    help="run ALL 8 Stage-A blocks into ONE run_id (k=1)")
    args = ap.parse_args()
    if not (args.live or args.dry_run):
        ap.print_help()
        return 2

    from tools.run_extraction_once import _select
    _select(args.ticker)

    blocks = [BLOCKS[b][0]() for b in STAGE_A_ORDER] if args.stage_a \
        else [BLOCKS[args.block][0]()]

    full = build_bundle()
    # ★★ RA-14 / MP-3 — the blind bundle, built by the contract's own method.
    blind = full.redact()
    body = "\n\n".join(p.content for p in blind.parts)

    label = "STAGE A · all 8 blocks, k=1" if args.stage_a else blocks[0].name
    print(f"── {label} (judgement, blind) ──")
    print(f"  ticker     : {args.ticker}   accession {ACCESSION}")
    print(f"  bundle     : {len(body):,} chars (blind)")

    plans = []
    for blk in blocks:
        # ⚠⚠ `RA-32` — a rubric block's enum is a property of THIS CALL's
        # bundle, not of the rubric: a level whose `evidence_required` is absent
        # is UNAVAILABLE. ★ The full published range is passed EXPLICITLY here,
        # in the composition root where it is visible, rather than defaulted
        # inside `judgement_tool` where it would look like a property of the
        # schema. `DX-82` tracks closing it properly.
        levels: tuple[int, ...] = ()
        gate_error = None
        if answer_shape(blk) == "rubric":
            # ★★★ `DX-82` CLOSED — `RA-32` is applied, not warned about.
            from src.fundamental.scorecard.availability import (
                NoAvailableLevel,
                evidence_ids_in,
                require_levels,
            )
            rubric = _rubric_for(blk.name)
            try:
                levels = require_levels(rubric, evidence_ids_in(blind))
            except NoAvailableLevel as exc:
                gate_error = str(exc)
        # ⚠⚠ `DX-67` — the SHARED ENVELOPE. §4.0: *"Composed into every J-block:
        #   S-1…S-6, plus S-7 in Stage A."* ★ `stage_a` is declared from the
        #   block's own `view`, which `STAGE_VIEW` sets to "blind" for Stage A.
        prompt = compose_prompt(blk, stage_a=(blk.view == "blind"))
        payload = f"{prompt}\n\n---\n\n{body}"
        # ⚠ MEASURED 2026-09-10: `//4` predicted 52,912 tokens and the call
        # billed **70,371** — a 33% underestimate. ★ Filing prose tokenises
        # nearer 3 chars/token than 4, so estimates for THIS corpus use 3.
        est_in = len(payload) // 3
        plans.append((blk, levels, payload, est_in, gate_error))
        gate = ("  ⛔ RA-32 REFUSES — no level's evidence is in the bundle"
                if gate_error else f"  levels={levels}" if levels else "")
        print(f"   {blk.name} {blk.version}  {answer_shape(blk):<7} "
              f"hash={blk.declared_hash[:16]}…  ≈{est_in:,} in{gate}")

    billable = [p for p in plans if not p[4]]
    est = sum(p[3] * PRICE_IN for p in billable) + len(billable) * MAX_OUT * PRICE_OUT
    print(f"  estimate   : ${est:.2f}  ({len(billable)} billable call(s)"
          f"{f', {len(plans) - len(billable)} REFUSED before sending' if len(billable) != len(plans) else ''})")
    if args.dry_run:
        print("\n  ★ dry run — nothing sent.")
        return 0

    from src.fundamental.prompts.envelope import envelope_hash
    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import traced_transport
    from tools.anthropic_transport import anthropic_transport

    # ⚠ `DX-83` — the suffix names what actually ran. It was hardcoded `-j01`,
    #   so a `J-05` run would have been filed under `j01` and `DX-70` already
    #   showed what a mislabelled recording costs.
    suffix = "stage-a" if args.stage_a else blocks[0].name.lower().replace("-", "")
    run_id = (f"run-{datetime.now(timezone.utc):%Y-%m-%dT%H%M%S}"
              f"-{args.ticker.lower()}-{suffix}")
    store = TraceStore(REPO / ".state/runs", run_id)

    spent, answers, failed = 0.0, {}, []
    for blk, levels, payload, _est, gate_error in plans:
        if gate_error:
            # ★★★ `RA-32` refuses BEFORE the call, so it costs nothing. ⚠ The
            # ungated run answered these blocks anyway and returned 1 / 3 / 3 /
            # 0 — numbers resting on nothing structural, for $2.6.
            failed.append((blk.name, gate_error))
            print(f"   ⛔ {blk.name}: NOT SENT — {gate_error.splitlines()[0]}")
            continue
        transport = traced_transport(
            anthropic_transport(tool=judgement_tool(blk, levels=levels),
                                max_output=MAX_OUT),
            store, step_id=f"judge:{blk.name}", kind="llm",
            # ⚠⚠ `cost_of(model_id, TOKENS)` receives the NORMALISED `{input,
            # output}` dict, not the raw response (`DX-65`) — an absent cost
            # reads as "unknown" and a zero reads as "free".
            cost_of=lambda _m, tokens: (tokens.get("input", 0) * PRICE_IN
                                        + tokens.get("output", 0) * PRICE_OUT),
            prompt_version=blk.version,
            # ⚠⚠ `DX-76` — the judgement envelope differs from the extraction
            # one (`S-7` is Stage-A only), so the hash uses the SAME flags
            # `compose_prompt` was given, not a constant.
            envelope_hash=envelope_hash("judgement",
                                        stage_a=(blk.view == "blind")))
        try:
            result = transport({"model": MODEL, "max_tokens": MAX_OUT,
                                "payload": payload})
        except Exception as exc:                       # noqa: BLE001
            # ⚠⚠ `P5` — one block failing must not discard the seven that
            # succeeded, and it must NOT be reported as a completed Stage A.
            # ★ The trace already records the failure (`traced_transport`
            #   re-raises after appending); this keeps the run going and the
            #   summary honest.
            failed.append((blk.name, f"{type(exc).__name__}: {exc}"))
            print(f"   ⛔ {blk.name}: {type(exc).__name__}")
            continue
        # ★★★ `DX-84` / `GW-23` — *a truncated response is a failure, not a
        # short answer.* ⚠⚠ This runner wires `anthropic_transport` STRAIGHT
        # into `traced_transport`, so it never reaches `Gateway.call` and
        # `GW-23` never ran. 7 of 8 calls came back `stop_reason: max_tokens`
        # and every one printed ✅ — a false success report on $3.22 of
        # unusable output.
        stop = (result.get("stop_reason") or "").lower()
        if stop == "max_tokens":
            failed.append((blk.name, f"truncated at max_tokens={MAX_OUT}"))
            print(f"   ⛔ {blk.name}: TRUNCATED (stop_reason=max_tokens) — "
                  f"GW-23: a truncated response is a failure, not a short answer")
            continue
        text = result.get("text") or ""
        try:
            answers[blk.name] = json.loads(text[text.index("{"):text.rindex("}") + 1])
        except Exception:                              # noqa: BLE001
            answers[blk.name] = {"_unparsed": text[:300]}
        # ⚠ `MP-5` — the schema DECLARES required fields; the vendor is not
        # obliged to honour them on a degraded call. ★ `J-01`'s truncated run
        # dropped `why` and still parsed as JSON, so "it parsed" is not "it is
        # complete" — the same mistake `DX-68` taught about "it parses now".
        missing = [f for f in judgement_tool(blk, levels=levels)["input_schema"]
                   ["required"] if f not in answers[blk.name]]
        if missing:
            failed.append((blk.name, f"missing required field(s) {missing}"))
            print(f"   ⛔ {blk.name}: parsed but INCOMPLETE — missing {missing}")
            continue
        tin, tout = result.get("tokens_in", 0), result.get("tokens_out", 0)
        cost = tin * PRICE_IN + tout * PRICE_OUT
        spent += cost
        print(f"   ✅ {blk.name}  {tin:,} in / {tout:,} out  ${cost:.4f}")
    store.close()

    print(f"\n  run_id={run_id}   spent ${spent:.4f}   "
          f"{len(answers)}/{len(plans)} block(s)")
    if failed:
        # ★ `PG-10`'s shape: the artifact states its own limitation.
        print(f"  ⚠⚠ INCOMPLETE — {len(failed)} block(s) failed: "
              f"{[n for n, _ in failed]}. This is NOT a Stage A.")
    print(json.dumps(answers, indent=2)[:2000])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
