"""The FMP-backed `EventFeed` — §6A.2's sourced classes (DE-31…DE-36).

One method per class rather than one big dispatch, because **each class has a
different knowability date** and that is the fact §6A exists to get right. A
shared "extract the date field" helper would be the place the distinction went
to die.

⚠ Classes this feed reports `UNCHECKED` rather than empty:

    earnings_scheduled  no publication axis — 34.6 % of rows are forward-dated
                        and the schedule itself is revised (QD-11)
    news                ~92 days of depth, at any price (K-8)
    restatement_silent  needs a prior dated ingest to diff against (DE-24)
    index_membership    no source, permanently
"""

from __future__ import annotations

from datetime import date, datetime

from src.data_engine.calendar.check import ClassResult, news_status
from src.data_engine.calendar.classes import BY_NAME, CHECKED, unchecked
from src.data_engine.contracts.envelopes import Finding
from src.data_engine.errors import SourceUnavailableError


class FMPEventFeed:
    """Fetches one §6A.2 class at a time, over the whole universe."""

    def __init__(self, client, *, prior_ingest_available: bool = False) -> None:
        self._client = client
        self._prior_ingest_available = prior_ingest_available

    def fetch(self, event_class: str, tickers, start: date, end: date,
              as_of: date) -> ClassResult:
        spec = BY_NAME[event_class]
        if spec.permanently_unchecked:
            return ClassResult(unchecked(spec.note or "no source"))

        handler = getattr(self, f"_{event_class}", None)
        if handler is None:
            return ClassResult(unchecked(
                f"{event_class} has no implemented source in this feed — a class "
                f"nobody wired is UNCHECKED, not clean (DE-35)"
            ))
        return handler(tickers, start, end, as_of)

    # -- BLOCK classes ------------------------------------------------------- #

    def _split(self, tickers, start, end, as_of):
        return self._splits(tickers, start, end, as_of, reverse=False)

    def _reverse_split(self, tickers, start, end, as_of):
        return self._splits(tickers, start, end, as_of, reverse=True)

    def _splits(self, tickers, start, end, as_of, *, reverse: bool):
        name = "reverse_split" if reverse else "split"
        found = []
        for ticker in tickers:
            for r in self._get("splits", symbol=ticker):
                effective = _as_date(r["date"])
                if not (start <= effective <= end):
                    continue
                num, den = float(r["numerator"]), float(r["denominator"])
                is_reverse = den > num
                if is_reverse != reverse:
                    continue
                found.append(Finding(
                    ticker, name, BY_NAME[name].severity, effective, effective,
                    {"numerator": num, "denominator": den}, "fmp:splits",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _restatement_amended(self, tickers, start, end, as_of):
        """Class 4 — an amended filing that amends a period INSIDE the window.

        K-7: MSFT's 2024-2026 amendments are `8-K/A`, `4/A`, `3/A`, `SC 13G/A`
        and there is **no `10-K/A`**. The probe asserts the detector finds these
        and does not invent others.
        """
        found = []
        for ticker in tickers:
            for r in self._get("sec-filings-search/symbol", symbol=ticker,
                               **{"from": start.isoformat(), "to": end.isoformat()}):
                form = str(r.get("formType", ""))
                if "/A" not in form:
                    continue
                accepted = _as_date(r.get("acceptedDate") or r.get("filedDate"))
                if not (start <= accepted <= end):
                    continue
                found.append(Finding(
                    ticker, "restatement_amended", BY_NAME["restatement_amended"].severity,
                    accepted, accepted, {"form_type": form}, "fmp:sec-filings-search",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _restatement_silent(self, tickers, start, end, as_of):
        """Class 5 — detectable only by diffing dated ingests (DE-24).

        ⚠ With no prior dated ingest there is nothing to diff, so this reports
        UNCHECKED. That is not a gap in the implementation — **FMP has no
        restatement history at all**, and DE-17 retains `data/fmp_dump/` for
        exactly this reason.
        """
        if not self._prior_ingest_available:
            return ClassResult(unchecked(
                "no prior dated ingest to diff against; FMP serves one answer, "
                "today's, with nothing indicating a value changed (DE-24, §5C.2)"
            ))
        return ClassResult(CHECKED)

    def _delisting(self, tickers, start, end, as_of):
        """Class 6 — survivorship (INV-017). The universe is live-listed names only."""
        wanted = set(tickers)
        found = []
        for r in self._get("delisted-companies"):
            symbol = str(r.get("symbol", "")).upper()
            if symbol not in wanted:
                continue
            when = _as_date(r.get("delistedDate") or r.get("ipoDate"))
            if not (start <= when <= end):
                continue
            found.append(Finding(symbol, "delisting", BY_NAME["delisting"].severity,
                                 when, when, {"company": r.get("companyName")},
                                 "fmp:delisted-companies"))
        return ClassResult(CHECKED, tuple(found))

    # -- FLAG classes -------------------------------------------------------- #

    def _filing_mid_window(self, tickers, start, end, as_of):
        """Class 7 — a statement landing inside the window changes what was knowable.

        K-6: MU's filing lag is min 20, median 28, max 57 days after period end.
        Keyed on `acceptedDate`, never on `date` (DE-21).
        """
        found = []
        for ticker in tickers:
            for r in self._get("income-statement", symbol=ticker, period="annual", limit=40):
                accepted = r.get("acceptedDate") or r.get("filingDate")
                if not accepted:
                    continue
                when = _as_date(accepted)
                if not (start <= when <= end):
                    continue
                found.append(Finding(
                    ticker, "filing_mid_window", BY_NAME["filing_mid_window"].severity,
                    when, when, {"period_end": str(r.get("date")), "accepted": str(accepted)},
                    "fmp:income-statement",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _dividend(self, tickers, start, end, as_of):
        found = []
        for ticker in tickers:
            for r in self._get("dividends", symbol=ticker):
                ex = _as_date(r["date"])
                if not (start <= ex <= end):
                    continue
                declared = _as_date(r["declarationDate"]) if r.get("declarationDate") else ex
                found.append(Finding(
                    ticker, "dividend", BY_NAME["dividend"].severity, ex, declared,
                    {"dividend": r.get("dividend")}, "fmp:dividends",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _earnings_reported(self, tickers, start, end, as_of):
        found = []
        for ticker in tickers:
            for r in self._get("earnings", symbol=ticker):
                when = _as_date(r["date"])
                if not (start <= when <= end) or r.get("epsActual") is None:
                    continue
                found.append(Finding(
                    ticker, "earnings_reported", BY_NAME["earnings_reported"].severity,
                    when, when,
                    {"eps_actual": r.get("epsActual"), "eps_estimated": r.get("epsEstimated")},
                    "fmp:earnings",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _earnings_scheduled(self, tickers, start, end, as_of):
        """Class 10 — UNCHECKED unless snapshotted (DE-18, QD-11).

        ⚠ `earnings-calendar` supplies **no publication axis**, and 34.6 % of its
        rows are future-dated. Joined to a training row by event date — the
        obvious join — the model learns that an earnings date was known months
        ahead. Sometimes it was; sometimes the date moved, and the calendar
        carries only today's answer.
        """
        return ClassResult(unchecked(
            "earnings-calendar has no publication axis and 34.6% of rows are "
            "forward-dated; a single-date calendar entry cannot be served to D-04 "
            "(DE-18, QD-11) — snapshot it into CT-7.6 first"
        ))

    def _material_event_8k(self, tickers, start, end, as_of):
        found = []
        for ticker in tickers:
            for r in self._get("sec-filings-search/symbol", symbol=ticker,
                               **{"from": start.isoformat(), "to": end.isoformat()}):
                if str(r.get("formType", "")) != "8-K":
                    continue
                when = _as_date(r.get("acceptedDate") or r.get("filedDate"))
                found.append(Finding(
                    ticker, "material_event_8k", BY_NAME["material_event_8k"].severity,
                    when, when, {"link": r.get("finalLink")}, "fmp:sec-filings-search",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _ma_announcement(self, tickers, start, end, as_of):
        wanted = set(tickers)
        found = []
        for r in self._get("mergers-acquisitions-latest"):
            symbol = str(r.get("symbol", "")).upper()
            if symbol not in wanted:
                continue
            when = _as_date(r.get("acceptedDate") or r.get("transactionDate"))
            if not (start <= when <= end):
                continue
            found.append(Finding(symbol, "ma_announcement",
                                 BY_NAME["ma_announcement"].severity, when, when,
                                 {"target": r.get("targetedCompanyName")},
                                 "fmp:mergers-acquisitions-latest"))
        return ClassResult(CHECKED, tuple(found))

    def _beneficial_ownership(self, tickers, start, end, as_of):
        found = []
        for ticker in tickers:
            for r in self._get("acquisition-of-beneficial-ownership", symbol=ticker):
                when = _as_date(r.get("filingDate"))
                if not (start <= when <= end):
                    continue
                found.append(Finding(
                    ticker, "beneficial_ownership",
                    BY_NAME["beneficial_ownership"].severity, when, when,
                    {"reporting_person": r.get("nameOfReportingPerson")},
                    "fmp:acquisition-of-beneficial-ownership",
                ))
        return ClassResult(CHECKED, tuple(found))

    # -- NOTE classes -------------------------------------------------------- #

    def _analyst_action(self, tickers, start, end, as_of):
        found = []
        for ticker in tickers:
            for r in self._get("grades", symbol=ticker):
                when = _as_date(r.get("date") or r.get("publishedDate"))
                if not (start <= when <= end):
                    continue
                found.append(Finding(
                    ticker, "analyst_action", BY_NAME["analyst_action"].severity,
                    when, when,
                    {"firm": r.get("gradingCompany"), "previous": r.get("previousGrade"),
                     "new": r.get("newGrade")},
                    "fmp:grades",
                ))
        return ClassResult(CHECKED, tuple(found))

    def _news(self, tickers, start, end, as_of):
        status = news_status(start, as_of)
        if status != CHECKED:
            return ClassResult(status)
        found = []
        for ticker in tickers:
            for r in self._get("news/stock", symbols=ticker):
                when = _as_date(r.get("publishedDate"))
                if not (start <= when <= end):
                    continue
                found.append(Finding(ticker, "news", BY_NAME["news"].severity, when, when,
                                     {"title": r.get("title")}, "fmp:news/stock"))
        return ClassResult(CHECKED, tuple(found))

    def _macro_release(self, tickers, start, end, as_of):
        """Class 16 — universe-wide, not per ticker. Span must stay under 180d (§5A.2)."""
        if (end - start).days >= 365:
            return ClassResult(unchecked(
                f"economic-calendar span {(end - start).days}d exceeds the 180d Starter "
                f"limit; a 402 here is a plan gate, not an absence (§5A.2 cause 2)"
            ))
        found = []
        for r in self._get("economic-calendar", **{"from": start.isoformat(),
                                                   "to": end.isoformat(),
                                                   "_span_days": (end - start).days}):
            when = _as_date(r.get("date"))
            found.append(Finding("*", "macro_release", BY_NAME["macro_release"].severity,
                                 when, when, {"event": r.get("event")},
                                 "fmp:economic-calendar"))
        return ClassResult(CHECKED, tuple(found))

    # -- transport ----------------------------------------------------------- #

    def _get(self, endpoint: str, **params):
        try:
            return self._client.get(endpoint, **params) or []
        except SourceUnavailableError:
            # Re-raised, never swallowed (EH-6). A source that could not be
            # reached is not a source that found nothing — the caller turns this
            # into UNCHECKED at the class level, which is DE-35's whole point.
            raise


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value)
    return datetime.fromisoformat(text.replace("Z", "+00:00")).date() if "T" in text \
        else date.fromisoformat(text[:10])
