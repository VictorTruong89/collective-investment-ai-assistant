# Librarian enquiry — draft

> **Companion to** [`L4-6-retrieval-and-the-literature-loop.html`](L4-6-retrieval-and-the-literature-loop.html) §6.4.
> Not SDD material. Governs nothing.
>
> **Purpose.** Obtain *sanctioned* programmatic access to licensed literature — TDM tokens,
> API entitlements — rather than improvising around a proxy. §6.4 explains why the sanctioned
> route is the only one worth taking: at any noticeable volume, the unsanctioned one gets the
> whole institution's IP range blocked by the publisher.

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

## What to do with the answers

Record them in the resource table at §6.3(c) of the lecture, and mark the JSTOR/Constellate and
Semantic Scholar rate-limit status notes as confirmed or corrected. If a TDM token is granted,
it is a credential — ⚠ **environment variable, never in the repo** (house rule).
