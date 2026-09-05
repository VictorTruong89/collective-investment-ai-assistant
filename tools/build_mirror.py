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
    "tools/check_all.py", "tools/check_framework_confinement.py",
    "tools/check_import_fences.py", "tools/check_evaluation_boundaries.py",
    "tools/build_mirror.py",
    "tests/", "tests_src/fixtures/", "tests_src/broker_fixtures.py",
    "tests_src/test_recording_ingest_synthetic.py",
    ".github/",
    ".claude/hooks/", ".claude/skills/",
    "sdd/specs/_templates/",
]

#: ⚠ A second, independent check. Nothing matching these may appear in the output
#: even if an INCLUDE entry would have carried it. Belt and braces on purpose:
#: this is the one script where a mistake is irreversible.
FORBIDDEN_FRAGMENTS = (
    "bmo_investorline", ".state", "trained_models", "reports/",
    "/data/", ".env", "secrets", ".pkl", ".joblib", ".parquet",
)


def _files_for(entry: str) -> list[pathlib.Path]:
    p = REPO / entry
    if p.is_file():
        return [p]
    if p.is_dir():
        return [q for q in p.rglob("*")
                if q.is_file() and "__pycache__" not in q.parts]
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
        # ⚠ and by filesystem path — DX-9's lesson applied here.
        src_text = f.read_text(encoding="utf-8")
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
    print("  ⚠ NO git history. Do not `git push` this into a repo that has any.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
