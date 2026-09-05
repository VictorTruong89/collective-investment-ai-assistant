"""§6B — identity. ★ A ticker is a label with a validity interval, never an
instrument (DE-61)."""

from src.data_engine.symbology.master import (
    SymbolHistory, current_symbol, fetch_symbol_for, resolve,
)
from src.data_engine.symbology.detect import detect_changes, sec_snapshot

__all__ = ["SymbolHistory", "current_symbol", "fetch_symbol_for", "resolve",
           "detect_changes", "sec_snapshot"]
