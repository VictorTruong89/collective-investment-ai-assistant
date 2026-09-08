"""D-02 Feature Engineering — the deterministic computation layer. SEAT-5.

```
"Give me the computed number — the same number, by the same formula,
 whoever is asking and whenever they ask."
```

The weight is on **the same number**. Any domain can compute a margin; only D-02
can guarantee that the margin the thesis quotes, the margin the model trains on,
and the margin the backtest replays are **one definition with one
implementation**. That is what makes **INV-4** checkable rather than aspirational.

★ **D-02 is NEUTRAL GROUND** (SEAT-5). It is upstream of both analyst seats and
consumes neither's output — **FE-21**, and it is the property that keeps INV-014
intact. A deterministic function of an LLM's output is still the LLM's judgement:
the determinism is in the transport, not the source.
"""

from src.feature_engineer.contracts.panel import ENVELOPE, coverage, validate_panel
from src.feature_engineer.contracts.registry import ContractRegistry
from src.feature_engineer.contracts.sets.b3_minimal_v1 import B3_MINIMAL_V1
from src.feature_engineer.contracts.spec import FeatureContract, FeatureSpec
from src.feature_engineer.errors import (
    AnalystDerivedInputError,
    AsOfRequiredError,
    CalendarHaltError,
    ContractMutatedError,
    ContractUnknownError,
    DuplicateDefinitionError,
    FeatureError,
    LabelInContractError,
    MissingFeatureError,
    RangeViolationError,
    UndeclaredColumnError,
)
from src.feature_engineer.ml_features.assemble import BUILDERS, build_panel

__all__ = [
    "AnalystDerivedInputError", "AsOfRequiredError", "B3_MINIMAL_V1", "BUILDERS",
    "CalendarHaltError", "ContractMutatedError", "ContractRegistry",
    "ContractUnknownError", "DuplicateDefinitionError", "ENVELOPE", "FeatureContract",
    "FeatureError", "FeatureSpec", "LabelInContractError", "MissingFeatureError",
    "RangeViolationError", "UndeclaredColumnError", "build_panel", "coverage",
    "validate_panel",
]
