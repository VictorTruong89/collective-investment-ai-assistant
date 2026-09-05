"""CT-7.1 price panel and CT-7.2 fundamental panel — the two DataFrame contracts.

These are the shapes that cross the D-07 -> D-02 boundary, so they are where
**CA-8** bites: schema, dtypes and units declared, validated at the boundary.
"""

from __future__ import annotations

import pandas as pd

from src.data_engine.contracts.schema import Column, Schema
from src.data_engine.errors import ContractViolationError, RawRequiredError

#: CT-7.1. `adj_as_of` was added 2026-08-23 (spec v0.7.0): DE-30, AC-7.46 and
#: D-02 FE-8 all assert against it and the contract had never declared it —
#: the same seam defect that left `adj_open_minor` undeclared until v0.6.0.
PRICE_PANEL = Schema(
    contract_id="CT-7.1",
    title="Price panel",
    key=("ticker", "date"),
    monetary=("open", "high", "low", "close", "adj_close", "adj_open"),
    columns=(
        Column("ticker", "string", note="uppercase (DE-7)"),
        Column("date", "date32", note="trading day"),
        Column("open_minor", "int64", unit="minor units"),
        Column("high_minor", "int64", unit="minor units"),
        Column("low_minor", "int64", unit="minor units"),
        Column("close_minor", "int64", unit="minor units"),
        Column("open_currency", "string"),
        Column("high_currency", "string"),
        Column("low_currency", "string"),
        Column("close_currency", "string"),
        Column("volume", "int64", unit="shares"),
        Column("adj_close_minor", "int64", unit="minor units",
               note="close_minor x adj_factor (DE-42)"),
        Column("adj_open_minor", "int64", unit="minor units",
               note="open_minor x adj_factor (DE-42, QA-84)"),
        Column("adj_close_currency", "string"),
        Column("adj_open_currency", "string"),
        Column("adj_factor", "float64", unit="ratio",
               note="cumulative split.dividend factor in effect at adj_as_of"),
        Column("adj_as_of", "date32", nullable=True,
               note="null when raw; DE-30 / AC-7.46 / FE-8"),
        Column("is_adjusted", "bool", note="explicit, never inferred"),
        Column("source", "string"),
        Column("fetched_at", "timestamp"),
    ),
)

#: CT-7.2. `filing_date` is required (DE-6.3) and `accession_id` is nullable
#: because FMP rows have none — DE-5.2 makes `source` part of the contract, so a
#: consumer can tell which guarantee it is getting (DE-23).
FUNDAMENTAL_PANEL = Schema(
    contract_id="CT-7.2",
    title="Fundamental panel",
    key=("ticker", "period_end", "period_type"),
    monetary=(),
    columns=(
        Column("ticker", "string"),
        Column("period_start", "date32", note="both required — §5.1"),
        Column("period_end", "date32"),
        Column("period_type", "string", note="annual | quarterly"),
        Column("shares_outstanding", "int64", nullable=True, unit="shares",
               note="not monetary"),
        Column("source", "string", note='"edgar" | "fmp" — DE-5.1'),
        Column("accession_id", "string", nullable=True, note="null for FMP rows"),
        Column("filing_date", "date32", note="required — DE-6.3"),
        Column("ingested_at", "timestamp"),
        Column("pit_guarantee", "string",
               note="reconstructed (EDGAR) | best_effort (FMP) — DE-23, AC-7.38"),
        Column("restated", "bool", note="DE-6.5 / AC-7.13 — surfaced, not smoothed"),
        Column("quality_flags", "string",
               note="FLAG findings, ';'-joined; empty when clean (DE-12)"),
    ),
)


def line_item_columns(schema: Schema, df: pd.DataFrame) -> list[str]:
    """The `<line_item>_minor` columns a fundamental frame carries beyond the base.

    CT-7.2 declares "one pair per monetary line item" without enumerating them —
    the set is per-filer. So the base schema is fixed and the line items are
    validated by pairing rather than by name.
    """
    return sorted(c for c in df.columns
                  if c.endswith("_minor") and c not in schema.names)


def validate_fundamental_panel(df: pd.DataFrame) -> pd.DataFrame:
    """CT-7.2, including the open-ended line-item pairs (AC-7.14, AC-7.16).

    ⚠ `Schema.validate` rejects undeclared columns, which is right for a fixed
    shape and wrong here: the line items ARE the payload. So the pairs are split
    off, checked for their currency sibling, and the fixed part validated alone.
    """
    absent = [n for n in FUNDAMENTAL_PANEL.names if n not in df.columns]
    if absent:
        # Checked here rather than left to the column selection below, which
        # would raise a bare pandas KeyError and lose the contract id (EH-4).
        raise ContractViolationError(
            "CT-7.2", f"missing required column(s) {absent}; present: {sorted(df.columns)}"
        )
    items = line_item_columns(FUNDAMENTAL_PANEL, df)
    for col in items:
        base = col[: -len("_minor")]
        if f"{base}_currency" not in df.columns:
            from src.data_engine.errors import MissingCurrencyError
            raise MissingCurrencyError("CT-7.2", base)
    known = set(FUNDAMENTAL_PANEL.names) | set(items) | {
        f"{c[:-len('_minor')]}_currency" for c in items
    }
    unknown = [c for c in df.columns if c not in known]
    if unknown:
        raise ContractViolationError(
            "CT-7.2", f"undeclared column(s) {unknown} that are not line-item pairs"
        )
    FUNDAMENTAL_PANEL.validate(df[list(FUNDAMENTAL_PANEL.names)])
    return df


def validate_price_panel(df: pd.DataFrame) -> pd.DataFrame:
    """CT-7.1 plus the DC-1 constraints the schema cannot express (AC-7.15).

    Constitution **DC-1**: date monotonic per ticker, no future dates, no null
    close, OHLC ordering. Each is checked here because each has a real failure
    mode: an unsorted panel makes every `shift` silently wrong (**PD-5**), a
    future date is INV-1 arriving through the price feed, and `low > open` means
    the vendor sent a row nobody should build a return from.
    """
    PRICE_PANEL.validate(df)

    for ticker, grp in df.groupby("ticker", sort=True):
        if not grp["date"].is_monotonic_increasing:
            raise ContractViolationError(
                "CT-7.1",
                f"{ticker}: dates are not monotonic. Pandas will happily shift an "
                f"unsorted group and produce a plausible, wrong series with no "
                f"warning (DC-1, PD-5)",
            )

    today = pd.Timestamp.utcnow().tz_localize(None).normalize()
    future = df.loc[df["date"] > today, "date"]
    if len(future):
        raise ContractViolationError(
            "CT-7.1",
            f"{len(future)} row(s) dated after {today.date()} — a future price bar "
            f"is INV-1 arriving through the price feed (DC-1)",
        )

    bad = df[(df["high_minor"] < df["low_minor"])
             | (df["open_minor"] > df["high_minor"]) | (df["open_minor"] < df["low_minor"])
             | (df["close_minor"] > df["high_minor"]) | (df["close_minor"] < df["low_minor"])]
    if len(bad):
        raise ContractViolationError(
            "CT-7.1",
            f"{len(bad)} row(s) violate OHLC ordering (high >= low; low <= open, "
            f"close <= high) — first is "
            f"{bad.iloc[0]['ticker']} {bad.iloc[0]['date'].date()} (DC-1)",
        )

    if (df["adj_factor"] <= 0).any():
        raise ContractViolationError(
            "CT-7.1",
            "adj_factor must be strictly positive (DE-43). A zero or negative "
            "factor turns every adjusted price into nonsense that still has a dtype",
        )

    adjusted = df["is_adjusted"]
    if adjusted.any() and df.loc[adjusted, "adj_as_of"].isna().any():
        raise ContractViolationError(
            "CT-7.1",
            "is_adjusted is true on rows with a null adj_as_of. Two panels over the "
            "same dates with different adj_as_of are different data (DE-30)",
        )
    if (~adjusted).any() and df.loc[~adjusted, "adj_as_of"].notna().any():
        raise ContractViolationError(
            "CT-7.1", "a raw panel (is_adjusted false) must carry a null adj_as_of"
        )
    return df


def require_raw(df: pd.DataFrame, use: str) -> pd.DataFrame:
    """DE-29 / AC-7.45 — the guard a non-scale-invariant consumer calls.

    ★ This is the enforcement half of DE-29, and it is deliberately something the
    CONSUMER invokes: D-07 cannot know whether the caller is about to compute a
    return (scale-invariant, adjusted is correct) or an M-1 penny-stock screen
    (not scale-invariant, adjusted is a mandate-compliance defect). What D-07 can
    do is make the wrong one impossible to do silently.
    """
    if bool(df["is_adjusted"].any()):
        raise RawRequiredError(use)
    return df
