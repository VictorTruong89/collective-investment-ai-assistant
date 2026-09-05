# L1: Domain Specification — Portfolio Strategy (D-06)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-06 · **Seat:** SEAT-4
> **Path:** `src/portfolio/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1) — **REBUILD, no legacy equivalent**
> **Depends on:** [`L1-recording.md`](L1-recording.md) (D-11, the book) ·
> [`L1-feature-engineering.md`](L1-feature-engineering.md) (D-02) ·
> [`L1-model-training.md`](L1-model-training.md) (D-04, the volatility forecast) · D-05
> **Binding:** **M-2**, **M-3**, M-5 · **INV-022**, **INV-026**, INV-028 · **P2 / AP-5**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.4.0 | 2026-08-25 | Victor | ⚠⚠ **B5 readiness — two defects.** ★★ **PS-43 (closes QS-7)**: **PS-27 divides the risk budget by `n_reserve = target_positions − current_positions`** and **`target_positions` was declared nowhere** — a number that *divides the risk budget* cannot have an invented default, and PS-27's own *"never derived from free cash"* rules out the tempting inference. It is **required per-account configuration**, reported on the answer, and ⚠ **`n_reserve ≤ 0` yields `unavailable`, not a floor**. ★ **PS-44**: **AC-6.9k** requires every applied factor to resolve to a MethodEntry, and the register is **D-03's** — so it would put D-06's entries in D-03's tree or create a **SEAT-3 → SEAT-4 import edge** the graph cannot tell from consuming a nomination. The register's check is a **filesystem scan**, so entries live in each domain's own `methods/entries/`. AC-6.9l/6.9m added. |
| 0.6.0 | 2026-08-18 | Victor | ⚠ **QS-4 stale — its premise (*"D-05 is blocked on QQ-6"*) was false twice over**: QQ-6 is closed and D-05 is written. Exposure is D-05's (RK-1…RK-7); D-06 reads it. |
| 0.5.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: D-06 sized against "the book" without naming its contract.** **PS-41** names **CT-11.4 BookState** for `capital_base`/`nav_base`/`positions[]` and D-05's `P`/`D` factors for the risk terms — and states that a book in `break`, or with `nav_base: null`, **cannot size anything**, since every sizing output is a fraction of a number that is not currently known. |
| 0.4.0 | 2026-08-18 | Victor | ⚠ **Audit: D-12 forbids `D-12 → D-06`, which left D-06 with no stated source for the graded inputs sizing needs.** **New §6Z / PS-37…PS-40** — D-06 reads the **transported `grade`** from `CT-12.1` (DN-25), so it never reads D-01 or D-03 directly and INV-014's mediation holds; the grade is an input to a deterministic computation, not a blind multiplier; only `actionable: true` is sized; the scorecard is read, never summed (RA-53). Parent bumped to L0 v0.18.0. |
| 0.3.0 | 2026-08-18 | Victor | ★ **QS-1 ELEVATED to a high-priority joint D-05/D-06 feature** (Victor): *"a fixed percentage for risk budget is meaningless in reality"*. New **§5.1d** — why a constant is wrong *in kind* (blind to edge, correlation, drawdown state, estimation confidence and the opportunity set), and a **multiplicative framework** `r_ceiling × E × C × P × D` with every factor ∈ (0,1] **so INV-022 holds structurally rather than by a clamp**. Candidate methods sketched with references (fractional Kelly, vol targeting, marginal risk contribution, drawdown control, risk of ruin), each requiring a **MethodEntry** (QA-20) before it multiplies a real position. **PS-33…PS-36** — notably **PS-34** (an unmeasurable factor is 1.0 and *reported* `unmeasured`) and **PS-35** (the framework must be able to say it cannot differentiate; manufacturing edge from noise is worse than a flat budget). §0 amended: this is **the one part of D-06 that is not pilot scope**. QS-8 raised. |
| 0.2.0 | 2026-08-18 | Victor | **QS-1 / QS-3 / QS-5 answered (Victor).** New **§5.1a** — what a risk budget *is*: max loss at the stop, not capital deployed; the same 2 % gives a **15 %–90 %** position depending only on stop width. **§5.1b** — the budget is **per account** (QS-3), accumulates, and is consumed as `max(0, entry−stop)×shares` so that **a winner whose stop trails above entry releases its whole allocation without being sold** — M-3 in arithmetic (**PS-29**). ⚠ **The "divide by n trades" derivation is circular**: total deployable notional is `R × entry/d` **independent of n** (verified: $60,000 at n=1,2,3,4). Replaced by **PS-27** (`n_reserve` = open slots, a stated policy) and **PS-28** (report which constraint binds — risk capacity or cash). **§5.1c** — risk parity **reported** (**PS-31**) and never ranked against (**PS-32**). CT-6.1 extended; AC-6.9a–f added; QS-7 raised. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. Records that **position size is currently authored by an LLM** (§1.4) — a live P2/AP-5 violation the existing contract already contradicts. §5.3 surfaces the collision this domain cannot avoid: **risk-based sizing mechanically fights M-2**. Scoped as a **pilot effort** per Victor. |

---

# 0. SCOPE — pilot

```text
╔══════════════════════════════════════════════════════════════════╗
║  RISK CALCULATION AND POSITION SIZING ARE A PILOT EFFORT.        ║
║  (Victor, 2026-08-18.)                                           ║
║                                                                  ║
║  Four registered accounts, orders to ~$30k, one human deciding.  ║
║  D-06 exists to replace an LLM's guess at a position size with   ║
║  arithmetic, and to show the consequence of a trade the human    ║
║  is already considering.                                         ║
║                                                                  ║
║  It is NOT an optimiser, NOT a risk system, and NOT a step       ║
║  toward one. §1.3 is the boundary and it is not negotiable       ║
║  at any scale.                                                   ║
║                                                                  ║
║  ★ ONE EXCEPTION, HIGH PRIORITY: the DYNAMIC RISK BUDGET         ║
║    (§5.1d). "A fixed percentage is meaningless in reality"       ║
║    — Victor. That is a full joint D-05/D-06 feature with its     ║
║    own mathematical framework, and it is not pilot work.         ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"If I did X, what happens to this book?"** — a question the human asked.

D-06 is the **forward-looking** half of SEAT-4; D-05 Risk is the backward-looking half. Both answer
*"what does this position do to this book?"* — D-05 for positions already held, D-06 for one being
considered.

## 1.2 Position

```text
                ┌─────────────────────────────────────┐
                │  SEAT 1 — PM & Trader (human)       │  asks · decides
                └──────────────▲──────────────────────┘
                               │ via D-09 (renders; never alters)
                ┌──────────────┴──────────────────────┐
                │  D-06 PORTFOLIO STRATEGY   SEAT-4   │  ← this spec
                │  size-given-a-stop · what-if math   │
                │  ★ deterministic · no LLM · no agent│
                └──▲──────────▲──────────▲────────────┘
                   │          │          │
              D-11 book  D-04 vol   D-02 features
              capital    forecast   beta, corr
              positions  ★ NOT YET BUILT (§9)
```

## 1.3 Boundary — the rule that defines the domain

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-06 COMPUTES CONSEQUENCES. IT NEVER PROPOSES A BOOK.           ║
║                                                                  ║
║  It answers  "if I did X, what happens?"                         ║
║  It NEVER answers "what should I hold?", never emits a target    ║
║  allocation, and never computes drift-from-target.               ║
║                                                                  ║
║  Optimising toward a target IS the diversification pressure      ║
║  M-2 rejects, and the allocation decision is SEAT 1's alone.     ║
║                                                                  ║
║  The domain name is inherited. Read it as PORTFOLIO ARITHMETIC,  ║
║  not portfolio construction.                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

**No agent serves D-06.** SEAT-4's agent is the Risk Manager Agent and its authority is **ALERT**;
D-06 is a computation the human invokes, not an actor with a voice.

## 1.4 ★ What is true today: an LLM is doing the arithmetic

```python
# buffett/synthesis/report_writer.py:139  — inside the LLM's JSON schema
"position_size_pct": {"type": "number", "description": "Suggested % of equity portfolio."}

# :693  — the prompt instruction
"7. position_size_pct should reflect risk — high beta + cyclical => smaller size."
```

Meanwhile the contract the value lands in says the opposite:

```python
# report/schemas.py:110-111
"""CT-1.1 ``position_size`` — risk-based sizing, never conviction-based."""
basis: str = "risk-based: % of portfolio from max-loss-at-stop (not conviction)"
```

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE CONTRACT SAYS "risk-based, from max-loss-at-stop".          ║
║  THE IMPLEMENTATION ASKS A LANGUAGE MODEL TO EYEBALL IT.         ║
║                                                                  ║
║  This is a live P2 / AP-5 violation — deterministic math must    ║
║  not be delegated to an LLM — and a spec-vs-code disagreement    ║
║  in which the SPEC is right.                                     ║
║                                                                  ║
║  Worse than wrong: the LLM's number arrives with a `basis`       ║
║  string asserting a derivation that never happened. It reads     ║
║  as computed. D-09 RP-1 would class it `computation` on the      ║
║  strength of that string.                                        ║
║                                                                  ║
║  D-06 EXISTS TO DELETE THAT FIELD FROM THE PROMPT.               ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **PS-1** | ★ **Position size is computed, never generated.** `position_size_pct` is removed from every LLM schema and prompt (P2, AP-5). D-01 may *narrate* a size it did not choose — DC-1, and the same rule as QA-27/MT-38 for the stop |

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **SizingQuestion** | one candidate trade | `question_id` | ticker, account, side, entry, stop, risk budget |
| **SizingAnswer** | one question | `question_id` | shares, notional, **and the consequences** — §5.4 |
| **Scenario** | book × hypothetical trade | `(as_of, trade_id)` | the book *after*, never a proposal |
| **ExposureDelta** | scenario × dimension | `(scenario, dim)` | name, sector, theme, currency, account |
| **PyramidCheck** | candidate vs held lot | `(ticker, account)` | **M-3** — average-cost direction |
| **HoldAlternative** | held position | `(ticker, account, as_of)` | ★ **M-3's other half** — §7.2 |

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-11  ★ the book: positions, cost basis, cash, CAPITAL BASE (RC-19)
  ├── D-04  ★ the VOLATILITY FORECAST — not yet built (§9)
  ├── D-02  beta, correlation inputs, sector/theme mapping
  └── D-05  current exposure (the backward-looking half of the same seat)

DEPENDED ON BY
  └── D-09 Reporting — renders the arithmetic; may not alter it (DC-1)

DOES NOT DEPEND ON
  ✗ D-01 — a thesis does not size a position (P2, and §5.3)
  ✗ the LLM gateway (AP-5, ST-5)
  ✗ any optimiser, target allocation, or benchmark
```

---

# 4. MODULE DECOMPOSITION

```text
src/portfolio/
├── sizing/          # size given a stop — §5
│   ├── risk_based.py
│   └── stop_distance.py   #   from the vol forecast; realised-vol fallback (§9)
├── scenario/        # what-if: the book after a hypothetical trade — §6
├── pyramid/         # ★ M-3: scale-in detection AND the hold alternative — §7
└── contracts/
```

---

# 5. POSITION SIZING GIVEN A STOP

## 5.1 The arithmetic

```
        risk_capital  =  capital_base × risk_budget_pct
        stop_distance =  entry − stop                     (per share, absolute)
        shares        =  risk_capital / stop_distance
        notional      =  shares × entry
```

**This is the only sizing basis D-06 computes.** Not conviction, not `rank_score`, not fair value —
**max loss at the stop**, which is the one quantity a stop makes knowable in advance.

| ID | Rule |
|---|---|
| **PS-2** | The basis is **max-loss-at-stop**. A size that varies with conviction is a conviction bet wearing a risk label |
| **PS-3** | `capital_base` comes from **D-11 (RC-19)**, point-in-time, never configured and never hard-coded |
| **PS-4** | Every output is a **`Money` with explicit currency** (INV-001). Entry, stop and capital may be in different currencies; the FX step is explicit and recorded (FX-2), and **absent a rate the answer is unavailable, not estimated** (FX-3) |
| **PS-5** | **A candidate with no stop gets no size.** Sizing without a stop is not conservative — it is undefined, and returning a number anyway invents the missing input |

## 5.1a What a risk budget actually is — and what it is not

> **The single most confused idea in position sizing**, and worth stating plainly before anything
> is built on it.

**The risk budget is the most you are willing to LOSE on the trade if the stop is hit. It is not
the amount of capital you deploy.**

```
        risk_capital  =  account_equity × risk_budget_pct     ← what you can LOSE
        shares        =  risk_capital / (entry − stop)
        notional      =  shares × entry                        ← what you DEPLOY
```

The two are related by **`entry / stop_distance`** — the *tightness* of the stop — and nothing else:

| Risk budget | Stop | Multiplier `entry/d` | Shares | **Position** |
|---|---|---|---|---|
| **2 %** ($2,000) | −2.2 % | 41× | 1,000 | **$90,000 = 90 % of account** |
| **2 %** ($2,000) | −6.7 % | 15× | 333 | **$30,000 = 30 %** |
| **2 %** ($2,000) | −13.3 % | 7.5× | 167 | **$15,000 = 15 %** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  SAME 2 % RISK. POSITION RANGES FROM 15 % TO 90 % OF THE         ║
║  ACCOUNT. THE STOP WIDTH DOES ALL OF IT.                         ║
║                                                                  ║
║  "I risk 2% per trade" says NOTHING about how concentrated the   ║
║  book is. A tight stop on a volatile name is a huge position     ║
║  with a small risk budget — and it will be stopped out often.    ║
║                                                                  ║
║  This is why PS-6 ties the stop to volatility rather than        ║
║  letting it be chosen: an eyeballed stop is an unstated          ║
║  position-size decision.                                         ║
╚══════════════════════════════════════════════════════════════════╝
```

## 5.1b The account-level risk budget — QS-1 and QS-3 answered

> **QS-3 closed (Victor): the risk budget is per account** — TFSA_1, TFSA_2, RRSP, RESP. They are
> separate registered accounts with separate capital that cannot be shared, so a fund-level budget
> would be an abstraction over something that cannot actually be moved.

### It accumulates, and it is spent and recovered

| Quantity | Definition |
|---|---|
| `risk_allowance` | `account_equity × r_total` — the account's **total** risk capacity |
| `risk_committed` | Σ over open positions of **`max(0, entry − stop) × shares`** |
| `risk_remaining` | `risk_allowance − risk_committed` |

★ **Committed risk is measured against the entry, floored at zero** — and that choice is
load-bearing:

| Price | Stop | Committed risk | |
|---|---|---|---|
| $90 | $84 | **$600** | at entry |
| $100 | $90 | **$0** | stop now above entry |
| $130 | $115 | **$0** | still zero |

```text
╔══════════════════════════════════════════════════════════════════╗
║  A WINNER WITH A TRAILING STOP STOPS CONSUMING RISK BUDGET.      ║
║                                                                  ║
║  Once the stop clears the entry, the position cannot lose money  ║
║  against cost, so it releases its whole allocation — WITHOUT     ║
║  SELLING ANYTHING.                                               ║
║                                                                  ║
║  That is M-3 implemented in arithmetic: "sell less and let       ║
║  winners run" is REWARDED, because holding a winner frees        ║
║  capacity for the next idea. Charging initial risk forever       ║
║  would penalise exactly the behaviour the mandate wants.         ║
╚══════════════════════════════════════════════════════════════════╝
```

### ⚠ The "divide by n trades" proposal — the intuition is right, the derivation is circular

The proposal: *if the remaining cash supports one more ticker, give it the remaining budget; if it
supports two, halve it.* **The intuition — don't spend the whole budget on one trade — is correct
and is now PS-27. The derivation does not work, for a reason worth seeing:**

```
        per-trade risk  =  R / n
        shares          =  (R/n) / d
        notional        =  (R/n) × (entry/d)
        total over n    =  n × (R/n) × (entry/d)  =  R × entry/d      ← n CANCELS
```

**Total capital deployed is `R × entry/d` no matter how you split it.** Verified: at `R = $4,000`,
`entry = $90`, `d = $6`, the total is **$60,000 whether n is 1, 2, 3 or 4**. Splitting changes only
the size of each trade, never how much cash the budget can absorb.

So *"how many trades does the cash support"* cannot determine `n` — it is either true for every `n`
or false for every `n`. **`n` has to come from somewhere else.**

### What replaces it: two independent questions

**① Which constraint binds?**

```
        risk_capacity_notional  =  risk_remaining × (entry / stop_distance)
        cash_available          =  free_cash
```

| Stop | Risk allows | Cash | **Binds** | Deploy | Risk consumed |
|---|---|---|---|---|---|
| tight (`d=$6`) | $60,000 | $40,000 | **CASH** | $40,000 | $2,667 of $4,000 |
| wide (`d=$18`) | $20,000 | $40,000 | **RISK** | $20,000 | $4,000 of $4,000 |

**② How many slots am I holding open?** — a *stated policy*, not a derivation:

```
        n_reserve            =  target_positions − current_positions   (per account)
        per_trade_budget     =  risk_remaining / n_reserve
```

| ID | Rule |
|---|---|
| **PS-27** | ★ **The per-trade risk budget is `risk_remaining / n_reserve`**, where `n_reserve` is the account's **open slots** — `target_positions − current_positions` — a **stated policy**, never derived from free cash. Deriving it from cash is circular: total deployable notional is `R × entry/d` independent of `n` |
| **PS-28** | ★ **Every sizing answer reports which constraint binds** — risk capacity or cash — with both numbers. *"Cash binds: $40,000 deployable against $60,000 of risk capacity"* is a different decision from the reverse, and the reader cannot infer it from the share count |
| **PS-29** | ★ **Committed risk is `max(0, entry − stop) × shares`**, so a position whose stop has trailed above entry **releases its budget without being sold** (M-3). The alternative convention — mark-to-market risk from the current price — would keep a winner charged forever and quietly penalise holding |
| **PS-30** | `risk_allowance`, `risk_committed` and `risk_remaining` are reported **per account** and never netted across accounts. Registered accounts hold capital that cannot be moved between them |
| **PS-43** | ★★ **`target_positions` is REQUIRED per-account configuration with no default, and `n_reserve == 0` makes the budget unavailable — never a fallback.** ⚠ *Added 2026-08-25 building B5, closing **QS-7**: **PS-27 divides the risk budget by `n_reserve`** and `target_positions` was declared nowhere — not in L0 §config, not here. A number that DIVIDES the risk budget cannot have an invented default*, and *"deriving it from cash is circular"* (PS-27) rules out the tempting inference. ★ PS-27 already calls it **"a stated policy"** — so it is stated, by the caller, per account, and reported on the answer beside the budget it produced. ⚠ **A full account (`n_reserve ≤ 0`) yields `unavailable`, not a division by a floor**: there is no open slot to size into, and a budget computed anyway would be sizing a position the policy says does not exist |
| **PS-44** | ★ **A MethodEntry lives in ITS OWN domain's `methods/entries/`; QA-20 owns the STANDARD, not the storage.** ⚠ *Added 2026-08-25: **AC-6.9k requires every applied risk-budget factor to resolve to a MethodEntry** and the register is D-03's (`CT-3.3`), so satisfying it would either put **D-06's entries in D-03's tree** or create a **SEAT-3 → SEAT-4 import edge** that the import graph cannot distinguish from consuming a nomination (FE-21's shape, one seat over).* ★ The register's check is a **filesystem scan, not an import**, so widening it to search each domain's own `entries/` directory satisfies QA-20 verbatim and **creates no dependency in either direction** |

## 5.1d ★ THE DYNAMIC RISK BUDGET — a feature, not a parameter

> **Elevated to HIGH PRIORITY 2026-08-18 (Victor):** *"A fixed percentage for risk budget is
> meaningless in reality. This alone is worth a full feature in portfolio-strategy and
> risk-management."*
>
> **This is the one part of D-06 that is not pilot scope** (§0). It spans **D-05 and D-06** — D-05
> measures portfolio risk state, D-06 translates it into a per-trade number — and it is a design
> effort, not a config value.

### Why a fixed percentage is wrong

Not "imprecise" — **wrong in kind**. A constant `r` is blind to every quantity that should move it:

| It ignores | Consequence |
|---|---|
| **Edge** | A marginal setup and a strong one get the same stake. That is a bet on different odds at the same price |
| **Correlation** | Five semiconductor names at 2 % each is **not** 10 % of risk — under M-2's deliberate concentration it is closer to one 6–8 % bet |
| **Drawdown state** | Risking 2 % at a high-water mark and 2 % after a 20 % drawdown are different acts with different survival consequences |
| **Estimation confidence** | At IC ≈ 0.03 the edge estimate is mostly noise. A budget that cannot shrink when confidence is low has no way to express doubt |
| **The opportunity set** | If nothing screens well, 2 % is too much; if everything does, 2 % is arbitrary |

### The proposed shape — multiplicative, bounded, measurable

```
        risk_budget_i  =  r_ceiling  ×  E_i  ×  C_i  ×  P_i  ×  D_i
                                        └─────────┬─────────┘
                                       each ∈ (0, 1]
```

| Factor | Meaning | Source | Computable today? |
|---|---|---|---|
| `r_ceiling` | the **maximum**, not the target — INV-022's cap | config | ✔ |
| **`E_i`** edge | signal strength vs the cross-section | `rank_score` z, or the D-03 §9.3 quantile band | ✔ |
| **`C_i`** confidence | ★ **D-01's k-run verdict stability (RM-1)**, model calibration, feature coverage | D-01, D-04 | ✖ **specified, not built** |
| **`P_i`** portfolio | **marginal** contribution to portfolio risk, not standalone | D-05 / D-02 correlation | ✔ (D-05 unspecified) |
| **`D_i`** drawdown | scales down as drawdown deepens | D-11 book | ✔ |

★ **Bounding every factor at 1 makes INV-022 structural**: the product can never exceed `r_ceiling`,
so *"the system's own recommendation may never exceed MAX_POSITION_PCT"* holds by construction
rather than by a clamp bolted on afterwards.

★ **`C_i` is the factor that makes this system's own machinery pay off.** `L1-fundamental-analysis.md`
§7.1 builds a k-run stability probe and §7.3 argues its whole value is that a reader *sizes
differently* on 3/5 than on 5/5. **`C_i` is where that stops being a hope and becomes arithmetic.**

### Candidate methods — each needs a MethodEntry before it is used

**QA-20 binds here** (D-03 §8): statement, symbols, reference, assumptions, what it was chosen over,
and a known-answer test. Sketched, not chosen:

| Method | Form | Why / why not |
|---|---|---|
| **Fractional Kelly** | `f* = μ/σ² `; with IC as the link, `f* ∝ ρ·z/σ` | Optimal log-growth, and it produces exactly the edge×(1/vol) shape wanted. **But it is savage under parameter uncertainty** — at IC ≈ 0.03 the error in `μ` dwarfs `μ`, so half-Kelly is a floor on the haircut, not a solution. *Kelly (1956); Thorp (2006); MacLean, Thorp & Ziemba (2011)* |
| **Volatility targeting** | `w_i ∝ σ_target / σ_i` | Robust, and needs only `σ` — the one thing this system can forecast well (D-03 §9.5). **Ignores edge entirely**, so it is the `P_i`/`D_i` half of the product, not the whole |
| **Marginal risk contribution** | `MCR_i = w_i (Σw)_i / σ_p` | The institutional standard and the honest treatment of correlation. **This is `P_i`** |
| **Drawdown control** | `r(t) = r_max·(1 − DD_t/DD_max)` | Survival constraint; connects to INV-024. **This is `D_i`.** *Grossman & Zhou (1993)* |
| **Risk of ruin** | size so `P(ruin) < ε` given win rate and payoff ratio | The most retail-appropriate framing, and the most legible to a human. A constraint on the product rather than a factor in it |

### The rule that keeps it honest

| ID | Rule |
|---|---|
| **PS-33** | ★ **The risk budget is computed per trade, not configured.** `r_ceiling` is a maximum; the budget is `r_ceiling × ∏ factors`, each factor ∈ (0,1], each **named, sourced and reported on the answer** (CT-6.1). A budget the reader cannot decompose is a fixed percentage with extra steps |
| **PS-34** | ★ **A factor that cannot be measured is set to 1 and reported as `unmeasured` — never estimated, never quietly omitted.** `C_i` is unmeasurable until RM-1 is built; it must show as `unmeasured`, so the budget is visibly *incomplete* rather than falsely complete. This is DE-35's rule in a fourth domain |
| **PS-35** | ★ **The framework must be able to report that it cannot differentiate.** At IC ≈ 0.03 `E_i` may be statistically indistinguishable from 1 across the whole cross-section. **Manufacturing differentiation from noise is worse than a flat budget**, because it wears the authority of arithmetic. `E_i` is applied only where the edge spread clears its own measurement error (D-03 §5.3b's MDE logic, applied to sizing) |
| **PS-36** | Every factor carries a **MethodEntry** (D-03 QA-20) — statement, reference, assumptions, alternatives rejected, known-answer test — before it multiplies a real position |

### Sequencing

| | |
|---|---|
| **Blocked on** | **D-05** (marginal risk contribution, drawdown state) — itself blocked on QQ-6; **RM-1** (verdict stability) for `C_i`; the **volatility forecast** (QA-41) for the `σ` every factor leans on |
| **Buildable first** | `D_i` (drawdown, from D-11's reconciled book) and `r_ceiling`. Together they are already better than a constant, and they need nothing that does not exist |
| **Scope** | **A joint D-05/D-06 feature.** It may warrant its own desk in `vision.md` §4 when it graduates to `sdd/specs/` — **QS-8** |

## 5.1c Risk parity — QS-5 approved, with the boundary intact

> **QS-5 closed (Victor): report the risk-parity comparison.**

```
        equal_risk_weight  =  risk_allowance / n_positions / (entry/d)   per name
```

| ID | Rule |
|---|---|
| **PS-31** | ★ D-06 **reports** the equal-risk weight beside the actual weight — *"equal-risk would be 6 %; you hold 31 %"*. It is the honest counterweight to a concentrated book, and INV-026 makes reporting mandatory and blocking forbidden |
| **PS-32** | ★ **It is a comparison, never a target.** D-06 does not rank names by distance from risk parity, does not compute drift toward it, and does not order a slate by it. **Reporting the number is a disclosure; optimising toward it is the target allocation PS-12 forbids** — and M-2 rejects the pressure it would apply |

## 5.2 The stop distance should come from volatility

A stop picked by eye is an unstated volatility assumption. The principled form:

```
        stop_distance  =  k · σ̂ · √h · entry
   ⇒    shares         =  risk_capital / (k · σ̂ · √h · entry)
   ⇒    shares         ∝  1 / σ̂
```

**Position size is inversely proportional to forecast volatility.** That is standard, and it is why
`L1-quantitative-analysis.md` §9.5 argues the volatility forecast — not the return forecast — is the
most decision-relevant ML output this system could produce.

| ID | Rule |
|---|---|
| **PS-6** | The stop distance is **`k · σ̂ · √h`** where `σ̂` is D-04's volatility forecast and `h` the holding horizon (**21 d**, HorizonSet v1). `k` is configuration and is **stated on every answer** |
| **PS-7** | Where the human supplies their own stop, D-06 **computes with it and reports the implied `k`**. A stop at 0.4σ and a stop at 3σ are different decisions and the number makes that visible |

## 5.3 ★ The collision: risk-based sizing mechanically fights M-2

```text
╔══════════════════════════════════════════════════════════════════╗
║  shares ∝ 1/sigma MEANS HIGH-VOLATILITY NAMES GET SMALL          ║
║  POSITIONS.                                                      ║
║                                                                  ║
║  The AI/semiconductor theme is high-volatility. M-2 says          ║
║  concentration in it is a DELIBERATE BET, not an accident.       ║
║                                                                  ║
║  So the textbook sizing rule systematically pushes the book       ║
║  AWAY from the posture the mandate chose. Applied as a           ║
║  RECOMMENDATION it would quietly implement the diversification   ║
║  pressure M-2 rejects — one trade at a time, with arithmetic     ║
║  as the alibi.                                                    ║
║                                                                  ║
║  This is QA-45's low-volatility tilt arriving in a second        ║
║  domain, by a completely different route.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

**The resolution is the same shape as QA-58's**: separate the *computation* from the *decision*.

| ID | Rule |
|---|---|
| **PS-8** | ★ **D-06 computes the risk-based size; it does not propose it.** The output is *"at a 2 % risk budget and a 1.5σ stop this is 340 shares"* — a **consequence of stated assumptions**, not an answer to "how much should I buy" |
| **PS-9** | ★ **The human's intended size is a first-class input.** Given one, D-06 reports **the risk budget it implies** and the exposure it produces. It never substitutes its own number for theirs (INV-026 — reported, never blocked) |
| **PS-10** | **INV-022 caps only what the system proposes.** A computed size above `MAX_POSITION_PCT` (15 %) is **capped and labelled as capped**. The human's own size is **never capped** — it is reported with its consequences, and M-2 makes that distinction load-bearing |

## 5.4 What a SizingAnswer actually contains

Not a number. A number, its assumptions, and what it does to the book:

| Block | Content |
|---|---|
| **The arithmetic** | shares, notional, risk capital, stop distance, implied `k`, `σ̂` and **its source** |
| **The assumptions** | risk budget, capital base and its `as_of`, horizon, FX rate if used |
| **The consequences** | resulting weight in the account, in the fund, sector %, **theme %**, currency mix |
| **The thresholds crossed** | against `CONCENTRATION_THRESHOLD_PCT` 25, `SECTOR_MAX_PCT` 35, `THEME_REPORT_THRESHOLD_PCT` 40 — **as reports, never vetoes** (INV-026) |
| **The M-3 check** | does this raise the average cost of an existing lot? (§7) |
| **What is missing** | any input unavailable, named — never silently defaulted |

---

# 6. SCENARIO ARITHMETIC

| ID | Rule |
|---|---|
| **PS-11** | A scenario is **the book after a stated hypothetical**, computed from D-11's actual book. It is never a suggestion, and the artifact says so in words |
| **PS-12** | **No target allocation, no recommended book, no drift-from-target** — the forbidden dependency in L0 §4.3, restated because it is the thing this domain would drift into |
| **PS-13** | Scenarios are **deterministic and reproducible**: same book + same hypothetical + same `as_of` ⇒ byte-identical (INV-2) |
| **PS-14** | Stress scenarios state their **historical source or their assumption**, and are labelled **not predictions** (INV-010's spirit) |

---

# 7. M-3 — PYRAMIDING, AND ITS OTHER HALF

> **M-3:** *"Pyramiding-up is the behaviour to curb. The intended fix is to **sell less and let
> winners run**, not to scale in at ever-higher average cost. Features must serve **holding
> winners**, not only exiting."*

## 7.1 The scale-in check

| ID | Rule |
|---|---|
| **PS-15** | A candidate buy in a **held** name computes the **resulting average cost**. If it rises, the trade is **pyramiding-up and is flagged** with the before/after average cost and the added exposure |
| **PS-16** | ★ **Flagged, never blocked** (INV-028, INV-026). A fund-manager override is **logged and visible** — D-11's journal (RC-24) — never prevented |

## 7.2 ★ The half that is usually forgotten

M-3's second sentence is a *requirement*, not context: **features must serve holding winners, not
only exiting.** A domain that only ever computes "what if I sell" satisfies the letter of the
mandate and inverts its intent — the same defect QA-55 records for the timing leg.

| ID | Rule |
|---|---|
| **PS-17** | ★ For a held position, D-06 computes the **hold alternative** alongside any trim: what holding preserves (exposure, unrealised gain, optionality) against what trimming realises (cash, reduced concentration, **and — since all four accounts are registered — no tax event, D-11 §5.5**). **Holding is a first-class computed alternative, not the absence of an action** |
| **PS-18** | A trim scenario reports the **remaining position's** risk-based size, so *"should I trim"* and *"is what remains correctly sized"* are answered together rather than sequentially |

---

# 8. MULTI-ACCOUNT AND CURRENCY

Four accounts, **all registered**; the RESP is excluded from fund performance (D-11 RC-4).

| ID | Rule |
|---|---|
| **PS-19** | **Sizing is per account** — you buy in one — while **exposure is book-wide**. Both are reported, and conflating them understates concentration |
| **PS-41** | ★ **D-06 reads `L1-recording.md` **CT-11.4 BookState** for the capital base and current exposure** — `capital_base`, `nav_base`, `positions[]` — and **D-05's `P`/`D` factors** for the risk terms (RK-20/21). ⚠ *Added by cross-spec audit: this spec sized against "the book" without naming its contract.* ★ **`capital_base` is read, never assumed** (D-03 QA-107) — and a `BookState` with `reconciled: "break"` or `nav_base: null` **cannot size a position**, because every sizing output is a fraction of a number that is not currently known |
| **PS-20** | The **RESP is excluded** from fund exposure and sizing by default (RC-4), and its exclusion is stated on the artifact rather than assumed |
| **PS-21** | ★ **No tax-lot reasoning is needed, and that is a finding, not an omission.** All four accounts are registered (D-11 §5.5), so a trim triggers **no capital-gains event**. The usual "tax cost of trimming" term is **identically zero here** — which strengthens M-3's *"trim rather than exit"* rather than weakening it |
| **PS-22** | Currency is explicit throughout (M-5). A CDR is CAD, its underlying USD; **exposure aggregates in base currency with the FX rate recorded** (FX-2), and is unavailable without one (FX-3) |

---

# 9. WHAT IS NOT COMPUTABLE YET

| Input | Status | D-06's response |
|---|---|---|
| **Volatility forecast `σ̂`** | ★ **Not built** — D-04 QA-41, D-03 QQ-9 | **PS-23** |
| Correlation / beta | D-02 can supply from the price panel | available |
| Sector / theme mapping | D-07 `profile`, **Class B** (no as-of) — D-02 QF-5 | available, with a caveat |
| Current exposure | D-05, **not yet specified** | D-06 can compute it from D-11 directly in the interim |

| ID | Rule |
|---|---|
| **PS-23** | ★ Until D-04 publishes a volatility forecast, D-06 uses **realised volatility as a stand-in, labelled `realised`, and never called a forecast.** The distinction is not pedantry: realised vol is backward-looking and understates exactly when it matters — before an earnings gap. D-09 renders the label (RP-1) |
| **PS-24** | An input that is unavailable makes the dependent output **unavailable, not estimated** (P5, FX-3's shape). A sizing answer with a missing `σ̂` says so |

---

---

# 6Z. ★ WHERE D-06 GETS ITS INPUTS — the D-12 seam

> ⚠ **Added after a consistency audit.** This spec predates **D-12 Decision** (L0 v0.17.0). D-12's
> §1.5 forbids `D-12 → D-06` ("sizing is not composition"), which left D-06 with **no stated source
> for the graded information sizing needs**.

| ID | Rule |
|---|---|
| **PS-37** | ★ **D-06 reads the transported `grade` block from `CT-12.1`** — `ranked_quantity`, `conviction`, `stability_fraction`, `scorecard` — which D-12 **DN-25** carries precisely so it does not die at the composition layer. **D-06 still does not read D-01 or D-03 directly**, so the cross-seat coupling INV-014 guards stays mediated |
| **PS-38** | ★ **The grade is an INPUT to sizing, never a multiplier applied blindly.** **RA-20** says a reader seeing 3/5 stability should size differently; **PS-1** says size is computed, not generated. Both hold: the stability fraction enters the computation, and the computation is deterministic |
| **PS-39** | ⚠ **D-06 sizes only what D-12 marked `actionable: true`.** A recommendation that was vetoed, incomplete, or `NO_THESIS` is not a sizing input (D-12 DN-12/DN-22, DC-3) |
| **PS-40** | ★ **The scorecard is read, never summed** (D-01 **RA-53**). A weighted composite would be a second verdict produced by weights nobody fitted — `L2` §5.0's argument, with more force at D-06's smaller `n` |

# 10. CONTRACTS

> **ID-collision notice.** `AC-6.k` / `CT-6.k` key `n` on **D-06**. No `F6` spec exists yet — but
> **F6 is reserved** in `vision.md` §4 (*macro & regime context*), so this family is **latent**, like
> D-07/F7 (L0 §16.4). Qualify anyway.

## CT-6.1 — SizingAnswer (JSON)

```json
{
  "question_id": "…", "ticker": "MU", "account_id": "TFSA_1", "as_of": "2026-08-18",
  "arithmetic": {
    "shares": 340, "notional": {"minor": 3110000, "currency": "CAD"},
    "risk_capital": {"minor": 200000, "currency": "CAD"},
    "stop_distance_per_share": {"minor": 5880, "currency": "CAD"},
    "implied_k": 1.5, "sigma": 0.0412, "sigma_source": "realised_20d", "sigma_class": "realised"
  },
  "assumptions": {"risk_budget_pct": 2.0, "capital_base_as_of": "2026-08-17",
                  "horizon_days": 21, "fx_rate_used": null,
                  "n_reserve": 2, "risk_source": "risk_remaining / n_reserve"},
  "risk_budget_factors": {                       // PS-33/34 — decomposed, never opaque
    "r_ceiling": 0.02,
    "E_edge":       {"value": 1.00, "status": "unapplied", "why": "edge spread below its MDE"},
    "C_confidence": {"value": 1.00, "status": "unmeasured", "why": "RM-1 not built"},
    "P_portfolio":  {"value": 0.70, "status": "applied", "source": "D-05 marginal risk"},
    "D_drawdown":   {"value": 0.85, "status": "applied", "source": "D-11 book"},
    "effective":    0.0119},
  "account_risk": {"allowance": 600000, "committed": 200000, "remaining": 400000,
                   "currency": "CAD", "committed_basis": "max(0, entry-stop) x shares"},
  "binding_constraint": {"binds": "cash", "risk_capacity_notional": 6000000,
                         "cash_available": 4000000, "currency": "CAD"},
  "risk_parity": {"equal_risk_weight_pct": 6.0, "actual_weight_pct": 31.0,
                  "is_target": false},
  "consequences": {"weight_account_pct": 14.2, "weight_fund_pct": 6.1,
                   "sector_pct": 38.4, "theme_pct": 61.7},
  "thresholds_crossed": [
    {"name": "SECTOR_MAX_PCT", "limit": 35.0, "value": 38.4, "effect": "reported_only"},
    {"name": "THEME_REPORT_THRESHOLD_PCT", "limit": 40.0, "value": 61.7, "effect": "reported_only"}
  ],
  "capped_by_inv022": false,
  "pyramid": {"is_scale_in": true, "avg_cost_before": 84.10, "avg_cost_after": 89.55},
  "unavailable": []
}
```

**`effect: "reported_only"` is on every threshold** — there is no other value (INV-026). `capped_by_inv022`
records INV-022 explicitly, and applies **only** to a system-computed size.

## CT-6.2 — Scenario (JSON)

`(scenario_id, as_of, book_ref, hypothetical{}, exposure_before{}, exposure_after{}, deltas{},
is_proposal: false)` — the last field is a **constant**, present so the contract states it.

## CT-6.3 — HoldAlternative (JSON)

`(ticker, account_id, as_of, hold{exposure, unrealised, optionality_note},
trim{cash_freed, exposure_after, tax_event: false, remaining_size_check})`

---

# 11. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `size_for_stop(ticker, account, entry, stop, risk_budget, as_of)` | `SizingAnswer` | raises without a stop (PS-5) |
| `implied_risk(ticker, account, entry, stop, shares, as_of)` | `SizingAnswer` | ★ the human's size in, the implied budget out (PS-9) |
| `account_risk(account, as_of)` | `RiskBudgetState` | allowance · committed · remaining (PS-29, PS-30) |
| `risk_parity(account, as_of)` | `ParityComparison` | reported, never a target (PS-31, PS-32) |
| `scenario(hypothetical, as_of)` | `Scenario` | the book after; never a proposal |
| `pyramid_check(ticker, account, add_qty, price)` | `PyramidCheck` | flags, never blocks (PS-16) |
| `hold_alternative(ticker, account, as_of)` | `HoldAlternative` | ★ M-3's other half (PS-17) |
| `exposure_after(hypothetical, as_of)` | `ExposureDelta` | name · sector · theme · currency · account |

---

# 12. BUSINESS RULES

| ID | Rule |
|---|---|
| PS-1 | Position size is computed, never generated — §1.4 |
| **PS-2…PS-10** | Sizing — §5 |
| **PS-11…PS-14** | Scenarios — §6 |
| **PS-15…PS-18** | M-3 — §7 |
| **PS-19…PS-22** | Accounts & currency — §8 |
| **PS-23…PS-24** | Missing inputs — §9 |
| **PS-27…PS-30** | The account risk budget — §5.1b |
| **PS-31…PS-32** | Risk parity — §5.1c |
| **PS-33…PS-36** | ★ The dynamic risk budget — §5.1d |
| **PS-25** | D-06 imports **no LLM gateway** (AP-5, ST-5) and **no D-01** output |
| **PS-26** | D-06 **writes nothing**. It computes on demand and returns; the book is D-11's |

---

# 13. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `PST.SIZE.NO_STOP` | ERROR | sizing requested with no stop — undefined, not conservative (PS-5) |
| `PST.SIZE.NO_CAPITAL_BASE` | ERROR | D-11 has no reconciled book at `as_of` (PS-3) |
| `PST.SIZE.NO_VOLATILITY` | ERROR | neither forecast nor realised σ available (PS-24) |
| `PST.SIZE.FX_UNAVAILABLE` | ERROR | cross-currency sizing with no rate — unavailable, never estimated (FX-3) |
| `PST.SIZE.CAPPED` | WARNING | system-computed size exceeded `MAX_POSITION_PCT`; **capped and labelled** (INV-022) |
| `PST.EXPOSURE.THRESHOLD` | WARNING | a reporting threshold crossed — **never a veto** (INV-026) |
| `PST.PYRAMID.SCALE_IN` | WARNING | average cost rises — **flagged, never blocked** (M-3, INV-028) |
| `PST.SCENARIO.PROPOSAL_REQUESTED` | ERROR | a caller asked for a target allocation or drift-from-target (PS-12, L0 §4.3) |
| `PST.INPUT.ANALYST_DERIVED` | ERROR | a sizing input traced to D-01 (PS-25, P2) |

---

# 14. ACCEPTANCE CRITERIA

```text
SIZING  (§5)
□ AC-6.1   position_size_pct is absent from every LLM schema and prompt (PS-1, P2)
□ AC-6.2   shares = risk_capital / stop_distance; no conviction term enters (PS-2)
□ AC-6.3   capital_base comes from D-11 point-in-time, never configured (PS-3)
□ AC-6.4   Sizing with no stop raises (PS-5)
□ AC-6.5   Every answer states sigma, its source AND its class (forecast|realised)
□ AC-6.6   A user-supplied stop yields the implied k on the answer (PS-7)
□ AC-6.7   implied_risk() accepts the human's share count and returns the implied
           budget — it never substitutes its own number (PS-9)
□ AC-6.8   A system-computed size over MAX_POSITION_PCT is capped AND labelled;
           a human-supplied size is never capped (PS-10, INV-022 vs M-2)
□ AC-6.9   Cross-currency sizing with no FX rate returns unavailable (FX-3, PS-4)

RISK BUDGET  (§5.1a-c)
□ AC-6.9a  Committed risk = max(0, entry-stop) x shares; a stop above entry
           releases the whole allocation without a sale (PS-29, M-3)
□ AC-6.9b  risk_allowance/committed/remaining are per account, never netted (PS-30)
□ AC-6.9c  n_reserve comes from target_positions - current_positions, never from
           free cash; a cash-derived n_reserve raises (PS-27)
□ AC-6.9d  Every answer states which constraint binds, with both numbers (PS-28)
□ AC-6.9e  The equal-risk weight is reported beside the actual weight (PS-31)
□ AC-6.9f  Nothing ranks, sorts or tracks drift against risk parity (PS-32, PS-12)

DYNAMIC RISK BUDGET  (§5.1d)
□ AC-6.9g  Every risk budget reports its factor decomposition; an opaque scalar
           fails the contract (PS-33)
□ AC-6.9h  An unmeasurable factor is 1.0 with status=unmeasured — never estimated,
           never omitted (PS-34)
□ AC-6.9i  The product never exceeds r_ceiling, by construction (INV-022)
□ AC-6.9j  E_edge is applied only where the edge spread clears its own measurement
           error; otherwise status=unapplied (PS-35)
□ AC-6.9k  Every applied factor resolves to a MethodEntry (PS-36, QA-20)
□ AC-6.9l  ★ target_positions is supplied per account, reported on the answer, and
           n_reserve <= 0 yields unavailable rather than a fallback (PS-43, QS-7)
□ AC-6.9m  ★ D-06's MethodEntries live in src/portfolio/methods/entries/, and
           src/portfolio imports nothing from src/quant (PS-44, QA-20)

CONSEQUENCES, NOT PROPOSALS  (§6)
□ AC-6.10  Every threshold crossing carries effect="reported_only" (INV-026)
□ AC-6.11  A request for a target allocation or drift-from-target raises (PS-12)
□ AC-6.12  Same book + hypothetical + as_of => byte-identical scenario (INV-2)
□ AC-6.13  Stress scenarios are labelled not-predictions

M-3  (§7)
□ AC-6.14  A buy raising the average cost of a held lot is flagged with before/after
□ AC-6.15  A pyramiding flag never blocks; an override is journalled (INV-028)
□ AC-6.16  hold_alternative() is computed for held positions — holding is a
           first-class alternative, not the absence of an action (PS-17)
□ AC-6.17  A trim scenario reports tax_event=false (all accounts registered, PS-21)

ACCOUNTS, CURRENCY, BOUNDARY
□ AC-6.18  Sizing is per account; exposure is book-wide; both reported (PS-19)
□ AC-6.19  RESP exclusion is stated on the artifact, not assumed (PS-20)
□ AC-6.20  src/portfolio imports no LLM gateway and no D-01 output (PS-25)
□ AC-6.21  D-06 writes nothing (PS-26)
```

---

# 15. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QS-1** | ★★ **How is the risk budget computed per trade?** | 🔴 **HIGH PRIORITY — a full joint D-05/D-06 feature, NOT a config value** (Victor, 2026-08-18): *"a fixed percentage for risk budget is meaningless in reality"*. **Framework sketched in §5.1d**: `r_ceiling × E × C × P × D`, each factor ∈ (0,1] so INV-022 holds structurally. **Resolved when Risk & Portfolio Management is implemented**, not before. `D` (drawdown) and `r_ceiling` are buildable today; `C` waits on RM-1; `P` waits on D-05. **§5.1b's `risk_remaining / n_reserve` is the interim mechanism, not the answer** |
| **QS-2** | What is **`k`** in `stop = k·σ̂·√h`? | 1.5–2σ is conventional. Interacts with QA-56's triple-barrier `k` — **they should be the same number**, and currently neither exists |
| ~~QS-3~~ | ~~Per account or per fund?~~ | ✅ **CLOSED 2026-08-18 (Victor): per account.** TFSA_1, TFSA_2, RRSP, RESP hold capital that cannot be moved between them, so a fund-level budget would abstract over something unactionable. **PS-30** — never netted across accounts |
| ~~**QS-4**~~ | ~~Does D-06 own exposure until D-05 exists?~~ | ✅ **CLOSED — D-05 exists** (`L1-risk-management.md`). Exposure is **RK-1…RK-7**; D-06 reads it, never recomputes it. The premise (*"D-05 is blocked on QQ-6"*) was itself stale |
| ~~QS-5~~ | ~~Should D-06 report a risk-parity comparison?~~ | ✅ **CLOSED 2026-08-18 (Victor): yes, report it.** §5.1c — **PS-31** reports the equal-risk weight beside the actual; **PS-32** forbids ranking, drift-tracking or slate-ordering against it. Reporting is a disclosure (INV-026); optimising toward it is the target allocation PS-12 forbids |
| **QS-8** | Does the dynamic risk budget warrant **its own desk** in `vision.md` §4? | It spans D-05 and D-06, has its own mathematical framework, and is the kind of thing F5–F10 reserve IDs for. Decide at promotion, not now |
| ~~**QS-7**~~ | ~~What is `target_positions` per account?~~ ✅ **CLOSED 2026-08-25 — PS-43: it is required per-account configuration with no default.** ★ *A number that divides the risk budget cannot have an invented one*, and PS-27 already called it a stated policy. | Feeds `n_reserve` (PS-27). Interacts with D-03 §5.8's `N=5` sleeve resolution — but that was one book, and there are four accounts. Needs settling with `r_total` |
| **QS-6** | What is the **theme taxonomy**? | `THEME_REPORT_THRESHOLD_PCT` is 40 % and there is no definition of "AI/semiconductor" anywhere in the repo. A threshold on an undefined set is unenforceable |

---

# 16. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-06, §4.3, **M-2, M-3**, **INV-022, INV-026, INV-028**, §8 | the boundary, the mandate this domain collides with, the thresholds |
| `L1-recording.md` **RC-19**, RC-4, §5.5 | the capital base; RESP exclusion; **all accounts registered ⇒ no tax event on a trim** |
| `L1-model-training.md` **MT-38**, and D-03 **QA-41 / §9.5** | the volatility forecast PS-6 needs and §9 does without |
| `L1-quantitative-analysis.md` **QA-45**, QA-56, QA-58 | the low-volatility tilt §5.3 meets again; `k`; computation-vs-decision separation |
| `L1-reporting.md` **RP-1**, DC-1 | how a `realised` σ label reaches the reader; renders but never alters |
| `sdd/specs/constitution.md` **P2**, P5, INV-2 | deterministic math stays code — the violation §1.4 records |
| `pipeline/report/schemas.py:110` | the contract that already says "risk-based, never conviction-based" |
