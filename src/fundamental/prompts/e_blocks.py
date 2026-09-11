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

⚠ Only `E-01` is declared. `E-02`…`E-15` stay in the design doc until something
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


def e02_v2() -> PromptBlock:
    """`E-02` `v2` — guidance, without the derived direction label."""
    return block("E-02", "v2", "extraction", E02_V2_TEXT)


def e02_v1() -> PromptBlock:
    """`E-02` — stated guidance and its revision, `v1`."""
    return block("E-02", "v1", "extraction", E02_V1_TEXT)


def e01_v3() -> PromptBlock:
    """`E-01` `v3` — candidate. ⚠ Not shipped until a live run verifies it."""
    return block("E-01", "v3", "extraction", E01_V3_TEXT)


def e01_v2() -> PromptBlock:
    """`E-01` — segment revenue and operating income, `v2`."""
    return block("E-01", "v2", "extraction", E01_V2_TEXT)


#: The version this repo currently ships. ★ One name to change at the next bump.
E01_CURRENT_VERSION = "v3"

#: ★ Every declared block: id -> (factory, item ids, current version).
#: ⚠ A block absent here is NOT runnable — `E-03`…`E-15` remain design-doc only,
#: because a registry entry nothing calls is a claim, not a capability.
BLOCKS = {
    "E-01": (e01_v3, E01_ITEM_IDS, E01_CURRENT_VERSION),
    "E-02": (e02_v2, E02_V2_ITEM_IDS, "v2"),
    # ⚠ `J-01` is a JUDGEMENT block: its "item ids" are the closed option set,
    #   not evidence ids. ★ `RA-5` keeps extraction and judgement apart —
    #   extraction has ground truth, judgement has a recorded judge.
    "J-01": (j01_v1, J01_OPTIONS, "v1"),
}
