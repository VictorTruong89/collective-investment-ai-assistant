"""F5 `AC-5.9` — is an attribution actually explaining the model?

★★ **The deletion curve is the test that catches a plausible-looking lie.** If
removing the top-`k` attributed features degrades performance no faster than
removing random ones, the attribution carries no information about the model —
however convincing its ranking looks.

⚠ `PG-5`: a negative result here is a real result and is worth publishing.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.metrics.models import MetricResult, insufficient, measured


@dataclass(frozen=True, slots=True)
class DeletionCurve:
    """`attributed` and `random_baseline`: performance after deleting top-k."""

    attributed: tuple[float, ...]
    random_baseline: tuple[float, ...]
    verdict: str                 # FAITHFUL | UNFAITHFUL | INSUFFICIENT
    result: MetricResult


def deletion_curve(attributed: list[float], random_baseline: list[float], *,
                   inputs_ref: str, n_features: int,
                   experimental: bool = False) -> DeletionCurve:
    """Area between the curves. ⚠ Positive means the attribution beats chance."""
    if len(attributed) != len(random_baseline):
        raise ValueError("the two curves must be sampled at the same k values")
    if n_features < 30:  # D3 admitted floor — see MINIMUM_N["deletion_curve"]
        return DeletionCurve((), (), "INSUFFICIENT",
                             insufficient("deletion_curve", n_features, "A",
                                          inputs_ref, experimental=experimental))
    # ★ strict=True: the two curves are asserted equal-length above, and a
    # silent truncation here would average a SHORTER curve and report it as
    # the gap — a wrong number rather than an error.
    gap = sum(r - a for a, r in zip(attributed, random_baseline, strict=True)
              ) / len(attributed)
    res = measured("deletion_curve", gap, n_features, "A", inputs_ref,
                   experimental=experimental)
    verdict = "FAITHFUL" if (res.is_sufficient and gap > 0) else "UNFAITHFUL"
    return DeletionCurve(tuple(attributed), tuple(random_baseline), verdict, res)
