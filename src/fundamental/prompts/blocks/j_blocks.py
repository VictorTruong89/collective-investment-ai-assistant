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

#: ✏✏ **`DX-110` (Victor, 2026-09-14/15): ONE declaration per block.** This file held its
#: own `J-11 v1` text (*"State the strongest case that this investment is a mistake…"*) —
#: a DIFFERENT prompt from the master prompt's `J-11 v1`, under the same name and version —
#: and ran J-11 and J-15 on the BLIND view, while the master prompt and `author.py`'s own
#: `STAGE_VIEW` put Stages C and D on `view:full`. ★ The blocks now come from `e_blocks.py`,
#: the drift-guarded copy of the doc, so a recording under `J-11 v1` means one prompt.
from src.fundamental.prompts.e_blocks import (  # noqa: E402
    J11_V1_TEXT,
    J15_V1_TEXT,
    J16_V1_TEXT,
    J16_VERDICTS,
    j11_v1,
    j15_v1,
)

J15_TEXT, J16_TEXT, J11_TEXT = J15_V1_TEXT, J16_V1_TEXT, J11_V1_TEXT
#: ⚠ 2026-10-01 — this ORCHESTRATED path stays on `J-15 v1`, deliberately. `thesis/run.py`
#:   parses J-15's falsifiers out of PROSE with no answer schema, and `v2` asks for a test
#:   "in the grammar the answer schema declares". The Stage B–D runner
#:   (`tools/run_thesis_once.py`, via `e_blocks.BLOCKS`) ships `v2`. ⬜ Moving this path to the
#:   structured Stage B–D calls is go-live work (`L3` §2.1p item 10), not a version bump.
J15 = j15_v1()
J11 = j11_v1()
#: J-16 sees the full bundle — the reconciliation stage. ★ Declared with its options here
#: (same text, same hash) because `RA-17` permutes them per call on this path.
J16 = block("J-16", "v1", "judgement", J16_TEXT, view="full", options=J16_VERDICTS)

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
