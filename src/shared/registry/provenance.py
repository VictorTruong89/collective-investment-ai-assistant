"""F1 `CT-1.4` — the provenance record. Consumed by `F2`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Provenance:
    """Which implementation produced this? (`AP-6`, `C8`)

    ★ `AC-1.8`: fully determined by the registry ENTRY, never by anything the
    resolved object reports about itself. An adapter that lies about its own
    version cannot corrupt the record.
    """

    port: str
    variant: str
    version: str
    experimental: bool


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """`AC-1.4` + `AC-1.12` — what `validate_coverage` observed.

    ⚠ A *raise* wins over a *report*: if anything is missing, `IncompleteRegistry`
    is raised and this is never returned.
    """

    required: tuple[str, ...]
    missing: tuple[str, ...]
    thin_ports: tuple[str, ...]
