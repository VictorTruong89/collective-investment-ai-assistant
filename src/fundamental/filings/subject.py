"""`DX-97` — the SUBJECT guard: an item about another company may not name the registrant.

★★★ **What `X-01` cannot see.** `X-01` proves a value is in its quote and the
quote is in the document. It cannot prove the value answers the question the
item asks. Every block before `E-13` asked about the registrant, so the gap never
bit; `E-13` asks about COMPETITORS, and its first live run returned the
registrant's own fabs — 37 items, all verified, all wrong.

★ `AP-5` — *"is this competitor the company itself?"* is a comparison against
the filing's own cover page, so it is code, not a prompt instruction.

⚠ Deliberately narrow. It catches the measured failure (the registrant named as
its own competitor) and does not pretend to judge whether a named rival is
really a rival — that stays `J-08`'s question.
"""

from __future__ import annotations

import re

from src.fundamental.errors import SubjectIsRegistrantError

#: Items whose value must name a company OTHER than the registrant.
OTHER_COMPANY_ITEMS = ("cx.competitor",)

_COVER_MARKER = "(Exact name of registrant as specified in its charter)"
_SUFFIXES = {"inc", "incorporated", "corp", "corporation", "co", "company",
             "ltd", "limited", "plc", "llc", "lp", "sa", "ag", "nv", "the"}
#: How a filing refers to its own registrant in running text.
_SELF_REFERENCES = {"we", "us", "our", "the company", "the registrant"}


def registrant_name(filing_text: str) -> str:
    """The registrant as the 10-K/10-Q cover page states it — the line above
    the SEC's fixed caption. ⚠ Refuses rather than guessing (`P5`)."""
    lines = filing_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == _COVER_MARKER:
            name = next((ln.strip() for ln in reversed(lines[:i]) if ln.strip()), "")
            if name:
                return name
    raise SubjectIsRegistrantError(
        "the filing has no cover-page registrant line "
        f"({_COVER_MARKER!r}) — the subject guard cannot tell the registrant "
        "from a competitor, and will not assume (DX-97, P5)")


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def names_registrant(value: str, registrant: str, ticker: str) -> bool:
    """True when `value` refers to the registrant.

    ★ Matches: the registrant's name without corporate suffixes appearing in
    the value (`"Micron Technology"`), the name's first word standing alone
    (`"Micron"`), the ticker as a word (`"MU"`), or a self-reference (`"we"`).
    """
    words = _words(value)
    core = [w for w in _words(registrant) if w not in _SUFFIXES]
    if not words or not core:
        return False
    joined, core_joined = " ".join(words), " ".join(core)
    return (f" {core_joined} " in f" {joined} "
            or words == core[:1]
            or ticker.casefold() in words
            or joined in _SELF_REFERENCES)


def assert_subject_is_not_registrant(results, bundle) -> None:
    """Refuse any extraction result whose other-company item names the registrant.

    ⚠ Checked only when such an item was FOUND; a bundle with no cover page is
    refused only then — a block that never names another company needs no
    registrant to be checked against.
    """
    for result in results:
        suspects = [i for i in result.items
                    if i.evidence_id in OTHER_COMPANY_ITEMS and i.status == "found"]
        if not suspects:
            continue
        filings = bundle.of_kind("filing")
        if not filings:
            raise SubjectIsRegistrantError(
                f"{result.block_id}: names other companies but the bundle has no "
                f"filing to read the registrant from (DX-97, P5)")
        registrant = registrant_name(filings[0].content)
        hits = [i for i in suspects
                if names_registrant(i.value, registrant, bundle.ticker)]
        if hits:
            raise SubjectIsRegistrantError(
                f"{result.block_id}: {len(hits)} of {len(suspects)} "
                f"{OTHER_COMPANY_ITEMS[0]} item(s) name the registrant "
                f"{registrant!r} (e.g. {hits[0].value!r}). ⛔ DX-97 — X-01 passed "
                f"them because the words ARE in the filing; they do not answer "
                f"the question. The whole result is refused: its capacity rows "
                f"are the registrant's own.")
