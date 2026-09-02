# F1 — Module protocol & registry (SPI)

> **Spec-ID:** F1 · **Status:** 🟡 draft *(has ACs; not yet approved)* · **Adopted:** —
> **Source discussion:** `sdd/design/rel1_brainstorm.md` §D.5 · §H.1 ·
> [`../../questions.md`](../../questions.md) `QR-7`, `QR-8`
> **Milestone:** `M1` — [`../../design/rel1_design/L3-build-sequence.md`](../../design/rel1_design/L3-build-sequence.md)
> **Governs:** `constitution.md` — enforces `PG-8`, `PG-9`; inherits `P5`, `CA-3`, `AP-6`.
> **Capability:** `C1` (plugin architecture / SPI), and the substrate `C8` (governance) stands on.
>
> ⚠ **`PG-1` blocks implementation** until the inherited pipeline completes a verified
> end-to-end run (`M0`). This spec may be written, reviewed and approved now; **no code
> may be written against it yet.**

---

## 1. Goal & why

**One registry, keyed by `(port, variant)`, through which every swappable implementation in the system
is registered and resolved.** A port declares a contract; adapters implement it; the registry maps a
name to a way of building one; and a single contract-test suite proves every adapter is actually
substitutable.

This is the mechanism behind capability `C1` and behind the **vertical scalability axis**
(`vision.md` §6): a module is improved or replaced behind an unchanged contract without its callers
knowing. It is also what makes `C8` possible — an output can name *which implementation version*
produced it.

★ **It is deliberately first.** `M1` is the only platform milestone with no pipeline dependency: a
registry and a protocol can be built and fully contract-tested in isolation, so this spec is writable
and approvable while `M0` is still in flight.

> ⚠ **The interface is the easy half.** A satisfied type signature does **not** make an implementation
> substitutable — the upstream `MU`-71 % incident is a case where two adapters shared a signature and
> differed in a guarantee nobody had written down. §5's ports must state guarantees, and §6's `AC-1.9`
> is what makes them checkable.

## 2. Scope / non-goals

**In scope**
- The registry: registration, resolution, coverage validation, versioning, experimental tagging.
- The **closed variant set** rule and its consequences (`QR-7`).
- Per-run instance caching.
- `AgentPort` — declared here as **one registered port among several**, not as the registry's purpose.
- The contract-test *harness pattern* every port must use.

**Non-goals (this spec)**
- ✗ **Hot reload / code swap without restart** — cut by `QR-7`, and a durable non-goal (`vision.md` §7).
- ✗ **Lazy or dynamic variant discovery** — excluded by the closed-set rule; see `AC-1.5`.
- ✗ **A dependency-injection container.** Resolution happens at a composition root and the resolved
  object is passed downward. This spec does not introduce framework-wide injection.
- ✗ **The semantics of any particular port.** `PricePort`, `RankingModelPort`, `ThesisSourcePort` (`F9`)
  and the rest each define their own contract in their own spec. F1 defines only the *mechanism* and
  the *obligations a port declaration must meet*.
- ✗ **Routing** — choosing *which* variant is `F6a`. F1 only resolves the name it is given.
- ✗ **Tracing** — recording the resolution is `F2`. F1 must *expose* the provenance record (`CT-1.4`);
  it does not persist it.

## 3. Users & triggers

| ID | Trigger | Input / selection | Entry point (code) |
|---|---|---|---|
| T1 | Process start — every variant is registered | module import / explicit wiring call | `src/shared/registry/wiring.py::register_all` |
| T2 | Process start — coverage is validated before work begins | list of required ports, from config | `Registry.validate_coverage` |
| T3 | Composition root resolves an implementation | `(port, variant)`; variant from config (`T3a`) or from a routing function (`T3b`, `F6a`) | `Registry.resolve` |
| T4 | Test suite enumerates variants to run a contract suite against | `port` | `Registry.variants` |

## 4. Behaviour & reuse (the lean "how")

- **Ports are pure typing.** A port is a `typing.Protocol` in a module containing declarations only —
  no implementation, no I/O, no SDK import. Inherits `CA-3`. ★ Structural typing is chosen over `ABC`
  so a third-party or upstream class can satisfy a port without inheriting from it, which matters at
  absorption (`PG-8`).
- **The registry stores factories, not instances.** Registering a live object would force construction
  at import time and couple registration order to configuration.
- **Registration is fail-loud.** A duplicate `(port, variant)` raises. ⚠ Silent overwrite makes import
  order load-bearing — inherits `P5`.
- **The variant set is closed.** Everything selectable is registered at startup; resolution never
  discovers, imports or loads a variant that was not (`QR-7`). ★ This is what makes the hot-reload
  non-goal *structural* rather than merely stated.
- **Coverage is validated once, at startup.** ⚠ The registry is a *service locator*: it trades a
  compile-time error for a runtime one. `validate_coverage()` is the mitigation that turns a 3 a.m.
  `KeyError` into a boot failure.
- **Resolution caches per `(port, variant)` within a run scope.** A model load is expensive and
  per-ticker selection may resolve the same variant hundreds of times.
- **Every entry carries a version**, and every resolution yields a provenance record, so an output can
  answer *"which implementation produced this?"* (`AP-6`, `C8`).
- **Experimental variants are tagged and the tag propagates.** Seat 9 swaps an experimental variant in,
  runs the pipeline, swaps it back; ⚠ nothing it produces may be mistakable for production output
  (`PG-2`).
- **One contract suite per port, parameterised over every registered variant.** ★ This — not the
  registry — is what makes substitution *safe*.

## 5. Contracts (inline)

**CT-1.1 — `Key`** (in-memory; the registry's key):
```json
{ "port":    "str — stable port name, e.g. 'price', 'ranking_model', 'agent.fundamental'",
  "variant": "str — stable variant name, e.g. 'edgar', 'lightgbm', 'scorecard'" }
```
Rules: both non-empty; `[a-z0-9_.]+`; the pair is unique across the registry; **neither is ever
renumbered or reused for a different implementation** — they appear in provenance records that outlive
the code.

**CT-1.2 — `Entry`** (in-memory; what a registration stores):
```json
{ "factory":      "Callable[..., object] — builds the implementation; NOT the instance",
  "version":      "str — semver of the IMPLEMENTATION, not of the port",
  "experimental": "bool — default false",
  "port_type":    "type — the Protocol this entry claims to satisfy" }
```

**CT-1.3 — Registry API surface:**
- `register(port, variant, factory, version, experimental=False) -> None`
  → raises `DuplicateRegistration` if `(port, variant)` exists.
- `resolve(port, variant, **kwargs) -> object`
  → raises `UnknownVariant(port, variant, available)` — ⚠ **`available` is required**, so a typo
  diagnoses itself.
- `variants(port) -> tuple[str, ...]` → registered variant names, sorted. Used by T4.
- `validate_coverage(required_ports) -> None` → raises `IncompleteRegistry(missing)`.
- `provenance(port, variant) -> Provenance` → `CT-1.4` without constructing the implementation.

**CT-1.4 — `Provenance`** (returned by `resolve` and by `provenance`; consumed by `F2`):
```json
{ "port": "str", "variant": "str", "version": "str", "experimental": "bool" }
```
Rules: immutable; **fully determined by the registry entry**, never by the resolved object.

**CT-1.5 — `AgentPort`** (one registered port among several):
```json
{ "capability": "property -> AgentCapability — seat, domain, version, supported message types",
  "analyze":    "(ticker: str, context: Mapping) -> Mapping — this seat's view of one ticker" }
```
⚠ Message handling (`respond_to_message`) is **not** in F1 — it belongs to `F6b` and is added there if
and when `F6b` graduates (gated on `F7a`, `PG-5.1`).

## 6. Acceptance criteria (Given / When / Then → test tier)

- **AC-1.1** *(duplicate registration is loud)* — **Given** `(port, variant)` is registered, **when**
  the same pair is registered again, **then** `DuplicateRegistration` is raised and the first entry is
  unchanged. → *unit.* (`P5`)
- **AC-1.2** *(unknown variant names the alternatives)* — **Given** a registry with variants of `port`,
  **when** an unregistered variant of that port is resolved, **then** `UnknownVariant` is raised **and
  its message lists the registered variants for that port**. → *unit.* (`P5`)
- **AC-1.3** *(factories, not instances)* — **Given** a registered factory, **when** registration
  occurs, **then** the factory is **not** invoked; **when** `resolve` is first called, **then** it is.
  → *unit.*
- **AC-1.4** *(coverage fails at boot)* — **Given** a required port with no registered variant, **when**
  `validate_coverage` runs, **then** `IncompleteRegistry` is raised naming every missing port. → *unit.*
- **AC-1.5** *(★ the variant set is closed)* — **Given** any variant name not registered at startup,
  **when** it is resolved, **then** `UnknownVariant` is raised — **and no import, module load or
  filesystem lookup is attempted**. → *invariant / property.* (`QR-7`; makes `vision.md` §7's
  hot-reload non-goal structural)
- **AC-1.6** *(per-run caching)* — **Given** a registered factory, **when** the same `(port, variant)`
  is resolved `n > 1` times within one run scope, **then** the factory is invoked **exactly once** and
  every call returns the same object. → *unit.*
- **AC-1.7** *(⚠ reuse is a port obligation)* — **Given** any registered variant, **when** its
  `analyze`-equivalent entry point is invoked twice with identical inputs on the same instance,
  **then** both calls return equal results — i.e. **no caller-visible state carries between calls**.
  → *invariant / property, run against every registered variant.* (the obligation `AC-1.6`'s caching
  depends on)
- **AC-1.8** *(provenance is complete and entry-derived)* — **Given** a resolution, **when**
  `Provenance` is read, **then** it carries `port`, `variant`, `version` and `experimental`, and its
  values equal the registry entry's — **not** anything reported by the resolved object.
  → *data contract.* (`AP-6`, `C8`)
- **AC-1.9** *(★★ every variant faces the same contract suite)* — **Given** a port with a contract
  suite, **when** the suite runs, **then** it executes once per name in `registry.variants(port)`, and
  **a variant registered without being added to the suite causes a failure**. → *invariant / property
  (meta-test over the parameterisation).* (`A3` — the rule that makes substitution safe)
- **AC-1.10** *(ports carry no implementation)* — **Given** any module declaring a port, **when** it is
  inspected, **then** it contains only `Protocol` declarations, type aliases and imports **from
  `typing`/stdlib typing modules** — no I/O, no vendor SDK import, no executable statement at module
  scope. → *invariant / property (structural).* (`CA-3`, `A2`)
- **AC-1.11** *(experimental output is never mistakable for production)* — **Given** a variant
  registered with `experimental=True`, **when** it is resolved, **then** `Provenance.experimental` is
  `True`; and **when** any artifact is produced from it, **then** that artifact carries the flag.
  → *data contract.* (`PG-2`)
- **AC-1.12** *(a port declaration is earned)* — **Given** a port in `src/shared/`, **when** the
  registry is validated, **then** it has **at least two registered variants**, of which a fixture or
  test double counts as one. → *invariant / property.* (`A4`; ⚠ *blocked — Q1*)

## 7. Open questions (must resolve before/at implementation)

- **Q1 — What is a "run scope"?** `AC-1.6` caches "within one run scope". For a once-daily batch that
  is the process lifetime; but `F8`'s control surface is long-lived and serves many runs, and a cached
  model there would outlive the data it was built for. **Options:** process-lifetime cache (simplest,
  wrong for `F8`); an explicit `RunScope` object threaded through resolution (correct, more plumbing);
  cache keyed by `(port, variant, run_id)` (middle). ⚠ Blocks `AC-1.6`'s precise wording.
- **Q2 — Where does `required_ports` come from?** `validate_coverage` needs a list. From config, or
  from a declared manifest in code? A config list can drift from reality silently; a code manifest
  cannot, but is another thing to keep current. Blocks `AC-1.4`'s fixture.
- **Q3 — Is the registry accessed concurrently?** If `F6b`'s agents ever run in parallel, both
  registration (startup-only, so probably safe) and the `AC-1.6` cache (definitely not) need
  thread-safety. Deferring is acceptable **only if** the answer is recorded, not assumed.
- **Q4 — Does `AC-1.12` hold for `AgentPort` on day one?** At `M1` there may be exactly one agent
  implementation plus a stub. If the stub does not count, `AC-1.12` fails and either the AC or the
  port must move. ⚠ This is `A4` ("abstraction is earned") meeting reality — resolve before approval.

## 8. Traceability (spec → test → code)

⚠ **Empty by design.** `PG-1` blocks implementation until `M0` completes; no test may be marked green
before it has been run.

| AC | Test (file::test) | Code module |
|---|---|---|
| AC-1.1 | *(to be written)* | `src/shared/registry/registry.py` |
| AC-1.2 | *(to be written)* | `src/shared/registry/registry.py` |
| AC-1.3 | *(to be written)* | `src/shared/registry/registry.py` |
| AC-1.4 | *(to be written)* | `src/shared/registry/registry.py` |
| AC-1.5 | *(to be written)* | `src/shared/registry/registry.py` |
| AC-1.6 | *(to be written — blocked Q1)* | `src/shared/registry/registry.py` |
| AC-1.7 | *(to be written)* | contract suite, all variants |
| AC-1.8 | *(to be written)* | `src/shared/registry/provenance.py` |
| AC-1.9 | *(to be written)* | `tests/contracts/conftest.py` |
| AC-1.10 | *(to be written)* | structural test over `src/shared/**/ports.py` |
| AC-1.11 | *(to be written)* | `src/shared/registry/provenance.py` |
| AC-1.12 | *(to be written — blocked Q4)* | structural test |
