"""`L2-shared-infrastructure` §5.7 — the `claude_code` transport (GW-24…GW-29).

⚠⚠ **No test here runs the real CLI.** Every call goes through an injected
`runner`, and `tests/conftest.py` points `CIA_CLAUDE_BIN` at a path that does
not exist, so a test that forgot to inject one fails instead of spending
subscription usage.
"""

from __future__ import annotations

import json
import subprocess

import pytest

from src.shared.errors import DecodingControlError, TransportError
from src.shared.llm import claude_code_transport as cc

AUTH_OK = json.dumps({"loggedIn": True, "authMethod": "claude.ai"})


def _result(**over) -> str:
    """A CLI `--output-format json` result, shaped like the one measured
    2026-10-01 (`claude` 2.1.286)."""
    base = {
        "type": "result", "subtype": "success", "is_error": False,
        "stop_reason": "tool_use", "num_turns": 2,
        "result": '{"a":7}', "structured_output": {"a": 7},
        "total_cost_usd": 0.00878,
        "usage": {"input_tokens": 2, "cache_creation_input_tokens": 969,
                  "cache_read_input_tokens": 10, "output_tokens": 51},
        "modelUsage": {"claude-opus-5-5": {"costUSD": 0.00878}},
    }
    base.update(over)
    return json.dumps(base)


class FakeRunner:
    """Records every subprocess invocation; answers `auth status` and `-p`."""

    def __init__(self, result: str | None = None, auth: str = AUTH_OK, returncode: int = 0):
        self.result = _result() if result is None else result
        self.auth, self.returncode = auth, returncode
        self.calls: list[dict] = []

    def __call__(self, argv, *, input=None, env=None, cwd=None, timeout=None,
                 capture_output=True, text=True):
        self.calls.append({"argv": list(argv), "input": input, "env": dict(env or {}),
                           "cwd": cwd})
        out = self.auth if argv[1:3] == ["auth", "status"] else self.result
        return subprocess.CompletedProcess(argv, self.returncode, stdout=out, stderr="")

    @property
    def prompt_calls(self):
        return [c for c in self.calls if "-p" in c["argv"]]


REQUEST = {"model": "claude-opus-5", "max_tokens": 20000, "payload": "PROMPT",
           "effort": "medium", "thinking": "adaptive"}


# ── AC-0.21 ─────────────────────────────────────────────────────────────────

def test_ac_0_21_unset_selects_claude_code(monkeypatch):
    """AC-0.21 (GW-24) — with `CIA_LLM_TRANSPORT` unset, development defaults to
    the subscription."""
    monkeypatch.delenv(cc.TRANSPORT_ENV, raising=False)
    assert cc.selected_transport() == cc.CLAUDE_CODE


@pytest.mark.parametrize("value", [cc.CLAUDE_CODE, cc.ANTHROPIC_API])
def test_ac_0_21_known_values_are_honoured(monkeypatch, value):
    """AC-0.21 (GW-24)."""
    monkeypatch.setenv(cc.TRANSPORT_ENV, value)
    assert cc.selected_transport() == value


@pytest.mark.parametrize("value", ["api", "anthropic", "Claude_Code", " "])
def test_ac_0_21_unknown_value_raises(monkeypatch, value):
    """AC-0.21 (GW-24) — a typo must not quietly select either path (P5)."""
    monkeypatch.setenv(cc.TRANSPORT_ENV, value)
    with pytest.raises(ValueError, match=cc.TRANSPORT_ENV):
        cc.selected_transport()


# ── AC-0.22 ─────────────────────────────────────────────────────────────────

def test_ac_0_22_api_credentials_never_reach_the_cli(monkeypatch):
    """AC-0.22 (GW-25) — a key exported in the shell must not turn a
    subscription call into a billed API call."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-should-not-leak")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "tok-should-not-leak")
    runner = FakeRunner()
    cc.make_claude_code_transport(runner=runner, binary="claude")(dict(REQUEST))
    assert runner.calls, "the transport ran nothing"
    for call in runner.calls:                       # auth status AND the call
        assert "ANTHROPIC_API_KEY" not in call["env"]
        assert "ANTHROPIC_AUTH_TOKEN" not in call["env"]


@pytest.mark.parametrize("auth", [
    json.dumps({"loggedIn": True, "authMethod": "api_key"}),
    json.dumps({"loggedIn": False}),
    "not json",
])
def test_ac_0_22_not_logged_in_via_claude_ai_raises_before_any_call(auth):
    """AC-0.22 (GW-25) — the auth check runs first; no prompt is ever sent."""
    runner = FakeRunner(auth=auth)
    transport = cc.make_claude_code_transport(runner=runner, binary="claude")
    with pytest.raises(TransportError, match="claude.ai"):
        transport(dict(REQUEST))
    assert runner.prompt_calls == []


def test_ac_0_22_auth_is_checked_once_per_transport():
    """AC-0.22 — once per transport, not once per call."""
    runner = FakeRunner()
    transport = cc.make_claude_code_transport(runner=runner, binary="claude")
    transport(dict(REQUEST))
    transport(dict(REQUEST))
    auth_calls = [c for c in runner.calls if c["argv"][1:3] == ["auth", "status"]]
    assert len(auth_calls) == 1 and len(runner.prompt_calls) == 2


# ── AC-0.23 / AC-0.24 ───────────────────────────────────────────────────────

def test_ac_0_23_response_names_its_transport():
    """AC-0.23 (GW-26)."""
    out = cc.make_claude_code_transport(runner=FakeRunner(), binary="claude")(dict(REQUEST))
    assert out["transport"] == cc.CLAUDE_CODE


def test_ac_0_24_tokens_and_notional_cost_are_reported():
    """AC-0.24 (GW-27) — input counts every input the CLI sent, cache included;
    the CLI's list cost is kept as notional, and the call is priced at $0."""
    out = cc.make_claude_code_transport(runner=FakeRunner(), binary="claude")(dict(REQUEST))
    assert out["tokens_in"] == 2 + 969 + 10
    assert out["tokens_out"] == 51
    assert out["notional_usd"] == pytest.approx(0.00878)
    assert cc.cost_usd(out) == 0.0


def test_ac_0_24_structured_output_is_the_text_and_stop_reason_is_verbatim():
    """AC-0.24 — with a schema, the answer is the structured output; the
    stop reason is passed through so `reverify_recording`'s `tool_use` check
    still holds."""
    runner = FakeRunner()
    schema = {"type": "object", "properties": {"a": {"type": "integer"}}}
    out = cc.make_claude_code_transport(json_schema=schema, runner=runner,
                                        binary="claude")(dict(REQUEST))
    assert json.loads(out["text"]) == {"a": 7}
    assert out["stop_reason"] == "tool_use"
    argv = runner.prompt_calls[0]["argv"]
    assert json.loads(argv[argv.index("--json-schema") + 1]) == schema


# ── AC-0.25 ─────────────────────────────────────────────────────────────────

def test_ac_0_25_temperature_is_rejected_before_the_cli_runs():
    """AC-0.25 (GW-28) — a control the CLI cannot honour is refused, not dropped."""
    runner = FakeRunner()
    transport = cc.make_claude_code_transport(runner=runner, binary="claude")
    with pytest.raises(DecodingControlError, match="temperature"):
        transport({"model": "claude-haiku-4-5", "max_tokens": 256,
                   "payload": "x", "temperature": 0.0})
    assert runner.prompt_calls == []


def test_ac_0_25_effort_and_max_tokens_reach_the_cli():
    """AC-0.25 (GW-28)."""
    runner = FakeRunner()
    cc.make_claude_code_transport(runner=runner, binary="claude",
                                  max_output=128_000)(dict(REQUEST))
    call = runner.prompt_calls[0]
    argv = call["argv"]
    assert argv[argv.index("--effort") + 1] == "medium"
    assert argv[argv.index("--model") + 1] == "claude-opus-5"
    assert call["env"]["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] == "20000"
    # ★ no built-in tools, no project settings, no saved session
    assert argv[argv.index("--tools") + 1] == ""
    assert "--no-session-persistence" in argv
    assert argv[argv.index("--setting-sources") + 1] == ""


def test_ac_0_25_cache_prefix_and_payload_are_sent_on_stdin_in_order():
    """AC-0.25 — the prompt goes on stdin (bundles run to ~250k chars, too big
    for argv), stable prefix first, as the API transport orders them."""
    runner = FakeRunner()
    cc.make_claude_code_transport(runner=runner, binary="claude")(
        {**REQUEST, "cache_prefix": "EVIDENCE", "payload": "INSTRUCTIONS"})
    sent = runner.prompt_calls[0]["input"]
    assert sent.index("EVIDENCE") < sent.index("INSTRUCTIONS")


def test_ac_0_25_cli_runs_outside_the_repo():
    """AC-0.25 — the CLI must not pick up this repo's CLAUDE.md or hooks."""
    import pathlib
    runner = FakeRunner()
    cc.make_claude_code_transport(runner=runner, binary="claude")(dict(REQUEST))
    repo = pathlib.Path(__file__).resolve().parents[2]
    cwd = pathlib.Path(runner.prompt_calls[0]["cwd"]).resolve()
    assert repo not in (cwd, *cwd.parents)


# ── AC-0.26 ─────────────────────────────────────────────────────────────────

def test_ac_0_26_output_cap_error_is_a_truncation():
    """AC-0.26 (GW-29) — the CLI's prose must not become an answer (GW-22)."""
    capped = _result(is_error=True, subtype="success", stop_reason="stop_sequence",
                     structured_output=None,
                     result="API Error: Claude's response exceeded the 40 output "
                            "token maximum. To configure this behavior, set the "
                            "CLAUDE_CODE_MAX_OUTPUT_TOKENS environment variable.")
    out = cc.make_claude_code_transport(runner=FakeRunner(result=capped),
                                        binary="claude")(dict(REQUEST))
    assert out["stop_reason"] == "max_tokens"
    assert out["text"] == ""


@pytest.mark.parametrize("stdout,code", [
    (_result(is_error=True, result="API Error: 529 overloaded", structured_output=None), 1),
    ("Error: something broke", 1),
    ("", 0),
])
def test_ac_0_26_any_other_cli_error_raises(stdout, code):
    """AC-0.26 (GW-29)."""
    transport = cc.make_claude_code_transport(
        runner=FakeRunner(result=stdout, returncode=code), binary="claude")
    with pytest.raises(TransportError):
        transport(dict(REQUEST))


def test_ac_0_26_a_missing_binary_raises_transport_error():
    """AC-0.26 — and it is what keeps the suite hermetic (`tests/conftest.py`)."""
    transport = cc.make_claude_code_transport(binary="/nonexistent/claude")
    with pytest.raises(TransportError, match="not found"):
        transport(dict(REQUEST))


# ── the composition roots ───────────────────────────────────────────────────

def test_ac_0_21_dev_runners_default_to_the_subscription(monkeypatch):
    """AC-0.21 (GW-24) — `tools/llm_transport.dev_transport` with the variable
    unset builds the claude_code transport, never the API one, and prices at $0."""
    import tools.anthropic_transport as api
    from tools import llm_transport

    monkeypatch.delenv(cc.TRANSPORT_ENV, raising=False)
    monkeypatch.setattr(api, "anthropic_transport",
                        lambda **_: pytest.fail("the API transport was built"))
    transport = llm_transport.dev_transport(tool={"input_schema": {"type": "object"}},
                                            max_output=1000)
    assert callable(transport)
    assert llm_transport.price_factor() == 0.0
    with pytest.raises(TransportError, match="not found"):   # conftest's sentinel
        transport(dict(REQUEST))


def test_ac_0_21_dev_runners_use_the_api_only_when_asked(monkeypatch):
    """AC-0.21 (GW-24) — the API factory gets the runner's arguments unchanged."""
    import tools.anthropic_transport as api
    from tools import llm_transport

    seen = {}
    monkeypatch.setenv(cc.TRANSPORT_ENV, cc.ANTHROPIC_API)
    monkeypatch.setattr(api, "anthropic_transport",
                        lambda **kw: seen.update(kw) or (lambda r: r))
    llm_transport.dev_transport(tool={"x": 1}, max_output=5)
    assert seen == {"tool": {"x": 1}, "max_output": 5}
    assert llm_transport.price_factor() == 1.0


def test_ac_0_21_the_gateway_path_needs_no_api_key_on_the_subscription(monkeypatch):
    """AC-0.21 / AC-0.24 — `build_gateway` on the default transport neither
    reads the key nor prices a call."""
    from src.fundamental.prompts.call import build_gateway

    monkeypatch.delenv(cc.TRANSPORT_ENV, raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    gw = build_gateway()
    assert gw is not None


def test_ac_0_23_the_api_transport_names_itself():
    """AC-0.23 (GW-26) — both transports label their responses."""
    from types import SimpleNamespace

    from tools.anthropic_transport import to_transport_result

    msg = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="hi")], stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=1, output_tokens=1))
    assert to_transport_result(msg)["transport"] == cc.ANTHROPIC_API
