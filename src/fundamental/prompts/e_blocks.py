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
    # ★★ `F10` `D5` — declared 2026-09-13. ⚠ Not in `STAGE_A_ORDER` yet: adding it
    #   changes what `--stage-a` sends and costs; run it with `--block J-20`.
    "J-20": (j20_v1, (), "v1"),
}
