"""D-02 CT-2.3 — the label set. FE-11, FE-12, FE-31.

⚠ **Labels are never in a panel** (FE-11). `build_labels` is a separate call so
that a feature panel cannot accidentally carry the answer — the single most
common source of leakage in a tabular pipeline.

★ **`decision_anchor` is a field of the label set, not a convention** (FE-31,
D-03 QA-72). ⚠ *A label set whose anchor is not on the row cannot be compared
with one built on a different anchor, and nothing would notice.*
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.data_engine.contracts.schema import as_date32

#: FE-31 — the three anchors, and the reason the field exists.
OPEN, CLOSE, ARRIVAL = "open", "close", "arrival"
ANCHORS = (OPEN, CLOSE, ARRIVAL)

#: CT-2.3's columns, in order.
LABEL_COLUMNS = ("ticker", "date", "horizon_days", "label_def_id",
                 "decision_anchor", "value", "available_at")


@dataclass(frozen=True, slots=True)
class LabelDef:
    """What is being predicted, named so an artifact can cite it (MT-48)."""

    label_def_id: str
    horizon_days: int
    decision_anchor: str
    #: ★ D-03 §5.9's form: the forward return between two anchor prices.
    #: `vol_normalised` divides by trailing volatility — a different label, and
    #: therefore a different `label_def_id`.
    vol_normalised: bool = False

    def __post_init__(self) -> None:
        from src.feature_engineer.errors import FeatureError

        if self.decision_anchor not in ANCHORS:
            raise FeatureError(
                f"decision_anchor {self.decision_anchor!r} is not one of "
                f"{ANCHORS}. ★ It is a declared property of the label set "
                f"(FE-31, QA-72), not a convention")
        if self.horizon_days <= 0:
            raise FeatureError(
                f"{self.label_def_id}: horizon_days must be positive")

    def to_json_obj(self) -> dict:
        return {"label_def_id": self.label_def_id,
                "horizon_days": self.horizon_days,
                "decision_anchor": self.decision_anchor,
                "vol_normalised": self.vol_normalised}


#: HorizonSet v1's selection leg — ★ the only horizon that may nominate.
FWD_RETURN_21D_OPEN = LabelDef("fwd_return_21d_open", 21, OPEN)
#: The timing leg — may delay or veto, never nominate (MT-31).
FWD_RETURN_5D_OPEN = LabelDef("fwd_return_5d_open", 5, OPEN)


def build_labels(*, label_def: LabelDef, price_panel: pd.DataFrame,
                 price_column: str | None = None) -> pd.DataFrame:
    """CT-2.3 — ★ **`available_at` is MATERIALISED, never computed** (FE-12).

    ⚠ *So INV-1 is checkable by comparison rather than by trusting arithmetic at
    every call site.* A consumer asks *"was this knowable at `as_of`?"* by
    reading a column, not by re-deriving a date.

    ⚠ **The anchor selects the column.** An `open`-anchored label built from
    `close` is D-08 OR-35's full-session drift, introduced one domain earlier —
    and it is **invisible in backtest**, because the backtest shares it.
    """
    from src.feature_engineer.errors import FeatureError

    column = price_column or _anchor_column(label_def.decision_anchor)
    if column not in price_panel.columns:
        raise FeatureError(
            f"{label_def.label_def_id} is {label_def.decision_anchor!r}-anchored "
            f"and the panel carries no {column!r} column. ★ The anchor selects "
            f"the column; substituting another is a full session of drift on "
            f"every row (FE-31, D-08 OR-35)")

    frames = []
    for ticker, group in price_panel.sort_values("date").groupby("ticker",
                                                                sort=True):
        forward = group[column].shift(-label_def.horizon_days)
        value = (forward - group[column]) / group[column]
        if label_def.vol_normalised:
            volatility = group[column].pct_change().rolling(21).std()
            value = value / volatility.replace(0.0, pd.NA)
        available = group["date"].shift(-label_def.horizon_days)
        frames.append(pd.DataFrame({
            "ticker": ticker, "date": group["date"],
            "horizon_days": label_def.horizon_days,
            "label_def_id": label_def.label_def_id,
            "decision_anchor": label_def.decision_anchor,
            "value": value.astype("float64"),
            # ⚠ FE-12 — the real trading date h sessions ahead, not
            #   `date + horizon_days`, which would land on weekends.
            "available_at": available,
        }))
    labels = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=list(LABEL_COLUMNS))
    labels = labels.dropna(subset=["value", "available_at"]).reset_index(drop=True)
    labels["date"] = as_date32(labels["date"])
    labels["available_at"] = as_date32(labels["available_at"])
    return labels[list(LABEL_COLUMNS)]


#: FE-42 — the suffix a within-day Gaussian-rank target adds to its label id.
XS_GAUSS = "xs_gauss"


def cross_sectional_gauss(labels: pd.DataFrame) -> pd.DataFrame:
    """FE-42 / AC-2.49 — each date's returns as centred normal scores by rank.

    `ẑ = Φ⁻¹((r − ½) / n)`, `r` the average-tie rank among the date's `n` names.
    ★ A TARGET, not a label for evaluation: realised IC, the simulation and the
    gates keep the raw return (MT-59). ★ Gaussian, not a raw percentile,
    because inference publishes `ẑ · σ̂ · √h` (QA-58) — a percentile in (0, 1)
    is all positive and σ̂ would then rank mostly by volatility.
    ⚠ A date with fewer than 3 names gives no target: a rank over two is ±1.
    """
    from statistics import NormalDist

    import numpy as np

    out = labels.copy()
    grouped = out.groupby("date", sort=False)["value"]
    rank = grouped.rank(method="average")
    count = grouped.transform("count")
    out = out[count >= 3].copy()
    quantile = ((rank[count >= 3] - 0.5) / count[count >= 3]).to_numpy(dtype="float64")
    out["value"] = np.vectorize(NormalDist().inv_cdf, otypes=[float])(quantile) \
        if len(quantile) else quantile
    out["label_def_id"] = out["label_def_id"].astype(str) + f".{XS_GAUSS}"
    return out.reset_index(drop=True)


def _anchor_column(anchor: str) -> str:
    return {OPEN: "adj_open_minor", CLOSE: "adj_close_minor",
            ARRIVAL: "adj_open_minor"}[anchor]


def assert_no_lookahead(labels: pd.DataFrame, *, as_of: date) -> pd.DataFrame:
    """INV-1 / FE-12 — ★ **by comparison, not by arithmetic.**

    A label whose `available_at` is after `as_of` was not knowable then, and a
    training set containing one is a look-ahead — the class this project keeps
    finding (`_cumulative_fys` 41.5 %, FMP TTM 71 %).
    """
    from src.feature_engineer.errors import FeatureError

    cut = as_date32(pd.Series([as_of])).iloc[0]
    leaked = labels[labels["available_at"] > cut]
    if len(leaked):
        raise FeatureError(
            f"{len(leaked)} label(s) have available_at after {as_of} — they "
            f"were not knowable then (INV-1, FE-12). Earliest: "
            f"{leaked['available_at'].min()}")
    return labels


def assert_single_anchor(labels: pd.DataFrame) -> str:
    """FE-31 — ⚠ *a mixed-anchor panel is a defect*, and QA-82's dual-anchor
    evaluation is distinguished by the field, not by a filename."""
    from src.feature_engineer.errors import FeatureError

    anchors = set(labels["decision_anchor"].unique())
    if len(anchors) > 1:
        raise FeatureError(
            f"the label set mixes anchors {sorted(anchors)!r}. They are not "
            f"comparable, and nothing downstream would notice (FE-31, QA-72)")
    return anchors.pop() if anchors else ""
