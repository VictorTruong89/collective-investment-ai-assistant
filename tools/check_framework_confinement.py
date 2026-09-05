#!/usr/bin/env python3
"""F2 `AC-2.10` / `QR-14` — an orchestration framework lives ONLY in `src/orchestration/graph/`.

★ **Why confinement rather than prohibition.** `A8`: a framework earns its place
in the one module whose job is graph execution. Everywhere else it is a
dependency that spreads, and `PG-9` requires the control plane stay deterministic
and replayable — a framework's own scheduler is exactly what would erode that.

⚠ **AST, not grep.** `L4` §10.1 writes these rules as greps, but a grep matches
the *string* anywhere — a docstring in `src/reporting/` mentioning LangGraph
would fail the build. The rule is about **imports**, so imports are what is
parsed. (Same reasoning as upstream `tests_src/architecture.py`.)
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The frameworks QR-14 confines. Top-level module names.
FRAMEWORKS = ("langgraph", "langchain", "llama_index", "haystack",
              "autogen", "crewai", "semantic_kernel", "dspy")

#: The ONE place they may be imported.
PERMITTED_PREFIX = "src/orchestration/graph/"


def imports_of(source: str, filename: str) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(source, filename=filename)):
        if isinstance(node, ast.Import):
            found |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module)
    return found


def violations(root: pathlib.Path | None = None) -> list[str]:
    root = root or REPO / "src"
    out: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root.parent).as_posix()
        if rel.startswith(PERMITTED_PREFIX):
            continue
        for mod in imports_of(path.read_text(encoding="utf-8"), rel):
            if mod.split(".")[0] in FRAMEWORKS:
                out.append(f"{rel} imports {mod}")
    return out


def main() -> int:
    bad = violations()
    if bad:
        print("⛔ QR-14 / AC-2.10 — orchestration framework outside "
              f"{PERMITTED_PREFIX}:", file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        print("\n★ A framework belongs in the one module whose job is graph "
              "execution (A8). Elsewhere it erodes PG-9's deterministic, "
              "replayable control plane.", file=sys.stderr)
        return 1
    print(f"✅ AC-2.10 — no framework imported outside {PERMITTED_PREFIX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
