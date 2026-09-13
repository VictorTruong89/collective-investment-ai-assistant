"""★★★ `DX-85`ⓒ — the judgement runner's `--extractions` wiring.

⚠⚠ `DX-82`'s lesson, applied from the start: the part kind and its builder are
tested in `tests/unit/test_extraction_bundle_part.py`; THIS file tests the
CALLER — that a recorded E-block run reaches the Stage-A bundle only after
re-verification, and that it actually opens a rubric level in `main()`.
"""

from __future__ import annotations

import json

import pytest

import tools.run_judgement_once as rj
from tools.run_extraction_once import build_bundle

CAPEX = "Expenditures for property, plant, and equipment | (10,199) | (5,266)"


def _record(root, run_id, *, items, status="SUCCESS", block="E-07"):
    """A run directory in the shape `traced_transport` writes."""
    run = root / run_id
    (run / "trace/payloads").mkdir(parents=True)
    ref = f"extract:{block}:llm:1"
    (run / "trace/payloads" / f"{ref}.json").write_text(json.dumps(
        {"request": {}, "response": {"text": json.dumps({"items": items})}}))
    lines = [{"type": "ExternalCall", "run_id": run_id, "step_id": f"extract:{block}",
              "call_id": ref, "prompt_version": "v1", "payload_ref": ref}]
    if status:
        lines.append({"type": "__run_closed__", "status": status})
    (run / "trace.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    return run_id


def _capex(quote=CAPEX, value="(10,199)"):
    return {"evidence_id": "ca.capex", "status": "found", "quote": quote,
            "value": value, "unit": "millions of USD", "period_end": "2025-05-29"}


@pytest.fixture
def roots(tmp_path, monkeypatch):
    monkeypatch.setattr(rj, "RUN_ROOTS", (tmp_path,))
    return tmp_path


def test_a_recorded_run_becomes_a_verified_extraction_part(roots):
    run = _record(roots, "run-x-mu-e07", items=[
        _capex(), {"evidence_id": "ca.buyback", "status": "not_found",
                   "quote": "", "note": "none"}])
    (part,) = rj.load_extraction_parts([run], build_bundle(), ticker="MU")
    assert part.kind == "extraction"
    assert part.pins["evidence_ids"] == ["ca.capex"]
    assert part.pins["source_bundle_hash"] == build_bundle().bundle_hash


def test_a_quote_NOT_in_this_filing_refuses(roots):
    """⚠⚠ The re-verification is what ties a recording to THIS filing (the
    trace does not record the bundle hash, `DX-95`)."""
    run = _record(roots, "run-x-mu-e07",
                  items=[_capex(quote="Capital expenditures were $3,000 million.",
                                value="3,000")])
    with pytest.raises(ValueError, match="not in the bundle"):
        rj.load_extraction_parts([run], build_bundle(), ticker="MU")


def test_a_real_quote_carrying_a_value_it_does_not_state_refuses_at_X01(roots):
    """★ The half only `X-01` catches: the quote IS in the filing, the value
    is not in the quote. Without the re-verification in the loader this
    would open `J-06`'s levels on a fabricated figure."""
    from src.fundamental.errors import ValueNotInSpanError

    run = _record(roots, "run-x-mu-e07", items=[_capex(value="9,999")])
    with pytest.raises(ValueNotInSpanError):
        rj.load_extraction_parts([run], build_bundle(), ticker="MU")


@pytest.mark.parametrize("status", ["FAILED", None])
def test_a_run_that_did_not_close_SUCCESS_refuses(roots, status):
    run = _record(roots, "run-x-mu-e07", items=[_capex()], status=status)
    with pytest.raises(ValueError, match="SUCCESS"):
        rj.load_extraction_parts([run], build_bundle(), ticker="MU")


def test_another_tickers_run_refuses(roots):
    run = _record(roots, "run-x-amd-e07", items=[_capex()])
    with pytest.raises(ValueError, match="not a MU run"):
        rj.load_extraction_parts([run], build_bundle(), ticker="MU")


def test_the_same_block_loaded_twice_refuses(roots):
    a = _record(roots, "run-a-mu-e07", items=[_capex()])
    b = _record(roots, "run-b-mu-e07", items=[_capex()])
    with pytest.raises(ValueError, match="loaded twice"):
        rj.load_extraction_parts([a, b], build_bundle(), ticker="MU")


def test_an_unknown_run_refuses(roots):
    with pytest.raises(FileNotFoundError):
        rj.load_extraction_parts(["run-nope-mu-e07"], build_bundle(), ticker="MU")


def _found(evidence_id, quote, value):
    return {"evidence_id": evidence_id, "status": "found", "quote": quote,
            "value": value, "unit": "millions", "period_end": "2025-05-29"}


def _j06(monkeypatch, capsys, *runs) -> str:
    argv = ["x", "--dry-run", "--block", "J-06"]
    if runs:
        argv += ["--extractions", *runs]
    monkeypatch.setattr("sys.argv", argv)
    assert rj.main() == 0
    return capsys.readouterr().out


def test_main_refuses_J06_on_NO_evidence_and_on_PARTIAL_evidence(roots, monkeypatch, capsys):
    """★★★ End to end through the composition root.

    ⛔ `DX-98` (decided 2026-09-12): `ca.capex` alone makes `capital_allocation`
    level 0 available and nothing else — measured on MU. The runner must refuse
    that as PARTIAL, not send a one-option enum that records a floor score."""
    assert "RA-32 REFUSES" in _j06(monkeypatch, capsys)

    run = _record(roots, "run-x-mu-e07", items=[_capex()])
    out = _j06(monkeypatch, capsys, run)
    assert "found=['ca.capex']" in out
    assert "DX-98 REFUSES" in out and "levels=(" not in out
    assert "1 REFUSED before sending" in out


def test_main_offers_J06_the_FULL_range_when_every_level_has_its_evidence(roots, monkeypatch, capsys):
    """★ The positive half: `ca.capex` (E-07) + `sc.diluted`/`sc.sbc_expense`
    (E-10) + `cp.statement` (E-12), each a real quote from the MU filing."""
    e07 = _record(roots, "run-a-mu-e07", items=[_capex()])
    e10 = _record(roots, "run-b-mu-e10", block="E-10", items=[
        _found("sc.diluted", "Diluted | 1,125 | 1,123 | 1,123 | 1,104", "1,125"),
        _found("sc.sbc_expense",
               "Stock-based compensation expense | — | — | 220 | — | — | — | 220", "220")])
    e12 = _record(roots, "run-c-mu-e12", block="E-12", items=[_found(
        "cp.statement",
        "On June 25, 2025, our Board of Directors declared a quarterly dividend of $0.115 per share",
        "our Board of Directors declared a quarterly dividend of $0.115 per share")])
    out = _j06(monkeypatch, capsys, e07, e10, e12)
    assert "levels=(4, 3, 2, 1, 0)" in out and "REFUSES" not in out


@pytest.mark.parametrize("runner", ["tools/run_extraction_once.py",
                                    "tools/run_judgement_once.py"])
def test_dx_95_both_runners_pass_bundle_hash_to_the_trace(runner):
    """★★ `DX-95` — `CT-2.2` `A6` exists in the wrapper; this checks the CALLERS
    use it (`DX-82`'s lesson). ⚠ A live run cannot execute offline, so the
    `traced_transport(...)` call is read from the AST, not from a string grep
    that a comment could satisfy."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(runner).read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "traced_transport"]
    assert calls, f"{runner} no longer calls traced_transport"
    for call in calls:
        kw = {k.arg: k.value for k in call.keywords}
        assert "bundle_hash" in kw, f"{runner}: a traced call records no bundle_hash"
        assert not (isinstance(kw["bundle_hash"], ast.Constant)), (
            f"{runner}: bundle_hash is a literal — it must be the bundle actually sent")


def test_dx_97_the_loader_refuses_an_E13_run_whose_competitor_is_the_registrant(roots):
    """⛔ `DX-97` on the loader — so a run recorded BEFORE the guard existed
    (the 2026-09-12 E-13) cannot reach a Stage-A bundle either. The quote is
    the REAL cover-page line of the MU filing."""
    from src.fundamental.errors import SubjectIsRegistrantError

    run = _record(roots, "run-x-mu-e13", block="E-13", items=[_found(
        "cx.competitor", "Micron Technology, Inc.", "Micron Technology, Inc.")])
    with pytest.raises(SubjectIsRegistrantError, match="DX-97"):
        rj.load_extraction_parts([run], build_bundle(), ticker="MU")


def _not_found(evidence_id):
    return {"evidence_id": evidence_id, "status": "not_found", "quote": "",
            "note": "no non-GAAP measure is presented"}


def test_dx_99_main_offers_J04_the_full_range_when_non_GAAP_was_SEARCHED_and_absent(
        roots, monkeypatch, capsys):
    """★★★ `DX-99` end to end, in MU's measured shape: E-04 returns every item
    `not_found`; E-09 returns `ap.change` `not_found`; E-01 finds segment income
    (a real MU quote). Under `v2` this refused at every level."""
    e01 = _record(roots, "run-a-mu-e01", block="E-01", items=[_found(
        "seg.op_income", "CNBU | $2,182 | $442 | $5,812 | $73", "2,182")])
    e04 = _record(roots, "run-b-mu-e04", block="E-04", items=[
        _not_found(i) for i in ("ng.measure", "ng.gaap_start", "ng.adjustment",
                                "ng.recurrence_note", "ng.nongaap_end")])
    e09 = _record(roots, "run-c-mu-e09", block="E-09", items=[_not_found("ap.change")])
    monkeypatch.setattr("sys.argv", ["x", "--dry-run", "--block", "J-04",
                                     "--extractions", e01, e04, e09])
    assert rj.main() == 0
    out = capsys.readouterr().out
    assert "levels=(4, 3, 2, 1, 0)" in out and "REFUSES" not in out

    monkeypatch.setattr("sys.argv", ["x", "--dry-run", "--block", "J-04",
                                     "--extractions", e01, e04])
    assert rj.main() == 0
    assert "DX-98 REFUSES" in capsys.readouterr().out, "no E-09 → partial → refused"


def _j06_evidence(roots):
    e07 = _record(roots, "run-a-mu-e07", items=[_capex()])
    e10 = _record(roots, "run-b-mu-e10", block="E-10", items=[
        _found("sc.diluted", "Diluted | 1,125 | 1,123 | 1,123 | 1,104", "1,125"),
        _found("sc.sbc_expense",
               "Stock-based compensation expense | — | — | 220 | — | — | — | 220", "220")])
    e12 = _record(roots, "run-c-mu-e12", block="E-12", items=[_found(
        "cp.statement",
        "On June 25, 2025, our Board of Directors declared a quarterly dividend of $0.115 per share",
        "our Board of Directors declared a quarterly dividend of $0.115 per share")])
    return [e07, e10, e12]


def _live_j06(roots, tmp_path, monkeypatch, capsys, pick):
    """Drive the LIVE path offline: a fake transport stands in for the vendor,
    and the trace is written under tmp. `pick(enum)` chooses the answer."""
    import tools.anthropic_transport as at

    seen = {}

    def fake_factory(*, tool=None, max_output=0):
        seen["tool"] = tool

        def transport(request):
            seen["request"] = request
            enum = tool["input_schema"]["properties"]["criterion"]["enum"]
            answer = {"criterion": pick(enum), "why": "w",
                      "what_would_move_it_down": "a disclosed issuance"}
            return {"text": json.dumps(answer), "stop_reason": "tool_use",
                    "tokens_in": 10, "tokens_out": 5}
        return transport

    monkeypatch.setattr(at, "anthropic_transport", fake_factory)
    monkeypatch.setattr(rj, "REPO", tmp_path)
    monkeypatch.setattr("sys.argv", ["x", "--live", "--block", "J-06", "--seed", "t",
                                     "--extractions", *_j06_evidence(roots)])
    code = rj.main()
    return code, capsys.readouterr().out, seen


def test_dx_100_the_LIVE_path_sends_the_criteria_and_DERIVES_the_score(
        roots, tmp_path, monkeypatch, capsys):
    """★★★ `DX-100` end to end through the composition root. The rubric's
    criterion text is in the payload, the tool's enum is exactly the offer (plus
    the exit), the shown order is recorded in the call's trace payload, and the
    printed score is DERIVED from the echoed criterion."""
    from src.fundamental.scorecard.selection import INSUFFICIENT_EVIDENCE

    # ★ The rubric the RUNNER resolves for J-06 — never a pinned version (`DX-72`).
    CAP = rj._rubric_for("J-06")
    target = CAP.level(3).criterion
    code, out, seen = _live_j06(roots, tmp_path, monkeypatch, capsys,
                                pick=lambda enum: target)
    assert code == 0, out
    payload = seen["request"]["payload"]
    for lv in CAP.levels:
        assert lv.criterion in payload
    enum = seen["tool"]["input_schema"]["properties"]["criterion"]["enum"]
    assert set(enum) == {lv.criterion for lv in CAP.levels} | {INSUFFICIENT_EVIDENCE}
    order = seen["request"]["option_permutation"]
    assert sorted(order) == [0, 1, 2, 3, 4]
    assert enum[:5] == [CAP.level(s).criterion for s in order], "enum ≠ shown order"
    assert "score=3" in out and CAP.rubric_id in out

    (run_dir,) = (tmp_path / ".state/runs").iterdir()
    (payload_file,) = (run_dir / "trace/payloads").iterdir()
    recorded = json.loads(payload_file.read_text())["request"]
    assert recorded["option_permutation"] == order and recorded["option_seed"]


def test_dx_100_insufficient_evidence_is_reported_and_is_NOT_a_score(
        roots, tmp_path, monkeypatch, capsys):
    from src.fundamental.scorecard.selection import INSUFFICIENT_EVIDENCE

    code, out, _ = _live_j06(roots, tmp_path, monkeypatch, capsys,
                             pick=lambda enum: INSUFFICIENT_EVIDENCE)
    assert code == 0 and "INSUFFICIENT_EVIDENCE (not a score)" in out
    assert "score=" not in out


def test_dx_100_an_answer_that_is_not_an_offered_criterion_gets_NO_score(
        roots, tmp_path, monkeypatch, capsys):
    """⚠ The vendor is not obliged to honour an enum on a degraded call."""
    code, out, _ = _live_j06(roots, tmp_path, monkeypatch, capsys,
                             pick=lambda enum: "Management allocated capital well.")
    assert code == 1 and "NO SCORE" in out and "score=" not in out
