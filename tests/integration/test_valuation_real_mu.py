"""`F10` on REAL data — Micron's recorded EDGAR facts (`AC-F10.7`, `DX-103`).

★ The figures asserted here are read off the FILING (`MU_FY2025Q3_10Q.txt`), not
off the valuation's own output — so this grades the data path, not itself.
"""

from __future__ import annotations

import pathlib
from datetime import date

import pandas as pd
import pytest

from src.data_engine.pit.snapshot import assemble_rows

REPO = pathlib.Path(__file__).resolve().parents[2]
FIXTURE = REPO / "tests_src/fixtures/edgar/MU_facts_valuation_subset.parquet"
AS_OF = date(2025, 6, 26)


@pytest.fixture(scope="module")
def quarters():
    ledger = pd.read_parquet(FIXTURE)
    rows = assemble_rows(ledger, AS_OF, source="edgar")
    return rows[rows["period_type"] == "quarterly"].reset_index(drop=True)


def test_ac_f10_7_real_trailing_year_is_four_contiguous_edgar_quarters(quarters):
    """AC-F10.7 (recorded half) — ⚠ the real quarters abut with a 0-day gap."""
    from src.feature_engineer.valuation.basis import trailing_quarters

    q = trailing_quarters(quarters, as_of=AS_OF, ticker="MU")
    ends = [str(e)[:10] for e in q["q_end"]]
    assert ends == ["2024-08-29", "2024-11-28", "2025-02-27", "2025-05-29"]
    gaps = [(b - a).days for a, b in zip(q["q_end"], q["q_start"].iloc[1:], strict=False)]
    # ⚠⚠ Measured: [1, 0, 0] — BOTH conventions inside ONE filer's trailing year.
    #   A "day after" rule (1–7) and an "on the end date" rule (0) would each refuse
    #   this real series; only 0–7 accepts it (DX-103).
    assert gaps == [1, 0, 0]
    assert set(q["source"]) == {"edgar"}


def test_dx_103_real_balance_matches_the_10q(quarters):
    """★ Cash, debt and shares as the 10-Q prints them — via the fallback tags."""
    from src.feature_engineer.valuation.basis import balance, known_omissions

    net_debt, comps, shares = balance(quarters, as_of=AS_OF, ticker="MU")
    by = {c["item"]: (c["value"].amount_minor // 100_000_000, c["tag"]) for c in comps}
    assert by["cash"] == (10_163, "CashAndCashEquivalentsAtCarryingValue")      # line 559
    assert by["long_term_debt"] == (15_003, "LongTermDebtAndCapitalLeaseObligations")  # line 347
    assert by["current_debt"] == (538, "DebtCurrent")                             # line 344
    assert shares == 1_125_000_000                                                 # line 1090
    assert net_debt.amount_minor // 100_000_000 == 15_003 + 538 - 10_163 - 648 - 1_402
    assert known_omissions(comps) == ("operating_leases",)


def test_ac_f10_20_real_net_debt_matches_the_10q(quarters):
    """AC-F10.20 on the real filer — securities as the 10-Q's line 559 prints them
    (short-term $648M, long-term marketable $1,402M; with cash, $12,213M), and NO
    finance lease added: both of MU's debt tags already hold them (`D8`, measured)."""
    from src.feature_engineer.valuation.basis import balance

    net_debt, comps, _ = balance(quarters, as_of=AS_OF, ticker="MU")
    by = {c["item"]: (c["value"].amount_minor // 100_000_000, c["tag"]) for c in comps}
    assert by["marketable_securities_current"] == (
        648, "AvailableForSaleSecuritiesDebtSecuritiesCurrent")
    assert by["marketable_securities_noncurrent"] == (
        1_402, "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent")
    assert by["cash"][0] + 648 + 1_402 == 12_213                                   # line 559
    assert not any(item.startswith("finance_lease") for item in by)
    assert net_debt.amount_minor // 100_000_000 == 3_328


def test_ac_f10_17_real_basis_resolves_every_D6_item(quarters):
    """Every `D6` term resolves on the real filer; the rate is a plausible one."""
    from src.feature_engineer.valuation.basis import reported_basis

    basis = reported_basis(quarters, as_of=AS_OF, ticker="MU")
    items = {i["item"] for i in basis.inputs}
    assert items == {"operating_cash_flow", "interest_expense", "income_tax",
                     "pretax_income", "capex", "sbc"}
    assert 0 < basis.tax_rate < 1
    assert basis.base_fcff.currency == "USD"
