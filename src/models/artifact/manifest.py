"""D-04 §5 — the model artifact. CT-4.1, MT-1…MT-4, MT-41.

★ **Everything in this domain is a property of the artifact**, so the artifact
carries enough to make those properties checkable.

⚠ **MT-1 is a rebuild, not a rename.** *Today `model_manager.py:91` stores
`feature_names` as a list of strings and nothing else — **the whole D-17 class
follows from that one choice**.* A name list can be satisfied by coincidence;
a version cannot.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date

SELECTION, TIMING, RESEARCH = "selection", "timing", "research"
ROLES = (SELECTION, TIMING, RESEARCH)

#: MT-33 — ★ enforced **at load**, not by convention.
RESEARCH_HORIZON = "h1q"


@dataclass(frozen=True, slots=True)
class FeatureContractRef:
    """★ MT-1 — **a name and a version, never a column list.**

    ⚠⚠ *And a CONTENT HASH, from 2026-08-27.* `FeatureContract.content_hash`
    exists and says why in its own docstring — *"hashing the CONTENT rather than
    trusting the version number is what makes the rule mechanical … whatever the
    file says"* — and **this ref did not carry it**.

    ★★ The consequence was measured, not hypothetical: two artifacts, one with
    **59** features and one with **61**, both declared `price_and_fundamental@v1`
    after Group C was added without a version bump. **`check_parity` compares
    name and version, so it waved the difference through** — which is FE-2's
    immutability defeated by the one field that could have caught it.
    """

    name: str
    version: int
    #: ⚠ Defaulted empty so pre-existing artifacts still load; `check_parity`
    #: reports an absent hash as **unverifiable**, never as a match.
    content_hash: str = ""

    def __post_init__(self) -> None:
        if not self.name or self.version is None:
            from src.models.errors import ContractUnresolvableError

            raise ContractUnresolvableError(
                "<manifest>", "the feature contract needs a name AND a version")

    def to_json_obj(self) -> dict:
        return {"name": self.name, "version": self.version,
                "content_hash": self.content_hash}


@dataclass(frozen=True, slots=True)
class ModelManifest:
    """CT-4.1 — what must travel with a model."""

    role: str
    horizon_set_name: str
    horizon_set_version: int
    horizon_id: str
    feature_contract: FeatureContractRef
    label_def_id: str
    #: ★ MT-41 — the anchor the model was FITTED on, asserted at inference.
    decision_anchor: str
    training_start: date
    training_end: date
    training_as_of: date
    #: ★ MT-4 — two artifacts trained on "the same window" at different
    #: adjustment states are **different models** (D-02 FE-8, D-07 §5C.7).
    adj_as_of: date
    protocol: dict
    framework: dict
    seeds: dict
    code_version: str
    #: ★★ **How many names the cross-section held.** ⚠ *Added 2026-08-27 (AB-4).*
    #: `check_parity` compares the feature CONTRACT and cannot see the
    #: population — but `rank_ret_5d`, `rank_vol_20d` and every `*_sector_z` are
    #: **defined by the cross-section they are computed in**, so *a percentile
    #: among 497 names is not a percentile among 130*. Without this field the
    #: mismatch is undetectable: the column names match exactly.
    training_names: int = 0
    #: MT-17 — the D-03 BacktestResult that measured it. ⚠ Absent until D-03
    #: evaluates it, and **absence blocks promotion, not creation**.
    evaluation_result_id: str = ""
    artifact_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        from src.models.errors import HorizonRoleError, ModelError

        if self.role not in ROLES:
            raise ModelError(f"role {self.role!r} is not one of {ROLES}")
        if self.role == SELECTION and self.horizon_id == RESEARCH_HORIZON:
            raise HorizonRoleError(
                f"{RESEARCH_HORIZON} is a RESEARCH horizon (D-10 only) and may "
                f"never carry the selection role")
        if not self.decision_anchor:
            raise ModelError(
                "the manifest declares no decision_anchor. ★ MT-41: a model "
                "records the anchor it was fitted on, and inference asserts it "
                "against the RunManifest (MT-42, D-08 OR-44)")
        object.__setattr__(self, "artifact_id", self.content_hash())

    def to_json_obj(self) -> dict:
        return {
            "artifact_id": self.artifact_id, "role": self.role,
            "horizon_set": {"name": self.horizon_set_name,
                            "version": self.horizon_set_version},
            "horizon_id": self.horizon_id,
            "feature_contract": self.feature_contract.to_json_obj(),
            "label_def_id": self.label_def_id,
            "decision_anchor": self.decision_anchor,
            "training_names": self.training_names,
            "training_window": {"start": self.training_start.isoformat(),
                                "end": self.training_end.isoformat(),
                                "as_of": self.training_as_of.isoformat()},
            "adj_as_of": self.adj_as_of.isoformat(),
            "protocol": dict(self.protocol), "framework": dict(self.framework),
            "seeds": dict(self.seeds),
            "evaluation_result_id": self.evaluation_result_id,
            "code_version": self.code_version,
        }

    def content_hash(self) -> str:
        """MT-3 — ★ artifacts are **immutable**; a retrain produces a new id.

        ⚠ `artifact_id` and `evaluation_result_id` are excluded: the first is
        this hash, and the second is stamped *after* the model exists, so
        including it would change the id of a model that did not change.
        """
        payload = {k: v for k, v in self.to_json_obj().items()
                   if k not in ("artifact_id", "evaluation_result_id")}
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ModelArtifact:
    """The manifest plus the fitted thing. ★ MT-2 — no manifest, no scoring."""

    manifest: ModelManifest
    estimator: object
    feature_names: tuple[str, ...]

    @property
    def artifact_id(self) -> str:
        return self.manifest.artifact_id

    def assert_loadable_for_production(self) -> None:
        """MT-33 — ★ a 1q artifact may not be loaded by production inference,
        **enforced at load, not by convention.**"""
        from src.models.errors import HorizonRoleError

        if self.manifest.horizon_id == RESEARCH_HORIZON:
            raise HorizonRoleError(
                f"{self.artifact_id} is fitted at {RESEARCH_HORIZON} — a "
                f"RESEARCH horizon that never reaches a human-facing artifact")
