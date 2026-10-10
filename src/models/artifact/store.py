"""Artifact persistence — `.state/models/<artifact_id>/`, append-only.

★ `fit()` returned a `ModelArtifact` and **nothing wrote it**, so every run's
model died with the process and `_incumbent_model()` returned `None`. This is the
same shape as the fact ledger, the observation ledger and the two run stores.

```text
   .state/models/<artifact_id>/
       manifest.json        CT-4.1 — what the fit was pinned to
       estimator.pkl        the fitted thing
       features.json        the column order, separately readable
       evaluation.json      the walk-forward result the gates read
       promotion.json       written ONLY when every required gate says PASS
```

⚠ **The manifest is written even when the gates refuse.** A refused artifact is a
record — MT-17's *"a promotion with no evaluation is the gate skipped, not
passed"* cuts both ways, and a model that failed is the most useful thing to have
kept when the next one passes.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.recording.errors import AppendOnlyViolation

MANIFEST = "manifest.json"
ESTIMATOR = "estimator.pkl"
FEATURES = "features.json"
EVALUATION = "evaluation.json"
PROMOTION = "promotion.json"
RETIREMENT = "retirement.json"


class ArtifactStore:
    """★ **The manifest is written once; evaluations append; nothing is revised.**

    ⚠ `artifact_id` is derived from the manifest's own content, so a re-fit with
    any input changed produces a **new** id and cannot collide. A collision
    therefore means the *same* fit ran twice — which a reproducible pipeline
    should permit, so it is a no-op rather than an error.

    ★★ **The evaluation is not part of the id**, so the same model can be graded
    more than once — a gate wired later, a longer window. Those are *second
    verdicts on one model* and both belong in the record: they append as
    `evaluation-2.json`, `evaluation-3.json`. ⚠ Overwriting would let **a refusal
    be replaced by a pass with nothing saying so**, which is the shape OR-13
    forbids one domain over.
    """

    __slots__ = ("root",)

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def dir_for(self, artifact_id: str) -> Path:
        return self.root / artifact_id

    def write(self, artifact, *, evaluation=None) -> Path:
        """Persist the fit. ★ **Re-running an identical fit is a no-op, not an error.**

        ⚠ `artifact_id` is derived from the manifest, so the *same* fit always
        yields the *same* id — and re-running one is exactly what a reproducible
        pipeline should permit. What may never happen is a **changed** manifest
        under an existing id, and that cannot arise: a changed input changes the
        id.

        ★★ **A re-EVALUATION is appended, never overwritten.** The evaluation is
        not part of the id — the same fit graded again (a new gate wired, a
        longer window) is a *second* verdict on one model, and both belong in the
        record. Overwriting would let a refusal be replaced by a pass with
        nothing saying so.
        """
        target = self.dir_for(artifact.artifact_id)
        first = not (target / MANIFEST).is_file()
        target.mkdir(parents=True, exist_ok=True)

        if first:
            _write_json(target / MANIFEST, artifact.manifest.to_json_obj())
            _write_json(target / FEATURES, list(artifact.feature_names))
        if evaluation is not None:
            _write_json(target / self._next_evaluation(target), evaluation)
        if not first:
            return target

        # ⚠ Pickle is the estimator's own format and it is **not** the record.
        #   The manifest is; a pickle that fails to load leaves a readable
        #   account of what was fitted, which a pickle-only store would not.
        import pickle

        (target / ESTIMATOR).write_bytes(pickle.dumps(artifact.estimator))
        return target

    @staticmethod
    def _next_evaluation(target: Path) -> str:
        """`evaluation.json`, then `evaluation-2.json`, … — ★ append-only."""
        if not (target / EVALUATION).is_file():
            return EVALUATION
        index = 2
        while (target / f"evaluation-{index}.json").is_file():
            index += 1
        return f"evaluation-{index}.json"

    def record_promotion(self, record) -> Path:
        """★ Written **only** on a promotion — its absence is the refusal."""
        target = self.dir_for(record.artifact_id)
        target.mkdir(parents=True, exist_ok=True)
        path = target / PROMOTION
        if path.is_file():
            raise AppendOnlyViolation("promotion record", record.artifact_id)
        _write_json(path, record.to_json_obj())
        return path

    def retire(self, artifact_id: str, *, reason: str, at=None) -> Path:
        """★★ **Retirement is a TOMBSTONE, never a deletion.**

        ⚠ The obvious move is `rm -rf` the directory. This codebase forbids it
        everywhere else for one reason — **CT-4.3, RC-60, OR-13: a record that
        can be removed after the outcome is known is not evidence** — and a
        superseded model is exactly the record you want when the next one
        misbehaves. *"A refused model is a record"* cuts the same way for a
        retired one.

        ★ So the artifact stays on disk, keeps its manifest, its evaluations and
        its promotion, and gains a **reason it was stood down**. `promoted()`
        then skips it — the tombstone is what removes it from service, not its
        absence.

        ⚠ A reason is **required**: MT-36's argument, one level down —
        *retirement needs a reason recorded*, or a registry accumulates models
        nobody can account for.
        """
        from datetime import datetime, timezone

        from src.models.errors import ModelError

        if not reason or not reason.strip():
            raise ModelError(
                f"{artifact_id}: retirement needs a stated reason. ★ A model "
                f"stood down for no recorded cause is indistinguishable from one "
                f"stood down by accident (MT-36)")

        target = self.dir_for(artifact_id)
        if not (target / MANIFEST).is_file():
            raise ModelError(f"no artifact {artifact_id!r} to retire")
        path = target / RETIREMENT
        if path.is_file():
            raise AppendOnlyViolation("retirement record", artifact_id)

        _write_json(path, {
            "artifact_id": artifact_id,
            "retired_at": (at or datetime.now(timezone.utc)).isoformat(),
            "reason": reason,
        })
        return path

    def is_retired(self, artifact_id: str) -> bool:
        return (self.dir_for(artifact_id) / RETIREMENT).is_file()

    def read(self, artifact_id: str) -> dict:
        target = self.dir_for(artifact_id)
        if not target.is_dir():
            return {}
        out = {}
        for path in sorted(target.iterdir()):
            if path.suffix == ".json":
                out[path.name] = json.loads(path.read_text(encoding="utf-8"))
        return out

    def latest_evaluation(self, artifact_id: str) -> dict | None:
        """The most recent verdict. ⚠ Earlier ones stay on disk — *a refusal
        replaced by a pass with nothing saying so* is what the numbering
        prevents."""
        files = self.read(artifact_id)
        # ⚠ **Ordered by index, not lexically.** `sorted()` puts
        #   `evaluation-2.json` BEFORE `evaluation.json` — `-` (0x2D) sorts under
        #   `.` (0x2E) — so a lexical `[-1]` returns the FIRST verdict and
        #   reports a superseded refusal as the current one.
        indexed = [(_evaluation_index(n), n) for n in files
                   if n.startswith("evaluation")]
        return files[max(indexed)[1]] if indexed else None

    def artifact_ids(self) -> list:
        if not self.root.is_dir():
            return []
        return sorted(p.name for p in self.root.iterdir() if p.is_dir())

    def promoted(self, *, role: str, horizon_id: str) -> str | None:
        """The newest **promoted** artifact for a role and horizon, or `None`.

        ⚠ Reads `promotion.json`, never the manifest alone: **a fitted artifact
        is not a promoted one**, and treating the presence of a model as licence
        to score with it is precisely what MT-17 makes impossible.
        """
        best = None
        for artifact_id in self.artifact_ids():
            files = self.read(artifact_id)
            record = files.get(PROMOTION)
            manifest = files.get(MANIFEST) or {}
            if not record:
                continue
            # ★ A retired artifact keeps its promotion record — that promotion
            #   really happened — and is simply no longer served. ⚠ Deleting the
            #   record instead would make the history claim it never did.
            if RETIREMENT in files:
                continue
            if manifest.get("role") != role or manifest.get("horizon_id") != horizon_id:
                continue
            if best is None or record["promoted_at"] > best[1]:
                best = (artifact_id, record["promoted_at"])
        return best[0] if best else None

    # -- MT-67: the card's INFORMATIONAL ranker (a refused model, labelled) -- #

    CARD_INFORMATIONAL = "card_informational.json"

    def card_informational(self, *, role: str, horizon_id: str) -> dict | None:
        """The designated refused ranker for `(role, horizon)`, or `None` (MT-67)."""
        path = Path(self.root) / self.CARD_INFORMATIONAL
        if not path.is_file():
            return None
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("role") != role or record.get("horizon_id") != horizon_id:
            return None
        return record

    def designate_card_informational(self, record: dict) -> Path:
        """★ An explicit, revocable act — never `promotion.json` (MT-52, MT-67)."""
        path = Path(self.root) / self.CARD_INFORMATIONAL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=1, sort_keys=True), encoding="utf-8")
        return path

    def revoke_card_informational(self) -> bool:
        path = Path(self.root) / self.CARD_INFORMATIONAL
        if not path.is_file():
            return False
        path.unlink()
        return True

    def load_estimator(self, artifact_id: str):
        import pickle

        path = self.dir_for(artifact_id) / ESTIMATOR
        if not path.is_file():
            return None
        return pickle.loads(path.read_bytes())


def _evaluation_index(name: str) -> int:
    """`evaluation.json` → 1, `evaluation-7.json` → 7."""
    stem = name[: -len(".json")]
    return int(stem.split("-")[1]) if "-" in stem else 1


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str)
                    + "\n", encoding="utf-8")
