"""F2 `AC-2.9` / `AC-2.14` — secrets never written; positions filtered at EXPORT.

★★ **Two different rules, deliberately not merged.**

**Credentials are never written at all** (`AC-2.9`). An API key in a trace is a
leak the moment the file exists, and no downstream filter can undo it.

**Book positions and P&L ARE written, in full** (`AC-2.14`, `D4`). They are
*sensitive but not secret*, `.state/` is git-ignored, and ⚠ **redacting them at
write time would break replay — positions are INPUTS to the decisions being
replayed.** A trace redacted at the source is not evidence of the run that
happened.

★ Publication is a separate act: `QR-12`'s mirror exports through
`export_for_publication()`. Same shape as `DX-5`'s answer — keep the artifact
complete, control its **distribution**.
"""

from __future__ import annotations

import re
from typing import Any

REDACTED = "<redacted>"

#: `AC-2.9` — never written. Key names, matched case-insensitively.
SECRET_KEYS = ("api_key", "apikey", "token", "password", "secret", "authorization",
               "auth", "bearer", "credential", "private_key")

#: `AC-2.14` — written, then removed at export. NOT at write time.
SENSITIVE_KEYS = ("positions", "holdings", "pnl", "p_and_l", "book", "account_number",
                  "quantity_held", "market_value", "cash_balance")

_SECRET_VALUE = re.compile(r"\b(sk-[A-Za-z0-9_\-]{8,}|ghp_[A-Za-z0-9]{8,})\b")


def _walk(obj: Any, drop: tuple[str, ...], scrub_values: bool) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if any(s in str(k).lower() for s in drop):
                out[k] = REDACTED
            else:
                out[k] = _walk(v, drop, scrub_values)
        return out
    if isinstance(obj, (list, tuple)):
        return [_walk(v, drop, scrub_values) for v in obj]
    if scrub_values and isinstance(obj, str):
        return _SECRET_VALUE.sub(REDACTED, obj)
    return obj


def redact_secrets(obj: Any) -> Any:
    """`AC-2.9` — applied to EVERY record before it is written."""
    return _walk(obj, SECRET_KEYS, scrub_values=True)


def export_for_publication(obj: Any) -> Any:
    """`AC-2.14` / `D4` — applied only when leaving the machine.

    ⚠ Never called on the write path. The local trace stays complete so replay
    still works.
    """
    return _walk(redact_secrets(obj), SECRET_KEYS + SENSITIVE_KEYS, scrub_values=True)
