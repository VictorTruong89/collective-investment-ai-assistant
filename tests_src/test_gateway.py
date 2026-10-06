"""The LLM gateway — AC-0.4 … AC-0.13.

Tier: unit + API-contract (constitution §4).

★ Every test here is hermetic: `transport` is injected, so no test in this repo
makes a live API call. That is deliberate — a suite that spends money is a suite
someone eventually stops running.
"""

from __future__ import annotations

import json

import pytest

from src.shared.config import Config
from src.shared.errors import (
    BudgetExceededError,
    DecodingControlError,
    DriftBlockedError,
    RefusedError,
    TransportError,
    TruncatedError,
    UnparseableError,
)
from src.shared.llm.gateway import Gateway, Outcome, Tier, decoding_for

BASE = {
    "llm.deep.model_id": "claude-opus-5",
    "llm.deep.effort": "high",
    "llm.deep.thinking_mode": "adaptive",
    "llm.cheap.model_id": "claude-haiku-4-5",
    "llm.cheap.temperature": 0.0,
    "llm.budget.usd_per_run": 5.00,
    "llm.pricing.claude-opus-5.input_per_mtok": 5.0,
    "llm.pricing.claude-opus-5.output_per_mtok": 25.0,
    "llm.pricing.claude-haiku-4-5.input_per_mtok": 1.0,
    "llm.pricing.claude-haiku-4-5.output_per_mtok": 5.0,
}


def cfg(**over):
    values = dict(BASE)
    values.update(over)
    return Config(values, ["<test>"])


def ok_transport(**over):
    reply = {"text": '{"verdict": "HOLD"}', "stop_reason": "end_turn",
             "tokens_in": 1000, "tokens_out": 500}
    reply.update(over)
    seen = []

    def transport(request):
        seen.append(request)
        return reply

    transport.seen = seen
    return transport


def gw(config=None, **kw):
    kw.setdefault("transport", ok_transport())
    return Gateway(config or cfg(), **kw)


def send(gateway, tier=Tier.DEEP, **kw):
    kw.setdefault("prompt_name", "thesis.judgement")
    kw.setdefault("prompt_version", "v4")
    kw.setdefault("payload", {"bundle": "…"})
    kw.setdefault("max_tokens", 16000)
    kw.setdefault("run_id", "run-1")
    return gateway.call(tier=tier, **kw)


# --------------------------------------------------------------------------- #
# Decoding controls — §5.2a, the B0-blocking amendment
# --------------------------------------------------------------------------- #

def test_deep_tier_records_effort_and_never_temperature():
    """AC-0.4 — the control that APPLIES to the tier is what gets recorded."""
    d = decoding_for(Tier.DEEP, cfg())
    assert (d.control, d.effort, d.temperature) == ("effort", "high", None)


def test_cheap_tier_records_temperature_zero():
    """AC-0.4 — GW-8 survives the amendment, on the cheap tier."""
    d = decoding_for(Tier.CHEAP, cfg())
    assert (d.control, d.temperature, d.effort) == ("temperature", 0.0, None)


def test_deep_tier_sending_temperature_is_rejected_before_the_request_leaves():
    """AC-0.4a — ★ rejected by the rule, not by a provider 400.

    A 400 from Anthropic tells a reader that a parameter was wrong. This tells
    them WHICH RULE says so, which is the difference between a debugging session
    and a lookup.
    """
    with pytest.raises(DecodingControlError) as e:
        decoding_for(Tier.DEEP, cfg(**{"llm.deep.temperature": 0.0}))
    assert "GW-8a" in str(e.value) and "400" in str(e.value)


def test_omitted_effort_fails_the_call():
    """AC-0.4b — GW-9a: an omitted effort takes a provider default nobody controls."""
    with pytest.raises(DecodingControlError) as e:
        decoding_for(Tier.DEEP, cfg(**{"llm.deep.effort": None}))
    assert "GW-9a" in str(e.value)


def test_thinking_is_never_disabled_on_deep():
    """AC-0.4d — GW-9c: the failure is silent, which is why it is a rule.

    With thinking disabled, Opus 5 can write a tool call into visible text: the
    turn succeeds, the call never runs, no error is raised — and D-01's
    extraction presents as a document that said nothing.
    """
    with pytest.raises(DecodingControlError) as e:
        decoding_for(Tier.DEEP, cfg(**{"llm.deep.thinking_mode": "disabled"}))
    assert "visible text" in str(e.value).lower() or "GW-9c" in str(e.value)


def test_cheap_tier_with_no_temperature_fails():
    """GW-8 — an unset temperature is the maximum variance, chosen by omission."""
    with pytest.raises(DecodingControlError):
        decoding_for(Tier.CHEAP, cfg(**{"llm.cheap.temperature": None}))


def test_decoding_fingerprint_distinguishes_an_effort_change():
    """AC-0.4c (PARTIAL) — makes an effort change comparable across runs.

    ⚠ The re-baselining check itself is RM-5's and lives in D-01, which does not
    exist yet. This is the recording half only, and the AC is reported partial
    rather than green.
    """
    high = decoding_for(Tier.DEEP, cfg())
    xhigh = decoding_for(Tier.DEEP, cfg(**{"llm.deep.effort": "xhigh"}))
    assert high.fingerprint() != xhigh.fingerprint()


def test_the_request_carries_only_the_controls_the_model_accepts():
    """§5.2a — mutually exclusive controls, verified on the wire, not just in the record."""
    t = ok_transport()
    send(gw(transport=t), tier=Tier.DEEP)
    assert "temperature" not in t.seen[0] and t.seen[0]["effort"] == "high"

    t2 = ok_transport()
    send(gw(transport=t2), tier=Tier.CHEAP, max_tokens=256)
    assert "effort" not in t2.seen[0] and t2.seen[0]["temperature"] == 0.0


# --------------------------------------------------------------------------- #
# Alignment, model resolution, accounting
# --------------------------------------------------------------------------- #

def test_drifted_prompt_blocks_the_call_and_surfaces():
    """AC-0.7 — INV-9/GW-12/13: a check that logs and proceeds is no check."""
    t = ok_transport()
    g = gw(transport=t, alignment=lambda name, ver: False)
    with pytest.raises(DriftBlockedError):
        send(g)
    assert t.seen == []               # ★ no call was made at all


def test_model_id_is_resolved_from_config_and_recorded():
    """AC-0.6 — GW-5/6: a model that changed without the manifest changing makes
    every prior measurement incomparable and nothing would notice."""
    r = send(gw())
    assert r.call.model_id == "claude-opus-5"
    assert r.call.to_json_obj()["model_id"] == "claude-opus-5"


def test_prompt_version_is_required():
    """GW-14 — there is no unversioned call path."""
    with pytest.raises(ValueError):
        send(gw(), prompt_version="")


def test_tokens_and_cost_are_recorded_on_every_call():
    """AC-0.12 — GW-18: every dollar figure in L2 §7B depends on this."""
    r = send(gw())
    assert (r.call.tokens_in, r.call.tokens_out) == (1000, 500)
    # 1000/1e6*5 + 500/1e6*25 = 0.005 + 0.0125
    assert r.call.cost_usd == pytest.approx(0.0175)


def test_exceeding_the_declared_budget_fails_the_run():
    """AC-0.13 — GW-20: a budget that can be exceeded silently is not a budget."""
    g = gw(cfg(**{"llm.budget.usd_per_run": 0.02}))
    send(g)                                       # 0.0175 — fits
    with pytest.raises(BudgetExceededError) as e:
        send(g)                                   # 0.035 — does not
    assert "budget" in str(e.value).lower()


def test_ac_0_24_a_claude_code_call_is_priced_at_zero_BY_THE_GATEWAY():
    """AC-0.24 — GW-27, at the gateway and not only at one composition root.

    ⛔ Found 2026-10-04: `run_extraction_once` builds its own gateway with list prices, so a
    subscription call of $2.74 NOTIONAL was charged against the $2.00 run budget and its
    verified answer refused. ★ The response says which transport carried it; a `claude_code`
    response costs $0 of API money whatever the config's prices say."""
    big = ok_transport(tokens_in=400_000, tokens_out=40_000, transport="claude_code")
    g = gw(cfg(**{"llm.budget.usd_per_run": 0.02}), transport=big)
    send(g)
    send(g)                                   # ~$3 each at list price; $0 of spend
    assert all(c.cost_usd == 0.0 for c in g.calls)


def test_ac_0_24_an_api_call_is_still_priced_and_still_BUDGETED():
    """⚠ The exemption is the transport's, never a default: an API response is priced."""
    g = gw(cfg(**{"llm.budget.usd_per_run": 0.02}),
           transport=ok_transport(transport="anthropic_api"))
    send(g)
    with pytest.raises(BudgetExceededError):
        send(g)


def test_every_call_is_available_for_the_run_manifest():
    """AC-0.9, GW-16 — a retry invisible to the manifest makes a slow flaky run
    indistinguishable from a fast clean one."""
    g = gw()
    send(g)
    assert len(g.calls) == 1 and g.calls[0].attempts == 1
    json.dumps(g.calls[0].to_json_obj())          # must serialise for OR-9


# --------------------------------------------------------------------------- #
# Retry classification — GW-15/17, EH-15
# --------------------------------------------------------------------------- #

def test_a_transport_error_retries_and_then_succeeds():
    """AC-0.8 — retry the request that got no real answer."""
    calls = {"n": 0}

    def flaky(request):
        calls["n"] += 1
        if calls["n"] < 3:
            raise TransportError("429 rate limited")
        return {"text": "ok", "stop_reason": "end_turn", "tokens_in": 1, "tokens_out": 1}

    r = send(gw(transport=flaky))
    assert calls["n"] == 3 and r.call.attempts == 3
    assert len(r.call.retry_reasons) == 2


def test_retries_are_bounded():
    """GW-17 — bounded and backed off; it does not retry for ever."""
    def always_429(request):
        raise TransportError("503 unavailable")

    with pytest.raises(TransportError):
        send(gw(transport=always_429))


def test_an_unclassified_transport_error_is_not_retried():
    """GW-17 — EH-14's default: do not retry what you cannot classify."""
    calls = {"n": 0}

    def weird(request):
        calls["n"] += 1
        raise TransportError("something unexpected", retryable=True)

    with pytest.raises(TransportError):
        send(gw(transport=weird))
    assert calls["n"] == 1            # no hint matched -> not retried


@pytest.mark.parametrize("stop,err", [
    ("max_tokens", TruncatedError),
    ("refusal", RefusedError),
])
def test_semantic_failures_are_never_retried(stop, err):
    """AC-0.8, AC-0.10 — never retry the answer you disliked (EH-15, GW-15)."""
    t = ok_transport(stop_reason=stop)
    with pytest.raises(err):
        send(gw(transport=t))
    assert len(t.seen) == 1           # exactly one attempt


# --------------------------------------------------------------------------- #
# GW-22 — the guard this file exists for
# --------------------------------------------------------------------------- #

def test_a_truncated_response_is_a_failure_not_a_short_answer():
    """AC-0.10, GW-23 — incident one: a card built from a FAILED narrative."""
    with pytest.raises(TruncatedError) as e:
        send(gw(transport=ok_transport(stop_reason="max_tokens")))
    assert "not a short answer" in str(e.value)


def test_an_empty_response_is_a_failure_not_a_default():
    """AC-0.10, GW-22 — incident two: a card built from an ABSENT narrative."""
    with pytest.raises(UnparseableError) as e:
        send(gw(transport=ok_transport(text="")))
    assert "absent narrative" in str(e.value)


def test_a_schema_violation_raises_rather_than_returning_the_text():
    """AC-0.10, GW-3 — the gateway parses and raises; meaning is D-01's."""
    with pytest.raises(UnparseableError):
        send(gw(transport=ok_transport(text="not json")), schema=json.loads)


def test_outcome_has_no_partial_member():
    """★ AC-0.10 made structural — GW-22.

    The absence is the guard. Both real incidents in this repo came from
    treating a partial as a success, so the enum makes it unrepresentable
    rather than discouraged.
    """
    assert "partial" not in {o.value for o in Outcome}
    assert {o.value for o in Outcome} == {
        "ok", "transport_failed", "refused", "truncated", "unparseable", "drift_blocked",
    }


def test_a_failed_call_is_never_charged_to_the_budget():
    """GW-20 + GW-22 — a failure that consumed tokens is recorded, not billed as work."""
    g = gw(transport=ok_transport(stop_reason="max_tokens"))
    with pytest.raises(TruncatedError):
        send(g)
    assert g.spent_usd == 0.0 and g.calls == []


# --------------------------------------------------------------------------- #
# Boundary — §1.2
# --------------------------------------------------------------------------- #

def test_no_gateway_api_returns_a_business_value():
    """AC-0.3 — if one ever does, §1.2 has been broken.

    A Response carries text, a parsed payload and the call record. It carries no
    verdict, no score and no threshold — those would be D-00 holding a business
    rule that nobody owns and everybody obeys.
    """
    r = send(gw())
    assert set(r.__slots__) == {"text", "parsed", "call"}
