"""F5 `CT-5.1` — the shape every figure this harness emits.

★★ **The point of this module is that a number cannot leave the harness without
its context.** `n` is required, the tier is required, and a figure computed on
too little data is not a figure at all — it is an insufficiency with a reason
(`AC-5.10`, `P5`).

⚠ **Coverage is not calibration.** Upstream `AB-1` defines
`confidence := evidence_coverage` — *how much the system looked at*, not *how
often it is right*. Both are computed here and they **never share a field name**
(`AC-5.5`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Tier = Literal["A", "B"]

#: ★ `D3` / `CN-10` — per-metric ADMITTED FLOORS. Each states who set it and on
#: what basis. Copying `src/quant/metrics/breadth.py::MIN_NAMES`, which says:
#: *"An admitted floor — nothing measured it; it exists so the function declines
#: rather than returning a confident number from four observations."*
#:
#: ⚠ Upstream `CN-10`: **"'admitted guess' is an acceptable answer; silence is
#: not."** None of these is derived from a power calculation, because the effect
#: sizes are unknown — that is what `F7a` exists to find out. They are revisable
#: precisely because they are written down.
MINIMUM_N: dict[str, int] = {
    # Victor + Claude, 2026-09-04, admitted guess. A rate over fewer than 20
    # claims moves by 5 percentage points per claim.
    "grounding_rate": 20,
    # Admitted guess. ECE with 5 bins needs enough per bin to mean anything;
    # 50 puts ~10 in each, which is still thin and is why the floor is stated.
    "ece": 50,
    "brier": 50,
    # Admitted guess. A deletion curve on fewer than 30 features is a step
    # function, not a curve.
    "deletion_curve": 30,
}

DEFAULT_MINIMUM_N = 20


def minimum_for(metric: str) -> int:
    """The admitted floor for `metric` (`D3`)."""
    return MINIMUM_N.get(metric, DEFAULT_MINIMUM_N)


class InsufficientSample(Exception):
    """Raised only where a caller asked for a bare number. Prefer the record."""


@dataclass(frozen=True, slots=True)
class MetricResult:
    """`CT-5.1` — ⚠ `value` and `insufficient_reason` are mutually exclusive."""

    metric: str
    n: int
    tier: Tier
    inputs_ref: str
    value: float | None = None
    selection_count: int | None = None
    insufficient_reason: str | None = None
    experimental: bool = False
    #: `AC-5.16` / `D4` — the inputs behind this figure have expired, so it can
    #: never be re-derived. ⚠ It remains a valid RECORD of what was measured.
    recomputable: bool = True
    computed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if self.n is None or self.n < 0:
            raise ValueError(f"n is never optional and never negative (AC-5.2); got {self.n}")
        if (self.value is None) == (self.insufficient_reason is None):
            raise ValueError(
                "exactly one of value / insufficient_reason must be set (CT-5.1) — "
                "a figure that is both present and insufficient is neither"
            )
        if self.value is not None and self.n <= 0:
            raise ValueError(
                f"{self.metric}: a value on n={self.n} is not a measurement (AC-5.2)")
        if self.tier not in ("A", "B"):
            raise ValueError(f"tier must be A or B (PG-5.1); got {self.tier!r}")
        if self.selection_count is not None and self.selection_count < 1:
            raise ValueError("selection_count counts candidates; it starts at 1 (QR-19)")

    @property
    def is_sufficient(self) -> bool:
        return self.value is not None

    def to_json_obj(self) -> dict:
        return {
            "metric": self.metric, "value": self.value, "n": self.n,
            "selection_count": self.selection_count, "tier": self.tier,
            "insufficient_reason": self.insufficient_reason,
            "computed_at": self.computed_at, "inputs_ref": self.inputs_ref,
            "experimental": self.experimental, "recomputable": self.recomputable,
        }


def insufficient(metric: str, n: int, tier: Tier, inputs_ref: str,
                 minimum: int | None = None, **kw) -> MetricResult:
    """`AC-5.10` — decline, and say by how much (`D3`)."""
    need = minimum if minimum is not None else minimum_for(metric)
    return MetricResult(
        metric=metric, n=n, tier=tier, inputs_ref=inputs_ref, value=None,
        insufficient_reason=(
            f"{metric} needs at least {need} observations; got {n}. "
            "⚠ An admitted floor (CN-10) — it exists so this declines rather than "
            "returning a confident number from too little data."),
        **kw)


def measured(metric: str, value: float, n: int, tier: Tier, inputs_ref: str,
             **kw) -> MetricResult:
    """A figure, or an insufficiency if `n` is below the metric's floor."""
    if n < minimum_for(metric):
        return insufficient(metric, n, tier, inputs_ref, **kw)
    return MetricResult(metric=metric, value=value, n=n, tier=tier,
                        inputs_ref=inputs_ref, **kw)
