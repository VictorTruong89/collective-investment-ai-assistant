"""`F5` — ⚠⚠ an EMPTY golden kind must be a DECLARED gap, never a silent one.

★★★ `test_the_golden_set_is_not_silently_empty` passes on **28 extraction
cases** — and `thesis` has **zero**. The guard was written when the whole set was
empty, so it asks *"is there anything?"* rather than *"is there anything per
kind?"*, and an empty kind is invisible to it.

⊘ `ranking` was a third kind until 2026-09-10; `F5` `D6` removed it as
**unaddressable** (`DX-62`), which is a closed question rather than a gap — so it
is not declared here, it simply no longer exists.

⚠ `thesis` is the kind `D2` calls a **judgement**, on the most expensive output
in the system. Its emptiness is the single largest measurement gap in the
project, and nothing in CI says so.

★★ This file does not demand cases exist — they legitimately cannot yet (see
`GAPS`). It demands the **reason** exists, which is `CN-10`'s rule: *"'admitted
guess' is an acceptable answer; **silence is not**."*
"""

from __future__ import annotations

import pytest

from src.evaluation.golden.store import KINDS, coverage

#: ⚠ Why each kind is under-covered. ★ An entry here is a DEBT, not an excuse.
#:
#: ⚠⚠ **`covers` is the field that makes this survive partial progress.** The
#: first version keyed expiry on *"the kind has ≥1 case"*, which conflates
#: **"a case exists"** with **"the debt is paid"**. Those are the same thing
#: only when one case closes the kind — and `DX-64` created exactly the case
#: where they are not: a single `J-09` block yields a recordable call, but a
#: `CT-9.2` thesis is **17 blocks × k=3**, so one case would have deleted the
#: declaration while the real gap stood. ★ That is `DX-63` recurring inside the
#: fix for `DX-63`, and `covers` is what stops it.
#:
#: `covers` = how many cases would mean the debt is actually paid.
#: `None` = the kind is wholly blocked and no number of cases is expected yet.
GAPS: dict[str, dict] = {
    "thesis": {
        # ⬜ A `CT-9.2` thesis is 17 J-blocks × K_RUNS=3. One signed `J-01`
        #    case would be PARTIAL coverage, not payment — so `covers` stays
        #    None until the block set that constitutes a thesis is declared.
        "covers": None,
        "why": (
            "⛔ NO J-BLOCK IS DECLARED (DX-64). `e_blocks.py` ships "
            "BLOCKS={'E-01','E-02'}; `author.py`'s STAGE_BLOCKS names J-01…J-17 "
            "and none has prompt text in `src/`, so `author_once` cannot "
            "construct a judgement block and no thesis can be recorded at any "
            "price. ★ DX-23's shape exactly, one domain over. ⚠ A full CT-9.2 "
            "thesis is 17 blocks x K_RUNS=3 = 51 calls (~$11-$27); one J-09 "
            "block alone yields a recordable call — DONE 2026-09-10, $0.3708, "
            "run-2026-09-11T025139-mu-j01 — but it is NOT a CT-9.2 thesis and "
            "cannot price QR-20 (DX-60). ⚠ STILL partial: one case is drafted "
            "in thesis.pending.yaml awaiting D2 signature, and 16 of 17 blocks "
            "remain undeclared."
        ),
    },
}


def test_every_empty_kind_has_a_DECLARED_reason():
    """⚠⚠ The rule: a kind may be empty; it may not be **quietly** empty."""
    undeclared = [k for k, n in coverage().items() if n == 0 and k not in GAPS]
    assert not undeclared, (
        f"{undeclared} have no golden cases and no recorded reason. ⚠ An empty "
        "baseline reports green forever, and `test_the_golden_set_is_not_"
        "silently_empty` cannot see it because another kind is populated.")


def test_a_declaration_EXPIRES_ONLY_WHEN_THE_DEBT_IS_PAID():
    """★★ What stops `GAPS` becoming permanent cover — **without** letting one
    partial case erase a standing gap.

    ⚠⚠ The first version fired on *"the kind has ≥1 case"*. `DX-64` showed why
    that is wrong: one `J-09` block is recordable, a `CT-9.2` thesis is 17
    blocks × k=3, and deleting the declaration on the first case would have
    hidden the remaining gap — `DX-63` recurring inside its own fix.

    ★ So expiry is keyed on `covers`: the entry must go only when the kind has
    reached the coverage the declaration itself named.
    """
    have = coverage()
    stale = [k for k, g in GAPS.items()
             if g["covers"] is not None and have.get(k, 0) >= g["covers"]]
    assert not stale, (
        f"{stale} reached its declared `covers` — delete the entry, the debt "
        "is paid")


def test_partial_coverage_keeps_the_declaration_and_UPDATES_it():
    """★★★ The case `DX-64` created. A kind with SOME cases but fewer than
    `covers` still carries its reason — ⚠ and the reason must have been
    updated to say what is still missing, not left describing an empty kind."""
    have = coverage()
    for kind, g in GAPS.items():
        n = have.get(kind, 0)
        if n > 0 and (g["covers"] is None or n < g["covers"]):
            assert "partial" in g["why"].lower() or "still" in g["why"].lower(), (
                f"{kind} has {n} case(s) but its declaration still reads as "
                "wholly empty — say what remains")


@pytest.mark.parametrize("kind", sorted(GAPS))
def test_a_declared_gap_says_WHY_and_names_its_blocker(kind):
    """★ A reason that does not distinguish *blocked* from *not yet done* is not
    a reason. ⚠ `thesis` is waiting on a RUN, not on judgement — a distinction a
    shared shrug would hide."""
    why = GAPS[kind]["why"]
    assert len(why) > 80, "a one-liner is a shrug, not a declaration"
    assert "DX-" in why, "name the finding that records the blocker"


def test_the_coverage_report_still_sees_every_declared_kind():
    """⚠ A gap declared for a kind that no longer exists is dead weight, and a
    kind missing from `coverage()` would be invisible to both tests above."""
    assert set(GAPS) <= set(KINDS), f"GAPS names unknown kinds: {set(GAPS)-set(KINDS)}"
    assert set(coverage()) == set(KINDS)


def test_extraction_is_NOT_in_gaps_because_it_is_populated():
    """★ The positive control: the mechanism must distinguish a real gap from a
    filled one, or it would accept a declaration for everything."""
    assert "extraction" not in GAPS
    assert coverage()["extraction"] > 0
