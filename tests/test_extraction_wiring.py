"""`DX-23` step 5, verified WITHOUT the network — offsets and token mapping.

⚠⚠ **Why a stub rather than a live call.** Victor authorised the spend, but this
machine has **no Anthropic credentials at all** — no `ANTHROPIC_API_KEY`, no
`ANTHROPIC_AUTH_TOKEN`, no `ant` CLI, no `~/.config/anthropic/`. So the live run
is deferred, and everything that does not require the vendor is pinned here.

★ **What this DOES verify** — the two things named:
  1. `parse_items` computes character offsets that `X-01` accepts, against the
     **real 211,895-char filing**, not a toy string.
  2. `to_transport_result` emits `tokens_in`/`tokens_out`, the names the gateway
     actually reads — the `DX-11` defect class.

⚠ **What it does NOT verify:** that the SDK's real `Message` matches the stub's
shape, and that Opus 5 accepts this request (tool schema, `effort`, adaptive
thinking). Those need one `--live` run. ★ The stub is built from the SDK's
documented shape, so if it is wrong the live run is where that shows.
"""

from __future__ import annotations

import json
import pathlib
import sys
from types import SimpleNamespace

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fundamental.filings.models import CUMULATIVE_YTD  # noqa: E402
from tools.anthropic_transport import to_transport_result  # noqa: E402
from tools.run_extraction_once import (  # noqa: E402
    build_bundle,
    parse_items,
)

#: The real CNBU row, copied out of the fixture at test time (never hardcoded —
#: a hardcoded copy would pass while the fixture drifted underneath it).
FILING_TEXT = (REPO / "tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt").read_text(
    encoding="utf-8"
)


def _cnbu_row() -> str:
    for line in FILING_TEXT.splitlines():
        if line.startswith("CNBU | $ | 5,069"):
            return line
    pytest.fail("the CNBU row is no longer in the fixture — the case is stale")


def _tool_use_message(items, *, tin=53_473, tout=4_211):
    """A stub shaped like the SDK's `Message` for a `tool_use` response."""
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name="record_extractions",
                                 input={"items": items})],
        usage=SimpleNamespace(input_tokens=tin, output_tokens=tout),
        stop_reason="tool_use",
    )


def _call_result(items):
    """What `parse_items` actually receives — a `CallResult`, NOT an SDK Message.

    ⚠⚠ The chain matters and is easy to get wrong: the transport returns the
    tool input as a JSON **string** in `text`; `Gateway.complete` sets
    `parsed = text` when no schema is given (it only calls `schema(text)` if one
    is), so `CallResult.parsed` is that same string. ★ Feeding an SDK `Message`
    here instead — as this test first did — fails with a type error, which is
    how the shape got pinned down rather than assumed.
    """
    text = to_transport_result(_tool_use_message(items))["text"]
    return SimpleNamespace(text=text, parsed=text, run=None)


# ── 1. the token mapping — the DX-11 defect class ──────────────────────────

def test_transport_emits_tokens_in_tokens_out_not_the_sdk_names():
    """⚠⚠ The gateway reads `tokens_in`/`tokens_out`. Passing the SDK's own
    `usage.input_tokens` through under its own name records **0 tokens on every
    call** and destroys cost accounting silently."""
    out = to_transport_result(_tool_use_message([], tin=53_473, tout=4_211))
    assert out["tokens_in"] == 53_473
    assert out["tokens_out"] == 4_211
    assert "input_tokens" not in out and "usage" not in out


def test_transport_returns_the_tool_input_as_the_text_payload():
    """★ MP-5 — the tool call IS the answer; its input is already schema-valid."""
    out = to_transport_result(_tool_use_message([{"evidence_id": "seg.revenue"}]))
    assert json.loads(out["text"])["items"][0]["evidence_id"] == "seg.revenue"
    assert out["stop_reason"] == "tool_use"


def test_transport_falls_back_to_text_when_no_tool_was_called():
    """⚠ A model that answers in prose instead of calling the tool must not
    yield an empty body — GW-22 turns that into UNPARSEABLE, which is right,
    but the text should reach it so the failure names what happened."""
    msg = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="I could not find the table.")],
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
        stop_reason="end_turn",
    )
    assert to_transport_result(msg)["text"].startswith("I could not")


# ── 2. offsets, against the REAL filing ────────────────────────────────────

def test_parse_items_computes_offsets_that_resolve_in_the_real_filing():
    """★★ The offset is arithmetic, not something the model is asked for
    (`AP-5`). This checks it against the actual 211,895-char fixture."""
    row = _cnbu_row()
    items = parse_items(_call_result([{
        "evidence_id": "seg.revenue", "qualifier": "CNBU", "value": "5,069",
        "unit": "millions of USD", "quote": row,
        "period_start": "2025-02-28", "period_end": "2025-05-29",
    }]))
    (it,) = items
    start, end = it.span.start, it.span.end
    assert FILING_TEXT[start:end] == row, "the computed offset does not resolve"
    assert it.qualifier == "CNBU"
    assert it.value in row


def test_parse_items_survives_x01_verification_end_to_end():
    """★★ The whole point: offsets computed here must satisfy the check that
    aborts a real run. Both columns of the CNBU row, as F5 cases 1 and 2."""
    from src.fundamental.claims.verify import x01_verify_extraction

    row = _cnbu_row()
    items = parse_items(_call_result([
        {"evidence_id": "seg.revenue", "qualifier": "CNBU", "value": "5,069",
         "unit": "millions of USD", "quote": row,
         "period_start": "2025-02-28", "period_end": "2025-05-29"},
        {"evidence_id": "seg.revenue", "qualifier": "CNBU", "value": "14,028",
         "unit": "millions of USD", "quote": row, "cumulative_ytd": True,
         "period_start": "2024-08-30", "period_end": "2025-05-29"},
    ]))
    report = x01_verify_extraction(build_bundle(), items)
    assert report is not None
    discrete, cumulative = items
    assert CUMULATIVE_YTD in cumulative.tags
    assert CUMULATIVE_YTD not in discrete.tags
    # ⚠ MP-18 — same id, same qualifier, same quote; only `period` separates them.
    assert discrete.identity != cumulative.identity


def test_parse_items_refuses_a_quote_that_is_not_in_the_filing():
    """⚠ P5 — loud. A fabricated quote fails here with a readable message
    rather than deeper in X-01 with a character offset."""
    with pytest.raises(ValueError, match="not in the bundle"):
        parse_items(_call_result([{
            "evidence_id": "seg.revenue", "value": "9,999",
            "unit": "millions of USD", "quote": "CNBU | $ | 9,999 (invented)",
        }]))


def test_the_transport_does_not_silently_lower_the_requested_max_tokens():
    """⚠⚠ MEASURED: the transport defaulted `max_output` to 16,000 and clamped,
    so a gateway request for 32,000 was sent as 16,000 — and `GW-23` then
    reported "hit max_tokens=32000", a number never sent.

    ★ A clamp that quietly lowers the ask makes every downstream error message
    a lie about what was requested.
    """
    from tools.anthropic_transport import MODEL_MAX_OUTPUT, anthropic_transport
    captured = {}

    class _Stub:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def get_final_message(self):
            return _tool_use_message([])

    class _Msgs:
        def stream(self, **kw):
            captured.update(kw)
            return _Stub()

    class _Client:
        messages = _Msgs()

    import tools.anthropic_transport as mod
    real = mod.anthropic
    mod.anthropic = SimpleNamespace(Anthropic=lambda **kw: _Client())
    try:
        anthropic_transport(tool=None)({"model": "claude-opus-5",
                                        "max_tokens": 32_000, "payload": "x"})
    finally:
        mod.anthropic = real
    assert captured["max_tokens"] == 32_000, "the request was silently lowered"
    assert MODEL_MAX_OUTPUT == 128_000
