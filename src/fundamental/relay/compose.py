"""D-01 §4B / WF-8 — composing the relay prompt. RA-122, RA-123, RA-124.

★ **WF-8 composes a prompt and makes no LLM call** (AC-1.73). The request is
D-01's; the *response* arrives from outside as an external artifact.

⚠ **RA-124: the relay stays manual. No automation of a chat interface, ever** —
no browser driving, no scripted paste. It is a flat-rate personal subscription
used personally; automating it would be both a terms problem and the exact
"leak by execution" XP-33 refused. **This module therefore has no transport of
any kind**, and a test asserts it.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.fundamental.errors import RelayPromptUnattributedError

#: J-01's enum (master prompt §J-01@v1). ★ The classification governs which
#: analytical questions the rest of the analysis is allowed to ask, so it is the
#: first judgement and **the one with the widest blast radius**.
ARCHETYPES = (
    "cyclical_commodity", "compounder", "secular_growth",
    "regulated_utility", "financial", "binary_outcome", "insufficient_evidence",
)

#: Blocks every relay prompt carries, in order.
BASE_BLOCKS = ("RLY-0", "RLY-A", "RLY-B")

#: ★ RA-123 — **sector and archetype adaptation is J-01 driving block
#: selection**, and this table is that sentence made executable. *A
#: `cyclical_commodity` gets the cycle and supply-side blocks; a `financial`
#: gets book-value framing instead of EPS.* ⚠ **This is the "intelligence" that
#: places the feature in D-01** rather than in SEAT-5.
ARCHETYPE_BLOCKS = {
    "cyclical_commodity": ("RLY-CYCLE", "RLY-SUPPLY"),
    "compounder": ("RLY-ROIC", "RLY-REINVEST"),
    "secular_growth": ("RLY-TAM", "RLY-UNIT"),
    "regulated_utility": ("RLY-RATEBASE",),
    "financial": ("RLY-BOOK", "RLY-SPREAD"),
    "binary_outcome": ("RLY-EVENTS",),
    "insufficient_evidence": (),
}


@dataclass(frozen=True, slots=True)
class RelayPrompt:
    """A composed prompt and the attribution that makes it ingestible.

    ★ RA-122 — the composition is **recorded**, not just performed: MP-12
    extended to the relay. ⚠ A hand-edited prompt makes the artifact
    unattributable and silently breaks INV-9's alignment for that name.
    """

    ticker: str
    archetype: str
    blocks: tuple[str, ...]          # "RLY-0@v1" — name and version
    text: str
    passes: int = 1

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "archetype": self.archetype,
                "blocks": list(self.blocks), "passes": self.passes}


def blocks_for(archetype: str) -> tuple[str, ...]:
    """RA-123 / AC-1.75 — which blocks this archetype's prompt carries."""
    if archetype not in ARCHETYPES:
        raise ValueError(
            f"archetype {archetype!r} is not one of J-01's {ARCHETYPES}. ★ A "
            f"seventh archetype is a master-prompt change, not a relay one"
        )
    return BASE_BLOCKS + ARCHETYPE_BLOCKS[archetype]


def compose(registry, *, ticker: str, archetype: str, context: str = "",
            version: str = "v1", passes: int = 1) -> RelayPrompt:
    """RA-122 / AC-1.73 — compose from the registry. **No call is made here.**

    Every block is fetched through `registry.check`, so a block whose text has
    drifted from its declared hash raises **before** a prompt is handed to a
    human to paste (RA-13, INV-9).
    """
    names = blocks_for(archetype)
    parts, refs = [], []
    for name in names:
        block = registry.check(name, version)
        parts.append(block.text)
        refs.append(f"{block.name}@{block.version}")

    header = f"TICKER: {ticker}\nARCHETYPE: {archetype}\n"
    body = "\n\n".join(parts)
    text = f"{header}\n{body}" + (f"\n\n{context}" if context else "")
    return RelayPrompt(ticker=ticker, archetype=archetype, blocks=tuple(refs),
                       text=text, passes=passes)


def assert_prompt_attributed(ticker: str, prompt: RelayPrompt, envelope) -> None:
    """RA-122 / AC-1.74 — a hand-edited prompt fails ingest.

    ★ The check is that the blocks the response *claims* were used are exactly
    the blocks composition *produced*. ⚠ Anything else — a name added, a version
    slipped, a block dropped — means the artifact cannot be attributed to a
    prompt version, and INV-9's alignment silently stops applying to it.
    """
    claimed = tuple(envelope.prompt_blocks)
    if claimed != prompt.blocks:
        raise RelayPromptUnattributedError(
            ticker,
            f"the response cites blocks {list(claimed)!r} but composition "
            f"produced {list(prompt.blocks)!r}")
    if envelope.archetype_applied and envelope.archetype_applied != prompt.archetype:
        raise RelayPromptUnattributedError(
            ticker,
            f"the response applied archetype {envelope.archetype_applied!r} "
            f"against a prompt composed for {prompt.archetype!r} — RA-123's "
            f"block selection and the analysis disagree")
