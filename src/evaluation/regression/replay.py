"""F5 `D5` / `DX-21` — resolving a golden case's `input_ref` to a recorded response.

★★ **This is the wire that was missing.** `run_regression` has always taken a
`replay_response` callable, but nothing ever implemented one: it was supplied
only by fakes in tests, so a golden case could be *written* and never *run*.

⚠⚠ **Why `input_ref` names a RECORDING and not a filing.** A filing fixture is
an *input*. Comparing it to `expected` would require producing an extraction
from it — i.e. an LLM call — and `D5` forbids the regression from reaching the
network at all. ★ The recorded response is the only artefact that is both a
*product of the system* and *available offline*, which is exactly what a
regression needs. (`CT-5.2` calls `input_ref` "the fixture"; `run.py` calls it
"the recording". The recording reading is the one that can be implemented.)

**Format:** `input_ref: "<run_id>/<call_id>"`, optionally with a **selector**:

    <run_id>/<call_id>#<evidence_id>|<qualifier>|<start>:<end>

⚠⚠ **Why a selector is needed** (`DX-25`). One recorded `E-01` call returns
EVERY segment row in BOTH columns; one golden case pins ONE item. Comparing the
whole response to a single-item `expected` can never match. ★ The selector is
exactly `MP-18`'s identity — `(evidence_id, qualifier, period)` — so the golden
set's granularity and the extraction's identity are **the same thing**, not two
conventions to keep in step. A bare ref with no `#` compares the whole response,
which is what a single-item block wants.

⚠⚠ **Why the payload reader is INJECTED rather than imported.** Two fences meet
here and both bind: `OR-3` — *no domain imports orchestration* — and `ST-2` —
*nothing imports the harness*. So `src/evaluation/` and `src/orchestration/`
may not reference each other in either direction, and the `F2` adapter is wired
by the **caller**: CI, which is `F5`'s `T1` trigger. ★ `tools/f2_payload_reader.py`
is that adapter. *(Found by `OR-3` when this module first imported `TraceStore`
directly — the fence did its job on the first attempt.)*
"""

from __future__ import annotations

import re
from collections.abc import Callable

#: `<run_id>/<call_id>`. ⚠ Exactly two segments — a bare id is ambiguous once a
#: second run records a call under the same name.
INPUT_REF_RE = re.compile(
    r"^(?P<run_id>[^/\s#]+)/(?P<call_id>[^/\s#]+)"
    r"(?:#(?P<evidence_id>[^|\s]+)\|(?P<qualifier>[^|]*)\|"
    r"(?P<start>[^:\s]*):(?P<end>[^\s]+))?$"
)


class UnresolvableCase(Exception):
    """⚠ A golden case pointing at a recording that cannot be served.

    ★ `P5` — loud. The tempting alternative is to skip the case, which turns a
    broken baseline into a *smaller* baseline and still reports green. `DX-20`
    was the same failure one layer up: **the golden set's whole job is to
    notice, so it may never quietly stop noticing.**
    """


#: `(run_id, call_id) -> {"request": ..., "response": ...}`.
#: ⚠ Raises `UnresolvableCase` when the recording cannot be served — the
#: adapter owns that translation, because only it knows `F2`'s failure modes.
PayloadReader = Callable[[str, str], dict]


def recorded_response(
    read_payload: PayloadReader,
    *,
    parse: Callable[[object], object] | None = None,
) -> Callable[[str], object]:
    """Build the `replay_response` callable `run_regression` expects.

    `parse` maps the recorded response body to whatever `expected` is written
    in — for extraction, the `ExtractedItem` shape. ⚠ It is injected for the
    same reason `run_extraction` injects it: **the response shape is the API's
    contract, not this module's** (`MP-5`).

    ★ Nothing here can reach a vendor: this module has no I/O and no client.
    That is `D5` enforced by construction rather than by a rule in prose.
    """

    def replay_response(input_ref: str) -> object:
        match = INPUT_REF_RE.match(input_ref or "")
        if not match:
            raise UnresolvableCase(
                f"input_ref {input_ref!r} is not '<run_id>/<call_id>' — a golden "
                "case names the recording it grades (F5 CT-5.2, DX-21)"
            )
        payload = read_payload(match["run_id"], match["call_id"])
        response = payload.get("response")
        if parse is not None:
            response = parse(response)
        if match["evidence_id"] is None:
            return response
        return _select(response, match, input_ref)

    return replay_response


def _select(response: object, m: re.Match, input_ref: str) -> object:
    """`DX-25` — pick the ONE item a golden case is about.

    ⚠ Loud on both failure directions. *No match* means the reading vanished —
    which is a real regression and must not be reported as a pass. *Several
    matches* means the identity is not identifying, and silently taking the
    first would hide exactly the ambiguity `MP-18` exists to prevent.
    """
    if not isinstance(response, list):
        raise UnresolvableCase(
            f"{input_ref}: the recorded response is "
            f"{type(response).__name__}, not a list of items — a selector only "
            "makes sense for a call that returns several (DX-25)"
        )
    want_period = ({"start": m["start"] or None, "end": m["end"]}
                   if m["end"] else None)
    hits = [it for it in response
            if isinstance(it, dict)
            and it.get("evidence_id") == m["evidence_id"]
            and (it.get("qualifier") or "") == m["qualifier"]
            and it.get("period") == want_period]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise UnresolvableCase(
            f"{input_ref}: no item matches "
            f"({m['evidence_id']!r}, {m['qualifier']!r}, "
            f"{m['start']}..{m['end']}) in a response of {len(response)} item(s). "
            "⚠ The reading this case pins is GONE — that is a regression, not a "
            "missing fixture."
        )
    raise UnresolvableCase(
        f"{input_ref}: {len(hits)} items share one identity — MP-18 says that "
        "cannot happen, so either the extractor emitted a duplicate or the "
        "selector is under-specified. ⚠ Taking the first would hide it."
    )
