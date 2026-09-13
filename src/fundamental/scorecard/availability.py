"""`RA-32` — which rubric levels a given bundle can actually support (`DX-82`).

★★★ **`RA-32`: a level selected without its evidence present in the bundle is a
FAILED selection, not a low-confidence one.** Every `RubricLevel` names its
`evidence_required`, and `b43_v1.py` is explicit that this includes the LOW
levels — *"a level declaring none would be unconditionally available, which is a
level nothing can fail to support."*

⚠⚠ **What this module refuses to do is the point.** The tempting implementation
offers all five levels and lets the model pick; that is one line, and it discards
the rubric's entire discipline. `J-03`/`J-04`/`J-05` were answered ungated on
2026-09-12 and returned 1 / 3 / 3 — numbers that rest on nothing structural.

★ Pure, no I/O, no model. The bundle says what it carries; this says what that
permits. `AP-5` — the question *"is this evidence present?"* is a computation.
"""

from __future__ import annotations

from src.fundamental.scorecard.models import Rubric

#: `DX-99` — the prefix of an evidence requirement satisfied by a stated absence.
SEARCHED = "searched:"


class NoAvailableLevel(Exception):
    """⚠ Not one level's evidence is present — the block cannot be scored.

    ★★ `P5`, and the distinction that matters: this is **not** "score it 0". A
    floor score is a JUDGEMENT that the evidence was looked for and found
    wanting; this is the statement that the rubric could not be applied at all.
    ⚠ Collapsing the two would let a wiring gap read as an analytical finding —
    which is exactly what an ungated `capital_allocation = 0` did.
    """


def evidence_ids_in(bundle) -> frozenset[str]:
    """The evidence ids a bundle actually carries.

    ⚠⚠ **Raw filing text carries NONE**, and that is not a technicality. An
    evidence id (`seg.revenue`, `cap.action`) is an **extraction output** —
    `MP-4`. A filing contains the facts from which one would be extracted; it
    does not contain the extraction. ★ `RA-19`: assembly is mechanical, so a
    bundle that has not been through the E-blocks has not got the evidence, and
    saying otherwise here would let the judging layer assume its own inputs.

    ★ A part declares its ids in `pins["evidence_ids"]`.

    ★★ `DX-99` — and `searched:<id>` for every id in `pins["searched_ids"]`:
    the block ran to completion, passed `X-01`, and explicitly RETURNED that
    item, `found` or `not_found`. A rubric level cites `searched:ng.adjustment`
    when its criterion rests on ABSENCE ("no non-GAAP add-back") — which a
    found-only id can never support for the company that has none.
    ⚠ `searched:` is NOT extraction (`RA-66` is unchanged): a `not_found` is the
    model's stated, located answer, and `X-01` does not verify it.
    """
    ids: set[str] = set()
    for part in bundle.parts:
        pins = part.pins or {}
        ids.update(pins.get("evidence_ids") or ())
        ids.update(f"{SEARCHED}{i}" for i in (pins.get("searched_ids") or ()))
    return frozenset(ids)


def available_levels(rubric: Rubric, present: frozenset[str]) -> tuple[int, ...]:
    """The scores whose `evidence_required` is fully satisfied by `present`.

    ⚠ **All of a level's evidence, not any of it.** `RA-32` reads *"items are
    absent"* — a level citing three evidence ids is a criterion a reader checks
    against three things, and two of them is an unchecked criterion.
    """
    return tuple(level.score for level in rubric.levels
                 if set(level.evidence_required) <= present)


class PartialRubricEvidence(NoAvailableLevel):
    """⛔ `DX-98` — SOME levels are available, but not all. The block is refused.

    ★★★ A subclass on purpose: every caller that already refuses on
    `NoAvailableLevel` refuses on this too, so no caller can score a partial
    rubric by forgetting a second `except`.
    """


def require_levels(rubric: Rubric, present: frozenset[str]) -> tuple[int, ...]:
    """The levels a rubric block may be offered — ALL of them, or it refuses (`P5`).

    ⛔⛔ **`DX-98`, decided by Victor 2026-09-12: a dimension is scored only when
    EVERY one of its levels is available.** The rubrics give higher scores more
    evidence, so a partial bundle removes levels from the TOP: measured on MU,
    with `E-10`/`E-12` truncated, `J-05`/`J-06` were offered `levels=(0,)` — one
    option, a floor score by construction, on a 10-Q that discloses dividends
    and buybacks. ★ A missing input must never be able to move a score; with
    the full range or nothing, it cannot.
    ✗ Rejected: refusing only below two levels (still biased low); scoring the
    partial range and recording the gap (the gap would not survive into the
    number anyone reads).
    """
    levels = available_levels(rubric, present)
    everything = tuple(level.score for level in rubric.levels)
    if levels and levels != everything:
        needed = sorted({e for lv in rubric.levels for e in lv.evidence_required})
        raise PartialRubricEvidence(
            f"{rubric.dimension}@v{rubric.version}: only levels {levels} of "
            f"{everything} have their evidence. Missing: "
            f"{sorted(set(needed) - present)}. ⛔ DX-98 — a partial rubric is "
            f"refused: the levels it loses are the HIGH ones, so scoring it would "
            f"let a missing input push the score down. This is NOT a score of 0."
        )
    if not levels:
        needed = sorted({e for lv in rubric.levels for e in lv.evidence_required})
        raise NoAvailableLevel(
            f"{rubric.dimension}@v{rubric.version}: NO level's evidence is "
            f"present. The rubric needs {needed}; the bundle carries "
            f"{sorted(present) or 'nothing'}. ⚠ RA-32 — this block cannot be "
            f"scored, and that is NOT a score of 0: a floor is a judgement that "
            f"the evidence was looked for and found wanting, this is the "
            f"statement that the rubric could not be applied at all."
        )
    return levels
