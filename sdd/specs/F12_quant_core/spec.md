# F12 — Quant core (D-03 `src/quant/`: horizons, evaluation protocol, method register, nomination)

> **Spec-ID:** F12 · **Status:** 🟢 **approved 2026-10-05** (Victor Truong) · **Drafted:** 2026-10-05
> ✅ Approved as drafted; `Q1` → `D6`, `Q2` → `D7`; `D8` (commission $0) added the same day.
> ✏ **Amended 2026-10-06 (Victor):** `D9` (the IC gate decides on the REALISED standard error — `AB-12`) and `D10`
> (the breadth gate becomes an implied-information-ratio test on the universe) → `AC-F12.31`, `AC-F12.32`.
> ✏ **Amended 2026-10-08 (Victor):** `D11` — a true expanding-window walk-forward beside the purged k-fold (`DX-162`)
> → `AC-F12.33`.
> ✏ **Amended 2026-10-08 (Victor):** `D12` — the residual correlation measured against EXTERNAL factors (SPY and the
> GICS sector SPDRs), reported beside the breadth gate → `AC-F12.34`.
> ✏ **Amended 2026-10-08 (Victor):** `D13` — the breadth gate's `BR` comes from the EXTERNAL **market-only** residual
> correlation (`D12`'s `rho_market`) → `AC-F12.35`.
> ✏ **Amended 2026-10-08 (Victor):** `D14` — the WALK-FORWARD gates significance (and supplies the IC the breadth gate
> pairs with `BR`); the purged k-fold is reported beside → `AC-F12.36`.
> ✏ **Amended 2026-10-09 (Victor):** `D15` — the Nomination carries its ranker's status (`rule` / `promoted` /
> `refused_informational`) and a refused ranker's failed gates → `AC-F12.37`.
> ✏ **Amended 2026-10-20 (Victor's ruling of 2026-10-11):** `D16` — the gates are MEASUREMENTS, not D-04's completion
> bar; no threshold moves (option Ⓐ; Ⓑ, lowering the thresholds, rejected). No AC: nothing in the gate code changes.
> ✏ **Amended 2026-10-20:** `D17` — the purged k-fold purges and embargoes in TRADING days, like the walk-forward
> (`DX-161`) → `AC-F12.38`.
> **Source discussion:** `sdd/design/rel1_design/L3-build-sequence.md` §2.1s (Victor, 2026-10-05): row 9
> re-scoped to **govern & close** — graduate the D-03 core that is already built, wire `src/quant/**`
> into `ownership.yaml`, and record what is out of rel-1 as declared limitations. No new capability.
> **Home:** D-03 `src/quant/` · seat 3 (this repo's nine-seat model, vision §3) · capability C8.
> **Governs:** `constitution.md` — `P5` fail loud · `AP-5` deterministic · `INV-1` no look-ahead ·
> `INV-2` determinism · `INV-014`/`ST-9` the analyst firewall · `PG-10` a claim carries its subject's
> status. Design-tier source of every rule cited here: `sdd/design/rel6_design/L1-quantitative-analysis.md`
> (`QA-n`, `CT-3.n`, §14 `AC-3.n`). Rules are cited **by id, never re-worded** (constitution §3).

---

## 1. Goal & why

`src/quant/` (22 files, 1,805 lines) is the stateless half of seat 3: the HorizonSet, the evaluation
protocol D-04's `promote()` is judged by, the MethodEntry register, and the daily `Nomination`. It came in
with the absorption and is **ungoverned** — an edit there needs only the constitution. This spec makes the
built behaviour authoritative, so the gate protects it, and states plainly which of the design doc's
criteria are met, which are gaps, and which have nothing built for them to apply to.

⚠ **Why now, measured 2026-10-05.** The 2026-09-17 figure *"26 `AC-3.x`, 81 % cited"* was **inflated by a
collision** (`DX-151`): bare `AC-3.1…3.12` also means `F3` corporate actions, and `tests/test_sdd_process.py`
uses `AC-3.1…3.7` for upstream's `F3_sdd_adoption`. Counting only D-03's own tests, **17 of 29 criteria are
met**. That is why this spec's criteria are written **`AC-F12.k`** (constitution §1.1, `DX-44`'s rule).

## 2. Scope / non-goals

**In scope:** every module under `src/quant/` as built on 2026-10-05; the D-03 criteria of
`L1-quantitative-analysis.md` §14, carried one-for-one as `AC-F12.k`.

**Non-goals (this spec):**

- ⊘ **New factors.** *(Victor, 2026-10-05 → `D2`)* The factors for rel-1 are the existing D-02 feature sets
  (`b3_minimal_v1`, `price_ohlcv_v1`, `fundamental_v1`). D-02 owns them; nothing here defines one (QA-7, QA-8).
- ⊘ **Regime handling.** *(Victor, 2026-10-05 → `D3`)* One model for all market states (§9.2 of the design
  doc). A **declared limitation**, revisited once real daily runs give observations.
- ⊘ **D-04 `src/models/`** — training, promotion, drift, inference, the retrain cadence (`MT-45…47`,
  `OR-37/38`, already built). *(Victor, 2026-10-05 → `D4`)* A separate spec if ever needed.
- ⊘ **The open research questions** `QQ-2`, `QQ-3`, `QQ-4`, `QQ-5`, `QQ-9`, `QQ-10`, `QQ-11`, `QQ-12`,
  `QQ-13`, `QQ-14`, `QQ-15`, `QQ-17`, `QQ-19`, `QQ-21`, `QQ-22`, `QQ-23` — stay in the design doc, deferred.
- ⊘ **A ranking golden case** — removed by Victor 2026-09-10 (`DX-62`, `F5` `D6`); the golden programme is
  closed (`L8` §9). Deterministic ranking is guarded by unit and property tests here.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | daily run, rank step | D-02 feature panel, HorizonSet v1 | `src/quant/signals/rank.py`, `signals/tradeable.py` → `contracts/nomination.py` |
| T2 | D-04 promotion | a model's predictions | `src/quant/backtest/engine.py` → `gates/metric_gate.py` |
| T3 | build / test | every `formula_id` in `src/` | `src/quant/methods/registry.py` |

## 4. Behaviour & reuse (the lean "how")

Nothing new is built by graduating. The behaviour is the code as it stands; §6 classifies each criterion.
Where a criterion is a **gap**, the fix is the smallest change that makes its test pass; where it is
**vacuous** (no such thing exists to test), it stays unbuilt and says so rather than receiving a test that
proves nothing (constitution §4: an example test on an invariant *"looks green and proves almost nothing"*).

## 5. Contracts (inline)

By reference, unchanged: **`CT-3.1` HorizonSet**, **`CT-3.2` BacktestSpec / BacktestResult**, **`CT-3.3`
MethodEntry**, **`CT-3.4` Nomination** — `L1-quantitative-analysis.md` §10. The persisted copy of the
nomination (`excluded[]` included) is `recommendation.json` (`L6` AB-16, closed 2026-08-27).

## 6. Acceptance criteria

> Each `AC-F12.k` carries the design doc's `AC-3.x` **verbatim**. Status as measured 2026-10-05:
> ✅ met (a test exists; it gains the `AC-F12.k` tag at implementation) · ⬜ gap · ⊘ vacuous / deferred.

**Horizons (§5)**

- **AC-F12.1** ≡ `AC-3.1` — *Every model/backtest declares its HorizonSet name and version.* → unit. ✅
- **AC-F12.2** ≡ `AC-3.2` — *Purge length is derived from max horizon; a shorter one raises.* → unit. ✅
- **AC-F12.3** ≡ `AC-3.3` — *Replicated rows (Option C) never straddle a CV fold.* → invariant/property. ✅
- **AC-F12.4** ≡ `AC-3.4` — *Labels for a horizon use only prices within that horizon (INV-1).* → invariant/property. ✅ 2026-10-05 — checked by perturbation over every row (h = 1, 5, 21); the behaviour already held, the test now pins it. The labels live in D-02 and nothing there changed.
- **AC-F12.5** ≡ `AC-3.5` — *A multi-horizon design is compared to the per-horizon single-task baseline before adoption (QA-6).* ⊘ vacuous: HorizonSet v1 adopts no multi-horizon design (one production horizon, 1m). Becomes live the day one is proposed.
- **AC-F12.6** ≡ `AC-3.6` — *The HorizonSet records its mandate justification (QA-2).* → data contract. ✅ 2026-10-05 — `HorizonSet` gains `mandate_justification` / `approved_by` / `approved_on`; v1's text is transcribed verbatim from `CT-3.1`; an empty one raises `QNT.HORIZON.UNPINNED`.

**Evaluation (§7)**

- **AC-F12.7** ≡ `AC-3.7` — *Every reported statistic carries effective N and a corrected SE.* → unit. ✅
- **AC-F12.8** ≡ `AC-3.8` — *Gates are per horizon; a pooled cross-horizon gate raises.* → unit. ✅
- **AC-F12.9** ≡ `AC-3.9` — *An uncomputable statistic reports NOT_EVALUATED, never PASS.* → unit. ✅
- **AC-F12.10** ≡ `AC-3.10` — *A gate where every candidate failed cannot report PASS (the D-18 regression).* → invariant/property. ✅ 2026-10-05 — exhaustive over every verdict combination up to three gates, and a PASS with no statistic (or a verdict outside the three) raises the new `GateVacuousError` (`QNT.GATE.VACUOUS`).
- **AC-F12.11** ≡ `AC-3.11` — *An unpinned backtest spec raises — including a missing initial_capital.* → unit. ✅
- **AC-F12.12** ≡ `AC-3.11a` — *A backtest result states costs_charged in {none, commission_only, full}.* → data contract. ✅ 2026-10-05 — ⚠ **found a defect**: with charging switched off the result still said `commission_only` beside a $0 fee. `CostModel.costs_charged` now reads `none` when off; a value outside the three raises.
- **AC-F12.13** ≡ `AC-3.11b` — *With charge_transaction_cost=true, a single-position single-round-trip backtest moves by exactly $20 (the known-answer test QA-62 requires).* → unit. ✏ **Amended by `D8`**: the $20 premise (legacy $10 fee) no longer holds — the fee is **$0.00** since 2026-10-05. Known answer: the simulator charges **exactly one flat commission per trade**, so a buy-then-sell round trip costs exactly 2 × the fee — $0.00 today, and exactly $19.90 at the old $9.95, where the mechanics stay pinned so a zero cannot hide a broken charge. ✅ 2026-10-05.
- **AC-F12.14** ≡ `AC-3.11c` — *A weight change on a HELD position is charged as a trade (QA-61).* → unit. ⬜ gap — a **confirmed spec/code disagreement**: the simulator scored each period as the MEAN of the top-N labels, which silently re-equalised every held name at every rebalance and charged $0. ✏ `D6`: **held names keep their drifted weight**; only entries and exits trade. QA-61 is then satisfied because no held name is re-weighted — and the test pins that a held name's weight at the next rebalance is its drifted weight, not 1/N. ✅ 2026-10-05.
- **AC-F12.15** ≡ `AC-3.12` — *Backtest results carry costs and are labelled not-expected-returns.* → data contract. ✅
- **AC-F12.16** ≡ `AC-3.13` — *Survivorship treatment is stated; listed-only is flagged biased.* → unit. ✅

**Method provenance (§8)**

- **AC-F12.17** ≡ `AC-3.14` — *Every formula_id in src/ resolves to a MethodEntry, or the build fails.* → invariant/property. ✅
- **AC-F12.18** ≡ `AC-3.15` — *Every MethodEntry has statement, symbols, reference, assumptions, alternatives-rejected, and a known-answer test.* → data contract. ✅
- **AC-F12.19** ≡ `AC-3.16` — *Every MethodEntry's known-answer test executes and passes.* → invariant/property. ⬜ partial: known-answer tests exist for several entries (`mde`, `rank_ic`, `rank`, `momentum`, `volatility`), but nothing links each of the 15 entries across `src/*/methods/entries/` to a test that runs, so *every* is unchecked. ✅ 2026-10-05 — `unresolved_known_answer_tests()`: every entry must name a `path.py::test_name` that resolves to a real test (which the suite then runs). ⚠ **It found three broken links on its first run** (breadth named a file only; volatility named a function that never existed; fcff's shorthand had no path) — all three entries fixed.
- **AC-F12.20** ≡ `AC-3.17` — *A method with no external reference is flagged HOUSE VARIANT (QA-22).* → data contract. ✅
- **AC-F12.21** ≡ `AC-3.18` — *Assumptions name the ones this system violates and point at the correction (QA-23).* → data contract. ✅
- **AC-F12.22** ≡ `AC-3.19` — *Changing a formula without amending its MethodEntry in the same commit fails CI (QA-25).* → invariant/property. ⬜ gap: the register cites QA-25; no check exists. A content hash of each formula's code pinned in its MethodEntry is the smallest form. ✅ 2026-10-05 — `stale_entries()`: each entry whose formula has a `FORMULA_ID` assignment pins `Code: <path> @ sha256:<16 hex>`; 10 pinned as a baseline. ⚠ The 5 entries with no assignment are a FIXED list (`UNLOCATED_FORMULAS`). ⚠ The pins reach outside `src/quant/` (D-02 valuation, D-04 zoo, D-06 sizing — PS-44: QA-20 owns the standard): editing any of those 10 files now requires re-reading and re-pinning its entry.

**Boundary & correctness**

- **AC-F12.23** ≡ `AC-3.20` — *No module in src/quant holds fitted parameters (QA-28).* → invariant/property. ✅
- **AC-F12.24** ≡ `AC-3.21` — *src/quant does not import src/models (D-04) or src/fundamental (D-01).* → invariant/property. ✅
- **AC-F12.25** ≡ `AC-3.22` — *A price-level screen reads the RAW panel, not the adjusted one (QA-10).* ⊘ vacuous: no screen is built (`screens/` does not exist). The error class exists and waits for the first screen.
- **AC-F12.26** ≡ `AC-3.23` — *Every output records contract version, as_of, adj_as_of, calendar id.* → data contract. ✅ 2026-10-05 — the `Nomination` gains `contract_version` / `adj_as_of` / `calendar_check_id`, each refused when empty; both daily paths (`b3_run`, `wiring`) pass them through as supplied (OR-1).
- **AC-F12.27** ≡ `AC-3.24` — *A stop or target produced deterministically is not altered downstream (QA-27).* ⊘ vacuous: no deterministic stop or target is produced (the quantile heads of design §9.3 are not built, `QQ-4`/`QQ-5`).
- **AC-F12.28** ≡ `AC-3.31` — *the raw measure recovers a known correlation; the residual one returns -1/(n-1) at every true rho; an unmeasurable breadth is None, never n (QA-43, QA-124, QQ-14).* → unit. ✅
- **AC-F12.29** ≡ `AC-3.32` — *an untradeable name never reaches candidates and appears in excluded[] with its reason; a name with a stale last bar is excluded even when it still prices (QA-125, QA-126).* → unit. ✅

**Gate rulings (✏ amended 2026-10-06)**

- **AC-F12.31** *(new — `D9`, `AB-12`)* — **Given** walk-forward predictions, **when** rank IC is measured, **then** the
  result keeps the per-date IC series and reports **both** standard errors — the null `corrected_se` (kept as the MDE /
  planning figure, QA-4, §5.3b) and the **realised** SE: Newey-West (Bartlett) over the per-date ICs with `h − 1` lags —
  and `ic_significance` **PASSES only if `|mean IC| ≥ 3 × realised SE`**. Too few dates for the lag window ⇒ realised SE
  is `None` ⇒ the gate is `NOT_EVALUATED`, never PASS. → unit, with a known answer. ✅ 2026-10-06
- **AC-F12.32** *(new — `D10`)* — **Given** a measured universe breadth `BR` (bets per year, `AC-F12.28`) and the mean
  IC, **when** the `breadth` gate runs, **then** its statistic is the **implied information ratio `|IC| · √BR`**
  (Grinold–Kahn) and it **PASSES only if ≥ `IR*` = 0.5** — equivalently `BR ≥ (0.5 / IC)²`. The gate **can fail at the
  1-month horizon** (the old `BR ≥ 3` could not). The held book's breadth (`n_eff` of the top-N at the universe
  correlation × rebalances per year) and its implied IR are **reported beside it, never gated**. An unmeasured `BR` or IC ⇒
  `NOT_EVALUATED`. ⚠ **Provisional** — refine after the fresh training's results. → unit. ✅ 2026-10-06

- **AC-F12.33** *(new — `D11`, `DX-162`)* — **Given** the sorted trading dates and the protocol, **when** walk-forward
  folds are made, **then** the dates are cut into the same `n_folds` contiguous test blocks as the purged k-fold; block 0
  is never tested (it has no past); each block `k ≥ 1` trains **only on dates strictly before it**, ending at least
  `purge_days` **trading days** (positions in the date list, not calendar days) before its first test date; no training
  date follows any test date. The walk-forward IC is **reported beside** the purged k-fold IC, with its own realised SE
  and per-fold ICs — **never gated** until Victor rules which protocol gates. → unit. ✅ 2026-10-08

- **AC-F12.34** *(new — `D12`)* — **Given** the universe's forward-return matrix and EXTERNAL factor returns on the
  same basis (SPY; each name's GICS sector SPDR), **when** breadth is measured, **then** each name is regressed (with
  an intercept, one β per name over the window) on the market, and separately on market + its sector ETF; the average
  pairwise correlation of each residual set is reported (`rho_market`, `rho_market_sector`), with the within-sector and
  cross-sector averages and the `n_eff` / breadth / implied IR it would give. On a synthetic panel whose residual
  correlation is known, the measure **recovers it** — and unlike `rho_residual` it is **not** pinned at `−1/(n−1)`.
  **Reported, never gated** until Victor rules how breadth is measured. → unit, with a known answer. ✅ 2026-10-08

- **AC-F12.35** *(new — `D13`)* — **Given** the external measurement of `AC-F12.34`, **when** the `breadth` gate runs,
  **then** its `BR` is `n_eff(rho_market) × 252/h` — the residual correlation after the EXTERNAL market factor only,
  not after the sector factor and not the raw ρ — and its `why` names that basis. No external market factor ⇒ the gate
  is `NOT_EVALUATED` (never the raw ρ, never `n`). The raw and market+sector figures stay reported beside it. → unit. ✅
  2026-10-08

- **AC-F12.36** *(new — `D14`)* — **Given** both out-of-sample measurements (`AC-F12.33`), **when** the gates run,
  **then** `ic_significance` and `breadth` read the **walk-forward** IC (its mean and its realised Newey-West SE), and
  the purged k-fold IC is reported beside, never gated. A walk-forward that produced no prediction ⇒ both IC-reading
  gates `NOT_EVALUATED` — never the k-fold in its place. → unit. ✅ 2026-10-08

- **AC-F12.37** *(new — `D15`)* — **Given** a Nomination, **when** it is built or serialised, **then** it carries
  `ranker_status` ∈ {`rule`, `promoted`, `refused_informational`} and, for `refused_informational`, a non-empty
  `refused_gates`; any other status, or a refused status with no gates, is REFUSED (`QNT.NOMINATION`). → data contract.
  ✅ 2026-10-09

- **AC-F12.38** *(new — `D17`, `DX-161`)* — **Given** the sorted trading dates and the protocol, **when** purged k-fold
  folds are made, **then** a training date is at least `purge_days + 1` **positions** (trading days) before the test
  block's first date, or at least `purge_days + embargo_days + 1` positions after its last — positions in the date list,
  never calendar days; the test blocks are unchanged. → unit. ✅ 2026-10-20

**Declared limitation**

- **AC-F12.30** *(new — `D3`)* — **Given** any `Nomination` or `BacktestResult`, **when** it is serialised,
  **then** it carries the fixed sentence (`D7`) *"Not regime-conditioned: one model is fitted across all
  market states; a result from one regime is not evidence for another."* → data contract. (`PG-10`) ✅ 2026-10-05

**Tally (2026-10-05, after implementation):** 30 · ✅ **27** · ⊘ 3 vacuous (`.5` `.25` `.27`). ✏ 2026-10-06: + `.31`, `.32` ✅ built the same day → **29 / 32 green**, 3 vacuous. ✏ 2026-10-08: + `.33`–`.36` → **33 / 36 green**, 3 vacuous. ✏ 2026-10-09: + `.37` → **34 / 37 green**. ✏ 2026-10-20: + `.38` → **35 / 38 green**.

## 7. Decisions

- **`D1` — govern & close, no new capability** *(Victor, 2026-10-05)*. Rejected: ⓑ graduate and also build
  new quant capability (needs definitions nobody has written — memory rule *no domain content until
  decided*); ⓒ leave `src/quant/` ungoverned (the gate would keep protecting nothing there).
- **`D2` — the factors are the existing D-02 feature sets** *(Victor, 2026-10-05)*. Rejected: a new
  factor list now; deferral (nothing to defer — the sets exist and the ranker reads them).
- **`D3` — regime handling is a declared limitation** *(Victor, 2026-10-05)* → `AC-F12.30`. Rejected:
  defining regimes now (policy, unmeasured); dropping it unrecorded (a silent limit, `PG-10`).
- **`D4` — `src/quant/**` only** *(Victor, 2026-10-05)*. Rejected: one spec for all of seat 3 including
  `src/models/` (larger; D-04 is governed in practice by its tests and `MT-n`).
- **`D6` — held names drift; only entries and exits trade** *(Victor, 2026-10-05, was `Q1`)* → `AC-F12.14`.
  The period return is the drifted-weight return of the book, not the mean of the picked names. Matches how
  a small flat-fee book trades: nobody pays $10 to trim a name they still hold. Rejected: ⓑ charge one trade
  per held name re-equalised (QA-61 read literally; adds cost for a trade the fund would not make); ⓒ keep
  the uncharged re-equalisation and declare it (an approximation where the correct model is cheap).
  ⚠ It changes every backtest return the simulator produces.
- **`D7` — the regime sentence** *(Victor, 2026-10-05, was `Q2`)* → `AC-F12.30`, verbatim as proposed.
  Rejected: the shorter *"Not regime-conditioned (one model for all market states)."*
- **`D8` — the commission is $0.00** *(Victor, 2026-10-05)* → `AC-F12.13`, `FLAT_COMMISSION`. *"BMO InvestorLine
  has changed policy that allows completely free buying or selling, across all of my accounts."* Was $9.95,
  measured over 137 real orders (D-11 RC-43). Rejected (offered as `.13`'s options before the policy was
  stated): ⓐ 2 × $9.95 plus a charged final-basket sale; ⓑ 2 × $9.95 with the final basket unsold.
  ⚠ Consequences: `cost_survival` is now gross vs gross − 0, so it can no longer fail a signal on commission;
  spread and slippage (QA-49) are the only costs left and they are unmodelled — every net figure overstates
  by that unmeasured amount. The mechanics tests run at an explicit $9.95.
- **`D9` — the IC gate decides on the REALISED standard error** *(Victor, 2026-10-06; closes L6 `AB-12`)* →
  `AC-F12.31`. On the August 2026 fit (500 names, ten years, mean IC 0.0203) the null SE gave t = 4.94 (PASS) and the
  realised one t = 1.42 (fail): the skill came and went (≈0.034 in 2016-18 and 2024-26, ≈0.009 in 2018-20 and 2022-24),
  and the variance a holder lives through is the realised one. Newey-West with `h − 1` lags because consecutive 21-day
  labels overlap. Rejected: ⓐ keep the null SE as the acceptance test (it answers *"could luck do this?"* — a planning
  question, §5.3b's own word is MDE); ⓑ require both (equivalent to ⓒ whenever skill varies); ⓓ null SE plus a
  stability rule (more rules, less standard).
- **`D10` — the breadth gate is an implied information ratio, measured on the UNIVERSE** *(Victor, 2026-10-06)* →
  `AC-F12.32`. `IR ≈ IC · √BR` (Grinold–Kahn) pairs the IC and the breadth **of the same decisions**, and the IC is
  measured on the universe ranking — so the breadth is too. `IR* = 0.5`. ⚠ The old gate (`BR ≥ 3`) **could not fail** at
  1m: even at ρ = 1, `n_eff = 1` and 12 rebalances give `BR = 12`. ⚠ Expect the new one to refuse a weak signal: at
  IC 0.02 it needs `BR ≈ 600`; a 500-name universe with ρ ≈ 0.25 offers ≈ 48 (illustrative). Rejected: ⓐ the held book
  as the gated population (Victor's first ruling — the IC is not measured on the held book, so IC × √BR(held) mixes two
  populations; it stays as a reported diagnostic); ⓑ keep `BR ≥ 3` (decoration, QA-17); ⓒ drop the gate. **Provisional**:
  refine after the first fresh training run.
- **`D11` — a true walk-forward is measured beside the purged k-fold** *(Victor, 2026-10-08)* → `AC-F12.33`. ⚠ Found
  writing lecture L8 (`DX-162`): the console's *"walk-forward"* was **purged k-fold** — block 0 (2016–18) was tested by a
  model trained on 2018–26. Labels cannot leak across the purge, but a model that learned later regimes was grading an
  earlier one, which confounds the fold decay (0.052 → 0.013) with look-back knowledge. Expanding window answers *"what
  would the fund have known then?"* exactly. Purge in **trading** days here (the k-fold's calendar-day purge is `DX-161`,
  still open). Rejected: ⓐ replace the k-fold (it uses every block, and its numbers are the record so far); ⓑ gate on the
  walk-forward now (fewer test dates — 4 of 5 blocks — so a wider SE; which protocol gates is a ruling, not a default).
- **`D12` — measure the residual correlation against EXTERNAL factors** *(Victor, 2026-10-08)* → `AC-F12.34`. ★ Why:
  after fit 3 (IC 0.036) the breadth gate is the only refusal, and its verdict turns on one number — pass if the
  residual ρ is below ≈ 0.060, fail above (lecture L8 §7.8). `rho_residual` cannot answer: it removes an equal-weight
  factor built from the same names, which forces `−1/(n−1)` (`AC-F12.28`). SPY and the sector SPDRs are priced outside
  the calculation. ⚠ **Caveats, stated:** they are cap-weighted and HOLD these names, so a mega-cap's own move is partly
  in its factor (small, larger in thin sectors such as Real Estate and Materials); XLC exists only from 2018-06, so a
  Communication Services name's sector residual starts there; GICS is today's (DE-77). Rejected: ⓐ keep raw ρ (it
  counts the market as a bet, which an information ratio — active return over benchmark — does not hold); ⓑ PCA
  factors from the panel itself (built from the same names, the `−1/(n−1)` trap again, more subtly).
- **`D13` — the breadth gate uses the external MARKET-ONLY residual ρ** *(Victor, 2026-10-08)* → `AC-F12.35`. Measured
  2026-10-08 on 509 names, split-adjusted: raw ρ 0.294 (n_eff 3.4), market-only 0.057 (n_eff ≈ 17, BR ≈ 203), market +
  sector 0.012 (n_eff 73, BR 881); break-even at IC 0.036 is 0.060. ★ Why market-only: an information ratio is on active
  return, so the shared market move is not a bet — but the ranker is **not sector-neutral**, so five names from one
  sector are correlated bets and removing the sector factor would count a sector tilt as diversification. Rejected:
  ⓐ raw ρ (counts the market as a bet; at ρ 0.29 the gate needs IC ≈ 0.08 — unpassable for a realistic monthly signal);
  ⓑ market + sector (correct only for a sector-neutral ranking — revisit if one is adopted); ⓒ fall back to raw ρ when
  the external factor is missing (a substitution, QA-43 — `NOT_EVALUATED` instead). `IR* = 0.5` unchanged (`D10`).
- **`D14` — the walk-forward gates significance** *(Victor, 2026-10-08)* → `AC-F12.36`. ★ Why: the gate protects real
  money (`PG-2`), and only the walk-forward answers *"would this have worked in real time?"*; the data is
  non-stationary (the 2020–22 block carries no signal; the signal fades across the decade), which is exactly where a
  k-fold that trains on later regimes flatters. ★ **Ruled before the clean refit**, so its result cannot steer the
  choice — on fit 3 the k-fold passed (t 3.23) and the walk-forward did not (t 2.70). The breadth gate takes the same IC
  (`IR = IC · √BR` pairs the IC and the breadth of the same decisions). The simulation keeps the k-fold predictions
  (all five blocks) and feeds only `cost_survival`. Rejected: ⓐ the k-fold (more power, but optimistic on the regime
  question that is this model's weakness); ⓑ require both (in practice the walk-forward, plus a rule that adds no
  information); ⓒ walk-forward with a lower t (the t ≥ 3 bar answers the profession's search, which has not changed);
  ⓓ run both and keep the better (choosing the answer).
- **`D15` — the nomination says what kind of ranker made it** *(Victor, 2026-10-09: card option b)* → `AC-F12.37`.
  The card may be ranked by a REFUSED model (D-04 MT-67, D-08 OR-58); PG-10 then requires every downstream output to
  say so, and the nomination is where the status must ride (D-12 and D-09 re-derive nothing). Rejected: ⓐ D-12 reading
  the model store to find out (D-12 originates nothing); ⓑ a free-text note (unenforceable).
- **`D16` — the gates are measurements, not D-04's completion bar** *(Victor, 2026-10-11: option Ⓐ)*. D-04 closes as
  **functionally complete, skill unproven**: `ic_significance`, `breadth` and `cost_survival` keep computing and
  printing exactly as `D9`, `D10`, `D13`, `D14` define them — walk-forward t ≥ 3, IR ≥ 0.5 on the market-only residual
  breadth — and **no threshold moves**. Passing them is no longer the condition for calling D-04 done, and no longer
  blocks work on any other domain. What a failed gate still does is unchanged: promotion refuses (D-04 MT-17, MT-52),
  and a refused model may rank the card only as designated and labelled (`D15`, MT-67, DN-41, RP-55) — never
  actionable. Victor's reason, verbatim: *"this D-04 ML model may never process any skills with my limited computing
  and news capacity, as well as the nature of predicting future stocks' ranking."* Rejected: Ⓑ lower the thresholds so
  fit 4 passes (e.g. t ≥ 2, IR ≥ 0.3) — it would promote fit 4, drop the label, and with a thesis could make a card
  actionable; against it `PG-2` (his own capital wins on any number someone trades on), the bar was fixed in advance so
  a result could not move it (`D14`), and four fits on one decade are four draws.
- **`D17` — the purged k-fold purges in trading days** *(2026-10-20, closes `DX-161`; hand-over 2026-10-11 §3.2)* →
  `AC-F12.38`. `make_folds` removed `timedelta(days=purge_days)` — 63 calendar ≈ 43 trading days — while `purge_days`
  is `max(trading_days)` of the HorizonSet (QA-18) and the walk-forward (`D11`) already counts positions. The embargo is
  counted the same way, so the protocol has one unit. Safe until now only because the selection label is 21 days.
  Rejected: converting days with a 252/365 factor (an approximation where the exact count is free). ⚠ The k-fold now
  trains on slightly fewer dates than fits 1–4 did; their recorded numbers stand as measured.
- **`D5` — `AC-F12.k`, not bare `AC-12.k`** — D-12 Decision's upstream criteria are `AC-12.x`
  (constitution §1.1, `DX-44`).

## 8. Open questions

*None.* `Q1` → `D6`, `Q2` → `D7` (Victor, 2026-10-05).

## 9. Traceability (spec → test → code)

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-F12.1 | `tests_src/test_quant_b3.py::test_ac_3_1_the_horizon_set_is_named_and_versioned` | `src/quant/horizons/horizon_set.py` |
| AC-F12.2 | `tests_src/test_quant_b3.py::test_ac_3_2_purge_shorter_than_the_longest_horizon_raises` | `src/quant/horizons/horizon_set.py` · `backtest/protocol.py` |
| AC-F12.3 | `tests_src/test_quant_evaluation.py::test_qa19_cv_groups_on_ticker_and_date` | `src/quant/backtest/protocol.py` |
| AC-F12.4 | `tests_src/test_quant_b3.py::test_ac_f12_4_a_label_reads_only_prices_inside_its_horizon` | `src/feature_engineer/contracts/labels.py` (read only) |
| AC-F12.5 | ⊘ vacuous | — |
| AC-F12.6 | `tests_src/test_quant_b3.py::test_ac_f12_6_the_horizon_set_records_its_mandate_justification` | `src/quant/horizons/horizon_set.py` |
| AC-F12.7 | `tests_src/test_quant_evaluation.py::test_qa4_every_statistic_carries_effective_n_and_a_corrected_se` | `src/quant/metrics/ic.py` |
| AC-F12.8 | `tests_src/test_quant_evaluation.py::test_qa16_gates_are_evaluated_per_horizon_and_never_pooled` | `src/quant/gates/metric_gate.py` |
| AC-F12.9 | `tests_src/test_quant_evaluation.py::test_qa17_an_uncomputable_statistic_is_not_evaluated_never_a_pass` | `src/quant/gates/metric_gate.py` |
| AC-F12.10 | `tests_src/test_quant_evaluation.py::test_ac_f12_10_a_gate_set_where_every_gate_failed_cannot_pass` · `::test_ac_f12_10_a_pass_with_no_statistic_is_vacuous_and_raises` | `src/quant/gates/metric_gate.py` · `src/quant/errors.py` |
| AC-F12.11 | `tests_src/test_quant_evaluation.py::test_qa11_an_unpinned_spec_is_inadmissible_as_evidence` · `tests_src/test_quant_portfolio.py::test_a_simulation_without_a_capital_base_raises` | `src/quant/contracts/backtest.py` · `backtest/portfolio.py` |
| AC-F12.12 | `tests_src/test_quant_portfolio.py::test_ac_f12_12_costs_charged_is_one_of_three_and_says_none_when_off` | `src/quant/backtest/costs.py` · `engine.py` · `portfolio.py` |
| AC-F12.13 | `tests_src/test_quant_portfolio.py::test_ac_f12_13_a_round_trip_costs_exactly_two_commissions` | `src/quant/backtest/costs.py` · `backtest/portfolio.py` |
| AC-F12.14 | `tests_src/test_quant_portfolio.py::test_ac_f12_14_a_held_name_keeps_its_drifted_weight` · `::test_ac_f12_14_an_entry_takes_the_exits_proceeds` | `src/quant/backtest/portfolio.py` |
| AC-F12.15 | `tests_src/test_quant_evaluation.py::test_the_result_carries_its_label_and_its_formula_ids` | `src/quant/backtest/engine.py` |
| AC-F12.16 | `tests_src/test_quant_evaluation.py::test_qa14_a_survivorship_blind_backtest_is_biased_not_a_result` | `src/quant/contracts/backtest.py` |
| AC-F12.17 | `tests_src/test_quant_b3.py::test_ac_3_14_every_formula_id_in_src_resolves_to_a_methodentry` | `src/quant/methods/registry.py` |
| AC-F12.18 | `tests_src/test_quant_b3.py::test_ac_3_15_every_methodentry_carries_the_six_required_fields` | `src/quant/methods/registry.py` |
| AC-F12.19 | `tests_src/test_quant_b3.py::test_ac_f12_19_every_methodentry_names_a_known_answer_test_that_exists` · `::test_ac_f12_19_a_dangling_known_answer_link_is_reported` | `src/quant/methods/registry.py` |
| AC-F12.20 | `tests_src/test_quant_b3.py::test_ac_3_17_a_house_variant_is_flagged_as_one` | `src/quant/methods/registry.py` |
| AC-F12.21 | `tests_src/test_quant_b3.py::test_ac_3_18_assumptions_name_the_ones_this_system_violates` | `src/quant/methods/registry.py` |
| AC-F12.22 | `tests_src/test_quant_b3.py::test_ac_f12_22_every_located_formula_is_pinned_to_its_code` · `::test_ac_f12_22_a_code_change_without_its_entry_is_stale` | `src/quant/methods/registry.py` · `src/*/methods/entries/*.md` |
| AC-F12.23 | `tests_src/test_quant_b3.py::test_ac_3_20_and_3_21_stateless_and_no_forbidden_imports` | `src/quant/**` |
| AC-F12.24 | `tests_src/test_quant_b3.py::test_ac_3_20_and_3_21_stateless_and_no_forbidden_imports` | `src/quant/**` |
| AC-F12.25 | ⊘ vacuous | — |
| AC-F12.26 | `tests_src/test_quant_b3.py::test_ac_f12_26_a_nomination_records_its_provenance` | `src/quant/contracts/nomination.py` · `src/orchestration/jobs/b3_run.py` · `src/orchestration/jobs/wiring.py` |
| AC-F12.27 | ⊘ vacuous | — |
| AC-F12.28 | `tests_src/test_quant_breadth.py` (raw · residual · unmeasurable) | `src/quant/metrics/breadth.py` |
| AC-F12.29 | `tests_src/test_quant_tradeable.py` (delisted · absent · stale) | `src/quant/signals/tradeable.py` |
| AC-F12.30 | `tests_src/test_quant_b3.py::test_ac_f12_30_both_outputs_state_the_regime_limitation` | `src/quant/contracts/nomination.py` · `contracts/backtest.py` |
| AC-F12.31 | `tests_src/test_quant_gates_d9_d10.py` (Newey-West known answers · the August case FAILs · no realised SE ⇒ NOT_EVALUATED) | `src/quant/metrics/ic.py` · `gates/metric_gate.py` |
| AC-F12.32 | `tests_src/test_quant_gates_d9_d10.py` (IR = IC·√BR · boundary · can fail at 1m · held book reported, never gated) | `src/quant/gates/metric_gate.py` · `metrics/breadth.py` |
| AC-F12.33 | `tests_src/test_quant_walk_forward.py` (past only · block 0 untested · purge in trading days · same blocks as k-fold) | `src/quant/backtest/protocol.py` |
| AC-F12.34 | `tests_src/test_quant_breadth_external.py` (recovers a known residual ρ · not pinned at −1/(n−1) · within/cross split · missing factor ⇒ None) | `src/quant/metrics/breadth.py` |
| AC-F12.35 | `tests_src/test_quant_breadth_external.py::test_ac_f12_35_*` (BR from market-only ρ · why names the basis · no market factor ⇒ NOT_EVALUATED) | `src/quant/metrics/breadth.py` · `gates/metric_gate.py` · `src/models/train/__main__.py` |
| AC-F12.36 | `tests_src/test_models_train_walk_forward.py::test_ac_f12_36_*` (the gates read the walk-forward IC · the k-fold is reported, not gated · no walk-forward ⇒ NOT_EVALUATED) | `src/models/train/__main__.py` · `src/models/train/run.py` |
| AC-F12.37 | `tests_src/test_card_refused_ranker.py::test_ac_f12_37_*` | `src/quant/contracts/nomination.py` |
| AC-F12.38 | `tests_src/test_quant_walk_forward.py::test_ac_f12_38_*` (purge before · purge + embargo after, in positions) | `src/quant/backtest/protocol.py` |

✅ 2026-10-05: the 17 pre-existing tests now carry their `AC-F12.k` id in the docstring; 9 criteria were built test-first the same day. Suite **2,572 pass / 1 red (`J-07`)**.
