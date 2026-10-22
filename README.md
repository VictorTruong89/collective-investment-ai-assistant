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
| **Specs** | **14** feature specs (`F1`…`F12`, with `F6a/b`, `F7a/b`), **213 acceptance criteria**, all 🟢 approved — plus design-tier rules for the 15 inherited domains |
| **Code** | ~46,500 lines in 377 modules across 15 domains (`src/`) |
| **Tests** | **2,736** — 2,729 pass, 6 skip, and **1 red on purpose** (`J-07`, a golden case re-established against its recording by the fund manager) |
| **Findings** | **169** discrepancies logged (`DX-n`), each with what it cost and how it was closed |
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

★ **The D-04 detail lives in one place: [`src/models/README.md`](src/models/README.md)** — what the run prints and how
to read it, every argument, the decisions, where files land. The default sequence, same day as step 2:

```bash
python -m src.models.train                     # fit + out-of-sample + simulation + three gates, ~21 min — ONE command
python -m src.models.promote <artifact_id>     # read the gate report; changes nothing
```

It **never promotes on its own** (MT-52) and the bars do not move: D-04 is **functionally complete, skill unproven**
(Victor, 2026-10-11 — F12 `D16`). ⚠ The simulated return is survivorship-biased and not to be quoted.

### 4 · Review, promote, or designate (D-04)

`--approve` promotes only a model whose every gate passed (no override). `--card-informational` lets a **refused**
model rank the card, labelled as one — fit 4 (`sha256:8200ada7…`) is designated today; such a card is **never**
actionable (DN-41). Details: [`src/models/README.md`](src/models/README.md) §4.

### 4b · The shadow trial (D-04, MT-64…66)

Fit 4 is frozen and scored on the future. **On or after 2026-11-06, after the close**, then every 21+ trading days:

```bash
python -m src.data_engine.ingest events --universe sp500 --years 10
python -m src.models.shadow record      # ~15–20 min
python -m src.models.shadow score       # grades every matured snapshot
```

`status` shows the record. The criterion and the rest: [`src/models/README.md`](src/models/README.md) §4.

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

- **No promoted model.** The best fit (fit 4) was refused — walk-forward *t* = 2.51 against a bar of 3; it ranks the
  card as a designated, labelled refused model, and D-04 is closed as *functionally complete, skill unproven*.
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
