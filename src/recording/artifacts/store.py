"""CT-11.7 — one directory per run, append-only. **RC-59, RC-60, RC-61.**

★★ **RC-33 has required this since v0.5.0 and nothing implemented it.**
`ManifestStore` and `JournalStore` were both built and **neither was ever
called**: every manifest, recommendation, card and thesis evaporated when the
process exited.

⚠ Two consequences, and the second is the larger one:

  * **P6 is constitutional and was unmet** — *anything sent to the user must be
    viewable later without depending on a live server*.
  * **Every measurement in these specs needs run history, and there was none.**
    RM-2/RM-3's base rates, DN-17's veto rate, DN-29's liveness monitor and
    D-01 §7.4's monitors are all specified and none of them could be computed.

★ **A directory per run, not a row per run** (CT-11.7): the renderings are the
part P6 is about, and they are documents. `runs.parquet` is the tabular view a
measurement wants, **derived from the directories and rebuildable from them** —
a convenience, never the record.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.recording.errors import AppendOnlyViolation

#: Files a run directory may hold. ⚠ Named rather than globbed so that a typo
#: in a caller creates a *missing* file rather than a silently new kind of one.
MANIFEST = "manifest.json"
OUTCOME = "outcome.json"
RECOMMENDATION = "recommendation.json"
THESIS = "thesis.json"
DELIVERY = "delivery.json"      # RC-63

#: The index. ★ Rebuildable — see `rebuild_index`.
INDEX = "runs.parquet"

#: ⚠ Statuses that must reach the index verbatim. **A failed run is a record,
#: not an absence** (RC-33, OR-19) — an index holding only successes would make
#: every base rate measure the wrong population.
TERMINAL_STATES = ("SUCCESS", "INCOMPLETE", "BLOCKED_PRECONDITION", "FAILED")


class RunArtifactStore:
    """`.state/runs/<run_id>/…` — ★ **written once, never revised** (RC-60)."""

    __slots__ = ("root",)

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def dir_for(self, run_id: str) -> Path:
        return self.root / run_id

    # -- write -------------------------------------------------------------- #

    def write_run(self, *, run_id: str, manifest=None, outcome=None,
                  recommendation=None, thesis=None, renderings=None,
                  nomination=None) -> Path:
        """Persist one run. ⚠ **A second write to the same `run_id` raises.**

        ★ RC-60 / OR-13: *a rerun creates a new run_id; it never edits the old
        one.* Overwriting would let a run's recorded inputs be adjusted to match
        its outputs — and the temptation is highest on the record that says a
        verdict was wrong.

        ★★ **RC-62 — `nomination` is FOLDED INTO `recommendation.json`.** ⚠ It
        is composed here, at write time, so **D-12's `Recommendation` class does
        not gain D-03's fields**: one file for the reader, two independent
        contracts for the code. The reader gaining a file is not a reason for
        the writer to gain a dependency.
        """
        target = self.dir_for(run_id)
        if target.exists() and any(target.iterdir()):
            raise AppendOnlyViolation("run artifact", run_id)
        target.mkdir(parents=True, exist_ok=True)

        for name, value in ((MANIFEST, manifest), (OUTCOME, outcome),
                            (RECOMMENDATION, _fold(recommendation, nomination)),
                            (THESIS, thesis)):
            if value is not None:
                _write_json(target / name, _as_json(value))
        for name, blob in (renderings or {}).items():
            path = target / name
            path.write_bytes(blob if isinstance(blob, bytes)
                             else str(blob).encode("utf-8"))
        return target

    # -- read --------------------------------------------------------------- #

    def read_run(self, run_id: str) -> dict:
        """Everything the run left, keyed by file name."""
        target = self.dir_for(run_id)
        if not target.is_dir():
            return {}
        out: dict = {}
        for path in sorted(target.iterdir()):
            if not path.is_file():
                continue                       # ★ RC-69 — a folder is not a file of the run
            if path.suffix == ".json":
                out[path.name] = json.loads(path.read_text(encoding="utf-8"))
            else:
                out[path.name] = path.read_text(encoding="utf-8")
        return out

    def run_ids(self) -> list:
        """Every run, oldest first. ⚠ `run_id` begins with an ISO timestamp, so
        lexical order **is** chronological — see `CT-8.1`.

        ★ RC-69 (`DX-173`) — only a directory holding a CT-11.7 file is a run.
        The thesis runners' traces share this root and are not runs.
        """
        if not self.root.is_dir():
            return []
        return sorted(p.name for p in self.root.iterdir() if p.is_dir()
                      and ((p / MANIFEST).is_file() or (p / OUTCOME).is_file()))


def _fold(recommendation, nomination):
    """RC-62 — the recommendation with D-03's nomination under `nomination`.

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  MEASURED 2026-08-27 on a complete run directory:                 ║
    ║    $ grep -rl "85b75744" .state/runs/<run_id>/   →  nothing       ║
    ║                                                                  ║
    ║  The record could not name the model that produced the pick.      ║
    ║  QA-121: a nomination that cannot be traced to what produced it   ║
    ║  cannot be re-run (INV-2).                                        ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ★ It also carries `excluded[]` — **QA-125**'s visible half. Without it a
    reader cannot tell a name that was *beaten* from one that was *barred*.
    """
    if nomination is None:
        return recommendation
    if recommendation is None:
        # ⚠ A nomination with no recommendation is a run that ranked and did not
        #   decide. That is a real state (D-12 blocked), and dropping the
        #   nomination would erase the only evidence the ranking happened.
        return {"nomination": _as_json(nomination)}
    payload = dict(_as_json(recommendation))
    payload["nomination"] = _as_json(nomination)
    return payload


def record_delivery(run_id: str, *, root, delivery) -> Path:
    """RC-63 — `delivery.json` beside the run it delivered.

    ⚠ **Absence means NOT DELIVERED, never unknown** (DE-35). A run that did not
    deliver writes no file — an empty one, or an `outcome: ""` placeholder,
    would make the two indistinguishable.

    ★ Written by **D-11** from the `Delivery` **D-09** returns: *D-09 delivers,
    D-11 records, D-08 wires* — and no domain does two of the three.
    """
    target = RunArtifactStore(root).dir_for(run_id)
    if not target.is_dir():
        raise AppendOnlyViolation("delivery for an unrecorded run", run_id)
    path = target / DELIVERY
    if path.exists():
        # ★ RC-60 — a re-send is a new delivery_id, never a rewritten record.
        raise AppendOnlyViolation("delivery record", run_id)
    _write_json(path, _as_json(delivery))
    return path


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str)
                    + "\n", encoding="utf-8")


def _as_json(value):
    """Accept a contract object or a plain dict — ★ D-11 stores what it is
    handed and normalises nothing (CT-11.1's rule, one contract out)."""
    return value.to_json_obj() if hasattr(value, "to_json_obj") else value


# --------------------------------------------------------------------------- #
# RC-61 — the thesis cache, keyed by bundle_hash
# --------------------------------------------------------------------------- #

def latest_thesis_for(bundle_hash: str, *, root) -> dict | None:
    """The most recent stored thesis for this exact evidence set, or `None`.

    ★★ **RC-61.** Three Opus passes measured **$1.34**; a daily run on an
    unchanged filing set would pay it again for evidence that did not move.

    ⚠ **The obvious objection is wrong and worth stating:** *does reusing a
    thesis destroy RM-1's variance measurement?* ★ **No — RM-1's k runs happen
    INSIDE one authoring event** (`author_thesis` calls the author k times over
    one bundle), and **GW-8 sets `temperature = 0`**, so cross-run sampling
    variance is not the measurement — RA-61's perturbation probe replaced the
    sampling probe in v0.4.0.

    ★ Reuse is the **caller's** decision, never the store's: every authored
    thesis is kept, and a forced re-author is always available.
    """
    store = RunArtifactStore(root)
    for run_id in reversed(store.run_ids()):
        path = store.dir_for(run_id) / THESIS
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("bundle_hash") == bundle_hash:
            return payload
    return None


# --------------------------------------------------------------------------- #
# The graph's entry point — D-08 invokes this by dotted name (OR-2, OR-48)
# --------------------------------------------------------------------------- #

def record_run(*, run_id: str, root, manifest=None, outcome=None,
               recommendation=None, thesis=None, renderings=None,
               status: str = "SUCCESS", as_of=None, nomination=None) -> str:
    """Persist the run and refresh the index. Returns the directory written.

    ⚠ **Called for a BLOCKED or INCOMPLETE run too** (RC-59, RC-33): *a failed
    run is a record, not an absence*, and an index of successes only would make
    every base rate measure the wrong population.
    """
    store = RunArtifactStore(root)
    target = store.write_run(run_id=run_id, manifest=manifest, outcome=outcome,
                             recommendation=recommendation, thesis=thesis,
                             renderings=renderings, nomination=nomination)
    rebuild_index(root)
    return str(target)


def rebuild_index(root) -> object:
    """`runs.parquet` from the run directories — ★ **the index is derived.**

    CT-11.7: *a convenience, never the record.* Rebuilding from the directories
    is what makes that claim checkable rather than asserted — and it means a
    corrupt or deleted index costs nothing.
    """
    import pandas as pd

    store = RunArtifactStore(root)
    rows = [_index_row(store, run_id) for run_id in store.run_ids()]
    frame = pd.DataFrame(rows, columns=list(INDEX_COLUMNS))
    if rows:
        Path(root).mkdir(parents=True, exist_ok=True)
        frame.to_parquet(Path(root) / INDEX, index=False)
    return frame


#: One row per run. ⚠ Every column answers a question a spec already asks:
#: `verdict`/`actionable` for **DN-17**'s veto rate, `agreement` for **RM-1**,
#: `alerts_status` for **DN-38**, `status` for **DN-29**'s liveness.
#: ★ **RC-64** adds the last four. ⚠ Without `excluded_n` the exclusion rate is
#: unmeasurable — RC-59's own argument one column over: *an index that held only
#: successes would make the base rates measure the wrong population.*
INDEX_COLUMNS = (
    "run_id", "as_of", "job_graph_id", "status", "ticker", "verdict",
    "actionable", "was_downgraded", "alerts_status", "bundle_hash",
    "thesis_verdict", "agreement", "spend_usd",
    "universe_n", "excluded_n", "model_artifact_id", "delivery_status",
)


def _index_row(store: RunArtifactStore, run_id: str) -> dict:
    files = store.read_run(run_id)
    manifest = files.get(MANIFEST) or {}
    outcome = files.get(OUTCOME) or {}
    recommendation = files.get(RECOMMENDATION) or {}
    thesis = files.get(THESIS) or {}
    nomination = recommendation.get("nomination") or {}
    delivery = files.get(DELIVERY) or {}
    stability = thesis.get("verdict_stability") or {}
    candidate = recommendation.get("candidate") or {}
    # ⚠ `verdict` is an OBJECT — `{final, nominated, was_downgraded}` — because
    #   D-12 records the gate's effect, not just its result. The index keeps
    #   `final`, and `was_downgraded` is what DN-17's veto rate counts.
    verdict = recommendation.get("verdict")
    if not isinstance(verdict, dict):
        verdict = {"final": verdict}
    return {
        "run_id": run_id,
        "as_of": str(manifest.get("as_of") or recommendation.get("as_of") or ""),
        "job_graph_id": manifest.get("job_graph_id", ""),
        "status": outcome.get("status", ""),
        "ticker": candidate.get("ticker", ""),
        "verdict": verdict.get("final") or "",
        "was_downgraded": bool(verdict.get("was_downgraded")),
        # ⚠ `bool(None)` is False and would report an unknown as a decided "no";
        #   the index keeps the distinction the artifact made.
        "actionable": recommendation.get("actionable"),
        "alerts_status": recommendation.get("alerts_status", ""),
        "bundle_hash": thesis.get("bundle_hash", ""),
        "thesis_verdict": thesis.get("verdict", ""),
        "agreement": stability.get("agreement"),
        "spend_usd": outcome.get("spend_usd"),
        # ── RC-64 ──────────────────────────────────────────────────────────
        "universe_n": nomination.get("universe_n"),
        # ⚠ `None` when there is no nomination, `0` when nothing was barred.
        #   *We did not rank* and *we barred nobody* are different facts.
        "excluded_n": (len(nomination["excluded"])
                       if "excluded" in nomination else None),
        "model_artifact_id": nomination.get("model_artifact_id", ""),
        # ★ RC-63 — "" means no delivery.json, i.e. NOT DELIVERED.
        "delivery_status": delivery.get("outcome", ""),
    }
