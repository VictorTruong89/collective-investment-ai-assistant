"""D-01 §10 — `check_invalidation`. RA-39/RA-40/RA-41/RA-42.

★ **RA-39 is the deliberate exception to RA-18.** Invalidation checking *sees*
the prior thesis and its falsifiers, because **re-checking is a different task
from re-deciding**. RA-18's blindness protects the authoring call; applying it
here would leave nothing to check against.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from src.fundamental.invalidation.models import (
    TIER_CHEAP, InvalidationCheck, InvalidationEvent, NewEvidenceItem, Triage,
)


def _as_of_instant(as_of: date) -> datetime:
    """The thesis `as_of` as an instant, so RA-40's comparison is total."""
    return datetime.combine(as_of, time.max, tzinfo=timezone.utc)


def new_evidence_only(items, *, thesis_as_of: date):
    """RA-40 — split the feed into what is new and what was already read.

    ⚠ *Re-reading old evidence produces drift, not information.* An item
    knowable **on or before** the thesis's `as_of` was available to the
    authoring call, so re-reading it is not monitoring — it is re-deciding with
    the same inputs and a different sample.
    """
    cut = _as_of_instant(thesis_as_of)
    fresh, known = [], []
    for item in items:
        (fresh if item.knowable_at > cut else known).append(item)
    return fresh, known


def check_invalidation(thesis, items, *, triage, as_of: date | None = None,
                       tier: str = TIER_CHEAP) -> InvalidationCheck:
    """The daily check. `triage` is the cheap-tier judgement (RA-42), injected.

    ★ The LLM never reaches this module: `triage` is a callable, so the gateway
    stays behind `prompts/call.py` (ST-5) and the whole control flow here is
    deterministic and testable without a network.
    """
    as_of = as_of or date.today()
    fresh, known = new_evidence_only(items, thesis_as_of=thesis.as_of)
    by_ordinal = {f.ordinal: f for f in thesis.falsifiers}

    events, escalated = [], []
    for item in fresh:
        result: Triage = triage(thesis, item)
        if result.escalate:
            escalated.append(item.ref)
        if not result.flagged:
            continue
        ordinal = result.falsifier_ordinal
        falsifier = by_ordinal.get(ordinal)
        if falsifier is None:
            from src.fundamental.errors import ResearchError
            raise ResearchError(
                f"{thesis.ticker}: triage flagged falsifier {ordinal!r}, which "
                f"this thesis version does not state. A condition that was never "
                f"written cannot have fired (RA-35, RA-41)"
            )
        events.append(InvalidationEvent(
            ticker=thesis.ticker,
            thesis_version=thesis.thesis_version,
            falsifier_ordinal=falsifier.ordinal,
            condition=falsifier.condition,
            materiality=falsifier.materiality,
            occurred_at=item.knowable_at,
            evidence_ref=item.ref,
            tier=tier,
        ))

    return InvalidationCheck(
        ticker=thesis.ticker, thesis_version=thesis.thesis_version, as_of=as_of,
        events=tuple(events),
        considered=tuple(i.ref for i in fresh),
        skipped_already_known=tuple(i.ref for i in known),
        escalated=tuple(escalated),
    )
