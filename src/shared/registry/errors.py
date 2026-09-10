"""F1 — registry failure modes. Every one is loud (`P5`)."""

from __future__ import annotations


class RegistryError(Exception):
    """Base for every registry failure."""


class InvalidKey(RegistryError):
    """CT-1.1 — port/variant must be non-empty and match [a-z0-9_.]+."""

    def __init__(self, field: str, value: str) -> None:
        self.field, self.value = field, value
        super().__init__(
            f"invalid {field} {value!r}: must be non-empty and match [a-z0-9_.]+ (CT-1.1)"
        )


class DuplicateRegistration(RegistryError):
    """AC-F1.1 — a second registration of one (port, variant).

    ⚠ Silent overwrite would make import order load-bearing.
    """

    def __init__(self, port: str, variant: str) -> None:
        self.port, self.variant = port, variant
        super().__init__(
            f"({port!r}, {variant!r}) is already registered; "
            "the first entry is unchanged (AC-F1.1)"
        )


class UnknownVariant(RegistryError):
    """AC-F1.2 — resolution of a name that was never registered.

    ★ `available` is REQUIRED, so a typo diagnoses itself.
    """

    def __init__(self, port: str, variant: str, available: tuple[str, ...]) -> None:
        self.port, self.variant, self.available = port, variant, available
        listed = ", ".join(repr(v) for v in available) if available else "(none registered)"
        super().__init__(
            f"no variant {variant!r} for port {port!r}; registered: {listed}"
        )


class IncompleteRegistry(RegistryError):
    """AC-F1.4 — a required port has no variant. Turns a 3 a.m. KeyError into a boot failure."""

    def __init__(self, missing: tuple[str, ...]) -> None:
        self.missing = missing
        super().__init__(
            "required ports with no registered variant: " + ", ".join(sorted(missing))
        )


class ConcurrentRegistryAccess(RegistryError):
    """AC-F1.14 / `D3` — the registry is single-threaded, and says so out loud.

    ⚠ `INV-2` (reproducibility) is a property of the whole invocation. A lock here
    would guard the cache dict while leaving the SHARED INSTANCE exactly as exposed
    — it would look like a fix and not be one.
    """

    def __init__(self, owner: str, caller: str) -> None:
        self.owner, self.caller = owner, caller
        super().__init__(
            f"registry was constructed on thread {owner!r} but accessed from {caller!r}. "
            "F1 D3: single-threaded by decision, not by accident. If F6b now needs "
            "parallel agent calls, reopen D3 deliberately."
        )
