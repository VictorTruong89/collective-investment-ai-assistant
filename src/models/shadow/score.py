"""MT-66 — grade matured snapshots, once each, on adjusted open-to-open returns."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.models.shadow.trial import HORIZON_DAYS

SCORES = "scores.jsonl"


def realised_returns(prices: pd.DataFrame, as_of, *, horizon_days: int = HORIZON_DAYS):
    """`{ticker: open(T+h)/open(T) − 1}`, or `None` if `T+h` has not happened yet.

    `prices` is a CT-7.1 panel adjusted with refreshed events (DE-78) — a split inside
    the 21 days would otherwise read as a crash.
    """
    frame = prices.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    sessions = sorted(frame["date"].dt.date.unique())
    if as_of not in sessions:
        return None
    end_index = sessions.index(as_of) + horizon_days
    if end_index >= len(sessions):
        return None
    start, end = pd.Timestamp(as_of), pd.Timestamp(sessions[end_index])
    wide = frame[frame["date"].isin([start, end])].pivot_table(
        index="ticker", columns="date", values="adj_open_minor", aggfunc="last")
    if start not in wide.columns or end not in wide.columns:
        return None
    return (wide[end] / wide[start] - 1.0).dropna()


def snapshot_ic(ranking, realised: pd.Series):
    """Spearman of the ranking (rank 1 = best) against the realised return."""
    order = pd.Series({r["ticker"]: -r["rank"] for r in ranking})
    both = pd.concat([order.rename("score"), realised.rename("value")], axis=1).dropna()
    if len(both) < 3:
        return None
    return float(both["score"].corr(both["value"], method="spearman"))


def scored(root) -> list:
    path = Path(root) / SCORES
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_score(root, row: dict) -> None:
    """Write-once per snapshot date — a re-score never overwrites (MT-66)."""
    if any(r["as_of"] == row["as_of"] for r in scored(root)):
        return
    with (Path(root) / SCORES).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
