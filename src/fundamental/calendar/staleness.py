"""D-01 §10A.2 — `staleness`. RA-71, RA-72, RA-139, RA-43.

★★ **RA-43 is a timer, and a timer is the wrong instrument.** A thesis is not
stale because forty-eight hours elapsed. It is stale because **a scheduled event
bearing on it has occurred and has not been read** — so the clock survives only
as a floor for names with no events in the window.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from src.fundamental.calendar.models import (
    SCOPE_BOOK, CalendarEvent, StalenessState,
)

#: L0 §config — RA-43's floor, unchanged. Now the *secondary* test.
STALENESS_FILINGS_HOURS = 48

#: L0 §config — RA-72/RA-139. Ten CALENDAR days: wide enough to catch RA-72's
#: own case (*"conviction High, written four days before results"*) and narrow
#: enough against a ~91-day reporting cycle that it still marks something.
PRE_EVENT_WINDOW_DAYS = 10

#: The classes a thesis is taken to depend on when the caller names none.
#: ★ Any thesis with a business falsifier is read by a quarterly result — that
#: is what a business falsifier *is*. Macro classes are never inferred: a thesis
#: depends on CPI only if it says so.
_DEFAULT_CLASSES = frozenset({"earnings"})


def depended_classes(thesis, *, extra=()) -> frozenset:
    """Which event classes bear on this thesis (RA-71's *"a class it depends on"*).

    ⚠ Deliberately conservative in one direction only: it never *narrows* below
    `earnings` for a thesis that states a business falsifier, because a missed
    dependency shows up as a thesis silently trusted past its own test.
    """
    classes = set(extra)
    if any(f.about_business for f in thesis.falsifiers):
        classes |= _DEFAULT_CLASSES
    for falsifier in thesis.falsifiers:
        head = falsifier.observable_field.split(".", 1)[0].casefold()
        if head in ("fomc", "cpi", "pce", "payrolls", "macro"):
            classes.add(head)
    return frozenset(classes)


def _relevant(event: CalendarEvent, thesis, classes) -> bool:
    if event.event_class not in classes:
        return False
    return event.scope == SCOPE_BOOK or event.ticker == thesis.ticker


def staleness(thesis, as_of: date, *, events=(), last_check_at: datetime | None = None,
              depends_on=()) -> StalenessState:
    """RA-71 — event-relative first, clock-relative second.

    `last_check_at` is the most recent **invalidation check** against this
    thesis, not the most recent run of anything.
    """
    classes = depended_classes(thesis, extra=depends_on)
    relevant = [e for e in events if _relevant(e, thesis, classes)]

    # ── RA-72/RA-139: provisional, not stale. Computed first because it is
    #    about the *next* event and survives whatever the staleness test says.
    pre_event, pre_date, pre_class = False, None, ""
    for event in sorted(relevant, key=lambda e: e.scheduled_date):
        if event.scheduled_date < as_of:
            continue
        lead = (event.scheduled_date - thesis.as_of).days
        if 0 <= lead <= PRE_EVENT_WINDOW_DAYS:
            pre_event, pre_date, pre_class = True, event.scheduled_date, event.event_class
            break

    # ── RA-71, the primary test: has a depended event OCCURRED and not been read?
    check_cut = last_check_at or _instant(thesis.as_of)
    for event in sorted(relevant, key=lambda e: e.scheduled_date, reverse=True):
        if event.scheduled_date >= as_of:
            continue                       # not yet occurred
        if event.scheduled_date > thesis.as_of and _instant(event.scheduled_date) > check_cut:
            return StalenessState(
                stale=True, basis="event", driving_event=event,
                reason=(f"{event.event_class} on {event.render_date()} occurred "
                        f"after the thesis and has not been read (RA-71)"),
                pre_event=pre_event, pre_event_date=pre_date, pre_event_class=pre_class,
            )

    # ── RA-43, the floor: names with no events in the window still go stale.
    if last_check_at is not None:
        age = _instant(as_of) - last_check_at
        if age > timedelta(hours=STALENESS_FILINGS_HOURS):
            return StalenessState(
                stale=True, basis="clock",
                reason=(f"no invalidation check in {age.total_seconds() / 3600:.0f}h "
                        f"(floor {STALENESS_FILINGS_HOURS}h, RA-43)"),
                pre_event=pre_event, pre_event_date=pre_date, pre_event_class=pre_class,
            )

    return StalenessState(
        stale=False, basis="fresh",
        reason="no depended event occurred unread; inside the clock floor",
        pre_event=pre_event, pre_event_date=pre_date, pre_event_class=pre_class,
    )


def _instant(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
