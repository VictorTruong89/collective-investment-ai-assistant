# Release 1 — Feature Design & Brainstorm

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** This is the brainstorm / rationale /
> decision log, not a contract. **Do not code from this file.** Ideas here *graduate* into
> `../specs/F<n>_<slug>/spec.md` once their acceptance criteria can be written.
>
> **Status:** OPEN · **Opened:** 2026-08-28 · **Previous release:** none (first release)
> This is a *living* doc — each brainstorm session appends to it.

---

## Release goal

Decide whether, and in what form, the `ai-investment-pipeline` should be extended into a
**pluggable-agent platform with inter-agent communication**, serving a dual purpose:
investment capability, and an AI-engineering portfolio for a role transition around
**May–June 2027 (~8 months)**.

This release produces **decisions and specs**, not code.

---

## Discussion log

> ⚠ **Note added 2026-08-30:** `prompt.md` and `chat-AI.Code.Specs.Guide-20260828.md` — cited
> throughout Session 1 below — **were deleted from the repo on 2026-08-30.** They were written by an
> agent with no access to the actual pipeline, served only the first prompt, and carried invented seat
> numbers and domain structure. **The references below are left unedited as a historical record of
> what Session 1 was reacting to.** Nothing in `sdd/specs/` derives from them; the seat model, the
> capabilities and the architecture come from Victor's direction and from the live pipeline repo.

### 2026-08-28 — Session 1: Independent evaluation of the agent-platform pivot

**Trigger:** `prompt.md` proposes the pivot (LangGraph, `AgentPort`, deliberation,
four layers of pluggability, INV-014 relaxation). Victor asked for an *independent*
evaluation — including whether the plan is realistically beneficial — plus a new topic
not yet in `prompt.md`: **explainable AI (xAI)** in the recommendation path.

---

## A. The evaluation — measured against what actually exists

### A.1 What the existing system actually is (verified 2026-08-28)

| Fact | Measurement | Source |
|---|---|---|
| Code in the rewritten tree | **34,723 LOC**, 294 files, 13 domains under `src/` | file count |
| Test suite | **1,192 passing**, 9 skipped, 11.8 s | `pytest tests/ tests_src/` |
| Spec corpus | ~30 L-tier documents, an enforced `PreToolUse` gate, `ownership.yaml` | `sdd/` |
| **Walk-forward IC** (500 names, 10y, 5 folds, purge 63d, embargo 5d) | **0.0203** | L6 §7 |
| — `t` on the **null** SE | 4.94 → gate PASS | L6 §7 |
| — `t` on the **realised** dispersion | **1.42 → fail** | L6 §7 |
| Model promoted? | ⚠ **No.** Gates refused it. | L6 §7 |
| Portfolio sim excess, annualised | +10.35 % — *self-flagged as survivorship-flattered, concentrated, under-costed* | L6 §7 |
| End-to-end verified production run | ⚠ **Has not happened yet** | HEAD commit message |

★★ **The single most important sentence in the entire repo is in L6 §7:**
*"A signal that passed would not have been shown to work."* A system whose author refuses
to promote his own model, and writes down why, is displaying something rarer in this job
market than any framework on a CV.

### A.2 ⚠⚠ The honest answer to "is this beneficial?"

**Split verdict. The pivot is directionally right and specifically mis-aimed.**

| | Assessment |
|---|---|
| **Is agentic/pluggable architecture worth building?** | ★ **Yes** — but for about **40 %** of what `prompt.md` proposes, and not as the headline |
| **Will it help the career plan as written?** | ⚠ **Weakly, and with a real downside risk** — see A.3 |
| **Will it help investment capability as written?** | ⚠ **Mostly no.** Layers 2–4 of the pluggability stack and the deliberation subgraph add *demonstrable* complexity, not *analytical* capability |
| **Is there a better version of the same ambition?** | ★★ **Yes — and Victor already named it: xAI.** See §B |

### A.3 ⚠⚠ The career risk, stated plainly

```text
╔══════════════════════════════════════════════════════════════════════╗
║  BY MAY 2027, "I BUILT A MULTI-AGENT SYSTEM WITH LANGGRAPH" IS       ║
║  TABLE STAKES, NOT DIFFERENTIATION.                                  ║
║                                                                      ║
║  Every bootcamp portfolio, every hackathon project and every         ║
║  tutorial-follower will have a LangGraph DAG with agents that pass   ║
║  typed messages. The supply of that artifact is enormous and         ║
║  growing. It is a WEEK of learning presented as eight months of      ║
║  work, and an experienced interviewer knows it.                      ║
║                                                                      ║
║  ★ WHAT IS SCARCE IN 2027:                                          ║
║    · someone who can EVALUATE a non-deterministic system             ║
║    · someone who can EXPLAIN why a model said what it said           ║
║    · someone who ships a system that KNOWS WHAT IT DOESN'T KNOW      ║
║    · someone with real DOMAIN depth + AI (fintech AI is a niche      ║
║      that pays, and is hard to fake)                                 ║
║                                                                      ║
║  ⚠ THE REPO ALREADY HAS ALL FOUR. THE PIVOT AS WRITTEN BURIES       ║
║    THEM UNDER A COMMODITY DEMO.                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

⚠ **A second, sharper risk — the interview question that breaks the demo.** The proposed
5-minute demo is two agents debating whether to buy AAPL. The obvious follow-up from any
competent interviewer is: *"Does it work? What's your edge?"* Today the honest answer is
*"walk-forward IC 0.02, t = 1.42, my own gate refuses to promote it."*

★ That is an **excellent** answer if rigour is the pitch. It is a **damaging** answer if
agent deliberation is the pitch — because it reveals that the elaborate deliberation is
being conducted over a signal not yet distinguishable from noise. **The framing decides
which of the two happens.**

### A.4 ★★ The deliberation-theatre problem — the core technical criticism

```text
   Research agent (LLM) writes a thesis.
   Risk agent (LLM) writes a challenge to the thesis.
   Research agent (LLM) writes a revision.
        ↓
   ⚠ WHERE DID THE NEW INFORMATION COME FROM?
```

If Risk's challenge is *"tech is already 28 % of the portfolio"*, that is **arithmetic**,
and `src/risk/` already computes it deterministically. Wrapping it in a CHALLENGE message
and an LLM-authored rebuttal does not make the position sizing better — it makes the
transcript longer.

⚠ **This collides head-on with the project's own AP-5** (*"do the computation where
computation applies, instead of over-relying on an agentic AI"*) and with the L0 LLM
usage policy (*"✗ portfolio optimization math, ✗ risk calculations"*). The pivot document
resolves that collision by **amending the rules that block it** — INV-014 relaxed, D-12
opened to non-determinism, ST-5 widened, §11.1's no-framework rule reversed.

★★ **That is the finding of this session: the proposal amends away four of the constraints
that make the existing system unusually good, to buy a capability whose value is
demonstrative rather than analytical.** Every one of those amendments is individually
defensible. Together they trade the system's distinguishing property — disciplined
restraint about where non-determinism is allowed — for a feature set that is abundant
elsewhere.

> ★ **This is not an argument against agents. It is an argument for AP-5 applied to
> agency itself:** use an agent where the task requires open-ended interaction with an
> unbounded external world, and deterministic code everywhere else. See §B.2.

---

## B. The reframe — what I recommend instead

### B.1 ★★ Change the headline, keep most of the work

| | Proposed in `prompt.md` | ★ Recommended |
|---|---|---|
| **Headline** | "A pluggable multi-agent investment platform" | **"An investment system that can explain and defend every recommendation it makes — and prove it didn't regress"** |
| **Demo opens with** | two agents debating AAPL | a recommendation, then *"here is every input that moved it, the filing span behind every sentence, and what would have to change to flip it"* |
| **Agents** | the product | ★ a component, used where they earn their place |
| **Scarcity of the skill shown** | ⚠ low and falling | ★ high and rising |
| **Survives "does it work?"** | ⚠ badly | ★ **it is the answer** |

★ **The reframe costs almost nothing.** Most of the proposed engineering still gets built —
`AgentPort`, the registry, the LLM-tier routing, the trace/replay layer, the corporate-action
agent. What changes is **which capability is load-bearing in the story**, and therefore
what gets built *first* and what gets cut if time runs out.

### B.2 ★ The rule that decides where an agent is justified

> **AP-7 (proposed):** *An agent is justified only where the task requires open-ended,
> tool-using interaction with an unbounded external world. Where the inputs are known and
> the computation is definable, write the code.*

Applying it to the existing system:

| Task | Agent justified? | Why |
|---|---|---|
| ★★ **Corporate-action resolution** (delisting vs rename vs merger-of-equals) | ★★ **YES — the strongest case in the system** | The answer is *not in the data* — it is on the internet. Already proven by the EQR/AVB incident and the `ticker-went-silent` skill. Needs web search, source corroboration, structured findings |
| **Filing interpretation / claim extraction** | ★ yes | Unbounded natural-language input, needs judgement |
| **News materiality** | ★ yes | Same |
| **Experiment sweeps** (D-10) | ◐ partially | Tool use over a bounded space; agent adds convenience, not capability |
| **Risk arithmetic, exposure, concentration** | ✗ **no** | `src/risk/` computes it exactly. AP-5 forbids it |
| **Position sizing** | ✗ **no** | Arithmetic from a stop. D-06 already does it |
| **Verdict combination (D-12)** | ✗ **no** — see §D.3 | The current meet-semilattice is *provably* safe |

★ **The corporate-action agent alone is a better portfolio story than the deliberation
subgraph**, because it solves a problem where deterministic code demonstrably failed, with
a measured incident behind it (two of five "delisted" names were still trading; a retired
symbol printing its successor's prices produced a fabricated −2.8 % return no feature could
distinguish from a real one).

### B.3 ★★ xAI — why Victor's new idea is the best one in this session

**This is not a new direction. It is closing gaps the repo's own register already names.**

| Existing gap | Register entry | What it means today |
|---|---|---|
| Confidence is **not measured** — `evidence_coverage` never computed | **AB-1** | AP-1's confidence score is a declared non-number |
| **Claim-binding does not run on the narrative** | **AB-2** | ⚠⚠ *"if the model writes 'NAND margins expanded on HBM demand', nothing checks it against the filing"* — the hallucination guard for prose is built, tested, exported, **and never called** |
| Feature attribution on the ranker | *absent* | A rank_score arrives with no account of what moved it |
| Calibration of stated confidence | *absent* | Nothing checks whether 0.8-confidence calls are right 80 % of the time |

★★ **Three of the four are already built-but-not-wired, or specified-but-unmeasured.** The
xAI lane is therefore *cheaper than it looks* and lands directly on the system's known
weakest seam.

**Why it is the better career bet:**

1. ★ **Scarcity.** Interpretability + evaluation is a harder skill to fake than orchestration,
   and the supply is far smaller.
2. ★★ **Regulatory tailwind.** Financial AI explainability is a live, funded, growing job
   category (model risk management, EU AI Act). "I built explainability into a financial
   recommendation system" is a *sector-specific* claim that maps onto real open roles.
3. ★ **It composes with what exists.** AP-1 (transparency), AP-2 (cited claims only), AP-3
   (adversarial thinking) are *already explainability principles*. The work completes the
   design rather than bolting onto it.
4. ★★ **It is the only lane that improves the investment tool as much as the CV.** An
   unexplainable ranked list is not decision-support for a PM who must own the P&L. A
   recommendation carrying *"this is what moved it, this is the evidence, this is what would
   flip it"* is the difference between a signal and a usable one.

**The three xAI layers, concretely:**

```text
QUANT LAYER — attribution on the ranker
  SHAP / permutation importance per nomination, plus ★ an ATTRIBUTION
  STABILITY check: do the attributions move wildly run-to-run? If yes,
  that is a FINDING about the model, not a display bug.

FUNDAMENTAL LAYER — claim → evidence-span binding  (closes AB-2)
  Every sentence in a thesis traces to a filing span, or is marked
  unbound. The machinery exists in src/fundamental/claims/ and is
  not called.

DECISION LAYER — ★★ counterfactual explanation
  "This is HOLD. It becomes BUY if gross margin holds above 42 % for
   two more quarters, or if the 1m rank enters the top decile."
  ★ This is the single most useful output for a real PM, and the best
    five seconds of any demo.
```

### B.4 ★ The second scarce skill: an evaluation harness

The repo already has a **metric-gate test tier** and an IC gate that *refuses its own
model*. That instinct, pointed at the LLM path, produces the thing almost nobody has:

- a golden set of filings with known-correct extractions
- citation-verification rate as a **tracked metric**, not a hope
- regression tests that fail when a **prompt** changes behaviour
- calibration curves for stated confidence

> ★★ *"I can prove my LLM pipeline didn't regress"* is a rarer sentence in 2027 than
> *"I built agents that talk to each other."* And this repo is three-quarters of the way
> to being able to say it.

---

## C. Sequencing — the part that matters most

⚠ **The binding constraint is not skill or time. It is that the pipeline has never
completed a verified end-to-end run.** Building an agent platform on an unverified
pipeline risks arriving at May 2027 with an elaborate demo over an unproven signal.

★ **Victor's own precedent applies.** AB-5 records his gate for D-10: *"I do not plan to
implement D-10 code until the full pipeline runs stably."* **The same gate should bind the
agent layer.**

| Phase | Window | What lands | Serves |
|---|---|---|---|
| **0 — Close the loop** | ~months 1–2 | Verified E2E daily run · **AB-12 decided** · delivery confirmed · AB-3 priced or scoped out | ★★ investment **and** every later demo |
| **1 — xAI + eval** | ~months 2–4 | Attribution · claim-binding wired (AB-2) · coverage/confidence real (AB-1) · counterfactuals · golden eval set | ★★ **both** — highest scarcity |
| **2 — Agents where earned** | ~months 4–6 | `AgentPort` + registry · **corporate-action agent** · LLM-tier routing · trace/replay | ★ career, ★ real capability |
| **3 — Deliberation, measured** | ~months 6–7 | Research ↔ Risk request/response · **the A/B study (§D.1)** | ★ career |
| **4 — Write-up & polish** | ~months 7–8 | Demo · architecture essay · sanitised public doc | ★★ career |

⚠ **Phase 3 is the first thing cut if Phase 0 or 1 overruns**, and the plan should say so
out loud now, while it is cheap to say.

★ **Note on Phase 4:** the L6 document is better written than most published engineering
blogs. A sanitised public write-up of *"how I built a system that refuses to promote its own
model"* is a disproportionately high-return artifact for the target role, and it costs days,
not months.

---

## D. Specific technical positions on `prompt.md`'s proposals

### D.1 Deliberation — build it, but **measure** it

★★ **The killer version of Scenario A is not "watch them debate."** It is:

> *"Here are 200 historical decisions run with deliberation and without. Here is whether
> deliberation improved calibration, changed conviction, or merely added tokens."*

⚠ **If the answer is "it did not help," publishing that is *more* impressive than a
polished transcript** — it demonstrates exactly the evaluation instinct that is scarce.
This converts the weakest lane into a defensible one, and it is the only framing under
which the deliberation subgraph earns its eight-month slot.

### D.2 ⚠⚠ INV-014 relaxation — the distinction is thinner than it looks

The proposed INV-014a (analytical firewall preserved) / INV-014b (configuration influence
allowed) split is intellectually clean, but:

```text
   ★ CHOOSING A MODEL HORIZON *IS* AN ANALYTICAL CHOICE.

   If the Fundamental agent requests "run the 1-week momentum model
   for this volatile tech name", it has shaped the quant input.
   The two views are then NO LONGER INDEPENDENT — and their
   AGREEMENT NO LONGER MEANS WHAT IT MEANT.

   ⚠ The whole value of the firewall is that concurrence between two
     independent views is INFORMATIVE. Cross-configuration quietly
     converts concurrence into an echo.
```

**Recommended constraint if INV-014b is adopted:** every cross-configuration request is
**recorded on the nomination**, and any decision where one seat configured the other is
**bucketed separately in evaluation**. The combined verdict may never claim *"two
independent views agree"* when one configured the other. ★ Stating this makes the
relaxation safe *and* is itself a strong piece of design reasoning to show an interviewer.

### D.3 ✗ D-12 should stay deterministic

The current verdict algebra is a **bounded meet-semilattice** — *"verdicts gate, never
upgrade"* is a **structural** guarantee, not a runtime check. Replacing it with a learned or
LLM-assisted combiner discards a provable safety property for an unmeasurable one, at the
exact point where the system's output becomes an action.

★ **Recommendation:** keep D-12 deterministic. Implement `AgentPort` on the node (cheap,
preserves the option) but any agent-assisted combination must be **advisory alongside**, never
replacing. ⚠ An unfalsifiable combination rule at the decision point is the single most
expensive mistake available in this design.

### D.4 ◐ LangGraph — a reasonable choice, wrongly weighted

| | |
|---|---|
| ★ **Real wins** | checkpoint/replay, human-in-the-loop interrupts, conditional routing, and — honestly — **recruiter keyword signal** |
| ⚠ **Real costs** | a large dependency tree, and abstractions that can obscure the clean architecture already built |
| ★ **Correct mitigation** | *`prompt.md` already gets this right*: LangGraph confined to D-08; agents stay plain Python behind `AgentPort`; ST-5 preserved |
| ⚠ **Wrong weighting** | LangGraph is **~a week to learn**. It should not be the architectural centrepiece of an eight-month plan |
| ★ **Worth watching** | by 2027, **MCP** fluency and eval tooling may signal more than any single orchestration framework |

### D.5 Pluggability — keep Layers 1–4; cut only *hot reload*

> ⚠⚠ **CORRECTED 2026-08-29 (S2).** The original version of this table cut "Layer 4"
> and deferred Layer 2. **Both verdicts were wrong, and the Layer-4 one rested on a
> conflation.** See §H.2 — `prompt.md` uses "Layer 4" for **dynamic selection**
> (the orchestrator picks a variant per ticker) while its Question-3 "Interpretation D"
> means **hot reload without restart**. These are different features with different
> costs. I cut the cheap, load-bearing one by name-collision. Original verdicts struck
> through below.

| Layer | Verdict |
|---|---|
| **1 — LLM tier swap** (Opus/Sonnet/Haiku) | ★ **Keep.** Already nearly there via the gateway; real cost savings |
| **2 — Config / personality variants** (growth vs value) | ★★ **Keep** ~~defer~~. ⚠ **It is load-bearing for Feature 2**: "agent A influences agent B's config" is meaningless if B has no config variants to select among. The original objection — *an unvalidated free parameter on an unpromoted model* — is real but is answered by `PG-5` (measure it) and `PG-7` (record it), not by removing the mechanism |
| **3 — Implementation swap** (`Port` variants via registry) | ★★ **Keep — the genuine architecture story**, and what makes the §D.1 A/B study possible |
| **4 — Dynamic selection** (orchestrator routes per ticker) | ★ **Keep** ~~cut~~. It is a **routing function** — `(features) → variant name` — not a plugin loader. Cheap, deterministic, testable, and it is the *mechanism* Feature 2's config-influence rides on |
| **D — Hot reload without restart** | ✗ **Cut** *(this is what the original row meant to cut)*. Over-engineered for a single-machine, single-user, once-daily batch system. ⚠ An interviewer who knows systems reads it as ornament |

---

## E. What should graduate into `specs/`, and in what order

> Nothing graduates until its acceptance criteria can be written. Proposed order:

| # | Candidate spec | Depends on | Ready to write ACs? |
|---|---|---|---|
| **F1** | Agent protocol & registry (`AgentPort`, capability, versioning) | — | ★ yes |
| **F2** | Execution trace & replay (the observability substrate) | F1 | ★ yes |
| **F3** | Corporate-action resolution agent | F1, F2 | ★ yes — the `ticker-went-silent` skill is most of the spec already |
| **F4** | Explainability contract (attribution + claim-binding + counterfactual) | — | ◐ needs a decision on AB-1/AB-2 first |
| **F5** | LLM evaluation harness (golden set, citation rate, calibration) | F4 | ◐ partially |
| **F6** | Inter-agent messaging & deliberation | F1, F2 | ⚠ **not yet** — blocked on Q3 below |
| **F7** | Deliberation efficacy study (the A/B) | F6 | ✗ later |

★ **F1 + F2 + F3 is a coherent, honest, demonstrable release on its own** — and if the
other eight months went badly, it would still interview well.

---

## Open questions (must be answered before anything graduates)

- **Q1 — ★★ Which repo is the home?** `prompt.md` says *"develop `ai-investment-pipeline`
  into…"*, but this scaffolding sits in `collective-investment-ai-assistant`. Three options:
  (a) extend the existing repo in place; (b) build the agent platform here and import the
  pipeline as a dependency; (c) fork and diverge. ⚠ **This blocks every spec**, because
  `ownership.yaml` globs cannot be written until it is settled. *(a) is lowest-risk for
  investment capability; (b) is the cleanest portfolio artifact.*
- **Q2 — Does Victor accept the reframe in §B.1** (xAI + evaluation as the headline, agents
  as a component), or is multi-agent deliberation the non-negotiable centrepiece?
- **Q3 — Is deliberation acceptable only if measured** (§D.1)? If yes, F6 must not graduate
  before F7's design exists. If no, F6 is demo-only and should be scheduled last and cut first.
- **Q4 — Does Phase 0 gate the rest?** i.e. does *"no agent-layer code until the pipeline
  completes a verified E2E run"* become a binding rule, mirroring AB-5's precedent for D-10?
- **Q5 — AB-12 must be decided regardless.** It is upstream of every claim this system makes
  about its own performance, and therefore upstream of every demo. *(Owned in the pipeline
  repo, not here — but it blocks the story.)*
- **Q6 — Is D-12 agreed to stay deterministic** (§D.3)?
- **Q7 — Are Layers 2 and 4 of pluggability cut** (§D.5)?

---

## F. ★★ Session 1 addendum — why the dual pitch is coherent, not a compromise

Victor chose the **balanced dual pitch** (Q2): explainability *and* deliberation, equal
weight. My §B.1 recommendation was to subordinate deliberation. ⚠ The stated risk of a
dual pitch is that eight months split two ways leaves neither at portfolio depth.

★★ **That risk is avoidable, and the escape is already in §D.1.** The two lanes are not
independent — they share a substrate:

```text
        THE EVALUATION HARNESS IS THE LOAD-BEARING PIECE OF BOTH.

   xAI lane needs it:            "are my explanations faithful?
                                  is stated confidence calibrated?"
   Deliberation lane needs it:   "did deliberation improve calibration,
                                  or merely add tokens?"   (§D.1 A/B)

   ★ ONE harness. TWO headline demos. The A/B study IS the agent demo
     AND an evaluation demo simultaneously.
```

★ **So the unifying claim is not "I built agents" nor "I built explainability."** It is:

> **"I built a system whose every recommendation can be explained and defended — including
> the parts produced by agents — and I can measure whether any of it actually helps."**

⚠ **The dual pitch only holds if the evaluation harness is built once, early, and shared.**
If the two lanes each grow their own ad-hoc measurement code, the split-focus risk becomes
real. **This is now the governing structural constraint on the build order** — recorded as
`PG-4` in the constitution.

## G. ★ Structural findings forced by the "absorb the pipeline" decision (Q1)

Victor's Q1 answer — *build here, import for now, copy `ai-investment-pipeline` over once
stable, then **retire it*** — means this repo's tree must be a **superset** of the
pipeline's, so the eventual copy is a merge and not a restructuring. Two consequences that
are not obvious:

### G.1 ⚠⚠ An "explainability domain" would breach the analyst firewall

A single `src/explain/` that reads both the fundamental thesis and the quant rank_score
would **import D-01 and D-03 in the same module** — exactly what INV-014 / ST-9 forbid.

★ **Resolution: explanation is positioned downstream of the firewall, alongside D-12 and
D-09** — the two places that already legitimately see both views (D-09's `DC-4` renders
them side by side by design). Per-domain attribution stays *inside* each domain and is
exposed as part of that domain's own output contract.

> ★ This is a case where the existing fences caught a design error before any code was
> written. Worth keeping as a worked example for the write-up (Phase 4).

### G.2 ★ The evaluation harness already has a structural home: the D-10 shape

The harness must import many domains and be imported by none — which is **precisely
`ST-2`**, the one-way rule that already holds D-10 Experiments safe without a spec. So the
harness needs no new structural rule; it inherits a proven one.

### G.3 ⚠ ID-family collision hazard

The pipeline carries a large ID space (`P1–P7`, `INV-1..9`, `INV-0nn`, `AP-n`, `ST-n`,
`CA-n`, `DR-n`, `DE-nn`, `RA-nn`, `QA-nn`, `RC-nn`, `MT-nn`, `FE-nn`, `DN-nn`, `CB-nn`,
`BS-nn`, `AB-nn`, `QD-nn`). L0 §5.2 records a real defect from *"two live meanings for one
ID"*. ★ **This repo therefore opens a fresh, non-colliding family — `PG-n` (Platform
Governance) — for its own process rules**, and leaves every inherited family untouched for
the absorption.

---

### 2026-08-29 — Session 2: Spec review against the three intentional features

**Trigger:** Victor named the three features the platform is *for*, and asked whether the
specs actually carry them:

> **1.** pluggable **modules** — swap a module by changing a registry; both sides align to an
> interface / adaptor / template.
> **2.** **interactive** AI/ML agents — one agent's output influences another's **configs and
> model selection**; and two agents can **argue** before a final conclusion.
> **3.** **explainable** AI.

## H. Review findings — coverage is 2 of 3, and one of my own verdicts was wrong

| Feature | Spec that carries it | Verdict |
|---|---|---|
| **1 — pluggable modules** | F1 | ⚠ **PARTIAL — scoped too narrowly.** See §H.1 |
| **2 — interactive agents** | F6 (+ `PG-7`) | ⚠ **PARTIAL — only the "argue" half is specified.** See §H.2 |
| **3 — explainable AI** | F4 | ★ **COVERED.** attribution · claim→span binding · counterfactual, with `D-13` placed downstream of the firewall |

### H.1 ⚠ F1 is *agent*-scoped; Feature 1 is *module*-scoped

F1 as written is `AgentPort` + an **agent** registry. Victor asked for **modules** — which is
strictly broader, and the pipeline already proves the wider need: `DataSourcePort`
(EDGAR/FMP), `RankingModelPort` (LightGBM/XGBoost/CatBoost), `LLMGatewayPort`,
`ReportRendererPort`. ★ **An agent is just one kind of pluggable module.**

**Resolution:** F1 is widened to *"Module protocol & registry"* — one registry keyed by
`(port, variant)`, with `AgentPort` as **one registered port among several**. ⚠ Building an
agent-only registry first would mean writing the same resolution, validation and versioning
logic twice.

### H.2 ⚠⚠ Feature 2 has two mechanisms; I specified one and cut the other's substrate

```text
   FEATURE 2, PART A — CONFIG INFLUENCE
     "Fundamental agent's output selects the 1-week horizon model for Quant"
     → constrained by PG-7 ✅   ... but specified by NOTHING ❌
     → and its substrate (Layers 2 + 4) I had DEFERRED and CUT ❌❌

   FEATURE 2, PART B — ARGUMENTATION
     "two agents argue before concluding"
     → specified by F6 ✅   measured by F7 ✅
```

★ **The two halves have different failure modes and belong in different specs:**

| | Part A — config influence | Part B — argumentation |
|---|---|---|
| Mechanism | a **routing function**, `(features, peer output) → variant` | a **message state machine** with turn budget |
| Determinism | ★ fully deterministic and replayable | ⚠ non-deterministic (LLM in the loop) |
| Main hazard | ⚠⚠ **cycles** (A configures B configures A) and loss of view independence | ⚠⚠ **sycophancy** — the challenged agent capitulates regardless of merit |
| Governing rule | `PG-7` | `PG-5` |

**Resolution:** **F6 splits.** `F6a` — Config-influence routing (Part A). `F6b` —
Inter-agent messaging & deliberation (Part B). ★ F6a is deterministic, cheap, testable,
and unblocked by Q3; F6b remains blocked on Q3.

### H.3 What did not change

★ **F4 covers Feature 3 as asked**, and §G.1's placement of `D-13` downstream of the analyst
firewall stands. **F2 (trace & replay) becomes more load-bearing, not less** — Part A's
routing decisions and Part B's transcripts are both only auditable if the trace records them.

---

### 2026-08-30 — Session 3: `QR-3` (then "V-Q3") worked through

## I. `QR-3` — "is deliberation acceptable only if measured?"

**The question:** may `F6b` (two agents argue) graduate and ship **before** a measurement of whether
deliberation helps exists?

### I.1 Why it is not already answered by `PG-5`

`PG-5` says a demonstration must be measured. That looks decisive until you ask *measured how*, and
the answer splits into two tiers with **completely different costs and completely different power**.

| | **Tier A — process** | **Tier B — outcome** |
|---|---|---|
| Question | *Does deliberation behave like reasoning, or like theatre?* | *Did deliberation make better decisions?* |
| Needs investment outcomes | ✗ **no** | ★ yes, resolved |
| Sample size available | ★ **unlimited** — synthetic + historical inputs | ⚠ ~250 decisions/yr, and only the subset deliberation changed |
| Time to a result | **days** | ⚠ **years** |
| Statistical power | ★ adequate | ⚠ **weak, possibly never sufficient** |
| Catches | ★★ sycophancy · correlated errors · position bias · zero-information exchange | whether it made money |
| Confounded by markets | ✗ no | ⚠⚠ yes — and see below |

⚠⚠ **Tier B inherits the reward-signal problem from §2.8 of the lecture.** The underlying signal is at
walk-forward IC 0.0203, *t* = 1.42 — not yet distinguishable from noise. Measuring whether deliberation
improves a first-order effect that is itself unestablished is a second-order measurement on an
unestablished first-order one. **More time does not fix it; the noise grows with the sample.**

★ **So a gate written against Tier B is not "rigorous" — it is a gate that can never open**, and it
would quietly kill half the portfolio thesis (rel1 S1, Q2) by procedural accident rather than by
decision.

### I.2 What Tier A actually contains

"Measurement design exists" must mean something concrete. It means these:

| # | Test | What a bad result looks like |
|---|---|---|
| **T1** | ★★ **Sycophancy / capitulation.** Run the same decisions twice — once with *valid* risk challenges, once with challenges that are **deliberately false** (a concentration figure that is wrong, an exposure that does not exist). Compare revision rates | ⚠ **revision rate on bogus ≈ revision rate on valid** ⇒ deliberation transfers social pressure, not evidence |
| **T2** | **Effect size.** How often does deliberation change the verdict, the conviction, or the size at all? | Changes nothing ⇒ expensive no-op. Changes almost everything ⇒ the first pass was worthless |
| **T3** | **Direction.** Does it only ever soften (consistent with `P3`), or does it sometimes escalate? | Escalation ⇒ a `P3` breach in a new surface |
| **T4** | **Order dependence.** Randomise which agent speaks first; does the outcome follow the order? | Outcome tracks speaking order ⇒ you are measuring the protocol, not the question |
| **T5** | **Information content.** What fraction of challenges cite a *checkable* fact the other side demonstrably lacked, versus restating what it already had? | Mostly restatement ⇒ no asymmetry, so no reason to expect gain (lecture §2.6) |
| **T6** | **Termination behaviour.** Convergence rate, escalation rate, turn distribution against budget | Never escalates ⇒ it is papering over genuine disagreement |
| **T7** | **Cost.** Tokens and dollars per deliberation, versus the single-pass baseline | — |

★ **Every one of these runs without a single resolved investment outcome**, on as many synthetic or
historical inputs as you care to generate. `T1` alone is the cheapest high-value experiment in the
whole project and it directly targets the documented failure mode.

### I.3 The options

| | Gate | Consequence |
|---|---|---|
| **1** | **Strict — Tier B.** No graduation until outcome measurement exists | ⚠ **blocks `F6b` for years, probably forever.** Maximally rigorous on paper; in practice deletes half the thesis without deciding to |
| ★ **2** | **Tier A.** `F6b` graduates when the Tier-A design exists; Tier B accrues but never gates | Cheap, fast, adequate power, catches the real failure modes, keeps the thesis intact |
| **3** | **None.** Ship it; measure later if convenient | ⚠ contradicts `PG-5`; failure modes are **silent** — deliberation that helps nothing still produces a convincing transcript |
| **4** | **Tier A + advisory-only.** Graduate on Tier A, but deliberation may not alter the actionable verdict until Tier B supports it | Most conservative that still ships. ⚠ A deliberation that cannot change anything is arguably not deliberation, and the demo weakens |

### I.4 ★★ The condition that matters more than the choice

Whichever option is taken, **one requirement is non-negotiable and time-critical**:

> **Persist the pre-deliberation verdict alongside the post-deliberation verdict, from the very first
> run.**

The pipeline already *has* the pre-deliberation verdict in memory — it is the input to the exchange.
Writing it costs one field. ⚠ **Not writing it destroys the counterfactual arm permanently**, and Tier
B becomes impossible even once the samples eventually accumulate.

★ Identical in shape to `PG-9`'s propensity field: **near-free today, impossible to backfill.** If
`QR-3` is deferred, this requirement must not be.

### I.5 Recommendation

**Option 2, with §I.4 as a hard condition** — and one addition: **pre-register the kill rule.**

> *"If `T1` shows capitulation on false challenges within X of capitulation on valid challenges,
> `F6b` is deleted."*

Stating that threshold **before** running the test is what separates a measurement from a
rationalisation, and pre-registration is itself a strong signal for the target role.

⚠ **Option 4 deserves consideration on `PG-2` grounds** — deliberation would be touching a number the
fund manager trades on, and the conservative reading of `PG-2` says an unproven mechanism should not.
The cost is a less compelling demo.

---

## Decisions log

> Append-only. Each entry: date, session, decision, and the reasoning that makes it
> re-checkable later. **At release close, anything here that still binds must be promoted**
> into a spec, the constitution, or `../specs/vision.md`.

- **2026-08-28 (S1) — Q1 · Home = this repo; the pipeline is absorbed, then retired.**
  Build the platform in `collective-investment-ai-assistant`, importing
  `ai-investment-pipeline` in the interim. Once the platform is stable, copy the pipeline's
  `src/**` tree in and **retire the old repo** for ease of maintenance. *Rationale: cleanest
  portfolio artifact and a genuine architecture story, without maintaining two divergent
  copies long-term.* ⚠ **Consequence:** this repo's tree must be a superset of the
  pipeline's from day one — see §G and `L4-target-structure.md`.
- **2026-08-28 (S1) — Q2 · Balanced dual pitch.** Explainability and deliberation carry
  equal weight in the portfolio story. *Rationale: Victor's call, over my recommendation to
  subordinate deliberation.* ★ **Made coherent by §F: one shared evaluation harness serves
  both lanes, and the §D.1 A/B study is simultaneously the agent demo and the evaluation
  demo.** ⚠ Binding consequence recorded as `PG-4`.
- **2026-08-28 (S1) — Q4 · Phase 0 is a binding gate.** No agent-layer or platform code
  ships until the pipeline completes a verified end-to-end run. *Rationale: mirrors Victor's
  own AB-5 precedent for D-10 (“I do not plan to implement D-10 code until the full pipeline
  runs stably”), and protects against arriving at May 2027 with an elaborate demo over an
  unproven signal.* Recorded as `PG-1`.

- **2026-08-30 (S3) — `QR-3` · Option 2 — deliberation is gated on Tier A, not Tier B.**
  `F6b` graduates when `F7a` (process tests) has a design; `F7b` (outcome study) accrues from day one
  and never gates. *Rationale: Tier B is a second-order measurement on an unestablished first-order
  effect (IC 0.0203, t = 1.42) at ~250 decisions/year — a gate written against it could never open,
  and would cancel half the portfolio thesis by procedural accident rather than by decision. Tier A
  has unlimited samples, results in days, and catches the failure modes that actually make
  deliberation worthless.* Recorded as **`PG-5.1`**.
  ⚠ **Hard condition, binding immediately:** `PG-5.2` — the pre-deliberation verdict is persisted
  alongside the post-deliberation verdict **from the first run**. Near-free now; the counterfactual
  arm is unrecoverable if skipped. ★ The Tier-A kill rule is **pre-registered** before the test runs.
- **2026-08-30 (S3) — `QR-6` · D-12 stays deterministic this release.** The meet-semilattice remains;
  *"verdicts gate, never upgrade"* stays structural. An `AgentPort` may sit on the node to preserve
  the option, but agent-assisted combination is advisory alongside, never replacing (`PG-6`).
- **2026-08-30 (S3) — `QR-11` · Two scalability axes, not three.** Horizontal (additional modules) and
  vertical (deeper maths/logic within a module, **including swapping a better implementation behind
  an unchanged contract**). *The earlier "substitutional" third axis is withdrawn — substitution is a
  vertical move, and `C1`/`A3` are what make it cheap.*
- **2026-08-30 (S4) — QR-5 · The IC gate uses a Newey–West HAC standard error on the realised
  per-date IC series, reported alongside the null SE, gated on the HAC figure.** *Rationale: the null
  SE asserts a per-date dispersion of 0.0448 that the data has already falsified (measured 0.156,
  3.49× larger); and a promotion gate is a forward decision, where regime variation is genuine
  uncertainty about next period's outcome rather than descriptive spread. It also satisfies QA-4 as
  written instead of amending the rule down to match a weaker formula.* Rejected: keeping the null SE
  (promotes a model at realised t = 1.42), and the plain realised SE (still no true autocorrelation
  correction). ⚠ **`QR-19` spun out — the t-threshold must be re-derived in the same change**, or the
  bar silently rises ~3.5×. ⬆ **Implementation is an upstream edit to D-03's contract, `mde()`, §5.3b
  and QA-4 — not applied here.** Full record: `../questions.md` QR-5.
- **2026-08-30 (S4) — QR-7 · Pluggability layers 1–4 kept; hot reload cut; variant set is CLOSED.**
  Every selectable variant is registered at startup and resolvable at any time. *Rationale: keeps
  `validate_coverage()` meaningful so a missing variant fails at boot rather than mid-run, and makes
  the hot-reload non-goal **structural** — you cannot select what was never registered.* Rejected: an
  open/lazily-discovered variant set, which reintroduces the hazards just cut. ⚠ **`F1` must cache
  instances per `(port, variant)` within a run**, or per-ticker selection reloads a model 500 times.
  Full record: `../questions.md` QR-7.
- **2026-09-01 (S5) — `QR-17` reframed and answered: directives are INTERPRETED, not enumerated.**
  An LLM maps one line of free text onto a **closed effect vocabulary**; the manager confirms the
  parameter diff; the system applies it deterministically. ★ **Interpretation is frozen at input
  time** — replay never re-invokes the model, so `PG-9` holds. Raw text reaches no downstream prompt.
  ⏳ The initial vocabulary is deferred to E2E validation (`L3` §7 `E1`). Binds `F8` §2.1.
- **2026-09-01 (S5) — `F7a`'s kill rule becomes a pre-registered analysis plan, not a threshold.**
  Null, statistic, α, power, δ and bands (`KEEP`/`ADVISORY_ONLY`/`DELETE`); `min_n_per_arm` from a
  power calculation. *Rationale: a threshold cannot be chosen honestly before the data and will be
  chosen to pass after it; science pre-registers the analysis, not a constant.* ⚠ Kills on failure to
  reject, so an underpowered run returns `INSUFFICIENT`, never `DELETE`.
- **2026-09-01 (S5) — An E2E validation checklist is opened** (`L3` §7, `E1`–`E9`) for decisions that
  cannot honestly be made before real behaviour exists.
- **2026-08-30 (S4) — The question register is opened.** All questions, answered and open, move to
  `../questions.md`, categorised by module, with rejected options and binding locations. New family
  `QR-n`. ⚠ The register records *why*; the constitution and specs record *what*.
- **2026-08-30 (S3) — Explainability ownership split.** **Attribution** lives inside each analytical
  seat as a field on its own output contract, because only the module that performed a computation
  can attribute it. **Explanation** (cross-view, counterfactual) is D-13 at seat 6, the only seat
  permitted to read both analyst views. *Seats 2/3 do not own D-13; they carry an obligation it
  consumes.*

### ⏳ Open questions — now tracked in the register

★ **All questions from this release, answered and open, moved to
[`../questions.md`](../questions.md) on 2026-08-30** and are tracked there by module with their
rejected options and binding locations. The session IDs below map to `QR-n` as follows:

| Session ID | Register | Status |
|---|---|---|
| Q1 repo home | `QR-1` | ✅ |
| Q2 framing | `QR-2` | ✅ |
| Q3 deliberation measured | `QR-3` | ✅ |
| Q4 phase gate | `QR-4` | ✅ |
| ★ **Q5 IC gate SE** | **`QR-5`** | ✅ **decided 2026-08-30 — ⬆ upstream edit pending** |
| Q6 D-12 deterministic | `QR-6` | ✅ |
| ★ **Q7 pluggability layers** | **`QR-7`** | ✅ **decided 2026-08-30** |

⚠ **Do not add new open questions to this file.** The brainstorm records the *discussion*; the register
records the *question*.
