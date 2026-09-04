# L2: Module Specification — Shared Infrastructure (D-00, non-money)

> ⚠⚠ **ABSORBED COPY — this is now the AUTHORITATIVE one.** `src/shared/` moved into
> `collective-investment-ai-assistant` on 2026-09-04 (`questions.md` `QR-22` — absorption is
> per-domain). The code this spec governs lives **here**, so this spec is edited **here**.
> ⚠ `../ai-investment-pipeline` still carries a copy because ~10 of its documents cross-reference it;
> that copy is **historical** and must not be edited. It is reconciled at `MS-8`.
> **Path deliberately mirrors upstream's** (`sdd/design/rel6_design/`) so `MS-8` is a merge, not a
> move (`PG-8`).

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **v0.22.0** §4.2 · **Domain:** D-00 · **Seat:** none (cross-cutting)
> **Path:** `src/shared/{llm,config,logging,secrets}/` ([`L4-coding-standards.md`](L4-coding-standards.md) §1.1)
> **Sibling:** [`L2-shared-money.md`](L2-shared-money.md) — D-00's fourth duty, already specified
> **Binding:** **INV-8** (model tiering) · **INV-9** (prompt alignment) · **INV-034** ·
> **AP-5** / **ST-5** · **P5** · **DC-3** · L4 **CN-1…CN-5**, **EH-14/15**

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.3.0 | 2026-08-23 | Victor | ⚠ **GW-8/GW-9 AMENDED — §5.2a.** Raised as D-01 **QP-1** on 2026-08-20, never propagated to the owning spec, and surfaced again as a **B0 blocker**: the gateway is built at B0 and **`AC-0.4` as written could not pass.** ★★ **`claude-opus-5` REJECTS `temperature` with a 400**; the deep-tier control is `output_config.effort`, and the two tiers take **mutually exclusive** controls (Haiku takes temperature and errors on effort; Opus 5 the reverse). **GW-8a, GW-9a/b/c added.** ★★ **GW-9b is the clause that adds rather than corrects: an `effort` change re-baselines like a model change, and RM-5 does not fire on it today** — a live, un-baselined decoding control, which is *worse* than the unset temperature GW-9 was written to fix. ★ **GW-9c**: thinking is never disabled on deep, because Opus 5 can then write a tool call into visible text — the turn succeeds, the call never runs, **and D-01's extraction would present as a document that said nothing.** `CT-0.1.decoding` becomes an object so `null` means *not settable* rather than *forgotten*. **AC-0.4a–d added; QI-1 narrowed; QI-4 opened.** |
| 0.2.0 | 2026-08-18 | Victor | ✅ **QI-4 and QI-5 closed.** `max_tokens` is **per call site** with `settings.yaml`'s existing values reused (16000/32000/8000/256) — ★ **the current config already gets this right**, so GW-7a preserves a pattern rather than introducing one. **GW-7b** notes the consequence of adaptive thinking: the response budget is the ceiling *minus unknowable thinking*, so truncation is **caught, not predicted**. **One provider (Anthropic) ⇒ CA-5's port is not required** — and INV-8's tiering is a *model* swap, not a *provider* swap. |
| 0.1.0 | 2026-08-18 | Victor | Initial draft, closing the last domain gap. §5.3 resolves the **temperature contradiction** — D-01's RA-60 requires temperature be set and RM-1 measures variance that only exists if it is *not* zero; §5.5 declares the **retry exception to D-08 OR-14** that LLM calls have been silently relying on; §5.6 gives **token accounting an owner**, which every dollar figure in `L2-signal-combination.md` §7B was already priced against. |

---

# 1. DOMAIN CONTEXT

## 1.1 Purpose

> **"The services every domain needs and no domain should own."**

The LLM gateway, configuration, structured logging and secret handling. Money is the fourth duty and
is specified separately.

## 1.2 ★ The defining constraint

```text
╔═══════════════════════════════════════════════════════════════════╗
║  D-00 IS IMPORTED BY EVERYTHING, SO IT MAY CONTAIN NOTHING        ║
║  ANYONE COULD DISAGREE WITH.                                      ║
║                                                                   ║
║  A business rule placed here becomes a rule NOBODY OWNS AND       ║
║  EVERYBODY OBEYS — invisible to the seat model, to ownership.yaml ║
║  and to every review that works domain by domain.                 ║
║                                                                   ║
║  It has no seat, no authority level, and no judgement. Its        ║
║  correctness is entirely mechanical, which is what makes it safe  ║
║  to sit beneath twelve domains.                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

## 1.3 Boundary

```text
  IN SCOPE                            OUT OF SCOPE
  ✓ the LLM transport + its guards    ✗ what to ask the model      -> D-01
  ✓ config loading and validation     ✗ what the config MEANS      -> owning domain
  ✓ structured logging                ✗ ★ the audit trail          -> D-11 (§7)
  ✓ secret retrieval                  ✗ any business rule          -> §1.2
```

---

# 2. DEPENDENCIES

```text
   D-00 ──► NOTHING.  It imports no domain, ever.

   ★ That is not tidiness — it is what makes D-00 safe to be imported by all
     twelve. A single edge outward creates a cycle with whichever domain it
     touches, and the cycle is undetectable from inside either one.
```

| ID | Rule |
|---|---|
| **SI-1** | ★ **`src/shared/` imports no `src/<domain>/`.** Grep-checkable in CI alongside ST-2/5/9/10 (L4 §10.1). **A shared module that knows about a domain is that domain's module in the wrong folder** |
| **SI-2** | D-00 contains **no business rule, no threshold, no verdict, no judgement** (§1.2). A constant with an investment meaning belongs to the domain that means it (L4 CN-1) |

---

# 3. MODULE DECOMPOSITION

```text
src/shared/
├── llm/          # the gateway — §5.  ★ imported ONLY by src/fundamental/ (ST-5)
├── config/       # load, validate, freeze — §6
├── logging/      # structured, correlated — §7
├── secrets/      # environment only — §8
└── money.py      # L2-shared-money.md
```

Internal layering follows **L4 §18** (`CA-0`); it is not restated here.

---

# 4. THE LLM GATEWAY — what it is

**A transport with guards.** It takes a fully-formed request and returns a checked response. It
does not compose prompts, choose models per call, interpret output, or decide anything.

| ID | Rule |
|---|---|
| **GW-1** | ★ **The gateway is imported only by `src/fundamental/` (D-01)** — AP-5, ST-5. **D-09 renders LLM-authored text it did not request** (DC-1) and therefore does not import the gateway either |
| **GW-2** | The gateway **composes no prompt**. It receives a prompt with a name and version and sends it. Authoring is D-01's |
| **GW-3** | The gateway **interprets no output**. It parses to the declared schema and raises on failure; what the content *means* is D-01's |

---

# 5. THE GUARDS

## 5.1 Model tiering — INV-8

| ID | Rule |
|---|---|
| **GW-4** | ★ **The tier is a property of the CALL SITE, declared statically — never chosen at runtime from data.** A gateway that picks a model based on the input is making a cost/quality judgement, which §1.2 forbids it to hold |
| **GW-5** | ★ **Model IDs live in config, not in code** (L4 CN-1: a policy choice). `claude-haiku-4-5-20251001` and `claude-opus-5` are values, and a model change is a **decision with a re-baselining cost** (D-01 RM-5) |
| **GW-6** | ★ **The resolved `model_id` is recorded on every call** and reaches the RunManifest (D-08 OR-9). **A model that changed without the manifest changing makes every prior measurement incomparable and nothing would notice** |
| **GW-7a** | ★ **`max_tokens` is declared PER CALL SITE, never once globally.** Values (`settings.yaml`, reused): deep synthesis **16000**, report composition **32000**, per section **8000**, classifier **256**. ⚠ **A single global value either starves the cheap calls or truncates the deep ones** — and only the second is fatal (GW-23) |
| **GW-7b** | ⚠ **With adaptive thinking the response budget is `max_tokens` MINUS whatever thinking consumed, and that is not knowable in advance.** So the ceiling cannot be tuned to fit — it is set with headroom and **truncation is caught, not predicted** (GW-23) |
| **GW-7** | **Opus-tier calls declare `max_tokens` headroom for thinking.** INV-8 records that Opus 5 runs adaptive thinking by default and `max_tokens` caps thinking **and** response together — so an unadjusted cap truncates mid-answer |

## 5.2 ★ Sampling — and the contradiction it resolves

D-01 **RA-60** requires `temperature` be set explicitly. D-01 **RM-1** measures agreement across `k`
runs on *identical input*. **These pull against each other and the tension has never been stated:**

```text
   temperature = 0   ⟹  RM-1 reports ~1.0 always. It measures NOTHING,
                        and k_stab is money spent on a constant.

   temperature > 0   ⟹  RM-1 measures variance THE SYSTEM CHOSE TO ADD.
                        (D-01 §7.4b: "self-inflicted variance".)
```

**Resolution — and it makes RA-60, RA-61 and RM-1 coherent for the first time:**

| ID | Rule |
|---|---|
| **GW-8** | ⚠ **AMENDED 2026-08-23 — see §5.2a. `temperature = 0` is the CHEAP-TIER rule only.** It remains right there and for the reason given: **extraction** has ground truth in the document (D-01 RA-6), and **judgement** gains nothing from sampling noise it did not ask for. ⚠ **The current repo sets no temperature at all**, so cheap-tier calls run at the API default — the maximum available variance, chosen by omission |
| **GW-8a** | ★★ **The DEEP tier has no `temperature` to set. `claude-opus-5` REJECTS the parameter with a 400** — sampling controls (`temperature`, `top_p`, `top_k`) were removed across the 4.6+ family. ★ **The deep-tier control is `output_config.effort`**, and it is a different instrument answering a different question (§5.2a) |
| **GW-9** | ★ **The decoding control that APPLIES TO THE TIER is recorded on every call, and the record says which one applied.** Cheap tier → `temperature`. Deep tier → `effort` and `thinking_mode`. ⚠ **A `temperature: null` on a deep-tier record must be readable as *"not settable"*, never as *"we forgot"*** — those are different facts and the field alone cannot tell them apart, which is why `decoding` is an object and not a number (CT-0.1) |
| **GW-9a** | ★★ **`effort` is set EXPLICITLY and never omitted.** GW-9's original argument transfers intact: omitting it takes the provider default (`high` today), and **a default that can change under us is a baseline nobody controls.** The reason RM-5 would not fire is unchanged — no INV-8 tier change occurred |
| **GW-9b** | ★★ **An `effort` change re-baselines exactly as a model change does — RM-5 extends to it.** ⚠ **Effort alters the output distribution as much as a tier swap would, and today nothing fires**: RM-5 keys on INV-8 tier changes, and `high → xhigh` is not one. **This is the amendment's most consequential clause**, because it is the failure that would otherwise be silent |
| **GW-9c** | ⚠ **Thinking is not disabled on the deep tier, and the reason is a silent failure, not a preference.** With `thinking: {type: "disabled"}` on Opus 5 the model can write a **tool call into visible text**: the turn succeeds, the call never runs, no error is raised. ★ **D-01's extraction path is structured tool use** (RA-5, MP-5), so that failure would present as an extraction that returned nothing — indistinguishable from a document that said nothing. Constitution INV-8's amendment already records this; **GW-9c is where it becomes the gateway's rule** |
| **GW-10** | ★★ **The sampling-stability probe is retired in favour of the perturbation probe** (D-01 **RA-61/62**). At `temperature = 0` there is no sampling variance left to measure, and **the variance worth measuring was never the decoder's** — it is whether the verdict survives a reordered option list or a paraphrased prompt |
| **GW-11** | A **non-zero temperature is permitted only for a declared probe**, recorded as such and never on the actionable path (INV-6). **A probe that cannot be distinguished from production in the record is not a probe** |

## 5.2a ⚠ THE AMENDMENT — why `temperature = 0` could not be the whole rule

> **Raised as D-01 `QP-1` on 2026-08-20 and never propagated to the spec that owns it.** It surfaced
> again in the **B0 readiness review (2026-08-23)**, where it is blocking: **the gateway is built at
> B0, and `AC-0.4` as written could not pass.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE TWO TIERS TAKE DIFFERENT CONTROLS, AND THEY ARE MUTUALLY    ║
║  EXCLUSIVE.                                                      ║
║                                                                  ║
║   CHEAP  claude-haiku-4-5   temperature ✅ settable              ║
║                             effort      ✗ errors                 ║
║                                                                  ║
║   DEEP   claude-opus-5      temperature ✗ 400, parameter removed ║
║                             effort      ✅ low|medium|high|       ║
║                                            xhigh|max             ║
║                                                                  ║
║  ★ So "production calls run at temperature = 0" is not a rule    ║
║    with an exception. It is a rule that applies to exactly ONE   ║
║    of the two tiers, and the other tier needs its own.           ║
╚══════════════════════════════════════════════════════════════════╝
```

### What survives, and what does not

| GW-8's original claim | Verdict |
|---|---|
| Extraction wants no sampling noise — it has ground truth | ✅ **survives**, both tiers |
| Judgement gains nothing from noise it did not ask for | ✅ **survives**, both tiers |
| *"The current repo sets no temperature, so it runs at maximum variance"* | ◐ **true of the cheap tier only.** On the deep tier there was never a knob to leave unset |
| ★ **GW-10 — the sampling probe is retired for the perturbation probe** | ✅★ **survives, and is now over-determined.** It was argued from *"at temperature 0 there is no sampling variance left to measure"*; on the deep tier the stronger fact is that **the setting does not exist**, so the sampling probe was never measuring a property anyone controlled. **D-01 RA-61's perturbation form is not merely the better probe — on the deep tier it is the only one available** |

### The one thing the amendment adds rather than corrects

★★ **`effort` is a live, un-baselined decoding control.** RM-5 re-baselines on an INV-8 *tier* change,
and `high → xhigh` is not a tier change — so today an effort edit would move every deep-tier output
with **nothing firing**. ⚠ **That is a strictly worse position than the one GW-9 was written to fix**,
because at least an unset temperature was visibly unset. **GW-9b closes it.**

> ⚠ **Verify at B0, do not assume: the exact Haiku model id.** The constitution's INV-8 names
> `claude-haiku-4-5-20251001`; the current model table lists `claude-haiku-4-5`. Both may resolve —
> a dated snapshot and an alias — but **`GW-5`'s "model_id is resolved from config" means the wrong
> string fails at the first cheap-tier call**, and one API call settles it before any code depends on it.

## 5.3 Prompt alignment — INV-9

| ID | Rule |
|---|---|
| **GW-12** | ★ **No call runs if the prompt spec and its components have drifted** (INV-9). The gateway is where this is enforced, because it is the only chokepoint every call passes through |
| **GW-13** | The failure is **surfaced to the caller**, never swallowed (INV-9, P5). A drift check that logs and proceeds is the check not existing |
| **GW-14** | `prompt_name` and `prompt_version` are **required arguments** — there is no unversioned call path |

## 5.4 ★ Retry — the declared exception to D-08 OR-14

**D-08 OR-14 says only `src/orchestration/` retries.** But LLM calls happen inside D-01, and a 429
is transport. **Something has been retrying, or nothing has, and neither was written down.**

```text
╔═══════════════════════════════════════════════════════════════════╗
║  THE GATEWAY RETRIES TRANSPORT, BENEATH THE DOMAIN LAYER.         ║
║  THIS IS AN EXCEPTION TO OR-14 AND IS DECLARED, NOT SMUGGLED.     ║
║                                                                   ║
║  RETRYABLE  429 · 5xx · timeout · connection reset                ║
║  NEVER      a refusal · a truncation · an unparseable response ·  ║
║             a schema violation · a drift failure (GW-12)          ║
║                                                                   ║
║  The rule is L4 EH-15's, applied one layer down: retry the        ║
║  request that got no real answer; never the answer you disliked.  ║
╚═══════════════════════════════════════════════════════════════════╝
```

| ID | Rule |
|---|---|
| **GW-15** | ★ **Transport retry lives in the gateway; semantic retry lives nowhere.** D-08 keeps orchestration-level retry for *jobs*; the gateway owns it for *calls*. Both obey EH-15 |
| **GW-16** | ★ **The attempt count is recorded and reaches the RunManifest** (D-01 CT-1.2, D-08 OR-15). **A retry invisible to the manifest makes a slow, flaky run indistinguishable from a fast, clean one** |
| **GW-17** | Retries are **bounded and backed off**; an unclassified error is **not retried** (EH-14's default) |

## 5.5 ★ Token and cost accounting — the thing everything was priced against

`L2-signal-combination.md` §7B prices the entire reliability programme in dollars — `$624/yr` at
`k_cov = 3`, `$2,079/yr` at 10, `18.97 % of NAV` for full coverage. **Nothing owned the measurement
those figures assume.**

| ID | Rule |
|---|---|
| **GW-18** | ★ **Every call records `tokens_in`, `tokens_out`, `model_id` and elapsed time** (D-01 CT-1.2 already declares the fields — this is what populates them) |
| **GW-19** | ★ **Cost is aggregated per run, per domain and per day, and reported.** Otherwise D-01's coverage decisions are priced against an estimate that is never checked against a bill |
| **GW-20** | ★ **A declared budget that is exceeded FAILS the run** (P5). ⚠ **A budget that can be exceeded silently is not a budget** — and at `k_cov × k_stab` the call count multiplies, so overspend arrives faster than intuition suggests (D-01 §7.4a) |

## 5.6 Failure — INV-034

| ID | Rule |
|---|---|
| **GW-21** | ★ **An LLM failure raises for that call and does not halt non-LLM work** (INV-034, D-08 OR-18). The pipeline **degrades scope and reports the absence** |
| **GW-22** | ★★ **The gateway never returns a partial, truncated or default response as a successful one.** ⚠ **Both real incidents in this repo are this defect**: a discipline card built from a **failed** LLM narrative, and from an **absent** one, each emailed as a genuine recommendation with no stop and no targets. **The gateway is the last place either could have been caught** |
| **GW-23** | A truncated response (hit `max_tokens`) is a **failure, not a short answer** — and GW-7 is what makes it rare |

---

# 6. CONFIGURATION

| ID | Rule |
|---|---|
| **CF-1** | ★ **Config is validated against a declared schema at load, and a missing required key raises** (P5). There is no silent default for a value the system needs |
| **CF-2** | ★ **Config is read once at the edge and passed inward** (L4 CN-4). A value re-read deep in a call stack can resolve differently within one run |
| **CF-3** | ★ **Every config value used by a run appears in the RunManifest** (L4 CN-5, D-08 OR-9). **A tuned number no manifest records makes the run irreproducible while looking deterministic** |
| **CF-4** | ★ **Config is immutable after load.** A runtime mutation makes CF-3's record a lie about the second half of the run |
| **CF-5** | D-00 **validates shape; it never interprets meaning.** That `δ = 2.19` is sane is D-03's judgement (§1.2) |

---

# 7. STRUCTURED LOGGING

| ID | Rule |
|---|---|
| **LG-1** | ★★ **A log is not the audit trail.** **D-11's journal and trade log are** (INV-006, append-only). Logs are diagnostic, may be rotated, and **nothing may depend on one for a fact about the book** |
| **LG-2** | Every record carries the **`run_id`** as a correlation key (D-08 OR-9), so one run is reconstructible across twelve domains |
| **LG-3** | Logs are **structured** (key–value), not formatted prose. A message that must be regex-parsed to be useful is a data structure someone declined to declare |
| **LG-4** | ★ **A secret never appears in a log** — see **SC-3**, which makes this structural rather than a matter of care |
| **LG-5** | **A degraded result logs at WARNING or above and also raises** (P5). ★ **A log line is not a substitute for a failure**: the two card incidents were both logged |

---

# 8. SECRETS

| ID | Rule |
|---|---|
| **SC-1** | ★ **Secrets are read from the environment and never hardcoded** — `ANTHROPIC_API_KEY`, `FMP_API_KEY`, `GMAIL_SMTP_USER`, `GMAIL_APP_PASSWORD`. `.env` stays gitignored |
| **SC-2** | ★ **A missing secret fails at STARTUP, not at first use.** Failing at first use means a nightly run dies forty minutes in, having already spent tokens and produced half a panel |
| **SC-3** | ★★ **A secret is never logged, never in an exception message, never in a RunManifest, and never in an artifact.** ★ **The value is held in a wrapper whose `__repr__` and `__str__` return a redaction** — so this is a property of the *type*, not a rule someone has to remember at every call site |
| **SC-4** | ⚠ **A leaked key is rotated, not merely purged.** Repo history has been rewritten once for this; **purging removes the copy, rotation removes the risk**, and only the second is a fix |

---

# 9. CONTRACTS

## CT-0.1 — LLMCall (JSON, one per gateway invocation)

```json
{
  "call_id": "…", "run_id": "…", "ticker": "MU",
  "prompt_name": "thesis.judgement", "prompt_version": "v4",
  "tier": "deep", "model_id": "claude-opus-5",
  "decoding": {                       // ★ GW-9 — the control that APPLIES to the tier
    "control": "effort",              //   "effort" (deep) | "temperature" (cheap)
    "effort": "high",                 //   set explicitly, never omitted (GW-9a)
    "temperature": null,              //   ⚠ null = NOT SETTABLE on this model,
                                      //     never "we forgot" (GW-8a)
    "thinking_mode": "adaptive"       //   never "disabled" on deep (GW-9c)
  },
  "max_tokens": 8192,
  "alignment_ok": true,
  "attempts": 1, "retry_reasons": [],
  "tokens_in": 30142, "tokens_out": 4870, "elapsed_ms": 21430,
  "outcome": "ok",
  "probe": null
}
```

★ `outcome ∈ {ok, transport_failed, refused, truncated, unparseable, drift_blocked}` — **there is no
`partial`** (GW-22). `probe` is non-null only for a declared probe (GW-11).

★ **`decoding` is an object, not a flat `temperature` field, and that is the load-bearing change.**
A flat `temperature: null` cannot distinguish *"this model has no such parameter"* from *"nobody set
it"* — and **the second is the defect GW-9 exists to prevent**, so a record that conflates them
defeats its own check.

## CT-0.2 — ConfigManifest

`(config_hash, source_files[], resolved{key: value}, loaded_at)` — the input to D-08's RunManifest
(CF-3). ★ **Secrets are excluded by construction, not filtered on the way out** (SC-3).

---

# 10. PUBLIC API SURFACE

| Method | Returns | Note |
|---|---|---|
| `call(prompt_name, version, tier, payload, schema)` | `Response` | raises on drift, truncation, schema failure |
| `load_config(paths)` | `Config` (frozen) | validates; raises on a missing required key |
| `manifest()` | `ConfigManifest` | for OR-9 |
| `logger(name, run_id)` | `Logger` | structured, correlated |
| `secret(name)` | `Secret` | redacting wrapper; raises at startup if absent |

★ **No method returns a business value.** If one ever does, §1.2 has been broken.

---

# 11. ERROR CATALOG

| Code | Severity | Behaviour |
|---|---|---|
| `SHR.LLM.DRIFT_BLOCKED` | ERROR | prompt alignment failed — no call runs (INV-9, GW-12) |
| `SHR.LLM.TRUNCATED` | ERROR | hit `max_tokens` — a failure, not a short answer (GW-23) |
| `SHR.LLM.UNPARSEABLE` | ERROR | response does not match the declared schema (GW-3) |
| `SHR.LLM.SEMANTIC_RETRY` | ERROR | ★ retry attempted on a non-transport failure (GW-15) |
| `SHR.LLM.BUDGET_EXCEEDED` | ERROR | declared budget passed — fails the run (GW-20) |
| `SHR.CFG.MISSING_KEY` | ERROR | required key absent; no silent default (CF-1) |
| `SHR.CFG.MUTATED` | ERROR | config changed after load (CF-4) |
| `SHR.SEC.ABSENT` | ERROR | secret missing — raised **at startup** (SC-2) |
| `SHR.SEC.LEAKED` | ERROR | ★ a secret reached a log, error, manifest or artifact (SC-3) |
| `SHR.BOUNDARY.DOMAIN_IMPORT` | ERROR | ★ `src/shared/` imported a domain (SI-1) |

---

# 12. ACCEPTANCE CRITERIA

```text
BOUNDARY
□ AC-0.1   src/shared/ imports no src/<domain>/ — grep-checkable (SI-1)
□ AC-0.2   the gateway is imported only by src/fundamental/ (GW-1, ST-5)
□ AC-0.3   no D-00 API returns a business value (§1.2)

GATEWAY
□ AC-0.4   ★ every call records the decoding control that APPLIES to its tier:
           temperature=0.0 on cheap, effort on deep (GW-8, GW-8a, GW-9)
□ AC-0.4a  ★ a deep-tier call that sends `temperature` is rejected BEFORE the
           request leaves the gateway — not by a provider 400 (GW-8a)
□ AC-0.4b  ★ effort is set explicitly; an omitted effort fails the call (GW-9a)
□ AC-0.4c  ★ an effort change re-baselines like a model change: RM-5 fires
           (GW-9b)
□ AC-0.4d  thinking_mode is never "disabled" on the deep tier (GW-9c)
□ AC-0.5   a non-default decoding setting is possible only on a declared probe,
           and never
           on the actionable path (GW-11)
□ AC-0.6   model_id is resolved from config and reaches the RunManifest (GW-5/6)
□ AC-0.7   a drifted prompt blocks the call and surfaces (INV-9, GW-12/13)
□ AC-0.8   ★ a transport error retries; a refusal, truncation, unparseable
           response or drift failure NEVER does (GW-15)
□ AC-0.9   attempts reach the RunManifest (GW-16)
□ AC-0.10  ★ no partial/truncated/default response is returned as success (GW-22)
□ AC-0.11  an LLM failure does not halt non-LLM work, and the absence is
           reported (INV-034, GW-21)
□ AC-0.12  tokens_in/out and model_id are recorded on every call (GW-18)
□ AC-0.13  ★ exceeding a declared budget fails the run (GW-20)

CONFIG
□ AC-0.14  a missing required key raises at load (CF-1)
□ AC-0.15  every used value appears in the RunManifest (CF-3)
□ AC-0.16  config cannot be mutated after load (CF-4)

LOGGING & SECRETS
□ AC-0.17  every record carries run_id (LG-2)
□ AC-0.18  ★ a degraded result both logs AND raises (LG-5, P5)
□ AC-0.19  ★ Secret.__repr__ and __str__ redact — verified by a test that tries
           to leak one through a log, an exception and a manifest (SC-3)
□ AC-0.20  a missing secret raises at startup, not at first use (SC-2)
```

---

# 13. OPEN QUESTIONS

| ID | Question | Note |
|---|---|---|
| **QI-1** | ⚠ **NARROWED 2026-08-23 to the cheap tier.** Does `temperature = 0` change measured output quality? | ★ **Unanswerable on the deep tier — the parameter does not exist there**, so the question survives only for Haiku-tier work. GW-8 is still argued from first principles rather than measured, and RM-1's agreement fraction remains the cheapest check *where the knob exists* |
| **QI-4** | ★ **What effort level do deep-tier calls run at, and was it chosen or defaulted?** | GW-9a forces it to be set; **it does not say to what.** ⚠ `high` is the provider default and the obvious first choice, but D-01's extraction calls and its judgement calls have different needs, and **nothing has measured either.** First candidate for a D-10 sweep once that exists |
| **QI-2** | What is the declared **budget**, and per what — run, day, month? | GW-20 needs a number. D-01 §7.4a's coverage costs give the shape ($624/yr at `k_cov=3`); the cap should sit above it with stated headroom |
| **QI-3** | Does the gateway **cache**? | The filing-aware cache exists (P4) and is D-07's. A gateway-level response cache would make RM-1 and GW-10's perturbation probe meaningless by construction — ★ **probably forbidden, and worth saying so explicitly** |
| ~~**QI-4**~~ | ~~Where does `max_tokens` per call site live?~~ | ✅ **CLOSED — per call site, in config, and the existing values are reused** (Victor, 2026-08-18): **16000** deep synthesis · **32000** full report composition · **8000** per section · **256** classifier. ★ **`settings.yaml` already does the right thing** — `max_tokens` is *already* per-call-site there, not global, so GW-7 is a pattern to preserve rather than introduce |
| ~~**QI-5**~~ | ~~Is there a second LLM provider, ever?~~ | ✅ **CLOSED — no. Anthropic only** (Victor, 2026-08-18). ★ **So `CA-5`'s port is NOT required for the gateway** — one implementation, and `L4` §1.3/CA-7 forbid speculative Protocols. ⚠ **INV-8's Haiku↔Opus tiering is a MODEL swap, not a provider swap** — it needs `GW-5`'s config value, not an abstraction |

---

# 14. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` §4.2 D-00, **AP-5**, INV-8, INV-9, INV-034 | the four duties; the gateway boundary |
| `L1-fundamental-analysis.md` **RA-60/61/62**, RM-1, RM-5, CT-1.2 | ★ the temperature contradiction §5.2 resolves; the fields §5.5 populates |
| `L1-orchestration.md` **OR-14/15**, OR-9, OR-18 | ★ the retry exception §5.4 declares; the RunManifest everything records into |
| `L2-signal-combination.md` **§7B** | ★ every dollar figure there depends on GW-18/19 |
| `L4-coding-standards.md` **EH-14/15**, **CN-1…CN-5**, ST-5, §10.1, **CA-0** | retry classification; config-vs-constant; the checked import edges |
| `L2-shared-money.md` | D-00's fourth duty |
| `sdd/specs/constitution.md` **P5**, P2, DC-3 | fail loud; why GW-22 exists |
