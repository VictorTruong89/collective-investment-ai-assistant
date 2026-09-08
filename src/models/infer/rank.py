"""Rank by a promoted model's scores — **D-04 inference**, consumed by D-03.

⚠ *This module began in `src/quant/signals/` and **QA-21 moved it***: D-03 may
not import from `src.models`, and the first draft reached for
`models.errors.ParityError`. ★ The rule is right and it settles the ownership —
**scoring with a fitted artifact is D-04's inference path**; D-03 owns the
`CT-3.4 Nomination` that wraps the resulting scores, and orchestration joins the
two. A domain that both fits and ranks would be the D-18 shape.


★ A model was promoted on 2026-08-27 and **the daily card was still ranked by
`z(mom_21) × vol_21 × √21`**: `_incumbent_model()` loaded the artifact only so
OR-44's precondition could read its anchor, and nothing scored with it.

```text
   promoted artifact -> check_parity(panel)  -> estimator.predict
                     -> denormalise to ranked_quantity (QA-58)
```

⚠⚠ **Parity is checked BEFORE scoring, over the whole batch** (MT-6/MT-8). The
model declares `price_and_fundamental@v1` with **59** features; the B3 daily
panel carried **2**. ★ Scoring anyway is not a smaller model — it is **D-17**,
the defect the specs cite repeatedly: `model_bundle.py:80`'s
`[c for c in feature_names if c in df.columns]` is *one word away from correct*,
and that word is the whole of it.

★ **The output is `ranked_quantity`, not the raw score** (QA-58, QA-119). D-03
publishes the **denormalised** quantity `ẑ · σ̂ · √h`; publishing only the
normalised score would let a consumer rank on it, which is the low-vol tilt QA-58
exists to remove.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


#: ★ The ranker's identity when a model produced the scores. ⚠ It is the
#: artifact's own content hash, so `CT-3.4.model_artifact_id` names the exact
#: fitted thing rather than a family or a version string (QA-121).
def model_id(artifact_id: str) -> str:
    return artifact_id


#: ★ The volatility QA-58's denormalisation multiplies by, in preference order.
#: ⚠ **`vol_21` belongs to `b3_minimal`; `vol_20d` to `price_ohlcv`** — a model
#: fitted on the second and denormalised with a column only the first defines
#: fails with a `TypeError` deep inside pandas rather than saying so.
VOL_COLUMNS = ("vol_20d", "vol_21", "vol_10d")


def _volatility(panel: pd.DataFrame, requested: str | None) -> pd.Series:
    """The σ̂ for QA-58, or raise naming what was looked for.

    ⚠ **Never substituted with 1.0.** A denormalisation that quietly drops σ̂
    publishes the *normalised* score as though it were the denormalised one,
    which is precisely the low-vol tilt QA-58 exists to remove.
    """
    from src.quant.errors import QuantError

    for column in ([requested] if requested else []) + list(VOL_COLUMNS):
        if column and column in panel.columns:
            return pd.to_numeric(panel[column], errors="coerce")
    raise QuantError(
        f"the panel carries no volatility column from {VOL_COLUMNS!r}, so "
        f"QA-58's ranked_quantity cannot be denormalised. ★ Publishing the "
        f"normalised score instead would be the low-vol tilt QA-58 removes")


def rank_by_model(panel: pd.DataFrame, *, as_of, horizon_days: int, estimator,
                  feature_names, vol_column: str | None = None) -> list:
    """One row per rankable ticker at `as_of`, ordered by `ranked_quantity`.

    ⚠ **A name whose features are incomplete is reported unrankable, never
    scored on what is present.** FE-27's shape: it is not dropped silently and
    not scored as the median — *it simply cannot be ranked today*.
    """
    from src.quant.errors import QuantError

    features = list(feature_names)
    missing = [c for c in features if c not in panel.columns]
    if missing:
        raise QuantError(
            f"the panel lacks {missing[:5]!r}{'…' if len(missing) > 5 else ''} "
            f"({len(missing)} of {len(features)}). ★ A model never narrows to "
            f"what is present — that is D-17, and it scored an arbitrary frame")

    day = panel[pd.to_datetime(panel["date"]).dt.date == as_of]
    if not len(day):
        raise QuantError(
            f"no panel rows at as_of {as_of}. A nomination for a date the panel "
            f"does not cover would be a rank over nothing")

    scored = day.copy()
    scored["_score"] = np.asarray(estimator.predict(day[features]), dtype="float64")

    # ★ QA-58 — denormalise. `σ̂` is D-02's, never recomputed here (FE-4).
    sigma = _volatility(scored, vol_column)
    scale = math.sqrt(horizon_days)
    rows = []
    for (_index, row), sd in zip(scored.iterrows(), sigma):
        score = row["_score"]
        if pd.isna(score) or pd.isna(sd):
            continue                        # ⚠ FE-27 — unrankable, not median
        rows.append({"ticker": row["ticker"], "z": float(score),
                     "ranked_quantity": float(score) * float(sd) * scale})

    # PD-20 — ties break on ticker, so the same panel yields the same ranking.
    rows.sort(key=lambda c: (-c["ranked_quantity"], c["ticker"]))
    for position, candidate in enumerate(rows, start=1):
        candidate["rank"] = position
    return rows


def assert_population_parity(artifact, panel, *, tolerance: float = 0.5) -> str:
    """★★ **AB-4 — the cross-section the model was FITTED on versus this one.**

    ⚠ `check_parity` compares the feature **contract**; it does not look at how
    many names are in the cross-section. But `rank_ret_5d`, `rank_vol_20d` and
    every `*_sector_z` are **defined by the population they are computed in** —
    *a percentile among 497 names is not a percentile among 130*. A model fitted
    on one and applied to the other is being fed a differently-scaled input
    under an identical column name, which is **INV-4** and is invisible to a
    contract check.

    ⚠ **Raises rather than warning.** A warn-and-continue here is
    `check_parity`'s own rule ignored one level down — *a check that lets the
    batch through has not checked it*.
    """
    from src.models.errors import ParityError

    # ★ Accepts the artifact or the shim's dict — the check belongs at the
    #   inference seam, and the seam holds a dict.
    trained = (artifact.get("training_names") if isinstance(artifact, dict)
               else getattr(artifact.manifest, "training_names", None))
    live = int(panel["ticker"].nunique())

    if not trained:
        # ⚠⚠ **Returned, never swallowed.** An artifact fitted before
        #   `training_names` existed cannot have this checked — and *"could not
        #   check"* must not read like *"checked and fine"*. The caller prints
        #   it; silence here is the shape FE-14 refuses one domain over.
        return (f"UNCHECKED: the artifact declares no training_names, so the "
                f"{live}-name cross-section cannot be compared to the one it "
                f"was fitted on (AB-4). ★ The next fit records it")

    ratio = min(trained, live) / max(trained, live)
    if ratio < tolerance:
        artifact_id = (artifact.get("artifact_id", "<artifact>")
                       if isinstance(artifact, dict) else artifact.artifact_id)
        raise ParityError(
            artifact_id,
            f"fitted on {trained} names and this panel carries {live} — a ratio "
            f"of {ratio:.2f}. ★ Rank and sector-z features are defined by their "
            f"population, so the same column means a different thing (AB-4). "
            f"A contract check cannot see this")
    return f"OK: fitted on {trained}, scoring {live} (ratio {ratio:.2f})"
