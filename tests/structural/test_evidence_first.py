"""F13 `D14` / AC-F13.20 — evidence first in the extraction and Stage-A calls (Victor 2026-10-22).

★ The same bytes, moved: the evidence becomes the request's `cache_prefix` (GW-30) and the
instructions follow, so the 7 filing extractions and the 9 Stage-A calls can reuse one cached
bundle. Opt-in by `--cache-evidence`; without it every runner sends what it always sent.
"""

from __future__ import annotations

import json

import pytest

from src.shared.llm.anthropic_transport import _flatten
from tests.structural.test_judgement_runner_extractions import _j06_evidence, roots  # noqa: F401
import tools.run_judgement_once as rj

PAYLOAD = {"prompt": "TASK: extract", "options": ["a", "b"],
           "bundle": {"ticker": "MU", "parts": [{"content": "FILING BODY"}]}}


# ── the split ────────────────────────────────────────────────────────────────

def test_ac_f13_20_the_split_moves_bytes_and_adds_none():
    """AC-F13.20 — prefix + rest are exactly what `_flatten` sent, reordered."""
    from tools.llm_transport import split_evidence

    prefix, rest = split_evidence(PAYLOAD)
    assert prefix.startswith("EVIDENCE BUNDLE:") and "FILING BODY" in prefix
    assert "FILING BODY" not in rest and rest.startswith("TASK: extract")
    assert f"{rest}\n\n{prefix}" == _flatten(PAYLOAD)


def test_ac_f13_20_a_payload_with_no_evidence_is_refused():
    """AC-F13.20 (P5) — nothing to move is a wiring error, never a silent pass-through."""
    from tools.llm_transport import split_evidence

    with pytest.raises(ValueError, match="EVIDENCE BUNDLE"):
        split_evidence("a plain string payload")


def test_ac_f13_20_the_adapter_sends_the_evidence_as_the_prefix():
    """AC-F13.20 — the request below the adapter carries `cache_prefix` and a string rest."""
    from tools.llm_transport import evidence_first

    seen = []
    send = evidence_first(lambda r: seen.append(r) or {"text": "{}"})
    send({"model": "m", "max_tokens": 1, "payload": PAYLOAD, "effort": "high"})
    (req,) = seen
    assert req["cache_prefix"].startswith("EVIDENCE BUNDLE:")
    assert req["payload"].startswith("TASK: extract") and req["effort"] == "high"


# ── the extraction family ────────────────────────────────────────────────────

def test_ac_f13_20_every_extraction_run_hands_over_the_SAME_family():
    """AC-F13.20 (GW-31) — one family for all of `D8`, keyed by block, so seven separate
    processes send one tools segment."""
    from src.fundamental.on_demand.chain import E_BLOCKS
    from tools.anthropic_transport import extraction_tool
    from tools.run_extraction_once import BLOCKS, extraction_family

    family = extraction_family()
    assert list(family) == list(E_BLOCKS)
    for b in E_BLOCKS:
        assert family[b] == extraction_tool(BLOCKS[b][1])
    assert json.dumps(extraction_family(), sort_keys=True) == json.dumps(family, sort_keys=True)


# ── the Stage-A runner, end to end ───────────────────────────────────────────

def _live(roots, tmp_path, monkeypatch, *flags):  # noqa: F811
    import tools.anthropic_transport as at
    import tools.llm_transport as llm

    seen = {}

    def capture(*, family=None, family_key=None, tool=None, max_output=0, **_k):
        seen.update(family=family, family_key=family_key, tool=tool)

        def transport(request):
            seen["request"] = request
            enum = tool["input_schema"]["properties"]["criterion"]["enum"]
            return {"text": json.dumps({"criterion": enum[0], "why": "w",
                                        "what_would_move_it_down": "x"}),
                    "stop_reason": "tool_use", "tokens_in": 1, "tokens_out": 1}
        return transport

    monkeypatch.delenv("CIA_LLM_TRANSPORT", raising=False)
    monkeypatch.setattr(llm, "dev_transport", capture)
    monkeypatch.setattr(at, "anthropic_transport", lambda **_: pytest.fail("API built"))
    monkeypatch.setattr(rj, "REPO", tmp_path)
    monkeypatch.setattr("sys.argv", ["x", "--live", "--block", "J-06", "--seed", "t",
                                     *flags, "--extractions", *_j06_evidence(roots)])
    assert rj.main() == 0
    return seen


def test_ac_f13_20_stage_a_sends_the_blind_bundle_first(roots, tmp_path, monkeypatch):  # noqa: F811
    """AC-F13.20 — the evidence is the prefix; instructions and the rubric follow."""
    seen = _live(roots, tmp_path, monkeypatch, "--cache-evidence")
    req = seen["request"]
    cap = rj._rubric_for("J-06")
    assert req["cache_prefix"] and "TASK TYPE: JUDGEMENT" not in req["cache_prefix"]
    assert "TASK TYPE: JUDGEMENT" in req["payload"]
    for lv in cap.levels:
        assert lv.criterion in req["payload"], "the rubric stays with the instructions"
    assert req["cache_prefix"] not in req["payload"]
    assert seen["family_key"] == "J-06" and seen["family"]["J-06"] == seen["tool"]


def test_ac_f13_20_without_the_flag_stage_a_sends_what_it_always_sent(roots, tmp_path,  # noqa: F811
                                                                      monkeypatch):
    """AC-F13.20 / AC-F13.9 — no flag, no prefix, no family: the old request."""
    seen = _live(roots, tmp_path, monkeypatch)
    assert "cache_prefix" not in seen["request"]
    assert seen["family"] is None
    assert "TASK TYPE: JUDGEMENT" in seen["request"]["payload"]


# ── the chain passes it ──────────────────────────────────────────────────────

def test_ac_f13_20_thesis_for_passes_the_flag_to_every_extraction_and_stage_a(tmp_path):
    """AC-F13.20 — `D14` binds on the live chain, and only there."""
    from tests_src.test_thesis_for import FakeRunners, _chain, _repo

    runners = FakeRunners()
    rc, _manifest, _ = _chain(_repo(tmp_path), runners)
    assert rc == 0
    sent = [(k, a) for k, a in runners.calls if k in ("extract", "stage_a")]
    assert sent and all("--cache-evidence" in a for _k, a in sent)
    assert all("--cache-evidence" not in a for k, a in runners.calls if k == "thesis")
