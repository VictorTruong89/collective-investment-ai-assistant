"""F2 — replay, redaction and retention. `AC-2.3`, `AC-2.4`, `AC-2.9`, `AC-2.14`–`AC-2.16`."""

from __future__ import annotations

import pytest

from src.orchestration.trace import (
    DecisionRecord,
    ExternalCall,
    StepRecord,
    TraceStore,
    replay,
)
from src.orchestration.trace.redact import (
    REDACTED,
    export_for_publication,
    redact_secrets,
)
from src.orchestration.trace.replay import SCOPE, NetworkReachedError

RUN = "2026-09-04T00:00:00Z-daily@v1-abc123"


@pytest.fixture
def recorded(tmp_path):
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(StepRecord(run_id=RUN, job_id="j1", step_id="s1", node="fetch",
                        started_at="2026-09-04T00:00:01Z", ended_at="2026-09-04T00:00:02Z",
                        status="SUCCESS"))
    s.append(ExternalCall(run_id=RUN, step_id="s1", call_id="c1", kind="llm",
                          request={"prompt": "why?"}, response={"text": "because"},
                          model_id="claude-opus-5", latency_ms=42))
    s.close(status="SUCCESS")
    return s


def _faithful(records, respond):
    """Re-executes by serving every external result from the recording."""
    out = []
    for r in records:
        r = dict(r)
        if r.get("type") == "ExternalCall":
            respond(r["payload_ref"])          # the only door to the outside
        out.append(r)
    return out


# --------------------------------------------------------------------------- #
# AC-2.3 — replay reproduces CONTROL FLOW, and says so
# --------------------------------------------------------------------------- #
def test_ac_2_3_a_faithful_replay_is_reproduced(recorded):
    rep = replay(recorded, _faithful)
    assert rep.verdict == "REPRODUCED"
    assert rep.first_divergence is None


def test_ac_2_3_the_verdict_carries_its_own_scope(recorded):
    """★ D3 / PG-10 — the verdict travels into reports, so its limit travels too."""
    rep = replay(recorded, _faithful)
    assert rep.scope == SCOPE
    assert "given recorded external responses" in rep.scope
    assert rep.verdict != "IDENTICAL", "D3 renamed it; `identical` over-claims"


def test_ac_2_3_replay_reaches_no_network(recorded):
    """⚠ A replay that reaches the network has failed, by definition."""
    def cheats(records, respond):
        raise NetworkReachedError("live call attempted during replay")
    with pytest.raises(NetworkReachedError):
        replay(recorded, cheats)


def test_ac_2_16_excluded_wall_clock_fields_are_listed(recorded):
    """AC-2.16 / D5 — an invisible exclusion is a lie."""
    rep = replay(recorded, _faithful)
    assert "started_at" in rep.excluded_fields and "ended_at" in rep.excluded_fields


def test_ac_2_3_a_clock_difference_alone_does_not_diverge(recorded):
    """D5 — 43 wall-clock sites are not covered by `seed`; they must not create noise."""
    def later(records, respond):
        out = []
        for r in records:
            r = dict(r)
            if "started_at" in r:
                r["started_at"] = "2027-01-01T00:00:00Z"
            if r.get("type") == "ExternalCall":
                respond(r["payload_ref"])
            out.append(r)
        return out
    assert replay(recorded, later).verdict == "REPRODUCED"


# --------------------------------------------------------------------------- #
# AC-2.4 — divergence is LOCATED
# --------------------------------------------------------------------------- #
def test_ac_2_4_divergence_names_the_first_step_and_field(recorded):
    def changed(records, respond):
        out = []
        for r in records:
            r = dict(r)
            if r.get("type") == "StepRecord":
                r["node"] = "fetch_v2"
            if r.get("type") == "ExternalCall":
                respond(r["payload_ref"])
            out.append(r)
        return out
    rep = replay(recorded, changed)
    assert rep.verdict == "DIVERGED"
    assert rep.first_divergence["field"] == "node"
    assert rep.first_divergence["recorded"] == "fetch"
    assert rep.first_divergence["replayed"] == "fetch_v2"
    assert rep.first_divergence["step_id"] == "s1"


def test_ac_2_12_an_unclosed_run_is_unreplayable(tmp_path):
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(StepRecord(run_id=RUN, job_id="j", step_id="s1", node="n",
                        started_at="t", status="INCOMPLETE"))
    rep = replay(s, _faithful)
    assert rep.verdict == "UNREPLAYABLE" and "INCOMPLETE" in rep.reason


# --------------------------------------------------------------------------- #
# AC-2.15 — expiry is recorded, never silent
# --------------------------------------------------------------------------- #
def test_ac_2_15_expired_payloads_are_unreplayable_and_say_why(recorded):
    """⚠ Deleted, not lost. Silence would read as corruption."""
    recorded.expire_payloads("2027-09-04")
    rep = replay(recorded, _faithful)
    assert rep.verdict == "UNREPLAYABLE"
    assert "expired" in rep.reason and "2027-09-04" in rep.reason


def test_ac_2_15_expiry_keeps_every_record(recorded):
    """D2 — decisions and deltas are permanent; only raw bodies go."""
    before = len(list(recorded.read_all()))
    recorded.expire_payloads("2027-09-04")
    assert len(list(recorded.read_all())) == before


# --------------------------------------------------------------------------- #
# AC-2.9 / AC-2.14 — secrets vs sensitive
# --------------------------------------------------------------------------- #
def test_ac_2_9_a_credential_never_reaches_the_disk(tmp_path):
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(ExternalCall(run_id=RUN, step_id="s1", call_id="c1", kind="http",
                          request={"headers": {"Authorization": "Bearer sk-abcdefgh12345"}},
                          response={"ok": True}, model_id=None, latency_ms=1))
    on_disk = (s.log_path.read_text() + (s.payload_dir / "c1.json").read_text())
    assert "sk-abcdefgh12345" not in on_disk
    assert REDACTED in on_disk


def test_ac_2_9_a_credential_in_a_NON_call_record_is_also_redacted(tmp_path):
    """AC-2.9 — ⚠ the log path, not just the payload path.

    Found by mutation: removing `redact_secrets` from the log write left every
    test passing, because the only secret under test lived in an ExternalCall
    payload — which is redacted on a DIFFERENT code path. A credential in a
    DecisionRecord's `state` would have been written verbatim, unnoticed.
    ★ Two code paths need two tests; one of them was doing all the work.
    """
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(DecisionRecord(run_id=RUN, step_id="s1", decision_id="d1",
                            state={"vendor_token": "sk-secretvalue999", "vol": 0.5},
                            candidates=["a"], action="a", reason="r", propensity=1.0))
    log = s.log_path.read_text()
    assert "sk-secretvalue999" not in log
    assert REDACTED in log
    assert "0.5" in log, "redaction must not eat ordinary state"


def test_ac_2_9_a_secret_shaped_value_is_scrubbed_even_under_a_harmless_key(tmp_path):
    """⚠ Key-name matching alone is not enough — the VALUE is scrubbed too."""
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(StepRecord(run_id=RUN, job_id="j", step_id="s2", node="sk-abcdefgh12345",
                        started_at="t", status="SUCCESS"))
    assert "sk-abcdefgh12345" not in s.log_path.read_text()


def test_ac_2_14_positions_are_written_in_full(tmp_path):
    """★★ Redacting at write would BREAK REPLAY — positions are inputs."""
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(ExternalCall(run_id=RUN, step_id="s1", call_id="c1", kind="tool",
                          request={"positions": {"NVDA": 100}}, response={"ok": True},
                          model_id=None, latency_ms=1))
    body = s.payload(call_id="c1")
    assert body["request"]["positions"] == {"NVDA": 100}


def test_ac_2_14_export_removes_positions_but_the_local_trace_keeps_them(tmp_path):
    s = TraceStore(tmp_path / "runs", run_id=RUN)
    s.append(ExternalCall(run_id=RUN, step_id="s1", call_id="c1", kind="tool",
                          request={"positions": {"NVDA": 100}, "pnl": -12.5},
                          response={"ok": True}, model_id=None, latency_ms=1))
    exported = export_for_publication(s.payload("c1"))
    assert exported["request"]["positions"] == REDACTED
    assert exported["request"]["pnl"] == REDACTED
    assert s.payload("c1")["request"]["positions"] == {"NVDA": 100}, "local stays complete"


def test_redaction_leaves_ordinary_fields_alone():
    obj = {"ticker": "NVDA", "reason": "vol > 0.45", "api_key": "sk-zzzz1111"}
    out = redact_secrets(obj)
    assert out["ticker"] == "NVDA" and out["reason"] == "vol > 0.45"
    assert out["api_key"] == REDACTED


# --------------------------------------------------------------------------- #
# AC-2.2 at CALL granularity — the gateway's vendor boundary
# --------------------------------------------------------------------------- #
def test_ac_2_2_a_gateway_transport_call_is_recorded_with_both_halves(tmp_path):
    """★ `traced_transport` closes what `traced()` cannot see.

    ⚠ Zero edits to the inherited gateway: `Gateway(config, transport=...)`
    injects the vendor boundary, so wrapping the transport is enough.
    """
    from src.orchestration.trace import traced_transport

    s = TraceStore(tmp_path / "runs", run_id=RUN)
    calls = []

    def transport(request):
        calls.append(request)
        return {"model": "claude-opus-5", "content": [{"text": "hi"}],
                "usage": {"input_tokens": 12, "output_tokens": 3}}

    wrapped = traced_transport(transport, s, step_id="job:thesis")
    out = wrapped({"model": "claude-opus-5", "messages": [{"role": "user"}]})

    assert out["content"][0]["text"] == "hi", "the transport's result passes through"
    rec = [r for r in s.read_all() if r["type"] == "ExternalCall"][0]
    assert rec["kind"] == "llm" and rec["model_id"] == "claude-opus-5"
    assert rec["tokens"] == {"input": 12, "output": 3}
    body = s.payload(rec["payload_ref"])
    assert body["request"]["messages"] == [{"role": "user"}]
    assert body["response"]["content"] == [{"text": "hi"}]


def test_ac_2_2_a_failing_transport_is_recorded_AND_re_raised(tmp_path):
    """⚠⚠ The gateway's own retry must still see the exception.

    `EH-14` — only orchestration retries. A recorder that swallowed this would
    change WHICH calls get retried, which is a recorder altering the run.
    """
    from src.orchestration.trace import traced_transport

    s = TraceStore(tmp_path / "runs", run_id=RUN)

    def boom(_request):
        raise TimeoutError("vendor timeout")

    wrapped = traced_transport(boom, s, step_id="job:thesis")
    with pytest.raises(TimeoutError):
        wrapped({"model": "claude-opus-5"})

    rec = [r for r in s.read_all() if r["type"] == "ExternalCall"][0]
    assert "TimeoutError" in rec["error"]
    assert rec["payload_ref"], "the request is kept even though there is no response"


def test_ac_2_9_a_credential_in_a_transport_request_is_redacted(tmp_path):
    """The vendor boundary is exactly where an API key would appear."""
    from src.orchestration.trace import traced_transport

    s = TraceStore(tmp_path / "runs", run_id=RUN)
    wrapped = traced_transport(lambda r: {"ok": True}, s, step_id="job:x")
    wrapped({"headers": {"x-api-key": "sk-livesecret12345"}, "model": "m"})
    assert "sk-livesecret12345" not in (s.log_path.read_text()
                                        + (s.payload_dir / "job:x:llm:1.json").read_text())


# --------------------------------------------------------------------------- #
# ⚠⚠ regression — redaction must not eat usage accounting
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("key", ["tokens", "max_tokens", "input_tokens",
                                 "tokens_in", "output_tokens", "token_count"])
def test_ac_2_9_usage_fields_are_NOT_redacted(key):
    """⚠⚠ `"token" in "tokens"` is True.

    The substring form redacted **every usage and cost field in every traced
    call** — `tokens`, `max_tokens`, `input_tokens` — and the trace would have
    reported `<redacted>` where the accounting should be. ★ Caught only because
    a call-level test asserted an exact token count.
    """
    assert redact_secrets({key: 42})[key] == 42


@pytest.mark.parametrize("key", ["api_key", "x-api-key", "X-API-Key", "auth_token",
                                 "authorization", "password", "client_secret",
                                 "private_key", "bearer"])
def test_ac_2_9_credential_shaped_keys_ARE_redacted(key):
    """★ And the fix must not weaken the rule it was fixing.

    `x-api-key` is the interesting one: the substring form MISSED it (hyphen vs
    underscore) and was relying on the value regex to catch the leak.
    """
    assert redact_secrets({key: "hunter2"})[key] == REDACTED
