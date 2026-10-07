"""D-07 — AC-7.18: a converted value is accompanied by the FxRate used (CT-7.5, FX-2, FX-3).

✏ Written 2026-10-06 (L9 §8 D4). D-07 converts no amounts itself: it SUPPLIES rates
(`DataEngine.get_fx`) and RECORDS the rate a consumer used on its provenance
(`DataEngine.provenance(..., fx_rate=...)` → `fx_rate_used`). `Money.convert_with_record`
(L2-shared-money AC-M.10) emits the converted amount and its rate together; this pins
D-07's half. Local only — no network, no FMP call.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from src.data_engine.pit.models import UniverseEntry
from src.data_engine.service import DataEngine
from src.data_engine.universe.membership import Universe
from src.shared.money import FxRate

AS_OF = date(2026, 8, 28)


def _engine(fx_source=None):
    universe = Universe([UniverseEntry(ticker="NVDA", cik="0001045810",
                                       filer_class="10-K/10-Q", source="edgar")])
    return DataEngine(universe=universe, fact_ledger=None, observation_ledger=None,
                      price_source=None, fx_source=fx_source)


def _rate():
    return FxRate(pair="USDCAD", rate=Decimal("1.3742"),
                  as_of=datetime(2026, 8, 28, 20, 0, tzinfo=timezone.utc), source="FMP")


def test_ac_7_18_the_provenance_carries_the_rate_that_was_used():
    """AC-7.18 — ★ a converted figure is reproducible only beside its rate."""
    rate = _rate()
    prov = _engine().provenance("NVDA", AS_OF, fx_rate=rate)
    assert prov.fx_rate_used == rate.to_json_obj()
    assert prov.fx_rate_used["pair"] == "USDCAD" and prov.fx_rate_used["rate"] == "1.3742"


def test_ac_7_18_no_conversion_means_no_rate_is_claimed():
    """AC-7.18 — a figure that was not converted records NO rate, never a default."""
    assert _engine().provenance("NVDA", AS_OF).fx_rate_used is None


def test_ac_7_18_no_rate_source_gives_none_never_a_guess():
    """FX-3 / EH-2 — no rate, no number: with no source `get_fx` returns `None`
    (*legitimately absent*), never a plausible default; the dependent value is then
    reported unavailable."""
    assert _engine().get_fx("USDCAD", AS_OF) is None


def test_ac_7_18_get_fx_returns_the_sources_rate_unchanged():
    """The rate a consumer converts with is the one the source gave — then recorded."""
    rate = _rate()

    class _Source:
        def rate(self, pair, as_of):
            assert (pair, as_of) == ("USDCAD", AS_OF)
            return rate

    assert _engine(_Source()).get_fx("USDCAD", AS_OF) is rate
