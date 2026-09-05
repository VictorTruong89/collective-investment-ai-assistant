"""D-01 B4.7 — AC-1.66, 1.67, 1.68, 1.68a, 1.69, 1.69a, 1.70, 1.71, 1.71a.

★ **L3 §3A.4's done-when:** *a source-list item missing with no logged reason
raises; a schema change without a version bump raises.*

⚠ **BS-29 — the sector file lands AFTER the monitors, not before.** It is a
**shared prior by construction** (RA-102): one input feeding every thesis in the
industry, so a defect in it is a *correlated* defect. RM-16 is the instrument
that would see it, and it had to exist first.

★ §10C's argument is that **a view can hide in four places** — the prose
(RA-97), the sampling (RA-98), the ordering (RA-99) and the schema (RA-100) —
and *they get harder to see in that order.*

Tier: unit + invariant/property (constitution §4).
"""

from __future__ import annotations

import dataclasses
from datetime import date

import pytest

from src.fundamental import (
    AuthoringRun, BUY, BearCase, CAPACITY_STATUSES, CapacityRowMutatedError,
    ConclusionFieldError, Falsifier, KIND_CAPACITY, OMISSION_FIELDS_V1, Omission,
    RECORD_FIELDS_V1, SCHEMA_V1, SchemaDriftError, SectorFile, SectorRecord,
    SectorSchema, Source, SourceList, SourceListIncompleteError, append_transition,
    assemble, assert_complete, assert_no_conclusion_fields, assert_schema_current,
    computed, declared_on, filing, fingerprint_of, ingest_sector, profile, schema_for,
    sector_file,
)

AS_OF = date(2026, 8, 25)
DEADLINE = date(2027, 3, 31)


def record(record_id="r1", day=date(2026, 7, 14), **kw):
    base = dict(kind=KIND_CAPACITY, subject="TSMC AZ P2", source_id="src-tsmc-ir",
                url="https://example.invalid/ir", quote="P2 has begun tool move-in.",
                status="commissioning", prior_status="")
    return SectorRecord(record_id=record_id, date=day, **{**base, **kw})


def source_list(*ids, version="srcs.v3"):
    ids = ids or ("src-tsmc-ir",)
    return SourceList(source_list_version=version, industry="semiconductors",
                      sources=tuple(Source(source_id=i, name=i) for i in ids))


def sector(records=None, omissions=(), **kw):
    base = dict(industry="semiconductors", as_of=AS_OF, file_version=17,
                source_list_version="srcs.v3",
                records=tuple(records if records is not None else (record(),)),
                omissions=tuple(omissions))
    return SectorFile(**{**base, **kw})


# --------------------------------------------------------------------------- #
# The PROSE — RA-97. AC-1.66
# --------------------------------------------------------------------------- #

def test_ac_1_66_a_conclusion_shaped_field_raises():
    """AC-1.66 / RA-97 — if one appears, the rejected macro narrative is back."""
    for name in ("outlook", "view", "implication", "summary", "assessment"):
        with pytest.raises(ConclusionFieldError, match="conclusion-shaped"):
            assert_no_conclusion_fields({"records": [{name: "constructive"}]})


def test_the_wordlist_is_wider_than_the_rule_s_five():
    """RA-97 — the defect is a conclusion, not a spelling.

    ⚠ Renaming `outlook` to `takeaway` is the cheapest possible evasion, and a
    guard that matches only the five words in the rule text invites it.
    """
    with pytest.raises(ConclusionFieldError):
        assert_no_conclusion_fields({"takeaway": "supply stays tight"})
    assert {"outlook", "view", "implication", "summary", "assessment"} <= set(
        __import__("src.fundamental", fromlist=["x"]).CONCLUSION_FIELDS)


def test_the_scan_reaches_nested_records():
    """RA-97 — a view one level down is still a view."""
    with pytest.raises(ConclusionFieldError, match=r"records\[1\]"):
        assert_no_conclusion_fields({"records": [{"quote": "x"}, {"opinion": "y"}]})


def test_a_file_carrying_a_conclusion_field_cannot_be_constructed():
    """RA-97 — enforced at construction, not at render."""
    class Sneaky(SectorRecord):
        def to_json_obj(self):
            return {**super().to_json_obj(), "assessment": "bullish"}

    with pytest.raises(ConclusionFieldError):
        sector([Sneaky(record_id="r1", date=date(2026, 7, 14), kind="news",
                       subject="s", source_id="src-tsmc-ir", quote="q")])


# --------------------------------------------------------------------------- #
# The SAMPLING — RA-98. AC-1.67
# --------------------------------------------------------------------------- #

def test_ac_1_67_a_source_that_produced_nothing_and_logged_nothing_raises():
    """AC-1.67 / RA-98 — ★★ *selection of evidence is itself a conclusion.*"""
    listed = source_list("src-tsmc-ir", "src-samsung-ir")
    with pytest.raises(SourceListIncompleteError, match="src-samsung-ir"):
        assert_complete(sector(), listed)


def test_a_logged_omission_satisfies_completeness():
    """RA-98 — the file may be empty of a source; it may not be *silent* about one."""
    listed = source_list("src-tsmc-ir", "src-samsung-ir")
    file = sector(omissions=[Omission("src-samsung-ir", "IR page returned 503",
                                      "2026-08-25T06:04:00Z")])
    assert_complete(file, listed)


def test_an_omission_with_no_reason_raises():
    """RA-98 — an omission with no reason is indistinguishable from a poll that
    never ran, which is the state DE-35 and RA-30 both refuse to allow."""
    with pytest.raises(ValueError, match="curation is where the view hides"):
        Omission("src-samsung-ir", "   ", "2026-08-25T06:04:00Z")


def test_completeness_is_measured_against_the_declared_list_version():
    """RA-98 — completeness against the *wrong* list is not completeness."""
    with pytest.raises(SourceListIncompleteError):
        assert_complete(sector(), source_list("src-tsmc-ir", version="srcs.v4"))


def test_the_ingest_cannot_skip_a_source_without_producing_an_omission():
    """★ RA-98 — the two outcomes are exhaustive **by construction**.

    A poll that raises becomes a logged row rather than an exception that ends
    the run and leaves twelve good sources unpolled. ⚠ That is a deliberate
    reading of P5: the failure is *loud in the artifact*.
    """
    listed = source_list("src-ok", "src-raises", "src-empty")

    def poll(source):
        if source.source_id == "src-raises":
            raise TimeoutError("no response in 30s")
        if source.source_id == "src-empty":
            return []
        return [record(record_id="r-ok", source_id="src-ok")]

    file = ingest_sector(listed, poll=poll, as_of=AS_OF, file_version=1)
    reasons = {o.source_id: o.reason for o in file.omissions}
    assert set(reasons) == {"src-raises", "src-empty"}
    assert "TimeoutError" in reasons["src-raises"]
    assert reasons["src-empty"] == "polled, no new items"
    assert_complete(file, listed)          # tautological here — and that is the point


# --------------------------------------------------------------------------- #
# The ORDERING — RA-99, RA-141. AC-1.68, AC-1.68a
# --------------------------------------------------------------------------- #

def test_ac_1_68_the_file_is_returned_in_date_order():
    """AC-1.68 / RA-99 — a file sorted by importance carries a view in the SORT KEY."""
    late = record("r-late", date(2026, 7, 20), status="operating", prior_status="")
    early = record("r-early", date(2026, 1, 5), status="announced")
    file = sector([late, early])
    assert [r.record_id for r in file.records] == ["r-early", "r-late"]


def test_the_file_exposes_no_other_sort():
    """AC-1.68 — ★ the absence of a knob is the guarantee.

    ⚠ A `sort_by=` parameter anywhere would make RA-99 a default rather than a
    rule, and the reader reads the top of the file.
    """
    import inspect

    import src.fundamental.sector.models as models

    for name, obj in vars(models).items():
        if not callable(obj) or getattr(obj, "__module__", "") != models.__name__:
            continue
        params = inspect.signature(obj).parameters
        assert not {"sort", "sort_by", "order", "order_by", "key"} & set(params), name


def test_ac_1_68a_a_capacity_transition_is_its_own_dated_record():
    """AC-1.68a / RA-141 — ★ the file's unit is the RECORD; the row is a projection.

    ⚠ RA-99 says *"ordered by date"* and RA-101 gives a row several dates.
    Announcement order buries yesterday's transition beside a 2019 announcement;
    latest-transition order makes the sort key **mutate**. Neither is a fixed sort.
    """
    announced = record("r1", date(2019, 5, 2), status="announced")
    building = record("r2", date(2023, 3, 9), status="under construction",
                      prior_status="announced")
    commissioning = record("r3", date(2026, 7, 14), status="commissioning",
                           prior_status="under construction")
    other = record("r4", date(2024, 1, 8), subject="Samsung Taylor",
                   status="announced", source_id="src-tsmc-ir")
    file = sector([commissioning, announced, other, building])

    assert [r.record_id for r in file.records] == ["r1", "r2", "r4", "r3"]
    row = file.capacity_row("TSMC AZ P2")
    assert [r.record_id for r in row.transitions] == ["r1", "r2", "r3"]
    assert row.current_status == "commissioning"
    assert row.announced_on == date(2019, 5, 2)


def test_the_row_is_derived_and_has_no_setter():
    """RA-101/RA-141 — there is no way to write a row, only to append a record."""
    assert not hasattr(sector().capacity_row("TSMC AZ P2"), "set_status")
    assert callable(SectorFile.capacity_row)


# --------------------------------------------------------------------------- #
# The SCHEMA — RA-100, RA-140. AC-1.69, AC-1.69a
# --------------------------------------------------------------------------- #

def test_ac_1_69_an_undeclared_schema_version_raises():
    """AC-1.69 / RA-100 — versioned, and the version has to exist."""
    with pytest.raises(SchemaDriftError):
        schema_for("sector.v2")
    with pytest.raises(SchemaDriftError):
        sector(schema_version="sector.v2")


def test_ac_1_69a_a_changed_field_set_fingerprints_differently():
    """AC-1.69a / RA-140 — ★★ drift is caught by ARITHMETIC, not by review.

    ⚠ RA-100's own argument is that **a schema change looks like maintenance**.
    A guard that depends on someone noticing is the guard it says will fail.
    """
    with_new_column = RECORD_FIELDS_V1 + ("materiality",)
    assert (fingerprint_of(with_new_column, OMISSION_FIELDS_V1, SCHEMA_V1)
            != schema_for(SCHEMA_V1).fingerprint)
    with pytest.raises(SchemaDriftError, match="version bump"):
        assert_schema_current(SCHEMA_V1, with_new_column, OMISSION_FIELDS_V1)


def test_reordering_columns_is_a_schema_change():
    """RA-140 — ★ order is part of the fingerprint, because a reader reads in order."""
    swapped = (RECORD_FIELDS_V1[1], RECORD_FIELDS_V1[0]) + RECORD_FIELDS_V1[2:]
    with pytest.raises(SchemaDriftError):
        assert_schema_current(SCHEMA_V1, swapped, OMISSION_FIELDS_V1)


def test_a_new_version_may_add_a_column():
    """RA-100 — ★ a new column is an analytical change and takes a version bump.
    The rule is not *never change*; it is *never change silently*."""
    v2 = SectorSchema("sector.v2", RECORD_FIELDS_V1 + ("materiality",),
                      OMISSION_FIELDS_V1)
    assert v2.fingerprint != schema_for(SCHEMA_V1).fingerprint
    assert v2.to_json_obj()["schema_version"] == "sector.v2"


def test_a_built_file_carries_its_fingerprint():
    """RA-140 — the file declares what it was checked against."""
    file = sector()
    assert file.schema_fingerprint == schema_for(SCHEMA_V1).fingerprint
    assert file.to_json_obj()["schema_fingerprint"] == file.schema_fingerprint


# --------------------------------------------------------------------------- #
# APPEND-ONLY — RA-101. AC-1.70
# --------------------------------------------------------------------------- #

def test_ac_1_70_a_transition_that_replaces_the_row_raises():
    """AC-1.70 / RA-101, INV-006 — ★ *the transition history is the finding.*"""
    file = sector([record("r1", date(2019, 5, 2), status="announced")])
    with pytest.raises(CapacityRowMutatedError, match="replaces the row"):
        append_transition(file, record("r2", date(2023, 3, 9),
                                       status="under construction"))


def test_a_transition_appended_over_a_gap_raises():
    """RA-101 — appending over a history that does not lead here loses the
    transition in between, which is exactly what makes an announcement that
    quietly never became capacity invisible."""
    file = sector([record("r1", date(2019, 5, 2), status="announced")])
    with pytest.raises(CapacityRowMutatedError, match="but the row is at"):
        append_transition(file, record("r2", date(2026, 7, 14),
                                       status="commissioning",
                                       prior_status="under construction"))


def test_a_backdated_transition_raises():
    """RA-101 — an append that reorders history is not an append."""
    file = sector([record("r1", date(2023, 3, 9), status="announced")])
    with pytest.raises(CapacityRowMutatedError, match="reorders history"):
        append_transition(file, record("r2", date(2019, 5, 2),
                                       status="under construction",
                                       prior_status="announced"))


def test_a_well_formed_transition_appends_and_the_history_survives():
    """RA-101 — the row grows; nothing is overwritten."""
    file = sector([record("r1", date(2019, 5, 2), status="announced")])
    file = append_transition(file, record("r2", date(2023, 3, 9),
                                          status="under construction",
                                          prior_status="announced"))
    file = append_transition(file, record("r3", date(2026, 7, 14),
                                          status="commissioning",
                                          prior_status="under construction"))
    row = file.capacity_row("TSMC AZ P2")
    assert [r.status for r in row.transitions] == [
        "announced", "under construction", "commissioning"]


def test_a_cancellation_is_a_transition_like_any_other():
    """RA-101 — ★ a project that stalls or dies is precisely the history the rule
    protects, so the lifecycle is not one-way."""
    assert "cancelled" in CAPACITY_STATUSES
    file = sector([record("r1", date(2019, 5, 2), status="announced")])
    file = append_transition(file, record("r2", date(2024, 2, 1),
                                          status="cancelled",
                                          prior_status="announced"))
    assert file.capacity_row("TSMC AZ P2").current_status == "cancelled"


def test_an_unknown_status_raises():
    """RA-101 / INV-006 — the lifecycle is an enum, not free text."""
    with pytest.raises(ValueError, match="INV-006"):
        record("r1", status="going well")


# --------------------------------------------------------------------------- #
# THE BUNDLE SEAM — RA-102, RA-142. AC-1.71, AC-1.71a
# --------------------------------------------------------------------------- #

def falsifiers():
    return (Falsifier(ordinal=1, condition="Gross margin below 55% twice.",
                      observable_field="f_gross_margin", source="D-02",
                      deadline=DEADLINE, materiality="The premise fails."),
            Falsifier(ordinal=2, condition="Net debt / EBITDA above 3.0x.",
                      observable_field="f_net_debt_ebitda", source="D-02",
                      deadline=DEADLINE, materiality="The balance sheet premise fails."))


def thesis_over(parts):
    run = AuthoringRun(ticker="MU", as_of=AS_OF)
    return run.author(
        bundle=assemble(ticker="MU", as_of=AS_OF, parts=parts),
        stage_a_payload={"moat_durability": 3}, falsifiers=falsifiers(),
        verdict=BUY, conviction="Medium-High",
        bear_case=BearCase(text="Capacity additions crush pricing.",
                           falsification_condition="Utilisation above 90%.",
                           prompt_version="J-11@v1", run_id="call-bear"),
        scorecard={"moat_durability": 3},
        confidence={"value": 0.62, "basis": "evidence_coverage"},
        bull_run_ids=("call-bull",), run_id="run-1")


def base_parts():
    return [filing("0000-1", "Gross margin was 55.4%."),
            computed("b3_minimal", 1, "fair_value_band=[380,445]"),
            profile(AS_OF, "Sector: IT")]


def test_ac_1_71_the_sector_file_changes_the_bundle_hash():
    """AC-1.71 / RA-102 — hashed into `bundle_hash`, so a re-ingest is visible.

    ⚠ *It is shared across every thesis in the industry, so a defect in it is a
    correlated defect by construction* — and RM-16 is what would see it.
    """
    without = assemble(ticker="MU", as_of=AS_OF, parts=base_parts())
    with_file = assemble(ticker="MU", as_of=AS_OF,
                         parts=base_parts() + [sector_file(sector())])
    assert without.bundle_hash != with_file.bundle_hash

    changed = sector(file_version=18)
    again = assemble(ticker="MU", as_of=AS_OF,
                     parts=base_parts() + [sector_file(changed)])
    assert again.bundle_hash != with_file.bundle_hash


def test_ac_1_71a_the_thesis_declares_the_version_it_consumed():
    """AC-1.71a / RA-142 — ★ hashing proves it did not change; **declaring says
    what it was.** A reader asking *which sector file did this thesis rest on?*
    cannot answer it from a hash without still holding the bundle."""
    thesis = thesis_over(base_parts() + [sector_file(sector())])
    assert thesis.sector_files == ({"industry": "semiconductors",
                                    "schema_version": SCHEMA_V1,
                                    "file_version": 17},)
    assert thesis.to_json_obj()["sector_files"][0]["file_version"] == 17
    assert declared_on(thesis) == thesis.sector_files


def test_a_thesis_that_consumed_none_declares_none():
    """RA-142 — an empty list is a claim, and it is the true one here."""
    assert thesis_over(base_parts()).sector_files == ()


def test_the_declaration_is_derived_from_the_bundle_not_supplied():
    """★ RA-142 with RA-19 — *the bundle is not curated by the layer that judges.*

    ⚠ A caller supplying its own list of "consumed" sector files would let an
    artifact declare a version it never actually read.
    """
    import inspect

    from src.fundamental.thesis.author import AuthoringRun as Run

    assert "sector_files" not in inspect.signature(Run.author).parameters


def test_the_pin_matches_the_declared_seam():
    """RA-102 — `PIN_FIELDS["sector_file"]` and `SectorFile.pin()` are one contract."""
    from src.fundamental import PIN_FIELDS

    assert tuple(sector().pin()) == PIN_FIELDS["sector_file"]
