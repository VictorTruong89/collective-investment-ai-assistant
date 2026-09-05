# Blueprint — D-05 Risk Management *(B3 refusal · B5 the full ladder)*

> **Governing spec:** [`../design/rel6_design/L1-risk-management.md`](../design/rel6_design/L1-risk-management.md)
> **Seat:** SEAT-4 · **Level:** 2 (ALERT) · **Path:** `src/risk/`

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-25 *(book wired)* | **M-3 and M-4 run on the real book, and need no market value** | RC-58 postpones Canadian listings and CDRs, so exposure percentages wait — ★ but the behavioural flags read the **trade history**, not the valuation. **109 flags on the real exports**: 67 registered short holds (13 closed within a day), 17 pyramiding events, 25 premature exits. A test pins that no price, market value or quote appears in the module | *Waiting for valuation* — it would defer the half of D-05 the mandate actually asked for |
| 2026-08-25 *(book wired)* | ★ **Average cost is weighted-average; round trips are FIFO** | Two different questions. M-3 is a rule about **the average rising**, which is the Canadian ACB convention — FIFO would answer something else. ⚠ For a *holding period*, **which** shares came back out is the question, so round trips match FIFO. The commission is **inside** the average cost: M-3 is about what you paid, and excluding $9.95 understates every small order by more than the price moves this rule cares about | *One convention for both* — it makes one of the two flags measure the wrong thing |
| 2026-08-25 *(B5)* | ★★ **`CT-11.4 BookState` is built at the head of B5** | **BS-15b.** B1 built *"enough of D-11 to hold"* the journal, calibration and counterfactual store — **the book was not among them** — and BS-9's amendment binds the *source* rather than a milestone, saying only that the book lands *"before B4"*. **Nobody owned it and B4 shipped without it.** D-05's step 0 is `RECONCILED?` against that contract | *Retro-fitting it into B1* — it is B5's blocker and nothing earlier needed it, which is also why nobody noticed |
| 2026-08-25 *(B5)* | ★★ **D-05 resolves theme from D-02's SECTOR; D-02 publishes no theme** | **RK-37**, closing **QK-2**. `L1-feature-engineering` §6.4 claimed D-02 publishes *"sector and theme mappings"*, while **RK-6** makes the taxonomy a declared artifact. For D-02 to label a theme it must know the taxonomy, and **FE-21 forbids D-02 importing an analytical domain.** ★ Theme membership is *a judgement call about what counts* — *is `ENB` in the AI theme because it powers datacentres?* — and a judgement belongs on a seat | *Moving the taxonomy to D-02* — it puts a judgement on neutral ground and makes INV-014's guarantee depend on nobody noticing |
| 2026-08-25 *(B5)* | ★★ **`ai_semiconductor` is a TICKER LIST, not `sectors=["Information Technology"]`** | The sector rule would sweep in every software name and make the 40 % threshold **a measure of the sector rather than of M-2's actual bet.** ★ The ticker list *is* the judgement, isolated where a reader can see it answered | *The sector rule alone* — cheaper to maintain and it measures the wrong set |
| 2026-08-25 *(B5)* | ★★ **`P` is MCTR, not a difference of book volatilities** | ⚠ **Found by a failing test.** *"How much did adding it move `σ_p`"* **clamps to zero for every name whose own vol is below the book's blend** — which includes both the diversifying name and the sixth semiconductor. The two then read identically, and **RK-20's entire distinction is destroyed by the estimator rather than by the input** | *`max(0, after − before)`* — it was the first thing written, it looked marginal, and it measured nothing |
| 2026-08-25 *(B5)* | ★ **The premature-exit flag reports a distribution against the book's own holds** | **RK-39**, closing **QK-4**. Two problems, one answer: a fixed *"exited inside N days"* repeats the fixed-percentage mistake QS-1 rejects, **and the only artifact carrying an intended horizon is the thesis — which RK-28 forbids D-05 to import** | *A threshold on days* — it would need a horizon D-05 is not allowed to see |
| 2026-08-25 *(B5)* | ★ **A drawdown from fewer than two reconciled states is `unmeasured`** | **RK-38/RK-36.** *A book whose history begins today is at its peak by construction*, and **"no drawdown" is the most misleading possible reading of it.** ⚠ Zero drawdown and unmeasured drawdown are opposite findings that would look identical | *Returning 0.0* — it flatters exactly the state that deserves least confidence |

# 1. What this domain does, in one paragraph

D-05 answers **"what is this book actually exposed to, and has anything crossed a line worth saying
out loud?"** It aggregates exposure on five dimensions, derives drawdown and marginal risk
contribution for D-06, raises the two behavioural flags the mandate names (M-3 pyramiding, M-4
registered short holds), and emits LEVEL 2 alerts. ★ **It never blocks and never sizes** — *most
risk systems earn their keep by refusing; this one earns it by being impossible to ignore and
impossible to obey.*

# 2. The objects and how they flow

```text
   D-11 CT-11.4 BookState  ──►  0 RECONCILED?  ⛔ abort on a break (RK-29)
            │                          │
            ▼                          ▼
   book/reconcile.py           2 EXPOSURE ────► 4 FLAGS  (parallel — RK-33)
   RC-10: positions+cash==NAV     five dims        M-3 · M-4
            │                          │              │
            ▼                          ▼              │
   D-02 sector ──► CT-5.3      3 METRICS  drawdown ◄──┘
   theme resolution (RK-37)           │
                                      ▼
                              5 FACTORS  P · D  ──►  D-06
                                      ▼
                              6 ALERTS  only from a COMPLETE pass (RK-30)
                                      ▼
                              7 PUBLISH  CT-5.1 BookRisk · CT-5.2 Flag[]
```

★ **There is no gate step, and its absence is deliberate** (RK-34, INV-026).

# 3. The sequence — what actually executes

`src/risk/alerts/daily.py::daily_book_pass` is §4A.2's ladder, in the order §4A.2's *"what forces
each position"* table forces. Step 0 raises `NoBookError` on any unreconciled account; steps 2–5
compute; step 6 emits; step 7 returns `(BookRisk, AlertSet)`.

# 4. ★ The mathematics

| Quantity | Form | Where |
|---|---|---|
| exposure share | `value_base / total_base` per dimension | `src/risk/exposure/aggregate.py` |
| base conversion | `market_value × fx_rate_used[ccy]`, **unavailable without a rate** | same |
| drawdown depth | `(peak − current) / peak`, peak derived from the series | `src/risk/metrics/drawdown.py` |
| `D` factor | `max(0, 1 − depth)` — monotone, bounded in `(0,1]` | same |
| book volatility | `√(w' Σ w)` | `src/risk/metrics/marginal.py` |
| **`P` factor** | `MCTR_i / (w_i σ_i)` where `MCTR_i = w_i (Σw)_i / σ_p` | same |
| stress impact | `Σ weight × shock`, deliberately trivial | `src/risk/stress/scenarios.py` |

★ **The `P` arithmetic is the one place a plausible alternative silently fails** — see the decision
log, and `test_ac_5_20_marginal_risk_is_marginal_not_standalone`.

# 5. The logic decisions

| Decision | Rule |
|---|---|
| Positions key on `analysis_symbol` | RK-5 is applied **by construction**, not by a caller remembering to merge a CDR with its underlying |
| Exposure and flags never call each other | RK-33 — sequencing them would invent a dependency that would then be maintained |
| The `unclassified` residual is not thresholded | RK-7 — it is reported so the reader sees the unmeasured share; alerting on an unnamed set says nothing |
| The RESP is excluded from exposure and **included** in M-4 | RC-4 excludes it from the *fund*; RK-16 gives M-4 no exempt population. Both, at once |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Changing it affects |
|---|---|---|---|
| `CONCENTRATION_THRESHOLD_PCT` · `SECTOR_MAX_PCT` · `THEME_REPORT_THRESHOLD_PCT` | `src/risk/exposure/aggregate.py` | 25 · 35 · 40 | ★ **Reporting only** (RK-2). Which crossings emit a LEVEL 2 alert — never what may be held |
| `THEMES_V1` | `src/risk/contracts/theme.py` | `themes.v1` | ★ **Not config** — a versioned artifact. Adding a ticker is an analytical change and takes a version bump |
| `MIN_SERIES` | `src/risk/metrics/drawdown.py` | `2` | When drawdown reports `unmeasured`. ⚠ Two is the arithmetic minimum for a peak, not a judgement |
| `REGISTERED_SHORT_HOLD_DAYS` | `src/risk/flags/behavioural.py` | `30` | M-4's window — the CRA framing, L0 §config |
| `short_tail_pct` | same | `25.0` | Which tail of the book's own holding-period distribution flags. ⚠ **ADMITTED GUESS** (CN-10) — RK-39 says *distribution*, not *which decile* |
| `RECONCILE_TOLERANCE` | `src/recording/book/models.py` | `0.005` | Float slack only; a `Money` book reconciles at zero |
| `SEMI_2022` shock | `src/risk/stress/scenarios.py` | `−0.45` | ⚠ **STATED, not fitted** — QK-6 is open on whether it should be parameterised |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | `CT-11.4 BookState` | D-11 | `reconciled != ok` ⇒ `NoBookError`, the pass aborts (RK-29) |
| in | sector, correlations, vols | D-02 | a missing correlation ⇒ `P` is `unmeasured`, never assumed zero |
| out | `CT-5.1 BookRisk` | D-09, D-12 | published only from a complete pass |
| out | `CT-5.2 Flag[]` | D-11 journal, D-09 | append-only; `suppressed` is a constant `false` |
| out | `P` · `D` | **D-06** | either may be `unmeasured` — a value, not a failure |

# 8. Failure behaviour

★ **Every failure mode in this domain is a refusal, and that is the design.** An unreconciled book
aborts the pass (RK-29); a partial pass emits **no alerts at all** (RK-30); an uncomputable factor
returns `unmeasured` (RK-23); an exposure that could not be computed is **never zero** (RK-36).
⚠ The one thing D-05 must never do is produce a plausible number about a book that does not exist.

# 9. What this domain deliberately does NOT do

| Not done | Why |
|---|---|
| Block, veto, downgrade or refuse a recommendation | INV-026. `refuse_to_block()` exists **in order to raise** — a domain with no `block()` is silently satisfied by a caller who assumes one |
| Size anything | D-06's, PS-2. §1.3's boundary |
| Report VaR as the headline | RK-10 — *when correlation across the book is near 1, VaR is a restatement of concentration in different units* |
| Import D-01, D-08 or an LLM gateway | RK-28 — the seat that sees everything and decides nothing needs none of them |

# 10. ⚠ Known-wrong, approximations, and open defects

| # | What | Severity | Detail | ID |
|---|---|---|---|---|
| 10.1 | ~~**Nothing ingests a broker export**~~ **RESOLVED 2026-08-26** | — | RC-9's *"derived from activity"* half now exists: `src/recording/reconcile/ingest.py` parses the **BMO InvestorLine** export, `src/recording/orders/group.py` does RC-14 grouping, `src/recording/book/from_activity.py` derives commissions (RC-15), and `src/recording/book/load.py` loads all four accounts. ⚠ *The earlier text here said "the CIBC parse" — **CIBC is only a CDR issuer and was never the broker** (RC-36, §5.3 H-0).* All four accounts reconcile to the cent | RC-9, RC-14 |
| 10.6 | ★★ **No account can produce a `COMPLETE` pass** | ⚠ **expected — this is what keeps the live card informational** | WF-R1 step 2 needs book-wide exposure, so every held name must be priced. **All four accounts hold at least one CAD-venue or CDR position**, and those symbols are **`402` on the current FMP plan** — measured 2026-08-26, `/stable/quote-short?symbol=MDA.TO` → 402, `MRV.NE` → 402, against a `NVDA` control at 200. ★ **RK-30 is right to leave the pass `UNCHECKED`**: a concentration figure computed over the priceable 40 % of a book is not a partial answer, it is a wrong one. D-12 **DN-39** then keeps the card non-actionable | **RC-58**, DE-49, RK-30 |
| 10.2 | **`short_tail_pct` is a guess** | low | RK-39 says *report the distribution against the book's own holds* and names no decile. 25 % is a plausible tail and was never measured | RK-39 |
| 10.3 | **Correlations and vols are supplied, not fetched** | ⚠ expected | `marginal_risk` takes them as arguments; **D-02 publishes no correlation contract yet**, so `P` is `unmeasured` in every real run today | RK-20, QK-3 |
| 10.4 | **Effective breadth is not computed** | ⚠ expected | RK-9 requires it on any reported VaR and **QK-3 is open on whether D-05 owns it**. The check enforces its *presence*; nothing produces it | RK-9, QK-3 |
| 10.5 | **`capital_base` defaults to `nav_base`** | low | RC-19 says the base is read from the book; contributions and withdrawals should separate the two. With no activity pipeline (10.1) they coincide | RC-19 |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_risk_b5.py` — 45 cases, each docstring naming its `AC-5.n` |
| 2 | ★ **Break it and confirm red** | **(a)** In `src/risk/metrics/marginal.py`, replace the `_mctr` call with `max(0.0, after - before)`. `test_ac_5_20_marginal_risk_is_marginal_not_standalone` must fail — ★★ **that is the estimator that reads identically for a diversifier and for the sixth semiconductor.** **(b)** In `src/risk/metrics/drawdown.py`, return a zero-depth `DrawdownState` instead of `unmeasured` on a short series. `test_ac_5_19a_an_incomplete_series_is_unmeasured_never_zero_drawdown` must fail — **it flatters exactly the state that deserves least confidence.** **(c)** In `src/risk/exposure/aggregate.py::exposure`, key `by_name` on `instrument_id`. `test_ac_5_3_a_cdr_and_its_underlying_are_one_exposure` must fail — ★ **and concentration is understated by exactly the amount that matters** |
| 3 | The worked example (§4) reproduces | `test_rk30_alerts_are_emitted_only_from_a_complete_pass` runs the whole ladder |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **No.** Every number here is computed from a book the tests construct. **Nothing has been reconciled against a real CIBC export** (10.1), which is the one external check that would matter — and RC-10 is precisely the check that would catch a parse error |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-risk-management.md` | **§4A** the runtime ladder, RK-29…RK-36; **RK-37/38/39**; **CT-5.1/5.2/5.3** |
| `sdd/design/rel6_design/L1-recording.md` | **CT-11.4**, RC-4, RC-9, RC-10, RC-16, RC-19, RC-25, RC-28 |
| `sdd/design/rel6_design/L1-portfolio-strategy.md` | §5.1d — what D-06 does with `P` and `D` |
| `sdd/design/rel6_design/L3-build-sequence.md` | **BS-15**, **BS-15a**, **BS-15b** |
