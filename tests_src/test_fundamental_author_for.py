"""D-01 WF-1 — `ticker + as_of` → a probed thesis, composed in one place."""
from datetime import date, timedelta

import pytest

from src.fundamental.thesis.author_for import (
    DEFAULT_HORIZON_DAYS, K_RUNS, author_for,
)

AS_OF = date(2026, 8, 25)


def test_k_runs_is_the_rm1_floor_not_a_tunable_default():
    """★ AC-1.8 makes a k<3 result unable to be the actionable pick, so three is
    a floor. ⚠ A `k=1` default would make every thesis silently unusable."""
    assert K_RUNS >= 3


def test_the_falsifier_deadline_lands_outside_the_bundle_window():
    """⚠ A deadline inside the bundle's own window is answerable before the
    thesis is filed — which is a fact, not a prediction."""
    assert DEFAULT_HORIZON_DAYS > 90
    assert AS_OF + timedelta(days=DEFAULT_HORIZON_DAYS) > AS_OF


def test_orchestration_passes_no_gateway_so_d01_must_be_able_to_build_one():
    """★★ ST-5 / AC-8.4 — orchestration may not import the gateway, so
    `gateway` must be optional or the wired path cannot run at all."""
    import inspect

    assert inspect.signature(author_for).parameters["gateway"].default is None


def test_exactly_one_d01_file_can_reach_the_model():
    """AC-1.38 — ★ narrower than ST-5 on purpose: checkable by reading one file.

    ⚠ The builder was first written as its own module and this caught it.
    """
    from pathlib import Path

    importers = [str(p) for p in sorted(Path("src/fundamental").rglob("*.py"))
                 if "src.shared.llm" in p.read_text(encoding="utf-8")]
    assert importers == ["src/fundamental/prompts/call.py"]


def test_a_missing_api_key_is_reported_as_configuration_not_as_no_thesis(monkeypatch):
    """P5 — ⚠ *"no API key"* and *"the model declined"* are different states, and
    a caller that cannot tell them apart reports a config fault as a verdict."""
    from src.fundamental.errors import ResearchError
    from src.fundamental.prompts.call import build_gateway

    monkeypatch.setenv("CIA_LLM_TRANSPORT", "anthropic_api")   # this test covers the API path (GW-24)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ResearchError, match="ANTHROPIC_API_KEY"):
        build_gateway()


def test_the_deep_tier_model_is_opus(monkeypatch):
    """INV-8 — thesis authoring is quality-critical and low-frequency."""
    from src.fundamental.prompts.call import THESIS_MODEL

    assert THESIS_MODEL == "claude-opus-5"
