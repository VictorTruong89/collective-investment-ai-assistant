"""`F5` `AC-5.7` / `T1` — the golden set, replayed against a REAL recording.

★★ **This is the whole `B5` thread arriving.** Two golden cases, established by
the fund manager from MU's FY2025 Q3 10-Q, graded against a genuine
`claude-opus-5` extraction recorded by `F2` — with **no network call**, because
`D5` says CI replays recordings and never reaches a vendor.

⚠ It skips when the recording is absent (a fresh clone has no `.state/runs/`),
and that is the one thing about this file worth watching: a skip must stay
**visible**, or this becomes `DX-12` again — 41 tests that skipped everywhere
and told nobody.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.evaluation.golden.store import load_all  # noqa: E402
from src.evaluation.regression.run import run_regression  # noqa: E402

RUNS = REPO / ".state/runs"


def _replay():
    from tools.golden_replay import golden_replay
    from tools.run_extraction_once import build_bundle

    return golden_replay(RUNS, build_bundle().parts[0].content)


@pytest.fixture(scope="module")
def cases():
    found = list(load_all())
    if not found:
        pytest.skip("golden set is empty — F5 D2, the fund manager establishes them")
    return found


@pytest.mark.skipif(not RUNS.exists(), reason="no F2 recordings in .state/runs")
def test_ac_5_7_the_golden_set_replays_green(cases):
    """★★ The measurement, not the machinery: does the extractor still read
    this filing the way the fund manager established it?"""
    report = run_regression(cases, _replay())
    assert report.ok, "\n".join(
        f"{d['case_id']}: expected {d['expected']} but produced {d['produced']} "
        f"(established by {d['established_by']})" for d in report.diverged
    )
    assert len(report.passed) == len(cases)


@pytest.mark.skipif(not RUNS.exists(), reason="no F2 recordings in .state/runs")
def test_ac_5_7_the_suite_reds_when_a_reading_changes(cases):
    """⚠⚠ A golden suite that cannot go red is decoration.

    ★ The mutation is the one that matters: swap in the CUMULATIVE figure where
    the DISCRETE one was established. That is `fmp-api` trap 1 — the defect that
    cost 71 % on Micron — and if this case cannot catch it, it is not worth its
    upkeep.
    """
    from dataclasses import replace

    discrete = next(c for c in cases if c.expected.get("tags") == [])
    drifted = replace(discrete,
                      expected={**discrete.expected, "value": "14,028"})
    assert not run_regression([drifted], _replay()).ok


@pytest.mark.skipif(not RUNS.exists(), reason="no F2 recordings in .state/runs")
def test_ac_5_7_dropping_the_cumulative_tag_reds(cases):
    """⚠ `cumulative_ytd` is the scar tag — *do not subtract*. A case that
    stopped asserting it would let a YTD figure pass as a quarterly one."""
    from dataclasses import replace

    ytd = next(c for c in cases if c.expected.get("tags") == ["cumulative_ytd"])
    assert not run_regression([replace(ytd, expected={**ytd.expected, "tags": []})],
                              _replay()).ok


def test_the_golden_set_is_not_silently_empty():
    """⚠⚠ `DX-12`'s lesson: a check that skips everywhere tells nobody.

    ★ This one does NOT skip. If the golden set empties — a bad merge, a lost
    file — it fails loudly, because an empty baseline reports green forever.
    """
    assert list(load_all()), (
        "the golden set is empty. Either no case has been established yet "
        "(F5 D2) or one was lost — and an empty baseline passes forever"
    )
