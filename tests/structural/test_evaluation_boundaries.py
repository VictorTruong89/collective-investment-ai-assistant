"""F5 `AC-5.11`, `AC-5.12`, `AC-5.15` — the import rules D-14 lives under."""

from __future__ import annotations

import pytest

from tools.check_evaluation_boundaries import (
    all_violations,
    one_way_violations,
    re_derivation_violations,
    study_consumer_violations,
)


def test_ac_5_12_the_real_tree_obeys_the_one_way_rule():
    assert one_way_violations() == []


def test_ac_5_11_no_metric_is_re_derived_here():
    assert re_derivation_violations() == []


def test_ac_5_15_nothing_imports_a_study():
    assert study_consumer_violations() == []


def _tree(tmp_path, files: dict[str, str]):
    src = tmp_path / "src"
    for rel, body in files.items():
        p = src / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return src


def test_ac_5_12_a_domain_importing_the_harness_is_caught(tmp_path):
    """⚠ BS-5 — the rule needs a case that fails it."""
    src = _tree(tmp_path, {"reporting/render.py":
                           "from src.evaluation.metrics.models import MetricResult\n"})
    assert one_way_violations(src) == [
        "src/reporting/render.py imports src.evaluation.metrics.models — "
        "ST-2 is one-way (AC-5.12)"]


def test_ac_5_15_a_study_that_acquires_a_consumer_is_caught(tmp_path):
    """★★ D1's silent direction — a study becoming load-bearing while exempt."""
    src = _tree(tmp_path, {
        "evaluation/studies/one_off.py": "X = 1\n",
        "reporting/card.py": "from src.evaluation.studies.one_off import X\n"})
    hits = study_consumer_violations(src)
    assert len(hits) == 1 and "a study that is CONSUMED is a metric" in hits[0]


def test_ac_5_15_a_study_importing_a_metric_is_fine(tmp_path):
    """The permitted direction: studies read metrics, not the reverse."""
    src = _tree(tmp_path, {
        "evaluation/metrics/m.py": "Y = 2\n",
        "evaluation/studies/s.py": "from src.evaluation.metrics.m import Y\n"})
    assert study_consumer_violations(src) == [] and one_way_violations(src) == []


@pytest.mark.parametrize("marker", ["def compute_ic(x):\n    return 1\n",
                                    "def effective_breadth(x):\n    return 1\n",
                                    "def ic_standard_error(x):\n    return 1\n"])
def test_ac_5_11_a_local_re_derivation_is_caught(tmp_path, marker):
    """★ *A second IC implementation that disagrees with the first is precisely
    the failure F5 exists to prevent.*"""
    src = _tree(tmp_path, {"evaluation/metrics/oops.py": marker})
    hits = re_derivation_violations(src)
    assert len(hits) == 1 and "import it from" in hits[0]


def test_ac_5_11_importing_the_upstream_metric_is_correct(tmp_path):
    src = _tree(tmp_path, {"evaluation/metrics/ok.py":
                           "from src.quant.metrics.breadth import effective_breadth\n"})
    assert all_violations(src) == []
