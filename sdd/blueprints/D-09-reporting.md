# Blueprint — D-09 Reporting *(B3 slice · the B4.8 relay surface)*

> **Code:** `src/reporting/` · **Spec:** `sdd/design/rel6_design/L1-reporting.md` · **Seat:** SEAT-5 · **LEVEL 1**
> **Status:** written 2026-08-23 at **B3** · **Tier rules:** [`README.md`](README.md) DR-1…DR-9
> ⚠ **PARTIAL DOMAIN.** B3 builds the **card, both renderings, the lint and email delivery**. The
> slate, the brief, the online surface and the staleness machinery are later — §9.

## Decision log — ★ APPEND ONLY (DR-8)

| Date | Decision | Why | Rejected, and why |
|---|---|---|---|
| 2026-08-25 *(B4.8)* | ★★ **RP-1 gains a fourth reliability class, `relayed_judgement`** | D-01's **RA-116** said *"RP-1's reliability classes gain a fourth"* and **RP-1 still listed three**, while D-01 **AC-1.79** requires it *in every medium*. The producing domain declared the class; the rendering domain was never told. ★ **RP-48** also fixes the DIRECTION: it renders as **more** provisional than `judgement`, never a footnote on it — a relay report is a judgement whose **bundle does not exist** and whose numbers are mostly unverifiable, and the rendering must not undo in presentation what RA-114 and RA-115 established in substance | *A `(relayed)` suffix on the `JUDGEMENT` label* — it reads as a variant of a class rather than a weaker one, and a reader scanning glyphs would not see it |
| 2026-08-25 *(B4.8)* | ★ **The `RELAY QUEUE` block carries four counts and no imperative** | **RP-49**, from D-01's RA-128: `queued · returned · overdue · stale`, **separate**. ⚠ *Not yet run* and *no longer trusted* are different states, and **collapsing them hides the moment one became the other.** ★ RA-127: the system reports and does not chase — *skipping is a decision SEAT-1 is entitled to make*, so `assert_does_not_chase` lints the block the way `FORECAST_VOICE` lints the card | *One `needs attention` count* — it is the collapse RA-128 names, wearing a friendlier word |
| 2026-08-23 | **The reliability class is a glyph AND a text label**; colour only reinforces | QP-1's surviving constraint. Colour inverts in dark mode and is invisible to a share of readers — and this is the one artifact where misreading a class means sizing off the least reliable number | Colour alone — the deferred cosmetics question, with the one part that is not cosmetic |
| 2026-08-23 | Absent stability renders **"not applicable — no model was run"** | ★ **BS-34.** The card must distinguish *no model* from *an unstable model*. Rendering `1/1` would be true and misleading; rendering nothing would be silent | A blank cell — silence is the D-15 shape |
| 2026-08-23 | `RPT.STABILITY.MISSING` fires **only on the actionable path** | ★ It is RP-13's own scoping, and it is what makes **BS-33** work: B3's card is informational, so no fabricated stability is needed to render it | Firing always — B3 could not ship a card at all, and BS-28's boundary would move for the wrong reason |
| 2026-08-23 | Self-containment is asserted on the **emitted bytes** | AC-9.24a says *"assert on the emitted bytes, not on intent"*. A template can be written correctly and still emit a `data:`-less URL through one careless f-string | Reviewing the template — intent is not evidence |
| 2026-08-23 | Content-equivalence is checked by **parsing both renderings back** | RP-32. Trusting two templates written from one object is exactly how they drift | Diffing the source object — proves nothing about what was rendered |
| 2026-08-23 | The archive is written **before** the send | RP-24: *if they can differ, the archive is not evidence of what was seen*. Writing after a successful send would leave a failed send unarchived, losing the artifact that failed | Archiving after — the failure case loses its evidence |

---

# 1. What this domain does, in one paragraph

```
D-09 is the ONLY place in this system where a machine's output becomes a
human decision. Everything upstream is measured, gated and reconciled. Here
it is READ — and a reader applies heuristics that none of those guarantees
survive.
```

It renders `CT-12.1` as a **Discipline Card**, in HTML (the artifact of record) and markdown (the
diffable copy), lints the narrative, and delivers by email. **It originates nothing and writes to
nothing.**

# 2. The objects and how they flow

```text
   CT-12.1 Recommendation
        │
        ▼
   build_card ──► RenderUnit[] (class · source · as_of) ──► DisciplineCard
        │                                                        │
        │  enforce() — forecast-voice lint, blocking     ┌────────┴────────┐
        ▼                                                ▼                 ▼
   ForecastVoiceError                              render_html      render_markdown
                                                         └────────┬────────┘
                                            assert_content_equivalent (RP-32)
                                                                  ▼
                                            archive ──► send ──► Delivery (CT-9.3)
```

| Object | Defined in | Created by | Consumed by | Lives how long |
|---|---|---|---|---|
| `RenderUnit` | `src/reporting/render/classes.py::RenderUnit` | `src/reporting/render/card.py::build_card` | both renderings | one card |
| `DisciplineCard` | `src/reporting/render/card.py::DisciplineCard` | `build_card` | delivery, archive | one run |
| `Delivery` | `src/reporting/deliver/email.py::Delivery` | `src/reporting/deliver/email.py::deliver` | the record | forever |

★ **The object that surprised me: `delivery_id`.** It is derived from the **content**, not
allocated — so a re-send of an identical card produces the same id. That makes a duplicate
*visible*, and RP-22's concern is precisely that *a silent duplicate is how a stale card gets acted
on twice*.

# 3. The sequence — what actually executes

| # | Step | Function | Why here | Fails how |
|---|---|---|---|---|
| 0 | escalation check | `src/reporting/render/card.py::build_card` | ★ RP-7/DC-5 **first**: the renderer is the last place a verdict could be quietly improved | `VerdictEscalatedError` |
| 1 | build units | same | each carries class, source and its **own** `as_of` (RP-1, RP-2) | `Untagged`/`NoProducer`/`FreshnessUnstated` |
| 2 | stability & confidence | `_stability_unit`, `_confidence_unit` | ★ **before the lint**, so an actionable card with no stability fails on the *right* error | `StabilityMissing`, `BareConfidence` |
| 3 | lint | `src/reporting/render/lint.py::enforce` | ⚠ **blocks the render** — after the text exists, before it leaves | `ForecastVoiceError` |
| 4 | render both | `src/reporting/deliver/html.py`, `src/reporting/deliver/markdown.py` | — | `ExternalRef`, `ScriptPresent` |
| 5 | equivalence | `src/reporting/deliver/archive.py::assert_content_equivalent` | ★ **after both**, because it is a claim about the pair | `RenderingsDivergedError` |
| 6 | archive, then send | `src/reporting/deliver/email.py::deliver` | RP-24 — the archive is evidence, so it precedes the thing it is evidence of | `ArchiveMismatch`, `DeliveryFailed` |

⚠ **Step 3 before step 4 is the ordering a rewrite would get wrong.** Linting the rendered HTML
would mean escaping and markup interfere with word-boundary matching, and a violation could hide
behind a tag.

# 4. ★ The mathematics

★ **None — and for D-09 that is a rule, not an accident.** **RP-43**: *D-09 renders `CT-12.1` and
never re-derives any of it. A card field computed inside the renderer is a second, unowned
computation.* The two things that look like computation are not:

| Looks like arithmetic | What it actually is |
|---|---|
| `_CONSERVATISM` comparison in `build_card` | a **verification** that the verdict was not escalated in transit, not a composition. D-12 owns the algebra |
| `digest()` / `delivery_id()` | content hashes for idempotence and archive evidence — no domain quantity involved |
| `stability` text assembly | formatting `k` and `verdict_distribution` **verbatim** (RA-20). ⚠ Note it does *not* compute the ratio: RA-51a is that 0.6 cannot produce "3 / 2" |

# 5. The logic decisions

| Decision | Where | Why this way | What it would take to change it |
|---|---|---|---|
| `FIELD_ORDER` puts falsifier first | `src/reporting/render/card.py` | ★ RP-15: *what would prove this wrong, before what we think.* **Ordering is an argument** | one tuple |
| Forecast-voice matches on **word boundaries** | `src/reporting/render/lint.py` | "willing" and "clearance" must not fire. **A lint with false positives is a lint that gets disabled** (IM-2) | the regex |
| Length is a **warning**, forecast voice **blocks** | same | RP-18 blocks; RP-19 is `RPT.LINT.LENGTH`, a WARNING. Length is a soft confidence signal; certainty language is a claim | `LintReport.blocking` |
| The email subject carries `[NOT ACTIONABLE]` | `src/reporting/deliver/email.py::build_message` | The notification is what a phone shows. BS-33's claim must survive the most constrained medium | — |
| `_fmt` renders an empty list as `—` | both renderings | ⚠ An em-dash for "none present"; the *status* line carries whether anyone looked (RP-47). **Neither alone is sufficient and that is why both are on the card** | — |

# 6. Configuration — where every knob lives

| Knob | File · key | Default | Changing it affects |
|---|---|---|---|
| `LENGTH_CAPS` | `src/reporting/render/lint.py` | 300–600 chars | ⚠ **an admitted guess** (CN-10) — chosen to fit one screen, never measured |
| `FORECAST_VOICE` | same | RA-26's list | what blocks a render |
| `GLYPH` / `LABEL` | `src/reporting/render/classes.py` | ◆ ▣ ◌ ◌⇄ | ★ deferred cosmetics (QP-1) — **except that colour alone is forbidden**, which is not cosmetic |
| `CHASING_VOICE` | `src/reporting/render/relay_queue.py` | 8 phrases | RP-49/RA-127 — what blocks a relay-queue render. ⚠ **ADMITTED GUESSES** (CN-10), same shape as `FORECAST_VOICE` |
| `ASSURANCE_ORDER` | `src/reporting/render/classes.py` | fact→relayed | ★ **RP-48 — not cosmetic.** A renderer asking *"is this weaker than that"* reads this rather than comparing strings |
| `SMTP_HOST` / `SMTP_PORT` | `src/reporting/deliver/email.py` | Gmail, 587 | ⚠ a **world fact** with its check date (CN-2) |
| sender / recipient | ⚠ **caller arguments** | — | should be config once D-08 supplies a manifest (CN-5) |

# 7. Inputs and outputs

| Direction | Contract | Producer / consumer | What happens if malformed |
|---|---|---|---|
| in | **CT-12.1** Recommendation | D-12 | the class/source/as_of validators raise |
| out | **CT-9.1** DisciplineCard | delivery | — |
| out | HTML + markdown bytes | the human | `ExternalRef` / `ScriptPresent` / `RenderingsDiverged` |
| out | **CT-9.3** Delivery record | the record | `DeliveryFailedError` |

# 8. Failure behaviour

| Failure | Detected where | Behaviour | Visible to whom |
|---|---|---|---|
| a value with no class / source / as_of | `RenderUnit.__post_init__` | raises | the run |
| an escalated verdict | `build_card` | `VerdictEscalatedError` | the run |
| actionable with no stability | `_stability_unit` | `StabilityMissingError` — ★ **D-15 with better plumbing** | the run |
| a bare confidence number | `_confidence_unit` | `BareConfidenceError` | the run |
| forecast voice | `enforce` | **blocks the render** | the run |
| a network reference or a script in the HTML | `assert_self_contained` | raises | the run |
| renderings disagreeing | `assert_content_equivalent` | raises | the run |
| a send failure | `send` | `DeliveryFailedError` — ★ *an email that did not arrive is indistinguishable from a run that never happened* | the human |

# 9. What this domain deliberately does NOT do

| Not here | Owner / when |
|---|---|
| originate a verdict, a stop, a target, a fair value, a size | ✗ **never** (DC-1). Every field names its producer |
| make a verdict **more aggressive** | ✗ never (DC-5, RP-7) — checked at render |
| write to the book, the journal, or any producing domain | ✗ **never** (RP-30, ST-9) — *a renderer that can mutate the book can rewrite history to match what it printed* |
| call the LLM gateway | ✗ never (ST-5). ★ D-09 **has an agent and no gateway**: it renders text D-01 authored |
| the slate (CT-9.2), the brief, the online surface | later — B3 has one candidate, so a slate would be a list of one |
| per-component staleness thresholds | ⚠ **QP-3** is open: L0 §8 has price/news/filings thresholds and **nothing for a thesis** |
| the D-19 caveat in practice | with the first rendered fair value (B4) — the register exists (`KNOWN_DEFECTS`), the field does not |

# 10. ⚠ Known-wrong, approximations, and open defects

| Item | Severity | Effect on outputs | Tracked as |
|---|---|---|---|
| **10.1 — `stale` is never set** | ⚠ medium | `RenderUnit.stale` exists and nothing computes it, because **QP-3** has no threshold for a thesis. RP-2's *"marked stale on the face of the card"* is therefore unenforced | **QP-3** |
| **10.2 — content-equivalence parses the field TABLE only** | ⚠ medium | The falsifier, data gaps and the risk status are compared by neither parser. **A divergence in the prose sections would pass RP-32** | RP-32 |
| **10.3 — the email body is not class-tagged** | low | RP-35 makes it a notification, and **QP-6** asks whether it needs classes at all. It currently carries one verdict with its marker | **QP-6** |
| **10.4 — `deliver()` is not idempotent against the transport** | ⚠ medium | The `delivery_id` is stable, so a duplicate is *identifiable* — but nothing refuses to send twice. RP-22 says *"a re-send is identifiable as one"*, which is satisfied; a reader might expect suppression, which is not | RP-22 |
| **10.5 — no `Slate`, so INV-6's count is enforced upstream only** | low | D-12's `enforce_inv6` holds it. With one candidate the slate would be a list of one | RP-12 |

| **the relay block is not wired into the card** | ⚠ **expected** | `render_relay_queue` produces the block and `assert_does_not_chase` lints it, but **nothing in `src/reporting/render/card.py` calls either** — the daily card has no relay section yet. ★ The block is a pure function of D-01's `QueueReport`, so wiring it is a card-composition change, not a rendering one | RP-49 |
| **`relayed_judgement` has no rendering path yet** | ⚠ **expected** | The class, glyph, label and ordering exist; **no `RenderUnit` is ever constructed with it**, because D-01's §10.21 gap means no relay report reaches a card. ★ AC-1.79's *"in every medium"* is therefore asserted on the class table, not on emitted bytes | RP-1, RP-48 |

# 11. How to verify this domain yourself

| # | Check | Command or file |
|---|---|---|
| 1 | The ACs and their tests | `tests_src/test_reporting_b3.py` — 24 cases, each docstring naming its `AC-9.n`; **AC-9.30/9.31** are covered from the consuming side in `tests_src/test_fundamental_b48.py` (`test_ac_1_79_d09_carries_a_fourth_reliability_class`, `test_ac_1_82_the_daily_report_carries_overdue_and_stale_as_separate_counts`) |
| 2 | ★ **Break it and confirm red** | In `src/reporting/render/card.py::_stability_unit`, return a fabricated `stable 1/1` instead of *"not applicable"*. `test_bs_34_no_graded_field_is_fabricated` must fail — **that string is the difference between an honest card and D-15** |
| 3 | The worked example (§4) reproduces | `tests_src/test_b3_skeleton.py::test_both_renderings_agree_and_the_html_fetches_nothing` |
| 4 | Pointers resolve | `python tools/sdd_audit.py` |
| 5 | ★ **Checked against external truth?** | ⚠ **Partly.** Self-containment and script-freedom are asserted on the emitted bytes, which *is* external to the template. Whether the card **reads** correctly to a human is not testable here and is the one thing this domain exists for |

# 12. Cross-references

| Document | Relevance |
|---|---|
| `sdd/design/rel6_design/L1-reporting.md` | RP-1…**RP-49**, CT-9.1/9.3, **§8Z** the D-12 seam; **RP-48/RP-49** the relay surface |
| `sdd/design/rel6_design/L1-decision.md` | **CT-12.1** — the artifact D-09 renders |
| `sdd/design/rel6_design/L1-fundamental-analysis.md` | RA-20…RA-27 — the anti-overconfidence obligations §8 executes |
| `sdd/design/rel6_design/L3-build-sequence.md` | **BS-28**, **BS-33**, **BS-34** |
| `sdd/design/rel6_design/L5-inherited-defects.md` **D-15**, **D-19** | the incident §7 prevents; the defect RP-5 discloses |
