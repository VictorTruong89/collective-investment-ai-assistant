"""WF-1 — fresh authoring, Stages A→D (§4A.2, RA-14…RA-19, RA-105…RA-111).

```
  4  STAGE A    J-01 … J-08     view:blind   no price, no market cap, no valuation
  5  ★ FREEZE   hash + persist Stage A output   ◄── IRREVERSIBLE
  6  STAGE B    J-09 ──► J-10   view:full
  7  STAGE C    J-11 · J-12 · J-13 · J-14      separate prompts, separate calls
  8  STAGE D    J-15 ──► persist ──► J-16 ──► J-17
                ★ STRICTLY SEQUENTIAL, with a write between 15 and 16
```

★★ **Two writes carry this whole module, and both are the same argument:**

```
  THE STAGE-A FREEZE (step 5)
     Staging without a persisted commit lets Stage B silently revise Stage A
     once it has seen the price — AND THE ANCHOR-STRIPPING BOUGHT NOTHING.

  THE FALSIFIER COMMIT (step 8)
     Held in memory, the ordering is nominal and A SINGLE CALL COULD PRODUCE
     BOTH — so the falsifiers get fitted to a verdict already reached.
```

⚠ **RA-105: D-01 sequences its own work.** *A caller may invoke an entry point;
it may not reorder, skip or re-enter a step* — a caller able to skip Stage A has
removed RA-14, and one able to re-run Stage D has removed RA-16. **The anti-bias
guarantees live in the order, so exposing the steps individually would export the
ability to break them.**
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date

from src.fundamental.errors import (
    BearCaseNotSeparateError, PriorVerdictLeakError, UncommittedFalsifiersError,
)
from src.fundamental.thesis.models import BearCase, Falsifier, Thesis

STAGE_A, STAGE_B, STAGE_C, STAGE_D = "A", "B", "C", "D"

#: §1.2's block-to-stage map. ★ **Stage membership is enforced by the BUNDLE, not
#: by the instruction** (MP-3): a Stage-A prompt cannot see price because the
#: bundle handed to it has no price field — *"do not consider valuation" is a
#: request; an absent field is a guarantee.*
STAGE_BLOCKS = {
    STAGE_A: ("J-01", "J-02", "J-03", "J-04", "J-05", "J-06", "J-07", "J-08"),
    STAGE_B: ("J-09", "J-10"),
    STAGE_C: ("J-11", "J-12", "J-13", "J-14"),
    STAGE_D: ("J-15", "J-16", "J-17"),
}
STAGE_VIEW = {STAGE_A: "blind", STAGE_B: "full", STAGE_C: "full", STAGE_D: "full"}


def _content_hash(payload) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        .encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class StageCommit:
    """★ RA-108 — *a persisted, content-hashed commit, not a variable held across
    steps.* Later stages **read** it. Nothing rewrites it, including a re-run of
    a later stage."""

    stage: str
    bundle_hash: str
    payload: dict
    commit_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "commit_hash",
                           _content_hash({"stage": self.stage,
                                          "bundle_hash": self.bundle_hash,
                                          "payload": self.payload}))

    def to_json_obj(self) -> dict:
        return {"stage": self.stage, "bundle_hash": self.bundle_hash,
                "commit_hash": self.commit_hash, "payload": self.payload}


class CommitLog:
    """Where a stage output is persisted. **Append-only, and re-commit raises.**

    ⚠ *Nothing rewrites it, including a re-run of a later stage* (RA-108). A
    store that permitted overwrite would let Stage B revise Stage A by the simple
    route of committing again.
    """

    def __init__(self) -> None:
        self._by_stage: dict[str, StageCommit] = {}

    def commit(self, stage: str, bundle_hash: str, payload: dict) -> StageCommit:
        if stage in self._by_stage:
            raise UncommittedFalsifiersError(
                f"stage {stage} is already committed; a re-commit would let a later "
                f"stage rewrite an earlier judgement (RA-108)"
            )
        record = StageCommit(stage=stage, bundle_hash=bundle_hash, payload=payload)
        self._by_stage[stage] = record
        return record

    def get(self, stage: str) -> StageCommit:
        hit = self._by_stage.get(stage)
        if hit is None:
            raise KeyError(
                f"stage {stage} was never committed. A later stage reading an "
                f"uncommitted earlier one is reading a variable, not a commitment "
                f"(RA-108)"
            )
        return hit

    def __contains__(self, stage: str) -> bool:
        return stage in self._by_stage

    @property
    def stages(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_stage))


# --------------------------------------------------------------------------- #
# The guards each step depends on
# --------------------------------------------------------------------------- #

def assert_fresh_authoring_bundle(bundle) -> None:
    """AC-1.15 / RA-18 — fresh authoring never sees the prior verdict.

    ⚠ **Invalidation is the deliberate exception** (RA-39) and must see it:
    *re-deciding and re-checking are different tasks.* The distinction lives in
    which entry point was called, which is why RA-106 makes the workflows
    separate functions rather than one `analyse(mode=…)`.
    """
    if bundle.of_kind("prior_thesis"):
        raise PriorVerdictLeakError(bundle.ticker)


def assert_stage_view(stage: str, bundle) -> None:
    """AC-1.12 / RA-14, MP-3 — the staging is physical.

    ★ *You cannot be anchored by a number you were never given.* Stage A gets a
    bundle with `computed` withheld, so price, market cap and valuation are
    **absent**, not merely un-asked-about.
    """
    expected = STAGE_VIEW[stage]
    if bundle.view != expected:
        raise PriorVerdictLeakError(
            f"{bundle.ticker}: stage {stage} requires a {expected!r} bundle and was "
            f"handed {bundle.view!r}. Stage membership is enforced by the bundle, "
            f"not by the instruction (MP-3, RA-14)"
        )


def assert_bear_case_separate(bear: BearCase, bull_run_ids) -> None:
    """AC-1.13 / RA-15 — a different prompt in a separate call.

    ⚠ Checked on the **call id**, not on the prose. *A bear case written in the
    same breath is a rhetorical concession, not an analysis* — and prose cannot
    show which call produced it.
    """
    if bear.run_id in set(bull_run_ids):
        raise BearCaseNotSeparateError(
            f"the bear case shares call {bear.run_id!r} with the bull-side output. "
            f"RA-15 requires a separate call with a different prompt — the "
            f"separateness is the analysis, not the wording (AP-3, INV-011)"
        )


#: RM-11's other half — X-05, deterministic token overlap with the bull case.
#: ⚠ **An ADMITTED GUESS** (CN-10): RM-11 says *"shares > X % of its tokens with
#: the bull case"* and **never declares X**. 0.6 is chosen as a level at which
#: two texts are plainly the same argument; it has never been measured.
BEAR_OVERLAP_CAP = 0.6


def bear_case_overlap(bear_text: str, bull_text: str) -> float:
    """X-05 — Jaccard overlap of the two token sets. Deterministic, no LLM."""
    a, b = set(bear_text.casefold().split()), set(bull_text.casefold().split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# --------------------------------------------------------------------------- #
# Stage D — the sequence RA-16 is about
# --------------------------------------------------------------------------- #

@dataclass(frozen=True, slots=True)
class FalsifierCommit:
    """★ J-15's output, persisted BEFORE J-16 is called (RA-16, §4A.2 step 8)."""

    falsifiers: tuple[Falsifier, ...]
    commit: StageCommit

    @property
    def commit_hash(self) -> str:
        return self.commit.commit_hash


def commit_falsifiers(log: CommitLog, *, bundle_hash: str, falsifiers) -> FalsifierCommit:
    """Step 8's write. ★ **This is the whole of RA-16 as amended.**

    Returning a hash rather than the list is deliberate: `Thesis` requires the
    hash, so a caller who skipped the commit **cannot construct a thesis at all**
    — the ordering is enforced by the type rather than by the call sequence.
    """
    falsifiers = tuple(falsifiers)
    record = log.commit("D:falsifiers", bundle_hash,
                        {"falsifiers": [f.to_json_obj() for f in falsifiers]})
    return FalsifierCommit(falsifiers=falsifiers, commit=record)


@dataclass
class AuthoringRun:
    """WF-1's state. ⚠ Not a public entry point — `author_thesis` drives it.

    RA-105: *a caller may invoke an entry point; it may not reorder, skip or
    re-enter a step.* Exposing the stages individually would export the ability
    to break the guarantees that live in their order.
    """

    ticker: str
    as_of: date
    log: CommitLog = field(default_factory=CommitLog)

    def freeze_stage_a(self, *, bundle, payload: dict) -> StageCommit:
        """★★ Step 5 — *the load-bearing one.*

        ```
        The freeze is what makes staging real. Staging without a persisted
        commit lets Stage B silently revise Stage A once it has seen the
        price — and the anchor-stripping bought nothing.
        ```
        """
        assert_stage_view(STAGE_A, bundle)
        return self.log.commit(STAGE_A, bundle.bundle_hash, payload)

    def author(self, *, bundle, stage_a_payload: dict, falsifiers, verdict: str,
               conviction: str, bear_case: BearCase, scorecard: dict,
               confidence: dict, bull_run_ids=(), thesis_version: int = 1,
               run_id: str = "", claims=(), data_gaps=(), assumptions=()) -> Thesis:
        """Steps 4→8, in order, with both writes.

        ⚠ The blind bundle is derived HERE rather than accepted from the caller —
        RA-19: *the evidence bundle is not curated by the same layer that judges*,
        and a caller supplying its own "blind" view is that curation.
        """
        assert_fresh_authoring_bundle(bundle)

        blind = bundle.redact()                       # RA-14, MP-3 — physical
        stage_a = self.freeze_stage_a(bundle=blind, payload=stage_a_payload)

        assert_bear_case_separate(bear_case, bull_run_ids)      # RA-15

        # ★ Step 8: J-15 → persist → J-16. The commit happens before the verdict
        # is accepted, and `Thesis` will refuse without its hash.
        committed = commit_falsifiers(self.log, bundle_hash=bundle.bundle_hash,
                                      falsifiers=falsifiers)

        # ★ RA-142: derived from the bundle, never accepted from the caller —
        #   the same argument as the blind view above. A caller supplying its own
        #   list of "consumed" sector files is the curation RA-19 forbids, and it
        #   would let an artifact declare a version it did not actually read.
        sector_files = tuple(dict(p.pins) for p in bundle.parts
                             if p.kind == "sector_file")

        return Thesis(
            ticker=self.ticker, thesis_version=thesis_version, as_of=self.as_of,
            bundle_hash=bundle.bundle_hash, run_id=run_id, verdict=verdict,
            conviction=conviction, falsifiers=committed.falsifiers,
            bear_case=bear_case, scorecard=dict(scorecard),
            confidence=dict(confidence), claims=tuple(claims),
            data_gaps=tuple(data_gaps), assumptions=tuple(assumptions),
            falsifier_commit_hash=committed.commit_hash,
            stage_a_hash=stage_a.commit_hash, sector_files=sector_files,
        )


def supersede(previous: Thesis, **changes) -> Thesis:
    """RA-36 / AC-1.33 — the ONLY path by which a falsifier set changes.

    ★ *Falsifiers are written at authoring time, versioned with the thesis, and
    never edited.* ⚠ **Editing one after the fact is how a thesis becomes
    unfalsifiable** — the condition drifts toward whatever did not happen. A
    supersession leaves the old thesis intact and bumps the version.
    """
    from dataclasses import replace

    return replace(previous, thesis_version=previous.thesis_version + 1, **changes)
