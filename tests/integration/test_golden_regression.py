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


#: ⚠⚠ `DX-76` — envelopes the golden set may grade, BESIDES the current ones.
#:
#: ★ `"None"` = a recording made before `envelope_hash` existed. It means
#: **unknown**, never *"no envelope"* — that case is the string `"none"`.
#: ⚠⚠ The four recordings promoted earlier on 2026-09-11 WERE made under the
#: envelope, but nothing in the artefact proves it: `promote_recording` elides
#: the composed prompt. ★★ That is `DX-76`'s whole point, seen from the inside —
#: the provenance is known to the session that made them and to nobody else,
#: which is precisely the state the field exists to end. They are admitted here
#: rather than re-recorded at ~$1.7 to buy a hash we already know the value of.
#:
#: ✏ `DX-111` (2026-09-15) — ★ the Stage-A envelope WITHOUT `S-8`. Every graded judgement
#: recording (J-01, J-05, J-06, J-07, J-08) was made before Stage A composed `S-8`; the
#: split is held on purpose until the next paid Stage-A re-record, and declared here so it
#: stays visible (`DX-76`).
from src.fundamental.prompts.envelope import envelope_hash as _envelope_hash  # noqa: E402

DECLARED_ENVELOPES = {"None", _envelope_hash("judgement", stage_a=True)}


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
    stopped asserting it would let a YTD figure pass as a quarterly one.

    ★★ `DX-73` — all 6 cumulative cases were withdrawn on 2026-09-11 (they
    asserted a `period.start` the filing never states) and re-established by the
    fund manager the same day with `start: null`. ⚠ While they were out this
    xfailed against a written declaration rather than raising a bare
    `StopIteration`; the declaration was deleted the moment they returned.
    """
    from dataclasses import replace

    ytd = [c for c in cases if c.expected.get("tags") == ["cumulative_ytd"]]
    assert ytd, (
        "no live case asserts `cumulative_ytd` — the scar tag is UNGUARDED. "
        "⚠ A YTD figure could pass as a quarterly one and nothing would notice. "
        "★ `DX-73` withdrew all 6 such cases on 2026-09-11 and this assertion "
        "xfailed against a written declaration while they were out; the 6 were "
        "re-established by the fund manager the same day and the declaration "
        "was DELETED with them. A declaration that outlives its reason is how a "
        "gap becomes permanent (DX-63)."
    )
    assert not run_regression([replace(ytd[0], expected={**ytd[0].expected, "tags": []})],
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


def test_dx_76_the_golden_set_does_not_grade_two_PROMPT_REGIMES_at_once():
    """★★★ `DX-76` — `prompt_version` names HALF the prompt.

    ⚠⚠ `DX-67` composed `S-1`…`S-6` in front of every call and bumped no
    version, so `E-02` is `v2` before and after and the retired-prompt guard
    could not see the change. This one can: it compares the recorded
    `envelope_hash` across everything the golden set actually grades.

    ★ It does NOT demand a particular envelope — only that the set does not
    silently mix regimes. A deliberate split and an invisible one look identical
    in CI, and that is the defect being closed. ⚠ A split held ON PURPOSE must
    be DECLARED, exactly as `DX-73`'s coverage loss is.
    """
    import json

    from src.fundamental.prompts.envelope import envelope_hash
    from tools.golden_replay import RECORDINGS

    referenced = {c.input_ref.split("/")[0] for c in load_all()}
    seen: dict[str, list[str]] = {}
    for log in sorted(RECORDINGS.glob("*/trace.jsonl")):
        if log.parent.name not in referenced:
            continue
        for line in log.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec.get("type") == "ExternalCall":
                seen.setdefault(str(rec.get("envelope_hash")), []).append(log.parent.name)
    # ★★ The CURRENT envelopes, computed live rather than hardcoded — the same
    # discipline `test_ra_13_*` applies to block text. ⚠ Extraction and
    # judgement legitimately differ (`S-7` is Stage-A only), so "one envelope
    # for the whole set" would be wrong; what must hold is that every graded
    # recording carries an envelope this repo STILL SHIPS.
    current = {envelope_hash("extraction"), envelope_hash("judgement", fresh=True),
               envelope_hash("judgement", stage_a=True, fresh=True)}      # ✏ DX-111
    unexpected = {h: r for h, r in seen.items()
                  if h not in current and h not in DECLARED_ENVELOPES}
    assert not unexpected, (
        f"the golden set grades a recording under an envelope this repo no "
        f"longer ships: {sorted(unexpected)}\n  "
        + "\n  ".join(f"{h}: {sorted(set(r))}" for h, r in unexpected.items())
        + "\n★ Re-record under one envelope, or declare the split and say why "
          "(DX-76). ⚠ A split held on purpose and one nobody noticed look the "
          "same from here."
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
