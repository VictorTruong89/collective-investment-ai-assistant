#!/usr/bin/env python3
"""F4 `AC-4.2` / `AC-4.7` — the analyst firewall, at seat 6.

★★ **`INV-014` / `ST-9`: D-01 and D-03 must not see each other's in-progress
work.** The firewall's whole value is that when the fundamental and quant views
*agree*, the agreement is informative — two independent reads reaching the same
place. ⚠ If seat 6 reached into either domain's internals it would become a path
between them, and concurrence would quietly become an echo (`PG-7` says the same
thing about cross-configuration).

So `src/explain/**` may import **published contract types only** — a domain's
`contracts`/`models` surface — and never its analysis internals.

`AC-4.7`: it also may not contain gate-binding logic. `decision/attribute/binding.py`
already answers *"which gates bound, and why"*; a second implementation would be a
second answer (`P4`).

⚠ **AST, not grep** — a docstring naming a module is not an import.
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
EXPLAIN = "src/explain"

#: Domains whose INTERNALS seat 6 may not reach into (`INV-014`, `ST-9`).
WALLED_DOMAINS = ("src.fundamental", "src.quant")

#: The only sub-modules of a walled domain that are published surface.
PUBLISHED_SUFFIXES = (".contracts", ".models", ".contracts.", ".models.")

#: `AC-4.7` — gate binding is consumed, never re-implemented here.
GATE_BINDING_MARKERS = ("def bind_gates", "def gate_binding", "def which_gates_bound",
                        "def _bind(", "def compute_binding")


def _imports(source: str, filename: str) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(ast.parse(source, filename=filename)):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.add(node.module)
    return out


def _py(root: pathlib.Path):
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" not in p.parts:
            yield p


def _is_published(mod: str) -> bool:
    return any(s in mod for s in PUBLISHED_SUFFIXES) or mod in WALLED_DOMAINS


def firewall_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-4.2` — seat 6 reaching into a walled domain's internals."""
    src_root = src_root or REPO / "src"
    explain_dir = src_root / "explain"
    if not explain_dir.is_dir():
        return []
    out = []
    for path in _py(explain_dir):
        rel = path.relative_to(src_root.parent).as_posix()
        for mod in _imports(path.read_text(encoding="utf-8"), rel):
            if mod.startswith(WALLED_DOMAINS) and not _is_published(mod):
                out.append(
                    f"{rel} imports {mod} — ⚠ INV-014/ST-9: seat 6 may read a "
                    "domain's PUBLISHED contracts, never its analysis internals. "
                    "Reaching inside makes D-13 a path between the two analysts, "
                    "and their agreement stops being independent.")
    return out


def gate_binding_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-4.7` — gate binding rebuilt here instead of consumed."""
    src_root = src_root or REPO / "src"
    explain_dir = src_root / "explain"
    if not explain_dir.is_dir():
        return []
    out = []
    for path in _py(explain_dir):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(src_root.parent).as_posix()
        for marker in GATE_BINDING_MARKERS:
            if marker in text:
                out.append(f"{rel} defines {marker!r} — read "
                           "decision/attribute/binding.py instead (AC-4.7, P4)")
    return out


def all_violations(src_root: pathlib.Path | None = None) -> list[str]:
    return firewall_violations(src_root) + gate_binding_violations(src_root)


def main() -> int:
    bad = all_violations()
    if bad:
        print("⛔ F4 firewall violations:", file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-4.2 / AC-4.7 — the analyst firewall holds at seat 6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
