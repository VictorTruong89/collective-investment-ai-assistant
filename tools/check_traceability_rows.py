#!/usr/bin/env python3
"""`DX-53` — ★★ a traceability row is a CLAIM; this resolves it.

    python3 tools/check_traceability_rows.py

⚠⚠ **Why this exists.** Constitution §6: *"Every spec keeps its traceability
table current … **an AC with no row is not done, however green the test is** —
because nobody can find it later."* ★ The rule says a row must EXIST. Nothing
said the row had to be **true**.

★★★ **Measured 2026-09-09, and the pattern is the point.** Six specs were
completed that day, and in every one a structural AC turned out to be
unenforced behind a row that read as coverage:

| spec | the row named | reality |
|---|---|---|
| `F6a` `AC-6a.6` | `check_import_fences.py` | existed, checked a **different fence** |
| `F9` `AC-F9.2` | `check_no_reimplementation.py` | **did not exist** |
| `F7a` `AC-7a.1` | `check_gate_ordering.py` | **did not exist** |
| `F8` `AC-8.16` | `check_no_raw_directive_in_prompt.py` | **did not exist** |
| `F7b` `AC-7b.5` | `check_no_tier_b_gating.py` | **did not exist** |
| `F3` `AC-3.10` | *(no row at all)* | **did not exist** |

⚠ **The rows are written by the same hand as the code, so they agree by
construction** — constitution §5.1's illegal move (*"improvise, then write a
test that agrees with the improvisation"*) displaced one level up, where nothing
was looking. ★ Invisible per-spec; obvious across six.

★★ **THE LIMIT, and it must travel with this check.** It resolves that a named
**file exists** and that a named **test function exists somewhere**. It cannot
verify that the named test *tests the named AC* — `AC-6a.6` above named a real
file that checked the wrong thing, and **no file-resolver finds that**. That
half stays a human's job, exactly as `tools/check_id_families.py` says: *"the
check asks only 'is it written down?'"*

⚠ Resolution is **basename-tolerant** (`DX-53` option ⓑ, Victor 2026-09-09):
rows legitimately abbreviate (`.../corroborate.py`, `::test_x`), and a strict
path rule would make ~30 honest rows illegal to buy nothing.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SPECS = REPO / "sdd/specs"

#: Where a named module or test may live. ⚠ `sdd_staging/` is deliberately
#: absent — it is separate work in progress and not part of this tree.
SEARCH_ROOTS = ("src", "tools", "tests", "tests_src", "sdd")

#: A token is a PATH if it ends in a source suffix. ★ Anything else in a row —
#: `AC-1.5`, `P4`, `RA-67`, a class name — is prose or a cross-reference and is
#: not this check's business.
PATH_SUFFIX = re.compile(r"\.(py|md|ya?ml)$")

#: `file.py::member` — only the file half is resolved.
MEMBER_SPLIT = "::"

#: ⚠ Rows use `*` to mean "and its siblings" (`::test_ac_5_7_*`). A trailing
#: star is stripped before lookup rather than treated as a literal name.
STAR = "*"


def _iter_rows():
    """Every `| AC-… |` row in every spec's §9 table."""
    for spec in sorted(SPECS.glob("F*/spec.md")):
        text = spec.read_text(encoding="utf-8")
        if "## 9." not in text:
            continue
        for line in text[text.index("## 9."):].splitlines():
            if line.startswith("| AC-"):
                yield spec, line


def _tokens(row: str):
    """Backticked tokens from the test and code cells."""
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    return re.findall(r"`([^`]+)`", " ".join(cells[1:]))


def _file_exists(path: str, roots) -> bool:
    """★ Exact repo-relative first, then a GLOB, then **basename** anywhere.

    ⚠ Rows legitimately write a glob (`src/shared/ports/*.py`) when an AC is
    satisfied by a directory rather than one module. ★ Treating that as a
    literal filename was this check's first false positive, caught on its first
    run — the same class of over-strictness option ⓐ would have institutionalised.
    """
    if (REPO / path).exists():
        return True
    if STAR in path:
        try:
            return any(REPO.glob(path))
        except (ValueError, IndexError):        # pragma: no cover — a bad pattern
            return False
    return pathlib.PurePosixPath(path).name in roots


def check() -> list[str]:
    """Every row whose named file or test cannot be found."""
    # ⚠ Built ONCE. A per-row rglob over ~2,000 test functions is the difference
    # between a check people run and a check people skip.
    files, test_names = set(), set()
    for root in SEARCH_ROOTS:
        base = REPO / root
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                files.add(path.name)
                if path.suffix == ".py":
                    test_names.update(
                        re.findall(r"^def (test_[A-Za-z0-9_]+)",
                                   path.read_text(encoding="utf-8", errors="ignore"),
                                   re.M))

    out = []
    for spec, row in _iter_rows():
        ac = row.strip("|").split("|")[0].strip()
        where = f"{spec.parent.name} {ac}"
        for token in _tokens(row):
            token = token.strip()
            if token.startswith("*(") or token.startswith("("):
                continue                       # ⚠ "(to be written)" and friends
            path, _, member = token.partition(MEMBER_SPLIT)
            path = path.strip().rstrip(STAR)
            if PATH_SUFFIX.search(path) and not _file_exists(path, files):
                out.append(f"{where}: names {path!r}, which does not exist "
                           "— ⚠ DX-53: a traceability row is a CLAIM, and an AC "
                           "whose named module is missing is not done "
                           "(constitution §6).")
            member = member.strip().rstrip(STAR)
            if (member.startswith("test_") and member not in test_names
                    and not any(t.startswith(member) for t in test_names)):
                out.append(f"{where}: names test {member!r}, which exists "
                           "nowhere — ⚠ a renamed or deleted test leaves the "
                           "row asserting coverage that is gone.")
    return out


def main() -> int:
    bad = check()
    if bad:
        print("⛔ DX-53 — a traceability row names something that does not exist:",
              file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    total = sum(1 for _ in _iter_rows())
    print(f"✅ DX-53 — all {total} traceability rows resolve to files and tests "
          "that exist (⚠ NOT that each test tests its AC — that stays human)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
