"""F5 `CT-5.2` / `D2` — golden cases, and who is allowed to establish one.

⚠⚠ **`D2`: the fund manager establishes every golden value. Never the system.**

The tempting alternative — seeding the golden set from the pipeline's own best
output — produces *more cases* and a *permanently green suite*, while certifying
the system against itself. Any regression then becomes the new gold, silently.
★ It is rejected here in code, not merely in prose, because it is the option that
looks better.

⚠ For `kind == "thesis"` the correct answer is a **judgement**, not ground truth.
The case records **whose judgement it was**; it does not pretend to objectivity.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Kind = Literal["extraction", "thesis", "ranking"]

#: ⚠ `DX-28` — the date a case was established. A template blank is not a date.
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

#: `D2` — names that may NOT appear in `established_by`. A golden value traceable
#: to the pipeline is circular no matter how it is worded.
FORBIDDEN_ESTABLISHERS = (
    "pipeline", "system", "model", "llm", "claude", "gpt", "agent",
    "src.", "auto", "generated", "gateway",
)

#: `DX-38` — tokens that are a BLANK WAITING TO BE FILLED, not a name.
#: ⚠ Deliberately short and exact-match-only: this list must never grow into a
#: guess about whether a real name looks real. It catches the states a TEMPLATE
#: produces, and nothing else.
PLACEHOLDER_ESTABLISHERS = frozenset({
    "tbd", "todo", "pending", "unknown", "n/a", "na", "none", "null",
    "xxx", "fixme", "anon", "anonymous", "me", "self",
})


def _is_placeholder(name: str) -> bool:
    """★ Does `established_by` name a PERSON, or is it a blank (`AC-5.1`)?

    Two tests, and deliberately no third:

    1. **no letters at all** — `'____'`, `'---'`, `'???'`, `'...'`. ⚠ This is
       the one that mattered: it is the shape every template blank in this repo
       actually takes, and it is unambiguous — nothing that names a person is
       written without a single letter.
    2. **an exact placeholder word** — `'TBD'`, `'pending'`.

    ⚠⚠ There is deliberately no *"does this look like a real name?"* step. Names
    are one-word, hyphenated, non-Latin and initialled; a heuristic that judges
    them would reject real fund managers, and `P5` says fail loud — not fail
    clever. ★ The job here is to refuse a BLANK, not to authenticate a person.
    """
    stripped = name.strip()
    if not any(ch.isalpha() for ch in stripped):
        return True
    return stripped.lower().strip(".") in PLACEHOLDER_ESTABLISHERS


#: ⚠ `thesis` answers are judgements. Stated so a reader cannot mistake the
#: golden set for ground truth on the most expensive output in the system.
JUDGEMENT_KINDS = ("thesis",)


class CircularGoldenValue(Exception):
    """`D2` — a golden value the system itself produced.

    ⚠ This is the failure mode that produces a green suite forever: the harness
    certifies the system against its own past output, so a regression becomes the
    new expected value and nothing ever reds.
    """


@dataclass(frozen=True, slots=True)
class GoldenCase:
    """`CT-5.2`. ⚠ `source` is required — an unrecorded derivation gets trusted
    for the wrong reason eventually."""

    case_id: str
    kind: Kind
    input_ref: str
    expected: object
    source: str
    established_at: str
    established_by: str

    def __post_init__(self) -> None:
        if not self.case_id or not self.input_ref:
            raise ValueError("case_id and input_ref are required")
        if not self.source.strip():
            raise ValueError(
                f"{self.case_id}: `source` is required (CT-5.2) — a golden value "
                "whose derivation is unrecorded cannot be re-checked, and will "
                "eventually be trusted for the wrong reason"
            )
        if not self.established_by.strip():
            raise ValueError(f"{self.case_id}: established_by is required (D2)")
        if _is_placeholder(self.established_by):
            # ⚠⚠ DX-38. `DX-28` fixed EXACTLY this for `established_at` and left
            # its twin open ONE LINE ABOVE: the empty-string check passes any
            # non-empty text, so the template's own blank — `____` — validated.
            # ★ Measured: 3 of 8 prepared cases carried `established_by: '____'`
            # with a real `established_at`, and every one of them constructed
            # cleanly. Two of the three were the cases pinning `DX-33` and
            # `DX-35` — so the fixes would have graded as established by nobody.
            # ★★★ `AC-5.1` says established_by names **a person**. A placeholder
            # names neither a person nor a pipeline component, so `D2`'s
            # circularity check could never catch it — it is not circular, it is
            # UNATTRIBUTED, and that is a second way for an unestablished value
            # to grade as gold.
            raise ValueError(
                f"{self.case_id}: established_by is {self.established_by!r}, "
                "which names nobody. ⚠ AC-5.1 requires a PERSON — a case that "
                "grades a value nobody signed for is unestablished, however "
                "complete the template looks (D2, DX-38)."
            )
        if not _ISO_DATE.match(self.established_at or ""):
            # ⚠⚠ DX-28. Eight cases were signed with a real name and the
            # placeholder date `____-__-__` still in place, and **nothing
            # objected** — the set reported "10 established" when 8 were half
            # done. ★ A blank left in a template is exactly the state a
            # signature is supposed to end, so the field that records WHEN must
            # refuse a blank as firmly as the field that records WHO.
            # ★★ Same family as DX-20: a placeholder that validates is a
            #    placeholder that ships.
            raise ValueError(
                f"{self.case_id}: established_at is {self.established_at!r}, not "
                "an ISO date (YYYY-MM-DD). ⚠ A case carrying a name but no date "
                "is half-signed — and a golden value nobody can date is one "
                "nobody can audit against the filing as it stood (D2)"
            )
        if self.expected is None:
            # ⚠⚠ DX-20. An `expected` left empty is a case the fund manager has
            # not finished establishing — the state every case passes through
            # while the filing is still open on the desk. It did not merely
            # load: `run_regression` compares with `==`, so any run producing
            # nothing (extraction NOT_FOUND, a stub, a failed call) matched
            # `None` and the case reported **PASS**.
            # ★ Every other check here guards a value that is WRONG. This one
            #   guards a value that was never established at all — and it is the
            #   only one whose failure mode is GREEN.
            raise ValueError(
                f"{self.case_id}: `expected` is empty (CT-5.2, DX-20) — an "
                "unestablished case must not load: it would PASS whenever the "
                "system produces nothing. ★ If the document genuinely does not "
                "state the figure, say so explicitly (e.g. "
                "`expected: {status: NOT_FOUND}`) — 'the document does not say' "
                "is a finding; 'I have not looked yet' is not."
            )
        low = f"{self.established_by} {self.source}".lower()
        for bad in FORBIDDEN_ESTABLISHERS:
            if bad in low:
                raise CircularGoldenValue(
                    f"{self.case_id}: established_by/source names {bad!r}. ⚠ D2 — the "
                    "fund manager establishes golden values; a value the system "
                    "produced would certify the system against itself, and every "
                    "regression would become the new gold."
                )

    @property
    def is_judgement(self) -> bool:
        """⚠ True for `thesis` — the expected value is an opinion, recorded as one."""
        return self.kind in JUDGEMENT_KINDS
