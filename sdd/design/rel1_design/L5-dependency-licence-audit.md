# L5 — Dependency licence audit  ·  `MS-9.3`

> **Tier:** release-scoped design record. **Status:** ✅ first pass 2026-09-04.
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
| ⚠ `anthropic` | **not installed here** | MIT *(believed)* | ⛔ **UNVERIFIED — verify before publish** |

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

1. ⛔ **Install `anthropic` and verify — THREE things, not one:**
   - **(a) the SDK's own licence.** Expect MIT. ⛔ *GPL/AGPL/SSPL/Commons Clause* would conflict
     with all-rights-reserved publication.
   - ⚠⚠ **(b) its TRANSITIVE dependencies** — `httpx`, `pydantic`, `anyio`, `distro`, `sniffio`,
     `jiter`, `typing-extensions`. ★ **A package's own licence says nothing about what it pulls
     in**, and this is exactly where reading one line differs from an audit.
   - **(c) licence vs. TERMS OF SERVICE.** The SDK is MIT; **the API it calls is governed by
     Anthropic's commercial terms**, which are a separate instrument. ⚠ Not a dependency-licence
     question — but it does bear on whether *model outputs* may be published.

   ```bash
   pip install anthropic
   python3 -c "import importlib.metadata as m; print(m.metadata('anthropic').get('License'))"
   pip install pip-licenses && pip-licenses --packages anthropic --with-system   # (b)
   ```
2. ✅ Declare the runtime dependencies (done 2026-09-04 — see `pyproject.toml`).
3. ⚠ Re-run this audit whenever a dependency is added. It is cheap and it is a gate.
