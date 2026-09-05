"""D-04 §8 — drift. MT-21…MT-25.

★ **Three kinds, observable on very different timescales** — which matters more
under HorizonSet v1 than it did at 1w:

| Kind | Latency | Use |
|---|---|---|
| **Input** — feature distributions vs the training window | immediate | early warning |
| **Output** — `rank_score` distribution, rank turnover | immediate | early warning |
| **Performance** — realised IC decay | **≥ 21 trading days at 1m** | confirmation |

⚠ **MT-21: a retrain triggered on performance alone reacts a horizon late.**

★ **MT-22: the thresholds are D-03's.** They are metric gates; D-04 computes and
reports, and **does not set the bar.**
"""

from __future__ import annotations

from dataclasses import dataclass, field

INPUT, OUTPUT, PERFORMANCE = "input", "output", "performance"
UNMEASURED = "unmeasured"


@dataclass(frozen=True, slots=True)
class DriftReport:
    artifact_id: str
    window_days: int
    input_drift: dict = field(default_factory=dict)
    output_drift: dict = field(default_factory=dict)
    performance_drift: dict = field(default_factory=dict)

    @property
    def early_warnings(self) -> tuple[str, ...]:
        """★ MT-21 — input and output are the early warnings."""
        return tuple(k for k in (INPUT, OUTPUT)
                     if getattr(self, f"{k}_drift").get("status") == "moved")

    def to_json_obj(self) -> dict:
        return {"artifact_id": self.artifact_id, "window_days": self.window_days,
                "input": dict(self.input_drift), "output": dict(self.output_drift),
                "performance": dict(self.performance_drift),
                "early_warnings": list(self.early_warnings),
                # ⚠ MT-22 — no verdict here. The bar is D-03's.
                "verdict": "reported_not_judged"}


def _summary(values) -> dict:
    values = [v for v in values if v is not None]
    if not values:
        return {"status": UNMEASURED, "n": 0}
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n if n > 1 else 0.0
    return {"status": "measured", "n": n, "mean": round(mean, 6),
            "sd": round(var ** 0.5, 6)}


def drift(artifact, *, window_days: int, training_feature_stats=None,
          live_feature_stats=None, training_scores=None, live_scores=None,
          realised_ic=None) -> DriftReport:
    """MT-21 — all three are computed; ⚠ **none is judged here** (MT-22).

    `performance_drift` is `unmeasured` until at least one horizon has elapsed —
    ★ **not zero, and not "no drift"**: at 1m the earliest confirmation is 21
    trading days away, and reporting a number before then would invent one.
    """
    report_input = {"status": UNMEASURED}
    if training_feature_stats and live_feature_stats:
        shifted = [k for k in training_feature_stats
                   if k in live_feature_stats
                   and abs(live_feature_stats[k] - training_feature_stats[k])
                   > abs(training_feature_stats[k]) * 0.5]
        report_input = {"status": "moved" if shifted else "measured",
                        "shifted": sorted(shifted),
                        "compared": len(training_feature_stats)}

    report_output = {"status": UNMEASURED}
    if training_scores is not None and live_scores is not None:
        before, after = _summary(training_scores), _summary(live_scores)
        moved = (before["status"] == after["status"] == "measured"
                 and before["sd"] > 0
                 and abs(after["mean"] - before["mean"]) > before["sd"])
        report_output = {"status": "moved" if moved else "measured",
                         "training": before, "live": after}

    if realised_ic is None:
        report_performance = {
            "status": UNMEASURED,
            "why": (f"performance drift needs at least one horizon to elapse; "
                    f"at {window_days}d the earliest confirmation is that far "
                    f"away (MT-21). ⚠ Unmeasured is not 'no drift'")}
    else:
        report_performance = {"status": "measured", **_summary(realised_ic)}

    return DriftReport(artifact_id=artifact.artifact_id, window_days=window_days,
                       input_drift=report_input, output_drift=report_output,
                       performance_drift=report_performance)
