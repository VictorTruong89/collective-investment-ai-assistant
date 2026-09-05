"""The Fact ledger — CT-7.3, append-only (DE-6.2, DE-6.3, AC-7.9, AC-7.12).

★ THE LEDGER IS THE SYSTEM OF RECORD. CT-7.2 is derived from it at an `as_of`
and may be rebuilt at any time; if the two disagree, the ledger is right
(AC-7.17).

★ WHY APPEND-ONLY IS ENFORCED IN CODE AND NOT BY CONVENTION.
A restatement APPENDS. Overwriting a Fact destroys the only information that
makes look-ahead detectable, and it does so invisibly — the resulting ledger is
internally consistent, passes every schema check, and quietly asserts that the
restated number was knowable all along.

⚠ QD-1 is open (one parquet per ticker vs one partitioned dataset). Per-ticker
is implemented here because it is simpler to write atomically and because the
whole-ledger scan this project needs is 130 files, not 130 million rows. The
choice is recorded in the blueprint; nothing outside this module depends on it.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.data_engine.contracts.ledgers import FACT_LEDGER
from src.data_engine.contracts.schema import as_date32, as_utc_timestamp
from src.data_engine.errors import AppendOnlyError, NoFilingDateError
from src.data_engine.pit.models import Fact
from src.data_engine.store.atomic import read_parquet, write_parquet

#: The columns that identify a Fact. A second filing reporting the same period
#: differs on `accession_id`, which is exactly how a restatement gets its own row
#: rather than replacing one.
KEY = list(FACT_LEDGER.key)

#: Sort order for every write. INV-2: same ledger, same bytes. Without an
#: explicit order, two ingests of identical Facts in a different arrival order
#: produce different files and AC-7.19 fails for a reason that has nothing to do
#: with the data (PD-20).
SORT = KEY + ["filing_date"]


class FactLedger:
    """Append-only per-ticker parquet store."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def path(self, ticker: str) -> Path:
        return self.root / f"{ticker.upper()}.parquet"

    # -- read --------------------------------------------------------------- #

    def read(self, ticker: str) -> pd.DataFrame:
        p = self.path(ticker)
        if not p.is_file():
            return FACT_LEDGER.empty()
        return read_parquet(p)

    # -- write -------------------------------------------------------------- #

    def append(self, facts) -> int:
        """Append `facts`, returning the number of NEW rows written.

        Three outcomes, and the middle one is the reason this is not a plain
        concat:

          * a key that is not present  -> appended
          * a key present with the SAME value -> no-op, so re-ingest is
            idempotent (DE-11, AC-7.19)
          * a key present with a DIFFERENT value -> raises. That is not a
            restatement: a restatement arrives on a new `accession_id` and gets
            its own row. Same accession, same tag, same period, different number
            means the ingest is wrong, and overwriting would hide it (DE-6.2)
        """
        facts = list(facts)
        if not facts:
            return 0
        by_ticker: dict[str, list[Fact]] = {}
        for f in facts:
            _reject_undateable(f)
            by_ticker.setdefault(f.ticker.upper(), []).append(f)

        written = 0
        for ticker, group in sorted(by_ticker.items()):
            written += self._append_one(ticker, group)
        return written

    def _append_one(self, ticker: str, facts: list[Fact]) -> int:
        incoming = _to_frame(facts)
        existing = self.read(ticker)

        if len(existing):
            merged = incoming.merge(
                existing, on=KEY, how="left", suffixes=("", "_old"),
                validate="one_to_one",          # PD-11 — a duplicate key here is a bug
            )
            clash = merged[merged["value_minor_old"].notna()
                           & (merged["value_minor"] != merged["value_minor_old"])]
            if len(clash):
                row = clash.iloc[0]
                raise AppendOnlyError(
                    "CT-7.3 Fact ledger",
                    {k: row[k] for k in KEY}
                    | {"stored": int(row["value_minor_old"]), "incoming": int(row["value_minor"])},
                )
            fresh = incoming[~_key_index(incoming).isin(_key_index(existing))]
        else:
            fresh = incoming

        if not len(fresh):
            return 0
        out = pd.concat([existing, fresh], ignore_index=True) if len(existing) else fresh
        out = out.sort_values(SORT, kind="mergesort").reset_index(drop=True)
        FACT_LEDGER.validate(out)
        write_parquet(out, self.path(ticker))
        return int(len(fresh))

    # -- audit -------------------------------------------------------------- #

    def restated_periods(self, ticker: str) -> pd.DataFrame:
        """Periods reported by more than one filing — DE-6.5, AC-7.13.

        Restatements are **surfaced, not smoothed**. A consumer asking for a
        period that has been restated can see that it was.
        """
        df = self.read(ticker)
        if not len(df):
            return df
        counts = (df.groupby(["tag", "period_end", "period_type"], sort=True)
                    ["accession_id"].nunique())
        return counts[counts > 1].reset_index(name="filings")


def _reject_undateable(fact: Fact) -> None:
    """DE-6.3 / AC-7.9 — a Fact with no filing_date never enters the ledger.

    Rejected at INGEST rather than filtered at read: a Fact that cannot be
    placed in time can never be safely served, so admitting it and remembering
    to exclude it later is one forgotten filter away from a look-ahead.
    """
    if fact.filing_date is None or not isinstance(fact.filing_date, date):
        raise NoFilingDateError(fact.ticker, fact.tag, fact.period_end)


def _to_frame(facts: list[Fact]) -> pd.DataFrame:
    df = pd.DataFrame([{
        "ticker": f.ticker.upper(), "accession_id": f.accession_id, "tag": f.tag,
        "period_start": pd.Timestamp(f.period_start),
        "period_end": pd.Timestamp(f.period_end),
        "period_type": f.period_type,
        "value_minor": int(f.value_minor), "value_currency": f.value_currency,
        "unit": f.unit, "filing_date": pd.Timestamp(f.filing_date),
        "ingested_at": pd.Timestamp(f.ingested_at).tz_convert("UTC"),
    } for f in facts])
    for col in ("period_start", "period_end", "filing_date"):
        df[col] = as_date32(df[col])
    df["ingested_at"] = as_utc_timestamp(df["ingested_at"])
    return df[list(FACT_LEDGER.names)]


def _key_index(df: pd.DataFrame) -> pd.Series:
    """A joinable string form of the composite key.

    A tuple column would work and would also make the parquet round-trip
    lossy — pyarrow widens a tuple to a list and the dtype comes back different.
    """
    return df[KEY].astype(str).agg("\x1f".join, axis=1)
