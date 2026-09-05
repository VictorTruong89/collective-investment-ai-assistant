# L1 Companion: The Relay Prompt — copy-paste fundamental research (D-01 §4B)

> **Tier:** `sdd/design/rel6_design/` — design tier, non-authoritative.
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** · **Domain:** D-01 · **Seat:** SEAT-2
> **Governed by:** [`L1-fundamental-analysis.md`](L1-fundamental-analysis.md) **§4B**, RA-114…RA-125
> **Composed from:** [`L1-fundamental-analysis-master-prompt.md`](L1-fundamental-analysis-master-prompt.md)
> **Purpose:** the actual text to paste into Claude Pro / ChatGPT Plus, plus the ingest contract the
> response must satisfy.
>
> ```text
> ╔════════════════════════════════════════════════════════════════╗
> ║  ⚠ STATUS: HAND-WRITTEN — and scheduled to STOP being a source.║
> ║                                                                ║
> ║  QP-8 closed 2026-08-23: the relay prompt is GENERATED from    ║
> ║  the block registry (master-prompt §10A, RG-1…RG-6), so a fix  ║
> ║  made to a block reaches the chat window without anyone        ║
> ║  remembering to copy it.                                       ║
> ║                                                                ║
> ║  Until the renderer lands at L3 B4.8 this file is written by   ║
> ║  hand — ★ which makes it THE ONE FILE IN THIS SET THAT CAN     ║
> ║  DRIFT, because nothing yet regenerates it.                    ║
> ║                                                                ║
> ║  §6 records which block each section came from, so generation  ║
> ║  is mechanical rather than archaeological.                     ║
> ╚════════════════════════════════════════════════════════════════╝
> ```

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.2.0 | 2026-08-23 | Victor | ✅ **QP-8: this file becomes GENERATED** from the block registry (master-prompt §10A). ★ **New §6 — the composition manifest**, recording block-by-block what each rendered section came from and **which three blocks are deliberately omitted**, so generation at B4.8 is mechanical. ⚠ Marked hand-written until then, and flagged as the one file here that can drift. |
| 0.1.0 | 2026-08-22 | Victor | Initial. **§2 one-paste form** (recommended to start), **§3 two-paste form** (restores RA-14 structurally), **§4 archetype inserts** (RA-123), **§5 the return contract**. |

---

# 1. HOW THIS FILE IS USED

```text
   D-01 composes  ──►  YOU paste into a FRESH chat  ──►  YOU paste the
   (WF-8, no LLM       (Claude Pro / ChatGPT Plus)       response back
    call, no cost)                                       (WF-9, ingest)
                                                              │
                                        ┌─────────────────────┘
                                        ▼
                        verify numbers vs D-02/D-07 (RA-118)
                        coverage → confidence → the floors fire (RA-114)
                        verdict_stability = null                (RA-115)
                        provenance = relayed_judgement          (RA-116)
```

| Rule | In practice |
|---|---|
| **RA-117** | ★ **Fresh chat every time. One prompt, one response.** Ask follow-ups if you want them — **do not paste a follow-up answer back** |
| **RA-122** | ★ **Do not hand-edit the prompt.** If it is wrong, the block is wrong — fix it here so every future ticker gets the fix |
| **RA-124** | **Manual only.** No browser automation, no scripted paste |
| **RA-125** | ★ **A truncated answer is a failed relay.** Re-run the whole prompt in a new chat; never ask it to "continue" |

> ⚠ **Turn web search ON.** This deliberately departs from **RA-1** (bundle-only), which is exactly
> why the output is a lower-assurance class. The prompt compensates by demanding a source for every
> number, so **§7's ingest can check the ones we hold data for.**

---

# 2. ★ THE ONE-PASTE PROMPT — recommended to start

**Replace `[TICKER]`, `[COMPANY]`, `[TODAY]`.** Insert the archetype block from §4 where marked.

```text
You are a senior equity research analyst. I am a self-directed investor running a
concentrated, deliberately high-risk book from Canada (base currency CAD), with
no derivatives, no shorts and no penny stocks. I make every decision myself; your
job is to give me evidence and the strongest case against my position — not a
recommendation I should follow.

Analyse [TICKER] — [COMPANY]. Today is [TODAY].

════════════════════════════════════════════════════════════════════
GROUND RULES — these bind the whole answer
════════════════════════════════════════════════════════════════════

1. EVERY number carries a source and a date, inline, at the point of use.
   Format: value (source, period). A number without one will be deleted.
2. If you cannot find something, write:
   INSUFFICIENT_EVIDENCE: <what you needed> — <where you looked>
   That is a correct answer. A plausible figure you did not verify is not.
3. Never estimate, interpolate or annualise a figure and present it as reported.
   If you derive something, mark it DERIVED and show the two inputs.
4. Tag every sentence you write as one of:
   [FACT]      — stated in a source you cite
   [INFERENCE] — follows from facts you have already stated
   [ASSUMPTION]— you supplied it; the sources do not
5. Do not use forecast voice. Not "will", "is set to", "poised to". Write the
   conditional and name the condition: "if X holds, then Y".
6. Do not use "clearly", "obviously", "undoubtedly", "the market is missing".
7. No media opinion as evidence. An analyst rating is consensus to measure
   yourself against, never support for a business fact.
8. Where a company's fiscal year differs from its peers', say so before
   comparing them.

════════════════════════════════════════════════════════════════════
PART A — THE BUSINESS, WITHOUT THE PRICE
★ Complete Part A fully before you look up the share price or any
  valuation multiple. Do not revise Part A after reading Part B.
  If you find yourself reasoning about whether the stock is cheap,
  stop and return to the business question.
════════════════════════════════════════════════════════════════════

A1. ARCHETYPE. Classify into exactly one and say what would change it:
    cyclical_commodity | compounder | secular_growth | regulated_utility |
    financial | binary_outcome | insufficient_evidence
    Name the runner-up and the one observation that would settle it.

A2. THE BUSINESS. How does this company turn an input into a dollar of profit?
    - what is sold, to whom, and what the buyer is choosing between
    - the cost structure: what is fixed, what is variable
    - the three variables that most move profit, ranked, with evidence
    - ★ what you do NOT understand about this business after reading its
      disclosures. This may not be "nothing".
    Max 400 words.

A3. MOAT. First: which mechanism, if any — intangible assets, switching costs,
    network effects, cost advantage, efficient scale? Evidence for each you
    claim. Then the two outcome tests, which override the story:
      (a) has market share among the leaders reordered over the last 5 years?
      (b) has ROIC exceeded the cost of capital in every year you can see?
    ★ "Returns are excellent and I cannot say why" is a legitimate and useful
    answer — it is NOT the same finding as a moat.
    Score 0-4 and name the observation that would move it down one.

A4. EARNINGS QUALITY.
    (a) operating cash flow vs net income, every year available
    (b) accrual ratio, and which line drives it
    (c) free cash flow after ALL capex vs net income
    (d) which "non-recurring" adjustments have recurred? List the years each
        label appeared.
    (e) DSO, inventory days, payables — is any growing faster than its driver?
    (f) ★ decompose ROE into margin x asset turnover x leverage. Which of the
        three moved? An ROE rising on leverage is a different fact from one
        rising on margin, and the headline number cannot tell them apart.
    Score 0-4 + the observation that would move it down one.

A5. BALANCE SHEET. Net debt, the maturity ladder, covenants and their disclosed
    headroom, liquidity, off-balance-sheet items.
    ★ At the worst operating cash flow visible in its own history, does this
    balance sheet still service its debt? If it has never been tested, say so —
    untested is not the same as passed.
    Score 0-4 + the observation that would move it down one.

A6. CAPITAL ALLOCATION. Where the cash went, year by year, as proportions.
    - buybacks: average price paid vs the price range of the year bought in
    - acquisitions: what was paid, goodwill recognised, later impaired?
    - incremental capital deployed vs the change in operating profit after it
    - is buyback spend net of issuance actually retiring shares?
    - ★ SAID VERSUS DID: what has management stated it would do with capital,
      and did they? Per commitment: kept / not kept / not yet testable.
    Score 0-4 + the observation that would move it down one.

A7. [INSERT ARCHETYPE BLOCK FROM §4 HERE]

A8. DATA GAPS. What did you want and not have? For each: why you wanted it,
    which conclusion is weaker without it, and whether it exists and you could
    not find it, the company does not disclose it, or nobody knows it.
    This list may not be empty.

════════════════════════════════════════════════════════════════════
PART B — NOW LOOK UP THE PRICE
════════════════════════════════════════════════════════════════════

B1. Current price, market cap, and the multiples you consider relevant for the
    archetype you chose in A1 — with the reason each is or is not meaningful
    at this point in the cycle.

B2. ★ WHAT DOES THE PRICE REQUIRE TO BE TRUE? Work backwards from the current
    price: what growth rate, what margin, for how long, does it imply? Then
    set each requirement against what you concluded in Part A:
      required_less_than_evidenced | roughly_consistent |
      required_more_than_evidenced | insufficient_evidence
    ★ Do not revise Part A. If the valuation makes you want to, say so
    explicitly as a finding — that sentence is more useful than the revision.

B3. THE GAP. Where the requirement and the evidence differ most, is that gap
    explained by something you found in Part A, or is it unexplained? An
    unexplained gap is a question you have not answered, not an opportunity.

B4. DIFFERENTIAL VIEW. State the consensus in one sentence. Then state where
    you differ and why — or state plainly that you do not. ★ "I hold the
    consensus view with the consensus confidence" is a legitimate answer and
    you should give it when it is true.

════════════════════════════════════════════════════════════════════
PART C — THE CASE AGAINST
★ Argue this properly. Do not hedge back toward Part A.
════════════════════════════════════════════════════════════════════

C1. BEAR CASE. You are a short-side analyst paid on whether you turn out right,
    not on whether you are persuasive.
    - the single strongest reason this business is worse than its accounts
      suggest
    - the three most load-bearing assumptions the price requires, what breaks
      each, and the observable early symptom of the break
    - what the accounts look like in two years if you are correct
    - ★ the falsification condition for YOUR OWN case: what observation in the
      next four quarters would show the bear case is wrong?
    Max 500 words.

C2. PRE-MORTEM. It is three years from now and this investment lost half its
    value. It is a fact. Explain how it happened — write the history, not a
    list of risks. Four causal paths, each with dates and ordering.
    For each: the earliest observable symptom, and how many quarters it
    preceded the damage.
    ★ Rank by HOW EARLY THE SYMPTOM APPEARS, not by likelihood. I can only act
    on risks that announce themselves in time.
    Which path, if any, was already visible in what you read today?

C3. IS THE HEADLINE METRIC REAL? Take the single metric this story most rests
    on. Enumerate every mechanism by which it could look better than the
    business: leverage, a shrinking denominator, one-time gains, asset sales,
    reserve releases, cash conversion, receivables, inventory, accounting
    changes, capitalised costs, cycle position, a non-standard definition.
    For each: present / absent / insufficient_evidence, with the specific
    item that would settle it.
    ★ If nothing is present, say so plainly. Do not manufacture a concern to
    appear rigorous.

════════════════════════════════════════════════════════════════════
PART D — COMMIT
★ Answer D1 before D2. Do not go back and adjust D1 after writing D2.
════════════════════════════════════════════════════════════════════

D1. WHAT WOULD PROVE THIS WRONG? Two to four conditions. Each must be:
      observable  — from public data, a filing line or a quoted figure
      dated       — with a deadline or evaluation window
      checkable   — a script could decide it. "Competition intensifies" fails.
                    "Gross margin below 55% in two consecutive quarters" passes.
      material    — if it fired, the thesis is wrong, not merely dented
    ★ At least one must be about the BUSINESS, not the share price. A list of
    price levels is a stop-loss wearing a thesis's clothing.
    You may not write "the thesis is invalid if the investment case no longer
    holds" or any variant.

D2. VERDICT. BUY / HOLD / SELL / INSUFFICIENT_DATA, and a conviction of
    Low / Medium / Medium-High / High.
    Then:
      - the three considerations that most determined it, ranked
      - ★ the strongest consideration pointing the OTHER way, and why it did
        not govern. If nothing points the other way, return INSUFFICIENT_DATA
        and say the analysis is incomplete.
      - what would move this one step more conservative, and by when
      - state your confidence as EVIDENCE, not feeling: "of the evidence a
        verdict like this needs, I found <what> and could not find <what>."

    ★ Do NOT give me a position size, an entry price, a stop-loss or a price
    target. Those are mine, and a number from you would carry an authority it
    has not earned.

════════════════════════════════════════════════════════════════════
FINALLY — the machine-readable block
════════════════════════════════════════════════════════════════════

End your answer with a fenced ```json block exactly matching the schema in the
message below this line. Values only from what you wrote above; no new claims.

[INSERT §7 RETURN SCHEMA HERE]
```

---

# 3. THE TWO-PASTE FORM — when RA-14 matters

★ **Use this for a name you are about to size up.** The one-paste form asks the model not to look at
the price; **this one does not give it the chance**, which is the difference between an instruction
and a guarantee (RA-119).

| Paste | Content | Rule |
|---|---|---|
| **Pass A** | Ground rules + **Part A only** + A8. ⚠ End with: *"Do not look up the share price, market capitalisation, any valuation multiple or any analyst target. If you already know them, do not use them. Stop after A8."* | RA-14 — structural |
| **Pass B** | ★ **A fresh chat.** Paste **Pass A's full output back as given context**, then Parts B, C and D. Add: *"The analysis above is FIXED. You may not revise it. If the valuation makes you want to, say so as a finding."* | RA-108's freeze, approximated by a session boundary |

> ⚠ **Pass B in a *fresh* chat is what makes this work.** Continuing the Pass A session leaves the
> model free to quietly revise Part A once it sees the price — which is the exact failure RA-14
> exists to prevent, and it would look identical in the output.

---

# 4. ARCHETYPE BLOCKS (A7) — RA-123

★ **D-01 selects one based on J-01's classification.** This is the "intelligence" that makes the
relay D-01's rather than a template service.

**`cyclical_commodity`** *(memory, energy, materials, autos, airlines, shipping)*
```text
A7. CYCLE POSITION AND SUPPLY.
    Where in the cycle: trough / early / mid / late / peak / cannot tell.
    Evidence for each, or an explicit gap: realised prices or ASPs vs their
    10-year range; inventory in days, company and channel; capacity
    utilisation; order lead times and cancellations; INDUSTRY-WIDE capex.
    ★ State explicitly which side of this trap the evidence puts you on: at a
    cyclical peak trailing earnings are highest and trailing multiples lowest,
    so the business looks cheapest exactly when it is most dangerous. At a
    trough the reverse. If you cannot tell, say so.
    SUPPLY: every announced competitor capacity addition, its stated timing,
    its status (announced / building / commissioning / operating) and any
    condition attached. Then: over the next eight quarters is announced supply
    growing faster than, in line with, or slower than the demand evidence?
    ★ Do NOT compute a normalised or mid-cycle EPS. I compute that elsewhere.
```

**`compounder` / `secular_growth`**
```text
A7. REINVESTMENT RUNWAY.
    How much capital can this business redeploy at its current return, and for
    how long? Evidence: incremental capital vs incremental profit, the size of
    the opportunity in the terms disclosures support, and any sign the return
    on new capital differs from the return on existing capital.
    ★ A high return with nowhere left to deploy it is a different investment
    from a high return with a decade of runway, and the ROIC number is
    identical in both.
```

**`financial`** *(banks, insurers, REITs)*
```text
A7. BOOK VALUE, SPREAD AND RESERVES.
    ★ EPS is not the primary metric here — do not lead with it.
    Book value per share and its growth; net interest margin or underwriting
    margin and what moves it; loss reserves and whether they have been
    strengthened or released, by year; capital ratios against requirement;
    the asset/liability duration mismatch if disclosed.
    ★ A reserve release flatters earnings and shrinks the cushion at once.
    Say which years had one.
```

**`regulated_utility`**
```text
A7. RATE BASE AND THE REGULATOR.
    Rate base and its growth; allowed vs earned ROE and the gap; the current
    rate case and its timetable; the capex plan and how it is funded; dividend
    coverage from cash flow, not earnings.
    ★ The regulator sets the return here, so "competitive advantage" is the
    wrong frame. The question is the regulatory relationship and its stability.
```

**`binary_outcome`** — ⚠ **out of mandate (M-1).** D-01 should not queue these; if one appears, the
correct relay is *"this name is outside the mandate"*, not an analysis.

---

# 6. ★ COMPOSITION MANIFEST — what generation will assemble

> ✅ **QP-8, closed 2026-08-23.** Recorded now so the renderer at **B4.8** is a mechanical exercise
> rather than an archaeological one. **Source of truth:
> [`L1-fundamental-analysis-master-prompt.md`](L1-fundamental-analysis-master-prompt.md) §10A**
> — RG-1…RG-6 and the substitution map.

## 6.1 Section → source block

| This file's section | Assembled from |
|---|---|
| Ground rules 1–8 (§2) | ★ **relay preamble** *(hand-written; replaces **S-2** grounding, **S-6** output contract, **S-7** anti-anchoring)* + **S-3** citation · **S-4** insufficient-evidence · **S-5** voice, all verbatim |
| A1 archetype | **J-01** |
| A2 the business | **J-02** |
| A3 moat | **J-03** |
| A4 earnings quality | **J-04** |
| A5 balance sheet | **J-05** |
| A6 capital allocation | **J-06** |
| A7 archetype block (§4) | **J-07** (cycle) · **J-08** (supply) · per-archetype variants, selected by J-01 — **RA-123** |
| A8 data gaps | **J-17** |
| B1–B4 | **J-09** reconciliation |
| C1 bear case | **J-11** |
| C2 pre-mortem | **J-12** |
| C3 metric forgery | **J-13** |
| D1 falsifiers | **J-15** |
| D2 verdict | **J-16** |
| §7 return schema | **CT-1.5** + the ingest contract |

## 6.2 ⚠ Deliberately NOT rendered — the omissions are decisions

| Block | Why omitted | Recoverable? |
|---|---|---|
| **J-10** base-rate check | ★ It reports an absence on every run (**QP-4** — a single-company bundle has no reference class). **A section that always says "no base rate available" trains the reader to skip sections**, which costs more than the section is worth | when D-07 supplies reference classes |
| **J-14** disconfirming sweep | ★ It reads *the analysis produced so far* — **impossible inside the single pass that produced it** | ✅ **yes, in the two-paste form** — Pass B can see Pass A |
| **J-19** attribution | Needs a period-aligned peer set the chat cannot assemble reliably (**RA-96a** — MU's August fiscal year-end against calendar-quarter peers) | when D-02 supplies `peer_context` to the ingest |

★ **J-14's omission is the one that costs most**, and it is the strongest argument for §3's two-paste
form *beyond* RA-14: the second paste does not merely restore the anchor-strip — **it restores the
adversarial re-read of the first pass.**

## 6.3 What generation will and will not change

| | |
|---|---|
| ✅ **Unchanged** | Every task instruction. They are transport-agnostic as written — *"assess whether this company can defend its pricing"* does not care who fetched the filing |
| ⚠ **Substituted** | Six token-level swaps from **§10A.3's closed map**: `the bundle`→`your sources`, `<computed_metrics>`→`the figures you have gathered`, evidence spans→inline source-and-date, structured output→fenced JSON, `view:blind`→the Part-A instruction |
| ⚠ **Lost** | ★ **Per-section prose tuning.** A sentence that reads well *only here* has nowhere to live under **RG-2**. **If that bites, the fix is to improve the block — not to fork the render**; a relay-only sentence is usually one compensating for a weak block |

## 6.4 Provenance the rendered file will carry (RG-5)

```yaml
generated_from: L1-fundamental-analysis-master-prompt.md@v0.3.0
substitution_map: v1
blocks: [relay-preamble@v1, S-3@v1, S-4@v1, S-5@v1,
         J-01@v1, J-02@v1, J-03@v1, J-04@v1, J-05@v1, J-06@v1,
         J-07@v1, J-08@v1, J-17@v1, J-09@v1, J-11@v1, J-12@v1,
         J-13@v1, J-15@v1, J-16@v1]
omitted: [J-10, J-14, J-19]          # §6.2 — with reasons
archetype_variant: cyclical_commodity
```

★ **This is what makes a pasted prompt attributable** (RA-122). A `RelayReport` records these block
versions, so when a relayed analysis turns out to have been wrong you can ask **which version of
which block asked the question that way** — and **RM-4 can re-run the pinned set against the old
composition** to see whether a block edit caused it.

---

# 7. THE RETURN SCHEMA — what the ingest reads (WF-9)

Appended to the prompt so the response ends machine-readable. **Every field must trace to prose
already written above it** — the block is a summary, never a new claim.

```json
{
  "ticker": "MU",
  "as_of": "2026-08-22",
  "archetype": "cyclical_commodity",
  "scorecard": {
    "moat_durability": 3,
    "earnings_quality": 2,
    "balance_sheet_resilience": 3,
    "capital_allocation": 2
  },
  "falsifiers": [
    {"condition": "gross margin below 55% in two consecutive quarters",
     "observable": "gross_margin", "by": "2027-08-22", "class": "business"}
  ],
  "verdict": "HOLD",
  "conviction": "Medium",
  "confidence_basis": "of the evidence a HOLD needs, I found X and could not find Y",
  "claims": [
    {"text": "...", "kind": "fact", "value": 0.581, "metric": "gross_margin",
     "period": "2026Q3", "source": "10-Q filed 2026-07-02"}
  ],
  "data_gaps": [
    {"gap": "maintenance vs growth capex split", "obtainable": "not_disclosed",
     "impact": "capital_allocation capped"}
  ],
  "bear_case_own_falsifier": "...",
  "premortem_earliest_symptom_quarters": 3
}
```

| Ingest step | Rule |
|---|---|
| **1. Freshness** | Session must be `fresh`; response must be complete — a truncated block fails (RA-117, RA-125) |
| **2. ★ Verify** | Every `claims[].value` with a `metric` + `period` is checked against D-02/D-07. Result per claim: `verified` / `contradicted` / `unverifiable`. ⚠ **Any `contradicted` fails the ingest** (RA-118) |
| **3. Coverage** | `coverage = verified / claims_total` → `confidence`. **INV-012/013's floors then fire unchanged** (RA-114) |
| **4. Falsifiers** | Each must bind to an observable this system receives, or it is recorded `not_checkable` (J-15's rule) |
| **5. Stability** | ★ `verdict_stability = null`, always. **AC-1.8 therefore blocks this name from being the actionable pick** (RA-115) |
| **6. Provenance** | `provenance_class = "relayed_judgement"` travels to D-09 and renders (RA-116) |

> ★ **Step 2 is the whole ingest.** Everything else is bookkeeping. **A relayed report is worth
> exactly as much as the fraction of it we can check against data we hold** — and that fraction,
> computed rather than asserted, is what caps the verdict.
