# L7 — The golden set: provenance, guard rails, and the full run history

> **Status:** Living record. Written 2026-09-08, after the first filing's ten cases went green.
> **Audience:** ⚠⚠ **any agent or session that touches the golden set, the filing fixtures, the
> extraction prompt, or `X-01` — especially while adding a SECOND filing.**
> **Scope:** what filing 1 is, why every piece of it is shaped the way it is, and **what must not be
> changed to make a second filing pass.**

---

# 0. ⚠⚠ READ THIS FIRST — the one rule

**A fix for filing 2 must not change anything filing 1 depends on, unless filing 1 is re-verified in
the same change.**

Filing 1 cost **$11.93 across 20 live API calls** and **29 recorded findings** to get green. Almost
every one of those findings was a defect in the *plumbing*, not the model — and several were caused
by fixing something else. ★ The cheapest thing in this whole document is the list in §5 of what a
plausible-looking fix would break.

**Before changing any file in §5, run:**

```bash
python3 -m pytest -q tests/integration/test_golden_regression.py
```

⚠ It replays a **recorded** call — no network, no cost. There is no excuse for breaking filing 1
silently.

---

# 1. What filing 1 IS

| | |
|---|---|
| Filer | MICRON TECHNOLOGY INC, CIK `0000723125` |
| Form | 10-Q, fiscal Q3 FY2025, **quarter ended 2025-05-29**, filed 2025-06-26 |
| Accession | `0000723125-25-000021` |
| Source | `https://www.sec.gov/Archives/edgar/data/723125/000072312525000021/mu-20250529.htm` |
| Fixture | `tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt` |
| Recording | `tests_src/fixtures/recordings/run-2026-09-08T230439-mu-e01/` |
| Prompt | `E-01` **v3** — recorded under it, and the suite asserts that |
| Cases | 10, all established by Victor Truong, 2026-09-07 |

★ **Why Micron.** Its fiscal year ends late August/early September, so quarter labels are a live
hazard — and the `fmp-api` skill records that **FMP guessed MU's quarter wrong by 71 %**, with the
same defect class (`_cumulative_fys`) understating MU's TTM revenue by 41.5 % and moving fair value
by **$379/share**. The filing is the natural home of the trap this project has already been bitten by.

---

# 2. The ten cases, and what each is FOR

⚠ Each was chosen for what it can **catch**, not for coverage. Deleting one silently removes a
specific guard.

| # | case_id | asserts | ⚠ if removed, nothing catches |
|---|---|---|---|
| 1 | `mu-fy2025q3-cnbu-revenue` | CNBU `5,069`, discrete quarter | a cumulative figure returned where a quarterly one was asked |
| 2 | `…-cnbu-revenue-ytd` | CNBU `14,028`, `cumulative_ytd` | the reverse, **and** the two being collapsed into one |
| 3 | `…-sbu-op-income` | SBU `(9)` | ★★ **SIGN** — dropped parentheses turn a loss into a profit |
| 4 | `…-sbu-revenue` | SBU `1,451` | `qualifier` not actually discriminating between segments |
| 5 | `…-ebu-revenue-ytd` | EBU `3,304`, cumulative | the YTD tag being applied by *position* rather than by reading |
| 6 | `…-cnbu-op-income` | CNBU `2,182` | revenue and operating income being crossed |
| 7 | `…-mbu-op-income-ytd` | MBU `604`, cumulative | the scar tag riding only on the headline figure |
| 8 | `…-ebu-op-income-ytd` | EBU `112`, cumulative | ⚠ **looks wrong, is not** — 112 barely exceeds its own 98 quarter. Verify, do not "correct" |
| 9 | `…-seg-assets-not-disclosed` | `seg.assets` **not_found** | ★★ the system **inventing** a figure the filing does not state |
| 10 | `…-cnbu-segment-name` | `seg.name` CNBU, narrative | `C14`'s identity rule for non-numeric items |

★ **Cases 1 and 2 are the pair that justifies `MP-18`'s `period` component.** They share
`evidence_id` *and* `qualifier* and differ **only** by period. Simplify identity to
`(evidence_id, qualifier)` and they collide.

⚠ **Case 10 deliberately asserts no `value`.** The filing writes the segment name with typographic
quotes; pinning it would test the HTML converter rather than the extraction. See `C13`.

---

# 3. ⚠⚠ Where every value came from — the `D2` chain

**Values were transcribed from the FILING (fixture lines ~1155–1169), never from the model's
output.** Reading them back from the recording would make the golden set certify the system against
itself, and **it would look identical from the outside**.

| field | established by | how |
|---|---|---|
| `value`, `unit` | ★ **Victor**, from the filing's segment tables | read off the document |
| `period.end` | the table's own column header | printed in the filing |
| `period.start` (quarter) | ⚠ **Item 2**, the share-repurchase table | it lists the quarter's fiscal months, beginning 2025-02-28 |
| `period.start` (nine-month) | the equity statement's opening balance | "Balance as of August 29, 2024" → the period begins the next day |
| `quote`, `span`, `note` | ⛔ **NOT asserted** | only the system can supply them — see §4 |

★★ **`DX-24` is the reason this section exists.** An AI agent claimed the filing "never states the
quarter's start date" and sourced it from XBRL — **its own earlier grep had already returned the
line that disproved that**, and it explained it away. Victor caught it on first read. ⚠ Treat any
agent-supplied provenance in this repo as a draft until a human has re-read the document.

---

# 4. ★★ The subset rule — the single most load-bearing design decision

`run_regression` compares with `_matches`, **not `==`**. A case's `expected` is a **subset**: it
asserts what was established and stays silent about the rest.

⚠⚠ **Do not "tighten" this to equality.** Snapshot equality would force `expected` to carry the
system's own `quote` and character offsets — meaning you would run the system, copy its output, and
thereafter assert that the system still produces what the system produced. **That is `D2`'s
circularity arriving through the back door, and it looks like diligence.**

★ It is also what makes filing 1 survive a fixture re-render: `C13` moved **every character offset
in the repo**, twice. Offsets move; the reading does not.

---

# 5. ⛔ THE BLAST RADIUS — what a filing-2 fix could break

Each row is a real defect already paid for once. ⚠ Changing any of these without re-running filing 1
is how the $11.93 gets spent again.

| file / rule | what filing 1 needs from it | ⚠ the plausible "fix" that breaks it |
|---|---|---|
| `tools/convert_filing.py` | `$`/`%` folded into their value cell; **all exotic whitespace → plain space**; **page furniture stripped** (`DX-35`) | "improving" table rendering. ★★ **6 of 9 live failures came from this file.** ⚠ A re-render was believed to invalidate every recording via `bundle_hash`; **`DX-36` found no hash was ever written and nothing compared one.** ✅ The real guard is now `test_every_recorded_quote_still_resolves_in_its_filing` |
| `MU_FY2025Q3_10Q.txt` | quotes resolve against it. ⚠ **NOT byte-stable — amended 2026-09-09, see §10.3.** Offsets are **recomputed at parse time**, never stored: a golden case's `input_ref` `start:end` is the **period**, not a character range | re-converting it "to match filing 2's style" **without first measuring which recorded quotes stop resolving** |
| `E-01` prompt text | **v3**, byte-identical to `L1-fundamental-analysis-master-prompt.md` §E-01 | editing one copy. ★ `tests/structural/test_prompt_text_matches_spec.py` catches it; do not delete that test |
| `E01_CURRENT_VERSION` | must match the recording's `prompt_version` | bumping to v3 without re-recording — the suite would grade a retired prompt |
| `MP-18` identity (`models.py`) | span included **only** for non-figures | adding the span unconditionally — ⚠ kills the numeric ambiguity guard (`test_c14_the_numeric_guard_is_UNCHANGED`) |
| `_matches` (`regression/run.py`) | subset comparison | "strictness" — see §4 |
| `_split_currency` | `$5,069` → `5,069` + `millions of USD` | letting the symbol back into `value`; ⚠ raising is correct when `unit` names no currency (`$` is not always USD) |
| `_locate` | tolerates whitespace, typography, literal `\uXXXX` | tightening to exact match — ⚠ the locator must never be **stricter than `X-01`**, which collapses whitespace |
| `parse_items` offset | the span END comes from `_locate`, **never** `start + len(quote)` (`DX-37`) | "simplifying" it back — ⚠ they agree only for an EXACT match, and `X-01` ① then refuses good citations |
| `X-01` typographic normalisation | curly quotes ≈ straight | reverting it — ★ those curly quotes come from **our own** `html.unescape` |
| `traced_transport(prompt_version=…)` | recordings must be attributable | dropping the argument — every recording silently becomes `None` again |
| `tests_src/fixtures/recordings/` | **version-controlled**, not `.state/` | moving it back to run state — ⚠ `DX-12`: the suite would skip everywhere and tell nobody |

---

# 6. The history, in one table — 20 calls, $11.93

⚠ Every failure below was in the **plumbing**, not the model. Only one was the model's (a paraphrase
in a narrative value), and that is what forced `E-01 v2`.

| # | outcome | what it taught |
|---|---|---|
| 1 | no credentials | — |
| 2 | ⚠ **billed, undecodable** | `Brotli 1.0.9` + `httpx2`: served, decoded locally, failed. ★★ *"it errored" ≠ "it was free"* |
| 3 | truncated @8k | `GW-23` refuses half answers |
| 4 | `X-01` refused | prose written into `value` — ★★ `MP-7` predicted it verbatim |
| 5 | ✅ **both golden values reproduced** | the question that mattered, answered |
| 6–7 | truncated | ⚠⚠ **a silent `max_tokens` clamp to 16,000** — `GW-23` reported a ceiling never sent. ~$1.56 wasted |
| 8 | `X-01` refused | curly quotes, from our own converter |
| 9 | truncated @32k | thinking expands into whatever budget it is given |
| 10 | missing `quote` | `MP-5` — what the schema does not require will not appear |
| 11–14 | quote not located | the converter, three more times (pipes, `$` cells, `\xa0`) |
| 15 | `MP-18` collision | narrative items over-fitted by a rule derived from `seg.revenue` |
| 16 | ✅ **50 items verified** | `B5` closed |
| 17 | truncated | ⚠ first `v2` run — looked like a 4× cost regression |
| 18–19 | ★★ **the A/B** | $0.46 disproved *both* of the agent's claims about `v2` |
| 20 | ✅ **59 items verified** | filing 1 final, `$0.6213` |

★★ **The A/B is the method to repeat for filing 2.** Two calls on a 15 k slice cost **$0.46** and
settled a question that a single full-filing retry ($1.17) would have left ambiguous. ⚠ When a
question is *"is this systematic or variance?"*, buy two cheap samples, not one expensive one.

---

# 7. ★ Filing 2 — which ticker, and why

## The rule that decides it

> ⚠⚠ *"a first pass on MSFT · MU · ARM found the series identical … **none of the three split in the
> window.** One name that actually split reversed the conclusion completely. **Never generalise a
> price finding from names that did not experience the event.**"* — `fmp-api` skill

★ So filing 2 must be chosen for what it **experiences that MU does not**, not for being "another
semiconductor".

## What MU already covers — and therefore does not test again

non-calendar fiscal year (Aug/Sep) · 4 reportable segments · cumulative-vs-discrete on both revenue
and operating income · a negative in parentheses · a segment recast **announced but not yet made** ·
segment assets **not disclosed** · US domestic 10-Q.

## Candidates

| ticker | what it adds | ⚠ risk |
|---|---|---|
| ★★ **AMD** or **INTC** | **calendar fiscal year** — Q3 is Jul–Sep. ★ Every period derivation in filing 1 was tuned against MU's Aug-30 / Feb-28 boundaries; a calendar filer is the cheapest test that nothing is hardcoded to them. Same 10-Q form, so the **converter is held constant** | segment assets probably also undisclosed, so case 9's *found* counterpart stays untested |
| **ARM** | ★★ the ticker where the cumulative-vs-discrete ratios were **actually measured** (Q3 2.76×, FY 3.30×) | ⛔ files **6-K/20-F**, not 10-Q — changes the **document form** at the same time as the company. ⚠ The converter caused 4 of 7 failures; do not vary it and the company together |
| NVDA | non-calendar FY (ends Jan) | ⚠ its documented defect is **price-split adjustment**, not segments — it does not test this pipeline |

## ★ Recommendation

**Filing 2 = AMD or Intel** (calendar-year 10-Q). It varies exactly one thing that matters — the
**fiscal calendar** — while holding the form, and therefore the converter, constant.

**Filing 3 = ARM.** It is the higher-value target because the defect was measured on it, but it is
also a **20-F/6-K**, and introducing a new document form deserves its own run rather than being
confounded with a new company.

⚠ **Not yet run.** Establishing filing 2's values is Victor's (`D2`), and the call costs ~$0.62.


---

# 8. Filing 2 (AMD FY2025 Q3) — status and the `v3` episode

*Appended 2026-09-08. ★ Filing 1 was green at every point below; every change was re-verified before
and after.*

## 8.1 Where filing 2 stands

| | |
|---|---|
| Filer | ADVANCED MICRO DEVICES INC, CIK `0000002488` |
| Form | 10-Q, Q3 FY2025, **quarter ended 2025-09-27**, filed 2025-11-05 |
| Accession | `0000002488-25-000166` |
| Fixture | `tests_src/fixtures/filings/AMD_FY2025Q3_10Q.txt` |
| Recording | `tests_src/fixtures/recordings/run-2026-09-08T222412-amd-e01` — **38 items, `E-01 v3`** |
| Cases | ⏳ **7, in `extraction.pending.yaml` — NOT signed, NOT graded** |

## 8.2 ⚠⚠ The `v3` episode — shipped and reverted within the hour

`E-01 v3` fixes `DX-31`, a real defect MU could not expose. It completed AMD **twice**. So it was
shipped, and MU was re-recorded under it.

**MU under `v3` returned ONE item** — `seg.name`/CNBU, **empty value** — where `v2` returns 50-59.
Not a truncation: 2,428 of 12,000 tokens, then it stopped.

| prompt | MU | AMD |
|---|---|---|
| `v2` | ✅ 50-59 items | ⛔ truncates |
| `v3` | ⛔ **1 empty item** | ✅ 38-46 items |

★★★ **The lesson, bought for $0.44: a prompt version must be proven against EVERY filing the golden
set grades, not only the filing that motivated it.** `v3` fixed something MU could not expose and
broke something AMD could not expose. **Neither filing alone would have caught both.**

⬜ `E01_CURRENT_VERSION` is back to `v2`; `v3` is a candidate again.

## 8.3 Two process holes closed on the way

**⚠ An unsigned case could not be staged.** `DX-28` makes a blank `established_at` refuse to load —
correctly — but that stops the **whole file** loading, filing 1 included. And commenting it out is
what produced the *"CASE 2 — NOT YET ESTABLISHED"* contradiction cleaned up the day before.
★ Fixed: `extraction.pending.yaml`, which `load_kind` never reads. A case is **moved** there and
back, never copied.

**⚠ The retired-prompt guard punished preparation.** It scanned every recording on disk, so AMD's
`v3` recording failed it even though no live case grades that recording. ★ Fixed: it now checks only
recordings a **loaded case actually references**.

## 8.4 ★★ The finding that solved AMD — a SMALLER budget

| cap | output | outcome | cost | latency |
|---|---|---|---|---|
| 32,000 | 32,000 | ⛔ truncated, zero items | $1.1828 | 246 s |
| **12,000** | **7,584** | ✅ **38 items** | **$0.5724** | 67 s |

Same filing, same prompt, **identical 76,551 input tokens**. ⚠⚠ **The generous cap caused the
failure** — adaptive thinking expands into whatever budget it is given, so a larger ceiling is a
risk, not insurance. ★ I raised that ceiling twice *because* runs were truncating, which made every
subsequent run worse.

## 8.5 ⚠ What filing 2 still needs from the fund manager

**`period.start` cannot be established from AMD's filing.** Verified:

| period | evidence |
|---|---|
| nine months | ★ derivable — balance-sheet comparative `December 28, 2024` is the prior fiscal year end, so the period begins **Dec 29, 2024** |
| **discrete quarter** | ⛔ **absent.** `June 29, 2025` appears nowhere; `June 28, 2025` only in commercial-paper text |

The model returned `2025-06-29` — an **inference**, not a quotation. MU's Item 2 listed its quarter's
fiscal months explicitly; AMD has no equivalent. ⚠ So every `period.start` in the pending cases is
blank, and closing them needs a **second document** (AMD's Q2 10-Q, period `2025-06-28` per EDGAR)
or XBRL — recorded in `source` either way.

## 8.6 Cost, end to end

**$16.32 measured across 26 live calls** (`python3 tools/spend_report.py`), ⚠ a floor: two calls
reached the vendor and recorded no tokens. Filing 1 ~$11.9, filing 2 ~$4.4.

★ What it bought: a working instrument, **33 recorded findings**, ten signed cases that replay for
free forever, and a second filing prepared to the last blank.


---

# 9. ✅ Resolved 2026-09-08 — `E-01 v3` ships, both filings green

**17 cases across two filings, `VERDICT: PASS`.** `E01_CURRENT_VERSION = "v3"`; both recordings
remade under it; the retired-`v2` recording deleted.

## 9.1 ★★ The result that mattered

**Every one of filing 1's ten established values is UNCHANGED under `v3`.** The prompt altered how
the model **cites**, not what the filing **says** — which is exactly the distinction a golden set
exists to police, and it held under a prompt change that was expected to be disruptive.

## 9.2 ⚠⚠ `v3` was shipped, reverted, and shipped again — in one evening

| attempt | MU | verdict |
|---|---|---|
| ship #1 | **1 item**, empty value, 2,428 tokens | ⛔ reverted within the hour |
| ship #2 | **57 items**, 9,596 tokens, $0.61 | ✅ shipped |

★★★ **The same prompt, on the same filing, differed 57x in yield between two runs.** The first
result was a bad sample, not a systematic failure.

⚠ **The revert was still correct on the information available.** With one observation, "v3 breaks
MU" and "that was a bad draw" are indistinguishable — and the cheap, reversible move was to protect
filing 1. ★ The lesson is not *"should have trusted v3"*; it is:

> ⚠⚠ **One sample is not evidence about a stochastic system.** It was not evidence when it looked
> like a 4x cost regression (`DX-29`, disproved by a $0.46 A/B), and it was not evidence here.
> ★ Where a second sample is cheap, buy it before concluding.

## 9.3 Two bugs the second filing exposed in the harness itself

- ⚠ **`golden_replay` used ONE bundle for every case.** Correct with a single filing; a bug the
  moment a second joined — AMD's cases were parsed against MU's text and every quote *"was not in
  the bundle"*. ★ Each recording now carries a **`filing.json`** naming its own fixture.
- ⚠ **`promote_recording.py` could not import `tools`** when run as a script. Silent until it needed
  a sibling module.

## 9.4 Filing 2 — established

Seven cases, signed by Victor 2026-09-08, `period.start` established from **XBRL**
(`2025-06-29` discrete / `2024-12-29` cumulative, both cross-checked against the filing's own
"Total net revenue" totals of $9,246M and $24,369M).

★ **Case 17's basis differs from filing 1's** and is recorded as such: MU states outright *"we do not
identify or report internally our assets … by segment"*; AMD's basis is an **exclusion from an
enumeration** — the CODM reviews *"segment net revenue, cost of sales and operating expenses, and
operating income (loss)"*, and assets are absent from that list (ASC 280).

## 9.5 Cost

**$16.94 across 27 live calls.** ⚠ A floor — two calls reached the vendor and recorded no tokens.


---

# 10. ✅ 2026-09-09 — `E-02 v2` live, and the blast radius re-measured

## 10.1 The run

**74,986 in / 10,509 out, $0.6377, 103 s, 51 items**, `effort=medium`. Running total **$18.22 / 29
calls**. Both fixes carried into it held, measured against the recorded response:

- ✅ **`DX-33`** — **0 of 51** values fail `X-01` ② (was 2 of 44). The currency/verbatim conflict is
  gone.
- ✅ **`DX-34`** — `gd.direction` absent; six ids returned, not seven.

⚠ Yield by id: `gd.value` 15 · `gd.metric` 10 · `gd.stated_on` 10 · `gd.language_note` 8 ·
`gd.period` 7 · `gd.prior_value` 1. ★ `gd.prior_value` at 1 is expected and not a defect — a single
10-Q rarely restates its own earlier guidance; it needs a **multi-filing bundle** to exercise, which
is a filing-3 question, not a prompt question.

## 10.2 ⛔ `DX-35` — the sixth defect from `convert_filing.py`

47 of 51 quotes located. The 4 that did not are **one quote**, and the quote is right: MU paginates
mid-sentence and our converter left the page number, the running header and `Table of Contents`
sitting inside the sentence. The model read across the break the way a person does.

★★ **`E-01` could never have found this.** It reads segment TABLES, and a table does not straddle a
page. `E-02` reads narrative prose, which does. ⚠ Add this to §8's list of what a second *block*
buys that a second *filing* cannot.

★★★ **`X-01` aborts, so 4 dead items discarded 47 good ones** — `DX-30`'s *zero items at full price*
arriving from a new direction. ⚠ The $0.6377 was **not** lost: `D5` keeps the response on disk and
re-parsing is free. Whether `X-01` should abort the batch or quarantine the item is now an open
design question; it has cost a full call's yield twice.

## 10.3 ★★★ §5 amended — measure the blast radius, do not assume it

§5 said a re-render *"invalidates the recording"*. Before spending ~$1.20 to re-record, the strip was
applied in memory and the question asked directly:

```
MU : 211,618 -> 209,984 chars (1,634 removed)   recorded E-01 quotes that stop locating: 0
AMD: 228,658 -> 227,542 chars (1,116 removed)   recorded E-01 quotes that stop locating: 0
E-02 unlocatable: 4 -> 0                        X-01 (1) span-vs-quote mismatches: 0
```

★ **A re-render invalidates a recording only if it moves text the model quoted.** Furniture is text
nobody quotes. Three reasons this held, and all three are load-bearing facts about this design:

1. offsets are **recomputed at parse time**, never stored (`AP-5` — the offset is arithmetic);
2. a golden case's `input_ref` `start:end` is the **period**, not a character span (`MP-18`);
3. `_locate` collapses whitespace, so line-deletion at a boundary is invisible to it.

⚠⚠ **And the guard §5 relied on was fiction (`DX-36`).** `promote_recording.py` claimed the
`bundle_hash` makes drift *"disagree loudly"*; no hash was ever written and nothing compared one.
★★ A hash would also have been the **wrong** guard — it fires on any byte change, and would have
charged $1.20 for a change measured to alter nothing. The guard that shipped instead asks the
question that actually matters — *does every recorded quote still resolve in its filing?* — over
every recording × every quote, and it is a test, not a sentence.

## 10.4 ⛔ `DX-37` — verifying a guard with a SIMULATION verifies the simulation

★★★ I checked `DX-35` with a hand-rolled whitespace comparison. It passed. Then I ran the **real**
`x01_verify_extraction`, and it failed — because `parse_items` computes `start, end = _locate(...)`
and then **discards `end`**, writing `offset=(start, start + len(quote))`.

Those agree only when the match was **exact**. `_locate` also matches under normalisation, where the
document's span is a different LENGTH from the quote — so the span ends short and `X-01` ① rejects a
good citation, **blaming the model for our arithmetic**.

⚠ **Latent, not new.** 0 of MU's 60 and 0 of AMD's 41 recorded spans change; only a
normalisation-matched quote can differ in length, and `DX-35`'s strip is what creates the `\n\n\n`
runs that reach it. ★ Add to §5: `parse_items`' offset must come from the locator, never from
`len(quote)`.

## 10.5 ✅ The failed call, recovered for $0

With the strip applied and `DX-37` fixed, the aborted `$0.6377` run re-parses clean:

```
parse_items : 51 items      (was: ValueError, 0 items)
X-01 (REAL) : checked=49  facts=49  not_found=2
```

★★ **This is `D5` paying for itself a third time.** The call is on disk; every fix since has been
free. Two defects — one of them latent for weeks — were found and closed without a single new call.

## 10.6 ⬜ What the run says about `E-02 v2`'s PROMPT — three open questions

⚠ None of these is a defect and none blocks a case. They are what 51 real items reveal about a
prompt that had never been run, and they are recorded so a future `v3` is argued from evidence.

1. **`gd.stated_on` returns `"Form 10-Q"` — ten times out of ten.** The block asks for *"the
   filing/date it was stated in"* and gets the FORM TYPE, which every item in a single-filing bundle
   shares. ⚠ 10 of 51 items carry near-zero information. ★ The date is already in the bundle
   metadata, so the honest options are to drop the item or to ask for the accession — not to ask
   the model harder.
2. **A negative statement was returned as guidance.** `gd.metric` = *"We do not expect these enacted
   laws to materially impact our effective tax rate for 2025"*, with its `gd.value` correctly
   `not_found`. ⚠ Is *"we do not expect a material impact"* forward-looking guidance? ★ It is a
   real company statement about the future with no figure — arguably the most honest possible
   `E-02` item, and arguably not guidance at all. **The fund manager's call, not the prompt's.**
3. **`gd.metric` does not JOIN to its `gd.value`s.** The amortization schedule returns one
   `gd.metric` qualified *"Expected amortization expense (intangible assets)"* and six `gd.value`s
   qualified *"… — 2026"*, *"… — 2027"*, and so on. ⚠⚠ The qualifier is doing two jobs at once —
   *which guidance* and *which year* — so nothing links the metric to its own figures. ★ `MP-18`
   made identity `(evidence_id, qualifier, period)`; this is the first evidence that a block may
   need the qualifier to be STRUCTURED rather than a free string.

## 10.7 ✅ `E-02` cases — 8 prepared, **5 signed and live**, 3 held back

★ Written to `extraction.pending.yaml` 2026-09-09, covering **all six** `E-02` item ids. Every one
resolves, replays green, **and reds under mutation** — verified before Victor sees them, because a
case that cannot go red is decoration.

| # | case | what it catches |
|---|---|---|
| 21 | `gd-capex-value` | ★★★ `DX-33` — a PHRASE keeps its `$` |
| 22 | `gd-chips-ceiling` | *"up to"* dropped → a cap becomes a forecast |
| 23 | `gd-newyork-ceiling` | ★★★ `DX-35` — the item that died on the page break |
| 24 | `gd-newyork-nonbinding` | ★★★ *"non-binding"* dropped → $5.5bn reads as committed |
| 25 | `gd-amortization-2025` | ★★ `DX-33`'s other half — a BARE FIGURE drops its `$`; 6 numbers in one sentence |
| 26 | `gd-hedge-relative-period` | `MP-6` — a relative period silently resolved to a date |
| 27 | `gd-prior-value-absent` | ★★★ `MP-7` — the only case in the set that grades an ABSENCE |
| 28 | `gd-dividend-per-share` | `MO-1` — a per-share unit read as millions |

★ **Signed by Victor 2026-09-09 and moved into `extraction.yaml`: 24, 25, 26, 27, 28.** The golden
set now loads **25 cases — 20 `E-01`, 5 `E-02` — and replays green.**

⚠⚠ **Cases 21, 22 and 23 were NOT signed and stay in `extraction.pending.yaml`.** ★★★ Two of them,
21 and 23, are the cases that pin this session's own fixes — `DX-33` and `DX-35`. Until they are
signed, both fixes are in code but **ungraded**, and an ungraded fix is one refactor from undone.
⚠ Case 24 is live while case 23 is not, and they quote the SAME SENTENCE: the golden set currently
asserts that the New York funding is *"non-binding"* without asserting the *"up to $5.5 billion"* it
qualifies.

## 10.8 ⛔⛔ `DX-38` — the unsigned cases would have graded as ESTABLISHED

★★★ **The three blanks are how this was found, and finding it is worth more than the five cases.**
`established_by: "____"` **passed validation.** The check was `if not self.established_by.strip()`,
which refuses an empty string and accepts anything else — including the template's own blank.

⚠⚠ **`DX-28` had already fixed exactly this hole, on `established_at`, ONE LINE BELOW**, and wrote
the lesson down in the code: *"a placeholder that validates is a placeholder that ships"*. The fix
was applied to WHEN and not to WHO.

★★ `D2`'s circularity check could never have caught it. A placeholder names **neither a person nor a
pipeline component** — it is not circular, it is **UNATTRIBUTED**. That is a second, independent
route for an unestablished value to grade as gold, and the third appearance of `DX-20`'s family.

✅ `_is_placeholder()` refuses a value with **no letters at all** plus an exact-match word list.
⚠⚠ Deliberately **no** *"does this look like a real name?"* step: `'张伟'`, `"O'Brien"`, `'M K'` and
`'Ana'` all pass. ★ A blank-detector that rejects real people makes signing feel arbitrary and gets
worked around — so it tests for the **absence of letters**, never for a name-like shape.

## 10.9 ✅ All 8 `E-02` cases signed — and `DX-35` PROVEN pinned

★ Victor signed 21, 22 and 23 on the second pass. The golden set is **28 cases — 20 `E-01`, 8
`E-02` — replaying green**.

★★★ **Case 23 was then tested against a REGRESSED fixture** — the page furniture put back exactly
where `DX-35` found it — and the original failure reproduced on demand:

```
ValueError: 'gd.metric': quoted text is not in the bundle —
            'We have also signed a non-binding term sheet with the State '
```

⚠ That is the difference between a fix and a *pinned* fix. `DX-33` and `DX-35` can no longer be
undone silently: the golden set now fails, loudly, with the same message that cost a $0.6377 call.

## 10.10 ⛔ `DX-39` — `D2`'s guard refuses ordinary FILING prose (OPEN)

⚠ Case 22 would not construct: `CircularGoldenValue` fired because my own template `source` read
*"the **model**'s own note adds…"*. ★ The guard was RIGHT there — `source` must record how the value
was established **from the filing**, and citing what the model said is exactly the provenance `D2`
forbids. It was rewritten from the filing's own sentences.

★★ But probing it revealed the general problem. `GoldenCase` substring-scans `source` too, and
`source` describes **filings**. Measured, 5 of 6 realistic sources are refused:

| `source` | refused for |
|---|---|
| *"Automotive segment revenue table"* | `auto` |
| *"cash generated from operations"* | `generated` |
| *"the company's business model is described in Item 1"* | `model` |
| *"confirmed with the transfer agent's record date"* | `agent` |
| *"the company's ERP system migration disclosure"* | `system` |

⚠⚠ **The damage is the workaround, not the refusal.** The error names a word, so the natural
response is to write vaguer `source` text — and `source` exists to be specific enough to re-check.
★★★ **A guard that punishes specific prose trains people to write vague prose**, degrading the very
field it protects.

★ Word boundaries do not fix it: `generated`, `model`, `system` and `agent` are whole words in real
filings. **Proposed** — keep full substring scanning on `established_by`, and scan `source` for
PROVENANCE PHRASES (*"generated by"*, *"pipeline output"*, *"the model said"*, *"auto-generated"*)
plus the unambiguous vendor names. ⬜ **Not applied**: it changes how `D2` is enforced, and
constitution §5.1 says that choice is the fund manager's.

## 10.11 ⬜ Open — Victor's hand required



1. ✅ **DONE 2026-09-09** — both fixtures re-rendered by Victor via `tools/rerender_fixtures.py
   --apply`; blast radius measured 0; **478 passed, 1 skipped**.
2. ✅ **DONE** — `E-02` recording promoted to `tests_src/fixtures/recordings/run-2026-09-09T074110-mu-e02`
   and re-parsed for $0: 51 items, `X-01` checked 49, 2 `not_found`.
3. ✅ **DONE (5 of 8)** — signed and moved; the set loads **25 cases** and replays green.
4. ✅ **DONE** — all 8 signed; `extraction.pending.yaml` is empty again. `DX-35` verified pinned
   by replaying case 23 against a deliberately regressed fixture.
5. ⬜ **`DX-39` — decide how `D2` scans `source`.** ⚠ It currently refuses ordinary filing prose.
6. ⬜ `extraction` is **2 filings × 2 blocks, 28 cases**. ⚠ Still **13 of 15 `E-blocks` with no
   cases**, and `ranking` / `thesis` have none at all.
