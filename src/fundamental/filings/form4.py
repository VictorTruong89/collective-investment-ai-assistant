"""`DX-148` ⓑ (Victor, 2026-10-04) — a Form 4 transaction CODE → `E-08`'s `in.type` label.

★ `AP-5`: the codes are SEC-defined (Form 4 General Instructions, Item 8), so the label is a
lookup, not a reading. `E-08 v2` asks the model for the code verbatim — which `X-01` ② can check
in its quote — and the label is derived here. ⚠ The mapping is the one Victor approved: the five
named codes, and every other code → `other` (e.g. `F` tax withholding, `X` in-the-money exercise).
"""

from __future__ import annotations

import re

TRANSACTION_LABELS = {"S": "sale", "P": "purchase", "M": "option exercise",
                      "G": "gift", "A": "award"}

#: A code as a Form 4 prints it: one letter, optionally followed by footnote markers `(1)(2)`.
_CODE = re.compile(r"^([A-Z])(?:\(\d+\))*$")


def transaction_label(code: str) -> str:
    """The label for a code. ⚠ Raises on anything that is not a code (P5) — a label or a
    blank passed here would otherwise come back as a confident `other`."""
    match = _CODE.match(str(code).strip())
    if not match:
        raise ValueError(f"{code!r} is not a Form 4 transaction code (one letter, optional "
                         f"footnote markers) — DX-148")
    return TRANSACTION_LABELS.get(match.group(1), "other")
