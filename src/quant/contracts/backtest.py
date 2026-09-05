"""D-03 CT-3.2 — BacktestSpec and BacktestResult. QA-11…QA-14.

★★ **QA-11: a backtest is not runnable without a fully pinned spec.** *Any
unpinned input makes the result unreproducible and therefore **inadmissible as
evidence**.*

⚠ **`initial_capital` is not housekeeping.** A flat per-trade fee's drag in
percentage terms depends entirely on the book — **1.20 %/yr at 1m on $100 k,
0.12 % on $1 M, a 10× spread on the same strategy** — so two backtests that
differ only in an unstated capital base are not comparable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date

#: QA-11's list, from §7.1. ⚠ Every one of them, or the spec does not run.
PINNED_FIELDS = (
    "universe", "start", "end", "horizon_set_name", "horizon_set_version",
    "initial_capital", "contract_version", "calendar_check_id", "as_of",
    "adj_as_of", "decision_anchor",
)


@dataclass(frozen=True, slots=True)
class BacktestSpec:
    """Everything §7.1 pins. ★ The id is its content hash — INV-2."""

    universe: tuple[str, ...]
    start: date
    end: date
    horizon_set_name: str
    horizon_set_version: int
    initial_capital: float
    contract_version: int
    calendar_check_id: str
    as_of: date
    adj_as_of: date
    decision_anchor: str
    protocol: dict = field(default_factory=dict)
    cost_model: dict = field(default_factory=dict)
    rebalance: str = "monthly"
    #: ⚠ QA-14 — survivorship is addressed **explicitly**, using D-07's
    #: `delisted-companies`. A backtest over currently-listed names only is
    #: reported as **biased**, not as a result.
    survivorship_handled: bool = False

    def __post_init__(self) -> None:
        from src.quant.errors import QuantError

        unpinned = [f for f in PINNED_FIELDS if not getattr(self, f, None)]
        if unpinned:
            raise QuantError(
                f"the backtest spec leaves {sorted(unpinned)!r} unpinned. ★ An "
                f"unpinned input makes the result unreproducible and therefore "
                f"INADMISSIBLE AS EVIDENCE (QA-11)")

    @property
    def spec_id(self) -> str:
        blob = json.dumps(self.to_json_obj(), sort_keys=True,
                          separators=(",", ":"))
        return "bts:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def to_json_obj(self) -> dict:
        return {"universe": list(self.universe), "start": self.start.isoformat(),
                "end": self.end.isoformat(),
                "horizon_set": {"name": self.horizon_set_name,
                                "version": self.horizon_set_version},
                "initial_capital": self.initial_capital,
                "contract_version": self.contract_version,
                "calendar_check_id": self.calendar_check_id,
                "as_of": self.as_of.isoformat(),
                "adj_as_of": self.adj_as_of.isoformat(),
                "decision_anchor": self.decision_anchor,
                "protocol": dict(self.protocol),
                "cost_model": dict(self.cost_model),
                "rebalance": self.rebalance,
                "survivorship_handled": self.survivorship_handled}


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """CT-3.2 — ★ per horizon: statistic, threshold, effective N, corrected SE,
    verdict and **the `formula_id` of every metric used**."""

    spec_id: str
    gate_sets: tuple
    gross_return: float | None = None
    net_return: float | None = None
    costs_charged: str = "commission_only"
    result_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "result_id", self._hash())

    @property
    def verdict(self) -> str:
        """⚠ One FAIL fails the result; one NOT_EVALUATED is not a pass."""
        from src.quant.gates.metric_gate import FAIL, NOT_EVALUATED, PASS

        verdicts = {g.verdict for g in self.gate_sets}
        if not self.gate_sets or NOT_EVALUATED in verdicts:
            return NOT_EVALUATED if FAIL not in verdicts else FAIL
        return FAIL if FAIL in verdicts else PASS

    @property
    def formula_ids(self) -> tuple[str, ...]:
        return tuple(sorted({g.formula_id for s in self.gate_sets
                             for g in s.gates if g.formula_id}))

    def gate_outcomes(self) -> dict:
        """The shape D-04's `promote()` reads (MT-17, MT-18)."""
        merged: dict = {}
        for gate_set in self.gate_sets:
            merged.update(gate_set.outcomes())
        return merged

    def to_json_obj(self) -> dict:
        return {"result_id": self.result_id, "spec_id": self.spec_id,
                "verdict": self.verdict,
                "per_horizon": [g.to_json_obj() for g in self.gate_sets],
                "gross_return": self.gross_return,
                "net_return": self.net_return,
                # ★ QA-12/INV-016 — the components, named, on every result.
                "costs_charged": self.costs_charged,
                "formula_ids": list(self.formula_ids),
                # ★ QA-13/INV-010 — the label travels with the number.
                "label": ("BACKTESTED, NET OF STATED COSTS — not an expected "
                          "return (QA-13, INV-010)")}

    def _hash(self) -> str:
        payload = {k: v for k, v in self.to_json_obj().items()
                   if k != "result_id"}
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return "bt:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def assert_survivorship_stated(result: BacktestResult, spec: BacktestSpec) -> None:
    """QA-14 / INV-017 — ★ *a backtest over currently-listed names only is
    reported as **biased**, not as a result.*"""
    from src.quant.errors import QuantError

    if not spec.survivorship_handled:
        raise QuantError(
            f"{result.result_id}: the spec does not handle survivorship. Use "
            f"D-07's `delisted-companies` feed, or label the result BIASED — "
            f"it is not admissible as a plain result (QA-14, INV-017)")
