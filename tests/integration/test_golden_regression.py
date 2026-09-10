"""`F5` `AC-5.7` / `T1` — the golden set, replayed against a REAL recording.

★★ **This is the whole `B5` thread arriving.** Two golden cases, established by
the fund manager from MU's FY2025 Q3 10-Q, graded against a genuine
`claude-opus-5` extraction recorded by `F2` — with **no network call**, because
`D5` says CI replays recordings and never reaches a vendor.

⚠⚠ **It used to skip, and that was `DX-12` reintroduced in the very file that
warns about it.** The recording lived under `.state/runs/`, which `.gitignore`
excludes — so these tests ran on exactly one laptop and skipped silently
everywhere else. ★ The recording is now a **version-controlled fixture**
(`tests_src/fixtures/recordings/`, 36 KB) and **nothing here skips**.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.evaluation.golden.store import load_all  # noqa: E402
from src.evaluation.regression.run import run_regression  # noqa: E402


def _replay():
    from tools.golden_replay import golden_replay

    # ★ No root AND no bundle_text: the committed fixtures, with each recording
    #   resolving its OWN filing via its `filing.json`.
    # ⚠ Passing one `bundle_text` was correct with a single filing and became a
    #   bug the moment a second joined — AMD's cases were parsed against MU's
    #   text, and every quote "was not in the bundle".
    return golden_replay()


@pytest.fixture(scope="module")
def cases():
    # ⚠ No skip. An empty golden set is a FAILURE, not a reason to go quiet —
    #   `test_the_golden_set_is_not_silently_empty` says why.
    return list(load_all())


def test_ac_5_7_the_golden_set_replays_green(cases):
    """★★ The measurement, not the machinery: does the extractor still read
    this filing the way the fund manager established it?"""
    report = run_regression(cases, _replay())
    assert report.ok, "\n".join(
        f"{d['case_id']}: expected {d['expected']} but produced {d['produced']} "
        f"(established by {d['established_by']})" for d in report.diverged
    )
    assert len(report.passed) == len(cases)


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


def test_ac_5_7_dropping_the_cumulative_tag_reds(cases):
    """⚠ `cumulative_ytd` is the scar tag — *do not subtract*. A case that
    stopped asserting it would let a YTD figure pass as a quarterly one."""
    from dataclasses import replace

    ytd = next(c for c in cases if c.expected.get("tags") == ["cumulative_ytd"])
    assert not run_regression([replace(ytd, expected={**ytd.expected, "tags": []})],
                              _replay()).ok


def test_the_recording_is_version_controlled_not_local_state():
    """⚠⚠ `DX-12`'s shape, guarded. If the recording ever moves back under
    `.state/` these tests would skip everywhere and tell nobody."""
    from tools.golden_replay import RECORDINGS
    assert RECORDINGS.exists(), "the golden recording fixture is missing"
    assert ".state" not in str(RECORDINGS), (
        "the recording is under gitignored run state — the golden regression "
        "would run on one machine only (DX-12)"
    )
    assert list(RECORDINGS.glob("*/trace.jsonl")), "no recording in the fixture"


def test_the_golden_set_is_not_silently_empty():
    """⚠⚠ `DX-12`'s lesson: a check that skips everywhere tells nobody.

    ★ This one does NOT skip. If the golden set empties — a bad merge, a lost
    file — it fails loudly, because an empty baseline reports green forever.
    """
    assert list(load_all()), (
        "the golden set is empty. Either no case has been established yet "
        "(F5 D2) or one was lost — and an empty baseline passes forever"
    )


def test_the_recording_is_not_from_a_RETIRED_prompt_version():
    """⚠⚠ A prompt bump retires every recording made under the old version.

    `E-01` went `v1` → `v2` on 2026-09-07 because `v1` let a paraphrase through.
    The golden set grades a RECORDED call — so after a bump it is grading a
    prompt this repo no longer ships, and it would go on reporting green about
    behaviour that has been replaced.

    ★★ This test is deliberately the loud kind. It does not skip and it does not
    warn: a regression suite pinned to a retired prompt is worse than no suite,
    because it reports green about the past.
    """
    import json

    from src.fundamental.prompts.e_blocks import BLOCKS
    from tools.golden_replay import RECORDINGS

    # ⚠ Only the recordings LIVE cases actually grade. A recording staged for
    #   work in progress (see extraction.pending.yaml) is not "the golden set
    #   grading a retired prompt" — it is not being graded at all, and failing
    #   on it would punish preparation rather than staleness.
    referenced = {c.input_ref.split("/")[0] for c in load_all()}
    stale = []
    for log in sorted(RECORDINGS.glob("*/trace.jsonl")):
        if log.parent.name not in referenced:
            continue
        for line in log.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec.get("type") != "ExternalCall":
                continue
            # ⚠⚠ The version to compare against is the one THIS BLOCK ships,
            #   not `E-01`'s. ★ Hardcoding `E01_CURRENT_VERSION` was correct
            #   while one block existed and became a trap the moment `E-02`
            #   earned a case: it would have failed a fresh `E-02 v2` recording
            #   for not being `E-01`'s `v3` — a stale-prompt alarm firing on
            #   the newest recording in the repo.
            block_id = (rec.get("step_id") or "").split(":")[-1]
            want = BLOCKS.get(block_id, (None, None, None))[2]
            if want is None:
                stale.append(f"{log.parent.name}: step {rec.get('step_id')!r} "
                             f"names no declared block — nothing states which "
                             f"prompt version it should carry")
                continue
            got = rec.get("prompt_version")
            if got != want:
                stale.append(f"{log.parent.name} ({block_id}): recorded under "
                             f"{got!r}, repo ships {want!r}")
    assert not stale, (
        "the golden set grades a recording made under a retired prompt:\n  "
        + "\n  ".join(stale)
        + "\n★ Re-record with the current prompt, or the suite measures the past."
    )


def test_every_recorded_quote_still_resolves_in_its_filing():
    """⚠⚠ `DX-36` — **the drift detector that was only ever a docstring.**

    `tools/promote_recording.py` says the request payload is *"replaced by its
    `bundle_hash`"* and that on a re-render the recording *"disagrees
    **loudly**"*. Neither is true: it writes `{"__elided__": …, "chars": …}`
    with **no hash anywhere**, and nothing in the repo compares one. The guard
    named in the comment does not exist.

    ★★ That is `DX-12`'s exact shape one level up — not a check that skips, but
    a check that was never written, described in prose as though it had been.

    ★★★ And a hash would have been the WRONG guard. `DX-35` re-rendered both
    fixtures to strip page furniture; a hash-equality guard fires on *any* byte
    change, so it would have demanded ~$1.20 of re-recording for a change
    measured to alter nothing. What actually matters is not whether the bytes
    moved but whether the recording still MEANS what it meant — so this checks
    the thing the golden set is built on: **every quote still resolves.**
    """
    import json

    from tools.golden_replay import RECORDINGS
    from tools.run_extraction_once import _locate

    REPO_ = pathlib.Path(__file__).resolve().parents[2]
    broken = []
    for manifest in sorted(RECORDINGS.glob("*/filing.json")):
        run = manifest.parent
        text = (REPO_ / json.loads(manifest.read_text())["fixture"]).read_text(
            encoding="utf-8")
        for pf in sorted((run / "trace/payloads").glob("*.json")):
            resp = json.loads(pf.read_text()).get("response")
            body = resp.get("text") if isinstance(resp, dict) else resp
            if not isinstance(body, str):
                body = json.dumps(body)
            for row in json.loads(body).get("items", []):
                quote = row.get("quote") or ""
                if quote and _locate(text, quote)[0] < 0:
                    broken.append(f"{run.name}: {row.get('evidence_id')} "
                                  f"{quote[:50]!r}")
    assert not broken, (
        "a recorded quote no longer resolves in its filing fixture — the "
        "document drifted under the recording and the golden set is grading "
        "text the model never saw:\n  " + "\n  ".join(broken[:10])
    )
