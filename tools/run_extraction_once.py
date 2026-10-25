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
from src.fundamental.claims.models import sector_citation  # noqa: E402
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


def extraction_family() -> dict:
    """F13 `D14` / AC-F13.20 — `{block: tool}` for every E-block a thesis reads (`D8`).

    ★ The SAME family in every extraction process, so seven runs over one filing send one
    tools segment and the filing they share stays cached (GW-31). Keyed by block: every
    extraction tool is named `record_extractions`.
    """
    from src.fundamental.on_demand.chain import E_BLOCKS
    from tools.anthropic_transport import extraction_tool

    return {b: extraction_tool(BLOCKS[b][1]) for b in E_BLOCKS}

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

#: ✏ 2026-10-04 (`L3` §2.1p row 6) — bundles of SEVERAL documents, for blocks that read more
#: than one filing: `E-03` (this annual filing against the prior one) and `E-08` (Form 4s).
#: ★ A section is cut at its HEADINGS, never at line numbers — a range tuned to one filing
#: silently slices the wrong text out of another (see `slice` above).
DOCUMENT_SETS = {
    "mu-10k-risk-factors": {
        "ticker": "MU", "as_of": date(2025, 6, 26),
        "section": ("ITEM 1A. RISK FACTORS", "ITEM 1B. UNRESOLVED STAFF COMMENTS"),
        "docs": (
            {"path": "tests_src/fixtures/filings/MU_FY2024_10K.txt",
             "accession": "0000723125-24-000027", "form": "10-K", "period_end": "2024-08-29"},
            {"path": "tests_src/fixtures/filings/MU_FY2023_10K.txt",
             "accession": "0000723125-23-000054", "form": "10-K", "period_end": "2023-08-31"},
        )},
    "mu-form4-2025q3": {
        "ticker": "MU", "as_of": date(2025, 6, 26),
        "index": "tests_src/fixtures/filings/MU_form4_2025-02-28_2025-06-25/index.json"},
}

#: ★ Module-level defaults, unchanged: `golden_replay` and the wiring tests
#: import `FILING`, and filing 1's cases resolve against it.
#: ★ `DX-119` — who the analysis is ABOUT, for a bundle that cannot say so itself (an
#: industry bundle carries the competitors' documents, not the subject's). ⚠ Declared, never
#: inferred: guessing the subject is how `E-13` came to name Micron as its own competitor.
SUBJECT_NAMES = {"MU": "Micron Technology, Inc.", "AMD": "Advanced Micro Devices, Inc."}


def subject_name(ticker: str) -> str:
    """AC-F13.22 — the declared subject: `SUBJECT_NAMES`, else `config/thesis_for.yaml`'s
    `subjects` (F13 `D15`). ⚠ A ticker declared in neither is refused, never guessed."""
    if ticker in SUBJECT_NAMES:
        return SUBJECT_NAMES[ticker]
    import yaml

    config = yaml.safe_load((REPO / "config/thesis_for.yaml").read_text(encoding="utf-8"))
    entry = (config.get("subjects") or {}).get(ticker)
    if not entry:
        raise SystemExit(f"{ticker} is declared neither in SUBJECT_NAMES nor in "
                         f"config/thesis_for.yaml — the subject is never inferred (DX-119)")
    return entry["name"]

TICKER = "MU"
FILING = REPO / FILINGS[TICKER]["path"]
ACCESSION = FILINGS[TICKER]["accession"]


def _declared_versions() -> list[str]:
    """Every prompt version any E-block declares (`DX-88`)."""
    import src.fundamental.prompts.e_blocks as eb
    return sorted({m.group(1).lower() for name in dir(eb)
                   if (m := re.match(r"E\d\d_(V\d+)_TEXT$", name))})


def _select(ticker: str) -> None:
    """Point the module at another filing. ⚠ Explicit, never implicit."""
    global TICKER, FILING, ACCESSION
    TICKER = ticker
    FILING = REPO / FILINGS[ticker]["path"]
    ACCESSION = FILINGS[ticker]["accession"]


def add_filing_args(ap) -> None:
    """★ F13 `D1` — the filing as ARGUMENTS. Omitted, the `FILINGS` defaults apply unchanged
    (AC-F13.9); given, they name a fixture from `tests_src/fixtures/filings/index.json`."""
    ap.add_argument("--filing", default=None, metavar="FIXTURE_TXT",
                    help="a converted filing fixture (default: the ticker's FILINGS entry)")
    ap.add_argument("--accession", default=None)
    ap.add_argument("--form", default=None, choices=["10-Q", "10-K"])
    ap.add_argument("--period-end", default=None, metavar="DATE")
    ap.add_argument("--as-of", dest="filing_as_of", default=None, metavar="DATE",
                    help="the analysis date (default: the FILINGS entry's)")


def apply_filing_args(args) -> bool:
    """Register `--filing …` as the ticker's entry. Returns whether one was given.

    ⚠ All five together or none — a filing with a guessed accession or period would pin a
    bundle to the wrong document (`RA-1`).
    """
    given = [args.filing, args.accession, args.form, args.period_end, args.filing_as_of]
    if not any(given):
        return False
    if not all(given):
        raise SystemExit("--filing needs --accession, --form, --period-end and --as-of too")
    path = pathlib.Path(args.filing)
    path = (path if path.is_absolute() else REPO / path).resolve()
    FILINGS[args.ticker] = {"path": str(path.relative_to(REPO)),
                            "accession": args.accession,
                            "as_of": date.fromisoformat(args.filing_as_of),
                            "form": args.form, "period_end": args.period_end}
    return True


def record_filing(run_dir: pathlib.Path) -> None:
    """★ F13 — `filing.json` beside the trace, so `rule_checks` reads THIS run's filing."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "filing.json").write_text(json.dumps(
        {"fixture": FILINGS[TICKER]["path"], "accession": FILINGS[TICKER]["accession"],
         "form": FILINGS[TICKER].get("form", "10-Q")}, indent=1), encoding="utf-8")

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
#: `DX-102` — lines that only ever appear in THIS repo's annotations, never in
#: an SEC filing. ★ Specific phrases, not a heuristic: a false refusal of a real
#: filing would be worse than useless.
REPO_ANNOTATION_MARKERS = (
    "PROVENANCE — do not edit below this header",
    "READ BEFORE ESTABLISHING A GOLDEN VALUE",
    "tools/convert_filing.py",
)


def assert_no_repo_annotation(text: str, path) -> None:
    """⛔ `DX-102` / `RA-1` — a bundle is evidence and nothing else (`P5`)."""
    found = [m for m in REPO_ANNOTATION_MARKERS if m in text]
    if found:
        raise ValueError(
            f"{path} carries repo annotation {found} inside the filing text. ⛔ "
            f"DX-102 — it would be sent to the model as SEC evidence, and X-01 would "
            f"accept a quote taken from it. Move it to the .meta.txt sidecar.")


def load_sector_file(path):
    """A sector file from its JSON — v1 or v2 (✏ 2026-10-04: `value`/`unit`/`period`)."""
    import json as _json

    from src.fundamental.sector.models import Omission, SectorFile, SectorRecord
    from src.fundamental.sector.schema import SCHEMA_V1

    doc = _json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return SectorFile(
        industry=doc["industry"], as_of=date.fromisoformat(doc["as_of"]),
        file_version=int(doc["file_version"]), source_list_version=doc["source_list_version"],
        records=tuple(SectorRecord(record_id=r["record_id"],
                                   date=date.fromisoformat(r["date"]), kind=r["kind"],
                                   subject=r["subject"], source_id=r["source_id"],
                                   url=r.get("url", ""), quote=r["quote"],
                                   status=r.get("status", ""),
                                   prior_status=r.get("prior_status", ""),
                                   value=r.get("value", ""), unit=r.get("unit", ""),
                                   period=r.get("period", ""))
                      for r in doc["records"]),
        omissions=tuple(Omission(**o) for o in doc.get("omissions", ())),
        schema_version=doc.get("schema_version", SCHEMA_V1))


def sector_bundle(path, *, ticker: str) -> EvidenceBundle:
    """`DX-117` — the industry evidence as ONE pinned `sector_file` part.

    ★ Every document travels verbatim, in the file's one permitted order (`RA-99`), with its
    source and date; `X-01` then verifies every quote `E-13` returns against this text.
    """
    from src.fundamental.bundle.assemble import sector_file

    file = load_sector_file(path)
    return EvidenceBundle(ticker=ticker.upper(), as_of=file.as_of,
                          parts=(sector_file(file),))


def document_set_bundle(name: str, *, only: str | None = None) -> EvidenceBundle:
    """A bundle of several documents, one `filing` part each, pinned by accession (`RA-1`).

    ✏ `DX-149` ⓐ — `only` keeps ONE document of the set: its own single-document bundle.
    """
    spec = DOCUMENT_SETS[name]
    if "index" in spec:
        index = REPO / spec["index"]
        docs = [{"path": str(index.parent.relative_to(REPO) / f"{f['accession']}.txt"),
                 "accession": f["accession"], "form": "4", "period_end": f["filed"]}
                for f in json.loads(index.read_text(encoding="utf-8"))["forms"]]
    else:
        docs = list(spec["docs"])
    if only is not None:
        docs = [d for d in docs if d["accession"] == only]
        if not docs:
            raise KeyError(f"{only!r} is not a document of {name!r}")
    parts = []
    for d in docs:
        path = REPO / d["path"]
        text = path.read_text(encoding="utf-8")
        assert_no_repo_annotation(text, path)
        if "section" in spec:
            head, tail = spec["section"]
            if text.count(head) != 1 or text.count(tail) != 1:
                raise ValueError(f"{path.name}: the section headings {spec['section']} must each "
                                 f"occur exactly once (P5 — never guess which one)")
            text = text[text.index(head):text.index(tail)]
        parts.append(BundlePart(kind="filing",
                                pins={"accession_id": d["accession"], "form": d["form"],
                                      "period_end": d["period_end"]},
                                content=text))
    return EvidenceBundle(ticker=spec["ticker"], as_of=spec["as_of"], parts=tuple(parts))


def build_bundle(*, whole_filing: bool = True) -> EvidenceBundle:
    """`RA-1` — every LLM call takes an `EvidenceBundle` and nothing else.

    ⚠ The `content` here is what `X-01` verifies quotes against, so it must be
    the SAME text a human re-checks the golden case against. That is why the
    fixture is the whole converted filing rather than an excerpt.
    """
    text = FILING.read_text(encoding="utf-8")
    # ⛔⛔ `DX-102` — the fixture's repo annotations were INSIDE every bundle
    #   (*"READ BEFORE ESTABLISHING A GOLDEN VALUE"*, *"a converter an AI agent
    #   wrote"*), sent to the model as SEC evidence. They now live in a
    #   `.meta.txt` sidecar; this refuses a fixture that carries them again.
    assert_no_repo_annotation(text, FILING)
    if not whole_filing:
        # ★ The segment note only — ~18x cheaper, and enough for E-01.
        # ⚠ A narrower bundle is a DIFFERENT bundle_hash, so a golden case
        #   recorded against one does not transfer to the other.
        lines = text.splitlines()
        lo, hi = FILINGS[TICKER]["slice"]
        text = "\n".join(lines[lo:hi])
    return EvidenceBundle(
        ticker=TICKER, as_of=FILINGS[TICKER]["as_of"],
        # ⚠ The defaults are filing 1's pins, kept for every entry that declares none —
        #   including AMD's, whose recordings were made under them (AC-F13.9).
        parts=(BundlePart(kind="filing",
                          pins={"accession_id": ACCESSION,
                                "form": FILINGS[TICKER].get("form", "10-Q"),
                                "period_end": FILINGS[TICKER].get("period_end", "2025-05-29")},
                          content=text),),
    )


# --------------------------------------------------------------------------- #
# 3. the parse — response -> ExtractedItem[]
# --------------------------------------------------------------------------- #
def parse_items(call, bundle_text: str | None = None, accession_id: str | None = None,
                documents: dict[str, str] | None = None) -> list:
    """Map one `CallResult` to `ExtractedItem`s (`MP-5`, `MP-18`).

    ⚠ **Offsets are computed here, not asked for.** A model-supplied character
    offset is a number it cannot verify and we can: `X-01` would reject a wrong
    one anyway, so asking for it spends tokens to create a failure mode.
    ★ The quote is the model's; the offset is arithmetic (`AP-5`).

    ✏ 2026-10-04 — `documents` (accession → text) is a bundle of several documents: each
    found item must NAME one of them, and its quote is located in that one only.
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
    if bundle_text is None and documents is None:
        bundle_text = FILING.read_text(encoding="utf-8")
    flat_bundle = " ".join((" ".join(documents.values()) if documents else bundle_text).split())  # DX-131
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
            # ★ `DX-135` — the qualifier names WHAT is absent; keep it.
            out.append(not_found(row["evidence_id"],
                                 note=f"{note} — {where}" if where else note,
                                 qualifier=row.get("qualifier", "")))
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
        cited, text = accession_id, bundle_text
        if documents is not None:
            cited = row.get("accession_id")
            if cited not in documents:
                raise ValueError(
                    f"{row['evidence_id']!r}: the bundle holds {len(documents)} documents and "
                    f"this item names no document it holds ({cited!r}) — its quote cannot be "
                    f"attributed (X-01, RA-131)")
            text = documents[cited]
        start, end = _locate(text, quote)
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
        period_start, period_end, cleared = _stated_period(
            flat_bundle, row.get("period_start"), row.get("period_end"))
        note = row.get("note", "")
        if row["evidence_id"] == "in.type":
            # ★ `DX-148` ⓑ — the value stays the form's code (X-01 ② checks it); the label is a
            #   lookup, stated beside it, never chosen by the model.
            from src.fundamental.filings.form4 import transaction_label
            note = " ".join(filter(None, [note, f"[DX-148] label: {transaction_label(value)}"]))
        if cleared:
            note = " ".join(filter(None, [note, (
                f"[DX-131] period date(s) {', '.join(cleared)} not stated in the "
                "document — cleared, never computed")]))
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
            quote=quote, accession_id=cited or ACCESSION, offset=(start, end),
            period_start=period_start, period_end=period_end,
            cumulative_ytd=bool(row.get("cumulative_ytd")),
            qualifier=row.get("qualifier", ""), note=note,
        ))
    if documents is not None:
        # ★ `DX-149` ⓒ (Victor, 2026-10-04) — `X-01` proves what an answer holds, never what it
        #   left out: one call over 20 Form 4s returned items from 6 and said nothing of 14.
        #   A document counts as read when a found item cites it or a not_found names it.
        cited = {it.span.accession_id for it in out if it.span is not None}
        stated = " ".join(it.note for it in out if it.span is None)
        silent = [a for a in documents if a not in cited and a not in stated]
        if silent:
            raise ValueError(
                f"the answer cites nothing from {len(silent)} of {len(documents)} documents "
                f"and names none of them as empty: {silent[:5]} — a document left out "
                f"silently is not read (DX-149, RA-98)")
    return _dedupe_not_found(out)


def _date_forms(iso: str) -> tuple[str, ...]:
    """The ways a filing writes one date: `May 29, 2025`, `May 29 2025`,
    `2025-05-29`, `5/29/2025`, `05/29/2025`."""
    d = date.fromisoformat(iso)
    month, short = d.strftime("%B"), d.strftime("%b")
    return (f"{month} {d.day}, {d.year}", f"{month} {d.day} {d.year}",
            f"{short} {d.day}, {d.year}", f"{short}. {d.day}, {d.year}", iso,
            f"{d.month}/{d.day}/{d.year}", f"{d.month:02d}/{d.day:02d}/{d.year}")


def _stated_period(flat_bundle: str, start, end) -> tuple:
    """★★ `DX-131` (Victor, 2026-10-01) — keep a period date only if the document STATES it.

    ⚠ The shared envelope asks for "both period endpoints" on a year-to-date
    figure, and a filing gives only the end ("nine months ended May 29, 2025").
    So `E-07` `E-09` `E-10` `E-12` returned the prior year end PLUS ONE DAY —
    arithmetic `S-2` forbids. ★ Enforced here, for every block at once, because
    the prompt-level fix (`DX-73`) reached one block only. The same ruling as
    `DX-73`: the date is cleared, never computed; D-02 may derive one, labelled.

    Returns `(start, end, cleared)`. An unstated END clears the whole period.
    """
    def stated(iso):
        try:
            return any(form in flat_bundle for form in _date_forms(str(iso)))
        except ValueError:
            return False                      # not an ISO date: not a stated date
    cleared = [str(v) for v in (start, end) if v and not stated(v)]
    if end and str(end) in cleared:
        return None, None, cleared
    return (start if start and str(start) not in cleared else None), end, cleared


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
def _guarded(run, argv: list[str]) -> int:
    """A document's failure is REPORTED and counted, never allowed to end the loop (`P5`)."""
    try:
        return run(argv)
    except Exception as exc:                     # noqa: BLE001 — named, counted, non-zero
        print(f"  ⛔ {argv[argv.index('--document') + 1]}: {type(exc).__name__}: {exc}")
        return 1


def _run_one(argv: list[str]) -> int:
    """One document's run — its own `run_id`, trace and `bundle_hash` (`DX-149` ⓐ)."""
    return _guarded(main, argv)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="★ free — plan + cost")
    g.add_argument("--live", action="store_true", help="⚠ SPENDS MONEY")
    # ⚠ `DX-88` — `choices=sorted(BLOCKS)` offered J-01…J-08 once Stage A was
    #   declared, so `--block J-03` would have been sent down the EXTRACTION
    #   path with an extraction tool. ★ Filtered by kind (`RA-5`).
    ap.add_argument("--block", default="E-01",
                    choices=sorted(b for b in BLOCKS
                                   if BLOCKS[b][0]().kind == "extraction"),
                    help="which E-block to run (default E-01 = filing 1's)")
    # ⚠ `DX-88` — the choices were hardcoded `["v2", "v3"]` while `E-01` ships
    #   `v4`: `DX-72`'s shape (a list pinned to the versions that existed when it
    #   was written). ★ Derived from the declared `E0n_Vn_TEXT` constants.
    ap.add_argument("--prompt-version", default=None,
                    choices=_declared_versions(),
                    help="⚠ v3 is a CANDIDATE; shipping it retires filing 1's "
                         "recording (L7 §5), so it is opt-in")
    ap.add_argument("--effort", default=None,
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="⚠ overrides llm.deep.effort. Extraction is "
                         "transcription; thinking is what truncates a run")
    # ★ `DX-96` — diagnostic only: show summarized thinking (still ON, `GW-9c`).
    ap.add_argument("--thinking-display", default=None, choices=["summarized"],
                    help="DIAGNOSTIC: record summarized thinking for a runaway call")
    ap.add_argument("--ticker", default="MU",
                    help="which filing (default MU = filing 1); one outside FILINGS needs --filing")
    add_filing_args(ap)
    # ★★ `DX-117` — run an E-block over the INDUSTRY sector file instead of the filing.
    #   The subject (the company being analysed) is declared, because the documents are
    #   the competitors' own and carry no cover page for it (`DX-119`).
    ap.add_argument("--sector", default=None, metavar="SECTOR_FILE_JSON",
                    help="run over the sector file (tools/ingest_sector_file.py output)")
    # ✏ 2026-10-04 — a bundle of several documents (`E-03`'s two 10-Ks, `E-08`'s Form 4s).
    ap.add_argument("--document-set", default=None, choices=sorted(DOCUMENT_SETS),
                    help="run over a declared set of documents instead of one filing")
    ap.add_argument("--document", default=None, metavar="ACCESSION",
                    help="with --document-set: only this document (its own bundle and run)")
    ap.add_argument("--per-document", action="store_true",
                    help="with --document-set: one run per document (DX-149 ⓐ)")
    ap.add_argument("--segment-note-only", action="store_true",
                    help="⚠⚠ DIAGNOSTIC ONLY (DX-32) — never for a recording "
                         "a golden case grades: the slice omits the evidence a "
                         "PERIOD START is derived from, so discrete and "
                         "cumulative figures collapse onto one MP-18 identity")
    ap.add_argument("--cache-evidence", action="store_true",
                    help="★ F13 D14 — send the bundle FIRST, as the cached prefix, with one "
                         "schema family for every D8 block (thesis_for passes it)")
    args = ap.parse_args(argv)
    if (args.document or args.per_document) and not args.document_set:
        print("  ⛔ --document / --per-document need --document-set")
        return 2
    if args.per_document:
        # ★ `DX-149` ⓐ — each document is its own call, so no answer has to hold twenty.
        rest = [a for a in (argv if argv is not None else sys.argv[1:]) if a != "--per-document"]
        accessions = [p.pins["accession_id"] for p in document_set_bundle(args.document_set).parts]
        failed = [a for a in accessions if _run_one([*rest, "--document", a]) != 0]
        print(f"\n  ── per-document: {len(accessions) - len(failed)} of {len(accessions)} "
              f"run(s) succeeded" + (f" · ⛔ FAILED {failed}" if failed else ""))
        return 1 if failed else 0
    custom_filing = apply_filing_args(args)
    if args.ticker not in FILINGS:
        print(f"  ⛔ no filing for {args.ticker} — pass --filing (F13)")
        return 2
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
    subject = subject_name(args.ticker) if args.sector else None
    if args.document_set and (args.sector or args.segment_note_only):
        print("  ⛔ --document-set is its own bundle; it does not combine with --sector or "
              "--segment-note-only")
        return 2
    bundle = (sector_bundle(args.sector, ticker=args.ticker) if args.sector
              else document_set_bundle(args.document_set, only=args.document)
              if args.document_set
              else build_bundle(whole_filing=not args.segment_note_only))
    if subject:
        # ★ `DX-119` — printed because it is a DECLARATION, not a default: a reader of the
        #   run must see which company may not appear among its own competitors.
        print(f"  subject    : {subject} (declared — the industry bundle has no cover page)")
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

    if args.document_set:
        print(f"  documents  : {args.document_set} — {len(bundle.parts)} part(s): "
              + ", ".join(p.pins["accession_id"] for p in bundle.parts[:4])
              + (" …" if len(bundle.parts) > 4 else ""))
    else:
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
    from tools.anthropic_transport import extraction_tool
    from tools.llm_transport import dev_transport, price_factor, transport_label

    # ⚠ DX-26 — a date alone repeats all day, so two runs appended to ONE
    # trace. The seconds make each run its own record.
    run_id = (f"run-{datetime.now().strftime('%Y-%m-%dT%H%M%S')}-"
              f"{TICKER.lower()}-{args.block.lower().replace('-', '')}"
              # ✏ `DX-149` ⓐ — one run per document: the document names its run.
              + (f"-{args.document.split('-')[-1]}" if args.document else ""))
    store = TraceStore(REPO / ".state/runs", run_id)
    print(f"\n  ⚠ LIVE. run_id = {run_id}")
    print(f"  transport  : {transport_label()}")

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
        # ★ GW-27 — $0 on the subscription; the CLI's list price is `notional_usd`.
        return (tokens.get("input", 0) * rate_in / 1e6
                + tokens.get("output", 0) * rate_out / 1e6) * price_factor()

    transport = traced_transport(
        dev_transport(tool=extraction_tool(item_ids),
                      thinking_display=args.thinking_display,
                      **({"family": extraction_family(), "family_key": args.block}
                         if args.cache_evidence else {})), store,
        step_id=f"extract:{args.block}", cost_of=_cost_of,
        # ⚠⚠ Without this the trace records `prompt_version: None` — so a
        # recording cannot say WHICH prompt produced it, and a golden case
        # grading it cannot tell whether it still grades what we ship.
        prompt_version=args.prompt_version,
        # ⚠⚠ `DX-76` — WHICH envelope. Without it the recording says
        # which BLOCK version ran and stays silent about the shared
        # sections composed in front of it, which is the half `DX-67`
        # changed without bumping anything.
        envelope_hash=envelope_hash("extraction"),
        # ★ `DX-95` — WHICH bundle this call read (`RA-2`).
        bundle_hash=bundle.bundle_hash)
    if args.cache_evidence:
        # ★ F13 `D14` — ABOVE the trace, so the recording says what was sent.
        from tools.llm_transport import evidence_first
        transport = evidence_first(transport)
    gateway = Gateway(Config(GATEWAY_VALUES, sources=("tools/run_extraction_once.py",)),
                      transport=transport)
    seam = AnalysisGateway(gateway, registry)

    # ⚠⚠ DX-26 — close EXACTLY ONCE, with the outcome that actually happened.
    # An earlier `finally: store.close("SUCCESS")` wrote SUCCESS whatever the
    # result, so the trace asserted success about a failed run. ★ A trace that
    # can disagree with its own run is worse than no trace.
    try:
        result = run_extraction(seam, block_ids=[(args.block, args.prompt_version)], bundle=bundle,
                                subject=subject,
                                run_id=run_id,
                                parse=lambda c: parse_items(
                                    c, bundle.parts[0].content,
                                    # ⚠ `DX-121` — an industry quote cites the SECTOR FILE,
                                    #   not the analysed company's accession.
                                    accession_id=sector_citation(bundle.parts[0].pins)
                                    or (bundle.parts[0].pins["accession_id"]
                                        if args.document_set else None),
                                    documents=({p.pins["accession_id"]: p.content
                                                for p in bundle.parts}
                                               if len(bundle.parts) > 1 else None)))
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
    if custom_filing:
        record_filing(REPO / ".state/runs" / run_id)

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
