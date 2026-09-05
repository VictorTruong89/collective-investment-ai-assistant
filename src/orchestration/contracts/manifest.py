"""CT-8.1 RunManifest and CT-8.2 RunOutcome (OR-9…OR-13, OR-43).

```
D-08 IS THE ONLY LAYER THAT CAN ENFORCE CONSTITUTION INV-2.

A domain can be deterministic in isolation and the pipeline still
irreproducible, because reproducibility is a property of THE WHOLE
INVOCATION — code + config + data + seed. Determinism has no owner if D-08
does not own the manifest.
```

★ Today's entire run identity is `datetime.now().strftime(...)`. No manifest, no
code version, no config hash, no data `as_of`, no run-level seed.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

SUCCESS, FAILED, INCOMPLETE, BUDGET_EXCEEDED, BLOCKED_PRECONDITION = (
    "SUCCESS", "FAILED", "INCOMPLETE", "BUDGET_EXCEEDED", "BLOCKED_PRECONDITION",
)


@dataclass(frozen=True, slots=True)
class Stub:
    """★ OR-43 — a stubbed domain, declared. `stubs: []` is the production value.

    ⚠ *A stub that is indistinguishable from a real gate in the record is how a
    placeholder survives into production* (L3 BS-27).
    """

    domain: str
    job: str
    behaviour: str
    replaced_at: str
    rule: str

    def to_json_obj(self) -> dict:
        return {"domain": self.domain, "job": self.job, "behaviour": self.behaviour,
                "replaced_at": self.replaced_at, "rule": self.rule}


@dataclass(frozen=True, slots=True)
class RunManifest:
    """CT-8.1 — written **before** work begins, immutable (OR-9, OR-13)."""

    run_id: str
    job_graph_id: str
    git_sha: str
    dirty: bool
    config_hash: str
    data_as_of: date
    decision_anchor: str
    seed: int
    inputs: tuple[dict, ...] = ()
    budgets: dict = field(default_factory=dict)
    preconditions: dict = field(default_factory=dict)
    #: ★ OR-43. Present even when empty — an absent key is not an empty list.
    stubs: tuple[Stub, ...] = ()
    written_at: datetime | None = None

    def to_json_obj(self) -> dict:
        return {
            "run_id": self.run_id, "job_graph_id": self.job_graph_id,
            "code": {"git_sha": self.git_sha, "dirty": self.dirty},
            "config_hash": self.config_hash,
            "data_as_of": self.data_as_of.isoformat(),
            "decision_anchor": self.decision_anchor,
            "seed": self.seed,
            "inputs": [dict(i) for i in self.inputs],
            "budgets": dict(self.budgets),
            "preconditions": dict(self.preconditions),
            "stubs": [s.to_json_obj() for s in self.stubs],
            "written_at": self.written_at.isoformat() if self.written_at else None,
        }


@dataclass(frozen=True, slots=True)
class JobRun:
    job_id: str
    status: str
    attempts: int
    elapsed_s: float
    error_code: str | None = None

    def to_json_obj(self) -> dict:
        return {"job_id": self.job_id, "status": self.status, "attempts": self.attempts,
                "elapsed_s": round(self.elapsed_s, 6), "error_code": self.error_code}


@dataclass(frozen=True, slots=True)
class RunOutcome:
    """CT-8.2. ★ `INCOMPLETE` is a first-class terminal status, not a variant of success."""

    run_id: str
    status: str
    jobs: tuple[JobRun, ...]
    started_at: datetime
    ended_at: datetime
    artifacts: tuple[str, ...] = ()

    @property
    def produces_human_artifact(self) -> bool:
        """OR-16 / AC-8.19 — ★ **partial success is failure.**

        *A run where some jobs succeeded and some failed is INCOMPLETE, and
        INCOMPLETE never produces a human-facing artifact.* Both real incidents
        in this repo came from a downstream consumer treating a degraded upstream
        as usable.
        """
        return self.status == SUCCESS

    def to_json_obj(self) -> dict:
        return {"run_id": self.run_id, "status": self.status,
                "jobs": [j.to_json_obj() for j in self.jobs],
                "started_at": self.started_at.isoformat(),
                "ended_at": self.ended_at.isoformat(),
                "artifacts": list(self.artifacts)}


def git_state(repo_root=None) -> tuple[str, bool]:
    """`(sha, dirty)` — OR-11.

    ⚠ A dirty tree is **permitted and marked**. *Silently recording a clean sha
    for a modified tree is worse than not recording one.*
    """
    def run(*args) -> str:
        return subprocess.run(args, cwd=repo_root, capture_output=True,
                              text=True, check=False).stdout.strip()
    sha = run("git", "rev-parse", "--short", "HEAD") or "unknown"
    dirty = bool(run("git", "status", "--porcelain"))
    return sha, dirty


def config_hash(config: dict) -> str:
    """Content hash of every config value the run used (OR-9, CN-5)."""
    return "sha256:" + hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
        .encode("utf-8")).hexdigest()


def new_run_id(job_graph_id: str, at: datetime | None = None) -> str:
    """OR-12 — ★ **not a wall-clock timestamp alone.**

    *Two runs launched in the same second must be distinguishable, and a run id
    must survive a clock change.* The random suffix supplies both.
    """
    at = at or datetime.now(timezone.utc)
    return f"{at.strftime('%Y-%m-%dT%H:%M:%SZ')}-{job_graph_id}-{uuid.uuid4().hex[:6]}"
