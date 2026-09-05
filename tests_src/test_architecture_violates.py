"""Every architectural rule FIRES on a deliberately planted violation.

L3 **BS-5**: *"Each check ships with a test that deliberately violates it and
asserts the check fires. A structural rule that cannot fail is worse than none —
it reports safety it never verified."*

This is not a formality. On 2026-08-23 the three blueprint checks added to
`tools/sdd_audit.py` were written, reviewed, and reported ALL CLEAN — while
crashing on a NameError, because the checks were inert on an empty tree and
nothing had made one fire. The bug surfaced the moment a violation was planted.

The violations are synthetic import graphs, not files on disk: planting a real
file would make the *other* suite fail, and a test that breaks its neighbours
gets deleted rather than fixed.

Tier: unit (constitution §4) — each case exercises one checker in isolation.
"""

from __future__ import annotations

import pytest

from tests_src import architecture as arch

#: (rule id, checker, a graph that MUST trip it, what the violation represents)
VIOLATIONS = [
    (
        "ST-1", arch.st_1,
        {"src/quant/rank.py": {"pipeline.ohlcv.features"}},
        "the new tree reaching back into the legacy one — makes pipeline/ undeletable",
    ),
    (
        "ST-2", arch.st_2,
        {"src/models/train.py": {"src.experiments.sweeps"}},
        "P7-exempt research reached by import rather than by a promotion decision",
    ),
    (
        "ST-5", arch.st_5,
        {"src/reporting/card.py": {"src.shared.llm.gateway"}},
        "a renderer calling the model — the gateway is D-01's alone",
    ),
    (
        "ST-9", arch.st_9,
        {"src/recording/book.py": {"src.reporting.render"}},
        "a renderer upstream of the book — LEVEL 1 advice above LEVEL 0 fact",
    ),
    (
        "ST-10", arch.st_10,
        {"src/fundamental/thesis.py": {"src.decision.compose"}},
        "a composed verdict returning to an analyst seat — INV-014 laundered",
    ),
    (
        "OR-3", arch.or_3,
        {"src/risk/exposure.py": {"src.orchestration.schedule"}},
        "a domain becoming schedule-aware, and untestable standalone",
    ),
    (
        "FE-21", arch.fe_21,
        {"src/feature_engineer/quality/moat.py": {"src.fundamental.thesis"}},
        "a D-02 feature taking an analyst's output as an input — INV-014's leak, "
        "and the live shape of it: a deterministic function of an LLM's judgement",
    ),
    (
        "QA-21", arch.qa_21,
        {"src/quant/signals/rank.py": {"src.models.bundle"}},
        "a stateless ranker acquiring fitted parameters by import (QA-28)",
    ),
    (
        "RP-30", arch.rp_30,
        {"src/reporting/render/card.py": {"src.recording.journal"}},
        "a renderer reaching the record it is supposed to only read through D-12",
    ),
    (
        "RA-45", arch.ra_45,
        {"src/fundamental/events/moves.py": {"numpy"}},
        "a fundamental desk computing its own return decomposition — a top-down "
        "call taken by accident (RA-88, RA-91)",
    ),
    (
        "SI-1", arch.si_1,
        {"src/shared/money.py": {"src.portfolio.sizing"}},
        "a shared module that knows about a domain — that domain's file, misfiled",
    ),
    (
        "CA-1", arch.ca_1,
        {"src/risk/models.py": {"anthropic"}},
        "a vendor SDK in the innermost circle",
    ),
    (
        "CA-2", arch.ca_2,
        {"src/quant/service.py": {"requests"}},
        "transport inside a service layer that should have been handed its inputs",
    ),
]


@pytest.mark.parametrize(
    "rule_id,check,bad_graph,meaning",
    VIOLATIONS,
    ids=[v[0] for v in VIOLATIONS],
)
def test_rule_fires_on_a_planted_violation(rule_id, check, bad_graph, meaning):
    """BS-5 — a check that cannot fail reports safety it never verified."""
    hits = check(bad_graph)
    assert hits, (
        f"{rule_id} did NOT fire on a planted violation ({meaning}). "
        f"The rule is unenforced and the green suite is misleading."
    )


@pytest.mark.parametrize(
    "rule_id,check,bad_graph,meaning",
    VIOLATIONS,
    ids=[v[0] for v in VIOLATIONS],
)
def test_rule_is_silent_on_a_clean_graph(rule_id, check, bad_graph, meaning):
    """A checker that fires on everything is as useless as one that never fires."""
    clean = {"src/shared/money.py": {"decimal", "dataclasses"}}
    assert not check(clean), f"{rule_id} fired on a clean graph — false positive"


def test_every_rule_in_RULES_has_a_violation_case():
    """A rule added to RULES without a planted violation silently bypasses BS-5."""
    covered = {v[0] for v in VIOLATIONS}
    declared = {r[0] for r in arch.RULES}
    assert declared <= covered, f"rules with no BS-5 violation test: {declared - covered}"


def test_st5_does_not_false_positive_on_prose():
    """★ The reason this suite parses imports instead of grepping text.

    L4 §10.1 states ST-5 as `grep -rn "llm" src/ | grep -v ...`, which matches
    the string anywhere — including a docstring. A reporting module that merely
    MENTIONS the gateway is not importing it, and failing the build for that
    would train someone to delete the check.
    """
    prose_only = arch.imports_of(
        '"""Renders LLM narrative it did not author (DC-1)."""\nimport json\n'
    )
    assert prose_only == {"json"}
    assert not arch.st_5({"src/reporting/card.py": prose_only})
