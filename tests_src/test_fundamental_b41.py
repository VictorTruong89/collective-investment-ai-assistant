"""D-01 B4.1 — AC-1.1, 1.2, 1.7, 1.7a, 1.10, 1.11, 1.27, 1.27a, 1.38, 1.39, 1.40.

★ **L3 §3A.4's done-when for this slice:** *the same `(ticker, as_of)` yields a
byte-identical `bundle_hash` twice; a call attempted without one raises; a
deliberately degraded response is neither persisted nor rendered.*

Tier: data contract + invariant/property + unit (constitution §4). Hermetic —
the gateway's transport is injected, so no test here reaches a model.
"""

from __future__ import annotations

import ast
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from src.fundamental import (
    AnalysisGateway, AnalysisRun, AnalysisRunLog, BundleInconsistentError,
    BundleNotPinnedError, ConversationalStateError, DegradedCallError, EvidenceBundle,
    PromptDriftError, PromptRegistry, assemble, block, computed, content_hash, filing,
    news, prior_thesis, profile,
)
from src.shared.config import Config
from src.shared.errors import TransportError
from src.shared.llm.gateway import Gateway, Tier

AS_OF = date(2026, 8, 23)
RUN_ID = "run-b41"

CONFIG = {
    "llm.deep.model_id": "claude-opus-5",
    "llm.deep.effort": "high",
    "llm.deep.thinking_mode": "adaptive",
    "llm.cheap.model_id": "claude-haiku-4-5-20251001",
    "llm.cheap.temperature": 0.0,
    "llm.budget.usd_per_run": 5.0,
    "llm.pricing.claude-opus-5.input_per_mtok": 5.0,
    "llm.pricing.claude-opus-5.output_per_mtok": 25.0,
}


#: The real `Config`, not a shim — CF-4 immutability and CF-1's raise-on-missing
#: are part of what the seam runs against.
def cfg():
    return Config(CONFIG, sources=("<test>",))


def parts():
    return [
        filing("0000-1", "Gross margin was 55.4% in the quarter."),
        news("fmp", "n1", date(2026, 8, 20), "Analysts raised targets."),
        computed("b3_minimal", 1, "fair_value_band=[380,445]"),
        profile(AS_OF, "Sector: Information Technology"),
    ]


def bundle(**kw):
    return assemble(ticker=kw.pop("ticker", "NVDA"), as_of=kw.pop("as_of", AS_OF),
                    parts=kw.pop("parts", parts()))


def registry(**kw):
    return PromptRegistry([
        block("J-09", "v1", "judgement", "Assess the moat.",
              options=("widening", "stable", "eroding")),
        block("J-04", "v1", "judgement", "Assess the business, blind.", view="blind"),
        block("E-01", "v1", "extraction", "Extract the stated FY guidance."),
    ], **kw)


def transport_ok(request):
    return {"text": '{"verdict": "BUY"}', "tokens_in": 1200, "tokens_out": 300,
            "stop_reason": "end_turn"}


def seam(transport=transport_ok, **kw):
    gw = Gateway(cfg(), transport=transport)
    return AnalysisGateway(gw, registry(**kw))


# --------------------------------------------------------------------------- #
# AC-1.2 — the hash
# --------------------------------------------------------------------------- #

def test_ac_1_2_same_ticker_and_as_of_give_the_same_bundle_hash():
    """AC-1.2 — RA-4. ★ B4.1's done-when, first clause.

    ```
    NOTHING IN §7 IS MEASURABLE IF THE INPUTS MOVE.
    ```
    """
    assert bundle().bundle_hash == bundle().bundle_hash


def test_ac_1_2_the_hash_is_independent_of_part_arrival_order():
    """RA-4 — determinism cannot depend on the order D-07 happened to answer in."""
    forward, reversed_ = parts(), list(reversed(parts()))
    assert (assemble(ticker="NVDA", as_of=AS_OF, parts=forward).bundle_hash
            == assemble(ticker="NVDA", as_of=AS_OF, parts=reversed_).bundle_hash)


def test_ac_1_2_a_different_as_of_or_content_gives_a_different_hash():
    """RA-2 — *two runs with different hashes are not comparable*, so the hash
    must actually move when the evidence does."""
    base = bundle().bundle_hash
    earlier = date(2026, 8, 22)
    # ⚠ Re-dated deliberately: a bundle at an earlier as_of whose parts are still
    # pinned to the later one is an RA-3 violation, not a hash difference — the
    # first draft of this test tripped that, which is the check working.
    earlier_parts = [filing("0000-1", "Gross margin was 55.4% in the quarter."),
                     profile(earlier, "Sector: Information Technology")]
    assert assemble(ticker="NVDA", as_of=earlier,
                    parts=earlier_parts).bundle_hash != base
    edited = parts()
    edited[0] = filing("0000-1", "Gross margin was 51.1% in the quarter.")
    assert bundle(parts=edited).bundle_hash != base, "same pin, changed text"


def test_a_part_with_no_stated_pin_cannot_enter_a_bundle():
    """RA-2 — *a part with no stated pin can change without the hash noticing.*"""
    from src.fundamental import BundlePart
    with pytest.raises(ValueError, match="missing pin field"):
        BundlePart("filing", {}, "text")
    with pytest.raises(ValueError, match="unknown bundle part kind"):
        BundlePart("vibes", {"accession_id": "x"}, "text")


def test_ra_3_a_bundle_may_not_mix_a_fresh_input_with_a_stale_one():
    """RA-3 — ★ **INV-1 applied to the input set rather than to a query.**

    D-07 guarantees each part was knowable at its own as_of; only assembly can
    guarantee they were all knowable at the *same* one.
    """
    future = [filing("0000-1", "x"), news("fmp", "n2", date(2026, 9, 1), "later")]
    with pytest.raises(BundleInconsistentError, match="pinned to two"):
        assemble(ticker="NVDA", as_of=AS_OF, parts=future)


def test_assemble_requires_an_explicit_as_of():
    """DE-6.4's rule one domain out — *a bundle pinned to 'now' is pinned to nothing.*"""
    with pytest.raises(BundleInconsistentError, match="explicit as_of"):
        assemble(ticker="NVDA", parts=parts())


def test_an_empty_bundle_is_refused():
    """RA-1's letter, defeated — *a call with nothing to read produces a judgement
    from the prompt alone.*"""
    with pytest.raises(ValueError, match="empty EvidenceBundle"):
        assemble(ticker="NVDA", as_of=AS_OF, parts=[])


def test_ra_14_a_blind_view_is_a_new_bundle_with_a_recorded_parent():
    """RA-14 — the anchor-stripped view, and it is a *bundle*, not a flag.

    ⚠ A `blind: bool` would let one hash stand for two different things the model
    saw, and RM-1's whole premise is that a hash identifies **what was read**.
    """
    full = bundle()
    blind = full.redact()
    assert blind.bundle_hash != full.bundle_hash
    assert blind.derived_from == full.bundle_hash
    assert blind.of_kind("computed") == (), "price and valuation withheld"
    assert full.of_kind("computed"), "…and still present on the full view"


# --------------------------------------------------------------------------- #
# AC-1.1 — a call without a hashed bundle raises
# --------------------------------------------------------------------------- #

def test_ac_1_1_a_call_without_a_hashed_bundle_raises():
    """AC-1.1 — RA-1/RA-2. ★ B4.1's done-when, second clause."""
    g = seam()
    for bad in ({"ticker": "NVDA"}, "NVDA", None, 42):
        with pytest.raises(BundleNotPinnedError, match="EvidenceBundle"):
            g.call(prompt_name="J-09", prompt_version="v1", bundle=bad, run_id=RUN_ID)


def test_ac_1_1_the_bundle_and_the_prompt_view_must_agree():
    """RA-14 — checked both ways.

    A blind prompt handed the full bundle has lost the anchor-stripping; a
    full-view prompt handed a redacted one is reasoning about a valuation it
    cannot see and would say so confidently.
    """
    g = seam()
    with pytest.raises(BundleNotPinnedError, match="view="):
        g.call(prompt_name="J-04", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)
    ok = g.call(prompt_name="J-04", prompt_version="v1",
                bundle=bundle().redact(), run_id=RUN_ID)
    assert ok.run.outcome == "ok"


# --------------------------------------------------------------------------- #
# AC-1.10 — alignment before any call
# --------------------------------------------------------------------------- #

def test_ac_1_10_prompt_drift_raises_before_any_call_is_made():
    """AC-1.10 — INV-9, RA-13, GW-12/13.

    ```
    A drifted prompt is an UNVERSIONED CHANGE TO THE ANALYTICAL METHOD, and it
    invalidates every baseline in §7.4.
    ```

    ★ *Before* is the load-bearing word: the assertion is that the transport was
    never reached, not merely that an error was raised.
    """
    sent = []

    def recording_transport(request):
        sent.append(request)
        return transport_ok(request)

    g = seam(recording_transport)
    drifted = g._registry.get("J-09", "v1")
    object.__setattr__(drifted, "text", "Assess the moat, but be optimistic.")

    with pytest.raises(PromptDriftError, match="drifted"):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)
    assert sent == [], "★ the call must not have left the process"


def test_ac_1_10_check_all_aborts_the_run_before_step_1():
    """§4A.2 step 0 — ⚠ checking at the call site lets a run reach step 8 having
    already spent deep-tier tokens on steps 2-7."""
    reg = registry()
    reg.check_all()
    victim = reg.get("E-01", "v1")
    object.__setattr__(victim, "text", "Extract everything.")
    with pytest.raises(PromptDriftError):
        reg.check_all()


def test_an_unregistered_prompt_or_version_cannot_be_called():
    """GW-14 — there is no unversioned call path."""
    g = seam()
    with pytest.raises(PromptDriftError):
        g.call(prompt_name="J-09", prompt_version="v2", bundle=bundle(), run_id=RUN_ID)
    with pytest.raises(PromptDriftError):
        g.call(prompt_name="J-99", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)


def test_republishing_a_prompt_version_with_different_content_raises():
    """The FE-2 argument, applied to prompts: *a version that can mean two things
    makes every baseline recorded against it a statement about an unknown.*"""
    reg = registry()
    with pytest.raises(PromptDriftError):
        reg.register(block("J-09", "v1", "judgement", "Assess the moat differently."))


def test_alignment_hashing_does_not_normalise_whitespace():
    """⚠ Deliberate. *"It was only formatting"* is precisely the edit that slips a
    method change past a version bump."""
    assert content_hash("Assess the moat.") != content_hash("Assess  the moat.")


# --------------------------------------------------------------------------- #
# AC-1.11 — no conversational state
# --------------------------------------------------------------------------- #

def test_ac_1_11_no_call_carries_conversational_state():
    """AC-1.11 — RA-12.

    ★ *Multi-turn accumulates path dependence, which converts a stochastic answer
    into a **stubborn** one — worse, because it looks stable.*

    The `extra_context` argument exists in order to be refused: a seam with no
    such parameter is silently satisfied by a caller who concatenates history
    into the payload instead.
    """
    g = seam()
    with pytest.raises(ConversationalStateError, match="fresh context"):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=bundle(),
               run_id=RUN_ID, extra_context=[{"role": "assistant", "content": "earlier"}])


def test_ac_1_11_the_payload_is_rebuilt_from_scratch_every_call():
    """RA-12, structurally — there is no accumulating context object to forget
    to clear."""
    seen = []

    def capture(request):
        seen.append(request)
        return transport_ok(request)

    g = seam(capture)
    b = bundle()
    for _ in range(3):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=b, run_id=RUN_ID)
    payloads = [s["payload"] for s in seen]
    assert all(set(p) == {"prompt", "options", "bundle"} for p in payloads)
    assert all(p["bundle"] == payloads[0]["bundle"] for p in payloads)


def test_ra_17_option_order_is_randomised_per_call_and_recorded():
    """RA-17 / AC-1.7 — ⚠ **per call, not per stage.**

    *A stage-level permutation would correlate the position bias across the very
    dimensions RM-2 compares.*
    """
    g = seam()
    b = bundle()
    perms = {g.call(prompt_name="J-09", prompt_version="v1", bundle=b,
                    run_id=RUN_ID).run.option_permutation for _ in range(12)}
    assert len(perms) > 1, "the permutation varies across calls"
    assert all(sorted(p) == ["eroding", "stable", "widening"] for p in perms)


# --------------------------------------------------------------------------- #
# AC-1.7 / AC-1.7a — the AnalysisRun
# --------------------------------------------------------------------------- #

def test_ac_1_7_every_analysisrun_records_the_reproducibility_fields():
    """AC-1.7 — RA-11, RA-17, AP-6. *A parameter that is not recorded cannot be
    held responsible.*"""
    result = seam().call(prompt_name="J-09", prompt_version="v1",
                         bundle=bundle(), run_id=RUN_ID)
    obj = result.run.to_json_obj()
    for key in ("run_id", "ticker", "as_of", "bundle_hash", "prompt_name",
                "prompt_version", "model_id", "decoding", "option_permutation",
                "started_at", "tokens_in", "tokens_out", "attempts", "outcome"):
        assert key in obj, key
    assert obj["bundle_hash"] == bundle().bundle_hash


def test_ac_1_7a_decoding_is_the_object_and_carries_the_deep_tier_effort():
    """AC-1.7a — ★★ RA-129, the defect this slice found.

    CT-1.2 carried a **flat `temperature`** — the shape CT-0.1 was reshaped away
    from — and **no `effort` at all**, while §6 puts both of D-01's call kinds on
    the deep tier where `effort` is the only control that exists (GW-8a).
    """
    run = seam().call(prompt_name="J-09", prompt_version="v1", bundle=bundle(),
                      run_id=RUN_ID).run
    assert isinstance(run.decoding, dict)
    assert run.decoding["control"] == "effort"
    assert run.effort == "high", "the deep tier's only knob, and it is recorded"
    assert run.decoding["temperature"] is None, "★ 'not settable', never 'forgotten'"

    with pytest.raises(ValueError, match="flat temperature"):
        AnalysisRun(run_id="r", ticker="NVDA", as_of=AS_OF, bundle_hash="sha256:x",
                    prompt_name="J", prompt_version="v1", model_id="m",
                    decoding=0.0, option_permutation=(),
                    started_at=datetime.now(timezone.utc), tokens_in=1, tokens_out=1,
                    attempts=1, outcome="ok")


def test_the_run_record_has_no_partial_outcome():
    """GW-22 / RA-64 — *both card incidents came from treating one as a success.*"""
    from src.fundamental import OUTCOMES
    assert "partial" not in OUTCOMES
    with pytest.raises(ValueError, match="no 'partial'"):
        AnalysisRun(run_id="r", ticker="NVDA", as_of=AS_OF, bundle_hash="sha256:x",
                    prompt_name="J", prompt_version="v1", model_id="m",
                    decoding={"control": "effort"}, option_permutation=(),
                    started_at=datetime.now(timezone.utc), tokens_in=1, tokens_out=1,
                    attempts=1, outcome="partial")


def test_runs_are_grouped_by_bundle_hash_for_rm_1():
    """RA-2 — *two runs with the same hash are comparable; two with different
    hashes are not*, so this is the only legitimate grouping."""
    g = seam()
    a, b = bundle(), bundle(ticker="MU")
    for _ in range(3):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=a, run_id=RUN_ID)
    g.call(prompt_name="J-09", prompt_version="v1", bundle=b, run_id=RUN_ID)
    assert len(g.log.for_bundle(a.bundle_hash)) == 3
    assert len(g.log.for_bundle(b.bundle_hash)) == 1


# --------------------------------------------------------------------------- #
# AC-1.27 / AC-1.27a — degraded handling
# --------------------------------------------------------------------------- #

def test_ac_1_27_a_degraded_call_is_never_returned_as_analysis():
    """AC-1.27 — ★ B4.1's done-when, third clause. RA-29, P5, DC-3, the D-15 regression.

    ```
    ✗ emit a partial Thesis    a verdict with no stop and no targets IS D-15
    ✗ fall back to the prior one
    ✗ vanish from the slate
    ```
    """
    def truncating(request):
        return {"text": "The moat is", "tokens_in": 900, "tokens_out": 8000,
                "stop_reason": "max_tokens"}

    g = seam(truncating)
    with pytest.raises(DegradedCallError, match="never rendered"):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)


def test_ac_1_27a_but_the_failure_IS_recorded():
    """AC-1.27a — ★★ RA-130, the reading hazard this slice resolved.

    ⚠ AC-1.27 says *never persisted*; RA-111 says the record must distinguish
    *"did not run"* from *"ran and failed"*. Read together, an implementer
    suppresses the record and destroys exactly what RA-111 exists for.

    **Record that it failed; never record what it produced.**
    """
    def truncating(request):
        return {"text": "The moat is", "tokens_in": 900, "tokens_out": 8000,
                "stop_reason": "max_tokens"}

    g = seam(truncating)
    with pytest.raises(DegradedCallError):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)

    assert len(g.log.failures) == 1
    failed = g.log.failures[0]
    assert failed.outcome == "truncated" and not failed.succeeded
    assert failed.bundle_hash == bundle().bundle_hash, "keyed to what was read"
    assert failed.tokens_out == 0, "★ no output is recorded — only that it failed"
    assert "The moat is" not in failed.to_json_obj()["detail"]


def test_a_transport_failure_is_recorded_with_its_own_outcome():
    """CT-0.1's enum — the failure MODE survives, so a flaky run is
    distinguishable from a refusing one."""
    def exploding(request):
        raise TransportError("connection reset")

    g = seam(exploding)
    with pytest.raises(DegradedCallError):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)
    assert g.log.failures[0].outcome == "transport_failed"


def test_a_drift_failure_is_not_recorded_as_a_call_that_ran():
    """★ Alignment blocks BEFORE the call, so there is no call to record.

    ⚠ The distinction matters for RA-111: a drift-blocked prompt did not run, and
    recording it as a failed call would say it did.
    """
    g = seam()
    object.__setattr__(g._registry.get("J-09", "v1"), "text", "changed")
    with pytest.raises(PromptDriftError):
        g.call(prompt_name="J-09", prompt_version="v1", bundle=bundle(), run_id=RUN_ID)
    assert g.log.runs == ()


# --------------------------------------------------------------------------- #
# AC-1.38 / 1.39 / 1.40 — independence and boundary
# --------------------------------------------------------------------------- #

def test_ac_1_38_no_module_outside_src_fundamental_imports_the_gateway():
    """AC-1.38 — ST-5, RA-44, grep-checkable in CI."""
    from tests_src.architecture import scan, st_5
    assert st_5(scan()) == []


def test_ac_1_38_and_within_d01_exactly_one_file_imports_it():
    """★ Narrower than ST-5 requires, and deliberately so.

    ST-5 is checked by a grep over twelve domains; this makes the same rule
    checkable by reading one file.
    """
    importers = [
        str(p) for p in sorted(Path("src/fundamental").rglob("*.py"))
        if "src.shared.llm" in p.read_text(encoding="utf-8")
    ]
    assert importers == ["src/fundamental/prompts/call.py"], importers


def test_ac_1_39_src_fundamental_imports_nothing_from_d03_or_d04():
    """AC-1.39 — INV-014, RA-46. ★ `rank_score` is a forbidden input to D-01."""
    from tests_src.architecture import _hits, scan
    assert _hits(scan(), importer_prefixes=("src/fundamental/",),
                 target_prefixes=("src.quant", "src.models")) == []


def test_ac_1_40_no_arithmetic_in_d01_that_d02_exposes():
    """AC-1.40 — RA-45, P2, AP-5. *A ratio computed in a prompt is a defect twice
    over — undeterministic and duplicated.*

    Checked structurally: D-01 may hash, sort and shuffle; it may not compute a
    ratio, a mean or a growth rate over market or fundamental data.
    """
    forbidden = {"mean", "std", "median", "pct_change", "corr", "var", "rolling"}
    for path in sorted(Path("src/fundamental").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden, (
                    f"{path}:{node.lineno} calls .{node.func.attr}() — that is D-02's "
                    f"arithmetic, and a second definition is the one nobody tests "
                    f"(RA-45, FE-4)"
                )


def test_d01_never_imports_d12_either():
    """ST-10 — a composed verdict returning to an analyst seat is INV-014
    laundered through a third party and a time lag."""
    from tests_src.architecture import scan, st_10
    assert st_10(scan()) == []
