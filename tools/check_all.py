#!/usr/bin/env python3
"""`MS-1.1` — run every guarantee this repo relies on. One command.

⚠⚠ **Why this exists.** Nine guarantees were established between `MS-1` and
`MS-7`, and every one of them held **because it was run by hand, once**:

    1  ruff, on the code this repo authored
    2  this repo's test suite
    3  the fresh-clone simulation (DX-5 — a clone must be green)
    4  AC-2.10  framework confinement (QR-14)
    5  AC-4.2/4.7  the analyst firewall at seat 6 (INV-014)
    6  AC-5.11/5.12/5.15  evaluation boundaries (ST-2, D1)
    7  ownership.yaml glob ordering + ST-8 stale globs (L4 §5.1)
    8  MS-8.7  every ID family in use is declared in constitution §1

✏ **MS-8**: the upstream-suite and upstream-pin checks are gone — there is one
tree now. ⚠ The fresh-clone check STAYS and matters more, not less: `DX-5`'s real
broker statements are still absent from git, and this is what proves a clone is
green rather than merely quiet.

★ Checks 5-9 are pytest tests and CI would catch them anyway; they are named
here because a green suite of 960 does not tell a reader **which** guarantees it
contains. `--list` prints them without running anything.

⚠ Exit code is non-zero if ANY check fails. It does not stop at the first —
seeing all failures at once is what makes a broken merge diagnosable.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
#: The paths THIS repo authored. ⚠ Absorbed trees are excluded in pyproject and
#: held to a separate baseline — they are inherited, not ours to reformat (PG-8).
OURS = [
    "src/shared/registry", "src/shared/ports", "src/orchestration/trace",
    "src/orchestration/control", "src/orchestration/graph",
    "src/orchestration/policy/routing.py", "src/evaluation", "src/explain",
    "src/data_engine/corporate_actions", "src/fundamental/source", "tests",
    # ⚠ tools/ is mixed: check_all, check_*, refresh_* are ours; sdd_audit.py and
    # inspect_data.py arrived at MS-8 and are excluded in pyproject.
    "tools",
]


def run(name: str, cmd: list[str], cwd: pathlib.Path, env: dict | None = None):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                       env={**os.environ, **(env or {})})
    ok = r.returncode == 0
    tail = (r.stdout or r.stderr).strip().splitlines()
    print(f"  {'✅' if ok else '⛔'} {name:44} {tail[-1][:56] if tail else ''}")
    if not ok:
        for line in (r.stdout or r.stderr).strip().splitlines()[-25:]:
            print(f"       {line}")
    return ok


CHECKS = [
    "ruff (code this repo authored)",
    "the test suite",
    "the suite from a FRESH CLONE (DX-5)",
    "AC-2.10 framework confinement",
    "AC-4.2/4.7 analyst firewall",
    "AC-5.11/5.12/5.15 evaluation boundaries",
    "AC-9.2 the relay is wrapped, not rebuilt",
    "AC-7a.1 F6b's measurement gate is in place",
    "MS-8.7 ID-family registry",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="name the checks, run nothing")
    args = ap.parse_args()
    if args.list:
        for c in CHECKS:
            print(f"  · {c}")
        return 0

    py = sys.executable
    results = []
    print("── MS-1.1 · every guarantee, in one place ──")

    results.append(run(CHECKS[0], # ⚠ --force-exclude: ruff does NOT apply `extend-exclude` to paths given
    # explicitly on the command line, so inherited files under tools/ and src/
    # would be linted despite being excluded in pyproject.
    [py, "-m", "ruff", "check", "--force-exclude", *OURS], REPO))
    results.append(run(CHECKS[1], [py, "-m", "pytest", "-q"], REPO))
    # ⚠ DX-5 — the real broker statements are not in git and never will be. This
    # proves a clone is GREEN, not merely quiet.
    results.append(run(CHECKS[2], [py, "-m", "pytest", "-q"], REPO,
                       env={"BMO_STATEMENTS_DIR": "/nonexistent"}))
    results.append(run(CHECKS[3], [py, "tools/check_framework_confinement.py"], REPO))
    results.append(run(CHECKS[4], [py, "tools/check_import_fences.py"], REPO))
    results.append(run(CHECKS[5], [py, "tools/check_evaluation_boundaries.py"], REPO))
    # ⚠ `AC-9.2` — added 2026-09-09 (`DX-42`). The spec's traceability row named
    # `tools/check_no_reimplementation.py` and the file did not exist, so F9's
    # FIRST non-goal was enforced by nothing.
    results.append(run(CHECKS[6], [py, "tools/check_no_reimplementation.py"], REPO))
    # ⚠ `AC-7a.1` — `PG-5.1` as a build check. `F6b` may not graduate before the
    # design that measures it exists, and a gate living only in a spec header is
    # enforced by whoever remembers it when least motivated to (`DX-47`).
    results.append(run(CHECKS[7], [py, "tools/check_gate_ordering.py"], REPO))
    results.append(run(CHECKS[8], [py, "tools/check_id_families.py"], REPO))

    failed = results.count(False)
    print("──" * 20)
    if failed:
        print(f"  ⛔ {failed} CHECK(S) FAILED")
        return 1
    print("  ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
