"""The counterfactual arm — vetoed candidates (CT-12.2, RC-31, DN-19/20/21).

```
╔══════════════════════════════════════════════════════════════════╗
║  ★ WHY THIS IS WRITE-ONCE AND WHY THAT IS HARDER THAN IT LOOKS   ║
║                                                                  ║
║  DN-21 / BS-7: "a rejected-name history that can be edited is    ║
║  the most tempting record in the system to edit."                ║
║                                                                  ║
║  It is tempting because NOTHING EXTERNAL RECONCILES IT. The book ║
║  is checked against the broker; a vetoed name was never bought,  ║
║  so the only account of what the gate rejected — and of how      ║
║  those names went on to do — is this file.                       ║
║                                                                  ║
║  D-12 §6.3: the gate is economically useful ~3.5–11x before it   ║
║  is statistically provable. This store is what eventually makes  ║
║  it provable, and every un-recorded veto is a lost observation.  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Append-only means append-only for the OUTCOME too.** A candidate is written
when it is vetoed and its realised return is known later — so marking appends a
second event rather than editing the first, and `read()` folds them. The file
keeps both; the caller sees the current view.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from src.recording.errors import AppendOnlyViolation


@dataclass(frozen=True, slots=True)
class VetoedCandidate:
    """CT-12.2 — the counterfactual arm.

    `outcome_h` is `None` while pending. ⚠ It is never `0.0` for "not yet
    known": zero is a realised return and pending is an absence, and collapsing
    them would put a fabricated flat outcome into the comparison (DE-35).
    """

    ticker: str
    as_of: date
    ranked_quantity: float
    horizon: str
    binding_gates: tuple[str, ...]
    reason: str
    decision_anchor: str
    outcome_h: float | None = None

    def __post_init__(self) -> None:
        if not self.binding_gates:
            raise ValueError(
                "a vetoed candidate must name at least one binding gate (DN-19) — "
                "a veto with no attributable gate is an exclusion nobody can explain, "
                "and D-12 §5.6 requires EVERY binding gate, not the first"
            )
        if not self.ticker or not self.reason:
            raise ValueError("ticker and reason are required")

    @property
    def key(self) -> tuple[str, str]:
        return (self.ticker, self.as_of.isoformat())

    def to_json_obj(self) -> dict:
        return {
            "event": "vetoed", "ticker": self.ticker, "as_of": self.as_of.isoformat(),
            "ranked_quantity": self.ranked_quantity, "horizon": self.horizon,
            "binding_gates": list(self.binding_gates), "reason": self.reason,
            "decision_anchor": self.decision_anchor,
        }

    @classmethod
    def from_json_obj(cls, obj: dict) -> "VetoedCandidate":
        return cls(
            ticker=obj["ticker"], as_of=date.fromisoformat(obj["as_of"]),
            ranked_quantity=obj["ranked_quantity"], horizon=obj["horizon"],
            binding_gates=tuple(obj["binding_gates"]), reason=obj["reason"],
            decision_anchor=obj["decision_anchor"],
        )


class CounterfactualStore:
    """Append-only JSONL of `vetoed` and `outcome` events."""

    __slots__ = ("_path",)

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _events(self) -> list[dict]:
        if not self._path.exists():
            return []
        out = []
        for n, line in enumerate(self._path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except Exception as exc:
                raise ValueError(f"{self._path}:{n} is not readable ({exc})") from exc
        return out

    def _write(self, obj: dict) -> None:
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, sort_keys=True) + "\n")

    def append(self, candidate: VetoedCandidate) -> None:
        """Record a veto. A second write for the same key is a revision (DN-21)."""
        if any(
            e["event"] == "vetoed" and (e["ticker"], e["as_of"]) == candidate.key
            for e in self._events()
        ):
            raise AppendOnlyViolation("vetoed candidate", candidate.key)
        self._write(candidate.to_json_obj())

    def record_outcome(self, ticker: str, as_of: date, *, realised_return: float) -> None:
        """Append the realised return as a SEPARATE event (DN-21).

        ★ It does not edit the veto row. The original record and the outcome are
        two facts learned at two times, and a store that merged them in place
        would make the second indistinguishable from the first.
        """
        key = (ticker, as_of.isoformat())
        events = self._events()
        if not any(e["event"] == "vetoed" and (e["ticker"], e["as_of"]) == key for e in events):
            raise ValueError(f"no vetoed candidate {key} to mark")
        if any(e["event"] == "outcome" and (e["ticker"], e["as_of"]) == key for e in events):
            raise AppendOnlyViolation("outcome for vetoed candidate", key)
        self._write({"event": "outcome", "ticker": ticker, "as_of": key[1],
                     "realised_return": realised_return})

    def read(self) -> list[VetoedCandidate]:
        """The folded view: each candidate with its outcome if one has arrived."""
        candidates: dict[tuple, VetoedCandidate] = {}
        outcomes: dict[tuple, float] = {}
        for e in self._events():
            key = (e["ticker"], e["as_of"])
            if e["event"] == "vetoed":
                candidates[key] = VetoedCandidate.from_json_obj(e)
            else:
                outcomes[key] = e["realised_return"]
        return [
            replace(c, outcome_h=outcomes[k]) if k in outcomes else c
            for k, c in candidates.items()
        ]

    def raw_line_count(self) -> int:
        """Events on disk, not folded rows — the append-only evidence."""
        return len(self._events())

    def revise(self, ticker: str, as_of: date, **_changes) -> None:
        """★ Exists only to raise — see JournalStore.revise for why."""
        raise AppendOnlyViolation("vetoed candidate", (ticker, as_of.isoformat()))
