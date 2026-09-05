# F3 — Corporate-action resolution agent

> **Spec-ID:** F3 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §B.2 · upstream skill
> `.claude/skills/ticker-went-silent/SKILL.md` · upstream `AB-18`, `AB-20`
> **Milestone:** `MS-6` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces **`PG-3`**; inherits `P5`, `ST-5`, `AP-2`, and upstream
> `DE-61`…`DE-68`.
> **Capability:** `C2` — ★ **the single clearest case in the system where an agent earns its place.**
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**; the rejected options are recorded there.

---

## 1. Goal & why

**Establish *why* a symbol stopped printing or changed — which the existing deterministic detector
cannot do, because the answer is not in the data.**

★ **The scope is narrow and the narrowness is the point.** Upstream already detects:

| Already built | What it does | Where |
|---|---|---|
| `detect.py` | *"DE-62 — ticker changes from a snapshot diff on CIK. ★ **No vendor, no search**"* | `src/data_engine/symbology/` |
| `combination.py` | *"DE-68 — a combination is TWO findings, and the retired symbol keeps printing"* | `src/data_engine/symbology/` |
| `master.py` | *"CT-7.8 — the point-in-time ticker map, anchored on CIK"* | `src/data_engine/symbology/` |
| event ingest | delisting-class events from the vendor feed | `src/data_engine/ingest/events.py` |

**Detection is deterministic, built, and deliberately search-free.** What it cannot supply is the
*cause* — and cause is what decides whether a name is dropped from the universe or migrated:

```text
   FROM A CIK DIFF, THESE ARE THE SAME SHAPE:
     BK  → BNY    a rebrand         ← 1 company, migrate the symbol
     EQR → VMRK   merger of equals  ← 2 companies, migrate ONE and
                                       delist the OTHER
   ⚠ Classifying the second as the first leaves the retired partner in
     the universe, printing the successor's prices.
```

★ **`PG-3` is satisfied here as nowhere else in the system**: the task requires open-ended, tool-using
interaction with an unbounded external world. There is no formula, no vendor field, and no amount of
deterministic code that answers it — the upstream vendor feed *"cannot speak about April, carries no
ticker-change class, and on `EQR` was simply wrong."*

**Measured cost of getting this wrong** (upstream `AB-18`, `AB-20`): of five S&P 500 names that stopped
printing, **two were not delisted at all** — they had been renamed and still traded. And `AVB`, the
retired half of a merger of equals, **kept printing the successor's prices**, producing a fabricated
−2.8 % return on the changeover date that no feature can distinguish from a real one.

## 2. Scope / non-goals

**In scope**
- The **classification** step: given a detection, determine which corporate action occurred.
- Tool-using search with **mandatory corroboration** before any classification.
- Splitting a combination into **two** findings (survivor + retired side).
- ⚠ The **contamination check** on a retired symbol.
- A structured `Finding` the existing stores consume.
- `undetermined` as a first-class outcome.

**Non-goals (this spec)**
- ✗ **Detection.** `detect.py` finds the candidates; F3 explains them. F3 is never the trigger.
- ✗ **The point-in-time ticker map.** `master.py` owns it; F3 writes findings, not the map.
- ✗ **Deciding universe membership.** F3 produces a classified finding; the universe rule acts on it.
- ✗ **Price repair or splicing.** ⚠ Upstream `DE-64` forbids splicing a retired symbol's bars onto its
  successor's, and F3 does not become the exception.
- ✗ **Calling an LLM directly.** All model access is through the shared gateway (`ST-5`).

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | `detect.py` reports a `ticker_change` from a CIK snapshot diff | CIK, old and new symbol | `src/data_engine/corporate_actions/resolve.py::classify` |
| T2 | A universe name stops printing bars beyond the staleness threshold | ticker, last bar date | same |
| T3 | A vendor delisting event arrives | ticker, vendor claim | same — ⚠ the vendor claim is **evidence, not a verdict** |
| T4 | Manual re-resolution of an `undetermined` finding | ticker | same |

## 4. Behaviour & reuse (the lean "how")

- ★★ **Search precedes classification, always.** The agent searches, corroborates, then classifies.
  ⚠ *A search run after a classification is not verification — it is confirmation-seeking, and it will
  find something that fits.*
- **Query the company name as well as the symbol.** A renamed or merged ticker is usually reported
  under the new symbol only.
- **Corroborate before classifying:** two independent sources, or one primary (an SEC filing, an
  exchange notice, the company's own IR release). ⚠ A single aggregator article is not enough —
  aggregators routinely describe a rename as a delisting.
- **A combination yields two findings**, reusing `combination.py`'s existing rule rather than
  restating it: a `ticker_change` for the surviving CIK **and** a `delisting` for the retired side.
  ⚠ The retired side does not appear in the CIK diff at all — it is invisible to the detector.
- ★ **Check the retired symbol for contamination.** Fetch retired and successor over the same window
  and compare closes day by day; a match after the effective date means the vendor is printing the
  successor's series under a dead ticker. **Volume is the tell** — a successor series usually rounds
  differently while OHLC agrees.
- **Cheap tier through the gateway.** Classification is high-frequency and shallow, so it runs on the
  cheap tier (`INV-8`) via `src/shared/llm/` — never a direct SDK call (`ST-5`).
- **Every step is traced** (`F2`): the queries issued, the pages retrieved, the sources cited, the
  classification and its confidence. ⚠ A finding whose evidence cannot be re-read later is not
  auditable.
- **`undetermined` is emitted, not avoided.** ⚠ Guessing "delisted" removes a live name permanently
  and nothing downstream questions it (`P5`).

## 5. Contracts (inline)

**CT-3.1 — `Finding`** (written to the event store; one per side of a combination):
```json
{ "ticker": "str",
  "outcome": "acquisition | merger | merger_of_equals | ticker_change | spinoff |
              bankruptcy | halt | vendor_gap | undetermined",
  "effective_date": "date | null",
  "company": "str",
  "surviving_cik": "str | null",
  "successor_symbol": "str | null",
  "retired_side": "bool",
  "series_contaminated_from": "date | null",
  "sources": ["url"],
  "confidence": "corroborated | single_source | undetermined",
  "provenance": "Provenance — F1 CT-1.4",
  "trace_ref": "str — F2 step_id" }
```
Rules: `sources` is **non-empty unless `outcome == "undetermined"`**; `confidence == "corroborated"`
requires ≥2 independent sources or one primary; `retired_side == true` requires a `successor_symbol`.

**CT-3.2 — resolution API:**
- `classify(ticker, cik, detected_at) -> tuple[Finding, ...]`
  → returns **one** finding normally, **two** for a combination.
  → raises nothing on failure: an unresolvable case returns a single `undetermined` finding.

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-3.1** *(★★ search precedes classification)* — **Given** a detection, **when** `classify` runs,
  **then** at least one search is issued **before** any outcome is assigned, and the trace shows the
  search steps preceding the classification step. → *integration.* (`PG-3`)
- **AC-3.2** *(no classification without corroboration)* — **Given** a case with exactly one
  non-primary source, **when** classified, **then** `confidence` is `single_source` — never
  `corroborated`. → *unit.*
- **AC-3.3** *(★ a combination yields two findings)* — **Given** a merger of equals, **when**
  classified, **then** two findings are returned: `ticker_change` for the surviving CIK and
  `delisting`-class for the retired side, sharing one `effective_date`. → *unit.* (`DE-68`)
- **AC-3.4** *(⚠ contamination is detected)* — **Given** a retired symbol whose closes match its
  successor's after the effective date, **when** classified, **then**
  `series_contaminated_from` is set to the first matching date. → *unit.*
- **AC-3.5** *(rename is never a delisting)* — **Given** a name that stopped printing but still trades
  under a new symbol, **when** classified, **then** the outcome is `ticker_change` and **no delisting
  finding is produced**. → *golden / characterization, over the recorded `BK`→`BNY` and `SATS`→`ECHO`
  cases.*
- **AC-3.6** *(★ `undetermined` is emitted, never guessed)* — **Given** searches that establish
  nothing, **when** classified, **then** the outcome is `undetermined` with `sources` possibly empty —
  ⚠ **and never `delisting`**. → *unit.* (`P5`)
- **AC-3.7** *(silence duration proves nothing)* — **Given** two cases with 3-day and 5-month
  staleness, **when** classified, **then** the outcome does not depend on the staleness duration.
  → *invariant / property.* (upstream: *the 3-day one was the rename*)
- **AC-3.8** *(every finding is evidence-backed)* — **Given** any finding with
  `outcome != "undetermined"`, **when** read, **then** `sources` is non-empty and every entry is a
  retrievable URL recorded in the trace. → *data contract.* (`AP-2`)
- **AC-3.9** *(the vendor claim is evidence, not verdict)* — **Given** a vendor delisting event that
  search contradicts, **when** classified, **then** the search-derived outcome wins and the vendor
  claim is recorded as a rejected source. → *unit.* (upstream `DE-67`)
- **AC-3.10** *(no direct SDK call)* — **Given** the source tree, **when** CI runs, **then**
  `src/data_engine/corporate_actions/**` imports no LLM SDK and reaches a model only through
  `src/shared/llm/`. → *invariant / property (structural).* (`ST-5`)
- **AC-3.11** *(traced and replayable)* — **Given** a completed classification, **when** its trace is
  replayed, **then** every search and page fetch is served from the recording and the same finding is
  produced. → *integration.* (`F2` `AC-2.3`)
- **AC-3.12** *(never splices)* — **Given** a contaminated retired symbol, **when** the finding is
  written, **then** no price series is modified, merged or spliced. → *invariant / property.*
  (`DE-64`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **`D1`–`D5` ADOPTED 2026-09-04.**

**`D1` — Search runs through the LLM gateway's server-side tool, not a separate API.**
*(Resolves `Q1`.)*

- ⚠ **`ST-5` decides this, not convenience:** *only the gateway calls an LLM.* A separate search API
  reached from `src/data_engine/` would put a second external caller outside the one place budget,
  retries, `model_id` and cost are recorded — and `F2` `CT-2.2` would stop seeing the call.
- **Measured:** `src/shared/llm/gateway.py` already carries `Tier`, `Decoding`, `LLMCall`, `charge()`
  and `spent_usd()`. ★ Adding a search-enabled tier extends that; it does not build a parallel path.
- **Rejected — a dedicated search API** (Brave/Serper/Tavily). ⚠ A second vendor, a second key, a
  second budget, and a call `F2` cannot replay.
- **Rejected — scraping.** Fragile, and `PG-3` justifies an agent here precisely because *"the answer
  is on the internet"* — not because we want an HTML parser.

**`D2` — F3 spends the EXISTING per-job budget; it declares no new one.** *(Resolves `Q2`.)*

- **Measured:** `src/orchestration/policy/budget.py` already has `Budgets.for_job` / `check_job` /
  `check_run`. ★ F3's sweep is a **job**, so it inherits a budget the orchestrator already enforces.
- ⚠ **The real control is scope, not spend:** `D3`'s severity cadence means a run sweeps only what is
  *due*, so *"hundreds of searches"* is a property of sweeping everything every day — which `D3` stops.
- **Rejected — a bespoke F3 cost cap.** A second budget that can disagree with the run's (`P4`), and
  the failure mode is the worst kind: two limits, neither authoritative.

**`D3` — Cadence is upstream `DE-72`'s severity schedule. F3 invents nothing.** *(Resolves `Q3`.)*

★★ **Already answered upstream, and better than a cron period would be.** `L1-data-engine` `DE-72`:

> *"Cadence follows **SEVERITY**, and staleness is measured from the refresh the store **RECORDED**.
> A stale `BLOCK` can let a real split through unhandled; a stale `NOTE` costs a reader context — so
> `BLOCK` is due after **1 day**, `FLAG` **7**, `NOTE` **30**."*

- ⚠ `DE-72` also warns that measuring from *when the sweep was invoked* lets a sweep that covered
  nothing reset the clock. F3 must read **recorded refresh time per name**, not run time.
- ★ Upstream separately records that with `DE-72` in place *"the cron period — still Victor's — **no
  longer blocks**"*, which is exactly why `Q3` can be closed without picking a number.
- **Rejected — a single daily sweep of the universe.** ⚠ `DE-72`'s own argument: one interval either
  hammers the rate limit for news or leaves splits unchecked for a week.

**`D4` — F3 WRITES the finding; it never acts on it.** *(Resolves `Q4`.)*

- **Decision: F3's output is a record, and the universe rule reads it.** ⚠ A resolver that also removed
  a name would be deciding, and `PG-3`'s justification for an agent here is *resolution*, not action.
- ★ The seam is already the right shape: `F2` records the finding with its `decision_id`, so whoever
  acts does so **traceably** and the two halves can be evaluated separately.
- **Rejected — F3 removes/flags the name directly.** Couples an agent to portfolio state, and an
  agent that acts is one whose mistakes are not merely wrong but *executed*.

**`D5` — `undetermined` is retried on the severity clock, with an attempt count and a ceiling.**
*(Resolves `Q5`.)*

- **Decision:** an `undetermined` finding is re-queued at its class's `DE-72` interval, carrying
  `attempts`. After a declared ceiling it becomes **`permanently_unchecked`** — which `DE-72` already
  treats as an **exempt** state, not an overdue one.
- ⚠ **That last clause is the point:** `DE-72` warns that reporting a permanently-unresolvable class as
  overdue daily *"would train a reader to ignore the whole report"* (`DE-35`). ★ An honest terminal
  state protects the report's signal.
- **Rejected — retry forever.** Produces a permanent backlog that readers learn to skip.
- **Rejected — never retry.** ⚠ *"As more information becomes available"* is exactly why a first
  `undetermined` is not final; a delisting rumour resolves in days.

## 8. Open questions (must resolve before/at implementation)

> ✅ **All five are resolved** — adopted 2026-09-04. **No open questions remain.**
> inherited code and specs** (`DE-72`, `policy/budget.py`), not by reasoning.

- **Q1 — Which search tool?** Server-side web search through the gateway, or a separate search API?
  ⚠ Affects `AC-3.11`: replay requires the page contents to be *recorded*, which a server-side tool
  may not expose. Blocks the replay AC's shape.
- **Q2 — Cost and rate budget.** A universe-wide sweep could issue hundreds of searches. Per-run
  budget, and what happens on exhaustion — fail the run, or emit `undetermined` for the remainder?
  ⚠ The second silently degrades the universe; the first is loud. Leaning loud (`P5`).
- **Q3 — Cadence.** Upstream `AB-14` records that nothing currently schedules the corporate-action
  sweep. Daily with the main run, weekly, or event-driven on detection only?
- **Q4 — Who acts on a finding?** F3 writes it; the universe rule consumes it. That rule's owner is
  D-07 upstream. ⚠ Confirm the boundary before `MS-6` so F3 does not quietly acquire universe authority.
- **Q5 — Re-resolution policy.** An `undetermined` finding should presumably be retried as more
  reporting appears. On what trigger, and does a later finding supersede or append?

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-3.1 | *(to be written)* | `src/data_engine/corporate_actions/resolve.py` |
| AC-3.2 | *(to be written)* | `.../corroborate.py` |
| AC-3.3 | *(to be written)* | `.../resolve.py` + reuse `symbology/combination.py` |
| AC-3.4 | *(to be written)* | `.../contamination.py` |
| AC-3.5 | *(to be written)* | golden fixtures from `AB-18` |
| AC-3.6 | *(to be written)* | `.../resolve.py` |
| AC-3.7 | *(to be written)* | `.../resolve.py` |
| AC-3.8 | *(to be written)* | `.../models.py` |
| AC-3.9 | *(to be written)* | `.../resolve.py` |
| AC-3.10 | *(to be written)* | `tools/check_llm_gateway_only.py` |
| AC-3.11 | *(to be written — blocked Q1)* | `src/orchestration/trace/replay.py` |
| AC-3.12 | *(to be written)* | `.../resolve.py` |
