"""The incrementally-maintained event store — QD-16 (§6A.6).

★ **Why this exists rather than a live sweep per run.** 130 tickers x 8 sourced
classes is ~1,000 calls per run against a 300/min cap, and DE-31 requires the
check before **every** training, backtest and inference run. A live sweep makes
the gate the most expensive thing in the pipeline, and an expensive precondition
is one somebody eventually makes optional.

So the store is the system of record for *what the vendor has told us*, refreshed
incrementally, and the gate reads it. That makes the store itself a D-07 artifact
— which is the second half of QD-16, and it is why it has a declared shape here
rather than being a cache directory.

⚠ **A cached event feed cannot answer "I could not look".** So `refreshed_at` is
per class, and a class whose refresh is older than its window is reported
`UNCHECKED` rather than served stale — DE-35 surviving contact with a cache is
the whole design problem here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from src.data_engine.calendar.check import ClassResult, news_status
from src.data_engine.calendar.classes import BY_NAME, CHECKED, unchecked
from src.data_engine.contracts.envelopes import Finding
from src.data_engine.contracts.schema import Column, Schema, as_date32, as_utc_timestamp
from src.data_engine.pit.models import utcnow
from src.data_engine.store.atomic import read_json, read_parquet, write_json, write_parquet

#: The store's own shape. Not a CT-7.x — it is D-07-internal, and QD-16 notes it
#: needs a contract if it is ever served outward.
EVENT_STORE = Schema(
    contract_id="D-07 event store (QD-16)",
    title="Corporate-action event store",
    key=("ticker", "event_class", "event_date", "source"),
    columns=(
        Column("ticker", "string"),
        Column("event_class", "string"),
        Column("event_date", "date32"),
        Column("knowable_at", "date32", note="DE-18 — the knowability date, not the event"),
        Column("detail", "string", note="canonical JSON"),
        Column("source", "string"),
        Column("observed_at", "timestamp"),
    ),
)


@dataclass(frozen=True, slots=True)
class Freshness:
    """When a class was last refreshed, and how far back that refresh reached."""

    event_class: str
    refreshed_at: datetime
    covers_from: date
    covers_to: date


class EventStore:
    """Parquet-backed, one file for all classes, plus a JSON freshness index."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @property
    def events_path(self) -> Path:
        return self.root / "events.parquet"

    @property
    def freshness_path(self) -> Path:
        return self.root / "freshness.json"

    # -- events ------------------------------------------------------------- #

    def read(self) -> pd.DataFrame:
        return read_parquet(self.events_path) if self.events_path.is_file() \
            else EVENT_STORE.empty()

    def upsert(self, findings) -> int:
        """Merge `findings` in on the store key. Returns the number of new rows.

        Upsert rather than append: unlike the Fact ledger these are *vendor
        statements about events*, not immutable filings, and a corrected split
        ratio should replace the wrong one. The Fact ledger's append-only rule
        exists because a restatement is itself the evidence; here it is not.
        """
        findings = list(findings)
        if not findings:
            return 0
        incoming = pd.DataFrame([{
            "ticker": f.ticker.upper(), "event_class": f.event_class,
            "event_date": f.event_date, "knowable_at": f.knowable_at,
            "detail": json.dumps(f.detail, sort_keys=True, default=str),
            "source": f.source, "observed_at": utcnow(),
        } for f in findings])
        for col in ("event_date", "knowable_at"):
            incoming[col] = as_date32(incoming[col])
        incoming["observed_at"] = as_utc_timestamp(incoming["observed_at"])

        existing = self.read()
        combined = pd.concat([existing, incoming], ignore_index=True) if len(existing) \
            else incoming
        before = len(existing)
        combined = (combined.drop_duplicates(subset=list(EVENT_STORE.key), keep="last")
                            .sort_values(list(EVENT_STORE.key), kind="mergesort")
                            .reset_index(drop=True))
        EVENT_STORE.validate(combined)
        write_parquet(combined, self.events_path)
        return len(combined) - before

    # -- freshness ---------------------------------------------------------- #

    def record_refresh(self, event_class: str, covers_from: date, covers_to: date,
                       *, covers_tickers=None) -> None:
        """Record that a class was fetched — ★ **for WHICH names, not only when.**

        ⚠⚠ *Found 2026-08-27:* this stored a date window and nothing else, so a
        sweep of **12 names marked the class refreshed** and a subsequent gate
        over **510** read `CHECKED` — **498 of them never fetched.** That is
        DE-56's defect one level up: a refresh recorded beyond what it covered.

        ★ `covers_tickers=None` means *"coverage not recorded"*, and the feed
        treats that as **unverifiable** rather than universal — an older index
        written before this field must not read as covering everything.
        """
        index = self.freshness()
        index[event_class] = {
            "refreshed_at": utcnow().isoformat(),
            "covers_from": covers_from.isoformat(),
            "covers_to": covers_to.isoformat(),
            "covers_tickers": (sorted({t.upper() for t in covers_tickers})
                               if covers_tickers is not None else None),
        }
        write_json(index, self.freshness_path)

    def freshness(self) -> dict:
        return read_json(self.freshness_path) if self.freshness_path.is_file() else {}


class CachedEventFeed:
    """An `EventFeed` reading the store — QD-16's answer to the 1,000-call sweep.

    ⚠ **Staleness is reported, never served.** If the store's coverage for a
    class does not span the requested window, the class comes back `UNCHECKED`
    with the gap named. That is the only honest answer: the store genuinely does
    not know, and returning its partial rows as though they were the whole
    picture would be DE-35 defeated by an implementation detail.
    """

    def __init__(self, store: EventStore, *, max_age_days: int = 1) -> None:
        self.store = store
        self.max_age_days = max_age_days

    def fetch(self, event_class: str, tickers, start: date, end: date,
              as_of: date) -> ClassResult:
        spec = BY_NAME[event_class]
        if spec.permanently_unchecked:
            return ClassResult(unchecked(spec.note or "no source"))

        entry = self.store.freshness().get(event_class)
        if entry is None:
            return ClassResult(unchecked(
                f"the event store has never refreshed {event_class!r}; a class that "
                f"was never fetched has not been checked (DE-35)"
            ))

        covers_from = date.fromisoformat(entry["covers_from"])
        covers_to = date.fromisoformat(entry["covers_to"])
        refreshed_at = datetime.fromisoformat(entry["refreshed_at"])

        # ★★ **Coverage in NAMES, not only in dates.** ⚠ *Measured 2026-08-27:*
        #   a sweep of 12 names marked `split` refreshed and a gate over 510
        #   read `CHECKED` — **498 never fetched**. DE-36 is why that matters:
        #   *a name excluded from the actionable slate still participates in
        #   cross-sectional normalisation, so its unhandled split contaminates
        #   every other name's rank.*
        covered = entry.get("covers_tickers")
        asked = {t.upper() for t in tickers}
        if covered is None:
            return ClassResult(unchecked(
                f"the refresh of {event_class!r} recorded no ticker coverage, so "
                f"it cannot be shown to cover these {len(asked)} names — "
                f"unverifiable is not checked (DE-35)"))
        absent = asked - set(covered)
        if absent:
            return ClassResult(unchecked(
                f"{len(absent)} of {len(asked)} names were never fetched for "
                f"{event_class!r} (e.g. {sorted(absent)[:3]}); a class refreshed "
                f"for a subset has not been checked for the rest (DE-35, DE-36)"))

        if covers_from > start or covers_to < min(end, as_of):
            return ClassResult(unchecked(
                f"store covers {covers_from}..{covers_to}, window needs "
                f"{start}..{min(end, as_of)}"
            ))
        age = (utcnow() - refreshed_at).days
        if age > self.max_age_days:
            return ClassResult(unchecked(
                f"store last refreshed {age}d ago (max {self.max_age_days}d) — a stale "
                f"answer served as current is worse than admitting the gap"
            ))
        if event_class == "news":
            status = news_status(start, as_of)
            if status != CHECKED:
                return ClassResult(status)

        return ClassResult(CHECKED, self._findings(event_class, tickers, start, end, as_of))

    def _findings(self, event_class, tickers, start, end, as_of) -> tuple[Finding, ...]:
        df = self.store.read()
        if not len(df):
            return ()
        wanted = {t.upper() for t in tickers}
        spec = BY_NAME[event_class]
        rows = df[(df["event_class"] == event_class)
                  & (df["event_date"] >= pd.Timestamp(start))
                  & (df["event_date"] <= pd.Timestamp(end))
                  & (df["knowable_at"] <= pd.Timestamp(as_of))]
        if not spec.universe_wide:
            rows = rows[rows["ticker"].isin(wanted)]
        return tuple(
            Finding(r["ticker"], event_class, spec.severity, r["event_date"].date(),
                    r["knowable_at"].date(), json.loads(r["detail"]), r["source"])
            for _, r in rows.sort_values(["ticker", "event_date"], kind="mergesort").iterrows()
        )


def stale_after(refreshed_at: datetime, days: int) -> datetime:
    return refreshed_at + timedelta(days=days)
