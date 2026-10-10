"""D-04 — MT-62 / AC-4.44: training reports the EXTERNAL residual correlation. ✏ 2026-10-08.

Hermetic: a fake FMP client serves flat-trend ETF bars; no network.
"""

from __future__ import annotations

import inspect
from datetime import date

import numpy as np
import pandas as pd

AS_OF = date(2026, 10, 8)


class _FakeClient:
    """Serves a random-walk price series per symbol; no splits, no dividends."""

    def __init__(self):
        self.calls = []

    def get(self, endpoint, **params):
        self.calls.append((endpoint, params.get("symbol")))
        if "historical-price-eod" not in endpoint:
            return []
        rng = np.random.default_rng(abs(hash(params["symbol"])) % 2**32)
        days = pd.bdate_range(params["from"], params["to"])
        px = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(days))))
        return [{"date": d.strftime("%Y-%m-%d"), "adjOpen": p, "adjHigh": p, "adjLow": p,
                 "adjClose": p, "open": p, "high": p, "low": p, "close": p, "volume": 1000}
                for d, p in zip(days, px, strict=True)]


def test_ac_4_44_factor_returns_are_built_like_the_labels():
    from src.models.train.run import SECTOR_ETFS, external_factor_returns

    client = _FakeClient()
    market, sectors = external_factor_returns(client, start=date(2025, 1, 2), as_of=AS_OF,
                                              horizon_days=21)
    assert market.name == "SPY" and len(market) > 100
    assert set(sectors.columns) == set(SECTOR_ETFS)          # keyed by GICS sector name
    assert {s for _, s in client.calls} >= {"SPY", *SECTOR_ETFS.values()}


def test_ac_4_44_an_unfetchable_etf_is_named_and_left_out():
    from src.models.train.run import external_factor_returns

    class _Broken(_FakeClient):
        def get(self, endpoint, **params):
            if params.get("symbol") == "XLRE":
                raise RuntimeError("402")
            return super().get(endpoint, **params)

    _, sectors = external_factor_returns(_Broken(), start=date(2025, 1, 2), as_of=AS_OF,
                                         horizon_days=21)
    assert "Real Estate" not in sectors.columns


def test_ac_4_44_training_reports_it_and_saves_it():
    from src.models.train import __main__ as train
    from src.models.train.run import decide_promotion

    body = inspect.getsource(train._train)
    assert "external_residual_correlation(" in body and "external_breadth=" in body
    assert "external_breadth" in inspect.signature(decide_promotion).parameters
