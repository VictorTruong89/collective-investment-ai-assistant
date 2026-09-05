"""D-01 Fundamental Analysis — qualitative, LLM-bearing. SEAT-2.

⚠ **B3 + B4.1 SLICE.** This package contains the `CT-1.4` gate contract, the B3
stub gate (BS-11), and **B4.1's reproducibility apparatus**: the evidence bundle,
its content hash, `CT-1.2 AnalysisRun`, the prompt registry with its alignment
gate, and the gateway seam. **B4.2** adds extraction and the citation spine: the E-block runner, `Claim`
with its evidence span, and the **deterministic** X-01/X-02 verifiers. **B4.3**
adds the scorecard — four versioned rubrics, criterion selection with derived
scores, `evidence_coverage` and the confidence floors. **B4.4** adds authoring
and **the real gate**: Stage A→D with the freeze, the falsifier commit, the bear
case, and §11.2's mapping — ★ **the B3 stub is superseded**. **B4.5** adds the
monitors: RM-1's **perturbation** probe (the only one available on this tier),
the weekly bias set, the calibration monitors, RM-4's release gate, and
`CT-1.3` — where **every `RM-n` appears** as a value or an explicit decline.
Invalidation (B4.6), the sector file (B4.7) and the relay (B4.8) are **not
built** — L3 §3A.

★★ **B4.5 is what BS-28 was waiting for.** A verdict may not reach a human as
actionable before RA-20/RA-21's fields exist; `rm1_perturbation_probe` supplies
`verdict_stability` and RA-30/RA-136 supply the honest `not_yet_calibrated` /
`not_measurable` forms of the rest.

★ **D-01 is the only domain permitted to import the LLM gateway** (ST-5, AP-5),
and within D-01 exactly one file does: `prompts/call.py`. That is narrower than
ST-5 requires, so the same rule is checkable by reading one file.

★★ **B4.1 ships the whole reproducibility apparatus BEFORE the first judgement
exists** (L3 **BS-25**) — which is what makes it look skippable. ⚠ *Without it,
§7's entire measurement programme has nothing to key on, and every judgement
built before it is unattributable after the fact.*
"""

from src.fundamental.bundle.assemble import (
    assemble, computed, filing, news, prior_thesis, profile, sector_file,
)
from src.fundamental.bundle.models import (
    BLIND_WITHHELD_KINDS, BundlePart, EvidenceBundle, PIN_FIELDS,
)
from src.fundamental.claims.models import (
    ASSUMPTION, Claim, ClaimSet, EvidenceSpan, FACT, INFERENCE, KINDS,
)
from src.fundamental.claims.verify import (
    VerificationReport, x01_verify_extraction, x02_verify_claims,
)
from src.fundamental.contracts.analysis_run import (
    AnalysisRun, AnalysisRunLog, FAILING_OUTCOMES, OK, OUTCOMES,
)
#: ⚠ `STATUSES` is defined in THREE D-01 modules with three different
#: tuples — the gate's, the extraction envelope's and the monitor
#: registry's. A flat re-export makes the last import win silently, so
#: the gate's is exported under its own name. See B4.6's collision test.
from src.fundamental.contracts.gate import (
    FLAG, GateVerdict, Grade, NO_THESIS, PASS, SCORECARD_DIMENSIONS,
    STATUSES as GATE_STATUSES, VETO,
)
from src.fundamental.errors import (
    BundleInconsistentError, BundleNotPinnedError, ConversationalStateError,
    BearCaseNotSeparateError, DegradedCallError, ExtractionKindError,
    FalsifierEditedError, GateMappingError, LevelUnavailableError, NoFalsifierError,
    NullBearCaseError, PriorVerdictLeakError, PromptDriftError, ResearchError,
    BriefMutatedError, BriefPredictsError, CalendarCitedAsFactError,
    EvidenceWithdrawnError, MoveRationalisedError, MoveUndecomposedError,
    SweepSilentError,
    CapacityRowMutatedError, ConclusionFieldError, SchemaDriftError,
    SourceListIncompleteError,
    RelayContradictedError, RelayNotFreshError, RelayPartialError,
    RelayPromptUnattributedError, RelayStabilityClaimedError,
    RubricMutatedError, ScoreEmittedError, SelfReportedConfidenceError,
    SpanMismatchError, SpanUnresolvableError, UncheckableFalsifierError,
    UncitedClaimError, UncommittedFalsifiersError, ValueNotInSpanError,
    VerdictNotEnumError,
)
from src.fundamental.calendar.models import (
    BOOK_LEVEL_CLASSES, CLEARS, CONFIRMED, CalendarEvent, ESTIMATED, FIRES,
    OutcomeMapping, PreEventBrief, SCOPE_BOOK, SCOPE_TICKER, StalenessState,
    UNDETERMINED, assert_not_cited_as_fact,
)
from src.fundamental.calendar.pre_event import (
    PREDICTION_MARKERS, assert_unedited, brief_targets, pre_event_brief,
)
from src.fundamental.calendar.staleness import (
    PRE_EVENT_WINDOW_DAYS, STALENESS_FILINGS_HOURS, depended_classes, staleness,
)
from src.fundamental.events.moves import (
    BASIS_RAW, BASIS_RESIDUAL, ClusterDiagnostic, EXPLAINED, MoveDecomposition,
    MoveReview, MoveTrigger, UNEXPLAINED, cluster_check, review_move,
)
from src.fundamental.events.router import (
    ESCALATE, ITEM_ROUTES, POST_EVENT, Route, Routing, TRIAGE, WITHDRAW,
    assert_scorecard_re_derived, route_filing, withdraw_extractions,
)
from src.fundamental.events.sweep import (
    ACCUMULATION_KINDS, Accumulation, SweepReport, actionable_recommendations,
    assert_sweep_emitted, weekly_sweep,
)
from src.fundamental.events.vintage import (
    ALFRED_COVERED, GRADE_UNCHECKED, NO_VINTAGE_SERVICE_NEEDED, PeerContext,
    REVISED_SERIES, SeriesComparison, VINTAGE_CHECKED, grade_comparison,
)
from src.fundamental.relay.compose import (
    ARCHETYPES, ARCHETYPE_BLOCKS, BASE_BLOCKS, RelayPrompt,
    assert_prompt_attributed, blocks_for, compose,
)
from src.fundamental.relay.ingest import (
    REFUSAL_MARKERS, TRUNCATION_MARKERS, assert_fresh, assert_whole,
    confidence_of, verify_claim,
)
from src.fundamental.relay.ingest import ingest as ingest_relay
from src.fundamental.relay.models import (
    CONTRADICTED, PROVENANCE_RELAYED, RelayEnvelope, RelayReport, SESSION_FRESH,
    UNVERIFIABLE, VERIFIED, ClaimVerification, VerificationResult,
)
from src.fundamental.relay.queue import (
    OVERRIDE_REASONS, QueueEntry, QueueReport, ROTATION, derive_queue,
    relay_staleness,
)
from src.fundamental.sector.ingest import declared_on
from src.fundamental.sector.ingest import ingest as ingest_sector
from src.fundamental.sector.models import (
    CAPACITY_STATUSES, CONCLUSION_FIELDS, CapacityRow, KIND_CAPACITY, Omission,
    SectorFile, SectorRecord, Source, SourceList, append_transition,
    assert_complete, assert_no_conclusion_fields,
)
from src.fundamental.sector.schema import (
    OMISSION_FIELDS_V1, RECORD_FIELDS_V1, SCHEMAS, SCHEMA_V1, SectorSchema,
    assert_schema_current, fingerprint_of, schema_for,
)
from src.fundamental.invalidation.check import check_invalidation, new_evidence_only
from src.fundamental.invalidation.models import (
    InvalidationCheck, InvalidationEvent, NewEvidenceItem, TIER_CHEAP, TIER_DEEP,
    Triage, assert_no_verdict,
)
from src.fundamental.invalidation.news import CHEAP_TIER_ITEMS, cheap_tier_queue
from src.fundamental.monitor.base_rates import (
    rm6_verdict_base_rate, rm7_dimension_dispersion, rm8_seat_disagreement,
    rm9_theme_skew,
)
from src.fundamental.monitor.calibration import (
    rm12_calibration_curve, rm13_falsifier_vs_abandonment, rm14_action_correlation,
    rm15_lint_and_uncited, rm16_thesis_error_correlation,
)
from src.fundamental.monitor.lint import (
    FORECAST_VOICE, LENGTH_CAPS, LintFinding, forecast_voice_violations,
    length_violations,
)
from src.fundamental.monitor.regression import (
    Baseline, RegressionResult, rm4_regression, rm4_result, rm5_rebaseline_required,
)
from src.fundamental.monitor.registry import (
    CADENCE, FAIL, MonitorReport, MonitorResult, NOT_MEASURABLE, NOT_YET_CALIBRATED,
    OK, RM_IDS, WARN, not_measurable, not_yet_calibrated,
)
from src.fundamental.monitor.variance import (
    K_STAB, PERTURBATION, PERTURBATIONS, SAMPLING, StabilityResult,
    rm1_perturbation_probe, rm1_result, rm1_sampling_probe, rm2_scorecard_dispersion,
    rm3_numeric_spread,
)
from src.fundamental.thesis.author import (
    AuthoringRun, BEAR_OVERLAP_CAP, CommitLog, FalsifierCommit, STAGE_A, STAGE_B,
    STAGE_C, STAGE_D, STAGE_BLOCKS, STAGE_VIEW, StageCommit,
    assert_bear_case_separate, assert_fresh_authoring_bundle, assert_stage_view,
    bear_case_overlap, commit_falsifiers, supersede,
)
from src.fundamental.thesis.gate import (
    FLAG_FLOOR, GateInputs, VETO_FLOOR, evaluate,
)
from src.fundamental.thesis.models import (
    BUY, CONVICTIONS, HOLD, INSUFFICIENT_DATA, MAX_FALSIFIERS, MIN_FALSIFIERS,
    SELL, BearCase, Falsifier, Thesis, VERDICTS,
)
from src.fundamental.scorecard.coverage import (
    CONFIDENCE_FLOOR, CONFIDENCE_HOLD_CAP, ConfidenceAssessment, CoverageReport,
    DimensionCoverage, HOLD_CAPPED, INSUFFICIENT_DATA, UNCAPPED, assess_confidence,
    coverage_report, dimension_coverage, reject_self_reported,
)
from src.fundamental.scorecard.models import (
    DIMENSIONS, MAX_SCORE, MIN_SCORE, Rubric, RubricLevel,
)
from src.fundamental.scorecard.registry import RubricRegistry
from src.fundamental.scorecard.rubrics.b43_v1 import B43_RUBRICS
from src.fundamental.scorecard.score import (
    DimensionScore, ScorecardResult, Selection, build_scorecard, derive_score,
)
from src.fundamental.filings.extract import (
    CHEAP_E_BLOCKS, E_BLOCK_IDS, ExtractionPass, assert_extraction_block, item,
    not_found, run_extraction,
)
from src.fundamental.filings.models import (
    CUMULATIVE_YTD, ExtractedItem, ExtractionResult, FOUND, NOT_FOUND, Period,
)
from src.fundamental.prompts.call import CallResult, MAX_TOKENS, TIER, AnalysisGateway
from src.fundamental.prompts.registry import (
    AlignmentCheck, PromptBlock, PromptRegistry, block, content_hash,
)
from src.fundamental.thesis.stub_gate import (
    GATE_ID, REPLACED_AT, STUB_REASON, stub_gate_verdict,
)

__all__ = [
    # the gate (B3)
    "FLAG", "GATE_ID", "GateVerdict", "Grade", "NO_THESIS", "PASS", "REPLACED_AT",
    "GATE_STATUSES", "SCORECARD_DIMENSIONS", "STUB_REASON", "VETO", "stub_gate_verdict",
    # the bundle (B4.1)
    "BLIND_WITHHELD_KINDS", "BundlePart", "EvidenceBundle", "PIN_FIELDS", "assemble",
    "computed", "filing", "news", "prior_thesis", "profile",
    # the record
    "AnalysisRun", "AnalysisRunLog", "FAILING_OUTCOMES", "OK", "OUTCOMES",
    # prompts and the seam
    "AlignmentCheck", "AnalysisGateway", "CallResult", "MAX_TOKENS", "PromptBlock",
    "PromptRegistry", "TIER", "block", "content_hash",
    # the citation spine (B4.2)
    "ASSUMPTION", "CUMULATIVE_YTD", "CHEAP_E_BLOCKS", "Claim", "ClaimSet",
    "E_BLOCK_IDS", "EvidenceSpan", "ExtractedItem", "ExtractionPass",
    "ExtractionResult", "FACT", "FOUND", "INFERENCE", "KINDS", "NOT_FOUND", "Period",
    "VerificationReport", "assert_extraction_block", "item", "not_found",
    "run_extraction", "x01_verify_extraction", "x02_verify_claims",
    # errors
    "BundleInconsistentError", "BundleNotPinnedError", "ConversationalStateError",
    "DegradedCallError", "ExtractionKindError", "GateMappingError", "PromptDriftError",
    "ResearchError", "SpanMismatchError", "SpanUnresolvableError",
    "UncitedClaimError", "ValueNotInSpanError",
    # the scorecard (B4.3)
    "B43_RUBRICS", "CONFIDENCE_FLOOR", "CONFIDENCE_HOLD_CAP", "ConfidenceAssessment",
    "CoverageReport", "DIMENSIONS", "DimensionCoverage", "DimensionScore",
    "HOLD_CAPPED", "INSUFFICIENT_DATA", "MAX_SCORE", "MIN_SCORE", "Rubric",
    "RubricLevel", "RubricRegistry", "ScorecardResult", "Selection", "UNCAPPED",
    "assess_confidence", "build_scorecard", "coverage_report", "derive_score",
    "dimension_coverage", "reject_self_reported",
    "LevelUnavailableError", "RubricMutatedError", "ScoreEmittedError",
    "SelfReportedConfidenceError",
    # authoring and the real gate (B4.4)
    "AuthoringRun", "BEAR_OVERLAP_CAP", "BUY", "BearCase", "CONVICTIONS", "CommitLog",
    "FLAG_FLOOR", "Falsifier", "FalsifierCommit", "GateInputs", "HOLD",
    "INSUFFICIENT_DATA", "MAX_FALSIFIERS", "MIN_FALSIFIERS", "SELL", "STAGE_A",
    "STAGE_B", "STAGE_BLOCKS", "STAGE_C", "STAGE_D", "STAGE_VIEW", "StageCommit",
    "Thesis", "VERDICTS", "VETO_FLOOR", "assert_bear_case_separate",
    "assert_fresh_authoring_bundle", "assert_stage_view", "bear_case_overlap",
    "commit_falsifiers", "evaluate", "supersede",
    "BearCaseNotSeparateError", "FalsifierEditedError", "NoFalsifierError",
    "NullBearCaseError", "PriorVerdictLeakError", "UncheckableFalsifierError",
    "UncommittedFalsifiersError", "VerdictNotEnumError",
    # the monitors (B4.5)
    "Baseline", "CADENCE", "FAIL", "FORECAST_VOICE", "K_STAB", "LENGTH_CAPS",
    "LintFinding", "MonitorReport", "MonitorResult", "NOT_MEASURABLE",
    "NOT_YET_CALIBRATED", "OK", "PERTURBATION", "PERTURBATIONS", "RM_IDS",
    "RegressionResult", "SAMPLING", "StabilityResult", "WARN",
    "forecast_voice_violations", "length_violations", "not_measurable",
    "not_yet_calibrated", "rm1_perturbation_probe", "rm1_result",
    "rm1_sampling_probe", "rm2_scorecard_dispersion", "rm3_numeric_spread",
    "rm4_regression", "rm4_result", "rm5_rebaseline_required",
    "rm6_verdict_base_rate", "rm7_dimension_dispersion", "rm8_seat_disagreement",
    "rm9_theme_skew", "rm12_calibration_curve", "rm13_falsifier_vs_abandonment",
    "rm14_action_correlation", "rm15_lint_and_uncited",
    "rm16_thesis_error_correlation",
    # the calendar, invalidation and events (B4.6)
    "ALFRED_COVERED", "Accumulation", "BASIS_RAW", "BASIS_RESIDUAL",
    "BOOK_LEVEL_CLASSES", "CHEAP_TIER_ITEMS", "CLEARS", "CONFIRMED",
    "ACCUMULATION_KINDS", "CalendarEvent", "ClusterDiagnostic", "ESCALATE", "ESTIMATED",
    "EXPLAINED",
    "FIRES", "GRADE_UNCHECKED", "ITEM_ROUTES", "InvalidationCheck",
    "InvalidationEvent", "MoveDecomposition", "MoveReview", "MoveTrigger",
    "NO_VINTAGE_SERVICE_NEEDED", "NewEvidenceItem", "OutcomeMapping", "PeerContext",
    "POST_EVENT", "PREDICTION_MARKERS", "PRE_EVENT_WINDOW_DAYS", "PreEventBrief",
    "REVISED_SERIES", "Route", "Routing", "SCOPE_BOOK", "SCOPE_TICKER",
    "STALENESS_FILINGS_HOURS", "SeriesComparison", "StalenessState", "SweepReport",
    "TIER_CHEAP", "TIER_DEEP", "TRIAGE", "Triage", "UNDETERMINED", "UNEXPLAINED",
    "VINTAGE_CHECKED", "WITHDRAW", "actionable_recommendations", "assert_no_verdict",
    "assert_not_cited_as_fact", "assert_scorecard_re_derived", "assert_sweep_emitted",
    "assert_unedited", "brief_targets", "check_invalidation", "cheap_tier_queue",
    "cluster_check", "depended_classes", "grade_comparison", "new_evidence_only",
    "pre_event_brief", "review_move", "route_filing", "staleness", "weekly_sweep",
    "withdraw_extractions",
    # the relay (B4.8)
    "ARCHETYPES", "ARCHETYPE_BLOCKS", "BASE_BLOCKS", "CONTRADICTED",
    "ClaimVerification", "OVERRIDE_REASONS", "PROVENANCE_RELAYED",
    "REFUSAL_MARKERS", "ROTATION", "QueueEntry", "QueueReport", "RelayEnvelope",
    "RelayPrompt", "RelayReport", "SESSION_FRESH", "TRUNCATION_MARKERS",
    "UNVERIFIABLE", "VERIFIED", "VerificationResult", "assert_fresh",
    "assert_prompt_attributed", "assert_whole", "blocks_for", "compose",
    "confidence_of", "derive_queue", "ingest_relay", "relay_staleness",
    "verify_claim",
    "RelayContradictedError", "RelayNotFreshError", "RelayPartialError",
    "RelayPromptUnattributedError", "RelayStabilityClaimedError",
    # the sector evidence file (B4.7)
    "CAPACITY_STATUSES", "CONCLUSION_FIELDS", "CapacityRow", "KIND_CAPACITY",
    "OMISSION_FIELDS_V1", "Omission", "RECORD_FIELDS_V1", "SCHEMAS", "SCHEMA_V1",
    "SectorFile", "SectorRecord", "SectorSchema", "Source", "SourceList",
    "append_transition", "assert_complete", "assert_no_conclusion_fields",
    "assert_schema_current", "declared_on", "fingerprint_of", "ingest_sector",
    "schema_for", "sector_file",
    "CapacityRowMutatedError", "ConclusionFieldError", "SchemaDriftError",
    "SourceListIncompleteError",
    "BriefMutatedError", "BriefPredictsError", "CalendarCitedAsFactError",
    "EvidenceWithdrawnError", "MoveRationalisedError", "MoveUndecomposedError",
    "SweepSilentError",
]
