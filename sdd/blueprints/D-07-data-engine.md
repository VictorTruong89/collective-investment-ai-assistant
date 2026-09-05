# Blueprint — D-07 Data Engine

> **Code:** `src/data_engine/` · **Spec:** `sdd/design/rel6_design/L1-data-engine.md` **v0.7.0** · **Seat:** SEAT-5
> **Status:** written 2026-08-23 at **B2** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **This describes the CODE, not the spec.** A sentence here that would still be true if the code
> were rewritten differently belongs in the spec (DR-1).

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-27 | ★★★ **DE-55 — the conversion EDGAR was CHOSEN for had never run** | `discrete_from_cumulative` has been in `src/data_engine/src/edgar/xbrl.py` since B2 and **nothing ever called it**; `extract_facts` rejected every cumulative span. ⚠ NVDA's cash-flow facts carry **70 year-to-date spans against 38 discrete quarters** — two of every three quarters had no cash flow, and every four-period feature read as *sparse data*. ★ Self-checking: the four derived FY2026 quarters sum to **102.718 bn against a reported 102.718 bn**. Also **DE-54**: sub-penny prices (`AAPL 310.245`) raised and surfaced as `no_source` | *Trusting a rejection reason* — `cumulative span` read as a decision when it was a gap |
| 2026-08-26 *(universe)* | **Every fetch failure is collected, then reported once** | ★ *A 130-name universe with three problems should take one run to diagnose, not three.* Raising on the first bad ticker tells you about one name per run, and the operator then plays whack-a-mole | *Fail-fast on the first* — technically DE-13-compliant and useless in practice |
| 2026-08-26 *(universe)* | ★★ **A 402 is classified apart from a missing security** | **DE-49.** DE-13 fails the run when a ticker *"resolves to no source"*, DE-46 says a 402 is never *"no data"* — **neither said what to DO about one**. An absent security is a **universe error to correct**; a plan-gated one is a **declaration** problem, and *discovering it at fetch time is discovering it too late* | *Treating both as DE-13* — the remedy differs, and conflating them sends you looking for a data bug that is a subscription boundary |
| 2026-08-26 *(universe)* | **A short history is NAMED, not dropped and not a failure** | ⚠ A name with 40 rows in a panel whose median is 900 carries NaNs in every trailing window. It is not a fetch failure — and it is **not ignorable**, because `coverage()` is what decides whether it may be the actionable pick (MT-11) | *Dropping short names* — it changes the cross-section the ranking is computed over, silently |
| 2026-08-23 | **`adj_factor` is derived from the EVENTS, not from `adj_close/close`** | CT-7.1 defined the factor as the vendor ratio, which is **circular under DE-27**: the raw series is the system of record, so `adj_close` is an *output* of the factor. Spec amended (DE-42) before the code was written | Keeping the vendor ratio — it works only while `full` is ingested, which DE-27 forbids |
| 2026-08-23 | **`volume` is always RAW, in both panel modes** | CT-7.1 declares no `adj_volume`, and DE-29 puts absolute/cross-sectional volume on the raw series anyway. ★ **Consequence a reader must know: dollar volume is `close_minor × volume` (raw × raw), never `adj_close × volume`**, which would be wrong by the split factor | Adding an `adj_volume` column — it would be a contract change with no consumer, and it invites the raw×adjusted mix it is meant to prevent |
| 2026-08-23 | An event on date `E` adjusts dates **strictly before** `E` | ⚠ This IS DE-44. The ex-date open already reflects the dividend drop and the split-date price is already post-split, so including `E` itself double-counts | `<=` — passes DE-43's monotonicity test either way (QA-85), which is exactly why DE-44 demands a separate ex-date assertion |
| 2026-08-23 | Price adjustment lives in **`src/data_engine/pit/adjustment.py`**, not a new module | §5C.7's own argument: *"the fix is the pattern §6 already uses"* — immutable observations plus the events that transform them. It is restatement handling applied to prices | A `prices/` module — it would put the same reasoning in two places and let the two drift |
| 2026-08-23 | `adj_as_of=None` means RAW; **omission raises** | DE-45. A `None` default would BE the default DE-6.4 forbids, spelled differently, and every existing call site would keep working | `adjusted: bool = True` — the original §8 signature, which made both `DATA.PRICE.*` error codes unraisable |
| 2026-08-23 | The Fact ledger is **per-ticker parquet** | QD-1, leaning per-ticker in the spec. Simpler to write atomically, and the whole-ledger scan is 130 files rather than 130M rows | A partitioned dataset — faster to scan, and nothing yet scans |
| 2026-08-23 | The event store **upserts**; the Fact ledger **appends** | They hold different things. A filing is immutable and its restatement is itself evidence (DE-6.2). A vendor's statement *about* an event is not — a corrected split ratio should replace the wrong one | Append-only for both — it would accumulate known-wrong split ratios with nothing saying which binds |
| 2026-08-23 | **`UNCHECKED` is D-07's own tri-state, not L4's `Unmeasured`** | DE-35 needs a status *per event class* carrying a reason, which is what `class_status` is. `Unmeasured` (EH-7) is a value type for a quantity; a class status is not a quantity | Introducing `Unmeasured` in `src/shared/` — a D-00 contract change with one consumer, and L2-shared-infrastructure does not declare it |
| 2026-08-23 | The 402 retry lives **in D-07's client** | DE-15/AC-7.32 against L4 EH-14. Resolved as **DE-46**: §5A.2's three causes are indistinguishable from one response, so re-sending is *classification*, not recovery. The attempt count rides on the error to the manifest | Tagging `PlanGatedError` retryable and letting D-08 do it — then D-07 could never report "plan gate" at all, and AC-7.32 becomes unimplementable |

---

# 1. What this domain does, in one paragraph

D-07 answers one question and must answer it identically every time: **"give me the data that was
*knowable* on date D, in canonical shape, with its provenance, regardless of which source supplied
it."** It reaches EDGAR and FMP (nothing else in `src/` holds a URL or a key), translates provider
formats to canonical shapes at the client boundary, stores Facts append-only, and *derives* panels
at a stated `as_of`. It is responsible for being right about **time** — not about value. If two
reasonable analysts could disagree about the formula, it belongs in D-02.

# 2. The objects and how they flow

```text
   EDGAR                              FMP
   submissions ──► filer_class ─┐     splits ─┐  dividends ─┐   non-split-adjusted
   companyfacts ──► extract_facts│              │             │        │
        │                        │              └──────┬──────┘        │
        ▼                        ▼                     ▼               ▼
     Fact ────────────► FactLedger              CorporateEvent    raw OHLCV frame
   (CT-7.3, append-only, per-ticker parquet)          │               │
        │                                             └───────┬───────┘
        │  facts_as_of(as_of)                                 ▼
        ▼                                          build_price_panel(adj_as_of)
   assemble_rows ──► CT-7.2 FundamentalPanel              CT-7.1 PricePanel
        │                                                      │
        └──────────────► DataEngine (§8 surface) ◄─────────────┘
                                 │
   FMPEventFeed ─► EventStore ─► CachedEventFeed ─► calendar_check ─► CT-7.7 report
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `Fact` | `src/data_engine/pit/models.py::Fact` | `src/data_engine/src/edgar/companyfacts.py::extract_facts` | `FactLedger`, `facts_as_of` | forever — append-only |
| `CorporateEvent` | `src/data_engine/pit/models.py::CorporateEvent` | `src/data_engine/src/fmp/prices.py::splits` / `::dividends` | `src/data_engine/pit/adjustment.py`, the gate | per run |
| `CalendarEntry` | `src/data_engine/pit/models.py::CalendarEntry` | *(not yet produced)* | D-04 via CT-7.6 only | per run |
| price panel | `src/data_engine/contracts/panels.py::PRICE_PANEL` | `src/data_engine/pit/adjustment.py::build_price_panel` | D-02 | per `(window, adj_as_of)` |
| `Finding` | `src/data_engine/contracts/envelopes.py::Finding` | the event feeds | `CalendarCheckReport` | with the run record |
| `Provenance` | `src/data_engine/contracts/envelopes.py::Provenance` | `src/data_engine/service.py::DataEngine.provenance` | every served artifact | with the artifact |

★ **The object that surprised me: `adj_factor`.** It reads like a column and it is a *derivation
parameter*. Two panels over the same dates differ entirely because of it, and it is the only field
in CT-7.1 whose value depends on **when you asked** rather than on what happened.

# 2a. ★ As-built — the ledger writes *(2026-08-27)*

⚠ **`DataEngine` read ledgers and nothing wrote one.** `get_fundamentals` and
`get_observation` were correct and answered from empty stores.

| Module | What it is | ⚠ Open / known-limited |
|---|---|---|
| `src/data_engine/ingest/edgar_facts.py` | EDGAR companyfacts → `FactLedger` | ★★ **DE-55**: `Q_n = YTD_n − YTD_(n−1)`, *the arithmetic EDGAR is chosen for*, had **never run** — NVDA carried **70 YTD spans against 38 discrete quarters** |
| `src/data_engine/ingest/observations.py` | FMP Class-B → `ObservationLedger` | ⚠ Cadences in `DEFAULT_SCHEDULE` are **admitted guesses** (CN-10) — none was measured |
| `src/data_engine/ingest/events.py` | corporate actions → `EventStore` | ★★★ **DE-56**: the gate recorded three classes as `CHECKED` **having fetched nothing**. With the store populated it **HALTs on NVDA's 2024-06-10 10:1 split** |

## ⚠⚠ Open question — the sweep §6A assumes and nobody schedules

★ **QD-16 is explicit**: *"510 tickers × 8 classes is thousands of calls per run
against a 300/min cap"*, so §6A's design is an **incrementally maintained store**
that the gate reads. `src/data_engine/ingest/events.py` is the maintainer — ⚠ **and nothing
schedules it.** Until something does, the daily run honestly reports
`split: UNCHECKED`, which is the truth and is **weaker than FE-10's guarantee
sounds**. Registered as **AB-14**.

## ⚠⚠ Open questions carried to `L6-as-built-remaining.md`

⚠ **INV-017 survivorship is UNCORRECTABLE from these sources.** §5A.5: *"the
universe is live-listed names only; nothing currently accounts for what left"*,
and **DE-35 makes index membership `UNCHECKED` permanently**. A measured IC on
today's index over ten years is an **upper bound**, not an estimate — recorded on
every artifact's `evaluation.json`.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | classify the filer | `src/data_engine/src/edgar/submissions.py::route` | ★ **DE-5.1 — decided ONCE, per ticker, before anything is fetched.** Deciding later means deciding per call, which is how a series switches source mid-history | `NoFundamentalSourceError` / `NoCikError` |
| 1 | run the gate | `src/data_engine/calendar/check.py::calendar_check` | **DE-31 — before the first feature is built.** A window whose units changed partway through is not fixable downstream | `UnhandledBlockError` (HALT) |
| 2 | fetch raw prices + events | `src/data_engine/src/fmp/prices.py` | DE-27: raw is the system of record; the adjusted panel is never ingested | `ContractViolationError` on an empty series |
| 3 | derive the panel | `src/data_engine/pit/adjustment.py::build_price_panel` | Needs step 2's events **and** the run's `adj_as_of`, which only the caller knows | `AdjAsOfRequiredError` |
| 4 | assert the adjustment | `assert_factor_discipline`, `assert_ex_dividend_convention` | ★ **After the panel, against step 1's flagged dates.** Running it before would have nothing to compare against | `ContractViolationError` |
| 5 | validate | `src/data_engine/validation/pipeline.py::run` | Classify, never modify — and *after* derivation, so a bad factor is visible as a bad row | REJECT rows dropped, FLAG rows kept |
| 6 | ingest facts | `src/data_engine/src/edgar/companyfacts.py::extract_facts` → `FactLedger.append` | DE-6.3 fires at ingest, not at read: an undateable Fact must never enter | `NoFilingDateError`, `AppendOnlyError` |
| 7 | resolve at `as_of` | `src/data_engine/pit/snapshot.py::facts_as_of` → `assemble_rows` | §6.3. Independent of ingest order, which is what makes INV-2 hold | `AsOfRequiredError` |

⚠ **Step 1 before step 2 is the ordering a rewrite would get wrong**, because fetching first and
checking after "works" and is faster. It is also how a blocked window gets a panel built for it.

# 4. ★ The mathematics

### The cumulative adjustment factor

| | |
|---|---|
| **Implemented in** | `src/data_engine/pit/adjustment.py::adjustment_factors` |
| **Formula** | ```python\nfor event in usable:                      # ascending, fixed order\n    cut = np.datetime64(pd.Timestamp(event.event_date))\n    ...\n    factors[day < cut] *= m\n``` |
| **Units** | dimensionless ratio. `adj_price_minor = round_half_up(raw_price_minor × factor)`; minor units in, minor units out, currency unchanged |
| **Domain / range** | `(0, ∞)`. Forward splits give `f < 1`, reverse splits `f > 1`, dividends `f < 1`. `f = 1` on and after the last event ≤ `adj_as_of` |
| **Why this form** | Only events with `event_date <= adj_as_of` contribute (**DE-28**), and each contributes to dates **strictly before** it. Strictness is DE-44: the raw price on the event date already reflects the change |
| **Alternatives rejected** | `adj_close/close` from the vendor — circular under DE-27 (see decision log). Recomputing per consumer — DE-42, "four call sites is four chances to derive it differently" |
| **Sensitivity** | Entirely driven by the event list. **A missing split is a 10× error on every pre-split price**; a spurious one is the same in reverse. The dividend term is second-order (~0.2 % per quarter for MSFT) |
| **★ Worked example** | NVDA, `adj_as_of = 2024-08-01`, one event: 10:1 effective 2024-06-10.<br>`m = denominator/numerator = 1/10 = 0.1`.<br>2024-06-07 `< 2024-06-10` ⇒ `f = 0.1`; `close_minor 120890 × 0.1 = 12089.0` → `round_half_up` → **12089** = $120.89.<br>2024-06-10 is **not** `< 2024-06-10` ⇒ `f = 1.0`; `12179 → 12179` = $121.79.<br>★ Same inputs, `adj_as_of = 2024-06-01`: the split is not yet usable ⇒ `f = 1.0` ⇒ **120890** = $1,208.90. **Verified against live FMP 2026-08-23** — our 12089 equals the vendor's own `full` close exactly (probe check K-2c) |
| **Known-wrong** | Float multiplication is not associative, so the factor depends on event ORDER. Fixed by sorting `(event_date, event_type, str(detail))`. Deterministic, but a *different* sort would give a different last-bit result |

### The dividend multiplier

| | |
|---|---|
| **Implemented in** | `src/data_engine/pit/adjustment.py::dividend_multiplier` |
| **Formula** | ```python\nreturn 1.0 - (float(cash_minor) / float(prior_close_minor))\n``` |
| **Units** | minor units ÷ minor units → dimensionless. **Both operands must be the same currency**; the caller guarantees it by taking `prior_close` from the same panel |
| **Domain / range** | `prior_close_minor > 0` and `cash_minor >= 0` ⇒ `(0, 1]`. A dividend exceeding the prior close would give `<= 0` and is not guarded — it would be caught by CT-7.1's strict-positivity check |
| **Why this form** | The reference close is the session **before** the ex-date. That is what makes DE-44's assertion meaningful: the factor step lands *between* `ex-1` and `ex`, not after `ex` |
| **Alternatives rejected** | Using the ex-date close — it already contains the drop, so the factor would subtract it twice |
| **Sensitivity** | Linear in the dividend. MSFT's $0.75 on a $415 close is 0.18 %; sign errors here are invisible in any aggregate |
| **★ Worked example** | MSFT ex-date 2024-05-16, `cash_minor = 75` ($0.75), prior close 2024-05-15 = `41500` ($415.00).<br>`m = 1 − 75/41500 = 1 − 0.0018072 = 0.9981928`.<br>2024-05-15 `f = 0.9981928`; 2024-05-16 (the ex-date) `f = 1.0`. **The ratio `f(ex−1)/f(ex)` is exactly `m` — that is AC-7.59's assertion** |
| **Known-wrong** | `prior_close` is the previous row **in the panel**, so a panel starting on an ex-date has no reference and raises rather than assuming 1.0 (DE-14) |

### Period-span classification

| | |
|---|---|
| **Implemented in** | `src/data_engine/src/edgar/xbrl.py::classify_span` |
| **Formula** | ```python\ndays = (period_end - period_start).days\nif ANNUAL_DAYS[0] <= days <= ANNUAL_DAYS[1]: return ANNUAL\nif QUARTER_DAYS[0] <= days <= QUARTER_DAYS[1]: return QUARTERLY\nreturn "cumulative"\n``` |
| **Units** | days |
| **Domain / range** | quarterly 80–100 d, annual 350–380 d, everything else `cumulative` |
| **Why this form** | ★ **`cumulative` is a first-class answer, and that is the whole point.** A 6- or 9-month span is neither a quarter nor a year, and ingesting it as either injects 2–3× inflated revenue (ARM: 1.93× / 2.76× / 3.30×) |
| **Alternatives rejected** | Trusting the filer's `fp` label — FMP has only the period end and must guess, which is exactly the 71 % MU defect |
| **Sensitivity** | The bounds. 80–100 d covers 13- and 14-week fiscal quarters with margin and **cannot admit a half-year (≈182 d)**, which is the only misclassification that matters |
| **★ Worked example** | ARM Q2 FY2026: start 2025-04-01, end 2025-09-30 → 182 d → `cumulative` → **rejected at ingest**, with the reason counted in `ExtractResult.reasons`. The discrete figure is recovered by `discrete_from_cumulative`: `2188 − 1053 = 1135`, which matches FMP's discrete Q2 exactly |
| **Known-wrong** | An instant fact (balance-sheet item) has no `start`; its span would read as 0 d ⇒ `cumulative`. Handled by typing instants from the filer's `fp` instead — see `src/data_engine/src/edgar/companyfacts.py::_one` |

# 5. The logic decisions

| Decision | Where | What it does | Why this way | What it would take to change it |
|---|---|---|---|---|
| Case A wins where both filings exist | `src/data_engine/src/edgar/submissions.py::filer_class` | a 10-K filer routes to EDGAR even if it also files 20-F | DE-5.3 forbids mixing sources within a series, so the better source takes **all** the history | one line; but the series would then have two provenance regimes |
| Rounding is **half-up**, not banker's | `src/data_engine/pit/adjustment.py::_round_half_up` | `floor(x + 0.5)` | numpy's default rounds 0.5 to even, which is *statistically* better and *reproducibly* identical either way. Half-up is chosen because it is the direction a reader predicts | `np.rint`; every adjusted price could shift by one minor unit |
| 3 attempts on a 402 | `src/data_engine/src/fmp/client.py::RETRY_DELAYS_S` | 0 s, 1 s, 4 s | ⚠ **Provisional — never measured.** §5A.2 cause 3 recovered on the **first** retry in every observed case; a fourth attempt only lengthens a decided failure (CN-10) | `RETRY_DELAYS_S`; it is a module constant, and arguably belongs in config |
| `max_age_days = 1` on the cached feed | `src/data_engine/calendar/store.py::CachedEventFeed` | a store older than a day reports UNCHECKED | ⚠ **Admitted guess.** Corporate actions are announced daily; a day-old sweep is the coarsest that still catches an overnight 8-K | constructor argument — already injectable |
| DQ-006 fires at \|1-day return\| > 50 % | `src/data_engine/validation/rules/price.py` | FLAG, not REJECT | ⚠ **Not a measured breakpoint.** A real 10:1 shows as −90 % here, which is what §6A's gate exists for; this is the backstop | one literal — but it should become config when D-08 wires a manifest |
| The universe is config-backed | `src/data_engine/universe/membership.py::load_universe` | reads JSON | **QD-5 is open.** §5A.1 shows `stock-list` would be better, and the answer changes only where the list comes *from* | rewrite `load_universe` alone |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Range | Who reads it | Changing it affects |
|---|---|---|---|---|---|
| universe list | a JSON path passed to `load_universe` | — | — | `Universe` | every % figure, DE-36's coverage |
| `RATE_LIMIT_PER_MIN` | `src/data_engine/src/fmp/client.py` | 300 | vendor-set | `FMPClient._throttle` | ⚠ **world fact**, checked 2026-08-15 (CN-2) |
| `RATE_LIMIT_PER_SEC` | `src/data_engine/src/edgar/client.py` | 10 | SEC-set | `EdgarClient._throttle` | ⚠ **world fact**, checked 2026-08-23 |
| `RETRY_DELAYS_S` | `src/data_engine/src/fmp/client.py` | `(1.0, 4.0)` | — | `FMPClient.get` | ⚠ **hard-coded policy choice — arguably config (CN-3)** |
| `NEWS_DEPTH_DAYS` | `src/data_engine/calendar/classes.py` | 92 | measured | `news_status` | when news flips to UNCHECKED |
| `DEFAULT_SCHEDULE` cadences | `src/data_engine/observation/schedule.py` | 1–30 d | — | `plan(overrides)` | CT-7.6 growth; **QD-6 is open** |
| `max_age_days` | `CachedEventFeed` ctor | 1 | — | the gate | how often UNCHECKED fires |

⚠ **Nothing here reaches a RunManifest yet** — D-08 does not exist. CN-5 becomes checkable at B6.

# 7. Inputs and outputs

| Direction | Contract | Shape | Producer / consumer | What happens if malformed |
|---|---|---|---|---|
| in | FMP JSON | list of dicts | `src/fmp/*` | `ContractViolationError`; ★ **the raw endpoint's fields are named `adjOpen`/`adjClose`** — see §10.1 |
| in | EDGAR companyfacts | nested dict | `src/data_engine/src/edgar/companyfacts.py` | dropped with a counted reason, never silently |
| out | **CT-7.1** | parquet, 20 columns | → D-02 | `validate_price_panel` raises |
| out | **CT-7.2** | parquet, base + line-item pairs | → D-02 | `validate_fundamental_panel` raises |
| out | **CT-7.3** | parquet per ticker, append-only | internal; audit via `get_facts` | `AppendOnlyError` |
| out | **CT-7.6** | parquet per field set | → D-04 **only** at an `as_of` | `LiveReadDeniedError` |
| out | **CT-7.7** | JSON with the run | → D-08, every artifact | missing class ⇒ `ContractViolationError` |
| out | **CT-7.5** | JSON envelope | every served artifact | invalid `pit_guarantee` ⇒ `ValueError` |

# 8. Failure behaviour

| Failure | Detected where | Behaviour | Visible to whom |
|---|---|---|---|
| no CIK / no source | `src/data_engine/universe/membership.py` | `NoCikError` / `NoFundamentalSourceError` — **run fails, ticker named** | the run |
| Fact with no `filed` | `src/data_engine/pit/ledger.py::_reject_undateable` | `NoFilingDateError` at ingest | the run |
| `as_of` omitted | `src/data_engine/pit/snapshot.py::require_as_of` | `AsOfRequiredError` | the caller |
| `adj_as_of` omitted | `src/data_engine/pit/adjustment.py::build_price_panel` | `AdjAsOfRequiredError` | the caller |
| adjusted panel to a raw-only consumer | `src/data_engine/contracts/panels.py::require_raw` | `RawRequiredError` | the consumer |
| unhandled BLOCK | `src/data_engine/calendar/check.py` | `UnhandledBlockError` — **HALT, tickers and events named** | the run |
| a class could not be sourced | the feeds | `UNCHECKED: <reason>` in `class_status` — ⚠ **never "no events"** | the report |
| persistent 402 | `src/data_engine/src/fmp/client.py` | `PlanGatedError` with endpoint, params, attempts | the run |
| known-gated parameters | `src/data_engine/src/fmp/gates.py` | `PlanGateRejected` — never sent | the caller |
| partial write | `src/data_engine/store/atomic.py` | `StoreWriteError`; temp file removed | the run |
| live probe cannot run | `src/data_engine/calendar/probe.py` | `SKIP` + `DATA.PROBE.SKIPPED` — ⚠ **never a pass** | the run summary |

# 9. What this domain deliberately does NOT do

| Not here | Owner |
|---|---|
| ratios, margins, growth, indicators, scores | **D-02.** *"If two reasonable analysts could disagree about the formula, it does not belong here"* |
| ingesting `technical-indicators/*` | D-02 owns our definitions — a vendor RSI is a second, silently different one (AC-7.31) |
| scoring news sentiment | **D-01** via the LLM gateway. FMP has no sentiment product, and that is the right outcome (§5A.3) |
| publishing a fair value | AP-5. FMP's DCF is a cross-check, never a number we publish |
| retrying for **recovery** | **D-08** (EH-14). D-07's 402 retry is classification only — DE-46 |
| scheduling | D-08. `backups/pipeline/fundamental_analysis/etl/data_ingest_scheduler.py` is explicitly *not* D-07's (L4 §1.5) |
| the capital base | **D-11** (RC-19). ⚠ BS-9 said "at B2"; amended 2026-08-23 — it lands with D-11's book |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — the raw endpoint's fields are named `adj*`** | ⚠ **medium, vendor-side** | `historical-price-eod/non-split-adjusted` returns `adjOpen`/`adjClose` holding **RAW** values, while `full` returns `open`/`close` holding **ADJUSTED** ones. Reading by field name gets it exactly backwards and **both shapes parse without error**. Handled by `src/data_engine/src/fmp/prices.py`'s `_FIELD_ALIASES`. ★ **Found by the live probe on its first real run** — a fixture written from this file's own assumptions never would have | new — no ID |
| **10.2 — `restatement_silent` is permanently UNCHECKED here** | ⚠ expected | DE-24 needs a prior dated ingest to diff. Until a second dated pull exists, class 5 admits ignorance rather than reporting clean | DE-17, QD-14 |
| **10.3 — `earnings_scheduled` is UNCHECKED** | ⚠ expected | `earnings-calendar` has no publication axis; 34.6 % of rows are forward-dated. Usable only once snapshotted into CT-7.6 | **QD-11** |
| **10.4 — `FMPEventFeed` is per-ticker per-class** | medium | ~1,000 calls for a 130-name universe against a 300/min cap. `CachedEventFeed` is the intended path; the direct feed is for refresh and for the probe | **QD-16** |
| **10.5 — `freshness()` reports no price rows** | low | `FreshnessReport.price_rows` is always 0: D-07 holds no price *store* yet, only a derivation. Honest but incomplete | new — no ID |
| **10.6 — no `Money` object crosses the panel boundary** | low, by design | Panels carry `*_minor` + `*_currency` per CT-M.1's two-column form; `Money` is constructed at the client boundary and decomposed immediately. Correct, and surprising if unstated | CT-M.1 |
| **10.7 — `assemble_rows` maps one tag to one column** | ⚠ medium | Two XBRL tags meaning the same line item produce two columns. Tag *resolution* (`src/data_engine/src/edgar/xbrl.py`'s stated job) is not implemented — only unit and period handling are | new — no ID |
| **10.8 — the dividend factor needs an in-panel prior close** | low | A window starting on an ex-date raises rather than assuming 1.0. Correct per DE-14, and it means a one-row window across an ex-date is unbuildable | new — no ID |

★ **10.7 is the one to read twice.** It produces a *plausible* panel — a column per tag, all
correctly typed — where a reader would expect one column per concept. That is the failure shape this
whole tier exists for.

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_data_engine_prices.py` · `tests_src/test_data_engine_pit.py` · `tests_src/test_data_engine_routing.py` · `tests_src/test_data_engine_calendar.py` · `tests_src/test_data_engine_probe.py` — 79 cases, each docstring naming its `AC-7.n` |
| 2 | ★ **Break it and confirm red** | In `src/data_engine/pit/adjustment.py::adjustment_factors`, change `factors[day < cut]` to `factors[day <= cut]`. `test_ac_7_59_ex_dividend_dates_get_their_own_assertion` must fail — **and DE-43's monotonicity test must still pass**, which is precisely why DE-44 exists |
| 3 | The worked example (§4) reproduces | `python -c "import pandas as pd; from datetime import date; from src.data_engine.pit import build_price_panel, CorporateEvent; raw=pd.DataFrame([{'ticker':'NVDA','date':'2024-06-07','open_minor':119770,'high_minor':121690,'low_minor':118020,'close_minor':120890,'volume':41238600,'currency':'USD','source':'fmp'}]); s=CorporateEvent('NVDA','split',date(2024,6,10),date(2024,5,22),{'numerator':10,'denominator':1},'fmp:splits'); print(int(build_price_panel(raw,[s],date(2024,8,1)).iloc[0]['adj_close_minor']), int(build_price_panel(raw,[s],date(2024,6,1)).iloc[0]['adj_close_minor']))"` → `12089 120890` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ✅ **Yes — and it is the only domain so far that is.** `set -a; source .env; set +a; pytest -m live tests_src/test_data_engine_probe.py` runs §6A.4's probe over the network against the K-1…K-10 known-answer set. Verified 2026-08-23: 8/8 checks PASS, including our reconstruction matching the vendor's own adjusted close. ⚠ Unset `FMP_API_KEY` and it reports **SKIPPED**, never green |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-data-engine.md` **v0.7.0** | DE-1…DE-46, CT-7.1…7.7, §5A catalog, §5C defects, §6 PIT, §6A the gate |
| `sdd/design/rel6_design/L1-feature-engineering.md` | **FE-8/FE-9/FE-10** — the consumer that depends on `adj_as_of` and the gate verdict |
| `sdd/design/rel6_design/L1-quantitative-analysis.md` | **QA-71** (the open anchor), **QA-84/85/91** (`adj_open` and its checks) |
| `sdd/design/rel6_design/L3-build-sequence.md` | B2's scope; **BS-8** (`adj_open` at B2), **BS-9** (amended — the capital base is not B2's) |
| `sdd/design/rel6_design/L4-coding-standards.md` | §1.1 layout · §5 errors (**EH-14** and its DE-46 carve-out) · §10 imports · §17 pandas · §18 CA-1…CA-9 |
| `sdd/specs/constitution.md` | **INV-1** (no look-ahead), **INV-2** (determinism), **DC-1**, **P5** |
| `data/fmp_dump/README.md` + `_MANIFEST_FINAL.csv` | the retained reference dump (DE-17) every §5A/§5C claim is checkable against |
