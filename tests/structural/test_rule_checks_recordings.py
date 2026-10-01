"""Rule checks over every promoted recording — `L8` §9 rule 4ⓑ.

★ Asserts the checker finds EXACTLY `tools.rule_checks.KNOWN`. A new violation
fails here with its detail; a fixed one fails too, until it is removed from
`KNOWN` — so the list of known violations can never drift from the recordings.
"""

from __future__ import annotations

from tools import rule_checks as rc


def test_the_rule_checks_ran_over_real_recordings():
    assert sum(1 for _ in rc.RECORDINGS.glob("*/trace/payloads/*.json")) >= 40


def test_every_rule_violation_in_the_recordings_is_known_and_explained():
    found = {(v.run, v.call, v.rule): v.detail for v in rc.check_root()}
    new = {k: d for k, d in found.items() if k not in rc.KNOWN}
    fixed = sorted(k for k in rc.KNOWN if k not in found)
    assert not new, "NEW rule violations:\n" + "\n".join(f"  {k}: {d}" for k, d in new.items())
    assert not fixed, f"no longer violated — remove from KNOWN: {fixed}"
