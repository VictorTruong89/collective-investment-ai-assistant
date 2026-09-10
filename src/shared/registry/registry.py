"""F1 — the `(port, variant)` registry.

★ `D1`: **the `Registry` instance IS the run scope.** One registry is built per
run and passed down by constructor injection; there is deliberately no importable
singleton. That is what makes `AC-F1.6`'s cache boundary checkable rather than
interpretive, and what stops a long-lived `F8` process from serving day 2 out of
day 1's cache — a run is already not a process (`F8` `AC-8.7`).

⚠ This is a *service locator*: it trades a compile-time error for a runtime one.
`validate_coverage()` is the mitigation.
"""

from __future__ import annotations

import re
import threading
from collections.abc import Callable, Iterable

from src.shared import ports as _ports
from src.shared.registry.errors import (
    ConcurrentRegistryAccess,
    DuplicateRegistration,
    IncompleteRegistry,
    InvalidKey,
    UnknownVariant,
)
from src.shared.registry.provenance import CoverageReport, Provenance

_KEY = re.compile(r"^[a-z0-9_.]+$")

#: `AC-F1.12` — a port with fewer than this many variants is reported, never failed.
EARNED_ABSTRACTION_MIN = 2


class _Entry:
    """`CT-1.2` — what a registration stores. A FACTORY, never an instance."""

    __slots__ = ("factory", "version", "experimental", "fixture", "port_type")

    def __init__(
        self,
        factory: Callable[[], object],
        version: str,
        experimental: bool,
        fixture: bool,
        port_type: type | None,
    ) -> None:
        self.factory = factory
        self.version = version
        self.experimental = experimental
        self.fixture = fixture
        self.port_type = port_type


class Registry:
    """`CT-1.3` — registration, resolution, coverage. One instance per run (`D1`)."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], _Entry] = {}
        self._cache: dict[tuple[str, str], object] = {}
        self._owner = threading.current_thread().name

    # ── D3: single-threaded, asserted rather than assumed ────────────────────
    def _assert_owner_thread(self) -> None:
        caller = threading.current_thread().name
        if caller != self._owner:
            raise ConcurrentRegistryAccess(self._owner, caller)

    @staticmethod
    def _check_key(field: str, value: str) -> None:
        if not isinstance(value, str) or not value or not _KEY.match(value):
            raise InvalidKey(field, value)

    # ── registration ─────────────────────────────────────────────────────────
    def register(
        self,
        port: str,
        variant: str,
        factory: Callable[[], object],
        version: str,
        experimental: bool = False,
        fixture: bool = False,
        port_type: type | None = None,
    ) -> None:
        """`AC-F1.1`, `AC-F1.3` — store the factory; never invoke it here.

        Invoking at registration would force construction at import time and make
        registration order load-bearing on configuration.
        """
        self._assert_owner_thread()
        self._check_key("port", port)
        self._check_key("variant", variant)
        key = (port, variant)
        if key in self._entries:
            raise DuplicateRegistration(port, variant)
        self._entries[key] = _Entry(factory, version, experimental, fixture, port_type)

    # ── resolution ───────────────────────────────────────────────────────────
    def _entry(self, port: str, variant: str) -> _Entry:
        """`AC-F1.5` — a pure dict lookup. No import, no module load, no filesystem."""
        try:
            return self._entries[(port, variant)]
        except KeyError:
            raise UnknownVariant(port, variant, self.variants(port)) from None

    def resolve(self, port: str, variant: str) -> object:
        """`AC-F1.6` — build at most once per (port, variant) per Registry instance.

        ★ No runtime arguments (`S1-6`): configuration belongs at registration,
        or the cache key would silently return an instance built with a different
        call's arguments while reporting identical provenance.
        """
        self._assert_owner_thread()
        entry = self._entry(port, variant)
        key = (port, variant)
        if key not in self._cache:
            self._cache[key] = entry.factory()
        return self._cache[key]

    def resolve_with_provenance(self, port: str, variant: str) -> tuple[object, Provenance]:
        """The instance and its `CT-1.4` record together.

        ★ `CT-1.3` (`A1`). `resolve` deliberately returns only the object — keeping its
        return type narrow is what lets `F6a` route and `F2` trace without either
        depending on the other's payload. A caller needing both asks for both.
        """
        return self.resolve(port, variant), self.provenance(port, variant)

    def provenance(self, port: str, variant: str) -> Provenance:
        """`AC-F1.8` — entry-derived, and available WITHOUT constructing anything."""
        entry = self._entry(port, variant)
        return Provenance(
            port=port, variant=variant, version=entry.version, experimental=entry.experimental
        )

    # ── enumeration ──────────────────────────────────────────────────────────
    def variants(self, port: str) -> tuple[str, ...]:
        """`T4` — the registered variant names for one port, sorted."""
        return tuple(sorted(v for (p, v) in self._entries if p == port))

    def real_variants(self, port: str) -> tuple[str, ...]:
        """`AC-F1.12` (`A1`) — variants that are implementations, not stand-ins.

        ⚠ `fixture` answers a DIFFERENT question from `experimental`: an experimental
        variant is real code on trial; a fixture is not an implementation at all.
        """
        return tuple(
            sorted(v for (p, v), e in self._entries.items() if p == port and not e.fixture)
        )

    def ports(self) -> tuple[str, ...]:
        """`CT-1.3` — every port with at least one registered variant, sorted.

        ★ Added to the contract by `A1`: `AC-F1.9`'s meta-test cannot check "a variant
        registered without being added to the suite causes a failure" without
        enumerating what is registered, so the AC was unimplementable without it.
        """
        return tuple(sorted({p for (p, _) in self._entries}))

    # ── coverage ─────────────────────────────────────────────────────────────
    def validate_coverage(self, required_ports: Iterable[str] | None = None) -> CoverageReport:
        """`AC-F1.4` (raise) + `AC-F1.12` (warn) + `AC-F1.13` (`D2` default).

        `required_ports` defaults to `src.shared.ports.__all__` minus
        `OPTIONAL_PORTS`. Passing a list explicitly is for TESTS — production never
        does, because the point of `D2` is that there is no second list to keep
        current.
        """
        if required_ports is None:
            required_ports = tuple(
                p for p in _ports.__all__ if p not in set(_ports.OPTIONAL_PORTS)
            )
        required = tuple(sorted(required_ports))

        missing = tuple(sorted(p for p in required if not self.variants(p)))
        if missing:
            raise IncompleteRegistry(missing)

        thin = tuple(
            sorted(p for p in required if len(self.real_variants(p)) < EARNED_ABSTRACTION_MIN)
        )
        return CoverageReport(required=required, missing=(), thin_ports=thin)

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"<Registry ports={len(self.ports())} entries={len(self._entries)} thread={self._owner!r}>"
