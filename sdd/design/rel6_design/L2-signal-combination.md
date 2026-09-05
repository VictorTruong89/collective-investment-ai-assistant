# L2: Cross-Domain Design — Combining D-01, D-03 and D-05

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** §1.6 — *the deferred combine point*
> **Resolves:** L0 §1.6 · D-03 **QQ-6** · `L4-coding-standards.md` **Q-5** · ~420 LOC blocked
> **Spans:** D-01 (fundamental) · D-03 (quant) · D-05 (risk) — a cross-domain design, hence **L2**
> **Binding:** **P3** (verdicts gate, never upgrade) · **INV-014** (seat independence) ·
> **INV-026** (concentration reported, never blocked) · **INV-6** · **M-2** · **AP-5**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.7.0 | 2026-08-18 | Victor | ✅ **Menu resolved.** F0 done (QA-107/110 — and **re-basing δ on the mandate dissolves the capital-base dependency**), F1/F3/P1 adopted (RA-59/57/55), P3 adopted as target (QA-113), P2 planned with a trigger (RA-56). ⚠ **P4 WITHDRAWN**: `k_stab: 3→5` measures the decoder rather than the analysis — no `temperature` is set anywhere — and is **replaced by a free change**, perturbing the input instead of resampling (RA-61). New **CB-33**: a metric that would vanish if a config flag changed is measuring the config. |
| 0.6.0 | 2026-08-18 | Victor | ★★ **New F0 at the top of the menu: resolve QA-63.** `$20,000` is a backtest literal and `$142,500` an F4 contract *example* — **neither measured** — and this document priced every coverage % against one while D-03 derived `δ` from the other, a **7× disagreement**. **CB-31**: the binding constraint was never money, it is *not knowing how much money there is*. **CB-32**: CB-30's freeze cliff is only half the danger — `δ` is bounded below too, and at a realistic book the hold collapses to ~2 days (**M-4 violation**). `k_stab` corrected to multiply with `k_cov` and given a **trigger** rather than a vague "later". |
| 0.5.0 | 2026-08-18 | Victor | ★★ **CB-30 — the freeze boundary.** `IC_critical = rt/(E[max]·σ) = 0.0223`, and the assumed `IC₀₃ = 0.030` sits only **26 % above it**; below it `δ_floor` exceeds the largest achievable opportunity gap and **the portfolio never trades** — §5.8.7's ladder kill from the parameter axis. **CB-23 widened**: `IC₀₃` is load-bearing for four conclusions across three documents including **QQ-21's sleeve architecture**. **CB-25 reversed — `n`→500 now precedes `k_cov`→3**, because measurement gates the interpretation of capability. Three corrections from external review: the uplift table applied the **full-coverage** formula at partial coverage (correct figures **+20 % at k=3, +32 % at k=10**, ~half the √2 limit); the `ρ` SE ignored **range restriction** (corrected 0.179 at k=3 — optimistic by 3.5×, the *same* error DN-28 already names); and `√(2 ln n)` is **+20 % high** at these `n` (Blom is correct). New **CB-28** (never merge covered and uncovered into one sort), **CB-29** (`k_cov` buys capability, stratification buys measurement — two purchases, F3 is P1's precondition). |
| 0.4.0 | 2026-08-18 | Victor | ★ **New §7A parameter/assumption register and §7B reliability menu.** ★★ **§4.3's cost argument priced the wrong point on the curve**: the gate/rank transition is at **`k_cov = 2`, not `k_cov = n`**, and covering the quant's **top-3 costs $624/yr (0.44 % NAV)** against the $27 k it priced for full coverage — so **CB-5 is conditional on `k_cov = 1`** (**CB-19**) and falls at `k ≥ 2`. ★ **`n: 130→500` buys only +17 % alpha but HALVES the MDE on `IC₀₃`** — from 0.0440 (larger than the 0.03 assumed) to 0.0224 — so it is a **measurability** investment, and **`IC₀₃` is revealed as an assumption that is currently unfalsifiable** (**CB-23**). §7B ranks levers by what they unblock per dollar: **the free ones bind, because their clocks start only when recording starts** (CB-24), and **F3 — stratifying D-01's existing rotating sample — buys `ρ` for zero marginal cost**. CB-19…CB-27. |
| 0.3.0 | 2026-08-18 | Victor | **§4.2a** — the sharp threshold `IC₀₁ > ρ·IC₀₃`, below which the optimal weight on the thesis is negative. **§4.2b** — the **forecast-combination puzzle**: fitting weights at this breadth is *active harm*, not merely forgone gain. Both from external review; both now the backbone of `L1-decision.md` §5.0. |
| 0.2.0 | 2026-08-18 | Victor | **QB-1, QB-2 and QB-5 closed** by the new `L1-decision.md` (**D-12**). QB-2 dissolved rather than resolved — commutativity of the meet means two delay authorities cannot deadlock. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. **§2 finds the three specs ready.** §4 is the mathematics: §4.1 proves the current blend has a **2.0× selection bias under pure noise**; §4.3 shows dense thesis coverage costs **6.3–19 % of NAV per year**, which is the decisive constraint; §4.4 shows the problem is textbook **Black–Litterman** and why BL's own degradation behaviour argues *against* blending here. §5 surveys practice and literature. §6 recommends **quant ranks → thesis gates → risk alerts**, which ratifies the existing architecture on grounds it never had. |

---

# 1. THE QUESTION

> **"D-01 says the business is good. D-03 says the name ranks 4th of 130. D-05 says the book is
> already 62 % in one theme. What comes out?"**

This has been deferred since L0 v0.1.0 and is referenced as open in six documents. It is the last
structural question in the design.

---

# 2. READINESS — are the three specs ready to support this?

**Yes.** Each supplies the thing the combination needs, and — more usefully — each already states a
property that *constrains* the answer.

| Spec | Version | What it supplies | ★ The constraint it imposes |
|---|---|---|---|
| **D-01** fundamental | v0.1.0 | CT-1.1 Thesis: `verdict`, `conviction`, **`verdict_stability`** (RM-1's k-run agreement), `confidence` with an explicit **calibration status** | ★ **`confidence.calibration = not_yet_calibrated (N=3)`.** RA-21 forbids publishing a bare confidence number. **An uncalibrated number cannot be a weight** |
| **D-03** quant | v1.4.0 | CT-3.1 HorizonSet with an **arbitration block** (`nominates / may_delay_or_veto / research_only`), CT-3.2 with per-horizon IC and **effective N** | ★ **D-03 already solved a combination problem internally** (QA-47), and solved it as *nominate + veto*, not as a blend. §6 mirrors its shape |
| **D-05** risk | v0.1.0 | Exposure, drawdown, flags, `P`/`D` factors, **LEVEL 2 ALERT** | ★ **INV-021 + INV-026: unsuppressible and powerless.** D-05 **cannot** be a gate in the P3 sense, because a gate that may never block is not a gate |

Three further facts are established and load-bearing:

- **INV-014 is not in the way.** It constrains *production of* the two analyses, not their combination — L0 §1.6 says so explicitly. Combining is legal; the question is only *how*.
- **P3 was amended on 2026-08-13.** The "quant ranks, thesis gates" **ordering is no longer mandated**; only monotonicity survives. So the existing architecture is a *choice that has never been justified* — this document is where it gets justified or replaced.
- **Both mechanisms already exist in the code, and they disagree.** `discipline/gate.py` implements a P3 gate (`PASS/FLAG/FAIL`, veto-only); `core/signal_engine.py:158` `combined_score` implements a linear z-blend. Nobody chose between them.

> **One clarification that prevents a false alarm.** `combined_score` blends `fundamental_composite`,
> which is **D-02's** computed composite (seat 5), **not D-01's thesis**. That is legitimate under
> INV-014 and always was. The blend is **quant-internal**; the thesis has never entered a score.
> **CB-14** requires the column to be named so no future reader re-litigates this.

---

# 3. ★ THE THREE OUTPUTS ARE NOT THE SAME KIND OF OBJECT

Before any weighting question, a typing question — and it disposes of most of the design space.

```text
  D-03   s : U → ℝ                     n = 130 names, every day.
         a CROSS-SECTIONAL FORECAST.   Comparable across names by construction;
                                       calibratable against realised return.

  D-01   v : V → {BUY,HOLD,SELL}×conf  |V| ≈ 1 per day.
         a PER-NAME CONDITIONAL        NOT comparable across names — "BUY MU" and
         JUDGEMENT.                    "BUY ARM" do not order MU against ARM.
                                       NOT calibrated (CT-1.1, N=3).

  D-05   g : (book, candidate) → alert  a PREDICATE ON A PAIR.
         a BOOK-STATE FUNCTION.        Not a property of the candidate at all:
                                       the same name scores differently depending
                                       on what is already held.
```

```text
╔══════════════════════════════════════════════════════════════════╗
║  score = w1*quant + w2*thesis + w3*risk   IS A TYPE ERROR.       ║
║                                                                  ║
║  D-05 is not a function of the candidate — it is a function of   ║
║  the (book, candidate) PAIR. Two identical candidates get        ║
║  different D-05 values depending on what you already own. There  ║
║  is no column to add.                                            ║
║                                                                  ║
║  D-01 is not cross-sectionally ordered. A verdict ranks a name   ║
║  against ITSELF at another price, never against another name.    ║
║                                                                  ║
║  P3's "gate, never blend" is usually read as a safety rule.      ║
║  It is also a TYPE-CORRECTNESS rule, and that is the stronger    ║
║  reading because it does not depend on anyone's risk appetite.   ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 4. THE MATHEMATICS

## 4.1 ★ The naive blend is not merely awkward — it is provably biased

`combined_score` renormalises over present components and, per its own docstring, treats *"a name
lacking a fundamental score as the cross-sectional average (z = 0) rather than dropped."*

Let the composite be `S_i = w_q·z(s_i) + w_f·z(f_i)` with `w_q = 0.65`, `w_f = 0.35`, and `f_i`
observed only on `V`, imputed to 0 elsewhere. Then under independence:

```text
    Var(S_i)  =  w_q²           for i ∉ V        =  0.4225
    Var(S_i)  =  w_q² + w_f²    for i ∈ V        =  0.5450

    SD ratio  =  √0.545 / 0.65  =  1.1358        ← covered names are 13.6% wider
```

Selection is `argmax` (INV-6, top-1). **A wider distribution wins an argmax more often**, entirely
independently of skill. Simulated at `n = 130`, 400 000 draws, **pure noise — no skill anywhere**:

| covered `k` | P(pick is covered) | fair share `k/n` | **lift** |
|---:|---:|---:|---:|
| 1 | 1.55 % | 0.77 % | **2.02×** |
| 3 | 4.59 % | 2.31 % | **1.99×** |
| 5 | 7.50 % | 3.85 % | **1.95×** |
| 10 | 14.54 % | 7.69 % | **1.89×** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  A NAME IS TWICE AS LIKELY TO BE PICKED SIMPLY BECAUSE SOMEONE   ║
║  WROTE A THESIS ABOUT IT — WITH NO SKILL IN THE THESIS AT ALL.   ║
║                                                                  ║
║  And the mechanism is self-reinforcing: coverage is chosen by    ║
║  looking at names that already rank well, so the bias feeds the  ║
║  sample that generates it.                                       ║
║                                                                  ║
║  This is L4 PD-1/PD-2 (imputation is the P5 violation with a     ║
║  friendly name) showing up as a live selection defect, not a     ║
║  style complaint.                                                ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **CB-1** | ★ **No missing signal is ever imputed to the cross-sectional mean.** A name without a component is either **excluded from that component's ranking** or the component is **absent for everyone** — never silently averaged (L4 PD-1, PD-2) |
| **CB-2** | ★ **Any composite must have identical variance across the covered and uncovered populations, or it is biased by construction.** This is testable directly under a null and is the cheapest guard available |

## 4.2 What combining actually buys — the Fundamental Law

Grinold & Kahn: `IR ≈ IC·√BR`. For two signals with correlation `ρ`, optimally weighted, the
composite IC is the multiple-correlation coefficient

```text
                  ┌                                    ┐ ½
        IC_c  =   │  (IC₁² + IC₂² − 2ρ·IC₁·IC₂)        │
                  │  ─────────────────────────────     │
                  └           (1 − ρ²)                 ┘

    with optimal weights   w ∝ Σ⁻¹ · IC        (Markowitz on signals;
                                                Qian–Hua–Sorensen 2007)
```

At `IC₁ = 0.03` (D-03's central τ case), as an **IR multiplier over quant alone**:

| ρ | IC₂ = 0.01 | IC₂ = 0.02 | IC₂ = 0.03 |
|---:|---:|---:|---:|
| 0.0 | 1.05× | 1.20× | **1.41×** |
| 0.2 | 1.01× | 1.11× | 1.29× |
| 0.4 | 1.00× | 1.04× | 1.20× |
| 0.6 | 1.05× | 1.00× | 1.12× |
| 0.8 | **1.27×** | 1.02× | 1.05× |

Three readings, in order of importance:

1. ★ **The value of the combination is a fact about `ρ`, not about D-01's quality.** An excellent
   thesis engine that likes the same names the model likes adds ~nothing (0.03/0.03 at ρ=0.6 is
   1.12×). A mediocre one that is *uncorrelated* adds more.
2. ★ **`ρ` is currently unmeasured, and at 1 thesis/day it is unmeasurable.** Estimating a
   correlation between two cross-sectional scores requires both to exist cross-sectionally.
3. ⚠ **The 1.27× at `ρ = 0.8, IC₂ = 0.01` is a trap.** That gain comes from a **negative optimal
   weight** — the weak, highly-correlated signal earns its place as a *hedge* against the strong
   one's noise. Operationally it means *"when the analyst says BUY, buy less."* It is real
   mathematics and an unusable instruction, and it is what naive `Σ⁻¹·IC` optimisation will
   produce if pointed at this problem without constraints.

### 4.2a ★ The sharp form — when D-01 adds nothing at all

With `k = IC₀₁ / IC₀₃`, the uplift over quant alone is `√((1 − 2ρk + k²)/(1 − ρ²))`. Set `ρ = k`:
numerator and denominator both become `1 − k²`, and the uplift is **exactly 1**.

```text
╔══════════════════════════════════════════════════════════════════╗
║   D-01 ADDS VALUE AS A SIGNAL IFF   IC₀₁  >  ρ · IC₀₃            ║
║                                                                  ║
║   Below that line the optimal weight on D-01 is NEGATIVE — the   ║
║   algebra instructs you to short the fundamental view. That is   ║
║   CB-4's incoherent case, reached by a cleaner route.            ║
║                                                                  ║
║   For equal-strength signals the whole table collapses to        ║
║        IC_c = ic · √( 2/(1+ρ) )                                  ║
║   ρ=0 → 1.41×,  ρ=1 → 1.00×. The entire value of having a        ║
║   fundamental seat lives in how UNCORRELATED it is.              ║
╚══════════════════════════════════════════════════════════════════╝
```

### 4.2b ★ …and why the weights must not be fitted anyway

Even where `IC₀₁ > ρ·IC₀₃`, **fitting the weight is the wrong move at this breadth.** The
**forecast combination puzzle** (Smith & Wallis 2009; Claeskens et al. 2016) is that optimal weights
are optimal only when the covariances are *known*; estimated weights are random, which **induces
bias even in unbiased components and inflates variance**, so parameter-free combinations routinely
win out of sample. DeMiguel, Garlappi & Uppal (2009) is the portfolio twin — `1/N` beats
optimisation.

> ★ **The penalty for fitting is active harm, not merely forgone gain.** This is developed as the
> primary justification for the gate in [`L1-decision.md`](L1-decision.md) **§5.0**.

| ID | Rule |
|---|---|
| **CB-3** | ★ **No combination weight is fitted until `ρ` between the two scores is measured on a common cross-section.** An unmeasured `ρ` makes every weight arbitrary, and the table above shows the answer ranges over 1.00×–1.41× |
| **CB-4** | ★ **Signal weights are constrained non-negative.** The hedging solution is mathematically valid and operationally incoherent under P3 — a negative weight on the thesis means the thesis *upgrades* a name by being negative about it |

## 4.3 ★ THE DECISIVE CONSTRAINT — breadth, and what coverage costs

The Fundamental Law's `BR` counts **independent forecasts**. This is where the design is actually
settled, and not by preference.

**D-01 does not see the cross-section.** It authors a thesis for the actionable pick (INV-6) plus a
rotating sample. Its input is *chosen by D-03's ranking*.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A SIGNAL OBSERVED ONLY ON THE NAME ANOTHER SIGNAL ALREADY       ║
║  SELECTED CARRIES ZERO RANKING INFORMATION.                      ║
║                                                                  ║
║  Not "little". Zero. Ranking requires comparison, comparison     ║
║  requires two observations, and there is only ever one.          ║
║                                                                  ║
║  Whatever D-01 knows can therefore express itself in exactly     ║
║  one way: CONFIRM or OBJECT to a nomination it did not make.     ║
║  That is the definition of a gate.                               ║
╚══════════════════════════════════════════════════════════════════╝
```

The obvious repair is to run D-01 over the whole universe. **It does not survive contact with the
cost**, at Opus-5 deep-tier pricing (INV-8), ~30k in / 5k out per thesis:

| coverage | per name | per day | per year | **as % of the $142.5 k book** |
|---|---:|---:|---:|---:|
| `k = 1`, no stability probe | $0.28 | $36 | $9,009 | **6.3 % of NAV / yr** |
| `k = 3`, RM-1 minimum (**AC-1.8**) | $0.83 | $107 | $27,027 | **19.0 % of NAV / yr** |

For scale: D-03 §5.8's *entire* trading-cost budget is **6.0 %/yr**. Dense thesis coverage costs
**one to three times the whole cost budget of the strategy**, to buy — per §4.2 — somewhere between
1.00× and 1.41× on IR, at an unmeasured `ρ`.

| ID | Rule |
|---|---|
| **CB-5** | ★ **D-01 is a gate, not a ranker, and this is a structural conclusion rather than a preference.** Its coverage is `O(1)` per day, conditioned on D-03's output, and dense coverage is economically excluded at this book size |
| **CB-6** | ★ **The gate direction is fixed by P3: D-01 may only make a verdict more conservative.** A thesis may veto or downgrade a nomination; it may **never** promote a name D-03 did not nominate, because to promote it would need the cross-sectional comparison it structurally lacks |
| **CB-7** | **CB-5 is contingent on cost and coverage**, and both are moving. §7 registers the conditions under which it is revisited — this is a live boundary, not a closed one |

## 4.4 ★ The correct formalism, and why it argues against blending here

If the two views *were* to be merged, this is not a bespoke problem. **k views on n assets with
k ≪ n is exactly Black–Litterman**, whose entire purpose is sparse views on a dense prior.

```text
    E[r | views]  =  [ (τΣ)⁻¹ + PᵀΩ⁻¹P ]⁻¹ [ (τΣ)⁻¹ Π  +  PᵀΩ⁻¹ q ]

      Π  (n×1)  the PRIOR.  ★ Here: D-03's ranked quantity ẑ·σ̂·√h (QA-58) —
                            not CAPM equilibrium. Using a quant forecast as Π
                            is standard quant-fundamental practice.
      P  (k×n)  the PICK MATRIX. Row j is eᵢ for an absolute view on name i.
                ★ This is the object that makes sparse coverage NATIVE rather
                  than a special case — no imputation, no fillna, no z=0.
      q  (k×1)  the analyst's view returns.
      Ω  (k×k)  ★ VIEW UNCERTAINTY — where D-01's RM-1 would enter.
```

Two properties make BL the right frame, and one of them is the argument against using it:

**(a) It degrades correctly.** As `Ω → ∞`, the posterior → `Π`. **A worthless thesis leaves the
quant ranking exactly untouched** — automatically, with no special-casing. That is precisely the
behaviour §4.1's blend fails to have, and it is why BL is the honest formalism.

**(b) `Ω` is where D-01's own instrumentation would land.** CT-1.1 already carries
`verdict_stability: {k: 5, modal: "BUY", agreement: 0.8}`. Mapping agreement → `Ω` is direct: a
3/5 thesis gets a wide `Ω` and barely moves the prior; a 5/5 gets a narrow one. **D-01 was specified
with the input BL needs, before anyone connected them.**

**(c) ★ And yet — `q` does not exist.** BL requires a **view return**: *"MU will return 8 % over the
next month."* D-01 produces `BUY / HOLD / SELL` with an **uncalibrated** confidence
(`not_yet_calibrated, N = 3`). Manufacturing `q` from a verdict requires exactly the calibration
mapping RA-21 forbids publishing.

```text
╔══════════════════════════════════════════════════════════════════╗
║  BLACK–LITTERMAN IS THE RIGHT FORMALISM AND CANNOT BE USED YET.  ║
║                                                                  ║
║  It needs a view RETURN and a view VARIANCE. D-01 has an         ║
║  ordinal verdict and an uncalibrated confidence. Inventing the   ║
║  missing numbers would put a fabricated q and a guessed Ω at     ║
║  the centre of the arithmetic — and BL's posterior is LINEAR in  ║
║  q, so the fabrication propagates undamped into the ranking.     ║
║                                                                  ║
║  D-01's calibration is not a missing nicety. It is the exact     ║
║  quantity a principled merge consumes. Until N accrues, the      ║
║  merge has no inputs, and a gate is the honest structure.        ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **CB-8** | ★ **If the two views are ever merged as peers, the mechanism is Black–Litterman with `Π` = D-03's ranked quantity, `P` the pick matrix over covered names, and `Ω` derived from RM-1 agreement** — not a linear z-blend. The pick matrix is what makes sparse coverage native |
| **CB-9** | ★ **BL may produce a posterior *ranking* only. It must never be run through mean–variance optimisation to emit weights** — that would be a target book, which L0 forbids (INV-026, M-2) and which is D-06's boundary |
| **CB-10** | ★ **`q` may not be manufactured from an ordinal verdict.** A BL merge is blocked until D-01's confidence is calibrated with a stated `N` and an empirical referent (RA-21). **This is the single gating precondition** — §7 |

## 4.5 D-05 cannot enter either side, and for a different reason

D-05's exclusion is not about coverage or calibration. It is about **authority**.

```text
    INV-021   risk alerts cannot be suppressed by any component
    INV-026   concentration is REPORTED, NEVER BLOCKED
```

A P3 gate returns `FAIL` and the pipeline declines to originate. **INV-026 forbids D-05 from ever
producing that outcome** on the concentration axis — the concentration *is* the mandate (M-2). So
D-05 is neither a score (§3: wrong type) nor a gate (INV-026: no authority).

| ID | Rule |
|---|---|
| **CB-11** | ★ **D-05 forms a third, parallel channel: unsuppressible and non-blocking.** It travels *beside* the recommendation, never inside it. This is L0's LEVEL 2 ALERT, and the combination design must not quietly promote it to a veto in order to make the diagram tidier |
| **CB-12** | ★ Because D-05 is a predicate on `(book, candidate)`, it is evaluated **after** a candidate exists — it cannot participate in producing one. The ordering is forced by its type, not chosen |
| **CB-13** | **The one exception is not an exception.** M-3/M-4 flags (pyramiding, registered short-hold) are also reported, not blocking (INV-028) — D-05 has *no* blocking path anywhere, and a design that gives it one has amended L0 without saying so |

---

# 5. HOW THE INDUSTRY AND THE LITERATURE DO THIS

## 5.1 The four established architectures

| Architecture | Mechanism | Who | Fit here |
|---|---|---|---|
| **Linear alpha blend** | z-score each signal, weight, sum. Weights from `w ∝ Σ⁻¹·IC` | The default quant-multifactor approach; Qian–Hua–Sorensen | ✗ **needs dense coverage** on both signals (§4.3) |
| **Bayesian view integration (Black–Litterman)** | sparse views update a dense prior via `P`, `Ω` | Goldman Sachs orig.; standard in asset allocation | ◐ **right formalism, missing inputs** (§4.4) |
| **Sequential screen / gate** | one signal ranks, the other vetoes | "Quantamental" — systematic sourcing, discretionary override | ✅ **matches the coverage asymmetry** |
| **Risk-parity across alpha sleeves** | run both as separate books, weight by inverse tracking error | Robeco: ~**65/35 quant/fundamental**, inverse-TE weighted | ✗ needs two *books*; this is one 10-name account |

## 5.2 What the sources actually say

- **Grinold & Kahn**, *Active Portfolio Management* — `IR ≈ IC·√BR`. The reason breadth, not signal
  quality, is the binding constraint in §4.3. The **Redux** literature adds the *transfer
  coefficient*, which penalises exactly the case where a good signal cannot be expressed in the
  book — a concentrated 10-name account has a low transfer coefficient by construction.
- **Qian, Hua & Sorensen (2007)**, *Information Horizon, Portfolio Turnover, and Optimal Alpha
  Models* — optimal weights are `Σ⁻¹·IC`, and **as transaction costs rise, weight should shift
  toward slower-decaying signals**. ★ That connects directly to D-03 §5.3a's decay law: the thesis
  is the slow signal (τ measured in quarters), the quant the fast one — an independent argument for
  the thesis acting as a *persistent* constraint rather than a daily score.
- **Black–Litterman** — the canonical treatment of `k` views on `n` assets. The `Ω` matrix is the
  formal home of "how much do we believe this analyst", which is what RM-1 measures.
- **AQR**, *Systematic vs. Discretionary* (2017) — the two are complements with different failure
  modes; the systematic side wins on breadth and consistency, the discretionary side on context and
  on situations with no statistical precedent. Argues for **structural separation**, not fusion.
- **Robeco** (2025), *Seizing fundamental and quant alpha* — an explicit **65/35 quant/fundamental**
  split with **inverse-tracking-error weighting**, i.e. a risk-parity blend of two *independently
  run books*, not two scores on one name.
- **LLM-specific (2025–26)** — `arXiv:2504.14345` and successors translate LLM forecasts into BL
  views and confidences, and report that portfolios from top LLMs beat baselines. ★ Their central
  caveat is the one D-01 §7 was written around: **"each LLM exhibits a distinct and consistent
  investment style"** — a persistent bias that survives every consistency check, exactly D-01's
  RM-2 concern. **A stable style is not skill, and RM-1's agreement metric cannot distinguish
  them** — 5/5 agreement on a systematically biased view looks identical to 5/5 on a correct one.

## 5.3 ★ The honest read of the literature

The blending literature is written for a setting this book does not occupy: **many names, dense
coverage on every signal, a benchmark, and tracking error to spend.** Robeco's 65/35 assumes two
staffed research processes; Grinold–Kahn's `√BR` assumes breadth exists.

**The one architecture built for asymmetric coverage — systematic sourcing plus discretionary
override — is the quantamental gate.** It is also the least mathematically glamorous, which is
probably why it is under-represented in papers and over-represented in actual funds.

---

# 6. ★ THE RECOMMENDATION

```text
   ┌──────────────────────────────────────────────────────────────┐
   │ D-03 QUANT — dense (n=130), calibratable, cheap per name     │
   │   ranks the universe on ẑ·σ̂·√h at h1m                        │
   │   ★ THE ONLY LAYER THAT MAY NOMINATE                         │
   └───────────────────────────┬──────────────────────────────────┘
                               │  nomination (top-1, INV-6)
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ D-01 FUNDAMENTAL — sparse (k≈1), expensive, uncalibrated     │
   │   PASS · FLAG · VETO           ★ MAY ONLY DOWNGRADE (P3)     │
   │   carries RM-1 stability onto the artifact verbatim (RA-20)  │
   └───────────────────────────┬──────────────────────────────────┘
                               │  gated recommendation
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ D-05 RISK — a predicate on (book, candidate)                 │
   │   LEVEL 2 ALERT ── unsuppressible (INV-021)                  │
   │                 ── NEVER blocking (INV-026)                  │
   │   travels BESIDE the recommendation, never inside it         │
   └───────────────────────────┬──────────────────────────────────┘
                               ▼
                    SEAT-1 — the human decides
```

**This ratifies the architecture already in the code** — `signal_engine` scores, `gate.py` vetoes —
but on grounds it has never had. P3 stopped mandating this ordering in August 2026; §4.3 re-derives
it from coverage economics, which is a stronger footing than a constitutional rule that was
withdrawn.

| ID | Rule |
|---|---|
| **CB-14** | ★ **`combined_score` is quant-internal and must be named so.** It blends D-03's model output with **D-02's** `fundamental_composite` — seat 5's computed numbers, never D-01's thesis. The column, the config key and the docstring say **`d02_fundamental_composite`**, so no future reader mistakes an INV-014-legal blend for an illegal one |
| **CB-15** | ★ **The gate's output is `PASS / FLAG / VETO`, never a number**, and never re-enters the score. A gate that returns a magnitude is a blend wearing a gate's name |
| **CB-16** | ★ **A VETO is loud and is recorded with its reason.** It vetoes the *pipeline's* recommendation, never the human (L0 §3.1); an override is journalled (D-11 RC-24), never prevented |
| **CB-17** | ★ **Absence of a thesis is `NO_THESIS`, not `PASS`.** The daily pick always has one (INV-6, AC-1.8); anything else is reported as ungated rather than silently approved — the F2 incidents were both a missing input read as an affirmative one |
| **CB-18** | The three channels are rendered on one artifact with their **reliability classes distinguished** (D-09 §5: fact · computation · judgement). The quant rank is a computation, the thesis a judgement, the risk state a fact |

---

# 7. WHAT WOULD REOPEN THIS

**CB-5 is contingent, and both of its terms are moving.** The conditions for revisiting, in the
order they would have to be met:

| # | Condition | Status |
|---|---|---|
| **1** | ★ **D-01's confidence is calibrated** — a stated `N`, an empirical referent, a Brier or log score against realised outcomes (RA-21, RM-12…14) | ⬜ `not_yet_calibrated (N=3)`. **The hard blocker** — without it there is no `q` and no `Ω` (CB-10) |
| **2** | ★ **`ρ` between the thesis score and the quant score is measured on a common cross-section** | ⬜ unmeasurable at k=1/day. §4.2 shows the answer spans 1.00×–1.41× |
| **3** | **Dense coverage is affordable** — inference cost falls ~10×, or the book grows ~10× | ⬜ 6.3–19 % of NAV today (§4.3) |
| **4** | **D-01 demonstrates it can rank, not only judge** — a verdict that orders two names it was not pointed at | ⬜ never tested; the sampling scheme forbids it |

> ★ **Condition 1 is worth pursuing on its own merits and is nearly free.** Calibration needs no new
> machinery — only that closed theses are scored against outcomes, which D-11's journal already
> records. It is the input a principled merge consumes **and** the strongest anti-overconfidence
> device D-01 has (RA-20/RA-21). **Every month of theses that closes uncalibrated is a month of
> evidence discarded**, and at one actionable pick per day the sample accrues slowly enough that
> starting late is expensive.

---

# 7A. ★ PARAMETER & ASSUMPTION REGISTER

Every number this document's conclusions rest on, with its source and whether it is **measured,
assumed, or unmeasurable today**. A conclusion is only as durable as the parameter it turns on.

## 7A.1 The parameters

| Symbol | Meaning | Owner | Today | Status |
|---|---|---|---|---|
| **`n`** | universe size | D-03 | **130** | measured · **scalable** |
| **`k_cov`** | names D-01 covers per day | D-01 | **1** (+ rotating sample) | ★ **the binding structural parameter** |
| `k_stab` | RM-1 stability runs | D-01 | 3 (AC-1.8) | decided |
| **`IC₀₃`** | quant information coefficient | D-03 | **~0.03 assumed** | ⚠ **never measured** — §7A.4 |
| **`IC₀₁`** | thesis information coefficient | D-01 | — | ⚠ **unmeasurable at `k_cov=1`** |
| **`ρ`** | correlation between the two seats | joint | — | ⚠ **unmeasurable at `k_cov=1`** (CB-3, DN-28) |
| `τ` | alpha decay time constant | D-03 | ~16 d predicted | ⚠ unmeasured (QQ-23) |
| `h` | production horizon | D-03 | 21 d | decided (HorizonSet v1) |
| `N` | sleeve count | D-03 | 5 | decided |
| `σ` | 21-day single-name vol | D-03 §9.1.6a | 8.66 % | measured (universe); ⚠ **not the nominated subset** (QN-7) |
| `E[max z]` | top-pick order statistic | derived | **2.590** at n=130 | derived — Blom |
| decisions/yr | rolls | D-03 §5.8 | 60 | derived (`N=λh`) |
| veto rate | how often the thesis gate fires | D-01/D-12 | — | ⚠ unmeasured (DN-17) |
| confidence calibration | `q`, `Ω` for a Bayesian merge | D-01 | `not_yet_calibrated (N=3)` | ⚠ **the hard blocker** (CB-10) |
| — | **D-05 contributes NO parameter** | D-05 | — | ★ by design — it is a parallel channel (CB-11), so **nothing in D-05 can change this model** |

## 7A.2 ★ Sensitivity — what `n = 500` and `k_cov = 10` actually change

**Universe `n` — the alpha gain is small and sublinear.** `E[max z]` by **Blom's approximation**
`Φ⁻¹((n−0.375)/(n+0.25))` — ⚠ *not* `√(2 ln n)`, which is the crude asymptotic and runs **+20 % high**
at these `n` (3.120 vs 2.590 at n=130):

| `n` | `E[max z]` | gross alpha/position | vs n=130 |
|---:|---:|---:|---:|
| **130** | 2.590 | 67.3 bps | 1.00× |
| 330 | 2.896 | 75.2 bps | 1.12× |
| **500** | **3.023** | **78.6 bps** | **1.17×** |
| 1000 | 3.227 | 83.8 bps | 1.25× |

```text
╔══════════════════════════════════════════════════════════════════╗
║  QUADRUPLING THE UNIVERSE BUYS +17% OF ALPHA. THAT IS NOT WHY    ║
║  YOU WOULD DO IT.                                                ║
║                                                                  ║
║  MDE on IC (t=3, 3 years):    n=130 -> 0.0440                    ║
║                               n=500 -> 0.0224                    ║
║                                                                  ║
║  ★ AT n=130 THE MDE ON YOUR OWN IC IS LARGER THAN THE IC YOU     ║
║  ASSUME (0.03). You cannot establish, in three years, that the   ║
║  quant model has ANY edge at all.                                ║
║                                                                  ║
║  At n=500 the MDE drops below 0.03 and the question becomes      ║
║  answerable. THE UNIVERSE EXPANSION BUYS MEASURABILITY, not      ║
║  alpha — and measurability is what every other decision here     ║
║  is currently starved of.                                        ║
╚══════════════════════════════════════════════════════════════════╝
```

**Coverage `k_cov` — this is the parameter that changes the architecture.**

| `k_cov` | $/yr (k_stab=3) | % of a $142.5 k book | can D-01 **rank**? |
|---:|---:|---:|---|
| **1** | $208 | 0.15 % | ★ **NO** — every covered name has rank 1 |
| **3** | $624 | 0.44 % | **yes** — ranks span 1–3 |
| **10** | **$2,079** | **1.46 %** | yes — ranks span 1–10 |
| 25 | $5,198 | 3.65 % | yes |
| 130 | $27,027 | 18.97 % | yes — and unaffordable |

```text
╔══════════════════════════════════════════════════════════════════╗
║  ★ THE GATE/RANK TRANSITION IS AT k = 2, NOT AT k = n.           ║
║                                                                  ║
║  §4.3 argued D-01 cannot rank because "a signal observed only    ║
║  on the name another signal already selected carries zero        ║
║  ranking information". TRUE — and it is true only at k = 1.      ║
║  Two observations are enough to ORDER two things.                ║
║                                                                  ║
║  §4.3 then priced DENSE coverage (130 names, 19% of NAV) and     ║
║  concluded ranking was economically excluded. That priced the    ║
║  WRONG POINT ON THE CURVE. Ranking within the quant's top-10     ║
║  costs 1.46% of NAV; within the top-3, 0.44%.                    ║
╚══════════════════════════════════════════════════════════════════╝
```

**And at `k_cov ≥ 2` the §4.2 uplift stops being theoretical — but at *partial-coverage* size.**

> ⚠ **Corrected (external review).** The v0.4.0 table applied the **full-coverage** Grinold limit
> (`×√2`, both signals on the whole cross-section) to a **partial-coverage** design. CB-20 already
> scoped the output correctly — *re-ranking within the covered set* — and then the table priced it
> with the universe formula. **They contradicted.**

Correctly scoped: re-rank D-03's top-`k` at `n = 500`, `IC₀₃ = IC₀₁ = 0.03`, `ρ = 0`
(200 k simulations):

| `k_cov` | `E[max composite]` | alpha | **uplift** | fraction of the √2 limit |
|---:|---:|---:|---:|---:|
| 1 | — | 78.9 bps | **0 %** | 0.00 |
| **3** | 2.582 | 94.9 bps | **+20.2 %** | **0.49** |
| 5 | 2.712 | 99.7 bps | +26.3 % | 0.64 |
| **10** | 2.843 | 104.4 bps | **+32.4 %** | 0.78 |
| 25 | 2.947 | 108.3 bps | +37.2 % | 0.90 |

★ **It converges slowly, and the reason is worth stating: the quant's top names are near-identical
by construction.** The top-3 differ by **12 bps of expected alpha against 866 bps of noise**, so
re-ranking them is an intrinsically low-information operation. CB-25 survives — at roughly **half**
the size v0.4.0 advertised.

**`ρ` becomes measurable — but far less precisely than v0.4.0 claimed**, because the covered set is
**range-restricted**: D-03's top-3 have `sd(z) ≈ 0.20` against an unrestricted 1.0. Thorndike Case II:

| `k_cov` | `sd(z)` covered | `S/s` | naive SE | **corrected SE** | detects |
|---:|---:|---:|---:|---:|---|
| 3 | 0.203 | 4.93 | 0.036 | **0.179** | `ρ > 0.36` |
| 10 | 0.300 | 3.33 | 0.020 | **0.066** | `ρ > 0.13` |
| 25 | 0.357 | 2.80 | 0.013 | 0.035 | `ρ > 0.07` |

★ **v0.4.0's "`k=10` detects `ρ > 0.04`" was optimistic by ~3.5×** — and it is **the same range-restriction
error DN-28 and CB-3 already establish for this exact quantity**, made a second time.

| ID | Rule |
|---|---|
| **CB-19** | ★ **CB-5 ("D-01 is a gate, not a ranker") is CONDITIONAL ON `k_cov = 1` and must always be cited with that condition.** It is a statement about the *sampling scheme*, not about D-01's nature. **At `k_cov ≥ 2` it does not hold**, and the §4.2 uplift becomes reachable |
| **CB-20** | ★ **The relevant D-01 output at `k_cov ≥ 2` is a re-ranking *within the covered set*, not a universe ranking.** D-01 re-orders the quant's top-`k`; it never nominates a name the quant did not surface. **P3 and CB-6 are untouched** — re-ordering within a nominated set is not promotion from outside it |
| **CB-21** | ★ **Universe expansion is a MEASURABILITY investment, not an alpha investment.** `n: 130→500` buys +17 % alpha and **halves the MDE on `IC₀₃`**, taking it from *above* the assumed IC to *below* it. **The second effect is the one that matters**, because every open question in this document is blocked on measurement rather than on return |
| **CB-28** | ★ **Covered and uncovered names are ranked SEPARATELY and never merged into one sort.** A composite score on the covered set and a quant-only score on the rest have **different variances** — merging them is exactly the §4.1 asymmetry CB-1/CB-2 forbid, reintroduced by the fix. CB-20's within-set scoping is what avoids it, **and it is an implementation constraint, not only a description** |
| **CB-29** | ★★ **`k_cov` buys a CAPABILITY; the stratified sample buys a MEASUREMENT. They are two purchases and D-01 needs two sampling policies.** Covering D-03's top-3 spans almost no rank variance, so **P1 does not deliver a measurable `ρ` — F3 is its precondition.** Priced and sequenced as one item, someone buys P1 and wonders why `ρ` is still unknown |
| **CB-22** | ★ **D-05 contributes no parameter to this model and cannot.** It is a predicate on `(book, candidate)` with no authority (CB-11/12). **A future change to D-05 can never require this document to be re-derived** — which is worth stating so nobody looks for a D-05 sensitivity that does not exist |

## 7A.3 What survives a parameter change, and what does not

| Conclusion | survives `n=500`? | survives `k_cov=10`? | why |
|---|---|---|---|
| §3 the type argument | ✅ | ✅ | D-05 is still a book predicate; verdicts are still ordinal |
| §4.1 imputation bias | ✅ **worse** | ✅ | a covered name is still ~2× likelier to be argmax; more uncovered names to crowd out |
| CB-6 gate direction (P3) | ✅ | ✅ | monotonicity is constitutional, not empirical |
| §5.0 zero-parameter rule | ✅ | ◐ **weakens** | with `ρ` and both ICs *measured*, a fitted weight stops being fitted to noise |
| **CB-5 gate-not-ranker** | ✅ | ❌ **falls** | CB-19 |
| **§4.3 the cost argument** | ✅ | ❌ **falls** | it priced `k=130`, not `k=10` |
| CB-10 BL blocked on calibration | ✅ | ✅ | ★ **coverage does not calibrate anything** — §7B.1 |

## 7A.4 ⚠ The assumption nobody has tested

**`IC₀₃ = 0.03` is an assumption, not a measurement.** It is the central case of D-03 §5.3a's decay
table and it propagates into every number in §4.2, §7A.2, and D-12 §6.

| ID | Rule |
|---|---|
| **CB-23** | ★★ **`IC₀₃` is an ASSUMPTION, and it is load-bearing for four conclusions across three documents.** At `n = 130` the 3-year MDE on IC is **0.0440 — larger than the 0.03 assumed** — so the system's foundational parameter is **currently unfalsifiable.** It propagates into: §4.2's uplift · D-12 §6's gate economics · D-03's minimum viable position size · ★ **and D-03's turnover penalty `δ`, hence the emergent holding period, hence QQ-21's whole sleeve architecture** |
| **CB-30** | ★★ **THE FREEZE BOUNDARY. `δ_floor = rt/(IC₀₃·σ)`, and it must stay below `E[max z] = 2.590` or no challenger can ever clear the hurdle and the portfolio never trades.** Solving: **`IC_critical = rt/(E[max]·σ) = 0.0223`.** The assumed 0.030 is only **26 % above it** |

```text
╔══════════════════════════════════════════════════════════════════╗
║   IC₀₃      β        δ_floor     outcome                         ║
║   0.050   0.00433     1.15       trades freely                   ║
║   0.030   0.00260     1.92       the QQ-21 resolution            ║
║  ★0.0223  0.00193     2.59       ★ THRESHOLD                     ║
║   0.020   0.00173     2.89       ★ NEVER TRADES                  ║
║   0.015   0.00130     3.85       ★ NEVER TRADES                  ║
║                                                                  ║
║  This is §5.8.7's ladder kill arriving from the PARAMETER axis   ║
║  instead of the position-size axis — and QQ-21's resolution      ║
║  (N=5, δ=1.92, ~40-day emergent hold) is CONDITIONAL on an       ║
║  unmeasured number sitting 26% above a cliff.                    ║
║                                                                  ║
║  ★ THAT is why universe expansion comes first. It is not "a      ║
║  measurability investment" in the abstract — it is the only way  ║
║  to falsify the parameter the SLEEVE ARCHITECTURE rests on.      ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 7B. ★ IMPROVING D-12'S RELIABILITY — the investment menu

The user framing: money and compute are constrained now and can be scaled next year. So the menu is
sorted by **what it unblocks per dollar**, not by size.

## 7B.1 ★ The free levers — and they are the binding ones

| # | Lever | Cost | What it unblocks | Clock |
|---|---|---|---|---|
| ~~**F0**~~ | ✅ **DONE — QA-107: capital base read from D-11's `book_state.nav_base`**; ★ and **δ re-based on the mandate (QA-110), which dissolves the dependency** — the mandate bound binds at every book size | **$0** | ★ **everything below is priced against it.** It swings `δ` by **7×**, decides whether the freeze cliff exists at all, and decides whether the holding period is 22 days or 2 (D-03 §5.8.6a) | immediate |
| ~~**F1**~~ | ✅ **ADOPTED — RA-59.** Calibrate D-01's confidence — score closed theses against outcomes | **$0** — D-11's journal already records what is needed | ★ **CB-10, the single hard blocker on a Bayesian merge.** Also RA-21's anti-overconfidence device | years; **starts only when you start** |
| **F2** | ★ **Record vetoed candidates** (DN-19) and mark them on the same horizon | ~$0 | makes the gate's value **measurable at all**; without it the gate is permanently unfalsifiable | 7.8 yr to 5 bps |
| ~~**F3**~~ | ✅ **ADOPTED — RA-57**, and promoted to a *separate sampling policy* rather than a tweak | $0 | ★ makes `ρ` estimable **without raising `k_cov`** — sidesteps the range restriction | 1–2 yr |
| **F4** | Report the veto rate every run (DN-17) | ~$0 | a rate near 0 % or 100 % is a **structural** finding needing no power | immediate |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE BINDING CONSTRAINTS ON D-12 ARE NOT MONEY.                  ║
║                                                                  ║
║  The hard blocker (calibration) costs nothing but TIME, and its  ║
║  clock does not start until the recording does. Every month of   ║
║  theses that closes uncalibrated is evidence thrown away, and    ║
║  at ~250 decisions/year the sample accrues slowly enough that    ║
║  starting late is the expensive mistake — not spending late.     ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **F3 is the highest-leverage item on this page.** It gets `ρ` — the parameter §4.2 shows the whole
combination question turns on — **for zero marginal cost**, by changing *which* names the existing
rotating sample covers rather than *how many*.

## 7B.2 The paid levers, priced

| # | Lever | Cost | What it unblocks |
|---|---|---|---|
| ~~**P1**~~ | ✅ **ADOPTED — RA-55, `k_cov = 3`** | **$624/yr** (0.44 % NAV) | ★ **crosses the rank/gate boundary** (CB-19). `ρ` measurable at SE 0.036. The §4.2 uplift becomes reachable |
| **P2** | ★ **PLANNED — RA-56, `k_cov = 10`.** Trigger: `n = 500` live **and** `ρ` estimated once | +$1,455/yr (1.46 % total) | `ρ` at SE 0.020; re-ranking over a set wide enough to matter |
| **P3** | ★ **ADOPTED as target — QA-113, `n = 500`** | ETL + compute (one-off) | ★ **halves the MDE on `IC₀₃`** — the only lever that makes the system's foundational parameter measurable. +17 % alpha as a side effect |
| ~~**P4**~~ | ⚠ **WITHDRAWN — D-01 RA-61.** `k_stab: 3→5` measures the **decoder**, not the analysis: no `temperature` is set, so RM-1 is quantifying **self-inflicted** variance that vanishes at temperature 0. ★ **Replaced by a free change — keep `k_stab = 3` and perturb the INPUT** (option order, evidence order, paraphrase) rather than resampling. Same cost, and it measures a property of the analysis | **$0** |
| **P5** | Arrival-quote capture | days of wiring, then time | QQ-20, QQ-22, and D-03's anchor option (B) |

## 7B.3 ★ The ordering, and the reasoning

```text
   NOW (free):        F1 calibration  ──►  F2 counterfactuals  ──►  F3 stratify
                      because their CLOCKS are the constraint, not their cost

   NEXT (measure):    P3  n 130 -> 500       ★ FIRST of the paid levers
                      the ONLY lever that can falsify IC_03, and IC_03
                      decides whether the sleeve architecture trades AT ALL
                      (CB-30). It also gates the INTERPRETATION of anything
                      P1 would buy.

   THEN (capability): P1  k_cov 1 -> 3       $624/yr   + F3 as its precondition
                      P2  k_cov 3 -> 10      $2,079/yr total

   ONLY AFTER:        revisit CB-5 with rho and both ICs MEASURED.
                      §5.0's zero-parameter argument weakens exactly when
                      the parameters stop being guesses — and not before.
```

| ID | Rule |
|---|---|
| **CB-31** | ★★ **F0 precedes everything, including the other free levers.** `$20,000` is a `backtester.py` literal and `$142,500` is an *illustrative value in an F4 contract example* — **neither is measured**, and this document priced every coverage percentage against the second while D-03 derived `δ` from the first. ★ **The binding constraint on D-12 was never money; it is that nobody knows how much money there is** |
| **CB-32** | ★ **CB-30's cliff is only half the danger.** `δ` is bounded **below** as well — too small and the holding period collapses to ~2 days, violating **M-4**. The failure modes are **opposite and both live**: small book ⇒ freeze, large book ⇒ churn. **A lever that moves `δ` must be checked against both bounds** (D-03 QA-105) |
| **CB-24** | ★ **Free levers before paid ones, because their binding constraint is elapsed time, not money.** Calibration and counterfactual recording have multi-year clocks that **only start when the recording starts**. Spending on coverage first buys a sharper measurement of a question you still cannot answer |
| **CB-25** | ★ **`k_cov: 1 → 3` is the highest-value *capability* change** at 0.44 % of NAV — the only item that alters what D-01 structurally **is**. ⚠ **But `n: 130 → 500` comes first** *(revised, external review)*: `IC₀₃` gates the interpretation of everything `k_cov` buys, **including whether the portfolio trades at all** (CB-30). **P1 gives a capability; P3 tells you whether the capability is worth having** |
| **CB-33** | ★★ **A metric that would vanish if a configuration flag changed is measuring the configuration, not the domain.** RM-1's stability is a property of an **unset `temperature`**; at 0 it reports ~1.0 and says nothing. ★ **The test for whether a measurement is worth buying: name the change that would make it read differently. If that change is a setting rather than a fact about the world, buy the perturbation form instead** (D-01 RA-61/62) |
| **CB-26** | ★ **A fitted combination weight remains forbidden until `ρ`, `IC₀₃` and `IC₀₁` are all measured** (CB-3, CB-23). §5.0's argument is about **estimated** parameters; it does not forbid weights that are *known*. **Coverage alone does not lift the ban — calibration and measurement do** |
| **CB-27** | ★ **Re-derive this document, not just its numbers, when `k_cov` crosses 2 or `n` crosses ~300.** §7A.3 lists which conclusions fall: **CB-5 and §4.3 do not survive `k_cov ≥ 2`**, and a reader who updates only the tables will keep a conclusion whose premise has gone |

## 7B.4 Tests that raise confidence without raising spend

| Test | What it catches | Tier |
|---|---|---|
| ★ **Null-variance test** on any composite (CB-2) | §4.1's 2× selection bias, **before** it reaches production | property |
| Gate-algebra laws over `V³` (DN-6) | an upgrade path becoming expressible | property |
| `roster_declared == roster_reported` (DN-11) | a silently absent gate | contract |
| ★ **Counterfactual completeness** — every veto has an outcome row | the gate quietly becoming unfalsifiable again | contract |
| `ρ(rank, σ̂)` (QA-88) | the ranker degenerating into a volatility screen | metric |
| Per-candidate deferral count (DN-29) | liveness starvation the veto rate cannot see | metric |

★ **The first row is the one to build first.** It is a pure property test, it needs no data, and it
catches the one defect in this document that is **live in production code today** —
`signal_engine.combined_score`'s `z = 0` imputation (§4.1).

# 8. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QB-1** | ~~Does FLAG change anything downstream?~~ | ✅ **CLOSED** — `L1-decision.md` **DN-8**. FLAG leaves the verdict unchanged (it is the identity in the algebra) and **must therefore change the artifact**. A severity that alters nothing anywhere trains the reader to skip it |
| **QB-2** | ~~Can the h1w timing leg and the thesis gate deadlock?~~ | ✅ **CLOSED — the question presupposed a conflict the algebra does not admit.** Both are meets into the same chain, and meet is commutative and associative, so no precedence rule is needed (`L1-decision.md` §5.7, DN-15) |
| **QB-3** | What is the **veto rate**, and what is too high? | A gate that never fires is decoration; one that fires half the time means the ranker and the analyst disagree systematically, which is a finding about `ρ` (§4.2) arriving through the back door — **and the cheapest available estimate of it** |
| **QB-4** | Does a **VETO suppress the day's recommendation entirely**, or surface the next-ranked name? | Surfacing #2 quietly turns the gate into a ranker over the top-`m`, which §4.3 says it cannot be. Suppression respects INV-6 more cleanly |
| **QB-5** | ~~Where does the combined step live?~~ | ✅ **CLOSED — a new domain, `D-12 Decision`, SEAT-5** (L0 v0.17.0, `L1-decision.md`). The finding stands: every existing domain was the wrong home for a stated reason, which is what a missing domain looks like |
| **QB-6** | Should D-01 be shown the quant **rank** before authoring? | Currently no, and **INV-014 forbids the reverse direction only**. Showing the rank risks anchoring (D-01 §7); withholding it means the thesis cannot address *why this name now*. Genuinely open |

---

# 9. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` **§1.6**, §3.1, **INV-014**, **INV-021**, **INV-026**, INV-6, M-2 | the deferred question this resolves; the authority levels that force §4.5 |
| `L1-fundamental-analysis.md` **CT-1.1**, RA-20, **RA-21**, RM-1, RM-12…14, §7 | `verdict_stability` → `Ω`; the calibration gap that blocks CB-10 |
| `L1-quantitative-analysis.md` **QA-47** (arbitration), QA-58, §5.3a (decay), **QA-43** (effective breadth), §5.8 | the internal precedent §6 mirrors; the prior `Π`; the cost budget §4.3 compares against |
| `L1-risk-management.md` **§1.4**, RK-2, RK-18 | *maximum voice, zero authority* — the reason D-05 is a third channel |
| `L4-coding-standards.md` **PD-1, PD-2**, §5 EH-7 | §4.1's imputation defect; `Unmeasured` as the alternative to z=0 |
| `sdd/specs/constitution.md` **P3** (as amended 2026-08-13), P2, P5 | monotonicity survives; the *ordering* does not — hence this document |
| `sdd/specs/F2_portfolio_and_delivery/spec.md` · `pipeline/discipline/gate.py` · `pipeline/core/signal_engine.py` | the two existing mechanisms, and the ~420 LOC this unblocks *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |

**Sources consulted (2026-08-18):**
[Robeco — Fundamental Law of Active Management](https://www.robeco.com/en-int/insights/2018/04/fundamental-law-of-active-management-shows-way-to-higher-information-ratio) ·
[The Fundamental Law of Active Management: Redux](https://www.sciencedirect.com/science/article/pii/S0927539817300543) ·
[Qian, Hua & Sorensen — Information Horizon, Portfolio Turnover, and Optimal Alpha Models](http://gyanresearch.wdfiles.com/local--files/alpha/JPM_FA_07_Qian.pdf) ·
[Robeco — Seizing fundamental and quant alpha (2025)](https://www.robeco.com/files/docm/docu-20250624-seizing-quant-and-fundamental-alpha-in-developed-equity-markets-hksg.pdf) ·
[AQR — Systematic vs. Discretionary (3Q17)](https://www.aqr.com/-/media/AQR/Documents/Insights/Alternative-Thinking/AQR-Alternative-Thinking--3Q17.pdf) ·
[View fusion and a Bayesian interpretation of Black-Litterman](https://arxiv.org/pdf/2301.13594) ·
[LLM-Enhanced Black-Litterman Portfolio Optimization (arXiv:2504.14345)](https://arxiv.org/abs/2504.14345) ·
[Multi-LLM sentiment aggregation with Black-Litterman](https://businessperspectives.org/index.php/journals/investment-management-and-financial-innovations/issue-493/enhancing-portfolio-optimization-with-multi-llm-sentiment-aggregation-a-black-litterman-integration-approach)
