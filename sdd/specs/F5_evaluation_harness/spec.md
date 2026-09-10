# F5 — Evaluation harness

> **Spec-ID:** F5 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §B.4 · lecture §3.6 ·
> [`../../questions.md`](../../questions.md) `QR-13`, `QR-19`
> **Milestone:** `MS-4` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces **`PG-4`**, **`PG-5`/`PG-5.1`**; inherits `P5`, `ST-2`, `P7`.
> **Capability:** `C6` — ★ **without it, `C1`–`C5` are demonstrations rather than results.**
> **Domain:** D-14 `src/evaluation/`, seat 9.
>
> ✅ **Approved 2026-09-04.** `Q1`–`Q5` adopted as `D1`–`D5` (§7) — ★ **read §7 before changing §5 or
> §6.** ⚠ `D2` is the one with a standing human obligation: **the fund manager establishes every golden
> value**, and no pipeline component may appear in `established_by`.

---

## 1. Goal & why

**One harness that measures whether anything in this system actually works — built once, shared by
both portfolio lanes (`PG-4`).**

★ **This is the spec that makes the project's central claim checkable.** `vision.md` §1.1 promises a
system that *"can explain and defend every recommendation — and measure whether any of it helps."*
Everything else produces the recommendations and the explanations; F5 produces the evidence.

**Why it is spec-governed rather than research-exempt** (`QR-13`): D-14 inherits D-10's *structural*
rule — imports anything, imported by nothing (`ST-2`) — but **not** its spec exemption. The exemption
protects exploration; this is not exploration. It is an **instrument other decisions depend on**:
`F7a`'s output gates `F6b`, and its calibration numbers back the portfolio thesis.

> ⚠ **A measurement instrument nobody verified is how you get confidently wrong numbers** — and under
> `PG-4` an error here is wrong in *both* lanes, silently.

**What it must not duplicate.** `src/quant/metrics/` already computes `ic.py` and `breadth.py`, and the
IC standard error is `QR-5`'s upstream change to `src/quant/gates/metric_gate.py`. ⚠ **F5 consumes
those; it does not re-implement them.** A second IC implementation that disagrees with the first is
precisely the failure this spec exists to prevent.

## 2. Scope / non-goals

**In scope**
- **Golden sets** — known-correct fixtures with their provenance.
- **Grounding metrics** — citation rate, unbound-claim count, span precision.
- **Calibration** — reliability curve, ECE, Brier and its decomposition.
- **Faithfulness** — deletion / insertion curves, attribution stability.
- **Regression** — a suite that reds when a *prompt* changes behaviour.
- The **Tier-A / Tier-B split** (`PG-5.1`) as a structural property of the harness.
- ★ **Sample size and selection count on every published figure** (`QR-19`'s lesson, generalised).

**Non-goals (this spec)**
- ✗ **Re-implementing IC, breadth, or the IC standard error.** Consumed from `src/quant/metrics/` and
  `metric_gate.py`. The `QR-5`/`QR-19` change is upstream work (`MS-0.2`).
- ✗ **The deliberation study itself** — that is `F7a` (Tier A) and `F7b` (Tier B). F5 supplies the
  machinery they run on.
- ✗ **Deciding promotion.** `metric_gate.py` gates models upstream; F5 measures and reports.
- ✗ **Producing explanations.** `F4` produces them; F5 tests whether they are faithful.
- ✗ **Collecting outcomes.** `F2`'s `CT-2.6` links `decision_id` to a realised outcome; F5 reads that
  join.
- ✗ **One-off exploratory studies** — see `Q1`; the metric/study boundary is the open question `QR-13`
  flagged.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | CI, every build | golden set | `src/evaluation/regression/run.py` |
| T2 | After a run, on its outputs | `run_id` | `src/evaluation/metrics/grounding.py` |
| T3 | Periodically, over resolved outcomes | date range | `src/evaluation/metrics/calibration.py` |
| T4 | A Tier-A study asks for a comparison | two arms of `CapabilityDelta` | `src/evaluation/studies/compare.py` |
| T5 | A prompt or model id changes | previous baseline | `src/evaluation/regression/run.py` |

## 4. Behaviour & reuse (the lean "how")

- **Consume, never re-derive.** IC and breadth come from `src/quant/metrics/`; outcomes come from
  `F2`'s join; provenance comes from `F1`. F5 owns only what nothing else computes.
- **Tier A needs no outcomes; Tier B does** (`PG-5.1`). ⚠ The harness keeps them **structurally
  separate**, so a Tier-A result can never be presented as evidence about decision quality.
- ★ **Every published figure carries `n` and, where a model or variant was selected from candidates,
  the selection count.** `QR-19` established that a significance figure with an unstated selection
  count is not interpretable; F5 generalises that to every metric it emits.
- **Coverage is not calibration.** ⚠ Upstream `AB-1` defines `confidence := evidence_coverage` — a
  measure of *how much the system looked at*, not *how often it is right*. F5 computes both and **they
  never share a field name**.
- **A metric is checked against a known answer.** Every metric implementation has a fixture whose
  correct value is derived independently — ★ this is the "who checks the checker" obligation that
  `QR-13` turned into a spec.
- **The harness imports domains; nothing imports the harness** (`ST-2`, inherited from D-10's shape).
- **Fail loud on insufficiency.** ⚠ A metric asked for on too small a sample returns an explicit
  insufficiency, never a number (`P5`).

## 5. Contracts (inline)

**CT-5.1 — `MetricResult`** (every figure the harness emits):
```json
{ "metric": "str — e.g. 'grounding_rate', 'ece', 'brier'",
  "value": "float | null — null when insufficient",
  "n": "int — ★ sample size, always present",
  "selection_count": "int | null — candidates the subject was chosen from (QR-19)",
  "tier": "A | B — PG-5.1",
  "insufficient_reason": "str | null",
  "computed_at": "iso8601",
  "inputs_ref": "str — golden set id or run_id range" }
```
Rules: `value` and `insufficient_reason` are mutually exclusive and one is always present.
⚠ `n` is **never optional** — a figure without its sample size is not publishable.

**CT-5.2 — `GoldenCase`:**
```json
{ "case_id": "str", "kind": "extraction | thesis | ranking",
  "input_ref": "str — '<run_id>/<call_id>', the F2 recording this case grades",
  "expected": "object",
  "source": "str — how the expected value was established",
  "established_at": "iso8601", "established_by": "str" }
```
⚠ `source` is required: a golden value whose derivation is unrecorded cannot be re-checked, and will
eventually be trusted for the wrong reason.

⚠⚠ **`input_ref` names a RECORDING, not a filing** *(clarified `A3` 2026-09-05, `DX-21`)*. It read
*"the fixture"*, which `run.py` had always read as *"the recording"* — and only one of those is
implementable. ★ A filing is an **input**; comparing it to `expected` would mean *producing* an
extraction from it, i.e. an LLM call, which `D5` forbids in CI. The recorded response is the only
artefact that is both a product of the system and available offline.

> ⚠ The filing still matters — it is how a **human** re-checks the case (`source` points at it, and
> the text lives in `tests_src/fixtures/filings/`). It is simply not what the **runner** resolves.

⚠⚠ **`expected` must be established — an empty one raises** *(added `A2` 2026-09-05, `DX-20`)*. A case
whose `expected` is empty is one the fund manager has not finished writing, and it did not merely load:
`run_regression` compares with `==`, so any run producing nothing matched it and the case reported
**PASS**. ★ *Absent* stays expressible, but only **explicitly** — `expected: {status: NOT_FOUND}` —
because **"the document does not say" is a finding; "I have not looked yet" is not.**

**CT-5.5 — the golden set on disk** — added `A1` 2026-09-05:
```text
tests_src/fixtures/golden/<kind>.yaml       # extraction.yaml · ranking.yaml · thesis.yaml
```
```yaml
cases:
  - case_id: nvda-2026q2-revenue
    input_ref: filings/NVDA_2026Q2_10Q.txt
    expected: {revenue_usd_m: 30040}
    source: "read from the 10-Q, page 4, 'Total revenue'"
    established_at: "2026-09-05"
    established_by: "Victor Truong"
```
Rules: **one file per `kind`**; `case_id` unique across the whole set; every field of `CT-5.2`
required. ⚠ **Version-controlled** — a golden set that is not versioned cannot show drift, which is
the only thing a regression suite measures.

⚠⚠ **The golden set is EXCLUDED from the `MS-9.1` public mirror.** `expected` values for `ranking`
and `thesis` are the fund's judgement, i.e. the strategy `QR-12` withholds. ★ Extraction cases are
public facts, but splitting the directory by sensitivity would put the decision in a filename — so the
whole set stays local and the mirror ships the machinery without the answers.

**CT-5.3 — `CalibrationResult`** (extends `CT-5.1`):
```json
{ "bins": [{"lower": "float", "upper": "float",
            "n": "int", "mean_confidence": "float", "observed_rate": "float"}],
  "ece": "float", "brier": "float",
  "brier_decomposition": {"reliability": "float", "resolution": "float",
                          "uncertainty": "float"} }
```

**CT-5.4 — `ComparisonResult`** (Tier-A arms, consumed by `F7a`):
```json
{ "arm_a": "str", "arm_b": "str", "metric": "str",
  "value_a": "float", "value_b": "float", "n_a": "int", "n_b": "int",
  "pre_registered_rule": "str — ★ stated BEFORE the run (PG-5.1)",
  "verdict": "PASS | FAIL | INSUFFICIENT" }
```

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-5.1** *(★ every metric is checked against a known answer — `D2`)* — **Given** any metric
  implementation, **when** run on its fixture, **then** it returns the expected value within tolerance;
  **and** that fixture's `source` is non-empty and its `established_by` names **a person, never a
  pipeline component**. → *golden / characterization, one per metric.* (`QR-13`, `D2`)
  > ⚠⚠ **`D2`'s reason, because the alternative looks better.** Seeding golden values from the system's
  > own output would give more cases and a permanently green suite — while **certifying the system
  > against itself**, so any regression silently becomes the new gold. ★ For `thesis` the correct answer
  > is a **judgement**, and the case records whose it was rather than pretending to objectivity.
- **AC-5.2** *(★ `n` is never absent)* — **Given** any `MetricResult`, **when** emitted, **then** `n`
  is present and > 0, or `value` is null with an `insufficient_reason`. → *data contract.*
- **AC-5.3** *(selection count travels with the figure)* — **Given** a subject chosen from `k > 1`
  candidates, **when** a metric about it is emitted, **then** `selection_count == k`. → *data
  contract.* (`QR-19`)
- **AC-5.4** *(★★ tiers do not mix)* — **Given** a Tier-A result, **when** any report is assembled,
  **then** it is never presented as evidence about decision quality; a Tier-B claim requires
  `tier == "B"` inputs. → *invariant / property.* (`PG-5.1`)
- **AC-5.5** *(coverage ≠ calibration)* — **Given** both are computed, **when** either is emitted,
  **then** they carry distinct metric names and neither is derived from the other. → *data contract.*
  (upstream `AB-1`)
- **AC-5.6** *(grounding rate is real)* — **Given** a thesis with bound and unbound claims, **when**
  grounding is computed, **then** the rate equals verified-claims ÷ factual-claims, and
  `unbound_claim_count` is reported alongside. → *unit.* (`AP-2`)
- **AC-5.7** *(a prompt change reds the suite — `D5`)* — **Given** a green regression baseline, **when**
  a prompt's text changes such that behaviour changes on the golden set, **then** the suite fails and
  names the diverging cases — **replaying `F2`'s recorded responses, making no live call**.
  → *integration.*
  > ⚠ Live calls in CI were rejected: cost, flakiness, and **a suite that fails when a vendor is down
  > teaches people to ignore red**, which destroys it permanently.
- **AC-5.18** *(★ a golden case resolves to its recording — `A3`, `DX-21`)* — **Given** a case whose
  `input_ref` is `<run_id>/<call_id>`, optionally with a selector
  `#<evidence_id>|<qualifier>|<start>:<end>`, **when** the regression runs, **then** the recorded
  response is served from `F2`'s payload store — and, with a selector, the ONE item matching that
  identity is picked out of it — and compared to `expected`; **and** an expired payload, a missing
  recording or a malformed `input_ref` **raises `UnresolvableCase`** rather than being skipped. → *unit.*
  > ⚠⚠ Skipping is the tempting failure: it turns a broken baseline into a *smaller* baseline and
  > still reports green. ★ Same shape as `DX-20` one layer up — **the golden set's job is to notice,
  > so it may never quietly stop noticing.**
  > ★ `D5` is enforced *structurally* here: the resolver only reads files, so the regression cannot
  > reach a vendor even by mistake.
  > ⚠⚠ `DX-25` — one recorded `E-01` call returns EVERY segment row in BOTH columns while one case
  > pins ONE item, so a bare ref could never match a single-item `expected`. ★ The selector **is**
  > `MP-18`'s identity, so the golden set's granularity and the extraction's identity are one thing
  > rather than two conventions to keep in step. A vanished item raises — *the reading this case pins
  > is gone* is the regression, not a missing fixture.
- **AC-5.17** *(★ the golden set is loaded from disk, and validated on load — `A1`)* — **Given**
  `tests_src/fixtures/golden/*.yaml`, **when** the set is loaded, **then** every case is constructed
  through `CT-5.2`'s validation — so `D2`'s circularity check runs on **file** contents, not only on
  values a programmer typed; **and** a duplicate `case_id` across files raises. → *unit.*
  > ⚠ Before this, `GoldenCase` existed with no store: establishing a golden value meant editing
  > Python, which is why the set stayed empty. ★ A rule nobody can act on is not enforced, it is
  > merely stated.
- **AC-5.15** *(★ a study may not be imported — `D1`)* — **Given** the source tree, **when** CI runs,
  **then** nothing imports `src/evaluation/studies/**`. → *invariant / property (structural).* (`D1`)
  > ★ `D1`'s boundary is **consumption, not intent**: a metric is anything another decision reads. ⚠ The
  > silent direction is a *study* acquiring a consumer and becoming load-bearing while still exempt —
  > this is the check that catches it.
- **AC-5.16** *(★ a non-recomputable figure says so — `D4`)* — **Given** a `MetricResult` whose inputs
  have expired under `F2` `D2`, **when** it is read, **then** it is marked non-recomputable.
  → *data contract.*
  > ⚠ A figure nobody can re-derive must not look freshly checked — the same reasoning as `F2`'s
  > `UNREPLAYABLE`.
- **AC-5.8** *(calibration joins on `decision_id`)* — **Given** resolved outcomes linked by `F2`
  `CT-2.6`, **when** calibration is computed, **then** every bin's `observed_rate` derives from that
  join and no outcome is counted twice. → *data contract.*
- **AC-5.9** *(deletion curve detects a useless attribution)* — **Given** an attribution that is pure
  noise, **when** the deletion curve is computed, **then** removing top-`k` attributed features
  degrades performance no faster than removing random features, and the result is reported as
  unfaithful. → *unit.*
- **AC-5.10** *(insufficient is loud — `D3`)* — **Given** a metric requested on a sample below its
  **per-metric** minimum, **when** computed, **then** `value` is null and `insufficient_reason` names
  the shortfall — ⚠ **never a number computed on too little data**. → *unit.* (`P5`, `CN-10`)
  > ★ Each minimum is an **admitted floor** carrying a `CN-10` note saying who set it and on what
  > basis, copying `src/quant/metrics/breadth.py::MIN_NAMES`. Upstream `CN-10`: *"'admitted guess' is
  > an acceptable answer; **silence is not**."*
- **AC-5.11** *(no re-implementation of upstream metrics)* — **Given** the source tree, **when** CI
  runs, **then** `src/evaluation/**` contains no independent computation of IC, breadth or the IC
  standard error; it imports them. → *invariant / property (structural).* (`P4`)
- **AC-5.12** *(one-way import)* — **Given** the source tree, **when** CI runs, **then** no module
  outside `src/evaluation/**` imports from it. → *invariant / property (structural).* (`ST-2`)
- **AC-5.13** *(experimental provenance propagates)* — **Given** inputs produced by a variant with
  `experimental == true`, **when** a metric is emitted, **then** the result is labelled experimental
  and cannot be reported as production. → *data contract.* (`F1` `AC-1.11`, `PG-2`)
- **AC-5.14** *(pre-registration is recorded, not retrofitted)* — **Given** a `ComparisonResult`,
  **when** it is written, **then** `pre_registered_rule` is non-empty and its recorded timestamp
  precedes the comparison's `computed_at`. → *data contract.* (`PG-5.1`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✏ **Amended `A3` 2026-09-05** — `AC-5.18` + `CT-5.2`: `input_ref` settled as the **recording**, and
> `replay_response` implemented (`DX-21`). ⚠ Until this, `run_regression` took a callable nothing ever
> supplied, so a golden case could be written and **never run** — the third rung of the same ladder as
> `A1` (nowhere to write one) and `A2` (an unfinished one passing).
>
> ✏ **Amended `A1` 2026-09-05** — `CT-5.5` + `AC-5.17`: the golden set gained a **place to live**.
> ⚠ `D2` made establishing golden values the fund manager's work, and then left nowhere to put one:
> `GoldenCase` was a dataclass with no store, so the only way to add a case was to edit Python.
> ★ **A decision that assigns a human a task must leave them a way to do it.**
>
> ✅ **`D1`–`D5` ADOPTED 2026-09-04** (`D2` confirmed by Victor: *"fund manager decides what is
> right"*). The ACs they touch were amended in the same change.
> ★ **Three of the five were settled by finding the answer already in the inherited code** rather than
> by reasoning — the `MS-2`/`MS-3` habit, applied again.

**`D1` — The metric/study boundary: *does anything else consume it?*** *(Resolves `Q1`.)*

**A metric** is anything whose output another decision, gate, report or test reads. It is
spec-governed, lives in `src/evaluation/metrics/`, and needs `AC-5.1`'s known-answer fixture.
**A study** is read once by a human and consumed by nothing. It is `P7`-exempt, lives in
`src/evaluation/studies/`, and ⚠ **may not be imported by anything.**

- ★ **The rule is enforceable rather than a judgement**, which is what `QR-13` asked for: *"is it
  imported?"* is a grep, and `AC-5.12`'s import checker already runs it. **Consumption is the test, not
  intent** — a study that acquires a consumer has become a metric and must move.
- ⚠ **The drift `QR-13` feared runs the other way too.** A case-by-case rule lets everything slide into
  the exempt side; this rule lets a *study* quietly become load-bearing. The import check catches the
  second, which is the more dangerous direction because it is silent.
- **Rejected — "exploratory means exempt".** Intent is unobservable and changes after the fact; every
  metric began as an exploration.
- **Rejected — everything under `src/evaluation/` is spec-governed.** ✗ Kills the exploration `P7`
  exists to protect, and `QR-13` explicitly preserved it.

**`D2` — A golden value is established by the fund manager, never by the system.** *(Resolves `Q2`.)*

- `CT-5.2`'s `source` and `established_by` become **enforced**, not merely present: `established_by`
  may not name any pipeline component, and `AC-5.1` fails on a golden case whose `source` is empty.
- ⚠ **The circularity `Q2` names is real and not fully escapable for `thesis`.** Extraction and ranking
  have objective answers (a filing says what it says). A thesis's "correct" answer is a judgement, so
  the golden case records **the judgement and who made it** rather than pretending to objectivity.
- ★ **Same shape as `DX-5`'s split**: where truth is external, keep it external and *say* it is a
  judgement; do not synthesise something that looks like ground truth.
- **Rejected — seed the golden set from the system's own best output.** ⚠⚠ Circular: the harness would
  certify the system against itself and **regressions would become the new gold**. This is the single
  most dangerous option on this page because it produces a green suite forever.
- **Rejected — an LLM judges the golden answers.** Same circularity one level removed, plus
  `Sharma et al. (2023)` sycophancy: the judge sees the candidate.
- **Rejected — no golden set for `thesis`.** Gives up the only check on the most expensive output.

**`D3` — Per-metric minimums, declared as ADMITTED FLOORS under `CN-10`.** *(Resolves `Q3`.)*

★★ **The answer is already upstream.** `src/quant/metrics/breadth.py`:

```python
#: ⚠ Below this many names a pairwise-correlation average is dominated by its own
#: sampling error. **An admitted floor** (CN-10) — nothing measured it; it exists
#: so the function declines rather than returning a confident number from four
#: observations.
MIN_NAMES = 10
```

and on insufficiency it returns a `why` naming the shortfall. ★ **F5 adopts that shape verbatim** —
per-metric constant, `CN-10` comment stating who set it and on what basis, and a refusal carrying its
reason. Upstream `CN-10` says *"**'admitted guess' is an acceptable answer; silence is not**"*.

- **Rejected — one global floor.** ⚠ ECE with 5 bins needs a different `n` from a grounding rate; a
  single number is wrong for every metric except the one it was chosen for.
- **Rejected — derive each floor from a power calculation.** ★ Correct in principle and **currently
  undeliverable**: the effect sizes are unknown, which is what `F7a` exists to find out. `CN-10`'s
  admitted floor is the honest interim, and it is revisable *because it is written down*.
- **Rejected — no minimum; report `n` and let the reader judge.** ⚠ `AC-5.10` exists because a number
  computed on 4 observations gets quoted without its `n`.

**`D4` — Retention: `MetricResult` history is permanent; inputs follow `F2` `D2`.** *(Resolves `Q4`.)*

- `Q4` says *"the same tiering question as `F2`'s `Q2`, and it should get the same answer"* — ★ agreed,
  and `F2` `D2` already decided it: **records forever, raw payloads expire.** A `MetricResult` is
  kilobytes and **is** the regression trend; the run payloads behind it are what expire.
- ⚠ A metric whose inputs have expired stays valid **as a recorded figure** and becomes
  **non-recomputable**. That distinction must appear in the record, exactly as `F2`'s `UNREPLAYABLE`
  does — a figure nobody can re-derive should say so rather than look freshly checked.
- **Rejected — expire old `MetricResult`s.** Destroys the trend, which is the only thing that makes a
  regression suite more than a point check.

**`D5` — CI runs the regression on RECORDED responses; live calls are opt-in.** *(Resolves `Q5`.)*

- ★★ **Both halves of the mechanism already exist.** `F2` records every LLM request/response
  (`CT-2.2`), and upstream already carries **4 `pytest.mark.live` tests** whose skip is loud. So the
  golden-set regression replays `F2`'s recordings in CI, and a `live` marker re-runs against the real
  vendor on demand.
- ⚠ **This is what makes `AC-5.7` affordable at all** — *"a prompt change reds the suite"* cannot mean
  an LLM call per case per commit.
- ★ It also gives `F5` a real second consumer of `F2`, which is evidence the trace substrate was worth
  building before the capabilities.
- **Rejected — live calls in CI.** Cost, flakiness, and ⚠ a suite that fails when a vendor is down
  teaches people to ignore red.
- **Rejected — no CI regression, measure after each run only.** A prompt change would be caught
  *after* it shipped, which is the wrong side of the change.

## 8. Open questions (must resolve before/at implementation)

> ✅ **All five are resolved** — `D1`–`D5` in §7, adopted 2026-09-04. **No open questions remain.**

- ~~**Q1 — Where is the metric / study boundary?**~~ → `D1` (consumption, not intent)
- ~~**Q2 — Who establishes a golden value?**~~ → `D2` (**the fund manager**; never the system)
- ~~**Q3 — Minimum sample sizes.**~~ → `D3` (per-metric admitted floors, `CN-10`)
- ~~**Q4 — Storage and retention.**~~ → `D4` (results forever; inputs follow `F2` `D2`)
- ~~**Q5 — Does F5 run in CI, after a run, or both?**~~ → `D5` (CI replays `F2`; live is opt-in)

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-5.1 | `tests/unit/test_evaluation_metrics.py::test_ac_5_1_*` (6, incl. 5 forbidden establishers, ★ 13 placeholder blanks and 8 real names — `DX-38`) | `src/evaluation/golden/models.py::GoldenCase` · `_is_placeholder` |
| AC-5.2 | `::test_ac_5_2_a_figure_without_n_cannot_be_built` · `::test_ac_5_2_value_and_insufficiency_are_mutually_exclusive` | `metrics/models.py::MetricResult` |
| AC-5.3 | `::test_ac_5_3_selection_count_travels_with_the_figure` · `::test_ac_5_3_selection_count_starts_at_one` | `metrics/models.py` |
| AC-5.4 | `::test_ac_5_4_tier_must_be_declared_and_valid` · `tests/integration/test_evaluation_regression.py::test_ac_5_4_an_underpowered_comparison_is_insufficient_never_a_pass` | `metrics/models.py`, `studies/compare.py` |
| AC-5.5 | `::test_ac_5_5_coverage_and_calibration_never_share_a_field_name` · `::test_ac_5_5_neither_is_derived_from_the_other` | `metrics/calibration.py::evidence_coverage` |
| AC-5.6 | `::test_ac_5_6_grounding_rate_is_verified_over_factual` · `::test_ac_5_6_unbound_count_is_reported_beside_the_rate` | `metrics/grounding.py` |
| AC-5.7 | `tests/integration/test_evaluation_regression.py::test_ac_5_7_*` (4) | `regression/run.py` |
| AC-5.8 | `::test_ac_5_8_an_outcome_is_never_counted_twice` · `::test_ac_5_8_unresolved_predictions_are_excluded` | `metrics/calibration.py::_resolved` |
| AC-5.9 | `::test_ac_5_9_*` (3) | `metrics/faithfulness.py::deletion_curve` |
| AC-5.10 | `::test_ac_5_10_*` (3) | `metrics/models.py::MINIMUM_N`, `insufficient` |
| AC-5.11 | `tests/structural/test_evaluation_boundaries.py::test_ac_5_11_*` (4) | `tools/check_evaluation_boundaries.py` |
| AC-5.12 | `::test_ac_5_12_*` (2) | `tools/check_evaluation_boundaries.py::one_way_violations` |
| AC-5.13 | `::test_ac_5_13_experimental_inputs_produce_an_experimental_figure` | `metrics/models.py` |
| AC-5.14 | `tests/integration/test_evaluation_regression.py::test_ac_5_14_*` (3) | `studies/compare.py::ComparisonResult` |
| AC-5.15 | `tests/structural/test_evaluation_boundaries.py::test_ac_5_15_*` (3) | `tools/check_evaluation_boundaries.py::study_consumer_violations` |
| AC-5.16 | `::test_ac_5_16_a_figure_whose_inputs_expired_is_marked` | `metrics/models.py::MetricResult.recomputable` |
| AC-5.17 | `tests/unit/test_golden_store.py::test_ac_5_17_*` (6) | `golden/store.py::load_kind` · `load_all` · `coverage` |
| AC-5.18 | `tests/unit/test_golden_replay.py::test_dx_21_*` (8) · `::test_dx_25_*` (5) | `regression/replay.py::recorded_response` · `_select` |

✅ **All 16 ACs green, 2026-09-04** — **21 mutations run, all caught on the first pass.**

✅ **The golden set is no longer empty — 25 cases, 2026-09-09.** 20 grade `E-01` (segment tables,
MU + AMD) and 5 grade `E-02` (guidance, MU), every one established by the fund manager against the
filing and every one verified to RED under mutation before it was signed.

⚠ **What is NOT covered, stated because a traceability table's job is to be honest:**
- **2 blocks of 15.** `E-03`…`E-15` have no cases at all, and `ranking` and `thesis` have none —
  ★ `thesis` is the kind `D2` says is a judgement, and the most expensive output in the system.
- **3 `E-02` cases remain unsigned** in `extraction.pending.yaml`, including the two that would pin
  `DX-33` and `DX-35`. ⚠ Until signed, both fixes are in code but **ungraded**.
- ⚠⚠ **`AC-5.1` was enforced weakly until `DX-38`** (2026-09-09): `established_by` refused an empty
  string but accepted the template's own blank `'____'`, so an unsigned case could grade as
  established. ★ `D2`'s circularity check could not catch it — a placeholder is not circular, it is
  unattributed. Measured on 3 real cases before it was closed.
