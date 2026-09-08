"""CT-2.2 — the feature panel, validated against its contract (CA-8, AC-2.1/2.2/2.4/2.5)."""

from __future__ import annotations

import pandas as pd

from src.feature_engineer.contracts.spec import FeatureContract
from src.feature_engineer.errors import (
    MissingFeatureError,
    RangeViolationError,
    UndeclaredColumnError,
)

#: CT-2.2's envelope — the columns that are not features. Every one is required:
#: FE-3 (contract identity), FE-7/FE-8 (both PIT axes), FE-10 (the check that
#: cleared the window). A panel missing any of them cannot be parity-checked,
#: reproduced, or traced to the corporate-action state it was built under.
ENVELOPE = ("ticker", "date", "contract_name", "contract_version",
            "as_of", "adj_as_of", "calendar_check_id")


def validate_panel(df: pd.DataFrame, contract: FeatureContract) -> pd.DataFrame:
    """Raise unless `df` satisfies CT-2.2 against `contract`; return it unchanged.

    ★ The two halves fail in opposite directions and both matter:
    an **undeclared** column is a feature nobody specified (FE-1); a **missing**
    one is D-17, where a model fitted on 61 features scored on 14 and the output
    was still called `rank_score`.
    """
    declared = set(contract.feature_names)
    present = set(df.columns) - set(ENVELOPE)

    missing = declared - present
    if missing:
        raise MissingFeatureError(missing)
    undeclared = present - declared
    if undeclared:
        raise UndeclaredColumnError(undeclared)

    absent_envelope = [c for c in ENVELOPE if c not in df.columns]
    if absent_envelope:
        raise MissingFeatureError(absent_envelope)

    # FE-5 / INV-3: the range is enforced at emit, not documented. NaN is not a
    # range violation — missing is a legitimate state (FE-14); out-of-range is not.
    for name in sorted(declared):
        spec = contract.spec(name)
        if spec.range is None:
            continue
        low, high = spec.range
        col = df[name]
        offending = col[(col.notna()) & ((col < low) | (col > high))]
        if len(offending):
            raise RangeViolationError(name, low, high, offending.head(3).tolist())

    if df.duplicated(subset=["ticker", "date"]).any():
        raise UndeclaredColumnError(["(ticker, date) is not unique"])
    return df


def coverage(df: pd.DataFrame, contract: FeatureContract) -> dict:
    """CT-2.4 — per-ticker usable-feature fraction (AC-2.20).

    ★ **NaN-but-present counts as missing**, and that is the whole point. A name
    can be *in* the panel with every `f_*` column present and every value NaN,
    and nothing in a column-name check will notice — which is exactly how D-17
    scored 7 of 13 watchlist names on nothing.
    """
    declared = list(contract.feature_names)
    out = {}
    for ticker, grp in df.groupby("ticker", sort=True):
        # ⚠ A declared column that is ABSENT is missing too — the strictest
        #   form of it. Indexing it directly raised a bare `KeyError` and lost
        #   the contract id, which is the shape D-07's `validate_fundamental_panel`
        #   had (v0.8.0) and the same fix applies.
        usable = [c for c in declared
                  if c in grp.columns and grp[c].notna().any()]
        out[ticker] = {
            "features_declared": len(declared),
            "features_usable": len(usable),
            "coverage_fraction": round(len(usable) / len(declared), 6) if declared else 0.0,
            "missing": sorted(set(declared) - set(usable)),
        }
    return out
