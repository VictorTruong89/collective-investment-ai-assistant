# L1: Domain Specification — Quantitative Analysis (D-03)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-03 · **Seat:** SEAT-3
> **Path:** `src/quant/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L1-feature-engineering.md`](L1-feature-engineering.md) (D-02) ·
> [`L1-data-engine.md`](L1-data-engine.md) (D-07)
> **Prior art:** `pipeline/ohlcv/backtest/**`, `pipeline/ohlcv/dataset/label_builder.py`,
> `pipeline/buffett/signals/**`, `pipeline/core/signal_engine.py`,
> `constitution.md` INV-1/INV-2/INV-3, P3, `F0` §12 **D-18**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.11.0 | 2026-08-27 | Victor | ★★★ **QA-125/126 — D-03 never nominates an untradeable name.** ⚠ *Measured:* `AVB` and `EQR` delisted mid-August and left the ranking **only because they printed no bar on the as-of date** — *a side effect doing a guard's job*. ★ §6A cannot cover it: *"has any name stopped trading?"* is **current-state** and the calendar gate is **window-scoped**, so a three-week feed is `UNCHECKED` against every real window (AB-15). `CT-3.4` gains `excluded[]`; tradeability is **supplied**, not fetched. AC-3.32. |
| 1.10.0 | 2026-08-27 | Victor | ★★ **Effective breadth is measured — the last `NOT_EVALUATED` gate.** `breadth_gate` has declared `breadth.residual_correlation.v1` since B4 and **nothing computed it**. ⚠⚠ New **QA-124**: QA-43's *residual* correlation is **`−1/(n−1)` by construction** and returns the same value at `ρ_true = 0.00` and `0.35` — *a statistic that cannot tell those apart measures nothing*. The gate is fed the **raw** correlation (G&K's independent bets); the residual is reported as a diagnostic. **QA-43 is not amended** — the choice is registered as **QQ-14**. ★ The measure also demonstrates QA-44: at `ρ = 0.35`, **488 extra names buy a third of a bet**. AC-3.31. |
| 1.9.0 | 2026-08-25 | Victor | ★★ **§7's evaluation protocol BUILT** — the thing D-04's `promote()` demanded and could not be given (MT-17/MT-19). `src/quant/{backtest,metrics,gates}` with `BacktestSpec`/`BacktestResult` (CT-3.2), derived purge/embargo (QA-18), rank IC with **effective N and a corrected SE** (QA-4), and gates that report `NOT_EVALUATED` rather than passing (QA-17). ★ **`mde.rank_ic.v1` reproduces §5.3b's published table to four decimals** — `n=130, T=1915, h=21, t*=3 ⇒ 0.0277`. ⚠ **QA-123**: the flat commission is **9.95, measured over 137 real orders** — not the `10.00` asserted in the legacy backtester, and QA-48's own defect shape. Three MethodEntries added (QA-20). |
| 2.9.0 | 2026-08-18 | Victor | ⚠ **QQ-6 was still listed as open two versions after D-12 answered it.** Closed: `combined_score` is quant-internal and stays here; the gate is D-12's. *An open-questions table is a claim about the present, and a stale row there is a false statement the audit script does not yet catch.* |
| 2.8.0 | 2026-08-18 | Victor | ⚠★ **Cross-spec audit: D-03 had NO contract for the thing it produces.** CT-3.1/3.2/3.3 covered configuration, evaluation and provenance; **the daily nomination D-12 consumes was undeclared.** New **CT-3.4 Nomination** + QA-119…122: `ranked_quantity` is the denormalised return **with `z` beside it** (publishing only `z` reinvites the low-vol tilt QA-58 removes); `nominating_horizon` is always `h1m` and `h1q` may not appear at all; `universe_n` and `model_artifact_id` are required; and ★ **`candidates` is a list, because a contract emitting only rank 1 makes `k_cov ≥ 2` unimplementable.** |
| 2.7.0 | 2026-08-18 | Victor | ⚠ **`QA-6` defined — cited by `AC-3.5` and never written.** A multi-horizon design is adopted only against a per-horizon single-task baseline on identical folds, costs and universe: **parameter sharing is a hypothesis, not a free lunch.** Closes the last dangling rule reference in the design tier. |
| 2.6.0 | 2026-08-18 | Victor | ⚠ **Audit finding B — dangling references closed.** **QA-27 was cited by four specs (D-04 MT-38, D-06, D-09, §9.3) and had never been written**; it is now defined — a model-produced stop or target is **immutable downstream**, narrated by D-01 and rendered by D-09, never altered or recomputed. **QA-26** likewise defined (the head set is a versioned bundle property). §12's roll-up ranges corrected to stop claiming IDs that do not exist. Parent bumped to L0 v0.18.0 (reconciled: D-03 has no D-12 seam; module tree governed by L4 §18 CA-1…9). |
| 2.5.0 | 2026-08-18 | Victor | ⚠ **Audit finding A fixed — supersession is now explicit.** `QA-87` was defined **three times** and `QA-77/79/80` twice each with **nothing indicating which bound**; a top-down reader met QA-79 as *downgraded → re-promoted → restored*. Superseded rows are now struck and pointed at their replacement; binding rows are marked **✅ binding**. New **§8.4**: **QA-116** (one binding definition per ID), **QA-117** (a rewrite carries its rule definitions forward — the `DN-16/17/18` defect), **QA-118** (accretion is deliberate, so supersession must be explicit or it becomes ambiguity). |
| 2.4.0 | 2026-08-18 | Victor | ⚠ **Consistency audit — a live contradiction fixed.** After QA-110 re-based `δ` to **2.19**, §5.8.5a still printed *"← the current δ"* against **1.92** and §5.8.4 still instructed *"Set δ = 1.92 now"*. Both **superseded in place** rather than left for a reader to reconcile. ★ **§5.8.5b's `τ ≈ 16` prediction is superseded in PURPOSE too**: it asked what `τ` makes the emergent hold match the training horizon *given a cost-derived δ* — a premise QA-110 removed, since the hold is now 30 days by construction and **δ is what gets recomputed**. The measurement survives; the consistency claim does not. |
| 2.3.1 | 2026-08-23 | Victor | ⚠ **QA-121 clarified for the pre-model milestone.** `model_artifact_id` is required and **L3 B3 has no model** — the walking skeleton ranks on one declared deterministic rule. The field identifies **whatever produced the ranking**, hashed; `null` stays forbidden, because the rule is re-runnability and a hashed rule satisfies it. No contract or AC change. |
| 2.3.0 | 2026-08-18 | Victor | ⚠ **QA-114 — `backtester.py:107` is deliberately NOT fixed.** This spec set builds `src/quant/`; patching a literal in a tree scheduled for deletion spends effort where the rule will not be enforced. **The finding is retained as the evidence for QA-63/QA-107 and the fix lands in the new backtest only** — same disposition as `L1-orchestration.md` §1.5. **QA-115**: the new backtest **records** its capital base in the `BacktestResult`, not only in the spec — the defect survived because the number appeared in neither input nor output. Cascaded to `L4` §1.5. |
| 2.2.0 | 2026-08-18 | Victor | ✅ **QA-63 RESOLVED and δ RE-BASED (§5.8.6b), closing QQ-24.** The capital base is **read from D-11's `book_state.nav_base`** (QA-107), RESP excluded (QA-108), and a missing book **fails** rather than falling back to a constant (QA-109). ★ **δ is now set by the MANDATE — `δ = E[max z]·(1−e^(−T_min/τ))` with `T_min = 30 d` (M-4) — and cost is a floor that is checked** (QA-110/111). This **dissolves the capital-base dependency**: the mandate bound binds at every book size tested (by 8× at $142.5k), so δ no longer moves with the book, and 30-day holds hold at any size. **QA-112** flags the residual danger — at `τ ≤ 10` the required δ reaches 2.46 against a 2.59 ceiling, and **universe expansion (QA-113, `n = 500`) is what makes it survivable** by lifting the ceiling to 3.02. |
| 2.1.0 | 2026-08-18 | Victor | ★★ **§5.8.6a — `δ` has a LOWER bound too, and commission cannot set it at any real book size.** From an external-review catch that D-03 and L2 were using **two different capital bases ($20k literal vs $142.5k contract *example* — neither measured), swinging δ by 7×**. §5.8.5 stated only the freeze bound; the churn bound is `δ ≥ E[max]·(1−e^(−t/τ))` = **1.893 at 21 d, 2.193 at M-4's 30 d** — so **the current δ = 1.92 fails M-4 even at $20k**. Solving for the position size that lands in the window gives **$2,972–$3,511**, i.e. a book of ~$15–17.5k at N=5; at $142.5k you would need **40 sleeves**, contradicting M-2. ★ **A flat fee vanishes as a fraction of a growing position, so §5.8's whole δ derivation holds only in a narrow band around the backtest literal — a coincidence, not a design.** §5.8.5b's `τ ≈ 15.7` consistency result is an artifact of the same literal. **QA-102** (δ from the mandate, cost as a floor), **QA-103** (proportional cost, not flat), **QA-104** (state the capital base), **QA-105** (`N` cuts both ways), **QA-106** + **QQ-24** (QQ-21 re-opened). |
| 2.0.0 | 2026-08-18 | Victor | ⚠ **Roll is confirmed ORDINALLY and FALSIFIED QUANTITATIVELY, and my v1.9.0 re-promotion of QA-79/80 is REVERSED.** The parameter-free magnitude test (`effect = −0.878·s²/σ_o`, one-sided) fits at **slope −3.922 — 4.47× too steep** — so bounce explains ~1/5 of the effect; implied spreads are 39–43 bps against Corwin–Schultz 5–21 bps. The `s²/σ_o` re-sort does **not** close the quintile-3 break either. ★ **QA-87's closure survives regardless** (QA-98: bounce or staleness, both mechanical and unharvestable at −17.5 bps against ~20 bps round-trip). ★★ **QA-79/80 re-downgraded**: the label-noise consequence is **0.006–0.06 % sd inflation**, 4–28× below the 0.24 % deviation v1.6.0 downgraded on — **and it holds at the implied spread too, so the pushback survives its own mechanism failing**. New **QA-97** (staleness carries the residual), **QA-98** (the distinction has no decision attached), **QA-99** (always report the parameter-free test beside an ordinal one — a correlation is not a mechanism), **QA-100** (file a finding at the strength of its consequence, not its interest), **QA-101** (§5.9.2's hedge replaced by ~0.02 %). |
| 1.9.0 | 2026-08-18 | Victor | ★★ **The §5.9.1i gap-reversal is MECHANICAL — Roll (1984) bid-ask bounce — and the mechanism moves the finding to a different rule.** Hypothesis from external review, confirmed on three tests over existing data with Corwin–Schultz spreads: normalising the gap leaves the gradient intact (so the QA-34 conditioning confound was real but not the driver); the 2×2 vol×spread double sort gives **`corr(spread/σ, effect) = +0.895`**; and a direct sort on `spread/σ` runs **−1.10 bps (t −0.44) → −17.50 bps (t −9.25)**. ★ **QA-87 closes confirmed** (mechanical, untradable), and ★ **QA-79/80 are RE-PROMOTED**, reversing v1.6.0 — an open-anchored label carries negatively-autocorrelated noise scaling with `spread/σ`, which is live today and which the variance ratio is structurally blind to. **QA-83a narrowed** per the review: the variance identity consumes *total* covariances, so `1.0006` stands and the retraction must not over-propagate. Two self-corrections: `corr(σ, spread) = +0.112` (positive, not inverse), and my "the confound strengthens the reading" argument assumed the wrong mechanism. New **QA-95** (`spread/σ` is the label-quality axis), **QA-96** (report Roll beside Corwin–Schultz). |
| 1.8.0 | 2026-08-18 | Victor | ★★ **QA-87 CLOSED by measurement, in the opposite direction to what either party predicted.** The reviewing agent's insight — that a *conditional* test is **better** powered than the unconditional one, because a within-date difference cancels the market factor that clustering penalises — is correct, and Berkman's dependent variable (`open→close`) was **already in the daily bar**. Run on **130 tickers × 2,917 dates**: four attention proxies give **four nulls at MDE 2.7–4.4 bps** against a 5–10 bps hypothesis, and the mechanism test (`open_position`, panel mean **0.4992**) shows the open does **not** sit high in the range. ★ **But the SIGNED gap test fires** — −7.59 bps, `t = −3.08`, **monotone across all ten deciles** — which **forces a caveat on §5.9.1c** (**QA-83a**): `ρ_od ≈ 0` is true *unconditionally* and false *within-date*. ★★ **The decisive result: the gap-reversal is absent in the high-volatility quartile the ranker selects into** (+1.5 bps, t=+0.39) and strongest in the calmest (−21.1 bps, t=−5.63) — so **the adverse selection runs in the system's favour**. Weakening post-2021 (t drops 3.29→1.39). New **QA-92** (condition the existing panel; never wait for the system to generate a sample), **QA-93** (within-date sort is the default form), **QA-94** (lag the proxy). |
| 1.7.0 | 2026-08-18 | Victor | ★ **v1.6.0's load-bearing sentence retracted — "170 bps is 40× (A)'s cost" compared a DISPERSION to a MEAN**, the third units error of its exact kind here (after QQ-16 and D-12 §6.2). Costed properly via EIV attenuation the mismatch is **2.46 bps against (A)'s 4.2–5.7**, so **the magnitudes favour neither** (§5.9.1f). **QA-77 restated on grounds that are not arithmetic**: correctness (a pre-decision fill is execution look-ahead — a defect at any magnitude) plus **QA-72 anchor parity — `open` is the only anchor with 11.5 years of history and the backtest and production anchors may not differ**. **QA-89** makes (A)'s exit a computable session count. The drift measurement is now **clustered on date** (measured `ρ̄ = 0.285`, `n_eff ≈ 1,060`) with its **MDE stated per QA-33** — 10.0 bps against a 5–10 bps hypothesis, so the bias is **undetermined, not a "coin flip"**; detecting 5 bps needs **7.8 years**. The `+0.036` reversal statistic is **withdrawn — wrong pair**. New **QA-90** (same-date observations are not independent), **QA-91** (ex-dividend adjustment convention); **QA-87** strengthened — `ρ_od ≈ 0` is *not* evidence against a conditional effect. |
| 1.6.0 | 2026-08-18 | Victor | ★ **§5.9.1c/d/e — three questions settled by MEASUREMENT rather than argument.** v1.5.0's simulation of `sd(oo)/sd(cc)` was worthless (iid legs ⇒ the ratio is *identically* 1.000; it confirmed its own assumption — **QA-83**). Measured on **130 tickers × 371,840 rows**: `ρ_od = −0.002`, ratio **1.0006**, max liquidity-decile deviation **0.24 %** — so **QA-79/80 are downgraded to regime guards**. Measured on **1,952 intraday sessions**: the 9:30→10:00 drift is **−4.4 bps, CI [−11.9, +3.2]** — *not significant*, so the bias argument for the anchor is **a wash both ways**; what decides it is the **170 bps label/fill dispersion**, 40× (A)'s 4.2–5.7 bps cost (**QA-77 restated**). ★ **New blocker: `adj_open` does not exist in the panel** (QA-84/85). Plus **QA-86** sleeve clock, **QA-87** adverse selection unresolved, **QA-88** `ρ(rank, σ̂)` volatility-screen diagnostic. |
| 1.5.0 | 2026-08-18 | Victor | **External review incorporated — one retraction, one new defect, two refinements.** ★ **§5.8.5's table was built on two constants this document had already superseded** (`2.8σ`→`2.600σ`, `δ=1.23`→`1.92`): the correct form is `t > τ·ln(2.60/(2.60−δ)) = 1.341·τ`, so at `τ=30` the emergent hold is **~40 d against a 21 d training horizon — the exact divergence QA-66 calls a defect**. Recast as a falsifiable prediction: **the two are consistent only at `τ ≈ 16 d`** (§5.8.5b), with **QQ-23** noting the agreement with §5.3b is not independent. ★ **§5.9.1a — QA-74's fill anchor is a look-ahead**: you cannot fill at a price that printed 30 minutes before the decision. **QA-74 superseded by QA-76/77/78**; target is the arrival price (which makes §5.9 and QQ-22 the same problem), interim is `open(T+1)`. ★ **§5.9.1c — the QA-58 normalisation concern is real but ~0.1 % at h=21** (simulated); what survives is **liquidity-correlated heterogeneity**, hence QA-79/80. Plus **QA-81** (panel-wide adjustment invariant) and **QA-82** (dual-anchor cycle to preserve comparability). §5.8.7's kill margin widened from 1.6× to **≈5×**. |
| 1.4.0 | 2026-08-18 | Victor | **§5.9 — the decision anchor moves to the open** (QA-71…QA-75), closing `L1-orchestration.md` **QO-7**. Labels become `open(T+h)/open(T) − 1` because D-08 §5A takes the decision at the day-T open, and **INV-4 forbids the two anchors differing**. §5.9.2 records the cost: the `open` column has **never been split-adjusted in anger**, and **every historical IC, fold and tuning result becomes non-comparable**. |
| 1.3.0 | 2026-08-17 | Victor | **Three findings from checking whether D-11 unblocks QQ-20 — it does not.** **(1) ★ QQ-20 is a DATA-CAPTURE problem, not a spec problem.** Slippage is *paired* — `(fill − arrival)/arrival` — and a broker export gives only the fill. The BMO InvestorLine export carries `Transaction **Date**`, not a timestamp (**V-30**), so it is **not retrospectively recoverable at all**. **QA-69/QA-70**: capture the arrival quote at submission, starting **now**, and keep the retrospective and forward logs as separate segments with separate quality. Arrival-quote capture is worth a **≈44× sample reduction** (≈3 months vs ≈13 years). **QQ-22.** **(2) ★ `δ` is far less blocked than v1.2.0 claimed** — `rt` has a **known floor (commission)**, exact once QA-63 fixes capital, and QQ-20 can only push `δ` **up**. **`δ_floor = 1.92` at $20 k / N=5 and is settable today** (1,900× the current `0.0`); it supersedes `1.23`, which came from the retracted 32 bps estimate. **(3) ★ An independent kill of the 21-bucket ladder** — at N=21, `δ_floor = 8.08` against an achievable spread of `E[max−min] = 5.20σ`, so **no challenger could ever clear the hurdle and the portfolio would never trade**. Two independent derivations now condemn the same architecture. **QA-68, V-29.** Blom's approximation corroborates V-28's 2.590 vs simulated 2.600. |
| 1.2.0 | 2026-08-17 | Victor | **New §5.8 — QQ-21 mostly resolved, and it dissolves rather than answers.** External review reframed it as **Little's Law** (`N = λ·h`): `buckets == horizon_days` is `N = 1×h` written down, so the question is *which of daily-action / 21-day-hold / concentrated-book you break*. ★ **QQ-21 and QQ-15 are one question.** M-2 attribution corrected — the fee schedule and M-2 both favour fewer, larger positions, so the trade is **cadence** against both. **Two corrections to the review**: (i) `E[max of 130 normals] = 2.60σ`, not 2.8 — floors ~8 % higher, daily-action threshold **~$180 k**; at n=330 it is 2.91, so **QQ-11's universe expansion helps cost as well as power (V-28)**; (ii) ★ **its proposed "fourth option" is already built** — `_resolve_incumbency` can decline a roll, so the penalty **is** load-bearing; the defect is that **`incumbency_margin_delta` is 0.0 and is the same number as `penalty_z ≈ 1.23`** (V-26, V-27). **Resolution: the ladder controls how often you LOOK, δ controls how often you TRADE, and the holding period is emergent** — `N=5`, weekly challenges, `δ=1.23` ⇒ ~20-day holds, 60 rolls/yr, 6.0 %/yr at $20 k, **no architecture change**. **QA-65/66/67.** |
| 1.1.0 | 2026-08-17 | Victor | ✅ **QA-50 APPLIED — `charge_transaction_cost: true`, with QA-62's known-answer test written first. Full suite 891 green.** Implementing it surfaced **three code findings, one of which invalidates §5.6a's cost table a third time**: **(1) ★ `buckets == horizon_days`** (`backtester.py:110-111`), so total rolls/yr `= h × 252/h = 252` at **every** horizon — **the commission drag is HORIZON-INVARIANT**, and every prior 1w-vs-1m commission figure assumed a fixed `N=5` the code does not use. Ground (b)'s commission component is **zero by construction**; only the unmeasured proportional part (QQ-20) could ever bear on it. **QA-64, V-23.** **(2) ★ `initial_capital = 20000.0` is hard-coded** (`backtester.py:107`) — at that capital `$20` is **50 bps** (1w) and **210 bps** (1m, 21 buckets × $952), so the config's *"immaterial at realistic capital"* was false by two orders of magnitude. **QA-63, V-24. New QQ-21 — the 1m bucket architecture is a design blocker for the retrain**, and it collides with M-2. **(3) `charge_fees=True` had never executed** — now pinned by a *differential* known-answer test (P&L cancels; delta must be exactly `$20`). **V-25.** Also added: QQ-19/QQ-20/QQ-21 as table rows (previously referenced in text only). |
| 1.0.0 | 2026-08-17 | Victor | **Seventh external review — the flip is endorsed, and two of its three pre-checks found real defects.** **(1) The decisive argument for flipping `charge_transaction_cost` is that the invalidation cost is already sunk** — §5.6 consequences #1/#2 already require every backtest number to be re-baselined, so the flip's marginal disruption is **zero**. It is also weakly dominant: no book size makes 0 % of cost more accurate than 50–70 %. **QA-62** sequences it: ship with the 1m retrain, plus a known-answer test, `initial_capital` pinned, and `costs_charged` recorded. **(2) ★ Verified in code: a TRIM is charged `$0`** — `_reconcile_bucket` tests set membership only (*"Held positions incur no fee"*). Latent today (top-1 sleeves never trim) and **load-bearing the moment M-3's "trim rather than exit" ships**, when trimming becomes the fund's dominant action and costs ~nothing. **QA-61, V-20.** **(3) ★ Verified: `charge_fees=True` is exercised nowhere in the test suite** — a dormant branch that would be trusted on its first production run, the **D-18(c) shape** one step milder. **V-21.** **(4) `initial_capital` added to BacktestSpec (§7.1) and QA-48** — a flat fee's percentage drag spans **10×** from $100 k to $1 M, and `settings.yaml:55`'s *"immaterial at realistic capital"* never says what realistic capital is. **V-22.** AC-3.11a/b/c added. |
| 0.9.0 | 2026-08-17 | Victor | **Sixth external review — four fixes, two of them reversals of my own v0.8.0 closures.** (1) **QA-60 misattributed the factor** — `1/ρ²` is the gap between the two candidate *fixes*, not the code's defect. The code is off by **`1/β ≈ 385×`** (return units used as score units) **× 3.2×** (10 bps vs 32 bps) = **1232×**. Also: `1/β` is **IC-dependent** (385× at ρ=0.03, 115× at 0.10) and `β` needs **Pearson**, not the Spearman IC used elsewhere (≈4.5 % apart). **V-19.** (2) ⚠ **QA-50 REVERSED — `charge_transaction_cost` must default to `true` now.** v0.8.0's ordering was wrong: commission-only understates by 50–70 %, zero by **100 %**, and — decisively — **charging zero biases by 3.84 pts *toward the short horizon*** at a $100k book, which is the exact comparison ground (b) turns on. **QA-50a**; the config change is flagged as a production task, not applied. (3) **QA-58 is tilt-*correcting*, not tilt-neutral** — fitting on raw `R` under heteroskedastic noise attenuates high-vol names more (`κ_i` decreasing in `σ_i`), so the incumbent regressor already carries a low-vol tilt **from the fit**. §5.7 extended; **V-18** to measure it. (4) **Governance note beside the approval**: the decision now rests on **one substantive ground (M-4) plus a mandate reading (c)**, and **its reopening test is not currently evaluable** because it compares against the indeterminate cost differential. **QA-33** now also records *which ranked quantity* an IC is of (QA-58 makes it load-bearing); `ranked_quantity` added to CT-3.1. |
| 0.8.0 | 2026-08-17 | Victor | **Fifth external review — three items closed, one of my own corrections corrected.** (1) **Ground (b) re-statused ⏸ INDETERMINATE, not withdrawn** — v0.7.0's reversal table used **commission-only** costs, which is what **QA-49 forbids**; §5.6a now records the **flip-back threshold (3–12 bps)** as the bar QQ-20 measures against, plus two further understatements (trims are trades; the config used as evidence is itself non-compliant). **CT-3.1's `mandate_justification` rewritten** — it was shipping the retracted arithmetic to every consumer. QQ-14 superseded. (2) **QQ-18 CLOSED — new §5.7, QA-58/QA-59**: *normalise for the loss, de-normalise for the decision*; both branches were false alternatives, and the same rule closes **V-14's second face** (a `P50` fitted on QA-34 targets is a median *Sharpe*). (3) **QA-50 CLOSED** as a dated, self-expiring exemption ordered **after** QA-49 — flipping it today would charge commission only, the same defect one layer down. (4) ⚠ **QQ-16's diagnosis closed and my own v0.7.0 fix retracted** — new §9.1.6a: the penalty is `rt/β` with `β` the slope of **realised return ON opportunity**; my proposed empirical recipe was the **reciprocal** regression and would have reproduced the bug (penalties differ by `1/ρ² ≈ 1111×`). **QA-60.** The economic reading — at IC 0.03 the correct penalty is ~1σ, which produces M-3's "hold winners" behaviour from arithmetic alone — **survives ground (b)'s collapse**. |
| 0.7.0 | 2026-08-17 | Victor | **Fourth external review; four alignment fixes and one finding of my own that is worse than anything they raised.** (a) ⚠ **§5.6 ground (b) is WITHDRAWN** — chasing their one-way/round-trip catch found that the `5+10+1` formula is **dead code**, the per-side convention is **undeclared**, and **the backtester uses a flat $10/trade model** with `charge_transaction_cost: false`. On the real cost model the drag differential is 0.4–3.8 %, not 12.3 %, and **it favours 1w in five of six scenarios**. New **§5.6a**; **the decision stands on grounds (a) and (c)**. New QA-48/49/50 — QA-50 records `charge_transaction_cost: false` as a **live QA-12 / INV-016 violation**. (b) **§9 re-aligned to the horizon decision** — banner added; **§9.4 re-sorted**, Option 5 is the frame not a research candidate. (c) **§9.1.1's "economic threshold" framing withdrawn** — `c` is < 0.04 σ at every horizon, i.e. a sign test. (d) **Claim 3 given its expiry date** (QA-34 forks it — QQ-18). (e) **§9.5's R² comparison corrected** — the two baselines differ; QA-52 gates volatility against **persistence/HAR, not the mean**. (f) New **§9.6 — the timing leg**, which §9 never covered (QA-53…QA-57, QQ-19). (g) **V-14…V-17 added, V-3 falsified.** |
| 0.6.0 | 2026-08-17 | Victor | **§9.1 rewritten as a validatable document** — exact label mathematics, the three LightGBM objectives with formulas and references, the bundle output, the blend arithmetic, and **V-1…V-13, a falsifiable claim list for external review**. Two corrections and two findings: (i) v0.1.0's "three deterministic functions of one variable" is **too loose** — `y^rank` depends on the cross-section, and the ranker's target is market-neutral where the other two are not; the sharpened claim is that **the blend's own z-step erases that difference**; (ii) **four LightGBM lambdarank parameters are never set** (`label_gain`, `lambdarank_truncation_level`=30, `sigmoid`, `eval_at`) and are load-bearing — truncation at 30 means the objective **ignores ~100 of 130 names**; (iii) the **turnover penalty is dimensionally inconsistent** (0.001 subtracted from a z-score-scale quantity ≈ 0.1 % of 1σ) — **QQ-16**; (iv) **`QuantileBundle` already exists** — §9.3 Option 3 is a promotion, not a build. |
| 0.5.0 | 2026-08-16 | **Victor (decision)** | ★ **QQ-1 CLOSED — HorizonSet v1 approved: `{ production 1m · timing-only 1w · research 1q }`.** 1w demoted from nomination objective to timing input. Grounds in order of force: **M-4** (a 5-day objective systematically manufactures the CRA *carrying on a business* pattern, and the downside is retroactive reclassification, not a drawdown), **cost** (16.13 %/yr drag at 1w vs 3.84 % at 1m on this repo's own 32 bps round trip — 1w must win by 12.3 % gross to tie), and **L0 §12.1** (5 days is not "weeks"). §5.6 rewritten as the decision record with the full reasoning, what was given up, and eight downstream consequences. QQ-2's decomposition axis settled by implication; QQ-3 de-risked. **QQ-14/QQ-15 raised** — the cost figure is an estimate that D-11's trade log can measure, and INV-6's daily cadence was written for a 5-day objective. |
| 0.4.0 | 2026-08-16 | Victor | **Third external review; four corrections.** (a) v0.3.0's "no `τ` gives a flat IC curve — the ratio never hits 1.00" was **self-refuting** — a continuous ratio running 2.24→0.29 must cross 1.00, and it does at **τ = 15.42d**. The real criticism is sharper: v0.2.0 **smuggled in an implicit τ estimate** and closed a question on it. (b) The `(n,T)` table inherited the same flat-IC anchor — **relabelled as an MDE object**, which needs no `τ` and makes the ~330-name result assumption-free. (c) The rank-invariance justification for QA-43 **overreached** (ranks remove an additive shock, not heterogeneous factor loading), and `BR` was conflated with `n` — G&K breadth is bets **per year**. (d) The GKX calibration anchor is now **hedged as an upper reference**. **§5.4 restructured into two axes** (decomposition vs estimation); **F moved to the target axis**. New **QA-47** — the arbitration rule. QQ-1/QQ-2 given full recommendations, **not closed** (QA-2: Victor's). |
| 0.3.0 | 2026-08-16 | Victor | **§5.3b rewritten after a second external review found a real error** — the v0.2.0 power table held `IC` flat across horizons, which §5.3a forbids. **QQ-3 is REOPENED**: 1q is testable iff the aggregate signal half-life exceeds ~3 weeks. Added the **`n` axis** (~330 names reaches t=3 at 1q on existing history — cheaper than any architecture option) and **QA-43/QA-44** on effective breadth. **§5.5 build order inverted** — diagnostics now precede the go/no-go power test. New **QA-45** (volatility neutralisation — a vol-normalised target induces a low-vol tilt), **QA-46** (per-horizon loss weighting under stacking), **QA-37 corrected** to López de Prado's full span-average uniqueness. Option verdicts B/D/E/F amended. |
| 0.2.0 | 2026-08-16 | Victor | **§5 substantially revised after an external review** (a second AI agent's analysis, cross-checked numerically). Added **§5.3a** the alpha-decay law — `IC(h) ∝ (1−e^(−h/τ))/√h`, `h* = 1.256τ`, extended to non-i.i.d. noise; **§5.3b** the power calculation, which **closes QQ-3: a 1-quarter horizon is not testable on this panel** (t=1.88 at 7.6y, IC=0.03); **§5.4a** three corrections that precede any architecture choice — volatility-normalised targets (Yang–Zhang), uniqueness weighting, multiple-testing correction. Options D and F upgraded to their parametric forms. Build order rewritten (§5.5). QA-31…QA-40 added; **§8.4 reference list** added. |
| 0.1.0 | 2026-08-16 | Victor | Initial draft. Three things beyond the routine: **§5** the horizon set — six options for training and inferring 1w/1m/1q together; **§8** the mathematical-provenance requirement for all quant code; **§9** a review of the three-head model bundle. §§5 and 9 raise decisions that **D-04 owns** — D-03 states the requirement and the evaluation protocol, D-04 chooses the machinery. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"Given the features, which names look best right now — and is that judgement real or is it
> noise that happens to have a number attached?"**

D-03 is the **stateless** half of SEAT-3. It computes screens, constructs signals, and — critically
— **owns the protocol by which any of it is judged to work.** It holds no model state and does no
training; D-04 does that. But D-03 defines what "works" means, and that is the more load-bearing of
the two jobs.

## 1.2 Position

```text
            ┌──────────────────────────────────────────────┐
            │  D-04 Model Training & Inference   SEAT-3    │
            │  fits models, produces rank_score            │
            └───────▲───────────────────────────┬──────────┘
                    │ evaluated by              │ consumes
                    │ D-03's protocol (§7)      │ D-03's horizon set (§5)
            ┌───────┴───────────────────────────▼──────────┐
            │  D-03 QUANTITATIVE ANALYSIS        SEAT-3    │  ← this spec
            │  screens · signals · backtest · metric gates │
            │  ★ stateless — pure functions, no fitting    │
            └───────────────────▲──────────────────────────┘
                                │
                    ┌───────────┴────────────┐
                    │ D-02 Feature Engineer  │  features + labels
                    └───────────▲────────────┘
                                │
                    ┌───────────┴────────────┐
                    │ D-07 Data Engine       │  prices, calendar check
                    └────────────────────────┘

            ✗ D-01 thesis / verdict — FORBIDDEN INPUT (INV-014)
```

## 1.3 Boundary — the D-03 / D-04 line

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-03 IS STATELESS. IF IT HAS TO BE FITTED, IT IS D-04.          ║
║                                                                  ║
║  D-03: a 52-week-high screen · a momentum z-score · a backtest   ║
║        engine · RankIC · a Sharpe ratio · a metric gate ·        ║
║        the definition of the horizon set · the purge/embargo     ║
║        rule · the cost model                                     ║
║                                                                  ║
║  D-04: anything with learned parameters — the ranker, the        ║
║        regressor, the classifier, the blend weights, the         ║
║        hyperparameters, rank_score itself                        ║
║                                                                  ║
║  The blend weights are the interesting edge case. They are       ║
║  FITTED (F0 D-18 fitted them across 8 folds), so they are        ║
║  D-04's — even though they look like configuration.              ║
╚══════════════════════════════════════════════════════════════════╝
```

**Authority: RECOMMEND (L0 §3.1).** D-03 produces a ranking, never a decision.

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **HorizonSet** | a named, versioned set of horizons | `(name, version)` | **§5** — the contract D-04 trains against |
| **Screen** | a stateless cross-sectional filter | `screen_id` | pure function over a D-02 panel |
| **Signal** | ticker × date × signal | `(ticker, date, signal_id)` | a stateless score, **not** `rank_score` |
| **BacktestSpec** | a reproducible evaluation | `spec_id` | universe, window, horizon, costs, CV protocol |
| **BacktestResult** | one run of a spec | `(spec_id, run_id)` | metrics per horizon, with effective-N |
| **MetricGate** | a threshold with a test | `gate_id` | pass/fail + the statistic and its distribution |
| **MethodEntry** | one formula's provenance | `formula_id` | **§8** — maths, symbols, citation, assumptions |

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-02 Feature Engineering   the feature panel + labels, contract-bound
  ├── D-07 Data Engine           prices (raw + adj_as_of), the calendar check (§6A)
  └── D-00 shared                Money, errors, logging

DEPENDED ON BY
  ├── D-04 Models    the horizon set (§5), the evaluation protocol (§7),
  │                  the metric gates — D-04 is JUDGED by D-03, not the reverse
  ├── D-05 Risk      signal inputs
  └── D-09 Reporting the slate

DOES NOT DEPEND ON
  ✗ D-01 — no thesis, no verdict, no conviction (INV-014)
  ✗ the LLM gateway (AP-5, ST-5)
  ✗ D-04 — ★ D-03 must not import the models it evaluates. An evaluator
      that depends on the thing it evaluates cannot fail it honestly
```

---

# 4. MODULE DECOMPOSITION

```text
src/quant/
├── horizons/           # ★ the HorizonSet — §5
├── screens/            #   52w position, gaps, volume, momentum rank
├── signals/            #   stateless scores; entry timing, sell monitor
├── backtest/           #   engine, cost model, CV protocol
│   ├── engine.py
│   ├── costs.py
│   └── protocol.py     #   purge/embargo, scaled to the longest horizon (§7.3)
├── metrics/            #   RankIC, ICIR, Sharpe, turnover — with effective-N
├── gates/              #   metric gates: threshold + statistic + distribution
└── methods/            # ★ THE METHOD REGISTER — §8
    └── entries/        #   one file per formula_id
```

---

# 5. THE HORIZON SET — training and inferring 1w · 1m · 1q together

## 5.1 The limitation, stated precisely

`LabelBuilder` builds **one horizon: 5 trading days.** Its own docstring says so — *"v1: Only
1-week horizon"* — and `horizon_days` declares `"1m": 21` with the comment *"not used in v1"*. Every
label is a deterministic function of `fwd_ret_1w`:

```python
fwd_ret_1w   = adj_close.shift(-5) / adj_close - 1
label_up_1w  = fwd_ret_1w > cls_threshold          # threshold = round-trip cost in bps
rank_label_1w = cross_sectional_quintile(fwd_ret_1w)
```

## 5.2 Why this is a mandate problem before it is a modelling problem

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE FUND HOLDS FOR WEEKS TO MONTHS. THE MODEL PREDICTS FIVE     ║
║  DAYS.                                                           ║
║                                                                  ║
║  L0 §12.1  holding period: "Medium-term (weeks-months); hold     ║
║            winners, trim rather than exit (M-3)"                 ║
║  M-4       registered-account day-trading is being ACTIVELY      ║
║            REDUCED — CRA "carrying on a business" risk           ║
║                                                                  ║
║  A 5-day training target is a short-hold objective. Optimising   ║
║  it optimises for exactly the behaviour M-3 and M-4 exist to     ║
║  curb, and then asks the human to hold the position for weeks    ║
║  on a signal that was never fitted for that.                     ║
║                                                                  ║
║  This is not primarily an accuracy question. It is a question    ║
║  of whether the objective matches the mandate.                   ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **QA-1** | A `HorizonSet` is **named, versioned and explicit**, and every model, backtest and metric gate declares which one it was fitted or evaluated against. "The horizon" is never implicit |
| **QA-2** | The production horizon set must be **justified against the mandate** (L0 §12.1, M-3, M-4) in the spec that adopts it, not chosen for statistical convenience. ✅ **Satisfied for HorizonSet v1 — see §5.6**, decided by Victor 2026-08-16 |

## 5.3 The problem every option must solve — overlapping labels

Before the options, the hazard they all share. **This is the single biggest statistical trap in
multi-horizon work**, and it gets worse the longer the horizon.

With daily sampling and a 63-day horizon, consecutive labels share **62 of their 63 days**. The rows
look independent; the labels are almost the same number. Consequences:

- **Effective sample size collapses.** ~250,000 rows at a 1-quarter horizon carry roughly
  `N / 63` independent observations per ticker — an order of magnitude less information than the
  row count advertises.
- **Naive cross-validation leaks massively.** A test-fold label computed from prices the training
  fold already saw is look-ahead wearing a fold boundary (constitution INV-1).
- **Every t-statistic is inflated.** Overlapping returns are autocorrelated by construction, so a
  RankIC standard error computed as `σ/√N` is wrong by roughly `√(overlap)`.

| ID | Rule |
|---|---|
| **QA-3** | Cross-validation **purges** training observations whose label window overlaps any test observation, and applies an **embargo** after each test fold. Both are **scaled to the longest horizon in the set**, not to a constant |
| **QA-4** | Every reported statistic carries its **effective sample size** and an autocorrelation-corrected standard error (Newey–West or equivalent). A metric gate compares against the corrected statistic, never the naive one |
| **QA-5** | Horizons in one set are **never compared on raw metric value**. A 1q RankIC of 0.03 and a 1w RankIC of 0.03 are not the same evidence, because their effective N differs by ~12× |
| **QA-6** | ★ ⚠ *(defined in the audit — cited by **AC-3.5** and never written.)* **A multi-horizon design is adopted only against a per-horizon single-task BASELINE**, evaluated on the same folds, costs and universe. ★ **Sharing parameters across horizons is a hypothesis, not a free lunch** — it can help through regularisation or hurt through negative transfer, and §5.4's option comparison is unreadable without the baseline it is being compared to |

## 5.3a The alpha-decay law — how to *choose* a horizon rather than assume one

> **Added v0.2.0** after an external review. This subsection did not exist in v0.1.0, which listed
> options without giving any criterion for picking among them. **The criterion is derivable**, and
> having it changes the build order (§5.5).

Model a signal whose expected instantaneous drift decays exponentially with time constant `τ`:

```
    μ(s)  = μ₀ · e^(−s/τ)                        drift s periods after observation
    M(h)  = ∫₀^h μ(s) ds = μ₀·τ·(1 − e^(−h/τ))   cumulative expected alpha over h
    noise ∝ σ√h                                   h-period return s.d. under i.i.d. returns

    ⇒  IC(h) ∝ (1 − e^(−h/τ)) / √h
```

Maximising over `h` gives `e^u = 2u + 1` with `u = h/τ`, whose non-trivial root is

```
    h* = 1.2564 · τ  =  1.813 × the signal's half-life
```

*(Verified numerically 2026-08-16. The half-life relation follows from `t½ = τ·ln2 = 0.6931τ`.)*

**Every feature has its own `τ`, therefore its own best horizon.** This is the actual reason a
model trained at one horizon does not transfer to another: it is not a scaling problem, it is a
**different effective feature set** — the fit concentrates on features whose decay matches the
training horizon and discards the rest.

### Extension: the √h assumption is itself a modelling choice

The `√h` noise term assumes i.i.d. returns. Under a variance-ratio departure — noise ∝ `h^H` for
Hurst exponent `H` — the optimum solves `u·e^(−u)/(1−e^(−u)) = H`:

| H | regime | h*/τ |
|---|---|---|
| 0.40 | mean-reverting | **1.62** |
| 0.45 | mean-reverting | 1.43 |
| **0.50** | **i.i.d. (the standard result)** | **1.26** |
| 0.55 | trending | 1.10 |
| 0.60 | trending | 0.95 |

Mean reversion *lengthens* the optimal horizon; trending *shortens* it. Equities show short-horizon
reversal (`H < 0.5` daily) and intermediate-horizon momentum (`H > 0.5`), so **`h*` is regime-
dependent and must be estimated, not assumed** — including the exponent.

| ID | Rule |
|---|---|
| **QA-31** | Before a horizon set is adopted, **`IC(h)` is measured empirically per feature** on a grid `h ∈ {1,2,3,5,10,21,42,63,126}` and `τ` is estimated. A horizon chosen without this measurement is chosen arbitrarily |
| **QA-32** | The decay fit records its assumed noise exponent `H` and whether it was estimated or assumed at 0.5 (§8, QA-23) |

## 5.3b Power — what can this panel detect, and on which axes

> **Rewritten v0.3.0, corrected again v0.4.0.** The v0.2.0 version held `IC = 0.03` fixed across all
> three horizons and closed QQ-3 on it, which is inconsistent with §5.3a. The conclusion is therefore
> **conditional**, and §5.5's build order was inverted. Both are corrected below.
>
> ⚠ **v0.3.0's justification for that was itself wrong, and the correction matters.** It said *"no
> value of `τ` produces a flat IC curve — the ratio runs 2.24 at τ=5 down to 0.29 at τ=1000, never
> 1.00."* A continuous, monotone ratio spanning 2.24 to 0.29 **must** pass through 1.00. It does, at
> **τ = 15.42 d** (half-life 10.7 d), where `IC(5) = IC(63) = 0.1239` — and at that `τ` the 1q
> t-statistic is **exactly the 1.88 v0.2.0 reported**.
>
> **So v0.2.0 was not off the model. It was self-consistent under an unstated `τ ≈ 15 d`** — an
> entirely plausible value for a feature set weighted toward 1–20d returns, RSI, MACD and volume
> z-scores. **That is the worse failing, not the lesser one:** in a document that requires a
> MethodEntry for every formula (§8), a load-bearing parameter that is never named, never sourced
> and never tested is a more serious defect than a number that is simply wrong.
>
> What *is* true is the three-point claim: at τ = 15.42, `IC(1m)` sits **31% above both endpoints**,
> so the curve is **peaked, not flat** — and a power table that treats all three horizons alike
> still misstates the middle one badly.

### Step one: the minimum detectable IC — this needs no `τ`

For cross-sectional rank IC with `n` names on `T` dates at horizon `h`, `ρ_t` has null variance
≈ `1/(n−1)`, and overlapping labels cut the independent count to `T/h`:

```
    SE(mean IC) ≈ √( h / ((n−1)·T) )       MDE(t*) = t* · √( h / ((n−1)·T) )
```

**MDE is computable before anything is measured** — it is the bar, not a prediction. At **n = 130,
T = 1915** (~7.6y, the ~249k-row panel):

| Horizon | smallest detectable IC at t>2 | at **t>3** (multiple-testing threshold) |
|---|---|---|
| 1w | 0.0090 | 0.0135 |
| 1m | 0.0184 | 0.0277 |
| **1q** | 0.0319 | **0.0479** |

For calibration — **and this anchor is hedged, per §8's own rules** *(v0.4.0)*: Gu, Kelly & Xiu
(2020) report ≈ 0.40% monthly out-of-sample `R²` for individual stocks, from which `IC ≈ √R² ≈
0.063` **is a house derivation, not their result**. Three conversions are hidden in that step —
pooled predictive `R²` → per-date cross-sectional `R²`, Pearson → Spearman, and total-return `R²` →
excess-return IC — and their direction is not all the same way. It is also an **upper reference**
(~94 characteristics with interactions, neural ensembles, ~30k stocks, 60 years), not a comparable
for an OHLCV-plus-fundamentals set over 130 names.

Read it as: **a 1q bar of 0.048 is demanding but within the range the literature reaches at its
best** — enough that it cannot be dismissed without measuring `τ`, and not enough to assume it will
be cleared. **This derivation needs a MethodEntry (QA-20) before it is cited again.**

### Step two: whether the bar is clearable — this *does* need `τ`

Anchoring on a measured `IC(1w) = 0.03` and propagating through the decay law:

| Signal `τ` | half-life | implied `IC(1q)` | t at 1q (n=130, T=1915) |
|---|---|---|---|
| 10 d | 6.9 d | 0.0214 | 1.34 ✗ |
| 25 d | 17.3 d | 0.0429 | 2.68 ✗ |
| **30 d** | **20.8 d** | **0.0483** | **3.03 — the threshold** |
| 50 d | 34.7 d | 0.0636 | 3.98 ✓ |
| 100 d | 69.3 d | 0.0810 | 5.07 ✓ |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE 1-QUARTER HORIZON IS TESTABLE ON THIS PANEL IF AND ONLY IF  ║
║  THE AGGREGATE SIGNAL HALF-LIFE EXCEEDS ROUGHLY THREE WEEKS.     ║
║                                                                  ║
║  v0.2.0 asserted "not testable" unconditionally and closed       ║
║  QQ-3. That was wrong: it assumed IC(1q) = IC(1w) = 0.03, which  ║
║  the decay law forbids.                                          ║
║                                                                  ║
║  Which side we land on is genuinely open. The current feature    ║
║  set mixes SHORT-tau price features (1-20d returns, RSI, MACD,   ║
║  vol z-scores) with LONG-tau fundamental features (Piotroski,    ║
║  accruals, growth, sector-relative z). The aggregate tau is      ║
║  whichever the fitted weights favour — and nobody has measured   ║
║  it.                                                             ║
║                                                                  ║
║  QQ-3 IS REOPENED. It closes at build step 5, on a measurement.  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Still step one: the axis v0.2.0 ignored entirely — `n`

`MDE(t*) = t*·√(h/((n−1)·T))`. **`n` and `T` enter identically.** v0.2.0 varied `T` across four
values, treated `n = 130` as a fact of the world, and concluded "19.4 years of data". That was an
artefact of holding the wrong variable fixed.

> **Relabelled v0.4.0.** This table previously read *"1q rank IC, IC = 0.03"* — which is the same
> flat-IC anchor the section opens by rejecting, two subsections earlier. The arithmetic was fine;
> the framing was not. **What it actually computes is the `(n, T)` combination at which
> `MDE(t=3)` for a 1q horizon falls to 0.03** — a step-one object requiring **no `τ`**, and
> therefore not vulnerable to the critique this section is built on.

**`(n, T)` at which a 1q horizon can detect `IC = 0.03` at t > 3** — bold clears the bar:

| n | T=657 (2.6y) | T=1915 (7.6y) | T=3780 (15y) | T=5040 (20y) |
|---|---|---|---|---|
| **130** | 1.10 | 1.88 | 2.64 | **3.05** |
| **250** | 1.53 | 2.61 | **3.67** | **4.23** |
| **500** | 2.16 | **3.69** | **5.19** | **5.99** |
| **1000** | **3.06** | **5.23** | **7.34** | **8.48** |

**On the history already held, ~330 names reaches t = 3 at 1q.** That is a data task — an ETL
re-run — not a twelve-year wait, and it is cheaper than every architecture option in §5.4.

Three things make this concrete rather than aspirational:

- `config/universe_balanced.yaml` **already defines 123 sector-balanced names**; the constraint on
  the current 130 was never analytical, it was that expanding needs an ETL re-run.
- D-07 serves `stock-list` (38,723 symbols) and `financial-statement-symbol-list` (26,149) — the
  universe source exists (`L1-data-engine.md` §5A.1, QD-5).
- **L0 §12 already sanctions this explicitly**: *"broad sector coverage in the universe exists to
  give the ranking model breadth, not to push the portfolio toward diversification."* **Universe
  breadth and book concentration are different things**, and M-2 constrains only the second.

### The haircut, stated honestly *(corrected v0.4.0)*

`Var(ρ_t) = 1/(n−1)` assumes cross-sectional independence. Real universes have factor structure, so
effective breadth is below `n`.

**The naive `n_eff = n/(1+(n−1)ρ̄)` correction is the wrong formula here** and would badly mislead:
it saturates at `1/ρ̄` regardless of `n`, implying universe expansion buys nothing. That formula is
for the variance of an equally-weighted *mean*.

> ⚠ **v0.3.0 justified this by saying a rank statistic "differences out the common factor, because
> ranks are location- and scale-invariant within a date." That argument is too strong and is
> withdrawn.** Ranks remove a common **additive** shock. Factor structure is not an additive shock —
> it is **heterogeneous loading**: a +5% market day moves high-beta names more than low-beta ones
> and genuinely reorders the cross-section. The market is therefore *not* differenced out of a rank
> statistic; only the equal-weighted level is.
>
> The **conclusion** still stands — residual pairwise correlations in equities are typically an
> order of magnitude below raw correlations, so widening the universe buys real breadth — but it
> rests on that empirical fact, **not** on an invariance argument. QA-43's own wording was already
> correct ("after removing the market and dominant sector factors"); it was the prose that
> overreached.

> ⚠ **Second correction: `BR` is not `n`.** Grinold & Kahn define breadth as **independent bets per
> year**, so a cross-sectional strategy rebalanced every `h` days has `BR ≈ BR_eff × 252/h`, not
> `BR ≈ n`. **Shorter horizons therefore carry more breadth** — which is the genuine counterweight
> to the turnover-cost argument in QQ-1, and any comparison that omits it is incomplete. Conflating
> the two in a document that mandates MethodEntries (§8) is exactly the defect QA-21 exists to
> prevent.

| ID | Rule |
|---|---|
| **QA-33** | *(revised v0.9.0)* A horizon is admitted to production only if the panel can detect the smallest IC worth acting on at **t > 3**. The power record states **`n`, `T`, `h`, the assumed `IC(h)` and its provenance** (measured or anchored-and-propagated), **plus which ranked quantity the IC is *of*** — QA-58 makes this load-bearing, since ranking `Ẑ` and ranking `Ẑ·σ̂√h` are different orderings with different ICs. It lives in the HorizonSet (CT-3.1). **Both axes are recorded** — a power claim that fixes `n` implicitly is incomplete |

> **Does QA-58 invalidate §5.3b's numbers?** No. The **MDE** formula depends only on `n`, `T`, `h`
> — not on which quantity is ranked — so the MDE table and the `(n,T)` grid stand as computed. What
> becomes quantity-specific is the **assumed `IC(h)`** and the `τ` estimates propagated from it.
> This is a **labelling requirement on the provenance field**, not a recomputation.
| **QA-43** | **Effective breadth is measured, not assumed.** Estimate average pairwise **residual** correlation after removing the market and dominant sector factors, and report `BR` alongside `n`. Neither `BR = n` nor the equally-weighted-mean haircut is admissible as a default |
| **QA-44** | Universe expansion is evaluated by **added breadth, not added count**. 370 more semiconductor names add little; names in uncorrelated sectors add more. This is a mandate-compatible lever (L0 §12) and must be considered **before** concluding that a horizon needs more history |
| **QA-124** | ⚠⚠ **QA-43's *residual* correlation cannot answer the breadth question, and the gate is fed the RAW correlation instead — a stated divergence, not a silent one.** *Measured 2026-08-27 on synthetic panels with a **known** common correlation:* removing a market factor **built from the same names** drives the average pairwise residual correlation to **exactly `−1/(n−1)`** — `−0.0909` at n=12, `−0.0020` at n=500 — **identically at `ρ_true = 0.00` and `ρ_true = 0.35`.** ★★ A statistic that cannot distinguish an uncorrelated universe from a 0.35-correlated one measures nothing; the raw measure recovers both to three decimals. ★ **Both readings are legitimate and ask different questions**: *residual* correlation asks *"is there structure left after the known factors"*, while **G&K breadth asks how many independent BETS a book holds** — and ten names all with β≈1 are one bet however independent their residuals are. The gate wants the second. ⚠ **QA-43 is NOT amended here** — the residual figure is still computed and reported as a diagnostic, and which statistic the gate should consume is **QQ-14, open** |
| **QA-125** | ★★★ **D-03 never nominates a name that cannot be traded, and the exclusion is RECORDED on the nomination.** ⚠ *Found 2026-08-27 running the S&P 500 sweep:* `AVB` and `EQR` delisted on 17 and 18 August and **dropped out of the ranking only because they print no bar on the as-of date** — `rank_by_model` selects `panel[date == as_of]`. ★★ **That is a side effect doing a guard's job**: a name that delisted *today* and still printed a bar would rank normally, and nothing would say so. ⚠ **§6A cannot cover this** — *"has any name stopped trading?"* is a **current-state** question and the calendar gate is **window-scoped by construction**, so a three-week delisting feed reports `UNCHECKED` against every real 200-day window (AB-15, DE-60). ★ The check belongs here: D-03 owns the ranking, and an untradeable name is **excluded from `candidates` and listed in `excluded[]` with its reason** — never silently dropped, which is DE-13's rule one domain over |
| **QA-126** | ★ **Tradeability is SUPPLIED to D-03, never fetched by it.** ⚠ D-03 ranks D-02's numbers and computes none of its own; reaching into D-07's event store here would make the ranking layer a data client. The orchestrator passes the delisted set, exactly as it passes the panel |

## 5.4a Three corrections that precede any architecture choice

Measured against an external review, v0.1.0's option list under-specified three things that matter
more than the choice between options. **All three apply to every option in §5.4.**

### (i) Normalise the target — by conditional volatility *and* by horizon

v0.1.0 said "standardise per horizon". That is not enough. The target should be

```
    y[t,h] = ( log P[t+h] − log P[t] ) / ( σ̂[t] · √h )
```

where `σ̂[t]` is a **conditional** daily volatility estimate, not a constant. This normalises across
three axes at once — horizons, time (volatility clustering) and the cross-section (high-beta vs
low-beta names) — and it is what allows one model to serve several horizons without the loss being
dominated by the longest one.

Estimate `σ̂[t]` from OHLC rather than close-to-close: range-based estimators are far more efficient
per observation (Parkinson ≈ 5×, Garman–Klass ≈ 7.4×, Yang–Zhang up to ≈ 14× the variance
efficiency of close-to-close).

| ID | Rule |
|---|---|
| **QA-34** | Labels are **volatility-normalised** using an OHLC range estimator, and the estimator is named in the HorizonSet (CT-3.1) with its MethodEntry (§8) |
| **QA-35** | **Yang–Zhang is the default**, not Garman–Klass or Parkinson. GK and Parkinson assume no overnight gap and zero drift; this universe gaps on earnings, and an estimator that ignores the overnight move **understates** volatility exactly on the days that matter |
| **QA-36** | ⚠ **A volatility-normalised target changes the economic object being predicted** — from a return to something closer to a forward Sharpe. That is arguably better for sizing, but the backtest and every metric gate must be restated in those terms rather than silently reinterpreted |
| **QA-45** | ★ **The normalised target must be neutralised against `σ̂[t]`, or IC reported conditional on volatility decile, before any gate accepts it.** Ranking on a forward-Sharpe target **systematically prefers low-volatility names** — it rediscovers the low-volatility / betting-against-beta anomaly (Frazzini & Pedersen 2014), and the backtest then looks good for reasons unrelated to any feature built here. Without this, QA-36's "restate the gates" is unenforceable: **the gate cannot separate signal from the volatility tilt** |

> **QA-45 has a mandate consequence too.** A low-volatility tilt systematically **underweights the
> high-volatility AI/semiconductor theme** — the concentration M-2 makes deliberately. So an
> un-neutralised vol-normalised target does not merely bias the statistics; it quietly pushes the
> ranker against the fund's stated posture.

### (ii) Weight observations by uniqueness, not just purge

Purging and embargo (QA-3) prevent *leakage*. They do **not** fix *over-counting*: with `h=63` and
daily sampling, the long-horizon head still sees each piece of information ~63 times and becomes
confident on duplicated evidence.

| ID | Rule |
|---|---|
| **QA-37** | *(corrected v0.3.0)* Training observations are weighted by **average uniqueness over the label's own span**: `ū_i = (1/\|span_i\|) · Σ_{t ∈ span_i} 1/c_t`, where `c_t` is the number of concurrently-open labels spanning `t` (López de Prado 2018, §4.4). **v0.2.0 wrote "approximately `1/c_t`", which is the concurrency at a point, not the mean over the span.** For fixed-`h` labels the distinction is cosmetic; for **variable-span labels (triple-barrier, §5.4 Option F) it is not**, and §8's own provenance rule requires the full definition rather than a paraphrase. Purging without uniqueness weighting fixes half the overlap problem and leaves the confident half |

### (iii) Correct for multiple testing across the horizon grid

Testing `h ∈ {1w, 1m, 1q}` × several feature sets × several model families multiplies the trials.

| ID | Rule |
|---|---|
| **QA-38** | A horizon-grid search reports a **deflated Sharpe / multiple-testing–corrected statistic**, and the number of effective trials is recorded. The corrected statistic is what the gate compares against (QA-15) |

## 5.4 The options — **two axes, not one menu** *(restructured v0.4.0)*

> **v0.1.0–v0.3.0 presented A–F as a six-way choice. They are not.** A, B, C and D are
> **estimation architectures** — *how you fit across horizons*. E is a **problem decomposition** —
> *what you predict, for which decision*. They are largely **orthogonal**: you can have E with a C
> selection leg. Forcing them into one list creates a false choice, and that is why QQ-2 resisted
> closure for three revisions.
>
> **F is not a peer of A–E at all.** It is a *target-definition* choice, and it belongs with §5.4a
> alongside vol-normalisation. It is left in place below so existing citations resolve, with its
> verdict rewritten to say where it actually fits.

| Axis | Options | Who decides |
|---|---|---|
| **Decomposition** — one objective, or selection + timing? | **E** vs "single objective" | Mandate-derived ⇒ **D-03 / Victor** (QA-2) |
| **Estimation** — how to fit across horizons | **A · B · C · D** | **D-04**, on D-03's protocol (QA-5, QA-26) |
| **Target definition** | §5.4a + **F** | D-02 owns labels; D-03 owns the protocol that accepts them |

### The six, as originally listed

Each is described with what it actually costs, not just what it promises. **The decision is D-04's;
D-03 states the options and the evaluation protocol that will judge them.**

### Option A — Independent bundles per horizon

Train the existing ranker/regressor/classifier separately for each horizon. **3 horizons × 3 roles
= 9 models.**

| | |
|---|---|
| **Pro** | No new machinery. Existing CPCV, tuning and governance apply unchanged. Each horizon is fitted optimally for itself. Easy to abandon a horizon that shows no signal |
| **Con** | **3× training and 3× tuning cost** — the rel5 3-c sweep was already 25 sweeps. Zero parameter sharing, so the 1q model must learn from its own collapsed effective-N alone. Fits the same underlying signal three times. Pushes the combination problem entirely downstream |
| **Verdict** | The honest baseline. **Build it first regardless**, because every other option must beat it to justify its complexity |

### Option B — Multi-task model: shared trunk, per-horizon heads

One model learns a shared representation; one output head per horizon.

| | |
|---|---|
| **Pro** | The short horizon — which has far more effective samples — **regularises the long one**. One artifact to govern. Auxiliary-task learning is well-established for exactly this sample-imbalance case |
| **Con** | **GBDTs do not do this natively.** Fitting one tree ensemble per output recovers Option A and loses the sharing. So this option forces the neural branch — `ft_transformer.py`, `tabm_models.py`, `sequence_model.py` all exist but none has demonstrated superiority over the GBDTs on this data |
| **Verdict** | *(amended v0.3.0 — "highest ceiling" was overstated.)* Multi-task learning pays when tasks are **related but not nested**. Here the horizons are **strictly nested**: `r(0→63) = r(0→5) + r(5→21) + r(21→63)`. The gain is therefore **asymmetric** — the short horizon, with ~12× the effective samples, does regularise the long one, but the long head teaches the trunk almost nothing the short one has not. And the nesting is **better exploited structurally (Option D) than by independent heads**. Keep at step 9; the honest claim is "modest per-head flexibility over Option C", not "highest ceiling" |

### Option C — Horizon as a feature (horizon-conditioned single model)

Stack the data: each `(ticker, date)` appears once per horizon, with `horizon_days` as an input
feature and that horizon's forward return as the label.

| | |
|---|---|
| **Pro** | **Works with the existing GBDT stack — no architecture change.** Maximal parameter sharing. One model. Can interpolate to horizons never trained on. The smallest code change of any option here |
| **Con** | Each row appears 3×, so the i.i.d. violation compounds — CV must group on `(ticker, date)` so one row's three copies **cannot straddle a fold boundary**. Label scales differ (1q return volatility is ≈ √12 × 1w), so the target must be **standardised per horizon** or the model will spend its capacity learning scale. Risk that it learns *only* scale |
| **Verdict** | ★ **Best effort-to-value ratio.** Standardise the target, group the CV, and it is a small, testable change to a stack that already works |
| **Also required** *(v0.3.0)* | **A per-horizon loss-weighting policy must be stated explicitly.** Uniqueness weighting (QA-37) alone gives the 1w copies roughly `63/5 ≈ 12.6×` the total weight of the 1q copies — so "just apply uniqueness weights" silently sets the horizon balance to ~12.6 : 1 in favour of the short horizon. That may be the right choice; it may not. **It must be a decision, not a side effect** (QA-46) |

### Option D — Term-structure decomposition (non-overlapping increments)

Predict **disjoint** increments — `r(0→1w)`, `r(1w→1m)`, `r(1m→1q)` — and sum them for any horizon.

| | |
|---|---|
| **Pro** | The increments are **far closer to independent**, which directly attacks §5.3. Any horizon reconstructs by summing. And it answers a question no other option asks: **where in time does the edge actually live?** If increments 2 and 3 carry no signal, that is a finding worth more than a model |
| **Con** | Errors compound on summation. The later increments are quite likely unpredictable — most documented equity predictability is short-horizon — so this may produce two dead heads. Reconstructed long-horizon variance is not the same as directly-modelled long-horizon variance |
| **Verdict** | ★ **The most scientifically informative option — but estimate it *parametrically*.** With ~80 independent 1q observations per name, three freely-estimated increments is already too many parameters. **§5.3a gives the functional form.** *(Corrected v0.3.0 — v0.2.0 said "fit the single decay constant τ", which contradicts **QA-31**'s "every feature has its own τ". Both cannot govern one model.)* The clean resolution is a model **linear in features with per-feature decay**:

```
        ŷ(h) = Σᵢ  wᵢ · xᵢ · τᵢ · (1 − e^(−h/τᵢ))
```

with each `τᵢ` **estimated once from the IC(h) diagnostic and then frozen**, leaving only the `wᵢ` free. One fitted parameter per feature, structurally coherent across horizons, no consistency penalty needed, and it uses the per-feature `τ` QA-31 mandates. **A Nelson–Siegel basis is strictly worse** here, because it estimates decay rates freely from ~80 effective observations.

**This construction requires linearity** and so is incompatible with the GBDT stack — which is an argument for D as research (D-10), and the reason should be recorded rather than rediscovered. **One cheaper hybrid is available**: precompute the decay-scaled features `xᵢ · gᵢ(h)` with `gᵢ(h) = τᵢ(1−e^(−h/τᵢ))` and feed them to a GBDT alongside `h`. That supplies the structure without enforcing it — weaker than the linear form, but it keeps the existing stack.

 Run as research (D-10, P7-exempt); a negative result reshapes the whole question |

### Option E — Long-horizon selection + short-horizon timing

Fit the **ranker at the longest horizon** (what to own) and use short-horizon models **only for
entry and exit timing** (when to act).

| | |
|---|---|
| **Pro** | ★ **Matches the mandate exactly.** M-3's "hold winners, trim rather than exit" is a holding-period statement; L0 §12.1 says weeks-to-months. It also matches the two decisions actually being made, which are not the same decision. `buffett/signals/{entry_timer,sell_monitor}.py` already exist as the timing layer |
| **Con** | The selection model gets the worst effective-N of any design. Requires the timing layer to be specified rather than incidental. Two objectives to govern |
| **Verdict** | ★ **The mandate-aligned option — but run selection at 1m, not 1q** *(v0.3.0)*. As written, E fits the ranker at the longest horizon; if that is 1q, its core component is the one component §5.3b may prove unvalidatable. **1m clears the bar on the current panel** (t = 3.25 at IC = 0.03) and "weeks to months" (L0 §12.1) is satisfied at its short end by a 21-day objective. With the universe expanded to ~330 names (§5.3b), 1q selection becomes viable and E can move out. Either way the framing — *selection and timing are different problems* — should survive into whatever is chosen |

### Option F — Horizon-free path-shaped label

Replace forward return with a label describing the **shape of the forward path**: e.g. MFE/MAE
ratio (maximum favourable vs adverse excursion) over a window, or the path's Sharpe.

| | |
|---|---|
| **Pro** | ★ The system's actual output is **entry, stop and target** (the Discipline Card). An MFE/MAE label is *the same shape as the decision* — it directly encodes "did it run before it hurt me". One label covers timing and magnitude together |
| **Con** | Exotic. Harder to benchmark; less literature; needs a stated definition before it can be trusted (§8). Still has a window, so §5.3 still applies |
| **Verdict** | Research-tier. **The only option whose label matches what the card actually asks for**, and §9.3 returns to it. The principled version is López de Prado's **triple-barrier** labelling with barriers at `k·σ̂[t]·√h` — label difficulty constant across horizons (the classification analogue of QA-34) *and* literally a stop/target/time-limit structure, i.e. the Discipline Card's own shape.

**Three consequences of its endogenous span, recorded v0.3.0** — the barrier hits when it hits, so the label span is *random*:
1. **QA-33's power calculation is undefined** as written. There is no single `h` to substitute. The **realised mean label span** must be measured and reported as the effective `h`, never assumed.
2. **QA-37's uniqueness must use the full span-average definition** — which is exactly why that rule was corrected in v0.3.0.
3. ★ **F and D are mutually exclusive.** Triple-barrier labels are path-dependent and non-additive, so they cannot feed Option D's summation or QA-39's structural consistency. These are **alternative research tracks, not complementary ones** |

## 5.5 Build order — revised v0.3.0

> **v0.2.0's order was logically inverted.** It put the power calculation at step 1 and the `τ`
> measurement at step 2 — but the go/no-go power test *consumes* `IC(h)`, so it depends on the
> diagnostic it preceded. Corrected below, along with two further reorderings: **validation must be
> fixed before `τ` is estimated** (you cannot measure a decay curve honestly with leaky CV), and
> **the feature set must be settled before `τ` is estimated** (new features have their own `τ`, so
> a diagnostic run before them is invalidated by them).

| # | Step | Why here | Domain |
|---|---|---|---|
| ✅ **0** | ~~Mandate question (QA-2 / QQ-1)~~ — **DONE 2026-08-16.** HorizonSet v1 = `{1m production · 1w timing-only · 1q research}` (**§5.6**) | A decision, not a computation. It scoped everything below, and it did not wait on a measurement | **Victor — complete** |
| **0b** | **MDE table (§5.3b step one)** — smallest detectable IC per horizon | Needs **no** `τ`. Pure arithmetic, hours. Sets the bar the rest of the work must clear, and tells you immediately whether `n` needs to move | D-03 |
| **1** | **Fix validation** — purge, embargo, **uniqueness weighting**, deflated Sharpe | ★ *Moved up from 4.* Every number below, **including the `τ` estimate itself**, is unreliable under leaky CV. ⚠ Re-baseline: expect current numbers to fall | D-03 |
| **2** | **Fix the target** — vol-normalised, Yang–Zhang, **plus vol-neutralisation (QA-45)** | ★ *Moved up from 3.* `IC(h)` measured on raw returns is not the `IC(h)` of the target you will actually model | D-02 |
| **3** | **Multi-scale features** (~1×, 4×, 16× lookbacks) | ★ *Moved up from 5.* It **changes the feature set**, so a `τ` diagnostic run before it is invalidated by it. Also: some of the multi-horizon gain may be obtainable here with no architecture change at all | D-02 |
| **4** | **Measure `IC(h)`; estimate `τ` and `H` per feature** (QA-31, QA-32) | Now honest, on the final feature set and the final target | D-03 |
| **5** | **Go/no-go power test over the `(n, T)` grid**, using measured `IC(h)` (QA-33, QA-43, QA-44) | ★ *Moved down from 1.* **This is where QQ-3 actually closes** — on a measurement, not a placeholder. If 1q fails, the first response is **more names**, not more years | D-03 |
| **6** | **Baseline: Option A**, per-horizon single-task, on the corrected protocol | Now it means something | D-04 |
| **7** | **Option C + pinball loss** at multiple quantiles, with an explicit horizon loss-weighting policy (QA-46) | Smallest architecture change; keeps the GBDT stack; composes with §9.3 Option 3 | D-04 |
| **8** | **Research: linear parametric decay (D) *or* triple-barrier (F) — not both** | Mutually exclusive (Option F verdict). Pick on what step 4 shows | D-10 |
| **9** | *Only then* — Option B, consistency penalties | See the caveat below | D-04 |

> **Why GBDT and not a transformer at step 7.** Simple linear models beat transformer variants on
> many long-horizon forecasting benchmarks (Zeng et al. 2023), and tree ensembles still outperform
> deep learning on typical tabular data (Grinsztajn et al. 2022; Shwartz-Ziv & Armon 2022). Those
> benchmarks carry *far* higher signal-to-noise than cross-sectional equity returns, so the argument
> applies with more force here, not less. The neural branch must first beat the GBDTs at a
> **single** horizon before being asked to span three.

| ID | Rule |
|---|---|
| **QA-47** | ★ **The arbitration rule is explicit and lives in the HorizonSet (CT-3.1).** QA-40 identifies the real question — *which horizon nominates the daily pick* (INV-6) — and no option in §5.4 answers it. Under a selection/timing decomposition the rule is *implicit* (the selection horizon nominates; the timing horizon may delay or veto but never nominates), and **QA-1 forbids implicit**. A HorizonSet without a stated arbitration rule is incomplete |
| **QA-46** | A stacked or shared multi-horizon fit **declares its per-horizon loss weighting explicitly** in the HorizonSet (CT-3.1). Uniqueness weighting alone implies ≈ `h_max/h_min : 1` in favour of the short horizon; that ratio is a design choice and is recorded as one |

### A caveat on cross-horizon consistency penalties

A penalty of the form `Σ(ŷ[t,h₁+h₂] − ŷ[t,h₁] − ŷ[t+h₁,h₂])²` is intuitive and **wrong as stated**,
for two reasons this spec should record before anyone implements it:

1. **Information sets differ.** `ŷ[t+h₁,h₂]` is an expectation formed at `t+h₁`. The additive
   identity requires `E_t[·]` for both terms. By the tower property the relation holds *in
   unconditional average*, so the penalty is defensible as a dataset-level regulariser — but it is
   **not an identity per observation**, and treating it as one will penalise correct predictions.
2. **It conflicts with QA-34.** Volatility-normalised targets are **not additive**: dividing by
   `σ̂[t]·√h` destroys the additivity that the penalty relies on. Any implementation must
   un-normalise before applying it.

| ID | Rule |
|---|---|
| **QA-39** | A cross-horizon consistency constraint is applied **structurally** — by predicting a parametric decay curve (§5.4 Option D) — in preference to a penalty term. Where a penalty is used anyway, it operates on **un-normalised log returns** and is A/B tested, because horizons may legitimately disagree |
| **QA-40** | ★ **The portfolio-layer answer is not available to this system, and that is a deliberate constraint, not an oversight.** The standard professional resolution — convert each horizon's forecast to expected returns and let a cost-aware optimiser trade them off, so that horizons compete on *IC per unit of turnover* (Grinold & Kahn 2000; Gârleanu & Pedersen 2013) — requires an optimiser emitting a target allocation. **L0 §4.3 forbids exactly that** (M-2, INV-026), and INV-6 takes one actionable name per day rather than a portfolio. The surviving form of the insight: horizons are compared **net of turnover cost in D-03's evaluation protocol** (QA-12), and the question becomes *which horizon nominates the daily pick*, not *what weights to hold* |

## 5.6 THE HORIZON DECISION — **DECIDED 2026-08-16**

```text
╔══════════════════════════════════════════════════════════════════╗
║  HORIZON SET v1 — APPROVED BY VICTOR, 2026-08-16                 ║
║                                                                  ║
║      production   1m   (21 trading days)  — nominates            ║
║      timing-only  1w   ( 5 trading days)  — may delay or veto,   ║
║                                             NEVER nominates      ║
║      research     1q   (63 trading days)  — never reaches a      ║
║                                             human-facing artifact║
║                                                                  ║
║  1w is DEMOTED from nomination objective to timing input.        ║
║  It is never fitted as the ranker's target and never produces    ║
║  the daily actionable pick (INV-6, QA-47).                       ║
╚══════════════════════════════════════════════════════════════════╝
```

| | |
|---|---|
| **Decision** | HorizonSet v1 = `{ production: 21d · timing_only: 5d · research: 63d }` |
| **Decided by** | **Victor**, 2026-08-16 |
| **Why Victor and not this spec** | **QA-2** makes the horizon a mandate question; L0 §15 and `vision.md` §6 reserve mandate-derived decisions to the fund manager; **G-1** forbids design-tier reasoning from promoting one on its own. This spec recommended (v0.4.0 §5.6) and did **not** close it. **The decision below carries Victor's authority, not the document's** |
| **Reversibility** | ⚠ **Currently not evaluable — see the governance note below.** As stated: reopens only if both (a) measured `IC(1w) − IC(1m)` exceeds the cost differential **and** (b) M-4 is relaxed |

> ⚠ **Governance note, added v0.9.0 — the record should carry this next to the approval.**
> *(Raised by external review, 2026-08-17.)*
>
> **The decision is now supported by one substantive ground plus a mandate reading.** Ground (a)
> M-4 is substantive: it supplies a *consequence* (retroactive tax reclassification) that is not
> merely definitional. Ground (c) — "5 days is not weeks" — is a **direct reading of L0 §12.1's own
> wording**. It is a legitimate ground for a mandate-derived decision, but it does not
> *corroborate* (a); it restates that the mandate says what it says. Ground (b) is ⏸ indeterminate
> (§5.6a).
>
> Two consequences a future reader must not have to rediscover:
>
> 1. **If M-4 is ever relaxed, nothing substantive remains.** Victor approved a three-legged
>    argument; one leg is suspended and one is definitional.
> 2. **The reopening test cannot currently be evaluated**, because it compares against "the cost
>    differential", which is exactly the quantity §5.6a marks indeterminate. **The test becomes
>    evaluable when QQ-20 resolves** — and not before.
>
> **None of this makes the decision wrong.** M-4 was flagged as decisive from the outset and
> depends on none of the retracted arithmetic. But a decision whose reopening criterion cannot be
> evaluated is a decision that cannot be revisited on evidence, and that is worth knowing.
| **Cost of the decision** | It invalidates every trained model and every tuned hyperparameter fitted against `fwd_ret_1w` — including the rel5 3-c 25-sweep tuning and the fitted sleeve blend. **This is not free and was accepted knowingly** |

### Why this answer — the full reasoning, preserved

Three arguments converge, and **none waits on a measurement** — which is what made this a step-0
decision rather than a step-5 one, and why it could be taken before any of §5.5's build work.

#### Ground (a) — M-4 is the binding constraint, and its downside is asymmetric

This is the **decisive** argument; the other two are corroborating.

CRA's *carrying on a business* test weighs transaction frequency, period of ownership, time spent,
and intent. **A 5-day training target is a short-hold objective by construction** — optimising it
manufactures exactly the pattern the test looks for, and it does so *systematically*, which is worse
than doing it occasionally by discretion.

The asymmetry is what settles it:

- **Upside of a 1w objective:** somewhat better statistical power (MDE 0.0135 vs 0.0277) and higher
  gross IR from greater breadth.
- **Downside:** business-income treatment of registered-account gains, **applied retroactively**,
  across years of trading. Not a drawdown — a reclassification.

**No backtest argues out of that**, because the exposure is not a market risk and is not diversified
away by being right. M-4 already states the behaviour is *"being actively reduced"*; training the
model to produce it would have contradicted the mandate directly rather than merely sitting
uncomfortably beside it.

#### Ground (b) — cost ⏸ **INDETERMINATE, pending QQ-20** *(status corrected v0.8.0)*

> **v0.7.0 marked this WITHDRAWN. That overcorrected.** The evidence does not show the argument
> fails — it shows **the sign is unknown and flips on a quantity of 3–12 bps that nobody has
> measured.** Withdrawn is hard to reinstate; suspended is what QQ-20 is for. *(Correction from
> external review, 2026-08-17.)*
>
> The original text claimed `16 bps one-way ⇒ 32 bps round trip` and a **12.3 %** annual
> differential, sourced to a `spread + slippage + commission` sum that is **dead code**. That
> attribution is wrong and stays retracted. What replaces it is **not a counter-result but an
> absence of one** — see **§5.6a**, which records the flip-back threshold so QQ-20 has a stated bar
> to be measured against rather than a re-derivation.
>
> **The decision stands on grounds (a) and (c)** either way. Ground (a) was always stated as
> decisive and depends on none of this arithmetic.

#### Ground (c) — the stated mandate

L0 §12.1: holding period **"medium-term (weeks–months); hold winners, trim rather than exit
(M-3)"**. Five trading days is not "weeks". Twenty-one is the short end of the stated range and
squarely inside it. The previous objective was not merely suboptimal — **it was outside the written
mandate**, and had been since the mandate was written.

#### What was given up, stated plainly

**1w has genuinely better statistical power.** MDE(t>3) of 0.0135 versus 0.0277 — a 1m signal must
be roughly twice as strong to be detectable on the same panel. That is a real cost of this decision
and it was accepted: **a detectable edge that cannot be traded profitably after cost, and that
carries tax reclassification risk, is not an edge.**

#### The structural result that outlives the decision

Since gross `∝ (1−e^(−h/τ))/h` and drag `∝ 1/h`, net `∝ [K(1−e^(−h/τ)) − 252c] / h`, and the bracket
**increases** with `h` while being negative for small `h`:

```text
╔══════════════════════════════════════════════════════════════════╗
║  THERE IS A MINIMUM VIABLE HORIZON SET BY TRANSACTION COST       ║
║  ALONE, BELOW WHICH NO IC IS LARGE ENOUGH TO PAY FOR ITSELF.     ║
║                                                                  ║
║  It depends on tau and on cost per round trip — not on the       ║
║  model, the features, or the architecture. Compute it at build   ║
║  step 4 and record it in the HorizonSet: it bounds every option  ║
║  in §5.4 from below, before any of them is fitted.               ║
║                                                                  ║
║  This decision is one instance of that bound. The bound itself   ║
║  survives any later change of model or feature set.              ║
╚══════════════════════════════════════════════════════════════════╝
```

### Consequences — what this decision changes downstream

| # | Consequence | Where it lands |
|---|---|---|
| 1 | **Every deployed model is now fitted to a timing objective, not a selection one.** `pipeline/ohlcv/**` trains on `fwd_ret_1w`; nothing is retroactively wrong, but the live ranker is no longer fitted for the job the decision assigns it | D-04; a **retrain is required** before 1m ships |
| 2 | **Tuning must be redone.** The rel5 3-c sweep and the fitted sleeve blend (`policy_params.json` = `{rank 0.5, return 0.3, prob 0.2}`) were fitted at 5 days | D-04, D-10 |
| 3 | **The timing leg is promoted from heuristic to model leg.** `buffett/signals/{entry_timer,sell_monitor}.py` become load-bearing rather than peripheral | D-03 §6, D-04 |
| 4 | **QQ-2's decomposition axis is settled by implication** — "selection at the longer horizon, timing at the shorter" **is** HorizonSet v1 restated as an architecture (§5.4 Option E) | §5.6 QQ-2 below |
| 5 | **QQ-3 is de-risked.** With 1m in production, 1q stops being a dependency and becomes a promotion candidate | §15 |
| 6 | **QA-46 becomes more urgent.** If C stacks `{5,21,63}` and uniqueness weighting gives the 1w copies ~12.6× the weight by default, the fit silently optimises for the horizon just retired | §5.4 Option C |
| 7 | ⚠ **INV-6's cadence needs re-examination.** "Exactly one actionable recommendation per day" was written when the objective was 5 days. At a 21-day objective the top-1 changes slowly, so daily nomination either repeats the same name for stretches or churns against its own horizon | **QQ-15 — raised, not resolved** |
| 8 | ⚠ **The cost assumption is now load-bearing and is currently an estimate.** The whole of ground (b) rests on 32 bps round trip from config, not from fills | **QQ-14 — measurable from D-11's trade log** |

### QQ-1 — the recommendation that was approved

Three independent arguments converge, and **none waits on a measurement** — which is what makes this
a step-0 decision rather than a step-5 one.

**(a) M-4 is the binding constraint, and it is asymmetric.** CRA's *carrying on a business* test
weighs transaction frequency, period of ownership and intent. **A 5-day training target is a
short-hold objective** — optimising it manufactures precisely the pattern the test looks for. The
downside, business-income treatment of registered-account gains applied retroactively, is far worse
than the foregone alpha, and no backtest argues out of it. M-4 already states the behaviour is
*being actively reduced*; training the model to produce it contradicts the mandate directly.

**(b) Cost — ⚠ withdrawn as written; see §5.6a.** The corrected analysis does not support the
decision. Grounds (a) and (c) are unaffected and are sufficient.


**(c) L0 §12.1** — "weeks–months". Five days is not weeks; twenty-one days is the short end of the
stated range and squarely inside it.

#### The counterargument in full — and why it loses

Two real points cut the other way, and any comparison omitting them is incomplete:

1. **1w has the best statistical power** — MDE(t>3) 0.0135 versus 0.0277 at 1m.
2. **Shorter horizons carry more breadth.** Per §5.3b's correction, `BR ≈ BR_eff × 252/h`, so 1w has
   4.2× the annual breadth of 1m — a `√4.2 ≈ 2.05×` multiplier on IR.

Under the decay law `IR(h) ∝ (1−e^(−h/τ))/h`, so **gross IR does favour short horizons
monotonically**. Illustratively at `τ = 30 d`, `σ_p = 25 %`, repo costs:

| `BR_eff` | horizon | gross | drag | **net** |
|---|---|---|---|---|
| 5 clusters | 1w | 11.9 % | 16.1 % | **−4.2 %** |
| | **1m** | 9.3 % | 3.8 % | **+5.5 %** |
| | 1q | 5.4 % | 1.3 % | +4.1 % |
| 20 clusters | 1w | 23.8 % | 16.1 % | **+7.7 %** |
| | **1m** | 18.6 % | 3.8 % | **+14.8 %** |
| | 1q | 10.8 % | 1.3 % | +9.5 % |

**1m wins net under both breadth assumptions.** 1w's gross advantage is real but ~2–6 points against
a ~12-point drag differential. *(Illustrative, not decisive: it assumes `τ = 30`, and `τ` is exactly
what step 4 measures.)*

A structural result falls out. Since gross `∝ (1−e^(−h/τ))/h` and drag `∝ 1/h`, net
`∝ [K(1−e^(−h/τ)) − 252c] / h` — and the bracket **increases** with `h` while being negative for
small `h`:

```text
╔══════════════════════════════════════════════════════════════════╗
║  THERE IS A MINIMUM VIABLE HORIZON SET BY TRANSACTION COST       ║
║  ALONE, BELOW WHICH NO IC IS LARGE ENOUGH TO PAY FOR ITSELF.     ║
║                                                                  ║
║  It depends on tau and on cost per round trip — not on the       ║
║  model, the features, or the architecture. Compute it at step 4  ║
║  and record it in the HorizonSet: it bounds every option in      ║
║  §5.4 from below, before any of them is fitted.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Proposed HorizonSet v1** — `{ production: 21d · timing-only: 5d · research: 63d }`, with 1w
demoted from *nomination objective* to *timing input*: never fitted as the ranker's target, never
nominating the daily pick (QA-47). **Reopens if** measured `IC(1w) − IC(1m)` at step 4 exceeds the
cost differential **and** M-4 is relaxed — both, not either.

> **This also de-risks QQ-3.** With 1m in production, the 1q question stops being load-bearing — it
> becomes a *promotion candidate* rather than a dependency.

## 5.6a The cost argument, corrected — **ground (b) does not survive**

> **Found 2026-08-17.** An external review flagged that §9.1.1 called `c` a *round-trip* cost while
> §5.6 called the same 16 bps *one-way*. Both cannot be right. Chasing it down showed the
> inconsistency was the smallest of three errors.

### Error 1 — the cited formula is dead code

```python
# label_builder.py:69-78
costs = config.get("costs", {})
if "cls_threshold_bps" in costs:          # ← config/settings.yaml:247 sets this to 16
    total_bps = costs["cls_threshold_bps"]
else:                                     # ← DEAD. Never executes.
    total_bps = spread 5 + slippage 10 + commission 1
```

`settings.yaml` sets `costs.cls_threshold_bps: 16` **directly**, so the `5 + 10 + 1` sum never
runs. The threshold is a **hard-coded 16 bps that happens to equal that sum**. Both §5.6 and
§9.1.1 described its provenance as a decomposition of spread, slippage and commission. It is not
one — and a threshold with no stated derivation is exactly what **QA-22** exists to catch.

### Error 2 — one-way vs round-trip was never declared, so neither reading is "the repo's"

The config carries no per-side convention. The reviewer was right that both documents cannot be
right; **the deeper answer is that neither was reading the repository, because the repository does
not say.**

### Error 3 — **the backtester does not use a bps cost model at all** ★

```python
# backtester.py:14-18
# BROKER REALITY: flat $10 per trade (entry or exit), regardless of size.
# DO NOT replace with proportional/bps-based fees — this is not a model
# assumption, it is the actual fee charged by the broker on this account.
FLAT_TRADE_FEE_DOLLARS = 10.0
```

```yaml
# settings.yaml:55
charge_transaction_cost: false     # §3b.5 — $20 round-trip immaterial at realistic capital
```

**The cost of record is a flat $10 per trade — $20 per round trip — and it is charged nowhere by
default.** A flat fee does not scale with position size, so the drag in percentage terms depends on
the **book**, which the bps framing hid completely.

### The corrected drag

`drag = N × (252 / h) × $20 / book`, at the current sleeve policy `N = 5`:

| Book | 1w (h=5) | 1m (h=21) | 1q (h=63) | **1w − 1m** |
|---|---|---|---|---|
| $100,000 | 5.04 % | 1.20 % | 0.40 % | **3.84 %** |
| $250,000 | 2.02 % | 0.48 % | 0.16 % | **1.54 %** |
| $500,000 | 1.01 % | 0.24 % | 0.08 % | **0.77 %** |
| $1,000,000 | 0.50 % | 0.12 % | 0.04 % | **0.38 %** |

*(against §5.6's claimed 16.13 % / 3.84 % / 1.28 % and a 12.3 % differential — overstated by
3× to 32× depending on book size)*

### And the conclusion reverses

Applying §5.6's own gross figures to the real cost model:

| `BR_eff` | book | net 1w | net 1m | winner |
|---|---|---|---|---|
| 5 | $100 k | 6.86 % | **8.10 %** | 1m |
| 5 | $250 k | **9.88 %** | 8.82 % | **1w** |
| 5 | $500 k | **10.89 %** | 9.06 % | **1w** |
| 20 | $100 k | **18.76 %** | 17.40 % | **1w** |
| 20 | $250 k | **21.78 %** | 18.12 % | **1w** |
| 20 | $500 k | **22.79 %** | 18.36 % | **1w** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THAT TABLE USES COMMISSION-ONLY COSTS.                          ║
║                                                                  ║
║  v0.7.0 captioned it "the repository's ACTUAL cost model".       ║
║  It is the repository's actual COMMISSION model. backtester.py's ║
║  comment — "the actual fee charged by the broker" — is a true    ║
║  statement about COMMISSION being read as a statement about      ║
║  TRANSACTION COST. Spread and slippage are paid to the market,   ║
║  not to the broker, and that comment says nothing about them.    ║
║                                                                  ║
║  Running a horizon comparison on a cost model that omits the     ║
║  proportional component is exactly what QA-49 forbids — a rule   ║
║  written thirty lines below the table that broke it.             ║
╚══════════════════════════════════════════════════════════════════╝
```

### The flip-back threshold — the bar QQ-20 must clear

*(Added v0.8.0 after external review, which supplied this analysis.)*

Proportional cost `cf` per round trip gives `drag(h) = 252·cf/h`, so the 1w−1m gap is
**`38.4 · cf`**. The sign of ground (b) therefore flips at `cf = G / 38.4` for a gross gap `G`:

| `BR_eff` | gross gap `G` | flips at `cf` | book | commission-equiv | **spread+slippage needed to restore 1m** |
|---|---|---|---|---|---|
| 5 | 2.60 % | 6.8 bps | $100 k | 10.0 bps | *(already 1m — commission alone clears it)* |
| 5 | 2.60 % | 6.8 bps | $250 k | 4.0 bps | **2.8 bps** |
| 5 | 2.60 % | 6.8 bps | $500 k | 2.0 bps | **4.8 bps** |
| 20 | 5.20 % | 13.5 bps | $100 k | 10.0 bps | **3.5 bps** |
| 20 | 5.20 % | 13.5 bps | $250 k | 4.0 bps | **9.5 bps** |
| 20 | 5.20 % | 13.5 bps | $500 k | 2.0 bps | **11.5 bps** |

**Every reversed scenario flips back at ≤ 11.5 bps round trip — under 6 bps per side.** Effective
half-spread plus market-order slippage on liquid US large caps sits routinely in that range.

```text
╔══════════════════════════════════════════════════════════════════╗
║  SO "FIVE OF SIX FAVOUR 1w" IS NOT A FINDING ABOUT HORIZONS.     ║
║  IT IS A FINDING ABOUT WHAT WAS LEFT OUT OF THE SUM.             ║
║                                                                  ║
║  Ground (b) is INDETERMINATE, not refuted. The threshold above   ║
║  is the bar: measure spread + slippage from D-11's trade log     ║
║  (QQ-20), compare against 3-12 bps, and ground (b) resolves      ║
║  one way or the other without re-deriving anything.              ║
╚══════════════════════════════════════════════════════════════════╝
```

### ⚠ Third correction — the commission drag is HORIZON-INVARIANT

*(Found 2026-08-17 while implementing QA-62's flip. Third time §5.6a's cost table has been wrong,
and the correction that removes commission from the argument entirely.)*

```python
# backtester.py:110-111
bucket_capital = self.initial_capital / self.horizon_days
self.buckets = [PortfolioBucket(bucket_capital) for _ in range(self.horizon_days)]
```

**The bucket count equals the horizon.** So rolls per year `= h × (252/h) = 252` — the bucket count
cancels the roll frequency exactly:

| h | buckets | rolls/yr each | **total rolls/yr** | cost/yr | drag @ $20 k |
|---|---|---|---|---|---|
| 5 (1w) | 5 | 50.4 | **252** | $5,040 | **25.2 %** |
| 21 (1m) | 21 | 12.0 | **252** | $5,040 | **25.2 %** |
| 63 (1q) | 63 | 4.0 | **252** | $5,040 | **25.2 %** |

Every prior version of this table — including v0.9.0's "corrected" one — assumed `N = 5` **fixed**
while `h` varied. **The code scales `N` with `h`.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  UNDER THE ACTUAL ARCHITECTURE, COMMISSION CONTRIBUTES EXACTLY   ║
║  NOTHING TO THE HORIZON COMPARISON. THE DIFFERENTIAL IS ZERO.    ║
║                                                                  ║
║  Ground (b) is therefore not merely indeterminate in MAGNITUDE.  ║
║  Its commission component is zero BY CONSTRUCTION, and only the  ║
║  unmeasured PROPORTIONAL part (spread + slippage, QQ-20) could   ║
║  ever have supported or opposed the decision either way.         ║
║                                                                  ║
║  Every "1w vs 1m" commission figure in §5.6, v0.7.0 and v0.9.0   ║
║  was an artefact of an assumption about bucket count that the    ║
║  code does not make.                                             ║
╚══════════════════════════════════════════════════════════════════╝
```

### ⚠ And the capital base is a hard-coded magic number

```python
self.initial_capital = 20000.0        # backtester.py:107 — not config, not a parameter
```

At **$20,000** the `$20` round trip is **50 bps** of a 1w position (5 buckets × $4,000) and
**210 bps** of a 1m position (21 buckets × $952). `settings.yaml`'s claim that *"$20 round-trip
[is] immaterial at realistic capital"* is **false at this repository's own capital** — by two orders
of magnitude at 1m.

> **This is a design blocker for the 1m retrain, not a cost footnote.** 21 buckets of $952 with a
> flat $10 per trade is **2.1 % per round trip**; commission alone would destroy a 1m policy that
> keeps `buckets == horizon_days`. **The bucket architecture must change at 1m**, and that decision
> — not the fee flag — determines whether cost bears on the horizon. It also collides with **M-2**:
> 21 equal sleeves is a far more diversified book than 5, and the concentration is deliberate.
> **QQ-21.**

| ID | Rule |
|---|---|
| **QA-63** | ★ **`initial_capital` is configuration, not a literal.** A hard-coded capital base makes every percentage cost figure in the repository unfalsifiable, and it is what let *"immaterial at realistic capital"* go unchecked for as long as it did. Pinned in the BacktestSpec (§7.1, QA-11) and read from D-11 (**QA-107**) |
| **QA-114** | ⚠ **`backtester.py:107` IS DELIBERATELY NOT FIXED.** *(Decided 2026-08-18.)* `pipeline/ohlcv/backtest/**` is **replaced, not repaired** — this whole spec set exists to build `src/quant/`, and patching a literal in the legacy tree spends effort on code scheduled for deletion while leaving the rule un-enforced where it will actually matter. ★ **The finding is retained as the EVIDENCE for QA-63/QA-107; the fix lands in the new backtest only.** Same disposition as `L1-orchestration.md` §1.5's rebuild inventory |
| **QA-115** | ★ **The new backtest reads its capital base from D-11 and records it in the `BacktestResult`**, not only in the spec. ★ **Two backtests that differ only in an unstated capital base are not comparable** (§7.1), and the way that defect survived for months was that the number appeared in neither the input nor the output — only in a source line nobody read |
| **QA-64** | ★ **A cost model whose per-horizon drag is invariant cannot be used as a horizon argument** — and whether it *is* invariant depends on the **rebalance architecture**, not on the fee schedule. Any cost-based horizon claim must state its assumed bucket/position count and show the `h`-dependence explicitly |

### Two further understatements, both pushing the same way

**Trims are trades — and the fee model charges nothing for them.** *(Verified against the code
2026-08-17, after external review raised it as a question.)*

```python
# backtester.py  _reconcile_bucket  — docstring: "Held positions incur no fee."
for ticker in bucket.positions:
    if ticker not in target_tickers:  total_fees += FLAT_TRADE_FEE_DOLLARS   # EXIT
for ticker in target_tickers:
    if ticker not in bucket.positions: total_fees += FLAT_TRADE_FEE_DOLLARS  # ENTRY
```

Both tests are **set membership**. A ticker present in both dicts **with a changed weight** — which
is precisely a trim — incurs **`$0`**. `N × 252/h` counts *round trips*, not trades; a trim-based
policy generates 3–4 trades per position cycle rather than 2, so the flat-fee drag is understated
by **50–100 %** before spread and slippage enter at all.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE GAP IS LATENT TODAY AND BECOMES LOAD-BEARING EXACTLY WHEN   ║
║  THE MANDATE'S INTENDED BEHAVIOUR IS IMPLEMENTED.               ║
║                                                                  ║
║  The current sleeve policy is top-1 per sleeve: a sleeve either  ║
║  holds a name or swaps it whole. There are NO TRIMS, so          ║
║  "trims are free" costs nothing right now.                       ║
║                                                                  ║
║  M-3 says the fix for pyramiding is to "sell less and let        ║
║  winners run" — TRIM RATHER THAN EXIT. The moment that policy    ║
║  ships, trimming becomes the fund's dominant action, and the     ║
║  cost model charges ~nothing for the fund's main activity.       ║
║                                                                  ║
║  So this is not a reason to delay QA-50's flip. It is a reason   ║
║  to fix the fee model BEFORE the policy changes.                 ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **QA-61** | ★ **The cost model charges per TRADE, not per position change of membership.** A weight change on a held name is a trade and is charged. A model that prices only entries and exits is structurally blind to the exact behaviour **M-3 mandates**, and will report a trim-based policy as cheaper than a swap-based one when it is more expensive |

**And the config used as ground truth is itself non-compliant.** §5.6a leans on
`charge_transaction_cost: false` as evidence of what the repository currently models, while
**QA-50** requires that same setting to be `true`. Both stand, on different clocks: the
configuration is evidence of the *present*, the rule states the *required* end state. See QA-50.

### What is actually unknown

The flat fee is **commission only**. **Spread and slippage are modelled nowhere in this
repository** — and those are precisely the proportional costs that scale with turnover. The true
differential sits between **~0.4 %/yr** (commission alone, $1 M book) and **~12 %/yr** (if real
spread + slippage is of order 16 bps one-way). **Nobody has measured it** — **QQ-20**.

| ID | Rule |
|---|---|
| **QA-48** | ★ *(extended v1.0.0)* **The cost model is declared explicitly**, per component, with its **per-side convention** stated: commission (flat or bps), spread, slippage, and whether each figure is one-way or round-trip. **A flat-fee component additionally declares the `initial_capital` it is a percentage of** — a flat fee has no percentage meaning without one. A cost number without a stated convention is not usable in an argument, and §5.6, §9.1.1 and `settings.yaml:55` are three proofs |
| **QA-49** | **Proportional costs (spread, slippage) are modelled, not omitted.** A backtest that charges only a flat commission understates turnover-sensitive strategies **specifically**, which is the exact comparison a horizon decision turns on |
| **QA-50** | ★ **`charge_transaction_cost` MUST default to `true`.** *(Reversed v0.9.0 — see below.)* A backtest accounts for whatever cost model exists, and the result records **which components were charged** (`costs_charged: commission_only` until QA-49 lands, `full` after). **QA-49 stays open independently** — charging commission is not charging cost |
| **QA-50a** | A backtest result records `costs_charged ∈ {none, commission_only, full}` **on its face**. A result omitting a cost component must say which — silence is never permitted (QA-12) |
| **QA-69** | ★ **Execution cost is measurable only if the ARRIVAL QUOTE is captured at order submission** — `(ticker, submit_ts, bid, ask, last, size, order_type)`. A broker export gives the fill and not the reference, so **retrospective measurement is impossible** and every un-captured trading day is permanently lost. Capture starts **before** the domain that will consume it is specified. The reference is the **arrival** price, never the decision price: implementation shortfall splits into *delay* (decision→arrival, a process defect) and *execution* (arrival→fill, which is QQ-20), and conflating them measures overnight drift rather than execution |
| **QA-70** | **A trade log records its own measurement quality per row.** A *retrospective* segment reconstructed from broker exports has exact commission and **no** execution cost; a *forward* segment with arrival quotes has both. **They may not merge into one table that implies uniform quality** — that is DE-35's rule (`UNCHECKED` is never "none") applied to cost |

> ⚠ **v0.8.0 closed this the other way and was wrong.** It ordered QA-49 *before* QA-50, arguing
> that flipping the flag today would charge commission only — *"the same defect one layer down"* —
> and would make QA-49's violation harder to see. **Both halves fail.** *(Reversal argued by
> external review, 2026-08-17; the asymmetry below is what settles it.)*
>
> **On accuracy.** Commission-only understates cost by perhaps 50–70 %. **Zero understates it by
> 100 %.** Flipping is strictly more accurate, immediately. QA-12 / INV-016 is a rule about
> **backtest accuracy**, not about audit legibility.
>
> **On visibility.** That concern is already met by the `costs_charged` field the same rule
> mandates. `costs_charged: commission_only` is exactly as legible as `costs_charged: none`, and it
> does not require the number to stay wrong in order to keep the gap conspicuous.
>
> **And the bias is not neutral — it runs in the direction of the open question:**
>
> | Book | uncharged 1w | uncharged 1m | **bias toward the SHORT horizon** |
> |---|---|---|---|
> | $100 k | 5.04 %/yr | 1.20 %/yr | **3.84 pts** |
> | $250 k | 2.02 %/yr | 0.48 %/yr | **1.54 pts** |
>
> Charging zero does not merely understate — it understates **asymmetrically, in favour of the
> shorter horizon**, which is precisely the comparison ground (b) turns on. Every backtest run
> between now and QQ-20's resolution inherits that bias. **Preserving a known 100 % understatement
> to keep a defect conspicuous optimises for the wrong thing.**
>
> ⚠ **The config change is not applied here.** `config/settings.yaml:55` still reads `false`. It is
> a production change needing Victor's go-ahead and the SDD loop, not a side effect of a spec edit.
> **The spec's normative position is settled; the code change is an open task — and the sequencing
> below is part of the position.**

#### How the flip should land — v1.0.0

> **The decisive argument is one neither §5.6a nor v0.9.0 made: the invalidation cost is already
> sunk.** *(External review, 2026-08-17.)*

v0.9.0 hesitated because flipping *"changes every backtest number in the repository."* **But §5.6's
consequences #1 and #2 already require exactly that** — every deployed model is fitted against
`fwd_ret_1w`, and the blend `{0.5, 0.3, 0.2}` and the rel5 3-c sweep were tuned at 5 days. All of
it is already dead under HorizonSet v1.

**Everything the flip would invalidate is already invalidated.** So the marginal disruption is
**zero**, and the choice is only between paying the re-baseline **once** (flip now, with the
retrain) or **twice** (flip later, and let the intervening numbers be used for decisions in
between).

The flip is also **weakly dominant**: at any capital level it moves the backtest from 0 % of cost
charged to 50–70 %. **There is no book size at which charging nothing is more accurate than
charging the commission actually paid.**

| ID | Rule |
|---|---|
| **QA-62** | ★ **The flip ships with the 1m retrain, not standalone**, and with three things attached: (i) a **known-answer test** — the `charge_fees=True` path is **exercised nowhere in the suite today** (only `test_sleeve_policy.py` sets it, to `False`), so a dormant branch would be trusted on its first production run; (ii) **`initial_capital` pinned** in the spec (QA-11, §7.1); (iii) **`costs_charged: commission_only`** on every result (QA-50a). QA-49 and QA-61 stay open |

> **Why (i) is not optional.** `test_flat_trade_fee.py` exercises `_reconcile_bucket` — the fee
> *computation* — but nothing exercises `capital -= rebalance_cost` at `backtester.py:267`. A
> reachable-but-never-executed branch being trusted is the **D-18(c) shape**, one step milder:
> there the producing branch could not run at all; here it simply never has. The known-answer test
> is a single-position, single-round-trip backtest whose result must move by **exactly $20**.

> **And accept a second re-baseline later.** When QQ-20 resolves and spread, slippage and QA-61's
> trim charge land, the numbers move again. Waiting for that in order to avoid one re-baseline
> means **waiting on an unscheduled dependency to avoid work that is happening anyway.**


### QQ-2 — recommend, on both axes

**Decomposition: Option E, selection at 1m.** Follows mechanically from QQ-1 — "selection at the
longer horizon, timing at the shorter" **is** HorizonSet v1 restated as an architecture, not a
separate choice. E therefore stops competing with A/B/C and becomes **the frame they sit inside**.
`buffett/signals/{entry_timer,sell_monitor}.py` already exist as the timing leg.

**Estimation, selection leg: A first, then C — and C's justification changes.** §5.4 sells C as "one
model spans three horizons". **Under QQ-1 only one horizon ships, so that value largely evaporates.**
C's remaining case is different and better: **stacking `{5, 21, 63}` lets the 1m head borrow strength
from the horizons that are not shipping** — the 1w rows carry ~12.6× the effective evidence, and
horizon-conditioning is how a 1m fit reaches them without inheriting 1w's turnover.

That sharpens the test: **C wins if it beats A *at 1m specifically*** — not if it produces plausible
forecasts at all three. And it makes **QA-46 more urgent, not less**: if uniqueness weighting hands
the 1w copies 12.6× the weight by default and only the 1m head ships, the fit is silently optimising
for a horizon that was deliberately retired.

**Estimation, timing leg: F / triple-barrier — and this is where F belongs.** Its problems are severe
when it labels the *ranker* and mild when it labels the *timer*: a timing model faces no
cross-sectional power test (it is judged on hit rate conditional on entry), so the undefined-`h`
objection dissolves. And the timing decision genuinely *is* a barrier question — enter now or wait,
exit now or hold — with the Discipline Card's stop / target / time-limit as literally the same object.

**Research: D** (linear per-feature decay) — precisely what would promote 1q out of research.
**B stays at step 9**; per its own amended verdict the nesting it would exploit is better handled by D.

| Leg | Recommendation | Authority |
|---|---|---|
| Decomposition | **E**, selection at 1m | mandate consequence ⇒ **Victor** (QA-2, G-1) |
| Selection estimation | **A** baseline → **C + pinball**, judged **at 1m** | **D-04**, on D-03's protocol |
| Timing estimation | **F / triple-barrier** | D-04 |
| Research | **D** (linear per-feature decay) | D-10 |

---

## 5.7 QQ-18 CLOSED — normalise for the loss, de-normalise for the decision

> **Closed 2026-08-17 as a D-03/D-04 design decision.** Unlike QQ-1 this is **not** mandate-derived,
> so QA-2/G-1 do not reserve it to Victor — but it has a *mandate consequence* (QA-45), and it sits
> **inside CT-3.1, a consumed contract**. Left open it would be settled silently by whoever
> implemented first. *(Urgency flagged by external review, 2026-08-17.)*

### The question

QA-34 makes the target `Z_i = R_i / (σ̂_i √h)`. §9.1.5 posed two branches: normalise `y^rank` too
(Claim 3 survives, but the ranking becomes risk-adjusted and QA-45's low-volatility tilt lands in
the selection decision), or normalise only the regression target (Claim 3 breaks).

### Both branches are false alternatives

They conflate two different uses of the normalisation:

| Purpose | Needs normalisation? |
|---|---|
| **Conditioning the loss** — comparable scale across names, dates and horizons; stops the fit spending capacity on volatility (QA-34) | **Yes.** This is the whole point of QA-34 |
| **Ordering the cross-section** — deciding which name to nominate | **No.** Nothing requires the *decision* to inherit the *loss's* parameterisation |

So: **fit on `Z`, predict `Ẑ`, and rank on `Ẑ_i · σ̂_i √h`** — back in return units. The fit is
well-conditioned; the ranking is a raw-return ranking; the volatility division cancels at the
decision boundary rather than propagating into it.

| ID | Rule |
|---|---|
| **QA-58** | ★ **Volatility normalisation is a property of the loss, not of the decision.** Models are fitted on `Z = R/(σ̂√h)`; any output used to **order or nominate** is de-normalised to return units (`× σ̂√h`) before ranking. Which quantity is being ranked is declared in the HorizonSet (CT-3.1) — never left to the implementation |
| **QA-59** | **QA-45 becomes the check, not the fix.** IC is reported conditional on volatility decile to confirm the tilt has leaked in neither direction. A ranking that is *deliberately* risk-adjusted is a legitimate design — it is just not this one, and it would need its own mandate justification against M-2 |

### QA-58 is tilt-*correcting*, not tilt-neutral — stronger than first stated

*(Added v0.9.0. Argument supplied by external review, 2026-08-17.)*

§5.7 as first written presented de-normalisation as **avoiding** a tilt. It also **removes one that
exists today**, and that is the stronger claim.

Write `R_i = μ_i + ε_i` with `ε_i ~ (0, σ_i²)` and let the predictable part scale with volatility,
`μ_i = σ_i · m_i`. Any regularised fit attenuates the signal by the local signal-to-noise ratio:

```
    fit on raw R :   μ̂_i ≈ κ_i · μ_i ,  κ_i DECREASING in σ_i    → non-uniform attenuation
    fit on Z     :   Ẑ_i ≈ λ  · m_i ,  λ  a SINGLE constant      → uniform attenuation
                     Ẑ_i · σ̂_i √h ≈ λ · μ_i
```

Normalising makes the noise homoskedastic, so shrinkage is uniform across names. **Fitting on raw
returns therefore already under-ranks high-volatility names relative to their true expected
return** — a low-volatility tilt arriving from the *fit*, not from the target definition, and
present in the incumbent regressor today.

So QA-58 does not merely decline to introduce a tilt; **it corrects one**. That changes the case
from "avoids a new problem" to "fixes an existing one", and it is a second, independent argument
for QA-34 that has nothing to do with horizon comparability.

> **Note it is a theoretical argument, not a measurement.** It also sits *beside* §9.1.2(b)'s
> observation that L2 on raw returns is **tail-dominated**: the two are different mechanisms and
> both hold — the fit spends capacity on high-volatility names while extracting proportionally
> less signal from them. **Recorded as V-18**, to be checked rather than assumed.

> **This also resolves V-14's second face.** The reviewer noted that if the quantile heads are fitted
> on QA-34 targets, `P50` is a **median Sharpe**, so `rank_score = P50` would be QA-45's low-vol tilt
> entering selection through the back door — QQ-18 branch (i) and V-14 arriving from opposite
> directions. Under QA-58 the quantile heads are de-normalised before use, so `P10/P50/P90` come
> back as a **price band** (which is what the Discipline Card needs anyway) rather than a Sharpe
> band. **One rule closes both.**


---

## 5.8 QQ-21 — the bucket architecture is not a free parameter

> **Reframed 2026-08-17 after external review, with two corrections to that review.** §5.6a
> presented QQ-21 as an open design choice. **It is mostly forced arithmetic**, and the part that
> *is* free turns out to be a knob that already exists in the code and is set to zero.

### 5.8.1 It is Little's Law

```
        N  =  λ · h
```

`λ` = rate at which nominations are **acted on** (per day) · `h` = holding period (days) ·
`N` = positions held at steady state. This is Little's Law and it holds for any system in
equilibrium.

Set `λ = 1/day` (INV-6 as currently read) and `h = 21`, and **`N = 21` whether you want it or
not.** `buckets == horizon_days` at `backtester.py:111` is not an implementation choice that
happened to be made — **it is `N = 1 × h` written down.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  QQ-21 IS NOT "HOW MANY BUCKETS?"                                ║
║                                                                  ║
║  It is: WHICH OF THE THREE DO YOU BREAK?                         ║
║                                                                  ║
║     daily action (INV-6)  ·  21-day holding (M-4, L0 §12.1)      ║
║                    ·  concentrated book (M-2)                    ║
║                                                                  ║
║  N=5, lambda=1, h=21 is ARITHMETICALLY IMPOSSIBLE.               ║
╚══════════════════════════════════════════════════════════════════╝
```

> ★ **This also unifies QQ-21 and QQ-15.** QQ-15 asked how INV-6's daily cadence squares with a
> 21-day objective. **The answer is Little's Law, and the bucket count is where it surfaces in
> code.** They are one question, and closing one closes the other.

### 5.8.2 Correcting the M-2 attribution

§5.6a said QQ-21 "collides with M-2". **Wrong target.** The fee schedule and M-2 point the *same*
way — both favour **fewer, larger** positions. The collision is between **the ladder and M-2**, and
what forces the ladder is **INV-6's daily action cadence**.

> **You are not trading concentration against cost. You are trading *cadence* against both.**

### 5.8.3 The minimum viable position — and a correction to the σ

A flat fee sets a floor on position size, which caps `N` directly. From §9.1.6a, one unit of
`opportunity` is worth `β = 26 bps` of expected 21-day return, and the top-ranked name sits at
roughly the expected maximum of `n` standard normals.

> ⚠ **The review used 2.8σ for n = 130. Measured, it is 2.60σ** (200 k simulations); 2.8 corresponds
> to `n ≈ 300`. The asymptotic formula gives 2.46 and understates at moderate `n`, which is probably
> the source of the spread. Gross per position is therefore **`2.60 × 26 = 67.6 bps`**, not 73 — so
> the floors below are ~8 % *higher* than the review's.

| `x` = share of gross lost to commission | minimum position (at 67.6 bps) |
|---|---|
| 50 % | $5,900 |
| **25 %** | **$11,800** |
| 15 % | $19,700 |

Taking **~$8,600** as a defensible midpoint floor, `N_max = capital / 8,600` and the fastest viable
cadence is `21 / N`:

| Capital | `N_max` | fastest cadence | daily action? |
|---|---|---|---|
| $20 k | 2 | every 10.5 d | **no** |
| $100 k | 11 | every 1.9 d | no |
| **~$180 k** | **21** | **daily** | **yes — the threshold** |
| $250 k | 29 | daily | yes |

**Daily action at a 21-day holding period requires roughly $180,000.** Below that, INV-6's daily
*transaction* cadence and a 21-day hold are structurally incompatible with a $10 flat fee — not
marginally, but arithmetically.

> **A pleasant corollary for QQ-11.** At the expanded universe `n = 330`, `E[max] = 2.91`, so gross
> rises to 75.6 bps and the floor *falls*. **Widening the universe improves the cost economics as
> well as the statistical power** — the same lever helps twice.

### 5.8.4 ⚠ Correction: the "fourth option" is already built, with both knobs at zero

The review proposed as a new architecture: *hold N names and swap only when a candidate beats the
weakest holding by more than the turnover penalty*, arguing that *"under any calendar ladder, rolls
are scheduled and the penalty does nothing."*

**That is not what the code does.** `SleeveSelector._resolve_incumbency`:

```python
if ch_score - inc_score > self.incumbency_delta:
    return challenger        # decisively better => swap
return incumbent             # within delta => STAY (anti-whipsaw)
```

**A sleeve can already decline to roll.** The architecture is an incumbency-challenge system, not a
pure calendar ladder — so the penalty **is** load-bearing. The defect is that **both of its knobs
are set to approximately zero**:

| Knob | Current value | Should be (§9.1.6a) |
|---|---|---|
| `incumbency_margin_delta` | **0.0** | `penalty_z ≈ 1.23` (at `IC = 0.03`, `rt = 32 bps`) |
| turnover penalty | 0.001 (~0.1 % of 1σ) | same quantity, expressed twice |

**`incumbency_margin_delta` and `penalty_z` are the same number in the same units** — z-units of
`opportunity`. §9.1.6a computed it and never noticed the code already has a field for it.

### 5.8.5 The resolution — decouple *looking* from *trading*

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE LADDER CONTROLS HOW OFTEN YOU LOOK.                         ║
║  DELTA CONTROLS HOW OFTEN YOU TRADE.                             ║
║  THE HOLDING PERIOD IS THE EMERGENT PRODUCT OF THE TWO.          ║
║                                                                  ║
║  Little's Law is satisfied by lowering lambda, not by raising N. ║
╚══════════════════════════════════════════════════════════════════╝
```

Keep **5 sleeves challenged weekly** and set `δ = 1.23`. A sleeve that declines its challenge
trades nothing and holds another week, so:

- **`N = 5`** — concentration preserved (**M-2** ✓)
- **holding ≈ 20 days** — emergent, not imposed (**M-4**, L0 §12.1 ✓)
- **`λ = 5/21 ≈ 0.238` trades/day** — Little's Law satisfied by lowering `λ`
- **60 rolls/yr = $1,200 = 6.0 %/yr at $20 k** — the review's `N=5` row exactly, **with no
  architecture change**
- **INV-6 survives, re-read honestly**: *the model nominates daily; the system trades only on a
  decisive challenge* (**QQ-15** ✓)

### 5.8.5a ⚠ CORRECTED — this table was built on two superseded constants

> ★ **Retraction (v1.5.0).** v1.2.0's table used `t > 0.579·τ`, derived from **`2.8σ`** for the top
> name and **`δ = 1.23`**. **Both were superseded inside this same document**: v1.2.0 itself
> corrected the max to **`2.600σ`** (V-28), and v1.3.0 replaced `δ = 1.23` with **`δ_floor = 1.92`**,
> noting that 1.23 came from the retracted 32 bps estimate. The table was never recomputed.
> *(External review, 2026-08-18. I verified that `ln(2.8/(2.8−1.23)) = 0.579` reproduces the stale
> figure exactly, which confirms the provenance.)*

A challenge succeeds when the challenger's edge exceeds the decayed incumbent's plus `δ`:

```text
        2.60·(1 − e^(−t/τ))  >  δ        ⟹        t  >  τ · ln( 2.60 / (2.60 − δ) )

            δ = 1.23, max 2.60   ⟹   t > 0.641·τ      (not 0.579·τ)
            δ = 1.92, max 2.60   ⟹   t > 1.341·τ      ← v1.3.0's cost-derived δ
            δ = 2.19, max 2.59   ⟹   t > 1.868·τ      ★ SUPERSEDES — QA-110, mandate-derived
```

| `τ` | v1.2.0 said | **corrected (`δ = 1.92`)** | training horizon |
|---|---|---|---|
| 15 d | ~10 d | **~20 d** | 21 d |
| **30 d** | **~20 d** | **~40 d** | 21 d |
| 50 d | ~30 d | **~67 d** | 21 d |

```text
╔══════════════════════════════════════════════════════════════════╗
║  AT τ = 30 — THE VALUE THIS SECTION CALLS PLAUSIBLE — THE        ║
║  EMERGENT HOLD IS ROUGHLY DOUBLE THE TRAINING HORIZON.           ║
║                                                                  ║
║  QA-66 says in terms: "a material divergence between them is a   ║
║  defect — it means the objective and the behaviour disagree."    ║
║                                                                  ║
║  v1.3.0's δ correction MANUFACTURED that defect, and §5.8.5      ║
║  went on reporting the old number as confirmation that the       ║
║  architecture lands on target. A superseded constant left in a   ║
║  derived table is worse than no table: it reads as evidence.     ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5.8.5b ★ The useful form — a falsifiable prediction

Set the emergent hold equal to the training horizon:

```text
        1.341 · τ  =  21   ⟹   τ  =  15.7 days      (half-life ≈ 10.9 d)
```

> ⚠ **SUPERSEDED IN PURPOSE by §5.8.6b (v2.2.0).** This prediction asked *"what `τ` makes the
> emergent hold equal the training horizon, **given a cost-derived `δ = 1.92`**?"* **QA-110 removed
> that premise** — `δ` is now derived from M-4's 30-day requirement, so the hold is 30 days *by
> construction* at whatever `τ` turns out to be, and `δ` is recomputed instead. ★ **What survives is
> the measurement, not the consistency claim: build step 4 still measures `τ`, and QA-110's `δ = 2.19`
> is provisional on it.** Kept as the record of how the number was arrived at.
>
> ~~★ **§5.8.5's resolution and §5.6's horizon choice are mutually consistent only at `τ ≈ 16` days.**~~
> Build step 4 measures `τ`. If it returns 30 or 50, **one of the two has to move** — either `δ` is
> capped below its cost-derived floor (accepting more turnover than commission justifies), or the
> production horizon is longer than 21 days.

That is a better state than a table which agreed with the target by arithmetic that no longer holds.

> ⚠ **And note the coincidence.** `τ ≈ 16` is very close to the **`τ ≈ 15.4`** §5.3b identified as
> the value v0.2.0's flat-IC assumption implicitly claimed. **Two independent routes pointing at the
> same number is either corroboration or a shared hidden assumption**, and it matters which. Both
> routes use the same decay law `IC(h) ∝ (1−e^(−h/τ))/√h` — so they are *not* fully independent, and
> the agreement is weaker evidence than it appears. **QQ-23.**

| ID | Rule |
|---|---|
| **QA-65** | ★ **`incumbency_margin_delta` is `penalty_z` (§9.1.6a) and is set from it, not independently.** They are the same quantity in the same units; two names for one number is how one of them ends up at zero |
| **QA-66** | ★ **The holding period is an OUTPUT of `δ`, not an input.** The HorizonSet's `h` is the *training* horizon; the *realised* hold emerges from the challenge cadence and `δ`. **Both are recorded, and a material divergence between them is a defect** — it means the objective and the behaviour disagree |
| **QA-67** | **A cost-based architecture claim states its capital base and its `λ`** (QA-63, QA-64). `N`, `λ` and `h` are related by `N = λ·h`; a design that fixes all three without checking the identity is arithmetically inconsistent |

### 5.8.6 Recommendation, and what still needs deciding

| Step | | |
|---|---|---|
| **1** | **Establish the real capital base** (QA-63) | Fact-finding, not judgement. Every figure above is a function of it, and it is currently a hard-coded `20000.0` |
| **2** | **Set `δ` from §9.1.6a rather than leaving it at 0.0** | The single highest-leverage change available: it converts a scheduled ladder into an incumbency system that already exists, and makes the holding period emergent |
| **3** | **Keep `N = 5`; do not scale buckets with the horizon** | Preserves M-2, keeps position size viable at realistic capital, and satisfies Little's Law through `λ` |
| **4** | **Re-read INV-6 as nominate-daily / trade-on-decisive-challenge** | ⚠ **Constitution-level — Victor's** (QQ-15). Nothing below this line is safe to assume |

> ⚠ **Correction (2026-08-17): `δ` is far less blocked than this said.** `δ = rt/β`, and **`rt` has
> a known floor — commission — which is exact the moment QA-63 fixes the capital base.** QQ-20's
> spread and slippage are strictly *additive*, so they can only push `δ` **upward**. `δ` therefore
> has a **computable lower bound today**:
>
> | Capital | `N` | position | commission round trip | **`δ_floor = rt/β`** |
> |---|---|---|---|---|
> | **real book** | — | **$8,941 median order** | **22 bps** | **0.86** ← *use this* |
| **real book** | — | $29,018 max order | 6.9 bps | 0.26 |
| $20 k *(hard-coded)* | **5** | $4,000 | 50 bps | ~~1.92~~ |
> | $20 k | 21 | $952 | 210 bps | **8.08** |
> | $100 k | 5 | $20,000 | 10 bps | 0.38 |
>
> ~~**Set `δ = 1.92` now**~~ ⚠ **SUPERSEDED by §5.8.6b / QA-110 (v2.2.0): `δ = 2.19`.** The
> cost-derived value is no longer the determinant — **the mandate sets `δ` and cost is a floor that
> is checked** (QA-111). Retained because it is the evidence for QA-63, and because `1.92` is still
> 1,900× better than the `0.0` in the code today.
>
> ★ **This also supersedes the `1.23` used above**, which came from the **retracted 32 bps
> estimate** rather than from this repository's actual fee schedule and capital.

### 5.8.6a ★★ δ HAS TWO SIDES, AND COMMISSION CANNOT SET IT AT ANY REAL BOOK SIZE

> ★ **Found by external review, 2026-08-18, from a capital-base inconsistency — then it went further
> than the review took it.** `δ = rt/(IC·σ)` and `rt = $20·N/book`, so **δ is a direct function of
> the book**. Two documents were using two different books:
>
> | source | book | position (N=5) | `rt` | **δ** | emergent hold |
> |---|---:|---:|---:|---:|---:|
> | `backtester.py:107` literal | $20,000 | $4,000 | 50.0 bps | **1.92** | 21.7 d |
> | `F4` CT-4.5 **example** | $142,500 | $28,500 | 7.0 bps | **0.27** | ★ **1.8 d** |
>
> ⚠ **Neither is measured.** One is a hard-coded backtest constant; the other is an *illustrative
> value in a contract example*. **QA-63 is not housekeeping — it is the input every number in §5.8
> depends on**, and it swings δ by **7×**.

**δ is bounded on both sides**, and §5.8.5 only ever stated the upper one:

```text
    UPPER (freeze):   δ < E[max z] = 2.590     no challenger ever clears (§5.8.7)
    LOWER (churn):    δ ≥ E[max]·(1 − e^(−t/τ)) for the required hold t

        t = 21 d (HorizonSet)      ⟹  δ ≥ 1.893
        t = 30 d (★ M-4)           ⟹  δ ≥ 2.193
```

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE CURRENT δ = 1.92 IS INSIDE THE 21-DAY WINDOW AND ★ OUTSIDE  ║
║  THE 30-DAY ONE. Even at the $20k literal, the architecture      ║
║  does not deliver M-4's registered-account holding period.       ║
║                                                                  ║
║  And the risk does not vanish at a larger book — IT INVERTS.     ║
║  At $20k the portfolio freezes; at $142.5k it churns at 1.8-day  ║
║  holds, which is precisely the pattern M-4 exists to prevent     ║
║  and the ground on which QQ-1 demoted the 1-week horizon.        ║
╚══════════════════════════════════════════════════════════════════╝
```

**Now solve for the position size that puts δ in the window:**

| required hold | position must be | ⇒ book at N=5 |
|---|---|---|
| ≥ 21 d | **$2,972 – $4,067** | $14,861 – $20,334 |
| ≥ 30 d (M-4) | **$2,972 – $3,511** | $14,861 – $17,553 |

| book | sleeves needed to hold `δ ≥ 2.193` |
|---:|---|
| $20,000 | 5.7 — plausible |
| $50,000 | **14.2** — ★ contradicts M-2 |
| $142,500 | **40.6** — ★ contradicts M-2 |
| $300,000 | **85.5** — ★ absurd |

```text
╔══════════════════════════════════════════════════════════════════╗
║  ★★ COMMISSION CANNOT SET THE TURNOVER PENALTY AT ANY BOOK SIZE  ║
║  YOU WOULD ACTUALLY RUN.                                         ║
║                                                                  ║
║  A FLAT fee shrinks to nothing as a fraction of a growing        ║
║  position, so the δ it implies collapses — and the only way to   ║
║  restore it is to hold more, smaller positions, which flatly     ║
║  contradicts M-2's deliberate concentration.                     ║
║                                                                  ║
║  §5.8's derivation of δ from the flat fee works ONLY in a narrow ║
║  band around $15-20k. That band is where the backtest literal    ║
║  happens to sit. IT IS A COINCIDENCE, NOT A DESIGN.              ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **And §5.8.5b's `τ ≈ 15.7` consistency result is an artifact of the same literal.** At the
$142.5k figure the emergent hold is 1.8 days and the tidy agreement with the 21-day training horizon
evaporates entirely. That result is currently doing work as evidence the architecture is coherent.

| ID | Rule |
|---|---|
| **QA-102** | ★★ **`δ` is set to deliver the holding period M-4 requires; cost is a FLOOR that is checked, not the determinant.** §5.8 has the causality backwards at any realistic book. **QA-66 stands** — the hold is an *output* of δ — but **δ itself must be an output of the mandate**, not of a commission that vanishes with scale |
| **QA-103** | ★ **A cost-derived `δ` must use a PROPORTIONAL cost, not a flat fee.** Spread and slippage stay roughly constant in bps as the position grows; commission does not. **This is what QQ-20 was always for**, and §5.8's derivation cannot be repaired without it |
| **QA-104** | ★ **Every δ, hold-period or drag figure states its capital base and its `N`** (extends QA-67). A number that does not is unreadable, and two documents already disagreed by 7× without either noticing |
| **QA-105** | ★ **`N` is a free lever on δ and it cuts BOTH ways.** `δ ∝ N`, so lowering `N` from 5 to 3 moves the freeze cliff 40 % away **and collapses the hold from 21.7 d to 9.4 d** — trading the freeze risk for the churn risk. **Any N change is checked against both bounds, never one** |
| **QA-106** | ⚠ **QQ-21's resolution (N=5, δ=1.92, ~21-day hold) is CONDITIONAL on a $20k book and does not satisfy M-4's 30 days even there.** It is re-opened as **QQ-24** pending QA-63 |

---

### 5.8.6b ✅ QA-63 RESOLVED, AND δ RE-BASED — **DECIDED 2026-08-18**

**QA-63 — the capital base.** Neither number in circulation was measured: `$20,000` is a
`backtester.py` literal, `$142,500` is an *illustrative value in F4's CT-4.5 example*.

| ID | Rule |
|---|---|
| **QA-107** | ✅ **The capital base is READ from D-11's reconciled book — `book_state.nav_base` (F4 CT-4.5) — never hard-coded and never taken from a spec example.** A backtest states the base it ran at (QA-11's pinned spec); it does not choose one |
| **QA-108** | ★ **The RESP is excluded from the fund capital base** (D-11 RC-4), and the exclusion is stated with the figure. A base that silently includes a child's education account is not the fund's |
| **QA-109** | **Where no reconciled book exists, the run FAILS** (`RSK.EXPOSURE.NO_BOOK`'s sibling). It does not fall back to a constant — that fallback is the defect QA-63 names |

**δ re-based — and this is what makes the capital base stop being load-bearing.**

```text
        δ  =  E[max z] · ( 1 − e^(−T_min/τ) )        T_min = 30 d  (M-4)

    the MANDATE sets δ.  Cost is a FLOOR that is CHECKED, not the determinant.
```

| `τ` | δ at n=130 | δ at n=500 |
|---:|---:|---:|
| 10 d | 2.461 | 2.873 |
| **16 d** *(§5.8.5b's prediction)* | **2.193** | 2.560 |
| 21 d | 1.969 | 2.299 |
| 30 d | 1.637 | 1.911 |

★ **And the mandate bound binds at every book size, including the $20 k literal:**

| book (N=5) | cost-derived δ | mandate δ | which binds |
|---:|---:|---:|---|
| $20,000 | 1.92 | 2.193 | **mandate** |
| $142,500 | 0.27 | 2.193 | **mandate** (by 8×) |
| $300,000 | 0.13 | 2.193 | **mandate** (by 17×) |

```text
╔══════════════════════════════════════════════════════════════════╗
║  RE-BASING δ ON THE MANDATE DISSOLVES THE CAPITAL-BASE PROBLEM.  ║
║                                                                  ║
║  The mandate bound binds at EVERY book size tested, so δ no      ║
║  longer moves with the book at all. QA-63 still must be fixed —  ║
║  the cost FLOOR check needs it, and so does every % figure —     ║
║  but it stops determining the architecture.                      ║
║                                                                  ║
║  ★ The failure mode this closes: at $142.5k the commission-      ║
║  derived δ was 0.27, giving 1.8-day holds. The mandate-derived   ║
║  δ is 2.19 and gives 30-day holds AT ANY BOOK SIZE.              ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **QA-110** | ✅ **`δ = E[max z]·(1 − e^(−T_min/τ))` with `T_min = 30` trading days (M-4).** Interim value **δ = 2.19** at `τ = 16`, `n = 130`. ⚠ **It is recomputed the moment build step 4 measures `τ`** — δ spans 1.17–2.46 across the plausible τ range, so this is a provisional number with a stated dependency, not a constant |
| **QA-111** | ★ **The cost floor is CHECKED, never used to set δ**: assert `δ ≥ rt/(IC·σ)` and **report the slack**. If it ever binds, the position size has fallen into the pathological band (§5.8.6a) and that is the finding |
| **QA-112** | ★ **δ must also satisfy the upper bound `δ < E[max z]`** (§5.8.7). At `τ ≤ 10` the mandate-derived δ reaches 2.46 against a 2.59 ceiling — **only 5 % of headroom.** ★ **If `τ` measures short, M-4's 30-day hold and a tradable portfolio become incompatible at n=130, and the resolution is universe expansion** (n=500 lifts the ceiling to 3.02) |
| **QA-113** | ★ **Universe target `n = 500`.** It buys three separate things: the MDE on `IC₀₃` halves (0.044 → 0.022, from *above* the assumed value to *below* it); the freeze ceiling rises 2.59 → 3.02, which is what makes QA-112 survivable; and gross alpha rises ~17 % as a side effect. **The first two are the reasons** |

### 5.8.7 An independent kill of the 21-bucket ladder

The δ floor condemns the ladder from a completely separate direction to §5.6a's drag arithmetic.

At 21 buckets on $20 k, position size is $952 and commission alone is **210 bps**, giving
**`δ_floor = 8.08`**. But the achievable spread of `opportunity` across the cross-section is bounded
by `E[max − min]`:

| Universe | `E[max − min]` |
|---|---|
| n = 130 | **5.20 σ** |
| n = 330 | 5.81 σ |

> ★ **The real margin is wider than this comparison (v1.5.0, external review).** `E[max − min]` is
> the most *generous* possible bound: the challenger does not have to beat the **worst** name in the
> universe, it has to beat the **incumbent** — a decayed former top pick sitting at perhaps
> `+0.5σ` to `+1.5σ`. The realistically achievable gap is therefore nearer **`2.60 − 1.0 ≈ 1.6σ`**,
> and the ladder fails by **≈ 5×** (3.8×–7.3× across that incumbent range), not 1.6×.
> **The conclusion is unchanged; the margin is considerably wider than stated.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  A CORRECTLY-SIZED DELTA UNDER THE 21-BUCKET LADDER IS           ║
║  UNREACHABLE. 8.08 EXCEEDS THE ENTIRE ACHIEVABLE SPREAD (5.20),  ║
║  AND EXCEEDS THE REALISTIC ONE (~1.6σ) BY ROUGHLY 5x.            ║
║                                                                  ║
║  No challenger could ever clear the hurdle. The portfolio        ║
║  would never trade at all.                                       ║
║                                                                  ║
║  Two independent derivations — the DRAG arithmetic (§5.6a) and   ║
║  the INCUMBENCY arithmetic (here) — kill the same architecture.  ║
║  Two derivations agreeing is much stronger evidence than one.    ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **QA-68** | ★ **A turnover hurdle must be reachable.** `δ` is checked against `E[max − min]` of the score across the universe. **`δ` exceeding the achievable spread is a silent no-trade condition** — the system stops trading and nothing reports why, because every day's challenge simply fails |
>
> **And QA-54's minimum-hold floor becomes binding, not a backstop.** At `τ = 15` the emergent hold
> is ~10 days, which is inside M-4's danger zone. If `τ` measures short, `δ` alone will not deliver
> a 21-day hold and the floor has to carry it (§9.6).

---

## 5.9 ★ THE DECISION ANCHOR — **DECIDED 2026-08-18** (closes `L1-orchestration.md` QO-7)

**Every label is anchored on the OPEN:**

```text
                 label(T, h)  =  open(T + h) / open(T)  −  1

          NOT   adj_close(T + h) / adj_close(T) − 1     ← what the code does today
```

### 5.9.1 Why the anchor moved

D-08 §5A fixed the production cadence: the daily run fires at **10:00 ET** and decides from the
**day-T opening print**. The label must be anchored where the decision is taken.

```python
# ohlcv/dataset/label_builder.py:86-87 — the current, close-anchored form
df["fwd_ret_1w"] = df.groupby("ticker")["adj_close"].shift(-5)
df["fwd_ret_1w"] = (df["fwd_ret_1w"] - df["adj_close"]) / df["adj_close"]
```

A model fitted on `close(T) → close(T+h)` and deployed to decide at `open(T)` is anchored **a full
session away from the return it was trained to predict**, on every prediction. The error is not
noise that averages out — it is a systematic one-session offset in the same direction every day,
and **the backtest cannot see it because the backtest shares the training anchor**. INV-4 does not
permit the two anchors to differ; one of them had to move, and the decision anchor is the one the
broker and the human actually live with.

| ID | Rule |
|---|---|
| **QA-71** | ★ **The label anchor is `open`, at both ends: `open(T+h)/open(T) − 1`.** Not `close→open`, not `open→close` — **both ends on the same field**, or the label carries a systematic intraday drift that the model will happily fit |
| **QA-72** | ★ **The anchor is a declared property of the label set**, recorded in the label contract and in D-04's model manifest, and **asserted equal to the RunManifest's `decision_anchor`** at inference (D-08 OR-35). A silent anchor disagreement is exactly the class of defect §9 exists to catch |
| **QA-73** | ★ **The open must be split- and dividend-adjusted consistently with the close it replaces.** Today only `adj_close` is adjusted; a raw `open` divided by a raw `open` across a split boundary produces a **10× label on NVDA's 10:1** (`L1-data-engine.md` §5C). ★ **This is the single highest-risk part of the change** — the current `open` column has never been used by any label or feature, so its adjustment has never been exercised |
| **QA-74** | Backtest fills are anchored on the **same open**, not the close. A backtest that labels on opens and fills on closes reintroduces the offset it was meant to remove |
| **QA-75** | The horizon `h` is counted in **trading days between opens**, and the T+h open must be a **real, settled print** — a synthetic or forward-filled open makes the label unfalsifiable (D-08 OR-32) |

### 5.9.1a ⚠ THE FILL ANCHOR IS WRONG — you cannot transact at a price that printed before you decided

> ★ **Found by external review, 2026-08-18. QA-74 as written credits a fill that was unobtainable.**

D-08 §5A fires the run at **10:00 ET**. The market opens at **9:30**. So `open(T)` is a print from
**thirty minutes before the decision exists**.

| | |
|---|---|
| `open(T)` as a **feature input** at 10:00 | ✅ **fine** — it is settled and in the past (INV-1 intact) |
| `open(T)` as the **fill anchor** (QA-74) | ❌ **look-ahead in the execution model** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  YOU CANNOT BOTH USE THE DAY-T OPEN AS AN INPUT AND FILL AT      ║
║  THE DAY-T OPEN. That is the crux, and it is unavoidable.        ║
║                                                                  ║
║  The signal is computed FROM the open, so any relationship       ║
║  between the signal and the 9:30->10:00 move transfers directly  ║
║  into the backtest as free alpha. Since intraday reversal is a   ║
║  documented effect, that relationship is unlikely to be zero.    ║
╚══════════════════════════════════════════════════════════════════╝
```

**A precision the review did not draw, and it matters.** The 9:30→10:00 dispersion is large — the
first thirty minutes carries roughly 15–20 % of daily variance in 7.7 % of the session:

| annualised vol | one-way | round trip |
|---|---:|---:|
| 30 % (universe, §9.1.6a) | 73–85 bps | **104–120 bps** |
| 45 % (semis) | 110–127 bps | 155–179 bps |

★ **That ~110 bps is a *dispersion*, not a bias.** It inflates label noise and *depresses* measured
IC; it does not by itself manufacture return. **The bias is only the systematic component** — the
mean open→10:00 drift conditional on the signal — which is much smaller than 110 bps but is the part
that is a genuine defect, and is the same defect class §5.9.1 was written to remove, relocated from
one session to thirty minutes. **Both matter and they must not be conflated:** the dispersion makes
the backtest *noisy*, the conditional drift makes it *wrong*.

Either way the comparison is stark: **the anchor gap's dispersion is an order of magnitude larger
than the 3–12 bps flip-back threshold §5.6a's entire cost argument turned on.**

### 5.9.1b The three consistent choices — and the one that is chosen

| | decision time | feature inputs | fill & label anchor | verdict |
|---|---|---|---|---|
| **A** | 10:00 | through `open(T)` | **`open(T+1)`** | ✅ consistent, tradable. Costs **one session of decay** |
| **B** | 10:00 | through `open(T)` | ★ **arrival price ≈ 10:00** | ✅ consistent, tradable, **zero delay** — needs QA-69 |
| **C** | 09:30 | through `close(T−1)` **only** | `open(T)` (MOO) | ✅ consistent — but **overturns D-08 §5A's cadence** |

| ID | Rule |
|---|---|
| **QA-76** | ★ **The fill and label anchor must be a price at or after the decision instant.** `open(T)` is a legitimate *input* at a 10:00 run and an illegitimate *fill*. **QA-74 is superseded.** |
| ~~**QA-77**~~ ⚠ **SUPERSEDED → §5.9.1g (v1.7.0)** | ★ **Target is (B); interim is (A).** (B) is the correct end state and requires no cadence change — **QA-69's arrival quote *is* the decision-moment price**, so §5.9 and §5.8's QQ-22 are the same problem and were being solved separately. Until arrival capture accrues, **(A)** — fill and label at `open(T+1)` — is unambiguously tradable and costs one session of decay rather than an unknown bias. **(C) is not chosen: it would overturn a cadence Victor has decided, and it forbids the open as an input** |
| **QA-78** | Once arrival capture runs, the **open→arrival drift is measurable directly**, and QA-71's anchor can be settled empirically instead of by assumption |

### 5.9.1c ★ MEASURED — the normalisation concern, settled from 11.5 years of our own data

> ⚠ **v1.5.0 used a simulation here and the reviewer was right to reject the method.** My simulation
> drew **independent** overnight and intraday legs, and under independence the two variances are not
> approximately equal — they are **identically** equal. The algebra is exact:
>
> ```text
>    close(T)→close(T+n) = Σ[T+1..T+n] (oᵢ + dᵢ)
>    open(T) →open(T+n)  = Σ[T..T+n−1] dᵢ + Σ[T+1..T+n] oᵢ
>
>    Both contain exactly n intraday and n overnight legs, so
>        Var_oo − Var_cc = 2n·[ Cov(dᵢ, oᵢ₊₁) − Cov(oᵢ, dᵢ) ]
>    and the ENTIRE effect lives in covariances an iid simulation sets to zero.
> ```
>
> **A simulation returning 1.001 confirmed its own assumption.** Reasoning about a quantity we hold
> 11.5 years of direct observations of is the same error class as reasoning about the fee model
> instead of reading `backtester.py` — which is what QA-64's horizon-invariance finding came from.

**So it was measured.** `data/ohlcv/price_data.parquet` — **130 tickers, 371,840 rows, 2015-01 to
2026-08**, with the adjusted open reconstructed as `open × adj_close/close`:

| quantity | measured |
|---|---|
| **`ρ_od` = corr(overnight, intraday)** | **median −0.0020**, mean +0.0003, 10–90 % `[−0.047, +0.052]` |
| names with `ρ_od < 0` | **50.8 %** — a coin flip |
| overnight share of daily variance | 0.363 |
| **`sd(oo)/sd(cc)` at `h = 21`** | **1.0006** (10–90 % `[0.9940, 1.0047]`) |
| …across **liquidity deciles** | **0.9976 – 1.0022** — max deviation **0.24 %** |
| …`ρ_od` across volatility deciles | −0.016 to +0.018 |
| …`ρ_od` across eras (2015-17 / 18-20 / 21-23 / 24-26) | −0.028, +0.040, −0.007, −0.020 |

```text
╔══════════════════════════════════════════════════════════════════╗
║  ρ_od IS INDISTINGUISHABLE FROM ZERO IN THIS UNIVERSE — IN       ║
║  EVERY LIQUIDITY DECILE, EVERY VOLATILITY DECILE, AND EVERY      ║
║  ERA MEASURED.                                                   ║
║                                                                  ║
║  So sd(oo)/sd(cc) really is ~1.000 at h=21, and QA-80's          ║
║  heterogeneity worry — that a panel-wide 1.000 hides ±5% by      ║
║  decile — is EMPIRICALLY FALSE HERE. The worst decile is off by  ║
║  0.24%, not 5%.                                                  ║
║                                                                  ║
║  ★ The predicted −0.10 covariance (from Berkman et al. 2012)     ║
║  does not appear. My 0.1% figure was RIGHT BY LUCK — the         ║
║  simulation could not have produced anything else — and it is    ║
║  now right on evidence.                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| ~~**QA-79**~~ ⚠ **SUPERSEDED → §5.9.1o (v2.0.0)** | *(downgraded, v1.6.0)* `σ̂` in QA-34/QA-58 is the volatility of the **anchored** return, and the unit-variance property of `Z` is **asserted as a test**: `sd(Z) ≈ 1` over the panel. **The Yang–Zhang restatement is not required at `h1m`** on current evidence — the measured correction is 0.06 %. It remains required at `h1w`, where the endpoints are a fifth of the span rather than a twenty-first |
| ~~**QA-80**~~ ⚠ **SUPERSEDED → §5.9.1o (v2.0.0)** | *(downgraded, v1.6.0)* `sd(Z)` is **still** checked per liquidity decile — not because a tilt is expected (measured max deviation 0.24 %) but because the check is free and **`ρ_od` is a regime-dependent quantity**: it is near zero in 2015–2026 US large-caps and was materially negative in the 1996–2008 sample Berkman measured. **The test guards a change, not a current defect** |
| **QA-83a** | ⚠ **§5.9.1c's pooled `ρ_od ≈ 0` was the WRONG statistic for inferring about Berkman and the RIGHT one for the variance ratio — do not over-propagate the retraction.** The identity `Var_oo − Var_cc = 2n·[Cov(dᵢ,oᵢ₊₁) − Cov(oᵢ,dᵢ)]` consumes **total** covariances, which is exactly what was measured; the within-date test shows that total decomposes into a positive market component and a negative idiosyncratic one that roughly cancel. ★ **So `ratio = 1.0006` stands and the variance-grounds downgrade of QA-79/80 was sound on its own terms** — they are re-promoted in §5.9.1l on *label-noise* grounds instead. **Retracting more than the evidence requires is its own failure mode, and the mirror image of over-reading a null** |
| **QA-83** | ★ **A structural claim about the panel is measured on the panel, never simulated.** 11.5 years × 130 names is already on disk; a simulation of a quantity we hold direct observations of can only return its own assumptions |

### 5.9.1d ⚠ NEW — `adj_open` does not exist, so QA-71 has no data yet

```python
>>> pd.read_parquet('data/ohlcv/price_data.parquet').columns
['date','ticker','open','high','low','close','adj_close','volume']
#                  ^^^^ raw only            ^^^^^^^^^ the ONLY adjusted field
```

★ **The panel carries `adj_close` and no `adj_open`, `adj_high` or `adj_low`.** QA-71's
open-anchored label therefore has **no adjusted open to anchor on**, and the raw `open` across
NVDA's 10:1 gives a **10× label** (QA-73).

| ID | Rule |
|---|---|
| **QA-84** | ★ **`adj_open` is constructed as `open × (adj_close / close)`** — the adjustment factor is a property of the **date**, not the field — and is **materialised into the panel with a contract**, never recomputed ad hoc at each call site |
| **QA-85** | ⚠ **QA-81's invariant is not runnable as stated until QA-84 lands.** `adj_close/close == adj_open/open` is trivially true of a reconstruction, so it tests nothing about the reconstruction. **The real check is against the vendor**: where FMP supplies an adjusted open, assert the reconstruction matches it; where it does not, assert the factor is **strictly positive, monotone within a ticker between corporate actions, and changes only on dates D-07's calendar check flags** (§6A) |
| **QA-91** | ⚠ **QA-84's reconstruction assumes one factor per date across all fields — unambiguous for splits, not for cash dividends.** Whether `adj_close/close` transfers to the open depends on **which side of the ex-date the vendor keys the factor to**: the ex-date *open* already reflects the dividend drop in the raw price, so a close-derived factor can double-count it. ★ **QA-85's monotonicity test passes either convention**, so this needs a **targeted check on ex-dividend dates specifically**, against D-07's dividend calendar (§6A) |

### 5.9.1e ★ MEASURED — the open→10:00 drift, with its power stated

Answered from `historical_chart_15min__*.csv` — **4 tickers × 492 sessions**, 2024-01→2026-08.

> ⚠ **v1.6.0 pooled these as 1,952 independent observations. They are not.** On any given morning
> the four names move together with the market in the first thirty minutes — **measured mean
> pairwise `ρ̄ = 0.285`**, so the Kish design effect gives `n_eff ≈ 1,060`, not 1,952. **This is the
> overlapping-label defect of §5.3b, one domain over: correlated observations counted as
> independent.** *(External review, 2026-08-18.)*

Inference is therefore **clustered on date** — collapse to daily cross-sectional means, which needs
no assumption about `ρ̄` at all:

| | naive pooled | ★ **date-clustered** |
|---|---:|---:|
| n | 1,952 | **492 dates** |
| mean drift | −4.39 bps | **−3.93 bps** |
| SE | 3.83 bps | **5.10 bps** (×1.33) |
| t | −1.14 | **−0.77** |
| 95 % CI | ±7.5 | **`[−13.93, +6.08]` bps** |
| ★ **MDE at t = 1.96** (QA-33) | 7.5 bps | **10.0 bps** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE HYPOTHESIS UNDER TEST IS A BIAS OF 5-10 bps.                ║
║  THE MDE IS 10.0 bps.                                            ║
║                                                                  ║
║  So this measurement CANNOT distinguish "no bias" from "a bias   ║
║  large enough to decide the question". v1.6.0 called it "a coin  ║
║  flip" — that over-reads it. A coin flip means evidence pointing ║
║  both ways with equal weight; what exists is NO EVIDENCE EITHER  ║
║  WAY, and a CI comfortably containing both 0 and −12 bps.        ║
║                                                                  ║
║  Detecting 5 bps at t=2 needs ~1,970 clustered sessions —        ║
║  ★ 7.8 YEARS. The unconditional bias joins the conditional one   ║
║  (QA-87) as undetermined, not as settled.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

> ⚠ **And v1.6.0 cited the wrong correlation.** `corr(9:30→10:00, 10:00→close) = +0.036` is an
> intraday-to-intraday statistic; **Berkman's pair is `corr(overnight gap, intraday move)` = `ρ_od`**,
> measured correctly in §5.9.1c as −0.002. The +0.036 answers a different question (does the first
> half-hour predict the rest of the day) and is **withdrawn as evidence about reversal.**

### 5.9.1f ⚠ RETRACTED — "170 bps is 40× (A)'s cost" compared a dispersion to a mean

> ★ **This was v1.6.0's load-bearing sentence and it is a units error** — the third of its exact
> kind in this document, after the turnover penalty (return units vs score units, QQ-16) and §6.2's
> sleeve weight (per-decision vs annual). **170 bps is a standard deviation; 4.2 bps is an expected
> cost. Their ratio has no interpretation.**

Costed in the units the dispersion actually damages — **attenuation of the fitted signal** by
classical errors-in-variables:

```text
    sd(label at h=21)          =  866 bps          (σ = 8.66 %, §9.1.6a)
    mismatch noise, both ends  =  170·√2 = 240 bps
    sd(observed label)         =  √(866² + 240²) = 899 bps

    attenuation = 866/899 = 0.9636   ⟹  3.6 % of IC lost
    cost in alpha = 0.036 × 67.5 bps =  2.46 bps
```

| | expected cost per position |
|---|---:|
| **(A)'s decay cost** | **4.2 – 5.7 bps** |
| mismatch, via IC attenuation | **2.46 bps** |
| mismatch, via bias | −3.9 bps, CI `[−13.9, +6.1]` → **undetermined** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  ON EXPECTED VALUE, (A) COSTS MORE THAN THE MISMATCH IT REMOVES. ║
║  THE 40x DISAPPEARS ENTIRELY ONCE THE UNITS ARE FIXED.           ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5.9.1g ★ So what justifies (A) — and it is not magnitude

Two grounds, neither arithmetic:

**(i) Correctness.** Filling at a price that printed before the decision existed is **look-ahead in
the execution model**. That is a defect at *any* magnitude, and §5.9.1a leads with it correctly.

> ★ **It must not be given a supporting magnitude argument.** A magnitude argument invites a future
> reader to re-run the numbers, find `2.46 < 4.2`, and revert. **This paragraph exists to stop that
> reader** — the arithmetic in §5.9.1f is not evidence *for* (A) and was never the reason.

**(ii) ★ QA-72 — the anchor must be the same in backtest and production.** This is the reason (A)
beats going straight to (B), and v1.6.0 framed it wrongly as *"(B) needs QA-69"*:

```text
   (B) needs QA-69's CAPTURE WIRING — days of work.  Production could
       switch to arrival-price fills almost immediately.

   What it CANNOT do is BACKTEST on arrival prices: no historical
   arrival prices exist, and none ever will (V-30 — the export carries
   Transaction DATE, not a timestamp).

   ★ QA-72 forbids the backtest and production anchors from differing.
```

| ID | Rule |
|---|---|
| **QA-77** ✅ *binding* | *(restated v1.7.0)* ★ **(A) is the interim because `open` is the only anchor with 11.5 years of history, and QA-72 requires the backtest and production anchors to agree.** Not because of any magnitude comparison — §5.9.1f shows the magnitudes favour neither. The standing justification is **correctness (§5.9.1g(i))** plus **anchor parity (ii)**, and both are robust to anyone recomputing the numbers |
| **QA-89** | ★ **(A) ends when enough arrival history exists to BACKTEST on** — not when capture "accrues". That is a **stated number of sessions, computable today** from the fold protocol's minimum window (§7.1), and it is recorded in the HorizonSet rather than left to judgement |
| **QA-86** | ★ **The sleeve clock convention is stated: does the hold start at nomination or at fill?** Currently unstated, and worth more than the 1.5 bps spread in (A)'s cost: **it also moves §5.8.5b's consistency point from `τ = 15.66 d` (21-day hold) to `τ = 16.40 d` (22-day)** — it shifts the number the whole retrain is tested against, so it must be fixed **before** build step 4 measures `τ`, not after |
| ~~**QA-87**~~ ⚠ **SUPERSEDED → §5.9.1n (v2.0.0)** | Berkman et al.'s adverse-selection argument is **unresolved, not dismissed.** MU — the most retail-attended of the four — has the most negative drift (−9.88 bps). ★ **§5.9.1c's `ρ_od ≈ 0` is not evidence against it**: Berkman's is a *conditional-mean* effect on an attention-sorted subset, and an effect concentrated in a small subset contributes almost nothing to a pooled correlation. The nominated-name subset is the population that matters, and it becomes measurable once nominations accrue |
| **QA-90** | ★ **Cross-sectional observations sharing a date are not independent.** Any statistic pooled across names and dates is **clustered on date**, or reports its design effect. Measured `ρ̄ = 0.285` for a 30-minute window on 4 names. **This is §5.3b's overlapping-label lesson in the cross-sectional direction, and QA-33's MDE requirement applies to nulls as much as to positives.** ★ *Corollary (§5.9.1i): clustering is not only a precision penalty — it is also what a well-designed conditional test **exploits**, since a within-date difference cancels the shared factor exactly* |

### 5.9.1h ★★ QA-87 CLOSED — measured on the daily panel, and it points the other way

> ★ **The reviewing agent's key structural insight, and it is correct:** the unconditional drift and
> the attention-*conditional* drift are affected by clustering in **opposite** directions. A pooled
> mean is contaminated by the market-wide opening move (the `ρ̄ = 0.285` that forced §5.9.1e's SE
> inflation); a **same-date cross-sectional difference cancels the market component exactly**.
> **The thing that damaged the unconditional test is the thing the conditional test differences
> away** — so the conditional test is *better* powered, not worse.
>
> ★ **And it needs no intraday data.** Berkman's dependent variable is `open → close`, which is
> already in the daily bar. **130 tickers × 2,917 dates, on disk.**

**Stage 1 — attention proxies at `T−1`, intraday return at `T`, top-minus-bottom decile spread:**

| attention proxy | spread | t | **MDE** |
|---|---:|---:|---:|
| `\|r(T−1)\|` | +0.44 bps | +0.22 | 3.85 |
| abnormal volume `T−1` | −1.12 bps | −0.81 | **2.70** |
| range expansion `T−1` | −0.33 bps | −0.23 | **2.89** |
| `\|overnight gap\|` at `T` | −0.00 bps | −0.00 | 4.39 |

**Mechanism test** — `open_position = (open−low)/(high−low)`, which tests Berkman's *causal story*
rather than its outcome: panel mean **0.4992**, and no attention decile spread is significant. **The
open does not sit high in the day's range.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  FOUR NULLS, THREE OF THEM WITH MDE BELOW 3 bps AGAINST A        ║
║  5-10 bps HYPOTHESIS.                                            ║
║                                                                  ║
║  The ATTENTION-conditional effect is excluded at any magnitude    ║
║  that could move the anchor decision. This is the first          ║
║  well-powered test in the whole line of enquiry, and it cost     ║
║  one script over data already on disk.                           ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5.9.1i ★★ …but the SIGNED gap test fires — and the caveat it forces on §5.9.1c

Sorting on the **signed** overnight gap rather than an attention proxy:

| gap decile | 0 (most −) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 (most +) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| intraday (bps) | **+4.83** | +3.27 | +3.38 | +2.61 | +0.83 | +1.40 | +0.40 | −0.66 | −0.75 | **−2.76** |

**Spread 9−0 = −7.59 bps, `t = −3.08`, monotone across all ten deciles.** Overnight-gap reversal is
**real in this panel** — Berkman's outcome, reached through the gap rather than through attention.

> ⚠ **This forces a caveat on §5.9.1c.** The pooled `corr(o, d) = +0.0038` is ~0, while the
> cross-sectional decile spread is `t = −3.08` on the same data. **They are not in conflict**: the
> pooled statistic is swamped by market-wide co-movement, which the within-date sort removes.
> **§5.9.1c's "`ρ_od` is indistinguishable from zero" is true unconditionally and false
> within-date**, and it must not be cited as evidence that no reversal exists. This is precisely the
> reviewer's methodological point arriving as an empirical result, and it **partially rehabilitates
> the `ρ_od ≈ −0.10` intuition** I had treated as refuted.

### 5.9.1j ★★ The finding that decides QA-87 — and neither of us predicted its direction

Splitting the signed-gap effect by the volatility quartile **QN-7 says the ranker selects into**:

| volatility quartile | spread | t |
|---|---:|---:|
| 0 — calmest | **−21.09 bps** | **−5.63** |
| 1 | −16.64 bps | −4.99 |
| 2 | −12.48 bps | −3.75 |
| **3 — most volatile** | **+1.49 bps** | **+0.39** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE GAP-REVERSAL EFFECT IS STRONGEST IN THE CALMEST NAMES AND   ║
║  ABSENT IN THE MOST VOLATILE ONES.                               ║
║                                                                  ║
║  That is the OPPOSITE of Berkman's "hard to value, costly to     ║
║  arbitrage" prediction — and, decisively, the OPPOSITE of the    ║
║  adverse-selection concern.                                      ║
║                                                                  ║
║  QA-58's denormalised ranking multiplies by σ̂, so QN-7 says the  ║
║  system tilts toward HIGH-volatility names. That is exactly the  ║
║  population where the effect does not appear.                    ║
║                                                                  ║
║  ★ THE ADVERSE SELECTION RUNS IN THE SYSTEM'S FAVOUR, NOT        ║
║  AGAINST IT.                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

Two robustness notes recorded honestly:

- **Split-half:** 2015–2020 `−9.68 bps (t = −3.29)`; 2021–2026 `−5.50 bps (t = −1.39)`. **The effect
  weakens and loses significance in the recent half** — consistent with the reviewer's own caveat
  that a published effect gets arbitraged.
- **A confound that does not rescue the concern:** gap deciles are formed panel-wide, so high-vol
  names populate the extremes with *larger absolute* gaps. If reversal scaled with gap size that
  would predict **more** reversal in the volatile quartile; we measure none. The confound therefore
  strengthens the reading rather than undermining it.

| ID | Rule |
|---|---|
| ~~**QA-87**~~ ⚠ **SUPERSEDED → §5.9.1n (v2.0.0)** | ✅ **CLOSED 2026-08-18, and not in the expected direction.** The attention-conditional effect is **excluded at MDE < 3 bps** (§5.9.1h); a signed-gap reversal **does** exist (−7.6 bps, `t = −3.08`, monotone) but is **absent in the high-volatility quartile the ranker selects into** (+1.5 bps, `t = +0.39`) and is **weakening post-2021**. ★ **The adverse-selection concern is retired on evidence, and it ran in the system's favour** |
| **QA-92** | ★ **The right population was never "names this system nominated".** Nominations arrive at ~250/yr with one observation each — that test takes decades. The population that matters is **"names with the characteristics the system selects for"**, and it has **371,971 rows on disk today**. ★ **A conditional hypothesis is tested by conditioning the existing panel, not by waiting for the system to generate a sample** |
| **QA-93** | ★ **A cross-sectional, within-date sort is the default form for any conditional hypothesis here** — it cancels the market factor exactly, where a pooled statistic is swamped by it. §5.9.1i is the demonstration: `t = +0.13` pooled versus `t = −3.08` sorted, **on identical data** |
| **QA-94** | ⚠ **Attention proxies must be strictly lagged to `T−1`.** The signed overnight gap is the one exception — it is observed *at* the `T` open, before the intraday move it predicts, so using it is legitimate and must be stated as deliberate rather than read as leakage |

### 5.9.1k ★★ THE MECHANISM IS ROLL (1984) BID-ASK BOUNCE — and it moves the finding to a different rule

> **Hypothesis supplied by external review, 2026-08-18, and it is confirmed.** Observed prices carry
> microstructure noise, and the **same opening-print noise enters the two legs with opposite signs**:
>
> ```text
>     o_i = log open(T)  − log close(T−1)   ⊃  +ε_open(T) − ε_close(T−1)
>     d_i = log close(T) − log open(T)      ⊃  +ε_close(T) − ε_open(T)
>
>     ⟹  Cov(o_i, d_i) ⊃ −Var(ε_open)      a MECHANICAL negative covariance
>     Roll's estimator inverts it:  ŝ = 2·√(−Cov)
> ```
>
> ★ **The prediction that separates it from a behavioural story:** the artefact scales with the
> **spread**, the genuine move scales with **volatility** — so what governs the effect is the
> **ratio `spread/σ`**, not either one alone.

**Three tests, all on data already held. Corwin–Schultz (2012) supplies the spread from daily H/L.**

**Test 1 — re-sort on the normalised gap `o/σ̂`** (the review correctly identified a **QA-34
violation inside my own diagnostic**: ranking raw bps means a calm name in the top decile is having
a news event while a volatile name is having an ordinary Tuesday, so the quartiles were conditioned
on different things):

| σ quartile | raw gap | **normalised gap** |
|---|---:|---:|
| 0 calmest | −15.85 | **−16.41** (t −9.44) |
| 3 most volatile | −1.35 | **−0.54** (t −0.14) |

★ **The gradient survives normalisation intact** — so that confound was real but is **not** the driver.

**Test 2 + 3 — the 2×2 double sort on volatility × Corwin–Schultz spread**, with each cell's
`spread/σ` shown:

| cell | `spread/σ` | effect | t |
|---|---:|---:|---:|
| high vol / low spread | **0.029** | **−0.91** | −0.40 |
| low vol / low spread | 0.075 | −10.63 | −6.96 |
| high vol / high spread | 0.121 | −11.90 | −4.40 |
| low vol / high spread | **0.154** | **−13.01** | −9.63 |

**`corr(spread/σ, effect magnitude) = +0.895`.** Sorting directly on the ratio:

| `spread/σ` quintile | 0.011 | 0.063 | 0.099 | 0.146 | 0.181 |
|---|---:|---:|---:|---:|---:|
| effect (bps) | **−1.10** | −6.14 | −12.22 | −8.97 | **−17.50** |
| t | −0.44 | −2.56 | −5.58 | −6.14 | **−9.25** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE EFFECT SCALES WITH SPREAD/SIGMA AND VANISHES WHERE THE      ║
║  RATIO IS SMALLEST. THAT IS ROLL'S SIGNATURE, NOT BERKMAN'S.     ║
║                                                                  ║
║  It is MECHANICAL, not behavioural. And it is NOT TRADABLE:      ║
║  you cannot harvest a bounce you would pay the spread to reach.  ║
║                                                                  ║
║  The post-2021 weakening (t 3.29 -> 1.39) corroborates. Retail    ║
║  attention ROSE over that period, so a behavioural mechanism      ║
║  predicts STRENGTHENING; spread compression predicts exactly     ║
║  the decay observed. ★ The time trend is EVIDENCE AGAINST the    ║
║  behavioural reading, not neutral — which is the reviewer's      ║
║  point and I had recorded it as a mere caveat.                   ║
╚══════════════════════════════════════════════════════════════════╝
```

> ⚠ **Two corrections to my own v1.8.0 reasoning.** (i) I wrote that σ and spread are *inversely*
> related here; **measured `corr = +0.112`** — weakly *positive*. The quartile medians misled me and
> the double sort is what settles it. (ii) My "the confound strengthens the reading" argument
> **does not reach**: it assumed reversal scales with *gap magnitude*. Under Roll it scales with
> *spread*, so the argument was answering the wrong mechanism.
>
> Roll-implied vs Corwin–Schultz spread came out at **1.43–1.54×**. That is **not** evidence of a
> behavioural residual: Roll captures *all* negative autocorrelation rather than the bounce alone
> (upward bias) and Corwin–Schultz is known to under-estimate. The ratio sits inside the range the
> two estimators' known biases already explain.

### 5.9.1l ★ Which rule owns the finding — and it is not the one I closed it under

The review's sharpest structural point: **the mechanism determines the owning rule**, not merely the
confidence.

| if | the finding is about | owner |
|---|---|---|
| behavioural | buying at the open is expensive for the names we pick | **QA-87** (adverse selection) |
| ★ **microstructure** | ★ **label quality varying by liquidity** | ★ **QA-79/80** |

| ID | Rule |
|---|---|
| **QA-87** ✅ *binding* | **CLOSED — confirmed, now on mechanism rather than outcome.** No behavioural adverse selection: the attention-conditional effect is excluded at MDE < 3 bps (§5.9.1h), and the signed-gap effect that *did* fire is **Roll bounce** (§5.9.1k), which is mechanical and untradable |
| ~~**QA-79**~~ ⚠ **SUPERSEDED → §5.9.1o (v2.0.0)** | ⚠ **RE-PROMOTED from regime guard (reversing the v1.6.0 downgrade).** Open-anchored labels carry **mechanically negatively-autocorrelated noise whose size scales with `spread/σ`**. This is not a hypothetical regime risk — it is **measured, monotone, and present today** at up to −17.5 bps in the widest-spread quintile |
| ~~**QA-80**~~ ⚠ **SUPERSEDED → §5.9.1o (v2.0.0)** | ⚠ **RE-PROMOTED and is now the load-bearing test.** `sd(Z)` per liquidity decile was downgraded on the grounds that the measured deviation was 0.24 %. ★ **That measurement was of the variance ratio, which is blind to this**: the bounce is a *within-date, cross-sectionally correlated* noise component, exactly the liquidity-correlated heterogeneity QA-80 exists to catch, and exactly what a panel-wide statistic cannot see. **The decile form is the point, not a refinement of it** |
| **QA-95** | ★ **`spread/σ` is the natural axis for label-quality reporting**, not liquidity or volatility alone. It is computable from OHLCV via Corwin–Schultz with no new data, and it predicts the noise contamination of an open-anchored label better than either input separately (`corr = +0.895`) |
| **QA-96** | ★ **Roll's estimator is reported beside Corwin–Schultz, not instead of it.** Two independent OHLCV estimators of the same quantity disagree only when something beyond the bounce is present; agreement is a null result worth having, and the **1.43–1.54× gap here is within their known biases** and must be stated as such rather than read as signal |

> ★ **This is the second time in this thread that the correct disposition was "close one rule and
> re-promote another".** §5.9.1h's result and §5.9.1k's result are about **different things** and
> only the mechanism separates them. A finding filed under the wrong rule would have closed the
> adverse-selection question correctly and silently left a **live label-quality defect unowned**.

### 5.9.1m ⚠ ROLL IS CONFIRMED ORDINALLY AND **FALSIFIED QUANTITATIVELY**

> ★ **The falsifiable half of the test, which v1.9.0 skipped.** Roll makes a **parameter-free**
> magnitude prediction, not just an ordering:
>
> ```text
>     Cov(o,d) ⊃ −s²/4      slope = −(s²/4)/σ_o²      Δo = 3.51·σ_o
>     ⟹  effect = −0.878 · s² / σ_o          ★ nothing fitted
> ```
> **And it is one-sided:** a real spread carries a *permanent* adverse-selection component that does
> **not** bounce, so the fitted coefficient must be **≤ 0.878 in magnitude**.

| cell | σ_o | `s_CS` | effect | **implied `s`** | implied/CS |
|---|---:|---:|---:|---:|---:|
| lo vol / lo spread | 101.4 | 9.7 | −13.28 | **39.2** | 4.05× |
| lo vol / hi spread | 80.4 | 18.9 | −16.40 | **38.7** | 2.05× |
| hi vol / hi spread | 121.5 | 20.9 | −13.03 | **42.5** | 2.03× |
| hi vol / lo spread | 143.6 | 5.1 | +0.50 | 0.0 | — |

```text
╔══════════════════════════════════════════════════════════════════╗
║  REGRESSION THROUGH THE ORIGIN of effect on s²/σ_o:              ║
║                                                                  ║
║      fitted slope = −3.922        Roll predicts −0.878           ║
║      ★ 4.47x TOO STEEP, and the prediction was ONE-SIDED.        ║
║                                                                  ║
║  Bid-ask bounce can account for roughly ONE FIFTH of the         ║
║  effect. It cannot be the whole story, and the ordinal fit       ║
║  (corr +0.895) concealed that completely.                        ║
║                                                                  ║
║  ★ A CORRELATION IS NOT A MECHANISM. v1.9.0 declared Roll        ║
║  "confirmed" on a ranking and skipped the one test that could    ║
║  have refuted it.                                                ║
╚══════════════════════════════════════════════════════════════════╝
```

**The loose thread does not close either.** Re-sorted on the *correct* normaliser `s²/σ_o` — the
review is right that `s/σ` was wrong, since `s²/σ ≠ f(s/σ)` — quintile 3 **still breaks**:

| quintile | 0 | 1 | 2 | **3** | 4 |
|---|---:|---:|---:|---:|---:|
| `s²/σ_o` (bps) | 0.02 | 0.80 | 1.86 | **3.76** | 7.53 |
| effect | +0.42 | −6.46 | −11.49 | **−9.41** | −17.47 |
| t | +0.17 | −3.02 | −5.50 | −5.05 | −8.62 |

### 5.9.1n ★ What survives — and it is the conclusion, not the mechanism

| ID | Rule |
|---|---|
| **QA-97** | ★ **The gap-reversal effect is MECHANICAL but is not fully explained by bid-ask bounce.** Roll accounts for ~1/5 of it. **Non-synchronous trading — a stale opening print corrected by the first trades — produces the same sign, the same liquidity gradient, and is not bounded by the spread**, so it can carry the residual where Roll cannot |
| **QA-98** | ★ **Roll and staleness need not be separated, because no decision hangs on the distinction.** Both are mechanical and **untradable**: you cannot harvest a bounce you would pay the spread to reach, nor a stale print you could not have transacted at. At −17.5 bps against ~20 bps of round-trip spread the effect is **unharvestable regardless of which mechanism carries it** — which is why **QA-87's closure is robust to this section failing** |
| **QA-99** | ★ **Report the parameter-free magnitude test alongside any ordinal one.** `corr = +0.895` looked like confirmation and the magnitude test says the mechanism explains a fifth. **An ordinal fit cannot falsify a quantitative theory**, and a theory admitted on ordinal evidence alone will be believed at the strength of the correlation rather than the strength of the test |

### 5.9.1o ⚠ **QA-79/80 RE-DOWNGRADED — my re-promotion did not reach**

> ★ **The reviewer's pushback is correct, and it survives even after their own mechanism failed.**

Cost the noise in **label** terms. Under QA-77 option (A) both anchors are opens and the two ends are
independent:

| assumed `s` | `Var(ε_open)` | added (2 ends) | **sd inflation of an h=21 label** |
|---|---:|---:|---:|
| 16 bps (CS, typical) | 64 bps² | 128 | **0.0085 %** |
| 24 bps | 144 bps² | 288 | **0.0192 %** |
| ★ 42 bps (the *implied* spread, §5.9.1m) | 441 bps² | 882 | **0.0588 %** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  v1.6.0 DOWNGRADED QA-79/80 ON A MEASURED 0.24% DEVIATION.       ║
║  THIS NOISE IS 0.006-0.06% — FOUR TO TWENTY-EIGHT TIMES BELOW    ║
║  THE THRESHOLD I ALREADY JUDGED TOO SMALL TO MATTER.             ║
║                                                                  ║
║  ★ AND IT HOLDS EVEN AT THE IMPLIED SPREAD — i.e. the pushback   ║
║  survives the failure of the mechanism it was built on.          ║
║                                                                  ║
║  THE v1.9.0 RE-PROMOTION IS REVERSED. The v1.6.0 downgrade       ║
║  stands, on its original grounds.                                ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **QA-79 / QA-80** ✅ *binding* | ⚠ **Downgrade RESTORED (v2.0.0).** They remain **cheap regime guards**. ★ If QA-80 is ever re-promoted it must be **on a separate, stated argument** — the general claim that a per-decile form catches what an aggregate hides is sound, but **this finding is not evidence for it** |
| **QA-100** | ★ **A finding is filed at the strength of its measured consequence, not its intellectual interest.** §5.9.1k–m is the cleanest diagnostic work in this spec and its operational consequence is **approximately zero**: it explains an anomaly, and changes no label, no rule and no decision. ★ **Re-promoting a rule on evidence that does not reach it is the exact mirror of QA-83a's over-retraction — and it is the more tempting direction, because the finding feels important** |
| **QA-101** | ✅ **§5.9.2's "measured IC may fall slightly" is now a number: ~0.02 % (≤0.06 %) — not detectable.** The qualitative hedge is replaced |

### 5.9.2 What this costs, honestly

| | |
|---|---|
| **Opening auctions are noisier than closes** | The open is a single auction print with wider effective spread. Label variance rises somewhat, and measured IC may fall slightly — **that fall is not a degradation, it is the removal of a flattering misalignment** |
| **The entire label set must be rebuilt** | Every horizon, every stored panel. No mixed-anchor panel may exist (QA-72) |
| **Every historical IC, RankICIR, backtest and tuning result was computed close-anchored** | They are **not directly comparable** to post-change numbers. The 25-sweep tuning run and the 8 walk-forward folds all sit on the old anchor |

### 5.9.2a ★ Two cheap wins on the migration

**(i) QA-73 has a one-line universal check.** The adjustment factor is a property of the **date**,
not of the field, so it must be identical across fields:

```text
        adj_close / close  ==  adj_open / open        for every (ticker, date)
```

One vectorised assertion catches splits, dividends **and partial backfills** alike — strictly
stronger than a spot-check on NVDA, because it needs no prior knowledge of *which* dates are
affected. **Per QA-62's precedent, this is the test to write before the change.**

**(ii) The comparability loss is avoidable for one cycle.** §5.9.2 says every historical IC, fold
and tuning result becomes non-comparable. **Build both label sets for one evaluation cycle**, run
the identical fold protocol on each, and report the delta. One extra column and one extra eval pass
buys three things: the migration, a **measured** answer to *"how much IC did the anchor cost"* —
which §5.9.2 currently only guesses at (*"may fall slightly"*) — and a **translation factor** that
makes the 25-sweep run and the 8 walk-forward folds interpretable rather than discarded.

★ **This is the same move §5.3b made for the horizon question**: converting an unmeasurable
*"not comparable"* into a measured offset, and it is available here for far less effort.

| ID | Rule |
|---|---|
| **QA-81** | ★ **The adjustment-consistency invariant `adj_close/close == adj_open/open` is asserted panel-wide before the anchor migration**, and thereafter on every ingest (D-07 §6A's calendar check) |
| **QA-88** | ★ **Report the rank correlation between the final ranking and `σ̂` alone.** QA-58 removes a low-vol tilt from the **fit** and introduces a high-vol tilt in the **ranking** — the first is a bias, the second is economics (higher vol is higher expected return at equal Sharpe). **They must not be conflated in monitoring, or someone will "fix" the second.** Because `Ẑ` is centred the product preserves its sign, so negative-forecast names stay at the bottom and the ranker cannot degenerate into a pure volatility screen — but if `sd(Ẑ)` is small against the cross-sectional spread of `σ̂`, the top pick may nearly always be the highest-vol positive-forecast name. **`ρ(rank, σ̂) > 0.7` means the ranker is closer to a volatility screen than an alpha model**, and QN-7's 1.5× is then a *lower* bound on the σ inflation feeding every MDE in this spec and in D-12 §6 |
| **QA-82** | ★ **One evaluation cycle runs BOTH anchors** under an identical fold protocol, and the IC delta is recorded as the translation factor for all pre-migration results |

> ★ **The last row is the practical consequence to plan for.** Moving the anchor **invalidates the
> comparability of every historical evaluation number in the repo.** That is an argument for doing
> it *now*, before more results accumulate against an anchor production will not use — not an
> argument against doing it.

---

# 6. SCREENS & SIGNALS

| ID | Rule |
|---|---|
| **QA-7** | A screen is a **pure function** of a D-02 panel slice. No fitted parameters, no state, no I/O |
| **QA-8** | A signal is **stateless and named**, and is never called `rank_score` — that name belongs to D-04's fitted output |
| **QA-9** | Any threshold in a screen is **either economically derived** (a cost, a spread) **or declared arbitrary** in its MethodEntry (§8). A tuned threshold is a fitted parameter and belongs to D-04 |
| **QA-10** | A signal reads only the **adjusted** panel where it is scale-invariant, and the **raw** panel otherwise (`L1-feature-engineering.md` FE-9). A 52-week-high screen is a *price-level* comparison and must not be computed on a retro-adjusted series across a split |

> **QA-10 is not hypothetical.** A 52-week-high screen over NVDA's adjusted history compares
> post-split prices to pre-split prices that were divided by 10 — see `L1-data-engine.md` §5C.7.
> Ratio-of-prices survives the adjustment; a level comparison across the split boundary does not.

---

# 7. THE EVALUATION PROTOCOL — D-03's real product

D-04 fits the models. **D-03 decides whether they worked**, and does so with machinery D-04 cannot
reach into (§3).

## 7.1 What a BacktestSpec pins

Universe · window · **horizon set and version** · cost model · **`initial_capital`** ·
CV protocol (purge, embargo) · rebalance cadence · `as_of` and `adj_as_of` · the D-02 contract
version · the D-07 calendar-check id.

> ★ **`initial_capital` added v1.0.0**, and it is not housekeeping. *(Gap identified by external
> review, 2026-08-17.)* **A flat per-trade fee's drag in percentage terms depends entirely on the
> book**: 1.20 %/yr at 1m on $100 k, 0.12 % on $1 M — a **10× spread on the same strategy**. While
> costs were charged at zero the capital base was irrelevant; **the instant QA-50's flip lands it
> becomes a primary determinant of every net return in the repository**, and two backtests that
> differ only in an unstated capital base are not comparable.
>
> `settings.yaml:55` asserts *"$20 round-trip immaterial at realistic capital"* **without stating
> what realistic capital is** — an undeclared convention doing load-bearing work, sitting in the
> very line §5.6a's whole argument was built on. That is precisely the defect **QA-48** exists to
> catch, so QA-48 is extended to cover it.

| ID | Rule |
|---|---|
| **QA-11** | A backtest is **not runnable without a fully pinned spec**. Any unpinned input makes the result unreproducible and therefore inadmissible as evidence |
| **QA-12** | Backtest results are **reported with costs applied** (INV-016) and with the cost assumptions stated. A gross-of-cost result may be shown *beside* a net one, never instead |
| **QA-13** | Backtested returns are **never presented as expected returns** (INV-010). The renderer is told this; the label travels with the number |
| **QA-14** | Survivorship is addressed explicitly (INV-017) using D-07's `delisted-companies`. A backtest over currently-listed names only is reported as **biased**, not as a result |

## 7.2 Metric gates

| ID | Rule |
|---|---|
| **QA-15** | A metric gate declares **the statistic, the threshold, the effective N, and the corrected standard error** (QA-4). A gate that reports only "0.031 ≥ 0.03 → PASS" is not a gate |
| **QA-16** | Gates are evaluated **per horizon**, never on a pooled statistic across horizons (QA-5) |
| **QA-17** | A gate whose statistic cannot be computed reports **`NOT_EVALUATED`**, never a pass. *(`L1-data-engine.md` DE-35 and `L1-fundamental-analysis.md` RA-30, applied here — the same rule in a third domain)* |
| **QA-123** | ★★ **The flat commission is `9.95`, MEASURED — not the `10.00` asserted at `backtester.py:14-18`.** ⚠ *Added 2026-08-25.* That line reads *"BROKER REALITY: flat $10 per trade"* and **137 real BMO InvestorLine orders** (2022-01-01 → 2026-08-25) put it at **9.95 exactly on 100 of them, in CAD and USD alike** (D-11 **RC-43**). ★ The 0.5 % error is trivial per trade and **is not trivial where §5.6a uses it**: ground (b) turns on a cost *differential* that flips sign at 3–12 bps, and **an unsourced constant doing load-bearing work is exactly what QA-48 exists to catch.** ⚠ It now carries its source and check date (L4 **CN-2**) |

> **QA-17 has a live precedent.** F0 **D-18**: every candidate in the sleeve optimiser failed,
> `best_sharpe` stayed at `-inf`, the untouched defaults were adopted — and **`phase3b` still
> reported PASS**, for over a month, across 8 of 8 folds. A gate that cannot fail is decoration.

## 7.3 Cross-validation

| ID | Rule |
|---|---|
| **QA-18** | Purge and embargo lengths are **derived from the horizon set**, not configured independently. Changing the horizon set changes them automatically, or they will be wrong the first time someone forgets |
| **QA-19** | Where a design replicates rows across horizons (Option C), CV groups on `(ticker, date)` so **all copies of a row fall in the same fold** |

---

# 8. MATHEMATICAL PROVENANCE — required for every quant method

> **Scope note: this binds D-02, D-03, D-04, D-05 and D-06**, not only this domain. It is written
> here because D-03 is where it was first required; it belongs in `L4-coding-standards.md` when
> §§2–13 of that document are drafted, and is recorded as **QQ-7** until then.

## 8.1 Why

A formula in this codebase is read by three audiences who cannot check it: the next engineer, an AI
agent, and Victor. Undocumented, it is indistinguishable from a correct one. Two live examples:

- **D-16 — `rsi_14`.** It uses a simple 14-day rolling mean where essentially every charting
  package and TA library uses **Wilder smoothing** (EMA, α=1/14). The two diverge materially. The
  code carries no statement of which definition it implements, no citation, and no note that a
  choice was made — so for years it read as *the* RSI.
- **D-19 — the DCF.** It discounts a firm-level cash flow at WACC (correct, produces an enterprise
  value) and then divides by share count **without subtracting net debt**. The variable is even
  named `entity_value`. No derivation, no reference, and the error scales with leverage — 455% of
  market cap on CHTR.

**Neither was a coding error. Both were an unstated modelling choice that later read as fact.**

## 8.2 The MethodEntry

Every `formula_id` — the identifier `L1-feature-engineering.md` FE-2 already requires on every
feature — resolves to exactly one MethodEntry.

```markdown
## formula_id: rank_ic.spearman.v1

### Statement
        ρ_t = 1 - (6 · Σ d_i²) / (n(n² - 1))
        RankIC = mean_t(ρ_t)   ·   ICIR = mean_t(ρ_t) / sd_t(ρ_t)

### Symbols
  ρ_t   Spearman rank correlation between predicted and realised
        cross-sectional ranks on date t
  d_i   rank difference for name i on date t
  n     number of names scored on date t  (NOT the number of rows)

### Reference
  Spearman, C. (1904). "The Proof and Measurement of Association between
  Two Things." American Journal of Psychology 15(1), 72-101.
  ICIR as an information-ratio-of-IC: Grinold & Kahn (2000),
  *Active Portfolio Management*, 2nd ed., Ch. 6 (the Fundamental Law).

### Assumptions
  - ρ_t are treated as independent across t.  ** VIOLATED under overlapping
    horizons (§5.3) — corrected per QA-4, and the correction is part of
    this method, not an optional extra. **
  - n_t is large enough for ρ_t to be meaningful; n_t < 10 is reported
    as NOT_EVALUATED (QA-17).

### Chosen over
  - Pearson IC: rejected — sensitive to outliers, and the decision is a
    RANKING (INV-6 takes the top-1), so rank correlation matches the use.
  - Kendall's tau: defensible; rejected for cost at O(n²) and for
    comparability with the published literature, which reports Spearman.

### Known-answer test
  Perfectly ordered input => ρ = 1.  Reversed => ρ = -1.
  Grinold & Kahn's worked example reproduces to 4 dp.

### House variant?  NO — standard definition.
```

## 8.3 Rules

| ID | Rule |
|---|---|
| **QA-20** | Every `formula_id` resolves to a MethodEntry carrying: **statement · symbol definitions · reference · assumptions · what it was chosen over · a known-answer test** |
| **QA-21** | A **citation is specific**: author, year, title, and edition/chapter/equation where one exists. *"See López de Prado"* is not a citation; *"López de Prado (2018), Advances in Financial Machine Learning, §7.4.1 (purged k-fold)"* is |
| **QA-22** | ★ **A method with no external reference is declared a HOUSE VARIANT explicitly**, with the reason it deviates and what it deviates *from*. This is the rule that would have caught D-16 the day it was written |
| **QA-23** | **Assumptions must name the ones this system violates**, and point at the correction. An assumptions list that only lists satisfied assumptions is marketing |
| **QA-24** | Every MethodEntry has a **known-answer test** — a case whose result is derivable independently (a closed form, a textbook worked example, a hand calculation). *This is `L1-data-engine.md` §6A.5's known-answer principle applied to mathematics rather than to data* |
| **QA-25** | Changing the mathematics changes the `formula_id` (FE-2), which changes the contract version, which fails parity **loudly** for every model fitted on the old one. **The MethodEntry and the code are amended in the same commit** — a stale entry is worse than none, because it is trusted |

> **QA-22 deserves its star.** The failure mode is not writing a wrong formula. It is writing a
> *defensible variant* and leaving no trace that a choice was made — after which every subsequent
> reader, human or agent, assumes the standard definition. `rsi_14` is that failure exactly, and it
> is now baked into every trained model.

## 8.4 Reference list — the claims in §5 and §9, sourced

**§8's own rule applied to §5.** Every non-obvious quantitative claim in this spec is listed with
its source, so a reader (human or agent) can check it rather than trust it. Entries marked
**[derived]** are worked out in this document and were verified numerically on 2026-08-16.

### Horizon, decay and sampling

| Claim | Source |
|---|---|
| `IC(h) ∝ (1−e^(−h/τ))/√h`; `h* = 1.2564τ = 1.813 × half-life` | **[derived]** §5.3a. Root of `e^u = 2u+1` |
| `h*/τ` under noise `∝ h^H`: root of `u·e^(−u)/(1−e^(−u)) = H` | **[derived]** §5.3a |
| `SE(mean rank IC) ≈ √(h/((n−1)T))`; Spearman `ρ` has null variance `1/(n−1)` | **[derived]** §5.3b, from the standard asymptotic `ρ√(n−1) ~ N(0,1)` |
| Purged k-fold CV with embargo | López de Prado, M. (2018). *Advances in Financial Machine Learning*, Wiley — **Ch. 7** (§7.4.1 purging, §7.4.2 embargo) |
| Average uniqueness / concurrent labels / sequential bootstrap | ibid., **Ch. 4** (§4.3–§4.5) |
| Triple-barrier labelling, barriers at `k·σ̂·√h` | ibid., **Ch. 3** (§3.4); meta-labelling §3.6 |
| Deflated Sharpe ratio (selection bias, backtest overfitting) | Bailey, D. & López de Prado, M. (2014). "The Deflated Sharpe Ratio." *Journal of Portfolio Management* 40(5), 94–107 |
| `t > 3` threshold for a new factor after multiple testing | Harvey, C., Liu, Y. & Zhu, H. (2016). "…and the Cross-Section of Expected Returns." *Review of Financial Studies* 29(1), 5–68 |
| Direct vs iterated multi-step forecasting | Chevillon, G. (2007). "Direct Multi-step Estimation and Forecasting." *Journal of Economic Surveys* 21(4), 746–785. **Note:** Marcellino, Stock & Watson (2006), *J. Econometrics* 135, find *iterated* often wins for macro — so "never recurse" is not a general law. It holds **here** because 1-step equity SNR is near zero, which is the condition under which iterated compounds noise |

### Volatility estimation

| Claim | Source |
|---|---|
| Range estimator, ~5× efficiency | Parkinson, M. (1980). "The Extreme Value Method for Estimating the Variance of the Rate of Return." *Journal of Business* 53(1), 61–65 |
| OHLC estimator, ~7.4× efficiency | Garman, M. & Klass, M. (1980). "On the Estimation of Security Price Volatilities from Historical Data." *Journal of Business* 53(1), 67–78 |
| Drift-independent estimator | Rogers, L.C.G. & Satchell, S. (1991). "Estimating Variance from High, Low and Closing Prices." *Annals of Applied Probability* 1(4), 504–512 |
| **Handles overnight gaps + drift; up to ~14× efficiency — QA-35's default** | Yang, D. & Zhang, Q. (2000). "Drift-Independent Volatility Estimation Based on High, Low, Open, and Close Prices." *Journal of Business* 73(3), 477–491 |
| Multi-scale volatility cascade (HAR-RV) | Corsi, F. (2009). "A Simple Approximate Long-Memory Model of Realized Volatility." *Journal of Financial Econometrics* 7(2), 174–196. **Note:** HAR's cascade is over *predictor lookbacks* (daily/weekly/monthly RV), not over *forecast horizons* — it is the multi-scale-**feature** idea (build step 5), not a multi-horizon output architecture |

### What is realistically achievable

| Claim | Source |
|---|---|
| Monthly out-of-sample `R²` ≈ 0.4% for individual stocks with ML | Gu, S., Kelly, B. & Xiu, D. (2020). "Empirical Asset Pricing via Machine Learning." *Review of Financial Studies* 33(5), 2223–2273 |
| ↳ **calibration note** | `R² ≈ IC²` for a univariate predictor, so `R² = 0.4%` ⇒ `IC ≈ 0.063`. **An IC of 0.03–0.06 is the realistic target band** — §5.3b's examples are in range. Note their setting: ~94 characteristics, ~30k stocks, 60 years. With 130 names and <10 years, expect less |
| Fundamental law `IR = IC·√BR`; alpha horizons | Grinold, R. & Kahn, R. (2000). *Active Portfolio Management*, 2nd ed., McGraw-Hill — Ch. 6 |
| **Low-volatility / betting-against-beta anomaly** — the tilt QA-45 neutralises | Frazzini, A. & Pedersen, L.H. (2014). "Betting Against Beta." *Journal of Financial Economics* 111(1), 1–25 |
| ↳ transfer coefficient under constraints | Clarke, R., de Silva, H. & Thorley, S. (2002). "Portfolio Constraints and the Fundamental Law of Active Management." *Financial Analysts Journal* 58(5), 48–66 |
| **Combining signals of different decay under transaction costs** — the precise form of "IC per unit turnover" (QA-40) | Gârleanu, N. & Pedersen, L.H. (2013). "Dynamic Trading with Predictable Returns and Transaction Costs." *Journal of Finance* 68(6), 2309–2340. Their result: the optimal portfolio partially trades toward an *aim* portfolio that **over-weights slow-decaying signals**, precisely because fast signals cost more to hold onto |

### Architecture

| Claim | Source |
|---|---|
| Direct multi-horizon + quantile loss + covariate typing | Lim, B., Arık, S.Ö., Loeff, N. & Pfister, T. (2021). "Temporal Fusion Transformers for Interpretable Multi-Horizon Time Series Forecasting." *International Journal of Forecasting* 37(4), 1748–1764 |
| Multi-horizon quantile outputs from a shared encoder | Wen, R., Torkkola, K., Narayanaswamy, B. & Madeka, D. (2017). "A Multi-Horizon Quantile Recurrent Forecaster." NIPS Time Series Workshop |
| Simple linear models beat transformers on long-horizon benchmarks | Zeng, A., Chen, M., Zhang, L. & Xu, Q. (2023). "Are Transformers Effective for Time Series Forecasting?" *AAAI 2023* |
| Trees still beat deep learning on tabular data | Grinsztajn, L., Oyallon, E. & Varoquaux, G. (2022). "Why do tree-based models still outperform deep learning on typical tabular data?" *NeurIPS 2022 Datasets & Benchmarks* |
| ↳ corroborating | Shwartz-Ziv, R. & Armon, A. (2022). "Tabular Data: Deep Learning is Not All You Need." *Information Fusion* 81, 84–90 |
| Reservoir computing / echo state networks | Lukoševičius, M. & Jaeger, H. (2009). "Reservoir computing approaches to recurrent neural network training." *Computer Science Review* 3(3), 127–149. **Assessment:** only the readout is fitted, which is attractive at ~80 effective samples — but spectral radius, leak rate and reservoir size are still tuned, which reimports the overfitting. At that sample count the right complexity class is a **3-parameter decay curve**, not a reservoir |
| Parsimonious 3-factor curve basis (level/decay/curvature) | Nelson, C. & Siegel, A. (1987). "Parsimonious Modeling of Yield Curves." *Journal of Business* 60(4), 473–489. **House variant flag (QA-22):** applying NS to an *expected-return decay* term structure is a transfer from the yield-curve literature, **not** an established equity method. Related but distinct: van Binsbergen & Koijen (2017), "The term structure of returns: Facts and theory," *JFE* 124(1) |

---

## 8.4 ★ SUPERSESSION — how a rule that changed is written

> ⚠ **Added after a consistency audit found `QA-87` defined three times and `QA-77/79/80` twice
> each, with nothing saying which one binds.** A reader scanning top-down met QA-79 as *downgraded*,
> then *re-promoted*, then *restored*. **Only the last was binding and the document did not say so.**

| ID | Rule |
|---|---|
| **QA-116** | ★ **A rule ID has exactly ONE binding definition.** When a rule changes, the superseded row is marked **`~~QA-n~~ ⚠ SUPERSEDED → §x`** and the binding row is marked **`✅ binding`**. Neither is deleted — the history is the argument — but **exactly one is in force and it is legible without reading the whole document** |
| **QA-117** | ★ **A section rewrite carries forward every rule definition inside it.** The same audit found **`DN-16/17/18` deleted by a §6 rewrite while still cited five times**, including by an acceptance criterion. **A rule that is referenced and undefined is worse than one that is wrong** — it reads as authority nobody can check |
| **QA-118** | ★ **This document is written by accretion and that is deliberate** — the retractions and reversals *are* the evidence. **The cost is that supersession must be explicit**, or accretion becomes ambiguity. QA-116 is what makes the style safe |

# 9. REVIEW — is the three-head bundle the right design?

> ⚠ **§9 was written before the horizon decision (v0.5.0) and has been re-aligned, not rewritten.**
> Two consequences a reader must carry through it:
>
> 1. **Everything in §9.1 is stated at `h = 5`, because that is what the code does.** Under
>    HorizonSet v1 (§5.6), 5 days is the **timing** horizon; the selection leg is 21 days. So
>    §9.1 accurately describes a bundle that is **fitted to the wrong objective for the job it is
>    being used for** — decision consequence #1 — and every V-claim below is true of code that is
>    slated for retrain.
> 2. **§9.4's original sort filed Option 5 under "research".** §5.6's QQ-2 approved it as the
>    **production decomposition**. Corrected in §9.4.

> **The decision is D-04's.** D-03 raises it because D-03 owns the evaluation protocol, and the
> protocol is where the answer will come from.

## 9.1 What the three heads actually are — code and mathematics

> **Written for external validation.** Every claim below is traceable to a file and line in
> `pipeline/`, or is a formula another agent can re-derive. §9.1.7 lists the falsifiable claims
> explicitly. Verified against **LightGBM 4.6.0** on 2026-08-17.

### 9.1.1 The labels — `pipeline/ohlcv/dataset/label_builder.py`

One forward return is computed; **all three labels are derived from it**.

```python
# label_builder.py:86-92
df["fwd_ret_1w"]   = df.groupby("ticker")["adj_close"].shift(-5)
df["fwd_ret_1w"]   = (df["fwd_ret_1w"] - df["adj_close"]) / df["adj_close"]
df["label_up_1w"]  = (df["fwd_ret_1w"] > self.cls_threshold).astype(int)
df["rank_label_1w"]= df.groupby("date")["fwd_ret_1w"].transform(
                         lambda x: _cross_section_rank(x, n_bins=5))
```

Formally, writing `R_{i,t}` for the forward return of name `i` at date `t`:

```
    R_{i,t}   = P_{i,t+5} / P_{i,t} − 1                    simple return, NOT log
    y^reg     = R_{i,t}
    y^cls     = 1[ R_{i,t} > c ] ,   c = 16 bps = 0.0016
    y^rank    = ⌊ 5 · F̂_t(R_{i,t}) ⌋ ∈ {0,1,2,3,4}
```

where `F̂_t` is the **empirical CDF within date `t`** (`pd.qcut(q=5, labels=False,
duplicates="drop")`), and

```
    c = (spread 5 + slippage 10 + commission 1) / 10,000 = 0.0016      # label_builder.py:70-78
```

`P` is `adj_close` — the **split-and-dividend-adjusted** series, which is restated data (§5C.7 of
`L1-data-engine.md`). Rows with null `fwd_ret_1w` or null `rank_label_1w` are dropped.

**Three things worth noting for validation:**

1. ⚠ **`c` is NOT what v0.6.0 said it was, and the "economically meaningful threshold" framing is
   withdrawn.** Three corrections, established in **§5.6a**:
   - **The `5 + 10 + 1` sum is dead code.** `settings.yaml:247` sets `costs.cls_threshold_bps: 16`
     directly, so `c = 0.0016` is a **hard-coded constant that happens to equal that sum**, not a
     decomposition of spread, slippage and commission.
   - **The one-way / round-trip convention is nowhere declared.** v0.6.0 called it round-trip;
     §5.6 called the same number one-way. Neither was reading the repository, because the
     repository does not say.
   - **The backtester does not use a bps cost model at all** — it charges a flat `$10` per trade
     (`backtester.py:18`), and `charge_transaction_cost` defaults to **`false`**.

   And the framing fails on its own terms regardless of which figure is right, because the
   threshold is negligible against the horizon's own noise (σ_ann = 30 %):

   | Horizon | 1σ of the horizon return | `c` = 16 bps | `c` = 32 bps |
   |---|---|---|---|
   | 1w | 4.23 % | **0.038 σ** | 0.076 σ |
   | 1m | 8.66 % | 0.019 σ | **0.037 σ** |
   | 1q | 15.00 % | 0.011 σ | 0.021 σ |

   **`y^cls` is `1[R > 0]` with a rounding error** — a sign test, not an economic test. An
   economic threshold has to **scale with the horizon's noise**, `k · σ̂_i · √h`, which is exactly
   §5.4a's triple-barrier construction (QA-34's classification analogue). *(Credit: this reading
   came from external review, 2026-08-17.)*
2. Simple returns, not log. Simple returns are **not additive across time**, which is why the
   cross-horizon consistency penalty in §5.5 would need log returns.
3. `y^rank` is **not a pointwise function of `R_{i,t}`** — it depends on the whole cross-section on
   date `t`. §9.1.5 turns on this.

### 9.1.2 The three objectives — `pipeline/ohlcv/models/lightgbm_models.py:83-98`

```python
_COMMON_DEFAULTS = {"boosting_type":"gbdt", "num_leaves":31, "learning_rate":0.05,
                    "feature_fraction":0.9, "bagging_fraction":0.8, "bagging_freq":5,
                    "min_data_in_leaf":20, "verbose":-1}
_ROLE_DEFAULTS = {
    "ranker":     {"objective":"lambdarank", "metric":"ndcg"},
    "regressor":  {"objective":"regression", "metric":"rmse"},
    "classifier": {"objective":"binary",     "metric":"binary_logloss"},
}
```

Train/validation: a **chronological 80/20 split on unique dates** (`_make_time_split`), early
stopping 50 rounds. Ranker `group` = `X.groupby("date").size()` — one query per date.

#### (a) Ranker — LambdaRank

Optimises a smoothed NDCG. For a query (here **one date**) with scores `s_i` and labels `y_i`, the
lambda gradient for a pair `(i, j)` with `y_i > y_j` is

```
    λ_ij = −σ / (1 + exp(σ (s_i − s_j))) · | ΔNDCG_ij |
    λ_i  = Σ_{j : y_i > y_j} λ_ij  −  Σ_{j : y_j > y_i} λ_ji
```

where `ΔNDCG_ij` is the change in NDCG from swapping `i` and `j`, and

```
    DCG@k = Σ_{i=1..k}  g(y_i) / log₂(i + 1) ,     NDCG@k = DCG@k / IDCG@k
```

- **Reference:** Burges, C. (2010). *From RankNet to LambdaRank to LambdaMART: An Overview.*
  Microsoft Research MSR-TR-2010-82. NDCG: Järvelin & Kekäläinen (2002), *TOIS* 20(4), 422–446.
- **Output:** an unbounded real score. **Ordinal within a date only** — it is not calibrated and
  carries no cross-date meaning.

#### (b) Regressor — L2

```
    L = Σ_i ( R_i − ŷ_i )²          leaf value = mean residual in the leaf
```

Output is in **return units**. L2 is maximally sensitive to the tails of a heavy-tailed,
heteroskedastic target — one +40 % week dominates many ordinary ones. This is precisely what
QA-34's volatility normalisation addresses.

#### (c) Classifier — binary logistic

```
    p̂ = σ(F(x)) = 1 / (1 + e^{−F(x)})
    L = − Σ_i [ y_i log p̂_i + (1 − y_i) log(1 − p̂_i) ]
```

Output is `P̂(R > 0.0016)`. **Verified 2026-08-17:** LightGBM's `Booster.predict` returns the
probability (not the raw score) for `objective="binary"`, so `predict_proba` delegating to
`predict` (`lightgbm_models.py`) is correct.

### 9.1.3 The bundle output — `model_bundle.py:180-192`

```python
return pd.DataFrame({
    "rank_score":  self.ranker.predict(Xf),                       # unbounded, ordinal-in-date
    "pred_return": self.regressor.predict(Xf),                    # return units
    "prob_up":     np.clip(self.classifier.predict_proba(Xf), 0, 1),
})
```

The code comment at `model_bundle.py:168` states it outright: **"the three models are
INDEPENDENT"** — three separate fits over the same `X`, no shared parameters, no shared trunk.

### 9.1.4 The blend — `pipeline/ohlcv/policy/sleeve_selector.py:207-223`

```
    z(·)          = cross-sectional standardisation within the scored frame
    opportunity_i = c_rank · z(rank_score)_i + c_ret · z(pred_return)_i + c_prob · z(prob_up)_i
    adj_opportunity_i = opportunity_i − penalty_i
```

- Weights are fitted by **grid search on backtest Sharpe** over
  `rank ∈ [0.50, 0.75)`, `return ∈ [0.30, 0.45)`, `prob ∈ [0.00, 0.25)`, step **0.05**
  (`sleeve_selector.py:253-258`). **They are not constrained to sum to 1** — the grid admits sums
  from 0.80 to 1.45.
- Fallback if `policy_params.json` is unreadable: `{rank 0.6, return 0.3, prob 0.1}`.
  Production before D-18 was `{0.65, 0.35, 0.0}`; after the fix, `{0.50, 0.30, 0.20}`.
- `SignalEngine.combined_score` then blends `ohlcv_score` with `fundamental_composite` and
  `technical_score`, again as cross-sectional z-scores with renormalised weights.

### 9.1.5 The information-content claim — **corrected and sharpened**

> **v0.1.0 said "all three are deterministic functions of one variable, `fwd_ret_1w`." That is too
> loose and an external validator should reject it as stated.** `y^rank` depends on the entire
> cross-section on date `t`, not on `R_{i,t}` alone. The precise version follows.

**Claim 1 — no independent information.** Conditional on the realised cross-section
`{R_{j,t}}_{j ∈ t}`, all three labels are **deterministic**. There is no second data source, no
second target variable, and no additional observation. The bundle is therefore not an ensemble over
different information; the diversity lives in the **loss function** and in **which functional of
`R` is being fitted**.

**Claim 2 — but they are not the same functional.** They differ in what they are invariant to:

| Label | Invariant to a date-level **additive** shift? | to a date-level **scale** change? |
|---|---|---|
| `y^reg = R` | **no** | no |
| `y^cls = 1[R > c]` | no | no |
| `y^rank = ⌊5·F̂_t(R)⌋` | **yes** | **yes** |

So the ranker's target is **approximately market-neutral** — a common move across the cross-section
does not change ranks — while the other two carry the market component. *(Approximately, not
exactly: heterogeneous beta means a market move does reorder the cross-section — the same
correction §5.3b applies to effective breadth.)* **That is a real informational difference, and
v0.1.0 obscured it.**

**Claim 3 — the blend then largely undoes that difference.** `compute_opportunity` applies
`z(·)` **cross-sectionally to all three columns before weighting**. Cross-sectional
standardisation removes the date-level location and scale — exactly the component that
distinguished `pred_return` and `prob_up` from `rank_score`.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE RANKER'S TARGET IS MARKET-NEUTRAL BY CONSTRUCTION.          ║
║  THE OTHER TWO ARE NOT — UNTIL THE BLEND Z-SCORES THEM,          ║
║  WHICH NEUTRALISES THEM TOO.                                     ║
║                                                                  ║
║  So the three heads enter the blend carrying near-identical      ║
║  information about the SAME underlying variable, differing       ║
║  mainly in the robustness properties of three loss functions:    ║
║                                                                  ║
║    lambdarank  — invariant to monotone transforms, outlier-robust║
║    L2          — efficient under Gaussian error, tail-dominated  ║
║    logloss     — discretised at an ECONOMIC threshold (16 bps)   ║
║                                                                  ║
║  That is a LOSS ENSEMBLE, not an information ensemble.           ║
║  It is defensible. It is not what "three-model bundle" implies.  ║
╚══════════════════════════════════════════════════════════════════╝
```

**This is the corrected basis for §9.4's recommendation**, and it is stronger than v0.1.0's: the
case for collapsing to one ranking head plus a calibrated band does not rest on the heads being
identical, but on the **blend's own z-step erasing the one dimension along which they differed**.

#### ⚠ Claim 3 has an expiry date: **build step 2**

> Raised by external review 2026-08-17, and sharpened here.

Claim 3 holds for the **raw-return labels the code uses today**. Under **QA-34** the target becomes
`Z_i = R_i / (σ̂_i √h)`, and `σ̂_i` is a **per-name** quantity. Cross-sectional z-scoring removes a
**date-level** location and scale; **it cannot remove a name-level rescaling.**

The reviewer framed this as "the heads diverge after step 2". The sharper statement is that
**QA-34 forces a decision that has not been made** — whether `y^rank` is normalised too:

| Branch | `y^reg` | `y^rank` | Consequence |
|---|---|---|---|
| **(i) normalise both** | `Z_i` | quintile of `Z_i` | Claim 3 **survives** — the invariance analysis repeats verbatim with `Z` in place of `R`. But the *ranking itself* is now risk-adjusted, so **QA-45's low-vol tilt lands in the selection decision**, which is the sharpest place it could land |
| **(ii) normalise only the regression target** | `Z_i` | quintile of `R_i` | Claim 3 **breaks** — `pred_return` carries a per-name division that the blend's z-step cannot erase, and the two heads differ in a dimension the blend cannot reach |

**Ranking `R_i` and ranking `R_i/σ̂_i` are different rankings** whenever `σ̂` varies across names,
which it always does. So there is no neutral option: branch (i) puts the BAB tilt in the ranking,
branch (ii) breaks the loss-ensemble argument. **QA-45's neutralisation is what decides which of
those is signal**, and the choice must be recorded in the HorizonSet, not discovered in an
implementation. **Recorded as QQ-18.**

### 9.1.6 Undeclared defaults, and one dimensional inconsistency

**Four LightGBM lambdarank parameters are never set in this repository**, so their defaults govern
and nothing records that a choice was made — precisely what **QA-22** exists to catch:

| Parameter | LightGBM default | Consequence here |
|---|---|---|
| `label_gain` | `2^i − 1` ⇒ `[0, 1, 3, 7, 15, …]` | With quintile labels 0–4, the top bucket is weighted **15×** the second-from-bottom. **Favourable by accident** — INV-6 takes the top-1 — but undeclared |
| `lambdarank_truncation_level` | **30** | With ~130 names per date, pairs beyond rank 30 are truncated: the objective effectively **ignores the bottom ~100 names** |
| `sigmoid` | 1.0 | the `σ` in the λ formula |
| `eval_at` / `ndcg_eval_at` | `[1..5]` | early stopping is driven by **NDCG@1–5**, i.e. top-5 quality |

None is wrong. **All four are load-bearing and unrecorded**, and each needs a MethodEntry (QA-20).

**A dimensional inconsistency in the turnover penalty** (`sleeve_selector.py`,
`_turnover_penalty`):

```python
penalty = is_new_position * (self.turnover_penalty_bps / 10_000.0)   # = 10/10_000 = 0.001
df["adj_opportunity"] = df["opportunity"] - penalty
```

`opportunity` is a **weighted sum of z-scores** with standard deviation of order **1.0**. The
penalty is **0.001** — i.e. about **0.1 % of one standard deviation**. The docstring says *"a new
name must beat the held one by at least the penalty"*, which is arithmetically true and
**practically a no-op**: a basis-point quantity is being subtracted from a dimensionless one.
Either the penalty belongs in return units (applied to `pred_return` before z-scoring) or it needs
recalibrating in z-units. **Recorded as QQ-16.**

### 9.1.6a The turnover penalty, sized correctly — and why two prior attempts failed

*(Added v0.8.0. The correct derivation came from external review, 2026-08-17.)*

§9.1.6 established the penalty is inert (`0.001` against `sd(opportunity) ≈ 1`). Sizing it needs
the answer to: **how much expected return does one unit of `opportunity` buy?** That is the slope
of **realised return regressed ON opportunity** —

```
    β = Cov(R, opp) / Var(opp) = ρ · sd(R) / sd(opp)
```

At `ρ = IC = 0.03`, `sd(R₂₁) = 0.30·√(21/252) = 8.66 %`, `sd(opp) = 1`:

```
    β = 0.03 × 0.0866 = 0.0026     ⇒  one unit of opportunity ≈ 26 bps of expected return
    penalty_z = rt / β
```

| Recipe | `penalty_z` at `rt = 32 bps` | Status |
|---|---|---|
| current code (`bps/10⁴`) | **0.001** | inert — the defect |
| `rt / sd(pred_return)` | 0.11 – 0.21 | ✗ assumes the model is perfectly calibrated (`ρ = 1`) |
| `c_ret · rt / sd(pred_return)` | 0.032 – 0.064 | ✗ **mine, v0.7.0** — same error, scaled by the blend weight |
| **`rt / β`** | **1.23** | ✓ correct |
| `rt / β` at `rt = 4 bps` (commission @ $250 k) | 0.15 | ✓ correct, different `rt` |

**Why the first two fail.** Both treat one z-unit of `pred_return` as worth `sd(pred_return)` of
realised return. That holds only if the model is perfect. With `IC = 0.03`, predictions are
enormously over-dispersed relative to the true conditional mean: `E[R | z_pred] = ρ · sd(R) · z_pred`,
so a one-z move buys `ρ·sd(R) = 26 bps`, **not** `sd(pred_return) ≈ 1.5–3 %`.

> ⚠ **And v0.7.0's proposed empirical fix was the reciprocal regression.** It said *"regress
> opportunity on realised return, penalty = rt × slope."* That slope is `ρ·sd(opp)/sd(R) = 0.346`,
> giving `penalty = 0.0011` — **essentially the broken value it was meant to replace.** The two
> *slopes* differ by `sd(opp)²/sd(R)² ≈ 133×`; the resulting **penalties** differ by **`1/ρ² ≈
> 1111×`**, because one recipe divides by a slope and the other multiplies by its reciprocal.
> The empirical instinct was right and the direction was backwards:
> **regress realised forward return ON opportunity, then `penalty = rt / slope`.**

| ID | Rule |
|---|---|
| **QA-60** | ★ *(corrected v0.9.0)* A turnover or churn penalty is expressed in the **units of the score it is subtracted from**, calibrated as `rt / β` where `β = ρ · sd(R) / sd(score)` is the slope of **realised return regressed ON that score**. **Two distinct errors, with two distinct factors:** a penalty left in **return units** is off by **`1/β`**; calibrating it by regressing the *score on returns* instead is off by a further **`1/ρ²`**. `β` uses the **Pearson** correlation between the score and forward return — **not** the Spearman IC used everywhere else in this document |

> **v0.8.0 attributed the wrong factor to the wrong defect.** It said the code is *"off by `1/ρ²`,
> three orders of magnitude"*. `1/ρ²` is the gap between the **two proposed fixes**, not the code's
> error. *(Correction from external review, 2026-08-17.)* The code's error decomposes cleanly:

| Factor | Source | At `ρ = 0.03` |
|---|---|---|
| `rt / penalty_bps` | the code uses `turnover_penalty_bps = 10` where the round trip is 32 bps | **3.2×** |
| **`1/β`** | ★ **return units used directly as score units — this is QA-60's subject** | **385×** |
| **total** | `0.001 → 1.232` | **1232×** |
| *(separately)* `1/ρ²` | wrong-regression fix vs right-regression fix | 1111× |

**Both precision notes matter, and §8 requires them stated rather than assumed:**

- **`1/β` is IC-dependent.** 385× at `ρ = 0.03`; **231× at 0.05; 115× at 0.10.** "Three orders of
  magnitude" is true only at the low end and must be quoted **with its IC**.
- **`β` needs Pearson, the rest of this document uses Spearman.** Under bivariate normality
  `ρ_S = (6/π)·arcsin(ρ_P/2) ≈ 0.955·ρ_P`, so a Spearman IC understates the Pearson by **≈ 4.5 %**
  — small here, but returns are not bivariate normal and the relation is indicative only. **State
  which correlation a `β` was computed from** (QA-20, QA-23).

#### The economic reading — and it endorses M-3 independently

At `IC = 0.03` the correct penalty is of order **one full σ of `opportunity`**.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A MODEL THAT BARELY SEPARATES NAMES SHOULD ALMOST NEVER PAY A   ║
║  CERTAIN COST TO CHASE AN UNCERTAIN 26 BASIS POINTS.             ║
║                                                                  ║
║  M-3 says: "sell less and let winners run"; "hold winners, trim  ║
║  rather than exit".                                              ║
║                                                                  ║
║  A correctly-sized turnover penalty produces that behaviour on   ║
║  its own, from the arithmetic, with no mandate input at all.     ║
║                                                                  ║
║  That is a stronger endorsement of the mandate than anything in  ║
║  §5.6 — and unlike ground (b), IT SURVIVES.                      ║
╚══════════════════════════════════════════════════════════════════╝
```

**Coupling, stated so it is not rediscovered:** `penalty_z` spans **0.15 → 1.23** across the
plausible `rt` range, so **QQ-16 cannot close numerically before QQ-20**. The diagnosis is closed;
the number is not.


### 9.1.7 Claims for the validating agent to check

Each is falsifiable from the repository or by re-derivation.

| # | Claim | How to check |
|---|---|---|
| **V-1** | All three labels derive from one variable, `fwd_ret_1w` | `label_builder.py:86-92` |
| **V-2** | `y^rank` is a function of the cross-section, not of `R_i` alone | `groupby("date").transform(_cross_section_rank)` |
| ~~**V-3**~~ | ~~`c = 0.0016` and is round-trip transaction cost~~ | ❌ **FALSIFIED 2026-08-17.** `c = 0.0016`, but the `5+10+1` branch is **dead code** (`settings.yaml:247` sets `cls_threshold_bps: 16` directly), the per-side convention is undeclared, and the backtester uses a **flat $10/trade** model instead. See §5.6a |
| **V-3′** | `c = 0.0016` is a hard-coded constant with no stated derivation and no per-side convention | `label_builder.py:69-78` + `settings.yaml:247` |
| **V-4** | Objectives are exactly lambdarank / L2 / binary-logloss | `lightgbm_models.py:96-98` |
| **V-5** | The three models share no parameters | `model_bundle.py:168-177`; three `.train()` calls |
| **V-6** | The blend z-scores all three **before** weighting | `sleeve_selector.py:213-221` |
| **V-7** | Blend weights are unconstrained in sum (0.80–1.45 admissible) | grid at `sleeve_selector.py:255-257` |
| **V-8** | Cross-sectional z-scoring removes date-level location and scale, and therefore erases the invariance difference in Claim 2 | re-derivation |
| **V-9** | `label_gain`, `lambdarank_truncation_level`, `sigmoid`, `eval_at` are unset in the repo | `grep -rn "label_gain\|truncation_level\|sigmoid" pipeline/` returns nothing |
| **V-10** | Truncation at 30 with ~130 names ignores the bottom ~100 in the objective | LightGBM docs + universe size |
| **V-11** | The turnover penalty is ~0.1 % of one σ of `opportunity` | `10/10000 = 0.001` vs `sd(opportunity) ≈ 1` |
| **V-12** | `predict` returns probability, not raw score, for `objective="binary"` | verified, LightGBM 4.6.0 |
| **V-13** | A `QuantileBundle` (P10/P50/P90) **already exists and is unused in production** | `model_bundle.py:201-277`; `bundle_factory.PARADIGMS` |
| **V-14** | ★ `QuantileBundle` sets `rank_score = P50` — so promoting it **also replaces the lambdarank ranker**, not only the regressor and classifier | `model_bundle.py` `predict_scores`: `"rank_score": p_mid` |
| **V-15** | The backtester's cost of record is a **flat $10/trade**, and `charge_transaction_cost` defaults to **`false`** | `backtester.py:14-18`, `settings.yaml:55` |
| **V-16** | `c / σ_horizon < 0.04` at every horizon ⇒ `y^cls` is a sign test | `σ = 0.30·√(h/252)`; re-derivation |
| **V-17** | Cross-sectional z-scoring cannot remove a **per-name** rescaling, so QA-34 changes Claim 3's status | re-derivation, §9.1.5 |
| **V-18** | Fitting on raw `R` under heteroskedastic noise attenuates high-volatility names more, so the **incumbent regressor already carries a low-vol tilt from the fit** — making QA-58 tilt-*correcting* | theoretical (§5.7); **measure `κ` by volatility decile to confirm** |
| **V-19** | The code's turnover penalty is off by **`1/β ≈ 385×`** (unit conversion) **× 3.2×** (10 bps vs 32 bps round trip) = **1232×** — and `1/ρ²` is a *different* factor, between the two candidate fixes | §9.1.6a; re-derivation |
| **V-20** | ★ **A trim is charged `$0`** — `_reconcile_bucket` tests set membership only, and its docstring says "Held positions incur no fee" | `backtester.py:320-330` |
| **V-21** | **`charge_fees = True` is exercised nowhere in the test suite** — the only test reference sets it `False` | `grep -rn charge_transaction_cost tests/` |
| **V-22** | A flat fee's percentage drag spans **10×** across a $100 k–$1 M book, so `initial_capital` is load-bearing the moment costs are charged | `N·(252/h)·$20/B` |
| **V-23** | ★ **`buckets == horizon_days`**, so total rolls/yr = 252 at every horizon and the **commission drag is horizon-invariant** | `backtester.py:110-111` |
| **V-24** | ★ `initial_capital = 20000.0` is **hard-coded**; at that capital `$20` is **50 bps** (1w) / **210 bps** (1m) — the config comment was false | `backtester.py:107` |
| **V-26** | ★ `SleeveSelector._resolve_incumbency` **can already decline to roll** — the architecture is an incumbency-challenge system, not a pure calendar ladder | `sleeve_selector.py` `_resolve_incumbency` |
| **V-27** | ★ `incumbency_margin_delta` defaults to **0.0** and is the **same quantity** as §9.1.6a's `penalty_z ≈ 1.23` | `sleeve_selector.py:121` |
| **V-28** | `E[max of 130 std normals] = 2.60`, not 2.8 — **Blom's approximation `Φ⁻¹((n−0.375)/(n+0.25)) = 2.590` corroborates**; 2.8 ⇒ n ≈ 241. At n = 330 it is **2.91**, so universe expansion *lowers* the minimum viable position | 200 k simulations + Blom |
| **V-29** | ★ `δ_floor` from **commission alone** is **1.92** at $20 k / N=5 and **8.08** at N=21 — the latter exceeds `E[max−min] = 5.20σ`, so the 21-bucket ladder **can never trade** | §5.8.7 |
| **V-30** | The **BMO InvestorLine** export carries `Transaction **Date**`, not a timestamp — so execution cost is **not retrospectively recoverable** | `pipeline/portfolio/ingest.py:188` |
| **V-25** | The `charge_fees=True` path works and costs exactly `$20` per round trip | `tests/test_flat_trade_fee.py::test_known_answer_one_round_trip_costs_exactly_twenty_dollars` (891 green) |

> **V-13 changes §9.4.** Five bundle paradigms are already implemented — `separate` (production),
> `quantile`, `multihead`, `stacked`, `sequence`. **§9.3 Option 3 is not a build, it is a
> promotion**: `QuantileBundle` fits LightGBM `objective="quantile"` at α = 0.1/0.5/0.9 and derives
> `prob_up = 1 − Φ((c − P50) / σ̂)` with `σ̂ = (P90 − P10)/(z_{0.9} − z_{0.1})`, divisor
> **2.5631** — arithmetically correct. What it lacks is an evaluation under D-03's protocol and a
> coverage check on the normal approximation, **not an implementation**.

## 9.2 What the current design does not provide

| Missing | Consequence |
|---|---|
| **Uncertainty** | The classifier's probability is the only thing resembling it, and the blend collapses it into a point score. The system cannot say "this ranking is weak today" |
| **Horizon** | §5 |
| **Regime conditioning** | One model for all market states; drift is detected (D-04) but not conditioned on |
| **Calibration** | Nothing checks whether `p=0.7` means 70% |
| **A stop and a target** | ★ These are currently authored by the **LLM** (D-01), which `L1-fundamental-analysis.md` §7 argues is the least reliable output class in the system |

## 9.3 Options

### Option 1 — Keep three heads, but describe them honestly

Reframe as a **loss ensemble over one target**, document it as such (§8), and stop treating the
three as independent evidence.

*Cheap, honest, no code change. It changes what we believe rather than what we run — which is
sometimes the correct outcome of a review.*

### Option 2 — One ranker + a calibrated uncertainty head ★

INV-6 takes **exactly one actionable name per day**. That is a *selection* problem. The regressor's
magnitude is never used except inside the blend, so two of three heads exist to feed a weighted sum
whose output is then ranked anyway.

Replace with: **a ranking model** (LambdaMART-style, which the GBDT stack already supports) **plus a
calibrated confidence** that the ordering is real — conformal prediction or a quantile head. Then
`rank_score` acquires an error bar, and the slate can say *"top-1, but the top-5 are
indistinguishable today."*

### Option 3 — Quantile regression, and let the model produce the band ★★

> **It is already implemented.** `QuantileBundle` (`model_bundle.py:201-277`) fits LightGBM
> `objective="quantile"` at α = 0.1 / 0.5 / 0.9 and is registered in `bundle_factory.PARADIGMS`.
> **This is a promotion, not a build** (V-13, QQ-17).

Predict `q10 / q50 / q90` of forward return instead of a point.

This is the option I would push hardest, for a reason outside the ML: **the Discipline Card's stop
and target are currently LLM-authored.** `L1-fundamental-analysis.md` §7.1 establishes that LLM
judgement is stochastic and requires a k-run probe just to know how stable it is; DC-3 exists
because a failed narrative once rendered a card with **no stop and no target** and it was emailed as
genuine (F0 D-15).

A quantile model supplies a stop and a target **deterministically, from the same data the ranking
came from, with a stated coverage level**. The LLM then *narrates* a band it did not invent — which
is exactly the division of labour L0 §5.3 asks for: *"LLMs interpret and synthesize; code
computes."*

| | |
|---|---|
| **Pro** | Uncertainty, magnitude and the card's two most decision-relevant numbers, from one model. Pinball loss is standard and well-referenced. GBDTs support it natively |
| **Con** | Quantile crossing needs handling. Coverage must be validated, not assumed. Does not by itself solve horizon (composes with §5 Option C) |

### Option 4 — Multi-task NN with `{horizon × quantile}` heads

The full generalisation: §5 Option B crossed with Option 3.

*Highest ceiling, most machinery, and it stakes the design on a neural branch that has not yet
beaten the GBDTs at a single horizon. Not now.*

### Option 5 — Two-stage: cross-sectional selection + per-name path model

Selection ranks the universe; a separate per-name model handles entry, trim and exit.

*Matches §5 Option E and the mandate. It is the most faithful to what the fund actually does — and
it is the largest change, because it makes the timing layer a first-class model rather than the
heuristics currently in `buffett/signals/`.*
## 9.4 Recommendation — **re-sorted v0.7.0**

> **v0.6.0's sort was written before the horizon decision and contradicted it.** It filed Option 5
> under *Research → D-10* while §5.6's QQ-2 approved **E / Option 5 as the production
> decomposition**, with the timing leg promoted from heuristic to load-bearing model leg
> (consequence #3). The same architecture cannot be production in §5.6 and research in §9.4.
> *(Caught by external review, 2026-08-17.)*

### The frame, not a candidate

**Option 5 (selection + timing) is the decided architecture.** It is §5.4's Option E seen from the
model axis rather than the horizon axis, and every remaining option sits *inside* it — one in the
selection leg, one in the timing leg. It is removed from the candidate list.

### Inside the selection leg

| Do | Why |
|---|---|
| **Adopt Option 1 now** — reframe the bundle as a *loss ensemble over one target* and document it (§9.1) | Costs nothing. Stops "three independent models" justifying further complexity |
| **Promote `QuantileBundle` — but as a hybrid** | See the correction below |
| **Retire the regressor and the classifier on that promotion** | They are superseded, not merely redundant |

**The regressor and classifier are retired by the same promotion**, and the reasoning is concrete
rather than staged:

| Head | Verdict | Why |
|---|---|---|
| **Ranker** | **Keep, retrain at 21 d** | INV-6 is a *selection* problem and lambdarank optimises the ordering **directly**. The four undeclared parameters (§9.1.6) become MethodEntries in the retrain |
| **Regressor** | **Superseded** | Its output is used only inside a blend that is re-ranked. `QuantileBundle`'s P50 replaces it with a strictly better loss: **pinball at α = 0.5 is proportional to MAE**, robust to exactly the tail domination §9.1.2(b) flags for L2 |
| **Classifier** | **Superseded** | Its threshold has no stated derivation and is < 0.04 σ regardless (§9.1.1). And `prob_up = 1 − Φ((c − P50)/σ̂)` is **already derived inside `QuantileBundle`** (V-13) — the same promotion supplies the output |

> **The external review reached this in one step rather than two, and it is right that Option 2**
> ("one ranker + calibrated uncertainty") **is not a later stage — it is what Option 3 leaves
> behind.** v0.6.0's staged "Option 3, then Option 2" had all the pieces and never joined them.

#### But a straight promotion also deletes the ranker — V-14

`QuantileBundle.predict_scores` sets **`"rank_score": p_mid`**. So promoting it *as implemented*
replaces lambdarank with **"rank by predicted median return"** — a **pointwise-accuracy** objective
standing in for an **ordering** objective, and a strictly weaker approach to the one problem INV-6
actually poses.

**So this is a small build, not a pure promotion**: a bundle that keeps the lambdarank ranker for
`rank_score` and takes the quantile heads for the band (`P10/P50/P90` -> stop, target, `prob_up`).
Roughly the union of `SeparateModelsBundle.ranker` and `QuantileBundle`, both of which exist.

| ID | Rule |
|---|---|
| **QA-51** | A bundle producing `rank_score` from a **pointwise** objective (predicted level) rather than a **ranking** objective must justify it against the lambdarank incumbent on D-03's protocol. Ranking by predicted value is not equivalent to optimising the ranking (INV-6 takes the top-1) |

### Inside the timing leg

**F / triple-barrier** — see §9.6.

### Research and later

**D** (linear per-feature decay) stays in D-10 — it is what would promote 1q out of research.
**Option 4** (multi-task NN over `{horizon x quantile}`) stays at the end; per §5.4 Option B's
amended verdict, the nesting it would exploit is better handled by D.

## 9.5 The overlooked head — volatility is the one thing here that is actually predictable

Neither v0.1.0 nor the external review drew this out fully, and it may be the most consequential
observation in the section.

| Target | Out-of-sample `R²` | Against which baseline | Source |
|---|---|---|---|
| **Cross-sectional return** | ≈ 0.004 | zero / unconditional mean — **and there is no persistence to exploit** | Gu, Kelly & Xiu (2020); the 0.40 % figure is theirs. *(The `IC ≈ 0.063` conversion is a house derivation — hedged in §5.3b, not re-litigated here)* |
| **Realized volatility** | ≈ 0.4 – 0.7 | unconditional mean — **but RV is strongly autocorrelated** | Corsi (2009) and the HAR literature |

> ⚠ **The headline comparison overstates the case, and v0.6.0 stated it without qualification.**
> *(Correction from external review, 2026-08-17.)* The two `R²` are measured against **different
> baselines**. Realised volatility is highly persistent, so a naive "yesterday's RV" forecast
> already scores `R² ≈ 0.3–0.5` **on its own**. **Most of HAR's headline number is persistence,
> not skill.** Returns have no comparable persistence to bank, so their `R²` against the mean is a
> much harder-won number.
>
> **The conclusion survives; the "two orders of magnitude" framing does not.** Volatility is
> genuinely the more tractable target, and it feeds the stop, the size and QA-34's normalisation.
> But the *incremental* skill over a persistence baseline is far smaller than 0.4–0.7 suggests, and
> a gate set against the unconditional mean is **cleared by a model that has learned nothing**. The system currently spends
all of its ML effort on the harder target and none on the easier one — and the easier one feeds
decisions the fund actually makes:

- **the stop distance** on the Discipline Card should be a function of *forecast* volatility, not a
  fixed percentage and not realized volatility (which is backward-looking);
- **position size given a stop** is D-06's arithmetic, and its dominant input is that same forecast;
- **the label normalisation** QA-34 requires is itself a volatility estimate, so the machinery is
  needed regardless;
- **`k·σ̂·√h` barriers** (§5.4 Option F) depend on it.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE MOST RELIABLE ML OUTPUT AVAILABLE TO THIS SYSTEM IS A       ║
║  VOLATILITY FORECAST — AND IT IS NOT CURRENTLY BEING PRODUCED.   ║
║                                                                  ║
║  Return prediction is where the alpha is and where the           ║
║  measurement problem is brutal (§5.3b).                          ║
║  Volatility prediction is tractable, well-referenced, and        ║
║  feeds the stop, the size and the label normalisation.           ║
║                                                                  ║
║  These are not competing. But if only one head can be built      ║
║  well, the evidence says it is not the return head.              ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **QA-41** | *(revised v0.7.0)* A **volatility forecast is a first-class model output**, not an intermediate of label normalisation. It is evaluated on its own metric gate — **QLIKE, per horizon, against a stated benchmark** — and it is what D-05/D-06 size against |
| **QA-52** | ★ **The volatility gate's benchmark is a persistence or HAR-RV forecast, never the unconditional mean.** RV is strongly autocorrelated; a mean-baseline `R²` is cleared by a model that has learned nothing. **QLIKE** is the loss because it is robust to noise in the RV proxy (Patton 2011). *Reference:* Corsi (2009) for HAR-RV; Hansen & Lunde (2005) for "does anything beat GARCH(1,1)?"; Patton, A. (2011), "Volatility forecast comparison using imperfect volatility proxies," *Journal of Econometrics* 160(1), 246–256 |
| **QA-42** | A stop distance derived from a volatility forecast is **deterministic** and therefore falls under QA-27 — the LLM narrates it and may not alter it |


---

## 9.6 The timing leg — the half §9 never covered

> **Added v0.7.0.** §5.6's QQ-2 promoted the timing leg from heuristic to load-bearing model leg
> and assigned it F / triple-barrier — but §9's five options are **all selection-side**, so the leg
> that ground (a) makes decisive had no model, no gate and no rules. *(Gap identified by external
> review, 2026-08-17.)*

### What it decides, and why it is not a small ranker

The timing leg answers two questions the selection leg cannot:

- **enter now, or wait?** — given a name the selection leg has nominated
- **exit now, or hold?** — given a name already held

Neither is cross-sectional. Both are per-name, path-dependent, and evaluated on a completely
different statistic from `rank_score`.

### Why triple-barrier fits here and not in selection

Its objections in §5.4 Option F were all consequences of the **endogenous label span**, and every
one of them is a *cross-sectional* objection:

| Objection in the selection leg | Status in the timing leg |
|---|---|
| QA-33's power calculation is undefined — no single `h` | **Dissolves.** A timing model faces no cross-sectional power test; it is judged on hit rate conditional on entry |
| Non-additive, so incompatible with Option D's summation | **Irrelevant.** The timing leg does not compose horizons |
| Variable span complicates uniqueness weighting | **Still applies** — QA-37's span-average form is required, which is why it was corrected in v0.3.0 |

And the fit is structural: **the barriers *are* the decision object.** Profit-take, stop-loss and
time-limit is exactly the Discipline Card's target / stop / horizon triple.

### Rules

| ID | Rule |
|---|---|
| **QA-53** | The timing leg is evaluated on **hit rate conditional on entry** and **realised MFE/MAE**, per horizon — **never on cross-sectional IC**, which does not apply to a per-name path decision |
| **QA-54** | ★ **A minimum holding period is a constraint on the timing leg, not an outcome of it.** M-4 is the decisive ground for HorizonSet v1 (§5.6); a timing model free to exit on day 2 would reintroduce the short-hold pattern the horizon decision exists to remove |
| **QA-55** | ★ **The timing leg must be able to say "hold", and holding must be its default.** M-3 states the behaviour to curb is pyramiding and the fix is to *sell less and let winners run* — so a leg trained only to optimise exits satisfies the letter of the mandate and inverts its intent. **An exit-only timing model is a mandate defect, not merely an incomplete one** |
| **QA-56** | Barriers are set at `k · σ̂_i · √h` (QA-34's estimator), so label difficulty is constant across names and horizons — **not at fixed basis points**, which §9.1.1 shows degenerates to a sign test |
| **QA-57** | The timing leg is a **gate** and therefore bound by P3 and QA-47: it may delay or veto, never nominate, and never make an outcome more aggressive (D-04 MT-31, MT-32) |

> **QA-54 and QA-55 pull in opposite directions and both are mandate-derived**, which is the point.
> QA-54 stops the timing leg reintroducing short holds; QA-55 stops it becoming an exit-only
> machine. The timing leg's objective has to be written so that *holding* is a first-class action
> with its own reward, not the residual left when no exit fires. **Recorded as QQ-19** — the exit
> criterion and the hold criterion are not the same model and may not share one threshold.


---

# 10. CONTRACTS

> **ID-collision notice.** `AC-3.k` / `CT-3.k` key `n` on **D-03**.
> **`sdd/specs/F3_sdd_adoption/spec.md` issues `AC-3.1`…`AC-3.7` and `CT-3.1`/`CT-3.2`.** Third live *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*
> collision (after D-01/F1 and D-02/F2) under the accepted convention (L0 §16.4). Always qualify.

## CT-3.1 — HorizonSet (versioned YAML)

**This is HorizonSet v1 as approved 2026-08-16 (§5.6)**, not an illustration.

```yaml
name: production
version: 1
approved_by: victor
approved_on: 2026-08-16               # §5.6 — QA-2 satisfied
horizons:
  - id: h1m                           # ★ PRODUCTION — the only nominating horizon
    trading_days: 21
    role: selection
    label: fwd_return
    standardise: per_horizon_vol      # QA-34; Yang-Zhang (QA-35); neutralised (QA-45)
  - id: h1w                           # timing only — never the ranker's target
    trading_days: 5
    role: timing
  - id: h1q                           # research only — never reaches a human artifact
    trading_days: 63
    role: research
purge_days: 63        # DERIVED from max(trading_days) — QA-18
embargo_days: 5
mandate_justification: |                          # QA-2 — see §5.6 (grounds) and §5.6a (cost)
  (a) M-4, DECISIVE: a 5-day objective systematically manufactures the CRA
      "carrying on a business" pattern; the downside is retroactive
      reclassification, not a drawdown. Independent of any cost figure.
  (c) L0 §12.1 "weeks-months": 5 trading days is not weeks; 21 is the short end.
  Accepted cost: 1w has better statistical power (MDE 0.0135 vs 0.0277 at t>3).
      A detectable edge that cannot be traded profitably is not an edge.
  (b) COST: **INDETERMINATE, pending QQ-20** — see §5.6a. The v0.7.0 figures
      (16.13%/3.84%, 12.3% differential) are RETRACTED: they were sourced to a
      dead code branch, the per-side convention is undeclared, and the
      backtester models commission only (flat $10/trade). Spread and slippage
      are unmodelled. Ground (b) flips sign at 3-12 bps of proportional cost.
      **This ground is NOT load-bearing for the decision** — (a) and (c) are.
ranked_quantity: denormalised_return              # QA-58 — 'Zhat * sigma_hat * sqrt(h)', NOT Zhat
                                                  #   QA-33: every IC/power figure is OF this quantity
cost_model_status: indeterminate                  # QA-48; resolves at QQ-20
flip_back_threshold_bps_round_trip: [3, 12]       # §5.6a — the bar QQ-20 measures against

arbitration:                          # QA-47 — never implicit
  nominates: h1m                      #   the ONLY horizon that may produce the daily pick (INV-6)
  may_delay_or_veto: [h1w]            #   timing leg: can defer or block, never nominate (P3)
  research_only: [h1q]                #   never reaches an artifact a human reads

loss_weighting:                       # QA-46 — a decision, not a side effect
  policy: explicit
  weights: {h1w: 0.2, h1m: 0.7, h1q: 0.1}
  note: "uniqueness weighting alone implies ~12.6:1 toward h1w — rejected"

power:                                # QA-33 / QA-43 — both axes recorded
  n: 130
  T: 1915
  effective_breadth: measured         # QA-43 — never assumed equal to n
  mde_t3: {h1w: 0.0135, h1m: 0.0277, h1q: 0.0479}
```

## CT-3.2 — BacktestSpec / BacktestResult (JSON)

Spec pins everything in §7.1. Result carries, **per horizon**: statistic, threshold, **effective N**,
corrected standard error, verdict ∈ `{PASS, FAIL, NOT_EVALUATED}`, and the `formula_id` of every
metric used.

## CT-3.4 — ★ Nomination (JSON) — D-03's production output

> ⚠ **Added 2026-08-18 by cross-spec audit.** D-03's three contracts covered **configuration**
> (CT-3.1), **evaluation** (CT-3.2) and **provenance** (CT-3.3). ★ **The thing D-03 actually
> produces every day had no contract at all** — `L1-decision.md` CT-12.1 consumes
> `candidate: {ticker, rank, ranked_quantity, horizon}` and nothing declared it.

```json
{
  "as_of": "2026-08-18", "run_id": "…", "decision_anchor": "open",
  "horizon_set": {"name": "production", "version": 1},
  "nominating_horizon": "h1m",
  "universe_n": 130,
  "model_artifact_id": "sha256:…",
  "candidates": [
    {"ticker": "MU", "rank": 1, "ranked_quantity": 0.0412, "z": 2.61}
  ],
  "arbitration": {"nominated_by": "h1m",
                  "delayed_by": [], "vetoed_by": [],
                  "research_only": ["h1q"]}
}
  "excluded": [{"ticker": "AVB", "reason": "delisted 2026-08-17 (QA-125)"}],
```

| ID | Rule |
|---|---|
| **QA-119** | ★ **`ranked_quantity` is the DENORMALISED return `ẑ·σ̂·√h`** (QA-58), and `z` travels beside it. **Publishing only `z` would let a consumer rank on the normalised quantity**, which is the low-vol tilt QA-58 exists to remove |
| **QA-120** | ★ **`nominating_horizon` is always `h1m`** (CT-3.1's arbitration block, QA-47). `h1w` may appear in `delayed_by`/`vetoed_by` and **never** in `nominated_by`; `h1q` is `research_only` and **may not appear in a Nomination consumed by D-12 at all** |
| **QA-121** | ★ **`universe_n` and `model_artifact_id` are required.** `n` sets `E[max z]`, which every downstream power and cost figure depends on (`L2-signal-combination.md` §7A.2), and **a nomination that cannot be traced to the model that made it cannot be re-run** (INV-2). ⚠ **Clarified 2026-08-23: `model_artifact_id` identifies WHATEVER PRODUCED THE RANKING — a fitted D-04 artifact or a declared deterministic rule — and is a content hash either way.** ★ Before D-04 exists (L3 B3) the ranker is a declared rule with a `formula_id` and a MethodEntry; **null is not permitted**, because the rule QA-121 states is re-runnability, and a hashed rule satisfies it exactly as a hashed model does |
| **QA-122** | ★ **`candidates` is a LIST of length `k_cov` or more**, ordered by rank — not a single winner. D-01 covers the top `k_cov` (**RA-55**), so the nomination must expose them; **a contract that emits only rank 1 makes `k_cov ≥ 2` unimplementable** (`L2` CB-19) |

## CT-3.3 — MethodEntry (markdown, one per `formula_id`)

The six required fields of §8.2. A `formula_id` referenced anywhere in `src/` with no MethodEntry
fails the build.

---

# 11. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `get_horizon_set(name, version)` | `HorizonSet` | version required in production |
| `run_screen(screen_id, panel, as_of)` | `ScreenResult` | pure |
| `compute_signal(signal_id, panel, as_of)` | `SignalPanel` | stateless; never `rank_score` |
| `backtest(spec)` | `BacktestResult` | spec fully pinned (QA-11) |
| `evaluate_gates(result, gate_set)` | `GateReport` | per horizon; `NOT_EVALUATED` is a valid outcome |
| `method(formula_id)` | `MethodEntry` | the provenance record (§8) |

---

# 12. BUSINESS RULES

| ID | Rule |
|---|---|
| **QA-1…QA-5** | The horizon set — §5 |
| **QA-7…QA-10** | Screens & signals — §6 |
| **QA-11…QA-19** | Evaluation protocol — §7 |
| **QA-20…QA-25** | Mathematical provenance — §8 |
| **QA-26…QA-28** | Model architecture — §9 |
| **QA-26** | ⚠ *(defined in the 2026-08-18 audit — it was referenced by §12's roll-up and by D-04 §5.4 and had never been written.)* **The head set is a declared property of the bundle**, versioned with it: which heads exist, what each optimises, and how their outputs combine (§9.1). Adding or removing a head is a **bundle version change**, not a config tweak |
| **QA-27** | ★ ⚠ *(defined in the audit — **cited by D-04 MT-38, D-06, D-09 and §9.3, and never written**.)* **A stop or target produced by a deterministic model is authored by D-03 and is IMMUTABLE downstream.** D-01 may **narrate** it and may not alter it; D-09 may **render** it and may not recompute it (DC-1, DC-5, P2/AP-5). ★ **The quantile heads (§9.3) are the intended source** — a stop is a distributional statement, and an LLM asked to produce one is doing risk arithmetic under a contract that says it is computed |
| **QA-28** | D-03 is **stateless**: no module holds fitted parameters, and none imports D-04 (§3) |
| **QA-29** | D-03 never emits a verdict. It ranks and it measures; gating is P3's business and belongs downstream |
| **QA-30** | Every D-03 output records the D-02 contract version, `as_of`, `adj_as_of` and the calendar-check id it was computed under |

---

# 13. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `QNT.HORIZON.UNPINNED` | ERROR | a model or backtest without a declared HorizonSet version (QA-1) |
| `QNT.CV.PURGE_TOO_SHORT` | ERROR | purge shorter than the longest horizon (QA-3, QA-18) |
| `QNT.CV.FOLD_STRADDLE` | ERROR | replicated rows split across folds (QA-19) |
| `QNT.METRIC.NAIVE_SE` | ERROR | a gate evaluated on an uncorrected standard error (QA-4) |
| `QNT.GATE.NOT_EVALUATED` | WARNING | statistic uncomputable — **never a pass** (QA-17) |
| `QNT.GATE.VACUOUS` | ERROR | a gate that cannot fail — every candidate errored yet the gate passed (QA-17, D-18) |
| `QNT.BACKTEST.UNPINNED` | ERROR | spec incomplete (QA-11) |
| `QNT.BACKTEST.GROSS_ONLY` | ERROR | results without costs (QA-12, INV-016) |
| `QNT.SURVIVORSHIP.UNADDRESSED` | WARNING | backtest over listed-only names, reported as biased (QA-14) |
| `QNT.METHOD.MISSING` | ERROR | a `formula_id` with no MethodEntry (QA-20) |
| `QNT.METHOD.STALE` | ERROR | code changed without its MethodEntry in the same commit (QA-25) |
| `QNT.SIGNAL.ADJUSTED_LEVEL` | ERROR | a price-level comparison computed on the adjusted panel (QA-10) |

---

# 14. ACCEPTANCE CRITERIA

```text
HORIZONS  (§5)
□ AC-3.1   Every model/backtest declares its HorizonSet name and version
□ AC-3.2   Purge length is derived from max horizon; a shorter one raises
□ AC-3.3   Replicated rows (Option C) never straddle a CV fold
□ AC-3.4   Labels for a horizon use only prices within that horizon (INV-1)
□ AC-3.5   A multi-horizon design is compared to the per-horizon single-task
           baseline before adoption (QA-6)
□ AC-3.6   The HorizonSet records its mandate justification (QA-2)

EVALUATION  (§7)
□ AC-3.7   Every reported statistic carries effective N and a corrected SE
□ AC-3.8   Gates are per horizon; a pooled cross-horizon gate raises
□ AC-3.9   An uncomputable statistic reports NOT_EVALUATED, never PASS
□ AC-3.10  A gate where every candidate failed cannot report PASS (the D-18 regression)
□ AC-3.11  An unpinned backtest spec raises — including a missing initial_capital
□ AC-3.11a A backtest result states costs_charged in {none, commission_only, full}
□ AC-3.11b With charge_transaction_cost=true, a single-position single-round-trip
           backtest moves by exactly $20 (the known-answer test QA-62 requires)
□ AC-3.11c A weight change on a HELD position is charged as a trade (QA-61)
□ AC-3.12  Backtest results carry costs and are labelled not-expected-returns
□ AC-3.13  Survivorship treatment is stated; listed-only is flagged biased

METHOD PROVENANCE  (§8)
□ AC-3.14  Every formula_id in src/ resolves to a MethodEntry, or the build fails
□ AC-3.15  Every MethodEntry has statement, symbols, reference, assumptions,
           alternatives-rejected, and a known-answer test
□ AC-3.16  Every MethodEntry's known-answer test executes and passes
□ AC-3.17  A method with no external reference is flagged HOUSE VARIANT (QA-22)
□ AC-3.18  Assumptions name the ones this system violates and point at the
           correction (QA-23)
□ AC-3.19  Changing a formula without amending its MethodEntry in the same
           commit fails CI (QA-25)

BOUNDARY & CORRECTNESS
□ AC-3.20  No module in src/quant holds fitted parameters (QA-28)
□ AC-3.21  src/quant does not import src/models (D-04) or src/fundamental (D-01)
□ AC-3.22  A price-level screen reads the RAW panel, not the adjusted one (QA-10)
□ AC-3.23  Every output records contract version, as_of, adj_as_of, calendar id
□ AC-3.24  A stop or target produced deterministically is not altered downstream (QA-27)
□ AC-3.31 ★★ the raw measure recovers a known correlation; the residual
           one returns -1/(n-1) at every true rho; an unmeasurable
           breadth is None, never n (QA-43, QA-124, QQ-14)
□ AC-3.32 ★★ an untradeable name never reaches candidates and appears in
           excluded[] with its reason; a name with a stale last bar is
           excluded even when it still prices (QA-125, QA-126)
```

---

# 15. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| ~~QQ-1~~ | ~~Is 1w the right production horizon at all?~~ | ✅ **CLOSED 2026-08-16 by Victor.** **HorizonSet v1 = `{ production 1m · timing-only 1w · research 1q }`.** Full reasoning, what was given up, and eight consequences: **§5.6**. Reopens only if measured `IC(1w)−IC(1m)` exceeds the cost differential **and** M-4 is relaxed |
| **QQ-2** | Which options go to production? | 🟡 **HALF-CLOSED 2026-08-16.** The **decomposition axis is settled by implication** of QQ-1: HorizonSet v1 *is* §5.4 Option E restated as an architecture (selection at the longer horizon, timing at the shorter). **The estimation axis remains open and is D-04's**: recommended **A** baseline → **C + pinball judged at 1m** for selection, **F / triple-barrier** for timing, **D** as research |
| ~~QQ-14~~ | ~~What is the real round-trip cost?~~ | **SUPERSEDED 2026-08-17 by QQ-20.** Its premise ("32 bps from config") was itself wrong — see §5.6a |
| ~~QQ-16~~ | ~~The turnover penalty is dimensionally inconsistent~~ | ✅ **DIAGNOSIS CLOSED 2026-08-17 — see §9.1.6a. Both earlier recipes were wrong, including mine.** The correct penalty is `rt / β` where `β` is the slope of **realised return regressed ON opportunity** — not opportunity on return. **Numeric closure still blocked on QQ-20**, since `penalty_z` spans 0.15–1.23 across the plausible `rt` range |
| **QQ-22** | ⚠ **Has arrival-quote capture started?** (QA-69) | The single time-critical item in this spec. `(ticker, submit_ts, bid, ask, last, size, order_type)` at submission. Capturing it takes **~36 trades ≈ 3 months** to measure QQ-20; using a daily-bar proxy instead takes **~1,600 trades ≈ 13 years**. `n ∝ σ²`, so the arrival quote is worth a **≈44× sample reduction** |
| **QQ-23** | Is the `τ ≈ 16` agreement between §5.8.5b and §5.3b corroboration or a shared assumption? | Both routes use the same decay law `IC(h) ∝ (1−e^(−h/τ))/√h`, so they are **not independent** and the agreement is weaker evidence than it looks. Build step 4's measured `τ` settles it |
| ~~**QQ-24**~~ | ✅ **CLOSED 2026-08-18 — §5.8.6b.** Capital base **read from D-11** (QA-107); **δ re-based on the mandate** (QA-110), which makes it book-independent. Residual: δ is provisional on `τ` | QQ-21's resolution is conditional on a **$20k backtest literal**; at any realistic book commission-derived δ collapses and the hold falls to ~2 days (**M-4 violation**). Needs QA-63 first, then QA-102's re-basing of δ on the mandate rather than the fee |
| **QQ-21** | ⚠ **What is the rebalance architecture at 1m?** | 🟡 **MOSTLY RESOLVED 2026-08-17 — see §5.8.** It is **Little's Law** (`N = λ·h`), not a free parameter, and it is **the same question as QQ-15**. Recommendation: keep `N = 5`, set `incumbency_margin_delta` from §9.1.6a (it is currently **0.0**, and it is the *same number* as `penalty_z`), and satisfy the identity by lowering **λ** rather than raising **N** — holding period then emerges at ~20 d. **Two things still open**: the capital base (QA-63) and the INV-6 re-reading, which is **Victor's** |
| ~~QQ-20~~ | ~~What is the real proportional cost — spread and slippage?~~ | ✅ **CLOSED 2026-08-18 — WILL NOT MEASURE** (Victor, via `L1-recording.md` §7). Arrival capture will not be built, so `(fill − arrival)` has no source. **Consequences: ground (b) is permanently indeterminate and the horizon decision rests on ground (a) — M-4 — alone**; `δ` is set from its commission floor permanently. Defensible at this scale: **22 bps at a median $8,941 order, 6.9 bps at the $29,018 max**. *(Superseded text below.)* ⚠ *What is the real proportional cost?* | ⚠ **REFRAMED 2026-08-17 — it is a DATA-CAPTURE problem, not a spec problem.** Slippage is a **paired** measurement, `(fill − arrival)/arrival`, and **a broker export supplies only the fill**. Worse: the BMO InvestorLine export carries `Transaction **Date**`, not a timestamp, so a fill cannot even be paired to a same-minute quote retrospectively. **D-11 as scoped cannot measure this**; it can only measure commission, which V-23 shows is horizon-invariant. **The arrival quote must be captured at order submission, and every trading day without it is permanently unrecoverable.** See QA-69 |
| **QQ-19** | ⚠ The timing leg's hold criterion and exit criterion are not the same model (§9.6) | QA-54 forbids short holds (M-4); QA-55 requires *holding* to be a first-class action (M-3). Both mandate-derived, pulling opposite ways. One threshold cannot serve both |
| **QQ-17** | Given `QuantileBundle` already exists (V-13), what blocks promoting it? | Not implementation — it needs an evaluation under D-03's protocol at 1m, plus a **coverage check on the normal approximation** behind `prob_up`. Empirical return distributions are fat-tailed, so `σ̂ = (P90−P10)/2.5631` will understate tail probability |
| **QQ-15** | ⚠ **Does INV-6's daily cadence still fit a 21-day objective?** ★ **Same question as QQ-21 — see §5.8.1.** Answer: **not as a daily *transaction* cadence** below ~$180 k of capital. It survives re-read as *nominate daily, trade on a decisive challenge*. **Constitution-level ⇒ Victor's** | "Exactly one actionable recommendation per day" was written when the objective was 5 days. At 1m the top-1 changes slowly, so daily nomination either repeats a name for stretches — arguably correct under M-3 "hold winners" — or churns against its own horizon. **A constitution-level question; raised, not resolved** |
| **QQ-13** | Does the ~330-name expansion (QQ-11) alone promote 1q out of research? | It clears the **statistical** bar. It does **not** clear the **cost** bar (§5.6), which is what demotes short horizons. Two separate tests; both must pass |
| **QQ-9** | Is the **volatility head** the highest-value model in the system (§9.5)? | If `R²(vol) ≈ 0.4–0.7` against `R²(returns) ≈ 0.004`, then yes on information content — and it feeds the stop distance and position size, which are decisions the fund actually makes. Needs measuring on our panel before it is believed |
| **QQ-10** | Does the target become a forward *Sharpe* rather than a forward *return* (QA-36)? | Volatility normalisation changes the economic object. Better for sizing; requires every gate and backtest statement to be restated. Not yet decided |
| **QQ-3** | Does the panel support a 1q horizon? | ⚠ **REOPENED 2026-08-16 (v0.3.0).** v0.2.0 closed it on a power table that held IC flat across horizons — which §5.3a forbids. The real answer: **testable iff the aggregate signal half-life exceeds ~3 weeks** (§5.3b), *or* the universe widens to ~330 names on existing history. **Closes at build step 5, on a measurement.** 🟢 **De-risked 2026-08-16** — with 1m in production (§5.6) 1q is a *promotion candidate*, no longer a dependency |
| **QQ-11** | How far should the universe widen, and toward which sectors? | ~330 names reaches t=3 at 1q on existing history — but by **added breadth, not count** (QA-44). `config/universe_balanced.yaml` has 123; D-07 can source 26k+. Needs QA-43's residual-correlation measurement to choose |
| **QQ-14** | ⚠⚠ **Which correlation should `breadth_gate` consume — raw or residual?** QA-43 says residual; **QA-124 measures that the residual figure is `−1/(n−1)` by construction and carries no information**. The gate is currently fed the **raw** correlation because that is what G&K's `BR` means, and the residual is reported beside it. ★ Resolving this decides whether **QA-43 is amended or the gate is**, and it is the last gate refusing promotion |
| **QQ-12** | What is the per-horizon loss weighting under stacking (QA-46)? | Uniqueness weighting alone implies ~12.6:1 toward 1w. Defensible, but it should be chosen |
| **QQ-4** | Which §9 option? | Recommendation: adopt 1 now, build 3 next |
| **QQ-5** | If quantile heads produce the stop/target (§9.3 Option 3), what happens to D-01's authored ones? | QA-27 says narrate-not-alter. But F1's card contract and `L1-fundamental-analysis.md` both currently assume the LLM authors them — a real cross-spec change |
| ~~**QQ-6**~~ | ~~Where does `combined_score` / `SignalEngine` land?~~ | ✅ **CLOSED — new domain `D-12 Decision`** (`L1-decision.md`, L0 v0.17.0). `combined_score` is **quant-internal** and stays in D-03 (it blends D-02's composite, never D-01's thesis — `L2` CB-14); the **gate** is D-12's |
| **QQ-7** | **Should §8 be lifted into `L4-coding-standards.md`?** | It binds D-02, D-03, D-04, D-05, D-06. It is written here because D-03 needed it first; L4 §§2–13 is its proper home |
| **QQ-8** | Do the 9 model families in `ohlcv/models/` all survive? | lightgbm · xgboost · catboost · linear · sklearn · ft_transformer · tabm · sequence. §9 may retire several, and each retained one needs a MethodEntry |

---

# 15A. ★ NOTE FOR THE REVIEWING AGENT — v2.0.0

**You were right to insist on the magnitude test, and it falsified the mechanism you proposed. You
were also right about QA-80, and that pushback survives its own premise failing.**

## 1. The magnitude test refutes Roll — 4.47× too steep

Regression through the origin of cell effect on `s_CS²/σ_o`:

```text
     fitted slope = −3.922        Roll predicts −0.878, ONE-SIDED (|slope| ≤ 0.878)
```

Implied spreads **38.7–42.5 bps** against Corwin–Schultz **5.1–20.9**. **Bounce accounts for about
one fifth of the effect.** And your `s²/σ_o` re-normalisation, though correct in principle —
`s²/σ ≠ f(s/σ)` — **does not close the quintile-3 break** (−9.41 against quintile 2's −11.49).

★ **The lesson is mine, recorded as QA-99: a correlation is not a mechanism.** `corr = +0.895` read
as confirmation, and I declared Roll confirmed on a *ranking* while skipping the one test that could
refute it. An ordinal fit cannot falsify a quantitative theory, and a theory admitted on ordinal
evidence gets believed at the strength of the correlation rather than the strength of the test.

**Your staleness point is what saves the conclusion** (QA-97/98). Non-synchronous trading gives the
same sign and gradient and is **not bounded by the spread**, so it can carry the residual where Roll
cannot. And you are right that the distinction needs no resolution: at **−17.5 bps against ~20 bps
of round-trip spread the effect is unharvestable whichever mechanism carries it**. **QA-87's closure
is therefore robust to this entire section being wrong**, which is the property it needed.

## 2. QA-80 — you are right, and I have reversed the re-promotion

Your arithmetic reproduces: at `s = 24 bps`, added label variance `2 × 144 = 288 bps²` against
`866² = 749,956`, giving **0.019 %** sd inflation, against the **0.24 %** deviation v1.6.0 downgraded
on.

★ **And it holds at the implied spread too** — at 42 bps it is **0.059 %**, still 4× below the
threshold. **So your pushback survives the failure of the mechanism it was built on**, which is the
strongest form it could have taken.

**QA-79/80 are re-downgraded to regime guards** and **QA-100** records why this happened:

> *A finding is filed at the strength of its measured consequence, not its intellectual interest.
> Re-promoting a rule on evidence that does not reach it is the exact mirror of QA-83a's
> over-retraction — and it is the more tempting direction, because the finding feels important.*

That is the fourth instance of the recurring pattern, and the first that is **not** a units error.
The three earlier ones reached for the largest available number; this one reached for the largest
available *consequence*. Same reflex, different currency.

## 3. And your last row was the best disposition in the thread

*"The Roll finding is intellectually the cleanest thing in this section and its operational
consequence is approximately zero."*

Correct, and now quantified: **QA-101** replaces §5.9.2's *"measured IC may fall slightly"* with
**~0.02 % (≤ 0.06 %) — not detectable**. The section explains a diagnostic anomaly and changes no
label, no rule and no decision. Saying that plainly is the point, because a finding this tidy invites
being given more weight than it earns — which is precisely what I gave it one version ago.

## Where §5.9 stands

Nothing in it now rests on a magnitude comparison, a mechanism, or a correlation. **QA-77** stands on
correctness plus **QA-72** anchor parity; **QA-87** closes on unharvestability; **QA-79/80** stay
downgraded. The remaining work is build-time only: **QA-84/91**, **QA-86**, **QA-89**.

The one honest residual: **the effect is 4.5× larger than bounce and I have no measured account of
the remainder.** Staleness is plausible and untestable on daily data. It does not block anything —
QA-98 makes the conclusion mechanism-independent — but it is an open empirical question, not a
closed one, and I would rather leave it labelled that way than reach for a third mechanism.

# 16. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-03, §1.6, §12.1, **M-3**, **M-4**, INV-010/015/016/017 | domain definition, the mandate §5.2 measures the horizon against |
| `L1-feature-engineering.md` §5 (feature contract), **FE-9**, **FE-11…FE-13** | features and labels; the raw-vs-adjusted rule QA-10 inherits; labels are D-02's, horizons are D-03's |
| `L1-data-engine.md` §5C.7, §6A, **DE-35** | price restatement behind QA-10; the calendar check QA-30 records; the "never a silent pass" rule QA-17 mirrors |
| `L1-fundamental-analysis.md` §7.1, §7.3 | why §9.3 Option 3 matters — the stop and target are currently the least reliable class of output in the system |
| `L4-coding-standards.md` §1.2, ST-2, ST-3 | path; D-10 research exemption for §5 Options D/F; **§8 belongs here eventually (QQ-7)** |
| `sdd/specs/constitution.md` §4 (metric-gate tier), P3, INV-1/2/3 | the test tier gates live in, verdict monotonicity, look-ahead/determinism/ranges |
| `sdd/specs/F0_code_map/spec.md` §12 **D-16**, **D-18** | the two incidents §8.1 and QA-17 are built on *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
