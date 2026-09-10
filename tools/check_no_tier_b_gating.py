#!/usr/bin/env python3
"""`F7b` `AC-7b.5` — ⛔⛔ **nothing gates on a Tier-B result.**

    python3 tools/check_no_tier_b_gating.py

⚠⚠ **Structurally, not by convention** — the AC says so in those words, and the
reason is that this is the one rule most likely to erode by good intentions.
`PG-5.1`: *"Tier B accrues from day one and **never gates**."*

★★★ Why it would erode. Once `F7b` finally has numbers, they will be the most
*interesting* numbers in the system — *"did deliberation make us money?"* — and
reaching for them at a promotion decision is the natural move. ⚠ But at ~250
decisions a year against an underlying signal at **IC 0.0203, t = 1.42**, a
Tier-B result is a second-order measurement on an unestablished first-order one,
and **more time does not fix it: the noise grows with the sample.**

★ `D4` keeps the escape hatch honest: a powered Tier-B result that contradicts
Tier A is **escalated to the fund manager as a finding**, never applied. That is
`reconcile()`, and it returns a string for a human — it gates nothing.

⚠ Reading a Tier-B figure to REPORT it is fine. Only a gate is refused.
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

#: The Tier-B surface.
TIER_B_NAMES = ("TierBReport", "OutcomeStudyResult", "deliberation_lift",
                "deliberation_tier_b")

#: ⚠ Where a gate actually lives. A Tier-B name appearing in any of these is
#: the failure `AC-7b.5` names.
GATING_ROOTS = (
    "src/quant/gates", "src/decision", "src/orchestration/policy",
    "src/orchestration/control", "src/orchestration/graph",
    "src/shared/registry",
)

#: ★ The study itself, its own tests, and the reconciler may name it.
OWNERS = ("src/evaluation/studies/deliberation_tier_b.py",)


def _py(root: pathlib.Path):
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def tier_b_gating_violations(src_root: pathlib.Path | None = None) -> list[str]:
    """Every place a gating module reaches for a Tier-B result."""
    src_root = src_root or REPO
    out = []
    for rel in GATING_ROOTS:
        root = src_root / rel
        if not root.is_dir():
            continue
        for path in _py(root):
            rel_path = path.relative_to(src_root).as_posix()
            if rel_path in OWNERS:
                continue
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, str(path))
            except SyntaxError:                            # pragma: no cover
                continue
            for node in ast.walk(tree):
                name = None
                if isinstance(node, ast.Name):
                    name = node.id
                elif isinstance(node, ast.Attribute):
                    name = node.attr
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    name = getattr(node, "module", "") or ""
                if name and any(t in name for t in TIER_B_NAMES):
                    out.append(
                        f"{rel_path}:{node.lineno}: a GATING module references "
                        f"{name!r} — ⛔ AC-7b.5 / PG-5.1: Tier B accrues and "
                        "NEVER gates. At ~250 decisions a year against a signal "
                        "at IC 0.0203 / t = 1.42 it is a second-order "
                        "measurement on an unestablished first-order one, and "
                        "more time does not fix it. ★ A powered disagreement is "
                        "ESCALATED to the fund manager (D4), never applied.")
    return out


def main() -> int:
    bad = tier_b_gating_violations()
    if bad:
        print("⛔ AC-7b.5 — a Tier-B result reaches a gate:", file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-7b.5 — no promotion, graduation or deployment path reads Tier B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
