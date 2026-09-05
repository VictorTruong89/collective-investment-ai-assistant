"""What the Starter key cannot get — §5A.2 and §5A.3, as data (DE-16).

★ **The list is data kept beside the client, and re-probed rather than
remembered.** Every row was measured live on 2026-08-15 against the real key,
156 endpoints on the `/stable/` API. FMP's marketing pages list endpoints the
Starter key returns `402` for, and the docs lag the API in both directions.

⚠ **A `404` and a `402` are completely different facts and must never be handled
alike.** A `402` says *"this exists and you cannot have it"* — the fix is money,
a parameter change, or a retry. A `404` says *"there is no such product"* — no
plan buys it, retrying is pointless, and the only fix is a different source.
"""

from __future__ import annotations

#: Cause 1 — the endpoint itself is gated. Permanent (§5A.2).
GATED_ENDPOINTS = {
    "institutional-ownership/symbol-ownership": "13F ownership — the biggest single gap",
    "institutional-ownership/latest": "13F ownership",
    "institutional-ownership/holder-performance-summary": "13F ownership",
    "institutional-ownership/holder-industry-breakdown": "13F ownership",
    "institutional-ownership/positions-summary": "13F ownership",
    "income-statement-ttm": "EDGAR is the TTM source anyway (§5.3)",
    "balance-sheet-statement-ttm": "EDGAR is the TTM source anyway (§5.3)",
    "cash-flow-statement-ttm": "EDGAR is the TTM source anyway (§5.3)",
    "latest-financial-statements": "gated",
    "news/press-releases": "8-K via sec-filings-search covers the material subset",
    "news/press-releases-latest": "as news/press-releases",
    "esg-disclosures": "no ESG mandate (vision.md §3)",
    "esg-ratings": "no ESG mandate",
    "esg-benchmark": "no ESG mandate",
    "etf/holdings": "etf/sector-weightings is a partial substitute",
    "batch-quote-short": "costs N calls instead of 1",
    "mergers-acquisitions-search": "-latest is available",
    "executive-compensation-benchmark": "not needed",
    "profile-bulk": "bulk download",
    "ratios-ttm-bulk": "bulk download",
    "scores-bulk": "bulk download",
}

#: §5A.3 — endpoints that do not exist. Recorded because each is a data type
#: someone will eventually assume exists, fail to find, and then quietly build
#: around with something worse. **The list is the point.**
ABSENT_ENDPOINTS = {
    "news/stock-sentiment": "no FMP sentiment product — scoring text is D-01's job (AP-2)",
    "social-sentiments": "no FMP sentiment product",
    "historical-social-sentiment": "no FMP sentiment product",
    "short-interest": "would need FINRA bi-monthly files — a real gap",
    "fail-to-deliver": "SEC publishes it directly",
    "earnings-call-transcripts": "★ the real loss for D-01 — QD-9",
    "commitment-of-traders": "irrelevant — no futures (M-1)",
    "all-shares-float": "per-ticker shares-float works",
}

#: ⚠ AC-7.31 — never ingested, at any tier, even though all nine return 200.
#: D-02 computes indicators from D-07 prices; importing a vendor's RSI creates a
#: second definition of a feature we already own, silently different from ours.
#: F0 §12 **D-16** is exactly this problem, self-inflicted once already.
FORBIDDEN_ENDPOINT_PREFIXES = ("technical-indicators/",)


def parameter_gate(endpoint: str, params: dict) -> str | None:
    """Cause 2 — the endpoint works and the ARGUMENTS decide. Returns why, or None.

    ★ This is the one that bites in production, because the same call succeeds
    in a probe and fails later when a `limit` grows or a backfill widens a date
    range. Rejecting at the client boundary (DE-16) is cheaper than sending it:
    the answer is already known and the request costs a slot against the cap.
    """
    period = params.get("period")
    limit = params.get("limit")

    if endpoint == "analyst-estimates":
        if period == "quarter":
            return "analyst-estimates period=quarter is 402 on Starter"
        if limit is not None and int(limit) >= 20:
            return f"analyst-estimates limit={limit} is 402 on Starter (limit<=10)"

    if endpoint in ("key-metrics", "ratios") and period == "quarter":
        return (f"{endpoint} period=quarter is 402 on Starter — quarterly ratios and "
                f"metrics must be COMPUTED from the quarterly statements (AC-7.34)")

    if endpoint.startswith("revenue-") and endpoint.endswith("-segmentation") \
            and period == "quarter":
        return f"{endpoint} period=quarter is 402 on Starter (annual only)"

    if endpoint == "economic-calendar":
        span = params.get("_span_days")
        if span is not None and int(span) >= 365:
            return f"economic-calendar span {span}d is 402 on Starter (<=180d)"

    if endpoint == "news/stock" and ("from" in params or "to" in params):
        return ("news/stock is 402 with ANY from/to — page through instead "
                "(and it is only ~92 days deep, §5C.4)")

    if endpoint == "governance-executive-compensation":
        symbol = str(params.get("symbol", "")).upper()
        if symbol in ("MU", "ARM"):
            return f"governance-executive-compensation is 402 for {symbol} — per company"

    if endpoint.startswith("historical-price-eod/"):
        if str(params.get("symbol", "")).upper() == "^SOX":
            return "historical-price-eod is 402 for ^SOX (^GSPC/^IXIC/^DJI/^RUT work)"

    return None
