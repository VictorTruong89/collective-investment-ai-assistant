# Venue policy — the source list, and the method behind it

> **Destination:** `.claude/skills/lit-search/references/venues.md`. Cited by `PG-11` req. 4.
> **Fields covered:** quant · finance · macroeconomics · applied mathematics *(in finance)* ·
> applied AI/ML *(in finance)*.
> **Built:** 2026-09-09 from published expert rankings, not from recollection. Sources at the end.

## The preference

> *"Focus only on the top-tier sources. I am willing to miss a few good papers rather than
> review and study poor papers from mediocre journals and conferences."*

★ **Adopted.** Reading time is the binding constraint, not paper availability. A weak paper
costs more than the one it displaced, because a plausible wrong method is harder to unlearn
than no method at all.

---

# 1 · The ranking methodology

Recorded so the list can be **re-derived and argued with**, rather than trusted.

## Criteria, in priority order

| # | Criterion | How it is applied |
|---|---|---|
| **1** | ★ **Convergence across independent expert rankings** | A venue rated top by **≥3** of: ABS/AJG 4\*, ABDC A\*, FT50, VHB A+, CNRS 1\*, RePEc top-20 → **Tier 1**. Rated top by only one → treat as Tier 2 and look for why the others disagree |
| **2** | ★★ **Field-specific, never generic** | A venue's tier **depends on the question being asked**. *Mathematical Finance* is Q1 in applied mathematics and only mid-tier by finance-scholar assessment — both true. Tier is recorded **per field**, and §2 does exactly that |
| **3** | **Selectivity** | Acceptance rate and annual volume. QJE ≈ **3%**; JPE and RES ≈ **5%**; AER and Econometrica ≈ **8%**. JF/JFE/RFS publish **87–111 papers a year** against 386–1,528 for mid-tier finance journals. ★ The scarcity *is* the signal |
| **4** | **Refereeing rigour** | Double-blind review, multi-round revise-and-resubmit as the norm rather than the exception |
| **5** | ★★ **Replication policy** — *project-specific, weighted heavily* | Does the journal **mandate a data and code archive**? AER, Econometrica, Management Science, JF and RFS do. For a project that *implements* the methods it reads, one paper with a working archive is worth several without one. ⚠ No general ranking uses this criterion; we do, because our use is unusual |
| **6** | **Field fit** | A world-leading journal in the wrong field contributes nothing. Applied last, as a filter |

## ⛔ Criteria explicitly rejected

| Rejected | Why |
|---|---|
| **Journal impact factor** | Meaningless for conferences (they have none, and they are ML's top venues); low for good quant journals — *Quantitative Finance* sits near **1.7**; and it is the single metric predatory publishers game hardest |
| **h-index, CiteScore, Google Scholar metrics** | Volume proxies. They reward large fields and long-lived journals, not quality |
| **"Q1" with no category named** | Almost every serious journal is Q1 in *something*. The category is the whole content of the claim |
| **Raw citation count** | ⚠ A heavily-cited Tier-3 paper is usually cited by other Tier-3 papers. Use citations only *within* a tier |

---

# 2 · The list

## Tier 1 — admit on venue alone (16)

| Field | Venue | Publisher | Note |
|---|---|---|---|
| **Finance** | ★ *Journal of Finance* | Wiley | Quality est. 4.83 — the field's first journal |
| **Finance** | ★ *Journal of Financial Economics* | Elsevier | 4.76 |
| **Finance** | ★ *Review of Financial Studies* | Oxford UP | 4.65 · ★ most ML-asset-pricing work lands here |
| **Finance** | *Journal of Financial and Quantitative Analysis* | Cambridge UP | 4.61 |
| **Finance** | *Review of Finance* | Oxford UP | European flagship |
| **Finance / quant / ML** | ★ *Management Science* | INFORMS | ★ Crosses all our fields; mandates code archive |
| **Macro / econ** | *American Economic Review* | AEA | Top-5 · ~8% acceptance · code archive |
| **Macro / econ** | *Econometrica* | Wiley (ES) | Top-5 · ~8% · code archive |
| **Macro / econ** | *Quarterly Journal of Economics* | Oxford UP | Top-5 · ★ ~3% — the most selective |
| **Macro / econ** | *Journal of Political Economy* | Chicago | Top-5 · ~5% |
| **Macro / econ** | *Review of Economic Studies* | Oxford UP | Top-5 · ~5% |
| **Econometrics** | *Journal of Econometrics* | Elsevier | The methods journal for our estimation questions |
| **ML** | ★ **NeurIPS** | open access | ★★ Conference — outranks nearly every ML journal |
| **ML** | ★ **ICML** | open access | ★★ Conference |
| **ML** | ★ **ICLR** | open access | ★★ Conference · open review visible |
| **ML** | *JMLR* | open access | The field's premier journal |

## Tier 2 — admit, and note the venue when citing (15)

| Field | Venue | Publisher |
|---|---|---|
| Finance applied | *Journal of Banking & Finance* · *Journal of Empirical Finance* · *Journal of Financial Markets* | Elsevier |
| Finance applied | *Review of Asset Pricing Studies* | Oxford UP |
| Macro specialist | *Journal of Monetary Economics* | Elsevier |
| Macro specialist | *AEJ: Macroeconomics* | AEA |
| Macro / computational | ★ *Journal of Economic Dynamics and Control* | Elsevier |
| **Applied maths in finance** | ★ *Mathematical Finance* | Wiley |
| **Applied maths in finance** | ★ *Finance and Stochastics* | Springer |
| **Applied maths in finance** | *SIAM Journal on Financial Mathematics* | SIAM |
| Quant | *Quantitative Finance* | Taylor & Francis |
| Practitioner | ★ *Financial Analysts Journal* | T&F / CFA Institute |
| Practitioner | *Journal of Portfolio Management* · *Journal of Financial Data Science* | PMR |
| Statistics | *Annals of Statistics* · *JASA* · *JRSS-B* · *Biometrika* | various |
| ML second rank | AISTATS · UAI · AAAI · KDD | open / ACM |

> ⚠ **On the three applied-maths journals.** They are **Tier 1 for a mathematical question**
> (existence, convergence, an estimator's properties) and **Tier 2 for an empirical claim**
> about markets. This is criterion 2 in action: rate them against the question you are asking.

## Working-paper series — channels, judged by author (3)

**NBER** · **SSRN** (Financial Economics Network) · **arXiv** `q-fin` / `cs.LG` / `stat.ML`

★ **Admission rule:** cite when **at least one author holds Tier-1 publications in the same
area**, or the paper is already well cited. Not a quality tier — a *distribution channel*,
and often carrying the current version of a result whose journal version is 18–30 months away.

## ⛔ Excluded

Predatory publishers · unrefereed preprints by unpublished authors · vendor white papers ·
blogs and Medium · LLM-generated summaries.

⚠ **And the specific trap for our fields — see §4.**

---

# 3 · How many sources is enough?

★ **The mistake to avoid is treating this as one list.** It is two, used differently, and they
want different sizes.

| | **Scan list** | **Filter list** |
|---|---|---|
| **Use** | Browse tables of contents; skim everything published | Admit or reject what a *topical search* already returned |
| **Right size** | ★ **5–6 venues** | ★ **~34 venues** (16 + 15 + 3 above) |
| **Why that size** | You genuinely read these. More than six and it silently stops happening | Search has already narrowed by topic, so a longer list costs nothing and prevents false rejections |

**The recommended scan list (6):** *Journal of Finance* · *Journal of Financial Economics* ·
*Review of Financial Studies* · *Management Science* · **NBER** new working papers ·
**arXiv `q-fin`** new listings.

## Why ~34 and not 15 or 60

- **Floor.** Five fields at a realistic minimum of 4 venues each is 20 before overlap. Fewer
  than ~25 and a field goes uncovered — most likely macro or applied maths, since finance
  dominates the overlap.
- **Ceiling.** Past ~40 the list stops filtering and becomes an inventory of respectable
  academia. The marginal venue contributes papers you will never reach.
- ★ **The real constraint is reading capacity, not list length.** At ~30 papers read properly
  per release and ~2 releases a year, the ceiling is **~60 papers a year**. A whitelist of 34
  venues emits several thousand papers a year; a topical search cuts that to tens. That is the
  right ratio — roughly **20× more screened than read**, so screening has work to do without
  being hopeless.
- **Overlap does the rest.** The five fields are not disjoint: JF, JFE, RFS and *Management
  Science* serve four of them at once. The union is far smaller than the sum, which is why 34
  covers five fields comfortably.

---

# 4 · ⚠ The trap in applied ML for finance — where this policy pays most

This is the one field where a venue filter is not fastidiousness but **load-bearing**.

The ML-in-finance literature has a documented replication problem. ⚠ **The numbers below are
the primary sources; an earlier draft of this file carried a "90% of academic strategies fail
with real capital" figure that does not survive tracing — see the note at the end of this
section.**

| Study | Venue | What was measured | Result |
|---|---|---|---|
| **Hou, Xue & Zhang (2020)**, *Replicating Anomalies* | ★ RFS 33(5) | 452 published anomalies re-tested with NYSE breakpoints and value-weighted returns, so microcaps cannot drive the result | **65% fail to clear \|t\| ≥ 1.96.** At the multiple-testing hurdle \|t\| ≥ 2.78, **82.1% fail**. 96% of the trading-frictions category fails. ★ Even the survivors have *"much smaller"* economic magnitudes than originally reported |
| **McLean & Pontiff (2016)**, *Does Academic Research Destroy Stock Return Predictability?* | ★ *Journal of Finance* | 97 published predictors, tracked across three windows: in-sample, post-sample/pre-publication, post-publication | Returns **26% lower out-of-sample** (an upper bound on data-mining effects) and **58% lower post-publication** — so **≈32% of the decline is attributable to publication-informed trading**. ★★ **58% lower is not zero: ~42% of the premium persists** |
| **Harvey, Liu & Zhu (2016)**, *…and the Cross-Section of Expected Returns* | ★ RFS 29(1) | The multiple-testing problem across the factor literature | Argues the conventional \|t\| > 2.0 hurdle is far too low given how many factors have been tried; proposes **\|t\| > 3.0**. Implies a large share of published factors are false discoveries |

★ **"Fail" in these studies means *statistically indistinguishable from zero on replication*, or
*decayed*. It does not mean "lost money," and none of them measures live capital.** Keep the
distinction — it is the difference between a claim you can cite and a claim you cannot.

**The mechanisms are well identified and recur:** backtest overfitting through in-sample
parameter search, lookahead bias, and **data snooping** — selecting the best backtest from many
candidates is a multiple-testing problem that inflates significance, and most papers make no
correction for it.

⛔ **The specific venues to refuse**, high-volume outlets carrying large quantities of
"we applied an LSTM to stock prices" with none of the above controlled:
*Expert Systems with Applications* · *Neurocomputing* · *IEEE Access* · most "international
journal of ..." finance-and-AI titles · the long tail of AI-in-finance conference proceedings.

★★ **Where the good ML-in-finance work actually appears:** in the **finance** Tier 1, not the ML
one. *Review of Financial Studies* and *Journal of Finance* publish the machine-learning asset
pricing literature, refereed by people who ask about transaction costs and out-of-sample design.
**Search finance venues for ML methods, not ML venues for finance applications.**

> ★ **This is the project's own instinct, arriving from outside.** The record shows a
> walk-forward IC of 0.0203 at *t* = 1.42 with promotion declined — *"a signal that passed
> would not have been shown to work."* Hou-Xue-Zhang's 82.1% failure rate at *t* = 2.78 is the
> aggregate of everyone who did not decline. **The venue filter is that same refusal, applied
> to what we read instead of what we build.**

## ⚠ A worked example of `PG-11` req. 1 — and a mistake this file made

An earlier draft of this section asserted: *"institutional investors report that over 90% of
academic strategies fail when implemented with real capital."* Traced:

1. It appears in the **introduction of an arXiv preprint**, not a refereed source.
2. That preprint attributes it to **Harvey, Liu & Zhu (2016)**.
3. ⛔ **Harvey, Liu & Zhu states no such figure.** It is a paper about multiple-testing hurdles
   in the factor literature. It says nothing about institutional implementation or live capital.
4. The preprint presents it as *"institutional investors report"* — an unattributed appeal to
   practitioner hearsay, carrying a citation that does not support the number.

★ **This is exactly what `PG-11` req. 1 exists to catch** — *"not a survey that cites it, not a
textbook, not a blog, and never the model's recollection."* The number was plausible, it was
directionally consistent with the real literature, and it was **not a fact**. A plausible number
with a citation attached is more dangerous than no number, because the citation stops the
checking. **Trace to the primary source or do not use the figure.**

---

# 5 · How to apply this during a search

1. **Screen on venue before reading anything.** OpenAlex returns host venue and ISSN on every
   record — filter first, read second.
2. **Rank by tier → selectivity → recency.** ⚠ Never by citation count across tiers.
3. **Rate the venue against the question** (criterion 2), not in the abstract.
4. **Prefer a paper with a data/code archive** where one exists (criterion 5).
5. **Journal version for the result; working paper for what the referees cut.**
6. **Report the tier in every shortlist** — the fund manager should never have to look it up.

---

## Sources

- [Academic Journal Guide 2024](https://charteredabs.org/academic-journal-guide/academic-journal-guide-2024) — Chartered ABS · [ABDC Journal Quality List](https://abdc.edu.au/abdc-journal-quality-list/)
- [Finance journal rankings: active scholar assessment revisited](https://www.sciencedirect.com/science/article/abs/pii/S0378426619302900) — the JF/JFE/RFS/JFQA quality estimates
- [Nine facts about top journals in economics](https://cepr.org/voxeu/columns/nine-facts-about-top-journals-economics) (Card & DellaVigna) · [The tyranny of the top five](https://www.aeaweb.org/research/charts/publishing-promotion-economics-top-five) — acceptance rates
- [The Revenue of Finance Journals: Networks, Pricing Power, and Publication Volume](https://arxiv.org/pdf/2508.14301) — annual volumes and per-document citations
- ★ **Primary sources for §4** — Hou, Xue & Zhang, *Replicating Anomalies*, [RFS 33(5) 2020](https://academic.oup.com/rfs/article-abstract/33/5/2019/5236964) ([NBER WP](https://www.nber.org/system/files/working_papers/w23394/w23394.pdf)) · McLean & Pontiff, *Does Academic Research Destroy Stock Return Predictability?*, [Journal of Finance 2016](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365) ([PDF](https://www.hec.ca/finance/Fichier/McLean.pdf)) · Harvey, Liu & Zhu, *…and the Cross-Section of Expected Returns*, RFS 29(1) 2016
- [Backtest overfitting in the machine learning era](https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110) · [Deep learning in the stock market — a systematic survey of practice and backtesting](https://pmc.ncbi.nlm.nih.gov/articles/PMC9245389/)
- [Mathematical Finance](https://www.scimagojr.com/journalsearch.php?q=18173&tip=sid) · [Finance and Stochastics](https://www.scimagojr.com/journalsearch.php?q=15495&tip=sid&clean=0) · [SIAM J. Financial Mathematics](https://www.scimagojr.com/journalsearch.php?q=21100223304&tip=sid&clean=0) — SJR category placements
