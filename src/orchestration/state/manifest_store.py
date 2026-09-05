"""Manifest and outcome persistence — append-only, immutable (OR-13, INV-005/006)."""

from __future__ import annotations

import json
from pathlib import Path

from src.orchestration.contracts.manifest import RunManifest


class ManifestImmutableError(Exception):
    """OR-13 / AC-8.14 — a written manifest cannot be mutated.

    ⚠ A rerun creates a NEW manifest; it never edits the old one. Editing it
    would let a run's recorded inputs be adjusted to match its outputs, which is
    the one thing a reproducibility record must make impossible.
    """


class ManifestStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def path(self, run_id: str) -> Path:
        return self.root / run_id / "manifest.json"

    def write(self, manifest: RunManifest) -> Path:
        path = self.path(manifest.run_id)
        if path.exists():
            raise ManifestImmutableError(
                f"a manifest already exists at {path}. A rerun creates a new manifest; "
                f"it never edits the old one (OR-13, INV-005/006)"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(manifest.to_json_obj(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def read(self, run_id: str) -> dict:
        return json.loads(self.path(run_id).read_text(encoding="utf-8"))

    def write_outcome(self, outcome) -> Path:
        path = self.root / outcome.run_id / "outcome.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(outcome.to_json_obj(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path
