"""`ownership.yaml` is first-match-wins — so ORDER is load-bearing. `L4` §5.1.

⚠⚠ This was scheduled as `MS-8` item 8.4a, *"assert glob ordering"*, on the
assumption the hazard arrived at absorption. **It arrived at `MS-2.7` instead**,
the moment `src/orchestration/**` was absorbed while four platform paths already
lived inside it:

    src/orchestration/trace/**         -> F2
    src/orchestration/policy/routing.py -> F6a
    src/orchestration/control/**       -> F8
    src/orchestration/graph/**         -> F6b

★ **Why this needs a test and not a comment.** If the broad inherited glob were
ordered above them, the inherited L1 spec would govern platform code, **the gate
would still fire**, the edit would still be allowed after reading *a* spec — and
nothing would look broken. The failure is invisible by construction, which is
exactly the class `ST-8` names for stale globs and `DX-3` found for stale fences.
"""

from __future__ import annotations

import fnmatch
import glob as _glob
import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
OWNERSHIP = REPO / "sdd" / "specs" / "ownership.yaml"

#: Globs for code not written yet. ⚠ A glob matching nothing makes the gate fail
#: OPEN, silently (ST-8) — tolerable only while the path is KNOWN not to exist.
#: Anything not listed here that matches nothing is a stale glob, and fails.
# ⚠ 2026-09-04: src/orchestration/trace/** (MS-3), src/evaluation/** (MS-4) and
# src/explain/** (MS-5), and at MS-6 all four of F3/F6a/F8/F9's paths — every
# one removed because the guard below fired first. That is exactly what it is
# for, and it has now fired on FIVE consecutive milestones (MS-3..MS-7).
KNOWN_UNBUILT = {
    "src/shared/agents/**",
}


def _entries():
    return yaml.safe_load(OWNERSHIP.read_text(encoding="utf-8"))["map"]


def _flat():
    return [(i, g, e["spec"]) for i, e in enumerate(_entries()) for g in e["globs"]]


def _covers(broad: str, narrow: str) -> bool:
    """Would `broad` also match everything `narrow` matches?"""
    if broad == narrow:
        return False
    probe = narrow.replace("**", "x/y").replace("*", "x")
    return fnmatch.fnmatch(probe, broad) or probe.startswith(broad.rstrip("*"))


def test_specific_globs_come_before_the_broad_ones_that_contain_them():
    """`L4` §5.1 — first match wins, so the container must never be first."""
    flat = _flat()
    wrong = [
        f"{broad!r} (entry {i}) contains {narrow!r} (entry {j}) but is ordered FIRST — "
        f"{narrow} would be governed by {bspec} instead of {nspec}"
        for i, broad, bspec in flat
        for j, narrow, nspec in flat
        if _covers(broad, narrow) and i < j
    ]
    assert not wrong, "ownership.yaml ordering violates L4 §5.1:\n  " + "\n  ".join(wrong)


def test_every_spec_path_exists():
    """⚠ A `spec:` the gate cannot read blocks its path forever.

    `sdd_gate.py`'s `rel()` returns None outside the repo, so a spec that is
    missing — or that lives in the sibling repo — can never enter the session
    ledger, and every edit under its globs is denied with no way to satisfy it.
    """
    missing = sorted({s for _, _, s in _flat() if not (REPO / s).exists()})
    assert not missing, f"ownership.yaml names spec files that do not exist: {missing}"


def test_no_stale_globs():
    """`ST-8` — a glob matching nothing makes the gate fail OPEN, silently."""
    dead = {g for _, g, _ in _flat() if not _glob.glob(str(REPO / g), recursive=True)}
    stale = sorted(dead - KNOWN_UNBUILT)
    assert not stale, (
        f"these globs match no files and are not listed as KNOWN_UNBUILT: {stale}. "
        "Either the code moved without its glob (ST-8 — the gate now fails OPEN "
        "for that path), or the glob is a typo."
    )


def test_known_unbuilt_shrinks_and_never_lies():
    """⚠ The allowlist must not outlive its entries.

    A path listed as unbuilt that now EXISTS means the list is stale, and a stale
    allowlist quietly re-permits the thing it was meant to permit only once.
    """
    built = sorted(g for g in KNOWN_UNBUILT if _glob.glob(str(REPO / g), recursive=True))
    assert not built, (
        f"these are listed KNOWN_UNBUILT but now exist: {built}. Remove them — "
        "the list is what makes test_no_stale_globs meaningful."
    )


@pytest.mark.parametrize(
    "path,expected_tail",
    [
        ("src/orchestration/trace/store.py", "F2_trace_replay/spec.md"),
        ("src/orchestration/policy/routing.py", "F6a_config_routing/spec.md"),
        ("src/orchestration/graph/build.py", "F6b_deliberation/spec.md"),
        ("src/orchestration/control/api.py", "F8_control_surface/spec.md"),
        ("src/orchestration/policy/budget.py", "L1-orchestration.md"),
        ("src/orchestration/entrypoint.py", "L1-orchestration.md"),
        ("src/orchestration/state/locks.py", "L1-orchestration.md"),
        ("src/shared/registry/registry.py", "F1_module_registry/spec.md"),
        ("src/shared/money.py", "L2-shared-money.md"),
    ],
)
def test_the_absorbed_boundary_resolves_as_intended(path, expected_tail):
    """★ The four platform paths inside D-08 must reach their OWN specs."""
    hit = next(
        (s for i, g, s in _flat()
         if fnmatch.fnmatch(path, g) or path.startswith(g.rstrip("*"))),
        None,
    )
    assert hit and hit.endswith(expected_tail), f"{path} -> {hit}, expected …{expected_tail}"
