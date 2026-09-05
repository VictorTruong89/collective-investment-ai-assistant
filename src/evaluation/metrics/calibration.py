"""F5 `CT-5.3` — calibration: does a stated confidence match the observed rate?

★★ **Coverage is not calibration** (`AC-5.5`, upstream `AB-1`). Upstream defines
`confidence := evidence_coverage` — *how much the system looked at*. That is a
different quantity from *how often it is right*, and conflating them turns a
diligence measure into an accuracy claim. Both are computed here, they never
share a field name, and **neither is derived from the other**.

⚠ **Tier B** (`PG-5.1`): calibration needs resolved outcomes, so it can never
gate. It accrues.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.metrics.models import MetricResult, insufficient, measured

DEFAULT_BINS = 5


@dataclass(frozen=True, slots=True)
class Prediction:
    decision_id: str
    confidence: float          # 0..1, as stated BEFORE the outcome
    correct: bool | None = None  # from F2's CT-2.6 join; None = unresolved


@dataclass(frozen=True, slots=True)
class Bin:
    lower: float
    upper: float
    n: int
    mean_confidence: float
    observed_rate: float


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    """`CT-5.3` — extends `CT-5.1` rather than replacing it."""

    ece: MetricResult
    brier: MetricResult
    bins: tuple[Bin, ...]
    brier_decomposition: dict


def _resolved(preds: list[Prediction]) -> list[Prediction]:
    """⚠ `AC-5.8` — only outcomes joined by `decision_id`, each counted once."""
    seen: set[str] = set()
    out = []
    for p in preds:
        if p.correct is None or p.decision_id in seen:
            continue
        seen.add(p.decision_id)
        out.append(p)
    return out


def calibrate(preds: list[Prediction], *, inputs_ref: str,
              n_bins: int = DEFAULT_BINS, experimental: bool = False) -> CalibrationResult:
    resolved = _resolved(preds)
    n = len(resolved)
    if n == 0:
        z = insufficient("ece", 0, "B", inputs_ref, experimental=experimental)
        return CalibrationResult(z, insufficient("brier", 0, "B", inputs_ref,
                                                 experimental=experimental), (), {})

    edges = [i / n_bins for i in range(n_bins + 1)]
    bins: list[Bin] = []
    ece_acc = 0.0
    # `edges[1:]` is one shorter by construction — truncation IS the intent.
    for lo, hi in zip(edges, edges[1:], strict=False):
        members = [p for p in resolved
                   if (lo <= p.confidence < hi) or (hi == 1.0 and p.confidence == 1.0)]
        if not members:
            continue
        mean_conf = sum(p.confidence for p in members) / len(members)
        observed = sum(1 for p in members if p.correct) / len(members)
        bins.append(Bin(lo, hi, len(members), mean_conf, observed))
        ece_acc += (len(members) / n) * abs(mean_conf - observed)

    brier = sum((p.confidence - (1.0 if p.correct else 0.0)) ** 2 for p in resolved) / n
    base = sum(1 for p in resolved if p.correct) / n
    reliability = sum(b.n / n * (b.mean_confidence - b.observed_rate) ** 2 for b in bins)
    resolution = sum(b.n / n * (b.observed_rate - base) ** 2 for b in bins)
    uncertainty = base * (1 - base)

    return CalibrationResult(
        ece=measured("ece", ece_acc, n, "B", inputs_ref, experimental=experimental),
        brier=measured("brier", brier, n, "B", inputs_ref, experimental=experimental),
        bins=tuple(bins),
        brier_decomposition={"reliability": reliability, "resolution": resolution,
                             "uncertainty": uncertainty})


def evidence_coverage(sources_consulted: int, sources_available: int, *,
                      inputs_ref: str) -> MetricResult:
    """⚠ **NOT calibration** — upstream `AB-1`'s `confidence := evidence_coverage`.

    ★ A separate metric name, computed from different inputs, so a report cannot
    quietly present diligence as accuracy (`AC-5.5`).
    """
    if sources_available <= 0:
        return insufficient("evidence_coverage", 0, "A", inputs_ref, minimum=1)
    return MetricResult(metric="evidence_coverage",
                        value=sources_consulted / sources_available,
                        n=sources_available, tier="A", inputs_ref=inputs_ref)
