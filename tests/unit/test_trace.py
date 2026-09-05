"""F2 — execution trace & replay. `MS-3`.

Every test names the `AC-2.<k>` it satisfies. ⚠ F2 EXTENDS the existing run
record downward; it never writes a second run-level record (`AC-2.1`).
"""

from __future__ import annotations

import json

import pytest

from src.orchestration.trace import (
    CapabilityDelta,
    DecisionRecord,
    ExternalCall,
    IncompleteTrace,
    StepRecord,
    TraceImmutableError,
    TraceStore,
    mint_decision_id,
)


@pytest.fixture
def store(tmp_path) -> TraceStore:
    return TraceStore(tmp_path / "runs", run_id="2026-09-04T00:00:00Z-daily@v1-abc123")


def _step(**kw):
    base = dict(run_id="2026-09-04T00:00:00Z-daily@v1-abc123", job_id="j1", step_id="s1",
                node="analyze", started_at="2026-09-04T00:00:01Z",
                ended_at="2026-09-04T00:00:02Z", status="SUCCESS")
    base.update(kw)
    return StepRecord(**base)


# --------------------------------------------------------------------------- #
# AC-2.1 — extends, never duplicates
# --------------------------------------------------------------------------- #
def test_ac_2_1_every_record_carries_the_run_id_and_no_second_run_record(store):
    """AC-2.1 — F2 joins to RunManifest by run_id and writes no rival run record."""
    store.append(_step())
    written = list(store.read_all())
    assert written and all(r["run_id"] == store.run_id for r in written)
    files = {p.name for p in store.run_dir.iterdir()}
    assert "manifest.json" not in files, "F2 must never write a run-level record (P4, PG-8)"
    assert "trace.jsonl" in files


def test_ac_2_1_rejects_a_record_from_another_run(store):
    with pytest.raises(ValueError, match="run_id"):
        store.append(_step(run_id="some-other-run"))


# --------------------------------------------------------------------------- #
# AC-2.2 — both halves of every external call · D1 payload separation
# --------------------------------------------------------------------------- #
def test_ac_2_2_an_external_call_records_request_and_response(store):
    """AC-2.2 — a request without its response cannot be replayed."""
    store.append(ExternalCall(
        run_id=store.run_id, step_id="s1", call_id="c1", kind="llm",
        request={"prompt": "hello"}, response={"text": "hi"},
        model_id="claude-opus-5", latency_ms=12))
    call = [r for r in store.read_all() if r["type"] == "ExternalCall"][0]
    assert call["payload_ref"] == "c1", "D1 — the body lives beside the log, not in it"
    body = json.loads((store.payload_dir / "c1.json").read_text())
    assert body["request"] == {"prompt": "hello"} and body["response"] == {"text": "hi"}


def test_ac_2_2_a_call_with_neither_response_nor_error_is_refused(store):
    with pytest.raises(ValueError, match="response"):
        store.append(ExternalCall(run_id=store.run_id, step_id="s1", call_id="c2",
                                  kind="llm", request={"p": 1}, response=None,
                                  model_id="m", latency_ms=1))


def test_ac_2_2_an_errored_call_needs_no_response(store):
    store.append(ExternalCall(run_id=store.run_id, step_id="s1", call_id="c3", kind="llm",
                              request={"p": 1}, response=None, model_id="m",
                              latency_ms=1, error="timeout"))
    assert [r for r in store.read_all() if r["type"] == "ExternalCall"]


# --------------------------------------------------------------------------- #
# AC-2.5 / AC-2.6 — PG-9 and PG-5.2 completeness
# --------------------------------------------------------------------------- #
def test_ac_2_5_a_decision_record_is_complete(store):
    """AC-2.5 — PG-9: state, candidates, action, reason, propensity all present."""
    store.append(DecisionRecord(
        run_id=store.run_id, step_id="s1", decision_id="d1",
        state={"vol": 0.5}, candidates=["a", "b"], action="a",
        reason="realised_vol_60d > 0.45", propensity=1.0))
    rec = [r for r in store.read_all() if r["type"] == "DecisionRecord"][0]
    for f in ("state", "candidates", "action", "reason", "propensity"):
        assert rec[f] is not None


@pytest.mark.parametrize("missing", ["state", "candidates", "action", "reason", "propensity"])
def test_ac_2_5_an_incomplete_decision_is_refused(store, missing):
    kw = dict(run_id=store.run_id, step_id="s1", decision_id="d1", state={"v": 1},
              candidates=["a"], action="a", reason="because", propensity=1.0)
    kw[missing] = None
    with pytest.raises(ValueError, match=missing):
        store.append(DecisionRecord(**kw))


def test_ac_2_6_a_delta_is_written_even_when_nothing_changed(store):
    """AC-2.6 — ⚠ PG-5.2: the no-change cases are HALF the comparison.

    Dropping them biases the Tier-B study, and the bias is invisible: the
    surviving sample is exactly the subset where the capability did something.
    """
    store.append(CapabilityDelta(run_id=store.run_id, decision_id="d1",
                                 capability="deliberation", pre={"v": "BUY"},
                                 post={"v": "BUY"}, changed=False))
    d = [r for r in store.read_all() if r["type"] == "CapabilityDelta"][0]
    assert d["changed"] is False and d["pre"] == d["post"]


# --------------------------------------------------------------------------- #
# AC-2.13 / CT-2.7 — decision_id
# --------------------------------------------------------------------------- #
def test_ac_2_13_decision_id_is_minted_once_per_run_ticker_attempt():
    """AC-2.13 — CT-2.7's mint format, and a drill-down gets its OWN id."""
    a = mint_decision_id("run1", "NVDA", 1)
    assert a == "run1:NVDA:1"
    assert mint_decision_id("run1", "NVDA", 1) == a, "same inputs, same id"
    assert mint_decision_id("run1", "NVDA", 2) != a, "a drill-down is a separate analysis"


def test_ac_2_13_all_record_types_share_one_decision_id(store):
    did = mint_decision_id(store.run_id, "NVDA", 1)
    store.append(_step(decision_id=did))
    store.append(DecisionRecord(run_id=store.run_id, step_id="s1", decision_id=did,
                                state={}, candidates=["a"], action="a", reason="r",
                                propensity=1.0))
    store.append(CapabilityDelta(run_id=store.run_id, decision_id=did,
                                 capability="deliberation", pre={}, post={}, changed=False))
    ids = {r.get("decision_id") for r in store.read_all() if r.get("decision_id")}
    assert ids == {did}


def test_ac_2_1_a_run_scoped_step_may_carry_no_decision_id(store):
    """CT-2.1 — ⚠ nullable: price ingest is not about one ticker."""
    store.append(_step(step_id="s9", node="ingest_prices", decision_id=None))
    assert any(r["step_id"] == "s9" and r["decision_id"] is None for r in store.read_all())


# --------------------------------------------------------------------------- #
# AC-2.8 — append-only
# --------------------------------------------------------------------------- #
def test_ac_2_8_rewriting_a_record_id_raises_and_leaves_the_original(store):
    """AC-2.8 — OR-13's rule, inherited. ⚠ A trace that can be edited is not evidence."""
    store.append(_step(node="first"))
    with pytest.raises(TraceImmutableError):
        store.append(_step(node="second"))
    assert [r for r in store.read_all() if r["step_id"] == "s1"][0]["node"] == "first"


# --------------------------------------------------------------------------- #
# AC-2.12 — incomplete is loud
# --------------------------------------------------------------------------- #
def test_ac_2_12_an_unclosed_run_reads_as_incomplete(store):
    store.append(_step())
    assert store.status() == "INCOMPLETE"
    store.close(status="SUCCESS")
    assert store.status() == "SUCCESS"


def test_ac_2_12_a_truncated_log_line_is_detected(store):
    """⚠ D1 — JSONL's last line is whole or visibly truncated. That is why it was chosen."""
    store.append(_step())
    store.close(status="SUCCESS")
    with store.log_path.open("a") as fh:
        fh.write('{"type": "StepRecord", "run_i')
    with pytest.raises(IncompleteTrace):
        list(store.read_all())
