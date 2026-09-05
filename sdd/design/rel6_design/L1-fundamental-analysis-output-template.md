# L1 Companion: Output Template & Schema — Fundamental Analysis (D-01)

> **Tier:** `sdd/design/rel6_design/` — **design tier, not authoritative.** Companion to
> [`L1-fundamental-analysis.md`](L1-fundamental-analysis.md) (governs) and
> [`L1-fundamental-analysis-master-prompt.md`](L1-fundamental-analysis-master-prompt.md) (the prompts that
> produce this). Where they disagree, the L1 spec is right.
> **Purpose:** what a D-01 output should look like — the JSON contract, the rubric criteria, the
> wording rules, and a full worked rendering — as a target to react to.

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚠  EVERY NUMBER, QUOTE AND CONCLUSION IN §6's WORKED EXAMPLE IS INVENTED.   ║
║                                                                              ║
║  It is a LAYOUT and SCHEMA demonstration on a familiar ticker. It is not     ║
║  research, not a recommendation, and no figure in it was read from any       ║
║  filing. Nothing here may be copied into a real report, a cache, or a        ║
║  picks log. If this file is ever rendered by the real pipeline, that is      ║
║  the D-15 incident happening a third time.                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-08-20 | Victor / AI | Initial draft. Four artifacts (§1), the extended `Thesis` (§2), the four rubrics written out in full (§3), the vocabulary contract (§4), numeric presentation (§5), a worked rendering (§6), the degraded rendering (§7), and a diff against `CT-1.1`/`CT-1.4` (§8). |

---

# 1. FOUR ARTIFACTS, NOT ONE

D-01 emits four things per run. They are separate because they have different readers, different
lifetimes, and different failure modes — and collapsing any two of them loses something specific.

| Artifact | Contract | Reader | Lifetime | If it were merged |
|---|---|---|---|---|
| **Thesis** | `CT-1.1` | the PM, via D-09 | until superseded by a new version | — |
| **GateVerdict** | `CT-1.4` | D-12, deterministically | one run | ★ **RA-47**: the projection would replace the thesis, and the falsifiers and bear case become unreachable |
| **MonitorReport** | `CT-1.3` | the monitor page; the run itself | one run, aggregated forever | The failure of a measurement would look like the absence of one (RA-30) |
| **AnalysisRun[]** | `CT-1.2` | nobody, until something goes wrong | forever (hashes), windowed (payloads) | ★ Nothing in §7 has anything to key on, and reproducibility-in-principle is gone |

```text
     Thesis          the analysis           ── rendered, read, argued with
       │
       ├─► GateVerdict    its decision-ready projection  ── consumed by D-12
       │
       ├─► MonitorReport  how much to trust it           ── published beside it
       │
       └─► AnalysisRun[]  how it was produced            ── never read until needed
```

---

# 2. THE THESIS CONTRACT — `CT-1.1` extended

Annotated. **★ marks a field this template proposes adding to `CT-1.1` as written**; §8 lists them
together with the reason.

```jsonc
{
  // ─── IDENTITY & REPRODUCIBILITY (AP-6) ────────────────────────────────
  "ticker": "MU",
  "thesis_version": 4,
  "as_of": "2026-08-16",
  "bundle_hash": "sha256:9f3c…",
  "supersedes": 3,                          // ★ explicit chain; null for v1
  "authored_by": {                          // ★ the composition, not just a version
    "prompt_blocks": ["S-1@v1","S-2@v1","S-3@v1","S-4@v1","S-5@v1",
                      "S-6@v1","S-8@v1","J-16@v1"],
    "rubrics": ["moat_durability@v2","earnings_quality@v1",
                "balance_sheet@v1","capital_allocation@v1"]
  },
  "runs": ["run_a1…","run_a2…","run_a3…"],  // ★ every AnalysisRun that fed this

  // ─── THE FALSIFIERS — FIRST IN THE DOCUMENT, AS THEY ARE ON THE PAGE ──
  // RA-23 governs the RENDER order; carrying it in the JSON too means a
  // renderer that iterates fields in order cannot get it wrong. (§8, D-1)
  "falsifiers": [
    {
      "ordinal": 1,
      "condition": "gross margin below 55% in two consecutive quarters",
      "observable": "f_gross_margin",       // a real D-02 field, not prose
      "source": "D-02",
      "threshold": {"op": "<", "value": 0.5500, "consecutive_periods": 2},
      "window_ends": "2027-08-16",          // ★ dated — RA-35
      "class": "business",                  // ★ business | price | event
      "checkable": true,
      "status": "unchecked",                // unchecked|unchanged|approaching|fired
      "last_checked": "2026-08-19T13:00:00Z",
      "current_value": 0.5810                // ★ so "approaching" is legible
    }
  ],
  "falsifier_coverage": {                   // ★ RA-35's "at least one business" rule,
    "business": 2, "price": 1, "event": 1   //   made visible rather than asserted
  },

  // ─── THE VERDICT AND HOW STABLE IT IS ─────────────────────────────────
  "verdict": "HOLD",
  "conviction": "Medium",
  "verdict_stability": {
    "perturbation": {                       // ★ RA-62 — the one that goes on the card
      "k": 3, "modal": "HOLD", "agreement": 0.667,
      "distribution": {"HOLD": 2, "BUY": 1},
      "variants": ["P-1","P-4"],
      "flipped_on": ["P-1"],                // ★ WHICH perturbation flipped it
      "seed": "sha256:9f3c…|J-16@v1|0"
    },
    "sampling": {                            // recorded, NOT rendered (§7.4b)
      "k": 1, "note": "single draw; production decoding is fixed"
    }
  },

  // ─── THE SCORECARD — TRANSPORTED, NEVER SUMMED (RA-53) ────────────────
  "scorecard": {
    "moat_durability":           {"score": 3, "rubric": "moat_durability@v2",
                                  "level_id": "moat.L3",
                                  "evidence_coverage": 0.75,
                                  "boundary_observation": "…",
                                  "claims": [3, 7, 9]},
    "earnings_quality":          {"score": 2, "rubric": "earnings_quality@v1",
                                  "level_id": "eq.L2",
                                  "evidence_coverage": 0.50, "…": "…"},
    "balance_sheet_resilience":  {"score": 3, "…": "…"},
    "capital_allocation":        {"score": 2, "…": "…"}
    // NO composite. NO average. NO weight. (RA-53)
  },

  // ─── CONFIDENCE — DERIVED, NEVER SELF-REPORTED (RA-38, RA-67) ─────────
  "confidence": {
    "value": 0.625,                         // = mean(evidence_coverage) — RA-65
    "basis": "evidence_coverage",           // never "self_reported"
    "coverage_detail": {                    // ★ so the reader sees WHICH gap
      "moat_durability": 0.75, "earnings_quality": 0.50,
      "balance_sheet_resilience": 0.75, "capital_allocation": 0.50
    },
    "floor_applied": null,                  // "INSUFFICIENT_DATA" | "HOLD_CAP" | null
    "calibration": {"n": 3, "status": "not_yet_calibrated"}
  },

  // ─── CLAIMS — THE AUDIT TRAIL OF EVERY SENTENCE (RA-9, S-3) ───────────
  "claims": [
    {"ordinal": 3, "kind": "fact",
     "text": "HBM revenue was $X in the September quarter.",
     "evidence_id": "seg.revenue|HBM|2026Q3",
     "evidence_span": {"accession_id": "0000723125-26-000042",
                       "offset": [104221, 104298],
                       "quote": "…"},
     "verified": true},                     // ★ X-01 ran and passed
    {"ordinal": 4, "kind": "inference",
     "text": "…which makes the segment the majority of incremental profit.",
     "rests_on": [3, 5], "evidence_span": null},
    {"ordinal": 5, "kind": "assumption",    // ★ third kind — S-3 has three
     "text": "The cycle trough passed in FY2025.",
     "rests_on": [], "rejectable_independently": true}
  ],

  // ─── THE ADVERSARIAL HALF — SEPARATELY PRODUCED (RA-15) ───────────────
  "bear_case": {
    "text": "…", "prompt_blocks": ["…","J-11@v1"], "run_id": "run_b1…",
    "own_falsifier": "…",                   // ★ J-11 item 4
    "substance_check": {"names_condition": true, "names_mechanism": true,
                        "independent_evidence": true,
                        "overlap_with_bull": 0.18}   // X-05, RM-11
  },
  "premortem": {"paths": [{"rank": 1, "narrative": "…",
                           "earliest_symptom": "…",
                           "lead_quarters": 3}], "run_id": "run_c1…"},

  // ─── WHAT WAS MISSING (AP-1, RA-25) ───────────────────────────────────
  "data_gaps": [
    {"gap": "no maintenance-vs-growth capex split",
     "why_wanted": "reinvestment quality in capital_allocation",
     "impact": "capital_allocation capped at L2",
     "obtainable": "not_disclosed",         // fetchable|not_disclosed|unknowable
     "would_change": "if maintenance capex were <40% of total, L3 becomes available"}
  ],
  "assumptions": ["cycle trough passed in FY2025"],

  // ─── FRESHNESS (RP-2) ─────────────────────────────────────────────────
  "staleness": {"hours_since_authored": 71, "threshold_hours": 168,
                "stale": false, "newest_evidence": "2026-08-15"},
  "degraded": false                         // ★ explicit; DC-3/RA-29
}
```

| Field | Rule |
|---|---|
| `verdict_stability.perturbation` | **required on the actionable pick** (RA-20, AC-1.8); `flipped_on` is what makes it diagnostic rather than decorative |
| `falsifiers[]` | ≥1, each `checkable: true`, ≥1 with `class: "business"` |
| `claims[].evidence_span` | required where `kind == "fact"`; `verified` must be `true` or the run fails (X-01, RA-6) |
| `confidence.basis` | never `"self_reported"` — `RES.CONFIDENCE.SELF_REPORTED` |
| `scorecard` | four keys exactly, no fifth, no composite (RA-52, RA-53) |
| `degraded` | if `true`, **nothing in this object may be rendered as analysis** (RA-29, DC-3) |

---

# 3. THE RUBRICS — written out, because a rubric is the analysis

RA-31 makes the model **select a written criterion**; the score is derived from the selection. That
puts the whole analytical method in the criteria text, which is why it belongs in a reviewable
document rather than buried in YAML nobody re-reads.

**Every dimension is `0–4`.** Level `0` is always `insufficient_evidence` and is **not a bad score**
— it is the absence of one, and it feeds `evidence_coverage`, not the judgement.

## 3.1 `moat_durability@v2`

| Score | Criterion | `evidence_required` |
|---|---|---|
| **4** | A named mechanism from the five (J-03 step 1) is evidenced, **and** the leaders' shares have not materially reordered across the bundle's history, **and** returns on invested capital have exceeded the cost of capital in every period the bundle covers. | `f_roic_series`, `f_wacc`, `peer_share_series`, `seg.revenue` |
| **3** | A mechanism is evidenced and **one** of the two outcome tests passes; the other is mixed or partially evidenced. | `f_roic_series`, `f_wacc`, `peer_share_series` |
| **2** | A mechanism is plausible from the disclosures but neither outcome test confirms it, **or** the outcome tests pass with no identifiable mechanism (a good run, not a moat). | `f_roic_series`, `seg.revenue` |
| **1** | No mechanism evidenced and at least one outcome test actively fails — share moving against the company, or returns at or below the cost of capital. | `f_roic_series`, `f_wacc` |
| **0** | `insufficient_evidence` — the bundle lacks the return series or the share history. | — |

> ★ **Level 2's second clause is the one that stops the rubric flattering.** "Returns are excellent
> and we cannot say why" is the honest description of a great many good businesses at a good moment,
> and it is *not* the same finding as a durable moat. A rubric without that clause scores them the
> same, which is how a moat score stops discriminating (RM-7, RA-34).

## 3.2 `earnings_quality@v1`

| Score | Criterion | `evidence_required` |
|---|---|---|
| **4** | Operating cash flow ≥ net income in every period in the bundle; free cash flow positive in every period; no adjustment label recurs in more than one period (E-04); no working-capital metric deteriorating faster than its driver. | `f_ocf_ni_series`, `f_fcf_series`, `ng.recurrence_note`, `f_dso`, `f_dio` |
| **3** | The cash test passes on trend with at most one period's exception, and that exception has a disclosed working-capital explanation the accounts corroborate. | `f_ocf_ni_series`, `f_fcf_series`, `ng.recurrence_note` |
| **2** | The cash test is mixed, **or** an adjustment label recurs in a majority of periods, **or** a working-capital metric is deteriorating faster than its driver without explanation. | `f_ocf_ni_series`, `ng.recurrence_note`, `f_dso`, `f_dio` |
| **1** | Reported earnings are persistently not converting to cash, **or** a material share of earnings comes from items outside the operating business, **or** an accounting change materially flattered the period (E-09). | `f_ocf_ni_series`, `f_accrual_ratio`, `ap.change` |
| **0** | `insufficient_evidence` — no cash-flow statement or fewer than three comparable periods. | — |

## 3.3 `balance_sheet@v1`

| Score | Criterion | `evidence_required` |
|---|---|---|
| **4** | Net cash, **or** net debt serviceable from the worst operating cash flow visible in the bundle's history, with no maturity wall inside three years and disclosed covenant headroom. | `f_net_debt`, `f_ocf_series`, `dm.ladder`, `dm.headroom` |
| **3** | Leverage within its own historical range, refinancing spread out, covenant headroom disclosed and adequate. | `f_net_debt_series`, `dm.ladder`, `dm.headroom` |
| **2** | Leverage elevated against its own history **or** a maturity concentration inside three years **or** covenant headroom not disclosed. | `f_net_debt_series`, `dm.ladder` |
| **1** | The bundle's worst historical operating cash flow would not service current debt, **or** a covenant is near its threshold, **or** liquidity depends on a revolver expiring inside 12 months. | `f_ocf_series`, `dm.headroom`, `dm.revolver` |
| **0** | `insufficient_evidence` — no maturity ladder or no multi-period cash-flow history. | — |

> ★ **Level 2's third clause treats an undisclosed covenant as a deduction, not a neutral.** A
> company comfortably inside its covenants generally says so; silence is weak evidence and the
> rubric should price it as weak evidence rather than as no evidence. This is the one place in the
> four rubrics where an *absence* moves the score rather than only the coverage — and it is
> deliberate, because the alternative rewards non-disclosure.

## 3.4 `capital_allocation@v1`

| Score | Criterion | `evidence_required` |
|---|---|---|
| **4** | Incremental capital has earned above the cost of capital across the bundle's history; buybacks were price-sensitive rather than steady; acquisitions have not been impaired; **and** stated priorities (E-12) match actions taken (E-07) with no unexplained reversal. | `f_incremental_roic`, `ca.buyback`, `ca.acquisition`, `cp.statement`, `f_price_range_series` |
| **3** | Reinvestment returns are adequate and the record of said-versus-did is clean, with one of the sub-tests mixed or unevidenced. | `f_incremental_roic`, `ca.buyback`, `cp.statement` |
| **2** | Capital is returned or deployed steadily without evidence of price or return discipline — a policy rather than a decision — **or** stated priorities and actions diverge without explanation. | `ca.buyback`, `ca.dividend`, `cp.statement` |
| **1** | Buybacks concentrated at the high end of the period's price range, **or** an acquisition subsequently impaired, **or** buyback spending is net of issuance not retiring shares (E-10), **or** a stated priority was reversed without explanation. | `ca.buyback`, `f_price_range_series`, `ca.acquisition`, `sc.end_of_period` |
| **0** | `insufficient_evidence` — fewer than three periods of allocation history, or no price series to test buyback timing. | — |

## 3.5 Rules the rubric set obeys

| ID | Rule |
|---|---|
| **OT-1** | ★ **Every criterion is a test against a named field, not an adjective.** "Strong balance sheet" is not a criterion; "serviceable from the worst OCF in the bundle" is. If a level cannot name what it reads, it cannot disperse (RA-34) |
| **OT-2** | **`evidence_required` cites extraction IDs and D-02 field names** (MP-4). A level whose required items are absent is *unavailable* (RA-32) — the model may not select it and say so quietly |
| **OT-3** | ★ **Level 0 is `insufficient_evidence`, not "bad".** It feeds `evidence_coverage`, never the judgement. Merging them makes an unread company look like a poor one, which is the most consequential confusion available in this schema |
| **OT-4** | **A rubric version is immutable once published** (RA-33). `moat_durability@v2` never changes; `@v3` supersedes it and invalidates every §7.4 baseline |

---

# 4. WORDING — the vocabulary contract

Prose quality is uncorrelated with analytical quality and strongly correlated with *perceived*
reliability (§7.3). These rules exist to remove the free confidence signals.

## 4.1 Banned, and what replaces them

| Banned | Why | Write instead |
|---|---|---|
| will · is set to · poised to · on track to | Forecast voice: a conditional wearing an indicative | "if X holds, Y follows" — and name X |
| clearly · obviously · undoubtedly · certainly · no doubt | Unearned certainty; adds nothing but tone | delete the word; the sentence survives |
| the market is missing · misunderstood · overlooked | Asserts a mind-state of the market | "the price requires X; the evidence supports Y" (J-09) |
| best-in-class · world-class · industry-leading | Superlative with no measurement | the figure, beside the peer figures it beats |
| strong · robust · healthy · solid *(unqualified)* | Adjectives standing in for a number | the number and its comparison |
| significant · substantial · material *(unquantified)* | ★ "Material" is an accounting term; using it loosely borrows its authority | the magnitude |
| we believe · in our view · it is worth noting | Process narration | say the thing |
| cannot be ruled out · possible that | True of everything; unfalsifiable | `insufficient_evidence` with the settling item named (S-4) |
| conservative estimate · at a minimum | Editorialises the arithmetic, which is D-02's | quote D-02's band |

## 4.2 Required constructions

| Where | Form |
|---|---|
| Any forward statement | `if <observable> <relation> <value>, then <consequence>` |
| Any comparison | `<value> vs <comparator value> (<comparator name>, <period>)` — never "vs peers" |
| Any absence | `INSUFFICIENT_EVIDENCE: needed <item>; bundle contains <what>; would change to <X\|Y>` |
| Any inference | traceable to the ordinals of the facts it rests on |
| Any assumption | listed in `assumptions[]`, rejectable on its own |
| Conviction | *"of the evidence a verdict like this needs, the bundle supplied <what> and did not supply <what>"* |

## 4.3 Length caps (RA-27)

| Section | Cap | Why this one |
|---|---|---|
| One-line thesis | 200 chars | It has to survive being read on a phone |
| Business model (J-02) | 400 words | Longer means the model is narrating the filing |
| Reconciliation (J-09) | 450 words | Two views and their gap; more is elaboration |
| Bear case (J-11) | 500 words | Equal to the bull case's total — ★ **deliberately not shorter** |
| Pre-mortem (J-12) | 500 words | Four paths |
| Verdict rationale (J-16) | 350 words | If it needs more, the scorecard is doing no work |
| Each falsifier | 150 chars | ★ A falsifier longer than a tweet is not checkable |

> ★ **The bear-case cap being equal to the bull's is the load-bearing one.** A 900-word bull case
> beside a 200-word bear case is an argument dressed as a balance, and the reader responds to the
> proportion long before they read either. RM-11 measures substance; this measures *space*, and space
> is what the eye actually weighs.

---

# 5. NUMBERS — how they render

| Rule | Detail |
|---|---|
| **OT-5** | ★ **Fair value renders as a band, never a point** (RA-24). `$380–$445`, not `$412.80`. The point estimate is an artifact of the arithmetic and reads as knowledge |
| **OT-6** | **Money is an amount plus a currency, inseparably** (L0 INV-001, INV-5). `US$412` — never a bare number, never a base-currency assumption |
| **OT-7** | **Percentages to 4 decimals internally** (INV-002), **rendered to the precision the source supports** — usually 1 dp. Internal precision is not a licence to display it |
| **OT-8** | ★ **A number renders with its reliability class** (RP-1): `fact` (reconciled), `computation` (traceable), `judgement` (stochastic). Same screen, same font, different marks |
| **OT-9** | ★ **A computation renders with its trail pointer and any known open defect in its producer** (RP-3, RP-5). A fair value whose DCF has a live defect carries the caveat on the face of the card |
| **OT-10** | **No number originated by D-01.** Every figure on a D-01 artifact is transported from D-02, D-07 or D-11. ★ A number that appears in a D-01 output and nowhere in its evidence bundle is a hallucination, not an insight |
| **OT-11** | ★ **A percentage that is a share of something names the denominator inline.** "Buybacks were 40 % (of operating cash flow, FY2026)" — an unlabelled percentage is the most portable form of a misleading number |

## 5.1 The typographic scheme

```text
   FACT          plain text, no mark          "220 sh @ US$91.40"
   COMPUTATION   ƒ prefix + trail link        "ƒ fair value US$380–445 ⟨trail⟩"
   JUDGEMENT     italic + stability tag       "moat: adequate (3/4)  ⟨stable 2/3⟩"
   ABSENCE       ▢ prefix, never blank        "▢ maintenance capex — not disclosed"
   DEFECT        ⚠ inline on the value        "ƒ fair value US$380–445 ⚠ D-19"
```

★ **`▢` matters more than it looks.** A blank where a number should be reads as "nothing to report";
a marked absence reads as "we looked and it was not there". Those are different findings and the
whole of AP-1 turns on the difference.

---

# 6. THE WORKED RENDERING

> ⚠ **Invented throughout.** See the banner at the top of this file.

```text
════════════════════════════════════════════════════════════════════════════════
  MU · Micron Technology            THESIS v4 · as of 2026-08-16 (71 h old)
  ⓘ  Analyst view (SEAT-2, D-01). Not a decision. The PM decides. 
════════════════════════════════════════════════════════════════════════════════

  ▸ WHAT WOULD PROVE THIS WRONG                          ← first, deliberately
  ─────────────────────────────────────────────────────────────────────────────
   1  business  gross margin < 55.0% in two consecutive quarters
                by 2027-08-16      now ƒ 58.1%        ●───────○  unchanged
   2  business  HBM share of segment revenue falls two quarters running
                by 2027-05-16      now ƒ 31.4%        ●──○      approaching
   3  event     a competitor's announced capacity moves to `operating`
                ahead of its stated schedule            ▢ not yet checkable
   4  price     close below US$62 for 10 sessions       now US$91.40   unchanged

   ▢ Falsifier 3 names an observable this system does not yet receive.
     It is reported as not-checkable rather than silently passing.  (J-15)

  ▸ VERDICT
  ─────────────────────────────────────────────────────────────────────────────
        HOLD          conviction Medium

        ⚠ perturbation-unstable: HOLD 2 / BUY 1  (k=3)
          flipped when the rubric options were reordered (P-1).
          A verdict that moves with option order is near a boundary.
          → gate status FLAG, not PASS.

        Of the evidence a HOLD needs, the bundle supplied the cash-flow and
        leverage record; it did not supply the maintenance-capex split or a
        disclosed covenant headroom.

  ▸ THE FOUR DIMENSIONS                    transported, never summed  (RA-53)
  ─────────────────────────────────────────────────────────────────────────────
     moat durability            3 / 4   ███░   coverage 75%   ⟨stable 3/3⟩
       mechanism: cost advantage (process node). Share among the three
       leaders has not reordered across the periods in the bundle; ƒ ROIC has
       exceeded ƒ WACC in 4 of 5 periods — one test clean, one mixed → L3.
       would move to L2 if: ƒ ROIC falls below ƒ WACC in any period.

     earnings quality           2 / 4   ██░░   coverage 50%   ⚠ moved 2 levels
       ƒ OCF/NI above 1.0 in 4 of 5 periods, but the "inventory
       revaluation" adjustment recurs in 3 of 5 (E-04) → L2.
       ▢ not read: cash-conversion-cycle detail by product line.
       ⚠ this dimension selected L2 and L4 across the k runs. Treat the
         number as unresolved, not as a 2. (RM-2)

     balance-sheet resilience   3 / 4   ███░   coverage 75%   ⟨stable 3/3⟩
       ƒ net debt/EBITDA within its own 5-period range; ladder spread past
       2030; ▢ covenant headroom not disclosed → capped at L3 per rubric.

     capital allocation         2 / 4   ██░░   coverage 50%   ⟨stable 3/3⟩
       Buybacks ran at a steady quarterly pace irrespective of the price
       range in each period — a policy, not an allocation decision → L2.
       ▢ maintenance vs growth capex not disclosed; reinvestment-return
         test unavailable.

     ─ no total. There is no fifth number here and there will not be one. ─

  ▸ THE PRICE VS THE STORY                                       (J-09)
  ─────────────────────────────────────────────────────────────────────────────
     price  US$91.40          ƒ fair value  US$380–445  ⟨trail⟩ ⚠ D-19
                              ⚠ the DCF returns an enterprise value per share;
                                overstated in proportion to leverage until
                                D-19 closes. Read the band with that in mind.

     What the price requires        vs the Stage-A evidence
       revenue growth ƒ 14%/yr      required MORE than evidenced
       gross margin ƒ 55% sustained roughly consistent
       10-year duration             required MORE than evidenced

     Differential view: I do not hold one. The consensus position and the
     evidence here point the same way with the same confidence.

  ▸ THE BEAR CASE                             separate call, separate prompt
  ─────────────────────────────────────────────────────────────────────────────
     [500 words, J-11 — overlap with the bull case 18%, names a mechanism,
      names its own falsification condition]

     Bear case's own falsifier: "if HBM qualification at a second
     hyperscaler is disclosed before 2027-03, this case is wrong."

  ▸ PRE-MORTEM — ranked by how early the symptom appears           (J-12)
  ─────────────────────────────────────────────────────────────────────────────
     1  ~3 quarters' warning   [path]   earliest symptom: [observable]
     2  ~2 quarters' warning   [path]   earliest symptom: [observable]
     3  ~1 quarter's warning   [path]   earliest symptom: [observable]
     4  no warning             [path]   ⚠ nothing announces this one

  ▸ WHAT I WANTED AND DID NOT HAVE                 mandatory · not collapsible
  ─────────────────────────────────────────────────────────────────────────────
     ▢ maintenance vs growth capex split      not disclosed by the company
         → caps capital_allocation at L2. If maintenance were <40% of total,
           L3 becomes available.
     ▢ covenant headroom                      not disclosed
         → caps balance_sheet at L3.
     ▢ cash-conversion detail by product line not disclosed
         → earnings_quality coverage 50%.
     ▢ reference-class base rates             not in bundle (D-07 gap, QP-4)
         → J-10 could not place any forward claim against a base rate.

  ▸ HOW MUCH TO TRUST THIS                                       (CT-1.3)
  ─────────────────────────────────────────────────────────────────────────────
     confidence            0.63   = mean evidence coverage.  ★ NOT a
                                    probability, and not the model's opinion.
     calibration           not yet calibrated (N=3)
                           ★ of 3 closed theses, too few to say whether
                             "Medium" conviction has meant anything.
     verdict base rate     BUY 41% / HOLD 47% / SELL 12%  (trailing 60)
     theme skew            AI/semis BUY rate 44% vs 41% universe — within noise
     seat disagreement     31% of scored names (D-01 vs D-03) — independence
                           looks real
     citation validity     138/138 numeric claims matched their spans
     forecast-voice lint   0 violations
     bear-case substance   pass
     falsifier trigger     ★ 2 fired / 5 abandoned across 7 closed theses —
                           ⚠ abandonment exceeds firing. The falsifiers may
                             be decorative. (RM-13)

  ▸ PROVENANCE
  ─────────────────────────────────────────────────────────────────────────────
     bundle sha256:9f3c…   model claude-opus-5   effort high   thinking adaptive
     prompts S-1@v1 S-2@v1 S-3@v1 S-4@v1 S-5@v1 S-6@v1 S-8@v1 J-16@v1
     rubrics moat_durability@v2 earnings_quality@v1 balance_sheet@v1
             capital_allocation@v1
     runs    run_a1 run_a2 run_a3   ·   supersedes thesis v3 (2026-05-02)
════════════════════════════════════════════════════════════════════════════════
```

## 6.1 What the layout is arguing

| Choice | The argument |
|---|---|
| Falsifiers **first** | RA-23. What would prove this wrong, before what we think. Ordering is an argument, and putting the verdict first makes everything after it a justification |
| Instability rendered **as a sentence, not a badge** | *"flipped when the rubric options were reordered"* cannot be skimmed past the way `0.67` can |
| `▢` for every absence | An absence that renders as blank space is indistinguishable from a clean result |
| The **⚠ on a dimension that dispersed** | RM-2 belongs beside the number it undermines, not on a monitor page nobody opens |
| **No composite score** — and the line saying so | RA-53. A reader who is told there is no total stops looking for one; a reader shown four numbers computes their own |
| Pre-mortem ranked by **warning time** | The PM can only act on risks that announce themselves. Probability ranking is the wrong sort for the decision this artifact serves |
| The **D-19 caveat inline on the fair value** | RP-5. Silence converts a recorded defect into an apparently sound number |
| `not yet calibrated (N=3)` **with the sentence explaining it** | RA-21. The bare phrase reads as a formality; the sentence says what is actually unknown |
| RM-13's **abandonment warning on the artifact** | It is the measurement that indicts the whole falsifier mechanism, so hiding it on a monitor page is self-serving |

---

# 7. THE DEGRADED RENDERING — the D-15 boundary

★ **The most important layout in this file**, because it is the one the two real incidents needed
and did not have. A failed call rendered as *"Verdict: HOLD | Conviction: Medium"* with no stop and
no targets, cached and emailed. **Nothing about the artifact looked wrong.**

```text
════════════════════════════════════════════════════════════════════════════════
  MU · Micron Technology                                    2026-08-20
  ⛔  NO ANALYSIS WAS PRODUCED
════════════════════════════════════════════════════════════════════════════════

   The research call for this name failed. There is no verdict, no
   conviction, no scorecard and no thesis, and none has been cached.

   what failed     J-16 verdict selection
   why             RES.LLM.DEGRADED — response truncated before the
                   structured output completed
   when            2026-08-20T09:14:22Z
   run             run_x7…                bundle sha256:9f3c…

   ★ The previous thesis (v4, 2026-08-16) is NOT shown here. Showing it
     would answer the question the reader is asking with an artifact
     that did not answer it.

   What happens next: the run is not retried automatically. Nothing
   downstream consumed this. The slate excludes this name explicitly
   rather than by omission.
════════════════════════════════════════════════════════════════════════════════
```

| ID | Rule |
|---|---|
| **OT-12** | ★ **A degraded call never renders as analysis, is never persisted, and is never built upon** (RA-29, P5, DC-3) — the three layers of the D-15 fix |
| **OT-13** | ★ **A truncated or refused response is a failure, not a partial success.** `outcome` has no `partial` value (RA-64/GW-22). **Both real incidents came from treating one as a success** |
| **OT-14** | ★ **The degraded card does not fall back to the prior thesis.** A stale answer displayed where a fresh one was expected is the same defect one layer removed — the reader cannot tell they are reading Tuesday's view |
| **OT-15** | **The name is excluded explicitly, never by omission** (CT-9.2). A name that vanishes from the slate looks like a name that was considered and passed over |

---

# 8. WHAT THIS TEMPLATE PROPOSES ADDING TO `CT-1.1` / `CT-1.4`

Each is a change to the governing spec, listed with what breaks without it.

| # | Addition | Without it |
|---|---|---|
| **D-1** | `falsifiers` **precede** `verdict` in the JSON, not only on the page | RA-23 is a rendering convention D-09 can quietly drop. Field order costs nothing and makes it structural |
| **D-2** | `falsifier.class ∈ {business, price, event}` + `falsifier_coverage` | ★ RA-35's "at least one about the business" is unverifiable. A falsifier set of four price levels is a stop-loss, and it satisfies the current contract |
| **D-3** | `falsifier.current_value` and `status: approaching` | "approaching" is unrenderable. The reader sees `unchanged` right up to the moment it fires |
| **D-4** | `verdict_stability.perturbation` **and** `.sampling` as separate objects, with `flipped_on` | RA-62 asks for exactly this split and `CT-1.1` still shows one merged `verdict_stability` from the retired sampling probe |
| **D-5** | `confidence.coverage_detail` per dimension | The reader sees `0.63` and cannot tell which dimension is thin — which is the only actionable part |
| **D-6** | `confidence.floor_applied` | INV-012/013 firing is invisible. A verdict capped at HOLD by a floor and one chosen as HOLD are different facts |
| **D-7** | `claims[].kind` includes **`assumption`** | S-3 has three kinds; `CT-1.1` has two. Assumptions currently live in a parallel string array with no link to the sentence that used them |
| **D-8** | `claims[].verified` — the result of X-01 | RA-6 runs and its result is discarded. `verified: false` should fail the run; today nothing carries it |
| **D-9** | `scorecard.<dim>.evidence_coverage` and `.level_id` | RA-65 is defined per dimension and `CT-1.1` transports only the aggregate. Also `level_id` makes RA-33's immutability checkable |
| **D-10** | `bear_case.own_falsifier` + `substance_check` | RM-11 computes and drops. The card cannot show that the bear case passed |
| **D-11** | `data_gaps[]` as **objects**, not strings | AP-1 wants impact and obtainability. A string list cannot be sorted into fetch / accept / unknowable, so nothing acts on it |
| **D-12** | `authored_by.prompt_blocks[]` — the composition | AP-6 records "prompt version" singular; a composed prompt (MP-2) has no single version, and the alignment key is the list |
| **D-13** | `supersedes` | The thesis chain is reconstructed by sorting on version, which breaks the moment one is deleted or a version is skipped |
| **D-14** | `degraded` explicit on the Thesis | RA-29 is enforced at render time only. A degraded object that reaches a different consumer has nothing on it saying so |
| **D-15** | `GateVerdict.grade` gains `evidence_coverage` per dimension | ★ RA-51a's argument — the grade carries what the artifact must *render*. The card shows per-dimension coverage; the grade currently cannot supply it |
