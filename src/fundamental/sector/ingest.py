"""D-01 §10C / WF-7 — building a sector file from a versioned source list.

★★ **RA-98 is the rule this module exists for.** *The file ingests EVERY item
from a defined, versioned source list, and omissions are logged with a reason.*
⚠ A file accumulating the capacity announcements someone found interesting **has
a view, with no opinion field anywhere in it** — and curation is where the view
hides. So the ingest is written so that **skipping a source is not expressible**
without producing an `Omission`.
"""

from __future__ import annotations

from datetime import date

from src.fundamental.sector.models import (
    Omission, SectorFile, SectorRecord, SourceList, assert_complete,
)
from src.fundamental.sector.schema import SCHEMA_V1


def ingest(source_list: SourceList, *, poll, as_of: date, file_version: int,
           schema_version: str = SCHEMA_V1) -> SectorFile:
    """Poll every source on the list. `poll(source)` returns records or raises.

    ★ **Every source is visited, in list order, and a raising poll becomes a
    logged omission** — never a silent gap. The two outcomes are exhaustive by
    construction, which is what makes `assert_complete` a tautology on a file
    this function built and a real check on one it did not.
    """
    records, omissions = [], []
    for source in source_list.sources:
        try:
            produced = tuple(poll(source))
        except Exception as exc:                       # noqa: BLE001 — see below
            # ⚠ P5 says fail loud, and this **is** loud: the failure becomes a
            # first-class row in the artifact, carrying its reason, rather than
            # an exception that ends the run and leaves twelve good sources
            # unpolled. RA-98's *"logged with a reason"* is that trade, stated.
            omissions.append(Omission(source_id=source.source_id,
                                      reason=f"{type(exc).__name__}: {exc}"[:200],
                                      observed_at=as_of.isoformat()))
            continue
        if not produced:
            omissions.append(Omission(source_id=source.source_id,
                                      reason="polled, no new items",
                                      observed_at=as_of.isoformat()))
            continue
        records.extend(produced)

    file = SectorFile(industry=source_list.industry, as_of=as_of,
                      file_version=file_version,
                      source_list_version=source_list.source_list_version,
                      records=tuple(records), omissions=tuple(omissions),
                      schema_version=schema_version)
    assert_complete(file, source_list)
    return file


def declared_on(artifact) -> tuple[dict, ...]:
    """RA-142 / AC-1.71a — the sector files an artifact declares it consumed.

    ⚠ **Hashing proves it did not change; declaring says what it was.** A reader
    asking *"which sector file did this thesis rest on?"* cannot answer it from
    a hash without still holding the bundle.
    """
    return tuple(getattr(artifact, "sector_files", ()) or ())
