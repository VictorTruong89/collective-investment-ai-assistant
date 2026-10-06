"""D-01 §10C — the sector file's schema, and the fingerprint that guards it.

★★ **RA-140.** RA-100 requires a *"fixed, versioned schema, immutable within a
version"* — and the check it asks for is only possible against a schema that was
**declared**. ⚠ RA-100's own argument is that *a schema change looks like
maintenance*; a guard that depends on someone noticing is the guard it says will
fail. So the field set is fingerprinted, and drift is caught by **arithmetic**.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

#: CT-1.6's `records[]` field set. ★ Order is part of the fingerprint: a
#: reordering is a schema change, because a reader reads columns in order.
RECORD_FIELDS_V1 = (
    "record_id", "date", "kind", "subject", "status", "prior_status",
    "source_id", "url", "quote",
)

#: CT-1.6's `omissions[]` field set — RA-98's half of the contract.
OMISSION_FIELDS_V1 = ("source_id", "reason", "observed_at")

SCHEMA_V1 = "sector.v1"

#: ✏ 2026-10-04 (Victor) — `sector.v2` = v1 + the three columns an `E-15` row carries that v1
#: has no place for. ★ v1 is untouched: a column arrives by a new version (`RA-100`).
RECORD_FIELDS_V2 = (*RECORD_FIELDS_V1, "value", "unit", "period")
SCHEMA_V2 = "sector.v2"


@dataclass(frozen=True, slots=True)
class SectorSchema:
    """A versioned field set. ⚠ Immutable within its version, exactly like a
    rubric (RA-33) — and for the same reason: an edit invalidates every artifact
    that declared it."""

    version: str
    record_fields: tuple[str, ...]
    omission_fields: tuple[str, ...]

    @property
    def fingerprint(self) -> str:
        payload = "|".join((self.version, ",".join(self.record_fields),
                            ",".join(self.omission_fields)))
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_json_obj(self) -> dict:
        return {"schema_version": self.version,
                "schema_fingerprint": self.fingerprint,
                "record_fields": list(self.record_fields),
                "omission_fields": list(self.omission_fields)}


#: The published schemas. ★ Adding a version is how a column arrives; editing
#: one in place is the defect RA-100 names.
SCHEMAS = {
    SCHEMA_V1: SectorSchema(SCHEMA_V1, RECORD_FIELDS_V1, OMISSION_FIELDS_V1),
    SCHEMA_V2: SectorSchema(SCHEMA_V2, RECORD_FIELDS_V2, OMISSION_FIELDS_V1),
}


def schema_for(version: str) -> SectorSchema:
    from src.fundamental.errors import SchemaDriftError

    schema = SCHEMAS.get(version)
    if schema is None:
        raise SchemaDriftError(version, "<undeclared>", "<undeclared>")
    return schema


def fingerprint_of(record_fields, omission_fields, version: str) -> str:
    """The fingerprint a file's ACTUAL field set produces (RA-140)."""
    return SectorSchema(version, tuple(record_fields),
                        tuple(omission_fields)).fingerprint


def assert_schema_current(version: str, record_fields, omission_fields) -> str:
    """RA-140 / AC-1.69a — the declared version and the actual fields must agree."""
    from src.fundamental.errors import SchemaDriftError

    schema = schema_for(version)
    actual = fingerprint_of(record_fields, omission_fields, version)
    if actual != schema.fingerprint:
        raise SchemaDriftError(version, schema.fingerprint, actual)
    return actual
