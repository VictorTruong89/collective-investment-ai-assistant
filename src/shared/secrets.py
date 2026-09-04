"""Secret handling — environment only, redacting by type (L2-shared-infrastructure §8).

★ SC-3 is a property of the TYPE, not a rule anyone has to remember at each call
site. `Secret.__repr__` and `Secret.__str__` return a redaction, so a secret
cannot reach a log, an exception message, a manifest or an artifact through the
ordinary paths that format objects — f-strings, `%s`, `json.dumps(default=str)`,
`logging`'s own lazy formatting, and traceback rendering all go through one of
those two methods.

Getting the value out requires calling `.reveal()`, which is deliberately named
so that every place a secret is genuinely used is greppable in one command.

⚠ SC-4: a leaked key is ROTATED, not merely purged. Repo history has been
rewritten once for this. Purging removes the copy; rotation removes the risk.
"""

from __future__ import annotations

import os
from typing import Iterable

from src.shared.errors import SecretAbsentError

#: The four secrets this system uses (SC-1). Listed so `require()` can check
#: them all at startup rather than discovering each one at its first use.
KNOWN_SECRETS = (
    "ANTHROPIC_API_KEY",
    "FMP_API_KEY",
    "GMAIL_SMTP_USER",
    "GMAIL_APP_PASSWORD",
)

REDACTION = "<redacted>"


class Secret:
    """A string that refuses to render itself (SC-3).

    Not a dataclass and not frozen-by-convention: `__slots__` plus no setters
    means the value cannot be rebound, and the absence of `__eq__` means two
    secrets do not compare (which would leak by timing and by accident).
    """

    __slots__ = ("_name", "_value")

    def __init__(self, name: str, value: str) -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_value", value)

    # The two methods that make SC-3 structural.
    def __repr__(self) -> str:
        return f"Secret({self._name}={REDACTION})"

    def __str__(self) -> str:
        return REDACTION

    def __format__(self, spec: str) -> str:
        # Without this, f"{secret:>10}" would bypass __str__ on some paths.
        return REDACTION

    def __setattr__(self, *_args) -> None:
        raise AttributeError("Secret is immutable")

    @property
    def name(self) -> str:
        """The NAME is not secret — only the value is. Safe to log."""
        return self._name

    def reveal(self) -> str:
        """Return the raw value.

        ★ Deliberately named so every genuine use is greppable:
        `grep -rn '\\.reveal()' src/`. If that command returns somewhere
        surprising, that is the review this method exists to enable.
        """
        return self._value


def secret(name: str) -> Secret:
    """Fetch one secret from the environment (SC-1).

    Raises immediately if absent — but prefer `require()` at startup so a run
    does not die forty minutes in (SC-2).
    """
    value = os.environ.get(name)
    if not value:
        raise SecretAbsentError([name])
    return Secret(name, value)


def require(names: Iterable[str] = KNOWN_SECRETS) -> dict[str, Secret]:
    """Check every needed secret AT STARTUP and return them together (SC-2).

    ★ All missing names are reported in one error rather than one per run.
    Discovering four missing keys across four failed runs is the avoidable
    version of this problem.
    """
    names = tuple(names)
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise SecretAbsentError(missing)
    return {n: Secret(n, os.environ[n]) for n in names}
