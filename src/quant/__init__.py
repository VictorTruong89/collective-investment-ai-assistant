from src.quant.backtest.costs import (
    COMMISSION_ONLY, CostModel, FLAT_COMMISSION, FULL,
)
from src.quant.backtest.engine import evaluate, folds_for
from src.quant.backtest.protocol import (
    CVProtocol, Fold, assert_no_leakage, derive_protocol, group_key, make_folds,
)
from src.quant.contracts.backtest import (
    BacktestResult, BacktestSpec, PINNED_FIELDS, assert_survivorship_stated,
)
from src.quant.gates.metric_gate import (
    FAIL, GateResult, GateSet, NOT_EVALUATED, PASS, assert_not_pooled,
    breadth_gate, cost_survival_gate, ic_significance_gate,
)
from src.quant.metrics.ic import (
    ICResult, T_MULTIPLE_TESTING, assert_comparable, corrected_se, effective_n,
    rank_ic,
)
"""D-03 Quantitative Analysis — stateless calculation. SEAT-3.

★ **D-03 never emits a verdict** (QA-29). It ranks and it measures; gating is
P3's business and belongs downstream. **It is stateless** (QA-28): no module
holds fitted parameters, and none imports D-04.
"""

from src.quant.contracts.nomination import Candidate, Nomination
from src.quant.errors import (
    AdjustedLevelError, HorizonUnpinnedError, MethodMissingError, NominationContractError,
    QuantError,
)
from src.quant.horizons.horizon_set import PRODUCTION_V1, Arbitration, Horizon, HorizonSet
from src.quant.methods.registry import (
    declared_formula_ids, formula_ids_referenced_in_src, method, missing_sections,
)
from src.quant.signals.rank import FORMULA_ID as RANK_FORMULA_ID
from src.quant.signals.rank import rank_candidates, rule_id, within_ticker_z

__all__ = [
    # the evaluation protocol (D-03 §7)
    "BacktestResult", "BacktestSpec", "COMMISSION_ONLY", "CVProtocol",
    "CostModel", "FAIL", "FLAT_COMMISSION", "FULL", "Fold", "GateResult",
    "GateSet", "ICResult", "NOT_EVALUATED", "PASS", "PINNED_FIELDS",
    "T_MULTIPLE_TESTING", "assert_comparable", "assert_no_leakage",
    "assert_not_pooled", "assert_survivorship_stated", "breadth_gate",
    "corrected_se", "cost_survival_gate", "derive_protocol", "effective_n",
    "evaluate", "folds_for", "group_key", "ic_significance_gate", "make_folds",
    "rank_ic",
    "AdjustedLevelError", "Arbitration", "Candidate", "Horizon", "HorizonSet",
    "HorizonUnpinnedError", "MethodMissingError", "Nomination",
    "NominationContractError", "PRODUCTION_V1", "QuantError", "RANK_FORMULA_ID",
    "declared_formula_ids", "formula_ids_referenced_in_src", "method",
    "missing_sections", "rank_candidates", "rule_id", "within_ticker_z",
]
