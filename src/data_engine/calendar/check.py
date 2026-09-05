"""§6A — the pre-run corporate-action gate (DE-31…DE-36, AC-7.47…7.53).

```
D-07 MUST ENUMERATE CORPORATE ACTIONS FOR THE WHOLE UNIVERSE BEFORE ANY
TRAINING, BACKTEST OR INFERENCE RUN BEGINS — AND HALT THE RUN ON AN
UNHANDLED ONE.

Not per ticker, on demand, when someone remembers.
Not as a report nobody reads.
A precondition, checked once, that can stop the run.
```

★ **Why a gate and not a report.** Point-in-time resolution is necessary and not
sufficient: every value §6 serves can be perfectly as-of correct while the
*series it belongs to* was silently redefined mid-window. A model trained across
such a window is not wrong at any single point — it is trained on a series whose
units changed partway through, and nothing in the data says so.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

from src.data_engine.contracts.envelopes import (
    BLOCK, CalendarCheckReport, Finding, HALT,
)
from src.data_engine.calendar.classes import (
    BY_NAME, CHECKED, EVENT_CLASSES, NEWS_DEPTH_DAYS, unchecked,
)
from src.data_engine.errors import CheckMissingError, UnhandledBlockError
from src.data_engine.pit.models import utcnow


@dataclass(frozen=True, slots=True)
class ClassResult:
    """One class's answer: a status and whatever it found.

    ⚠ The status is NOT derivable from the findings. An empty `findings` with
    status `CHECKED` means "we looked and there were none"; the same empty list
    with an `UNCHECKED:` status means "we could not look". Collapsing the two is
    exactly DE-35, and returning a bare list would make it unavoidable.
    """

    status: str
    findings: tuple[Finding, ...] = ()


class EventFeed(Protocol):
    """The port §6A's gate needs — declared by the CONSUMER (CA-6).

    Named for what the gate needs (a per-class answer over a window), not for
    who implements it. `FMPEventFeed` and `CachedEventFeed` both satisfy it, and
    the gate cannot tell which it has.
    """

    def fetch(self, event_class: str, tickers, start: date, end: date,
              as_of: date) -> ClassResult:
        ...


def calendar_check(
    *, tickers, start: date, end: date, as_of: date, adj_as_of: date | None,
    feed: EventFeed, run_id: str, handled: dict | None = None,
) -> CalendarCheckReport:
    """Run the gate. Raises `UnhandledBlockError` on an unhandled BLOCK (DE-32).

    `tickers` is the **universe**, not the watchlist (DE-36, AC-7.48). A name
    excluded from the actionable slate still participates in cross-sectional
    normalisation, so its unhandled split contaminates every other name's rank.

    `handled` maps `(ticker, class, event_date)` to a recorded handling string.
    A BLOCK may only be cleared by an explicit, recorded handling — never by an
    empty dict entry and never by severity downgrade.
    """
    tickers = sorted({t.upper() for t in tickers})
    handled = handled or {}
    status: dict[str, str] = {}
    findings: list[Finding] = []

    for spec in EVENT_CLASSES:
        if spec.permanently_unchecked:
            status[spec.name] = unchecked(spec.note or "no source")
            continue
        result = feed.fetch(spec.name, tickers, start, end, as_of)
        status[spec.name] = result.status
        for f in result.findings:
            # DE-34 / AC-7.52: the report is keyed on KNOWABILITY, not on the
            # event date. A split announced after as_of is absent even though it
            # is in today's `splits` response — the check is itself PIT.
            if f.knowable_at > as_of:
                continue
            key = (f.ticker, f.event_class, f.event_date)
            how = handled.get(key)
            findings.append(
                Finding(f.ticker, f.event_class, f.severity, f.event_date, f.knowable_at,
                        f.detail, f.source, handled=how is not None, handling=how)
            )

    _assert_every_class_present(status)

    report = CalendarCheckReport(
        run_id=run_id, as_of=as_of, adj_as_of=adj_as_of,
        window_start=start, window_end=end, universe_size=len(tickers),
        class_status=status, findings=tuple(findings), checked_at=utcnow(),
    )
    if report.verdict == HALT:
        # DE-32 / AC-7.49: names the tickers AND the events. A blocking ticker is
        # never silently dropped — dropping is the D-17 defect, where 7 of 13
        # watchlist names were scored on NaNs and nothing said so.
        raise UnhandledBlockError(report.blocked)
    return report


def news_status(start: date, as_of: date) -> str:
    """DE-35 / AC-7.51 — news beyond ~92 days is UNCHECKED, never "no events".

    K-8: `news/stock` returns ~92 days regardless of paging depth, measured
    across three tickers. A window reaching further back is not covered, and a
    covered-looking empty result would be a false negative on every day before
    the horizon.
    """
    horizon = as_of - timedelta(days=NEWS_DEPTH_DAYS)
    if start < horizon:
        return unchecked(
            f"source depth ~{NEWS_DEPTH_DAYS}d; window starts {start} but news is "
            f"only available from {horizon} (K-8, §5C.4)"
        )
    return CHECKED


def price_adjustment_status(panel_adj_as_of, run_adj_as_of, tickers) -> ClassResult:
    """Class 1 — the panel's adjustment must match the run's (DE-28, DE-30).

    Two panels covering the same dates with different `adj_as_of` are different
    data and must not compare equal. Running features from one against a
    decision taken under the other is INV-2 broken across the seam rather than
    inside a module, which is why it is a BLOCK and not a FLAG.
    """
    if panel_adj_as_of == run_adj_as_of:
        return ClassResult(CHECKED)
    return ClassResult(CHECKED, tuple(
        Finding(t, "price_adjustment_state", BLOCK,
                event_date=run_adj_as_of or date.min,
                knowable_at=run_adj_as_of or date.min,
                detail={"panel_adj_as_of": str(panel_adj_as_of),
                        "run_adj_as_of": str(run_adj_as_of)},
                source="derived")
        for t in tickers))


def require_check(report: CalendarCheckReport | None, *, window, what: str) -> CalendarCheckReport:
    """DE-31 / AC-7.47 — feature-building without a check raises.

    ⚠ The window is compared, not merely the presence of a report. A check run
    over January that clears a February run is a check in name only, and it is
    the easy mistake to make once the report becomes a parameter people pass
    around.
    """
    if report is None:
        raise CheckMissingError(what)
    start, end = window
    if report.window_start > start or report.window_end < end:
        raise CheckMissingError(
            f"{what}: the calendar check covers "
            f"{report.window_start}..{report.window_end} but the run needs "
            f"{start}..{end} — a check over a narrower window clears nothing outside it"
        )
    return report


def _assert_every_class_present(status: dict) -> None:
    """CT-7.7 / AC-7.50 — all eighteen appear, or the contract is violated."""
    from src.data_engine.errors import ContractViolationError

    missing = [c.name for c in EVENT_CLASSES if c.name not in status]
    if missing:
        raise ContractViolationError(
            "CT-7.7",
            f"class_status omits {missing}. Every one of the eighteen classes "
            f"appears as CHECKED or UNCHECKED:<why> — a class missing from this map "
            f"is a defect, not an implied pass (DE-35)",
        )
    bad = [k for k, v in status.items()
           if v != CHECKED and not v.startswith("UNCHECKED: ")]
    if bad:
        raise ContractViolationError(
            "CT-7.7",
            f"class_status values {bad} are neither CHECKED nor 'UNCHECKED: <reason>'. "
            f"A reasonless UNCHECKED collapses 'could not look' back into 'found "
            f"nothing' (DE-35)",
        )
    unknown = [k for k in status if k not in BY_NAME]
    if unknown:
        raise ContractViolationError("CT-7.7", f"class_status has unknown class(es) {unknown}")
