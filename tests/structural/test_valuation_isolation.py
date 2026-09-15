"""`F10` structural ACs — isolation (`AC-F10.14`) and the vendor-DCF rule (`AC-F10.16`)."""

from __future__ import annotations

import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
VALUATION = REPO / "src/feature_engineer/valuation"


def _imports(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def test_ac_f10_14_valuation_imports_no_analyst_domain_no_llm_no_vendor_sdk():
    """AC-F10.14 — `ST-5`, `FE-21`, `A2`. ★ AST, not grep: a comment cannot pass it."""
    files = sorted(VALUATION.glob("*.py"))
    assert len(files) >= 6, "the check would be vacuous"
    forbidden = ("src.fundamental", "src.quant", "src.models", "src.risk", "src.portfolio",
                 "src.shared.llm", "anthropic", "openai", "requests", "httpx",
                 "src.data_engine.src")
    for f in files:
        bad = sorted(i for i in _imports(f) if i.startswith(forbidden))
        assert not bad, f"{f.name} imports {bad}"


def test_ac_f10_14_no_feature_spec_lists_a_valuation_output_as_an_input():
    """AC-F10.14 — `QF-1` stays closed: no valuation value enters the panel."""
    sets = REPO / "src/feature_engineer/contracts/sets"
    text = "\n".join(p.read_text(encoding="utf-8") for p in sets.glob("*.py"))
    for name in ("value_per_share", "fv_model", "fv_analyst", "enterprise_value", "valuation."):
        assert name not in text, f"a feature contract references {name}"


def test_ac_f10_16_a_vendor_dcf_is_never_read_as_fv_model():
    """AC-F10.16 — FMP's DCF is a cross-check at most (`fmp-api`). ★ The service
    reads fundamentals and prices only; no observation field set, no vendor DCF."""
    src = "\n".join(p.read_text(encoding="utf-8") for p in VALUATION.glob("*.py"))
    for needle in ("get_observation", "discounted-cash-flow", "dcf_value", "dcfValue",
                   "advanced_dcf"):
        assert needle not in src, f"valuation/ reads {needle}"
