# Blueprint — D-03 Quantitative Analysis *(B3 slice)*

> **Code:** `src/quant/` · **Spec:** `sdd/design/rel6_design/L1-quantitative-analysis.md` · **Seat:** SEAT-3
> **Status:** written 2026-08-23 at **B3** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **PARTIAL DOMAIN.** B3 builds **HorizonSet v1, the method register, and one declared ranking
> rule**. The evaluation protocol (§7), backtesting, screens, gates and the metric machinery are
> **B4** — §9 lists what is absent.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-27 | ★★ **The portfolio simulation — `cost_survival` could not be reached before it** | `engine.evaluate()` took `gross_return`/`net_return` as arguments and **nothing produced them**, so the gate was `NOT_EVALUATED` on every run and **no artifact could be promoted by construction** (MT-17). `src/quant/backtest/portfolio.py` closes it. ★ It also compounds the **equal-weight universe**, because under INV-017 survivorship flatters the strategy *and* the benchmark — the **excess** is what survives that, the level is not | *Quoting an absolute annualised return* — on today's index over ten years it measures the sample, not the signal |
| 2026-08-25 *(§7)* | **The gate's bar is the MDE, not a hand-picked IC** | A fixed threshold means different things at different `n`, `T` and `h` — §5.3b's own table shows the same `0.03` is undetectable at 1q and comfortable at 1w. The MDE is **computable before anything is measured**, so it is the bar rather than a prediction | *A configured IC floor* — it looks objective and encodes an unstated sample size |
| 2026-08-25 *(§7)* | **Effective N is `T/h`, and the t-stat uses the corrected SE** | Overlapping labels mean `T` dates are not `T` observations. Using `T` inflates every t-statistic by the square root of the horizon — **4.6x at 1m** — and turns noise into a passing gate. That is exactly the error QA-5 exists to prevent | *Newey-West with an estimated bandwidth* — it estimates a quantity the horizon already tells us exactly, adding a free parameter where none is needed |
| 2026-08-25 *(§7)* | **Purging is applied on BOTH sides of the test block** | A training row **after** the block whose label window reaches back into it is exactly as leaky as one before — the overlap has no preferred direction. Purging only the past is the common half-implementation | *Past-only purging* — halves the protection for no stated reason |
| 2026-08-25 *(§7)* | **A date with no usable cross-section is dropped, not scored 0.0** | Zero variance makes the correlation undefined. Counting it as `0.0` biases the mean **toward no signal**, which is the safe-looking direction and still wrong | *Filling with 0.0* — it makes the metric look better behaved than the data is |
| 2026-08-25 *(§7)* | ⚠ **The flat commission is 9.95, measured — not the 10.00 the legacy backtester asserts** | **QA-123.** `backtester.py:14-18` reads *"BROKER REALITY: flat $10 per trade"*; **137 real BMO orders put it at 9.95**, CAD and USD alike (D-11 RC-43). The 0.5% error is trivial per trade and **not** trivial where §5.6a uses it — ground (b) turns on a cost *differential* that flips sign at 3-12 bps | *Keeping 10.00 as close enough* — an unsourced constant doing load-bearing work is precisely QA-48's defect |
| 2026-08-23 | `model_artifact_id` is the **content hash of the ranking module's source** | QA-121's rule is **re-runnability**, not the existence of a fitted artifact. A hashed rule satisfies it exactly as a hashed model does, and it changes the moment the maths does | `null` until B4 — QA-121 forbids it, and rightly: a nomination nobody can re-run is a number with no provenance |
| 2026-08-23 | `z` is a **within-ticker (time-series)** standardisation | ⚠ At `n = 1` the cross-sectional sd is undefined. The substitution is **in the `formula_id`**, so it reaches the hash and the stored nomination | A cross-sectional `z` with a silent n=1 fallback — an implicit branch that changes the meaning of the output without changing its name |
| 2026-08-23 | The ranked quantity is **denormalised** even at n=1 | ★ QA-58. Ranking on `z` alone is a low-vol tilt, and installing it now makes it a seam that gets more expensive to remove once a model depends on it | Deferring denormalisation to B4 — the observable behaviour would change at exactly the milestone where a regression is hardest to spot |
| 2026-08-23 | An unrankable name is **skipped**, not scored | PD-1/PD-2: a `NaN` z is *unknown*, and `fillna(0)` would let a data-poor name compete for the slot on the claim of being exactly average | `fillna(0.0)` — the P5 violation with a friendly name |
| 2026-08-23 | The method register scans for **`FORMULA_ID = "…"` assignments** | A grep for dotted lowercase would match half the codebase; **a check that fires on noise is a check that gets turned off** (IM-2) | Any-string matching — false positives, then disabled |

---

# 1. What this domain does, in one paragraph

D-03 ranks and measures; **it never emits a verdict** (QA-29). The B3 slice supplies the approved
**HorizonSet v1** (which horizon nominates, which may only delay, which never reaches a human), a
**method register** that fails the build on a `formula_id` with no provenance, and one deterministic
ranking rule producing a **CT-3.4 Nomination**. It holds no fitted parameters (QA-28).

# 2. The objects and how they flow

```text
   CT-2.2 panel (D-02: mom_21, vol_21)
        │
        ▼
   within_ticker_z ──► z ──┐
                           ├──► ranked_quantity = z · sigma · sqrt(21)
   vol_21 ──► sigma ───────┘            │
                                        ▼
   HorizonSet v1 (arbitration) ──► CT-3.4 Nomination ──► D-12
                                        ▲
                            rule_id() — the content hash (QA-121)
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `HorizonSet` | `src/quant/horizons/horizon_set.py::HorizonSet` | `PRODUCTION_V1` (module constant) | the ranker, D-04 later | versioned, immutable |
| `Nomination` | `src/quant/contracts/nomination.py::Nomination` | `src/orchestration/jobs/b3_run.py::_nominate` | D-12 | one run |
| MethodEntry | `src/quant/methods/entries/` (markdown) | a human | the build check | the formula's lifetime |

★ **The object that surprised me: `rule_id()`.** It hashes *this file's own bytes*, so editing a
comment in the ranker changes the recorded `model_artifact_id`. That is louder than necessary and
deliberately so — a false alarm is cheap; a nomination attributed to the wrong maths is not.

# 2a. ★ As-built — the portfolio simulation *(2026-08-27)*

⚠⚠ **`engine.evaluate()` has always taken `gross_return` and `net_return` as
ARGUMENTS, and nothing produced them.** So `cost_survival_gate` reported
`NOT_EVALUATED` on every run and **no artifact could be promoted by
construction** — MT-17 requires every required gate to PASS, and one of them
could not be reached at all.

| Module | What it is | ⚠ Open / known-limited |
|---|---|---|
| `src/quant/backtest/portfolio.py` | scored predictions → held positions → gross, net, benchmark | ⚠ `TOP_N = 10` and `--capital` are **admitted choices** (CN-10), and §7.1 shows the cost gate turns on both |
| `src/quant/metrics/breadth.py` | QA-43's effective breadth — `n`, `ρ`, `n_eff`, `BR` | ⚠⚠ **QA-124/QQ-14 — the gate is fed the RAW correlation, not QA-43's residual one.** See below |

## The decisions, and why each could have gone another way

| Decision | Why | ⚠ What it is not |
|---|---|---|
| **Rebalance every `horizon_days`, not daily** | Daily rebalancing on a 21-day label charges **21× the commission** for a signal that only changes monthly | the cost gate would then fail on an artefact of the simulation, not a property of the strategy |
| **Commission on TURNOVER, not holdings** | A name held through a rebalance incurs no fee | ⚠ the legacy `_reconcile_bucket` docstring said this and **its code did not** |
| **Equal weight over the top N** | makes the number about the **ranking** | ★ **not a sizing decision** — D-06 owns sizing (PS-43) |
| **Returns COMPOUND** | adding period returns overstates an alternating series and understates a trending one | over 100 periods that is not a rounding error |
| **Labels are the return source** | the simulation cannot disagree with the series the labels were built from | it holds no price series of its own |

## ⚠⚠ Open questions carried to `L6-as-built-remaining.md`

★★ **The benchmark is why the absolute return is not the headline.** The
simulation also compounds the **equal-weight universe on the same dates**, so the
reported figure is *"did the ranking beat holding everything"* rather than *"did
the strategy make money"*. ⚠ **This matters most under INV-017**: today's index over ten years flatters the
strategy **and the benchmark alike**, so the *excess* is **less** contaminated
than either level.

⚠⚠ **It is NOT "far more robust", and an earlier draft of this paragraph said so
— wrongly.** Survivorship removes the losers, and a *ranking* strategy is spared
precisely the picks it would have got wrong, so it benefits **asymmetrically**
against an equal-weight benchmark that merely holds everything. ★ The excess is
therefore biased **upward**, by an amount nobody has measured. An absolute
annualised return should not be quoted on its own; **an excess should be quoted
with this caveat attached**.

⚠ **`proportional_bps = 0.0` and stated.** QA-49: spread and slippage are not
modelled, and §5.6a's ground (b) **flips sign at 3-12 bps** — so the true drag is
larger by an amount nobody has measured, and a `cost_survival` PASS is a PASS
against commission only.

## ⚠⚠ QA-124 — the breadth measure diverges from QA-43, deliberately

QA-43 asks for *"average pairwise **residual** correlation after removing the
market and dominant sector factors."* ★★ **Measured on synthetic panels with a
known common correlation, that procedure returns `−1/(n−1)` and nothing else:**

```text
   n     rho_true   rho_residual   -1/(n-1)      rho_raw
   12      0.00       -0.09090     -0.09091       0.0060
   12      0.35       -0.09088     -0.09091       0.3384
  500      0.35       -0.00200     -0.00200       0.3463
```

⚠ **Identical at `rho_true = 0.00` and `0.35`.** Removing a factor built from the
same names removes the correlation the measure exists to find. The raw measure
recovers the truth to three decimals.

★ **Both readings are legitimate and ask different questions.** *Residual*
correlation asks *"is there structure left after the known factors"*; **G&K's
`BR` asks how many independent BETS a book holds** — and ten names all with β≈1
are one bet however independent their residuals are. The gate wants the second,
so it is fed `rho_raw`, and the residual figure is reported beside it.

⚠ **QA-43 is not amended.** Which statistic the gate should consume is registered
as **QQ-14, open** — resolving it decides whether the rule changes or the gate
does.

★ The measure also **demonstrates QA-44** rather than asserting it: at
`ρ = 0.35`, going from 12 names to 500 moves the independent count from **2.54 to
2.88** — *488 extra names buy a third of a bet*.

⚠⚠ **`BR` is bets per YEAR, not a name count** — L1-quant v0.4.0 correction (c)
records that the two were once conflated, so `n_eff` and `BR` are both returned
and never interchanged.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | resolve the nominating horizon | `src/quant/horizons/horizon_set.py::HorizonSet.horizon` | ★ **QA-47/QA-120: `h1m` nominates and nothing else may.** Reading it from the HorizonSet rather than a caller is what keeps the rule out of an `if` | `HorizonUnpinnedError` |
| 1 | standardise within ticker | `src/quant/signals/rank.py::within_ticker_z` | needs the trailing window before any scaling | `NaN` — and a `NaN` is *not rankable*, not average |
| 2 | denormalise | `src/quant/signals/rank.py::rank_candidates` | ★ QA-58: `z · σ · √h`, so the ranking is in return units | skipped rows |
| 3 | order, stably | same | **PD-20** — ties break on ticker. *A ranking system with an unstable tie-break is not reproducible, and D-03's whole product is a ranking* | — |
| 4 | build the contract | `src/quant/contracts/nomination.py::Nomination` | validates QA-119…QA-122 at construction, so a malformed nomination cannot exist | `NominationContractError` |

# 4. ★ The mathematics

### The ranked quantity

| | |
|---|---|
| **Implemented in** | `src/quant/signals/rank.py::rank_candidates` |
| **Formula** | ```python\nrows.append({"ticker": r["ticker"], "z": float(z),\n             "ranked_quantity": float(z) * float(sigma) * scale})\n``` with `scale = math.sqrt(horizon_days)` |
| **Units** | `z` (sd units, dimensionless) × `σ̂` (per day) × `√21` (√sessions) = ★ **an expected 21-session return** |
| **Domain / range** | Unbounded either sign. `NaN` in either factor ⇒ the name is not ranked |
| **Why this form** | QA-58: ranking on `z` divides out exactly the quantity the position will be sized against, producing a systematic low-volatility tilt |
| **Alternatives rejected** | Fully in `src/quant/methods/entries/rank.denormalised_within_ticker_z.v1.md` |
| **Sensitivity** | ★ **`σ̂` dominates when `z` is small.** Two names at equal `z` are ordered *entirely* by volatility — which is the intended behaviour and is also the thing a reader is most likely to mistake for a bug |
| **★ Worked example** | `z = 2.0`, `σ̂ = 0.02/day`, `h = 21` → `2.0 × 0.02 × √21 = 0.183303…` (≈ 18.3 % over the month). Live NVDA 2024-08-30: `z = 0.4250`, `rq = 0.111491` |
| **Known-wrong** | ⚠ `√h` scaling assumes iid returns. **Momentum is autocorrelated by definition**, so `√h` understates a trending name's horizon volatility — the estimate is biased low exactly for the names that rank highest |

### The within-ticker z-score

| | |
|---|---|
| **Implemented in** | `src/quant/signals/rank.py::within_ticker_z` |
| **Formula** | ```python\nz = (series - mean.reindex(ordered_idx)) / sd.reindex(ordered_idx)\nz[sd.reindex(ordered_idx) == 0] = np.nan\n``` |
| **Units** | dimensionless (sd units) |
| **Domain / range** | `sd > 0`; a flat signal gives `NaN`, **not 0 and not infinity** |
| **Why this form** | At n=1 there is no cross-section. The variant is declared in the `formula_id` so a stored nomination says which was used |
| **Alternatives rejected** | Cross-sectional `z` with an n=1 fallback — a branch that changes the meaning without changing the name |
| **Sensitivity** | The 21-row window: `SE(sd) ≈ 16 %`, inherited from `vol_21` |
| **★ Worked example** | A constant series has `sd = 0` ⇒ `z = NaN` ⇒ the name is unrankable. ⚠ **Not `z = 0`**, which would say "exactly typical" about a signal that never moved |
| **Known-wrong** | ★ **This is not the quantity QA-58 means.** Cross-sectional asks *"rich relative to peers today"*; this asks *"rich relative to its own recent history"*. At n=1 they coincide trivially, and **at n>1 they do not** — B4 must replace it, not extend it |

# 5. The logic decisions

| Decision | Where | Why this way | What it would take to change it |
|---|---|---|---|
| Ties break on **ticker**, ascending | `rank_candidates` | PD-20 determinism. Alphabetical is arbitrary and *stated*, which is what matters | one sort key |
| `h1q` is **rejected**, not ignored | `Nomination.__post_init__` | QA-120. Silently dropping it would let it back in later | — |
| `candidates` must be **dense from rank 1** | same | QA-122: a gap means a name was filtered after ranking, and the reader could not tell | — |
| The register scans `src/` at test time, not import time | `src/quant/methods/registry.py` | **IM-7**: no import-time side effects. A build check that ran on import would make `--help` walk the tree | move the call |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Who reads it | Changing it affects |
|---|---|---|---|---|
| HorizonSet | `src/quant/horizons/horizon_set.py::PRODUCTION_V1` | `production@v1` | everything | ⚠ **the contract**, not a setting — CT-3.1 is approved (§5.6) and a change is a version bump |
| `Z_WINDOW_SESSIONS` | `src/quant/signals/rank.py` | 21 | `within_ticker_z` | ⚠ a policy choice in code (CN-3); matched to `vol_21`'s window so both halves span the same period |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | **CT-2.2** panel with `mom_21`, `vol_21` | D-02 | `KeyError` — *"D-03 ranks D-02's numbers and computes none of its own"* |
| out | **CT-3.4** Nomination | D-12 | `NominationContractError` at construction |
| out | **CT-3.3** MethodEntry | the build | `MethodMissingError` |

# 8. Failure behaviour

| Failure | Detected where | Behaviour |
|---|---|---|
| a `formula_id` with no MethodEntry | `src/quant/methods/registry.py` | `MethodMissingError` — ★ fails the **build**, not the run |
| a horizon that is not in the set | `HorizonSet.horizon` | `HorizonUnpinnedError` |
| purge shorter than the longest horizon | `HorizonSet.__post_init__` | `HorizonUnpinnedError` |
| a nomination violating QA-119…122 | `Nomination.__post_init__` | `NominationContractError` |
| every candidate unrankable | `rank_candidates` → `Nomination.top` | raises — *a run that could rank nothing produces no nomination, not a nomination of nothing* |

# 9. What this domain deliberately does NOT do — and what B3 leaves unbuilt

| Not in the B3 slice | When |
|---|---|
| the evaluation protocol (§7), CPCV, purge/embargo enforcement | B4 |
| backtesting, CT-3.2, cost models, `initial_capital` from D-11 | B4/B5 |
| screens (52w position, gaps, volume), signal composition | B4 |
| gates, effective-N, corrected standard errors | B4 |
| ★ **measuring `τ`** — three decisions wait on it (BS-13) | B4 |
| the quantile heads that would author stop/target (QA-27, §9.3) | B4+ |
| emitting a verdict | ✗ **never** (QA-29) — gating is P3's business, downstream |
| holding fitted parameters | ✗ **never** (QA-28) — that is D-04's |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — the `z` is time-series, not cross-sectional** | ⚠ **medium, by design** | It is **not the quantity QA-58 specifies**. Honest at n=1, wrong at n>1, and declared in the `formula_id` so a stored nomination says so | QA-58, replaced at B4 |
| **10.2 — `universe_n = 1` makes every power figure degenerate** | ⚠ expected | `E[max z]` at n=1 is meaningless, and `L2` §7A.2's downstream cost figures depend on it. **B3 nominates from a universe of one; nothing about that generalises** | QA-121, QA-113 |
| **10.3 — `rule_id()` hashes comments too** | low | A docstring edit changes the recorded `model_artifact_id`. Deliberately loud | — |
| **10.4 — no MethodEntry check runs in CI's build step** | ⚠ medium | AC-3.14 says *"fails the build"*; today it fails a **test**. Equivalent for now because `make check` runs tests, and it would not survive someone running the pipeline without them | AC-3.14 |
| **10.5 — `√h` scaling is biased low for the top of the ranking** | ⚠ medium | Momentum is autocorrelated, so the horizon vol of a trending name exceeds `σ̂√h`. **The bias is toward under-stating risk on exactly the names that get nominated** | new — no ID |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_quant_b3.py` — 18 cases, each docstring naming its `AC-3.n` or `QA-n` |
| 2 | ★ **Break it and confirm red** | In `src/quant/signals/rank.py::rank_candidates`, drop the `* float(sigma) * scale` and rank on `z` alone. `test_qa_58_the_higher_volatility_name_ranks_first_at_equal_z` must fail — **that multiplication is QA-58** |
| 3 | The worked example (§4) reproduces | `python -c "import math; print(2.0*0.02*math.sqrt(21))"` → `0.1833030277982336` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **No — self-consistency and arithmetic known-answers only.** The ranking has no external referent until the evaluation protocol lands at B4; **that is what "the rank is trivial" means in BS-10** |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-quantitative-analysis.md` | CT-3.1 (approved v1), CT-3.3, CT-3.4, **QA-58**, QA-119…122, §8 |
| `sdd/design/rel6_design/L1-feature-engineering.md` | the CT-2.2 panel and why `vol_21` is a feature |
| `sdd/design/rel6_design/L1-decision.md` | **DN-34** — the nomination D-12 composes |
| `sdd/design/rel6_design/L3-build-sequence.md` | B3's scope; **BS-13** (`τ` is measured at B4) |
