"""`F9` `AC-9.2` — ★ the relay is WRAPPED, never rebuilt (`P4`, `AC-1.77`).

⚠⚠ **The spec's traceability row named `tools/check_no_reimplementation.py` and
the file did not exist** (`DX-42`). `F9` §2 puts this first in its non-goals —
*"✗ Re-implementing prompt composition, ingest, verification or de-rating"* —
and nothing checked it.

★★ Why it matters more than a normal `P4` duplication: `AC-1.77` records that
**the relay's whole safety case rests on `RA-67`'s coverage de-rating firing
unchanged.** A second copy of a floor in the wrapper fires *instead of* the real
one, and it looks like nothing at all.
"""

from __future__ import annotations

import pathlib

from tools.check_no_reimplementation import reimplementation_violations

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_ac_9_2_the_wrapper_reimplements_nothing():
    """The live tree. ⚠ No skip, no tolerance list."""
    assert reimplementation_violations() == []


def test_ac_9_2_a_reimplemented_confidence_function_is_caught(tmp_path):
    """⚠ The check must be able to FAIL, or it is decoration."""
    root = tmp_path / "src" / "fundamental" / "source"
    root.mkdir(parents=True)
    (root / "a.py").write_text("def assess_confidence(report):\n    return 1.0\n")
    hits = reimplementation_violations(root)
    assert len(hits) == 1 and "confidence logic" in hits[0]


def test_ac_9_2_a_copied_confidence_FLOOR_is_caught(tmp_path):
    """⚠⚠ `AC-1.77` — the floor is how the duplication actually arrives.

    ★ Not as a function anybody would notice in review, but as a **number**:
    one line, plausible, and it silently replaces the rule the relay's safety
    case depends on. `FE-4`'s defect in its most compact form.
    """
    root = tmp_path / "src" / "fundamental" / "source"
    root.mkdir(parents=True)
    (root / "a.py").write_text("CONFIDENCE_FLOOR = 0.35\n")
    hits = reimplementation_violations(root)
    assert len(hits) == 1 and "AC-1.77" in hits[0]


def test_ac_9_2_a_reimplemented_prompt_builder_is_caught(tmp_path):
    """⚠ `D2` — one prompt, two transports. A prompt built HERE would make the
    two variants incomparable, and `F5`/`F7b` both partition by variant."""
    root = tmp_path / "src" / "fundamental" / "source"
    root.mkdir(parents=True)
    (root / "a.py").write_text("def build_prompt(t):\n    return ''\n")
    hits = reimplementation_violations(root)
    assert len(hits) == 1 and "prompt composition" in hits[0]


def test_ac_9_2_CALLING_the_shared_logic_is_allowed(tmp_path):
    """★★ The distinction the whole check rests on: **calling is wrapping.**

    ⚠ A check that banned the NAME would ban the injection too — and the
    adapters take `assess_confidence` as a constructor parameter, which is
    exactly how `C3` is satisfied. Only a `def` or a threshold assignment is
    ownership.
    """
    root = tmp_path / "src" / "fundamental" / "source"
    root.mkdir(parents=True)
    (root / "a.py").write_text(
        "from src.fundamental.scorecard.coverage import assess_confidence\n"
        "def author(raw, assess_confidence=assess_confidence):\n"
        "    return assess_confidence(raw)\n")
    assert reimplementation_violations(root) == []


def test_ac_9_2_the_real_adapters_take_confidence_as_an_INJECTED_dependency():
    """★ The positive form of the rule, on the live code: the adapter never
    reaches for the floors, it is handed the function."""
    import inspect

    from src.fundamental.source.adapters import _BaseAdapter
    assert "assess_confidence" in inspect.signature(_BaseAdapter).parameters
    source = pathlib.Path(
        inspect.getfile(_BaseAdapter)).read_text(encoding="utf-8")
    assert "CONFIDENCE_FLOOR" not in source
