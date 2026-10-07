"""D-08 shim — AC-8.1…8.5, 8.10…8.14a, 8.19 (L3 BS-12: a shim, not D-08).

Tier: unit + contract. ⚠ Retry, budgets, cadence, locks and checkpoints are
**B6** and are deliberately untested here — see the blueprint §9.
"""

from __future__ import annotations

import ast
from datetime import date, datetime, timezone
import re
from pathlib import Path

import pytest

from src.orchestration import (
    INCOMPLETE, JobRun, ManifestImmutableError, ManifestStore, RunOutcome, SUCCESS,
    b3_stubs, build_manifest, config_hash, new_run_id, skeleton_plan as plan, topological_order,
)

AS_OF = date(2026, 8, 23)


def manifest(**kw):
    base = dict(data_as_of=AS_OF, config={"a": 1}, stubs=b3_stubs())
    return build_manifest(**{**base, **kw})


def test_ac_8_1_no_orchestration_function_returns_a_derived_value():
    """AC-8.1 — ★ OR-1.

    ```
    ORCHESTRATION INVOKES WORK. IT NEVER PERFORMS WORK.

    A computation inside an entrypoint has NO SPEC, NO OWNER and NO
    ACCEPTANCE CRITERIA — it is invisible to the whole SDD process by
    construction.
    ```

    Checked structurally: no arithmetic on market or fundamental data. The shim
    may sort, hash and time; it may not add, divide or compare prices.
    """
    forbidden_calls = {"mean", "std", "sum", "rank", "zscore", "corr", "var"}
    for path in sorted(Path("src/orchestration").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_calls, (
                    f"{path}:{node.lineno} calls .{node.func.attr}() — that is a "
                    f"computation, and it belongs to the domain that owns it (OR-1)"
                )


def test_ac_8_2_orchestration_performs_no_book_write():
    """AC-8.2 — OR-2. ⚠ *An inference run writing positions.json means a
    PREDICTION is editing the RECORD.*"""
    # ★ The rule is *no IMPORT*, not *no mention*. ⚠ This used to be a bare
    #   substring check, which also rejected the **sanctioned** seam: a `Job`
    #   whose `invokes` names a D-11 entrypoint as a dotted string, resolved at
    #   run time. Forbidding that left orchestration with no legal way to invoke
    #   D-11 at all — the opposite of what OR-2 says.
    offenders = []
    for path in Path("src/orchestration").rglob("*.py"):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if re.match(r"^(from|import)\s+src\.recording\b", stripped):
                offenders.append(f"{path}:{lineno} {stripped}")
    assert offenders == [], (
        f"the shim may INVOKE a D-11 entrypoint by dotted name; it may not "
        f"import the book directly — {offenders}"
    )


def test_ac_8_3_no_domain_imports_orchestration():
    """AC-8.3 — OR-3, the mirror of ST-2. Grep-checkable in CI."""
    from tests_src.architecture import or_3, scan
    assert or_3(scan()) == []


def test_ac_8_4_and_8_5_no_gateway_and_no_order_placement():
    """AC-8.4 / AC-8.5 — OR-4, OR-29.

    ★ *An automated schedule that could trade is the single most dangerous thing
    this domain could become, and it must be structurally impossible rather than
    merely absent.*
    """
    from tests_src.architecture import scan, st_5
    assert st_5(scan()) == []
    import src.orchestration as o
    forbidden = {"place_order", "submit_order", "execute", "trade", "buy", "sell"}
    assert not (forbidden & set(o.__all__))


def test_t2_the_job_graph_is_declared_data_and_inspectable_without_running():
    """T-2 — *Job dependencies are declared data, not control flow buried in a
    `main()`.*"""
    assert plan() == tuple(plan()), "a value, not a side effect"
    order = topological_order()
    assert order[0] == "calendar_check", "DE-31 — before the first feature"
    assert order.index("features") > order.index("calendar_check")
    assert order.index("compose") > max(order.index("gate"), order.index("risk"))
    assert order[-1] == "deliver"


def test_ac_8_10_a_manifest_is_written_before_any_job_runs(tmp_path):
    """AC-8.10 — OR-9. ★ *Without this a run cannot be reproduced, and INV-2 is
    unenforceable at the only layer that can enforce it.*"""
    m = manifest()
    path = ManifestStore(tmp_path).write(m)
    assert path.exists()
    written = ManifestStore(tmp_path).read(m.run_id)
    assert written["run_id"] == m.run_id


def test_ac_8_11_the_manifest_carries_every_required_field():
    """AC-8.11 — OR-9: git sha, dirty flag, config hash, data as_of, seed, inputs."""
    obj = manifest().to_json_obj()
    for key in ("run_id", "code", "config_hash", "data_as_of", "decision_anchor",
                "seed", "inputs", "budgets", "preconditions", "stubs"):
        assert key in obj, key
    assert set(obj["code"]) == {"git_sha", "dirty"}


def test_ac_8_12_a_dirty_tree_is_marked_dirty():
    """AC-8.12 — OR-11. ⚠ *Silently recording a clean sha for a modified tree is
    worse than not recording one.*"""
    assert isinstance(manifest().dirty, bool)


def test_ac_8_13_two_runs_in_the_same_second_have_distinct_ids():
    """AC-8.13 — OR-12. *A run id must survive a clock change.*"""
    at = datetime(2026, 8, 23, 14, 0, 0, tzinfo=timezone.utc)
    assert new_run_id("g", at) != new_run_id("g", at)


def test_ac_8_14_a_written_manifest_cannot_be_mutated(tmp_path):
    """AC-8.14 — OR-13, INV-005/006. A rerun creates a NEW manifest."""
    store = ManifestStore(tmp_path)
    m = manifest()
    store.write(m)
    with pytest.raises(ManifestImmutableError, match="never edits the old one"):
        store.write(m)


def test_ac_8_14a_every_stub_is_declared_in_the_manifest():
    """AC-8.14a — ★★ OR-43 / L3 BS-27.

    ```
    A stub that is indistinguishable from a real implementation in the RECORD
    is how a placeholder survives into production.
    ```

    And `stubs: []` is the production value: the key is present even when empty,
    because an absent key is not an empty list.
    """
    m = manifest()
    domains = {s.domain for s in m.stubs}
    assert domains == {"D-01", "D-05"}
    for s in m.stubs:
        assert s.behaviour and s.replaced_at and s.rule
    assert manifest(stubs=()).to_json_obj()["stubs"] == []


def test_ac_8_15_identical_config_gives_an_identical_hash():
    """AC-8.15 — OR-10. ★ *Determinism has no owner if D-08 does not own the manifest.*"""
    assert config_hash({"b": 2, "a": 1}) == config_hash({"a": 1, "b": 2})
    assert config_hash({"a": 1}) != config_hash({"a": 2})


def test_ac_8_19_partial_success_is_failure_and_produces_no_artifact():
    """AC-8.19 — ★ OR-16/DC-3.

    *Both real incidents in this repo came from a downstream consumer treating a
    degraded upstream as usable.*
    """
    now = datetime.now(timezone.utc)
    incomplete = RunOutcome("r", INCOMPLETE, (JobRun("a", SUCCESS, 1, 0.1),), now, now)
    assert incomplete.produces_human_artifact is False
    assert RunOutcome("r", SUCCESS, (), now, now).produces_human_artifact is True


_T0 = datetime(2026, 10, 6, 14, 0, tzinfo=timezone.utc)


def _crash_on_replace(monkeypatch):
    """Kill the write at its last step — the moment a non-atomic writer has
    already put half a file on disk."""
    import src.orchestration.state.manifest_store as store_mod

    def boom(*_a, **_k):
        raise KeyboardInterrupt("killed mid-write")
    monkeypatch.setattr(store_mod.os, "replace", boom, raising=True)


def test_ac_8_20_a_killed_manifest_write_leaves_no_half_file(tmp_path, monkeypatch):
    """AC-8.20 — OR-17 / INV-032. ★ *A killed run leaves either the old state or the
    new one, never a half-written one.* ✏ Written 2026-10-06 (L9 §9 O5): the store
    used plain `write_text`, so a kill mid-write left a truncated `manifest.json` —
    which `read()` would then fail on, or worse, which OR-13 would refuse to replace."""
    store = ManifestStore(tmp_path)
    m = manifest()
    _crash_on_replace(monkeypatch)
    with pytest.raises(KeyboardInterrupt):
        store.write(m)
    run_dir = tmp_path / m.run_id
    assert not (run_dir / "manifest.json").exists(), "no half-written manifest"
    assert not list(run_dir.glob("*.tmp")), "the temporary file is cleaned up"


def test_ac_8_20_a_killed_outcome_write_keeps_the_old_outcome(tmp_path, monkeypatch):
    """AC-8.20 — the OLD state survives a killed overwrite, byte for byte."""
    store = ManifestStore(tmp_path)
    m = manifest()
    store.write(m)
    first = RunOutcome(run_id=m.run_id, status=INCOMPLETE, jobs=(),
                       started_at=_T0, ended_at=_T0)
    path = store.write_outcome(first)
    before = path.read_bytes()
    _crash_on_replace(monkeypatch)
    with pytest.raises(KeyboardInterrupt):
        store.write_outcome(RunOutcome(run_id=m.run_id, status=SUCCESS, jobs=(),
                                       started_at=_T0, ended_at=_T0))
    assert path.read_bytes() == before
