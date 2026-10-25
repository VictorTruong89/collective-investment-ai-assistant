#!/usr/bin/env python3
"""Rule checks — properties every recorded LLM call must satisfy, whatever it answers.

    python3 tools/rule_checks.py                    # the promoted recordings
    python3 tools/rule_checks.py .state/runs        # live runs on this machine

`L8` §9 rule 4ⓑ (Victor, 2026-10-01): judgement quality is no longer measured by
golden cases. ★ A golden case asks *"does the model still agree with one reader?"*;
a rule check asks *"did this call obey the contract?"*, which has a right answer
for every call, needs no signature, and covers every block at once.

| Rule | Fires when |
|---|---|
| `leaked-tool-syntax` | an answer contains raw tool-call markup (`<parameter …>`) — `DX-134` |
| `incomplete-call` | a call stopped at `max_tokens`, or returned nothing — `DX-133`: `{}` PARSES |
| `quote-not-in-source` | a `FACT [...] "…"` quote attributed to the document is not in it |
| `absent-input-not-refused` | the bundle declared an input absent and the answer used one anyway |

⚠ **Not checked here, because it is enforced upstream for every call:** extraction
quotes (`X-01`, and `test_every_recorded_quote_still_resolves_in_its_filing`) and
unstated period dates (`DX-131`, cleared in `parse_items`).
"""

from __future__ import annotations

import contextlib
import json
import pathlib
import re
import sys
from dataclasses import dataclass

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))                   # run as a script, like the other tools
RECORDINGS = REPO / "tests_src/fixtures/recordings"
DEFAULT_FILING = REPO / "tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt"

LEAKED_TOOL_SYNTAX = "leaked-tool-syntax"
INCOMPLETE_CALL = "incomplete-call"
QUOTE_NOT_IN_SOURCE = "quote-not-in-source"
ABSENT_INPUT_NOT_REFUSED = "absent-input-not-refused"


@dataclass(frozen=True, order=True)
class Violation:
    run: str
    call: str
    rule: str
    detail: str


#: ★ Every violation present in the promoted recordings on 2026-10-01, each with the
#: finding that explains it. `tests/structural/test_rule_checks_recordings.py` asserts the
#: checker finds EXACTLY these: a new one fails the suite, and a fixed one must be removed
#: from here — so this list can never quietly stop describing the recordings.
KNOWN: dict[tuple[str, str, str], str] = {
    ("run-2026-09-15T022801-mu-thesis", "judge:C:J-11:llm:1", LEAKED_TOOL_SYNTAX):
        "DX-134 — `<parameter name=\"reason\">` captured inside `strongest_reason`",
    ("run-2026-09-12T024848-mu-stage-a", "judge:J-03:llm:1", QUOTE_NOT_IN_SOURCE):
        "DX-138 — quotes NAND ASPs as 'plus low-50%'; the filing says 'plus low-30%'",
    ("run-2026-09-12T024848-mu-stage-a", "judge:J-08:llm:1", QUOTE_NOT_IN_SOURCE):
        "DX-138 — drops 'also' from 'We have also signed a non-binding term sheet'",
    ("run-2026-09-11T111240-mu-j01", "judge:J-01:llm:1", INCOMPLETE_CALL):
        "DX-84 — the truncated J-01 (4,000 out, `why` absent); no case points at it since 2026-09-11",
}

# ── leaked tool syntax ──────────────────────────────────────────────────────

_TOOL_MARKUP = re.compile(r"<\s*/?\s*(?:parameter|invoke|function_calls)\b|antml:", re.I)

# ── quotes ──────────────────────────────────────────────────────────────────

#: `FACT [source] — "quote"`, the citation form the judgement envelope asks for.
_FACT_QUOTE = re.compile(r'FACT \[([^\]]+)\][^"“]{0,40}["“]([^"”]{12,}?)["”]')
#: A FACT whose source is NOT the filing: computed D-02 values, frozen answers from
#: earlier blocks, declared absences, extraction items. ⚠ Exempt, never assumed false.
_NOT_THE_FILING = re.compile(
    r"D-02|frozen|declared absent|not_found|status found|computed|J-\d\d|E-\d\d|bundle|"
    r"commit|basis|implied|band|price|rubric|^[a-z]{2}\.[a-z_]+|"
    # ✏ 2026-10-03 — the computed sections `F11` and the consensus part add to the bundle
    r"margin reach|fcff runs|cagr reach|reference.class|published|consensus|ratings|"
    # ✏ 2026-10-23 — the same F11 section, named by the model as "base rates" (SNDK J-11, J-16)
    r"base.rates?", re.I)
#: A quote may be abridged; each piece must be verbatim.
_ABRIDGED = re.compile(r"\.\.\.|…")
_MIN_PIECE = 10


def _letters_digits(text: str) -> str:
    """Compare on letters and digits only: a table row the filing splits across
    lines, or spacing around `|` and `$`, is layout, not content. A changed word or
    number still differs."""
    return re.sub(r"[^0-9a-z]", "", text.lower())


_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})|\\(n|t|\")")


def _unescape(text: str) -> str:
    """Decode escapes left by a double-encoded answer (`J-13` stores JSON in a string)."""
    return _ESCAPE.sub(lambda m: chr(int(m[1], 16)) if m[1]
                       else {"n": "\n", "t": "\t", '"': '"'}[m[2]], text)


def _strings(obj):
    """Every string in an answer, descending into JSON that was stored as a string."""
    if isinstance(obj, str):
        yield _unescape(obj)
        stripped = obj.strip()
        if stripped[:1] in "[{":
            with contextlib.suppress(ValueError):
                yield from _strings(json.loads(stripped))
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _strings(value)


# ── declared absences ───────────────────────────────────────────────────────

_ABSENT_HEADER = "DECLARED ABSENT INPUTS"


def _declared_absences(request: dict) -> set[str] | None:
    """The input names this call's bundle declared absent, or None if unknowable.

    ⚠ Promoted recordings ELIDE the bundle, so for them the run's declaration is gone.
    The fallback is `STAGE_B_ABSENCES` itself: no bundle has ever been built without
    those absences, because no source for them exists yet (L3 §2.1p item 5).
    """
    text = "\n".join(str(request.get(k) or "") for k in ("cache_prefix", "payload"))
    if _ABSENT_HEADER not in text:
        return None
    names: set[str] = set()
    for block in text.split(_ABSENT_HEADER)[1:]:
        for line in block.splitlines()[1:]:
            if not line.startswith("- "):
                break
            names.add(line[2:].split(":", 1)[0].strip())
    return names


def _default_absences() -> set[str]:
    from tools.run_thesis_once import STAGE_B_ABSENCES
    return set(STAGE_B_ABSENCES)


#: block → (the absences that oblige a refusal, how the answer must refuse)
_CONSENSUS = {"consensus_forward_estimates", "consensus_rating_and_price_target_actions"}
_BASE_RATES = {"reference_class_base_rates"}


def _refusal_problems(block: str, answer: dict, absent: set[str]) -> list[str]:
    problems = []
    if block == "J-09" and absent >= _CONSENSUS:
        position = str(answer.get("consensus_position", ""))
        if not position.startswith("INSUFFICIENT_EVIDENCE"):
            problems.append(f"consensus declared absent but consensus_position = {position[:80]!r}")
    if block == "J-10" and absent >= _BASE_RATES:
        # ★ The cross-company dataset is absent; the company's OWN history is not, and a
        #   base rate taken from it is legitimate. ⇒ The failure is an INVENTED rate: one
        #   marked out-of-bundle that does not say it is absent, or one marked in-bundle
        #   that cites nothing in the bundle.
        for c in answer.get("claims") or []:
            if not isinstance(c, dict):
                continue
            rate, in_bundle = str(c.get("base_rate", "")), c.get("base_rate_in_bundle")
            if in_bundle is False and "absent" not in rate.lower():
                problems.append(f"base rate not in bundle but not declared absent: {rate[:80]!r}")
            elif in_bundle is True and "FACT [" not in rate:
                problems.append(f"base rate marked in-bundle but cites no FACT: {rate[:80]!r}")
            elif in_bundle not in (True, False):
                problems.append(f"base_rate_in_bundle missing on claim {c.get('claim', '')[:50]!r}")
    return problems


# ── the checker ─────────────────────────────────────────────────────────────

def _source_text(run_dir: pathlib.Path, sector_texts: list[str]) -> str:
    manifest = run_dir / "filing.json"
    fixture = (json.loads(manifest.read_text())["fixture"] if manifest.exists()
               else str(DEFAULT_FILING))
    path = pathlib.Path(fixture)
    path = path if path.is_absolute() else REPO / path
    # ★ A judgement bundle can carry the industry evidence (`E-13`), so a quote may
    #   come from a competitor's document; every sector copy is searched too.
    return _letters_digits(path.read_text(encoding="utf-8") + "\n".join(sector_texts))


def _sector_texts(root: pathlib.Path) -> list[str]:
    out = []
    for copy in sorted(root.glob("*/sector_file.json")):
        from tools.promote_recording import sector_text
        out.append(sector_text(copy))
    return out


def check_call(run: str, call: str, record: dict, source: str,
               default_absent: set[str]) -> list[Violation]:
    request, response = record.get("request") or {}, record.get("response") or {}
    text = response.get("text") or ""
    found: list[Violation] = []

    def flag(rule, detail):
        found.append(Violation(run, call, rule, detail))

    if (response.get("stop_reason") or "").lower() == "max_tokens" or not text.strip():
        flag(INCOMPLETE_CALL, f"stop_reason={response.get('stop_reason')!r}, "
                              f"{len(text)} chars")
        return found
    try:
        answer = json.loads(text)
    except ValueError:
        answer = text
    strings = list(_strings(answer))

    for s in strings:
        if _TOOL_MARKUP.search(s):
            flag(LEAKED_TOOL_SYNTAX, s[max(0, _TOOL_MARKUP.search(s).start() - 10):][:80])
            break

    if call.startswith("judge:"):
        missing = []
        for s in strings:
            for tag, quote in _FACT_QUOTE.findall(s):
                if _NOT_THE_FILING.search(tag.strip()):
                    continue
                pieces = [p for p in _ABRIDGED.split(quote)
                          if len(_letters_digits(p)) >= _MIN_PIECE]
                missing += [f"[{tag[:30]}] {p.strip()[:100]!r}" for p in pieces
                            if _letters_digits(p) not in source]
        if missing:
            flag(QUOTE_NOT_IN_SOURCE, f"{len(set(missing))} piece(s), first: {sorted(set(missing))[0]}")

        block = re.search(r"J-\d\d", call)
        if block and isinstance(answer, dict):
            absent = _declared_absences(request)
            for problem in _refusal_problems(block[0], answer,
                                             default_absent if absent is None else absent):
                flag(ABSENT_INPUT_NOT_REFUSED, problem)
    return found


def check_root(root: str | pathlib.Path = RECORDINGS) -> list[Violation]:
    """Every rule, over every recorded call under `root`."""
    root = pathlib.Path(root)
    sectors = _sector_texts(root)
    default_absent = _default_absences()
    out: list[Violation] = []
    for run_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        payloads = sorted((run_dir / "trace/payloads").glob("*.json"))
        if not payloads:
            continue
        source = _source_text(run_dir, sectors)
        for payload in payloads:
            record = json.loads(payload.read_text(encoding="utf-8"))
            out += check_call(run_dir.name, payload.stem, record, source, default_absent)
    return sorted(out)


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1]) if len(argv) > 1 else RECORDINGS
    violations = check_root(root)
    calls = sum(1 for _ in root.glob("*/trace/payloads/*.json"))
    print(f"  rule checks over {calls} recorded call(s) in {root}")
    new = 0
    for v in violations:
        known = KNOWN.get((v.run, v.call, v.rule))
        new += known is None
        print(f"  {'known' if known else '⛔ NEW'}  {v.rule:26} {v.run[-24:]}  {v.call}")
        print(f"         {known or v.detail}")
    print(f"\n  ── {len(violations)} violation(s): {len(violations) - new} known, {new} new")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
