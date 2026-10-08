"""DE-74 / AC-7.92 (D-07) · MT-53 / AC-4.35 (D-04) — a long command shows it is alive.

★ Shared because it is generic: the D-07 ingest commands and the D-04 training run both use it,
and neither should import the other's internals for a timer.

✏ *2026-10-07 (Victor):* `python -m src.data_engine.ingest events --years 10` runs a long time
in silence, which reads exactly like a hung process.

```text
  ⏱ events · 2m15s elapsed · now: earnings          ← every `interval` seconds, to stderr
  ✓ earnings · 1m40s                                 ← when a stage ends
  ⏱ events · done in 12m05s                          ← when the command ends
```

★ **Whole lines, never a redrawn one.** The stages print their own results to stdout between
ticks; a `\\r` redraw would splice the two into one garbled line. ★ stderr, so a redirected stdout
still carries only the results.
"""

from __future__ import annotations

import sys
import threading
import time

#: Seconds between ticks — often enough to see it move, rare enough not to drown the results.
DEFAULT_INTERVAL = 15.0


def fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


class Heartbeat:
    """Elapsed time and the current stage, printed on a timer; stage and total durations.

    `clock` and `start_thread=False` exist so the behaviour is testable without real time.
    """

    def __init__(self, label: str, *, stream=None, interval: float = DEFAULT_INTERVAL,
                 clock=time.monotonic, start_thread: bool = True) -> None:
        self.label, self.stream, self.interval, self.clock = (
            label, stream or sys.stderr, interval, clock)
        self._started = clock()
        self._stage, self._stage_started = "starting", self._started
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        if start_thread:
            self._thread = threading.Thread(target=self._run, daemon=True,
                                            name=f"heartbeat:{label}")
            self._thread.start()

    @property
    def alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _write(self, line: str) -> None:
        with self._lock:
            self.stream.write(line + "\n")
            self.stream.flush()

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            self.tick()

    def tick(self) -> None:
        elapsed = fmt_duration(self.clock() - self._started)
        self._write(f"  ⏱ {self.label} · {elapsed} elapsed · now: {self._stage}")

    def stage(self, name: str) -> None:
        """Close the current stage (reporting its duration) and open `name`."""
        now = self.clock()
        if self._stage != "starting":
            self._write(f"  ✓ {self._stage} · {fmt_duration(now - self._stage_started)}")
        self._stage, self._stage_started = name, now

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        now = self.clock()
        if self._stage != "starting":
            self._write(f"  ✓ {self._stage} · {fmt_duration(now - self._stage_started)}")
            self._stage = "starting"
        self._write(f"  ⏱ {self.label} · done in {fmt_duration(now - self._started)}")

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        self.close()
