"""D-03 §7.2 — metric gates. QA-15, QA-16, QA-17.

★ **QA-15: a gate declares the statistic, the threshold, the effective N and the
corrected standard error.** ⚠ *A gate that reports only "0.031 ≥ 0.03 → PASS" is
not a gate.*

⚠ **QA-17 has a live precedent.** F0 **D-18**: every candidate in the sleeve
optimiser failed, `best_sharpe` stayed at `-inf`, the untouched defaults were
adopted — and **`phase3b` still reported PASS, for over a month, across 8 of 8
folds.** ★ *A gate that cannot fail is decoration.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

PASS, FAIL, NOT_EVALUATED = "PASS", "FAIL", "NOT_EVALUATED"

#: ★★ **The required gate set lives HERE, because the gates are D-03's**
#: (D-04 **MT-19**: *"D-04 does not evaluate itself. The gates are D-03's, run
#: by D-03's code, against D-03's protocol."*).
#:
#: ⚠ *Added 2026-08-26, found by running the chain end to end:* **D-04 had
#: enumerated its own list and included a `stability` gate D-03 never
#: produces**, so promotion refused every artifact. Neither spec enumerated the
#: set, so the producing and consuming domains disagreed silently — **MT-18
#: caught it**, which is the rule working exactly as intended.
#: ★ D-04 imports this; adding a gate here reaches promotion automatically.
REQUIRED_GATES = ("ic_significance", "cost_survival", "breadth")


@dataclass(frozen=True, slots=True)
class GateResult:
    """★ Everything QA-15 requires, on the artifact rather than in a log."""

    gate_id: str
    horizon_id: str
    statistic: float | None
    threshold: float
    effective_n: float | None
    corrected_se: float | None
    formula_id: str
    verdict: str
    why: str = ""

    @property
    def t_stat(self) -> float | None:
        if self.statistic is None or not self.corrected_se:
            return None
        return self.statistic / self.corrected_se

    def to_json_obj(self) -> dict:
        return {"gate_id": self.gate_id, "horizon_id": self.horizon_id,
                "statistic": self.statistic, "threshold": self.threshold,
                "effective_n": self.effective_n,
                "corrected_se": self.corrected_se, "t_stat": self.t_stat,
                "formula_id": self.formula_id, "verdict": self.verdict,
                "why": self.why}


def ic_significance_gate(result, *, horizon_id: str, t_star: float = 3.0
                         ) -> GateResult:
    """★★ The bar is the **MDE**, not a hand-picked IC.

    ⚠ *A fixed IC threshold means completely different things at different `n`,
    `T` and `h`* — §5.3b's table shows the same 0.03 is undetectable at 1q and
    comfortable at 1w.
    """
    if result.status == NOT_EVALUATED or result.mean_ic is None:
        # ★ QA-17 — never a pass.
        return GateResult(
            gate_id="ic_significance", horizon_id=horizon_id, statistic=None,
            threshold=0.0, effective_n=result.effective_n,
            corrected_se=result.corrected_se, formula_id=result.formula_id,
            verdict=NOT_EVALUATED, why=result.why or "the IC was not computable")
    mde = result.mde(t_star)
    passed = abs(result.mean_ic) >= mde
    return GateResult(
        gate_id="ic_significance", horizon_id=horizon_id,
        statistic=round(result.mean_ic, 6), threshold=round(mde, 6),
        effective_n=result.effective_n, corrected_se=result.corrected_se,
        formula_id=result.formula_id, verdict=PASS if passed else FAIL,
        why=(f"|IC| {abs(result.mean_ic):.4f} "
             f"{'>=' if passed else '<'} MDE(t>{t_star:g}) {mde:.4f} at "
             f"N_eff={result.effective_n}"))


def cost_survival_gate(*, gross_return: float | None, net_return: float | None,
                       horizon_id: str, costs_charged: str) -> GateResult:
    """QA-12/INV-016 — ★ **reported with costs applied**, and the components
    named. ⚠ A strategy that survives gross and dies net has not survived."""
    if gross_return is None or net_return is None:
        return GateResult("cost_survival", horizon_id, None, 0.0, None, None,
                          "cost.flat_commission.v1", NOT_EVALUATED,
                          "gross or net return was not computed")
    return GateResult(
        "cost_survival", horizon_id, round(net_return, 6), 0.0, None, None,
        "cost.flat_commission.v1", PASS if net_return > 0 else FAIL,
        f"net {net_return:.4f} vs gross {gross_return:.4f}, "
        f"costs_charged={costs_charged}")


def breadth_gate(*, effective_breadth: float | None, names: int,
                 horizon_id: str, minimum: float = 3.0) -> GateResult:
    """QA-43 — ★ **effective breadth is MEASURED, not assumed.**

    ⚠ *Neither `BR = n` nor the equally-weighted-mean haircut is admissible as a
    default*, so an unmeasured breadth is `NOT_EVALUATED` — never `n`.
    """
    if effective_breadth is None:
        return GateResult(
            "breadth", horizon_id, None, minimum, None, None,
            "breadth.residual_correlation.v1", NOT_EVALUATED,
            f"effective breadth was not measured. ⚠ QA-43 forbids substituting "
            f"n={names}: a ten-name book inside one theme is closer to 1-2")
    return GateResult(
        "breadth", horizon_id, round(effective_breadth, 4), minimum, None, None,
        "breadth.residual_correlation.v1",
        PASS if effective_breadth >= minimum else FAIL,
        f"BR {effective_breadth:.2f} vs minimum {minimum:.2f} over n={names}")


@dataclass(frozen=True, slots=True)
class GateSet:
    """QA-16 — ★ **evaluated per horizon, never on a pooled statistic.**"""

    horizon_id: str
    gates: tuple[GateResult, ...] = field(default_factory=tuple)

    @property
    def verdict(self) -> str:
        """⚠ `NOT_EVALUATED` propagates; it never rounds up to PASS."""
        verdicts = {g.verdict for g in self.gates}
        if not self.gates:
            return NOT_EVALUATED
        if FAIL in verdicts:
            return FAIL
        if NOT_EVALUATED in verdicts:
            return NOT_EVALUATED
        return PASS

    def outcomes(self) -> dict:
        """The shape D-04's `promote()` reads (MT-18)."""
        return {g.gate_id: g.verdict for g in self.gates}

    def to_json_obj(self) -> dict:
        return {"horizon_id": self.horizon_id, "verdict": self.verdict,
                "gates": [g.to_json_obj() for g in self.gates]}


def assert_not_pooled(gate_sets) -> None:
    """QA-16 — ★ one gate set per horizon, and they are not merged."""
    from src.quant.errors import QuantError

    horizons = [g.horizon_id for g in gate_sets]
    if len(horizons) != len(set(horizons)):
        raise QuantError(
            f"two gate sets share a horizon {horizons!r}. Gates are evaluated "
            f"per horizon and never pooled across them (QA-16, QA-5)")
