# Source evaluation — citation graphs and institutional databases

> **Destination:** folds into `docs/lectures/L4-6-retrieval-and-the-literature-loop.html` §6.3.
> **Researched:** 2026-09-09, against the bibliometrics literature rather than vendor claims.
> **Trigger:** the fund manager did not trust the stated values and impacts in §6.3(b)–(c). Correctly.

---

# 1 · OpenAlex vs Semantic Scholar — which citation graph do we trust?

## The measured position

Both are credible. The differences are **specific and publisher-dependent**, which turns out to
matter for us more than any overall quality verdict.

| | OpenAlex | Semantic Scholar (S2AG) |
|---|---|---|
| Total references indexed, 2015–2023 (~37.5M articles) | **982.6M** | **994.3M** precalculated · 896.8M source |
| Mean references per article | 25.52 | 25.83 precalc · 23.29 source |
| Journal coverage | ★ Indexes **nearly all journals in both Scopus and Web of Science**, plus non-Western sources | Broad, but sparser reference resolution |
| Reference coverage vs Scopus / WoS | ★ **Comparable**, on a cleaned 16.8M-publication shared corpus | Not the benchmark subject |
| Unique capability | Full CC0 snapshot; institutional aggregation; no API key | ★★ **Citation *contexts*** — the sentence in which one paper cites another |
| Known weakness | ⚠ Citation graph is **not complete** for indexed works; document-type classification noisy; abstracts fewer than WoS/Scopus | ⚠ Coverage gaps in ID resolution; possible duplicate/false-positive counting |

## ★ The finding that decides it for this project

Reference coverage **differs by publisher**, and the split falls almost exactly along our
reading list:

| Publisher | Which graph has more references | Journals this affects for us |
|---|---|---|
| **Elsevier** | ★ **OpenAlex, by +12.6M references** | *Journal of Financial Economics*, *Journal of Banking & Finance*, *Journal of Empirical Finance*, *Journal of Financial Markets* |
| **Taylor & Francis** | Semantic Scholar, by +269K | *Financial Analysts Journal*, *Quantitative Finance* |
| SAGE, Frontiers | Semantic Scholar | — (not our field) |

There are roughly **9 million articles where Semantic Scholar carries more source references
than OpenAlex** — so neither is a superset.

## ⚠ The caveat that matters most for us

**OpenAlex is a rapidly evolving index whose contents change.** The bibliometrics literature
raises this explicitly as a reproducibility concern. For this project it is not academic:
a search run today is **not reproducible later** unless the result set is snapshotted at the
time. That is the same problem `C7` solves for model runs, arriving in the research loop.

Separately, on cross-database metadata agreement: **66.7% of citations show at least one
metadata disagreement** between major databases. Author names agree only **29–39%** of the
time — **DOIs agree 100%**.

## Decision

| | Role |
|---|---|
| ★ **OpenAlex** | **Primary.** Discovery, citation-graph walking, venue/ISSN screening for the venue policy. Best coverage where our core journals live (Elsevier), CC0, no key |
| ★ **Semantic Scholar** | **Secondary, and not optional.** Citation *contexts* are unique to it and are our dissent-finding mechanism for `PG-11` req. 3. Also better for T&F |
| **Crossref** | **Tie-breaker and identity authority.** When the two disagree on metadata, the DOI is the only field that agrees everywhere — resolve on DOI, always |

⚠ **Never key a record on author name or title.** Key on DOI. The 29–39% author agreement rate
is the reason, and it is also why cross-source dedup is the one job that eventually justifies
`tools/litsearch.py`.

★ **Snapshot every search result set** — query, date, returned DOIs — at the time it is run.
Cheap now, impossible to reconstruct later.

---

# 2 · The four institutional databases — should we use all four?

## ★ First: the question contains a category error, and it is mine

The §6.3(c) table put **WRDS** alongside three publishers. That was wrong and it made the four
look comparable. They are not:

- **Elsevier, Springer Nature, Wiley** are *publishers* — they sell access to **papers**.
- **WRDS** is a *data* platform — CRSP, Compustat, IBES, TAQ. It contains **no papers at all**.

So "should we use all four" cannot be answered as one question. WRDS is on a different axis and
is evaluated separately below.

## ★★ Second: the four are the wrong four

Checked against the venue policy's Tier 1, the top finance journals map to publishers like this:

| Tier-1 finance journal | Publisher | In our four? |
|---|---|---|
| *Journal of Finance* | **Wiley** | ✅ yes |
| *Journal of Financial Economics* | **Elsevier** | ✅ yes |
| ★ *Review of Financial Studies* | **Oxford University Press** | ❌ **NO** |
| ★ *Journal of Financial and Quantitative Analysis* | **Cambridge University Press** | ❌ **NO** |
| *Review of Finance*, *Review of Asset Pricing Studies* | Oxford University Press | ❌ **NO** |
| *Management Science* | INFORMS | ❌ no |

**Two of the top four finance journals are not reachable through any of the four databases
we discussed.** OUP is the larger gap — it carries RFS, *Review of Finance* and *RAPS*.

✅ The librarian already confirmed uOttawa holds an **OUP TDM agreement**
(`data.mining@oup.com`). Cambridge was never asked about.

## The verdict, per database

| Database | Use it? | Reasoning |
|---|---|---|
| ★ **Wiley** | ✅ **Yes — first token to request** | *Journal of Finance* is the single most important journal for this project. Also *Mathematical Finance*, *Journal of Futures Markets* |
| ★ **Elsevier** | ✅ **Yes — second token** | *JFE* plus three Tier-2 journals. And OpenAlex's reference coverage is strongest here, so discovery and full text align |
| ★ **OUP** | ✅ **Yes — add it; it was missing** | *RFS* + *Review of Finance* + *RAPS*. Confirmed available. **The biggest gap in the original list** |
| **Cambridge** | ❓ **Ask the librarian** | *JFQA*, Tier 1. Not covered by the original enquiry — a one-line follow-up |
| **Springer Nature** | ⏸ **Not yet** | Weakest for our domains: *Finance and Stochastics* and *Annals of OR* are Tier 2 and peripheral to what release 2 needs. The free metadata key is sufficient. ⚠ Note *Nature* itself is Springer Nature — and per the venue policy, that is not where this project's literature lives |
| **WRDS** | ✅ **Yes — but it is not a literature database** | ★ It is what turns *"read the paper"* into *"replicate the paper."* Different axis, high value, and the one item here that touches actual analysis rather than reading |

## Answer, in one line

**No — not all four, and not only those four.** Take **Wiley + Elsevier + OUP** for papers,
add **WRDS** for data, **defer Springer Nature**, and **ask about Cambridge**. Requesting a
token you will not use has a cost: each carries an agreement to honour, and Mode B obligations
attach the moment you hold one.

---

# 3 · What this changes in `L4-6`

| § | Change |
|---|---|
| §6.3(b) | State that arXiv `q-fin` coverage is a **channel**, not a quality tier — admission is governed by the venue policy |
| §6.3(c) | ★ Add **OUP** and **Cambridge** rows; move **WRDS** out of the publisher table into its own row labelled *data, not literature*; downgrade **Springer Nature** to *deferred* |
| §6.3(a) | Record the OpenAlex-primary / S2-secondary / Crossref-authority split and the **DOI-only keying** rule |
| §6.7 | Add the snapshot rule — a search result set is only reproducible if captured when run |
| §6.10 | Add: ask the librarian about **Cambridge University Press** |

---

## Sources

- [Reference coverage analysis of OpenAlex compared to Web of Science and Scopus](https://arxiv.org/abs/2401.16359) — *Scientometrics* (2025), [published version](https://link.springer.com/article/10.1007/s11192-025-05293-3)
- [Is Semantic Scholar suitable for enriching references in OpenAlex?](https://subugoe.github.io/scholcomm_analytics/posts/s2_reference_analysis/s2_reference_analysis.html) — the per-publisher reference-count comparison
- [Analysis of the publication and document types in OpenAlex, Web of Science, Scopus, PubMed and Semantic Scholar](https://direct.mit.edu/qss/article/doi/10.1162/QSS.a.406/134713/Analysis-of-the-publication-and-document-types-in) — *Quantitative Science Studies*
- [The Semantic Scholar Open Data Platform](https://arxiv.org/html/2301.10140v2)
- [Finance journal rankings: active scholar assessment revisited](https://www.sciencedirect.com/science/article/abs/pii/S0378426619302900) — the JF/JFE/RFS/JFQA quality estimates
- [The Review of Financial Studies](https://academic.oup.com/rfs) (OUP) · [JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/information/about-this-journal) (Cambridge)
