# F8 — Human control surface

> **Spec-ID:** F8 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** `sdd/design/rel1_brainstorm.md` S4 ·
> [`../../questions.md`](../../questions.md) `QR-16`
> **Milestone:** `MS-6` · **Governs:** enforces `PG-2`; inherits `P5`, `INV-6`, upstream `RC-*` (journal).
> **Capability:** `C5` human-side · `C4` suspend/resume.
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**; the rejected options are recorded there.

---

## 1. Goal & why

**The inbound channel: the fund manager asks the system for something mid-decision, and the system
suspends, does the work, and resumes.**

Today the pipeline is **one-way** — schedule → compute → report → human. Both things the fund manager
asked for run the other direction: *"what about a different name?"* and *"tell me when this external
work is done."* Neither fits a batch that runs to completion and exits.

★ **The governing decision is `QR-16`, and it is not the obvious one.** When asked about a name outside
the top-1, the pipeline runs the **full analysis path — same depth, same rigour, same artifacts as the
top-1.** Not a stub, not a comparative summary, not a downgraded card.

> *"A ranked list the manager cannot interrogate is an oracle, not decision support."*

⚠ **No API surface exists in `src/`** — the legacy FastAPI app is in `backups/pipeline/api/`, unported.
This is greenfield in the new tree.

## 2. Scope / non-goals

**In scope** — the request surface; the full-depth drill-down path; the designation of which analysis
is the day's actionable one; journaling; suspend/resume with its token, idempotency, expiry and
stale-input guard; ★ **directives** — the interpreter, the closed effect vocabulary, the confirm step,
and the unmappable log (§2.1).

**Non-goals**
- ✗ **Any analysis.** F8 routes a request to `F9`'s port; it authors nothing.
- ✗ **Changing `INV-6`.** The actionable count stays **one** — see §4.
- ✗ **Deciding.** The manager designates; the system records.
- ✗ **Authentication beyond a single local user** — see `Q3`.
- ✗ **Inventing effects.** The interpreter may only emit effects already registered (`CT-8.5`); a new effect is a spec change.
- ✗ **Conversation.** One line in, one confirm. ⚠ No back-and-forth clarification dialogue.

## 2.1 ★ Directives — interpreted, not enumerated

*(Unblocked 2026-09-01. `QR-17`'s framing assumed directives could be enumerated in advance; Victor's
correction is that they are **case-by-case and diversified, and cannot be predicted**. That changes
the design from a fixed vocabulary of *inputs* to an interpreter over a fixed vocabulary of
*effects*.)*

**A directive is one line of natural language. An LLM translates it into a typed, bounded directive;
the fund manager confirms the resulting parameter changes; the system applies them deterministically.**

### ⚠ Why this does not breach `PG-9`

```text
   ✗ AN LLM THAT DECIDES what the system does   → a control policy. PG-9 forbids it.
   ✅ AN LLM THAT TRANSLATES what the manager    → a parser. The human still decides.
      already decided into a typed directive
```

★★ **And interpretation happens exactly once, at input time.** The typed directive is persisted and
**frozen**; replay reads the stored object and never re-invokes the model. A replayed run therefore
takes the same path — which is precisely what `PG-9` protects and what `F7a`/`F7b` depend on (`AC-8.13`).

It clears `PG-3` for the same reason `F3` does: **human natural language is genuinely unbounded**, so
no deterministic parser can cover it. That is where an agent earns its place.

### ★ Expressions are open; effects are closed

| | Vocabulary | Size |
|---|---|---|
| What the manager types | unbounded — *"be careful of noise"*, *"markets are jumpy"*, *"I don't trust today's data"* | ∞ |
| What the interpreter may emit | ★ a **registered set of effects** — see `CT-8.5` | small, and grows only by spec |

Many phrasings collapse onto few effects. The interpreter's job is the mapping, never the invention.

★ **An unmappable directive is information, not a failure.** It applies nothing, is shown to the
manager, and is **logged** — and the accumulated log becomes the backlog of which effects to add next
(`AC-8.19`). Each new effect arrives by spec amendment, never by prompt.

⚠ **The raw text never reaches another prompt.** It is recorded for the audit trail and consumed by
nothing downstream. Injecting it into an analysis prompt would reintroduce exactly the unfalsifiable,
untestable control `QR-17`'s analysis rejected (`AC-8.16`).

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | Manager requests analysis of a named ticker | ticker | `POST /analysis` |
| T2 | Manager designates the day's actionable recommendation | analysis id | `POST /designation` |
| T3 | External work completes; the run may resume | resume token | `POST /runs/{id}/resume` |
| T4 | Manager reads current state | — | `GET /runs/{id}` |
| T5 | ★ Manager types a one-line directive | free text | `POST /directives/interpret` |
| T6 | Manager confirms the interpreted effects | draft id | `POST /directives/{id}/apply` |
| T7 | Manager revokes an active directive | directive id | `DELETE /directives/{id}` |

## 4. Behaviour & reuse (the lean "how")

- **A request runs the full path.** T1 resolves `F9`'s `ThesisSourcePort` and produces the same
  artifact the top-1 gets (`QR-16`, `AC-F9.7`).
- ★★ **`INV-6` is preserved by designation, not by rationing.** The actionable count stays **one**;
  the manager chooses which analysis it attaches to, and **the designation is journaled** (D-11).
  ⚠ Exactly one actionable recommendation, chosen by the person who owns the P&L, with the
  substitution visible rather than silent.
- **Rank is always shown.** A drill-down card states the rank the name held. ⚠ A card that looks
  identical to the top-1's invites the reader to forget it was not.
- **The ask is recorded regardless of outcome** — ticker, rank held, whether a designation followed.
  ★ Over a year that is behavioural data about the manager's own discipline, which is more useful than
  a guardrail that would have blocked a legitimate question.
- **Suspend/resume is a first-class run state.** A run may pause for external work and resume later,
  possibly after a process restart. It needs a resume token, idempotency, an expiry, and a
  stale-input guard.
- ⚠ **Expiry reuses the existing rule.** An un-resumed request ages and its thesis goes stale under
  upstream `RA-126` — *"an overdue relay is not a backlog item, it is a thesis going stale."*
  **No second staleness mechanism is invented.**

## 5. Contracts (inline)

**CT-8.1 — `AnalysisRequest`:**
```json
{ "request_id": "str", "ticker": "str", "as_of": "date",
  "requested_at": "iso8601", "rank_at_request": "int | null",
  "source_variant": "str | null — null means the default (QR-20)" }
```

**CT-8.2 — `Designation`** (journaled to D-11):
```json
{ "run_id": "str", "designated_analysis_id": "str",
  "displaced_analysis_id": "str | null — the top-1 it replaced",
  "designated_at": "iso8601", "rank_of_designated": "int" }
```
⚠ `displaced_analysis_id` is required whenever the designation is not the top-1 — the substitution is
the fact worth keeping.

**CT-8.3 — suspend/resume:**
- `POST /runs/{id}/resume` with a **resume token** → `200` resumed · `409` already resumed
  (idempotent) · `410` expired · `422` stale inputs.
- ⚠ `422` carries *what* went stale, so the manager can decide rather than guess.

**CT-8.4 — `Directive`** (typed, frozen at apply time):
```json
{ "directive_id": "str",
  "raw_text": "str — ⚠ RECORDED for audit; consumed by NOTHING downstream (AC-8.16)",
  "window": {"from": "date", "to": "date"},
  "effects": [{"effect": "str — must be in CT-8.5", "operation": "set|scale|suppress",
               "value": "number|string|null"}],
  "unmapped_phrases": ["str"],
  "interpreter": {"model_id": "str", "prompt_version": "str", "interpreted_at": "iso8601"},
  "state": "DRAFT | ACTIVE | EXPIRED | REVOKED",
  "applied_at": "iso8601 | null", "applied_by": "str | null" }
```
Rules: a `DRAFT` has **no effect on any run**. Only `apply` (`T6`) moves it to `ACTIVE`. Once
`ACTIVE`, `effects` is **immutable** — a change is a new directive, not an edit.

**CT-8.5 — `EffectVocabulary`** (closed, registered, versioned):
```json
{ "effect": "str — stable name",
  "target": "str — the parameter it moves",
  "operations": ["set", "scale", "suppress"],
  "domain": "str — legal range",
  "owning_spec": "str — the spec that authorises this effect to exist" }
```
⚠ **Initial contents are deliberately empty** — see `Q6`. The vocabulary is defined during E2E
validation, once real directives exist to map.

**CT-8.6 — `UnmappableDirective`** (append-only log):
```json
{ "logged_at": "iso8601", "raw_text": "str", "unmapped_phrases": ["str"],
  "nearest_effects": ["str"], "resolved_by_effect": "str | null" }
```
★ This log **is** the backlog for `CT-8.5`'s growth.

## 6. Acceptance criteria

- **AC-8.1** *(★ a request runs the full path)* — **Given** a request for any universe name, **when**
  it completes, **then** the artifact has the same required fields at the same depth as the top-1's.
  → *integration.* (`QR-16`, `AC-F9.7`)
- **AC-8.2** *(★★ the actionable count stays one)* — **Given** any number of analyses in a day,
  **when** the day's outputs are read, **then** exactly one carries the actionable designation.
  → *invariant / property.* (`INV-6`)
- **AC-8.3** *(designation is journaled with what it displaced)* — **Given** a designation of a
  non-top-1 analysis, **when** the journal is read, **then** it records the designated id, the
  displaced id and the rank. → *data contract.* (`PG-2`)
- **AC-8.4** *(rank is on the card)* — **Given** a drill-down artifact, **when** rendered, **then** the
  rank the name held is present. → *data contract.*
- **AC-8.5** *(the ask is recorded even without designation)* — **Given** a request that leads to no
  designation, **when** the journal is read, **then** the request is still recorded. → *unit.*
- **AC-8.6** *(resume is idempotent)* — **Given** a resumed run, **when** the same token is presented
  again, **then** `409` and the run is not re-executed. → *API contract.*
- **AC-8.7** *(resume survives a restart)* — **Given** a suspended run and a process restart, **when**
  resumed, **then** it continues from its checkpoint. → *integration.* (`F2`)
- **AC-8.8** *(expiry uses the existing staleness rule)* — **Given** a suspended request older than the
  staleness threshold, **when** resumed, **then** `410` and the thesis is marked stale by the existing
  rule — ⚠ **no second mechanism**. → *unit.* (`RA-126`, `P4`)
- **AC-8.9** *(stale inputs are named, not swallowed)* — **Given** prices that moved materially while
  suspended, **when** resumed, **then** `422` naming what changed. → *API contract.* (`P5`)
- **AC-8.10** *(no verification bypass)* — **Given** any request path, **when** a thesis is produced,
  **then** it passes the same claim verification and confidence de-rating as the scheduled path.
  → *invariant / property.* (`AC-F9.3`, `AC-F9.4`)
- **AC-8.12** *(★★ the interpreter emits only registered effects)* — **Given** any directive text,
  **when** interpreted, **then** every emitted effect is present in `CT-8.5` — ⚠ **an unregistered
  effect is never produced**, however the text is phrased. → *invariant / property.*
- **AC-8.13** *(★★ interpretation is frozen; replay never re-interprets)* — **Given** an `ACTIVE`
  directive, **when** its run is replayed, **then** the stored typed `effects` are applied and **the
  interpreter model is not invoked**. → *integration.* (`PG-9`, `F2` `AC-2.3`)
- **AC-8.14** *(unmappable applies nothing)* — **Given** text that maps to no registered effect,
  **when** interpreted, **then** **no** effect is applied — not even the mappable part — the manager
  is shown what failed, and an `UnmappableDirective` is logged. → *unit.* (`P5`)
- **AC-8.15** *(★ nothing takes effect without confirmation)* — **Given** an interpreted `DRAFT`,
  **when** any run executes before `apply`, **then** the run is unaffected. → *invariant / property.*
- **AC-8.16** *(⚠ raw text never reaches a prompt)* — **Given** an `ACTIVE` directive, **when** any
  downstream LLM call is made, **then** `raw_text` appears in no prompt; only typed effects are
  applied. → *invariant / property (structural).* (`AP-5`)
- **AC-8.17** *(effects apply deterministically)* — **Given** the same `ACTIVE` directive and the same
  inputs, **when** a run executes twice, **then** the applied parameter values are identical.
  → *invariant / property.* (`PG-9`)
- **AC-8.18** *(the window is honoured and expiry is automatic)* — **Given** a directive whose window
  has passed, **when** a run executes, **then** its effects do not apply and its state is `EXPIRED`
  without manual action. → *unit.*
- **AC-8.19** *(the unmappable log is reviewable)* — **Given** logged unmappable directives, **when**
  the log is read, **then** each entry carries its text and unmapped phrases, and an entry can be
  marked resolved by a named effect once one is added. → *data contract.*
- **AC-8.20** *(a directive is a capability that alters output)* — **Given** an `ACTIVE` directive,
  **when** a run executes, **then** a `CapabilityDelta` records the pre- and post-directive values,
  including when nothing changed. → *data contract.* (`PG-5.2`)
- **AC-8.11** *(everything is traced)* — **Given** a request, **when** the trace is read, **then** the
  request, the suspension, the resume and the designation are all recorded with the run's `run_id`.
  → *data contract.* (`F2`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **`D1`–`D6` ADOPTED 2026-09-04.**
> ⚠⚠ **`D3` (authentication) is the one that must not be waved through** — it is the only decision in
> the whole corpus that, if wrong, is wrong *at the network boundary of a machine that trades*.

**`D1` — A drill-down is a STEP inside the day's run, not a run of its own.** *(Resolves `Q2`.)*

- Confirms the spec's own leaning, and `F2` `CT-2.7` already assumes it: a drill-down is
  `attempt >= 2` on the **same `run_id`**, minting its own `decision_id`.
- ★ **`INV-6` is the deciding argument** — one actionable recommendation per day is enforceable over
  **one** boundary. Separate runs would make *"how many recommendations did today produce?"* a
  question about how many processes started.
- **Rejected — its own run.** ⚠ Would need its own manifest, cadence claim and lock (`OR-24`/`OR-46`),
  and `INV-6` would have to be re-derived across runs. `AC-8.2`'s enforcement point would move from a
  check to a join.

**`D2` — The interpreter runs on the CHEAP tier, and refuses rather than guesses.**
*(Resolves `Q7`.)*

- **Decision:** mapping one line of English onto a **closed** effect vocabulary is a classification
  task, not a reasoning one. ⚠ **The safeguard is not the tier, it is the closed set plus a refusal
  path**: an unmapped directive returns *"I did not understand this"* and changes nothing.
- ★ `PG-3` applies to the tier choice too — where the output space is bounded and known, the small
  model is the right instrument, and the money saved is real at once-daily cadence.
- **Rejected — the expensive tier for safety.** ⚠ Buys the *appearance* of care: a larger model
  guessing plausibly at an ambiguous directive is **more** dangerous than a small one refusing, because
  its guess reads as competent.

**`D3` — ⚠⚠ Token required, bound to localhost/tailnet, and the surface REFUSES to start without it.**
*(Resolves `Q3`.)*

- **Decision:** a bearer token from the environment (never a literal), bound to loopback or the
  tailnet interface, and ⚠ **the process fails to start if the token is unset** — it does not fall back
  to open.
- ⚠⚠ **"Single local user on a private network" is a statement about today, and it is the premise that
  fails silently.** A tailnet is a network; a laptop joins other networks. The cost of the token is one
  environment variable, and the cost of omitting it is an unauthenticated endpoint that can
  **suspend, resume and designate** on a machine that trades real capital.
- ★ **Fail-closed is the whole decision.** An auth check that can be skipped by not setting a variable
  is not an auth check — it is a default, and defaults drift.
- **Rejected — no auth while it is local-only.** The spec itself says *"do not defer this past the
  first deployment"*; the first deployment is `MS-6`.
- **Rejected — auth optional, on by default.** ⚠ Optional security is off in exactly the situation
  where someone was in a hurry.

**`D4` — "Materially stale" is a DATA-AS-OF change, not a clock or a price threshold.**
*(Resolves `Q4`.)*

- **Decision:** a suspended request is materially stale when the **`data_as_of` it was computed
  against is no longer the current one** — i.e. new data landed. Time and price move continuously;
  `data_as_of` moves exactly when the answer could have changed.
- ★ **It reuses a field `RunManifest` already carries**, so staleness is checkable from the recorded
  run rather than recomputed — and `RA-126` (*"an overdue relay is not a backlog item, it is a thesis
  going stale"*) already supplies the expiry half.
- **Rejected — a time threshold.** ⚠ Arbitrary, and wrong in both directions: 4 hours is stale over an
  earnings release and fine over a quiet weekend.
- **Rejected — a price threshold.** Requires a live quote to evaluate staleness, which makes the
  *check* more expensive than the thing it guards, and re-introduces `RC-58`'s pricing problem.

**`D5` — A revocation is a SECOND journal entry, never an amendment.** *(Resolves `Q5`.)*

- Confirms the spec's parenthetical. ⚠ **Append-only is the same rule as `F2` `AC-2.8` and
  `OR-13`** — *a record that can be edited is not evidence.* The designation happened; changing one's
  mind is a new fact, not a correction of the old one.
- ★ **The behavioural data is the point.** `F8` §4 already says the ask is recorded *"regardless of
  outcome"* because *"over a year that is behavioural data about the manager's own discipline"*.
  ⚠ Amending would delete exactly the pattern worth seeing: how often a designation is reversed.
- **Rejected — amend in place.** Loses the reversal, which is the interesting half.

**`D6` — `Q6` stays OPEN by Victor's decision; ⚠ it is now a gate on `MS-9`, not a loose end.**
*(Records `Q6`.)*

- Victor deferred the initial effect vocabulary (`CT-8.5`) to **E2E validation** — *"defined after
  codes written, during E2E validation"*. ★ That is a sound sequence: the vocabulary should describe
  effects the system actually has.
- ⚠ **But `QR-23` made E2E a precondition for resuming real trading**, so this is no longer a note to
  remember — **it is on the critical path to trading again.** Recorded here and in `L3` §7's E2E
  checklist so it cannot be lost.
- **Rejected — guess a vocabulary now to unblock `MS-6`.** ⚠ A closed set invented before the effects
  exist would either be wrong or would *constrain the build to match the guess*.

## 8. Open questions

> ✅ **All six are resolved** — adopted 2026-09-04. **No open questions remain.**
> ⚠⚠ **`D3` — authentication — is the one to read properly.** It is the only decision here that is
> wrong *at the network boundary of a machine that trades*.
> ⏳ **`Q6` stays open deliberately** (`D6`) and is now a gate on resuming trading (`QR-23`). (must resolve before/at implementation)

- ✅ ~~**Q1 — what is a directive for?**~~ **Resolved 2026-09-01** — interpreted, not enumerated (§2.1).
- **Q6 — ⏳ The initial effect vocabulary (`CT-8.5`) is deferred to E2E validation.** Victor:
  *"defined after codes written, during E2E validation."* ⚠ Recorded in the build plan's E2E checklist
  so it is not forgotten. Until then `CT-8.5` is empty and **every directive is unmappable** — which is
  the correct behaviour, not a bug: `AC-8.14` applies nothing and logs it, and the log seeds the
  vocabulary.
- **Q7 — Does the interpreter run on the cheap tier?** Mapping one line to a small closed set is
  high-frequency and shallow — `INV-8` suggests the cheap tier. ⚠ But a misinterpretation touches a
  tradeable number (`PG-2`), which argues the other way. The confirm step (`AC-8.15`) is what makes
  the cheap tier defensible.
- **Q2 — Is a drill-down its own run, or a step inside the day's run?** ⚠ Affects `AC-8.2`'s
  enforcement point and whether `run_id` is shared. *Leaning: a step inside the day's run, so `INV-6`
  is enforceable over one boundary.*
- **Q3 — Authentication.** Single local user on a private network today, but `F8` is a network
  surface. Is a token required, and is the surface bound to localhost or the tailnet?
  ⚠ Do not defer this past the first deployment.
- **Q4 — What counts as "materially" stale** for `AC-8.9`? A price threshold, a time threshold, or a
  data-as-of change?
- **Q5 — Does a designation ever get revoked?** If the manager designates and then changes their mind,
  is that a second journal entry or an amendment? *(Append-only argues for the first.)*

## 9. Traceability (spec → test → code)

✅ **All 20 ACs green, 2026-09-09** — mutation-verified (5 mutations on the ACs completed today, all
caught on the first pass).

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-8.1 | ★ `tests/integration/test_drilldown_full_path.py::test_ac_8_1_*` (4) | `control/models.py::AnalysisRequest` · `fundamental/source/adapters.py` |
| AC-8.2 | `tests/unit/test_control_surface.py::test_ac_8_2_only_one_analysis_a_day_may_be_actionable` | `control/models.py::DesignationJournal` |
| AC-8.3 | `::test_ac_8_3_a_designation_records_what_it_displaced` | `control/models.py::Designation` |
| AC-8.4 | ★ `tests/unit/test_control_surface_gaps.py::test_ac_8_4_*` (2) | `reporting/render/card.py::FIELD_ORDER` |
| AC-8.5 | `tests/unit/test_control_surface.py::test_ac_8_5_the_ask_is_recorded_even_with_no_designation` | `control/models.py` |
| AC-8.6 | `tests/unit/test_control_surface.py::test_ac_8_6_resume_is_idempotent` | `control/resume.py::SuspendStore` |
| AC-8.7 | `::test_ac_8_7_a_suspended_run_survives_a_process_restart` | `control/resume.py` |
| AC-8.8 | `::test_ac_8_8_an_expired_token_is_refused_by_the_existing_staleness_rule` | `control/resume.py::ResumeExpired` |
| AC-8.9 | `::test_ac_8_9_stale_inputs_are_named_not_swallowed` · `::test_ac_8_9_an_unchanged_data_as_of_resumes_cleanly` | `control/resume.py::InputsMovedOn` |
| AC-8.10 | ★★ `tests/integration/test_drilldown_full_path.py::test_ac_8_10_*` (4, incl. 5 coverage values) | `fundamental/source/adapters.py::_check_claims` |
| AC-8.11 | ★ `tests/unit/test_control_surface_gaps.py::test_ac_8_11_*` (3) | `control/models.py::control_trace_records` |
| AC-8.12 | `tests/unit/test_control_surface.py::test_ac_8_12_only_registered_effects_are_emitted` | `control/directives.py::EffectVocabulary` |
| AC-8.13 | `::test_ac_8_13_replay_uses_frozen_effects_and_never_re_interprets` | `directives.py::effects_for_replay` |
| AC-8.14 | `::test_ac_8_14_an_unregistered_effect_applies_NOTHING` | `directives.py::interpret` |
| AC-8.15 | `::test_ac_8_15_nothing_takes_effect_without_confirmation` | `directives.py::confirm` |
| AC-8.16 | ★★ `tests/structural/test_no_raw_directive_in_prompt.py` (5) · `tests/unit/test_control_surface.py::test_ac_8_16_*` | `tools/check_no_raw_directive_in_prompt.py::raw_text_leaks` |
| AC-8.17 | `::test_ac_8_17_the_same_directive_applies_identically` | `directives.py::effects_for_replay` |
| AC-8.18 | `::test_ac_8_18_the_window_is_honoured_and_expiry_is_automatic` (4 cases) | `directives.py::Directive.applies_on` |
| AC-8.19 | `::test_ac_8_19_unmappable_directives_are_logged_reviewably` | `directives.py::UnmappableDirective` |
| AC-8.20 | ★ `tests/unit/test_control_surface_gaps.py::test_ac_8_20_*` (4) | `control/directives.py::directive_delta` |

### ⚠⚠ What completing this spec exposed — two findings, 2026-09-09

1. **`AC-8.16` was typed *structural* and enforced by a unit test on ONE OBJECT (`DX-51`).**
   `Directive.to_prompt_payload()` correctly omits `raw_text`, and a test asserted exactly that — but
   **nothing stopped a different module reading `.raw_text` and building a prompt of its own.**
   ★★★ §2.1 states the harm: a directive reaching a prompt is *"an untyped instruction channel into the
   analysis"* — **prompt injection with the fund manager as the vector** — and `AC-8.15`'s confirm step
   would be approving typed effects while unreviewed prose travelled beside them. ✅ Now a tree-wide
   check and the **10th** CI guarantee. ⚠ It catches `payload["raw_text"]` as well as `.raw_text`,
   because a trace record read back from JSON is a **dict** — the path most likely to be taken.
2. **`AC-8.20` had no code.** A directive **changes a tradeable number**, so it owes `PG-5.2`'s two
   arms like any other capability. ⚠ Without the no-change arm, the only recorded directives are the
   ones that moved a number and the effect size is **1.0 by construction** — the same defect `F7a`
   `AC-7a.6` guards against, arriving through a different capability.
