# L1: Domain Specification — Reporting (D-09)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-09 · **Seat:** SEAT-5
> **Path:** `src/reporting/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Consumes:** D-01 · D-02 · D-03/D-04 · D-05/D-06 · **D-11** — and writes to none of them
> **Prior art:** `pipeline/report/**` (2,112 LOC, **F1**), `pipeline/delivery/**` (**F2**),
> `pipeline/api/**`, `pipeline/buffett/report/**`
> **Governing rules inherited:** L0 §5.1a **DC-1…DC-5** · `L1-fundamental-analysis.md` **RA-20…RA-29** ·
> constitution **P3, P5, P6**, INV-6, INV-010

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.3.0 | 2026-08-27 | Victor | ★★★ **RP-50…52 — delivery is wired, and the defect it fixes is a job that reported SUCCESS for doing nothing.** ⚠ *Measured:* `deliver` returned in **0.000278 s** having never called `send()`; `artifacts: []`. ★ Sending is outward-facing so it stays behind an explicit **`--deliver`**; the recipient comes from **`REPORT_RECIPIENT`** and a missing one raises rather than defaulting to the SMTP user; the card is delivered **every trading day, actionable or not** (Victor, 2026-08-27). AC-9.32…9.34. |
| 0.7.0 | 2026-08-25 | Victor | ⚠ **B4.8 readiness — two D-01 ACs assigned work to D-09 that this spec never received.** ★★ D-01 **RA-116** states *"RP-1's reliability classes gain a fourth"* and **RP-1 still listed three**, while **AC-1.79** requires `relayed_judgement` to render *in every medium* — the producing domain declared the class and the rendering domain was never told. RP-1 amended; **RP-48** states the direction (*more* provisional, never a footnote on `judgement`). ★ **AC-1.82** requires a `RELAY QUEUE` block with **separate** `overdue` and `stale` counts and **no block existed** — **RP-49** adds it, carrying RA-127's *reports, does not chase*. AC-9.30/9.31 added. |
| 0.6.0 | 2026-08-23 | Victor | ★ **New RP-47 — an absent risk pass renders as absent.** D-12's new `alerts_status` (**DN-38**) reaches the card: an empty `alerts[]` with `UNCHECKED: <why>` prints as itself and never as a clean bill of health. RP-45 covered `INCOMPLETE`/`BLOCKED_PRECONDITION`/`NO_THESIS` and **missed the risk channel**, where silence is the domain's whole signal (RK-30). |
| 0.5.0 | 2026-08-18 | Victor | §8Z's thesis row pointed at `CT-1.1` *"via the gate"* — but **no contract carried the narrative**, and RP-43 as written forbade D-09 reading anything but `CT-12.1`. Resolved by **DN-33**'s `thesis_ref` plus **RP-43a**: D-09 may **resolve a reference**, and may not **re-derive a computation**. The analyst's own verdict is now rendered beside the composed one. |
| 0.4.0 | 2026-08-18 | Victor | §8Z cited `grade.stability_fraction` for RA-20 — but **a ratio cannot render *"BUY 3 / HOLD 2"***. Corrected to `{k, verdict_distribution}`, and `confidence` added for **RA-21**'s empirical-referent rule. Upstream contracts fixed in the same pass (D-01 CT-1.4, D-12 CT-12.1 / DN-32). |
| 0.3.0 | 2026-08-18 | Victor | ⚠ **Audit: D-12 was invisible to this spec** — it renders `CT-12.1 Recommendation` and never named the source. **New §8Z** maps every card element to its `CT-12.1` field with its reliability class, and adds **RP-43…RP-46**: render, never re-derive; the transported `grade` is how RA-20's stability reaches the human; incomplete runs render as themselves; alerts may never be suppressed. Parent bumped to L0 v0.18.0. |
| 0.2.0 | 2026-08-18 | Victor | ★ **The report attachment is HTML** (Victor). §9 rewritten as **one artifact, several renderings** — email body (notification, RP-35), **HTML attachment (the artifact of record)**, markdown (retained as the diffable/permanent form, RP-33), online surface. **RP-31: fully self-contained, no network fetch** — that is P6, not aesthetics. **RP-32: renderings may differ in presentation, never in content.** **RP-34: no script.** **QP-1 mostly dissolves** — the hard half was *email-client* HTML; a browser-rendered attachment has none of those limits, so RP-1 is satisfiable where the artifact lives. Cosmetics deferred to post-E2E, with one surviving constraint: **class is never signalled by colour alone**. AC-9.24a–d added. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft. §5 is the substance: **a card carries three different reliability classes on one screen**, and rendering is lossy by nature — D-09's rules exist to stop the flattening. §7 operationalises **D-15**. §8 is where `L1-fundamental-analysis.md` §7.3's anti-overconfidence obligations actually land. Closes **QQ-5**'s D-09 half. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"Put it on one screen without making it look more certain than it is."**

D-09 is **the only place in this system where a machine's output becomes a human decision.**
Everything upstream is measured, gated and reconciled. Here it is *read* — and a reader applies
heuristics that none of the upstream guarantees survive.

```text
╔══════════════════════════════════════════════════════════════════╗
║  RENDERING IS LOSSY BY CONSTRUCTION.                             ║
║                                                                  ║
║  It takes a reconciled fact, a measured computation and a        ║
║  stochastic judgement, and prints them in the same font, on the  ║
║  same screen, to the same number of decimal places.              ║
║                                                                  ║
║  Every rule in this spec exists to stop that flattening. D-09    ║
║  is not a formatting concern; it is the last safety boundary     ║
║  before capital moves.                                           ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.2 Position

```text
                    ┌──────────────────────────────────┐
                    │  SEAT 1 — PM & Trader (human)    │  reads · decides
                    └───────────────▲──────────────────┘
                                    │  brief · slate · card · email · phone
                    ┌───────────────┴──────────────────┐
                    │  D-09 REPORTING       SEAT-5     │  ← this spec
                    │  render · deliver · serve        │
                    │  ★ LEVEL 1 RECOMMEND             │
                    │  ★ Report Writer Agent lives here│
                    └──▲────▲────▲────▲────▲───────────┘
                       │    │    │    │    │
                    D-01  D-02  D-03 D-05  D-11
                  thesis  fair  rank  risk  BOOK
                 JUDGE-  COMPU-  ...  ...   FACT
                  MENT   TATION
                       ── all one-way. D-09 writes to nothing. ──
```

## 1.3 Boundary

```text
╔══════════════════════════════════════════════════════════════════╗
║  D-09 RENDERS WHAT IT IS GIVEN. IT ORIGINATES NOTHING.           ║
║                                                                  ║
║  It may:  lay out · soften a verdict · label · warn · refuse     ║
║           to render · archive · deliver.                         ║
║                                                                  ║
║  It may NOT:  originate a verdict, a stop, a target, a fair      ║
║           value, a risk number or a position size (DC-1);        ║
║           make any of them MORE aggressive (DC-5, P3);           ║
║           compute anything a producing domain exposes;           ║
║           write to the record (ST-9).                            ║
║                                                                  ║
║  The last one is structural: a renderer that can mutate the      ║
║  book can rewrite history to match what it printed.              ║
╚══════════════════════════════════════════════════════════════════╝
```

**Authority: LEVEL 1 RECOMMEND** — *everything* it emits is read as advice, however mechanical the
rendering felt from inside (L0 §3.1).

---

# 2. DOMAIN ENTITIES

| Entity | Grain | Key | Note |
|---|---|---|---|
| **DisciplineCard** | ticker × as_of | `(ticker, as_of)` | the one-screen pre-commitment contract (L0 §5.1a) |
| **Slate** | run | `run_id` | the ranked watchlist; **exactly one actionable pick** (INV-6) |
| **Brief** | run | `run_id` | the daily assembly of card + slate + context |
| **RenderUnit** | one field on one artifact | `(artifact_id, field)` | ★ carries its **reliability class** and **as_of** — §5 |
| **Delivery** | one send | `delivery_id` | email, file, or online surface |
| **Archive** | one delivered artifact | `artifact_id` | self-contained, readable later without a server (P6) |

---

# 3. DOMAIN DEPENDENCIES

```text
DEPENDS ON (read-only, all of them)
  ├── D-01  thesis, verdict, conviction, falsifier, claims, VERDICT STABILITY
  ├── D-02  fair value + the arithmetic trail (its §6.2)
  ├── D-03/D-04  rank_score, slate, coverage, arbitration outcome
  ├── D-05/D-06  risk flags, exposure, sizing arithmetic
  └── D-11  ★ the BOOK — positions, cash, P&L, capital base

DEPENDED ON BY
  └── nothing. D-09 is a leaf. Its consumer is a human.

DOES NOT
  ✗ write to D-11 (ST-9) — one-way, and structurally so
  ✗ compute anything a producing domain exposes (DC-1)
  ✗ call the LLM gateway — ★ it RENDERS LLM text it did not author (ST-5, DC-1)
```

> **D-09 has an agent but no gateway.** The Report Writer Agent assembles and delivers; the language
> it renders was authored in D-01. **A prompt in `src/reporting/` is a boundary violation**, and it
> is grep-checkable.

---

# 4. MODULE DECOMPOSITION

```text
src/reporting/
├── render/
│   ├── card.py         #   the Discipline Card — §6
│   ├── slate.py        #   ranked watchlist, one actionable pick
│   ├── brief.py        #   daily assembly
│   ├── classes.py      # ★ reliability-class tagging + presentation — §5
│   └── lint.py         # ★ forecast-voice + length + uncited-claim checks — §8
├── deliver/
│   ├── email.py        #   notification body + attachments (RP-35)
│   ├── html.py         # ★ self-contained HTML rendering — no network, no script
│   ├── markdown.py     #   plain-text rendering — diffable, permanent (RP-33)
│   └── archive.py      #   byte-identical to what was delivered
├── online_api/         #   local + phone read surface
└── contracts/          #   card / slate / brief schemas
```

---

# 5. THE RENDERING CONTRACT — three reliability classes on one screen

**This is the spec's centre.** A Discipline Card shows, simultaneously:

| Class | Example field | Source | How it can be wrong |
|---|---|---|---|
| **FACT** | position size, cost basis, cash | **D-11**, reconciled against the broker | a reconciliation break — **loud, and rare** |
| **COMPUTATION** | fair value, `rank_score`, margin of safety, stop | D-02 / D-03 / D-04 / D-06 | a formula defect, or measured-and-stated skill — **D-19 and D-16 are live examples** |
| **JUDGEMENT** | thesis, conviction, bear case, falsifier | **D-01**, an LLM | stochastic; *"stable 4/5 runs"* is the honest description |

```text
╔══════════════════════════════════════════════════════════════════╗
║  THESE THREE ARRIVE ON THE SAME SCREEN, IN THE SAME FONT, WITH   ║
║  THE SAME NUMBER OF DECIMAL PLACES.                              ║
║                                                                  ║
║  "Position: 220 sh @ $91.40"      is a RECONCILED FACT.          ║
║  "Fair value: $412.80"            is a COMPUTATION — and its     ║
║                                     DCF has a live open defect.  ║
║  "Conviction: Medium-High"        is one draw from a stochastic  ║
║                                     process.                     ║
║                                                                  ║
║  A reader who cannot tell them apart will size the position off  ║
║  the least reliable one, because it is the one written in prose. ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **RP-1** | ★ **Every rendered value carries a reliability class** — `fact` \| `computation` \| `judgement` \| ★ `relayed_judgement` — and the class is **visually distinguishable** in every medium the artifact is delivered in. This is `L1-fundamental-analysis.md` **RA-22** generalised from two classes to three, ⚠ *and to four on 2026-08-25*: **D-01's RA-116 said "RP-1's reliability classes gain a fourth" and RP-1 never gained it**, while D-01 **AC-1.79** requires a relay report to render with `provenance_class=relayed_judgement` **in every medium**. A reader must never have to remember which reports came from a chat window |
| **RP-48** | ★★ **`relayed_judgement` renders as MORE provisional than `judgement`, never as a footnote on it.** ⚠ *Added 2026-08-25 building B4.8.* A relay report is a judgement whose **bundle does not exist** (D-01 §4B.2: RA-1/RA-2 do not survive a chat paste) and whose numbers are mostly **unverifiable against data we hold** (RA-118). ★ It is already capped at HOLD or `INSUFFICIENT_DATA` by RA-114's floors and **can never be the actionable pick** (RA-115) — the rendering must not undo in presentation what those two rules established in substance |
| **RP-49** | ★ **The daily report carries a `RELAY QUEUE` block with `queued` · `returned` · `overdue` · `stale` as SEPARATE counts** (D-01 **RA-128**, AC-1.82). ⚠ *not yet run* and *no longer trusted* are different states, and **collapsing them hides the moment one became the other**. ★ The block reports and does not chase (RA-127): no nagging, no escalation, no re-prioritising a name because it was skipped — **skipping is a decision SEAT-1 is entitled to make**, and D-09's obligation is the override obligation, *make it visible and let it stand* |
| **RP-50** | ★★ **Delivery is WIRED, and it is OFF unless asked for.** ⚠ *Measured 2026-08-27:* the `deliver` job reported **`SUCCESS` in 0.000278 s having sent nothing** — its adapter returned the renderings and never called `send()`. ★★ **That is worse than a failure**: the outcome record actively asserted the artifact reached the human when it had not, and **P6 is the constitutional claim it was falsifying.** ★ Sending is outward-facing, so it is enabled by an explicit `--deliver`; the default sends nothing and **says so**, rather than looking like it sent |
| **RP-51** | ★ **The recipient is read from the environment (`REPORT_RECIPIENT`), never hardcoded, and a missing one RAISES when delivery is requested.** ⚠ A default recipient is the failure mode that matters here — mail to the wrong address is not recoverable, and a silent fallback to the SMTP user would deliver to whoever holds the sending account |
| **RP-53** | ★★ **While the thesis gate is the placeholder, the verdict row says NO VERDICT** — *"no verdict — ranked #1 by the rule; no thesis"* — never the nominated `BUY`. ⚠ *Added 2026-10-06 (Victor, L9 §10 C1):* D-12 nominates `BUY` for every rank-1 name and the placeholder gate always PASSes, so the card read **"Verdict: BUY"** with no analysis behind it. The composed verdict is unchanged in `recommendation.json`; the CARD states what it rests on. The placeholder's wording names today's cause (theses on demand, DX-153), never a milestone already passed |
| **RP-54** | ★ **The card names what ranked the pick** — the D-03 rule (by formula id) or a promoted D-04 model (by artifact id), as carried on `CT-12.1` (DN-40). ⚠ *Added 2026-10-06 (Victor, L9 §10 C4):* the identity sat only in `recommendation.json` (PG-10 transparency) |
| **RP-55** | ★★ **A card ranked by a refused model SAYS so, in the ranking line and the verdict line**: *"a REFUSED model … (failed: ic_significance, breadth) — informational, not promoted"* and *"no verdict — ranked #1 by a refused model; no thesis"*. ★ Victor, 2026-10-09: card option (b); PG-10 |
| **RP-57** | ★ **The behavioural flags render in the Risk block under their own label — *from trade history through `<history_through>`, not part of the exposure pass* — beside the risk status, never merged into it.** One line per kind with its count (and the short-hold trailing frequency), then every flag in D-05's `recent` list in full; the rest are counted, not listed (Victor 2026-10-21). An `UNCHECKED` pass renders as itself with its reason and no counts. D-09 selects nothing: the counts and the list are D-05's (RP-43). *Added 2026-10-21 (L9 §6.5 ⓐ, RK-40)* |
| **RP-56** | ★ **A `NO_THESIS` gate renders as the absence it is**: *"no verdict — ranked #1 by … ; no thesis — no peer set"* (or *"— not yet written"*), with the reason in the falsifier block and the data gaps — never the composed HOLD shown as a judgement. With a thesis, its own verdict renders beside the composed one (RP-8) with its falsifiers, and a `thesis_for` thesis is sourced as *authored over the full evidence bundle through the subscription transport (k=1)* — not as a relayed one. *Added 2026-10-21 (F13 `D13`, Victor)* |
| **RP-52** | ★ **The card is delivered on every trading day it is produced, actionable or not.** ⚠ A `NOT ACTIONABLE` day is **information** — RP-35's body states the verdict and the reason — and delivering only on action would make silence ambiguous between *nothing to do* and *the run did not happen*, which is exactly the ambiguity **DN-29**'s liveness monitor exists to remove |
| **RP-2** | ★ **Freshness is per component, never per card.** A card's `as_of` is not one clock: the thesis may be hours or days old (F1's refresh policy), the price is live, and the book is from the last export. **Each block states its own `as_of`**, and any component past its staleness threshold (L0 §8) is **marked stale on the face of the card**, not silently trusted |
| **RP-3** | A **computation** renders with a pointer to its arithmetic (D-02 §6.2 supplies the trail). A number the reader cannot trace is indistinguishable from a number the model invented |
| **RP-4** | A **judgement** renders with its **stability** (RA-20) and its **data gaps** (RA-25). A judgement rendered bare is the one class that reads most confidently and deserves it least |
| **RP-5** | ★ **A known open defect in a producing domain is disclosed on the artifact that uses it.** `F0` §12 **D-19** — the DCF returns an enterprise value per share — is live, so **every rendered fair value and margin of safety carries the caveat until it is closed.** Silence here converts a recorded defect into an apparently sound number |

> **RP-5 is uncomfortable and correct.** The alternative is a card that prints a fair value the
> project's own defect log says is overstated in proportion to leverage, with nothing on the page
> to say so. **ENB is on the practice watchlist and its net debt is 128 % of market cap.**

---

# 6. THE DISCIPLINE CARD

The one-screen pre-commitment contract: verdict, conviction, entry, **stop**, **target**, one-line
thesis, and the **falsification condition** (L0 §5.1a). It exists so a decision follows a written
plan rather than a feeling.

## 6.1 DC-1…DC-5, operationalised

| DC | Rule | How D-09 satisfies it |
|---|---|---|
| **DC-1** | Renders, never originates | Every card field maps to a producing domain's output. **A field with no producer is a contract violation** (RP-6) |
| **DC-2** | The card is RECOMMEND | It is the agent's output; its authority is the agent's |
| **DC-3** | **Fail loud** | §7 — three layers, all inherited from D-15 |
| **DC-4** | Both seats side by side, attributed, divergence visible | RP-8 |
| **DC-5** | May soften, never escalate | RP-7 — and this is already implemented (`discipline_card.py`) |

| ID | Rule |
|---|---|
| **RP-6** | **Every card field names its producing domain.** A field D-09 could compute itself is a field D-09 must not compute |
| **RP-7** | ★ **The verdict may be made equal or more conservative, never more aggressive** (DC-5, P3). Already live: `discipline_card.py` takes the more conservative of `quant_signal` and the thesis verdict along `BUY → HOLD → SELL`. **A name can top the slate as BUY and come back HOLD** — the thesis layer has veto authority, not scoring authority |
| **RP-8** | ★ **Divergence is rendered, never resolved in layout** (DC-4). When the quant rank and the thesis disagree, **both appear with attribution and the disagreement is stated in words.** A layout that quietly shows only the governing view manufactures a consensus that does not exist — and disagreement between two independent seats (INV-014) is *information*, not a presentation problem |

## 6.2 Who authors the stop and the target — QQ-5's D-09 half

> ✅ **Closed by DC-1: D-09 does not care.** It renders whatever the analysis layer produced and may
> not alter it.

Today D-01 authors them. `L1-quantitative-analysis.md` §9.3 recommends moving them to a **quantile
model**, which would make them *computations* rather than *judgements*.

**That changes the reliability class, not the contract.** Under RP-1 the card would render them as
`computation` with a coverage level instead of `judgement` with a stability count — **which is the
whole point of the change** (D-01 §7 argues LLM-authored stop/targets are the least reliable output
class in the system). **QA-27 / MT-38 already bind the other side: the LLM may narrate a
deterministic band and may not alter it.**

---

# 7. FAIL LOUD — the D-15 boundary

**L5 §3 D-15**: a failed LLM call returned a `Narrative` carrying `error` plus dataclass defaults —
`verdict="HOLD"`, **no stop, no targets** — and the writer persisted it to `{TICKER}_synthesis.json`
*and* `{TICKER}_report.md`, which rendered *"Verdict: **HOLD** | Conviction: **Medium**"* with no
indication the call had failed. It was cached and emailed as a genuine recommendation.

```text
╔══════════════════════════════════════════════════════════════════╗
║  NOTHING ABOUT THE ARTIFACT LOOKED WRONG.                        ║
║                                                                  ║
║  P5 was satisfied at the DECISION boundary — build_discipline_   ║
║  card raised — and violated at the ARTIFACT. A file on disk that ║
║  reads like analysis is itself a way for a failure to become a   ║
║  recommendation.                                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **RP-9** | **A degraded bundle is never persisted.** The last good artifact survives and the next run retries, rather than the failure being served for a full TTL |
| **RP-10** | **A degraded artifact renders a refusal, not a report** — a banner naming the failure, ahead of any content. It never renders a verdict, a stop or a target from defaults |
| **RP-11** | **A degraded cache is never built upon.** An UPDATE that would rest on a degraded bundle degrades to a full rebuild or fails |
| **RP-12** | ★ **A run degraded for coverage still delivers, and says so** (F1 AC-1.15, P6). Under-featured names stay ranked and **cannot be the actionable pick**; the slate carries `degraded`, the excluded list, and a banner. **If every curated name is excluded the build raises** rather than picking one anyway |

> **RP-9…RP-11 are three layers on one failure**, and that is deliberate — D-15 got through because
> there was only one. Already implemented; this spec pins them so they cannot be optimised away.

---

# 8. THE ANTI-OVERCONFIDENCE OBLIGATIONS

`L1-fundamental-analysis.md` §7.3 establishes that **the third failure mode of an LLM analyst is not in
the model — it is in the interface.** Those obligations are D-01's to satisfy in content and
**D-09's to satisfy in rendering.** They are restated here as the domain that actually executes them.

| ID | Rule | Source |
|---|---|---|
| **RP-13** | ★ **Verdict stability renders verbatim** — *"stable 5/5"* or *"⚠ unstable: BUY 3 / HOLD 2"*. Quantitative, honest, and impossible to skim past. **The single most effective anti-overconfidence device available** | RA-20 |
| **RP-14** | ★ **Confidence renders with an empirical referent, or as "not yet calibrated (N=…)"** — never a bare number. A confidence with nothing behind it is fabricated precision the reader cannot detect | RA-21 |
| **RP-15** | **The falsifier renders ABOVE the verdict.** What would prove this wrong, before what we think. Ordering is an argument | RA-23 |
| **RP-16** | **Fair value renders as a band, never a point.** The point estimate is an artifact of the arithmetic and reads as knowledge | RA-24 |
| **RP-17** | **The data-gap block is mandatory and non-collapsible.** What the analyst wanted and did not have is part of the finding | RA-25 |
| **RP-18** | ★ **Forecast-voice is linted out before render** — *"will"*, *"is set to"*, *"poised to"*, *"clearly"*, *"undoubtedly"*. Deterministic, cheap, and it removes the cheapest source of unearned certainty. **A violation blocks the render** | RA-26 |
| **RP-19** | **Narrative sections are length-capped.** Length is a free confidence signal; capping removes it and costs nothing analytical | RA-27 |
| **RP-20** | **Backtested returns are labelled as such and never presented as expected returns**, and the label travels with the number rather than sitting in a footnote | INV-010 |

---

# 9. DELIVERY — one artifact, several renderings

> **Changed 2026-08-18 (Victor): the report attachment is HTML.** Markdown is retained alongside it
> — see RP-33 for why. This is not a formatting preference; it changes what RP-1 can promise.

## 9.1 The model

```text
        Artifact  (content: class-tagged, freshness-tagged — CT-9.1/9.2)
             │
             ├── email body        HTML, EMAIL-CLIENT constrained
             ├── html attachment   ★ HTML, BROWSER rendered — the artifact of record
             ├── md attachment     plain text — diffable, greppable, permanent
             └── online surface    HTML, browser, read-only

        All four are RENDERINGS of one artifact. They may differ in
        PRESENTATION. They may never differ in CONTENT.
```

| ID | Rule |
|---|---|
| **RP-31** | ★ **The HTML attachment is fully self-contained.** No external stylesheet, no CDN font, no remote image, no network fetch of any kind — every asset inlined or a `data:` URI. **This is P6, not aesthetics**: an artifact that needs a live server to render is not viewable later, and "later" is exactly when a decision gets audited |
| **RP-32** | ★ **All renderings of one artifact are content-equivalent.** Presentation may differ per medium; **a value present in one rendering and absent in another is a defect**, as is a value that differs. Checked mechanically by extracting the class-tagged fields from each rendering and diffing |
| **RP-33** | **Markdown is retained as the plain-text rendering, not replaced.** HTML is what a human reads; markdown is what **diffs, greps, and survives** — two days' cards compare as text, and it is the format most likely to still open in ten years. Both are archived (RP-24) |
| **RP-34** | The HTML rendering carries **no script**. A self-contained report needs none, an emailed HTML file that executes is a needless risk surface, and script-free is what guarantees it still renders after the next browser generation |
| **RP-35** | **The email body is a notification, not the artifact.** It carries the slate inline and points at the attachment. Decision-relevant content that exists *only* in the email body is content trapped in the most constrained medium |

## 9.2 The rest of P6

| ID | Rule |
|---|---|
| **RP-21** | Every delivered artifact is readable later **without a live server** (P6) |
| **RP-22** | Delivery is **idempotent and recorded**. A re-send is identifiable as one; a silent duplicate is how a stale card gets acted on twice |
| **RP-23** | A delivery failure is **loud** (P5). An email that did not send is not a quiet log line |
| **RP-24** | **Archived bytes == delivered bytes**, per rendering. If they can differ, the archive is not evidence of what was seen |

# 10. THE ONLINE SURFACE

Local and phone access over a private network. **Read-only by construction.**

| ID | Rule |
|---|---|
| **RP-25** | The online surface is **read-only**. There is no endpoint that writes to the book, the journal, or any producing domain |
| **RP-26** | **Prompt-alignment drift returns an error to the viewer, not a stale page** (INV-9). The failure is surfaced to the phone with the diff — a blank or "pending" screen that hides a failure is the defect P5 exists to prevent |
| **RP-27** | The surface renders the **same artifact** the email delivered, not a re-derivation. Two renderings of one decision that can disagree is a defect with no upside |

---

---

# 8Z. ★ WHAT D-09 ACTUALLY RENDERS — the D-12 seam

> ⚠ **Added after a consistency audit.** This spec was written before **D-12 Decision** existed
> (L0 v0.17.0) and described rendering "the verdict" without naming its source. **The artifact D-09
> renders is `CT-12.1 Recommendation`**, and every field on the card traces to it.

| card element | source | reliability class (§5) |
|---|---|---|
| the verdict | `CT-12.1.verdict.final` | **computation** — composed, never originated (D-12 DN-1) |
| why it was downgraded | `CT-12.1.attribution.binding[]` | computation |
| the thesis, bear case, falsifiers | ★ **`CT-12.1.thesis_ref` → D-01 `CT-1.1`** | **judgement** |
| the analyst's own verdict | `CT-12.1.grade.verdict` | judgement — ★ shown **beside** `verdict.final`, never instead of it |
| ★ k-run stability | `CT-12.1.grade.{k, verdict_distribution}` | judgement — **RA-20 renders it verbatim: *"BUY 3 / HOLD 2"***, which **the ratio alone cannot produce** |
| confidence | `CT-12.1.grade.confidence` | judgement — ★ **RA-21: printed only with an empirical referent, else *"not yet calibrated (N=3)"*** |
| rank & ranked quantity | `CT-12.1.grade.ranked_quantity` | computation |
| risk alerts | `CT-12.1.alerts[]` | **fact** |
| deferral count | `CT-12.1.deferral` | fact — D-12 **DN-29** |

| ID | Rule |
|---|---|
| **RP-43a** | ★ **D-09 may RESOLVE a reference that `CT-12.1` carries; it may not RE-DERIVE a computation.** `thesis_ref` → `CT-1.1` is a lookup by an immutable key (**DN-33**) and is permitted. Recomputing a weight, a size or a verdict is not — that is the distinction RP-43 draws |
| **RP-43** | ★ **D-09 renders `CT-12.1` and never re-derives any of it.** A card field computed inside the renderer is a second, unowned computation (DC-5) |
| **RP-44** | ★ **The transported `grade` block is rendered, not consumed.** D-12 **DN-25** marks it `consumed_by_algebra: false`; D-09 is one of the two intended readers, and **RA-20's stability fraction reaches the human only through this path** |
| **RP-45** | ★ **`INCOMPLETE`, `BLOCKED_PRECONDITION` and `NO_THESIS` render as themselves.** D-09 may not present a run that did not complete as one that did (D-08 OR-16, D-12 DN-10/DN-12, DC-3) |
| **RP-47** | ★ **An absent risk pass renders as absent.** `CT-12.1.alerts_status` (**DN-38**) is rendered beside the alert block: `UNCHECKED: <why>` prints as itself, and **an empty alert list is never rendered as a clean bill of health**. ⚠ This is RP-45 extended to the one channel it missed — D-05's silence is a claim (RK-30), and a card that cannot distinguish *"nothing found"* from *"nobody looked"* makes it on the risk desk's behalf |
| **RP-46** | ⚠ **D-09 may never suppress an alert** (INV-021, D-05 RK-18) — including by severity filtering, pagination, or a "show more" that defaults to collapsed |

# 11. CONTRACTS

> **ID-collision notice.** `AC-9.k` / `CT-9.k` key `n` on **D-09**. **`sdd/specs/F9_universe_and_fundamental_sources/spec.md` issues `AC-9.1`…`AC-9.6` against live code.** Fifth live collision (L0 §16.4). Always qualify. *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))*

## CT-9.1 — DisciplineCard (JSON)

Inherits F1 CT-1.1 and adds the class/freshness envelope:

```json
{
  "ticker": "MU", "as_of": "2026-08-18",
  "fields": {
    "position":    {"value": "220 sh @ 91.40", "class": "fact",
                    "source": "D-11", "as_of": "2026-08-17"},
    "fair_value":  {"value": [380, 445], "class": "computation",
                    "source": "D-02", "as_of": "2026-08-18",
                    "trail_ref": "…", "known_defects": ["D-19"]},
    "verdict":     {"value": "HOLD", "class": "judgement", "source": "D-01",
                    "as_of": "2026-08-16",
                    "stability": {"k": 5, "modal": "BUY", "agreement": 0.6},
                    "softened_from": "BUY", "softened_by": "P3 gate"}
  },
  "falsifier": "…", "data_gaps": ["…"], "degraded": false
}
```

**Every field carries `class`, `source` and its own `as_of`** (RP-1, RP-2). `softened_from` records
DC-5 explicitly — a verdict that was made more conservative says so.

## CT-9.2 — Slate (JSON)

`(run_id, as_of, ranked[], actionable_pick, degraded, excluded[], arbitration{})` — **exactly one
`actionable_pick`** (INV-6), and `excluded[]` is never empty-by-omission.

## CT-9.3 — Delivery record (JSON, append-only)

`(delivery_id, artifact_ids[], channel, sent_at, recipient_hash, archive_path, outcome)`

---

# 12. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `build_card(ticker, as_of)` | `DisciplineCard` | raises on degraded input (RP-10) |
| `build_slate(run_id)` | `Slate` | one actionable pick; raises if all excluded (RP-12) |
| `build_brief(run_id)` | `Brief` | card + slate + context |
| `lint(artifact)` | `LintReport` | forecast-voice, length, uncited claims (RP-18) |
| `render(artifact, medium)` | `bytes` | **deterministic** — same input, same bytes |
| `deliver(artifact, channel)` | `Delivery` | idempotent, recorded, loud on failure |
| `archive(artifact)` | `ArchiveRef` | byte-identical to delivered (RP-24) |

---

# 13. BUSINESS RULES

| ID | Rule |
|---|---|
| **RP-1…RP-5** | Reliability classes & freshness — §5 |
| **RP-6…RP-8** | The Discipline Card — §6 |
| **RP-9…RP-12** | Fail loud — §7 |
| **RP-13…RP-20** | Anti-overconfidence — §8 |
| **RP-21…RP-24** | Delivery — §9.2 |
| **RP-31…RP-35** | One artifact, several renderings — §9.1 |
| **RP-25…RP-27** | The online surface — §10 |
| **RP-28** | ★ **Rendering is deterministic**: same artifact + same medium ⇒ **byte-identical output**. Without it there is no golden test, no diff between two days, and no evidence of what was seen |
| **RP-29** | D-09 imports **no** producing domain's internals and **never** the LLM gateway (ST-3, ST-5) |
| **RP-30** | D-09 **writes to nothing** — not the book, not the journal, not a producing domain's store (ST-9) |

---

# 14. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `RPT.INPUT.DEGRADED` | ERROR | a producing domain returned a degraded result — **refusal renders, report does not** (RP-10) |
| `RPT.INPUT.NO_PRODUCER` | ERROR | a card field with no producing domain (RP-6, DC-1) |
| `RPT.VERDICT.ESCALATED` | ERROR | rendering would make a verdict more aggressive (RP-7, DC-5, P3) |
| `RPT.CLASS.UNTAGGED` | ERROR | a rendered value with no reliability class (RP-1) |
| `RPT.FRESHNESS.UNSTATED` | ERROR | a component with no `as_of` (RP-2) |
| `RPT.FRESHNESS.STALE` | WARNING | component past its threshold — **rendered stale, never silently trusted** (RP-2) |
| `RPT.STABILITY.MISSING` | ERROR | a verdict on the actionable path with no stability result (RP-13) |
| `RPT.CONFIDENCE.BARE` | ERROR | a confidence number with no referent and no "not yet calibrated" (RP-14) |
| `RPT.LINT.FORECAST_VOICE` | ERROR | unearned-certainty language — **blocks the render** (RP-18) |
| `RPT.LINT.LENGTH` | WARNING | narrative over cap (RP-19) |
| `RPT.SLATE.ALL_EXCLUDED` | ERROR | every curated name below coverage — raises rather than picking one (RP-12) |
| `RPT.DELIVER.FAILED` | ERROR | send failed — loud, never a quiet log line (RP-23) |
| `RPT.ARCHIVE.MISMATCH` | ERROR | archived bytes ≠ delivered bytes (RP-24) |
| `RPT.RENDER.EXTERNAL_REF` | ERROR | HTML rendering references a network resource — breaks P6 (RP-31) |
| `RPT.RENDER.SCRIPT` | ERROR | HTML rendering contains script (RP-34) |
| `RPT.RENDER.DIVERGENT` | ERROR | two renderings of one artifact differ in **content** (RP-32) |
| `RPT.WRITE.ATTEMPTED` | ERROR | D-09 attempted a write to a producing domain (RP-30, ST-9) |

---

# 15. ACCEPTANCE CRITERIA

```text
RELIABILITY CLASSES  (§5)
□ AC-9.1   Every rendered value carries class in {fact, computation, judgement}
□ AC-9.2   The three classes are visually distinguishable in every delivered medium
□ AC-9.3   Every component states its own as_of; a card-level as_of alone fails
□ AC-9.4   A component past its staleness threshold renders marked stale
□ AC-9.5   A rendered fair value carries the D-19 caveat while D-19 is open (RP-5)

THE CARD  (§6)
□ AC-9.6   Every card field names a producing domain; one without raises
□ AC-9.7   Rendering may soften a verdict and never escalate it; softened_from records it
□ AC-9.8   Quant/thesis divergence renders both, attributed, with the disagreement stated
□ AC-9.9   D-09 computes no value a producing domain exposes

FAIL LOUD  (§7 — the D-15 regression)
□ AC-9.10  A degraded bundle is not persisted
□ AC-9.11  A degraded artifact renders a refusal banner, not a verdict from defaults
□ AC-9.12  An UPDATE never builds on a degraded cache
□ AC-9.13  A coverage-degraded run still delivers, carries the banner and the excluded
           list, and the under-featured names cannot be the actionable pick
□ AC-9.14  All curated names excluded => raises

ANTI-OVERCONFIDENCE  (§8)
□ AC-9.15  Verdict stability renders verbatim, including when unstable
□ AC-9.16  Confidence renders with a referent or "not yet calibrated (N=..)"
□ AC-9.17  The falsifier renders above the verdict
□ AC-9.18  Fair value renders as a band, never a point
□ AC-9.19  The data-gap block is present and non-collapsible
□ AC-9.20  Forecast-voice lint violations block the render (zero in output)
□ AC-9.21  Narrative sections respect their length caps
□ AC-9.22  Backtested returns are labelled and never shown as expected returns

DELIVERY, SURFACE, BOUNDARY
□ AC-9.23  A delivered artifact is readable with no live server (P6)
□ AC-9.24  Archived bytes == delivered bytes, per rendering
□ AC-9.24a The HTML rendering fetches nothing: no external css/font/image/script
           (assert on the emitted bytes, not on intent) — RP-31
□ AC-9.24b The HTML rendering contains no <script> (RP-34)
□ AC-9.24c HTML and markdown renderings of one artifact carry the SAME class-tagged
           field set and the same values; a divergence raises (RP-32)
□ AC-9.24d Reliability class is never signalled by colour alone (QP-1 residual)
□ AC-9.25  A delivery failure raises
□ AC-9.26  Prompt-alignment drift returns the diff to the viewer, not a stale page
□ AC-9.27  Same artifact + medium => byte-identical render (RP-28)
□ AC-9.28  src/reporting imports no LLM gateway and writes to nothing (RP-29, RP-30)
□ AC-9.29  ★ alerts_status renders; an empty alert list with UNCHECKED never
           renders as an all-clear (RP-47, DN-38)
```
□ AC-9.30  ★ A relayed value renders as relayed_judgement in EVERY medium, and
           more provisional than judgement — never a footnote on it (RP-1, RP-48)
□ AC-9.31  ★ The RELAY QUEUE block carries queued/returned/overdue/stale as
           SEPARATE counts and chases nothing (RP-49, D-01 RA-127/RA-128)
□ AC-9.32  ★★ With --deliver the card is SENT and a Delivery is returned; with-
           out it nothing is sent and the job reports that it did not (RP-50)
□ AC-9.33  ★ A missing REPORT_RECIPIENT raises when delivery is requested — it
           never falls back to the SMTP user (RP-51)
□ AC-9.34  ★ A NOT ACTIONABLE card is delivered like any other (RP-52)
□ AC-9.35  ★★ With a placeholder thesis gate the verdict row reads NO VERDICT —
           never BUY — and the placeholder text names today's cause (RP-53)
□ AC-9.36  ★ The card names the rule or model that ranked the pick (RP-54, DN-40)
□ AC-9.37  ★★ A refused-model card names it REFUSED with its failed gates, in both the ranking
           and the verdict lines (RP-55)
□ AC-9.38  ★ The card's Risk block shows the flag pass under its own label with
           history_through, a count per kind and D-05's recent flags in full, in
           markdown, HTML and the email body; an UNCHECKED pass shows its reason
           (RP-57, RK-40)

---

# 16. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| ~~QQ-5 (D-09 half)~~ | ~~If quantile heads produce the stop/target, what happens to D-09's card?~~ | ✅ **CLOSED — DC-1 already answers it.** D-09 renders what it is given and may not alter it. A deterministic band changes the field's *reliability class* from `judgement` to `computation` (RP-1), which is the point of the change, not a contract break |
| ~~QP-1~~ | ~~How are three reliability classes distinguished in email HTML?~~ | 🟡 **MOSTLY DISSOLVED 2026-08-18 by the HTML-attachment decision.** The hard half was *email-client* HTML — inline CSS only, unreliable `<style>`, uncontrolled dark-mode inversion. **A browser-rendered attachment has none of those limits**, so RP-1 is comfortably satisfiable where the artifact actually lives (§9). **What remains is genuinely cosmetic and deferred to post-E2E** (Victor): which glyph, which palette, how much emphasis. **One constraint survives the deferral** — class must not be signalled by **colour alone** (accessibility, and it inverts in dark mode); a glyph or text label carries it, and colour may reinforce |
| **QP-6** | Does the **email body** still need class distinction, given RP-35 makes it a notification? | It carries the slate — ranks and an actionable pick, all `computation`. If it never carries `judgement`, the question does not arise. Settle when the body's content is fixed |
| **QP-2** | Does the **card show the book position** at all? | It would make the card self-contained (P6) and pull D-11 onto the critical path of every render. Currently F1's Layer D is F2's and optional |
| **QP-3** | What is the staleness threshold **per component** (RP-2)? | L0 §8 has price/news/filings thresholds but nothing for *a thesis*. A 3-day-old thesis on a name that gapped is stale in a way no existing threshold catches |
| **QP-4** | Does RP-5's known-defect disclosure **scale**, or become banner blindness? | One caveat (D-19) is informative. Five would be ignored. Needs a severity bar, and the bar is a judgement |
| **QP-5** | Should the card render the **realised outcome** of its own prior falsifiers? | The strongest calibration device available (RM-12/RM-13) and it needs D-11's journal plus time |

---

# 17. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` **§5.1a DC-1…DC-5**, §3.1 LEVEL 1, §5.1 | the card's rules; RECOMMEND authority; the Report Writer Agent |
| `L1-fundamental-analysis.md` **§7.3**, RA-20…RA-29 | the anti-overconfidence obligations §8 executes |
| `L1-recording.md` ST-9, RC-19 | the book D-09 reads and may never write; the capital base |
| `L1-quantitative-analysis.md` §9.3, QA-27 | the quantile stop/target that would reclassify a card field |
| `L1-model-training.md` MT-38 | a deterministic stop/target is narrated, never altered |
| `L1-feature-engineering.md` §6.2, §8.1 | the arithmetic trail RP-3 needs; **D-19**, which RP-5 discloses |
| `sdd/specs/constitution.md` **P3, P5, P6**, INV-6, INV-9, INV-010 | monotonic verdicts, fail-loud, persistent delivery, one pick, prompt alignment |
| `sdd/design/rel6_design/L5-inherited-defects.md` **D-15**, **D-19** | the incident §7 exists to prevent; the defect RP-5 discloses |
| `sdd/specs/F1_disciplinary_report/spec.md` | prior art — Layers A–C, CT-1.1, **AC-1.15** *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `sdd/specs/F2_portfolio_and_delivery/spec.md` | prior art — delivery, CT-2.3 *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
