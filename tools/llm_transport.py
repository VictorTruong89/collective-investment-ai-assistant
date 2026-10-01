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


def dev_transport(**kwargs) -> Callable[[dict], dict]:
    """The transport for a development runner, chosen by `CIA_LLM_TRANSPORT`."""
    if is_paid():
        import tools.anthropic_transport as api
        return api.anthropic_transport(**kwargs)
    tool = kwargs.get("tool")
    # `thinking_display` is an API-only diagnostic (DX-96); the CLI shows no thinking.
    return make_claude_code_transport(
        json_schema=tool["input_schema"] if tool else None,
        max_output=kwargs.get("max_output", MODEL_MAX_OUTPUT))


def transport_label() -> str:
    """One line for a runner's banner, so the operator sees which path is live."""
    return ("anthropic_api — ⚠ PAID, API key" if is_paid()
            else "claude_code — subscription, $0 API (notional cost recorded)")
