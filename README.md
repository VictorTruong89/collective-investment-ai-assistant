# Collective Investment AI Assistant

A single-machine investment analysis system that can **explain and defend every
recommendation it makes — and measure whether any part of it actually helps.**

> ## ⚠⚠ Status disclosure — read this first
>
> **No ranking model is promoted.** The last fit (August 2026: walk-forward IC 0.0203,
> realised *t* = 1.42) was refused by its own significance gate, and the daily card ranks
> by a plain momentum **rule** and says so. **Every card is informational, never
> actionable**: it reads *"no verdict — ranked #1 by the rule; no thesis"*, because no
> thesis runs in the daily path and the book cannot be valued (Canadian listings and CDRs
> are not on the data plan). Nothing here is a claim that the strategy works.
>
> **Everything runs by hand** — the daily card, retraining, the data sweeps and theses. No
> paid LLM API is used; development LLM calls go through the Claude Code subscription.
>
> ★ This disclosure is required by the project's own constitution (`PG-10`):
> *no output may present a recommendation as actionable, or publish a performance
> figure, unless the model behind it has passed its own promotion gates — or the
> output states plainly that it has not.*

---

## What this is

*Measured 2026-10-06.*

| | |
|---|---|
| **Specs** | **14** feature specs (`F1`…`F12`, with `F6a/b`, `F7a/b`), **212 acceptance criteria**, all 🟢 approved — plus design-tier rules for the 15 inherited domains |
| **Code** | ~46,500 lines in 377 modules across 15 domains (`src/`) |
| **Tests** | **2,729** — 2,722 pass, 6 skip, and **1 red on purpose** (`J-07`, a golden case re-established against its recording by the fund manager) |
| **Findings** | **168** discrepancies logged (`DX-n`), each with what it cost and how it was closed |
| **Questions** | **25** design questions answered, with the options that were rejected (`sdd/questions.md`) |

It is **spec-driven**: `sdd/specs/` is the source of truth and the code is
downstream of it. A `PreToolUse` hook refuses an edit to a governed path until the
governing spec has been read in that session — per session, because context does
not carry over and neither should the permission.

## Start here

| If you want to | Read |
|---|---|
| ★ **Judge the engineering** | [`docs/essays/E1-what-the-process-caught.md`](docs/essays/E1-what-the-process-caught.md) — thirteen things the process caught that review did not *(written 2026-09-04; its counts are of that date)* |
| Understand the goal | [`sdd/specs/vision.md`](sdd/specs/vision.md) |
| Understand the rules | [`sdd/specs/constitution.md`](sdd/specs/constitution.md) |
| See *why* a decision went the way it did | [`sdd/questions.md`](sdd/questions.md), and each spec's §7 *Decisions* |
| See where the build stands | `sdd/design/rel1_design/L3-build-sequence.md` §2.1 — and its §6 for what went wrong and when |
| See what a live run still needs | `sdd/design/rel1_design/L9-go-live-checklist.md` — one section per domain |

## Running it

```bash
pip install -e ".[dev]"
python tools/check_all.py      # every guarantee, one command
python -m pytest -q            # the suite (J-07 is red on purpose)
```

⚠ **`src` is an implicit namespace package.** Do not add `src/__init__.py` — a
regular package ends the import scan, and the layout depends on it.

---

## Operating it by hand — the runbook

★ **Every step below costs $0 in API money.** FMP is a fixed monthly subscription, SEC and
EDGAR are free, and none of these commands calls an LLM. All state lands under `.state/`
(git-ignored) or `$PIPELINE_STATE_DIR` if set — one variable for every command (OR-54).

### 0 · Load the credentials (every new shell)

```bash
set -a; source .env; set +a      # FMP_API_KEY, EDGAR_CONTACT, the GMAIL_* delivery settings
```

### 1 · Record the BMO InvestorLine statements (D-11)

Download each account's **full history** and save it as
`.state/broker/bmo_investorline/TransactionHistory_<TYPE>_<N>.csv` (`TFSA_1`, `TFSA_2`,
`RRSP_1`, `RESP_1`). **Replace** the old file — never append, overlapping files double-count.

```bash
python -m src.recording.check            # read-only: window, orders, positions, cash per account
python -m src.recording.check --record   # then append each sound account to the change log
```

A bad file is named with its reason; a past row BMO changed is reported as a **restatement**.
⚠ Compare the derived cash with BMO's screen now and then — it matched to the cent on
2026-08-25 and 2026-10-06.

### 2 · Fresh market data (D-07)

```bash
python -m src.data_engine.ingest symbols --universe sp500              # SEC ticker snapshot (renames)
python -m src.data_engine.ingest events  --universe sp500 --years 10   # corporate actions, delistings, earnings
python -m src.data_engine.ingest status                                # what each store holds — and does not
```

⚠ Delistings reach back only ~3 weeks and the earnings calendar 365 days on the FMP plan, so
backtests stay stamped **survivorship-biased**. `status` names the command that sweeps each class
that has not been swept yet. A long sweep prints `⏱ … elapsed · now: <stage>` every 15 s to stderr,
and each stage's duration as it ends — `events --years 10` takes a long time.

### 3 · Train and backtest (D-04, graded by D-03)

```bash
python -m src.models.train --limit 20 --prepare-only   # smoke: data + panel + labels, no fit (minutes)
python -m src.models.train                             # the real run: ~500 names, 10 years, 1-month horizon
python -m src.models.train --refresh-events            # … re-sweeping splits/reverse splits/dividends inline only
```

⚠ **The calendar must cover today** (MT-57): if the event store was last swept on an earlier day, every class reads
unchecked and training is **refused**. ★ Run step 2's `events` sweep **the same day** for full coverage;
`--refresh-events` re-sweeps only splits, reverse splits and dividends, so the run proceeds with the other classes
(restatements included) unchecked and printed as such. `--allow-unchecked-calendar`
overrides, and the run then says it carries no calendar guarantee. The run's date is New York's (MT-56).
★ The trees are fitted on each day's **return rank** (`--target xs_gauss`, the default; `--target raw` for the old
target). Two out-of-sample measurements are printed: the **walk-forward** (trains on the past only — ★ it GATES significance
and breadth, F12 `D14`) and the **purged k-fold** (reported; feeds only the simulation).

The real run fetches **prices from FMP** and **fundamentals from EDGAR** for the whole S&P 500
(add `--skip-facts` to reuse the stored fundamentals; `--refresh-events` sweeps step 2's events
inline), fits the ranker, then runs the **D-03 backtest**: a purged, embargoed walk-forward IC, a
portfolio simulation (held names drift, $0 commission), breadth, and the three gates —

| gate | passes when | note |
|---|---|---|
| `ic_significance` | **walk-forward** `|mean IC| ≥ 3 × realised SE` (Newey-West) | the purged k-fold is printed beside it, not gated (F12 `D9`, `D14`) |
| `breadth` | implied IR `|IC| · √BR ≥ 0.5`, `BR` from the residual correlation after SPY (F12 `D13`) | raw-ρ and market+sector figures and the held book are printed, never gated |
| `cost_survival` | net return > 0 | at $0 commission this equals gross > 0 |

It prints `⏱ train · … elapsed · now: <stage>` every 15 s to stderr (fundamentals, prices, calendar
check, features panel, labels, fit, walk-forward IC, portfolio simulation, breadth, D-03 evaluation),
each stage's duration and the total. It **never promotes on its own** (MT-52). It prints the artifact id and leaves the model
**pending review** in `.state/models/<artifact_id>/` (`evaluation.json` holds every number).
⚠ Expect a refusal from a weak signal — that is the gates working.
⚠ **A calendar HALT stops the run** (MT-54) and names each event — e.g. a delisting. A restatement does not halt
training: its fundamentals are **replayed per filing date** (FE-40), so each day sees what was filed by then — the original
figure before an amendment, the amended one after (DE-76). The replay runs in parallel (cores − 2, at most 16). Sector-relative features use the GICS map in `config/sp500_tickers.yaml` (today's classification, applied to the whole window). Splits and dividends from the event store are applied to every price
panel (DE-78 — the `events` sweep in step 2 is what feeds them). Each run also prints the **residual correlation
against SPY and the sector SPDRs** (12 extra FMP calls) beside the breadth gate — reported, not gated (F12 `D12`).

### 4 · Review and promote (D-04)

```bash
python -m src.models.promote <artifact_id>             # show the gate report; changes nothing
python -m src.models.promote <artifact_id> --approve   # promote — refused unless every gate PASSed
```

There is no override. A promoted model ranks the next daily card.

★ **The card may instead be ranked by a REFUSED model — labelled as one** (MT-67, Victor 2026-10-09): the momentum
rule measured walk-forward IC −0.008, the refused fit 4 +0.030 on the same dates.

```bash
python -m src.models.promote <artifact_id> --card-informational       # designate (refused models only)
python -m src.models.promote <artifact_id> --card-informational-off   # revoke → the rule ranks again
```

The card then reads *"no verdict — ranked #1 by a refused model"* and names the failed gates; such a card can **never**
be actionable (DN-41). A promoted model, if one ever exists, takes precedence.

### 4b · The shadow trial — a refused model scored live (D-04, MT-64…66)

The refused clean fit (`sha256:8200ada7…`) is never served; it is **scored on the future**, the only evidence about
it that cannot be tuned. Start once, then record one snapshot **every 21+ trading days** (e.g. once a month, after the
close — `record` snapshots the latest COMPLETED trading day; FMP posts a day's bar after it ends), and score whenever
you like:

```bash
python -m src.models.shadow start sha256:8200ada7bf5f6ced48984006bc864f6908052a712a9be4c11060273bca7e5f36   # once — freezes the model + the criterion
python -m src.models.shadow record      # ~15–20 min: facts, prices, splits/dividends, panel, both rankings
python -m src.models.shadow score       # grades every snapshot whose 21 trading days have passed
python -m src.models.shadow status      # snapshots, live ICs, pooled t, leakage alarm
```

★ Pre-registered criterion: live monthly ICs pooled with the model's walk-forward history; **pooled t ≥ 3** meets the
evidence bar (≈ 3–4 years if the IC holds); from 6 snapshots a **leakage alarm** fires if live IC runs well below
history. The card's momentum rule is recorded beside it for comparison. ⚠ Meeting the bar does **not** promote —
step 4 does. `record` refuses a date inside the model's training window, within 21 sessions of the last snapshot, or
with 0 calendar classes checked (run step 2's `events` sweep the same day, or `--allow-unchecked-calendar`); it never
writes the event store.

### 5 · The daily card (D-08 → D-09)

```bash
python -m src.orchestration.entrypoint --plan-only   # show the job graph; runs nothing
python -m src.orchestration.entrypoint               # today's card (S&P 500 universe)
python -m src.orchestration.entrypoint --deliver     # … and email it (and any failure notice)
```

It blocks on a non-trading day or before the 10:00 ET open is settled. Run the step-2 event sweep
first, or the calendar check has nothing to check.

### 6 · A thesis on demand (D-01)

Not a single command. `tools/run_thesis_once.py` rebuilds Stages B–D over **fixed, recorded
Micron runs** (as of 2025-06-26); a thesis for another ticker or date is the manual chain in
`sdd/design/rel1_design/L9-go-live-checklist.md` §13.2.

---

## ⚠ What is deliberately not working

Stated because a project that lists only its successes is not evidence of judgement.

- **No promoted model.** The ranker's last fit was refused (realised *t* = 1.42); the card ranks by rule.
- **No card can be actionable.** The book cannot be valued — Canadian listings and CDRs are not on the
  FMP plan (accepted, `AB-3`) — and no thesis runs daily, by decision.
- **Backtests are survivorship-biased** and say so: the FMP plan cannot list past delistings.
- **On-demand theses cover one ticker at one date** (Micron, 2025-06-26) without a manual rebuild.
- **The golden-case programme is closed.** 53 signed cases are kept; judgement is now measured by
  falsifiers and rule checks (`L8` §9).
- **The deliberation experiment (`F7a`)** has run once and returned `INSUFFICIENT`.
- **External-truth tests run only on the fund manager's machine.** They check derived cash against
  real broker statements (a frozen August copy in `.state/broker/frozen_2026-08-25/`), which are
  correctly excluded from version control; on a fresh clone they skip, loudly.

## Licence

**Source-available. All rights reserved.** See [`LICENSE`](LICENSE).

⚠ This is **not open source**: the code is readable, and no rights to use, modify
or distribute are granted. Calling it open source would be a category error a
technical reviewer would notice.

Dependency licences are audited in
[`sdd/design/rel1_design/L5-dependency-licence-audit.md`](sdd/design/rel1_design/L5-dependency-licence-audit.md)
— no copyleft in the dependency set; `anthropic` (MIT) and its transitive tree were verified
2026-09-04.
