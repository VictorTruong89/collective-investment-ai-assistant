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

    <run_id>/<call_id>#<evidence_id>|<qualifier>|<start>:<end>[|ytd]

⚠⚠ **Why a selector is needed** (`DX-25`). One recorded `E-01` call returns
EVERY segment row in BOTH columns; one golden case pins ONE item. Comparing the
whole response to a single-item `expected` can never match. ★ The selector is
exactly `MP-18`'s identity — `(evidence_id, qualifier, period, cumulative_ytd)`
— so the golden set's granularity and the extraction's identity are **the same
thing**, not two conventions to keep in step. A bare ref with no `#` compares
the whole response, which is what a single-item block wants.

⚠⚠ **Why `|ytd` had to join the identity** (`DX-68`, 2026-09-11). Once the
shared prompt envelope's `S-2` item 3 landed — *"Do not compute … record a data
gap"* — the model stopped reporting `period_start` on segment rows, because a
segment table states only the period END and the start must be **derived**. It
was obeying the instruction. But `period` was carrying the whole discrete-vs-
year-to-date distinction, so 20 of 65 items collapsed onto 20 duplicate
identities. ★ `cumulative_ytd` is a fact the model **records**, not one it must
compute, so the identity now rests on observation rather than arithmetic.

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
    # ⚠⚠ `end` is `*`, not `+`: a trailing `|:` means **this item has no
    # period**. Requiring an end date made periodless items unaddressable —
    # and those are exactly the `not_found` items (`MP-7`) and the narrative
    # ones (`C14`), i.e. the two kinds the golden set most needs to pin,
    # because they are where a system quietly says nothing at all.
    r"(?:#(?P<evidence_id>[^|\s]+)\|(?P<qualifier>[^|]*)\|"
    # ⚠ `DX-74` — `@` is excluded from BOTH date groups. `end` was `[^|\s]*`,
    # which happily swallowed a trailing `@0:60`, so the span group never
    # matched and the selector silently ignored it. ★ Adding a delimiter means
    # widening every group that could eat it.
    r"(?P<start>[^:|@\s]*):(?P<end>[^|@\s]*)"
    # ⚠⚠ `DX-68` — the FOURTH component of `MP-18`'s identity. A trailing
    # `|ytd` selects the cumulative year-to-date row; its ABSENCE **asserts
    # discrete**, and is not a don't-care.
    # ⚠ So this is NOT backward compatible for cumulative rows: a pre-`DX-68`
    # ref to one now raises. ★ That is the direction to break in — loud, named,
    # unmistakable for a pass. A don't-care would have matched both rows and
    # rebuilt the exact ambiguity the component was added to remove.
    r"(?:\|(?P<ytd>ytd))?"
    # ⚠⚠ `DX-74` — the FIFTH component, and the one that makes this module's
    # own claim true. `identity` appends the span for a NON-FIGURE (`C14`), so
    # two narrative items on the same (id, qualifier, period) are distinct —
    # but the selector could not say so, which made it WEAKER than the identity
    # its docstring says it mirrors.
    # ★ Measured: two AMD runs 82 minutes apart differed in whether
    #   `seg.basis_note` carried a qualifier at all. In the second, FOUR notes
    #   collapsed onto one selector and `_select` refused — correctly, and two
    #   signed cases became unaddressable while their values were still right.
    # ⚠ Optional, and only meaningful for non-figures: a figure's identity
    #   deliberately EXCLUDES the span (`C14`), so pinning one here would
    #   address something `MP-18` does not distinguish.
    r"(?:@(?P<span>\d+:\d+))?)?$"
)

#: `DX-68` — the tag `MP-18`'s fourth component travels as, on the wire.
#:
#: ⚠ Written as a literal rather than imported from `src/fundamental/`: this
#: module reaches no domain module by design — the response shape is the API's
#: contract, which is why `parse` is injected (`MP-5`). ★ The drift a duplicated
#: literal invites is caught in `tests/unit/test_golden_replay.py`, which
#: asserts this equals `src.fundamental.filings.models.CUMULATIVE_YTD`.
CUMULATIVE_YTD_TAG = "cumulative_ytd"


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
    # ⚠ `DX-68` — absence of the flag is a POSITIVE assertion ("the discrete
    # column"), not "don't care". A don't-care would re-open exactly the
    # ambiguity that made 20 items share one identity.
    want_ytd = m["ytd"] is not None
    # ⚠ `DX-74` — absent means "do not discriminate on the span", NOT "the span
    # is empty". Unlike `|ytd`, an absent span cannot be a positive assertion:
    # every pre-`DX-74` ref omits it, and a figure has no span in its identity
    # at all. ★ So this narrows only when given, and ambiguity still RAISES
    # rather than resolving to the first hit.
    want_span = m["span"]
    hits = [it for it in response
            if isinstance(it, dict)
            and it.get("evidence_id") == m["evidence_id"]
            and (it.get("qualifier") or "") == m["qualifier"]
            and it.get("period") == want_period
            and (CUMULATIVE_YTD_TAG in (it.get("tags") or ())) == want_ytd
            and (want_span is None or _span_of(it) == want_span)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise UnresolvableCase(
            f"{input_ref}: no item matches "
            f"({m['evidence_id']!r}, {m['qualifier']!r}, "
            f"{m['start']}..{m['end']}, "
            f"{'cumulative_ytd' if want_ytd else 'discrete'}) "
            f"in a response of {len(response)} item(s). "
            "⚠ The reading this case pins is GONE — that is a regression, not a "
            "missing fixture."
        )
    raise UnresolvableCase(
        f"{input_ref}: {len(hits)} items share one selector"
        + (f"; their spans are {sorted(filter(None, (_span_of(h) for h in hits)))}"
           if want_span is None and len({_span_of(h) for h in hits}) > 1 else "")
        + ". MP-18 says that "
        "cannot happen, so either the extractor emitted a duplicate or the "
        "selector is under-specified. ⚠ Taking the first would hide it.\n"
        "★ `@<start>:<end>` narrows to one span — but ONLY for a NARRATIVE "
        "item. `MP-18` deliberately excludes the span from a FIGURE's identity "
        "(C14), so two figures sharing (id, qualifier, period, ytd) are a real "
        "duplicate; pinning a span there would hide it rather than resolve it."
    )


def _span_of(item: dict) -> str | None:
    """`DX-74` — `<start>:<end>` of the item's span, or `None` if it has none.

    ⚠ Only the offsets, never the accession id: `identity` includes the
    accession because one `ExtractionResult` may span several filings, but a
    selector already names one recording of one call, so the accession is fixed
    and repeating it would be noise a case author has to get right.
    """
    span = item.get("span")
    if not isinstance(span, dict):
        return None
    # ⚠⚠ The WIRE shape is `{"accession_id": ..., "offset": [start, end]}`.
    # `Span` the dataclass exposes `.start`/`.end` — which `identity` uses —
    # and `to_json_obj` emits neither name. ★ Reading `span["start"]` here
    # returned `None` for every item and the span silently never narrowed
    # anything: a filter that matches everything is indistinguishable from one
    # that was never applied. Caught by the four-notes test on the first run.
    offset = span.get("offset")
    if not isinstance(offset, (list, tuple)) or len(offset) != 2:
        return None
    start, end = offset
    return None if start is None or end is None else f"{start}:{end}"
