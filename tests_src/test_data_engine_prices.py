"""D-07 price adjustment — AC-7.43…7.46, AC-7.57…7.59, AC-7.61 (§5C.7, CT-7.1).

Tier: invariant/property + data contract (constitution §4). The invariant under
test is **INV-2 determinism**, not INV-1 — §5C.7's whole argument is that split
adjustment is a *restatement* hazard rather than a classical look-ahead.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.data_engine.contracts.panels import require_raw, validate_price_panel
from src.data_engine.errors import (
    AdjAsOfRequiredError, ContractViolationError, RawRequiredError,
)
from src.data_engine.pit.adjustment import (
    assert_ex_dividend_convention, assert_factor_discipline, assert_matches_vendor,
    build_price_panel, dividend_multiplier, split_multiplier,
)
from tests_src.data_engine_fixtures import dividend, raw_series, split

AFTER = date(2024, 8, 1)


def test_ac_7_43_raw_is_the_system_of_record_and_the_panel_is_derived():
    """AC-7.43 — the store holds the RAW series plus events; adjusted is derived (DE-27).

    The evidence that it is derived and not ingested: the SAME raw rows and the
    SAME events produce a different adjusted panel at a different `adj_as_of`.
    An ingested adjusted series could not do that.
    """
    raw, events = raw_series(), [split()]
    before = build_price_panel(raw, events, date(2024, 6, 1))
    after = build_price_panel(raw, events, AFTER)

    assert int(before.iloc[1]["adj_close_minor"]) == 120890      # $1,208.90, raw
    assert int(after.iloc[1]["adj_close_minor"]) == 12089        # $120.89, adjusted
    assert int(before.iloc[1]["close_minor"]) == int(after.iloc[1]["close_minor"])


def test_ac_7_44_only_events_on_or_before_adj_as_of_contribute():
    """AC-7.44 — a re-run later produces byte-identical prices (DE-28, INV-2).

    ★ This is the whole point of §5C.7. A backtest run on 2024-06-01 saw NVDA at
    $1,150; re-run today against today's vendor series it sees $115. Pinning
    `adj_as_of` is what makes the two agree.
    """
    raw, events = raw_series(), [split()]
    first = build_price_panel(raw, events, date(2024, 6, 1))
    rerun = build_price_panel(raw, events, date(2024, 6, 1))
    pd.testing.assert_frame_equal(first.drop(columns=["fetched_at"]),
                                  rerun.drop(columns=["fetched_at"]))
    assert (first["adj_factor"] == 1.0).all(), "a future split must not reach back"


def test_ac_7_45_non_scale_invariant_use_must_read_the_raw_series():
    """AC-7.45 — absolute price/volume, share counts, the M-1 screen use RAW (DE-29).

    ⚠ M-1 is a MANDATE rule, so this is a compliance defect and not only a
    modelling one: on an adjusted history a reverse split makes a stock that
    traded at $0.50 look like $10 retroactively.
    """
    raw, events = raw_series(), [split()]
    adjusted = build_price_panel(raw, events, AFTER)
    with pytest.raises(RawRequiredError, match="penny-stock"):
        require_raw(adjusted, "M-1 penny-stock screen")

    unadjusted = build_price_panel(raw, events, None)
    assert require_raw(unadjusted, "M-1 penny-stock screen") is unadjusted


def test_ac_7_46_panel_records_adj_as_of_and_two_panels_do_not_compare_equal():
    """AC-7.46 — the panel records its adj_as_of (DE-30, CT-7.1, FE-8)."""
    raw, events = raw_series(), [split()]
    a = build_price_panel(raw, events, date(2024, 6, 1))
    b = build_price_panel(raw, events, AFTER)

    assert a["adj_as_of"].iloc[0].date() == date(2024, 6, 1)
    assert b["adj_as_of"].iloc[0].date() == AFTER
    assert not a[["adj_close_minor", "adj_open_minor"]].equals(
        b[["adj_close_minor", "adj_open_minor"]]
    ), "two panels over the same dates with different adj_as_of must differ"


def test_ac_7_46_raw_panel_carries_a_null_adj_as_of():
    """AC-7.46 — `None` means raw, and the panel says so rather than implying it."""
    panel = build_price_panel(raw_series(), [split()], None)
    assert panel["adj_as_of"].isna().all()
    assert not panel["is_adjusted"].any()
    assert (panel["adj_factor"] == 1.0).all()


def test_ac_7_57_one_materialised_factor_drives_every_adjusted_field():
    """AC-7.57 — adj_factor is materialised per (ticker, date, adj_as_of) (DE-42).

    QA-84's original wording derived `adj_open` from `adj_close/close`, which
    presupposes a vendor `adj_close`. Under DE-27 the factor comes from the
    EVENTS, and both adjusted fields are `raw x factor` from the same number —
    "a factor derived independently at four call sites is four chances to derive
    it differently".
    """
    panel = build_price_panel(raw_series(), [split()], AFTER)
    f = panel["adj_factor"]
    assert (panel["adj_close_minor"] == (panel["close_minor"] * f + 0.5).astype(int)).all()
    assert (panel["adj_open_minor"] == (panel["open_minor"] * f + 0.5).astype(int)).all()
    assert f.iloc[1] == pytest.approx(0.1), "10:1 divides pre-split prices by ten"


def test_ac_7_58_factor_changes_only_on_dates_the_calendar_check_flags():
    """AC-7.58 — DE-43's real check, because the cross-field one is a tautology (QA-85).

    `adj_close/close == adj_open/open` is trivially true of a reconstruction, so
    it tests nothing. This one can fail: an adjustment appearing on a date with
    no corporate action behind it is a vendor artifact.
    """
    events = [split()]
    panel = build_price_panel(raw_series(), events, AFTER)
    assert_factor_discipline(panel, [e.event_date for e in events])

    with pytest.raises(ContractViolationError, match="calendar check did not flag"):
        assert_factor_discipline(panel, [])


def test_ac_7_58_factor_is_strictly_positive():
    """AC-7.58 — a non-positive factor is nonsense that still has a dtype (DE-43)."""
    with pytest.raises(ContractViolationError, match="non-positive split ratio"):
        split_multiplier(0, 1)


def test_ac_7_58_reconstruction_is_compared_against_the_vendor_where_it_exists():
    """AC-7.58 — DE-43's other half: the only non-self-referential check."""
    panel = build_price_panel(raw_series(), [split()], AFTER)
    vendor = pd.DataFrame({
        "ticker": panel["ticker"], "date": panel["date"],
        "adj_open_minor": panel["adj_open_minor"],
    })
    assert_matches_vendor(panel, vendor)

    vendor.loc[1, "adj_open_minor"] = int(vendor.loc[1, "adj_open_minor"]) + 500
    with pytest.raises(ContractViolationError, match="disagree with the vendor"):
        assert_matches_vendor(panel, vendor)


def test_ac_7_59_ex_dividend_dates_get_their_own_assertion():
    """AC-7.59 — the ex-date must NOT carry its own dividend factor (DE-44, QA-91).

    ★ The failure this catches: the ex-date *open already reflects the drop* in
    the raw price, so a close-derived factor applied to the ex-date itself
    subtracts the dividend twice. DE-43's monotonicity test passes either
    convention, which is exactly why this needs a targeted check.
    """
    rows = [
        (date(2024, 5, 14), 41000, 41500, 40800, 41000, 20_000_000),
        (date(2024, 5, 15), 41000, 41500, 40800, 41500, 21_000_000),
        (date(2024, 5, 16), 41400, 41800, 41200, 41600, 22_000_000),   # ex-date
        (date(2024, 5, 17), 41600, 42000, 41500, 41900, 20_500_000),
    ]
    div = dividend(ticker="MSFT", ex=date(2024, 5, 16), cash_minor=75)
    panel = build_price_panel(raw_series("MSFT", rows), [div], AFTER)

    assert_ex_dividend_convention(panel, [div])

    ex_row = panel[panel["date"] == pd.Timestamp(2024, 5, 16)].iloc[0]
    prev_row = panel[panel["date"] == pd.Timestamp(2024, 5, 15)].iloc[0]
    assert float(ex_row["adj_factor"]) == 1.0, "the ex-date itself is not discounted"
    assert float(prev_row["adj_factor"]) == pytest.approx(1 - 75 / 41500)


def test_ac_7_59_a_double_counted_dividend_is_detected():
    """AC-7.59 — the assertion FIRES when the convention is wrong (L4 IM-3's standard)."""
    rows = [
        (date(2024, 5, 15), 41000, 41500, 40800, 41500, 21_000_000),
        (date(2024, 5, 16), 41400, 41800, 41200, 41600, 22_000_000),
    ]
    div = dividend(ticker="MSFT", ex=date(2024, 5, 16), cash_minor=75)
    panel = build_price_panel(raw_series("MSFT", rows), [div], AFTER)
    # Simulate the wrong convention: the drop applied to the ex-date as well.
    panel.loc[panel["date"] == pd.Timestamp(2024, 5, 16), "adj_factor"] = 1 - 75 / 41500
    with pytest.raises(ContractViolationError, match="double-counts"):
        assert_ex_dividend_convention(panel, [div])


def test_ac_7_61_omitting_adj_as_of_raises_and_none_is_the_explicit_raw_value():
    """AC-7.61 — DE-45. A default adjustment is DE-6.4's defaulted as_of, renamed."""
    with pytest.raises(AdjAsOfRequiredError, match="pass None to mean the RAW series"):
        build_price_panel(raw_series(), [split()])

    assert build_price_panel(raw_series(), [split()], None) is not None


def test_ac_7_15_price_panel_satisfies_dc_1():
    """AC-7.15 — DC-1: monotonic dates, no future dates, no null close, OHLC ordering."""
    panel = build_price_panel(raw_series(), [split()], AFTER)
    validate_price_panel(panel)

    broken = panel.copy()
    broken.loc[0, "low_minor"] = broken.loc[0, "high_minor"] + 1
    with pytest.raises(ContractViolationError, match="OHLC ordering"):
        validate_price_panel(broken)

    future = panel.copy()
    future.loc[0, "date"] = pd.Timestamp.utcnow().tz_localize(None).normalize() \
        + pd.Timedelta(days=5)
    with pytest.raises(ContractViolationError, match="dated after"):
        validate_price_panel(future.sort_values("date"))


def test_dividend_multiplier_refuses_an_uncomputable_reference():
    """DE-14 — an unknown prior close is not 1.0, and it is not zero either."""
    with pytest.raises(ContractViolationError, match="prior close"):
        dividend_multiplier(75, 0)
