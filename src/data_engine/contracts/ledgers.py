"""CT-7.3 Fact ledger and CT-7.6 Observation ledger — the two append-only stores.

They exist for the same reason and against different failures.

    CT-7.3 answers "what did a filing SAY, and when did it become public" —
    EDGAR filings are immutable and separately addressable, so §6.3 can
    reconstruct any past date from them.

    CT-7.6 answers "what did a vendor say WHEN WE ASKED" — Class-B data has no
    publication axis at all, so D-07 supplies one. There is no retrofit:
    history not captured is gone.
"""

from __future__ import annotations

from src.data_engine.contracts.schema import Column, Schema

#: CT-7.3. `period_type` was added 2026-08-23 (spec v0.7.0): §6.3 step 2 groups
#: Facts by `(tag, period_end, period_type)` and this contract had never
#: declared it, so the PIT resolution algorithm keyed on a field its own ledger
#: did not have.
FACT_LEDGER = Schema(
    contract_id="CT-7.3",
    title="Fact ledger (append-only)",
    key=("ticker", "accession_id", "tag", "period_start", "period_end", "period_type"),
    monetary=("value",),
    columns=(
        Column("ticker", "string"),
        Column("accession_id", "string", note="which filing said this"),
        Column("tag", "string", note="XBRL concept"),
        Column("period_start", "date32"),
        Column("period_end", "date32"),
        Column("period_type", "string", note="annual | quarterly — §6.3 groups on it"),
        Column("value_minor", "int64", unit="minor units"),
        Column("value_currency", "string"),
        Column("unit", "string", note="the XBRL unit, e.g. USD, shares"),
        Column("filing_date", "date32", note="when it became public — the as-of axis"),
        Column("ingested_at", "timestamp", note="when WE learned it — our own latency"),
    ),
)

#: CT-7.6. `payload` is a canonicalised JSON string rather than a struct: the
#: field sets differ per endpoint, and a struct column would need a union type
#: that parquet only expresses by widening every row.
OBSERVATION_LEDGER = Schema(
    contract_id="CT-7.6",
    title="Observation ledger (append-only)",
    key=("ticker", "field_set", "observed_at"),
    columns=(
        Column("ticker", "string"),
        Column("field_set", "string", note="analyst_estimates | ratios_ttm | ..."),
        Column("observed_at", "timestamp", note="when WE asked — the whole point"),
        Column("source_endpoint", "string", note="the /stable/ path, verbatim"),
        Column("payload", "string", note="the response, canonicalised JSON"),
        Column("content_hash", "string", note="dedupe — an unchanged snapshot appends nothing"),
    ),
)

#: §5A.4's Class-B list, enumerated. A field set NOT in here is not Class-B and
#: does not need the ledger; one that IS may not be served live to a training,
#: backtest or inference consumer (DE-6.9, AC-7.26).
#:
#: ⚠ `analyst_estimates` is first deliberately. Its `date` field is the FORECAST
#: target period, not a publication date — the textbook look-ahead of §5A.4.
CLASS_B_FIELD_SETS = frozenset({
    "analyst_estimates",
    "price_target_consensus",
    "price_target_summary",
    "grades_consensus",
    "ratios_ttm",
    "key_metrics_ttm",
    "financial_scores",
    "shares_float",
    "profile",
    "ratings_snapshot",
    "stock_price_change",
    "insider_trading_statistics",
    "key_executives",
    "market_risk_premium",
    "fmp_dcf",
})

#: Consumers for whom a Class-B live read is illegal (DE-6.9). D-09 display is
#: deliberately absent: live consensus is genuinely useful on a report today and
#: genuinely poison in a training row, which is why the rule is written
#: per-consumer rather than per-field.
PIT_CONSUMERS = frozenset({"training", "backtest", "inference"})
