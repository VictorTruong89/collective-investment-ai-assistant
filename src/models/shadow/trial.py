"""MT-64 / MT-66 — the trial record and its pre-registered verdict."""

from __future__ import annotations

import json
import math
from datetime import date, datetime, timezone
from pathlib import Path

TRIAL = "trial.json"
HORIZON_DAYS = 21
MIN_LIVE_FOR_ALARM = 6
T_BAR = 3.0

#: ★★ Pre-registered 2026-10-09 (MT-66). Changing this after the first live
#: observation would be choosing the answer — it is copied into trial.json once.
CRITERION = (
    "Pool the live monthly rank ICs with the frozen artifact's historical walk-forward "
    "(dates/21 independent months; per-month sd implied by its realised Newey-West SE). "
    "Evidence bar met when the pooled t >= 3. From 6 live observations, a leakage alarm "
    "fires if the live mean IC is below the historical mean by more than 2 live standard "
    "errors (per-month sd from history). Meeting the bar does not promote: promotion stays "
    "`python -m src.models.promote <id> --approve` (MT-52).")

COMPARATOR = "rule: z(mom_21)·vol_21·√21 — the card's momentum rule (recorded, not judged)"


class ShadowError(RuntimeError):
    """A shadow-trial refusal — named, never a fallback."""


def start_trial(root, *, artifact_id: str, store, today: date | None = None) -> dict:
    """MT-64 — freeze the artifact, its history and the criterion. ★ Once only."""
    root = Path(root)
    path = root / TRIAL
    if path.exists():
        raise ShadowError(f"a shadow trial already exists at {path} — a trial is not "
                          f"restarted to reset its record (MT-64)")
    files = store.read(artifact_id)
    walk = (files.get("evaluation.json") or {}).get("walk_forward") or {}
    history = {k: walk.get(k) for k in ("mean_ic", "realised_se", "dates")}
    if any(v is None for v in history.values()):
        raise ShadowError(f"{artifact_id} carries no walk-forward measurement "
                          f"(evaluation.json `walk_forward`) — nothing to pool with (MT-66)")
    manifest = files.get("manifest.json") or {}
    trial = {
        "artifact_id": artifact_id,
        "started": (today or datetime.now(timezone.utc).date()).isoformat(),
        "contract_hash": (manifest.get("feature_contract") or {}).get("content_hash"),
        "label_def_id": manifest.get("label_def_id"),
        # ★ MT-65 — the last label's forward window ends at the training as_of: the
        #   model has SEEN returns through it, so no snapshot may predate it.
        "returns_seen_through": (manifest.get("training_window") or {}).get("as_of"),
        "features": list(files.get("features.json") or []),
        "history": history,
        "horizon_days": HORIZON_DAYS,
        "comparator": COMPARATOR,
        "criterion": CRITERION,
    }
    root.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trial, indent=1, sort_keys=True), encoding="utf-8")
    return trial


def load_trial(root) -> dict:
    path = Path(root) / TRIAL
    if not path.exists():
        raise ShadowError(f"no shadow trial at {path} — start one: "
                          f"`python -m src.models.shadow start <artifact_id>`")
    return json.loads(path.read_text(encoding="utf-8"))


def pooled_verdict(history: dict, live_ics) -> dict:
    """MT-66 / AC-4.48 — the pre-registered formula, nothing else."""
    live = [float(x) for x in live_ics if x is not None and not math.isnan(x)]
    n_h = float(history["dates"]) / HORIZON_DAYS
    sd = float(history["realised_se"]) * math.sqrt(n_h)      # per independent month
    n_l = len(live)
    live_mean = sum(live) / n_l if n_l else None
    pooled = (n_h * float(history["mean_ic"]) + (sum(live) if n_l else 0.0)) / (n_h + n_l)
    se = sd / math.sqrt(n_h + n_l)
    t = pooled / se if se > 0 else None
    alarm = None
    if n_l >= MIN_LIVE_FOR_ALARM:
        alarm = live_mean < float(history["mean_ic"]) - 2 * sd / math.sqrt(n_l)
    return {"live_n": n_l, "live_mean_ic": live_mean,
            "historical_months": round(n_h, 2), "historical_mean_ic": history["mean_ic"],
            "pooled_mean_ic": pooled, "pooled_se": se, "pooled_t": t,
            "bar_met": bool(t is not None and t >= T_BAR), "leakage_alarm": alarm}
