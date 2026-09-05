"""What gets snapshotted, and how often — CT-7.6's cadence (§5A.4, QD-6).

⚠ **QD-6 is open**: "how often is each Class-B field_set snapshotted?" Daily is
the obvious default and it is not free — 130 names x N field sets x 250 days.
Consensus moves slowly; TTM ratios move quarterly.

So the cadence is **config, not code** (CN-3: anything a human might tune is
config by definition, and anything in config appears in the RunManifest). The
table below is the DEFAULT this module ships with, and every entry is an
admitted estimate rather than a measurement — CN-10 says that is an acceptable
answer and silence is not.

★ The consolation §5A.4 records: for the two families that matter most, a
Class-A equivalent already exists. `grades` and `price-target-news` are the
event-stamped feeds behind `grades-consensus` and `price-target-consensus`.
**Prefer the event feed and aggregate it ourselves at an as_of** — that is
reconstructible backwards, where a snapshot is only ever forward from today.
"""

from __future__ import annotations

from dataclasses import dataclass

#: field_set -> (endpoint, default cadence in days, why).
#: ⚠ Every cadence here is an ADMITTED GUESS keyed to how fast the underlying
#: quantity is believed to move. None was measured (CN-10).
DEFAULT_SCHEDULE: dict[str, tuple[str, int, str]] = {
    "analyst_estimates":     ("analyst-estimates", 7,
                              "annual forecasts; limit<=10 and period=quarter is 402"),
    "price_target_consensus": ("price-target-consensus", 1,
                               "prefer price-target-news (Class A) — this is the fallback"),
    "grades_consensus":      ("grades-consensus", 1,
                              "prefer grades (Class A); snapshot only for D-09 display"),
    "ratios_ttm":            ("ratios-ttm", 30, "moves on the quarterly statement"),
    "key_metrics_ttm":       ("key-metrics-ttm", 30, "as ratios_ttm"),
    "financial_scores":      ("financial-scores", 30, "Altman/Piotroski, quarterly inputs"),
    "shares_float":          ("shares-float", 7, "changes on buybacks and issuance"),
    "profile":               ("profile", 30, "sector/industry/beta — near-static"),
}


@dataclass(frozen=True, slots=True)
class SnapshotPlan:
    field_set: str
    endpoint: str
    cadence_days: int
    rationale: str

    @property
    def is_class_a_available(self) -> bool:
        """True where §5A.4's event-stamped alternative exists and is preferred."""
        return self.field_set in ("price_target_consensus", "grades_consensus")


def plan(overrides: dict[str, int] | None = None) -> list[SnapshotPlan]:
    """The snapshot plan, with per-field-set cadence overrides from config (CN-4)."""
    overrides = overrides or {}
    return [
        SnapshotPlan(fs, endpoint, overrides.get(fs, days), why)
        for fs, (endpoint, days, why) in sorted(DEFAULT_SCHEDULE.items())
    ]
