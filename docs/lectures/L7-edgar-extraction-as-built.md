# L7 — EDGAR extraction, as built: the code, the prompt, the purpose, and where it is stuck

> **Written:** 2026-09-08, after 24 live Anthropic calls (**$15.31**) across two filings.
> **Audience:** Victor, for study — and any agent that needs the whole picture before touching
> `E-01`, the golden set, or the filing fixtures.
> **Companion:** [`../../sdd/design/rel1_design/L7-golden-set-filing-1.md`](../../sdd/design/rel1_design/L7-golden-set-filing-1.md)
> is the *guard rail* document (what must not break). This one is the *explanation*.

---

# 1. The as-built path, end to end

## 1.1 The one-sentence shape

> A **filing** becomes an **EvidenceBundle**, one LLM call turns it into **cited items**, a
> deterministic check **aborts** if any citation does not hold, and `F2` **records the call** so the
> whole thing can be re-graded later for free.

```
 EDGAR .htm                                    tools/convert_filing.py
     │  (SEC requires a declared User-Agent)          │  HTML → text, mechanical
     ▼                                                ▼
 tests_src/fixtures/filings/<T>_<FY><Q>_10Q.txt   ← the FIXTURE. Committed. Citable.
     │
     ▼  build_bundle()            RA-1: every LLM call takes an EvidenceBundle and NOTHING else
 EvidenceBundle(ticker, as_of, parts=[BundlePart(kind, pins, content)])
     │                                   bundle_hash = sha256 over the parts
     ▼
 AnalysisGateway.call(prompt_name="E-01", prompt_version="v2", bundle, run_id)
     │   D-01's four guards: pinned+aligned prompt · no ambient context · view match · permutation
     ▼
 Gateway.complete(...)               D-00. GW-1…GW-23: retry, budget cap, truncation, refusal
     │   builds {model, max_tokens, payload, effort, thinking}
     ▼
 traced_transport(...)               F2 CT-2.2 — records the call, re-raises on error
     │
     ▼
 anthropic_transport()               ★ the ONE place this repo calls Anthropic
     │   client.messages.stream(model=claude-opus-5, tools=[extraction_tool], thinking=adaptive)
     ▼
 {"text": <tool input as JSON>, "tokens_in", "tokens_out", "stop_reason"}
     │
     ▼  parse_items()               offsets computed in CODE, not asked of the model (AP-5)
 [ExtractedItem(evidence_id, qualifier, value, unit, period, quote, span, status, tags, note), …]
     │
     ▼  ExtractionResult(...)       MP-18: identity = (evidence_id, qualifier, period[, span])
     │
     ▼  x01_verify_extraction()     ★★ DETERMINISTIC ABORT. No LLM is asked anything.
 ExtractionPass(results, report)
```

## 1.2 The prompt — what actually goes to the model

**Two things are sent, and they are separate on purpose.**

**(a) The block text** (`E-01`, currently `v2`, 1,053 characters). It is stored in
`sdd/design/rel6_design/L1-fundamental-analysis-master-prompt.md` §E-01 and mirrored **byte-for-byte**
in `src/fundamental/prompts/e_blocks.py`. ★ A structural test asserts the two are identical — the doc
is the source of truth, and a copy in code drifts silently otherwise.

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

Every value must appear VERBATIM inside the quote you cite for it. …            ← v2 added this
```

**(b) The tool schema** — `record_extractions`, with `strict: true`. This is `MP-5`:
*output shape is enforced by the API, not by prose.*

| field | why it exists |
|---|---|
| `evidence_id` | ★ an **enum** of the block's own item ids. ⚠ It was a free string with a description saying *"never invent one"*, and the model returned **all 56 items tagged `E-01`** — the block id. A description is prose; an enum is the API |
| `qualifier` | which ROW, when one id yields several (the segment). ⚠ **Not** part of the id — the published rubric maps `segments → "seg.revenue"` and matches on bare ids |
| `value` | the figure **without** a currency symbol |
| `unit` | where the currency and scale go (`MO-1`: a bare value is not monetary) |
| `period_start` / `period_end` | ★★ both, because **start is what separates a quarter from a year-to-date** |
| `cumulative_ytd` | the scar tag — *return it tagged, do NOT subtract* |
| `quote` | a verbatim span containing the value |
| `status` | `found` / `not_found` — ★ `MP-7`'s **stated failure output** |

## 1.3 The three guards that make it trustworthy

**`X-01` — the citation check** (`src/fundamental/claims/verify.py`). Deterministic, no LLM:

1. the cited span **resolves** in the bundle and matches the quote (whitespace-collapsed);
2. the **value appears in its own quote** — literally, or as a reformatting of one figure in it;
3. otherwise it **raises**, and the whole pass aborts.

> ⚠ There is deliberately no *"is it close?"* and no *"can it be derived?"* step. ★★ *A value
> assembled from two places is arithmetic, and arithmetic is D-02's.*

**`MP-18` — identity.** `(evidence_id, qualifier, period)`, plus the **span** for non-numeric items.
Two items sharing one identity are refused: nothing would say which one a rubric cites.

**`GW-23` — truncation is failure.** A response that hit `max_tokens` is not a short answer.
Downstream receives `NO_THESIS` — never a half thesis, never the previous one, never a default.

---

# 2. ⚠⚠ The purpose — and the honest answer to *"why not just use FMP?"*

**This is the sharpest question in the whole design, and it deserves a straight answer.**

## 2.1 What FMP already gives you, cheaply

Income statement, balance sheet, cash flow, ratios, prices — all of it, per quarter, for a fraction
of a cent. ★ And FMP even has **`revenue-product-segmentation`** and
**`revenue-geographic-segmentation`**.

**So a large part of what `E-01` extracts is, in fact, obtainable elsewhere.** Anyone defending this
pipeline without saying that is selling something.

## 2.2 What it does NOT give — measured, not assumed

| | FMP | `E-01` |
|---|---|---|
| segment revenue | ✅ but ⚠ **annual only** (`period=quarter` is refused) | ✅ **quarterly** |
| segment **operating income** | ✗ | ✅ |
| segment **assets** | ✗ | ✅ (or an explicit `not_found`) |
| *"the segmentation changed / was restated"* | ✗ — it is a **sentence**, not a field | ✅ `seg.basis_note` |
| as-reported **vs** as-restated | ✗ | ✅ both, tagged |
| ★★ **a citation** | ✗ | ✅ verbatim quote + character offset, machine-verified |

## 2.3 ★★★ The real reason, and it is not the numbers

**`E-01` is not primarily a data-acquisition mechanism. It is an EVIDENCE-acquisition mechanism.**

The scorecard cannot use a bare number. `MP-4`, `RA-32` and `RA-65` together say: a rubric level
declares `evidence_required` as a list of **evidence ids**, and `evidence_coverage` **counts** them.
An extraction with no id cannot be counted, so **it cannot support a rubric level**. And `RA-66` is
blunt about why:

> *"a 10-K that is present but from which the required number could not be pulled is not evidence."*

★★ So the question is not *"can I get segment revenue?"* — you can, from FMP, annually. The question
is *"can this system show me the sentence it read, in the document, at a character offset I can
check?"* **FMP gives you a number to trust. `E-01` gives you a number you can audit.**

That is the whole of `vision.md` §1.1 — *a system that can explain and defend every recommendation*
— reduced to one call. ⚠ A recommendation built on an FMP number can be *stated*; it cannot be
*defended*, because there is nothing to point at.

## 2.4 ⚠ Where that argument is weakest

Say it plainly, because a future reader will notice:

1. **For annual segment revenue alone, `E-01` duplicates FMP at ~10,000× the cost.** The
   justification rests entirely on the other five rows of the table above.
2. **The citation is only worth its price if something consumes it.** Today the golden set does.
   ⚠ If the scorecard never actually cites `evidence_id`s, this becomes expensive bookkeeping.
3. **$15.31 has produced no number a trader would act on.** It has produced a working *instrument*
   and 32 recorded findings. ★ That is the right trade at this stage and the wrong one later.

---

# 3. Methodology — how the two filings were actually run

## 3.1 The loop

```
 pick a filing that EXPERIENCES something the last one did not
        │
        ▼  fetch from EDGAR, convert, commit the fixture
        ▼  ONE live call, recorded by F2                     ← the only step that costs money
        ▼  promote the recording into tests_src/fixtures/recordings/   ← version-controlled
        ▼  Victor reads the FILING and establishes values     ← D2. Never from the output.
        ▼  cases point at <run_id>/<call_id>#<identity selector>
        ▼  run_regression replays the recording — FREE, FOREVER
```

★★ **The economics that make this work: one call, then unlimited free re-grading.** `F5` `D5` —
*CI replays `F2`'s recordings; it makes no live call.* Every fix after the first recording was
validated for **$0**.

## 3.2 Filing 1 — MU FY2025 Q3 (✅ 10 cases live)

Chosen because the `fmp-api` skill records a **measured** defect on it: FMP guessed MU's quarter
wrong by **71 %**, and the same class understated its TTM revenue by 41.5 % — worth **$379/share**.

**16 live calls, ~$11 → 50–59 verified items → 10 signed cases.** Every failure but one was in the
plumbing, and every one was caught by a guard that already existed.

★ The cases were chosen for **what they can catch**, not coverage — sign (`(9)`), the cumulative
trap in both directions, a `not_found`, a narrative item.

## 3.3 Filing 2 — AMD FY2025 Q3 (⛔ halted)

Chosen by an explicit rule from the skill:

> ⚠⚠ *"none of the three split in the window. One name that actually split reversed the conclusion
> completely. **Never generalise from names that did not experience the event.**"*

AMD **experiences** what MU does not: a **completed retrospective restatement**, nested sub-rows, a
December-anchored 52/53-week calendar, and three segments where MU has four.

**4 live calls, ~$4.20, no usable extraction.** ★ But it found `DX-31` — a real prompt defect that
MU structurally could not surface.

## 3.4 The technique worth reusing: the cheap controlled A/B

When the question was *"does `v2` cost 4× `v1`?"*, the instinct was to retry the full filing
(~$1.17) — one ambiguous sample. Instead: **both prompts, same 15 k slice, same effort, $0.46
total.** It disproved *both* of my claims at once.

> ★★★ **When the question is "systematic or variance?", buy two cheap samples, never one expensive
> one.**

---

# 4. Where it is stuck, tied to the above

## 4.1 The symptom

**AMD's full filing truncates at `max_tokens=32000` and returns a 2-character payload** — under both
`v2` and `v3`, ~$1.18 each. The model spends the whole output budget on adaptive thinking and never
emits the tool call.

## 4.2 ⚠⚠ `DX-30` — a truncation is ALL-OR-NOTHING

Every 32,000 truncation ever recorded returned **2 characters**. There is no partial answer.

★ This makes `GW-23` more right than it reads — there is no short answer to be tempted by — and it
means **a failed extraction costs full price for zero items.**

⚠ It also explains why raising `max_tokens` never helped (`DX-27`): the budget is spent on
**thinking**, not on the answer, so a bigger ceiling buys more thinking.

## 4.3 ✅ `DX-31` — one cause found and fixed (`E-01 v3`)

`v2` said: *"If the company restated prior-period segments, return **BOTH** the as-originally-reported
and the as-restated figures."* AMD states a restatement **and contains only the restated figures**.

★★★ The prompt demanded something the document does not hold, **and gave no way to say so**. `MP-7`
provides `not_found` per **item**; a cross-cutting instruction has no such exit — so the model could
not even reach the failure output.

> ★★ **Every demand in a prompt needs a reachable exit.** `MP-7` one level up.

`v3` adds two sentences and **fixes it, measured**: the identical slice went from 32,000-and-nothing
to **7,401 tokens and 46 items, $0.20**.

## 4.4 ⬜ What is still unexplained

AMD's **full** filing truncates under `v3` too. Ruled out by measurement: input size (76,551 vs MU's
74,943), `effort` (`low` truncated on 3,688 tokens), the restatement clause, duplicated tables, and
orphaned label/number rows (MU has 43, AMD 40).

**Remaining candidates, untested:**

1. ★★ **A third metric table with no item id.** AMD's segment note carries *revenue*, ***cost of
   sales and operating expenses***, and *operating income*. `E-01`'s item list has no home for cost
   of sales — and `MP-4` forbids inventing an id. The model sees a table it cannot file.
2. **Nested sub-rows vs an explicit sentence.** `Client`/`Gaming` sit inside `Total Client and
   Gaming`, which the filing says are *not* separate reportable segments. Layout contradicts prose.
3. **An identical duplicate table.** MU's second copy is a *percentage* table — visibly different.
   AMD's lines 529 and 1003 are byte-identical: *two findings or one?* ⚠ `MP-18` would collide them,
   so there may be **no answer that satisfies the schema**.
4. **Density** — AMD: 49 "segment" mentions, 10 "reportable segment". MU: 33 and 4.

## 4.5 The two structural questions this raises

⚠ Both are Victor's, not an agent's:

**(a) Should `max_tokens` be lowered to make failure cheap?** Since a truncation yields nothing
whatever the cap, setting it just above the largest *observed* success (MU used 9,865) makes a
failure cost **~$0.68 instead of $1.18** and succeeds on everything that ever has. ★ It does not fix
AMD; it stops AMD costing double to discover that.

**(b) Is one call for a whole 10-Q the right unit of work?** `E-01` asks for *"every period the
filings cover"* over a 228 KB document, producing 50–70 cited items in a single response. ⚠ That is
inherently fragile, and `DX-30` means the failure mode is total. Splitting per table, or per
`evidence_id`, would make failures partial and cheap — at the cost of more calls.

---

# 5. What a future reader should take from this

1. ★★ **The guards work, and they found almost everything.** `GW-23`, `X-01`, `MP-5`, `MP-7`,
   `MP-18`, `CF-1` each caught a real defect. ⚠ The only defect nothing caught was a **silent
   `max_tokens` clamp** — because it produced a *true-looking error message about a false number*.
2. ★★ **The expensive mistakes were reasoning, not typing.** Two claims about `v2` — that it cost 4×
   and that it bought compliance rather than correctness — both felt sound and were both wrong. A
   $0.46 experiment beat them.
3. ★★★ **Record before fixing.** Every entry in the `DX` log was written before its fix. That is the
   only reason this document could be assembled at all.
