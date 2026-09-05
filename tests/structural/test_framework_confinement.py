"""F2 `AC-2.10` — `QR-14` framework confinement is enforced in CI."""

from __future__ import annotations

import pytest

from tools.check_framework_confinement import (
    FRAMEWORKS,
    imports_of,
    violations,
)


def test_ac_2_10_the_real_tree_has_no_framework_outside_graph():
    assert violations() == []


def test_ac_2_10_a_framework_import_elsewhere_is_caught(tmp_path):
    """⚠ BS-5 — a rule needs a case that FAILS it, or it proves nothing."""
    src = tmp_path / "src"
    (src / "reporting").mkdir(parents=True)
    (src / "reporting" / "render.py").write_text("import langgraph\n")
    assert violations(src) == ["src/reporting/render.py imports langgraph"]


def test_ac_2_10_the_permitted_directory_may_import_it(tmp_path):
    src = tmp_path / "src"
    (src / "orchestration" / "graph").mkdir(parents=True)
    (src / "orchestration" / "graph" / "build.py").write_text(
        "from langgraph.graph import StateGraph\n")
    assert violations(src) == []


def test_ac_2_10_a_docstring_mentioning_a_framework_is_not_a_violation(tmp_path):
    """★ Why AST and not grep — L4 §10.1's grep form would fail this file."""
    src = tmp_path / "src"
    (src / "reporting").mkdir(parents=True)
    (src / "reporting" / "notes.py").write_text(
        '"""We considered langgraph and rejected it (QR-14)."""\n')
    assert violations(src) == []


@pytest.mark.parametrize("fw", FRAMEWORKS)
def test_ac_2_10_every_named_framework_is_actually_checked(fw, tmp_path):
    """⚠ Guard against a name sitting in the list but never being matched."""
    src = tmp_path / "src"
    (src / "quant").mkdir(parents=True)
    (src / "quant" / "m.py").write_text(f"import {fw}\n")
    assert violations(src) == [f"src/quant/m.py imports {fw}"]


def test_imports_of_finds_both_import_forms():
    got = imports_of("import a.b\nfrom c.d import e\n", "x.py")
    assert got == {"a.b", "c.d"}
