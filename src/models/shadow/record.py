"""MT-65 — one shadow snapshot: the frozen model's ranking and the rule's, write-once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.models.shadow.trial import HORIZON_DAYS, ShadowError

SNAPSHOTS = "snapshots"


def assert_spacing(previous, as_of, sessions) -> None:
    """≥ 21 trading sessions after the previous snapshot — independent observations."""
    if previous is None:
        return
    ordered = sorted(sessions)
    if previous not in ordered or as_of not in ordered:
        raise ShadowError(f"cannot count sessions between {previous} and {as_of}: "
                          f"one of them is not a trading session in the price data")
    gap = ordered.index(as_of) - ordered.index(previous)
    if gap < HORIZON_DAYS:
        raise ShadowError(f"only {gap} trading sessions since the last snapshot "
                          f"({previous}); at least {HORIZON_DAYS} keep the observations "
                          f"independent (MT-65)")


def snapshot_date(sessions, requested=None):
    """The snapshot's date: `requested`, or the latest COMPLETED session in the data.

    ✏ *2026-10-09:* FMP's end-of-day history posts a day's bar only after that day
    ends, so "today" during market hours is not there yet. A snapshot dated T and
    recorded later is still knowable-at-T: every feature reads opens (and volume to
    T−1), fundamentals are filtered by filing date.
    """
    ordered = sorted(sessions)
    if not ordered:
        raise ShadowError("no price sessions fetched")
    if requested is None:
        return ordered[-1]
    if requested not in ordered:
        raise ShadowError(f"no end-of-day bar for {requested} yet (latest {ordered[-1]}) — FMP "
                          f"posts a day's bar after the close; record it then, or pass an "
                          f"earlier --as-of")
    return requested


def assert_out_of_sample(as_of, returns_seen_through) -> None:
    """MT-65 — a snapshot dated T predicts `open(T) → open(T+21)`; it is out of sample
    only if T is on or after the date through which the model saw returns.

    ⚠ *Found 2026-10-09 smoke-testing:* a snapshot at 2026-08-04 scored IC +0.35 —
    fit 4's labels ran through 2026-10-08, so it was grading its own homework.
    """
    from datetime import date as _date

    if not returns_seen_through:
        raise ShadowError("the frozen artifact does not record its training as_of — "
                          "cannot prove a snapshot is out of sample")
    seen = _date.fromisoformat(str(returns_seen_through)[:10])
    if as_of < seen:
        raise ShadowError(f"{as_of} is inside the frozen model's training window — it saw "
                          f"returns through {seen}; a snapshot must be dated on or after it "
                          f"(MT-65)")


def assert_contract(panel_hash: str, artifact_hash: str) -> None:
    """INV-4 — the panel must be the contract the artifact was fitted on."""
    if not panel_hash or panel_hash != artifact_hash:
        raise ShadowError(f"contract hash {panel_hash!r} ≠ the frozen artifact's "
                          f"{artifact_hash!r} — scoring would be on different features "
                          f"(INV-4, MT-51)")


def rankings(panel, *, as_of, estimator, feature_names, horizon_days: int = HORIZON_DAYS):
    """`(model, rule)` rankings at `as_of`, restricted to names BOTH can rank."""
    from src.models.infer.rank import rank_by_model
    from src.quant.signals.rank import rank_candidates

    model = rank_by_model(panel, as_of=as_of, horizon_days=horizon_days,
                          estimator=estimator, feature_names=feature_names)
    rule = rank_candidates(panel, as_of=as_of, horizon_days=horizon_days)
    common = {r["ticker"] for r in model} & {r["ticker"] for r in rule}
    model = [r for r in model if r["ticker"] in common]
    rule = [r for r in rule if r["ticker"] in common]
    for ranked in (model, rule):
        for position, row in enumerate(ranked, start=1):
            row["rank"] = position
    return model, rule


def write_snapshot(root, snapshot: dict) -> Path:
    """Write-once (MT-65). The content hash rides along so an edit is detectable."""
    folder = Path(root) / SNAPSHOTS
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{snapshot['as_of']}.json"
    if path.exists():
        raise ShadowError(f"{path} exists — a snapshot is write-once (MT-65)")
    body = json.dumps(snapshot, indent=1, sort_keys=True, default=str)
    payload = {**snapshot, "content_hash": "sha256:" + hashlib.sha256(body.encode()).hexdigest()}
    path.write_text(json.dumps(payload, indent=1, sort_keys=True, default=str), encoding="utf-8")
    return path


def snapshots(root) -> list:
    folder = Path(root) / SNAPSHOTS
    if not folder.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))]
