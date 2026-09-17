"""`F10` `D5` — the runner's `J-20` answer shape and its caller."""

from __future__ import annotations

import json

from src.fundamental.prompts.e_blocks import BLOCKS, J20_METHODS


def _bundle_with(text: str):
    from datetime import date

    from src.fundamental.bundle.models import BundlePart, EvidenceBundle
    return EvidenceBundle(ticker="MU", as_of=date(2025, 6, 26),
                          parts=(BundlePart("filing", {"accession_id": "acc"}, text),))


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


def test_j20_is_blind_and_is_LAST_in_the_stage_a_order():
    """✏ 2026-09-14 — added by Victor's decision (L3 §2.1g step 1)."""
    from tools.run_judgement_once import STAGE_A_ORDER, answer_shape
    blk = BLOCKS["J-20"][0]()
    assert blk.view == "blind" and answer_shape(blk) == "normalisation"
    assert STAGE_A_ORDER[-1] == "J-20" and len(STAGE_A_ORDER) == 9


def test_stage_a_without_the_annual_history_is_BLOCKED_before_any_spend(monkeypatch, capsys):
    """⚠ J-20 with no history part can only say `insufficient_evidence` — refused free."""
    import sys

    from tools import run_judgement_once as r
    monkeypatch.setattr(sys, "argv", ["x", "--dry-run", "--stage-a"])
    assert r.main() == 2
    assert "needs --annual-history" in capsys.readouterr().out


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
    bundle = _bundle_with("x")
    line = normalisation_outcome(ok, rows, ticker="MU", as_of=as_of, provenance=prov,
                                 bundle=bundle)
    assert "normalised basis normalised.cycle_average_fcff" in line
    assert ok["_basis"]["origin"] == "judgement"

    loss = {**ok, "last_fiscal_year": 2024, "trough_year": 2023}
    line = normalisation_outcome(loss, rows, ticker="MU", as_of=as_of, provenance=prov,
                                 bundle=bundle)
    assert "normalised basis normalised.cycle_average_fcff" in line, line

    early = {**ok, "first_fiscal_year": 2014, "last_fiscal_year": 2017, "trough_year": 2016,
             "peak_year": 2017}
    line = normalisation_outcome(early, rows, ticker="MU", as_of=as_of, provenance=prov,
                                 bundle=bundle)
    assert "NO normalised basis" in line                  # ⚠ the console line is truncated
    assert early["_basis"]["status"] == "NO_BASIS"
    assert "FY2014" in early["_basis"]["reason"] and "FY2015" in early["_basis"]["reason"]
    json.dumps(ok["_basis"])                              # serialisable into the trace


def test_dx_108_the_runner_CALLER_refuses_a_basis_whose_exclusion_quote_is_not_in_the_bundle():
    """★ `DX-108`(1) through the caller a live call reaches — the REAL J-20 answer's
    first quote, against a bundle that has it and one that does not."""
    import pandas as pd

    from src.data_engine.pit.snapshot import assemble_rows
    from tools.run_judgement_once import normalisation_outcome

    ledger = pd.read_parquet("tests_src/fixtures/edgar/MU_facts_valuation_subset.parquet")
    as_of = pd.Timestamp("2025-06-26").date()
    rows = assemble_rows(ledger, as_of, source="edgar")
    prov = {"prompt_version": "v1", "run_id": "r", "stage_commit_hash": "sha256:a",
            "bundle_hash": "sha256:b"}
    quote = "Patent cross-license agreement gain | \u2014 | \u2014 | \u2014 | 200"
    answer = {"method": "cycle_average_fcff", "first_fiscal_year": 2017, "last_fiscal_year": 2022,
              "trough_year": 2020, "peak_year": 2018, "what_would_change_it": "x", "why": "y",
              "exclusions": [{"item": "gain", "evidence_id": "e", "quote": quote}]}
    ok = normalisation_outcome(dict(answer), rows, ticker="MU", as_of=as_of, provenance=prov,
                               bundle=_bundle_with("table\nPatent cross-license agreement gain |"
                                                   " — | — | — | 200\nmore"))
    assert "normalised basis" in ok and "NO" not in ok
    bad = dict(answer)
    line = normalisation_outcome(bad, rows, ticker="MU", as_of=as_of, provenance=prov,
                                 bundle=_bundle_with("a filing without that line"))
    assert "NO normalised basis" in line and bad["_basis"]["status"] == "NO_BASIS"


def test_dx_111_stage_a_composes_S8_because_it_is_fresh_authoring(monkeypatch):
    """✏ `DX-111` — §4.0: S-8 in fresh authoring. ★ Checked on the prompt the runner SENDS,
    by capturing `build_payload`'s input in a dry run (free, nothing sent)."""
    import sys

    from src.fundamental.prompts.envelope import S7, S8
    from tools import run_judgement_once as r

    seen = []
    real = r.build_payload
    monkeypatch.setattr(r, "build_payload", lambda p, o, b: seen.append(p) or real(p, o, b))
    monkeypatch.setattr(sys, "argv", ["x", "--dry-run", "--block", "J-01"])
    assert r.main() == 0
    assert S8.strip() in seen[0] and S7.strip() in seen[0]
