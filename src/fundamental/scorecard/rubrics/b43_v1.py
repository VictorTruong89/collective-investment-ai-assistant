"""The four published rubrics — §8.1's closed dimension set (RA-52).

⚠ **These are FIRST DRAFTS, and saying so is the point.** RA-34: *a rubric whose
scores do not disperse across the universe (RM-7) is a defect in the rubric, and
it is fixed by rewriting criteria — never by asking the model to "use the full
range".* **No rubric here has been dispersion-checked**, because that needs a
universe of scored names and B4.3 has none. Each is `v1` and each will move.

★ **Every level names its `evidence_required`, including the low ones.** Under
**RA-134** the union is `evidence_coverage`'s denominator, so a level declaring
none would silently shrink it — and it would also be unconditionally available
(RA-32), which is a level nothing can fail to support.

Criteria are grounded in the provenance the master prompt records: Dorsey's five
moat sources and Greenwald's two empirical tests (J-03), cash conversion (J-04),
survival-without-dilution (J-05), and reinvestment-versus-destruction (J-06).
"""

from __future__ import annotations

from src.fundamental.scorecard.models import Rubric, RubricLevel

#: Evidence ids the E-blocks produce (MP-4). ⚠ These must match what B4.2's
#: extractors emit, or a level is unavailable for a naming reason rather than an
#: evidential one — which would read as thin evidence and be a wiring bug.
E = {
    "segments": "seg.revenue",
    "segment_income": "seg.op_income",
    "guidance": "gd.metric",
    "concentration": "con.customer_pct",
    "debt": "debt.maturity_ladder",
    "covenants": "debt.covenant",
    "capital_actions": "cap.action",
    "capital_priorities": "cap.stated_priority",
    "share_count": "shr.diluted",
    "sbc": "shr.sbc",
    "nongaap": "ngp.reconciling_item",
    "accounting_change": "acc.policy_change",
    "competitor_capacity": "cmp.capacity_announcement",
}


MOAT_DURABILITY = Rubric(
    dimension="moat_durability", version=1,
    note="Dorsey's five sources for the mechanism; Greenwald's share/return tests "
         "for the outcome. ★ Step 1 is where an LLM is weakest — every company's "
         "filings describe switching costs and almost none of them have any — so "
         "the top two levels require the OUTCOME evidence, not the mechanism.",
    levels=(
        RubricLevel(4, "A named mechanism is present AND the filings show stable "
                       "share among the leaders AND returns on invested capital "
                       "above the cost of capital across every period in the bundle.",
                    (E["segments"], E["segment_income"], E["competitor_capacity"])),
        RubricLevel(3, "A named mechanism is present and returns persist above the "
                       "cost of capital, but share is not shown or has drifted.",
                    (E["segments"], E["segment_income"])),
        RubricLevel(2, "A mechanism is described in the filings and the outcome "
                       "tests are inconclusive on the bundle's periods.",
                    (E["segments"],)),
        RubricLevel(1, "No mechanism is evidenced and returns do not persist; the "
                       "moat is a story about a moat.",
                    (E["segments"],)),
        RubricLevel(0, "The filings do not support any assessment of pricing or "
                       "share defence.",
                    (E["segments"],)),
    ),
)

EARNINGS_QUALITY = Rubric(
    dimension="earnings_quality", version=1,
    note="Does reported profit become cash the owners could have? The non-GAAP "
         "reconciliation is required at every level because its ABSENCE is itself "
         "the finding on names that lean on adjusted figures.",
    levels=(
        RubricLevel(4, "Reported earnings convert to cash across every period in "
                       "the bundle, with no recurring non-GAAP add-back and no "
                       "accounting-policy change in the window.",
                    (E["nongaap"], E["accounting_change"], E["segment_income"])),
        RubricLevel(3, "Earnings convert to cash, with non-GAAP add-backs that are "
                       "disclosed, non-recurring and individually explained.",
                    (E["nongaap"], E["accounting_change"])),
        RubricLevel(2, "Conversion is uneven across the bundle's periods, or "
                       "add-backs recur without a stated reason.",
                    (E["nongaap"],)),
        RubricLevel(1, "Reported earnings depend on recurring add-backs, or an "
                       "accounting-policy change moved the figure inside the window.",
                    (E["nongaap"], E["accounting_change"])),
        RubricLevel(0, "The bundle does not permit a cash-conversion assessment.",
                    (E["nongaap"],)),
    ),
)

BALANCE_SHEET_RESILIENCE = Rubric(
    dimension="balance_sheet_resilience", version=1,
    note="Does it survive a bad cycle WITHOUT DILUTION? ⚠ Dilution is the failure "
         "mode this dimension exists to see, so share count is required at every "
         "level — a balance sheet judged without it can look strong right up to "
         "the equity raise.",
    levels=(
        RubricLevel(4, "No maturity inside the bundle's horizon requires "
                       "refinancing, covenants have headroom disclosed, and the "
                       "share count has not risen outside stated compensation.",
                    (E["debt"], E["covenants"], E["share_count"])),
        RubricLevel(3, "Maturities are laddered and covered, with covenant headroom "
                       "disclosed but thin.",
                    (E["debt"], E["covenants"], E["share_count"])),
        RubricLevel(2, "A maturity falls inside the horizon and refinancing is "
                       "assumed rather than committed.",
                    (E["debt"], E["share_count"])),
        RubricLevel(1, "Covenant headroom is absent or breached, or the share count "
                       "rose to fund operations.",
                    (E["debt"], E["share_count"])),
        RubricLevel(0, "The bundle does not disclose the maturity ladder.",
                    (E["debt"],)),
    ),
)

CAPITAL_ALLOCATION = Rubric(
    dimension="capital_allocation", version=1,
    note="Does management reinvest or destroy? ★ The top level requires BOTH the "
         "stated priorities and the actions taken — the gap between what "
         "management said it would do and what it did is the whole assessment, "
         "and neither half alone can show it.",
    levels=(
        RubricLevel(4, "Actions taken across the bundle's periods match the stated "
                       "priorities, and buybacks were not made at prices the filings "
                       "later show were high.",
                    (E["capital_actions"], E["capital_priorities"], E["share_count"])),
        RubricLevel(3, "Actions broadly match stated priorities, with one departure "
                       "the filings explain.",
                    (E["capital_actions"], E["capital_priorities"])),
        RubricLevel(2, "Priorities are stated and the actions taken do not clearly "
                       "follow them.",
                    (E["capital_actions"], E["capital_priorities"])),
        RubricLevel(1, "Capital was deployed against the stated priorities, or "
                       "issuance funded compensation while buybacks were claimed.",
                    (E["capital_actions"], E["share_count"], E["sbc"])),
        RubricLevel(0, "The bundle does not disclose capital-allocation actions.",
                    (E["capital_actions"],)),
    ),
)

#: All four, in §8.1's order.
B43_RUBRICS = (MOAT_DURABILITY, EARNINGS_QUALITY, BALANCE_SHEET_RESILIENCE,
               CAPITAL_ALLOCATION)
