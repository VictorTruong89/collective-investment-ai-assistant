"""Versioned prompts and the alignment gate — INV-9, RA-13, GW-12/13/14.

```
NO CALL RUNS IF THE PROMPT SPEC AND ITS COMPONENTS HAVE DRIFTED.

A drifted prompt is an UNVERSIONED CHANGE TO THE ANALYTICAL METHOD, and it
invalidates every baseline in §7.4. Checking alignment AFTER the calls checks
nothing — the calls already ran.
```

★ **Per BLOCK, not per file.** `L4` v0.4.2 records D-01's **QR-5**: anchor
stripping (RA-14) requires splitting `prompt_stock_analysis.md`, *"whose sections
INV-9's alignment manifest tracks individually."* The J-01…J-17 and E-01…E-13
blocks are those sections, so the registry keys on a block and each carries its
own version and content hash.

⚠ **This is the alignment MECHANISM, not the inherited checker.** `L4` §1.5
classes `buffett/synthesis/prompt_alignment.py` (358 LOC) **VERBATIM**, and a
verbatim move is a pure `git mv` in its own commit (ST-6) — it cannot be done by
writing a file. The gate that AC-1.10 needs is here; the legacy checker lands at
cutover, wired in behind the same `AlignmentCheck` protocol.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from src.fundamental.errors import PromptDriftError


def content_hash(text: str) -> str:
    """What alignment compares. Whitespace is NOT normalised.

    ⚠ Deliberate: a reflowed paragraph changes what the model reads, and *"it
    was only formatting"* is precisely the edit that slips a method change past
    a version bump. Normalising would make the check agree with the intuition
    that is wrong.
    """
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class PromptBlock:
    """One versioned, hashed prompt block — an E-nn extractor or a J-nn judgement.

    `kind` is not decoration: **RA-5** requires extraction and judgement to be
    *separate calls with separate prompts*, and a registry that cannot tell them
    apart cannot enforce it. *A prompt that asks "summarise the filing and tell
    me if it's a good business" makes the verifiable half unverifiable.*
    """

    name: str                 # "J-09" | "E-01" | "thesis.judgement"
    version: str              # "v1" — bumped on ANY content change (RA-13)
    kind: str                 # "extraction" | "judgement"
    text: str
    declared_hash: str
    #: ★ RA-14. A judgement block declaring `view="blind"` must be called with a
    #: redacted bundle, and the seam checks it. A block that could be called with
    #: either view would make the anchor-stripping a convention.
    view: str = "full"
    #: RA-17 — enumerated options this block presents, order-randomised per call.
    options: tuple[str, ...] = ()

    KINDS = ("extraction", "judgement")
    VIEWS = ("full", "blind")

    def __post_init__(self) -> None:
        if self.kind not in self.KINDS:
            raise ValueError(
                f"prompt kind {self.kind!r} must be one of {self.KINDS}. RA-5 keeps "
                f"extraction and judgement in separate calls, and the registry is "
                f"where that becomes checkable"
            )
        if self.view not in self.VIEWS:
            raise ValueError(f"view {self.view!r} must be one of {self.VIEWS} (RA-14)")

    def check(self) -> None:
        """RA-13 / AC-1.10 — raise if the text no longer matches its declared hash."""
        actual = content_hash(self.text)
        if actual != self.declared_hash:
            raise PromptDriftError(self.name, self.declared_hash, actual)


class AlignmentCheck(Protocol):
    """The boundary the inherited `PromptAlignmentChecker` will implement (CA-6).

    Named for what the consumer needs — *is this prompt aligned?* — not for its
    implementation. **CA-5 qualifies it**: this boundary has already changed once
    (the legacy checker predates the block split QR-5 requires).
    """

    def __call__(self, block: PromptBlock) -> None:
        """Raise `PromptDriftError` if `block` has drifted; return otherwise."""


class PromptRegistry:
    """`prompts/master.md`'s role in code — the single-source registry (§4).

    ★ **GW-14: `prompt_name` and `prompt_version` are required arguments.** There
    is no unversioned call path, so there is no way to reach the gateway with a
    prompt this registry has never seen.
    """

    def __init__(self, blocks=(), *, alignment: AlignmentCheck | None = None) -> None:
        self._blocks: dict[tuple[str, str], PromptBlock] = {}
        self._alignment = alignment
        for block in blocks:
            self.register(block)

    def register(self, block: PromptBlock) -> PromptBlock:
        key = (block.name, block.version)
        existing = self._blocks.get(key)
        if existing is not None and existing.declared_hash != block.declared_hash:
            # The same immutability argument as D-02 FE-2, for the same reason:
            # a version that can mean two things makes every baseline recorded
            # against it a statement about an unknown.
            raise PromptDriftError(block.name, existing.declared_hash, block.declared_hash)
        self._blocks[key] = block
        return block

    def get(self, name: str, version: str) -> PromptBlock:
        hit = self._blocks.get((name, version))
        if hit is None:
            raise PromptDriftError(
                name, f"<registered: {sorted(v for n, v in self._blocks if n == name)}>",
                f"<requested {version}>",
            )
        return hit

    def check(self, name: str, version: str) -> PromptBlock:
        """★ The gate. Called BEFORE any request leaves — §4A.2 step 0.

        Runs the registry's own hash check and then any injected checker, so the
        inherited 358-LOC `PromptAlignmentChecker` composes with this rather than
        replacing it.
        """
        block = self.get(name, version)
        block.check()
        if self._alignment is not None:
            self._alignment(block)
        return block

    def check_all(self) -> None:
        """§4A.2 step 0 over the whole registry — ABORT before the run starts.

        ⚠ Checking one prompt at its call site would let a run reach step 8 and
        fail there, having already spent deep-tier tokens on steps 2–7.
        """
        for (name, version) in sorted(self._blocks):
            self.check(name, version)

    @property
    def blocks(self) -> tuple[PromptBlock, ...]:
        return tuple(self._blocks[k] for k in sorted(self._blocks))


def block(name: str, version: str, kind: str, text: str, *, view: str = "full",
          options=()) -> PromptBlock:
    """Declare a block, hashing its text now.

    ⚠ **Self-hashing is honest only because the version is the human's job.** The
    hash catches an edit made *after* declaration — a file touched in place, a
    template rendered differently. It cannot catch an author who edits the text
    and the version together, and nothing mechanical can: that is RM-4's
    prompt-change regression run, and it is B4.5's.
    """
    return PromptBlock(name=name, version=version, kind=kind, text=text,
                       declared_hash=content_hash(text), view=view,
                       options=tuple(options))
