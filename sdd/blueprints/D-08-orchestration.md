# Blueprint — D-08 Orchestration *(B3 shim · **B6 the real domain**)*

> **Code:** `src/orchestration/` · **Spec:** `sdd/design/rel6_design/L1-orchestration.md` · **Seat:** SEAT-5 · **LEVEL 0**
> **Status:** written 2026-08-23 at **B3** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠⚠ **THIS IS THE WALKING-SKELETON SHIM (L3 BS-12), NOT D-08.** Retry classification, time
> budgets, the DST-safe 10:00 ET cadence, preconditions, locks and checkpoints are **B6**, when
> D-08 replaces it (BS-16). §9 lists every one, so the gap is visible rather than looking like an
> oversight.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-26 | ★ **The `thesis` job — D-01 WF-1 reaches the graph, and OFF by default** | `daily_inference` **`v4` → `v5`**. ⚠ **Optional and disarmed unless `--thesis` is passed**: three live Opus passes are ~$1, and a daily job that quietly bills per invocation is a surprise P5 has no equivalent for. ★★ **Orchestration passes no gateway and cannot build one** — ST-5/AC-8.4 let only D-01 reach the model, and *a shim that can build a gateway can make a call*; nine architecture tests caught the first attempt. The shim hands over a flag and a `DataEngine`; D-01 reads its own credential | *Injecting the gateway* — reasonable by every other dependency's logic, and the one dependency where it is forbidden |
| 2026-08-26 *(wiring)* | **One adapter per job, and they route rather than compute** | The graph was declared, validated and **never actually run against a domain** — `src/orchestration/jobs/b3_run.py` wired the same sequence by hand. `src/orchestration/jobs/wiring.py` gives each job an adapter that reads what it needs from a `RunContext` and hands it to the domain. **The moment an adapter derives a value, D-08 has acquired analysis** and OR-1 is broken, so `test_no_adapter_computes` bans pandas, numpy and every aggregation from the module | *Letting the runner resolve and call* — one `importlib` inside `run()` and OR-1 becomes a convention |
| 2026-08-26 *(wiring)* | ★ **A job reading an absent upstream output RAISES** | `RunContext.require` refuses rather than defaulting. ⚠ An adapter that substituted an empty frame would let a job **run on data that was never produced** — the graph's own P5, and the cascade test proves it: a malformed price frame fails `prices`, every downstream job refuses, the run is `INCOMPLETE`, and **no card is built** | *Passing `None` through* — every domain would then need its own guard, and one of them would forget |
| 2026-08-26 *(wiring)* | ⚠ **The entrypoint still blocks: nothing assembles the universe's prices** | `_context_for` returns `None`, so a real invocation blocks rather than running the graph on nothing. ★ The pieces exist — `DataEngine.get_prices` is live-tested — but **nothing loops the universe**, and a partial panel is the defect MT-11 and RK-36 both refuse. It is a data-plane change, not an orchestration one | *Fetching one ticker and proceeding* — a one-name cross-section makes every rank statistic meaningless while looking fine |
| 2026-08-26 | ★★ **The `book` job — D-11 reaches the graph** | `daily_inference` goes **`v3` → `v4`**: a `book` job invokes `src.recording.book.load:load_books` by dotted name and `risk` depends on it, so D-05 finally reports **why** a book is unavailable instead of the B3 skeleton's stale *"the book is not built"* — which stopped being true the moment D-11 landed. ⚠ **AC-8.2's substring check had to be corrected first** (OR-48): it rejected the sanctioned `invokes`-plus-`resolve` seam as well as a real import, leaving no legal path from the graph to the book at all | *Importing D-11 into the shim* — OR-2 forbids an inference run editing the record, and the import is how that starts |
| 2026-08-25 *(B7)* | ★★ **`Job.invokes` is resolved and pinned by a test** | ⚠ **Found by running it:** when B6 declared `DAILY_INFERENCE`, **five of its nine names pointed at functions that did not exist** — `rank` for `rank_candidates`, `build` for `build_panel`, `render` for `build_card`, and `calendar_check` for `calendar_check_report`. Nothing noticed, because ★ **a declared pointer with no check is a comment.** `resolve()` + `assert_graph_resolves()` now pin all nine | *Leaving the strings unvalidated* — the graph reads as executable and was not |
| 2026-08-25 *(B7)* | ★ **Dispatch lives in `src/orchestration/entrypoint.py`, not in the runner** | **OR-1.** The runner still takes `invoke` as an argument, so **nothing inside `src/orchestration/` can return a value derived from market data**; the one place a domain is actually called sits at the edge, where it is visible and greppable. `test_resolution_lives_at_the_edge_not_in_the_runner` pins that `importlib` never enters the runner | *Resolving inside `run()`* — one import and OR-1 becomes a convention |
| 2026-08-25 *(B7)* | **`_day_bar()` returns `None`, so the daily run BLOCKS** | ⚠ D-07's settled-open feed is unwired, and **OR-33 says a missing open blocks and is never substituted with the previous close.** ★ Blocking is therefore the *correct* behaviour today, not a stub — and it exits 0, because BLOCKED is INFO (OR-42) | *Falling back to the last close* — it makes the decision a day stale while looking current |
| 2026-08-25 *(B6)* | ★★ **A model artifact declares `trained_anchor`, or the run blocks** | **OR-44.** **AC-8.32 raises when a model was trained on a different anchor — and nothing declared a training anchor.** The manifest carries `decision_anchor` (OR-35); D-03's nomination carries a hashed id and no anchor; D-04 is unbuilt: **`ORC.CADENCE.ANCHOR_MISMATCH` could never fire.** ★ Blocking on an *undeclared* anchor is the point — *matching* and *unknown* are opposite findings, and INV-4's drift is **a full session on every prediction, invisible in backtest** because the backtest shares the training anchor | *Assuming a match when the model is silent* — it makes the loudest rule in §5A undetectable while looking enforced |
| 2026-08-25 *(B6)* | ★★ **A failure notice is not a human-facing artifact** | **OR-45.** **OR-16 forbids an artifact from an INCOMPLETE run; OR-19 requires a failed run to reach the human by the same channel a success would.** Unqualified, the first forbids the second — and an implementer resolving it that way makes a failed run **silent**, which is exactly what OR-19 exists to prevent. ★ **The line is what the message CLAIMS**: a report asserts *"here is the analysis"*; a failure notice asserts *"the run did not complete, here is why"* and carries no analytical content | *Suppressing all output under INCOMPLETE* — the safest-sounding reading, and it produces the exact silence OR-19 forbids |
| 2026-08-25 *(B6)* | ★★ **One run per cadence window is a KEY, not the lock** | **OR-46.** **AC-8.37 cites OR-24 and the lock cannot deliver it.** A lock is mutual exclusion *in time* — two firings twenty minutes apart never overlap: the first completes, **releases the lock**, and the second finds it free and runs the whole cadence again. ★ `(job_graph_id, date, local_time)` is claimed by a completed run; ⚠ **a FAILED run does not claim it**, or OR-42's deliberate redundancy buys nothing exactly when it is needed | *Holding the lock for the window* — it turns a diagnosable holder into a 24-hour mystery, and OR-24 requires the holder be inspectable |
| 2026-08-25 *(B6)* | ★ **`invoke` is the caller's dispatch; the runner calls no domain function** | This is what keeps **OR-1 checkable**: *a function that returns a number derived from market data* cannot exist here, because **nothing in the runner computes one.** A grep-able boundary beats a reviewed one | *Importing the domains and calling them* — one import and OR-1 becomes a convention |
| 2026-08-25 *(B6)* | **Graph order breaks ties on `job_id`** | INV-2 through D-08: *reproducibility is a property of the whole invocation.* ⚠ A topological order that depends on dict insertion is not inspectable, and `plan()` must be byte-identical run to run | *Insertion order* — stable in practice and unstated, which is the same thing as unreliable |
| 2026-08-23 | The shim lives in **`src/orchestration/`**, governed by D-08's spec | BS-16 says *"D-08 replaces the B3 shim"* — replacing something means it was in the same place. And **OR-3 must hold for the shim too**: no domain may import it | A `scripts/` entrypoint — ungoverned, which is exactly §1.5's inherited violation being recreated |
| 2026-08-23 | The job graph is **declared data**, even for nine jobs | T-2: *dependencies are declared data, not control flow buried in a `main()`*. **The graph is inspectable without running it**, and `plan()` returns it | A hard-coded call sequence — nine calls is short enough to get away with, which is how it becomes forty |
| 2026-08-23 | ★★ **`stubs[]` was added to CT-8.1** (OR-43) | BS-27 requires the constant-PASS gate to be *"written into the RunManifest rather than being silently true"* — and **the contract had no field for it.** Fourth instance of a rule asserting against an undeclared field | A log line — logs are not the record, and *a stub indistinguishable from a real gate in the RECORD is how a placeholder survives into production* |
| 2026-08-23 | `b3_stubs()` **imports the constants from the stub modules** | So the manifest's `replaced_at` cannot drift from the stub's own answer. One source, two readers | Typing `"B4.4"` twice — the second copy is the one that goes stale |
| 2026-08-23 | The composition root is **`src/orchestration/jobs/b3_run.py`**, and it wires adapters | ★ CA-9: the root constructs while computing nothing. ⚠ *A "composition root" that starts choosing WHICH adapter based on data has become a decision layer, and D-12 is the only domain allowed to be one* | Wiring inside each domain — every domain would then know its neighbours' constructors |
| 2026-08-23 | `_Recorder` times jobs and **decides nothing** | Timing is recording, not computation (OR-1). It produces `JobRun`, which is a fact about the run, not about the market | Doing budget enforcement here — that is OR-20's, and it is B6's |

---

# 1. What this domain does, in one paragraph

```
ORCHESTRATION INVOKES WORK. IT NEVER PERFORMS WORK.

The reason is not tidiness. A computation inside an entrypoint has NO SPEC,
NO OWNER and NO ACCEPTANCE CRITERIA — it is invisible to the whole SDD
process by construction.
```

The B3 shim answers *"what should run, in what order, and what actually happened"* for nine jobs. ★ `DAILY_INFERENCE` (`v5`) runs **eleven** — `book` (D-11) and `thesis` (D-01 WF-1).
It writes a **RunManifest before any work begins** and a **RunOutcome** after, and it computes
nothing.

# 2. The objects and how they flow

```text
   build_manifest ──► RunManifest (CT-8.1, incl. stubs[]) ──► ManifestStore.write
        │                                                        (immutable — OR-13)
        ▼
   run_skeleton: calendar_check -> prices -> features -> rank -> gate
                                                          -> risk -> compose
                                                          -> render -> deliver
        │  each wrapped by _Recorder ──► JobRun[]
        ▼
   finish() ──► RunOutcome (CT-8.2)   SUCCESS | INCOMPLETE
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `RunManifest` | `src/orchestration/contracts/manifest.py::RunManifest` | `src/orchestration/jobs/skeleton.py::build_manifest` | the record; D-12's anchor check | forever — immutable |
| `Stub` | `src/orchestration/contracts/manifest.py::Stub` | `src/orchestration/jobs/skeleton.py::b3_stubs` | the manifest **and the card** | forever |
| `RunOutcome` | `src/orchestration/contracts/manifest.py::RunOutcome` | `src/orchestration/jobs/skeleton.py::finish` | D-11, D-09 | forever |

★ **The object that surprised me: `Stub`.** It is the only thing in the manifest that describes what
the system **could not** do. Everything else records inputs; this records an honest limitation, and
it is the field BS-27 exists for.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | write the manifest | `src/orchestration/jobs/b3_run.py::run_skeleton` | ★ **OR-9 — BEFORE any work.** *Without this a run cannot be reproduced, and INV-2 is unenforceable at the only layer that can enforce it* | `ManifestImmutableError` on a re-write |
| 1 | calendar check | `src/orchestration/jobs/b3_run.py::_calendar` | **DE-31** — before the first feature is built | `UnhandledBlockError` |
| 2–8 | the domain calls | `run_skeleton` | each is an **invocation of a public API** (ST-3); the order is `JOB_GRAPH`'s | each domain's own error |
| 9 | finish | `src/orchestration/jobs/skeleton.py::finish` | ★ **OR-16 — partial success is failure.** Any failed job ⇒ `INCOMPLETE` ⇒ no human artifact | — |

⚠ **`_calendar` seeds the event store from the run's own events and records the handling for the
split.** That is the only handling QD-15 defines (re-derive the panel at the run's `adj_as_of`), and
it is **recorded** rather than assumed — a BLOCK may only be cleared explicitly.

# 4. ★ The mathematics

★ **None, and here it is an acceptance criterion.** **AC-8.1**: *no function in
`src/orchestration/` returns a value derived from market or fundamental data.* The test enforces it
structurally, refusing `.mean()`, `.std()`, `.sum()`, `.rank()`, `.corr()`, `.var()` anywhere in the
package. The three things that compute:

| Computes | Why it is not OR-1's "computation" |
|---|---|
| `config_hash` | a content hash of configuration — no domain quantity |
| `new_run_id` | a timestamp plus randomness — identity, not analysis |
| `topological_order` | Kahn's algorithm over a **declared** graph — sequencing is exactly what D-08 is for |

# 5. The logic decisions

| Decision | Where | Why this way | What it would take to change it |
|---|---|---|---|
| Kahn's tie-break is **alphabetical** | `src/orchestration/jobs/skeleton.py::topological_order` | Determinism (INV-2). Arbitrary and *stated* | one `sorted()` |
| A dirty tree is **permitted and marked** | `src/orchestration/contracts/manifest.py::git_state` | OR-11. *Silently recording a clean sha for a modified tree is worse than not recording one* | — |
| `run_id` = timestamp + 6 hex | `new_run_id` | ★ OR-12: *two runs launched in the same second must be distinguishable, and a run id must survive a clock change* | — |
| `budgets: {}` written explicitly | `build_manifest` | ⚠ An empty dict says *no budgets were set*; an absent key would say nothing. Same reasoning as `stubs: []` | build OR-20 |

# 5A. ★ The B6 modules

| Module | Rules |
|---|---|
| `src/orchestration/schedule/cadence.py` | OR-8, OR-30, OR-31, OR-37, OR-46 — the DST-safe `(local_time, tz)` cadence and the `cadence_key` |
| `src/orchestration/schedule/preconditions.py` | OR-5…OR-7, OR-32, OR-33, OR-44, OR-46 — every gate that runs *before* a manifest exists |
| `src/orchestration/policy/retry.py` | OR-14, OR-14a, OR-15 — the transport/semantic table |
| `src/orchestration/policy/budget.py` | OR-20…OR-23 — the sentence L0 §4.2 stated and nothing implemented |
| `src/orchestration/state/locks.py` | OR-24…OR-27, OR-46 — lock, claims, checkpoints and the attempt log, kept **visibly separate** |
| `src/orchestration/jobs/graph.py` | OR-40, OR-41, T-2 — declared jobs, deterministic order, the timer lint |
| `src/orchestration/jobs/runner.py` | §11's surface — `plan · trigger · run · resume · status · history` |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Changing it affects |
|---|---|---|---|
| `JOB_GRAPH` | `src/orchestration/jobs/skeleton.py` | nine jobs (B3 shim; `DAILY_INFERENCE` now has **eleven**) | the run order — **declared data**, inspectable via `plan()` |
| `B3_TICKER` | `src/orchestration/jobs/b3_run.py` | `NVDA` | ★ **QY-2's recommendation**: a long clean history, an EDGAR filer class, and a split in-window to exercise QA-84/91 |
| `seed` | `build_manifest` | 42 | recorded in the manifest; nothing consumes it yet |
| budgets, retry, cadence | ⚠ **not built** | — | **B6** |

| `DAILY_LOCAL_TIME` · `MARKET_TZ` | `src/orchestration/schedule/cadence.py` | 10:00 · America/New_York | QO-3's cadence. ★ **Never a UTC constant** (OR-30) |
| `DECISION_ANCHOR` | same | `"open"` | ★ Propagates into D-02/D-03/D-04 (OR-35), and is checked against the model's `trained_anchor` |
| `TRANSPORT_CODES` · `SEMANTIC_CODES` | `src/orchestration/policy/retry.py` | 9 · 11 codes | ★ **Not a heuristic** — an unlisted code is unclassified and therefore **not retried** (OR-14) |
| `DEFAULT_MAX_ATTEMPTS` · `DEFAULT_BACKOFF_S` | same | 3 · 2.0s | ⚠ **ADMITTED GUESSES** (CN-10) — OR-15 says *bounded and backed off* and names no numbers |
| `DEFAULT_RUN_SECONDS` · `per_job` | `src/orchestration/policy/budget.py` | 1800s · per graph | OR-23 — **config, not constants**, and their values are in the manifest |
| `TIMER_POLICY_MARKERS` | `src/orchestration/jobs/graph.py` | 10 markers | OR-41's lint. ⚠ ADMITTED GUESSES, same shape as `FORECAST_VOICE` |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | raw prices + events | the caller (D-07 adapters) | the domain that receives them raises |
| out | **CT-8.1** RunManifest | the record; D-12 reads `decision_anchor` | `AnchorMismatchError` downstream |
| out | **CT-8.2** RunOutcome | D-11, D-09 | — |

# 8. Failure behaviour

| Failure | Detected where | Behaviour |
|---|---|---|
| a manifest already exists | `src/orchestration/state/manifest_store.py::ManifestStore.write` | `ManifestImmutableError` — a rerun creates a **new** manifest |
| any job raises | `src/orchestration/jobs/skeleton.py::_Recorder.run` | records `FAILED` with its error code, **re-raises** |
| any job failed | `finish` | `INCOMPLETE`, and `produces_human_artifact` is `False` |

# 9. What this domain deliberately does NOT do — and what the shim leaves unbuilt

| Not in the B3 shim | When |
|---|---|
| retry classification (OR-14) — ★ *retry transport, never semantics* | **B6** |
| time budgets (OR-20…OR-23) — ★ *budget breach fails the run; it never truncates and emits* | **B6** |
| the DST-safe `(10:00, America/New_York)` cadence (OR-30/OR-31) | **B6** |
| preconditions: trading day, input freshness, the lock (OR-5, OR-24) | **B6** |
| checkpoints and resume (OR-26) | **B6** |
| the monthly retrain and its ordering (OR-37, OR-38) | B6, with D-04 |
| ✗ **computing anything** | never — OR-1, and AC-8.1 checks it structurally |
| ✗ **writing the book** | never — OR-2. *An inference run writing `positions.json` means a PREDICTION is editing the RECORD* |
| ✗ **placing an order** | never — OR-29. *It must be structurally impossible rather than merely absent* |
| ✗ **being imported by a domain** | never — OR-3, grep-checked in CI |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — the graph is declared and then hand-sequenced** | ⚠ medium | `JOB_GRAPH` is inspectable, and `run_skeleton` calls the jobs in a **hand-written order** that happens to match `topological_order()`. **Nothing asserts they agree at runtime** — the test checks the graph, not the caller | T-2 |
| **10.2 — no lock, so two concurrent runs would both write** | ⚠ medium | Different `run_id`s make the manifests safe; the **event store is shared and would be raced**. OR-24 is B6's | OR-24 |
| **10.3 — `RunOutcome` is not written to D-11** | ⚠ expected | T-8 says the outcome goes to the record. `ManifestStore.write_outcome` writes it to disk; **the D-11 write lands with D-11** | T-8, OR-2 |
| **10.4 — a failed job re-raises before `finish()` runs** | ⚠ medium | The `INCOMPLETE` outcome is therefore **never constructed** on a real failure — the exception propagates instead. Loud, which is right (P5), but it means `RunOutcome(INCOMPLETE)` is tested and not exercised | OR-16 |
| **10.5 — `_calendar` decides the handling for a BLOCK** | ⚠ **medium, and the one to watch** | Re-deriving at the run's `adj_as_of` is QD-15's only defined handling, so the choice is forced — but **the composition root choosing a handling is one step from CA-9's warning** about a root that starts making choices based on data | **QD-15**, CA-9 |

| **B6.1 — nothing dispatches `invoke` in production** | ⚠ **expected** | The runner takes `invoke(job, manifest)` as an argument and **no production caller supplies one**: `Job.invokes` is a dotted name that nothing resolves. ★ Deliberate for OR-1 (the runner cannot compute), but it means **the graph has never driven the real domains** — `src/orchestration/jobs/b3_run.py` still does, with its own wiring | OR-1, OR-40 |
| **B6.2 — no external timer entrypoint exists** | ⚠ expected | `assert_timer_has_no_policy` lints a crontab line; **there is no crontab line and no `__main__`.** OR-40's *"thin external timer"* is specified, checkable and unbuilt | OR-40 |
| **B6.3 — locks, claims and checkpoints are in-process only** | ⚠ **medium** | All three are Python objects on the `Orchestrator`. ★ They satisfy every AC **within one process** and give **no protection across processes** — two `python -m` invocations would each hold their own lock and claim register. Durable state is what OR-24/OR-26 actually need | OR-24, OR-26 |
| **B6.4 — `resume()` re-runs rather than resuming a stored run** | low | It calls `run()` and relies on the checkpoint table to skip completed work, which satisfies AC-8.27. ⚠ A resume **after process death** has no checkpoints to consult (B6.3) | OR-26 |
| **B6.5 — the retrain graph is not built** | ⚠ expected | OR-37's `first_trading_day` and OR-38's `UngatedPromotionError` exist; **no `monthly_retrain@v1` graph does**, because D-04 is unbuilt. AC-8.34 is asserted on the ordering rule, not on a running retrain | OR-38 |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_orchestration_b6.py` — 44 cases, each docstring naming its `AC-8.n`; `tests_src/test_orchestration_b3.py` still covers the shim |
| 1a | ★ **Break it and confirm red** | **(a)** In `src/orchestration/policy/retry.py`, move `HTTP_402` into `TRANSPORT_CODES`. `test_http_402_is_the_one_that_looks_like_transport_and_is_not` must fail — ★ *retrying it forever is a bill, not a fix.* **(b)** In `src/orchestration/state/locks.py`, drop `CadenceClaims.claim`'s SUCCESS guard. `test_ac_8_37a_a_failed_run_does_not_claim_the_window` must fail — ⚠ **a failed cadence could never be retried.** **(c)** In `src/orchestration/schedule/preconditions.py`, make `assert_anchor` pass when `trained_anchor` is absent. `test_ac_8_32a_a_model_declaring_no_anchor_blocks_the_run` must fail — ★★ **and INV-4's full-session drift becomes undetectable while looking enforced** |
| 2 | ★ **Break it and confirm red** | Add `df["x"].mean()` anywhere under `src/orchestration/`. `test_ac_8_1_no_orchestration_function_returns_a_derived_value` must fail — **that check is OR-1, and §1.5a is a production defect that existed for exactly the reason it prevents** |
| 3 | The worked example (§4) reproduces | `python -c "from src.orchestration import topological_order; print(topological_order())"` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **No — the git sha is the only externally-verifiable field**, and it is checked against `git` itself. Reproducibility is *claimed* by the manifest and demonstrated by `test_the_whole_run_is_deterministic`, which is self-consistency at the pipeline level |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-orchestration.md` | OR-1…OR-43, CT-8.1/8.2, **§1.5** the inherited violation, **§1.5a** the defect it caused |
| `sdd/design/rel6_design/L3-build-sequence.md` | **BS-12** (a shim, not D-08), **BS-16** (D-08 replaces it at B6), **BS-27** |
| `sdd/design/rel6_design/L4-coding-standards.md` | **CA-9** the composition root; OR-3 in §10.1's checked edges |
| `sdd/specs/constitution.md` | **INV-2** (determinism — OR-10 says D-08 is the only layer that can enforce it), P5 |
