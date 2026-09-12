"""F5 `AC-5.7` / `D5` · `DX-21` — `input_ref` resolves to a recorded response.

★ Before this, `run_regression`'s `replay_response` was supplied only by fakes,
so a golden case could be written and never run.
"""

from __future__ import annotations

import pytest

from src.evaluation.golden.models import GoldenCase
from src.evaluation.regression.replay import UnresolvableCase, recorded_response
from src.evaluation.regression.run import run_regression
from src.orchestration.trace.models import ExternalCall
from src.orchestration.trace.store import TraceStore
from tools.f2_payload_reader import f2_payload_reader

RUN, CALL = "run-1", "call-1"
RESPONSE = {"evidence_id": "seg.revenue", "value": "1,242"}


def _record(root, response=RESPONSE, run_id=RUN, call_id=CALL):
    store = TraceStore(root, run_id)
    store.append(ExternalCall(run_id=run_id, step_id="s1", call_id=call_id,
                              kind="llm", request={"p": "E-01"}, response=response))
    store.close()
    return store


def _case(expected, input_ref=f"{RUN}/{CALL}"):  # noqa: D103
    return GoldenCase(case_id="c1", kind="extraction", input_ref=input_ref,
                      expected=expected, source="10-Q p.4",
                      established_at="2026-09-05", established_by="Victor")


def test_dx_21_a_case_resolves_to_the_recorded_response(tmp_path):
    """DX-21 — the wire exists: input_ref → recorded payload → comparison."""
    _record(tmp_path)
    report = run_regression([_case(RESPONSE)], recorded_response(f2_payload_reader(tmp_path)))
    assert report.verdict == "PASS"


def test_dx_21_a_changed_reading_of_the_SAME_document_reds(tmp_path):
    """★★ The whole purpose. ⚠ The drifted response is well-formed and would
    pass `x01_verify_extraction` — only the golden case knows it changed."""
    _record(tmp_path, {"evidence_id": "seg.revenue", "value": "3,430"})
    report = run_regression([_case(RESPONSE)], recorded_response(f2_payload_reader(tmp_path)))
    assert report.verdict == "FAIL"
    (d,) = report.diverged
    assert d["produced"]["value"] == "3,430"
    assert d["established_by"] == "Victor", (
        "a divergence must name who established the expectation — the reader "
        "needs to know who to ask, not just that the numbers differ"
    )


def test_dx_21_an_expired_payload_is_loud_not_a_pass(tmp_path):
    """⚠⚠ F2 D2 expires payloads. A case whose evidence is gone is
    UNREPLAYABLE — reporting it as pass OR fail would state something untrue."""
    store = _record(tmp_path)
    store.expire_payloads("2026-09-05")
    with pytest.raises(UnresolvableCase, match="expired"):
        recorded_response(f2_payload_reader(tmp_path))(f"{RUN}/{CALL}")


def test_dx_21_a_missing_recording_is_loud_not_a_pass(tmp_path):
    """⚠ P5 — the tempting alternative is skipping the case, which shrinks the
    baseline and still reports green (the DX-20 failure, one layer up)."""
    _record(tmp_path)
    with pytest.raises(UnresolvableCase):
        recorded_response(f2_payload_reader(tmp_path))(f"{RUN}/no-such-call")


@pytest.mark.parametrize("bad", ["", "bare-id", "a/b/c", "has space/x"])
def test_dx_21_a_malformed_input_ref_is_refused(tmp_path, bad):
    """`<run_id>/<call_id>`, exactly. ⚠ A bare id is ambiguous once a second
    run records a call under the same name."""
    with pytest.raises(UnresolvableCase, match="run_id"):
        recorded_response(f2_payload_reader(tmp_path))(bad)


# ── DX-25 · one call returns many items; one case pins one ─────────────────

def _e01_call(root):
    """A realistic E-01 recording: every segment row, BOTH columns."""
    from src.fundamental.filings.extract import item

    def mk(v, qual, start, cum=False):
        q = f"{qual} {v}"
        return item("seg.revenue", value=v, unit="millions of USD", quote=q,
                    accession_id="acc", offset=(0, len(q)), period_start=start,
                    period_end="2025-05-29", cumulative_ytd=cum,
                    qualifier=qual).to_json_obj()

    rows = [mk("5,069", "CNBU", "2025-02-28"), mk("1,451", "SBU", "2025-02-28"),
            mk("14,028", "CNBU", "2024-08-30", True),
            mk("4,574", "SBU", "2024-08-30", True)]
    _record(root, rows)
    return rows


def test_dx_25_a_selector_picks_the_one_item_the_case_is_about(tmp_path):
    """★★ F5 case 1 — CNBU, discrete quarter — out of a 4-item response."""
    rows = _e01_call(tmp_path)
    ref = f"{RUN}/{CALL}#seg.revenue|CNBU|2025-02-28:2025-05-29"
    report = run_regression([_case(rows[0], input_ref=ref)],
                            recorded_response(f2_payload_reader(tmp_path)))
    assert report.verdict == "PASS"


def test_dx_25_cases_1_and_2_differ_only_by_period_and_both_resolve(tmp_path):
    """★★ The pair MP-18's `period` component exists for. Same evidence_id,
    same qualifier, different column of the same row."""
    _e01_call(tmp_path)
    reader = recorded_response(f2_payload_reader(tmp_path))
    discrete = f"{RUN}/{CALL}#seg.revenue|CNBU|2025-02-28:2025-05-29"
    # ⚠ `DX-68` — the `|ytd` flag is now REQUIRED on a cumulative row.
    ytd = f"{RUN}/{CALL}#seg.revenue|CNBU|2024-08-30:2025-05-29|ytd"
    assert reader(discrete)["value"] == "5,069"
    assert reader(ytd)["value"] == "14,028"
    assert reader(ytd)["tags"] == ["cumulative_ytd"]


def test_dx_25_a_vanished_reading_raises_rather_than_passing(tmp_path):
    """⚠⚠ If the item a case pins is gone, that IS the regression. Reporting
    it as a missing fixture (or a pass) would hide the thing being measured."""
    _e01_call(tmp_path)
    gone = f"{RUN}/{CALL}#seg.revenue|MBU|2025-02-28:2025-05-29"
    with pytest.raises(UnresolvableCase, match="GONE"):
        recorded_response(f2_payload_reader(tmp_path))(gone)


def test_dx_25_an_ambiguous_selector_raises_rather_than_taking_the_first(tmp_path):
    """⚠ Two items on one identity is exactly what MP-18 forbids. Silently
    taking hits[0] would conceal it."""
    from src.fundamental.filings.extract import item
    q = "dup"
    dup = item("seg.revenue", value="1", unit="u", quote=q, accession_id="a",
               offset=(0, len(q)), period_start="2025-02-28",
               period_end="2025-05-29", qualifier="CNBU").to_json_obj()
    _record(tmp_path, [dup, dict(dup, value="2")])
    ref = f"{RUN}/{CALL}#seg.revenue|CNBU|2025-02-28:2025-05-29"
    # ⚠ `DX-74` — "one SELECTOR", not "one identity". The distinction is the
    #   finding: for a non-figure the two DO have different identities (the
    #   span), and it was the selector that could not say so.
    with pytest.raises(UnresolvableCase, match="share one selector"):
        recorded_response(f2_payload_reader(tmp_path))(ref)


def test_dx_25_a_bare_ref_still_compares_the_whole_response(tmp_path):
    """★ Unchanged for single-item blocks — the selector is opt-in."""
    _record(tmp_path, RESPONSE)
    report = run_regression([_case(RESPONSE)],
                            recorded_response(f2_payload_reader(tmp_path)))
    assert report.verdict == "PASS"


# ── DX-68 · the post-envelope shape: no period_start, only the ytd flag ────

def _e01_call_no_start(root):
    """★★ The recording the shared prompt envelope actually produces.

    ⚠ `S-2` item 3 says *"Do not compute… record a data gap"*, and a segment
    table states only the period END — so the model stopped reporting
    `period_start`. Measured on `run-2026-09-11T065539-mu-e01`: **65 of 65
    items carried `period_start: None`**, and `period` alone no longer told the
    discrete column from the year-to-date one.
    """
    from src.fundamental.filings.extract import item

    def mk(v, qual, cum=False):
        q = f"{qual} {v}"
        return item("seg.revenue", value=v, unit="millions of USD", quote=q,
                    accession_id="acc", offset=(0, len(q)), period_start=None,
                    period_end="2025-05-29", cumulative_ytd=cum,
                    qualifier=qual).to_json_obj()

    rows = [mk("5,069", "CNBU"), mk("14,028", "CNBU", True)]
    _record(root, rows)
    return rows


def test_dx_68_ytd_separates_two_rows_that_period_no_longer_separates(tmp_path):
    """★★★ `DX-68` — the pair that collapsed. Same evidence_id, same qualifier,
    same (start-less) period; the ONLY thing left distinguishing them is the
    tag the model records rather than derives."""
    _e01_call_no_start(tmp_path)
    reader = recorded_response(f2_payload_reader(tmp_path))
    assert reader(f"{RUN}/{CALL}#seg.revenue|CNBU|:2025-05-29")["value"] == "5,069"
    assert reader(f"{RUN}/{CALL}#seg.revenue|CNBU|:2025-05-29|ytd")["value"] == "14,028"


def test_dx_68_an_absent_flag_asserts_discrete_rather_than_dont_care(tmp_path):
    """⚠⚠ The failure this closes. Were the flag a *don't care*, the unflagged
    ref would match BOTH rows — which is the 20-duplicate state `MP-18` exists
    to forbid, arrived at through the selector instead of the extractor."""
    _e01_call_no_start(tmp_path)
    hit = recorded_response(f2_payload_reader(tmp_path))(
        f"{RUN}/{CALL}#seg.revenue|CNBU|:2025-05-29")
    assert hit["tags"] == []


def test_dx_68_a_ytd_ref_whose_row_is_gone_raises(tmp_path):
    """★ `DX-20`'s rule reaching the new component: a vanished reading is the
    regression, never a skip."""
    from src.fundamental.filings.extract import item
    q = "CNBU 5,069"
    only_discrete = item("seg.revenue", value="5,069", unit="u", quote=q,
                         accession_id="acc", offset=(0, len(q)),
                         period_start=None, period_end="2025-05-29",
                         qualifier="CNBU").to_json_obj()
    _record(tmp_path, [only_discrete])
    with pytest.raises(UnresolvableCase, match="cumulative_ytd"):
        recorded_response(f2_payload_reader(tmp_path))(
            f"{RUN}/{CALL}#seg.revenue|CNBU|:2025-05-29|ytd")


def test_dx_68_the_selector_tag_has_not_drifted_from_the_domain_constant():
    """⚠ `replay.py` duplicates the tag as a literal because it reaches no
    domain module (`MP-5`). ★ A test may import both, so the duplication is
    checked rather than merely commented."""
    from src.evaluation.regression.replay import CUMULATIVE_YTD_TAG
    from src.fundamental.filings.models import CUMULATIVE_YTD
    assert CUMULATIVE_YTD_TAG == CUMULATIVE_YTD


def test_dx_68_a_discrete_ref_is_unchanged_but_a_ytd_one_must_gain_the_flag(tmp_path):
    """⚠⚠ `DX-68` is **not** backward compatible, and that is deliberate.

    A pre-`DX-68` ref to a *discrete* row still resolves. A pre-`DX-68` ref to a
    *cumulative* row now **raises**, because the absent flag asserts "discrete".
    ★ That is the right direction to break in: it is loud, it names the case,
    and it cannot be mistaken for a pass. The silent alternative — treating an
    absent flag as *don't care* — would have matched both rows and reproduced
    the very ambiguity this component was added to remove.
    """
    rows = _e01_call(tmp_path)
    reader = recorded_response(f2_payload_reader(tmp_path))
    assert reader(f"{RUN}/{CALL}#seg.revenue|CNBU|2025-02-28:2025-05-29") == rows[0]
    with pytest.raises(UnresolvableCase, match="discrete"):
        reader(f"{RUN}/{CALL}#seg.revenue|CNBU|2024-08-30:2025-05-29")
    assert reader(f"{RUN}/{CALL}#seg.revenue|CNBU|2024-08-30:2025-05-29|ytd") == rows[2]


def test_dx_26_a_trace_cannot_be_closed_twice(tmp_path):
    """⚠⚠ DX-26 — `AC-2.8` applied to the sentinel.

    Found for real: a `finally: close("SUCCESS")` plus an error-path
    `close("FAILED")` wrote SUCCESS, SUCCESS, FAILED, SUCCESS into one trace,
    and the last word was SUCCESS for a run that had just failed.
    ★ A trace that can disagree with its own run is worse than no trace.
    """
    from src.orchestration.trace.errors import TraceImmutableError

    store = TraceStore(tmp_path, "r-once")
    store.close("FAILED")
    assert store.status() == "FAILED"
    with pytest.raises(TraceImmutableError, match="already closed"):
        store.close("SUCCESS")
    assert store.status() == "FAILED", "the first, true outcome must survive"


# ── C12 · the trace must be able to state what a call cost ─────────────────

def test_c12_cost_is_recorded_on_the_trace_record(tmp_path):
    """⚠⚠ Before this, `cost_usd` was null on EVERY record: `traced_transport`
    wraps the transport, so it saw tokens and never the gateway's cost. After
    ~$7 of live runs the trace could not answer "what did this cost?".

    ★★ A run whose cost nobody can state is a run nobody can budget for.
    """
    from src.orchestration.trace.wire import traced_transport

    store = TraceStore(tmp_path, "r-cost")
    priced = traced_transport(
        lambda req: {"text": "ok", "tokens_in": 1000, "tokens_out": 200},
        store, step_id="s",
        cost_of=lambda model, tok: tok["input"] * 5 / 1e6 + tok["output"] * 25 / 1e6,
    )
    priced({"model": "claude-opus-5", "max_tokens": 8})
    store.close()
    (rec,) = [r for r in store.read_all() if r["type"] == "ExternalCall"]
    assert rec["tokens"] == {"input": 1000, "output": 200}
    assert rec["cost_usd"] == pytest.approx(1000 * 5 / 1e6 + 200 * 25 / 1e6)


def test_c12_an_unpriced_call_records_absent_not_zero(tmp_path):
    """⚠ No pricer ⇒ `cost_usd` is None. A call recorded as FREE is worse than
    one recorded as unpriced — zero is a claim, null is an admission."""
    from src.orchestration.trace.wire import traced_transport

    store = TraceStore(tmp_path, "r-nocost")
    traced_transport(lambda req: {"text": "ok", "tokens_in": 5, "tokens_out": 1},
                     store, step_id="s")({"model": "m", "max_tokens": 8})
    store.close()
    (rec,) = [r for r in store.read_all() if r["type"] == "ExternalCall"]
    assert rec["cost_usd"] is None


def test_a_recording_states_which_prompt_version_produced_it(tmp_path):
    """⚠⚠ `CT-2.2` carried `prompt_version` and nothing ever filled it — every
    recording said `None`.

    ★★ It matters the moment a prompt is versioned (`E-01` v1 → v2): a golden
    case grades a RECORDED call, and without this it cannot tell whether it
    still grades what the repo ships. A suite pinned to a retired prompt
    reports green about the past.
    """
    from src.orchestration.trace.wire import traced_transport

    store = TraceStore(tmp_path, "r-ver")
    traced_transport(lambda req: {"text": "ok", "tokens_in": 1, "tokens_out": 1},
                     store, step_id="extract:E-01",
                     prompt_version="v2")({"model": "m", "max_tokens": 8})
    store.close()
    (rec,) = [r for r in store.read_all() if r["type"] == "ExternalCall"]
    assert rec["prompt_version"] == "v2"


# ── DX-74 · the selector learns the span the identity already carries ────────

def _four_basis_notes(root):
    """★★ The AMD run that broke: 4 narrative items, NO qualifier on any.

    ⚠ Measured on `run-2026-09-11T082118-amd-e01`. The run 82 minutes earlier
    gave each note a qualifier; this one gave none — so `qualifier`, which
    `MP-18` uses as an identity component, is **free text the model invents**.
    """
    from src.fundamental.filings.extract import item

    notes, off = [], 0
    for text in ("All prior period segment data were retrospectively adjusted.",
                 "Neither of the Client and Gaming businesses qualifies.",
                 "In the first quarter the Company reassigned goodwill.",
                 "The three and nine months ended September 27, 2025."):
        notes.append(item("seg.basis_note", value=text, unit=None, quote=text,
                          accession_id="acc", offset=(off, off + len(text)),
                          qualifier="").to_json_obj())
        off += len(text) + 1
    _record(root, notes)
    return notes


def test_dx_74_a_span_picks_one_of_four_otherwise_identical_notes(tmp_path):
    """★★★ The two AMD cases come back. Without the span these four are one
    selector; with it each addresses exactly one item."""
    notes = _four_basis_notes(tmp_path)
    reader = recorded_response(f2_payload_reader(tmp_path))
    for note in notes:
        start, end = note["span"]["offset"]
        ref = f"{RUN}/{CALL}#seg.basis_note||:@{start}:{end}"
        assert reader(ref)["value"] == note["value"]


def test_dx_74_without_the_span_the_four_still_refuse(tmp_path):
    """⚠⚠ The span NARROWS; it does not make ambiguity tolerable. A bare
    selector over four indistinguishable items must still raise — `DX-25`'s
    rule is unchanged, and the error now says what would separate them."""
    _four_basis_notes(tmp_path)
    with pytest.raises(UnresolvableCase, match="share one selector"):
        recorded_response(f2_payload_reader(tmp_path))(f"{RUN}/{CALL}#seg.basis_note||:")


def test_dx_74_the_error_names_the_spans_that_would_disambiguate(tmp_path):
    """★ `CN-10` — an error that names the shortfall beats one that states it.
    ⚠ It reports the spans as a FACT and warns that pinning one on a FIGURE
    would hide a real duplicate rather than resolve it."""
    _four_basis_notes(tmp_path)
    with pytest.raises(UnresolvableCase) as exc:
        recorded_response(f2_payload_reader(tmp_path))(f"{RUN}/{CALL}#seg.basis_note||:")
    assert "their spans are" in str(exc.value)
    assert "FIGURE" in str(exc.value)


def test_dx_74_a_span_that_matches_nothing_raises_rather_than_widening(tmp_path):
    """⚠ `DX-20`'s rule reaching the new component: an over-specified selector
    that matches nothing is a VANISHED reading, never a silent fallback to the
    unpinned match."""
    _four_basis_notes(tmp_path)
    with pytest.raises(UnresolvableCase, match="GONE"):
        recorded_response(f2_payload_reader(tmp_path))(
            f"{RUN}/{CALL}#seg.basis_note||:@9000:9100")


def test_dx_74_pre_existing_refs_are_unaffected(tmp_path):
    """★ Unlike `|ytd`, an absent span is NOT a positive assertion — it cannot
    be, since a figure has no span in its identity at all. Every ref written
    before `DX-74` keeps its exact meaning."""
    rows = _e01_call(tmp_path)
    reader = recorded_response(f2_payload_reader(tmp_path))
    assert reader(f"{RUN}/{CALL}#seg.revenue|CNBU|2025-02-28:2025-05-29") == rows[0]
