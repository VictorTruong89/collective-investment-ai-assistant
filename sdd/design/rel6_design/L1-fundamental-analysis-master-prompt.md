# L1 Companion: Master Prompt Registry — Fundamental Analysis (D-01)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not authoritative.** Companion to
> [`L1-fundamental-analysis.md`](L1-fundamental-analysis.md), which governs; where the two disagree the
> L1 spec is right and this file is the bug.
> **Domain:** D-01 · **Seat:** SEAT-2 · **Path it describes:** `src/fundamental/prompts/`
> **Purpose:** the single source of truth for *every* prompt D-01 is permitted to issue, so that
> INV-9's alignment checker has something complete to check against.
> **Prior art:** `pipeline/buffett/synthesis/prompt_stock_analysis.md` (the legacy mega-prompt),
> `samples/L1-research-analysis-explanation.md` (the ROE deep-dive sample).

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.3.0 | 2026-08-23 | Victor | ✅ **QP-8 closed — the relay prompt is GENERATED from these blocks** (§10A). ★★ **The finding that made it cheap: only THREE shared blocks (S-2, S-6, S-7) carry the entire API-vs-chat difference.** The task blocks are transport-agnostic as written, so generation is composition plus a **closed substitution map**, not a rewrite. **RG-1…RG-6**, with **RG-4** the load-bearing one — CI regenerates and diffs, ⚠ *without which the generated file becomes a source again within a month and nobody notices until the two disagree.* ★ **§10A.4 records which blocks the current hand-written file is made of, and which three are deliberately omitted** (J-10 always reports an absence; J-14 cannot read the pass that produced it; J-19 needs a peer set a chat cannot align). ⚠ **§10A.5 states the cost honestly: composed prose reads worse than hand-written**, and the artifact is pasted by a human who has to want to use it. |
| 0.2.0 | 2026-08-22 | Victor | ⚠ **Caught up with two days of decisions this file predated.** It was written 2026-08-20; §10A (calendar), §10B (events), §10B.5 (attribution), §10C (sector file) and §4B (the relay) all landed after it, and a grep found **zero** coverage of *calendar, 8-K, sector, relay, residual, attribution* or *vintage*. **Six new blocks: E-15 · J-18 · J-19 · V-05 · V-06 · V-07.** ★ **V-05 is the one that needed prompt text most** — RA-79 forbids rationalising an unexplained move, and *"an LLM asked why a stock fell will always produce a reason"* is a property of the model that only the prompt can push back on. ★ **S-2 gains the vintage rule (RA-93) and period-aligned peers (RA-96a)**; §9 gains variant-aware block IDs (XP-44). ★ **§0.2 now says it depicts WF-1 only** — there are nine workflows and the diagram showed one. |
| 0.1.0 | 2026-08-20 | Victor / AI | Initial draft. Consolidates the legacy mega-prompt, the ROE sample, and the external canon (§10) into **one registry of narrow prompts**, staged so that **RA-14 anchor-stripping is structural rather than instructed**. |

---

# 0. WHAT THIS FILE IS — and why it is not a mega-prompt

The request was "a master prompt file containing all the prompts this domain might use." This file
is that. It is deliberately **not** a single large prompt, and the reason is a rule in the governing
spec:

> **RA-10** — *Decompose. Many narrow calls beat one omnibus call. Variance scales with the degrees
> of freedom in a single response, so a prompt that asks for twelve judgements at once is twelve
> times less stable than twelve prompts.*
>
> **RA-5** — *Extraction and judgement are separate calls with separate prompts. A prompt that asks
> "summarise the filing and tell me if it's a good business" makes the verifiable half unverifiable.*

`prompt_stock_analysis.md` is one document that asks for fourteen sections, six web-search turns,
five valuation methods and a verdict in a single pass. Under RA-5/RA-10 that shape is the thing
D-01 exists to replace. **What survives from it is its analytical content — the archetype
classifier, the cycle rules, the supply-side read, the differential view, the tripwires — all of
which reappear below as individual calls.** What does not survive is its *procedure*: live web
search (RA-1), self-computed valuation (RA-45, P2), LLM-authored stop-losses (RP-1 reliability
class), and resumable multi-turn state (RA-12).

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE LEGACY MEGA-PROMPT IS A SOURCE OF QUESTIONS,                ║
║  NOT A SOURCE OF PROCEDURE.                                      ║
║                                                                  ║
║  Keep:  what to ask about a cyclical, what a supply-side read    ║
║         is, why PEG is disqualified at a trough, the             ║
║         differential view, ETF tripwires, 10b5-1 checking.       ║
║                                                                  ║
║  Drop:  one call for everything, live retrieval mid-prompt,      ║
║         arithmetic inside the prompt, verdict and valuation      ║
║         decided in the same breath as the business analysis.     ║
╚══════════════════════════════════════════════════════════════════╝
```

## 0.1 Rules this file adds

| ID | Rule |
|---|---|
| **MP-1** | **Every prompt D-01 issues appears here, with an ID and a version.** A call site whose prompt is not in this registry fails INV-9 alignment. There is no "small ad-hoc call" exemption — the two card incidents were both small calls |
| **MP-2** | **A prompt is composed, not written.** Every call = the shared blocks it declares (§2) + exactly one task block (§3–§7). Copy-pasting a shared block into a task block is drift with extra steps |
| **MP-3** | **Stage membership is enforced by the bundle, not by the instruction.** A Stage-A prompt cannot see price because the bundle handed to it has no price field — not because the prompt asks it not to look (RA-14). ★ *"Do not consider valuation" is a request; an absent field is a guarantee* |
| **MP-4** | **Every extraction has a stable `evidence_id`.** Rubric `evidence_required` lists (RA-32) cite those IDs, and `evidence_coverage` (RA-65) counts them. An extraction with no ID cannot be counted, so it cannot support a rubric level |
| **MP-18** | ★★ **An extraction's identity is `(evidence_id, qualifier, period)` — not `evidence_id` alone.** *(Added 2026-09-07, `F5` case 1.)* `E-01` returns **one item per reportable segment**, and every one of them is legitimately `seg.revenue` — the id names *what was extracted*, not *which row*. The segment goes in `qualifier`. ⚠ **The id itself may NOT be suffixed** (`seg.revenue.CNBU`): `b43_v1.py` maps the published rubric dimension `segments → "seg.revenue"` and `score.py` matches by **set membership on bare ids**, so a suffix makes the level unavailable *for a naming reason rather than an evidential one* — which the rubric map's own comment calls a wiring bug. ★ Precedent: `withdraw_extractions` already keys on `(evidence_id, period)` (`RA-138`). ⚠ `qualifier` is `""` for the ordinary one-item-per-id case, so nothing existing changes |
| **MP-5** | **Output shape is enforced by the API, not by prose.** Judgement calls use structured outputs with a closed enum; extraction calls use tool-use with `strict: true`. ★ A prompt that *asks* for JSON and parses the reply is doing RA-8's job with a worse tool |
| **MP-6** | **No prompt in this file computes anything.** Where a number is needed it arrives pre-computed from D-02 with its arithmetic trail (`L1-feature-engineering.md` §6.2). A prompt containing the word "calculate" is a defect (RA-45, AP-5) |
| **MP-7** | **Every prompt states its own failure output.** The insufficient-evidence path (S-4) is part of the contract, not an error branch — an LLM with no stated way to say "I could not" will always find something to say (P5, AP-4) |

## 0.2 How a run uses this registry

```text
   ┌─ D-07 filings, news, profile ─┐   ┌─ D-02 numbers + trail ─┐
   └───────────────┬───────────────┘   └───────────┬────────────┘
                   └───────────┬───────────────────┘
                     §5 EvidenceBundle  (hashed, pinned — RA-1…RA-4)
                               │
             ┌─────────────────┴──────────────────┐
             │  BUNDLE VIEWS — MP-3 makes staging │
             │  physical                          │
             │   view:blind    = no price, no MC, │
             │                   no multiples,    │
             │                   no FV, no targets│
             │   view:full     = everything       │
             │   view:delta    = new-since-as_of  │
             └─────────────────┬──────────────────┘
                               │
   E-blocks (extraction, view:full)  ──► checked vs bundle (RA-6)  ──► evidence_ids
                               │
   Stage A  J-01…J-08  view:blind    ──► scorecard + business view ──► HASHED & FROZEN
                               │
   Stage B  J-09…J-10  view:full     ──► reconciliation vs price
                               │
   Stage C  J-11…J-14  view:full     ──► bear case, pre-mortem, forgery hunt
                               │
   Stage D  J-15…J-17  view:full     ──► falsifiers FIRST, then verdict (RA-16)
                               │
   X-blocks (verification)           ──► citation check, substance check, lint
                               │
                        Thesis + GateVerdict + MonitorReport
```

> This is the lifecycle of one analysis run: where the material comes from, what shape it gets put into, and what order the prompts fire in.
>
> Top two boxes — nothing originates here. D-07 hands over raw material (filing text, news, company profile). D-02 hands over numbers already computed, each with the arithmetic that produced it. D-01 never fetches and never calculates; it receives.
>
> The EvidenceBundle — all of that gets sealed into one package and given a fingerprint (a hash). The reason is diagnostic: when two runs disagree, you need to know whether the model wavered or the inputs changed. Same fingerprint means comparable; different fingerprint means you're comparing two different questions.
>
>  Bundle views — the same sealed package, filtered three ways:
>  - blind — price, market cap, multiples, fair value and targets physically removed
>  - full — everything
>  - delta — only what's new since last time
>
>  ★ This is the idea the whole design rests on: the staging is enforced by what's in the envelope, not by asking the model not to peek. You cannot be anchored by a number you were never given.
>
> Then the prompts fire in order:
>  - E-blocks pull facts out of documents; each fact is checked back against the source text and gets an evidence_id.
>  - Stage A judges the business on the blind view — archetype, moat, earnings quality, balance sheet, capital allocation, cycle. No price anywhere in the room.
>  - FREEZE — Stage A's answer is written to disk and hashed.
>  - Stage B reveals the price and asks: what does this price require to be true, and does that match what Stage A found?
>  - Stage C attacks it — bear case, pre-mortem, metric-forgery hunt — as separate calls, so the model isn't conceding inside its own argument.
>  - Stage D writes the falsifiers first, then the verdict.
>  - X-blocks verify, and five of the seven are plain code, not prompts.
>
> Why the freeze is "load-bearing": it's the difference between sealing your prediction in an envelope and remembering what you predicted. If Stage A lived only in memory, Stage B could quietly revise it
> the moment it saw the price — and the output would look identical either way. Hashing it makes the earlier judgement something later stages can read but not rewrite.

> ⚠ **This diagram depicts WF-1 (fresh authoring) ONLY.** `L1-fundamental-analysis.md` §4A now
> defines **nine** workflows. The daily watch, the pre-event brief, the weekly sweep, the sector-file
> update and the relay each use a *different subset* of these blocks in a different order — §1's
> registry is the complete list, and the **Workflow** column says which run each block belongs to.

★ **The freeze between Stage A and Stage B is the load-bearing part.** RA-14 says you cannot un-see
a price. Staging alone does not deliver that — the Stage-A output has to be *committed* (hashed,
persisted) before the Stage-B bundle is assembled, or a later stage can quietly rewrite the earlier
judgement and the anchor-stripping bought nothing.

---

# 1. THE CALL REGISTRY

**Tier column** is constitution INV-8: `deep` = `claude-opus-5`, `cheap` = `claude-haiku-4-5-20251001`.
**View** is the bundle view of §0.2. **Guards** names the L1 rules the call must satisfy.

## 1.1 Extraction calls — ground truth exists in the document

| ID | Call | Tier | View | Output | Guards |
|---|---|---|---|---|---|
| **E-01** | Segment revenue & operating income | deep | full | table + spans | RA-6, MP-4 |
| **E-02** | Stated guidance & its revision | deep | full | table + spans | RA-6 |
| **E-03** | Risk-factor delta vs prior filing | deep | full | added/removed/reworded | RA-6 |
| **E-04** | Non-GAAP → GAAP reconciliation items | deep | full | line items + spans | RA-6 |
| **E-05** | Customer / supplier concentration | deep | full | named % or absent | RA-6 |
| **E-06** | Debt maturity ladder & covenants | deep | full | table + spans | RA-6 |
| **E-07** | Capital-allocation actions taken | deep | full | events + amounts | RA-6 |
| **E-08** | Insider transactions & 10b5-1 status | deep | full | per-transaction | RA-6 |
| **E-09** | Accounting-policy or estimate changes | deep | full | changes + spans | RA-6 |
| **E-10** | Share count & dilution mechanics | deep | full | basic/diluted/SBC | RA-6 |
| **E-11** | Litigation & regulatory matters | deep | full | matters + status | RA-6 |
| **E-12** | Management's stated capital priorities | deep | full | quotes + spans | RA-6 |
| **E-13** | Competitor capacity announcements | deep | full | table | RA-6 |
| **E-14** | News materiality triage | cheap | delta | per-item enum | RA-42 |
| **E-15** | ★ Sector-file ingest — source-list items | cheap | — | dated rows | RA-97…RA-101 |

## 1.2 Judgement calls — no ground truth; §7's guards apply

| ID | Call | Stage | Tier | View | Emits |
|---|---|---|---|---|---|
| **J-01** | Industry archetype classification | A | deep | blind | enum |
| **J-02** | Business-model comprehension | A | deep | blind | prose (capped) + claims |
| **J-03** | Moat durability | A | deep | blind | `moat_durability` level |
| **J-04** | Earnings quality | A | deep | blind | `earnings_quality` level |
| **J-05** | Balance-sheet resilience | A | deep | blind | `balance_sheet_resilience` level |
| **J-06** | Capital allocation | A | deep | blind | `capital_allocation` level |
| **J-07** | Cycle position | A | deep | blind | enum + evidence |
| **J-08** | Industry structure & supply side | A | deep | blind | enum + table |
| **J-09** | Expectations reconciliation | B | deep | full | enum + prose (capped) |
| **J-10** | Base-rate / outside-view check | B | deep | full | enum + reference class |
| **J-11** | Bear case | C | deep | full | structured bear case |
| **J-12** | Pre-mortem | C | deep | full | ranked failure paths |
| **J-13** | Metric-forgery hunt | C | deep | full | per-mechanism verdict |
| **J-14** | Disconfirming-evidence sweep | C | deep | full | list + spans |
| **J-15** | Falsifier authoring | D | deep | full | ≥1 checkable falsifier |
| **J-16** | Verdict selection | D | deep | full | enum + conviction |
| **J-17** | Data-gap census | D | deep | full | gaps + impact |
| **J-18** | ★ Pre-event brief | — | deep | full + calendar | outcome→falsifier map |
| **J-19** | ★ Industry-vs-company attribution | — | deep | full + peer_context | enum + magnitude |

## 1.3 Invalidation calls

| ID | Call | Tier | View | Note |
|---|---|---|---|---|
| **V-01** | Falsifier-fired triage | cheap | delta | RA-40, RA-42 |
| **V-02** | Falsifier-fired confirmation | deep | delta | escalation only |
| **V-03** | Thesis-material news classification | cheap | delta | RA-42 |
| **V-04** | Staleness attestation | — | — | ★ deterministic, no call (RA-43) |
| **V-05** | ★ Unexplained-move review | deep | delta | RA-79/80 — **may conclude *unexplained*** |
| **V-06** | ★ Weekly accumulation sweep | cheap | delta | RA-85/86 |
| **V-07** | ★ Assumption-state check | cheap | delta | the macro decision — §3.3 of the events note |

## 1.4 Verification calls — and the ones that must NOT be calls

| ID | Check | Mechanism |
|---|---|---|
| **X-01** | Extracted value present in cited span | ★ **deterministic string/number match — no LLM** (RA-6) |
| **X-02** | Every factual claim carries a span | ★ **deterministic schema check — no LLM** (RA-9) |
| **X-03** | Forecast-voice lint | ★ **deterministic wordlist — no LLM** (RA-26) |
| **X-04** | Length caps | ★ **deterministic — no LLM** (RA-27) |
| **X-05** | Bear-case token overlap with bull case | ★ **deterministic — no LLM** (RM-11) |
| **X-06** | Bear case names a falsifiable condition | deep, one narrow call | RM-11 |
| **X-07** | Claim–span semantic agreement (sample) | deep, one narrow call | RM-10 |

> ★ **Five of seven verification steps are not prompts.** That is the point. A checker built from
> the same stochastic process it is checking inherits its blind spots; an LLM asked *"does this
> number appear in this span"* is strictly worse than `in`. **Reach for X-06/X-07 only where the
> question is genuinely semantic** — "is this bear case about anything" and "does the span actually
> support the sentence".

---

# 2. SHARED BLOCKS — composed into every call (MP-2)

Each block has an ID and a version. The alignment manifest (§9) hashes them individually, so a
change to `S-3` reds every call that declares `S-3` and nothing else.

## S-1 · Role and reader — `v1`

```text
You are a research analyst at a one-person investment fund. Your output is read
by the fund's portfolio manager, who holds the decision and the P&L. You do not
hold either.

The reader is a competent non-institutional investor. He does not need finance
vocabulary explained, and he does need any conclusion to arrive with the
evidence that produced it. He is capable of disagreeing with you, and your
output is more useful to him when it makes disagreement easy.

You are not being asked whether to buy. You are being asked what is true, what
follows from it, and what would show you were wrong.
```

## S-2 · Grounding contract — `v1`

```text
You are given a fixed EVIDENCE BUNDLE below. It is the complete set of
information you may use. You have no browser, no other memory of this company,
and no access to anything outside the bundle.

  1. If a fact is not in the bundle, you do not know it. Say so (see S-4).
  2. Never supply a figure from memory, however confident you are. A number in
     your output that is not in the bundle is a fabrication, not a recollection.
  3. Do not compute. Every ratio, margin, growth rate and valuation figure you
     could need is supplied pre-computed in <computed_metrics>, each with the
     inputs that produced it. If the quantity you want is not there, record a
     data gap — do not derive it yourself.
  4. Do not interpolate, annualise, normalise or restate a figure the bundle
     gives you in another form. If the bundle has quarterly and you want annual,
     that is a data gap.
  5. The bundle is complete as of its stated `as_of`. Anything later does not
     exist for the purposes of this call.
  6. Where you compare against a released economic or industry series, the
     bundle gives you the value AS IT WAS PUBLISHED ON THAT DATE, not the value
     as later revised. Do not reason about the revised figure; you do not have
     it and you should not want it.
  7. Peer comparisons in <computed_metrics> are aligned by FISCAL PERIOD, not
     by calendar date. Where a peer set could not be period-aligned, the bundle
     says so — treat that comparison as unchecked rather than as a result.
```

> ⚠ **Rules 6 and 7 are RA-93 and RA-96a, and they exist because of measured defects.** Comparing a
> dated claim against a *revised* macro print is a look-ahead of the class this project keeps
> finding (`_cumulative_fys` 41.5 %, FMP TTM 71 %). And **MU's fiscal year ends in late August while
> its peers run calendar quarters** — a date-aligned peer median compares MU's Jun–Aug quarter
> against peers' Apr–Jun, on a live watchlist name.

> **Rule 3 is RA-45/AP-5 and it is the one models break most.** An LLM asked about ROE will divide
> if it sees a numerator and a denominator. **The countermeasure is supply, not instruction: if the
> pre-computed metric is present, the model has no reason to divide.** Where D-02 does not publish a
> metric the analysis needs, the fix is a D-02 feature contract, never a prompt that computes.

## S-3 · Evidence and citation contract — `v1`

```text
Every sentence you write is one of exactly three kinds, and you tag each one:

  FACT       Stated in the bundle. Carries `evidence_id` and a verbatim quote of
             the supporting text (or the exact metric name for a computed
             number). If you cannot quote it, it is not a fact.
  INFERENCE  Follows from one or more FACTs you have already stated. Carries the
             ordinals of the facts it rests on. An inference resting on nothing
             is an assumption; label it as one.
  ASSUMPTION Something you supplied that the bundle does not contain and does
             not imply. Permitted, and must be listed as an assumption so the
             reader can reject it independently of everything else.

An uncited factual claim is a defect, not a style choice. It fails the run.
```

## S-4 · The insufficient-evidence protocol — `v1`

```text
When the evidence needed for a judgement is absent, the correct output is that
absence, stated precisely:

  INSUFFICIENT_EVIDENCE
    needed:   <the specific item you required>
    why:      <what the bundle contains instead, or that it contains nothing>
    would_change: <what your judgement would become if the item existed and
                   said X, and what if it said Y>

This is a successful output. It is not a failure, it is not a low score, and it
must not be softened into a hedged answer. A plausible judgement built on absent
evidence is a failure even when it happens to be right, because nothing
downstream can tell the two apart.

Never fill a gap with an industry norm, a typical value, or a peer's figure
presented as this company's.
```

> ★ Directly inherited from the ROE sample's *"Nếu thiếu dữ liệu, ghi rõ **CHƯA ĐỦ DỮ LIỆU**"* —
> and strengthened by `would_change`, which converts an admission into a **research instruction**:
> it tells the data plane exactly which missing item is worth going to get.

## S-5 · Voice constraints — `v1`

```text
  - No forecast voice. Not "will", "is set to", "poised to", "on track to".
    Write the conditional instead: "if X holds, Y follows" — and name X.
  - No unearned certainty. Not "clearly", "obviously", "undoubtedly", "certainly",
    "no doubt", "without question", "the market is missing".
  - No superlative without a measured comparison in the bundle. "Best-in-class
    margins" is only permissible beside the peer figures it beats.
  - No appeal to authority. A publication's opinion, an analyst's rating and a
    price target are not evidence for a business fact. They may be described as
    the consensus you are measuring yourself against (J-09) and never cited in
    support of a claim.
  - No narration of your own process. Do not write "Let me analyse", "It is
    worth noting", "Importantly". Say the thing.
  - Precision must be earned. Do not write a figure to more significant digits
    than the bundle supports.
```

## S-6 · Output contract — `v1`

```text
Return your answer through the provided structured output schema and nothing
else. No preamble, no closing summary, no restatement of the question.

Where the schema offers an enumerated choice, you are selecting one of the
written options. You are not scoring, rating, or producing a number of your own.
If none of the options fits the evidence, select the `insufficient_evidence`
option — it exists for that case and is always present.
```

## S-7 · Anti-anchoring notice — `v1` — **Stage A only**

```text
This bundle deliberately omits the share price, the market capitalisation, every
valuation multiple, every fair-value estimate, every analyst target, and every
recent price move. Their absence is a design decision, not a data gap, and you
must not record it as one.

Do not ask for them. Do not estimate them. Do not reason about whether this
company is cheap or expensive — that is a later, separate call working from your
committed answer here.

If you notice yourself constructing a view about the stock, stop and return to
the question about the business.
```

## S-8 · No prior-verdict notice — `v1` — **fresh authoring only**

```text
You have not analysed this company before. There is no prior thesis, no prior
verdict and no prior conviction in this bundle, and you must not speculate about
what one might have said. You are answering from the evidence, not updating a
position.
```

> RA-18. The invalidation calls (§6) declare the opposite block, **S-9**, because re-checking a
> stated condition is a different task from re-deciding.

## S-9 · Prior-thesis notice — `v1` — **invalidation only**

```text
You are given a prior thesis and its falsification conditions. Your task is NOT
to re-decide whether the thesis is right. It is to check, against new evidence
only, whether a stated condition has occurred.

You may not revise the thesis, restate it more strongly, soften it, or add a
condition. You report on the conditions as written, including any you consider
badly written.
```

---

# 3. EXTRACTION PROMPTS (E-blocks)

**The verifiable half.** Ground truth exists in the document, so the guard is assertion against the
source (RA-6), not variance measurement. Every E-block emits items with a stable `evidence_id`
(MP-4) that rubric levels cite and `evidence_coverage` counts (RA-65/RA-66).

## 3.0 The shared extraction envelope

Composed into every E-block: **S-1 · S-2 · S-3 · S-4 · S-5 · S-6**.

```text
TASK TYPE: EXTRACTION.

You are reading a document to find what it says. You are not evaluating the
company, and no part of your answer may be an opinion about it.

For every item you return:
  evidence_id    the id given in the item list below — never invent one
  value          exactly as the document states it, in the document's own units
  unit           the units, verbatim ("thousands of USD", "%", "shares")
  period         the period the figure covers, with start AND end where the
                 document gives both
  quote          a verbatim span from the document containing the value
  accession_id   the document the span came from
  offset         [start, end] character offsets of the quote within that document

An item you cannot find is returned with status `not_found` and a one-line note
on where you looked. `not_found` is a correct answer. A value that is "roughly"
in the document, or that you assembled from two places, is not.

★ If the document gives a cumulative year-to-date figure where a discrete
  quarterly figure was requested, return it tagged `cumulative_ytd` with both
  period endpoints, and do NOT subtract to produce the discrete quarter. That
  subtraction is arithmetic and belongs to D-02.
```

> ★ **The last paragraph is a scar.** `F9` records that EDGAR's 6-K interim figures for foreign
> private issuers are cumulative YTD (ARM Q3 was 2.76× the discrete value) and that FMP guessed
> wrong on MU by 71 %. **Cumulative-vs-discrete is the single most expensive extraction error this
> project has actually made**, and an extractor that silently subtracts reproduces it inside the
> LLM layer where no `TTM_SOURCE_TOLERANCE` check can see it.

## E-01 · Segment revenue and operating income — `v1`

```text
From the filings in the bundle, extract the reporting-segment table for every
period the filings cover.

Items:
  seg.name          the segment name as the company defines it
  seg.revenue       revenue for that segment, that period
  seg.op_income     operating income or loss for that segment, that period
  seg.assets        identifiable assets, if disclosed
  seg.basis_note    any statement that the segmentation changed, was restated,
                    or that a segment was renamed or merged

If the company restated prior-period segments, return BOTH the as-originally-
reported and the as-restated figures, each tagged, and never silently prefer one.
```

**Why this one first:** a segment table is the cheapest available test of whether the story matches
the accounts. It is also where a restatement hides — and a restated comparative is exactly the kind
of figure that a five-year growth narrative is quietly built on.

## E-02 · Guidance, and its revision — `v1`

```text
Extract every forward-looking figure the COMPANY ITSELF stated, and only those.

  gd.metric         what is being guided (revenue, gross margin, capex, …)
  gd.value          the figure or range as stated
  gd.period         the period guided
  gd.stated_on      the filing/date it was stated in
  gd.prior_value    the same guidance as previously stated, if the bundle
                    contains an earlier statement of it
  gd.direction      raised | lowered | reaffirmed | initiated | withdrawn
  gd.language_note  verbatim hedging language attached to it

Do not include analyst estimates, consensus figures, or any third-party forecast.
Do not include a figure the company described as an illustration or a scenario.
`withdrawn` guidance is a high-value item — never drop it for being empty.
```

## E-03 · Risk-factor delta — `v1`

```text
Compare the risk-factor section of the most recent annual filing against the
prior one.

  rf.added      risk factors present now and absent before — full text
  rf.removed    present before and absent now — full text
  rf.reworded   present in both with materially changed wording; return BOTH
                versions and mark the specific clause that changed
  rf.reordered  a risk that moved materially in ordering, with both positions

Boilerplate churn is not a change. A risk that gained a specific number, a named
counterparty, a named jurisdiction, or a shift from "may" to "has" IS a change,
and is the reason this extraction exists.
```

> ★ **The highest-signal, least-read section of a 10-K.** Risk factors are written by counsel to be
> ignored; what counsel *adds* in a given year is a disclosure decision with a reason behind it. A
> risk that acquires a number was previously deniable and is not any more.

## E-04 · Non-GAAP reconciliation — `v1`

```text
Extract the full reconciliation from GAAP to every non-GAAP measure the company
presents.

  ng.measure          the non-GAAP measure's name as presented
  ng.gaap_start       the GAAP figure it reconciles from
  ng.adjustment       each adjusting line, its label and its amount
  ng.recurrence_note  for each adjustment: has an item with this label appeared
                      in the other periods in the bundle? Return the periods it
                      appeared in. Do not judge whether it "should" recur.
  ng.nongaap_end      the resulting non-GAAP figure

★ `ng.recurrence_note` is a lookup across periods the bundle already contains,
not an opinion. Return the list of periods; the judgement about what a recurring
"non-recurring" charge means is a different call.
```

## E-05 · Concentration — `v1`

```text
  cc.customer      any customer disclosed at ≥10% of revenue: identifier as
                   given (often "Customer A") and the percentage, per period
  cc.supplier      any supplier, sole-source or single-source dependency named
  cc.geography     revenue by geography as disclosed
  cc.channel       distributor/channel concentration if disclosed

Absence of disclosure is `not_found`, and it is meaningful: it means either no
customer crossed the threshold or the company did not disclose. Say which the
document supports; do not choose between them.
```

## E-06 · Debt maturity and covenants — `v1`

```text
  dm.instrument    each debt instrument: type, principal, coupon, maturity
  dm.ladder        principal due by year as the filing tabulates it
  dm.covenant      each financial covenant: the ratio, the threshold, the
                   direction of the test, and the tested entity
  dm.headroom      the covenant's most recently disclosed actual value, if given
  dm.revolver      undrawn revolver capacity and its expiry
  dm.rating        credit rating and outlook, if the filing states one

A covenant whose current value is not disclosed is `dm.headroom: not_found` —
which is itself the finding, since a company comfortably inside its covenants
usually says so.
```

## E-07 · Capital-allocation actions — `v1`

```text
Every deployment of capital DISCLOSED AS HAVING HAPPENED, per period:

  ca.buyback        shares repurchased, dollars spent, average price paid if given
  ca.authorisation  buyback authorisation size and remaining
  ca.dividend       per-share and total, and any change
  ca.acquisition    target, consideration, form (cash/stock/mixed), goodwill and
                    intangibles recognised
  ca.divestiture    what was sold, proceeds, gain or loss recognised
  ca.capex          capital expenditure, and any split into maintenance vs growth
                    IF the company itself makes that split
  ca.rd             research and development expense
  ca.issuance       equity or debt issued, amount and stated use of proceeds

Never split capex into maintenance and growth yourself. If the company does not
split it, return `not_found` for the split and the total for the whole.
```

## E-08 · Insider transactions and 10b5-1 status — `v1`

```text
For each insider transaction in the bundle's Form 4 material:

  in.person        name and stated relationship
  in.date          transaction date
  in.type          purchase | sale | option exercise | gift | award | other
  in.shares        share count
  in.price         price, where stated
  in.plan_status   ★ 10b5-1 | not_10b5-1 | not_stated — from the form's own
                   checkbox, never inferred from context
  in.plan_date     the plan adoption date, where the form states one
  in.holdings_after shares beneficially owned following the transaction

★ `in.plan_status` is the whole point of this extraction. A scheduled sale under
a plan adopted a year earlier and a discretionary at-market sale look identical
in a headline and mean different things. If the form does not state it, the
answer is `not_stated` — never "probably a plan".
```

> Inherited directly from the legacy mega-prompt's **Rule 12**, which was right about this and is
> the one procedural rule from that document worth keeping verbatim.

## E-09 · Accounting-policy and estimate changes — `v1`

```text
  ap.change        any change in accounting policy, estimate, or presentation,
                   with the company's stated reason and quantified effect
  ap.useful_life   changes to depreciation or amortisation lives
  ap.reserve       changes to allowance, warranty, or return reserves, and the
                   direction of the P&L effect
  ap.capitalisation any change in what is capitalised vs expensed
  ap.auditor       auditor change, disagreement, or a modified opinion
  ap.icfr          any material weakness or significant deficiency disclosed
  ap.late          any late-filing notification (NT 10-K / NT 10-Q)
```

## E-10 · Share count and dilution — `v1`

```text
  sc.basic / sc.diluted     weighted-average share counts per period
  sc.end_of_period          shares outstanding at period end
  sc.sbc_expense            stock-based compensation expense
  sc.sbc_revenue_note       revenue for the same period (for the reader's ratio —
                            do NOT compute the ratio)
  sc.unvested               unvested awards outstanding, if disclosed
  sc.antidilutive           securities excluded as anti-dilutive
```

## E-11 · Litigation and regulatory — `v1`

```text
  lg.matter       each matter: counterparty, claim, jurisdiction, stage
  lg.amount       damages sought or accrued, where stated
  lg.accrual      whether a loss is accrued, and the amount
  lg.language     verbatim probability language ("reasonably possible",
                  "probable", "cannot be estimated")

★ The verbatim language IS the finding. Those phrases are accounting terms of
art with defined thresholds, and paraphrasing one destroys the information.
```

## E-12 · Management's stated capital priorities — `v1`

```text
From MD&A, the shareholder letter, and any prepared remarks in the bundle,
extract what management SAID about how it intends to allocate capital.

  cp.statement    verbatim quote
  cp.period       when it was said
  cp.commitment   the specific commitment, if any (a figure, a ratio, a date)
  cp.condition    any condition attached to it

Return statements only. Whether they were kept is J-06's question, and answering
it here would contaminate an extraction with a judgement (RA-5).
```

## E-13 · Competitor capacity announcements — `v1`

```text
From the industry material in the bundle:

  cx.competitor    the company announcing
  cx.capacity      what is being added, in the units the source uses
  cx.timing        stated online date
  cx.status        announced | under construction | commissioning | operating
  cx.conditional   any stated condition ("subject to demand", "subject to
                   government approval") — verbatim
  cx.source        the bundle item this came from

An announcement is not capacity. Return the announcement and its status; whether
supply actually arrives is J-08's question.
```

> The legacy mega-prompt's **Rule/Section 4 supply-side table**, minus its plain-language
> interpretation column — which was a judgement smuggled into a data table and now lives in J-08.

## E-14 · News materiality triage — `v1` — ★ cheap tier

```text
TASK TYPE: TRIAGE. You are sorting, not analysing.

For each news item, select exactly one:

  material_to_business    changes a fact about the company's operations,
                          finances, customers, capacity, leadership or legal
                          position
  material_to_thesis      speaks to one of the stated thesis conditions supplied
                          with this call
  price_commentary        about the share price, a rating, a target, a move
  noise                   everything else, including opinion, listicles,
                          previews, and restatements of older items

Then, for material items only, one line: what specifically changed.

★ `price_commentary` is a separate bucket from `noise` on purpose. It is not
noise — it is evidence about sentiment — but it is never evidence about the
business, and merging the two buckets is how a price move becomes a fact.
```

> INV-8 cheap tier (RA-42): high-frequency and shallow. **This is the only extraction that runs
> daily**, and it is the gate that decides whether anything deep runs at all.

## E-15 · Sector-file ingest — `v1` — ★ cheap tier

```text
TASK TYPE: EXTRACTION into a shared file.

You are adding rows to an industry evidence file that EVERY thesis in this
industry will read. Nothing you write here is a conclusion.

For each item in the source list, extract every row it supports:

  capacity     competitor · what is being added · units as the source states
               them · stated online date · status (announced | under
               construction | commissioning | operating) · any condition
               attached, verbatim
  pricing      a disclosed price, ASP or contract term, with its period
  inventory    a disclosed inventory or channel figure, with its units
  demand       a disclosed order, backlog or customer-commitment figure
  policy       an export control, tariff or regulatory action, with its date

Every row carries: source item id · the date the item was published · a
verbatim quote.

★ Rows are APPEND-ONLY. If an item updates something already in the file — a
capacity that moved from `announced` to `operating` — emit a NEW row with the
new status and the new date. Never revise the old row. The transition history
is the finding, and an announcement that quietly never became capacity is
invisible once the row is overwritten.

⚠ You process EVERY item in the source list. If an item supports no rows, say
so with a one-line reason. Skipping an item silently is how a file that
contains no opinion acquires one — through what got left out.

You may not add a field. If something does not fit the shape above, report it
as an unfitted item and stop; the schema is versioned and a new column is an
analytical change, not a convenience.
```

**Guards:** RA-97 (no conclusion field) · RA-98 (completeness — the reason for the "every item"
clause) · RA-100 (fixed schema — the reason for the "may not add a field" clause) · RA-101
(append-only status transitions).

---

# 4. JUDGEMENT PROMPTS (J-blocks)

**The irreducible half.** No ground truth, so the guards are §7's: bounded output (RA-8), criterion
selection rather than scoring (RA-31), evidence required per level (RA-32), decomposition (RA-10),
and the staging that makes RA-14 physical (MP-3).

## 4.0 The shared judgement envelope

Composed into every J-block: **S-1 · S-2 · S-3 · S-4 · S-5 · S-6**, plus **S-7** in Stage A and
**S-8** in fresh authoring.

```text
TASK TYPE: JUDGEMENT.

You are answering a question that has no verifiable answer. Two things follow.

First, your answer's value is entirely in the evidence and reasoning you attach
to it, not in the answer itself. A confident selection with thin evidence is
worth less than a hedged one with thick evidence, and the reader will be shown
both.

Second, you are selecting from written criteria, not producing a score. Read
every option before choosing. Choose the one whose criterion the evidence
actually satisfies — not the one nearest your overall impression. If the
evidence for an option's stated requirements is missing from the bundle, that
option is unavailable to you no matter how well it describes the company.

You will also state, in one sentence, the single observation that would move you
to the adjacent option. That sentence is part of the answer.
```

> ★ **The last paragraph is the cheapest de-biasing device in this file.** It forces the boundary of
> the judgement to be named at the moment it is made, and it is what makes RM-2's dispersion
> readable: a dimension that moves two levels between identical runs, whose stated boundary
> observation is different each time, has an under-determined rubric (RA-34) — not a noisy model.

---

## Stage A — the price-blind pass (bundle `view:blind`)

★ Everything in Stage A is committed and hashed before Stage B's bundle exists (§0.2). Stage A
never sees, and can never be revised in light of, the price.

### J-01 · Industry archetype — `v1`

```text
Classify this company into exactly one archetype. The classification governs
which analytical questions the rest of the analysis is allowed to ask, so it is
the first judgement and the one with the widest blast radius.

  cyclical_commodity   Output is substantially fungible; the industry's own
                       capacity cycle, not this company's execution, dominates
                       the earnings swing. Reported earnings at any single point
                       are a poor guide to normal earnings.
  compounder           Demand is stable, returns on capital have persisted above
                       the cost of capital across the periods in the bundle, and
                       reinvestment is modest relative to cash generation.
  secular_growth       Growth dominates every other variable; heavy reinvestment
                       defers cash generation deliberately; the open question is
                       market size and share, not margin.
  regulated_utility    Returns are set by a regulator against a rate base rather
                       than by competition.
  financial            The balance sheet IS the business. Book value, spread,
                       reserves and capital ratios are primary; earnings are not.
  binary_outcome       Value depends on a small number of discrete events
                       (approval, drill result, litigation) rather than on a
                       continuing operating record.
  insufficient_evidence

A company may plausibly fit two. Choose the one whose FAILURE MODE would hurt
the reader more if ignored, name the runner-up, and state in one sentence what
would settle it.
```

**Provenance:** Peter Lynch's six categories (*One Up on Wall Street*), collapsed against the legacy
mega-prompt's Rule 2 archetype table. **Kept because it changes what counts as evidence downstream**
— a trailing P/E at a cyclical trough and the same number for a compounder are not the same
observation.

### J-02 · Business-model comprehension — `v1`

```text
Explain how this company converts an input into a dollar of profit, in terms a
reader could use to predict what happens to that dollar when a named condition
changes.

Answer, each grounded per S-3:
  1. What is sold, to whom, and what the buyer is choosing between.
  2. How revenue is recognised, and the gap between a sale and cash.
  3. The cost structure: what is fixed, what is variable, and what changes the
     ratio.
  4. The three variables that most move profit, ranked, each with the bundle
     evidence for the ranking.
  5. ★ What you do NOT understand about this business after reading the bundle.

Item 5 is mandatory and may not be "nothing". Every business has a part that its
own disclosures do not explain; naming it is the most useful sentence you will
write, and an analyst who claims complete understanding of a company from its
filings has stopped reading.

Length cap: 400 words.
```

### J-03 · Moat durability — `v1` — emits `moat_durability@v2`

```text
Assess whether this company can defend its pricing and its share, and for how
long.

STEP 1 — Which mechanism, if any, is present. For each, state present /
absent / insufficient_evidence with its bundle evidence:

  intangible_assets   brands, patents, regulatory licences — something that
                      legally or perceptually prevents substitution
  switching_costs     the customer's cost (money, time, risk, retraining) of
                      leaving, evidenced by contract terms, integration depth,
                      or disclosed retention
  network_effects     each additional user makes the product more valuable to
                      existing users
  cost_advantage      a structurally lower cost per unit — process, scale,
                      location, or a resource rivals cannot obtain
  efficient_scale     a market served adequately by its incumbents where a new
                      entrant's capacity would destroy the returns it entered for

STEP 2 — The two outcome tests, from the evidence, not the story:
  a) Market-share stability across the periods in the bundle. Stable shares
     among the leaders are evidence a barrier exists; churning shares are
     evidence one does not, whatever the mechanism above suggests.
  b) Persistence of returns on invested capital above the cost of capital, using
     the pre-computed series in <computed_metrics>. A moat that has never shown
     up in the returns is a story about a moat.

STEP 3 — Select ONE level from the rubric. A level whose `evidence_required`
items are absent from the bundle is unavailable (RA-32).

STEP 4 — Name the single observation over the next four quarters that would move
you down one level.
```

**Provenance:** Pat Dorsey's five sources (Morningstar's operating taxonomy) for Step 1; Bruce
Greenwald's two empirical tests — **stable share plus superior returns** — for Step 2.

> ★ **Step 2 exists because Step 1 is where an LLM is weakest.** Every company's filings describe
> switching costs; almost none of them have any. **The mechanism is a hypothesis and the share/return
> record is the test**, and a rubric that scored Step 1 alone would reward good corporate writing.

### J-04 · Earnings quality — `v1` — emits `earnings_quality@v1`

```text
Assess whether reported earnings represent cash the owners could have.

STEP 1 — The cash test. Using the pre-computed series:
  a) Cash conversion — operating cash flow against net income, every period in
     the bundle. A persistent gap in one direction is the finding; a single
     year's gap is usually working capital.
  b) The accrual ratio. Earnings whose growth arrives as accruals rather than
     cash have historically been the less persistent kind. State the level, the
     direction of travel, and which accrual line drives it.
  c) Free cash flow after ALL capital expenditure, against net income.

STEP 2 — The composition test, from E-04 and E-07:
  a) What share of the period's earnings came from items that are not the
     operating business — asset sales, reserve releases, one-time gains, fair-
     value marks, tax items?
  b) Which "non-recurring" adjustments have recurred? E-04 returns the periods
     each label appeared in; a label appearing in most of them is a recurring
     cost being presented as an interruption.
  c) Stock-based compensation against revenue, and its trend.

STEP 3 — The working-capital test:
  Days sales outstanding, days inventory, days payable, each across the periods.
  Receivables growing faster than revenue, or inventory growing faster than
  cost of sales, are the two classic ways a good quarter is borrowed from a
  later one. State which, if either, is present.

STEP 4 — The return-decomposition test:
  Decompose the return on equity into margin, asset turnover and leverage, and
  state which of the three moved. ★ An improving ROE driven by leverage is a
  different fact from one driven by margin, and they are indistinguishable in the
  headline number.

STEP 5 — Select ONE rubric level. STEP 6 — Name the observation that would move
you down one level.
```

**Provenance:** Howard Schilit's *Financial Shenanigans* (the seven manipulation families, reduced
to what a filing can show); Richard Sloan's accrual work (accrual vs cash components differ in
persistence); DuPont decomposition; **and the ROE sample in `samples/`, whose entire argument is
Step 4** — *"Đừng hỏi ROE cao hay thấp. Hãy hỏi ROE được tạo ra bằng cách nào."*

> ★ **Steps 1–4 are all lookups against pre-computed series.** The judgement is *which pattern is
> present and what it means* — the arithmetic is D-02's (RA-45). If a series named here is not
> published by D-02, the fix is a D-02 feature contract; **the fix is never a prompt that divides.**

### J-05 · Balance-sheet resilience — `v1` — emits `balance_sheet@v1`

```text
Assess whether this company survives a bad cycle without diluting its owners.

  1. Leverage, both gross and net, against the periods in the bundle and against
     the peer context supplied.
  2. The maturity ladder (E-06). What must be refinanced, when, and what the
     coupon on it is. A wall inside three years is a different company from the
     same leverage spread over ten.
  3. Covenants (E-06). The tested ratio, the threshold, and the disclosed
     headroom. Undisclosed headroom is a finding (S-4), not a pass.
  4. Liquidity: cash, undrawn revolver, and the revolver's own expiry.
  5. ★ The downside arithmetic, using ONLY pre-computed scenario figures where
     the bundle supplies them: at the worst earnings level visible in the
     bundle's history, does this balance sheet still service its debt? If the
     bundle contains no such period, say so — a company that has never been
     tested is not the same as one that passed.
  6. Off-balance-sheet and contingent items: leases, guarantees, litigation
     accruals (E-11), pension.

Select ONE rubric level. Name the observation that would move you down one.
```

**Provenance:** Altman's distress-prediction variables as the shape of the question (leverage,
liquidity, retained earnings, coverage) — **used as a checklist of what to look at, never as a score
this prompt computes** (MP-6).

### J-06 · Capital allocation — `v1` — emits `capital_allocation@v1`

```text
Assess whether management's deployment of capital has created value for owners.
Judge the record (E-07), against the stated intentions (E-12).

  1. Where the cash went, period by period, as proportions: reinvestment,
     acquisition, buyback, dividend, debt reduction, cash accumulation.
  2. ★ Buyback price discipline. Compare the average repurchase price to the
     price range of the period in which it was bought, from the pre-computed
     series. Buying steadily regardless of price is a policy, not an allocation
     decision, and it is the most common way a good business returns capital
     badly.
  3. Acquisitions: what was paid, what was recognised as goodwill, and — where
     the bundle covers a long enough window — whether the acquired assets were
     later impaired. An impairment is management marking its own homework, and
     it is the only honest acquisition scorecard filings offer.
  4. Reinvestment quality: incremental capital deployed against the change in
     operating profit that followed it, using the pre-computed series. Whether
     there is anywhere left to deploy at that return is the more important half.
  5. Dilution: has the share count fallen, and is buyback spending net of
     issuance actually retiring shares or offsetting compensation? (E-10)
  6. ★ Said versus did. E-12 supplies what management stated it would do. State,
     per commitment: kept / not kept / not yet testable — and do not grade the
     eloquence of the statement.

Select ONE rubric level. Name the observation that would move you down one.
```

**Provenance:** William Thorndike's *The Outsiders* (capital allocation as the CEO's actual job;
cash flow per share over reported earnings); Mauboussin's capital-allocation work for the
reinvestment-runway framing.

> ★ **Item 6 is the reason this dimension is worth scoring at all.** Every other dimension can be
> read off the accounts. This one is the only place the system builds a **track record of a specific
> management team's promises against its actions** — and it compounds: it is worth little in year
> one and a great deal in year five, which is an argument for starting it now.

### J-07 · Cycle position — `v1` — mandatory for `cyclical_commodity`

```text
Where in its industry cycle is this business, and on what evidence?

Select one: trough | early_recovery | mid | late | peak | not_applicable |
insufficient_evidence

Each of these must be addressed, with bundle evidence or an explicit gap:
  a) Realised prices or ASPs against their range across the bundle's history.
  b) Inventory: the company's, and the channel's where disclosed, in days.
  c) Capacity utilisation against its own history.
  d) Order patterns: lead times, backlog, cancellations, contract duration.
  e) Industry-wide capital expenditure — is the industry building or starving?
     (E-13) This is the leading variable, and it is about the industry, not this
     company.
  f) Margin position relative to the bundle's own history.

★ The trap, stated so it is checked rather than assumed: at a cyclical peak,
trailing earnings are at their highest and trailing multiples at their lowest,
so the business looks cheapest exactly when it is most dangerous — and at a
trough the reverse. State explicitly which side of that trap the present
evidence puts you on. If you cannot tell, that is `insufficient_evidence` and it
is a legitimate answer.

You are NOT estimating normalised earnings. That is arithmetic and belongs to
D-02; if D-02 publishes a mid-cycle series it is in <computed_metrics>, and if
it does not, that is a data gap.
```

**Provenance:** Lynch's cyclical rules; the legacy mega-prompt's Rules 7 and Section 3 —
**with its mid-cycle-EPS computation removed and reassigned to D-02** (P2, AP-5, RA-45).

### J-08 · Industry structure and supply — `v1`

```text
Assess the industry this company competes in, independent of the company.

  1. Concentration: who are the participants and how is share distributed?
  2. Barriers to entry — the practical question, not the theoretical one: what
     would it cost, and how long would it take, for a credible entrant to reach
     a share that mattered? Answer in the units the bundle supports.
  3. Buyer power and supplier power, evidenced by concentration (E-05) and by
     contract terms where disclosed.
  4. Substitution: what does the customer do instead, including doing nothing?
  5. ★ The supply read. From E-13's announced capacity, and only from it: over
     the next eight quarters, is announced supply growing faster than, in line
     with, or slower than the demand evidence in the bundle? Select one:
       supply_growing_faster | in_line | demand_growing_faster |
       insufficient_evidence
     For each competitor row, one sentence on what that announcement means for
     pricing IF it arrives on the stated schedule. Announced capacity that is
     conditional (E-13 `cx.conditional`) must be treated as conditional.

★ For a commodity business this is the single most important judgement in Stage A
and it is about the industry, not the company. A well-run participant in an
oversupplying industry loses money.
```

**Provenance:** Porter's five forces as the question set; Greenwald's reduction of them to
**barriers to entry as the force that dominates**; the legacy mega-prompt's Section 4 supply-side
table for item 5.

---

## Stage B — reveal the price (bundle `view:full`)

★ Stage A's output is now frozen and hashed. Stage B receives it as **given evidence it may not
revise** — the same relationship invalidation has with a prior thesis (S-9). If Stage B could
rewrite Stage A, the anchor-stripping was theatre.

### J-09 · Expectations reconciliation — `v1`

```text
You now have the price, the market capitalisation, the multiples, D-02's fair
value with its sensitivity band and its arithmetic trail, and the consensus view.
You also have your own Stage-A conclusions, which are FIXED. You may not revise
them here; if the valuation makes you want to, say so explicitly as a finding.

  1. ★ What does the current price require to be true? D-02 supplies the
     reverse-engineered figures — the growth, margin and duration implied by the
     present price. Read them out and state, in one sentence each, what the
     world looks like if each holds.
  2. Set those requirements against your Stage-A view. For each, select:
       required_less_than_evidenced | roughly_consistent |
       required_more_than_evidenced | insufficient_evidence
  3. Where the gap is widest, is it explained by something you found in Stage A,
     or is it unexplained? An unexplained gap is not an opportunity; it is a
     question you have not answered yet, and it belongs in the data gaps.
  4. ★ The differential view. State the consensus position in one sentence, then
     state where and why you differ, or state plainly that you do not differ. If
     you do not differ, say so — "I hold the consensus view with the consensus
     confidence" is a legitimate and useful output, and pretending to a
     contrarian angle is how an analyst manufactures one.
  5. Which method in D-02's trail does the most work in the fair value, and how
     sensitive is the conclusion to it? D-02 supplies the sensitivity band; state
     what the band means for this decision in one sentence.

You do not produce a fair value, a target, a stop, or a price. Those are D-02's
and D-06's outputs. You are stating whether the story and the numbers describe
the same company.

Length cap: 450 words.
```

**Provenance:** Mauboussin's expectations investing — *reverse-engineer what the price implies, then
judge whether the company can meet it* — with the DCF arithmetic left in D-02 where it belongs;
Damodaran's narrative/numbers coherence test; the legacy mega-prompt's Section 12 differential view.

> ★ **Item 1 inverts the usual direction and that is the entire value of this call.** "Here is my
> fair value, is the stock cheap?" invites the model to justify a number it just produced. "Here is
> what the market requires; is that plausible given what you already concluded?" is a test the
> Stage-A view can actually fail.

### J-10 · Base-rate check — `v1`

```text
For each forward-looking claim implied by the analysis so far — including the
claims the price requires (J-09) — place it against a reference class.

  1. Name the reference class: the set of companies or situations this one
     resembles, in the terms the bundle supports.
  2. State the base rate the bundle gives you for that class, or state that the
     bundle does not contain one. ★ Do NOT supply a base rate from memory — an
     invented base rate is worse than none, because it wears the clothing of
     evidence.
  3. State whether the claim asks this company to be typical of the class or
     exceptional within it.
  4. Where exceptional: what specifically, in the Stage-A evidence, justifies the
     exception? "Strong management" is not a justification; a mechanism is.

★ Most forecasts are built from the inside — from this company's story. This call
asks the other question: of the companies that have looked like this, how many
went on to do what this analysis assumes?

Length cap: 300 words.
```

**Provenance:** Mauboussin/Kahneman on base rates and the outside view.

> ⚠ **A real limitation, stated rather than hidden.** Item 2 will return "the bundle does not
> contain one" almost every time, because D-07 assembles a single-company bundle. **The honest
> options are to leave J-10 mostly reporting absences (a standing, visible data gap) or to add a
> reference-class dataset to the bundle** — the second is a D-07/D-02 deliverable, not a prompt.
> Recorded as an open question in §11.

---

## Stage C — adversarial (bundle `view:full`)

★ **Every call in Stage C is a separate call with its own prompt** (RA-15). A bear case written in
the same response as the bull case is a rhetorical concession, not an analysis — the model has
already committed to a direction and is now conceding gracefully within it.

### J-11 · Bear case — `v1`

```text
You are a short-side analyst. Your job is to establish that this is a bad
investment at this price, and you are paid on whether that turns out to be true —
not on whether it is persuasive.

You have the same bundle. You have NOT seen any bull case and must not construct
one to argue against.

  1. The single strongest reason this business is worse than its accounts
     suggest. One reason, the strongest, with its evidence.
  2. The three most load-bearing assumptions the current price requires (J-09
     supplies what the price requires), and for each: what breaks it, and what
     the observable early symptom of the break would be.
  3. What the accounts would look like two years from now if the bear case is
     correct — the specific lines, with direction and rough magnitude in the
     terms the bundle supports.
  4. ★ The falsification condition for YOUR OWN case: what observation over the
     next four quarters would establish the bear case is wrong? A bear case that
     nothing could disprove is a mood.
  5. What you would need that the bundle does not contain, and what you would do
     with it (S-4).

Do not hedge, and do not write "of course, the bull case is…". You are not
required to be balanced here; the balance is structural — this is one of several
calls and the reader sees them side by side.

Length cap: 500 words.
```

**Guards:** AP-3, INV-011, RA-15. **Checked by:** X-05 (token overlap with the bull case) and X-06
(does it name a falsifiable condition) — RM-11.

### J-12 · Pre-mortem — `v1`

```text
It is three years from today. This investment lost roughly half its value. The
loss is a fact; your task is to explain how it happened.

Do not hedge, do not assign probabilities, and do not write "if". Write the
history.

  1. The four most plausible causal paths, each as a short narrative with dates
     and the order events occurred in.
  2. For each: the earliest observable symptom, and how many quarters it
     preceded the damage.
  3. ★ Which path, if any, was ALREADY visible in the present bundle and
     dismissed? Name where in the evidence it was visible.
  4. Rank the four by how early the symptom appears — not by likelihood. The
     reader can only act on paths that announce themselves in time.

Length cap: 500 words.
```

**Provenance:** Gary Klein's pre-mortem (HBR, 2007) — prospective hindsight; imagining an outcome as
*having happened* rather than as possible measurably improves the identification of causes. Munger's
inversion is the same move.

> ★ **This is not a second bear case, and the difference is worth protecting.** J-11 argues that the
> business is worse than it looks. J-12 assumes the loss and works backwards, which surfaces paths
> an advocate would never construct — including ones with nothing to do with the business. **Item 4
> is the one the PM uses**: a risk that announces itself six quarters ahead is manageable, and one
> that announces itself the morning of is not, whatever their relative probabilities.

### J-13 · Metric-forgery hunt — `v1` — ★ parameterised over any headline metric

```text
You are a sceptical forensic analyst. You are NOT trying to establish that
<METRIC> is good. You are enumerating every mechanism by which <METRIC> could
look better than the underlying business, and stating what evidence would settle
each one.

For each mechanism below: present | absent | insufficient_evidence, with its
bundle evidence and — for anything not `absent` — the specific item that would
settle it.

  1. Leverage or capital-structure effects flattering the ratio.
  2. A shrinking denominator: buybacks, write-downs, impairments, or
     distributions reducing the base rather than the numerator improving.
  3. Non-recurring gains inside the numerator (E-04, E-07).
  4. Asset sales or revaluations booked through earnings.
  5. Reserve or provision releases (E-09).
  6. Cash conversion: does the metric's improvement appear in operating cash
     flow, and if not, where did it go?
  7. Receivables: growing faster than revenue?
  8. Inventory: growing faster than cost of sales?
  9. Accounting-policy, estimate or presentation changes (E-09).
 10. Capitalisation of costs that were previously expensed (E-09).
 11. Cyclical position: is the metric near a cycle extreme rather than a
     structural level? (J-07)
 12. Definitional: is the company's stated definition of <METRIC> the standard
     one? Quote its definition.

Then, in one sentence: what fraction of the metric's level do the mechanisms you
found `present` plausibly account for — stated as a range, with the mechanisms
named. If nothing is present, say so plainly; a clean answer here is a real
finding and you must not manufacture a concern to appear rigorous.

★ Do not speculate into fact. A mechanism you cannot evidence is
`insufficient_evidence` with the settling item named — never "possible" or
"cannot be ruled out", which are true of everything.
```

**`<METRIC>` is bound per call.** The standing set, one call each:
`return_on_equity` · `operating_margin` · `free_cash_flow` · `revenue_growth` ·
`non_gaap_eps` · `book_value` *(financials)*.

**Provenance:** ★ **This is the ROE sample in `samples/L1-research-analysis-explanation.md`,
generalised.** Its §8 *"DÙNG AI TÌM ROE GIẢ TẠO"* — *"Hãy đóng vai một nhà phân tích tài chính hoài
nghi. Đừng cố chứng minh ROE của doanh nghiệp này tốt"* — with its ten checks intact, the
per-mechanism *"chỉ ra dữ liệu cần kiểm chứng"* requirement kept as the settling item, and its
*"Không suy đoán thành sự thật"* kept as the closing rule. Schilit supplies mechanisms 3–5 and 9–10;
Sloan supplies 6–8.

> ★ **Why this earns a slot of its own rather than being folded into J-04.** J-04 asks *"is earnings
> quality good"* and selects a level; J-13 asks *"by what specific mechanism could this number be a
> lie"* and enumerates. **An assistant-trained model answers the first question agreeably and the
> second one adversarially** — same evidence, different posture, and §7.2 lists exactly that
> agreeableness as the bias this domain is most exposed to. The sample's core insight is that the
> *framing of the question* is the de-biasing instrument, not an instruction to be unbiased.

### J-14 · Disconfirming-evidence sweep — `v1`

```text
You are given the analysis produced so far. Re-read the bundle looking ONLY for
material that contradicts it. You are not weighing, not balancing, and not
concluding.

  1. Every item in the bundle inconsistent with a stated claim: the item, the
     claim, and the nature of the conflict.
  2. Every item that was available and is not cited anywhere in the analysis,
     where its content bears on a stated claim. ★ Silent omission is the
     footprint of confirmation bias, and it is invisible in the output that
     contains it.
  3. Anywhere the analysis cites part of a passage while the rest of that same
     passage qualifies or contradicts it. Quote both parts.
  4. Anywhere a claim rests on a single item that no other item corroborates.

Return findings only. If there are none, say so — but check item 2 twice before
you do, because it is the one that is hardest to see from inside the analysis
that omitted it.
```

**Guards:** §7.2 confirmation bias; RA-19 (the judging layer does not curate its own evidence — this
call verifies the consequence).

---

## Stage D — commit (bundle `view:full`)

★ **Order matters and is enforced by call order, not by prompt wording** (RA-16). J-15 completes and
is persisted before J-16 is issued. A falsifier written after a verdict is written to fit it.

### J-15 · Falsifier authoring — `v1` — ★ runs BEFORE the verdict

```text
Before any verdict exists, state what would prove the emerging thesis wrong.

Write two to four conditions. Each must be ALL of:

  observable   from data this system already receives — a filing line item, a
               computed metric, a disclosed figure. Not "sentiment worsens".
  dated        with a deadline or an evaluation window. Not "eventually".
  checkable    without a further judgement call. ★ The test: could a script
               decide it? "Competition intensifies" fails. "Gross margin below
               55% in two consecutive quarters" passes.
  material     if it fired, the thesis would be wrong — not merely dented. State
               in one line what it would mean.

For each, name the specific metric or field the check reads, choosing from the
supplied list of available observables. A falsifier naming a field this system
does not receive is not checkable, however precise it sounds.

★ At least one condition must be about the BUSINESS rather than the price. A
falsifier set that consists only of price levels is a stop-loss wearing a
thesis's clothing, and it will fire on volatility rather than on being wrong.

You may not write "the thesis is invalidated if the investment case no longer
holds" or any variant. That is a tautology and it fails the run.
```

**Guards:** RA-16, RA-35, RA-36. **Error:** `RES.THESIS.NO_FALSIFIER` when zero conditions pass.

> ★ **RM-13 is what makes this call honest over time** — the ratio of theses that died by their own
> stated condition to those quietly abandoned. **A high abandonment rate means the falsifiers were
> decorative**, and the fix is in this prompt, not in the reader.

### J-16 · Verdict selection — `v1`

```text
You have: the Stage-A scorecard and its evidence, the reconciliation (J-09), the
base-rate check (J-10), the bear case (J-11), the pre-mortem (J-12), the
forgery hunt (J-13), the disconfirming sweep (J-14), and the falsifiers you have
already committed to (J-15).

Select one verdict:
  BUY                 the evidence supports acquiring or adding at this price
  HOLD                the evidence supports neither acquiring nor exiting
  SELL                the evidence supports exiting
  INSUFFICIENT_DATA   the evidence does not support a directional view

And one conviction: Low | Medium | Medium-High | High.

Then, and this is the substance of the call:
  1. The three considerations that most determined the verdict, ranked, each
     naming the call it came from.
  2. ★ The strongest consideration pointing the OTHER way, and why it did not
     govern. If nothing points the other way, the analysis is incomplete —
     return INSUFFICIENT_DATA and say so.
  3. What would move this verdict one step more conservative, and by when.
  4. Your conviction is a claim about EVIDENCE, not about feeling. State it as:
     "of the evidence a verdict like this needs, the bundle supplied <what>, and
     did not supply <what>."

You are not sizing a position, setting a stop, setting a target, or naming an
entry price. Those belong to other domains and a number from you here would be
an LLM-authored price wearing an analyst's authority.

Length cap: 350 words.
```

> ★ **Item 4 is `confidence` with the model taken out of it.** RA-38 forbids self-reported
> confidence and RA-67 makes `confidence := evidence_coverage` until calibration exists. This
> phrasing keeps the model describing *coverage*, which is checkable, instead of *certainty*, which
> is not — and it keeps the two from being conflated in the prose even after RA-68 splits the fields.

### J-17 · Data-gap census — `v1`

```text
List everything you wanted and did not have. For each:

  gap          the specific item
  why_wanted   the judgement it would have informed
  impact       which scorecard dimension or conclusion is weaker without it
  obtainable   is this something that exists and was not fetched, something the
               company does not disclose, or something nobody knows?
  would_change what your conclusion becomes if the item existed and said X, and
               what if it said Y

★ `obtainable` sorts the list into three different actions: fetch it, accept it,
or stop pretending it is knowable. Collapsing them produces a gap list nobody
can act on, which is how the block becomes decorative.

This list may not be empty. A bundle that answered every question you had means
you did not ask enough of them.
```

**Guards:** AP-1, RA-25 (the block is mandatory and non-collapsible on the artifact).

---

## Calendar & event blocks — outside the WF-1 ladder

### J-18 · Pre-event brief — `v1` — ★ written BEFORE the event, immutable after

```text
A scheduled event is coming for a company you already have a thesis on. You are
writing this BEFORE it happens, and it will not be edited afterwards.

You are given: the thesis and its falsification conditions as written, the
assumptions it states, the event and its date, and what the market currently
expects from D-02's figures.

  1. Which falsifiers could this event resolve? Name them by ordinal.
  2. For each, in the metric's own units and FROM THE CONDITION AS WRITTEN:
       what result would FIRE it
       what result would CLEAR it
       what result would leave it UNDETERMINED
     You may not restate or reinterpret a condition to make it resolvable.
  3. Which stated assumptions does this event test?
  4. What is already expected — from the supplied figures only, never from your
     own view of what is likely.
  5. ★ What this event will NOT tell you. Mandatory, and it may not be empty.

★ You do not predict the result. A predicted result is a position taken before
the evidence, and the entire value of writing this in advance is that it is
written without knowing.
```

> ★ **Item 5 is the one that earns the call.** A quarterly result is over-read by default, and the
> only moment at which naming its limits is free is **before the number exists**. Afterwards, every
> limit sounds like an excuse. *(RA-73, RA-74, RA-75.)*

### J-19 · Industry-vs-company attribution — `v1`

```text
A metric moved. You are deciding whether that is a fact about this COMPANY or a
fact about its INDUSTRY, and the two lead to opposite conclusions.

You are given the company's change and the peer-set change over the same fiscal
periods, both pre-computed, with the peer set named and its alignment stated.

  1. State the company change and the peer-set change, in the same units.
  2. Select one:
       company_specific        the company moved and the peer set did not
       industry_wide           both moved together
       company_outperformed    both moved, the company less
       company_underperformed  both moved, the company more
       insufficient_evidence   the peer set is partially reported, not
                               period-aligned, or too small to read
  3. One sentence on what this means for the dimension it bears on.
  4. ★ If `industry_wide`: say explicitly that this is a CYCLE finding and not
     a quality finding, and name the cycle question it belongs to instead.

⚠ You are NOT judging whether the move is good. You are deciding whose move it
is. A company whose margin fell less than its peers' had a good quarter.
```

> ★★ **This is RA-92, and it is the guard for the most expensive error available to this desk.** A
> scorecard that marks a company down for an industry-wide margin compression is **wrong on every
> cyclical name, in the same direction, for as long as the cycle lasts** — and it reports 5/5
> stability while doing it, because a consistent bias survives every consistency check.

---

# 5. THE METRIC DEEP-DIVE FAMILY (D-blocks)

The ROE sample's real lesson is not about ROE. It is that **a headline metric deserves an
interrogation, and the interrogation is a repeatable shape**: decompose it, ask what produced it,
ask whether cash confirms it, ask whether it is repeatable, and ask what would end it. D-blocks are
that shape, parameterised. They are **on-demand** — invoked when a dimension's evidence is thin or
when RM-2 shows a dimension dispersing — not on every run.

## D-00 · The shape — `v1`

```text
For <METRIC>, working only from the pre-computed series and the filings:

  1. LEVEL      Where does it stand across every period in the bundle? Trend:
                rising, falling, stable, or erratic — and erratic is a finding,
                not a missing trend.
  2. DECOMPOSE  Break it into its drivers using the pre-computed decomposition.
                Which driver moved? A metric that improved because one component
                improved is a different fact from the same metric improving
                because another deteriorated more slowly.
  3. CAUSE      What in the filings explains the movement in that driver? Quote
                the company's own explanation where it offers one, and say
                whether the accounts corroborate it.
  4. CASH       Does operating cash flow move with it? A metric improving while
                cash does not is the highest-value observation in this block.
  5. DURABILITY What has to keep being true for the level to persist? Each item
                separately, each with its own evidence.
  6. COMPARE    Against its own history FIRST, then against the peer context
                supplied. ★ Cross-industry comparison of a capital-intensity-
                dependent metric is not informative; if the peer set is not
                comparable in business model, say so and compare only to history.
  7. END        What would end it? One observable condition.

Then classify:
  A  high quality and durable on the evidence
  B  sound, with a specific item to monitor (name it)
  C  flattered by leverage, one-offs, or cycle position (name which)
  D  weak or deteriorating
  insufficient_evidence
```

**Provenance:** ★ **the ROE sample's §4 prompt, generalised.** Its ten numbered requirements map to
steps 1–6 here, and its four-way A/B/C/D classification is kept intact — it is a well-designed
bounded output (RA-8) and its category C, *"ROE cao nhờ đòn bẩy hoặc yếu tố bất thường"*, is exactly
the distinction a bare number destroys. Its §6 warning about cross-industry comparison is step 6;
its §9 reinvestment-runway question is step 5.

| ID | `<METRIC>` | Decomposition used | Pairs with |
|---|---|---|---|
| **D-01m** | `return_on_equity` | DuPont: margin × turnover × leverage | J-13(`return_on_equity`) |
| **D-02m** | `return_on_invested_capital` | NOPAT margin × capital turnover; vs cost of capital | J-03 |
| **D-03m** | `gross_margin` | price/mix vs input cost vs volume, where disclosed | J-04 |
| **D-04m** | `free_cash_flow` | OCF bridge: earnings → working capital → capex | J-04 |
| **D-05m** | `revenue_growth` | volume vs price vs acquisition vs currency | J-02 |
| **D-06m** | `inventory_days` | by category where disclosed | J-07 |
| **D-07m** | `sbc_intensity` | expense/revenue; dilution net of buyback | J-06 |

> ⚠ **A D-block is only as good as D-02's published decomposition.** D-01m needs a DuPont series;
> D-04m needs an OCF bridge. **Where D-02 does not publish one, the D-block must return
> `insufficient_evidence` — it may not reconstruct the decomposition itself** (MP-6, RA-45). Which
> decompositions D-02 publishes is a real dependency and is listed in §11.

---

# 6. INVALIDATION PROMPTS (V-blocks)

The other half of D-01: watching a committed thesis for the condition that would break it. **New
evidence only** (RA-40), **prior thesis visible** (RA-39, S-9), **cheap tier by default** (RA-42).

## V-01 · Falsifier triage — `v1` — cheap tier, daily

```text
You are given a thesis's falsification conditions as written, and the evidence
that has become knowable since the thesis was authored. Nothing else.

For each condition, select exactly one:
  fired            the condition as written has occurred. Cite the evidence.
  approaching      the observable has moved materially toward the threshold
                   without crossing it. State the current value and the threshold.
  unchanged        no material movement
  not_checkable    the required observable is not in this evidence set. Say what
                   is missing.

You may not:
  - reinterpret a condition into a form the evidence happens to satisfy
  - decide a condition "effectively" fired
  - decide a condition no longer matters
  - propose a verdict, a rating, or an action

A condition you consider badly written is reported as written, with a note. It
is not your condition to fix.
```

> ★ **The rewriting failure is the one to guard against**, and it is subtle: a model asked to check
> a condition will, given ambiguity, resolve it toward whatever the evidence supports. **That is how
> a falsifier stops falsifying anything** — which is why RA-36 makes falsifiers immutable and why
> this prompt refuses interpretation four separate ways.

## V-02 · Fired-condition confirmation — `v1` — deep tier, escalation only

```text
V-01 reported that a condition may have fired. Confirm or reject, from the
evidence only.

  1. Quote the condition exactly as written.
  2. Quote the evidence, with its span.
  3. Does the evidence satisfy the condition AS WRITTEN — not as intended?
     yes | no | ambiguous_as_written
  4. If `ambiguous_as_written`: state precisely which clause is ambiguous and
     what wording would have settled it. ★ This is feedback for J-15, and it is
     the only mechanism by which the falsifier-authoring prompt ever improves.

You produce an event, not a verdict. Whether a fired condition changes the
position is the portfolio manager's decision (RA-41).
```

## V-03 · Thesis-material news classification — `v1` — cheap tier

Composes **S-9** with E-14's triage taxonomy, adding the thesis conditions as the classification
target. Escalates to V-02 only on `material_to_thesis`.

## V-05 · Unexplained-move review — `v1` — ★ the hardest rule in this file to enforce

```text
A holding moved abnormally. The move has ALREADY been decomposed for you into a
market component, a sector component, a currency component and an idiosyncratic
residual. You are given only the residual, and the evidence that became knowable
since the last analysis.

  1. Does anything in that new evidence explain the residual? For each candidate
     explanation: the evidence item, and whether its TIMESTAMP PRECEDES the move.
     ★ An item published after the move does not explain it.
  2. Select one:
       explained          a named item accounts for the residual
       partially          an item accounts for part; state what is left over
       unexplained        nothing in the evidence accounts for it
  3. If `explained` or `partially`: does the explaining item bear on a stated
     falsifier or assumption? Name it.

★★ `unexplained` IS A CORRECT AND VALUABLE ANSWER. Do not reach for a plausible
cause. You are not being asked why the stock moved — you are being asked whether
WE ALREADY HOLD EVIDENCE THAT EXPLAINS IT. Usually we do not, and saying so
tells the desk to go and find out.

⚠ You may not write "likely due to", "probably reflects", "consistent with
broader concerns about", or any phrasing that names a cause you cannot cite.
A plausible reason attached to an unexplained move is worse than the gap,
because nothing downstream can tell the two apart afterwards.
```

> ★★ **This is RA-79, and it is the block most at risk of being answered helpfully.** *"An LLM asked
> why a stock fell will always produce a reason"* is a property of the model, not a failure of
> instruction — so the prompt states the refusal three times, in three forms: the enum, the
> reframe (*"whether we already hold evidence"*), and the banned-phrase list. **Two of the three are
> checkable afterwards by X-03's lint.**

## V-06 · Weekly accumulation sweep — `v1` — cheap tier

```text
Nothing dramatic happened this week. That is the normal case and you are still
producing a report.

You are given the week's evidence delta and the current thesis state. Report
only STATE CHANGES, not events:

  drift        a falsifier's observable moved toward its threshold without
               crossing it. State the value, the threshold and the direction.
  residuals    small unexplained moves that individually breached nothing.
               ★ Report the COUNT and the direction — a fortnight of 1%/day in
               one direction is invisible on any single day.
  guidance     something previously repeated was NOT repeated this period.
               ★ An absence is a state change.
  risk_factor  a risk factor added, or one that acquired a number, a named
               counterparty or a jurisdiction.
  capacity     a sector-file row whose status transitioned (E-15).
  staleness    a thesis that crossed its staleness test this week.

★ If nothing changed, say "nothing accumulated" explicitly and list the
categories you checked. A sweep that appears only when it has something to say
cannot be told apart from a sweep that did not run.
```

**Guards:** RA-85 (accumulation, not events) · RA-86 (always emits) · RA-87 (no verdict, no
recommendation — INV-6 is untouched).

## V-07 · Assumption-state check — `v1` — cheap tier

```text
A thesis states assumptions. A series it depends on has been released. You are
checking one assumption against one release. You are not re-deciding anything.

  1. Quote the assumption exactly as written.
  2. Quote the released value, ★ AS PUBLISHED ON ITS RELEASE DATE — the bundle
     gives you the original print, not the revised figure.
  3. Select one:
       holding             the release is consistent with the assumption
       drifting            moving against it without contradicting it yet;
                           state the value, the assumed level and the gap
       contradicted        the release is inconsistent with it as written
       not_yet_testable    this release does not bear on it
  4. One sentence: if `contradicted`, what does that do to the thesis?

You may not soften an assumption to fit the data, restate it as a range, or
decide it "still broadly holds". ★ An assumption you consider badly written is
reported as written, with a note — it is not yours to fix.

⚠ You produce a STATE, never a verdict. Whether a contradicted assumption
changes the position is the portfolio manager's decision.
```

> ★ **Why this is its own block rather than an enum on V-01.** A falsifier is *checkable and
> binary*; an assumption can **drift** for months without ever being contradicted, and `drifting` is
> the state that carries the information. Folding it into V-01 would have forced a continuous thing
> into a fired/not-fired shape and lost exactly the signal worth having.

## V-04 · Staleness attestation — ★ **not a prompt**

Deterministic: `now − thesis.as_of > STALENESS_FILINGS_HOURS ⇒ stale`, rendered on the card
(RA-43). Listed here because it is the check most likely to be implemented as a call by someone
reading a list of prompts and finding no entry for it.

---

# 7. VERIFICATION PROMPTS (X-blocks) — and what must not be one

## X-06 · Bear-case substance — `v1` — deep tier, narrow

```text
You are given a bear case. Answer three questions about it. You are not
evaluating whether it is correct.

  1. Does it name at least one condition that is observable, dated and checkable
     without a further judgement call? Quote it, or answer no.
  2. Does it identify a mechanism, or only a mood? A mechanism names what
     changes, in what order, with what effect. "Competition could intensify" is
     a mood. Quote the mechanism, or answer no.
  3. Does it rest on any evidence the bull case does not also use? Name it, or
     answer no.

A `no` on question 1 fails the run (RM-11).
```

## X-07 · Claim–span agreement — `v1` — deep tier, sampled

```text
For each claim/span pair: does the quoted span support the claim as stated?

  supports          the span states or directly implies the claim
  partial           the span supports part of it; state which part is unsupported
  contradicts       the span says something inconsistent with the claim
  unrelated         the span does not bear on the claim
  span_not_found    the span is empty, malformed, or outside the document

You are not checking whether the claim is true. You are checking whether THIS
span is why anyone should believe it.
```

> ★ **`partial` is the value of this check.** Fabricated citations are rare and easy to catch
> deterministically (X-01). **The common failure is a real span that supports a weaker statement
> than the one it is attached to** — a directional quote cited for a magnitude, a segment figure
> cited for the company. No string match finds that.

## What must never be a prompt

| Check | Why it must be code |
|---|---|
| X-01 value-in-span | It is `in`. An LLM here is slower, dearer, and can be wrong |
| X-02 every fact has a span | Schema validation. A model asked to check its own citation completeness has an interest |
| X-03 forecast-voice lint | A fixed wordlist. RA-26 wants zero violations, and a stochastic linter cannot deliver zero |
| X-04 length caps | `len()` |
| X-05 bull/bear token overlap | A set intersection. RM-11 wants a number that moves for one reason |
| Verdict monotonicity (P3) | An ordering on an enum. **The one check that must never depend on a model, because it is the safety property** |
| Confidence floors (RA-38) | Computed from `evidence_coverage`. ★ Asking the model would let it raise its own ceiling |

---

# 8. PERTURBATION VARIANTS (RA-61/RA-62)

★ **The stability probe does not resample the decoder — it restructures the input.** RA-61 settles
this: same k× cost, but it measures a property of the analysis rather than of the sampler. Each
variant is generated **deterministically from `(bundle_hash, prompt_id, variant_index)`** so the
perturbation itself is reproducible and recorded on the `AnalysisRun`.

| Variant | What is perturbed | What a flip means |
|---|---|---|
| **P-1 option order** | Rubric levels and enum options presented in a recorded permutation (RA-17) | ★ Position bias. A verdict that changes with option order is not reading the criteria |
| **P-2 evidence order** | The order of items within each bundle section; content identical, `bundle_hash` unchanged | Recency/primacy within the context. A flip means one document is dominating by position |
| **P-3 paraphrase** | A pinned alternate wording of the task block at the same prompt version, stored beside it in this file | The judgement is tracking the phrasing, not the question |
| **P-4 distractor null** | An immaterial bundle item (E-14 `noise`) is added or removed | ★ A flip on immaterial input is the strongest available evidence the answer is not evidence-driven |
| **P-5 unit/format** | Figures presented in thousands vs millions, dates ISO vs long form | Should never flip. If it does, something is being pattern-matched rather than read |

| ID | Rule |
|---|---|
| **MP-8** | ★ **Each perturbation is generated from a recorded seed and is replayable.** A stability figure produced from perturbations nobody can reconstruct is a number, not a measurement |
| **MP-9** | **P-3's paraphrases are versioned artifacts in this file, not generated at call time.** A paraphrase written by a model at call time makes the probe's baseline move on its own |
| **MP-10** | ★ **P-1 and P-4 are the two that must always run.** They are the cheapest and they test the two claims the reader most relies on: that the criteria were read, and that the answer follows the evidence |

> ★ **What this buys that resampling did not.** Under `L2-shared-infrastructure.md` GW-8's production
> settings, resampling the same input measures the decoder, and §7.4b establishes that as a property
> of a setting rather than of the analysis. **Perturbation measures robustness to things that should
> not matter** — and `perturbation_stability` is the figure that belongs on the card (RA-62), because
> a verdict that flips when the options are reordered is fragile in a way the reader must see.
> *(See §11 QP-1: the gateway's current temperature rule needs re-examining against Opus 5, which
> rejects the parameter outright — which makes perturbation not merely the better probe but the only
> one available.)*

---

# 9. THE ALIGNMENT MANIFEST (INV-9)

`prompt_alignment.py` is inherited **verbatim** (RA-13, §4 of the governing spec). What it checks
must be extended from one document to this registry:

| ID | Rule |
|---|---|
| **MP-11** | **Every block in this file is hashed individually** — shared blocks (§2) and task blocks alike. A call's alignment key is the ordered list of block ids and their hashes |
| **MP-12** | **A call site declares its composition** (`["S-1","S-2","S-3","S-4","S-5","S-6","S-7","J-03"]`) and the checker rebuilds the prompt from this file. ★ The prompt text does not live in the Python at all — a call site that carries prompt text has already drifted |
| **MP-13** | **A block hash change reds every call that declares it, and only those.** This is the reason for composition: editing `S-5` should not invalidate the extraction baselines, and today it would |
| **MP-14** | ★ **A prompt change requires an RM-4 regression run against the pinned bundle set before release** (AC-1.9). **The pinned bundle set is a real artifact that must exist** — without it RM-4 is an intention. It needs: ≥1 name per archetype (J-01), ≥1 with a fired falsifier, ≥1 `INSUFFICIENT_DATA`, ≥1 with a known accounting red flag, and ≥1 where the two seats disagreed |
| **MP-16** | ★ **A prompt VARIANT is a new, versioned block — never an edit to an existing one.** `J-03@v2-outcome-weighted`, not a changed `J-03@v1`. ★ **The alignment checker then becomes the admission test for free**: it already refuses a call whose composition has drifted, so a variant that tried to mutate a block in place fails before it runs. *(D-10 intent `XP-44`; prompts are variants per QX-4.)* |
| **MP-17** | ⚠ **A SHARED-block variant (`S-1…S-9`) is a whole-system variant.** MP-13 means a change to `S-5` reds every call declaring it — so its sweep must cover **every call type**, not only the one that motivated it |
| **MP-15** | **Rubric YAML is versioned with the prompts that select from it** (RA-33). A rubric edit and a prompt edit are the same class of change: an unversioned change to the analytical method |

---

# 10. SOURCE BIBLIOGRAPHY

What each external source contributes, so a future reader can check the derivation rather than trust
it. **None of these is authoritative here** — the governing spec is. They are where the *questions*
come from.

| Source | Contributes | Used in |
|---|---|---|
| [CFA Institute — *Equity Research Report Essentials*](https://www.cfainstitute.org/sites/default/files/-/media/documents/support/research-challenge/challenge/rc-equity-research-report-essentials.pdf) | The section inventory of a professional report; footnote reading as the core of earnings-quality work; the explicit warning against extrapolating a cyclical from its current point | §4 overall, J-04, J-07 |
| [Pat Dorsey — five sources of moat](https://quartr.com/insights/investment-strategy/pat-dorsey-economic-moats-and-beyond) (Morningstar) | The moat taxonomy: intangibles, switching costs, network effects, cost advantage, efficient scale | J-03 step 1 |
| [Bruce Greenwald — *Competition Demystified*](https://poundtherockinvesting.wordpress.com/2018/10/06/introduction-to-the-value-investing-process-a-lecture-by-bruce-greenwald/) | Barriers to entry as the dominant force; the two empirical tests — **stable market share + persistent excess returns** | J-03 step 2, J-08 item 2 |
| [Michael Mauboussin — ROIC and the investment process](https://www.morganstanley.com/im/publication/insights/articles/article_roicandtheinvestmentprocess.pdf) · [base rates](https://excessreturnspod.substack.com/p/michael-mauboussin-the-benefits-of) | Reverse-engineering the expectations in the price; ROIC vs cost of capital and its mean reversion; the outside view | J-09, J-10, J-06, D-02m |
| [Aswath Damodaran — *Narrative and Numbers*](https://cup.columbia.edu/book/narrative-and-numbers/9780231180481/) | The coherence test between the story and the model; life-cycle-appropriate metrics | J-09 |
| [Howard Schilit — *Financial Shenanigans*](https://rpc.cfainstitute.org/research/multimedia/2010/financial-shenanigans-how-to-detect-accounting-gimmicks-and-fraud-in-financial-reports) | The manipulation families: premature/bogus revenue, one-time gains as operating, expense shifting, understated liabilities | J-04 step 2, J-13 |
| [Richard Sloan — the accrual anomaly](https://www.stockopedia.com/content/the-accrual-anomaly-why-investors-should-care-about-accruals-earnings-quality-63003/) | Cash and accrual components of earnings differ in persistence — the basis for the cash test | J-04 step 1, J-13 items 6–8 |
| [Piotroski F / Beneish M / Altman Z](https://www.nature.com/articles/s41599-024-03888-4) | The *variable sets* that distinguish improving from deteriorating, manipulated from clean, solvent from distressed | J-05, J-13 — ★ **as question lists only; D-01 computes no score** (MP-6) |
| [William Thorndike — *The Outsiders*](https://quartr.com/insights/business-philosophy/unconventional-ceos-william-thorndike-s-book-the-outsiders) | Capital allocation as the measurable half of management quality; cash flow per share over reported earnings; buyback price discipline | J-06 |
| [Philip Fisher — the fifteen points & scuttlebutt](https://www.tradejini.com/blogs/the-philip-fisher-approach-to-owning-stocks-like-a-business-owner) | Qualitative questions a filing can partly answer: R&D productivity, margin defensibility, management depth, candour in bad news | J-02, J-06 |
| [Peter Lynch — the six categories](https://thesisrationale.substack.com/p/super-investor-series-peter-lynch) | Classify before analysing; expectations follow from the category | J-01 |
| [Gary Klein — the pre-mortem](https://www.gary-klein.com/premortem) | Prospective hindsight: assume the failure, explain it. Materially better at surfacing causes than asking what could go wrong | J-12 |
| [Kill criteria / pre-commitment](https://www.kubera.com/blog/investment-thesis) | A thesis states what must be true **and what would prove it wrong**, chosen before the outcome | J-15 |
| [CFI — AI prompts for stock analysis](https://corporatefinanceinstitute.com/resources/artificial-intelligence-ai/best-ai-prompts-for-stock-analysis/) | Task decomposition into narrow prompts; the trace-back/sourcing prompt; guidance-scorecard tracking | §1 structure, E-12, J-06 item 6 |
| [Prompt Engineering for Equity Investors](https://davidwang95.github.io/Equities_Prompting_Ebook/) | "Using only the data provided" as the grounding stem; explicit format and length specification; requesting both directions separately | S-2, S-5, S-6 |
| [Brightwave — high-impact prompts for financial analysis](https://www.brightwave.io/blog/prompting-for-performance-part-ii-crafting-high-impact-prompts) | Constraining focus and supplying factual grounding as the primary hallucination controls | S-2 |
| [AI in Investment Analysis: LLMs for Equity Stock Ratings](https://arxiv.org/pdf/2411.00856) | Structured input ordering — text first, then numeric tables — measurably improves financial reasoning | §3.0, S-2 |
| [FinDebate: multi-agent collaborative financial analysis](https://arxiv.org/pdf/2509.17395) | Separate adversarial roles beat one balanced role | J-11, J-12, J-14 as distinct calls |
| **`samples/L1-research-analysis-explanation.md`** | ★ **The depth standard for this file.** The metric-interrogation shape (D-00), the sceptic's twin prompt (J-13), the four-way quality classification, "compare to itself first", the reinvestment-runway question, and the insufficient-data instruction (S-4) | D-blocks, J-13, J-04 step 4, S-4 |
| `pipeline/buffett/synthesis/prompt_stock_analysis.md` | The archetype table, cycle rules, supply-side read, differential view, 10b5-1 checking, headline tagging | J-01, J-07, J-08, J-09, E-08, E-14 |

---

# 10A. ★ GENERATING THE RELAY PROMPT — QP-8 closed

> ✅ **Decided 2026-08-23:** [`L1-fundamental-analysis-relay-prompt.md`](L1-fundamental-analysis-relay-prompt.md)
> is **a rendered artifact, not a source.** It is generated from the blocks in this file, so a fix
> made here reaches the chat window without anyone remembering to copy it.

## 10A.1 ★ Where the transport difference actually lives — and it is smaller than it looks

The relay runs in a chat with web search; the API path runs on a pinned bundle. That is a real
contradiction, so the first question is **how much of the registry it contaminates.**

★ **Almost none of it.** The conflict is confined to the **shared blocks**:

| Block | Relay status | Why |
|---|---|---|
| **S-2** grounding contract | ⚠ **REPLACED** | *"You have no browser… every ratio is supplied pre-computed"* is false in a chat |
| **S-6** output contract | ⚠ **REPLACED** | Structured outputs do not exist; a fenced JSON block does |
| **S-7** anti-anchoring | ⚠ **REPLACED** | The field cannot be absent, so it becomes an instruction (RA-119) |
| **S-1, S-3, S-4, S-5, S-8, S-9** | ✅ **verbatim** | Role, citation discipline, insufficient-evidence protocol, voice, no-prior-verdict — ★ **all transport-agnostic** |
| **E-01…E-15, J-01…J-19** | ✅ **verbatim, under substitution** | *"Assess whether this company can defend its pricing"* does not care who fetched the filing |

> ★★ **That table is the finding.** *Three* shared blocks carry the entire difference between an API
> call and a chat window. **The task blocks — the actual analysis — are transport-agnostic as
> written**, which means generation is composition plus a small substitution, not a rewrite.

## 10A.2 The rules

| ID | Rule |
|---|---|
| **RG-1** | ★ **The relay prompt = a hand-written RELAY PREAMBLE (replacing S-2/S-6/S-7) + the selected E/J blocks VERBATIM + the archetype block + the return schema.** Nothing else. The preamble is written once; every task block is carried unchanged |
| **RG-2** | ★★ **A CLOSED substitution map is the only place transport differences may live**, declared in one table (§10A.3) and applied uniformly. ⚠ **A block needing a bespoke relay rewrite is not a generation problem — it is a signal the BLOCK is transport-coupled**, and the fix belongs here, not in the renderer |
| **RG-3** | **Generation is deterministic and byte-reproducible.** Same registry version ⇒ same output (INV-2 applied to a document) |
| **RG-4** | ★ **CI regenerates and diffs.** A hand edit to the generated file fails the build. ⚠ *Without this the generated file becomes a source again within a month, and nobody notices until the two disagree* |
| **RG-5** | **The rendered file records its provenance**: registry version, the ordered block list with each block's version, and the substitution-map version — so a pasted prompt is attributable to exact block versions (RA-122) |
| **RG-6** | ★ **Stage collapse is ORDERING plus one instruction, and the rendered file says it is weaker** (RA-119). Generation does not get to quietly imply otherwise by omitting the caveat |

## 10A.3 The substitution map — `v1`

Applied to every task block on render. **Closed set; adding a row is a change to this file.**

| In the registry | In the relay | Why |
|---|---|---|
| `the bundle` | `your sources` | there is no bundle |
| `<computed_metrics>` | `the figures you have gathered` | the model gathers rather than receives |
| `Do not compute…supplied pre-computed` *(S-2 r.3)* | *(dropped — the preamble covers it)* | ⚠ **the one place D-01's no-arithmetic rule genuinely cannot hold**, and §4B accepts it |
| `evidence_span` / `offset` | `source and date, inline at the point of use` | offsets into documents we do not hold map to nothing |
| `Return through the provided schema` | `end with a fenced json block matching…` | no structured outputs |
| `view:blind` | `Do not look up the price until Part B` | RA-119 — an instruction, not a guarantee |

## 10A.4 The composition — what the current file is made of

| Rendered section | Source |
|---|---|
| Ground rules 1–8 | ★ **relay preamble** (replaces S-2/S-6/S-7) + **S-3**, **S-4**, **S-5** verbatim |
| Part A: A1 · A2 · A3 · A4 · A5 · A6 | **J-01 · J-02 · J-03 · J-04 · J-05 · J-06** |
| Part A: A7 | archetype block, selected by J-01 (RA-123) |
| Part A: A8 | **J-17** |
| Part B: B1–B4 | **J-09** |
| Part C: C1 · C2 · C3 | **J-11 · J-12 · J-13** |
| Part D: D1 · D2 | **J-15 · J-16** |
| Return schema | **CT-1.5** + the §5 ingest contract |

⚠ **Three blocks are deliberately NOT rendered**, and the omissions are decisions:

| Omitted | Why |
|---|---|
| **J-10** base-rate check | It reports an absence in every run (**QP-4**) — a whole section that always says *"the bundle contains no base rate"* trains the reader to skip sections |
| **J-14** disconfirming sweep | ★ It reads *the analysis produced so far* — impossible inside the single pass that produced it. **Restored by the two-paste form**, where Pass B can see Pass A |
| **J-19** attribution | Needs a period-aligned peer set the chat cannot assemble reliably (**RA-96a** — MU's August year-end) |

## 10A.5 ⚠ The honest cost of this decision

★ **A hand-written prompt reads better than a composed one, and the current file is hand-written.**
Concatenated blocks repeat themselves, change register between sections, and lose the connective
sentences that make a long prompt feel like one instruction rather than a checklist.

**This matters more than usual here**, because the artifact is pasted by a human who has to want to
use it — ★ **a protocol that is not run has zero assurance**, whatever its provenance.

**The mitigations, and what remains:**

| Mitigation | |
|---|---|
| **RG-1** puts the connective prose in the **preamble**, hand-written once | ✅ recovers most of it |
| Task blocks are already written in the imperative voice that works in both | ✅ |
| The renderer may insert **fixed section headers and transitions** from a template | ✅ |
| ⚠ **What does not survive** | Per-section tuning — a sentence that reads well *only* in the relay has nowhere to live, because RG-2 forbids bespoke rewrites |

> ★ **If that turns out to bite, the fix is to improve the BLOCK, not to fork the render** — which is
> RG-2 doing its job. **A relay-only sentence that would not survive in the registry is usually a
> sentence that was compensating for a weak block.**

## 10A.6 When

**`L3` B4.8**, with the relay itself. Until then the checked-in file stays hand-written and is
marked as such — ⚠ **and it is the one file in this set that will drift**, because nothing yet
regenerates it.

---

# 11. WHAT THIS FILE DOES NOT CONTAIN — and open questions

**Deliberately absent, because they belong to other domains:**

- **Any valuation prompt.** Fair value, mid-cycle earnings, reverse-DCF, peer multiples and the
  method-weighting table are D-02's (P2, AP-5, RA-45). J-09 *reads* D-02's output; it does not
  produce one. ★ This is the largest single deletion from the legacy mega-prompt, whose Rules 7–9
  and Section 5 are all arithmetic.
- **Any stop, target, entry zone or position size.** D-06 and SEAT-1. The legacy prompt's Rule 11
  derived a stop from an LLM-authored bear-case price — three stacked judgements presented as a
  number, which `L1-reporting.md` §6.2 is already moving to a quantile model.
- **Any technical-analysis prompt.** D-03's domain; INV-014 forbids D-01 consuming its output and
  symmetry forbids D-01 producing a competing one.
- **The ETF tripwire construction.** Observable price conditions are computations. What survives is
  the *idea* that a falsifier must be observable — J-15 — and at least one must be about the
  business rather than the price.
- **Any report-rendering instruction.** D-09 renders (DC-1). A prompt that specifies layout is a
  renderer authored in the wrong domain.

| ID | Open question |
|---|---|
| ~~**QP-1**~~ | ✅ **CLOSED 2026-08-23.** `L2-shared-infrastructure.md` §5.2a amends GW-8/GW-9: the two tiers take **mutually exclusive** controls — `temperature` on Haiku, `effort` on Opus 5. **RA-60 corrected, RA-60a added**, and `CT-1.2` carries `decoding` as an object mirroring **CT-0.1**, so `temperature: null` reads as *not settable* rather than *forgotten*. ⚠ **Raised 2026-08-20, fixed 2026-08-23 — it took a B0 readiness review to route it to the spec that owned it.** That is the cost of logging a defect against the domain that *notices* it rather than the one that *owns* it |
| **QP-2** | ⚠ **Native document citations and structured output are mutually exclusive in one API call.** RA-9's `evidence_span` with real character offsets is available natively — but only on a call that is *not* using a structured-output schema. This forces the E/J split to be an API-level split too, which is convenient (RA-5 wanted it anyway), and it means a judgement call **cannot** emit machine-verified spans of its own. QP-2 is: do judgement claims cite by `evidence_id` into extraction output only? *(Recommended: yes — it makes RA-7 structural)* |
| **QP-3** | Which decompositions does D-02 publish? D-01m needs DuPont, D-04m needs an OCF bridge, J-06 needs incremental-capital-vs-incremental-profit, J-09 needs the reverse-engineered expectations. **Each absent one turns a prompt into an `insufficient_evidence` generator** (MP-6 forbids the alternative) |
| **QP-4** | J-10's reference classes need a base-rate dataset the single-company bundle does not contain. Leave J-10 reporting absences, or extend D-07? |
| **QP-5** | The four scorecard dimensions (RA-52) cover the business. ★ **Nothing scores whether the price-to-story gap is justified** — which is the second half of §1.1's question. Is the reconciliation (J-09) deliberately unscored, or is there a fifth dimension? *(RA-52 closes the set, so this is an amendment question, not an implementation one)* |
| **QP-6** | Prompt-block IDs `MP-`, `S-`, `E-`, `J-`, `D-`, `V-`, `X-`, `P-` are **not registered in `L0-system-vision.md` §16.1**, and `D-` collides visibly with the domain family `D-01…D-12` (this file uses `D-01m` for the metric block to avoid it). Register or rename before this file is cited from elsewhere |
| ~~**QP-8**~~ | ✅ **CLOSED 2026-08-23 — the relay prompt is GENERATED from these blocks** (Victor). §10A below is the mechanism |
| **QP-9** | ⚠ **MP-14's pinned bundle set now needs THREE roles, not one** — `regression` (gates a release, never used to choose), `selection` (what a sweep iterates against), `confirmation` (held out, touched once at promotion). **Without the split every promoted prompt is promoted on the set it was fitted to.** *(D-10 intent `XP-48`.)* |
| **QP-7** | Retention: RM-4/RM-5 need historical bundles to re-run against, and MP-14's pinned set must survive prompt versions. The L1 spec's QR-7 is the same question from the other side |
