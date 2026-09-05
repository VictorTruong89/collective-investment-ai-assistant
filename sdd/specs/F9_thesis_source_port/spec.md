# F9 — Thesis source port

> **Spec-ID:** F9 · **Status:** 🟢 **approved** · **Adopted:** 2026-09-04
> **Source discussion:** `sdd/design/rel1_brainstorm.md` S4 ·
> [`../../questions.md`](../../questions.md) `QR-20`, `QR-16`
> **Milestone:** `MS-6` · **Governs:** inherits `P4`, `P5`, `AP-2`, upstream `RA-6`/`RA-9`,
> `RA-67`/`RA-114`/`RA-144`, `AC-1.77`.
> **Capability:** `C1` applied to seat 2 · `C8` provenance.
>
> ✅ **Approved 2026-09-04.** Open questions adopted as decisions in §7 — ★ **read §7 before changing
> §5 or §6**; the rejected options are recorded there.

---

## 1. Goal & why

**One port, two adapters: a thesis may be produced by the Anthropic API or by the relay, and nothing
downstream needs to know which.**

★ **This is `C1` proving itself on a real problem rather than a hypothetical one.** The two sources
have genuinely different properties — the API is one-shot, fast, fully controlled; the relay is
agentic, tool-using, slower, and has a human in the transport. Behind one contract they become a
config choice and an A/B pair.

**What already exists, and must not be rebuilt.** `src/fundamental/relay/` is built and in production —
`compose()` builds the schema-constrained prompt, `ingest()` validates and **re-verifies every claim
against the pipeline's own data, raising `RelayContradictedError` on contradiction**, `confidence_of()`
applies coverage de-rating through the *same* `assess_confidence` the scorecard uses, and `queue.py`
manages rotation with judgement overrides. ⚠ **F9 wraps this. It reimplements none of it** (`P4`).

**Decision (`QR-20`):** `ApiAdapter` is the **default**; `RelayAdapter` is the alternate; then measure
the actual API bill and revisit with a number rather than an estimate.

## 2. Scope / non-goals

**In scope** — `ThesisSourcePort`; `ApiAdapter`; `RelayAdapter` as a thin wrapper over the existing
relay; `provenance` on every thesis; registration of both variants; the shared contract suite.

**Non-goals**
- ✗ **Re-implementing prompt composition, ingest, verification or de-rating.** They exist.
- ✗ **Changing the confidence rules.** ⚠ `RA-67`'s coverage de-rating and `CONFIDENCE_FLOOR` fire
  **unchanged** — `AC-1.77` records that the relay's whole safety case rests on it.
- ✗ **Choosing which adapter runs.** Config, or `F6a`. F9 only makes both resolvable.
- ✗ **The relay's transport.** Whether a human pastes into a chat app or Claude Code writes to disk is
  an operational choice below the port; the port sees a completed envelope either way.

## 3. Users & triggers

| ID | Trigger | Input | Entry point |
|---|---|---|---|
| T1 | Daily run needs a thesis for the top-1 | ticker, as_of | `src/fundamental/source/port.py::ThesisSourcePort.author` |
| T2 | ★ Fund manager requests a name outside the top-1 (`QR-16`) | ticker, as_of | same — ⚠ **same depth, same path** |
| T3 | An A/B compares both adapters on one ticker | ticker | `F5` `studies/` |

## 4. Behaviour & reuse (the lean "how")

- **One contract, two adapters, `F1`-registered** as `("thesis_source", "api")` and
  `("thesis_source", "relay")`.
- **`RelayAdapter` delegates**: `compose()` → envelope out; `ingest()` → verified report back;
  `confidence_of()` → the confidence. F9 adds the port shape and the provenance, nothing else.
- ★ **Provenance travels with the thesis** (`F1` `CT-1.4`), so the discipline card can state which
  source produced it and a reader is never misled about what was verified.
- ⚠ **Verification is not adapter-specific.** `ingest()` re-verifies claims against the pipeline's own
  data and **raises on contradiction**. The API path gets the same treatment — a claim is checked
  because it is a claim, not because of who wrote it.
- ★ **Depth does not vary by source** (`QR-16`): both adapters produce the same artifact shape at the
  same depth. Provenance changes the *confidence*; it does not change the *work done*.
- **Fail loud on an unverifiable thesis** — a contradiction raises rather than downgrading silently
  (`P5`).

## 5. Contracts (inline)

**CT-9.1 — `ThesisSourcePort`:**
```json
{ "author": "(ticker: str, as_of: date, context: Mapping) -> Thesis" }
```
**CONTRACT — every implementation must guarantee:**
- **C1** every factual claim in the returned thesis is bound to an evidence span, or explicitly marked
  unbound (`RA-9`);
- **C2** a claim contradicting the pipeline's own data **raises**; it is never returned de-rated
  (`RA-118`);
- **C3** confidence is derived by the shared `assess_confidence`, never by the adapter (`RA-67`);
- **C4** the returned `Thesis` carries `provenance`;
- **C5** an unknown or unresolvable ticker raises; an empty thesis is never returned (`P5`).

**CT-9.2 — `Thesis` additions** (existing shape, plus):
```json
{ "provenance": "Provenance — F1 CT-1.4",
  "confidence": "object — from assess_confidence, unchanged",
  "claims": "tuple[Claim, ...] — RA-9; ⚠ empty is a defect, see AB-2" }
```

## 6. Acceptance criteria

- **AC-9.1** *(★ both adapters pass one contract suite)* — **Given** the `thesis_source` port, **when**
  the contract suite runs, **then** it executes against **every** registered variant and both satisfy
  `C1`–`C5`. → *invariant / property.* (`F1` `AC-1.9`)
- **AC-9.2** *(the relay is wrapped, not rebuilt)* — **Given** the source tree, **when** CI runs,
  **then** `src/fundamental/source/**` contains no prompt composition, claim verification or
  confidence logic of its own; it calls `relay/`. → *invariant / property (structural).* (`P4`)
- **AC-9.3** *(★★ verification survives the wrapper)* — **Given** a relayed report containing a claim
  that contradicts pipeline data, **when** it passes through `RelayAdapter`, **then**
  `RelayContradictedError` propagates — ⚠ **the adapter does not catch, soften or de-rate it**.
  → *characterization, over the existing `ingest` behaviour.* (`RA-118`, `P5`)
- **AC-9.4** *(de-rating is unchanged)* — **Given** identical evidence coverage, **when** confidence is
  computed through the adapter and directly via `assess_confidence`, **then** the results are equal.
  → *characterization.* (`RA-67`, `AC-1.77`)
- **AC-9.5** *(provenance is on every thesis)* — **Given** a thesis from either adapter, **when** read,
  **then** `provenance` names the port, variant and version that produced it. → *data contract.*
- **AC-9.6** *(the card states its source)* — **Given** a rendered discipline card, **when** its thesis
  came from the relay, **then** the card says so. → *data contract.* (`AP-2`, `DC-1`)
- **AC-9.7** *(★ depth parity)* — **Given** the same ticker authored by each adapter, **when** the two
  theses are compared, **then** they carry the same required fields at the same depth; ⚠ **neither is
  a reduced form of the other**. → *data contract.* (`QR-16`)
- **AC-9.8** *(the API is the default)* — **Given** no explicit variant, **when** the port is resolved,
  **then** `api` is returned. → *unit.* (`QR-20`)
- **AC-9.9** *(unresolvable raises)* — **Given** an unknown ticker, **when** `author` is called,
  **then** it raises; ⚠ **an empty or placeholder thesis is never returned**. → *unit.* (`P5`)
- **AC-9.10** *(both are traced identically)* — **Given** a thesis from either adapter, **when** the
  trace is read, **then** the external calls, the provenance and the step records have the same shape.
  → *data contract.* (`F2`)

## 7. Decisions (resolved questions — kept with their rejected options)

> ✅ **`D1`–`D3` ADOPTED 2026-09-04.**

**`D1` — The relay envelope carries spans, and the port requires them from BOTH adapters.**
*(Resolves `Q1`.)*

- **Decision:** `ThesisSourcePort`'s contract requires an evidence span per factual claim. ⚠ **A port
  whose two adapters make different guarantees is not one port** — callers would have to know which
  variant answered, which is exactly what `F1`'s substitution contract forbids (`AC-1.9`).
- ★ **The relay already re-verifies claims and raises on contradiction** (`QR-20`), so it has the
  machinery; what `Q1` asks is whether the *envelope* carries them across the transport. It must.
- ⚠ **Consequence to accept openly:** if the relay transport cannot carry spans for some answer, that
  answer is **degraded** and must say so — it does not silently arrive span-less. ★ `QR-16`'s *"earn the
  confidence back"* depends on the spans existing; without them there is nothing to earn it with.
- **Rejected — spans optional on the relay path.** Produces two contracts wearing one name, and the
  weaker one wins silently whenever the relay is used.
- **Rejected — spans on the relay only** (API exempt). ⚠ Inverts the risk: the API path is the
  **default** (`QR-20`), so exempting it exempts the common case.

**`D2` — The API adapter uses the SAME prompt spec as the relay. One prompt, two transports.**
*(Resolves `Q2`.)*

- **Measured:** `L1-fundamental-analysis-master-prompt.md` is **1,952 lines** upstream. ★ `QR-20` framed
  the relay as *"a change of transport, not a new architecture"* — `D2` holds the same line from the
  other side.
- ⚠ **Two prompts would make the two adapters incomparable.** `F5`'s golden-set regression and `F7b`'s
  study both partition by variant; if the variants also differ in prompt, every measured difference is
  confounded and no experiment separates transport from instruction.
- **Rejected — a leaner prompt for the API path.** Tempting (cost), and it destroys comparability.
  ★ If a leaner prompt is worth having, it is a **third variant** measured against the first — which is
  what `F1`'s registry is for.

**`D3` — Pull the cost report before `MS-6` closes, and record it as a `MetricResult`.**
*(Resolves `Q3` — `QR-20`'s outstanding action.)*

- **Decision:** the figure lands as an `F5` `CT-5.1` `MetricResult` with its `n` and `inputs_ref`, not
  as a number in a document. ★ `QR-20` chose the API as default *partly on cost*; a decision made on a
  cost estimate should carry the measured cost beside it.
- ⚠ **`AC-5.2` then applies**: a cost figure without its sample size is not publishable, and
  *"one week of runs"* is a very different claim from *"one run"*.
- **Rejected — record it in prose in `questions.md`.** A number in a decision log is never revisited;
  a `MetricResult` accrues a trend and reds when it moves.

## 8. Open questions

> ✅ **All three are resolved** — adopted 2026-09-04. **No open questions remain.**

- **Q1 — Does the relay envelope carry source spans?** `QR-16`'s "earn the confidence back" option
  depends on the relayed report returning claims **with spans** so `ingest()` can verify every one.
  ⚠ If it does not, the relay stays blanket-de-rated and `AC-9.7`'s parity is nominal. **Answerable by
  reading `relay/models.py` at `MS-6`.**
- **Q2 — What is the API adapter's prompt?** The relay has a 463-line prompt spec upstream. Does the
  API path reuse it, or does the master prompt differ? ⚠ If they differ, `AC-9.7`'s parity claim
  weakens and the A/B compares two things at once.
- **Q3 — Cost measurement (`QR-20`'s action).** Pull the usage report before `MS-6` closes and record
  the number in `QR-20`.

## 9. Traceability (spec → test → code)

⚠ **Empty by design** — no code exists yet; no AC may be marked green before its test runs.

| AC | Test | Code module |
|---|---|---|
| AC-9.1, AC-9.7 | *(to be written)* | `tests/contracts/test_thesis_source.py` |
| AC-9.2 | *(to be written)* | `tools/check_no_reimplementation.py` |
| AC-9.3, AC-9.4 | *(to be written — blocked Q1)* | `src/fundamental/source/relay_adapter.py` |
| AC-9.5, AC-9.8 … AC-9.10 | *(to be written)* | `src/fundamental/source/` |
| AC-9.6 | *(to be written)* | `src/reporting/render/` |
