# F8 — Human control surface

> **Spec-ID:** F8 · **Status:** 🟡 draft · **Adopted:** —
> **Source discussion:** `sdd/design/rel1_brainstorm.md` S4 ·
> [`../../questions.md`](../../questions.md) `QR-16`
> **Milestone:** `MS-6` · **Governs:** enforces `PG-2`; inherits `P5`, `INV-6`, upstream `RC-*` (journal).
> **Capability:** `C5` human-side · `C4` suspend/resume.
>
> ⚠ **No code exists yet** — `src/` is empty and this spec is unapproved. *(`PG-1`, which
> formerly blocked implementation, was retired 2026-09-02; verification is now manual.)*

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
  artifact the top-1 gets (`QR-16`, `AC-9.7`).
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
  → *integration.* (`QR-16`, `AC-9.7`)
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
  → *invariant / property.* (`AC-9.3`, `AC-9.4`)
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

> ✅ **None yet.** When a question in §8 is decided, move it here with a `D<n>`, and keep the
> **options that were rejected and why** — a later reader must be able to reconstruct the
> argument without the conversation that produced it. Cite the `D<n>` from every AC it changed.

## 8. Open questions (must resolve before/at implementation)

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

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test | Code module |
|---|---|---|
| AC-8.1, AC-8.10 | *(to be written)* | `src/orchestration/control/analysis.py` |
| AC-8.2 … AC-8.5 | *(to be written — Q2)* | `src/orchestration/control/` · `src/recording/` |
| AC-8.6 … AC-8.9 | *(to be written — Q4)* | `src/orchestration/control/resume.py` |
| AC-8.11 | *(to be written)* | `src/orchestration/trace/` |
| AC-8.12 … AC-8.14 | *(to be written)* | `src/orchestration/control/directives/interpret.py` |
| AC-8.15, AC-8.18, AC-8.19 | *(to be written)* | `.../directives/store.py` |
| AC-8.16, AC-8.17 | *(to be written)* | `tools/check_no_raw_directive_in_prompt.py` |
| AC-8.20 | *(to be written)* | `src/orchestration/trace/` |
