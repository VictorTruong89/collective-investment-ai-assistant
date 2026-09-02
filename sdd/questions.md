# Question Register — every question, answered and open

> **Tier:** permanent · release-independent · **cross-cutting**. Sits beside
> [`README.md`](README.md) (the tier map) rather than inside any one tier.
> **Purpose:** one place to find every design question this project has faced, what was decided,
> **what was rejected and why**, and where the answer actually binds.
> **ID family:** `QR-n` — sequential, assigned in the order a question arose, **never renumbered**.
> Module grouping is done by the §-sections and the index, not by the ID.

---

## ⚠ What this file is, and what it is NOT

```text
╔══════════════════════════════════════════════════════════════════════╗
║  THIS REGISTER CARRIES THE *WHY*.                                    ║
║  THE CONSTITUTION AND THE SPECS CARRY THE *RULE*.                    ║
║                                                                      ║
║  ★ A decision here always names where it BINDS. The binding text     ║
║    lives there, once. This file never restates a rule — it records   ║
║    the reasoning, the alternatives, and the date.                    ║
║                                                                      ║
║  ⚠ If this file ever starts restating rules, it has become the       ║
║    "second source of truth" that sdd/README.md forbids, and it       ║
║    will drift. Cut it back to reasoning + pointer.                   ║
╚══════════════════════════════════════════════════════════════════════╝
```

This is an **Architecture Decision Record** in substance (Nygard, 2011), collapsed into one register
rather than one file per decision, because tracking in a single place was the requirement.

**Statuses:** ✅ decided · 🔵 open · ⏸ deferred · ⬆ owned upstream · ⊘ withdrawn · ~~struck~~ superseded

---

# 1. Index

| ID | Question | Module | Status | Binds in |
|---|---|---|---|---|
| **QR-1** | Which repo is the home? | platform | ✅ | `vision.md` §2 |
| **QR-2** | Portfolio framing — xAI-led, agents-led, or both? | platform | ✅ | `vision.md` §1.1 |
| **QR-3** | Is deliberation acceptable only if measured? | D-14 · seat 9 | ✅ | `PG-5.1` · `PG-5.2` |
| **QR-4** | Does a verified E2E run gate platform code? | platform | ✅ | `PG-1` |
| **QR-5** | ★ **The IC gate's standard error** | D-03 · seat 3 | ✅ ⚠ *corrected 2026-09-01* | ⬆ upstream `metric_gate.py`, §5.3b — **action required** |
| **QR-6** | Does D-12 stay deterministic? | D-12 · seat 6 | ✅ | `PG-6` |
| **QR-7** | ★ **Which pluggability layers, and what binding times?** | D-00 · F1 | ✅ | `vision.md` §7 · `F1` scope |
| **QR-8** | Is the registry agent-scoped or module-scoped? | D-00 · F1 | ✅ | `vision.md` §4.1 `F1` |
| **QR-9** | Is "interactive agents" one feature or two? | D-08 · seat 7 | ✅ | `vision.md` §4.1 `F6a`/`F6b` |
| **QR-10** | Who owns explainability — each domain, or seat 6? | D-13 · seat 6 | ✅ | `vision.md` §3, §4.2 |
| **QR-11** | How many scalability axes? | platform | ✅ | `vision.md` §6 |
| **QR-12** | ★ **Publication model — how are all rights retained?** | platform | ✅ | [`../LICENSE`](../LICENSE) · `M9` |
| **QR-13** | Does `src/evaluation/` get a spec, or stay gate-exempt? | D-14 · seat 9 | ✅ | `ownership.yaml` · `F5` |
| **QR-14** | Is LangGraph confinement enforced by CI grep? | D-08 · seat 7 | ✅ | `A8` · `F2` ACs |
| **QR-15** | Does `config/` merge cleanly at absorption? | platform | 🔵 | — |
| **QR-16** | ★ **What is produced when asked about a name outside the top-1?** | D-09 · seat 8 | ✅ | `F8` · `F9` ACs |
| **QR-17** | ★ **How are unpredictable human directives handled?** | D-08 · seat 7 | ✅ *(reframed 2026-09-01)* | `F8` §2.1 · `AC-8.12`–`AC-8.20` |
| ~~QR-18~~ | *withdrawn — misread intent; ID retired, not reused* | — | ⊘ | — |
| **QR-19** | ★ **The IC gate's t-threshold** — spun out of QR-5 | D-03 · seat 3 | ✅ | ⬆ upstream — **with QR-5** |
| **QR-20** | Is the API or the relay the default thesis source? | D-01 · seat 2 | ✅ | `F9` default variant |
| ⬆ | Upstream questions that block this repo | various | ⬆ | §9 |

---

# 2. Platform-wide

## ✅ QR-1 — Which repo is the home?

**Origin:** rel1 S1, 2026-08-28. **Status:** ✅ decided 2026-08-28. **Binds:** `vision.md` §2, `PG-8`.

**Context.** The platform work could extend `ai-investment-pipeline` in place, live in a new repo, or
fork it. `ownership.yaml` globs cannot be written until this is settled, so it blocked every spec.

| Option | Rejected because |
|---|---|
| Extend the pipeline in place | Lowest risk to investment capability, but the portfolio artifact stays tangled with years of pipeline history |
| Fork and diverge | Two divergent copies to maintain; investment work splits from portfolio work |
| ★ **Build here, import, then absorb** | **Chosen** |

**Decision.** Build the platform in this repo, importing the pipeline in the interim; copy its `src/**`
tree in once stable; **retire the old repo**. Consequence: this tree must be a **superset** of the
pipeline's from day one so the absorption is a merge, not a restructuring (`PG-8`).

## ✅ QR-2 — Portfolio framing

**Origin:** rel1 S1. **Status:** ✅ decided 2026-08-28. **Binds:** `vision.md` §1.1.

**Context.** My recommendation was to make explainability the headline and subordinate agents, on the
grounds that "I built a multi-agent system with LangGraph" is table stakes by 2027 while
interpretability and evaluation are scarce.

| Option | Outcome |
|---|---|
| xAI-led, agents subordinate | *(my recommendation)* — not chosen |
| Agents-led | Not chosen |
| ★ **Balanced dual pitch** | **Chosen by Victor** |

**Why it works despite the split-focus risk.** The two lanes share one substrate — the evaluation
harness — and the deliberation A/B study is *simultaneously* the agent demo and the evaluation demo.
One thesis, two demos. ⚠ Conditional on the harness being built **once, early, and shared** (`PG-4`);
if each lane grows its own ad-hoc measurement code the risk becomes real.

## ✅ QR-4 — Does a verified E2E run gate platform code?

**Origin:** rel1 S1. **Status:** ✅ decided 2026-08-28. **Binds:** `PG-1`.

**Context.** The pipeline has 34,723 LOC and 1,192 passing tests but **has never completed a verified
end-to-end production run**.

**Decision.** Binding gate — no platform code until it does. Mirrors Victor's own precedent for D-10
(*"I do not plan to implement D-10 code until the full pipeline runs stably"*). ⚠ Blocks
*implementation* only; spec-writing continues.

**Rejected:** a soft gate allowing F1/F2 in parallel — faster, but risks arriving at May 2027 with an
elaborate demo over an unproven signal.

## ✅ QR-11 — How many scalability axes?

**Origin:** rel1 S3. **Status:** ✅ decided 2026-08-30. **Binds:** `vision.md` §6.

**Decision.** **Two** — horizontal (additional modules) and vertical (deeper maths/logic within a
module, *including swapping a better implementation behind an unchanged contract*).

**Rejected:** a third "substitutional" axis, which I had proposed. Substitution is a **vertical move** —
it makes an existing capability better or different behind an unchanged contract, rather than adding a
capability. `C1` and `A3` are what make it cheap.

## ✅ QR-12 — Publication model: source-available, all rights reserved

**Origin:** `vision.md` §8 (V-Q1), 2026-08-30. **Status:** ✅ decided 2026-08-30.
**Binds:** [`../LICENSE`](../LICENSE) *(written 2026-08-30)* · README §Licence *(pending)* · `M9.1`–`M9.3`.

**Victor's requirement:** *"this project only review the code base, but I keep all control and rights."*

### ⚠ First, the terminology — this is NOT open source

```text
   OPEN SOURCE (OSI)     grants rights: use, modify, distribute.
                         Even AGPL — the most restrictive OSI licence —
                         grants all three.

   ★ SOURCE-AVAILABLE    the code is READABLE. No rights are granted.
                         This is what "review only, I keep all rights" means.
```

⚠ **Calling it "open source" while reserving all rights is a category error** that a technical reviewer
will notice, and it reads as inexperience rather than caution. Use *source-available*.

### How it is enforced

★ **Chiefly by doing nothing.** Under the Berne Convention copyright attaches automatically on
creation, and **absent a licence grant, nobody has any right to use, copy, modify or distribute the
work.** "All rights reserved" is the *default state*; you enforce it by withholding the grant, not by
adding a restriction.

| # | Measure | Why |
|---|---|---|
| **1** | An explicit `LICENSE` file stating **"All rights reserved. No licence is granted."** | Removes the ambiguity a missing file creates. Readers assume an unlicensed public repo is an oversight |
| **2** | A short `README` §Licence: viewing and evaluation permitted; **no use, modification, redistribution or derivative works** | States intent in the place people actually read |
| **3** | Copyright header in source files | Survives a file being copied out of context |
| **4** | ⚠ **State that contributions are not accepted** | Accepting a PR without a CLA muddies ownership — the contributor holds copyright in their patch |
| **5** | ★ **Publish a curated mirror, not the working repo** | See below — this solves two problems at once |

### ⚠⚠ The GitHub trap

Making a repository public on GitHub grants other users, through GitHub's own Terms of Service, the
right to **view and fork** it — independently of what your `LICENSE` file says. A `LICENSE` reserving
all rights does **not** remove the fork right you granted by publishing there.

**So decide which you actually want:**

| Want | Do |
|---|---|
| Anyone with the link may read; forking acceptable | Public repo + all-rights-reserved `LICENSE` |
| ★ **No forking; controlled audience** | **Private repo, access granted per reviewer** — the normal arrangement for a hiring conversation |

⚠ Verify current GitHub terms before publishing rather than relying on this note; platform terms change.
*(This is a design record, not legal advice.)*

### ★ The curated mirror — recommended regardless

Publish a **separate, curated repository** containing the platform, rather than exposing the working
repo:

| Publish | Withhold entirely |
|---|---|
| SPI registry, agent protocol, orchestrator, trace/replay | the mandate and investment posture |
| explainability, evaluation harness | the book, positions, P&L, broker exports |
| ★ **the specs** — arguably the strongest artifact, and they carry no strategy | credentials, `.env`, API keys |
| synthetic-data fixtures so it actually runs | tuned parameters and the fitted model |

Two problems solved at once:
1. **The withheld surface is absent, not merely unlicensed.** Far stronger than trusting a licence.
2. ⚠ **Git history.** A secret ever committed to the working repo lives in its history forever. A
   fresh mirror has no history to leak.

### ⚠ One thing to check before publishing

**Dependency licences.** Copyleft dependencies (GPL/AGPL) can impose obligations on redistribution.
Audit the tree before the first publish — cheap then, expensive after.

### The tension worth knowing

For purpose 2, a repo nobody can *run* is less compelling than one they can. ★ The mirror resolves it:
the platform runs on synthetic fixtures while the strategy stays private. And note that what actually
gets reviewed in hiring is usually a link, a README and a walkthrough — **the specs may be the strongest
thing you show**, and they leak nothing.

**Rejected:** a permissive OSI licence (MIT/Apache-2.0) — grants exactly the rights Victor wants to
keep. **Rejected:** AGPL as a "restrictive" choice — it is still an OSI grant, and its copyleft targets
network distribution, which is not the concern here.

## 🔵 QR-15 — Does `config/` merge cleanly at absorption?

**Origin:** `L4-target-structure.md` S-3. **Status:** 🔵 open. Low urgency until Phase 0 completes.

---

# 3. D-00 Shared — the registry and protocol

## ✅ QR-8 — Agent-scoped or module-scoped registry?

**Origin:** rel1 S2, 2026-08-29 — Victor asked whether the specs actually carried his three intended
features. **Status:** ✅ decided 2026-08-29. **Binds:** `vision.md` §4.1 `F1`.

**Context.** F1 was written as `AgentPort` + an **agent** registry. The stated feature was pluggable
**modules** — strictly broader, and the pipeline already proves the wider need: `DataSourcePort`
(EDGAR/FMP), `RankingModelPort`, `LLMGatewayPort`, `ReportRendererPort`.

**Decision.** F1 is **module-scoped**: one registry keyed by `(port, variant)`, with `AgentPort` as one
registered port among several. ★ An agent is just one kind of pluggable module.

**Rejected:** agent-only first, generalise later — it would mean writing the same resolution,
validation and versioning logic twice.

## ★ ✅ QR-7 — Which pluggability layers, and what binding times?

**Origin:** rel1 S1 §D.5, 2026-08-28. ⚠ **Corrected** rel1 S2 §H.2, 2026-08-29.
**Status:** ✅ decided 2026-08-30. **Binds:** `vision.md` §7 (non-goal) · `F1` scope.

### Origin and the error that shaped it

`prompt.md` proposed four "layers" of pluggability, and separately (in its Question 3) four
"interpretations". My S1 recommendation cut "Layer 4" — **on a name collision.**

```text
   prompt.md §5.1 "LAYER 4"        = DYNAMIC SELECTION
                                     orchestrator picks a variant per ticker
                                     → a routing function. Cheap. Deterministic.

   prompt.md Q3 "INTERPRETATION D" = HOT RELOAD
                                     swap code while the process runs
                                     → a plugin loader. Expensive. Ornamental.

   ⚠ I conflated them and cut the cheap, load-bearing one by name.
```

Worse, I had also *deferred* Layer 2 (config/personality variants) as "an unvalidated free parameter."
⚠ **Layer 2 is load-bearing for `C2`**: "agent A influences agent B's config" is meaningless if B has
no config variants to select among. Deferring it would have quietly gutted a stated feature.

Both verdicts were struck through in place rather than silently rewritten.

### Decision — layers

| Layer | Verdict | Why |
|---|---|---|
| **1** — LLM tier swap (Opus/Sonnet/Haiku) | ✅ keep | Already near-built via the gateway; real cost saving (`C9`) |
| **2** — config / personality variants | ✅ keep | ★ Load-bearing for `C2`. The original objection is answered by `PG-5` (measure it) and `PG-7` (record it), **not** by removing the mechanism |
| **3** — implementation swap via registry | ✅ keep | The genuine architecture story; what makes the A/B study possible |
| **4** — dynamic per-ticker selection | ✅ keep | A routing function, `(features) → variant name`. It is `F6a`'s mechanism |
| **D** — hot reload without restart | ✗ **cut** | Over-engineered for a single-machine, single-user, once-daily batch system. An interviewer who knows systems reads it as ornament |

### Decision — the binding-time consequence (the part that was still open)

With Layer 4 in scope, the registry is called **during a run** with a variant chosen by a routing
function — not only once at startup. That forces a choice nobody had made:

| Option | Assessment |
|---|---|
| **Open set** — variants discovered or loaded lazily | ✗ **Rejected.** More flexible, but it reintroduces exactly the hot-reload hazards just cut, and makes boot-time validation impossible |
| ★ **Closed set** — every selectable variant registered at startup, resolvable at any time | ✅ **Chosen** |

**Why closed.** Three properties fall out of it:
1. `validate_coverage()` stays meaningful — a typo or missing variant fails **at boot**, not at 3am mid-run.
2. ★ **The hot-reload non-goal becomes structural rather than merely stated** — you cannot select a
   variant that was never registered.
3. The trace can enumerate the full candidate set, so "why this variant" has a complete answer.

⚠ **Consequence for `F1`'s spec, worth writing before it is discovered in profiling:** with per-ticker
selection over ~500 names, the registry must **cache instances per `(port, variant)` within a run**, or
a model gets reloaded 500 times.

---

# 4. D-01 Fundamental — seat 2

## ✅ QR-20 — The Anthropic API is the default thesis source

**Origin:** rel1 S4 discussion, 2026-08-30. **Status:** ✅ decided 2026-08-30. **Binds:** `F9` — the
registry's default variant for `ThesisSourcePort`.

**Context.** The pipeline **already has a relay** — `src/fundamental/relay/` (D-01 §4B,
*"an external provider with a human as its transport"*): prompt composition, a rotation queue with
judgement overrides, schema validation, **claim re-verification that raises on contradiction**, and
coverage-based confidence de-rating. ★ It is not "trust the paste". Victor proposed extending it to
use Claude Code as the transport — a *change of transport*, not a new architecture, and arguably an
improvement since Claude Code can write the result to disk directly instead of relying on a human
paste-back.

**Framing reached:** two adapters behind one `ThesisSourcePort` (`F9`), with a `provenance` field
driving the de-rating. The choice becomes a registry entry, and the two can be A/B'd against each
other on the same ticker.

**Decision.** **`ApiAdapter` is the default; `RelayAdapter` is the alternate.** Both sit behind one
`ThesisSourcePort` (`F9`), so the choice is a registry entry, not a fork in the pipeline.
★ **Then measure the actual monthly API bill and revisit with a number rather than an estimate.**

**Why.**
- The cost premise was never measured. An order-of-magnitude estimate puts a cached drill-down near
  **$0.20**, halved again by the Batch API — plausibly single-to-double-digit dollars a month.
  ⚠ **Building a manual relay to avoid a bill you have not read is optimising a guess.**
- The API path is **one button and ~60 seconds**; the relay costs 5–10 minutes of the manager's own
  attention per use. At a $0.20 alternative, that trade is poor.
- ★ **The relay's real justification is capability, not cost** — Claude Code is an *agent with tools*
  that can read filings, run the pipeline's own functions and iterate, where an API call is one-shot.
  That case stands on its own and survives a cost drop; the cost case does not.
- Provenance drives confidence either way (`QR-16`), so nothing downstream depends on which won.

**Rejected — relay as default:** it front-loads friction and weakens verifiability, on a premise that
measurement may dissolve.

**Action:** pull the usage and cost report before revisiting. ★ Ten minutes of work that either
validates the concern or removes it.

---

# 5. D-03 / D-04 Quant — seat 3

## ★★ ✅ QR-5 — The IC gate's standard error

**Origin:** upstream **AB-12**, found 2026-08-27 while wiring promotion. **Owner:** D-03.
**Upstream rules:** QA-4, QA-17, §5.3b. **Status:** ✅ decided 2026-08-30 — ⬆ **implementation is an
upstream change**.

### Context — what the number is

Each trading date the model scores ~500 names; the **Information Coefficient** for that date is the
rank correlation between predicted order and realised forward 21-day returns. Across 2,491 dates the
mean IC is **0.0203**. `ic_significance_gate` asks whether that is distinguishable from zero — a
t-test, `t = mean_IC / SE(mean_IC)`. **Everything turns on the denominator.**

### ⚠ The finding — two defensible denominators disagreeing by 3.49×

| Standard error | Formula | Value | **t** | Verdict |
|---|---|---|---|---|
| `corrected_se` *(current)* | `√( h / ((n−1)·T) )` | 0.00411 | **4.94** | ★ PASS |
| Realised | `sd(per-date IC) / √(T/h)`, `sd = 0.156` | 0.01433 | **1.42** | ⚠ fail |

Both carry the same overlap divisor — a 21-day forward label means consecutive daily ICs overlap, so
there are roughly `T/h = 2491/21 ≈ 118.6` effectively independent observations, not 2,491.

**The entire difference is the assumed per-date dispersion:**

```text
   NULL      sd = 1/√(n−1) = 1/√499 = 0.0448    ← ASSUMED
   OBSERVED  sd            =          0.156     ← MEASURED
                                    ─────────
                            0.156 / 0.0448 = 3.49×
```

Under H₀ of no skill, the sampling sd of a rank correlation across `n` names genuinely **is** `1/√(n−1)`.
That is a mathematical fact. The problem is that the measured dispersion is 3.49× larger — because real
cross-sectional IC swings across regimes (2016–18 and 2024–26 scored ~0.034; 2018–20 and 2022–24 ~0.009).

### Two further defects bundled in the same finding

- ⚠ **QA-4's promise is broken.** The rule requires *"an autocorrelation-corrected standard error."*
  `corrected_se` contains **no autocorrelation correction at all** — it is the null variance with an
  overlap divisor. The name and the rule both promise what the formula does not do. True regardless of
  which denominator wins.
- ⚠ **A power calculation is being used as an acceptance test.** §5.3b calls its table an **MDE** —
  *"the bar, not a prediction," "computable before anything is measured."* The gate computes
  `passed = |IC| >= mde`, which is inference, not planning. Mechanically it reduces to a null-SE t-test
  at t > 3, so it is not *wrong* — but the framing hides what is actually happening.

### Options considered

| # | Option | Assessment |
|---|---|---|
| **1** | **Keep the null SE** | ✗ **Rejected.** Defensible in principle — under H₀ the variance *is* `1/(n−1)`, and the excess dispersion is arguably time-varying *true* skill rather than noise, so charging the test for it is conservative to the point of being wrong. ⚠ But it requires amending QA-4 to stop promising autocorrelation correction and renaming `corrected_se`, **and it promotes a model whose realised t is 1.42** |
| ★ **2** | **Swap only the variance term — keep `N_eff = T/h`** | ✅ **CHOSEN (corrected 2026-09-01).** No bandwidth, no free parameter; changes exactly the term that is wrong |
| ~~3~~ | ~~Newey–West HAC~~ | ✗ **Rejected on 2026-09-01** — upstream's method registry already rejected NW for the overlap correction, with a sound argument (`h` is known exactly). It would replace an exact divisor with an estimated one |
| ★ **4** | **Report both, gate on the realised** | ✅ **Chosen as the reporting policy** |

### ⚠⚠ CORRECTED 2026-09-01 — option 2, not option 3

> **The original decision here was option 3 (Newey–West HAC). It was wrong, and it was wrong because
> I had not read the upstream method registry.**
>
> `src/quant/methods/entries/effective_n.overlap_corrected.v1.md` already considered Newey–West and
> **rejected it, with a sound argument**: *"Estimates a quantity we already know exactly; a bandwidth
> choice is a free parameter where none is needed."* At horizon `h` the overlap length is **known**, so
> `N_eff = T/h` is exact. Newey–West would replace an exact divisor with an estimated one.

★★ **And the decisive detail: both standard errors already share that identical divisor.** Verified
2026-09-01:

```text
   N_eff = T/h = 2491/21 = 118.6          ← SHARED by both

   SE_null     = 0.0448 / √118.6 = 0.00411   ← matches the published figure
   SE_realised = 0.1560 / √118.6 = 0.01432
                 ──────
                 the ONLY term that differs
```

★ **So the overlap correction was never the problem, and the 3.49× gap is entirely the dispersion
term.** Option 3 would have changed the half that was already correct and left the half that was
wrong.

### ✅ Decision — option 2

**Keep `N_eff = T/h` exactly as it is.** Replace only the variance term: the **null** `1/(n−1)` becomes
the **realised** `sd(per-date IC)²`. Report both figures side by side (option 4); gate on the realised.

```text
   SE = sd(per-date IC) / √(T/h)          no bandwidth · no free parameter
```

### ⚠ And a correction to AB-12's own wording

AB-12 states `corrected_se` *"contains no autocorrelation correction at all."* That is **overstated**.
The `T/h` divisor **is** the autocorrelation correction — the method entry says so explicitly, and
calls it *"the same one Newey–West applies in the time domain."*

★ The real defect is narrower and sharper than AB-12 claims: **the variance term is theoretical rather
than measured.** So `QA-4`'s wording needs *clarifying*, not the formula needs *fixing* — and 0.3 in
the build plan shrinks accordingly.

### Why

1. ★★ **The null SE relies on an assumption the data has already falsified.** It asserts per-date
   dispersion of 0.0448; 0.156 was measured. Continuing to divide by 0.0448 is not conservatism — it is
   discarding a measurement that was paid for.
2. ★★ **A promotion gate is a forward decision, not a historical hypothesis test.** The two SEs answer
   different questions: *"did this model have skill somewhere in 2016–2026?"* (null SE — yes, t = 4.94)
   versus *"should I deploy this next year, not knowing which regime comes?"* (realised — regime
   variation is genuine uncertainty about the forward outcome). **The second is the question a
   promotion gate exists to answer.**
3. ★ **It changes the minimum.** The overlap divisor is already exact and already correct; only the
   variance term is wrong. A fix that touches one term is reviewable in a way that a re-derivation is not.

### ⚠ Consequences — none of these are optional

- ★ **Spun out as `QR-19`: the t-threshold must be re-derived in the same change.** At t > 3 with the
  realised SE the required IC is ≈ 0.043 — high for a monthly-horizon equity ranker, where published
  cross-sectional ICs typically run 0.02–0.05. **Changing the denominator without revisiting the
  threshold silently raises the bar ~3.5× and may make it unreachable.**
- ⬆ **This is an upstream change.** `vision.md` §2: inherited analytical logic changes in the pipeline
  repo, not here. It touches D-03's contract, `mde()`, the §5.3b table and QA-4. **Not applied
  unilaterally** — recorded here as decided, pending an upstream edit.
- **The MDE-as-acceptance conflation should be fixed at the same time** — keep the MDE table as a
  planning artifact, and state the acceptance test separately as what it is.
- ⚠ **Expect the gate to start refusing models it previously passed.** That is the mechanism working,
  and it will look like a regression on the first run that hits it.

**Stakes, stated plainly:** `ic_significance` **passed** on the last run. The model was refused only
because `cost_survival` and `breadth` were `NOT_EVALUATED`. ★ **The moment those two land, the current
gate promotes a model whose realised t is 1.42.** For this repo it is worse than upstream: QR-5 blocks
every performance claim, therefore every demo, therefore the answer to *"does it work?"* — and it is
squarely `PG-2` territory.

## ✅ QR-19 — The IC gate's t-threshold

**Origin:** spun out of QR-5, 2026-08-30. **Status:** ✅ decided 2026-08-30 — ⬆ **applied with QR-5's
upstream change, not after.** **Owner:** D-03.

**Decision.** **t > 2.0** on the HAC standard error, **plus the selection count recorded and reported**;
where a model was chosen from `N` evaluated configurations, a Šidák-adjusted threshold applies.

### ★★ Why t > 2 is a tightening, not a loosening

This is the part that is counter-intuitive and settles the question. Work the required IC at each
combination:

| Denominator | Threshold | Required IC | vs today's bar |
|---|---|---|---|
| null SE `0.00411` | t > 3 *(status quo)* | **0.0123** | — *(= §5.3b's published MDE, confirming the reading)* |
| ★ HAC/realised `0.01433` | **t > 2** | **0.0287** | ★ **2.33× stricter** |
| HAC/realised `0.01433` | t > 3 | 0.0430 | ⚠ **3.49× stricter** |

★ **Switching the denominator has already tightened the gate substantially on its own.** Carrying
`t > 3` across as well *compounds* the two, producing a bar 3.49× the one anyone actually chose — a
decision nobody made, arrived at by inertia.

⚠ **And 0.043 is likely unreachable in practice.** Published cross-sectional equity ICs typically run
0.02–0.05, so a genuinely good signal at IC 0.03 yields `t = 0.03/0.01433 = 2.09` — it clears t > 2 and
fails t > 3. A gate that refuses genuinely working signals fails purpose 1 as surely as one that
promotes noise.

### The Type I / Type II balance

| Error | Cost |
|---|---|
| **Type I** — promote a model that does not work | ⚠ Trading real capital on noise. `PG-2` says this is the expensive one |
| **Type II** — refuse a model that does work | Opportunity cost — and, at the limit, **never deploying anything**, which also fails purpose 1 |

t > 2 (~95%) sits at the conventional point. ★ **And the significance gate is not the only safeguard** —
`cost_survival` and `breadth` gate independently, and nothing reaches capital without the manager's
decision. Loading all conservatism onto one gate double-counts it.

### ⚠ On the "t > 3 in finance" convention

Harvey, Liu & Zhu (2016) argue for a ~3.0 threshold in asset pricing — **because of multiple testing
across the published factor zoo**, where hundreds of researchers have tested thousands of factors. That
argument does not transfer unchanged to one researcher testing one model family.

★ **But it transfers *partially*, and that is what the selection count is for.** D-10 exists to sweep
configurations; choosing the best of `N` and then testing it at t > 2 is exactly the multiple-testing
error Harvey warns about. So:

- **Pre-registered single test** → t > 2.
- **Model selected from `N` candidates** → record `N` and apply Šidák:
  `α_adj = 1 − (1 − α)^(1/N)`, which raises the required t accordingly.
- ⚠ **Reporting `N` is mandatory either way.** A significance figure with an unstated selection count
  is not interpretable, and this is the single most common way quantitative results overstate
  themselves.

**Rejected — carry t > 3 unchanged:** it was calibrated against a denominator 3.49× smaller, and
keeping both compounds two independent conservatisms into an unreachable bar.
**Rejected — a fixed threshold with no selection count:** it leaves the multiple-testing problem
entirely unaddressed, which is the one that actually bites once D-10 starts sweeping.

⚠ **Revisit when D-10 begins large sweeps** — that is when the adjustment stops being bookkeeping and
starts binding.

---

# 6. D-08 Orchestration — seat 7

## ✅ QR-9 — Is "interactive agents" one feature or two?

**Origin:** rel1 S2 §H.2, 2026-08-29. **Status:** ✅ decided 2026-08-29. **Binds:** `vision.md` §4.1.

**Context.** The stated feature was *"one agent's output influences another's config/model selection,
and two agents can argue."* The spec carried only the arguing half; the config-influence half was
**constrained** by `PG-7` but **specified by nothing**.

**Decision.** Split into **`F6a`** (config-influence routing) and **`F6b`** (messaging and deliberation).

**Why.** The halves have different determinism properties and disjoint failure modes:

| | `F6a` config influence | `F6b` argumentation |
|---|---|---|
| Mechanism | routing function | message state machine |
| Determinism | ★ fully deterministic, replayable | ⚠ LLM in the loop |
| Main hazard | ⚠⚠ **cycles**; loss of view independence | ⚠⚠ **sycophancy** |
| Gating | none — ships on its own | gated on `F7a` (QR-3) |

⚠ Collapsing them hid the fact that only one is gated.

## ✅ QR-14 — LangGraph confinement is enforced by CI grep

**Origin:** `L4-target-structure.md` S-2. **Status:** ✅ decided 2026-08-30.
**Binds:** `A8` (principle) · `F2` acceptance criteria (mechanism).

**Decision.** Any orchestration framework is imported by **`src/orchestration/graph/` and nothing
else**, enforced by a CI grep — the same mechanism `ST-5` already uses for the LLM gateway. Agents stay
plain Python behind `AgentPort`.

**Why a grep rather than review.** `A8` says frameworks are confined; a principle that only reviewers
enforce degrades the moment someone is in a hurry. A grep is cheap, runs every build, and fails loudly.
★ It also converts an architectural claim into a **checkable** one — *"my domain logic is independent
of the framework, and here is the test that proves it"* is a far stronger interview statement than the
assertion alone.

⚠ **What the grep cannot catch** — record it so nobody mistakes the check for a proof: a dynamic
`importlib` call; a re-export that launders the import through an allowed module; a transitive
dependency pulling the framework in. The grep catches the *ordinary* violation, which is the one that
actually happens.

**Consequence:** if the framework is abandoned in 2028, the blast radius is one directory.

## ✅ QR-17 — *(withdrawn 2026-08-30, then answered 2026-09-01)*

**Withdrawn** because the formulation — *"are human directives tighten-only?"* — assumed directives
could be **enumerated in advance**. ★ **Victor's correction, 2026-09-01:** they are *"case-by-case and
diversified… I cannot define or predict these directives now."*

**That dissolves the original question and replaces it with a better one:** not *which directives are
allowed*, but *how is an unbounded expression mapped onto a bounded effect*.

**Decision.** An LLM **interprets** one line of natural language into a typed directive drawn from a
**closed effect vocabulary**; the manager confirms the resulting parameter diff; the system applies it
deterministically. ⚠ Interpretation is **frozen at input time** — replay reads the stored object and
never re-invokes the model, which is what keeps `PG-9` intact. Raw text reaches no downstream prompt.

**Binds:** `F8` §2.1, `CT-8.4`–`CT-8.6`, `AC-8.12`–`AC-8.20`.
⏳ **The initial effect vocabulary is deferred to E2E validation** — `L3` §7 `E1`.

## ⊘ QR-18 — *withdrawn*

**Withdrawn 2026-08-30.** As `QR-17`. ⚠ **ID retired — not reused.**

---

# 7. D-12 / D-13 Decision & Explainability — seat 6

## ✅ QR-6 — Does D-12 stay deterministic?

**Origin:** rel1 S1 §D.3. **Status:** ✅ decided 2026-08-30 **for this release**. **Binds:** `PG-6`.

**Decision.** Yes. The verdict algebra stays a bounded meet-semilattice, so *"verdicts gate, never
upgrade"* remains a **structural** guarantee rather than a runtime check.

**Rejected:** replacing it with a learned or LLM-assisted combiner. ⚠ That discards a provable safety
property for an unmeasurable one **at the exact point where output becomes action** — the most
expensive mistake available in this design. An `AgentPort` may sit on the node to preserve the option,
but agent-assisted combination is **advisory alongside, never replacing**.

## ✅ QR-10 — Who owns explainability?

**Origin:** rel1 S3, 2026-08-30 — Victor asked why seats 2 and 3 do not own D-13 when per-domain
attribution was said to live inside each domain. **Status:** ✅ decided 2026-08-30. **Binds:**
`vision.md` §3, §4.2.

**Context.** The seat table implied D-13 was the sole home of explainability; §4.2 said attribution
lives in each domain. Both could not be true — a real inconsistency.

**Decision.** Two different things share the word:

| | Lives | Why there |
|---|---|---|
| **Attribution** — *"what moved MY output"* | inside each analytical seat, as a field on its **own output contract** | ★ Only the module that performed a computation can attribute it. SHAP needs the fitted model; claim→span binding needs the extraction pipeline |
| **Explanation** — *"why THIS recommendation, what would flip it"* | **D-13, seat 6** | It must read **both** analyst views, and seat 6 is the only seat permitted to |

**Rejected:** a single cross-cutting `src/explain/` computing everything. ⚠ It would import D-01 and
D-03 in one module — a firewall breach — and could not work anyway, since attribution requires the
internals of the thing being explained.

★ **The fences caught a design error before any code existed.** Worth keeping for the Phase-4 write-up.

---

# 8. D-14 Evaluation — seat 9

## ✅ QR-3 — Is deliberation acceptable only if measured?

**Origin:** rel1 S1 §D.1; worked through rel1 S3 §I. **Status:** ✅ decided 2026-08-30.
**Binds:** `PG-5.1`, `PG-5.2`.

**Context.** `PG-5` already required measurement — but *"measured"* was ambiguous, and the ambiguity
mattered, because the two available measurements have wildly different costs.

| | Tier A — process | Tier B — outcome |
|---|---|---|
| Question | *reasoning, or theatre?* | *better decisions?* |
| Needs outcomes | ✗ no | yes, resolved |
| Samples | ★ unlimited | ⚠ ~250/yr |
| Time to result | days | ⚠ years |
| Power | ★ adequate | ⚠ weak, possibly never sufficient |

**Options.**

| # | Option | Assessment |
|---|---|---|
| 1 | Strict — gate on Tier B | ✗ **Rejected.** ⚠ At ~250 decisions/yr against a signal at IC 0.0203, t = 1.42, a Tier-B result is a second-order measurement on an unestablished first-order one. **More time does not fix it — noise grows with the sample.** A gate written against it can never open, and would cancel half the portfolio thesis by procedural accident rather than by decision |
| ★ 2 | **Gate on Tier A** | ✅ **Chosen** |
| 3 | No gate | ✗ Rejected — contradicts `PG-5`; the failure modes are **silent** (useless deliberation still produces a convincing transcript) |
| 4 | Tier A + advisory-only until Tier B | ◐ Not chosen, but has a real `PG-2` case. Cost: a deliberation that cannot change anything is arguably not deliberation |

**Decision.** `F6b` graduates when `F7a`'s process-test design exists; `F7b` accrues outcome data and
**never gates**. The Tier-A kill rule is **pre-registered** before the test runs.

⚠ **Amended 2026-09-01 — the kill rule is a pre-registered *analysis plan*, not a threshold.**
A bare number cannot be chosen honestly before the data exists, and chosen after it, it is chosen to
pass. `F7a` `CT-7a.2` now fixes the null, the statistic, α, power, δ and **bands**
(`KEEP` / `ADVISORY_ONLY` / `DELETE`); `min_n_per_arm` falls out of a power calculation.
★ **The verdict kills on *failure to reject*, so an underpowered run returns `INSUFFICIENT`, never
`DELETE`** (`AC-7a.11`). This removed the blocker without weakening the gate.

⚠ **Hard condition, binding immediately (`PG-5.2`):** persist the pre-deliberation verdict alongside
the post-deliberation verdict **from the first run**. Near-free now; **the counterfactual arm is
unrecoverable if skipped**, and Tier B becomes impossible even once samples accumulate.

## ✅ QR-13 — `src/evaluation/` is spec-governed

**Origin:** `L4-target-structure.md` S-1. **Status:** ✅ decided 2026-08-30.
**Binds:** `ownership.yaml` (globs added with `F5`) · `vision.md` §4.1 `F5`.

**Context.** D-14 inherits the D-10 *structural* shape — imports anything, imported by nothing
(`ST-2`) — and D-10 is `P7`-exempt from spec rigor. The question was whether D-14 inherits the
exemption along with the shape.

**Decision.** **No — D-14 is spec-governed.** The structural rule and the spec exemption are separable,
and only the first should be inherited.

### The trade-off, recorded

| | ★ Spec-governed *(chosen)* | Gate-exempt |
|---|---|---|
| **Correctness of the instrument** | ★★ ACs force the metric definitions to be pinned. ⚠ *A measurement instrument nobody verified is how you get confidently wrong numbers* | Nothing checks the checker |
| **Blast radius when wrong** | Contained | ⚠⚠ **`PG-4` makes this the shared substrate of both portfolio lanes.** A bug here is wrong in *both* — and silently |
| **Gating integrity** | `F7a` gates `F6b`; a spec'd gate means the gate itself is tested | ⚠ A harness bug can **silently un-gate** a capability |
| **Subtle-maths exposure** | ★ ECE binning, calibration, IC standard errors — `QR-5` is proof this class of error is live here | Highest-risk code with the least scrutiny |
| **The portfolio claim** | ★ *"my evaluation harness is itself specified and tested"* is the pitch | ⚠ *"my eval harness is unspecified"* undercuts the entire evaluation-discipline story |
| **Speed of exploration** | ⚠ Slower — spec first, `PreToolUse` friction on every edit | ★ Fast; churn freely |
| **Fit to early churn** | ⚠ Specs written before the shape settles get rewritten | ★ `P7` exists precisely for this |
| **Process overhead, solo project** | ⚠ Real | ★ None |

**Why the balance falls this way.** The exemption exists to protect *exploration*. This harness is not
exploration — it is **an instrument other decisions depend on**. `F7a`'s output gates `F6b`; the
calibration numbers back the central portfolio claim. Under `PG-4` an error here is wrong twice over,
and invisibly.

### ⚠ The boundary that still needs drawing

The counter-arguments are real for *part* of the directory. A refinement to consider when `F5` is
written — flagged, not decided:

| Sub-part | Suggested treatment |
|---|---|
| **Metric implementations** — calibration, ECE, IC and its standard error, citation rate, faithfulness | ★ **spec'd** — these are instruments others depend on |
| **One-off studies and sweeps** — an exploratory analysis, a parameter scan | ◐ arguably `P7`-exempt, like D-10 |

★ That split mirrors the existing D-03 / D-10 boundary rather than inventing a new rule.

---

# 9. D-09 Reporting — seat 8

## ✅ QR-16 — What the pipeline produces when asked about a name that is not the top-1

**Origin:** rel1 S4 discussion, 2026-08-30. **Status:** ✅ decided 2026-08-30 — ⚠ *interpretation of
Victor's instruction; confirm at spec time.* **Binds:** `F8` · `F9` acceptance criteria.

> ⚠⚠ **Reframed 2026-08-30.** This entry previously asked *"is a drill-down card actionable or
> informational?"* ★ **Victor rejected that framing: it poses a cheap binary, and the earlier note
> suggesting comparative attribution as a substitute was proposing a fobbed-off answer.**
> *"I don't like cheap answer; pipeline should give a proper answer."*

**Decision.** When the fund manager asks about a name outside the top-1, the pipeline runs the
**full analysis path for that name — the same depth, the same rigour and the same artifacts as the
top-1 receives.** Not a stub, not a comparative summary, not a downgraded card.

### Why this is the right call, not merely the instructed one

- ★ **A ranked list the manager cannot interrogate is an oracle, not decision support.** The whole
  premise (`vision.md` §1) is that this system supports a human decision. Refusing depth at exactly
  the moment he disagrees inverts that.
- **The cost objection does not survive measurement.** A cached deep analysis is order-$0.20, halved
  again by batch (`QR-20`). Rationing analysis at that price to save a human's own money is a
  false economy.
- ★ **Effort scales with genuine interest.** He only asks when he cares, so the expensive path runs
  rarely and for a reason — which is exactly when it is worth paying for.

### ⚠ What this does NOT do — the `INV-6` relationship

`INV-6` permits exactly **one actionable recommendation per day**. A full-depth analysis of a second
name does not create a second one:

> ★ **The count stays one. The fund manager designates *which* analysis is the day's actionable
> recommendation, and the designation is recorded in the decision journal (D-11).**

`INV-6` is preserved as written — exactly one actionable rec — while the manager, who holds sole
decision authority (seat 1), chooses which name it attaches to. **No cheap answer, no amendment, and
the discipline stays visible** because the substitution is journaled rather than silent.

⚠ **The relay's de-rating still applies on its own terms** (upstream RA-67, AC-1.8): if the analysis
arrives through the relay rather than the API, its coverage-derived confidence governs, exactly as it
does for the top-1. Provenance changes the confidence; **it does not change the depth of work done.**

### ⚠ The hazard to keep visible, without letting it dictate the design

`INV-6` is a curb on over-trading, and *"what about the others?"* is sometimes curiosity and sometimes
shopping for a recommendation you like better. The system cannot tell the difference — **so it should
not try to.** It records instead: the ask, the rank the name held, and the designation if one is made.
★ Over a year that is behavioural data about the manager's own discipline, which is more useful than a
guardrail that would have blocked a legitimate question.

**Comparative explainability (`D-13`) is an addition, not a substitute** — it belongs on the page
alongside a full analysis, answering *"why was #1 ranked above this one"*. ⚠ It was wrong to offer it
as a way to avoid doing the work.

---

# 10. ⬆ Upstream — owned in `ai-investment-pipeline`

These block or shape this repo but are **not ours to change** until absorption (`vision.md` §2).
Referenced by their upstream IDs; **not renumbered**.

| Upstream ID | Question | Why it matters here |
|---|---|---|
| **AB-12** | The IC gate's standard error | ★ = QR-5. **Decided here; upstream edit pending** |
| **AB-1** | `evidence_coverage` never computed, so confidence is declared unmeasured | Blocks `F4`. ⚠ Note the trap: once coverage becomes real, `CONFIDENCE_FLOOR` becomes *reachable* and will start firing — that is the mechanism working, not a regression |
| **AB-2** | Claim-binding does not run on the judgement narrative | ★ **Highest value-per-unit-work item in the xAI lane** — the machinery is built, tested, exported and never called |
| **AB-3** | Canadian listings and CDRs are not priced | Keeps the daily card non-actionable. A subscription boundary, not a bug |
| **AB-5** | D-10 unspecified and unbuilt | Precedent for `PG-1` |
| **AB-25** | Four decisions postponed 2026-08-28 | Unreviewed here |

---

# 11. How to use this register

- **Adding a question?** Claim the next free `QR-n`, put it in the right module section, add a row to
  §1. A question with no module goes in §2 platform-wide.
- **Answering one?** Record the options **including those rejected and why**, the decision, and
  ★ **where it binds**. Then write the rule in that binding location — not here.
- **Superseding one?** Strike it through; never delete. The reasoning that turned out wrong is often
  more useful later than the reasoning that held.
- ⚠ **Never let this file become the authority.** It records *why*. `constitution.md` and the specs
  record *what*.
