# Librarian enquiry — sent, and answered 2026-09-09

> **Companion to** [`L4-6-retrieval-and-the-literature-loop.html`](L4-6-retrieval-and-the-literature-loop.html) §6.4.
> Not SDD material. Governs nothing.
>
> **Purpose.** Obtain *sanctioned* programmatic access to licensed literature — TDM tokens,
> API entitlements — rather than improvising around a proxy. §6.4 explains why the sanctioned
> route is the only one worth taking: at any noticeable volume, the unsanctioned one gets the
> whole institution's IP range blocked by the publisher.
>
> ✅ **Status: closed.** Sent and answered. The reply is transcribed below and has been folded
> into lecture 06 §6.3(c), §6.4 and §6.6. **Outcome: all four publishers confirmed, plus WRDS.**

## Who to send it to

uOttawa Library — the **research support / scholarly communication** team, or the
**business and economics subject librarian** (Telfer). Either will route it. Start at
<https://biblio.uottawa.ca/en> → *Ask us* / *Research support*.

## Before you send

- `[]` Fill the two bracketed slots with your real program name and status. Keep them accurate —
  entitlement and TDM eligibility genuinely depend on them, and a librarian who has to correct
  the record later is a librarian who now has to re-check everything else.
- `[]` If your literature work is supervised, say so and name the supervisor; if it is independent
  study, say that instead. Both are normal; only misstating it causes a problem.
- `[]` Trim any question you don't actually need. A four-question email gets answered; a
  ten-question email gets triaged.

---

## Draft email

**Subject:** Text and data mining access for a graduate literature review — API and TDM options?

Hello,

I'm a master's student at the University of Ottawa in [PROGRAM], and I'm beginning an extensive
literature review in **quantitative finance, financial technology, and the mathematical methods
used in them** — portfolio and risk methodology, statistical evaluation of financial models, and
the machine-learning literature that has grown up around both.

The review covers a large and fast-moving body of work, so part of my methodology is to use
**AI-assisted ("agentic") search tools** to help with discovery and screening: querying scholarly
APIs programmatically, following citation graphs forward and backward to find replications and
critiques, and screening candidate papers before I read them properly myself. Open sources such
as OpenAlex, Crossref, arXiv and Semantic Scholar cover a good deal of this, but a significant
part of the core literature sits in subscription journals — *Journal of Finance*, *Journal of
Financial Economics*, *Review of Financial Studies*, *Quantitative Finance* and similar.

I want to do this **through whatever route the Library sanctions**, rather than improvising, so
I have a few questions:

1. **TDM agreements.** Does uOttawa hold text-and-data-mining agreements with Wiley, Elsevier,
   Oxford University Press, or Taylor & Francis? If so, how does a graduate student request a
   TDM token?

2. **Elsevier developer API.** Is there an institutional entitlement for the ScienceDirect API,
   and what does it require to resolve full text — campus IP, VPN, or an institutional token?

3. **Acceptable use.** What is the sanctioned method for programmatic access to licensed content,
   and what request volumes are considered reasonable? I would rather be told the limit than
   discover it.

4. **WRDS.** Does the University (or Telfer) subscribe to Wharton Research Data Services, and is
   graduate access available? Several papers I want to work through are only really understandable
   alongside the datasets they used.

5. **Alerting.** Is there a current-awareness or alerting service you'd recommend configuring for
   these subject areas, so new work arrives rather than needing to be hunted?

I'm happy to complete any form, agreement or training the Library requires, and to work within
whatever constraints apply. If a short meeting would be easier than email, I'm glad to book one.

Thank you very much for your time.

Best regards,
[NAME]
[PROGRAM], University of Ottawa
[STUDENT NUMBER] · [EMAIL]

---

## The reply — received 2026-09-09

> Transcribed from the Library's response. Licence snippets are quoted from uOttawa's agreements
> with each publisher and are the authoritative wording — the summaries in the lecture are summaries.

**Preamble.** The librarian has queried the **Web of Science API** at scale for a project, but had
not used publisher-specific APIs.

### 1 · TDM agreements — all four publishers confirmed

**Wiley** — Authorized Users accept Wiley's Text and Data Mining Agreement to receive an API token.
<https://www.onlinelibrary.wiley.com/library-info/resources/text-and-datamining>

**Elsevier** — *"Each Member may download and make a copy of the whole or any parts of the Licensed
Materials for the purposes of internal computational analysis, including text and data mining via an
API at https://dev.elsevier.com for the purpose of research for a non-commercial purpose and other
Scholarly and Educational Use solely, provided that:*

- *the copy or parts thereof are accompanied by sufficient acknowledgment, other than where this
  would be impossible for reasons of impracticability or otherwise;*
- *the copy or parts thereof are not distributed to or stored with any third party, including any
  third party service provider, without the prior approval of Publisher;*
- *the copy is stored on the Member's secure server in Canada, at a location to be confirmed between
  parties; and*
- *the results of the computational analysis shall not have the potential to compete with, to
  substitute and/or replicate any other existing Publisher products, services and/or solutions and
  the copies made under this Section shall be deleted promptly after the computational analysis has
  taken place."*

**OUP** — *"Members and Authorized Users may apply automated tools and processes to the Publications
for the purposes of textual analysis and visual mapping of textual and/or statistical relationships
within the context of scholarship, research, and other educational purposes, provided that:*

1. *such copies are made and stored only to the extent necessary for the purposes of such
   computational analysis;*
2. *such copies are not transferred to any other person or used for any other purpose without the
   Publisher's consent;*
3. *such copies are destroyed once they are no longer necessary for the relevant computational
   analysis;*
4. *the Authorized Users acknowledge the use of the Publications if any results of the computational
   analysis are published; and*
5. *the Authorized Users comply with all Publisher usage policies communicated to them or made
   available to them, including without limitation any security measures and conditions of access."*

*"Members and Authorized Users may publish the results of such text and data mining."*
Contact: `data.mining@oup.com`

**Taylor & Francis** — Contact: `support@tandfonline.com`

### 2 · Elsevier ScienceDirect API

Requires an **institutional login as well as an API token**, and ★ **can be used off-campus without
the VPN**. Standard use cases: <https://dev.elsevier.com/sd_api_spec.html> · usage limits:
<https://dev.elsevier.com/api_key_settings.html>. A higher access level may need to be requested
from Elsevier directly to retrieve a lot of full-text articles.

### 3 · Volume limits

⚠ **The publishers do not tell the institution a standard volume limit.** If it is not stated when
API access is granted, ask that publisher individually.

### 4 · WRDS

✅ **uOttawa has access.** <https://uottawa.libguides.com/financelab/access_descriptions>

### 5 · Alerting

- **Scopus alerts** — comprehensive, weekly or monthly. ★ The librarian's own practice: develop a
  *very targeted* search rather than an entire subject area, so the alert is not inundating.
- ⛔ **Google Scholar alerts** — not recommended, for the same reason.
- **Research Rabbit** — finds related new papers through **both keywords and citation networks**.

---

## What came out of it

| Change | Where it landed |
|---|---|
| All four publishers confirmed; Elsevier off-campus without VPN; WRDS available | Lecture 06 §6.3(c) — rows now marked `confirmed` |
| ★ **The two-mode access policy** — Mode A (reading, unrestricted) vs Mode B (TDM API, per-publisher terms) | Lecture 06 §6.4 — **the in-house rule** |
| The project's non-commercial standing, recorded with a review trigger | Lecture 06 §6.4 |
| Tier 2 storage split — durable metadata/notes/OA vs cleared Mode-B working storage | Lecture 06 §6.6 |
| Scopus-alert discipline and Research Rabbit corroborate the citation-graph argument | Lecture 06 §6.7 |

## Follow-through — do each only when a question needs it

- `[]` Accept **Wiley's TDM Agreement** → API token.
- `[]` Request the **Elsevier API token** (institutional login + token; ask for elevated access only
  if retrieving full text at volume).
- `[]` Email `data.mining@oup.com` / `support@tandfonline.com` if OUP or T&F content is needed.
- `[]` Open a **WRDS** account — the one that turns "read the paper" into "replicate the paper."
- `[]` Configure **one narrow Scopus alert**; try **Research Rabbit** before building any Tier 1 tool.
- `[]` Ask each publisher its volume limit at the point access is granted.

⚠ Any token is a credential — **environment variable, never in the repo** (house rule).
