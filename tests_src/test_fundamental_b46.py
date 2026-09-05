"""D-01 B4.6 — AC-1.35–1.37, 1.41–1.58, 1.60, 1.61, 1.65.

★ **L3 §3A.4's done-when:** *an 8-K item 4.02 drives `evidence_coverage` to zero
for the affected periods; a move trigger without a residual raises; the weekly
sweep emits a report on a week when nothing happened.*

⚠ **RA-88 is this slice's non-obvious ordering**: the residual is computed
*before* the move trigger fires, or the trigger measures the sector.

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, timedelta, timezone

import pytest

from src.fundamental import (
    ALFRED_COVERED, Accumulation, AuthoringRun, BASIS_RAW, BUY, BearCase,
    BriefMutatedError, BriefPredictsError, CONFIRMED, CalendarCitedAsFactError,
    CalendarEvent, Claim, ESTIMATED, EXPLAINED, EvidenceSpan,
    EvidenceWithdrawnError, Falsifier, INSUFFICIENT_DATA, MoveDecomposition,
    MoveRationalisedError,
    MoveReview, MoveTrigger, MoveUndecomposedError, NewEvidenceItem,
    OutcomeMapping, PRE_EVENT_WINDOW_DAYS, PeerContext, ResearchError,
    SCOPE_BOOK, SeriesComparison, SweepSilentError, TIER_CHEAP, Triage,
    UNEXPLAINED, actionable_recommendations, assemble, assert_no_verdict,
    assert_not_cited_as_fact, assert_scorecard_re_derived, assert_sweep_emitted,
    assert_unedited, brief_targets, check_invalidation, cheap_tier_queue,
    cluster_check, computed, filing, grade_comparison, pre_event_brief, profile,
    review_move, route_filing, staleness, weekly_sweep, withdraw_extractions,
)
from src.fundamental.filings.models import ExtractedItem, ExtractionResult, Period

AS_OF = date(2026, 8, 23)
DEADLINE = date(2027, 3, 31)
UTC = timezone.utc


def utc(y, m, d, h=12):
    return datetime(y, m, d, h, tzinfo=UTC)


def bundle():
    return assemble(ticker="MU", as_of=AS_OF,
                    parts=[filing("0000-1", "Gross margin was 55.4%."),
                           computed("b3_minimal", 1, "fair_value_band=[380,445]"),
                           profile(AS_OF, "Sector: IT")])


def falsifier(ordinal=1, **kw):
    base = dict(condition="Gross margin below 55% in two consecutive quarters.",
                observable_field="f_gross_margin", source="D-02", deadline=DEADLINE,
                materiality="The pricing-power premise fails.", about_business=True)
    return Falsifier(ordinal=ordinal, **{**base, **kw})


def thesis(**kw):
    run = AuthoringRun(ticker="MU", as_of=kw.pop("as_of", AS_OF))
    base = dict(bundle=bundle(), stage_a_payload={"moat_durability": 3},
                falsifiers=(falsifier(1), falsifier(2, observable_field="f_net_debt")),
                verdict=BUY, conviction="Medium-High",
                bear_case=BearCase(text="Capacity additions crush pricing by FY2028.",
                                   falsification_condition="Utilisation above 90%.",
                                   prompt_version="J-11@v1", run_id="call-bear"),
                scorecard={"moat_durability": 3},
                confidence={"value": 0.62, "basis": "evidence_coverage"},
                bull_run_ids=("call-bull",), run_id="run-1")
    return run.author(**{**base, **kw})


def earnings(day, status=CONFIRMED, ticker="MU"):
    return CalendarEvent(event_class="earnings", scheduled_date=day,
                         knowable_at=utc(2026, 7, 1), date_status=status,
                         ticker=ticker, entry_ref=f"cal:{ticker}:{day}")


# --------------------------------------------------------------------------- #
# §10 — invalidation. AC-1.35, 1.36, 1.37
# --------------------------------------------------------------------------- #

def test_ac_1_35_the_check_reads_only_evidence_newer_than_the_thesis():
    """AC-1.35 / RA-40 — re-reading old evidence produces drift, not information."""
    seen = []
    old = NewEvidenceItem("filing", "acc-old", utc(2026, 8, 1))
    new = NewEvidenceItem("filing", "acc-new", utc(2026, 8, 30))

    def triage(_t, item):
        seen.append(item.ref)
        return Triage(flagged=False)

    check = check_invalidation(thesis(), [old, new], triage=triage, as_of=date(2026, 9, 1))
    assert seen == ["acc-new"]
    assert check.skipped_already_known == ("acc-old",)


def test_ac_1_36_a_fired_falsifier_emits_an_event_never_a_verdict():
    """AC-1.36 / RA-41 — D-01 reports the condition occurred; SEAT-1 decides."""
    item = NewEvidenceItem("filing", "acc-new", utc(2026, 8, 30))
    check = check_invalidation(
        thesis(), [item], as_of=date(2026, 9, 1),
        triage=lambda _t, _i: Triage(flagged=True, falsifier_ordinal=1,
                                     rationale="margin printed 53.1%"))
    (event,) = check.events
    assert event.falsifier_ordinal == 1 and event.tier == TIER_CHEAP
    assert not hasattr(event, "verdict")
    assert_no_verdict(event.to_json_obj(), where="InvalidationEvent")


def test_a_flagged_falsifier_the_thesis_never_stated_raises():
    """RA-35/RA-41 — a condition never written cannot have fired."""
    item = NewEvidenceItem("news", "url-1", utc(2026, 8, 30))
    with pytest.raises(ResearchError, match="does not state"):
        check_invalidation(thesis(), [item], as_of=date(2026, 9, 1),
                           triage=lambda _t, _i: Triage(flagged=True,
                                                        falsifier_ordinal=9))


def test_ac_1_37_a_thesis_past_the_clock_floor_is_stale():
    """AC-1.37 / RA-43 — the floor survives for names with no events in the window."""
    state = staleness(thesis(), date(2026, 8, 27),
                      last_check_at=utc(2026, 8, 23))
    assert state.stale and state.basis == "clock"
    assert "48h" in state.reason


def test_a_recent_check_with_no_events_is_not_stale():
    """The floor is a floor, not a default — RA-43 read with RA-71."""
    state = staleness(thesis(), date(2026, 8, 24), last_check_at=utc(2026, 8, 24, 6))
    assert not state.stale and state.basis == "fresh"


# --------------------------------------------------------------------------- #
# §10A — the scheduled calendar. AC-1.41…1.48
# --------------------------------------------------------------------------- #

def test_ac_1_41_a_claim_citing_a_scheduled_event_as_a_fact_raises():
    """AC-1.41 / RA-69 — *"earnings are on the 24th"* is not a reason for anything."""
    event = earnings(date(2026, 9, 24))
    claim = Claim(ordinal=1, kind="fact", text="Earnings land on the 24th.",
                  span=EvidenceSpan(accession_id=event.entry_ref, start=0, end=5),
                  quote="Earn")
    with pytest.raises(CalendarCitedAsFactError):
        assert_not_cited_as_fact(claim, [event.entry_ref])


def test_only_a_fact_or_inference_can_reach_the_calendar_guard_at_all():
    """RA-69 read with S-3 — two independent rules close the same hole.

    ★ An `assumption` cannot carry a span in the first place (*"something the
    bundle does not contain"*), so it has no way to cite a `CalendarEntry`. The
    guard therefore only ever sees `fact` and `inference`.
    """
    event = earnings(date(2026, 9, 24))
    with pytest.raises(ValueError, match="carries a span"):
        Claim(ordinal=1, kind="assumption", text="Results land before quarter-end.",
              span=EvidenceSpan(accession_id=event.entry_ref, start=0, end=5),
              quote="Resu")
    unrelated = Claim(ordinal=1, kind="fact", text="Gross margin was 55.4%.",
                      span=EvidenceSpan(accession_id="0000-1", start=0, end=23),
                      quote="Gross margin was 55.4%.")
    assert_not_cited_as_fact(unrelated, [event.entry_ref])


def test_ac_1_42_confirmed_and_estimated_dates_are_distinguishable_and_render_apart():
    """AC-1.42 / RA-70 — 34.6 % of calendar rows are future-dated, and most are guesses."""
    confirmed = earnings(date(2026, 9, 24), CONFIRMED)
    estimated = earnings(date(2026, 9, 24), ESTIMATED)
    assert confirmed.is_confirmed and not estimated.is_confirmed
    assert confirmed.render_date() == "2026-09-24"
    assert estimated.render_date() == "~2026-09-24 (estimated)"
    assert confirmed.to_json_obj()["date_status"] != estimated.to_json_obj()["date_status"]


def test_an_unknown_date_status_raises():
    """RA-70 — there is no third kind of date."""
    with pytest.raises(ValueError, match="RA-70"):
        CalendarEvent(event_class="earnings", scheduled_date=date(2026, 9, 24),
                      knowable_at=utc(2026, 7, 1), date_status="probably", ticker="MU")


def test_ac_1_43_an_occurred_unread_event_is_stale_inside_the_clock_threshold():
    """AC-1.43 / RA-71 — event-relative first. The clock says fresh; the event does not."""
    event = earnings(date(2026, 8, 25))
    state = staleness(thesis(), date(2026, 8, 26), events=[event],
                      last_check_at=utc(2026, 8, 24, 18))
    assert state.stale and state.basis == "event"
    assert state.driving_event is event
    # ⚠ the clock alone would have called this fresh — 24h against a 48h floor.
    assert not staleness(thesis(), date(2026, 8, 26),
                         last_check_at=utc(2026, 8, 24, 18)).stale


def test_an_occurred_event_that_has_been_read_is_not_stale():
    """RA-71 — *occurred* is not the test; *occurred and unread* is."""
    event = earnings(date(2026, 8, 25))
    state = staleness(thesis(), date(2026, 8, 26), events=[event],
                      last_check_at=utc(2026, 8, 25, 23))
    assert not state.stale


def test_ac_1_44_a_thesis_written_inside_the_window_is_marked_pre_event():
    """AC-1.44 / RA-72/RA-139 — provisional, not stale, with the date on the card."""
    event = earnings(AS_OF + timedelta(days=4))
    state = staleness(thesis(), AS_OF, events=[event], last_check_at=utc(2026, 8, 23))
    assert state.pre_event and not state.stale
    assert state.pre_event_date == event.scheduled_date
    assert state.to_json_obj()["pre_event_date"] == event.scheduled_date.isoformat()


def test_the_pre_event_window_has_an_edge_and_it_is_ten_days():
    """RA-139 — a window wide enough to be always-on marks nothing."""
    inside = earnings(AS_OF + timedelta(days=PRE_EVENT_WINDOW_DAYS))
    outside = earnings(AS_OF + timedelta(days=PRE_EVENT_WINDOW_DAYS + 1))
    assert staleness(thesis(), AS_OF, events=[inside]).pre_event
    assert not staleness(thesis(), AS_OF, events=[outside]).pre_event


def brief_kw(**kw):
    base = dict(outcome_map=(OutcomeMapping("gross margin prints below 55%", 1, "fires"),
                             OutcomeMapping("gross margin prints above 57%", 1, "clears"),
                             OutcomeMapping("gross margin between", 1, "undetermined")),
                will_not_tell_you=("whether the DRAM cycle has turned",),
                authored_at=utc(2026, 9, 20))
    return {**base, **kw}


def test_ac_1_45_editing_a_brief_after_its_event_raises():
    """AC-1.45 / RA-73 — its entire value is the possibility of being wrong in public."""
    event = earnings(date(2026, 9, 24))
    brief = pre_event_brief(thesis(), event, **brief_kw())
    edited = dataclasses.replace(brief, will_not_tell_you=("nothing, actually",))
    with pytest.raises(BriefMutatedError):
        assert_unedited(brief, edited, now=utc(2026, 9, 25))


def test_an_unedited_brief_passes_after_the_event():
    """RA-73 — the check is on mutation, not on being read afterwards."""
    event = earnings(date(2026, 9, 24))
    brief = pre_event_brief(thesis(), event, **brief_kw())
    assert_unedited(brief, brief, now=utc(2026, 9, 25))


def test_a_brief_written_on_or_after_the_event_raises():
    """RA-73 — written BEFORE, or it is not a pre-commitment."""
    event = earnings(date(2026, 9, 24))
    with pytest.raises(BriefMutatedError):
        pre_event_brief(thesis(), event, **brief_kw(authored_at=utc(2026, 9, 24)))


def test_ac_1_46_a_brief_stating_an_expected_result_fails_the_run():
    """AC-1.46 / RA-74 — a forecast wearing a process's clothing."""
    event = earnings(date(2026, 9, 24))
    with pytest.raises(BriefPredictsError, match="expected result"):
        pre_event_brief(thesis(), event, **brief_kw(
            outcome_map=(OutcomeMapping("we expect gross margin near 56%", 1, "clears"),)))


def test_forecast_voice_in_a_brief_also_fails():
    """RA-74 with RA-137 — D-01 owns one wordlist, and the brief is inside it."""
    event = earnings(date(2026, 9, 24))
    with pytest.raises(BriefPredictsError):
        pre_event_brief(thesis(), event, **brief_kw(
            will_not_tell_you=("margin will certainly recover next year",)))


def test_ac_1_47_what_this_event_will_not_tell_you_is_mandatory():
    """AC-1.47 / RA-75 — naming the limit is free only before the number exists."""
    event = earnings(date(2026, 9, 24))
    with pytest.raises(ResearchError, match="RA-75"):
        pre_event_brief(thesis(), event, **brief_kw(will_not_tell_you=()))
    with pytest.raises(ResearchError, match="RA-75"):
        pre_event_brief(thesis(), event, **brief_kw(will_not_tell_you=("  ",)))


def test_a_brief_is_hashed_before_the_event():
    """RA-73 — the hash is the pre-commitment, and it is content-addressed."""
    event = earnings(date(2026, 9, 24))
    brief = pre_event_brief(thesis(), event, **brief_kw())
    assert brief.brief_hash and brief.brief_hash == brief.compute_hash()
    other = pre_event_brief(thesis(), event, **brief_kw(
        will_not_tell_you=("whether pricing has bottomed",)))
    assert other.brief_hash != brief.brief_hash


def test_ac_1_48_briefs_go_only_to_live_theses_and_macro_lands_once():
    """AC-1.48 / RA-76, RA-77 — thirteen CPI briefs is one narrative, thirteen leaks."""
    live = thesis()
    events = [earnings(date(2026, 9, 24), ticker="MU"),
              earnings(date(2026, 9, 25), ticker="NVDA"),
              CalendarEvent("cpi", date(2026, 9, 10), utc(2026, 8, 1)),
              CalendarEvent("cpi", date(2026, 9, 10), utc(2026, 8, 1))]
    targets = brief_targets([live], events)
    assert [(t.ticker if t else None, e.event_class) for t, e in targets] == [
        ("MU", "earnings"), (None, "cpi")]
    assert sum(1 for _t, e in targets if e.scope == SCOPE_BOOK) == 1


def test_a_book_level_class_may_not_be_written_per_ticker():
    """RA-77 — the scope is a property of the event class, not of the caller."""
    assert CalendarEvent("fomc", date(2026, 9, 17), utc(2026, 8, 1)).scope == SCOPE_BOOK


# --------------------------------------------------------------------------- #
# §10B — unscheduled events and moves. AC-1.49…1.58
# --------------------------------------------------------------------------- #

def decomposition(**kw):
    base = dict(ticker="MU", session=date(2026, 8, 26), total_return=-0.062,
                market=-0.011, sector=-0.020, residual=-0.031, trail_ref="d02:trail:1")
    return MoveDecomposition(**{**base, **kw})


def test_ac_1_49_the_decomposition_arrives_from_d02_with_its_trail():
    """AC-1.49 / RA-78, RA-45 — sourced from D-02 because D-02 is neutral ground."""
    with pytest.raises(MoveUndecomposedError, match="neutral ground"):
        decomposition(source="D-03")
    with pytest.raises(MoveUndecomposedError, match="trail"):
        decomposition(trail_ref="")


def test_the_decomposition_identity_must_close():
    """RA-45 — four numbers that do not add up are not a decomposition."""
    with pytest.raises(MoveUndecomposedError, match="identity"):
        decomposition(residual=-0.001)


def test_src_fundamental_computes_no_series_arithmetic():
    """AC-1.49 / RA-45 — enforced structurally; see architecture rule RA-45."""
    from tests_src import architecture
    assert architecture.ra_45(architecture.scan()) == []


def test_ac_1_50_an_unexplained_residual_is_a_data_gap_not_a_story():
    """AC-1.50 / RA-79, RA-80 — the honest gap beats the plausible reason."""
    review = review_move(MoveTrigger("MU", date(2026, 8, 26), 3.1), decomposition())
    assert review.status == UNEXPLAINED
    assert review.data_gap["obtainable"] == "fetchable"
    assert "does not say why" in review.data_gap["note"]
    assert review.explanation_refs == ()


def test_supplying_a_cause_for_an_unexplained_move_raises():
    """RA-79 — an LLM asked *why did this stock fall* will always produce a reason."""
    with pytest.raises(MoveRationalisedError):
        review_move(MoveTrigger("MU", date(2026, 8, 26), 3.1), decomposition(),
                    cause="investors rotated out of memory")


def test_an_explained_move_routes_to_v01():
    """§10B.2 — the bundle explains it, so it becomes *did a stated condition fire?*"""
    review = review_move(MoveTrigger("MU", date(2026, 8, 26), 3.1), decomposition(),
                         explanations=[("acc-8k-1", utc(2026, 8, 26, 8))],
                         move_at=utc(2026, 8, 26, 14))
    assert review.status == EXPLAINED and review.routed_to == "V-01"


def test_an_explanation_published_after_the_move_cannot_have_caused_it():
    """RA-81 — *"fell on the news"* requires the timestamp to precede the move."""
    with pytest.raises(MoveRationalisedError, match="RA-81"):
        review_move(MoveTrigger("MU", date(2026, 8, 26), 3.1), decomposition(),
                    explanations=[("url-1", utc(2026, 8, 26, 17))],
                    move_at=utc(2026, 8, 26, 14))


def test_ac_1_51_routing_is_a_pure_table_on_item_number():
    """AC-1.51 / RA-82 — the SEC already assigned the code; classifying it reverses AP-5."""
    routing = route_filing("acc-1", ["2.06"])
    assert routing.severity == "escalate"
    assert route_filing("acc-2", ["2.02"]).severity == "post_event"
    # ★ deterministic: identical inputs, identical routing (INV-2).
    assert route_filing("acc-1", ["2.06"]).to_json_obj() == routing.to_json_obj()
    assert route_filing("acc-3", ["9.99"]).severity == "note"


def extraction(*items):
    return ExtractionResult(block_id="E-01", bundle_hash="sha256:x", items=items)


def item(evidence_id, period):
    return ExtractedItem(evidence_id=evidence_id, value="55.4", unit="pct",
                         period=period, quote="Gross margin was 55.4%.",
                         span=EvidenceSpan(accession_id="0000-1", start=0, end=23))


def test_ac_1_52_item_4_02_withdraws_the_evidence_and_drives_coverage_to_zero():
    """AC-1.52 / RA-83 — a non-reliance filing withdraws the FACTS, not just the thesis."""
    routing = route_filing("acc-402", ["4.02"])
    assert routing.withdraws_evidence and routing.severity == "withdraw"

    affected = [Period(start="2024-10-01", end="2025-09-30")]
    result = extraction(item("e1", Period("2025-01-01", "2025-03-31")),
                        item("e2", Period("2025-04-01", "2025-06-30")))
    kept, withdrawn = withdraw_extractions(result, affected)
    assert kept.evidence_ids == frozenset()
    assert {i.evidence_id for i in withdrawn} == {"e1", "e2"}

    from src.fundamental import B43_RUBRICS, assess_confidence, coverage_report
    report = coverage_report(B43_RUBRICS, kept.evidence_ids)
    assert report.aggregate == 0.0
    assert assess_confidence(report).cap == INSUFFICIENT_DATA


def test_a_scorecard_level_citing_an_affected_period_must_be_re_derived():
    """RA-83 — re-derived, not adjusted; never "HOLD pending review"."""
    with pytest.raises(EvidenceWithdrawnError, match="re-derived"):
        assert_scorecard_re_derived(
            "MU", [Period("2025-01-01", "2025-03-31")],
            [Period("2024-10-01", "2025-09-30")], dimensions=["earnings_quality"])


def test_ac_1_52a_withdrawal_is_by_period_and_an_undated_item_goes_too():
    """AC-1.52a / RA-138 — an undated fact cannot be shown to lie outside the range."""
    affected = [Period("2024-10-01", "2025-09-30")]
    result = extraction(item("old", Period("2022-01-01", "2022-03-31")),
                        item("hit", Period("2025-01-01", "2025-03-31")),
                        item("undated", None))
    kept, withdrawn = withdraw_extractions(result, affected)
    assert kept.evidence_ids == frozenset({"old"})          # FY2022 survives
    assert {i.evidence_id for i in withdrawn} == {"hit", "undated"}


def test_ac_1_53_only_7_01_and_8_01_items_and_news_reach_the_cheap_tier():
    """AC-1.53 / RA-84 — everything the form already types is routed by the table."""
    news = NewEvidenceItem("news", "url-1", utc(2026, 8, 26))
    fd = NewEvidenceItem("filing", "acc-1", utc(2026, 8, 26), item_code="8.01")
    assert cheap_tier_queue([news, fd]) == (news, fd)
    typed = NewEvidenceItem("filing", "acc-2", utc(2026, 8, 26), item_code="4.01")
    with pytest.raises(ResearchError, match="RA-84"):
        cheap_tier_queue([typed])
    assert route_filing("acc-1", ["7.01", "8.01", "4.01"]).to_cheap_tier == ("7.01", "8.01")


def test_ac_1_54_the_sweep_reports_a_quiet_week_explicitly():
    """AC-1.54 / RA-86 — a sweep that appears only when it has something to say
    is indistinguishable from a sweep that did not run."""
    report = weekly_sweep(date(2026, 8, 21), findings=(), covered=["MU", "NVDA"])
    assert report.nothing_accumulated
    assert report.to_json_obj()["statement"] == "nothing accumulated"
    assert report.to_json_obj()["covered"] == ["MU", "NVDA"]


def test_a_missing_week_is_a_defect_not_an_empty_week():
    """RA-86 — the absence of a report is the thing being detected."""
    reports = [weekly_sweep(date(2026, 8, 21))]
    assert assert_sweep_emitted(reports, date(2026, 8, 21)).nothing_accumulated
    with pytest.raises(SweepSilentError):
        assert_sweep_emitted(reports, date(2026, 8, 28))


def test_ac_1_55_the_sweep_emits_no_verdict_and_no_recommendation():
    """AC-1.55 / RA-87 — INV-6 permits exactly one decision channel."""
    report = weekly_sweep(date(2026, 8, 21), findings=(
        Accumulation("residual_drip", "MU", "five sessions of -0.6% residual"),))
    obj = report.to_json_obj()
    assert set(obj) & {"verdict", "recommendation", "action"} == set()
    assert actionable_recommendations(report) == 0
    with pytest.raises(ResearchError, match="INV-6"):
        assert_no_verdict({"verdict": "SELL"}, where="SweepReport")


def test_an_event_may_not_be_filed_as_an_accumulation():
    """RA-85 — the sweep's subject is accumulation; events are handled daily."""
    with pytest.raises(ValueError, match="daily path"):
        Accumulation("8k_filed", "MU", "item 2.06")


def test_ac_1_56_a_move_trigger_without_a_residual_raises():
    """AC-1.56 / RA-88 — a raw-return trigger fires on every name at once."""
    with pytest.raises(MoveUndecomposedError):
        review_move(MoveTrigger("MU", date(2026, 8, 26), 3.1), None)
    with pytest.raises(MoveUndecomposedError, match="PARTIAL"):
        review_move(MoveTrigger("MU", date(2026, 8, 26), 3.1, basis=BASIS_RAW),
                    decomposition())


def test_a_trigger_and_decomposition_for_different_sessions_raise():
    """RA-88 — the residual must be *this* session's, or it explains nothing."""
    with pytest.raises(MoveUndecomposedError, match="does not match"):
        review_move(MoveTrigger("MU", date(2026, 8, 27), 3.1), decomposition())


def test_ac_1_57_two_names_tripping_the_same_session_are_a_suspected_common_factor():
    """AC-1.57 / RA-89 — a system firing thirteen triggers has diagnosed itself."""
    triggers = [MoveTrigger("MU", date(2026, 8, 26), 3.1),
                MoveTrigger("NVDA", date(2026, 8, 26), 2.8),
                MoveTrigger("MU", date(2026, 8, 27), 2.2)]
    (clustered, alone) = cluster_check(triggers)
    assert clustered.suspected_common_factor and clustered.tickers == ("MU", "NVDA")
    assert not alone.suspected_common_factor
    assert "already diagnosed itself" in clustered.to_json_obj()["note"]


def test_ac_1_58_fx_is_a_named_term_never_inside_the_residual():
    """AC-1.58 / RA-90, INV-5 — a CAD book carries the same exposure on every name."""
    with pytest.raises(MoveUndecomposedError, match="RA-90"):
        decomposition(quote_currency="USD", book_currency="CAD")
    ok = decomposition(quote_currency="USD", book_currency="CAD", fx=-0.004,
                       residual=-0.027)
    assert ok.to_json_obj()["fx"] == -0.004
    assert "fx" in ok.to_json_obj()


# --------------------------------------------------------------------------- #
# §10B.5 — vintages and the industry term. AC-1.60, 1.61, 1.65
# --------------------------------------------------------------------------- #

def test_ac_1_60_a_series_with_no_vintage_is_revised_series_and_unchecked_grade():
    """AC-1.60 / RA-93 — never silently used."""
    comparison = SeriesComparison("SEMI_UTILISATION", date(2026, 3, 31), 0.86)
    assert grade_comparison(comparison).basis == "revised_series"
    assert comparison.grade == "UNCHECKED"
    assert comparison.to_json_obj()["grade"] == "UNCHECKED"


def test_ac_1_65_a_series_alfred_covers_may_not_be_graded_revised():
    """AC-1.65 / RA-93 — recording a free check as unavailable downgrades it forever."""
    assert "CPIAUCSL" in ALFRED_COVERED
    with pytest.raises(ResearchError, match="ALFRED"):
        grade_comparison(SeriesComparison("CPIAUCSL", date(2026, 3, 31), 312.1))
    checked = grade_comparison(SeriesComparison("CPIAUCSL", date(2026, 3, 31), 312.1,
                                                vintage_date=date(2026, 4, 10)))
    assert checked.basis == "vintage_checked" and checked.grade == ""


def test_company_disclosure_needs_no_vintage_service_but_needs_its_filing_date():
    """RA-93a — its vintage IS its filing date, and DE-18 already carries it."""
    disclosure = SeriesComparison("MSFT_CAPEX_GUIDE", date(2026, 3, 31), 21.4,
                                  kind="company_disclosure",
                                  knowable_at=date(2026, 1, 29))
    assert grade_comparison(disclosure).basis == "vintage_checked"
    with pytest.raises(ResearchError, match="RA-93a"):
        grade_comparison(SeriesComparison("MSFT_CAPEX_GUIDE", date(2026, 3, 31), 21.4,
                                          kind="company_disclosure"))


def test_treasury_rates_are_market_prices_and_are_not_revised():
    """RA-93a — the ALFRED dependency is narrow and must not gate what does not need it."""
    rate = SeriesComparison("UST10Y", date(2026, 3, 31), 0.0412, kind="market_price")
    assert grade_comparison(rate).basis == "vintage_checked"


def test_ac_1_61_the_industry_term_comes_from_d02_with_its_trail():
    """AC-1.61 / RA-94, RA-45 — a chosen peer set is a conclusion wearing a denominator."""
    peers = PeerContext(industry="semiconductors", period="FY2026Q2",
                        members=("MU", "SK", "SEC"), median=0.41,
                        trail_ref="d02:peers:1")
    assert peers.source == "D-02"
    with pytest.raises(ResearchError, match="RA-94"):
        dataclasses.replace(peers, source="D-01")
    with pytest.raises(ResearchError, match="RA-45"):
        dataclasses.replace(peers, trail_ref="")


def test_src_fundamental_assembles_no_peer_set():
    """AC-1.61 — the module offers no way to select peers; it can only receive one."""
    import src.fundamental.events.vintage as vintage
    names = [n for n in dir(vintage) if "peer" in n.casefold()]
    assert names == ["PeerContext"]


# --------------------------------------------------------------------------- #
# ★ The package surface — a guard the B4.6 build earned
# --------------------------------------------------------------------------- #

def test_no_two_d01_modules_export_the_same_name_with_different_values():
    """★ D-01's `__init__` re-exports ~250 names from 25 modules, and a flat
    namespace makes a collision **silent**: the later import simply wins.

    ⚠ This is not hypothetical. Building B4.6, `events/sweep.KINDS` (the
    accumulation kinds) shadowed `claims/models.KINDS` (fact · inference ·
    assumption) in the package surface. Nothing in `src/` broke — a B4.2 test
    caught it, and only because it asserted the tuple's *contents*.
    """
    import importlib
    import pkgutil
    import types

    import src.fundamental as pkg

    seen, collisions = {}, []
    for info in pkgutil.walk_packages(pkg.__path__, prefix="src.fundamental."):
        module = importlib.import_module(info.name)
        for name in dir(module):
            if name.startswith("_") or name not in pkg.__all__:
                continue
            value = getattr(module, name)
            if isinstance(value, types.ModuleType):
                continue                      # `bundle.assemble` the module,
                                              # not `assemble` the function
            if getattr(value, "__module__", info.name) != info.name:
                continue                      # re-exported, not defined here
            prior = seen.get(name)
            if prior and prior[1] is not value:
                collisions.append((name, prior[0], info.name))
            seen.setdefault(name, (info.name, value))
    assert collisions == []
