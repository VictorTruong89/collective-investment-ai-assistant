"""`balance_sheet_resilience@v4` — `DX-188`. Published 2026-10-22 at Victor Truong's instruction
("Rubric v4, searched:").

⛔ **The defect `v3` has, measured on SNDK as of 2026-10-20.** Sandisk repaid its term loan in
full on 2026-03-04 and its revolver is undrawn, so `E-06` returned `dm.ladder` `not_found` —
correctly: there is no ladder. Every `v3` level requires `dm.ladder` FOUND, so `J-05` refused
at EVERY level (`RA-32`), including level 0, *"the bundle does not disclose the maturity
ladder"* — a criterion ABOUT absence that a found-only id can never support. `DX-99`'s shape;
its own note named this dimension as the next one.

★ **The fix is `v3`'s for `earnings_quality`:** `dm.ladder` → `searched:dm.ladder` at every
level. ⚠⚠ Only `evidence_required` changes — not one criterion and not one score (asserted),
for `DX-86`'s reason. A debt-free company is read against the existing levels.

⚠ **Not changed, deliberately:** `dm.covenant` stays FOUND at levels 4 and 3. A company with no
debt AND no covenant would still be refused — a separate criteria question (`DX-99`).
"""

from __future__ import annotations

from src.fundamental.scorecard.models import Rubric, RubricLevel
from src.fundamental.scorecard.rubrics.b43_v3 import (
    BALANCE_SHEET_RESILIENCE_V3,
    PUBLISHED_RUBRICS as V3_PUBLISHED,
)

#: `v3` id → `v4` requirement. ★ The ONLY difference between the two rubrics.
V4_SEARCHED = {"dm.ladder": "searched:dm.ladder"}

BALANCE_SHEET_RESILIENCE_V4 = Rubric(
    dimension="balance_sheet_resilience", version=4,
    note=("v4 (DX-188, 2026-10-22) — the maturity ladder is required as SEARCHED, not FOUND: "
          "a company with no debt has no ladder, and a found-only id made every level "
          "unreachable for it. ⚠ No criterion text changed and no score moved. Was: "
          + BALANCE_SHEET_RESILIENCE_V3.note),
    levels=tuple(
        RubricLevel(lv.score, lv.criterion,
                    tuple(V4_SEARCHED.get(e, e) for e in lv.evidence_required))
        for lv in BALANCE_SHEET_RESILIENCE_V3.levels
    ),
)

#: ★ Every published rubric, every version — the ONE list the runners and tests read.
PUBLISHED_RUBRICS = (*V3_PUBLISHED, BALANCE_SHEET_RESILIENCE_V4)
