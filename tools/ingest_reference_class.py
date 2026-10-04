#!/usr/bin/env python3
"""`F11` `T3` — ingest a reference class's members from EDGAR, and promote a fixture.

    python3 tools/ingest_reference_class.py memory 1

Each member's companyfacts go into D-07's FactLedger under its class LABEL (old and new
SanDisk share a ticker, so the label — not the ticker — is the key), through the same
`ingest_facts` the subject uses. ★ Then the ledger rows are COPIED to
`tests_src/fixtures/edgar/reference_class/<name>_v<version>/<LABEL>.parquet`, because
`.state/` is gitignored and a base rate that resolves on one laptop only is `DX-12`'s shape.
EDGAR is free; it needs `EDGAR_CONTACT` for its User-Agent (environment or `.env`).
"""

from __future__ import annotations

import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
FIXTURES = REPO / "tests_src/fixtures/edgar/reference_class"


def _contact() -> str:
    contact = os.environ.get("EDGAR_CONTACT")
    env = REPO / ".env"
    if not contact and env.exists():
        line = next((ln for ln in env.read_text().splitlines() if "EDGAR_CONTACT=" in ln), "")
        contact = line.split("=", 1)[1].strip().strip("'\"") if line else None
    if not contact:
        raise SystemExit("EDGAR_CONTACT is not set (environment or .env)")
    return contact


def fixture_dir(name: str, version: int) -> pathlib.Path:
    return FIXTURES / f"{name}_v{version}"


def main(argv=None) -> int:
    from src.data_engine.ingest.edgar_facts import ingest_facts
    from src.data_engine.pit.ledger import FactLedger
    from src.data_engine.src.edgar.client import EdgarClient
    from src.feature_engineer.base_rates.config import load_published_class
    from src.shared.secrets import Secret

    args = argv if argv is not None else sys.argv[1:]
    name, version = (args + ["memory", "1"])[:2]
    cls = load_published_class(name, int(version))
    client = EdgarClient(Secret("EDGAR_CONTACT", _contact()))
    ledger = FactLedger(REPO / ".state/facts")
    out = fixture_dir(cls.name, cls.version)
    out.mkdir(parents=True, exist_ok=True)
    failed = []
    for m in cls.members:
        try:
            written = ingest_facts(client, ledger, ticker=m.label, cik=m.cik)
        except Exception as exc:                                    # noqa: BLE001
            failed.append(m.label)
            print(f"  ⛔ {m.label} (CIK {m.cik}): {type(exc).__name__}: {exc}", file=sys.stderr)
            continue
        rows = ledger.read(m.label)
        rows.to_parquet(out / f"{m.label}.parquet", index=False)
        print(f"  {m.label:<10} CIK {m.cik:>8}  +{written} new · {len(rows)} ledger rows → "
              f"{(out / f'{m.label}.parquet').relative_to(REPO)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
