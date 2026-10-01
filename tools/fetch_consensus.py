#!/usr/bin/env python3
"""Fetch a name's published analyst actions from FMP into version-controlled fixtures.

    python3 tools/fetch_consensus.py MU --back-to 2024-01-01

Writes `tests_src/fixtures/consensus/<T>_{grades,price_target_news,earnings}.json` and a
`<T>.meta.json` provenance sidecar. `L3` §2.1p item 5 (Victor, 2026-10-01).

★ Version-controlled, not under `.state/`, so a thesis built from them reproduces on any
clone (`DX-12`'s lesson). The bundle section is built from these files by
`src/fundamental/bundle/consensus.py`, which applies the as-of boundary.
⚠ FMP calls are standing-approved (fixed-rate subscription), not free of quota: this
makes 2 calls plus one per 100 price-target rows.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
OUT = REPO / "tests_src/fixtures/consensus"
#: `price-target-news` returns at most 100 rows per call, newest first (measured 2026-10-01).
TARGET_PAGE = 100
MAX_PAGES = 30


def _client():
    import os

    from src.data_engine.src.fmp.client import FMPClient
    from src.shared.secrets import Secret
    key = os.environ.get("FMP_API_KEY")
    if not key and (REPO / ".env").exists():
        line = next((ln for ln in (REPO / ".env").read_text().splitlines()
                     if "FMP_API_KEY=" in ln), "")
        key = line.split("=", 1)[1].strip().strip("'\"") if line else None
    if not key:
        raise SystemExit("FMP_API_KEY is not set (environment or .env)")
    return FMPClient(Secret("FMP_API_KEY", key))


def fetch(ticker: str, back_to: str, client) -> dict:
    """The three series, raw. ★ Pages price targets until one is older than `back_to`."""
    grades = client.get("grades", symbol=ticker)
    earnings = client.get("earnings", symbol=ticker)
    targets, pages = [], 0
    for page in range(MAX_PAGES):
        rows = client.get("price-target-news", symbol=ticker, page=page, limit=TARGET_PAGE)
        pages += 1
        targets += rows
        if not rows or min(r["publishedDate"][:10] for r in rows) < back_to:
            break
    else:
        raise RuntimeError(f"price-target-news did not reach {back_to} in {MAX_PAGES} pages")
    return {"grades": grades, "earnings": earnings, "price_target_news": targets,
            "_pages": pages}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("--back-to", required=True, help="page price targets back to this date")
    args = ap.parse_args(argv)
    ticker = args.ticker.upper()
    data = fetch(ticker, args.back_to, _client())
    OUT.mkdir(parents=True, exist_ok=True)
    rows = {}
    for name in ("grades", "earnings", "price_target_news"):
        (OUT / f"{ticker}_{name}.json").write_text(json.dumps(data[name], indent=0),
                                                   encoding="utf-8")
        rows[name] = len(data[name])
    meta = {
        "ticker": ticker,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "FMP /stable/ — grades, earnings, price-target-news (paged)",
        "rows": rows, "price_target_pages": data["_pages"], "paged_back_to": args.back_to,
        "pit_class": "A (event-stamped); the as-of boundary is applied when the bundle is built",
        "hazards": [
            "price-target-news returns at most 100 rows per call; paged with page=0,1,…",
            "earnings rows carry lastUpdated AFTER the report: a past estimate may be revised",
            "earnings rows dated in the future hold TODAY's forward estimate — look-ahead; "
            "excluded by the as-of boundary",
            "grades carry a date but no time: a same-day row is excluded (decision 1b)",
        ],
    }
    (OUT / f"{ticker}.meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"  {ticker}: {rows} · {data['_pages']} price-target page(s) → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
