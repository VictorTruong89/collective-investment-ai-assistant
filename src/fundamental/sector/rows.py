"""`E-15`'s verified rows → dated `SectorRecord`s in a `sector.v2` file (Victor, 2026-10-04).

★ **What the model supplies and what is derived.** The model reads: the row kind, its subject
(`qualifier`), value, unit, period, a capacity status from `E-15`'s own set, and a verbatim
quote. WHICH source and WHICH date are NOT asked — they are the source document the quote
resolves into (`AP-5`). ⚠ A quote that resolves into no document, or into more than one, raises:
a row whose provenance must be guessed is a claim about a source, not evidence from it.

★ **`RA-98` — every document is accounted for.** A source document with no row must be named
by a `not_found` that says why. *Skipping an item silently is how a file that contains no
opinion acquires one — through what got left out* (`E-15`).

★ **`RA-101` — append-only.** A capacity row's `prior_status` is where that subject's row
already stands; it is computed, never asked, so a transition can never overwrite one.
"""

from __future__ import annotations

from src.fundamental.sector.models import KIND_CAPACITY, SectorFile, SectorRecord

#: The record kind an `E-15` capacity row becomes; the other four keep their own names.
_KIND = {"capacity": KIND_CAPACITY}
#: The record kind of a document ingested whole (`tools/ingest_sector_file.py`).
KIND_DOCUMENT = "source_document"


def _flat(text: str) -> str:
    return " ".join(text.split())


def _documents(file: SectorFile) -> tuple[SectorRecord, ...]:
    return tuple(r for r in file.records if r.kind == KIND_DOCUMENT)


def source_of(file: SectorFile, quote: str) -> SectorRecord:
    """The ONE source document a verbatim quote comes from. Raises on none or several."""
    needle = _flat(quote)
    hits = [r for r in _documents(file) if needle in _flat(r.quote)]
    if not hits:
        raise ValueError(f"the quote is in no source document of the file: {quote[:60]!r}")
    if len(hits) > 1:
        raise ValueError(f"the quote is in {len(hits)} source documents "
                         f"({[r.record_id for r in hits]}) — its source cannot be attributed")
    return hits[0]


def _period(row) -> str:
    if row.period is None:
        return ""
    start, end = row.period.start, row.period.end
    return f"{start}:{end}" if start else str(end or "")


def records_from_rows(file: SectorFile, rows, *, statuses: dict[int, str],
                      run_id: str) -> tuple[SectorRecord, ...]:
    """Every FOUND row as a record, in the order given. `statuses[i]` is row `i`'s capacity
    status (the answer's `status_label`)."""
    from src.fundamental.prompts.e_blocks import E15_CAPACITY_STATUSES

    current = {r.subject: r.status for r in file.records if r.kind == KIND_CAPACITY}
    out = []
    for i, row in enumerate(rows):
        if row.status != "found":
            continue
        source = source_of(file, row.quote)
        kind = _KIND.get(row.evidence_id, row.evidence_id)
        subject = row.qualifier or source.subject
        status = prior = ""
        if kind == KIND_CAPACITY:
            status = statuses.get(i, "")
            if status not in E15_CAPACITY_STATUSES:
                raise ValueError(f"row {i} ({subject}): capacity status {status!r} is not one "
                                 f"of E-15's {E15_CAPACITY_STATUSES} (DX-122)")
            prior = current.get(subject, "")
            current[subject] = status
        out.append(SectorRecord(
            record_id=f"e15:{run_id}:{i}", date=source.date, kind=kind, subject=subject,
            source_id=source.source_id, url=source.url, quote=row.quote,
            status=status, prior_status=prior,
            value=str(row.value or ""), unit=str(row.unit or ""), period=_period(row)))
    return tuple(out)


def assert_every_document_accounted(file: SectorFile, rows) -> None:
    """`RA-98` — each source document yielded a row, or a `not_found` names it with a reason."""
    sourced = {source_of(file, r.quote).record_id for r in rows if r.status == "found"}
    stated = " ".join(f"{r.qualifier} {r.note}" for r in rows if r.status != "found")
    silent = [d.record_id for d in _documents(file)
              if d.record_id not in sourced and d.record_id not in stated]
    if silent:
        raise ValueError(f"E-15 skipped {silent} silently — every source item yields a row "
                         f"or a stated reason (RA-98)")

