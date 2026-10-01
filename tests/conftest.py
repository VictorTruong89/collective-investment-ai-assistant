"""Suite-wide guards for `tests/`.

⚠⚠ **No test may start the real Claude Code CLI** (`L2-shared-infrastructure`
§5.7). `claude_code` is now the default transport, so a test that reaches a
runner without injecting a fake would otherwise spend subscription usage on
every `pytest`. Pointing `CIA_CLAUDE_BIN` at a path that does not exist turns
that into a `TransportError` instead.
"""

import pytest


@pytest.fixture(autouse=True)
def _no_real_claude_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("CIA_CLAUDE_BIN", str(tmp_path / "no-real-claude-cli-in-tests"))
