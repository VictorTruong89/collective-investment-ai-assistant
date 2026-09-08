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
                            "description": "Exactly as the document states it, in its own units.",
                        },
                        "unit": {"type": "string", "description": "Verbatim, e.g. 'millions of USD'."},
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
                        max_output: int = MODEL_MAX_OUTPUT) -> Callable[[dict], dict]:
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
            "messages": [{"role": "user", "content": str(request["payload"])}],
        }
        # ⚠ Opus 5 rejects `temperature` (400) — the gateway's `effort` control
        # path is the supported one. `budget_tokens` is likewise removed.
        if "effort" in request:
            kwargs["thinking"] = {"type": "adaptive"}
            kwargs["output_config"] = {"effort": request["effort"]}
        if tool is not None:
            kwargs["tools"] = [tool]

        # ⚠⚠ STREAMING is required above ~16k max_tokens — a non-streaming
        # request that large risks an HTTP timeout, and this call already runs
        # ~230s. ★ `.get_final_message()` returns the same `Message`, so the
        # mapping below is unchanged.
        with client.messages.stream(**kwargs) as stream:
            return to_transport_result(stream.get_final_message())

    return transport


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
    }
