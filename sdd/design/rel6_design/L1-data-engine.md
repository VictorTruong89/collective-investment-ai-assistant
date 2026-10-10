# L1: Domain Specification — Data Engine (D-07)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) · **Domain:** D-07 · **Seat:** SEAT-5
> **Path:** `src/data_engine/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L2-shared-money.md`](L2-shared-money.md) (D-00)
> **Prior art:** `sdd/specs/F9_universe_and_fundamental_sources/spec.md`, *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*
> `sdd/specs/F4_data_plane/spec.md`, `constitution.md` INV-1/INV-2/INV-5, `DCFCalculator.TTM_SOURCE_TOLERANCE` *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.28.0 | 2026-08-28 | Victor | ★★★ **EVERY event class is now accounted for — 5 → 15 CHECKED of 18.** Built this pass: `filing_mid_window` (7), `material_event_8k` (11), `beneficial_ownership` (13), `analyst_action` (14), `news` (15), `macro_release` (16), plus **DE-72 cadence**. ★★ Classes **4, 7 and 11 come from ONE EDGAR submissions pass** — fetching it three times would triple a throttled cost for nothing; a filing is emitted under exactly one class and **8-K item 4.02 outranks class 11**. ⚠⚠ *Measured:* **`grades` ignores `limit` entirely** (1 791 rows for AAPL whatever is asked — ~900 000 across the universe from one NOTE class), so the window is enforced client-side. ⚠⚠ `economic-calendar` truncates **non-monotonically** — a *wider* request returned **fewer** rows and less history. ★ **Class 1 needed no build**: it is derived at check time. AC-7.89/7.90. |
| 0.27.0 | 2026-08-28 | Victor | ★★★ **DE-70/DE-71 + classes 9 & 10 INGESTED — 7 of 18 → 9** (AB-14). ⚠⚠ **`earnings-calendar` truncates SILENTLY at 4 000 rows keeping the LATEST** — asking for 2026 returns November onward — and reaches **exactly 365 days** (`2025-08-29` answers, `2025-08-27` is 402). ★ So the sweep chunks by week, treats a response *at* the cap as truncated, and an uncovered chunk records **no refresh** while naming its cause (`capped` vs `refused` — different fixes). ★★ **The two classes have different knowability axes**: a reported result is knowable on its announcement; a **scheduled date is knowable only as of when we looked, and it MOVES** — DE-65's look-ahead in the calendar layer. ⚠ `lastUpdated` is never the axis (DE-23) — *17 of AAPL's 20 quarters share one stamp*. ★ *Live:* **2 540 findings — 2 033 reported, 507 scheduled, 70 chunks, none truncated.** AC-7.87/7.88. |
| 0.26.0 | 2026-08-28 | Victor | ★★ **Class 5 `restatement_silent` BUILT — and it reports `UNCHECKED`, which is the correct answer.** DE-24's `diff_against_stored` had existed since B-era with **no production caller**; the substrate now exists (the append-only, content-hashed observation ledger) and a caller diffs it. ⚠⚠ *Measured:* all four field sets hold **exactly one snapshot per ticker — 0 of 510 comparable**, so nothing is recorded as refreshed and the class stays UNCHECKED **with its reason**. ★ *That is not a shortfall*: FMP serves only today's answer, so one snapshot cannot be diffed, and calling it *'no restatements'* is the conflation DE-35 forbids. ⚠ A second, **structural** limit: no field set carries a period key, so a changed TTM value is **ambiguous by construction** — a new quarter entering the window is indistinguishable from a revision, and the finding says so. |
| 0.25.0 | 2026-08-28 | Victor | ★★★ **DE-69 + class 4 `restatement_amended` INGESTED — 6 of 18 classes → 7** (AB-14). ⚠⚠ **The declared source does not carry the data**: FMP's index returns **zero `10-K/A` across all filers** in three windows while `10-Q/A` fills a page — so the class was rebuilt on **EDGAR**, the same precedence that already governs TTM. ★ *Live sweep, 510 names, 3 years:* **69 findings — 48 `10-K/A`, 13 `10-Q/A`, and 5 non-reliance 8-Ks** (`CPAY`, `ADM`, `AES`, `AXON`, `MPWR`); **all 510 names reached, zero failures**. ⚠⚠ Every one of the 48 would have been missed **silently on a BLOCK class**. ★ `formType ~ /A` was also the wrong *test* — it matches `SC 13G/A`/`4/A` (63 for AAPL), so an explicit whitelist replaces it. AC-7.86. |
| 0.24.0 | 2026-08-28 | Victor | ★★ **Class 12 `ma_announcement` INGESTED — 5 of 18 classes → 6** (AB-14). ★ **The event that precedes the silence**: a combination is filed months before a ticker stops printing. ★★ *Measured:* unlike `delisted-companies`, this feed **PAGES** — page 40 still returns rows dated **1999**, against DE-60's three-week wall. ⚠ It names M&A only (not bankruptcies or compliance removals), so it is a **partial** survivorship source and **AB-3 stands**. ⚠⚠ **And the first cut over-claimed**: I labelled the pair acquirer/target, ran it, and **4 of 6 universe matches were not acquisitions of that name** — `CMI` split off Atmus, `AIG` divested Corebridge, `BDX` is a Reverse Morris Trust *parent*, `COF` matched **its own preferred class**; only `NSC`→`UNP` was genuine. ★ The pair is **S-4 filer/subject**, so the finding now records `side` and carries `investigate`, a **candidate never a conclusion** (DE-35). |
| 0.23.0 | 2026-08-28 | Victor | ★★ **The DE-68 contamination check is wired into `ingest symbols` and ran.** Live output: **`⚠⚠ AVB prints VMRK's series from 2026-08-18`**. ★★ `contaminated_by()` finds the retired side **without any search** — `AVB` is invisible to the CIK diff by construction and visible to arithmetic. ⚠ The step calls the vendor (the diff does not), so it is reported separately, scoped to `delisted × successors`, and degrades to a note. ★ Compares `close_minor` (CT-7.1 integers) — exact equality, not float rounding. |
| 0.22.0 | 2026-08-28 | Victor | ★★ **AC-7.85 BUILT** — `symbology/combination.py`. A combination emits **two** findings (survivor `ticker_change` + retired-side `delisting`), and ⚠⚠ **the cause is REFUSED without source URLs**: it is established by search, never derived, so an unsourced guess must not be storable next to a corroborated finding. ⚠⚠ **The first cut was wrong and the LIVE check caught it**: it flagged `BK`→`BNY` as contaminated, because a rebrand genuinely *is* one series through two symbols — ★ contamination is a **diverge-then-converge** shape, not agreement. ★ Re-verified live: `AVB`/`VMRK` → **2026-08-18**; `EQR`/`VMRK`, `BK`/`BNY`, `SATS`/`ECHO` → **None**. ⚠ A window starting at or after the changeover now **raises** instead of returning a clean `None` (P5). |
| 0.21.0 | 2026-08-28 | Victor | ★★★ **DE-68 — the diff says WHAT moved, never WHY, and `EQR` proves the gap is not academic.** Victor established by **search** that `EQR`→`VMRK` is a **merger of equals with AvalonBay**, not a rebrand. ⚠ The CIK diff shows a merger of equals and a rebrand as **the same shape**, so it reported *one* event where **two** names left the universe — the retired side is invisible to it by construction. ⚠⚠ *Measured:* the vendor **back-fills the retired symbol with the successor's prices** — `AVB` 2026-08-17 = 65.90 (its own), 2026-08-18 = 64.03 = `EQR` = `VMRK` — so a dead ticker keeps printing and carries **a fabricated return** on the changeover date. ★ Verified the survivor is clean: **VMRK's pre-merger closes equal EQR's 59/59**. AC-7.85. |
| 0.20.0 | 2026-08-28 | Victor | ★★★ **DE-67 — identity beats a vendor delisting.** Victor ruled **`EQR` is NOT a delisting** (2026-08-28): FMP's feed called it one on 2026-08-18, SEC showed CIK `0000906107` listing **`VMRK`**, and VMRK priced **41 bars through 2026-08-27**. ★ RC-54 said neither source is assumed right; the decision settles it in favour of the **registrant index**, on the same reasoning that makes EDGAR beat FMP for TTM — *the source with the explicit fact beats the source inferring one*. ⚠⚠ The delisting row is **superseded, never deleted**, and the `ticker_change` **BLOCK still stands** — the name is un-barred, not declared fine. ⚠ **`AVB` is NOT covered** — it has no `ticker_change`, keeps its own ticker at SEC, and stays barred. AC-7.84. |
| 0.19.0 | 2026-08-28 | Victor | ★★★ **§6B IDENTITY + CT-7.8 + DE-61…66 — a ticker is a label, not an instrument.** ⚠ *Measured:* `BK`→`BNY` and `SATS`→`ECHO` are **rebrands that still trade**, and from the price feed a rename and a delisting are **indistinguishable**. ★ **CIK is the anchor** (free, already fetched); renames are detected by **diffing dated SEC `company_tickers.json` snapshots on CIK** — verified to recover both from this repo's own stored universe with **no vendor call**. ⚠⚠ **A vanished CIK is NOT a delisting** (`AVB` proves the lag). ★ **Fetch under the CURRENT symbol** — it carries the full history (164 bars vs the retired symbol's 122) — and ⚠⚠ **NEVER splice**: OHLC agree exactly but **volume does not**, which would put a step into `volume.split_adjusted_zscore.v1`. New event class 18. AC-7.78…7.83, QD-17. |
| 0.19.0 | 2026-08-27 | Victor | ★★★ **DE-59/DE-60 — the `delisting` class, and what it does not buy.** Ingesting it immediately exposed a blanket handling that marked the real **AVB and EQR delistings `handled=True`** — *a price adjustment does not fix a name that stopped trading*. ⚠ **DE-60**: the feed reaches ~3 weeks (pages 1+ are 402), so it serves the gate and **cannot correct INV-017 survivorship** — AB-3 stands. AC-7.77. |
| 0.18.0 | 2026-08-27 | Victor | ★★★ **DE-58 — a 12-name sweep was reporting a 510-name universe as CHECKED.** `record_refresh` recorded *when* but not *which names*. ★ Coverage now travels with the refresh and the unfetched names are named in the status. Also `python -m src.data_engine.ingest` — **the sweeps §6A assumes someone runs**, which nothing could invoke. AC-7.76. |
| 0.17.0 | 2026-08-27 | Victor | ★★ **DE-57 — fixing DE-56 would have broken the daily run.** With the store empty the gate's `handled` map was empty too and nothing noticed; **populating the store makes every split unhandled and HALTs the run**. The handling now comes from the store, still filtered by knowability (DE-34). ★ `calendar/gate.py` is the one implementation — the training run's copy was a stub (**AB-9, closed**). AC-7.75. |
| 0.16.0 | 2026-08-27 | Victor | ★★★ **DE-56 — the calendar gate was reading a store nothing ever wrote.** `_calendar` recorded three classes as refreshed unconditionally while `events=()`, so they reported **`CHECKED` having fetched nothing** — DE-35's own defect, inside DE-35's implementation. ★ `src/data_engine/ingest/events.py` is the maintainer §6A assumed; with the store populated the gate **HALTs on NVDA's 2024-06-10 10:1 split**, where before it found zero. AC-7.74 added. |
| 0.15.0 | 2026-08-27 | Victor | ★★★ **DE-55 — the YTD→discrete conversion EDGAR was chosen for had never run.** `discrete_from_cumulative` existed since B2 and **nothing called it**; cumulative spans were rejected. ⚠ NVDA carried **70 YTD spans against 38 discrete quarters** — two of every three quarters had no cash flow, and every rolling feature read as sparse data. ★ Derived quarters sum to the reported year to the dollar. AC-7.73 added. |
| 0.14.0 | 2026-08-27 | Victor | ★★ **DE-54 — sub-penny vendor prices dropped whole tickers.** `AAPL` (`310.245`) and `SNDK` (`1454.445`) raised `PrecisionLossError` and surfaced as **`no_source`**, which reads as *the vendor has nothing*. ⚠ **Invisible at inference, fatal at training**: the daily run's 200-day window sat in front of the sub-penny prints. AC-7.72 added. |
| 0.13.0 | 2026-08-26 | Victor | ★★ **DE-53 — the PIT cutoff was in the wrong timezone.** `as_of` is an **ET trading date** everywhere here (the calendar, the open anchor, `is_trading_day`), but `ObservationLedger.get()` cut off at UTC midnight — **silently discarding the last four hours of every business day.** ⚠ A run captured a profile at 22:50 ET and then could not see its own capture. `MARKET_TZ` already existed in two other modules. AC-7.70 added. |
| 0.12.0 | 2026-08-26 | Victor | ★★ **DE-51/DE-52 — found ingesting all 130 names for the first time.** **DE-51**: EDGAR emits byte-identical duplicate facts and 5 of 130 tickers failed CT-7.3's guard; only identical repeats collapse, **a value conflict still raises**. **DE-52**: `EarningsPerShareDiluted` ingested as `value_minor=0` — ⚠ *a zero meaning "not monetary" reads exactly like a zero meaning "earned nothing"*. AC-7.68/7.69 added. |
| 0.11.0 | 2026-08-26 | Victor | ★★ **DE-50 — EDGAR had never successfully fetched anything.** `_get` asks for gzip, `urllib` does not decompress, and the transport decoded raw bytes as UTF-8: every `companyfacts` call died on the gzip magic byte. ⚠ **Every test injects a fake transport, so the only class that touches the network was the only class with no coverage** — and EDGAR is the *preferred* TTM source. Fixed to decode on the response's `Content-Encoding`; NVDA now yields 898 facts. AC-7.67 added. |
| 0.10.0 | 2026-08-26 | Victor | ★★ **The universe price assembler built** — one CT-7.1 panel over every name, with **DE-13 as its spine**: a ticker that does not resolve **fails the run**, is not dropped, and does not become a row of NaNs. ⚠ **DE-49**: a **402 is a subscription boundary, not a missing security** — an absent name is a universe error to correct, a plan-gated one is a **declaration** problem discovered too late at fetch time. ★ Failures are **collected and reported once**, so a 130-name universe with three problems takes one run to diagnose. **Verified live: 13 watchlist names → 1,794 rows in 4.1s**, and the full B6 graph then ran to a card on it. |
| 0.9.0 | 2026-08-25 | Victor | ⚠⚠ **Wiring D-08's daily run — CT-7.1 declared no settledness.** **OR-32** requires *"the settled day-T opening print, obtained as a real OHLC field from D-07"* and **nothing in this spec could say whether a bar was final.** ★ **DE-47**: the opening PRINT and the day-T BAR settle at different times — the auction is final at 09:30, the bar not until 16:00 — so a daily endpoint polled at **10:00 returns an in-progress row whose high/low/close are the running price.** That is `open == high == low == close`, the collapsed bar OR-32 names and `main_inference.py:250` produced. New `get_day_open`, AC-7.63/7.64. |
| 0.8.0 | 2026-08-23 | Victor | ⚠ **B3 readiness: CT-7.7 declared no id.** D-02's `CT-2.2` stamps every panel with **`calendar_check_id`** — *"the D-07 report that cleared this window"* (**FE-10**) — and **this contract emitted no identifier of any kind**. ★ **`report_id` added**, derived from `(run_id, as_of)` rather than allocated, so a panel's provenance is reproducible. Same seam-defect class as `adj_open_minor` (v0.6.0) and `adj_as_of` (v0.7.0): a consumer asserting against a field the producer never declared. |
| 0.7.0 | 2026-08-23 | Victor | ⚠ **B2 readiness pass — seven defects, five of them at a seam — plus two findings from building it.** ★ **§5A.1: the raw endpoint's FIELDS ARE NAMED `adjOpen`/`adjClose` and the adjusted one's are named `open`/`close`** — measured live 2026-08-23, caught by the §6A.4 probe on its first real run, and both shapes parse without error. ★ **CT-7.1 now states that `volume` is always raw**, because the contract's silence is the kind a reader fills in with the wrong guess. ★ **New DE-46 — DE-15/AC-7.32 and L4 EH-14 contradict**: one puts the 402 retry inside D-07's client, the other forbids any domain but D-08 from retrying. Resolved as a *classification probe*, with the attempt count carried to the manifest so EH-14's objection is answered rather than waived. ★ **The price read path was uncallable as written**: §8's `get_prices(ticker, start, end)` is *"adjusted by default"* and takes **neither `as_of` nor `adj_as_of`**, so every documented call violates **DE-28** and neither `DATA.PRICE.ADJ_AS_OF_REQUIRED` nor `DATA.PRICE.RAW_REQUIRED` is reachable — **new DE-45**, §8 corrected. ★ **`adj_factor` was defined circularly**: CT-7.1 called it `adj_close/close`, which presupposes a vendor `adj_close` that **DE-27 says we do not ingest** — **DE-42 restated** to derive it from the events at `adj_as_of`. ★ **CT-7.1 declared no `adj_as_of`** while DE-30, AC-7.46 and D-02 **FE-8** all assert against it — the same shape as the `adj_open` defect v0.6.0 fixed. ★ **CT-7.3 omitted `period_type`** though §6.3 step 2 groups on it. ★ **DE-42/43/44 and DE-12 had no acceptance criteria** — and DE-44 *is* L3 B2's done-when. AC-7.57…7.62 added. |
| 0.6.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: `adj_open` was assigned to D-07 by three specs and appeared ZERO times here.** `CT-7.1` gains **`adj_open_minor`** and a materialised **`adj_factor`**, with **DE-42/43/44** — the factor is a property of the date not the field, the cross-field assertion is a tautology against a reconstruction so the real check is the vendor or factor monotonicity, and **ex-dividend dates need their own assertion** because a close-derived factor can double-count the drop. The open-anchored label was blocked on a column no contract declared. |
| 0.5.0 | 2026-08-16 | Victor | **New §6A — the pre-run calendar check.** D-07 must enumerate corporate actions for the **whole universe over the full window before any training / backtest / inference run**, and **halt** on an unhandled one (DE-31…DE-36). 17 event classes with knowability dates and severities; **`UNCHECKED` is a first-class result** — never "no events" (DE-35). **§6A.4 requires a live FMP reality probe** (F3 Tier 1 / CT-3.2) that fetches over the network and digests through the real code path, asserting against the **§6A.5 known-answer set** K-1…K-10 (DE-37…DE-41). New **CT-7.7**, API `calendar_check`, 4 error codes, AC-7.47…7.56, QD-15/QD-16. |
| 0.4.0 | 2026-08-16 | Victor | **NVDA added to the dump to test the split case** (91 files / 71,214 rows, written additively per DE-17). **QD-2 answered — and the 2026-08-15 answer was wrong.** `historical-price-eod/full` retro-divides pre-split prices by the split factor and multiplies volume by it; only `non-split-adjusted` is raw. The earlier "split adjustment is not the hazard" reading was an inference from three names none of which split. New **§5C.7** with **DE-27…DE-30**: keep the raw series + split events as the system of record and derive the adjusted panel **at an as-of**, because the real defect is **constitution INV-2 determinism**, not classical look-ahead. §5A.1 price table and §5C.6 corrected; AC-7.43…7.46 added. |
| 0.3.0 | 2026-08-15 | Victor | **Findings from the retained dump folded in.** New **§5A.3a** (the `data/fmp_dump/` reference artifact + **DE-17 retain-it rule** + full inventory), **§5A.4a** (which data serves the **fundamental** seat vs the **quant** seat vs neither), **§5A.4b** (the planned **event calendar**, DE-18…DE-20), and **§5C — measured PIT & restatement defects** (DE-21…DE-26). §5A.3 expanded on what `404` means and why it differs from `402`. **Three §5A classifications corrected by evidence:** FMP statements *do* carry `filingDate`/`acceptedDate`; `lastUpdated` is a batch stamp, not a revision axis; `historical-market-capitalization` leaks ~28 days per quarter. AC-7.35…7.42 added. |
| 0.2.1 | 2026-08-15 | Victor | **§5A.2 rewritten after a full 3-year, 3-ticker dump** (`data/fmp_dump/`, 341 CSVs / 443,763 rows / 700+ calls). `402` turns out to have **three distinct meanings** — endpoint gate, **parameter-value gate**, and **transient-under-burst** — which the status code does not distinguish. New **DE-15**, corrected **AC-7.32**, new AC-7.33/7.34. Two §5A claims corrected by evidence: the split-vs-dividend adjustment, and `grades` history depth. |
| 0.2.0 | 2026-08-15 | Victor | **New §5A — FMP data catalog**, measured by probing 156 `/stable/` endpoints against the live Starter key on 2026-08-15: what is available, what is `402` paywalled, what does not exist (**no sentiment, no short interest, no transcripts**), and the **three point-in-time hazard classes** that decide how each may be ingested. §2 entities extended, §4 gains `observation/` (the Class-B snapshot ledger), **CT-7.6** added, QD-6…QD-10 raised. No change to §5 routing, §6 PIT resolution or existing ACs. |
| 0.1.1 | 2026-08-15 | Victor | Cascade from L0 **v0.9.0 / v0.10.0**: §1.2 consumer row now shows **D-09 Reporting** and **D-11 Recording** separately; constitution invariants qualified by source per **G-3** (`INV-1`/`INV-2` are the constitution's, not L0's — §13 previously attributed them to L0). No contract, rule or AC change. |
| 0.1.0 | 2026-08-14 | Victor | Initial draft. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

The Data Engine answers exactly one question, and it must answer it the same way every time:

> **"Give me the data that was *knowable* on date D, in canonical shape, with its provenance —
> regardless of which source supplied it."**

The phrase carrying the weight is **knowable on date D**. Any domain can fetch a number; only D-07
can guarantee the number was available at the time it is being used for. That guarantee is what
makes **constitution INV-1 (no look-ahead)** enforceable rather than aspirational, and it is why point-in-time
is a first-class module here (§6) rather than a flag on a query.

## 1.2 Position

```text
  D-01 Fundamental   D-03 Quant   D-04 Models   D-05 Risk   D-09 Reporting   D-11 Recording
          ▲               ▲             ▲            ▲             ▲                ▲
          └───────────────┴──────┬──────┴────────────┴─────────────┴────────────────┘
                                 │  (most consumption is indirect,
                                 │   via D-02 Feature Engineering)
                        ┌────────────────────┴───────────┐
                        │      D-02 Feature Eng.         │  SEAT-5
                        └────────────────┬───────────────┘
                                         ▲
                                    ┌────┴───────────────┐
                                    │  D-07 Data Engine  │  SEAT-5   ← this spec
                                    └─────────┬──────────┘
                                              ▲
                         ┌────────────────────┴────────────────────┐
                    ┌────┴─────┐                            ┌──────┴──────┐
                    │ SEC EDGAR│                            │     FMP     │
                    │ filings  │                            │ prices·news │
                    │ XBRL     │                            │ fundamentals│
                    └──────────┘                            └─────────────┘
```

**D-07 is the only domain permitted to reach an external data API.** Any other domain doing so is a
defect, not an optimisation (ST-3, L0 §4.3).

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-07 ACQUIRES, VALIDATES, STORES AND SERVES.                    ║
║  IT COMPUTES NOTHING A CONSUMER COULD ARGUE WITH.                ║
║                                                                  ║
║  Definitional derivation is in scope: gross_profit =             ║
║  revenue − cogs when the filer omits it; a Money built from      ║
║  a float; a fiscal period normalised to a calendar date.        ║
║                                                                  ║
║  Analytical derivation is NOT: ratios, margins, growth rates,    ║
║  indicators, scores. All of that is D-02.                        ║
║                                                                  ║
║  The test: if two reasonable analysts could disagree about the   ║
║  right formula, it does not belong here.                         ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Source |
|---|---|---|---|
| **PriceBar** | ticker × trading day | `(ticker, date)` | FMP |
| **Filing** | one SEC submission | `accession_id` | EDGAR |
| **Fact** | one XBRL value from one filing | `(accession_id, tag, period)` | EDGAR |
| **FundamentalRow** | ticker × fiscal period, canonical | `(ticker, period_end, period_type)` | EDGAR **or** FMP (§5) |
| **PitSnapshot** | what was knowable at a date | `(ticker, as_of)` | derived |
| **CompanyProfile** | ticker | `ticker` | FMP + EDGAR |
| **NewsItem** | article | `(source, external_id)` | FMP |
| **UniverseEntry** | ticker membership | `ticker` | config / FMP `stock-list` |
| **FxRate** | pair × observation | `(pair, as_of)` | FMP |
| **AnalystAction** | one rating or price-target change | `(ticker, date, firm, kind)` | FMP `grades`, `price-target-news` |
| **InsiderTransaction** | one Form 4 line | `(accession_id, reporting_cik, transaction_date, security)` | FMP `insider-trading/search` |
| **OwnershipFiling** | one SC 13D/G | `(cik, filing_date, reporting_person)` | FMP `acquisition-of-beneficial-ownership` |
| **CorporateEvent** | dividend · split · earnings · M&A · delisting | `(ticker, event_type, event_date)` | FMP |
| **CalendarEntry** | a *scheduled, not yet occurred* event | `(ticker, event_type, scheduled_date)` | FMP `earnings-calendar`, `dividends-calendar` |
| **SegmentRow** | revenue by product or geography | `(ticker, period_end, axis, segment)` | FMP |
| **MacroPoint** | one macro/rate observation | `(series, date)` | FMP `treasury-rates`, `economic-indicators` |
| **SectorPoint** | sector or industry performance / P&E | `(scope, name, date)` | FMP |
| **Observation** ★ | **a Class-B snapshot stamped with when *we* saw it** | `(ticker, field_set, observed_at)` | FMP — §5A.4 |

★ **`Observation` is the entity §5A.4 forces into existence.** Class-B data (analyst estimates,
target consensus, TTM ratios, scores, float) has no publication axis of its own, so D-07 supplies
one by recording *when we asked*. Without it none of that family is legal input to D-04, because
there is no honest answer to "what did this say on date D".

`CalendarEntry` is deliberately a separate entity from `CorporateEvent`, not a flag on it. A
scheduled earnings date is a *statement about the future* that gets revised; a reported earnings
result is a fact that does not. Collapsing them puts a mutable row and an immutable one in the same
table, which is how a revised date silently rewrites history.

Every monetary field on every entity is a **`Money`** (`L2-shared-money.md` CT-M.1) — an integer
minor amount plus its currency, never a bare number.

## 2.1 The Fact, and why it is not a FundamentalRow

A **Fact** is what one filing said. A **FundamentalRow** is what we believe about a period. They
differ because filers restate: two filings can report the same period with different numbers, and
both are true — one was true *then*, the other is true *now*.

Collapsing them loses the only information that makes look-ahead detectable. D-07 stores Facts and
*derives* rows at a stated `as_of`.

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-00 shared        Money, FxRate, errors, logging, ids
  ├── SEC EDGAR          submissions + companyfacts (XBRL)
  ├── FMP                prices, profiles, fundamentals, news, FX
  └── local disk         parquet + JSON (L0 §6.2 — no database)

DEPENDED ON BY
  └── every other domain, most of it through D-02

DOES NOT DEPEND ON
  ✗ any analytical domain (D-01…D-06)
  ✗ the LLM gateway — D-07 never calls a model (AP-5, ST-5)
  ✗ D-08 Orchestration — the scheduler invokes D-07, never the reverse
```

---

# 4. MODULE DECOMPOSITION

```text
src/data_engine/
├── src/edgar/          # SEC access + XBRL
│   ├── client.py       #   throttled HTTP, User-Agent, retry
│   ├── submissions.py  #   filing index per CIK
│   ├── companyfacts.py #   XBRL companyfacts → Facts
│   └── xbrl.py         #   tag resolution, unit handling, period parsing
├── src/fmp/            # FMP access
│   ├── client.py       #   throttled HTTP, key handling
│   ├── prices.py       #   OHLCV
│   ├── fundamentals.py #   statements (fallback source, §5)
│   ├── profile.py      #   sector, shares, float, market cap
│   ├── news.py
│   ├── analyst.py      #   grades, price targets, estimates — §5A.1
│   ├── insider.py      #   Form 4, SC 13D/G
│   ├── events.py       #   dividends, splits, earnings, M&A, calendars
│   ├── macro.py        #   treasury curve, indicators, sector P/E
│   └── fx.py           #   the single USDCAD rate
├── pit/                # ★ point-in-time — §6
│   ├── snapshot.py     #   as-of resolution
│   ├── restatement.py  #   multiple filings, one period
│   └── ledger.py       #   append-only Fact store
├── observation/        # ★ Class-B snapshot ledger — §5A.4
│   ├── ledger.py       #   append-only, stamped with observed_at
│   └── schedule.py     #   what gets snapshotted, how often
├── calendar/           # ★ pre-run corporate-action gate — §6A
│   ├── check.py        #   the gate: enumerate, classify, halt
│   ├── classes.py      #   the 17 event classes + knowability dates
│   ├── store.py        #   incrementally-maintained event store (QD-16)
│   └── probe.py        #   LIVE FMP reality probe, K-1…K-10 (§6A.4)
├── validation/         # quality rules, ACCEPT / FLAG / REJECT
│   ├── pipeline.py
│   ├── registry.py
│   └── rules/
├── contracts/          # authoritative on-disk shapes (CT-7.x)
├── store/              # parquet + JSON read/write, atomic
└── universe/           # membership, CIK mapping, watchlist
```

---

# 5. SOURCE ROUTING — the rule that must not drift

Two sources, one rule, three cases. **This section inherits F9 and the TTM precedence rule
verbatim, because both were bought with real defects.**

## 5.1 The cases

| Case | Filer files | Route to | Why |
|---|---|---|---|
| **A** | 10-K + 10-Q | **EDGAR** | Discrete quarters. EDGAR facts carry explicit period **start *and* end**, so a discrete quarter is distinguishable from a cumulative one **by arithmetic** |
| **B** | 20-F + 6-K *(foreign private issuer)* | **FMP** | 6-K interim reports are **cumulative year-to-date**, not discrete quarters. Ingesting them as quarterly injects 2–3× inflated revenue |
| **C** | neither, or no CIK | **fail loud** | A universe ticker with no fundamental source is an error, never a silent NaN row |

## 5.2 The measured evidence

ARM, 6-K/20-F cumulative series vs FMP discrete, verified row-by-row against external truth:

| Period | EDGAR 6-K/20-F | FMP discrete | Ratio |
|---|---|---|---|
| Q1 2025-06-30 | 1,053M | 1,053M | 1.00× |
| Q2 2025-09-30 | 2,188M | 1,135M | **1.93×** |
| Q3 2025-12-31 | 3,430M | 1,242M | **2.76×** |
| FY 2026-03-31 | 4,920M | 1,490M | **3.30×** |

Only Q1 matches, because for Q1 year-to-date *is* the quarter. This is the same defect class as the
`_cumulative_fys` bug, which understated MU's TTM revenue by 41.5% and moved its fair value by
$379/share — and which survived because a docstring asserting the wrong rule had a passing test
built on real production numbers.

## 5.3 TTM precedence

Where **both** sources have a period, **EDGAR wins for TTM line items** — for the same reason as
case A: period start *and* end are explicit, so cumulative-vs-discrete is decidable rather than
guessed. FMP exposes only the period end and must infer.

> **DE-5.1** Source selection is **per ticker, by filer class**, decided once at ingest and
> **recorded on every row** as `source`. It is never decided per-field, per-call, or by whichever
> source answered first.
>
> **DE-5.2** A row's `source` is part of its contract, not metadata. A consumer may filter on it; a
> consumer may not assume it.
>
> **DE-5.3** Mixing sources *within* one ticker's time series is forbidden without an explicit,
> recorded reason — a series that silently switches source mid-history has a discontinuity that
> looks like a business event.

---

# 5A. FMP DATA CATALOG — what the key can actually serve

> **This section is measured, not remembered.** Every row was probed live against the real
> `FMP_API_KEY` on **2026-08-15**, 156 endpoints on the **`/stable/` API, Starter tier**. Status,
> row count and field names come from the responses. FMP's marketing pages list endpoints the
> Starter key returns `402` for, and the docs lag the API in both directions, so a catalog built
> from documentation would have been wrong in ways nobody would notice until a feature silently
> returned nothing.
>
> **Re-probe before relying on this.** Plan gating changes. The probe script is disposable; what
> matters is that the numbers below were true on the date stated.
>
> **Scope note.** This catalogs *availability*, not commitment. A row here is **space made**, not a
> feature approved. Nothing is ingested until a consumer names it, and anything reaching D-04
> training additionally has to clear §5A.4.

## 5A.1 Available on Starter

Consumer column: **D-02** = computed into features; **D-01** = read as evidence by the LLM analyst;
**D-05/D-06** = risk & sizing; **D-09** = rendered directly.

### Price & market state

| Data type | `/stable/` endpoint | Grain | PIT class (§5A.4) | For |
|---|---|---|---|---|
| Daily OHLCV, split+div adjusted | `historical-price-eod/full` | ticker × day | **C** | D-02, D-03 |
| Daily OHLCV, **unadjusted** | `historical-price-eod/non-split-adjusted` | ticker × day | **A** ★ | D-02 — see QD-2 |
| Daily OHLCV, dividend-adjusted only | `historical-price-eod/dividend-adjusted` | ticker × day | C | D-02 |
| Intraday bars (5m/15m/30m/1h/4h) | `historical-chart/{interval}` | ticker × bar | A | *(unused — daily batch)* |
| Live quote + 50/200-day avg + 52w range | `quote` | ticker, now | **B** | D-09, D-05 |
| Pre/post-market bid-ask | `aftermarket-quote`, `aftermarket-trade` | ticker, now | B | D-09 |
| Trailing returns 1D…10Y, YTD | `stock-price-change` | ticker, now | B | D-02, D-09 |
| Market-cap history | `historical-market-capitalization` | ticker × day | C | D-02 |
| Exchange hours & holidays | `exchange-market-hours`, `holidays-by-exchange` | exchange | — | D-08 |

★ **`non-split-adjusted` is the only raw price feed, and it matters more than the name suggests.**
Everything else — `full`, `light`, `dividend-adjusted` — is retro-adjusted for every split that has
happened since. Measured on NVDA's 10:1 (2026-08-16, §5C.7):

| Series | Pre-split close, 2024-06-03 | What it is |
|---|---|---|
| `non-split-adjusted` | **1150.00** | **raw — what a person actually saw** |
| `full` | 115.00 | split-adjusted (÷10) |
| `light` | 115.00 | identical to `full` |
| `dividend-adjusted` | 114.80 | split-adjusted **and** dividend-adjusted |

**Volume is retro-adjusted too, in the opposite direction**: `full` reports 438,392,000 shares on
that date against a true 43,839,200 — ×10.

> ⚠ ★ **AND THE FIELD NAMES ARE INVERTED.** Measured live **2026-08-23**, building B2:
>
> ```
> historical-price-eod/non-split-adjusted  →  {"adjOpen": 1197.7, "adjClose": 1208.9,
>                                              "volume": 41238600}    ← RAW values
> historical-price-eod/full                →  {"open": 119.77, "close": 120.89,
>                                              "volume": 412386000}   ← ADJUSTED values
> ```
>
> **The endpoint whose fields are named `adj*` is the one that is NOT adjusted, and the endpoint
> with plain names is the one that is.** Reading by field name alone gets it exactly backwards, and
> **both shapes parse without error** — the wrong series would flow through the whole pipeline with
> correct dtypes. ★ **The §6A.4 live probe caught this on its first real run**; every fixture in the
> repository was written from the assumption it disproves, which is DE-37's argument in one incident.
>
> **A caution about how this was nearly missed.** The first pass (MSFT · MU · ARM) found `full` and
> `non-split-adjusted` identical to 4dp and concluded split adjustment was not the hazard. That was
> an inference from three names **none of which split in the window** — the two series agreed
> because there was nothing to disagree about. One name that actually split reversed the
> conclusion completely. See §5C.7.

### Fundamentals & derived financials

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Income / balance / cash-flow | `income-statement`, `balance-sheet-statement`, `cash-flow-statement` | ticker × period | C | D-02 — **EDGAR wins where both have it (§5.3)** |
| Growth rates (3 statements + blended) | `*-growth`, `financial-growth` | ticker × period | C | D-02 |
| 60+ ratios | `ratios` | ticker × period | C | D-02 |
| 45+ key metrics (ROIC, EV/EBITDA, Graham, cash-conversion) | `key-metrics` | ticker × period | C | D-02 |
| TTM ratios / metrics | `ratios-ttm`, `key-metrics-ttm` | ticker, now | **B** | D-02 |
| **Altman Z + Piotroski F** | `financial-scores` | ticker, now | B | D-02 — *we compute Piotroski ourselves today; this is a **cross-check**, not a replacement* |
| **Owner earnings + maintenance capex** | `owner-earnings` | ticker × period | C | D-02 ★ **directly relevant to D-19** |
| Enterprise value **with net-debt bridge** | `enterprise-values` | ticker × period | C | D-02 ★ **D-19's missing term** |
| Revenue by product / geography | `revenue-product-segmentation`, `revenue-geographic-segmentation` | ticker × period × segment | C | D-01, D-02 |
| As-reported statements (raw XBRL shape) | `financial-statement-full-as-reported` | ticker × period | C | *(EDGAR is better — §5)* |
| Report links (10-K/10-Q JSON & XLSX) | `financial-reports-dates` | ticker × period | A | D-01 |
| FMP's own DCF | `discounted-cash-flow`, `levered-discounted-cash-flow`, `custom-discounted-cash-flow` | ticker, now | B | **third-party cross-check only** — never a fair value we publish (AP-5) |

### Analyst consensus, estimates & ratings

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| **Forward estimates** — revenue/EBITDA/EBIT/net income/EPS, low·avg·high, analyst counts | `analyst-estimates` | ticker × forecast year | **B** ⚠ | D-01, D-02 |
| **Price-target consensus** — high/low/median/consensus | `price-target-consensus` | ticker, now | **B** | D-01, D-05 |
| Price-target counts & averages by window (1m/1q/1y/all) | `price-target-summary` | ticker, now | B | D-02 |
| **Individual price-target changes** — analyst, firm, old→new, price at post | `price-target-news` | event | **A** ★ | D-02, D-01 |
| **Individual rating actions** — firm, previous→new grade, action | `grades` | event | **A** ★ | D-02, D-01 |
| Rating distribution history (strongBuy…strongSell counts) | `grades-historical` | ticker × month | **A** | D-02 |
| Current rating distribution + consensus | `grades-consensus` | ticker, now | B | D-09 |
| FMP quant rating + component scores | `ratings-snapshot` / `ratings-historical` | ticker, now / × date | B / A | cross-check |
| Rating-change news | `grades-news` | event | A | D-01 |

⚠ **`analyst-estimates.date` is the forecast *target* period, not the date the estimate was
published.** There is no publication axis. Treated naively it is a textbook look-ahead — §5A.4.

★ `grades` and `price-target-news` are the honest, event-stamped versions of the same information
the consensus snapshots give you already-aggregated. **`grades` ignores date filters and returns
its whole history**: MSFT came back with **967 actions from 2012-03-16**, across **82 firms** —
fourteen years of event-stamped analyst behaviour, at Starter price. Revision *momentum* — the direction and pace of estimate and target changes — is a
well-known cross-sectional signal, and these two endpoints are the only PIT-safe way to build it.

### Corporate events & calendar

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Earnings actual vs estimate (+ revenue) | `earnings` | ticker × report | **A** | D-02 (surprise), D-01 |
| **Upcoming earnings, whole market** | `earnings-calendar` | date range | A | D-05 (event risk), D-09 |
| Dividends — declaration/record/payment/ex | `dividends` | event | **A** | D-02, D-11 |
| Dividend calendar | `dividends-calendar` | date range | A | D-09 |
| Splits (+ calendar) | `splits`, `splits-calendar` | event | **A** | D-07 (adjustment), D-02 |
| **M&A announcements** | `mergers-acquisitions-latest` | event | A | D-01 ★ thesis-invalidation trigger |
| IPO calendar / disclosures / prospectuses | `ipos-calendar`, `ipos-disclosure`, `ipos-prospectus` | event | A | *(low priority — no IPO mandate)* |
| Delistings | `delisted-companies` | event | A | **D-07 — survivorship (INV-017)** ★ |

### Filings & disclosure

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| **All SEC filings by symbol / CIK / form type** | `sec-filings-search/{symbol,cik,form-type}` | filing | **A** | D-07 cache invalidation, D-01 |
| Filings that carry financials | `sec-filings-financials` | filing | A | D-07 |
| SEC registrant profile (SIC, incorporation, FY end) | `sec-profile` | ticker | B | D-07, D-01 |

> **`sec-filings-search/form-type` is the 8-K / special-announcement feed.** Query `formType=8-K`
> over a date window and you have every material-event filing across the market, publication-stamped.
> This is the natural trigger for D-01's invalidation monitoring and for CT-7.4's filing-aware cache
> — and it is available today, unused.

### Insider & beneficial ownership

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| **Form 4 insider transactions** — who, type, shares, price, direct/indirect | `insider-trading/search` | transaction | **A** | D-02, D-01 |
| Insider buy/sell aggregates by quarter | `insider-trading/statistics` | ticker × quarter | A | D-02 |
| Market-wide latest Form 4s | `insider-trading/latest` | transaction | A | D-03 screens |
| **SC 13D/G — 5%+ beneficial ownership** | `acquisition-of-beneficial-ownership` | filing | **A** | D-01 ★ activist / stake-building |
| Congressional trading (Senate + House) | `senate-trades`, `house-trades`, `*-latest` | disclosure | A | D-01 *(novelty; weak signal)* |

### Sector, industry & macro context

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Sector / industry daily performance | `sector-performance-snapshot`, `industry-performance-snapshot` | date × sector | A | D-02 (sector-relative), D-05 |
| Sector / industry performance history | `historical-sector-performance`, `historical-industry-performance` | date × sector | A | D-02 |
| **Sector / industry P/E** | `sector-pe-snapshot`, `industry-pe-snapshot` | date × sector | A | D-02 ★ relative-valuation denominator |
| Gainers / losers / most active | `biggest-gainers`, `biggest-losers`, `most-actives` | day | A | D-03 screens |
| **Treasury curve, 1M–30Y** | `treasury-rates` | date | **A** | D-02 ★ **the risk-free rate the DCF currently hard-codes** |
| Fed funds, CPI, unemployment, … | `economic-indicators?name=…` | date × series | A | D-02, **F6 reserved desk** |
| Economic calendar | `economic-calendar` | event | A | D-05 |
| Equity risk premium by country | `market-risk-premium` | country | B | D-02 ★ **the other DCF input** |

### Company reference & structure

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Profile — sector, industry, beta, CEO, CIK, ISIN, description | `profile` | ticker | B | D-07, D-01 |
| **Float, free float, shares outstanding** | `shares-float` | ticker | B | D-02, D-05 |
| Employee count (+ history) | `employee-count`, `historical-employee-count` | ticker × filing | A | D-02 (revenue/employee) |
| Executives + compensation | `key-executives`, `governance-executive-compensation` | ticker | B / A | D-01 (management quality) |
| Company notes / issued debt | `company-notes` | ticker | B | D-01 |
| Universe lists | `stock-list`, `etf-list`, `actively-trading-list`, `financial-statement-symbol-list`, `cik-list` | market | — | **D-07 universe ★ closes QD-5** |
| Sector / industry / exchange vocabularies | `available-sectors`, `available-industries`, `available-exchanges` | market | — | D-07 validation |

### News

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| Per-ticker news (title, publisher, full `text`, url) | `news/stock` | article | **A** | D-01 |
| Market-wide latest | `news/stock-latest`, `news/general-latest` | article | A | D-01 |
| FMP editorial with tickers | `fmp-articles` | article | A | *(low value)* |

### FX & index

| Data type | Endpoint | Grain | PIT | For |
|---|---|---|---|---|
| **USDCAD spot + history** | `quote`, `historical-price-eod/full` on `USDCAD` | pair × day | A | **D-00 `FxRate` — M-5, FX-2** |
| Pair list | `forex-list` | — | — | D-07 |
| Index history (`^GSPC` etc.) | `historical-price-eod/light` | index × day | C | D-02 (beta), D-05 |
| Index list | `index-list` | — | — | D-07 |
| ETF info + sector weights | `etf/info`, `etf/sector-weightings` | ticker | B | D-05 theme exposure (M-2) |

### Server-side technical indicators

`technical-indicators/{sma,ema,wma,dema,tema,rsi,adx,williams,standarddeviation}` — all return 200.

> **Do not ingest these.** D-02 computes indicators from D-07 prices, and INV-2 determinism plus
> INV-4 parity both require *our* code path. Importing a vendor's RSI creates a second definition
> of a feature we already own, silently different from ours (F0 §12 **D-16** is exactly this
> problem, self-inflicted). Listed only so the choice is recorded as deliberate.

## 5A.2 `402` has three meanings — and the status code does not say which

> **Measured 2026-08-15** by a full dump of MSFT · MU · ARM over 2024-01-01…2026-08-15 —
> 700+ calls, 341 CSVs, 443,763 rows, in `data/fmp_dump/` (see its `README.md`). The first pass
> lost 50 responses; a second pass recovered 44. **The 6 that stayed lost and the 44 that came
> back failed identically at the HTTP layer.**

### Cause 1 — the endpoint is gated. Permanent.

| Data type | Endpoint | Worth an upgrade? |
|---|---|---|
| **Institutional / 13F ownership** (5 endpoints) | `institutional-ownership/*` | **The biggest single gap.** Holder concentration, position changes and holder performance are all unavailable |
| TTM statements | `income-statement-ttm`, `balance-sheet-statement-ttm`, `cash-flow-statement-ttm`, `latest-financial-statements` | **No** — EDGAR is the TTM source anyway (§5.3), and FMP TTM is exactly the cumulative-vs-discrete guess that rule exists to avoid |
| Press releases | `news/press-releases`, `-latest` | Moderate — 8-K via `sec-filings-search` covers the material subset |
| ESG | `esg-disclosures`, `esg-ratings`, `esg-benchmark` | **No** — no ESG mandate (`vision.md` §3) |
| ETF holdings | `etf/holdings` | Moderate — would sharpen M-2 theme exposure; `etf/sector-weightings` is a partial substitute |
| Batch quotes | `batch-quote-short` | Minor — costs N calls instead of 1 |
| M&A search by name | `mergers-acquisitions-search` | No — `-latest` is available |
| Exec-comp benchmark | `executive-compensation-benchmark` | No |
| Bulk downloads | `profile-bulk`, `ratios-ttm-bulk`, `scores-bulk` | Would cut a universe refresh from 130 calls to 1 |

### Cause 2 — a **parameter value** is gated. Permanent, and invisible until you hit it.

**The endpoint works. The arguments decide.** This is the one that bites in production, because
the same call succeeds in a probe and fails later when a `limit` grows or a backfill widens a
date range.

| Endpoint | Legal on Starter | Returns `402` |
|---|---|---|
| `analyst-estimates` | `limit<=10`, `period=annual` | `limit>=20`, **`period=quarter`** |
| `key-metrics`, `ratios` | `period=annual` (limit 40 is fine) | **`period=quarter`** |
| `revenue-*-segmentation` | `period=annual` | `period=quarter` |
| `economic-calendar` | span `<=180d` | span `>=365d` |
| `news/stock` | `page=N` paging | **any `from`/`to` at all** |
| `governance-executive-compensation` | MSFT, NVDA | **MU, ARM** — *per company* |
| `historical-price-eod/*` | `^GSPC`, `^IXIC`, `^DJI`, `^RUT` | `^SOX` |

> **`period=quarter` being gated on `key-metrics` and `ratios` is a real constraint on D-02.**
> Quarterly ratio and metric series cannot be bought at this tier — they must be **computed by us
> from the quarterly statements**, which *are* available. That is the right answer anyway (AP-5,
> constitution INV-2), but it is now a requirement rather than a preference.

### Cause 3 — transient under burst. Succeeds on retry, unchanged.

`key-metrics`, `ratios`, `revenue-*-segmentation`, `splits-calendar` and index prices all returned
`402` inside a 595-call run and **`200` on retry with identical parameters**.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A 402 IS NOT EVIDENCE OF A PLAN GATE UNTIL IT HAS BEEN RETRIED. ║
║                                                                  ║
║  In the first pass, key-metrics and ratios came back 402 for     ║
║  all three tickers. Read naively that says "not on your plan".   ║
║  Both return 40 periods of data on retry.                        ║
║                                                                  ║
║  Had ingest treated 402 as "no data", D-02 would have lost every ║
║  key metric and every ratio for the whole universe — and the     ║
║  downstream frame would have looked like a clean empty result,   ║
║  not a failure. That is the D-17 defect class exactly.           ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **DE-15** | A `402` is **retried with backoff** before it is reported. If it persists it fails loud (P5), and the error records **the endpoint *and the parameters*** — the parameter is half of what was refused. A `402` is never converted into an empty result |
| **DE-16** | A parameter combination known to be plan-gated is **rejected at the client boundary**, not sent and failed. The gate list is data, kept beside the client, and re-probed rather than remembered |
| **DE-46** | ★ **The 402 retry is a CLASSIFICATION probe, not error recovery — the one carve-out from L4 **EH-14** (*"only `src/orchestration/` retries"*).** ⚠ **The two rules contradict as written** (found 2026-08-23 building B2): DE-15 and **AC-7.32** put the retry inside D-07's client, EH-14 forbids any domain from retrying. ★ **What resolves it is that §5A.2's three causes are indistinguishable from a single response** — a 402 is *not yet a fact* until it has been re-sent, so the probe is how D-07 learns what it is reporting, not how it recovers from it. **EH-14's actual objection is answered rather than waived**: the attempt count is carried on the raised `PlanGatedError` and into the provenance envelope (CT-7.5), so it still reaches the RunManifest. **Recovery retries remain D-08's alone** |

## 5A.2a Superseded heading — *(kept so existing "§5A.2 paywalled" citations resolve)*

| Data type | Endpoint | Worth an upgrade? |
|---|---|---|
| **Institutional / 13F ownership** (5 endpoints) | `institutional-ownership/*` | **The biggest single gap.** Holder concentration, position changes and holder performance are all unavailable |
| TTM statements | `income-statement-ttm`, `balance-sheet-statement-ttm`, `cash-flow-statement-ttm` | **No** — EDGAR is the TTM source anyway (§5.3), and FMP TTM is exactly the cumulative-vs-discrete guess that rule exists to avoid |
| Press releases | `news/press-releases`, `-latest` | Moderate — 8-K via `sec-filings-search` covers the material subset |
| ESG | `esg-disclosures`, `esg-ratings`, `esg-benchmark` | **No** — no ESG mandate (`vision.md` §3) |
| ETF holdings | `etf/holdings` | Moderate — would sharpen M-2 theme exposure; `etf/sector-weightings` is a partial substitute |
| Batch quotes | `batch-quote-short` | Minor — costs N calls instead of 1 |
| M&A search by name | `mergers-acquisitions-search` | No — `-latest` is available |
| Executive comp benchmark | `executive-compensation-benchmark` | No |
| Bulk downloads | `profile-bulk`, `ratios-ttm-bulk`, `scores-bulk` | Would cut universe refresh from 130 calls to 1 |

## 5A.3 `404` — the endpoint does not exist. Not a gate; an absence.

**A `404` and a `402` are completely different facts and must never be handled alike.** A `402`
says *"this exists and you cannot have it"* — the fix is money, or a parameter change, or a retry
(§5A.2). A `404` says *"there is no such product"* — no plan buys it, retrying is pointless, and
the only fix is a different source or a different design.

Recording these matters more than recording the ones that work: each is a data type someone will
eventually assume exists, look for, fail to find, and then quietly build around with something
worse. The list is the point.

| Data type | Status | If it is wanted |
|---|---|---|
| **Sentiment — social or news-derived** | **No endpoint.** `news/stock-sentiment`, `social-sentiments`, `historical-social-sentiment` all 404 | FMP serves the article `text`; **scoring it is D-01's job via the LLM gateway**, not an ingested field. This is the honest answer to "can we poll sentiment": no, and we should not want to — a vendor sentiment score is an uncited claim (AP-2) |
| **Short interest / days-to-cover** | 404 | Would need FINRA bi-monthly files or another vendor. A real gap for a squeeze/crowding feature |
| **Fail-to-deliver** | 404 | SEC publishes it directly |
| **Earnings-call transcripts** | 404 | A genuine loss for D-01 — management tone and guidance language are exactly what an LLM analyst should read |
| Commitment of Traders | 404 | Irrelevant — no futures (M-1) |
| 1-minute bars | 404 | Irrelevant — daily batch |
| `all-shares-float` (bulk) | 404 | Per-ticker `shares-float` works |

### The three that actually cost us something

**Sentiment does not exist as an FMP product, and that is the right outcome.** Three plausible
endpoint names were probed and all 404: `news/stock-sentiment`, `social-sentiments`,
`historical-social-sentiment`. What FMP *does* serve is the article body — `news/stock.text`,
populated on 1,031 of 2,081 MSFT articles in the dump. So sentiment is available to this system as
**evidence to be read**, not as a number to be ingested. Scoring it is D-01's job through the LLM
gateway, where the reasoning is citable (AP-2) and the prompt is versioned (AP-6). A vendor
sentiment float has neither property: it is an uncited claim with a plausible-looking magnitude,
which is the exact shape of input P5 and AP-2 exist to keep out of a verdict.

**Earnings-call transcripts are the real loss.** Management tone, guidance language and the
question-and-answer section are among the highest-signal qualitative inputs a research analyst
reads, and D-01 is precisely the domain built to read them. There is no in-house substitute and no
FMP tier that sells them. Recorded as **QD-9**; closing it means a second vendor, which is a
`vision.md`-level decision, not an implementation one (§2.2: "adding a third source is a decision,
not an implementation detail").

**Short interest is a genuine feature gap.** Days-to-cover and short-interest change are standard
crowding/squeeze inputs for a cross-sectional model, and nothing in the catalog substitutes.
FINRA publishes the bi-monthly file directly; whether that is worth a third source is the same
`vision.md` decision.

## 5A.3a The reference dump — `data/fmp_dump/` — **keep it**

Everything §5A asserts was measured against a real pull: **MSFT · MU · ARM, 2024-01-01 →
2026-08-15, 341 CSVs, 443,763 rows, 82 MB, 700+ API calls**, produced 2026-08-15.

| ID | Rule |
|---|---|
| **DE-17** | **`data/fmp_dump/` is retained as a permanent debugging reference and must not be deleted or regenerated in place.** It is the only frozen record of what FMP returned on a known date, and it is the fixture every claim in §5A / §5C is checkable against. When a re-pull is wanted, write it to `data/fmp_dump_<YYYY-MM-DD>/` beside this one — **two dated pulls of the same periods are the only way this system can observe an FMP restatement at all** (§5C.2) |

It is gitignored (`data/`), so it is a working artifact rather than a committed one. That is
deliberate — 82 MB of vendor data does not belong in git — but it means **the retention rule is a
convention this spec has to state, because nothing enforces it.**

### What is in it

Start at **`_MANIFEST_FINAL.csv`** — one row per file with endpoint, params, rows, cols, date
range and bytes. `README.md` in the same directory is the human-facing summary. Every CSV carries
provenance columns `_ticker`, `_endpoint`, `_params`, `_fetched_at`.

| Family | Files | What makes it worth keeping |
|---|---|---|
| **Daily prices, 4 adjustment variants** | 12 | `full` · `light` · `non-split-adjusted` · `dividend-adjusted`. Diffing them is what corrected the QD-2 premise (§5A.1) |
| **Intraday bars** | 15 | 5m/15m/30m/1h/4h chunked across 3 years. **The retention boundary is visible as empty leading chunks** — 5min data starts 2024-01-22, so intraday depth is ~2.5y, not 3 |
| **Statements** | 18 | annual + quarterly, 40 periods, **with `filingDate` and `acceptedDate`** (§5C.1) |
| **Growth series** | 24 | per-statement + blended `financial-growth` |
| **Key metrics / ratios** | 6 | **annual only** — `period=quarter` is plan-gated (§5A.2 cause 2) |
| **Enterprise values + owner earnings** | 12 | ★ the net-debt bridge and maintenance-capex figure **D-19** needs |
| **As-reported XBRL** | 6 | one row per tag per period. MU quarterly = 5,304 rows over **536 distinct tags**, 20 periods |
| **Revenue segmentation** | 12 | product + geographic, nested `data` exploded per segment. Annual only |
| **Analyst** | 27 | estimates, target consensus/summary/news, `grades`, `grades-historical`, `ratings-historical` |
| **Corporate events** | 30 | dividends (with `declarationDate`), splits, earnings (with `lastUpdated`), employee counts, executives, report links |
| **SEC filings** | 9 | by symbol and by CIK, **including amendments** |
| **Insider & ownership** | 15 | Form 4, quarterly statistics, SC 13D/G, senate + house trades |
| **Technical indicators** | 36 | all 9 types; SMA/EMA at 10/20/50/200. Kept **only** as a comparison baseline — D-02 owns our definitions |
| **Macro** | 18 | treasury curve + **17 valid `economic-indicators` series names, discovered by probing** (the names are undocumented; `GDP`, `realGDP`, `realGDPPerCapita`, `inflation` all return empty) |
| **Sector / industry** | 6 | performance + P/E snapshots and history |
| **Market-wide feeds** | 20 | earnings/dividends/splits/economic calendars, M&A, delistings, IPOs, gainers/losers |
| **News** | 5 | 2,081 MSFT · 1,895 MU · 186 ARM, **with full body text** — and only ~92 days deep (§5C.4) |
| **Reference** | 15 | 38,723-symbol stock list, ETF list, CIK list, sectors, industries, exchanges, market hours, holidays |
| **FX & index** | 8 | USDCAD, `^GSPC`, `^IXIC`, `^DJI`, `^VIX`, ETF info + sector weights |
| **`UNAVAILABLE__*`** | 12 | **zero-row files recording what the key cannot get.** Deliberate: an absent file is ambiguous, an empty file with a manifest row is evidence |

### Two things it incidentally proved

**ARM is `20-F` / `6-K` / `SC 13G` — no 10-K, no 10-Q.** `sec_filings_search_symbol__ARM.csv`
contains the full form-type list, so §5.1 case B is now backed by primary evidence in this
repository rather than by an assertion inherited from F9.

**MU's quarterly series is genuinely discrete, not cumulative.** Two independent endpoints agree to
1.0000 on all 12 quarters (`income-statement.revenue` vs `earnings.revenueActual`), and the four
quarters of FY2024 and FY2025 each sum **exactly** to their annual figure. Given that the
`_cumulative_fys` defect cost 41.5% on MU's TTM revenue, having a frozen artifact that demonstrates
the current series is clean is worth the 82 MB on its own.

## 5A.4 The point-in-time hazard — read this before wiring any of it to D-04

§6 guarantees "knowable on date D". **Most of §5A.1 cannot satisfy that guarantee on its own**,
and the failure is invisible: the number looks right, the backtest improves, and the skill does not
survive contact with live data. Three classes, and the class decides the ingest design.

| Class | What it means | Examples | What D-07 must do |
|---|---|---|---|
| **A — natively point-in-time** | The row carries its own publication date and is never revised | news, Form 4, SEC filings, `grades`, `price-target-news`, dividends, splits, earnings actuals, sector performance, treasury rates | Store as-is with its publication date; the §6.3 as-of filter works unchanged |
| **B — snapshot, no history** | Current value, **no as-of axis at all**. Ask tomorrow, get a different number, with no way to recover today's | `analyst-estimates`, `price-target-consensus`, `grades-consensus`, `ratios-ttm`, `key-metrics-ttm`, `financial-scores`, `shares-float`, `profile`, FMP DCF | **We must create the axis.** Snapshot on a schedule and append to an observation ledger stamped with **our** `observed_at`. There is no retrofit — history not captured is gone |
| **C — restated series** | Carries a period date but reflects *today's* restatement of that period | statements, `ratios`, `key-metrics`, `financial-growth`, `enterprise-values`, `historical-market-capitalization`, adjusted prices | The problem §5/§6 already solve for EDGAR. For FMP-routed rows there is **no restatement history**, so the PIT guarantee is weaker — record that, do not paper over it |

```text
╔══════════════════════════════════════════════════════════════════╗
║  CLASS B IS THE ONE THAT WILL BITE.                              ║
║                                                                  ║
║  analyst-estimates has a `date` field. It is the FORECAST        ║
║  target period — FY2027 — not the day the estimate was made.     ║
║  Joining it to a 2024 training row gives the model a 2026        ║
║  opinion about 2027 and calls it a 2024 feature.                 ║
║                                                                  ║
║  Same shape: price-target-consensus, grades-consensus,           ║
║  ratios-ttm, financial-scores. Every one has an obvious          ║
║  join key and no publication date.                               ║
║                                                                  ║
║  DE-6.4 says as_of is never defaulted to today. Class B data      ║
║  defaults to today STRUCTURALLY — it has no other value to        ║
║  offer. The snapshot ledger is not a nicety; it is the only      ║
║  thing that makes this data legal input to D-04.                 ║
╚══════════════════════════════════════════════════════════════════╝
```

> **The consolation.** For the two Class-B families that matter most, a Class-A equivalent already
> exists and is available: `grades` and `price-target-news` are the event-stamped feeds behind
> `grades-consensus` and `price-target-consensus`. **Prefer the event feed and aggregate it
> ourselves at an as-of** — that is strictly better than snapshotting the vendor's aggregate,
> because it is reconstructible backwards rather than only forwards from today.
>
> `grades-historical` (monthly rating-distribution history) is the same trick FMP has already done
> for us, and it is the template for what the snapshot ledger should look like.

## 5A.4a Which agent each data type actually serves

The catalog is organised by *what FMP calls things*. This is the same inventory organised by **who
consumes it**, which is the question that matters for planning D-02's output contracts (Q-10).

Two consumers, and they fail in different ways (L0 §1.6), so they want different data:

| | **D-01 Fundamental analyst** (SEAT-2, LLM) | **D-03/D-04 Quant** (SEAT-3, ML) |
|---|---|---|
| Unit | one company, deeply | the whole universe, cross-sectionally |
| Wants | **narrative, causes, disclosure text, one-off events** | **numeric, dense, comparable across 130 names, dated** |
| Tolerates | sparse, irregular, unstructured | nothing sparse — a feature present for 12 names is noise |
| Breaks on | a hallucinated fact, an uncited number | look-ahead, a NaN column, a regime break |

> **Everything below is computed by D-02 and served to both.** Neither analyst seat reaches D-07
> directly, and neither owns any of this data — that is what keeps INV-014 intact (L0 §4.2). The
> columns say *who the feature is built for*, not who owns it.

### Serves the QUANT seat — dense, dated, cross-sectional

These exist for every name every day (or every quarter) and can be ranked across the universe.

| Data | Source | Feature shape |
|---|---|---|
| OHLCV + volume | `historical-price-eod/*` | returns, momentum, volatility, gaps, 52w position |
| Intraday bars | `historical-chart/*` | realised vol, overnight gap, open-to-close — **~2.5y depth only** |
| Statements (quarterly) | `income-statement`, `balance-sheet-statement`, `cash-flow-statement` | growth, margins, accruals, leverage — **and they carry `filingDate`, so they are lagged correctly** |
| Ratios & metrics | **computed by D-02** from the above | `period=quarter` is plan-gated, so these must be ours anyway (§5A.2) |
| Enterprise value + net debt | `enterprise-values` | EV multiples, leverage — **the D-19 term** |
| Analyst revision events | `grades`, `price-target-news` | **revision momentum** — count and direction of upgrades/target raises in a trailing window. Class A, 14 years deep, and the single most under-used family in the catalog |
| Rating distribution | `grades-historical` | monthly consensus tilt |
| Earnings surprise | `earnings` (`epsActual` vs `epsEstimated`) | SUE, surprise drift |
| Insider aggregates | `insider-trading/statistics`, `insider-trading/search` | net buy/sell ratio over trailing quarters |
| Sector / industry performance & P/E | `sector-*`, `industry-*` | **sector-relative** normalisation — the denominator `fundamental_analysis/features/**` currently fakes with a constant |
| Treasury curve, macro series | `treasury-rates`, `economic-indicators` | regime features, discount-rate input, F6 |
| Float & share count | `shares-float` | turnover, size — **but see §5C.3** |
| Index & ETF series | `^GSPC`, `^IXIC`, `^VIX`, `etf/sector-weightings` | beta, market regime, M-2 theme exposure |
| Delistings | `delisted-companies` | **survivorship correction (INV-017)** |

### Serves the FUNDAMENTAL seat — narrative, sparse, one-off

These are irregular by nature. Feeding them to a cross-sectional model produces a column that is
null for 95% of the panel; feeding them to an LLM analyst produces exactly the evidence it needs.

| Data | Source | What D-01 does with it |
|---|---|---|
| **News with full body text** | `news/stock.text` | the qualitative read — materiality, thesis invalidation. **The sentiment answer** (§5A.3) |
| **SEC filings index incl. 8-K** | `sec-filings-search/{symbol,form-type}` | material-event trigger; cache invalidation (CT-7.4) |
| **As-reported XBRL** | `financial-statement-full-as-reported` | what the filer actually said, tag by tag — the audit trail behind a cited number |
| Revenue by segment & geography | `revenue-*-segmentation` | where the business actually earns; concentration risk |
| **M&A announcements** | `mergers-acquisitions-latest` | a thesis-invalidating event by definition |
| **SC 13D/G** | `acquisition-of-beneficial-ownership` | activist or strategic stake-building |
| Individual analyst actions | `price-target-news`, `grades-news` | who changed their mind and what they said |
| Forward estimates | `analyst-estimates` | the market's expectation the thesis argues with — **Class B, annual only, `limit<=10`** |
| Executives & compensation | `key-executives`, `governance-executive-compensation` | management quality, incentive alignment — **402 on MU and ARM** |
| Employee count history | `employee-count` | revenue/employee trend, headcount inflection |
| Company notes / debt issues | `company-notes` | capital structure narrative |
| Report links | `financial-reports-dates` | the source document itself |
| Congressional trades | `senate-trades`, `house-trades` | novelty; weak, and honest about it |

### Serves neither — recorded so nobody re-derives the decision

| Data | Why not |
|---|---|
| `technical-indicators/*` | D-02 computes indicators. A vendor RSI is a **second definition** of a feature we own, silently different from ours — F0 §12 **D-16** is this exact defect, self-inflicted once already (AC-7.31) |
| `discounted-cash-flow`, `levered-*`, `custom-*` | A fair value we did not compute cannot be published (AP-5). Useful **only** as a cross-check against our own DCF, especially while D-19 is open |
| `ratings-snapshot`, `financial-scores` | Vendor composite scores. Same objection: uncited, unversioned, and they smuggle someone else's model into our verdict |
| `biggest-gainers/losers`, `most-actives` | Screening convenience; nothing here is not already derivable from the price panel |

## 5A.4b The event calendar — a planned D-07 surface

> **Status: specified in §6A** *(as of v0.5.0)*. This subsection stays as the **data inventory** —
> what the catalog can supply an event calendar. **§6A is the behaviour**: a pre-run gate over the
> whole universe that halts on an unhandled corporate action, plus the live reality probe that
> keeps it honest. Read this for *what is available*, §6A for *what D-07 must do with it*.

The intent is a **calendar check for special events** — dividends, earnings, splits, M&A, 8-K
filings, macro releases — consumed by *both* seats: D-01 as thesis-invalidation triggers and
event-risk context, D-03/D-04 as event-proximity features in training.

Available today, all of it:

| Event | Source | The date that makes it **knowable** |
|---|---|---|
| Earnings — scheduled | `earnings-calendar` | *(none — the schedule itself is revised; see below)* |
| Earnings — reported | `earnings` | the report date, with `epsActual` present |
| Dividend | `dividends` | **`declarationDate`** — *not* `date`, which is the ex-date |
| Split | `splits`, `splits-calendar` | announcement is in an 8-K; `date` is the *effective* date |
| Material event | `sec-filings-search/form-type=8-K` | `acceptedDate` |
| M&A | `mergers-acquisitions-latest` | `acceptedDate` |
| 5%+ stake | `acquisition-of-beneficial-ownership` | `filingDate` |
| Macro release | `economic-calendar` | the release date |
| Analyst action | `grades`, `price-target-news` | `publishedDate` |

```text
╔══════════════════════════════════════════════════════════════════╗
║  A CALENDAR IS THE EASIEST PLACE IN THIS SYSTEM TO INTRODUCE     ║
║  LOOK-AHEAD, BECAUSE FORWARD-DATED ROWS ARE THE WHOLE POINT.     ║
║                                                                  ║
║  Measured in the dump:                                           ║
║    earnings-calendar    34.6% of rows are future-dated           ║
║    dividends-calendar   15.3%                                    ║
║    splits-calendar       3.0%                                    ║
║                                                                  ║
║  Every one of those rows is a fact about a date that has not     ║
║  happened. Joined to a training row by event date — the obvious  ║
║  join — the model learns that an earnings date was known months  ║
║  ahead. Sometimes it was. Sometimes the date moved, and the      ║
║  calendar carries only today's answer.                           ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **DE-18** | A calendar entry carries **two dates**: the event date and the date the event became *knowable*. Where the vendor supplies only one, the calendar is **snapshot into CT-7.6** and the knowability date is our `observed_at`. There is no third option — a single-date calendar entry cannot be served to D-04 |
| **DE-19** | **Scheduled and occurred are different entities** (§2 `CalendarEntry` vs `CorporateEvent`). A scheduled earnings date is a revisable claim about the future; a reported result is a fact. They may not share a table, because a revised schedule would otherwise silently rewrite history |
| **DE-20** | An event feature for D-04 is built from the **occurred** entity plus the *snapshot history* of the scheduled one — never from today's calendar read |

> **Why `declarationDate` matters more than it looks.** MSFT's dividends declare a median **~72
> days before the ex-date** (measured across 90 rows, all with `declarationDate` populated). Build
> a "dividend coming up" feature keyed on `date` and it fires far too late to be the signal it
> claims to be; key it on `declarationDate` and it is both earlier *and* honestly point-in-time.

## 5A.5 Priority — what to make space for first

Ordered by *value ÷ effort*, given the mandate and the known open defects. This is a
recommendation for the D-02/D-07 specs to accept or reject, not a commitment.

| # | Data | Why now |
|---|---|---|
| **1** | `enterprise-values` (net-debt bridge) + `owner-earnings` | **D-19.** The DCF divides an enterprise value by share count with no net-debt subtraction. `enterprise-values` supplies `minusCashAndCashEquivalents` + `addTotalDebt` — the missing term — and `owner-earnings` supplies FMP's own maintenance-capex figure, which is the cross-check the reality probe needs before anything is changed |
| **2** | `treasury-rates` + `market-risk-premium` | The DCF discount rate is currently a config constant. These are the two live inputs a WACC actually needs, both PIT-clean |
| **3** | `sec-filings-search/form-type` (8-K) | Publication-stamped material-event feed → CT-7.4 cache invalidation and D-01 invalidation monitoring. Both already specified, neither has a trigger |
| **4** | `grades` + `price-target-news` | The revision-momentum family. Class A, event-stamped, cross-sectional, and unavailable from EDGAR at any price |
| **5** | `insider-trading/search` + `insider-trading/statistics` | Class A, already partly wired (`fmp_provider.py:622`), unused downstream |
| **6** | `non-split-adjusted` prices | Closes **QD-2** properly instead of accepting split look-ahead. Cheap: same endpoint family |
| **7** | `sector-pe-snapshot` / `industry-pe-snapshot` | The denominator for sector-relative valuation, which `fundamental_analysis/features/**` computes today against a fixed constant |
| **8** | `delisted-companies` | **INV-017 survivorship.** The universe is live-listed names only; nothing currently accounts for what left |
| **9** | The Class-B snapshot ledger | Not a data type — the *mechanism* §5A.4 requires. Nothing in the B column is safe for D-04 until it exists |
| **10** | `stock-list` / `financial-statement-symbol-list` | Closes **QD-5** (where the universe lives) with a source of truth rather than a hand-kept config |

---

# 5C. WHAT THE DUMP REVEALED — measured PIT & restatement defects

> Findings from inspecting `data/fmp_dump/` on 2026-08-15. Each is reproducible against the
> retained files (DE-17). **Three of these contradict §5A's original classification**, which is the
> argument for keeping the artifact rather than the summary.

## 5C.1 Good news: FMP statements *are* point-in-time capable

§5A originally filed the three statements as **Class C** (period-dated, no as-of). That was wrong.

```
income-statement / balance-sheet-statement / cash-flow-statement carry:
    date          period end        2026-05-28
    filingDate    date filed        2026-06-25
    acceptedDate  SEC timestamp     2026-06-24 18:59:46
```

Measured on MU across 40 quarters: filing lag **min 20 days, median 28, max 57**. That is the exact
window in which a naive `date`-keyed join is look-ahead — **on average four weeks of it, every
quarter, on every fundamental feature.**

| ID | Rule |
|---|---|
| **DE-21** | Fundamental rows sourced from FMP are placed in time by **`acceptedDate`**, falling back to `filingDate` — **never by `date`**, which is the period end and precedes knowability by 20–57 days |

**But every *derived* periodic drops it.** `key-metrics`, `ratios`, `enterprise-values`,
`financial-growth`, `owner-earnings`, the three `*-growth` series, `revenue-*-segmentation` and
`financial-statement-full-as-reported` carry **only the period end** — no `filingDate`, no
`acceptedDate`.

| ID | Rule |
|---|---|
| **DE-22** | A derived periodic with no filing date **inherits the `acceptedDate` of the statement for the same `(ticker, period_end, period_type)`**. If no statement row matches, the derived row is **not served to a PIT consumer** — it cannot be placed in time, and an unplaceable row is DE-6.3's rule applied one layer out |

## 5C.2 `lastUpdated` proves FMP rewrites history — and is useless as an axis

`earnings` carries `lastUpdated`, which looks like the restatement axis this system needs. It is not.

| Ticker | Reported quarters | Distinct `lastUpdated` values | Median lag after report |
|---|---|---|---|
| MSFT | 99 | **8** | 4,018 days |
| MU | 99 | **6** | 4,174 days |

99 quarters share 8 timestamps, and the median row was "last updated" **eleven years** after it was
reported. That is not per-row revision tracking — it is a **batch reload stamp**. A 2003 quarter
carrying `lastUpdated = 2025-09-06` means FMP rewrote its whole history in September 2025.

Two consequences, and the second is the important one:

1. `lastUpdated` **cannot** be used as a knowability date. It is later than the report, by years.
2. **FMP's history is not stable.** Whole spans get rewritten, silently, with no version, no
   diff, and no notification.

```text
╔══════════════════════════════════════════════════════════════════╗
║  FMP HAS NO RESTATEMENT HISTORY. IT SERVES ONE ANSWER: TODAY'S.  ║
║                                                                  ║
║  EDGAR is different — every filing is immutable and separately   ║
║  addressable, which is why §6 can reconstruct what was knowable  ║
║  on any past date from the Fact ledger.                          ║
║                                                                  ║
║  For an FMP-routed ticker there is no such reconstruction. If a  ║
║  number changes, the old value is gone, and NOTHING IN THE       ║
║  RESPONSE INDICATES THAT IT CHANGED.                             ║
║                                                                  ║
║  The only way this system can ever observe an FMP restatement    ║
║  is to have kept a dated earlier pull and diff it. That is why   ║
║  DE-17 retains data/fmp_dump/ and why re-pulls go to a NEW       ║
║  dated directory rather than overwriting.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **DE-23** | The PIT guarantee (§6.1) is **strictly weaker for FMP-routed tickers than for EDGAR-routed ones**, and a served artifact must say which it is. `source` is already on every row (DE-5.2); a consumer computing a backtest over FMP-routed fundamentals is entitled to know its as-of is best-effort rather than reconstructed |
| **DE-24** | Re-ingestion of an FMP periodic **diffs against the prior stored value** and records a change event. This is the only restatement detection available on that side, and it works only if we never overwrite silently |

## 5C.3 `historical-market-capitalization` has a ~28-day look-ahead, every quarter

Dividing `marketCap` by `close` recovers the share count FMP used. For MU over 657 days it takes
**9 distinct values** — so it is *not* one retro share count applied to all history, which is the
usual failure and would have been worse.

It is a subtler failure. The step dates:

| Share count steps on | Statement period end | `filingDate` |
|---|---|---|
| 2024-02-29 | 2024-02-29 | 2024-03-21 |
| 2024-05-30 | 2024-05-30 | 2024-06-27 |
| 2024-08-29 | 2024-08-29 | 2024-10-04 |
| 2025-02-27 | 2025-02-27 | 2025-03-21 |
| 2025-08-28 | 2025-08-28 | 2025-10-03 |

**The share count changes on the period-end date — 21 to 36 days before the filing that disclosed
it.** Nobody knew MU's Q3 share count on 2024-05-30; it was published on 2024-06-27. So every
`marketCap` value in that window is built from a number that was not yet public.

This is not cosmetic. Market cap feeds size, every EV and P/x multiple, and index/theme weighting —
so the leak propagates into a large share of the valuation feature set.

| ID | Rule |
|---|---|
| **DE-25** | `historical-market-capitalization` is **not served to a PIT consumer**. Market cap for a past date is computed as `close(d) × shares_outstanding(as_of=d)`, where the share count is placed in time by DE-21 — i.e. it steps on the **filing** date, not the period end |

## 5C.4 News is ~92 days deep, not 3 years

`news/stock` pages return the **last ~3 months only**, regardless of paging depth:

| Ticker | Articles | Range | Days covered | With body text |
|---|---|---|---|---|
| MSFT | 2,081 | 2026-05-15 → 2026-08-15 | 93 of 92 | 1,031 |
| MU | 1,895 | 2026-05-15 → 2026-08-15 | 93 of 92 | 687 |
| ARM | 186 | 2026-05-15 → 2026-08-13 | 69 of 90 | 63 |

Coverage inside the window is dense for large caps and **thin for ARM (77% of days, 63 bodies)** —
a coverage bias that tracks market cap and would show up as a spurious cross-sectional feature.

**There is no historical news backfill at any price.** Any news-derived feature for D-04 must be
accumulated forward from the day we start capturing, which makes the CT-7.6 observation ledger the
prerequisite for news features too — not just for Class-B snapshots.

| ID | Rule |
|---|---|
| **DE-26** | News is **captured forward and stored**, never re-fetched for history. A news-derived feature's usable training window begins at first capture, and that date is recorded so a backtest cannot silently extend before it |

## 5C.5 Smaller findings, each with a rule or a note

| Finding | Evidence | Consequence |
|---|---|---|
| **`acceptedDate` is usually after the close** | 408 of 437 MSFT filings accepted at or after 16:00 ET | Knowability is the **next session**, not the filing date. A same-day join is a half-day leak |
| **Form 4 lag is usually 1–2 days but has a long tail** | MSFT median 1d, p95 4d, **max 233d** | Insider features must key on `filingDate`. Keying on `transactionDate` leaks by up to 233 days on the tail |
| **`price-target-news` carries `priceWhenPosted`** | present on all rows | Implied upside at post time is computable **without joining a price series** — natively PIT, no join risk |
| **`grades` ≠ `grades-historical`** | `grades` = 967 event rows from 2012; `grades-historical` = 90 monthly distribution snapshots from 2019 | Different entities. The first is Class A events; the second is a pre-aggregated monthly panel |
| **`dividends.adjDividend` is a retro-adjusted field** | equals `dividend` on all 90 MSFT rows (no split in range) | Not proven adjusted by this sample, but it is by construction. Use `dividend`; treat `adjDividend` as Class C |
| **57 of 341 files have no date column at all** | `ratios-ttm`, `key-metrics-ttm`, `financial-scores`, `price-target-consensus`, `grades-consensus`, `ratings-snapshot`, `stock-price-change`, `insider-trading/statistics`, `key-executives`, … | The Class-B list, enumerated. Every one needs CT-7.6 before it can reach D-04 |
| **Intraday depth is ~2.5 years** | 5min starts 2024-01-22 against a 2024-01-01 request | State it; do not let a backtest assume 3 years |
| **Sector snapshots return `200` with zero rows on non-trading dates** | 2026-08-15 empty, 2026-08-14 fine | An empty result is not an error — but it is also not a zero. DE-14 |

## 5C.7 Prices ARE restated data — QD-2 answered, and the earlier answer was wrong

> **NVDA added to the dump 2026-08-16** specifically because it split 10:1 on 2024-06-10, inside
> the window. 91 files, 71,214 rows, written additively — nothing from the 2026-08-15 pull was
> touched (DE-17). This is the test case the first three names could not provide.

### What the split does to the panel

| | 2024-06-07 (pre) | 2024-06-10 (post) |
|---|---|---|
| `non-split-adjusted` close | **1208.90** | 121.79 |
| `full` close | **120.89** | 121.79 |
| `non-split-adjusted` volume | **41,238,600** | 314,162,650 |
| `full` volume | **412,386,000** | 314,162,650 |

`full` divides every pre-split price by 10 and multiplies every pre-split volume by 10. The
`splits` endpoint carries the events needed to reconstruct this — NVDA: **10:1 2024-06-10, 4:1
2021-07-20, 3:2 2007-09-11, 2:1 2006-04-07**.

Two dependent series inherit the adjustment:

- **`historical-market-capitalization` implies 24.578B shares in January 2024**, when the true
  count was 2.458B. The market-cap *value* is invariant (adjusted price × adjusted shares = raw ×
  raw), so the number is right — but **the share count recoverable from it is off by the split
  factor**, which compounds DE-25.
- **Vendor `technical-indicators/*` are computed on the adjusted series** — SMA-50 reads ~95 against
  a close of 121 on the split date. Another reason not to ingest them (AC-7.31).

### The hazard is determinism, not classical look-ahead

This deserves precision, because the obvious reading is wrong.

Split adjustment is **necessary**, not a defect: returns computed on the raw series would show a
fake −90% on 2024-06-10. And most quant features are **scale-invariant** — returns, price ratios,
dollar volume (115 × 438M ≡ 1150 × 43.8M), z-scores and cross-sectional ranks within a ticker all
come out identical either way. For those, adjusted is correct and nothing is leaking.

What breaks is reproducibility:

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE SAME QUERY, FOR THE SAME PAST DATES, RETURNS DIFFERENT      ║
║  NUMBERS DEPENDING ON WHEN YOU ASK.                              ║
║                                                                  ║
║  A backtest run on 2024-06-01 saw NVDA at $1,150.                ║
║  The same backtest, same code, same config, same date range,     ║
║  re-run today sees $115.                                         ║
║                                                                  ║
║  Constitution INV-2 says: same input data + same config =>       ║
║  byte-identical output. The config did not change. The code did  ║
║  not change. THE INPUT DATA CHANGED UNDERNEATH, silently, on a   ║
║  vendor's schedule, for dates already in the past.               ║
║                                                                  ║
║  That is the same class of defect as a fundamental restatement   ║
║  (§5C.2) — arriving through the price panel, which nobody was    ║
║  watching because "prices are just prices".                      ║
╚══════════════════════════════════════════════════════════════════╝
```

**Where it *is* genuine look-ahead** — the features that are not scale-invariant:

| Affected | Why |
|---|---|
| **Absolute price thresholds** | **M-1 excludes penny stocks (< $5).** Applied to an adjusted history, a *reverse* split makes a stock that traded at $0.50 look like $10 retroactively — so a mandate filter run over adjusted history silently admits names that were penny stocks at the time. This is a mandate-compliance defect, not merely a modelling one |
| **Absolute or cross-sectional volume** | pre-split volume is inflated by the split factor; a "volume > X shares" screen and any cross-name volume comparison shift by 10× on split names only |
| **Share-count-derived values** | 24.578B vs 2.458B shares — anything per-share built off `historical-market-capitalization` is wrong by the factor |
| **Golden/characterization tests** | `tests/test_ohlcv_features_golden.py` freezes feature output. If its fixture is a live pull, a future split reddens it for reasons unrelated to the code; if frozen, it drifts from production. Both are bad, and the split is the trigger |

### The fix is available, and it is the pattern §6 already uses

FMP serves **both** halves: the raw series (`non-split-adjusted`) and the split events (`splits`).
That is exactly the Fact-ledger shape — immutable observations plus the events that transform them
— applied to prices instead of filings.

| ID | Rule |
|---|---|
| **DE-27** | The price store keeps the **raw** series (`historical-price-eod/non-split-adjusted`) as the system of record, plus the `splits` and `dividends` event series. The adjusted panel is **derived**, never ingested as though it were primary |
| **DE-28** | Adjustment is applied **at an `as_of`**: only split and dividend events with `date <= as_of` contribute a factor. A backtest as of 2024-06-01 therefore sees $1,150, and re-running it next year still sees $1,150 — which is what constitution INV-2 requires |
| **DE-29** | Any feature that is **not scale-invariant** — absolute price or volume thresholds, share counts, penny-stock screening (M-1) — is computed on the **raw** series at its as-of, never on the adjusted panel |
| **DE-30** | A price panel artifact records **which adjustment as-of produced it**. Two panels covering the same dates with different `adj_as_of` are different data and must not compare equal |

> **This closes QD-2**, and it closes it in the opposite direction from the 2026-08-15 reading.
> It also generalises: `dividends.adjDividend` is retro-adjusted by the same machinery (QD-13), so
> the same as-of rule applies to it.

## 5C.6 What was checked and found clean

Stated so the absence of a finding is not mistaken for absence of a check:

- **MU's quarterly series is discrete, not cumulative.** `income-statement.revenue` and
  `earnings.revenueActual` agree to **1.0000 on all 12 quarters**, and FY2024 and FY2025 quarterly
  sums equal their annual figures **exactly**. The `_cumulative_fys` defect class is not present in
  the FMP quarterly path for this filer.
- ~~**`full` and `non-split-adjusted` prices are identical to 4dp**~~ — **retracted 2026-08-16.**
  True for MSFT, MU and ARM, and true only because **none of them split in the window**. NVDA shows
  a 10× divergence. See §5C.7. *Kept as a tombstone because the reasoning error is the lesson: three
  names agreeing proved nothing when all three lacked the event being tested for.*
- **No `10-K/A` or `10-Q/A`** for any of the three in 2024–2026. The amendments present are
  `8-K/A`, `4/A`, `3/A`, `SC 13G/A`. No annual restatement to test against in this sample.

---

# 6. POINT-IN-TIME — the domain's reason to exist

## 6.1 What it guarantees

```text
╔══════════════════════════════════════════════════════════════════╗
║  A POINT-IN-TIME QUERY RETURNS WHAT WAS KNOWABLE, NOT WHAT IS    ║
║  TRUE.                                                           ║
║                                                                  ║
║  as_of(2024-03-01) returns the numbers a person could have       ║
║  read on 2024-03-01 — including the ones later restated.         ║
║  It does NOT return today's corrected figures.                   ║
║                                                                  ║
║  Returning corrected figures is look-ahead (constitution        ║
║  INV-1). It makes                                                ║
║  every backtest optimistic and every parity check pass while     ║
║  training on information inference will never have.              ║
╚══════════════════════════════════════════════════════════════════╝
```

## 6.2 The four fields that make it work

Every Fact carries these, and a Fact missing any of them is rejected:

| Field | Meaning | Without it |
|---|---|---|
| `accession_id` | which filing said this | restatements are indistinguishable |
| `filing_date` | when it became public | **the as-of filter is impossible** |
| `period_end` (+ `period_start`) | what span it describes | cumulative-vs-discrete is a guess (§5) |
| `ingested_at` | when *we* learned it | our own latency is invisible |

`filing_date` is the axis the as-of filter runs on. `ingested_at` is separate and also required:
the gap between them is our own staleness, and conflating the two hides it.

## 6.3 Resolution

```text
as_of(ticker, D) →
  1. Load all Facts for ticker with filing_date <= D          ← the whole guarantee
  2. Group by (tag, period_end, period_type)
  3. Within each group take the fact from the LATEST filing_date
     (a restatement published on or before D was knowable on D)
  4. Assemble canonical FundamentalRows
  5. Attach provenance: accession_id + filing_date per field
```

Step 3 is the subtle one. "Knowable on D" is not "the first thing filed" — if a restatement landed
before D, it *was* knowable. The filter is on publication, not on originality.

## 6.4 Rules

| ID | Rule |
|---|---|
| **DE-6.1** | Every query that feeds training, backtest or inference is point-in-time. There is **no non-PIT read path** for those consumers — not a flag, not a default, not a fast path |
| **DE-6.2** | The Fact ledger is **append-only**. A restatement appends; it never overwrites. Deleting a Fact destroys the ability to reproduce a past decision (AP-6) |
| **DE-6.3** | A Fact with no `filing_date` is **rejected at ingest**. It cannot be placed in time, so it can never be safely served |
| **DE-6.4** | `as_of` is **required**, never defaulted to today. A defaulted as_of is look-ahead with a convenient signature |
| **DE-6.5** | Restatements are **surfaced, not smoothed**. A consumer asking for a period that has been restated can see that it was |
| **DE-6.6** | PIT resolution is **deterministic** (constitution INV-2): same ledger + same `as_of` ⇒ byte-identical output |

> **DE-6.4 is the rule most likely to be eroded.** `as_of=None → today` is convenient at every call
> site and silently correct in production, where today *is* the as-of. It is silently **wrong** in
> every backtest and every training run, and the failure is invisible: the numbers look right, the
> model looks good, and the skill does not survive contact with live data.

---

# 6A. THE PRE-RUN CALENDAR CHECK — a corporate-action gate

> **Sits here, immediately after §6, on purpose.** §6 guarantees *what a number was* at a date.
> This section guarantees that the consumer is told *what happened to that number's meaning* inside
> its window. They are different guarantees and the second is not implied by the first.

## 6A.1 Why a gate rather than a report

Point-in-time resolution is necessary and not sufficient. Every value §6 serves can be perfectly
as-of correct while the **series it belongs to** was silently redefined mid-window:

- a **split** rescales every price and volume before it (§5C.7);
- a **restatement** replaces a period's numbers with different ones (§5C.2), and on the FMP side
  leaves no trace at all;
- a **dividend** changes the adjusted series and the realised return;
- an **8-K, an M&A announcement or a 13D** changes what the fundamental story even is;
- a **delisting** removes a name that the panel still contains (constitution INV-017).

A model trained across such a window is not wrong at any single point. It is trained on a series
whose units changed partway through, and nothing in the data says so.

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-07 MUST ENUMERATE CORPORATE ACTIONS FOR THE WHOLE UNIVERSE    ║
║  BEFORE ANY TRAINING, BACKTEST OR INFERENCE RUN BEGINS —         ║
║  AND HALT THE RUN ON AN UNHANDLED ONE.                           ║
║                                                                  ║
║  Not per ticker, on demand, when someone remembers.              ║
║  Not as a report nobody reads.                                   ║
║  A precondition, checked once, that can stop the run.            ║
║                                                                  ║
║  This is the same shape as F1 AC-1.15's feature-coverage gate:   ║
║  measure it, name the tickers, refuse rather than proceed        ║
║  silently. D-17 is what happens without it.                      ║
╚══════════════════════════════════════════════════════════════════╝
```

## 6A.2 What it enumerates

Per **(ticker × window × as_of)**, for every name in the **universe** — not the watchlist (DE-36).

| # | Event class | Source (§5A.1) | Knowability date | Severity |
|---|---|---|---|---|
| 1 | **Price-adjustment state** | derived: `splits` + `dividends` in effect at `as_of` | — | **BLOCK** if the window's `adj_as_of` differs from the run's (DE-28/DE-30) |
| 2 | **Stock split** | `splits` (`numerator`/`denominator`) | 8-K announcement; `date` is *effective* | **BLOCK** |
| 3 | **Reverse split** | `splits`, `denominator > numerator` | as above | **BLOCK** — also an M-1 penny-stock screening hazard (§5C.7) |
| 4 | **Restatement — amended filing** | `sec-filings-search/symbol`, `formType` contains `/A` | `acceptedDate` | **BLOCK** if it amends a period inside the window |
| 5 | **Restatement — silent value change** | our own diff across dated ingests (DE-24) | ingest date | **BLOCK** |
| 6 | **Delisting** | `delisted-companies` | `delistedDate` | **BLOCK** — survivorship, INV-017 |
| 7 | **Fundamental filing landing mid-window** | statements' `acceptedDate` (§5C.1) | `acceptedDate` | **FLAG** — what was knowable changes inside the window |
| 8 | **Dividend — declared / ex / paid** | `dividends` | **`declarationDate`** | **FLAG** |
| 9 | **Earnings reported** | `earnings` | report date | **FLAG** |
| 10 | **Earnings scheduled inside window** | `earnings-calendar` | *(none — 34.6% forward-dated, §5A.4b)* | **FLAG**, and **UNCHECKED** unless snapshotted (QD-11) |
| 11 | **Material event (8-K)** | `sec-filings-search/form-type=8-K` | `acceptedDate` | **FLAG** |
| 12 | **M&A announcement** | `mergers-acquisitions-latest` | `acceptedDate` | **FLAG** |
| 13 | **5%+ stake (SC 13D/G)** | `acquisition-of-beneficial-ownership` | `filingDate` | **FLAG** |
| 14 | **Analyst rating / target action** | `grades`, `price-target-news` | `publishedDate` | **NOTE** — sentiment-affecting |
| 15 | **Notable news** | `news/stock` | `publishedDate` | **NOTE** — and **UNCHECKED beyond ~92 days** (§5C.4) |
| 16 | **Macro release** | `economic-calendar` | release date | **NOTE** — universe-wide, not per ticker |
| 17 | **Index / ETF membership change** | *(no source)* | — | **UNCHECKED, permanently** — record the gap |
| 18 | **Ticker change** | derived: diff of dated **SEC `company_tickers.json`** snapshots on **CIK** | the snapshot date the new symbol first appears | **BLOCK** — §6B |

**Severity is a run-gate axis, distinct from DE-12's ACCEPT/FLAG/REJECT**, which classifies
individual rows. A row can be perfectly valid and still sit inside a window this gate blocks.

| Severity | Effect |
|---|---|
| **BLOCK** | the run **halts** unless the event is explicitly handled and the handling is recorded |
| **FLAG** | the run proceeds; the event is attached to the run record and surfaced in the artifact |
| **NOTE** | recorded for context; no effect on the run |
| **UNCHECKED** | **the class could not be evaluated.** Never reported as "no events" |

## 6A.3 Rules

| ID | Rule |
|---|---|
| **DE-31** | Every training, backtest and inference run calls the calendar check for the **entire universe over its full window, before the first feature is built.** Not per-ticker, not lazily, not on the actionable subset |
| **DE-32** | An unhandled **BLOCK** halts the run and **names the tickers and the events** (P5). A blocking ticker is never silently dropped — dropping is the D-17 defect, where 7 of 13 watchlist names were scored on NaNs and nothing said so |
| **DE-33** | The check's output is **persisted with the run record** (D-08) and referenced by every artifact the run produces (AP-6). A past recommendation's corporate-action context must be reconstructable |
| **DE-34** | The check is itself **point-in-time**: it enumerates what was knowable at `as_of`, keyed on **knowability dates, not event dates** (DE-18). A split announced after `as_of` is not in the report even though it is in today's `splits` response |
| **DE-35** | **An event class that cannot be sourced is reported `UNCHECKED`, never as "no events found."** Absence of evidence and evidence of absence are different results, and conflating them is how a false assumption becomes a silent one. News older than ~92 days is `UNCHECKED`; index membership is `UNCHECKED` permanently |
| **DE-36** | The check covers the **universe**, not the watchlist. A name excluded from the actionable slate still participates in cross-sectional normalisation, so its unhandled split contaminates every other name's rank |

> **DE-35 is the rule this section exists for.** Every other rule here fails safe by halting.
> DE-35 fails safe by *admitting ignorance* — and it is the one an implementation will be tempted
> to skip, because an empty list is so much easier to return than a tri-state.

## 6A.4 The check must be verified against live FMP — not against a fixture

A calendar check built and tested only against recorded fixtures is a machine for confirming its
author's assumptions. Every wrong belief in this spec's history was of exactly that shape: the
`_cumulative_fys` docstring asserted the wrong rule and had a passing test built on real production
numbers; the 2026-08-15 split conclusion was drawn from three names that could not have shown the
effect (§5C.6). **Fixtures freeze what we already believe.**

F3 §4a **Tier 1 — reality probe** is the answer this repository already has: *"run the real code
path on a real ticker and compare against a source outside this repository."*

| ID | Rule |
|---|---|
| **DE-37** | The calendar check carries a **live reality probe** (F3 Tier 1, recording CT-3.2) that **fetches from FMP over the network and digests the response through the real code path** — not a fixture, not a mock, not a recorded cassette |
| **DE-38** | The probe asserts against a **known-answer set** of events established independently of this system (§6A.5). A probe that only checks "something came back" verifies nothing |
| **DE-39** | The probe compares **every intermediate**, not just the final report — CT-3.2's requirement, and the lesson of FMP's TTM being wrong while the DCF still produced a plausible number |
| **DE-40** | The probe is **separately invocable** (network, API key, rate limit) and **its skip is loud**. A live probe that silently skips when `FMP_API_KEY` is unset is worse than no probe: it reports green while verifying nothing. Skipped ⇒ reported as skipped, in the run summary |
| **DE-41** | The probe **re-runs on a schedule**, not once. Endpoint shapes, plan gates and field names all drift (§5A.2 documents three kinds of drift in one day). This is F3 **Q1** — its cadence is that question's answer, and this is a second caller for it |

## 6A.5 The known-answer set

Facts established outside this repository, each verifiable from the retained dump (DE-17) *and*
from primary sources. A probe asserts against these; when a probe and this table disagree, F3 §4c
applies — **neither is assumed right until it is established which is wrong.**

| # | Known answer | Established by | Probes |
|---|---|---|---|
| K-1 | **NVDA split 10:1 effective 2024-06-10** (also 4:1 2021-07-20, 3:2 2007-09-11, 2:1 2006-04-07) | `splits` + SEC 8-K | split detection, adjustment factors |
| K-2 | NVDA `full` close 2024-06-07 = **120.89**; `non-split-adjusted` = **1208.90**; ratio exactly 10 | dump, §5C.7 | which series is raw; `adj_as_of` derivation |
| K-3 | NVDA volume 2024-06-07: raw **41,238,600**, `full` **412,386,000** | dump | volume is adjusted in the opposite direction |
| K-4 | **MSFT declares dividends a median ~72 days before ex-date**; `declarationDate` populated on 90/90 rows | dump | knowability keyed on declaration, not ex-date |
| K-5 | **ARM files 20-F and 6-K; no 10-K, no 10-Q** | `sec-filings-search`, EDGAR | source routing (§5.1 case B) |
| K-6 | **MU statement filing lag: min 20, median 28, max 57 days** after period end | dump, §5C.1 | mid-window filing detection (class 7) |
| K-7 | MSFT amendments present in 2024–2026: `8-K/A`, `4/A`, `3/A`, `SC 13G/A`; **no `10-K/A`** | `sec-filings-search` | restatement detection must find these and not invent others |
| K-8 | **`news/stock` returns ~92 days regardless of paging** | dump, §5C.4 | that news reports `UNCHECKED` beyond the window (DE-35) |
| K-9 | **408 of 437 MSFT filings accepted at/after 16:00 ET** | dump, §5C.5 | next-session knowability |
| K-10 | MU quarterly revenue is **discrete**: FY2024 and FY2025 quarters sum exactly to annual, and `income-statement` agrees with `earnings.revenueActual` to 1.0000 | dump, §5A.3a | the `_cumulative_fys` class stays absent |

> **K-2 and K-8 are the two most valuable rows**, because each contradicts something this spec
> previously asserted. A known-answer set earns its keep by containing the cases that already
> caught us out.

## 6A.6 Open, deliberately

- **What "handled" means for a BLOCK.** Re-deriving the adjusted panel at the run's `adj_as_of`
  handles a split. Nothing yet says what handles a restatement — QD-15.
- **Cost.** 130 tickers × 8 sourced classes is ~1,000 calls per run against a 300/min cap. It
  almost certainly needs its own cached, incrementally-updated store rather than a live sweep per
  run — QD-16.

---

# 6B. IDENTITY — a ticker is a label, not an instrument

> **Sits after §6A on purpose.** §6A asks *what happened to this name inside the window*. This
> section asks the prior question: **is this the same name at all?**

## 6B.1 The problem, measured

`BK` stopped printing on 2026-06-29 and `SATS` on 2026-08-24. Neither was delisted. **Bank of New
York Mellon rebranded `BK` → `BNY`; EchoStar rebranded `SATS` → `ECHO`, and both still trade.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  FROM THE PRICE FEED ALONE, A RENAME AND A DELISTING ARE          ║
║  INDISTINGUISHABLE.  Bars stop.  Nothing says why.               ║
║                                                                  ║
║  ⚠ And the silence length is NO guide: SATS was 3 days stale     ║
║  and HOLX was 5 months — and the 3-DAY ONE WAS THE RENAME.       ║
╚══════════════════════════════════════════════════════════════════╝
```

★★ **The deeper hazard is reuse.** A retired ticker is reassigned to an unrelated company: `S` was
**Sears Roebuck**, became **Sprint** in 2005, and is **SentinelOne** since 2021. A ticker-keyed join
over a long history silently welds three different companies into one series — and every statistic
computed on it is meaningless in a way no range check detects. (The TSX embargoes reuse for 53
weeks; there is no general guarantee.)

★ This is a solved problem outside this repo: CRSP assigns **PERMNO**, a permanent number that
survives ticker, name, CUSIP and exchange changes. What follows is the same idea built from a
source we already fetch.

## 6B.2 The anchor — CIK, and why it is the right one here

| Candidate | Verdict |
|---|---|
| **CIK** (SEC) | ★ **chosen** — permanent per registrant, free, and `load_cik_map()` already holds one for all 510 names |
| CUSIP / ISIN | never reused, but **not free** and not in any source this repo has |
| OpenFIGI | free and good, but a **new vendor dependency** for a problem CIK already solves |
| ticker | ⚠ **not an identity** — this whole section is why |

⚠ **The one limitation, stated rather than discovered later:** a CIK identifies a *registrant*, not
a *security*. `GOOG` and `GOOGL` share one CIK, as do `BRK.A`/`BRK.B`. CIK is CRSP's **PERMCO**, not
its **PERMNO**. For a book that holds one share class per company this is sufficient; a universe
containing both classes of one issuer needs `(cik, ticker_class)` and **this spec does not yet
provide it** (QD-17).

## 6B.3 Detection — a snapshot diff, and it costs nothing

SEC publishes `company_tickers.json` as a **current-state** file. Dated snapshots of it, diffed on
CIK, yield the change history:

```text
  stored snapshot           SEC today
  BK   -> 0001390777   vs   BNY  -> 1390777     ⇒ ticker_change  BK  → BNY
  SATS -> 0001415404   vs   ECHO -> 1415404     ⇒ ticker_change  SATS → ECHO
```

★ **Verified against this repo's own `config/sp500_tickers.yaml` on 2026-08-28** — the stored
universe still held both retired symbols, and the diff recovered both renames exactly, with **no
vendor call and no web search**.

⚠⚠ **A CIK that DISAPPEARS from the file is not a delisting.** Measured the same day: `AVB` is
delisted at FMP (2026-08-17) and **still present in SEC's ticker file**. The SEC file lags
deregistration. A vanished CIK is a *candidate* that triggers investigation
(`.claude/skills/ticker-went-silent/`), never a conclusion.

## 6B.4 Retrieval — which symbol to ask for

Measured against FMP on 2026-08-28, over `2026-01-01 … 2026-08-27`:

| Symbol | Bars | Range |
|---|---|---|
| `BNY` (current) | **164** | 2026-01-02 … 2026-08-27 ★ **complete, including the `BK` period** |
| `BK` (retired) | 122 | 2026-01-02 … **2026-06-29** ⚠ truncated at the changeover |
| `ECHO` (current) | **164** | 2026-01-02 … 2026-08-27 |
| `SATS` (retired) | 161 | 2026-01-02 … 2026-08-24 |

★ **FMP re-keys history forward onto the current symbol.** So the rule is simple: **fetch under the
current symbol and take the whole series from it.** The retired symbol is not *wrong*, it is a
truncated prefix — and a universe still holding it silently loses the name to staleness.

## 6B.5 ⚠⚠ Never splice — the finding that decides the algorithm

The obvious implementation is to fetch the old symbol for the old period and the new for the new,
and concatenate. **Measured, that is wrong:**

```text
  BK vs BNY   : 122 overlapping bars, 21 DISAGREE
      2026-04-24   BK volume 2 790 284   BNY volume 2 790 283
  SATS vs ECHO: 161 overlapping bars, 138 DISAGREE
      2026-01-02   SATS volume 3 856 093  ECHO volume 3 856 100  (rounded to hundreds)

  ★ OHLC PRICES AGREE EXACTLY.  ONLY VOLUME DIFFERS.
```

⚠ **Volume is not decorative here**: `volume.split_adjusted_zscore.v1` is one of the 14 price
features. A spliced series carries a **volume discontinuity at the changeover date** — a step in a
z-scored feature that looks like a real liquidity event and is an artefact of the join.

★ One symbol, one series. And **which symbol the panel was fetched under is recorded**, for the same
reason `adj_as_of` is recorded (DE-30): two panels over identical dates fetched under different
symbols are **different data**.

## 6B.6 Rules

| ID | Rule |
|---|---|
| **DE-61** | ★★ **A ticker is a label with a validity interval, never an identity.** Every stored series, fact and past decision is anchored to a **CIK**, and joins across time are on the anchor. ⚠ *`S` was Sears, then Sprint (2005), then SentinelOne (2021)* — a ticker-keyed join welds unrelated companies into one series, and no range check detects it |
| **DE-62** | ★ **Ticker changes are detected by diffing dated SEC `company_tickers.json` snapshots on CIK**: same CIK + different ticker ⇒ `ticker_change`. ⚠⚠ **A CIK that disappears is NOT a delisting** — `AVB` was delisted at FMP and still present in SEC's file the same day. It is a candidate for investigation, never a conclusion (DE-35's distinction) |
| **DE-63** | ★ **OHLCV is fetched under the CURRENT symbol**, and the symbol used is **recorded with the panel**. Measured: the current symbol carries the complete history; the retired one truncates at the changeover, and a universe still holding it loses the name to staleness while `universe_n` still counts it |
| **DE-64** | ⚠⚠ **A series is NEVER spliced across a rename.** Measured: OHLC agree exactly and **volume does not** (`BK` 2 790 284 vs `BNY` 2 790 283). A splice injects a volume step at the changeover into `volume.split_adjusted_zscore.v1` that reads as a liquidity event and is an artefact |
| **DE-65** | ★ **The symbol map is point-in-time.** `resolve(ticker, as_of)` returns the instrument that held the ticker **then**, not the one holding it now. ⚠ Using today's map to answer a historical question is **look-ahead in the identity layer** (INV-1) — and with reuse it is not merely stale, it is a different company |
| **DE-66** | `ticker_change` is **BLOCK**. ★ It clears only on an explicit recorded handling — *the panel was fetched under the resolved current symbol* — never by severity downgrade (QD-15). ⚠ A run whose universe still names a retired symbol is silently short a name, and the guard that catches it (QA-125) reports *"stopped printing"*, which is true of a rename and explains nothing |
| **DE-67** | ★★ **A knowable `ticker_change` SUPERSEDES a vendor `delisting` for the same ticker.** The registrant's own filing index is the authority on *identity*; the `delisted-companies` feed infers it from a symbol going dark and **cannot tell a rebrand from an exit**. ⚠ *Measured 2026-08-28:* FMP called `EQR` a delisting on 2026-08-18 while SEC showed CIK `0000906107` listing **`VMRK`**, which priced **41 bars through 2026-08-27** — barring it would have dropped a live S&P 500 name. ★ Same precedence shape as EDGAR-over-FMP for TTM: the source carrying the *explicit* fact beats the one inferring it. ⚠⚠ **The delisting is never deleted** — the ledger is append-only, so it is *superseded*: the row stays, and the name is **not** thereby silently fine, because its `ticker_change` is a **BLOCK** that still demands the explicit handling DE-66 requires. ★ Suppressing the bar without leaving the BLOCK standing would be a severity downgrade (QD-15). ⚠ **The converse does NOT hold**: a delisting with no `ticker_change` stands — `AVB` keeps its own ticker at SEC and remains barred (DE-62, RC-54) |
| **DE-68** | ⚠⚠ **A `ticker_change` derived from a CIK diff does NOT establish WHY, and a rebrand and a *merger of equals* are the same shape in SEC's file.** ★ *Established by search 2026-08-28 (Victor):* `EQR`→`VMRK` is not a rebrand — **Equity Residential and AvalonBay combined**, `EQR`'s CIK survived, and **`AVB`'s side is retired and is NOT in the diff at all**. ⚠ So the detector sees *one* event where *two* names left the universe, and the retired partner is **invisible to it by construction**. ⚠⚠ Worse than invisible — *measured:* the vendor **back-fills the retired symbol with the successor's prices** (`AVB` 2026-08-17 = 65.90 its own, 2026-08-18 = 64.03 = `EQR` = `VMRK`), so a dead ticker keeps printing and carries **a fabricated return on the changeover date** that no range check detects — DE-61's welding hazard arriving through a symbol nobody retired. ★ **The cause must come from a search** (skill `ticker-went-silent`), never from the diff, and a combination is recorded as **two** findings: a `ticker_change` for the survivor and a `delisting` for the retired side |
| **DE-69** | ★★ **Class 4 is sourced from EDGAR, and the `/A` suffix is NOT the test.** ⚠⚠ *Measured 2026-08-28:* FMP's filing index returns **ZERO `10-K/A` across all filers** in 2024, 2025 H1 and 2026 YTD, while `10-Q/A` fills a 100-row page over the same windows; a 2 683-filing scan of five mega-caps found not one. **EDGAR holds five for TSLA alone**, and the live sweep found **48** across the S&P 500 — every one of which the declared source would have missed **silently, on a BLOCK class**. ★ The same precedence as TTM: *EDGAR wins where FMP omits.* ⚠⚠ And `formType ~ /A` was the wrong **test** as well — it matches `SC 13G/A`, `4/A`, `13F-HR/A` (**63 for AAPL alone**), ownership amendments that restate no financial statements. ★ An explicit **whitelist** of financial-statement forms, plus **8-K item 4.02** (*non-reliance*), which is the **announcement** and lands weeks before the amendment — FMP exposes no item numbers at all |
| **DE-70** | ⚠⚠ **`earnings-calendar` truncates SILENTLY at 4 000 rows, keeping the LATEST — and reaches exactly ONE YEAR back.** *Measured 2026-08-28:* asking `2026-01-01..2026-12-31` returns `2026-11-05..` and says nothing; `2026-08-01..2026-09-30` returns `2026-08-13..`. ⚠ The horizon is sharp — a window opening **2025-08-29 answers, 2025-08-27 is 402** — so the reachable history is a **rolling 365 days**, not the range requested. ★ So the sweep **chunks by week and treats a response AT the cap as truncated**, halving until it fits; an uncovered chunk records **no refresh** and names its cause — `capped` and `refused` are different problems with different fixes. ⚠⚠ **Consequence for INV-017**: `earnings_reported` cannot backfill a multi-year backtest window from this source, exactly as `delisted-companies` cannot (DE-60) |
| **DE-71** | ★★ **The two earnings classes have DIFFERENT knowability axes, and conflating them is look-ahead.** `earnings_reported` is knowable **on its announcement date** — *measured:* the feed's `date` is the announcement (Apple's rows fall in late Jan/Apr/Jul/Oct, not on period ends). ⚠ `earnings_scheduled` is a **future** event whose only knowable fact is *that we saw this schedule today*, so `knowable_at = as_of`. ⚠⚠ **A scheduled date MOVES**, and this feed keeps no history of what it once said — so today's calendar cannot answer *"what was scheduled as of 2024-03-01"*; that is DE-65's look-ahead in the calendar layer, and every scheduled finding carries the caveat. ⚠ `lastUpdated` is **never** the axis (DE-23): *measured*, **17 of AAPL's 20 quarters share one stamp** |
| **DE-74** | ★ **A long `ingest` command shows it is alive.** Every few seconds it prints the elapsed time and the stage it is in, to stderr, as whole lines (never a redrawn line that stage output could garble); each stage reports its own duration when it ends, and the command its total (`src/shared/progress.py` — shared with D-04's training run, MT-53). ⚠ *Added 2026-10-07 (Victor):* `ingest events --years 10` runs a long time in silence, indistinguishable from a hung process |
| **DE-75** | ★★ **`get_fundamentals_history(ticker, as_of)` — the ledger as it stood at each filing date.** One `(filing_date, CT-7.2 rows as of that date)` pair per distinct filing date ≤ `as_of`, ascending; each element equals `get_fundamentals(ticker, as_of=filing_date)`. ⚠ *Added 2026-10-07 (`DX-159`, Victor):* a multi-year consumer that reads `get_fundamentals` once at today gets each period dated at its **latest re-filing** — a 10-K re-files two years of comparatives — and its panel runs ~1 year stale (13 % of points PIT-correct, median 371 d). One ledger read per ticker, not one per date |
| **DE-76** | ★★ **`restatement_amended` is handled when — and only when — the caller derives its fundamentals point-in-time per filing date** (QD-15, Victor 2026-10-07: *"PIT store"*). Recorded handling: *"fundamentals as filed before the amendment, amended after (DE-75)"*. ⚠ It is **opt-in by the caller** (`check_window(..., fundamentals_pit=True)`): a caller that reads once and joins across dates would see amended figures dated at the amendment and nothing for the gap — not "handled". The daily run does not opt in yet and still HALTs on one (follow-up) |
| **DE-77** | ★ **`load_sector_map()` — `{TICKER: GICS sector}` from `config/sp500_tickers.yaml::sector_map`, the ONE sector source for every cross-sectional consumer** (training and the daily run read the same map, so a model never sees one classification in training and another in production). ⚠ *Declared limitation:* it is **today's** GICS classification (retrieved 2026-06-21) applied to the whole window — the 2018 GICS reshuffle (Communication Services) is not reflected, the same kind of declaration as the universe being today's index. ⚠ A name absent from the map is absent from the result, never defaulted. *Added 2026-10-07 (`DX-160`, Victor: supply the sector map)* |
| **DE-78** | ★★★ **`price_events(store, tickers, adj_as_of)` — the event store's splits, reverse splits and dividends as `CorporateEvent`s: the ONE source of the price adjustment for every panel builder** (training and the daily run). Every event with `event_date ≤ adj_as_of` for the asked names; `reverse_split` is a split whose ratio is below one. ⚠ *Added 2026-10-08 (`DX-166`, Victor):* both builders called `build_price_panel(raw, (), adj_as_of)` on FMP's RAW series — **no split was ever applied**. Measured: NVDA's 10:1 split gave 21 training labels below −50 % (min −89.5 %); 133 splits/reverse splits across 101 names sat unapplied in the window; and §6A recorded those splits as *handled — "panel derived at adj_as_of"* — a handling that was not performed. ★ With the events passed, that handling string becomes true by construction: the gate and the panel read one store |
| **DE-79** | ★★ **`price_event_conflicts(raw, events, adj_as_of)` names every ticker whose stored events CONTRADICT its own raw prices** — a dividend at or above the prior close (a factor ≤ 0, impossible), or a dividend inside the window with no prior close — with the event and the numbers. A consumer refuses those NAMES for the run, by name; it never adjusts them with a guessed factor and never drops the event to make the series fit. ⚠ *Found 2026-10-08 running DE-78 over all 510 names:* FMP restates KDP's pre-merger history in post-merger units (≈ $19.91 on 2018-07-09) but records the 2018-07-10 special dividend in pre-merger units ($103.75): `1 − 103.75/19.91 < 0`. DE-43's guard refused the WHOLE panel without naming the ticker |
| **DE-80** | ★ **A universe price fetch makes ONE retry pass, after a pause, over the names that failed** (`fetch_universe`, D-04's `fetch_prices`). A name that fails twice is still NAMED (DE-13) — the retry changes how often a transient answer costs a name, never whether a failure is reported. ⚠ *Added 2026-10-09 (`DX-168`, Victor):* the first shadow snapshot lost AAPL, ACGL, ADM, ADP, ADSK, AKAM, AON, AOS, APD to empty responses at the start of the burst — re-fetched minutes later, complete (fmp-api trap 4: transient under burst) |
| **DE-81** | ★★ **A refresh record is MERGED, never blindly overwritten — the merged record claims only what is true for EVERY name in it.** New ⊇ existing names AND starts no later ⇒ replace. New ⊆ existing names ⇒ the existing record stands (the subset refresh adds no new claim). Otherwise ⇒ union of names over the INTERSECTION of the windows, stamped with the OLDER refresh time. An existing record with no ticker coverage (legacy, unverifiable) is replaced. ⚠ *Added 2026-10-09 (`DX-167`, Victor):* `record_refresh` replaced the class's entry with the requested names and window, so a smoke run (`train --limit 20 --refresh-events`) left `split` covering 20 names and the next full run read 490 unfetched ⇒ UNCHECKED |
| **DE-73** | ★ **`ingest status` reads ONE declared map of which command sweeps which class** (`SWEPT_BY`), composed from the ingest modules' own class constants. ⚠ *Added 2026-10-06 (`DX-157`, Victor):* status decided *"built or not"* from `events.SOURCED` — four classes — so eleven classes the `events` sweep records were labelled *"no ingest built"*. A class that is sourceable and never swept now says **which command sweeps it**; *"no ingest built"* is reserved for a class no command records (DE-35: the two absences are different) |
| **DE-72** | ★★ **Cadence follows SEVERITY, and staleness is measured from the refresh the store RECORDED.** A stale `BLOCK` can let a real split through unhandled; a stale `NOTE` costs a reader context — so `BLOCK` is due after **1 day**, `FLAG` **7**, `NOTE` **30**, and one interval for all three would either hammer the rate limit for news or leave splits unchecked for a week. ⚠ Measuring from *when the sweep was invoked* would let a sweep that covered nothing reset the clock — DE-58's rule applied to time instead of to names. ⚠⚠ **Three states, not two**: *never refreshed* and *stale* need different fixes and are counted apart, and a class that is `permanently_unchecked` or **derived at check time** is **exempt** — reporting `index_membership` as overdue daily would train a reader to ignore the whole report (DE-35) |

---

# 7. CONTRACTS

## CT-7.1 — Price panel (parquet)

| Column | Type | Note |
|---|---|---|
| `ticker` | string | uppercase |
| `date` | date32 | trading day |
| `open_minor`…`close_minor` | int64 | `Money` minor units (CT-M.1) |
| `*_currency` | string | required sibling of every `*_minor` |
| `volume` | int64 | shares — ★ **always RAW, in both panel modes.** There is no `adj_volume`: DE-29 puts absolute and cross-sectional volume on the raw series, and **dollar volume is therefore `close_minor × volume` (raw × raw), never `adj_close × volume`**, which would be wrong by the split factor |
| `adj_close_minor` | int64 | split/dividend adjusted |
| ★ `adj_open_minor` | int64 | **required** — `open × adj_factor`. See **DE-42** |
| ★ `adj_factor` | float64 | the **cumulative split·dividend factor in effect at `adj_as_of`**, materialised so the adjustment is auditable rather than inferred. See **DE-42** |
| ★ `adj_as_of` | date32 | **required when `is_adjusted`, null when raw** — which adjustment produced this panel (**DE-30**, AC-7.46, D-02 **FE-8**) |
| `is_adjusted` | bool | explicit, never inferred |
| `source` | string | `"fmp"` |
| `fetched_at` | timestamp[us, UTC] | |

Constraints: `date` monotonic per ticker · no future dates · no null `close_minor` ·
`high >= low` · `low <= open, close <= high`. *(Inherits constitution DC-1.)*

> ★ **`adj_open_minor` added 2026-08-18 by cross-spec audit.** D-03 **QA-84**, D-03 §5.9.1d and
> `L3-build-sequence.md` **BS-8** all assign its production to D-07 — and **`adj_open` appeared
> nowhere in this spec.** The open-anchored label (**QA-71**) was blocked on a column no contract
> declared and no domain had been told to build.

| ID | Rule |
|---|---|
| **DE-42** | ★ **`adj_factor` is a property of the DATE, not of the field, and every adjusted field is `raw × adj_factor`** — `adj_open_minor = open_minor × adj_factor`, `adj_close_minor = close_minor × adj_factor`. It is **materialised** once per `(ticker, date, adj_as_of)`, never recomputed per consumer — a factor derived independently at four call sites is four chances to derive it differently. ⚠ **Amended 2026-08-23: the factor is computed from the `splits` and `dividends` events with `date <= adj_as_of` (DE-28), NOT from the ratio `adj_close/close`.** That original wording was **circular under DE-27** — the raw series is the system of record, so `adj_close` is an *output* of the factor and cannot also be its input |
| **DE-43** | ★ **The adjustment is asserted consistent across fields**: `adj_close/close == adj_open/open` for every `(ticker, date)`. ⚠ **Against a reconstruction this is a tautology** (D-03 **QA-85**) — so the real check is against the **vendor's** adjusted open where FMP supplies one, and otherwise that `adj_factor` is strictly positive and **changes only on dates the calendar check flags** (§6A) |
| **DE-45** | ★ **`adj_as_of` is a REQUIRED parameter on the price read path, and `None` is its explicit *raw* value** — omitting it raises `DATA.PRICE.ADJ_AS_OF_REQUIRED`, exactly as omitting `as_of` raises on a PIT path (DE-6.4). D-07 additionally exposes a **raw-only guard** raising `DATA.PRICE.RAW_REQUIRED` when a non-scale-invariant consumer (DE-29) is handed a panel whose `is_adjusted` is true. ⚠ **Amended 2026-08-23: §8 read `get_prices(ticker, start, end)` — *"adjusted by default"*, with `adj_as_of` nowhere in the signature.** That contradicted DE-28, left DE-29's raw path unreachable, and made **both** error codes unraisable by any documented call. ★ A default adjustment is DE-6.4's defaulted `as_of` wearing a different name |
| **DE-44** | ⚠ **Cash dividends are checked separately from splits.** For a split the factor is unambiguous; for a dividend it depends on **which side of the ex-date the vendor keys it to** — the ex-date *open* already reflects the drop in the raw price, so a close-derived factor can double-count. **DE-43's monotonicity test passes either convention** (D-03 **QA-91**), so ex-dividend dates get their own assertion |

## CT-7.2 — Fundamental panel (parquet)

| Column | Type | Note |
|---|---|---|
| `ticker` | string | |
| `period_end` · `period_start` | date32 | **both required** — §5.1 |
| `period_type` | string | `annual` \| `quarterly` |
| `<line_item>_minor` + `_currency` | int64 + string | one pair per monetary line item |
| `shares_outstanding` | int64 | not monetary |
| `source` | string | `"edgar"` \| `"fmp"` — DE-5.1 |
| `accession_id` | string | null for FMP rows |
| `filing_date` | date32 | **required** — DE-6.3 |
| `ingested_at` | timestamp[us, UTC] | |
| `quality_flags` | list[string] | FLAG-severity findings; empty when clean |

## CT-7.3 — Fact ledger (parquet, append-only)

`(ticker, accession_id, tag, period_start, period_end, period_type, value_minor, currency, unit, filing_date, ingested_at)`

> ★ **`period_type` added 2026-08-23.** §6.3 step 2 groups Facts by **`(tag, period_end, period_type)`** and CT-7.2 carries it, but this contract never declared it — the PIT resolution algorithm keyed on a field its own ledger did not have. Same seam-defect class as `adj_open`.

The ledger is the system of record. CT-7.2 is **derived** from it at an `as_of` and may be rebuilt
from it at any time. If the two disagree, the ledger is right.

## CT-7.4 — Filing-aware cache (JSON)

Keyed by `accession_id`, not by clock. A filing is immutable once published, so its cache entry
never expires; the cache is invalidated by **a new filing appearing**, not by a TTL. This is why
repeated analysis of an unchanged name is nearly free, and it is inherited from the existing
filing-aware cache (constitution P4).

## CT-7.7 — Calendar check report (JSON, persisted with the run) — §6A

One report per run, referenced by every artifact the run produces (DE-33, AP-6).

```json
{
  "run_id": "...", "report_id": "...",
  "as_of": "2026-08-16", "adj_as_of": "2026-08-16",
  "window": {"start": "2024-01-01", "end": "2026-08-16"},
  "universe_size": 130,
  "verdict": "HALT",
  "class_status": {
    "split": "CHECKED", "restatement_amended": "CHECKED",
    "news": "UNCHECKED:  source depth ~92d < window",
    "index_membership": "UNCHECKED: no source"
  },
  "findings": [
    {"ticker": "NVDA", "class": "split", "severity": "BLOCK",
     "event_date": "2024-06-10", "knowable_at": "2024-05-22",
     "detail": {"numerator": 10, "denominator": 1},
     "source": "fmp:splits", "handled": false, "handling": null}
  ],
  "blocked_tickers": ["NVDA"]
}
```

| Field | Rule |
|---|---|
| ★ `report_id` | **the handle D-02's `CT-2.2.calendar_check_id` refers to** (FE-10). ⚠ *Added 2026-08-23: D-02 stamps every panel with the id of the check that cleared its window, and **CT-7.7 declared no id at all** — the consumer referenced a field the producer never emitted.* Derived from `(run_id, as_of)` so it is reproducible rather than allocated |
| `class_status` | **every one of §6A.2's 17 classes appears**, as `CHECKED` or `UNCHECKED:<reason>`. A class missing from this map is a defect, not an implied pass (DE-35) |
| `knowable_at` | the knowability date, **not** the event date (DE-34) |
| `handled` / `handling` | a BLOCK may only be cleared by an explicit, recorded handling |
| `verdict` | `PROCEED` \| `PROCEED_WITH_FLAGS` \| `HALT` |

## CT-7.6 — Observation ledger (parquet, append-only) — §5A.4

The axis Class-B data does not carry. One row per (ticker, field-set, observation).

| Column | Type | Note |
|---|---|---|
| `ticker` | string | |
| `field_set` | string | `analyst_estimates` \| `price_target_consensus` \| `ratios_ttm` \| … |
| `observed_at` | timestamp[us, UTC] | **when we asked** — the whole point |
| `source_endpoint` | string | the `/stable/` path, verbatim |
| `payload` | struct / JSON | the response, canonicalised |
| `content_hash` | string | dedupe — an unchanged snapshot appends nothing |

Rules, mirroring CT-7.3:

| ID | Rule |
|---|---|
| **DE-6.7** | The observation ledger is **append-only**. A changed consensus appends; it never overwrites |
| **DE-6.8** | `observed_at` is **ours**, never the vendor's. It is the only honest timestamp on Class-B data, and labelling it as anything else would claim a publication date that does not exist |
| **DE-6.9** | A Class-B field may be served to a **training, backtest or inference** consumer **only** through this ledger, at an `as_of`. Serving it live is legal for D-09 display and illegal for D-04 (§5A.4) |
| **DE-6.10** | An unchanged snapshot (same `content_hash`) appends **no row**. The ledger records *changes*, so its size tracks information rather than uptime |

> **DE-6.9 is where this will be argued.** Live consensus is genuinely useful on a report today, and
> the same field is genuinely poison in a training row. Both are true, which is why the rule is
> written per-consumer rather than per-field.

## CT-7.8 — Symbol history (parquet, append-only) — §6B

`.state/symbology/history.parquet` — the point-in-time ticker map.

| Column | Meaning |
|---|---|
| `cik` | ★ the permanent anchor, zero-padded to 10 |
| `ticker` | the symbol, **valid only inside the interval** |
| `valid_from` | first date this CIK was observed under this ticker |
| `valid_to` | last date, or null while current |
| `knowable_at` | ⚠ the **snapshot date** the mapping was observed — DE-65's axis, not `valid_from` |
| `source` | `sec:company_tickers.json` |

⚠ **Append-only** (DE-6.2's argument one layer over): a correction appends a row. Overwriting a
mapping would make a past decision's universe unreconstructable — and *the temptation is highest on
the row that says we fetched the wrong symbol.*

★ The table is **derived and rebuildable** from the dated snapshots, which are themselves kept.

## CT-7.5 — Provenance envelope (JSON)

Every served artifact carries: `source`, `as_of`, `fetched_at`, and — where any value was converted
— the `FxRate` used (`L2-shared-money.md` FX-2).

---

# 8. PUBLIC API SURFACE

Exported from `src/data_engine/__init__.py`. Nothing else is importable from outside (ST-3).

| Method | Returns | Note |
|---|---|---|
| `get_prices(ticker, start, end, adj_as_of)` | `PricePanel` | ★ **`adj_as_of` required; `None` means the RAW series** (DE-45). `is_adjusted` and `adj_as_of` are always stated on the panel (CT-7.1, DE-30) |
| `get_fundamentals(ticker, as_of, period_type)` | `list[FundamentalRow]` | **`as_of` required** (DE-6.4) |
| `get_facts(ticker, as_of)` | `list[Fact]` | raw ledger view, for audit |
| `get_profile(ticker)` | `CompanyProfile \| None` | |
| `get_news(ticker, since)` | `list[NewsItem]` | |
| `get_analyst_actions(ticker, as_of)` | `list[AnalystAction]` | grades + target changes, Class A (§5A) |
| `get_insider_transactions(ticker, as_of)` | `list[InsiderTransaction]` | Form 4, Class A |
| `get_events(ticker, as_of, kinds)` | `list[CorporateEvent]` | dividends · splits · earnings · M&A · delisting |
| `get_calendar(kind, start, end)` | `list[CalendarEntry]` | **forward-looking** — never a training input |
| `get_macro(series, as_of)` | `list[MacroPoint]` | treasury curve, indicators |
| `get_observation(ticker, field_set, as_of)` | `Observation \| None` | **the only Class-B read path for D-04** (DE-6.9) |
| `calendar_check(tickers, start, end, as_of, adj_as_of)` | `CalendarCheckReport` | **§6A. Called before every training/backtest/inference run** (DE-31). Raises on an unhandled BLOCK (DE-32) |
| `get_fx(pair, as_of)` | `FxRate \| None` | **`None` when unavailable** — never a guess (FX-3) |
| `get_universe()` | `list[UniverseEntry]` | |
| ★ `get_day_open(ticker, as_of)` | `DayOpen` | **DE-47** — the settled day-T opening print. ⚠ `settled=False` blocks D-08's run (OR-33); **never the previous close** |
| `freshness(ticker)` | `FreshnessReport` | per data type |

> Every method that can be used for training, backtest or inference takes `as_of` and has **no
> default for it**. Convenience wrappers that supply "today" belong in the caller, where the choice
> is visible.

---

# 9. BUSINESS RULES

| ID | Rule |
|---|---|
| **DE-48** | ★★ **`is_trading_day` lives in D-07, and returns `None` outside its holiday coverage.** ⚠ *Added 2026-08-25 — this is **OR-7's migration**, which QO-1 called the cheapest of §1.5's ten misplaced functions and which never happened; D-08's step 0 asked for it and D-07 had no trading-day predicate at all.* ★ **It is a rebuild, not a port**: the legacy `_is_market_open_et` was **weekday-only with no holiday calendar of any kind** — it returns `True` on Christmas whenever Christmas is a Tuesday — and it answered *"is the market open right now"* when the caller needs *"was this DATE a session"*. ⚠ The holiday set is an **ADMITTED LIST** (CN-10), hand-entered and not fetched, so **outside its covered span the answer is `None`, never `True`** — *no holidays found* and *we did not look* are opposite findings (DE-35), and a silent wrong `True` runs the pipeline against a market that never opened |
| **DE-47** | ★★ **The day-T OPENING PRINT is a distinct read from the day-T BAR, and only the print is settled at 10:00.** ⚠ *Added 2026-08-25 wiring D-08's daily run: **D-08 **OR-32** requires "the settled day-T opening print, obtained as a real OHLC field from D-07" and **CT-7.1 declares no settledness at all**.* ★ **The two settle at different times, and conflating them is the legacy defect verbatim**: the opening auction prints at 09:30 and is final; the *bar* is not final until 16:00, so a daily endpoint polled at 10:00 returns an **in-progress row whose high/low/close are the running price** — which is exactly `open == high == low == close`, the collapsed bar OR-32 names and `main_inference.py:250` produced. ★ `get_day_open` therefore serves the **print**, carrying `settled` explicitly, and **never fabricates the other three fields**. ⚠ **`settled` is false before the auction completes and the run BLOCKS** (OR-33) — it is never backfilled from the previous close. ★★ **MEASURED 2026-08-25 14:42 ET, mid-session, NVDA** (CT-3.2 reality probe, `historical-price-eod/full`): the endpoint returned `open 211.025, high 214.7291, low 210.11, close 212.855` — ⚠ **a plausible, NON-collapsed bar whose `close` is simply the running price, with nothing in the payload saying so.** So **collapse-detection is necessary and NOT sufficient**: the legacy defect was detectable because it wrote one spot quote into five fields, and **the vendor's own in-progress row is not detectable that way at all.** ★ The load-bearing guard is therefore *has the session closed*, which is a **calendar** question D-07 already owns — and the safe read is **the `open` alone, never the other three** |
| **DE-1** | All external access goes through D-07. No other domain holds an API key or a URL |
| **DE-2** | Provider formats are translated to canonical shape **at the client boundary**. No provider field name exists past `src/edgar/` or `src/fmp/` |
| **DE-3** | Money is constructed at the boundary via `Money.from_decimal_str` — or `from_float` where the provider returns JSON floats (FMP), which is permitted and deliberately greppable (QM-2, decided) |
| **DE-4** | Timestamps are UTC at the boundary. Trading *dates* are calendar dates, not timestamps |
| **DE-7** | Tickers are uppercased at the boundary |
| **DE-8** | API keys and the EDGAR User-Agent email never appear in a log, an artifact, or an error message |
| **DE-9** | EDGAR access is throttled in-process and sends a contactable `User-Agent` — SEC requires it, and being blocked is a self-inflicted outage |
| **DE-10** | Writes are atomic: write-temp-then-rename. A partially-written parquet must never be readable (L0 §6.2) |
| **DE-11** | Re-ingestion is idempotent: same inputs ⇒ same files. Overwrite, never append — except CT-7.3, which is append-only by design |
| **DE-12** | Validation classifies **ACCEPT / FLAG / REJECT** and never modifies data. A FLAG is stored with the row; a REJECT is not stored at all, and is logged with its rule id |
| **DE-49** | ★★ **A 402 is a SUBSCRIPTION boundary, not a missing security, and the two need different remedies.** ⚠ *Added 2026-08-26 building the universe assembler.* **DE-13** fails the run when a ticker *"resolves to no source"* and **DE-46** already says a 402 is never read as *"no data"* — but neither says what to DO about one. ★ An absent security is a **universe error to correct**; a plan-gated one is a **DECLARATION problem** — the name does not belong in the universe while the plan does not cover it, and **discovering that at fetch time is discovering it too late**. ⚠ Measured: every `.TO`/`.NE` symbol returns 402 on this plan, so Canadian listings and CDRs cannot be in a universe until the plan changes (D-11 RC-58). ★ **Every failure is collected and reported once** — a 130-name universe with three problems should take one run to diagnose, not three |
| **DE-50** | ★★ **A transport that requests an encoding must be able to decode it — and it decodes what the RESPONSE declares, never what the request asked for.** ⚠ *Found 2026-08-26 on **the first real EDGAR call this project has ever made**.* `EdgarClient._get` sends `Accept-Encoding: gzip, deflate`; `urllib` does **not** decompress transparently; `_UrllibTransport` read `.decode("utf-8")` straight off the wire — so every `companyfacts` fetch died on `0x8b`, **the second byte of the gzip magic number**. ★★ **Nothing caught it because every test injects a fake transport: the one class that talks to the network was the one class with no coverage** — and EDGAR is the *preferred* source for TTM line items, so the preferred path had never once run |
| **DE-51** | ★ **EDGAR reports a fact twice, and only a BYTE-IDENTICAL repeat may collapse.** ⚠ *Found 2026-08-26 ingesting the universe: **5 of 130 names** — CSCO, ISRG, SBUX, WMT, MDLZ — failed CT-7.3's duplicate-key guard.* Companyfacts genuinely emits one fact under two unit or frame labels. CT-7.3 is **right** to refuse a duplicate key (*it silently multiplies rows on the next merge and the result still looks like a panel*, PD-11), so the fix belongs at ingest. ★★ **Two rows on one key with DIFFERENT values are a real conflict and must still raise** — *deduplicating by "keep the first" picks a reported figure by arrival order*, which is exactly the silent choice P5 exists to prevent |
| **DE-52** | ★★ **A per-share figure is not a monetary fact and must never be ingested as one.** ⚠ *`extract_facts` takes "every dated, filed, **monetary** Fact" — `EarningsPerShareDiluted` came through as **`value_minor=0, currency=""`**.* ★ **A zero meaning "not a monetary quantity" is indistinguishable from a zero meaning "the company earned nothing"**, and a model reading the bundle cannot tell them apart — it is worse than the field being absent, because absence is visible. Per-share figures are **D-02's**, computed from a monetary numerator and a share count (RA-132, MP-6) |
| **DE-53** | ★★ **`as_of` is a TRADING DATE in the market's timezone, so a PIT cutoff ends at the close of that ET day — never at UTC midnight.** ⚠ *Found 2026-08-26:* `ObservationLedger.get()` cut off at `Timestamp(as_of, tz="UTC") + 1 day`, which ends the business day at **19:00/20:00 ET**. Every Class-B observation captured in the evening of day T was **invisible to a run dated T**. ★★ **The failure was silent and self-inflicted**: a run captured a profile at 22:50 ET, wrote it, read back `None`, and assembled the bundle without it — *"nothing was captured"* and *"it was captured four hours ago"* were indistinguishable. ⚠ **Never fixed by back-dating `observed_at`**: DE-6.8 says the stamp is ours — *the moment we asked* — and moving it claims we asked earlier than we did |
| **DE-54** | ★★ **A vendor price with more precision than the currency supports is ROUNDED at the boundary, once, explicitly — never refused.** ⚠ *Measured 2026-08-27:* FMP returns `AAPL` at **`310.245`** and `SNDK` at **`1454.445`** in the historical series; `Money.from_float` raised `PrecisionLossError` and **the whole ticker was dropped**. ★★ The refusal then reported as `no_source` — *"the vendor has no data"* — when the truth was *"the vendor has data we declined to round"*, and DE-13's own rule says a missing name is **not** dropped. ⚠ **It was invisible at inference and fatal at training**: the daily run fetches 200 days and the sub-penny prints sat further back, so the defect scales with the history a model needs. Rounded HALF_UP, the same decision `day_open_row` states, with the exponent taken from `Money`'s own currency TABLE rather than the literal `2` |
| **DE-55** | ★★★ **`Q_n = YTD_n − YTD_(n−1)` — the arithmetic this project chose EDGAR FOR, and it was never performed.** ⚠ *Found 2026-08-27 building D-02's 45 fundamental features.* `xbrl.py` has carried `discrete_from_cumulative` since B2 and **nothing ever called it**; `extract_facts` rejected every cumulative span outright. ★ NVDA's raw cash-flow facts carry **38 discrete quarters and 70 year-to-date spans** (36 six-month, 34 nine-month), so **roughly two of every three quarters had no cash flow at all** — and every four-period rolling feature came back null, which reads as *sparse data* rather than as a discarded conversion. ★★ CLAUDE.md states the rationale exactly: *EDGAR's facts carry explicit period start **and** end, so a discrete quarter is distinguishable from a cumulative YTD one by arithmetic, whereas FMP exposes only the period end and must guess — it guessed wrong on MU by 71 %.* **The distinguishing was done; the arithmetic was not.** ⚠ Differenced only **within one fiscal year** and against the immediately preceding YTD of the same series; a repeated `(start, end)` from a restating accession is de-duplicated first, or a span is differenced against itself and emits **a zero-value quarter that looks real**. ★ Self-checking: NVDA FY2026's four derived quarters sum to **102.718 bn against a reported 102.718 bn** |
| **DE-56** | ★★★ **A refresh is recorded only for a class that was actually FETCHED — recording one without a fetch turns `UNCHECKED` into `CHECKED` while checking nothing.** ⚠ *Found 2026-08-27:* `_calendar` recorded `split`, `reverse_split` and `dividend` as refreshed **unconditionally**, and the entrypoint passes `events=()` — so **in production three classes reported `CHECKED` having fetched nothing**. ★★ **DE-35 exists to prevent precisely this** — *"absence of evidence and evidence of absence are different results, and conflating them is how a false assumption becomes a silent one"* — and **the conflation was inside the code implementing the rule.** ★ Measured after the fix: with the store populated from D-07, the gate **HALTs on NVDA's real 10-for-1 split of 2024-06-10**; before it, the same window reported `split: CHECKED` with **zero findings**. ⚠ A **partial** sweep records nothing either: 400 of 510 names leaves 110 unchecked, and DE-36 says an unhandled split on an excluded name *contaminates every other name's rank* |
| **DE-57** | ★★ **The BLOCK handling is derived from what the STORE holds in the window, never from what a run happened to seed.** ⚠ *Found 2026-08-27 immediately after DE-56:* `_calendar` built `handled` from the events passed in, and the entrypoint passes none — so **the moment `ingest/events.py` populated the store, every split in it became unhandled and the daily run would HALT.** ★ QD-15's handling is a property of **how the panel is derived** — *the panel is derived at the run's `adj_as_of`* — not of where the finding came from. ⚠ Still **PIT**: a split not knowable by `as_of` is neither handled nor seen (DE-34), because handling something the run could not have known about is look-ahead **inside the guard**. ★ One implementation in `src/data_engine/calendar/gate.py`, called by both the daily run and the training run — the second had been **a stub asserting `PROCEED` without checking** |
| **DE-58** | ★★★ **A refresh records WHICH NAMES it covered, and a class swept for a subset is `UNCHECKED` for the rest.** ⚠ *Measured 2026-08-27:* `record_refresh` stored a date window and nothing else, so a sweep of **12 names** marked `split` refreshed and a gate over **510** read **`CHECKED` — 498 of them never fetched.** ★★ That is **DE-56's defect one level up**: a refresh recorded beyond what it covered, and the date window made it look rigorous. ⚠ **DE-36 is why it matters** — *a name excluded from the actionable slate still participates in cross-sectional normalisation, so its unhandled split contaminates every other name's rank.* ★ The unfetched names are **NAMED in the status**, not merely counted. ⚠ `covers_tickers = None` — an index written before this field — reads as **unverifiable**, never as universal |
| **DE-59** | ★★★ **QD-15's handling covers `split` and `reverse_split` — NOT every BLOCK.** ⚠ *Found 2026-08-27 the moment `delisting` was ingested:* the handling cleared **every** BLOCK-severity finding, and while the store held only splits that read as correct. Adding delistings marked the real **AVB (2026-08-17) and EQR (2026-08-18) as `handled=True`** — and **re-deriving the panel at `adj_as_of` does nothing for a delisted name**: it has no forward price, its label is undefined, and it cannot be traded. ★ QD-15 says *a BLOCK may only be cleared by an explicit, recorded handling*, and **a blanket handling is not explicit — it just looks like it.** ⚠ An unhandled delisting now HALTs, which is the right outcome: *a name that stopped trading is something a human should look at* |
| **DE-60** | ⚠⚠ **`delisted-companies` CANNOT correct historical survivorship on this plan, and INV-017 stays UNCORRECTED.** *Measured 2026-08-27:* the endpoint returns **100 rows on page 0 and 402 on every page after**, spanning about **three weeks**. ★ So it answers *"who is delisting now"* — which is what §6A's `delisting` class needs — and **cannot** answer *"who delisted in 2019"*, which is what survivorship correction needs. ⚠ The refresh records **the window the feed actually reached**, never the one requested: recording ten years from a three-week feed is DE-56 and DE-58's defect a third time, and the date range is exactly what makes it look rigorous |
| **DE-13** | A universe ticker that resolves to no source **fails the run** (P5). It is not dropped, and it does not become a row of NaNs |
| **DE-14** | Missing is `null`, never `0`, never `""`. A zero revenue and an unknown revenue are different facts |
| **DE-15…DE-16** | Plan-gate handling — see §5A.2 |
| DE-17 | `data/fmp_dump/` is retained; re-pulls go to a new dated directory — see §5A.3a |
| **DE-18…DE-20** | Event-calendar rules — see §5A.4b |
| **DE-21…DE-26** | Point-in-time defects measured in the dump — see §5C |
| **DE-27…DE-30** | Price adjustment is restatement — raw series + events, derived at an as-of — see §5C.7 |
| **DE-31…DE-36** | The pre-run calendar check — see §6A |
| **DE-37…DE-41** | The live FMP reality probe — see §6A.4 |

> **DE-13 is inherited from a real incident.** A LEFT JOIN silently dropped 7 tickers from the
> training panel — 7 of the 13 on the practice watchlist, the *actionable* path. They were scored
> with all 47 fundamental features NaN and nothing said so.

---

# 10. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `DATA.SOURCE.NO_CIK` | ERROR | universe ticker has no CIK → fail run (DE-13) |
| `DATA.SOURCE.NO_FUNDAMENTALS` | ERROR | neither source has the ticker → fail run |
| `DATA.SOURCE.THROTTLED` | WARNING | back off and retry; never drop the request |
| `DATA.SOURCE.UNAVAILABLE` | ERROR | source unreachable after retries |
| `DATA.PIT.NO_FILING_DATE` | ERROR | Fact rejected at ingest (DE-6.3) |
| `DATA.PIT.AS_OF_REQUIRED` | ERROR | as-of omitted on a PIT path (DE-6.4) |
| `DATA.PIT.EMPTY_AS_OF` | WARNING | nothing knowable at that date — empty result, **not** an error |
| `DATA.VALIDATION.REJECTED` | WARNING | row failed a REJECT rule; not stored |
| `DATA.CONTRACT.MISSING_CURRENCY` | ERROR | `*_minor` with no `*_currency` sibling (CT-M.1) |
| `DATA.STORE.WRITE_FAILED` | ERROR | atomic write failed; no partial file remains |
| `DATA.FX.UNAVAILABLE` | WARNING | no rate — dependent value reported unavailable (FX-3) |
| `DATA.SOURCE.PLAN_GATED` | ERROR | endpoint returned `402` — names the endpoint and the tier; **never treated as an empty result** (§5A.2) |
| `DATA.OBSERVATION.LIVE_READ_DENIED` | ERROR | a training/backtest/inference consumer asked for a Class-B field outside CT-7.6 (DE-6.9) |
| `DATA.PIT.NO_FILING_DATE_DERIVED` | ERROR | a derived periodic has no statement to inherit `acceptedDate` from (DE-22) |
| `DATA.PIT.WEAK_GUARANTEE` | WARNING | serving FMP-routed fundamentals to a PIT consumer — best-effort, not reconstructed (DE-23) |
| `DATA.RESTATEMENT.VALUE_CHANGED` | WARNING | an FMP periodic changed value between ingests; recorded, never silently overwritten (DE-24) |
| `DATA.PRICE.ADJ_AS_OF_REQUIRED` | ERROR | an adjusted price panel was requested without an `adj_as_of` (DE-28) |
| `DATA.PRICE.RAW_REQUIRED` | ERROR | a non-scale-invariant feature tried to read the adjusted panel (DE-29) |
| `DATA.CALENDAR.UNHANDLED_BLOCK` | ERROR | corporate action inside the window with no recorded handling — **halts the run**, names tickers and events (DE-32) |
| `DATA.CALENDAR.CHECK_MISSING` | ERROR | a run reached feature-building without a calendar check (DE-31) |
| `DATA.CALENDAR.CLASS_UNCHECKED` | WARNING | an event class could not be evaluated; reported as `UNCHECKED`, never as "none" (DE-35) |
| `DATA.PROBE.SKIPPED` | WARNING | the live reality probe did not run (no key / no network) — **surfaced, never silent** (DE-40) |

---

# 11. ACCEPTANCE CRITERIA

```text
SOURCE ROUTING
□ AC-7.1   A 10-K/10-Q filer routes to EDGAR; recorded as source="edgar"
□ AC-7.2   A 20-F/6-K filer routes to FMP; recorded as source="fmp"
□ AC-7.3   ARM's 6-K series is NOT ingested as quarterly (the 1.93×/2.76×/3.30× regression)
□ AC-7.4   A universe ticker with no source fails the run, with the ticker named
□ AC-7.5   Where both sources have a period, EDGAR supplies the TTM line items
□ AC-7.6   Source is per-ticker and stable across a series (DE-5.3)

POINT-IN-TIME
□ AC-7.7   as_of(D) excludes every Fact with filing_date > D
□ AC-7.8   A restatement filed before D IS returned; filed after D is NOT
□ AC-7.9   A Fact with no filing_date is rejected at ingest
□ AC-7.10  Omitting as_of on a PIT path raises — no default to today
□ AC-7.11  Same ledger + same as_of ⇒ byte-identical output (constitution INV-2)
□ AC-7.12  The ledger is append-only; a restatement adds a row and changes none
□ AC-7.13  A period with a restatement is visibly marked to the consumer

CONTRACTS & MONEY
□ AC-7.14  Every monetary column has its *_currency sibling; a missing one fails validation
□ AC-7.15  Price panel satisfies DC-1 (monotonic dates, no future, no null close, OHLC ordering)
□ AC-7.16  Both period_start and period_end are present on every fundamental row
□ AC-7.17  CT-7.2 can be rebuilt from CT-7.3 and matches byte-for-byte
□ AC-7.18  A converted value is accompanied by the FxRate used

SOURCE CATALOG & CLASS-B OBSERVATION  (§5A)
□ AC-7.26  A Class-B field served to a training/backtest/inference consumer comes
           from CT-7.6 at an as_of; serving it live to those consumers raises (DE-6.9)
□ AC-7.27  observed_at on an Observation row is OUR fetch time, never a vendor field (DE-6.8)
□ AC-7.28  Re-snapshotting unchanged Class-B data appends no row (DE-6.10, content_hash)
□ AC-7.29  The observation ledger is append-only; a changed consensus adds a row
           and modifies none (DE-6.7)
□ AC-7.30  analyst-estimates is NOT joined to a training row by its `date` field
           — that field is the forecast period, not a publication date (§5A.4)
□ AC-7.31  No module in src/data_engine ingests technical-indicators/* from FMP
           (indicators are D-02's, per §5A.1 — enforces constitution INV-2/INV-4)
□ AC-7.32  A 402 is retried with backoff before being reported; a persistent one
           fails loud naming the endpoint AND the parameters, and is never
           converted into an empty result (DE-15, P5)
□ AC-7.33  A parameter combination known to be plan-gated is rejected at the client
           boundary rather than sent and failed (DE-16, §5A.2 cause 2)
□ AC-7.34  Quarterly ratios and key metrics are COMPUTED from quarterly statements,
           never fetched — `period=quarter` is 402 on those endpoints

POINT-IN-TIME DEFECTS MEASURED IN THE DUMP  (§5C)
□ AC-7.35  An FMP fundamental row is placed in time by acceptedDate/filingDate,
           never by `date` (period end) — the gap is 20-57 days (DE-21)
□ AC-7.36  A derived periodic with no filing date inherits its statement's
           acceptedDate; with no matching statement it is not served PIT (DE-22)
□ AC-7.37  `lastUpdated` is never used as a knowability date (DE-23, §5C.2)
□ AC-7.38  A served artifact states whether its PIT guarantee is reconstructed
           (EDGAR) or best-effort (FMP) (DE-23)
□ AC-7.39  Re-ingesting an FMP periodic diffs against the stored value and records
           a change event rather than overwriting silently (DE-24)
□ AC-7.40  historical-market-capitalization is not served to a PIT consumer; past
           market cap is close(d) x shares(as_of=d) (DE-25)
□ AC-7.41  A calendar entry carries both an event date and a knowability date;
           scheduled and occurred events are separate entities (DE-18, DE-19)
□ AC-7.42  A news-derived feature's training window starts at first capture, and
           that date is recorded so a backtest cannot extend before it (DE-26)

PRICE ADJUSTMENT AS RESTATEMENT  (§5C.7)
□ AC-7.43  The price store holds the RAW series plus split/dividend events; the
           adjusted panel is derived, never ingested as primary (DE-27)
□ AC-7.44  Adjustment applies only events with date <= adj_as_of; the same backtest
           re-run later produces byte-identical prices (DE-28, constitution INV-2)
□ AC-7.45  Non-scale-invariant features - absolute price/volume thresholds, share
           counts, the M-1 penny-stock screen - are computed on the RAW series (DE-29)
□ AC-7.46  A price panel records its adj_as_of; two panels over the same dates with
           different adj_as_of do not compare equal (DE-30)

PRE-RUN CALENDAR CHECK  (§6A)
□ AC-7.47  A training/backtest/inference run that builds features without a calendar
           check raises (DE-31)
□ AC-7.66  The check covers the whole UNIVERSE over the full window, not the
           watchlist and not the actionable subset (DE-36)
□ AC-7.49  An unhandled BLOCK halts the run and names the tickers AND the events;
           no ticker is silently dropped (DE-32)
□ AC-7.50  All 18 event classes appear in class_status as CHECKED or UNCHECKED:<why>;
           a missing class fails the contract (DE-35, CT-7.7)
□ AC-7.51  News beyond ~92 days reports UNCHECKED, never "no events" (DE-35, K-8)
□ AC-7.52  Findings are keyed on knowability dates, not event dates — a split
           announced after as_of is absent from the report (DE-34)
□ AC-7.53  The report is persisted with the run and referenced by every artifact
           the run produces (DE-33, AP-6)

LIVE REALITY PROBE  (§6A.4 — F3 Tier 1, records CT-3.2)
□ AC-7.54  A live probe fetches from FMP over the network and digests through the
           real code path — no fixture, no mock, no cassette (DE-37)
□ AC-7.55  The probe asserts against the K-1..K-10 known-answer set, comparing every
           intermediate rather than only the final report (DE-38, DE-39)
□ AC-7.56  A skipped live probe is reported as skipped in the run summary and never
           counted as a pass (DE-40)

ADJUSTMENT FACTOR, READ PATH & VALIDATION  (CT-7.1 DE-42..DE-45, DE-12)
□ AC-7.57  adj_factor is materialised once per (ticker, date, adj_as_of) and every
           adjusted field is raw x adj_factor; no consumer recomputes it (DE-42)
□ AC-7.58  Where FMP supplies an adjusted open the reconstruction matches it; where
           it does not, adj_factor is strictly positive and changes only on dates
           the calendar check flags (DE-43, D-03 QA-85)
□ AC-7.59  Ex-dividend dates carry their OWN assertion - a close-derived factor must
           not double-count the drop already present in the raw open (DE-44, QA-91)
□ AC-7.60  Validation classifies ACCEPT / FLAG / REJECT and never modifies a value:
           a FLAG is stored with the row, a REJECT is not stored at all (DE-12)
□ AC-7.61  Omitting adj_as_of on the price read path raises; None is the explicit
           RAW value and never an implied adjustment (DE-45)
□ AC-7.62  Every Fact carries period_type, so §6.3's grouping key
□ AC-7.63  ★ get_day_open serves the opening PRINT, not the day-T bar; a row whose
           OHLC fields are all equal is refused, never returned (DE-47, OR-32)
□ AC-7.64  ★ An unsettled open returns settled=False and is never backfilled
□ AC-7.65  ★ is_trading_day returns None outside its declared holiday coverage,
           and D-08's OR-6 blocks on it rather than assuming a session (DE-48)
           from the previous close (DE-47, OR-33)
           (tag, period_end, period_type) resolves against CT-7.3

OPERATIONAL
□ AC-7.19  Re-running ingest produces identical files (idempotent)
□ AC-7.20  A killed write leaves no readable partial file
□ AC-7.21  EDGAR requests carry a contactable User-Agent and are throttled
□ AC-7.22  No API key or User-Agent email appears in any log, artifact or error
□ AC-7.23  The filing-aware cache is invalidated by a new filing, not by elapsed time
□ AC-7.24  No module in src/data_engine imports the LLM gateway
□ AC-7.25  Missing values are null; no zero-filling anywhere
□ AC-7.67 ★ the EDGAR transport decodes a gzip response; a fake that
           returns raw gzip bytes must not reach json.loads (DE-50)
□ AC-7.68 ★ identical duplicate facts collapse; a value CONFLICT on the
           same key still reaches CT-7.3 and raises (DE-51)
□ AC-7.69 ★ no per-share tag is ingested as a monetary fact — a 0 that
           means 'not monetary' never reaches a bundle (DE-52)
□ AC-7.70 ★ an observation captured at 22:50 ET on day T is visible to a
           run dated T; one captured on T+1 is not (DE-53)
□ AC-7.72 ★ a sub-penny vendor price is rounded HALF_UP at the boundary
           and the ticker ingests — never reported as no_source (DE-54)
□ AC-7.73 ★★ a YTD series yields discrete quarters that sum to the
           reported year; a repeated span is never differenced against
           itself; a missing operand yields no fact (DE-55, DE-14)
□ AC-7.74 ★★ a class is CHECKED only if fetched; a partial sweep records
           no refresh; a reverse split is classified by RATIO not label (DE-56)
□ AC-7.75 ★★ the handling covers BLOCKs the run did not seed; an event
           not yet knowable is neither handled nor seen; both runs share
           one gate (DE-57, DE-34, FE-4)
□ AC-7.76 ★★★ a class swept for a subset is UNCHECKED for the rest and
           names them; an uncovered refresh is unverifiable (DE-58)
□ AC-7.77 ★★★ a delisting is not cleared by the price adjustment and
           HALTs; the feed's reachable window is recorded, not the
           requested one (DE-59, DE-60)
□ AC-7.78 ★★ two snapshots with the same CIK under different tickers yield a
           ticker_change finding naming the successor symbol (DE-62)
□ AC-7.79 ⚠ a CIK that disappears from the SEC file is NOT reported as a
           delisting — it is a candidate for investigation (DE-62, DE-35)
□ AC-7.80 ★★ resolve(ticker, as_of) returns the instrument that held the
           ticker THEN, not the one holding it now (DE-65, DE-61)
□ AC-7.81 ★ the fetch symbol for a renamed name is the CURRENT one, and the
           symbol used is recorded with the panel (DE-63)
□ AC-7.82 ⚠⚠ a series is never spliced across a rename (DE-64)
□ AC-7.83 ticker_change is BLOCK and clears only on a recorded handling,
           never by severity downgrade (DE-66, QD-15)
□ AC-7.84 ★★ a knowable ticker_change SUPERSEDES a vendor delisting for the
           same ticker; the delisting row is NOT deleted and the
           ticker_change BLOCK still stands (DE-67, DE-66, RC-54)
☑ AC-7.85 ⚠⚠ a ticker_change does not by itself classify the cause: a
           merger of equals yields TWO findings (survivor + retired side),
           the cause is REFUSED without sources, and the retired symbol is
           checked for successor-price contamination — ⚠ which is a
           DIVERGE-then-CONVERGE shape, never mere agreement (DE-68)
□ AC-7.86 ★★ class 4 comes from EDGAR and is matched by an explicit form
           whitelist plus 8-K item 4.02 — NEVER by the /A suffix, which
           matches ownership amendments that restate nothing (DE-69)
□ AC-7.87 ⚠⚠ a feed that truncates silently is CHUNKED and a response at
           the row cap is treated as truncated; an uncovered chunk records
           NO refresh and names its cause (DE-70, DE-58)
□ AC-7.88 ★★ a scheduled earnings date is knowable at as_of, not on the
           date, and carries the caveat that it moves (DE-71, DE-65)
□ AC-7.89 ★★ a feed that ignores `limit` is windowed CLIENT-SIDE, and a
           per-ticker cap is admitted in the result rather than silently
           dropping rows (DE-35, CN-10)
□ AC-7.90 ★ cadence is by severity, measured from the RECORDED refresh;
           never-refreshed, stale and exempt are three states (DE-72)
□ AC-7.91 ★ every event class is either swept by a named `ingest` command, derived at
           check time, or permanently unchecked — and `status` says which (DE-73)
□ AC-7.92 ★ a running `ingest` command prints elapsed time and its current stage at a
           fixed interval, each stage's duration, and its total — and stops cleanly (DE-74)
□ AC-7.93 ★★ get_fundamentals_history yields one (filing_date, rows) per distinct filing date,
           each equal to get_fundamentals at that date; a later amendment is absent before
           its own filing date (DE-75)
□ AC-7.94 ★★ a restatement_amended BLOCK is handled only when the caller declares PIT
           fundamentals, with the recorded handling string; otherwise it still HALTs (DE-76)
□ AC-7.95 ★ load_sector_map returns every configured ticker's GICS sector, upper-cased
           keys, and never invents one for an absent name (DE-77)
□ AC-7.96 ★★★ price_events turns the store's splits, reverse splits and dividends into the
           adjustment's events; a panel built with them shows no split as a return (DE-78)
□ AC-7.97 ★★ price_event_conflicts names a ticker whose dividend is ≥ its prior close, with the
           numbers; a consistent ticker is not named (DE-79)
□ AC-7.98 ★ A name that fails once and succeeds on the retry pass is fetched; one that fails
           twice is named with its last reason; the pause happens once per pass (DE-80)
□ AC-7.99 ★★ A narrower refresh never narrows the recorded coverage; a wider one replaces it;
           new names merge over the common window at the older time (DE-81)
```

---

# 12. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QD-1** | Does the Fact ledger keep one parquet per ticker, or one partitioned dataset? | Per-ticker is simpler to write atomically; partitioned is faster to scan. Leaning per-ticker |
| ~~QD-2~~ | ~~Are prices point-in-time too?~~ | **CLOSED 2026-08-16 — yes, decisively.** NVDA's 10:1 shows `full` retro-adjusts price ÷10 and volume ×10 across the whole history. See **§5C.7** and DE-27…DE-30. The 2026-08-15 reading was wrong and is retracted in §5C.6 |
| **QD-3** | How far back does the ledger rebuild? Full EDGAR history is large | |
| **QD-4** | Does D-07 serve news raw, or with materiality pre-filtered? | Filtering is judgement → D-01. Leaning raw |
| **QD-5** | Where does the universe list live — config file or a D-07 artifact? | §5A.1 shows `stock-list` / `financial-statement-symbol-list` / `actively-trading-list` are all available; a D-07 artifact built from them beats a hand-kept config |
| **QD-6** | How often is each Class-B `field_set` snapshotted (CT-7.6)? | Daily is the obvious default and it is not free — 130 names × N field-sets × 250 days. Consensus moves slowly; TTM ratios move quarterly. Probably per-field-set cadence, not one global one |
| **QD-7** | Do we build revision momentum from `grades`/`price-target-news` (Class A, reconstructible backwards) or snapshot `grades-consensus` (Class B, forward-only)? | §5A.4 recommends the event feeds. Confirm before either is wired |
| **QD-8** | Is the **institutional-ownership `402`** worth a plan upgrade? | It is the largest single gap. Nothing else on the paywalled list is load-bearing |
| **QD-9** | Where do earnings-call transcripts come from, if anywhere? | FMP has none at any tier (§5A.3). This is the biggest D-01 loss, and there is no in-house substitute |
| **QD-10** | Does the **calendar** family belong in D-07 at all, or is a forward-looking schedule D-05's? | It is data with a source and a timestamp, so D-07 by DE-1 — but a `CalendarEntry` is a claim about the future, which nothing else in D-07 is. §5A.4b now sketches the surface; the owning domain is still open |
| **QD-11** | Do we snapshot `earnings-calendar` daily to get schedule-revision history (DE-18/DE-20), or accept that scheduled-date features are unavailable for training? | Snapshotting is cheap and forward-only; without it, 34.6% of calendar rows are unusable for D-04 |
| **QD-12** | Is `revenue-*-segmentation` worth having at annual-only granularity? | `period=quarter` is 402. Annual segments are useful to D-01 as narrative, near-useless to D-04 as a feature |
| **QD-13** | `dividends.adjDividend` vs `dividend` — which does the book use? | §5C.7 settles the mechanism: `adjDividend` is retro-adjusted by the same split machinery, so it needs the same `adj_as_of`. Which one D-11 records for a real cash dividend received is still open |
| **QD-14** | How often is the dump re-pulled to a new dated directory (DE-17), and does anything diff them automatically? | Manual for now. An automated quarterly diff is the only restatement detector available on the FMP side (DE-24) |
| **QD-15** | What counts as **handling** a BLOCK-class event (§6A.3 DE-32)? | A split is handled by re-deriving the panel at the run's `adj_as_of`. A restatement has no defined handling yet — re-ingest? exclude the period? exclude the ticker? ⬜ *2026-10-07 — Victor chose **the PIT store** (as filed before the amendment, amended after), verify first. Verification: the fact ledger keeps every filing, so the store CAN answer it; but training reads it once at today, so the claim is not yet true of the training panel (L3 `DX-159`). Not recorded as a handling until it is.* ✅ *Ruled 2026-10-07: DE-75 replays the ledger per filing date; DE-76 records the handling, opt-in by a caller that replays.* |
| **QD-16** | Does the calendar check sweep FMP live per run, or read an incrementally-maintained store? | 130 tickers × 8 sourced classes ≈ 1,000 calls against a 300/min cap. A store is almost certainly required; that store is then itself a D-07 artifact needing a contract |
| **QD-17** | Cadence for the live reality probe (DE-41)? | This is **F3 Q1** reaching D-07. Two callers now; it should be answered once, in F3 |

> **QD-2 deserves attention.** Split-adjusted prices are restated data with exactly the same
> look-ahead hazard as a restated filing — a backtest reading today's adjusted series is using
> adjustments that did not exist then. The current codebase does not model this, and neither did
> the original design. It may be acceptable; it should be an explicit decision.

---

# 13. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-07, M-5, §17 G-1…G-7 | domain definition, currency, tier & promotion rules |
| `L0-system-vision.md` §17.3 | **why `INV-1` and `INV-001` are different families** — always qualify by source (G-3) |
| `L2-shared-money.md` | Money, FxRate, CT-M.1/M.2, FX-1…FX-3 |
| `L4-coding-standards.md` §1.1, §1.5, ST-1…ST-8 | paths, migration classes, structural rules |
| `sdd/specs/F9_universe_and_fundamental_sources/spec.md` | source routing, 6-K cumulative evidence, coverage *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F4_data_plane/spec.md` | currency-per-leg, `fx_rate_used` *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/constitution.md` DC-1, INV-1/2/5, P5 | price panel contract, invariants, fail-loud |
| `L0-system-vision.md` INV-017 | survivorship — the reason `delisted-companies` is in §5A.5 |
| `data/fmp_dump/README.md` + `_MANIFEST_FINAL.csv` | **the retained reference dump** every §5A/§5C claim is checkable against (DE-17), and the source of the §6A.5 known-answer set |
| `sdd/specs/F3_sdd_adoption/spec.md` §4a Tier 1, **CT-3.2**, §4c, Q1 | the reality-probe tier §6A.4 requires, its record format, and the cadence question *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F1_disciplinary_report/spec.md` AC-1.15 | prior art for a **gate that measures, names the tickers, and refuses** rather than proceeding silently *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `L0-system-vision.md` §1.6 | the two analyst seats §5A.4a splits the catalog between |
| [`L1-feature-engineering.md`](L1-feature-engineering.md) | **D-02, the primary consumer.** Its §6 says which of this catalog reaches which analyst seat; its FE-8…FE-10 depend on §5C.7 and §6A |
| `sdd/specs/F0_code_map/spec.md` §12 **D-19** | the DCF net-debt omission `enterprise-values` would inform *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
