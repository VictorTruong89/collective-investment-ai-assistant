"""D-00 — the `claude_code` transport: development calls on the subscription.

`L2-shared-infrastructure` §5.7, GW-24…GW-29. ★ **Same provider, same model,
different wire.** During development every LLM call runs through headless
Claude Code (`claude -p`) on the fund manager's subscription; the Anthropic API
is reserved for the real daily runs (`CLAUDE.md`, 2026-10-01).

It honours the transport contract the gateway and `traced_transport` already
read — `{"text", "tokens_in", "tokens_out", "stop_reason"}` — and adds
`transport` and `notional_usd` so a recording says how it was made (GW-26/27).

⚠⚠ **It is not a byte-identical substitute for the API.** The CLI adds its own
framing, takes no `temperature`, caps output only through
`CLAUDE_CODE_MAX_OUTPUT_TOKENS`, and returns structured output from
`--json-schema` rather than a strict tool call. A golden case signed on a
`claude_code` recording grades the PROMPT, not the production transport.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from collections.abc import Callable, Mapping

from src.shared.errors import DecodingControlError, TransportError

#: GW-24 — chosen once, at the composition root.
TRANSPORT_ENV = "CIA_LLM_TRANSPORT"
CLAUDE_CODE = "claude_code"
ANTHROPIC_API = "anthropic_api"
_TRANSPORTS = (CLAUDE_CODE, ANTHROPIC_API)

#: Overrides the CLI binary. ★ `tests/conftest.py` points it at a path that
#: does not exist, so no test can spend subscription usage by accident.
BIN_ENV = "CIA_CLAUDE_BIN"

#: GW-25 — never handed to the subprocess. Either one makes the CLI bill the API.
_STRIPPED_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")

#: Replaces Claude Code's own coding-agent system prompt. ⚠ The API path sends
#: no system prompt at all; this is the nearest the CLI allows.
SYSTEM_PROMPT = ("You are called programmatically. Follow the user message "
                 "exactly and answer in the format it requires.")

MODEL_MAX_OUTPUT = 128_000
_CAP_ERROR = re.compile(r"exceeded the \d+ output token maximum")
_RETRYABLE_STATUS = {429, 500, 502, 503, 504, 529}


def selected_transport(environ: Mapping[str, str] | None = None) -> str:
    """GW-24 — `claude_code` unless `CIA_LLM_TRANSPORT` says otherwise.

    ⚠ An unknown value raises rather than falling back to either path: a typo
    must not quietly decide whether a call is paid (P5).
    """
    env = os.environ if environ is None else environ
    value = env.get(TRANSPORT_ENV)
    if value is None:
        return CLAUDE_CODE
    if value not in _TRANSPORTS:
        raise ValueError(
            f"{TRANSPORT_ENV}={value!r} is not one of {_TRANSPORTS} — refusing to "
            f"guess which transport (and so whether the call is paid)")
    return value


def cost_usd(response: Mapping) -> float | None:
    """GW-27 — what a response cost in API dollars, if the transport says.

    A `claude_code` call costs $0; its list price is `notional_usd`, kept apart.
    `None` means *not known here* — the caller prices it from tokens as before.
    """
    if response.get("transport") == CLAUDE_CODE:
        return 0.0
    return None


def _flatten(payload) -> str:
    # ★ The same flattening the API transport uses, so the two send the same text.
    from src.shared.llm.anthropic_transport import _flatten as flatten
    return flatten(payload)


def _child_env(max_tokens: int) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _STRIPPED_ENV}
    env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(max_tokens)
    return env


def make_claude_code_transport(
    *,
    json_schema: dict | None = None,
    max_output: int = MODEL_MAX_OUTPUT,
    runner: Callable | None = None,
    binary: str | None = None,
    timeout: float = 1800.0,
) -> Callable[[dict], dict]:
    """Return the callable `Gateway(transport=...)` / `traced_transport` expect.

    `json_schema` is the output schema (the API path's strict tool
    `input_schema`). `runner` is injected for tests; it defaults to
    `subprocess.run`.
    """
    run = runner or subprocess.run
    exe = binary or os.environ.get(BIN_ENV) or "claude"
    state = {"auth_ok": False}

    def _invoke(argv, *, stdin, env, cwd):
        try:
            return run(argv, input=stdin, env=env, cwd=cwd, timeout=timeout,
                       capture_output=True, text=True)
        except FileNotFoundError:
            raise TransportError(f"Claude Code CLI not found at {exe!r}",
                                 retryable=False) from None
        except subprocess.TimeoutExpired:
            raise TransportError(f"Claude Code CLI timed out after {timeout:.0f}s") from None

    def _check_auth(cwd):
        """GW-25 — refuse unless the CLI is logged in through claude.ai."""
        proc = _invoke([exe, "auth", "status"], stdin=None,
                       env=_child_env(max_output), cwd=cwd)
        try:
            method = json.loads(proc.stdout or "").get("authMethod")
        except (ValueError, AttributeError):
            method = None
        if method != "claude.ai":
            raise TransportError(
                f"Claude Code is not logged in via claude.ai (authMethod={method!r}) — "
                f"refusing: a development call must run on the subscription, never "
                f"bill an API key (GW-25). Run `claude auth login`.", retryable=False)
        state["auth_ok"] = True

    def transport(request: dict) -> dict:
        if request.get("temperature") is not None:
            raise DecodingControlError(
                "the Claude Code transport cannot honour `temperature` — refused "
                "rather than silently dropped (GW-28). Use CIA_LLM_TRANSPORT="
                "anthropic_api for a cheap-tier call.")
        max_tokens = min(int(request.get("max_tokens") or max_output), max_output)
        prompt = _flatten(request["payload"])
        if request.get("cache_prefix"):
            prompt = f"{request['cache_prefix']}\n\n{prompt}"

        argv = [exe, "-p", "--output-format", "json",
                "--model", str(request["model"]),
                "--tools", "", "--no-session-persistence",
                "--setting-sources", "", "--strict-mcp-config",
                "--system-prompt", SYSTEM_PROMPT]
        if request.get("effort"):
            argv += ["--effort", str(request["effort"])]
        if json_schema is not None:
            argv += ["--json-schema", json.dumps(json_schema)]

        # ★ An empty directory outside the repo: the CLI must not load this
        #   repo's CLAUDE.md, hooks or memory into a pipeline call.
        with tempfile.TemporaryDirectory(prefix="cia-claude-code-") as cwd:
            if not state["auth_ok"]:
                _check_auth(cwd)
            proc = _invoke(argv, stdin=prompt, env=_child_env(max_tokens), cwd=cwd)

        try:
            data = json.loads(proc.stdout or "")
        except ValueError:
            raise TransportError(
                f"Claude Code returned no JSON result (exit {proc.returncode}): "
                f"{(proc.stdout or proc.stderr or '')[:200]}") from None

        usage = data.get("usage") or {}
        common = {
            "transport": CLAUDE_CODE,
            "tokens_in": (int(usage.get("input_tokens") or 0)
                          + int(usage.get("cache_creation_input_tokens") or 0)
                          + int(usage.get("cache_read_input_tokens") or 0)),
            "tokens_out": int(usage.get("output_tokens") or 0),
            "cache_read": usage.get("cache_read_input_tokens"),
            "cache_write": usage.get("cache_creation_input_tokens"),
            "notional_usd": data.get("total_cost_usd"),
            "num_turns": data.get("num_turns"),
            "models_used": sorted(data.get("modelUsage") or {}),
        }
        message = str(data.get("result") or "")
        if data.get("is_error"):
            if _CAP_ERROR.search(message):
                # ★ GW-29 — a truncation is a failure, and its prose is not an answer.
                return {**common, "text": "", "stop_reason": "max_tokens",
                        "cli_error": message[:300]}
            status = data.get("api_error_status")
            raise TransportError(f"Claude Code error: {message[:300]}",
                                 retryable=status in _RETRYABLE_STATUS)
        if proc.returncode != 0:
            raise TransportError(f"Claude Code exited {proc.returncode}: {message[:200]}")

        structured = data.get("structured_output")
        text = (json.dumps(structured) if json_schema is not None and structured is not None
                else message)
        return {**common, "text": text, "stop_reason": data.get("stop_reason")}

    return transport
