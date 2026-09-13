"""D-01 error family (L4 §5.3). B3 slice only — the gate adapter."""

from __future__ import annotations

from src.shared.errors import PipelineError


class ResearchError(PipelineError):
    code = "RSC.UNSPECIFIED"
    retryable = False


class GateMappingError(ResearchError):
    """RA-49 — a Thesis state with no row in §11.2's table.

    ★ **A state with no row is a defect, not a default to PASS.** The mapping is
    total and deterministic: every reachable state maps to exactly one status,
    and identical theses map identically (INV-2). Falling through to PASS is
    D-12 **DN-10**'s identity-by-omission arriving one domain early.
    """

    code = "RSC.GATE.UNMAPPED_STATE"

    def __init__(self, state: str) -> None:
        super().__init__(
            f"thesis state {state!r} maps to no gate status. RA-49 requires the "
            f"mapping to be TOTAL — an unmapped state is a defect, never a default "
            f"to PASS"
        )


# --------------------------------------------------------------------------- #
# B4.1 — the bundle and the seam (§5, §6, §14's catalog)
# --------------------------------------------------------------------------- #

class BundleNotPinnedError(ResearchError):
    """RES.BUNDLE.NOT_PINNED — an LLM call without a hashed bundle (RA-1, RA-2).

    ★ **RA-1: every LLM call takes an EvidenceBundle and nothing else.** No
    ambient retrieval, no live fetch mid-prompt, no tool that reaches outside it.

    ⚠ The reason this is an *error* and not a convention: **two runs with
    different bundle hashes are not comparable, and any variance measurement
    across them is meaningless** (RA-2). An unpinned call does not merely risk a
    bad answer — it silently destroys RM-1's ability to say anything at all.
    """

    code = "RES.BUNDLE.NOT_PINNED"

    def __init__(self, what: str) -> None:
        super().__init__(
            f"{what} was attempted without a hashed EvidenceBundle. Every call takes "
            f"a bundle and nothing else (RA-1), and two runs with different hashes "
            f"are not comparable (RA-2)"
        )


class BundleInconsistentError(ResearchError):
    """RA-3 / RA-4 — the bundle is not internally consistent, or not pinnable.

    ⚠ **INV-1 applied to the input set rather than to a query.** D-07 guarantees
    each part was knowable at its own as_of; only assembly can guarantee they
    were all knowable at the **same** one.
    """

    code = "RES.BUNDLE.INCONSISTENT"


class PromptDriftError(ResearchError):
    """RES.PROMPT.DRIFT — alignment failed (INV-9, RA-13, GW-12/13).

    ★ **A drifted prompt is an unversioned change to the analytical method**, and
    it invalidates every baseline in §7.4. ⚠ Checking alignment *after* the calls
    checks nothing — the calls already ran (§4A.2 step 0).

    Surfaced to the caller, **never swallowed**: *a drift check that logs and
    proceeds is the check not existing* (GW-13).
    """

    code = "RES.PROMPT.DRIFT"

    def __init__(self, prompt_name: str, declared: str, actual: str) -> None:
        super().__init__(
            f"prompt {prompt_name!r} has drifted: registry declares content hash "
            f"{declared[:20]}…, the file is {actual[:20]}…. No call runs (INV-9). "
            f"A prompt edit is a change of analytical method and needs a version bump"
        )
        self.prompt_name = prompt_name


class ConversationalStateError(ResearchError):
    """RA-12 / AC-1.11 — a call carrying state from a previous one.

    ★ *Multi-turn accumulates path dependence, which converts a stochastic answer
    into a **stubborn** one — worse, because it looks stable.*

    ⚠ And RA-107 records what RA-12 bought for free: *"no conversational state"*
    makes every call in a stage independent by construction, which is where the
    intra-stage parallelism comes from.
    """

    code = "RES.CALL.CONVERSATIONAL_STATE"

    def __init__(self, detail: str) -> None:
        super().__init__(
            f"{detail}. Each call starts from a fresh context containing the bundle "
            f"and nothing else (RA-12) — and a resumed conversation is exactly what "
            f"the legacy [TICKER]_progress.json did (RA-109)"
        )


class DegradedCallError(ResearchError):
    """RES.LLM.DEGRADED — the call failed or returned a degraded narrative.

    ```
    ✗ emit a partial Thesis        a verdict with no stop and no targets IS D-15
    ✗ fall back to the prior one   the reader cannot tell they are reading
                                    last Tuesday's view
    ✗ vanish from the slate        a name that disappears looks like one that
                                    was considered and passed over
    ```

    ★ **RA-130**: the failed *analysis* is never persisted — but this call's
    `AnalysisRun` **is**, carrying the failing outcome, or *"did not run"* and
    *"ran and failed"* become indistinguishable (RA-111).
    """

    code = "RES.LLM.DEGRADED"

    def __init__(self, prompt_name: str, outcome: str, detail: str = "") -> None:
        super().__init__(
            f"call {prompt_name!r} returned outcome {outcome!r}: {detail}. It is "
            f"never persisted as analysis and never rendered (RA-29, P5, DC-3). "
            f"Downstream receives NO_THESIS — never a half thesis, never the "
            f"previous one, never a plausible default (RA-110)"
        )
        self.outcome = outcome


# --------------------------------------------------------------------------- #
# B4.2 — extraction and the citation spine (§6, X-01/X-02)
# --------------------------------------------------------------------------- #

class UncitedClaimError(ResearchError):
    """RES.CLAIM.UNCITED — a factual claim with no evidence span (RA-9, INV-004).

    ★ **X-02, and it is a deterministic SCHEMA check — no LLM.** *An uncited
    factual claim is a defect, not a style choice. It fails the run* (S-3).
    """

    code = "RES.CLAIM.UNCITED"

    def __init__(self, ordinal: int, text: str) -> None:
        super().__init__(
            f"claim {ordinal} is tagged a fact and carries no resolvable span: "
            f"{text[:80]!r}. If you cannot quote it, it is not a fact (S-3, RA-9)"
        )


class SpanUnresolvableError(ResearchError):
    """RA-131 — the cited offset does not resolve against the bundle.

    ⚠ Not a soft miss. An offset naming a filing the bundle does not hold, or
    running past the end of one it does, is **a citation that was never
    checkable** — and an uncheckable citation is indistinguishable from a
    fabricated one.
    """

    code = "RES.CLAIM.SPAN_UNRESOLVABLE"


class SpanMismatchError(ResearchError):
    """RES.CLAIM.SPAN_MISMATCH — X-01's FIRST half (RA-131, RM-10).

    ```
    THE OFFSET IS THE ONLY PART OF A CITATION THE MODEL CANNOT ALSO AUTHOR.
    ```

    ★ A `quote` is the model's *claim* about what the document says. Checking
    only that the value appears in the quote **verifies the model against
    itself** — a model that fabricates the quote and the value consistently
    passes, and the citation is fiction with a character range attached.
    """

    code = "RES.CLAIM.SPAN_MISMATCH"

    def __init__(self, evidence_id: str, quoted: str, actual: str) -> None:
        super().__init__(
            f"{evidence_id}: the cited span does not contain the quoted text.\n"
            f"  quoted:   {quoted[:90]!r}\n"
            f"  document: {actual[:90]!r}\n"
            f"A quote that disagrees with the document at its own offsets is not a "
            f"citation (RA-131, X-01)"
        )


class ValueNotInSpanError(ResearchError):
    """RES.EXTRACT.UNVERIFIED — X-01's SECOND half (RA-6, AC-1.3).

    ⚠ **RA-132 bounds what counts as derivable**: reformatting ONE stated figure
    (`"1,234"` → `1234`, `"(500)"` → `-500`) passes; **combining two does not**.
    Subtracting a prior year-to-date to reach a discrete quarter is *the single
    most expensive extraction error this project has actually made* — ARM at
    2.76×, MU at 71 % — and an extractor that does it silently reproduces it
    inside the LLM layer where no `TTM_SOURCE_TOLERANCE` check can see it.
    """

    code = "RES.EXTRACT.UNVERIFIED"

    def __init__(self, evidence_id: str, value: str, quote: str) -> None:
        super().__init__(
            f"{evidence_id}: extracted value {value!r} does not appear in its cited "
            f"span {quote[:90]!r}, literally or as a reformatting of one figure in "
            f"it. A value assembled from two places is arithmetic, and arithmetic is "
            f"D-02's (RA-6, RA-132, RA-45)"
        )


class SubjectIsRegistrantError(ResearchError):
    """⛔ `DX-97` — an item about ANOTHER company names the registrant itself.

    ★★★ `X-01` checks that a value is IN the document, never that it ANSWERS
    the question. Measured 2026-09-12: `E-13` (competitor capacity) returned 37
    items, every one passing `X-01`, every one **Micron's own fabs** with
    `cx.competitor = "Micron Technology, Inc."` — and loading them would have
    opened `moat_durability` level 4 on the company's own capacity.
    ⚠ The whole result is refused, not the item: the capacity rows cannot be
    separated from the competitor rows that name whose capacity they are.
    """

    code = "RES.EXTRACT.SUBJECT_IS_REGISTRANT"


class ExtractionKindError(ResearchError):
    """RA-5 / AC-1.4 — extraction and judgement mixed in one call.

    ★ *A prompt that asks "summarise the filing and tell me if it's a good
    business" makes the verifiable half unverifiable.* The split is what makes
    hallucination a **detectable class** rather than a general anxiety.
    """

    code = "RES.EXTRACT.KIND_MIXED"


# --------------------------------------------------------------------------- #
# B4.3 — the scorecard, coverage and the confidence floors (§8, RA-31…RA-38)
# --------------------------------------------------------------------------- #

class RubricMutatedError(ResearchError):
    """RA-33 / AC-1.31 — a published rubric version's content changed.

    *A rubric edit invalidates every baseline in §7.4* (RM-4). Exactly the FE-2
    argument, for the same reason: **a version that can mean two things makes
    every measurement recorded against it a statement about an unknown.**
    """

    code = "RES.RUBRIC.MUTATED"

    def __init__(self, rubric_id: str, declared: str, actual: str) -> None:
        super().__init__(
            f"{rubric_id} is already published and its content differs "
            f"({declared[:20]}… vs {actual[:20]}…). A rubric edit is a change of "
            f"analytical method and needs a version bump (RA-33)"
        )


class LevelUnavailableError(ResearchError):
    """RA-32 / AC-1.30 — a level selected without its required evidence.

    ★ *A level selected without that evidence present in the bundle is a **failed
    selection**, not a low-confidence one.*

    ⚠ **RA-66**: an item counts as extracted only if X-01 passed — *a 10-K that
    is present but from which the required number could not be pulled is not
    evidence*, and counting presence rather than extraction is how a coverage
    metric reports 100 % on a bundle nothing could be read from.
    """

    code = "RES.SCORE.LEVEL_UNAVAILABLE"

    def __init__(self, rubric_id: str, score: int, missing) -> None:
        super().__init__(
            f"{rubric_id}: level {score} was selected and requires "
            f"{sorted(missing)}, which were not extracted. An unavailable level is "
            f"a failed selection, not a low-confidence one (RA-32)"
        )


class ScoreEmittedError(ResearchError):
    """RA-31 / AC-1.29 — a number arrived where a criterion selection belonged.

    ★ *The model selects a criterion, and the score is derived from the
    selection. It never emits a number directly — **a number invites
    interpolation, and interpolation is where dispersion enters**.*
    """

    code = "RES.SCORE.EMITTED_NOT_SELECTED"


class SelfReportedConfidenceError(ResearchError):
    """RA-38 — confidence came from the model rather than from coverage.

    ```
    AP-1 asks the agent for a confidence score. A MODEL ASKED TO GATE ITSELF
    WILL NOT GATE ITSELF.
    ```

    ⚠ **RA-67 makes this structural rather than a rule someone enforces**: until
    calibration exists, `confidence := evidence_coverage`, so there is no
    model-produced number to launder in the first place.
    """

    code = "RES.CONFIDENCE.SELF_REPORTED"


# --------------------------------------------------------------------------- #
# B4.4 — authoring and the real gate (§9, §11.2)
# --------------------------------------------------------------------------- #

class VerdictNotEnumError(ResearchError):
    """RA-8 / AC-1.6 — a free-form value where an enum was required.

    ★ *Bounded outputs for anything that gates a decision.* Free prose is
    permitted only where nothing downstream branches on it — and everything
    branches on the verdict.
    """

    code = "RES.VERDICT.NOT_ENUM"

    def __init__(self, field: str, value, allowed) -> None:
        super().__init__(
            f"{field} was {value!r}; it is an enum with written criteria and admits "
            f"only {tuple(allowed)}. A free-form value invites interpolation, and "
            f"interpolation is where dispersion enters (RA-8, RA-31)"
        )


class NoFalsifierError(ResearchError):
    """RES.THESIS.NO_FALSIFIER — AC-1.32, RA-35.

    ★ *A thesis is not valid without at least one falsifier that is observable,
    dated, and checkable without a further judgement call.*
    """

    code = "RES.THESIS.NO_FALSIFIER"

    def __init__(self, ticker: str, count: int, detail: str = "") -> None:
        super().__init__(
            f"{ticker}: {count} usable falsifier(s). "
            + (detail or "A thesis with no checkable breaking condition cannot be "
                         "wrong, which means it cannot be right either (RA-35)")
        )


class UncheckableFalsifierError(ResearchError):
    """RA-35 — a condition that is not observable, dated, checkable and material.

    ⚠ **The test J-15 states: could a script decide it?** *"Competition
    intensifies" fails. "Gross margin below 55 % in two consecutive quarters"
    passes.*
    """

    code = "RES.THESIS.FALSIFIER_UNCHECKABLE"

    def __init__(self, ordinal: int, detail: str) -> None:
        super().__init__(f"falsifier {ordinal}: {detail}")


class FalsifierEditedError(ResearchError):
    """RES.THESIS.FALSIFIER_EDITED — AC-1.33, RA-36.

    ★ *Falsifiers are written at authoring time, versioned with the thesis, and
    never edited — only superseded by a new thesis version.* ⚠ **Editing a
    falsifier after the fact is how a thesis becomes unfalsifiable**: the
    condition drifts toward whatever did not happen.
    """

    code = "RES.THESIS.FALSIFIER_EDITED"

    def __init__(self, ticker: str, version: int, ordinal: int) -> None:
        super().__init__(
            f"{ticker} v{version}: falsifier {ordinal} was mutated. Superseding is "
            f"the only path — a new thesis version, with the old one intact (RA-36, "
            f"INV-006)"
        )


class UncommittedFalsifiersError(ResearchError):
    """★★ RA-16 as amended / AC-1.14 — the verdict ran without a persisted commit.

    ```
    Held in memory, the ordering is nominal and A SINGLE CALL COULD PRODUCE
    BOTH.
    ```

    ⚠ One call emitting `{falsifiers, verdict}` satisfies *"the falsifier is
    written before the verdict"* exactly and buys nothing: a model choosing both
    in one forward pass can **fit the falsifiers to the verdict it has already
    reached**, which is the anchoring RA-16 exists to prevent.
    """

    code = "RES.THESIS.FALSIFIERS_UNCOMMITTED"

    def __init__(self, ticker: str) -> None:
        super().__init__(
            f"{ticker}: the thesis carries no falsifier_commit_hash, so nothing "
            f"shows the falsifiers were persisted BEFORE the verdict call began. "
            f"J-15 -> persist -> J-16 is strictly sequential (RA-16, §4A.2 step 8)"
        )


class NullBearCaseError(ResearchError):
    """RM-11 / AC-1.18 — a bear case with no falsifiable condition of its own.

    ★ *A bear case that nothing could disprove is a mood.* Measurable without
    judgement, which is why it fails the run rather than being flagged.
    """

    code = "RES.BEAR.NULL"


class BearCaseNotSeparateError(ResearchError):
    """RA-15 / AC-1.13 — the bear case came from the same call as the bull case.

    ⚠ *A bear case written in the same breath is a **rhetorical concession**, not
    an analysis* (AP-3, INV-011).
    """

    code = "RES.BEAR.NOT_SEPARATE"


class PriorVerdictLeakError(ResearchError):
    """RA-18 / AC-1.15 — fresh authoring was handed the prior verdict.

    ★ *Fresh authoring never sees the prior verdict.* Invalidation checking is
    the exception and **must** see it (RA-39) — *re-deciding and re-checking are
    different tasks*, and the distinction is deliberate.
    """

    code = "RES.THESIS.PRIOR_VERDICT_LEAKED"

    def __init__(self, ticker: str) -> None:
        super().__init__(
            f"{ticker}: a fresh-authoring bundle carries a prior_thesis part. That "
            f"is an anchor, and RA-18 excludes it precisely because re-deciding is "
            f"not re-checking (RA-18, RA-39)"
        )


# --------------------------------------------------------------------------- #
# B4.6 — invalidation, the scheduled calendar, unscheduled events (§10, §10A/B)
# --------------------------------------------------------------------------- #

class CalendarCitedAsFactError(ResearchError):
    """RA-69 / AC-1.41 — a `Claim` cited a scheduled event as support for a fact.

    ★ *A scheduled event is evidence about the FUTURE.* It travels in its own
    `calendar` block carrying `knowable_at`, and never enters the bundle as a
    fact. ⚠ *"Earnings are on the 24th"* is not a reason for anything — and a
    claim that rests on one has cited the calendar as though it were a filing.
    """

    code = "RES.CALENDAR.CITED_AS_FACT"

    def __init__(self, claim_ref: str, event_ref: str) -> None:
        super().__init__(
            f"claim {claim_ref!r} cites scheduled event {event_ref!r} as support "
            f"for a business fact (RA-69)"
        )


class BriefMutatedError(ResearchError):
    """RA-73 / AC-1.45 — a `PreEventBrief` was edited at or after its event.

    ★ **The brief's entire value is the possibility of being wrong in public.**
    A brief editable post-event is a memory of what we would have said.
    """

    code = "RES.BRIEF.MUTATED"

    def __init__(self, brief_id: str, event_date, edited_at) -> None:
        super().__init__(
            f"pre-event brief {brief_id!r} for {event_date} was edited at "
            f"{edited_at} — it is immutable from the event onward (RA-73)"
        )


class BriefPredictsError(ResearchError):
    """RA-74 / AC-1.46 — a brief stated an expected result.

    ⚠ **A forecast wearing a process's clothing.** The brief maps *outcomes to
    falsifier states*; naming which outcome is expected re-anchors the
    post-event read the brief exists to discipline.
    """

    code = "RES.BRIEF.PREDICTS"

    def __init__(self, brief_id: str, detail: str) -> None:
        super().__init__(f"pre-event brief {brief_id!r}: {detail} (RA-74)")


class EvidenceWithdrawnError(ResearchError):
    """RA-83 / AC-1.52 — an item 4.02 covers a period a selected level cited.

    ★★ **The strongest rule in §10B.** A non-reliance filing withdraws the
    *facts* the analysis was built from, so every `ScorecardResult` citing an
    affected period is unsupported and must be **re-derived, not adjusted** —
    and the verdict is `INSUFFICIENT_DATA`, never "HOLD pending review."
    """

    code = "RES.EVIDENCE.WITHDRAWN"

    def __init__(self, ticker: str, periods, dimensions=()) -> None:
        where = ", ".join(sorted(dimensions)) or "the scorecard"
        super().__init__(
            f"{ticker}: 8-K item 4.02 withdraws {sorted(periods)!r}; {where} "
            f"cited those periods and must be re-derived (RA-83)"
        )


class MoveRationalisedError(ResearchError):
    """RA-79 / AC-1.50 — an unexplained residual came back with a cause.

    ⚠ **A plausible reason attached to an unexplained move is strictly worse
    than the honest gap.** It closes an open question with a fabrication, and
    nothing downstream can tell the two apart.
    """

    code = "RES.MOVE.RATIONALISED"

    def __init__(self, ticker: str, cause: str, *, rule: str = "RA-79") -> None:
        super().__init__(
            f"{ticker}: {cause} — report the gap, never the story ({rule})"
            if rule != "RA-79" else
            f"{ticker}: residual is unexplained but a cause was supplied "
            f"({cause[:70]!r}) — report the gap, never the story (RA-79)"
        )


class MoveUndecomposedError(ResearchError):
    """RA-88 / AC-1.56 — a move trigger fired with no residual.

    ★★ **A trigger keyed on the RAW return is measuring the sector, not the
    company** — and it fires on the days it fires on every name at once.
    ⚠ RA-91: acting on an undecomposed move is a top-down allocation call,
    SEAT-1's authority exercised without the seat and without anyone choosing to.
    """

    code = "RES.MOVE.UNDECOMPOSED"

    def __init__(self, ticker: str, detail: str = "no residual supplied") -> None:
        super().__init__(
            f"{ticker}: move trigger fired on a raw return — {detail}. The "
            f"residual is computed BEFORE the trigger, not after it (RA-88)"
        )


class SweepSilentError(ResearchError):
    """RA-86 / AC-1.54 — a weekly sweep produced no report at all.

    ★ *A sweep that appears only when it has something to say is
    indistinguishable from a sweep that did not run* (RA-30, DE-35).
    """

    code = "RES.SWEEP.SILENT"

    def __init__(self, week_ending) -> None:
        super().__init__(
            f"week ending {week_ending}: no sweep report — 'nothing accumulated' "
            f"is a result and must be emitted (RA-86)"
        )


# --------------------------------------------------------------------------- #
# B4.7 — the sector evidence file (§10C), and the four places a view hides
# --------------------------------------------------------------------------- #

class ConclusionFieldError(ResearchError):
    """RA-97 / AC-1.66 — a conclusion-shaped field in an evidence-only file.

    ★ *If one appears, the rejected macro-narrative option has returned under
    another name.* This is the **first** of §10C's four guards and the only one
    caught on sight — which is exactly why the other three exist.
    """

    code = "RES.SECTOR.CONCLUSION_FIELD"

    def __init__(self, path: str, field: str) -> None:
        super().__init__(
            f"{path}: field {field!r} is conclusion-shaped. ★ The sector file is "
            f"EVIDENCE ONLY — no outlook, view, implication, summary or "
            f"assessment (RA-97)"
        )


class SourceListIncompleteError(ResearchError):
    """RA-98 / AC-1.67 — a source-list item neither ingested nor logged.

    ⚠⚠ **Selection of evidence is itself a conclusion.** A file accumulating the
    capacity announcements someone found interesting **has a view, with no
    opinion field anywhere in it** — and curation is where the view hides.
    """

    code = "RES.SECTOR.INCOMPLETE"

    def __init__(self, missing, source_list_version: str) -> None:
        super().__init__(
            f"{sorted(missing)!r} appear in {source_list_version} but neither "
            f"produced a record nor a logged omission. An omission with no "
            f"reason is the defect; completeness is measured, not assumed (RA-98)"
        )


class SchemaDriftError(ResearchError):
    """RA-100 / AC-1.69 — the field set changed without a version bump.

    ⚠⚠ **The hardest of the four to see, because a schema change looks like
    maintenance.** ★ A new column is an analytical change: it declares what
    someone decided was worth recording, and that is a view in the schema.
    """

    code = "RES.SECTOR.SCHEMA_DRIFT"

    def __init__(self, version: str, declared: str, actual: str) -> None:
        super().__init__(
            f"schema {version!r} declares fingerprint {declared[:19]}… but the "
            f"file's field set fingerprints {actual[:19]}…. A new column takes a "
            f"version bump (RA-100, RA-140)"
        )


class CapacityRowMutatedError(ResearchError):
    """RA-101 / AC-1.70 — a capacity row was overwritten rather than appended to.

    ★ **The transition history IS the finding.** An announcement that quietly
    never became capacity is invisible once the row is mutated (L0 INV-006).
    """

    code = "RES.SECTOR.ROW_MUTATED"

    def __init__(self, subject: str, detail: str) -> None:
        super().__init__(f"capacity row {subject!r}: {detail} (RA-101, INV-006)")


# --------------------------------------------------------------------------- #
# B4.8 — the relay (§4B): an external provider with a human as its transport
# --------------------------------------------------------------------------- #

class RelayContradictedError(ResearchError):
    """RA-118 / AC-1.76 — a relayed number disagrees with our own data.

    ⚠ **Not a difference of opinion.** A relayed report that contradicts what
    D-02/D-07 hold about a *fact* has failed the ingest — ★ *a number does not
    become trustworthy because a human carried it.*
    """

    code = "RES.RELAY.CONTRADICTED"

    def __init__(self, ticker: str, findings) -> None:
        detail = "; ".join(
            f"claim #{f.ordinal} {f.checked_against}: ours {f.ours!r} vs "
            f"theirs {f.theirs!r}" for f in findings) or "unspecified"
        super().__init__(f"{ticker}: {detail} (RA-118)")


class RelayNotFreshError(ResearchError):
    """RA-117 / AC-1.80 — the response came from a continued session.

    ★ **A chat box IS conversational state.** A follow-up makes the analysis
    path-dependent, which RA-12 forbids because it turns a stochastic answer
    into a **stubborn** one.
    """

    code = "RES.RELAY.NOT_FRESH"

    def __init__(self, ticker: str, session: str) -> None:
        super().__init__(
            f"{ticker}: session {session!r} — one prompt, one response, one "
            f"fresh session. Follow-ups are permitted for understanding and may "
            f"not be pasted back (RA-117, RA-12)"
        )


class RelayPartialError(ResearchError):
    """RA-125 / AC-1.80 — a truncated or refused response.

    ⚠ **There is no `partial`** (RA-64/GW-22). It must not be topped up by a
    follow-up (RA-117): re-run the whole prompt in a fresh session.
    """

    code = "RES.RELAY.PARTIAL"

    def __init__(self, ticker: str, reason: str) -> None:
        super().__init__(
            f"{ticker}: {reason}. Re-run the whole prompt in a fresh session — "
            f"never top up (RA-125, RA-117)"
        )


class RelayPromptUnattributedError(ResearchError):
    """RA-122 / AC-1.74 — the prompt was hand-edited or its blocks unrecorded.

    ⚠ A hand-edited prompt makes the artifact **unattributable** and silently
    breaks INV-9's alignment for that name.
    """

    code = "RES.RELAY.PROMPT_UNATTRIBUTED"

    def __init__(self, ticker: str, detail: str) -> None:
        super().__init__(f"{ticker}: {detail} (RA-122, MP-12, INV-9)")


class RelayStabilityClaimedError(ResearchError):
    """RA-115 / AC-1.78 — a relay report carrying a `verdict_stability`.

    ★★ **Impossible by construction: a single chat response has no
    distribution.** AC-1.8 requires the actionable pick to carry `k ≥ 3`, so the
    relay can inform, gate and populate the card — **it cannot be the one thing
    INV-6 lets you trade on.**
    """

    code = "RES.RELAY.STABILITY_CLAIMED"

    def __init__(self, ticker: str) -> None:
        super().__init__(
            f"{ticker}: a relay report claimed a verdict_stability. One chat "
            f"response has no distribution, so AC-1.8 cannot be satisfied and "
            f"this report can never be the actionable pick (RA-115)"
        )
