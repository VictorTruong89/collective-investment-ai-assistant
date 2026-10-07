"""MT-52 / AC-4.34 — promote a trained model, by the fund manager's explicit approval.

    python -m src.models.promote <artifact_id>             # show the gate report; change nothing
    python -m src.models.promote <artifact_id> --approve   # promote it — only if every gate PASSed

★ **Why it exists** (Victor, 2026-10-06): *training should hold promotion until I've reviewed it.*
A training run writes the artifact and its gate report marked `pending` (`decide_promotion`);
this is the only other way `promotion.json` is written, and it is a human act.

⚠ **No override.** `--approve` still goes through `promote()`, which refuses unless every
required D-03 gate says PASS and a BacktestResult id exists (MT-17, MT-19). Review can decline
a passing model; it can never pass a failing one.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


def _models_root() -> Path:
    return Path(os.environ.get("PIPELINE_STATE_DIR", ".state")) / "models"


def _artifact_view(artifact_id: str, manifest: dict):
    """What `promote()` reads, rebuilt from `manifest.json` — the artifact itself is not reloaded."""
    contract = manifest.get("feature_contract") or {}
    return SimpleNamespace(
        artifact_id=artifact_id,
        manifest=SimpleNamespace(
            horizon_set_version=manifest.get("horizon_set_version"),
            feature_contract=SimpleNamespace(version=contract.get("version"))))


def _report(artifact_id: str, files: dict, evaluation: dict) -> None:
    manifest = files.get("manifest.json") or {}
    review = evaluation.get("review") or {}
    print(f"artifact {artifact_id}")
    print(f"  role {manifest.get('role')} · horizon {manifest.get('horizon_id')} · "
          f"contract {(manifest.get('feature_contract') or {}).get('name')}"
          f"@v{(manifest.get('feature_contract') or {}).get('version')}")
    print(f"  review: {review.get('status', 'unknown')}"
          f"{' · already PROMOTED' if 'promotion.json' in files else ''}")
    for gate_id, gate in (evaluation.get("gates") or {}).items():
        print(f"  {gate_id:16s} {gate.get('verdict')}  — {gate.get('why', '')}")
    survivorship = evaluation.get("survivorship")
    if survivorship:
        print(f"  ⚠ {survivorship}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="src.models.promote",
        description="Show a trained model's gate report, or promote it on approval (MT-52).")
    parser.add_argument("artifact_id")
    parser.add_argument("--approve", action="store_true",
                        help="promote it — refused unless every required gate PASSed")
    parser.add_argument("--models", default=None,
                        help="model store (default: $PIPELINE_STATE_DIR/models, else .state/models)")
    args = parser.parse_args(argv)

    from src.models.artifact.store import ArtifactStore
    from src.models.governance.promotion import promote

    store = ArtifactStore(args.models or _models_root())
    files = store.read(args.artifact_id)
    evaluation = store.latest_evaluation(args.artifact_id) if files else None
    if not files or evaluation is None:
        print(f"⛔ no artifact {args.artifact_id} with an evaluation in {store.root}",
              file=sys.stderr)
        return 1

    _report(args.artifact_id, files, evaluation)
    if not args.approve:
        print(f"\nNothing changed. To promote after review:\n"
              f"  python -m src.models.promote {args.artifact_id} --approve")
        return 0

    verdicts = {g: (v or {}).get("verdict") for g, v in (evaluation.get("gates") or {}).items()}
    try:
        record = promote(_artifact_view(args.artifact_id, files.get("manifest.json") or {}),
                         backtest_result_id=evaluation.get("backtest_result_id", ""),
                         gate_outcomes=verdicts,
                         promoted_by="fund manager review (src.models.promote --approve)",
                         at=datetime.now(timezone.utc))
        store.record_promotion(record)
    except Exception as exc:     # noqa: BLE001 — MT-17's refusal (or an append-only clash), named
        print(f"⛔ REFUSED — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"\n★ PROMOTED {args.artifact_id} — the next daily run scores with it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
