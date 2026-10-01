"""`DX-131` and `DX-135` — rulings by Victor, 2026-10-01.

★ `DX-131`: a period date the document does not state is CLEARED in the parse,
for every block at once. It is never computed (`S-2`, `AP-5`); the same ruling
`DX-73` made for `E-01`. Enforced in code because the prompt-level fix had been
applied to one block only, three times.

★ `DX-135`: an absent (`not_found`) item KEEPS its qualifier. An absence is a
fact about a question asked of a subject, so it needs the subject.
"""

from __future__ import annotations

import json

from tools.run_extraction_once import parse_items

BUNDLE = (
    "Nine months ended May 29, 2025. Balance as of August 29, 2024.\n"
    "Revenue for the quarter ended\nMay 29,\n2025 was $9,301 million.\n"
    "We do not disclose capacity by competitor.\n"
)


class _Call:
    def __init__(self, rows):
        self.parsed = json.dumps({"items": rows})


def _found(**over):
    row = {"evidence_id": "rev.total", "status": "found", "value": "9,301",
           "unit": "millions of USD", "quote": "was $9,301 million",
           "period_end": "2025-05-29"}
    row.update(over)
    return row


# ── DX-131 ──────────────────────────────────────────────────────────────────

def test_dx_131_a_start_the_document_does_not_state_is_cleared():
    """DX-131 — `2024-08-30` (prior year end plus one day) is not in the text."""
    [it] = parse_items(_Call([_found(period_start="2024-08-30", cumulative_ytd=True)]),
                       BUNDLE)
    assert it.period.start is None
    assert it.period.end == "2025-05-29"
    assert "DX-131" in it.note and "2024-08-30" in it.note


def test_dx_131_a_stated_date_is_kept_whatever_its_line_breaks():
    """DX-131 — `May 29,\\n2025` in a table header still counts as stated."""
    [it] = parse_items(_Call([_found(period_start="2024-08-29")]), BUNDLE)
    assert (it.period.start, it.period.end) == ("2024-08-29", "2025-05-29")
    assert "DX-131" not in it.note


def test_dx_131_an_unstated_end_clears_the_whole_period():
    """DX-131 — with no stated end there is no period to report (`E-12`'s
    `2024-08-30 → 2025-08-28`, neither in the filing)."""
    [it] = parse_items(_Call([_found(period_start="2024-08-30",
                                     period_end="2025-08-28")]), BUNDLE)
    assert it.period is None
    assert "2025-08-28" in it.note


# ── DX-135 ──────────────────────────────────────────────────────────────────

def _absent(qualifier, ev="cx.capacity"):
    return {"evidence_id": ev, "status": "not_found", "qualifier": qualifier,
            "quote": "We do not disclose capacity by competitor.", "note": "searched"}


def test_dx_135_an_absent_item_keeps_its_qualifier():
    """DX-135 — *which* competitor was silent is the substance."""
    [it] = parse_items(_Call([_absent("SK hynix")]), BUNDLE)
    assert it.qualifier == "SK hynix"
    assert it.status == "not_found"


def test_dx_135_absences_about_different_subjects_are_not_merged():
    """DX-135 — `gd.prior_value` held two different absences and the collapse
    merged them into one."""
    items = parse_items(_Call([_absent("Samsung"), _absent("Kioxia")]), BUNDLE)
    assert sorted(it.qualifier for it in items) == ["Kioxia", "Samsung"]


def test_dx_135_identical_absences_still_collapse():
    """DX-135 — the `seg.assets` ×5 case (same id, same qualifier) is one claim."""
    items = parse_items(_Call([_absent("all segments", "seg.assets")] * 5), BUNDLE)
    assert len(items) == 1
