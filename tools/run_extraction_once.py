#!/usr/bin/env python3
"""Run ONE real `E-01` extraction and record it — `DX-23` step 5.

    python3 tools/run_extraction_once.py --dry-run     # ★ free: shows the plan
    python3 tools/run_extraction_once.py --live        # ⚠ SPENDS MONEY

⚠⚠ **`--live` calls Anthropic and costs real money** (~$0.15-$0.40 for this
filing; the estimate is printed by `--dry-run`). It exists so `F5`'s golden
cases get an `input_ref`: one `E-01` call over the MU 10-Q returns EVERY segment
row in BOTH columns, so cases 1, 2 and any later case on this filing all resolve
from **one** recording.

★ Wired here, outside `src/`, for the same reason as `f2_payload_reader.py`:
this is a composition root (`CA-9`), and it is the only place that may know
about the gateway, the registry, the trace store and the filing at once.

⚠ The API key is read from the environment (`ANTHROPIC_API_KEY`), never
hardcoded and never a CLI argument — a key in `argv` lands in shell history.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import date, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.fundamental.bundle.models import BundlePart, EvidenceBundle  # noqa: E402
from src.fundamental.filings.extract import (  # noqa: E402
    item,
    not_found,
    run_extraction,
)
from src.fundamental.filings.models import FOUND  # noqa: E402
from src.fundamental.prompts.e_blocks import (  # noqa: E402
    BLOCKS,
    e01_v2,
)
from src.fundamental.prompts.registry import PromptRegistry  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent

#: ⚠⚠ `L7` §5 — MU is FILING 1 and it is load-bearing. It stays the DEFAULT and
#: its constants keep their names, so nothing that imports `FILING` changes
#: behaviour. A second filing is selected explicitly with `--filing`, never by
#: editing these.
FILINGS = {
    "MU": {"path": "tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt",
           "accession": "0000723125-25-000021", "as_of": date(2025, 6, 26),
           # ⚠ the segment note's line range — it is NOT in the same place in
           #   every filing, and a range tuned for one silently slices the wrong
           #   text out of another.
           "slice": (1060, 1240)},
    "AMD": {"path": "tests_src/fixtures/filings/AMD_FY2025Q3_10Q.txt",
            "accession": "0000002488-25-000166", "as_of": date(2025, 11, 5),
            "slice": (500, 560)},
}

#: ★ Module-level defaults, unchanged: `golden_replay` and the wiring tests
#: import `FILING`, and filing 1's cases resolve against it.
TICKER = "MU"
FILING = REPO / FILINGS[TICKER]["path"]
ACCESSION = FILINGS[TICKER]["accession"]


def _select(ticker: str) -> None:
    """Point the module at another filing. ⚠ Explicit, never implicit."""
    global TICKER, FILING, ACCESSION
    TICKER = ticker
    FILING = REPO / FILINGS[ticker]["path"]
    ACCESSION = FILINGS[ticker]["accession"]

#: ★ `claude-opus-5`, $5.00 / $25.00 per 1M tokens (input / output).
PRICE_IN, PRICE_OUT = 5.00 / 1e6, 25.00 / 1e6

#: ⚠⚠ A `Config`, NOT a dict. The gateway calls `cfg.get_optional(...)`, which a
#: dict does not have — `DX-11` already caught this exact assumption once, and
#: the first `--live` attempt reproduced it. ★ It failed at config resolution,
#: BEFORE any request was sent, so it cost nothing.
#:
#: ⚠ `llm.deep.temperature` is deliberately ABSENT: `GW-8a` treats its presence
#: as the error, because Opus 5 rejects `temperature` outright (400). The
#: gateway probes with `get_optional` precisely so absent is the correct state.
GATEWAY_VALUES = {
    # the hard cap — the gateway RAISES rather than overspending (GW-20).
    # One E-01 call is estimated ~$0.40; $2 leaves room for a retry.
    "llm.budget.usd_per_run": 2.00,
    "llm.deep.model_id": "claude-opus-5",
    # ⚠⚠ `medium`, not `high` — changed 2026-09-07 after FIVE measured runs on
    # one bundle spent 13,243 / 16,000* / 16,000* / 13,243 / 32,000 output
    # tokens (*a clamp). ★ Raising `max_tokens` is not the lever: adaptive
    # thinking expands into whatever budget it is given, so a bigger ceiling
    # buys more thinking, not more headroom. Effort bounds it directly.
    # ★★ Extraction is TRANSCRIPTION, not reasoning — the task is "copy what
    # the table says", which is where the docs put `medium` as the step-down
    # that holds quality. `high` remains right for judgement blocks.
    "llm.deep.effort": "medium",
    "llm.deep.thinking_mode": "adaptive",
    # ★ Pricing is config, not code: the gateway computes cost per call from it.
    "llm.pricing.claude-opus-5.input_per_mtok": 5.00,
    "llm.pricing.claude-opus-5.output_per_mtok": 25.00,
}


# --------------------------------------------------------------------------- #
# 2. the bundle
# --------------------------------------------------------------------------- #
def build_bundle(*, whole_filing: bool = True) -> EvidenceBundle:
    """`RA-1` — every LLM call takes an `EvidenceBundle` and nothing else.

    ⚠ The `content` here is what `X-01` verifies quotes against, so it must be
    the SAME text a human re-checks the golden case against. That is why the
    fixture is the whole converted filing rather than an excerpt.
    """
    text = FILING.read_text(encoding="utf-8")
    if not whole_filing:
        # ★ The segment note only — ~18x cheaper, and enough for E-01.
        # ⚠ A narrower bundle is a DIFFERENT bundle_hash, so a golden case
        #   recorded against one does not transfer to the other.
        lines = text.splitlines()
        lo, hi = FILINGS[TICKER]["slice"]
        text = "\n".join(lines[lo:hi])
    return EvidenceBundle(
        ticker=TICKER, as_of=FILINGS[TICKER]["as_of"],
        parts=(BundlePart(kind="filing",
                          pins={"accession_id": ACCESSION, "form": "10-Q",
                                "period_end": "2025-05-29"},
                          content=text),),
    )


# --------------------------------------------------------------------------- #
# 3. the parse — response -> ExtractedItem[]
# --------------------------------------------------------------------------- #
def parse_items(call, bundle_text: str | None = None) -> list:
    """Map one `CallResult` to `ExtractedItem`s (`MP-5`, `MP-18`).

    ⚠ **Offsets are computed here, not asked for.** A model-supplied character
    offset is a number it cannot verify and we can: `X-01` would reject a wrong
    one anyway, so asking for it spends tokens to create a failure mode.
    ★ The quote is the model's; the offset is arithmetic (`AP-5`).
    """
    payload = getattr(call, "parsed", call)
    if isinstance(payload, str):
        payload = json.loads(payload)
    rows = payload.get("items", payload) if isinstance(payload, dict) else payload

    # ⚠⚠ Offsets must resolve in the BUNDLE — that is what X-01 checks against.
    # Reading the file here instead meant a sliced bundle (--segment-note-only)
    # produced offsets pointing into the FULL document, outside the bundle, so
    # every item would have failed verification for a reason that had nothing to
    # do with the model. ★ The default keeps the whole-filing behaviour.
    if bundle_text is None:
        bundle_text = FILING.read_text(encoding="utf-8")
    out = []
    for row in rows:
        # ★ MP-7 — `not_found` is a CORRECT answer, and needs a note saying
        #   where you looked. A bare not_found is indistinguishable from a step
        #   that never ran.
        if row.get("status") == "not_found":
            # ★ The quote is carried into the note: MP-7 wants *where you
            #   looked*, and the document's own sentence is the best answer.
            where = (row.get("quote") or "").strip()
            note = row.get("note") or "not disclosed"
            out.append(not_found(row["evidence_id"],
                                 note=f"{note} — {where}" if where else note))
            continue
        # ⚠ `unit` and `quote` are OPTIONAL in the schema, because `seg.name`
        # and `seg.basis_note` are text items with no unit — 16 of 66 items in
        # the measured run carried none. ★ Missing `quote` on a FOUND item is a
        # different matter: it is a contract breach, so it raises here with a
        # readable message rather than a KeyError deep in the loop.
        quote = row.get("quote")
        if not quote:
            raise ValueError(
                f"{row['evidence_id']!r} ({row.get('qualifier') or '-'}): a "
                "found item needs a verbatim quote — X-01 has nothing to check "
                "it against (RA-6, RA-131)"
            )
        start, end = _locate(bundle_text, quote)
        if start < 0:
            # ⚠ P5 — loud. A quote not in the document is the hallucination
            # X-01 exists to catch; failing here just catches it one step
            # earlier, with a better message.
            raise ValueError(
                f"{row.get('evidence_id')!r}: quoted text is not in the bundle — "
                f"{quote[:60]!r}"
            )
        value, unit = _split_currency(row.get("value", ""), row.get("unit", ""),
                                     row["evidence_id"])
        out.append(item(
            row["evidence_id"], value=value, unit=unit,
            # ⚠⚠ `DX-37` — use `_locate`'s END, never `start + len(quote)`.
            # ★★ The two agree only when the match was EXACT. `_locate` also
            # matches under whitespace/typography normalisation, and there the
            # document's span is a DIFFERENT LENGTH from the quote — so
            # `start + len(quote)` cuts the span short and `X-01` ① rejects a
            # citation that is perfectly good, blaming the model for our
            # arithmetic. Measured on `DX-35`'s repaired sentence: the document
            # holds `'State of\n\n\nNew York'` where the quote holds
            # `'State of\nNew York'`, so the span ended 2 chars early on
            # `'…provides fo'`.
            quote=quote, accession_id=ACCESSION, offset=(start, end),
            period_start=row.get("period_start"), period_end=row.get("period_end"),
            cumulative_ytd=bool(row.get("cumulative_ytd")),
            qualifier=row.get("qualifier", ""), note=row.get("note", ""),
        ))
    return _dedupe_not_found(out)


def _dedupe_not_found(items: list) -> list:
    """Collapse repeated `not_found` claims that share one `MP-18` identity.

    ⚠⚠ MEASURED: the model returned **five** `not_found` items for `seg.assets`
    — one per segment — all with no qualifier and no period, so all five carried
    the identity `('seg.assets', '', None)` and `ExtractionResult` refused them.

    ★ It is right to refuse and right to collapse: with no qualifier and no
    period the five are literally the same claim, `evidence_coverage` counts ids
    as a SET so copies add nothing, and `RA-66` cares whether the figure was
    extracted at all — not how many times its absence was asserted.

    ⚠ **`found` items are NOT collapsed.** Two values sharing an identity is
    real ambiguity about a number, which is exactly what `MP-18` exists to
    surface — silently keeping the first would hide it.
    """
    seen, out = set(), []
    for it in items:
        if it.status == FOUND:
            out.append(it)
            continue
        if it.identity in seen:
            continue
        seen.add(it.identity)
        out.append(it)
    return out


#: Currency marks that belong in `unit`, never in `value` (`C15`).
_CURRENCY = {"$": "USD", "£": "GBP", "€": "EUR", "¥": "JPY"}


def _split_currency(value: str, unit: str, evidence_id: str) -> tuple[str, str]:
    """`C15` — the currency lives in `unit`; `value` is the bare figure.

    ⚠⚠ Decided by the fund manager 2026-09-07: **`5,069` with unit
    `millions of USD`**, not `$5,069`. Carrying the symbol in `value` AND the
    currency in `unit` states it twice, and `MO-1` wants it stated once —
    where a reader will look for it.

    ★ Enforced here in code rather than asked for in the prompt (`AP-5`): the
    symbol is a deterministic prefix, and this is the third time a constraint
    left to prose came back wrong.

    ⚠ If a symbol is present and `unit` does NOT name the currency, this
    **raises**. It does not invent one — `$` is not always USD, and a guessed
    currency on a money figure is exactly the silent default `P5` forbids.
    """
    stripped = value.strip()
    symbol = stripped[:1] if stripped[:1] in _CURRENCY else ""
    if not symbol:
        return value, unit
    bare = stripped[1:].strip()
    iso = _CURRENCY[symbol]
    if iso.lower() not in unit.lower() and symbol not in unit:
        raise ValueError(
            f"{evidence_id}: value {value!r} carries {symbol!r} but unit "
            f"{unit!r} does not name a currency. MO-1 — a bare value is not "
            f"monetary, and guessing {iso!r} here would be a silent default (P5)"
        )
    return bare, unit


def _locate(haystack: str, needle: str) -> tuple[int, int]:
    """Find `needle` in `haystack`, tolerating what `X-01` itself tolerates.

    ⚠⚠ MEASURED: a plain `str.find` rejected a quote that was genuinely in the
    document — the model returned it with different internal whitespace. ★★ The
    locator must be **no stricter than the check it feeds**: `X-01` compares the
    resolved span with `_collapse_whitespace`, so a finder demanding a byte-exact
    match fails items `X-01` would have accepted, and blames the model for it.

    ★ Returns real offsets into the ORIGINAL text, so the recorded span still
    resolves to the document's own characters — the normalisation is used to
    locate, never to rewrite.
    """
    exact = haystack.find(needle)
    if exact >= 0:
        return exact, exact + len(needle)

    # ⚠⚠ MEASURED: 66 of 67 items located; the one failure carried a LITERAL
    # six-character `\u00a0` where the document has an actual non-breaking
    # space. The model escaped the character into its JSON string instead of
    # emitting it. ★ A serialisation artefact, not a hallucination — decoding it
    # is the same category as the typography normalisation, and it still has to
    # be FOUND in the document afterwards or this returns -1.
    needle = _UNICODE_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), needle)
    exact = haystack.find(needle)
    if exact >= 0:
        return exact, exact + len(needle)

    def _norm(text: str) -> tuple[str, list[int]]:
        out, idx, prev_space = [], [], False
        for i, ch in enumerate(text):
            c = _TYPO.get(ch, ch)
            if c.isspace():
                if prev_space:
                    continue
                c, prev_space = " ", True
            else:
                prev_space = False
            out.append(c)
            idx.append(i)
        return "".join(out), idx

    hay_n, hay_idx = _norm(haystack)
    needle_n, _ = _norm(needle.strip())
    if not needle_n:
        return -1, -1
    hit = hay_n.find(needle_n)
    if hit < 0:
        return -1, -1
    return hay_idx[hit], hay_idx[hit + len(needle_n) - 1] + 1


#: A literal `\uXXXX` the model wrote as TEXT rather than as the character.
_UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")

#: Same set `X-01` normalises — rendering-level only, nothing semantic.
_TYPO = {"\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
         "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u00a0": " "}


# --------------------------------------------------------------------------- #
# 4. the job
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="★ free — plan + cost")
    g.add_argument("--live", action="store_true", help="⚠ SPENDS MONEY")
    ap.add_argument("--block", default="E-01", choices=sorted(BLOCKS),
                    help="which E-block to run (default E-01 = filing 1's)")
    ap.add_argument("--prompt-version", default=None,
                    choices=["v2", "v3"],
                    help="⚠ v3 is a CANDIDATE; shipping it retires filing 1's "
                         "recording (L7 §5), so it is opt-in")
    ap.add_argument("--effort", default=None,
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="⚠ overrides llm.deep.effort. Extraction is "
                         "transcription; thinking is what truncates a run")
    ap.add_argument("--ticker", default="MU", choices=sorted(FILINGS),
                    help="which filing (default MU = filing 1)")
    ap.add_argument("--segment-note-only", action="store_true",
                    help="⚠⚠ DIAGNOSTIC ONLY (DX-32) — never for a recording "
                         "a golden case grades: the slice omits the evidence a "
                         "PERIOD START is derived from, so discrete and "
                         "cumulative figures collapse onto one MP-18 identity")
    args = ap.parse_args()
    _select(args.ticker)

    if not FILING.exists():
        print(f"  ⛔ {FILING.relative_to(REPO)} is missing")
        return 1

    if args.effort:
        # ⚠ A copy — GATEWAY_VALUES is module state and a live run must not be
        #   able to leave it changed for the next one.
        globals()["GATEWAY_VALUES"] = {**GATEWAY_VALUES,
                                       "llm.deep.effort": args.effort}
        print(f"  ⚠ effort override: {args.effort}")

    registry = PromptRegistry()
    factory, item_ids, block_version = BLOCKS[args.block]
    if args.prompt_version is None:
        args.prompt_version = block_version
    # ⚠ E-01 keeps its v2 factory reachable for A/B work; every other block
    #   ships exactly one version.
    if args.block == "E-01" and args.prompt_version == "v2":
        factory = e01_v2
    registry.register(factory())
    bundle = build_bundle(whole_filing=not args.segment_note_only)
    chars = sum(len(p.content) for p in bundle.parts)
    # ⚠ MEASURED 2026-09-07: this filing tokenised at 2.78 chars/token, not the
    # 4.0 assumed here first — table text with `|` separators and digits is far
    # denser than prose, and the estimate came out 43% LOW.
    est_in = int(chars / 2.78) + 500
    # ⚠ READ from the cap, never retyped beside it. This said 32,000 while the
    #   cap was 12,000 — the same drift as the hardcoded "E-01 v1" label, in the
    #   number a reader uses to decide whether to spend.
    from src.fundamental.prompts.call import MAX_TOKENS
    est_out = MAX_TOKENS["extraction"]

    print(f"  filing     : {FILING.relative_to(REPO)}")
    print(f"  bundle     : {chars:,} chars  (hash {bundle.bundle_hash[:16]}…)")
    # ⚠ The version is READ, not typed. This line said "E-01 v1" while running
    #   v2 — a label hardcoded beside the value it describes drifts the moment
    #   the value changes, and it is the printout a reader trusts.
    # ⚠⚠ `DX-67` — print the COMPOSED length, not the block's. The comment
    #   above warns that a label beside the value it describes drifts; this
    #   line then reported 1,210 chars while 7,504 were being sent, because the
    #   shared envelope is composed downstream in `call.py`.
    _blk = registry.get(args.block, args.prompt_version)
    from src.fundamental.prompts.envelope import compose_prompt
    print(f"  block      : {args.block} {args.prompt_version}  "
          f"({len(_blk.text)} chars + envelope = "
          f"{len(compose_prompt(_blk, stage_a=(_blk.view == 'blind')))} sent)")
    print(f"  est tokens : ~{est_in:,} in / ~{est_out:,} out (incl. thinking)")
    print(f"  est cost   : ~${est_in * PRICE_IN + est_out * PRICE_OUT:.2f}")

    if args.dry_run:
        print("\n  ⓘ dry run — nothing was sent and nothing was recorded.")
        print("  ⚠ --live spends real money. Re-run with it when you want the")
        print("    recording that gives F5 cases 1 and 2 their input_ref.")
        return 0

    # ⚠⚠ Do NOT gate on ANTHROPIC_API_KEY. An unset key does not mean there are
    # no credentials: the SDK resolves ANTHROPIC_API_KEY → ANTHROPIC_AUTH_TOKEN
    # → an `ant auth login` profile → workload identity → the default profile.
    # ★ Gating on the env var alone refuses to run for anyone authenticated by
    #   profile — a working setup told it was broken. Let the SDK decide, and
    #   report ITS answer.

    # ⚠ Imported here so a --dry-run needs neither the SDK nor a key.
    from src.fundamental.prompts.call import AnalysisGateway
    from src.fundamental.prompts.envelope import envelope_hash
    from src.orchestration.trace.store import TraceStore
    from src.orchestration.trace.wire import traced_transport
    from src.shared.config import Config
    from src.shared.llm.gateway import Gateway
    from tools.anthropic_transport import anthropic_transport, extraction_tool

    # ⚠ DX-26 — a date alone repeats all day, so two runs appended to ONE
    # trace. The seconds make each run its own record.
    run_id = (f"run-{datetime.now().strftime('%Y-%m-%dT%H%M%S')}-"
              f"{TICKER.lower()}-{args.block.lower().replace('-', '')}")
    store = TraceStore(REPO / ".state/runs", run_id)
    print(f"\n  ⚠ LIVE. run_id = {run_id}")

    # ★ traced_transport wraps the vendor call, so CT-2.2 records the request
    #   and response with ZERO edits to inherited D-00 code (AC-2.1).
    # ★ C12 — the pricer is injected, so the trace records what the call cost
    #   at write time. ⚠ An earlier attempt to wire this silently no-opped
    #   because the edit's anchor did not match, and `cost_usd` stayed null
    #   through a whole live run. A replace that cannot fail is a change that
    #   cannot be trusted.
    def _cost_of(model_id, tokens):
        rate_in = GATEWAY_VALUES.get(f"llm.pricing.{model_id}.input_per_mtok")
        rate_out = GATEWAY_VALUES.get(f"llm.pricing.{model_id}.output_per_mtok")
        if rate_in is None or rate_out is None:
            return None          # ⚠ absent, never 0
        return (tokens.get("input", 0) * rate_in / 1e6
                + tokens.get("output", 0) * rate_out / 1e6)

    transport = traced_transport(
        anthropic_transport(tool=extraction_tool(item_ids)), store,
        step_id=f"extract:{args.block}", cost_of=_cost_of,
        # ⚠⚠ Without this the trace records `prompt_version: None` — so a
        # recording cannot say WHICH prompt produced it, and a golden case
        # grading it cannot tell whether it still grades what we ship.
        prompt_version=args.prompt_version,
        # ⚠⚠ `DX-76` — WHICH envelope. Without it the recording says
        # which BLOCK version ran and stays silent about the shared
        # sections composed in front of it, which is the half `DX-67`
        # changed without bumping anything.
        envelope_hash=envelope_hash("extraction"))
    gateway = Gateway(Config(GATEWAY_VALUES, sources=("tools/run_extraction_once.py",)),
                      transport=transport)
    seam = AnalysisGateway(gateway, registry)

    # ⚠⚠ DX-26 — close EXACTLY ONCE, with the outcome that actually happened.
    # An earlier `finally: store.close("SUCCESS")` wrote SUCCESS whatever the
    # result, so the trace asserted success about a failed run. ★ A trace that
    # can disagree with its own run is worse than no trace.
    try:
        result = run_extraction(seam, block_ids=[(args.block, args.prompt_version)], bundle=bundle,
                                run_id=run_id,
                                parse=lambda c: parse_items(c, bundle.parts[0].content))
    except Exception as exc:                       # noqa: BLE001
        store.close("FAILED")
        if "authentication" in str(exc).lower() or "api_key" in str(exc).lower():
            print("\n  ⛔ No Anthropic credentials found. Either:")
            print("       export ANTHROPIC_API_KEY=sk-ant-...")
            print("     or install the `ant` CLI and run `ant auth login`.")
            print(f"  ⓘ the failed attempt is recorded at .state/runs/{run_id}/")
            return 1
        raise
    store.close("SUCCESS")

    (extraction,) = result.results
    print(f"  ✅ {len(extraction.items)} item(s) extracted and verified")

    # ★ ACTUAL cost, from the trace — not the estimate. The gateway computes it
    #   per call from `llm.pricing.*`, so this is what the run really used.
    for rec in store.read_all():
        if rec.get("type") != "ExternalCall":
            continue
        tok = rec.get("tokens") or {}
        tin, tout = tok.get("input", 0), tok.get("output", 0)
        actual = rec.get("cost_usd")
        print("\n  ── actual, from the trace ──")
        print(f"  tokens     : {tin:,} in / {tout:,} out")
        if actual is None:
            # ⚠⚠ F2 gap: `traced_transport` wraps the TRANSPORT, so it sees
            # tokens but never the gateway's computed cost — `cost_usd` is
            # always null on these records. ★ Recomputed here from the same
            # `llm.pricing.*` numbers so the figure is not simply lost.
            actual = tin * PRICE_IN + tout * PRICE_OUT
            note = "  (recomputed — cost_usd is null in the trace, F2 gap)"
        else:
            note = ""
        print(f"  cost       : ${actual:.4f}{note}")
        print(f"  estimated  : ${est_in * PRICE_IN + est_out * PRICE_OUT:.2f}")
        print(f"  latency    : {rec.get('latency_ms', 0):,} ms")
    call_id = None
    for record in store.read_all():
        if record.get("payload_ref"):
            call_id = record["payload_ref"]
    print(f"\n  ★ input_ref prefix for F5's golden cases:\n      {run_id}/{call_id}")
    print("  ⚠ Append the selector already written in each case, e.g.")
    print(f"      {run_id}/{call_id}#seg.revenue|CNBU|2025-02-28:2025-05-29")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
