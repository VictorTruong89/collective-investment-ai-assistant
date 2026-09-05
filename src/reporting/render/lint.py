"""Forecast-voice, length and uncited-claim checks — §8 (RP-18, RP-19, RA-26).

★ **A lint violation BLOCKS the render.** Deterministic, cheap, and it removes
the cheapest source of unearned certainty: *"will"*, *"is set to"*, *"poised
to"*, *"clearly"*, *"undoubtedly"* all assert a confidence the analysis does not
have, and none of them costs anything analytical to remove.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


from src.reporting.errors import ForecastVoiceError

#: ★★ **RA-137 — D-01 DECLARES these; D-09 EXECUTES them.**
#:
#: ⚠ They used to be restated here, which is **FE-4's defect in another domain**:
#: *the second definition is always the one nobody tests.* And the two
#: enforcement points differ in consequence — **X-03 fails the run** (D-01,
#: §4A.2 step 9) and **RP-18 blocks the render** (here) — so a list that drifted
#: between them would make which one fires depend on which copy was edited.
#:
#: `L1-reporting.md` §8 states the ownership: these obligations are *"D-01's to
#: satisfy in CONTENT and D-09's to satisfy in RENDERING"*, and §3 already
#: declares D-09 depends on D-01.
from src.fundamental.monitor.lint import FORECAST_VOICE, LENGTH_CAPS


@dataclass(frozen=True, slots=True)
class LintReport:
    forecast_voice: tuple[str, ...]
    over_length: tuple[tuple[str, int, int], ...]

    @property
    def blocking(self) -> bool:
        """⚠ Only forecast voice blocks. Length is a WARNING (RPT.LINT.LENGTH)."""
        return bool(self.forecast_voice)


def lint(sections: dict) -> LintReport:
    """Check every narrative section. `sections` maps a name to its text."""
    hits: list[str] = []
    over: list[tuple[str, int, int]] = []
    for name, text in sorted(sections.items()):
        if not text:
            continue
        for phrase in FORECAST_VOICE:
            if re.search(rf"\b{re.escape(phrase)}\b", text, re.I):
                hits.append(f"{name}: {phrase!r}")
        cap = LENGTH_CAPS.get(name)
        if cap is not None and len(text) > cap:
            over.append((name, len(text), cap))
    return LintReport(tuple(sorted(hits)), tuple(over))


def enforce(sections: dict) -> LintReport:
    """Lint and raise on a blocking violation (AC-9.20 — zero in output)."""
    report = lint(sections)
    if report.blocking:
        raise ForecastVoiceError(report.forecast_voice)
    return report
