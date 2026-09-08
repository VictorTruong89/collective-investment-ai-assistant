"""D-05 Risk Management — measures and says. SEAT-4. LEVEL 2 ALERT.

```
D-05 CANNOT BE SILENCED AND CANNOT STOP ANYTHING.

Most risk systems earn their keep by refusing; this one earns it by being
impossible to ignore and impossible to obey. It follows from M-2: the
concentration IS the bet, and a risk function that could veto it would be
overruling the mandate on the strength of a statistic.
```

★ **B5 — the full WF-R1 ladder.** *(B3 shipped the alert channel and a refusal;
`daily_pass` still refuses when handed no book, which is RK-29 and not a gap.)*
The book itself — `CT-11.4` — was assigned to no milestone and is built at the
head of B5 (**BS-15b**).
"""

from src.risk.alerts.daily import daily_book_pass
from src.risk.alerts.service import daily_pass, emit, refuse_to_block, suppress
from src.risk.contracts.alerts import COMPLETE, Alert, AlertSet, unchecked
from src.risk.contracts.book_risk import (
    VAR_OMITTED_REASON,
    VAR_REQUIRED_FIELDS,
    BookRisk,
)
from src.risk.contracts.theme import THEMES_V1, UNCLASSIFIED, Theme, ThemeTaxonomy
from src.risk.errors import (
    BlockAttemptedError,
    FxUnavailableError,
    NoBookError,
    NotAggregatedError,
    NoTaxonomyError,
    RiskError,
    SuppressionAttemptedError,
    VarMethodUnstatedError,
    VarWithoutConcentrationError,
)
from src.risk.exposure.aggregate import (
    ALERT_LEVEL_2,
    CONCENTRATION_THRESHOLD_PCT,
    DIMENSIONS,
    REPORTED_ONLY,
    SECTOR_MAX_PCT,
    THEME_REPORT_THRESHOLD_PCT,
    UNCHECKED,
    ExposureView,
    ThresholdCrossing,
    assert_aggregated,
    exposure,
    thresholds_crossed,
)
from src.risk.flags.behavioural import (
    KINDS,
    PREMATURE_EXIT,
    PYRAMIDING,
    REGISTERED_SHORT_HOLD_DAYS,
    SHORT_HOLD,
    Flag,
    HoldingPeriods,
    acknowledge,
    premature_exit_flag,
    pyramiding_flag,
    short_hold_flags,
)
from src.risk.metrics.drawdown import (
    MIN_SERIES,
    UNMEASURED,
    DrawdownState,
    drawdown,
    unmeasured_factor,
)
from src.risk.metrics.marginal import (
    MarginalRisk,
    Unmeasured,
    hypothetical_book,
    marginal_risk,
)
from src.risk.stress.scenarios import (
    NOT_A_PREDICTION,
    SEMI_2022,
    Scenario,
    StressResult,
    stress,
)

__all__ = [
    # the alert channel (B3)
    "Alert", "AlertSet", "BlockAttemptedError", "COMPLETE", "NoBookError",
    "RiskError", "SuppressionAttemptedError", "daily_pass", "emit",
    "refuse_to_block", "suppress", "unchecked",
    # the full WF-R1 ladder (B5)
    "ALERT_LEVEL_2", "BookRisk", "CONCENTRATION_THRESHOLD_PCT", "DIMENSIONS",
    "DrawdownState", "ExposureView", "Flag", "FxUnavailableError",
    "HoldingPeriods", "KINDS", "MIN_SERIES", "MarginalRisk", "NOT_A_PREDICTION",
    "NoTaxonomyError", "NotAggregatedError", "PREMATURE_EXIT", "PYRAMIDING",
    "REGISTERED_SHORT_HOLD_DAYS", "REPORTED_ONLY", "SECTOR_MAX_PCT", "SEMI_2022",
    "SHORT_HOLD", "Scenario", "StressResult", "THEMES_V1",
    "THEME_REPORT_THRESHOLD_PCT", "Theme", "ThemeTaxonomy", "ThresholdCrossing",
    "UNCHECKED", "UNCLASSIFIED", "UNMEASURED", "Unmeasured",
    "VAR_OMITTED_REASON", "VAR_REQUIRED_FIELDS", "VarMethodUnstatedError",
    "VarWithoutConcentrationError", "acknowledge", "assert_aggregated",
    "daily_book_pass", "drawdown", "exposure", "hypothetical_book",
    "marginal_risk", "premature_exit_flag", "pyramiding_flag", "short_hold_flags",
    "stress", "thresholds_crossed", "unmeasured_factor",
]
