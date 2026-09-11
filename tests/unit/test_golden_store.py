"""F5 `AC-5.17` / `CT-5.5` — the golden set loads from disk and validates there."""

from __future__ import annotations

import pytest

from src.evaluation.golden.models import CircularGoldenValue
from src.evaluation.golden.store import (
    GOLDEN_DIR,
    KINDS,
    GoldenSetError,
    coverage,
    load_all,
    load_kind,
)

CASE = """cases:
  - case_id: {cid}
    input_ref: filings/X.txt
    expected: {{revenue_usd_m: 100}}
    source: "10-Q page 4"
    established_at: "2026-09-05"
    established_by: "{who}"
"""


def _write(tmp_path, kind, body):
    (tmp_path / f"{kind}.yaml").write_text(body)
    return tmp_path


def test_ac_5_17_a_case_written_in_yaml_loads_as_a_golden_case(tmp_path):
    _write(tmp_path, "extraction", CASE.format(cid="c1", who="Victor Truong"))
    (case,) = load_kind("extraction", tmp_path)
    assert case.case_id == "c1" and case.kind == "extraction"
    assert case.expected == {"revenue_usd_m": 100}
    assert case.is_judgement is False


def test_ac_5_17_d2s_circularity_check_runs_on_FILE_contents(tmp_path):
    """⚠⚠ The point of the store: the check must reach values written in YAML,
    not only ones a programmer typed into a test."""
    _write(tmp_path, "extraction", CASE.format(cid="c1", who="the pipeline"))
    with pytest.raises(CircularGoldenValue):
        load_kind("extraction", tmp_path)


def test_ac_5_17_a_missing_field_names_what_is_required(tmp_path):
    _write(tmp_path, "extraction", "cases:\n  - case_id: c1\n    input_ref: f\n    expected: 1\n")
    with pytest.raises(GoldenSetError, match="Every field of"):
        load_kind("extraction", tmp_path)


def test_ac_5_17_a_duplicate_case_id_across_kinds_raises(tmp_path):
    _write(tmp_path, "extraction", CASE.format(cid="dup", who="Victor Truong"))
    _write(tmp_path, "thesis", CASE.format(cid="dup", who="Victor Truong"))
    with pytest.raises(GoldenSetError, match="duplicate case_id"):
        load_all(tmp_path)


def test_ac_5_17_malformed_yaml_raises_but_an_ABSENT_file_does_not(tmp_path):
    assert load_kind("extraction", tmp_path) == ()  # ⚠ empty is honest
    _write(tmp_path, "thesis", "cases: [ unclosed")
    with pytest.raises(GoldenSetError, match="not valid YAML"):
        load_kind("thesis", tmp_path)


def test_ac_5_17_a_thesis_case_is_marked_a_judgement(tmp_path):
    _write(tmp_path, "thesis", CASE.format(cid="t1", who="Victor Truong"))
    (case,) = load_kind("thesis", tmp_path)
    assert case.is_judgement is True, "⚠ D2 — it does not pretend to be ground truth"


# --------------------------------------------------------------------------- #
# the real set — empty today, and that is REPORTED not assumed
# --------------------------------------------------------------------------- #
def test_the_real_golden_set_loads_whatever_it_holds():
    """⚠ `D2` makes filling this Victor's work. This asserts the set is
    LOADABLE, never that it is populated — a test demanding cases would fail
    until a human did homework, which is not what a test is for."""
    cases = load_all()
    assert all(c.source and c.established_by for c in cases)


def test_every_kind_has_a_template_file_to_copy():
    """★ `B5` is actionable only if there is somewhere to write. All three
    files exist with a commented example, so the task is *edit YAML*, not
    *write Python*."""
    import pathlib

    for kind in KINDS:
        f = pathlib.Path(GOLDEN_DIR) / f"{kind}.yaml"
        assert f.exists(), f"{f} missing — B5 would have nowhere to go"
        text = f.read_text()
        assert "case_id:" in text and "established_by:" in text
        assert "D2" in text, "the template must carry the rule it enforces"


def test_coverage_reports_zero_rather_than_hiding_it():
    assert set(coverage()) == set(KINDS)


# ── DX-20 · an unestablished case must not load, and must not PASS ──────────
# ⚠⚠ These cover AC-5.17's "validated on load" — the hole was in CT-5.2's own
#    validation, which never looked at `expected`.


def test_ac_5_17_a_case_with_an_empty_expected_refuses_to_load(tmp_path):
    """AC-5.17 / DX-20 — a half-written case is not a case.

    ⚠ This is the state EVERY case passes through while the filing is still
    open. Before the fix it loaded with `expected is None`.
    """
    _write(tmp_path, "extraction", (
        "cases:\n"
        "  - case_id: half-written\n"
        "    input_ref: rec/x\n"
        "    expected:\n"
        "    source: '10-Q p.4'\n"
        "    established_at: '2026-09-05'\n"
        "    established_by: 'Victor Truong'\n"
    ))
    with pytest.raises(GoldenSetError) as exc:
        load_kind("extraction", tmp_path)
    assert "expected" in str(exc.value)


def test_ac_5_17_the_unestablished_case_would_have_reported_PASS(tmp_path):
    """★★ DX-20's teeth — why `expected: None` is worse than a wrong value.

    ⚠ `run_regression` compares with `==`. A system that produces NOTHING
    matches an unestablished expectation, so the suite goes **green**. Every
    other guard in `CT-5.2` fails loudly; this one failed silently in the
    reassuring direction. ⚠ If this test ever passes with the guard removed,
    the guard has stopped working.
    """
    from src.evaluation.golden.models import GoldenCase
    from src.evaluation.regression.run import run_regression

    with pytest.raises(ValueError):
        GoldenCase(case_id="c", kind="extraction", input_ref="r", expected=None,
                   source="s", established_at="2026-09-05", established_by="Victor")

    # ★ The counterfactual, spelled out: had it loaded, this is what CI showed.
    established = GoldenCase(case_id="c", kind="extraction", input_ref="r",
                             expected={"revenue_usd_m": 30040}, source="10-Q p.4",
                             established_at="2026-09-05", established_by="Victor")
    report = run_regression([established], lambda ref: None)
    assert report.verdict == "FAIL", (
        "a system producing nothing must FAIL an established case — if this "
        "reds only because of the None guard, the comparison itself is wrong"
    )


def test_ac_5_17_absent_is_still_expressible_but_only_explicitly(tmp_path):
    """DX-20 — the guard must not make 'the document does not say' unsayable."""
    _write(tmp_path, "extraction", (
        "cases:\n"
        "  - case_id: no-segment-disclosure\n"
        "    input_ref: rec/y\n"
        "    expected: {status: NOT_FOUND}\n"
        "    source: '10-K: no segment revenue table is published'\n"
        "    established_at: '2026-09-05'\n"
        "    established_by: 'Victor Truong'\n"
    ))
    (case,) = load_kind("extraction", tmp_path)
    assert case.expected == {"status": "NOT_FOUND"}


def test_dx_28_a_placeholder_date_is_not_a_signature(tmp_path):
    """⚠⚠ DX-28 — eight cases were signed with a real NAME and the template's
    `____-__-__` still in `established_at`, and nothing objected. The set
    reported ten established when eight were half done.

    ★ A blank left in a template is exactly the state a signature ends, so the
    field recording WHEN must refuse a blank as firmly as the one recording WHO.
    """
    _write(tmp_path, "extraction", (
        "cases:\n"
        "  - case_id: half-signed\n"
        "    input_ref: r/c\n"
        "    expected: {v: 1}\n"
        "    source: '10-Q p.4'\n"
        "    established_at: '____-__-__'\n"
        "    established_by: 'Victor Truong'\n"
    ))
    with pytest.raises(GoldenSetError, match="established_at"):
        load_kind("extraction", tmp_path)


def test_dx_28_a_real_iso_date_is_accepted(tmp_path):
    """★ The guard must not reject a properly signed case."""
    _write(tmp_path, "extraction", (
        "cases:\n"
        "  - case_id: signed\n"
        "    input_ref: r/c\n"
        "    expected: {v: 1}\n"
        "    source: '10-Q p.4'\n"
        "    established_at: '2026-09-07'\n"
        "    established_by: 'Victor Truong'\n"
    ))
    (case,) = load_kind("extraction", tmp_path)
    assert case.established_at == "2026-09-07"
