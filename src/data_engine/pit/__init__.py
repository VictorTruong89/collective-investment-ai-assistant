"""Point-in-time — §6, the reason D-07 exists.

Any domain can fetch a number; only D-07 can guarantee the number was available
at the time it is being used for. That guarantee is what makes constitution
**INV-1** enforceable rather than aspirational, which is why point-in-time is a
first-class module here and not a flag on a query.
"""

from src.data_engine.pit.adjustment import (
    assert_ex_dividend_convention, assert_factor_discipline, assert_matches_vendor,
    build_price_panel, dividend_multiplier, split_multiplier,
)
from src.data_engine.pit.ledger import FactLedger
from src.data_engine.pit.models import (
    ANNUAL, CalendarEntry, CorporateEvent, EDGAR, FMP, Fact, QUARTERLY, UniverseEntry,
    utcnow,
)
from src.data_engine.pit.restatement import (
    diff_against_stored, knowability_date, market_cap_at, next_session_knowability,
)
from src.data_engine.pit.snapshot import (
    assemble_rows, facts_as_of, inherit_filing_date, require_as_of, restatement_flags,
)

__all__ = [
    "ANNUAL", "CalendarEntry", "CorporateEvent", "EDGAR", "FMP", "Fact", "FactLedger",
    "QUARTERLY", "UniverseEntry", "assemble_rows", "assert_ex_dividend_convention",
    "assert_factor_discipline", "assert_matches_vendor", "build_price_panel",
    "diff_against_stored", "dividend_multiplier", "facts_as_of", "inherit_filing_date",
    "knowability_date", "market_cap_at", "next_session_knowability", "require_as_of",
    "restatement_flags", "split_multiplier", "utcnow",
]
