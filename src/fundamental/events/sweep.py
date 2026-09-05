"""D-01 §10B.4 — the weekly accumulation sweep. RA-85, RA-86, RA-87.

★ **"Weekly" is right for the sweep and wrong for the trigger.** Events are
handled daily — *a 4.02 filed Monday cannot wait until Friday*. The sweep exists
for what no single day trips: **a drip of small residuals** none of which
breaches the daily threshold, guidance quietly not repeated, a risk factor
added, competitor capacity moving `announced → operating`, a falsifier
approaching slowly. ★ **That is how a thesis usually actually dies.**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.fundamental.errors import SweepSilentError
from src.fundamental.invalidation.models import assert_no_verdict

#: RA-85's subject matter. ⚠ Not events — those are daily.
ACCUMULATION_KINDS = (
    "residual_drip", "guidance_not_repeated", "risk_factor_added",
    "competitor_capacity", "falsifier_approaching",
)


@dataclass(frozen=True, slots=True)
class Accumulation:
    """One slow change. It is *routed*, never acted on (RA-87)."""

    kind: str
    ticker: str
    detail: str
    refs: tuple[str, ...] = ()
    route_to: str = ""

    def __post_init__(self) -> None:
        if self.kind not in ACCUMULATION_KINDS:
            raise ValueError(
                f"{self.kind!r} is not an accumulation kind {ACCUMULATION_KINDS}. ⚠ An event "
                f"belongs in the daily path, not the sweep (RA-85)"
            )

    def to_json_obj(self) -> dict:
        return {"kind": self.kind, "ticker": self.ticker, "detail": self.detail,
                "refs": list(self.refs), "route_to": self.route_to}


@dataclass(frozen=True, slots=True)
class SweepReport:
    """★ RA-86 — emitted every week, *including* the weeks nothing happened.

    *A sweep that appears only when it has something to say is indistinguishable
    from a sweep that did not run* (RA-30, DE-35).
    """

    week_ending: date
    accumulations: tuple[Accumulation, ...]
    covered: tuple[str, ...] = ()

    @property
    def nothing_accumulated(self) -> bool:
        return not self.accumulations

    def to_json_obj(self) -> dict:
        obj = {
            "week_ending": self.week_ending.isoformat(),
            "covered": list(self.covered),
            "nothing_accumulated": self.nothing_accumulated,
            "accumulations": [a.to_json_obj() for a in self.accumulations],
            "statement": ("nothing accumulated" if self.nothing_accumulated
                          else f"{len(self.accumulations)} state changes routed"),
        }
        # ⚠ RA-87 — **the sweep produces no verdict and no recommendation.** A
        #   weekly monitor that began proposing trades would be a second
        #   decision channel, and the constitution permits exactly one (INV-6).
        assert_no_verdict(obj, where="SweepReport")
        return obj


def weekly_sweep(week_ending: date, *, findings=(), covered=()) -> SweepReport:
    """Always returns a report. There is no path here that returns `None`."""
    return SweepReport(week_ending=week_ending,
                       accumulations=tuple(findings),
                       covered=tuple(sorted(covered)))


def assert_sweep_emitted(reports, week_ending: date) -> SweepReport:
    """RA-86 / AC-1.54 — a missing week is a defect, not an empty week."""
    for report in reports:
        if report.week_ending == week_ending:
            return report
    raise SweepSilentError(week_ending)


def actionable_recommendations(report: SweepReport) -> int:
    """RA-87 / AC-1.55 — INV-6's count, and the sweep's contribution to it: zero."""
    return 0
