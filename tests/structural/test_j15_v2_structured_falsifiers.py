"""`J-15 v2` — every falsifier carries its own structured TEST (`L3` §2.1p item 3).

★ `L8` §9 rule 4ⓐ (2026-10-01): judgement quality is measured by falsifiers, and
the only falsifier verdicts this project has ever reached (`DX-128`, MU #1 #2
FIRED) needed a person to translate prose into a test by hand. `J-15 v2` asks the
model to write that test itself, in the grammar `falsifier_check` already
decides, over the observables the system already publishes; the schema enforces
both, and a test that fails validation stops the run before the verdict (RA-16).
"""

from __future__ import annotations

import json
import pathlib
from datetime import date

import pytest

from src.fundamental.errors import UncheckableFalsifierError
from src.fundamental.monitor.falsifier_check import MODES, validate_test

REPO = pathlib.Path(__file__).resolve().parents[2]
MU_TESTS = json.loads((REPO / "config/falsifiers/mu-2025-06-26.json").read_text())
OBS = ("NetCashProvidedByUsedInOperatingActivities", "PaymentsToAcquirePropertyPlantAndEquipment",
       "GrossProfit", "LongTermDebtAndCapitalLeaseObligations", "DebtCurrent",
       "CashAndCashEquivalentsAtCarryingValue")


def _test(**over):
    t = {"window_periods": 4, "clauses": [{"mode": "each", "consecutive": None, "per_period": [
        {"expr": [{"field": "GrossProfit", "sign": 1}], "op": ">", "value": 0}]}]}
    t.update(over)
    return t


# ── the version and the schema ──────────────────────────────────────────────

def test_j15_v2_is_what_the_stage_b_to_d_runner_ships():
    from src.fundamental.prompts.e_blocks import BLOCKS

    factory, _ids, version = BLOCKS["J-15"]
    assert version == "v2" and factory().version == "v2"
    assert "TEST" in factory().text, "v2's one addition: write each condition's test"


def test_the_orchestrated_prose_path_stays_on_v1_on_purpose():
    """⚠ `thesis/run.py` parses falsifiers from PROSE with no schema, so `v2`'s
    "the grammar the answer schema declares" has nothing to point at there. A silent
    move would send v2 text to a path that cannot honour it."""
    from src.fundamental.prompts.blocks.j_blocks import J15

    assert J15.version == "v1"


def test_the_schema_requires_a_test_built_only_from_the_observables():
    from tools.run_thesis_once import thesis_tool

    item = thesis_tool("J-15", observables=OBS)["input_schema"]["properties"]["falsifiers"]["items"]
    assert "test" in item["required"]
    clause = item["properties"]["test"]["properties"]["clauses"]["items"]
    assert clause["properties"]["mode"]["enum"] == list(MODES)
    term = clause["properties"]["per_period"]["items"]["properties"]["expr"]["items"]
    assert term["properties"]["field"]["enum"] == list(OBS), "a test may read only what is published"


# ── the grammar ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("ordinal", ["1", "2", "3", "4"])
def test_the_hand_written_mu_tests_are_valid_in_the_same_grammar(ordinal):
    """★ DX-128's four readings are the reference J-15 v2's output is held to."""
    assert validate_test(MU_TESTS[ordinal], observables=OBS) == []


@pytest.mark.parametrize("bad,why", [
    (_test(clauses=[{"mode": "each", "consecutive": None, "per_period": [
        {"expr": [{"field": "Sentiment", "sign": 1}], "op": ">", "value": 0}]}]), "Sentiment"),
    (_test(clauses=[{"mode": "eventually", "consecutive": None, "per_period": []}]), "mode"),
    (_test(clauses=[{"mode": "consecutive", "consecutive": None, "per_period": [
        {"expr": [{"field": "GrossProfit", "sign": 1}], "op": ">", "value": 0}]}]), "consecutive"),
    (_test(clauses=[{"mode": "sum", "consecutive": None, "per_period": [
        {"expr": [{"field": "GrossProfit", "sign": 1}], "op": ">", "value": 0},
        {"expr": [{"field": "DebtCurrent", "sign": 1}], "op": ">", "value": 0}]}]), "exactly one"),
    (_test(window_periods=0), "window_periods"),
    (_test(clauses=[]), "clause"),
    (_test(clauses=[{"mode": "each", "consecutive": None, "per_period": [
        {"expr": [{"field": "GrossProfit", "sign": 2}], "op": "~", "value": 0}]}]), "op"),
])
def test_an_invalid_test_is_named_not_guessed(bad, why):
    problems = validate_test(bad, observables=OBS)
    assert problems and any(why in p for p in problems), problems


# ── the runner ──────────────────────────────────────────────────────────────

def _answer(test):
    return {"falsifiers": [
        {"condition": "Gross profit falls in each of the next four quarters.",
         "observable_field": "GrossProfit", "deadline": "2026-06-30",
         "materiality": "the cycle has turned", "about_business": True, "test": test},
        {"condition": "OCF minus capex is positive in each of the next four quarters.",
         "observable_field": "NetCashProvidedByUsedInOperatingActivities",
         "deadline": "2026-06-30", "materiality": "cash generation", "about_business": True,
         "test": MU_TESTS["1"] | {"clauses": [c | {"consecutive": None}
                                              for c in MU_TESTS["1"]["clauses"]]}}],
        "answer": "x"}


def test_the_runner_turns_v2_answers_into_a_tests_file_for_its_own_thesis():
    from tools.run_thesis_once import falsifier_tests_from

    out = falsifier_tests_from(_answer(_test()), observables=OBS, run_id="run-z-mu-thesis")
    assert out["_thesis_run_id"] == "run-z-mu-thesis"
    assert {k for k in out if not k.startswith("_")} == {"1", "2"}
    assert out["1"]["source"] == "J-15 v2 (model-authored)"


def test_an_invalid_model_test_stops_the_run_before_the_verdict():
    """RA-16 — a falsifier whose test cannot be decided is not checkable."""
    from tools.run_thesis_once import falsifier_tests_from

    bad = _test(clauses=[{"mode": "each", "consecutive": None, "per_period": [
        {"expr": [{"field": "Sentiment", "sign": 1}], "op": ">", "value": 0}]}])
    with pytest.raises(UncheckableFalsifierError, match="Sentiment"):
        falsifier_tests_from(_answer(bad), observables=OBS, run_id="run-z")


def test_a_model_test_decides_exactly_as_the_hand_written_one_does():
    """The decision path is shared: the same test over the same periods, same status."""
    from src.fundamental.monitor.falsifier_check import evaluate_test
    from tools.run_thesis_once import falsifier_tests_from

    periods = [{"period_end": date(2025, 8, 28 + i), "values": {
        "NetCashProvidedByUsedInOperatingActivities": 5e9,
        "PaymentsToAcquirePropertyPlantAndEquipment": 3e9}} for i in range(1)] * 4
    model = falsifier_tests_from(_answer(_test()), observables=OBS, run_id="r")["2"]
    assert evaluate_test(model, periods) == evaluate_test(MU_TESTS["1"], periods)


# ── the checker finds them by itself ────────────────────────────────────────

def test_check_falsifiers_finds_the_tests_beside_the_thesis(tmp_path):
    from tools.check_falsifiers import tests_for

    thesis = tmp_path / "run-z" / "thesis.json"
    thesis.parent.mkdir()
    thesis.write_text("{}")
    assert tests_for(thesis, explicit=None) == {}
    (thesis.parent / "falsifier_tests.json").write_text(json.dumps({"_thesis_run_id": "run-z"}))
    assert tests_for(thesis, explicit=None) == {"_thesis_run_id": "run-z"}
    hand = tmp_path / "hand.json"
    hand.write_text(json.dumps({"_thesis_run_id": "hand"}))
    assert tests_for(thesis, explicit=str(hand)) == {"_thesis_run_id": "hand"}, "explicit wins"
