"""The decision journal — CT-11.6, append-only (RC-24, INV-006, AC-11.15).

```
╔══════════════════════════════════════════════════════════════════╗
║  ★ THIS IS THE CLOCK THAT CAN START TODAY.  (L3 BS-3b)           ║
║                                                                  ║
║  `thesis_version` is nullable BY DESIGN, so a decision is        ║
║  recordable before D-01 exists — and these entries become        ║
║  RA-59's calibration sample later.                               ║
║                                                                  ║
║  Of B1's obligations this is the only one whose input exists     ║
║  now: Victor is already making decisions. Every one not written  ║
║  down is a row deleted from the sample that will eventually      ║
║  decide whether conviction carries information.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

Storage is **JSONL**, not parquet: the journal is small, is read by a human as
often as by code, and a record that needs this codebase to be readable is a
record that dies with it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date
from pathlib import Path

from src.recording.errors import AppendOnlyViolation


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """CT-11.6 — `(date, ordinal, ticker, action, rationale, thesis_version,
    overridden_flags[], author)`.

    Frozen: an entry that can be mutated in place is an entry whose rationale
    can be improved once the outcome is known, which is the one thing the
    journal must make impossible (RC-24).
    """

    date: date
    ticker: str
    action: str
    rationale: str
    author: str
    thesis_version: int | None = None
    overridden_flags: tuple[str, ...] = ()
    ordinal: int = field(default=-1)      # assigned by the store, not the caller

    def __post_init__(self) -> None:
        if not self.rationale or not self.rationale.strip():
            raise ValueError(
                "a journal entry needs a rationale — an entry with no reason is a "
                "timestamp pretending to be evidence, and RA-59 can never learn "
                "anything from it"
            )
        if not self.ticker or not self.action:
            raise ValueError("ticker and action are required")

    def to_json_obj(self) -> dict:
        obj = asdict(self)
        obj["date"] = self.date.isoformat()
        obj["overridden_flags"] = list(self.overridden_flags)
        return obj

    @classmethod
    def from_json_obj(cls, obj: dict) -> JournalEntry:
        return cls(
            date=date.fromisoformat(obj["date"]), ticker=obj["ticker"],
            action=obj["action"], rationale=obj["rationale"], author=obj["author"],
            thesis_version=obj["thesis_version"],
            overridden_flags=tuple(obj["overridden_flags"]), ordinal=obj["ordinal"],
        )


class JournalStore:
    """Append-only JSONL. There is no update path, by construction."""

    __slots__ = ("_path",)

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: JournalEntry) -> JournalEntry:
        """Assign the next ordinal and write one line."""
        stored = replace(entry, ordinal=len(self.read()))
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(stored.to_json_obj(), sort_keys=True) + "\n")
        return stored

    def read(self) -> list[JournalEntry]:
        """Every entry, in write order.

        ⚠ A malformed line RAISES rather than being skipped (P5): a silently
        dropped row makes the calibration sample quietly incomplete, and nothing
        downstream could tell.
        """
        if not self._path.exists():
            return []
        out = []
        for n, line in enumerate(self._path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                out.append(JournalEntry.from_json_obj(json.loads(line)))
            except Exception as exc:
                raise ValueError(
                    f"{self._path}:{n} is not a readable journal entry ({exc}) — "
                    f"a skipped row is a hole in the calibration sample that nothing "
                    f"downstream can see"
                ) from exc
        return out

    def revise(self, ordinal: int, **_changes) -> None:
        """★ Exists only to raise.

        A store with no `revise` at all would be silently satisfied by a caller
        rewriting the file; a `revise` that raises names the rule and the reason
        at the moment someone reaches for it (INV-006, RC-24).
        """
        raise AppendOnlyViolation("journal entry", ordinal)
