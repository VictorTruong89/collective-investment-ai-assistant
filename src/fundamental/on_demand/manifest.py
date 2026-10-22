"""CT-F13.1 — the chain manifest, `.state/thesis_for/<TICKER>_<as_of>/chain.json`.

★ Rewritten ATOMICALLY after every step (a temp file, then `os.replace`), so a chain killed
mid-step leaves the last complete record, never half of one (`RA-108`'s shape: on disk
BEFORE the next step is issued).
"""

from __future__ import annotations

import json
import os
import pathlib
from datetime import date, datetime, timezone

STATUSES = ("pending", "done", "failed")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChainManifest:
    def __init__(self, path: pathlib.Path, data: dict) -> None:
        self.path = path
        self.data = data

    @classmethod
    def open(cls, root, ticker: str, as_of: date, *, transport: str) -> "ChainManifest":
        """The chain for `ticker` at `as_of` — resumed if one exists (AC-F13.7)."""
        path = pathlib.Path(root) / f"{ticker.upper()}_{as_of.isoformat()}" / "chain.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if (data["ticker"], data["as_of"]) != (ticker.upper(), as_of.isoformat()):
                raise ValueError(f"{path} records {data['ticker']} {data['as_of']}, "
                                 f"not {ticker.upper()} {as_of}")
            data["transport"] = transport
        else:
            data = {"ticker": ticker.upper(), "as_of": as_of.isoformat(), "transport": transport,
                    "created_at": _now(), "inputs": [], "steps": [], "thesis_run_id": None}
        return cls(path, data)

    def find(self, step: str, block: str | None = None) -> dict | None:
        return next((s for s in self.data["steps"]
                     if s["step"] == step and s.get("block") == block), None)

    def done(self, step: str, block: str | None = None) -> dict | None:
        found = self.find(step, block)
        return found if found and found["status"] == "done" else None

    def record(self, step: str, block: str | None = None, **fields) -> dict:
        """Upsert one step and SAVE. `status` must be one of `STATUSES`."""
        if fields.get("status") not in STATUSES:
            raise ValueError(f"status {fields.get('status')!r} is not one of {STATUSES}")
        entry = self.find(step, block)
        if entry is None:
            entry = {"step": step, **({"block": block} if block else {}), "run_id": None,
                     "started_at": _now(), "ended_at": None}
            self.data["steps"].append(entry)
        entry.update(fields)
        if fields["status"] != "pending":
            entry["ended_at"] = _now()
        if fields["status"] == "done":
            entry.pop("error", None)
        self.save()
        return entry

    def set(self, **fields) -> None:
        self.data.update(fields)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.data, indent=1, default=str), encoding="utf-8")
        os.replace(tmp, self.path)
