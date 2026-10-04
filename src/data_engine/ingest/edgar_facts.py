"""EDGAR companyfacts → `FactLedger`. ★ The step nothing had ever run.

⚠ **`DataEngine` reads ledgers; nothing wrote one.** `get_fundamentals` was
correct and answered from an empty store, so D-01's assembler had no evidence to
assemble and D-07's *preferred* TTM source (CLAUDE.md: **EDGAR wins**) was
unreachable in practice — see **DE-50**, the gzip defect that made every fetch
fail before this could even be noticed.

★ `append` is idempotent by key (`FactLedger.append`), so re-ingesting a ticker
is a no-op rather than a duplicate — which is what makes this safe to call on
every run instead of guarding it with state.
"""

from __future__ import annotations

#: The line items a thesis actually reasons over. ⚠ **Restricted deliberately:**
#: companyfacts for a large filer runs to hundreds of concepts and MU's
#: as-reported quarterly alone spans 536 tags — ingesting all of them buries the
#: five figures a reader checks in a bundle nobody can read.
#:
#: ★ **Measured 2026-08-27:** a `companyfacts` payload is **4.5 MB and 643 tags
#: for NVDA, fetched in 0.3 s**, and the tag filter is applied *client-side* — so
#: widening this set costs **no extra network at all**, only ledger rows
#: (NVDA 2 011 → 2 687). The restriction is about legibility, not cost.
THESIS_TAGS = frozenset({
    "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
    "CostOfRevenue", "GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss",
    "Assets", "Liabilities", "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue",
    "ResearchAndDevelopmentExpense",
    "NetCashProvidedByUsedInOperatingActivities",
})

#: ★ D-02's fundamental features need more than a thesis does. ⚠ **Coverage is
#: NOT uniform across filers, and that is a fact about accounting rather than a
#: data defect** — measured 2026-08-27 over these 20 tags:
#:
#: ```text
#:   NVDA  20/20      WMT  15/20      XOM  16/20
#:   JPM    9/20      PLD  10/20
#: ```
#:
#: ⚠⚠ A **bank has no gross profit and no current/non-current split**; a REIT
#: reports neither. So `f_gross_margin` and `f_current_ratio` are null for JPM
#: *correctly*. ★ The consequence belongs to the consumer and is registered as
#: **FE-37**: **null-ness itself correlates with sector**, and a model fed these
#: columns can learn *"the ones with holes are financials"* — which is a sector
#: dummy arriving through the back door.
FEATURE_TAGS = THESIS_TAGS | frozenset({
    "CostOfGoodsAndServicesSold",
    "AssetsCurrent", "LiabilitiesCurrent",
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",      # ✏ F11 D4 — the capex fallback (old SanDisk)
    "SalesRevenueNet",                        # ✏ DX-143 ⓐ — pre-ASC 606 revenue (MU ≤ FY2017)
    "InterestExpense",
    "LongTermDebtNoncurrent", "LongTermDebtCurrent",
    "WeightedAverageNumberOfDilutedSharesOutstanding",
    # ★ `F10` `D6` (2026-09-13) — the valuation's cash-flow formula needs tax,
    #   pretax income and stock-based compensation. Client-side filter: no extra
    #   network, only ledger rows (see the measurement above).
    "IncomeTaxExpenseBenefit",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    "ShareBasedCompensation",
    # ⚠ Measured on MU 2026-09-13: the concepts it files TODAY — `InterestExpense`
    #   stops May 2024 and `LongTermDebt*` stop in 2013 (`F10` fallbacks, `DX-103`).
    "InterestExpenseNonoperating", "DebtCurrent", "LongTermDebtAndCapitalLeaseObligations",
    # ★ `F10` `D8` (2026-09-14) — net debt counts marketable securities and finance
    #   leases (`valuation/basis.py::NET_DEBT_TAGS`).
    "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
    "AvailableForSaleSecuritiesCurrent", "ShortTermInvestments",
    "MarketableSecuritiesNoncurrent", "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent",
    "AvailableForSaleSecuritiesNoncurrent",
    "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent",
})

#: ⚠⚠ **Deliberately NOT ingested, and this is the reason.** `extract_facts`
#: takes *"every dated, filed, **monetary** Fact"* — a per-share ratio is not
#: monetary, and it came through as **`value_minor=0, currency=""`**. ★ A zero
#: that means *"this is not a monetary quantity"* is **indistinguishable from a
#: zero that means "the company earned nothing"**, and the model reading the
#: bundle cannot tell them apart. Per-share figures belong to D-02, which
#: computes them from a monetary numerator and a share count (RA-132, MP-6).
NOT_MONETARY = frozenset({
    "EarningsPerShareDiluted", "EarningsPerShareBasic",
    "CommonStockSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic",
})


def ingest_facts(client, ledger, *, ticker: str, cik: str, tags=FEATURE_TAGS) -> int:
    """Fetch one company's facts and append them. Returns NEW rows written.

    ⚠ Raises on a fetch failure rather than returning zero: *"no facts"* and
    *"the fetch failed"* are different states, and a caller that cannot tell
    them apart writes a thesis on an empty bundle (P5, DE-46).
    """
    from src.data_engine.src.edgar.companyfacts import extract_facts

    payload = client.companyfacts(cik)
    result = extract_facts(payload, ticker=ticker,
                           tags=set(tags) - NOT_MONETARY)
    return ledger.append(_collapse_identical(result.facts))


def _collapse_identical(facts):
    """Drop facts that repeat a key **with the same value**.

    ⚠ *Found 2026-08-26 ingesting the universe: 5 of 130 names — CSCO, ISRG,
    SBUX, WMT, MDLZ — failed CT-7.3's duplicate-key guard.* EDGAR's companyfacts
    genuinely reports one fact twice (the same value under two unit or frame
    labels), and CT-7.3 is right to refuse a duplicate key: *a duplicate
    silently multiplies rows on the next merge and the result still looks like a
    panel* (PD-11).

    ★ **Only byte-identical repeats collapse.** Two rows on one key with
    DIFFERENT values are a real conflict about a reported figure, and this lets
    CT-7.3 raise on them — *deduplicating by "keep the first" would pick a
    number by arrival order*, which is the silent-choice defect P5 exists for.
    """
    seen, kept = {}, []
    for fact in facts:
        key = (fact.ticker, fact.accession_id, fact.tag, fact.period_start,
               fact.period_end, fact.period_type)
        prior = seen.get(key)
        if prior is None:
            seen[key] = fact
            kept.append(fact)
        elif (prior.value_minor, prior.value_currency) != (
                fact.value_minor, fact.value_currency):
            kept.append(fact)          # ⚠ a real conflict — CT-7.3 must see it
    return kept


def load_cik_map(path: str = "config/sp500_tickers.yaml") -> dict:
    """`{TICKER: cik}` — ★ the routing D-07 needs and the universe already holds.

    ⚠ CIKs are **zero-padded strings**, and YAML reads an unquoted `0001045810`
    as the integer `1045810`. The leading zeros are not decoration: EDGAR's URL
    builder strips them itself, but a map that has already lost them cannot tell
    a missing entry from a mangled one.
    """
    import yaml

    with open(path, encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    raw = loaded.get("cik_map") or {}
    return {str(k).upper(): str(v).zfill(10) for k, v in raw.items()}
