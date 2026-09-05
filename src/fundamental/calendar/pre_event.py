"""D-01 §10A.3 — the pre-event brief. RA-73…RA-77.

★ **Pre-commitment, dated.** Written before the event, hashed before it, and
immutable from it onward — *a brief editable post-event is a memory of what we
would have said* (RA-73).
"""

from __future__ import annotations

import re
from datetime import date, datetime

from src.fundamental.calendar.models import (
    SCOPE_BOOK, SCOPE_TICKER, CalendarEvent, OutcomeMapping, PreEventBrief,
)
from src.fundamental.errors import BriefMutatedError, BriefPredictsError
from src.fundamental.monitor.lint import FORECAST_VOICE

#: RA-74 — phrases that state an *expected result* rather than mapping outcomes.
#: ★ Distinct from `FORECAST_VOICE` (RA-26), which is about unearned certainty
#: anywhere; these are about a **prediction of this event's number**, which is
#: the specific defect a brief can carry.
PREDICTION_MARKERS = (
    "we expect", "i expect", "expected to come in", "should come in",
    "our estimate", "we forecast", "we anticipate", "consensus is",
    "likely to report", "should beat", "should miss", "we think it will",
)


def _prediction_findings(text: str) -> tuple[str, ...]:
    low = text or ""
    hits = [m for m in PREDICTION_MARKERS if m in low.casefold()]
    hits += [p for p in FORECAST_VOICE
             if re.search(rf"\b{re.escape(p)}\b", low, re.I)]
    return tuple(dict.fromkeys(hits))


def brief_targets(theses, events) -> tuple[tuple, ...]:
    """RA-76/RA-77 — who gets a brief, and how many.

    ★ Briefs are written for names with a **live thesis**, never the universe:
    *a brief nobody will read is cost with no reader*, and that is what keeps
    the calendar's cost near zero. ⚠ RA-77 collapses macro and FOMC to **one**
    book-level brief — *thirteen near-identical CPI briefs is one macro
    narrative given thirteen independent chances to leak into thirteen theses*.
    """
    live = {t.ticker: t for t in theses}
    targets, seen_book = [], set()
    for event in events:
        if event.scope == SCOPE_BOOK:
            key = (event.event_class, event.scheduled_date)
            if key in seen_book:
                continue
            seen_book.add(key)
            targets.append((None, event))
            continue
        thesis = live.get(event.ticker)
        if thesis is None:
            continue                     # RA-76 — no live thesis, no brief
        targets.append((thesis, event))
    return tuple(targets)


def pre_event_brief(thesis, event: CalendarEvent, *, outcome_map,
                    will_not_tell_you, authored_at: datetime,
                    brief_id: str = "") -> PreEventBrief:
    """Write and hash the brief. RA-73/RA-74/RA-75, all three checked here.

    ⚠ The hash is computed **now**, before the event, because it is the only
    moment at which it means anything.
    """
    if authored_at.date() >= event.scheduled_date:
        raise BriefMutatedError(brief_id or "<new>", event.scheduled_date,
                                authored_at)

    mapping = tuple(outcome_map)
    if not mapping:
        raise BriefPredictsError(
            brief_id or "<new>",
            "maps no outcome to any falsifier state — a brief with no mapping "
            "is a note about an upcoming date",
        )

    # ── RA-75: mandatory, and non-empty. The limit is free to name only now.
    limits = tuple(s for s in (will_not_tell_you or ()) if s and s.strip())
    if not limits:
        from src.fundamental.errors import ResearchError
        raise ResearchError(
            f"pre-event brief {brief_id or '<new>'!r}: 'what this event will "
            f"NOT tell you' is empty. ★ A quarterly result is over-read by "
            f"default, and naming the limit is free only before the number "
            f"exists (RA-75)"
        )

    # ── RA-74: the brief predicts nothing.
    for text in [o.outcome for o in mapping] + list(limits):
        hits = _prediction_findings(text)
        if hits:
            raise BriefPredictsError(
                brief_id or "<new>",
                f"states an expected result ({hits[0]!r}) — the brief maps "
                f"outcomes to falsifier states, it does not pick one",
            )

    scope = SCOPE_BOOK if event.scope == SCOPE_BOOK else SCOPE_TICKER
    brief = PreEventBrief(
        brief_id=brief_id or _brief_id(thesis, event),
        event=event, authored_at=authored_at,
        thesis_version=thesis.thesis_version if thesis else 0,
        outcome_map=mapping, will_not_tell_you=limits,
        ticker="" if scope == SCOPE_BOOK else event.ticker, scope=scope,
    )
    from dataclasses import replace
    return replace(brief, brief_hash=brief.compute_hash())


def assert_unedited(original: PreEventBrief, candidate: PreEventBrief, *,
                    now: datetime) -> None:
    """RA-73 / AC-1.45 — editing at or after the event raises.

    ★ RA-36's rule applied to a different artifact: **superseded, never edited.**
    """
    if candidate.compute_hash() == original.brief_hash:
        return
    if now.date() >= original.event.scheduled_date:
        raise BriefMutatedError(original.brief_id, original.event.scheduled_date, now)


def _brief_id(thesis, event: CalendarEvent) -> str:
    who = event.ticker or "BOOK"
    return f"{who}:{event.event_class}:{event.scheduled_date.isoformat()}"
