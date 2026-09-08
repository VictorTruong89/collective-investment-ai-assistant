"""D-06 Portfolio Strategy — sizing, scenarios, M-3. SEAT-4, forward-looking.

```
D-06 COMPUTES CONSEQUENCES. IT DOES NOT PROPOSE.

The output is "at a 2% risk budget and a 1.5σ stop this is 340 shares" — a
consequence of stated assumptions, not an answer to "what should I do".
```

⚠ **§5.3's collision is why that distinction is load-bearing.** `shares ∝ 1/σ`
means high-volatility names get small positions; the AI/semiconductor theme is
high-volatility, and **M-2 says concentration in it is a deliberate bet.**
Applied as a recommendation, the textbook rule would quietly implement the
diversification pressure M-2 rejects — **one trade at a time, with arithmetic as
the alibi.**
"""

from src.portfolio.contracts.sizing import (
    APPLIED,
    MAX_POSITION_PCT,
    REPORTED_ONLY,
    UNAPPLIED,
    UNMEASURED,
    Factor,
    RiskBudget,
    SizingAnswer,
    ThresholdCrossing,
)
from src.portfolio.errors import (
    NoStopError,
    PortfolioError,
    ReserveUnavailableError,
    TargetAllocationError,
    UnavailableInputError,
)
from src.portfolio.pyramid.scale import (
    TAX_EVENT,
    HoldAlternative,
    PyramidCheck,
    hold_alternative,
    pyramid_check,
)
from src.portfolio.scenario.whatif import (
    FORBIDDEN_REQUESTS,
    NOT_A_PROPOSAL,
    ParityComparison,
    Scenario,
    assert_not_a_target_request,
    risk_parity,
    scenario,
)
from src.portfolio.sizing.risk_based import (
    CONCENTRATION_THRESHOLD_PCT,
    SECTOR_MAX_PCT,
    THEME_REPORT_THRESHOLD_PCT,
    RiskBudgetState,
    account_risk,
    committed_risk,
    edge_factor,
    implied_risk,
    n_reserve,
    risk_budget,
    size_for_stop,
)
from src.portfolio.sizing.stop_distance import (
    DEFAULT_HORIZON_DAYS,
    DEFAULT_K,
    FORECAST,
    REALISED,
    StopDistance,
    implied_k,
    stop_distance,
)

__all__ = [
    "APPLIED", "CONCENTRATION_THRESHOLD_PCT", "DEFAULT_HORIZON_DAYS", "DEFAULT_K",
    "FORBIDDEN_REQUESTS", "FORECAST", "Factor", "HoldAlternative",
    "MAX_POSITION_PCT", "NOT_A_PROPOSAL", "NoStopError", "ParityComparison",
    "PortfolioError", "PyramidCheck", "REALISED", "REPORTED_ONLY",
    "ReserveUnavailableError", "RiskBudget", "RiskBudgetState", "SECTOR_MAX_PCT",
    "Scenario", "SizingAnswer", "StopDistance", "TAX_EVENT",
    "THEME_REPORT_THRESHOLD_PCT", "TargetAllocationError", "ThresholdCrossing",
    "UNAPPLIED", "UNMEASURED", "UnavailableInputError", "account_risk",
    "assert_not_a_target_request", "committed_risk", "edge_factor",
    "hold_alternative", "implied_k", "implied_risk", "n_reserve",
    "pyramid_check", "risk_budget", "risk_parity", "scenario", "size_for_stop",
    "stop_distance",
]
