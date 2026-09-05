"""D-07 Data Engine — acquire, validate, store, serve. SEAT-5.

```
"Give me the data that was KNOWABLE on date D, in canonical shape, with its
 provenance — regardless of which source supplied it."
```

The phrase carrying the weight is **knowable on date D**. Any domain can fetch a
number; only D-07 can guarantee the number was available at the time it is being
used for. That guarantee is what makes constitution **INV-1** enforceable rather
than aspirational.

```
D-07 ACQUIRES, VALIDATES, STORES AND SERVES.
IT COMPUTES NOTHING A CONSUMER COULD ARGUE WITH.

Definitional derivation is in scope: gross_profit = revenue − cogs when the
filer omits it; a Money built from a float; a fiscal period normalised.

Analytical derivation is NOT: ratios, margins, growth rates, indicators,
scores. All of that is D-02.

The test: if two reasonable analysts could disagree about the right formula,
it does not belong here.
```

★ **This module is the whole public surface** (ST-3, §8). Reaching into
`src/data_engine/<module>/` from another domain is a defect even though Python
allows it (**IM-6**).
"""

from src.data_engine.contracts import (
    CalendarCheckReport, FUNDAMENTAL_PANEL, Finding, PRICE_PANEL, Provenance,
    require_raw, validate_fundamental_panel, validate_price_panel,
)
from src.data_engine.calendar import (
    EVENT_CLASSES, EventStore, ProbeResult, calendar_check, require_check, run_probe,
)
from src.data_engine.errors import (
    AdjAsOfRequiredError, AsOfRequiredError, CheckMissingError, ContractViolationError,
    DataError, LiveReadDeniedError, NoCikError, NoFilingDateError,
    NoFundamentalSourceError, PlanGateRejected, PlanGatedError, PointInTimeError,
    RawRequiredError, SourceUnavailableError, UnhandledBlockError, WARNING_CODES,
)
from src.data_engine.observation import ObservationLedger
from src.data_engine.pit import (
    CorporateEvent, Fact, FactLedger, UniverseEntry, build_price_panel,
)
from src.data_engine.service import DataEngine, FreshnessReport
from src.data_engine.universe import Universe, load_universe
from src.data_engine.validation import ValidationResult

__all__ = [
    # entities & contracts
    "CalendarCheckReport", "CorporateEvent", "FUNDAMENTAL_PANEL", "Fact", "Finding",
    "PRICE_PANEL", "Provenance", "UniverseEntry",
    # stores
    "EventStore", "FactLedger", "ObservationLedger", "Universe",
    # the surface
    "DataEngine", "FreshnessReport", "build_price_panel", "calendar_check",
    "load_universe", "require_check", "require_raw", "run_probe",
    "validate_fundamental_panel", "validate_price_panel",
    # the gate's vocabulary
    "EVENT_CLASSES", "ProbeResult", "ValidationResult", "WARNING_CODES",
    # errors
    "AdjAsOfRequiredError", "AsOfRequiredError", "CheckMissingError",
    "ContractViolationError", "DataError", "LiveReadDeniedError", "NoCikError",
    "NoFilingDateError", "NoFundamentalSourceError", "PlanGateRejected",
    "PlanGatedError", "PointInTimeError", "RawRequiredError", "SourceUnavailableError",
    "UnhandledBlockError",
]
