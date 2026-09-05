"""D-04 Model Training & Inference. SEAT-3's machinery, not its judgement.

```
A GUARD THAT FILTERS IS NOT A GUARD THAT CHECKS.

Filtering answers "what can I score with?"
Checking answers  "am I allowed to score at all?"

The first always succeeds. That is the entire problem —
it cannot fail, so it cannot warn.
```

★ This domain exists to close two incidents: **D-17** (a model fitted on 61
features scoring on 14, and 7 of 13 watchlist names scoring on all-NaN
fundamentals) and **D-18** (four failures with one signature — *a failure
indistinguishable from a result*).
"""

from src.models.artifact.manifest import (
    FeatureContractRef, ModelArtifact, ModelManifest, RESEARCH, RESEARCH_HORIZON,
    ROLES, SELECTION, TIMING,
)
from src.models.errors import (
    AnchorMismatchError, ContractUnresolvableError, DefaultSubstitutedError,
    HorizonRoleError, ModelError, NotEvaluatedError, ParityError,
)
from src.models.governance.drift import DriftReport, drift
from src.models.governance.parity import (
    HALT, MIN_FEATURE_COVERAGE, PASS, ParityReport,
    assert_some_name_is_actionable, check_parity,
)
from src.models.governance.promotion import (
    NOT_EVALUATED, PromotionRecord, REQUIRED_GATES, Registry, promote,
)
from src.models.infer.arbitrate import (
    ArbitrationResult, DELAY, NOMINATE, VETO, arbitrate,
)
from src.models.infer.score import ScoreResult, score
from src.models.train.fit import SELECTION_HORIZON_DAYS, TrainSpec, fit, select_best

__all__ = [
    "AnchorMismatchError", "ArbitrationResult", "ContractUnresolvableError",
    "DELAY", "DefaultSubstitutedError", "DriftReport", "FeatureContractRef",
    "HALT", "HorizonRoleError", "MIN_FEATURE_COVERAGE", "ModelArtifact",
    "ModelError", "ModelManifest", "NOMINATE", "NOT_EVALUATED",
    "NotEvaluatedError", "PASS", "ParityError", "ParityReport",
    "PromotionRecord", "REQUIRED_GATES", "RESEARCH", "RESEARCH_HORIZON",
    "ROLES", "Registry", "SELECTION", "SELECTION_HORIZON_DAYS", "ScoreResult",
    "TIMING", "TrainSpec", "VETO", "arbitrate", "assert_some_name_is_actionable",
    "check_parity", "drift", "fit", "promote", "score", "select_best",
]
