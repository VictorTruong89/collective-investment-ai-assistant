"""D-09 Reporting — render, deliver, originate nothing. SEAT-5 · LEVEL 1.

```
"Put it on one screen without making it look more certain than it is."

D-09 is the ONLY place in this system where a machine's output becomes a
human decision. Everything upstream is measured, gated and reconciled. Here
it is READ — and a reader applies heuristics none of those guarantees survive.
```

⚠ **D-09 writes to nothing** (RP-30, ST-9) — not the book, not the journal, not
a producing domain's store. That is structural: *a renderer that can mutate the
book can rewrite history to match what it printed.*
"""

from src.reporting.deliver.archive import assert_content_equivalent
from src.reporting.deliver.email import (
    Delivery, archive, build_message, deliver, delivery_id, digest, send,
)
from src.reporting.deliver.html import assert_self_contained, render_html
from src.reporting.deliver.markdown import render_markdown
from src.reporting.errors import (
    ArchiveMismatchError, BareConfidenceError, DeliveryFailedError, ExternalRefError,
    ForecastVoiceError, FreshnessUnstatedError, NoProducerError, RenderingsDivergedError,
    ReportingError, ScriptPresentError, StabilityMissingError, UntaggedClassError,
    VerdictEscalatedError,
)
from src.reporting.render.card import DisciplineCard, build_card
from src.reporting.render.classes import (
    CLASSES, COMPUTATION, FACT, JUDGEMENT, KNOWN_DEFECTS, RenderUnit,
)
from src.reporting.render.lint import LintReport, enforce, lint

__all__ = [
    "ArchiveMismatchError", "BareConfidenceError", "CLASSES", "COMPUTATION",
    "Delivery", "DeliveryFailedError", "DisciplineCard", "ExternalRefError", "FACT",
    "ForecastVoiceError", "FreshnessUnstatedError", "JUDGEMENT", "KNOWN_DEFECTS",
    "LintReport", "NoProducerError", "RenderUnit", "RenderingsDivergedError",
    "ReportingError", "ScriptPresentError", "StabilityMissingError",
    "UntaggedClassError", "VerdictEscalatedError", "archive",
    "assert_content_equivalent", "assert_self_contained", "build_card",
    "build_message", "deliver", "delivery_id", "digest", "enforce", "lint",
    "render_html", "render_markdown", "send",
]
