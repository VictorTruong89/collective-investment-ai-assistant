#!/usr/bin/env python3
"""Refresh `config/upstream_pin.json` — MS-2.3.

⚠ **Run this only after re-running BOTH suites.** The pin's job is to make a
`DX-n` attributable to a known upstream state; refreshing it without observing
that state replaces a real fact with a plausible-looking one, which is worse than
having no pin at all (`P5` — fail loud, never silent).

The test that guards the pin says "do not edit the pin to silence this". This
script exists so the legitimate path is one command, rather than a hand-edit that
looks identical to the illegitimate one.

    python3 tools/refresh_upstream_pin.py \
        --upstream-tests "1056 passed, 4 skipped" \
        --this-repo-tests "157 passed, 1 skipped" \
        --reason "committed the MS-2.2a absorption"
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import date

REPO = pathlib.Path(__file__).resolve().parents[1]
PIN = REPO / "config" / "upstream_pin.json"


def git(upstream: pathlib.Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(upstream), *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"git {' '.join(args)} failed in {upstream}: {r.stderr.strip()}")
    # ⚠ trailing newline ONLY — .strip() eats the leading space of the first
    # `git status --porcelain` line and truncates that path's first character.
    return r.stdout.rstrip("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream-tests", required=True, help='e.g. "1056 passed, 4 skipped"')
    ap.add_argument("--this-repo-tests", required=True, help='e.g. "157 passed, 1 skipped"')
    ap.add_argument("--reason", required=True, help="why the pin moved — goes into the file")
    ap.add_argument("--milestone", default="", help="milestone doing the refresh, e.g. MS-3")
    args = ap.parse_args()

    pin = json.loads(PIN.read_text(encoding="utf-8"))
    upstream = (REPO / pin["repo"]).resolve()

    head = git(upstream, "rev-parse", "HEAD").strip()
    branch = git(upstream, "rev-parse", "--abbrev-ref", "HEAD").strip()
    dirty = sorted(
        line[3:] for line in git(upstream, "status", "--porcelain").splitlines()
        if line and not line.startswith("??")
    )

    was = pin["commit"]
    pin.update(
        commit=head,
        branch=branch,
        pinned_at=date.today().isoformat(),
        pinned_at_milestone=args.milestone or pin.get("pinned_at_milestone", ""),
    )
    pin["verified"].update(
        upstream_tests=args.upstream_tests, this_repo_tests=args.this_repo_tests
    )
    pin["expected_uncommitted"]["paths"] = dirty
    pin["last_refresh_reason"] = args.reason

    PIN.write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")

    print(f"pin: {was[:12]} -> {head[:12]} on {branch}")
    print(f"     {len(dirty)} expected-uncommitted path(s)")
    if dirty:
        print("     ⚠ upstream is DIRTY — every one of these is an unreviewed difference")
        for d in dirty:
            print(f"       {d}")
    else:
        print("     ✅ upstream tree is clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
