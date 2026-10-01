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

from src.fundamental.claims.models import sector_citation  # noqa: E402
from src.fundamental.prompts.e_blocks import (  # noqa: E402
    BLOCKS,
    EMITS_RUBRIC,
    ENUM_ANSWER,
    FIELD_ENUMS,
    PROSE_REQUIRED,
)
from src.fundamental.prompts.envelope import compose_prompt  # noqa: E402
from tools.run_extraction_once import (  # noqa: E402
    ACCESSION,
    SUBJECT_NAMES,
    build_bundle,
    sector_bundle,
)

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
    from src.fundamental.scorecard.rubrics.b43_v3 import PUBLISHED_RUBRICS

    # ★ `DX-99` — one list of every published version, shared with the tests.
    reg = RubricRegistry(PUBLISHED_RUBRICS)
    dimension, _, version = EMITS_RUBRIC[block_id].partition("@v")
    return reg.get(dimension, int(version))


#: ✏ 2026-09-14 — `J-20` joins (Victor, L3 §2.1g step 1): +≈$0.50 per `--stage-a`, and
#:   `--stage-a` now REQUIRES `--annual-history`, the part `J-20` chooses a window from.
STAGE_A_ORDER = ("J-01", "J-02", "J-03", "J-04", "J-05", "J-06", "J-07", "J-08", "J-20")


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
    if block.name == "J-20":
        return "normalisation"        # ★ `F10` `D5` — a method + window, never a figure
    return "prose"


def judgement_tool(block, *, criteria: tuple[str, ...] = ()) -> dict:
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
        from src.fundamental.scorecard.selection import INSUFFICIENT_EVIDENCE

        dimension = EMITS_RUBRIC[block.name].partition("@v")[0]
        if not criteria:
            raise ValueError(
                f"{block.name} emits {EMITS_RUBRIC[block.name]} and no criteria "
                f"were supplied. ⚠ RA-32 — a level whose `evidence_required` is "
                f"absent from the bundle is UNAVAILABLE, so the enum is a "
                f"property of THIS CALL's bundle, not of the rubric. Passing the "
                f"full set by default would silently re-offer levels the "
                f"evidence cannot support."
            )
        return {
            "name": f"score_{dimension}",
            "description": (f"Select the ONE {dimension} criterion the evidence "
                            f"satisfies, copied exactly, and justify it."),
            "input_schema": {
                "type": "object",
                "properties": {
                    # ⛔⛔ `DX-100` — this was `level: integer enum [4..0]` and
                    #   the criterion text was sent NOWHERE: the model picked a
                    #   number it was never told the meaning of. ★ `RA-31`: the
                    #   answer is the CRITERION; the score is derived from it
                    #   (`scorecard/selection.py::resolve` → `derive_score`).
                    #   ★ `MP-7`: `insufficient_evidence` is a stated exit, so
                    #   the floor is never used to mean "cannot grade".
                    "criterion": {"type": "string",
                                  "enum": [*criteria, INSUFFICIENT_EVIDENCE]},
                    "why": {"type": "string"},
                    # ★ Every rubric block ends with the same instruction:
                    #   "Name the observation that would move you down one level."
                    "what_would_move_it_down": {"type": "string"},
                },
                "required": ["criterion", "why", "what_would_move_it_down"],
            },
        }

    if shape == "normalisation":
        from src.fundamental.prompts.e_blocks import J20_METHODS

        year = {"type": ["integer", "null"]}
        return {
            "name": "choose_normalised_earnings",
            "description": "Choose the method and window code will apply. Never a figure.",
            "input_schema": {
                "type": "object",
                "properties": {
                    # ★ `MP-5` — the closed set is the enum. ⚠ There is no field
                    #   for an amount: `F10` `D5` keeps every figure out of the model.
                    "method": {"type": "string", "enum": list(J20_METHODS)},
                    "first_fiscal_year": year, "last_fiscal_year": year,
                    "trough_year": year, "peak_year": year,
                    "exclusions": {"type": "array", "items": {
                        "type": "object",
                        "properties": {"item": {"type": "string"},
                                       "evidence_id": {"type": "string"},
                                       "quote": {"type": "string"}},
                        "required": ["item", "evidence_id", "quote"]}},
                    "what_would_change_it": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["method", "first_fiscal_year", "last_fiscal_year",
                             "trough_year", "peak_year", "exclusions",
                             "what_would_change_it", "why"],
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


def build_payload(prompt: str, the_offer, body: str) -> str:
    """The text one judgement call sends: prompt, then the rubric, then the bundle.

    ★★ `DX-100` — a rubric block's CRITERIA sit between its instructions and the
    evidence, so *"Select ONE rubric level"* finally has something to select
    from. ⚠ Only the offered levels' criteria, never their scores (`RA-31`).
    """
    rubric = f"\n\n{the_offer.render()}" if the_offer else ""
    return f"{prompt}{rubric}\n\n---\n\n{body}"


def add_annual_history(bundle, ledger_dir, *, ticker: str):
    """`F10` `D5` — the blind-visible annual FCFF history `J-20` chooses a window from."""
    from pathlib import Path

    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.pit.snapshot import assemble_rows
    from src.fundamental.bundle.assemble import annual_history_part
    from src.fundamental.bundle.models import EvidenceBundle

    rows = assemble_rows(FactLedger(Path(ledger_dir)).read(ticker.upper()), bundle.as_of,
                         source="edgar")
    part = annual_history_part(rows[rows["period_type"] == "annual"], ticker=ticker,
                               as_of=bundle.as_of)
    return (EvidenceBundle(ticker=bundle.ticker, as_of=bundle.as_of,
                           parts=(*bundle.parts, part)), rows)


def _answer_hash(answer: dict) -> str:
    """The committed answer's content hash — what `CT-F10.3` `stage_commit_hash` cites."""
    import hashlib
    body = json.dumps({k: v for k, v in answer.items() if not k.startswith("_")},
                      sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def normalisation_outcome(answer: dict, rows, *, ticker: str, as_of, provenance: dict,
                          bundle) -> str:
    """`J-20`'s choice → the D-01 basis, or the named reason there is none (`P5`).

    ⚠ Stops at the BASIS: `fv_analyst` also needs a price, which this runner has no
    source for (FMP is paid; `value_on_basis` is the next step once one is wired).
    """
    from src.feature_engineer.errors import ValuationUnavailable
    from src.fundamental.valuation.normalise import NoNormalisedBasis, normalise

    if rows is None:
        answer["_basis"] = {"status": "NOT_COMPUTED", "reason": "no --annual-history"}
        return "  → basis NOT computed (no --annual-history)"
    try:
        basis = normalise(answer, quarterly_rows=rows[rows["period_type"] == "quarterly"],
                          annual_rows=rows[rows["period_type"] == "annual"],
                          ticker=ticker, as_of=as_of, provenance=provenance, bundle=bundle)
    except (NoNormalisedBasis, ValuationUnavailable) as exc:   # ⚠ only the DESIGNED refusals
        answer["_basis"] = {"status": "NO_BASIS", "reason": f"{type(exc).__name__}: {exc}"}
        return f"  → NO normalised basis — {type(exc).__name__}: {str(exc)[:120]}"
    answer["_basis"] = json.loads(json.dumps(basis.to_json_obj()))
    return (f"  → normalised basis {basis.label} = "
            f"{basis.base_fcff.amount_minor / 100:,.0f} {basis.base_fcff.currency}")


#: Where a recorded extraction run may live: fresh, or promoted.
RUN_ROOTS = (REPO / ".state/runs", REPO / "tests_src/fixtures/recordings")


def load_extraction_parts(run_ids, filing_bundle, *, ticker: str, sector=None) -> tuple:
    """★★★ `DX-85`ⓒ — recorded E-block runs → VERIFIED `extraction` bundle parts.

    ⚠⚠ Each recording is re-parsed and **re-verified by `X-01` against THIS
    filing bundle** before it may enter. The trace does not record the bundle
    hash an extraction ran over (`DX-95`), so re-verification is what proves the
    quotes belong to this filing: a span that does not resolve here refuses.
    ★ `P5` — a run that did not close `SUCCESS`, holds no extraction call, names
    another ticker, or repeats a block already loaded REFUSES; nothing is
    skipped quietly, because a silently dropped run is a rubric level closed
    for a wiring reason.
    """
    from src.fundamental.bundle.assemble import extractions
    from src.fundamental.claims.verify import x01_verify_extraction
    from src.fundamental.filings.extract import ExtractionPass
    from src.fundamental.filings.models import ExtractionResult
    from tools.run_extraction_once import parse_items

    class _Call:
        def __init__(self, text):
            self.text = self.parsed = text

    # ✏ `DX-124` (2026-09-16) — a recorded run is re-verified against THE BUNDLE IT READ, not
    #   always the filing. An industry `E-13` quotes the peer documents in the sector file, and
    #   those spans cannot resolve in Micron's 10-Q. ★ `DX-95` put `bundle_hash` in every trace
    #   record, which is what makes the choice a LOOKUP rather than a guess.
    sources = {filing_bundle.bundle_hash: filing_bundle}
    if sector is not None:
        sources[sector.bundle_hash] = sector
    parts, seen = [], {}
    for run_id in run_ids:
        root = next((r / run_id for r in RUN_ROOTS if (r / run_id).is_dir()), None)
        if root is None:
            raise FileNotFoundError(f"no recorded run {run_id} under {[str(r) for r in RUN_ROOTS]}")
        if f"-{ticker.lower()}-" not in run_id:
            raise ValueError(f"{run_id} is not a {ticker} run — its evidence is another company's")
        records = [json.loads(ln) for ln in (root / "trace.jsonl").read_text().splitlines() if ln]
        closed = [r for r in records if r.get("type") == "__run_closed__"]
        if [c.get("status") for c in closed] != ["SUCCESS"]:
            raise ValueError(f"{run_id} did not close SUCCESS ({closed!r}) — "
                             f"a failed or open run is not evidence")
        calls = [r for r in records if r.get("type") == "ExternalCall"
                 and str(r.get("step_id", "")).startswith("extract:")]
        if not calls:
            raise ValueError(f"{run_id} holds no extraction call")
        # ⚠ A run recorded BEFORE `DX-95` carries no bundle hash; it predates the sector path
        #   entirely, so the filing is the only bundle it can have read.
        read = {c.get("bundle_hash") for c in calls}
        source = next((sources[h] for h in read if h in sources), filing_bundle)
        if read - {None} and not (read & set(sources)):
            # ⚠ Not a refusal: a hash can legitimately fail to match a bundle whose TEXT is
            #   unchanged — `DX-102` re-rendered the fixture (header → spaces), so every
            #   recording made before it carries a hash nothing now reproduces. ★ X-01 is the
            #   real check: if the quotes do not resolve in the filing, the load fails loudly
            #   two lines below. This only says WHICH bundle was used and why.
            print(f"  ⚠ {run_id} recorded bundle {sorted(read)[0][:23]}…, which matches neither "
                  f"source; verifying against the filing (a pre-DX-102 recording, RA-2)")
        text = source.of_kind("filing")[0].content if source.of_kind("filing") \
            else source.parts[0].content
        results, versions = [], {}
        for call in calls:
            block_id = call["step_id"].split(":", 1)[1]
            if block_id in seen:
                raise ValueError(
                    f"{block_id} is loaded twice ({seen[block_id]}, {run_id}). ⚠ RA-32 "
                    f"would count the union of two samples as one — pass one run per block")
            seen[block_id] = run_id
            payload = json.loads((root / "trace/payloads" / f"{call['payload_ref']}.json")
                                 .read_text(encoding="utf-8"))["response"]
            body = payload["text"] if isinstance(payload, dict) and "text" in payload else payload
            items = parse_items(_Call(body if isinstance(body, str) else json.dumps(body)), text,
                                # ⚠ `DX-124` — an industry item cites the SECTOR FILE; the
                                #   default is the analysed filing's accession (`DX-121`).
                                accession_id=sector_citation(source.parts[0].pins) or None)
            results.append(ExtractionResult(block_id, source.bundle_hash, tuple(items)))
            versions[block_id] = call["prompt_version"]
        report = x01_verify_extraction(source, [i for r in results for i in r.items])
        # ⛔ `DX-97` — re-applied on load, so a run recorded BEFORE the guard
        #   (the 2026-09-12 E-13) is refused here too.
        from src.fundamental.filings.subject import assert_subject_is_not_registrant
        assert_subject_is_not_registrant(
            results, source,
            # ★ `DX-119` — over the industry bundle the subject is DECLARED: the analysed
            #   company has no cover page there.
            subject=SUBJECT_NAMES[ticker.upper()] if source is not filing_bundle else None)
        parts.extend(extractions(ExtractionPass(results=tuple(results), report=report),
                                 prompt_versions=versions, run_id=run_id))
    return tuple(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="⚠ spends money")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ticker", default="MU")
    # ★★ `DX-81` — `blk = j01_v1()` was hardcoded, so this runner could send
    #    exactly one of the eight declared Stage-A blocks. ⚠ Default stays
    #    `J-01` so every existing invocation and recording is unaffected.
    ap.add_argument("--block", default="J-01",
                    # ✏ 2026-09-14 — BLIND blocks only: `J-09`…`J-17` are full-view and
                    #   need frozen Stage-A evidence; `tools/run_thesis_once.py` runs them.
                    choices=[b for b in sorted(BLOCKS)
                             if BLOCKS[b][0]().kind == "judgement"
                             and BLOCKS[b][0]().view == "blind"],
                    help="which Stage-A judgement block to run")
    # ★★★ `DX-83` — a STAGE is a unit, not eight unrelated calls. Running the
    #   blocks one invocation at a time produced eight `run_id`s with no record
    #   that they belong together, which is precisely what `F2` exists to stop.
    ap.add_argument("--stage-a", action="store_true",
                    help="run ALL Stage-A blocks (STAGE_A_ORDER) into ONE run_id (k=1)")
    # ★★★ `DX-85`ⓒ — the evidence a rubric level cites is EXTRACTION output,
    #   so a rubric block can be scored only over a bundle that carries it.
    ap.add_argument("--extractions", nargs="*", default=(), metavar="RUN_ID",
                    help="recorded E-block runs to add as verified extraction parts")
    # ★ `DX-100` / `RA-17` — the rubric option order is seeded by
    #   `<seed>:<run tag>:<block>` and RECORDED with each call.
    # ★★ `F10` `D5` — J-20 needs the per-year FCFF history, pre-computed, in the
    #   BLIND bundle. Reads D-07's fact ledger (EDGAR, already ingested — free).
    # ★★ `DX-117` — the industry evidence an `E-13` run was extracted from, so its recorded
    #   quotes can be re-verified. ⚠ The peer DOCUMENTS do not enter the judgement bundle:
    #   the verified items do, at a fraction of the tokens.
    ap.add_argument("--sector", default=None, metavar="SECTOR_FILE_JSON",
                    help="sector file an --extractions run read (re-verification source)")
    ap.add_argument("--annual-history", default=None, metavar="LEDGER_DIR",
                    help="D-07 fact ledger dir (e.g. .state/facts) for J-20's history part")
    ap.add_argument("--seed", default="0",
                    help="seed for the recorded rubric option order (RA-17)")
    args = ap.parse_args()
    if not (args.live or args.dry_run):
        ap.print_help()
        return 2

    from tools.run_extraction_once import _select
    _select(args.ticker)

    if args.stage_a and not args.annual_history:
        # ⚠ `J-20` is in Stage A; without its history part it can only answer
        #   `insufficient_evidence` — a paid call with a known answer (`P5`).
        print("BLOCKED: --stage-a includes J-20 and needs --annual-history LEDGER_DIR")
        return 2
    blocks = [BLOCKS[b][0]() for b in STAGE_A_ORDER] if args.stage_a \
        else [BLOCKS[args.block][0]()]

    full = build_bundle()
    if args.extractions:
        from src.fundamental.bundle.models import EvidenceBundle
        extracted = load_extraction_parts(
            args.extractions, full, ticker=args.ticker,
            sector=sector_bundle(args.sector, ticker=args.ticker) if args.sector else None)
        full = EvidenceBundle(ticker=full.ticker, as_of=full.as_of,
                              parts=(*full.parts, *extracted))
        for p in extracted:
            print(f"  extraction : {p.pins['block_id']} {p.pins['prompt_version']}  "
                  f"{p.pins['run_id']}  found={p.pins['evidence_ids'] or 'none'}")
    history_rows = None
    if args.annual_history:
        full, history_rows = add_annual_history(full, args.annual_history,
                                                ticker=args.ticker)
    # ★★ RA-14 / MP-3 — the blind bundle, built by the contract's own method.
    blind = full.redact()
    body = "\n\n".join(p.content for p in blind.parts)

    label = (f"STAGE A · all {len(STAGE_A_ORDER)} blocks, k=1" if args.stage_a
             else blocks[0].name)
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
        the_offer = None
        gate_error = None
        gate_label = ""
        if answer_shape(blk) == "rubric":
            # ★★★ `DX-82` CLOSED — `RA-32` is applied, not warned about.
            from src.fundamental.scorecard.availability import (
                NoAvailableLevel,
                PartialRubricEvidence,
                evidence_ids_in,
                require_levels,
            )
            rubric = _rubric_for(blk.name)
            try:
                levels = require_levels(rubric, evidence_ids_in(blind))
            except PartialRubricEvidence as exc:
                # ⛔ `DX-98` — some levels available, not all: refused, and
                #   said differently, because the fix is a missing E-block run.
                gate_error = str(exc)
                gate_label = "  ⛔ DX-98 REFUSES — partial rubric evidence"
            except NoAvailableLevel as exc:
                gate_error = str(exc)
                gate_label = "  ⛔ RA-32 REFUSES — no level's evidence is in the bundle"
            if not gate_error:
                # ★★ `DX-100` — the levels are OFFERED as criteria, in a seeded
                #   order that is recorded with the call.
                from src.fundamental.scorecard.selection import offer
                the_offer = offer(rubric, levels, seed=f"{args.seed}:{blind.bundle_hash}:{blk.name}")
        # ⚠⚠ `DX-67` — the SHARED ENVELOPE. §4.0: *"Composed into every J-block:
        #   S-1…S-6, plus S-7 in Stage A."* ★ `stage_a` is declared from the
        #   block's own `view`, which `STAGE_VIEW` sets to "blind" for Stage A.
        # ✏ `DX-111` (2026-09-15): `fresh=True` — §4.0 composes `S-8` into every J-block
        #   in fresh authoring, and Stage A IS fresh authoring. Every earlier Stage-A
        #   recording went out without it; that split is DECLARED in the golden test.
        prompt = compose_prompt(blk, stage_a=(blk.view == "blind"), fresh=True)
        payload = build_payload(prompt, the_offer, body)
        # ⚠ MEASURED 2026-09-10: `//4` predicted 52,912 tokens and the call
        # billed **70,371** — a 33% underestimate. ★ Filing prose tokenises
        # nearer 3 chars/token than 4, so estimates for THIS corpus use 3.
        est_in = len(payload) // 3
        plans.append((blk, the_offer, payload, est_in, gate_error))
        gate = (gate_label if gate_error
                else f"  levels={levels} shown as {the_offer.permutation}" if the_offer
                else "")
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
    from tools.llm_transport import dev_transport, price_factor, transport_label

    # ⚠ `DX-83` — the suffix names what actually ran. It was hardcoded `-j01`,
    #   so a `J-05` run would have been filed under `j01` and `DX-70` already
    #   showed what a mislabelled recording costs.
    suffix = "stage-a" if args.stage_a else blocks[0].name.lower().replace("-", "")
    run_id = (f"run-{datetime.now(timezone.utc):%Y-%m-%dT%H%M%S}"
              f"-{args.ticker.lower()}-{suffix}")
    store = TraceStore(REPO / ".state/runs", run_id)
    print(f"  transport  : {transport_label()}")
    paid = price_factor()                  # ★ GW-27 — 0.0 on the subscription

    spent, answers, failed = 0.0, {}, []
    for blk, the_offer, payload, _est, gate_error in plans:
        criteria = the_offer.criteria if the_offer else ()
        if gate_error:
            # ★★★ `RA-32` refuses BEFORE the call, so it costs nothing. ⚠ The
            # ungated run answered these blocks anyway and returned 1 / 3 / 3 /
            # 0 — numbers resting on nothing structural, for $2.6.
            failed.append((blk.name, gate_error))
            print(f"   ⛔ {blk.name}: NOT SENT — {gate_error.splitlines()[0]}")
            continue
        transport = traced_transport(
            dev_transport(tool=judgement_tool(blk, criteria=criteria),
                                max_output=MAX_OUT),
            store, step_id=f"judge:{blk.name}", kind="llm",
            # ⚠⚠ `cost_of(model_id, TOKENS)` receives the NORMALISED `{input,
            # output}` dict, not the raw response (`DX-65`) — an absent cost
            # reads as "unknown" and a zero reads as "free".
            cost_of=lambda _m, tokens: (tokens.get("input", 0) * PRICE_IN
                                        + tokens.get("output", 0) * PRICE_OUT) * paid,
            prompt_version=blk.version,
            # ⚠⚠ `DX-76` — the judgement envelope differs from the extraction
            # one (`S-7` is Stage-A only), so the hash uses the SAME flags
            # `compose_prompt` was given, not a constant.
            envelope_hash=envelope_hash("judgement",
                                        stage_a=(blk.view == "blind"), fresh=True),
            # ★★ `DX-95` — the BLIND bundle this call read; since `DX-85`ⓒ it
            #   differs by which extraction runs were loaded.
            bundle_hash=blind.bundle_hash)
        try:
            request = {"model": MODEL, "max_tokens": MAX_OUT, "payload": payload}
            if the_offer:
                # ★ `RA-17` — the order SHOWN, recorded in the call's own trace
                #   payload (the transport ignores keys it does not read).
                request["option_permutation"] = list(the_offer.permutation)
                request["option_seed"] = the_offer.seed
            result = transport(request)
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
        missing = [f for f in judgement_tool(blk, criteria=criteria)["input_schema"]
                   ["required"] if f not in answers[blk.name]]
        if missing:
            failed.append((blk.name, f"missing required field(s) {missing}"))
            print(f"   ⛔ {blk.name}: parsed but INCOMPLETE — missing {missing}")
            continue
        tin, tout = result.get("tokens_in", 0), result.get("tokens_out", 0)
        cost = (tin * PRICE_IN + tout * PRICE_OUT) * paid
        spent += cost
        derived = ""
        if the_offer:
            # ★★★ `DX-100` — the score is DERIVED from the echoed criterion,
            #   through `derive_score`; an invented or un-offered criterion, or
            #   a level without its evidence, refuses (`RA-31`, `RA-32`).
            from src.fundamental.errors import LevelUnavailableError, ScoreEmittedError
            from src.fundamental.scorecard.availability import evidence_ids_in
            from src.fundamental.scorecard.selection import resolve
            try:
                score = resolve(the_offer, answers[blk.name], evidence_ids_in(blind))
            except (ScoreEmittedError, LevelUnavailableError) as exc:
                failed.append((blk.name, f"{type(exc).__name__}: {exc}"))
                print(f"   ⛔ {blk.name}: answered, but NO SCORE — {exc}")
                continue
            answers[blk.name]["_derived"] = (
                {"score": score.score, "rubric_id": score.rubric_id} if score
                else {"score": None, "outcome": "INSUFFICIENT_EVIDENCE"})
            derived = (f"  → {score.rubric_id} score={score.score}" if score
                       else "  → INSUFFICIENT_EVIDENCE (not a score)")
        if answer_shape(blk) == "normalisation":
            derived = normalisation_outcome(answers[blk.name], history_rows,
                                            ticker=args.ticker, as_of=full.as_of,
                                            provenance={"prompt_version": blk.version,
                                                        "run_id": run_id,
                                                        "stage_commit_hash": _answer_hash(answers[blk.name]),
                                                        "bundle_hash": blind.bundle_hash},
                                            bundle=blind)
        print(f"   ✅ {blk.name}  {tin:,} in / {tout:,} out  ${cost:.4f}{derived}")
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
