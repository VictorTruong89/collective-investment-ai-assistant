"""CHARACTERIZATION — the inherited LLM gateway's transport contract.

⚠⚠ **This test FREEZES behaviour. It does not claim the behaviour is correct.**

★ **Why this contract.** `src/orchestration/trace/wire.py::traced_transport`
wraps `Gateway(config, transport=...)` to satisfy `AC-2.2` at call granularity,
and that wrapper depends on three things nobody had written down:

  1. the gateway calls `transport(request)` with a **dict** carrying at least
     `model`, `max_tokens` and `payload`;
  2. the transport's return dict is read for **`tokens_in` / `tokens_out`** —
     *not* `usage.input_tokens`;
  3. a `TransportError` raised by the transport is **caught and retried** by the
     gateway, so a wrapper must re-raise rather than swallow.

⚠⚠ **Point 2 is why this file exists.** The first version of `traced_transport`
read `usage.input_tokens` — the Anthropic SDK's shape — and would have recorded
**0 tokens on every real call**. Its unit test passed because the test invented
the same shape the wrapper assumed. ★ A characterization test reads the
*inherited* code instead of the author's memory of it, which is the whole point
of constitution §5 item 3: **freeze inherited behaviour before building near it.**

⚠ `DX-11`: this and `test_characterization_orchestrator.py` cover the two
inherited contracts this repo's own code actually relies on today. Other
inherited surfaces are not frozen — and are also **not yet consumed**.
"""

from __future__ import annotations

import contextlib

import pytest

from src.orchestration.trace import TraceStore, traced_transport
from src.shared.config import Config
from src.shared.errors import TransportError
from src.shared.llm.gateway import Gateway, Tier

#: ⚠⚠ FROZEN, and BOTH halves were assumed wrong on the first draft:
#:  1. keys are **flat dotted paths** (`llm.cheap.model_id`), not a nested
#:     `llm.tiers` mapping (`CF-4` — "a manifest entry names one value rather
#:     than a nested blob a reader has to search");
#:  2. the gateway needs a real **`Config`**, not a `dict` — it calls
#:     `get_optional`, and a dict raises `AttributeError` deep inside the call.
CONFIG = Config(
    {
        "llm.budget.usd_per_run": 10.0,
        "llm.cheap.model_id": "claude-haiku-4-5",
        "llm.deep.model_id": "claude-opus-5",
        # ⚠ FROZEN (GW-8): a cheap-tier call MUST set temperature explicitly —
        # "an unset temperature runs at the provider default", which would make
        # two runs of the same prompt differ for a reason nobody recorded.
        # ★ And the mirror (GW-9): the DEEP tier must NOT set temperature, because
        # claude-opus-5 rejects it with a 400. The gateway raises before the
        # request leaves, so the failure names the rule instead of arriving as a
        # provider error a reader has to decode.
        "llm.cheap.temperature": 0.0,
    },
    sources=("characterization-test",),
)


def _call(g, **kw):
    """FROZEN: `call` is keyword-only and requires `tier`, `max_tokens`, `run_id`."""
    base = dict(prompt_name="p", prompt_version="1", tier=Tier.CHEAP,
                payload={"prompt": "hi"}, max_tokens=512, run_id="r1")
    return g.call(**{**base, **kw})


def _gateway(transport, *, config=None, **kw):
    return Gateway(config or CONFIG, transport=transport, **kw)


def test_characterization_the_transport_receives_a_dict_with_model_and_payload():
    """FROZEN: `transport(request)` — one positional dict, not kwargs."""
    seen = {}

    def transport(request):
        seen.update(request)
        return {"text": "ok", "tokens_in": 10, "tokens_out": 2}

    # ⚠ We are freezing the CALL SHAPE, not the outcome — the response is a stub
    # and downstream validation may reject it. `suppress` says that deliberately.
    g = _gateway(transport)
    with contextlib.suppress(Exception):
        _call(g)
    assert "model" in seen and "max_tokens" in seen and "payload" in seen
    assert seen["payload"] == {"prompt": "hi"}


def test_characterization_token_counts_are_read_as_tokens_in_tokens_out():
    """⚠⚠ FROZEN: `tokens_in` / `tokens_out` — NOT `usage.input_tokens`.

    ★ This is the assumption that was wrong in `traced_transport`'s first draft.
    """
    from src.orchestration.trace.wire import _tokens_of

    assert _tokens_of({"tokens_in": 7, "tokens_out": 3}) == {"input": 7, "output": 3}
    # and the SDK shape still works, for a transport that returns one unwrapped
    assert _tokens_of({"usage": {"input_tokens": 5, "output_tokens": 1}}) == {
        "input": 5, "output": 1}
    assert _tokens_of(None) == {"input": 0, "output": 0}


def test_characterization_a_transport_error_is_retried_not_propagated(tmp_path):
    """FROZEN: the gateway owns the retry (`GW-15`/`EH-15`).

    ⚠ So `traced_transport` must **re-raise**: swallowing would remove the
    gateway's ability to retry, and a recorder that changes retry behaviour is
    not an observer.
    """
    attempts = {"n": 0}

    def flaky(_request):
        attempts["n"] += 1
        raise TransportError("timeout", retryable=True)

    store = TraceStore(tmp_path / "runs", run_id="run-char")
    wrapped = traced_transport(flaky, store, step_id="job:thesis")
    g = _gateway(wrapped, max_attempts=3)
    with pytest.raises(TransportError):
        _call(g)

    assert attempts["n"] > 1, "the gateway retried — the wrapper did not block it"
    calls = [r for r in store.read_all() if r["type"] == "ExternalCall"]
    assert len(calls) == attempts["n"], "every attempt is recorded, not just the last"
    assert all("TransportError" in c["error"] for c in calls)


def test_characterization_gw8_cheap_requires_temperature_and_gw9_deep_forbids_it():
    """FROZEN: the two decoding rules, and that both fail BEFORE the request leaves.

    ⚠ Not endorsed — frozen. ★ Failing early is the valuable half: a provider
    400 would have to be decoded by whoever reads the log.
    """
    from src.shared.errors import DecodingControlError

    no_temp = Config({"llm.budget.usd_per_run": 10.0,
                      "llm.cheap.model_id": "claude-haiku-4-5"},
                     sources=("t",))
    with pytest.raises(DecodingControlError, match="GW-8"):
        _call(_gateway(lambda r: {"text": "x"}, config=no_temp))

    deep_temp = Config({"llm.budget.usd_per_run": 10.0,
                        "llm.deep.model_id": "claude-opus-5",
                        "llm.deep.temperature": 0.5}, sources=("t",))
    with pytest.raises(DecodingControlError):
        _call(_gateway(lambda r: {"text": "x"}, config=deep_temp), tier=Tier.DEEP)
