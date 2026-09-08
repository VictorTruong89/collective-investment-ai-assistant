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

#: Verbatim from `L1-fundamental-analysis-master-prompt.md` §E-01 `v1`.
E01_V1_TEXT = """\
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


def e01_v1() -> PromptBlock:
    """`E-01` — segment revenue and operating income, `v1`."""
    return block("E-01", "v1", "extraction", E01_V1_TEXT)
