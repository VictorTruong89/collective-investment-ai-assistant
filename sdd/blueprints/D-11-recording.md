# Blueprint — D-11 Recording *(B1 slice only)*

> **Code:** `src/recording/` · **Spec:** `sdd/design/rel6_design/L1-recording.md` · **Seat:** SEAT-5
> **Status:** written 2026-08-23 at **B1** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **PARTIAL DOMAIN.** B1 builds only the three clock-bearing stores. Broker ingestion, order
> reconstruction, instruments, the book, reconciliation and the capital base are **B2 and later** —
> §9 lists what is deliberately absent so a reader does not mistake this for the domain.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-25 *(D-11 §8)* | **The header is read, never assumed** | **RC-41.** The export has **two column layouts** - `TFSA_2` carries 13 columns, inserting `Account name/type/number`; the others carry 10. A positional parser reads `Account name` where `Activity Description` belongs and **silently mis-books every row of that file.** It also hid an activity type: a column-3 survey reported six and **missed `Interest`**, which **RC-13 caught on the first real parse** | *Counting columns* - it works on three files out of four, which is the worst possible failure rate |
| 2026-08-25 *(D-11 §8)* | **Price is NOT in the order key** | **RC-42.** The first attempt included it - one order, one price, seemingly obvious. **BMO fills one order at several prices**: `NVDA 2026-04-29` filled `200 @ 47.68` and `10 @ 47.69`, and keyed on price those become two orders with residuals `9.48` and `0.47`. Grouped, the residual is **exactly 9.95**. So the notional is the per-tranche sum, never `Q_total x p_avg` | *Keying on price* - it reproduces **H-1's own defect inside the parser** rather than inheriting it from the vendor |
| 2026-08-25 *(D-11 §8)* | **The flat fee is measured, and a multiple of it is evidence** | **RC-43.** `9.95` exactly on 100 of 137 orders, **in CAD and USD alike**; `0.00` on BMO's own ETFs; `19.90` once - SPCX, four tranches, **two orders merged**. **The export carries no order id**, so the fee is the only evidence the merge happened, and `implied_order_count` reports it | *Hard-coding 9.95 and asserting it* - RC-15 says the fee is **derived**; a constant is a modelling assumption wearing the word "reality" |
| 2026-08-25 *(D-11 §8)* | **The USD-sell excess is reported, not absorbed** | **RC-44.** Every order above `9.95` beyond price-rounding is a **USD sell** - `MU -23 -> 10.13`, `ARM -70 -> 10.71`, `ENB -220 -> 11.30`. SEC Section 31 is the obvious candidate and **does not fit the magnitudes**, so nothing asserts a cause. Carried as `residual_unexplained` - *a plausible reason attached to an unexplained residual is strictly worse than the honest gap* (D-01 RA-79) | *Widening the tolerance until it passed* - that is absorbing the finding, which is what RA-79 forbids |
| 2026-08-25 *(D-11 §8)* | **A negative derived quantity blocks** | **RC-45.** Replaying the real exports produced `PLTR RESP -520`, `AVGO TFSA_2 -1000`. **Those are not shorts** - they are lots opened before `From=2026-01-01`, whose sells are in the file and whose buys are not. **The cash still balances**, so RC-10 passes and nothing else notices | *Treating them as shorts* - the mandate holds none, and booking one would put a fabricated position into every downstream exposure figure |
| 2026-08-25 *(D-11 §8)* | **An opening snapshot may origin the book - but never `current - activity`** | **RC-47.** A snapshot read off a statement gives the derivation somewhere to start. Back-computing it from current holdings makes them an **input**, so the forward replay reproduces them **by construction** and the check becomes a tautology - RC-45's shape one level up | *Deriving it backwards* - it was the tempting option precisely because it needs nothing from anyone |
| 2026-08-25 *(B5)* | ★★ **`CT-11.4 BookState` built at the head of B5, not in B1** | **BS-15b.** B1's build list names the journal, calibration scoring, the counterfactual store and *"enough of D-11 to hold them"* — **the book was not among them**, and BS-9's amendment binds the SOURCE rather than a milestone (*"lands with D-11's book, before B4"*). **Nobody owned it and B4 shipped without it.** ★ D-05's step 0 is `RECONCILED?` against this contract, so B5 could not begin without it | *Retro-fitting into B1* — nothing earlier needed the book, which is exactly why the gap survived four milestones |
| 2026-08-25 *(B5)* | ★ **`build_book` records a break; `assert_reconciled` raises on one** | RC-10 says *a break raises; it is never absorbed* — but **a break must be RECORDABLE to be reported.** A constructor that refuses to build one leaves nothing to look at, so the refusal lives at the point of USE | *Raising inside the constructor* — the break becomes invisible at exactly the moment someone needs to read it |
| 2026-08-23 | **The capital base is not a B1 or B2 obligation** | BS-9 read *"at B2"* and B2's own build list and done-when name **D-07 only**. `capital_base(as_of)` reads `book_state.nav_base` from a reconciled book neither milestone builds, and its first consumer is D-03's backtest at B4. L3 amended | Building the book in B2 to satisfy the clause — it is most of D-11, scoped nowhere, and exercised by nothing in B2's done-when |
| 2026-08-23 | **Arrival capture not built** (QC-5 stands) | `L3` BS-3 made it *first* among B1's obligations while `L1-recording` §7 had cancelled it the same day. ★ Settled by **structure, not cost**: RC-38 — split tranches fill within seconds at an identical price, so **there is no intra-order gap to measure** | Building it anyway to preserve the option — rejected once RC-38 showed the option was empty, not merely low-value |
| 2026-08-23 | Storage is **JSONL**, not parquet | Small, human-read as often as machine-read, and **a record that needs this codebase to be readable dies with it** | parquet — right for the price panel, wrong for a few hundred rows a human audits by eye |
| 2026-08-23 | An outcome is a **separate append**, not an edit | DN-21. The veto and its outcome are two facts learned at two times; merging them in place makes the second indistinguishable from the first | Updating the row — simpler, and it destroys exactly the evidence the store exists to keep |
| 2026-08-23 | `revise()` **exists in order to raise** | A store with no `revise` is silently satisfied by a caller rewriting the file. One that raises names the rule at the moment someone reaches for it | Omitting the method — the temptation arrives anyway, with no signpost |
| 2026-08-23 | `outcome_h = None` while pending, never `0.0` | Zero is a realised return; pending is an absence. Collapsing them injects a fabricated flat outcome into the comparison (DE-35) | A zero default — the shape that makes an absence look like a finding |

---

# 1. What this domain does, in one paragraph

D-11 is **custody of the fact** — the only domain whose output is checkable against an external
authority. **The B1 slice builds none of that yet.** It builds three append-only stores whose value
is a function of *elapsed time*: the **decision journal** (recordable today), the **counterfactual
store** of vetoed candidates, and the **outcome marking** that makes the two arms comparable. They
produce nothing readable and are built first for that reason — nothing later can recover the
interval in which they were not running.

# 2. The objects and how they flow

```text
   TODAY                              WHEN D-01 / D-12 EXIST
   ─────                              ──────────────────────
   Victor decides                     D-12 vetoes a candidate
        │                                      │
        ▼                                      ▼
   JournalEntry                        VetoedCandidate
   (thesis_version=None)               (outcome_h=None, pending)
        │                                      │
        │ append-only JSONL                    │ append-only JSONL
        ▼                                      ▼
   journal.jsonl  ─────────┐          vetoed.jsonl
                           │                   │
                           │                   │ later: record_outcome()
                           │                   │  → SECOND event, not an edit
                           ▼                   ▼
                    RA-59 calibration    D-12 §6.1 gate effect
                    (needs years)        (needs ~7.8 years)
                           └─────── one Basis ────────┘
                                  (DN-20 / RC-32)
```

| Object | Defined in | Created by | Lives how long |
|---|---|---|---|
| `JournalEntry` | `src/recording/journal.py` | a human decision | for ever (INV-006) |
| `JournalStore` | `src/recording/journal.py` | the entry point | one file |
| `VetoedCandidate` | `src/recording/counterfactual.py` | D-12 (not yet built) | for ever |
| `CounterfactualStore` | `src/recording/counterfactual.py` | the entry point | one file |
| `Basis` | `src/recording/outcomes.py` | whoever marks an outcome | a value |

★ **The object that will surprise a reader: `CounterfactualStore.read()` returns fewer rows than
the file has lines.** The file is an event log (`vetoed`, `outcome`); `read()` folds them into the
current view. `raw_line_count()` exposes the underlying evidence, and the two disagreeing is normal.

# 2a. ★ As-built — the record that was never written *(2026-08-26/27)*

⚠ **RC-33 has required run storage since v0.5.0.** `ManifestStore` and
`JournalStore` were both built and **neither was ever called**: every manifest,
recommendation, card and thesis evaporated at process exit, and **P6 was unmet**.

| Module | What it is | ⚠ Open / known-limited |
|---|---|---|
| `src/recording/artifacts/store.py` | CT-11.7 — a directory per run, append-only | ★ `runs.parquet` is **derived and rebuildable**; the directories are the record |
| `src/recording/book/load.py` | the four BMO accounts → `BookState` | ⏸ **AB-3/RC-58** — one unpriceable account withholds all four, *because a book-wide figure over the rest would be wrong, not partial* |

## ⚠⚠ Open question carried to `L6-as-built-remaining.md`

**RC-61 thesis reuse.** A thesis is stored under its `bundle_hash` and reused
(**$1.34/run otherwise**). ★ This does **not** harm RM-1: its k runs happen
*inside one authoring event*, and GW-8 sets `temperature = 0`. ⚠ Release 7 should
re-check that argument if sampling is ever reintroduced.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 1 | validate the entry | `src/recording/journal.py::JournalEntry.__post_init__` | ★ A blank rationale is caught at construction, not at write — an invalid value should not exist even briefly | `ValueError` |
| 2 | assign the ordinal | `src/recording/journal.py::JournalStore.append` | CT-11.6 keys on `(date, ordinal)`; **the store assigns it** so two callers cannot pick the same one | — |
| 3 | append one line | same | JSONL, opened in `"a"` | — |
| 4 | veto recorded | `src/recording/counterfactual.py::CounterfactualStore.append` | Duplicate key ⇒ a revision in disguise (DN-21) | `AppendOnlyViolation` |
| 5 | outcome, later | `src/recording/counterfactual.py::CounterfactualStore.record_outcome` | ★ a **second event**, never an edit | `AppendOnlyViolation` on a second outcome |
| 6 | compare arms | `src/recording/outcomes.py::Basis.assert_comparable` | **DN-20** — must run *before* differencing two returns | `OutcomeBasisMismatch` |

# 4. ★ The mathematics

### Realised simple return

| | |
|---|---|
| **Implemented in** | `src/recording/outcomes.py::mark_to_market` |
| **Formula** | ```python\nreturn (exit_px - entry_px) / entry_px\n``` |
| **Units** | prices in the same currency → dimensionless. ⚠ **Not `Money`** — a same-currency ratio leaves the Money type (MO-8) and a cross-currency one is forbidden (MO-9) |
| **Domain / range** | `entry_px != 0`. Zero raises rather than returning infinity (P5) |
| **Why this form** | Simple, not log: the two arms are **differenced**, and simple returns difference into something a reader can interpret as "how much better". Log returns compound cleanly but their difference is not the quantity D-12 §6.1 asks about |
| **Alternatives rejected** | log return — better for compounding, wrong for a two-arm comparison. Excess over benchmark — ⚠ **needs M-6?, which is not adopted**; adding one here would be D-11 choosing a benchmark, which is not its call |
| **Sensitivity** | Entirely to `basis`. ★ **A 1w-vs-1m mismatch produces a difference that is mostly horizon and reads as gate skill** — which is why `Basis` is a required keyword |
| **★ Worked example** | acted-on `100.00 → 104.00` = **+0.04**; vetoed `100.00 → 96.90` = **−0.031**; gate effect on this pair = **+0.071**, *and only because both were marked at `("1m","open")`* |
| **Known-wrong** | none known |

# 5. The logic decisions

| Decision | Where | What it does | Why this way | To change it |
|---|---|---|---|---|
| Ordinal assigned by the store | `JournalStore.append` | `len(self.read())` | Callers cannot collide | — |
| Duplicate veto = violation | `CounterfactualStore.append` | raises on repeated `(ticker, as_of)` | A second write for one key is a revision wearing an append | — |
| Corrupt line raises | both stores' readers | no skip, no warn-and-continue | ⚠ A silently dropped row is a hole in the sample that **nothing downstream can see** | — |
| `Basis` is a required kwarg | `mark_to_market` | no default horizon | ★ A default is how two arms end up on different bases without anyone choosing | — |

★ **There is no magic number in this slice.** Horizons come from the caller; commission and prices
belong to B2.

# 6. Configuration — where every knob lives

| Knob | Where | Note |
|---|---|---|
| journal path | constructor argument | ⚠ **No config key yet** — the entry point that owns it is B3's |
| counterfactual path | constructor argument | as above |

★ Deliberately un-configured at B1: **CF-2 says config is read once at the edge and passed inward**,
and the edge does not exist yet. Inventing a key now would place it in D-00 with no reader.

# 7. Inputs and outputs

| Direction | Contract | Shape | Producer / consumer | If malformed |
|---|---|---|---|---|
| in | `CT-11.6` | `JournalEntry` | a human, today | `ValueError` at construction |
| in | `CT-12.2` | `VetoedCandidate` | D-12 (B4+) | `ValueError`; missing gates rejected |
| out | JSONL | one event per line | RA-59, D-12 §6.1 | reader raises |

# 8. Failure behaviour

| Failure | Detected where | Behaviour |
|---|---|---|
| blank rationale | `JournalEntry.__post_init__` | raise |
| no binding gate | `VetoedCandidate.__post_init__` | raise |
| revision attempted | `revise()` on either store | `AppendOnlyViolation`, naming INV-006 |
| duplicate veto / outcome | `CounterfactualStore` | `AppendOnlyViolation` |
| mixed basis | `Basis.assert_comparable` | `OutcomeBasisMismatch` |
| corrupt line | either reader | raise — never skip |

# 9. What this domain deliberately does NOT do — **and what B1 leaves unbuilt**

| Not in the B1 slice | When |
|---|---|
| broker ingestion, tranche grouping (H-1), instruments (H-2), FX prose parsing (H-4) | **B2** |
| the book, reconciliation, `nav_base` | B2 |
| ★ **the capital base** (`QA-63`/RC-19) | ⚠ **NOT B2** — corrected 2026-08-23. BS-9 said *"read from D-11 at B2"* while B2's build list names **D-07 only**; the rule binds the SOURCE, not the milestone. It lands with the book, before **B4**'s backtest consumes it |
| ~~arrival capture~~ | ⚠ **never** — QC-5, CT-11.5 tombstoned |
| calibration *scoring* (RA-59) | ★ the **store** is here; the scoring is D-01's and needs theses (B4) |
| rendering, risk metrics, sizing | D-09 / D-05 / D-06 — never here |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect | Tracked as |
|---|---|---|---|
| **10.1 — two of three arms have no producer yet** | ⚠ expected | The counterfactual store and outcome marking are **exercised only by tests**; D-12 and D-01 do not exist. **Only the journal accrues real data today** | L3 **BS-3b** |
| **10.2 — `read()` is O(n) per append** | low | `JournalStore.append` calls `read()` to get the next ordinal. At a few hundred entries this is irrelevant; at 10⁵ it is not | — |
| **10.3 — no `Money` in this slice** | ⚠ medium | Returns are floats (correct, MO-8) but **no monetary value is stored yet**. When B2 adds cash, RC-23 applies and every amount becomes `Money` | RC-23 |
| **10.4 — the journal has no schema version** | ⚠ medium | A `CT-11.6` field added later cannot be told apart from a corrupt row by the reader. ★ **For an append-only store meant to last years, that is the defect most likely to bite** | ★ **new — no ID yet** |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | ACs and their tests | `tests_src/test_recording_b1.py` — 19 cases, each docstring names its rule |
| 2 | ★ **Break it and confirm red** | In `src/recording/journal.py::JournalStore.revise`, replace the raise with `pass`. `test_editing_an_existing_entry_raises` must fail — that is INV-006, and it is the rule with the strongest temptation behind it |
| 3 | The worked example (§4) reproduces | `python -c "from src.recording.outcomes import Basis, mark_to_market as m; b=Basis('1m','open'); print(m(entry_px=100.0, exit_px=104.0, basis=b), m(entry_px=100.0, exit_px=96.9, basis=b))"` |
| 4 | Append-only is real, not claimed | append a veto, record its outcome, then `raw_line_count()` — **2 lines, 1 folded row** |
| 5 | ★ **Checked against external truth?** | ⚠ **No — self-consistency only.** D-11's defining property is that it reconciles against the broker, and **the B1 slice reconciles against nothing.** That arrives at B2 with ingestion |

★ **Check 5 is the honest limit.** This slice is the part of D-11 that cannot be reconciled, built
first because its clock cannot be restarted.

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-recording.md` | CT-11.6, RC-24, RC-31…RC-39, §7 (QC-5), AC-11.15/11.18 |
| `sdd/design/rel6_design/L1-decision.md` | CT-12.2, DN-19/20/21 — the counterfactual arm |
| `sdd/design/rel6_design/L3-build-sequence.md` | B1's scope; **BS-1**, BS-7, **BS-3a/3b** |
| `sdd/design/rel6_design/L1-fundamental-analysis.md` | RA-59 — what the journal eventually feeds |
| `sdd/specs/constitution.md` | P5 · INV-006 (append-only) |
