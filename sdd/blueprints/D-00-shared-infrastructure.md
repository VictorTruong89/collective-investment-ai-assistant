# Blueprint — D-00 Shared Infrastructure

> **Code:** `src/shared/` · **Specs:** `sdd/design/rel6_design/L2-shared-infrastructure.md` ·
> `sdd/design/rel6_design/L2-shared-money.md` · **Seat:** none (cross-cutting)
> **Status:** written 2026-08-23 at B0 · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **This describes the CODE, not the spec.** A sentence here that would still be true if the code
> were rewritten differently belongs in the spec (DR-1).

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-23 | A same-currency ratio returns **`Decimal`**, not `float` | ⚠ **The spec contradicts itself**: `FR-002` says Decimal, `MO-8` says "a plain float". FR-002 is the functional contract, and `AC-M.20` only requires "dimensionless and leaves the Money type" — which Decimal satisfies without reintroducing the float MO-4 exists to keep away | `float` — matches MO-8's wording, but loses exactness for no gain. **Flagged for the spec to settle; not silently resolved** |
| 2026-08-23 | `Config.get()` raises; **`get_optional()` added** | An earlier draft had one getter, and every gateway probe for a key that must be ABSENT (`llm.deep.temperature`) raised `MissingConfigKeyError` on a *correct* config. 19 tests failed | A sentinel default on `get()` — that is precisely how a silent default is born (CF-1) |
| 2026-08-23 | `logging.configure()` split from `logger()` | The first draft configured root logging lazily on first `logger()` call. **The suite caught what that costs**: whichever test ran first silently replaced every handler installed by anything else, so behaviour depended on collection order | Lazy auto-configuration — convenient, and it makes the module impossible to compose |
| 2026-08-23 | Architecture rules parse **imports (AST)**, not text (grep) | `L4` §10.1 states ST-5 as `grep -rn "llm" src/ \| grep -v …`, which matches the *string* anywhere — **a docstring in `src/reporting/` mentioning the gateway would fail the build**. The rule is about imports | Following the grep literally. Rejected: a check that false-positives on prose is a check someone deletes |
| 2026-08-23 | `transport` is a **plain injected callable**, no `Protocol` | `QI-5` closed: Anthropic only, so `CA-5`'s port is not required and `L4 CA-7` forbids speculative abstractions. Injection is for **hermeticity**, not for a second provider | A `TransportPort` Protocol — speculative generality for a provider that will not exist |
| 2026-08-23 | `Outcome` has **no `partial` member** | GW-22 made structural rather than documented. Both real incidents came from treating a partial as a success; an enum without the member makes it unrepresentable | A `partial` member plus a rule forbidding its use — a rule that has to be remembered at every call site |

---

# 1. What this domain does, in one paragraph

Four services every domain needs and no domain should own: **money** (an exact amount inseparable
from its currency), the **LLM gateway** (a transport with guards, called only by D-01), **config**
(load once, validate, freeze) and **secrets** (environment only, redacting by type). Plus the error
hierarchy and structured logging everything else raises and writes through. It holds **no business
rule, no threshold and no verdict** — a rule placed here would be one nobody owns and everybody
obeys, invisible to the seat model and to every review that works domain by domain.

# 2. The objects and how they flow

```text
   application entry point
        │
        ├─ secrets.require()          ← SC-2, at STARTUP, all four at once
        ├─ config.load_config(paths)  ← CF-1 validate, CF-4 freeze
        ├─ logging.configure(stream)  ← installs the JSON handler ONCE
        │
        └─ Gateway(config, transport=…, alignment=…, log=…)
                 │
                 │  D-01 only (GW-1 / ST-5)
                 ▼
            gateway.call(prompt_name, prompt_version, tier, payload, …)
                 │
                 ├─ alignment check ──► DriftBlockedError   (no request sent)
                 ├─ decoding_for(tier, cfg) ──► DecodingControlError
                 ├─ transport(request)  ──► retry loop, TRANSPORT errors only
                 ├─ stop_reason gate ──► TruncatedError | RefusedError
                 ├─ schema(text) ──► UnparseableError
                 └─ budget.charge ──► BudgetExceededError
                          │
                          ▼
                    Response(text, parsed, call: LLMCall)
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `Money` | `src/shared/money.py` | every boundary that reads an amount | all domains | immutable value |
| `FxRate` | `src/shared/money.py` | D-07 | `Money.convert` | immutable value |
| `Config` | `src/shared/config.py` | entry point, once | everything | the run (CF-2) |
| `ConfigManifest` | `src/shared/config.py` | `Config.manifest()` | D-08 RunManifest | the run |
| `Secret` | `src/shared/secrets.py` | `require()` at startup | the gateway | process lifetime |
| `LLMCall` | `src/shared/llm/gateway.py` | every gateway call | D-08, D-11 | append-only record |
| `Decoding` | `src/shared/llm/gateway.py` | `decoding_for` | `LLMCall` | per call |

★ **The object that will surprise a reader: `_Budget` holds state on the `Gateway` instance.**
Everything else in D-00 is a pure value or a frozen mapping. The budget accumulates because
**GW-20 is a per-run cap**, so one gateway instance is one run. ⚠ Sharing a `Gateway` across two
runs would silently merge their budgets — the instance lifetime *is* the budget scope, and nothing
in the type says so.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | require secrets | `src/shared/secrets.py::require` | **SC-2** — at startup, or a nightly run dies forty minutes in having spent tokens | `SecretAbsentError`, all missing names in one message |
| 1 | load + freeze config | `src/shared/config.py::load_config` | **CF-1/CF-2** — read once at the edge; a value re-read deep in a stack can resolve differently within one run | `MissingConfigKeyError` |
| 2 | configure logging | `src/shared/logging.py::configure` | explicit, so the library never hijacks the application's handlers | — |
| 3 | alignment | `src/shared/llm/gateway.py::Gateway.call` | ★ **GW-12 — before the request is built.** Checking after the call would check nothing | `DriftBlockedError`, no request sent |
| 4 | decoding controls | `src/shared/llm/gateway.py::decoding_for` | ★ **GW-8a — before the request leaves**, so the failure names the rule instead of arriving as a provider 400 | `DecodingControlError` |
| 5 | transport + retry | `src/shared/llm/gateway.py::Gateway.call` | **GW-15** — transport retry lives here, beneath the domain layer; a declared exception to D-08 OR-14 | `TransportError` after bounded attempts |
| 6 | stop-reason gate | same | ★ **GW-23/GW-22** — a truncation is a failure, not a short answer | `TruncatedError` · `RefusedError` |
| 7 | schema parse | same | **GW-3** — parse and raise; what it *means* is D-01's | `UnparseableError` |
| 8 | charge budget | `_Budget.charge` | ★ **after success only** — a failed call is recorded but never billed as work | `BudgetExceededError` |

⚠ **Step 8 after step 7 is deliberate and slightly counter-intuitive**: a truncated call *did* consume
provider tokens, and we do not charge it. The budget measures **work delivered**, not tokens burned,
because GW-20's purpose is to stop a runaway *from producing output nobody asked for*. The tokens are
still recorded on the `LLMCall`, so the discrepancy is visible rather than hidden.

# 4. ★ The mathematics

### Minor-unit quantization

| | |
|---|---|
| **Implemented in** | `src/shared/money.py::_quantize_to_int` |
| **Formula** | ```python\nreturn int(value.quantize(_ONE, rounding=rounding))\n``` |
| **Units** | in: `Decimal` scaled to minor units · out: `int` minor units. ★ **Never a currency-free number** — the caller pairs it with a code |
| **Domain / range** | any finite `Decimal`. NaN is rejected upstream in `from_decimal_str` |
| **Why this form** | Integers are exact, hash cleanly, serialise unambiguously and compare without tolerance. `Decimal` appears only as an intermediate (MO-5) |
| **Alternatives rejected** | `float` — the recorded defect (see below). `Decimal` as a *stored* field — reintroduces the precision-and-serialisation questions the integer removes |
| **Sensitivity** | The rounding **mode** dominates, not the precision. `ROUND_HALF_UP` vs `ROUND_HALF_EVEN` differs on exactly the `.5` boundary — which is where money lands constantly |
| **★ Worked example** | `Money.from_decimal_str("1.00","USD")` → `100` minor. `.mul_rate(Decimal("1.365"))` → `Decimal(100) * 1.365 = 136.5` → quantize HALF_UP → **`137`** → `$1.37`. ⚠ The legacy float path returned **`1.36`** |
| **Known-wrong** | none known |

> ★ **The recorded defect this exists to prevent** (AC-M.19): two error sources compounded —
> binary representation error in `float(rate)`, and the builtin `round()` being **banker's**
> rounding where money requires half-up. ⚠ **The resulting cent errors were systematically
> DOWNWARD**, so they did not cancel across many conversions the way symmetric noise would.

### Multi-step quantization — quantize ONCE

| | |
|---|---|
| **Implemented in** | `src/shared/money.py::Money.from_minor_decimal` |
| **Why this form** | §4.3 — quantizing at each step accumulates error. Carry `Decimal` through `weight × price × quantity × fx` and quantize at the boundary where a `Money` is returned |
| **★ Worked example** | `100.05 USD` = `10005` minor, × `0.333` × `0.333` × `7`:<br>**once:** `10005 × 0.333 = 3331.665` → `× 0.333 = 1109.444445` → `× 7 = 7766.111115` → **`7766`**<br>**stepwise:** `3331.665→3332` → `3332×0.333 = 1109.556→1110` → `×7 = ` **`7770`**<br>★ **A 4-cent divergence on one three-step chain.** Frozen by `tests_src/test_money.py::test_multi_step_computation_quantizes_once` |
| **Known-wrong** | none known |

### Call cost

| | |
|---|---|
| **Implemented in** | `src/shared/llm/gateway.py::Gateway._cost` |
| **Formula** | ```python\ntokens_in / 1_000_000 * input_per_mtok\n+ tokens_out / 1_000_000 * output_per_mtok\n``` |
| **Units** | tokens → USD. ⚠ **`float`, not `Money`** — see known-wrong below |
| **Why this form** | Provider pricing is quoted per million tokens; prices come from config (CN-1) so a price change is a config edit, not a code change |
| **Alternatives rejected** | Hard-coded prices — they change without warning and would make every `L2 §7B` figure quietly stale |
| **★ Worked example** | 1000 in / 500 out on `claude-opus-5` at $5/$25 per MTok: `0.001×5 + 0.0005×25 = 0.005 + 0.0125 =` **`$0.0175`** |
| **Known-wrong** | ⚠ **yes — see §10.1** |

# 5. The logic decisions

| Decision | Where | What it does | Why this way | What it would take to change it |
|---|---|---|---|---|
| Tier → decoding control | `src/shared/llm/gateway.py::decoding_for` | deep ⇒ `effort`; cheap ⇒ `temperature` | ★ The two are **mutually exclusive** at the provider: Opus 5 rejects `temperature` with a 400; Haiku 4.5 errors on `effort` | A model change. **GW-9b says that re-baselines** |
| Retry classification | `src/shared/llm/gateway.py` `_RETRYABLE_HINTS` | retry only on `429/5xx/timeout/connection` | EH-15 one layer down: retry the request that got **no real answer**; never the answer you disliked | Adding a hint — and each addition widens what gets retried, so it is a decision, not a tweak |
| Unclassified ⇒ **no** retry | same | a `TransportError` matching no hint is raised, not retried | EH-14's default. ⚠ Retrying the unknown is how a semantic failure gets retried by accident | — |
| `max_attempts = 3` | `Gateway.__init__` | bounded retry | ⚠ **Provisional — never measured.** Chosen as a conventional default | A measurement of real 429 patterns, which needs live traffic |
| Budget charged on success only | `Gateway.call` step 8 | failures recorded, not billed | GW-20 caps *work produced*, not tokens burned | A stated decision that the cap is a spend cap; the tokens are already recorded either way |

★ **`max_attempts = 3` is the only magic number in this domain**, and it is marked provisional rather
than justified. Every other constant is either in config or derived from a spec rule.

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Range | Who reads it | Changing it affects |
|---|---|---|---|---|---|
| deep model | `llm.deep.model_id` | none — **required** | a model id | `Gateway.call` | ★ re-baselines everything (RM-5) |
| deep effort | `llm.deep.effort` | none — **required** (GW-9a) | `low…max` | `decoding_for` | ★ **re-baselines (GW-9b), and nothing fires yet** |
| deep thinking | `llm.deep.thinking_mode` | `adaptive` | `adaptive` only | `decoding_for` | `disabled` is refused (GW-9c) |
| cheap model | `llm.cheap.model_id` | none — **required** | a model id | `Gateway.call` | re-baselines cheap-tier work |
| cheap temperature | `llm.cheap.temperature` | none — **required** (GW-8) | `0.0` in production | `decoding_for` | RM-1's baseline |
| ⚠ deep temperature | `llm.deep.temperature` | **must be ABSENT** | — | `decoding_for` probe | its *presence* is the error |
| run budget | `llm.budget.usd_per_run` | none — **required** | USD | `_Budget` | ★ **QI-2 — the number is Victor's, not D-00's** |
| pricing | `llm.pricing.<model>.{input,output}_per_mtok` | none — **required** | USD/MTok | `Gateway._cost` | every §7B figure |

⚠ **Hard-coded and arguably config:** `max_attempts=3` (constructor default) and
`_RETRYABLE_HINTS` (module constant). Both are transport policy rather than investment policy, so
they sit in code under **SI-2** — but they are listed here because a reader looking for a knob will
look for them.

# 7. Inputs and outputs

| Direction | Contract | Shape | Producer / consumer | What happens if malformed |
|---|---|---|---|---|
| out | `CT-0.1 LLMCall` | `to_json_obj()` | → D-08 RunManifest, D-11 | serialisation asserted in tests; a non-serialisable field fails the suite |
| out | `CT-0.2 ConfigManifest` | `to_json_obj()` | → D-08 | ★ secrets cannot appear — refused at `_flatten`, not filtered on exit |
| out | `CT-M.1` parquet | `{name}_minor` int64 + `{name}_currency` str | → D-07 | a `_minor` with no `_currency` sibling raises `InvalidAmountError` |
| out | `CT-M.2` JSON | `{"minor": int, "currency": str}` | → any artifact | nested so a careless field selection cannot split the pair |
| in | transport reply | `{text, stop_reason, tokens_in, tokens_out}` | ← provider | missing `text` ⇒ `UnparseableError` (the *absent narrative* incident) |

# 8. Failure behaviour

| Failure | Detected where | Behaviour | Visible to whom |
|---|---|---|---|
| secret absent | `src/shared/secrets.py::require` | raise at startup | operator, before any spend |
| required key absent | `src/shared/config.py::ConfigSpec.validate` | raise at load | operator |
| config mutated | `src/shared/config.py::Config.__setattr__` | raise | the mutating caller |
| prompt drift | `src/shared/llm/gateway.py::Gateway.call` | raise, **no request sent** | D-01 |
| wrong decoding control | `src/shared/llm/gateway.py::decoding_for` | raise **before** the request | D-01, naming the rule |
| transport 429/5xx | retry loop | bounded retry, then raise | recorded in `retry_reasons` |
| truncation / refusal | stop-reason gate | raise | D-01 |
| empty or unparseable | schema gate | raise | D-01 |
| budget exceeded | `_Budget.charge` | raise, run fails | operator |

★ **No path in this domain returns a default on bad input** (P5). The `Response` type is only ever
constructed on the success path — `src/shared/llm/gateway.py::Gateway.call` builds it once, after
every gate.

# 9. What this domain deliberately does NOT do

| Not here | Owner |
|---|---|
| what to ask the model | D-01 |
| what the config *means* (`δ = 2.19` sane?) | the owning domain (CF-5) |
| fetching FX rates | D-07 |
| deciding when to convert | the calling domain |
| formatting money for display | D-09 |
| the audit trail | ★ **D-11** — a log is *not* the audit trail (LG-1) |
| any threshold or verdict | whichever domain means it (SI-2) |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — cost is a `float`, not `Money`** | ⚠ medium | `Gateway._cost` returns a float and `_Budget` accumulates floats. **INV-001 says a monetary value is an integer amount plus a currency**, and this is neither. Rounding drift is negligible per call and accumulates across a run | ★ **New — no ID yet.** Money is USD-denominated while the book is CAD (M-5), so fixing it needs a `Money` in USD and an FX step to report spend in base |
| **10.2 — `max_attempts = 3` never measured** | low | retry behaviour under real rate limits is unknown | §5, marked provisional |
| **10.3 — `AC-0.4c` is partial** | ⚠ medium | `Decoding.fingerprint()` makes an effort change *comparable*; **nothing re-baselines on it.** RM-5 lives in D-01, which does not exist | GW-9b · D-01 RA-60a |
| **10.4 — Haiku model id unverified** | ⚠ medium | constitution INV-8 names `claude-haiku-4-5-20251001`; the current model table says `claude-haiku-4-5`. **GW-5 resolves it from config, so the wrong string fails at the first cheap-tier call** | L2 §5.2a's "verify at B0" note — **still open** |
| **10.5 — no production transport yet** | ⚠ expected | `transport` is injected and every test is hermetic. **Nothing has ever called Anthropic through this gateway** | B0 scope; the wrapper lands with D-01's first real call |
| **10.6 — `FR-002` vs `MO-8` disagree** | low | same-currency ratio returns `Decimal`; MO-8's text says "plain float" | Decision log, row 1 — **the spec should settle it** |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_money.py` · `tests_src/test_shared_infra.py` · `tests_src/test_gateway.py` — each docstring names its AC |
| 2 | ★ **Break it and confirm red** | In `src/shared/money.py::_quantize_to_int`, change `rounding=rounding` to `rounding="ROUND_HALF_EVEN"`. `test_mul_rate_rounds_half_up_not_bankers` must fail — it is the legacy defect, reproduced |
| 3 | The worked examples (§4) reproduce | `python -c "from decimal import Decimal as D; from src.shared.money import Money; print(Money.from_decimal_str('1.00','USD').mul_rate(D('1.365')))"` → `137` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` — the `blueprint pointers resolve` check |
| 5 | ★ **Checked against external truth?** | ⚠ **No — self-consistency only.** No test here calls a real API. The Haiku id (10.4) and the real transport (10.5) are both unverified against the provider. **This domain has no reality probe** |

★ **Check 5 is the honest limit of this blueprint.** Everything here is internally consistent and
none of it has met the provider.

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L2-shared-infrastructure.md` | GW-1…GW-23, CF-1…CF-5, LG-1…LG-5, SC-1…SC-4, §5.2a |
| `sdd/design/rel6_design/L2-shared-money.md` | MO-1…MO-10, FX-1…FX-3, CT-M.1…CT-M.3 |
| `sdd/design/rel6_design/L3-build-sequence.md` | B0's scope; BS-4/BS-5; **BS-31** (this file's obligation) |
| `sdd/design/rel6_design/L4-coding-standards.md` | §1.1 layout · §10.1 the checked import edges · EH-14/15 · CN-1…CN-5 |
| `sdd/specs/constitution.md` | P5 · INV-5 · INV-8 · INV-9 |
| `backups/pipeline/portfolio/money.py` | prior art (P4) — the exactness discipline, **not** the API |
