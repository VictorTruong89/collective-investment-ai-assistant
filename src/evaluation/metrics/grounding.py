"""F5 `AC-5.6` — grounding rate: how many factual claims are actually bound.

★ `AP-2` — cited claims only. ⚠ `unbound_claim_count` is reported **beside** the
rate, never folded into it: a 90 % rate over 10 claims and over 200 claims are
different facts, and the count is what tells them apart.

⚠ **This is not calibration** (`AC-5.5`). It measures whether claims are
*attached to evidence*, not whether they are *right*.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.metrics.models import MetricResult, insufficient, measured


@dataclass(frozen=True, slots=True)
class Claim:
    text: str
    is_factual: bool
    evidence_ref: str | None = None

    @property
    def is_bound(self) -> bool:
        return bool(self.evidence_ref)


@dataclass(frozen=True, slots=True)
class GroundingReport:
    result: MetricResult
    unbound_claim_count: int
    factual_claim_count: int


def grounding_rate(claims: list[Claim], *, inputs_ref: str,
                   tier: str = "A", experimental: bool = False) -> GroundingReport:
    """verified ÷ factual. ⚠ Non-factual claims are excluded from BOTH sides."""
    factual = [c for c in claims if c.is_factual]
    unbound = [c for c in factual if not c.is_bound]
    n = len(factual)
    if n == 0:
        return GroundingReport(
            insufficient("grounding_rate", 0, tier, inputs_ref,
                         experimental=experimental), 0, 0)
    rate = (n - len(unbound)) / n
    return GroundingReport(
        measured("grounding_rate", rate, n, tier, inputs_ref,
                 experimental=experimental),
        unbound_claim_count=len(unbound), factual_claim_count=n)
