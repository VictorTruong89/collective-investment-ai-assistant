"""RM-1/RM-2/RM-3 — the k-run probe, in its PERTURBATION form (RA-61, RA-62, GW-10).

```
DO NOT RAISE k_stab TO 5. CHANGE WHAT VARIES BETWEEN RUNS INSTEAD.

Resampling the same distribution measures THE DECODER.
★ Perturbing the INPUT measures robustness to things that should not matter —
option order, evidence-item order, a paraphrased prompt at a fixed version.
Same k× cost, a property of THE ANALYSIS rather than of the sampler.
```

★★ **On this tier the perturbation form is not merely better — it is the only one
available.** `claude-opus-5` rejects `temperature` (GW-8a), so *the sampling probe
was never measuring a property anyone controlled* (GW-10). RM-1's sampling half is
therefore **`not_measurable`**, not `not_yet_calibrated` (**RA-136**).

⚠ **RA-20: this is the single most effective anti-overconfidence device
available**, because it is quantitative, honest and impossible to skim past. *A
reader who sees 3/5 sizes the position differently, and should.*
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.fundamental.monitor.registry import (
    FAIL, OK, WARN, MonitorResult, not_measurable,
)

#: RA-61 — **k stays at 3**; what varies is the input, not the sampler.
K_STAB = 3

#: What a perturbation may change. ⚠ **All of it is structure the answer should
#: be invariant to** — that is the definition of a perturbation here, and adding
#: anything that could legitimately change the answer would turn the probe into
#: a measurement of something else.
PERTURBATIONS = ("option_order", "evidence_order", "prompt_paraphrase")

#: RA-62 — the two forms, reported separately. `sampling` is structurally
#: unavailable on the deep tier and says so.
SAMPLING, PERTURBATION = "sampling", "perturbation"

#: ⚠ **ADMITTED GUESSES** (CN-10). RA-20 publishes the fraction verbatim and
#: names no threshold; these only colour the monitor row. RA-48's gate thresholds
#: are separate and live in `thesis/gate.py`.
UNSTABLE_BELOW = 0.8
SEVERELY_UNSTABLE_BELOW = 0.5


@dataclass(frozen=True, slots=True)
class StabilityResult:
    """RM-1's output. ★ It renders VERBATIM on the card (RA-20, RP-13)."""

    probe: str
    k: int
    distribution: dict
    perturbations_applied: tuple[str, ...] = ()

    @classmethod
    def from_json_obj(cls, payload: dict) -> "StabilityResult":
        """★ RM-1's figure **as it was measured**. ⚠ Never recomputed from a
        single stored verdict — that would report `agreement = 1.00` for every
        cached thesis, which is a measurement of nothing."""
        return cls(probe=payload["probe"], k=int(payload["k"]),
                   distribution=dict(payload.get("distribution") or {}),
                   perturbations_applied=tuple(
                       payload.get("perturbations_applied") or ()))

    def __post_init__(self) -> None:
        if self.probe not in (SAMPLING, PERTURBATION):
            raise ValueError(f"probe {self.probe!r} is not one of {(SAMPLING, PERTURBATION)}")
        total = sum(self.distribution.values())
        if total != self.k:
            raise ValueError(
                f"distribution sums to {total} but k={self.k}. RA-20 renders "
                f"'BUY 3 / HOLD 2' from these two and they must agree (RA-51a)"
            )
        if self.k < K_STAB:
            # AC-1.8 — the actionable pick always carries a k >= 3 result.
            raise ValueError(
                f"k={self.k} is below {K_STAB}. ★ AC-1.8: the actionable pick is "
                f"never exempt, because it is the only output anyone trades on"
            )

    @property
    def modal(self) -> str:
        return max(sorted(self.distribution), key=lambda v: self.distribution[v])

    @property
    def agreement(self) -> float:
        return self.distribution[self.modal] / self.k

    @property
    def is_stable(self) -> bool:
        return self.agreement >= UNSTABLE_BELOW

    @property
    def renders_as(self) -> str:
        """RA-20 verbatim — *"stable 5/5"* or *"⚠ unstable: BUY 3 / HOLD 2"*.

        ⚠ `stability_fraction` alone **cannot** produce the second form: 0.6 is
        equally 3/5, 6/10 or 12/20 (RA-51a). The distribution is what renders.
        """
        if self.agreement == 1.0:
            return f"stable {self.k}/{self.k}"
        parts = " / ".join(f"{v} {n}" for n, v in sorted(self.distribution.items()))
        return f"⚠ unstable: {parts}"

    def to_json_obj(self) -> dict:
        return {"probe": self.probe, "k": self.k, "modal": self.modal,
                "agreement": round(self.agreement, 6),
                "distribution": dict(self.distribution),
                "perturbations": list(self.perturbations_applied)}


def rm1_perturbation_probe(verdicts, *, perturbations=PERTURBATIONS) -> StabilityResult:
    """RM-1 — `k` runs of the SAME bundle with the INPUT restructured (RA-61).

    ⚠ **The caller supplies the verdicts, not the calls.** Running them is WF-1's
    job and each is a full authoring pass; this measures the spread. Keeping the
    measurement separate from the running is what lets RM-2 and RM-3 read the same
    `k` outputs without a second `k×` spend.
    """
    verdicts = tuple(verdicts)
    return StabilityResult(probe=PERTURBATION, k=len(verdicts),
                           distribution=dict(Counter(verdicts)),
                           perturbations_applied=tuple(perturbations))


def rm1_sampling_probe() -> MonitorResult:
    """★★ RA-136 / GW-10 — **structurally unavailable, and it says so.**

    ⚠ Not `not_yet_calibrated`: that promises a number is coming. *`claude-opus-5`
    rejects `temperature` with a 400 and sampling controls were removed across the
    4.6+ family* — so there is no knob, and there never will be one on this tier.
    """
    return not_measurable(
        "RM-1",
        "the deep tier has no sampling control — claude-opus-5 rejects temperature "
        "(GW-8a), so the sampling probe was never measuring a property anyone "
        "controlled (GW-10). RA-61's perturbation form is the only probe available",
    )


def rm1_result(stability: StabilityResult) -> MonitorResult:
    """RM-1 as a monitor row, coloured by the agreement fraction."""
    if stability.agreement < SEVERELY_UNSTABLE_BELOW:
        status = FAIL
    elif stability.agreement < UNSTABLE_BELOW:
        status = WARN
    else:
        status = OK
    return MonitorResult("RM-1", status, value=stability.to_json_obj(),
                         n=stability.k)


def rm2_scorecard_dispersion(scorecards) -> MonitorResult:
    """RM-2 — per-dimension spread across the k runs.

    ★ *A dimension that moves ≥ 2 levels between identical runs is not measuring
    anything.* ⚠ And **RA-34 says the fix is in the RUBRIC**: a dimension whose
    stated boundary observation differs each time has an under-determined
    rubric — not a noisy model.
    """
    scorecards = list(scorecards)
    if len(scorecards) < K_STAB:
        from src.fundamental.monitor.registry import not_yet_calibrated
        return not_yet_calibrated("RM-2", n=len(scorecards))
    spread = {}
    for dimension in sorted(scorecards[0]):
        values = [s[dimension] for s in scorecards]
        spread[dimension] = max(values) - min(values)
    worst = max(spread.values())
    return MonitorResult("RM-2", FAIL if worst >= 2 else OK, value=spread,
                         n=len(scorecards))


def rm3_numeric_spread(values_by_field) -> MonitorResult:
    """RM-3 — coefficient of variation of stop and targets across the k runs.

    ★ *Wide spread ⇒ the numbers are decoration.*
    """
    from statistics import fmean, pstdev

    cv = {}
    for field, values in sorted(values_by_field.items()):
        values = list(values)
        mean = fmean(values)
        cv[field] = 0.0 if mean == 0 else pstdev(values) / abs(mean)
    if not cv:
        from src.fundamental.monitor.registry import not_yet_calibrated
        return not_yet_calibrated("RM-3")
    return MonitorResult("RM-3", WARN if max(cv.values()) > 0.25 else OK,
                         value={k: round(v, 6) for k, v in cv.items()},
                         n=len(next(iter(values_by_field.values()), ())))
