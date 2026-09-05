"""D-01 B4.8 — AC-1.73…1.85, plus AC-1.76a and AC-1.77a.

★★ **BS-30a: B4.8 is the only D-01 slice that REDUCES running cost instead of
adding capability.** It moves the expensive deep-tier authoring onto a flat-rate
subscription, making B4.4's API path optional for most names.

```text
  THE RELAY IS AN EXTERNAL PROVIDER WITH A HUMAN AS ITS TRANSPORT.
  ⚠ A number does not become trustworthy because a human carried it.
```

★ **§4B.3 is the safety case, and it needed no new rule**: `confidence :=
evidence_coverage` (RA-114) de-rates the relay automatically, and AC-1.8's
`k ≥ 3` requirement (RA-115) keeps it off the actionable slot by construction.

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from src.fundamental import (
    ARCHETYPES, AuthoringRun, BUY, BearCase, CONFIDENCE_FLOOR, CONFIDENCE_HOLD_CAP,
    CONTRADICTED, CalendarEvent, ClaimVerification, Falsifier, HOLD_CAPPED,
    INSUFFICIENT_DATA, PROVENANCE_RELAYED, PromptRegistry, QueueEntry,
    RelayContradictedError, RelayEnvelope, RelayNotFreshError, RelayPartialError,
    RelayPromptUnattributedError, RelayReport, RelayStabilityClaimedError,
    ROTATION, UNVERIFIABLE, VERIFIED, VerificationResult, assemble, assert_fresh,
    assert_whole, block, blocks_for, compose, computed, confidence_of,
    derive_queue, filing, ingest_relay, profile, relay_staleness, verify_claim,
)

AS_OF = date(2026, 8, 25)
DEADLINE = date(2027, 3, 31)
UTC = timezone.utc


def registry():
    reg = PromptRegistry()
    for name in ("RLY-0", "RLY-A", "RLY-B", "RLY-CYCLE", "RLY-SUPPLY",
                 "RLY-BOOK", "RLY-SPREAD"):
        reg.register(block(name, "v1", "judgement", f"<<{name} body>>"))
    return reg


def envelope(**kw):
    base = dict(assistant="claude_pro", model_stated="Claude Opus 4.5",
                relayed_by="victor", pasted_at="2026-08-25T19:40:00Z",
                prompt_blocks=("RLY-0@v1", "RLY-A@v1", "RLY-B@v1",
                               "RLY-CYCLE@v1", "RLY-SUPPLY@v1"),
                archetype_applied="cyclical_commodity")
    return RelayEnvelope(**{**base, **kw})


def verifications(verified=3, unverifiable=7, contradicted=0):
    out, n = [], 0
    for _ in range(verified):
        n += 1
        out.append(ClaimVerification(n, f"claim {n}", VERIFIED,
                                     checked_against="D-07 f_gross_margin",
                                     ours="55.4", theirs="55.4"))
    for _ in range(contradicted):
        n += 1
        out.append(ClaimVerification(n, f"claim {n}", CONTRADICTED,
                                     checked_against="D-07 f_gross_margin",
                                     ours="55.4", theirs="61.0"))
    for _ in range(unverifiable):
        n += 1
        out.append(ClaimVerification(n, f"claim {n}", UNVERIFIABLE))
    return tuple(out)


def report(**kw):
    base = dict(ticker="MU", as_of=AS_OF, envelope=envelope(),
                text="A full analysis of the memory cycle.",
                verifications=verifications(), verdict="HOLD",
                conviction="Medium")
    return ingest_relay(**{**base, **kw})


# --------------------------------------------------------------------------- #
# Composition — RA-122, RA-123, RA-124. AC-1.73, 1.74, 1.75
# --------------------------------------------------------------------------- #

def test_ac_1_73_composition_makes_no_llm_call():
    """AC-1.73 / RA-124 — ★ **the relay stays manual. No automation of a chat
    interface, ever.**

    ⚠ Automating it would be both a terms problem and the exact "leak by
    execution" XP-33 refused. Structural, not a convention: the module imports
    no transport and no gateway.
    """
    from tests_src import architecture

    graph = architecture.scan()
    reached = graph.get("src/fundamental/relay/compose.py", set())
    assert not {m for m in reached
                if m.split(".")[0] in {"anthropic", "requests", "httpx",
                                       "urllib", "selenium", "playwright"}}
    assert not any("gateway" in m for m in reached)


def test_ac_1_74_a_hand_edited_prompt_fails_ingest():
    """AC-1.74 / RA-122 — ⚠ a hand-edited prompt makes the artifact
    **unattributable** and silently breaks INV-9's alignment for that name."""
    prompt = compose(registry(), ticker="MU", archetype="cyclical_commodity")
    with pytest.raises(RelayPromptUnattributedError, match="composition produced"):
        report(prompt=prompt,
               envelope=envelope(prompt_blocks=("RLY-0@v1", "MY-OWN-BLOCK@v1")))


def test_the_declared_archetype_must_match_the_one_composed_for():
    """RA-122/RA-123 — block selection and the analysis may not disagree."""
    prompt = compose(registry(), ticker="MU", archetype="cyclical_commodity")
    with pytest.raises(RelayPromptUnattributedError, match="disagree"):
        report(prompt=prompt, envelope=envelope(archetype_applied="financial"))


def test_a_well_formed_relay_passes_attribution():
    """RA-122 — the blocks the response cites are the blocks composition made."""
    prompt = compose(registry(), ticker="MU", archetype="cyclical_commodity")
    assert report(prompt=prompt).relay.prompt_blocks == prompt.blocks


def test_a_drifted_block_raises_before_a_human_is_handed_the_prompt():
    """RA-13/INV-9 — every block goes through `registry.check`, so the drift is
    caught at composition rather than after a paste."""
    from src.fundamental import PromptDriftError

    reg = registry()
    drifted = reg.get("RLY-A", "v1")
    object.__setattr__(drifted, "text", "<<edited in place>>")
    with pytest.raises(PromptDriftError):
        compose(reg, ticker="MU", archetype="cyclical_commodity")


def test_ac_1_75_archetype_drives_block_selection():
    """AC-1.75 / RA-123 — ★ *this is the "intelligence" that places the feature
    in D-01.* A `cyclical_commodity` gets the cycle and supply-side blocks; a
    `financial` gets book-value framing instead of EPS."""
    assert blocks_for("cyclical_commodity")[-2:] == ("RLY-CYCLE", "RLY-SUPPLY")
    assert blocks_for("financial")[-2:] == ("RLY-BOOK", "RLY-SPREAD")
    assert blocks_for("insufficient_evidence") == blocks_for("regulated_utility")[:3]

    text = compose(registry(), ticker="MU",
                   archetype="cyclical_commodity").text
    assert "RLY-CYCLE" in text and "RLY-BOOK" not in text


def test_the_archetypes_are_j01s_enum():
    """RA-123 — ★ a seventh archetype is a master-prompt change, not a relay one."""
    assert set(ARCHETYPES) == {
        "cyclical_commodity", "compounder", "secular_growth", "regulated_utility",
        "financial", "binary_outcome", "insufficient_evidence"}
    with pytest.raises(ValueError, match="J-01"):
        blocks_for("meme_stock")


# --------------------------------------------------------------------------- #
# Ingest — RA-117, RA-118, RA-125. AC-1.76, 1.76a, 1.80
# --------------------------------------------------------------------------- #

def test_ac_1_76_a_contradicted_number_fails_the_ingest():
    """AC-1.76 / RA-118 — ⚠ **not a difference of opinion.**

    *A number does not become trustworthy because a human carried it.*
    """
    with pytest.raises(RelayContradictedError):
        report(verifications=verifications(contradicted=1))


def test_ac_1_76a_the_failure_names_which_claim_contradicted():
    """AC-1.76a / RA-143 — ★ *"contradicted: 1"* is not an error message anyone
    can act on. The per-claim record is what makes it one."""
    with pytest.raises(RelayContradictedError, match=r"claim #4.*55\.4.*61\.0"):
        report(verifications=verifications(contradicted=1))


def test_a_hold_capped_report_names_which_claims_were_unverifiable():
    """AC-1.76a / RA-143 — ★ that set is precisely what the cap is about."""
    unverified = report().verification.unverifiable_claims
    assert [c.ordinal for c in unverified] == [4, 5, 6, 7, 8, 9, 10]
    assert all(c.checked_against == "" for c in unverified)


def test_the_counts_are_a_projection_of_the_claims_never_a_parallel_store():
    """RA-143 / RA-133's shape — two stores for one idea is how they diverge."""
    result = VerificationResult(claims=verifications(verified=2, unverifiable=3))
    assert (result.claims_total, result.verified, result.unverifiable) == (5, 2, 3)
    assert result.to_json_obj()["claims_total"] == len(result.to_json_obj()["claims"])


def test_verify_claim_marks_a_missing_counterpart_unverifiable():
    """RA-118 — ★ the honest majority case, and the one RA-114 prices."""
    assert verify_claim({"value": 55.4, "text": "gm"}, ours=None, ordinal=1,
                        checked_against="").result == UNVERIFIABLE
    assert verify_claim({"value": 55.4}, ours=55.4, ordinal=1,
                        checked_against="D-07").result == VERIFIED
    assert verify_claim({"value": 61.0}, ours=55.4, ordinal=1,
                        checked_against="D-07").result == CONTRADICTED


def test_a_verified_claim_must_name_what_it_was_checked_against():
    """RA-118 — ★ a verification that cannot say what it checked against is not one."""
    with pytest.raises(ValueError, match="not a verification"):
        ClaimVerification(1, "gm", VERIFIED)


def test_ac_1_80_a_continued_session_fails_ingest():
    """AC-1.80 / RA-117 — ★ **a chat box IS conversational state.**

    A follow-up makes the analysis path-dependent, which RA-12 forbids because
    it turns a stochastic answer into a **stubborn** one.
    """
    with pytest.raises(RelayNotFreshError):
        report(envelope=envelope(session="continued"))
    assert_fresh("MU", envelope())


def test_ac_1_80_a_truncated_or_refused_response_fails_ingest():
    """AC-1.80 / RA-125 — ⚠ **there is no `partial`**, and it is never topped up."""
    with pytest.raises(RelayPartialError, match="truncated"):
        report(text="The cycle analysis so far... shall I continue")
    with pytest.raises(RelayPartialError, match="refused"):
        report(text="I can't help with that.")
    with pytest.raises(RelayPartialError, match="empty"):
        report(text="   ")


def test_the_partial_error_says_re_run_not_top_up():
    """RA-125 with RA-117 — topping up would make it a conversation."""
    with pytest.raises(RelayPartialError, match="never top up"):
        assert_whole("MU", "[continued]")


# --------------------------------------------------------------------------- #
# §4B.3 — the two mechanisms that de-rate WITHOUT a new rule. AC-1.77, 1.78
# --------------------------------------------------------------------------- #

def test_ac_1_77_the_floors_fire_on_verification_coverage():
    """AC-1.77 / RA-114 — ★★ *a mechanism built to stop a model inflating its
    own confidence turns out to price an untrusted transport correctly too.*"""
    assessment = confidence_of(report())            # 3 verified of 10
    assert assessment.value == pytest.approx(0.3)
    assert assessment.cap == HOLD_CAPPED
    assert assessment.basis == "evidence_coverage"

    thin = confidence_of(report(verifications=verifications(1, 9)))
    assert thin.value < CONFIDENCE_FLOOR and thin.cap == INSUFFICIENT_DATA

    strong = confidence_of(report(verifications=verifications(9, 1)))
    assert strong.value >= CONFIDENCE_HOLD_CAP and strong.cap == "none"


def test_ac_1_77a_the_floors_are_one_implementation_not_two():
    """AC-1.77a / RA-144 — ★★ two copies of one rule is FE-4's defect, and the
    one RA-137 had just finished removing from the wordlist.

    ⚠ **The denominators stay different and must**: RA-65's is the rubric's
    `required_union`, the relay's is `claims_total`. *What is shared is the
    threshold, not the arithmetic that reaches it.*
    """
    from src.fundamental.scorecard.coverage import assess_confidence

    from_relay = confidence_of(report())
    from_float = assess_confidence(0.3)
    assert (from_relay.cap, from_relay.value) == (from_float.cap, from_float.value)

    import inspect
    source = inspect.getsource(
        __import__("src.fundamental.relay.ingest", fromlist=["x"]))
    assert "CONFIDENCE_FLOOR" not in source and "< floor" not in source


def test_ac_1_78_a_relay_report_can_never_be_the_actionable_pick():
    """AC-1.78 / RA-115 — ★★ **impossible by construction**, not by policy.

    AC-1.8 requires the actionable pick to carry a `k ≥ 3` stability result, and
    **a single chat response has no distribution.**
    """
    relayed = report()
    assert relayed.verdict_stability is None
    assert relayed.can_be_actionable is False
    assert relayed.to_json_obj()["verdict_stability"] is None


def test_claiming_a_verdict_stability_on_a_relay_raises():
    """RA-115 — the field is kept precisely so a claim on it is *visible*."""
    with pytest.raises(RelayStabilityClaimedError):
        RelayReport(ticker="MU", as_of=AS_OF, relay=envelope(),
                    verification=VerificationResult(claims=verifications()),
                    verdict_stability={"k": 5, "agreement": 1.0})


def test_two_passes_restore_the_anchor_strip_structurally():
    """RA-119 / §4B.6 — ⚠ *staging inside a single prompt is ordering, not a
    freeze, and the spec says so.* ★ Pass A never receives the price."""
    assert envelope(passes=1).anchor_strip_is_structural is False
    assert envelope(passes=2).anchor_strip_is_structural is True
    assert envelope(passes=1).to_json_obj()["anchor_strip"] == "instruction_only"
    with pytest.raises(ValueError, match="one paste or two"):
        envelope(passes=3)


def test_the_stated_model_is_never_recorded_as_a_fact():
    """§4B.2 / CT-1.5 — ★ a chat UI reports no model id. Record what is knowable,
    leave the rest unknown, **never fabricate**."""
    obj = report().to_json_obj()["relay"]
    assert obj["model_stated"] == "Claude Opus 4.5"
    assert "model_id" not in obj and "temperature" not in obj


# --------------------------------------------------------------------------- #
# Provenance — RA-116. AC-1.79
# --------------------------------------------------------------------------- #

def test_ac_1_79_the_provenance_class_travels_on_the_report():
    """AC-1.79 / RA-116 — ⚠ *a reader must never have to remember which reports
    came from a chat window.*"""
    assert report().provenance_class == PROVENANCE_RELAYED
    assert report().to_json_obj()["provenance_class"] == PROVENANCE_RELAYED
    with pytest.raises(ValueError, match="RA-116"):
        RelayReport(ticker="MU", as_of=AS_OF, relay=envelope(),
                    verification=VerificationResult(claims=verifications()),
                    provenance_class="judgement")


def test_ac_1_79_d09_carries_a_fourth_reliability_class():
    """AC-1.79 / RP-1, RP-48 — ★ **more provisional than `judgement`, never a
    footnote on it.** D-01 declared the fourth class and RP-1 listed three."""
    from src.reporting.render.classes import (
        CLASSES, GLYPH, JUDGEMENT, LABEL, RELAYED_JUDGEMENT, is_weaker_than,
    )

    assert RELAYED_JUDGEMENT in CLASSES
    assert is_weaker_than(RELAYED_JUDGEMENT, JUDGEMENT)
    assert GLYPH[RELAYED_JUDGEMENT] != GLYPH[JUDGEMENT]      # QP-1 — not colour
    assert "unverified transport" in LABEL[RELAYED_JUDGEMENT]


# --------------------------------------------------------------------------- #
# Staleness and the queue — RA-120, RA-126…RA-128. AC-1.81…1.85
# --------------------------------------------------------------------------- #

def falsifiers():
    return (Falsifier(ordinal=1, condition="Gross margin below 55% twice.",
                      observable_field="f_gross_margin", source="D-02",
                      deadline=DEADLINE, materiality="The premise fails."),
            Falsifier(ordinal=2, condition="Net debt / EBITDA above 3.0x.",
                      observable_field="f_net_debt_ebitda", source="D-02",
                      deadline=DEADLINE, materiality="Balance-sheet premise fails."))


def thesis(as_of=AS_OF):
    run = AuthoringRun(ticker="MU", as_of=as_of)
    return run.author(
        bundle=assemble(ticker="MU", as_of=as_of,
                        parts=[filing("0000-1", "Gross margin was 55.4%."),
                               computed("b3_minimal", 1, "fv=[380,445]"),
                               profile(as_of, "Sector: IT")]),
        stage_a_payload={"moat_durability": 3}, falsifiers=falsifiers(),
        verdict=BUY, conviction="Medium-High",
        bear_case=BearCase(text="Capacity additions crush pricing.",
                           falsification_condition="Utilisation above 90%.",
                           prompt_version="J-11@v1", run_id="call-bear"),
        scorecard={"moat_durability": 3},
        confidence={"value": 0.62, "basis": "evidence_coverage"},
        bull_run_ids=("call-bull",), run_id="run-1")


def test_ac_1_81_relay_staleness_is_event_relative_not_clock_relative():
    """AC-1.81 / RA-120 — ★ *"D-01 just needs to search, re-evaluate and update
    if the report is too old"* — **and it already exists** (RA-71, unchanged)."""
    results = CalendarEvent("earnings", AS_OF + timedelta(days=1), datetime(
        2026, 7, 1, tzinfo=UTC), date_status="confirmed", ticker="MU")
    state = relay_staleness(thesis(), AS_OF + timedelta(days=2), events=[results],
                            last_relayed_on=AS_OF)
    assert state.stale and state.basis == "event"
    # ⚠ the clock alone calls this fresh: ~48h since the relay, at the floor.
    assert not relay_staleness(thesis(), AS_OF + timedelta(days=2),
                               last_relayed_on=AS_OF + timedelta(days=1)).stale


def test_ac_1_83_an_unrun_queued_name_goes_stale_and_the_queue_does_not_absorb_it():
    """AC-1.83 / RA-126 — ★★ **an overdue relay is not a backlog item — it is a
    thesis going stale.** *A name sitting in a queue is not a name that has been
    analysed.*"""
    entry = QueueEntry(ticker="MU", last_relayed_on=AS_OF,
                       queued_since=AS_OF - timedelta(days=9))
    late = AS_OF + timedelta(days=5)
    queue = derive_queue([entry], as_of=late,
                         stale_tickers=[thesis().ticker])
    assert entry in queue.overdue
    # ⚠ being queued changes nothing about the thesis's own staleness test.
    assert relay_staleness(thesis(), late, last_relayed_on=AS_OF).stale
    assert queue.stale == ("MU",)


def test_ac_1_84_a_stale_relay_sourced_thesis_flags_at_the_gate():
    """AC-1.84 / RA-126, §11.2 — ★ **the cost of not running one is paid in
    visible confidence, not in a hidden gap**, which is what makes *"my
    responsibility to remember"* a workable arrangement rather than a hope."""
    from src.fundamental import FLAG, GateInputs, PASS, evaluate

    verdict = evaluate(GateInputs(thesis=thesis(), stale=True), as_of=AS_OF)
    assert verdict.status == FLAG
    assert evaluate(GateInputs(thesis=thesis(), stale=False),
                    as_of=AS_OF).status == PASS


def test_ac_1_85_nothing_is_re_prioritised_for_having_been_skipped():
    """AC-1.85 / RA-127 — ⚠ **a queue that pesters is a system asserting
    authority it does not hold.**

    ★ *Skipping is a decision SEAT-1 is entitled to make*, and D-01's obligation
    is the override obligation: **make it visible and let it stand.**
    """
    day = AS_OF - timedelta(days=3)
    skipped = QueueEntry("MU", last_relayed_on=day, queued_since=day,
                         times_skipped=9)
    never = QueueEntry("NVDA", last_relayed_on=day, queued_since=day)
    ordered = derive_queue([skipped, never], as_of=AS_OF, per_day=2).today
    # alphabetical within the same dates — the skip count moved nothing.
    assert [e.ticker for e in ordered] == ["MU", "NVDA"]
    flipped = derive_queue([never, skipped], as_of=AS_OF, per_day=2).today
    assert [e.ticker for e in flipped] == ["MU", "NVDA"]


def test_ac_1_85_nothing_is_dropped_to_make_room():
    """AC-1.85 / RA-128 — ★ **an overdue entry ages in place.**"""
    entries = [QueueEntry(t, last_relayed_on=None,
                          queued_since=AS_OF - timedelta(days=d))
               for d, t in enumerate(("A", "B", "C", "D", "E"), start=1)]
    queue = derive_queue(entries, as_of=AS_OF, per_day=2)
    assert len(queue.today) == 2
    assert len(queue.carried) == 5              # nothing dropped
    assert {e.ticker for e in queue.carried} == {"A", "B", "C", "D", "E"}


def test_urgency_overtakes_and_the_queue_is_re_derived_not_consumed():
    """§4B.5 / RA-121 — ★ *nothing is "already scheduled" in a way that resists
    new evidence.* The mechanics are arithmetic; the priority is D-01's."""
    day = AS_OF - timedelta(days=1)
    entries = [QueueEntry("AAA", last_relayed_on=None, queued_since=day),
               QueueEntry("MU", last_relayed_on=AS_OF, queued_since=day)]
    plain = derive_queue(entries, as_of=AS_OF, per_day=1).today
    assert plain[0].ticker == "AAA"
    urgent = derive_queue(entries, as_of=AS_OF, per_day=1,
                          urgent=["MU"]).today
    assert urgent[0].ticker == "MU"
    assert entries[0].reason == ROTATION


def test_ac_1_82_the_daily_report_carries_overdue_and_stale_as_separate_counts():
    """AC-1.82 / RA-128, RP-49 — ⚠ *not yet run* and *no longer trusted* are
    different states, and **collapsing them hides the moment one became the
    other.**"""
    from src.reporting.render.relay_queue import (
        assert_does_not_chase, render_relay_queue,
    )

    entries = [QueueEntry("MU", last_relayed_on=None,
                          queued_since=AS_OF - timedelta(days=9)),
               QueueEntry("NVDA", last_relayed_on=AS_OF, queued_since=AS_OF)]
    queue = derive_queue(entries, as_of=AS_OF, per_day=1, stale_tickers=["MU"])
    obj = queue.to_json_obj()
    assert obj["counts"]["overdue"] == 1 and obj["counts"]["stale"] == 1
    assert set(obj["counts"]) == {"queued", "returned", "overdue", "stale"}

    text = render_relay_queue(queue)
    assert "overdue" in text and "stale" in text
    assert "overdue = not yet run" in text
    assert_does_not_chase(text)


def test_the_relay_queue_block_may_not_chase():
    """RP-49 / RA-127 — the system reports; it does not chase."""
    from src.shared.errors import PipelineError
    from src.reporting.render.relay_queue import assert_does_not_chase

    with pytest.raises(PipelineError, match="does not chase"):
        assert_does_not_chase("RELAY QUEUE\n  MU is overdue! Please run it.")
