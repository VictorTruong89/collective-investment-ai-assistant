#!/usr/bin/env python3
"""`MS-9.1` — assemble the curated public mirror. ⚠⚠ DRY-RUN BY DEFAULT.

★ `QR-12`: **source-available, all rights reserved.** The mirror exists so a
reviewer can read the engineering. It is **not** a working fund.

⚠⚠ **What must never leave this machine**, and why this script refuses rather
than filters:

  · real BMO broker statements  — `DX-5`, personal financial data
  · `.state/`, `data/`, `reports/`, `logs/`, `trained_models/`
  · anything `.gitignore` covers
  · the **strategy** — the analytical domains are the fund's edge (`QR-12`)

★ **The allowlist is positive, not negative.** A deny-list is one forgotten path
away from a leak; an allow-list is one forgotten path away from an *incomplete
mirror*, which is a bug you notice. That asymmetry is the whole design.

⚠ **No git history.** The mirror is a fresh tree. History would carry paths,
commit messages and possibly data the curation removed.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: ★ PLATFORM ONLY — the layers this project claims as its engineering
#: contribution. ⚠ The analytical domains (quant, models, risk, portfolio,
#: decision, fundamental, recording, reporting, feature_engineer) are the
#: strategy and are DELIBERATELY ABSENT.
INCLUDE = [
    "README.md", "LICENSE", "pyproject.toml", ".gitignore",
    "CLAUDE.md",
    "docs/",
    "sdd/specs/",
    "sdd/questions.md",
    "sdd/README.md",
    "src/shared/registry/", "src/shared/ports/",
    "src/orchestration/trace/", "src/orchestration/control/",
    "src/orchestration/graph/", "src/orchestration/policy/routing.py",
    "src/evaluation/", "src/explain/",
    # ⚠⚠ DX-22: `check_all.py` INVOKES these as subprocesses. A tool that
    # invokes a missing tool ships a red check to a fresh clone — and the
    # `DX-14` guard never saw it, because it models tests importing code, not
    # a tool spawning a tool. ★ Verified now by RUNNING check_all in the mirror.
    "tools/check_all.py", "tools/check_framework_confinement.py",
    "tools/check_import_fences.py", "tools/check_evaluation_boundaries.py",
    "tools/check_id_families.py",
    "tools/build_mirror.py",
    # ★ The golden-case demo and its adversarial reviewer. `PG-5` calls the
    # evaluation instinct the scarce skill; these are where it is legible.
    "tools/demo_golden_case.py", "tools/review_golden_case.py",
    "tools/f2_payload_reader.py",
    "tests/",
    # ⚠⚠ `tests_src/fixtures/broker_statements/` ONLY — NOT the whole fixtures
    # directory. `tests_src/fixtures/golden/` holds the golden set, whose
    # `expected` values for `ranking` and `thesis` ARE the fund's judgement, i.e.
    # the strategy QR-12 withholds. ★ The mirror ships the machinery without the
    # answers. (F5 CT-5.5.)
    "tests_src/fixtures/broker_statements/", "tests_src/broker_fixtures.py",
    "tests_src/test_recording_ingest_synthetic.py",
    ".github/",
    ".claude/hooks/", ".claude/skills/",
    "sdd/specs/_templates/",
]

#: ⚠⚠ Tests that assert about the FULL tree's composition. They are correct in
#: this repo and meaningless in the mirror, which is a deliberately narrowed
#: tree — e.g. `test_id_families` asserts `QA` (D-03 quant) is in heavy use, and
#: `src/quant/` is withheld as strategy, so it counts 6 and fails.
#:
#: ★ Excluded EXPLICITLY here rather than taught to skip when the tree looks
#: small. ⚠ "Skip when narrowed" is `DX-9` exactly — the shape where a check
#: quietly stops checking. A named exclusion with a written reason cannot rot
#: silently; a self-disabling assertion can.
MIRROR_EXCLUDE_TESTS = (
    "tests/structural/test_id_families.py",
)

#: ⚠ A second, independent check. Nothing matching these may appear in the output
#: even if an INCLUDE entry would have carried it. Belt and braces on purpose:
#: this is the one script where a mistake is irreversible.
FORBIDDEN_FRAGMENTS = (
    "bmo_investorline", ".state", "trained_models", "reports/",
    "fixtures/golden",   # ⚠ the golden set is the strategy (F5 CT-5.5)
    "/data/", ".env", "secrets", ".pkl", ".joblib", ".parquet",
)


def _files_for(entry: str) -> list[pathlib.Path]:
    p = REPO / entry
    if p.is_file():
        return [p] if p.suffix not in (".pyc", ".pyo") else []
    if p.is_dir():
        # ⚠ __pycache__ is excluded here, not only in the test scan: a .pyc
        # embeds the ABSOLUTE source path it was compiled from, so publishing one
        # leaks `/home/<user>/Workspace/...` into a public repo.
        return [q for q in p.rglob("*")
                if q.is_file() and "__pycache__" not in q.parts
                and q.suffix not in (".pyc", ".pyo")]
    return []


def _gitignored(paths: list[pathlib.Path]) -> set[pathlib.Path]:
    if not paths:
        return set()
    rel = [str(p.relative_to(REPO)) for p in paths]
    r = subprocess.run(["git", "-C", str(REPO), "check-ignore", "--stdin"],
                       input="\n".join(rel), capture_output=True, text=True)
    return {REPO / line for line in r.stdout.splitlines() if line}


def _module_is_included(mod: str, included: set[str]) -> bool:
    """Would `import mod` resolve inside the mirror?"""
    if not mod.startswith(("src.", "tests_src.", "tools.")):
        return True                       # stdlib / third-party
    # ⚠ The FULL dotted path only. An ancestor match is wrong: `src/orchestration/`
    # is PARTIALLY included (trace/, control/, graph/), which made every
    # `src.orchestration.*` import look present — including `jobs`, which is
    # withheld. That is how DX-14 survived its own first fix.
    stem = mod.replace(".", "/")
    return f"{stem}.py" in included or f"{stem}/__init__.py" in included


#: ⚠⚠ DX-9's shape, a THIRD time. A test can depend on the tree by IMPORT or by
#: FILESYSTEM PATH, and an import-only check sees half of them. These are the
#: prefixes a repo-relative path literal starts with.
_PATH_PREFIXES = ("sdd/", ".claude/", "config/", "src/", "tools/", "docs/",
                  "tests/", "tests_src/", "backups/")


def _path_literals(source: str) -> set[str]:
    import re
    return set(re.findall(r'["\']((?:' + "|".join(
        p.replace(".", r"\.") for p in _PATH_PREFIXES) + r')[A-Za-z0-9_./*-]*)["\']',
        source))


def unrunnable_tests(files: list[pathlib.Path]) -> list[pathlib.Path]:
    """⚠ DX-14 — tests the curation breaks, by IMPORT **or** by PATH.

    ★ COMPUTED from the allowlist, never hand-kept: a maintained list would drift
    the moment INCLUDE changed, and the failure mode is a mirror that does not
    collect — which is a reviewer's first impression.
    """
    import ast
    included = {str(f.relative_to(REPO)) for f in files}
    bad = []
    for f in files:
        rel = str(f.relative_to(REPO))
        if not (rel.startswith(("tests/", "tests_src/")) and rel.endswith(".py")):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                mods.add(n.module)
        if any(not _module_is_included(m, included) for m in mods):
            bad.append(f)
            continue
        # ⚠⚠ and by filesystem path — DX-9's lesson, ONE HOP DEEP.
        # A test can reach a withheld directory through a CONSTANT it imports
        # (`from ...store import GOLDEN_DIR`), so scanning only the test file
        # misses it. Found when `test_golden_store.py` shipped and failed in the
        # mirror because `tests_src/fixtures/golden/` is withheld.
        src_text = f.read_text(encoding="utf-8")
        for mod in mods:
            if not mod.startswith("src."):
                continue
            for cand in (REPO / (mod.replace(".", "/") + ".py"),
                         REPO / mod.replace(".", "/") / "__init__.py"):
                if cand.exists():
                    src_text += "\n" + cand.read_text(encoding="utf-8")
        for lit in _path_literals(src_text):
            stem = lit.rstrip("/*")
            if not stem or "*" in lit:
                continue
            if stem in included or any(x.startswith(stem + "/") for x in included):
                continue
            bad.append(f)
            break
    return bad


def collect() -> tuple[list[pathlib.Path], list[str]]:
    """Returns (files, refusals). ⚠ A non-empty refusal list means DO NOT SHIP."""
    files: list[pathlib.Path] = []
    for entry in INCLUDE:
        files.extend(_files_for(entry))
    files = sorted(set(files))

    refusals: list[str] = []
    ignored = _gitignored(files)
    for f in files:
        rel = str(f.relative_to(REPO))
        if f in ignored:
            refusals.append(f"{rel} — .gitignore covers it, so it must not be published")
        for frag in FORBIDDEN_FRAGMENTS:
            if frag in rel:
                refusals.append(f"{rel} — matches forbidden fragment {frag!r}")
    kept = [f for f in files if f not in ignored]
    # ⚠ DX-14 — drop tests that cannot run without the withheld strategy, and SAY
    # how many. Publishing a suite that does not collect is worse than publishing
    # a smaller one.
    kept = [f for f in kept
            if str(f.relative_to(REPO)) not in MIRROR_EXCLUDE_TESTS]
    unrunnable = unrunnable_tests(kept)
    if unrunnable:
        print(f"  ⚠ dropping {len(unrunnable)} test file(s) that import withheld "
              "domains (DX-14) — the mirror must be able to run its own suite:")
        for f in unrunnable:
            print(f"      {f.relative_to(REPO)}")
    return [f for f in kept if f not in set(unrunnable)], refusals


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="write the mirror here (otherwise dry-run)")
    ap.add_argument("--i-have-read-the-refusals", action="store_true",
                    help="⚠ required to write even when refusals is empty")
    args = ap.parse_args()

    files, refusals = collect()
    print(f"  mirror would contain {len(files)} files from {len(INCLUDE)} allowlist entries")
    by_top: dict[str, int] = {}
    for f in files:
        by_top[str(f.relative_to(REPO)).split("/")[0]] = \
            by_top.get(str(f.relative_to(REPO)).split("/")[0], 0) + 1
    for k, v in sorted(by_top.items()):
        print(f"      {k:16} {v}")

    print("\n  ★ DELIBERATELY ABSENT (the strategy — QR-12):")
    for d in sorted(p.name for p in (REPO / "src").iterdir()
                    if p.is_dir() and p.name != "__pycache__"):
        if not any(str(f.relative_to(REPO)).startswith(f"src/{d}/") for f in files):
            print(f"      src/{d}/")

    if refusals:
        print(f"\n  ⛔ {len(refusals)} REFUSAL(S) — DO NOT SHIP:")
        for r in refusals:
            print(f"      {r}")
        return 1
    print("\n  ✅ no refusals: nothing gitignored or sensitive is in the set")

    if not args.out:
        print("  ⓘ dry-run. Pass --out DIR --i-have-read-the-refusals to write.")
        return 0
    if not args.i_have_read_the_refusals:
        print("  ⛔ refusing to write without --i-have-read-the-refusals")
        return 1

    out = pathlib.Path(args.out)
    if out.exists():
        print(f"  ⛔ {out} exists — refusing to overwrite")
        return 1
    for f in files:
        dest = out / f.relative_to(REPO)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
    print(f"  ✅ wrote {len(files)} files to {out}")

    # ⚠⚠ DX-22 — the generalisation. Three times now the mirror's self-check was
    # written against ONE kind of dependency and a second kind was already
    # shipping broken (DX-14 tests importing code, DX-19 an imported constant,
    # DX-22 a tool spawning a tool). ★★ So stop enumerating dependency kinds and
    # RUN THE DOCUMENTED ENTRY POINT. Whatever it needs, it will say so itself.
    print("\n  ── verifying the mirror can run its own checks (DX-22) ──")
    proc = subprocess.run([sys.executable, "tools/check_all.py"], cwd=out,
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-12:]
        print("  ⛔ THE MIRROR'S OWN check_all.py FAILS — do not publish:")
        for line in tail:
            print(f"      {line}")
        return 1
    print("  ✅ the mirror's check_all.py passes in the mirror")
    print("  ⚠ NO git history. Do not `git push` this into a repo that has any.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
