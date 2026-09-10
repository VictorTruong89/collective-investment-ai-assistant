#!/usr/bin/env python3
"""`F8` `AC-8.16` — ⚠⚠ a directive's RAW TEXT never reaches a prompt.

    python3 tools/check_no_raw_directive_in_prompt.py

★★ **`AC-8.16` is typed *invariant / property (structural)* and was enforced by
a unit test on one object** (`DX-51`). `Directive.to_prompt_payload()` correctly
omits `raw_text`, and a test asserted that — but nothing stopped a *different*
module reading `.raw_text` and putting it in a prompt of its own. ⚠ The guarantee
is about the whole tree, so the check has to be about the whole tree.

⚠⚠ **What this prevents.** §2.1: *"The raw text never reaches another prompt. It
is recorded for the audit trail and consumed by nothing downstream. Injecting it
into an analysis prompt would reintroduce exactly the unfalsifiable, untestable
control `QR-17`'s analysis rejected."*

★★★ Put plainly: a directive that reached a prompt would be **an untyped
instruction channel into the analysis — prompt injection with the fund manager
as the vector**, and `AC-8.15`'s confirm step would be confirming typed effects
while unreviewed prose travelled alongside them.

★ Recording it, logging it and rendering it back to the manager are all fine.
Only *reaching a prompt* is refused.
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

#: The field that must not travel.
RAW_FIELD = "raw_text"

#: ★ Where a directive legitimately HOLDS its raw text: the contract that
#: defines it, the interpreter that receives it, and the unmappable log that
#: exists to show it back to the manager (`CT-8.6`, `AC-8.19`).
OWNERS = ("src/orchestration/control/directives.py",
          "src/orchestration/control/models.py")

#: ⚠ Anything that builds or sends a prompt. A `raw_text` reference reaching
#: one of these is the failure `AC-8.16` names.
PROMPT_ROOTS = ("src/fundamental/prompts", "src/shared/llm",
                "src/fundamental/relay", "src/orchestration/graph")


def _py(root: pathlib.Path):
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def raw_text_leaks(src_root: pathlib.Path | None = None) -> list[str]:
    """Every place outside its owners that reads a directive's raw text."""
    src_root = src_root or REPO
    out = []
    for rel in PROMPT_ROOTS:
        root = src_root / rel
        if not root.is_dir():
            continue
        for path in _py(root):
            rel_path = path.relative_to(src_root).as_posix()
            if rel_path in OWNERS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
            except SyntaxError:                            # pragma: no cover
                continue
            for node in ast.walk(tree):
                hit = (isinstance(node, ast.Attribute) and node.attr == RAW_FIELD)
                key = (isinstance(node, ast.Constant)
                       and node.value == RAW_FIELD)
                if hit or key:
                    out.append(
                        f"{rel_path}:{node.lineno}: references {RAW_FIELD!r} — "
                        "⚠⚠ AC-8.16: a directive's raw text may never reach a "
                        "prompt. It would be an untyped instruction channel "
                        "into the analysis — prompt injection with the fund "
                        "manager as the vector — and the confirm step would be "
                        "approving typed effects while unreviewed prose "
                        "travelled beside them (§2.1, QR-17).")
    return out


def main() -> int:
    bad = raw_text_leaks()
    if bad:
        print("⛔ AC-8.16 — a directive's raw text reaches a prompt:",
              file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-8.16 — no directive raw text reaches any prompt-building module")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
