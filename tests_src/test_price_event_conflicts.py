"""DE-79 / AC-7.97 · MT-63 / AC-4.45 — vendor events that contradict the vendor's prices. ✏ 2026-10-08.

⚠ Found running DE-78 over the universe: FMP's KDP history is in post-merger units (≈ $19.91 on
2018-07-09) while its 2018-07-10 special dividend is in pre-merger units ($103.75). The factor
`1 − 103.75/19.91` is negative; DE-43 refused the whole 510-name panel without naming the ticker.
"""

from __future__ import annotations

import inspect
from datetime import date

import pandas as pd

from src.data_engine.pit.models import CorporateEvent

ADJ = date(2026, 10, 8)


def _raw(ticker, close):
    rows = [{"ticker": ticker, "date": d, "open_minor": close, "high_minor": close,
             "low_minor": close, "close_minor": close, "volume": 1, "currency": "USD",
             "source": "fmp"} for d in pd.bdate_range("2018-07-02", periods=10)]
    return pd.DataFrame(rows)


def _div(ticker, cash_minor):
    return CorporateEvent(ticker, "dividend", date(2018, 7, 10), date(2018, 6, 20),
                          {"cash_minor": cash_minor, "currency": "USD"}, "fmp:dividends")


def test_ac_7_97_a_dividend_above_the_prior_close_is_named_with_its_numbers():
    from src.data_engine.pit.adjustment import price_event_conflicts

    raw = pd.concat([_raw("KDP", 1991), _raw("OK", 1991)])
    found = price_event_conflicts(raw, [_div("KDP", 10375), _div("OK", 50)], ADJ)
    assert set(found) == {"KDP"}
    assert "2018-07-10" in found["KDP"] and "103.75" in found["KDP"] and "19.91" in found["KDP"]


def test_ac_7_97_no_events_no_conflicts():
    from src.data_engine.pit.adjustment import price_event_conflicts

    assert price_event_conflicts(_raw("OK", 1000), [], ADJ) == {}


def test_ac_4_45_training_excludes_conflicting_names_by_name():
    from src.models.train import __main__ as train

    body = inspect.getsource(train._train)
    assert "price_event_conflicts(" in body and "inputs.unresolved" in body
