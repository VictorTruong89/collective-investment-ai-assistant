"""The EvidenceBundle — §5. ENTITY layer: stdlib only (CA-1).

```
NOTHING IN §7 IS MEASURABLE IF THE INPUTS MOVE.

An analysis that differs from yesterday's may differ because the model is
stochastic, or because a filing landed, or because a price moved, or because
D-02 changed a formula. THOSE MUST BE DISTINGUISHABLE, and only pinning
makes them so.
```

★ **This is why B4.1 goes first** (L3 **BS-25**): it ships the whole
reproducibility apparatus **before the first judgement exists**, which is what
makes it look skippable. ⚠ *Without it, §7's entire measurement programme has
nothing to key on, and every judgement built before it is unattributable after
the fact.*
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date

#: §5's table — the five pinnable parts and what pins each. A part kind absent
#: from here cannot enter a bundle, because **a part with no stated pin is a
#: part that can change without the hash noticing** (RA-2).
PIN_FIELDS: dict[str, tuple[str, ...]] = {
    "filing":      ("accession_id",),
    "news":        ("source", "external_id", "published_date"),
    "computed":    ("contract_name", "contract_version"),
    "profile":     ("as_of",),
    "prior_thesis": ("thesis_version",),          # invalidation only — RA-39
    #: B4.7's sector file (RA-102, AC-1.71). Declared now so the hash contract
    #: does not change when it lands — a bundle whose hash definition moves
    #: invalidates every baseline recorded against the old one.
    "sector_file": ("industry", "schema_version", "file_version"),
    #: ★★ The observable field names a falsifier may cite (RA-35, J-15).
    #: ⚠ *Added 2026-08-26 on the first live authoring run.* It began life as a
    #: `computed` part and **the blind view withheld it** — so J-15, told to
    #: *"name the field the check reads, choosing from the supplied list"*,
    #: was never shown a list. The model noticed and said so:
    #: *"this bundle carries filing line items and disclosure text only"*.
    #: ★ Its own kind, because **a list of field NAMES is not a price anchor**
    #: and RA-14 withholds anchors, not vocabulary.
    "observables": ("contract_name", "contract_version"),
    #: ★★ Margins, returns, leverage, turnover — **and nothing price-derived.**
    #: ⚠ *Added 2026-08-26 capturing Class-B observations.* Its own kind rather
    #: than `computed` **precisely because `computed` is what RA-14 strips**:
    #: *"is this a good business?"* is the question a margin answers, and a
    #: blind pass that cannot see one has been denied the evidence it exists to
    #: weigh. The 26 price-derived keys in the same vendor payload go to
    #: `computed` instead — see `for_ticker.OPERATING_RATIOS`.
    "operating_ratios": ("contract_name", "contract_version"),
    #: ★★★ `DX-85`ⓒ — one E-block's VERIFIED output, so a judgement bundle can
    #: carry the evidence ids a rubric level cites (`RA-32`). *Approved by
    #: Victor 2026-09-12.* ⚠ Raw filing text carries no evidence id (`MP-4`):
    #: until this kind existed, `J-03`…`J-06` could not be scored even in
    #: principle.
    #: ★ Pinned by WHICH prompt ran over WHICH bundle in WHICH recorded run, and
    #: by the ids it found — `evidence_ids` is checked against the content in
    #: `__post_init__`, because a declared id the content does not carry is a
    #: rubric level made available by assertion.
    #: ⚠ Adding a kind moves no existing hash: `bundle_hash` covers each part's
    #: kind, pins and content, never this table.
    #: ★★ `searched_ids` (`DX-99`) — every item the block explicitly RETURNED,
    #: `found` or `not_found`. It lets a rubric level rest on a stated ABSENCE
    #: ("no non-GAAP add-back"), which `evidence_ids` (found only, `RA-66`)
    #: cannot express. ⚠ Added before any baseline existed for this kind.
    "extraction": ("block_id", "prompt_version", "source_bundle_hash", "run_id",
                   "evidence_ids", "searched_ids"),
    #: ★★ A COMMITTED stage output a later stage reads and may not revise (`RA-108`,
    #: `S-9`'s relationship; L3 §2.1g step 4, 2026-09-14). Pinned by the commit's own
    #: content hash, so a later call's `bundle_hash` proves WHICH commitment it read.
    #: ⚠ Withheld from every blind view (below): Stage B–D outputs carry the price.
    "stage_output": ("stage", "block_id", "prompt_version", "run_id", "commit_hash"),
}

#: Parts a BLIND view withholds (RA-14). ★ The qualitative passes run with price,
#: market cap and valuation **withheld**, and valuation is revealed only at the
#: reconciliation stage — *after the qualitative view is committed and hashed*.
#:
#: ⚠ **`observables` is deliberately NOT here.** It carries field *names*, not
#: values — `f_gross_margin` tells the model what is checkable, never what it
#: is worth. Withholding it made J-15 unable to obey its own instruction, and
#: RA-14 withholds **anchors, not vocabulary**.
#:
#: ✏ 2026-09-14 — `stage_output` joins: a Stage B–D commitment has READ the price, so
#: it is an anchor by construction. ★ No blind call reads any stage output, so this
#: withholds nothing any existing bundle carries (every recorded hash is unchanged).
BLIND_WITHHELD_KINDS = ("computed", "stage_output")


def _assert_extraction_ids_match_content(pins: dict, content: str) -> None:
    """`DX-85`ⓒ — an `extraction` part's declared ids ARE its found items' ids.

    ★★ `evidence_ids_in` trusts `pins["evidence_ids"]`, and `RA-32` makes a
    rubric level available on that set. ⚠ So a pin claiming an id the content
    does not carry would open a level by assertion — and one omitting a found
    id would close a level for a naming reason. Both refuse (`P5`).
    ⚠ `RA-66`: a `not_found` item is NOT evidence and must not be declared.
    """
    declared = pins["evidence_ids"]
    # ★ Compared as a LIST against the sorted found set below, so an unsorted
    #   or duplicated declaration refuses too (`RA-4` — one set, one hash).
    if not isinstance(declared, (list, tuple)):
        raise ValueError(
            f"extraction part {pins.get('block_id')}: `evidence_ids` must be a "
            f"list, got {type(declared).__name__}")
    try:
        items = json.loads(content)["items"]
        found = sorted({i["evidence_id"] for i in items if i["status"] == "found"})
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError(
            f"extraction part {pins.get('block_id')}: content is not an "
            f"extraction result ({exc!r}) — its evidence ids cannot be checked") from exc
    if list(declared) != found:
        raise ValueError(
            f"extraction part {pins.get('block_id')}: pins declare "
            f"{list(declared)} but the content's FOUND items are {found}. ⚠ RA-32 "
            f"would open or close rubric levels on a set the evidence does not "
            f"support (RA-66: not_found is not evidence)")
    # ★ `DX-99` — the same check for what the block SEARCHED.
    searched = pins["searched_ids"]
    returned = sorted({i["evidence_id"] for i in items})
    if not isinstance(searched, (list, tuple)) or list(searched) != returned:
        raise ValueError(
            f"extraction part {pins.get('block_id')}: pins declare searched "
            f"{searched!r} but the content RETURNED {returned}. ⚠ A `searched:` "
            f"level would rest on an absence nobody stated (DX-99)")


@dataclass(frozen=True, slots=True)
class BundlePart:
    """One pinned piece of evidence.

    `pins` is what makes the part *identifiable*; `content` is what the model
    reads. Both are hashed: two filings with the same text and different
    accession ids are different evidence, and two with the same id and different
    text mean something upstream is wrong.
    """

    kind: str
    pins: dict
    content: str

    def __post_init__(self) -> None:
        if self.kind not in PIN_FIELDS:
            raise ValueError(
                f"unknown bundle part kind {self.kind!r}; §5 declares "
                f"{sorted(PIN_FIELDS)}. A part with no stated pin can change "
                f"without the hash noticing (RA-2)"
            )
        missing = [f for f in PIN_FIELDS[self.kind] if f not in self.pins]
        if missing:
            raise ValueError(
                f"{self.kind} part is missing pin field(s) {missing}. §5 pins a "
                f"{self.kind} by {list(PIN_FIELDS[self.kind])} — an unpinned part "
                f"makes the bundle unreproducible (RA-2, RA-4)"
            )
        if self.kind == "extraction":
            _assert_extraction_ids_match_content(self.pins, self.content)

    @property
    def sort_key(self) -> tuple:
        """★ RA-4's determinism depends on this and nothing else.

        Ordering by `(kind, pins, content-digest)` rather than by arrival order
        is what makes *"same as_of ⇒ same bundle ⇒ same hash"* true regardless
        of the order D-07 happened to return things in (INV-2, PD-20).
        """
        return (self.kind,
                json.dumps(self.pins, sort_keys=True, separators=(",", ":"), default=str),
                hashlib.sha256(self.content.encode("utf-8")).hexdigest())

    def to_json_obj(self) -> dict:
        return {"kind": self.kind, "pins": self.pins, "content": self.content}


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    """The complete, ordered, hashed set of what the model is allowed to see.

    ★ **RA-1: every LLM call takes an EvidenceBundle and nothing else.** No
    ambient retrieval, no live fetch mid-prompt, no tool that reaches outside it.

    ⚠ **RA-19: the bundle is not curated by the layer that judges.** Assembly is
    mechanical and as-of-driven — *if the judging layer could choose its
    evidence, confirmation bias would have a supply chain.*
    """

    ticker: str
    as_of: date
    parts: tuple[BundlePart, ...]
    view: str = "full"
    #: Set on a derived view, so a redacted bundle is traceable to the one it
    #: came from. Two hashes, one lineage — RM-1 compares within a hash, and
    #: RA-14's staging needs to know the blind pass belonged to this analysis.
    derived_from: str | None = None
    withheld_kinds: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.parts:
            raise ValueError(
                f"an empty EvidenceBundle for {self.ticker} would pass RA-1's letter "
                f"and defeat it entirely — a call with nothing to read produces a "
                f"judgement from the prompt alone"
            )
        object.__setattr__(self, "parts", tuple(sorted(self.parts, key=lambda p: p.sort_key)))

    # -- the hash ------------------------------------------------------------ #

    @property
    def bundle_hash(self) -> str:
        """★ RA-2. Two runs with the same hash are comparable; two with different
        hashes are not, **and any variance measurement across them is meaningless**.

        The hash covers the ticker, the `as_of`, the view, and every part's pins
        AND content — deliberately not the assembly timestamp, which would make
        every bundle unique and RM-1 unmeasurable.
        """
        payload = json.dumps(
            {
                "ticker": self.ticker, "as_of": self.as_of.isoformat(),
                "view": self.view, "withheld": list(self.withheld_kinds),
                "parts": [p.to_json_obj() for p in self.parts],
            },
            sort_keys=True, separators=(",", ":"), default=str,
        )
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # -- views ---------------------------------------------------------------- #

    def redact(self, kinds=BLIND_WITHHELD_KINDS, *, view: str = "blind") -> EvidenceBundle:
        """RA-14 — a staged view with price, market cap and valuation withheld.

        ★ **A view is a NEW bundle with its own hash and a recorded parent**, not
        a flag on this one. ⚠ A `blind: bool` would let one hash stand for two
        different things the model saw, and RM-1's whole premise is that a hash
        identifies *what was read*.

        ⚠ **B4.1 provides the mechanism; B4.4 owns the staging** (L3 §3A.2). It is
        here now because the hash contract cannot change later without
        invalidating every baseline recorded against it.
        """
        kinds = tuple(kinds)
        kept = tuple(p for p in self.parts if p.kind not in kinds)
        if not kept:
            raise ValueError(
                f"redacting {list(kinds)} would empty the bundle for {self.ticker}. "
                f"A blind pass with nothing left to read is not a blind pass"
            )
        return EvidenceBundle(
            ticker=self.ticker, as_of=self.as_of, parts=kept, view=view,
            derived_from=self.bundle_hash, withheld_kinds=kinds,
        )

    # -- reading -------------------------------------------------------------- #

    def of_kind(self, kind: str) -> tuple[BundlePart, ...]:
        return tuple(p for p in self.parts if p.kind == kind)

    def contains(self, text: str) -> bool:
        """RA-6's primitive — is this value actually in the bundle?

        ⚠ **B4.2 owns the real span check.** This is the crude containment test
        the seam needs to refuse an obviously-unsourced value; it is not
        `X-01`/`X-02`, and the blueprint says so.
        """
        return any(text in p.content for p in self.parts)

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "as_of": self.as_of.isoformat(),
            "bundle_hash": self.bundle_hash, "view": self.view,
            "derived_from": self.derived_from,
            "withheld_kinds": list(self.withheld_kinds),
            "parts": [p.to_json_obj() for p in self.parts],
        }
