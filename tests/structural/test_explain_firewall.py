"""F4 `AC-4.2` / `AC-4.7` — the analyst firewall at seat 6."""

from __future__ import annotations

import pytest

from tools.check_import_fences import (
    all_violations,
    firewall_violations,
    gate_binding_violations,
)


def test_ac_4_2_the_real_tree_respects_the_firewall():
    assert firewall_violations() == []


def test_ac_4_7_gate_binding_is_not_rebuilt_here():
    assert gate_binding_violations() == []


def _tree(tmp_path, files):
    src = tmp_path / "src"
    for rel, body in files.items():
        p = src / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return src


@pytest.mark.parametrize("bad_import", [
    "from src.fundamental.scorecard.coverage import assess_confidence",
    "from src.quant.metrics.ic import information_coefficient",
    "import src.fundamental.prompts.call",
])
def test_ac_4_2_reaching_into_a_walled_domain_is_caught(tmp_path, bad_import):
    """⚠⚠ INV-014/ST-9 — the firewall's value is that agreement between the two
    analysts is INDEPENDENT. A path through seat 6 makes it an echo."""
    src = _tree(tmp_path, {"explain/service.py": bad_import + "\n"})
    hits = firewall_violations(src)
    assert len(hits) == 1 and "INV-014" in hits[0]


@pytest.mark.parametrize("ok_import", [
    "from src.fundamental.contracts.analysis_run import AnalysisRun",
    "from src.quant.models import Nomination",
    "from src.decision.attribute.binding import gate_binding",
])
def test_ac_4_2_published_contracts_are_permitted(tmp_path, ok_import):
    """★ Seat 6 reads PUBLISHED surface — that is how it composes at all."""
    src = _tree(tmp_path, {"explain/service.py": ok_import + "\n"})
    assert firewall_violations(src) == []


def test_ac_4_7_a_local_gate_binding_implementation_is_caught(tmp_path):
    """P4 — decision/attribute/binding.py already answers this; a second
    implementation is a second answer."""
    src = _tree(tmp_path, {"explain/oops.py": "def bind_gates(x):\n    return x\n"})
    hits = gate_binding_violations(src)
    assert len(hits) == 1 and "AC-4.7" in hits[0]


def test_ac_4_2_a_docstring_naming_a_domain_is_not_an_import(tmp_path):
    """★ Why AST and not grep."""
    src = _tree(tmp_path, {
        "explain/notes.py": '"""We must not import src.fundamental internals."""\n'})
    assert all_violations(src) == []


def test_ac_4_2_other_domains_are_unaffected(tmp_path):
    """The fence guards src/explain/**, not the whole tree."""
    src = _tree(tmp_path, {
        "reporting/render.py": "from src.fundamental.scorecard.coverage import x\n"})
    assert all_violations(src) == []
