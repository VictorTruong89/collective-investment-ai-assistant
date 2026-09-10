"""`DX-58` — ⚠⚠ a challenge must CROSS the threshold it claims to cross.

`F6b` `D2`: a challenge is a **declared numeric trigger** — Risk raises it
*because a metric it owns crossed a level it declared in advance*. `AC-6b.2`
requires the disputed field and the expected value to be present, and
`is_material(value, threshold)` gates whether an exchange happens at all.

⛔⛔ **Nothing checked that the CITED figure actually crosses.** In the first
live `F7a` run, **8 of 46** challenges asserted *"X is past my T trigger"* while
X sat on the safe side of T — self-contradictory on their face. A generator
written for a five-book set was worse: **67 of 115**.

★★★ **The 8 broken rows turned out to be the most informative in the run: the
agent held 8 of 8.** Rejecting a self-contradictory challenge is correct
behaviour, so counting those holds as *"failed to revise on a valid challenge"*
understated the valid arm and moved `T1`'s ratio the wrong way — the reported
0.929 was really **1.032**.

⚠ This test exists so a future fixture cannot ship the same defect silently.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
FIXTURE = REPO / "tests_src/fixtures/studies/deliberation_challenges.pending.yaml"

#: ⚠ Metrics whose trigger is a FLOOR — crossing means going BELOW it.
#: ★ Getting this set wrong inverts the check for those metrics, which is why
#:   it is data rather than a sign convention buried in a comparison.
BELOW_IS_CROSSING = frozenset({
    "diversification_ratio", "median_hold_days", "uninvested_cash_pct",
})


def crosses(value, threshold, metric: str) -> bool:
    """Does `value` breach `threshold` in the direction the challenge claims?"""
    if not isinstance(value, (int, float)) or not isinstance(threshold, (int, float)):
        return True                      # ⚠ unfilled template — a different defect
    return value < threshold if metric in BELOW_IS_CROSSING else value > threshold


def _pairs():
    if not FIXTURE.exists():             # pragma: no cover
        pytest.skip("challenge fixture not present")
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))["pairs"]


def test_dx58_the_sign_convention_is_declared_not_inferred():
    """★ A floor and a ceiling breach in opposite directions. ⚠ Inferring it
    from the metric name would silently invert three of the families."""
    assert crosses(0.9, 1.3, "diversification_ratio"), "a floor is crossed from below"
    assert not crosses(1.5, 1.3, "diversification_ratio")
    assert crosses(30.0, 25.0, "single_name_concentration_pct"), "a ceiling from above"
    assert not crosses(20.0, 25.0, "single_name_concentration_pct")


def test_dx58_an_incoherent_challenge_is_LABELLED_never_silent():
    """★★ The rule this file enforces: a challenge either crosses its own
    threshold, **or says out loud that it does not.**

    ⚠⚠ The fixture is the **as-run record** of the 2026-09-10 study. Silently
    correcting the 8 broken rows would make the artifact disagree with the run
    it documents — the same reason `F2` `AC-2.8` makes a trace append-only:
    *a record that can be edited is not evidence.*

    ★ So they are kept, flagged `incoherent_arms`, and excluded from the
    corrected ratio. **A NEW fixture with an unflagged breach still fails.**
    """
    unflagged = []
    for p in _pairs():
        flagged = set(p.get("incoherent_arms") or ())
        if not crosses(p["true_value"], p["threshold"], p["metric"]) \
                and "valid" not in flagged:
            unflagged.append(f"{p['id']} valid: {p['true_value']} vs {p['threshold']}")
        if not crosses(p["false_value"], p["threshold"], p["metric"]) \
                and "false" not in flagged:
            unflagged.append(f"{p['id']} false: {p['false_value']} vs {p['threshold']}")
    assert not unflagged, (
        "a challenge does not cross its own threshold and is NOT labelled — "
        "Risk would never raise it, and an analyst that holds is behaving "
        "correctly, which the study would score as a failure to revise "
        "(DX-58):\n  " + "\n  ".join(unflagged))


def test_dx58_the_as_run_record_still_carries_its_eight_known_breaks():
    """⚠ The evidence must not quietly heal. ★ If this count changes, someone
    edited the record of a completed run."""
    flagged = [p["id"] for p in _pairs() if p.get("incoherent_arms")]
    assert len(flagged) == 8, (
        f"the 2026-09-10 run had 8 incoherent challenges; found {len(flagged)}")


def test_dx58_why_the_FALSE_arm_needs_it_too():
    """★★ The subtler half, stated so it is not lost.

    ⚠ A false figure that also fails to cross is **doubly** broken: the analyst
    can reject it for self-contradiction without ever judging whether the number
    is true. `T1` would then be measuring the same self-consistency check on
    both arms and could not separate them at all.

    ★★★ Measured: the agent held **8 of 8** on the incoherent rows — perfect
    discrimination on self-contradiction, and zero information about truth.
    """
    both = [p["id"] for p in _pairs()
            if set(p.get("incoherent_arms") or ()) == {"valid", "false"}]
    assert not both, (
        f"a pair broken on BOTH arms carries no signal at all: {both}")


def test_dx58_true_and_false_are_never_the_same_value():
    """⚠ A pair whose arms carry an identical figure is one observation
    recorded twice, in two arms. ★ Found in the five-book generator
    (`b3-flag-pyramiding`), where a book with 1 prior add collided with a
    hardcoded false value of 1."""
    same = [p["id"] for p in _pairs() if p["true_value"] == p["false_value"]]
    assert not same, f"arms carry identical figures: {same}"
