"""D-07's authoritative on-disk and in-flight shapes (CT-7.x).

`contracts.py` per L4 §1.3, widened to a package because D-07 owns six of them.
They differ from `models.py` in **authority**, not in layer: a contract is what
another domain may rely on, a model is what this one happens to use.
"""

from src.data_engine.contracts.envelopes import (
    BLOCK, FLAG, HALT, NOTE, PROCEED, PROCEED_WITH_FLAGS, UNCHECKED,
    CalendarCheckReport, Finding, Provenance,
)
from src.data_engine.contracts.ledgers import (
    CLASS_B_FIELD_SETS, FACT_LEDGER, OBSERVATION_LEDGER, PIT_CONSUMERS,
)
from src.data_engine.contracts.panels import (
    FUNDAMENTAL_PANEL, PRICE_PANEL, require_raw, validate_fundamental_panel,
    validate_price_panel,
)
from src.data_engine.contracts.schema import Column, Schema

__all__ = [
    "BLOCK", "CLASS_B_FIELD_SETS", "CalendarCheckReport", "Column", "FACT_LEDGER",
    "FLAG", "FUNDAMENTAL_PANEL", "Finding", "HALT", "NOTE", "OBSERVATION_LEDGER",
    "PIT_CONSUMERS", "PRICE_PANEL", "PROCEED", "PROCEED_WITH_FLAGS", "Provenance",
    "Schema", "UNCHECKED", "require_raw", "validate_fundamental_panel",
    "validate_price_panel",
]
