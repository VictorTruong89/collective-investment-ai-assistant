# ⏳ TEMPORARY — Golden cases, Micron, and what all those runs were for

**For Victor, 2026-09-17. Delete when absorbed into L3.** Written from the code as built; where
something is not built, it says so and explains the intention instead.

---

## 1. The problem golden cases exist to solve

You are building a system whose output is a *judgement* produced by a model that is **stochastic**,
whose prompts you keep editing, over **fixtures you occasionally re-render**. Three things can change
an answer, and from the outside they look identical:

```text
   the model was sampled differently          ← noise
   the prompt changed                         ← your edit
   the evidence changed                       ← a re-render, a new filing, a new tag
```

⚠ Without an anchor you cannot tell an improvement from a regression from a coin flip. Measured here:
two AMD runs of the same prompt, 82 minutes apart, differed in whether a field existed at all
(`DX-74`). That is the variance you are working against.

**A golden case is the anchor.** It says: *for this exact recorded call, the right answer to ONE field
is X, and here is who says so and why.* The harness replays the recording and fails if the field no
longer equals X.

---

## 2. What a golden case IS, in the code

`src/evaluation/golden/models.py` · `tests_src/fixtures/golden/*.yaml`

```yaml
- case_id: mu-fy2025q3-cnbu-revenue
  input_ref: "run-2026-09-11T082002-mu-e01/extract:E-01:llm:1#seg.revenue|CNBU|2025-02-28:2025-05-29"
  expected:                       # ← a SUBSET, never a snapshot
    evidence_id: seg.revenue
    qualifier: CNBU
    value: "5,069"
    unit: millions of USD
    status: found
  source: >-
    …where in the filing this is, so a future reader can re-check it without asking you
  established_at: "2026-09-07"
  established_by: "Victor Truong"
```

Four design decisions are load-bearing:

1. **`input_ref` points at a RECORDING, not at a live call.** `run-id / call-id # selector`. Replay is
   free and deterministic; grading never spends money and never re-asks the model.
2. **`expected` is a SUBSET** (`src/evaluation/regression/run.py::_matches`). You assert the value, the
   unit, the period — and stay silent about `quote`, `span`, `note`, which only the system produces.
   ★ A snapshot would be circular: to write it you would run the system and copy its output, and
   thereafter you would be asserting *"the system still does what the system did"*.
3. **`established_by` is a person.** For judgement cases the file records **whose** judgement it is
   (`is_judgement` is True for the `thesis` kind) rather than pretending to objectivity.
4. **The selector matches by MEANING, not position** — `(evidence_id, qualifier, period)`, the `MP-18`
   identity. Re-render the fixture and character offsets move; the reading does not.

**Two kinds, because two different contracts** (`RA-5`):

| kind | question | ground truth? | graded on |
|---|---|---|---|
| `extraction` | *what does this document say?* | ★ yes — the filing says what it says | the item's value, verified by `X-01` against a quoted span |
| `thesis` | *is this good / where in the cycle / how durable?* | ✗ none | **your** recorded judgement, `D2` |

---

## 3. What is actually in the golden set today

**33 live cases · 32 pass · 1 red** (`tests/integration/test_golden_regression.py`).

| Recording | Company | Block | Cases |
|---|---|---|---|
| `run-2026-09-11T082002-mu-e01` | Micron | E-01 segments | 11 |
| `run-2026-09-11T082118-amd-e01` | **AMD** | E-01 segments | 9 |
| `run-2026-09-11T115548-mu-e02` | Micron | E-02 guidance | 8 |
| `run-2026-09-12T024848-mu-stage-a` | Micron | J-01, J-07, J-08 | 3 |
| `run-2026-09-13T184111-mu-j05` / `…184227-mu-j06` | Micron | J-05, J-06 | 2 |

★ The one red is **J-07 cycle position**: the model said `mid`, you established `late`. It is red **on
purpose** — a recorded disagreement between you and the machine, which is exactly what the instrument
is for. Silencing it by changing the expected value to `mid` would destroy the measurement.

**Why AMD is in there at all:** a second company, same block (`E-01`), different filing. It answers
*"does the extractor read a DIFFERENT issuer's segment table correctly, or has it learned Micron?"*
That is the only cross-ticker thing the golden set does today — see §7.

---

## 4. Why so many `--dry-run` and `--live` rounds

Two different acts, and the distinction is the cost discipline:

- **`--dry-run` is free.** It builds the real bundle, composes the real prompt, counts the characters,
  prints the token estimate and the dollar ceiling — and sends nothing. Every live call in this project
  was preceded by one.
- **`--live` spends.** It is the only way to create a *recording*, and a recording is the thing a golden
  case points at. So: **you cannot have a golden case without having paid for the call once.**

A recording is retired — and must be re-made — when any of these change:

| What changed | Why the recording dies | Where |
|---|---|---|
| the block's prompt text | the answer graded is no longer the prompt shipped | `RA-13`, version bump |
| the **envelope** (`S-1`…`S-9`) | same, invisibly: the version does not move | `DX-76` records the hash |
| the fixture's text | offsets and quotes shift | `DX-102` (the repo header), `C13` |

⚠ That is why the same block has been run live several times. The costly instances, honestly:

| Round | Spend | What it bought |
|---|---|---|
| E-01 × 13 attempts (Sept 7-11) | ~$7.88 | the first clean extraction recording; a converter defect found three times |
| Stage A, 8 blocks | $3.68 → wasted | **truncated**: a third output budget nobody had reconciled (`DX-84`) |
| Stage A, re-run | ~$3.2 | the 8 recordings the thesis cases rest on |
| 7 E-blocks | $4.74 | 4 usable; 3 truncated (`DX-96`) |
| J-05 / J-06 × 3 orders | ~$4.8 | the first DERIVED rubric scores, after `DX-100` voided the first pair |
| E-09 × 6 | ~$4.8 | five truncations, then **success at `--effort low`, $0.42** (`DX-129`) |
| The first thesis (J-09…J-17) | $16.93 | one complete thesis; $5.33 of it lost to three failures |
| Industry E-13 × 3 + J-03 + J-08 | $3.31 | the moat score; $1.88 lost |

**Total: $71.66 over 104 calls.** Roughly **$20 of that was waste**, and every instance is a `DX` row
with the lesson attached. That ratio is itself a measurement: it is what it costs to learn a new failure
mode when each experiment is ~$0.50-0.90.

---

## 5. What we were doing with Micron specifically

Micron is **filing 1** (`tools/run_extraction_once.py::FILINGS`) — the FY2025 Q3 10-Q, as of
2025-06-26. One company, one document, carried end to end, to answer: *can this machine produce an
investment judgement in which every number is traceable to a filing line, and can we tell when it is
wrong?* The path as built:

```text
  EDGAR facts ──► D-07 ledger ──► D-02 valuation trail ($15.96/share, band, implied 28.3 %)
       │                                   │
       ├─► filing fixture ──► E-blocks ────┤          extraction: quotes verified by X-01
       │        (E-01 … E-13)              │
       │                                   ▼
       └─► sector file (Samsung · SK hynix · Sandisk) ──► Stage A, BLIND: J-01…J-08, J-20
                                                              │  price withheld physically
                                                     ★ FREEZE (hashed, committed)
                                                              ▼
                                        Stage B  J-09 J-10   ← the price is revealed here
                                        Stage C  J-11 J-12 J-13×5 J-14
                                        Stage D  J-15 → commit → J-16 → J-17
                                                              ▼
                                                    CT-1.1 Thesis: SELL / Low
                                                    4 falsifiers · 9 data gaps
```

**What it produced, and what happened to it:** the thesis said **SELL** at $126 because the price
required ~28.3 % annual cash-flow growth for a decade. Four quarters later, **two of its own four
falsifiers had fired** (cash flow after capex $26.2bn against a $5bn threshold; gross profit up every
quarter). The thesis was wrong, it said in advance exactly what would prove it wrong, and a script now
computes that verdict (`tools/check_falsifiers.py`). ★ **That loop closing is the deliverable** — not
the SELL.

---

## 6. The working principle, stated once

```text
   ①  PIN the inputs        bundle_hash over (ticker, as_of, every part's pins + content)
   ②  PIN the prompt        block text hashed at declaration + envelope hash
   ③  RECORD everything     F2 trace: payload, response, tokens, cost, bundle_hash
   ④  VERIFY mechanically   X-01: the quote resolves in the document; the value is in the quote
   ⑤  GATE on evidence      RA-32: a rubric level whose evidence is absent is not offered
   ⑥  ANCHOR with a person  D2: the golden value is the fund manager's, not the model's
   ⑦  MEASURE               replay the recording; red on divergence
```

⑥ is the one that makes ⑦ worth anything. Everything else can be automated; *what the right answer is*
cannot be, which is why `established_by` exists and why I never sign a case.

---

## 7. ⚠ How other tickers relate to Micron and AMD — **read this part carefully**

This is where intention and as-built diverge most, so here is the honest split.

### What IS built

- **The contracts are ticker-independent.** Prompt text, the shared envelope, the rubrics
  (`moat_durability@v2`, `earnings_quality@v3`, `balance_sheet_resilience@v3`,
  `capital_allocation@v3`), `X-01` verification, the evidence gate, the coverage ladder and the
  valuation formulas apply unchanged to any US filer with EDGAR facts. Running NVDA tomorrow needs a
  fixture and a CIK, not new analytical code.
- **The rubric levels are the comparable thing across tickers.** A `capital_allocation = 4` for Micron
  and a `4` for another name mean the same criterion text was satisfied. That, not a golden case, is
  what makes two companies comparable.
- **The sector file is shared per industry, not per ticker** (`RA-102`): the memory file
  (Samsung · SK hynix · Sandisk) serves every memory name you analyse. *"One sector file serves nearly
  the whole book."*
- **Two companies already prove the extractor is not company-specific**: the AMD E-01 cases pass under
  the same prompt that reads Micron.

### What is NOT built — and the intention

1. **A golden case does NOT transfer to another ticker.** It is bound to one recording of one call over
   one filing. There is no mechanism — and should not be — by which Micron's `cyclical_commodity`
   answer becomes an expectation for NVDA. ⇒ *Intention:* the golden set is a **regression instrument**
   for the CONTRACTS, not a truth set about companies. L3's standing rule is explicit: **do not grade
   every block on every name** — your time is the binding cost (`D2`), so a handful of deeply-checked
   cases on two companies protect the machinery that runs on all of them.
2. **There is no cross-ticker comparison module.** Nothing today ranks Micron against AMD, or computes
   a peer z-score of a rubric dimension. ⇒ *Intention:* `L1-feature-engineering` §6.2's peer context
   and `quality()`/`moat()` outputs are declared non-goals of `F10` and unbuilt; D-03's panel has
   `*_sector_z` features for the QUANT side, but the fundamental scorecard has no peer normalisation.
   When it lands it belongs in D-02 (arithmetic over many tickers), not in a prompt.
3. **`J-19` (industry-vs-company attribution) is written but undeclared.** It is the block designed to
   answer *"did this company move, or did its industry?"* — the real cross-ticker question. Its inputs
   (a peer-set change, pre-computed) do not exist yet; the sector file carries capacity announcements,
   not peer financial series.
4. **k = 3 stability has never been run.** `RM-1` needs three independent passes to say whether a
   verdict is stable; every result so far is k = 1. ⇒ *Intention:* run k = 3 once the evidence is
   complete — which, as of today, it finally is (coverage 1.000).
5. **No second company has been carried past Stage A.** AMD has extraction cases only. ⇒ *Intention:*
   the second full thesis is what turns "it worked once" into "it works", and it is also the first
   honest test of whether the blocks read a different business correctly.

---

## 8. Where the system stands, and what each number means

| Measure | Value | What it means |
|---|---|---|
| Spec ACs built | **169 / 169** | every acceptance criterion in this repo's 12 specs has a passing test in the right tier |
| Tests | **2,299 pass**, 1 red | the red is J-07, your recorded disagreement |
| Prompt blocks declared | **27 / 35 (77 %)** | text in code, drift-guarded against the design doc |
| Blocks that have completed a live call | **26 / 35 (74 %)** | ⚠ J-04's only answer is the pre-`DX-100` void one, so it has never produced a valid score |
| Scorecard coverage (Micron) | **1.000** | all four rubric dimensions have every evidence id they require |
| Golden cases | **33** (28 extraction · 5 thesis) | 2 blocks of 15 E-blocks and 5 of 20 J-blocks are graded |
| Theses produced | **1**, at k = 1 | its falsifiers: 2 FIRED, 2 HELD, computed |
| Findings | **129 `DX`**, 120 closed | every failure above is one of these rows |

---

## 9. If you read only one thing

The golden cases are not there to tell the system what Micron is worth. They are there so that **six
months from now, when a prompt is edited or a fixture re-rendered, CI can tell you that the machine
stopped reading a filing the way you read it** — and so that when the machine is wrong about a company,
as it was about Micron, the thesis has already written down what would prove it wrong, and a script can
check that without asking anyone's opinion.
