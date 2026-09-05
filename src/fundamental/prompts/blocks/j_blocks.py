"""D-01 — the J-blocks, registered verbatim from the master prompt. MP-12, RA-13.

★ **The text is the spec's, copied exactly.** ⚠ A paraphrase here would make the
declared `prompt_version` describe a prompt that is not the one sent — and
`PromptBlock.check()` hashes the text, so a later edit without a version bump
raises rather than drifting.

★ **RA-16: J-15 runs BEFORE the verdict, as a separate call with a persisted
write between them.** *One call emitting both satisfies the old wording and buys
nothing: the falsifiers get fitted to a verdict already reached.*
"""

from __future__ import annotations

from src.fundamental.prompts.registry import PromptRegistry, block

#: `L1-fundamental-analysis-master-prompt.md` §J-15, verbatim.
J15_TEXT = """Before any verdict exists, state what would prove the emerging thesis wrong.

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
holds" or any variant. That is a tautology and it fails the run."""

#: §J-16, verbatim. ⚠ Item 4 is `confidence` with the model taken out of it.
J16_TEXT = """You have: the Stage-A scorecard and its evidence, the reconciliation (J-09), the
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

Length cap: 350 words."""

#: §J-11 — ★ RA-15: a **separate call**, so the bear case cannot be written by
#: the same pass that argued the bull.
J11_TEXT = """State the strongest case that this investment is a mistake, in its own terms.

Do not hedge it, do not answer it, and do not weaken it so the bull case
survives. Name the single condition that would confirm it.

Length cap: 500 words."""

#: ★ RA-14/MP-3 — J-11 and J-15 run on the BLIND view: price, market cap and
#: valuation withheld, so the qualitative view is committed before the anchor.
J15 = block("J-15", "v1", "judgement", J15_TEXT, view="blind")
J11 = block("J-11", "v1", "judgement", J11_TEXT, view="blind")
#: J-16 sees the full bundle — the reconciliation stage (§4A.2 step 5).
J16 = block("J-16", "v1", "judgement", J16_TEXT, view="full",
            options=("BUY", "HOLD", "SELL", "INSUFFICIENT_DATA"))

#: ★ RA-17 — the enumerated options are **order-randomised per call**, which is
#: one of RM-1's three perturbations. Declaring them here is what makes that
#: permutation possible without touching the prompt text.
ALL_BLOCKS = (J11, J15, J16)


def production_registry(*, alignment=None) -> PromptRegistry:
    """The registry a real authoring run uses. ★ Every block is hashed at
    declaration, so `check()` catches a text edit without a version bump."""
    registry = PromptRegistry(alignment=alignment)
    for prompt in ALL_BLOCKS:
        registry.register(prompt)
    return registry
