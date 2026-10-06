"""`X-01` ② and items whose value is a CLASSIFICATION — `DX-122`.

⛔ **The measured failure (2026-09-16, $0.50).** `E-13`'s `cx.status` answers *"announced |
under construction | commissioning | operating"*. That is a label the reader assigns from
what the document describes; a filing almost never contains the phrase. `X-01` ② requires the
value to appear IN its quote, so the item is unsatisfiable by construction — the run aborted
with `cx.status = "under construction"` cited against a gross-profit sentence.

★ **What is exempted, and what is NOT.** Only ② is relaxed, and only for an item declared
here with its closed set (`MP-5`). The value must be one of that set, and ① still holds in
full: the quote must resolve in the bundle, verbatim. ⚠ What nothing checks is whether the
cited span is the RIGHT span for the label — the failing run cited an unrelated sentence, and
under this rule that item would pass. That gap is real, recorded, and belongs to a prompt
version (`E-13 v2`: quote the sentence the status is read FROM), not to this file.
"""

from __future__ import annotations

#: evidence_id → the closed set its value must come from. ★ Copied from the block's own
#: prompt text; a structural test asserts every value appears there verbatim (`RA-13`).
CLASSIFICATION_VALUES: dict[str, tuple[str, ...]] = {
    "cx.status": ("announced", "under construction", "commissioning", "operating"),
    # ✏ 2026-10-04 — `E-08`: the plan status is a ticked box, not these words. ① still holds:
    #   the quote must be the form's own text. (`in.type` left this set the same day —
    #   `DX-148` ⓑ: it is now the form's code, verbatim, and its label is mapped.)
    "in.plan_status": ("10b5-1", "not_10b5-1", "not_stated"),
}


def is_classification(evidence_id: str) -> bool:
    return evidence_id in CLASSIFICATION_VALUES


def assert_declared_value(evidence_id: str, value: str) -> None:
    """The half of `X-01` ② that still applies: the label is one of the declared set."""
    from src.fundamental.errors import ValueNotInSpanError

    allowed = CLASSIFICATION_VALUES[evidence_id]
    if str(value).strip().casefold() not in {a.casefold() for a in allowed}:
        raise ValueNotInSpanError(
            evidence_id, str(value),
            f"a classification item's value must be one of {allowed} (MP-5, DX-122)")
