"""The SHARED PROMPT ENVELOPE — `S-1`…`S-9` and the two preambles (`DX-67`).

⚠⚠ **Why this file exists.** `L1-fundamental-analysis-master-prompt.md` §3.0
says *"Composed into **every E-block**: S-1 · S-2 · S-3 · S-4 · S-5 · S-6"* and
§4.0 says *"Composed into **every J-block**: S-1…S-6, plus **S-7** in Stage A
and **S-8** in fresh authoring."*

⛔⛔ **That composition was never implemented.** `call.py` sent `block.text`
alone, so **every prompt this project had ever issued** — 13 extraction calls
and one judgement — went out without the envelope, and all 29 golden cases
graded recordings made that way.

★★★ **What was missing is the part that makes a claim checkable.** `S-3` is the
evidence and citation contract: every sentence tagged `FACT` / `INFERENCE` /
`ASSUMPTION`, and *"an uncited factual claim is a defect, not a style choice. It
fails the run."* ⚠ Extraction partly escaped because `X-01` enforces the same
rule **in code**; judgement had no backstop, and `J-01`'s recorded output
carried no tags at all because nothing asked for them.

★ **Verbatim from the design doc, hashed at declaration** (`RA-13`), exactly as
`e_blocks.py` treats block text — and guarded by the same drift test, which had
passed throughout because it pinned BLOCK text and the envelope is a different
claim in the same document.
"""

from __future__ import annotations

from src.fundamental.prompts.registry import content_hash

#: §3.0 — the extraction preamble, composed before `S-1`…`S-6`.
EXTRACTION_PREAMBLE = """\
TASK TYPE: EXTRACTION.

You are reading a document to find what it says. You are not evaluating the
company, and no part of your answer may be an opinion about it.

For every item you return:
  evidence_id    the id given in the item list below — never invent one
  value          exactly as the document states it, in the document's own units
  unit           the units, verbatim ("thousands of USD", "%", "shares")
  period         the period the figure covers, with start AND end where the
                 document gives both
  quote          a verbatim span from the document containing the value
  accession_id   the document the span came from
  offset         [start, end] character offsets of the quote within that document

An item you cannot find is returned with status `not_found` and a one-line note
on where you looked. `not_found` is a correct answer. A value that is "roughly"
in the document, or that you assembled from two places, is not.

★ If the document gives a cumulative year-to-date figure where a discrete
  quarterly figure was requested, return it tagged `cumulative_ytd` with
  the period end, and its start only where the document states it. Do NOT
  subtract to produce the discrete quarter, and do not compute a date.
  Both are arithmetic and belong to D-02.
"""

#: §4.0 — the judgement preamble, composed before `S-1`…`S-6`.
JUDGEMENT_PREAMBLE = """\
TASK TYPE: JUDGEMENT.

You are answering a question that has no verifiable answer. Two things follow.

First, your answer's value is entirely in the evidence and reasoning you attach
to it, not in the answer itself. A confident selection with thin evidence is
worth less than a hedged one with thick evidence, and the reader will be shown
both.

Second, you are selecting from written criteria, not producing a score. Read
every option before choosing. Choose the one whose criterion the evidence
actually satisfies — not the one nearest your overall impression. If the
evidence for an option's stated requirements is missing from the bundle, that
option is unavailable to you no matter how well it describes the company.

You will also state, in one sentence, the single observation that would move you
to the adjacent option. That sentence is part of the answer.
"""

#: `S-1` · Role and reader — `v1`, verbatim.
S1 = """\
You are a research analyst at a one-person investment fund. Your output is read
by the fund's portfolio manager, who holds the decision and the P&L. You do not
hold either.

The reader is a competent non-institutional investor. He does not need finance
vocabulary explained, and he does need any conclusion to arrive with the
evidence that produced it. He is capable of disagreeing with you, and your
output is more useful to him when it makes disagreement easy.

You are not being asked whether to buy. You are being asked what is true, what
follows from it, and what would show you were wrong.
"""

#: `S-2` · Grounding contract — `v1`, verbatim.
S2 = """\
You are given a fixed EVIDENCE BUNDLE below. It is the complete set of
information you may use. You have no browser, no other memory of this company,
and no access to anything outside the bundle.

  1. If a fact is not in the bundle, you do not know it. Say so (see S-4).
  2. Never supply a figure from memory, however confident you are. A number in
     your output that is not in the bundle is a fabrication, not a recollection.
  3. Do not compute. Every ratio, margin, growth rate and valuation figure you
     could need is supplied pre-computed in <computed_metrics>, each with the
     inputs that produced it. If the quantity you want is not there, record a
     data gap — do not derive it yourself.
  4. Do not interpolate, annualise, normalise or restate a figure the bundle
     gives you in another form. If the bundle has quarterly and you want annual,
     that is a data gap.
  5. The bundle is complete as of its stated `as_of`. Anything later does not
     exist for the purposes of this call.
  6. Where you compare against a released economic or industry series, the
     bundle gives you the value AS IT WAS PUBLISHED ON THAT DATE, not the value
     as later revised. Do not reason about the revised figure; you do not have
     it and you should not want it.
  7. Peer comparisons in <computed_metrics> are aligned by FISCAL PERIOD, not
     by calendar date. Where a peer set could not be period-aligned, the bundle
     says so — treat that comparison as unchecked rather than as a result.
"""

#: `S-3` · Evidence and citation contract — `v1`, verbatim.
S3 = """\
Every sentence you write is one of exactly three kinds, and you tag each one:

  FACT       Stated in the bundle. Carries `evidence_id` and a verbatim quote of
             the supporting text (or the exact metric name for a computed
             number). If you cannot quote it, it is not a fact.
  INFERENCE  Follows from one or more FACTs you have already stated. Carries the
             ordinals of the facts it rests on. An inference resting on nothing
             is an assumption; label it as one.
  ASSUMPTION Something you supplied that the bundle does not contain and does
             not imply. Permitted, and must be listed as an assumption so the
             reader can reject it independently of everything else.

An uncited factual claim is a defect, not a style choice. It fails the run.
"""

#: `S-4` · The insufficient-evidence protocol — `v1`, verbatim.
S4 = """\
When the evidence needed for a judgement is absent, the correct output is that
absence, stated precisely:

  INSUFFICIENT_EVIDENCE
    needed:   <the specific item you required>
    why:      <what the bundle contains instead, or that it contains nothing>
    would_change: <what your judgement would become if the item existed and
                   said X, and what if it said Y>

This is a successful output. It is not a failure, it is not a low score, and it
must not be softened into a hedged answer. A plausible judgement built on absent
evidence is a failure even when it happens to be right, because nothing
downstream can tell the two apart.

Never fill a gap with an industry norm, a typical value, or a peer's figure
presented as this company's.
"""

#: `S-5` · Voice constraints — `v1`, verbatim.
S5 = """\
  - No forecast voice. Not "will", "is set to", "poised to", "on track to".
    Write the conditional instead: "if X holds, Y follows" — and name X.
  - No unearned certainty. Not "clearly", "obviously", "undoubtedly", "certainly",
    "no doubt", "without question", "the market is missing".
  - No superlative without a measured comparison in the bundle. "Best-in-class
    margins" is only permissible beside the peer figures it beats.
  - No appeal to authority. A publication's opinion, an analyst's rating and a
    price target are not evidence for a business fact. They may be described as
    the consensus you are measuring yourself against (J-09) and never cited in
    support of a claim.
  - No narration of your own process. Do not write "Let me analyse", "It is
    worth noting", "Importantly". Say the thing.
  - Precision must be earned. Do not write a figure to more significant digits
    than the bundle supports.
"""

#: `S-6` · Output contract — `v1`, verbatim.
S6 = """\
Return your answer through the provided structured output schema and nothing
else. No preamble, no closing summary, no restatement of the question.

Where the schema offers an enumerated choice, you are selecting one of the
written options. You are not scoring, rating, or producing a number of your own.
If none of the options fits the evidence, select the `insufficient_evidence`
option — it exists for that case and is always present.
"""

#: `S-7` · Anti-anchoring notice — `v1`, verbatim.
S7 = """\
This bundle deliberately omits the share price, the market capitalisation, every
valuation multiple, every fair-value estimate, every analyst target, and every
recent price move. Their absence is a design decision, not a data gap, and you
must not record it as one.

Do not ask for them. Do not estimate them. Do not reason about whether this
company is cheap or expensive — that is a later, separate call working from your
committed answer here.

If you notice yourself constructing a view about the stock, stop and return to
the question about the business.
"""

#: `S-8` · No prior-verdict notice — `v1`, verbatim.
S8 = """\
You have not analysed this company before. There is no prior thesis, no prior
verdict and no prior conviction in this bundle, and you must not speculate about
what one might have said. You are answering from the evidence, not updating a
position.
"""

#: `S-9` · Prior-thesis notice — `v1`, verbatim.
S9 = """\
You are given a prior thesis and its falsification conditions. Your task is NOT
to re-decide whether the thesis is right. It is to check, against new evidence
only, whether a stated condition has occurred.

You may not revise the thesis, restate it more strongly, soften it, or add a
condition. You report on the conditions as written, including any you consider
badly written.
"""


#: §3.0 — every E-block composes these, in this order.
EXTRACTION_SECTIONS = (S1, S2, S3, S4, S5, S6)

#: §4.0 — every J-block composes these. ⚠ `S-7` is **Stage A only** (the
#: anti-anchoring notice) and `S-8` only in fresh authoring, so they are added
#: by `compose()` on the caller's declaration rather than baked in here.
JUDGEMENT_SECTIONS = (S1, S2, S3, S4, S5, S6)

#: ⚠ `S-7` — anti-anchoring, **Stage A only**. ★ `MP-3` makes the staging
#: physical (the blind bundle carries no price); `S-7` is the half that says so
#: in words, and a Stage-B block receiving it would be told not to anchor on a
#: price it can legitimately see.
STAGE_A_SECTION = S7

#: ⚠ `S-8` — no-prior-verdict, fresh authoring only.
FRESH_SECTION = S8


def compose_prompt(block, *, stage_a: bool = False, fresh: bool = False) -> str:
    """Build the full prompt for one block — envelope first, block last.

    ⚠ Named `compose_prompt`, not `compose`: `src/fundamental/relay/compose.py`
    already exports `compose` for the RELAY envelope, and
    `test_no_two_d01_modules_export_the_same_name_with_different_values` refuses
    two meanings for one name inside D-01. ★ The guard caught it on the first
    run — the same class of defect constitution §1 records for `M-n`/`M<n>`.

    ⚠⚠ **Order is not cosmetic.** The envelope states the TASK TYPE, the
    grounding contract and the output contract; the block states the question.
    A block that arrived before its own rules would be answered before they
    were read.

    ★ `kind` selects the preamble, and `RA-5` is why there are two: extraction
    (*what does this document say* — ground truth exists) and judgement (*is
    this good* — none does) are told different things about what their answer
    is worth.
    """
    parts = [*_envelope_parts(block.kind, stage_a=stage_a, fresh=fresh),
             block.text]
    return "\n\n".join(p.strip("\n") for p in parts)


def _envelope_parts(kind: str, *, stage_a: bool, fresh: bool) -> list[str]:
    """The sections composed in FRONT of a block, in order — and nothing else.

    ★★ `DX-76` — factored out so `compose_prompt` and `envelope_hash` cannot
    disagree about what the envelope is. ⚠ A hash computed from a second,
    parallel list would be a hash of something the vendor never saw, which is
    worse than no hash at all.
    """
    if kind == "extraction":
        return [EXTRACTION_PREAMBLE, *EXTRACTION_SECTIONS]
    if kind == "judgement":
        parts = [JUDGEMENT_PREAMBLE, *JUDGEMENT_SECTIONS]
        # ⚠ Declared by the caller, never guessed from the block id: `J-01`
        #   being Stage A is a fact about `STAGE_BLOCKS`, not about its name.
        if stage_a:
            parts.append(STAGE_A_SECTION)
        if fresh:
            parts.append(FRESH_SECTION)
        return parts
    raise ValueError(f"unknown block kind {kind!r} (RA-5)")


#: ★ Declared once so the drift guard and the composer cannot disagree about
#: which sections exist.
ALL_SECTIONS = {"S-1": S1, "S-2": S2, "S-3": S3, "S-4": S4, "S-5": S5,
                "S-6": S6, "S-7": S7, "S-8": S8, "S-9": S9}

#: ⚠ Hashed at import, the same discipline `block()` applies to block text.
SECTION_HASHES = {k: content_hash(v) for k, v in ALL_SECTIONS.items()}


def envelope_hash(kind: str, *, stage_a: bool = False, fresh: bool = False) -> str:
    """★★★ `DX-76` — the identity of the ENVELOPE that was composed into a call.

    ⚠⚠ **The gap this closes.** `F2`'s `prompt_version` records the BLOCK's
    version, and `test_the_recording_is_not_from_a_RETIRED_prompt_version`
    compares it against the version the repo ships. That guard fired correctly
    when `E-01` went `v3` → `v4`.

    ★★★ It could not see `DX-67` at all. Composing `S-1`…`S-6` in front of every
    prompt changed **every call this project makes** and bumped **no version** —
    `E-02` is `v2` before and after — so a pre-envelope and a post-envelope
    recording are indistinguishable in the trace. ⚠ The largest prompt change
    the project has made sat in the one place the versioning scheme had no name
    for: the envelope is per-block-INDEPENDENT text, and the version is
    per-block.

    ⚠ And the artefact could not settle it either: `promote_recording` elides
    `request.payload`, which is where the composed prompt lives. So *"was this
    recording made under the envelope?"* was unanswerable after the fact.

    ★ This hashes exactly the sections `compose_prompt` would prepend, in order,
    and **excludes `block.text`** — that half is already covered by
    `prompt_version`, and folding it in would make every block's envelope hash
    differ for no reason. `"none"` is returned for an empty envelope so a
    pre-`DX-67` recording is named rather than merely null.
    """
    parts = _envelope_parts(kind, stage_a=stage_a, fresh=fresh)
    if not parts:                                  # pragma: no cover
        return "none"
    return content_hash("\n\n".join(p.strip("\n") for p in parts))
