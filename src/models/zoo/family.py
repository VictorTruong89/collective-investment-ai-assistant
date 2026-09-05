"""D-04 §11 — the model zoo. MT-35, MT-36, MT-37.

★ **MT-36: an unretained family is maintenance surface, not optionality.**
*Retirement is the default; retention needs a reason recorded in the registry.*
⚠ The legacy tree holds **nine families — 2,736 LOC across 18 files, for one
production horizon and ~250k rows.**

★ **MT-35: a family with no MethodEntry cannot be promoted.** The check is a
filesystem scan against `src/models/methods/entries/`, so it costs nothing and
cannot be argued with.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Family:
    """One model family, and the reason it is retained (MT-36)."""

    family_id: str
    formula_id: str
    #: ⚠ **Retention needs a REASON**, recorded here. An empty one is refused,
    #: because *"we might want it later"* is how nine families accumulate.
    retained_because: str
    library: str
    version: str = ""

    def __post_init__(self) -> None:
        from src.models.errors import ModelError

        if not self.retained_because.strip():
            raise ModelError(
                f"family {self.family_id!r} states no reason for retention. "
                f"★ MT-36: retirement is the DEFAULT — an unretained family is "
                f"maintenance surface, not optionality")

    def assert_promotable(self) -> None:
        """MT-35 — ★ **no MethodEntry, no promotion.**"""
        from src.models.errors import ModelError
        from src.quant.methods.registry import missing_sections

        try:
            missing = missing_sections(self.formula_id)
        except Exception as exc:                            # noqa: BLE001
            raise ModelError(
                f"family {self.family_id!r} declares formula "
                f"{self.formula_id!r} and no MethodEntry exists for it. A "
                f"family with no MethodEntry cannot be promoted (MT-35, "
                f"D-03 QA-20)") from exc
        if missing:
            raise ModelError(
                f"{self.formula_id}: MethodEntry is missing {missing!r}. "
                f"★ QA-20's six fields are what let a reader tell a standard "
                f"estimator from a house variant (MT-35)")

    def to_json_obj(self) -> dict:
        return {"family_id": self.family_id, "formula_id": self.formula_id,
                "retained_because": self.retained_because,
                "library": self.library, "version": self.version}


@dataclass
class Zoo:
    """The register. ★ One family today, and that is a decision (MT-36)."""

    _families: dict = field(default_factory=dict)

    def register(self, family: Family) -> Family:
        family.assert_promotable()
        self._families[family.family_id] = family
        return family

    def get(self, family_id: str) -> Family:
        from src.models.errors import ModelError

        family = self._families.get(family_id)
        if family is None:
            raise ModelError(
                f"no family {family_id!r} in the zoo. ⚠ There is no default "
                f"model family — MT-9's 'no fallback' applied one level up")
        return family

    def to_json_obj(self) -> dict:
        return {"families": [f.to_json_obj()
                             for _, f in sorted(self._families.items())]}
