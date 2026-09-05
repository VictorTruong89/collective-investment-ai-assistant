"""F2 `CT-2.8` — the on-disk trace, beside the existing run record (`D1`).

```text
.state/runs/<run_id>/
    manifest.json  outcome.json     ← EXISTS (OR-13). F2 NEVER writes here.
    trace.jsonl                     ← append-only, one JSON object per line
    trace/payloads/<call_id>.json   ← CT-2.2 bodies, by reference
    trace/EXPIRED                   ← ⚠ written when D2 retention removes them
```

★★ **Why payloads sit beside the log rather than inside it.** `D2` expires raw
payloads while keeping decisions forever. If the bodies were inline, expiring
them would mean **rewriting the log** — which `AC-2.8` forbids. Separated, expiry
is deleting a directory, which append-only permits without qualification. ⚠ The
layout choice is what makes the retention policy implementable at all.

★ **Why JSONL and not a JSON array.** A crashed run leaves a half-written array
that does not parse at all; JSONL's last line is either whole or visibly
truncated, which is exactly what `AC-2.12`'s `INCOMPLETE` needs to detect.
"""

from __future__ import annotations

import json
import pathlib
from collections.abc import Iterator

from src.orchestration.trace.errors import (
    IncompleteTrace,
    PayloadsExpired,
    TraceImmutableError,
)
from src.orchestration.trace.models import ExternalCall, TraceRecord
from src.orchestration.trace.redact import redact_secrets

#: Written by `close()`. Its absence is what makes a crashed run INCOMPLETE.
_SENTINEL = "__run_closed__"


class TraceStore:
    """Append-only trace for one run. ⚠ Never writes a run-level record."""

    def __init__(self, root: str | pathlib.Path, run_id: str) -> None:
        self.run_id = run_id
        self.run_dir = pathlib.Path(root) / run_id
        self.trace_dir = self.run_dir / "trace"
        self.payload_dir = self.trace_dir / "payloads"
        self.log_path = self.run_dir / "trace.jsonl"
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        self._keys: set[str] = {r.get("_key") for r in self._raw()} - {None}

    # ── writing ──────────────────────────────────────────────────────────────
    def append(self, record: TraceRecord) -> None:
        """`AC-2.8` — append-only; a repeated record key raises."""
        if record.run_id != self.run_id:
            raise ValueError(
                f"record carries run_id {record.run_id!r} but this store is "
                f"{self.run_id!r} — F2 joins to ONE existing run (AC-2.1)"
            )
        record.validate()
        key = record.record_key
        if key in self._keys:
            raise TraceImmutableError(key)

        # AC-2.9 — secrets are removed BEFORE anything touches the disk.
        obj = redact_secrets(record.to_json_obj())
        if isinstance(record, ExternalCall):
            # D1 — the bulky halves live beside the log, referenced by call_id.
            (self.payload_dir / f"{record.call_id}.json").write_text(
                json.dumps(redact_secrets({"request": record.request,
                                           "response": record.response}),
                           indent=2, default=str), encoding="utf-8")
            obj.pop("request", None)
            obj.pop("response", None)
            obj["payload_ref"] = record.call_id

        obj["_key"] = key
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, default=str) + "\n")
        self._keys.add(key)

    def close(self, status: str = "SUCCESS") -> None:
        """Mark the run complete. ⚠ Its absence is `AC-2.12`'s INCOMPLETE."""
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": _SENTINEL, "status": status}) + "\n")

    # ── reading ──────────────────────────────────────────────────────────────
    def _raw(self) -> Iterator[dict]:
        if not self.log_path.exists():
            return iter(())
        out = []
        for n, line in enumerate(self.log_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise IncompleteTrace(
                    f"{self.log_path}:{n} is truncated — the run did not finish "
                    f"writing it (AC-2.12). A partial trace must never read as whole. ({exc})"
                ) from None
        return iter(out)

    def read_all(self) -> Iterator[dict]:
        """Every record, sentinel excluded."""
        return (r for r in self._raw() if r.get("type") != _SENTINEL)

    def status(self) -> str:
        """`AC-2.12` — SUCCESS/FAILED once closed, otherwise INCOMPLETE."""
        closing = [r for r in self._raw() if r.get("type") == _SENTINEL]
        return closing[-1]["status"] if closing else "INCOMPLETE"

    # ── payloads · D2 retention ──────────────────────────────────────────────
    @property
    def expired_marker(self) -> pathlib.Path:
        return self.trace_dir / "EXPIRED"

    def payload(self, call_id: str) -> dict:
        if self.expired_marker.exists():
            raise PayloadsExpired(self.run_id, self.expired_marker.read_text().strip())
        path = self.payload_dir / f"{call_id}.json"
        if not path.exists():
            raise IncompleteTrace(f"no recorded payload for call {call_id!r} (AC-2.2)")
        return json.loads(path.read_text(encoding="utf-8"))

    def expire_payloads(self, at: str) -> None:
        """`D2` — remove raw bodies, keep every record, and SAY SO (`AC-2.15`)."""
        for p in self.payload_dir.glob("*.json"):
            p.unlink()
        self.expired_marker.write_text(at, encoding="utf-8")
