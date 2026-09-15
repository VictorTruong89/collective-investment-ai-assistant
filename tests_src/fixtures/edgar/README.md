# EDGAR fact-ledger fixtures

Public SEC data, recorded from `https://data.sec.gov/api/xbrl/companyfacts/` through
D-07's own `ingest_facts` path, then filtered to the tags a test needs.

| File | Recorded | What | Why |
|---|---|---|---|
| `MU_facts_valuation_subset.parquet` | 2026-09-13 · ✏ re-recorded 2026-09-14 with `D8`'s securities and finance-lease tags (2,123 rows; the 1,779 earlier rows unchanged) | Micron (CIK 0000723125), CT-7.3 ledger rows for the `F10` valuation tags + revenue | `AC-F10.7`'s recorded-fixture half and `DX-103`: the real filer uses `InterestExpenseNonoperating` and lease-inclusive debt tags, and its derived quarters abut with a **0-day gap** |

⚠ **Verified against the filing, not against itself:** as of 2025-06-26 the valuation reads
cash **$10,163M** (10-Q line 559), long-term debt **$15,003M** and current debt **$538M** (lines
347/344), diluted shares **1,125M** (line 1090) — the lines of
`tests_src/fixtures/filings/MU_FY2025Q3_10Q.txt`. ✏ 2026-09-14: short-term investments **$648M** and
long-term marketable investments **$1,402M** (line 559 — with cash, $12,213M) ⇒ net debt **$3,328M**.
