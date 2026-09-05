# Release 6 — Feature Design & Brainstorm

> **SDD role: `design/` tier — NON-AUTHORITATIVE.** This is the *brainstorm /
> rationale / decision log*, not a contract. **Do not code from this file.** The
> source of truth is `sdd/specs/vision.md` (what we are building) +
> `sdd/specs/constitution.md` (global rules) + the per-feature
> `sdd/specs/F<n>_<slug>/spec.md`. Ideas here *graduate* into a spec once their
> acceptance criteria can be written; if this doc and a spec ever disagree,
> **the spec wins.** (Moved here from `notebooks/rel6_features.md` on 2026-07-11
> during the SDD restructure — a pre-rename path.)
>
> **⚠️ Paths in the session logs below predate the `notebooks/` → `sdd/` rename
> (2026-08-08).** The navigational header and spec pointers were updated; the
> historical session text was not, because it records what was true when written.
> Read `notebooks/…` in an old entry as today's `sdd/…`.
>
> **⚠️ Session numbering is release-local.** "Session 11" here means **rel6 S11**.
> When citing a session from a spec or the constitution, write `rel6 S11` — a bare
> number becomes ambiguous once rel7 restarts its own numbering at 1.
>
> **Status:** OPEN — living design doc; each brainstorm session appends/updates it.
> The **SDD scaffold landed** (Feature 3) and **F1 / F2 / F4 are built** (F1 partial —
> 11/14 ACs; see `sdd/specs/README.md` for the current scoreboard, and
> `sdd/design/releases/rel6_closeout.md` for the close-out slot).
> **Release 5 is CLOSED and merged** (PR #7 / `db1b996`, 2026-07-08; close-out
> cleanup `ccd6d14`). The old "R5 freeze — do not touch R5 code" rule is
> **lifted**; R6 builds on the merged R5 code.
> **Code references below were refreshed against merged R5 in Session 6 (2026-07-11)** —
> earlier sessions predate the SlotSelector→SleeveSelector removal and the config
> cleanup; where an older line still names old code, Session 6 is the correction.

## Guiding vision

`main_inference` + the online (phone-accessible) API should assist **DISCIPLINARY TRADING**.
The product is *not* "tell me what to buy" — the quant pipeline already ranks ideas.
Release-6's job is to be the **disciplinarian**: the part of a professional fund's process
that sits between the idea and the click, and that manages/exits the position by rule.

### Investor profile & principles (Victor)
- **Risk posture:** deliberately takes extra risk for high return — *but not* penny stocks or derivatives.
- **2026 concentration is intentional:** accepts holding almost entirely AI / semiconductor names this year.
  (So "diversify the theme" is **not** a goal; concentration is a chosen bet, not an accident.)
- **Pyramiding-up:** wants to *avoid* it — intended fix is to **sell less / let winners run** to take more profit,
  rather than scaling in at ever-higher average cost.
- **Portfolio risk-estimation:** wants this feature; undecided on Google-Sheet template vs AI-agent (see §E).
- **TFSA day-trading:** actively reducing in real life (CRA "carrying on a business" risk — see §B).

---

## Intended Features (living list)

> **Canonical, continuously-clarified list of what Release-6 will build.** Each feature is refined as the
> brainstorm continues; the Session-1 "Candidate feature backlog" (further below) feeds ideas into this list.
> **Audience: the AI-agent that will implement the code** — details are written to be implementation-ready
> (concrete data flow, file paths, reuse targets). Status: 🟢 clarified · 🟡 partially specified · 🔵 idea only.
>
> Feature list: **Feature 1 — Disciplinary Trading Report (single stock)** · **Feature 2 — Portfolio, Risk, Journal & Delivery** · **Feature 3 — Spec-Driven Development (SDD) adoption** (major cross-cutting feature; pilot delivered) · **Feature 4 — Portfolio & Market Data Plane (feed & monitor)**. [all defined below]
>
> **Organizing lens (Session 11): the AI-pipeline as a professional fund back-office.** Victor = **Portfolio Manager +
> Trader** (decides, sizes, executes — keeps discretion & P&L accountability). The AI-pipeline = **Analyst desk +
> Risk desk + Back-office** (advises, computes, records — never decides; constitution P2/P3). Each *desk* maps to a
> feature: **Analyst → F1**, **Risk + Journal + Delivery → F2**, **Back-office data plane → F4**. See Session 11 for the
> roles model + the full task catalog with input/output schemas.

---

### Feature 1 — Disciplinary Trading Report (single stock) 🟡

**One-line goal.** For a *single stock*, produce a **DISCIPLINARY TRADING report** = (a) an eye-catching, concise,
**actionable summary thesis** the user can act on directly, immediately followed by (b) the **detailed analysis**
(today's Layer-2 synthesis report). Summary-on-top, depth-below. Scope is always **one individual stock per report.**

**Trigger scenarios (all three produce the same report shape for one ticker):**
- **T1 — On-demand (phone / online-API).** User inputs a specific ticker → report generated for *that* ticker.
  Reuse the `/infer` + `/synthesis/{ticker}` surface; the report must auto-build instead of showing "pending".
- **T2 — Manual `main_inference`.** User runs `main_inference` by hand → report generated for the **pipeline's #1 pick**
  (top of SleeveSelector→SignalEngine FINAL ranking). *(R5 removed `SlotSelector`; the live path now rolls today's
  weekday sleeve via `SleeveSelector` — Session 6.)*
- **T3 — Scheduled `main_inference`.** Auto-run **daily at 09:35 ET using the daily open price** → report for the #1 pick.
  (09:35 = 5 min after the 09:30 open, so the open print is available.)

**Output contract (what every trigger must emit):**
1. **Summary thesis card** (the "eye-catching" part): verdict (BUY/…), conviction, 1–2 sentence **thesis statement**,
   **falsification condition**, horizon, stop, target. Phone-glanceable.
2. **Detailed analysis** below it: the existing synthesis report (archetype, cycle, valuation reconciliation, narrative).
3. Exactly **one** ticker per report; persisted to `reports/llm_reports/{TICKER}_report.md` (+ `_synthesis.json`).

---

#### Implementation details (D1–D10 — former F1–F10, now sub-features of Feature 1)

> Reuse-first. The LLM plumbing already exists — see "Reusable assets discovered" (Session 2). Build the gaps,
> rewire the rest. Items once marked **[portfolio-scoped]** have now **graduated out of Feature 1**: D8 (data
> reconciliation) → **Feature 4** (data plane); D9/D10 (risk math + discipline guards, computed *on* F4 data) →
> **Feature 2**. They are kept in this table only as historical cross-references (Session 11).

| # | Detail | Status | Implementation notes (for the coding agent) |
|---|---|---|---|
| **D1** | ~~One pick per run~~ → **Dual pick + Watchlist Slate (revised S9)** | 🟡 **redesigned (S9)** | **Top-1 stays for backtest/experiment only** (`SleeveSelector` — untouched, it's the validated policy). **In practice (T2/T3): produce a Watchlist Slate** (ranking of a curated familiar list, reusing the full `rank_score` already computed in `run_inference` — cheap, no LLM) **AND build TWO deep reports: the global top-1** (to expand knowledge on *unfamiliar* names) **and the top-watchlist name** (underwritable), deduped to one if they coincide. See §3a + CT-1.5/CT-1.6 in F1 spec. *(Selection primitive from S7 still true; scope widened from single-pick to dual-pick + slate.)* |
| **D2** | **Auto-trigger the detailed (Layer-2) report.** | 🟢 | Call `run_synthesis_report_one(ticker, force_refresh=...)` automatically: for T1 from the `/infer` path; for T2/T3 inside `run_inference` after the pick is known. No manual `/synthesis/refresh`. Use `async_jobs` for the phone path so T1 stays responsive. |
| **D3** | **Summary thesis card schema** — the eye-catching actionable part. | 🟡 | Define a struct: `verdict, conviction, thesis (1–2 sentences), falsification_condition, horizon, stop, target`. Generate from the synthesis bundle (`narrative.verdict/conviction`, reconciliation FV/margin) + thesis inputs. Render on top of the report; persist in `_synthesis.json` (envelope = F1 CT-1.0). **Verdict enum = BUY/HOLD/SELL only** (S10). *Positions/holdings now come from **F4** `portfolio_state.json` (CT-4.2), not the flat `current_positions.json`.* See F1 CT-1.1. |
| **D4** | **Thesis-vs-falsification invalidation monitor** — drives `reason`. | 🟡 | Re-point `NewsAnalyst.analyze` to ask "does this news break *THIS* stored thesis?" (pass the D3 card as context) instead of generic materiality. Output feeds `reason` + the SignalEngine gate. |
| **D5** | **Model cost split.** | 🟢 | **Haiku 4.5** (`claude-haiku-4-5-20251001`) for cheap/high-frequency calls (materiality, thesis extraction, invalidation); **Opus 4.8** (`claude-opus-4-8`) for complex work (deep synthesis report, thesis critique). Set via `infer.llm_model` / `synthesis.llm_model` / `NewsAnalyst._model`. |
| **D6** | **Remove obsolete Gemini config/deps.** | 🟢 | Delete the `llm:` block in `config/settings.yaml` (now **lines 58–60** post-R5 cleanup; `model: gemini-2.0-flash` + `enabled:`) + `config/env.yaml:44` (`google-generativeai`). Re-confirmed Session 6 (2026-07-11): **still present, still dead** — no Python imports genai/gemini and nothing reads `config['llm']` (only `config['buffett']['llm']`, `infer.llm_model`, `synthesis.llm_model`, all `claude-sonnet-4-6`). |
| **D7** | **Surface prompt-alignment 409 to the viewer.** | 🟡 | When auto-trigger hits `PromptAlignmentError` (HTTP 409), render the diff/reason on the report page instead of a silent "pending". Critical now that reports auto-build. See `synthesis/prompt_alignment.py`. |
| **D8** | **Portfolio reconciliation** from broker `TransactionHistory_*.xlsx`. | ➡️ **moved to Feature 4** | **Now owned by Feature 4** (data plane): parse the real BMO InvestorLine export (CT-4.1) → canonical `portfolio_state.json` (CT-4.2: holdings, avg cost, realized/unrealized P&L, cash, per-currency). Deterministic, no LLM. *(No longer F1/F2 — it is the data backbone both stand on.)* |
| **D9** | **Risk-estimation sheet/script** — deterministic, **non-AI**. | ➡️ **moved to Feature 2** | **Now Feature 2's Risk desk**, computing *on* F4's `portfolio_state.json`: exposure %, vol, beta, correlation, simple VaR (CT-2.1). Plain Python, not LLM (P2). |
| **D10** | **Discipline guards** — pre-trade gate, pyramiding monitor, stop & time-stop alerts. | ➡️ **moved to Feature 2** | **Now Feature 2**: no buy without thesis+stop+target+size (the gate reads the F4 trade log CT-4.3 + `portfolio_state.json`); pyramiding flag from avg cost; stop/time-stop alerts. |

**Open implementation questions for Feature 1:**
- T3 "daily open price": **R5 changed live pricing** — `--live-price` is now a **deprecated no-op** (live FMP pricing
  is *always on*: in-hours a live spot bar is appended via `_append_live_prices`; off-hours the previous trading day's
  close is used, no synthetic bar). It still uses the FMP quote `price` (spot), **not** the session **open**. So T3 at
  09:35 ET still needs an explicit `open`-field fetch tweak in `_append_live_prices` — confirm before building. (Spec F1 Q1.)
- Scheduling for T3: cron / scheduler at 09:35 ET (DST-aware). Decide host (same box as the API?).
- T1 latency: the deep synthesis (Opus + web search) is slow; phone path should return the summary thesis fast and
  stream/poll the detailed analysis (reuse `async_jobs` + the existing pending→poll pattern).

---

### Feature 2 — Portfolio, Risk, Journal & Delivery 🟡

**One-line goal.** The AI-pipeline's **Risk desk + Back-office compute + Delivery** (roles model, Session 11): put each
report *in the context of the actual book* (**portfolio context, risk metrics, pre-trade discipline gate, decision
journal**), and **deliver the daily bundle to Victor through a self-contained, persistent, view-later channel** that does
**not** depend on the online-API being reachable at read time. **Spec:** `sdd/specs/F2_portfolio_and_delivery/spec.md`.

**What F2 covers (broadened past the original "delivery channel" placeholder):**
- **Layer D — Position & Portfolio Context** (CT-2.1): current holding, **pyramiding flag**, theme exposure (track, not
  block), deterministic **risk metrics** (vol/beta/corr/VaR — was D9), **pre-trade discipline gate** PASS/FLAG/FAIL (was D10).
- **Layer E — Decision Journal & Grading** (CT-2.2): grade the **process, not the outcome** (anti-"resulting").
- **Delivery** (CT-2.3): the daily email bundle (slate + both deep reports).

**Data dependency (no overlap with F4).** F2 **consumes** F4's canonical `portfolio_state.json` (CT-4.2) and trade log
(CT-4.3) — it **does not parse the broker export** (that is Feature 4's data plane). F2 = *compute on the truth F4 provides*.
The risk math is deterministic — **no LLM** (P2); the thesis/analyst work stays in F1.

**Key constraint (design driver).** Delivery must be **self-contained & persistent** (P6): the content lives *in the
delivered message / inbox*, not behind a link to a server that may be offline later.

**Scope boundary.** The 09:35 ET scheduling + open-price fetch is owned by **Feature-1 (T3)**; the single-stock report
Layers A–C are **F1**; the data ingestion/reconciliation is **F4**. F2 owns the portfolio/risk/journal *compute* + delivery.

**Delivery options (brainstorm — Session 4, historical):**

| Method | Push | View later | Rich / attach | Effort | Notes |
|---|---|---|---|---|---|
| **Telegram bot** | ✅ native | ✅ chat history | ✅ markdown + file | low | best convenience/effort; free; interactive (buttons) later |
| **Email** (Gmail SMTP / SES) | weak | ✅ archived & searchable | ✅ HTML + PDF/MD attach | low–med | universal system-of-record; format/deliverability quirks |
| **Discord webhook** | ✅ | ✅ channel history | ✅ + file | very low | trivial POST to a webhook URL |
| **Pushover / ntfy.sh** | ✅ | ✅ history | limited | low | purpose-built alerts; thin formatting |
| **Cloud-synced file** (Drive/Dropbox/Syncthing) | ❌ | ✅ | ✅ | low | no push — must remember to look |

**Decision (Session 9 → 10, supersedes the Session-4 recommendation):** **channel = Email via Gmail SMTP**, **HTML body**
(watchlist slate table + Discipline Cards inline), **`.md` report attachment(s)** (1–2 after dedupe). Fully automated,
**no interactive input** at fire time. Telegram remains an optional later add. **Avoid** a link-back-to-the-API as the
*only* delivery (P6). See F2 spec CT-2.3.

**Status:** 🟡 draft — delivery slice ready (channel resolved, AC-2.7/2.8); portfolio Layers D & E are reserved
contracts (🔵), unblocked once F4's `portfolio_state.json` lands. Open: risk-metric details, theme ceiling (Q-D4),
pyramiding threshold value (Q-D5).

---

### Feature 3 — Spec-Driven Development (SDD) adoption 🟡 (pilot delivered)

**One-line goal.** Make **lean SDD** the working method for Release-6 and beyond: every *production* feature is
specified (WHAT/WHY + acceptance criteria + inline contracts) **before** it is coded, and a **test/contract layer** is
forced into existence so feature-engineering and the online-API can no longer break silently. This is a **major,
cross-cutting Release-6 feature** — it governs *how* Features 1 & 2 get built, not just an aside. Decision + rationale:
Session 5 (adopt lean SDD); global rules: `sdd/specs/constitution.md`.

**Why it's a feature, not just process.** The project's three standing pains — weak tests, a silently-breaking
online-API, and feature-engineering that can be falsified without anyone noticing — are exactly what a spec +
contract/test layer fixes. SDD is the frame that forces that layer to exist and keeps the implementing AI-agent aligned.

**What "lean" means here (locked, Session 5):**
- **One `spec.md` per production feature** = WHAT/WHY + **acceptance criteria (Given/When/Then)** + **contracts inline**
  (data/API/schema). No separate `plan.md` / `tasks.md` — the agent derives tasks from the spec.
- A project **`constitution.md`** holds global non-negotiables (principles P1–P7, invariants INV-1…9, data contracts
  DC-1…3, test tiers, change process, traceability convention).
- **Research/experiment lane is exempt** (`--mode experiment`, sweeps, feature discovery). SDD gates *production*, not discovery.
- **Do not retro-spec rel1–5.** Freeze legacy behavior with **characterization tests**; spec only *forward*.

**Delivered so far (pilot, committed 2026-07-08 in `2ac2b9a`):**
- `sdd/specs/constitution.md` — the project constitution (P1–P7, INV-1…9, DC-1…3, test tiers §4,
  change process §5, traceability §6).
- `sdd/specs/F1_disciplinary_report/spec.md` — the **pilot feature spec** (F1 = Feature 1 above), with
  Spec-ID, triggers T1–T3, inline contracts CT-1.1…1.3, acceptance criteria AC-1.1…1.8, open questions Q1–Q4, and a
  spec→test→code traceability table (tests still TBD).

**SDD rollout plan (from Session 5's incremental P0–P3):**

| Phase | Deliverable | Status |
|---|---|---|
| **P0** | `constitution.md` + spec template (`specs/_templates/spec.md`) + spec index (`specs/README.md`) | 🟢 **DONE (2026-07-11)** — constitution, `_templates/spec.md`, and `specs/README.md` all exist |
| **P1** | Pilot spec = Feature 1 (`F1_disciplinary_report/spec.md`) | 🟢 DONE (draft) |
| **P2** | **Characterization tests** freezing current feature-eng (`OhlcvFeatureEngineer` golden output) + the online-API contract — *before* any R6 coding (this alone kills most of the falsification fear) | 🔵 not started — **highest-leverage next step** |
| **P3** | CI gate: the five test tiers (data-contract · invariant/property · golden · API-contract · metric-gate) must pass to merge | 🔵 not started |

**`notebooks/` restructure — LARGELY DONE (2026-07-11):**
- ✅ `specs/` = source of truth: `constitution.md`, `_templates/spec.md`, `README.md` (spec index + SDD loop), per-feature `F1_disciplinary_report/`.
- ✅ `design/` = this brainstorm log — moved from `notebooks/rel6_features.md` to `notebooks/design/rel6_brainstorm.md` (a one-line pointer stub remains at the old path). *(Both are pre-rename paths; the tree became `sdd/` on 2026-08-08.)*
- ⬜ `archive/` (move rel1–5 docs as-is) — **still pending**; the only remaining structural step.

**Open questions for Feature 3:**
- Sequence: do **P2 characterization tests** before writing Feature-1 *product* code (Session 5 says yes — it's the
  guardrail that makes touching feature-eng safe). Confirm this ordering.
- When to do the last structural step — move rel1–5 into `sdd/archive/` — pre-R6-coding or later?

---

### Feature 4 — Portfolio & Market Data Plane (feed & monitor) 🟡

**One-line goal.** The **deterministic data backbone** (the AI's **back-office data desk** — roles model, Session 11):
turn *real* trading data into one trustworthy **canonical portfolio state**, and expose a **book-state monitor** — so
Victor can *feed data in* and *watch what the AI sees*. No LLM anywhere (constitution P2). **Spec:**
`sdd/specs/F4_data_plane/spec.md`.

**Why it's its own feature (and the foundation under F1/F2).** Everything about the *actual book* — risk metrics,
pyramiding flags, the pre-trade gate, unrealized P&L, the decision journal — needs one answer to *"what do I hold, at
what cost, in what currency, worth what today?"* Today there is none: `data/current_positions.json` is a flat
`{TICKER: weight}` with no cost/P&L/currency/cash. F4 is that missing backbone (Session-1 backlog #1, "the clean first
deliverable"). It **absorbs former D8** (broker reconciliation) out of F1/F2.

**Inputs (how Victor feeds data):**
- **CT-4.1 — Broker export** (`data/TransactionHistory_*.xlsx`): the *real* BMO InvestorLine file — columns
  `Transaction Date, Settlement Date, Activity Description, Description, Symbol, Quantity, Price, Price Currency,
  Total Amount, Total Currency`; activities `Buy/Sell/Dividend/Non resident tax/Contribution/Foreign Exchange`; mixes
  USD+CAD; has pre-header metadata rows the parser skips. *Feeding data = dropping the `.xlsx` in `data/`.*
- **CT-4.3 — Trade log** (`data/portfolio/trade_log.jsonl`, append-only): Victor records `PLANNED`/`EXECUTED` trades —
  the record of his **PM/Trader actions**; `PLANNED` feeds the F2 pre-trade gate, `EXECUTED` feeds the F2 journal.
- **CT-4.4 — Live market snapshot** (reuse the existing FMP `_append_live_prices` path) for mark-to-market.

**Outputs (the truth + the monitor):**
- **CT-4.2 — `portfolio_state.json`** — the reconciled **single source of truth**: holdings, avg cost, realized +
  unrealized P&L, cash, **per-currency** (INV-5). **F1 and F2 read this; they do not re-derive it.**
- **CT-4.5 — `book_state.json`** — the *"state of my book"* read model Victor monitors (NAV, weights, `thesis_status`,
  open flags, last-run picks + refresh modes); also attached to the F2 daily email.

**Behaviour & reuse.** Deterministic parse + reconcile (avg cost, realized P&L, FX legs — INV-5), reusing the FMP price
path (P4); positions round-trip (INV-7); unknown activity **fails loud** (P5). **No LLM** (P2).

**Relationship to F1 / F2 (no overlap — clean layering).**
- **F4 owns the *data*** (ingest → `portfolio_state.json` → `book_state.json`).
- **F1 (Analyst)** reads positions/holdings from F4 for the thesis/monitor; it no longer references the flat
  `current_positions.json` (D3 adjusted).
- **F2 (Risk/Journal/Delivery)** *consumes* F4's `portfolio_state.json` and computes risk/gate/flags/journal *on* it —
  F2 **does not parse the broker export** (that was the old D8; now F4).

**Status:** 🟡 draft — 8 acceptance criteria (AC-4.1…4.8). Open: FX rate source/timing (Q-F4.2), multi-account/TFSA
dimension (Q-F4.1), idempotent re-ingest (Q-F4.3), theme mapping source (Q-F4.4).

---

## Discussion log

### 2026-06-28 — Session 1

#### Part A — The professional BUY → MANAGE → SELL lifecycle (definition of "disciplinary trading")

Core idea: a professional **executes a pre-defined process**, not in-the-moment decisions.
Discipline = removing discretion from the parts of trading where humans are predictably bad
(sizing, cutting losers, taking profits).

**Before the buy — thesis & plan**
1. Idea origination (here: `main_inference` ranked sleeve).
2. Thesis statement — one/two sentences: *why* it goes up, *over what horizon*. If you can't write it, don't buy.
3. **Falsification condition** — what would prove me wrong? Written *now*. (Most important pro habit.)
4. **Risk-first sizing** — size from max loss if stop hits (e.g. 0.5–1% of portfolio), not from hoped gain.
5. Pre-defined exits both directions — stop-loss *and* profit target / trim plan.
6. Portfolio-level checks — concentration limits, correlation to existing book.

**The buy — execution**
7. Entry trigger — the specific condition to actually buy.
8. Scaling plan — scale *in on confirmation*; avoid averaging *down* into losers.
9. Logging — entry price, thesis, stop, target, size, date (the audit trail).

**Managing the open position**
10. Monitor against the *thesis*, not the price.
11. **Stop discipline** — may *trail* up, rarely *widen*. Moving a stop down is the cardinal sin.
12. Trim winners past size limit; add only if thesis strengthens *and* room exists.
13. **Time stop** — exit if thesis hasn't started working in N weeks (dead money is a cost).

**The sell — exits**
14. Stop hit → exit, no negotiation.
15. Target hit → take profit / trim per plan.
16. Thesis broken → exit even at profit/small loss.
17. Better opportunity → capital is finite; sell weakest to fund strongest.
18. Post-trade review — log P&L *and grade the decision separately from the outcome*.

**Definition adopted:**
> Every position has, in writing and *before* entry: a thesis, a falsification condition,
> a risk-based size, a stop, and a target — and exits are executed by rule, not feeling.
> Outcomes are reviewed and decisions are graded on process.

The agent's real product: **"don't let me break my own rules."**

#### Part B — Transaction analysis (data/TransactionHistory_23280095.xlsx, Jan–Jun 2026, ~half the portfolio)

49 rows; 19 Buys, 18 Sells, 3 Dividends, 2 non-resident tax, 2 contributions, 2 FX.

| Symbol | Theme | #Trades | Hold span | Realized (closed) | Note |
|---|---|---|---|---|---|
| MRVL | AI/semis | in/out | 7 d | **+$10,137** | 100 sh 205→306 |
| SNDK | memory/semis | 9 (!) | repeated | **+$6,746** | in/out 901→1577 |
| MU | memory/semis | round-trip | 34 d | +$1,157 | |
| AMD | semis | round-trip | 5 d | +$492 | |
| SPCX (SpaceX CDR) | space | 5 | 2 d | +$1,866 | quick flip |
| INTC | semis | 2 round-trips | ~56 d | ~+$590 | USD+CAD legs |
| ENB | energy/income | flips + divs | ~63 d | +$900 + divs | only non-correlated name |
| ARM | AI/semis | 3 buys,1 sell | open | large open position | bought 235→345→391 |
| DELL | AI hardware | flips + open | open | 60 sh open ~419 | |

Note: raw "negative" net on ARM/DELL = **open positions**, not realized losses. Closed trades are net green.

**Strengths:** takes profits (doesn't marry positions); rode a real momentum trend; closed trades net positive.

**Red flags (professional read):**
1. **Extreme thematic concentration** — ~8/9 names = one AI/semis bet; true diversification ≈ 1.
   *(NOTE: per §profile, this is an accepted, intentional bet for 2026 — track it, don't "fix" it.)*
2. **Pyramiding up** — SNDK 901→920→1004→1091→1375; ARM 235→345→391; DELL 248→419.
   Biggest size ends up at worst price → how momentum traders give it back. **Victor wants to avoid this.**
3. **No visible risk framework** — sizes $2k–$25k with no apparent rule; no evident stops.
4. **Over-trading one name** — SNDK 9 times; churn cost.
5. **⚠️ TFSA + day-trading tax risk** — CRA can reassess a frequently-traded TFSA as "carrying on a business"
   and tax the *entire* gains. Highest-priority real-life flag. **Victor is reducing this in reality.**

**Real-life suggestions:** track theme exposure as a number (even if intentionally high); size by risk not conviction;
stop pyramiding past ~1.5× initial entry unless base is trimmed; confirm TFSA exposure w/ accountant; keep a trade journal.

#### Part C — Investor principles clarified (Victor's response)
Captured in the **Investor profile & principles** section above. Key deltas vs my first read:
concentration is *intended*; pyramiding fix = *sell less / let winners run*; risk-estimation feature wanted;
TFSA reduction already underway.

#### Part D — Thesis representation: how can the agent generate/understand/judge a qualitative thesis?

Reframe: the agent doesn't replace judgment. It (1) forces a written thesis, (2) structures it,
(3) monitors validity, (4) flags conflict with the quant signal.

**Approaches & trade-offs**

- **A. External LLM as thesis brain (Claude API).** Generate/critique/invalidate theses.
  - + Zero local compute (offloads the hard part); real language reasoning; can read news/filings (FMP MCP); cheap at this volume.
  - − Per-call cost/latency/network; non-deterministic (hard to backtest); sends portfolio context out.
- **B. Structured scorecard schema (fully local).** Decompose thesis → fixed scoreable fields; local pipeline aggregates.
  - + Deterministic, cheap, backtestable, transparent, integrates w/ rel5 SignalEngine.
  - − Rigid; loses nuance; doesn't *understand* text — pushes the judgment onto whoever fills the form.
- **C. Hybrid — LLM as extraction layer → local schema → local scorer. ✅ RECOMMENDED.**
  LLM *only* translates free text + news into the schema; cached as "thesis card"; refreshed on change.
  Local deterministic pipeline does all scoring/ranking.
  - + Language understanding (rare/cheap LLM calls) + deterministic backtestable judgment (local, in control);
    minimal spend; transparent; quant pipeline stays the decision-maker.
  - − Two layers to design/maintain; schema design effort up front.
- **D. Local embeddings for thesis-drift monitoring.** Small embedding model; cosine(thesis, news) detects divergence.
  - + Fully local, no per-call cost, good for *continuous* monitoring.
  - − Measures similarity, doesn't reason; can't generate/critique. A sensor, not a judge.

**Decision (this session): Approach C.**
Rationale — given *very limited local AI compute*, the external API is **more** feasible, not less:
it moves the heavy reasoning off the GPU (which Group-B training needs) and the volume is tiny
(~10 positions, refreshed only on news/change → cents/day).
- **Haiku 4.5** (`claude-haiku-4-5-20251001`): thesis→schema extraction + daily news-vs-thesis invalidation checks.
- **Sonnet 4.6** (`claude-sonnet-4-6`): occasional deep "red-team my thesis" critique (e.g. weekly).
- **Local pipeline stays boss:** thesis layer feeds a **gate/veto (pass / flag / fail)**, *not* another number
  blended into `combined_score`. Quant ranks; thesis gates. Cheaper, more robust, fits the discipline goal.
- Optional later: **D (embeddings)** for free continuous drift-sensing between LLM calls.

**Principle locked in:** use AI *only* where the problem is genuinely linguistic/qualitative;
everything deterministic stays plain code.

#### Part E — Portfolio risk-estimation: Google Sheet vs AI-agent?

Risk estimation is **deterministic math** (exposure %, vol, beta, pairwise correlation, concentration, simple VaR).
No qualitative judgment → **AI adds nothing.**
→ **Use a Google-Sheet template (or a small local Python script fed by the `TransactionHistory_*.xlsx` parser).**
Transparent, owned, auditable. Reserve the LLM for the thesis/news layer.
(This is Part-D's principle applied: Sheet/script for risk math; LLM only for thesis.)

---

### 2026-06-28 — Session 2: code audit of existing thesis/analysis generation

**Goal:** trace how the current code generates a "thesis" when (a) a stock name is entered in the
online-API and (b) `main_inference` runs. *Read-only audit — no code changed.* Symptom reported:
the online-API shows a **summary + signal** but **no detailed analysis report** while Group-B runs.

#### Key finding — Approach-C already exists in code (for the value/"Buffett" paradigm)
`pipeline/llm/llm_client.py` is a full Anthropic SDK wrapper (prompt caching, structured-JSON output),
default model `claude-sonnet-4-6`. So the hybrid "LLM understands text → structured fields → local logic"
plumbing is **already built** — Release-6 should *reuse* it, not rebuild it.

#### The two LLM layers (this is the core of the architecture)

**Layer 1 — "infer" = the summary + signal you see.**
`BuffettPipeline.run_infer_one(ticker)` → `InferResult` dataclass. Flow:
1. `QualityScreener` → cached fundamentals + `CompanyProfile` (moat_type comes from an earlier LLM filing parse).
2. `MarketDataEnricher` + `DCFCalculator` → intrinsic value; `SafetyMarginCalculator` → `zone`, `margin_of_safety`.
3. `EntryTimer` → technical entry signal (SMA50, RSI14, vol z-score, earnings-safe).
4. `NewsAggregator` → multi-source headlines.
5. **One LLM call:** `NewsAnalyst.analyze()` (Sonnet 4.6, `infer.llm_model`) judges *news materiality* →
   returns `material_event`, `direction`, `modified_signal`, `reason` (≈1 sentence), `high_impact_headlines`.
   Structured-JSON schema output; news caching disabled (per-call); graceful fallback to the quant signal
   with `reason="News analysis unavailable."` on LLM failure.
6. Result cached at `data/buffett/infer/{TICKER}_infer.json` — **filing-aware** cache (valid until the latest
   EDGAR periodic-filing date changes; 7-day wall-clock TTL safety net).
- Served by: `POST /infer`, `GET /infer/{ticker}`, `GET /api/infer/{ticker}` (synchronous).
- **This is the "summary + signal" surface. It works.**

**Layer 2 — "synthesis" = the detailed analysis report (the missing piece).**
`BuffettPipeline.run_synthesis_report_one(ticker)` → `SynthesisReportWriter.generate()`.
Sonnet 4.6 **+ web search**; produces archetype classification, cycle phase, valuation reconciliation,
narrative `verdict`/`conviction`, weighted FV, margin %. Writes:
- `reports/llm_reports/{TICKER}_report.md` (human-readable detailed report)
- `reports/llm_reports/{TICKER}_synthesis.json` (structured cache)
- Served by: `GET /synthesis/{ticker}/decision`, `/synthesis/{ticker}/full`, `/api/synthesis/{ticker}`.

#### main_inference flow (daily run)
> ⚠ **Superseded by Session 6** (R5 removed `SlotSelector`) — read `SlotSelector`→`SleeveSelector` and "top-3 BUY
> candidates" → "today's rolled weekday-sleeve pick" below. Kept verbatim as the Session-2 record.

`run_inference()` (pipeline/main_inference.py): build OHLCV (+f_* fundamentals) → load ranker/regressor/
classifier → score → `SlotSelector` → optional fundamental overlay → **Buffett review = `FundamentalEngine.infer_one`
(Layer 1 only)** on top-3 BUY candidates + current holdings → `SignalEngine.decide` fuses ML+overlay+Buffett into
FINAL action (veto/escalate) → persist positions → write `reports/inference_reports/<ts>/inference_summary.{json,md}`.
**`main_inference` never calls Layer 2 (synthesis).** The daily report carries the signal + short `reason`, not a detailed report.

#### ROOT CAUSE of "summary+signal but no detailed report"
The `/synthesis/{ticker}/full` and `/decision` endpoints **only read the disk cache**; if the file is absent
they return `render_pending_page(ticker)`. The detailed report is generated **only** by an explicit
`POST /synthesis/{ticker}/refresh`, which queues an **async background job** (`run_synthesis_report_one(force_refresh=True)`).
Nothing auto-triggers it — not `/infer`, not `main_inference`. So entering a ticker yields Layer-1 signal+summary,
while the full-report tab stays "pending" until you manually refresh **and wait** for the background job.
→ This is a **wiring/trigger gap**, not an ML gap. Matches the reported symptom exactly.

#### Bugs / gaps noted (NOT fixed, per freeze)
- **B1 — No auto-trigger for the detailed report.** Layer 2 is on-demand + async + cache-read-only.
  Design decision needed: should `/infer` (or `main_inference` for BUY candidates) pre-warm synthesis?
- **B2 — Alignment 409 is invisible to the report viewer.** `/synthesis/.../refresh` runs `enforce_alignment()`
  pre-flight and returns HTTP 409 + a prompt-diff *to the POST caller* if master vs component prompts drift.
  The GET `/full` page only ever shows "pending", so a drift failure looks like "report never generates"
  with no on-page reason. Surfacing the 409 into the pending/full page would remove this blind spot.
- **B3 — Everything uses Sonnet 4.6, including the cheap per-news materiality call**
  (`infer.llm_model` and `NewsAnalyst._model` both default `claude-sonnet-4-6`). Per the Part-D decision,
  the high-frequency materiality / invalidation check is the ideal place to drop to **Haiku 4.5** for cost.
- **B4 — Config model inconsistency.** Top-level `config/settings.yaml` `llm.model: "gemini-2.0-flash"` (legacy
  fundamental_analysis analyst?) coexists with the Buffett stack's `claude-sonnet-4-6` (`buffett.llm`, `infer`,
  `synthesis`). Verify which path is actually live to avoid paying for / debugging a dead config branch.
- **B5 — `reason` ≠ a disciplined thesis.** Layer-1 `reason` is a one-sentence *news-materiality* note, and
  `NewsAnalyst` judges news *generically*, NOT against a user-written thesis with a falsification condition.
  So today's system has a *materiality reason*, not the *thesis card* from Part-D.

#### What Approach-C still needs (Release-6 work, given the audit)
The LLM plumbing exists; the **disciplinary thesis layer** does not. To finish Approach C:
1. **Thesis-card schema + store** — per *position* (not per ticker): thesis statement, horizon, key catalysts,
   **falsification condition**, stop/target. Persist alongside `current_positions.json`.
2. **Thesis extraction** — reuse `LLMClient` (drop to **Haiku 4.5**) to parse free-text thesis → schema. New, small.
3. **Invalidation monitor** — re-point the *existing* `NewsAnalyst` materiality check at the *stored thesis*
   ("does this news break THIS thesis?") instead of a generic read. Reuse, don't rebuild.
4. **Auto-trigger / surfacing (fixes B1/B2)** — decide the trigger policy for Layer-2 synthesis (pre-warm BUY
   candidates in `main_inference`, or kick off from `/infer`), and surface alignment 409s to the viewer.
5. **Cost split (fixes B3)** — Haiku 4.5 for materiality/invalidation/extraction; Sonnet 4.6 only for the deep
   synthesis report. Matches the Part-D budget design.
6. **Thesis gate, not blended score** — feed the thesis layer into `SignalEngine.decide` as a pass/flag/fail
   gate (it already has veto/escalate authority), keeping the quant pipeline the ranker.

**Reusable assets discovered (don't rebuild):** `pipeline/llm/llm_client.py` (Anthropic wrapper),
`NewsAnalyst` (structured materiality call w/ JSON schema), `SynthesisReportWriter` (detailed report + cache),
`SignalEngine` (veto/escalate fusion), filing-aware caching, async job runner (`pipeline/api/async_jobs.py`),
prompt-alignment guard (`synthesis/prompt_alignment.py`).

---

### 2026-06-28 — Session 3: clarification of the 5 audit items (B1–B5) → folded into Intended Features

Victor's decisions on the Session-2 bug/gap list. These are **future implementation** (Release-5 frozen).

- **B1 — auto-trigger the detailed report. ✅ DECIDED.** The Layer-2 synthesis report **auto-generates for the
  daily BUY candidate.** Release-6 recommends **exactly one stock per day**, so this is one report/day — cost
  and trigger logic stay trivial. → **F1 + F2.**
- **B2 — alignment-409 explained (was a question, not a bug to "decide").** The master prompt spec
  `pipeline/buffett/synthesis/prompt_stock_analysis.md` is the single source of truth; a manifest requires each
  "key concept" to appear in *both* the master spec text *and* the matching component module. `enforce_alignment()`
  runs before any LLM call and raises `PromptAlignmentError` (→ HTTP **409 Conflict** + diff) if they drift.
  It prevents running the LLM with an inconsistent prompt definition. Consequence to fix: the 409 currently only
  reaches the POST caller, so the report viewer shows a silent "pending". With B1 auto-triggering, surfacing the
  409 to the page becomes necessary. → **F7.**
- **B3 — model tiering. ✅ DECIDED.** **Haiku 4.5** (`claude-haiku-4-5-20251001`) for the cheap materiality call
  (and thesis extraction + invalidation checks); **Opus 4.8** (`claude-opus-4-8`) for complex tasks (deep synthesis
  report, thesis critique). *(Updates the Part-D note that had named Sonnet for deep work — now Opus.)* → **F5.**
- **B4 — remove obsolete Gemini. ✅ DECIDED (future).** Read-only audit (Session 3): the only Gemini references
  are `config/settings.yaml:61–63` (top-level `llm:` block) and `config/env.yaml:44` (`google-generativeai`).
  **No Python imports gemini/genai**, and **nothing reads `config['llm']`** (only `config['buffett']['llm']` is
  consumed, by `LLMClient`). So removal is low-risk: delete the 3 config lines + the dep. Re-verify `llm.enabled`
  (line 63) has no consumer at implementation time. *Not removed now — R5 freeze.* → **F6.**
- **B5 — thesis-driven reason. ✅ DECIDED.** The `reason` must come from a **thesis-vs-falsification check**
  (re-point `NewsAnalyst` at the stored thesis card, asking "does this news break THIS thesis?") rather than a
  generic materiality read. Ties F4 ⇄ F3 (needs the thesis card to exist first). → **F3 + F4.**

---

### 2026-06-28 — Session 5: adopt **lean Spec-Driven Development (SDD)** from Release-6 onward

**Decision: ADOPT lean SDD.** The project's pains — weak tests, a silently-breaking online-API, and the risk that
**feature-engineering can be falsified without anyone noticing** — are exactly what a spec + contract/test layer fixes.
Honest framing: *the test/contract layer is what fixes the pain; SDD is the framework that forces it to exist and keeps
the implementing AI-agent aligned.* So we adopt SDD **lean**, not dogmatic.

**"Lean" means (strictness decided):**
- **One `spec.md` per feature** = WHAT/WHY + **acceptance criteria (Given/When/Then)** + **contracts inline**
  (data/API/schema). **Skip** separate `plan.md` / `tasks.md` — the AI-agent derives tasks from the spec.
- A project **`constitution.md`** for global non-negotiables (data contracts, invariants, the "AI only for
  qualitative" and veto/gate principles).
- **Research/experiment lane is exempt** from spec rigor (e.g. `--mode experiment`) — SDD gates production, not discovery.
- **Do not retro-spec rel1–5** — freeze the past with *characterization tests*; spec only *forward*.

**ML-adapted test tiers the specs must force into existence:**
data contracts · invariants/property tests (look-ahead, ranges, determinism) · **golden/characterization**
(freeze `OhlcvFeatureEngineer` output) · **API contract tests** (the breaking online-API) · metric gates (backtest RankICIR).

**`notebooks/` restructure (proposal — deferred until after R5 freeze; only NEW spec files created now):**
- `sdd/archive/` — move rel1–5 docs **as-is** (immutable record).
- `sdd/specs/` — **source of truth, current truth only**: `constitution.md`, `_templates/`, per-feature folders
  (`F1_disciplinary_report/spec.md`, `F2_delivery_channel/spec.md`, …).
- `sdd/design/` — non-authoritative brainstorm/rationale: the Session 1–5 discussion log moves here.
- `rel6_features.md` → becomes the specs index/README (or retired for `specs/README.md`).
- **`rel6_features.md` split:** "Intended Features" graduates into `specs/F*/spec.md`; the discussion+decisions log
  becomes `design/rel6_brainstorm.md`. Each spec gains a **Spec-ID + acceptance criteria + contracts + traceability
  (spec → tests → code)** — the acceptance criteria are the piece currently missing.

**Rollout (incremental):** P0 constitution + spec template · **P1 pilot spec = Feature 1** (this session) ·
**P2 characterization-test current feature-eng + API to freeze behavior** (do *before* R6 coding — this alone kills
most of the falsification fear) · P3 CI gate (test tiers must pass to merge).

**Pilot delivered this session:** `sdd/specs/constitution.md` + `sdd/specs/F1_disciplinary_report/spec.md`.

---

### 2026-07-11 — Session 6: post-R5 code-status refresh + SDD elevated to Feature 3

**Trigger:** Release 5 is CLOSED and merged (PR #7 / `db1b996`; close-out cleanup `ccd6d14`). This session re-reads the
merged R5 code and reconciles the (mostly Session-1–3) design notes with what the code actually does now, so the
implementing agent isn't coding against stale references. **No code changed — doc-only.** Where an earlier session
names old code, the note below is the correction of record.

**Code-status deltas vs. the earlier sessions (verified in merged R5):**
1. **`SlotSelector` is GONE.** R5 Feature 3-b removed it entirely; `SleeveSelector`
   (`pipeline/ohlcv/policy/sleeve_selector.py`) is the one and only selector, and the `backtest.policy`/`legacy_slots`
   knob was removed too. **Any "SlotSelector" / "top-3 slots" phrasing in Sessions 1–3 → read as `SleeveSelector`
   (1 pick/day, 5 persisted weekday sleeves).** Fixed inline in D1, T2.
2. **`main_inference` flow changed.** It no longer decides "top-3 BUY candidates re-picked daily". It scores the
   universe, **rolls TODAY'S weekday sleeve** through `SleeveSelector` (the other 4 sleeves surface as HOLD so the
   overlay/Buffett review can still veto held names), persists `data/sleeve_positions.json` + a flat
   `data/current_positions.json`. The Buffett Layer-1 review still runs on the rolled pick ∪ current holdings.
   *(Supersedes the Session-2 "main_inference flow" bullet.)*
3. **Live pricing is always-on.** `--live-price` is a **deprecated no-op**; in-hours a live FMP spot bar is appended,
   off-hours the previous trading day's close is used (**no synthetic bar**). This tightens F1 Q1/AC-1.8: T3's
   "session open" is still an explicit `open`-field fetch the code does NOT yet do.
4. **Gemini config still dead, line numbers shifted.** The `llm: {model: gemini-2.0-flash, enabled: …}` block is now
   `config/settings.yaml:58–60` (was 61–63 before the R5 config cleanup removed the `alpha_vantage:`/`news_api:`
   blocks), plus `config/env.yaml:44` `google-generativeai`. Still no live consumer → D6/B4 removal is still valid & safe.
5. **News is already FMP-first (B-adjacent).** R5 rewired `NewsAggregator` to FMP-first + keyless Yahoo RSS fallback and
   deleted the dead 5-way free fan-out (`news_fetcher.py` removed; the finnhub/marketaux/newsdata/alpha_vantage keys are
   gone from settings). Any R6 news work builds on the FMP path.
6. **LLM models unchanged since the audit:** `infer.llm_model` / `synthesis.llm_model` / `buffett.llm.model` all still
   `claude-sonnet-4-6`. So **B3/D5 model tiering (Haiku 4.5 cheap / Opus 4.8 deep) is still entirely unbuilt** — it
   remains R6 work.
7. **Feature counts (FYI for any feature-eng spec/golden test):** `ALL_FEATURES = 59` (14 price + 45 fundamental),
   `ALL_FEATURES_V2 = 61` (+2 Group-C). Relevant to the SDD P2 characterization/golden test.

**SDD elevated to Feature 3.** Session 5 adopted lean SDD and delivered the pilot; this session promotes it to a
first-class, **major cross-cutting Release-6 feature** (new "Feature 3 — Spec-Driven Development (SDD) adoption"
section above) with an explicit P0–P3 rollout status. **P0 completed later the same day (2026-07-11):**
`specs/_templates/spec.md` + `specs/README.md` added, and this brainstorm moved `rel6_features.md` →
`design/rel6_brainstorm.md` (pointer stub left behind). Still open: **P2 characterization tests**, **P3 CI gate**,
and the last structural step (move rel1–5 into `sdd/archive/`).

**Nothing about the Feature-1/2 *design intent* changed** — only the code coordinates it targets. The reuse assets in
"Reusable assets discovered" were re-confirmed present: `pipeline/llm/llm_client.py`, `NewsAnalyst`,
`SynthesisReportWriter` (`pipeline/buffett/synthesis/report_writer.py`), `SignalEngine`,
`pipeline/api/async_jobs.py`, `pipeline/buffett/synthesis/prompt_alignment.py`.

---

### 2026-07-22 — Session 7: pre-build code re-verification of D1–D10 (branch `rel6_discipline`)

**Trigger:** resuming the brainstorm before any Feature-1 code is written; re-verify every D-item against the
*actual* code on `rel6_discipline` so the implementing agent codes against reality, not Session-1–3 memory.
**Read-only audit — no product code changed** (only this doc + the D1 status cell). **Bottom line: zero Release-6
product code exists yet; every reuse asset is present & unchanged; all three LLM model settings are still
`claude-sonnet-4-6`. All D-items remain valid, with D1 re-scoped.**

**Per-item verdict (verified in code):**
- **D1 — selection DONE, hand-off open.** `SleeveSelector.select()` (`pipeline/ohlcv/policy/sleeve_selector.py:114`)
  already returns a single-element decision list (top-1 + incumbency δ); `main_inference.run_inference` already rolls
  today's sleeve and `SignalEngine.decide` (`main_inference.py:674`) emits the one FINAL action. The only missing piece
  is feeding that ticker to the Layer-2 report → **folds into D2.** *(This is the "D1 seems already implemented" observation — confirmed: the pick primitive ships; the report wiring does not.)*
- **D2 — NOT built (core gap).** `run_synthesis_report_one` is invoked from **exactly one** call site:
  `POST /synthesis/{ticker}/refresh` (`pipeline/api/app.py:343`). Neither `/infer` nor `main_inference` auto-triggers it.
- **D3 — NOT built.** No `ThesisCard`/thesis schema in `pipeline/`; `data/current_positions.json` is a flat
  `{"CHTR": 0.2}`. (grep hits for "thesis/falsification" are synthesis-narrative prose in `report_writer.py`, not a schema.)
- **D4 — NOT built.** `NewsAnalyst.analyze` (`pipeline/buffett/analysis/news_analyst.py:90`) still does *generic*
  materiality; no stored-thesis context is passed. Depends on D3.
- **D5 — NOT built.** `infer.llm_model` (`settings.yaml:336`), `synthesis.llm_model` (`:346`), `buffett.llm.model`
  (`:305`), `NewsAnalyst._model`, `web_search_provider._model`, `archetype_classifier._model`, `report_writer._model`
  — **all still default `claude-sonnet-4-6`.** **New finding:** `sonnet-4-6` is an *older generation*; D5 is therefore
  also a **model-version bump**, not just a cost split — cheap tier → **Haiku 4.5** (`claude-haiku-4-5-20251001`),
  deep tier → **Opus 4.8** (`claude-opus-4-8`), retire `sonnet-4-6` entirely.
- **D6 — still dead & safe to delete.** `config/settings.yaml:58-59` (`llm:` → `model: gemini-2.0-flash`) +
  `config/env.yaml:44` (`google-generativeai`) still present; **no Python reads `config['llm']`** (only
  `config['buffett']['llm']`), no `genai`/`gemini` import anywhere. *(Line-number correction: block is `58-59` now,
  not `58-60`; re-confirm whether an `enabled:` key still trails at `:60` at delete time.)*
- **D7 — still a gap.** The alignment **409 + diff is rendered only to the POST `/refresh` caller**
  (`app.py:176`, `:329` via `_render_alignment_failure_html`). The GET pending pages (`app.py:296`, `:311`) still call
  `render_pending_page(ticker)` with **no alignment reason** → the viewer blind spot D7 targets is intact.
- **D8 / D9 / D10 — NOT built** (portfolio-scoped). No `TransactionHistory_*.xlsx` parser, no risk script, no
  pyramiding/stop/time-stop guard in `pipeline/`. Still valid Feature-2 migration candidates.

**Reuse assets re-confirmed present & unchanged (S6 list holds):** `pipeline/llm/llm_client.py`,
`pipeline/buffett/analysis/news_analyst.py`, `pipeline/buffett/synthesis/report_writer.py` (writes
`reports/llm_reports/{TICKER}_report.md` + `_synthesis.json` at `report_writer.py:253-254` — matches the D3/output
contract), `pipeline/core/signal_engine.py`, `pipeline/api/async_jobs.py`,
`pipeline/buffett/synthesis/prompt_alignment.py`.

**Housekeeping note:** the only uncommitted spec edits (`spec.md`, `constitution.md`) are trivial header repointing
(`rel6_features.md` → `design/rel6_brainstorm.md`); no contract changed. SDD **P0/P1 still DONE, P2/P3 still not started.**

**Build-order implication (unchanged from S5/S6, now code-grounded):** the Feature-1 critical path is
**D3 (thesis schema) → D2 (auto-trigger wiring, consuming the D1 pick) → D4 (thesis-aware invalidation) → D7 (surface 409)**,
with **D5 (Haiku/Opus tiering + version bump)** and **D6 (Gemini delete)** as cheap parallel cleanups. Per S6, **P2
characterization tests should land before this product code.**

---

### 2026-07-22 — Session 8: daily-report **schema design** (graduated into F1 + F2 specs)

**Goal:** design the daily Disciplinary-Trading-Report schema — *meaningful, scalable, psychologically attractive,
actionable* — grounded in (a) the Session-1 discipline lifecycle + Victor's investor profile, (b) the existing
`reports/llm_reports/SNDK_Analysis_Report.md` (already an institution-grade decision one-pager), and (c) professional /
institutional templates (refs below). **Outcome graduated the same session:** the schema is now a **contract in the
specs** — F1 owns Layers A–C (`CT-1.1` Discipline Card expanded, `CT-1.4` Invalidation Monitor added), and **Layers D & E
split into the new `F2` spec** (`CT-2.1` portfolio context, `CT-2.2` decision journal) per Victor's decision.

**Design principle → mechanism (the four adjectives):**
- **Meaningful** — every field is an *action*, an *observable trigger*, or the *evidence* behind one. No decoration.
- **Scalable** — strict **layers A–E**, each independently serialized into `_synthesis.json`; **absent layers degrade
  gracefully** ("not yet tracked") so the report ships now (A–C) and grows (D–E) without breaking the JSON contract.
- **Psychologically attractive** — **card-on-top, depth-below**: Layer A is ≤1 phone screen, colour-coded verdict;
  depth collapses. Pre-committed exits remove in-the-moment agony (the whole point of "discipline = decide in advance").
- **Actionable** — Layer A is a *contract*: verdict + risk-based size + stop + time-stop + target + falsification, all
  concrete enough for a person to execute or a monitor to watch.

**The five layers (the SNDK report, formalized + the discipline fields it lacked):**

| Layer | Name | Owner | Maps to SNDK section | New vs SNDK |
|---|---|---|---|---|
| **A** | **Discipline Card** — glanceable pre-commitment contract | **F1** (CT-1.1) | SECTION 0 "DECISION PAGE" + "THESIS BREAKS IF" | **`time_stop`** (dead-money exit); **risk-based `position_size`** (size from max-loss-at-stop, not conviction) |
| **B** | **Invalidation Monitor** — observable tripwires + confirming signals | **F1** (CT-1.4) | SECTION 13 "BEAR-CASE TRIPWIRES" | `thesis_confirming_signals` (supports *let winners run*, not only exit) |
| **C** | **Detailed Analysis** — existing 14-section synthesis (reused as-is) | **F1** (CT-1.2) | SECTIONS 1–14 | — (no new work; `SynthesisReportWriter` already emits it) |
| **D** | **Position & Portfolio Context** — holding, pyramiding, exposure, risk, gate | **F2** (CT-2.1) | — (absent today) | pyramiding flag, theme-exposure *tracking*, deterministic risk, discipline gate, TFSA flag (D8/D9/D10) |
| **E** | **Decision Journal & Grading** — process-vs-outcome grade | **F2** (CT-2.2) | END "REQUIRED ACTIONS" (picks_log) | grade the **process, not the outcome** (anti-"resulting", Annie Duke) |

**Two discipline fields the SNDK template is missing** (and why they matter to Victor specifically): **`time_stop`**
(the Session-1 lifecycle rule "dead money is a cost"; SNDK has stop + target but no time-based exit) and **risk-based
`position_size`** (Session-1 Part-B red-flag #3 "no visible risk framework"; size from max-loss-at-stop, not conviction).
Both are cheap card fields and both target behaviors in the transaction analysis (over-holding, unsystematic sizing).

**Discipline reminder (re-derived for Victor, mapped to schema fields):** *discipline = pre-committing the decision so
nothing is decided in the heat of the moment* (Annie Duke; every trade-plan guide). BEFORE buy → thesis (`thesis`),
falsification (`falsification_condition`), risk-based size (`position_size`), both exits (`stop` + `targets`),
concentration *tracked* not blocked (Layer D `theme_exposure`). BUY → entry trigger (`entry_trigger`), scale on
confirmation / **avoid pyramiding-up** (Layer D `pyramiding_flag`; fix = *sell less / let winners run* → Layer B
`thesis_confirming_signals`). MANAGE → monitor thesis not price (Layer B), stops **trail up never widen down**
(`stop.basis`), **time-stop** (`time_stop`). SELL → stop/target/thesis-broken by rule; **grade decision ≠ outcome**
(Layer E `process_grade`). Product's job in one line: **"don't let me break my own rules."**

**Professional / institutional references (searched 2026-07-22):**
- **Discipline / trade-plan templates:** [AvaTrade Trading Plan](https://www.avatrade.com/education/correct-trading-rules/trading-plan) ·
  [TradeZella template](https://www.tradezella.com/tools/trading-plan-template) ·
  [Traders Union free templates](https://tradersunion.com/what-is-forex/trading-plan/plan-template/) ·
  [Notion Trading Journal](https://notiontradingjournal.com/blog/trading-plan/) (journal fields that separate *process from gambling*).
- **Institutional thesis structure & falsifiability:** [CFI Equity Research Report](https://corporatefinanceinstitute.com/resources/valuation/equity-research-report/) ·
  [Wall Street Prep sample report](https://www.wallstreetprep.com/knowledge/sample-equity-research-report/) ·
  [Sutton Prep — Investment Thesis Structure](https://suttonprep.substack.com/p/free-template-the-investment-thesis) (thesis as a *falsifiable hypothesis*).
- **Kill criteria / pre-mortem / decision grading:** [Gary Klein — Pre-Mortem](https://www.gary-klein.com/premortem) +
  [HBR Project Premortem](https://hbr.org/2007/09/performing-a-project-premortem) (assume it failed; list why — this *is* Layer A `falsification_condition` + Layer B tripwires) ·
  [Annie Duke — overcoming outcome bias / "resulting"](https://www.annieduke.com/overcoming-outcome-bias-how-to-improve-learning-decision-making-ft-annie-duke-ovul-sezer/) (grade the decision, not the outcome — Layer E).
- **Best in-repo template:** `reports/llm_reports/SNDK_Analysis_Report.md` §0 "DECISION PAGE" — the schema is largely its formalization.

---

### 2026-07-24 — Session 9: revise D1 — top-1 is a backtest policy; practice needs a familiar Watchlist Slate + dual report

**Trigger:** Victor is *not confident* acting on a top-1 pick drawn from 123 names — an unfamiliar name can't be
underwritten, and the disciplinary product only works on names you can write a thesis for. Evaluated whether to keep
top-1 only for backtest/experiment. **Outcome graduated into F1/F2 specs the same session.**

**Core reframe — three universes (do not conflate):**
1. **Training universe** (123 names) — ML breadth (RankICIR); untouched.
2. **Backtest/experiment selection** (`SleeveSelector` top-1 + 5 weekday sleeves + incumbency) — the *validated
   portfolio-construction policy*; **stays exactly as-is** (it's what the Sharpe/RankICIR is optimized on).
3. **Practice watchlist** (curated ~10–30 familiar names) — **NEW**; the live decision surface. Distinct from the
   existing `data/buffett/watchlist.json`, which is an **auto-populated quality-screen registry** (currently holds
   ISRG etc.), *not* a curated familiar list — do **not** overload it; use a new curated config list.

**Honest counterpoints raised (not just agreement):** (a) restricting to familiar names is discretion overriding a
breadth model — resolved by keeping it *reviewable* (the off-watchlist nudge lets the watchlist grow) rather than a
silent blindfold; (b) trading a familiar subset won't reproduce the backtested Sharpe — the backtest validates *ranking
skill*, the watchlist is a personal risk overlay. Suggested (future) a **watchlist-restricted backtest variant** to
*measure* the edge given up.

**Victor's four decisions (this session):**
1. **Deep report on BOTH the global top-1 AND the top-watchlist** — top-1 to *expand knowledge on unfamiliar stocks*,
   watchlist for underwritable action. Dedupe to one report when they coincide.
2. **Repeated unfamiliar (global-top-1) names → reuse + update** the prior report, don't regenerate (save credits).
3. **Same reuse + update for the top-watchlist report** (expected to recur often).
4. **Fully automated daily → email**, so the reuse-vs-regenerate + which-report decisions must be **by rule, no
   interactive input** at fire time.

**Key mechanic discovered in code:** `SynthesisReportWriter.generate()` is today **binary** — a <24h cache hit returns
the old report *unchanged*, else a **full Opus regenerate**; there is no incremental "reuse-narrative + refresh-volatile"
path. **Elegant fix:** the **Haiku invalidation check (D4 / Layer B) becomes the refresh gate** — a 3-state policy
**REUSE / UPDATE / REGENERATE** (CT-1.6): UPDATE reuses the expensive Opus narrative and refreshes only live price + MoS
+ `as_of` (one cheap Haiku call), REGENERATE (full Opus) fires only on a new EDGAR filing, a fired invalidation, or TTL.
The invalidation monitor thus does double duty: discipline feature *and* cache-refresh gate.

**Spec changes made:** F1 — new §3a (three universes + daily dual output), T2/T3 now dual-pick, new **CT-1.5 Watchlist
Slate** + **CT-1.6 Refresh Policy**, AC-1.4 rewritten (dual + dedupe), new AC-1.11/1.12/1.13, Q5 (watchlist scope,
default = subset of scored universe) + Q6 (refresh TTLs). F2 — Email confirmed (Q-D1 resolved), payload = slate + both
reports, new AC-2.8 (no interactive input).

**Still open:** Q6 TTL thresholds (REUSE/UPDATE/REGENERATE windows).

**Session-10 resolutions (2026-07-24):** **Q5 CONFIRMED** — watchlist ⊆ 123-name scored universe (unknown name fails
loud, not silently dropped). **Q-D1 CONFIRMED** — delivery = **Gmail SMTP**, **HTML** body (slate table + cards inline),
**`.md`** report attachment(s); credentials via env.

---

### 2026-07-25 — Session 11: the fund-desk roles model + AI-pipeline task catalog (I/O schemas)

**Trigger:** Victor asked how a professional active-managed fund divides work, and where he vs the AI-pipeline vs the
"fund manager" sit — then asked to turn the AI's roles into intended features + SDD specs with **input/output schemas**
so he can *feed real trading data and monitor* the pipeline.

**Roles model (locked):** a professional fund has four seats — **Fundamental Analyst** (ideas + thesis + monitoring),
**Portfolio Manager / Fund Manager** (the *decision*: what, how much, when to add/trim/exit; owns the P&L),
**Execution Trader** (fills the PM's decision well), **Back/Middle office + Risk** (reconciliation, P&L, risk, records).
The separation exists so the *decider* is not the *idea-generator* or the *book-keeper* — that's what removes bias.

- **Victor = Portfolio Manager + Trader.** *Not "just the trader"* — a trader only executes decisions someone else made;
  here there is no other human and **the AI is deliberately not the PM** (P3: quant ranks, thesis *gates*, never decides).
  So the PM seat — discretion, sizing, and **P&L accountability** — must be Victor's. He wears two hats: PM (decide/size/
  manage the book) and Trader (place the order well).
- **AI-pipeline = Analyst + Risk + Back-office.** Confined to the *non-discretionary* seats: it advises, computes, and
  records. It never commits capital. When Victor overrides a discipline flag, the AI's job is to make that override
  **visible and logged**, not to block it.
- **The "fund manager" is not a separate entity** — it's a hat Victor must consciously wear. Accountability can't be
  outsourced to a stochastic model. The line between Victor and the AI is **authority/accountability, not capability**:
  the AI may *support* PM work (sizing math, exposure) but never hold PM *authority*.

**AI-pipeline task catalog (desk → task → I/O → owning spec/contract → status).** This is the "how do I feed data &
monitor" map — each task's data shape is a spec contract:

| Desk | Task | Input | Output | Owner | Status |
|---|---|---|---|---|---|
| **Analyst** | Idea generation / ranking | OHLCV+fundamental features | ranked slate (`rank_score`, `pred_return`, `prob_up`) | F1 CT-1.5 + ML pipeline | 🟢 exists (ranking); slate 🟡 |
| **Analyst** | Deep research / synthesis | ticker + fundamentals + web | Layer-C report `{TICKER}_report.md` | F1 CT-1.2 | 🟢 exists |
| **Analyst** | Thesis authoring | synthesis bundle | Discipline Card (CT-1.1) | F1 | 🟡 spec'd |
| **Analyst** | Thesis monitoring / invalidation | stored card + news | invalidation verdict + Layer-B monitor | F1 CT-1.4 (D4) | 🟡 spec'd |
| **Risk** | Portfolio risk metrics | portfolio state (F4) | vol, beta, corr, VaR, exposure | F2 CT-2.1 | 🔵 reserved |
| **Risk** | Pre-trade discipline gate | trade intent + card + state | PASS/FLAG/FAIL | F2 (P3 gate) | 🔵 reserved |
| **Risk** | Pyramiding / theme / TFSA flags | portfolio state (F4) | flags | F2 CT-2.1 | 🔵 reserved |
| **Back-office** | Broker-export ingestion | `TransactionHistory_*.xlsx` (CT-4.1) | parsed txns | **F4 CT-4.1** | 🟡 spec'd (NEW) |
| **Back-office** | Reconciliation → portfolio state | txns + live prices | `portfolio_state.json` (CT-4.2) | **F4 CT-4.2** | 🟡 spec'd (NEW) |
| **Back-office** | Mark-to-market | live FMP snapshot (CT-4.4) | unrealized P&L | **F4** (reuse `_append_live_prices`) | 🟡 spec'd |
| **Back-office** | Trade/intent log | manual entry (CT-4.3) | `trade_log.jsonl` | **F4 CT-4.3** | 🟡 spec'd (NEW) |
| **Back-office** | Decision journal + grading | card snapshot + close | Layer-E grade (CT-2.2) | F2 CT-2.2 | 🔵 reserved |
| **Back-office** | Book-state monitor | state + F1/F2 flags | `book_state.json` (CT-4.5) | **F4 CT-4.5** | 🟡 spec'd (NEW) |
| **Back-office** | Delivery | persisted reports + slate | daily email | F2 CT-2.3 | 🟡 spec'd |

**Key gap identified → new spec F4.** The Analyst desk was already F1 and the Risk/Journal/Delivery desk already F2, but
**nothing specced the data plane** — how real trading data gets *in* and how Victor *monitors* the book. `data/
current_positions.json` is only `{TICKER: weight}` (no cost, P&L, currency, or cash). So **F4 — Portfolio & Market Data
Plane** was created (grounded in Victor's *real* BMO InvestorLine export: columns `Transaction Date, Settlement Date, Activity
Description, Description, Symbol, Quantity, Price, Price Currency, Total Amount, Total Currency`; activities `Buy/Sell/
Dividend/Non resident tax/Contribution/Foreign Exchange`; mixes USD+CAD). F4 is pure deterministic plumbing (P2, no LLM),
and it is the **foundation F2's portfolio layers stand on** — F2 now *consumes* F4's `portfolio_state.json` rather than
parsing the export itself.

**Data flow (feed → compute → monitor):** `TransactionHistory_*.xlsx` (feed) → **F4** parse+reconcile →
`portfolio_state.json` (truth) → **F1** thesis/monitor + **F2** risk/gate/journal compute on it → **F4** `book_state.json`
+ **F2** email (monitor). Victor reads the book-state + reports, makes the PM/Trader decision, records it via the trade
log (CT-4.3) — closing the loop.

---

### 2026-07-26 — Session 12: mock-report review → Layer F, the curated watchlist, and pre-coding spec audit (1st production trial)

**Trigger:** after visualizing the full daily product as a mock (real FMP data for MU), Victor made three calls and
asked for a final spec audit before an AI-agent starts the **first production trial**.

**1. "Your Move" is now a mandatory report layer (F).** Victor wants the PM/Trader action checklist kept in *every*
production report — an explicit coaching reminder while he builds experience in the roles. → new **F1 Layer F / CT-1.7**
(`your_move`), assembled **deterministically** from Layers A/B(/D), role-tagged `{PM, TRADER, BACK_OFFICE}`, always
rendered, never an auto-action (AI advises, Victor decides). Added to the CT-1.0 envelope (now 6 required keys) + AC-1.14.

**2. Curated watchlist set (13 names).** `pipeline.practice_watchlist` (config/settings.yaml, new key — distinct from
`data/buffett/watchlist.json`): MSFT, GOOGL, NVDA, MU, SNDK, ARM, INTC, AMD, MRVL, CNQ, ENB, POWL, PLTR. Per Q5 the
watchlist must be ⊆ the scored universe, so the **7 not in the 123-set were added to `pipeline.tickers`** (now 130) —
pending a **retrain + data verification**:
- **In 123 already (score now):** MSFT, GOOGL, NVDA, MU, INTC, AMD.
- **In `sp500_tickers.yaml` (US filers) → need OHLCV+fundamental pull:** SNDK, MRVL, PLTR.
- **NOT in any list → need CIK+sector in `sp500_tickers.yaml` + data-availability check:** POWL (US 10-K, easy),
  **ARM (foreign 20-F ADR), CNQ + ENB (Canadian 40-F)** — foreign filers are a real EDGAR/fundamental-pipeline risk to verify.

**3. Pre-coding spec audit — resolved 2 ambiguities the mock exposed:**
- **P3 hand-off (slate BUY vs card HOLD):** added the rule — slate `signal` = quant's raw view; card `verdict` =
  thesis-gated final; the gate may only make `verdict` **equal-or-more-conservative** (never upgrade); when they differ
  the **card governs the action** and Layer F reflects the card. Card now records `quant_signal` for audit (F1 §4 + CT-1.1).
- **Book-state `thesis_status` with no cached report:** added `UNTRACKED` (+`thesis_as_of`) — only the daily pick(s) get
  a fresh thesis; other holdings show last-known or UNTRACKED, surfaced not blank (F4 CT-4.5).
- Housekeeping: README AC ranges refreshed (F1→1.14, F2→2.8, F2 status 🟡); "Layers A–C" → "A–C + F" where stale.
- **FMP finding (real):** the news config default `lookback_hours` ≈ 3h returned **0** MU headlines; 168h returned 50.
  **Recommend defaulting news lookback to ≥72h** before the invalidation monitor (D4) goes live, or it runs half-blind.

**Recommended build order for the FIRST production trial (thin vertical slice first):**
1. **Slice 1 — end-to-end on ONE name:** watchlist-top pick → Discipline Card (A, incl. `quant_signal`) + reuse the
   existing `SynthesisReportWriter` for C + **Your Move (F)** → **Gmail-SMTP email**. Skip dual-report, refresh policy,
   book state. Proves the pipeline. *(Do the P2 characterization tests first — S6.)*
2. **Slice 2:** dual pick + dedupe (D1/§3a) + Watchlist Slate (CT-1.5) + model tiering (D5, Haiku/Opus) + Gemini delete (D6).
3. **Slice 3:** incremental refresh policy (CT-1.6) + surface 409 (D7).
4. **Slice 4 — F4 data plane:** ingest → `portfolio_state.json` → `book_state.json` (unblocks F2 Layers D/E).
5. **Slice 5 — F2:** risk metrics + discipline gate + decision journal, computed on F4.

---

## Candidate feature backlog (from Session 1)

Priority reflects fit to Victor's actual behavior; not yet scheduled.

1. **Portfolio reconciliation** — ingest `TransactionHistory_*.xlsx` → current holdings, avg cost,
   realized/unrealized P&L, per-theme exposure. *Data backbone for everything; clean first deliverable.*
2. **Pre-trade discipline gate** — no logged buy without thesis + stop + target + risk-based size.
3. **Concentration / theme-exposure tracker** — report theme % (concentration is intentional, so *track*, don't block);
   alert only on hard user-set ceilings.
4. **Pyramiding monitor** — flag a buy materially above avg cost in the same name ("adding at +52% above basis").
   Directly targets the behavior Victor wants to curb.
5. **Stop & time-stop tracker (phone alerts)** — enforce exits by rule.
6. **Thesis layer (Approach C)** — thesis card schema + Haiku extraction + invalidation gate.
7. **Trade journal + decision grading** — auto-log from broker export; grade decision vs outcome post-close.
8. **TFSA-activity flag** — count short-hold round-trips in registered accounts; warn near "business" territory.
9. **Risk-estimation sheet/script** (§E) — deterministic risk metrics, non-AI.

---

## Open questions (to revisit)
- Victor has further comments on earlier parts of Session 1 — **pending discussion.**
- Which feature is the Release-6 MVP? (Leaning: #1 reconciliation → #6 thesis gate / #9 risk sheet.)
- Phone/online API surface: read-only alerts first, or interactive (log trades, request thesis critique)?
- Data privacy stance on sending portfolio context to Claude API (affects Approach C scope).
- **(Session 2) Layer-2 trigger policy:** auto-pre-warm synthesis for BUY candidates in `main_inference`,
  kick off from `/infer`, or keep manual `/synthesis/{ticker}/refresh`? (fixes symptom B1)
- ~~**(Session 2) Verify the live LLM path** — is `llm.model: gemini-2.0-flash` dead config or an active analyst? (B4)~~
  → **RESOLVED (S6): dead config.** No Python reads `config['llm']`; safe to delete (`settings.yaml:58–60` + `env.yaml:44`).
- **(Session 6) SDD sequencing** — write the P2 characterization tests (freeze feature-eng + online-API) *before* any
  Feature-1 product code? (Session 5 says yes.) And create `specs/_templates/` + run the `notebooks/` archive/design
  restructure — before R6 coding or after Feature 1 ships?
- **(Session 4) Feature-2 delivery channel** — confirm **Telegram (primary) + Email (archive)**, or pick another
  (Discord webhook / Pushover / ntfy / cloud-sync)? Decision pending Victor.

## Decisions log
- 2026-06-28: Thesis representation → **Approach C (hybrid LLM-extraction → local schema → local gate)**;
  Haiku for extraction/monitoring, Sonnet for deep critique; thesis is a **gate/veto**, not a blended score.
- 2026-06-28: Risk-estimation → **deterministic Sheet/script, not AI.**
- 2026-06-28: Principle → **AI only for genuinely qualitative/linguistic problems; deterministic math stays plain code.**
- 2026-06-28 (S2): Audit → **Approach-C LLM plumbing already exists** (`pipeline/llm/llm_client.py`, Sonnet 4.6).
  Two layers: infer (signal+summary, works) vs synthesis (detailed report, on-demand/async/cache-read-only).
  "No detailed report" = **wiring/trigger gap (B1)**, not an ML gap. Release-6 = thesis card + invalidation monitor
  + Layer-2 trigger + Haiku/Opus cost split, **reusing** existing assets.
- 2026-06-28 (S3): B1 → **auto-trigger Layer-2 report for the single daily BUY candidate** (Release-6 = 1 stock/day).
- 2026-06-28 (S3): B3 → model tiering **Haiku 4.5 (cheap calls) + Opus 4.8 (complex)** — **supersedes** the
  Part-D "Sonnet for deep critique" line.
- 2026-06-28 (S3): B4 → **remove orphaned Gemini config/deps** (settings.yaml 61–63 + env.yaml 44); audit confirms
  no live consumer. Deferred until after R5 freeze.
- 2026-06-28 (S3): B5 → **`reason` derives from a thesis-vs-falsification check**, not generic news materiality.
- 2026-06-28 (S4): Added **Feature 2 — Automated daily run + report delivery channel** (placeholder). Delivery must be
  **self-contained & persistent** (no API-link dependency). Leaning **Telegram (primary) + Email (archive)** — pending Victor.
- 2026-06-28 (S5): **Adopt lean SDD from Release-6.** Strictness = **spec.md (acceptance criteria + inline contracts)
  per feature; skip plan/tasks docs; `constitution.md` for globals; research lane exempt; characterize-not-retro-spec
  the legacy.** `notebooks/` → archive/ + specs/ + design/ (restructure deferred; new spec files created now).
- 2026-07-11 (S6): **R5 closed & merged** (PR #7 / `db1b996`) → the R5-freeze rule is lifted; R6 builds on merged R5.
- 2026-07-11 (S6): **SDD promoted to Feature 3** (major cross-cutting R6 feature). **P0 DONE** — pilot
  (`constitution.md` + F1 `spec.md`) plus `specs/_templates/spec.md`, `specs/README.md` index, and the
  `design/rel6_brainstorm.md` move. Still NOT done: **P2 characterization tests**, **P3 CI gate**, `sdd/archive/`.
  **P2 characterization tests are the highest-leverage next step — do them before writing Feature-1 product code.**
- 2026-07-11 (S6): Code-status refresh — **`SlotSelector` removed → `SleeveSelector`**; live pricing always-on
  (`--live-price` deprecated no-op); Gemini config still dead at `settings.yaml:58–60` + `env.yaml:44`; news already
  FMP-first; model tiering (Haiku/Opus) still unbuilt. (Design intent unchanged; only code coordinates.)
- 2026-07-26 (S12b): **All undecided parameter values RESOLVED** (config/settings.yaml): refresh hard-TTL **7d** +
  REUSE window **6h** (`synthesis.*`); news `lookback_hours` **72** (`news_apis`, fixes the 3h→0-headlines bug);
  new `portfolio:` block — `base_currency CAD`, FMP run-time `USDCAD`, **realized P&L per-currency** (no historical FX),
  `pyramiding_threshold_pct 15.0` (severe ≥50%), `theme_ceiling_pct null` (track-only), `track_account true`,
  `txn_dedupe_key` tuple (idempotent re-ingest), `theme_map_path` (+ GICS-sector fallback). Specs Q6/Q-D4/Q-D5/
  Q-F4.1–4.4 all marked RESOLVED. Only design-level Qs remain (F1 Q1 T3-open-price, Q2 thesis-origin, Q3 scheduler-host,
  Q4 card-persistence; F4 Q-F4.5 trade-log UX) — not parameter values.
- 2026-07-26 (S16): **FIRST REAL END-TO-END LLM RUN — 4 production bugs found that stubs could not.**
  Staged (Haiku ping → live invalidation → Opus 5 synthesis) so the expensive call only ran once everything upstream
  was proven. **Bugs found & fixed:** (1) **web-search 400** — `web_search_provider` double-wrapped the caller's tool
  definition as `input_schema`, so the inner object had no top-level `type`; the API rejected the request and **all
  three web-search sections (cycle, supply-side, ETF) silently failed** on every synthesis ever run. (2) **"Streaming
  is required"** — raising `max_tokens` for Opus-5 thinking headroom crossed the SDK's non-streaming 10-minute
  ceiling, so *every* deep synthesis failed; `LLMClient` now auto-streams at ≥16000 max_tokens. (3) **ETF tripwires
  silently dropped** — the real ETF schema has no `action` field (the model writes "…condition → trim" inline), and
  the builder required a separate field, discarding the most useful (free-to-watch) tripwires. (4) **`openpyxl` not
  declared** in `config/env.yaml` — the project env could not read the broker export at all, so F4 was undeployable.
  Also fixed a **misleading log** (`LLMClient ready (model=opus-5)` printed before the per-feature override, making
  cheap Haiku calls look expensive) → new auditable `use_model()`; billing was always correct.
  **Live results (MU):** Opus 5 returned archetype=cyclical_commodity, cycle=**peak** with quantified evidence
  (DRAM +98% QoQ, GM 84.9%, growth all price no volume), verdict **SELL / medium-high**, weighted FV $747 vs $921
  (MoS −18.9%), stop $460, targets 418/747/1250, size 1.5%, plus SMH/SOXX observable tripwires. The **P3 gate fired
  on real data**: quant BUY → card SELL. Haiku invalidation on real news returned **FLAGGED** (CXMT competitive
  entry), correctly checking each falsification condition and not over-calling BROKEN.
  **Measured cost: ~$2.50 per full REGENERATE** (399k in / 20k out — web search dominates), ~$0.006 per daily UPDATE;
  with CT-1.6 that is **≈$10/month**. 500 tests green in the project env, 497 in base.
- 2026-07-26 (S15): **F2 BUILT — 8/8 ACs green** (`pipeline/discipline/`: risk, flags, gate, journal, context;
  89 tests, 490 overall). Layers D/E now compute on F4's `portfolio_state.json` and are wired into the daily brief.
  **Risk** = pure deterministic stats (annualized vol, beta, corr-to-book, parametric 1-day 95% VaR with component
  contributions that sum to 100%) — tests assert no LLM and no socket (P2). **Gate** returns PASS/FLAG/FAIL and folds
  into the signal as a **veto only** — `apply_to_signal` can downgrade a BUY but never create or upgrade one (P3).
  **Journal** grades *process, not outcome*: identical process + opposite P&L ⇒ identical grade, and
  `graded_separately_from_pnl` is asserted True at the schema level so it can't drift into convention.
  **Real-data findings:** (1) **TFSA risk quantified — 17 of 18 round-trips held under 30 days** (SNDK ×5, SPCX ×4),
  which is Session-1's highest-consequence flag now measured rather than suspected; (2) ARM is **63.5% of the book**
  at −32.7%, gate=FLAG (38.5 pts over a 25% target), annualized vol 93%, beta 1.57, 1-day 95% VaR 6.15% of NAV
  (CAD 1,984), VaR contribution 100%; (3) incomplete-history now also catches **DELL** (first event is a dividend on
  shares bought pre-window). **Integration bug caught by a test:** `portfolio_context_by_ticker` was coerced None→{}
  before the Layer-D builder's `is None` check, so Layer D silently never populated — fixed to test emptiness.
- 2026-07-26 (S14): **INV-8 amended → Claude Opus 5** + **F4 data plane BUILT.**
  **Constitution amendment (§5.3):** deep tier moves Opus 4.8 → **`claude-opus-5`** (same $5/$25 per MTok, better
  reasoning). **Migration consequence handled:** Opus 5 runs adaptive thinking *by default* and `max_tokens` caps
  thinking+answer together, so every Opus call site got headroom (filing 4096→16000, synthesis 16000→32000, sections
  2000→8000). Thinking left ON deliberately — our Opus calls are structured tool-use extractions, and disabling thinking
  on Opus 5 can make a tool call arrive as plain text that silently never runs. Also upgraded web search
  `web_search_20250305` → `web_search_20260209` (dynamic filtering) and dropped the stale `prompt-caching-2024-07-31`
  beta header (caching is GA). Verified no `temperature`/`top_p`/`top_k` anywhere — those 400 on Opus-tier.
  **F4 BUILT — 8/8 ACs green** (`pipeline/portfolio/`: ingest, reconcile, snapshot, trade_log, book_state; 75 tests).
  Verified end-to-end on the real BMO InvestorLine export: 47 transactions → 1 open position (ARM 56sh @ avg $386.22 vs $260.01
  live = −32.7%), realized YTD +$27,576 USD / +$1,056 CAD, fees YTD $262 USD / $60 CAD, NAV CAD 32,277 at live
  USDCAD 1.408. **Real data-integrity finding:** the export sells 355 ENB but buys only 135 — 220 shares predate the
  Jan-1 window, so ENB's cost basis is understated. Silently clamping would have produced an authoritative-looking
  wrong number, so CT-4.2 gained `incomplete_history` + a loud WARNING (P5). **Fix: ingest an earlier export.**
  397 tests green.
- 2026-07-26 (S13): **Slice 2 built — D5 + D6 + D4.** **D5 model tiering (INV-8) landed:** `infer.llm_model` →
  Haiku 4.5 (news materiality, the highest-frequency call), new `synthesis.llm_model_classifier` → Haiku 4.5 (the
  256-token archetype call), `synthesis.llm_model` → Opus 4.8 (deep report), `buffett.llm.model` → Opus 4.8 (filing
  analysis — low-frequency but quality-critical, so deep tier despite being "extraction"). No `claude-sonnet-4-6`
  remains anywhere. **D6 done:** the dead `llm:` gemini block and `google-generativeai` dep are deleted. **D4 done:**
  `NewsAnalyst.analyze` now takes the stored Discipline Card and answers "does this news break THIS thesis?", returning
  `thesis_status ∈ {INTACT, FLAGGED, BROKEN, UNTRACKED}`; BROKEN forces `reason` to "THESIS BROKEN", sets the signal to
  AVOID, and — via new `pipeline/report/invalidation.py` — **closes the CT-1.6 refresh gate** that Slice 1 left stubbed.
  Verified end-to-end: warm cache + intact thesis → UPDATE with **no Opus call**; broken thesis → REGENERATE.
  Fail-safe: a failed check returns FLAGGED, never a false "intact". **Q1 resolved (spot price is fine)** → AC-1.8
  re-scoped from blocked to a characterization test. 309 tests green.
- 2026-07-26 (S12): **Layer F "Your Move" mandatory** (F1 CT-1.7, coaching reminder, deterministic, role-tagged);
  **curated `pipeline.practice_watchlist` set (13 names)** + 7 added to training universe (now 130) pending retrain/data
  (ARM/CNQ/ENB/POWL need CIK+foreign-filer checks). **Pre-coding audit resolved:** P3 hand-off (card `verdict` governs,
  gate only downgrades, card records `quant_signal`); book-state `thesis_status=UNTRACKED` when no cached report. **FMP:**
  default news `lookback_hours`≈3h → 0 headlines; raise to ≥72h. Recommended 5-slice build order for the 1st trial.
- 2026-07-25 (S11): **Fund-desk roles model + AI task catalog → new spec F4.** Victor = PM + Trader (keeps decision &
  P&L accountability); AI = Analyst + Risk + Back-office (advises/computes/records, never decides — P2/P3). Desks map to
  features: Analyst→F1, Risk+Journal+Delivery→F2, **Back-office data plane→F4 (NEW)**. F4 grounds input/output schemas in
  Victor's real BMO InvestorLine export (CT-4.1) → canonical `portfolio_state.json` (CT-4.2) → `book_state.json` monitor (CT-4.5);
  deterministic, no LLM. F2 now *consumes* F4's portfolio state instead of parsing the export.
- 2026-07-24 (S10): **Spec-quality audit fixes.** **Constitution INV-6 amended** (per §5.3, with rationale): "one
  *actionable* recommendation/day" (watchlist-top) — discovery reports (global-top-1) don't count, so the dual report is
  compliant. Added **Unit + Integration** test tiers to constitution §4. F1: new **CT-1.0 `_synthesis.json` envelope**
  (required vs optional keys); **AC-1.1 layering fixed** (`/infer` returns Layer-1 DC-3, not the Layer-2 CT-1.1 card);
  **verdict enum → BUY/HOLD/SELL only** (matches `SignalEngine`; accumulate/trim nuance moves to
  `position_size.existing_holder_action`). Threshold magic-numbers (`pyramiding_threshold_pct`, refresh TTLs)
  **parameterized but left undecided** (F2 Q-D5 / F1 Q6).
- 2026-07-24 (S9): **D1 revised — top-1 is backtest-only; practice = Watchlist Slate + dual deep report.** Three
  universes (training 123 / backtest top-1 / curated practice watchlist). T2/T3 build **both** the global top-1 (learn
  unfamiliar names) **and** the top-watchlist name (deduped). **Incremental refresh policy CT-1.6 (REUSE/UPDATE/
  REGENERATE)** with the Haiku invalidation check as the refresh gate → repeated names reuse+update, not regenerate
  (credit-saver). **Email confirmed** as delivery (F2); fully automated, no interactive input. New curated watchlist ≠
  `data/buffett/watchlist.json`.
- 2026-07-22 (S8): **Daily-report schema designed & graduated into specs.** Five layers A–E (card-on-top/depth-below,
  graceful degradation). **F1 owns A–C** — expanded `CT-1.1` Discipline Card (added `time_stop` + risk-based
  `position_size` vs SNDK), new `CT-1.4` Invalidation Monitor, ACs 1.9/1.10. **Layers D & E split into new `F2` spec**
  (`F2_portfolio_and_delivery`, 🔵 draft) as reserved contracts `CT-2.1`/`CT-2.2` + delivery. Grounded in SNDK report §0
  + institutional refs (pre-mortem/kill-criteria, process-vs-outcome grading). Risk math stays deterministic (P1).
- 2026-07-22 (S7): Pre-build re-verification on `rel6_discipline` — **all D1–D10 still valid; zero R6 product code yet.**
  **D1 re-scoped: selection primitive already ships** (`SleeveSelector` top-1 pick); only the report hand-off remains
  (→ D2). D2/D3/D4/D5/D7 unbuilt; D6 confirmed dead (`settings.yaml:58-59` + `env.yaml:44`). **New: D5 is also a
  model-version bump** — baseline is `claude-sonnet-4-6` (older gen), replace with Haiku 4.5 / Opus 4.8. Critical path:
  **D3 → D2 → D4 → D7**, with D5/D6 as parallel cleanups; P2 characterization tests first.
