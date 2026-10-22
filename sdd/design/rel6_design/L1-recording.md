# L1: Domain Specification — Recording (D-11)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-11 · **Seat:** SEAT-5
> **Path:** `src/recording/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L2-shared-money.md`](L2-shared-money.md) (D-00) · [`L1-data-engine.md`](L1-data-engine.md) (D-07, prices/FX)
> **Prior art:** `pipeline/portfolio/**` (1,038 LOC, **F4, 8/8 ACs green**), `pipeline/discipline/journal.py`
> **Grounded in:** `samples/bmo_investorline_transactions/` — 3 real accounts, 149 transactions, 2026-01-01…2026-08-18

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.12.0 | 2026-08-27 | Victor | ★★★ **RC-62…64 — the run record could not name the model that produced the pick.** ⚠ *Measured on a complete run directory:* `grep` for the promoted model's hash **found nothing**; `manifest.json` carried `inputs: []` and `code.git_sha: ""`. **QA-121** requires the trace and **INV-2** rests on it. D-03's `Nomination` is now folded into `recommendation.json` (**Victor's choice of file**, 2026-08-27) — ★ composed by D-11 at write time so **D-12's contract gains no dependency on D-03's**. **`delivery.json`** added to CT-11.7 and four columns to the index. AC-11.44…11.46. |
| 0.11.0 | 2026-08-26 | Victor | ★★ **RC-59…61 + CT-11.7 — the run artifact, which RC-33 has required since v0.5.0 and nothing implemented.** ⚠ **`ManifestStore` and `JournalStore` were both built and NEITHER was ever called**: every manifest, recommendation, card and thesis evaporated at process exit. ★ **P6 was unmet**, and *every* measurement in these specs — RM-2/RM-3, DN-17, DN-29 — needs run history that did not exist. **RC-61** stores a thesis under its `bundle_hash` and reuses it ($1.34/run otherwise); ★ this does **not** harm RM-1, whose k runs happen inside one authoring event with `temperature = 0` (GW-8). AC-11.40…11.43. |
| 0.10.0 | 2026-08-25 | Victor | ✅✅ **RC-57 — ALL FOUR ACCOUNTS RECONCILE TO THE CENT against the balances BMO shows.** The first external check of any number in this system. It took two more defects, both mine: **RC-55** — the column layout **changes within one file** (75 narrow + 74 wide rows interleaved in `TFSA_2`), so each row is mapped by its own width; **RC-56** — **a blank `Activity Description` can carry real cash** (three RESP `GRANT REC` rows at $500), and skipping them silently lost **exactly the $1,500** the account was short. ⏸ **RC-58**: Canadian listings and CDRs are **postponed** at Victor's instruction — positions are still derived and reconciled; only market value waits, because the FMP plan covers US listings only. |
| 0.9.0 | 2026-08-25 | Victor | ⚠⚠ **Wiring the book into D-05 surfaced four valuation defects, three of them silent.** **RC-51**: a transaction export **carries no balance**, so RC-10 reconciles derived NAV against derived NAV and **checks nothing** — the book is `UNRECONCILED` until a balance arrives from outside it, and D-05 correctly refuses it. **RC-52**: a CDR is valued from **CAD cost basis × the underlying's USD return**, ratio-free. ★★ **RC-53**: a bare ticker is **ambiguous across venues** — `MDA` and `BMO` returned the **NYSE listings in USD** for TSX positions held in CAD, *a plausible number in the wrong currency*, **more dangerous than the 402s that refuse loudly**. **RC-54**: FMP answers `SPCX` with a NASDAQ listing this spec says does not exist; **neither side is assumed right**. |
| 0.8.0 | 2026-08-25 | Victor | ★★ **Re-ingested against FULL-HISTORY exports (`From=2022-01-01`, all four accounts) — the book now derives from activity alone and every position is non-negative.** RC-45 is cleared: 462 activities → **225 orders → 14 open positions, none negative**. ★ Three findings the longer history produced: **RC-48** — `TFSA_2`'s file carries **one row from a different (`Joint`) account**, refused rather than absorbed; **RC-49** — `Disbursement` **moves shares with no cash** (`PLTR 390 @ 0`), and classifying it cash-only would lose 390 shares while the cash balanced; **RC-50** — **five new activity types**, each caught by RC-13 on first parse. ⚠ The opening-snapshot *inference* helper was **deleted at Victor's instruction**: it produced numbers nobody could check against a statement. |
| 0.7.2 | 2026-08-25 | Victor | ★ **RC-47 — the book may origin from a stated opening snapshot.** RC-45 leaves a book whose activity starts after its lots were opened with no correct derivation; a snapshot read off a statement supplies the starting balance, and **RC-10 still has to balance**. ⚠ It may **not** be back-computed as `current − activity` — that makes the holdings an input, so the replay reproduces them by construction and checks nothing. AC-11.34/11.35 added. |
| 0.7.1 | 2026-08-25 | Victor | ⚠⚠ **RC-45 — replaying the real exports produced NEGATIVE positions, and they are not shorts.** `PLTR RESP −520`, `GOOG TFSA_2 −30`, `BBD.B RRSP −26` are lots opened **before** the `From=2026-01-01` window: their sells are in the file and their buys are not. ★ **RC-9 derives the book from activity**, so a truncated window derives the wrong lot **while the arithmetic looks healthy** — a negative derived quantity now blocks. **RC-46**: `instrument_id` separator changed to `|` because **`BBD.B` is a real holding** and a dotted id cannot be split back into RC-16's triple. |
| 0.7.0 | 2026-08-23 | Victor | ⚠ **Arrival capture RETIRED — QC-5 stands, `L3` BS-3 amended.** BS-3 made it *first* among B1's obligations while §7 had already cancelled it; the contradiction surfaced while scoping B1. **`CT-11.5` tombstoned (T-2), `record_arrival()` removed from §11, `RC-7` superseded → `RC-7a`, `log_segment` dropped from `CT-11.2`.** ★★ **RC-7a states the asymmetry**: a one-valued enum asserts nothing and is retired; a permanently-`false` boolean asserts *we looked and the answer is no* and stays (DE-35). ★ **§7's argument upgraded from SCALE to STRUCTURE** — RC-38 means there is no intra-order gap to measure, not merely one too small to bother with. |
| 0.7.0 | 2026-08-25 | Victor | ★★ **§8 built against the four real exports, and the data overturned three assumptions.** **RC-37**: the export has **two column layouts** (10 vs 13 — `TFSA_2` inserts three account columns), so a positional parser mis-books every row of the wider file; it also hid the `Interest` activity, which **RC-13 caught on the first real parse**. **RC-38**: an order fills at **several prices**, so price is not part of the order key and the notional is `Σ|qᵢ|·pᵢ` per tranche — keyed on price, `NVDA 2026-04-29` splits into residuals `9.48`/`0.47` instead of one `9.95`. **RC-39**: the flat fee is `9.95` in **both** currencies (measured over 137 orders), `0.00` on BMO's own ETFs, and a **multiple** of it reveals two same-day orders merged — the export carries no order id. ⚠ **RC-44**: USD sells carry an unexplained excess, **reported not absorbed**. AC-11.30…11.33 added. |
| 0.6.0 | 2026-08-23 | Victor | ⚠ **New §5.3 H-0 — the broker misnaming, promoted to the top of §5 where a reader lands.** `"CIBC"` in this export is the **CDR issuer inside an instrument Description**, not the institution; the broker is **BMO InvestorLine**. The error had propagated to four files (`sdd/specs/README.md`, D-03 **V-30**, L4 §1.5, the brainstorm) — **all corrected**. **RC-36.** ✅ **Tranche handling CONFIRMED by the account holder** (2026-08-23): split rows fill *within seconds at an identical price* and carry **one** `$9.95` commission. **RC-37/38/39** — ★ **RC-38 is the consequential one: the tranche split is a REPORTING artifact and never a source of slippage**, which removes the last plausible intra-order execution cost in this book. |
| 0.5.0 | 2026-08-18 | Victor | ⚠ **Audit finding B: `RC-7` was cited twice (§11 API, §12 roll-up) and had never been written.** Now defined — every trade row carries `log_segment ∈ {retrospective, forward}`, the two have different quality and **are never pooled without saying so**. `RC-6` defined alongside it (account is a required field, not an inference). |
| 0.4.0 | 2026-08-18 | Victor | ⚠ **Audit: D-12 and D-08 both write into the record and neither was named.** **New §7Z / RC-31…RC-35** — the append-only `VetoedCandidate` counterfactual arm (DN-19/21), marking vetoed names on the **same horizon and open anchor** as acted-on ones (DN-20), D-08's `RunOutcome` including its failure states, the journalled VETO override, and the write boundary. Parent bumped to L0 v0.18.0. |
| 0.3.0 | 2026-08-18 | Victor | ★ **QC-3 CLOSED (Victor): a CDR is the same instrument as its underlying** — **no change needed in D-07 or D-02**, and the ticker collision dissolves. The split survives only in **valuation**, and §5.6 resolves it: **FMP Starter has NO Canadian coverage at all** (RY.TO/SHOP.TO/ENB.TO/XIU.TO all 402), so there is no CDR price feed and none is obtainable without an L0 §2.2 decision. **RC-26: mark a CDR lot by applying the underlying's USD return to its CAD cost basis** — ratio-agnostic, which matters because CIBC's share ratio is exactly what FMP cannot supply. **RC-27** makes it self-checking; **RC-28** separates `analysis_symbol` from `instrument_id`. Measured on 8 closed round trips: mean signed error **−0.08 pts** vs the USD return against **−0.98** unhedged, but sd ≈ 2.2 either way — **corroborated, not proven** (QC-4). |
| 0.2.0 | 2026-08-18 | Victor | ★ **Re-scoped down on Victor's instruction: this is a recording-and-monitoring template for a retail book, not a fund back-office. Minimal priority.** §0 states the scope; §7's two-log structure collapses to a note because **QC-5 is closed "won't do"** — no arrival capture, so **QQ-20 closes as *will not measure***. All four accounts now sampled and named by type: **H-5 is resolved by the filename convention**, and **QC-1 / QC-2 / QC-5 all close**. New finding: **all four accounts are registered**, so M-4 is book-wide. Capital base grounded — median order **$8,941**, max **$29,018**. §14 trimmed to what a monitoring template actually needs. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft, written against **real broker exports** rather than a described format. §5 records **eight hazards found in the sample data**, four of which the current parser does not handle. |

---

# 0. SCOPE — read this before the rest

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-11 IS A RECORDING AND MONITORING TEMPLATE FOR A RETAIL BOOK.  ║
║  IT IS NOT A FUND BACK-OFFICE. PRIORITY: MINIMAL.                ║
║                                                                  ║
║  Four registered accounts. Orders up to ~$30k, median ~$9k.      ║
║  One human, one broker, a manual CSV drop, no API, no venue.     ║
║                                                                  ║
║  What it must do:  ingest the export without getting the cash    ║
║      wrong, keep positions and cash per currency, reconcile,     ║
║      publish the capital base, keep the decision journal.        ║
║                                                                  ║
║  What it must NOT become:  a transaction-cost analytics stack,   ║
║      an attribution engine, or an execution-quality programme.   ║
║      Risk (D-05) and sizing (D-06) are a PILOT EFFORT and this   ║
║      domain should not be built as though they were more.        ║
╚══════════════════════════════════════════════════════════════════╝
```

> **v0.1.0 over-built this**, on the assumption that D-11 would carry the execution-cost measurement
> QQ-20 needs. **It will not** — see §7. The hazards in §5 survive the re-scope unchanged, because
> they are *correctness* problems: getting the cash flow wrong breaks a simple recorder exactly as
> badly as a complex one. What shrinks is ambition, not accuracy.

### Sizing the ambition honestly

| | Measured from the four exports |
|---|---|
| Accounts | **4 — RESP ×1, RRSP ×1, TFSA ×2. All registered.** |
| Transactions, 2026 YTD | 221 |
| Distinct symbols | 6–11 per account |
| Order size | median **$8,941**, p90 **$17,677**, max **$29,018** |
| Commission | **$9.95**/trade ⇒ **$19.90** round trip ⇒ **11–22 bps** at typical order size |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"What does the book actually hold, what actually happened to it, and can I prove it?"**

D-11 is **custody of the fact**. It is the only domain whose output is checkable against an external
authority — the broker — and that is its defining property: **every other domain's correctness is
argued; D-11's is reconciled.**

## 1.2 Position

```text
        ┌──────────────────────────────────────────────────────┐
        │  D-09 Reporting · D-05 Risk · D-06 Portfolio Strategy │
        │  all READ the book; none of them writes it            │
        └───────────────────────▲──────────────────────────────┘
                                │ one-way (ST-9)
        ┌───────────────────────┴──────────────────────────────┐
        │  D-11 RECORDING                        SEAT-5        │  ← this spec
        │  ingest · reconcile · book · trades · journal        │
        │  ★ LEVEL 0 AUTONOMOUS — no agent, no LLM             │
        └───────────────────────▲──────────────────────────────┘
                                │
        ┌───────────────────────┴──────────────────────────────┐
        │  Broker export (MANUAL, file drop)  +  D-07 prices/FX │
        └──────────────────────────────────────────────────────┘
```

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-11 RECORDS WHAT HAPPENED. IT NEVER DECIDES, NEVER ADVISES,    ║
║  AND NEVER RENDERS.                                              ║
║                                                                  ║
║  In scope:  broker ingestion, reconciliation, position and cash  ║
║      state, P&L, the trade log, the decision journal,            ║
║      performance attribution, the CAPITAL BASE (QA-63).          ║
║                                                                  ║
║  Out:  presentation (D-09) · risk metrics (D-05) · sizing        ║
║      (D-06) · any judgement about whether a trade was good.      ║
║                                                                  ║
║  D-11 MAY NOT import D-09 (ST-9). A renderer upstream of the     ║
║  book can rewrite history to match what it printed.              ║
╚══════════════════════════════════════════════════════════════════╝
```

**Authority: LEVEL 0 AUTONOMOUS** (L0 §3.1). Writing a trade to the log commits nothing and
recommends nothing — it records something that already happened.

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **Account** | one brokerage account | `account_id` | **four exist; three sampled.** Registered status is *not* a field — §5.3 H-5 |
| **RawActivity** | one export row, verbatim | `(account_id, row_ordinal, file_hash)` | immutable; never edited |
| **Order** | one instruction, possibly multi-tranche | `(account_id, date, symbol, side, price_level)` | **derived** — §5.3 H-1 |
| **Trade** | one executed order | `order_id` | the unit QA-61 charges |
| **Instrument** | what was actually traded | `(symbol, venue_currency, wrapper)` | **not the ticker** — §5.3 H-2 |
| **CashFlow** | contribution · dividend · tax · FX · fee | `(account_id, date, kind, ordinal)` | |
| **Position** | account × instrument × date | `(account_id, instrument_id, date)` | |
| **BookState** | account × date | `(account_id, date)` | positions + cash per currency |
| **CapitalBase** | account × date | `(account_id, date)` | ★ **QA-63** |
| **JournalEntry** | one decision | `(date, ordinal)` | why, written at the time, never revised |
| **ArrivalQuote** | one order submission | `(submit_ts, symbol)` | ★ **forward-only** — §7, QA-69 |

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── the broker export   MANUAL file drop; no API exists or is planned (L0 §2.2)
  ├── D-07               prices for marking, FX rates for M-5 conversion
  └── D-00               Money — every amount is (minor, currency)

DEPENDED ON BY
  ├── D-09 Reporting     renders the book                (one-way, ST-9)
  ├── D-05 Risk          exposure, drawdown, flags
  ├── D-06 Portfolio     sizing arithmetic
  └── D-03/D-04          ★ the CAPITAL BASE (QA-63) and the realised cost (QQ-20)

DOES NOT DEPEND ON
  ✗ D-09  — ST-9, one-way
  ✗ D-01/D-03/D-04 — the book is a fact, not an opinion
  ✗ the LLM gateway (AP-5, ST-5)
```

---

# 4. MODULE DECOMPOSITION

```text
src/recording/
├── ingest/          # broker export -> RawActivity, verbatim and hashed
│   ├── bmo.py       #   the ONE format that exists (§5.1)
│   └── registry.py  #   format detection; unknown format => raise (RC-3)
├── orders/          # ★ tranche grouping: RawActivity -> Order -> Trade (§5.3 H-1)
├── instruments/     # ★ symbol + wrapper + currency -> Instrument (§5.3 H-2)
├── book/            # positions, cash per currency, P&L, NAV
├── capital/         # ★ the capital base — QA-63
├── reconcile/       # export vs computed book; breaks
├── trades/          # the retrospective log
├── arrival/         # ★ the forward log — arrival quotes (§7, QA-69)
├── journal/         # decision journal
├── attribution/     # performance attribution (reserved desk F8)
└── contracts/       # on-disk shapes
```

---

# 5. THE BROKER EXPORT — what it actually contains

> **Written from the files, not from a description.** Everything below is verifiable against
> `samples/bmo_investorline_transactions/`. **Four of the eight hazards in §5.3 are not handled by
> the current parser.**

## 5.1 Format

```text
Transaction Type=ALL,Product Type=All,Symbol=,From=2026-01-01,To=2026-08-18,,,,,   ← filter echo
Transaction Date,Settlement Date,Activity Description,Description,Symbol,Quantity,Price,Price Currency,Total Amount,Total Currency
----------------,---------------,--------------------,-----------,------,--------,-----,--------------,------------,--------------
2026-02-24,2026-02-24,Dividend,RBC,RY,80,0,,131.2,CAD
```

Ten columns, a filter-echo line above the header, a dashes line below it, and a **UTF-8 BOM**.
`Symbol`, `Price Currency` and `Price` are **empty on cash rows**.

## 5.2 Activity taxonomy — the complete observed set

| Activity | n | Shape |
|---|---|---|
| `Buy` / `Sell` | 68 / 63 | `Quantity` signed (+buy / −sell), `Price`, `Total Amount` = −(Q×P) − commission |
| `Dividend` | 8 | `Quantity` = **shares held**, `Price` = 0, `Total Amount` = cash |
| `Non resident tax` | 3 | negative cash; **15 % of the paired dividend** |
| `Contribution` | 4 | no symbol; **the only place the account type appears** (H-5) |
| `Foreign Exchange` | 2 | **two rows, one per currency**; rate is in the *description text* (H-4) |
| *(blank)* | 1 | **an untyped row** — a government grant (H-8) |

## 5.3 Eight hazards, all present in 149 real rows

### H-0 ⚠ READ FIRST — "CIBC" in this data is **not** the broker

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE BROKER IS **BMO INVESTORLINE**.                             ║
║                                                                  ║
║  "CIBC" appears throughout the export and is CORRECT — it is     ║
║  the CDR ISSUER, inside the instrument DESCRIPTION:              ║
║                                                                  ║
║      MICRON TECHNOLOGY CIBC CDN DEP                              ║
║      SPACETECH CORP(SPACEX) CIBC CDR                             ║
║                                                                  ║
║  CIBC runs the Canadian Depositary Receipt programme. It is a    ║
║  PRODUCT NAME on a security, not the institution holding the     ║
║  account.                                                        ║
║                                                                  ║
║  ★ A product name was read as the institution, and the error     ║
║    propagated into F4, `pipeline/portfolio/ingest.py`,           ║
║    `sdd/specs/README.md`, D-03's V-30 and L4's migration table.  ║
║    All corrected 2026-08-23 (Victor). The legacy docstring in    ║
║    ingest.py is fixed on move (L4 §1.5).                         ║
║                                                                  ║
║  ⚠ IF YOU ARE AN AGENT SEEING "CIBC" HERE: check whether it sits ║
║    in a Description field (issuer, keep) or names the account /  ║
║    export / broker (wrong, fix).                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **RC-36** | ★ **The broker is BMO InvestorLine. `"CIBC"` in this data is the CDR issuer and belongs to the INSTRUMENT, never to the account or the export.** Naming the broker CIBC anywhere is a defect, and it has been made four times |

### H-1 ★ Partial fills — cash is consolidated onto one tranche

One order filled at several prices produces **several rows, most with `Total Amount = 0.00`**:

```
2026-06-16  Buy  SPCX   35 @ 35.00   Total     0.00
2026-06-16  Buy  SPCX   40 @ 37.00   Total -2,706.78
2026-06-16  Buy  SPCX  300 @ 35.00   Total     0.00
2026-06-16  Buy  SPCX  500 @ 37.00   Total -29,018.12
```

Reconstructed: `335 × 35 + 540 × 37 = 31,705`, plus `2 × 9.95` commission = **31,724.90**, which is
exactly `2,706.78 + 29,018.12`. **Two orders, four tranches, two commissions.**

> **A row-by-row ingest gets the cash flow wrong, the trade count wrong, and the commission wrong.**
> `Total Amount = 0.00` is not a free trade; it is a tranche whose cash is booked on a sibling.

#### ✅ Confirmed by the account holder, 2026-08-23

> *"Sometimes you may see a transaction record split 1 buy-order into 2 transactions. I can confirm
> both records are filled in a split of seconds, with identical price, and the transaction fee is
> only once ($9.95)."* — Victor

★ **This CONFIRMS the reconstruction above rather than changing it**, and it upgrades the grouping
key from an inference off four sample files to a stated fact about how the broker reports:

| ID | Rule |
|---|---|
| **RC-37** | ★ **Rows sharing `(account_id, date, symbol, side, price_level)` are ONE order with ONE `$9.95` commission** — confirmed by the account holder, not merely inferred from the sample. The `price_level` in the key is load-bearing: **the same day and symbol at a DIFFERENT price is a different order and carries its own commission.** The H-1 example is two orders (`@35.00`, `@37.00`) of two rows each — **not one order of four rows, and not four trades** |
| **RC-38** | ★★ **Within one order there is no execution variance to measure**: the split rows fill *within seconds, at an identical price*. ⚠ **So the tranche split is a REPORTING artifact, never a source of slippage** — an ingest that treats the two rows as two fills would manufacture a price difference that did not occur |
| **RC-39** | **Commission is `$9.95` per order, flat and confirmed unchanged.** RC-15 still DERIVES it from the residual rather than reading a constant — ★ **the derivation is the check**: a derived value that disagrees with `$9.95` means the grouping is wrong, and that is exactly the signal RC-15 exists to give. **The constant is the expectation, not the input** |

> ★ **RC-38 is the half that matters for QQ-20.** The tranche split was the most plausible remaining
> source of intra-order execution cost in this book, and it is now known not to be one.

### H-2 ★ Same ticker, different instrument — CDRs · **RESOLVED 2026-08-18**

| Account | `Symbol` | `Description` | Price | Currency |
|---|---|---|---|---|
| RRSP | `MU` | `MICRON TECHNOLOGY CIBC CDN DEP` | **17.54** | **CAD** |
| TFSA | `MU` | `MICRON TECHNOLOGY` | **400.61** | **USD** |

A **Canadian Depositary Receipt** — a CAD wrapper on the US stock with an issuer-set share ratio —
versus the stock itself. Same ticker, ~20× price difference.

> ✅ **DECIDED (Victor): a CDR is the same instrument as its underlying.** The analysis side
> (D-01, D-02, D-03, D-04) sees one ticker, one price series, one set of fundamentals — the US
> listing. **There is no ticker collision to resolve in D-07 or D-02**, and no change is needed
> there.
>
> **The split survives in exactly one place: valuation.** D-11 must still know a CDR lot is a CDR,
> because its *unrealized CAD value* cannot be read from the US price. See **§5.6**.

> ★ **This is also where the broker misidentification came from.** F4 and `ingest.py` both say
> *"CIBC Investor's Edge"*. **The broker is BMO InvestorLine.** "CIBC" in the data is the **CDR
> issuer**, appearing in the `Description` of the *instrument*, not the account. A product name was
> read as the institution. **RC-16.**

### H-3 CDRs on unlisted companies

`SPCX` = `SPACETECH CORP(SPACEX) CIBC CDR`. **SpaceX is private**: no US listing, no CIK, no EDGAR
filings, no FMP fundamentals. D-07's source routing (§5.1 case C) would **fail the run** on it —
correctly, but it must be classified as *"CDR on an unlisted issuer"* rather than *"broken ticker"*.

### H-4 FX is two rows, and the rate is in prose

```
2026-06-22  Foreign Exchange  "SELL USD @ 1.3953 (AUTO FX"   −6.27  USD
2026-06-22  Foreign Exchange  "SELL USD @ 1.3953 (AUTO FX"   +8.75  CAD
```

`6.27 × 1.3953 = 8.75` ✓. **The rate exists only inside a truncated description string**, and
**FX-2 requires it recorded** with every converted value. Parsing prose for a load-bearing number is
fragile, and the string is cut off mid-parenthesis.

### H-5 ~~Registered status is not a field~~ — **RESOLVED by naming convention**

The account type appears **only** in the `Description` of a `Contribution` row, so an export window
with no contribution carries no indication whether the account is registered — and **M-4's flag
depends on knowing**.

> ✅ **Closed 2026-08-18.** Exports are now named `TransactionHistory_<TYPE>_<n>.csv` —
> `RESP_1`, `RRSP_1`, `TFSA_1`, `TFSA_2`. **The account type is in the filename**, which is
> configuration in the only place that survives a window with no contributions. RC-18 stands as the
> rule; the convention is how it is satisfied.
>
> ★ **And the answer is uniform: all four accounts are registered.** There is no non-registered
> sleeve. **M-4 therefore applies to the entire book** — every short-hold round trip in this system
> is a registered-account round trip, and there is nowhere to put tactical trading where the CRA
> *carrying on a business* exposure does not apply. See §5.5.

### H-6 The mandate's target behaviour is visible in the data

The RRSP account shows **1-day round trips**: `MU` bought 2026-05-06, sold 2026-05-07; `INTC` and
`SNDK` similar. That is precisely the pattern **M-4** exists to flag, occurring in a registered
account, in the sample.

### H-7 Commission is **$9.95**, not $10.00

41 trades show a residual of exactly `−9.95`. `backtester.py` hard-codes `FLAT_TRADE_FEE_DOLLARS =
10.0`, and **`tests/test_flat_trade_fee.py` asserts it as "broker reality, not a modelling
assumption"** — a test that enforces a number the broker does not charge.

> Small in dollars, instructive in kind: the "reality" constant was never checked against a
> statement. It also shifts §5.8's `δ_floor` slightly (`$19.90` round trip, not `$20.00`).

### H-8 An untyped row

One row has a **blank** `Activity Description` — a RESP government grant. Under **P5** an
unclassifiable activity **must raise**, never be dropped or defaulted to a neutral type.

## 5.6 ★ Marking a CDR lot — the one thing the "identical" decision does not cover

H-2 collapses CDR and underlying **for analysis**. It cannot collapse them **for valuation**,
because a CDR lot's unrealized value is in CAD and its market price is not obtainable.

### The constraint, measured

```text
FMP Starter has NO Canadian equity coverage at all.
  RY.TO  SHOP.TO  ENB.TO  XIU.TO  MU.NE   ->  all 402, on retry.
```

So there is **no CDR price feed**, and there is no partial one either — this is not a CDR gap, it is
a whole-market gap. Adding a source is an **L0 §2.2 decision** (EDGAR + FMP only), not an
implementation detail.

### Therefore: synthesise from the underlying, never reconstruct the price

```
    unrealized_cad(t) = qty_cdr × entry_price_cad × [ usd_close(t) / usd_close(entry_date) ]
```

**Apply the underlying's USD return to the CAD cost basis.** Four reasons this is the right form:

1. ★ **It is ratio-agnostic.** It never needs CIBC's CDR share ratio — which is precisely the number
   FMP cannot supply and which CIBC adjusts to pass through hedge costs and dividends. A method that
   reconstructs price *from* the underlying needs the ratio; a method that tracks *return from the
   CAD cost basis* does not.
2. **It matches how CIBC's CDRs are built** — the programme is currency-hedged, so the CDR is
   designed to deliver the USD return without the FX leg.
3. **It fits the data better**, though not decisively — see below.
4. **It is self-checking.** Every closed round trip yields the true CAD exit value from the sell
   row, so the realised error is observable per position (RC-27).

### What the eight closed round trips actually show

| Reference | mean signed error | mean abs error | sd |
|---|---|---|---|
| **underlying USD return** *(the recommended method)* | **−0.08 pts** | 2.16 | 2.47 |
| unhedged CAD translation (`usd × fx`) | −0.98 pts | 2.10 | 2.44 |

> **Read this honestly.** The mean signed error is **12× smaller** against the USD return, which
> favours the hedged form. But the **spread is ~2.2 pts either way**, so a single hold cannot
> distinguish the two and eight barely can. Most of that spread is **execution price vs daily
> close**, not method error — the transaction rows carry fills at unknown times of day, compared
> against closes.
>
> **The choice is therefore made on construction and convenience, corroborated but not proven by
> the data.** That is a weaker claim than "measured", and it is stated as such (QA-23).

| ID | Rule |
|---|---|
| **RC-26** | ★ A CDR lot is **marked by applying the underlying's USD return to its CAD cost basis** — never by reconstructing a price from the underlying, which would require the unobtainable share ratio. The lot records `wrapper=cdr` and its `entry_price_cad` and `entry_date` for exactly this purpose |
| **RC-27** | ★ **Every closed CDR round trip records its realised tracking error** against the synthetic mark. The method is self-checking, and **a drifting mean is the signal that the hedged assumption is wrong** — which is the only way this will ever be settled properly |
| **RC-28** | Analysis identity and settlement identity are **separate fields**: `analysis_symbol` (the US ticker, what D-02/D-03/D-04 see) and `instrument_id` (what the book holds). **One ticker upstream, two lots downstream** |

## 5.5 ★ All four accounts are registered — and that is the strongest fact in the file

| Account | Type | Registered |
|---|---|---|
| `RRSP_1` | Retirement | ✔ |
| `RESP_1` | Education (beneficiary) | ✔ |
| `TFSA_1` | Tax-free | ✔ |
| `TFSA_2` | Tax-free | ✔ |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THERE IS NO NON-REGISTERED SLEEVE. M-4 IS BOOK-WIDE.            ║
║                                                                  ║
║  M-4 flags short-hold round trips IN REGISTERED ACCOUNTS. With   ║
║  every account registered, that is not a subset rule — it is     ║
║  the whole book, always.                                         ║
║                                                                  ║
║  This materially strengthens ground (a) of the horizon decision  ║
║  (L1-quantitative-analysis §5.6), which after ground (b)'s       ║
║  collapse is the only substantive ground left standing.          ║
║                                                                  ║
║  It also means the sample's 1-day MU/INTC/SNDK round trips       ║
║  (H-6) are not an edge case to be flagged occasionally. They     ║
║  are the behaviour the mandate is aimed at, in the only kind of  ║
║  account this fund has.                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **RC-25** | ★ **The M-4 flag has no exempt population.** Any design that routes tactical or short-hold activity to a "non-registered sleeve" is describing an account that does not exist |

## 5.4 What the export does **not** contain

| Missing | Consequence |
|---|---|
| **Any execution timestamp** — `Transaction Date` is a **date** | ★ Execution cost is **not retrospectively recoverable** (QQ-20). §7 |
| A reference/arrival price | ★ Same |
| Account type | H-5 |
| Instrument identity beyond a truncated name | H-2, H-3 |
| An explicit commission field | H-1, H-7 — it is inferred from a residual |
| Cash balance | The book is a *reconstruction*, never a read |

---

# 6. FOUR ACCOUNTS, ONE BOOK

Four accounts exist; three were sampled — **RRSP, RESP, TFSA**, plus one unsampled.

| ID | Rule |
|---|---|
| **RC-1** | Every record carries its `account_id`. **There is no unattributed activity** |
| **RC-2** | **Aggregation across accounts is explicit and currency-aware** (INV-001, M-5). A "total book" that silently sums CAD and USD is a defect |
| **RC-3** | ★ **A missing account fails the run.** Three exports where four accounts exist is an **incomplete book**, not a smaller one — and every exposure, concentration and drawdown figure computed from it is wrong in an unstated direction (INV-025) |
| **RC-4** | An **RESP is not the fund.** It has a beneficiary and its own mandate; it is recorded, and **excluded from the fund's performance and exposure** unless Victor says otherwise. **QC-1** |

---

# 7. EXECUTION COST — **not measured, by decision**

> **QC-5 is closed "won't do" (Victor, 2026-08-18) and RECONFIRMED 2026-08-23** after
> `L3-build-sequence.md` **BS-3** was found to contradict it — BS-3 made arrival capture *first*
> among B1's clock-bearing obligations while this section had already cancelled it. **BS-3 is
> amended; QC-5 stands.**
>
> v0.1.0 specified a two-log structure and an arrival-quote capture, because QQ-20 needs
> `(fill − arrival)/arrival` and the broker export supplies only the fill. **That capture will not
> be built.**
>
> ★ **The 2026-08-23 confirmation changed the argument from SCALE to STRUCTURE.** v0.2.0 rested on
> order size — 22 bps of commission at a median $8,941 order dwarfs any plausible slippage, which is
> a *"not worth measuring"* argument. **RC-38 is stronger: the tranche split fills within seconds at
> an identical price, so there is no intra-order gap to measure at all.** A capture built for it
> would record a constant. ⚠ *(The submission→fill gap remains unmeasured; at effectively
> instantaneous fills on liquid names it is assumed negligible, and that assumption is stated here
> rather than hidden.)*

The consequences are stated here rather than left to be rediscovered:

| Consequence | |
|---|---|
| **QQ-20 closes as *will not measure*** | Not "not yet measured". Spread and slippage have no source and no plan for one |
| **Ground (b) of the horizon decision is permanently indeterminate** | It was already ⏸ suspended pending QQ-20 (`L1-quantitative-analysis` §5.6a). It now stays there. **The decision rests on ground (a) — M-4 — alone**, which §5.5 has just strengthened |
| **`δ` is set from its commission floor, permanently** | `δ = rt/β` with `rt` = commission only. At real order sizes that is **0.4 – 0.9**, not the 1.92 computed from the hard-coded `$20 k / 5` book |
| **Trade rows still declare their quality** | `execution_cost_available: false`, always. **The field stays** — DE-35's rule holds even when the answer is permanently "no" |

**And the decision is defensible at this scale.** At a median order of **$8,941** the round trip is
**22 bps**; at the $29,018 maximum it is **6.9 bps**. Building an execution-quality programme to
measure a cost that small, for one person placing a handful of orders a week, is effort with no
plausible payoff. *(That is a scale argument, not a correctness one — it would not hold at
institutional size, and the reasoning should not be reused there.)*

| ID | Rule |
|---|---|
| **RC-5** | *(revised v0.2.0)* Every trade row carries `execution_cost_available` — **permanently `false`** absent arrival capture. `execution_cost()` returns **`NotMeasurable` as a value, never zero and never an exception** (QA-70) |
| **RC-6** | ⚠ *(defined in the audit.)* **A trade row's account is a required field, not an inference.** Registered status is not derivable from the instrument or the symbol (§5.5), and every M-4 check depends on it |
| ~~**RC-7**~~ | ⚠ **SUPERSEDED → RC-7a** (2026-08-23). It required every trade row to carry `log_segment ∈ {retrospective, forward}`. ★ **With arrival capture retired, `forward` is unreachable, and a field with one reachable value cannot discriminate anything** |
| **RC-7a** | ★★ **`log_segment` is retired; `execution_cost_available` STAYS — and the asymmetry is the point.** ⚠ **A one-valued enum asserts nothing**: `log_segment: "retrospective"` on every row tells a reader only that the field exists. **A boolean that is permanently `false` asserts something real** — *we looked, and the answer is no* — which is DE-35's rule (`UNCHECKED` is never "none") doing its job. **Retire the field that cannot discriminate; keep the field that records a finding** |
| **RC-8** | *(revised)* D-11 publishes **no** slippage estimate. A domain that cannot measure a quantity does not publish a proxy for it |

---

# 8. RECONCILIATION

| ID | Rule |
|---|---|
| **RC-9** | The book is **derived from activity and reconciled against the export**, never read from it — no cash balance is supplied (§5.4) |
| **RC-10** | `sum(positions) + cash == NAV` per currency, per account, every day (INV-025). A break **raises**; it is never absorbed |
| **RC-11** | Re-ingesting the same export is **idempotent** — file-hashed, and a changed hash for a covered window is a **restatement**, recorded not overwritten (DE-24's shape) |
| **RC-67** | ★ **A dropped export can be CHECKED without running the pipeline** — `python -m src.recording.check`. For every discovered account it reports the file, its date window, row and order counts, derived positions and cash per currency, and **names any refusal** (a truncated window — RC-45; an unknown activity — RC-13; another account's row — RC-48) instead of stopping at the first. ⚠ *Added 2026-10-06 (Victor, L9 §11 K1):* the CSV drop is how D-11 is fed, and until now a bad file surfaced only inside a pipeline run. **Read-only by default**; it records only when asked (RC-68). Exit status is non-zero if any account refused |
| **RC-68** | ★★ **RC-11 built: the ingest log.** `.state/broker/ingest_log.jsonl`, **append-only** — one entry per account per recording: `file_hash`, the date window, and a **digest of every row** (verbatim fields; a multiset, because two identical tranches are legitimate). Compared with the last entry for that account: **identical hash → no-op** (AC-11.9) · rows **after** the previous window → *new activity* · rows **inside** the previously covered window that disappeared or appeared → a **RESTATEMENT**, reported and recorded, **never overwritten** (DE-24's shape) · a window that now starts **later** than before → reported (history the new file no longer carries). ⚠ *Added 2026-10-06 (Victor, L9 §11 K2):* `file_hash()` existed and nothing stored it, so a silent BMO correction of an old row simply replaced it. Recording is **explicit** (`--record`), never a side effect of reading |
| **RC-69** | ★ **A run directory is one that holds a CT-11.7 file (`manifest.json` or `outcome.json`); anything else under `.state/runs/` is not a run, and a subdirectory inside a run is not a file of it.** ⚠ *Added 2026-10-20 (`DX-173`), found on the first live card:* the thesis runners write their traces (`trace.jsonl`, `trace/payloads/…`) under the same root, and `read_run` read the `trace` FOLDER as a file — `IsADirectoryError` failed the card's `record` job and the index rebuild. The traces stay where they are (F2 owns them); the run store just stops reading them as runs |
| **RC-12** | **Missing is `null`, never zero** (DE-14). A zero `Total Amount` is a *tranche* (H-1), not an absence — the two must not collapse |
| **RC-13** | An **unclassifiable activity raises** (H-8, P5). No neutral default, no silent drop |
| **RC-14** | **Trades are grouped into orders before anything counts them** (H-1). A tranche is not a trade; the commission residual is the evidence |
| **RC-15** | **Commission is derived, not assumed** — `Total Amount − (−Q×P)`, per order (H-7). A hard-coded fee constant is a modelling assumption wearing the word "reality" |
| **RC-16** | *(revised v0.2.0)* **Instrument identity is `(symbol, wrapper, venue_currency)` in the BOOK; `analysis_symbol` collapses to the underlying US ticker everywhere else** (H-2, RC-28). A CDR and its underlying are the same *company* and different *lots* — one ticker for D-02/D-03/D-04, two lots for D-11 |
| **RC-17** | The **FX rate is recorded with every converted amount** (FX-2). Where it exists only in prose (H-4), the parse is **checked against the paired legs** — `|leg_usd × rate − leg_cad| < tolerance` — and fails loud on mismatch |
| **RC-47** | ★★ **A book may ORIGIN from a stated opening snapshot, and the snapshot is EVIDENCE — never derived from a later state.** ⚠ *Added 2026-08-25: **RC-9 derives the book from activity and RC-45 shows a truncated window derives the wrong lot**, so a book whose activity does not reach back to inception needs a starting balance. Without one the only alternatives are a deep re-export or a wrong book.* ★ The snapshot is **read off a broker statement** at a stated date and carries it; the book is then `opening + activity`, and **RC-10 still has to balance at the end** — the snapshot changes where the derivation starts, not whether it is checked. ⚠ **It may NOT be back-computed as `current − activity`.** That makes the current holdings an input rather than an output, so the forward replay reproduces them **by construction** and checks nothing — *the arithmetic would look perfectly healthy* (RC-45's shape, one level up). ★ **A snapshot is preferred over a partial window and inferior to a full one**, and the artifact says which was used |
| **RC-55** | ★★ **The column layout can change WITHIN one file.** ⚠ *Measured 2026-08-25:* `TransactionHistory_TFSA_2.csv` carries **75 ten-column rows and 74 thirteen-column rows, interleaved** — newer activity appended from a differently-shaped export. ★ Reading the header once and applying it to every row puts `Quantity` where `Activity Description` belongs; the first symptom was **an activity called `'1000'`**. **Each row is mapped by its own width**, and RC-41's rule becomes: read the header, then check every row against it |
| **RC-56** | ★★ **A blank `Activity Description` is not an absence — it can carry real cash.** ⚠ *Measured:* three RESP rows read `BENE: 01 … GRANT REC` with **no activity type and $500 each**. Skipping them silently lost **exactly $1,500**, and the account missed its stated balance by that amount and no other. ★ The mapping from description to activity is **DECLARED DATA** (`BLANK_ACTIVITY_BY_DESCRIPTION`), not an inference — a reader can see which rows it claims and disagree. ⚠ **A blank activity carrying cash that the table does not claim RAISES** (RC-13), because the alternative is losing money quietly |
| **RC-57** | ✅ **RC-10 CHECKED AGAINST EXTERNAL TRUTH, 2026-08-25 — all four accounts reconcile to the cent.** Derived cash vs the balances BMO shows: `TFSA_1 25.30 CAD / 832.81 USD`, `TFSA_2 30.86 / 151.22`, `RRSP_1 18.83 / 0`, `RESP_1 45.43 / 0`. ★ **This is the first time any number in this system has been checked against something outside it** (F3 Tier 1, `CT-3.2` in `L5-inherited-defects.md` §5) — and it validates the whole chain at once: the per-row layout mapping, twelve activity classifications, order grouping, the derived commission and the cash accumulation. ⚠ **RC-51 still stands for POSITIONS**: the cash side is now reconciled, the market-value side is not |
| **RC-51** | ★★ **A transaction export carries NO BALANCE, so RC-10 has nothing to reconcile against.** ⚠ *Found 2026-08-25 wiring the book into D-05.* `positions + cash == NAV` is the check; **derive all three from the same rows and it passes by construction and checks nothing** — the same tautology RC-47 refuses on the opening side. ★ So a book built from activity alone is **`UNRECONCILED`** until a reported NAV or cash balance is supplied from outside it, and **D-05 correctly refuses it** (RK-29). ⚠ `UNRECONCILED` is *not* a third value of `CT-11.4.reconciled` — that field still has exactly two (RC-10, RK-0); it is carried on the result of the derivation |
| **RC-58** | ⏸ **POSTPONED by Victor, 2026-08-25: Canadian-listed stocks and CDRs are not valued until the rest of the code is complete.** ★ The *positions* are still derived, grouped and reconciled — **only the market-value step is deferred**, and it is deferred for a reason outside the code: **the FMP plan covers US listings only** (every `.TO` / `.NE` symbol returns 402), so `BBD.B`, `MDA` and `BMO` have no quote, and `MRV`/`SPCX` have no usable underlying. ⚠ **A CDR is a SEPARATE STOCK that tracks a US underlying; its price is NOT the underlying's price** (Victor) — so nothing may substitute one for the other. RC-52's cost-basis-times-return method tracks the *return*, never the price, and stays valid; it is simply not exercised while this is postponed |
| **RC-52** | ★ **A CDR is valued from its CAD cost basis scaled by the UNDERLYING'S USD RETURN — never reconstructed from the ratio.** It is **ratio-agnostic**, and CIBC's ratio is *precisely the number FMP cannot supply* and which CIBC adjusts to pass through hedge costs and dividends. ⚠ It needs an underlying with a USD price, so **`MRV` and `SPCX` cannot be valued this way** |
| **RC-53** | ★★ **A bare ticker is AMBIGUOUS ACROSS VENUES, and the vendor answers with the US listing.** ⚠ *Measured 2026-08-25:* `MDA` returned **MDA Space Ltd, NYSE, USD** and `BMO` returned **Bank of Montreal, NYSE, USD** — the right companies on the **wrong venue, in the wrong currency**, for positions held on the TSX in CAD. ★★ **This is more dangerous than the 402s**: a plan-gated symbol refuses loudly, while a same-named US listing returns **a plausible number in the wrong currency**, and a CAD book that adds it is wrong by the FX rate — silently. ⚠ The quote's currency must match the venue's, or the position is **unavailable, never converted** (FX-3's shape) |
| **RC-54** | ⚠ **Where the vendor and this spec disagree about a SECURITY, neither is assumed right.** *Measured:* §5.3 records that **SpaceX is private — no US listing, no CIK, no EDGAR** — and FMP answers `SPCX` with *"Space Exploration Technologies Cor, NASDAQ, USD"*. ★ D-11 does not silently pick the vendor: `SPCX` is **unpriceable until the disagreement is resolved** (F3 §4c, carried in `L5-inherited-defects.md` §5). ⚠ `QUOTE_CONTRADICTS_SPEC` is **a list of open disagreements, not a blocklist of bad tickers** |
| **RC-48** | ★★ **Where the export carries account columns, a row belonging to ANOTHER account is refused — never absorbed.** ⚠ *Measured 2026-08-25 on the full-history exports:* `TransactionHistory_TFSA_2.csv` is about account `23280100` (146 rows) and contains **one `Joint` row, account `23098925`**. ★ Booking it into the TFSA attributes another account's cash to this one — **$0.50 here, and the principle is RC-1's**: there is no unattributed activity, and there is no *mis*-attributed activity either. ⚠ Skipping such a row must be **deliberate and visible** (`strict_accounts=False`), never the default |
| **RC-49** | ★★ **`Disbursement` moves SHARES and carries no cash, and its sign is taken from the file — never inferred.** ⚠ *Measured:* `RESP_1 · PLTR CDR · 390 @ 0 · total 0`. **Classifying it as cash-only loses 390 shares while the cash still balances** — RC-45's failure shape from a different cause. ★ BMO signs dispositions negative throughout, so a positive quantity is shares arriving; **the book reconciles on that reading and not the other**, which is evidence rather than a guess |
| **RC-50** | ★ **Four years of history contained FIVE activity types that eight months did not** — `Harmonized sales tax`, `Admin fee charged`, `Withdrawal`, `Disbursement`, `Online banking`. ⚠ Each one **stopped the run on first parse** (RC-13) instead of vanishing from a book that has to balance. ★ *This is the argument for failing loud made twice over*: the same rule caught `Interest` in the short window and five more in the long one, and **not one of them was predictable from the shorter file** |
| **RC-45** | ★★ **A position cannot be derived from a PARTIAL activity window, and the export does not say so.** ⚠ *Measured 2026-08-25:* the four exports cover `From=2026-01-01`, and replaying them yields **negative quantities** — `PLTR RESP −520`, `GOOG TFSA_2 −30`, `BBD.B RRSP −26`. ★ **Those are not shorts.** They are positions opened *before* the window whose sells appear and whose buys do not. **RC-9 derives the book from activity, so an activity window that does not reach back to a lot's opening derives the wrong lot** — and the arithmetic looks perfectly healthy while doing it. ⚠ A derived quantity below zero is therefore **evidence of a truncated window**, not a short, and it must **block** rather than book (P5, RC-10) |
| **RC-46** | ★ **`instrument_id` uses `|`, because `BBD.B` is a real holding.** A dotted id — `BBD.B.COMMON.CAD` — cannot be split back into `(symbol, wrapper, venue_currency)` by any consumer, and RC-16 makes that triple the book's identity |
| **RC-41** | ★★ **The export has TWO column layouts, so the header is READ, never assumed.** ⚠ *Measured 2026-08-25:* `TFSA_1`, `RRSP_1`, `RESP_1` carry **10 columns**; **`TFSA_2` carries 13** — it inserts `Account name`, `Account type`, `Account number` after `Settlement Date`. ★ **A positional parser reads `Account name` where `Activity Description` should be and silently mis-books every row of that file.** It also hid an activity type: a column-3 survey of all four files reported six activities and **missed `Interest`**, which RC-13 then caught on the first real parse |
| **RC-42** | ★★ **An order fills at SEVERAL prices, so price is NOT part of the order key.** ⚠ *Measured:* `NVDA CDR 2026-04-29` filled `200 @ 47.68` and `10 @ 47.69`; keyed on price those are two orders with residuals `9.48` and `0.47`, and **grouped they are one order with a residual of exactly `9.95`.** ★ So the notional is `Σ|qᵢ|·pᵢ` **per tranche** — never `Q_total × p̄`, which would move the notional and take the derived fee with it |
| **RC-43** | ★★ **The flat commission is `9.95` in BOTH currencies, measured — and a residual that is a MULTIPLE of it means two same-day orders were merged.** ★ Over all **137 orders** in the four exports: `9.95` exactly ×100, `0.00` ×2 (**BMO charges nothing on its own ETFs**, ZCN), and `19.90` ×1 — `SPCX 2026-06-16`, four tranches, **two orders**. ⚠ **The export carries no order id**, so the fee is the *only* evidence the merge happened, and `implied_order_count` reports it rather than hiding it |
| **RC-44** | ⚠ **USD SELLS carry an extra charge above the flat fee and WE DO NOT KNOW WHAT IT IS.** *Measured:* `MU −23 → 10.13`, `INTC −115 → 10.39`, `ARM −70 → 10.71`, `ENB −220 → 11.30` — every order exceeding `9.95` by more than price-rounding explains is a **USD sell**. ★ A US regulatory transaction fee (SEC Section 31, sells only) is the obvious candidate and **does not fit the magnitudes, so it is not asserted.** ⚠ The excess is carried as **`residual_unexplained`** and never absorbed into a tolerance — *a plausible reason attached to an unexplained residual is strictly worse than the honest gap* (D-01 **RA-79**, applied to fees). **QC-7** |
| **RC-18** | **Account type is configuration** (H-5), never inferred from a `Contribution` description that may be outside the window. **M-4's flag depends on it** |

---

# 9. THE CAPITAL BASE — closing QA-63

**Every percentage cost figure in this repository is a function of a number that is currently the
literal `20000.0` at `backtester.py:107`.**

| ID | Rule |
|---|---|
| **RC-19** | ★ D-11 publishes `capital_base(account_id, as_of)` and `capital_base(as_of)` for the fund, **per currency and in base** (M-5). It is **read from the book**, never configured, never hard-coded |
| **RC-20** | A backtest or cost figure **states the capital base it assumed** (QA-11, QA-48). Two figures with different bases are not comparable |
| **RC-21** | The capital base is **point-in-time**: `capital_base(as_of)` returns the book as it was, not as it is (INV-1). A cost percentage computed against today's capital and applied to a 2024 backtest is a look-ahead |

> **What this unblocks the day it lands:** `δ_floor = rt/β` becomes a real number rather than an
> illustration (§5.8), QA-64's horizon-invariance claim becomes checkable, and every drag figure in
> §5.6a stops being parameterised by an unknown.

---

---

# 7Z. ★ WHAT D-11 RECEIVES FROM D-12 AND D-08

> ⚠ **Added after a consistency audit.** This spec predates **D-12 Decision** (L0 v0.17.0) and
> **D-08's RunOutcome**, both of which write into the record.

| ID | Rule |
|---|---|
| **RC-31** | ★ **D-11 stores `CT-12.2 VetoedCandidate` — the counterfactual arm** (D-12 **DN-19**). Append-only and never revised (**DN-21**): a rejected-name history that can be edited is the most tempting record in the system to edit |
| **RC-32** | ★ **Vetoed candidates are marked to market on the SAME horizon and the same open-anchored basis as acted-on ones** (D-12 **DN-20**, D-03 QA-71), or the two arms are not comparable and the gate stays unfalsifiable |
| **RC-33** | D-11 stores **D-08's `CT-8.2 RunOutcome`**, including `INCOMPLETE` and `BLOCKED_PRECONDITION` terminal states. ★ **A failed run is a record, not an absence** (OR-19) |
| **RC-34** | ★ **An override of a D-12 `VETO` is journalled** with the verdict, the binding gates and the human's stated reason (**DN-16**'s companion). The system never prevents the override; it records that it happened |
| **RC-35** | ★ **D-11 writes; D-12 does not.** D-12 may invoke a D-11 write and may never perform one (**DN-31**'s sibling, and the same boundary ST-9 draws for D-09) |
| **RC-59** | ★★ **Every run persists a RUN ARTIFACT, and a failed run persists one too.** ⚠ *Added 2026-08-26: **RC-33 has said this since v0.5.0 and nothing implemented it.** `ManifestStore` and `JournalStore` were both built and **neither was ever called** — every run's manifest, recommendation, card and thesis evaporated when the process exited.* ★ **P6 is constitutional and was unmet**: *anything sent to the user must be viewable later without depending on a live server*. ⚠ It also made every measurement in these specs untestable — **RM-2/RM-3 base rates, DN-17's veto rate, DN-29's liveness monitor and D-01 §7.4's monitors all need run history, and there was none** | 
| **RC-60** | ★ **The artifact is append-only and immutable: a run_id is written ONCE.** A rerun produces a **new** run_id, exactly as **OR-13** already requires of the manifest. ⚠ *Overwriting would let a run's recorded inputs be adjusted to match its outputs*, which is the one thing a reproducibility record must make impossible — and the temptation is highest on the record that says a verdict was wrong |
| **RC-61** | ★★ **A thesis is stored under its `bundle_hash`, and an unchanged bundle REUSES it rather than re-authoring.** Three Opus passes measured **$1.34** on 2026-08-26, so a daily run on an unchanged filing set would pay it again for evidence that did not move. ⚠ **The obvious objection is wrong and worth stating:** *does caching destroy RM-1's variance measurement?* ★ **No — RM-1's k runs happen INSIDE one authoring event**, and GW-8 sets `temperature = 0` so cross-run sampling variance is not the measurement (RA-61's perturbation probe replaced it, v0.4.0). ★ Reuse is the **caller's** decision, never the store's: the store accumulates every authored thesis, and a forced re-author is always available |
| **RC-62** | ★★ **The run record names what produced it.** D-03's `Nomination` is persisted inside `recommendation.json` — the ranked slate, `excluded[]` **with reasons**, `universe_n` and `model_artifact_id`. ⚠ *Measured 2026-08-27:* `grep` for the promoted model's hash across a complete run directory **found nothing** — the artifact of record could not answer *"what made this pick?"*, which **QA-121** requires and **INV-2** rests on. ★ The exclusions are the visible half: without them a reader cannot tell a name that was **beaten** from one that was **barred** (QA-125) |
| **RC-63** | ★ **A delivery writes `delivery.json` into the run directory; a run that did not deliver writes none.** ⚠ **Absence means not-delivered and never unknown** — DE-35's distinction, and the reason an empty file or an `outcome: ""` placeholder is refused. ★ It is written **after** the send by D-11, from the `Delivery` D-09 returns (CT-9.3): *D-09 delivers, D-11 records, D-08 wires* — no domain does two of the three |
| **RC-64** | ★ **The index carries `universe_n`, `excluded_n`, `model_artifact_id` and `delivery_status`.** ⚠ Without `excluded_n` the exclusion rate is unmeasurable, which is **RC-59's own argument** one column over: *an index that held only successes would make the base rates measure the wrong population.* ★ Still **derived** — CT-11.7's index is rebuildable from the directories and never the record |
| **RC-65** | ★★ **The account set is DISCOVERED from the export directory, never listed in code.** ⚠ `ACCOUNTS` was a hardcoded 4-tuple, so a fifth statement dropped into the directory was **silently ignored** — not read, not refused, not mentioned, and the new portfolio simply would not exist. ★ **H-5 already established that the filename carries the account** (`TransactionHistory_<ACCOUNT_ID>.csv`, and the registered TYPE is the prefix), so the directory is a sufficient source and a second list in code can only disagree with it. ⚠ **An empty directory RAISES** rather than deriving an empty book — *"no accounts found" and "this book holds nothing" are different facts*, and `RK-5`'s aggregation rule means the second would silently withhold everything while looking healthy |
| **RC-66** | ★ **The exports live in `.state/broker/bmo_investorline/`, outside the spec tier.** ⚠ `EXPORT_DIR` previously pointed into `sdd/design/rel6_design/samples/` — the **book of record** sat in the tier that governs the code, inside a **release-scoped, frozen** design directory, under a name (`samples/`) that says *fixture*. ★ `.state/` is already git-ignored, so real broker statements cannot enter history (`DX-5`), and `$BMO_STATEMENTS_DIR` still overrides for tests. ⚠ The old path is still read as a **fallback** so an unmigrated checkout degrades to working rather than to empty |

# 10. CONTRACTS

> **ID-collision notice.** `AC-11.k` / `CT-11.k` key `n` on **D-11**. No `F11` exists, so this
> family is currently **unambiguous** — unlike D-01/F1, D-02/F2, D-03/F3 and D-04/F4 (L0 §16.4).

## CT-11.1 — RawActivity (parquet, append-only)

`(account_id, file_hash, row_ordinal, transaction_date, settlement_date, activity, description,
symbol, quantity, price_minor, price_currency, total_minor, total_currency, ingested_at)`

**Verbatim.** Prices and totals are `Money` (CT-M.1). Nothing is normalised here — normalisation is
`orders/` and `instruments/`, and keeping the raw row is what makes a re-derivation checkable.

## CT-11.2 — Order / Trade (parquet)

`(order_id, account_id, date, instrument_id, side, quantity, avg_price_minor, currency,
gross_minor, commission_minor, net_minor, tranche_count, execution_cost_available)`

`tranche_count > 1` records H-1 — ★ **and per RC-38 it is a REPORTING artifact, never a price
spread**: the tranches filled within seconds at one price. `execution_cost_available` is
**permanently `false`** (RC-5) and stays, because it records a finding rather than a category
(RC-7a). ⚠ `log_segment` was here until 2026-08-23 and is retired with RC-7.

## CT-11.3 — Instrument (JSON)

`(instrument_id, symbol, wrapper ∈ {none, cdr, adr}, issuer, venue_currency, underlying_symbol,
underlying_cik | null, ratio | null)`

`underlying_cik = null` with `wrapper = cdr` is the **H-3 unlisted case** — a stated fact, not a
lookup failure.

## CT-11.4 — BookState (JSON, per account per day)

`(account_id, date, positions[], cash_by_currency{}, nav_by_currency{}, nav_base, fx_rate_used,
capital_base, reconciled ∈ {ok, break}, breaks[])`

`nav_base` is **`null` when no FX rate is available** — never a guess (FX-3, inherited from
`snapshot.py`).

## ~~CT-11.5 — ArrivalQuote~~ — ⚠ **RETIRED 2026-08-23** *(tombstone, T-2)*

> **Superseded by the QC-5 decision, confirmed by Victor 2026-08-23.** The contract described a
> capture that **§7 already said would not be built** — it survived v0.2.0's re-scope as an artefact
> of the v0.1.0 design and read as a commitment.
>
> ★ **RC-38 is what closed it structurally rather than by cost.** The tranche split was the last
> plausible source of intra-order execution variance, and the account holder confirmed those rows
> fill *within seconds at an identical price*. **There is no gap left to measure**, so a capture
> built to measure one would record a constant.
>
> **The row stays** (T-2 — a vanished ID leaves dangling references that resolve to nothing and are
> never noticed). Nothing may implement it.

## CT-11.6 — JournalEntry (JSON, append-only)

`(date, ordinal, ticker, action, rationale, thesis_version | null, overridden_flags[], author)`
— **append-only, never revised** (INV-006).

---

## CT-11.7 — RunArtifact (JSON per run, append-only)

`.state/runs/<run_id>/` holding `manifest.json`, `outcome.json`, `recommendation.json`,
`thesis.json`, **`delivery.json`** and the D-09 renderings (`<TICKER>_<as_of>.md` / `.html`).

★ **A directory per run, not a row per run**, because the renderings are the part **P6** is about
and they are documents. The tabular view a measurement needs is `runs.parquet` — one row per run
`(run_id, as_of, job_graph_id, status, ticker, verdict, actionable, alerts_status, bundle_hash,
thesis_verdict, agreement, spend_usd, universe_n, excluded_n, model_artifact_id, delivery_status)` —
derived from the directories and **rebuildable from them**, so the index is a convenience and never
the record.

⚠ `status` carries `INCOMPLETE` and `BLOCKED_PRECONDITION` verbatim: **a failed run is a record,
not an absence** (RC-33, OR-19), and an index that held only successes would make the base rates
measure the wrong population.

### ★★ `recommendation.json` carries the NOMINATION — v0.12.0

```text
╔══════════════════════════════════════════════════════════════════╗
║  MEASURED 2026-08-27 on a real run directory:                    ║
║                                                                  ║
║    $ grep -rl "85b75744" .state/runs/<run_id>/                    ║
║    (nothing)                                                     ║
║                                                                  ║
║  The run record could NOT NAME THE MODEL THAT PRODUCED THE PICK.  ║
║  `recommendation.json` held one candidate — ticker, rank,         ║
║  ranked_quantity — and `manifest.json` held `inputs: []` and      ║
║  `code.git_sha: ""`.  QA-121: *a nomination that cannot be        ║
║  traced to what produced it cannot be re-run* (INV-2).           ║
╚══════════════════════════════════════════════════════════════════╝
```

D-03's `Nomination` (**CT-3.4**) is persisted **inside `recommendation.json`** under a
`nomination` key, carrying the full ranked slate, `excluded[]` with reasons, `universe_n`,
`model_artifact_id` and `horizon_set`.

⚠ **D-11 composes that file from the two objects at write time; D-12's `Recommendation` class
does not gain the fields.** ★ One file on disk, and the two domain contracts stay independent —
adding D-03's slate to D-12's dataclass would make the recommendation's schema depend on quant,
and the reader gaining a file is not a reason for the writer to gain a dependency.

★ `excluded[]` is the point of the exercise (**QA-125**): *"was this name barred, or merely
beaten?"* is unanswerable from a directory that records only the winner.


# 11. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `ingest(paths)` | `IngestReport` | all four accounts or it raises (RC-3) |
| `orders(account_id, window)` | `list[Order]` | tranche-grouped (RC-14) |
| `instrument(symbol, description)` | `Instrument` | resolves the CDR/underlying split (RC-16) |
| `book(account_id, as_of)` | `BookState` | reconciled or raises (RC-10) |
| `capital_base(as_of, account_id=None)` | `Money` | ★ QA-63, point-in-time (RC-21) |
| `trade_log(window, segment)` | `TradeLog` | segment-tagged (RC-7) |
| `execution_cost(window)` | `ExecCostReport \| NotMeasurable` | ★ **`NotMeasurable` is a first-class return**, not an exception |
| `journal(window)` | `list[JournalEntry]` | |

---

# 12. BUSINESS RULES

| ID | Rule |
|---|---|
| **RC-1…RC-4** | Accounts — §6 |
| **RC-5…RC-8** | The two logs — §7 |
| **RC-9…RC-18** | Ingestion & reconciliation — §8 |
| **RC-19…RC-21** | The capital base — §9 |
| **RC-22** | D-11 imports **no** analytical domain and **not D-09** (ST-9) |
| **RC-23** | Every monetary value is a `Money` (INV-001). The export mixes CAD and USD **within one account** — an untagged amount is a defect, not a default-to-base |
| **RC-24** | The journal is **append-only and never revised** (INV-006). A rationale edited after the outcome is known is worthless as evidence |

---

# 13. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `REC.INGEST.UNKNOWN_FORMAT` | ERROR | header does not match a registered format (RC-3) |
| `REC.INGEST.MISSING_ACCOUNT` | ERROR | fewer exports than known accounts — **incomplete book** (RC-3) |
| `REC.INGEST.UNTYPED_ACTIVITY` | ERROR | blank `Activity Description` (H-8, RC-13) |
| `REC.ORDER.ORPHAN_TRANCHE` | ERROR | `Total = 0.00` row with no sibling carrying the cash (H-1) |
| `REC.ORDER.COMMISSION_IMPLAUSIBLE` | WARNING | derived commission outside the observed band (H-7, RC-15) |
| `REC.INSTRUMENT.AMBIGUOUS_SYMBOL` | ERROR | one ticker resolving to two instruments without a wrapper (H-2, RC-16) |
| `REC.INSTRUMENT.UNLISTED_UNDERLYING` | WARNING | CDR on an unlisted issuer — **stated, not a failure** (H-3) |
| `REC.FX.RATE_UNPARSEABLE` | ERROR | FX description does not yield a rate (H-4) |
| `REC.FX.LEGS_DISAGREE` | ERROR | parsed rate does not reconcile the two legs (RC-17) |
| `REC.ACCOUNT.TYPE_UNKNOWN` | ERROR | account type not configured — **M-4's flag cannot fire** (H-5, RC-18) |
| `REC.RECONCILE.BREAK` | ERROR | positions + cash ≠ NAV (RC-10, INV-025) |
| `REC.CAPITAL.NOT_AVAILABLE` | ERROR | capital base requested for a date with no reconciled book (RC-19) |
| `REC.EXEC.NOT_MEASURABLE` | *(not an error)* | window predates arrival capture — **a value, not a failure** (RC-7) |

---

# 14. ACCEPTANCE CRITERIA

> **Trimmed v0.2.0 to what a monitoring template needs.** The cuts are all in *ambition*; every
> criterion below is a *correctness* one, and §5's hazards break a simple recorder exactly as badly
> as an elaborate one.

```text
INGESTION — the four hazards the current parser does not handle
□ AC-11.1  A multi-tranche order reconstructs to ONE Order with ONE commission;
           the sibling row with Total=0.00 is not a free trade (H-1)
□ AC-11.2  MU-as-CDR and MU-as-US-stock resolve to DIFFERENT instrument_ids (H-2)
□ AC-11.3  The FX rate parsed from prose reconciles both legs, or raises (H-4)
□ AC-11.4  A blank Activity Description raises (H-8)

INGESTION — the rest
□ AC-11.5  Commission is DERIVED per order, not read from a constant (H-7: $9.95)
□ AC-11.6  A CDR on an unlisted issuer resolves with underlying_cik=null and does
           NOT fail the run as a broken ticker (H-3)
□ AC-11.7  Account type comes from the filename convention; an unrecognised name raises
□ AC-11.8  Fewer exports than the four known accounts raises (RC-3)
□ AC-11.9  Re-ingesting an identical file is a no-op (RC-11)

BOOK, CAPITAL, JOURNAL
□ AC-11.10 positions + cash == NAV per currency per account per day (INV-025)
□ AC-11.11 nav_base is null when no FX rate exists — never estimated (FX-3)
□ AC-11.12 Every amount is a Money with explicit currency (INV-001)
□ AC-11.13 capital_base(as_of) is read from the reconciled book, not configured (QA-63)
□ AC-11.14 capital_base is point-in-time; a future book never leaks in (INV-1)
□ AC-11.15 The journal is append-only; editing an existing entry raises (INV-006)

MONITORING
□ AC-11.16 A short-hold round trip is flagged — with NO exempt account population,
           because all four accounts are registered (RC-25, M-4)
□ AC-11.17 execution_cost() returns NotMeasurable, never zero, never raising (RC-5)

BOUNDARY
□ AC-11.18 src/recording imports neither src/reporting (ST-9) nor any analytical domain
□ AC-11.30 ★ The header is read, not assumed; the 13-column export parses to the
           same canonical fields as the 10-column one (RC-37)
□ AC-11.31 ★ An unknown activity type raises rather than being dropped (RC-13)
□ AC-11.32 ★ NVDA 2026-04-29's two tranches group to ONE order with a derived
           commission of exactly 9.95 (RC-38, RC-15) — known answer
□ AC-11.33 ★ A zero Total Amount is a tranche, not an absence: MU 2026-05-06
           keeps all 550 shares and still derives 9.95 (RC-12, H-1)
□ AC-11.34 ★ A book may origin from a stated opening snapshot; the artifact
           records which origin was used (RC-47)
□ AC-11.39 ★ An opening snapshot that still leaves a position negative raises —
           the snapshot or the window is wrong, and neither is guessed (RC-47, RC-45)
□ AC-11.40 ★ every run writes a CT-11.7 artifact, and a BLOCKED or
            INCOMPLETE run writes one too (RC-59, RC-33)
□ AC-11.41 ★ a run_id is written once — a second write raises, it never
            overwrites (RC-60, OR-13)
□ AC-11.42 ★ a thesis is stored under its bundle_hash and an unchanged
            bundle reuses it instead of re-authoring (RC-61)
□ AC-11.43 ★ runs.parquet is rebuildable from the run directories — the
            index is a convenience, never the record (CT-11.7)
□ AC-11.44 ★★ recommendation.json carries the nomination — the ranked slate,
            excluded[] with reasons, universe_n and model_artifact_id — and
            D-12's Recommendation class does not gain the fields (RC-62)
□ AC-11.45 ★ a delivered run writes delivery.json; a run that did not deliver
            writes none, because absence means not-delivered (RC-63, DE-35)
□ AC-11.46 ★ runs.parquet carries excluded_n and model_artifact_id and is
| **AC-11.47** | ★★ **RC-65** — **Given** an export directory holding statements for *n* accounts, **when** the book is loaded, **then** exactly those *n* accounts are read, whatever *n* is; **and** a statement added later is picked up with **no code change**. → *unit.* ⚠ This is what makes a 5th portfolio (`RRSP_2`, planned 2027) a file drop rather than an edit |
| **AC-11.48** | **RC-65** — **Given** an export directory with no statements, **when** `discover_accounts` runs, **then** it **raises** naming the directory; **and when** `load_books` runs, **then** it returns `((), reason)` with that text — ⚠ **it does not crash.** ★ Both halves are required and they are not in tension: at the query layer *"no accounts"* is an error, while `load_books`' contract is `RC-10`/`RK-5`'s — *carry the refusal forward as a reason, because a refusal that cannot say what it lacks is the defect `RC-10` exists to prevent.* ⚠ Caught by the fresh-clone check: a raise here turned an orchestration job from `SUCCESS` to `FAILED` |
| **AC-11.49** | ★ **RC-67** — **Given** the export directory, **when** `python -m src.recording.check` runs, **then** every account is reported (window, rows, orders, positions, cash per currency) and a bad file is **named with its reason** while the others are still reported; nothing is written; the exit status is non-zero when any account refused. → *integration (hermetic, synthetic files).* |
| **AC-11.50** | ★★ **RC-68** — **Given** a recorded entry, **when** the same file is checked again, **then** it is a no-op; **when** a row inside the covered window changes, **then** a RESTATEMENT is reported naming the removed and added rows; **when** rows are added after the window, **then** they are reported as new activity, not a restatement. → *unit.* |
| **AC-11.51** | ★ **RC-68** — `--record` APPENDS an entry (with any restatement it found) and never rewrites an earlier line; without `--record` the log is untouched. → *unit.* |
| **AC-11.52** | ★ **RC-69** — **Given** `.state/runs/` holding a CT-11.7 run beside a thesis trace directory (`trace.jsonl` + a `trace/` folder), **when** a run is recorded and the index rebuilt, **then** both succeed, the index lists only the CT-11.7 run, and no subdirectory is read as a file. → *unit.* |
            still rebuildable from the directories (RC-64, CT-11.7)
```

> **Deferred with the priority, not dropped:** performance attribution (F8 is a reserved desk),
> multi-period P&L attribution, and anything that would only matter at institutional scale.

# 15. OPEN QUESTIONS

**Five of seven closed 2026-08-18.** What remains is small, and matches the priority.

| ID | Question | Note |
|---|---|---|
| ~~QC-1~~ | ~~Is the RESP part of the fund?~~ | ✅ **CLOSED** — recorded and reconciled like any account, **excluded from fund performance and exposure** (RC-4). It has a beneficiary and its own mandate |
| ~~QC-2~~ | ~~What is the fourth account?~~ | ✅ **CLOSED** — `TFSA_2`. All four now sampled: RESP ×1, RRSP ×1, TFSA ×2, **all registered** (§5.5) |
| ~~QC-5~~ | ~~Where does arrival capture run?~~ | ✅ **CLOSED — won't do** (Victor). See §7; QQ-20 closes as *will not measure* and ground (b) is permanently indeterminate |
| ~~H-5~~ | ~~Registered status is not a field~~ | ✅ **CLOSED** by the `TransactionHistory_<TYPE>_<n>.csv` convention |
| ~~QC-3~~ | ~~How are CDRs treated by D-07 and D-02?~~ | ✅ **CLOSED 2026-08-18 (Victor): a CDR is the same instrument as its underlying.** **No change to D-07 or D-02** — one ticker, one price series, one set of fundamentals. The split survives only in D-11's *valuation*, resolved by **RC-26** (§5.6) |
| **QC-4** | Does the **CDR FX hedge** change the return? | 🟡 **Corroborated, not proven.** Over 8 closed round trips the mean signed error is **−0.08 pts vs the USD return** and **−0.98 vs the unhedged CAD translation** — 12× better for the hedged form — but sd ≈ 2.2 either way, mostly execution-vs-close noise. **RC-27's realised-error monitor is what settles it**, over time and for free |
| **QC-8** | Is FMP's **total absence of Canadian coverage** a constraint anywhere else? | `RY.TO`, `SHOP.TO`, `ENB.TO`, `XIU.TO` are all 402 — this is a whole-market gap, not a CDR gap. It bites anywhere a CAD-listed instrument needs a price. Adding a source is an **L0 §2.2 decision** |
| **QC-6** | `FLAT_TRADE_FEE_DOLLARS` → `9.95`, or derived? | RC-15 says derived. `tests/test_flat_trade_fee.py` asserts `10.0` as "broker reality" and is **wrong by 5¢**. A `pipeline/` edit under the SDD loop; trivial, and not urgent at 22 bps |
| **QC-7** | Is the RESP **grant** row a cash flow or a contribution? | Neither Victor's money nor market P&L. Only matters if attribution is built — **deferred with it** |

> ★ **QC-3 does not inherit D-11's minimal priority.** The re-scope covers *this domain's ambition*;
> it does not downgrade a defect this domain found in another one. A CDR and its underlying sharing
> a ticker corrupts the feature panel, the ranking and the book **silently**, and `MU` is on the
> actionable path.

# 16. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-11, §3.1 LEVEL 0, **M-4**, **M-5**, INV-001/006/025 | domain definition, autonomy, registered-account flagging, currency |
| `L1-quantitative-analysis.md` **§5.6a**, **§5.8**, QA-63, QA-69, QA-70, QQ-20 | the capital base this domain answers; the arrival capture it owns; the cost measurement it enables |
| `L1-data-engine.md` §5, §6, DE-14, DE-24, DE-35 | prices and FX; the null/restatement/UNCHECKED rules this domain inherits |
| `L2-shared-money.md` CT-M.1, **FX-2**, **FX-3** | `Money`; the recorded rate; `nav_base = None` rather than a guess |
| `L4-coding-standards.md` §1.1, **ST-9** | path; **Recording must not import Reporting** |
| `sdd/specs/F4_data_plane/spec.md` | **prior art, 8/8 ACs green — and it names the wrong broker** (H-2) *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F2_portfolio_and_delivery/spec.md` | the decision journal's current home *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `samples/bmo_investorline_transactions/` | ★ the three real exports every claim in §5 is checkable against |
