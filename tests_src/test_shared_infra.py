"""Config, logging and secrets — AC-0.14 … AC-0.20.

Tier: unit (constitution §4), except AC-0.19 which is closer to a property: it
tries to leak a secret through every ordinary rendering path rather than
asserting one.
"""

from __future__ import annotations

import io
import json
import logging as stdlib_logging
import os

import pytest

from src.shared.config import Config, ConfigSpec, load_config
from src.shared.errors import (
    ConfigMutationError,
    MissingConfigKeyError,
    PipelineError,
    SecretAbsentError,
)
from src.shared.logging import degraded, logger
from src.shared.secrets import KNOWN_SECRETS, Secret, require, secret


@pytest.fixture
def cfg_files(tmp_path):
    base = tmp_path / "settings.yaml"
    base.write_text(
        "llm:\n  deep:\n    model_id: claude-opus-5\n    effort: high\n"
        "  cheap:\n    model_id: claude-haiku-4-5\n    temperature: 0.0\n",
        encoding="utf-8",
    )
    override = tmp_path / "local.yaml"
    override.write_text("llm.deep.effort: xhigh\n", encoding="utf-8")
    return base, override


# --------------------------------------------------------------------------- #
# Config — CF-1 … CF-5
# --------------------------------------------------------------------------- #

def test_missing_required_key_raises_at_load(cfg_files):
    """AC-0.14 — CF-1: no silent default for a value the system needs."""
    base, _ = cfg_files
    spec = ConfigSpec(required=("llm.deep.model_id", "llm.budget.usd_per_run"))
    with pytest.raises(MissingConfigKeyError) as e:
        load_config([base], spec)
    assert "llm.budget.usd_per_run" in str(e.value)


def test_declared_optional_default_is_applied(cfg_files):
    """CF-1 — an OPTIONAL key may default; a required one may not."""
    base, _ = cfg_files
    cfg = load_config([base], ConfigSpec(optional={"llm.retry.max_attempts": 3}))
    assert cfg.get("llm.retry.max_attempts") == 3


def test_keys_are_flattened_to_dotted_paths(cfg_files):
    """CF-3 — a manifest entry must name ONE value, not a nested blob."""
    base, _ = cfg_files
    cfg = load_config([base], ConfigSpec())
    assert cfg.get("llm.deep.model_id") == "claude-opus-5"
    assert cfg.get("llm.cheap.temperature") == 0.0


def test_later_sources_override_earlier_ones(cfg_files):
    base, override = cfg_files
    cfg = load_config([base, override], ConfigSpec())
    assert cfg.get("llm.deep.effort") == "xhigh"


def test_every_resolved_value_appears_in_the_manifest(cfg_files):
    """AC-0.15 — CF-3: a tuned number no manifest records makes a run
    irreproducible while looking deterministic."""
    base, _ = cfg_files
    cfg = load_config([base], ConfigSpec())
    man = cfg.manifest()
    assert man.resolved["llm.deep.effort"] == "high"
    assert man.config_hash.startswith("sha256:")
    assert str(base) in man.source_files
    json.dumps(man.to_json_obj())          # must be serialisable for OR-9


def test_manifest_hash_is_stable_and_content_sensitive(cfg_files):
    """CF-3 — two runs are comparable only if identical config hashes match."""
    base, override = cfg_files
    a = load_config([base], ConfigSpec()).manifest().config_hash
    b = load_config([base], ConfigSpec()).manifest().config_hash
    c = load_config([base, override], ConfigSpec()).manifest().config_hash
    assert a == b and a != c


def test_config_cannot_be_mutated_after_load(cfg_files):
    """AC-0.16 — CF-4: a mutation makes the manifest a lie about the rest of the run."""
    base, _ = cfg_files
    cfg = load_config([base], ConfigSpec())
    with pytest.raises(ConfigMutationError):
        cfg.anything = 1
    with pytest.raises(ConfigMutationError):
        cfg["llm.deep.effort"] = "max"


def test_reading_an_undeclared_key_raises_rather_than_returning_none(cfg_files):
    """CF-1 — `None` from a config getter is how a silent default is born."""
    base, _ = cfg_files
    with pytest.raises(MissingConfigKeyError):
        load_config([base], ConfigSpec()).get("llm.deep.nonexistent")


def test_a_secret_in_config_is_refused_structurally(tmp_path):
    """CT-0.2, SC-3 — secrets are excluded BY CONSTRUCTION, not filtered out.

    A filter on the way out is a filter someone can forget. Refusing entry means
    the manifest has nothing to leak.
    """
    cfg = tmp_path / "s.yaml"
    cfg.write_text("api: {}\n", encoding="utf-8")
    from src.shared.config import _flatten

    with pytest.raises(ConfigMutationError) as e:
        _flatten({"api": {"key": Secret("ANTHROPIC_API_KEY", "sk-live-123")}})
    assert "sk-live-123" not in str(e.value)   # the error must not leak it either


# --------------------------------------------------------------------------- #
# Secrets — SC-1 … SC-4
# --------------------------------------------------------------------------- #

def test_missing_secret_raises_at_startup_not_first_use(monkeypatch):
    """AC-0.20 — SC-2: a nightly run must not die forty minutes in."""
    for name in KNOWN_SECRETS:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(SecretAbsentError) as e:
        require()
    for name in KNOWN_SECRETS:
        assert name in str(e.value)        # all of them, in one error


def test_require_returns_every_secret_when_present(monkeypatch):
    for name in KNOWN_SECRETS:
        monkeypatch.setenv(name, f"value-of-{name}")
    got = require()
    assert set(got) == set(KNOWN_SECRETS)
    assert got["FMP_API_KEY"].reveal() == "value-of-FMP_API_KEY"


def test_single_secret_lookup_raises_when_absent(monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    with pytest.raises(SecretAbsentError):
        secret("FMP_API_KEY")


@pytest.mark.parametrize("render", [
    repr, str, lambda s: f"{s}", lambda s: f"{s!s}", lambda s: f"{s:>20}",
    lambda s: "%s" % (s,), lambda s: json.dumps({"k": s}, default=str),
    lambda s: "{}".format(s),
])
def test_secret_never_renders_its_value(render):
    """AC-0.19 — SC-3: try to leak one through every ordinary rendering path.

    ★ This is the test the AC asks for: not "does __repr__ redact" but "can I
    get the value out by accident". Each entry is a real way a value reaches a
    log line or an exception message.
    """
    s = Secret("ANTHROPIC_API_KEY", "sk-live-DO-NOT-LEAK")
    assert "sk-live-DO-NOT-LEAK" not in render(s)


def test_secret_leaks_only_through_the_greppable_escape():
    """SC-3 — `.reveal()` is the one way out, named so every use is greppable."""
    s = Secret("ANTHROPIC_API_KEY", "sk-live-DO-NOT-LEAK")
    assert s.reveal() == "sk-live-DO-NOT-LEAK"
    assert s.name == "ANTHROPIC_API_KEY"      # the NAME is not secret


def test_secret_is_immutable():
    s = Secret("FMP_API_KEY", "v")
    with pytest.raises(AttributeError):
        s._value = "other"


def test_secret_does_not_leak_through_a_traceback():
    """SC-3 — an exception carrying a Secret must render redacted."""
    s = Secret("ANTHROPIC_API_KEY", "sk-live-DO-NOT-LEAK")
    try:
        raise PipelineError(f"call failed with {s}")
    except PipelineError as exc:
        assert "sk-live-DO-NOT-LEAK" not in str(exc)


# --------------------------------------------------------------------------- #
# Logging — LG-1 … LG-5
# --------------------------------------------------------------------------- #

@pytest.fixture
def captured():
    """Attach a capturing handler using the module's own formatter."""
    from src.shared.logging import _JsonFormatter

    stream = io.StringIO()
    handler = stdlib_logging.StreamHandler(stream)
    handler.setFormatter(_JsonFormatter())
    root = stdlib_logging.getLogger()
    previous, level = root.handlers, root.level
    root.handlers = [handler]
    root.setLevel(stdlib_logging.DEBUG)
    yield stream
    root.handlers, root.level = previous, level


def test_every_record_carries_run_id(captured):
    """AC-0.17 — LG-2: one run must be reconstructible across twelve domains."""
    logger("d01.thesis", run_id="run-abc").info("authored", ticker="MU")
    record = json.loads(captured.getvalue().strip())
    assert record["run_id"] == "run-abc"
    assert record["ticker"] == "MU" and record["logger"] == "d01.thesis"


def test_run_id_is_required():
    """LG-2 — a record with no correlation key belongs to no run."""
    with pytest.raises(ValueError):
        logger("d01", run_id="")


def test_records_are_structured_not_prose(captured):
    """LG-3 — a message that must be regex-parsed is an undeclared structure."""
    logger("d02", run_id="r1").info("computed", metric="roic", value=0.24)
    record = json.loads(captured.getvalue().strip())
    assert record["metric"] == "roic" and record["value"] == 0.24


def test_degraded_logs_AND_raises(captured):
    """AC-0.18 — LG-5/P5: both card incidents were logged, and then proceeded."""
    log = logger("d01", run_id="r2")
    with pytest.raises(PipelineError):
        degraded(log, "llm returned nothing", PipelineError("empty response"), ticker="MU")
    record = json.loads(captured.getvalue().strip())
    assert record["level"] == "WARNING"
    assert record["degraded"] is True and record["ticker"] == "MU"


def test_a_secret_logged_by_accident_is_redacted(captured):
    """LG-4 / SC-3 — structural, via the type, not care at the call site."""
    logger("d00", run_id="r3").info("configured", key=Secret("ANTHROPIC_API_KEY", "sk-leak"))
    assert "sk-leak" not in captured.getvalue()
    assert "<redacted>" in captured.getvalue()
