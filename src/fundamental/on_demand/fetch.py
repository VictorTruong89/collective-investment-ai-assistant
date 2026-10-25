"""`--fetch-inputs` — the MISSING inputs a free source can supply, as NEW versioned fixtures.

★ Free or standing-approved only: EDGAR (submissions, archive documents, companyfacts) and
FMP (raw prices, analyst actions). The clients are injected; nothing here reads a key.

⚠ Three rules (AC-F13.11):
  · a fixture is WRITTEN ONCE — an existing path raises `FixtureExists`, never overwritten
    (`tests_src/fixtures/filings/README.md`: editing history destroys what was knowable when);
  · company-IR documents are NOT fetched — they are named as manual steps (`D11`);
  · the filing is converted by the ONE converter (`tools/convert_filing.py`, injected) —
    a second renderer is how four of seven early live-run failures happened.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from src.fundamental.on_demand.inputs import (
    CONSENSUS_DIR,
    FILINGS_DIR,
    INDUSTRY_DIR,
    PRICES_DIR,
)

RAW_PRICE_ENDPOINT = "historical-price-eod/non-split-adjusted"
#: How far back a price fixture reaches — enough for the valuation's price at `as_of`.
PRICE_WINDOW_DAYS = 28
#: How far back analyst actions are paged — the depth of the first consensus set.
CONSENSUS_BACK_DAYS = 2 * 365
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}"
PERIODIC = ("10-Q", "10-K")


class FixtureExists(FileExistsError):
    """A fixture path is already taken — refused, never overwritten."""


@dataclass
class FetchReport:
    written: list[str] = field(default_factory=list)
    manual: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def fiscal_label(report_date: date, fye_mmdd: str, form: str) -> str:
    """`FY2026` for a 10-K, `FY2025Q3` for a 10-Q — the fixture-name convention.

    ⚠ `fye_mmdd` is EDGAR's `fiscalYearEnd`; a 52/53-week year moves it by days, so a
    period end within a week after it still belongs to that fiscal year.
    """
    mm, dd = int(fye_mmdd[:2]), int(fye_mmdd[2:])
    fye = date(report_date.year, mm, dd)
    if report_date > fye + timedelta(days=7):
        fiscal_year, previous = report_date.year + 1, fye
    else:
        fiscal_year, previous = report_date.year, date(report_date.year - 1, mm, dd)
    if form == "10-K":
        return f"FY{fiscal_year}"
    return f"FY{fiscal_year}Q{round((report_date - previous).days / 91.3)}"


def latest_periodic(submissions: dict, as_of: date) -> dict | None:
    """The newest 10-Q/10-K FILED on or before `as_of` (INV-1), from EDGAR submissions."""
    recent = submissions["filings"]["recent"]
    rows = [{"form": f, "filed": recent["filingDate"][i], "period_end": recent["reportDate"][i],
             "accession": recent["accessionNumber"][i], "doc": recent["primaryDocument"][i]}
            for i, f in enumerate(recent["form"]) if f in PERIODIC
            and date.fromisoformat(recent["filingDate"][i]) <= as_of]
    return max(rows, key=lambda r: r["filed"]) if rows else None


def _archive_url(cik: str, row: dict) -> str:
    return ARCHIVE.format(cik=int(cik), acc=row["accession"].replace("-", ""), doc=row["doc"])


def _write_new(path: pathlib.Path, text: str) -> None:
    if path.exists():
        raise FixtureExists(f"{path} already exists — a fixture is written once, never "
                            f"overwritten (add a second one instead)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fetch_inputs(subject, as_of: date, resolution, *, repo: pathlib.Path, edgar, fmp, convert,
                 ingest_facts, fetch_consensus, edgar_sources: dict, manual_sources: dict,
                 today: date) -> FetchReport:
    """Fetch what is MISSING and a free source can supply. Returns what was written."""
    report = FetchReport()
    del manual_sources                     # ★ the supply text already names where (inputs.py)
    filing = resolution.get("filing")
    if not filing.found:
        _fetch_filing(subject, as_of, repo=repo, edgar=edgar, convert=convert, today=today,
                      report=report)
    for inp in resolution.inputs:
        if not inp.name.startswith("sector:") or inp.found:
            continue
        source_id = inp.name.split(":", 1)[1]
        if source_id in edgar_sources:
            _fetch_sector_filing(source_id, edgar_sources[source_id], as_of, repo=repo,
                                 edgar=edgar, convert=convert, today=today, report=report)
        else:
            report.manual.append(f"{source_id}: {inp.supply}")
    if not resolution.get("facts").found:
        ingest_facts(subject.ticker, subject.cik)
        report.written.append(f".state/facts/{subject.ticker}.parquet (EDGAR companyfacts)")
    if not resolution.get("price").found:
        start = as_of - timedelta(days=PRICE_WINDOW_DAYS)
        params = {"symbol": subject.ticker, "from": start.isoformat(), "to": as_of.isoformat()}
        body = fmp.get(RAW_PRICE_ENDPOINT, **params)
        rel = f"{PRICES_DIR}/{subject.ticker}_raw_eod_{as_of.isoformat()}.json"
        _write_new(repo / rel, json.dumps({"endpoint": RAW_PRICE_ENDPOINT, "params": params,
                                           "fetched_on": today.isoformat(), "response": body},
                                          indent=0))
        report.written.append(rel)
    if not resolution.get("consensus").found:
        _fetch_consensus(subject.ticker, as_of, repo=repo, fmp=fmp, fetch=fetch_consensus,
                         report=report)
    return report


def _fetch_filing(subject, as_of, *, repo, edgar, convert, today, report) -> None:
    submissions = edgar.submissions(subject.cik)
    row = latest_periodic(submissions, as_of)
    if row is None:
        report.notes.append(f"EDGAR holds no 10-Q/10-K for {subject.ticker} filed by {as_of}")
        return
    index_path = repo / FILINGS_DIR / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if any(r["accession"] == row["accession"] for r in index["filings"]):
        report.notes.append(f"{row['accession']} is already indexed — the newest EDGAR filing "
                            f"by {as_of} is the one held; it is stale or its file is absent")
        return
    label = fiscal_label(date.fromisoformat(row["period_end"]),
                         submissions.get("fiscalYearEnd") or "1231", row["form"])
    rel = f"{FILINGS_DIR}/{subject.ticker}_{label}_{row['form'].replace('-', '')}.txt"
    url = _archive_url(subject.cik, row)
    body = convert(edgar.document(url))
    _write_new(repo / rel, body)
    _write_new((repo / rel).with_suffix(".meta.txt"), _provenance(subject, row, url, today, body))
    index["filings"].append({"ticker": subject.ticker, "form": row["form"],
                             "accession": row["accession"], "period_end": row["period_end"],
                             "filed": row["filed"], "path": rel})
    index_path.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    report.written.append(rel)


def _provenance(subject, row, url, today, body) -> str:
    """The `.meta.txt` sidecar — ⚠ never inside the `.txt` (`DX-102`)."""
    return "\n".join([
        "PROVENANCE — written by `tools/thesis_for.py --fetch-inputs` (F13 D6). Do not edit",
        "the body; a restated filing gets a SECOND fixture.",
        "",
        f"Filer          : {subject.name}  (CIK {subject.cik})",
        f"Form           : {row['form']}",
        f"Period end     : {row['period_end']}",
        f"Filed          : {row['filed']}",
        f"Accession      : {row['accession']}",
        f"Source URL     : {url}",
        f"Retrieved      : {today} via EDGAR (declared User-Agent, DE-83)",
        f"Converted      : {today} by tools/convert_filing.py — {len(body):,} chars",
        "",
        "⚠ F13 D7: if this is a 10-K, the 32 prompt blocks were verified on a 10-Q; its first",
        "thesis is a new observation. Verify any figure against the Source URL, not this file.",
        ""])


def _fetch_sector_filing(source_id, spec, as_of, *, repo, edgar, convert, today, report) -> None:
    submissions = edgar.submissions(spec["cik"])
    row = latest_periodic(submissions, as_of)
    if row is None:
        report.notes.append(f"{source_id}: EDGAR holds no 10-Q/10-K filed by {as_of}")
        return
    form = row["form"].lower().replace("-", "")
    stem = f"{row['filed']}_{spec['slug']}-{form}-{row['period_end']}"
    folder = repo / INDUSTRY_DIR / source_id
    url = _archive_url(spec["cik"], row)
    body = convert(edgar.document(url))
    _write_new(folder / f"{stem}.txt", body)
    import hashlib
    _write_new(folder / f"{stem}.meta.json", json.dumps({
        "title": f"{spec['subject']} Form {row['form']} for the period ended {row['period_end']}",
        "url": url, "published_date": row["filed"],
        "published_date_source": f"EDGAR filingDate for accession {row['accession']}",
        "accession_id": row["accession"], "subject": spec["subject"],
        "converter": "tools/convert_filing.py", "source_id": source_id,
        "retrieved_at": today.isoformat(), "chars": len(body),
        "sha256": "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "removed": []}, indent=1))
    report.written.append(str((folder / f"{stem}.txt").relative_to(repo)))


def _fetch_consensus(ticker, as_of, *, repo, fmp, fetch, report) -> None:
    folder = repo / CONSENSUS_DIR / as_of.isoformat()
    # ★ A set is ONE ticker's: another ticker's set on the same date sits beside it (DX-186).
    if (folder / f"{ticker}.meta.json").exists() or any(folder.glob(f"{ticker}_*.json")):
        raise FixtureExists(f"{folder} already holds {ticker}'s set — a consensus set is "
                            f"written once (D10)")
    back_to = (as_of - timedelta(days=CONSENSUS_BACK_DAYS)).isoformat()
    data = fetch(ticker, back_to, fmp)
    for name in ("grades", "price_target_news", "earnings"):
        _write_new(folder / f"{ticker}_{name}.json", json.dumps(data[name], indent=0))
    _write_new(folder / f"{ticker}.meta.json", json.dumps({
        "ticker": ticker, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "FMP /stable/ — grades, earnings, price-target-news (paged)",
        "rows": {n: len(data[n]) for n in ("grades", "earnings", "price_target_news")},
        "price_target_pages": data.get("_pages"), "paged_back_to": back_to,
        "pit_class": "A (event-stamped); the as-of boundary is applied when the bundle is built",
        "written_by": "tools/thesis_for.py --fetch-inputs (F13 D10)"}, indent=1))
    report.written.append(str(folder.relative_to(repo)))
