# Project Vision — Collective Investment AI Assistant

> **Status:** Living · **Adopted:** 2026-08-30 · **Tier:** authoritative, **release-independent**.
> **Read this first.** [`constitution.md`](constitution.md) says *how* to build; this says *what* is
> being built and *why*. Neither overrides the other.
> **Audience:** the AI agent proposing, designing or reviewing work — and any future reader who needs
> the goal without reading a release brainstorm.
> **Source:** derived 2026-08-30 from `../../../ai-investment-pipeline/sdd/specs/vision.md` with
> substantial revision — the dual purpose (§1), the platform capabilities (§4), the nine-seat model
> (§3), and the scalability axes (§6) are new. Decisions recorded in
> [`../design/rel1_brainstorm.md`](../design/rel1_brainstorm.md) rel1 S1–S3.

---

# 1. What this project is

**A single-machine investment analysis platform that can explain and defend every recommendation it
makes — and measure whether any part of it actually helps.**

It takes on the roles of a professional stock-investment fund — research, thesis authoring, valuation,
quantitative ranking, risk, portfolio construction, record-keeping — to **support one human's
decision-making as fund manager**.

It is **not** a "tell me what to buy" machine. Ranking was never the scarce resource. The scarce
resource is **process**: the part of a fund that sits between the idea and the click, and that manages
or exits a position by rule rather than by feeling.

## 1.1 Two purposes, in a deliberate order

| # | Purpose | Measured by |
|---|---|---|
| **1** | **A real investment tool.** Produce analysis the fund manager acts on with his own capital. | Whether he acts on it, and whether the reasoning survives review months later |
| **2** | **A career portfolio piece.** Demonstrate AI-engineering and architecture competence for a role transition around **May–June 2027**. | Whether it survives the question *"does it work?"* — by measurement, not assertion |

> ⚠ **`PG-2`: where the two conflict on anything that touches a number someone would trade on,
> purpose 1 wins.** A feature that improves the demo and degrades the analysis is a **defect**, not a
> trade-off to be balanced. The reverse — analysis-improving, demo-neutral — needs no justification.

**The portfolio thesis, in one sentence:**

> *"I built a system whose every recommendation can be explained and defended — including the parts
> produced by agents — and I can measure whether any of it actually helps."*

Two demonstrations of equal weight (rel1 S1): **explainability** and **agents, measured**. They share
one substrate — the evaluation harness (`PG-4`) — which is what makes a dual pitch coherent rather
than a split focus.

## 1.2 What purpose 2 actually demands

Not a demo. **Evidence of architectural judgement**: industry-standard patterns applied deliberately,
boundaries that hold under change, and decisions recorded with the alternatives that were rejected.
The specs are as much the artifact as the code.

---

# 2. This is a multi-year platform, not a release

Assume every structure here is **extended, not finished**. The measure of success for the architecture
is not that it is complete — it is that **the next sophisticated module can be added without rewriting
the platform**.

⚠ **This repo will absorb `../ai-investment-pipeline` and retire it.**

```text
   TODAY                        THEN                       FINALLY
   ─────                        ────                       ───────
   platform layers here         copy the pipeline's        ai-investment-pipeline
   · imports the pipeline       src/** tree in as a          is RETIRED
     as a dependency            MERGE, not a restructuring
```

★ **Binding consequence (`PG-8`):** this repo's tree must be a **superset** of the pipeline's from day
one. Every inherited domain keeps its upstream path so the absorption is a merge with no import
rewriting. Target tree:
[`../design/rel1_design/L4-target-structure.md`](../design/rel1_design/L4-target-structure.md).

⚠ Until absorption, the pipeline repo remains authoritative for its own domains. Inherited analytical
logic changes **there**, not here.

---

# 3. The fund model — nine seats

A professional fund separates seats so the *decider* is not the *idea-generator* or the *book-keeper*.
That separation removes bias, and it is reproduced here deliberately.

> ⚠ **This repo's seat numbering is its own.** Upstream `L0` §1.5 numbers 1–5; this file numbers 1–9.
> Never cite a seat number across repos without saying which model it belongs to.

| # | Seat | Held by | Owns | Authority |
|---|---|---|---|---|
| **1** | **Fund PM & Trader** | ★ **Human** | *nothing* — no domain, no agent, no module | ★ **the only decision authority** |
| 2 | **Fundamental Analyst** | AI | D-01 `src/fundamental/` | RECOMMEND |
| 3 | **Quantitative Analyst** | AI | D-03 `src/quant/` · D-04 `src/models/` | RECOMMEND |
| 4 | **Risk Management** | AI | D-05 `src/risk/` | ALERT — *sees everything, decides nothing* |
| 5 | **Portfolio Strategy** | AI | D-06 `src/portfolio/` | RECOMMEND — arithmetic only, never an allocation |
| 6 | **Decision Mediator** | AI | D-12 `src/decision/` · **D-13** `src/explain/` | RECOMMEND — *composes; originates nothing* |
| 7 | **Orchestrator** | AI | D-08 `src/orchestration/` | AUTONOMOUS for control flow · ★ **zero analytical authority** |
| 8 | **Back Office** | AI | D-07 `src/data_engine/` · D-02 `src/feature_engineer/` · D-09 `src/reporting/` · D-11 `src/recording/` | split — recording AUTONOMOUS, reporting RECOMMEND |
| 9 | **Experiments** | AI | D-10 `src/experiments/` · **D-14** `src/evaluation/` | none — research, `P7`-exempt |

**Cross-cutting, no seat:** D-00 `src/shared/` — the SPI registry, the agent protocol, the LLM gateway,
money, errors. It serves every seat and belongs to none.

> ★★ **Explainability is not owned solely by seat 6, and the table above would mislead without this
> note.** Two different things carry the same word:
>
> | | Where it lives | Why there |
> |---|---|---|
> | **Attribution** — *"what moved MY output"* | ⚠ **inside each analytical seat** (2, 3, 4, 5), shipped as a field on that domain's own **output contract** | ★ **Only the module that performed a computation can attribute it.** SHAP needs the fitted model; claim→span binding needs the extraction pipeline. Attribution cannot be computed from outside the thing being explained |
> | **Explanation** — *"why THIS recommendation, and what would flip it"* | **D-13, seat 6** | It must read **both** analyst views to compare them — and seat 6 is the only seat permitted to (§3.2) |
>
> So seats 2 and 3 do not *own* D-13; they carry an **obligation** that D-13 consumes. `D-13` composes
> already-published attributions into a cross-view account. It never recomputes them, and it never sees
> in-progress analysis.

## 3.1 Authority levels

| Level | Meaning | Examples |
|---|---|---|
| **AUTONOMOUS** | acts without approval | fetch data, compute metrics, reconcile, record, run the schedule |
| **RECOMMEND** | suggests; the human decides | verdicts, sizing suggestions, **any report** |
| **ALERT** | warns; the human must act | risk breach, data-quality failure, contradictory signals |
| ⛔ **BLOCKED** | can never do | execute trades, move money, alter guardrails, suppress alerts, delete audit trail |

★ **A report is RECOMMEND, not AUTONOMOUS.** It carries a verdict, a stop and a target, and is read as
advice. **The dividing line is whether a human could act on the output** — writing a trade to the log
is autonomous; writing a brief about it is not.

## 3.2 The structural fences

| Fence | Rule |
|---|---|
| **Analyst firewall** | ★ Seats **2 and 3 reach their views independently.** Neither consumes the other's *conclusion*; both freely consume the same *data* and the same *computed numbers* from seat 8 |
| **Seat 6 is the only convergence point** | The Decision Mediator is the sole seat that sees both analyst conclusions. Neither analyst may import it |
| **Seat 4 inverts the rule** | Risk *must* see everything — which is safe precisely because it holds **zero authority**: it can make a risk visible and can never act on it |
| **Seat 7 carries, never computes** | The Orchestrator invokes, routes, budgets and traces. ⚠ It must never decide *what the answer is* — a conditional edge may choose which node runs next, never compute a verdict |
| **Seat 9 is one-way** | Experiments may import any domain; **nothing imports Experiments** |

## 3.3 Why the AI is not the PM

The line between the human and the AI is **authority and accountability, not capability**. The AI may
*support* PM work — sizing math, exposure, scenario arithmetic — but never holds PM *authority*.
Accountability cannot be outsourced to a stochastic model.

- The AI advises, computes and records. It never commits capital and never auto-executes.
- When the human overrides a discipline flag, the AI's job is to make that override **visible and
  logged** — never to block it.
- **Seat 1 has no agent, no domain and no module.** Nothing here is built to occupy or stand in for
  the human decision seat.

## 3.4 What changed from the inherited five-seat model

| Change | Rationale |
|---|---|
| Portfolio Strategy split out of Risk (now seat 5) | Risk **measures** exposure; Portfolio Strategy **sizes** a position. Different questions, different failure modes |
| Decision Mediator promoted to its own seat (6) | It is the only convergence point of the firewall. Burying it in the back office understated a load-bearing boundary |
| Orchestrator promoted to its own seat (7) | ★ Control flow is now a first-class concern (agents, routing, resumable runs). It gets a seat **and explicitly no analytical authority** |
| Experiments promoted to its own seat (9) | It has a distinct import rule and is spec-exempt. A seat makes that visible |
| Back Office narrowed to 4 domains (8) | It is now the neutral-infrastructure seat only |

---

# 4. The platform capabilities

These are what purpose 2 exists to demonstrate and what purpose 1 benefits from. Each is a *capability
of the platform*, not a feature of the investment strategy.

| # | Capability | What it means | Seat / domain |
|---|---|---|---|
| **C1** | ★ **Plugin architecture (SPI)** | One registry keyed by `(port, variant)`. Any module replaceable by another honouring the same contract, selected by config or at runtime. Ports & adapters, dependency inversion, contract tests | D-00 |
| **C2** | ★ **Interactive agents** | Two mechanisms: **(a) configuration influence** — one agent's output selects another's variant/model/horizon, mediated by the orchestrator, deterministic; **(b) argumentation** — typed messages, turn budget, termination | 7 · 2 · 3 · 4 |
| **C3** | ★ **Explainable AI** | Attribution for the ranker, claim→evidence-span binding for the LLM, counterfactuals, calibrated confidence | 6 (D-13) |
| **C4** | **Orchestrator** | Graph topology, scheduling, retries, budgets, **suspend/resume for human-in-the-loop** | 7 |
| **C5** | **Control plane** | ★ Split in two: the **machine-side** half (routing functions, variant selection) and the **human-side** half (directives, drill-down requests, resume signals) | 7 |
| **C6** | ★★ **Evaluation & measurement** | Golden sets, citation and grounding rates, calibration, faithfulness tests, regression on prompt change, efficacy studies. ⚠ **Without this, C1–C5 cannot be shown to work** | 9 (D-14) |
| **C7** | **Observability — trace, replay, audit** | Every routing decision with its reason, every message, every tool call and response, model ids, prompt versions, input hashes. The substrate all others stand on | 7 |
| **C8** | **Governance & reproducibility** | Provenance on every output, versioned implementations, promotion gates, the ability to answer *"which implementation produced this recommendation?"* | 7 · 9 |
| **C9** | **Cost & budget control** | Model tiering, prompt caching, batch execution, per-run budgets, cheap-tier detectors escalating to expensive analysis | 7 · D-00 |

> ★ **C6 and C7 were not in the original feature list and are the two that most change the outcome.**
> C7 is what makes C2 and C4 auditable; C6 is what turns every other capability from a demonstration
> into a result. Both are cheap to build early and impossible to retrofit onto history that was never
> recorded.

## 4.1 Spec registry

`F<n>` IDs are claimed here and **never renumbered**.

| ID | Spec | Cap. | Home | Status |
|---|---|---|---|---|
| **F1** | Module protocol & registry (SPI) | C1 | D-00 | 🔵 idea |
| **F2** | Execution trace & replay | C7 | 7 | 🔵 idea |
| **F3** | Corporate-action resolution agent | C2 | 8 (D-07) | 🔵 idea |
| **F4** | Explainability contract | C3 | 6 (D-13) | 🔵 idea |
| **F5** | Evaluation harness | C6 | 9 (D-14) | 🔵 idea |
| **F6a** | Config-influence routing | C2·C5 | 7 | 🔵 idea |
| **F6b** | Inter-agent messaging & deliberation | C2 | 7 | 🔵 idea — ★ **gated on `F7a`** (`PG-5.1`) |
| **F7a** | ★ **Deliberation process tests (Tier A)** — capitulation on false challenges, effect size, direction, order-dependence, information content, termination, cost | C6 | 9 | 🔵 idea — **gates `F6b`** |
| **F7b** | Deliberation outcome study (Tier B) — calibration and hit-rate against resolved outcomes | C6 | 9 | 🔵 idea — accrues, **never gates** |
| **F8** | Human control surface — API, directives, drill-down, resume | C5·C4 | 7 | 🔵 idea |
| **F9** | Thesis source port — API and relay adapters behind one contract | C1·C8 | 2 | 🔵 idea |
| F10+ | *reserved* | — | — | — |

★ **F1 + F2 + F3 is a coherent release on its own** — and would still interview well if nothing after
it landed.

## 4.2 The two new domains

**D-13 Explainability — `src/explain/`, seat 6.** Owns **cross-view explanation only** (see §3's note):
the comparative account of why one name over another, the counterfactual that would flip the verdict,
and the assembly of per-domain attributions into one page.

⚠ It does **not** own attribution. A single module computing both the fundamental and the quant
attributions would have to import D-01 and D-03 together, breaching the firewall — and could not do it
anyway, since attribution requires the fitted model and the extraction pipeline. **Each analytical seat
attributes its own output through its own contract; D-13 consumes those published outputs and never
sees in-progress analysis.**

**D-14 Evaluation — `src/evaluation/`, seat 9.**
It must import many domains and be imported by none — which is exactly seat 9's existing one-way rule.
No new structural rule is needed.

---

# 5. Architecture principles

The architecture is a deliverable, not an implementation detail (§1.2).

| | Principle |
|---|---|
| **A1** | **Industry-standard patterns, named and applied deliberately** — ports & adapters (hexagonal), dependency inversion, Strategy, service-provider interface, contract tests. Not invented vocabulary |
| **A2** | ★ **Dependency direction is inward.** Domain logic imports ports; adapters implement them. Domain code never imports an SDK |
| **A3** | ★ **Contracts are semantic, not syntactic.** A port states what every implementation must *guarantee*, and one contract-test suite runs against all of them. A satisfied type signature is not substitutability |
| **A4** | **Abstraction is earned.** A port exists where a second implementation is real or contractually promised — not speculatively |
| **A5** | ★ **The control plane stays deterministic.** Judgement lives in agents, where it is bounded and checkable. Routing is a pure function with a recorded reason |
| **A6** | **Every boundary is observable.** If a decision crosses a module boundary, it is traced with enough state to replay it |
| **A7** | **Fail loud, never silent.** A degraded input raises; it never emits a plausible-looking default |
| **A8** | **Frameworks are confined.** Any third-party orchestration framework is imported by one directory and enforced by CI. Abandoning it must cost one rewrite, not a migration |

---

# 6. How this scales — two axes

Expansion is expected along two independent axes. **The architecture's job is to make both cheap.**

```text
   ▲ VERTICAL — depth
   │   improving an EXISTING module with more
   │   sophisticated maths, logic and algorithms
   │
   │   · a stronger DCF · CPCV over a naive split
   │   · a richer verdict algebra
   │   · a second implementation behind the same
   │     port, chosen by config  (LightGBM ↔ EBM,
   │     scorecard ↔ LLM-reasoning, API ↔ relay)
   │
   │
   │
   └──────────────────────────────────────────────────▶
        HORIZONTAL — breadth
        ADDITIONAL modules, features, domains, seats
        · macro & regime · execution support
        · tax & registered accounts · attribution
```

| Axis | What grows | What must not break | Enabled by |
|---|---|---|---|
| **Horizontal** | count of modules / domains / seats | existing import fences; the seat model | the seat structure, `ownership.yaml` |
| **Vertical** | sophistication *within* a module — including **swapping in a better implementation** behind the same contract | the module's **published contract** | `C1` the SPI registry · `A3` contract tests |

> ★ **Substitution is a vertical move, not a third axis.** Replacing LightGBM with an EBM, or the API
> thesis source with the relay, does not add a capability — it makes an existing one better or
> different behind an unchanged contract. That is why `C1` (the registry) and `A3` (contract tests) are
> the enablers of the vertical axis: **they are what let a module be improved without the callers
> knowing.**

★ **The test of the architecture is a question, not a diagram:** *can a new module be added, or an
existing one deepened or swapped, without rewriting the platform?* If the answer is no on either axis,
that is a defect in the architecture — not a feature request.

---

# 7. Durable non-goals

- **No AI decision authority.** Verdicts gate; they never decide, and never upgrade a signal.
- **No automatic execution.** No path from a report to a broker order, ever.
- **No AI in deterministic math.** Risk metrics, feature formulas, P&L stay plain code. ★ The rule is
  **no arithmetic inside a prompt** — an LLM never does the multiplication.
- ★ **No non-deterministic control plane.** Routing and orchestration stay deterministic and replayable.
  A learned or LLM policy in the control plane is out of scope, with the reversal conditions written
  down (see the lecture, §2.8).
- **No hot reload.** Variants are selected at load or run time from a registry; the process does not
  swap code while running.
- **Not a general-purpose research tool.** Research is spec-exempt and stays separated from production;
  promotion requires a spec.
- **No retro-speccing inherited code.** Characterization tests and reality probes instead.

---

# 8. Open questions and decisions

★ **Every question this project has faced — answered and open — is tracked in one place:
[`../questions.md`](../questions.md)**, the question register. It carries the origin, the context, the
options **including those rejected and why**, and a pointer to where each answer binds. Questions are
categorised by module.

⚠ **This file does not duplicate it.** A decision's *rule* lives in [`constitution.md`](constitution.md)
or in the governing spec; its *reasoning* lives in the register. Restating either here would create the
second source of truth that `../README.md` forbids.

**The mandate is deliberately absent from this file.** Investment posture — risk appetite, instrument
exclusions, concentration policy, account constraints, base currency — is **release-scoped** and varies
between releases. It belongs in the design tier for the release that adopts it, not in a
release-independent vision. ⚠ A proposal must still respect the mandate in force; it is simply not
defined *here*.

---

# 9. How to use this file

- **Proposing or brainstorming?** Start here, then `../design/rel<N>_brainstorm.md`. A proposal that
  serves no capability in §4, or contradicts §5 or §7, is out of scope — say so rather than building it.
- **Implementing?** This file binds nothing directly. Go to [`constitution.md`](constitution.md) and the
  governing spec. ⚠ **`PG-1` blocks implementation** until the inherited pipeline completes a verified
  end-to-end run; it does **not** block spec-writing.
- **Amending?** The seats (§3), the capabilities (§4) and the non-goals (§7) change only when the fund
  manager says so, and the change lands **here first**. The spec registry (§4.1) is expected to churn.

> ★★ **The single most valuable property this project already has is the willingness to refuse its own
> model.** The inherited record shows a walk-forward IC of 0.0203 at *t* = 1.42 and declines promotion,
> noting: *"A signal that passed would not have been shown to work."* **Nothing in this repo may erode
> that instinct.** It is the portfolio.
