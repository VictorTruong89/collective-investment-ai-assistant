"""`F11` — reference-class base rates (D-02). One test per acceptance criterion, named.

★ The known answers are counted by hand INSIDE the test, independently of `base_rates/`.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest
import yaml

from src.shared.money import Money

AS_OF = date(2025, 6, 26)


def usd(major) -> Money:
    return Money.from_decimal_str(str(major), "USD")


class Year:
    """The shape `F10` `annual_history` yields: `fiscal_year`, `basis`, `margin`, `unavailable`."""

    class _B:
        def __init__(self, fcff, revenue, filed):
            self.fcff, self.revenue = usd(fcff), usd(revenue)
            self.inputs = ({"filing_date": filed},)

    def __init__(self, fy, fcff=None, revenue=None, filed=None, unavailable=None):
        self.fiscal_year, self.fiscal_year_end = fy, date(fy, 8, 30)
        self.unavailable = unavailable
        self.basis = None if unavailable else self._B(fcff, revenue, filed or date(fy, 10, 15))
        self.margin = None if unavailable else Decimal(fcff) / Decimal(revenue)


# Hand-worked class: subject AAA, peer BBB.
#   AAA: FY2015 fcff 10/100 · 2016 -5/80 · 2017 40/100 · 2018 50/120 · 2019 unavailable · 2020 30/150
#   BBB: FY2016 20/50 · 2017 25/60 · 2018 30/70
HISTORY = {
    "AAA": (Year(2015, 10, 100), Year(2016, -5, 80), Year(2017, 40, 100), Year(2018, 50, 120),
            Year(2019, unavailable="missing capex"), Year(2020, 30, 150)),
    "BBB": (Year(2016, 20, 50), Year(2017, 25, 60), Year(2018, 30, 70)),
}


def _class_doc(**over):
    doc = {"name": "toy", "version": 1, "decided_by": "test",
           "members": [{"label": "AAA", "name": "A", "cik": "1", "role": "memory",
                        "years": {"from": None, "to": None}, "why": "subject"},
                       {"label": "BBB", "name": "B", "cik": "2", "role": "memory",
                        "years": {"from": None, "to": None}, "why": "peer"}],
           "excluded": [{"name": "C", "why": "not on EDGAR"}]}
    doc.update(over)
    return doc


def _write(tmp_path, doc, name="toy_v1.yaml"):
    from src.feature_engineer.base_rates.config import content_hash
    doc = {**doc, "content_hash": content_hash(doc)}
    p = tmp_path / name
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    return p


# ═══ AC-F11.1 — the declared class ═════════════════════════════════════════

def test_ac_f11_1_a_value_changed_without_a_version_change_refuses(tmp_path):
    from src.feature_engineer.base_rates.config import load_class
    from src.feature_engineer.errors import AssumptionsMutatedError

    p = _write(tmp_path, _class_doc())
    assert [m.label for m in load_class(p).members] == ["AAA", "BBB"]
    doc = yaml.safe_load(p.read_text())
    doc["members"][1]["cik"] = "99"
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    with pytest.raises(AssumptionsMutatedError):
        load_class(p)


def test_ac_f11_1_every_member_and_exclusion_says_why(tmp_path):
    from src.feature_engineer.base_rates.config import load_class
    doc = _class_doc()
    doc["excluded"][0]["why"] = ""
    with pytest.raises(ValueError, match="why"):
        load_class(_write(tmp_path, doc))


def test_ac_f11_1_the_published_memory_class_is_victors(tmp_path):
    """`D1`/`D3`: Micron, both SanDisks, Western Digital FY2017–FY2025 only."""
    from src.feature_engineer.base_rates.config import load_published_class
    c = load_published_class("memory", 1)
    assert {m.cik for m in c.members} == {"723125", "1000180", "2023554", "106040"}
    wdc = next(m for m in c.members if m.cik == "106040")
    assert (wdc.year_from, wdc.year_to, wdc.role) == (2017, 2025, "memory_and_storage")


# ═══ AC-F11.2 / AC-F11.3 — point in time, one formula ══════════════════════

def test_ac_f11_2_a_year_filed_after_as_of_is_not_used():
    from src.feature_engineer.base_rates.service import member_years
    late = (Year(2024, 10, 100, filed=date(2025, 10, 1)),)
    used, excluded = member_years({"AAA": late}, as_of=AS_OF, ranges={})
    assert used == {"AAA": []} and excluded == []


def test_ac_f11_3_an_unresolvable_year_is_excluded_and_named_never_zero():
    from src.feature_engineer.base_rates.service import member_years
    used, excluded = member_years(HISTORY, as_of=AS_OF, ranges={})
    assert [y.fiscal_year for y in used["AAA"]] == [2015, 2016, 2017, 2018, 2020]
    assert excluded == [{"member": "AAA", "fiscal_year": 2019, "reason": "missing capex"}]


def test_ac_f11_3_a_member_year_range_is_honoured():
    from src.feature_engineer.base_rates.service import member_years
    used, _ = member_years(HISTORY, as_of=AS_OF, ranges={"BBB": (2017, 2017)})
    assert [y.fiscal_year for y in used["BBB"]] == [2017]


def test_ac_f11_3_member_fcff_is_F10_annual_basis_on_a_real_row():
    """The service consumes `F10` `annual_history` itself — no second FCFF formula here."""
    import ast
    import pathlib
    src = "\n".join(p.read_text() for p in pathlib.Path(
        "src/feature_engineer/base_rates").glob("*.py"))
    assert "annual_history" in src
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name):
            assert node.id not in ("operating_cash_flow", "capex"), "a second D6 formula"


# ═══ AC-F11.4 — the three statistics, hand-counted ═════════════════════════

def _used():
    from src.feature_engineer.base_rates.service import member_years
    return member_years(HISTORY, as_of=AS_OF, ranges={})[0]


def test_ac_f11_4_margin_reach():
    """Margins: AAA .10 −.0625 .40 .4167 .20 · BBB .40 .4167 .4286. Threshold .40 ⇒
    all 5/8 (AAA 2017 2018 · BBB all three); excluding AAA 3/3."""
    from src.feature_engineer.base_rates.stats import margin_reach
    r = margin_reach(_used(), [(10, Decimal("0.40"))], subject="AAA")
    assert r == [{"threshold": "0.40", "periods": 10, "all": {"hits": 5, "n": 8},
                  "excluding_subject": {"hits": 3, "n": 3}}]


def test_ac_f11_4_positive_runs_break_at_a_loss_and_at_a_missing_year():
    """AAA: [2015] · [2017 2018] · [2020] (2016 is a loss, 2019 is missing) · BBB: [2016–2018].
    Runs ≥ 2 years: all 2/4 · excluding AAA 1/1. Runs ≥ 3: all 1/4 · excl 1/1."""
    from src.feature_engineer.base_rates.stats import positive_runs
    r = positive_runs(_used(), [2, 3], subject="AAA")
    assert r == [{"at_least_years": 2, "all": {"hits": 2, "n": 4},
                  "excluding_subject": {"hits": 1, "n": 1}},
                 {"at_least_years": 3, "all": {"hits": 1, "n": 4},
                  "excluding_subject": {"hits": 1, "n": 1}}]


def test_ac_f11_4_revenue_cagr_over_overlapping_windows():
    """2-year windows (both ends present): AAA 2015→17 100→100 · 2016→18 80→120 ·
    2018→20 120→150 · BBB 2016→18 50→70. Required 15 %/yr ⇒ (1.15)² = 1.3225:
    AAA 80→120 (1.5) yes · 120→150 (1.25) no · 100→100 no · BBB 1.4 yes ⇒ all 2/4, excl 1/1."""
    from src.feature_engineer.base_rates.stats import revenue_cagr_reach
    r = revenue_cagr_reach(_used(), [(2, Decimal("0.15"))], subject="AAA")
    assert r == [{"periods": 2, "required_growth": "0.15", "all": {"hits": 2, "n": 4},
                  "excluding_subject": {"hits": 1, "n": 1}, "windows": "overlapping"}]


# ═══ AC-F11.5 — thresholds come from the subject's trail ═══════════════════

V2_TRAIL = {"implied_by_duration": [
    {"explicit_years": 5, "status": "NO_ROOT_IN_BRACKET", "value": None,
     "share_of_trailing_revenue": None},
    {"explicit_years": 10, "status": "SOLVED", "value": "0.15",
     "share_of_trailing_revenue": "0.40"}]}


def test_ac_f11_5_every_threshold_is_a_value_from_implied_by_duration():
    from src.feature_engineer.base_rates.service import thresholds_from
    t = thresholds_from(V2_TRAIL)
    assert t == {"margin": [(10, Decimal("0.40"))], "growth": [(10, Decimal("0.15"))],
                 "runs": [5, 10]}


def test_ac_f11_5_a_trail_without_a_duration_table_refuses():
    from src.feature_engineer.base_rates.service import thresholds_from
    with pytest.raises(ValueError, match="implied_by_duration"):
        thresholds_from({"implied": {}})


def test_ac_f11_5_no_threshold_literal_in_base_rates_code():
    import pathlib
    import re
    src = "\n".join(p.read_text() for p in pathlib.Path(
        "src/feature_engineer/base_rates").glob("*.py"))
    code = re.sub(r'"""[\s\S]*?"""|#.*', "", src)
    assert not re.search(r"(?<![\w.])0\.\d+", code), "a decimal literal in base_rates/"


# ═══ AC-F11.6 / AC-F11.7 — n everywhere; the published table ═══════════════

def test_ac_f11_6_every_rate_renders_hits_over_n_and_zero_n_says_so():
    from src.feature_engineer.base_rates.render import rate
    assert rate({"hits": 2, "n": 8}) == "2/8 (25.0 %)"
    assert rate({"hits": 0, "n": 0}) == "no observations"


def test_ac_f11_7_the_published_table_is_the_base_rate_book_with_pages_and_sums():
    from src.feature_engineer.base_rates.config import load_published_table
    t = load_published_table("base_rate_book_2016")
    assert t.source["authors"] == "Michael J. Mauboussin, Dan Callahan, Darius Majd"
    h10 = next(h for h in t.horizons if h["years"] == 10)
    assert h10["total"] == 2886 and h10["page"] == {"printed": 31, "pdf": 32}
    assert h10["rates_page"] == {"printed": 24, "pdf": 25}


def test_ac_f11_7_a_horizon_whose_bins_do_not_sum_refuses(tmp_path):
    from src.feature_engineer.base_rates.config import CONFIG_DIR, load_published_table
    doc = yaml.safe_load((CONFIG_DIR / "published_base_rate_book_2016.yaml").read_text())
    doc["horizons"][0]["bins"][0]["observations"] += 1
    p = tmp_path / "published_x.yaml"
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    with pytest.raises(ValueError, match="sum"):
        load_published_table("x", root=tmp_path)


def test_ac_f11_7_a_required_rate_inside_a_bin_is_a_bracket_never_interpolated():
    """10-yr bins at and above 25 %: 25-30 0 · 30-35 0 · … ⇒ [0, 0] of 2,886 at 28.3 %;
    at 22 %: inside 20-25 (6) ⇒ between ≥25 (0) and ≥20 (6)."""
    from src.feature_engineer.base_rates.config import load_published_table
    from src.feature_engineer.base_rates.stats import published_bracket
    t = load_published_table("base_rate_book_2016")
    assert published_bracket(t, 10, Decimal("0.282629394532")) == {
        "at_least": 0, "at_most": 0, "n": 2886}
    assert published_bracket(t, 10, Decimal("0.22")) == {"at_least": 0, "at_most": 6, "n": 2886}
    assert published_bracket(t, 7, Decimal("0.39")) is None          # the book has no 7-yr column


# ═══ AC-F11.8 — staging and isolation ══════════════════════════════════════

def test_ac_f11_8_base_rates_import_no_analyst_domain_no_llm_no_vendor_sdk():
    import ast
    import pathlib
    for p in pathlib.Path("src/feature_engineer/base_rates").glob("*.py"):
        for node in ast.walk(ast.parse(p.read_text())):
            mods = ([a.name for a in node.names] if isinstance(node, ast.Import)
                    else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            for m in mods:
                assert not m.startswith(("src.fundamental", "src.shared.llm", "anthropic",
                                         "requests")), f"{p}: imports {m}"


def test_ac_f11_8_the_part_is_computed_so_the_blind_view_withholds_it():
    from src.feature_engineer.base_rates.render import KIND
    from src.fundamental.bundle.models import BLIND_WITHHELD_KINDS
    assert KIND == "computed" and KIND in BLIND_WITHHELD_KINDS


def test_ac_f11_6_the_rendered_part_names_members_n_caveats_and_pages():
    from src.feature_engineer.base_rates.config import load_published_table
    from src.feature_engineer.base_rates.render import as_bundle_part
    from src.feature_engineer.base_rates.service import BaseRates, compute

    class Cls:
        name, version, content_hash = "toy", 1, "sha256:x"
        members = ()

    res = compute(reference_class=Cls, history=HISTORY, subject="AAA", as_of=AS_OF,
                  trail=V2_TRAIL, published=load_published_table("base_rate_book_2016"),
                  ranges={})
    assert isinstance(res, BaseRates)
    text = as_bundle_part(res)["content"]
    for must in ("hits/n", "excluding the subject", "overlapping windows", "2015 dollars",
                 "sales growth", "p. 24", "p. 31", "missing capex"):
        assert must in text, must
    assert json.loads(res.to_json())["class"]["name"] == "toy"
