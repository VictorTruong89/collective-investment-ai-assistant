#!/usr/bin/env python3
"""The memory-industry sector file, ingested from a VERSIONED source list (`RA-98`, `DX-117`).

    python3 tools/ingest_sector_file.py --as-of 2025-06-26      # ★ free: no model, no network

★★ **What this does and does not do.** It visits **every** source on
`config/sector/<list>.yaml`, takes each recorded document knowable at `as_of`, and turns it
into a dated `SectorRecord` carrying the document VERBATIM. A source that yields nothing
becomes an `Omission` with its reason — skipping one is not expressible (`RA-98`).

⚠ **It does not read the documents.** Pulling *"Samsung is adding X wafers by Y"* out of prose
is EXTRACTION, and extraction is `E-13`'s job under `X-01`: every item it returns is verified
against this file's text. A keyword filter here would be the sampling `RA-98` forbids, dressed
as engineering — so the whole document travels and the model does the reading.

⚠ **`INV-1` holds per document**: a document published after `as_of` is omitted with that
reason, never carried. The dates come from each document's `.meta.json`, which records where
the date itself came from.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.fundamental.sector.ingest import ingest  # noqa: E402
from src.fundamental.sector.models import SectorRecord, Source, SourceList  # noqa: E402

#: Where a source's recorded documents live: `<INDUSTRY_ROOT>/<source_id>/<date>_<slug>.txt`
#: beside a `.meta.json`. ★ The provenance is a SIDECAR (`DX-102`): a header inside the text
#: would be quotable as if the company had written it.
INDUSTRY_ROOT = REPO / "tests_src/fixtures/industry"
CONFIG_ROOT = REPO / "config/sector"

#: The record kind for a document ingested whole. ⚠ NOT `capacity_transition`: that kind
#: carries a status from a closed lifecycle, and deciding a project's status from prose is a
#: reading, not an ingest (`RA-101`). Transitions are built from `E-13`'s verified items.
KIND_DOCUMENT = "source_document"


def load_source_list(path: pathlib.Path) -> tuple[SourceList, list[dict]]:
    import yaml

    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    sources = tuple(Source(source_id=s["source_id"], name=s["name"],
                           kind=s.get("kind", "company_ir"),
                           cadence=s.get("cadence", "quarterly"))
                    for s in doc["sources"])
    return (SourceList(source_list_version=doc["source_list_version"],
                       industry=doc["industry"], sources=sources),
            list(doc.get("excluded") or ()))


def documents_for(source_id: str, *, as_of: date) -> list[tuple[dict, str]]:
    """Every recorded document of one source that was knowable at `as_of`."""
    folder = INDUSTRY_ROOT / source_id
    out = []
    for meta_path in sorted(folder.glob("*.meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        text = meta_path.with_suffix("").with_suffix(".txt").read_text(encoding="utf-8")
        published = date.fromisoformat(meta["published_date"])
        if published > as_of:
            continue                       # INV-1 — reported below as the source's reason
        out.append((meta, text))
    return out


def poller(as_of: date):
    """`poll(source)` → records, or RAISE so `ingest` logs the omission with its reason."""
    def poll(source: Source):
        folder = INDUSTRY_ROOT / source.source_id
        if not folder.is_dir():
            raise FileNotFoundError(
                f"no recorded documents for {source.source_id} — the source is on the list "
                f"and nothing has been fetched for it")
        found = documents_for(source.source_id, as_of=as_of)
        if not found:
            later = sorted(p.name for p in folder.glob("*.meta.json"))
            raise ValueError(
                f"{source.source_id}: no document published on or before {as_of} "
                f"(held, later: {later or 'none'}) — INV-1")
        records = []
        for meta, text in found:
            records.append(SectorRecord(
                record_id=f"{source.source_id}:{meta['published_date']}",
                date=date.fromisoformat(meta["published_date"]), kind=KIND_DOCUMENT,
                subject=meta["subject"], source_id=source.source_id, url=meta.get("url", ""),
                quote=text))
        return records
    return poll


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", default="memory_v1", help="source list in config/sector/")
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--file-version", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of)
    source_list, excluded = load_source_list(CONFIG_ROOT / f"{args.list}.yaml")
    sector = ingest(source_list, poll=poller(as_of), as_of=as_of,
                    file_version=args.file_version)

    print(f"── SECTOR FILE · {sector.industry} · as of {as_of} "
          f"(list {sector.source_list_version}, file v{sector.file_version}) ──")
    for record in sector.records:
        print(f"   {record.date}  {record.subject:32s} [{record.source_id}] "
              f"{len(record.quote):,} chars")
    for omission in sector.omissions:
        print(f"   ⚠ OMITTED {omission.source_id}: {omission.reason[:120]}")
    for item in excluded:
        print(f"   ⊘ EXCLUDED {item['subject']}: {' '.join(item['reason'].split())[:110]}")

    out = pathlib.Path(args.out or REPO / f".state/sector/{args.list}_{as_of}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({**sector.to_json_obj(),
                               "source_list": source_list.to_json_obj(),
                               "excluded": excluded,
                               "ingested_at": datetime.now(timezone.utc).isoformat()},
                              indent=1), encoding="utf-8")
    print(f"  {len(sector.records)} record(s) · {len(sector.omissions)} omission(s) → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
