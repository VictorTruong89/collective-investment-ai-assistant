"""F1 — structural ACs over src/shared/ports/ (AC-F1.10, AC-F1.13)."""

from __future__ import annotations

import ast
import pathlib

import pytest

from src.shared.registry import IncompleteRegistry, Registry

PORTS_DIR = pathlib.Path("src/shared/ports")

TYPING_MODULES = {"typing", "typing_extensions", "collections.abc", "abc", "dataclasses", "enum"}


def _module_files():
    return sorted(PORTS_DIR.glob("*.py"))


def test_ac_f1_10_port_modules_carry_no_implementation():
    """AC-F1.10 — declarations only: no I/O, no vendor import, no executable statement.

    ⚠ A literal binding (__all__, a type alias) is a DECLARATION, not an executable
    statement — the ban is on module-scope calls and side effects.
    """
    assert _module_files(), "src/shared/ports/ must exist and be scannable"
    for path in _module_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # docstring
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = (
                    [a.name for a in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                for n in names:
                    assert n.split(".")[0] in {m.split(".")[0] for m in TYPING_MODULES} or n == "__future__", (
                        f"{path}: non-typing import {n!r}"
                    )
                continue
            if isinstance(node, ast.ClassDef):
                continue
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                assert value is None or isinstance(
                    value, (ast.Constant, ast.Tuple, ast.List, ast.Set, ast.Dict, ast.Name, ast.Subscript, ast.BinOp)
                ), f"{path}: module-scope assignment calls something: {ast.dump(value)[:80]}"
                continue
            pytest.fail(f"{path}: executable statement at module scope: {type(node).__name__}")


def test_ac_f1_13_declaring_a_port_is_requiring_it():
    """AC-F1.13 — a Protocol in ports.__all__ with no variant and no optional marker fails coverage."""
    from src.shared import ports

    empty = Registry()
    required = tuple(p for p in ports.__all__ if p not in ports.OPTIONAL_PORTS)
    if not required:
        pytest.skip("no ports declared yet — the mechanism is proven by the D2 default below")
    with pytest.raises(IncompleteRegistry):
        empty.validate_coverage()


def test_ac_f1_13_default_required_ports_comes_from_all_not_a_second_list():
    """AC-F1.13/D2 — validate_coverage() with no argument reads ports.__all__."""
    from src.shared import ports

    r = Registry()
    report = r.validate_coverage()
    expected = tuple(sorted(p for p in ports.__all__ if p not in ports.OPTIONAL_PORTS))
    assert report.required == expected


def test_ac_f1_13_a_declared_port_with_no_variant_is_caught():
    """AC-F1.13 — simulate adding a Protocol to __all__: coverage must fail."""
    r = Registry()
    with pytest.raises(IncompleteRegistry) as exc:
        r.validate_coverage(required_ports=("newly_declared_port",))
    assert "newly_declared_port" in exc.value.missing
