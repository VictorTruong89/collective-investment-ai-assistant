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
    ytd = f"{RUN}/{CALL}#seg.revenue|CNBU|2024-08-30:2025-05-29"
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
    with pytest.raises(UnresolvableCase, match="share one identity"):
        recorded_response(f2_payload_reader(tmp_path))(ref)


def test_dx_25_a_bare_ref_still_compares_the_whole_response(tmp_path):
    """★ Unchanged for single-item blocks — the selector is opt-in."""
    _record(tmp_path, RESPONSE)
    report = run_regression([_case(RESPONSE)],
                            recorded_response(f2_payload_reader(tmp_path)))
    assert report.verdict == "PASS"


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
