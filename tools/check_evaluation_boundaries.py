#!/usr/bin/env python3
"""F5 `AC-5.11`, `AC-5.12`, `AC-5.15` — the three import rules D-14 lives under.

`AC-5.12` **`ST-2`, one-way**: the harness imports anything; nothing imports the
harness. ⚠ D-14 inherits D-10's shape — an instrument that something depends on
would have to be promoted before it could be used, which is the point of the rule.

`AC-5.11` **no re-derivation**: `src/evaluation/**` must not compute IC, breadth
or the IC standard error itself. ★ *A second IC implementation that disagrees with
the first is precisely the failure F5 exists to prevent* — it imports them from
`src/quant/metrics/`.

`AC-5.15` **`D1`, studies are not consumed**: `src/evaluation/studies/**` is
`P7`-exempt *because nothing reads it*. ⚠ The silent direction is a study
acquiring a consumer and becoming load-bearing while still unspecified — this is
what catches it.
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
EVAL = "src/evaluation"
STUDIES = "src/evaluation/studies"

#: `AC-5.11` — names that would mean a local re-derivation.
RE_DERIVED = ("def information_coefficient", "def compute_ic", "def _ic(",
              "def breadth(", "def effective_breadth", "def ic_standard_error",
              "def ic_se(")


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


def one_way_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-5.12` — anything outside the harness importing it."""
    src_root = src_root or REPO / "src"
    out = []
    for path in _py(src_root):
        rel = path.relative_to(src_root.parent).as_posix()
        if rel.startswith(EVAL):
            continue
        for mod in _imports(path.read_text(encoding="utf-8"), rel):
            if mod.startswith("src.evaluation"):
                out.append(f"{rel} imports {mod} — ST-2 is one-way (AC-5.12)")
    return out


def study_consumer_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-5.15` / `D1` — a study that something reads has become a metric."""
    src_root = src_root or REPO / "src"
    out = []
    for path in _py(src_root):
        rel = path.relative_to(src_root.parent).as_posix()
        if rel.startswith(STUDIES):
            continue
        for mod in _imports(path.read_text(encoding="utf-8"), rel):
            if mod.startswith("src.evaluation.studies"):
                out.append(
                    f"{rel} imports {mod} — D1: a study that is CONSUMED is a "
                    "metric. Move it to src/evaluation/metrics/ and give it a "
                    "known-answer fixture (AC-5.1)")
    return out


def re_derivation_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """`AC-5.11` — IC/breadth computed here instead of imported."""
    src_root = src_root or REPO / "src"
    out = []
    for path in _py(src_root / "evaluation") if (src_root / "evaluation").is_dir() else []:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(src_root.parent).as_posix()
        for marker in RE_DERIVED:
            if marker in text:
                out.append(f"{rel} defines {marker!r} — import it from "
                           "src/quant/metrics/ instead (AC-5.11, P4)")
    return out


def all_violations(src_root: pathlib.Path | None = None) -> list[str]:
    return (one_way_violations(src_root) + study_consumer_violations(src_root)
            + re_derivation_violations(src_root))


def main() -> int:
    bad = all_violations()
    if bad:
        print("⛔ F5 boundary violations:", file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-5.11 / AC-5.12 / AC-5.15 — evaluation boundaries hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
