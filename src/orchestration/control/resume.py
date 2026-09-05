"""F8 `CT-8.3` — suspend / resume. `MS-6.5`.

★ A run may pause for external work and resume later, **possibly after a process
restart** (`AC-8.7`). That is why `F2` `D1` made the `Registry` the run scope and
why the token lives on disk rather than in memory.

⚠ **`D4`: "materially stale" means the `data_as_of` CHANGED**, not that a clock
ran or a price moved. Time and price move continuously; `data_as_of` moves
exactly when the answer could have changed — and `RunManifest` already carries it,
so staleness is checkable from the recorded run rather than recomputed.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import asdict, dataclass


class ResumeExpired(Exception):
    """`AC-8.8` — ⚠ expiry reuses `RA-126`: *an overdue relay is not a backlog
    item, it is a thesis going stale.* No second staleness mechanism."""


class InputsMovedOn(Exception):
    """`AC-8.9` — ⚠ stale inputs are NAMED, never swallowed."""


@dataclass(frozen=True, slots=True)
class ResumeToken:
    token: str
    run_id: str
    step_id: str
    data_as_of: str
    issued_at: str
    expires_at: str


class SuspendStore:
    """On disk, because `AC-8.7` requires surviving a process restart."""

    def __init__(self, root: str | pathlib.Path) -> None:
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, token: str) -> pathlib.Path:
        return self.root / f"{token}.json"

    def suspend(self, t: ResumeToken) -> None:
        self._path(t.token).write_text(json.dumps(asdict(t)), encoding="utf-8")

    def resume(self, token: str, *, now: str, current_data_as_of: str) -> ResumeToken:
        """⚠ `AC-8.6` — **idempotent**: resuming twice with one token is not an error.

        ★ The token is not consumed on use. A resume that failed on a retry
        because the first attempt "used it up" would turn a transient network
        blip into a lost run.
        """
        p = self._path(token)
        if not p.exists():
            raise ResumeExpired(f"no suspended work for token {token!r}")
        t = ResumeToken(**json.loads(p.read_text(encoding="utf-8")))
        if now > t.expires_at:
            raise ResumeExpired(
                f"token {token!r} expired at {t.expires_at} (RA-126 — an overdue "
                "request is not a backlog item, it is a thesis going stale)")
        if current_data_as_of != t.data_as_of:
            raise InputsMovedOn(
                f"suspended against data_as_of {t.data_as_of}, now "
                f"{current_data_as_of}. ⚠ D4 — new data landed, so the answer "
                "could have changed. Re-run rather than resuming onto inputs that "
                "no longer describe the same day.")
        return t
