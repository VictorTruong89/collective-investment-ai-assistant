# F12 — Quant core (D-03 `src/quant/`: horizons, evaluation protocol, method register, nomination)

> **Spec-ID:** F12 · **Status:** 🟢 **approved 2026-10-05** (Victor Truong) · **Drafted:** 2026-10-05
> ✅ Approved as drafted; `Q1` → `D6`, `Q2` → `D7`; `D8` (commission $0) added the same day.
> ✏ **Amended 2026-10-06 (Victor):** `D9` (the IC gate decides on the REALISED standard error — `AB-12`) and `D10`
> (the breadth gate becomes an implied-information-ratio test on the universe) → `AC-F12.31`, `AC-F12.32`.
> ✏ **Amended 2026-10-08 (Victor):** `D11` — a true expanding-window walk-forward beside the purged k-fold (`DX-162`)
> → `AC-F12.33`.
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

**Declared limitation**

- **AC-F12.30** *(new — `D3`)* — **Given** any `Nomination` or `BacktestResult`, **when** it is serialised,
  **then** it carries the fixed sentence (`D7`) *"Not regime-conditioned: one model is fitted across all
  market states; a result from one regime is not evidence for another."* → data contract. (`PG-10`) ✅ 2026-10-05

**Tally (2026-10-05, after implementation):** 30 · ✅ **27** · ⊘ 3 vacuous (`.5` `.25` `.27`). ✏ 2026-10-06: + `.31`, `.32` ✅ built the same day → **29 / 32 green**, 3 vacuous. ✏ 2026-10-08: + `.33` → **30 / 33 green**, 3 vacuous.

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

✅ 2026-10-05: the 17 pre-existing tests now carry their `AC-F12.k` id in the docstring; 9 criteria were built test-first the same day. Suite **2,572 pass / 1 red (`J-07`)**.
