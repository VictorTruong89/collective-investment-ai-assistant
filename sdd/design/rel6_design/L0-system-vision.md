# L0: System Vision — AI Investment Pipeline

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> This is a candidate L0 under adaptation. The authoritative statement of *what* is being
> built remains `sdd/specs/vision.md` until this file is promoted into `sdd/specs/`.

## Document Control

| Version | Date       | Author       | Changes                                                              |
|---------|------------|--------------|----------------------------------------------------------------------|
| 0.22.0  | 2026-08-21 | Victor       | ★★ **Seats renumbered and renamed.** The human seat is now **SEAT-1** — it was third, between the two AI analyst seats, which read as a pipeline stage rather than the seat every other seat reports to. **Fundamental Analyst = SEAT-2, Quantitative Analyst = SEAT-3, Risk Management = SEAT-4, Back/Middle office = SEAT-5.** *"Research Analyst" → "Fundamental Analyst"* (symmetry, and `src/fundamental/` already said so); *"Risk" → "Risk Management"*. **371 references updated across 17 files.** ★ **§1.6 retitled "The THREE Analyst Seats"** — Risk Management analyses the *book*, and **its independence rule is the opposite of the other two: it must see both, and INV-026's zero authority is what makes that safe.** ⚠ **"How are the outputs combined?" had read DEFERRED since v0.17.0 added the domain that closed it** — now DECIDED: **D-12**, three inputs, composes and originates nothing. **D-12 added to the §2.1 and §4.1 diagrams**, where it was missing from both. ★★ **§4.2 — the valuation split (VS-1…VS-5)**: *"D-01 interprets, never computes"* was too clean and had already produced a live contradiction with `L1-fundamental-analysis.md` §8.1. **Split by determinism, not topic: `fv_model` (D-02, neutral, both seats may consume) vs `fv_analyst` (D-01, opinion, no analyst seat may consume).** Moat/quality **inputs** stay D-02; the **rubric selection** is D-01's. **VS-4: D-01 contains deterministic code — the rule is no arithmetic in a *prompt*, and none that is judgement-free.** ★ **D-10 Experiments moved seat 3 → seat 5** so it can serve all three analyst seats (§1.2). ★ **§1.4 — seven PROPOSED mandates M-6?…M-12?** from a CFA-IPS cross-check, none adopted. **§12.1 — TSX and Canada added to future scope, with the D-07 sourcing cost stated.** |
| 0.21.0  | 2026-08-18 | Victor       | ⚠ **New §17.5a — the F-tier was deleted** (Victor's decision), ending two live spec sets. **This departs from G-7** — which retires an F-spec only when its code is deleted — and the departure is recorded rather than glossed. ★ **Consequence stated plainly: `pipeline/**` is no longer spec-governed**, and its globs were *removed* from `ownership.yaml` rather than left stale, because a stale glob makes the gate **fail open silently** (ST-8). Carried over first: **`D-19`** (already in FE-18) and **`AC-4.9` → `AC-M.1`** with its 19 tests. **Not** carried: F0's code map (and its 33 tests). New **G-8** (F-citations are historical provenance, not readable references) and **G-9** (`pipeline/**` is ungoverned by design). |
| 0.20.0  | 2026-08-18 | Victor       | ★ **`L3-build-sequence.md` written — the last open design item.** Claims the unused **L3** tier: it consumes L1/L2 (what to build) and L4 (how files move) and produces the **execution order**. Closes **§17.6's phase-ordering deferral** and `L4` **Q-3**. ⚠ **§17.6 also had a stale bullet** — it still listed the combine point as *"the largest open question in the design"* two versions after D-12 answered it; corrected. Families `BS-` / `QY-` registered in §16.1. |
| 0.19.0  | 2026-08-18 | Victor       | ★ **`L2-shared-infrastructure.md` written — the last unspecified domain.** D-00 had one of its four duties covered (`L2-shared-money.md`); the LLM gateway, configuration, logging and secret handling had **no spec**, while **INV-8, INV-9, INV-034, AP-5/ST-5 and D-01's `RA-60` all pointed at it**. Families `SI-`/`GW-`/`CF-`/`LG-`/`SC-` and questions `QI-` registered in §16.1. **Every registered domain is now specified except D-10, which is deliberate (§4.2).** |
| 0.18.0  | 2026-08-18 | Victor       | ★ **New §4.4 — Clean Architecture adopted as the *Dependency Rule*, not the folder taxonomy.** States that there are now **two orthogonal dependency rules** — the horizontal domain axis (§4.3) and the vertical layer axis — and that a file is legal only if it satisfies both. Records honestly where Clean Architecture **does not** apply to a numerical pipeline: **the DataFrame is the domain model**, not a framework detail. Concrete rules `CA-1…CA-9` in `L4` §18. Assessed after D-12 by decision, so the new domain was in the tree first. |
| 0.17.0  | 2026-08-18 | Victor       | ★ **New domain D-12 Decision (SEAT-5, LEVEL 1)** — `L1-decision.md`, closing `L2-signal-combination.md` **QB-5**. It owns the composition step, which had no correct home: every existing domain is the wrong owner for a stated reason, and D-09 owning it is how a renderer starts deciding (DC-5). Placed in SEAT-5 by **the same argument that placed D-02** — a neutral layer that privileges neither analyst seat. **New forbidden edge in §4.3: nothing may feed D-12's output back to D-01 or D-03.** Twelve domains. |
| 0.16.0  | 2026-08-18 | Victor       | ★ **§1.6's deferred question is answered** in the new `L2-signal-combination.md` (families `CB-`/`QB-` registered in §16.1). The combination is **quant ranks → thesis gates → risk alerts**, derived from **coverage economics** rather than from the P3 ordering that was withdrawn in Aug 2026: D-01's coverage is `O(1)/day` and conditioned on D-03's output, so it carries **zero cross-sectional ranking information**, and dense coverage costs **6.3–19 % of NAV per year**. §1.6's deferral text stays as history; the answer lives in the L2. |
| 0.15.0  | 2026-08-18 | Victor       | **`L4-coding-standards.md` §5, §10, §14, §17 written.** Four new L4 rule families registered in §16.1 per **T-7**: `EH-` errors · `IM-` imports · `CN-` constants · `PD-` pandas. |
| 0.14.0  | 2026-08-18 | Victor       | **QO-7 closed: the decision anchor moves to the open** — labels become `open(T+h)/open(T) − 1` (D-03 §5.9, D-04 §6.3/§8.1, D-02 §5Z). **D-10 Experiments is deliberately left unspecified** (§4.2): it is the one domain whose content is unknowable before the first E2E run, and the **one-way import rule ST-2 — not a spec — is what makes that safe**. |
| 0.13.0  | 2026-08-18 | Victor       | **Production cadence decided** (Victor): daily **10:00 ET** consuming the **day-T open**, retrain the **1st of every month**, orchestration **in-process behind a thin external timer**. Recorded in `L1-orchestration.md` **§5A** (closes QO-3, QO-5). §4.3's *"never computes"* edge is **kept unchanged** — the two entrypoints are **redesigned rather than repaired**, so nothing in §1.5's inventory is grandfathered. The cadence fixes the **decision anchor** and thereby opens **QO-7** against D-03/D-04: the decision is now taken at the open while the label is anchored on the close, and **INV-4 does not permit both**. |
| 0.12.0  | 2026-08-18 | Victor       | **`L1-orchestration.md` (D-08) written.** `QO-` registered in §16.1; §15 registry updated. §4.3's *"never computes"* edge now has a spec that names **ten functions currently violating it**, and D-08 is assigned ownership of the **RunManifest** — the only layer at which constitution **INV-2 (determinism)** is enforceable, since reproducibility is a property of the whole invocation rather than of any one domain. |
| 0.11.0  | 2026-08-18 | Victor       | **`L1-risk-management.md` (D-05) written.** §4.2's D-05 entry corrected — it still claimed the sizing arithmetic that has belonged to **D-06 since v0.6.0** (stranded v0.5.0 text; closes **QK-1**). `QK-` registered in §16.1; §15 registry updated. |
| 0.10.0  | 2026-08-15 | Victor       | **D-09 split into two domains at the same level, both under SEAT-5**: **D-09 Reporting** (narrowed — render, deliver, the read surface) and **D-11 Recording** (new — book, reconciliation, trade log, journal, attribution). The cut follows §3.1's own dividing line: recording is LEVEL 0 AUTONOMOUS custody of fact, reporting is LEVEL 1 RECOMMEND. Eleven domains. Cascaded through §1.5, §1.6, §3.1, §4.1, §4.2, §4.3, §5.1, §5.1a, §16.2, §17.5, and the `L4` file structure and migration table. |
| 0.9.0   | 2026-08-15 | Victor       | **D-02 redefined: Valuation (SEAT-2) → Feature Engineering (SEAT-5)**, cascading the decision `L4-coding-standards.md` v0.3.0 already made and `L1-data-engine.md` already draws. Valuation is now a sub-area of D-02, tombstoned per T-2. **D-10 Experiments (SEAT-3, P7-exempt) added** — it existed only in L4, which T-7 forbids. Cascaded through §1.5, §1.6, §4.1, §4.2, §4.3, §16.1, §16.2. **INV-014 wording fixed** (closes L4 Q-8). §14 repointed at files that exist; §16.4 corrected (the §6.3 gap it lists was closed in v0.8.0). **New §17 — Tier & governance**: how this document relates to `sdd/specs/vision.md`, `constitution.md`, the F-specs and `ownership.yaml`, and what promotion requires. |
| 0.1.0   | [DATE]     | Claude Opus 4.6 | Initial draft (written without knowledge of the existing codebase) |
| 0.2.0   | 2026-08-13 | Victor       | Adapted to the actual fund: added §1.4 **The Mandate** and §1.5 **The seats** (both from `sdd/specs/vision.md` §2–§3); reconciled §5.1, §7.3, §8 and §12 with the mandate. |
| 0.3.0   | 2026-08-13 | Victor       | Merged Portfolio Manager and Execution Trader into **one human seat** (neither requires code). Assigned the **Discipline Card** to the Report Writer Agent under new **§5.1a**, bounded by DC-1…DC-5. |
| 0.8.0   | 2026-08-13 | Victor       | **Constitution P3 narrowed** to "Verdicts gate, never upgrade" — the quant-ranks-then-thesis-gates *ordering* is no longer a constitutional rule (51 gate tests still pass); `CLAUDE.md` updated. **AP-5 sharpened** and shown to be complementary to constitution P5, not competing. **M7:** report generation moved LEVEL 0 → **LEVEL 1 RECOMMEND**; Report Writer Agent is now RECOMMEND throughout and the DC-2 carve-out is retired. **M9:** §6.3 removed (§8 is authoritative for freshness); two sibling citations repointed. **M10:** dashboard retained as an intended-but-unspecified capability. **M11:** 14 terms added to the glossary. |
| 0.7.0   | 2026-08-13 | Victor       | **Added §16 — ID families & traceability** (M-, SEAT-, D-, AP-, DC-, DQ-, INV-, AC-, CT-), with **D-01…D-09 assigned to the nine domains** and rules T-1…T-7. **Renamed agent principles `P1`–`P6` → `AP-1`–`AP-6`** — `P1`–`P7` already mean different things in `sdd/specs/constitution.md`. **Deleted §9 (Phased Delivery) and §10 (Quality Attributes)**; numbers left vacant so sibling citations do not silently redirect. |
| 0.6.0   | 2026-08-13 | Victor       | **Portfolio Strategy restored as a domain under seat 4** (not an agent) — nine domains; agent count stays four. **INV-001 and INV-027 merged** into a single amount+currency invariant. **§2.2 rewritten for EDGAR + FMP only** (EDGAR primary for TTM; no vector DB, no news vendor, no brokerage API). **Options and brokerage integration struck from §9.2 Phase 6** per M-1. **§6.2 and §11.1 fixed to Parquet + JSON on local disk** — no database, no cache server, no vector store. |
| 0.5.0   | 2026-08-13 | Victor       | **Structural pass — resolved C1–C6.** §1.6 separates *independent production* (decided) from *combination* (deferred). **INV-014** and **§4.3** rewritten to forbid inheriting the other seat's *judgement* while explicitly permitting shared *data*. **Portfolio Strategist Agent removed** — seat 1 has no agent; sizing arithmetic moves to Risk. §4 rebuilt: **eight domains mapped to owning seats**; seat 2 = Fundamental Analysis + Valuation, seat 3 = Quantitative Analysis + Model Training & Inference, seat 5 = Data Engine + Orchestration + **Recording & Reporting** (renamed from "Execution & Reporting"); **Portfolio Strategy domain deleted**. DC-1/DC-4/DC-5 made combination-agnostic. |
| 0.4.0   | 2026-08-13 | Victor       | Split the analyst function into **two seats** — 1 Fundamental Analyst (fundamental) and 2 Quantitative Analyst (ML ranking) — restoring **five seats**, now **one agent per seat**. Added **§1.6** defining the two analyst seats by unit-of-analysis and method, with a provenance map to the existing codebase (`buffett/` + `fundamental_analysis/` → seat 2; `ohlcv/` three-model bundle → seat 3). How the two views combine is **deferred**. |

> **Section numbers here are load-bearing.** §§4.2, 4.3, 6.2 and 12 are cross-referenced *by number*
> from `L1-data-engine.md`, `L2-shared-money.md` and `L4-coding-standards.md`. That is why the
> mandate and the seats were added as §1.4–§1.6 rather than as a new top-level §3, why §§9–10
> were left **vacant** rather than renumbered when they were deleted, and why v0.9.0 appended §17
> rather than inserting it.
>
> *(The pre-0.9.0 version of this note also listed `L2-data-validation.md`,
> `L4-ai-agent-design-standards.md`, `L4-financial-calculation-standards.md` and
> `L4-data-pipeline-standards.md`. Those live in `samples/` and are **format references only** —
> their details and values do not apply here (§17.1). They cite section numbers of the generic
> template this document was adapted from, not of this document, and are not a constraint on it.)*
>
> **Prefer citing IDs over section numbers** — see §16 (T-3).

## How to Read This Document

This is the **highest-level specification of the hierarchy it heads** — L0 wins over L1, L2 and L4
within `sdd/design/rel6_design/` until formally amended.

> **It is not the highest authority in this repository.** `sdd/specs/vision.md` and
> `sdd/specs/constitution.md` are, and the F-specs govern the code that actually runs today.
> **Read §17 before treating anything here as binding** — this whole tier governs no code until
> it is promoted, and promotion has preconditions (G-5).

**Audience:** All stakeholders, all AI coding agents, all future contributors.
Read this document first before reading anything else in this design tier.

---

# 1. PURPOSE & VISION

## 1.1 Mission Statement

Build an AI-powered investment pipeline that functions as a **virtual
investment team** for a US equity fund. The pipeline performs the analytical,
research, quantitative, and risk management functions traditionally carried
out by a team of human professionals, delivering structured recommendations
and continuous portfolio oversight to a single human fund manager who retains
all decision-making authority.

## 1.2 Vision Statement

A fund manager opens their terminal each morning to find:

- A prioritized brief of overnight events affecting their portfolio and
  watchlist, with impact assessments already completed
- Proactive risk alerts if portfolio exposure has drifted outside policy
- Fresh analysis on any stock, available on demand in under three minutes,
  backed by cited data, transparent methodology, and honest uncertainty
- A quantitative scoring framework running continuously across the investable
  universe, surfacing opportunities that match the fund's strategy
- Position-level sizing and exposure arithmetic, stress-tested against historical
  scenarios — presented for the PM seat to act on, **not** an optimizer pushing the
  book toward diversification (see §1.4 M-2)
- A complete audit trail of every recommendation, every data input, and
  every analytical step — fully reproducible
- ★ **A research lane where a quick experiment is cheap** — for the **Fundamental
  Analyst, the Quantitative Analyst and Risk Management alike**: a hypothesis can be
  tried, measured and discarded without a spec, a migration or a production change.
  This is **D-10 Experiments**, and constitution **P7** exempts it from spec rigor;
  promoting anything it produces into production requires a spec

The fund manager makes every investment decision. The pipeline's job is to
ensure those decisions are **faster, better-informed, more consistent, and
more rigorously documented** than any single human could achieve alone.

## 1.3 What This System Is NOT

| This System IS                              | This System IS NOT                    |
|---------------------------------------------|---------------------------------------|
| A decision-support tool                     | An autonomous trading bot             |
| An analytical assistant                     | A replacement for human judgment      |
| A research automation platform              | A guaranteed-returns system           |
| A risk monitoring system                    | A high-frequency trading platform     |
| A structured recommendation engine          | Financial advice for third parties    |
| A portfolio analytics dashboard *(intended; not yet built or specified — see Glossary)* | A brokerage or execution platform |

## 1.4 The Mandate

> **Source:** `sdd/specs/vision.md` §3. This is the fund's **stated investment posture**.
> It is here because it changes *what an agent should propose*, not merely how the proposal
> is built. **A proposal that contradicts the mandate is out of scope even if it is
> well-engineered.** Say so rather than building it.

| ID  | Mandate rule                                                                                                                                                                                                                                    |
|-----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **M-1** | **Deliberately takes extra risk for high return** — but **no penny stocks and no derivatives.**                                                                                                                                          |
| **M-2** | **Concentration is an intentional bet, not an accident.** Heavy AI/semiconductor weighting is chosen. *"Diversify the theme" is not a goal.* Theme exposure is **tracked and reported, never auto-blocked.**                              |
| **M-3** | **Pyramiding-up is the behaviour to curb.** The intended fix is to **sell less and let winners run**, not to scale in at ever-higher average cost. Features must serve *holding winners*, not only exiting.                               |
| **M-4** | **Registered-account (TFSA) day-trading is being actively reduced.** CRA "carrying on a business" risk is a real-world constraint, not a hypothetical. Short-hold round-trips in registered accounts get **flagged**.                     |
| **M-5** | **Base currency is CAD.** The book mixes USD and CAD; **currency is always explicit** and no arithmetic mixes currencies without an explicit FX step.                                                                                     |

### ⚠ PROPOSED additions — for review, NOT adopted

> Cross-checked 2026-08-21 against the **CFA Institute Investment Policy Statement** framework
> (return objective · risk objective · the five constraints — **time horizon, taxes, liquidity,
> legal/regulatory, unique circumstances** — plus permitted investments, benchmark, rebalancing
> policy and review schedule). M-1…M-5 map onto **risk posture, concentration, behaviour, tax and
> currency**. ★ **The rows below are the IPS elements with no rule here**, ordered by how much each
> would change what an agent proposes — which is §1.4's own test for whether something is a mandate.
> **None is adopted. Each needs Victor's decision.**

| ID | Proposed mandate | Why it changes what gets proposed |
|---|---|---|
| **M-6?** | ★★ **Benchmark and return objective.** Name the benchmark the book is measured against, and the excess return sought over what period | ⚠ **The largest gap.** *"Deliberately takes extra risk for high return"* (M-1) has **no measurable target and no reference**, so **"is this system working?" is currently unanswerable** — F8 attribution, RM-14 and every calibration curve have nothing to compare against. A concentrated AI/semi book measured against the S&P 500 and against SOXX are two different verdicts |
| **M-7?** | ★★ **Drawdown tolerance.** The peak-to-trough decline at which the process changes behaviour — a number, even if the response is *"review"* rather than *"de-risk"* | M-1 licenses extra risk with **no bound**, which makes every threshold in §7.3 arbitrary. ⚠ **A risk limit never derived from a stated tolerance cannot be defended at the moment it fires** |
| **M-8?** | ★ **Intended holding period.** A minimum intended hold, and what justifies breaking it | M-3 says *"let winners run"* with **no unit**. It also interacts with **M-4** — the CRA "carrying on a business" test is partly about holding period — so this has a real-world consequence, not only a stylistic one |
| **M-9?** | ★ **Liquidity floor.** A cash reserve, and a position-size ceiling relative to average daily volume | ⚠ **A position that cannot be exited at its stop has no stop.** The legacy prompt already warned that cyclicals gap through stops; nothing in the mandate constrains size against tradability |
| **M-10?** | **Permitted-instrument allowlist.** Convert M-1's exclusions into a closed *positive* list | M-1 says what is forbidden, not whether an **ADR, an IPO, a dual-listed name, an OTC-traded foreign issuer or a plain sector ETF** is in scope. §12.1 answers some of that and the mandate does not, so the two can drift apart |
| **M-11?** | ★ **Superficial-loss discipline.** Canada's 30-day superficial-loss rule, and the account-level rules for realising a loss | ⚠ **Mechanical, dated and jurisdiction-specific — exactly the shape of M-4.** Any tax-loss proposal is wrong without it, and the system has no way to know that |
| **M-12?** | **Mandate review cadence.** When the mandate itself is re-examined, and on what trigger | The mandate binds every proposal. ★ **An unreviewed mandate silently becomes a description of the past** — a pattern this document has already found three times in its own sections |

> ★ **Two IPS elements are deliberately NOT proposed.** A **rebalancing policy** would fight M-2 —
> mechanical rebalancing *is* the "diversify the theme" instinct M-2 rejects. And **unique
> circumstances** are already covered: single decision-maker, no external capital, no fiduciary
> duty to a third party (§1.3).

### Consequences that bind design work

- **M-2 forbids a hard concentration block.** Any position-size or sector-exposure limit in this
  document is a **reporting threshold**, not a veto. See §7.3 and §8.
- **M-3 reframes the risk features.** A feature that only makes it easier to exit is half a
  feature; the same surface must make it easier to *hold*.
- **M-1 removes whole capability classes from scope.** Options strategy analysis, leveraged/inverse
  instruments and penny-stock coverage are out — permanently, not "phase 6".
- **M-5 makes currency a first-class field**, not a display concern. A monetary value without a
  currency tag is a defect.
- When the fund manager **overrides** a mandate-derived flag, the system's job is to make that
  override **visible and logged** — never to block it.

## 1.5 The Fund Model — Five Seats, and Who Holds Them

> **Source: `sdd/specs/vision.md` §2, which now carries the five-seat model directly.** ✅ **This
> section is no longer an adaptation of it** — as of 2026-08-21 the authoritative file states the
> five numbered seats itself, and the three corrections that used to live here as local adaptations
> were promoted upstream where they belong:
> **(a)** Portfolio Manager and Execution Trader **merged into one human seat** (both are Victor;
> neither needs code, so splitting them created a seat with no software surface);
> **(b)** the analyst function **split into two seats**, Fundamental and Quantitative, because they
> are separate disciplines on separate machinery and are required to be independent;
> **(c)** Risk Management is **its own seat**, not an appendix to the back office.
> ★ **Renumbered and renamed 2026-08-21:** the human seat is **SEAT-1**, because it is the seat that
> decides and every other seat exists to serve it; *"Research Analyst" → "Fundamental Analyst"*
> (symmetry with "Quantitative Analyst"; the code path already said `src/fundamental/`); *"Risk" →
> "Risk Management"* (symmetry with the domain, which already carried the longer name).

A professional fund separates seats so the *decider* is not the *idea-generator* or the
*book-keeper*. That separation is what removes bias, and it is reproduced here deliberately.

| # | Seat | Held by | Responsibility | Code? |
|---|---|---|---|---|
| **1** | **Portfolio Manager & Trader** | **Fund manager (human)** | The *decision*: what, how much, when to add/trim/exit — and placing the order well. **Owns the P&L.** | **No** |
| 2 | **Fundamental Analyst** | **AI pipeline** | The *fundamental / qualitative* view of **one company**: filings, the **judgement** over valuation, moat and quality, thesis authoring, monitoring for invalidation (§4.2 D-01) | Yes |
| 3 | **Quantitative Analyst** | **AI pipeline** | The *systematic, cross-sectional* view of **the whole universe**: price/volume features, ML ranking, signals, backtests | Yes |
| 4 | **Risk Management** | **AI pipeline** | Risk metrics, exposure, unsuppressable flags | Yes |
| 5 | **Back / Middle office** | **AI pipeline** | Reconciliation, P&L, records, reporting | Yes |

> ★ **Seat 1 is first because it decides.** The renumbering is not cosmetic: the old order placed
> the human **third**, between the two AI analyst seats, which reads as a processing stage in a
> pipeline. **It is not a stage — it is the seat every other seat reports to** (§3.2).

> **Seat 1 is a human activity, not a component.** Nothing is built *for* it and nothing is built
> *as* it. Agents may hand it inputs — sizing arithmetic, exposure, scenario math — but the seat
> itself has no module, no domain in §4, and no agent. There is no execution/order-routing
> surface anywhere in this system.

## 1.6 The Three Analyst Seats — What Each One Actually Is

> ⚠ **Retitled 2026-08-21, from "The Two Analyst Seats".** Risk Management is an analyst seat and was
> being described everywhere as an afterthought to the other two. It analyses — it just analyses
> **the book** rather than a company or the cross-section, and **its independence rules are the
> opposite of theirs** (below).

The three analyst seats are distinguished by **unit of analysis** and **method**, not by seniority.
Seat 2 asks *"is this a good business at this price?"* about one name. Seat 3 asks *"which names
rank highest right now?"* across the universe. ★ Seat 4 asks *"what does this do to the book we
already hold?"* They run on different machinery and fail in different ways.

| | **Seat 2 — Fundamental Analyst** | **Seat 3 — Quantitative Analyst** | ★ **Seat 4 — Risk Management** |
|---|---|---|---|
| Unit of analysis | One company | The whole universe, cross-sectionally | ★ **The book** — the positions actually held |
| Method | Filings, statements, narrative judgement — ★ **and the deterministic arithmetic its own judgements parameterise** (§4.2 D-01) | Feature engineering + supervised ML | ★ **Deterministic exposure, limit and scenario arithmetic. No LLM, no model** |
| Core output | Thesis + verdict + falsification condition, **and the fair-value opinion it forms over D-02's method outputs** | `rank_score` per ticker | ★ **Alerts and flags — never a verdict, never a ranking** (INV-026) |
| Primary inputs | Statements, filings, news, profile — **and D-02's deterministic valuation, ratio and peer output** | Price/volume history, **D-02's engineered features**, D-02's `fv_model` | D-11's book · D-02's numbers · ★ **and, unlike the other two, BOTH analyst seats' outputs** |
| Independent of the others? | ✅ **Yes — required** (INV-014) | ✅ **Yes — required** (INV-014) | ⚠ **No — and deliberately not.** See below |
| Fails by | Hallucinating a fact, anchoring on a narrative | Look-ahead leakage, overfitting, regime shift | ★ A flag that is suppressed, or a limit that silently never fires |
| Guarded by | Citation requirements, bear-case requirement | No-look-ahead, determinism, train/inference parity | ★ **Zero authority (INV-026) + unsuppressable alerts** — it may never block, so it may never be argued with |

> ★ **Why Risk Management must NOT be independent.** INV-014 keeps seats 2 and 3 apart so neither
> inherits the other's conclusion. **Seat 4 measures the consequence of what is proposed, so it has
> to see what is proposed** — a risk desk blinded to the recommendation is measuring a book nobody
> is considering. ⚠ **The safety property that makes this harmless is INV-026: seat 4 has zero
> authority.** It cannot act on what it sees; it can only make it visible. **Independence and
> authority are the two dials, and seat 4 is set to `sees everything / decides nothing`.**

**Today's equivalent in the existing codebase** *(provenance, not a structural commitment —
these paths describe where the capability lives now, not where it must live after any rewrite)*:

| Seat | Existing code |
|---|---|
| **1 PM & Trader** | *(none — human)* |
| 2 Fundamental Analyst | `pipeline/buffett/synthesis/**`, `pipeline/buffett/analysis/news_analyst.py`, `llm_filing_parser.py` — the LLM-bearing half |
| 3 Quantitative Analyst | `pipeline/ohlcv/**` — the three-model bundle (**ranker + regressor + classifier**, `SeparateModelsBundle`) combined by `SignalEngine.combined_score` into `rank_score` |
| 4 Risk Management | `pipeline/discipline/**` (risk, flags, gate) |
| 5 Back / Middle office | **D-02:** `pipeline/buffett/analysis/**` (DCF, moat, quality), `pipeline/fundamental_analysis/features/**`, `pipeline/ohlcv/dataset/**` · **D-07:** `pipeline/fundamental_analysis/etl/**`, `pipeline/data_providers/**` · **D-09:** `pipeline/report/**`, `pipeline/delivery/**`, `pipeline/api/**` · **D-11:** `pipeline/portfolio/**`, `pipeline/discipline/journal.py` |

> ⚠ **The seat-2 row shrank in v0.9.0 and PARTLY GREW BACK in v0.22.0.** v0.9.0 moved DCF, moat
> scoring, quality gates and fundamental ratios wholesale to D-02. That was **half right**: the
> *arithmetic* is D-02's, but **fair value, moat and quality are not fully deterministic** — a P/E
> requires a judgement about which earnings to capitalise, and a moat score is a judgement by
> construction. **§4.2 D-01/D-02 now splits them by determinism rather than by topic.** The mapping
> in `L4-coding-standards.md` §1.5 is the file-by-file authority; this table is orientation.

### Decided vs deferred — read this carefully

Three questions are easily confused. **All three are now settled** — the third was deferred here
until v0.17.0 and this table had not been updated.

| Question | Status |
|---|---|
| **Are the FUNDAMENTAL and QUANT analyses produced independently?** | ✅ **DECIDED: yes.** Seat 2 authors its thesis without seeing `rank_score`; seat 3 computes `rank_score` without seeing the thesis. Neither conditions its work on the other's *output*. Enforced by **INV-014** and §4.3. |
| ★ **Is RISK MANAGEMENT independent of them?** | ⚠ **DECIDED: NO — deliberately.** Seat 4 measures the consequence of what the other two propose, so it **must** see both. **INV-014 binds seats 2 and 3 only.** What makes this safe is not independence but **INV-026 — seat 4 has zero authority**: it sees everything and decides nothing. |
| **How are the three outputs combined afterward?** | ✅ **DECIDED (v0.17.0) — by D-12.** ⚠ *This row read "DEFERRED" until 2026-08-21, three versions after the domain that closed it was added.* **D-12 Decision** composes **D-03's nomination, D-01's gate and D-05's alerts** into exactly one `Recommendation`. It **originates nothing** and may only make a verdict *more* conservative (P3, `L1-decision.md` DN-1). It sits in **seat 5** for the same reason D-02 does — a neutral layer, so neither analyst seat's conclusion is privileged. |

> ★ **The three-way composition is the reason D-12 had to exist.** Two outputs can be gated one by
> the other with no new domain. **Three cannot** — and every existing domain was the wrong home for
> a stated reason (`L1-decision.md` §1.2). *That is what a missing domain looks like.*

> **What "independent" does and does not forbid.** Seat 3 **may** consume fundamental *data*
> (statements, ratios, filing-derived features) from D-07, **and any computed number from D-02 —
> including the fair value** — because D-02 is seat 5's, not seat 2's. This is how the existing
> feature pipeline works and it is legitimate. Seat 3 **may not** consume seat 2's *analytical
> output*: the thesis, the verdict, the conviction, the reading seat 2 places on that fair value.
> Data is shared; judgement is not. The same rule applies in reverse. Independence is about not
> inheriting the other seat's conclusion, not about starving either seat of inputs.
>
> Nothing in this document may assume a particular combination mechanism. Where a downstream
> artifact needs a verdict (§5.1a), it takes whatever the analysis layer produced and does not
> presume how that verdict was formed.

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   THE AI IS DELIBERATELY NOT THE PORTFOLIO MANAGER.              ║
║                                                                  ║
║   The line between the fund manager and the AI is AUTHORITY      ║
║   AND ACCOUNTABILITY, NOT CAPABILITY. The AI may *support* PM    ║
║   work — sizing math, exposure, scenario arithmetic — but never  ║
║   holds PM *authority*. Accountability cannot be outsourced to   ║
║   a stochastic model.                                            ║
║                                                                  ║
║   "The fund manager" is not a separate component to be built.    ║
║   It is a hat the human wears consciously.                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Seat → agent mapping.** Four agents for five seats. **Seat 1 has no agent at all** — not an
advisory one, not a bounded one. Nothing in this system is built to occupy or to stand in for the
human decision seat.

| Seat | Agent that serves it (§5.1)  | Domains owned (§4.1) | Max authority (§3.1) |
|---|---|---|---|
| **1 Portfolio Manager & Trader** | **none**          | **none**             | —          |
| 2 Fundamental Analyst        | Fundamental Analyst Agent | Fundamental Analysis (D-01) | RECOMMEND  |
| 3 Quantitative Analyst       | Quantitative Analyst Agent | Quantitative Analysis (D-03), Model Training & Inference (D-04) | RECOMMEND  |
| 4 Risk Management            | Risk Manager Agent     | Risk Management (D-05), Portfolio Strategy (D-06) | ALERT      |
| 5 Back / Middle office       | Report Writer Agent    | Data Engine (D-07), Feature Engineering (D-02), Orchestration (D-08), Reporting (D-09), Recording (D-11), Decision (D-12), * **Experiments (D-10, P7-exempt — §4.2)** | RECOMMEND *(the agent serves **D-09 only**. The seat's other four domains — ingest, compute, schedule, record — are deterministic work with no agent in the loop and stay AUTONOMOUS)* |

> **Why deterministic computation sits under seat 5** *(v0.9.0)*. Every number an analyst reasons
> over — a DCF fair value, a margin, an indicator, an ML feature, a label — is computed in **D-02
> Feature Engineering**, owned by seat 5 alongside the Data Engine. It is derived-data custody: it
> consumes D-07, computes deterministically, and serves whoever asks. Putting it under either
> analyst seat would make one seat's arithmetic the *other* seat's inherited output, which INV-014
> forbids. Under seat 5 both analyst seats consume a neutral third party. See §4.2 D-02.

> **Where sizing and exposure arithmetic lives.** Seat 1 decides position size; it does not compute
> it. The arithmetic that informs that decision — exposure, scenario math, sizing given a stop — is
> the **Portfolio Strategy** domain, owned by **seat 4 (Risk)** and served by the Risk Manager
> Agent. It sits under Risk because it is the same machinery: both answer "what is the effect of
> this position on this book?"
>
> There is **no Portfolio Strategist agent**. The capability is a domain, not an actor. Nothing
> proposes an allocation, and no agent stands between the arithmetic and the human.

---

# 2. SYSTEM CONTEXT

## 2.1 System Context Diagram

```text
                        ┌──────────────────┐
                        │   FUND MANAGER   │
                        │   (Human User)   │
                        └────────┬─────────┘
                  Commands /     │     \ Reports / Briefs /
                  Queries /      │      \ Alerts / Recommendations
                  Overrides      │
                                 ▼
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                 AI INVESTMENT PIPELINE                        │
│                    [THIS SYSTEM]                              │
│                                                               │
│  ┌───────────┐ ┌───────────┐ ┌────────────┐ ┌────────────┐    │
│  │Fundamental│ │Quantitativ│ │ Risk       │ │ Report     │    │
│  │ Analyst   │ │ e Analyst │ │ Management │ │ Writer     │    │
│  │ Agent     │ │ Agent     │ │ Agent      │ │ Agent      │    │
│  │  seat 2   │ │  seat 3   │ │  seat 4    │ │  seat 5    │    │
│  └─────┬─────┘ └─────┬─────┘ └─────┬──────┘ └─────▲──────┘    │
│        │ gate        │ nomination  │ alerts       │ renders   │
│        └─────────────┴──────┬──────┘              │           │
│                             ▼                     │           │
│  ┌──────────────────────────────────────────────┐ │           │
│  │ ★ D-12 DECISION      seat 5 · no LLM         │─┘           │
│  │   composes the three · originates nothing ·  │             │
│  │   exactly ONE Recommendation (INV-6)         │             │
│  └──────────────────────────────────────────────┘             │
│         (no agent serves seat 1 — the human decision seat)    │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐    │
│  │              Orchestration Layer                      │    │
│  └───────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────┐    │
│  │              Data Engine & Infrastructure             │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                               │
└────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│Market  │ │SEC     │ │News    │ │LLM     │ │Brokerage   │
│Data    │ │EDGAR   │ │APIs    │ │Provider│ │(Future/    │
│APIs    │ │        │ │        │ │(s)     │ │Manual)     │
└────────┘ └────────┘ └────────┘ └────────┘ └────────────┘
```

## 2.2 External Systems & Integrations

**There are exactly two market-data sources: SEC EDGAR and FMP.** Adding a third is a decision,
not an implementation detail.

| External System | Direction | Purpose | Notes |
|---|---|---|---|
| **SEC EDGAR** | Inbound | Filings (10-K, 10-Q, 8-K) and XBRL company facts | **Primary source for TTM line items.** EDGAR facts carry an explicit period *start and end*, so a discrete quarter is distinguishable from a cumulative YTD one by arithmetic. Foundational, not a later phase. |
| **FMP** (Financial Modeling Prep) | Inbound | OHLCV, quotes, company profiles, fundamentals, news | Primary for prices and profiles; **fallback** for fundamentals where EDGAR coverage is absent. Exposes only a period *end*, so it must guess at cumulative-vs-discrete — hence the precedence rule above. Also the news source. |
| **Anthropic API** | Both | LLM reasoning, synthesis, extraction, classification | Tiered by cost-and-value: high-frequency shallow calls on the cheap tier, low-frequency quality-critical work on the deep tier. |
| **SMTP (email)** | Outbound | Delivery of reports, briefs and alerts | Delivered artifacts must be readable later without a live server. |
| **Broker statement export** | Inbound, **manual** | Transaction history (CSV/XLSX). ⚠ **BMO InvestorLine**, not CIBC — F4 and `ingest.py` both misname it; "CIBC" in the data is the **CDR issuer** appearing in instrument descriptions (`L1-recording.md` §5.3 H-2) | **File export only. There is no brokerage API, no portfolio sync, and no execution path — now or planned** (§1.5, §3.1 LEVEL 3). |

> **Deliberately absent:** any vector database, any separate news/sentiment vendor, any market-data
> aggregator beyond FMP, and any brokerage integration. Each was in the original draft; none exists
> or is planned. Their absence is a design position, not an oversight.
>
> **The EDGAR-over-FMP precedence rule for TTM is load-bearing**, not a preference — guessing wrong
> on cumulative-vs-discrete quarters has moved a single name's intrinsic value by more than 70%.

## 2.3 User Roles

| Role          | Count | Seats held (§1.5)                  | Description                                      |
|---------------|-------|------------------------------------|--------------------------------------------------|
| Fund Manager  | 1     | 3 Portfolio Manager & Trader       | Sole human user. Owns the P&L and every decision that commits capital. Requires no software surface. |
| AI Agents     | 4     | 1 Fundamental Analyst, 2 Quantitative Analyst, 4 Risk, 5 Back/Middle office | System-internal actors. Advisory only. **No agent serves seat 1.** |
| System Admin  | 1     | —                                  | Same person as fund manager for now.             |

> **Note:** This is a single-user system by design. There is no multi-tenancy,
> no role-based access control for multiple humans, and no public-facing
> interface. Security model is simplified accordingly but must still protect
> sensitive financial data and API credentials.

---

# 3. DECISION AUTHORITY FRAMEWORK

This is the most important governance structure in the entire system.

## 3.1 Authority Levels

```text
┌────────────────────────────────────────────────────────┐
│              DECISION AUTHORITY MATRIX                 │
├──────────────────────┬─────────────────────────────────┤
│ LEVEL 0: AUTONOMOUS  │ System acts without approval    │
│                      │                                 │
│ • Fetch market data  │ • Run scheduled pipelines       │
│ • Calculate metrics  │ • Reconcile & record            │
│ • Store/cache data   │ • Send informational alerts     │
│ • Detect anomalies   │ • Update watchlist scores       │
├──────────────────────┼─────────────────────────────────┤
│ LEVEL 1: RECOMMEND   │ System suggests, human decides  │
│                      │                                 │
│ • Buy/Sell/Hold rec  │ • Position sizing suggestions   │
│ • GENERATE REPORTS   │ • Risk mitigation actions       │
│ • Watchlist adds     │ • Thesis upgrades/downgrades    │
├──────────────────────┼─────────────────────────────────┤
│ LEVEL 2: ALERT       │ System warns, human must act    │
│                      │                                 │
│ • Risk limit breach  │ • Data quality failure          │
│ • Concentration warn │ • Stale data beyond threshold   │
│ • Drawdown threshold │ • Contradictory signals         │
├──────────────────────┼─────────────────────────────────┤
│ LEVEL 3: BLOCKED     │ System CANNOT do, ever          │
│                      │                                 │
│ • Execute trades     │ • Move money                    │
│ • Commit capital     │ • Alter risk limits silently    │
│ • Override fund mgr  │ • Suppress alerts/warnings      │
│ • Delete audit trail │ • Change its own guardrails     │
└──────────────────────┴─────────────────────────────────┘
```

> **Report generation is LEVEL 1, not LEVEL 0** *(moved 2026-08-13)*. A report is not a neutral
> rendering — it carries a verdict, a stop and a target, and it is read as advice. Producing it is
> therefore a recommendation and never an autonomous act, regardless of how mechanical the
> rendering feels from inside the system.
>
> The autonomous half of the same seat remains at LEVEL 0: **recording and reconciling** are custody
> of fact, not judgement. Writing a trade to the log is autonomous; writing a brief about it is not.
> **The dividing line is whether a human could act on the output.**
>
> *(v0.10.0: that line is now a domain boundary, not a convention inside one domain — **D-11
> Recording** is LEVEL 0, **D-09 Reporting** is LEVEL 1. See §4.1.)*

## 3.2 Core Governance Principle

```text
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   THE AI PIPELINE NEVER ACTS ON CAPITAL.                      ║
║   THE AI PIPELINE NEVER SUPPRESSES RISK WARNINGS.             ║
║   THE AI PIPELINE NEVER HIDES UNCERTAINTY.                    ║
║                                                               ║
║   The Fund Manager is the sole decision authority for any     ║
║   action that affects real capital, portfolio composition,    ║
║   or risk exposure.                                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

# 4. DOMAIN ARCHITECTURE

## 4.1 Bounded Contexts — Owned by Seat

The system is decomposed into **eleven domains plus shared infrastructure**. Every domain is owned by
exactly one seat (§1.5). Every AI-held seat has **one agent and one or more domains** — seats own
work, agents perform it.

| Seat | Domains owned | Why grouped this way |
|---|---|---|
| **1 PM & Trader** | *(none — human)* | Decides; does not compute |
| **2 Fundamental Analyst** | Fundamental Analysis (D-01) | Narrative judgement, LLM-bearing, guarded by citation (AP-2) and the mandatory bear case (AP-3). ★ **The only domain that *reasons*** — it also computes, but only arithmetic its own judgements parameterise (§4.2 D-01) |
| **3 Quantitative Analyst** | Quantitative Analysis (D-03) · **Model Training & Inference (D-04)** | Stateless calculation (deterministic, guarded by ranges + golden tests) vs. the ML lifecycle (guarded by no-look-ahead, train/inference parity, drift) |
| **4 Risk Management** | Risk Management (D-05) · **Portfolio Strategy (D-06)** | Both answer "what does this position do to this book?" — measuring current exposure and computing the effect of a hypothetical are the same machinery |
| **5 Back / Middle office** | Data Engine (D-07) · **Feature Engineering (D-02)** · Orchestration (D-08) · **Reporting (D-09)** · **Recording (D-11)** · **Decision (D-12)** · ★ *Experiments (D-10, P7-exempt)* | Custody of data, of *derived* data, of the schedule, of the **record**, of the **artifact**, and of the **composition**. ★ **D-02 and D-12 are the same structural device at the two ends of the pipeline** — a neutral layer upstream of both analyst seats and a neutral layer downstream of them, so that neither seat's conclusion is privileged (`L1-decision.md` §1.4). Six back-office duties at **three different authority levels** |
| *(none)* | Shared Infrastructure (D-00) | Cross-cutting; owned by no seat |

Where a seat owns several domains, the split is a **guard-rail boundary** — drawn so each half can
carry its own invariants and its own tests rather than one blurred set. Two kinds of boundary are
in use: **deterministic computation vs. LLM-generated judgement** (seats 3 and 3), and
**authority level** (seat 5, where D-11 is LEVEL 0 and D-09 is LEVEL 1).

> **Ownership is not exclusivity.** Seat 5 owning the Data Engine means seat 5 is *accountable*
> for it — its correctness, its contracts, its failures. Every other seat freely **consumes** it.
> The same holds for Orchestration: seat 5 owns the scheduler; the pipelines it triggers belong to
> whichever seat owns the work.

> **Recording and Reporting are two domains, not one** *(split in v0.10.0)*. They were bundled
> because both are "the human-facing end of the pipeline". They are separated because they are not
> the same *kind* of work, and the difference is one §3.1 already draws:
>
> | | **D-11 Recording** | **D-09 Reporting** |
> |---|---|---|
> | What it keeps custody of | **the fact** — what happened to the book | **the artifact** — what the human reads |
> | Authority (§3.1) | **LEVEL 0 AUTONOMOUS** | **LEVEL 1 RECOMMEND** |
> | Agent | **none** — deterministic throughout | **Report Writer Agent** |
> | Fails by | a break going unnoticed, a P&L that does not reconcile | rendering a verdict the analysis layer did not produce (DC-3, DC-5) |
> | Written by | reconciliation, arithmetic | layout, templates, an LLM narrative it did not author |
>
> §3.1 states the test directly: *"Writing a trade to the log is autonomous; writing a brief about
> it is not. The dividing line is whether a human could act on the output."* Holding both sides of
> that line inside one domain meant one directory carried two authority levels, and a file's
> location no longer determined its authority (ST-4). **The split makes the authority boundary a
> directory boundary.**
>
> Recording is also **upstream** of Reporting and of D-05 Risk: both read the book D-11 keeps.
> Nothing flows the other way — a report never writes to the record.

> **Name history.** "Execution & Reporting" → "Recording & Reporting" (v0.5.0) → **"Recording"
> and "Reporting"** (v0.10.0). The first rename was because there is no execution in this system
> (§1.5, §3.1 LEVEL 3), so the original name described a capability that does not and will not
> exist. The second is the split above. **No domain is named "Recording & Reporting" any more** —
> a citation using that name predates v0.10.0 and means one of the two.

```text
┌───────────────────────────────────────────────────────────────────────┐
│  SEAT 1 — PORTFOLIO MANAGER & TRADER    (human · no domain · no agent)│
│        consumes everything below · decides · owns the P&L             │
└───────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ ONE Recommendation, via D-09
        ┌──────────────────────────┴──────────────────────────┐
        │  ★ D-12 DECISION       (seat 5 · neutral · no LLM)  │
        │  composes the three below · originates nothing ·    │
        │  P3-monotone · exactly one Recommendation (INV-6)   │
        └───┬──────────────────────┬──────────────────────┬───┘
            │ gate                 │ nomination           │ alerts
┌───────────┴────┐        ┌────────┴────────┐        ┌────┴────────────┐
│ SEAT 2         │        │ SEAT 3          │        │ SEAT 4          │
│ FUNDAMENTAL    │        │ QUANTITATIVE    │        │ RISK            │
│ ANALYST        │        │ ANALYST         │        │ MANAGEMENT      │
│ ┌────────────┐ │        │ ┌─────────────┐ │        │ ┌─────────────┐ │
│ │ D-01       │ │        │ │ D-03 Quant  │ │        │ │ D-05 Risk   │ │
│ │ Fundamental│ │        │ │ Analysis    │ │        │ │ Management  │ │
│ │ Analysis   │ │        │ └─────────────┘ │        │ └─────────────┘ │
│ └────────────┘ │        │ ┌─────────────┐ │        │ ┌─────────────┐ │
│                │        │ │ D-04 Model  │ │        │ │ D-06        │ │
│ thesis,        │        │ │ Training &  │ │        │ │ Portfolio   │ │
│ verdict,       │        │ │ Inference   │ │        │ │ Strategy    │ │
│ invalidation,  │        │ └─────────────┘ │        │ └─────────────┘ │
│ ★ fair-value   │        │                 │        │                 │
│   OPINION      │        │                 │        │ exposure, VaR,  │
│ ★ the only     │        │                 │        │ stress, flags,  │
│   LLM-bearing  │        │                 │        │ sizing math     │
│   domain       │        │                 │        │                 │
└───────┬────────┘        └────────┬────────┘        └────────┬────────┘
        │                          │                          │
        └──── independent ─────────┘   ⚠ SEAT 4 is NOT        │
             (INV-014 · §4.3)             independent — it    │
                                          sees both, and      │
                                          INV-026 (zero       │
                                          authority) is what  │
                                          makes that safe     │
        │                          │                          │
        └──────────────────────────┴──────────────────────────┘
                                   ▲
┌──────────────────────────────────┴────────────────────────────────────┐
│  SEAT 5 — BACK / MIDDLE OFFICE                                        │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ D-02 FEATURE ENGINEERING          ← neutral ground (INV-014)    │  │
│  │ every number an analyst reasons over, computed once:            │  │
│  │ DCF & fair value · moat & quality · ratios · indicators ·       │  │
│  │ ML features · labels · the feature contract (INV-4)             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                   ▲                                   │
│  ┌──────────────┐   ┌────────────────┐                                │
│  │ D-07 Data    │   │ D-08 Orchestr- │                                │
│  │ Engine       │   │ ation          │                                │
│  │ ingest,      │   │ scheduling,    │                                │
│  │ validate,    │   │ pipeline state,│                                │
│  │ store, serve │   │ retries        │                                │
│  └──────────────┘   └────────────────┘                                │
│                                                                       │
│  ┌─────────────────────────┐      ┌─────────────────────────┐         │
│  │ D-11 RECORDING          │─────►│ D-09 REPORTING          │         │
│  │ custody of the FACT     │      │ custody of the ARTIFACT │         │
│  │                         │      │                         │         │
│  │ book state, P&L,        │      │ brief, slate,           │         │
│  │ reconciliation,         │      │ Discipline Card (§5.1a),│         │
│  │ trade log, journal,     │      │ delivery, read surface  │         │
│  │ attribution             │      │                         │         │
│  │                         │      │ ★ Report Writer Agent   │         │
│  │ no agent · LEVEL 0      │      │   LEVEL 1 RECOMMEND     │         │
│  └─────────────────────────┘      └─────────────────────────┘         │
│         one-way: a report never writes to the record                  │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│  SHARED INFRASTRUCTURE          (cross-cutting · owned by no seat)    │
│  LLM gateway · config · logging · secrets                             │
└───────────────────────────────────────────────────────────────────────┘

  ✅ ASSIGNED (v0.17.0): seats 2, 3 and 4's outputs are combined by
  D-12 Decision, seat 5. See §1.6 — no longer deferred.
  ★ D-10 Experiments moved to seat 5 (v0.22.0) — it serves all three
    analyst seats, so it cannot sit inside one of them.
```

## 4.2 Domain Summaries

### FUNDAMENTAL ANALYSIS — *seat 2* · D-01
**The whole of seat 2**, and the only domain in the system that reasons rather than computes.
Understanding individual companies: what they do, how they make money, competitive position,
management quality, earnings trajectory, catalysts and risks. Authors the **investment thesis** and
its **falsification condition**, and monitors for invalidation as new filings and news arrive.
Consumes filings, news and profile data from **D-07**, and D-02's **deterministic method outputs**.
**LLM-bearing** — guarded by citation requirements (AP-2) and the mandatory bear case (AP-3).

#### ★ v0.22.0 — the valuation split, and why "interprets, never computes" was too clean

⚠ **The previous wording said D-01 *interprets* D-02's valuation and *never recomputes* it. That
was half right, and the half that was wrong had already produced a live contradiction**: L0 assigned
*"moat and quality scoring"* to D-02, while `L1-fundamental-analysis.md` §8.1 fixes **`moat_durability`
and `earnings_quality` as D-01 rubric dimensions**, selected by an LLM against written criteria.
Two documents, two owners, one capability.

**The resolution is to split by DETERMINISM, not by topic.**

| Deterministic — **D-02, seat 5, neutral ground** | Judgement — **D-01, seat 2** |
|---|---|
| DCF mechanics, discount rate, terminal value, the sensitivity band | ★ **Which earnings to capitalise** — normalising for the cycle, one-offs and non-GAAP adjustments |
| Every ratio and growth rate, with its arithmetic trail | ★ **Which multiple is appropriate**, and why this business earns it |
| Peer statistics at matching periods (`peer_context`) | ★ **Which peers are comparable at all** |
| Analyst-consensus retrieval | ★ **How much weight each method deserves for THIS name** |
| ★ **`fv_model`** — the method outputs and their band | ★ **`fv_analyst`** — the reconciled fair-value **opinion** |
| Moat and quality **inputs**: ROIC series, share stability, accrual ratio, coverage | ★ **`moat_durability` / `earnings_quality` rubric SELECTION** (D-01 §8.1) |

| ID | Rule |
|---|---|
| **VS-1** | ★★ **There are two fair values and they must never share a name.** `fv_model` is D-02's deterministic output; `fv_analyst` is D-01's opinion over it. ⚠ **Collapsing them is what makes INV-014 unenforceable**, because nothing downstream can tell whether it consumed arithmetic or a conclusion |
| **VS-2** | ★★ **`fv_model` and every D-02 fundamental feature stay consumable by BOTH analyst seats.** They are neutral ground and INV-014 is untouched — this is the whole point of the split |
| **VS-3** | ★★ **`fv_analyst`, the scorecard levels and the thesis are consumable by NO analyst seat.** Seat 3 may not read them (INV-014); D-12 and D-09 may. ⚠ **`F0` §16 already records a live breach of exactly this** — `MoatScorer` blends a score derived from D-01's LLM-authored profile into a quant feature. This split **names** that defect; it does not create it |
| **VS-4** | ★ **D-01 contains deterministic computation, and that does not weaken AP-5.** The rule is not *"D-01 may not compute"* — it is **(a)** no arithmetic *inside a prompt*, ever, and **(b)** no arithmetic that is **judgement-free**, because that is definitional, reusable and therefore D-02's. ★ **Arithmetic that a judgement parameterises — applying a multiple D-01 selected to earnings D-01 normalised — is plain code inside D-01.** The LLM chooses the inputs; it never does the multiplication |
| **VS-5** | ⚠ **Consequence for `L1-fundamental-analysis.md` RA-45**, which currently reads *"D-01 performs no arithmetic that D-02 could perform."* That still holds — **D-02 could not perform this arithmetic, because it does not hold the judgement it depends on** — but the rule's wording invites the wrong reading and should be restated in D-01's next revision |

### ~~VALUATION~~ — *retired in v0.9.0*
> **Tombstone (T-2).** Valuation was D-02 under seat 2. It is now a **sub-area of D-02 Feature
> Engineering under seat 5** — see the D-02 entry below. The capability did not change; its owner
> did, because a fair value computed by seat 2 and consumed by seat 3 would be seat 3 inheriting
> seat 2's output, which INV-014 forbids. Nothing new took the name "Valuation" as a domain.

### QUANTITATIVE ANALYSIS — *seat 3* · D-03
The **stateless calculation** half of seat 3. Cross-sectional screens (52-week position, gaps,
volume anomalies, momentum rank), signal construction and backtesting, computed **over features
D-02 supplies** rather than over raw data. Pure functions — no model state, no training. Guarded by
bounded-range checks, determinism and golden tests, and by the backtest bias disclosure.

### MODEL TRAINING & INFERENCE — *seat 3* · D-04
The **ML lifecycle** half of seat 3. Supervised training, model selection, inference, and the
production of **`rank_score`** across the universe. It **consumes** the feature contract; **D-02
owns it** (changed in v0.9.0). Guarded by the three invariants unique to this domain: **no
look-ahead**, **train/inference parity**, and **drift detection** — parity being an explicit gate
asserted *against D-02's published contract*, not an implicit convention. Retraining cadence,
promotion from research to production, and model governance live here.

### EXPERIMENTS — *seat 5* · D-10 · **P7-exempt** *(moved from seat 3 in v0.22.0)*
Exploratory work: hyperparameter sweeps, CPCV, feature discovery, blend attribution, leaderboards.

> ★ **Moved to seat 5 because §1.2 requires it to serve all three analyst seats.** A research lane
> owned by the Quantitative Analyst is a research lane the Fundamental Analyst and Risk Management
> cannot use without borrowing another seat's domain. **Seat 5 is neutral ground — the same argument
> that placed D-02 and D-12** — so a fundamental rubric variant, a quant feature sweep and a risk
> scenario study can all run in the same lane.
>
> ⚠ **P7 exempts D-10 from SPEC rigor. It does not exempt it from INV-014.** An experiment may
> freely read anything; **its output may not cross a seat boundary that a production path could not
> cross.** The one-way import rule below is what keeps that true by construction — nothing may
> import D-10, so nothing it discovers reaches production except by a deliberate, specified
> promotion.
**Exempt from spec rigor by constitution P7**, and the exemption is kept honest by a one-way import
rule — D-10 may import any domain; **no domain may import D-10** (`L4-coding-standards.md` ST-2).
Promoting an experiment's output into a governed domain requires a spec. Without the one-way rule,
"exempt from spec rigor" leaks into production by import rather than by decision.

> ★ **D-10 gets no L1 spec, and that is a decision — not a gap** *(Victor, 2026-08-18)*. **Every
> other domain is specified first and built second; D-10 is the one domain where that order is
> wrong.** What belongs in an experiment — which hyperparameters are worth sweeping, which
> comparisons are worth running, what a leaderboard should even measure — is **not knowable until
> the other ten domains exist and have been run end-to-end**. Writing it now would specify a
> research agenda from imagination rather than from a first E2E result.
>
> ★ **Intent is captured in the meantime.** [`L1-experiments-intent.md`](L1-experiments-intent.md)
> records what D-10 must eventually be able to do, and audits it against the **1,978 LOC of working
> experiment harness already in `pipeline/ohlcv/experiments/`** (P4). ⚠ **It is not the L1 spec, it
> declares no acceptance criteria, and it governs no path** — the trigger below still gates that.
>
> **The trigger for writing it:** the first full E2E run is complete and its results have been
> evaluated. Until then D-10 stays P7-exempt and unspecified, held only by the **one-way import
> rule** (`L4` ST-2) — which is what makes leaving it unspecified safe, because an unspecified
> domain nothing may import cannot leak into production by accident.

### RISK MANAGEMENT — *seat 4* · D-05
The risk oversight function. Measures current risk and surfaces it: exposure by name/sector/theme,
VaR/CVaR, correlation, stress testing, drawdown tracking, and the **behavioural flags M-3 and M-4
name** — pyramiding and short holds in registered accounts. Generates LEVEL 2 ALERT notifications
that no component may suppress (INV-021). Per **M-2 / INV-026**, everything here **reports**;
nothing here blocks — a combination `L1-risk-management.md` §1.4 calls *maximum voice, zero
authority*. **Sizing and what-if arithmetic belong to D-06**, not here.

> *(v0.11.0 removed a stale sentence claiming D-05 "also owns the sizing and scenario arithmetic".
> That text dates from **v0.5.0**, when Portfolio Strategy had been deleted and D-05 temporarily
> absorbed its work; **v0.6.0 restored D-06** and the sentence was never withdrawn. Closes
> `L1-risk-management.md` **QK-1**.)*

### PORTFOLIO STRATEGY — *seat 4* · D-06
The **forward-looking** half of seat 4, where Risk Management is the backward-looking half. Given a
candidate position it computes the arithmetic seat 1 needs to decide: **position size given a
stop**, the exposure the book would carry after the trade, correlation and theme impact, and
scenario/what-if math. Deterministic throughout.

```text
╔══════════════════════════════════════════════════════════════════╗
║  PORTFOLIO STRATEGY COMPUTES CONSEQUENCES. IT NEVER PROPOSES     ║
║  A BOOK.                                                         ║
║                                                                  ║
║  It answers "if I did X, what happens?" — a question the human   ║
║  asked. It never answers "what should I hold?", produces a       ║
║  target allocation, or detects drift from one. Optimizing        ║
║  toward a target is the diversification pressure M-2 rejects,    ║
║  and the allocation decision is seat 1's alone.                  ║
║                                                                  ║
║  The domain name is inherited. Read it as *portfolio             ║
║  arithmetic*, not portfolio construction.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

### DATA ENGINE — *seat 5* · D-07
The foundation layer. Acquires, normalizes, validates, stores and serves all data consumed by every
other domain, and guarantees that a query for date D returns what was **knowable** on D. No
analytical logic — ingestion, canonical transformation, point-in-time resolution, storage, caching,
retrieval, source routing, rate limiting, quality validation. Accountable to seat 5; consumed by
all seats. Specified in `L1-data-engine.md`.

### FEATURE ENGINEERING — *seat 5* · D-02 *(new in v0.9.0)*
**Every number an analyst reasons over, computed once, by nobody's analyst.** Discounted cash flow
and **`fv_model`**, the sensitivity band, fundamental ratios and growth, **peer context at matching
periods**, the **inputs** moat and quality judgements are made from, technical indicators and derived
series, ML features, labels, and the **feature contract** that INV-4 parity asserts against.
Deterministic throughout — **no LLM participates in any of this computation** (§5.3, AP-5).

> ⚠ **Narrowed in v0.22.0.** This entry used to claim *"moat and quality **scoring**"* and *"fair
> value"* outright. **It keeps the arithmetic and gives up the judgement** — see §4.2 D-01's
> valuation split and **VS-1…VS-5**. ★ **D-02 remains neutral ground and INV-014 is unaffected**,
> because everything D-02 still owns is judgement-free and therefore consumable by both analyst
> seats. What moved to D-01 is precisely the part that was never consumable by seat 3 anyway.

It is one step downstream of D-07 and the same duty: *custody of derived data*. It consumes the Data
Engine, computes, and serves whoever asks — D-01 and D-03/D-04 alike.

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-02 IS NEUTRAL GROUND, AND THAT IS WHAT KEEPS INV-014 INTACT.  ║
║                                                                  ║
║  INV-014 forbids each analyst seat from consuming the OTHER      ║
║  seat's analytical output. Had valuation stayed under seat 2, a  ║
║  fair value flowing into the ranking models would have been      ║
║  seat 3 inheriting seat 2's conclusion — a violation on the      ║
║  face of it. Under seat 5 it is neither seat's output.           ║
║                                                                  ║
║  Independence is preserved by OWNERSHIP, not by exception.       ║
║                                                                  ║
║  The risk this creates, stated rather than discovered: D-02 is   ║
║  now on the critical path of BOTH analyst seats, so a defect     ║
║  here degrades both views simultaneously — the two stop being    ║
║  independent evidence without INV-014 being broken on paper.     ║
║  Its test bar is the highest in the tree.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

Guarded by known-value formula tests, golden/characterization tests, and cross-checks
(balance-sheet identity, cash-flow reconciliation). **Inherits one known open defect** — the DCF
returns an enterprise value divided by share count with no net-debt subtraction (`F0` §12 **D-19**,
🔴 open). It must be carried into the D-02 spec as an open item, not silently absorbed as correct
code during the migration.

### ORCHESTRATION — *seat 5* · D-08
Custody of the schedule. Triggers pipelines, manages pipeline state, handles failure and retry,
enforces time budgets. **Orchestration invokes work; it never performs work.** It contains no
analysis, no computation and no judgement — if a scheduled job computes something, that computation
belongs to the domain that owns it.

### RECORDING — *seat 5* · D-11 *(split out of D-09 in v0.10.0)*
**Custody of the fact.** What the book actually holds and what actually happened to it: broker
statement ingestion and reconciliation, position and P&L state, the trade log and manual trade
entry, performance attribution, and the **decision journal**. Deterministic throughout — no LLM,
no agent, no judgement (AP-5).

**LEVEL 0 AUTONOMOUS** (§3.1). Writing a trade to the log commits nothing and recommends nothing;
it records something that already happened. This is the half of the old D-09 that was always
autonomous, and bundling it with a RECOMMEND-level renderer is what made the old domain's authority
ambiguous.

It is **upstream** of D-09 Reporting and of D-05 Risk — both read the book it keeps. **Nothing
writes back**: a report never mutates the record (§4.3).

> **The journal is Recording, not Reporting**, though it is read by a human. A journal entry is a
> record of a decision that was made, written at the time and never revised — the same custody duty
> as the trade log. Rendering it into a brief is D-09's job.

### REPORTING — *seat 5* · D-09 *(narrowed in v0.10.0)*
**Custody of the artifact.** The rendering and delivery of everything a human reads: briefs,
slates, the **Discipline Card** (§5.1a), email delivery, and the local/phone read surface. This is
the primary human interface layer, and the only domain in seat 5 with an agent — the **Report
Writer Agent** (§5.1).

**LEVEL 1 RECOMMEND** (§3.1). Everything it emits is read as advice, however mechanical the
rendering feels from inside the system. It **may render** LLM-authored text it did not write
(DC-1), and it **may never** originate a verdict, escalate one (DC-5), or emit a plausible-looking
default when its inputs failed (DC-3).

### DECISION — *seat 5* · D-12 *(added v0.17.0)*
**Custody of the composition.** Takes D-03's nomination, D-01's gate verdict and D-05's alerts and
produces the single `Recommendation` a human reads. **It originates nothing** — every verdict it
emits was emitted by someone else first, and its only freedom is to make one *more conservative*.

**LEVEL 1 RECOMMEND** (§3.1). Deterministic, **no agent, no LLM** (P2, AP-5): composition is
arithmetic on a three-element lattice, where **P3 is implied by the structure rather than enforced
by a check** (`L1-decision.md` §5).

It exists because §1.6's combine point had **no correct home** — every other domain is the wrong
owner for a stated reason, and D-09 owning it is how a renderer starts deciding (DC-5). See
[`L2-signal-combination.md`](L2-signal-combination.md) and [`L1-decision.md`](L1-decision.md).

> ⚠ **No feedback edge.** D-12's output must never reach D-01 or D-03, in this run or a later one.
> INV-014 keeps the two seats independent at production; a composed verdict fed back would launder
> exactly that dependency through a third party and a time lag (`L1-decision.md` **DN-3**).

### SHARED INFRASTRUCTURE — *no seat* · D-00
Cross-cutting technical services with no business ownership: the LLM gateway, configuration,
structured logging, secret handling. Contains no domain logic and makes no decisions.

## 4.3 Domain Dependency Rules

```text
ALLOWED DEPENDENCIES

  D-07 Data Engine ──► everything.  Every domain consumes canonical data.
  D-07 ──► D-02 Feature Engineering ──► every analytical domain
           (most consumption of D-07 is INDIRECT, through D-02)

  Seat 2:  D-07 + D-02 ──► D-01 Fundamental Analysis
                           (filings/news from D-07; fair value,
                            quality, moat from D-02 — interpreted,
                            never recomputed)

  Seat 3:  D-07 + D-02 ──► D-03 Quantitative Analysis
           D-07 + D-02 ──► D-04 Model Training & Inference
                           (D-02 owns the feature contract;
                            D-04 consumes and asserts parity against it)
           D-10 Experiments ──► may import ANY domain (one-way, ST-2)

  Seat 4:  D-07 + D-11 (book state) ──► D-05 Risk ──► D-06 Portfolio Strategy
                           (current exposure feeds what-if arithmetic)

  Seat 5:  D-03 + D-01 + D-05 ──► D-12 Decision ──► D-09, D-11
                           (composes; NEVER originates a verdict)
           D-11 Recording ◄── every domain feeds the record
           D-11 Recording ──► D-09 Reporting   (one-way)
           every domain    ──► D-09 Reporting   (it renders their output)
           D-08 Orchestration ──► may invoke any domain's pipeline
                             (invokes only — never computes)

FORBIDDEN DEPENDENCIES

  ✗ Seat 3 MUST NOT consume seat 2's ANALYTICAL OUTPUT
      — no thesis, no verdict, no conviction as model input, feature,
        or label.
  ✗ Seat 2 MUST NOT consume seat 3's ANALYTICAL OUTPUT
      — rank_score does not enter thesis authoring.
  ✗ D-02 MUST NOT consume any analytical domain (D-01, D-03…D-06).
      It is upstream of all of them. A D-02 input that came from an
      analyst is the INV-014 leak wearing a different hat.
  ✗ NO domain may import D-10 Experiments.  The reverse is allowed.
      (P7 exemption stays behind a one-way door — ST-2)
  ✗ D-12 Decision MUST NOT be consumed by D-01 or D-03.
      Composition flows one way. A composed verdict returning to
      either analyst seat is INV-014 laundered through a third
      party and a time lag.  (L1-decision.md DN-3)
  ✗ D-12 MUST NOT produce a ranking, a score, or a position size.
  ✗ Risk MUST NOT depend on Orchestration
  ✗ Orchestration MUST NOT contain analysis, computation or judgement
  ✗ Portfolio Strategy MUST NOT emit a target allocation, a recommended
      book, or drift-from-target — it computes consequences of a
      position the human is considering (M-2 / INV-026)
  ✗ D-09 Reporting MUST NOT write to the record.  It reads D-11 and
      renders it.  A renderer that can mutate the book can rewrite
      history to match what it printed.
  ✗ D-11 Recording MUST NOT render, format for display, or call the
      LLM gateway.  It keeps facts; presenting them is D-09.
  ✗ No domain may bypass Data Engine to reach an external API
  ✗ No domain may write to another domain's data store directly
  ✗ No domain except D-01 may import the LLM gateway (AP-5, ST-5).
      D-09 Reporting may RENDER LLM text it did not author (DC-1).

EXPLICITLY ALLOWED — do not mistake this for a violation

  ✓ Both analyst seats MAY consume the SAME D-02 output — the same
    fair value, the same feature set. D-02 belongs to seat 5, so
    neither seat is inheriting the other's conclusion.
  ✓ Seat 3 MAY consume fundamental features. Fundamental features in
    the model are legitimate and expected.
  ✓ Seat 2 MAY consume price data and computed indicators.
  ✓ D-09 Reporting MAY read anything it renders — the book from
    D-11, risk from D-05, the thesis from D-01. Reading is its job;
    writing back is what it may never do.

  The line is DATA vs JUDGEMENT. Shared inputs, however derived:
  fine. Inherited conclusions: forbidden.
```

> **Design rationale (INV-014).** The two analyst seats are kept independent so their views can be
> compared rather than confirming each other. If seat 3 could see the thesis, a bullish narrative
> would leak into the ranking; if seat 2 could see `rank_score`, the thesis would rationalise the
> model. Independence is what makes a disagreement between them *informative*.
>
> **What this rule does NOT decide.** It constrains how each analysis is **produced**. It says
> nothing about how the two outputs are **combined** afterward, or which domain does the combining
> — that is deferred (§1.6) and no domain above is assigned to it.

---

## 4.4 Clean Architecture — the requirement, and its honest scope

**Requirement (added v0.18.0).** This system adopts **Clean Architecture's Dependency Rule**
(Martin, *Clean Architecture*, 2017, ch. 22): **source-code dependencies point only inward**, from
mechanism toward policy. Concretely — business rules never import I/O, transport, vendor SDKs or
file formats; the arrow is inverted with a Protocol at the boundary.

### ★ There are now TWO dependency rules, on orthogonal axes

```text
     HORIZONTAL — the domain axis (§4.3)      "may D-03 import D-01?"
        who may import whom, by SEAT and by
        analytical independence (INV-014)

     VERTICAL — the layer axis (§4.4)          "may a rule import an HTTP client?"
        policy never imports mechanism, ever,
        in any domain

     ★ A FILE IS LEGAL ONLY IF IT SATISFIES BOTH.
       They constrain different things and neither implies the other:
       D-03 importing D-01 is a horizontal breach at any layer;
       a D-03 rule importing `requests` is a vertical breach even
       though D-03 imports no forbidden domain.
```

### ⚠ Where Clean Architecture does **not** apply here, and why saying so matters

Clean Architecture was written for systems whose entities are business objects with behaviour. This
is a **numerical pipeline**, and two of its prescriptions are actively wrong for it:

| Prescription | Verdict here |
|---|---|
| Entities are objects; DTOs cross every boundary | ✗ **The `DataFrame` is the domain model**, not a framework detail. A 130×N panel decomposed into row objects to satisfy a layering diagram would destroy both performance and readability, and buy no safety |
| Invert every boundary with an interface | ◐ **Only where a second implementation exists or is contractually promised.** `L4` §1.3 already says this, on YAGNI grounds, and that judgement stands — speculative Protocols are indirection with no reader |
| Top-level folders named for layers | ✗ The tree is organised by **domain (vertical slices)**, which is what makes `ownership.yaml` and the `sdd_gate` hook work at all. Layer lives *inside* a module, not above it |

> ★ **The adoption is of the Dependency Rule, not the folder taxonomy.** That is the part which
> earns its keep — it is what keeps a vendor SDK out of a valuation formula and lets D-07's sources
> be swapped without touching a single analytical domain. The concentric-circle diagram is a
> teaching device, and this system's circles are drawn per module.

**The concrete rules are `CA-1…CA-9` in [`L4-coding-standards.md`](L4-coding-standards.md) §18.**
Structural impact was deliberately assessed only **after D-12 was settled** (Victor, 2026-08-18), so
that the new domain was in the tree before the tree was judged.

# 5. AI AGENT ARCHITECTURE

## 5.1 Agent Roster

**Four agents for five seats.** Every AI-held seat has exactly one agent. **Seat 1 has none** —
there is no portfolio-construction agent, no strategist, no advisor to the decision seat.

| Agent                    | Serves seat (§1.5)        | Fund Role Equivalent     | Phase | Authority |
|--------------------------|---------------------------|--------------------------|-------|-----------|
| Fundamental Analyst Agent   | 1 Fundamental Analyst        | Equity Fundamental Analyst  | 2     | RECOMMEND |
| Quantitative Analyst Agent      | 2 Quantitative Analyst           | Quantitative Analyst     | 3     | RECOMMEND |
| Risk Manager Agent       | 4 Risk                    | Chief Risk Officer       | 4     | ALERT     |
| Report Writer Agent      | 5 Back / Middle office    | Investor Relations / Ops | 5     | **RECOMMEND** |

> **The Report Writer Agent serves D-09 Reporting only** *(v0.10.0)*. Seat 5 owns five domains; the
> agent is present in exactly one of them. D-02, D-07, D-08 and D-11 have no agent — they are
> deterministic domain work, and their authority is LEVEL 0 regardless of what the agent is rated.

> **Why the Report Writer is RECOMMEND and not AUTONOMOUS** *(changed 2026-08-13)*: everything it
> produces is read as advice. The autonomous parts of seat 5 — ingesting data, running the
> scheduler, reconciling and recording — are **not agent actions at all**. They are deterministic
> domain work in D-07/D-02/D-08/**D-11** with no agent in the loop, and they stay at LEVEL 0. The agent's
> authority describes what *the agent* does, not everything its seat owns.

> **The absence is deliberate and load-bearing.** There is no Portfolio Strategist *agent*. The
> capability it would have carried lives instead as the **Portfolio Strategy domain under seat 4**
> (§4.2), served by the Risk Manager Agent.
>
> The distinction matters: a **domain** computes when asked and hands back arithmetic; an **agent**
> is an actor with its own authority level, its own voice in a report, and its own standing to
> recommend. A "portfolio construction assistant" with a seat at the table is the shortest path to
> an AI that proposes allocations, and an allocation proposal read at 6am is a decision in
> everything but name.
>
> **If a future need looks like it wants a strategist agent, that is a signal to re-read §1.5**,
> not to add one.

## 5.1a The Discipline Card — owned by the Report Writer Agent

The **Discipline Card** is the glanceable, one-screen pre-commitment contract that opens every
single-stock report: verdict, conviction, entry, **stop**, **target**, thesis in one line, and the
falsification condition that would prove the thesis wrong. It exists so a decision follows a
written plan rather than a feeling.

**Ownership:** the Report Writer Agent, in **D-09 Reporting**, assembles, renders and delivers the
card. The facts it prints about the book come from **D-11 Recording**; the verdict comes from the
analysis layer. D-09 originates neither.

**Bounded:**

| Rule | Statement |
|---|---|
| **DC-1** | The Report Writer **renders** the card; it does **not originate** its content. Verdict, stop and target arrive from the analysis layer already formed. The Report Writer may lay them out and may not alter them. **This rule is neutral on how that verdict was produced** — see §1.6; the card takes what it is given. |
| **DC-2** | The card is **RECOMMEND** (§3.1) — as is everything the Report Writer produces. Formatting authority never extends to content. *(Until 2026-08-13 the card was a carve-out from an otherwise AUTONOMOUS agent; that carve-out is gone because the whole agent is now RECOMMEND. The card is the reason the rule changed.)* |
| **DC-3** | **Fail loud.** If the underlying narrative, verdict or thesis inputs are missing or the upstream call failed, the card build **must raise** and the report must show the failure. It may never emit a plausible-looking default — a card with no stop and no target rendered as though it were genuine is the defect this rule exists to prevent. |
| **DC-4** | The card shows **seat 2's and seat 3's views side by side, both attributed**, so any divergence between them stays visible rather than being silently resolved in the layout. Whichever view governs the action is stated explicitly on the card. |
| **DC-5** | The Report Writer may never render a verdict **more aggressive** than the one it received. Rendering may preserve or soften; it may never escalate. *(This constrains the renderer only. It does not decide how seats 3 and 3 combine — §1.6.)* |

> **Why the card sits in Back/Middle office rather than an analyst seat:** the card is a *record
> and delivery* artifact — it packages a decision surface and archives it. Authoring the thesis it
> summarises remains seat 2; producing the ranking it cites remains seat 3. Deciding whether to
> act on it remains seat 1.

## 5.2 Agent Design Principles

All AI agents must adhere to these principles. **They are `AP-n` (Agent Principle), renamed from `P1`–`P6` in v0.7.0** — `P1`–`P7` already mean something entirely different in `sdd/specs/constitution.md` (there, P3 is *quant ranks, thesis gates* and P5 is *fail loud, never silent*). Two live meanings for one ID is a defect.

### AP-1: Transparency Over Confidence
Every agent output must include:
- Confidence score (0.0 – 1.0)
- Data completeness score (0.0 – 1.0)
- Explicit list of data sources used
- Explicit list of data gaps (what the agent wanted but did not have)
- Explicit list of assumptions made

### AP-2: Cited Claims Only
Every factual claim, every number, every assertion in an agent's output must
be traceable to a specific data point. The output schema enforces a citation
structure. An uncited claim is considered a defect.

### AP-3: Mandatory Adversarial Thinking
Every agent that produces a directional recommendation (buy/sell/overweight)
must also produce the strongest counter-argument. A research agent recommending
BUY must articulate the bear case. A risk agent clearing a position must state
what risk it considered acceptable and why.

### AP-4: Graceful Degradation
If an agent cannot access required data, it must:
1. Attempt fallback sources (defined per module spec)
2. If still unavailable: produce a partial report clearly marked as INCOMPLETE
3. Never fabricate data to fill gaps
4. Reduce confidence score proportionally

### AP-5: Deterministic When Possible
**Do the computation where computation applies, instead of over-relying on an agentic AI or an ML
model.** Where a task can be accomplished with plain deterministic code — financial ratios,
technical indicators, risk metrics, P&L, position arithmetic — write the code. Reach for an LLM
only where the task genuinely requires judgement, synthesis or natural-language generation, and
reach for a learned model only where the relationship is genuinely statistical rather than
definitional. This buys reproducibility, auditability and a test that can actually fail.

The failure mode this guards against is **capability creep**: an LLM or a model is easy to point at
a problem, so it gets pointed at problems that a formula would have solved exactly, cheaply and
verifiably.

> **AP-5 and constitution P5 are complementary, not competing.** They share a number and nothing
> else, and both stand.
>
> | | Question it answers |
> |---|---|
> | **AP-5** (this document) | *What should perform the computation?* — deterministic code wherever it applies |
> | **P5** (`sdd/specs/constitution.md`) | *What happens when something fails?* — surface it loudly; never emit a plausible default |
>
> A deterministic calculation that silently returns a default on bad input satisfies AP-5 and
> violates P5. Both are required.

### AP-6: Versioned and Reproducible
Every agent output must record:
- Agent version
- Prompt version (if LLM-based)
- Model identifier and parameters (temperature, etc.)
- Input data snapshot reference (or hash)
- Timestamp

This allows any past recommendation to be audited and approximately
reproduced.

## 5.3 LLM Usage Policy

```text
┌────────────────────────────────────────────────────────────────┐
│                  LLM USAGE BOUNDARIES                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  USE LLM FOR:                                                  │
│  ✓ Synthesizing multiple data points into narrative analysis   │
│  ✓ Interpreting qualitative information (news, filings text)   │
│  ✓ Generating human-readable reports and briefs                │
│  ✓ Classifying events (positive/negative/neutral)              │
│  ✓ Extracting structured data from unstructured text           │
│  ✓ Answering ad-hoc natural language queries about data        │
│                                                                │
│  DO NOT USE LLM FOR:                                           │
│  ✗ Calculating financial ratios or metrics                     │
│  ✗ Computing technical indicators                              │
│  ✗ Portfolio optimization math                                 │
│  ✗ Risk calculations (VaR, correlation, etc.)                  │
│  ✗ Backtesting simulation execution                            │
│  ✗ Any arithmetic that must be precise                         │
│                                                                │
│  RATIONALE: LLMs are unreliable at math. All numerical         │
│  computation must be done by deterministic, tested code.        │
│  LLMs interpret and synthesize; code computes.                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

# 6. DATA ARCHITECTURE PRINCIPLES

## 6.1 Canonical Data Model Philosophy

All external data is transformed into **canonical internal formats** at the
point of ingestion. No downstream module ever works with provider-specific
formats. This enables provider switching without downstream impact.

```text
External Provider A ──┐
                      ├──► Adapter A ──┐
External Provider B ──┘                ├──► Canonical Format ──► All Consumers
                      ┌──► Adapter B ──┘
External Provider C ──┘
```

## 6.2 Data Categories

**Storage is files on local disk — Parquet for tabular data, JSON for documents and state.**
There is no database server, no cache server, and no vector store.

| Category          | Examples                            | Update Freq  | Storage     |
|-------------------|-------------------------------------|------------- |-------------|
| Market Data       | OHLCV, quotes, indices              | Daily        | **Parquet** |
| Fundamental Data  | Income stmt, balance sheet, ratios  | Quarterly    | **Parquet** |
| Alternative Data  | News                                | On fetch     | **JSON**    |
| Filing Data       | 10-K, 10-Q, 8-K, XBRL company facts | Event-driven | **JSON** (filing-aware cache) |
| Computed Data     | Features, indicators, scores, signals | On-demand  | **Parquet** |
| Agent Output      | Reports, theses, cards, briefs      | On-demand    | **JSON + Markdown** |
| Portfolio Data    | Holdings, transactions, P&L         | On change    | **JSON**    |
| System Data       | Config, logs, audit trail           | Continuous   | **YAML config, plain-text logs** |

> **Why this is a decision, not a limitation.** A single-user daily-batch pipeline gets no benefit
> from a database server, and the file layout is inspectable, diffable, trivially backed up, and
> survives a machine rebuild by copy. Introducing PostgreSQL/TimescaleDB/Redis would add an
> operational surface with no user-visible gain.
>
> **What this obliges the design to keep honest:** the properties a database would have given
> for free must now be provided deliberately — atomic writes (write-temp-then-rename, never
> in-place), idempotent re-runs (deterministic paths, overwrite not append), an explicit schema
> per Parquet artifact, and a stated cache-invalidation rule per cached artifact. These are
> requirements on the Data Engine (seat 5), not assumptions.

## 6.3 *(removed — freshness thresholds live in §8)*

> **Removed in v0.8.0.** This section restated the freshness thresholds that §8 already defines as
> configurable YAML. Two sources of truth for the same numbers guarantees that one drifts, and the
> drift is silent. **§8 is authoritative** for every staleness threshold.
>
> Heading retained as a tombstone (§16 T-2) because sibling specs cite "Section 6.3" by number.

## 6.4 Data Quality Rules

- **DQ-001:** Every ingested data point must have a source and timestamp
- **DQ-002:** Price data must pass sanity checks (no negatives, no > 50% daily
  moves without flagging, no zero volume on trading days)
- **DQ-003:** Financial statements must balance (assets = liabilities + equity
  within rounding tolerance)
- **DQ-004:** Missing data must be represented as `null`, never as zero or
  empty string
- **DQ-005:** All timestamps must be stored in UTC with timezone metadata
- **DQ-006:** Adjusted vs unadjusted prices must be explicitly labeled
- **DQ-007:** Stock splits and dividends must be tracked and prices adjusted
  accordingly in historical data

---

# 7. BUSINESS RULES & INVARIANTS

These are rules that must **never be violated** by any component of the
system at any time. They are the non-negotiable constraints.

## 7.1 Data Integrity Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-001 | **A monetary value is an integer amount in minor units PLUS an explicit currency code — inseparably.** Never a float. Never a bare integer. `1500` is not a monetary value; `(1500, "CAD")` is. No arithmetic combines two amounts of different currencies without an explicit, recorded FX step. An untagged amount is a defect, not a default-to-base. *(M-5. Merged with the former INV-027 in v0.6.0 — "integer cents" alone licensed exactly the untagged value the currency rule forbids.)* |
| INV-002 | All percentages calculated to minimum 4 decimal precision     |
| INV-003 | No floating-point equality comparisons (use epsilon tolerance)|
| INV-004 | Every AI-generated claim must have a citation reference       |
| INV-005 | Historical data is immutable once ingested and validated      |
| INV-006 | Audit trail entries are append-only, never modified or deleted|
| INV-007 | All timestamps in UTC; display conversion at presentation only|

## 7.2 Analytical Integrity Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-010 | Backtested returns must never be presented as expected returns|
| INV-011 | Every recommendation must include a bear case / counter-thesis|
| INV-012 | Confidence < 0.3 forces recommendation to INSUFFICIENT_DATA  |
| INV-013 | Confidence 0.3–0.5 caps recommendation at HOLD               |
| INV-014 | **Seats 3 and 3 must produce independent analyses.** Neither may take the other's *analytical output* — thesis, verdict, conviction, **the thesis's reading of a fair value**, `rank_score` — as an input, feature or label. Both may freely consume the same *data* from D-07 **and the same computed numbers from D-02**, including the fair value itself: D-02 belongs to seat 5, so neither seat inherits the other's conclusion by consuming it. Constrains **production only**; how the two outputs are combined is deferred (§1.6, §4.3). *(Wording corrected in v0.9.0 — closes `L4-coding-standards.md` Q-8. The pre-0.9.0 text listed a bare "fair value" as a seat-2 output; since D-02 moved to seat 5 that is no longer true, and the version that is forbidden is the **interpretation** a thesis places on it, not the computed number.)* |
| INV-015 | No analysis may use future data (look-ahead bias prevention)  |
| INV-016 | Backtest results must account for transaction costs           |
| INV-017 | Survivorship bias must be addressed in any historical analysis|

## 7.3 Portfolio & Risk Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-020 | System never executes trades autonomously                     |
| INV-021 | Risk alerts cannot be suppressed or silenced by any component |
| INV-022 | The system's *own* position-size **recommendation** may never exceed MAX_POSITION_PCT. This constrains what the AI proposes; it does **not** constrain what the fund manager may hold (M-2). |
| INV-023 | Portfolio concentration alerts fire at CONCENTRATION_THRESHOLD|
| INV-024 | Drawdown alerts fire at DRAWDOWN_THRESHOLD and cannot be muted|
| INV-025 | All portfolio values reconcile: sum(positions) = total value  |
| INV-026 | **Concentration and theme exposure are reported, never blocked** (M-2). No component may refuse, downgrade or hide a position because it increases concentration. Exposure is surfaced; the decision stays with the PM seat. |
| INV-027 | *(merged into **INV-001** in v0.6.0 — the amount and its currency are one invariant, not two. ID retained so nothing references a gap.)* |
| INV-028 | **Mandate-derived behaviours are flagged, not prevented** (M-3, M-4): scale-ins at a higher average cost, and short-hold round-trips in registered accounts, are surfaced with their rationale. A fund-manager override is **logged and visible**, never blocked. |

## 7.4 System Integrity Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-030 | API keys and credentials never appear in logs or agent output |
| INV-031 | No external API call without rate-limit compliance            |
| INV-032 | Pipeline failures must not cause data corruption              |
| INV-033 | System must remain functional if any single external API fails|
| INV-034 | LLM provider failure must not halt non-LLM operations        |

---

# 8. CONFIGURABLE PARAMETERS

The following values govern system behavior and must be configurable
without code changes (via configuration file or environment).

> ⚠️ **Per M-2, every exposure threshold below is a REPORTING threshold, not a veto.**
> Crossing one produces a LEVEL 2 ALERT (§3.1) that cannot be suppressed (INV-021). It never
> refuses, resizes or downgrades a position (INV-026). The only value that caps anything is
> `MAX_POSITION_PCT`, and it caps *what the system may recommend*, not what may be held (INV-022).

```yaml
# ── Portfolio Reporting Thresholds (alerts, NOT blocks — M-2 / INV-026) ──
MAX_POSITION_PCT: 15.0          # Cap on the system's OWN sizing recommendation (INV-022)
CONCENTRATION_THRESHOLD_PCT: 25.0 # Alert if single position exceeds this
SECTOR_MAX_PCT: 35.0            # Alert if single sector exposure exceeds this
THEME_REPORT_THRESHOLD_PCT: 40.0  # Alert (report only) on AI/semiconductor theme exposure — M-2
DRAWDOWN_ALERT_PCT: 10.0        # Portfolio drawdown alert threshold
DRAWDOWN_CRITICAL_PCT: 20.0     # Portfolio drawdown critical threshold
CORRELATION_ALERT: 0.85         # Alert if two positions corr > this

# ── Mandate Controls (M-3, M-4, M-5) ──
BASE_CURRENCY: "CAD"            # M-5 — the book mixes USD and CAD; currency always explicit
PYRAMIDING_FLAG_ENABLED: true   # M-3 — flag scale-ins at a higher average cost
REGISTERED_SHORT_HOLD_DAYS: 30  # M-4 — round-trips faster than this in a registered
                                #       account are flagged (CRA "carrying on a business")

# ── Data Freshness (hours) ──
STALENESS_PRICE_HOURS: 0.25     # 15 minutes
STALENESS_DAILY_HOURS: 18
STALENESS_FUNDAMENTALS_DAYS: 100
STALENESS_NEWS_HOURS: 24
STALENESS_FILINGS_HOURS: 48
PRE_EVENT_WINDOW_DAYS: 10       # RA-72/RA-139 — a thesis authored this close to a
                                #   scheduled event it depends on is marked pre_event

# ── AI Agent Controls ──
CONFIDENCE_FLOOR: 0.3           # Below this → INSUFFICIENT_DATA
CONFIDENCE_HOLD_CAP: 0.5        # Below this → max recommendation is HOLD
MAX_AGENT_LATENCY_SECONDS: 180  # Kill agent task if exceeds
AGENT_RETRY_MAX: 2              # Max retries on agent failure

# ── Pipeline Controls ──
MORNING_SCAN_TIME_ET: "06:00"   # Daily scan trigger
PIPELINE_TIMEOUT_SECONDS: 300   # Max total pipeline duration
RATE_LIMIT_BUFFER_PCT: 20       # Stay 20% under API rate limits

# ── Watchlist ──
MAX_WATCHLIST_SIZE: 200          # Max tickers on active watchlist
MAX_DEEP_DIVE_PER_DAY: 10       # Rate limit on full research reports

# ── Backtest Controls ──
DEFAULT_COMMISSION_BPS: 10      # 10 basis points per trade
DEFAULT_SLIPPAGE_BPS: 5         # 5 basis points slippage assumption
MIN_BACKTEST_YEARS: 3           # Minimum history for valid backtest
```

---

# 9. *(vacant)* · # 10. *(vacant)*

> **Removed in v0.7.0.** §9 *Phased Delivery Strategy* and §10 *Quality Attributes* were deleted.
> §9 was a greenfield month-by-month plan describing the construction of capabilities that already
> run; §10 stated performance and coverage targets that were never measured against this system.
> Neither was load-bearing, and both invited planning from numbers nobody had verified.
>
> **The numbers 9 and 10 are left vacant on purpose.** Sibling specs cite L0 sections by number;
> renumbering §11–§15 would silently redirect those citations. A vacant number resolves to nothing,
> which is the honest outcome. Do not reuse them.

---

# 11. TECHNOLOGY CONSTRAINTS

## 11.1 Mandated Technology

| Layer               | Technology            | Rationale                     |
|---------------------|-----------------------|-------------------------------|
| Primary Language    | Python 3.11+          | Data science ecosystem        |
| **Storage (tabular)** | **Parquet on local disk** | Columnar, typed, no server (§6.2) |
| **Storage (documents/state)** | **JSON on local disk** | Inspectable, diffable, no server (§6.2) |
| **Database**        | **none**              | Deliberate — see §6.2         |
| **Cache**           | **on-disk, filing-aware** | Invalidated by filing event, not by clock alone |
| **Vector Store**    | **none**              | No embedding/semantic-search capability exists or is planned |
| **LLM Provider**    | **Anthropic (sole provider)** | Tiered by cost-and-value; no multi-provider gateway |
| **LLM Framework**   | **none — direct SDK** | An agent framework would add indirection over a small number of call sites |
| Web/API             | FastAPI               | Local + phone access over private network |
| ML                  | PyTorch, gradient-boosted trees | Ranker / regressor / classifier bundle |
| Task Scheduler      | **unresolved** — cron or systemd timer | *Open: the daily run is not currently scheduled by anything* |
| Containerization    | *not used*            | Single machine, single user   |
| Version Control     | Git                   | Source and spec management    |

## 11.2 Technology Constraints

- Must run on a single machine initially (no Kubernetes requirement)
- Must support offline operation for non-data-fetch functions
- Must support provider switching without code changes to consumers
- Must not require GPU for core operations (LLM calls are API-based)
- All dependencies must be pinned to specific versions
- No proprietary/paid data sources required for Phase 1 (free tier viable)

---

# 12. INVESTMENT UNIVERSE

> **Universe breadth ≠ book composition (M-2).** The tables below describe what the system may
> *screen and analyse*. They do **not** describe a target allocation. The book is deliberately
> concentrated in the AI/semiconductor theme; broad sector coverage in the universe exists to give
> the ranking model breadth, not to push the portfolio toward diversification.

## 12.1 Scope

| Attribute          | Current Scope               | Future Scope                          |
|--------------------|-----------------------------|---------------------------------------|
| Asset Class        | US Equities (common stock)  | + ETFs (cash, unleveraged) — **never options or other derivatives (M-1)** |
| Exchanges          | NYSE, NASDAQ                | ★ **+ Toronto (TSX)** · + OTC (selective) |
| Market Cap         | Large + Mid cap (> $2B)     | + Small cap — **never penny stocks (M-1)** |
| Sectors            | All GICS sectors *(screening breadth — not an allocation target, M-2)* | No change |
| Geography          | US-listed only              | ★ **+ Canada** · + ADRs               |
| Base Currency      | **CAD**; book holds USD and CAD, always explicitly tagged (M-5) | No change — ★ **but TSX listings make CAD a *position* currency, not only the base**, so M-5's explicit-tag rule stops being a conversion concern and becomes a per-holding one |
| Instruments        | Long-only equity            | **No change — no short, no options hedging (M-1)** |
| Holding Period     | Medium-term (weeks–months); **hold winners, trim rather than exit (M-3)** | **Not tactical/day-trading — actively being reduced (M-4)** |

> ★ **What adding the TSX actually costs.** It is not one row. **D-07 has no Canadian filing
> source** — SEDAR+ is the Canadian equivalent of EDGAR and is not in the catalog, so a TSX name
> would arrive with **FMP-only fundamentals and no filing text**, which the whole of D-01 §5 depends
> on. ⚠ **The TTM precedence rule (`EDGAR wins`) has no Canadian analogue**, and that rule exists
> because FMP guessed wrong on MU by 71 %. **Treat TSX as a D-07 sourcing project, not a universe
> change**, and see D-07 §5A for what a new source has to prove before it is trusted.

## 12.2 Excluded (Permanently)

Per **M-1**, these are excluded permanently — not deferred to a later phase:

- **Penny stocks** (< $5 share price AND < $500M market cap)
- **All derivatives** — options (including hedging and covered calls), futures, swaps, warrants
- Cryptocurrencies
- Forex (as a position; FX conversion for the CAD/USD book is operational, not a position — M-5)
- Commodities (direct)
- Fixed income (direct)
- Private equity / venture
- Leveraged / inverse ETFs

> Any roadmap item elsewhere in this document that implies options analysis, short positions or
> tactical day-trading is **superseded by M-1 and M-4** and should be struck when that section is
> next revised.

---

# 13. GLOSSARY

| Term                    | Definition                                                       |
|-------------------------|------------------------------------------------------------------|
| **Agent**               | An AI-powered module that performs an analytical role, producing structured output from structured input. Agents may use LLMs for reasoning and synthesis. |
| **Alpha**               | Returns above a benchmark (e.g., outperformance vs S&P 500).    |
| **AP-n / D-nn / SEAT-n / M-n** | Identifier families defined in §16. `AP-` agent principle, `D-` domain, `SEAT-` seat, `M-` mandate rule. Cite these rather than section numbers — sections move, IDs do not. |
| **Backtest**            | Simulating a strategy against historical data to evaluate performance. Subject to numerous biases that must be disclosed. |
| **Basis Points (bps)**  | 1/100th of a percentage point. 100 bps = 1%.                    |
| **Bear Case**           | The pessimistic scenario for an investment thesis.               |
| **Bounded Context**     | A domain boundary where a particular model and language apply consistently. From Domain-Driven Design. |
| **Bull Case**           | The optimistic scenario for an investment thesis.                |
| **Canonical Format**    | The standardized internal data format used across the system, independent of any external provider's format. |
| **Catalyst**            | An event or development expected to drive a stock's price.       |
| **Concentration**       | Overexposure to a single stock, sector, or factor.               |
| **Confidence Score**    | A 0.0–1.0 value indicating the agent's self-assessed reliability of its output, based on data completeness and analytical certainty. |
| **Correlation**         | Statistical measure (-1 to +1) of how two securities move relative to each other. |
| **CVaR (Conditional VaR)** | Expected loss given that the loss exceeds VaR. Also called Expected Shortfall. |
| **Dashboard**           | A single-pane view of portfolio state and pending decisions. **Not built and not yet specified** — the term is retained in §1.3 as an intended capability, and its scope, contents and owning domain are deliberately left for a future amendment. |
| **Discipline Card**     | The one-screen pre-commitment contract opening every single-stock report: verdict, conviction, entry, stop, target, one-line thesis and the falsification condition. Owned by the Report Writer Agent (§5.1a) but never authored by it. |
| **Domain**              | A bounded context — one coherent area of responsibility, owned by exactly one Seat, carrying its own invariants and (after restructuring) its own directory. Enumerated as `D-00`…`D-10` in §16.2. |
| **Feature Contract**    | The versioned, published schema of what D-02 computes — the artifact INV-4 train/inference parity asserts against. Owned by D-02 (seat 5), consumed by D-01, D-03 and D-04. Its absence is why parity has historically been a convention rather than a gate. |
| **Neutral ground**      | A domain both analyst seats may consume without either inheriting the other's conclusion, because it belongs to a third seat. D-02 is the only one. The mechanism by which INV-014 is preserved structurally rather than by exception (§4.2). |
| **Drawdown**            | Peak-to-trough decline in portfolio value, expressed as percentage. |
| **Drift (model)**       | Degradation of a trained model's skill as market conditions move away from its training distribution. A failure mode specific to Model Training & Inference (D-04); detecting it is that domain's obligation. |
| **EDGAR**               | SEC's Electronic Data Gathering, Analysis, and Retrieval system. Public repository of all SEC filings. |
| **EV/EBITDA**           | Enterprise Value divided by Earnings Before Interest, Taxes, Depreciation, and Amortization. A valuation metric. |
| **Factor**              | A measurable characteristic of stocks that explains return patterns (e.g., value, momentum, quality, size). |
| **Falsification Condition** | The observable event that would prove an investment thesis wrong, written down *before* the position is taken. A thesis without one cannot be invalidated, only abandoned. |
| **GICS**                | Global Industry Classification Standard. Sector/industry taxonomy maintained by MSCI and S&P. |
| **Guardrail**           | A hard-coded or configurable constraint that prevents the system from producing dangerous outputs or violating risk policy. |
| **Invalidation**        | The act of detecting that a thesis's falsification condition has occurred. Owned by Fundamental Analysis (D-01) and surfaced on the Discipline Card. |
| **Invariant**           | A rule that must be true at all times, in all circumstances, with no exceptions. |
| **Look-ahead Bias**     | Using information in analysis that would not have been available at the time being analyzed. A critical backtest flaw. |
| **Mandate**             | The fund's stated investment posture (§1.4, `M-1`…`M-5`). Constrains *what may be proposed*, not merely how it is built. A proposal contradicting the mandate is out of scope however well engineered. |
| **Minor Units**         | The smallest indivisible unit of a currency (cents for CAD/USD). All monetary values are integer minor units **plus an explicit currency code** — see INV-001. |
| **Morning Brief**       | The daily summary report produced pre-market, containing overnight events, portfolio status, and action items. |
| **OHLCV**               | Open, High, Low, Close, Volume — the standard representation of a trading period's price action. |
| **P/E Ratio**           | Price-to-Earnings ratio. Stock price divided by earnings per share. |
| **P/S Ratio**           | Price-to-Sales ratio. Market cap divided by revenue.             |
| **Pipeline**            | A defined sequence of processing stages that transforms inputs into outputs, orchestrated by the system. |
| **Position Sizing**     | Determining how many shares/dollars to allocate to a single investment. |
| **Pyramiding**          | Scaling further into a winning position at a progressively higher average cost. Identified in `M-3` as the specific behaviour this system exists to curb; flagged, never blocked. |
| **`rank_score`**        | The cross-sectional score produced by Quantitative Analyst (SEAT-3) from the ranker/regressor/classifier bundle. Orders the universe; carries no thesis and no verdict on its own. |
| **Rebalancing**         | Adjusting portfolio weights back toward target allocation.       |
| **Registered Account**  | A Canadian tax-sheltered account (TFSA/RRSP). Frequent short-hold trading inside one risks CRA reclassification as *carrying on a business*, which is why `M-4` flags short round-trips there. |
| **Seat**                | A unit of accountability in the fund model (§1.5, `SEAT-2`…`SEAT-5`). A seat owns domains and is held either by the human or by the AI pipeline. Seats own work; agents perform it. |
| **Signal**              | A quantitative output indicating a potential action (buy, sell, hold) based on model criteria. |
| **Spec**                | A specification document that defines the expected behavior, inputs, outputs, and constraints of a system component. |
| **Stress Test**         | Simulating portfolio performance under extreme but plausible market scenarios. |
| **Survivorship Bias**   | Analyzing only currently-existing stocks, ignoring those that were delisted or went bankrupt, leading to overly optimistic conclusions. |
| **Theme Exposure**      | Aggregate portfolio weight in a correlated investment theme (for this fund, AI/semiconductors). Tracked and reported under `M-2`; **never automatically blocked**. |
| **Thesis**              | The structured investment rationale for owning (or not owning) a stock, including bull/base/bear cases. |
| **Train/Inference Parity** | The guarantee that inference builds features through the same code path and feature set the model was trained on. Its absence produces plausible-looking predictions from silently different inputs. |
| **VaR (Value at Risk)** | The maximum expected loss over a given time period at a given confidence level (e.g., "95% 1-day VaR of $10,000" means 95% chance of losing less than $10,000 in one day). |
| **Watchlist**           | The curated set of tickers actively monitored by the system.     |

---

# 14. CROSS-REFERENCES

> **Corrected in v0.9.0.** The previous table listed `specs/L1-domains/*.md`,
> `specs/guardrails/*.md` and `specs/SPEC-INDEX.md` — paths inherited from the generic sample this
> document was adapted from. **None of them exist in this repository.** A cross-reference that
> resolves to nothing is worse than an admitted gap, because it reads as though the work is done.
> Everything below is either a real file or explicitly marked as unwritten.

### Design tier — `sdd/design/rel6_design/` *(this tier; governs no code)*

| Document | Status |
|---|---|
| `L0-system-vision.md` | **this file** |
| `L1-data-engine.md` — D-07 | ✅ v0.1.0 |
| `L2-shared-money.md` — D-00 `Money` | ✅ v0.1.1 |
| **`L1-feature-engineering.md` — D-02** | ✅ **v0.1.0** — closes `L4` Q-10; records 4 inherited defects incl. a live INV-014 breach |
| **`L1-fundamental-analysis.md` — D-01** | ✅ **v0.1.0** — §7 is the substance: the three failure modes of an LLM analyst (inconsistency · bias · induced reader overconfidence), each with a reduce/monitor pair |
| **`L1-portfolio-strategy.md` — D-06** | ✅ **v0.1.0** — *pilot scope*. Records a live **P2/AP-5 violation**: position size is currently authored by an LLM while the contract says "risk-based, from max-loss-at-stop". §5.3 surfaces the collision it cannot avoid — **risk-based sizing mechanically fights M-2** |
| **`L1-risk-management.md` — D-05** | ✅ **v0.1.0** — *pilot scope*. §1.4 names the domain's defining tension: **INV-021 makes it unsilenceable and INV-026 makes it powerless**. §6 argues **VaR is near-useless on a deliberately concentrated ten-name book** and that concentration and drawdown replace it; §8 supplies the **`P` and `D` factors** D-06 §5.1d's dynamic risk budget needs, of which **`D` is buildable today** |
| **`L1-orchestration.md` — D-08** | ✅ **v0.2.0** — §1.2 states the **eight tasks and their expectations**; §1.5 is a **rebuild inventory** for the ten functions currently breaking §4.3. **§5A carries the first stated production cadence** — daily **10:00 ET off the day-T open**, retrain the **first trading day of each month**, in-process graph behind a thin timer — and records the three collisions it exposes, of which **the open-anchored decision vs. the close-anchored label (INV-4) is a live cross-domain break** (QO-7) |
| **`L2-signal-combination.md`** — §1.6 | ✅ **v0.1.0** — ★ **resolves the deferred combine point.** Proves the current z-blend gives a **2.0× selection bias under pure noise**; shows dense thesis coverage costs **6.3–19 % of NAV/yr**, so D-01 **cannot** be a ranker; identifies **Black–Litterman** as the right formalism and **D-01's uncalibrated confidence** as the one thing blocking it. Recommends **quant ranks → thesis gates → risk alerts** |
| **`L2-shared-infrastructure.md`** — D-00 | ✅ **v0.1.0** — the last domain gap. §5.2 resolves the **temperature contradiction** (RA-60 requires it set; RM-1 measures variance that only exists if it is not 0 — production goes to **0** and stability moves to RA-61's perturbation probe); §5.4 **declares the retry exception to OR-14** that LLM calls were silently relying on; §5.5 gives **token accounting an owner**, which `L2-signal-combination.md` §7B was already priced against |
| **`L3-build-sequence.md`** | ✅ **v0.1.0** — the execution order, closing **§17.6** and `L4` **Q-3**. ★ Its argument: the order is set by the dependency graph **and by the measurement clocks**, and the second inverts the usual instinct — **calibration, counterfactual recording and arrival capture produce nothing for years and must therefore be built first**, because elapsed time is the only quantity here that cannot be bought back |
| **`L1-decision.md` — D-12** | ✅ **v0.1.0** — ★ the composition layer the L2 found had no home. §5 makes **P3 a property of the type**: the verdict set is a bounded meet-semilattice, so an upgrade is not merely forbidden but **inexpressible**, and the five algebraic laws are exhaustive property tests over a 3-element domain. §5.4 derives that **a gate cannot veto a SELL**; §6.3 finds the gate is useful **~20–37× before it is provable**, so it is justified on process, never on P&L |
| **`L1-reporting.md` — D-09** | ✅ **v0.2.0** — the last safety boundary before capital moves. §5: **three reliability classes on one screen** (fact · computation · judgement) and freshness **per component, not per card**; §7 pins D-15's three layers; §8 is where D-01's anti-overconfidence obligations execute |
| **`L1-recording.md` — D-11** | ✅ **v0.3.0** — written against **real BMO InvestorLine exports**; records 8 ingestion hazards (partial fills, CDR ticker collisions, FX-rate-in-prose, registered status not a field), answers **QA-63** the capital base, and owns the **arrival-quote capture** QQ-20 depends on |
| **`L1-model-training.md` — D-04** | ✅ **v0.1.0** — organised around the two defect classes this domain owns: **parity** (D-17, *a guard that filters is not a guard that checks*) and **promotion** (D-18, *a fallback indistinguishable from a result*). Implements HorizonSet v1 |
| **`L1-quantitative-analysis.md` — D-03** | ✅ **v0.5.0** — the **mathematical-provenance requirement** (§8, binds D-02…D-06), a review of the three-head model bundle (§9), and **§5.6: HorizonSet v1 decided by Victor 2026-08-16** — `{ production 1m · timing-only 1w · research 1q }`, the first mandate-derived decision taken in this tier under G-1 |
| `L4-coding-standards.md` | 🟡 v0.3.0 — **§1 only**; §§2–13 undrafted |
| L1 — D-10 Experiments | ⬛ **deliberately unspecified** — §4.2. Not a gap: what to experiment on is unknowable before the first E2E run. Gated by ST-2, not by a spec |
| L1 — D-05 | ⬜ **blocked** on the combine point (§1.6, `L4` Q-5) — as is `signal_engine.py`'s home (D-03 QQ-6) |
| `samples/**` | reference for **format and structure only** — its technology choices, values and details do not apply here (`L4` §1.8) |

### Authoritative tier — `sdd/specs/` *(governs `pipeline/**` today — see §17)*

| Document | Relevance |
|---|---|
| `sdd/specs/vision.md` | The authoritative statement of what is being built. **This file does not replace it** (§17) |
| `sdd/specs/constitution.md` | P1–P7, INV-1…9, DC-1…3, test tiers, change process, traceability |
| `sdd/specs/ownership.yaml` | spec → code globs; read by the `PreToolUse` gate |
| `sdd/specs/F0_code_map/spec.md` | The as-is map of `pipeline/**`, incl. the D-nn defect log (**D-19**) *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F1…F4, F9` | The specs governing live code today |

---

# 15. AMENDMENT PROCESS

This document may only be amended through the following process:

1. **Propose:** Create a written amendment proposal describing the change
   and rationale
2. **Impact Assessment:** Identify all lower-level specs affected by the
   change
3. **Review:** Fund manager reviews and approves
4. **Update:** Amend this document with a new version entry in Document
   Control
5. **Cascade:** Update all affected downstream specs
6. **Notify:** All AI agents operating from affected specs must receive
   updated context

> **The mandate (§1.4) and the seats (§1.5) amend only on the fund manager's word.**
> They are statements of investment posture and accountability, not engineering decisions,
> and no impact assessment or downstream cascade can justify changing them.

---

# 16. ID FAMILIES & TRACEABILITY

This document introduces several families of identifiers. Without a stated convention they drift,
collide, and get renumbered — and a renumbered ID silently invalidates every reference to it. This
section is the convention.

## 16.1 The families

| Prefix | Family | Defined in | Range in use | Cited by |
|---|---|---|---|---|
| **M-n** | **Mandate rule** — investment posture | L0 §1.4 | M-1 … M-5 | Any spec proposing scope. A proposal contradicting an M- is out of scope. |
| **SEAT-n** | **Seat** — who is accountable | L0 §1.5 | SEAT-2 … SEAT-5 | Domain specs; the code-ownership map |
| **D-nn** | **Domain** — bounded context | L0 §4.2 | D-00, D-01 … D-11 | L1 domain specs; **directory layout** |
| **AP-n** | **Agent design principle** | L0 §5.2 | AP-1 … AP-6 | Agent specs. *(Renamed from `P1`–`P6`; `P1`–`P7` in `constitution.md` are a separate family with separate meanings — see below.)* |
| **DC-n** | **Discipline Card rule** | L0 §5.1a | DC-1 … DC-5 | The report spec that owns the card |
| **DQ-nnn** | **Data quality rule** | L0 §6.4 | DQ-001 … DQ-007 | Validation rule implementations |
| **INV-nnn** | **Invariant** — must always hold | L0 §7 | INV-001 … INV-034 | **Tests, at the invariant tier** |
| **AC-n.k** | **Acceptance criterion** | L1 / L2 specs | per spec | **Exactly one test each** |
| **CT-n.k** | **Contract** — an authoritative shape | L1 / L2 specs | per spec | Contract tests |
| **G-n** | **Governance rule** — how this tier relates to `sdd/specs/` | L0 §17 | G-1 … G-7 | Anyone promoting a file, moving a governed path, or citing an invariant across tiers |
| **`<XX>-n`** | **Domain rule** — a rule owned by one L1/L2 spec, prefixed by that domain | the owning spec | `DE-` D-07 · `FE-` D-02 · `RA-` D-01 · `QA-` D-03 · `MT-` D-04 · `RK-` D-05 · `PS-` D-06 · `OR-` D-08 · `RP-` D-09 · `RC-` D-11 · `DN-` D-12 · `MO-`/`FX-` D-00 money · `SI-`/`GW-`/`CF-`/`LG-`/`SC-` D-00 infra · `CB-` L2-combination · `BS-` L3-build · **L4:** `ST-` §1.7 structure · `EH-` §5 errors · `IM-` §10 imports · `CN-` §14 constants · `PD-` §17 pandas · `CA-` §18 clean architecture | Tests and ACs **within that domain**. A domain rule binds its own domain only; a rule that binds two domains belongs in L0 |
| **`RM-n`** | **Monitor / metric** — a measurement with a threshold, not a rule | the owning spec | `RM-1 … RM-15` (D-01 §7) | The monitor report. Distinct from a rule: a rule can be violated, a metric can only be *read* |
| **`Q<X>-n`** | **Open question**, scoped to one spec | the owning spec | `QD-` D-07 · `QF-` D-02 · `QR-` D-01 · `QQ-` D-03 · `QT-` D-04 · `QS-` D-06 · `QK-` D-05 · `QP-` D-09 · `QC-` D-11 · `QO-` D-08 · `QN-` D-12 · `QB-` L2-combination · `QI-` D-00 infra · `QY-` L3-build · `QM-` D-00 · `Q-` L4 | Nothing binds on these; they are the register of what is undecided |

`AC-n.k` and `CT-n.k` follow the convention already in `sdd/specs/constitution.md` §6 rather than
inventing a competing one — `n` is the owning spec's number, `k` the ordinal within it.

### Why `AP-n` and not `P-n`

`sdd/specs/constitution.md` owns a `P1`–`P7` family about **how the project is built**. This
document's principles are about **how an agent behaves**. Two families, two scopes — but they
overlapped numerically, and two of the overlaps were dangerous rather than merely untidy:

| ID | Meant here (now `AP-n`) | Means in `constitution.md` | Status |
|---|---|---|---|
| 3 | Mandatory Adversarial Thinking | ~~Quant ranks, thesis gates~~ → **Verdicts gate, never upgrade** | **Resolved 2026-08-13** — the constitution's P3 was narrowed to its safety half; the ordering mandate is gone, so the two no longer make competing architectural claims |
| 5 | Deterministic When Possible | Fail loud, never silent | **Both stand** — different questions, see AP-5 |

The `AP-` prefix is kept even though the semantic clash is resolved. An ID should be unambiguous on
sight, without the reader having to know which document it came from.

## 16.2 Domain IDs

These are the IDs that map to directories. Assigning them is what makes a restructure checkable.

| ID | Domain | Owning seat | Path (`L4` §1.2) | LLM? |
|---|---|---|---|---|
| **D-00** | Shared Infrastructure | *(no seat — cross-cutting)* | `src/shared/` | gateway only |
| **D-01** | Fundamental Analysis | SEAT-2 | `src/fundamental/` | **yes** |
| **D-02** | **Feature Engineering** *(was Valuation, SEAT-2 — v0.9.0)* | **SEAT-5** | `src/feature_engineer/` | no |
| **D-03** | Quantitative Analysis | SEAT-3 | `src/quant/` | no |
| **D-04** | Model Training & Inference | SEAT-3 | `src/models/` | no |
| **D-05** | Risk Management | SEAT-4 | `src/risk/` | no |
| **D-06** | Portfolio Strategy | SEAT-4 | `src/portfolio/` | no |
| **D-07** | Data Engine | SEAT-5 | `src/data_engine/` | no |
| **D-08** | Orchestration | SEAT-5 | `src/orchestration/` | no |
| **D-09** | **Reporting** *(narrowed from Recording & Reporting — v0.10.0)* | SEAT-5 | `src/reporting/` | rendering only |
| **D-10** | **Experiments** *(P7-exempt — added v0.9.0)* | SEAT-3 | `src/experiments/` | no |
| **D-11** | **Recording** *(split out of D-09 — v0.10.0)* | SEAT-5 | `src/recording/` | **no** |
| **D-12** | **Decision** *(added v0.17.0)* | SEAT-5 | `src/decision/` | **no** |

SEAT-1 owns no domain. That is not a gap to be filled.

> **On narrowing D-09** *(v0.10.0)*. D-09 keeps its ID and means **Reporting**; the extracted half
> is issued a **new** ID, D-11 Recording. This is a *narrowing*, not a reuse: everything D-09 meant
> before still lives in D-09 or in a domain that names it. An existing citation of D-09 — the
> Discipline Card, the briefs, DC-1…DC-5, the Report Writer Agent — resolves to the same work it
> always did, so nothing silently redirects (T-1). The half that moved out is the half no existing
> citation pointed at by ID.
>
> **Why D-09 and not D-11 kept the name.** The reporting half carries almost every existing D-09
> reference and the whole agent surface; repointing them would have been churn with a real chance
> of a missed reference, for no gain. `src/reporting/` also stays put in `L4` §1.1.

> **On reusing D-02** *(v0.9.0)*. T-1 says an ID is never reused for a different meaning, and this
> amendment does exactly that — deliberately, and once. The justification is that **Valuation was
> not superseded, it was absorbed**: `src/feature_engineer/valuation/` holds the same DCF, the same
> margin of safety, the same moat and quality scoring the old D-02 named. The domain grew and
> changed owner; it did not vanish and get replaced by something unrelated. Issuing a fresh ID
> would have left a D-02 that owned almost nothing.
>
> The old meaning is tombstoned in §4.2 rather than deleted, and **no future ID may be issued for a
> domain called "Valuation."** If a second case like this appears, prefer a new ID — one exception
> is a judgement call, two is a habit that makes every D- citation ambiguous by date.

## 16.3 Rules

| # | Rule |
|---|---|
| **T-1** | **An ID is permanent.** Once issued it is never reused for a different meaning and never renumbered, even if the file is reorganised. |
| **T-2** | **Retire by tombstone, never by deletion.** A superseded ID keeps its row and says where it went — as INV-027 does, and as §§9–10 do. A vanished ID leaves dangling references that resolve to nothing and are never noticed. |
| **T-3** | **Cite by ID, not by section number.** Section numbers move; IDs do not. Prefer "INV-014" over "§7.2". Where a section number must be cited across files, expect it to rot and check it. |
| **T-4** | **Every `AC-n.k` maps to exactly one test**, named so the mapping is obvious. An AC with no test is not satisfied, regardless of whether the code appears to work. |
| **T-5** | **Every spec ends with a traceability table**: `AC → test file::test → code module`. This is the artifact that makes the spec falsifiable rather than decorative. |
| **T-6** | **Every `INV-nnn` is owned by at least one test.** An invariant nothing tests is a wish. Where an invariant currently has no owning test, say so explicitly rather than leaving it implied. |
| **T-7** | **A new ID family requires a row in §16.1.** No family may exist that is not declared here. |

## 16.4 Known gaps in this document

Stated rather than left to be discovered:

- **INV-012 / INV-013** (confidence floors) have **no owner and no method for SEAT-3.** ML models
  emit a score, not a calibrated confidence. Applying a confidence floor to `rank_score` is
  currently undefined.
- **Several INV- entries have no owning test yet.** Per T-6 that is a gap, not a pass.
- **The combine point (§1.6) is unassigned**, and it blocks `pipeline/core/signal_engine.py` and
  `pipeline/discipline/gate.py` (~420 LOC) from being placed in the target layout — `L4` Q-5. It is
  now *answerable*: constitution P3 was narrowed on 2026-08-13 and no longer mandates the
  rank-then-gate ordering, so this is a design decision rather than a constraint being waited on.
- ~~**D-02 has no L1 spec**~~ — **written 2026-08-16** (`L1-feature-engineering.md`). It surfaced a
  **live INV-014 breach**: `MoatScorer` blends a score derived from D-01's LLM-authored profile,
  inside what L4 assigns to SEAT-5. The D-02/SEAT-5 argument holds only if D-02 itself consumes
  neither analyst seat's output, and today it does. See that spec §8.3 and FE-21.
- **`AC-<n>.<k>` is ambiguous across tiers, accepted knowingly** *(decided 2026-08-15)*. The L-tier
  keys `n` on the **domain** (`AC-7.1` = D-07); constitution §6 keys it on the **F-spec**
  (`AC-7.1` = a future F7, reserved in `vision.md` §4 for tax & registered-account compliance).
  Both conventions stand as they are. The collision is latent, not live — no F5–F8 or F10 spec
  exists yet — and is to be disambiguated **when the first reserved desk graduates**, not
  pre-emptively. Recorded here so it is found rather than discovered.
- ~~**§6.3 and §8 both state the freshness thresholds.**~~ **Closed in v0.8.0** — §6.3 was removed
  and replaced by a tombstone pointing at §8. The row survived the fix and is corrected here.

---

# 17. TIER, AUTHORITY & PROMOTION

> **New in v0.9.0.** Two spec hierarchies now exist in this repository at once — the **F-specs**
> that govern `pipeline/**` today, and this **L-tier** that describes the `src/**` the parallel
> build is heading toward. Nothing said how they relate. This section says it.

## 17.1 The ladder

| Tier | Path | Authority | Governs which code |
|---|---|---|---|
| **Vision + Constitution** | `sdd/specs/vision.md`, `sdd/specs/constitution.md` | **Highest.** Vision sets the goal; the constitution constrains the means. A spec may add constraints, never contradict them | all of it |
| **Feature specs** | `sdd/specs/F<n>_<slug>/spec.md` + `ownership.yaml` | **Authoritative per feature.** Hook-enforced by `.claude/hooks/sdd_gate.py` | `pipeline/**`, by glob |
| **Design tier — L0…L4** | `sdd/design/rel6_design/` | **None.** Brainstorm, rationale, decision log | **nothing, yet** |
| **Samples** | `sdd/design/rel6_design/samples/` | **None, and not even as guidance.** Format and structure only — its technology choices, values and specific details do not apply here | nothing |
| **Archive** | `sdd/archive/` | Historical, frozen | nothing |

```text
╔══════════════════════════════════════════════════════════════════╗
║  NOTHING IN THIS TIER GOVERNS A LINE OF CODE.                    ║
║                                                                  ║
║  This document wins over L1, L2 and L4 — WITHIN this tier.       ║
║  It does not win over sdd/specs/. Until a file is promoted,      ║
║  `pipeline/**` remains the live system and F0–F9 remain the      ║
║  specs an implementer obeys.                                     ║
║                                                                  ║
║  "Highest-level specification" (How to Read This Document)       ║
║  is scoped to the hierarchy this document heads — L1, L2, L4 —   ║
║  not to the repository.                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

## 17.2 What L0 does *not* replace

L0 was adapted from a generic template and then reconciled against the real fund. Three places where
it and `sdd/specs/vision.md` **do not currently agree** — stated rather than left to be found:

| Topic | `sdd/specs/vision.md` (authoritative) | L0 (this tier) | Resolution |
|---|---|---|---|
| **Seats** | §2 — **four** seats: Fundamental Analyst / PM / Trader / Back-office+Risk | §1.5 — **five**: analyst split into Research + Quant; PM and Trader merged | **Vision wins until Victor amends it.** L0's five-seat model binds design work inside this tier only |
| **Decomposition** | §4 — by **desk**, F-numbered, one spec per desk | §4 / §16.2 — by **domain**, D-numbered, one directory per domain | Orthogonal, not contradictory: a desk is a *deliverable*, a domain is a *bounded context*. §17.5 maps them |
| **Mandate** | §3 — the source | §1.4 M-1…M-5 — a restatement | **If they ever diverge, vision.md is right.** L0 §1.4 is a copy for locality, not a second source |

| ID | Governance rule |
|---|---|
| **G-1** | **`sdd/specs/vision.md` §2 (seats) and §3 (mandate) change only on Victor's word** — vision §6, L0 §15. No amount of design-tier reasoning promotes L0's seat model on its own. Promoting L0 therefore *requires* a vision amendment first, not as a side effect |
| **G-2** | **Where L0 restates something `sdd/specs/` already owns, `sdd/specs/` is the source.** L0's copy is for locality. A restatement that has drifted is a defect in L0, never in the source |

## 17.3 `INV-n` and `INV-nnn` are two different families

The most dangerous ID overlap in the repository, and it is invisible on a quick read: **only the
zero-padding tells them apart.**

| ID | Means | Owner |
|---|---|---|
| **INV-1** | No look-ahead | `sdd/specs/constitution.md` §2 |
| **INV-001** | A monetary value is an integer minor amount **plus** its currency | L0 §7.1 |
| **INV-4** | Train/inference parity | constitution §2 |
| **INV-014** | Seats 3 and 3 produce independent analyses | L0 §7.2 |

Worse than the collision: several are **duplicates across the two families**, which is a live drift
risk because nothing keeps them in step.

| L0 | Restates | Note |
|---|---|---|
| **INV-015** (no future data) | **constitution INV-1** | Same rule, two homes |
| **INV-001** (currency explicit) | **constitution INV-5** | L0's is stronger — it also mandates integer minor units |

| ID | Governance rule |
|---|---|
| **G-3** | **Always qualify an invariant with its source in cross-tier text**: "constitution INV-1", "L0 INV-014". A bare `INV-1` in a file that cites both families is ambiguous, and the zero-padding is too fragile to carry the distinction alone |
| **G-4** | **On promotion, a duplicate is removed in favour of the constitution's version** and the L-tier row becomes a tombstone pointing at it (T-2). Two homes for one rule guarantees one drifts, and the drift is silent |

## 17.4 Promotion — what must be true before a file moves into `sdd/specs/`

| ID | Governance rule |
|---|---|
| **G-5** | **A design-tier file is promoted only when all of the following hold.** Promotion is a deliberate, reviewed act — never a side effect of the file looking finished. |

```text
□ 1  Its acceptance criteria are WRITTEN and TESTABLE.
     (sdd/README.md loop step 3 — if you cannot write the ACs,
      it is not clarified yet, however polished the prose.)
□ 2  Any vision.md/constitution.md amendment it depends on has
     LANDED FIRST, in its own change, with rationale.  (G-1,
     constitution §5.3)
□ 3  Its globs are added to sdd/specs/ownership.yaml IN THE SAME
     COMMIT, and they match REAL, EXISTING paths.  (F3 CT-3.3)
□ 4  It has a traceability table: AC → test file::test → module.
     (T-5)
□ 5  A row is added to sdd/specs/README.md's spec index, and
     vision.md §4's desk registry is updated.
□ 6  The "design tier, not yet authoritative" banner is REMOVED —
     it is the only thing standing between a reader and an
     unenforceable spec being obeyed as law.
```

> **Step 3 is the one that fails silently.** A glob that matches nothing does not error — the
> `PreToolUse` gate simply never fires for those paths, and the enforcement disappears with no
> signal at all. `L4-coding-standards.md` ST-8 names this the highest-risk step in the whole
> migration, and it applies identically to a first-time promotion.

## 17.5 Coexistence during the parallel build

`L4` §1.7 ST-1 makes this a **parallel build**: `src/` is created alongside `pipeline/`, and the
legacy tree keeps running and keeps passing its tests until each domain is cut over. Both spec
families are therefore live simultaneously, and neither un-governs the other.

| ID | Governance rule |
|---|---|
| **G-6** | **While `pipeline/**` runs, its F-spec governs it.** An L-spec describes `src/**` and nothing else. A newly-promoted L-spec does not retire the F-spec covering the legacy code it duplicates |
| **G-7** | **An F-spec is retired only when the code it governs is deleted** (`sdd/README.md`). Its acceptance criteria must migrate into the receiving L-spec *before* that, or they are lost — the ACs are the only record of why the behaviour is what it is |

**Where each existing F-spec lands** — orientation for G-7, not a commitment:

| F-spec | Governs today | Receiving domain(s) |
|---|---|---|
| **F0** Code map | `pipeline/**`, descriptively | **Dies with `pipeline/`.** `src/` needs its own map; the D-nn defect log (**D-19**) must be carried over, not left behind |
| **F1** Disciplinary report | `pipeline/report/**` | **D-09** (render, deliver) + **D-01** (prompt assembly) — the split `L4` §1.5 already schedules for `report_writer.py` |
| **F2** Portfolio, journal & delivery | `pipeline/discipline/**`, `pipeline/delivery/**` | **D-05** (risk, flags) + **D-11** (journal) + **D-09** (deliver); the gate is **blocked on §1.6**. This spec now spans three domains — expect it to be the messiest cutover |
| **F3** SDD adoption | *(process — governs no code)* | **Tier-independent.** It governs the process both trees follow |
| **F4** Data plane | `pipeline/portfolio/**` | **D-11** (book, reconcile, trade log) — with `Money` from **D-00** replacing the float+sibling-string convention |
| **F9** Universe & fundamental sources | two ETL files | **D-07** — inherited verbatim by `L1-data-engine.md` §5, evidence table included |

## 17.5a ⚠ THE F-TIER WAS DELETED — 2026-08-18

**Decided by Victor.** All six F-specs — `F0_code_map`, `F1_disciplinary_report`,
`F2_portfolio_and_delivery`, `F3_sdd_adoption`, `F4_data_plane`,
`F9_universe_and_fundamental_sources` — were **removed from `sdd/specs/`**, to end the confusion of
two live spec sets.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THIS DEPARTS FROM G-7, AND THE DEPARTURE IS RECORDED RATHER     ║
║  THAN GLOSSED.                                                   ║
║                                                                  ║
║  G-7 retires an F-spec only when the code it governs is deleted. ║
║  pipeline/** still runs. So the F-specs went FIRST and their     ║
║  code follows at B7.                                             ║
║                                                                  ║
║  ★ THE CONSEQUENCE, STATED PLAINLY: pipeline/** IS NO LONGER     ║
║  SPEC-GOVERNED. Its globs were REMOVED from ownership.yaml       ║
║  rather than left pointing at deleted files — a stale glob       ║
║  matches nothing and the gate FAILS OPEN SILENTLY (ST-8).        ║
║  It now requires the constitution only, which is honest: the     ║
║  legacy tree is being replaced, not maintained.                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**What was carried over before deletion (G-7's substance, if not its timing):**

| From | What | Landed in |
|---|---|---|
| `F0` §12 | **`D-19`** — DCF returns an enterprise value per share with no net-debt subtraction | ✅ **already** in `L1-feature-engineering.md` §8.1 / **FE-18** |
| `F4` | **`AC-4.9`** — money arithmetic exact and unbiased, **19 passing tests** | ✅ `L2-shared-money.md` **AC-M.1** |
| `F0` | the whole-system code map | ⚠ **not carried — `src/` needs its own**, and `tests/test_code_map.py` (33 tests) was deleted with it |
| `F1`/`F2`/`F9` | acceptance criteria against live `pipeline/` behaviour | ⚠ **not carried.** The behaviour is respecified in D-09/D-05/D-11/D-07 from first principles, not migrated |

| ID | Rule |
|---|---|
| **G-8** | ★ **A citation to `F0`–`F9` anywhere in this tier is HISTORICAL PROVENANCE, not a readable reference.** The files are gone. *"Prior art: F2, 8/8 ACs green"* records that the code once had a governing spec and passed it — it is evidence about the past, and no reader should look for the file |
| **G-9** | ⚠ **`pipeline/**` is now ungoverned by design.** Changes to it are outside the SDD loop. **If it needs a real change before B7, that is the signal to bring the change into `src/` instead** — the legacy tree should be receiving bug-stops, not features |

## 17.6 What this section deliberately does not decide

- **Whether the L-tier ultimately replaces `vision.md` and `constitution.md` or sits beneath them.**
  Today it sits beneath. That is a decision for the promotion of L0 itself, and it needs Victor
  (G-1), not an argument from consistency.
- ~~**The migration's phase ordering**~~ ✅ **CLOSED — [`L3-build-sequence.md`](L3-build-sequence.md)**
  (v0.19.0). `L4` Q-3 turned out to be a non-question: **ST-2's one-way import rule takes D-10 off
  the critical path entirely**, so its position is unconstrained by every other domain.
- ~~**The combine point**~~ ✅ **CLOSED — [`L2-signal-combination.md`](L2-signal-combination.md) and
  the new domain [`L1-decision.md`](L1-decision.md) (D-12)**, L0 v0.17.0. ⚠ *This bullet stood stale
  for two versions after the question was answered; found by the 2026-08-18 consistency audit.*
- **Whether the L-tier ultimately replaces `vision.md`** — still open, still needs Victor (G-1).

---