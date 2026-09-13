"""`earnings_quality@v3` — `DX-99`. Published 2026-09-13 at Victor Truong's instruction.

⛔⛔ **The defect `v2` has, measured on MU 2026-09-12.** Every `earnings_quality`
level requires `ng.adjustment` to be FOUND. `E-04` on MU's 10-Q returned all five
items `not_found` — *"no non-GAAP measure is presented"* — so `J-04` refused at
EVERY level, and would for any issuer that reports no adjusted figures.

★★★ **`v2`'s own note says the opposite should happen:** *"the non-GAAP
reconciliation is required at every level because its ABSENCE is itself the
finding."* The intent was right; the evidence form could not express it. An id in
`evidence_required` is satisfied only by a FOUND item (`RA-66`), so an absence can
never be evidence — and levels 4 and 3 are criteria ABOUT absence (*"no
recurring non-GAAP add-back and no accounting-policy change"*).

★ **The fix: `searched:<id>`** (`scorecard/availability.py::SEARCHED`). It is
satisfied when the E-block ran to completion, passed `X-01`, and explicitly
RETURNED that item — `found` or `not_found`. A company with no non-GAAP measures
now has a checkable answer instead of an unscoreable one.

⚠⚠ **What `v3` changes: only `evidence_required`** — `ng.adjustment` →
`searched:ng.adjustment` and `ap.change` → `searched:ap.change` at every level.
Not one `criterion` string and not one score moves (asserted byte-for-byte), for
the reason `DX-86` gave: an evidence-form change and a criteria change mixed
together make a later score move unattributable. `seg.op_income` (level 4) stays a
FOUND requirement — segment income is a fact that exists or does not.

⚠ **The honest cost.** `searched:` rests on `not_found`, which `X-01` does not
verify: a model could claim it looked and did not find. The schema requires a
quote and a note on every `not_found` (`MP-7`), so the claim is located, but it is
the model's. ★ Recorded in `DX-99`; a deterministic check that a `not_found`'s
cited "where I looked" text is in the filing is the natural next guard.

⚠ **Only `earnings_quality`.** The same shape exists elsewhere — `dm.covenant`
for a company with no covenants, `cp.statement` for one that states no priorities,
`cx.capacity` with no industry material — and each is a separate CRITERIA
question, deliberately not generalised here (`DX-99`).
"""

from __future__ import annotations

from src.fundamental.scorecard.models import Rubric, RubricLevel
from src.fundamental.scorecard.rubrics.b43_v1 import B43_RUBRICS
from src.fundamental.scorecard.rubrics.b43_v2 import (
    B43_V2_RUBRICS,
    BALANCE_SHEET_RESILIENCE_V2,
    CAPITAL_ALLOCATION_V2,
    EARNINGS_QUALITY_V2,
)

#: `v2` id → `v3` requirement. ★ The ONLY difference between the two rubrics.
V3_SEARCHED = {"ng.adjustment": "searched:ng.adjustment",
               "ap.change": "searched:ap.change"}

EARNINGS_QUALITY_V3 = Rubric(
    dimension="earnings_quality", version=3,
    note=("v3 (DX-99, 2026-09-13) — the non-GAAP reconciliation and accounting-policy "
          "checks are required as SEARCHED, not FOUND: their absence is the finding "
          "levels 4 and 3 describe, and a found-only id made those levels "
          "unreachable for a company with nothing to adjust. ⚠ No criterion text "
          "changed and no score moved. Was: " + EARNINGS_QUALITY_V2.note),
    levels=tuple(
        RubricLevel(lv.score, lv.criterion,
                    tuple(V3_SEARCHED.get(e, e) for e in lv.evidence_required))
        for lv in EARNINGS_QUALITY_V2.levels
    ),
)

# ═══════════════════════════════════════════════════════════════════════════
# ★★ `DX-101` (2026-09-13, at Victor Truong's instruction) — two criteria whose
# WORDING, not the business, decided the first criterion-selected scores.
# ⚠ Only the named criterion strings change. Evidence, scores and every other
# level are byte-identical to `v2` (asserted), for `DX-86`'s reason: a wording
# fix and an evidence change mixed together make a later score move
# unattributable.
# ═══════════════════════════════════════════════════════════════════════════


def _reworded(rubric: Rubric, version: int, changes: dict[int, str], note: str) -> Rubric:
    """`rubric` at `version`, with only `changes[score]`'s criterion replaced."""
    return Rubric(
        dimension=rubric.dimension, version=version, note=note + " Was: " + rubric.note,
        levels=tuple(RubricLevel(lv.score, changes.get(lv.score, lv.criterion),
                                 lv.evidence_required) for lv in rubric.levels),
    )


#: ① `balance_sheet_resilience` — *"absent"* meant both "none left" and "not
#: disclosed". Measured on MU (`run-2026-09-13T181048-mu-j05`): the covenant is
#: disclosed, the headroom is not, and the model scored 1 while writing that the
#: balance sheet *"looks capable of absorbing a bad cycle without an equity
#: raise"*. ★ Resolution: level 1 keeps the ADVERSE meaning only (*exhausted or
#: breached*); undisclosed headroom joins level 3 beside *"disclosed but thin"* —
#: consistent with `E-06`'s own note that *"a company comfortably inside its
#: covenants usually says so"*, so silence is mildly negative, never the second
#: floor. ⚠ Level 4 still requires headroom DISCLOSED.
BS_V3_CHANGES = {
    3: "Maturities are laddered and covered, with covenant headroom disclosed but "
       "thin, or not disclosed.",
    1: "Covenant headroom is exhausted or breached, or the share count rose to fund "
       "operations.",
}
BALANCE_SHEET_RESILIENCE_V3 = _reworded(
    BALANCE_SHEET_RESILIENCE_V2, 3, BS_V3_CHANGES,
    "v3 (DX-101, 2026-09-13) — 'absent' covenant headroom split: exhausted or "
    "breached stays at level 1; NOT DISCLOSED moves to level 3 beside 'disclosed "
    "but thin'. No evidence requirement and no score changed.")

#: ② `capital_allocation` — the top level's price-discipline clause did not say
#: what a window with NO buybacks means. Measured on MU
#: (`run-2026-09-13T181257-mu-j06`): the model scored 4 on a stated ASSUMPTION
#: that abstention satisfies it. ★ Resolution: say so explicitly, in the model's
#: direction. The clause tests buybacks MADE (`J-06` item 2: *"buying steadily
#: regardless of price is a policy"*); reading abstention as a failure would make
#: level 4 unreachable for every company that does not buy back — `DX-99`'s
#: shape, an absence scored as a defect. ⚠ A window with no buybacks gets no
#: CREDIT for discipline either: the level is earned by matching stated
#: priorities, which is unchanged.
CAP_V3_CHANGES = {
    4: "Actions taken across the bundle's periods match the stated priorities, and "
       "no buyback in those periods was made at a price the filings later show was "
       "high (a window with no buybacks meets this condition).",
}
CAPITAL_ALLOCATION_V3 = _reworded(
    CAPITAL_ALLOCATION_V2, 3, CAP_V3_CHANGES,
    "v3 (DX-101, 2026-09-13) — the top level states that a window with no "
    "buybacks meets its price-discipline condition. No evidence requirement and "
    "no score changed.")


#: ★ Every published rubric, every version — ONE list the judgement runner and
#: its tests both read (`DX-72`/`DX-88`: a list copied into two places drifts).
PUBLISHED_RUBRICS = (*B43_RUBRICS, *B43_V2_RUBRICS, EARNINGS_QUALITY_V3,
                     BALANCE_SHEET_RESILIENCE_V3, CAPITAL_ALLOCATION_V3)
