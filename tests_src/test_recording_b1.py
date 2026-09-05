"""B1 — the clock-bearing stores. AC-11.15, DN-19/20/21, RC-31/32, BS-7.

Tier: unit + data-contract (constitution §4).

★ WHY THESE EXIST BEFORE ANYTHING CONSUMES THEM
-----------------------------------------------
L3 **BS-1**: their value is a function of *elapsed* time, not of build effort,
and it is the only quantity in this project that cannot be bought back later.
A thesis that closed unscored is evidence destroyed; a vetoed name whose outcome
went unrecorded is a counterfactual that cannot be reconstructed.

⚠ Two of the three arms cannot run end-to-end until D-01 and D-12 exist. What is
testable NOW is that the stores accept the right shapes, refuse revision, and
mark both arms on one basis — **BS-3b**: the journal is the clock that starts
today, because `CT-11.6` allows `thesis_version: null`.
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from src.recording.counterfactual import CounterfactualStore, VetoedCandidate
from src.recording.errors import AppendOnlyViolation, OutcomeBasisMismatch
from src.recording.journal import JournalEntry, JournalStore
from src.recording.outcomes import Basis, mark_to_market


@pytest.fixture
def journal(tmp_path):
    return JournalStore(tmp_path / "journal.jsonl")


@pytest.fixture
def counterfactual(tmp_path):
    return CounterfactualStore(tmp_path / "vetoed.jsonl")


def entry(**over):
    kw = dict(date=date(2026, 8, 23), ticker="MU", action="BUY",
              rationale="cycle trough passed; HBM share gain not yet priced",
              thesis_version=None, overridden_flags=(), author="victor")
    kw.update(over)
    return JournalEntry(**kw)


def candidate(**over):
    kw = dict(ticker="MU", as_of=date(2026, 8, 23), ranked_quantity=1.84,
              horizon="1m", binding_gates=("thesis",), reason="verdict HOLD",
              decision_anchor="open")
    kw.update(over)
    return VetoedCandidate(**kw)


# --------------------------------------------------------------------------- #
# The journal — AC-11.15, RC-24, INV-006
# --------------------------------------------------------------------------- #

def test_a_decision_can_be_journalled_today(journal):
    """★ BS-3b — the clock that starts NOW.

    `thesis_version: null` is legal, so a decision is recordable before D-01
    exists, and these entries become RA-59's calibration sample later.
    """
    journal.append(entry(thesis_version=None))
    got = journal.read()
    assert len(got) == 1 and got[0].thesis_version is None
    assert got[0].ordinal == 0


def test_ordinals_are_assigned_and_dense(journal):
    """CT-11.6 keys on `(date, ordinal)` — the store assigns it, not the caller."""
    for _ in range(3):
        journal.append(entry())
    assert [e.ordinal for e in journal.read()] == [0, 1, 2]


def test_editing_an_existing_entry_raises(journal):
    """AC-11.15 — INV-006. A rationale edited after the outcome is known is
    worthless as evidence, which is the entire reason the journal exists."""
    journal.append(entry())
    with pytest.raises(AppendOnlyViolation) as e:
        journal.revise(0, rationale="actually I always thought it was risky")
    assert "append-only" in str(e.value).lower()


def test_the_entry_itself_is_immutable(journal):
    """RC-24 — defence in depth: the store refuses, and so does the value."""
    e = entry()
    with pytest.raises(Exception):
        e.rationale = "rewritten"


def test_rationale_may_not_be_empty(journal):
    """★ An entry with no reason is a timestamp pretending to be evidence.

    RA-59 will score these; a blank rationale contributes a row to the
    calibration sample that can never be learned from.
    """
    with pytest.raises(ValueError):
        journal.append(entry(rationale="   "))


def test_an_override_records_which_flags_were_overridden(journal):
    """RC-34 — the system never prevents an override; it records that it happened."""
    journal.append(entry(overridden_flags=("M-3 pyramiding", "thesis VETO")))
    assert journal.read()[0].overridden_flags == ("M-3 pyramiding", "thesis VETO")


def test_the_store_survives_a_reopen(tmp_path):
    """INV-006 — append-only means durable, not in-memory."""
    path = tmp_path / "j.jsonl"
    JournalStore(path).append(entry())
    reopened = JournalStore(path)
    reopened.append(entry(ticker="NVDA"))
    assert [e.ticker for e in reopened.read()] == ["MU", "NVDA"]
    assert [e.ordinal for e in reopened.read()] == [0, 1]


def test_a_corrupt_line_raises_rather_than_being_skipped(tmp_path):
    """P5 — a silently skipped row makes the sample quietly incomplete."""
    path = tmp_path / "j.jsonl"
    JournalStore(path).append(entry())
    path.write_text(path.read_text() + "{not json}\n", encoding="utf-8")
    with pytest.raises(Exception):
        JournalStore(path).read()


# --------------------------------------------------------------------------- #
# The counterfactual store — DN-19/20/21, RC-31, BS-7
# --------------------------------------------------------------------------- #

def test_a_vetoed_candidate_is_recorded_with_its_binding_gates(counterfactual):
    """DN-19 — ticker, as_of, the binding gate(s) and the ranked quantity it carried."""
    counterfactual.append(candidate())
    got = counterfactual.read()[0]
    assert (got.ticker, got.binding_gates, got.ranked_quantity) == ("MU", ("thesis",), 1.84)
    assert got.outcome_h is None                # pending until marked


def test_the_counterfactual_record_is_write_once(counterfactual):
    """★ DN-21, BS-7 — a rejected-name history that can be edited is the most
    tempting record in the system to edit."""
    counterfactual.append(candidate())
    with pytest.raises(AppendOnlyViolation):
        counterfactual.revise("MU", date(2026, 8, 23), reason="changed my mind")


def test_recording_the_same_candidate_twice_raises(counterfactual):
    """DN-21 — write-once keys on (ticker, as_of); a second write is a revision."""
    counterfactual.append(candidate())
    with pytest.raises(AppendOnlyViolation):
        counterfactual.append(candidate())


def test_a_candidate_must_name_at_least_one_binding_gate(counterfactual):
    """DN-19 — a veto with no binding gate is an exclusion nobody can attribute."""
    with pytest.raises(ValueError):
        counterfactual.append(candidate(binding_gates=()))


def test_marking_an_outcome_appends_rather_than_mutating(counterfactual):
    """DN-21 — the outcome arrives later and must not rewrite the original row."""
    counterfactual.append(candidate())
    counterfactual.record_outcome("MU", date(2026, 8, 23), realised_return=-0.031)
    rows = counterfactual.read()
    assert len(rows) == 1                       # read() folds the outcome in
    assert rows[0].outcome_h == pytest.approx(-0.031)
    assert counterfactual.raw_line_count() == 2  # ★ but the file has both events


# --------------------------------------------------------------------------- #
# Outcome marking — DN-20 / RC-32, the rule that makes the two arms comparable
# --------------------------------------------------------------------------- #

def test_both_arms_are_marked_on_the_same_horizon_and_anchor():
    """★★ DN-20 / RC-32 — or the two arms are not comparable and the gate's
    effect stays unfalsifiable, which is the whole point of recording it."""
    basis = Basis(horizon="1m", anchor="open")
    acted = mark_to_market(entry_px=100.0, exit_px=104.0, basis=basis)
    vetoed = mark_to_market(entry_px=100.0, exit_px=96.9, basis=basis)
    assert acted == pytest.approx(0.04)
    assert vetoed == pytest.approx(-0.031)


def test_marking_two_arms_on_different_bases_raises():
    """★ DN-20 — the failure this rule exists to prevent, made loud.

    A vetoed name marked at 1w against an acted-on name at 1m produces a
    difference that is mostly horizon, and it would look like gate skill.
    """
    a, b = Basis(horizon="1m", anchor="open"), Basis(horizon="1w", anchor="open")
    with pytest.raises(OutcomeBasisMismatch) as e:
        Basis.assert_comparable(a, b)
    assert "horizon" in str(e.value)


def test_a_different_anchor_is_also_incomparable():
    """QA-71 — open-anchored and close-anchored returns are different quantities."""
    a, b = Basis(horizon="1m", anchor="open"), Basis(horizon="1m", anchor="close")
    with pytest.raises(OutcomeBasisMismatch):
        Basis.assert_comparable(a, b)


def test_a_zero_entry_price_raises_rather_than_returning_infinity():
    """P5 — a division that cannot be performed is a failure, not an infinity."""
    with pytest.raises(ValueError):
        mark_to_market(entry_px=0.0, exit_px=10.0, basis=Basis("1m", "open"))


# --------------------------------------------------------------------------- #
# Boundary — AC-11.18 / RC-22 / ST-9
# --------------------------------------------------------------------------- #

def test_recording_imports_neither_reporting_nor_an_analytical_domain():
    """AC-11.18 — enforced tree-wide by test_architecture; asserted here too.

    A renderer upstream of the book can rewrite history to match what it printed.
    """
    from pathlib import Path

    from tests_src.architecture import imports_of

    root = Path(__file__).resolve().parents[1] / "src" / "recording"
    forbidden = ("src.reporting", "src.fundamental", "src.quant", "src.models",
                 "src.risk", "src.decision")
    for py in root.rglob("*.py"):
        for mod in imports_of(py.read_text(encoding="utf-8"), str(py)):
            assert not mod.startswith(forbidden), f"{py.name} imports {mod}"


def test_stored_json_is_readable_without_the_code(tmp_path):
    """★ P6-adjacent — a record that needs this codebase to be read is a record
    that dies with it. The journal is plain JSONL."""
    path = tmp_path / "j.jsonl"
    JournalStore(path).append(entry())
    line = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert line["ticker"] == "MU" and line["date"] == "2026-08-23"
