"""D-02 `fundamental@v1` — §5.3's 45 `f_*` features."""
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from src.feature_engineer.contracts.sets.fundamental_v1 import FUNDAMENTAL_V1
from src.feature_engineer.fundamental import build, growth, items, ratios


def _canonical(periods, **items_by_name):
    """A per-filing canonical frame — one row per reported period."""
    rows = []
    for i, end in enumerate(periods):
        row = {"ticker": "A", "period_end": pd.Timestamp(end),
               "period_type": "quarterly",
               "filing_date": pd.Timestamp(end) + pd.Timedelta(days=40),
               "accession_id": f"acc-{i}", "source": "edgar", "restated": False}
        for name, values in items_by_name.items():
            row[name] = values[i]
        rows.append(row)
    return pd.DataFrame(rows)


QUARTERS = [date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30),
            date(2025, 12, 31), date(2026, 3, 31)]


# --------------------------------------------------------------------------- #
# The contract
# --------------------------------------------------------------------------- #

def test_ac_2_38_the_contract_declares_the_fundamental_45_plus_group_c():
    """§5.3 — *Fundamental (45)* **plus Group C (2)**, all `f_`-prefixed.

    ★ With `price_ohlcv@v1`'s 14 that is **61 of 61** — the whole declared set.
    ⚠ Group C sits here rather than in its own contract because both members are
    `f_*` and both come from the same as-of joined frame; §5.3 counts them
    separately only because the legacy built them in a different module.
    """
    assert len(FUNDAMENTAL_V1.features) == 47
    assert all(f.name.startswith("f_") for f in FUNDAMENTAL_V1.features)

    from src.feature_engineer.contracts.sets.price_ohlcv_v1 import PRICE_OHLCV_V1

    assert len(PRICE_OHLCV_V1.features) + len(FUNDAMENTAL_V1.features) == 61


def test_ac_2_38_the_doubled_prefix_is_kept_not_quietly_fixed():
    """⚠ §5.3 records `f_f_net_margin_trend_4` as an inherited naming defect
    *"recorded rather than fixed in the move"*. ★ FE-6: a rename is a
    **tombstone plus a new version**, not an edit — renaming here would break
    every model whose contract names the old column."""
    assert "f_f_net_margin_trend_4" in [f.name for f in FUNDAMENTAL_V1.features]


def test_ac_2_38_the_contract_is_derived_from_the_build_tables():
    """FE-4 in the declaration layer — ⚠ a second hand-maintained list is *two
    implementations of one concept*, and §5.3 shows the scar of one."""
    assert set(build.FEATURE_NAMES) == {f.name for f in FUNDAMENTAL_V1.features}


# --------------------------------------------------------------------------- #
# ★★ The as-of join — where the look-ahead lives
# --------------------------------------------------------------------------- #

def test_ac_2_39_a_filing_is_never_joined_to_a_date_before_it_was_filed():
    """★★★ ⚠ `merge_asof(direction="nearest")` attaches a filing published
    *after* the date whenever that one is closer — look-ahead that reads as a
    rounding choice and makes a backtest unfalsifiably good."""
    canonical = _canonical(QUARTERS, revenue=[100.0] * 5)
    panel = pd.DataFrame({"ticker": ["A"] * 3,
                          "date": pd.to_datetime(["2025-04-01", "2025-05-10",
                                                  "2025-05-11"])})
    joined = items.as_of_join(panel, canonical)
    # Q1 ends 2025-03-31 and is FILED 2025-05-10.
    assert pd.isna(joined["accession_id"].iloc[0]), "before the filing date"
    assert joined["accession_id"].iloc[1] == "acc-0"
    assert joined["accession_id"].iloc[2] == "acc-0"


def test_ac_2_39_the_join_is_keyed_on_filing_date_not_period_end():
    """★★ ⚠ **A quarter ending 31 March is not knowable on 31 March.** Joining on
    the period end is worth roughly one quarter of hindsight on every row — the
    single most expensive look-ahead available in fundamentals."""
    canonical = _canonical(QUARTERS, revenue=[100.0] * 5)
    panel = pd.DataFrame({"ticker": ["A"], "date": pd.to_datetime(["2025-04-15"])})
    joined = items.as_of_join(panel, canonical)
    assert pd.isna(joined["revenue"].iloc[0])


# --------------------------------------------------------------------------- #
# ★★ Per-filing before the join
# --------------------------------------------------------------------------- #

def test_ac_2_40_multi_period_features_survive_a_short_panel_window():
    """★★★ **The structural bug this module is shaped to avoid.** ⚠ Measured: a
    120-day panel window holds **three** NVDA filings, so a four-filing lag
    computed *after* the join is null on every row — and the failure looks
    exactly like sparse data rather than a discarded history."""
    canonical = _canonical(QUARTERS, revenue=[100.0, 110.0, 120.0, 130.0, 200.0])
    change = growth.change(canonical, "revenue", lag=4)
    assert not pd.isna(change.iloc[-1])
    assert change.iloc[-1] == pytest.approx(1.0)      # 200 vs 100


def test_ac_2_40_growth_is_denominated_on_the_absolute_prior():
    """⚠ A swing from −100 to +50 is a **rise**. Dividing by a signed prior flips
    the sign of every recovery from a loss — the case a growth feature most
    needs to get right."""
    canonical = _canonical(QUARTERS[:2], net_income=[-100.0, 50.0])
    assert growth.change(canonical, "net_income", lag=1).iloc[-1] > 0


def test_ac_2_40_a_margin_trend_needs_a_full_window():
    """⚠ *A line through two points is a line, not a trend* — and `polyfit`
    returns one without complaint."""
    canonical = _canonical(QUARTERS, revenue=[100.0] * 5,
                           net_income=[10.0, 12.0, 14.0, 16.0, 18.0])
    trend = growth.margin_trend(canonical, "net")
    assert pd.isna(trend.iloc[2]), "fewer than four periods"
    assert trend.iloc[-1] == pytest.approx(0.02)      # +2 margin points/quarter


# --------------------------------------------------------------------------- #
# Undefined is null, never a number
# --------------------------------------------------------------------------- #

def test_ac_2_41_a_margin_on_zero_revenue_is_null_not_infinite():
    """FE-14 — ★ *a margin computed on zero revenue is not enormous, it is
    undefined*, and pandas carries `inf` into a model without complaint."""
    canonical = _canonical(QUARTERS[:1], revenue=[0.0], net_income=[5.0])
    assert pd.isna(ratios.net_margin(canonical).iloc[0])


def test_ac_2_41_roe_on_negative_equity_is_null_not_a_sign_flip():
    """⚠ Book equity goes negative after large buybacks. `net_income / equity`
    then reports a **positive** ROE for a profitable company with negative book
    value — arithmetically true and the opposite of the truth."""
    canonical = _canonical(QUARTERS[:1], net_income=[10.0],
                           stockholders_equity=[-50.0])
    assert pd.isna(ratios.roe(canonical).iloc[0])


def test_ac_2_41_a_debt_free_company_has_undefined_coverage_not_infinite():
    """⚠ `inf` ranks first in any sort, so a company with no debt would top a
    *safest* ranking through a division by zero rather than its balance sheet."""
    canonical = _canonical(QUARTERS[:1], operating_income=[100.0],
                           interest_expense=[0.0])
    assert pd.isna(ratios.interest_coverage(canonical).iloc[0])


def test_ac_2_41_cash_conversion_survives_a_loss_making_quarter():
    """★ `allow_negative=True` — a loss is exactly where this ratio is
    interesting, and nulling it hides the cases the feature exists to flag."""
    canonical = _canonical(QUARTERS[:1], operating_cash_flow=[50.0],
                           net_income=[-25.0])
    assert ratios.ocf_to_net_income(canonical).iloc[0] == pytest.approx(-2.0)


# --------------------------------------------------------------------------- #
# Piotroski — unknown is not failure
# --------------------------------------------------------------------------- #

def test_ac_2_42_an_uncomputable_signal_nulls_the_score_rather_than_scoring_zero():
    """★★ FE-14 — ⚠ `pandas.sum` skips NaN by default, which scores a bank's
    missing margin signals as zeros and reports a **low F-score for a company
    that was never tested**. *We could not tell* and *it failed* are different
    facts, and only one belongs in a ranking."""
    canonical = _canonical(QUARTERS, total_assets=[1000.0] * 5,
                           net_income=[10.0] * 5)     # no cash flow at all
    assert pd.isna(growth.piotroski(canonical)["f_piotroski_f"].iloc[-1])


def test_ac_2_42_the_f_score_is_on_a_seven_point_scale():
    """⚠ Piotroski's original is nine signals; two need inputs a bank never
    reports. ★ **7/7 and 7/9 are different claims** — the range says which."""
    spec = next(f for f in FUNDAMENTAL_V1.features if f.name == "f_piotroski_f")
    assert spec.range == (0.0, 7.0)


# --------------------------------------------------------------------------- #
# Sector z — FE-13's hazard
# --------------------------------------------------------------------------- #

def test_ac_2_43_sector_z_is_null_when_the_peer_group_is_too_small():
    """⚠ A z-score over two observations is **±0.707 by construction** and says
    nothing about the company (CN-10 — say so rather than emit it)."""
    panel = pd.DataFrame({"ticker": ["A", "B"], "date": pd.to_datetime(["2026-01-02"] * 2)})
    z = growth.sector_z(panel, pd.Series([1.0, 2.0]), pd.Series(["Tech", "Tech"]))
    assert z.isna().all()


def test_ac_2_43_sector_z_is_computed_within_a_date():
    """★★ FE-13 — pooling dates scores a 2019 row against 2026's distribution."""
    dates = pd.to_datetime(["2026-01-02"] * 3 + ["2026-01-03"] * 3)
    panel = pd.DataFrame({"ticker": list("ABC") * 2, "date": dates})
    values = pd.Series([1.0, 2.0, 3.0, 100.0, 200.0, 300.0])
    z = growth.sector_z(panel, values, pd.Series(["T"] * 6))
    # ★ Both days have the same SHAPE, so the same z — a pooled z would not.
    assert z.iloc[0] == pytest.approx(z.iloc[3])


# --------------------------------------------------------------------------- #
# A null block never silently validates
# --------------------------------------------------------------------------- #

def test_ac_2_44_a_contract_of_f_features_with_no_fundamentals_raises():
    """★ FE-1 — ⚠ 45 columns of null **validate, train, and read as a filer that
    reports nothing.** The refusal is the only thing that distinguishes them."""
    from src.feature_engineer.errors import MissingFeatureError
    from src.feature_engineer.ml_features.assemble import build_panel

    class _Report:
        report_id, verdict, blocked = "t", "PROCEED", ()

    panel = pd.DataFrame({"ticker": ["A"], "date": pd.to_datetime(["2026-01-02"])})
    with pytest.raises(MissingFeatureError):
        build_panel(contract=FUNDAMENTAL_V1, price_panel=panel,
                    calendar_report=_Report(), as_of=date(2026, 1, 2),
                    adj_as_of=date(2026, 1, 2))



# --------------------------------------------------------------------------- #
# ★★ Group C — the two that need a price
# --------------------------------------------------------------------------- #

def test_ac_2_45_a_share_count_is_not_divided_out_of_minor_units():
    """★★★ ⚠ *Found 2026-08-27:* `canonical_frame` divided **every** column by
    100 to leave minor units, and a share count went with it — NVDA's real
    **24 285 000 000** diluted shares became **242 850 000**, so market
    capitalisation came out **100× too small**.

    ★ Same class as **DE-52**, one layer up: a non-monetary quantity carried
    through a monetary conversion.
    """
    from src.feature_engineer.fundamental.items import NON_MONETARY, canonical_frame

    assert "diluted_shares" in NON_MONETARY
    rows = pd.DataFrame({
        "ticker": ["A"], "period_end": [pd.Timestamp("2026-03-31")],
        "period_type": ["quarterly"],
        "filing_date": [pd.Timestamp("2026-05-10")], "accession_id": ["a-0"],
        "source": ["edgar"], "restated": [False],
        "WeightedAverageNumberOfDilutedSharesOutstanding_minor": [24_285_000_000],
        "NetIncomeLoss_minor": [100_000_000_000],      # $1.0bn in minor units
    })
    frame = canonical_frame(rows)
    assert frame["diluted_shares"].iloc[0] == 24_285_000_000
    assert frame["net_income"].iloc[0] == 1_000_000_000.0


def test_ac_2_45_graham_is_null_when_the_company_lost_money():
    """⚠ The legacy clipped the product at zero **before** the square root, which
    turns *"this company lost money"* into a Graham number of **0.00** — finite,
    plottable and rankable for a case the formula has no answer to."""
    from src.feature_engineer.fundamental.group_c import graham_number

    joined = pd.DataFrame({"diluted_shares": [1000.0, 1000.0],
                           "net_income": [-500.0, 500.0],
                           "stockholders_equity": [2000.0, 2000.0]})
    values = graham_number(joined)
    assert pd.isna(values.iloc[0]), "a loss has no Graham number"
    assert values.iloc[1] > 0


def test_ac_2_45_the_moat_stability_term_actually_varies():
    """★★ ⚠ The legacy's `clip(1 − std(ROA), 0, 1)` spanned **0.95–0.99** for
    real filers — a 20 % weight on a near-constant. The coefficient-of-variation
    form spans the range."""
    from src.feature_engineer.fundamental.ratios import _ratio

    steady = _ratio(pd.Series([0.005]), pd.Series([0.05]))     # cv = 0.1
    erratic = _ratio(pd.Series([0.15]), pd.Series([0.05]))     # cv = 3.0
    c_steady = 1.0 / (1.0 + steady.iloc[0])
    c_erratic = 1.0 / (1.0 + erratic.iloc[0])
    assert c_steady > 0.9 and c_erratic < 0.3


def test_ac_2_45_group_c_features_are_declared_anchors():
    """⚠⚠ RA-14/RA-151 — they carry the price by construction, so D-01's blind
    passes may never see them. §6.2 and §6.3 publish different sets to the two
    seats for exactly this reason."""
    from src.feature_engineer.contracts.sets.fundamental_v1 import ANCHOR_FEATURES

    assert "f_graham_number_ratio" in ANCHOR_FEATURES
    assert "f_market_to_book" in ANCHOR_FEATURES


# --------------------------------------------------------------------------- #
# ★★★ FE-2 — immutability, enforced on the CONTENT
# --------------------------------------------------------------------------- #

def test_ac_2_46_changing_membership_bumped_the_version():
    """★★ FE-2 — *"A contract version is immutable once published. Changing any
    `formula_id`, range, or **membership** produces a NEW version."*

    ⚠ Group C took `fundamental` from **45 to 47** features and the version
    stayed at 1, so two different feature sets shared one identity.
    """
    # ✏ v3 (2026-09-14, `DX-103`): `CANONICAL` gained fallback tags, so the SAME
    #   membership takes different inputs — the version moved with the values.
    assert FUNDAMENTAL_V1.version == 3
    assert len(FUNDAMENTAL_V1.features) == 47


def test_ac_2_46_the_content_hash_changes_when_membership_does():
    """★★ ⚠ *"Hashing the CONTENT rather than trusting the version number is what
    makes the rule mechanical … whatever the file says."* The hash is the part
    that cannot be talked round."""
    import dataclasses

    trimmed = dataclasses.replace(
        FUNDAMENTAL_V1, features=FUNDAMENTAL_V1.features[:-2])
    assert trimmed.content_hash != FUNDAMENTAL_V1.content_hash


def test_ac_2_46_the_model_manifest_carries_the_content_hash():
    """★★★ **The hole this closes, measured 2026-08-27.** Two artifacts — one
    with **59** features, one with **61** — both declared
    `price_and_fundamental@v1`, and `check_parity` compares **name and version**,
    so it waved the difference through. FE-2's own mechanism existed and the
    manifest did not carry it."""
    from src.models.artifact.manifest import FeatureContractRef

    assert "content_hash" in FeatureContractRef.__dataclass_fields__
    ref = FeatureContractRef("c", 1, "sha256:abc")
    assert ref.to_json_obj()["content_hash"] == "sha256:abc"


def test_ac_2_46_parity_fails_on_a_membership_change_under_one_version():
    """★ The check that would have caught it."""
    import dataclasses

    from src.models.artifact.manifest import FeatureContractRef
    from src.models.governance.parity import check_parity

    class _Manifest:
        feature_contract = FeatureContractRef(
            "fundamental", FUNDAMENTAL_V1.version, "sha256:a-different-membership")
        decision_anchor = "open"

    class _Artifact:
        manifest = _Manifest()
        feature_names = tuple(f.name for f in FUNDAMENTAL_V1.features)
        artifact_id = "sha256:test"

    panel = pd.DataFrame({name: [1.0] for name in _Artifact.feature_names})
    # `coverage()` groups by ticker, so the panel needs its key columns.
    panel["ticker"] = ["A"]
    panel["date"] = [pd.Timestamp("2026-08-26")]
    report = check_parity(_Artifact(), panel, contract=FUNDAMENTAL_V1,
                          raise_on_halt=False)
    assert any("CONTENT differs" in r for r in report.reasons), report.reasons
    del dataclasses
