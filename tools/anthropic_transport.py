"""The D-00 transport — the one place this repo actually calls Anthropic.

⚠⚠ **Nothing here runs unless someone passes `--live`.** Constructing the
transport is free; only calling it spends.

★ **Wired outside `src/` on purpose**, like `f2_payload_reader.py`: this is a
composition root (`CA-9`). `ST-5` says only the gateway calls an LLM, and this
is the callable the gateway is constructed with — the gateway still owns retry,
budget, truncation and refusal handling (`GW-1`…`GW-23`).

**The contract, frozen by `tests/test_characterization_gateway.py`:**

    in  : {"model", "max_tokens", "payload", and either
           ("effort", "thinking") or ("temperature",)}
    out : {"text", "tokens_in", "tokens_out", "stop_reason"}

⚠ `tokens_in` / `tokens_out` — **not** `usage.input_tokens`. Reading the SDK's
names straight through would record 0 tokens on every call and silently destroy
cost accounting; the characterization test exists because that was assumed once.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import anthropic


def extraction_tool(item_ids: tuple[str, ...]) -> dict:
    """`MP-5` — the output shape is enforced by the API, not by prose.

    ⚠⚠ Both defects this schema has already caused were the same mistake —
    describing a constraint instead of declaring it:

    * `evidence_id` was a free string whose description said *"never invent
      one"*. The model returned **all 56 items tagged `E-01`**, the block id.
      ★ Now an `enum` of the block's actual item ids.
    * There was no `status`, so a genuinely absent figure had nowhere to go and
      the model wrote a PROSE SENTENCE into `value` ("Identifiable assets by
      segment are NOT disclosed…"). `X-01` refused it, correctly. ★★ `MP-7`
      predicted it word for word: *an LLM with no stated way to say "I could
      not" will always find something to say.*
    """
    tool = json.loads(json.dumps(_EXTRACTION_TOOL_TEMPLATE))
    props = tool["input_schema"]["properties"]["items"]["items"]["properties"]
    props["evidence_id"]["enum"] = list(item_ids)
    return tool


#: `MP-5` — extraction output shape is enforced by the API, via tool use with
#: `strict: true`. ⚠ Not by asking for JSON in prose and parsing the reply.
_EXTRACTION_TOOL_TEMPLATE = {
    "name": "record_extractions",
    "description": "Record every extracted item from the filings in the bundle.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    # ⚠⚠ `quote` is REQUIRED for every item, `not_found`
                    # included — measured 2026-09-07: with it optional, the
                    # model returned a FOUND `seg.revenue` carrying no quote at
                    # all, and X-01 then had nothing to check.
                    # ★★ Requiring it on `not_found` too is not a workaround, it
                    # is better evidence: "not disclosed" backed by the sentence
                    # that says so ("We do not identify or report internally our
                    # assets...") is a citation; a bare assertion is not, and
                    # MP-7 asks for *where you looked*.
                    "required": ["evidence_id", "status", "quote"],
                    "properties": {
                        "evidence_id": {
                            "type": "string",
                            # ⚠ `enum` is filled by `extraction_tool()` from the
                            # block's own item ids — NOT described in prose.
                            "description": "Which item from the block's item list this is.",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["found", "not_found"],
                            "description": (
                                "MP-7 — the stated failure output. Use "
                                "'not_found' when the document does not give "
                                "this item, and put where you looked in `note`. "
                                "NEVER write an explanation into `value`."
                            ),
                        },
                        "qualifier": {
                            "type": "string",
                            "description": (
                                "Which ROW this is when one evidence_id yields "
                                "several — the segment name for E-01. NOT part "
                                "of the evidence_id."
                            ),
                        },
                        "value": {
                            "type": "string",
                            "description": (
                                "If the value is a BARE FIGURE, give it without "
                                "a currency symbol — '5,069', not '$5,069' — and "
                                "put the currency in `unit`. Keep the document's "
                                "own scale and its parentheses for negatives, "
                                "e.g. '(9)'. ⚠ If the value is a PHRASE quoted "
                                "from the document, copy it EXACTLY, symbol "
                                "included: 'approximately $14 billion', never "
                                "'approximately 14 billion'. Verbatim always "
                                "wins — a value that cannot be found in its own "
                                "quote is refused. "
                                "FOR A TEXT ITEM (seg.name, seg.basis_note) the "
                                "value must be a VERBATIM SUBSTRING of `quote` — "
                                "copy the words, do NOT summarise or combine two "
                                "sentences. A paraphrase is refused: it cannot be "
                                "checked against the document."
                            ),
                        },
                        "unit": {
                            "type": "string",
                            "description": (
                                "Where the currency and scale go, e.g. "
                                "'millions of USD'. MO-1: a bare value is not "
                                "monetary, so a money figure MUST name its "
                                "currency here."
                            ),
                        },
                        "period_start": {"type": "string", "description": "ISO date, or omit if the document does not give one."},
                        "period_end": {"type": "string", "description": "ISO date."},
                        "cumulative_ytd": {
                            "type": "boolean",
                            "description": (
                                "TRUE if this figure is cumulative year-to-date "
                                "where a discrete period was requested. Return it "
                                "tagged with BOTH period endpoints and do NOT "
                                "subtract to produce the discrete figure."
                            ),
                        },
                        "quote": {
                            "type": "string",
                            "description": (
                                "A VERBATIM span from the document. For a found "
                                "item it must CONTAIN this item's value; for a "
                                "not_found item, quote the passage showing the "
                                "figure is not disclosed. Copy characters exactly."
                            ),
                        },
                        "note": {"type": "string"},
                    },
                },
            }
        },
    },
}


#: Opus 5's documented output ceiling. ⚠ Streaming is required to go near it.
MODEL_MAX_OUTPUT = 128_000


def anthropic_transport(*, tool: dict | None = None,
                        max_output: int = MODEL_MAX_OUTPUT,
                        thinking_display: str | None = None) -> Callable[[dict], dict]:
    """Build the transport. ⚠ The API key is read from the environment by the
    SDK (`ANTHROPIC_API_KEY`, or an `ant auth login` profile) — never passed in,
    never logged, never a CLI argument.
    """
    client = anthropic.Anthropic(
        # ⚠⚠ Brotli 1.0.9 is installed and `httpx2` calls its decompressor as
        # `process(data, output_buffer_limit=...)`, which that version does not
        # accept — so a brotli-encoded response raises `TypeError`, which the
        # SDK re-raises as `APIConnectionError`. ★★ The call SUCCEEDS and is
        # BILLED; only the local decode fails, so the money is spent and the
        # answer is thrown away. Asking for gzip sidesteps it entirely.
        # ✏ The permanent fix is `pip install -U Brotli` (or `brotlicffi`), but
        #   that mutates the shared anaconda base env, so it is Victor's call.
        default_headers={"Accept-Encoding": "gzip"},
        # ⚠⚠ EH-14 — **only orchestration retries.** The SDK's default
        # `max_retries=2` sits UNDER a gateway that already owns retry (GW-17),
        # so a failure is attempted 3x by the SDK inside each gateway attempt.
        # ★ On a 53k-token request that multiplies the bill by three for one
        #   logical call, and the trace records only the gateway's view of it.
        max_retries=0,
    )

    def transport(request: dict) -> dict:
        kwargs: dict = {
            "model": request["model"],
            # ⚠⚠ MEASURED DEFECT, 2026-09-07. This clamped to 16,000 by
            # default, so the gateway asking for 20,000 and then 32,000 silently
            # got 16,000 — and `GW-23` then reported "hit max_tokens=32000",
            # **a number that was never sent**. Two runs and ~$1.56 were spent
            # chasing a ceiling that was not the one in force.
            # ★★ A clamp that quietly lowers the ask makes every downstream
            #    error message a lie about what was requested.
            "max_tokens": min(int(request["max_tokens"]) or max_output, max_output),
            # ★★ `DX-127` — prompt caching. When a request carries `cache_prefix`, the
            #   STABLE evidence goes in its own content block marked `cache_control`, and the
            #   variable part (this call's commits and its instructions) follows. ⚠ Caching is
            #   a PREFIX match: any byte change before the breakpoint invalidates it, which is
            #   why the prefix must be the one thing every call in a stage shares.
            "messages": [{"role": "user", "content": (
                [{"type": "text", "text": str(request["cache_prefix"]),
                  "cache_control": {"type": "ephemeral"}},
                 {"type": "text", "text": str(request["payload"])}]
                if request.get("cache_prefix") else str(request["payload"]))}],
        }
        # ⚠ Opus 5 rejects `temperature` (400) — the gateway's `effort` control
        # path is the supported one. `budget_tokens` is likewise removed.
        if "effort" in request:
            kwargs["thinking"] = {"type": "adaptive"}
            # ★ `DX-96` — a DIAGNOSTIC knob, off by default. Thinking stays ON
            #   (`GW-9c` forbids disabling it); `summarized` only makes it
            #   VISIBLE, so a call that thinks out of budget can say what about.
            if thinking_display:
                kwargs["thinking"]["display"] = thinking_display
            kwargs["output_config"] = {"effort": request["effort"]}
        if tool is not None:
            kwargs["tools"] = [tool]

        # ⚠⚠ STREAMING is required above ~16k max_tokens — a non-streaming
        # request that large risks an HTTP timeout, and this call already runs
        # ~230s. ★ `.get_final_message()` returns the same `Message`, so the
        # mapping below is unchanged.
        #
        # ★★ `DX-96` — the deltas are TALLIED while streaming. ⚠⚠ Without this a
        #   truncated call's recording is `{}` and cannot say whether 20,000
        #   tokens went to THINKING or to a TOOL CALL cut off mid-JSON: the final
        #   message drops thinking text and a partial tool input alike. Two
        #   opposite diagnoses were drawn from that `{}` on 2026-09-13, and
        #   both were inference.
        with client.messages.stream(**kwargs) as stream:
            tally = tally_stream(stream)
            result = to_transport_result(stream.get_final_message())
        return {**result, **tally_fields(tally, result["stop_reason"])}

    return transport


def tally_stream(events) -> dict:
    """★ `DX-96` — characters streamed per delta kind, and the partial tool JSON.

    ⚠ Counts only RAW `content_block_delta` events: the SDK also yields its own
    convenience events (`text`, `thinking`, `input_json`) for the same bytes,
    and counting both would double every figure.
    ⚠ Characters, not tokens — the API reports one output-token total. The
    split is what diagnoses a truncation; the ratio is approximate.
    """
    tally = {"thinking": 0, "text": 0, "tool_input": 0}
    partial: list[str] = []
    thinking: list[str] = []
    for event in events:
        if getattr(event, "type", "") != "content_block_delta":
            continue
        delta = event.delta
        kind = getattr(delta, "type", "")
        if kind == "thinking_delta":
            tally["thinking"] += len(delta.thinking)
            thinking.append(delta.thinking)
        elif kind == "text_delta":
            tally["text"] += len(delta.text)
        elif kind == "input_json_delta":
            tally["tool_input"] += len(delta.partial_json)
            partial.append(delta.partial_json)
    return {"chars": tally, "partial_tool_input": "".join(partial),
            "thinking_text": "".join(thinking)}


def tally_fields(tally: dict, stop_reason: str | None) -> dict:
    """The fields a transport result carries from the tally.

    ★ The partial tool JSON is kept ONLY for a `max_tokens` stop: it is the
    evidence of what the model was writing when the budget ran out. A completed
    call's input is already in `text`, and a second copy would double the
    payload for nothing. ⚠ A trace is evidence, not output (`F2` §4) — this
    text is never parsed as an answer.
    """
    out = {"stream_chars": dict(tally["chars"])}
    if stop_reason == "max_tokens":
        out["partial_tool_input"] = tally["partial_tool_input"]
        # ★ `DX-96` — whatever thinking was VISIBLE (only with `display:
        #   summarized`): the evidence of what a runaway call deliberated.
        out["thinking_text"] = tally.get("thinking_text", "")
    return out


def to_transport_result(message) -> dict:
    """Map an SDK `Message` to the gateway's transport contract.

    ★ **Split out so it is testable without a network call.** The mapping is
    where the money is: `DX-11` found four wrong assumptions in code that had
    never met a real response, and the worst was reading the SDK's own
    `usage.input_tokens` straight through into a field the gateway does not
    read — which records **0 tokens on every call** and silently destroys cost
    accounting while everything looks fine.
    """
    # ★ The tool call IS the answer; its input is already schema-valid (MP-5).
    text = ""
    for blk in message.content:
        if blk.type == "tool_use":
            text = json.dumps(blk.input)
            break
        if blk.type == "text" and not text:
            text = blk.text

    return {
        "text": text,
        # ⚠⚠ tokens_in / tokens_out — the gateway reads THESE names, NOT the
        # SDK's usage.input_tokens/output_tokens. Frozen by
        # tests/test_characterization_gateway.py.
        "tokens_in": message.usage.input_tokens,
        "tokens_out": message.usage.output_tokens,
        "stop_reason": message.stop_reason,
        # ★ `DX-127` — what the cache actually did. ⚠ Reported, never assumed: a silent
        #   invalidator shows up here as a read of 0 across calls that should have shared a
        #   prefix, and nowhere else.
        "cache_read": getattr(message.usage, "cache_read_input_tokens", None),
        "cache_write": getattr(message.usage, "cache_creation_input_tokens", None),
    }
