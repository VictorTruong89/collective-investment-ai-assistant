"""Rule checks — properties every recorded call must satisfy, whatever it answers.

`L8` §9 rule 4ⓑ (Victor, 2026-10-01): judgement quality moves from golden cases
to falsifiers and rule checks. Each rule here is tested on a synthetic recording
in BOTH directions: it fires on a violation and stays quiet on a clean call.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tools import rule_checks as rc

FILING = ("Revenue for the quarter was $9,301 million.\n"
          "Data center and networking\n55% | 30%\n"
          "In the past five years, NAND prices have ranged from plus low-30% to a minus low-50% range.\n")


def _run(tmp_path: pathlib.Path, call_id: str, answer, *, stop="tool_use",
         payload="P") -> pathlib.Path:
    """Write one recording in the promoted layout: `<run>/trace/payloads/<call>.json`."""
    run = tmp_path / "run-2026-10-01T000000-mu-x"
    (run / "trace/payloads").mkdir(parents=True, exist_ok=True)
    fixture = tmp_path / "FILING.txt"
    fixture.write_text(FILING, encoding="utf-8")
    (run / "filing.json").write_text(json.dumps({"fixture": str(fixture), "ticker": "MU"}))
    text = answer if isinstance(answer, str) else json.dumps(answer)
    (run / f"trace/payloads/{call_id}.json").write_text(json.dumps({
        "request": {"model": "m", "payload": payload},
        "response": {"text": text, "stop_reason": stop}}))
    return tmp_path


def _rules(root):
    return sorted({v.rule for v in rc.check_root(root)})


# ── leaked tool syntax (DX-134) ─────────────────────────────────────────────

def test_leaked_tool_syntax_fires_on_a_parameter_tag(tmp_path):
    root = _run(tmp_path, "judge:C:J-11:llm:1",
                {"strongest_reason": '\n<parameter name="reason">The income statement…'})
    assert rc.LEAKED_TOOL_SYNTAX in _rules(root)


def test_leaked_tool_syntax_quiet_on_prose_about_tags(tmp_path):
    root = _run(tmp_path, "judge:J-01:llm:1", {"why": "parameters were in range"})
    assert rc.LEAKED_TOOL_SYNTAX not in _rules(root)


# ── incomplete call ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("answer,stop", [("{}", "max_tokens"), ("", "tool_use")])
def test_incomplete_call_fires_on_truncation_or_empty(tmp_path, answer, stop):
    """`DX-133` — a 2-character `{}` truncation PARSES; the stop reason says what it is."""
    root = _run(tmp_path, "judge:J-14:llm:1", answer, stop=stop)
    assert rc.INCOMPLETE_CALL in _rules(root)


# ── a quote attributed to the filing must be in the filing ─────────────────

def test_quote_rule_fires_on_a_changed_number(tmp_path):
    """The measured case: `J-03` quoted NAND as 'plus low-50%' — the filing says low-30%."""
    root = _run(tmp_path, "judge:J-03:llm:1", {"why": (
        'FACT [Risk Factors] — "In the past five years, NAND prices have ranged '
        'from plus low-50% to a minus low-50% range."')})
    assert rc.QUOTE_NOT_IN_SOURCE in _rules(root)


def test_quote_rule_accepts_table_rows_joined_and_abridged_quotes(tmp_path):
    """Layout is not content: a table row the filing splits across lines, and a
    `...` abridgement whose pieces are each verbatim, both resolve."""
    root = _run(tmp_path, "judge:J-07:llm:1", {"why": (
        'FACT [10Q-NOTE-CONC] — "Data center and networking | 55% | 30%". '
        'FACT [MD&A] — "Revenue for the quarter ... $9,301 million."')})
    assert rc.QUOTE_NOT_IN_SOURCE not in _rules(root)


def test_quote_rule_skips_sources_that_are_not_the_filing(tmp_path):
    """A computed D-02 figure or a frozen earlier answer is not filing text."""
    root = _run(tmp_path, "judge:B:J-09:llm:1", {"answer": (
        'FACT [D-02 `implied`]: "solves_for stage1_growth at 0.2826 exactly". '
        'FACT [J-08 frozen]: "insufficient_evidence for the supply read".')})
    assert rc.QUOTE_NOT_IN_SOURCE not in _rules(root)


# ── a declared-absent input must be refused, not invented ──────────────────

def test_absent_consensus_must_be_refused(tmp_path):
    root = _run(tmp_path, "judge:B:J-09:llm:1",
                {"consensus_position": "Consensus expects $8.50 EPS and a Buy rating."})
    assert rc.ABSENT_INPUT_NOT_REFUSED in _rules(root)


def test_absent_consensus_refusal_passes(tmp_path):
    root = _run(tmp_path, "judge:B:J-09:llm:1",
                {"consensus_position": "INSUFFICIENT_EVIDENCE — needed: the consensus set"})
    assert rc.ABSENT_INPUT_NOT_REFUSED not in _rules(root)


@pytest.mark.parametrize("claim", [
    {"claim": "x", "base_rate_in_bundle": False,
     "base_rate": "About 70% of memory upcycles last under three years."},   # invented
    {"claim": "y", "base_rate_in_bundle": True,
     "base_rate": "Memory upcycles usually last two years."},                # cites nothing
    {"claim": "z", "base_rate": "Absent."},                                  # flag missing
])
def test_an_invented_base_rate_fires(tmp_path, claim):
    root = _run(tmp_path, "judge:B:J-10:llm:1", {"claims": [claim]})
    assert rc.ABSENT_INPUT_NOT_REFUSED in _rules(root)


def test_the_recorded_j10_shape_passes(tmp_path):
    """The measured answer: the cross-company rate declared absent, and the
    company's own history used as a base rate, cited — both legitimate."""
    root = _run(tmp_path, "judge:B:J-10:llm:1", {"claims": [
        {"claim": "x", "base_rate_in_bundle": False,
         "base_rate": 'Absent. FACT [declared absent inputs]: "reference_class_base_rates: none"'},
        {"claim": "y", "base_rate_in_bundle": True,
         "base_rate": "FACT [annual history, metric `fcff`]: negative in four of nine years"}]})
    assert rc.ABSENT_INPUT_NOT_REFUSED not in _rules(root)


def test_a_supplied_input_lifts_the_refusal_rule(tmp_path):
    """When a run's bundle stops declaring consensus absent, the rule must not
    demand a refusal — item 5 adds that source, and the rule follows."""
    root = _run(tmp_path, "judge:B:J-09:llm:1",
                {"consensus_position": "Consensus expects $8.50 EPS."},
                payload=("EVIDENCE …\nDECLARED ABSENT INPUTS — stage_b_to_d_inputs\n"
                         "- reference_class_base_rates: no dataset\n\nINSTRUCTIONS"))
    assert rc.ABSENT_INPUT_NOT_REFUSED not in _rules(root)


@pytest.mark.parametrize("tag", ["FCFF MARGIN REACH", "POSITIVE-FCFF RUNS", "REVENUE CAGR REACH",
                                 "REFERENCE-CLASS", "PUBLISHED", "CONSENSUS", "PRICE TARGETS"])
def test_quote_rule_exempts_the_computed_bundle_sections(tmp_path, tag):
    """✏ 2026-10-03 — `F11` base rates and the consensus section are COMPUTED parts, not the
    filing; `J-11` quoting "≥ 40.1 %: all 0/21" was flagged until these were listed."""
    root = _run(tmp_path, "judge:J-11:llm:1", {"why": (
        f'FACT [{tag}] — "≥ 40.1 %: all 0/21 (0.0 %) in the class"')})
    assert rc.QUOTE_NOT_IN_SOURCE not in _rules(root)
