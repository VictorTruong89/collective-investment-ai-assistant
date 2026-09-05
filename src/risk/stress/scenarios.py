"""D-05 §9 — stress replay. RK-24, RK-25, RK-26, RK-32.

★ **RK-26: the most informative stress for THIS book is a single-theme shock,
not a market shock.** A 2022-style semiconductor drawdown is the scenario M-2's
concentration actually exposes; ⚠ **a broad-market scenario mostly restates
beta.**

⚠ **RK-32: never on the daily critical path.** Scenario replay is expensive, is
labelled and never predictive, and a daily decision does not wait on it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: RK-24 — ★ every scenario is labelled, in the artifact, not in a docstring.
NOT_A_PREDICTION = (
    "NOT A PREDICTION — a replay of a stated historical episode or an explicit "
    "assumption, applied to today's book (RK-24, INV-010)"
)


@dataclass(frozen=True, slots=True)
class Scenario:
    """RK-24 — states its **historical source or its explicit assumption**."""

    scenario_id: str
    shocks: dict                  # theme or sector -> return, e.g. -0.45
    historical_source: str = ""
    assumption: str = ""

    def __post_init__(self) -> None:
        if not (self.historical_source or self.assumption):
            raise ValueError(
                f"{self.scenario_id!r} states neither a historical source nor "
                f"an explicit assumption. ★ A scenario that states neither is "
                f"a number with an author and no provenance (RK-24)"
            )

    def to_json_obj(self) -> dict:
        return {"scenario_id": self.scenario_id, "shocks": dict(self.shocks),
                "historical_source": self.historical_source,
                "assumption": self.assumption}


@dataclass(frozen=True, slots=True)
class StressResult:
    as_of: date
    scenario: Scenario
    impact_by_theme: dict
    total_impact_pct: float
    label: str = NOT_A_PREDICTION

    def to_json_obj(self) -> dict:
        return {"as_of": self.as_of.isoformat(),
                "scenario": self.scenario.to_json_obj(),
                "impact_by_theme": dict(self.impact_by_theme),
                "total_impact_pct": round(self.total_impact_pct, 4),
                "label": self.label}


def stress(view, scenario: Scenario, *, as_of: date) -> StressResult:
    """RK-25 — deterministic and reproducible given the book and the scenario.

    The arithmetic is `weight × shock`, summed. ★ Deliberately trivial: the
    value here is the *scenario choice* and its label, not the model.
    """
    impact, total = {}, 0.0
    for theme, weight in sorted(view.by_theme.items()):
        shock = scenario.shocks.get(theme)
        if shock is None:
            continue
        contribution = weight * float(shock)
        impact[theme] = round(contribution, 4)
        total += contribution
    return StressResult(as_of=as_of, scenario=scenario, impact_by_theme=impact,
                        total_impact_pct=total)


#: ★ RK-26's named candidate. ⚠ **QK-6 remains open** on whether the magnitude is
#: parameterised from history or stated; it is STATED here, and says so.
SEMI_2022 = Scenario(
    scenario_id="single_theme_shock_semi_2022",
    shocks={"ai_semiconductor": -0.45},
    historical_source=(
        "the 2022 semiconductor drawdown; SOX fell roughly 45% peak-to-trough. "
        "⚠ The magnitude is STATED, not fitted — QK-6 is open on whether it "
        "should be parameterised, and a MethodEntry is required either way (QA-20)"
    ),
)
