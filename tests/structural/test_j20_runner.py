"""`F10` `D5` — the runner's `J-20` answer shape and its caller."""

from __future__ import annotations

import json

from src.fundamental.prompts.e_blocks import BLOCKS, J20_METHODS


def _tool():
    from tools.run_judgement_once import judgement_tool
    return judgement_tool(BLOCKS["J-20"][0]())


def test_j20_answers_a_METHOD_from_the_closed_set_and_has_NO_field_for_a_figure():
    """★★ `D5`: the block chooses; code calculates. ⚠ A schema with an amount
    field would invite the model to produce the number."""
    props = _tool()["input_schema"]["properties"]
    assert props["method"]["enum"] == list(J20_METHODS)
    for forbidden in ("base_fcff", "amount", "value", "fcff", "normalised_earnings"):
        assert forbidden not in props


def test_j20_is_blind_and_is_not_yet_in_the_stage_a_order():
    from tools.run_judgement_once import STAGE_A_ORDER, answer_shape
    blk = BLOCKS["J-20"][0]()
    assert blk.view == "blind" and answer_shape(blk) == "normalisation"
    assert "J-20" not in STAGE_A_ORDER, "adding it changes --stage-a's cost; a deliberate step"


def test_the_runner_CALLER_turns_an_answer_into_a_basis_or_a_named_refusal(tmp_path):
    """★ `normalisation_outcome` is what a live J-20 call reaches — on the REAL
    Micron fixture. ✏ `DX-104`: a window through the FY2023 loss now RESOLVES (t = 0);
    a window reaching back before Micron's revenue tag refuses and names the years."""
    import pandas as pd

    from src.data_engine.pit.snapshot import assemble_rows
    from tools.run_judgement_once import normalisation_outcome

    ledger = pd.read_parquet("tests_src/fixtures/edgar/MU_facts_valuation_subset.parquet")
    as_of = pd.Timestamp("2026-09-13").date()
    rows = assemble_rows(ledger, as_of, source="edgar")
    prov = {"prompt_version": "v1", "run_id": "r", "stage_commit_hash": "sha256:a",
            "bundle_hash": "sha256:b"}
    base = {"exclusions": [], "what_would_change_it": "x", "why": "y"}

    ok = {**base, "method": "cycle_average_fcff", "first_fiscal_year": 2017,
          "last_fiscal_year": 2022, "trough_year": 2020, "peak_year": 2018}
    line = normalisation_outcome(ok, rows, ticker="MU", as_of=as_of, provenance=prov)
    assert "normalised basis normalised.cycle_average_fcff" in line
    assert ok["_basis"]["origin"] == "judgement"

    loss = {**ok, "last_fiscal_year": 2024, "trough_year": 2023}
    line = normalisation_outcome(loss, rows, ticker="MU", as_of=as_of, provenance=prov)
    assert "normalised basis normalised.cycle_average_fcff" in line, line

    early = {**ok, "first_fiscal_year": 2014, "last_fiscal_year": 2017, "trough_year": 2016,
             "peak_year": 2017}
    line = normalisation_outcome(early, rows, ticker="MU", as_of=as_of, provenance=prov)
    assert "NO normalised basis" in line                  # ⚠ the console line is truncated
    assert early["_basis"]["status"] == "NO_BASIS"
    assert "FY2014" in early["_basis"]["reason"] and "FY2015" in early["_basis"]["reason"]
    json.dumps(ok["_basis"])                              # serialisable into the trace
