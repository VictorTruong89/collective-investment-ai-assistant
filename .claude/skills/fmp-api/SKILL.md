---
name: fmp-api
description: >
  What Financial Modeling Prep can and cannot serve, measured against the real
  Starter key rather than read from FMP's docs. Use BEFORE designing or coding
  anything that fetches market data, fundamentals, analyst data, corporate
  events, insider/institutional data, news, macro series or FX — and before
  assuming a data type exists. Carries the five traps that have already caused
  measured defects, the plan gates (402 vs 404), and the point-in-time hazard
  classes. Triggers: "FMP", "financialmodelingprep", "market data", "price
  history", "fundamentals", "analyst estimates", "earnings calendar", "insider
  trading", "does FMP have", "which endpoint", "data source", "402", "quarterly
  data", "TTM".
---

# FMP — what the key actually serves

**Full endpoint catalog:** [`references/endpoints.md`](references/endpoints.md).
**Live gate data (code):** `src/data_engine/src/fmp/gates.py` — `GATED_ENDPOINTS`,
`ABSENT_ENDPOINTS`, `FORBIDDEN_ENDPOINT_PREFIXES`, `parameter_gate()`.
**Source of record:** upstream `L1-data-engine.md` §5A.

> ⚠⚠ **This is a MEASUREMENT, not documentation.** Every row was probed live on **2026-08-15**
> against the real key — **156 `/stable/` endpoints, Starter tier**. FMP's marketing pages list
> endpoints the key returns `402` for, and **the docs lag the API in both directions**.
> ★ **Re-probe rather than remember.** If a decision turns on availability, verify it.

---

# ⚠ The five traps

Each has already caused a measured defect. Read these before writing a fetch.

## ★★ 1. FMP guesses the quarter. EDGAR knows it. (the Micron case)

```text
   EDGAR facts carry period START **and** END
        → discrete quarter vs cumulative year-to-date is decidable BY ARITHMETIC

   FMP exposes only the period END
        → it must GUESS — and it guessed wrong on MU by 71 %
```

**Measured, row by row** (ARM 6-K/20-F cumulative vs FMP discrete):

| Period | Cumulative | Discrete | Ratio |
|---|---|---|---|
| Q1 | 1,053 M | 1,053 M | 1.00× ← *only Q1 matches, because YTD **is** the quarter* |
| Q2 | 2,188 M | 1,135 M | **1.93×** |
| Q3 | 3,430 M | 1,242 M | **2.76×** |
| FY | 4,920 M | 1,490 M | **3.30×** |

★ **THE RULE: for TTM and any per-quarter line item, EDGAR wins.** Route to FMP only where EDGAR
does not have it (upstream §5.3).

⚠ **Same defect class as `_cumulative_fys`**, which understated MU's TTM revenue by **41.5 %** and
moved its fair value by **$379/share** — and survived because a docstring asserting the wrong rule
had a passing test built on real production numbers.

**Detection, not trust:** classify from the *span*, never from a label —
`src/data_engine/src/edgar/xbrl.py::classify_span`. A discrete quarter is 80–100 days (filers run
13–14 weeks on 52/53-week calendars); a fiscal year is 350–380. **A half-year cannot pass either
window.**

## ★★ 2. The adjusted-price field names are INVERTED

```text
historical-price-eod/non-split-adjusted → {"adjOpen": 1197.7, "adjClose": 1208.9}  ← RAW
historical-price-eod/full               → {"open":  119.77,  "close":  120.89}     ← ADJUSTED
```

⚠ **The endpoint whose fields are named `adj*` is the one that is NOT adjusted.** Reading by field
name gets it exactly backwards — and **both shapes parse without error**, so the wrong series flows
through the whole pipeline with correct dtypes.

| Series | NVDA pre-split close 2024-06-03 | What it is |
|---|---|---|
| `non-split-adjusted` | **1150.00** | ★ **raw — what a person actually saw** |
| `full` / `light` | 115.00 | split-adjusted (÷10) |
| `dividend-adjusted` | 114.80 | split **and** dividend adjusted |

**Volume is retro-adjusted in the opposite direction** — `full` reported 438,392,000 shares against
a true 43,839,200 (×10).

⚠ **How this was nearly missed:** a first pass on MSFT · MU · ARM found the series identical to 4 dp
and concluded split adjustment was not a hazard — **none of the three split in the window.** One name
that actually split reversed the conclusion completely. **Never generalise a price finding from names
that did not experience the event.**

## ★ 3. `402` and `404` are completely different facts

| Code | Means | Fix |
|---|---|---|
| **402** | *"this exists and you cannot have it"* | money, a parameter change, or a retry |
| **404** | *"there is no such product"* | ⚠ **no plan buys it** — retrying is pointless; use another source |

**Never handle them alike.**

## ★ 4. `402` itself has three meanings, and the status code does not say which

1. **Endpoint gate** — permanent. See `GATED_ENDPOINTS`.
2. **Parameter-value gate** — the endpoint works and the *arguments* decide.
   ⚠ **This is the one that bites in production**: the same call passes a probe and fails later when
   a `limit` grows or a backfill widens a date range.
3. **Transient under burst** — succeeds on retry.

Known parameter gates (`parameter_gate()`):

| Endpoint | Gated when |
|---|---|
| `analyst-estimates` | `period=quarter`, or `limit >= 20` |
| `key-metrics`, `ratios` | `period=quarter` → ★ **compute quarterly ratios from the statements instead** |
| `revenue-*-segmentation` | `period=quarter` (annual only) |
| `economic-calendar` | span ≥ 365 d (≤ 180 d works) |
| `news/stock` | **any** `from`/`to` — page instead; only ~92 days deep |
| `governance-executive-compensation` | per-company (MU, ARM are 402) |
| `historical-price-eod` | `^SOX` (but `^GSPC`/`^IXIC`/`^DJI`/`^RUT` work) |

## ★ 5. Point-in-time class decides how a row may be stored

| Class | Meaning | Handling |
|---|---|---|
| **A — natively PIT** | carries its own publication date, never revised | store as-is; the as-of filter works unchanged |
| **B — snapshot, no history** | ⚠ current value with **no as-of axis at all**; ask tomorrow, get a different number | ★ **we must create the axis** — snapshot on a schedule into an observation ledger stamped with *our* `observed_at`. **History not captured is gone; there is no retrofit** |
| **C — restated series** | has a period date but reflects *today's* restatement | FMP carries no restatement history, so the PIT guarantee is weaker — **record that, do not paper over it** |

⚠ **`analyst-estimates.date` is the forecast *target* period, not the publication date.** There is no
publication axis. Treated naively it is a textbook look-ahead.

---

# What the Starter key cannot get

## Gated — `402`, exists but paywalled

**Institutional / 13F ownership (5 endpoints)** — ★ *the biggest single gap*: holder concentration,
position changes, holder performance. Also: `*-statement-ttm` (EDGAR is the TTM source anyway),
`latest-financial-statements`, `news/press-releases*`, all ESG, `etf/holdings`, `batch-quote-short`,
`mergers-acquisitions-search` (use `-latest`), `executive-compensation-benchmark`, and the `*-bulk`
downloads.

## Absent — `404`, no product exists at any tier

⚠ **The list is the point** — each is a data type someone will assume exists, fail to find, and then
quietly build around with something worse.

| Missing | Note |
|---|---|
| **Earnings-call transcripts** | ★ **the real loss** for the fundamental seat |
| **Short interest** | a real gap — would need FINRA bi-monthly files |
| Sentiment (news, social, historical) | no FMP product — scoring text is the analyst seat's job |
| Fail-to-deliver | SEC publishes it directly |
| Commitment of traders | irrelevant — no futures |
| `all-shares-float` | per-ticker `shares-float` works |

## ⛔ Forbidden by our own rule, though they return 200

**`technical-indicators/*` — never ingested, at any tier.** Indicators are computed from our own
price data; importing a vendor's RSI creates a **second definition of a feature we already own**,
silently different from ours. This has been self-inflicted once already.

---

# Using it

- **Check the catalog before assuming.** [`references/endpoints.md`](references/endpoints.md) lists
  every available endpoint with grain, PIT class and consumer.
- **Reject at the client boundary.** A known-402 call still costs a slot against the cap — the answer
  is already known, so do not send it.
- **EDGAR wins for statements.** FMP is the fallback where EDGAR has nothing (§5.3).
- **FMP's own DCF is a cross-check, never a published fair value.**
- ⚠ **If availability has changed, fix `gates.py` and re-date the measurement** — do not work around
  it locally.
