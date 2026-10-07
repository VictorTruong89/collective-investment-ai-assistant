"""RC-68 — the ingest log: RC-11 built. Append-only (INV-006), one entry per account per recording.

★ **Why it exists.** RC-11 says *"a changed hash for a covered window is a RESTATEMENT,
recorded not overwritten"* — and `file_hash()` existed with nothing storing it, so a
download whose old rows BMO had silently corrected simply replaced the old file.

```text
  entry = {account_id, recorded_at, file, file_hash, window: [first, last], rows: [...]}

  compared with the LAST entry for the account:
    identical file_hash                      -> unchanged   (AC-11.9: a no-op)
    rows inside the old window changed      -> RESTATEMENT (removed / added named)
    rows only after the old window           -> new_activity
    the window now starts later              -> window_starts_later (history dropped)
```

⚠ **Rows are a MULTISET, not a set**: two identical tranches on one day are legitimate
(H-1), and a set would hide one of them disappearing.

★ A row's key is **readable** — date, activity, symbol, quantity, price, total, currency,
description — so a restatement names what changed instead of quoting a hash. The log
lives in `.state/broker/`, beside the statements, and is git-ignored with them (RC-66).
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def row_key(activity) -> str:
    """The verbatim content of one row — ⚠ never its file name or row number,
    which change when BMO re-orders or re-names an export without changing a fact."""
    def fmt(value):
        return "" if value is None else f"{value}"

    return "|".join([
        activity.trade_date.isoformat(), activity.activity, activity.symbol,
        fmt(activity.quantity), fmt(activity.price), fmt(activity.price_currency),
        fmt(activity.total_amount), fmt(activity.total_currency),
        activity.instrument_name])


def entry_for(account_id: str, *, file: str, file_hash: str, activities) -> dict:
    rows = sorted(row_key(a) for a in activities)
    dates = sorted(a.trade_date.isoformat() for a in activities)
    return {"account_id": account_id, "file": file, "file_hash": file_hash,
            "window": [dates[0], dates[-1]] if dates else [None, None], "rows": rows}


def compare(previous: dict | None, current: dict) -> dict:
    """What changed since the last RECORDED entry for this account (RC-68)."""
    if previous is None:
        return {"status": "first", "removed": [], "added": [], "new_rows": len(current["rows"]),
                "window_starts_later": False}
    if previous["file_hash"] == current["file_hash"]:
        return {"status": "unchanged", "removed": [], "added": [], "new_rows": 0,
                "window_starts_later": False}

    first, last = previous["window"]
    inside = Counter(r for r in current["rows"] if first <= r[:10] <= last)
    before = Counter(previous["rows"])
    removed = sorted((before - inside).elements())
    added = sorted((inside - before).elements())
    new_rows = sum(1 for r in current["rows"] if r[:10] > last)
    starts_later = bool(current["window"][0] and first and current["window"][0] > first)
    status = ("restatement" if removed or added
              else "new_activity" if new_rows else "unchanged")
    return {"status": status, "removed": removed, "added": added,
            "new_rows": new_rows, "window_starts_later": starts_later}


class IngestLog:
    """`.state/broker/ingest_log.jsonl` — ★ append-only; an earlier line is never rewritten."""

    def __init__(self, path) -> None:
        self.path = Path(path)

    def entries(self) -> list[dict]:
        if not self.path.is_file():
            return []
        return [json.loads(line) for line in
                self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def last(self, account_id: str) -> dict | None:
        found = [e for e in self.entries() if e["account_id"] == account_id]
        return found[-1] if found else None

    def append(self, entry: dict, comparison: dict) -> dict:
        record = {**entry, "comparison": comparison,
                  "recorded_at": datetime.now(timezone.utc).isoformat()}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        return record
