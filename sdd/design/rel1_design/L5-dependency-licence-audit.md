# L5 — Dependency licence audit  ·  `MS-9.3`

> **Tier:** release-scoped design record. **Status:** ✅ first pass 2026-09-04.
> **Status:** ✅ **complete 2026-09-04** — every declared dependency audited, including the
> `anthropic` transitive tree.
> **Why it exists:** `MS-9.3` gates the **first publish** (`QR-12`). ⚠ This repo is
> **source-available, all rights reserved** — it grants no rights — so a copyleft
> dependency would be a genuine conflict, not a formality.

## The audit

| Package | Version | Licence | Verdict |
|---|---|---|---|
| `pandas` | 2.2.3 | BSD 3-Clause | ✅ permissive |
| `numpy` | 2.1.3 | BSD 3-Clause *(the metadata inlines the text; the classifier confirms)* | ✅ permissive |
| `PyYAML` | 6.0.2 | MIT | ✅ permissive |
| `lightgbm` | 4.6.0 | MIT | ✅ permissive |
| `pyarrow` | 19.0.0 | Apache-2.0 | ✅ permissive |
| `pytest` | 8.3.4 | MIT | ✅ dev only |
| `ruff` | 0.16.6 | MIT | ✅ dev only |
| `anthropic` | 1.4.0 | **MIT** | ✅ **verified 2026-09-04** |

### ✅ `anthropic`'s transitive tree — audited 2026-09-04

★ **This is the half that a one-line licence check misses.** The SDK is MIT; what it *pulls in* is
the actual question.

| Package | Version | Licence | |
|---|---|---|---|
| `httpx` · `httpcore` · `idna` | — | BSD-3-Clause | ✅ |
| `pydantic` · `pydantic_core` · `anyio` · `sniffio` · `jiter` · `h11` · `annotated-types` | — | MIT | ✅ |
| `distro` | 1.9.0 | Apache-2.0 | ✅ |
| `typing_extensions` | 4.16.0 | PSF-2.0 | ✅ |
| ⚠ **`certifi`** | 2025.11.12 | **MPL-2.0** | ★ **see below** |

#### ⚠ `certifi` is MPL-2.0 — and it does NOT constrain this project

A keyword scan flags `MPL` as copyleft and **stops there**; that would be the wrong conclusion.

- **MPL-2.0 is FILE-LEVEL (weak) copyleft.** It obliges you to share modifications **to the
  MPL-licensed files themselves**. ⚠ It does **not** reach the surrounding project, unlike GPL/AGPL.
- `certifi` is Mozilla's **CA root bundle**; MPL is the bundle's own licence.
- ★ **This project does not modify it** — it arrives transitively through `httpx` and is used
  unmodified. **Obligation: none beyond retaining its notice.**

> ★★ **The lesson worth keeping.** The only non-permissive licence in the tree was **four levels
> down**, in a package nobody chose, and it needed a **judgement about the KIND of copyleft** rather
> than a match on the word. ⚠ An automated licence gate that fails on `MPL` would have blocked this
> project on a CA certificate bundle.

## ★ What licences THIS project may adopt

Because **nothing in the dependency tree is strong copyleft**, the choice is **completely
unconstrained** — no dependency forces or forbids any option below.

| | Option | Grants | Fits `QR-12`? |
|---|---|---|---|
| ★ **1** | **All rights reserved / source-available** *(current)* | ⛔ none — readable only | ✅ **yes** — this is what *"review only, I keep all rights"* means |
| **2** | **PolyForm Noncommercial** / **PolyForm Strict** | non-commercial or evaluation use | ✅ yes, if you want to grant *something* |
| **3** | **BUSL-1.1** (Business Source Licence) | use now, converts to Apache-2.0 after N years | ◐ partly — the auto-conversion gives rights away on a timer |
| **4** | **Elastic Licence 2.0** | use, except as a hosted service | ◐ aimed at SaaS competition, not at this |
| **5** | **MIT / Apache-2.0 / BSD** | ⚠ everything | ✗ **no** — `QR-12` rejected these explicitly |
| **6** | **GPL-3.0 / AGPL-3.0** | ⚠ everything, with copyleft | ✗ **no** — still an OSI grant |

★ **Recommendation: stay on option 1.** `QR-12` decided it, nothing has changed, and it is the only
row that grants **nothing**. ⚠ Options 2-4 are worth knowing only if you later want reviewers to
*run* the code rather than read it — and **none of them is reversible in practice**, because a
licence once granted cannot be withdrawn from copies already distributed.

★ **No copyleft anywhere in the declared set.** Nothing conflicts with an
all-rights-reserved publication.

⚠ **`anthropic` is the one gap.** It is declared upstream and imported by the LLM
gateway, but is **not installed in this environment**, so its licence was not read
— only recalled. `MS-9.3` is a *gate*, and a recalled licence is not an audited
one. **Install it and re-run before the first publish.**

## ⚠⚠ Two findings the audit surfaced that are not about licences

**1. `lightgbm` is imported and was NEVER DECLARED — not here, not upstream.**
Three import sites in `src/models/`. ★ An undeclared runtime dependency means a
clean environment fails at import time with no hint of what to install, and the
`MS-9.1` mirror would ship a `pyproject.toml` that cannot build the thing it
describes.

**2. ⚠⚠ This repo declared NO runtime dependencies at all.** `pyproject.toml`
carried a `dev` extra only, while `MS-8` moved in 15 domains needing `pandas`,
`numpy`, `PyYAML`, `lightgbm` and `anthropic`.

> ★★ **So the absorption checklist was missing a SIXTH thing.** `DX-3` established
> four (code · tests · `ownership.yaml` globs · architecture rules); `DX-8` added
> `config/`. **`DX-13` adds runtime dependency declarations.** Each absorption moved
> the code that *needs* the dependency and left the line that *declares* it behind —
> and because the dev machine already had everything installed, **nothing failed.**

## What to do before the first publish (`MS-9.1`)

1. ✅ **DONE 2026-09-04 — `anthropic` verified.** The check was three things, not one:
   - **(a) the SDK's own licence.** Expect MIT. ⛔ *GPL/AGPL/SSPL/Commons Clause* would conflict
     with all-rights-reserved publication.
   - ⚠⚠ **(b) its TRANSITIVE dependencies** — `httpx`, `pydantic`, `anyio`, `distro`, `sniffio`,
     `jiter`, `typing-extensions`. ★ **A package's own licence says nothing about what it pulls
     in**, and this is exactly where reading one line differs from an audit.
   - **(c) licence vs. TERMS OF SERVICE.** The SDK is MIT; **the API it calls is governed by
     Anthropic's commercial terms**, which are a separate instrument. ⚠ Not a dependency-licence
     question — but it does bear on whether *model outputs* may be published.

   ★ **Result:** SDK **MIT**; tree permissive except `certifi` (**MPL-2.0**, weak/file-level, used
   unmodified — no obligation). ⚠ **(c) remains open and is NOT a licence question:** the SDK is MIT,
   but **the API it calls is governed by Anthropic's commercial terms**, which bear on whether *model
   outputs* may be published. That is worth reading before publishing anything the model wrote.
2. ✅ Declare the runtime dependencies (done 2026-09-04 — see `pyproject.toml`).
3. ⚠ Re-run this audit whenever a dependency is added. It is cheap and it is a gate.
