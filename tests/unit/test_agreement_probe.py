"""`tools/agreement_probe.py` — did a prompt change MOVE an answer, or is it noise?

`L8` §9 rule 4ⓑ / `L3` §2.1p item 4 (2026-10-01). ★ A single re-run after a prompt
edit cannot separate a moved answer from a different draw (`DX-74`: two runs of one
prompt 82 minutes apart differed). The probe re-sends ONE recorded call k times
per arm, changing only the block's prompt text, and compares the DECISION fields.

⚠⚠ No test here makes a live call: every transport is a fake.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tools import agreement_probe as ap

SCHEMA = {"type": "object", "properties": {
    "verdict": {"type": "string", "enum": ["BUY", "HOLD", "SELL"]},
    "none_found": {"type": "boolean"},
    "items": {"type": "array", "items": {"type": "object", "properties": {
        "kind": {"type": "string", "enum": ["a", "b"]}, "why": {"type": "string"}}}},
    "answer": {"type": "string"}}}


# ── what counts as a decision ───────────────────────────────────────────────

def test_decision_fields_are_the_closed_answers_never_the_prose():
    fields = ap.decision_fields(SCHEMA, {
        "verdict": "SELL", "none_found": False, "answer": "long prose",
        "items": [{"kind": "b", "why": "x"}, {"kind": "a", "why": "y"}]})
    assert fields == {"verdict": "SELL", "none_found": False,
                      "items[].kind": ("a", "b"), "items[]#": 2}


# ── the pre-registered rule ─────────────────────────────────────────────────

@pytest.mark.parametrize("a,b,expected", [
    (["SELL"] * 3, ["SELL"] * 3, ap.SAME),
    (["SELL", "SELL", "HOLD"], ["SELL", "HOLD", "SELL"], ap.SAME),     # same modal
    (["SELL"] * 3, ["HOLD"] * 3, ap.MOVED),                           # unanimous both, differ
    (["SELL", "SELL", "HOLD"], ["HOLD"] * 3, ap.UNCLEAR),             # one arm split
    (["SELL", "HOLD", "BUY"], ["HOLD", "BUY", "SELL"], ap.UNCLEAR),   # no modal at all
])
def test_the_rule_calls_a_move_only_when_both_arms_are_unanimous(a, b, expected):
    assert ap.compare(a, b)["result"] == expected


def test_agreement_is_the_modal_fraction():
    assert ap.compare(["SELL", "SELL", "HOLD"], ["SELL"] * 3)["agreement"] == (2 / 3, 1.0)


# ── the probe itself ────────────────────────────────────────────────────────

class FakeTransport:
    """Answers by arm: the payload tells it which prompt text it was given."""

    def __init__(self, answers_by_text):
        self.answers_by_text, self.sent = answers_by_text, []

    def __call__(self, request):
        self.sent.append(request)
        for marker, answer in self.answers_by_text.items():
            if marker in request["payload"]:
                return {"text": json.dumps(answer), "stop_reason": "tool_use",
                        "tokens_in": 1, "tokens_out": 1, "transport": "claude_code"}
        raise AssertionError("payload carried neither prompt text")


def _recorded(tmp_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "judge:D:J-16:llm:1.json"
    path.write_text(json.dumps({
        "request": {"model": "claude-opus-5", "max_tokens": 32000, "effort": "medium",
                    "payload": "BUNDLE … OLD PROMPT TEXT … INSTRUCTIONS"},
        "response": {"text": json.dumps({"verdict": "SELL", "none_found": False,
                                         "items": [], "answer": "a"}),
                     "stop_reason": "tool_use"}}))
    return path


def test_arm_a_reuses_the_recording_and_arm_b_changes_only_the_prompt_text(tmp_path):
    fake = FakeTransport({"OLD PROMPT TEXT": {"verdict": "SELL", "none_found": False,
                                              "items": [], "answer": "x"},
                          "NEW PROMPT TEXT": {"verdict": "HOLD", "none_found": False,
                                              "items": [], "answer": "y"}})
    report = ap.probe(_recorded(tmp_path), old_text="OLD PROMPT TEXT",
                      new_text="NEW PROMPT TEXT", schema=SCHEMA, k=3, transport=fake)
    assert len(fake.sent) == 5, "arm A reuses the recorded answer: 2 + 3 new calls"
    for request in fake.sent:                       # ★ nothing else may vary between arms
        assert (request["model"], request["effort"], request["max_tokens"]) == (
            "claude-opus-5", "medium", 32000)
    assert report["fields"]["verdict"]["result"] == ap.MOVED
    assert report["fields"]["none_found"]["result"] == ap.SAME
    assert report["arms"]["A"]["calls"] == 2 and report["arms"]["B"]["calls"] == 3


def test_a_noise_floor_run_needs_no_new_text(tmp_path):
    """`new_text=None` measures one prompt's own run-to-run spread (arm A only)."""
    fake = FakeTransport({"OLD PROMPT TEXT": {"verdict": "SELL", "none_found": True,
                                              "items": [], "answer": "x"}})
    report = ap.probe(_recorded(tmp_path), old_text="OLD PROMPT TEXT", new_text=None,
                      schema=SCHEMA, k=3, transport=fake)
    assert len(fake.sent) == 2 and "B" not in report["arms"]
    assert report["fields"]["verdict"]["agreement"] == (1.0,)
    assert report["fields"]["none_found"]["distribution"] == [{"False": 1, "True": 2}]


def test_the_old_text_must_be_in_the_recorded_payload_exactly_once(tmp_path):
    """⚠ Otherwise the 'new' arm would be sending a different prompt than claimed."""
    fake = FakeTransport({})
    with pytest.raises(ValueError, match="exactly once"):
        ap.probe(_recorded(tmp_path), old_text="NOT THERE", new_text="NEW",
                 schema=SCHEMA, k=3, transport=fake)
    assert fake.sent == []


def test_a_truncated_or_unparseable_answer_is_reported_not_counted(tmp_path):
    class Truncating(FakeTransport):
        def __call__(self, request):
            self.sent.append(request)
            return {"text": "", "stop_reason": "max_tokens", "tokens_in": 1, "tokens_out": 1}

    report = ap.probe(_recorded(tmp_path), old_text="OLD PROMPT TEXT", new_text=None,
                      schema=SCHEMA, k=3, transport=Truncating({}))
    assert report["arms"]["A"]["failed"] == 2
    assert report["fields"]["verdict"]["result"] == ap.UNCLEAR, "1 usable answer decides nothing"


def test_k_below_three_is_refused():
    """RM-1's `K_STAB`: fewer runs than this cannot show agreement."""
    with pytest.raises(ValueError, match="k"):
        ap.probe(pathlib.Path("x"), old_text="a", new_text="b", schema=SCHEMA, k=2,
                 transport=FakeTransport({}))


def test_the_j15_arms_answer_through_their_own_versions_schema():
    """v1 has no `test`; comparing v1 with v2 must not force v1 to answer v2's schema."""
    from tools.run_thesis_once import thesis_tool

    item = lambda v: thesis_tool("J-15", observables=("GrossProfit",),  # noqa: E731
                                 j15_version=v)["input_schema"]["properties"]["falsifiers"]["items"]
    assert "test" not in item("v1")["properties"] and "test" in item("v2")["properties"]
