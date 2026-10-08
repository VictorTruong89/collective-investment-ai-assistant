"""D-07's §8 API surface, as one object (USE-CASE layer — CA-2).

★ **Every method that can feed training, backtest or inference takes `as_of` and
has NO DEFAULT for it** (DE-6.4), and the price path additionally takes
`adj_as_of` with no default (DE-45). Convenience wrappers that supply "today"
belong in the caller, where the choice is visible.

⚠ **CA-2**: this file imports no transport, no filesystem path and no vendor
SDK. It receives its sources and its ledgers. That is why `DataEngine` takes
seven constructor arguments instead of reading a config — the wiring is D-08's
job (CA-9), and a service that constructs its own adapters has inverted the rule
whatever its import list looks like.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.data_engine.contracts.envelopes import CalendarCheckReport, Provenance
from src.data_engine.contracts.ledgers import CLASS_B_FIELD_SETS
from src.data_engine.errors import WARNING_CODES
from src.data_engine.pit.adjustment import UNSET, build_price_panel
from src.data_engine.pit.models import EDGAR, utcnow
from src.data_engine.pit.snapshot import assemble_rows, facts_as_of, require_as_of
from src.data_engine.observation.ledger import deny_live_read


@dataclass(frozen=True, slots=True)
class FreshnessReport:
    """Per data type: what we hold, and how stale it is.

    ⚠ Staleness is measured against `ingested_at`, not `filing_date`. The gap
    between the two is **our own latency**, and reporting the filing date as
    freshness would hide exactly the quantity this report exists to expose
    (§6.2).
    """

    ticker: str
    as_of: date
    facts: int
    latest_filing: date | None
    latest_ingest: date | None
    price_rows: int
    latest_price: date | None

    @property
    def ingest_lag_days(self) -> int | None:
        if self.latest_filing is None or self.latest_ingest is None:
            return None
        return (self.latest_ingest - self.latest_filing).days


class DataEngine:
    """The §8 surface. Nothing else in `src/data_engine/` is importable (ST-3)."""

    def __init__(self, *, universe, fact_ledger, observation_ledger, price_source,
                 event_source=None, calendar_report: CalendarCheckReport | None = None,
                 fx_source=None) -> None:
        self._universe = universe
        self._facts = fact_ledger
        self._observations = observation_ledger
        self._prices = price_source
        self._events = event_source
        self._calendar_report = calendar_report
        self._fx = fx_source

    # -- prices -------------------------------------------------------------- #

    def get_prices(self, ticker: str, start: date, end: date, adj_as_of=UNSET
                   ) -> pd.DataFrame:
        """CT-7.1. `adj_as_of` is REQUIRED; `None` means the RAW series (DE-45).

        Amended from §8's original `get_prices(ticker, start, end)` — see DE-45.
        The old signature was "adjusted by default" with `adj_as_of` nowhere in
        it, which contradicted DE-28 and made `DATA.PRICE.ADJ_AS_OF_REQUIRED`
        unraisable by any documented call.
        """
        raw = self._prices.raw_prices(ticker.upper(), start, end)
        events = (list(self._prices.splits(ticker.upper()))
                  + list(self._prices.dividends(ticker.upper())))
        return build_price_panel(raw, events, adj_as_of)

    # -- fundamentals -------------------------------------------------------- #

    def get_facts(self, ticker: str, as_of=None) -> pd.DataFrame:
        """The raw ledger view, for audit. PIT-filtered like everything else."""
        as_of = require_as_of(as_of, "get_facts")
        return facts_as_of(self._facts.read(ticker.upper()), as_of)

    def get_fundamentals(self, ticker: str, as_of=None, period_type: str | None = None
                         ) -> pd.DataFrame:
        """CT-7.2, derived from CT-7.3 at `as_of` (§6.3, AC-7.17)."""
        as_of = require_as_of(as_of, "get_fundamentals")
        ticker = ticker.upper()
        rows = assemble_rows(self._facts.read(ticker), as_of,
                             source=self._universe.source_of(ticker))
        if period_type is not None and len(rows):
            rows = rows[rows["period_type"] == period_type].reset_index(drop=True)
        return rows

    def get_fundamentals_history(self, ticker: str, as_of=None, *,
                                 since: date | None = None) -> list:
        """DE-75 / AC-7.93 — `[(filing_date, CT-7.2 rows as of it)]`, one per filing.

        ★★ For a consumer spanning many dates (training, backtest). Each element is
        exactly `get_fundamentals(ticker, as_of=filing_date)`; one ledger read.
        `since` drops snapshots a panel starting then can never join: everything
        before the last filing on or before `since` (that one is kept).
        ⚠ *DX-159:* read ONCE at today, a 10-K's comparatives re-date every period
        to its latest re-filing, and a ten-year panel runs ~1 year stale.
        """
        as_of = require_as_of(as_of, "get_fundamentals_history")
        ticker = ticker.upper()
        ledger_df = self._facts.read(ticker)
        if not len(ledger_df):
            return []
        source = self._universe.source_of(ticker)
        filed = sorted({pd.Timestamp(d).date() for d in ledger_df["filing_date"]
                        if pd.Timestamp(d).date() <= as_of})
        if since is not None:
            before = [d for d in filed if d <= since]
            if before:
                filed = [d for d in filed if d >= before[-1]]
        return [(d, assemble_rows(ledger_df, d, source=source)) for d in filed]

    def provenance(self, ticker: str, as_of: date, *, adj_as_of: date | None = None,
                   fx_rate=None) -> Provenance:
        """CT-7.5 — and DE-23's `pit_guarantee` is set from the ROUTE, not guessed.

        An EDGAR-routed ticker is `reconstructed`; an FMP-routed one is
        `best_effort`, and `DATA.PIT.WEAK_GUARANTEE` rides along so the weaker
        guarantee is countable and not merely stated.
        """
        source = self._universe.source_of(ticker.upper())
        reconstructed = source == EDGAR
        return Provenance(
            source=source, as_of=as_of, fetched_at=utcnow(),
            pit_guarantee=Provenance.RECONSTRUCTED if reconstructed
            else Provenance.BEST_EFFORT,
            fx_rate_used=fx_rate.to_json_obj() if fx_rate is not None else None,
            adj_as_of=adj_as_of,
            warnings=() if reconstructed else (WARNING_CODES["weak_guarantee"],),
        )

    # -- Class-B ------------------------------------------------------------- #

    def get_observation(self, ticker: str, field_set: str, as_of=None,
                        consumer: str = "display"):
        """DE-6.9 / AC-7.26 — the only Class-B read path for D-04."""
        deny_live_read(field_set, consumer)
        return self._observations.get(ticker=ticker, field_set=field_set,
                                      as_of=as_of, consumer=consumer)

    def get_day_open(self, ticker: str, as_of, *, now=None, row=None):
        """DE-47 / AC-7.63, AC-7.64 — ★ the settled day-T **opening print**.

        ⚠ Distinct from the day-T *bar*: the auction is final at 09:30, the bar
        is not final until 16:00, so a daily endpoint polled at 10:00 returns an
        **in-progress row whose high/low/close are the running price.**
        `settled=False` blocks D-08's run (OR-33) and is **never backfilled from
        the previous close.**
        """
        from datetime import datetime, timezone

        from src.data_engine.observation.day_open import day_open

        if row is None:
            row = self._fetch_open_row(ticker.upper(), as_of)
        return day_open(ticker=ticker.upper(), as_of=as_of, row=row,
                        now=now or datetime.now(timezone.utc))

    def _fetch_open_row(self, ticker: str, as_of):
        """The vendor row for `as_of`, or `None`.

        ⚠ **Only `open` is taken.** MEASURED 2026-08-25 14:42 ET: FMP returns a
        **non-collapsed in-progress bar** mid-session — `close` is the running
        price and nothing in the payload says so — so reading `high`/`low`/
        `close` here would import three provisional numbers wearing settled
        clothes (DE-47).
        """
        fetch = getattr(self._prices, "open_row", None)
        if fetch is None:
            # ⚠ No source wired ⇒ unsettled ⇒ the run blocks (OR-33). A `None`
            #   here is the absence of an answer, never the previous close.
            return None
        try:
            return fetch(ticker, as_of)
        except Exception:                                  # noqa: BLE001
            return None

    @staticmethod
    def is_class_b(field_set: str) -> bool:
        return field_set in CLASS_B_FIELD_SETS

    # -- universe & calendar --------------------------------------------------#

    def get_universe(self):
        return [self._universe.entry(t) for t in self._universe.tickers]

    def calendar_check_report(self) -> CalendarCheckReport | None:
        """The report DE-33 attaches to every artifact this run produces."""
        return self._calendar_report

    # -- FX ------------------------------------------------------------------ #

    def get_fx(self, pair: str, as_of=None):
        """`None` when unavailable — never a guess (FX-3).

        `None` here means *legitimately absent* (EH-2): there genuinely was no
        rate for that pair on that date. A dependent value is then reported
        unavailable, not converted at a plausible rate.
        """
        as_of = require_as_of(as_of, "get_fx")
        if self._fx is None:
            return None
        return self._fx.rate(pair, as_of)

    # -- freshness ------------------------------------------------------------#

    def freshness(self, ticker: str, as_of=None) -> FreshnessReport:
        as_of = require_as_of(as_of, "freshness")
        ticker = ticker.upper()
        facts = self._facts.read(ticker)
        return FreshnessReport(
            ticker=ticker, as_of=as_of, facts=int(len(facts)),
            latest_filing=facts["filing_date"].max().date() if len(facts) else None,
            latest_ingest=facts["ingested_at"].max().date() if len(facts) else None,
            price_rows=0, latest_price=None,
        )
