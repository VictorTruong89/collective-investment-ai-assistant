# L9 — Go-live checklist (`MS-0`, L3 §2.1p row 10)

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** A preparation list, not a plan of record.
> **Status:** DRAFT · **Opened:** 2026-10-05 · **Source:** `_TEMP_handover_2026-10-05.md` Task 3, L3 §2.1s.
> ⚠ **Every step below is Victor's.** Nothing here was spent, switched or enabled while writing it. Costs are
> list-price estimates from measured traces (`tools/spend_report.py`, fixed 2026-10-05), priced at
> `claude-opus-5` $5 / $25 per million input / output tokens.

## ✅ Decisions taken — Victor, 2026-10-05

| step | decision |
|---|---|
| 1 · G1 daily thesis | ✅ **ⓑ — card only; theses on demand.** The daily run does not author a thesis |
| 5 · thesis cadence | ✅ **only on Victor's manual command** — no scheduled or automatic re-authoring |
| 3 · budget `QI-2` | ⏸ **no figure yet** — pending real-run tests and reviews |
| 4 · transport switch | ⛔ **do NOT turn on the paid Anthropic API yet.** Dev and on-demand runs stay on the subscription |
| FMP | ✅ **OK to use** — fixed monthly subscription (standing approval unchanged) |
| 2 · API spot-check | ⏸ not approved — it would be a paid API call, which step 4 rules out for now |

⚠ Recorded only — nothing was run, scheduled or switched when these were noted.

## 0. Where it stands (measured 2026-10-05)

| | |
|---|---|
| API spend to date | **$72.41 over 105 calls**, none since 2026-09-17. 89 later calls ran on the subscription ($99.36 notional, **not** spend). ⚠ Until today the report counted those as spend ($137.18) — fixed, with a test |
| Daily run | ⛔ **not scheduled.** The only user timer is `snapshot-analyst-estimates` (weekdays 18:30 NY). `Linger=no`, so user timers run only while Victor is logged in |
| Ranker | ⛔ **no promoted model** (`.state/models` absent) → the card ranks on the deterministic rule `z(mom_21)·vol_21·√21`, informational (`PG-10`, DN-39). Last fit: walk-forward IC 0.0203, *t* = 1.42 — refused |
| Thesis in the daily graph | ⚠⚠ **NOT the thesis that was built** — see G1 |
| Commission | **$0** since 2026-10-05 (F12 `D8`) |

## 1. ⚠⚠ G1 — the daily graph authors the OLD thesis

`src/orchestration/jobs/graph.py` → `thesis` job → `src.fundamental.thesis.author_for` → `run.author_once`:
**three calls** — `J-11@v1`, `J-15@v1`, `J-16@v1` — with `scorecard={}` and confidence `UNMEASURED`. No Stage A
extraction, no J-01…J-10, no F10 valuation, no F11 base rates, no consensus, and the falsifier prompt is `v1`,
not the `J-15 v3` the fourth MU thesis needed. The **32-block `CT-9.2` thesis** built and verified since
September runs **only** through `tools/run_thesis_once.py`, over hand-built MU fixtures (filings, sector file,
consensus). `entrypoint.py`'s `THESIS_ASSEMBLER_MISSING` comment is itself stale (`bundle_for` exists).

| option | what it means | effort | cost |
|---|---|---|---|
| ⓐ wire the 32-block runner into the daily graph | generalise `run_thesis_once` past MU: EDGAR filing fetch + conversion per ticker, a sector file per industry (today: memory only), consensus from the snapshot | ⚠ several sessions; needs a spec amendment (D-01 / F9) | per thesis, §3 |
| ⓑ go live quant-only; thesis on demand | the card stays informational; Victor runs `run_thesis_once` by hand for a name he is considering | none | per run, §3 |
| ⓒ go live with the old 3-call path | cheapest, but it is not the analysis the project measured, and its falsifiers predate DX-139/144/147 | none | ~3 calls/name |

★ Recommendation: **ⓑ now, ⓐ as the next build** — ⓒ would put an unmeasured analysis on a card.
✅ **Decided ⓑ** (Victor, 2026-10-05). ✅ **The old path was REMOVED the same day** (L3 §2.1s, `DX-153`): the daily graph is `daily_inference@v8` with no `thesis`/`observe` job and no `--thesis` flag. Restore: `git apply -R sdd/archive/2026-10-05_removed_old_thesis_path.patch`.

## 2. The steps

| # | step | what Victor decides / does | cost | depends on |
|---|---|---|---|---|
| 1 | **G1** | ⓐ / ⓑ / ⓒ above | — | — |
| 2 | **API spot-check of signed golden cases** (CLAUDE.md house rule) | approve a sample, per call. All 53 cases come from **15 distinct recorded calls**; re-running all 15 ≈ **$8.60**. Proposed sample: 5 calls covering 31 cases — E-01 MU (11 cases), E-01 AMD (9), E-02 MU (9), J-01, J-05 ≈ **$3.10** | $3–9 | — |
| 3 | **Budget `QI-2`** (`L2-shared-infrastructure`, GW-20) | a number and a period. ⚠ D-01 §7.4a's *$624/yr at `k_cov=3`* predates the 32-block thesis and no longer holds — see §3 | — | 1, 5 |
| 4 | **Transport switch** | set `CIA_LLM_TRANSPORT=anthropic_api` **for the daily run only**, with `ANTHROPIC_API_KEY` in its environment; dev stays on the subscription. Every runner prints the live transport | per §3 | 2, 3 |
| 5 | **Thesis cadence** | which names, how often, which `k`. The cost driver by far (§3) | — | 1 |
| 6 | **Daily timer** | a thin systemd user timer at 10:00 America/New_York (OR-30, OR-40); and `loginctl enable-linger` if it must run while logged out (also fixes the snapshot timer) | $0 | 1 |
| 7 | **Delivery** | SMTP credentials in the environment for `--deliver` (RP-50); a failed send fails the run (OR-50) | $0 | 6 |
| 8 | **Sector file v2** | switch `DEFAULT_SECTOR` to `memory_v1_2025-06-26_e15_v2.json` (Victor 2026-10-05: *at go-live*). Re-hashes every downstream bundle | $0 | 1ⓐ/ⓑ |
| 9 | **`E-14` news + a news snapshot** | FMP news is standing-approved but only **~92 days deep** — a snapshot like `snapshots/analyst-estimates/` must run for months before `E-14` has history. ★ Starting the snapshot now costs nothing and cannot be backfilled later | $0 (FMP) | — |
| 10 | **`J-18` event briefs** | needs the event workflow designed first (deferred by Victor) | spec first | — |
| 11 | **Model retrain under F12** — ✏ expanded in **§5** | `D6` (drift weights) and `D8` ($0 fee) change every backtest, so the last refusal no longer describes the current simulator. A retrain + gate run is local CPU (no API). `cost_survival` can no longer fail on commission; `ic_significance` still decides | $0 | — |
| 12 | **Retire `../ai-investment-pipeline`** (`MS-8.9`) | archive read-only, **do not delete**; `MS-8.1` (clean tree + tag) is still unmet. Repo stays private | $0 | — |
| 13 | **`DX-152`** | D-11's merged-order detection loses its fee evidence at $0 — ⓐ date-switch · ⓑ accept and state · ⓒ measure the first free export | $0 | — |
| 14 | **Open findings** | `DX-57 60 61 78 79 87 89–92 134`, partial `DX-44 71 80` — none blocks go-live by itself; review which must close first | — | — |

## 3. What a daily run would cost (estimates, stated assumptions)

Measured per-call inputs: an extraction over one 10-Q ≈ 76 k in / 2–12 k out ≈ **$0.42–0.69**; a Stage B–D
judgement over the full bundle ≈ 240–490 k in ≈ **$1.29–2.71** uncached. Whole theses: **$16.93** (first MU, 4 runs)
and an estimated **$11.38** with prompt caching (DX-127, never validated live).

| scenario (per year, ~252 trading days) | assumption | ≈ cost |
|---|---|---|
| quant-only card (G1 ⓑ) | no LLM call | **$0** |
| on-demand theses | 2 per month × k=1 × $11–17 | **$260–410** |
| per-filing re-author, top-3 | 3 names × 4 filings × k=3 × $11–17, plus ~1 new name/month × k=3 | **$800–1,200** |
| ⚠ daily re-author, top-3 | 3 × k=3 × $11 every trading day | **~$25,000** — not a real option |

★ The cadence (step 5) moves the bill by two orders of magnitude; the transport switch (step 4) only decides
whether it is paid at all.

## 4. What is free and could start before go-live

Steps 6 (timer), 9 (news snapshot), 11 (retrain), 12 (archive) and 13 (DX-152) spend nothing. ⚠ Step 9 is the
only one with a clock on it: every day without a snapshot is a day of news history `E-14` will never have.

## 5. ★ D-04 — the ranker model (`src/models/`) — added 2026-10-05

> ✅ **Victor's decisions (2026-10-05):** pull **fresh** OHLCV data, **train a fresh model**, **backtest again** ·
> **no spec for D-04 now** · **retraining is MANUAL** (by his command, like theses). Recorded only; nothing run.
>
> ✅ **Rulings, 2026-10-06 (Victor):** **`AB-12` → the REALISED standard error** decides acceptance (Newey-West with
> `h−1` lags preferred), the null SE stays as the MDE / planning figure · **breadth gate → `BR ≥ (IR*/IC)²` with
> `IR* = 0.5`**, measured on the held book. ⚠ The breadth design is **provisional: refine it after the fresh training and
> backtest**, once there are results to analyse. Recorded only — neither is built yet.

> ★★ **State on 2026-10-20 — D-04 CLOSED as *functionally complete, skill unproven*** (Victor, 2026-10-11: option Ⓐ —
> F12 `D16`, MT-68). §5.1–5.5 below are the 2026-10-05/06 record and are kept as written; this box is today.
>
> | | state |
> |---|---|
> | pipeline | sweep → train (fit + both out-of-sample protocols + simulation + breadth + gates) → hold for review → promote or designate → rank the card → shadow trial. Operator's page: `src/models/README.md` |
> | gates | built and unchanged (F12 `D9`, `D10`, `D13`, `D14`). ★ **Measurements, not D-04's completion bar**; no threshold moves (Ⓑ rejected) |
> | fits | four on 2016–2026; **fit 4** `sha256:8200ada7…` (splits applied) walk-forward IC 0.0296, t 2.51 — **refused** (`ic_significance`, `breadth`); `cost_survival` passes. No further fits unless Victor asks — then one pre-registered attempt (#5) |
> | card | ranked by fit 4, **designated** refused informational ranker (MT-67, 2026-10-10); never actionable (DN-41). ✅ **first live run 2026-10-20** (`…-c04583`, 508 names, #1 MRNA, not actionable) after `DX-170`…`DX-173` were fixed. Each run needs a same-day `ingest events --universe sp500 --years 1` |
> | shadow trial | started 2026-10-09, frozen on fit 4; one snapshot (2026-10-08). Next `record` + first `score` on or after **2026-11-06** |
> | promotion | none. `--approve` stays available; it still cannot override a failed gate (MT-17, MT-52) |
> | defects closed 2026-10-20 | `DX-161` (k-fold purge in trading days, F12 `D17`), `DX-169` (daily run dates itself in New York, OR-59), the split-count print (AC-4.50); from the first live card `DX-170` (DE-82) · `DX-171` (OR-60; PSKY/WBD removed) · `DX-172` (OR-61) · `DX-173` (RC-69) |
> | retrain cadence | manual, by Victor's command (unchanged) |

### 5.1 Where it stands

| | state |
|---|---|
| code | built and unit-tested: `python -m src.models.train` (fit → D-03 backtest → gates → `decide_promotion`), artifact store, drift, inference. Ungoverned by any spec (F12 `D4`; no D-04 spec by decision) |
| price data | **no local OHLCV store** — training and the daily run fetch from FMP at run time (`src/models/train/run.py::fetch_prices`). FMP is fixed-rate and standing-approved |
| model | **none** — `.state/models` does not exist; the card ranks on the rule `z(mom_21)·vol_21·√21`, informational |
| backtest | **none under the current simulator.** The only fit (2026-08-27: 497 names, 10 years, mean IC 0.0203) predates F12 `D6` (held names drift) and `D8` ($0 fee) |
| retrain cadence | code for *first trading day of the month* exists (`OR-37/38`, `MT-45…47`) but nothing schedules it — ✅ manual by decision |

### 5.2 ⚠⚠ Promotion is AUTOMATIC — and today two of three gates cannot refuse

`src/models/train/__main__.py` ends with `decide_promotion(...)`: when every required gate passes it writes
`promotion.json`, and **the next daily run scores the card with that model** (`entrypoint._incumbent_model`). No human
step sits in between. On the August fit the gates read:

| gate | August 2026 | today | why |
|---|---|---|---|
| `ic_significance` | PASS (t = 4.94 on the null SE) | **would PASS again** on a similar fit | `AB-12` — see 5.3 |
| `cost_survival` | NOT_EVALUATED (no simulation then) | **passes whenever gross return > 0** | F12 `D8`: the fee is $0, so net = gross |
| `breadth` | NOT_EVALUATED (not measured then) | **cannot fail at the 1-month horizon** | see 5.4 |

⇒ **A fresh retrain today would very likely promote itself** on a signal whose realised t was 1.42 in August — the
opposite of *verification by the fund manager*. ★ Suggested order: decide 5.3 and 5.4 (or hold promotion for review,
5.5 ①) **before** the fresh training run.

### 5.3 `AB-12` — which standard error the IC gate uses (Victor's ruling, postponed 2026-08-28 as AB-25 #2)

The gate asks *"is the mean rank IC far enough from zero?"* — `t = mean IC / SE`, PASS if `|IC| ≥ 3 × SE`. Two SEs:

| | formula | August value | t | answers |
|---|---|---|---|---|
| **null SE** (current, `corrected_se`) | `√( h / ((n−1)·T) )` — the spread per-date IC would have **if the model had no skill**, divided down for overlapping 21-day labels | 0.00411 | **4.94** | *"could pure luck produce this?"* — a **power / planning** figure (§5.3b calls it the MDE, *"the bar, not a prediction"*) |
| **realised SE** | `sd(per-date IC) / √(T/h)` — the spread the IC **actually showed**, same overlap divisor | 0.01433 | **1.42** | *"is the skill reliably above zero from one period to the next?"* |

The realised spread was **3.5× the null one** because the skill came and went: ~0.034 in 2016-18 and 2024-26, ~0.009 in
2018-20 and 2022-24. ⚠ `QA-4` promises an *autocorrelation-corrected* SE; the null formula contains no autocorrelation
correction at all — only the overlap divisor.

★ **Suggestion: the realised SE for acceptance (ideally Newey-West with `h−1` lags), the null SE kept as the MDE.**
Why: ⓐ `PG-2` — purpose 1 (your own money) wins, and the conservative error costs a missed model, the other costs a
card ranked by a signal that is weak half the time; ⓑ the variance you will *live through* is the realised one — a
model that earns 0.034 in some years and 0.009 in others is that model; ⓒ the null SE answers a planning question and
the gate uses it as an acceptance test (L6 AB-12's own diagnosis); ⓓ it is standard practice for overlapping-return
IC tests. ⚠ Cost: on August's numbers the model is **refused**, so the card stays on the rule — which is today's state
anyway. Alternatives: require **both** to pass (equivalent to the realised one whenever skill varies); keep the null SE
and add a stability condition (e.g. positive IC in ≥ N of the yearly blocks) — more rules, less standard.

### 5.4 The breadth gate — measured since 2026-08-27, but it cannot fail at 1m

What it computes (`src/quant/metrics/breadth.py`, AC-F12.28): the average pairwise correlation `ρ` of the **universe's**
21-day forward returns → effective independent names `n_eff = n / (1 + (n−1)·ρ)` → breadth `BR = n_eff × rebalances per
year` (Grinold-Kahn: independent bets per year). Gate: **PASS if `BR ≥ 3`**.

⚠⚠ **It cannot fail.** Even at `ρ = 1` (every stock moving as one), `n_eff = 1`, and with 12 monthly rebalances
`BR = 12 ≥ 3`. Any horizon up to ~84 trading days passes by arithmetic — the `QA-17` shape (*"a gate that cannot fail
is decoration"*) and exactly what `AC-F12.10` was written against, one level up: AC-F12.10 checks a PASS has a
statistic, not that the threshold can be missed. Two further limits: it measures the **universe**, not the ~10 names the
strategy actually holds; and `3.0` is an admitted, unmeasured number.

★ **Suggestion: tie the threshold to the signal, via the Grinold-Kahn law `IR ≈ IC × √BR`.** For a target information
ratio `IR*`, the breadth needed is `BR ≥ (IR* / IC)²`. With August's IC 0.0203 and `IR* = 0.5`, that is
**BR ≥ ≈ 610** — far above what a 500-name monthly universe offers once correlation is counted (e.g. `ρ = 0.25` ⇒
`n_eff ≈ 4`, `BR ≈ 48`). Why: ⓐ it makes the gate able to fail, and fail for the reason breadth matters — *this little
skill needs many more independent bets than we have*; ⓑ the number becomes derived, not admitted (`CN-10`); ⓒ measure it
on the **held book** (top-N per rebalance), which is what the money is in. ⚠ `IR*` is a policy value — **yours to set**;
0.5 is an illustration. Alternatives: keep the gate but mark it *informational* until redesigned (honest, cheap); or
drop it from `REQUIRED_GATES` (then promotion rests on IC and cost alone — and cost is now trivially passed).

### 5.5 The steps (all $0 API; FMP only)

| # | step | decides / does | depends on |
|---|---|---|---|
| ① | **hold promotion for review** | ✅ **BUILT 2026-10-06** (MT-52 / AC-4.34): training writes the artifact + gate report marked `pending`, never `promotion.json`; `python -m src.models.promote <id>` shows the report, `--approve` promotes — still refused unless every gate PASSed (no override) | — |
| ② | **`AB-12` ruling** — 5.3 | ✅ **BUILT 2026-10-06** — F12 `D9` / AC-F12.31: Newey-West realised SE (`h−1` lags) decides; the null MDE is still reported | — |
| ③ | **breadth gate** — 5.4 | ✅ **BUILT 2026-10-06** — F12 `D10` / AC-F12.32: implied IR `|IC|·√BR ≥ 0.5` on the **UNIVERSE** (Victor changed it from the held book the same day); the held book reported beside it, never gated; ⚠ **provisional — refine after ⑤'s results** | — |
| ④ | **fresh data pull + completeness check** — 510-name S&P universe, 10 years, from FMP; named failures (AB-18 silent names, AB-20 merger) reported, not dropped | ✅ decided | — |
| ⑤ | **fresh training + D-03 backtest** under the current simulator (drift weights, $0 fee): IC with **both** SEs, breadth, gross = net return | ✅ decided | ①–④ |
| ⑥ | **your review of the gate report**, then promote or not | Victor | ⑤ |
| ⑦ | **retrain cadence** | ✅ manual, by your command | — |
| ⑧ | **open D-04/D-03 items** — `AB-21` (revalidate the membership fix), `AB-25` #1 CAD/CDR valuation (the only thing keeping the card non-actionable), `AB-23`/`AB-24` (data-feed shortfalls), `QQ-11` universe breadth | review before go-live | — |

## 6. ★ D-05 — risk management (`src/risk/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-risk-management.md` (v0.5.0). Recorded only; nothing run.
>
> ✅ **Victor's rulings (2026-10-06):** **R1 accepted** as a standing limitation (no plan upgrade; the card stays
> informational) · **R2 wiring fix — BUILT** (OR-53 / AC-8.41) · **R3 — NOT wired yet (Victor, after the RK-30
> conflict, §6.5): revisit later** · **R4** fresh BMO exports before the live run · **R5** ignored (same-day merged orders are rare; `DX-152`
> closed) · **QK-1** D-06 owns position size · **QK-3** D-04 owns the effective-breadth number · **QK-6** stress taken from
> history.

### 6.1 Verdict: code-complete against its design, but NOT live — no daily run has ever produced a real risk pass

| | state |
|---|---|
| code | `src/risk/` — 19 files, 1,500 lines: exposure (5 dimensions, CDR ↔ underlying netting, FX-3), concentration + drawdown, VaR-with-caveats, marginal risk, stress scenarios, behavioural flags (M-3 pyramiding, M-4 short-hold, premature exit), alerts. Ungoverned by any `F`-spec |
| criteria | **26 / 26** design ACs (`AC-5.1`…`AC-5.23` incl. `5.6a` `5.13a` `5.19a`) cited by D-05's own tests (`tests_src/test_risk_b3.py`, `test_risk_b5.py`, `test_risk_flags_from_book.py`) — all green. **39 / 40** `RK-n` rules cited; `RK-4` (per-account AND book-wide reporting) is not cited by name, though its RESP half is tested under `AC-5.5`. ⚠ Bare `AC-5.x` collides with `F5`'s `AC-5.1…5.18` (the `DX-151` shape); counted here in D-05's own files only |
| in the daily graph | jobs `book` → `risk` exist (both optional). ⚠ `_risk` falls back to the B3 refusal (`UNCHECKED`) whenever **no valued book OR no taxonomy** — and today it has neither (R1, R2) |

### 6.2 The blockers

| # | blocker | detail | whose |
|---|---|---|---|
| **R1** | **CAD-venue / CDR positions cannot be priced** (`AB-3`, postponed as `AB-25` #1) | every account holds at least one; those symbols return `402` on the FMP Starter plan (`MDA.TO`, `MRV.NE` measured 2026-08-26). No valued book ⇒ no `COMPLETE` risk pass ⇒ the card stays non-actionable (DN-39). ★ The one thing keeping the card informational | Victor — commercial: FMP plan upgrade, a second price source, or accept |
| **R2** | **the theme taxonomy is never supplied to the daily run** | `THEMES_V1` exists (`src/risk/contracts/theme.py`, 13 tickers in `ai_semiconductor`), but `entrypoint._context_for` never sets `RunContext.taxonomy`, so even a valued book would hit the refusal | small wiring fix (`src/orchestration/`) |
| **R3** | **the M-3 / M-4 behavioural flags are never called** | `src/risk/flags/from_book.py` is built and tested on the real exports, and **no module in `src/` calls it**; `daily_book_pass` is passed `flags=()`. ★ These need **trade history only, no prices** — so they could run today, despite R1. M-4 is the registered-account (CRA) short-hold flag | wiring fix; Victor: run them now? |
| **R4** | **the broker exports are ~6 weeks stale** | `.state/broker/bmo_investorline/` last transaction 2026-08-25 (RRSP), 08-20 / 08-19 (TFSA), 08-07 (RESP) | Victor — export fresh files from BMO |
| **R5** | **`DX-152`** — commission-free trading removes D-11's merged-order evidence | affects order counts in the book D-05 reads, not cash or positions | Victor |

### 6.3 Open design questions (from the doc's §15)

| | question | note |
|---|---|---|
| `QK-1` | L0 §4.2 still says D-05 owns sizing | a one-line doc fix — sizing is D-06 |
| `QK-3` | who owns **effective breadth** as a reported number | ⚠ now tied to the new D-04 breadth gate (§5.4): one computation, two consumers — decide when that gate is refined |
| `QK-6` | is the single-theme stress (e.g. a 2022-style semiconductor drawdown) **from history or stated**? | needs a MethodEntry either way (QA-20) |

### 6.4 Steps (all $0 API; FMP only)

| # | step | decides / does | depends on |
|---|---|---|---|
| ① | fresh BMO exports into `.state/broker/bmo_investorline/` | Victor | — |
| ② | wire `THEMES_V1` into the daily run (R2) | approve the fix | — |
| ③ | wire the M-3/M-4/premature-exit flags into the daily run from the trade history alone (R3) — they would render even while R1 stands | approve the fix | ① |
| ④ | `AB-3` — how CAD/CDR positions get a price (R1) | Victor, commercial | — |
| ⑤ | `DX-152`, `QK-1`, `QK-3`, `QK-6` | Victor | — |
| ⑥ | a first real risk pass on the current book; you review it | Victor | ①–④ |

### 6.5 ⚠ R3 meets `RK-30` — a design conflict, Victor's ruling needed

`RK-30`: *"Alerts are emitted only from a complete pass. A step that failed means no alerts are emitted at all."* Its
reason: a partial alert set reads as an all-clear on whatever is missing. With R1 accepted, the daily pass **never
completes**, so wiring the behavioural flags into the full pass alone means they **never** render. Showing them now
needs `RK-30` amended. The case for amending: `RK-33` already makes flags independent of exposure (*"flags read the
book; exposure aggregates it"*), and the flags need only the trade history, so a behavioural-flag pass **can be
complete on its own** while exposure stays `UNCHECKED` — the all-clear risk is met by labelling the two halves
separately, never by a blended status.

✅ **Ruling (Victor, 2026-10-06): don't wire R3 yet — revisit later.** `RK-30` stays as written; the flags stay
built, tested and uncalled. Options kept for the revisit: ⓐ amend `RK-30` so the behavioural-flag pass is complete on its
own beside an `UNCHECKED` exposure · ⓑ wire them into the full pass only (they render only if R1 is ever lifted).

✅ **Revisited — Victor, 2026-10-21: option ⓐ.** `RK-40` amends `RK-30`; built 2026-10-22 (OR-63, DN-43, RP-57 — L3 §2.1).
The card shows a count per kind and the last 30 days of flags in full. ✏ **R4**: the exports were refreshed 2026-10-06 and run to
2026-10-02 — no longer six weeks stale.

## 7. ★ D-06 — portfolio strategy / position sizing (`src/portfolio/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-portfolio-strategy.md`. Recorded only; nothing run.
>
> ✅ **Victor's ruling (2026-10-06): leave D-06 as a library for rel-1** (option ⓐ). No wiring, no sizing tool;
> `target_positions`, `QS-1` and `QS-2` stay open until sizing is wanted.

### 7.1 Verdict: a tested library that nothing calls — NOT live, and under today's rulings it would size nothing

| | state |
|---|---|
| code | `src/portfolio/` — 12 files, 909 lines: risk-based sizing given a stop (`shares = risk_capital / stop_distance`), volatility stop distance (`k = 1.5`, 21 days), dynamic risk budget with factor decomposition, `MAX_POSITION_PCT` cap (15 %, system sizes only — a human size is never capped), what-if scenarios, risk-parity comparison (reported, never a target), M-3 pyramid check + `hold_alternative`. Ungoverned by any `F`-spec |
| criteria | **30 / 34** design ACs cited by `tests_src/test_portfolio_b5.py` (32 tests, green). Not cited: `AC-6.18` per-account sizing + book-wide exposure, `AC-6.19` RESP exclusion stated, `AC-6.20` no LLM / D-01 import, `AC-6.21` D-06 writes nothing. **33 / 43** `PS-n` cited; uncited include the whole **D-12 seam, `PS-37…41`** (read the recommendation's grade; size **only** what D-12 marked actionable; read the scorecard, never sum it) |
| wiring | ⛔ **no module in `src/` imports `src/portfolio/`**, no job in the daily graph, no command line. The card carries no size |

### 7.2 Why it cannot run usefully today

| # | blocker | detail |
|---|---|---|
| **P1** | **nothing is ever actionable** | `PS-39`: D-06 sizes only recommendations D-12 marked `actionable: true`. With R1 accepted (§6) the card is permanently informational, so there is nothing to size |
| **P2** | **no capital base** | `PS-3`: `capital_base` comes from D-11's valued book, point in time — and every account holds an unpriceable CAD/CDR position (R1), so no account has one |
| **P3** | **`target_positions` per account is unset** | `PS-43` makes it required configuration with **no default**; nothing in `config/` declares it — a policy value, yours |
| **P4** | **the risk budget is undecided** | `QS-1` (🔴 high priority in the design): how much of an account one trade may risk (`r_ceiling`); the code takes it as an argument with no default. `QS-2`: the stop multiple `k` (code default 1.5; should equal D-03's triple-barrier `k`) |
| **P5** | **no volatility forecast** | D-04 publishes none, so sizing would use **realised** volatility, labelled as such (`PS-23`) |
| **P6** | **the D-12 seam is not built** | `PS-37…41` — D-06 has no input path from a recommendation at all |

### 7.3 Open design questions (§15)

`QS-1` risk budget per trade (high priority, a joint D-05/D-06 feature) · `QS-2` the stop multiple `k` · `QS-8` whether the
dynamic risk budget deserves its own desk · `QS-6` the theme taxonomy — ✅ answered in effect by `THEMES_V1` / `RK-37` (§6),
still listed open in the D-06 doc.

### 7.4 What would make it useful — options for Victor

| | option | what it gives |
|---|---|---|
| ⓐ | **leave D-06 as a library for rel-1** | nothing on the card; consistent with an informational card under R1 |
| ⓑ | **an on-demand sizing tool**, like theses: you give ticker, account, entry, stop, capital and `r_ceiling`; it returns shares, the binding constraint and the consequences | useful today despite P1/P2 — you supply the capital you know; needs P3/P4 decided |
| ⓒ | **wire it into the daily run** | only meaningful once a card can be actionable — blocked by R1 by your decision |

## 8. ★ D-07 — the data engine (`src/data_engine/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-data-engine.md` (1,880 lines). Recorded only; nothing run.
>
> ✅ **Victor's rulings (2026-10-06):** **D1 — do NOT copy; this pipeline starts fresh** (the old repo's `.state/` is not
> migrated; consequences in §8.3) · **D2 — fixed**: one state root, `PIPELINE_STATE_DIR` (OR-54 / AC-8.42, `DX-154`
> closed) · **D3 — the event sweep is run MANUALLY** (`python -m src.data_engine.ingest`), like retraining and theses ·
> **D4 — DONE 2026-10-06 ($0)**: new tests for AC-7.18 (`tests_src/test_data_engine_fx_provenance.py`) and AC-7.77's
> reached-window half; existing tests tagged for AC-7.75, AC-7.77, AC-7.88 → **75 / 88** ACs by id · **D5** explained (§8.3).

### 8.1 Verdict: the code is the most complete of the domains, but this repo has never run it live — its operational state still lives in the OLD repo

| | state |
|---|---|
| code | `src/data_engine/` — 65 files, 8,711 lines: FMP + EDGAR clients, PIT fact ledger, price panel and split adjustment, calendar check (18 event classes, 15 sourceable and CHECKED), observation ledger (Class-B), symbology (rebrands, mergers), universe membership. Only `corporate_actions/` is governed (F3) |
| criteria | **71 / 88** design ACs cited by D-07's tests by AC id; of the other 17, most are tested under their **DE-rule** id (DE-50…56, 58, 69, 70, 72). **Genuinely uncovered: `AC-7.18`** (a converted value carries its FX rate) and the behaviours of **DE-57** (`AC-7.75`, handling derived from the store), **DE-59/60** (`AC-7.77`, a delisting HALTs and is not cleared by the price adjustment), **DE-71** (`AC-7.88`, a scheduled earnings date is knowable at `as_of`). **69 / 72** `DE-n` cited |
| in the daily run | ✅ the day-T opening print is wired (`fmp.prices.open_row`, OR-32/33/47); prices, features and the calendar check run as graph jobs |
| live history | ⛔ **no daily run has ever executed in this repo.** `.state/` holds no `daily_inference` manifest, **no event store (`.state/events`), no observation ledger (`.state/obs`), no models**. They exist in `../ai-investment-pipeline/.state/` (events 3.2 MB, obs 232 KB, facts 13 MB, models 2 MB incl. two `promotion.json`, runs 964 KB) |

### 8.2 The blockers and findings

| # | finding | detail | whose |
|---|---|---|---|
| **D1** | **operational state is in the old repo** | the event store's sweep history matters and **cannot be re-fetched**: the delisting feed reaches back only ~3 weeks (DE-60), and `restatement_silent` needs a *prior* snapshot to compare against. ⚠ Retiring the old repo (`MS-8.9`) without moving it loses that history. The old `models/` are moot (fresh retrain decided) | Victor — migrate `events/` + `obs/` (+ `facts/`), or start fresh |
| **D2** | ⚠ **`DX-154` — two env-var names for the state root** | `src/orchestration/entrypoint.py` reads **`PIPELINE_STATE`**; `src/models/train/__main__.py` and `src/data_engine/ingest/__main__.py` read **`PIPELINE_STATE_DIR`**. Set one and not the other, and training writes a model (or the sweep writes events) where the daily run never looks. Harmless only while both default to `.state` | approve a one-name fix |
| **D3** | **the corporate-action / event sweep is unscheduled** | `python -m src.data_engine.ingest` has never run in this repo; its cadence is still Victor's (`AB-14`). With an empty store the calendar check has nothing to check | Victor — manual (like retrain/theses) or scheduled |
| **D4** | **4 uncovered behaviours** | `AC-7.18`, DE-57, DE-59/60, DE-71 — tests to write (the code exists) | approve |
| **D5** | **open data issues** | `AB-21` revalidate the membership fix at end of release (scheduled by Victor) · `AB-23` class 5 unchecked by construction · `AB-24` three feeds with silent shortfalls · ⚠ survivorship cannot be corrected on this plan (DE-60): every backtest stays stamped **biased** (QA-14) | review |
| **D6** | **FMP is the only price source** | US listings only on Starter — the same fact as R1 (§6), accepted | ✅ accepted |

### 8.3 Starting fresh — what it costs, stated so nobody rediscovers it (D1)

* **Delisting history before the first fresh sweep is gone for good**: the feed reaches ~3 weeks back (DE-60), so a name
  that delisted in, say, August 2026 will never enter this repo's event store.
* **Class 5 (`restatement_silent`) stays `UNCHECKED` until a SECOND dated sweep** exists here (AB-23) — the old repo's
  first snapshot is not carried over.
* **The old promoted models are not carried over** — moot: a fresh retrain is decided (§5).
* ⚠ `MS-8.9` (retire the old repo) loses nothing this repo still needs, by this decision.

## 9. ★ D-08 — orchestration (`src/orchestration/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-orchestration.md`. Nothing run against live data.
>
> ✅ **Victor's rulings (2026-10-06):** **O1 — the daily run is MANUAL** (no timer; like theses, retrain and the event
> sweep) · **O2 — BUILT**: a failed run with `--deliver` now emails its notice (`entrypoint._announce_failure` →
> D-09 `send_failure_notice`; no analytical content, OR-45) · **O5 — BUILT**: `AC-8.20` and `AC-8.39` tested (§9.3).

### 9.1 Verdict: the run machinery is built and tested, but there is no way to start it on schedule, a failed run would not reach you, and it has never run in this repo

| | state |
|---|---|
| code | `src/orchestration/` — 35 files, 4,835 lines (incl. the platform parts governed by F2 trace, F6a routing, F6b deliberation, F8 control). The daily graph `daily_inference@v8`: 11 jobs, calendar check → prices → features → rank → thesis gate (stub) → book → risk → decide → render → record → deliver. Preconditions (trading day, inputs fresh, lock, day-T open, one run per cadence window), retry (transport only), time budgets (run 1,800 s, one per job), run manifest, failure notice |
| criteria | **43 / 47** design ACs cited by D-08's own tests. ⚠ Bare `AC-8.x` collides with **F8**'s `AC-8.1…8.20` (control surface) — counted in orchestration test files only. Of the other 4: `AC-8.35` (a failed retrain keeps the incumbent) is tested in D-04 as **MT-46**; `AC-8.30a` (only the open is needed at 10:00) by the open-print tests; **genuinely untested: `AC-8.20`** (a killed run leaves old or new state, never half-written — OR-17) and **`AC-8.39`** (the entrypoint stamps a REAL git sha / config hash / inputs — OR-51; tests supply them by hand). **50 / 54** `OR-n` cited |
| retrain | ✅ **not triggered by the daily run** — matches Victor's *manual retrain* ruling (§5) |
| live history | ⛔ **no daily run has executed in this repo** (fresh state, §8 D1) |

### 9.2 The blockers and findings

| # | finding | detail | whose |
|---|---|---|---|
| **O1** | **nothing starts the daily run** | OR-30/OR-40 want a thin timer at 10:00 America/New_York; `deploy/` holds only the analyst-estimates snapshot timer. And `loginctl` Linger is off, so a user timer runs only while you are logged in | Victor — a timer, or manual like theses/retrain/sweep |
| **O2** | ⚠ **a failed run does not reach you** | OR-19: *a failed run reaches the human by the SAME channel a success would*. The entrypoint builds the failure notice (OR-45, no analytical content) and **only prints it to stderr**; a successful `--deliver` run emails the card. A scheduled run that fails would be silent | wiring fix — email the notice when `--deliver` is on |
| **O3** | **the calendar check means nothing before a sweep** | with an empty event store the check returns **PROCEED** with every class `UNCHECKED` (stated in the report) — it does not block. Your manual sweep (§8 D3) must precede each live run | ✅ manual sweep decided |
| **O4** | **delivery credentials** | `GMAIL_SMTP_USER`, `GMAIL_APP_PASSWORD`, `REPORT_RECIPIENT` in the environment for `--deliver` (RP-50/51); a failed send fails the run (OR-50) | Victor |
| **O5** | **2 untested behaviours** | `AC-8.20` atomic writes on a killed run · `AC-8.39` real provenance from the entrypoint — tests to write, local, $0 | approve |
| **O6** | **first run is a smoke run** | fresh state, fresh model (§5), fresh sweep (§8) — the first live run will exercise every seam for the first time in this repo; expect findings | — |

### 9.3 Built 2026-10-06 — and what building it found

| | change | finding |
|---|---|---|
| **O2** | `src/orchestration/entrypoint.py::_announce_failure` + `src/reporting/deliver/email.py::build_failure_message` / `send_failure_notice` · 5 tests in `tests_src/test_orchestration_failure_email.py` | ⚠ **`AC-8.22` was cited but not met**: its test checked that the notice is *composed*, never *sent*. Now: emailed when `--deliver` is on; a missing `REPORT_RECIPIENT` or a failed send is printed loudly, never swallowed; the exit status stays FAILED |
| **O5 · AC-8.20** | `src/orchestration/state/manifest_store.py` — writes now go to a temporary file, are flushed, then atomically renamed · 2 tests in `tests_src/test_orchestration_b3.py` | ⚠ **a real defect**: `manifest.json` and `outcome.json` were written with plain `write_text`, so a run killed mid-write left a truncated file that `read()` cannot parse and OR-13 would refuse to replace |
| **O5 · AC-8.39** | 1 test: the entrypoint hands `trigger()` the real git sha, dirty flag and `sha256:` config hash | the code was right; it had no test |

### 9.4 Two further findings, recorded, not changed

| # | finding | detail |
|---|---|---|
| **O7** | **one-run-per-day is per PROCESS** | `RunLock` and `CadenceClaims` (OR-24, OR-46) live in memory; each command starts empty, so a second manual run on the same day is not blocked. Harmless under manual runs if you run once a day; it would matter under a timer |
| **O8** | **`inputs` is always empty, so `AC-8.39` is only partly met** | the entrypoint passes no input digests: prices are fetched after the manifest is written (OR-9: manifest before work), so the manifest records `inputs: []` and OR-52 reports freshness *not evaluated*. A real fix needs a design choice (e.g. a second, post-fetch provenance record) |

## 10. ★ D-09 — reporting / the discipline card (`src/reporting/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-reporting.md`. Nothing run against live data.
>
> ✅ **Victor's rulings (2026-10-06): C1 as suggested; C2, C3, C4 fixed — all BUILT the same day** (§10.3).

### 10.1 Verdict: it renders and delivers a correct, self-contained, honestly non-actionable card — but four things on it would mislead a reader today

| | state |
|---|---|
| code | `src/reporting/` — 13 files, 1,152 lines: card builder (renders, re-derives nothing — RP-43; refuses a verdict made more aggressive in transit — RP-7), HTML (self-contained, fetches nothing) and Markdown renderings, forecast-voice lint, archive (archived bytes = sent bytes), Gmail SMTP delivery, relay-queue block, and since today the failure email (§9) |
| criteria | **24 / 38** design ACs cited by D-09's own tests (`tests_src/test_reporting_b3.py`, `test_orchestration_deliver.py`, `tests/unit/test_card_states_its_source.py`); **33 / 45** `RP-n`. Most of the 14 others describe things **not on today's card** — fair value as a band (`AC-9.18`), backtested-return labels (`AC-9.22`), the degraded-run refusal banner and cache rules (`AC-9.10…9.14`), the online page (`AC-9.23`, `AC-9.26`), quant/thesis divergence (`AC-9.8`), staleness marking (`AC-9.4`) — so they are vacuous for a card-only rel-1 and become live when that content arrives |
| what the card shows today | `[NOT ACTIONABLE]` banner with the named missing inputs (no k≥3 thesis; risk `UNCHECKED` — AB-3) · "what would prove this wrong" · verdict · stability · confidence · rank + ranked quantity · alerts (with their status) · data gaps · stubs |
| delivery | tested with a fake transport; **never sent from this repo** (a real send was verified in August from the old repo, AB-6) |

### 10.2 Findings

| # | finding | detail | whose |
|---|---|---|---|
| **C1** | ⚠ **the card says "Verdict: BUY" with no analysis behind it** | D-12 nominates `BUY` for every top-ranked name (`NOMINATED_VERDICT`), and the placeholder thesis gate always PASSes, so the composed verdict is BUY — rendered as a COMPUTATION from D-12. The banner and the falsifier text say why it is not actionable, but the word BUY sits in the verdict row | Victor — e.g. render *"no verdict — ranked #1 by the rule; no thesis"* while the gate is the placeholder |
| **C2** | ⚠ **stale placeholder wording** | the gate's reason and the card's falsifier text say *"D-01 is not built … replaced by the real gate at B4.4"*. D-01 is built; theses are authored on demand by your command and the daily run writes none (DX-153). A reason that names a cause already fixed is worse than a vague one (the code's own RK-29 comment) | wording fix |
| **C3** | **the daily run declares no stubs** | OR-43 / AC-8.14a: a stubbed domain is declared in the RunManifest. The daily entrypoint passes `stubs=()`, so the manifest says `[]` while the thesis gate IS a stub. The card still says so (from the gate), but the run record does not | wiring fix |
| **C4** | **the card does not say what ranked the pick** | PG-10 is satisfied (the card is not actionable), but nothing on it says the rank comes from the momentum **rule** (`rank.denormalised_within_ticker_z.v1`) rather than a promoted model — the id sits only in `recommendation.json` | small render addition |
| **C5** | **first real email** | `--deliver` needs `GMAIL_SMTP_USER`, `GMAIL_APP_PASSWORD`, `REPORT_RECIPIENT` (§9 O4); the first live send is the real test | Victor |

### 10.3 Built 2026-10-06 — rules first, then failing tests, then code

| | rule added | change | test |
|---|---|---|---|
| **C1** | `RP-53` / `AC-9.35` (L1-reporting) | with the placeholder gate and no thesis, the verdict row reads **"no verdict — ranked #1 by the rule; no thesis"**; the composed verdict stays untouched in `recommendation.json`; a real graded gate still renders its verdict (`src/reporting/render/card.py`) | `tests_src/test_reporting_card_honesty.py` |
| **C2** | `RP-53` | placeholder wording now names today's cause — *"theses are authored on demand (DX-153)"* — in the gate reason, `replaced_at`, the falsifier text and the data gap (`src/fundamental/thesis/stub_gate.py`, `card.py`) | same file |
| **C3** | `OR-55` / `AC-8.43` (L1-orchestration) | the daily run declares the placeholder gate in the RunManifest's `stubs[]` (`entrypoint._daily_stubs`) | same file |
| **C4** | `DN-40` / `AC-12.30` (L1-decision) · `RP-54` / `AC-9.36` | D-12 carries `candidate.ranked_by = {artifact_id, kind: rule|model, formula_id}` byte-identical from the nomination (`src/decision/compose/service.py`); the card renders a **`ranked_by`** row — e.g. *"the rule rank.denormalised_within_ticker_z.v1 (…) — no trained model"* | same file |

4 existing tests pinned the old wording (`"B4.4"`, "stub", `| verdict | BUY |`) and were updated to assert the new
wording. Suite **2,581 pass / 1 red (`J-07`)**; lint adds nothing.

## 11. ★ D-11 — recording (`src/recording/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-recording.md`. Recorded only; nothing run.
> ✅ **Victor (2026-10-06): D-11 is NOT for live trading guidance** — the pipeline is not yet trustworthy enough to
> drive real buys or sells. Its role: **record the BMO InvestorLine transaction CSVs he downloads and drops in**, so
> the pipeline can use the real book.

### 11.1 Verdict: that is exactly D-11's intended design — and it works today, with three caveats

L1-recording §0: *"Four registered accounts … **One human, one broker, a manual CSV drop, no API, no venue.** What it
must do: ingest the export without getting the cash wrong, keep positions and cash per currency, reconcile, publish
the capital base, keep the decision journal."*

| | state |
|---|---|
| code | `src/recording/` — 19 files, 2,415 lines: BMO export parser (reads the header — two column layouts exist; every activity classified, an unknown one raises), tranche → order grouping, commission derived, CDR vs US-listed identity, FX legs, lots (average cost), round trips, book state + reconciliation, opening snapshot, decision journal (append-only), run record (CT-11.7), counterfactual store |
| criteria | **48 / 63** `RC-n` rules cited by D-11's tests (most tests cite rules, not ACs; only 7/33 ACs by id). Real-export tests run against your files in `.state/broker/` (they skip on a clone without them — DX-5) |
| your files | 4 exports, all full history: `TFSA_1` 2022-02-22 → 2026-08-20 · `TFSA_2` 2022-02-04 → 08-19 · `RRSP_1` 2024-01-23 → 08-25 · `RESP_1` 2024-08-06 → 08-07 |

### 11.2 How the CSV drop works today

1. Download each account's **full history** from BMO and save it in `.state/broker/bmo_investorline/` as
   **`TransactionHistory_<TYPE>_<N>.csv`** — `TFSA_1`, `TFSA_2`, `RRSP_1`, `RESP_1`. The name IS the account and its
   registered type (H-5, RC-18); a new account is just a new file (RC-65). `.state/` is git-ignored, so statements never
   enter history.
2. **Replace** the old file with the new download — there is no import step; D-11 re-reads the files whenever the book
   is needed.
3. Safety already built: a window that starts after a position was opened raises (`TruncatedWindowError`, RC-45) unless
   an opening snapshot is supplied (AC-11.34); a blank-but-cash row, a new activity type or an unknown column layout
   raises rather than being dropped.

### 11.3 Findings

| # | finding | detail | whose |
|---|---|---|---|
| **K1** | **no command to check a dropped file** | nothing reports "these files parse, these are the positions and cash per account, here is what refused" — today you would only find out inside a pipeline run or a test | suggest a read-only check command ($0, writes nothing) |
| **K2** | **a changed past row would not be noticed** (RC-11) | the design says a re-download whose content changed for an already-covered window is a *restatement*, recorded, not overwritten. `file_hash()` exists but nothing stores hashes, so a silent BMO correction of an old row simply replaces it | suggest a small ingest log (hash per file + per-row digests) |
| **K3** | **overlapping files double-count** | one file per account; there is no de-duplication across two files or pasted overlapping rows. The rule is *replace, never append* | rule, stated (§11.2) |
| **K4** | **no stored ledger** (CT-11.1 `RawActivity`, append-only) | the CSVs ARE the record — consistent with §0's "minimal"; K2 is the part of it worth having | accept |
| **K5** | **what the pipeline gets from it today** | the book cannot be VALUED (CAD/CDR, R1 accepted), so the daily run receives the refusal reason; the M-3/M-4 flags that need only this history are built but not wired (R3, not yet). The run record, journal and counterfactual store are written by the daily run | — |

### 11.4 ✅ K1 + K2 BUILT 2026-10-06 (Victor: "build K1 and K2 now")

Rules first — **RC-67** (the check command) and **RC-68** (the ingest log, RC-11 built) with **AC-11.49…11.51** in
L1-recording — then 11 failing tests (`tests_src/test_recording_check.py`, synthetic exports only), then the code:
`src/recording/check.py` and `src/recording/reconcile/ingest_log.py`.

```text
python -m src.recording.check            # read-only: every account, window, rows, orders, positions, cash
python -m src.recording.check --record   # also APPEND each sound account to .state/broker/ingest_log.jsonl
```

* Reuses the book's own ingest path (`parse_export` → `group_orders` → `derive_quantities` / `derive_cash`).
* A bad file is **named with its reason** (e.g. a truncated window, RC-45) and the others still report; exit status 1.
* The log compares each file with the last **recorded** entry for its account: `unchanged` · `new_activity` (rows
  after the old window) · **`restatement`** (rows inside the old window removed or added, each listed) ·
  *window starts later* (older history dropped). Rows are a multiset, so a vanished duplicate tranche is caught.
  Append-only; a refused account is never recorded.
* ★ **Checked read-only on the real exports, 2026-10-06:** all four accounts sound, 0 refused, and the derived cash
  equals the BMO balances D-11 reconciled to the cent in August (RC-57: TFSA_1 25.30 CAD / 832.81 USD, TFSA_2
  30.86 / 151.22, RRSP_1 18.83, RESP_1 45.43). Nothing written.
* ⬜ **The log has no baseline yet** — the first `--record` (Victor's) creates it; restatements are detectable only
  from then on.

## 12. ★ D-12 — decision / composition (`src/decision/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-decision.md`. Recorded only; nothing run.

### 12.1 Verdict: ready for the card-only run — its composition half is complete; its measurement half is unwired, and has nothing to measure until a real thesis gate runs daily

| | state |
|---|---|
| code | `src/decision/` — 11 files, 743 lines: the verdict algebra (a bounded meet — *verdicts gate, never upgrade*, PG-6), gate application and binding attribution, INV-6 (at most one actionable recommendation per run), the actionable rule (DN-39: a COMPLETE risk pass **and** a stability figure), anchor match, `ranked_by` (DN-40, built today), `veto_rate()` |
| criteria | **24 / 31** design ACs tested (`tests_src/test_decision_b3.py`, exhaustive over the 27 verdict × status cases; `test_decision_actionable.py`; `test_reporting_card_honesty.py`); **25 / 40** `DN-n` cited |
| on a card-only day | the placeholder gate PASSes, risk is `UNCHECKED` (R1), so every recommendation is **informational** — correct by DN-39; the card now says *"no verdict"* (RP-53) |

### 12.2 The uncovered part — all of it the MEASUREMENT half

| # | finding | detail |
|---|---|---|
| **E1** | **the counterfactual arm is not wired** (`DN-19…21`, `AC-12.16…12.18`) | `src/recording/counterfactual.py` (the append-only store of vetoed names, PG-5.2's *log both arms*) exists; **nothing in the daily run writes to it**. Vacuous today: the placeholder gate never vetoes |
| **E2** | **`veto_rate()` is not reported per run** (`AC-12.19`, DN-17) | the function exists and is tested; the daily run never calls it. Under card-only it would always read 0 vetoes over a placeholder |
| **E3** | **per-candidate deferrals are not tracked** (`DN-29`, `AC-12.24`) | `Recommendation.deferral` exists and is never populated |
| **E4** | **ρ — thesis order vs rank order — is not built** (`DN-27/28`, `AC-12.25/26`) | it needs D-01 coverage across the rank distribution; with theses on demand only, it is unestimable by design |

★ **No ruling needed now.** E1–E4 become live the day a real thesis gate runs in the daily path (rel-1 rules that
out: card only, theses on demand). ⚠ When that day comes, **E1 must be wired first**: PG-5.2 says the counterfactual
arm is *near-free today and impossible to backfill*.

## 13. ★ D-01 — fundamental analysis (`src/fundamental/`) — added 2026-10-06

> From the record (L3 §2.1i…§2.1s, DX-153), plus one check of `tools/run_thesis_once.py`. Recorded only; nothing run.
>
> ✅ **Victor (2026-10-06): T1 — keep the MANUAL chain** (no one-command thesis builder). A thesis for another ticker or
> date is the hand-run sequence in §13.2.
>
> ✏ **SUPERSEDED 2026-10-20 (Victor, after 2026-10-11): T1 → build the one-command `thesis_for TICKER --as-of DATE`**,
> chaining the steps below with run ids as arguments, MU first — spec `sdd/specs/F13_thesis_on_demand/spec.md` (🟢 approved and ✅ built 2026-10-20, 12/12 ACs).
>
> ★ **State on 2026-10-20 — `thesis_for` BUILT.** `python tools/thesis_for.py MU --as-of DATE [--dry-run | --fetch-inputs]`.
> The $0 replay of 2025-06-26 carried and re-verified every step of the fourth MU thesis (base `sha256:ed40721f…`).
> For 2026-10-20 `--fetch-inputs` supplied MU's FY2026 **10-K** (the first 10-K anchor, F13 `D7`), Sandisk's FY2026 10-K,
> MU facts, price and consensus. ⬜ **Victor:** save the newest SK hynix and Samsung releases by hand (`D11`; steps in
> `tools/thesis_for.py --help`), then run the chain (~30 subscription calls). §13.2's hand-run sequence is now history.
> Theses stay on his manual command; the paid API stays off. The card wording stays "REFUSED".

### 13.1 Verdict: not in the daily run, by decision — and "theses on demand" is today a Micron-only, single-date command

| | state |
|---|---|
| decisions | **card only; theses on demand, only on Victor's manual command** (2026-10-05) · paid Anthropic API **off** (dev calls on the subscription, `claude_code`) · falsifier improvement **deferred** until real runs · AMD thesis **skipped** · golden programme **closed** (L8 §9) |
| built | 32 / 35 prompt blocks declared, every one run live and verified (`E-14`, `J-18`, `J-19` deferred by decision) · the 32-block `CT-9.2` thesis runner `tools/run_thesis_once.py` (Stages B–D over a frozen Stage A, J-15 v3 falsifiers, F10 valuation, F11 base rates, consensus) · falsifier checker, rule checks, re-derate — all $0 |
| record | four MU theses (k=1 each): SELL → HOLD → SELL → SELL, all falsified or on course to be |
| daily path | ⊘ the old three-call `thesis` job was **removed** (DX-153); the daily card carries a placeholder gate and says *"no verdict"* (RP-53) |

### 13.2 ⚠ Finding — what "on demand" actually covers today

`tools/run_thesis_once.py` rebuilds Stages B–D on top of **fixed, recorded MU runs**: `DEFAULT_STAGE_A` (J-01…J-08,
J-20) and `DEFAULT_EXTRACTIONS` (E-01, E-04, E-06, E-07, E-09, E-10, E-12, E-13) are **run-id constants in the code**,
`as_of` comes from the MU FY2025-Q3 10-Q bundle (**2025-06-26**), the price fixture is MU June 2025, and the sector file
is the memory industry only. `--ticker` exists, but nothing else follows it. So **a thesis for another ticker, or for MU
on a newer filing, is a hand-run chain today**:

```text
convert_filing (10-K/10-Q → fixture) → run_extraction_once per E-block → run_judgement_once for Stage A (J-01…J-08, J-20)
→ ingest_sector_file (a sector file for that industry) → fetch_consensus / the snapshot → edit DEFAULT_STAGE_A /
DEFAULT_EXTRACTIONS → run_thesis_once → check_falsifiers · rule_checks
```

| # | finding | whose |
|---|---|---|
| **T1** | **no one-command on-demand thesis** for a ticker and date of your choosing — the constants above must be edited by hand | Victor — build `thesis_for TICKER --as-of …` that chains the steps and passes run ids as arguments (several sessions), or keep the hand-run chain |
| **T2** | **sector evidence exists for one industry** (memory); any other industry needs its peer set chosen by you first (as `DX-117` did for memory) | Victor, per industry |
| **T3** | **consensus is snapshotted for MU and AMD only** (`snapshots/analyst-estimates/`, timer weekdays 18:30 NY) | add tickers to the snapshot when a thesis is wanted |
| **T4** | **sector file v2** is not yet the runner's default — switch at go-live (Victor, 2026-10-05) | ✅ decided |

## 14. ★ D-03 — quantitative analysis (`src/quant/`) — added 2026-10-06

> From `sdd/specs/F12_quant_core/spec.md` and L3 §2.1s. Recorded only; nothing run.

### 14.1 Verdict: governed and closed for rel-1 — its remaining work is shared with D-04's fresh training

| | state |
|---|---|
| spec | **F12 🟢 approved 2026-10-05** (Victor) — *govern & close*: `src/quant/**` governed; **27 / 30** ACs green, 3 vacuous (no multi-horizon design, no screen, no deterministic stop yet) |
| rulings | factors = the existing D-02 feature sets (`D2`) · regime handling a **declared limitation**, stated on every Nomination and BacktestResult (`D3`/`D7`) · held names **drift**, only entries/exits trade (`D6` — every backtest return moved) · commission **$0** (`D8`, BMO commission-free) |
| daily role | ranks the universe and nominates; with no promoted model it ranks by the **rule** `rank.denormalised_within_ticker_z.v1`, and the card now says so (RP-54) |
| ⬜ open | the two gate rulings to BUILD before the fresh training (§5): **`AB-12` — the realised standard error** decides IC acceptance · **breadth — `BR ≥ (0.5 / IC)²` on the held book**, provisional until results. Both live in `src/quant/gates/` and `src/quant/metrics/` (F12-governed: amend F12 first) · hold-promotion-for-review still undecided (§5.5 ①) |

## 15. ★ D-02 — feature engineering (`src/feature_engineer/`) — added 2026-10-06

> Measured 2026-10-06 against `sdd/design/rel6_design/L1-feature-engineering.md`. Recorded only; nothing run.
> ✅ **Victor (2026-10-06): F1 ACCEPTED** — the daily run's fundamentals refresh when he retrains · **F3 DONE** —
> `tests_src/test_feature_engineer_b3.py::test_ac_2_21_a_ticker_with_absent_inputs_is_degraded_never_dropped` (the
> behaviour was already correct; it had no test).
> Scope: the inherited feature code — 23 files, 2,609 lines. `valuation/` (F10) and `base_rates/` (F11) are already
> governed and green, and serve the on-demand thesis (§13), not the daily card.

### 15.1 Verdict: the code that feeds the ranker is built and tested; one rule is untested, and the daily run's fundamentals are only as fresh as the last training run

| | state |
|---|---|
| code | three contract sets — `b3_minimal_v1` (`mom_21`, `vol_21` — what the **rule** ranks on today), `price_ohlcv_v1` (14 price features) and `fundamental_v1` (45 `f_*` features) — plus labels (open-anchored, `available_at` materialised), cross-sectional ranks and sector z-scores, the coverage report, the analyst-consensus arithmetic for theses |
| criteria | only **18 / 46** design ACs carry their `AC-2.x` id in D-02's tests — ⚠ bare `AC-2.x` also means **F2** (trace & replay, `AC-2.1…2.16`), so the ids were counted in D-02's own files only (`DX-155`). Checked by behaviour, almost all of the other 28 are tested under their **FE-rule** ids or by description (Wilder RSI, MACD, within-date ranks, sector z below three names, filing-date joins, denominators, share counts, no-look-ahead, byte-identical panels…). **27 / 39** `FE-n` cited |
| ⚠ genuinely untested | **`AC-2.21` / `FE-27`** — *a ticker with absent inputs is reported degraded, never dropped*: `coverage()` exists and the daily run calls it, but no test names the rule. Also legacy-shaped criteria that no longer bind the way they read: `AC-2.26` (the old DCF move, FE-18 — superseded by F10) and `AC-2.29` (golden-fixture `adj_as_of`, FE-22) |

### 15.2 Findings

| # | finding | detail | whose |
|---|---|---|---|
| **F1** | **the daily run reads fundamentals; it never fetches them** | `entrypoint._fundamentals_for` reads the fact ledger without ingesting (deliberately — *a daily run that silently fetched 500 companyfacts payloads would be doing D-07's write path on a schedule nobody declared*). The ledger is filled by the **training run** (`ingest_universe_facts`, EDGAR). So once a model on `price_and_fundamental` is promoted, its `f_*` features are **as fresh as your last manual retrain** — a 10-Q filed since then is invisible to the card. Today the rule needs no fundamentals, so it does not bite yet | Victor — accept (refresh = retrain), or a manual `ingest` step before each run |
| **F2** | **fresh state** | this repo's fact ledger holds only MU, SNDK and WDC (F11's reference class) — the first fresh training run (§5) fills it for the universe | ✅ part of the decided fresh training |
| **F3** | **`AC-2.21` untested** | a $0 test that a name with missing inputs appears degraded in the coverage report and is not dropped | approve |

### 11.5 Fresh exports dropped 2026-10-06 — what the check found

* `python -m src.recording.check` (read-only) on Victor's fresh downloads: **0 refused** after `DX-156` — the first run
  refused `TFSA_1` on a −$0.09 rounding residual (`CRWD 2026-10-02`), the first commission-free negative; fixed.
  Windows now end 2026-09-17 (RESP_1) and 2026-10-02 (the other three).
* ★ **Test truth is frozen separately**: `.state/broker/frozen_2026-08-25/` holds the four August exports the
  external-truth tests were measured on (Victor, 2026-10-06), so replacing the live files never breaks them again.
* ✅ **RC-57 re-verified on the fresh files, 2026-10-06** — Victor read the balances off BMO InvestorLine; **all seven
  derived cash figures match to the cent**: TFSA_1 25.30 CAD / 10,242.04 USD · TFSA_2 33.96 CAD / 318.52 USD ·
  RRSP_1 35.63 CAD / 0.00 USD · RESP_1 28.51 CAD. The second external check of this book, on a different download.
* Investment values BMO reported the same day (recorded for reference; D-11 cannot value them itself — CAD listings and
  CDRs, R1): TFSA_1 9,011.10 CAD + 48,331.80 USD · TFSA_2 52,004.41 CAD + 21,932.30 USD · RRSP_1 20,009.66 CAD ·
  RESP_1 13,685.25 CAD.
* ✅ **The change log has its baseline**: `python -m src.recording.check --record` run 2026-10-06 (at Victor's request) —
  4 entries in `.state/broker/ingest_log.jsonl` (66 / 127 / 182 / 160 rows); an immediate re-check reads `unchanged`
  for all four. A later download that alters a past row is now reported as a RESTATEMENT.
