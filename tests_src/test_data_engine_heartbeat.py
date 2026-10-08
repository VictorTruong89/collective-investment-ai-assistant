"""D-07 — DE-74 / AC-7.92: a long `ingest` command shows it is alive. ✏ Written 2026-10-07.

Victor: `ingest events --years 10` runs a long time in silence. The heartbeat is driven
here by a FAKE clock and explicit `tick()` calls, so nothing depends on real time.
"""

from __future__ import annotations

import io
import time

from src.shared.progress import Heartbeat


class _Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_ac_7_92_ticks_name_the_elapsed_time_and_the_stage():
    clock, out = _Clock(), io.StringIO()
    beat = Heartbeat("events", stream=out, clock=clock, start_thread=False)
    beat.stage("earnings")
    clock.t = 135.0
    beat.tick()
    assert "⏱ events · 2m15s elapsed · now: earnings" in out.getvalue()


def test_ac_7_92_each_stage_reports_its_duration_and_the_command_its_total():
    clock, out = _Clock(), io.StringIO()
    beat = Heartbeat("events", stream=out, clock=clock, start_thread=False)
    beat.stage("splits & dividends")
    clock.t = 40.0
    beat.stage("earnings")
    clock.t = 3725.0
    beat.close()
    text = out.getvalue()
    assert "✓ splits & dividends · 40s" in text
    assert "✓ earnings · 1h01m25s" in text      # 3725 − 40 = 3685 s
    assert "⏱ events · done in 1h02m05s" in text


def test_ac_7_92_whole_lines_never_a_redrawn_line():
    """Stage output prints between ticks; a carriage-return redraw would garble it."""
    clock, out = _Clock(), io.StringIO()
    beat = Heartbeat("events", stream=out, clock=clock, start_thread=False)
    beat.stage("news")
    clock.t = 5.0
    beat.tick()
    assert "\r" not in out.getvalue() and out.getvalue().endswith("\n")


def test_ac_7_92_the_background_thread_ticks_and_stops_cleanly():
    out = io.StringIO()
    beat = Heartbeat("events", stream=out, interval=0.01)
    beat.stage("symbols")
    time.sleep(0.05)
    beat.close()
    assert "now: symbols" in out.getvalue()
    assert not beat.alive, "the thread is stopped after close()"
    lines_after = out.getvalue()
    time.sleep(0.03)
    assert out.getvalue() == lines_after, "nothing printed after close()"


def test_ac_7_92_the_ingest_command_runs_inside_a_heartbeat():
    """The `events`, `symbols` and `facts` subcommands are wrapped (not `status`, which is instant)."""
    import inspect

    from src.data_engine.ingest import __main__ as cli

    source = inspect.getsource(cli.main)
    assert "Heartbeat(" in source
    events = inspect.getsource(cli._events)
    assert events.count(".stage(") >= 8, "each sweep in `events` names its stage"
