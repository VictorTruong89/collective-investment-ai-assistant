"""`v2` rubrics — `DX-85`/`DX-86`. ✅ **PUBLISHED 2026-09-12, approved by Victor Truong.**

★ **Approval record.** Reviewed as a draft (`b43_v2_draft.py`) and approved on
2026-09-12, with `capital_actions` resolved as option ⓐ (`ca.capex`). Published
ALONGSIDE `v1`, never over it: `RA-52` makes rubrics *versioned*, so any baseline
recorded against `v1` stays interpretable, and `v1` itself is unchanged.

⚠⚠ **What changed from `v1`: only `evidence_required` ids.** Not one `criterion`
string and not one score — asserted byte-for-byte by
`tests/unit/test_rubric_v2.py`. A later score move is therefore attributable to
evidence, never ambiguously to a criteria rewrite.

═══════════════════════════════════════════════════════════════════════════════
WHAT IS WRONG WITH `v1`, MEASURED
═══════════════════════════════════════════════════════════════════════════════

`b43_v1.py`'s `E` dict carries its own warning:

    ⚠ These must match what B4.2's extractors emit, or a level is unavailable
      for a naming reason rather than an evidential one — which would read as
      thin evidence and be a wiring bug.

**It is that wiring bug.** Measured 2026-09-12 against the 15 E-blocks in
`L1-fundamental-analysis-master-prompt.md`, which emit **74** evidence ids:

  * `v1`'s `E` dict declares 13 ids. **3 resolve** — `seg.revenue`,
    `seg.op_income`, `gd.metric`. The other 10 use prefixes
    `con. debt. cap. shr. ngp. acc. cmp.`, and **not one of those prefixes
    exists** anywhere in the extractor vocabulary.
  * ⚠ Of the 13, only **11 are cited by any level**. `guidance` and
    `concentration` are declared and used by nothing — so the load-bearing
    count is **9 broken of 11**. ★ An unused entry is the one place a wrong id
    costs nothing and is therefore never noticed: `con.customer_pct` has been
    wrong since it was written and could not have failed anything.
  * Consequence: with `RA-32` applied, **all four rubrics return ZERO available
    levels**, so no rubric block can be scored at all.

⚠ The 2026-09-12 Stage-A run answered all four anyway (ungated), returning
`moat=1 · earnings=3 · balance=3 · capital=0` for ~$2.6. `capital_allocation=0`
reads *"the bundle does not disclose capital-allocation actions"* — while the MU
10-Q **does** disclose a declared dividend and buybacks. ★ A wiring gap read as
an analytical finding, which is the specific harm this file exists to end.

═══════════════════════════════════════════════════════════════════════════════
★ WHAT CHANGES, AND WHAT DOES NOT
═══════════════════════════════════════════════════════════════════════════════

**Only `evidence_required` ids change. Not one `criterion` string is edited, and
no level's score moves.** ⚠ That is deliberate: correcting a wiring fault and
revising analytical criteria are two different changes, and mixing them would
make it impossible to tell which one moved a score afterwards.

    rubric key            v1 (resolves to nothing)      v2 (real id)      block
    ───────────────────── ───────────────────────────── ───────────────── ─────
    segments              seg.revenue                   seg.revenue   ✅  E-01
    segment_income        seg.op_income                 seg.op_income ✅  E-01
    guidance              gd.metric                     gd.metric     ✅  E-02
    nongaap               ngp.reconciling_item          ng.adjustment     E-04
    concentration         con.customer_pct              cc.customer       E-05
    debt                  debt.maturity_ladder          dm.ladder         E-06
    covenants             debt.covenant                 dm.covenant       E-06
    capital_actions       cap.action                    ca.capex      ⬜  E-07
    accounting_change     acc.policy_change             ap.change         E-09
    share_count           shr.diluted                   sc.diluted        E-10
    sbc                   shr.sbc                       sc.sbc_expense    E-10
    capital_priorities    cap.stated_priority           cp.statement      E-12
    competitor_capacity   cmp.capacity_announcement     cx.capacity       E-13

Each v2 id is quoted from the E-block that emits it:

  ng.adjustment   "each adjusting line, its label and its amount"            E-04
  cc.customer     "any customer disclosed at >=10% of revenue"               E-05
  dm.ladder       "principal due by year as the filing tabulates it"         E-06
  dm.covenant     "each financial covenant: the ratio, the threshold"        E-06
  ca.capex        "capital expenditure, and any split into maintenance vs
                   growth"                                                   E-07
  ap.change       "any change in accounting policy, estimate, or
                   presentation"                                            E-09
  sc.diluted      "weighted-average share counts per period"                 E-10
  sc.sbc_expense  "stock-based compensation expense"                         E-10
  cp.statement    "verbatim quote" (management's stated capital priorities)  E-12
  cx.capacity     "what is being added, in the units the source uses"        E-13

═══════════════════════════════════════════════════════════════════════════════
⬜ THE ONE ENTRY THAT IS A JUDGEMENT, NOT A LOOKUP — `capital_actions`
═══════════════════════════════════════════════════════════════════════════════

⚠⚠ `v1`'s `cap.action` is a **generic** id: one slot meaning *"the capital
allocation actions the company took"*. `E-07` does not have a generic id — it
emits **eight specific ones**: `ca.buyback · ca.authorisation · ca.dividend ·
ca.acquisition · ca.divestiture · ca.capex · ca.rd · ca.issuance`.

So there is no mechanical translation, and the choice changes which companies
can be scored at all:

  ⓐ **`ca.capex` alone** — ✅ CHOSEN (approved 2026-09-12).
     Every operating company deploys capital, so the dimension stays scoreable
     for a company that pays no dividend and runs no buyback. ⚠ Weakest link to
     level 4's criterion, which is explicitly about buyback price discipline.

  ⓑ **several ids per level** (e.g. level 4 cites `ca.buyback` + `ca.dividend`).
     ⚠⚠ `RA-32` requires **ALL** of a level's evidence, so this makes level 4
     UNAVAILABLE for any company that does not do both — which reads as "we
     could not assess" when the truth is "it does not do buybacks". ⛔ That is
     the failure mode `RA-32` is meant to prevent, arriving from the other side.

  ⓒ **add a generic `ca.action` to `E-07`** — ★ the cleanest answer and the
     most expensive: it changes an E-block's item list, so `E-07`'s prompt text
     and its enum both move, and any recording made against the old one retires.

✅ **Resolved 2026-09-12: ⓐ, approved by the fund manager.** ★ Recorded with its
rejected alternatives because this is the entry where the wiring fix touched
analysis, and the reasoning is what a later reader will need.

═══════════════════════════════════════════════════════════════════════════════
⚠ WHAT THIS DOES NOT FIX
═══════════════════════════════════════════════════════════════════════════════

Correcting the ids makes the rubrics *addressable*. It does not make them
*satisfiable*: `E-04`…`E-13` are **not declared in `src/`** (only `E-01`, `E-02`
are), and the bundle contract has **no part kind carrying extraction output**
(`DX-85`ⓒ). ★ So after this lands, the rubric blocks still refuse — but they
refuse for an EVIDENTIAL reason rather than a naming one, which is exactly the
distinction `b43_v1.py`'s warning drew.
"""

from __future__ import annotations

from src.fundamental.scorecard.models import Rubric, RubricLevel

#: ✅ The real extractor vocabulary. Every value is quoted above from the
#: E-block that emits it. `capital_actions` is option ⓐ, approved 2026-09-12.
E2 = {
    "segments": "seg.revenue",                   # E-01  (unchanged)
    "segment_income": "seg.op_income",           # E-01  (unchanged)
    "guidance": "gd.metric",                     # E-02  (unchanged)
    "nongaap": "ng.adjustment",                  # E-04  was ngp.reconciling_item
    "concentration": "cc.customer",              # E-05  was con.customer_pct
    "debt": "dm.ladder",                         # E-06  was debt.maturity_ladder
    "covenants": "dm.covenant",                  # E-06  was debt.covenant
    "capital_actions": "ca.capex",               # E-07  was cap.action  ✅ ⓐ approved
    "accounting_change": "ap.change",            # E-09  was acc.policy_change
    "share_count": "sc.diluted",                 # E-10  was shr.diluted
    "sbc": "sc.sbc_expense",                     # E-10  was shr.sbc
    "capital_priorities": "cp.statement",        # E-12  was cap.stated_priority
    "competitor_capacity": "cx.capacity",        # E-13  was cmp.capacity_announcement
}

_NOTE = ("v2 (DX-85, approved 2026-09-12) — evidence ids corrected to the real extractor "
         "vocabulary. ⚠ No criterion text changed and no score moved; this "
         "revision is a WIRING fix, deliberately kept separate from any "
         "analytical revision so a later score change is attributable.")

MOAT_DURABILITY_V2 = Rubric(
    dimension="moat_durability", version=2,
    note="Dorsey's five sources for the mechanism; Greenwald's share/return "
         "tests for the outcome. ★ Step 1 is where an LLM is weakest — every "
         "company's filings describe switching costs and almost none of them "
         "have any — so the top two levels require the OUTCOME evidence, not "
         "the mechanism. " + _NOTE,
    levels=(
        RubricLevel(4, "A named mechanism is present AND the filings show stable "
                       "share among the leaders AND returns on invested capital "
                       "above the cost of capital across every period in the bundle.",
                    (E2["segments"], E2["segment_income"], E2["competitor_capacity"])),
        RubricLevel(3, "A named mechanism is present and returns persist above the "
                       "cost of capital, but share is not shown or has drifted.",
                    (E2["segments"], E2["segment_income"])),
        RubricLevel(2, "A mechanism is described in the filings and the outcome "
                       "tests are inconclusive on the bundle's periods.",
                    (E2["segments"],)),
        RubricLevel(1, "No mechanism is evidenced and returns do not persist; the "
                       "moat is a story about a moat.",
                    (E2["segments"],)),
        RubricLevel(0, "The filings do not support any assessment of pricing or "
                       "share defence.",
                    (E2["segments"],)),
    ),
)

EARNINGS_QUALITY_V2 = Rubric(
    dimension="earnings_quality", version=2,
    note='Does reported profit become cash the owners could have? The non-GAAP reconciliation is required at every level because its ABSENCE is itself the finding on names that lean on adjusted figures.' + " " + _NOTE,
    levels=(
        RubricLevel(4, 'Reported earnings convert to cash across every period in '
                     'the bundle, with no recurring non-GAAP add-back and no '
                     'accounting-policy change in the window.',
                    (E2["nongaap"], E2["accounting_change"], E2["segment_income"],)),
        RubricLevel(3, 'Earnings convert to cash, with non-GAAP add-backs that are '
                     'disclosed, non-recurring and individually explained.',
                    (E2["nongaap"], E2["accounting_change"],)),
        RubricLevel(2, "Conversion is uneven across the bundle's periods, or "
                     'add-backs recur without a stated reason.',
                    (E2["nongaap"],)),
        RubricLevel(1, 'Reported earnings depend on recurring add-backs, or an '
                     'accounting-policy change moved the figure inside the '
                     'window.',
                    (E2["nongaap"], E2["accounting_change"],)),
        RubricLevel(0, 'The bundle does not permit a cash-conversion assessment.',
                    (E2["nongaap"],)),
    ),
)


BALANCE_SHEET_RESILIENCE_V2 = Rubric(
    dimension="balance_sheet_resilience", version=2,
    note='Does it survive a bad cycle WITHOUT DILUTION? ⚠ Dilution is the failure mode this dimension exists to see, so share count is required at every level — a balance sheet judged without it can look strong right up to the equity raise.' + " " + _NOTE,
    levels=(
        RubricLevel(4, "No maturity inside the bundle's horizon requires "
                     'refinancing, covenants have headroom disclosed, and the '
                     'share count has not risen outside stated compensation.',
                    (E2["debt"], E2["covenants"], E2["share_count"],)),
        RubricLevel(3, 'Maturities are laddered and covered, with covenant '
                     'headroom disclosed but thin.',
                    (E2["debt"], E2["covenants"], E2["share_count"],)),
        RubricLevel(2, 'A maturity falls inside the horizon and refinancing is '
                     'assumed rather than committed.',
                    (E2["debt"], E2["share_count"],)),
        RubricLevel(1, 'Covenant headroom is absent or breached, or the share '
                     'count rose to fund operations.',
                    (E2["debt"], E2["share_count"],)),
        RubricLevel(0, 'The bundle does not disclose the maturity ladder.',
                    (E2["debt"],)),
    ),
)


CAPITAL_ALLOCATION_V2 = Rubric(
    dimension="capital_allocation", version=2,
    note='Does management reinvest or destroy? ★ The top level requires BOTH the stated priorities and the actions taken — the gap between what management said it would do and what it did is the whole assessment, and neither half alone can show it.' + " " + _NOTE,
    levels=(
        RubricLevel(4, "Actions taken across the bundle's periods match the stated "
                     'priorities, and buybacks were not made at prices the '
                     'filings later show were high.',
                    (E2["capital_actions"], E2["capital_priorities"], E2["share_count"],)),
        RubricLevel(3, 'Actions broadly match stated priorities, with one '
                     'departure the filings explain.',
                    (E2["capital_actions"], E2["capital_priorities"],)),
        RubricLevel(2, 'Priorities are stated and the actions taken do not clearly '
                     'follow them.',
                    (E2["capital_actions"], E2["capital_priorities"],)),
        RubricLevel(1, 'Capital was deployed against the stated priorities, or '
                     'issuance funded compensation while buybacks were claimed.',
                    (E2["capital_actions"], E2["share_count"], E2["sbc"],)),
        RubricLevel(0, 'The bundle does not disclose capital-allocation actions.',
                    (E2["capital_actions"],)),
    ),
)


#: All four, in §8.1's order — the `v2` counterpart of `b43_v1.B43_RUBRICS`.
#: ⚠ `B43_RUBRICS` (v1) is deliberately left as it is: it is imported by the
#: inherited confidence/coverage path and characterization-tested in
#: `tests_src/`. Moving that path onto v2 is a separate decision (`DX-87`).
B43_V2_RUBRICS = (MOAT_DURABILITY_V2, EARNINGS_QUALITY_V2,
                  BALANCE_SHEET_RESILIENCE_V2, CAPITAL_ALLOCATION_V2)
