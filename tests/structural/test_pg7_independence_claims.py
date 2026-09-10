"""`PG-7.3` at the SECOND enforcement point — rendering (D-09).

⚠⚠ **`F6a` `D3` deliberately puts the rule in two places, and says why.**

> *"the rule is enforced **where the claim is constructed** (D-12 composition)
> and **checked again** where it is rendered (D-09). … A single guard at
> composition would be correct and would still let a *report template* phrase
> concurrence into existence."*

★ Composition stops the claim entering the DATA (`src/decision/concurrence.py`).
This file stops it entering the PROSE — because `PG-7.3` is about **what the
reader is told**, and a template can assert agreement without ever consulting a
boolean.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
RENDERERS = (REPO / "src/reporting",)

#: ⚠ Phrases that assert INDEPENDENT CONCURRENCE — the exact claim `PG-7.3`
#: forbids when a seat was cross-configured.
#: ★ Deliberately narrow: it is not an English-language filter. Each pattern is
#: the shape of the specific false claim, not a word that happens to appear.
CLAIM_PATTERNS = (
    re.compile(r"independent(ly)?\s+(views?|analyses|agree)", re.I),
    re.compile(r"two\s+independent", re.I),
    re.compile(r"(views?|seats?|analyses)\s+agree", re.I),
    re.compile(r"independent\s+confirmation", re.I),
)


def _sources():
    for root in RENDERERS:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            yield path, path.read_text(encoding="utf-8")


def test_ac_6a_10_no_renderer_asserts_independent_agreement_in_prose():
    """⚠⚠ A template may not phrase concurrence into existence (`D3`).

    ★ If a renderer ever needs to say two views agree, it must first consult
    `Recommendation.concurrence` — and at that point the honest sentence is
    available to it. The point of this test is that the claim cannot be made
    **without** consulting it.
    """
    offenders = []
    for path, source in _sources():
        for pattern in CLAIM_PATTERNS:
            for match in pattern.finditer(source):
                line = source[:match.start()].count("\n") + 1
                offenders.append(f"{path.relative_to(REPO)}:{line}: {match.group(0)!r}")
    assert not offenders, (
        "a renderer asserts that independent views agree. ⚠ PG-7.3 forbids that "
        "claim whenever one seat configured another, and cross-configuration is "
        "recorded per-run — so a STATIC assertion is wrong in exactly the runs "
        "that matter (AC-6a.10, F6a D3):\n  " + "\n  ".join(offenders)
    )


def test_ac_6a_10_the_concurrence_status_is_serialised_with_the_verdict():
    """★★ `PG-10`'s shape — the status travels **in the field**.

    ⚠ `F2` `D3` renamed `IDENTICAL` → `REPRODUCED` because *"the name is what
    gets copied"*. A concurrence status that never reaches the stored JSON
    cannot travel with the verdict into a report, and the guard becomes
    decoration.
    """
    from src.decision.contracts.recommendation import Recommendation
    fields = Recommendation.__dataclass_fields__
    assert "concurrence" in fields, "CT-12.1 must carry the PG-7.3 status"
    assert fields["concurrence"].default == "independent"


def test_ac_6a_10_the_guard_is_not_importable_from_the_harness_side():
    """⚠⚠ `ST-2` / `AC-5.12` — nothing imports the harness.

    ★ Found while building this: defining `PG-7.3`'s guard in
    `src/evaluation/metrics/influence.py` would have forced `src/decision/` to
    import the harness, which `AC-5.12` fails the build over. The guard lives
    with the code that CONSTRUCTS the claim (`F6a` `D3` names composition), and
    the harness imports **it**.
    """
    import src.decision.concurrence as guard
    source = pathlib.Path(guard.__file__).read_text(encoding="utf-8")
    assert "src.evaluation" not in source, (
        "D-12 must not import the evaluation harness (ST-2, AC-5.12)")
