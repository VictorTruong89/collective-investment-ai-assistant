"""AC-8.48 / OR-60 — the daily calendar check and amended filings.

*Found on the first live card, 2026-10-20:* nine 10-K/A and 10-Q/A inside the
200-day window halted the card while training, reading the same store, records
them handled (DE-76). The card ranks only the `as_of` row, read at `as_of`.
"""
from datetime import date
from types import SimpleNamespace

import pandas as pd
import pytest

AS_OF = date(2026, 10, 20)


def _ctx(tmp_path, *, feature_names, findings):
    from src.data_engine.calendar.store import EventStore

    store = EventStore(tmp_path)
    store.upsert(findings)
    for cls in {f.event_class for f in findings}:
        store.record_refresh(cls, date(2026, 1, 1), AS_OF, covers_tickers=("TSLA", "WBD"))
    contract = SimpleNamespace(features=tuple(SimpleNamespace(name=n) for n in feature_names))
    return SimpleNamespace(
        universe=("TSLA", "WBD"), as_of=AS_OF, adj_as_of=AS_OF, events=(),
        event_store_root=str(tmp_path), contract=contract,
        raw_prices=pd.DataFrame({"date": [pd.Timestamp("2026-04-03"), pd.Timestamp(AS_OF)]}))


def _amended():
    from src.data_engine.contracts import BLOCK, Finding

    return Finding("TSLA", "restatement_amended", BLOCK, date(2026, 4, 30), date(2026, 4, 30),
                   {"form": "10-K/A"}, "edgar:submissions")


def _delisting():
    from src.data_engine.contracts import BLOCK, Finding

    return Finding("WBD", "delisting", BLOCK, date(2026, 10, 7), date(2026, 10, 7),
                   {"exchange": "NASDAQ"}, "fmp:delisted-companies")


def _check(ctx):
    from src.orchestration.jobs.wiring import _calendar_check

    return _calendar_check(None, SimpleNamespace(run_id="t"), ctx)


def test_ac_8_48_a_fundamentals_card_records_an_amended_filing_as_handled(tmp_path):
    report = _check(_ctx(tmp_path, feature_names=("mom_21", "f_net_margin"),
                         findings=[_amended()]))
    found = next(f for f in report.findings if f.event_class == "restatement_amended")
    assert found.handled is True and "DE-76" in found.handling


def test_ac_8_48_a_delisting_still_halts(tmp_path):
    from src.data_engine.errors import UnhandledBlockError

    with pytest.raises(UnhandledBlockError, match="WBD delisting"):
        _check(_ctx(tmp_path, feature_names=("mom_21", "f_net_margin"),
                    findings=[_amended(), _delisting()]))


def test_ac_8_48_a_price_only_card_does_not_opt_in(tmp_path):
    """A contract with no `f_*` feature reads no fundamentals — nothing to replay."""
    from src.data_engine.errors import UnhandledBlockError

    with pytest.raises(UnhandledBlockError, match="TSLA restatement_amended"):
        _check(_ctx(tmp_path, feature_names=("mom_21", "vol_21"), findings=[_amended()]))
