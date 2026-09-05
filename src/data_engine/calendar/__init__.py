"""The pre-run corporate-action gate — §6A.

⚠ This package shadows the stdlib `calendar` module INSIDE `src.data_engine`
only. Every import in this tree is absolute (**IM-5**), so `import calendar`
elsewhere still resolves to the stdlib; the name is §6A's and matches the module
decomposition in `L1-data-engine.md` §4.
"""

from src.data_engine.calendar.check import (
    ClassResult, EventFeed, calendar_check, news_status, price_adjustment_status,
    require_check,
)
from src.data_engine.calendar.classes import (
    BY_NAME, CHECKED, EVENT_CLASSES, EventClass, NEWS_DEPTH_DAYS, unchecked,
)
from src.data_engine.calendar.probe import KNOWN_ANSWERS, ProbeResult, run_probe
from src.data_engine.calendar.store import CachedEventFeed, EventStore

__all__ = ["BY_NAME", "CHECKED", "CachedEventFeed", "ClassResult", "EVENT_CLASSES",
           "EventClass", "EventFeed", "EventStore", "KNOWN_ANSWERS", "NEWS_DEPTH_DAYS",
           "ProbeResult", "calendar_check", "news_status", "price_adjustment_status",
           "require_check", "run_probe", "unchecked"]
