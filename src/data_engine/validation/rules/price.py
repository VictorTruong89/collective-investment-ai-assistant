"""Price-panel quality rules. Each `rule_id` is L0 §6.4's `DQ-nnn` family."""

from __future__ import annotations

import pandas as pd

from src.data_engine.validation.registry import FLAG, REJECT, Rule, RuleRegistry


def price_rules() -> RuleRegistry:
    return (RuleRegistry()
            .add(Rule("DQ-001", REJECT, "close is null or non-positive",
                      lambda df: df["close_minor"].isna() | (df["close_minor"] <= 0)))
            .add(Rule("DQ-002", REJECT, "OHLC ordering violated (high < low)",
                      lambda df: df["high_minor"] < df["low_minor"]))
            .add(Rule("DQ-003", REJECT, "open or close outside the high-low range",
                      lambda df: (df["open_minor"] > df["high_minor"])
                                 | (df["open_minor"] < df["low_minor"])
                                 | (df["close_minor"] > df["high_minor"])
                                 | (df["close_minor"] < df["low_minor"])))
            .add(Rule("DQ-004", REJECT, "negative volume",
                      lambda df: df["volume"] < 0))
            # ⚠ FLAG, not REJECT. A zero-volume day is real on a holiday-adjacent
            # session and on a halted name; rejecting it would delete a true bar.
            # Flagging says "look before you build a liquidity feature on this".
            .add(Rule("DQ-005", FLAG, "zero volume — real on halts, suspicious otherwise",
                      lambda df: df["volume"] == 0))
            # ⚠ FLAG, not REJECT, and the threshold is an ADMITTED GUESS (CN-10).
            # 50 % is not a measured breakpoint; it is a level above which a
            # single-session move is worth a human look. A real 10:1 split shows
            # as -90 % here, which is exactly what §6A's gate is for.
            .add(Rule("DQ-006", FLAG, "|1-day return| > 50% — check for an unhandled split",
                      lambda df: _abs_return(df) > 0.50)))


def _abs_return(df: pd.DataFrame) -> pd.Series:
    # PD-5/PD-6: sort explicitly, and shift WITHIN ticker. A bare .shift() on a
    # stacked panel gives each ticker's first row the previous ticker's tail.
    ordered = df.sort_values(["ticker", "date"], kind="mergesort")
    prev = ordered.groupby("ticker")["close_minor"].shift(1)
    out = ((ordered["close_minor"] - prev) / prev).abs()
    return out.reindex(df.index)
