"""CT-3.3 — the MethodEntry register (QA-20, QA-25, AC-3.14…AC-3.19).

```
A formula_id referenced anywhere in src/ with no MethodEntry FAILS THE BUILD.
```

★ **Why a build-time check and not a docstring convention.** §8's six required
fields — statement, symbols, reference, assumptions, alternatives-rejected, and
a known-answer test — are precisely the things a reader needs to tell a standard
estimator from a house variant. `rsi_14` is the live proof: ours is a simple
rolling mean where every charting package uses Wilder smoothing, the two diverge
materially after warm-up, and **nothing anywhere recorded the choice**.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.quant.errors import MethodMissingError

ENTRIES_DIR = Path(__file__).resolve().parent / "entries"

#: ★★ **PS-44 — QA-20 owns the STANDARD, not the storage.** D-06's risk-budget
#: factors each need a MethodEntry (**AC-6.9k**), and putting them here would
#: either file SEAT-4's work in SEAT-3's tree or create a `src/portfolio` →
#: `src/quant` import edge **the graph cannot distinguish from consuming a
#: nomination** (FE-21's shape, one seat over). ★ This check is a **filesystem
#: scan, not an import**, so searching each domain's own `methods/entries/`
#: satisfies QA-20 verbatim and creates no dependency in either direction.
_SRC = Path(__file__).resolve().parents[2]

#: ⚠ Generalised 2026-08-26, after adding a second and then a third domain one
#: path at a time. **Every domain's own `methods/entries/` is searched**, so a
#: new domain needs no edit here — and forgetting this edit was the only way
#: PS-44's rule could have silently stopped applying.
ENTRY_DIRS = tuple(
    [ENTRIES_DIR]
    + sorted(d for d in _SRC.glob("*/methods/entries") if d != ENTRIES_DIR))

#: The six §8.2 fields, as the headings a MethodEntry must carry. Matched on the
#: heading rather than on prose so the check is mechanical (AC-3.15).
REQUIRED_SECTIONS = (
    "Statement", "Symbols", "Reference", "Assumptions",
    "Alternatives rejected", "Known-answer test",
)


def entry_path(formula_id: str) -> Path:
    """The entry for `formula_id`, wherever its own domain files it (PS-44)."""
    for directory in ENTRY_DIRS:
        candidate = directory / f"{formula_id}.md"
        if candidate.exists():
            return candidate
    return ENTRIES_DIR / f"{formula_id}.md"          # the reported miss


def method(formula_id: str) -> str:
    """The provenance record for `formula_id`, or raise (§11's API surface)."""
    path = entry_path(formula_id)
    if not path.is_file():
        raise MethodMissingError(formula_id, str(ENTRIES_DIR))
    return path.read_text(encoding="utf-8")


def missing_sections(formula_id: str) -> list[str]:
    """Which of the six required fields a MethodEntry omits (AC-3.15)."""
    text = method(formula_id)
    headings = {h.strip().lower() for h in re.findall(r"^##\s+(.+)$", text, re.M)}
    return [s for s in REQUIRED_SECTIONS if s.lower() not in headings]


def declared_formula_ids() -> set[str]:
    """Every declared entry, across every domain's own directory (PS-44)."""
    return {p.stem for d in ENTRY_DIRS for p in d.glob("*.md")}


def formula_ids_referenced_in_src(root: Path | None = None) -> set[str]:
    """Every `FORMULA_ID = "..."` declared under `src/`.

    ⚠ Deliberately keyed on the ASSIGNMENT, not on any string that looks like an
    id. A grep for dotted lowercase would match half the codebase and the check
    would be disabled within a week (IM-2's argument: a check that fires on
    noise is a check that gets turned off).
    """
    root = root or Path(__file__).resolve().parents[2]
    found: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        for match in re.finditer(r'^FORMULA_ID\s*=\s*"([^"]+)"', path.read_text(
                encoding="utf-8"), re.M):
            found.add(match.group(1))
    return found
