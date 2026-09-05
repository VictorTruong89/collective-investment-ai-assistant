"""The architectural rules hold on the real src/ tree.

L3 BS-4: the checked import edges go in CI at B0, not later — cheap on an empty
tree and expensive on a full one, and their whole purpose is to prevent an
architecture that has already been built wrong.

Tier: invariant/property (constitution §4) — these hold for ALL files under
src/, not for a chosen example.

⚠ These tests passing on an empty tree proves nothing on its own. That is what
test_architecture_violates.py is for (BS-5).
"""

from __future__ import annotations

import pytest

from tests_src.architecture import RULES, SRC_ROOTS, scan


@pytest.fixture(scope="module")
def graph():
    return scan()


@pytest.mark.parametrize("rule_id,spec,check", RULES, ids=[r[0] for r in RULES])
def test_architectural_rule_holds(rule_id, spec, check, graph):
    """BS-4 — every declared import edge is checked in CI."""
    violations = check(graph)
    assert not violations, (
        f"{rule_id} ({spec}) violated:\n  " + "\n  ".join(violations)
    )


def test_every_domain_directory_is_a_package(graph):
    """L4 §1.1 — a domain directory without __init__.py is not importable.

    Caught early because the failure mode is confusing: imports resolve via
    namespace packages until one does not, and the error names the wrong file.
    """
    # A directory holding no Python is DATA, not a package — `quant/methods/entries/`
    # is markdown MethodEntries (CT-3.3). Adding an __init__.py there would claim
    # it is importable, which is exactly the confusion this check exists to remove.
    #
    # ⚠ Spans every root (DX-3): scoping this to one repo would stop checking an
    # absorbed domain the day it moved, and pass while doing so.
    missing = [
        str(d.relative_to(root.parent))
        for root in SRC_ROOTS
        for d in sorted(root.rglob("*"))
        if d.is_dir() and not d.name.startswith("__")
        and any(d.glob("*.py"))
        and not (d / "__init__.py").exists()
    ]
    assert not missing, f"domain directories missing __init__.py: {missing}"


def test_the_graph_is_not_vacuous(graph):
    """⚠⚠ DX-3 — the guard against the guards.

    SI-1 once went from policing `src/shared/` to scanning ZERO files, because
    the directory was absorbed into a sibling repo while the rule still looked
    only here. It reported `14 passed`. ★ A rule that CANNOT fail is
    indistinguishable from one that passes; the only defence is to assert it
    still has something to examine.
    """
    assert len(SRC_ROOTS) >= 1
    per_prefix = {
        prefix: sum(1 for f in graph if f.startswith(prefix))
        for prefix in ("src/shared/", "src/fundamental/", "src/orchestration/")
    }
    empty = [p for p, n in per_prefix.items() if n == 0]
    assert not empty, (
        f"these prefixes match no files, so every rule scoped to them now passes "
        f"vacuously: {empty}. If a domain was absorbed, add its repo to "
        f"architecture._SIBLING_REPOS (or ARCHITECTURE_SRC_ROOTS). See DX-3."
    )


def test_no_domain_exists_in_two_trees(graph):
    """QR-22 — exactly one owner per domain; scan() raises otherwise.

    Two copies mean imports resolve to whichever root sits first on sys.path,
    silently, and the two drift apart from there.
    """
    assert graph, "the import graph is empty — no root resolved"
