"""Characterization — `run_extraction`, the E-block runner (`DX-23`).

⚠⚠ **Why this file exists.** `F5`'s whole `extraction` golden kind is defined
against what `run_extraction` produces, and until now **nothing called it and
no test exercised it** (`DX-23`). Constitution §5 item 3: *relying on inherited
behaviour ⇒ characterization test to freeze it before building near it.* Golden
cases 1 and 2 are built near it.

★ **No network, no key, no spend.** The seam is faked. This freezes the runner's
CONTRACT — call composition, verification, abort — not the model's answers.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.fundamental.bundle.models import BundlePart, EvidenceBundle
from src.fundamental.errors import ExtractionKindError
from src.fundamental.filings.extract import item, run_extraction
from src.fundamental.prompts.registry import PromptRegistry, block

FILING = (
    "Segment and Other Information\n"
    "Quarter Ended | Nine Months Ended\n"
    "CNBU | $ | 5,069 | $ | 2,573 | $ | 14,028 | $ | 6,495\n"
)
ACC = "0000723125-25-000021"


def _bundle() -> EvidenceBundle:
    return EvidenceBundle(
        ticker="MU", as_of=date(2025, 6, 26),
        parts=(BundlePart(kind="filing", pins={"accession_id": ACC}, content=FILING),),
    )


class FakeSeam:
    """★ Stands in for `PromptSeam`. Records what it was asked, answers canned.

    ⚠ It must NOT be cleverer than the real seam — a fake that accepts a call
    the real one would refuse turns this characterization into fiction.
    """

    def __init__(self, registry, response="<canned>"):
        self._registry = registry
        self._response = response
        self.calls: list[dict] = []

    def call(self, *, prompt_name, prompt_version, bundle, run_id, step=None,
             **kw):
        self.calls.append({"prompt_name": prompt_name, "step": step,
                           "prompt_version": prompt_version, "run_id": run_id})
        return self._response


def _registry(kind="extraction"):
    r = PromptRegistry()
    r.register(block("E-01", "v2", kind, "Extract the reporting-segment table."))
    return r


def _parse_one(_call):
    quote = "CNBU | $ | 5,069"
    return [item("seg.revenue", value="5,069", unit="millions of USD",
                 quote=quote, accession_id=ACC,
                 offset=(FILING.index(quote), FILING.index(quote) + len(quote)),
                 period_start="2025-02-28", period_end="2025-05-29",
                 qualifier="CNBU")]


def test_dx_23_run_extraction_calls_the_seam_once_per_block_and_verifies():
    """The runner's contract: one call per declared block, then X-01."""
    reg = _registry()
    seam = FakeSeam(reg)
    result = run_extraction(seam, block_ids=[("E-01", "v2")], bundle=_bundle(),
                            run_id="run-1", parse=_parse_one)

    assert len(seam.calls) == 1
    assert seam.calls[0]["prompt_name"] == "E-01"
    assert seam.calls[0]["step"] == "extract:E-01"
    assert seam.calls[0]["run_id"] == "run-1"

    (extraction,) = result.results
    assert extraction.block_id == "E-01"
    assert extraction.evidence_ids == frozenset({"seg.revenue"})
    # ★ Step 3 is not optional — verification runs in the same call.
    assert result.report is not None


def test_dx_23_a_judgement_block_is_refused_before_any_call():
    """★ RA-5 — extraction and judgement are separate calls with separate
    prompts. ⚠ The refusal must happen BEFORE the seam is reached, or the spend
    has already occurred."""
    reg = _registry(kind="judgement")
    seam = FakeSeam(reg)
    with pytest.raises(ExtractionKindError):
        run_extraction(seam, block_ids=[("E-01", "v2")], bundle=_bundle(),
                       run_id="run-1", parse=_parse_one)
    assert seam.calls == [], "refused only AFTER calling the model — that costs money"


def test_dx_23_a_quote_not_in_the_bundle_aborts():
    """★★ X-01 is a deterministic ABORT, not a warning (`ExtractionPass`).

    ⚠ This is the hallucination guard the whole `extraction` kind rests on: an
    unverified fact entering a judgement is a hallucination with a scorecard
    built on it.
    """
    def _parse_hallucinated(_call):
        bogus = "CNBU | $ | 9,999"
        return [item("seg.revenue", value="9,999", unit="millions of USD",
                     quote=bogus, accession_id=ACC, offset=(0, len(bogus)),
                     period_start="2025-02-28", period_end="2025-05-29",
                     qualifier="CNBU")]

    reg = _registry()
    with pytest.raises(Exception) as exc:
        run_extraction(FakeSeam(reg), block_ids=[("E-01", "v2")],
                       bundle=_bundle(), run_id="run-1", parse=_parse_hallucinated)
    assert "9,999" in str(exc.value) or "span" in str(exc.value).lower()


def test_dx_23_the_segment_table_survives_the_runner_intact():
    """★★ MP-18 end to end — the shape F5 cases 1 and 2 are written against.

    ⚠ Under the pre-MP-18 rule this raised: every row is `seg.revenue`.
    """
    # ⚠⚠ X-01 requires the value to appear in ITS OWN quote — "a value assembled
    # from two places is arithmetic, and arithmetic is D-02's". So both rows
    # cite the WHOLE table row, which contains both figures. ★ The quote cannot
    # distinguish the two columns; only `period` does. That is exactly why
    # MP-18's identity carries the period.
    ROW = "CNBU | $ | 5,069 | $ | 2,573 | $ | 14,028 | $ | 6,495"

    def _parse_rows(_call):
        out = []
        for value, qual, start, cum in (
            ("5,069", "CNBU", "2025-02-28", False),
            ("14,028", "CNBU", "2024-08-30", True),
        ):
            out.append(item("seg.revenue", value=value, unit="millions of USD",
                            quote=ROW, accession_id=ACC,
                            offset=(FILING.index(ROW),
                                    FILING.index(ROW) + len(ROW)),
                            period_start=start, period_end="2025-05-29",
                            cumulative_ytd=cum, qualifier=qual))
        return out

    result = run_extraction(FakeSeam(_registry()), block_ids=[("E-01", "v2")],
                            bundle=_bundle(), run_id="run-1", parse=_parse_rows)
    (extraction,) = result.results
    assert len(extraction.items) == 2
    discrete, cumulative = extraction.items
    assert not discrete.is_cumulative_ytd and cumulative.is_cumulative_ytd
    assert discrete.identity != cumulative.identity
