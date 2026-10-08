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


# ── AC-F12.19 (≡ AC-3.16) — every entry's known-answer test is a real test ──────
_REPO = _SRC.parent
_KAT_LINK = re.compile(r"`?((?:tests|tests_src)/[\w/]+\.py)?::(test_\w+)`?")


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text,
                      re.M | re.S | re.I)
    return match.group(1) if match else ""


def unresolved_known_answer_tests(entry_dirs=None, repo: Path | None = None
                                  ) -> dict[str, str]:
    """`{formula_id: why}` for every entry whose known-answer test cannot be found.

    ★ The section must name at least one `path.py::test_name` (a bare
    `::test_name` inherits the last path named before it). A named test RUNS
    with the suite, so a link that resolves is a test that executes; ⚠ the link
    is what rots — a renamed function or a moved file leaves prose behind that
    still reads like coverage.
    """
    repo = repo or _REPO
    problems: dict[str, str] = {}
    for directory in entry_dirs or ENTRY_DIRS:
        for path in sorted(Path(directory).glob("*.md")):
            section = _section(path.read_text(encoding="utf-8"), "Known-answer test")
            last, links, bad = None, [], []
            for file_part, name in _KAT_LINK.findall(section):
                last = file_part or last
                links.append((last, name))
            for file_part, name in links:
                target = repo / file_part if file_part else None
                if target is None or not target.is_file():
                    bad.append(f"{file_part or '?'}::{name} (no such file)")
                elif not re.search(rf"^def {name}\(", target.read_text(
                        encoding="utf-8"), re.M):
                    bad.append(f"{file_part}::{name} (no such test)")
            if not links:
                problems[path.stem] = "names no `path.py::test_name` known-answer test"
            elif bad:
                problems[path.stem] = "; ".join(bad)
    return problems


# ── AC-F12.22 (≡ AC-3.19, QA-25) — an entry is amended with its code ───────────
#: ★ Entries whose formula has no `FORMULA_ID = "..."` assignment anywhere in
#: `src/`, so there is no file to pin. ⚠ A FIXED list: a new entry without an
#: assignment must be added here by hand, which is the moment to ask why.
UNLOCATED_FORMULAS = frozenset({
    "cv.purge_embargo.derived.v1", "effective_n.overlap_corrected.v1",
    "mde.rank_ic.v1", "rank_ic.spearman.v1",
    "volatility.realised_open_to_open_std.v1",
    # ✏ 2026-10-06 — F12 D9: declared as `FORMULA_REALISED_SE` in metrics/ic.py
    #   (not a `FORMULA_ID =` assignment), the same shape as its neighbours above.
    "se.newey_west_bartlett.v1",
    # ✏ 2026-10-08 — F12 D11: `FORMULA_WALK_FORWARD` in backtest/protocol.py.
    "cv.walk_forward.expanding.v1",
})
_CODE_PIN = re.compile(r"^Code:\s*(\S+)\s*@\s*sha256:([0-9a-f]{16})\s*$", re.M)


def code_digest(path: Path) -> str:
    """The first 16 hex of the file's sha256 — what an entry pins."""
    import hashlib

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def stale_entries(repo: Path | None = None) -> dict[str, str]:
    """`{formula_id: why}` for every located formula whose entry does not pin
    the CURRENT code. ★ QA-25: *the MethodEntry and the code are amended in the
    same commit* — so a code change alone turns this red, and the fix is to
    re-read the entry, amend it, and re-pin."""
    repo = repo or _REPO
    src = repo / "src"
    declared: dict[str, Path] = {}
    for path in sorted(src.rglob("*.py")):
        for match in re.finditer(r'^FORMULA_ID\s*=\s*"([^"]+)"',
                                 path.read_text(encoding="utf-8"), re.M):
            declared[match.group(1)] = path
    entries = {p.stem: p for d in src.glob("*/methods/entries") for p in d.glob("*.md")}
    problems: dict[str, str] = {}
    for formula_id, code in sorted(declared.items()):
        entry = entries.get(formula_id)
        if entry is None:
            continue                                  # AC-F12.17's failure, not this one
        pin = _CODE_PIN.search(entry.read_text(encoding="utf-8"))
        rel = code.relative_to(repo).as_posix()
        if pin is None:
            problems[formula_id] = f"entry pins no code (want `Code: {rel} @ sha256:…`)"
        elif pin.group(1) != rel:
            problems[formula_id] = f"entry pins {pin.group(1)}, formula is in {rel}"
        elif pin.group(2) != code_digest(code):
            problems[formula_id] = (f"{rel} changed since its entry was amended "
                                    f"(pinned {pin.group(2)}, now {code_digest(code)})")
    return problems
