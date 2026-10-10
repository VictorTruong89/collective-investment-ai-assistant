"""D-07 — assembling one price panel over the whole universe. DE-13, DE-36.

★★ **DE-13: a universe ticker that resolves to no source FAILS THE RUN.**
⚠ *It is not dropped, and it does not become a row of NaNs.*

> **DE-13 is inherited from a real incident.** A LEFT JOIN silently dropped
> **7 of the 13 watchlist names** — the majority of the actionable path — and
> every one of them kept its row with all 47 fundamental columns present and
> entirely `NaN`. The columns existed. Nothing noticed.

★ **DE-36: the panel covers the UNIVERSE, not the watchlist.** *A name excluded
from the actionable slate still participates in cross-sectional
normalisation* — so a 13-name fetch produces a 13-name cross-section, and every
rank statistic computed on it is answering a different question.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

#: ⚠ A ticker may fail for reasons that need different remedies, and DE-13 does
#: not distinguish them. See **DE-49**.
NO_SOURCE, PLAN_GATED, EMPTY_WINDOW = "no_source", "plan_gated", "empty_window"


@dataclass(frozen=True, slots=True)
class TickerFailure:
    ticker: str
    reason: str
    detail: str

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "reason": self.reason,
                "detail": self.detail}


@dataclass(frozen=True, slots=True)
class AssemblyReport:
    """What the fetch found, before anything is built from it."""

    requested: tuple[str, ...]
    fetched: tuple[str, ...]
    failures: tuple[TickerFailure, ...]
    rows_by_ticker: dict = field(default_factory=dict)
    #: ★ **DE-63** — `{universe_ticker: symbol_actually_requested}`, populated
    #: only where they differ. ⚠ Recorded for the same reason `adj_as_of` is
    #: (DE-30): two panels over identical dates fetched under different symbols
    #: are **different data**, and a panel that does not say which is not
    #: reproducible.
    fetched_as: dict = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return not self.failures

    @property
    def short_history(self) -> tuple[str, ...]:
        """★ Names with materially less history than the panel's median.

        ⚠ **Not a failure and not ignorable**: a name with 40 rows in a panel
        whose median is 900 will carry NaNs in every trailing window, and
        `coverage()` is what decides whether it may be the actionable pick
        (MT-11). This *names* them so the decision is visible.
        """
        counts = sorted(self.rows_by_ticker.values())
        if not counts:
            return ()
        median = counts[len(counts) // 2]
        return tuple(sorted(t for t, n in self.rows_by_ticker.items()
                            if n < median * 0.5))

    def to_json_obj(self) -> dict:
        return {"requested": len(self.requested), "fetched": len(self.fetched),
                "complete": self.complete,
                "failures": [f.to_json_obj() for f in self.failures],
                "short_history": list(self.short_history)}


def _classify(exc) -> tuple[str, str]:
    """DE-49 — ★ **a 402 is a subscription boundary, not a missing security.**

    ⚠ DE-46 already says a 402 is never read as *"no data"*. The two need
    **different remedies**: an absent security is a universe error to correct;
    a plan-gated one is a **declaration** problem — the name should not be in
    the universe while the plan does not cover it, and discovering that at
    fetch time is discovering it too late.
    """
    from src.data_engine.errors import PlanGatedError

    if isinstance(exc, PlanGatedError):
        return PLAN_GATED, str(exc)[:180]
    return NO_SOURCE, f"{type(exc).__name__}: {exc}"[:180]


#: DE-80 — seconds between the first pass and the single retry pass.
RETRY_PAUSE_SECONDS = 10.0


def fetch_universe(source, tickers, *, start: date, end: date,
                   fetch=None, symbol_for=None, retry_pause: float | None = None,
                   sleep=None) -> tuple[dict, AssemblyReport]:
    """Fetch every name. ★ **Every failure is collected, then reported once.**

    ⚠ Raising on the first bad ticker tells you about one name per run, and a
    130-name universe with three problems then takes three runs to diagnose.

    ★★ **`symbol_for` resolves a renamed name to the symbol the vendor answers
    to** (§6B, DE-63). *Measured 2026-08-28:* `BNY` returns **164 bars covering
    the whole `BK` period** while `BK` returns 122 and stops at the changeover —
    so a universe still naming `BK` silently loses the name to staleness while
    `universe_n` keeps counting it.

    ⚠ **Frames stay keyed by the UNIVERSE ticker.** The resolution is a fetch
    detail; re-keying the panel here would make every downstream join disagree
    with the universe it was built from. What was actually requested is recorded
    in `fetched_as`.

    ★ `symbol_for=None` is the identity map, so an unmapped repo behaves exactly
    as before — this is a no-op until the symbol history is populated.
    """
    resolve_symbol = symbol_for or (lambda ticker: ticker)
    call = fetch or (lambda symbol: source.raw_prices(symbol, start, end))
    frames, counts, fetched_as = {}, {}, {}

    def one_pass(names) -> list:
        failed = []
        for ticker in names:
            symbol = resolve_symbol(ticker) or ticker
            if symbol != ticker:
                fetched_as[ticker] = symbol
            try:
                rows = call(symbol)
            except Exception as exc:                        # noqa: BLE001
                reason, detail = _classify(exc)
                failed.append(TickerFailure(ticker, reason, detail))
                continue
            if rows is None or len(rows) == 0:
                failed.append(TickerFailure(
                    ticker, EMPTY_WINDOW,
                    f"the source returned no rows for {start}..{end}"))
                continue
            frames[ticker] = rows
            counts[ticker] = len(rows)
        return failed

    failures = one_pass(tickers)
    if failures:
        # ★ DE-80 (DX-168) — ONE retry pass after a pause: an empty answer at the
        #   start of a burst is often transient. ⚠ Still named if it fails again.
        import time as _time

        (sleep or _time.sleep)(RETRY_PAUSE_SECONDS if retry_pause is None else retry_pause)
        failures = one_pass([f.ticker for f in failures])

    report = AssemblyReport(requested=tuple(tickers), fetched=tuple(frames),
                            failures=tuple(failures), rows_by_ticker=counts,
                            fetched_as=fetched_as)
    return frames, report


def assert_complete(report: AssemblyReport) -> AssemblyReport:
    """DE-13 — ★ **fails the run.** *It is not dropped, and it does not become a
    row of NaNs.*"""
    from src.data_engine.errors import UniverseIncompleteError

    if not report.complete:
        raise UniverseIncompleteError(report.failures, len(report.requested))
    return report


def assemble_universe_panel(source, tickers, *, start: date, end: date,
                            events, adj_as_of, fetch=None,
                            strict: bool = True) -> tuple[pd.DataFrame,
                                                          AssemblyReport]:
    """One CT-7.1 panel over the whole universe, or a loud failure.

    ⚠ **`strict=False` is for diagnosis, never for a run.** It returns the panel
    it could build *and* the report, so a caller can see what is missing — but
    DE-13 means a run does not proceed on it.
    """
    from src.data_engine.pit.adjustment import build_price_panel

    frames, report = fetch_universe(source, tickers, start=start, end=end,
                                    fetch=fetch)
    if strict:
        assert_complete(report)
    if not frames:
        from src.data_engine.errors import UniverseIncompleteError

        raise UniverseIncompleteError(report.failures, len(report.requested))

    raw = pd.concat([_as_frame(rows) for rows in frames.values()],
                    ignore_index=True)
    panel = build_price_panel(raw, events, adj_as_of)
    # ★ The panel must carry every name the fetch claimed. A concat that lost
    #   one would be the LEFT JOIN incident in a new shape.
    built = set(panel["ticker"].unique())
    lost = sorted(set(frames) - built)
    if lost:
        from src.data_engine.errors import UniverseIncompleteError

        raise UniverseIncompleteError(
            tuple(TickerFailure(t, NO_SOURCE, "fetched, then lost in assembly")
                  for t in lost), len(report.requested))
    return panel, report


def _as_frame(rows) -> pd.DataFrame:
    if isinstance(rows, pd.DataFrame):
        return rows
    return pd.DataFrame([r.to_json_obj() if hasattr(r, "to_json_obj") else r
                         for r in rows])
