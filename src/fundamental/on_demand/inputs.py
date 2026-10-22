"""Step 0 — the inputs a thesis at `as_of` reads, found or MISSING, before any model call.

★ Free and offline: it reads versioned fixtures and one injected question about the fact
ledger. Nothing here fetches — `--fetch-inputs` does that, and only when asked (`fetch.py`).

⚠ Three rules apply to every input (spec §4):
  · `INV-1` — nothing knowable only after `as_of` is chosen (AC-F13.4);
  · `D9` — the newest document older than `STALE_DAYS` counts as MISSING (AC-F13.12);
  · `P5` — a missing input names the command that supplies it (AC-F13.3).
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable

#: `D9` — one quarterly cadence plus a reporting lag.
STALE_DAYS = 120
#: A price fixture must hold a session this close before `as_of` (a weekend or holiday).
PRICE_SESSION_DAYS = 5

FILINGS_DIR = "tests_src/fixtures/filings"
INDUSTRY_DIR = "tests_src/fixtures/industry"
PRICES_DIR = "tests_src/fixtures/prices"
CONSENSUS_DIR = "tests_src/fixtures/consensus"
FETCH = "python tools/thesis_for.py {ticker} --as-of {as_of} --fetch-inputs"


@dataclass(frozen=True)
class Input:
    name: str
    found: bool
    detail: str
    supply: str = ""
    path: str | None = None
    knowable_at: date | None = None
    meta: dict = field(default_factory=dict)

    def to_json_obj(self, repo: pathlib.Path) -> dict:
        target = repo / self.path if self.path else None
        digest = None
        if target is not None and target.is_file():
            digest = "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
        return {"name": self.name, "found": self.found, "path": self.path,
                "detail": self.detail, "supply": self.supply or None, "sha256": digest,
                "knowable_at": self.knowable_at.isoformat() if self.knowable_at else None,
                **({"meta": self.meta} if self.meta else {})}


@dataclass(frozen=True)
class Resolution:
    ticker: str
    as_of: date
    inputs: tuple[Input, ...]

    @property
    def missing(self) -> tuple[Input, ...]:
        return tuple(i for i in self.inputs if not i.found)

    def get(self, name: str) -> Input:
        return next(i for i in self.inputs if i.name == name)


def resolve_inputs(subject, as_of: date, *, repo: pathlib.Path, sources: list[dict],
                   facts_accessions: Callable[[str], set], edgar_sources: dict,
                   manual_sources: dict) -> Resolution:
    """Every input for `subject` at `as_of`, in a fixed order."""
    fetch = FETCH.format(ticker=subject.ticker, as_of=as_of)
    filing = _filing(repo, subject.ticker, as_of, fetch)
    inputs = [filing]
    for source in sources:
        inputs.append(_sector_document(repo, source, as_of, fetch, edgar_sources, manual_sources))
    inputs.append(_consensus(repo, subject.ticker, as_of, fetch))
    inputs.append(_price(repo, subject.ticker, as_of, fetch))
    inputs.append(_facts(subject.ticker, filing, facts_accessions, fetch))
    return Resolution(ticker=subject.ticker, as_of=as_of, inputs=tuple(inputs))


def _stale(published: date, as_of: date) -> bool:
    return as_of - published > timedelta(days=STALE_DAYS)


def _filing(repo, ticker, as_of, fetch) -> Input:
    index = repo / FILINGS_DIR / "index.json"
    rows = json.loads(index.read_text(encoding="utf-8"))["filings"] if index.exists() else []
    held = [r for r in rows if r["ticker"] == ticker and r["form"] in ("10-Q", "10-K")
            and date.fromisoformat(r["filed"]) <= as_of]                     # INV-1
    if not held:
        return Input("filing", False, f"no 10-Q/10-K for {ticker} filed on or before {as_of} "
                     f"in {FILINGS_DIR}/index.json", fetch)
    row = max(held, key=lambda r: r["filed"])
    filed = date.fromisoformat(row["filed"])
    if _stale(filed, as_of):
        return Input("filing", False, f"stale — the newest held is {row['form']} filed {filed}, "
                     f"{(as_of - filed).days} days before {as_of} (D9)", fetch, row["path"], filed)
    if not (repo / row["path"]).is_file():
        return Input("filing", False, f"index row {row['accession']} names {row['path']}, "
                     f"which is absent", fetch)
    return Input("filing", True, f"{row['form']} {row['accession']} (period {row['period_end']}, "
                 f"filed {filed})", path=row["path"], knowable_at=filed, meta=dict(row))


def _sector_document(repo, source, as_of, fetch, edgar_sources, manual_sources) -> Input:
    source_id = source["source_id"]
    name = f"sector:{source_id}"
    if source_id in edgar_sources:
        supply = fetch
    else:
        where = (manual_sources.get(source_id) or {}).get("where", "the company's IR site")
        supply = (f"BY HAND (D11): save the newest release published on or before {as_of} from "
                  f"{where} as {INDUSTRY_DIR}/{source_id}/<published>_<slug>.txt with its "
                  f".meta.json — see tools/thesis_for.py --help")
    folder = repo / INDUSTRY_DIR / source_id
    docs = []
    for meta_path in sorted(folder.glob("*.meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        published = date.fromisoformat(meta["published_date"])
        if published <= as_of:                                                # INV-1
            docs.append((published, meta_path))
    if not docs:
        return Input(name, False, f"no document published on or before {as_of}", supply)
    published, meta_path = max(docs)
    text = meta_path.with_suffix("").with_suffix(".txt")
    rel = str(text.relative_to(repo))
    if _stale(published, as_of):
        return Input(name, False, f"stale — the newest is {published}, "
                     f"{(as_of - published).days} days before {as_of} (D9)", supply, rel, published)
    return Input(name, True, f"{text.name} (published {published})", path=rel,
                 knowable_at=published)


def _consensus(repo, ticker, as_of, fetch) -> Input:
    root = repo / CONSENSUS_DIR
    sets = []
    for meta in [root / f"{ticker}.meta.json", *sorted(root.glob(f"*/{ticker}.meta.json"))]:
        if meta.exists():
            fetched = date.fromisoformat(
                json.loads(meta.read_text(encoding="utf-8"))["fetched_at"][:10])
            if fetched >= as_of:            # ⚠ a set fetched earlier lacks the rows up to as_of
                sets.append((fetched, meta))
    if not sets:
        return Input("consensus", False, f"no consensus set fetched on or after {as_of} (D10)",
                     fetch)
    fetched, meta = min(sets)               # ★ the earliest that covers as_of — reproducible
    return Input("consensus", True, f"{meta.parent.relative_to(repo)} (fetched {fetched}; rows "
                 f"after {as_of} are cut when the bundle is built)",
                 path=str(meta.relative_to(repo)), knowable_at=fetched,
                 meta={"dir": str(meta.parent.relative_to(repo))})


def _price(repo, ticker, as_of, fetch) -> Input:
    found = []
    for path in sorted((repo / PRICES_DIR).glob(f"{ticker}_raw_eod_*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        params = doc.get("params") or {}
        if params.get("symbol") != ticker:
            continue
        days = {date.fromisoformat(r["date"][:10]) for r in doc.get("response") or ()}
        near = [d for d in days if as_of - timedelta(days=PRICE_SESSION_DAYS) <= d <= as_of]
        if near and date.fromisoformat(params["from"]) <= as_of <= date.fromisoformat(params["to"]):
            found.append((doc.get("fetched_on", ""), path, max(near)))
    if not found:
        return Input("price", False, f"no raw price fixture with a session within "
                     f"{PRICE_SESSION_DAYS} days before {as_of}", fetch)
    _fetched, path, session = min(found)
    return Input("price", True, f"{path.name} (last session ≤ as_of: {session})",
                 path=str(path.relative_to(repo)), knowable_at=session)


def _facts(ticker, filing: Input, facts_accessions, fetch) -> Input:
    if not filing.found:
        return Input("facts", False, "waits on the filing (the ledger must hold its accession)",
                     fetch)
    accession = filing.meta["accession"]
    if accession not in facts_accessions(ticker):
        return Input("facts", False, f".state/facts/{ticker}.parquet does not hold {accession}",
                     fetch)
    return Input("facts", True, f".state/facts/{ticker}.parquet holds {accession}",
                 path=f".state/facts/{ticker}.parquet")
