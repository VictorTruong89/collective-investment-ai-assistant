"""MS-2.3 — the upstream revision is pinned, and drift fails LOUD.

WHY THIS EXISTS
---------------
`L3` `MS-2.3`: *"Pin the upstream revision. A moving dependency makes
discrepancies unattributable."* Absorption is per-domain (`QR-22`), so this repo
imports `src.quant.*`, `src.orchestration.*` … straight out of a sibling working
tree — **not a released package**. Nothing about that is version-controlled from
this side: someone can `git pull` upstream and this repo's tests keep passing
against different code, silently.

⚠ That is the same shape as `DX-3` — a check that stops checking without saying
so. A `DX-n` recorded today is worthless if nobody can say which upstream state
produced it.

WHAT IT ENFORCES
----------------
1. the sibling repo is where the pin says it is;
2. its `HEAD` and branch are what the pin says;
3. every uncommitted tracked path is one the pin **expects**.

★ (3) is the interesting one. Upstream is *legitimately* dirty right now — the
`MS-2.2a` absorption and `MS-2.2b` multi-root change were made there and await
review. A pin that ignored that would be a lie; one that merely failed would be
noise. So the pin lists the expected delta and fails only on the **unexpected** —
which is exactly what "attributable" means.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PIN_PATH = REPO / "config" / "upstream_pin.json"


def _pin() -> dict:
    assert PIN_PATH.exists(), f"missing pin file: {PIN_PATH} (MS-2.3)"
    return json.loads(PIN_PATH.read_text(encoding="utf-8"))


def _upstream() -> pathlib.Path:
    return (REPO / _pin()["repo"]).resolve()


def _git(*args: str) -> str:
    """⚠ Strips only the TRAILING newline.

    `.strip()` here was a real bug: `git status --porcelain` puts the status in
    columns 1-2 and the path at index 3, so an unstaged edit reads
    ` M pyproject.toml` — and stripping the whole output ate the leading space of
    the FIRST line only, turning it into `yproject.toml`. The pin generator had
    the identical bug, so the two agreed and the suite passed. ★ Two wrongs
    cancelling is exactly why the parsing now has its own regression test below.
    """
    r = subprocess.run(
        ["git", "-C", str(_upstream()), *args], capture_output=True, text=True
    )
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr.strip()}"
    return r.stdout.rstrip("\n")


def _porcelain_paths(output: str) -> set[str]:
    """Tracked-file paths from `git status --porcelain` — index 3 onwards."""
    return {line[3:] for line in output.splitlines() if line and not line.startswith("??")}


def test_the_pinned_upstream_repo_exists():
    """Without the sibling, every cross-repo import resolves to nothing."""
    up = _upstream()
    assert up.is_dir(), (
        f"pinned upstream not found at {up}. This repo imports src.quant.*, "
        "src.orchestration.* etc. from that working tree (QR-22). Clone it as a "
        "sibling, or update config/upstream_pin.json."
    )
    assert (up / ".git").exists(), f"{up} is not a git repo — the pin cannot be verified"


def test_upstream_is_on_the_pinned_commit():
    """⚠ The whole point: a discrepancy must be attributable to a known state."""
    pin = _pin()
    head = _git("rev-parse", "HEAD").strip()
    assert head == pin["commit"], (
        f"upstream moved.\n"
        f"  pinned : {pin['commit']}  ({pin['pinned_at']}, {pin['pinned_at_milestone']})\n"
        f"  actual : {head}\n"
        "Every DX-n recorded against the old pin now refers to code that is no longer "
        "there. Re-run BOTH suites, then refresh config/upstream_pin.json — do not "
        "edit the pin to silence this."
    )


def test_upstream_is_on_the_pinned_branch():
    pin = _pin()
    branch = _git("rev-parse", "--abbrev-ref", "HEAD").strip()
    assert branch == pin["branch"], (
        f"upstream is on {branch!r}, pinned to {pin['branch']!r}. A different branch "
        "is a different dependency."
    )


def test_no_unexpected_uncommitted_changes_upstream():
    """★ Distinguishes KNOWN pending work from unattributed drift."""
    pin = _pin()
    expected = set(pin["expected_uncommitted"]["paths"])
    actual = _porcelain_paths(_git("status", "--porcelain"))
    unexpected = sorted(actual - expected)
    assert not unexpected, (
        "upstream has uncommitted changes the pin does not account for:\n  "
        + "\n  ".join(unexpected)
        + "\nEither they are intended — add them to expected_uncommitted.paths with a "
        "reason — or someone edited upstream underneath this repo."
    )


def test_pin_records_what_was_verified_against_it():
    """A pin with no observed results cannot show drift, only identity."""
    v = _pin()["verified"]
    for key in ("upstream_tests", "this_repo_tests"):
        assert v.get(key), f"pin is missing verified.{key} — refresh it with real counts"


def test_expected_uncommitted_is_documented_not_a_blanket_allowance():
    """⚠ Guard against the list quietly becoming 'anything goes'.

    An entry is a deliberate, reviewed exception. A wildcard would turn this
    whole file into decoration — the `DX-3` failure mode, one level up.
    """
    block = _pin()["expected_uncommitted"]
    assert block.get("_note"), "expected_uncommitted must carry a _note explaining itself"
    assert not any("*" in p for p in block["paths"]), (
        "wildcards are not allowed in expected_uncommitted — list paths explicitly"
    )


@pytest.mark.parametrize(
    "line,expected",
    [
        (" M pyproject.toml", {"pyproject.toml"}),          # unstaged edit — the bug case
        ("D  src/shared/money.py", {"src/shared/money.py"}),  # staged delete
        ("?? untracked.txt", set()),                          # untracked: ignored
        ("MM a/b.py", {"a/b.py"}),
        ("", set()),
    ],
)
def test_porcelain_parsing_keeps_the_first_character_of_the_path(line, expected):
    """⚠ Regression — `.strip()` on the whole output ate the leading space of the
    first line, silently dropping the path's first character (`yproject.toml`).

    Both the pin and its checker had the same defect, so they agreed with each
    other and nothing failed. A shared bug is invisible to a comparison.
    """
    assert _porcelain_paths(line) == expected
