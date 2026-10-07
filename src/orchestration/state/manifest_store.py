"""Manifest and outcome persistence — append-only, immutable (OR-13, INV-005/006)."""

from __future__ import annotations

import json
import os
import tempfile
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
        _atomic_write(path, manifest.to_json_obj())
        return path

    def read(self, run_id: str) -> dict:
        return json.loads(self.path(run_id).read_text(encoding="utf-8"))

    def write_outcome(self, outcome) -> Path:
        path = self.root / outcome.run_id / "outcome.json"
        _atomic_write(path, outcome.to_json_obj())
        return path


def _atomic_write(path: Path, obj: dict) -> None:
    """OR-17 / INV-032 / AC-8.20 — ★ a killed run leaves the OLD file or the NEW one.

    ⚠ *Until 2026-10-06* both writes used `write_text`, so a kill mid-write left a
    truncated JSON that `read()` cannot parse and OR-13 would refuse to replace.
    Written to a temporary file in the same directory, flushed to disk, then
    `os.replace`d — the rename is atomic on POSIX. The temporary file never
    survives a failure. (D-07 has the same helper; it is not imported across the
    domain boundary, ST-3.)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, indent=2, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)   # noqa: PTH105 — the atomic step; AC-8.20 kills it here
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
