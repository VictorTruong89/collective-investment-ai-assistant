#!/usr/bin/env python3
"""Snapshot FMP's forward analyst estimates, stamped with WHEN we observed them.

    python3 tools/snapshot_analyst_estimates.py              # the tickers in config/snapshots/
    python3 tools/snapshot_analyst_estimates.py MU AMD       # or name them

★ Runs weekdays at 18:30 New York from a systemd user timer (`deploy/snapshot-analyst-
estimates.{service,timer}.example`; L3 §2.1q decision 3, Victor 2026-10-02).

`L3` §2.1p item 5 (Victor, 2026-10-01). ⚠⚠ `analyst-estimates` is Class B (`fmp-api` trap 5):
it returns TODAY's forward consensus, and its `date` is the forecast TARGET period, not
the day it was published. Asked tomorrow, it returns different numbers and yesterday's are
gone. ★ So we create the publication axis ourselves: each call is written once, append-only,
to `snapshots/analyst-estimates/<TICKER>/<observed_at>.json` — ✏ a VERSION-CONTROLLED path
(2026-10-02): under gitignored `.state/` the history died with the laptop (`DX-12`'s shape). A future thesis may use
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
ROOT = REPO / "snapshots/analyst-estimates"
CONFIG = REPO / "config/snapshots/analyst_estimates.yaml"
LIMIT = 10


def configured_tickers(path=CONFIG) -> list[str]:
    import yaml
    tickers = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))["tickers"]
    if not tickers:
        raise SystemExit(f"{path}: no tickers configured")
    return [str(t).upper() for t in tickers]


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


def run(tickers, client) -> int:
    """Every ticker is attempted; ⚠ any failure makes the run exit 1, so the timer's journal
    shows a missed day rather than a quiet gap (P5)."""
    failed = []
    for t in tickers:
        try:
            print(f"  {t.upper()} → {snapshot(t, client, root=ROOT)}")
        except Exception as exc:                                    # noqa: BLE001
            failed.append(t.upper())
            print(f"  ⛔ {t.upper()}: {type(exc).__name__}: {exc}", file=sys.stderr)
    if failed:
        print(f"  ⛔ NOT RECORDED today: {failed}", file=sys.stderr)
    return 1 if failed else 0


def main(argv=None) -> int:
    from tools.fetch_consensus import _client
    tickers = (argv if argv is not None else sys.argv[1:]) or configured_tickers()
    return run(tickers, _client())


if __name__ == "__main__":
    raise SystemExit(main())
