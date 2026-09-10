"""F3 — corporate-action resolution. `MS-6.1`."""

from __future__ import annotations

import pytest

from src.data_engine.corporate_actions.classify import (
    SearchNotRun,
    classify,
    corroboration_of,
)
from src.data_engine.corporate_actions.models import (
    MAX_RESOLUTION_ATTEMPTS,
    Evidence,
    Finding,
)

E1 = Evidence("https://sec.gov/x", "completed the merger on 2026-06-01")
E2 = Evidence("https://reuters.com/y", "deal closed June 1")


def _search(items):
    return lambda t: items


def _interpret(**kw):
    return lambda t, s: {"outcome": "acquisition", **kw}


def test_ac_3_1_no_evidence_yields_undetermined_never_a_guess():
    """⚠⚠ PG-3 — the answer is on the internet. An answer that did not come from
    there is not what this agent exists to produce."""
    (f,) = classify("XYZ", search=_search([]), interpret=_interpret())
    assert f.outcome == "undetermined" and f.sources == ()


def test_ac_3_2_a_single_source_downgrades_to_undetermined():
    """AC-3.2 — one source is a lead, not a finding."""
    (f,) = classify("XYZ", search=_search([E1]), interpret=_interpret())
    assert f.outcome == "undetermined"
    assert f.confidence == "single_source", "⚠ the lead is kept, not discarded"


def test_ac_3_2_two_independent_sources_corroborate():
    (f,) = classify("XYZ", search=_search([E1, E2]), interpret=_interpret())
    assert f.outcome == "acquisition" and f.confidence == "corroborated"


def test_ac_3_2_two_snippets_from_ONE_url_are_not_corroboration():
    """⚠ Independence is about the SOURCE, not the number of quotations."""
    same = [E1, Evidence(E1.url, "a second sentence from the same page")]
    assert corroboration_of(same) == "single_source"


def test_ac_3_8_a_classified_finding_without_sources_cannot_be_built():
    with pytest.raises(ValueError, match="is a guess"):
        Finding(ticker="XYZ", outcome="acquisition", confidence="corroborated")


def test_ac_3_2_corroborated_requires_two_distinct_urls():
    with pytest.raises(ValueError, match="two INDEPENDENT sources"):
        Finding(ticker="XYZ", outcome="acquisition", confidence="corroborated",
                sources=(E1,))


def test_ac_3_3_a_merger_of_equals_yields_two_findings_one_per_side():
    """★ AC-3.3 — both sides are recorded; the retired one is marked."""
    out = classify("AAA", search=_search([E1, E2]),
                   interpret=lambda t, s: {"outcome": "merger_of_equals",
                                           "other_side": "BBB",
                                           "successor_symbol": "CCC",
                                           "contaminated_from": "2026-06-01"})
    assert len(out) == 2
    assert {f.ticker for f in out} == {"AAA", "BBB"}
    assert [f.retired_side for f in out] == [False, True]


def test_ac_3_12_contamination_is_RECORDED_never_spliced():
    """⚠ AC-3.12 — the finding says the series is another company's from a date.
    It does not repair the series; that is not F3's to decide (D4)."""
    out = classify("AAA", search=_search([E1, E2]),
                   interpret=lambda t, s: {"outcome": "merger_of_equals",
                                           "other_side": "BBB",
                                           "contaminated_from": "2026-06-01"})
    retired = [f for f in out if f.retired_side][0]
    assert retired.series_contaminated_from == "2026-06-01"
    assert not hasattr(retired, "repaired_series")


def test_ac_3_5_a_rename_is_never_reported_as_a_delisting():
    """★ AC-3.5 — ⚠ calling a rename a delisting deletes a live holding."""
    (f,) = classify("OLD", search=_search([E1, E2]), vendor_claim="delisted",
                    interpret=lambda t, s: {"outcome": "ticker_change",
                                            "successor_symbol": "NEW"})
    assert f.outcome == "ticker_change" and f.successor_symbol == "NEW"


def test_ac_3_9_the_vendor_claim_is_evidence_not_verdict():
    """AC-3.9 — the search decides; the vendor's event is one input."""
    (f,) = classify("OLD", search=_search([E1, E2]), vendor_claim="delisted",
                    interpret=lambda t, s: {"outcome": "ticker_change"})
    assert f.outcome != "bankruptcy"


def test_ac_3_6_an_interpreter_that_concludes_nothing_raises():
    """P5 — a classifier that cannot say what it concluded has not concluded."""
    with pytest.raises(SearchNotRun):
        classify("XYZ", search=_search([E1, E2]),
                 interpret=lambda t, s: {"outcome": None})


def test_ac_3_7_silence_duration_proves_nothing():
    """AC-3.7 — 3 days and 5 months of silence are the same evidence: none."""
    a = classify("A", search=_search([]), interpret=_interpret())[0]
    b = classify("B", search=_search([]), interpret=_interpret())[0]
    assert a.outcome == b.outcome == "undetermined"


def test_d5_undetermined_retries_then_becomes_permanently_unchecked():
    """D5 — ⚠ DE-72 treats `permanently_unchecked` as EXEMPT, not overdue:
    reporting an unresolvable class daily trains a reader to ignore the report."""
    early = classify("XYZ", search=_search([]), interpret=_interpret(), attempts=1)[0]
    assert early.state == "retry_due" and not early.is_terminal
    late = classify("XYZ", search=_search([]), interpret=_interpret(),
                    attempts=MAX_RESOLUTION_ATTEMPTS)[0]
    assert late.state == "permanently_unchecked" and late.is_terminal


def test_d4_a_finding_carries_no_action():
    """D4 — F3 writes the finding; the universe rule consumes it. ⚠ An agent
    that acts is one whose mistakes are executed."""
    (f,) = classify("XYZ", search=_search([E1, E2]), interpret=_interpret())
    for forbidden in ("remove", "drop_from_universe", "apply", "execute"):
        assert not hasattr(f, forbidden)


def test_ac_3_11_provenance_and_trace_ref_travel_with_the_finding():
    (f,) = classify("XYZ", search=_search([E1, E2]),
                    interpret=_interpret(provenance={"variant": "search_v1"},
                                         trace_ref="job:corp_actions"))
    assert f.provenance == {"variant": "search_v1"}
    assert f.trace_ref == "job:corp_actions"


def test_ac_3_4_contamination_is_detected_and_dated_on_the_retired_side():
    """`AC-3.4` — ⚠⚠ *contamination is detected*, and the DATE is the finding.

    ★★★ Why this AC is the sharpest in `F3`. A retired symbol whose closes
    match its successor's after the effective date is a series that **silently
    becomes another company's price history**. ⚠ Nothing about it looks wrong:
    the ticker is the same, the series is continuous, and every downstream
    computation — returns, volatility, the ranker's features — runs happily on
    a company that stopped existing.

    ★ `D4` is why it is only RECORDED: repairing the series is an investment
    judgement about which company the history belongs to, and `F3` refuses to
    make it. The finding names the first matching date so the decision is
    someone's, explicitly.

    ⚠ This AC had **no test** until 2026-09-09, found while filling `F3`'s
    traceability table — which said *"(to be written)"* on all twelve rows.
    """
    out = classify("AAA", search=_search([E1, E2]),
                   interpret=lambda t, s: {"outcome": "merger_of_equals",
                                           "other_side": "BBB",
                                           "successor_symbol": "CCC",
                                           "contaminated_from": "2026-06-01"})
    retired = next(f for f in out if f.retired_side)
    assert retired.series_contaminated_from == "2026-06-01"
    surviving = next(f for f in out if not f.retired_side)
    assert surviving.series_contaminated_from is None, (
        "only the RETIRED side's series is contaminated — the survivor's own "
        "history is still its own")


def test_ac_3_4_an_uncontaminated_finding_says_so_with_None_not_a_guess():
    """⚠ `P5` — absence is explicit. ★ A default date would assert a
    contamination nobody detected, which is worse than missing one."""
    (f,) = classify("XYZ", search=_search([E1, E2]),
                    interpret=lambda t, s: {"outcome": "ticker_change",
                                            "successor_symbol": "ZZZ"})
    assert f.series_contaminated_from is None
