"""`tools/run_thesis_once.py` — Stages B–D over a frozen Stage A (L3 §2.1g steps 4–5).

★ Each test pins one guarantee the runner's docstring states: the staging rule, the
falsifier-before-verdict order, the declared enums, the frozen-output part kind, and
the refusals. ⚠ None needs the network or `.state/`: a fresh clone runs them.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.fundamental.prompts.e_blocks import BLOCKS

AS_OF = date(2025, 6, 26)


def _text(block_id: str) -> str:
    return " ".join(BLOCKS[block_id][0]().text.split())


@pytest.mark.parametrize(("block_id", "path"), [
    ("J-09", ("price_requirements", "items", "properties", "versus_stage_a")),
    ("J-10", ("claims", "items", "properties", "typical_or_exceptional")),
    ("J-13", ("mechanisms", "items", "properties", "status")),
    ("J-16", ("verdict",)),
    ("J-16", ("conviction",)),
])
def test_mp_5_every_enum_the_prompt_names_is_declared_verbatim(block_id, path):
    """★ `MP-5` — a closed set the prompt LISTS is the schema's enum, word for word."""
    from tools.run_thesis_once import thesis_tool

    node = thesis_tool(block_id, observables=("x",))["input_schema"]["properties"]
    for step in path:
        node = node[step]
    for value in node["enum"]:
        assert value in _text(block_id), f"{block_id} schema offers {value!r}, the prompt never names it"


def test_j15_answers_only_from_the_supplied_observables_and_j16_cannot_be_built_without_them():
    from tools.run_thesis_once import thesis_tool

    schema = thesis_tool("J-15", observables=("Revenues", "GrossProfit"))["input_schema"]
    item = schema["properties"]["falsifiers"]
    assert item["items"]["properties"]["observable_field"]["enum"] == ["Revenues", "GrossProfit"]
    assert (item["minItems"], item["maxItems"]) == (2, 4)             # J-15: two to four
    with pytest.raises(ValueError, match="observable"):
        thesis_tool("J-15")


def test_every_stage_b_to_d_block_is_full_view_and_declared_verbatim_elsewhere():
    """★ `MP-3` — Stage B is where the price is revealed; the drift guard covers the text."""
    for block_id in ("J-09", "J-10", "J-11", "J-12", "J-13", "J-14", "J-15", "J-16", "J-17"):
        assert BLOCKS[block_id][0]().view == "full"


def test_ra_16_the_plan_issues_J15_before_J16_and_J17_last():
    from tools.run_thesis_once import metrics_for, stage_plan

    order = [b for _s, b, _m in stage_plan(metrics_for(False))]
    assert order.index("J-15") < order.index("J-16") < order.index("J-17") == len(order) - 1
    assert order[:2] == ["J-09", "J-10"]


def test_j13_binds_one_call_per_standing_metric_and_book_value_only_for_a_financial():
    from tools.run_thesis_once import metrics_for

    assert "book_value" not in metrics_for(False) and len(metrics_for(False)) == 5
    assert "book_value" in metrics_for(True)


@pytest.mark.parametrize(("stage", "block", "must_see", "must_not_see"), [
    ("B", "J-09", {"A:J-01"}, {"C:J-11"}),
    ("B", "J-10", {"A:J-01", "B:J-09"}, set()),
    ("C", "J-11", {"A:J-01", "B:J-09", "B:J-10"}, {"C:J-12"}),
    ("C", "J-12", {"B:J-10"}, {"C:J-11"}),
    ("C", "J-13", {"B:J-10"}, {"C:J-11", "C:J-12"}),
    ("C", "J-14", {"C:J-11", "C:J-12", "C:J-13:operating_margin"}, set()),
    ("D", "J-16", {"D:falsifiers", "C:J-14"}, set()),
])
def test_ra_15_the_staging_rule_says_exactly_what_each_call_reads(stage, block, must_see, must_not_see):
    """★★ `J-11`: *"You have NOT seen any bull case"*; a pre-mortem that reads the bear case
    is a reply to it (`RA-15`). `J-14` reads the analysis so far."""
    from tools.run_thesis_once import visible_commits

    committed = ["A:J-01", "B:J-09", "B:J-10", "C:J-11", "C:J-12", "C:J-13:operating_margin",
                 "C:J-14", "D:falsifiers"]
    seen = set(visible_commits(stage, block, committed))
    assert must_see <= seen and not (must_not_see & seen)


def test_call_prompt_binds_the_metric_and_refuses_an_unbound_placeholder():
    from tools.run_thesis_once import call_prompt

    bound = call_prompt("J-13", "free_cash_flow")
    assert "<METRIC>" not in bound and "free_cash_flow is good" in " ".join(bound.split())
    with pytest.raises(ValueError, match="needs a metric"):
        call_prompt("J-13", None)
    with pytest.raises(ValueError, match="no <METRIC>"):
        call_prompt("J-09", "operating_margin")


def test_s8_is_composed_and_s7_is_not():
    """§4.0: `S-8` in fresh authoring; `S-7` (anti-anchoring) is Stage A only."""
    from src.fundamental.prompts.envelope import S7, S8
    from tools.run_thesis_once import call_prompt

    prompt = call_prompt("J-09", None)
    assert S8.strip() in prompt and S7.strip() not in prompt


@pytest.mark.parametrize(("answer", "problem"), [
    ({"verdict": "STRONG_BUY"}, "not in"),
    ({"verdict": "HOLD"}, "required"),
    ({"verdict": "HOLD", "conviction": "High",
      "considerations": [{"consideration": "a", "from_call": "J-09"}] * 4}, "maxItems"),
])
def test_mp_5_the_answer_is_validated_because_the_vendor_is_not_obliged_to(answer, problem):
    from tools.run_thesis_once import thesis_tool, validate

    assert any(problem in p for p in validate(thesis_tool("J-16")["input_schema"], answer))


def _falsifier(**over):
    base = {"condition": "Revenues below 7,000,000,000 USD in the quarter ending 2026-02-26",
            "observable_field": "Revenues", "deadline": "2026-04-30",
            "materiality": "the recovery thesis is wrong", "about_business": True}
    return {**base, **over}


@pytest.mark.parametrize(("over", "match"), [
    ({"deadline": "2025-06-01"}, "not after the as_of"),
    ({"deadline": "next year"}, "not a date"),
    ({"observable_field": "sentiment"}, "not an observable"),
    ({"condition": "the investment case no longer holds"}, "tautology"),
])
def test_ra_35_a_falsifier_that_cannot_be_checked_refuses_before_any_commit(over, match):
    from src.fundamental.errors import UncheckableFalsifierError
    from tools.run_thesis_once import falsifiers_from

    with pytest.raises(UncheckableFalsifierError, match=match):
        falsifiers_from({"falsifiers": [_falsifier(), _falsifier(**over)]}, as_of=AS_OF,
                        observables=("Revenues",))


def test_the_thesis_is_built_only_from_committed_outputs_and_validates():
    """★ `CT-1.1` end to end on synthetic outputs — `Thesis.__post_init__` is the judge."""
    from src.fundamental.thesis.author import CommitLog, commit_falsifiers
    from tools.run_thesis_once import STAGE_A_ABSENT, build_thesis, falsifiers_from

    log = CommitLog()
    a = log.commit("A", "sha256:blind", {"blocks": []})
    fc = commit_falsifiers(log, bundle_hash="sha256:b", falsifiers=falsifiers_from(
        {"falsifiers": [_falsifier(), _falsifier(condition="Revenues fall two quarters running")]},
        as_of=AS_OF, observables=("Revenues",)))
    outputs = {"C:J-11": {"answer": "bear text", "own_falsification_condition": "GM above 40%"},
               "D:J-16": {"verdict": "HOLD", "conviction": "Medium"},
               "D:J-17": {"gaps": [{"gap": "channel inventory", "obtainable": "not_disclosed"}]}}
    ids = {"C:J-11": "r:judge:C:J-11", "B:J-09": "r:judge:B:J-09", "D:J-16": "r:judge:D:J-16"}
    stage_a = [{"block_id": "J-05", "derived": {"rubric_id": "bs@v3", "score": 3}}]
    thesis = build_thesis(ticker="MU", as_of=AS_OF, run_id="r", bundle_hash="sha256:base",
                          outputs=outputs, call_ids=ids, falsifier_commit=fc,
                          stage_a_commit=a, stage_a=stage_a)
    assert thesis.falsifier_commit_hash == fc.commit_hash and thesis.stage_a_hash == a.commit_hash
    assert thesis.scorecard["J-05"]["score"] == 3
    assert set(STAGE_A_ABSENT) <= set(thesis.scorecard)
    assert thesis.data_gaps == ("channel inventory [not_disclosed]",)


def test_a_stage_output_is_pinned_by_its_commit_and_withheld_from_every_blind_view():
    """★ A Stage B–D commitment has read the price; a blind view must never carry one."""
    from src.fundamental.bundle.assemble import filing, stage_output
    from src.fundamental.bundle.models import EvidenceBundle

    part = stage_output(stage="B", block_id="J-09", prompt_version="v1", run_id="r",
                        commit_hash="sha256:c", answer={"answer": "price requires 28%"})
    assert part.pins["commit_hash"] == "sha256:c" and "may not revise" in part.content
    bundle = EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(filing("acc", "text"), part))
    assert part in bundle.parts and part not in bundle.redact().parts


def test_dx_109_the_declared_absences_part_names_each_input_and_refuses_being_empty():
    from src.fundamental.bundle.assemble import declared_absences
    from src.fundamental.errors import BundleInconsistentError
    from tools.run_thesis_once import STAGE_B_ABSENCES

    part = declared_absences("x", STAGE_B_ABSENCES)
    for item in ("consensus_forward_estimates", "implied_margin", "implied_duration",
                 "valuation_multiples", "market_capitalisation"):
        assert f"- {item}:" in part.content
    with pytest.raises(BundleInconsistentError):
        declared_absences("x", {})


def test_a_rubric_answer_recorded_before_dx_100_is_VOID_and_refused():
    """⚠ The 2026-09-12 Stage A's J-05 chose a level blind to the criteria (`DX-100`)."""
    from src.fundamental.bundle.assemble import filing
    from src.fundamental.bundle.models import EvidenceBundle
    from tools.run_thesis_once import load_stage_a

    blind = EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(filing("acc", "text"),)).redact()
    with pytest.raises(ValueError, match="predates DX-100"):
        load_stage_a({"J-05": "run-2026-09-12T024848-mu-stage-a"}, blind=blind,
                     history_rows=None, ticker="MU", as_of=AS_OF)


def test_an_enum_stage_a_answer_loads_from_its_recording():
    from src.fundamental.bundle.assemble import filing
    from src.fundamental.bundle.models import EvidenceBundle
    from tools.run_thesis_once import load_stage_a

    blind = EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(filing("acc", "text"),)).redact()
    (record,) = load_stage_a({"J-07": "run-2026-09-12T024848-mu-stage-a"}, blind=blind,
                             history_rows=None, ticker="MU", as_of=AS_OF)
    assert record["answer"]["cycle_position"] == "mid" and record["derived"] is None


def test_live_without_an_approved_cap_is_BLOCKED_before_anything_is_built(capsys, monkeypatch,
                                                                         tmp_path):
    """⚠⚠ Wired to fakes that RAISE: found 2026-09-14 when a mutant disabling this guard ran
    the real composition and wrote a run directory (it crashed before any vendor call). A
    test of a spend guard must not be able to spend when the guard is broken."""
    import tools.anthropic_transport as transport_mod
    import tools.run_thesis_once as r

    def boom(*_a, **_k):
        raise AssertionError("the guard let a --live run proceed")

    monkeypatch.setattr(r, "REPO", tmp_path)
    monkeypatch.setattr(r, "build_base", boom)
    monkeypatch.setenv("CIA_LLM_TRANSPORT", "anthropic_api")   # this test covers the API path (GW-24)
    monkeypatch.setattr(transport_mod, "anthropic_transport", boom)
    assert r.main(["--live"]) == 2
    assert "requires --budget-usd" in capsys.readouterr().out


# ═══════════════════════════════════════════════════════════════════════════
# ★★ The LIVE loop, with a fake vendor — the order guarantees where they actually run
# ═══════════════════════════════════════════════════════════════════════════

def _fill(schema: dict):
    """The smallest answer that satisfies a schema — a stand-in for the vendor."""
    kinds = schema.get("type")
    kinds = kinds if isinstance(kinds, list) else [kinds]
    if "enum" in schema:
        return schema["enum"][0]
    if "object" in kinds:
        return {k: _fill(v) for k, v in schema["properties"].items()}
    if "array" in kinds:
        import re
        n = schema.get("minItems") or int((re.findall(r"\d+", schema.get("description", "")) or [1])[0])
        return [_fill(schema["items"]) for _ in range(max(n, 1))]
    if "null" in kinds:
        return None              # ✏ `DX-147`: a nullable `consecutive` filled as 1 is refused
    return {"string": "x", "boolean": True, "integer": 1,
            "number": 1.0}[next(k for k in kinds if k != "null")]


# ✏ 2026-10-03 (`DX-144` ⓐ): the fake J-15's test has a 1-quarter window, so its deadline must
#   fall before a SECOND quarter reports — 2026-03-31 would leave ~2 quarters unexamined.
def _wire_fake_run(monkeypatch, tmp_path, *, j15_deadline="2025-12-31"):
    import json as _json

    import src.feature_engineer.valuation.service as service
    import tools.anthropic_transport as transport_mod
    import tools.run_thesis_once as r
    from src.fundamental.bundle.assemble import filing
    from src.fundamental.bundle.models import EvidenceBundle

    # ✏ 2026-10-04: a marker no prompt contains — J-15 v3 says "…for the filing", which made
    #   "evidence sent twice" fire on the PROMPT, not the evidence.
    base = EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(filing("acc", "FIXTURE-FILING-BODY"),))
    monkeypatch.setattr(r, "REPO", tmp_path)
    monkeypatch.setattr(r, "build_base", lambda *_a, **_k: (base, None, None, None, ("Revenues",)))
    monkeypatch.setattr(r, "load_stage_a", lambda *_a, **_k: [
        {"block_id": "J-20", "prompt_version": "v1", "run_id": "run-x-mu-j20",
         "recorded_bundle_hash": None, "answer": {"method": "reported_ttm"},
         "derived": {"basis": {"base_fcff": {"minor": 1}}, "_basis_obj": None}}])

    class _Val:
        def to_json(self):
            return _json.dumps({"value_per_share": 1, "price": {"value": 2, "date": "2025-06-26"},
                                "implied": {"value": "0.28", "status": "SOLVED"}})

    monkeypatch.setattr(service, "valuation", lambda *_a, **_k: _Val())
    monkeypatch.setattr(service, "value_on_basis", lambda *_a, **_k: _Val())
    issued = []

    def fake_transport(*, tool, max_output, **_k):
        def send(request):
            name = tool["name"]
            commits = (tmp_path / ".state/runs").glob("*/commits.jsonl")
            assert tool.get("strict") is True, "the live loop must send the STRICT schema (DX-113)"
            if name in ("answer_j_13", "answer_j_14", "answer_j_15", "answer_j_16", "answer_j_17"):
                assert (max_output, request.get("effort")) == (32_000, "medium"), "DX-114/115"
            else:
                assert "effort" not in request and request["max_tokens"] == 16_000
            issued.append((name, [_json.loads(ln)["stage"] for f in commits
                                  for ln in f.read_text().splitlines()], request["reads_commits"]))
            answer = _fill(tool["input_schema"])
            if name == "answer_j_15":
                for f in answer["falsifiers"]:
                    f["deadline"] = j15_deadline
            return {"text": _json.dumps(answer), "stop_reason": "tool_use",
                    "tokens_in": 10, "tokens_out": 10}
        return send

    monkeypatch.setenv("CIA_LLM_TRANSPORT", "anthropic_api")   # this test covers the API path (GW-24)
    monkeypatch.setattr(transport_mod, "anthropic_transport", fake_transport)
    return r, issued


def test_ra_16_live_J16_is_issued_only_after_the_falsifier_commit_is_ON_DISK(monkeypatch, tmp_path):
    """★★ The guarantee in the loop that runs it: when J-16 is sent, `commits.jsonl`
    already holds `D:falsifiers`, and J-16's bundle reads that commit."""
    import json as _json

    r, issued = _wire_fake_run(monkeypatch, tmp_path)
    assert r.main(["--live", "--budget-usd", "100"]) == 0
    names = [n for n, _c, _s in issued]
    assert names[-3:] == ["answer_j_15", "answer_j_16", "answer_j_17"]
    _n, on_disk, reads = issued[names.index("answer_j_16")]
    assert "D:falsifiers" in on_disk and "D:falsifiers" in reads
    _n, on_disk_at_j11, reads_j11 = issued[names.index("answer_j_11")]
    assert "B:J-10" in on_disk_at_j11 and not any(k.startswith("C:") for k in reads_j11)
    (summary_file,) = (tmp_path / ".state/runs").glob("*/thesis.json")
    summary = _json.loads(summary_file.read_text())
    assert summary["failed"] is None and summary["thesis"]["falsifier_commit_hash"]
    # ✏ `DX-118` — the measured coverage travels on the artifact, and with NO extraction
    #   evidence in this fake bundle the floor declines rather than proposing a direction.
    confidence = summary["thesis"]["confidence"]
    assert confidence["basis"] == "evidence_coverage" and confidence["value"] == 0.0
    assert summary["thesis"]["verdict"] == "INSUFFICIENT_DATA"
    assert confidence["verdict_as_authored"] == "BUY" and confidence["coverage"]["by_dimension"]


def test_ra_16_live_a_failed_falsifier_set_means_J16_is_NEVER_issued(monkeypatch, tmp_path):
    """⚠ `RES.THESIS.NO_FALSIFIER` — a deadline inside the bundle window refuses the commit,
    and no verdict call is made (P5: no thesis)."""
    import json as _json

    r, issued = _wire_fake_run(monkeypatch, tmp_path, j15_deadline="2025-01-01")
    assert r.main(["--live", "--budget-usd", "100"]) == 1
    names = [n for n, _c, _s in issued]
    assert "answer_j_15" in names and "answer_j_16" not in names
    (summary_file,) = (tmp_path / ".state/runs").glob("*/thesis.json")
    summary = _json.loads(summary_file.read_text())
    assert summary["thesis"] is None and "NO_FALSIFIER" in summary["failed"][1]


def test_the_budget_cap_stops_BEFORE_a_call_that_could_pass_it(monkeypatch, tmp_path):
    r, issued = _wire_fake_run(monkeypatch, tmp_path)
    assert r.main(["--live", "--budget-usd", "0.01"]) == 1
    assert issued == []


# ═══════════════════════════════════════════════════════════════════════════
# ✏ 2026-09-15 — after the first live run failed at J-11 (L3 DX-113)
# ═══════════════════════════════════════════════════════════════════════════

def test_dx_113_the_SENT_schema_is_strict_and_the_validated_one_keeps_every_constraint():
    """⛔ J-11 returned 4 of 6 required fields under a non-strict schema. ★ The sent copy is
    strict (every object closed, no array bounds); `validate` still holds the bounds."""
    from tools.run_thesis_once import strict_tool, thesis_tool, validate

    tool = thesis_tool("J-11")
    sent = strict_tool(tool)
    assert sent["strict"] is True and "strict" not in tool

    def objects(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                yield node
            for v in node.values():
                yield from objects(v)
        elif isinstance(node, list):
            for v in node:
                yield from objects(v)

    assert all(o.get("additionalProperties") is False for o in objects(sent["input_schema"]))
    assert "minItems" not in str(sent) and "minItems" in str(tool)
    bounds = sent["input_schema"]["properties"]["load_bearing_assumptions"]
    assert bounds["description"] == "exactly 3 items"          # the bound still reaches the model
    partial = {"strongest_reason": {"reason": "r", "evidence": "e"}, "evidence": "stray"}
    assert any("required" in v for v in validate(tool["input_schema"], partial))


def _carry_setup(tmp_path, monkeypatch):
    import json as _json

    import tools.run_thesis_once as r
    from src.fundamental.bundle.assemble import filing, stage_output
    from src.fundamental.bundle.models import EvidenceBundle
    from src.fundamental.thesis.author import CommitLog

    monkeypatch.setattr(r, "REPO", tmp_path)
    base = EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(filing("acc", "the filing"),))

    def fresh():
        log = CommitLog()
        a = log.commit("A", "sha256:blind", {"blocks": []})
        parts = {"A:J-01": stage_output(stage="A", block_id="J-01", prompt_version="v1",
                                        run_id="run-x", commit_hash=a.commit_hash, answer={})}
        return log, a, parts

    log, a, parts = fresh()
    j09_bundle = r.call_bundle(base, parts, ["A:J-01"]).bundle_hash
    j09 = log.commit("B:J-09", j09_bundle, {"answer": "the price requires 28%"})
    run = tmp_path / ".state/runs/run-prior-mu-thesis"
    run.mkdir(parents=True)
    lines = [a.to_json_obj(), j09.to_json_obj()]
    (run / "commits.jsonl").write_text("\n".join(_json.dumps(x) for x in lines) + "\n")
    return r, base, fresh, run, lines


def test_resume_carries_a_commit_only_when_it_REPRODUCES(tmp_path, monkeypatch):
    r, base, fresh, _run, _lines = _carry_setup(tmp_path, monkeypatch)
    log, a, parts = fresh()
    outputs, ids, carried, fc = r.carry_forward("run-prior-mu-thesis", log=log, a_commit=a,
                                                base=base, parts_by_key=parts)
    assert outputs["B:J-09"]["answer"] == "the price requires 28%" and len(carried) == 1
    assert "B:J-09" in parts and parts["B:J-09"].pins["run_id"] == "run-prior-mu-thesis"
    assert fc is None and ids["B:J-09"].startswith("run-prior-mu-thesis:")


@pytest.mark.parametrize("tamper", ["payload", "bundle", "stage_a"])
def test_resume_REFUSES_a_tampered_or_foreign_commit(tmp_path, monkeypatch, tamper):
    import json as _json

    r, base, fresh, run, lines = _carry_setup(tmp_path, monkeypatch)
    if tamper == "payload":
        lines[1]["payload"] = {"answer": "the price requires 5%"}
    elif tamper == "bundle":
        # ★ A GENUINE commit replayed over DIFFERENT evidence: its own hash reproduces, so
        #   only the bundle check can refuse it (the first version of this case also broke
        #   the commit hash and let a disabled bundle check survive mutation).
        from src.fundamental.bundle.assemble import filing
        from src.fundamental.bundle.models import EvidenceBundle
        base = EvidenceBundle(ticker="MU", as_of=AS_OF, parts=(filing("acc", "another filing"),))
    else:
        lines[0]["commit_hash"] = "sha256:another-stage-a"
    (run / "commits.jsonl").write_text("\n".join(_json.dumps(x) for x in lines) + "\n")
    log, a, parts = fresh()
    with pytest.raises(ValueError, match="not carried|different Stage A"):
        r.carry_forward("run-prior-mu-thesis", log=log, a_commit=a, base=base, parts_by_key=parts)


def test_resend_from_carries_only_the_commits_BEFORE_the_block(tmp_path, monkeypatch):
    """✏ 2026-10-03 — re-asking J-15 under a new falsifier rule (`DX-144`) must not carry the
    old J-15: `resend_from` stops the carry at that block, in plan order."""
    import json as _json

    r, base, fresh, run, lines = _carry_setup(tmp_path, monkeypatch)
    log, a, parts = fresh()
    # ★ A J-10 that would NOT verify: carried, it would raise — so passing proves it was skipped.
    j10 = {"stage": "B:J-10", "bundle_hash": "sha256:unchecked", "commit_hash": "sha256:x",
           "payload": {"answer": "stale"}}
    (run / "commits.jsonl").write_text(
        "\n".join(_json.dumps(x) for x in [*lines, j10]) + "\n")
    outputs, _ids, carried, _fc = r.carry_forward("run-prior-mu-thesis", log=log, a_commit=a,
                                                  base=base, parts_by_key=parts,
                                                  resend_from="J-10")
    assert [c["stage"] for c in carried] == ["B:J-09"]
    assert "B:J-10" not in outputs and "B:J-10" not in parts


def test_dx_113_a_failed_live_run_closes_its_trace_FAILED(monkeypatch, tmp_path):
    r, _issued = _wire_fake_run(monkeypatch, tmp_path, j15_deadline="2025-01-01")
    assert r.main(["--live", "--budget-usd", "100"]) == 1
    (trace,) = (tmp_path / ".state/runs").glob("*/trace.jsonl")
    assert '"status": "FAILED"' in trace.read_text()


def test_a_resume_of_a_resume_pins_each_commit_to_the_run_that_PRODUCED_it(tmp_path, monkeypatch):
    """⛔ Found 2026-09-15: resuming the resumed run re-pinned J-09/J-10 to the carrying run,
    so their bundle hashes stopped reproducing — refused, correctly, by the bundle check."""
    import json as _json

    r, base, fresh, run, lines = _carry_setup(tmp_path, monkeypatch)
    log, a, parts = fresh()
    *_ignored, carried, _fc = r.carry_forward("run-prior-mu-thesis", log=log, a_commit=a,
                                              base=base, parts_by_key=parts)
    second = tmp_path / ".state/runs/run-second-mu-thesis"
    second.mkdir(parents=True)
    (second / "commits.jsonl").write_text(
        "\n".join(_json.dumps(x) for x in [lines[0], *carried]) + "\n")
    log, a, parts = fresh()
    _o, ids, again, _f = r.carry_forward("run-second-mu-thesis", log=log, a_commit=a, base=base,
                                         parts_by_key=parts)
    assert parts["B:J-09"].pins["run_id"] == "run-prior-mu-thesis"
    assert again[0]["carried_from"] == "run-prior-mu-thesis"
    assert ids["B:J-09"].startswith("run-prior-mu-thesis:")


# ═══════════════════════════════════════════════════════════════════════════
# `DX-127` — prompt caching: the stable evidence is its own block
# ═══════════════════════════════════════════════════════════════════════════

def test_dx_127_every_call_sends_the_SAME_cache_prefix_and_only_the_rest_varies(monkeypatch,
                                                                                tmp_path):
    """★★ Caching is a PREFIX match: one byte of drift and every later call pays full price.
    ⚠ So what must hold is not "a prefix was sent" but that all 13 are byte-identical."""
    r, issued = _wire_fake_run(monkeypatch, tmp_path)
    seen: list[tuple[str, str]] = []
    import tools.anthropic_transport as transport_mod
    inner = transport_mod.anthropic_transport

    def capture(*, tool, max_output, **kw):
        send = inner(tool=tool, max_output=max_output, **kw)

        def wrapped(request):
            seen.append((request.get("cache_prefix", ""), request["payload"]))
            return send(request)
        return wrapped

    monkeypatch.setenv("CIA_LLM_TRANSPORT", "anthropic_api")   # this test covers the API path (GW-24)
    monkeypatch.setattr(transport_mod, "anthropic_transport", capture)
    assert r.main(["--live", "--budget-usd", "100"]) == 0
    prefixes = {p for p, _ in seen}
    assert len(seen) == 13 and len(prefixes) == 1, "the cached prefix must not vary"
    prefix = prefixes.pop()
    assert "FIXTURE-FILING-BODY" in prefix                      # the base evidence
    assert all("FIXTURE-FILING-BODY" not in rest for _p, rest in seen), "evidence sent twice"
    # ★ The instructions and the commits this call may read are the variable half.
    assert "TASK TYPE: JUDGEMENT" in seen[0][1]


def test_ac_0_28_every_subscription_call_shares_ONE_schema_family(monkeypatch, tmp_path):
    """AC-0.28 (GW-31, `DX-181`) — on `claude_code` a per-call schema is a different tool,
    and tools precede the cached prefix, so all 13 calls must be handed the SAME family,
    and each call's own strict tool must be in it."""
    import json

    import tools.anthropic_transport as transport_mod
    import tools.llm_transport as llm

    r, _issued = _wire_fake_run(monkeypatch, tmp_path)
    fake = transport_mod.anthropic_transport
    seen = []

    def capture(*, family=None, **kw):
        seen.append((kw["tool"], family))
        return fake(**kw)

    monkeypatch.delenv("CIA_LLM_TRANSPORT", raising=False)
    monkeypatch.setattr(llm, "dev_transport", capture)
    assert r.main(["--live", "--budget-usd", "100"]) == 0
    assert len(seen) == 13
    families = {json.dumps(f, sort_keys=True) for _t, f in seen}
    assert len(families) == 1, "the schema family must not vary between calls"
    for tool, family in seen:
        assert family[tool["name"]] == tool
    assert len(seen[0][1]) == 9                                          # J-09…J-17


def test_dx_127_no_cache_reproduces_the_single_block_payload(monkeypatch, tmp_path):
    """⚠ The escape hatch matters: `--no-cache` sends exactly what the first thesis sent
    (instructions first, one block), so a regression can be bisected against it."""
    r, _issued = _wire_fake_run(monkeypatch, tmp_path)
    seen = []
    import tools.anthropic_transport as transport_mod
    inner = transport_mod.anthropic_transport

    def capture(*, tool, max_output, **kw):
        send = inner(tool=tool, max_output=max_output, **kw)
        return lambda request: (seen.append(request) or send(request))

    monkeypatch.setenv("CIA_LLM_TRANSPORT", "anthropic_api")   # this test covers the API path (GW-24)
    monkeypatch.setattr(transport_mod, "anthropic_transport", capture)
    assert r.main(["--live", "--budget-usd", "100", "--no-cache"]) == 0
    assert all("cache_prefix" not in req for req in seen)
    first = seen[0]["payload"]
    assert first.index("TASK TYPE: JUDGEMENT") < first.index("FIXTURE-FILING-BODY"), "instructions first"


def test_j15_v2_live_writes_its_structured_tests_beside_the_thesis(monkeypatch, tmp_path):
    """★ `J-15 v2` (`L3` §2.1p item 3) — the live loop writes `falsifier_tests.json`
    next to `thesis.json`, stamped with THIS run's id, and every test is valid in the
    grammar `falsifier_check` decides, so `check_falsifiers.py` needs no `--tests`."""
    import json as _json

    from src.fundamental.monitor.falsifier_check import validate_test
    from tools.check_falsifiers import tests_for

    r, _issued = _wire_fake_run(monkeypatch, tmp_path)
    assert r.main(["--live", "--budget-usd", "100"]) == 0
    (thesis_file,) = (tmp_path / ".state/runs").glob("*/thesis.json")
    summary = _json.loads(thesis_file.read_text())
    tests = tests_for(thesis_file, explicit=None)
    assert tests["_thesis_run_id"] == summary["run_id"]
    ordinals = [k for k in tests if not k.startswith("_")]
    assert len(ordinals) == len(summary["thesis"]["falsifiers"]) >= 2
    assert all(validate_test(tests[k], observables=("Revenues",)) == [] for k in ordinals)


# ═══════════════════════════════════════════════════════════════════════════
# AC-F13.19 (`DX-183`) — the planner's ceiling is a ceiling
# ═══════════════════════════════════════════════════════════════════════════

#: MEASURED — `run-2026-10-22T004557-mu-thesis`, the `claude_code` trace payloads:
#: `(block, tokens_in, tokens_out, num_turns, notional_usd)`. Every one wrote the whole
#: prompt to the cache (no reuse, `DX-181`); J-15/J-17 took a schema-repair turn (`DX-182`).
MEASURED_MU_2026_10_20 = (
    ("J-13", 234_508, 16_818, 2, 2.76552),
    ("J-14", 286_054, 23_674, 2, 3.45238),
    ("J-15", 605_298, 16_067, 3, 3.612026),
    ("J-16", 300_021, 3_272, 2, 3.082),
    ("J-17", 607_052, 14_938, 3, 3.573335),
)


@pytest.mark.parametrize("block,tokens_in,_out,turns,notional", MEASURED_MU_2026_10_20)
def test_ac_f13_19_the_ceiling_covers_every_measured_call(block, tokens_in, _out, turns,
                                                          notional):
    """AC-F13.19 — priced from the PROMPT size (a repair turn re-reads the same prompt, so
    a 3-turn call's measured input is twice it), the ceiling is ≥ what the call cost."""
    import tools.run_thesis_once as r

    prompt_tokens = tokens_in // (2 if turns == 3 else 1)
    cap = r.output_settings(block)[0]
    assert r.call_ceiling(prompt_tokens, cap, transport="claude_code") >= notional


def test_ac_f13_19_the_claude_code_write_rate_is_the_measured_one():
    """AC-F13.19 — the CLI caches for an hour, at 2× the input rate: J-16 wrote 300,019
    tokens and output 3,272 for a notional $3.0820 — 2.0× fits it to the cent; 1.25× is $1.12
    short."""
    import tools.run_thesis_once as r

    assert r.CACHE_WRITE_RATES["claude_code"] == 2.0
    j16 = 300_019 * 2.0 * r.PRICE_IN + 3_272 * r.PRICE_OUT
    assert j16 == pytest.approx(3.082, abs=0.005)


def test_ac_f13_19_expected_writes_the_prefix_once_and_reads_it_after():
    """AC-F13.19 — with GW-30/31 the shared prefix is written by the first call only."""
    import tools.run_thesis_once as r

    calls = [(100_000, 10_000)] * 3                  # (prompt tokens, output cap)
    expected, ceiling = r.plan_cost(calls, prefix_tokens=90_000, projected_out=1_000,
                                    transport="claude_code")
    w, rd = r.CACHE_WRITE_RATES["claude_code"], r.CACHE_READ_RATE
    first = 100_000 * w * r.PRICE_IN
    later = (90_000 * rd + 10_000 * w) * r.PRICE_IN
    assert expected == pytest.approx(first + 2 * later + 3 * 1_000 * r.PRICE_OUT)
    assert ceiling == pytest.approx(3 * r.call_ceiling(100_000, 10_000, transport="claude_code"))
    assert ceiling > expected
