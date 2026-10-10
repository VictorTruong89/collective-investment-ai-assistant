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

import math
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

    def __post_init__(self) -> None:
        """AC-F12.10 — ★ a PASS must rest on a statistic (QA-17, D-18)."""
        from src.quant.errors import GateVacuousError

        if self.verdict not in (PASS, FAIL, NOT_EVALUATED):
            raise GateVacuousError(
                f"gate {self.gate_id!r}: verdict {self.verdict!r} is not one of "
                f"PASS / FAIL / NOT_EVALUATED")
        if self.verdict == PASS and self.statistic is None:
            raise GateVacuousError(
                f"gate {self.gate_id!r} reported PASS with no statistic — a gate "
                f"that cannot fail is decoration (QA-17, F0 D-18)")

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
    """★★ F12 `D9` / AC-F12.31 — PASS only if `|mean IC| ≥ t* × REALISED SE`.

    ✏ *2026-10-06 (Victor, closes L6 AB-12):* the bar used to be the MDE —
    `t* × corrected_se`, the NULL SE, i.e. the spread per-date IC would have **if
    the model had no skill**. That answers a planning question; the variance a
    holder lives through is the realised one, and on the August 2026 fit the two
    disagreed by 3.5× (t 4.94 vs 1.42). The null MDE is still reported in `why`.
    ⚠ No realised SE (too few dates for the lag window) ⇒ NOT_EVALUATED (QA-17).
    """
    realised = getattr(result, "realised_se", None)
    if result.status == NOT_EVALUATED or result.mean_ic is None or not realised:
        # ★ QA-17 — never a pass.
        return GateResult(
            gate_id="ic_significance", horizon_id=horizon_id, statistic=None,
            threshold=0.0, effective_n=result.effective_n,
            corrected_se=realised, formula_id=result.formula_id,
            verdict=NOT_EVALUATED,
            why=(result.why or ("the realised standard error could not be "
                                "estimated (too few dates for the h-1 lag window)"
                                if result.mean_ic is not None
                                else "the IC was not computable")))
    bar = t_star * realised
    passed = abs(result.mean_ic) >= bar
    mde = result.mde(t_star)
    return GateResult(
        gate_id="ic_significance", horizon_id=horizon_id,
        statistic=round(result.mean_ic, 6), threshold=round(bar, 6),
        effective_n=result.effective_n, corrected_se=realised,
        formula_id=result.formula_id, verdict=PASS if passed else FAIL,
        why=(f"|IC| {abs(result.mean_ic):.4f} {'>=' if passed else '<'} "
             f"{t_star:g} × realised SE {realised:.4f} = {bar:.4f} "
             f"(t {abs(result.mean_ic) / realised:.2f}; Newey-West, F12 D9) · "
             f"null MDE {mde:.4f} (t {abs(result.t_stat or 0):.2f}) reported, not "
             f"decisive · N_eff={result.effective_n}"))


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


#: ★ F12 `D10` — the information ratio the breadth gate asks for (Victor, 2026-10-06).
#: ⚠ PROVISIONAL: refine after the first fresh training run's results.
IR_TARGET = 0.5


def breadth_gate(*, effective_breadth: float | None, names: int,
                 horizon_id: str, mean_ic: float | None = None,
                 ir_target: float = IR_TARGET, held_book: dict | None = None,
                 basis: str = "raw ρ") -> GateResult:
    """★★ F12 `D10` / AC-F12.32 — the implied information ratio `|IC|·√BR` ≥ `IR*`.

    Grinold–Kahn: `IR ≈ IC · √BR`. Equivalently `BR ≥ (IR*/IC)²` — *this much skill
    needs this many independent bets a year*. `BR` is the UNIVERSE's (QA-43, measured,
    never `n`), because the IC is measured on the universe ranking and the law pairs
    the IC and the breadth OF THE SAME DECISIONS. The held book is reported in `why`,
    never gated.

    ✏ *2026-10-06:* the gate was `BR ≥ 3`, and **it could not fail at 1m** — even at
    ρ = 1, `n_eff = 1` and 12 rebalances give `BR = 12` (QA-17: decoration).
    ⚠ An unmeasured `BR` or IC ⇒ NOT_EVALUATED, never a pass.

    ✏ *2026-10-08 — F12 `D13`:* the caller supplies `BR` from the EXTERNAL
    market-only residual ρ (`breadth.gated_breadth`); `basis` names it in `why`.
    """
    formula = "breadth.residual_correlation.v1"
    if effective_breadth is None or mean_ic is None:
        missing = (f"effective breadth was not measured ({basis}) — ⚠ QA-43 forbids "
                   f"substituting n={names} or another ρ" if effective_breadth is None
                   else "the mean IC was not measured")
        return GateResult("breadth", horizon_id, None, ir_target, None, None,
                          formula, NOT_EVALUATED, missing)
    ir = abs(mean_ic) * math.sqrt(max(effective_breadth, 0.0))
    held = ""
    if held_book and held_book.get("breadth") is not None:
        held_ir = abs(mean_ic) * math.sqrt(held_book["breadth"])
        held = (f" · held book (diagnostic, never gated): BR {held_book['breadth']:.1f}"
                f", IR {held_ir:.3f}")
    needed = (ir_target / abs(mean_ic)) ** 2 if mean_ic else float("inf")
    return GateResult(
        "breadth", horizon_id, round(ir, 4), ir_target, None, None, formula,
        PASS if ir >= ir_target - 1e-12 else FAIL,
        f"implied IR |IC| {abs(mean_ic):.4f} × √BR {effective_breadth:.1f} = {ir:.3f} "
        f"vs IR* {ir_target:g} (needs BR ≥ {needed:.0f}; universe n={names}; "
        f"BR from {basis}; F12 D10/D13){held}")


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
