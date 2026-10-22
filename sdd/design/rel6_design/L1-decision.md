# L1: Domain Specification — Decision (D-12)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-12 · **Seat:** SEAT-5
> **Path:** `src/decision/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Design basis:** [`L2-signal-combination.md`](L2-signal-combination.md) — **closes its QB-5**
> **Authority:** **LEVEL 1 RECOMMEND** (L0 §3.1) · **no agent, no LLM** (P2, AP-5)
> **Prior art:** `pipeline/discipline/gate.py` (141 LOC) · `pipeline/core/signal_engine.py` (~280 LOC)
> **Binding:** **P3** · **INV-014** · **INV-026** · **INV-6** · constitution **INV-2** · **P5**/**DC-3**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.10.0 | 2026-08-26 | Victor | ★★ **DN-39 — `actionable: true` now requires a COMPLETE risk pass AND a stability figure.** ⚠ `compose` took `actionable` as a **caller argument and checked neither**, so a card could claim actionability while `alerts_status` read `UNCHECKED` — the all-clear D-05 **RK-30** exists to prevent. ★ Not D-05 blocking (INV-026 stands): **D-12 declining to call something actionable when a declared input never ran.** AC-12.29 added. |
| 0.9.0 | 2026-08-23 | Victor | ⚠ **B3 readiness — `alerts[]` had no status channel.** D-05 **RK-30** emits alerts only from a *complete* pass and **RK-36** makes `UNCHECKED` first-class, but `CT-12.1` could express neither: **a risk desk that correctly refused to run looked exactly like one that ran and found nothing.** ★ **New DN-38 + `alerts_status`** — `COMPLETE` or `UNCHECKED: <why>`, mirroring D-07 DE-35. AC-12.28 added. **Found building the B3 walking skeleton**, where D-11's book does not exist yet and D-05 must refuse (RK-29). |
| 0.8.0 | 2026-08-18 | Victor | ✅ **QN-5 closed — DN-35…37.** A vetoed candidate is scored at **exactly `T+h`**, same horizon and anchor, **no early close and no extension** — *a counterfactual whose window can be chosen after the fact measures the chooser*. Delisted/halted names are `terminated`, never dropped (survivorship). ★ **DN-37 is the one that costs something: overlapping windows make the observations autocorrelated, so §6.3's 3.5–11× gap assumed independence and is OPTIMISTIC.** |
| 0.7.0 | 2026-08-18 | Victor | ⚠ **Seam audit: `CT-12.1.candidate` mirrored a contract this spec never named.** **DN-34** names **CT-3.4 Nomination**, and states the two properties D-12 depends on: `candidates` is a **list** (so `k_cov ≥ 2` is expressible) and a Nomination carrying `h1q` is **rejected, not ignored**. |
| 0.6.0 | 2026-08-18 | Victor | The superset check (DN-32) still showed `verdict` dropped — **the ANALYST's own verdict, distinct from `verdict.final`** — now carried in the grade block. ★ **And chasing it found a second gap: nothing carried the thesis NARRATIVE to D-09.** New **DN-33** + `thesis_ref`: the narrative is **referenced by resolvable key, never copied**, because copying puts the same prose under two contracts and the rendered one would be whichever was written last. |
| 0.5.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit found the transported grade dropping three fields** — `k`, `verdict_distribution` and `confidence` — **each required by RA-20 or RA-21 for the artifact to render.** That is precisely the loss **DN-25 exists to prevent**, reintroduced by the contract example. New **DN-32**: transport is **complete, not selective** — `CT-12.1.grade` is a superset of `CT-1.4`'s, and **a field dropped in transport is indistinguishable downstream from one the producer never emitted.** AC-12.23/23a make it checkable. |
| 0.4.0 | 2026-08-18 | Victor | ⚠ **Consistency audit: DN-16/17/18 restored (§6.3b).** They were defined in v0.1.0, cited **five times** since — including by `AC-12.19` and the `veto_rate()` API row — and **silently dropped when §6 was rewritten in v0.2.0**. A rewrite that replaces a block must carry its rule definitions forward; this one did not. |
| 0.3.0 | 2026-08-18 | Victor | ★ **The thesis gate's `status` now has a source.** CT-12.1 showed `{"gate_id":"thesis","status":"VETO"}` with nothing producing it; **D-01 CT-1.4 `GateVerdict`** now does, and **DN-31** states the general rule — statuses are **consumed, never derived**, because deriving one is origination (DN-1) and needs policy D-12 may not hold (DN-2). The `scorecard` example is replaced with D-01 §8.1's **four fixed dimensions** (it had been invented). |
| 0.2.0 | 2026-08-18 | Victor | **External review incorporated; three corrections, one of them to a headline.** ★ **§6.2/§6.3 were wrong by 5×** — annual uplift was computed per-decision without the **1/N sleeve weight**, and `σ` disagreed with D-03 §9.1.6a. The gap between *useful* and *provable* is **3.5–11× at three years, not 20–37×**, and falls to ~2× at ten years. **§5.0 reframes the whole justification**: the meet is chosen because it is a **zero-parameter rule** (forecast-combination puzzle; DeMiguel et al.), not because of order-theoretic elegance — the statistical argument survives a reader who dislikes lattices and the implementation argument does not. New: **§5.0a** estimation-vs-feasibility, **§5.4a** the long-only precondition, **§5.8** grade transport (DN-25/26), **§6.3a** measure `ρ` instead (DN-27/28), **§6.6** liveness (DN-29), **§6.7** the priced trade-off (DN-30). **QN-1's reasoning about `ADD` was wrong and is corrected.** |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. §1.4 argues the seat from **the same structural reason that put D-02 in SEAT-5**. §5 is the substance: the verdict algebra is a **bounded meet-semilattice**, which makes P3 a **type-level guarantee rather than a runtime check** and yields **five property tests**. §5.4 derives a non-obvious consequence — **a gate cannot veto a SELL**. §5.5 states P5 algebraically: *the identity element must not be reachable by omission*. §6 shows the gate is **economically useful ~20–37× before it is statistically provable**, so it must be justified on process, not P&L. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"Three domains have spoken. What is the one thing the human is shown — and why?"**

D-12 is the **composition layer**. It takes D-03's nomination, D-01's gate and D-05's alerts, and
produces exactly one artifact-ready `Recommendation` with a complete audit trail.

★ **It originates nothing.** Every verdict it emits was emitted by someone else first; D-12's only
freedom is to make one *more conservative* (P3). That is not a restriction added for safety — §5
shows it is the algebraic structure of the composition itself.

## 1.2 Why a domain exists at all — closing QB-5

`L2-signal-combination.md` QB-5 found that the combination step **had no home**:

| Candidate | Why not |
|---|---|
| `src/quant/` (D-03) | would make seat 3 the owner of a step that consumes seat 2's output — reads as seat 3 adjudicating seat 2 |
| `src/fundamental/` (D-01) | the mirror problem, and D-01 is the only LLM-bearing domain (AP-5) — composition must be deterministic |
| `src/risk/` (D-05) | D-05 has **zero authority** (INV-026). A domain that may never block cannot own the step that blocks |
| `src/reporting/` (D-09) | ★ **the dangerous one.** D-09 may render a verdict but **never originate or escalate one** (DC-5). Putting composition there is how a renderer starts deciding |
| `src/orchestration/` (D-08) | forbidden outright — orchestration invokes, never computes (L0 §4.3, OR-1) |

**Every existing domain is the wrong home for a specific, stated reason.** That is what a missing
domain looks like.

## 1.3 Position

```text
   D-03 quant ──► nomination ──┐
   D-01 research ──► gate ─────┤
   D-05 risk ──► alerts ───────┤
                               ▼
        ┌──────────────────────────────────────────────┐
        │  D-12 DECISION          SEAT-5 · LEVEL 1     │
        │  compose · attribute · never originate       │
        └──────────────────┬───────────────────────────┘
                           │ Recommendation (CT-12.1)
              ┌────────────┴────────────┐
              ▼                         ▼
        D-09 renders            D-11 records
                                (incl. ★ vetoed candidates — §6.4)
```

## 1.4 ★ Why SEAT-5 — the same argument that placed D-02

`L4-coding-standards.md` §1.2 records: *"D-02 belongs to SEAT-5 — and that is what keeps INV-014
intact,"* because a **neutral third-party computation layer** means neither analyst seat consumes
the other's output.

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-02 IS THE NEUTRAL LAYER UPSTREAM OF BOTH ANALYST SEATS.       ║
║  D-12 IS THE NEUTRAL LAYER DOWNSTREAM OF BOTH.                   ║
║                                                                  ║
║  They are the same structural device applied at the two ends of  ║
║  the pipeline, and they belong to the same seat for the same     ║
║  reason: if either analyst seat owned it, that seat's conclusion ║
║  would be privileged by construction.                            ║
║                                                                  ║
║  SEAT-1 is excluded for a stronger reason. Seat 1 is the HUMAN.  ║
║  "The fund manager is not a separate component to be built"      ║
║  (L0 §1.6). A D-12 in seat 1 would be the AI holding PM          ║
║  authority, which is the one thing the whole design refuses.     ║
╚══════════════════════════════════════════════════════════════════╝
```

SEAT-5 already hosts a LEVEL 1 domain (D-09), so the authority level is not novel. D-12 differs from
its seat-mates in having **no agent** — composition is arithmetic on a finite lattice.

## 1.5 Boundary

```text
  IN SCOPE                          OUT OF SCOPE
  ✓ compose verdicts (P3-monotone)  ✗ produce a ranking          -> D-03
  ✓ attribute every downgrade       ✗ author a thesis            -> D-01
  ✓ assemble the Recommendation     ✗ compute exposure or risk   -> D-05
  ✓ record vetoed counterfactuals   ✗ size a position            -> D-06
  ✓ enforce INV-6 (one actionable)  ✗ render or deliver          -> D-09
                                    ✗ ORIGINATE any verdict      -> nobody
```

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **Nomination** | candidate × as_of | `(ticker, as_of)` | D-03's rank + ranked quantity |
| **GateVerdict** | gate × candidate | `(gate_id, ticker, as_of)` | `PASS / FLAG / VETO` + reason |
| **Recommendation** | one per run | `(as_of, run_id)` | ★ the single artifact-ready output |
| **Attribution** | recommendation | `run_id` | ★ **every** binding gate, not the first (§5.6) |
| **VetoedCandidate** | candidate × as_of | `(ticker, as_of)` | ★ the counterfactual record (§6.4) |

---

# 3. DEPENDENCIES

```text
ALLOWED
  D-03, D-01, D-05  ──► D-12          (D-12 reads all three)
  D-12 ──► D-09  (renders)  ·  D-12 ──► D-11  (records)

FORBIDDEN
  ✗ D-12 ──► D-01 or D-03            ★ NEW EDGE — see DN-3
  ✗ D-12 ──► the LLM gateway         (P2, AP-5, ST-5)
  ✗ D-09 ──► D-12 as an originator   (DC-5: render, never decide)
  ✗ D-12 ──► D-06                    sizing is not composition
```

| ID | Rule |
|---|---|
| **DN-1** | ★ **D-12 originates no verdict.** Every verdict it emits is traceable to an input verdict. A `Recommendation` whose verdict appears in no input is a defect, and it is checkable |
| **DN-34** | ★ **The nomination D-12 composes is `L1-quantitative-analysis.md` **CT-3.4 Nomination**** — `candidates[]`, `nominating_horizon`, `universe_n`, `model_artifact_id`, `decision_anchor`. ⚠ *Added by seam audit: `CT-12.1.candidate` mirrored fields from a contract this spec never named.* ★ **`candidates` is a list** (QA-122), which is what makes `k_cov ≥ 2` expressible; **`nominating_horizon` must be `h1m`** and a Nomination carrying `h1q` is rejected, not ignored (QA-120) |
| **DN-2** | D-12 is **deterministic** — no LLM, no sampling, no wall-clock (P2, AP-5, INV-2) |
| **DN-3** | ★ **No feedback edge.** D-12's output must never reach D-01 or D-03, in the same run or a later one. INV-014 keeps the two seats independent *at production*; a composed verdict fed back would make each seat's next analysis depend on the other's last one — **laundering the exact dependency INV-014 forbids, through a third party and a time lag** |
| **DN-4** | D-12 imports no domain it does not read (§3), and is imported by no analytical domain |

---

# 4. MODULE DECOMPOSITION

```text
src/decision/
├── algebra/      # ★ the verdict lattice — meet, gate map, laws (§5)
├── compose/      # nomination + gates -> Recommendation
├── attribute/    # which gates bound, and why (§5.6)
├── counterfactual/  # ★ vetoed candidates, for §6's measurement
└── contracts/
```

---

# 5. ★ THE VERDICT ALGEBRA

## 5.0 ★ Why a meet — the statistical argument, which is the decisive one

> **Reframed in v0.2.0 after external review.** v0.1.0 justified the meet on order-theoretic
> grounds — *P3 becomes a type guarantee rather than a runtime check*. That is true and it is a real
> benefit, but it is an **implementation** argument: the same guarantee is available from a
> well-tested `max()`. **It would not survive a reader who dislikes lattices.** The decisive
> argument is statistical, and it is this:

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE MEET IS A ZERO-PARAMETER COMBINATION RULE.                  ║
║                                                                  ║
║  It estimates nothing. No weight, no covariance, no threshold —   ║
║  so nothing in it can be fitted to noise.                        ║
║                                                                  ║
║  At n ≈ 60 decisions/year, that is not a safety compromise. It   ║
║  is the OUT-OF-SAMPLE OPTIMUM.                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

This is the **forecast combination puzzle**, one of the most replicated results in forecasting:
optimal combination weights can be derived when variances and covariances are *known*, but when
they must be **estimated**, the equally-weighted (or otherwise parameter-free) combination
routinely wins out of sample. The mechanism — Smith & Wallis (2009), Claeskens et al. (2016) — is
that optimality is derived assuming **fixed** weights; once the weights are random, the combination
acquires a bias even when its components are unbiased, and its variance exceeds the fixed-weight
case. The penalty for fitting is therefore **not merely "no gain" but active harm**.

Its twin in portfolio construction is DeMiguel, Garlappi & Uppal (2009): naïve `1/N` beats
mean–variance optimisation out of sample, for the same reason and at realistic sample sizes.

> ★ **Put that beside §6.** At n ≈ 60/yr this system cannot estimate the pass/veto spread; it
> certainly cannot estimate a covariance between D-01 and D-03. **Any fitted combination weight
> here is fitted to noise**, and the literature says fitting it makes things worse rather than
> neutral. The meet is parameter-free by construction, which is exactly the class of rule this
> regime rewards.

**The order-theoretic properties (§5.1–§5.7) remain, and remain valuable** — they are what make the
rule *checkable*. They are the second argument, not the first.

## 5.0a ★ Two problems, not one — and the meet answers only one

The three inputs are not the same kind of object (§3), and the distinction has a name:

```text
   ESTIMATION    μ̂ = f(x_D01, x_D03)     two noisy estimators of ONE latent
                                          quantity — the forward excess return.
                                          Optimal mathematics: weights, covariance, Bayes.

   FEASIBILITY   A* = A ∩ constraints     which actions are permissible.
                                          Optimal mathematics: lattices, meets, monotonicity.
```

★ **D-12 deliberately routes D-01 through the feasibility path.** D-01 emits `PASS/FLAG/VETO`
rather than a return estimate, so a second estimator of the same quantity is being spent as a
constraint. **That is a choice, and §6.5 prices it.**

---

This section exists so that **P3 is checkable, and an upgrade is not merely forbidden but
inexpressible.** Everything below is testable, and §5.2 lists the tests.

## 5.1 The lattice

Verdicts form a **totally ordered set (a chain)** under *aggressiveness*. Define the conservatism
index `c`:

```text
        c(BUY) = 0   <   c(HOLD) = 1   <   c(SELL) = 2
                    increasingly conservative  ──►

        v₁ ⊑ v₂   ⟺   c(v₁) ≥ c(v₂)          "v₁ is no more aggressive than v₂"
```

Composition of `k` gate outputs is the **meet** (greatest lower bound) in this order:

```text
        v*  =  ⊓ᵢ vᵢ  =  argmax_i  c(vᵢ)      — the LEAST aggressive input wins
```

`(V, ⊓)` is a **bounded meet-semilattice** with identity `⊤ = BUY` and absorbing element
`⊥ = SELL`. (Standard order theory — Davey & Priestley, *Introduction to Lattices and Order*, §2.)

## 5.2 ★ The five laws — and the five tests

| Law | Statement | Why it matters here |
|---|---|---|
| **Idempotence** | `v ⊓ v = v` | re-running a gate cannot compound its effect |
| **Commutativity** | `v₁ ⊓ v₂ = v₂ ⊓ v₁` | ★ **gate evaluation order cannot change the outcome** |
| **Associativity** | `(v₁ ⊓ v₂) ⊓ v₃ = v₁ ⊓ (v₂ ⊓ v₃)` | grouping/batching gates is safe |
| **Identity** | `v ⊓ BUY = v` | a passing gate is a no-op |
| **Absorption** | `v ⊓ SELL = SELL` | ★ once conservative, never recovered — monotone by construction |

```text
╔══════════════════════════════════════════════════════════════════╗
║  P3 IS NOT ENFORCED HERE. IT IS IMPLIED.                         ║
║                                                                  ║
║      v*  =  ⊓ᵢ vᵢ   ⟹   v* ⊑ vⱼ   for every j                   ║
║                                                                  ║
║  The meet is a lower bound BY DEFINITION, so the composition     ║
║  cannot be more aggressive than any input. There is no branch    ║
║  to forget, no assertion to omit, no code path where an upgrade  ║
║  is expressible.                                                 ║
║                                                                  ║
║  Compare gate.py's current _SEVERITY dict + max(): the same      ║
║  arithmetic, but written as an imperative escalation that a      ║
║  future edit could invert. Same answer today; different          ║
║  guarantee.                                                      ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **DN-5** | ★ Composition is the **meet**. It is implemented once, in `algebra/`, and every gate composes through it |
| **DN-6** | ★ **All five laws are property tests** (constitution §4, invariant/property tier), exhaustive over `V^k` for `k ≤ 3` — the domain is 3 elements, so exhaustive testing is free and there is no excuse for sampling |

## 5.3 Applying a gate: the map φ

Gate *statuses* and *verdicts* are different types. A gate emits a status; the algebra needs a
verdict. The bridge is a **monotone map** `φ : V × S → V`:

```text
        S = { PASS  ⊏  FLAG  ⊏  VETO }        gate severity, also a chain

        φ(v, PASS) = v                        identity
        φ(v, FLAG) = v                        ★ verdict unchanged — see DN-8
        φ(v, VETO) = v ⊓ HOLD                 refuse to act; do not instruct
```

| ID | Rule |
|---|---|
| **DN-7** | ★ `φ` is **monotone in both arguments**: more severe status ⇒ no more aggressive verdict; more conservative input verdict ⇒ no more aggressive output. Testable exhaustively (3×3 = 9 cases) |
| **DN-8** | ★ **`FLAG` does not move the verdict, and must therefore change the artifact** — closing `L2` **QB-1**. A severity level that alters nothing anywhere trains the reader to skip it, which is worse than not having it. FLAG's obligation is to D-09, not to the algebra |
| **DN-9** | ★ **`VETO` maps to `HOLD`, never to `SELL`.** A veto is *"do not act on this"*, not *"take the opposite side"*. Mapping a vetoed BUY to SELL would have the discipline layer originating a trade instruction — DN-1's exact prohibition |

## 5.4 ★ A gate cannot veto a SELL — a consequence, not a choice

Apply DN-9 to `v = SELL`:

```text
        φ(SELL, VETO)  =  SELL ⊓ HOLD  =  SELL          (absorption)
```

The veto has **no effect**. And it cannot: `SELL → HOLD` is an *upgrade* in aggressiveness, which
P3 forbids outright.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE DISCIPLINE LAYER CAN STOP YOU BUYING. IT CANNOT STOP YOU    ║
║  SELLING.                                                        ║
║                                                                  ║
║  This falls out of P3 with no additional assumption, and it is   ║
║  the right asymmetry: a system that could block an exit would    ║
║  be holding a position against its owner's instruction.          ║
║                                                                  ║
║  It also explains why D-05's premature-exit flag (RK-14) is a    ║
║  FLAG and not a VETO. Not a scoping compromise — a VETO there    ║
║  would be algebraically inert. The mandate's "sell less, let     ║
║  winners run" (M-3) is reachable only by persuasion, and the     ║
║  artifact is the only instrument that has.                       ║
╚══════════════════════════════════════════════════════════════════╝
```

## 5.5 ★ P5, stated algebraically

`⊤ = BUY` is the identity: `v ⊓ BUY = v`. So a gate that returns the identity is invisible.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE IDENTITY ELEMENT MUST NOT BE REACHABLE BY OMISSION.         ║
║                                                                  ║
║  If a missing gate input is treated as PASS, the meet is         ║
║  unchanged and the recommendation goes out ungated — looking      ║
║  exactly like one that passed.                                    ║
║                                                                  ║
║  Both real incidents in this repo are this bug: a discipline     ║
║  card built from a FAILED and from an ABSENT LLM narrative,      ║
║  emailed as genuine recommendations with no stop and no targets. ║
║  In this algebra they are the same defect, and it has a name.    ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5.4a ⚠ The chain has an unstated precondition

`c(BUY) = 0 < c(HOLD) = 1 < c(SELL) = 2` is an ordering **only for a name currently held.**

| | BUY | HOLD | SELL |
|---|---|---|---|
| **held** | adds exposure | keeps it | exits to cash — *least* risk ✓ chain holds |
| **not held** | takes risk | takes none | ★ **short** — *more* aggressive than HOLD ✗ **chain inverts** |

| ID | Rule |
|---|---|
| **DN-24** | ★ **The conservatism chain presumes a long-only book and presumes `SELL` is emitted only for currently-held positions.** Under a long-short mandate, `SELL` on an unheld name is an *escalation*, not a downgrade, and §5's ordering does not hold. ★ **Here the precondition is guaranteed rather than assumed: all four accounts are registered** (D-11 §5.5), and **CRA rules prohibit short selling in a registered account** — so the inversion is legally unreachable, not merely out of scope. Stated anyway, because it is a precondition of the *algebra* that would silently fail if a margin account were ever added |

| ID | Rule |
|---|---|
| **DN-10** | ★ **A missing gate input raises. It is never the identity.** `NO_THESIS` is a distinct state, not `PASS` (`L2` CB-17) |
| **DN-11** | ★ **Every gate declared for a run must report**, and the set of expected gates is **declared before the run, not inferred from what answered**. Inferring the roster from responders makes a silently-absent gate structurally undetectable |
| **DN-12** | A gate that errors is `UNAVAILABLE` — neither PASS nor VETO — and the run **produces no actionable recommendation** (P5, DC-3). D-09 renders the absence |

## 5.6 Attribution — all binding gates, not the first

With a meet, several gates can be simultaneously binding (`c(vᵢ) = c(v*)`).

| ID | Rule |
|---|---|
| **DN-13** | ★ The `Attribution` records **every** gate at the binding level, not the first encountered. Reporting one of three makes the other two invisible, and the reader fixes a third of the problem believing they fixed it |
| **DN-14** | Attribution is **order-independent** — guaranteed by DN-6's commutativity test, not asserted separately |

## 5.7 ★ QB-2 dissolves — there is no deadlock

`L2` QB-2 asked how D-03's h1w timing leg and D-01's gate compose when one says *"wait"* and the
other *"act now"*.

**They cannot conflict.** Both are meets into the same chain; meet is commutative and associative
(DN-6), so the composition is `v* = v_h1w ⊓ v_thesis` regardless of order, and *"wait"* is simply
more conservative. **A precedence rule is unnecessary** — the question presupposed a conflict the
algebra does not admit.

| ID | Rule |
|---|---|
| **DN-15** | ★ **Any number of delay/veto authorities compose without precedence.** Adding a gate later requires no change to the composition — which is the practical payoff of choosing an algebraic structure over an `if`-chain |

## 5.8 ★ The meet is lossy — so D-12 must TRANSPORT what it does not consume

A meet discards everything except the ordering. It throws away D-03's rank magnitude, D-01's
conviction, **RM-1's k-run stability fraction**, and the per-dimension scorecard.

**Discarding them for the *verdict* is correct** — the go/no-go is binary and graded information has
nowhere to go inside it. But §1.5 forbids `D-12 → D-06`, and if D-12 is the sole consumer of D-01
and D-03 output, **the graded information dies here.** D-06 would then size on nothing, or read
D-01/D-03 directly — reintroducing precisely the unmediated cross-seat coupling the architecture
exists to avoid.

That would also break a rule already on the books: **RA-20** calls publishing the k-run variance
*"the single most effective anti-overconfidence device available"* and says a reader seeing 3/5
**should size differently**. Impossible if the number cannot reach D-09 or D-06.

| ID | Rule |
|---|---|
| **DN-31** | ★ **Gate statuses are consumed, never derived.** D-12 receives `PASS/FLAG/VETO` from the owning domain — for the thesis gate that is **D-01 `CT-1.4 GateVerdict`** (D-01 §11.1). **Deriving a status inside D-12 would be originating a verdict** (DN-1) and would require analytical policy D-12 has no standing to hold (DN-2). A gate that supplies only raw analysis and expects D-12 to grade it is an incomplete gate |
| **DN-25** | ★ **D-12 composes the verdict and *transports* the grade.** `CT-12.1` carries every graded input as an **immutable pass-through** — `ranked_quantity`, `conviction`, `stability_fraction`, `scorecard` — each explicitly marked **`consumed_by_algebra: false`**. Sizing and rendering read the grade; the algebra does not. *"Sizing is not composition"* stays true — D-12 still sizes nothing — but the composition layer stops being a lossy bottleneck for the whole pipeline |
| **DN-33** | ★ **Narrative is REFERENCED, never copied.** `CT-12.1.thesis_ref` is a resolvable key `(ticker, thesis_version, as_of, bundle_hash)`; the thesis text, bear case, falsifiers and claims stay in **D-01 CT-1.1**. ⚠ **Copying them would put the same prose under two contracts with two versions**, and the one D-09 rendered would be whichever was written last |
| **DN-32** | ★★ **Transport is COMPLETE, not selective.** `CT-12.1.grade` is a **superset** of the producing contract's grade block (D-01 **CT-1.4**) plus D-03's rank fields. ⚠ **A field dropped in transport is indistinguishable downstream from a field the producer never emitted** — and this contract had silently dropped `k`, `verdict_distribution` and `confidence`, each of which **RA-20 or RA-21 requires the artifact to render**. Checkable: the consumer's key set contains the producer's |
| **DN-40** | ★ **`candidate.ranked_by` carries WHAT ranked the pick** — `{artifact_id, kind: rule|model, formula_id}` — passed through from D-03's `Nomination.model_artifact_id` (DN-26: byte-identical), `kind` decided by comparing it with D-03's declared rule id. ⚠ *Added 2026-10-06 (L9 §10 C4)* so D-09 can render it (RP-54) without importing D-03 |
| **DN-41** | ★★★ **A recommendation ranked by a REFUSED model is never actionable** — `compose` REFUSES `actionable=True` when the nomination's `ranker_status` is `refused_informational` (it does not trust the caller to have checked), and `ranked_by` carries the status and the failed gates byte-identical (DN-26). ★ Victor, 2026-10-09: card option (b); PG-10: an output from a model that has not passed its own gates must say so |
| **DN-42** | ★ **`thesis_ref` is carried, never derived** — the nominee's thesis reference (run id, as of, verdict, conviction, falsifiers, provenance) is passed into `compose` and onto the Recommendation VERBATIM (DN-26's rule for the nomination, applied to the thesis); D-12 composes from the GATE only (DN-1), and DN-39 is unchanged. *Added 2026-10-21 (F13 `D13`, Victor)* |
| **DN-39** | ★★ **`actionable: true` requires a COMPLETE risk pass and a verdict stability figure. Both, or the card is informational.** ⚠ *Added 2026-08-26 making the first card actionable: **`compose` took `actionable` as a caller argument and checked neither.*** A recommendation could be marked actionable while `alerts_status` read `UNCHECKED` — and D-05 **RK-30**'s whole argument is that *silence means "nothing found"*, so *a partial run has told the reader the other categories are clear.* ★ **This is not D-05 blocking** — INV-026 gives it zero authority and it still has none. It is **D-12 declining to call something actionable when a declared input never ran**, which is DN-11's rule about absent gates applied to the alert channel. ⚠ `verdict_stability: null` fails the same test (RA-20, AC-1.8, BS-28): *a verdict may not reach a human as actionable before that field exists* |
| **DN-38** | ★★ **`alerts[]` carries a companion `alerts_status`, and an empty list without one is an ALL-CLEAR the risk desk never made.** ⚠ *Added 2026-08-23 building B3.* **D-05 RK-30** emits alerts *only from a complete pass* and **RK-36** makes `UNCHECKED` a first-class result distinct from *"no risk found"* — but `CT-12.1` had no channel for either, so a D-05 that correctly refused to run (**RK-29**, no reconciled book) was indistinguishable from one that ran and found nothing. ★ **Status is `COMPLETE` or `UNCHECKED: <reason>`**, mirroring D-07 **DE-35**'s tri-state, and D-09 renders it (**RP-47**). *Because this domain's whole value is that silence means "nothing found"* — RK-30's own words — a silence D-12 cannot qualify is a claim it cannot support |
| **DN-26** | Pass-through fields are **byte-identical to their source** and are never recomputed, rescaled or rounded in transit. A transported number that differs from its origin is a second, unowned computation |

---

# 6. ★ MEASURING THE GATE — what is out of reach, and what is not

A gate that never fires is decoration; one that fires at random is noise. Both are testable.

## 6.1 The gate's value

Let `R` be the realised forward return of a nominated candidate, and partition on the gate:

```text
    E[R]  =  P(pass)·E[R|pass]  +  P(veto)·E[R|veto]

    ⟹   E[R|pass] − E[R]  =  P(veto) · ( E[R|pass] − E[R|veto] )
                              ╰──┬───╯   ╰──────────┬──────────╯
                               fires?            discriminates?
```

★ **Value = veto rate × the spread it creates.** Both factors must be non-zero, which answers
`L2` QB-3 quantitatively: the veto rate is not a free parameter to be tuned for comfort — it is
half the value term.

## 6.2 ⚠ CORRECTED — how large a spread would be useful

> ★ **v0.1.0's table was wrong by 5×, and the correction is the same defect class the rest of this
> project keeps hitting: a per-decision figure annualised without the position weight** (cf. D-03
> §5.6a's cost convention and §5.8's capital base). *Found by external review, 2026-08-18.*
>
> v0.1.0 computed annual uplift as `60 × P(veto) × spread`. **That treats every decision as
> deploying the whole book.** It deploys **one sleeve — 1/N = 20 %** (D-03 §5.8, `N = 5`). With 5
> sleeves each rolling ~12×/yr, the *book* turns over **12 times a year, not 60**:
>
> ```text
>       annual uplift  =  60 rolls × (1/5 weight) × P(veto) × spread
>                      =  12 × P(veto) × spread          ← NOT 60 ×
> ```

> ⚠ **A second correction, compounding with the first.** v0.1.0 used `σ = 13 %` for a 21-day return
> (45 % annualised). **D-03 §9.1.6a uses `sd(R₂₁) = 0.30·√(21/252) = 8.66 %`** (30 % annualised) for
> the same universe. Two specs disagreeing on the same parameter is exactly what **QA-48** exists to
> catch. **D-03's figure is adopted** — it is the 130-name balanced universe, which is what D-03
> nominates from.
>
> ★ **But it is probably a lower bound, and knowing why matters.** QA-58 ranks on the
> **denormalised** quantity `ẑ·σ̂·√h`, which multiplies by `σ̂` — so **high-volatility names are
> systematically over-represented at the top of the ranking**, and the *nominated* name's σ exceeds
> the universe average by an unmeasured amount. Both columns are shown below; the truth is between
> them and nearer the right. **QN-7.**

## 6.3 ★ CORRECTED — the gap between useful and provable

Required spread for **+1 %/yr**, and the minimum detectable spread (two-sided 95 %):

| veto rate | required spread | **σ = 8.66 %** 3 yr / 10 yr | **σ = 13 %** 3 yr / 10 yr | **ratio @3 yr** | **@10 yr** |
|---:|---:|---:|---:|---:|---:|
| 5 % | 1.67 % | 5.80 % / 3.18 % | 8.71 % / 4.77 % | 3.5–5.2× | **1.9–2.9×** |
| **10 %** | **0.83 %** | **4.22 % / 2.31 %** | 6.33 % / 3.47 % | **5.1–7.6×** | **2.8–4.2×** |
| 20 % | 0.42 % | 3.16 % / 1.73 % | 4.75 % / 2.60 % | 7.6–11.4× | 4.2–6.2× |
| 35 % | 0.24 % | 2.65 % / 1.45 % | 3.98 % / 2.18 % | 11.1–16.7× | 6.1–9.2× |

```text
╔══════════════════════════════════════════════════════════════════╗
║  RETRACTED: v0.1.0's "useful 20-37x before provable".            ║
║  CORRECTED: the gap is 3.5-11x at three years, and falls to      ║
║             roughly 2-4x at ten years.                           ║
║                                                                  ║
║  DN-16 SURVIVES AT THE THREE-YEAR HORIZON. A 3.5-11x gap still   ║
║  means P&L tuning is fitting noise.                              ║
║                                                                  ║
║  BUT IT IS GENUINELY MARGINAL AT TEN YEARS AND A LOW VETO RATE   ║
║  (1.9x at 5%), and that must be said rather than hidden behind   ║
║  the larger number. A decade of counterfactual records would be  ║
║  weak evidence — not no evidence.                                ║
║                                                                  ║
║  Which is the argument for DN-19: START RECORDING NOW. The       ║
║  measurement is out of reach for years, and only becomes         ║
║  reachable at all if the data collection began long before.      ║
╚══════════════════════════════════════════════════════════════════╝
```

> The conclusion of §6 is **unchanged in direction and weaker in magnitude**. That is the honest
> state, and the corrected number is the one that goes on the artifact.

## 6.3a ★ What IS measurable — the seat correlation

§6.3 says the gate's P&L effect is out of reach. **It does not follow that nothing is**, and the
quantity that *is* reachable is the one `L2` §4.2 showed to be decisive.

For two signals with ICs `IC₀₃`, `IC₀₁` and mutual correlation `ρ`, optimally weighted:

```text
    IC_combined = √( ic' C⁻¹ ic )        w ∝ C⁻¹ ic

    equal strength:   IC_c = ic·√( 2/(1+ρ) )     ρ=0 → 1.41×,  ρ=1 → 1.00×

    ★ with k = IC₀₁/IC₀₃ :   uplift = 1  exactly when  ρ = k
```

> ★ **D-01 adds value as a signal if and only if `IC₀₁ > ρ · IC₀₃`.** Below that the optimal weight
> on D-01 is **negative** — the algebra says to short the fundamental view, which is `L2` **CB-4**'s
> incoherent case arriving by a cleaner route.

The gate's P&L needs a difference of means across ~6 vetoes/yr. **`ρ` is a cross-sectional statistic
over every name D-01 covers**, vetoed or not:

| covered names/yr | `SE(ρ̂) ≈ 1/√(n−1)` | detects |
|---:|---:|---:|
| 240 | 0.065 | `ρ > 0.13` within a year |
| 60 | 0.130 | `ρ > 0.26` |

| ID | Rule |
|---|---|
| **DN-27** | ★ **Report the rank correlation between D-01's verdict-plus-conviction ordering and D-03's ranked quantity, over all covered names.** It is the one quantity in §6 with adequate power, and it is **the empirical content of INV-014**: `ρ ≈ 0` means the seats are genuinely independent and the theoretical uplift is near its 1.41× maximum; `ρ` high means D-01 is rediscovering what D-03 already knows and the fundamental seat is expensive decoration |
| **DN-28** | ★ **`ρ` is estimable only if D-01's coverage spans the rank distribution.** ⚠ If D-01 covers only the daily top pick, **every covered name has rank 1, the covered-sample variance of the rank is ~0, and `ρ` is not estimable at all** — severe range restriction, not merely a small sample. The rotating sample (D-01 §7.4) must therefore be **stratified across rank deciles**, and any residual restriction corrected for (Thorndike Case II) before `ρ̂` is reported |

### 6.3b ⚠ RESTORED — DN-16/17/18 (dropped by the v0.2.0 §6 rewrite)

> ⚠ **These three were defined in v0.1.0, cited five times since — including by `AC-12.19` and the
> `veto_rate()` API row — and silently deleted when §6 was rewritten.** Restored verbatim in
> substance, with the corrected magnitudes.

| ID | Rule |
|---|---|
| **DN-16** | ★ **The gate is never tuned on realised P&L.** At this breadth any such tuning fits noise: §6.3's gap between *useful* and *provable* is **3.5–11× at three years**, so the measurement is far too coarse to see the effect it nominally tests |
| **DN-17** | ★ **The veto rate is nonetheless monitored and reported every run.** A rate near 0 % or 100 % is a **structural** finding — decoration, or a ranker and an analyst that systematically disagree — and reading it needs no statistical power |
| **DN-18** | The gate's stated warrant is **process compliance** (§6.7), recorded as such, so no future reader mistakes an unmeasurable claim for an unmade one |

## 6.4 ★ Record what you rejected — and start now

Everything in §6 requires `E[R|veto]`, which requires knowing what happened to names **not acted
on**. Most systems never record this and are therefore permanently unfalsifiable.

| ID | Rule |
|---|---|
| **DN-19** | ★ **Every vetoed candidate is recorded** with ticker, `as_of`, the binding gate(s), and the ranked quantity it carried (CT-12.2) — the counterfactual arm |
| **DN-20** | ★ D-11 marks vetoed candidates to market on the **same horizon and the same open-anchored basis** as acted-on ones (QA-71), or the two arms are not comparable and §6.1 is uncomputable |
| **DN-21** | The counterfactual record is **write-once and never revised** (INV-005/006). A rejected-name history that can be edited is the most tempting record in the system to edit |
| **DN-35** | ★ **A vetoed candidate is scored at exactly `T+h` — the same horizon and the same open anchor as an acted-on position** (DN-20, QA-71). ⚠ **No early close and no extension.** A counterfactual arm whose window can be chosen after the fact measures the chooser, and the temptation runs one way: closing losers early and letting winners run is precisely the bias the gate is being tested for |
| **DN-36** | ★ **A candidate that delists, halts past `T+h`, or is acquired is recorded `terminated` with the reason — never dropped.** Dropping it is survivorship bias in the counterfactual arm (INV-017's shape), and it removes exactly the cases where a veto was most likely right |
| **DN-37** | ★★ **Overlapping windows are the norm and the effective sample is smaller than the row count.** The same name vetoed on consecutive days yields overlapping `T+h` windows, so the observations are autocorrelated — **§6.3's 3.5–11× gap assumed independence and is therefore OPTIMISTIC**. Any statistic over this arm reports its **effective N** (**QA-90**, QA-4), and the purge/embargo logic that applies to labels (QA-3) applies here too |
## 6.6 ★ Liveness is not derivable from the algebra

§5.7 proved the gates cannot deadlock. **A meet-semilattice expresses safety — "nothing bad
happens" — and cannot express liveness — "something eventually happens."**

```text
   D-01 PASSes a name for 40 consecutive runs.
   The h1w timing leg defers on all 40.
   The meet returns HOLD 40 times.

   No deadlock. Perfect commutativity. Every law satisfied.
   And the name is SILENTLY STARVED — 40 deferrals of one name inside
   a normal-looking 10% aggregate veto rate is invisible to DN-17.
```

| ID | Rule |
|---|---|
| **DN-29** | ★ **Track per-candidate consecutive deferrals.** A candidate deferred more than `d` consecutive runs while its thesis remains PASS is a **structural finding reported on the artifact**, regardless of the aggregate veto rate. §5's success at eliminating one class of bug makes it tempting to assume the whole class is handled: **safety is handled, liveness never will be by a lattice** |

## 6.7 ★ What routing D-01 through the gate actually costs

§5.0a called this a choice. Its price, from §6.3a:

| | |
|---|---|
| **Forgone** | up to **1.41×** IR uplift, if `ρ ≈ 0` and `IC₀₁ ≈ IC₀₃` |
| **Bought** | a zero-parameter rule, in a regime where §5.0's literature says fitted weights do **active harm** |
| **Reason it is the right trade** | the uplift is **unverifiable here** — it requires estimating `ρ` *and* both ICs, and §6.3 shows even the far cruder pass/veto spread is out of reach for a decade |

| ID | Rule |
|---|---|
| **DN-30** | ★ **The gate is recorded as a priced trade-off, not as the only option.** D-01 is a gate *by choice*, forgoing an uplift that cannot be verified at this breadth. **DN-27's `ρ` is what would reopen it** — and `ρ ≈ 0` sustained over years, with `IC₀₁` measurable, is the specific evidence that would justify revisiting `L2` CB-5 |


---

# 7. CONTRACTS

> **ID-collision notice.** `AC-12.k` / `CT-12.k` key `n` on **D-12**. `vision.md` §4 reserves F-IDs
> only through **F10**, so **F12 is unallocated** and this is currently collision-free — unlike
> D-01/F1, D-02/F2 and D-03/F3 (L0 §16.4). Qualify anyway, per T-4.

## CT-12.1 — Recommendation (JSON)

```json
{
  "as_of": "2026-08-18", "run_id": "…", "decision_anchor": "open",
  "candidate": {"ticker": "MU", "rank": 1, "ranked_quantity": 0.0412, "horizon": "h1m"},
  "verdict": {"final": "HOLD", "nominated": "BUY", "was_downgraded": true},
  "gates": [
    {"gate_id": "thesis",    "status": "VETO", "verdict_after": "HOLD",   // ★ status SOURCED from D-01 CT-1.4
     "reason": "falsifier 1 tripped: gross margin < 55% for 2 quarters",
     "stability": {"k": 5, "modal": "SELL", "agreement": 0.6}},
    {"gate_id": "timing_h1w", "status": "PASS", "verdict_after": "BUY"}
  ],
  "attribution": {"binding": ["thesis"], "binding_level": "HOLD"},
  "thesis_ref": {"ticker": "MU", "thesis_version": 4,        // ★ narrative is REFERENCED, not copied
                 "as_of": "2026-08-16", "bundle_hash": "sha256:…"},
  "alerts": [
    {"source": "D-05", "level": 2, "text": "theme 61.7% vs 40% reporting threshold",
     "blocking": false, "suppressible": false}
  ],
  "alerts_status": "COMPLETE",        // ★ DN-38 — or "UNCHECKED: <why>". An empty
                                      //   alerts[] with no status is an ALL-CLEAR claim

  "grade": {                          // ★ DN-25 — transported, NOT consumed by the algebra
    "consumed_by_algebra": false,
    "ranked_quantity": 0.0412, "rank": 1,                    // from D-03
    "verdict": "HOLD",                                       // ↓ from D-01 CT-1.4, COMPLETE
                                                             //   (the ANALYST's verdict, distinct
                                                             //    from verdict.final above)
    "conviction": "Medium-High",
    "stability_fraction": 0.6, "k": 5,
    "verdict_distribution": {"BUY": 3, "HOLD": 2},           // ★ RA-20 renders this verbatim
    "confidence": {"value": 0.62, "basis": "evidence_coverage",
                   "calibration": {"n": 3, "status": "not_yet_calibrated"}},
    "scorecard": {"moat_durability": 3, "earnings_quality": 4,
                  "balance_sheet_resilience": 3, "capital_allocation": 2}   // D-01 §8.1
  },
  "deferral": {"consecutive_runs": 2, "thesis_status_throughout": "PASS"},   // DN-29
  "actionable": true,
  "gate_roster_declared": ["thesis", "timing_h1w"],
  "gate_roster_reported": ["thesis", "timing_h1w"]
}
```

★ `gate_roster_declared` **vs** `_reported` is DN-11 made checkable: a difference is an error, not a
shorter list. `alerts[].blocking` is a constant `false` (INV-026, RK-2), present so the contract
says no other value exists.

## CT-12.2 — VetoedCandidate (JSONL, append-only → D-11)

`(ticker, as_of, ranked_quantity, horizon, binding_gates[], reason, decision_anchor,
outcome_h: {realised_return | pending})` — the counterfactual arm (DN-19, DN-20).

---

# 8. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `compose(nomination, gates, alerts)` | `Recommendation` | pure; total on declared inputs |
| `meet(*verdicts)` | `Verdict` | ★ the algebra — the only place composition happens |
| `apply_gate(verdict, status)` | `Verdict` | `φ`, monotone (DN-7) |
| `attribution(recommendation)` | `Attribution` | all binding gates (DN-13) |
| `veto_rate(window)` | `Rate` | DN-17's monitor |

★ **No method returns a score, a size, or a ranking.** If one ever does, D-12 has stopped composing.

---

# 9. BUSINESS RULES

| ID | Rule |
|---|---|
| **DN-1…DN-4** | Boundary — originates nothing; no feedback edge — §3 |
| **DN-5…DN-15** | The verdict algebra — §5 |
| **DN-16…DN-21** | Measurement and counterfactuals — §6 |
| **DN-24…DN-30** | Precondition · grade transport · seat correlation · liveness · the priced trade-off — §5.4a, §5.8, §6.3a, §6.6, §6.7 |
| **DN-22** | ★ **INV-6 is enforced here** — exactly one *actionable* recommendation per run. Informational/discovery output is permitted and explicitly marked non-actionable |
| **DN-23** | A `Recommendation` carries its `decision_anchor` and fails if it disagrees with the RunManifest (D-08 OR-35, MT-42) |

---

# 10. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `DEC.GATE.MISSING` | ERROR | a declared gate did not report (DN-11) |
| `DEC.GATE.ABSENT_TREATED_AS_PASS` | ERROR | ★ identity reached by omission (DN-10, §5.5) |
| `DEC.GATE.UNAVAILABLE` | ERROR | a gate errored — no actionable recommendation (DN-12) |
| `DEC.VERDICT.UPGRADE` | ERROR | ★ composed verdict more aggressive than an input — algebraically impossible; **firing means the meet was bypassed** (DN-5) |
| `DEC.VERDICT.ORIGINATED` | ERROR | a verdict traceable to no input (DN-1) |
| `DEC.ATTRIBUTION.INCOMPLETE` | ERROR | binding gates omitted (DN-13) |
| `DEC.FEEDBACK.DETECTED` | ERROR | ★ a D-12 output reached D-01 or D-03 (DN-3) |
| `DEC.ANCHOR.MISMATCH` | ERROR | anchor disagrees with the RunManifest (DN-23) |
| `DEC.GRADE.RECOMPUTED` | ERROR | ★ a transported field differs from its source (DN-26) |
| `DEC.SELL.NOT_HELD` | ERROR | ★ SELL emitted for an unheld name — outside the chain's precondition (DN-24) |
| `DEC.RHO.RANGE_RESTRICTED` | *(not an error)* | ρ unestimable — reported as **unmeasured**, never as a number (DN-28) |
| `DEC.INV6.MULTIPLE_ACTIONABLE` | ERROR | more than one actionable recommendation (DN-22) |

---

# 11. ACCEPTANCE CRITERIA

```text
THE ALGEBRA  (§5)  ★ exhaustive — |V| = 3, so there is no excuse for sampling
□ AC-12.1   meet is idempotent, commutative, associative, has identity BUY and
            absorbing element SELL — all four verified over V^3 exhaustively
□ AC-12.2   ★ for every input set, the composed verdict is no more aggressive
            than ANY input (P3, implied by DN-5)
□ AC-12.3   phi is monotone in both arguments, all 9 cases (DN-7)
□ AC-12.4   FLAG leaves the verdict unchanged AND changes the artifact (DN-8)
□ AC-12.5   ★ VETO on a SELL is inert — no upgrade occurs (DN-9, §5.4)
□ AC-12.6   gate evaluation order never changes the outcome (DN-14, DN-15)

FAIL LOUD  (§5.5)
□ AC-12.7   ★ a missing gate input raises; it is never treated as PASS (DN-10)
□ AC-12.8   the gate roster is declared before the run; declared != reported
            raises (DN-11)
□ AC-12.9   a gate error yields NO actionable recommendation (DN-12, DC-3)
□ AC-12.10  every binding gate appears in the attribution (DN-13)

BOUNDARY  (§3)
□ AC-12.11  every emitted verdict is traceable to an input verdict (DN-1)
□ AC-12.12  ★ no D-12 output reaches D-01 or D-03 — grep-checkable (DN-3)
□ AC-12.13  src/decision imports no LLM gateway (DN-2, ST-5)
□ AC-12.14  the API returns no score, size or ranking (§8)
□ AC-12.15  identical inputs produce an identical Recommendation (INV-2)

MEASUREMENT  (§6)
□ AC-12.16  ★ every vetoed candidate is recorded with its binding gates and
            ranked quantity (DN-19)
□ AC-12.17  vetoed candidates are marked on the same horizon and open anchor as
            acted-on ones (DN-20, QA-71)
□ AC-12.18  the counterfactual record is append-only and unrevisable (DN-21)
□ AC-12.19  veto_rate() is reported every run (DN-17)

GRADE TRANSPORT & LIVENESS  (§5.8, §6.6)
□ AC-12.22  ★ every graded input appears in CT-12.1 marked consumed_by_algebra:
            false, byte-identical to its source (DN-25, DN-26)
□ AC-12.23  ★ CT-12.1.grade's keys are a SUPERSET of D-01 CT-1.4's grade keys —
            no field is lost in transport (DN-32)
□ AC-12.23a RA-20 is renderable from CT-12.1 alone: k and verdict_distribution
            are both present, so "BUY 3 / HOLD 2" can be produced
□ AC-12.24  ★ consecutive deferrals are tracked per candidate and reported past
            d runs, independently of the aggregate veto rate (DN-29)

SEAT CORRELATION  (§6.3a)
□ AC-12.25  rho is reported over all covered names, not only vetoed ones (DN-27)
□ AC-12.26  ★ rho is NOT reported when coverage does not span the rank
            distribution -- range restriction makes it unestimable (DN-28)

PRECONDITION  (§5.4a)
□ AC-12.27  ★ a SELL on a name not currently held raises -- the chain's ordering
            does not hold for it (DN-24)

MANDATE
□ AC-12.20  exactly one actionable recommendation per run (INV-6, DN-22)
□ AC-12.21  alerts[].blocking is false for every alert (INV-026, DN-22)
□ AC-12.28  ★ an empty alerts[] carries alerts_status UNCHECKED:<why> whenever
            D-05 did not complete a pass; COMPLETE is emitted only after one
            (DN-38, RK-30, RK-36)
□ AC-12.29 ★ actionable=true requires alerts_status COMPLETE and a non-null
           verdict_stability; either absent forces informational (DN-39)
□ AC-12.30 ★ candidate.ranked_by carries the nomination's artifact id byte-identical
           and names it rule or model (DN-40)
□ AC-12.31 ★★★ A refused-model nomination composes only as not actionable (actionable=True
           raises); ranked_by carries status + failed gates (DN-41)
```

---

# 12. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QN-1** | ⚠ **CORRECTED v0.2.0.** Is the verdict set `{BUY, HOLD, SELL}`, or does it need `TRIM` / `ADD`? | v0.1.0 claimed *"ADD is more aggressive than BUY, so it cannot be reached by a meet, and adding it invalidates §5."* ★ **That reasoning is wrong** *(external review)*. Set `c(ADD) = −1` and `V = {ADD, BUY, HOLD, SELL}` is **still a chain, still a bounded meet-semilattice**; all five laws hold, `\|V\|³ = 64` is still exhaustive, and ADD *is* reachable — when every input is ADD. **What actually breaks is different: `BUY` ceases to be the identity.** §5.5's entire P5 argument is stated in terms of `⊤ = BUY`, so it needs restating for `⊤ = ADD`, and a gate returning BUY becomes a *downgrade* rather than a no-op. Second: **some domain must originate ADD**, or it is unreachable and inert — which DN-8 forbids on its own terms. `TRIM` at `c = 1.5` is genuinely harmless. **Recorded because the wrong reason would have caused a future reader to reject ADD for a non-problem while accepting an extension that breaks something real** |
| **QN-2** | Should `φ(v, VETO)` be **configurable per gate**? | Uniform `⊓ HOLD` is simple and provable. A gate wanting `⊓ SELL` is asking to originate a trade instruction (DN-9) — probably never, but state it |
| **QN-3** | ★ What is the **declared gate roster**, and who declares it? | DN-11 needs a source of truth. Config is the obvious home, which makes it a policy choice and therefore RunManifest-recorded (L4 CN-1, CN-5) |
| **QN-4** | Does a VETO **suppress the day** or surface the next-ranked name? | Inherited from `L2` QB-4 and still open. Surfacing #2 makes the gate a ranker over the top-`m`, which `L2` §4.3 says it cannot be |
| ~~**QN-5**~~ | ~~How long is `outcome_h` pending?~~ | ✅ **CLOSED 2026-08-18 — DN-35…DN-37** (recommended, adopted). Scored at **exactly `h`**, the same horizon and anchor as an acted-on position, with **no discretion** |
| **QN-6** | Does D-12 own the **INV-6 count**, or does D-08? | D-12 is the only place that knows what is actionable, which argues for here. D-08 knows what ran. Overlaps QQ-15 |
| **QN-7** | ★ What is `σ` for the **nominated** name, as opposed to the universe? | §6.2 adopts D-03's 8.66 % but notes QA-58's denormalised ranking over-represents high-vol names at the top. The gap between the two σ columns is a **factor of 1.5 on every MDE in §6.3**. Measurable directly from the nomination history once it exists |

---

# 13. REFERENCES

| Source | Used for |
|---|---|
| **Davey & Priestley**, *Introduction to Lattices and Order*, 2nd ed., CUP 2002, §§1–2 | meet-semilattice, bounded chains, the five laws of §5.2 |
| **Birkhoff**, *Lattice Theory*, AMS Colloquium Publications vol. 25 | monotone maps on ordered sets (§5.3's `φ`) |
| **Smith, J. & Wallis, K.** (2009), *A Simple Explanation of the Forecast Combination Puzzle*, Oxford Bull. Econ. Stat. 71(3) | ★ §5.0 — why estimated optimal weights lose to parameter-free ones |
| **Claeskens, Magnus, Vasnev & Wang** (2016), *The Forecast Combination Puzzle: A Simple Theoretical Explanation*, Int. J. Forecasting 32(3) | ★ §5.0 — random weights induce bias and inflate variance even with unbiased components |
| **DeMiguel, Garlappi & Uppal** (2009), *Optimal Versus Naive Diversification*, RFS 22(5) | ★ §5.0 — the portfolio-construction twin: `1/N` beats optimisation out of sample |
| **Clarke, de Silva & Thorley** (2002), *Portfolio Constraints and the Fundamental Law*, FAJ 58(5) | the transfer coefficient behind §6.3 |
| **Grinold & Kahn**, *Active Portfolio Management*, 2nd ed. | `IR ≈ IC·√BR`; the breadth constraint behind §6.3 |
| **Ding & Martin**, *The Fundamental Law of Active Management: Redux*, JEF 2017 | the **transfer coefficient** — a concentrated book cannot express, hence cannot measure, a modest signal (§6.3) |
| **Qian, Hua & Sorensen**, *Information Horizon, Portfolio Turnover, and Optimal Alpha Models*, JPM 2007 | slow vs fast signals; why the thesis acts as a persistent constraint rather than a daily score |
| `sdd/specs/constitution.md` **P3** (as amended 2026-08-13), P2, P5, INV-2, §4 tiers | monotonicity; determinism; the property-test tier §5.2 uses |
| [`L2-signal-combination.md`](L2-signal-combination.md) §3, §4.3, §6, CB-15…CB-18 | the architecture D-12 implements; QB-1/QB-2/QB-5 closed here |

---

# 14. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §1.6, §3.1, **§4.3**, INV-014, **INV-026**, INV-6, §16.2 | the domain registry D-12 joins; the seat argument in §1.4 |
| `L1-quantitative-analysis.md` **QA-47**, QA-58, **QA-71**, §5.8 | the nomination; the internal arbitration D-12 generalises; the open anchor DN-20 needs |
| `L1-fundamental-analysis.md` CT-1.1, RA-20, RM-1 | the gate input and the stability that travels with it |
| `L1-risk-management.md` **§1.4**, RK-2, **RK-14**, RK-18 | the third channel; why the premature-exit flag is a FLAG (§5.4) |
| `L1-orchestration.md` OR-35, §5A | `decision_anchor`; where the composed run sits in the cadence |
| `L1-recording.md` RC-24 | the journal that records an override of a VETO |
| `L1-reporting.md` §5, DC-3, DC-5 | reliability classes; why D-09 may render but never originate (§1.2) |
