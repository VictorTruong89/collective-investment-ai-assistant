"""The B3 ranker — a declared deterministic rule (L3 BS-10, QA-121 as clarified).

★ **There is no model at B3, and QA-121 still binds.** `model_artifact_id` is
required because *"a nomination that cannot be traced to the model that made it
cannot be re-run"* (INV-2). A **content hash of the declared rule** satisfies
that exactly as a hashed model artifact does, so the field is populated rather
than nulled — and the hash changes the moment the rule does.

★ **The ranked quantity is DENORMALISED** (QA-58, QA-119):

```
    ranked_quantity  =  z_hat * sigma_hat * sqrt(h)
```

⚠ **Publishing only `z` would let a consumer rank on the normalised quantity**,
which is a systematic low-volatility tilt. `z` travels beside it so a reader can
see both, and QA-119 requires exactly that.

⚠ **At B3 `z_hat` is a WITHIN-TICKER (time-series) z-score, not a
cross-sectional one.** With one ticker there is no cross-section — the
cross-sectional sd is undefined at n = 1. The substitution is declared in the
`formula_id` and therefore in the hash, so a reader of a stored nomination can
tell which was used. **B4 replaces it with the model's ẑ.**
"""

from __future__ import annotations

import hashlib
import math

import numpy as np
import pandas as pd

FORMULA_ID = "rank.denormalised_within_ticker_z.v1"

#: Trailing window for the within-ticker standardisation, in sessions. Matches
#: `vol_21`'s window so the two halves of `z * sigma` are measured over the same
#: span — a POLICY CHOICE, and stated because a reader would otherwise have to
#: derive it (CN-1).
Z_WINDOW_SESSIONS = 21


def rule_id() -> str:
    """The content hash QA-121's `model_artifact_id` carries at B3.

    Hashes the **source of this module**, so any change to the ranking maths
    produces a different id. That is the property QA-121 asks for: re-runnability
    of a stored nomination, checkable rather than asserted.
    """
    src = __import__("pathlib").Path(__file__).read_bytes()
    return "sha256:" + hashlib.sha256(src).hexdigest()


def within_ticker_z(series: pd.Series, ticker: pd.Series, *,
                    window: int = Z_WINDOW_SESSIONS) -> pd.Series:
    """Trailing z-score of `series` within each ticker.

    ⚠ **No `fillna`.** A name with insufficient history scores `NaN` and is
    therefore not rankable — it is not "exactly average" (**PD-1**). Filling a
    z-score with 0.0 is the P5 violation with a friendly name, and it lets every
    data-poor name compete for a slot on that basis.
    """
    ordered_idx = series.index
    grouped = series.groupby(ticker, sort=True)
    mean = grouped.rolling(window, min_periods=window).mean().reset_index(level=0, drop=True)
    sd = grouped.rolling(window, min_periods=window).std(ddof=1).reset_index(level=0, drop=True)
    z = (series - mean.reindex(ordered_idx)) / sd.reindex(ordered_idx)
    # A zero trailing sd means the signal did not move: the z-score is undefined,
    # not infinite and not zero (DE-14's shape, one layer out).
    z[sd.reindex(ordered_idx) == 0] = np.nan
    return z.astype("float64")


def rank_candidates(panel: pd.DataFrame, *, as_of, horizon_days: int,
                    signal: str = "mom_21", vol: str = "vol_21") -> list[dict]:
    """One row per rankable ticker at `as_of`, ordered by `ranked_quantity`.

    Deterministic and stably ordered (**PD-20**): ties break on ticker, so the
    same panel yields the same ranking every time. *A ranking system with an
    unstable tie-break is not reproducible, and D-03's whole product is a
    ranking.*
    """
    if signal not in panel.columns or vol not in panel.columns:
        raise KeyError(
            f"rank_candidates needs {signal!r} and {vol!r} in the CT-2.2 panel; got "
            f"{sorted(panel.columns)}. D-03 ranks D-02's numbers and computes none "
            f"of its own (D-02 §1.2)"
        )
    ordered = panel.sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    ordered["_z"] = within_ticker_z(ordered[signal], ordered["ticker"])

    day = ordered[ordered["date"] == pd.Timestamp(as_of)]
    if not len(day):
        raise KeyError(
            f"no panel rows at as_of {as_of}. A nomination for a date the panel does "
            f"not cover would be a rank over nothing"
        )

    scale = math.sqrt(horizon_days)
    rows = []
    for _, r in day.iterrows():
        z, sigma = r["_z"], r[vol]
        if pd.isna(z) or pd.isna(sigma):
            # FE-27's shape: reported as unrankable, never silently dropped and
            # never scored as median. It simply cannot be ranked today.
            continue
        rows.append({"ticker": r["ticker"], "z": float(z),
                     "ranked_quantity": float(z) * float(sigma) * scale})

    rows.sort(key=lambda c: (-c["ranked_quantity"], c["ticker"]))
    for i, c in enumerate(rows, start=1):
        c["rank"] = i
    return rows
