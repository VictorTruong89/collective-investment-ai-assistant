"""⚠ SI-1 re-implemented for the ABSORBED `src/shared/` — `L3` `DX-3`.

Upstream's `tests_src/architecture.py` scans `SRC = <upstream repo>/src`. When
`src/shared/` was absorbed here (`QR-22`, 2026-09-04) that directory emptied, so
upstream's `SI-1` began scanning **zero files** and passing unconditionally —
silently. Measured, and caught by planting a violation that upstream did not
report.

★ This file restores enforcement for the code that moved. It does NOT close the
whole gap: no rule currently spans BOTH trees (`L3` §6.3).
"""

from __future__ import annotations

import ast
import pathlib

import pytest

SHARED = pathlib.Path(__file__).resolve().parents[2] / "src" / "shared"

#: Every `src/<domain>/` a shared module must not know about. ⚠ `shared` itself
#: is absent by design — that is the whole rule.
FORBIDDEN_PREFIXES = (
    "src.data_engine", "src.decision", "src.experiments", "src.feature_engineer",
    "src.fundamental", "src.models", "src.orchestration", "src.portfolio",
    "src.quant", "src.recording", "src.reporting", "src.risk", "src.evaluation",
    "src.explain",
)


def imports_of(source: str) -> list[str]:
    """Module names imported by `source`, via AST — not grep.

    ⚠ Grep matches the *string* anywhere, so a docstring mentioning a domain
    would fail the build. The rule is about IMPORTS, so parse imports.
    """
    tree = ast.parse(source)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.append(node.module)
    return found


def violations_in(source: str) -> list[str]:
    return [m for m in imports_of(source) if m.startswith(FORBIDDEN_PREFIXES)]


def _shared_modules():
    return sorted(p for p in SHARED.rglob("*.py") if "__pycache__" not in p.parts)


def test_si_1_shared_imports_no_domain():
    """SI-1 — a shared module that knows about a domain is that domain's module."""
    assert _shared_modules(), "src/shared/ must exist and be scannable"
    offenders = {
        str(p.relative_to(SHARED.parents[1])): violations_in(p.read_text(encoding="utf-8"))
        for p in _shared_modules()
    }
    offenders = {k: v for k, v in offenders.items() if v}
    assert not offenders, f"SI-1 violated: {offenders}"


def test_si_1_scans_a_nonzero_number_of_files():
    """⚠ DX-3 — the guard against the guard.

    SI-1 became vacuous upstream by scanning an empty directory and passing. This
    asserts the rule has something to examine, so the same silent failure cannot
    happen here.
    """
    assert len(_shared_modules()) >= 5, (
        f"SI-1 is scanning only {len(_shared_modules())} files — if src/shared/ moved "
        "again, this rule went vacuous rather than failing. See L3 DX-3."
    )


@pytest.mark.parametrize(
    "snippet,expected",
    [
        ("from src.quant.methods import registry", ["src.quant.methods"]),
        ("import src.orchestration.errors", ["src.orchestration.errors"]),
        ("from src.shared.errors import PipelineError", []),
        ("from decimal import Decimal", []),
        ('"""A docstring mentioning src.quant should NOT trip this."""', []),
    ],
)
def test_si_1_detector_has_power(snippet, expected):
    """⚠ DX-3's lesson — prove the rule CAN fail, and does not fire on the innocent."""
    assert violations_in(snippet) == expected
