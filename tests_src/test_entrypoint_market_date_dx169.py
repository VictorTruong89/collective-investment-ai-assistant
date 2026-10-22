"""OR-59 / AC-8.47 (`DX-169`) — the daily run dates itself in New York, not UTC. ✏ 2026-10-20.

⚠ A manual run on a Friday at 21:30 EDT read Saturday (UTC) and was refused NOT_TRADING_DAY.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace

from src.orchestration import entrypoint


def test_ac_8_47_a_friday_evening_in_new_york_is_still_friday():
    """AC-8.47 — 21:30 EDT Friday 2026-10-09 is 01:30 UTC Saturday; the run's date is Friday."""
    now = datetime(2026, 10, 10, 1, 30, tzinfo=timezone.utc)
    assert entrypoint.market_date(now) == date(2026, 10, 9)


def test_ac_8_47_winter_time_shifts_the_boundary_by_an_hour():
    """AC-8.47 — 19:30 EST is 00:30 UTC the next day; still the New York date."""
    now = datetime(2026, 12, 4, 0, 30, tzinfo=timezone.utc)
    assert entrypoint.market_date(now) == date(2026, 12, 3)


def test_ac_8_47_main_defaults_to_the_new_york_date(monkeypatch):
    """AC-8.47 — `main` takes its default as_of from `market_date`, never the UTC clock."""
    seen = {}

    class _Stop(Exception):
        pass

    def capture(as_of):
        seen["as_of"] = as_of
        raise _Stop

    monkeypatch.setattr(entrypoint, "market_date", lambda: date(2026, 10, 9))
    monkeypatch.setattr(entrypoint, "build_orchestrator", lambda: SimpleNamespace(trigger=lambda **_: None))
    monkeypatch.setattr(entrypoint, "git_state", lambda: ("sha", False))
    monkeypatch.setattr(entrypoint, "_day_bar", capture)
    try:
        entrypoint.main([])
    except _Stop:
        pass
    assert seen["as_of"] == date(2026, 10, 9)
