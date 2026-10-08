"""DX-159 — the per-filing-date replay. FE-40 / AC-2.47 · DE-75 / AC-7.93 · DE-76 / AC-7.94.

✏ Written 2026-10-07 (Victor: *"build the per-filing-date replay"*).

⚠ *Measured on the real ledger:* training read `get_fundamentals` once at today and joined the
result across ten years. A 10-K re-files two years of comparatives, so every period sat at its
LATEST re-filing date and the panel ran ~1 year stale (13 % of points PIT-correct, median 371 d).

The fixture is that shape in miniature — one filer, four filings:

    A1 2023-04-25  10-Q   Q1-2023  revenue 100, net income 10
    A2 2024-04-30  10-Q   Q1-2024  revenue 120, net income 12   (+ Q1-2023 re-filed)
    A3 2024-07-15  10-Q/A Q1-2024  net income AMENDED 12 → 11   (revenue re-filed)
    A4 2025-04-30  10-Q   Q1-2025  revenue 130, net income 13   (+ Q1-2024 re-filed)

Hermetic: a tmp fact ledger, no network.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.data_engine.pit.ledger import FactLedger
from src.data_engine.pit.models import UniverseEntry
from src.data_engine.service import DataEngine
from src.data_engine.universe.membership import Universe
from tests_src.data_engine_fixtures import fact

T = "ADM"
TODAY = date(2026, 10, 7)
Q23 = dict(start=date(2023, 1, 1), end=date(2023, 3, 31))
Q24 = dict(start=date(2024, 1, 1), end=date(2024, 3, 31))
Q25 = dict(start=date(2025, 1, 1), end=date(2025, 3, 31))


def _facts():
    def f(acc, filed, period, rev, ni):
        return [fact(T, "Revenues", accession=acc, filed=filed, value=rev * 100, **period),
                fact(T, "NetIncomeLoss", accession=acc, filed=filed, value=ni * 100, **period)]

    return (f("A1", date(2023, 4, 25), Q23, 100, 10)
            + f("A2", date(2024, 4, 30), Q24, 120, 12) + f("A2", date(2024, 4, 30), Q23, 100, 10)
            + f("A3", date(2024, 7, 15), Q24, 120, 11)
            + f("A4", date(2025, 4, 30), Q25, 130, 13) + f("A4", date(2025, 4, 30), Q24, 120, 11))


@pytest.fixture
def engine(tmp_path):
    ledger = FactLedger(tmp_path / "facts")
    ledger.append(_facts())
    universe = Universe([UniverseEntry(ticker=T, cik="0000007084",
                                       filer_class="10-K/10-Q", source="edgar")])
    return DataEngine(universe=universe, fact_ledger=ledger, observation_ledger=None,
                      price_source=None)


PANEL_DATES = ["2023-06-01", "2024-06-03", "2024-08-01", "2025-06-02"]


def _panel():
    return pd.DataFrame({"ticker": T, "date": pd.to_datetime(PANEL_DATES)})


# ── AC-7.93 · DE-75 — the ledger as it stood at each filing date ─────────────

def test_ac_7_93_one_snapshot_per_filing_date_each_equal_to_a_read_then(engine):
    history = engine.get_fundamentals_history(T, as_of=TODAY)
    assert [d for d, _ in history] == [date(2023, 4, 25), date(2024, 4, 30),
                                       date(2024, 7, 15), date(2025, 4, 30)]
    for filed, rows in history:
        pd.testing.assert_frame_equal(_stable(rows), _stable(engine.get_fundamentals(T, as_of=filed)))


def _stable(rows):
    """`ingested_at` is stamped at read time — every other column must match."""
    return rows.drop(columns=["ingested_at"], errors="ignore")


def test_ac_7_93_a_filing_after_as_of_is_absent(engine):
    history = engine.get_fundamentals_history(T, as_of=date(2024, 7, 1))
    assert [d for d, _ in history] == [date(2023, 4, 25), date(2024, 4, 30)]


def test_ac_7_93_as_of_is_required(engine):
    from src.data_engine.errors import AsOfRequiredError

    with pytest.raises(AsOfRequiredError):
        engine.get_fundamentals_history(T)


# ── AC-2.47 · FE-40 — the panel carries what a run on each date would compute ─

def _joined(**fundamentals):
    from src.feature_engineer.fundamental.build import joined_rows

    return joined_rows(_panel(), **fundamentals)


def test_ac_2_47_a_single_read_at_today_is_stale_the_defect_pinned(engine):
    """⚠ The DX-159 shape, kept as a known answer: one read at today puts Q1-2024 at its
    re-filing (2025-04-30), so on 2024-06-03 the panel shows Q1-2023."""
    got = _joined(rows_by_ticker={T: engine.get_fundamentals(T, as_of=TODAY)})
    assert pd.Timestamp(got.iloc[1]["period_end"]) == pd.Timestamp(2023, 3, 31)


def test_ac_2_47_the_replay_shows_each_period_from_its_first_filing(engine):
    got = _joined(history_by_ticker={T: engine.get_fundamentals_history(T, as_of=TODAY)})
    periods = [pd.Timestamp(p).date() for p in got["period_end"]]
    assert periods == [date(2023, 3, 31), date(2024, 3, 31), date(2024, 3, 31),
                       date(2025, 3, 31)]


def test_ac_2_47_an_amended_figure_appears_only_from_the_amendment(engine):
    got = _joined(history_by_ticker={T: engine.get_fundamentals_history(T, as_of=TODAY)})
    assert list(got["net_income"].astype(float)) == [10.0, 12.0, 11.0, 13.0]


def test_ac_2_47_every_date_equals_a_single_read_at_that_date(engine):
    """★ The general statement: the replay is the daily computation, done on each date."""
    from src.feature_engineer.fundamental.build import per_filing
    from src.feature_engineer.fundamental.items import as_of_join

    got = _joined(history_by_ticker={T: engine.get_fundamentals_history(T, as_of=TODAY)})
    for i, d in enumerate(PANEL_DATES):
        one = pd.DataFrame({"ticker": [T], "date": [pd.Timestamp(d)]})
        expected = as_of_join(one, per_filing(engine.get_fundamentals(T, as_of=date.fromisoformat(d))))
        for col in ("period_end", "filing_date", "net_income", "revenue", "f_net_margin"):
            assert str(got.iloc[i][col]) == str(expected.iloc[0][col]), (d, col)


def test_ac_2_47_the_fundamental_block_accepts_a_history(engine):
    """The 45-feature block builds from a history and agrees with the joined rows."""
    from src.feature_engineer.fundamental.build import build

    block = build(_panel(), history_by_ticker={T: engine.get_fundamentals_history(T, as_of=TODAY)})
    assert list(block["f_net_margin"].astype(float).round(4)) == [0.1, 0.1, round(11 / 120, 4), 0.1]


# ── AC-7.94 · DE-76 — a restatement is handled only by a PIT caller ──────────

def _amendment():
    from src.data_engine.contracts.envelopes import BLOCK, Finding

    return Finding(T, "restatement_amended", BLOCK, date(2024, 11, 18), date(2024, 11, 18),
                   {"form": "10-K/A"}, "edgar:submissions")


def test_ac_7_94_a_restatement_is_unhandled_by_default():
    from src.data_engine.calendar.gate import adjustment_handling

    assert adjustment_handling([_amendment()], adj_as_of=TODAY) == {}


def test_ac_7_94_a_pit_caller_records_the_handling():
    from src.data_engine.calendar.gate import adjustment_handling

    handled = adjustment_handling([_amendment()], adj_as_of=TODAY, fundamentals_pit=True)
    why = handled[(T, "restatement_amended", date(2024, 11, 18))]
    assert "as filed before the amendment" in why and "DE-75" in why


def test_ac_7_94_training_declares_pit_fundamentals():
    import inspect

    from src.models.train import run

    assert "fundamentals_pit=True" in inspect.getsource(run.training_calendar_check)
    assert "fundamentals_histories(" in inspect.getsource(run.build_training_panel)


def test_ac_7_93_since_keeps_the_last_snapshot_before_it_and_everything_after(engine):
    history = engine.get_fundamentals_history(T, as_of=TODAY, since=date(2024, 6, 1))
    assert [d for d, _ in history] == [date(2024, 4, 30), date(2024, 7, 15), date(2025, 4, 30)]


def test_ac_2_47_a_trimmed_history_joins_identically_from_its_start(engine):
    """`since` is a speed-up only: from the panel's first date on, nothing changes."""
    full = _joined(history_by_ticker={T: engine.get_fundamentals_history(T, as_of=TODAY)})
    trimmed = _joined(history_by_ticker={
        T: engine.get_fundamentals_history(T, as_of=TODAY, since=date(2023, 6, 1))})
    pd.testing.assert_frame_equal(full, trimmed)


def test_ac_2_47_parallel_replay_is_identical_to_serial(engine):
    """Two keys so the pool is actually used (one ticker short-circuits to serial)."""
    from src.feature_engineer.fundamental.build import _replay_all

    history = engine.get_fundamentals_history(T, as_of=TODAY)
    serial = _replay_all({"X": history, "Y": history}, workers=1)
    pooled = _replay_all({"X": history, "Y": history}, workers=2)
    for key in ("X", "Y"):
        pd.testing.assert_frame_equal(_stable(serial[key]), _stable(pooled[key]))
