"""X-03 / X-04 — the forecast-voice wordlist and the length caps (RA-26, RA-27).

★★ **RA-137: this is the ONE declaration, and D-09 executes it.** ⚠ *Added
2026-08-23: RA-26/RA-27 are **D-01's** rules — `L1-reporting.md` §8 says these
obligations are "D-01's to satisfy in CONTENT and D-09's to satisfy in
RENDERING" — but **neither spec said where the list lives**, and it was
implemented only in D-09.*

```
TWO DETERMINISTIC IMPLEMENTATIONS OF ONE WORDLIST IS FE-4's DEFECT IN ANOTHER
DOMAIN — "the second definition is always the one nobody tests".

And here the two enforcement points differ in CONSEQUENCE:
   X-03  (D-01, §4A.2 step 9)   non-zero ⇒ FAILS THE RUN
   RP-18 (D-09, at render)      a violation ⇒ BLOCKS THE RENDER

A list that drifts between them makes which one fires depend on which copy
was edited.
```

★ **Deterministic — no LLM** (§1.4). *An LLM asked "does this number appear in
this span" is strictly worse than `in`*, and the same holds for a wordlist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: RA-26's list. ⚠ Word-boundary matched, so "willing" and "clearance" do not
#: fire — **a lint with false positives is a lint that gets disabled** (IM-2).
FORECAST_VOICE = (
    "will", "is set to", "are set to", "poised to", "clearly", "undoubtedly",
    "certainly", "guaranteed", "inevitably", "obviously", "no doubt", "surely",
)

#: RA-27 — *length is a free confidence signal; capping removes it and costs
#: nothing analytical.* ⚠ **ADMITTED GUESSES** (CN-10) except where a J-block
#: states its own cap, which these mirror: J-02 400 words, J-11 500 words.
LENGTH_CAPS = {
    "thesis": 600, "bear_case": 600, "falsifier": 300, "reason": 400,
    "business_model": 2600,      # J-02's 400-word cap, in characters
    "pre_mortem": 3200,
}


@dataclass(frozen=True, slots=True)
class LintFinding:
    section: str
    phrase: str

    def __str__(self) -> str:
        return f"{self.section}: {self.phrase!r}"


def forecast_voice_violations(sections: dict) -> tuple[LintFinding, ...]:
    """X-03 — every unearned-certainty phrase, with the section it was in.

    ⚠ Returns findings rather than a boolean: **RM-15 counts them**, and
    *"should be zero — non-zero is a regression, not a style question"* needs the
    count, not a flag.
    """
    out = []
    for name, text in sorted(sections.items()):
        if not text:
            continue
        for phrase in FORECAST_VOICE:
            if re.search(rf"\b{re.escape(phrase)}\b", text, re.I):
                out.append(LintFinding(name, phrase))
    return tuple(out)


def length_violations(sections: dict) -> tuple[tuple[str, int, int], ...]:
    """X-04 — `(section, length, cap)` for each section over its cap.

    ⚠ **A WARNING, not a block** (`RPT.LINT.LENGTH`). Length is a soft signal;
    certainty language is a claim.
    """
    out = []
    for name, text in sorted(sections.items()):
        cap = LENGTH_CAPS.get(name)
        if cap is not None and text and len(text) > cap:
            out.append((name, len(text), cap))
    return tuple(out)
