"""CT-2.1 — the FeatureContract. ENTITY layer (CA-1): stdlib and pandas only.

```
A FEATURE LIST SAYS WHICH COLUMNS EXIST.
A FEATURE CONTRACT SAYS WHAT EACH COLUMN MEANS.

"rsi_14" in a list is a name. Two implementations can both satisfy it and
disagree by 15 points (D-16 — ours uses a simple rolling mean where every
charting package uses Wilder smoothing, and nothing recorded the choice).

In a contract, rsi_14 carries a FORMULA ID. Change the formula, change the
id, change the contract version — and every model trained on the old one
fails parity LOUDLY instead of scoring on a silently different input.
```

★ Today's equivalent, `feature_schema.py`, is four Python lists. It is the right
idea doing real work; **what it lacks is a version, a formula identity per
feature, and any statement of range or provenance** — and those three absences
are exactly what let D-16, D-17 and the duplicate-moat defect happen.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from src.feature_engineer.errors import (
    AnalystDerivedInputError,
    DuplicateDefinitionError,
    LabelInContractError,
)

#: Input namespaces a FeatureSpec may name (FE-21). D-07 fields and other D-02
#: features — nothing else. The list is short on purpose: an input namespace is
#: a trust decision, and adding one should require reading this comment.
ALLOWED_INPUT_NAMESPACES = ("price", "fundamentals", "events", "macro", "sector", "feature")

#: Namespaces that would be an INV-014 breach. Named rather than inferred from
#: "not in the allow-list", so the error can say WHICH seat leaked in.
ANALYST_NAMESPACES = ("thesis", "gate", "scorecard", "rank", "model", "risk", "sizing",
                      "recommendation", "profile")

#: FE-11 — a label may never appear in a contract. Matched on the name, because
#: the directory boundary cannot see a spec someone hand-wrote in the wrong file.
LABEL_MARKERS = ("fwd_", "label_", "_ahead", "target_", "future_")


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    """One feature — §5.2's nine fields, none of them optional by accident."""

    name: str
    formula_id: str          # rsi.wilder.v1 | rsi.rolling_mean.v1 — the maths IS the id
    dtype: str
    inputs: tuple[str, ...]
    owner_module: str        # ★ the ONE place it is computed (FE-4)
    pit_class: str = "C"     # A / B / C, inherited from L1-data-engine §5A.4
    null_policy: str = "allow"          # allow | forbid — never fill_zero (§7.5)
    range: tuple[float, float] | None = None
    since_version: int = 1
    deprecated_in: int | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.null_policy not in ("allow", "forbid"):
            raise ValueError(
                f"null_policy must be 'allow' or 'forbid', not {self.null_policy!r}. "
                f"There is deliberately no 'fill_zero': an imputed value is "
                f"indistinguishable from a measured one once it is in the panel (FE-15)"
            )
        if any(self.name.startswith(m) or self.name.endswith(m) for m in LABEL_MARKERS):
            raise LabelInContractError([self.name])
        bad = [i for i in self.inputs
               if i.split(".", 1)[0] in ANALYST_NAMESPACES]
        if bad:
            raise AnalystDerivedInputError(self.name, bad)
        unknown = [i for i in self.inputs
                   if i.split(".", 1)[0] not in ALLOWED_INPUT_NAMESPACES]
        if unknown:
            raise AnalystDerivedInputError(self.name, unknown)

    def to_json_obj(self) -> dict:
        obj = asdict(self)
        obj["inputs"] = list(self.inputs)
        obj["range"] = list(self.range) if self.range else None
        return obj


@dataclass(frozen=True, slots=True)
class FeatureContract:
    """A named, versioned, immutable declaration (FE-1, FE-2)."""

    name: str
    version: int
    features: tuple[FeatureSpec, ...]
    created: str = ""
    note: str = ""
    _index: dict = field(default_factory=dict, compare=False, repr=False)

    def __post_init__(self) -> None:
        by_formula: dict[str, set[str]] = {}
        for spec in self.features:
            by_formula.setdefault(spec.formula_id, set()).add(spec.owner_module)
        for formula_id, modules in sorted(by_formula.items()):
            if len(modules) > 1:
                raise DuplicateDefinitionError(formula_id, modules)
        object.__setattr__(self, "_index", {s.name: s for s in self.features})

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Live features, in declaration order. Tombstones excluded (FE-6)."""
        return tuple(s.name for s in self.features if s.deprecated_in is None)

    def spec(self, name: str) -> FeatureSpec:
        """Resolve a spec — including a deprecated one.

        ★ FE-6 / AC-2.7: deprecation is by **tombstone**. A removed feature keeps
        its spec with `deprecated_in` set, so an old model's contract still
        resolves rather than failing to describe the thing it was trained on.
        """
        hit = self._index.get(name)
        if hit is None:
            raise KeyError(
                f"{name!r} has no FeatureSpec in {self.name}@v{self.version}. A "
                f"tombstoned feature still resolves; an unknown one never did (FE-6)"
            )
        return hit

    @property
    def content_hash(self) -> str:
        """What FE-2's immutability is checked against.

        Hashing the CONTENT rather than trusting the version number is what makes
        the rule mechanical: republishing v3 with a changed `formula_id` produces
        a different hash and is refused, whatever the file says.
        """
        payload = json.dumps(
            {"name": self.name, "version": self.version,
             "features": [s.to_json_obj() for s in self.features]},
            sort_keys=True, separators=(",", ":"),
        )
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
