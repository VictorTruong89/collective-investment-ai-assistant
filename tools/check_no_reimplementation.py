#!/usr/bin/env python3
"""`F9` `AC-9.2` — ★ the relay is WRAPPED, never rebuilt (`P4`).

    python3 tools/check_no_reimplementation.py

⚠⚠ **Why a structural check and not a code review.** `src/fundamental/relay/`
already composes the prompt, validates the schema, **re-verifies every claim
against the pipeline's own data**, and applies `RA-67`'s coverage de-rating.
F9's job is to put a port shape around it. ★ The failure this guards is not
someone deciding to rewrite the relay — it is a wrapper growing *one* convenience
that happens to duplicate a rule, and the duplicate then disagreeing.

★★ **`AC-1.77` is why this one matters more than a normal `P4` check**: the
relay's whole safety case rests on the de-rating firing *unchanged*. A second
copy of a floor in the adapter layer is `FE-4`'s defect — the one `RA-137` had
just finished removing from the wordlist — and it would fire *instead of*, not
beside, the real one.

⚠ This asks *"is the logic defined here?"*, never *"is it correct?"*. Meaning
stays a human's job (the same limit `tools/check_id_families.py` states).
"""

from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

#: The layer that must stay a wrapper.
WRAPPER_ROOT = "src/fundamental/source"

#: ⚠ The three kinds of logic `AC-9.2` names, as the shapes they take in code.
#: ★ Each entry is a FUNCTION NAME the wrapper would have to define in order to
#: own that logic. Calling one is fine — that is what wrapping means.
FORBIDDEN_DEFINITIONS = {
    "prompt composition": (
        "compose_prompt", "build_prompt", "render_prompt", "_prompt_text",
        "compose_envelope", "build_envelope",
    ),
    "claim verification": (
        "verify_claim", "verify_claims", "_verify", "recheck_claim",
        "reverify", "validate_against_data", "contradicts",
    ),
    "confidence logic": (
        "assess_confidence", "_assess_confidence", "derate", "de_rate",
        "apply_floor", "confidence_of", "_confidence",
    ),
}

#: ⚠⚠ A NUMBER is how a duplicated floor actually arrives — not a function.
#: ★ `CONFIDENCE_FLOOR` and `CONFIDENCE_HOLD_CAP` live in
#: `src/fundamental/scorecard/coverage.py`. A literal copy in the wrapper is the
#: `FE-4` defect in its most compact form.
FORBIDDEN_CONSTANTS = ("CONFIDENCE_FLOOR", "CONFIDENCE_HOLD_CAP",
                       "HOLD_CAP", "COVERAGE_FLOOR")


def _py(root: pathlib.Path):
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def reimplementation_violations(root: pathlib.Path | None = None) -> list[str]:
    """Every place the wrapper DEFINES logic it is supposed to delegate."""
    root = root or REPO / WRAPPER_ROOT
    if not root.is_dir():
        return []
    out = []
    for path in _py(root):
        rel = path.relative_to(root.parent.parent.parent).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        except SyntaxError as exc:                       # pragma: no cover
            out.append(f"{rel}: does not parse — {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for kind, names in FORBIDDEN_DEFINITIONS.items():
                    if node.name in names:
                        out.append(
                            f"{rel}:{node.lineno}: defines {node.name}() — ⚠ "
                            f"AC-9.2: {kind} belongs to src/fundamental/relay/, "
                            "and this layer WRAPS it. A second implementation is "
                            "a second answer to a question that already has one "
                            "(P4).")
            # ⚠ A field or parameter NAMED assess_confidence is fine — that is
            # the injected dependency. Only a `def` or an assignment of a
            # threshold VALUE is ownership.
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in FORBIDDEN_CONSTANTS:
                        out.append(
                            f"{rel}:{node.lineno}: assigns {target.id} — ⚠⚠ "
                            "AC-9.2 / AC-1.77: the confidence floors live in "
                            "src/fundamental/scorecard/coverage.py. A copy here "
                            "fires INSTEAD of the real one and the relay's "
                            "safety case rests on it firing unchanged.")
    return out


def main() -> int:
    bad = reimplementation_violations()
    if bad:
        print("⛔ AC-9.2 — the thesis-source layer reimplements the relay:",
              file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-9.2 — src/fundamental/source/ wraps the relay, reimplements none of it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
