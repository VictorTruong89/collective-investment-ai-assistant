"""D-03 §7 — the evaluation run. QA-11…QA-19, and D-04's MT-19 counterpart.

★★ **D-04 fits the models; D-03 decides whether they worked** — with machinery
D-04 cannot reach into (§3). This module is the thing `promote()` demands and
could not previously be given.
"""

from __future__ import annotations

import pandas as pd

from src.quant.backtest.costs import CostModel
from src.quant.backtest.protocol import assert_no_leakage, make_folds
from src.quant.contracts.backtest import BacktestResult, BacktestSpec
from src.quant.gates.metric_gate import (
    GateSet, assert_not_pooled, breadth_gate, cost_survival_gate,
    ic_significance_gate,
)
from src.quant.metrics.ic import rank_ic


def evaluate(spec: BacktestSpec, *, predictions: pd.DataFrame, horizons,
             cost_model: CostModel | None = None,
             effective_breadth: float | None = None,
             gross_return: float | None = None,
             net_return: float | None = None) -> BacktestResult:
    """Run the gates, **per horizon** (QA-16), and package CT-3.2.

    `predictions` carries `(date, ticker, horizon_days, score, value)`.
    ⚠ **Nothing here fits anything** — D-03 evaluates, and a domain that both
    fits and grades is the D-18 shape one level up.
    """
    costs = cost_model or CostModel()
    gate_sets = []
    for horizon in horizons:
        subset = predictions[predictions["horizon_days"] == horizon.trading_days]
        ic = rank_ic(subset, horizon_days=horizon.trading_days)
        gates = [
            ic_significance_gate(ic, horizon_id=horizon.id),
            cost_survival_gate(gross_return=gross_return, net_return=net_return,
                               horizon_id=horizon.id,
                               costs_charged=costs.components),
            breadth_gate(effective_breadth=effective_breadth,
                         names=int(round(ic.names_per_date)),
                         horizon_id=horizon.id),
        ]
        gate_sets.append(GateSet(horizon_id=horizon.id, gates=tuple(gates)))

    assert_not_pooled(gate_sets)
    return BacktestResult(spec_id=spec.spec_id, gate_sets=tuple(gate_sets),
                          gross_return=gross_return, net_return=net_return,
                          costs_charged=costs.components)


def folds_for(spec: BacktestSpec, dates, protocol) -> tuple:
    """The CV split, with the leakage check the construction should make
    unnecessary — ⚠ *"should" is not a guarantee.*"""
    folds = make_folds(dates, protocol)
    for fold in folds:
        assert_no_leakage(fold, purge_days=protocol.purge_days)
    return folds
