"""Structured, correlated logging (L2-shared-infrastructure §7).

```
╔══════════════════════════════════════════════════════════════════╗
║  LG-1 — A LOG IS NOT THE AUDIT TRAIL.                            ║
║                                                                  ║
║  D-11's journal and trade log are (INV-006, append-only). Logs   ║
║  are diagnostic, may be rotated, and NOTHING may depend on one   ║
║  for a fact about the book.                                      ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **LG-5 is the rule with a scar attached**: a degraded result logs at WARNING
or above *and also raises*. **A log line is not a substitute for a failure — the
two discipline-card incidents were both logged.** `degraded()` below makes that
mechanical, so the pairing cannot be half-remembered at a call site.
"""

from __future__ import annotations

import json
import logging as _stdlib_logging
import sys
from typing import Any

from src.shared.errors import PipelineError

_CONFIGURED = False


class _JsonFormatter(_stdlib_logging.Formatter):
    """LG-3 — key/value, not formatted prose.

    A message that must be regex-parsed to be useful is a data structure someone
    declined to declare.
    """

    def format(self, record: _stdlib_logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "run_id": getattr(record, "run_id", None),
            "msg": record.getMessage(),
        }
        extra = getattr(record, "fields", None)
        if extra:
            payload.update(extra)
        if record.exc_info:
            payload["exc_type"] = record.exc_info[0].__name__
        # default=str routes any object through __str__ — which is what makes a
        # Secret render as its redaction rather than its value (SC-3, LG-4).
        return json.dumps(payload, default=str, sort_keys=True)


class Logger:
    """A thin wrapper that guarantees `run_id` on every record (LG-2)."""

    __slots__ = ("_log", "_run_id")

    def __init__(self, name: str, run_id: str) -> None:
        self._log = _stdlib_logging.getLogger(name)
        self._run_id = run_id

    def _emit(self, level: int, msg: str, **fields: Any) -> None:
        self._log.log(level, msg, extra={"run_id": self._run_id, "fields": fields})

    def debug(self, msg: str, **f: Any) -> None:
        self._emit(_stdlib_logging.DEBUG, msg, **f)

    def info(self, msg: str, **f: Any) -> None:
        self._emit(_stdlib_logging.INFO, msg, **f)

    def warning(self, msg: str, **f: Any) -> None:
        self._emit(_stdlib_logging.WARNING, msg, **f)

    def error(self, msg: str, **f: Any) -> None:
        self._emit(_stdlib_logging.ERROR, msg, **f)

    @property
    def run_id(self) -> str:
        return self._run_id


def configure(stream=None, level: int = _stdlib_logging.INFO) -> None:
    """Install the JSON handler. Called ONCE by the application entry point.

    ⚠ Deliberately separate from `logger()`. An earlier draft configured the
    root logger lazily on the first `logger()` call, and the test suite caught
    what that costs: whichever test ran first silently replaced every handler
    installed by anything else, so behaviour depended on collection order.

    A library that reconfigures root logging on import or on first use is a
    library that cannot be composed — the application owns handlers, D-00 owns
    the record shape.
    """
    global _CONFIGURED
    handler = _stdlib_logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(_JsonFormatter())
    root = _stdlib_logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
    _CONFIGURED = True


def logger(name: str, run_id: str) -> Logger:
    """Get a correlated logger. `run_id` is required — LG-2 has no default.

    One run must be reconstructible across twelve domains, and a record with a
    missing correlation key is a record that belongs to no run.
    """
    if not run_id:
        raise ValueError("run_id is required on every log record (LG-2)")
    return Logger(name, run_id)


def degraded(log: Logger, message: str, error: PipelineError, **fields: Any):
    """LG-5 / P5 — log at WARNING **and** raise. Never one without the other.

    ★ This exists because the pairing is exactly what gets half-remembered. Both
    real incidents in this repo were logged and then proceeded: a discipline
    card built from a failed LLM narrative, and one built from an absent
    narrative, each emailed as a genuine recommendation with no stop and no
    targets.

    Always raises; the `NoReturn` shape is intentional so a caller cannot treat
    it as a soft warning.
    """
    log.warning(message, degraded=True, error_type=type(error).__name__, **fields)
    raise error
