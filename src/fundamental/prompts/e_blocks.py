"""The E-block prompt texts, in code (`DX-23`).

⚠⚠ **Why this file exists.** `E-01`'s prompt lived only in
`sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md` §E-01. Nothing
in `src/` could construct it, so `run_extraction` had no block to run and no
extraction could ever be recorded — which is why `F5`'s golden `input_ref` had
nothing to point at.

★ **The text is copied VERBATIM from the design doc.** `RA-13`: the version is
bumped on any content change, and `block()` hashes the text at declaration so a
later in-place edit is caught. ⚠ Editing the text here without bumping the
version is the one thing neither guard can catch (`MP-4`'s note in the registry).

⚠ Nine E-blocks are declared (`E-01` `E-02` `E-04` `E-06` `E-07` `E-09` `E-10`
`E-12` `E-13`). The other six stay in the design doc until something
actually runs them — a registry entry nothing calls is a claim, not a capability.
"""

from __future__ import annotations

from src.fundamental.prompts.registry import PromptBlock, block

#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-01 `v2`.
#:
#: ✏ **`v1` → `v2`, 2026-09-07 (`RA-13`).** ⚠ `v1` left "verbatim" to the tool
#: schema's field description, and a live run returned a **paraphrase** as a
#: `seg.basis_note` value while quoting the document's real sentence. `X-01`
#: refused it, correctly. ★★ `MP-5` puts the SHAPE in the API — but *what counts
#: as a value* is meaning, not shape, and no schema carries meaning. That
#: belongs in the prompt, which is why this is a version bump and not a patch.
#:
#: ⚠⚠ **A bump retires every recording made under the old version.** `F5`'s
#: golden cases grade a recorded call; one recorded under `v1` no longer grades
#: what this repo ships. See `tools/golden_replay.py`.
E01_V2_TEXT = """\
From the filings in the bundle, extract the reporting-segment table for every
period the filings cover.

Items:
  seg.name          the segment name as the company defines it
  seg.revenue       revenue for that segment, that period
  seg.op_income     operating income or loss for that segment, that period
  seg.assets        identifiable assets, if disclosed
  seg.basis_note    any statement that the segmentation changed, was restated,
                    or that a segment was renamed or merged

If the company restated prior-period segments, return BOTH the as-originally-
reported and the as-restated figures, each tagged, and never silently prefer one.

Every value must appear VERBATIM inside the quote you cite for it. For a figure,
quote the line that states it, and give the figure without a currency symbol —
the currency belongs in the unit. For a text item, the value must be words
copied from the quote: never a summary of it, never two sentences joined.
A value that cannot be found in its own quote cannot be checked, and is refused.
"""


#: ⚠⚠ The item ids `E-01` may return, from its own item list above. The tool
#: schema turns these into an ENUM.
#:
#: ★★ Measured 2026-09-07: with `evidence_id` declared as a free string whose
#: *description* said "the id from the block's item list, never invent one",
#: the model returned **all 56 items tagged `E-01`** — the BLOCK id. `MP-5`
#: exactly: *output shape is enforced by the API, not by prose.* A description
#: is prose; an enum is the API.
E01_ITEM_IDS = ("seg.name", "seg.revenue", "seg.op_income", "seg.assets",
                "seg.basis_note")


#: ✅ **`v3` SHIPPED 2026-09-08, on the SECOND attempt.** Both filings were
#: re-recorded under it in the same change: MU 57 items, AMD 38.
#: ★★ Every one of filing 1's ten established values is UNCHANGED under `v3` —
#: the prompt altered how the model CITES, not what the filing SAYS. That is
#: the distinction a golden set exists to police, and it held.
#:
#: ⚠⚠ **The first ship was REVERTED within the hour.**
#: It completed AMD twice (46 items on the slice, 38 on the full filing) — but
#: the very first `v3` run against MU returned **ONE item, `seg.name`/CNBU,
#: with an EMPTY value**, where `v2` returns 50-59. Not a truncation: it used
#: 2,428 of 12,000 tokens and simply stopped.
#:
#: ★★★ The lesson, and it cost $0.44 to learn: **a prompt version must be
#: proven against EVERY filing the golden set grades, not only the filing that
#: motivated it.** `v3` fixed a real defect that MU could not expose (`DX-31`)
#: and introduced one that AMD could not expose. Neither filing alone would
#: have caught both.
#:
#: ✅ Resolved: the 1-item run was a BAD SAMPLE, not a systematic failure. The
#: retry returned 57 items in 9,596 tokens. ⚠ Two runs of the same prompt on the
#: same filing differed by 57x in yield — **one sample is not evidence about a
#: stochastic system**, and the earlier revert was still the right call on the
#: information available.
#: ★ It adds a reachable exit to the restatement clause — `v2` demanded BOTH
#: bases whenever a restatement was mentioned, and AMD's filing states one
#: while containing only the restated figures. The model spent 32,000 output
#: tokens producing nothing (`DX-31`).
E01_V3_TEXT = """\
From the filings in the bundle, extract the reporting-segment table for every
period the filings cover.

Items:
  seg.name          the segment name as the company defines it
  seg.revenue       revenue for that segment, that period
  seg.op_income     operating income or loss for that segment, that period
  seg.assets        identifiable assets, if disclosed
  seg.basis_note    any statement that the segmentation changed, was restated,
                    or that a segment was renamed or merged

If the company restated prior-period segments, return BOTH the as-originally-
reported and the as-restated figures, each tagged, and never silently prefer one.
If the filing presents only ONE basis, return that basis and say which one it is
in a seg.basis_note. Do not search for figures the filing does not contain.

Every value must appear VERBATIM inside the quote you cite for it. For a figure,
quote the line that states it, and give the figure without a currency symbol —
the currency belongs in the unit. For a text item, the value must be words
copied from the quote: never a summary of it, never two sentences joined.
A value that cannot be found in its own quote cannot be checked, and is refused.
"""


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-01 `v4`.
#:
#: ★★★ **`DX-71` — this block was never wrong; the ENVELOPE changed what it
#: meant.** Once `DX-67` composed `S-2` item 3 (*"Do not compute … record a data
#: gap"*) in front of it, the model stopped reporting `period.start` — correctly,
#: since a segment table states only the period END.
#:
#: ⚠⚠ **The split is what identifies the cause.** Measured on the post-envelope
#: re-records: AMD's DISCRETE rows kept `2025-06-29`, while every YTD row and
#: every MU row returned `None`. `S-2` did not suppress the field — it suppressed
#: it exactly where the model would have had to look somewhere ELSE in the
#: document. ★ So the fix is not to weaken `S-2`; it is to say plainly that
#: **looking elsewhere is reading, not deriving.**
#:
#: ⚠ The last sentence is load-bearing: subtracting thirteen weeks stays
#: forbidden. `v4` widens where the model may LOOK, never what it may CALCULATE.
E01_V4_TEXT = E01_V3_TEXT.rstrip("\n") + """

Each figure covers a reporting PERIOD with a start date and an end date. The END
date is normally in the column header ("Thirteen weeks ended May 29, 2025"). The
START date is often stated in a DIFFERENT part of the same filing - the share
repurchase table in Item 2, the cover page, or the comparative balance sheet.
Look there, and read it.

Reading a date from elsewhere in the bundle is EXTRACTION, not computation. S-2's
rule against deriving forbids arithmetic you would perform; it does not forbid
evidence that is already written down somewhere you have not yet looked. But if
no part of the filing states the start date, leave it absent and record the gap -
do NOT obtain it by subtracting thirteen weeks from the end date.
"""


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-02 `v1`.
#:
#: ★★ **The second block to be declared, 2026-09-09.** 14 of 15 `E-blocks` had
#: zero golden cases; `E-01` alone proved the harness works for ONE prompt on
#: two filings. ⚠ That is a weaker claim than it reads — a harness that
#: generalises across FILINGS may still not generalise across BLOCKS.
#:
#: ★ Guidance is also the clearest answer to *"why not just use FMP?"*: FMP
#: serves ANALYST ESTIMATES — third-party forecasts. This block extracts what
#: **the company itself said**, and the prompt refuses the other kind outright.
E02_V1_TEXT = """\
Extract every forward-looking figure the COMPANY ITSELF stated, and only those.

  gd.metric         what is being guided (revenue, gross margin, capex, …)
  gd.value          the figure or range as stated
  gd.period         the period guided
  gd.stated_on      the filing/date it was stated in
  gd.prior_value    the same guidance as previously stated, if the bundle
                    contains an earlier statement of it
  gd.direction      raised | lowered | reaffirmed | initiated | withdrawn
  gd.language_note  verbatim hedging language attached to it

Do not include analyst estimates, consensus figures, or any third-party forecast.
Do not include a figure the company described as an illustration or a scenario.
`withdrawn` guidance is a high-value item — never drop it for being empty.
"""

#: `E-02`'s item ids. ⚠ `gd.direction` carries a CLOSED set in the prompt
#: (raised | lowered | reaffirmed | initiated | withdrawn) — a candidate for a
#: schema enum of its own if this block earns cases.
E02_ITEM_IDS = ("gd.metric", "gd.value", "gd.period", "gd.stated_on",
                "gd.prior_value", "gd.direction", "gd.language_note")


#: Verbatim from the design doc §E-02 `v2`.
#:
#: ✏ **`v1` → `v2`, 2026-09-09 (`RA-13`, `DX-34`) — `gd.direction` REMOVED.**
#: ⚠⚠ It asked the model to compare `gd.value` with `gd.prior_value`, which is
#: a COMPUTATION — and `MP-6` already forbade prompts from computing. It also
#: could not pass `X-01`: the returned `'reaffirmed'` appears nowhere in its
#: cited span, because the model CHOSE it rather than copying it.
#: ★ Direction is now `D-02`'s, derived with an arithmetic trail (`AP-5`).
E02_V2_TEXT = """\
Extract every forward-looking figure the COMPANY ITSELF stated, and only those.

  gd.metric         what is being guided (revenue, gross margin, capex, …)
  gd.value          the figure or range as stated
  gd.period         the period guided
  gd.stated_on      the filing/date it was stated in
  gd.prior_value    the same guidance as previously stated, if the bundle
                    contains an earlier statement of it
  gd.language_note  verbatim hedging language attached to it

Do not include analyst estimates, consensus figures, or any third-party forecast.
Do not include a figure the company described as an illustration or a scenario.
`withdrawn` guidance is a high-value item — never drop it for being empty: return
gd.metric and gd.period with the company's own words about the withdrawal in
gd.language_note.
"""

#: ⚠ `gd.direction` is GONE — six ids, not seven.
E02_V2_ITEM_IDS = ("gd.metric", "gd.value", "gd.period", "gd.stated_on",
                   "gd.prior_value", "gd.language_note")


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-01 `v1`.
#:
#: ★★★ **The FIRST judgement block declared** (`DX-64`, 2026-09-10). `e_blocks.py`
#: has shipped `E-01`/`E-02` only, while `thesis/author.py::STAGE_BLOCKS` named
#: `J-01`…`J-17` — none with text in `src/`. ⚠ So `author_once` could construct
#: no judgement block and **no thesis could ever be recorded**, which is why
#: `F5`'s `thesis` kind has sat empty. ★ `DX-23`'s shape exactly, one domain over.
#:
#: ⚠⚠ **`J-01` was chosen over `J-09` because it is the only kind of block that
#: can run ALONE.** `J-09` opens *"You also have your own Stage-A conclusions,
#: which are FIXED"* — it consumes `J-01`…`J-08` plus D-02's valuation trail, so
#: running it standalone would produce a confident answer over absent inputs.
#: ★ `J-01` is Stage A's first block: *"the first judgement and the one with the
#: widest blast radius"*, reading only the bundle.
#:
#: ★★ It also makes the better golden case. The answer is a **closed enum**, so
#: it is checkable the way an extraction item is — not prose a reader must
#: adjudicate. `D2` still calls it a judgement (`is_judgement` is True for
#: `thesis`), and the case records whose judgement it was.
J01_V1_TEXT = """\
Classify this company into exactly one archetype. The classification governs
which analytical questions the rest of the analysis is allowed to ask, so it is
the first judgement and the one with the widest blast radius.

  cyclical_commodity   Output is substantially fungible; the industry's own
                       capacity cycle, not this company's execution, dominates
                       the earnings swing. Reported earnings at any single point
                       are a poor guide to normal earnings.
  compounder           Demand is stable, returns on capital have persisted above
                       the cost of capital across the periods in the bundle, and
                       reinvestment is modest relative to cash generation.
  secular_growth       Growth dominates every other variable; heavy reinvestment
                       defers cash generation deliberately; the open question is
                       market size and share, not margin.
  regulated_utility    Returns are set by a regulator against a rate base rather
                       than by competition.
  financial            The balance sheet IS the business. Book value, spread,
                       reserves and capital ratios are primary; earnings are not.
  binary_outcome       Value depends on a small number of discrete events
                       (approval, drill result, litigation) rather than on a
                       continuing operating record.
  insufficient_evidence

A company may plausibly fit two. Choose the one whose FAILURE MODE would hurt
the reader more if ignored, name the runner-up, and state in one sentence what
would settle it.
"""

#: `RA-17` — the enumerated options, order-randomised per call so position
#: cannot become an answer. ⚠ `insufficient_evidence` is one of them: `MP-7`,
#: a block with no way to say *"I could not"* will always find something to say.
# ═══════════════════════════════════════════════════════════════════════════
# ★★★ STAGE A, THE REST — `J-02`…`J-08`, declared 2026-09-11 (`DX-64`).
#
# ⚠⚠ **Declared is not callable.** All seven are verbatim from the design doc
# and pinned to it by `test_ra_13_*`, so the TEXT is now under the same drift
# guard `E-01` has had since `DX-23`. But `tools/run_judgement_once.py`'s
# `judgement_tool` returns ONE schema — `classify_archetype`, with `archetype`
# and `runner_up` enums — which fits `J-01` and `J-07` and **nothing else**.
# ★ `DX-81` records that, because a block that is declared but unservable is
#   exactly the state `DX-23` found `E-01` in, one layer up.
#
# ★★ THREE ANSWER SHAPES live in these seven, and the difference is the work:
#      enum      J-07                 (like J-01 — the only shape tooled today)
#      rubric    J-03 · J-04 · J-05 · J-06   → a level from `scorecard/rubrics`
#      prose     J-02                 (5 numbered parts, 400-word cap)
#      mixed     J-08                 (prose + one closed field enum)
# ═══════════════════════════════════════════════════════════════════════════

#: `J-02` · business-model comprehension — verbatim from the doc §J-02 `v1`.
#:
#: ★★ **A PROSE block, and the first one.** `J-01` answers with an enum; this
#: answers with five numbered paragraphs under a 400-word cap. `options=()`
#: is therefore correct and not an omission — see `DX-81`, which records that
#: the judgement TOOL cannot yet serve this shape.
#: ★ Item 5 (*"what you do NOT understand"*) is `MP-7` inside a prompt: a
#: block with no way to say *"I could not"* will always find something to say.
J02_V1_TEXT = """\
Explain how this company converts an input into a dollar of profit, in terms a
reader could use to predict what happens to that dollar when a named condition
changes.

Answer, each grounded per S-3:
  1. What is sold, to whom, and what the buyer is choosing between.
  2. How revenue is recognised, and the gap between a sale and cash.
  3. The cost structure: what is fixed, what is variable, and what changes the
     ratio.
  4. The three variables that most move profit, ranked, each with the bundle
     evidence for the ranking.
  5. ★ What you do NOT understand about this business after reading the bundle.

Item 5 is mandatory and may not be "nothing". Every business has a part that its
own disclosures do not explain; naming it is the most useful sentence you will
write, and an analyst who claims complete understanding of a company from its
filings has stopped reading.

Length cap: 400 words.
"""


#: `J-03` · moat durability — verbatim from the doc §J-03 `v1`.
#:
#: ⚠⚠ **Emits a RUBRIC LEVEL, not a free answer.** The doc heading says
#: *"emits `moat_durability@v2`"*; the registry publishes `moat_durability@v1`
#: (`DX-80`). The version in `EMITS` below is the one the CODE can actually
#: resolve, and the discrepancy is recorded rather than silently reconciled.
#: ★ `RA-32`: a level whose `evidence_required` is absent from the bundle is
#: UNAVAILABLE — which is why the options are the rubric's levels, not 0-4.
J03_V1_TEXT = """\
Assess whether this company can defend its pricing and its share, and for how
long.

STEP 1 — Which mechanism, if any, is present. For each, state present /
absent / insufficient_evidence with its bundle evidence:

  intangible_assets   brands, patents, regulatory licences — something that
                      legally or perceptually prevents substitution
  switching_costs     the customer's cost (money, time, risk, retraining) of
                      leaving, evidenced by contract terms, integration depth,
                      or disclosed retention
  network_effects     each additional user makes the product more valuable to
                      existing users
  cost_advantage      a structurally lower cost per unit — process, scale,
                      location, or a resource rivals cannot obtain
  efficient_scale     a market served adequately by its incumbents where a new
                      entrant's capacity would destroy the returns it entered for

STEP 2 — The two outcome tests, from the evidence, not the story:
  a) Market-share stability across the periods in the bundle. Stable shares
     among the leaders are evidence a barrier exists; churning shares are
     evidence one does not, whatever the mechanism above suggests.
  b) Persistence of returns on invested capital above the cost of capital, using
     the pre-computed series in <computed_metrics>. A moat that has never shown
     up in the returns is a story about a moat.

STEP 3 — Select ONE level from the rubric. A level whose `evidence_required`
items are absent from the bundle is unavailable (RA-32).

STEP 4 — Name the single observation over the next four quarters that would move
you down one level.
"""


#: `J-04` · earnings quality — verbatim from the doc §J-04 `v1`.
#: ★ Six steps, ending in one rubric level plus a falsifier. The four tests
#: (cash · composition · working capital · return decomposition) all read
#: PRE-COMPUTED series: `S-2` forbids the model to derive them itself.
J04_V1_TEXT = """\
Assess whether reported earnings represent cash the owners could have.

STEP 1 — The cash test. Using the pre-computed series:
  a) Cash conversion — operating cash flow against net income, every period in
     the bundle. A persistent gap in one direction is the finding; a single
     year's gap is usually working capital.
  b) The accrual ratio. Earnings whose growth arrives as accruals rather than
     cash have historically been the less persistent kind. State the level, the
     direction of travel, and which accrual line drives it.
  c) Free cash flow after ALL capital expenditure, against net income.

STEP 2 — The composition test, from E-04 and E-07:
  a) What share of the period's earnings came from items that are not the
     operating business — asset sales, reserve releases, one-time gains, fair-
     value marks, tax items?
  b) Which "non-recurring" adjustments have recurred? E-04 returns the periods
     each label appeared in; a label appearing in most of them is a recurring
     cost being presented as an interruption.
  c) Stock-based compensation against revenue, and its trend.

STEP 3 — The working-capital test:
  Days sales outstanding, days inventory, days payable, each across the periods.
  Receivables growing faster than revenue, or inventory growing faster than
  cost of sales, are the two classic ways a good quarter is borrowed from a
  later one. State which, if either, is present.

STEP 4 — The return-decomposition test:
  Decompose the return on equity into margin, asset turnover and leverage, and
  state which of the three moved. ★ An improving ROE driven by leverage is a
  different fact from one driven by margin, and they are indistinguishable in the
  headline number.

STEP 5 — Select ONE rubric level. STEP 6 — Name the observation that would move
you down one level.
"""


#: `J-05` · balance-sheet resilience — verbatim from the doc §J-05 `v1`.
#:
#: ⚠⚠ The doc heading says *"emits `balance_sheet@v1`"*; the registry's
#: dimension is **`balance_sheet_resilience`** (`DX-80`). `EMITS` carries the
#: registry's name — the one `RubricRegistry.get` can resolve.
#: ★ Item 3 is `S-4` made concrete: *undisclosed covenant headroom is a
#: FINDING, not a pass* — absence of evidence stated as such.
J05_V1_TEXT = """\
Assess whether this company survives a bad cycle without diluting its owners.

  1. Leverage, both gross and net, against the periods in the bundle and against
     the peer context supplied.
  2. The maturity ladder (E-06). What must be refinanced, when, and what the
     coupon on it is. A wall inside three years is a different company from the
     same leverage spread over ten.
  3. Covenants (E-06). The tested ratio, the threshold, and the disclosed
     headroom. Undisclosed headroom is a finding (S-4), not a pass.
  4. Liquidity: cash, undrawn revolver, and the revolver's own expiry.
  5. ★ The downside arithmetic, using ONLY pre-computed scenario figures where
     the bundle supplies them: at the worst earnings level visible in the
     bundle's history, does this balance sheet still service its debt? If the
     bundle contains no such period, say so — a company that has never been
     tested is not the same as one that passed.
  6. Off-balance-sheet and contingent items: leases, guarantees, litigation
     accruals (E-11), pension.

Select ONE rubric level. Name the observation that would move you down one.
"""


#: `J-06` · capital allocation — verbatim from the doc §J-06 `v1`.
#: ★★ Item 6 (*"said versus did"*) is the one that needs `E-12`, and it is
#: explicitly told **not to grade the eloquence of the statement** — the
#: failure mode an LLM reaches for when asked to judge management.
J06_V1_TEXT = """\
Assess whether management's deployment of capital has created value for owners.
Judge the record (E-07), against the stated intentions (E-12).

  1. Where the cash went, period by period, as proportions: reinvestment,
     acquisition, buyback, dividend, debt reduction, cash accumulation.
  2. ★ Buyback price discipline. Compare the average repurchase price to the
     price range of the period in which it was bought, from the pre-computed
     series. Buying steadily regardless of price is a policy, not an allocation
     decision, and it is the most common way a good business returns capital
     badly.
  3. Acquisitions: what was paid, what was recognised as goodwill, and — where
     the bundle covers a long enough window — whether the acquired assets were
     later impaired. An impairment is management marking its own homework, and
     it is the only honest acquisition scorecard filings offer.
  4. Reinvestment quality: incremental capital deployed against the change in
     operating profit that followed it, using the pre-computed series. Whether
     there is anywhere left to deploy at that return is the more important half.
  5. Dilution: has the share count fallen, and is buyback spending net of
     issuance actually retiring shares or offsetting compensation? (E-10)
  6. ★ Said versus did. E-12 supplies what management stated it would do. State,
     per commitment: kept / not kept / not yet testable — and do not grade the
     eloquence of the statement.

Select ONE rubric level. Name the observation that would move you down one.
"""


#: `J-07` · cycle position — verbatim from the doc §J-07 `v1`.
#:
#: ★ **Enum-answering, like `J-01`** — so `J07_OPTIONS` is real and the
#: existing judgement tool shape fits it. ⚠ `not_applicable` AND
#: `insufficient_evidence` are BOTH present and mean different things:
#: *this is not a cyclical business* vs *it is and I cannot tell where*.
#: ★★ The block states the cyclical trap explicitly — trailing multiples
#: look cheapest at the peak — and requires the answer to say which side of
#: it the evidence puts you on. `MP-6`: normalised earnings are `D-02`'s
#: arithmetic, and the prompt says so rather than leaving it implied.
J07_V1_TEXT = """\
Where in its industry cycle is this business, and on what evidence?

Select one: trough | early_recovery | mid | late | peak | not_applicable |
insufficient_evidence

Each of these must be addressed, with bundle evidence or an explicit gap:
  a) Realised prices or ASPs against their range across the bundle's history.
  b) Inventory: the company's, and the channel's where disclosed, in days.
  c) Capacity utilisation against its own history.
  d) Order patterns: lead times, backlog, cancellations, contract duration.
  e) Industry-wide capital expenditure — is the industry building or starving?
     (E-13) This is the leading variable, and it is about the industry, not this
     company.
  f) Margin position relative to the bundle's own history.

★ The trap, stated so it is checked rather than assumed: at a cyclical peak,
trailing earnings are at their highest and trailing multiples at their lowest,
so the business looks cheapest exactly when it is most dangerous — and at a
trough the reverse. State explicitly which side of that trap the present
evidence puts you on. If you cannot tell, that is `insufficient_evidence` and it
is a legitimate answer.

You are NOT estimating normalised earnings. That is arithmetic and belongs to
D-02; if D-02 publishes a mid-cycle series it is in <computed_metrics>, and if
it does not, that is a data gap.
"""


#: `J-08` · industry structure and supply — verbatim from the doc §J-08 `v1`.
#:
#: ⚠ **A MIXED shape**: item 5 carries a closed 4-value enum for the supply
#: read, wrapped in prose answers for items 1-4. `J08_SUPPLY_OPTIONS` is
#: declared because `MP-5` says a closed set is DECLARED, never described —
#: but it is a FIELD's enum, not the block's answer, which is why it is not
#: passed as `options=`. ★ `DX-81` records that no tool shape serves this.
J08_V1_TEXT = """\
Assess the industry this company competes in, independent of the company.

  1. Concentration: who are the participants and how is share distributed?
  2. Barriers to entry — the practical question, not the theoretical one: what
     would it cost, and how long would it take, for a credible entrant to reach
     a share that mattered? Answer in the units the bundle supports.
  3. Buyer power and supplier power, evidenced by concentration (E-05) and by
     contract terms where disclosed.
  4. Substitution: what does the customer do instead, including doing nothing?
  5. ★ The supply read. From E-13's announced capacity, and only from it: over
     the next eight quarters, is announced supply growing faster than, in line
     with, or slower than the demand evidence in the bundle? Select one:
       supply_growing_faster | in_line | demand_growing_faster |
       insufficient_evidence
     For each competitor row, one sentence on what that announcement means for
     pricing IF it arrives on the stated schedule. Announced capacity that is
     conditional (E-13 `cx.conditional`) must be treated as conditional.

★ For a commodity business this is the single most important judgement in Stage A
and it is about the industry, not the company. A well-run participant in an
oversupplying industry loses money.
"""

#: `J-07`'s closed set, from its own prose (`MP-5` — declared, never described).
J07_OPTIONS = ("trough", "early_recovery", "mid", "late", "peak",
               "not_applicable", "insufficient_evidence")

#: `J-08` item 5's supply read. ⚠ A FIELD enum, not the block's answer.
J08_SUPPLY_OPTIONS = ("supply_growing_faster", "in_line",
                      "demand_growing_faster", "insufficient_evidence")

#: ⚠⚠ `DX-81` — the ANSWER FIELD an enum-answering block returns, per block.
#:
#: ★★★ **`J-01` must stay `archetype`, and the reason is a signed golden case.**
#: `tests_src/fixtures/golden/thesis.yaml::mu-fy2025q3-j01-archetype` asserts
#: `expected: {archetype: cyclical_commodity}` against a recorded call. Renaming
#: this field to something neutral like `answer` would break a case the fund
#: manager established — so the field name is **per block**, not a convention
#: the tool imposes. ⚠ A "tidier" generalisation here silently invalidates `D2`
#: work that cannot be regenerated.
ENUM_ANSWER = {
    "J-01": ("classify_archetype", "archetype"),
    "J-07": ("select_cycle_position", "cycle_position"),
}

#: `DX-81` — required fields a PROSE block must return beyond its answer.
#:
#: ★★ `MP-5` applied to a rule that was previously only prose: `J-02` says item
#: 5 *"is mandatory and may not be 'nothing'"*. A required schema field enforces
#: that; a sentence asks for it. The measured lesson is `E-01`'s — a free-string
#: `evidence_id` whose description said *"never invent one"* returned all 56
#: items tagged with the BLOCK id.
PROSE_REQUIRED = {
    "J-02": ("what_i_do_not_understand",),
    "J-08": (),
}

#: `DX-81` — closed sets a block declares for a FIELD rather than for its answer.
#: ⚠ Kept separate from `options` on purpose: `RA-17` permutes the block's
#: ANSWER options, and permuting a field's enum would record a permutation that
#: describes nothing. ★ A structural test asserts every value below appears
#: VERBATIM in the block's own prompt text, so the schema cannot drift from what
#: the model is actually asked.
FIELD_ENUMS = {
    "J-08": {"supply_read": J08_SUPPLY_OPTIONS},
}

#: ⚠⚠ `DX-80` — which rubric each Stage-A scoring block emits, as the REGISTRY
#: names it. The design doc's headings say `moat_durability@v2` and
#: `balance_sheet@v1`; neither resolves. ★ These are the code's names, and the
#: mismatch is a recorded finding rather than a silent reconciliation — a
#: structural test asserts every value here resolves in `RubricRegistry`.
#:
#: ✅ **Moved to `@v2` 2026-09-12 (`DX-86`, approved).** `v1`'s evidence ids
#: resolve to no extractor (`DX-85`: 9 broken of 11 load-bearing), so a block
#: emitting `@v1` could never be scored once `RA-32` applied. `v1` stays
#: published for history; nothing new emits it.
#: ★ Side effect on `DX-80`: the doc's `J-03 — emits moat_durability@v2` now
#: RESOLVES. ⚠ `J-04`/`J-06`'s headings still say `@v1` (which also resolves,
#: since v1 stays published, but is no longer what they emit) and `J-05`'s
#: `balance_sheet@v1` still names a dimension that does not exist.
EMITS_RUBRIC = {
    "J-03": "moat_durability@v2",
    # ✏ `DX-99` (2026-09-13) — `@v3`: non-GAAP and policy checks as SEARCHED,
    #   so a company with no non-GAAP measures is scoreable, not refused.
    "J-04": "earnings_quality@v3",
    # ✏ `DX-101` (2026-09-13) — `@v3`: undisclosed covenant headroom is not "absent".
    "J-05": "balance_sheet_resilience@v3",
    # ✏ `DX-101` (2026-09-13) — `@v3`: a window with no buybacks is stated, not assumed.
    "J-06": "capital_allocation@v3",
}


J01_OPTIONS = ("cyclical_commodity", "compounder", "secular_growth",
               "regulated_utility", "financial", "binary_outcome",
               "insufficient_evidence")


def j01_v1() -> PromptBlock:
    """`J-01` — industry archetype, Stage A, **blind** (`RA-14`).

    ⚠ `view="blind"` is enforced at the seam BOTH WAYS (`call.py`): a blind
    prompt handed the full bundle has lost its anchor-stripping, and a
    full-view prompt handed a redacted one is reasoning over less than it
    should. ★ `MP-3`: *"an absent field is a guarantee"* — Stage A cannot see
    price because the bundle it receives has none.
    """
    return block("J-01", "v1", "judgement", J01_V1_TEXT,
                 view="blind", options=J01_OPTIONS)


def _stage_a(name: str, text: str, options: tuple[str, ...] = ()) -> PromptBlock:
    """Stage-A judgement block — `view="blind"` without exception.

    ⚠⚠ Stage A is blind for a reason `MP-3` states physically: *"an absent field
    is a guarantee"*. The redacted bundle carries no price, no multiple and no
    market cap, so a Stage-A judgement **cannot** be anchored on valuation even
    by accident. ★ `call.py` enforces the pairing BOTH ways, so a blind block
    handed a full bundle fails loudly rather than quietly reasoning from an
    anchor it was built to be denied.

    ★ Factored rather than repeated seven times: `view="blind"` is the property
    every one of these shares, and a per-block literal is a per-block chance to
    get it wrong.
    """
    return block(name, "v1", "judgement", text, view="blind", options=options)


def j02_v1() -> PromptBlock:
    """`J-02` — business-model comprehension. ⚠ PROSE; `options` is empty."""
    return _stage_a("J-02", J02_V1_TEXT)


def j03_v1() -> PromptBlock:
    """`J-03` — moat durability. Emits `moat_durability@v1` (`DX-80`)."""
    return _stage_a("J-03", J03_V1_TEXT)


def j04_v1() -> PromptBlock:
    """`J-04` — earnings quality. Emits `earnings_quality@v1`."""
    return _stage_a("J-04", J04_V1_TEXT)


def j05_v1() -> PromptBlock:
    """`J-05` — balance-sheet resilience. Emits `balance_sheet_resilience@v1`."""
    return _stage_a("J-05", J05_V1_TEXT)


def j06_v1() -> PromptBlock:
    """`J-06` — capital allocation. Emits `capital_allocation@v1`."""
    return _stage_a("J-06", J06_V1_TEXT)


def j07_v1() -> PromptBlock:
    """`J-07` — cycle position. ★ ENUM-answering, like `J-01`."""
    return _stage_a("J-07", J07_V1_TEXT, J07_OPTIONS)


def j08_v1() -> PromptBlock:
    """`J-08` — industry structure and supply.

    ⚠ `options` is EMPTY although the block contains a closed set: that enum
    belongs to item 5's supply-read FIELD, not to the block's answer, and
    `RA-17` permutes the block's answer options. ★ Passing a field's enum here
    would order-randomise the wrong thing and record a permutation that
    describes nothing.
    """
    return _stage_a("J-08", J08_V1_TEXT)


def e02_v2() -> PromptBlock:
    """`E-02` `v2` — guidance, without the derived direction label."""
    return block("E-02", "v2", "extraction", E02_V2_TEXT)


def e02_v1() -> PromptBlock:
    """`E-02` — stated guidance and its revision, `v1`."""
    return block("E-02", "v1", "extraction", E02_V1_TEXT)


def e01_v3() -> PromptBlock:
    """`E-01` `v3` — candidate. ⚠ Not shipped until a live run verifies it."""
    return block("E-01", "v3", "extraction", E01_V3_TEXT)


def e01_v4() -> PromptBlock:
    """`E-01` `v4` — the period-start clause (`DX-71`)."""
    return block("E-01", "v4", "extraction", E01_V4_TEXT)


def e01_v2() -> PromptBlock:
    """`E-01` — segment revenue and operating income, `v2`."""
    return block("E-01", "v2", "extraction", E01_V2_TEXT)


# ═══════════════════════════════════════════════════════════════════════════
# ★★ `DX-85`ⓑ — the seven E-blocks whose evidence the `v2` rubric LEVELS cite,
# declared 2026-09-12. ⚠ Text generated from the design doc, never retyped;
# the drift guard pins it. Declaring them does NOT make J-03…J-06 scoreable:
# `DX-85`ⓒ (a bundle part kind for extraction output) still stands between.
# ═══════════════════════════════════════════════════════════════════════════

#: Verbatim from the design doc §E-04 `v1` — rubric cites `ng.adjustment`.
#:
#: ⚠ `DX-89` — `ng.recurrence_note` returns a LIST of periods gathered
#: across several spans; one quote cannot contain it, so `X-01` may refuse the run.
E04_V1_TEXT = """\
Extract the full reconciliation from GAAP to every non-GAAP measure the company
presents.

  ng.measure          the non-GAAP measure's name as presented
  ng.gaap_start       the GAAP figure it reconciles from
  ng.adjustment       each adjusting line, its label and its amount
  ng.recurrence_note  for each adjustment: has an item with this label appeared
                      in the other periods in the bundle? Return the periods it
                      appeared in. Do not judge whether it "should" recur.
  ng.nongaap_end      the resulting non-GAAP figure

★ `ng.recurrence_note` is a lookup across periods the bundle already contains,
not an opinion. Return the list of periods; the judgement about what a recurring
"non-recurring" charge means is a different call.
"""

#: `MP-5` — `E-04`'s item ids, parsed from its own item list.
E04_ITEM_IDS = ("ng.measure", "ng.gaap_start", "ng.adjustment",
                "ng.recurrence_note", "ng.nongaap_end")


def e04_v1() -> PromptBlock:
    """`E-04` `v1` — non-GAAP reconciliation."""
    return block("E-04", "v1", "extraction", E04_V1_TEXT)


#: Verbatim from the design doc §E-06 `v1` — rubric cites `dm.ladder`, `dm.covenant`.
#:
#: ⚠ `DX-92` — `dm.revolver`'s *undrawn* capacity is a subtraction when the
#: filing states only size and drawn amount; `dm.covenant`'s *direction of the
#: test* must be copied wording, not a chosen label.
E06_V1_TEXT = """\
  dm.instrument    each debt instrument: type, principal, coupon, maturity
  dm.ladder        principal due by year as the filing tabulates it
  dm.covenant      each financial covenant: the ratio, the threshold, the
                   direction of the test, and the tested entity
  dm.headroom      the covenant's most recently disclosed actual value, if given
  dm.revolver      undrawn revolver capacity and its expiry
  dm.rating        credit rating and outlook, if the filing states one

A covenant whose current value is not disclosed is `dm.headroom: not_found` —
which is itself the finding, since a company comfortably inside its covenants
usually says so.
"""

#: `MP-5` — `E-06`'s item ids, parsed from its own item list.
E06_ITEM_IDS = ("dm.instrument", "dm.ladder", "dm.covenant", "dm.headroom",
                "dm.revolver", "dm.rating")


def e06_v1() -> PromptBlock:
    """`E-06` `v1` — debt maturity and covenants."""
    return block("E-06", "v1", "extraction", E06_V1_TEXT)


#: Verbatim from the design doc §E-07 `v1` — rubric cites `ca.capex` (`DX-86` ⓐ).
#:
#: ⚠ `DX-90` — `ca.dividend` *"and any change"* is a comparison when the
#: company does not state the change: `gd.direction`'s shape (`DX-34`).
#: ⚠ `DX-92` — `ca.authorisation` *remaining*; `ca.buyback`/`ca.issuance` pack
#: several figures into one id and lean on `qualifier` rows.
E07_V1_TEXT = """\
Every deployment of capital DISCLOSED AS HAVING HAPPENED, per period:

  ca.buyback        shares repurchased, dollars spent, average price paid if given
  ca.authorisation  buyback authorisation size and remaining
  ca.dividend       per-share and total, and any change
  ca.acquisition    target, consideration, form (cash/stock/mixed), goodwill and
                    intangibles recognised
  ca.divestiture    what was sold, proceeds, gain or loss recognised
  ca.capex          capital expenditure, and any split into maintenance vs growth
                    IF the company itself makes that split
  ca.rd             research and development expense
  ca.issuance       equity or debt issued, amount and stated use of proceeds

Never split capex into maintenance and growth yourself. If the company does not
split it, return `not_found` for the split and the total for the whole.
"""

#: `MP-5` — `E-07`'s item ids, parsed from its own item list.
E07_ITEM_IDS = ("ca.buyback", "ca.authorisation", "ca.dividend",
                "ca.acquisition", "ca.divestiture", "ca.capex", "ca.rd",
                "ca.issuance")


def e07_v1() -> PromptBlock:
    """`E-07` `v1` — capital-allocation actions."""
    return block("E-07", "v1", "extraction", E07_V1_TEXT)


#: Verbatim from the design doc §E-09 `v1` — rubric cites `ap.change`.
#:
#: ⚠ `DX-92` — `ap.reserve`'s *direction of the P&L effect* is a label the
#: model would choose unless the filing words it.
E09_V1_TEXT = """\
  ap.change        any change in accounting policy, estimate, or presentation,
                   with the company's stated reason and quantified effect
  ap.useful_life   changes to depreciation or amortisation lives
  ap.reserve       changes to allowance, warranty, or return reserves, and the
                   direction of the P&L effect
  ap.capitalisation any change in what is capitalised vs expensed
  ap.auditor       auditor change, disagreement, or a modified opinion
  ap.icfr          any material weakness or significant deficiency disclosed
  ap.late          any late-filing notification (NT 10-K / NT 10-Q)
"""

#: `MP-5` — `E-09`'s item ids, parsed from its own item list.
E09_ITEM_IDS = ("ap.change", "ap.useful_life", "ap.reserve",
                "ap.capitalisation", "ap.auditor", "ap.icfr", "ap.late")


def e09_v1() -> PromptBlock:
    """`E-09` `v1` — accounting-policy and estimate changes."""
    return block("E-09", "v1", "extraction", E09_V1_TEXT)


#: Verbatim from the design doc §E-09 `v2` — ✏ `DX-96`, Victor's decision 2026-09-13.
#:
#: ⚠⚠ `v1` truncated on MU three times (20,000 out; the third instrumented at
#: ZERO tool-call characters — thinking). `GW-9c` forbids thinking off. ★ `v2`
#: adds scope, a rule on unadopted standards and a stated empty answer (`MP-7`);
#: the item list — and so the enum — is unchanged.
E09_V2_TEXT = """\
From the filings in the bundle, extract changes the COMPANY ITSELF disclosed
as having been made in the periods the filings cover, and only those.

  ap.change        any change in accounting policy, estimate, or presentation,
                   with the company's stated reason and quantified effect
  ap.useful_life   changes to depreciation or amortisation lives
  ap.reserve       changes to allowance, warranty, or return reserves, and the
                   direction of the P&L effect
  ap.capitalisation any change in what is capitalised vs expensed
  ap.auditor       auditor change, disagreement, or a modified opinion
  ap.icfr          any material weakness or significant deficiency disclosed
  ap.late          any late-filing notification (NT 10-K / NT 10-Q)

A standard issued but not yet adopted is not a change — do not report it.
A routine estimate the company describes without saying it changed is not a
change. If the filings disclose no change for an item, return that item ONCE as
`not_found`, quoting the passage you checked (for example the note on recently
issued accounting standards). Most quarterly filings disclose few or none; an
empty answer is a correct answer.
"""


def e09_v2() -> PromptBlock:
    """`E-09` `v2` — scoped, with a stated empty answer (`DX-96`)."""
    return block("E-09", "v2", "extraction", E09_V2_TEXT)


#: Verbatim from the design doc §E-10 `v1` — rubric cites `sc.diluted`, `sc.sbc_expense`.
#:
#: ⚠⚠ `DX-93` — the prompt names TWO ids on one line (`sc.basic / sc.diluted`).
#: A first-token parse yields `sc.basic` alone and silently drops `sc.diluted`,
#: which the rubric cites. ★ `sc.sbc_revenue_note` is NOT a computation: it asks
#: for the revenue figure and says *"do NOT compute the ratio"*.
E10_V1_TEXT = """\
  sc.basic / sc.diluted     weighted-average share counts per period
  sc.end_of_period          shares outstanding at period end
  sc.sbc_expense            stock-based compensation expense
  sc.sbc_revenue_note       revenue for the same period (for the reader's ratio —
                            do NOT compute the ratio)
  sc.unvested               unvested awards outstanding, if disclosed
  sc.antidilutive           securities excluded as anti-dilutive
"""

#: `MP-5` — `E-10`'s item ids, parsed from its own item list.
E10_ITEM_IDS = ("sc.basic", "sc.diluted", "sc.end_of_period",
                "sc.sbc_expense", "sc.sbc_revenue_note", "sc.unvested",
                "sc.antidilutive")


def e10_v1() -> PromptBlock:
    """`E-10` `v1` — share count and dilution."""
    return block("E-10", "v1", "extraction", E10_V1_TEXT)


#: Verbatim from the design doc §E-12 `v1` — rubric cites `cp.statement`.
#:
#: ★ Pre-flight clean: the *ratio* in `cp.commitment` is one management
#: stated. `cp.period` has `gd.stated_on`'s shape, which passes `X-01` by quoting
#: the dated line.
E12_V1_TEXT = """\
From MD&A, the shareholder letter, and any prepared remarks in the bundle,
extract what management SAID about how it intends to allocate capital.

  cp.statement    verbatim quote
  cp.period       when it was said
  cp.commitment   the specific commitment, if any (a figure, a ratio, a date)
  cp.condition    any condition attached to it

Return statements only. Whether they were kept is J-06's question, and answering
it here would contaminate an extraction with a judgement (RA-5).
"""

#: `MP-5` — `E-12`'s item ids, parsed from its own item list.
E12_ITEM_IDS = ("cp.statement", "cp.period", "cp.commitment", "cp.condition")


def e12_v1() -> PromptBlock:
    """`E-12` `v1` — management's stated capital priorities."""
    return block("E-12", "v1", "extraction", E12_V1_TEXT)


#: Verbatim from the design doc §E-13 `v1` — rubric cites `cx.capacity`.
#:
#: ⛔ `DX-91` — needs NON-FILING evidence: a 10-Q holds no rival's
#: announcement, so expect `not_found`. ⛔ `cx.status` is a closed label the
#: model CHOOSES and `cx.source` is a pointer, not quotable text — both fail
#: `X-01` once a bundle has real industry material. Declared `v1` as written
#: (Victor, 2026-09-12).
E13_V1_TEXT = """\
From the industry material in the bundle:

  cx.competitor    the company announcing
  cx.capacity      what is being added, in the units the source uses
  cx.timing        stated online date
  cx.status        announced | under construction | commissioning | operating
  cx.conditional   any stated condition ("subject to demand", "subject to
                   government approval") — verbatim
  cx.source        the bundle item this came from

An announcement is not capacity. Return the announcement and its status; whether
supply actually arrives is J-08's question.
"""

#: `MP-5` — `E-13`'s item ids, parsed from its own item list.
E13_ITEM_IDS = ("cx.competitor", "cx.capacity", "cx.timing", "cx.status",
                "cx.conditional", "cx.source")


def e13_v1() -> PromptBlock:
    """`E-13` `v1` — competitor capacity announcements."""
    return block("E-13", "v1", "extraction", E13_V1_TEXT)


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-15 `v1`. ✏ Declared 2026-10-04
#: (Victor: the sector ingest moves onto it). Runs over the sector file's source documents
#: (`run_extraction_once.py --block E-15 --sector FILE`); its verified rows are appended to a
#: `sector.v2` file by `tools/ingest_sector_file.py --rows-from RUN_ID` (`sector/rows.py`).
#: ⚠ `CHEAP_E_BLOCKS` names it cheap tier (`INV-8`); the dev runner sends it on the deep tier.
E15_V1_TEXT = """\
TASK TYPE: EXTRACTION into a shared file.

You are adding rows to an industry evidence file that EVERY thesis in this
industry will read. Nothing you write here is a conclusion.

For each item in the source list, extract every row it supports:

  capacity     competitor · what is being added · units as the source states
               them · stated online date · status (announced | under
               construction | commissioning | operating) · any condition
               attached, verbatim
  pricing      a disclosed price, ASP or contract term, with its period
  inventory    a disclosed inventory or channel figure, with its units
  demand       a disclosed order, backlog or customer-commitment figure
  policy       an export control, tariff or regulatory action, with its date

Every row carries: source item id · the date the item was published · a
verbatim quote.

★ Rows are APPEND-ONLY. If an item updates something already in the file — a
capacity that moved from `announced` to `operating` — emit a NEW row with the
new status and the new date. Never revise the old row. The transition history
is the finding, and an announcement that quietly never became capacity is
invisible once the row is overwritten.

⚠ You process EVERY item in the source list. If an item supports no rows, say
so with a one-line reason. Skipping an item silently is how a file that
contains no opinion acquires one — through what got left out.

You may not add a field. If something does not fit the shape above, report it
as an unfitted item and stop; the schema is versioned and a new column is an
analytical change, not a convenience.
"""

#: `MP-5` — `E-15`'s ids are its five ROW KINDS, in its own order.
E15_ITEM_IDS = ("capacity", "pricing", "inventory", "demand", "policy")

#: `E-15`'s capacity status set — its own words (`DX-122`'s rule: a label from a declared set).
E15_CAPACITY_STATUSES = ("announced", "under construction", "commissioning", "operating")


def e15_v1() -> PromptBlock:
    """`E-15` `v1` — sector-file ingest (append-only rows)."""
    return block("E-15", "v1", "extraction", E15_V1_TEXT)


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-03 `v1`. ✏ Declared 2026-10-04
#: (`L3` §2.1p row 6): runs on `--document-set mu-10k-risk-factors` (this 10-K's Item 1A against the prior one's).
E03_V1_TEXT = """\
Compare the risk-factor section of the most recent annual filing against the
prior one.

  rf.added      risk factors present now and absent before — full text
  rf.removed    present before and absent now — full text
  rf.reworded   present in both with materially changed wording; return BOTH
                versions and mark the specific clause that changed
  rf.reordered  a risk that moved materially in ordering, with both positions

Boilerplate churn is not a change. A risk that gained a specific number, a named
counterparty, a named jurisdiction, or a shift from "may" to "has" IS a change,
and is the reason this extraction exists.
"""

#: `MP-5` — `E-03`'s item ids, parsed from its own item list.
E03_ITEM_IDS = ("rf.added", "rf.removed", "rf.reworded", "rf.reordered")


def e03_v1() -> PromptBlock:
    """`E-03` `v1` — risk-factor delta."""
    return block("E-03", "v1", "extraction", E03_V1_TEXT)


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-08 `v1`. ✏ Declared 2026-10-04
#: (`L3` §2.1p row 6): runs on `--document-set mu-form4-2025q3` (the Form 4s; `in.type`/`in.plan_status` are declared classifications, `DX-122`).
E08_V1_TEXT = """\
For each insider transaction in the bundle's Form 4 material:

  in.person        name and stated relationship
  in.date          transaction date
  in.type          purchase | sale | option exercise | gift | award | other
  in.shares        share count
  in.price         price, where stated
  in.plan_status   ★ 10b5-1 | not_10b5-1 | not_stated — from the form's own
                   checkbox, never inferred from context
  in.plan_date     the plan adoption date, where the form states one
  in.holdings_after shares beneficially owned following the transaction

★ `in.plan_status` is the whole point of this extraction. A scheduled sale under
a plan adopted a year earlier and a discretionary at-market sale look identical
in a headline and mean different things. If the form does not state it, the
answer is `not_stated` — never "probably a plan".
"""

#: `MP-5` — `E-08`'s item ids, parsed from its own item list.
E08_ITEM_IDS = ("in.person", "in.date", "in.type", "in.shares", "in.price", "in.plan_status",
                "in.plan_date", "in.holdings_after")


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-08 `v2`. ★ v1 with ONE line
#: changed: `in.type` is the form's code; the label is mapped (`filings/form4.py`, `DX-148` ⓑ).
E08_V2_TEXT = """\
For each insider transaction in the bundle's Form 4 material:

  in.person        name and stated relationship
  in.date          transaction date
  in.type          the transaction code exactly as the form states it (S, P,
                   M, A, G, F, ...) — the label is mapped from it, never
                   chosen here
  in.shares        share count
  in.price         price, where stated
  in.plan_status   ★ 10b5-1 | not_10b5-1 | not_stated — from the form's own
                   checkbox, never inferred from context
  in.plan_date     the plan adoption date, where the form states one
  in.holdings_after shares beneficially owned following the transaction

★ `in.plan_status` is the whole point of this extraction. A scheduled sale under
a plan adopted a year earlier and a discretionary at-market sale look identical
in a headline and mean different things. If the form does not state it, the
answer is `not_stated` — never "probably a plan".
"""


def e08_v2() -> PromptBlock:
    """`E-08` `v2` — `in.type` as the Form 4 code (`DX-148`)."""
    return block("E-08", "v2", "extraction", E08_V2_TEXT)


def e08_v1() -> PromptBlock:
    """`E-08` `v1` — insider transactions and 10b5-1 status."""
    return block("E-08", "v1", "extraction", E08_V1_TEXT)

#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-05 `v1`. ✏ Declared 2026-10-04
#: (`L3` §2.1p row 6): runs on the filing bundle (`tools/run_extraction_once.py --block E-05`).
E05_V1_TEXT = """\
  cc.customer      any customer disclosed at ≥10% of revenue: identifier as
                   given (often "Customer A") and the percentage, per period
  cc.supplier      any supplier, sole-source or single-source dependency named
  cc.geography     revenue by geography as disclosed
  cc.channel       distributor/channel concentration if disclosed

Absence of disclosure is `not_found`, and it is meaningful: it means either no
customer crossed the threshold or the company did not disclose. Say which the
document supports; do not choose between them.
"""

#: `MP-5` — `E-05`'s item ids, parsed from its own item list.
E05_ITEM_IDS = ("cc.customer", "cc.supplier", "cc.geography", "cc.channel")


def e05_v1() -> PromptBlock:
    """`E-05` `v1` — concentration."""
    return block("E-05", "v1", "extraction", E05_V1_TEXT)


#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-11 `v1`. ✏ Declared 2026-10-04
#: (`L3` §2.1p row 6): runs on the filing bundle (`tools/run_extraction_once.py --block E-11`).
E11_V1_TEXT = """\
  lg.matter       each matter: counterparty, claim, jurisdiction, stage
  lg.amount       damages sought or accrued, where stated
  lg.accrual      whether a loss is accrued, and the amount
  lg.language     verbatim probability language ("reasonably possible",
                  "probable", "cannot be estimated")

★ The verbatim language IS the finding. Those phrases are accounting terms of
art with defined thresholds, and paraphrasing one destroys the information.
"""

#: `MP-5` — `E-11`'s item ids, parsed from its own item list.
E11_ITEM_IDS = ("lg.matter", "lg.amount", "lg.accrual", "lg.language")


def e11_v1() -> PromptBlock:
    """`E-11` `v1` — litigation and regulatory."""
    return block("E-11", "v1", "extraction", E11_V1_TEXT)


# ═══════════════════════════════════════════════════════════════════════════
# ★★ `F10` `D5` (2026-09-13) — the normalised-earnings judgement, and `J-07`'s
# sentence that contradicted it. Text generated from the design doc.
# ═══════════════════════════════════════════════════════════════════════════

#: Verbatim from the design doc §J-07 `v2`. ⚠ A CANDIDATE, not shipped: `BLOCKS`
#: still sends `v1`, because `J-07`'s golden case grades a `v1` recording and
#: shipping `v2` retires it — a live re-record (money) comes first.
J07_V2_TEXT = """\
Where in its industry cycle is this business, and on what evidence?

Select one: trough | early_recovery | mid | late | peak | not_applicable |
insufficient_evidence

Each of these must be addressed, with bundle evidence or an explicit gap:
  a) Realised prices or ASPs against their range across the bundle's history.
  b) Inventory: the company's, and the channel's where disclosed, in days.
  c) Capacity utilisation against its own history.
  d) Order patterns: lead times, backlog, cancellations, contract duration.
  e) Industry-wide capital expenditure — is the industry building or starving?
     (E-13) This is the leading variable, and it is about the industry, not this
     company.
  f) Margin position relative to the bundle's own history.

★ The trap, stated so it is checked rather than assumed: at a cyclical peak,
trailing earnings are at their highest and trailing multiples at their lowest,
so the business looks cheapest exactly when it is most dangerous — and at a
trough the reverse. State explicitly which side of that trap the present
evidence puts you on. If you cannot tell, that is `insufficient_evidence` and it
is a legitimate answer.

You are NOT choosing normalised earnings here. Which level of earnings a
valuation should capitalise is J-20's judgement, made separately; D-02 does
the arithmetic on J-20's choice. Do not name a normalised figure in this answer.
"""


def j07_v2() -> PromptBlock:
    """`J-07` `v2` — candidate: J-20 now owns the normalised-earnings choice."""
    return block("J-07", "v2", "judgement", J07_V2_TEXT, view="blind", options=J07_OPTIONS)


#: Verbatim from the design doc §J-20 `v1`.
#:
#: ★★ **The block CHOOSES; code CALCULATES** (`VS-4`, `F10` `D5`). It returns a
#: method from `J20_METHODS` and a window; `src/fundamental/valuation/normalise.py`
#: turns that into a `CashFlowBasis(origin="judgement")`. ⚠ Blind (`MP-3`): a
#: normaliser that can see the price can pick the window that justifies it.
J20_V1_TEXT = """\
Choose the level of free cash flow a valuation of this business should
capitalise, and defend the choice. You do not compute it: you choose a METHOD
and a WINDOW, and code applies them to the figures in the annual history part
of the bundle.

That part gives, per fiscal year, free cash flow to the firm and its margin on
revenue, already computed. Do not add, average, rescale or restate them.

Select one method:
  reported_ttm              the latest trailing twelve months, unadjusted
  cycle_average_fcff        the average free cash flow over the window
  cycle_average_fcff_margin the average free-cash-flow margin over the window,
                            applied to trailing revenue
  insufficient_evidence     the bundle does not let you choose

For cycle_average_fcff and cycle_average_fcff_margin, name the WINDOW as the
first and last fiscal year, both present in the annual history, spanning at
least three fiscal years. A cycle window should contain a trough and a peak you
can point to; name the trough year and the peak year.

List any one-off item you would exclude, each with its evidence_id and a
verbatim quote. It is recorded with your choice; do not quantify it.

State in one sentence the observation that would make you choose a different
method or window.

For a cyclical business the level you choose largely IS the valuation, and you
are choosing it before you have seen any price.
"""

#: ★ `MP-5` — the closed method set, DECLARED (the schema enum), never described.
J20_METHODS = ("reported_ttm", "cycle_average_fcff", "cycle_average_fcff_margin",
               "insufficient_evidence")


def j20_v1() -> PromptBlock:
    """`J-20` — normalised earnings. ★ Stage-A view (blind); answers a METHOD."""
    return _stage_a("J-20", J20_V1_TEXT)



# ═══════════════════════════════════════════════════════════════════════════
# ★★ STAGES B–D — `J-09`…`J-17`, declared 2026-09-14 (L3 §2.1g steps 4–5).
#
# ✏ `DX-109` ⓐ (Victor): declared VERBATIM. Where a block names an input the build
#   cannot supply (J-09's consensus view, implied margin and duration, multiples),
#   the BUNDLE names the absence (`assemble.declared_absences`) — the text is not
#   rewritten to fit the build.
# ★ `view="full"` for every one: Stage B is where the price is revealed (`MP-3`),
#   and the Stage-A output reaches them as a frozen `stage_output` part (`RA-108`).
# ═══════════════════════════════════════════════════════════════════════════
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-09 `v1`.
J09_V1_TEXT = """\
You now have the price, the market capitalisation, the multiples, D-02's fair
value with its sensitivity band and its arithmetic trail, and the consensus view.
You also have your own Stage-A conclusions, which are FIXED. You may not revise
them here; if the valuation makes you want to, say so explicitly as a finding.

  1. ★ What does the current price require to be true? D-02 supplies the
     reverse-engineered figures — the growth, margin and duration implied by the
     present price. Read them out and state, in one sentence each, what the
     world looks like if each holds.
  2. Set those requirements against your Stage-A view. For each, select:
       required_less_than_evidenced | roughly_consistent |
       required_more_than_evidenced | insufficient_evidence
  3. Where the gap is widest, is it explained by something you found in Stage A,
     or is it unexplained? An unexplained gap is not an opportunity; it is a
     question you have not answered yet, and it belongs in the data gaps.
  4. ★ The differential view. State the consensus position in one sentence, then
     state where and why you differ, or state plainly that you do not differ. If
     you do not differ, say so — "I hold the consensus view with the consensus
     confidence" is a legitimate and useful output, and pretending to a
     contrarian angle is how an analyst manufactures one.
  5. Which method in D-02's trail does the most work in the fair value, and how
     sensitive is the conclusion to it? D-02 supplies the sensitivity band; state
     what the band means for this decision in one sentence.

You do not produce a fair value, a target, a stop, or a price. Those are D-02's
and D-06's outputs. You are stating whether the story and the numbers describe
the same company.

Length cap: 450 words.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-10 `v1`.
J10_V1_TEXT = """\
For each forward-looking claim implied by the analysis so far — including the
claims the price requires (J-09) — place it against a reference class.

  1. Name the reference class: the set of companies or situations this one
     resembles, in the terms the bundle supports.
  2. State the base rate the bundle gives you for that class, or state that the
     bundle does not contain one. ★ Do NOT supply a base rate from memory — an
     invented base rate is worse than none, because it wears the clothing of
     evidence.
  3. State whether the claim asks this company to be typical of the class or
     exceptional within it.
  4. Where exceptional: what specifically, in the Stage-A evidence, justifies the
     exception? "Strong management" is not a justification; a mechanism is.

★ Most forecasts are built from the inside — from this company's story. This call
asks the other question: of the companies that have looked like this, how many
went on to do what this analysis assumes?

Length cap: 300 words.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-11 `v1`.
J11_V1_TEXT = """\
You are a short-side analyst. Your job is to establish that this is a bad
investment at this price, and you are paid on whether that turns out to be true —
not on whether it is persuasive.

You have the same bundle. You have NOT seen any bull case and must not construct
one to argue against.

  1. The single strongest reason this business is worse than its accounts
     suggest. One reason, the strongest, with its evidence.
  2. The three most load-bearing assumptions the current price requires (J-09
     supplies what the price requires), and for each: what breaks it, and what
     the observable early symptom of the break would be.
  3. What the accounts would look like two years from now if the bear case is
     correct — the specific lines, with direction and rough magnitude in the
     terms the bundle supports.
  4. ★ The falsification condition for YOUR OWN case: what observation over the
     next four quarters would establish the bear case is wrong? A bear case that
     nothing could disprove is a mood.
  5. What you would need that the bundle does not contain, and what you would do
     with it (S-4).

Do not hedge, and do not write "of course, the bull case is…". You are not
required to be balanced here; the balance is structural — this is one of several
calls and the reader sees them side by side.

Length cap: 500 words.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-12 `v1`.
J12_V1_TEXT = """\
It is three years from today. This investment lost roughly half its value. The
loss is a fact; your task is to explain how it happened.

Do not hedge, do not assign probabilities, and do not write "if". Write the
history.

  1. The four most plausible causal paths, each as a short narrative with dates
     and the order events occurred in.
  2. For each: the earliest observable symptom, and how many quarters it
     preceded the damage.
  3. ★ Which path, if any, was ALREADY visible in the present bundle and
     dismissed? Name where in the evidence it was visible.
  4. Rank the four by how early the symptom appears — not by likelihood. The
     reader can only act on paths that announce themselves in time.

Length cap: 500 words.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-13 `v1`.
J13_V1_TEXT = """\
You are a sceptical forensic analyst. You are NOT trying to establish that
<METRIC> is good. You are enumerating every mechanism by which <METRIC> could
look better than the underlying business, and stating what evidence would settle
each one.

For each mechanism below: present | absent | insufficient_evidence, with its
bundle evidence and — for anything not `absent` — the specific item that would
settle it.

  1. Leverage or capital-structure effects flattering the ratio.
  2. A shrinking denominator: buybacks, write-downs, impairments, or
     distributions reducing the base rather than the numerator improving.
  3. Non-recurring gains inside the numerator (E-04, E-07).
  4. Asset sales or revaluations booked through earnings.
  5. Reserve or provision releases (E-09).
  6. Cash conversion: does the metric's improvement appear in operating cash
     flow, and if not, where did it go?
  7. Receivables: growing faster than revenue?
  8. Inventory: growing faster than cost of sales?
  9. Accounting-policy, estimate or presentation changes (E-09).
 10. Capitalisation of costs that were previously expensed (E-09).
 11. Cyclical position: is the metric near a cycle extreme rather than a
     structural level? (J-07)
 12. Definitional: is the company's stated definition of <METRIC> the standard
     one? Quote its definition.

Then, in one sentence: what fraction of the metric's level do the mechanisms you
found `present` plausibly account for — stated as a range, with the mechanisms
named. If nothing is present, say so plainly; a clean answer here is a real
finding and you must not manufacture a concern to appear rigorous.

★ Do not speculate into fact. A mechanism you cannot evidence is
`insufficient_evidence` with the settling item named — never "possible" or
"cannot be ruled out", which are true of everything.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-14 `v1`.
J14_V1_TEXT = """\
You are given the analysis produced so far. Re-read the bundle looking ONLY for
material that contradicts it. You are not weighing, not balancing, and not
concluding.

  1. Every item in the bundle inconsistent with a stated claim: the item, the
     claim, and the nature of the conflict.
  2. Every item that was available and is not cited anywhere in the analysis,
     where its content bears on a stated claim. ★ Silent omission is the
     footprint of confirmation bias, and it is invisible in the output that
     contains it.
  3. Anywhere the analysis cites part of a passage while the rest of that same
     passage qualifies or contradicts it. Quote both parts.
  4. Anywhere a claim rests on a single item that no other item corroborates.

Return findings only. If there are none, say so — but check item 2 twice before
you do, because it is the one that is hardest to see from inside the analysis
that omitted it.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-15 `v1`.
J15_V1_TEXT = """\
Before any verdict exists, state what would prove the emerging thesis wrong.

Write two to four conditions. Each must be ALL of:

  observable   from data this system already receives — a filing line item, a
               computed metric, a disclosed figure. Not "sentiment worsens".
  dated        with a deadline or an evaluation window. Not "eventually".
  checkable    without a further judgement call. ★ The test: could a script
               decide it? "Competition intensifies" fails. "Gross margin below
               55% in two consecutive quarters" passes.
  material     if it fired, the thesis would be wrong — not merely dented. State
               in one line what it would mean.

For each, name the specific metric or field the check reads, choosing from the
supplied list of available observables. A falsifier naming a field this system
does not receive is not checkable, however precise it sounds.

★ At least one condition must be about the BUSINESS rather than the price. A
falsifier set that consists only of price levels is a stop-loss wearing a
thesis's clothing, and it will fire on volatility rather than on being wrong.

You may not write "the thesis is invalidated if the investment case no longer
holds" or any variant. That is a tautology and it fails the run.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-15 `v2`. ★ v1 plus ONE
#: paragraph: write each condition's TEST in `falsifier_check`'s grammar (2026-10-01,
#: `L3` §2.1p item 3), so `RM-13` decides every thesis without a hand translation.
J15_V2_TEXT = """\
Before any verdict exists, state what would prove the emerging thesis wrong.

Write two to four conditions. Each must be ALL of:

  observable   from data this system already receives — a filing line item, a
               computed metric, a disclosed figure. Not "sentiment worsens".
  dated        with a deadline or an evaluation window. Not "eventually".
  checkable    without a further judgement call. ★ The test: could a script
               decide it? "Competition intensifies" fails. "Gross margin below
               55% in two consecutive quarters" passes.
  material     if it fired, the thesis would be wrong — not merely dented. State
               in one line what it would mean.

For each, name the specific metric or field the check reads, choosing from the
supplied list of available observables. A falsifier naming a field this system
does not receive is not checkable, however precise it sounds.

★ At least one condition must be about the BUSINESS rather than the price. A
falsifier set that consists only of price levels is a stop-loss wearing a
thesis's clothing, and it will fire on volatility rather than on being wrong.

You may not write "the thesis is invalidated if the investment case no longer
holds" or any variant. That is a tautology and it fails the run.

For each condition, also write its TEST: the same condition in the grammar the
answer schema declares. A test is a window of reported periods and one or more
clauses, each a comparison of the listed observables against a threshold in
the field's own units. The test must decide exactly the condition you wrote,
no more and no less. If the condition cannot be expressed in that grammar,
rewrite the condition until it can: a condition only a reader can decide is
not checkable, and it fails the run.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-15 `v3`. ★ v2 plus TWO
#: sentences: the test window must reach the deadline (`DX-144` ⓐ), and a run of quarters
#: is mode `consecutive` (`DX-147` ⓐ). Victor, 2026-10-04.
J15_V3_TEXT = """\
Before any verdict exists, state what would prove the emerging thesis wrong.

Write two to four conditions. Each must be ALL of:

  observable   from data this system already receives — a filing line item, a
               computed metric, a disclosed figure. Not "sentiment worsens".
  dated        with a deadline or an evaluation window. Not "eventually".
  checkable    without a further judgement call. ★ The test: could a script
               decide it? "Competition intensifies" fails. "Gross margin below
               55% in two consecutive quarters" passes.
  material     if it fired, the thesis would be wrong — not merely dented. State
               in one line what it would mean.

For each, name the specific metric or field the check reads, choosing from the
supplied list of available observables. A falsifier naming a field this system
does not receive is not checkable, however precise it sounds.

★ At least one condition must be about the BUSINESS rather than the price. A
falsifier set that consists only of price levels is a stop-loss wearing a
thesis's clothing, and it will fire on volatility rather than on being wrong.

You may not write "the thesis is invalidated if the investment case no longer
holds" or any variant. That is a tautology and it fails the run.

For each condition, also write its TEST: the same condition in the grammar the
answer schema declares. A test is a window of reported periods and one or more
clauses, each a comparison of the listed observables against a threshold in
the field's own units. The test must decide exactly the condition you wrote,
no more and no less. If the condition cannot be expressed in that grammar,
rewrite the condition until it can: a condition only a reader can decide is
not checkable, and it fails the run.
The window must reach your deadline: count the quarters that will have
been reported by then (about one per 91 days after the as-of date, less
60 days for the filing), and make the window at least that long. A run
of N quarters in a row is a clause with mode "consecutive" and
"consecutive": N — not mode "each" over the first N quarters, which
stops looking before the deadline.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-16 `v1`.
J16_V1_TEXT = """\
You have: the Stage-A scorecard and its evidence, the reconciliation (J-09), the
base-rate check (J-10), the bear case (J-11), the pre-mortem (J-12), the
forgery hunt (J-13), the disconfirming sweep (J-14), and the falsifiers you have
already committed to (J-15).

Select one verdict:
  BUY                 the evidence supports acquiring or adding at this price
  HOLD                the evidence supports neither acquiring nor exiting
  SELL                the evidence supports exiting
  INSUFFICIENT_DATA   the evidence does not support a directional view

And one conviction: Low | Medium | Medium-High | High.

Then, and this is the substance of the call:
  1. The three considerations that most determined the verdict, ranked, each
     naming the call it came from.
  2. ★ The strongest consideration pointing the OTHER way, and why it did not
     govern. If nothing points the other way, the analysis is incomplete —
     return INSUFFICIENT_DATA and say so.
  3. What would move this verdict one step more conservative, and by when.
  4. Your conviction is a claim about EVIDENCE, not about feeling. State it as:
     "of the evidence a verdict like this needs, the bundle supplied <what>, and
     did not supply <what>."

You are not sizing a position, setting a stop, setting a target, or naming an
entry price. Those belong to other domains and a number from you here would be
an LLM-authored price wearing an analyst's authority.

Length cap: 350 words.
"""
#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §J-17 `v1`.
J17_V1_TEXT = """\
List everything you wanted and did not have. For each:

  gap          the specific item
  why_wanted   the judgement it would have informed
  impact       which scorecard dimension or conclusion is weaker without it
  obtainable   is this something that exists and was not fetched, something the
               company does not disclose, or something nobody knows?
  would_change what your conclusion becomes if the item existed and said X, and
               what if it said Y

★ `obtainable` sorts the list into three different actions: fetch it, accept it,
or stop pretending it is knowable. Collapsing them produces a gap list nobody
can act on, which is how the block becomes decorative.

This list may not be empty. A bundle that answered every question you had means
you did not ask enough of them.
"""

#: `J-09` item 2's closed set — a FIELD enum on each requirement (`MP-5`).
J09_VERSUS_OPTIONS = ("required_less_than_evidenced", "roughly_consistent",
                      "required_more_than_evidenced", "insufficient_evidence")
#: `J-10` item 3 — typical of the class, or exceptional within it.
J10_TYPICALITY = ("typical", "exceptional")
#: `J-13` — one status per mechanism.
J13_STATUS = ("present", "absent", "insufficient_evidence")
#: `J-13`'s standing metric set, one call each (the doc's binding note). ⚠ `book_value`
#: is *(financials)* only, so a non-financial runs the first five.
J13_METRICS = ("return_on_equity", "operating_margin", "free_cash_flow", "revenue_growth",
               "non_gaap_eps", "book_value")
J13_FINANCIALS_ONLY = ("book_value",)
#: `J-13`'s placeholder, bound per call. ★ The DECLARED text keeps it, so the hash and
#: the drift guard see one text; the bound metric is recorded with each call.
METRIC_PLACEHOLDER = "<METRIC>"
#: `J-16`'s closed sets — the SAME tuples `Thesis` validates (`thesis/models.py`).
J16_VERDICTS = ("BUY", "HOLD", "SELL", "INSUFFICIENT_DATA")
J16_CONVICTIONS = ("Low", "Medium", "Medium-High", "High")
#: `J-17`'s `obtainable` — the three actions the prompt names, as a declared enum.
J17_OBTAINABLE = ("exists_not_fetched", "not_disclosed", "unknowable")


def _full_view(name: str, text: str, *, version: str = "v1") -> PromptBlock:
    """Stages B–D — `view="full"` without exception (`STAGE_VIEW`, `MP-3`)."""
    return block(name, version, "judgement", text, view="full")

def j09_v1() -> PromptBlock:
    """`J-09` — full view."""
    return _full_view("J-09", J09_V1_TEXT)

def j10_v1() -> PromptBlock:
    """`J-10` — full view."""
    return _full_view("J-10", J10_V1_TEXT)

def j11_v1() -> PromptBlock:
    """`J-11` — full view."""
    return _full_view("J-11", J11_V1_TEXT)

def j12_v1() -> PromptBlock:
    """`J-12` — full view."""
    return _full_view("J-12", J12_V1_TEXT)

def j13_v1() -> PromptBlock:
    """`J-13` — full view."""
    return _full_view("J-13", J13_V1_TEXT)

def j14_v1() -> PromptBlock:
    """`J-14` — full view."""
    return _full_view("J-14", J14_V1_TEXT)

def j15_v1() -> PromptBlock:
    """`J-15` — full view."""
    return _full_view("J-15", J15_V1_TEXT)

def j15_v2() -> PromptBlock:
    """`J-15 v2` — full view; each falsifier carries its structured test."""
    return _full_view("J-15", J15_V2_TEXT, version="v2")

def j15_v3() -> PromptBlock:
    """`J-15 v3` — v2 plus the window rule stated to the model (`DX-144`, `DX-147`)."""
    return _full_view("J-15", J15_V3_TEXT, version="v3")

def j16_v1() -> PromptBlock:
    """`J-16` — full view."""
    return _full_view("J-16", J16_V1_TEXT)

def j17_v1() -> PromptBlock:
    """`J-17` — full view."""
    return _full_view("J-17", J17_V1_TEXT)


#: The version this repo currently ships. ★ One name to change at the next bump.
E01_CURRENT_VERSION = "v4"

#: ★ Every declared block: id -> (factory, item ids, current version).
#: ⚠ A block absent here is NOT runnable — `E-03` `E-05` `E-08` `E-11` `E-14`
#: `E-15` remain design-doc only, because a registry entry nothing calls is a claim, not a capability.
BLOCKS = {
    "E-01": (e01_v4, E01_ITEM_IDS, E01_CURRENT_VERSION),
    "E-02": (e02_v2, E02_V2_ITEM_IDS, "v2"),
    "E-04": (e04_v1, E04_ITEM_IDS, "v1"),
    "E-06": (e06_v1, E06_ITEM_IDS, "v1"),
    "E-07": (e07_v1, E07_ITEM_IDS, "v1"),
    "E-09": (e09_v2, E09_ITEM_IDS, "v2"),     # ✏ `DX-96` — v1 thought itself out of budget
    "E-10": (e10_v1, E10_ITEM_IDS, "v1"),
    "E-12": (e12_v1, E12_ITEM_IDS, "v1"),
    "E-13": (e13_v1, E13_ITEM_IDS, "v1"),
    # ✏ 2026-10-04 — `L3` §2.1p row 6. ⊘ `E-14` `J-18` `J-19` deferred with their workflows.
    "E-03": (e03_v1, E03_ITEM_IDS, "v1"),
    "E-05": (e05_v1, E05_ITEM_IDS, "v1"),
    "E-08": (e08_v2, E08_ITEM_IDS, "v2"),     # ✏ DX-148 ⓑ — in.type is the form's code
    "E-11": (e11_v1, E11_ITEM_IDS, "v1"),
    "E-15": (e15_v1, E15_ITEM_IDS, "v1"),     # ✏ 2026-10-04 — the sector ingest (sector.v2)
    # ⚠ `J-01` is a JUDGEMENT block: its "item ids" are the closed option set,
    #   not evidence ids. ★ `RA-5` keeps extraction and judgement apart —
    #   extraction has ground truth, judgement has a recorded judge.
    "J-01": (j01_v1, J01_OPTIONS, "v1"),
    # ★★ Stage A completed 2026-09-11 (`DX-64`). ⚠ `options` is the block's
    # ANSWER set; empty means "not an enum answer", never "not yet filled in".
    "J-02": (j02_v1, (), "v1"),
    "J-03": (j03_v1, (), "v1"),
    "J-04": (j04_v1, (), "v1"),
    "J-05": (j05_v1, (), "v1"),
    "J-06": (j06_v1, (), "v1"),
    "J-07": (j07_v1, J07_OPTIONS, "v1"),
    "J-08": (j08_v1, (), "v1"),
    # ★★ `F10` `D5` — declared 2026-09-13; in `STAGE_A_ORDER` since 2026-09-14.
    "J-20": (j20_v1, (), "v1"),
    # ★★ Stages B–D — declared 2026-09-14, full view; run by `tools/run_thesis_once.py`.
    "J-09": (j09_v1, (), "v1"),
    "J-10": (j10_v1, (), "v1"),
    "J-11": (j11_v1, (), "v1"),
    "J-12": (j12_v1, (), "v1"),
    "J-13": (j13_v1, (), "v1"),
    "J-14": (j14_v1, (), "v1"),
    "J-15": (j15_v3, (), "v3"),     # ✏ 2026-10-04 — v2 + the window rule (DX-144, DX-147)
    "J-16": (j16_v1, (), "v1"),
    "J-17": (j17_v1, (), "v1"),
}
