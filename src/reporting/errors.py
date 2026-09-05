"""D-09 error family — §14's catalog (L4 §5.3)."""

from __future__ import annotations

from src.shared.errors import PipelineError


class ReportingError(PipelineError):
    code = "RPT.UNSPECIFIED"
    retryable = False


class UntaggedClassError(ReportingError):
    """RPT.CLASS.UNTAGGED — a rendered value with no reliability class (RP-1).

    ```
    "Position: 220 sh @ $91.40"   is a RECONCILED FACT.
    "Fair value: $412.80"         is a COMPUTATION — whose DCF has a live defect.
    "Conviction: Medium-High"     is one draw from a stochastic process.

    A reader who cannot tell them apart will size the position off the least
    reliable one, because it is the one written in prose.
    ```
    """

    code = "RPT.CLASS.UNTAGGED"


class FreshnessUnstatedError(ReportingError):
    """RPT.FRESHNESS.UNSTATED — a component with no `as_of` (RP-2).

    ★ **Freshness is per component, never per card.** The thesis may be days old,
    the price is live, the book is from the last export — one clock would be
    wrong for at least two of them.
    """

    code = "RPT.FRESHNESS.UNSTATED"


class NoProducerError(ReportingError):
    """RPT.INPUT.NO_PRODUCER — a card field with no producing domain (RP-6, DC-1).

    ⚠ **A field D-09 could compute itself is a field D-09 must not compute.**
    """

    code = "RPT.INPUT.NO_PRODUCER"


class VerdictEscalatedError(ReportingError):
    """RPT.VERDICT.ESCALATED — rendering would make a verdict more aggressive (RP-7, DC-5)."""

    code = "RPT.VERDICT.ESCALATED"


class StabilityMissingError(ReportingError):
    """RPT.STABILITY.MISSING — a verdict on the ACTIONABLE path with no stability (RP-13).

    ★ **Scoped to the actionable path, and that scoping is what makes L3 BS-33
    work.** B3's card carries a stub gate with no stability; it is rendered as
    `actionable: false`, so this does not fire — and the first actionable card is
    B4.5's, which is exactly where BS-28 put it.
    """

    code = "RPT.STABILITY.MISSING"


class BareConfidenceError(ReportingError):
    """RPT.CONFIDENCE.BARE — a confidence number with no referent (RP-14, RA-21)."""

    code = "RPT.CONFIDENCE.BARE"


class ForecastVoiceError(ReportingError):
    """RPT.LINT.FORECAST_VOICE — unearned-certainty language. ★ BLOCKS the render.

    Deterministic, cheap, and it removes the cheapest source of unearned
    certainty (RP-18, RA-26).
    """

    code = "RPT.LINT.FORECAST_VOICE"

    def __init__(self, hits) -> None:
        super().__init__(
            f"forecast-voice violations block the render: {sorted(hits)}. These words "
            f"assert certainty the analysis does not have, and removing them costs "
            f"nothing analytical (RP-18)"
        )


class ExternalRefError(ReportingError):
    """RPT.RENDER.EXTERNAL_REF — the HTML fetches something. Breaks P6 (RP-31).

    ⚠ **An artifact that needs a live server to render is not viewable later,
    and "later" is exactly when a decision gets audited.**
    """

    code = "RPT.RENDER.EXTERNAL_REF"


class ScriptPresentError(ReportingError):
    """RPT.RENDER.SCRIPT — the HTML rendering contains script (RP-34)."""

    code = "RPT.RENDER.SCRIPT"


class RenderingsDivergedError(ReportingError):
    """RPT.RENDER.DIVERGENT — two renderings of one artifact differ in CONTENT (RP-32)."""

    code = "RPT.RENDER.DIVERGENT"


class DeliveryFailedError(ReportingError):
    """RPT.DELIVER.FAILED — send failed. ★ Loud, never a quiet log line (RP-23)."""

    code = "RPT.DELIVER.FAILED"
    retryable = True          # transport; D-08 owns the retry (EH-14, EH-15)


class ArchiveMismatchError(ReportingError):
    """RPT.ARCHIVE.MISMATCH — archived bytes != delivered bytes (RP-24).

    If they can differ, the archive is not evidence of what was seen.
    """

    code = "RPT.ARCHIVE.MISMATCH"
