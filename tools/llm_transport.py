"""Which transport a development runner uses — GW-24 at the composition root.

★ **Default: `claude_code`** — headless Claude Code on the subscription. Set
`CIA_LLM_TRANSPORT=anthropic_api` to use the paid API path (reserved for the
real daily runs, `CLAUDE.md` 2026-10-01).

`dev_transport(**kwargs)` takes exactly the arguments `anthropic_transport`
takes, so a runner switches by changing one name. ⚠ The API factory is looked
up at CALL time, so tests that monkeypatch `tools.anthropic_transport.
anthropic_transport` still intercept it.
"""

from __future__ import annotations

from collections.abc import Callable

from src.shared.llm.claude_code_transport import (
    ANTHROPIC_API,
    MODEL_MAX_OUTPUT,
    make_claude_code_transport,
    selected_transport,
)


def is_paid() -> bool:
    """True only on the API path. A `claude_code` call costs no API dollars (GW-27)."""
    return selected_transport() == ANTHROPIC_API


def price_factor() -> float:
    """Multiply a dollar figure by this: 1.0 on the API, 0.0 on the subscription."""
    return 1.0 if is_paid() else 0.0


def dev_transport(*, family: dict[str, dict] | None = None, family_key: str | None = None,
                  **kwargs) -> Callable[[dict], dict]:
    """The transport for a development runner, chosen by `CIA_LLM_TRANSPORT`.

    `family` — `{key: tool}` for every tool the run's calls answer through (GW-31), and
    `family_key` the one this call fills (default: the tool's own name). On the
    subscription every call then sends one schema, so the cached prefix is shared;
    ⚠ the API path ignores it and keeps its per-call strict tool (`DX-185`).
    """
    if is_paid():
        import tools.anthropic_transport as api
        return api.anthropic_transport(**kwargs)
    tool = kwargs.get("tool")
    keyed = bool(family and tool)
    # `thinking_display` is an API-only diagnostic (DX-96); the CLI shows no thinking.
    return make_claude_code_transport(
        json_schema=tool["input_schema"] if tool else None,
        schema_family={k: t["input_schema"] for k, t in family.items()} if keyed else None,
        schema_name=(family_key or tool["name"]) if keyed else None,
        max_output=kwargs.get("max_output", MODEL_MAX_OUTPUT))


#: The marker `_flatten` writes before the bundle — the line the split is made at.
EVIDENCE_MARKER = "EVIDENCE BUNDLE:"


def split_evidence(payload) -> tuple[str, str]:
    """F13 `D14` / AC-F13.20 — `(evidence, instructions)` from a gateway payload.

    ★ The SAME bytes `_flatten` sends, cut at the bundle: `f"{rest}\n\n{prefix}"` is the
    old message exactly. Only the order the two reach the model changes (GW-30).
    """
    from src.shared.llm.anthropic_transport import _flatten

    if not isinstance(payload, dict) or not payload.get("bundle"):
        raise ValueError(f"no {EVIDENCE_MARKER!r} section to move ahead of the instructions "
                         f"(AC-F13.20) — refusing to send a prefix that is not the evidence")
    text = _flatten(payload)
    # ⚠ The cut is located from the payload's OWN head, never by searching for the
    #   marker — a prompt or a filing that mentions it would move the cut.
    empty_tail = f"{EVIDENCE_MARKER}\n{{}}"
    head = _flatten({**payload, "bundle": {}})[:-len(empty_tail)]
    if not (head.endswith("\n\n") and text.startswith(head + EVIDENCE_MARKER)):
        raise ValueError(f"the payload does not flatten to instructions + {EVIDENCE_MARKER!r} "
                         f"(AC-F13.20) — refusing a split that would change the bytes")
    return text[len(head):], head[:-2]


def evidence_first(send: Callable[[dict], dict]) -> Callable[[dict], dict]:
    """Wrap a transport so the gateway's evidence goes as `cache_prefix` (F13 `D14`).

    ★ Sits ABOVE `traced_transport`, so the trace records what was actually sent.
    """
    def call(request: dict) -> dict:
        prefix, rest = split_evidence(request["payload"])
        return send({**request, "cache_prefix": prefix, "payload": rest})
    return call


def transport_label() -> str:
    """One line for a runner's banner, so the operator sees which path is live."""
    return ("anthropic_api — ⚠ PAID, API key" if is_paid()
            else "claude_code — subscription, $0 API (notional cost recorded)")
