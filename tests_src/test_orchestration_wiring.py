"""D-08 — the graph driving the real domains. OR-1, OR-16, OR-40.

★★ **The B6 graph was declared, validated and never actually run against a
domain.** `b3_run.py` wired the same sequence by hand; this makes the *graph*
drive it, which is what OR-40 means by an in-process job graph.

⚠ **An adapter routes; it never computes.** The moment one derives a value,
D-08 has acquired analysis and OR-1 is broken.

Tier: integration (constitution §4).
"""

from __future__ import annotations

import tempfile
from datetime import date, datetime, timezone

import pandas as pd
import pytest

from src.feature_engineer.contracts.sets.b3_minimal_v1 import B3_MINIMAL_V1
from src.orchestration import (
    Budgets, Cadence, DAILY_INFERENCE, Orchestrator, artifact_allowed,
    failure_notice,
)
from src.orchestration.errors import OrchestrationError
from src.orchestration.jobs.wiring import ADAPTERS, RunContext, make_dispatch


def raw_prices(days: int = 90) -> pd.DataFrame:
    """CT-7.1's raw shape — `*_minor` int columns with their currency sibling."""
    dates = pd.bdate_range("2026-01-02", periods=days)
    return pd.DataFrame({
        "ticker": "NVDA", "date": [d.date() for d in dates],
        "open_minor": [10000 + i * 50 for i in range(days)],
        "high_minor": [10100 + i * 50 for i in range(days)],
        "low_minor": [9900 + i * 50 for i in range(days)],
        "close_minor": [10050 + i * 50 for i in range(days)],
        "volume": [1_000_000] * days, "currency": "USD", "source": "fmp"})


def context(prices=None) -> RunContext:
    prices = raw_prices() if prices is None else prices
    return RunContext(as_of=prices["date"].iloc[-1],
                      adj_as_of=prices["date"].iloc[-1], universe=("NVDA",),
                      contract=B3_MINIMAL_V1, raw_prices=prices, events=(),
                      event_store_root=tempfile.mkdtemp(),
                      # ★ CT-11.7 — the `record` job is required, not optional:
                      #   a run with nowhere to persist is misconfigured (RC-59).
                      artifact_root=tempfile.mkdtemp())


def orchestrator() -> Orchestrator:
    return Orchestrator(graph=DAILY_INFERENCE,
                        cadence=Cadence(job_graph_id=DAILY_INFERENCE.job_graph_id),
                        budgets=Budgets(run_seconds=600.0))


def triggered(orc, ctx, **kw):
    base = dict(as_of=ctx.as_of, calendar=lambda _d: True,
                day_bar={"open": 12345, "settled": True, "high": None,
                         "low": None, "close": None},
                model=None, git_sha="wired", config_hash="cfg:1",
                now=datetime.now(timezone.utc))
    return orc.trigger(**{**base, **kw})


# --------------------------------------------------------------------------- #
# ★★ The graph drives the domains
# --------------------------------------------------------------------------- #

def test_every_job_in_the_graph_has_an_adapter():
    """OR-40 — ⚠ *a graph node nothing can run is a declared step that silently
    does nothing.*"""
    assert {j.job_id for j in DAILY_INFERENCE.jobs} == set(ADAPTERS)


def test_the_graph_runs_all_twelve_jobs_and_produces_a_card():
    """★★ **D-07 → D-02 → D-03 → {D-01, D-05} → D-12 → D-09, driven by the
    graph** rather than by a hand-rolled sequence."""
    orc, ctx = orchestrator(), context()
    outcome = orc.run(triggered(orc, ctx).run_id, invoke=make_dispatch(ctx))

    assert outcome.status == "SUCCESS"
    assert artifact_allowed(outcome) is True
    # ✏ 2026-10-05: 13 → 11 — `observe` and `thesis` (the old three-call thesis
    #   path) were removed (L3 §2.1s); `thesis_gate` falls back to the stub.
    # ✏ 2026-10-21: 11 → 12 — the `flags` job (OR-63, RK-40).
    assert [j.status for j in outcome.jobs] == ["SUCCESS"] * 12
    assert set(ctx.outputs) == set(ADAPTERS)

    card = ctx.outputs["render"]
    assert card.ticker == "NVDA"
    # ⚠ BS-33 — the skeleton's card is informational; it claims no action.
    assert ctx.outputs["decide"].actionable is False


def test_the_jobs_run_in_the_graphs_declared_order():
    """T-2 / DE-31 — ★ the calendar check runs **before the first feature**."""
    orc, ctx = orchestrator(), context()
    order = []

    def spy(job, manifest):
        order.append(job.job_id)
        return make_dispatch(ctx)(job, manifest)

    orc.run(triggered(orc, ctx).run_id, invoke=spy)
    assert order[0] == "calendar_check"
    assert order.index("features") > order.index("prices")
    assert order.index("decide") > max(order.index("rank"),
                                       order.index("thesis_gate"))
    assert order[-1] == "deliver"


def test_a_job_reading_an_absent_upstream_output_raises():
    """★ The graph's own P5 — ⚠ *an adapter that defaults instead of raising
    would let a job run on data that was never produced.*"""
    ctx = context()
    with pytest.raises(OrchestrationError, match="never produced"):
        ctx.require("features")


def test_a_failed_upstream_job_stops_everything_downstream():
    """★★ OR-16 — **partial success is failure**, and the cascade proves it.

    ⚠ A malformed price frame fails `prices`; every downstream job then refuses
    because its input is absent, the run is `INCOMPLETE`, and **no human-facing
    artifact is allowed**.
    """
    broken = raw_prices().drop(columns=["close_minor"])
    orc, ctx = orchestrator(), context(broken)
    outcome = orc.run(triggered(orc, ctx).run_id, invoke=make_dispatch(ctx))

    assert outcome.status == "INCOMPLETE"
    assert artifact_allowed(outcome) is False
    statuses = {j.job_id: j.status for j in outcome.jobs}
    assert statuses["calendar_check"] == "SUCCESS"
    assert statuses["prices"] == "FAILED"
    for downstream in ("features", "rank", "decide", "render", "deliver"):
        assert statuses[downstream] == "FAILED", downstream
    assert "render" not in ctx.outputs, "no card was built from a broken panel"

    # ★ OR-19 + OR-45 — the failure is loud, and carries no analysis.
    notice = failure_notice(outcome)
    assert "prices" in notice["failed_jobs"]


def test_an_optional_job_degrades_scope_rather_than_failing_the_run():
    """OR-18 / INV-033 — ★ `risk` is declared optional: **D-05 refuses on an
    unreconciled book** (RK-29) and the run still completes, with the absence
    reported rather than filled."""
    orc, ctx = orchestrator(), context()
    outcome = orc.run(triggered(orc, ctx).run_id, invoke=make_dispatch(ctx))
    alerts = ctx.outputs["risk"]
    assert outcome.status == "SUCCESS"
    assert alerts.status.startswith("UNCHECKED"), \
        "no book exists, so D-05 reports UNCHECKED rather than all-clear"


# --------------------------------------------------------------------------- #
# OR-1 — the boundary the wiring must not cross
# --------------------------------------------------------------------------- #

def test_no_adapter_computes():
    """★★ OR-1 — ⚠ *the moment an adapter derives a value, D-08 has acquired
    analysis.*

    The adapters may only route: read from the context, call the domain, return
    what it gave back.
    """
    import inspect

    import src.orchestration.jobs.wiring as module

    source = inspect.getsource(module)
    for banned in ("import pandas", "import numpy", ".mean()", ".std()",
                   ".rolling(", ".pct_change("):
        assert banned not in source, banned


def test_resolution_still_lives_outside_the_runner():
    """OR-1 — ★ the runner takes `invoke` as an argument, so **nothing inside it
    can return a value derived from market data.**"""
    import inspect

    import src.orchestration.jobs.runner as runner

    assert "importlib" not in inspect.getsource(runner)
    assert "wiring" not in inspect.getsource(runner)


def test_the_dispatch_proves_the_declared_target_exists():
    """★ MT-50's shape — `Job.invokes` stays honest because every dispatch
    resolves it first. ⚠ Five of the nine names were wrong when the graph was
    written, and nothing noticed."""
    from src.orchestration.jobs.graph import Job

    ctx = context()
    dispatch = make_dispatch(ctx)
    ghost = Job("rank", "src.quant.signals.rank:no_such_function")
    with pytest.raises(AttributeError, match="does not resolve"):
        dispatch(ghost, object())


def test_ac_8_41_the_daily_context_carries_the_declared_taxonomy():
    """AC-8.41 (OR-53, CT-5.3) — ★ the daily run supplies D-05's declared taxonomy.

    ⚠ Found 2026-10-06 (L9 §6 R2): `RunContext.taxonomy` was never set, so `_risk`
    fell back to the B3 refusal even for a valued book. Checked at the seam the
    entrypoint uses (`_theme_taxonomy`) and on the `RunContext(...)` call itself,
    because `_context_for` fetches the universe live.
    """
    import ast
    import inspect

    from src.orchestration import entrypoint
    from src.risk import THEMES_V1

    assert entrypoint._theme_taxonomy() is THEMES_V1
    tree = ast.parse(inspect.getsource(entrypoint._context_for))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", "") == "RunContext"]
    assert calls and all(any(k.arg == "taxonomy" for k in c.keywords) for c in calls)


def test_ac_8_42_one_state_root_name_everywhere():
    """AC-8.42 (OR-54, DX-154) — ★ every state-root read in `src/` uses ONE name.

    ⚠ Found 2026-10-06: the daily run read `PIPELINE_STATE`, training and ingest read
    `PIPELINE_STATE_DIR` — a model trained under one would be invisible to the other.
    """
    import re
    from pathlib import Path

    names = set()
    for path in Path("src").rglob("*.py"):
        names |= set(re.findall(r'environ\.get\(\s*"(PIPELINE_STATE\w*)"',
                                path.read_text(encoding="utf-8")))
    assert names == {"PIPELINE_STATE_DIR"}, names


def test_ac_8_42_the_retired_name_is_refused_not_ignored(monkeypatch, tmp_path):
    """AC-8.42 — P5: a set `PIPELINE_STATE` would otherwise be silently ignored."""
    from src.orchestration import entrypoint

    monkeypatch.setenv("PIPELINE_STATE", str(tmp_path / "old"))
    with pytest.raises(SystemExit, match="PIPELINE_STATE_DIR"):
        entrypoint._state_dir()
