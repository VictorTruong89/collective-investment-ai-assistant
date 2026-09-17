#!/usr/bin/env python3
"""Stages B–D over a FROZEN Stage A — the first complete thesis (L3 §2.1g steps 4–5).

    python3 tools/run_thesis_once.py --dry-run                 # ★ free: the plan and its cost
    python3 tools/run_thesis_once.py --live --budget-usd 15    # ⚠ SPENDS — stops at the cap

★★ **What this runner guarantees, and where each guarantee lives.**

```text
  STAGE A    loaded from RECORDED runs, re-validated, COMMITTED     RA-108 — frozen, hashed
  STAGE B    J-09 → J-10          sees A (J-10 also J-09)         view:full (price revealed)
  STAGE C    J-11 · J-12 · J-13×n see A+B, NOT each other          RA-15 — separate calls
             J-14                 sees A+B+C                       "the analysis produced so far"
  STAGE D    J-15 → COMMIT → J-16 → J-17                            RA-16 — falsifiers first
```

⚠ **Every output is committed, and persisted to `commits.jsonl`, BEFORE a later call
can read it** — and a later call reads it only as a `stage_output` bundle part pinned by
the commit hash, so its `bundle_hash` proves which commitment it read (`RA-1`, `RA-2`).
⚠ J-16 is not issued unless J-15's falsifiers passed `Falsifier`'s own validation and
were committed: `Thesis` cannot be built without that commit hash (`RA-16`).

✏ **`DX-109` ⓐ (Victor, 2026-09-14): `J-09` is declared verbatim** and the inputs it
names that do not exist are NAMED ABSENT in the bundle (`STAGE_B_ABSENCES`).

★ Composition root (`CA-9`), like `run_judgement_once.py`: the only place that knows the
fixtures, the ledger, the recorded price, the trace store and the vendor at once.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.fundamental.prompts.e_blocks import (  # noqa: E402
    BLOCKS,
    J09_VERSUS_OPTIONS,
    J10_TYPICALITY,
    J13_FINANCIALS_ONLY,
    J13_METRICS,
    J13_STATUS,
    J16_CONVICTIONS,
    J16_VERDICTS,
    J17_OBTAINABLE,
    METRIC_PLACEHOLDER,
)
from src.fundamental.prompts.envelope import compose_prompt  # noqa: E402
from tools.run_judgement_once import (  # noqa: E402
    MAX_OUT,
    MODEL,
    PRICE_IN,
    PRICE_OUT,
    RUN_ROOTS,
    _answer_hash,
    _rubric_for,
    answer_shape,
    build_payload,
    judgement_tool,
)

# ═══════════════════════════════════════════════════════════════════════════
# The inputs of the first thesis — MU, the FY2025 Q3 10-Q, as of 2025-06-26
# ═══════════════════════════════════════════════════════════════════════════

#: Stage A, block → the RECORDED run that answered it. ★ Explicit per block: two runs
#: holding one block would otherwise be resolved by arrival order.
#: ⚠ `J-01` `J-02` `J-07` `J-08` come from the 2026-09-12 complete Stage A, which predates
#: `DX-95` (no `bundle_hash` recorded) and `DX-102` (the fixture header was in its bundle).
#: ★ `J-05`/`J-06` are the criterion-selected, golden-established runs (`DX-100`, `DX-101`).
DEFAULT_STAGE_A = {
    "J-01": "run-2026-09-12T024848-mu-stage-a",
    "J-02": "run-2026-09-12T024848-mu-stage-a",
    "J-05": "run-2026-09-13T184111-mu-j05",
    "J-06": "run-2026-09-13T184227-mu-j06",
    "J-07": "run-2026-09-12T024848-mu-stage-a",
    # ✏ 2026-09-16 — re-run over the INDUSTRY evidence (`DX-117`): `J-03` is scored for the
    #   first time (moat_durability@v2 = 2) and `J-08` answered with competitor capacity in
    #   the bundle rather than absent from it (its read is still `insufficient_evidence`).
    "J-03": "run-2026-09-16T130712-mu-j03",
    "J-08": "run-2026-09-16T130840-mu-j08",
    "J-20": "run-2026-09-14T122547-mu-j20",
}

#: Stage-A blocks with NO usable answer, and why — carried into the frozen commit and
#: into the bundle as named absences, never silently dropped (`P5`).
STAGE_A_ABSENT = {
    # ✅ `J-03` left this list 2026-09-16: the industry sector file supplied `cx.capacity`.
    "J-04": ("earnings_quality@v3 needs searched:ap.change, and E-09 was SKIPPED after five "
             "truncated runs (DX-96) — the dimension cannot be scored"),
}

#: The E-block runs `J-05`/`J-06` were scored over — the same evidence, re-verified by
#: `X-01` on load (`load_extraction_parts`).
DEFAULT_EXTRACTIONS = (
    "run-2026-09-12T221728-mu-e04", "run-2026-09-12T221836-mu-e06",
    "run-2026-09-12T222114-mu-e07", "run-2026-09-13T071638-mu-e10",
    "run-2026-09-13T071852-mu-e12",
    # ✏ 2026-09-16 (`DX-117`) — segment rows and the INDUSTRY capacity evidence. Measured:
    #   scorecard coverage 0.583 → **0.917** (moat 0.00 → 1.00, earnings quality 0.33 → 0.67).
    "run-2026-09-11T082002-mu-e01", "run-2026-09-16T070237-mu-e13-replay",
    # ✏ 2026-09-17 — `E-09` completed at LAST, at `--effort low` ($0.42, 1,639 out against five
    #   truncations at 20,000). It supplies `searched:ap.change`, the final missing marker:
    #   scorecard coverage **0.917 → 1.000** (`DX-129`).
    "run-2026-09-17T071619-mu-e09",
)

#: The sector file the industry `E-13` read — needed to RE-VERIFY its quotes (`DX-124`).
DEFAULT_SECTOR = REPO / ".state/sector/memory_v1_2025-06-26.json"

#: ★ The RAW daily close, recorded from FMP once (`historical-price-eod/non-split-adjusted`,
#: 2026-09-14, approved) — `fmp-api` trap 2: the `adj*` field names are the RAW series.
PRICE_FIXTURE = REPO / "tests_src/fixtures/prices/MU_raw_eod_2025-06.json"
ASSUMPTIONS = ("dcf_two_stage", 1)

#: ✏ `DX-109` ⓐ — what Stages B–D ask for and this bundle does not carry, with why.
STAGE_B_ABSENCES = {
    "consensus_forward_estimates": (
        "FMP analyst-estimates is Class B: its date is the TARGET period and it has no "
        "publication axis, so what consensus expected on the bundle's as_of cannot be "
        "reconstructed (fmp-api trap 5; L3 DX-109)"),
    "consensus_rating_and_price_target_actions": (
        "event-dated and reconstructable (FMP grades, price-target-news are Class A) but NOT "
        "fetched for this bundle (L3 DX-109)"),
    "implied_margin": "D-02 solves only the stage-1 growth the price requires (F10 D7)",
    "implied_duration": (
        "D-02 solves only stage-1 growth; the 10-year explicit period is a DECLARED "
        "assumption, not an implied figure (F10 D4, D7)"),
    "market_capitalisation": (
        "no D-02 output computes it; combining the raw price and share count is D-02's "
        "arithmetic, not this bundle's (RA-45)"),
    "valuation_multiples": "D-02 has no multiples output (F10 non-goal)",
    "reference_class_base_rates": (
        "the bundle is single-company; no reference-class dataset exists (master prompt "
        "J-10 note)"),
    "peer_set_figures": "no peer or industry part kind exists (L3 §2.1e)",
    "falsifier_deadline_calendar": (
        "no earnings calendar is in the bundle; a deadline is a date you state, and it must "
        "fall after the bundle's as_of"),
}


#: ⛔ `DX-114` (measured 2026-09-15, `run-2026-09-15T025134-mu-thesis`): `J-13` on
#: `return_on_equity` spent the whole 16,000-token cap on hidden THINKING —
#: `stream_chars` thinking-invisible, `tool_input 0` — and returned nothing ($1.12). The
#: `DX-96` shape on a judgement block. ★ `effort` bounds thinking (the supported lever,
#: thinking stays ON per `GW-9c`); the larger cap leaves room for twelve evidenced
#: mechanisms. Every other block keeps the defaults it already succeeded under.
#: ✏ `DX-115` (2026-09-15): `J-14` ran away the same way at default effort with 193k input.
#: ★ The cause is GENERAL (a long, sweeping judgement over a large bundle), so the fix goes to
#: every block that shares it — J-14…J-17 all read MORE context than J-13 did.
_BOUNDED = {"max_tokens": 32_000, "effort": "medium"}
BLOCK_OUTPUT = {b: dict(_BOUNDED) for b in ("J-13", "J-14", "J-15", "J-16", "J-17")}


def output_settings(block_id: str) -> tuple[int, str | None]:
    """`(max_tokens, effort)` for one block — the cap the cost ceiling must also use."""
    cfg = BLOCK_OUTPUT.get(block_id, {})
    return cfg.get("max_tokens", MAX_OUT), cfg.get("effort")


def stage_plan(metrics) -> tuple[tuple[str, str, str | None], ...]:
    """`(stage, block, metric)` in call order. ★ The ORDER is the guarantee (`RA-105`)."""
    return (("B", "J-09", None), ("B", "J-10", None),
            ("C", "J-11", None), ("C", "J-12", None),
            *(("C", "J-13", m) for m in metrics),
            ("C", "J-14", None),
            ("D", "J-15", None), ("D", "J-16", None), ("D", "J-17", None))


def visible_commits(stage: str, block_id: str, committed: list[str]) -> list[str]:
    """★★ Which committed outputs a call may read — the staging rule, in one place.

    ⚠ `J-11`…`J-13` read Stages A and B only: *"You have NOT seen any bull case"* (J-11),
    and a pre-mortem or forgery hunt that reads the bear case becomes a reply to it
    (`RA-15`). `J-14` reads "the analysis produced so far" — everything before it.
    """
    def of(*stages):
        return [k for k in committed if k.split(":", 1)[0] in stages]
    if stage == "B":
        return of("A", "B")                     # J-09 reads A; J-10 reads A and J-09
    if stage == "C" and block_id != "J-14":
        return of("A", "B")
    return of("A", "B", "C", "D")


def metrics_for(is_financial: bool) -> tuple[str, ...]:
    return tuple(m for m in J13_METRICS if is_financial or m not in J13_FINANCIALS_ONLY)


# ═══════════════════════════════════════════════════════════════════════════
# D-07 over recorded data — the ledger and the one recorded price call
# ═══════════════════════════════════════════════════════════════════════════

class RecordedEngine:
    """D-07's public surface as `valuation()` uses it (`FE-23`), over RECORDED inputs.

    ⚠ `get_prices` serves the RAW series only (`adj_as_of=None`, DE-45): an adjusted
    request raises rather than returning raw prices under an adjusted name.
    """

    def __init__(self, ticker: str, *, ledger_dir: pathlib.Path, price_fixture: pathlib.Path):
        import pandas as pd

        from src.data_engine.pit.ledger import FactLedger
        from src.data_engine.src.fmp.prices import raw_prices

        class _Replay:
            def __init__(self, body):
                self.body = body

            def get(self, endpoint, **params):  # noqa: ARG002 — FMPClient's signature
                return self.body

        recorded = json.loads(price_fixture.read_text(encoding="utf-8"))
        if recorded["params"].get("symbol") != ticker.upper():
            raise ValueError(f"{price_fixture} records {recorded['params'].get('symbol')}, "
                             f"not {ticker} — another company's price")
        start = date.fromisoformat(recorded["params"]["from"])
        end = date.fromisoformat(recorded["params"]["to"])
        self._ledger = FactLedger(ledger_dir).read(ticker.upper())
        self._prices = raw_prices(_Replay(recorded["response"]), ticker.upper(), start, end)
        self._pd = pd

    def get_fundamentals(self, ticker, as_of=None, period_type=None):  # noqa: ARG002 — D-07's signature
        from src.data_engine.pit.snapshot import assemble_rows
        rows = assemble_rows(self._ledger, as_of, source="edgar")
        return (rows[rows["period_type"] == period_type].reset_index(drop=True)
                if period_type else rows)

    def get_prices(self, ticker, start, end, adj_as_of=object()):  # noqa: ARG002 — D-07's signature
        if adj_as_of is not None:
            raise ValueError("RecordedEngine serves the RAW series only (adj_as_of=None, DE-45)")
        p = self._prices
        days = p["date"].map(lambda d: self._pd.Timestamp(d).date())
        return p[(days >= start) & (days <= end)].assign(close_currency=p["currency"])


# ═══════════════════════════════════════════════════════════════════════════
# Stage A — recorded answers, re-validated, then frozen
# ═══════════════════════════════════════════════════════════════════════════

def _recorded_call(run_id: str, block_id: str, *, ticker: str):
    root = next((r / run_id for r in RUN_ROOTS if (r / run_id).is_dir()), None)
    if root is None:
        raise FileNotFoundError(f"no recorded run {run_id} under {[str(r) for r in RUN_ROOTS]}")
    if f"-{ticker.lower()}-" not in run_id:
        raise ValueError(f"{run_id} is not a {ticker} run")
    records = [json.loads(ln) for ln in (root / "trace.jsonl").read_text().splitlines() if ln]
    if [r.get("status") for r in records if r.get("type") == "__run_closed__"] != ["SUCCESS"]:
        raise ValueError(f"{run_id} did not close SUCCESS — a failed run is not evidence")
    calls = [r for r in records if r.get("type") == "ExternalCall"
             and r.get("step_id") == f"judge:{block_id}"]
    if len(calls) != 1:
        raise ValueError(f"{run_id} holds {len(calls)} {block_id} call(s); exactly one is needed")
    call = calls[0]
    if call.get("error"):
        raise ValueError(f"{run_id} {block_id} recorded an error: {call['error']}")
    payload = json.loads((root / "trace/payloads" / f"{call['payload_ref']}.json")
                         .read_text(encoding="utf-8"))
    return call, payload


def load_stage_a(assignments: dict, *, blind, history_rows, ticker: str, as_of: date) -> list:
    """★ Recorded Stage-A answers → frozen records, each re-validated before it may count.

    ⚠ `P5` on every path: a truncated or incomplete answer, a rubric answer recorded
    BEFORE `DX-100` (chosen blind to the criteria — no `option_permutation`), a criterion
    that does not resolve, or a `J-20` choice whose basis refuses — each REFUSES the load.
    """
    from src.fundamental.scorecard.availability import evidence_ids_in
    from src.fundamental.scorecard.selection import offer, resolve
    from src.fundamental.valuation.normalise import normalise

    out = []
    for block_id, run_id in sorted(assignments.items()):
        blk = BLOCKS[block_id][0]()
        if blk.view != "blind":
            raise ValueError(f"{block_id} is not a Stage-A (blind) block")
        call, payload = _recorded_call(run_id, block_id, ticker=ticker)
        response = payload["response"]
        if (response.get("stop_reason") or "").lower() == "max_tokens":
            raise ValueError(f"{run_id} {block_id} was TRUNCATED (GW-23) — not an answer")
        text = response.get("text") or ""
        answer = json.loads(text[text.index("{"):text.rindex("}") + 1])
        request = payload["request"]
        derived = None
        criteria: tuple = ()
        if answer_shape(blk) == "rubric":
            if "option_permutation" not in request:
                raise ValueError(
                    f"{run_id} {block_id} predates DX-100: the rubric criteria were never shown, "
                    f"so its level was chosen blind — VOID, not frozen")
            the_offer = offer(_rubric_for(block_id), request["option_permutation"],
                              seed=request["option_seed"])
            criteria = the_offer.criteria
            score = resolve(the_offer, answer, evidence_ids_in(blind))
            derived = ({"rubric_id": score.rubric_id, "score": score.score} if score
                       else {"score": None, "outcome": "INSUFFICIENT_EVIDENCE"})
        missing = [f for f in judgement_tool(blk, criteria=criteria)["input_schema"]["required"]
                   if f not in answer]
        if missing:
            raise ValueError(f"{run_id} {block_id} is INCOMPLETE — missing {missing}")
        if answer_shape(blk) == "normalisation":
            basis = normalise(
                answer, quarterly_rows=history_rows[history_rows["period_type"] == "quarterly"],
                annual_rows=history_rows[history_rows["period_type"] == "annual"],
                ticker=ticker, as_of=as_of, bundle=blind,
                provenance={"prompt_version": call["prompt_version"], "run_id": run_id,
                            "stage_commit_hash": _answer_hash(answer),
                            "bundle_hash": call.get("bundle_hash") or "unrecorded"})
            derived = {"basis": json.loads(json.dumps(basis.to_json_obj(), default=str)),
                       "_basis_obj": basis}
        out.append({"block_id": block_id, "prompt_version": call["prompt_version"],
                    "run_id": run_id, "recorded_bundle_hash": call.get("bundle_hash"),
                    "answer": answer, "derived": derived})
    return out


def public(record: dict) -> dict:
    """A frozen record without in-memory objects (the basis object stays out of JSON)."""
    derived = record["derived"]
    if isinstance(derived, dict):
        derived = {k: v for k, v in derived.items() if not k.startswith("_")}
    return {**record, "derived": derived}


# ═══════════════════════════════════════════════════════════════════════════
# Answer schemas — `MP-5` (closed sets declared), `MP-7` (stated exits)
# ═══════════════════════════════════════════════════════════════════════════

STR = {"type": "string"}


def _obj(**props) -> dict:
    return {"type": "object", "properties": props, "required": list(props)}


def _arr(item: dict, lo: int = 0, hi: int | None = None) -> dict:
    return {"type": "array", "items": item, "minItems": lo, **({"maxItems": hi} if hi else {})}


def _enum(values) -> dict:
    return {"type": "string", "enum": list(values)}


def thesis_tool(block_id: str, *, observables=()) -> dict:
    """The tool schema each Stage B–D block answers through.

    ★ Structured where the prompt enumerates, so what a later stage and the thesis read is
    a FIELD, not a phrase parsed out of prose (`thesis/run.py::parse_falsifiers` is the
    prose parser this path does not use). ⚠ Every block also returns `answer` — its prose
    under the prompt's length cap — because `S-3`'s tagged reasoning lives there.
    """
    if block_id == "J-09":
        schema = _obj(
            price_requirements=_arr(_obj(requirement=STR, if_it_holds=STR,
                                         versus_stage_a=_enum(J09_VERSUS_OPTIONS)), 1),
            widest_gap=_obj(requirement=STR,
                            explained=_enum(("explained_by_stage_a", "unexplained")),
                            detail=STR),
            consensus_position=STR, differential_view=STR,
            most_load_bearing_method=STR, band_meaning=STR,
            stage_a_revision_findings=STR, answer=STR)
    elif block_id == "J-10":
        schema = _obj(claims=_arr(_obj(claim=STR, reference_class=STR, base_rate=STR,
                                       base_rate_in_bundle={"type": "boolean"},
                                       typical_or_exceptional=_enum(J10_TYPICALITY),
                                       exception_mechanism=STR), 1),
                      answer=STR)
    elif block_id == "J-11":
        schema = _obj(strongest_reason=_obj(reason=STR, evidence=STR),
                      load_bearing_assumptions=_arr(_obj(assumption=STR, what_breaks_it=STR,
                                                         early_symptom=STR), 3, 3),
                      accounts_in_two_years=STR, own_falsification_condition=STR,
                      missing_evidence=_arr(_obj(item=STR, what_i_would_do=STR)), answer=STR)
    elif block_id == "J-12":
        schema = _obj(paths=_arr(_obj(narrative=STR, earliest_symptom=STR,
                                      lead_quarters={"type": ["integer", "null"]},
                                      visible_in_bundle_now=STR), 4, 4),
                      ranked_by_symptom_earliness=_arr({"type": "integer"}, 4, 4), answer=STR)
    elif block_id == "J-13":
        schema = _obj(mechanisms=_arr(_obj(number={"type": "integer"}, status=_enum(J13_STATUS),
                                           evidence=STR, settling_item=STR), 12, 12),
                      company_definition_quote=STR, fraction_of_level_accounted=STR,
                      answer=STR)
    elif block_id == "J-14":
        finding = _obj(item=STR, claim=STR, conflict=STR)
        schema = _obj(inconsistent_items=_arr(finding), uncited_bearing_items=_arr(finding),
                      partial_citations=_arr(finding), single_source_claims=_arr(finding),
                      none_found={"type": "boolean"}, answer=STR)
    elif block_id == "J-15":
        if not observables:
            raise ValueError("J-15 needs the observable field list — it chooses from it (RA-35)")
        schema = _obj(falsifiers=_arr(_obj(condition=STR, observable_field=_enum(observables),
                                           deadline=STR, materiality=STR,
                                           about_business={"type": "boolean"}), 2, 4),
                      answer=STR)
    elif block_id == "J-16":
        schema = _obj(verdict=_enum(J16_VERDICTS), conviction=_enum(J16_CONVICTIONS),
                      considerations=_arr(_obj(consideration=STR, from_call=STR), 3, 3),
                      strongest_other_way=_obj(consideration=STR, why_it_did_not_govern=STR),
                      more_conservative_if=_obj(what=STR, by_when=STR),
                      evidence_coverage=_obj(supplied=STR, not_supplied=STR), answer=STR)
    elif block_id == "J-17":
        schema = _obj(gaps=_arr(_obj(gap=STR, why_wanted=STR, impact=STR,
                                     obtainable=_enum(J17_OBTAINABLE),
                                     would_change=_obj(if_it_said_x=STR, if_it_said_y=STR)), 1),
                      answer=STR)
    else:
        raise ValueError(f"{block_id} is not a Stage B–D block")
    return {"name": f"answer_{block_id.replace('-', '_').lower()}",
            "description": f"Answer {block_id}, grounded per S-3.", "input_schema": schema}


#: `DX-127` — cache pricing relative to the input rate: a write costs 1.25×, a read 0.1×.
CACHE_WRITE_RATE, CACHE_READ_RATE = 1.25, 0.10

#: ⚠ MEASURED 2026-09-15: J-09…J-13 produced 4k–19k output tokens, mean ≈ 11k. The first
#: projection (7,500) under-stated every later call's input AND its cost (`DX-115`).
PROJECTED_OUT_TOKENS = 12_000
#: ⚠ MEASURED 2026-09-15 on the first live run: filing + JSON parts tokenise at ≈2.75
#: chars/token (J-09: 382k chars → 139,031 tokens), not the 3 the Stage-A runner uses —
#: `//3` under-estimated J-09 by 9 %. A cost ceiling must not under-estimate.
CHARS_PER_TOKEN = 2.7


def strict_tool(tool: dict) -> dict:
    """★★ The schema AS SENT: `strict: true`, so the vendor must return schema-valid input.

    ⛔ MEASURED 2026-09-15 (`run-2026-09-15T022801-mu-thesis`): without it, `J-11` ended
    `stop_reason: tool_use` with a 981-character input — `strongest_reason` plus a stray
    top-level `evidence` — and four required fields absent. The schema was a REQUEST.
    ⚠ Strict mode needs `additionalProperties: false` on every object and does not accept
    complex array constraints, so `minItems`/`maxItems` are removed FROM THE SENT COPY
    only; `validate` still enforces them on the answer (`MP-5`).
    """
    import copy

    def walk(node):
        if isinstance(node, dict):
            lo, hi = node.pop("minItems", None), node.pop("maxItems", None)
            # ★ The bound still reaches the model — as the field's description, which
            #   strict mode accepts. Stripped silently, "the three most load-bearing
            #   assumptions" would be prompt prose only, and a two-item answer a paid failure.
            if lo and hi and lo == hi:
                node["description"] = f"exactly {lo} items"
            elif lo and hi:
                node["description"] = f"{lo} to {hi} items"
            elif lo:
                node["description"] = f"at least {lo} item(s)"
            if node.get("type") == "object":
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        return node

    sent = copy.deepcopy(tool)
    walk(sent["input_schema"])
    sent["strict"] = True
    return sent


def validate(schema: dict, value, path: str = "$") -> list[str]:
    """★ `MP-5` — the vendor is not obliged to honour a schema on a degraded call, so the
    answer is checked against it here. Returns the violations; empty means valid."""
    kinds = schema.get("type")
    kinds = kinds if isinstance(kinds, list) else [kinds]
    if value is None and "null" in kinds:
        return []
    if "enum" in schema:
        return [] if value in schema["enum"] else [f"{path}: {value!r} not in {schema['enum']}"]
    if "object" in kinds:
        if not isinstance(value, dict):
            return [f"{path}: expected an object"]
        errors = [f"{path}.{k}: required" for k in schema.get("required", ()) if k not in value]
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                errors += validate(sub, value[k], f"{path}.{k}")
        return errors
    if "array" in kinds:
        if not isinstance(value, list):
            return [f"{path}: expected an array"]
        errors = []
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: {len(value)} item(s) < minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: {len(value)} item(s) > maxItems {schema['maxItems']}")
        for i, item in enumerate(value):
            errors += validate(schema["items"], item, f"{path}[{i}]")
        return errors
    checks = {"string": lambda v: isinstance(v, str),
              "boolean": lambda v: isinstance(v, bool),
              "integer": lambda v: isinstance(v, int) and not isinstance(v, bool)}
    ok = any(checks[k](value) for k in kinds if k in checks)
    return [] if ok else [f"{path}: expected {kinds}"]


# ═══════════════════════════════════════════════════════════════════════════
# The thesis — built only from committed, validated outputs
# ═══════════════════════════════════════════════════════════════════════════

def falsifiers_from(answer: dict, *, as_of: date, observables) -> tuple:
    """J-15's structured answer → `Falsifier`s. ⚠ Validation is `Falsifier`'s own
    (`RA-35`); this adds only what a date needs: a deadline AFTER the as_of — one inside
    the bundle's window is answerable before the thesis exists."""
    from src.fundamental.errors import UncheckableFalsifierError
    from src.fundamental.thesis.models import Falsifier

    out = []
    for n, f in enumerate(answer["falsifiers"], start=1):
        try:
            deadline = date.fromisoformat(str(f["deadline"])[:10])
        except ValueError as exc:
            raise UncheckableFalsifierError(n, f"deadline {f['deadline']!r} is not a date") from exc
        if deadline <= as_of:
            raise UncheckableFalsifierError(n, f"deadline {deadline} is not after the as_of {as_of}")
        if f["observable_field"] not in observables:
            raise UncheckableFalsifierError(n, f"{f['observable_field']!r} is not an observable")
        out.append(Falsifier(ordinal=n, condition=f["condition"],
                             observable_field=f["observable_field"], source="D-07",
                             deadline=deadline, materiality=f["materiality"],
                             about_business=bool(f["about_business"])))
    return tuple(out)


def emitted_rubrics():
    """The four dimensions at the versions the Stage-A blocks emit (`EMITS_RUBRIC`)."""
    from src.fundamental.prompts.e_blocks import EMITS_RUBRIC
    from src.fundamental.scorecard.registry import RubricRegistry
    from src.fundamental.scorecard.rubrics.b43_v3 import PUBLISHED_RUBRICS

    reg = RubricRegistry(PUBLISHED_RUBRICS)
    return tuple(reg.get(*(lambda d, v: (d, int(v)))(*EMITS_RUBRIC[b].split("@v")))
                 for b in sorted(EMITS_RUBRIC))


def build_thesis(*, ticker: str, as_of: date, run_id: str, bundle_hash: str, outputs: dict,
                 call_ids: dict, falsifier_commit, stage_a_commit, stage_a: list,
                 extracted=frozenset()):
    """★ `CT-1.1` from the committed outputs. `Thesis.__post_init__` is the validator.

    ✏ 2026-09-15 (`DX-118`): the verdict and conviction pass through the coverage floors
    (`thesis/derate.py`) — measured, declared, and never more aggressive.
    """
    from src.fundamental.thesis.author import assert_bear_case_separate
    from src.fundamental.thesis.derate import Derating
    from src.fundamental.thesis.models import BearCase, Thesis

    j11, j16, j17 = outputs["C:J-11"], outputs["D:J-16"], outputs["D:J-17"]
    bear = BearCase(text=j11["answer"], falsification_condition=j11["own_falsification_condition"],
                    prompt_version="J-11@v1", run_id=call_ids["C:J-11"])
    assert_bear_case_separate(bear, bull_run_ids=(call_ids["B:J-09"], call_ids["D:J-16"]))
    scorecard = {r["block_id"]: r["derived"] for r in stage_a
                 if answer_shape(BLOCKS[r["block_id"]][0]()) == "rubric"}
    scorecard.update({b: {"score": None, "outcome": "ABSENT", "reason": why}
                      for b, why in STAGE_A_ABSENT.items()})
    derated = Derating.of(verdict=j16["verdict"], conviction=j16["conviction"],
                          rubrics=emitted_rubrics(), extracted=extracted, outputs=outputs,
                          stage_a=stage_a)
    return Thesis(
        ticker=ticker, thesis_version=1, as_of=as_of, bundle_hash=bundle_hash, run_id=run_id,
        verdict=derated.verdict, conviction=derated.conviction,
        falsifiers=falsifier_commit.falsifiers, bear_case=bear, scorecard=scorecard,
        confidence=derated.confidence,
        data_gaps=tuple(f"{g['gap']} [{g['obtainable']}]" for g in j17["gaps"]),
        falsifier_commit_hash=falsifier_commit.commit_hash,
        stage_a_hash=stage_a_commit.commit_hash)


# ═══════════════════════════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════════════════════════

def build_base(ticker: str, extractions, sector=DEFAULT_SECTOR):
    """The Stage B–D evidence, once: filing + verified extractions + annual history +
    `fv_model` with the recorded raw price + observables + declared absences."""
    from src.feature_engineer.valuation.assumptions import load_published
    from src.fundamental.bundle.assemble import (
        assemble,
        declared_absences,
        observables,
        valuation_part,
    )
    from src.fundamental.bundle.for_ticker import observable_fields
    from src.fundamental.bundle.models import EvidenceBundle
    from tools.run_extraction_once import _select, build_bundle, sector_bundle
    from tools.run_judgement_once import add_annual_history, load_extraction_parts

    _select(ticker)
    filing = build_bundle()
    extracted = load_extraction_parts(
        extractions, filing, ticker=ticker,
        sector=sector_bundle(sector, ticker=ticker) if sector and pathlib.Path(sector).exists()
        else None)
    with_history, rows = add_annual_history(
        EvidenceBundle(ticker=filing.ticker, as_of=filing.as_of,
                       parts=(*filing.parts, *extracted)),
        REPO / ".state/facts", ticker=ticker)
    engine = RecordedEngine(ticker, ledger_dir=REPO / ".state/facts", price_fixture=PRICE_FIXTURE)
    assumptions = load_published(*ASSUMPTIONS)
    fields = observable_fields(engine, ticker, filing.as_of, None)
    absences = dict(STAGE_B_ABSENCES)
    absences.update({f"stage_a_{b.lower().replace('-', '')}": why
                     for b, why in STAGE_A_ABSENT.items()})
    base = assemble(ticker=ticker, as_of=filing.as_of, parts=(
        *with_history.parts,
        valuation_part(ticker, filing.as_of, engine=engine, assumptions=assumptions),
        observables(fields),
        declared_absences("stage_b_to_d_inputs", absences)))
    return base, rows, engine, assumptions, fields


def _commit_key(block_id: str, key: str) -> str:
    return "D:falsifiers" if block_id == "J-15" else key


def carry_forward(prior_run: str, *, log, a_commit, base, parts_by_key: dict):
    """★ Resume a failed run WITHOUT re-buying what it already committed — and without
    trusting it: every carried commit is RE-DERIVED here and must reproduce its recorded
    hash, including the bundle hash of the call that produced it.

    ⚠ Refuses when the prior run froze a different Stage A, when any hash does not
    reproduce (the evidence, a prompt-visible part or the payload moved), or when the
    commits are out of plan order. Returns `(outputs, call_ids, records, falsifier_commit)`.
    """
    from src.fundamental.bundle.assemble import stage_output
    from src.fundamental.thesis.author import commit_falsifiers
    from src.fundamental.thesis.models import Falsifier

    path = REPO / ".state/runs" / prior_run / "commits.jsonl"
    records = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln]
    if not records or records[0].get("stage") != "A" \
            or records[0].get("commit_hash") != a_commit.commit_hash:
        raise ValueError(f"{prior_run} froze a different Stage A — its later commits read other "
                         f"evidence and cannot be carried (RA-108)")
    order = {(s, b, m): i for i, (s, b, m) in enumerate(stage_plan(J13_METRICS))}
    outputs, call_ids, carried, falsifier_commit = {}, {}, [], None
    committed = list(parts_by_key)
    for record in records[1:]:
        # ★ The run that PRODUCED the commit, not the one that last carried it: a resume of a
        #   resume must pin the part exactly as the producing run did, or every hash moves.
        origin = record.get("carried_from") or prior_run
        key = record["stage"]
        stage, rest = key.split(":", 1)
        block_id, _, metric = rest.partition(":")
        block_id = "J-15" if key == "D:falsifiers" else block_id
        metric = metric or None
        if (stage, block_id, metric) not in order:
            raise ValueError(f"{prior_run}: commit {key!r} is not a step of the plan")
        expected_bundle = call_bundle(base, parts_by_key,
                                      visible_commits(stage, block_id, committed)).bundle_hash
        if record["bundle_hash"] != expected_bundle:
            raise ValueError(f"{prior_run}: {key} read bundle {record['bundle_hash'][:23]}…, and "
                             f"this run's evidence gives {expected_bundle[:23]}… — not carried")
        if key == "D:falsifiers":
            falsifier_commit = commit_falsifiers(
                log, bundle_hash=record["bundle_hash"],
                falsifiers=tuple(Falsifier.from_json_obj(f) for f in record["payload"]["falsifiers"]))
            derived = falsifier_commit.commit
        else:
            derived = log.commit(key, record["bundle_hash"], record["payload"])
            outputs[key] = record["payload"]
        if derived.commit_hash != record["commit_hash"]:
            raise ValueError(f"{prior_run}: {key}'s commit hash does not reproduce — tampered or "
                             f"a different payload; not carried")
        call_ids[key] = f"{origin}:judge:{key}"
        parts_by_key[key] = stage_output(
            stage=stage, block_id=f"{block_id}:{metric}" if metric else block_id,
            prompt_version=BLOCKS[block_id][0]().version, run_id=origin,
            commit_hash=derived.commit_hash, answer=derived.payload)
        committed.append(key)
        carried.append({**record, "carried_from": origin})
    return outputs, call_ids, carried, falsifier_commit


def call_bundle(base, parts_by_key: dict, seen: list[str]):
    """The bundle one call reads: the base evidence plus EXACTLY the commits it may see."""
    from src.fundamental.bundle.models import EvidenceBundle
    return EvidenceBundle(ticker=base.ticker, as_of=base.as_of,
                          parts=(*base.parts, *(parts_by_key[k] for k in seen)))


def call_payload(base, parts_by_key: dict, seen, block_id: str, metric: str | None,
                 *, cached: bool) -> tuple[str, str]:
    """`(cache prefix, the rest)` — the stable evidence and what varies per call (`DX-127`).

    ⚠ Uncached the whole thing is one string in the historical order (instructions first), so
    `--no-cache` reproduces exactly what the first thesis sent.
    """
    base_body = "\n\n".join(p.content for p in base.parts)
    commits = "\n\n".join(parts_by_key[k].content for k in seen if k in parts_by_key)
    prompt = call_prompt(block_id, metric)
    if not cached:
        return "", build_payload(prompt, None, "\n\n".join(x for x in (base_body, commits) if x))
    return base_body, build_payload(prompt, None, commits) if commits else prompt


def call_prompt(block_id: str, metric: str | None) -> str:
    """★ `S-8` is composed: Stages B–D are FRESH authoring (§4.0). `S-7` is not: it tells a
    reader not to anchor on a price, and these blocks are handed one legitimately."""
    prompt = compose_prompt(BLOCKS[block_id][0](), stage_a=False, fresh=True)
    if metric:
        if METRIC_PLACEHOLDER not in prompt:
            raise ValueError(f"{block_id} has no {METRIC_PLACEHOLDER} to bind")
        prompt = prompt.replace(METRIC_PLACEHOLDER, metric)
    elif METRIC_PLACEHOLDER in prompt:
        raise ValueError(f"{block_id} needs a metric bound to {METRIC_PLACEHOLDER}")
    return prompt


def main(argv=None) -> int:
    from src.fundamental.bundle.assemble import stage_output
    from src.fundamental.thesis.author import (
        CommitLog,
        assert_fresh_authoring_bundle,
        commit_falsifiers,
    )

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="⚠ spends money")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ticker", default="MU")
    ap.add_argument("--budget-usd", type=float, default=None,
                    help="HARD cap: a call is not sent if its CEILING cost would pass it")
    ap.add_argument("--no-cache", action="store_true",
                    help="send one block per call (the pre-DX-127 shape) instead of caching")
    ap.add_argument("--financial", action="store_true",
                    help="the company is a financial (adds J-13's book_value call)")
    ap.add_argument("--resume-from", default=None, metavar="RUN_ID",
                    help="carry a failed run's VERIFIED commits forward; send only what is missing")
    args = ap.parse_args(argv)
    if not (args.live or args.dry_run):
        ap.print_help()
        return 2
    if args.live and args.budget_usd is None:
        print("BLOCKED: --live requires --budget-usd (the approved cap)")
        return 2

    from src.fundamental.scorecard.availability import evidence_ids_in

    base, rows, engine, assumptions, fields = build_base(args.ticker, DEFAULT_EXTRACTIONS)
    assert_fresh_authoring_bundle(base)                        # RA-18
    as_of = base.as_of
    blind = base.redact()
    stage_a = load_stage_a(DEFAULT_STAGE_A, blind=blind, history_rows=rows,
                           ticker=args.ticker, as_of=as_of)

    from src.feature_engineer.valuation.service import valuation, value_on_basis
    fv_model = json.loads(valuation(args.ticker, as_of, engine=engine,
                                    assumptions=assumptions).to_json())
    j20 = next(r for r in stage_a if r["block_id"] == "J-20")
    fv_analyst = json.loads(value_on_basis(args.ticker, as_of, basis=j20["derived"]["_basis_obj"],
                                           engine=engine, assumptions=assumptions).to_json())

    log = CommitLog()
    a_commit = log.commit("A", blind.bundle_hash,
                          {"blocks": [public(r) for r in stage_a], "absent": STAGE_A_ABSENT})
    parts_by_key = {f"A:{r['block_id']}": stage_output(
        stage="A", block_id=r["block_id"], prompt_version=r["prompt_version"],
        run_id=r["run_id"], commit_hash=a_commit.commit_hash, answer=public(r))
        for r in stage_a}

    outputs, call_ids, carried = {}, {}, []
    falsifier_commit = None
    if args.resume_from:
        outputs, call_ids, carried, falsifier_commit = carry_forward(
            args.resume_from, log=log, a_commit=a_commit, base=base,
            parts_by_key=parts_by_key)
    plan = stage_plan(metrics_for(args.financial))
    print(f"── THESIS · Stages B–D over a frozen Stage A · {args.ticker} as of {as_of} ──")
    print(f"  Stage A    : {len(stage_a)} frozen · absent {sorted(STAGE_A_ABSENT)} · "
          f"commit {a_commit.commit_hash[:23]}…")
    for r in stage_a:
        d = r["derived"] or {}
        shown = (f"score={d.get('score')}" if "score" in d
                 else f"basis={d['basis']['base_fcff']}" if "basis" in d else "")
        print(f"     {r['block_id']} {r['prompt_version']}  {r['run_id']}  {shown}")
    print(f"  fv_model   : {fv_model['value_per_share']} · price {fv_model['price']['value']} "
          f"({fv_model['price']['date']}, raw) · implied stage-1 growth "
          f"{fv_model['implied']['value']} ({fv_model['implied']['status']})")
    print(f"  fv_analyst : {fv_analyst['value_per_share']} on J-20's basis — recorded, NOT in "
          f"the bundle (VS-3)")
    print(f"  bundle     : {len(base.parts)} base parts · {base.bundle_hash[:23]}… · "
          f"{len(fields)} observables")

    # ── the plan and its cost, BEFORE anything is sent ──────────────────────────
    # ★ Unknown later outputs are projected from the MEASURED output size, not from Stage A.
    projected = int(PROJECTED_OUT_TOKENS * CHARS_PER_TOKEN)
    base_chars = sum(len(p.content) for p in base.parts)
    ceiling = expected = 0.0
    estimates, keys = [], list(parts_by_key)
    for stage, block_id, metric in plan:
        key = f"{stage}:{block_id}" + (f":{metric}" if metric else "")
        if _commit_key(block_id, key) in parts_by_key:
            print(f"   {key:<28} CARRIED from {args.resume_from} (verified, not re-sent)")
            continue
        seen = visible_commits(stage, block_id, keys)
        known = sum(len(parts_by_key[k].content) for k in seen if k in parts_by_key)
        unknown = sum(1 for k in seen if k not in parts_by_key) * projected
        est_in = int((len(call_prompt(block_id, metric)) + base_chars + known + unknown)
                     / CHARS_PER_TOKEN)
        # ★ `DX-127` — the base evidence is written to the cache once and read thereafter.
        cached_in = 0 if args.no_cache else int(base_chars / CHARS_PER_TOKEN)
        rate = CACHE_WRITE_RATE if not estimates else CACHE_READ_RATE
        billed = (est_in - cached_in) + cached_in * rate
        ceiling += billed * PRICE_IN + output_settings(block_id)[0] * PRICE_OUT
        expected += billed * PRICE_IN + PROJECTED_OUT_TOKENS * PRICE_OUT
        estimates.append(est_in)
        keys.append("D:falsifiers" if block_id == "J-15" else key)
        print(f"   {key:<28} sees {len(seen):>2} commit(s)  ≈{est_in:,} in")
    print(f"  estimate   : ≈${expected:.2f} expected ({PROJECTED_OUT_TOKENS // 1000}k out/call, "
          f"{'cache OFF' if args.no_cache else 'cached prefix'}) · ≤${ceiling:.2f} ceiling "
          f"({len(estimates)} call(s) to send; caps {MAX_OUT}, J-13 "
          f"{output_settings('J-13')[0]} at effort {output_settings('J-13')[1]})")
    if args.dry_run:
        print("\n  ★ dry run — nothing sent.")
        return 0

    from src.fundamental.errors import NoFalsifierError, UncheckableFalsifierError
    from src.fundamental.prompts.envelope import envelope_hash
    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import traced_transport
    from tools.anthropic_transport import anthropic_transport

    run_id = f"run-{datetime.now(timezone.utc):%Y-%m-%dT%H%M%S}-{args.ticker.lower()}-thesis"
    root = REPO / ".state/runs" / run_id
    store = TraceStore(REPO / ".state/runs", run_id)
    commits_file = root / "commits.jsonl"

    def persist_raw(obj: dict) -> None:
        # ★ RA-108 — on disk BEFORE any later call is issued.
        commits_file.parent.mkdir(parents=True, exist_ok=True)
        with commits_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, sort_keys=True, default=str) + "\n")

    def persist(record) -> None:
        persist_raw(record.to_json_obj())

    persist(a_commit)
    for record in carried:
        persist_raw(record)                  # `carried_from` names the PRODUCING run
    spent, failed = 0.0, None
    committed = list(parts_by_key)
    for stage, block_id, metric in plan:
        key = f"{stage}:{block_id}" + (f":{metric}" if metric else "")
        if _commit_key(block_id, key) in parts_by_key:
            continue                                  # carried forward, verified
        seen = visible_commits(stage, block_id, committed)
        bundle = call_bundle(base, parts_by_key, seen)
        # ★★ `DX-127` — the BASE evidence is byte-identical in all 13 calls, so it is the
        #   cache prefix; only the commits this call may read and its own instructions vary.
        #   ⚠ The model therefore reads evidence → frozen commits → instructions, where it
        #   previously read instructions → evidence. Recorded as a deliberate order change.
        prefix, payload = call_payload(base, parts_by_key, seen, block_id, metric,
                                       cached=not args.no_cache)
        max_out, effort = output_settings(block_id)
        ceiling_cost = (int((len(payload) + len(prefix)) / CHARS_PER_TOKEN) * PRICE_IN
                        + max_out * PRICE_OUT)
        if spent + ceiling_cost > args.budget_usd:
            failed = (key, f"NOT SENT — its ceiling (${ceiling_cost:.2f}) would pass the "
                           f"${args.budget_usd:.2f} cap after ${spent:.2f} spent")
            break
        blk = BLOCKS[block_id][0]()
        tool = thesis_tool(block_id, observables=fields)
        transport = traced_transport(
            anthropic_transport(tool=strict_tool(tool), max_output=max_out), store,
            step_id=f"judge:{key}", kind="llm",
            cost_of=lambda _m, t: t.get("input", 0) * PRICE_IN + t.get("output", 0) * PRICE_OUT,
            prompt_version=blk.version,
            envelope_hash=envelope_hash("judgement", stage_a=False, fresh=True),
            bundle_hash=bundle.bundle_hash)
        request = {"model": MODEL, "max_tokens": max_out, "payload": payload,
                   **({"cache_prefix": prefix} if prefix else {}),
                   **({"effort": effort} if effort else {}),
                   "reads_commits": seen, **({"metric": metric} if metric else {})}
        try:
            result = transport(request)
        except Exception as exc:                                    # noqa: BLE001
            failed = (key, f"{type(exc).__name__}: {exc}")
            break
        tin, tout = result.get("tokens_in", 0), result.get("tokens_out", 0)
        spent += tin * PRICE_IN + tout * PRICE_OUT
        if (result.get("stop_reason") or "").lower() == "max_tokens":
            failed = (key, f"TRUNCATED at max_tokens={max_out} (GW-23) — stream "
                           f"{result.get('stream_chars')} — a truncated response is a failure")
            break
        text = result.get("text") or ""
        try:
            answer = json.loads(text[text.index("{"):text.rindex("}") + 1])
        except ValueError:
            failed = (key, "UNPARSEABLE answer")
            break
        problems = validate(tool["input_schema"], answer)
        if problems:
            failed = (key, f"schema violations {problems[:4]}")
            break
        call_ids[key], outputs[key] = f"{run_id}:judge:{key}", answer
        if block_id == "J-15":
            try:
                falsifier_commit = commit_falsifiers(
                    log, bundle_hash=bundle.bundle_hash,
                    falsifiers=falsifiers_from(answer, as_of=as_of, observables=fields))
            except (UncheckableFalsifierError, NoFalsifierError) as exc:
                failed = (key, f"RES.THESIS.NO_FALSIFIER — {exc}; J-16 NOT issued (RA-16)")
                break
            record, commit_key = falsifier_commit.commit, "D:falsifiers"
        else:
            record, commit_key = log.commit(key, bundle.bundle_hash, answer), key
        persist(record)
        parts_by_key[commit_key] = stage_output(
            stage=stage, block_id=f"{block_id}:{metric}" if metric else block_id,
            prompt_version=blk.version, run_id=run_id, commit_hash=record.commit_hash,
            answer=record.payload)
        committed.append(commit_key)
        cached = f"  cache r/w {result.get('cache_read')}/{result.get('cache_write')}" \
            if result.get("cache_read") is not None else ""
        print(f"   ✅ {key:<28} {tin:,} in / {tout:,} out  "
              f"${tin * PRICE_IN + tout * PRICE_OUT:.4f}{cached}")
    # ⚠ The trace's own close status must say what happened: the first live run closed
    #   `SUCCESS` after failing at J-11, because `close()` defaults to it (L3 DX-113).
    store.close("SUCCESS" if failed is None else "FAILED")

    summary = {"run_id": run_id, "ticker": args.ticker, "as_of": as_of.isoformat(),
               "spent_usd": round(spent, 4), "base_bundle_hash": base.bundle_hash,
               "stage_a_commit": a_commit.commit_hash, "fv_model": fv_model,
               "fv_analyst_on_j20_basis": fv_analyst, "outputs": outputs,
               "failed": failed, "thesis": None}
    if failed is None:
        thesis = build_thesis(ticker=args.ticker, as_of=as_of, run_id=run_id,
                              bundle_hash=base.bundle_hash, outputs=outputs, call_ids=call_ids,
                              falsifier_commit=falsifier_commit, stage_a_commit=a_commit,
                              stage_a=stage_a, extracted=evidence_ids_in(blind))
        summary["thesis"] = thesis.to_json_obj()
        c = thesis.confidence
        print(f"\n  ★ THESIS  verdict={thesis.verdict}  conviction={thesis.conviction}  "
              f"falsifiers={len(thesis.falsifiers)}  gaps={len(thesis.data_gaps)}")
        print(f"     coverage {c['value']:.2f} (cap {c['cap']}) · authored "
              f"{c['verdict_as_authored']}/{c['conviction_as_authored']} · absent-governing "
              f"{len(c['governing_inputs_absent'])}")
    else:
        print(f"\n  ⚠⚠ INCOMPLETE at {failed[0]}: {failed[1]} — NO thesis (P5)")
    root.mkdir(parents=True, exist_ok=True)
    (root / "thesis.json").write_text(json.dumps(summary, indent=1, default=str),
                                      encoding="utf-8")
    print(f"  run_id={run_id}   spent ${spent:.4f}   → {root / 'thesis.json'}")
    return 0 if failed is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
