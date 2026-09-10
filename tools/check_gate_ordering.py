#!/usr/bin/env python3
"""`F7a` `AC-7a.1` — ★★ `F6b` may not graduate before its measurement exists.

    python3 tools/check_gate_ordering.py

⚠⚠ **This is `PG-5.1` as a build check.** F7a's own header says *"this spec is a
gate: `F6b` (deliberation) may not graduate until **this design exists**. F7a is
therefore written *before* the thing it measures."*

★★★ **Why a check and not a convention.** The gate protects against the most
natural sequence in the world: build the interesting thing, measure it later.
⚠ And `PG-5.1` explains why "later" never arrives on its own — `F6b` is the
capability *most at risk of being theatre*, and a convincing transcript is
available either way. A gate that lives only in a spec header is enforced by
whoever remembers it at the moment they are most motivated to forget.

⚠ Like every structural check here, it asks *"does the gate exist?"*, never
*"is the measurement good?"* — meaning stays a human's job.
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
F7A_SPEC = REPO / "sdd/specs/F7a_deliberation_process_tests/spec.md"
F6B_SPEC = REPO / "sdd/specs/F6b_deliberation/spec.md"

#: `CT-7a.1` — the seven tests that must be DEFINED before `F6b` graduates.
REQUIRED_TESTS = ("T1", "T2", "T3", "T4", "T5", "T6", "T7")

#: `CT-7a.2` — a registered plan, not a bare threshold (`AC-7a.4`).
REQUIRED_PLAN_FIELDS = ("null_hypothesis", "alpha", "power",
                        "detectable_ratio", "min_n_per_arm", "bands")


def gate_violations() -> list[str]:
    """Everything `AC-7a.1` requires to be true before `F6b` may graduate."""
    out = []
    if not F7A_SPEC.exists():
        return [f"{F7A_SPEC.name} does not exist — ⚠ PG-5.1: F6b "
                "may not graduate before the design that measures it."]
    spec = F7A_SPEC.read_text(encoding="utf-8")

    missing = [t for t in REQUIRED_TESTS if f"**{t}**" not in spec]
    if missing:
        out.append(
            f"F7a defines no {', '.join(missing)} — CT-7a.1 requires all seven "
            "Tier-A tests to exist before F6b graduates.")

    absent = [f for f in REQUIRED_PLAN_FIELDS if f not in spec]
    if absent:
        out.append(
            f"the registered KillRule omits {', '.join(absent)} — ⚠ AC-7a.4: "
            "**a rule naming only a bare threshold is rejected**, because the "
            "unstated half is what gets chosen after the data (PG-5.1).")

    # ★★ The plan must be CONSTRUCTIBLE, not merely described. A spec can
    #    describe a rule the code cannot build, and then the gate is prose.
    try:
        sys.path.insert(0, str(REPO))
        from src.evaluation.studies.killrule import KillRule
        rule = KillRule(registered_at="2026-09-01T00:00:00+00:00",
                        expected_revision_rate_true=0.6,
                        registered_by="gate check")
        for field in REQUIRED_PLAN_FIELDS:
            if getattr(rule, field, None) is None:
                out.append(f"KillRule cannot supply {field!r} (AC-7a.4)")
        # ⚠ D1's finding, asserted rather than remembered: the DELETE verdict
        #   must stay visibly more expensive than KEEP, so nobody quietly
        #   widens the band to make the kill cheaper.
        if rule.cost_asymmetry < 3:
            out.append(
                f"the DELETE band now costs only {rule.cost_asymmetry:.1f}x the "
                "KEEP band. ⚠ D1 measured 3-4x; a drop means a band moved, and "
                "*widening the DELETE band to make it cheaper* is a threshold "
                "chosen after seeing the COST (PG-5.1).")
    except Exception as exc:                              # pragma: no cover
        out.append(f"the KillRule cannot be constructed: {exc!r}")

    if F6B_SPEC.exists():
        f6b = F6B_SPEC.read_text(encoding="utf-8")
        if "F7a" not in f6b:
            out.append(
                "F6b's spec does not reference F7a — ⚠ the capability under "
                "measurement must name the gate it passes through, or the "
                "ordering is invisible to its reader.")
    return out


def main() -> int:
    bad = gate_violations()
    if bad:
        print("⛔ AC-7a.1 — F6b's measurement gate is not in place:", file=sys.stderr)
        for b in bad:
            print(f"   {b}", file=sys.stderr)
        return 1
    print("✅ AC-7a.1 — F7a's design gates F6b: T1-T7 defined, KillRule registrable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
