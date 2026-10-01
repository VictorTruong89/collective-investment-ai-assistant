#!/usr/bin/env python3
"""Snapshot FMP's forward analyst estimates, stamped with WHEN we observed them.

    python3 tools/snapshot_analyst_estimates.py MU AMD          # run daily (cron is Victor's call)

`L3` §2.1p item 5 (Victor, 2026-10-01). ⚠⚠ `analyst-estimates` is Class B (`fmp-api` trap 5):
it returns TODAY's forward consensus, and its `date` is the forecast TARGET period, not
the day it was published. Asked tomorrow, it returns different numbers and yesterday's are
gone. ★ So we create the publication axis ourselves: each call is written once, append-only,
to `.state/snapshots/analyst-estimates/<TICKER>/<observed_at>.json`. A future thesis may use
only snapshots observed on or before its as-of; history not captured cannot be retrofitted.

⚠ Parameter gate (`gates.parameter_gate`): `period=annual` and `limit` below 20.
"""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
ROOT = REPO / ".state/snapshots/analyst-estimates"
LIMIT = 10


def snapshot(ticker: str, client, *, root=ROOT, now=None) -> pathlib.Path:
    """One append-only observation. ⚠ Refuses to overwrite: a snapshot is a record."""
    observed = (now or datetime.now(timezone.utc)).replace(microsecond=0)
    rows = client.get("analyst-estimates", symbol=ticker.upper(), period="annual", limit=LIMIT)
    if not rows:
        raise RuntimeError(f"{ticker}: analyst-estimates returned no rows — nothing recorded (P5)")
    out = pathlib.Path(root) / ticker.upper() / f"{observed.strftime('%Y-%m-%dT%H%M%SZ')}.json"
    if out.exists():
        raise FileExistsError(f"{out} exists — a snapshot is never overwritten")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"ticker": ticker.upper(), "observed_at": observed.isoformat(),
                               "source": "FMP /stable/analyst-estimates period=annual",
                               "pit_class": "B — observed_at is OUR axis; `date` is the target",
                               "rows": rows}, indent=1), encoding="utf-8")
    return out


def main(argv=None) -> int:
    from tools.fetch_consensus import _client
    tickers = (argv if argv is not None else sys.argv[1:]) or []
    if not tickers:
        raise SystemExit("usage: snapshot_analyst_estimates.py TICKER [TICKER …]")
    client = _client()
    for t in tickers:
        print(f"  {t.upper()} → {snapshot(t, client)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
