"""D-01 §10C — the sector evidence file. RA-97…RA-102, RA-140…RA-142.

★ **The one funded capability.** With 13 watchlist names largely in one theme,
J-08 and E-13 do the same industry work thirteen times over the same industry.
**One sector file serves nearly the whole book.**

⚠ **It is also a shared prior by construction** — §7.2's correlated-error
channel wearing a data structure. The guard is not one rule but **four, because
a view can hide in four places**:

```text
   the PROSE      ── an "outlook" field         → RA-97
   the SAMPLING   ── which items got ingested   → RA-98
   the ORDERING   ── what sits at the top       → RA-99
   the SCHEMA     ── what got a column at all   → RA-100
```

★ They get harder to see in that order, and **the last one looks like
engineering.**
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.fundamental.errors import (
    CapacityRowMutatedError,
    ConclusionFieldError,
    SourceListIncompleteError,
)
from src.fundamental.sector.schema import (
    OMISSION_FIELDS_V1,
    RECORD_FIELDS_V1,
    SCHEMA_V1,
    assert_schema_current,
    schema_for,
)

#: RA-97 — the five the rule names, plus the near-synonyms the same field would
#: arrive under. ⚠ The list is *deliberately* wider than the rule's five: the
#: defect is a conclusion, not a spelling, and renaming `outlook` to `takeaway`
#: is the cheapest possible evasion.
CONCLUSION_FIELDS = frozenset({
    "outlook", "view", "implication", "summary", "assessment",   # RA-97's five
    "conclusion", "opinion", "takeaway", "recommendation", "rating",
    "thesis", "verdict", "signal", "call", "expectation", "forecast",
})

#: RA-101 / L0 INV-006 — the capacity lifecycle, in order. ★ A transition
#: **backwards** is permitted and interesting: a project can be cancelled or
#: stall, and that is precisely the history the rule protects.
CAPACITY_STATUSES = ("announced", "under construction", "commissioning",
                     "operating", "cancelled")

KIND_CAPACITY = "capacity_transition"


def assert_no_conclusion_fields(obj, *, path: str = "sector_file") -> None:
    """RA-97 / AC-1.66 — caught on sight, and the only one of the four that is."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).casefold() in CONCLUSION_FIELDS:
                raise ConclusionFieldError(path, str(key))
            assert_no_conclusion_fields(value, path=f"{path}.{key}")
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            assert_no_conclusion_fields(value, path=f"{path}[{i}]")


@dataclass(frozen=True, slots=True)
class Source:
    """One entry on the versioned source list (CT-1.7)."""

    source_id: str
    name: str
    kind: str = "company_ir"
    cadence: str = "daily"

    def to_json_obj(self) -> dict:
        return {"source_id": self.source_id, "name": self.name,
                "kind": self.kind, "cadence": self.cadence}


@dataclass(frozen=True, slots=True)
class SourceList:
    """CT-1.7 — ★ **completeness is only meaningful against a fixed list.**

    ⚠ The list is the artifact that gets reviewed, not the file that results
    from it: *selection of evidence is itself a conclusion* (RA-98).
    """

    source_list_version: str
    industry: str
    sources: tuple[Source, ...]

    @property
    def ids(self) -> frozenset:
        return frozenset(s.source_id for s in self.sources)

    def to_json_obj(self) -> dict:
        return {"source_list_version": self.source_list_version,
                "industry": self.industry,
                "sources": [s.to_json_obj() for s in self.sources]}


@dataclass(frozen=True, slots=True)
class SectorRecord:
    """★ RA-141 — **the file's unit is the dated RECORD, not the row.**

    ⚠ RA-99 says *"ordered by date"* and RA-101 gives a capacity row several
    dates. Sorting rows by announcement buries a transition that happened
    yesterday; sorting by latest transition makes the sort key **mutate**, and a
    file whose order changes without its content changing is not a fixed sort.
    So each transition is its own record, and the row is their **projection**.
    """

    record_id: str
    date: date
    kind: str
    subject: str
    source_id: str
    url: str = ""
    quote: str = ""
    status: str = ""
    prior_status: str = ""
    # ✏ `sector.v2` (2026-10-04) — an `E-15` row's reading. Empty on a v1 record.
    value: str = ""
    unit: str = ""
    period: str = ""

    def __post_init__(self) -> None:
        if self.kind == KIND_CAPACITY:
            if self.status not in CAPACITY_STATUSES:
                raise ValueError(
                    f"{self.record_id}: status {self.status!r} is not one of "
                    f"{CAPACITY_STATUSES} (RA-101, L0 INV-006)"
                )
            if self.prior_status and self.prior_status not in CAPACITY_STATUSES:
                raise ValueError(
                    f"{self.record_id}: prior_status {self.prior_status!r} is "
                    f"not a capacity status (RA-101)"
                )
        if not self.quote:
            raise ValueError(
                f"{self.record_id}: a record with no quote is a claim about a "
                f"source rather than evidence from it (RA-97's spirit, RA-6)"
            )

    def to_json_obj(self) -> dict:
        return {f: (self.date.isoformat() if f == "date" else getattr(self, f))
                for f in RECORD_FIELDS_V1}


@dataclass(frozen=True, slots=True)
class Omission:
    """RA-98 — a source that produced nothing, and **why**.

    ⚠ *Omissions are logged with a reason.* An omission with no reason is
    indistinguishable from a poll that never ran (RA-30, DE-35's shape).
    """

    source_id: str
    reason: str
    observed_at: str

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError(
                f"{self.source_id}: an omission with no reason is the defect "
                f"RA-98 names — curation is where the view hides"
            )

    def to_json_obj(self) -> dict:
        return {f: getattr(self, f) for f in OMISSION_FIELDS_V1}


@dataclass(frozen=True, slots=True)
class CapacityRow:
    """RA-101's projection — the transition history, reconstructed from records.

    ★ *The transition history is the finding, and an announcement that quietly
    never became capacity is invisible once the row is mutated.*
    """

    subject: str
    transitions: tuple[SectorRecord, ...]

    @property
    def current_status(self) -> str:
        return self.transitions[-1].status if self.transitions else ""

    @property
    def announced_on(self) -> date | None:
        for record in self.transitions:
            if record.status == "announced":
                return record.date
        return None

    def to_json_obj(self) -> dict:
        return {"subject": self.subject, "current_status": self.current_status,
                "announced_on": self.announced_on.isoformat()
                                if self.announced_on else None,
                "transitions": [r.to_json_obj() for r in self.transitions]}


@dataclass(frozen=True, slots=True)
class SectorFile:
    """CT-1.6. ★ Date-sorted, versioned schema, hashed into the bundle."""

    industry: str
    as_of: date
    file_version: int
    source_list_version: str
    records: tuple[SectorRecord, ...]
    omissions: tuple[Omission, ...] = ()
    schema_version: str = SCHEMA_V1
    schema_fingerprint: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        # ── RA-100/RA-140: the field set, before anything reads it.
        schema = schema_for(self.schema_version)
        fingerprint = assert_schema_current(
            self.schema_version, schema.record_fields, schema.omission_fields)
        object.__setattr__(self, "schema_fingerprint", fingerprint)
        # ✏ `sector.v2` — a record carrying a field its file's schema has no column for is
        #   REFUSED: writing it would drop the reading silently (`RA-100` inverted).
        for record in self.records:
            extra = [f for f in ("value", "unit", "period")
                     if getattr(record, f) and f not in schema.record_fields]
            if extra:
                raise ValueError(f"{record.record_id}: {extra} have no column in "
                                 f"{self.schema_version} — write a sector.v2 file")

        # ── RA-99/RA-141: one sort, over records, and it is not negotiable.
        ordered = tuple(sorted(self.records, key=lambda r: (r.date, r.record_id)))
        object.__setattr__(self, "records", ordered)

        # ── RA-97: last, so a conclusion field cannot hide behind a sort error.
        assert_no_conclusion_fields(self.to_json_obj())

    def to_json_obj(self) -> dict:
        return {
            "industry": self.industry, "as_of": self.as_of.isoformat(),
            "schema_version": self.schema_version,
            "schema_fingerprint": self.schema_fingerprint,
            "file_version": self.file_version,
            "source_list_version": self.source_list_version,
            "records": [self._record_obj(r) for r in self.records],
            "omissions": [o.to_json_obj() for o in self.omissions],
        }

    def _record_obj(self, record: SectorRecord) -> dict:
        """The record's v1 object plus the columns this file's schema adds (`sector.v2`)."""
        obj = record.to_json_obj()
        for f in schema_for(self.schema_version).record_fields:
            obj.setdefault(f, getattr(record, f))
        return obj

    # ── RA-101: the row is a PROJECTION. There is no setter, by construction.
    def capacity_row(self, subject: str) -> CapacityRow:
        return CapacityRow(subject, tuple(
            r for r in self.records
            if r.kind == KIND_CAPACITY and r.subject == subject))

    @property
    def subjects(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(
            r.subject for r in self.records if r.kind == KIND_CAPACITY))

    def pin(self) -> dict:
        """RA-102/RA-142 — what the bundle pins and the thesis declares."""
        return {"industry": self.industry, "schema_version": self.schema_version,
                "file_version": self.file_version}


def assert_complete(file: SectorFile, source_list: SourceList) -> None:
    """RA-98 / AC-1.67 — every source produced a record **or** a logged omission.

    ⚠⚠ *Selection of evidence is itself a conclusion.* This is the guard that
    needs an external artifact to check against, which is why RA-98 requires the
    source list to be **defined and versioned** before the file means anything.
    """
    if file.source_list_version != source_list.source_list_version:
        raise SourceListIncompleteError(
            {f"<list {file.source_list_version} vs {source_list.source_list_version}>"},
            source_list.source_list_version)
    accounted = ({r.source_id for r in file.records}
                 | {o.source_id for o in file.omissions})
    missing = source_list.ids - accounted
    if missing:
        raise SourceListIncompleteError(missing, source_list.source_list_version)


def append_transition(file: SectorFile, record: SectorRecord) -> SectorFile:
    """RA-101 / AC-1.70 — append-only, with the prior status stated.

    ⚠ **A row is never overwritten.** The only way a capacity row changes is by
    a new dated record whose `prior_status` matches where the row actually was —
    which is what makes an announcement that never became capacity *visible*.
    """
    import dataclasses

    if record.kind != KIND_CAPACITY:
        return dataclasses.replace(file, records=file.records + (record,))

    row = file.capacity_row(record.subject)
    if row.transitions:
        if not record.prior_status:
            raise CapacityRowMutatedError(
                record.subject,
                f"a transition to {record.status!r} states no prior_status, so "
                f"it replaces the row rather than extending it")
        if record.prior_status != row.current_status:
            raise CapacityRowMutatedError(
                record.subject,
                f"claims prior_status {record.prior_status!r} but the row is at "
                f"{row.current_status!r} — appending over a history that does "
                f"not lead here loses the transition in between")
        if record.date < row.transitions[-1].date:
            raise CapacityRowMutatedError(
                record.subject,
                f"dated {record.date} before the row's last transition "
                f"{row.transitions[-1].date} — an append that reorders history")
    elif record.prior_status:
        raise CapacityRowMutatedError(
            record.subject,
            f"claims prior_status {record.prior_status!r} on a row with no "
            f"transitions — the history it names was never recorded")
    return dataclasses.replace(file, records=file.records + (record,))
