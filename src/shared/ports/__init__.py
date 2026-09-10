"""★ The port declarations, and the SINGLE source of `required_ports` (F1 `D2`).

`__all__` IS the requirement list: declaring a port here is the same act as
requiring it, so the drift a hand-kept list permits — add a port, forget the
entry, coverage silently stops checking it — is impossible (`AC-F1.13`).

A port that is genuinely optional must SAY SO in `OPTIONAL_PORTS`; optionality
is never achieved by omission.

⚠ Empty on purpose. F1 §2 makes the semantics of any particular port a
NON-GOAL — `PricePort`, `ThesisSourcePort` (`F9`) and the rest each arrive with
their own spec. F1 owns the mechanism, not the ports.

⚠ `AC-F1.10`: declarations only. No I/O, no vendor import, no module-scope call.
"""

from __future__ import annotations

__all__: tuple[str, ...] = ()

OPTIONAL_PORTS: tuple[str, ...] = ()
