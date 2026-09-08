#!/usr/bin/env python3
"""`MS-8.7` — every ID family in use is DECLARED in constitution §1.

★★ **`MS-8` merged two ID spaces into one tree**, and constitution §1 opens with
*"read before inventing an ID"* plus *"every family below is reserved"*. That is
only true if the list is complete.

⚠⚠ It was not. At `MS-8` the merged tree used **39 families §1 did not name** —
and §1 had already been *"corrected 2026-09-02"* after missing eleven. ★ A
registry that drifts is worse than no registry: it reads as authoritative while
being half the story, which is exactly how `M-n` (mandate) and `M<n>`
(milestone) came to collide.

⚠ This check is deliberately **not** a naming-convention rule. It asks one
question: **is this family written down?** Meaning is a human's job; presence is
a machine's.
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CONSTITUTION = REPO / "sdd" / "specs" / "constitution.md"

SCAN_ROOTS = ("src", "sdd", "tests", "tests_src", "tools")
SCAN_SUFFIXES = (".py", ".md", ".yaml", ".yml")

#: An ID reference: `RA-45`, `AC-1.12`, `PG-10`.
_ID = re.compile(r"\b([A-Z]{1,4})-(\d{1,3})(?:\.\d+)?\b")

#: ⚠ Below this, a "family" is usually prose (`COVID-19`, `UTF-8`) rather than an
#: ID space. An admitted floor (`CN-10`) — nothing measured it; it exists so the
#: check reports real families instead of drowning in coincidences.
MIN_USES = 20


def declared_families() -> set[str]:
    """Families named in constitution §1."""
    text = CONSTITUTION.read_text(encoding="utf-8")
    section = text[text.index("# 1."):text.index("# 2.")]
    return (set(re.findall(r"`([A-Z]{1,4})[-`<]", section))
            | set(re.findall(r"\*\*`?([A-Z]{1,4})`?-", section)))


def families_in_use(root: pathlib.Path | None = None) -> collections.Counter:
    root = root or REPO
    counts: collections.Counter = collections.Counter()
    for name in SCAN_ROOTS:
        for p in (root / name).rglob("*"):
            if (not p.is_file() or p.suffix not in SCAN_SUFFIXES
                    or "__pycache__" in p.parts):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for fam, _ in _ID.findall(text):
                counts[fam] += 1
    return counts


def undeclared(root: pathlib.Path | None = None) -> dict[str, int]:
    declared = declared_families()
    return {f: n for f, n in families_in_use(root).items()
            if f not in declared and n >= MIN_USES}


def main() -> int:
    missing = undeclared()
    if missing:
        print(f"⛔ {len(missing)} ID families are in use but NOT declared in "
              "constitution §1:", file=sys.stderr)
        for f, n in sorted(missing.items(), key=lambda x: -x[1]):
            print(f"   {f:6} {n:5} uses", file=sys.stderr)
        print("\n★ §1 says 'every family below is reserved'. Add them, or the "
              "next ID collision will look like a free letter.", file=sys.stderr)
        return 1
    print(f"✅ MS-8.7 — every ID family in use (>={MIN_USES} uses) is declared in §1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
