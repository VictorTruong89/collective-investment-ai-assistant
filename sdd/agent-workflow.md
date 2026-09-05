# How an AI agent turns these specs into code

> **Audience:** Victor, learning SDD — and future-Victor validating work an agent already did.
> **Tier:** process explainer. **Binds nothing.** The constitution, the L-specs and `ownership.yaml`
> bind; this file only explains how they are used.
> **Companion to:** [`README.md`](README.md) (the tier map) · [`specs/constitution.md`](specs/constitution.md) §5
> (the change process) · [`design/rel6_design/L3-build-sequence.md`](design/rel6_design/L3-build-sequence.md) (what order to build in).

---

# 1. Three misconceptions worth clearing first

**① "The spec contains the code."** It does not, and it must not. A spec says **what must be true**;
the code is one way of making it true. If the spec contained the code you would have written the
code twice and would now maintain two copies that can disagree.

**② "The agent reads the specs."** It reads a **routed subset** — usually two or three files. Which
ones is decided by the *path it is about to edit*, via `specs/ownership.yaml`, and a `PreToolUse`
hook **refuses the edit** until it has actually read them. Nobody reads twenty-two documents.

**③ "You implement a domain."** You never implement `D-01`. You implement **`AC-1.3`**. The unit of
work is one acceptance criterion, because that is the unit that can be shown to be done.

```text
   ┌──────────────────────────────────────────────────────────────┐
   │  THE SPEC IS A CONSTRAINT SET, NOT A BLUEPRINT.              │
   │                                                              │
   │  "An extracted value absent from its cited span raises"      │
   │   ↑ this is testable, and it forbids a large family of       │
   │     wrong implementations without naming the right one.      │
   │                                                              │
   │  The agent's job: write the SMALLEST thing that satisfies    │
   │  every constraint that applies. Not the cleverest thing.     │
   └──────────────────────────────────────────────────────────────┘
```

---

# 2. The loop, followed end to end on one real criterion

Take **`AC-1.3` — *"An extracted value absent from its cited span raises (RA-6)"*.**

### Step 0 — Routing: which specs am I allowed to have opinions about?

The agent intends to touch `src/fundamental/filings/`. `ownership.yaml` says:

```yaml
- globs: ["src/fundamental/**"]
  spec: sdd/design/rel6_design/L1-fundamental-analysis.md
```

So the required reading is **`specs/constitution.md`** (always) plus **`L1-fundamental-analysis.md`**.
`.claude/hooks/sdd_gate.py` blocks the write until both have been read **in this session** — a fresh
conversation must read them again, because context does not carry over and neither should the
permission.

### Step 1 — Find the acceptance criterion, and its **tier**

§15 lists `AC-1.3`. Constitution §4 maps every AC to a **test tier**, and the tier determines the
*shape* of the test:

| Tier | Shape | Example here |
|---|---|---|
| data contract | schema assertion | a price panel has these columns |
| invariant / property | ★ holds for **all** inputs | no look-ahead, ranges |
| golden / characterization | output frozen against a fixture | `OhlcvFeatureEngineer` |
| API contract | request/response + status | 409 on prompt drift |
| metric gate | statistical regression | backtest `RankICIR ≥ threshold` |
| unit | one function | ★ **AC-1.3 lives here** |
| integration | multi-component flow | the dual-pick run |

⚠ **Getting the tier wrong is the most common quiet failure.** An invariant AC given a single
example test *looks* green and proves almost nothing.

### Step 2 — Read the rules the AC cites, not just the AC

`AC-1.3` cites **RA-6**. RA-6 says the check is *"present in, or arithmetically derivable from, the
cited span"*, and **§7 X-01 adds that this check must be deterministic — not an LLM call.** That
second constraint is in a different section and would be missed by reading only §15.

★ **This is the skill: an AC is an index into constraints, not the whole constraint.**

### Step 3 — Write the test that fails **for the right reason**

```python
def test_extracted_value_absent_from_span_raises():
    """AC-1.3 · RA-6 — an extracted value not in its cited span raises."""
    span = Span(accession_id="0000723125-26-000042", text="gross margin was 58.1%")
    with pytest.raises(ExtractionUnverified):      # RES.EXTRACT.UNVERIFIED
        verify(Extraction(value=0.612, metric="gross_margin", span=span))
```

★ **Run it before writing the code.** A test that passes before the feature exists is testing
nothing, and this is the single cheapest bug-catch in the whole method.

### Step 4 — The smallest code that passes

Not a framework. Not an abstraction "for later". If a second case needs it, the second case pays for
it.

### Step 5 — Run the **whole** suite

```
/home/victor/anaconda3/envs/tf_gpu/bin/python -m pytest tests/ -q
```

★ Not just the new test. The suite is the regression net; a green new test beside three newly-red
old ones is a net loss.

### Step 6 — Record it

Add the row to the spec's §8 traceability table: `AC-1.3 → tests/test_extraction.py::test_… → src/fundamental/filings/verify.py`.
**An AC with no row is not done, however green the test is** — because nobody can find it later.

---

# 3. ★ Four domains, four completely different relationships between spec and code

**This is the part that answers "how does the agent find the right algorithm."** The answer is
different in each domain, and knowing which situation you are in is most of the work.

| Domain | What the spec gives you | What the agent must supply | Where the answer actually comes from |
|---|---|---|---|
| **D-12 Decision** | ★★ **the algorithm itself** | an encoding | **the spec, literally** |
| **D-01 Fundamental** | ★ **the sequence, and why each step sits where it does** | prompt composition + deterministic checkers | the spec + the prompt registry |
| **D-05 Risk** | the **measures** and what they mean | ⚠ **the sequence — which is not written down** | ★ **nowhere yet. The spec must be amended first** |
| **D-03/D-04 Quant** | ★ the **evaluation protocol** and the constraints | the model — ★ **by measurement, never by choice** | **D-10 Experiments** (currently parked) |

## 3.1 D-12 Decision — the one place the spec *is* the algorithm

`L1-decision.md` §5 states that the verdict algebra is a **bounded meet-semilattice** over
`BUY > HOLD > SELL`, and its module map has `algebra/  # the verdict lattice — meet, gate map, laws`.

That is not a description of an algorithm; it **is** the algorithm. Consequences for codegen:

- **Composition is `meet`** — take the greatest lower bound of the inputs. There is nothing to design.
- ★ **P3 ("verdicts gate, never upgrade") becomes a type-level guarantee, not a runtime check.** A
  meet cannot return something more aggressive than its inputs. The property is structural.
- **The tests are property tests, not examples**: idempotence, commutativity, associativity, identity,
  monotonicity. Five laws, five tests, and they hold for *all* inputs rather than the three you
  thought of.
- **§5.5 is stated algebraically too**: *"the identity element must not be reachable by omission"* —
  i.e. a missing gate must not silently mean PASS.

★ **When a spec reaches this level of precision, the agent has almost no freedom, and that is the
point.** You should expect near-identical code from two different agents.

## 3.2 D-01 Fundamental — the sequence is stated; the "algorithms" are mostly prompts

`L1-fundamental-analysis.md` **§4A** gives the eleven-step ladder for a fresh analysis (align →
assemble → extract → verify → Stage A → **freeze** → Stage B → Stage C → Stage D → verify → project
→ emit), and — more importantly — a column saying **what forces each step to be where it is**:

- extraction before judgement, because RA-7 says judgement consumes *checked facts*, never raw documents
- the freeze between Stage A and B, because RA-14 says you cannot un-see a price
- falsifier before verdict **with a persisted write between them**, because otherwise the ordering is nominal

So the agent does **not** invent an order. It implements a stated one and the *reasons* tell it which
reorderings are forbidden.

The "algorithms" split in two:
- **Judgement** → a composed prompt from `L1-fundamental-analysis-master-prompt.md`. Codegen here is
  *composition and validation*, not logic.
- **Verification** → ★ **five of seven checks are explicitly marked "must NOT be a prompt"** — value-in-span
  is `in`, the lint is a wordlist, length is `len()`.

> ⚠ **§4A did not exist until 2026-08-21.** Before that, an agent asked to "build D-01" would have
> had 100+ rules and **no stated order** — and would have invented one. **That is exactly the
> situation D-05 is in today.**

## 3.3 D-05 Risk Management — ⚠ the honest gap, and what an agent must do about it

`L1-risk-management.md` is a good spec. It has §5 exposure, §6 (*"VaR is nearly useless here — and
saying so is the useful part"*), §7 behavioural flags for M-3/M-4, §8 the `P` and `D` factors D-06
needs, §9 stress testing, contracts, and an API surface.

⚠ **It contains no stated execution sequence.** Searching it for a workflow, a step order or a
"runs first" returns **zero matches**. So an agent asked to build D-05 faces questions the spec does
not answer:

- Does exposure compute before or after the flags — and do the flags read the exposure?
- Is stress testing part of the daily run or a separate cadence?
- When the book fails to reconcile, does risk compute on a stale book, or refuse?
- Are `P` and `D` computed every run, or on demand when D-06 asks?

**The correct agent behaviour is to STOP.** Constitution §5.1: a change with no covering AC means
**the spec is amended first**. Improvising a sequence and shipping code that passes a test the agent
also wrote is the failure this whole method exists to prevent.

★ **You saw this happen four times in one session** — §4A (runtime workflow), §10A/§10B (calendar and
events), §10C (sector file), §4B (the relay) were all written *because the code could not be written
without them*. **A spec growing under an implementation request is the process working, not a delay.**

## 3.4 D-03 / D-04 Quant — ★★ the model cannot come from the spec, and a spec that named one would be wrong

This is the sharpest of the four, and the most counter-intuitive.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A SPEC CANNOT SAY "USE LIGHTGBM".                               ║
║                                                                  ║
║  Whether LightGBM beats a linear model on this universe, at      ║
║  this horizon, with this feature set, is an EMPIRICAL question   ║
║  about data that changes. A spec that fixed the answer would     ║
║  be asserting a measurement it never made — and would have to    ║
║  be amended every time the measurement moved.                    ║
║                                                                  ║
║  ★ So the spec fixes the QUESTION and the SCORING, and lets      ║
║    measurement pick the model.                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

**What the spec DOES fix, and binds absolutely:**

| Fixed | Where |
|---|---|
| ★ **The schema** — label set, nomination shape, the `HorizonSet` (1w/1m/1q) | `CT-2.3`, `CT-3.4`, D-03 §on horizons |
| ★ **The feature contract** — train and inference build features by the *same code path* | **INV-4**, `feature_engineer/ml_features/` |
| **No look-ahead** — a feature for date *t* uses only data with timestamp ≤ *t* | **INV-1**, property test |
| **Determinism** — same data + same config ⇒ byte-identical output | **INV-2**, golden test |
| **Ranges** — `rsi_14 ∈ [0,100]`, `prob_up ∈ [0,1]` | **INV-3** |
| ★ **The evaluation protocol** — CPCV, purging, walk-forward, the metric-gate tier | D-03 §7, `cpcv.py` |
| ★ **Preconditions on choosing at all** — §5.4a is literally *"three corrections that precede any architecture choice"* | D-03 §5.4a |

**What it deliberately leaves open:** the architecture, the hyperparameters, the blend.

★ **So the answer to "how does the agent find the proper ML model" is: it does not find one — it
builds the harness that lets a measurement find one.** That harness is **D-10 Experiments**, which is
**parked** by your decision until the pipeline runs stably.

⚠ **Which means the honest state today is:** carry the rel5 choice forward (the three-model bundle —
ranker + regressor + classifier), **record it as an inherited, unvalidated default**, and do not
present it as a spec decision. It was chosen by a 2026 sweep on a 30-name universe, and
`L2-signal-combination.md` **CB-23** already records that `IC₀₃` — the number that would justify it —
is currently **unfalsifiable**.

> ★ **Schema and model are opposites here.** The schema is binding and an agent may not deviate. The
> model is provisional and an agent may not pretend otherwise. Confusing the two in either direction
> is the mistake.

---

# 4. What the agent does when the spec is silent

**Three legal moves. One illegal one.**

| Situation | Move |
|---|---|
| No AC covers the change | ★ **Amend the spec first** (constitution §5.1). This is a real deliverable, not overhead |
| Building next to untested legacy code | **Characterization test first** (§5.2) — freeze what it does *before* touching it, even if what it does is wrong |
| The choice is genuinely the user's | **Stop and ask.** Ordering questions, thresholds, mandate calls |
| — | ✗ **Improvise, then write a test that agrees with the improvisation** |

⚠ **The illegal move is dangerous precisely because it produces green tests.** The agent wrote the
code *and* the test, so of course they agree.

---

# 5. ★★ How YOU validate what an agent produced

The structural problem, stated plainly:

```text
   THE AGENT WRITES BOTH THE TEST AND THE CODE.
   A PASSING TEST THEREFORE PROVES CONSISTENCY, NOT CORRECTNESS.
```

**Seven checks, cheapest first.** You do not need to read the implementation for most of them.

| # | Check | How |
|---|---|---|
| **1** | **Does the test name its AC?** | `grep -rn "AC-1.3" tests/` — the docstring must cite it (constitution §6). No citation ⇒ nothing links the code to a requirement |
| **2** | **Is it in the right tier?** | An **invariant** AC with a single-example test is a silent downgrade. Property/invariant ACs want generated inputs, not one case |
| **3** | ★★ **Mutation check — the strongest one** | **Deliberately break the code and confirm the test goes red.** Flip a comparison, drop a clause, return early. ★ *This repo already does it:* `test_ohlcv_features_golden.py` is recorded as *"mutation-verified against four independent changes"*, and the INV-4 parity test as *"mutation-verified, 5 mutations"* |
| **4** | **Did the AC exist before the code?** | `git log --follow` on the spec vs the source file. ⚠ An AC added in the *same commit* as the code it blesses is a rationalisation |
| **5** | **Is the traceability row there?** | The spec's §8 table. Missing row ⇒ un-findable later |
| **6** | **Does the audit pass?** | `python tools/sdd_audit.py` — 9 structural checks: dangling rule refs, duplicate definitions, struck rules with no successor, stale parent versions, orphan specs, contract-field citations |
| **7** | ★ **Is anything checked against EXTERNAL truth?** | The deepest one. A suite can be fully self-consistent and uniformly wrong. **F3 Tier 1 "reality probes"** exist for this — e.g. D-07 §6A.4 requires a *live* FMP fetch asserted against a known-answer set |

### Red flags, in rough order of how much they should worry you

1. ⚠ **A test that would pass with the feature deleted.** Check 3 catches it.
2. ⚠ **An AC and its code in one commit.** The spec was written to fit.
3. ⚠ **A confident docstring on untested logic.** ★ This repo's own scar: `_cumulative_fys` had a confident docstring, a passing test, and a **41.5% error**.
4. ⚠ **A number with no stated source or check.** Three arithmetic errors were found in *reviews* this month; each looked authoritative.
5. ⚠ **"Improved" alongside "moved."** L4's migration classes forbid it — a move commit changes **zero bytes**, or git records a rewrite and the review becomes impossible.
6. ⚠ **A new abstraction with one caller.** The smallest thing that passes, not the most general.

### Three questions that catch most of it

> **"Which AC is this?"** — no answer means it should not have been written.
> **"What breaks if I delete this line?"** — no answer means the test does not cover it.
> **"What is this checked against — our own data, or the world?"** — self-consistency is not correctness.

---

# 6. What order to build in

Not covered here — it has its own document:
**[`design/rel6_design/L3-build-sequence.md`](design/rel6_design/L3-build-sequence.md)**, milestones
**B0…B7**, with the D-01 slices at **§3A (B4.1…B4.7)**.

★ Its central argument is counter-intuitive and worth knowing: three obligations (calibration
scoring, the counterfactual store, arrival-quote capture) **produce nothing for years** and are
therefore built **first**, because their value is a function of elapsed time and **no later effort
can buy back the interval**.

---

# 7. One page, for the wall

```text
   ROUTE      ownership.yaml decides which specs. The hook enforces it.
   FIND       an AC — not a domain. Note its TIER.
   READ       the rules the AC cites. They live in other sections.
   FAIL       write the test. Run it. It must fail first, for the right reason.
   PASS       the smallest code. No frameworks for hypothetical callers.
   SUITE      all of it, not just the new test.
   TRACE      the §8 row. No row, not done.

   SILENT?    Spec has no AC  → amend the spec FIRST
              Legacy nearby   → characterization test FIRST
              Victor's call   → stop and ask
              Never           → improvise and test the improvisation

   VALIDATE   1 does the test cite its AC?
              2 right tier?
              3 ★ break the code — does it go red?
              4 did the AC predate the code?
              5 traceability row?
              6 tools/sdd_audit.py
              7 ★ checked against the world, or only itself?

   FOUR SHAPES OF "FIND THE ALGORITHM"
     D-12   the spec IS the algorithm      → encode it
     D-01   the spec gives the SEQUENCE    → follow it, compose prompts
     D-05   the spec gives MEASURES only   → ⚠ amend before coding
     D-03   the spec gives the PROTOCOL    → measurement picks the model,
            and the schema is binding         not the spec — and not you
```
