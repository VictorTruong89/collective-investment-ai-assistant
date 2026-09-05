# L1: Domain Specification — Risk Management (D-05)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-05 · **Seat:** SEAT-4
> **Path:** `src/risk/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Depends on:** [`L1-recording.md`](L1-recording.md) (D-11, the book) ·
> [`L1-feature-engineering.md`](L1-feature-engineering.md) (D-02) · D-04 (volatility forecast)
> **Prior art:** `pipeline/discipline/{risk,flags,context}.py` (~630 LOC, **F2, 8/8 ACs green**)
> **Binding:** **INV-021**, **INV-026**, INV-023, INV-024, INV-028 · **M-2**, **M-3**, **M-4**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.5.0 | 2026-08-25 | Victor | ⚠⚠ **B5 readiness — three defects, and two open questions this milestone cannot be built around.** ★★ **RK-37 (closes QK-2)**: `L1-feature-engineering` §6.4 says **D-02 publishes theme mappings** while **RK-6** makes the taxonomy a declared artifact — and for D-02 to label a theme it must know the taxonomy, which **FE-21 forbids**. **D-02 publishes sector; D-05 resolves theme** from its own **CT-5.3**, so no import edge appears in either direction. ★★ **RK-38**: **AC-5.19 says `drawdown()` needs "D-11's book alone"** but `CT-11.4` is **one account on one day**, while `peak`/`duration_days` need history and **RK-27 forbids D-05 persisting a tracker**. The series *is* the accumulation of CT-11.4; the peak is derived, and ⚠ an incomplete series is **unmeasured, never zero**. ★★ **RK-39 (closes QK-4)**: the premature-exit flag reports a **distribution**, not a threshold — *and the only artifact carrying an intended horizon is the thesis, which **RK-28 forbids D-05 to import***. AC-5.6a/5.13a/5.19a added. |
| 0.4.0 | 2026-08-22 | Victor | ★★ **New §4A — the runtime workflow, which did not exist.** §5–§9 gave the *measures* and §11 listed methods in no order; **nothing said what runs when**, and an implementation audit found four unanswered questions. **Five workflows (WF-R1…WF-R5), the daily ladder with the rule forcing each position, RK-29…RK-36.** ★★ **RK-29: never compute on an unreconciled book** — the tempting fallback (use the last good book) produces a correct-looking report *about yesterday* with nothing on the artifact saying so. ★★ **RK-30: alerts emit only from a complete pass**, because in a domain whose value is that silence means *"nothing found"*, a partial alert set is an all-clear on everything absent. ★ **RK-34 states that there is NO gate step** — INV-026 means one would be wrong, and saying so is cheaper than having someone add it. |
| 0.3.0 | 2026-08-18 | Victor | ⚠ **QK-5 stale — closed by D-12.** And the answer was already implied by this spec: **INV-026 gives D-05 zero blocking authority, so it could never have owned the gate.** |
| 0.2.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: D-05 read "the book" in prose and cited no contract.** **RK-0** names **CT-11.4 BookState** as the input, and adds the rule that follows from its `reconciled` field: ★ **a book in `break` is not a risk input** — exposure measured on an unreconciled book describes a book that does not exist. Also fixes the `nav_base: null` case (FX-3): a cross-currency exposure with no rate is **unavailable**, not zero. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. §1.4 states the domain's defining tension — **maximum voice, zero authority**. §6 says plainly that **VaR is near-useless on a deliberately concentrated ten-name book** and what replaces it. §8 supplies the `P` and `D` factors D-06 §5.1d needs. **The gate stays deferred** to L0 §1.6 (QQ-6) — this spec covers measurement, not combination. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"What is this book actually exposed to, and has anything crossed a line worth saying out loud?"**

D-05 is the **backward-looking** half of SEAT-4 — risk in the book as it stands. D-06 is the
forward-looking half: risk in a trade being considered. Both answer *"what does this position do to
this book?"*, one for held positions and one for hypothetical ones.

## 1.2 Position

```text
                ┌──────────────────────────────────────┐
                │  SEAT 1 — PM & Trader (human)        │  must act on ALERTs
                └───────────────▲──────────────────────┘
                                │ via D-09 (renders; may never suppress)
                ┌───────────────┴──────────────────────┐
                │  D-05 RISK MANAGEMENT     SEAT-4     │  ← this spec
                │  exposure · drawdown · correlation   │
                │  behavioural flags (M-3, M-4)        │
                │  ★ LEVEL 2 ALERT · Risk Manager Agent│
                └───▲──────────────▲───────────────┬───┘
                    │              │               │
              D-11 book      D-02 features     D-06 consumes
              positions      corr, beta        P and D factors
              drawdown       sector/theme      (§8)
```

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-05 MEASURES AND SAYS. IT NEVER BLOCKS AND NEVER SIZES.        ║
║                                                                  ║
║  In scope:  exposure by name/sector/theme/currency/account,      ║
║      drawdown, correlation, concentration, stress scenarios,     ║
║      and the BEHAVIOURAL FLAGS M-3 and M-4 name.                 ║
║                                                                  ║
║  Out of scope:                                                   ║
║      position sizing and what-if arithmetic  -> D-06             ║
║      the VERDICT GATE                        -> deferred, §1.5   ║
║      any refusal, veto, downgrade or block   -> INV-026          ║
╚══════════════════════════════════════════════════════════════════╝
```

> ⚠ **L0 §4.2's D-05 entry is stale.** It still says D-05 *"also owns the sizing and scenario
> arithmetic"* — text from **v0.5.0**, when Portfolio Strategy had been deleted. **v0.6.0 restored
> D-06 and the sentence was never removed.** Sizing is D-06's; the L0 text needs the one-line fix.
> **QK-1.**

## 1.4 ★ The defining tension: maximum voice, zero authority

Two invariants bind this domain and they pull in opposite directions:

| | |
|---|---|
| **INV-021** | *"Risk alerts cannot be suppressed or silenced by any component."* |
| **INV-026** | *"Concentration and theme exposure are **reported, never blocked**. No component may refuse, downgrade or hide a position because it increases concentration."* |

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-05 CANNOT BE SILENCED AND CANNOT STOP ANYTHING.               ║
║                                                                  ║
║  That combination is unusual, and it is the whole character of   ║
║  the domain. Most risk systems earn their keep by refusing;      ║
║  this one earns it by being impossible to ignore and impossible  ║
║  to obey.                                                        ║
║                                                                  ║
║  It follows directly from M-2: the concentration IS the bet.     ║
║  A risk function that could veto it would be overruling the      ║
║  mandate on the strength of a statistic.                         ║
║                                                                  ║
║  So every threshold in L0 §8 is a REPORTING threshold. The only  ║
║  cap in the system is INV-022, and it caps what the SYSTEM       ║
║  proposes — never what Victor may hold.                          ║
╚══════════════════════════════════════════════════════════════════╝
```

**Authority: LEVEL 2 ALERT** (L0 §3.1) — *"system warns, human must act"*. Stronger than RECOMMEND
in obligation, weaker in power: D-05 cannot act, and its warning cannot be dismissed by any
component other than the human.

## 1.5 What is deferred, and what is not

**Deferred:** `discipline/gate.py` — the verdict gate. It implements the **combine point** (L0 §1.6,
`L4` Q-5, D-03 QQ-6), which is still open. **That is a combination question, not a risk question**,
and D-05 does not need it.

**Not deferred:** everything in §1.3's in-scope list. `discipline/{risk,flags,context}.py` are ~630
LOC of working, F2-governed, 8/8-green code that measures exposure and raises flags, and none of it
waits on §1.6.

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **PositionRisk** | position × as_of | `(account, instrument, as_of)` | weight, vol, beta, corr-to-book, **marginal contribution** |
| **BookRisk** | book × as_of | `as_of` | aggregate exposure, drawdown, concentration |
| **ExposureView** | dimension × as_of | `(dim, as_of)` | name · sector · **theme** · currency · account |
| **DrawdownState** | book × as_of | `as_of` | current, peak, depth, duration — ★ the `D` factor (§8) |
| **Flag** | one behavioural warning | `(kind, ticker, as_of)` | M-3 pyramiding, M-4 short-hold — **unsuppressible** |
| **Alert** | one LEVEL-2 notification | `alert_id` | crossed a reporting threshold; never a veto |
| **StressResult** | scenario × as_of | `(scenario_id, as_of)` | labelled, never a prediction |

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON
  ├── D-11  ★ the book — positions, cost basis, capital base, trade history
  ├── D-02  correlation inputs, beta, sector/theme mapping
  └── D-04  the volatility forecast (realised-vol stand-in until built)

DEPENDED ON BY
  ├── D-06  ★ the P (marginal risk) and D (drawdown) factors — §8
  └── D-09  renders alerts and flags; ★ MAY NOT SUPPRESS THEM (INV-021)

DOES NOT DEPEND ON
  ✗ D-01 — a thesis is not a risk input
  ✗ the LLM gateway (AP-5, ST-5). The Risk Manager Agent's authority is
      ALERT; the measurement underneath it is arithmetic
  ✗ D-08 Orchestration — L0 §4.3's forbidden edge, stated there and kept
```

---

# 4. MODULE DECOMPOSITION

```text
src/risk/
├── exposure/        # name · sector · theme · currency · account
├── metrics/         # vol, beta, correlation, drawdown, marginal contribution
├── stress/          # scenario replay — labelled, never predictive
├── flags/           # ★ M-3 pyramiding · M-4 registered short-hold
├── alerts/          # LEVEL 2 emission; unsuppressible by construction
└── contracts/
```

---

# 4A. ★ THE RUNTIME WORKFLOW — what runs, in what order, on what trigger

> ⚠ **Added v0.4.0 to close a gap found by an implementation audit.** §5–§9 state the *measures* —
> exposure, VaR, flags, the `P`/`D` factors, stress — and §11 lists methods in no order. **Nothing
> said what runs when.** An agent asked to build this domain faced four questions the spec did not
> answer: does exposure precede the flags; is stress daily; what happens when the book does not
> reconcile; are `P`/`D` computed every run or on demand. **This section answers them.**
> *(Same shape as `L1-fundamental-analysis.md` §4A, and written for the same reason.)*

## 4A.0 Who triggers, and the one thing this domain never does

D-08 invokes; D-05 sequences itself (OR-1, OR-3). ★ **And a reader arriving from another domain
should be told immediately what is absent: there is no gate step in this ladder.** D-05 holds
**zero authority** (INV-026). It measures, it flags, it never blocks — so nothing below returns a
pass/fail that anything waits on.

## 4A.1 Five workflows

| ID | Workflow | Trigger | Cadence | Emits |
|---|---|---|---|---|
| **WF-R1** | **The daily book pass** | the 10:00 ET run, ★ **after D-11 reconciles** | daily | `BookRisk` (CT-5.1) · `Flag[]` (CT-5.2) |
| **WF-R2** | **Candidate risk** | D-06 or D-12 asks *"what would this position do to the book?"* | on request | marginal contribution · `P` · `D` |
| **WF-R3** | **Stress replay** | weekly, or on request | weekly | labelled scenario outcomes |
| **WF-R4** | **Behavioural flags** | inside WF-R1 | daily | M-3 · M-4 flags |
| **WF-R5** | **Alert emission** | end of WF-R1 | daily | ★ unsuppressible alerts |

## 4A.2 WF-R1 — the daily book pass

```text
  0  RECONCILED?   D-11 book state balances        deterministic   ⛔ ABORT
                                 │
                                 ▼
  1  SNAPSHOT      book at as_of (CT-11.4)         nav_base · capital_base
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼          ║ PARALLEL ║
  2  EXPOSURE                                 4  FLAGS
     name · sector · theme                       M-3 pyramiding
     currency · account                          M-4 registered short-hold
              │                                     │
              ▼                                     │
  3  METRICS   vol · beta · correlation             │
              drawdown · marginal contribution      │
              │                                     │
              └──────────────────┬──────────────────┘
                                 ▼
  5  FACTORS     P and D for D-06 (§8)
                                 │
                                 ▼
  6  ALERTS      emit — only from a COMPLETE pass
                                 │
                                 ▼
  7  PUBLISH     BookRisk (CT-5.1) · Flag[] (CT-5.2)
```

### What forces each position

| Step | Forced there by | What breaks if it moves |
|---|---|---|
| **0** before everything | ★★ **P5 / RK-29** | **A risk number computed on an unreconciled book is worse than no risk number** — it is a confident statement about a book that is not the book. ⚠ It would also be *indistinguishable* from a correct one on the card |
| **2** before **3** | marginal contribution is exposure-weighted | Weights that do not exist yet; the metric silently computes against equal weights |
| **4** parallel with **2** | ★ **RK-33** | ⚠ **The flags read the BOOK, not the aggregation.** M-3 needs position history and cost basis; M-4 needs account type and holding period. **Neither needs sector or theme exposure**, and sequencing them after it invents a dependency that would then be maintained |
| **5** after **3** | `D` is drawdown (RK-21, from D-11's book alone); `P` needs the metrics | D-06 receives a factor computed from an incomplete measure |
| **6** after **all** | ★★ **RK-30** | **A partial pass emitting a partial alert set reads as an all-clear on everything absent.** Silence from a risk desk is a claim |
| **7** last | contracts are published complete | A consumer reading a half-written `BookRisk` cannot tell it is half-written |

| ID | Rule |
|---|---|
| **RK-29** | ★★ **D-05 never computes on an unreconciled book. It refuses, loudly** (P5, DC-3). ⚠ The tempting alternative — compute on the last good book — is worse: it produces a correct-looking risk report **about yesterday**, and nothing on the artifact would say so |
| **RK-30** | ★★ **Alerts are emitted only from a complete pass.** A step that failed means **no alerts are emitted at all** and the failure is surfaced instead. ★ **Because this domain's whole value is that silence means "nothing found"**, a partial run that emits three of five alerts has told the reader the other two categories are clear |
| **RK-31** | ★ **WF-R2 uses the SAME code path as WF-R1, on a hypothetical book.** ⚠ A candidate evaluated by different code is a different measurement, and the two would drift exactly where it matters — the comparison between "the book now" and "the book with this position". *(This is INV-4's train/inference parity argument, applied to risk.)* |
| **RK-32** | **Stress (WF-R3) is a separate cadence and is never on the daily critical path.** Scenario replay is expensive, is **labelled and never predictive** (§9), and a daily decision does not wait on it |
| **RK-33** | **Exposure and flags are independent.** Flags read the book; exposure aggregates it. Neither is an input to the other |
| **RK-34** | ★ **There is no gate step, and its absence is deliberate** (INV-026). ⚠ A reader who assumes a "risk pipeline" ends in a pass/fail will look for one; **stating that it does not exist is cheaper than having someone add it** |

## 4A.3 WF-R2 — candidate risk, and what D-05 is allowed to see

★ **Unlike the other two analyst seats, D-05 is NOT independent** (L0 §1.6, decided 2026-08-21). It
sees D-03's nomination and D-01's gate, because **it measures the consequence of what they propose**
and a risk desk blinded to the recommendation is measuring a book nobody is considering.

⚠ **What makes that safe is INV-026, not independence.** D-05 sees everything and decides nothing.

## 4A.4 Failure and partial state

| ID | Rule |
|---|---|
| **RK-35** | ★ **A failed step aborts the pass and publishes nothing** — no partial `BookRisk`, no stale fallback, no empty-but-valid object. Downstream sees the failure (P5, DC-3) |
| **RK-36** | ★ **`UNCHECKED` is a first-class result, distinct from "no risk found"** (`L1-data-engine.md` DE-35 applied here). ⚠ **An exposure that could not be computed must never render as zero** — zero theme exposure and unmeasured theme exposure are opposite findings and would look identical |

---

# 5. EXPOSURE — the measure that actually matters here

| ID | Rule |
|---|---|
| **RK-0** | ★ **D-05 reads `L1-recording.md` **CT-11.4 BookState** — `(account_id, date, positions[], cash_by_currency, nav_by_currency, nav_base, fx_rate_used, capital_base, reconciled, breaks[])`.** ⚠ *Added by cross-spec audit: this spec described its input in prose ("the book") and **named no contract**, so nothing tied its exposure arithmetic to a declared shape.* ★ **A `BookState` with `reconciled: "break"` is not a risk input** — measuring exposure on an unreconciled book reports a number about a book that does not exist |
| **RK-1** | Exposure is reported on **five dimensions**: name, sector, **theme**, currency, account. Any one alone understates a concentrated book |
| **RK-2** | ★ **Every threshold in L0 §8 is a reporting threshold.** `CONCENTRATION_THRESHOLD_PCT` 25, `SECTOR_MAX_PCT` 35, `THEME_REPORT_THRESHOLD_PCT` 40 — crossing one emits a **LEVEL 2 ALERT** and changes nothing else (INV-023, INV-026). The existing code already says this in words: *"tracked, not blocked — concentration is intentional"* |
| **RK-3** | Exposure aggregates **in base currency with the FX rate recorded** (M-5, FX-2), and is **unavailable rather than estimated** without one (FX-3) |
| **RK-4** | Exposure is **per account and book-wide**, both reported (D-06 PS-19). The **RESP is excluded** from fund exposure (D-11 RC-4), and its exclusion is stated |
| **RK-5** | ★ **A CDR and its underlying are one exposure.** D-11 keeps them as separate lots for valuation (RC-28) and **D-05 must aggregate them** — holding `MU` as a CDR in the RRSP and as the US stock in a TFSA is **one position in Micron**, and reporting them separately understates concentration by exactly the amount that matters |

## 5.1 ⚠ The theme taxonomy does not exist

```python
# discipline/flags.py — theme_exposure()
theme = pos.get("theme")     # ← an input field. Nothing in the repo defines it.
```

`THEME_REPORT_THRESHOLD_PCT` is **40 %**, and *"AI/semiconductor"* — the theme M-2 names as the
deliberate bet — **is defined nowhere in the repository.**

| ID | Rule |
|---|---|
| **RK-6** | ★ **The theme taxonomy is declared data, versioned, with a stated membership rule** — not a free-text field a caller supplies. A threshold on an undefined set is unenforceable, and **the one threshold M-2 explicitly calls out is the one with no definition behind it**. **QK-2** |
| **RK-7** | A position whose theme cannot be resolved is reported **`theme: unclassified`** and counted in a visible residual — never silently dropped from the aggregate, which would understate the very concentration being tracked (DE-35's shape) |
| **RK-37** | ★★ **The theme taxonomy is D-05's declared artifact (`CT-5.3`), and D-02 publishes SECTOR, not theme.** ⚠ *Added 2026-08-25 building B5, closing **QK-2**: **`L1-feature-engineering.md` §6.4 says D-02 publishes "sector and theme mappings" to D-05**, while **RK-6** makes the taxonomy a declared, versioned artifact with a membership rule. ★ **Those cannot both hold**: for D-02 to label a position's theme it must know the taxonomy, and **FE-21 forbids D-02 importing an analytical domain** — so either the taxonomy leaves D-05, or D-02 stops publishing theme.* ★ **D-02 stops.** Theme membership is *"a judgement call about what counts"* (QK-2's own words — *is `ENB` in the AI theme because it powers datacentres?*), and a judgement belongs on a seat, not on neutral ground. D-05 resolves theme from D-02's **sector** plus its own declared rule, so **no new import edge exists in either direction** |

---

# 6. ★ VaR IS NEARLY USELESS HERE — and saying so is the useful part

L0 §4.2 lists *"VaR/CVaR, correlation, stress testing"*. At this book's actual shape, most of that
measures something already known.

| The book | |
|---|---|
| Names | **6–11 per account**, heavily overlapping |
| Concentration | deliberate, in one theme (**M-2**) |
| Effective breadth | D-03 QA-43 estimates **3–5 independent clusters at n = 130** for the *universe*. A ten-name book inside one theme is closer to **1–2** |

```text
╔══════════════════════════════════════════════════════════════════╗
║  WHEN CORRELATION ACROSS THE BOOK IS NEAR 1, VaR IS A            ║
║  RESTATEMENT OF CONCENTRATION IN DIFFERENT UNITS.                ║
║                                                                  ║
║  "95% 1-day VaR is $4,100" and "you are 62% in one theme" are    ║
║  the same fact. The second is checkable, needs no distribution   ║
║  assumption, and cannot be quietly wrong.                        ║
║                                                                  ║
║  A VaR number on a ten-name single-theme book carries the        ║
║  authority of a distributional model it has no data to fit,      ║
║  and it is the classic way a concentrated book is made to look   ║
║  risk-managed.                                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **RK-8** | ★ **Concentration and drawdown are the primary risk measures for this book.** They are direct, assumption-free, and they say what a correlated book actually risks |
| **RK-9** | **VaR/CVaR, where computed, states its method, its window, its distributional assumption and its effective breadth** (QA-20's MethodEntry, QA-43's breadth). A VaR without those is a number with borrowed authority |
| **RK-10** | ★ **VaR is never the headline.** It may appear beside concentration; it may not stand in for it. **A book that reports VaR and not theme weight is reporting the derived number and hiding the direct one** |
| **RK-11** | Correlation is reported **with its estimation window and its own instability**. Correlations among semiconductor names in a drawdown converge toward 1 — a correlation matrix estimated in a calm window understates exactly when it matters |

---

# 7. THE BEHAVIOURAL FLAGS — M-3 and M-4

These are the flags the mandate explicitly asks for, and they are the part of D-05 with the clearest
justification: they detect **behaviours Victor has said he wants to curb**, not statistical states.

## 7.1 M-3 — pyramiding

| ID | Rule |
|---|---|
| **RK-12** | A buy that **raises the average cost** of a held position is flagged with before/after average cost and added exposure (INV-028). Already implemented — `flags.pyramiding_flag` |
| **RK-13** | ★ **Flagged, never blocked.** An override is **logged and visible** in D-11's journal (RC-24), never prevented (INV-028, INV-026) |
| **RK-14** | ★ **The symmetric flag exists too.** M-3's fix is *"sell less and let winners run"*, so D-05 also surfaces **premature exits** — a winner trimmed well inside its horizon. A domain that flags only scale-ins implements half the mandate and silently biases toward selling. Pairs with D-06 **PS-17** |
| **RK-39** | ★★ **The premature-exit flag reports a DISTRIBUTION against the book's own realised holding periods — it has no threshold and needs no intended horizon.** ⚠ *Added 2026-08-25 building B5, closing **QK-4**. Two problems, one answer. First, QK-4's own: **a fixed "exited inside N days" repeats the fixed-percentage mistake D-06 QS-1 rejects**. Second, and sharper: **RK-14 says "well inside its horizon" and the only artifact carrying an intended horizon is the THESIS — which `RK-28` forbids D-05 from importing.*** ★ So the flag is **self-contained**: report each exit's holding period against the distribution of the book's own completed holds, and mark the short tail. It needs no threshold, no D-01 edge and no invented horizon — ⚠ and it keeps M-3's fix honest, because *a domain that flags only scale-ins implements half the mandate and silently biases toward selling* |

## 7.2 M-4 — registered short-hold, and it is book-wide

| ID | Rule |
|---|---|
| **RK-15** | A round trip completing inside `REGISTERED_SHORT_HOLD_DAYS` (**30**) in a registered account is flagged with the holding period and the CRA rationale |
| **RK-16** | ★ **There is no exempt account.** All four accounts are registered (D-11 §5.5), so M-4 applies to the **entire book, always** — it is not a subset rule. Any design routing tactical activity to a "non-registered sleeve" is describing an account that does not exist (D-11 RC-25) |
| **RK-17** | The flag reports the **trailing count and frequency**, not only the individual trip. CRA's *carrying on a business* test weighs **pattern**; a single fast round trip is unremarkable and twenty is the finding |

> **The sample data already trips this.** D-11 §5.3 H-6 records 1-day round trips in `MU`, `INTC`
> and `SNDK` in the RRSP — the exact pattern, in a registered account, in the eight months sampled.

## 7.3 Unsuppressibility

| ID | Rule |
|---|---|
| **RK-18** | ★ **No component may suppress, downgrade, filter or defer a flag or alert** (INV-021) — not D-09's renderer, not a config flag, not a severity threshold that quietly drops the tail. **A flag that can be turned off is a flag that will be off when it matters** |
| **RK-19** | An alert the human has seen may be **acknowledged**, and the acknowledgement is recorded in D-11's journal. **Acknowledged is not suppressed** — it still renders, marked as acknowledged |

---

# 8. ★ WHAT D-06 NEEDS FROM HERE — the `P` and `D` factors

D-06 §5.1d's dynamic risk budget is `r_ceiling × E × C × P × D`. **Two of those four factors are
D-05's**, and this is the highest-value thing this domain produces.

| Factor | D-05 supplies | Status |
|---|---|---|
| **`P`** portfolio | **Marginal contribution to book risk** — how much *new* risk a candidate adds given what is already held, not its standalone volatility | computable from D-02 correlation + D-11 book |
| **`D`** drawdown | Current drawdown depth and duration against the peak | ★ **computable today** from D-11's reconciled book alone |

| ID | Rule |
|---|---|
| **RK-20** | ★ **`P` is a marginal, not a standalone, measure.** A sixth semiconductor name adds far less diversification and far more concentration than its own volatility suggests. **Standalone vol would size it as though the book were empty** |
| **RK-21** | ★ **`D` is buildable now and is the cheapest real improvement over a fixed risk budget.** It needs only D-11's reconciled book — no volatility forecast, no correlation matrix, no D-05 machinery beyond a peak tracker |
| **RK-22** | Both factors are returned **with their inputs and their `as_of`**, so D-06's decomposition (PS-33) can be read rather than trusted |
| **RK-23** | A factor that cannot be computed is returned **`unmeasured`, never estimated** (PS-34, DE-35) |
| **RK-38** | ★★ **`drawdown()` takes the SERIES of reconciled book states; the peak is DERIVED, never stored.** ⚠ *Added 2026-08-25 building B5: **AC-5.19 says `drawdown()` is "computable from D-11's book alone, with no other input"** — but `CT-11.4` is **one account on one day**, and `CT-5.1.drawdown` carries `peak` and `duration_days`, which need history. **RK-21 says "a peak tracker"** and **RK-27 forbids D-05 writing anything except its own alert and flag records** — so a persisted peak is not available to it either.* ★ The resolution needs no new contract: **`CT-11.4` is per account per DAY, so the history is the accumulation of the contract already declared**. D-05 reads the series and derives the peak each run. ⚠ **A drawdown computed from an incomplete series is `unmeasured`, not zero** (RK-36) — a book whose history begins at today's NAV is at a peak by construction, and *"no drawdown"* would be the most misleading possible reading of it |

> **RK-21 is the practical recommendation of this spec.** The full framework waits on the volatility
> forecast, RM-1 and the combine point. **`D` waits on nothing**, and a risk budget that shrinks in
> a drawdown is already meaningfully better than a constant.

---

# 9. STRESS TESTING

| ID | Rule |
|---|---|
| **RK-24** | A stress scenario states its **historical source or its explicit assumption**, and is labelled **not a prediction** (INV-010's spirit) |
| **RK-25** | Scenarios are **deterministic and reproducible** given the book and the scenario definition (INV-2) |
| **RK-26** | ★ The most informative stress for **this** book is a **single-theme shock**, not a market shock. A 2022-style semiconductor drawdown is the scenario M-2's concentration actually exposes; a broad-market scenario mostly restates beta |

---

# 10. CONTRACTS

> **ID-collision notice.** `AC-5.k` / `CT-5.k` key `n` on **D-05**. **`F5` is reserved** in
> `vision.md` §4 (*execution & order support*) — latent, like D-07/F7 (L0 §16.4). Qualify anyway.

## CT-5.1 — BookRisk (JSON)

```json
{
  "as_of": "2026-08-18", "base_currency": "CAD",
  "exposure": {
    "by_theme": {"ai_semiconductor": 61.7, "unclassified": 8.3},
    "by_sector": {"Information Technology": 74.0},
    "by_currency": {"CAD": 62.1, "USD": 37.9},
    "by_account": {"TFSA_1": 31.0, "TFSA_2": 40.2, "RRSP_1": 28.8},
    "resp_excluded": true
  },
  "thresholds_crossed": [
    {"name": "THEME_REPORT_THRESHOLD_PCT", "limit": 40.0, "value": 61.7,
     "effect": "reported_only", "alert_level": 2}
  ],
  "drawdown": {"peak": 100.0, "current": 88.4, "depth_pct": 11.6, "duration_days": 23},
  "var": null,
  "var_omitted_reason": "effective breadth ~1-2; concentration is the direct measure (RK-10)",
  "factors_for_d06": {"D": {"value": 0.85, "source": "drawdown"},
                      "P": {"status": "unmeasured", "why": "correlation window insufficient"}}
}
```

`effect: "reported_only"` is on **every** threshold — there is no other value (INV-026). `var: null`
with a stated reason is a legitimate outcome (RK-10).

## CT-5.3 — ★ ThemeTaxonomy (declared data, versioned) — RK-6, RK-37

★ **The artifact `THEME_REPORT_THRESHOLD_PCT` is measured against.** ⚠ *A
threshold on an undefined set is unenforceable, and the one threshold M-2
explicitly calls out is the one with no definition behind it* (§5.1).

```json
{
  "taxonomy_version": "themes.v1",
  "membership_rule": "A position is in a theme when its D-02 sector is in the
                      theme's `sectors` AND its ticker is not in `excluded`, OR
                      its ticker is in `included`. Ticker lists are the JUDGEMENT
                      and are reviewed as such; the sector rule is the mechanism.",
  "themes": [
    {"theme_id": "ai_semiconductor", "sectors": ["Information Technology"],
     "included": ["NVDA", "MU", "AMD", "AVGO", "TSM", "ASML", "INTC", "SNDK"],
     "excluded": ["ORCL"]}
  ]
}
```

| Field | Rule |
|---|---|
| `taxonomy_version` | bumped on **any** membership change — ★ adding a ticker to a theme is an analytical change, exactly as adding a column to the sector file is (D-01 RA-100's argument, one domain over) |
| `membership_rule` | **required and non-empty.** ⚠ RK-6: *declared data with a stated membership rule, not a free-text field a caller supplies* |
| `included` / `excluded` | ★ **the judgement, isolated and named.** *Is `ENB` in the AI theme because it powers datacentres?* is a question a reader must be able to see answered, not infer from an aggregate |
| a position matching none | **`unclassified`**, counted in a visible residual (RK-7) — never dropped |

## CT-5.2 — Flag (JSON, append-only)

`(flag_id, kind ∈ {pyramiding, premature_exit, registered_short_hold}, ticker, account, as_of,
detail{}, trailing_count, acknowledged_at | null, suppressed: false)`

★ **`suppressed` is a constant `false`.** It is present so the contract states that no other value
exists (RK-18).

---

# 11. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `book_risk(as_of)` | `BookRisk` | exposure, drawdown, thresholds |
| `exposure(dimension, as_of)` | `ExposureView` | name · sector · theme · currency · account |
| `drawdown(as_of)` | `DrawdownState` | ★ the `D` factor — needs only D-11 |
| `marginal_risk(candidate, as_of)` | `MarginalRisk \| Unmeasured` | ★ the `P` factor |
| `flags(window)` | `list[Flag]` | never filtered by severity (RK-18) |
| `acknowledge(flag_id)` | `Flag` | records; **does not suppress** (RK-19) |
| `stress(scenario, as_of)` | `StressResult` | labelled not-a-prediction |

---

# 12. BUSINESS RULES

| ID | Rule |
|---|---|
| **RK-1…RK-7** | Exposure — §5 |
| **RK-8…RK-11** | Why VaR is not the headline — §6 |
| **RK-12…RK-19** | Behavioural flags & unsuppressibility — §7 |
| **RK-20…RK-23** | The `P` and `D` factors — §8 |
| **RK-24…RK-26** | Stress — §9 |
| **RK-27** | D-05 **blocks nothing, sizes nothing, and writes nothing** except its own alert/flag records |
| **RK-28** | D-05 imports no LLM gateway (AP-5, ST-5), no D-01 output, and not D-08 (L0 §4.3) |

---

# 13. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `RSK.EXPOSURE.NO_BOOK` | ERROR | no reconciled book at `as_of` (D-11 RC-10) |
| `RSK.EXPOSURE.FX_UNAVAILABLE` | ERROR | cross-currency aggregate with no rate — unavailable, never estimated (FX-3) |
| `RSK.THEME.UNRESOLVED` | WARNING | position with no theme — counted as `unclassified`, never dropped (RK-7) |
| `RSK.THEME.NO_TAXONOMY` | ERROR | theme threshold evaluated with no declared taxonomy (RK-6) |
| `RSK.CDR.NOT_AGGREGATED` | ERROR | a CDR and its underlying counted as two exposures (RK-5) |
| `RSK.VAR.UNSTATED_METHOD` | ERROR | VaR without method, window, assumption and effective breadth (RK-9) |
| `RSK.FLAG.SUPPRESSION_ATTEMPTED` | ERROR | any component tried to filter, defer or silence a flag (RK-18, INV-021) |
| `RSK.FACTOR.UNMEASURED` | *(not an error)* | `P` or `D` unavailable — **a value, not a failure** (RK-23) |
| `RSK.BLOCK.ATTEMPTED` | ERROR | a caller asked D-05 to veto, refuse or downgrade (INV-026) |

---

# 14. ACCEPTANCE CRITERIA

```text
EXPOSURE  (§5)
□ AC-5.1   Exposure is reported on all five dimensions
□ AC-5.2   Every threshold crossing carries effect="reported_only" (INV-026)
□ AC-5.3   A CDR and its underlying aggregate to ONE exposure (RK-5)
□ AC-5.4   Cross-currency aggregation with no FX rate is unavailable (FX-3)
□ AC-5.5   RESP exclusion is stated, not assumed
□ AC-5.6   A theme threshold with no declared taxonomy raises (RK-6)
□ AC-5.7   An unclassifiable theme is counted as `unclassified`, never dropped (RK-7)
□ AC-5.6a  ★ The taxonomy is versioned and states its membership rule; D-05 resolves
           theme from D-02's SECTOR, and D-02 publishes no theme (RK-37, FE-21)

MEASUREMENT  (§6)
□ AC-5.8   Concentration and drawdown are present whenever risk is reported
□ AC-5.9   VaR, if present, states method, window, assumption and effective breadth
□ AC-5.10  An artifact reporting VaR without concentration fails (RK-10)
□ AC-5.11  Correlation is reported with its estimation window

FLAGS  (§7)
□ AC-5.12  A buy raising average cost is flagged with before/after (M-3)
□ AC-5.13  A premature exit is flagged — the symmetric case (RK-14)
□ AC-5.13a ★ The premature-exit flag reports a distribution against the book's own
           realised holds — no threshold, no intended horizon, no D-01 edge (RK-39)
□ AC-5.14  A round trip under 30 days in a registered account is flagged (M-4)
□ AC-5.15  M-4 has no exempt account population (RK-16)
□ AC-5.16  The flag reports trailing count and frequency, not just the instance
□ AC-5.17  Any attempt to suppress, filter or defer a flag raises (INV-021)
□ AC-5.18  Acknowledging a flag records it and does NOT stop it rendering (RK-19)

FACTORS FOR D-06  (§8)
□ AC-5.19  drawdown() is computable from D-11's book alone, with no other input
□ AC-5.20  marginal_risk() is marginal, not standalone (RK-20)
□ AC-5.21  An uncomputable factor returns Unmeasured, never an estimate (RK-23)
□ AC-5.19a ★ drawdown() reads the SERIES of book states and derives the peak;
           an incomplete series is unmeasured, never zero drawdown (RK-38)

BOUNDARY
□ AC-5.22  A request to veto, refuse or downgrade raises (INV-026, RK-27)
□ AC-5.23  src/risk imports no LLM gateway, no D-01, and not D-08
```

---

# 15. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QK-1** | ⚠ **L0 §4.2's D-05 entry still claims sizing.** | One-line fix — text stranded from v0.5.0 when Portfolio Strategy was deleted; v0.6.0 restored D-06 and never removed it. **Sizing is D-06's** |
| ~~**QK-2**~~ | ~~★ **What is the theme taxonomy?**~~ ✅ **CLOSED 2026-08-25 — `CT-5.3`, RK-37.** | `THEME_REPORT_THRESHOLD_PCT` is 40 % and *"AI/semiconductor"* is defined nowhere. **The one threshold M-2 explicitly names has no definition behind it.** Needs a declared, versioned membership rule — and it is a judgement call about what counts (is `ENB` in the AI theme because it powers datacentres?) |
| **QK-3** | Does D-05 own **effective breadth** as a reported number? | D-03 QA-43 requires it for power calculations; D-05 needs it for RK-9. **Same quantity, two consumers** — it should have one home, and D-05 is the one with the book |
| ~~**QK-4**~~ | ~~Should the **premature-exit flag** have a threshold?~~ ✅ **CLOSED 2026-08-25 — the distribution, RK-39.** ★ *And for a second reason QK-4 did not state: the only artifact carrying an intended horizon is the thesis, which RK-28 forbids D-05 to import.* | A fixed "exited inside N days" repeats the fixed-percentage mistake D-06 QS-1 rejects. Reporting the holding-period distribution against the intended horizon may be the honest form |
| ~~**QK-5**~~ | ~~Where does the verdict gate land?~~ | ✅ **CLOSED — `D-12 Decision`.** D-05 is **not** the gate: INV-026 gives it zero blocking authority, so it could never have been (§1.4). D-05's alerts travel **beside** the recommendation (`L2` CB-11) |
| **QK-6** | Is a **single-theme stress** (RK-26) parameterised from history, or stated? | A 2022-style semiconductor drawdown is the obvious candidate. Needs a MethodEntry either way (QA-20) |

---

# 16. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-05, §3.1 LEVEL 2, **INV-021, INV-023, INV-024, INV-026, INV-028**, §8 | authority, the unsuppressible/never-blocking pair, the reporting thresholds |
| `L1-portfolio-strategy.md` **§5.1d**, PS-17, PS-19 | the `P` and `D` factors §8 supplies; the hold alternative RK-14 pairs with |
| `L1-recording.md` **§5.5**, RC-4, RC-24, RC-28 | all accounts registered ⇒ M-4 is book-wide; RESP exclusion; the journal; CDR lots RK-5 must aggregate |
| `L1-quantitative-analysis.md` **QA-43**, QA-20 | effective breadth (QK-3); the MethodEntry every metric needs |
| `L1-reporting.md` **RP-1**, and INV-021 | how alerts render; **and that D-09 may never suppress them** |
| `sdd/specs/constitution.md` P5, INV-2 | fail-loud; deterministic stress |
| `sdd/specs/F2_portfolio_and_delivery/spec.md` | prior art — `discipline/{risk,flags,context}.py`, 8/8 ACs green *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
