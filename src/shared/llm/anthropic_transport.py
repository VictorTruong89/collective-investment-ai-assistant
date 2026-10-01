"""D-00 — the Anthropic transport. GW-1, GW-8a, GW-23, SC-3.

★ **The gateway owns the policy; this owns the wire.** It converts one request
dict into one response dict and does nothing else — no retry (GW-15 is the
gateway's), no parsing (GW-22 is the gateway's), no judgement of any kind.

⚠ **`stop_reason` is passed through verbatim.** A transport that normalised
`max_tokens` into a short answer would destroy GW-23's ability to call a
truncation a failure — *a truncated response is a failure, not a short answer.*
"""

from __future__ import annotations

import json
from typing import Any


def _flatten(payload: Any) -> str:
    """The composed payload, as one user message.

    ⚠ **The bundle is serialised whole and in the order it arrives** — RM-1's
    `evidence_order` perturbation is applied upstream in `_compose`, and a
    transport that re-sorted anything would undo it silently.
    """
    if isinstance(payload, str):
        return payload
    prompt = payload.get("prompt", "")
    options = payload.get("options") or []
    bundle = payload.get("bundle") or {}
    lines = [prompt, ""]
    if options:
        lines += ["Options, in the order presented:", ", ".join(options), ""]
    lines += ["EVIDENCE BUNDLE:", json.dumps(bundle, indent=2, default=str)]
    return "\n".join(lines)


def make_transport(api_key, *, timeout: float = 300.0):
    """Return the callable `Gateway(transport=...)` expects.

    `api_key` is a `Secret` — ⚠ **SC-3/DE-8**: it is unwrapped here, at the wire,
    and never enters a log, an exception message or a manifest.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=api_key.reveal()
                                 if hasattr(api_key, "reveal") else str(api_key),
                                 timeout=timeout)

    def transport(request: dict) -> dict:
        from src.shared.errors import TransportError

        kwargs: dict = {
            "model": request["model"],
            "max_tokens": request["max_tokens"],
            "messages": [{"role": "user", "content": _flatten(request["payload"])}],
        }
        # ★★ GW-8a/9a/9c — the deep tier carries `effort` and ADAPTIVE thinking.
        #
        # ⚠ **The API states the shape and it is not the older one.** A first
        # attempt sent `thinking: {"type": "enabled", "budget_tokens": …}` and
        # got back, verbatim:
        #
        #     "thinking.type.enabled" is not supported for this model.
        #     Use "thinking.type.adaptive" and "output_config.effort"
        #
        # ★ That is GW-9a and GW-9c described by the server — `effort` is its
        # own block, and thinking is adaptive rather than budgeted. It also
        # confirms GW-8a's other half: the tier **rejects `temperature`**, so
        # the request never carries one.
        if "effort" in request:
            kwargs["output_config"] = {"effort": request["effort"]}
            thinking = request.get("thinking") or "adaptive"
            if thinking != "off":
                kwargs["thinking"] = {"type": thinking}
        elif "temperature" in request:
            kwargs["temperature"] = request["temperature"]

        try:
            message = client.messages.create(**kwargs)
        except Exception as exc:                            # noqa: BLE001
            # ⚠ The key must not reach the message. `anthropic` does not put it
            #   there, and this truncation is the belt to that brace (SC-3).
            raise TransportError(f"{type(exc).__name__}: {str(exc)[:200]}") from None

        text = "".join(block.text for block in message.content
                       if getattr(block, "type", "") == "text")
        return {
            "transport": "anthropic_api",           # GW-26
            "text": text,
            # ★ Verbatim — GW-23 needs to see `max_tokens` to call it a failure.
            "stop_reason": message.stop_reason,
            "tokens_in": message.usage.input_tokens,
            "tokens_out": message.usage.output_tokens,
        }

    return transport


class MappingConfig:
    """The `get`/`get_optional` surface the gateway reads (CF-*).

    ★ Flat dotted keys, so a missing one is a `KeyError` naming the key rather
    than a `None` that travels.
    """

    def __init__(self, values: dict) -> None:
        self._values = dict(values)

    def get(self, key: str):
        if key not in self._values:
            raise KeyError(
                f"config key {key!r} is not set — the gateway does not default "
                f"a model id, a price or a budget (GW-5, GW-18)")
        return self._values[key]

    def get_optional(self, key: str, default=None):
        return self._values.get(key, default)
