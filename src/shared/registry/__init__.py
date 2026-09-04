"""F1 — module protocol & registry (SPI). See `sdd/specs/F1_module_registry/spec.md`."""

from __future__ import annotations

from src.shared.registry.errors import (
    ConcurrentRegistryAccess,
    DuplicateRegistration,
    IncompleteRegistry,
    InvalidKey,
    RegistryError,
    UnknownVariant,
)
from src.shared.registry.provenance import CoverageReport, Provenance
from src.shared.registry.registry import EARNED_ABSTRACTION_MIN, Registry

__all__ = [
    "ConcurrentRegistryAccess",
    "CoverageReport",
    "DuplicateRegistration",
    "EARNED_ABSTRACTION_MIN",
    "IncompleteRegistry",
    "InvalidKey",
    "Provenance",
    "Registry",
    "RegistryError",
    "UnknownVariant",
]
