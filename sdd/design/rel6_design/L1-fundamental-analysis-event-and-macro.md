# L1 Design Note: Events, Surprises & Macro — proposed additions to D-01

> **Tier:** `sdd/design/rel6_design/` — **design tier, non-authoritative. Nothing here binds yet.**
>
> **Status (v0.4.0):** two rounds of independent review folded in — **§3.13** (round 1) and
> **§3.14** (round 2). ✅ **Every target is now decided**; §3.14.6 carries the final four.
>
> **Prior status (v0.2.0):**
> · **§1 and §2 — ✅ FOLDED IN.** They are now `L1-fundamental-analysis.md` **§10A / §10B**, rules
>   **RA-69…RA-87**, with ACs **AC-1.41…AC-1.55**. **The spec governs; this note keeps the
>   reasoning that did not belong in it.**
> · **§3 — ✅ methodology DECIDED, ⚠ not yet folded in** (tracked as spec **QR-11**). Decisions at
>   §3.11.
> **Companion to:** the master prompt registry and the output template.

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.4.0 | 2026-08-20 | Victor | ★ **Round 2 — §3.14.** ✅ **Sector file adopted** (spec §10C) with a **fourth** guard the reviewer added: prose → sampling → ordering → **schema**, *"and the last one looks like maintenance."* ⚠ **Three of my own numbers corrected back**: the effect-size sensitivity is **~8.7×, not ~5×**; **ρ = 0.6 was as assumed as their ρ = 0** (now measurable — **RM-16**); and **vintages ARE obtainable** — ALFRED, not FMP. ★★ **My contribution: the level/rank asymmetry.** Shared error is not merely *neutral* for ranking — it **cancels**, leaving `2(1−ρ)σ²`, so **L2's CB-19 case is strengthened rather than spared**. ★ **Targets: five → four**, the two decompositions merged — **with a two-estimator caveat, because five annual observations cannot support a fitted `β`.** |
| 0.3.0 | 2026-08-20 | Victor | ★ **Independent review folded in — new §3.13.** Adopts the **Q1/Q2/Q3 triage** (forecast / exposure / attribution) as the organising frame, the **perfect-foresight evidence** that replaces *"we have no edge"* with *"no edge would suffice"*, the **vintage rule**, and the **completeness rule** on the sector file. ⚠ **Four corrections issued** — attribution was *not* absent (it is spec §10B); the `n×` correlated-error multiplier is an **upper bound**, not an estimate, and concentration shrinks it; the "~50 % false-positive" figure does not follow from an R²; the power calculation ignores **clustering** and roughly doubles. ★ **One target substituted**: real-yield-as-discount-rate demoted (D-02 plumbing needing no D-01 behaviour, behind a live D-19 defect), **fundamental attribution promoted** in its place — now spec **§10B.5, RA-92…RA-94**. |
| 0.2.0 | 2026-08-20 | Victor | ✅ **Decisions 1, 3, 5 and 10 taken.** §1 and §2 are **FOLDED INTO** `L1-fundamental-analysis.md` v0.8.0 as **§10A/§10B, RA-69…RA-87** — this note is now their *rationale*, not their statement. §3's methodology is **decided and not yet folded** (spec **QR-11**): the assumption ledger is adopted, the deterministic layer lives in **D-02**, and **hyperscaler capex is the primary macro variable**. Remaining open: 2, 4, 6, 8, 9. |
| 0.1.0 | 2026-08-20 | Victor / AI | Three additions raised 2026-08-20: (1) scheduled market calendar, (2) weekly unscheduled-event and price-jump check, (3) macro/sector methodology. |

---

# 0. THE RULE THAT DECIDES ALL THREE

Before any of it: the same boundary settles who owns what, and it settles it the same way each time.

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-01 INTERPRETS. IT DOES NOT DETECT, FETCH, OR COMPUTE.         ║
║                                                                  ║
║  "MU reports on 2026-09-24"           → D-07  (a calendar fact)  ║
║  "MU fell 9.2%, 3.1σ, unexplained     → D-03  (arithmetic)       ║
║   by index and sector"                                           ║
║  "CPI came in at 3.1%"                → D-07  (a released fact)  ║
║                                                                  ║
║  "That report is the next test of     → D-01                     ║
║   falsifier 2, and here is what                                  ║
║   result would break it"                                         ║
║  "Nothing in the bundle explains      → D-01                     ║
║   that move, which is itself the                                 ║
║   finding"                                                       ║
║  "This thesis assumed capex growth    → D-01                     ║
║   ≥12%; the release says 4%"                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **All three additions are therefore mostly not D-01 work.** The detection, the feeds and the
arithmetic belong upstream, and a great deal of it is already specified. What D-01 gains in each
case is a small, sharply-bounded set of behaviours — and in two of the three cases, the upstream
half already exists with **nothing calling it**.

---

# 1. THE SCHEDULED CALENDAR

## 1.1 What already exists — more than expected

`L1-data-engine.md` specifies most of this already:

| Piece | Where | State |
|---|---|---|
| `CalendarEntry` as an entity distinct from `CorporateEvent` | D-07 §2, **DE-19** | ✅ specified |
| Two dates per entry: event date **and** knowability date | **DE-18** | ✅ specified |
| Event features built from *occurred* + snapshot history, never today's read | **DE-20** | ✅ specified |
| Pre-run calendar gate over the whole universe; halts on unhandled action | D-07 **§6A**, DE-31…DE-36 | ✅ specified |
| `UNCHECKED` as a first-class result — never "no events" | **DE-35** | ✅ specified |
| Earnings, dividend, split, M&A, 8-K, macro-release feeds identified with knowability dates | D-07 §5A.4b | ✅ inventoried |
| Macro series: `treasury-rates`, `economic-indicators` (17 probed names), `economic-calendar` | D-07 §5A.4b, §5A.5 | ✅ inventoried |
| Consumption by **"D-01 as thesis-invalidation triggers and event-risk context"** | D-07 §5A.4b | ⚠ **named, never specified on the D-01 side** |

> ★ **The gap is exactly one sentence wide.** D-07 says its calendar is consumed by D-01 as
> invalidation triggers. **`L1-fundamental-analysis.md` §10 contains no reference to a calendar at
> all** — invalidation is described as running "against new evidence", with no notion that some
> evidence is *scheduled* and therefore knowable in advance. Nothing is wrong; something is missing.

## 1.2 The trap that must be respected

D-07 measured it: **34.6 % of `earnings-calendar` rows are future-dated**, and a scheduled date is
a *revisable claim*, not a fact (DE-19). Two consequences bind D-01:

| ID | Rule |
|---|---|
| **RA-69** | ★ **A scheduled event is evidence about the future and never enters an evidence bundle as a fact.** It may be carried in a dedicated `calendar` block with its `knowable_at`, and no claim may cite it as support for a business fact. *"Earnings are on the 24th"* is not a reason for anything |
| **RA-70** | **A confirmed date and an estimated date are different fields and render differently.** Most vendor earnings dates are estimates until the company announces. ★ An estimated date presented as confirmed is a small lie that produces a real one — a pre-event brief written for the wrong week |

## 1.3 The three behaviours D-01 gains

### (a) ★ Event-aware staleness — replaces the clock

**RA-43 today:** a thesis with no invalidation check in `STALENESS_FILINGS_HOURS` is reported stale.
That is a **timer**, and a timer is the wrong instrument. A thesis is not stale because 168 hours
elapsed. It is stale because **a scheduled event that bears on it has happened and has not been
read.**

| ID | Rule |
|---|---|
| **RA-71** | ★ **Staleness is event-relative first, clock-relative second.** A thesis is `stale` if any calendar event of a class it depends on has *occurred* since its `as_of` without an invalidation check. The clock threshold remains as a floor for names with no events |
| **RA-72** | ★ **A thesis authored inside the window before a scheduled event it depends on is marked `pre_event`, with the date, on the card.** Not stale — *provisional*. ⚠ The reader must not learn that a verdict was written three days before an earnings report by remembering it themselves |

> ★ **RA-72 is the cheapest of the three and possibly the most valuable.** A thesis written the week
> before results is a different object from one written the week after, and today the card cannot
> tell them apart. The mandate's stated problem is **pyramiding-up** (vision §3) — adding at ever
> higher cost — and *"conviction was High and the report was four days pre-earnings"* is precisely
> the context that makes an add look better than it is.

### (b) The pre-event brief — pre-commitment, dated

★ This is J-15's falsifier machinery pointed at a **known date**. Written *before* the event, it
converts a scheduled release into a test the thesis can fail.

```text
  N days before a scheduled event on a watchlist name:

  1. Which falsifiers could this event resolve? Name them by ordinal.
  2. For each: what result would fire it, what result would clear it, and
     what result would leave it undetermined? Answer in the metric's own
     units, from the falsifier as written — you may not restate it.
  3. Which stated assumptions does this event test?
  4. What is already priced in, from D-02's expectations figures — NOT from
     your own view of what is likely.
  5. State what you will NOT learn from this event, so it is not
     over-read afterwards.

  You do not predict the result. A predicted result is a position taken
  before the evidence, and the whole point of writing this in advance is
  that it is written without knowing.
```

| ID | Rule |
|---|---|
| **RA-73** | ★ **The pre-event brief is written and hashed before the event, and is immutable after it.** A brief editable post-event is a memory of what we would have said. Its whole value is being wrong in public |
| **RA-74** | **The pre-event brief predicts nothing.** It maps outcomes to falsifier states. A brief containing an expected result is a defect — it is a forecast wearing a process's clothing |
| **RA-75** | ★ **Item 5 — "what this event will not tell you" — is mandatory.** A quarterly result is over-read by default, and naming the limit in advance is the only moment at which naming it is free |

### (c) The post-event read

Deterministic comparison (D-02: actual vs guided vs consensus) → D-01 answers only: *did the stated
condition occur?* This is **V-01/V-02 unchanged**, triggered by the calendar rather than by a
crawler. **No new prompt is needed** — which is the correct outcome.

## 1.4 Scope: narrow, and why

| Class | Scope | Cadence |
|---|---|---|
| Earnings — watchlist names | `practice_watchlist` (13) + any name with a live thesis | brief at T−3 trading days |
| Earnings — universe | the 130-name universe | ★ **calendar only, no brief** — it feeds D-05 event risk, not D-01 |
| Macro releases | the fixed set in §3.5 | ★ **book-level, not per-name** — one brief, not thirteen |
| FOMC | the eight scheduled meetings + minutes | book-level |
| Dividend / split | declared, per name | no brief — deterministic, D-07 handles |

| ID | Rule |
|---|---|
| **RA-76** | ★ **Pre-event briefs are written for names with a LIVE THESIS, never for the universe.** A brief for a name nobody holds and nobody has analysed is a report with no reader. This is what keeps the cost of the calendar near zero |
| **RA-77** | **A macro or FOMC brief is written once at book level, never per ticker.** Thirteen near-identical CPI briefs is the failure mode, and it is also how a macro narrative gets thirteen chances to leak into thirteen theses |

---

# 2. UNSCHEDULED EVENTS, SURPRISES & SUDDEN MOVES

## 2.1 The upstream half exists and has no trigger

D-07 §5A.5 ranks `sec-filings-search/form-type` (the 8-K feed) **#3 by value ÷ effort**, with the
note:

> *"Publication-stamped material-event feed → CT-7.4 cache invalidation and D-01 invalidation
> monitoring. **Both already specified, neither has a trigger.**"*

★ **That sentence is this addition.** The feed is identified, the consumer is specified, and nothing
connects them.

## 2.2 Detection is arithmetic — D-01 must not do it

| Question | Owner |
|---|---|
| Did the price move abnormally? | ★ **D-03** — return vs trailing volatility; a threshold on a z-score |
| How much of the move was market, sector, idiosyncratic? | ★ **D-02/D-03** — a decomposition, not a judgement |
| Was there an 8-K, and of what item type? | **D-07** — a feed with item codes |
| Was there news, and is it material? | **D-01** cheap tier — E-14 exists already |
| **Does any of it bear on the thesis?** | ★ **D-01** — the only judgement in the chain |

| ID | Rule |
|---|---|
| **RA-78** | ★ **D-01 never detects a price move.** It receives a decomposed move as an input with its arithmetic trail, exactly as it receives a fair value. A prompt that reads a price series and decides it moved a lot is arithmetic in a prompt (RA-45, P2) |

## 2.3 ★ The unexplained-residual finding

The single most useful output of this whole addition, and it is nearly free:

```text
   move  =  market beta  +  sector  +  idiosyncratic residual
                                            └─────┬─────┘
                                                  │
                       only the residual needs an explanation
                                                  │
              ┌───────────────────────────────────┴──────────────┐
              │                                                  │
   the bundle explains it                    NOTHING in the bundle explains it
   (8-K, news, guidance)                                  │
              │                                           ▼
              ▼                        ★ THAT IS THE FINDING, NOT A FAILURE
   route to V-01: does it                "the market repriced this name by
   fire a condition?                      3.1σ and our evidence does not say
                                          why" — an information gap with a
                                          direction, and the highest-value
                                          thing a monitor can tell a PM
```

| ID | Rule |
|---|---|
| **RA-79** | ★ **An idiosyncratic move the evidence does not explain is reported as an unexplained move, never rationalised.** ⚠ An LLM asked *"why did this stock fall"* will always produce a reason, and a plausible reason attached to an unexplained move is strictly worse than the honest gap — it closes an open question with a fabrication |
| **RA-80** | ★ **An unexplained residual is a `data_gap` with `obtainable: fetchable`**, not a narrative. It is a research instruction: *go find out.* This is S-4's `would_change` applied to price action |
| **RA-81** | **Direction is reported; causation is not inferred from direction.** "Fell on the news" requires the news to precede the fall in the timestamps, and D-07 supplies both timestamps |

## 2.4 The 8-K item-code triage — the concrete engine

8-K item numbers are **semantically typed by the SEC**, which makes most of this triage
deterministic. ★ The classification below is a lookup, not a judgement:

| Item | Meaning | Route |
|---|---|---|
| **4.02** | ★ **Non-reliance on previously issued financial statements** | ⛔ **highest severity in the system.** Every extraction from the affected periods is invalid; every scorecard level resting on them is unsupported. **Escalate immediately, mark the thesis degraded** |
| **4.01** | Change in certifying accountant | ⛔ escalate deep tier; pair with E-09 `ap.auditor` |
| **2.02** | Results of operations | route to the post-event read (§1.3c) |
| **1.01 / 1.02** | Entry into / termination of a material agreement | escalate if a falsifier names a counterparty or contract |
| **2.01 / 2.05 / 2.06** | Acquisition or disposition; exit costs; impairment | ★ escalate — impairment is management scoring its own capital allocation (J-06) |
| **3.01** | Delisting notice / listing-rule failure | ⛔ escalate |
| **5.02** | Departure or appointment of directors/officers | escalate if `capital_allocation` rests on a named individual's record |
| **1.05** | Material cybersecurity incident | escalate |
| **7.01 / 8.01** | Regulation FD / other events | ★ cheap-tier triage — this is where the genuinely unexpected lands, and it is unstructured by design |

| ID | Rule |
|---|---|
| **RA-82** | ★ **8-K routing is a deterministic table keyed on item number, not an LLM classification.** The item code is structured data the SEC already assigned. Asking a model to classify what the form has declared is the reverse of AP-5 |
| **RA-83** | ★ **Item 4.02 invalidates extractions, not just the thesis.** A non-reliance filing means the *facts* the analysis was built from are withdrawn. `evidence_coverage` for the affected periods goes to zero, RA-38's floor fires, and the verdict becomes `INSUFFICIENT_DATA` — not "HOLD pending review" |
| **RA-84** | **Only `7.01`/`8.01` and news reach the cheap-tier LLM.** Everything else is routed by table |

> ★ **RA-83 is the strongest rule in this note.** A restatement is the one event that reaches
> backwards through everything already concluded. Treating it as "news to consider" instead of "the
> evidence has been withdrawn" is how an analysis survives the invalidation of its own inputs.

## 2.5 Cadence — daily *and* weekly, for different reasons

★ **"Weekly" is right for the sweep and wrong for the trigger**, and the two need separating.

| Layer | Cadence | Why |
|---|---|---|
| Residual detection + 8-K item routing | **daily**, deterministic, ~free | A 4.02 on Monday cannot wait until Friday |
| Cheap-tier triage of what the router escalated | **daily**, Haiku, only on escalations | RA-42 |
| Deep-tier confirmation | **on escalation only** | V-02 |
| ★ **The weekly sweep** | **weekly** | Catches what no single day trips: **a drip of small unexplained residuals that never breaches the daily threshold**, guidance quietly not repeated, a risk factor added, a competitor's capacity moving from `announced` to `operating`, an approaching falsifier that is approaching slowly |

| ID | Rule |
|---|---|
| **RA-85** | ★ **The weekly sweep's subject is ACCUMULATION, not events.** Events are handled daily. The sweep exists for the slow kind of change, which is invisible at daily resolution and is where a thesis usually actually dies |
| **RA-86** | **The weekly sweep runs whether or not anything happened, and reports "nothing accumulated" explicitly** (RA-30, DE-35). ★ A sweep that only appears when it has something to say cannot be distinguished from a sweep that did not run |
| **RA-87** | ⚠ **The sweep produces no verdict and no recommendation.** It reports state changes and routes them. INV-6's one-actionable-recommendation-per-day is untouched, and must be — a weekly monitor that started proposing trades would be a second decision channel |

---

# 3. MACRO, INDUSTRY & SECTOR — the methodology discussion

> ⚠ **This section proposes no rules.** It sets out why the obvious approach is the wrong one, four
> methodologies that are not, and a recommendation. The decisions at §3.11 are Victor's.

## 3.1 Why this is the most dangerous thing in the whole system to hand an LLM

Three reasons, and they compound:

**It is the domain where fluent text is cheapest and content is thinnest.** *"With the Fed on hold
and real yields elevated, multiple compression remains a headwind for long-duration assets"* is a
sentence a model can produce for any month of the last fifteen years, about any stock. It has the
grammar of analysis and the content of weather small-talk. §7.3's whole argument — fluency reads as
insight, and the reader sizes the position off the tone — has its worst case exactly here.

**It is unfalsifiable on our timescale.** J-15 demands falsifiers that are *observable, dated and
checkable*. A macro view — "the cycle is turning" — is none of the three. It is never wrong on a
date; it is early. **A layer that cannot be wrong cannot be measured, and §7's entire apparatus is
built on measuring.**

**★ It is the one input that biases every name at once.** A per-name mistake costs one thesis. A
macro view leaks into thirteen theses simultaneously and in the same direction — which is
*correlated* error, invisible to RM-1 (each thesis is perfectly stable), invisible to RM-6 (the base
rate shifts uniformly), and visible only to RM-9's theme skew, after the fact. **Given a book that
is deliberately concentrated in one theme (vision M-2), a shared macro prior is the single most
efficient way to make every position wrong together.**

★ **How much worse — and the honest bound.** With `n` equal-weighted positions whose analytical
errors have variance `σ²` and pairwise correlation `ρ`, portfolio error variance is
`σ²·(1 + (n−1)ρ)/n`, while a *shared* error has variance `σ²`. So:

```text
    damage(shared)          n
   ─────────────────  =  ──────────────
   damage(per-name)      1 + (n−1)ρ
```

**At ρ = 0 that is `n` — 13×.** ⚠ **But ρ is not 0 here.** Thirteen names in one theme, scored by one
analyst against one rubric set, have *correlated* per-name errors by construction; at ρ ≈ 0.6 the
multiplier is ≈ **1.6×**, not 13×. **13× is the ceiling, not the estimate.**

> ★ **And the correction cuts the other way once you follow it.** A low multiplier means
> `σ²(1+(n−1)ρ)/n` was **already large** — the book never had `n`-fold diversification of analytical
> error to begin with. **The argument is not "a macro prior would spoil a well-diversified error
> budget"; it is "the error budget is already undiversified, and a macro prior is another draw from
> the same correlated pile."** That is a worse position to be in, not a better one.

★ **The case against forecasting is also stronger than "we have no edge"** — which invites *"so let
us get better at it."*
[Molchanov & Stangl, *The myth of business cycle sector rotation*](https://onlinelibrary.wiley.com/doi/full/10.1002/ijfe.2882)
(IJFE, 2024) tests sector rotation while **granting the investor perfect foresight of the cycle**:
across 15 NBER cycles, 1948–2022, perfect foresight earns **0.16 % per month risk-adjusted, before
transaction costs** — ≈ 1.9 %/yr. The earlier
[Jacobsen, Stangl & Visaltanachoti](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1572888_code386377.pdf?abstractid=1467457&mirid=1)
study over 1948–2007 puts it at 2.3 %/yr on the same terms.

⚠ **`L2-signal-combination.md` §4.3 records D-03's *entire* trading-cost budget as 6.0 %/yr.** An
oracle handing us the cycle **for free** would not pay for the trading it implies.

> ★ **Scope this argument honestly or it will over-prune.** It kills **forecast-and-trade**. It says
> nothing whatever about **forecast-free explanation** — which is what Q2 and Q3 (§3.13) are, and
> which is the stated purpose here: *explain the fundamentals, justify the prospects, explain the
> price trend.* ⚠ Citing a sector-rotation result against an attribution layer answers the wrong
> paper.

```text
╔══════════════════════════════════════════════════════════════════╗
║  WE HAVE NO EDGE IN FORECASTING THE ECONOMY, AND NEITHER DOES    ║
║  THE MODEL. THAT IS NOT A REASON TO IGNORE MACRO.                ║
║                                                                  ║
║  It is a reason to change the QUESTION:                          ║
║                                                                  ║
║    ✗ "What will the economy do, and what does that mean          ║
║       for our positions?"                                        ║
║                                                                  ║
║    ✓ "Our theses each assume something about the world.          ║
║       Which of those assumptions did this week's data            ║
║       just contradict?"                                          ║
║                                                                  ║
║  The first is a forecast we cannot make and cannot score.        ║
║  The second is a LOOKUP against something we already wrote       ║
║  down — cheap, checkable, and wrong in public when it is wrong.  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 3.2 The four constraints any answer has to satisfy

| Constraint | What it rules out |
|---|---|
| **P2 / AP-5** — no AI in deterministic work | An LLM reading a rate series and characterising it. The series is arithmetic |
| **L0 INV-014** — the two analyst seats stay independent | ★ **Macro context inside D-01 cannot be consumed by D-03/D-04 as a regime feature.** D-07 §5A.5 explicitly wants `treasury-rates` for *"regime features"* — SEAT-3's use. If macro lives in SEAT-2, that use becomes an INV-014 breach |
| **Vision §2 / M-2** — the AI never holds PM authority; concentration is deliberate | A macro layer that recommends reducing theme exposure. That is a portfolio decision and it is Victor's, and it fights a mandate that is chosen, not accidental |
| **RA-14** — you cannot un-see an anchor | Macro in the Stage-A bundle. "Rates are rising" quietly shades a moat judgement, and no instruction prevents it |

## 3.3 ★ The reframe: the unit of analysis is the assumption, not the economy

Every thesis already carries `assumptions[]` (CT-1.1, AP-1, J-17). Some are company-specific
(*"the cycle trough passed in FY2025"*); some are macro (*"hyperscaler capex grows ≥12 % through
2027"*). **Today nothing distinguishes them and nothing watches either.**

That is the whole opportunity, and it requires no forecast:

```text
   thesis v4 assumptions
     a1  "cycle trough passed in FY2025"          class: company
     a2  "hyperscaler capex grows ≥12% thru 2027" class: macro   ← watchable
     a3  "no >25% tariff on imported fab equip"   class: policy  ← watchable
     a4  "real 10y yield stays below 2.5%"        class: macro   ← watchable
                                                        │
                          each bound to an observable series at authoring time
                                                        │
                    ┌───────────────────────────────────┘
                    ▼
     release arrives (deterministic, D-07)
                    ▼
     compare to the assumption as written (deterministic, D-02)
                    ▼
     ★ D-01's only job:  holding | drifting | contradicted | not_yet_testable
        …and one sentence on what a contradiction does to the thesis
```

★ **This is §10's invalidation machinery pointed at a different input class**, and that is an
argument in its favour rather than a coincidence: it reuses a mechanism that is already specified,
already tested, and already understood to be *checking* rather than *deciding* (RA-39, RA-41). It
inherits RA-36's immutability for free — an assumption, like a falsifier, may be superseded and
never edited.

**What it deliberately does not produce:** a view on rates, a view on the cycle, a recommendation, or
a number. It produces the statement *"you assumed X; the data says not-X"* — which is the only macro
output this system can be held to.

## 3.4 The five methodologies, compared

| | **M-A** Falsifier substrate | **M-B** Assumption ledger | **M-C** Written-rule regime | **M-D** Learned regime | **M-E** Macro narrative |
|---|---|---|---|---|---|
| **What it is** | Macro series become legal `observable`s for J-15 falsifiers | §3.3 — macro assumptions tracked against releases | Versioned written criteria over observable series → a labelled context block, like a rubric | HMM / clustering over macro series → learned regime label | An LLM writes "what this means" over macro releases |
| **Produces** | more checkable falsifiers | assumption-state per thesis | a label + its base rate | a label + a probability | prose |
| **Owner** | D-01 (J-15) + D-07 (series) | D-01 §10 + D-02 (comparison) | ★ **D-02 — neutral ground** | D-04, SEAT-3 | D-01 |
| **INV-014** | ✅ clean — D-07 data | ✅ clean | ★ ✅ **clean *because* D-02 owns it — both seats may consume** | ✅ if SEAT-3 owns it, ⚠ D-01 may not consume it | ⚠ leaks a shared prior into every thesis (§3.1) |
| **P2 / AP-5** | ✅ | ✅ comparison is arithmetic | ✅ deterministic classification | ✅ genuinely statistical | ⚠ judgement over numbers |
| **Falsifiable** | ✅ by construction | ✅ by construction | ⚠ only if a base rate is published under the label | ✅ backtestable | ✗ **never** |
| **Cost** | ~$0 | ~$0 — reuses V-01 | low, deterministic | high — data, validation, tuning | k× tokens, weekly, forever |
| **Value now** | ★★ falsifiers stop being only company-level | ★★★ the thing that is actually missing | ★★ conditions the reader; ★ **supplies QP-4's missing reference class** | ★ unproven | ✗ negative — §3.1 |
| **Main risk** | a macro falsifier fires on noise | assumptions written vaguely at authoring | a label with no measured content reads as a forecast | the quant stack's problems, in a new place | reads as insight; is not |
| **Blocked on** | nothing | nothing | someone writing the criteria | universe expansion, `IC` measurement | — |

## 3.5 The recommendation

```text
   NOW      M-A  +  M-B  +  M-F        ~$0, reuses specified machinery
   NEXT     M-C, owned by D-02          once there is a use that needs a label
   LATER    M-D                         after the quant stack has its own house in order
   NEVER    M-E as a standalone product  — but see §3.5a
```

### The concrete "now" shape

| Piece | Owner | Mechanism |
|---|---|---|
| A fixed, versioned macro observable set (§3.5b) | **D-07** | already inventoried: `treasury-rates`, `economic-indicators`, `economic-calendar` |
| `assumptions[]` gains `class` and `observable` | **D-01** | a contract change to `CT-1.1` |
| Assumption ↔ release comparison | **D-02** | deterministic, with the arithmetic trail |
| Assumption-state judgement + one sentence | **D-01** | V-01's prompt, one new enum |
| Weekly macro **digest** — released vs expected, and which assumptions each touches | **D-09** renders, **D-02** computes | ★ no forecast, no narrative |

### 3.5a ★ The nuance on M-E — what is being rejected, and what is not

**Rejected:** a free-standing weekly macro outlook that characterises the environment and reasons
forward. It is unfalsifiable, it is the same for every name, and it is the correlated-error channel
of §3.1.

**Not rejected, and genuinely wanted:** the **digest** — a factual account of what was released,
against what was expected, with a link to each thesis assumption it touches. That is M-B rendered,
and it is what a back-office desk actually produces. ★ **The difference is one sentence at the end:
a digest stops at "here is what happened and what it touches"; an outlook adds "and so we think".
The second sentence is the entire disagreement, and it is where all the risk lives.**

### 3.5b The macro observable set — small and fixed, on purpose

An open-ended macro feed is an invitation to find a story. The set should be **short, written down,
and versioned like a rubric** (RA-33), chosen because the *mandate* is exposed to it:

| Series | Why this book cares |
|---|---|
| Real 10y yield / treasury curve | The discount rate in every DCF (D-07 §5A.5 priority #2); duration exposure of a growth-heavy book |
| FOMC decision + statement, 8 scheduled | The dominant scheduled repricing event |
| CPI / PCE | The input to the above |
| ★ Hyperscaler aggregate capex guidance | ★ **The single most load-bearing macro variable for this specific book**, and it is not a macro series at all — it is four companies' guidance (E-02). ⚠ Worth more than every rate series combined here |
| Semiconductor industry inventory / billings | The cycle variable J-07 asks about |
| Export controls / tariff actions on semi equipment | A policy variable that has repriced this theme before |
| USD/CAD | INV-5 — the book's base currency is CAD and the holdings are largely USD |

> ★ **The fourth row is the finding.** For a book concentrated in AI/semis, "macro" mostly is not
> macro — it is the capex plans of four customers. That is company disclosure, arrives on a
> **schedule we can put in the calendar (§1)**, is extractable (E-02), and is *falsifiable*. **The
> highest-value macro work available here is not macroeconomics.** Building a rates-and-cycle layer
> first would be answering a harder question with a worse instrument, and skipping the one that
> actually drives the book.

## 3.6 Sector and industry — a different problem, and the concentration changes it

Macro and sector get conflated and should not be. **Sector work is closer to what D-01 already does
well**, and the mandate makes it unusually cheap.

| | Macro | Sector / industry |
|---|---|---|
| Unit | the economy | an industry's supply, demand and pricing |
| Our edge | none | ★ real — it is company-level evidence aggregated |
| Falsifiable | poorly | ✅ capacity, inventory, ASPs, lead times are all observable |
| Already specified | no | ✅ **J-08 + E-13 do exactly this, per-analysis** |
| What is missing | everything | ★ **continuity** — it is recomputed per name and never accumulated |

★ **With 13 watchlist names largely in one theme, one sector read serves nearly the whole book.**
That inverts the usual cost argument: sector work is normally expensive because it must be repeated
per industry. Here it is repeated **thirteen times over the same industry**, which is waste today
and leverage tomorrow.

| Proposed | Detail |
|---|---|
| **M-F — the persistent sector file** | J-08's output becomes an accumulating, versioned artifact per industry instead of a per-analysis paragraph. Competitor capacity (E-13) accumulates with status transitions (`announced → under construction → operating`); inventory and ASP evidence accumulates; each entry is dated and cited |
| Reused by | every thesis in that industry, as a **bundle input** — so thirteen analyses share one evidence base instead of thirteen partial ones |
| ⚠ The risk | ★ **A shared sector file is a shared prior, which is §3.1's correlated-error channel again.** The mitigation is that it holds **evidence, not conclusions** — capacity rows and dated observations, never a sector view. If it ever acquires a "sector outlook" field it has become M-E through the back door |
| Weekly | the sector file's *changes* are exactly what the §2.5 weekly sweep should report |

## 3.7 Where it lives — and the argument that settles it

Vision §4 already reserves **F6 — *Macro & regime context: rates, cycle, sector rotation feeding the
analyst*, Analyst seat, 🔵 reserved.** So the desk exists on paper. The question is where the code
sits in the L-tier, and one constraint decides it:

```text
╔══════════════════════════════════════════════════════════════════╗
║  IF MACRO CONTEXT LIVES IN D-01, SEAT 3 CANNOT USE IT.           ║
║                                                                  ║
║  D-07 §5A.5 already wants treasury-rates for "regime features"   ║
║  — that is a D-04 training input. If the regime layer is a       ║
║  SEAT-2 product, D-03/D-04 consuming it is D-01 output entering  ║
║  the quant seat: INV-014, exactly.                               ║
║                                                                  ║
║  D-02 is the ONLY neutral ground (L0 §4.2). Put the              ║
║  DETERMINISTIC macro layer there and both seats consume it       ║
║  without either inheriting the other's conclusion.               ║
║                                                                  ║
║  D-01 keeps only the INTERPRETATION against a thesis's stated    ║
║  assumptions — which is a judgement, is per-thesis, and is       ║
║  useless to SEAT 3 anyway.                                       ║
╚══════════════════════════════════════════════════════════════════╝
```

**So: not a new domain.** The split is **D-07 (series) → D-02 (comparison, and later M-C's regime
label) → D-01 (assumption-state judgement only)**. F6 becomes the *name of the capability*
spanning three domains rather than a thirteenth domain — which is also how F9's data work already
sits across D-07 and D-02.

## 3.8 Staging — macro is blinded in Stage A, for RA-14's reason

Macro belongs in the **`view:full`** bundle (Stage B onward) and never in `view:blind`.

★ The argument is identical to the price argument and is not usually made: *"the Fed is cutting"* in
the context window while a model judges moat durability will shade the judgement, and no instruction
prevents it — the same finding that produced RA-14. **Macro is an anchor with the same properties as
a price and should be stripped by the same mechanism (MP-3: the field is absent, not forbidden).**

## 3.9 A macro read never modifies a verdict

| Proposed rule | Why |
|---|---|
| **Macro annotates; it never gates and never scores** | P3 permits a gate to make a verdict more conservative. ★ Even that is wrong here: a macro layer trimming verdicts across a theme *is* a top-down allocation decision, and allocation is SEAT-1's (vision §2). It also mechanically fights M-2, which says concentration is chosen |
| **A contradicted macro assumption produces an `InvalidationEvent`, not a verdict change** | RA-41, unchanged. D-01 reports that a stated condition occurred; whether it changes the position is Victor's |
| **No fifth scorecard dimension for macro** | RA-52 closes the set at four, and a macro score would be a number with no rubric, no dispersion check and no base rate |

## 3.10 How we would know any of it works

★ **Any macro or sector layer that is not measured is decoration**, and §7.5 already warns that
metrics become targets. Minimum bar before a label or a read is published to the card:

| Check | Bar |
|---|---|
| Assumption-state discrimination | Do assumptions marked `contradicted` precede thesis failures more often than assumptions marked `holding`? Until N suffices: **`not yet calibrated (N=…)`** (RA-30) |
| Base rate of the state | ★ If 90 % of assumptions read `holding` forever, the assumptions are written too loosely to be contradicted — a J-15 defect, not a macro one |
| Sector-file staleness | An accumulating file rots. Every row dated; rows past their horizon marked, not dropped |
| Correlated-error watch | ★ RM-9 theme skew, read **specifically** for the week after a macro digest. The failure mode of §3.1 has a signature: verdicts across one theme moving together without company-level cause |

## 3.11 ⚠ DECISIONS NEEDED — this is what I need from you

| # | Question | My recommendation |
|---|---|---|
| **1** | Adopt the §3.3 reframe — **track assumptions, never forecast the economy**? | ✅ **DECIDED 2026-08-20 — YES.** Assumption ledger only. ~$0, reuses §10, and it is the only macro output this system can be held to |
| **2** | Build **M-C** (written-rule regime labels) now, or wait? | ⚠ **OPEN — recommend wait.** It needs criteria authored and a use that needs a label; it becomes compelling when it can supply QP-4's reference classes |
| **3** | Does the deterministic macro layer live in **D-02 (neutral ground)**? | ✅ **DECIDED 2026-08-20 — YES.** Otherwise SEAT-3 can never consume it without breaching INV-014 |
| **4** | Accept **§3.5a** — a factual macro **digest**, explicitly no macro **outlook**? | ⚠ **OPEN — recommend yes.** The disagreement is one sentence long and that sentence carries all the risk |
| **5** | ★ Treat **hyperscaler capex guidance as the primary "macro" variable** for this book? | ✅ **DECIDED 2026-08-20 — YES.** It changes the build order: company disclosure, so it needs §1's calendar and **E-02**, not a macro stack |
| **6** | Build **M-F**, the persistent sector file (§3.6)? | ⚠ **OPEN — recommend yes**, highest-value item in §3 after M-B. Evidence only; the moment it grows an "outlook" field, stop |
| **7** | Is **F6** a capability spanning D-07/D-02/D-01, or a thirteenth domain? | ✅ **SETTLED by decision 3** — a capability. A D-13 whose deterministic half must live in D-02 anyway is a boundary drawn around nothing |
| **8** | Pre-event briefs on the 13-name watchlist, or only names with a live thesis? | ✅ **Live thesis only** — now spec **RA-76** |
| **9** | Is the daily/weekly split of §2.5 right? | ✅ **Split** — now spec **§10B.4, RA-85…RA-87** |
| **10** | Fold §1 and §2 into `L1-fundamental-analysis.md`? | ✅ **DONE 2026-08-20** — spec v0.8.0, §10A/§10B, RA-69…RA-87, AC-1.41…AC-1.55 |

## 3.12 What folding §3 in will require — the shape of the next change

Decisions 1, 3 and 5 are taken; the work they imply is **not** a prompt. Tracked as spec **QR-11**:

| Change | Where |
|---|---|
| `assumptions[]` becomes objects with `class ∈ {company, macro, policy}`, an `observable`, a threshold and a state | **D-01** — a `CT-1.1` contract change |
| Assumption ↔ release comparison, deterministic, with the arithmetic trail | ★ **D-02** — a new surface on neutral ground, so SEAT-3 may consume it |
| The fixed, versioned macro observable set (§3.5b) — ★ led by **hyperscaler capex guidance**, which is **E-02 extraction on a calendar (§1)**, not a macro feed | **D-07** + **D-01** |
| Assumption-state enum (`holding \| drifting \| contradicted \| not_yet_testable`) + one sentence on what a contradiction does | **D-01** — one new enum on V-01, no new prompt |
| A contradicted assumption emits an `InvalidationEvent`, never a verdict change | **D-01** — RA-41 unchanged |
| Macro is absent from the Stage-A bundle, by the same mechanism as price | **D-01** — `view:blind` (§3.8, MP-3) |

★ **Note what is not on that list: anything that forms a macro view.** The largest piece of work is a
D-02 comparison surface, and the D-01 half is one enum. That asymmetry is the decision working.

---

## 3.13 ★ INDEPENDENT REVIEW — adopted, corrected, and one target substituted

> An external agent reviewed §3 against the literature. **The review is strong and most of it is
> adopted.** This subsection records what was taken, what was corrected, and where the ranking
> changed — because a review absorbed without a record is indistinguishable from one that was
> ignored.

### 3.13.1 Adopted — the organising frame

★ **The Q1/Q2/Q3 triage is better than §3.3's reframe and supersedes it as the top-level device.**
§3.3 was a Q3 argument that did not know Q2 existed:

| | Question | Epistemics | Answerable? |
|---|---|---|---|
| **Q1 FORECAST** | *what will the macro variable do?* | needs an edge over consensus | ✗ — and §3.1 now shows a **perfect** edge would not pay |
| **Q2 EXPOSURE** | *given what I hold, what am I exposed to?* | ★ **no forecast at all** — a measurement of the book | ✅ today |
| **Q3 ATTRIBUTION** | *it already happened; what did it happen to, and does it contradict something I wrote down?* | backward-looking, deterministic, dated | ✅ today |

★ **Q1 is a forecasting problem, Q2 is an accounting problem, Q3 is a lookup problem.** The forecast
gate is a **gate, not a weight** — the same structural device D-12 landed on, for the same reason: a
forecast-dependent target cannot be rescued by being valuable, because the whole chain inherits an
input we cannot produce.

Also adopted, verbatim in intent:

| Item | Where it landed |
|---|---|
| **The perfect-foresight evidence** replacing *"we have no edge"* | §3.1 above — verified, and the **2024 paper is tighter than the review's figure**: 0.16 %/month before costs, 15 cycles to 2022 |
| ★ **The vintage rule** — compare against the print that existed on the date | ✅ **now spec RA-93**, with the consequence the review did not state (§3.13.3) |
| ★ **The completeness rule** on the sector file — *curation is where the view hides* | §3.13.4 — **the single best addition in the review** |
| **FX as a named decomposition term**, not row seven of a list | ✅ **now spec RA-90** |
| **False invalidation as SEAT-1 authority taken by accident** | ✅ **now spec RA-91** — a sharper *why* than the note had |
| **Guidance revisions matter more than levels** | folded into §3.5b's capex row |
| **"Priced ≠ predictable"** (Chen–Roll–Ross is a Q2 result, not a Q1 one) | §3.13.1, above |
| **"This is the assumptions tab, made machine-checkable"** | ★ a useful deflation — *"we automated the assumptions tab"* is a far safer claim than *"we invented a macro methodology"* |
| **The digest template has no free-text field at the end** | ✅ decision 4, §3.11 — the sentence that carries the risk now has nowhere to go |
| **The rejected contrary claim** (LLM sector allocation, Sharpe 2.51) recorded rather than omitted | §3.13.5 |

### 3.13.2 ⚠ Correction 1 — attribution was not absent

The review lists return attribution as *"Status in draft: absent"* and calls it the highest-value
missing item. **It is not missing.** §2.2–§2.3 of this note carry the decomposition, and it was
folded into `L1-fundamental-analysis.md` **§10B.2 as RA-78…RA-81 with AC-1.49/AC-1.50** before the
review ran. The review appears to have read §3 and not §2.

★ **This matters beyond bookkeeping**, because the review's two genuine additions on top of it would
have been lost inside a "you are missing this" framing:

1. ★★ **The residual must be computed BEFORE the trigger fires** — the note routed to the residual
   *after* detection, which leaves a raw-return trigger measuring the sector. **Now RA-88.**
2. ★★ **The false-invalidation consequence** — a sector-wide repricing read as company evidence is
   an *allocation* decision, i.e. SEAT-1's authority exercised without the seat. **Now RA-91.**

### 3.13.3 ⚠ Corrections 2–4 — three numbers that do not survive checking

| # | Claim | Correction |
|---|---|---|
| **2** | *"a shared macro error is `n×` — 13× — as damaging"* | ★ **`n` is the ceiling, not the estimate.** The ratio is `n/(1+(n−1)ρ)`; per-name analytical errors across 13 names in one theme, one analyst, one rubric set are **not** independent. At ρ ≈ 0.6 it is ≈ 1.6×. **§3.1 above now carries the corrected form — and notes it cuts the other way**: a low multiplier means the error budget was already undiversified |
| **3** | *"market + sector explain 40–60 % of variance, so the false-positive rate is near 50 % by construction"* | ⚠ **An R² in variance does not convert into a false-positive rate for a threshold trigger.** Conditional on a *large* move, idiosyncratic causes (earnings, guidance, 8-K) are over-represented relative to their unconditional variance share — so for a `>3σ` trigger the rate is materially **below** 50 %. ★ **But the conclusion survives in a better form**: the rate is near **100 % on precisely the days that matter**, because a sector-wide move trips *every* name at once. **The diagnostic is the CLUSTERING, not the rate** — and clustering is free to detect and needs no factor model. **Now RA-89** |
| **4** | *"52 assumption-observations per cycle ⇒ ~86 pairs ⇒ 2–4 years to calibrate"* | ⚠ **The power calculation treats clustered data as independent.** Four assumptions from one thesis share the thesis, the company, the analyst and the rubric. With a design effect `1+(m−1)·ICC` at m=4, ICC≈0.3, 52 observations behave like ≈27 — **roughly 4–8 years, not 2–4.** The effect size (60 % vs 30 %) is also assumed, not measured; at 45 % vs 35 % the requirement rises ~5×. ★ **The directional claim still stands and is still the argument for building it first**: assumptions multiply the observation count relative to verdicts by ≈2×, not ≈4× |

> ★ **None of the three corrections reverses a recommendation.** They change magnitudes, and in this
> project a magnitude stated without its correction is how `_cumulative_fys` shipped with a
> confident docstring and a 41.5 % error. The review's judgement was right in every case; three of
> its numbers were not.

★ **The vintage rule needs a consequence the review did not state.** *"Compare against the print
that existed on the date"* is correct and mostly **unimplementable with current sources** — FRED's
ALFRED publishes vintages, FMP's `economic-indicators` does not. A rule with no available data
silently becomes an aspiration. **RA-93 therefore names what happens when no vintage exists: the
comparison is reported `revised_series` and is UNCHECKED-grade, never silently used** — the DE-35
pattern applied to macro.

### 3.13.4 ★ The completeness rule — adopted and extended

> *"Selection of evidence is itself a conclusion. A file that accumulates the capacity announcements
> someone found interesting has a view, with no 'outlook' field anywhere in it."*

**This is the best line in the review**, and it repairs a real hole: §3.6's *"evidence, not
conclusions"* guard was necessary and not sufficient. The sector file must ingest **all** items from
a defined, versioned source list, with omissions logged.

★ **Extended: ranking is also a conclusion.** A completeness rule stops the view hiding in the
*sampling*; it does not stop it hiding in the *ordering*. **The sector file sorts by date and by
nothing else** — a file sorted by importance has an author's view in the sort key, and the reader
will read the top of it.

### 3.13.5 The strongest published claim against this position, recorded

There is recent work reporting LLM-driven top-down sector allocation at **8.79 % return, Sharpe
2.51**, against −1.39 % / −0.61 for cross-momentum over the same window.

**Recorded and not acted on.** A Sharpe of 2.51 from a top-down allocation overlay sits far outside
anything the sector-rotation literature supports (§3.1), the benchmark is chosen, and the window is
short. ★ It belongs here so the rejection is **a judgement on the record rather than an omission** —
and so that a future reader with a stronger version of this result knows exactly which argument it
has to defeat.

### 3.13.6 ★ Disagreement — one target substituted

The review's top five: capex · assumption ledger · return attribution · sector file · **real yield
as valuation input**. I agree with four and replace the fifth.

**Demote — real yield as a discount-rate input.** The review's own defence undoes it: *"it needs no
base rate, no calibration and no falsifier, because it isn't a claim about the world — it's a model
input."* ★ **That is an argument that it is not a research target at all — it is plumbing**, it is
D-02's, `L1-data-engine.md` §5A.5 already ranks `treasury-rates` priority #2 for exactly this, and
it requires **no D-01 behaviour whatsoever**. ⚠ It also sits behind a live defect: **D-19 — the DCF
returns an enterprise value per share.** Refining the denominator while the numerator is wrong buys
precision in the wrong place.

**Promote — fundamental attribution (industry vs idiosyncratic on the accounts).** ✅ **Now spec
§10B.5, RA-92…RA-94.** The reasons:

- ★ **The stated purpose is fundamental, and the review's list is return-centric.** The ask was to
  *"explain the fundamentals, the health of companies, justify the business prospect, **or** explain
  the price trend."* Four of those five are fundamental; the review's five contain one price-
  attribution target and no fundamental one. **The finance literature is about returns, so a
  literature-led review drifts toward returns.**
- ★★ **The unguarded error is larger than the guarded one.** A false invalidation costs one
  position. A scorecard that cannot separate the cycle from the company is **wrong on every cyclical
  name, in the same direction, for as long as the cycle lasts** — and reports 5/5 stability while
  doing it, because a consistent bias survives every consistency check (§7.5).
- **It is the only target that improves an existing rubric's discriminating power** (RA-34, RM-7),
  rather than adding a new surface beside it.
- **Cost is moderate, not high.** D-02 already publishes `peer_context` at the level; what is
  missing is the decomposition of a *change*.

**The revised five:**

| # | Target | Class | Cost | Status |
|---|---|---|---|---|
| **1** | Demand-chain visibility — hyperscaler capex guidance | Q2/Q3 | ~0 | ✅ decided |
| **2** | The assumption ledger | Q3 | ~0 | ✅ decided |
| **3** | Return attribution + false-invalidation defence | Q3 | low | ✅ **spec §10B, RA-78…RA-91** |
| **4** | ★ **Fundamental attribution — cycle vs company on the accounts** | Q3 | moderate | ✅ **spec §10B.5, RA-92…RA-94** |
| **5** | The persistent sector evidence file (M-F) | Q3 | ★ **the only running cost** | ⚠ open — recommend yes, with §3.13.4 |

> ★ **The shape argument survives the substitution and is the best structural observation in the
> review: four of five targets put the work in D-02 and leave D-01 with a judgement it can be held
> to. If a future proposal reverses that ratio, that is M-E returning under another name.**

---

## 3.14 ★ ROUND 2 — the review of the review

> The reviewer conceded five of six and returned four improvements, three of which correct **my**
> corrections. Recorded in the same spirit: a rebuttal absorbed without a record is indistinguishable
> from one that was ignored.

### 3.14.1 ⚠ Three of mine corrected back

| # | My claim | Correction |
|---|---|---|
| **a** | *"at 45 %/35 % the requirement rises ~5×"* | ⚠ **~8.7×.** `n = 7.84·2·p̄(1−p̄)/(p₁−p₂)²` gives **376 per group** at 45/35 against **43** at 60/30. **The effect-size sensitivity is more of the story than the clustering correction is** — and I under-stated it while correcting someone else's arithmetic |
| **b** | *"at ρ ≈ 0.6 the multiplier is ≈ 1.6×"* | ⚠ **`ρ = 0.6` is exactly as assumed as their `ρ = 0`.** The multiplier is bounded `[1, 13]` and we each picked a point on it and reported it as a finding. ★ **By this project's own standard it is declared-assumed and measured** — as the correlation of realised thesis errors across names, once outcomes accrue. **Now spec RM-16**, an RM-9 extension rather than new machinery |
| **c** | *"no vintage available — FMP's `economic-indicators` does not supply one"* | ⚠ **Wrong scope.** [ALFRED](https://fred.stlouisfed.org/docs/api/fred/alfred.html) publishes as-first-released values via `realtime_start`/`realtime_end` for CPI, PCE, industrial production and treasuries, free, over the FRED API. **FMP is the vendor that cannot, not the world**, and recording it as unavailable would have permanently downgraded a free check. **RA-93 rewritten**; ★ **RA-93a narrows it further** — capex guidance is company disclosure whose vintage is its filing date (DE-18), and treasury rates are not revised, so ALFRED gates only CPI/PCE/IP and **must not gate the capex work** |

> ★ **The meta-finding is worth more than any of the three.** The reviewer noted that **three of its
> four original errors were the same error**: ② and ④ treated correlated observations as
> independent, ③ combined incommensurable quantities. Those are the two failure modes this project
> has already recorded as patterns to watch — and they were made **in a document that cites the rules
> forbidding them.** Mine (a) is a third instance of under-checked arithmetic in the same exchange.
> **The lesson is not "check harder"; it is that a stated number needs its check attached, which is
> what `RA-93`, `RM-16` and the whole `not_yet_calibrated` convention exist to force.**

### 3.14.2 ★★ My contribution: shared error CANCELS for rank, it is not merely neutral

The reviewer argued correctly that a shared analytical error `c` differences out of a within-set
ranking, so L2's re-ranking case is untouched. **It is better than untouched.** Writing
`f_i = μ_i + c + u_i` with `Var(c) = ρσ²`, `Var(u) = (1−ρ)σ²`:

| Decision | Error | Consequence |
|---|---|---|
| **LEVEL** — *"is this a BUY?"* | `c + u_i`, variance `σ²` | effective breadth `n/(1+(n−1)ρ)` — **13 → 1.6** |
| **RANK** — *"is i better than j?"* | `u_i − u_j`, variance `2(1−ρ)σ²` | ★ **smaller than the `2σ²` independent errors of the same size would give** |

★ **So `ρ` is dangerous exactly where D-01 acts as a GATE, and helpful where L2 re-ranks** (CB-19,
`k_cov ≥ 2`). The coverage uplift is **strengthened**, not merely spared. **Third appearance of the
same structure** — `L1-quantitative-analysis.md` **QA-93** found that a within-date sort cancels the
market factor a pooled statistic drowns in (`t = +0.13` pooled vs `t = −3.08` sorted, identical
data). ⚠ Exact for equicorrelated errors only; sub-clusters leave common structure inside each.
**Now in spec §7.2 beside RM-16.**

### 3.14.3 The clustering blind spot — accepted, and it closes with existing machinery

> *"Simultaneous clustering catches a sector that drops 5 % in a day. It misses a sector drifting
> 1 %/day for two weeks."*

Correct, and RA-89 must not be allowed to displace RA-88. ★ **But the slow form is already
specified**: it is exactly what **RA-85's weekly accumulation sweep** exists for — *"the drip of
small residuals none of which breaches the daily threshold."* So this is **three layers, not a gap**:

```text
   fast common-factor event   → RA-89 clustering        free, partial
   slow common-factor drift   → RA-85 weekly sweep      already specified
   either, correctly          → RA-88 decomposition     ★ the only complete one
```

### 3.14.4 The peer set has the same vintage problem — accepted, and it is worse here

Accepted verbatim: companies report across a ~6-week window, so the peer median on a thesis date is
**partially reported**, and the comparison must declare which peers had reported (**RA-96**).

★ **One addition the reviewer did not reach: the incompleteness is not random, it is a fiscal
offset.** **MU's fiscal year ends in late August while its peers run calendar quarters** — a
date-aligned median compares MU's Jun–Aug quarter against peers' Apr–Jun. **MU is on the practice
watchlist**, so this bites on a live name, and it bites on cyclicals at exactly the moment the
comparison matters. **RA-96a: peer comparison is period-aligned, never date-aligned.**

### 3.14.5 The merge — accepted, with the caveat that stops it going wrong

The two decompositions are one capability: subtract the common component, keep the residual, same
D-02 surface, same neutral-ground argument, same vintage rules. **Accepted — targets go five → four.**

⚠ **But they are one capability and TWO estimators, and the spec has to say so.**

```text
   return:       r_i       = β_m·r_mkt + β_s·r_sec + β_fx·r_fx + ε    ← β FITTED,
                                                                        100s of daily obs
   fundamental:  Δmargin_i = Δmargin_peer_median             + ε    ← β ≡ 1 BY CHOICE,
                                                                        ~5 annual obs
```

★ **Specified as "one operation" without that clause, it is an invitation to regress on five data
points.** The unit-sensitivity difference is not a simplification of the regression — it is the
correct estimator when the sample cannot support a fitted one. **Now RA-95.**

### 3.14.6 ✅ The final four targets

| # | Target | Class | Cost | Status |
|---|---|---|---|---|
| **1** | Demand-chain visibility — hyperscaler capex guidance | Q2/Q3 | ~0 | ✅ decided; ★ needs no vintage service (RA-93a) |
| **2** | The assumption ledger | Q3 | ~0 | ✅ decided — spec **QR-11** |
| **3** | ★ **The merged decomposition** — returns *and* accounts, one surface, two estimators | Q3 | low–moderate | ✅ spec **§10B, §10B.5, RA-78…RA-96a** |
| **4** | The sector evidence file | Q3 | ★ **the only running cost** | ✅ **spec §10C, RA-97…RA-102** |

★ **The peer-set definition is now a design requirement on Target 3 rather than a target of its own**
— which is where a view hides in a decomposition, exactly as curation is where it hides in a file.

### 3.14.7 The fourth guard — schema

Adopted directly, and it is the best of the three additions to the sector file:

> *"A file whose fields evolve encodes a view in what it decided was worth a column, and that one is
> harder to see than either curation or ordering because schema changes look like engineering."*

**Now RA-100**, versioned and immutable within a version exactly like a rubric (RA-33). The four
channels — prose, sampling, ordering, schema — are §10C's opening box, ordered by how hard each is
to see.

---

# 4. WHAT THIS NOTE DOES NOT SETTLE

- **Prompt text for §1 and §2.** Once the rules are accepted, they add roughly five blocks to the
  master prompt registry: a pre-event brief, an assumption-state check, an unexplained-move triage,
  a weekly-accumulation sweep, and a sector-file update. **§3 deliberately adds none** — its output
  is a comparison, not a narrative.
- **`RA-` numbering.** `RA-69`…`RA-87` are used here provisionally and collide with nothing today.
  They are not claimed until the L1 spec adopts them.
- **The cost.** §1 and §2 are near-free (deterministic routing, cheap-tier triage on escalation
  only). §3's M-B is near-free. **M-F's sector file is the only piece with a real running cost**, and
  it wants an estimate before it is committed to.
- **D-05's overlap.** D-07 already routes the earnings calendar to **D-05 (event risk)**. Whether
  D-05's event-risk use and D-01's pre-event brief share one calendar consumer or two is a seam
  question this note does not answer.
