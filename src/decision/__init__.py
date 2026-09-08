"""D-12 Decision — compose, attribute, originate nothing. SEAT-5 · LEVEL 1.

```
D-03 quant ---> nomination ---+
D-01 research ---> gate ------+
D-05 risk ---> alerts --------+
                              v
              D-12 DECISION — compose, attribute, never originate
                              |
                    +---------+---------+
                    v                   v
              D-09 renders        D-11 records
```

★ **Every existing domain was the wrong home for a stated reason** — that is what
a missing domain looks like (§1.2). D-12 is the neutral layer *downstream* of both
analyst seats, exactly as D-02 is the neutral layer *upstream* of both.
"""

from src.decision.algebra.verdict import (
    ABSORBING,
    BUY,
    CONSERVATISM,
    FLAG,
    HOLD,
    IDENTITY,
    PASS,
    SELL,
    SEVERITY,
    VETO,
    apply_gate,
    conservatism,
    is_no_more_aggressive_than,
    meet,
)
from src.decision.attribute.binding import attribute
from src.decision.compose.service import compose, enforce_inv6, veto_rate
from src.decision.contracts.recommendation import (
    Attribution,
    GateOutcome,
    Recommendation,
)
from src.decision.errors import (
    AbsentTreatedAsPassError,
    AnchorMismatchError,
    AttributionIncompleteError,
    DecisionError,
    GateMissingError,
    GateUnavailableError,
    MultipleActionableError,
    SellNotHeldError,
    VerdictOriginatedError,
    VerdictUpgradeError,
)

__all__ = [
    "ABSORBING", "AbsentTreatedAsPassError", "AnchorMismatchError", "Attribution",
    "AttributionIncompleteError", "BUY", "CONSERVATISM", "DecisionError", "FLAG",
    "GateMissingError", "GateOutcome", "GateUnavailableError", "HOLD", "IDENTITY",
    "MultipleActionableError", "PASS", "Recommendation", "SELL", "SEVERITY",
    "SellNotHeldError", "VETO", "VerdictOriginatedError", "VerdictUpgradeError",
    "apply_gate", "attribute", "compose", "conservatism", "enforce_inv6",
    "is_no_more_aggressive_than", "meet", "veto_rate",
]
