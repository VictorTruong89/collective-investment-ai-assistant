"""`F10` `CT-F10.4` / `T4` wired — the valuation reaches the Stage-B bundle.

★ The D-02 half (`as_bundle_part`) is tested in `test_valuation_f10.py`; this is
the CALLER (`DX-82`'s lesson): D-01's `bundle_for` / `valuation_part`.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.fundamental.bundle.models import BundlePart, EvidenceBundle
from tests.unit.test_valuation_f10 import AS_OF, FakeEngine, rows


@pytest.fixture
def assumptions():
    from src.feature_engineer.valuation.assumptions import load_published
    return load_published("dcf_two_stage", 1)


def _bundle(part):
    filing = BundlePart("filing", {"accession_id": "acc"}, "Total revenue was $9,301 million.")
    return EvidenceBundle(ticker="XYZ", as_of=AS_OF, parts=(filing, part))


def test_ct_f10_4_the_stage_b_bundle_carries_fv_model_and_the_blind_view_does_not(assumptions):
    from src.fundamental.bundle.assemble import valuation_part

    part = valuation_part("XYZ", AS_OF, engine=FakeEngine(rows()), assumptions=assumptions)
    assert part.kind == "computed"
    assert part.pins == {"contract_name": "valuation.dcf_two_stage", "contract_version": 1}
    assert "fv_model" in part.content and "value_per_share" in part.content
    bundle = _bundle(part)
    assert part in bundle.parts and part not in bundle.redact().parts


def test_an_UNAVAILABLE_valuation_is_a_part_that_names_what_is_missing(assumptions):
    """★ `P5` / `PG-10` — never a silent absence, never a default value."""
    from src.fundamental.bundle.assemble import valuation_part

    frame = rows()
    frame.loc[3, "InterestExpense_minor"] = None
    part = valuation_part("XYZ", AS_OF, engine=FakeEngine(frame), assumptions=assumptions)
    assert part.kind == "computed"
    assert part.pins["contract_name"] == "valuation.dcf_two_stage.unavailable"
    assert "missing: interest_expense" in part.content
    assert "value_per_share" not in part.content
    assert part not in _bundle(part).redact().parts, "withheld from Stage A too"


def test_bundle_for_adds_the_part_ONLY_when_asked(monkeypatch, assumptions):
    """★ Opt-in, so every existing bundle — and every recorded `bundle_hash` —
    is unchanged (`RA-2`)."""
    import src.fundamental.bundle.assemble as asm
    import src.fundamental.bundle.for_ticker as ft

    calls = []
    sentinel = BundlePart("computed", {"contract_name": "valuation.x", "contract_version": 1}, "v")
    monkeypatch.setattr(asm, "valuation_part",
                        lambda *a, **k: calls.append((a, k)) or sentinel)
    filing = BundlePart("filing", {"accession_id": "acc"}, "text")
    monkeypatch.setattr(ft, "_filing_part", lambda *a, **k: filing)
    for name in ("_profile_part", "_ratios_part", "_computed_part"):
        monkeypatch.setattr(ft, name, lambda *a, **k: None)
    monkeypatch.setattr(ft, "observable_fields", lambda *a, **k: ("f_x",))

    plain = ft.bundle_for("XYZ", as_of=date(2025, 6, 26), engine=object())
    assert calls == [] and sentinel not in plain.parts
    staged = ft.bundle_for("XYZ", as_of=date(2025, 6, 26), engine=object(),
                           valuation_assumptions=assumptions)
    assert len(calls) == 1 and sentinel in staged.parts
    assert staged.bundle_hash != plain.bundle_hash
