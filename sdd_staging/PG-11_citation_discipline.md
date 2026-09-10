# `PG-11` — draft constitution amendment

> **Destination:** `sdd/specs/constitution.md`, §2 *Platform governance rules*, after `PG-10`.
> **Status:** 🟡 **DRAFT — not approved, not in force.**
> **Drafted:** 2026-09-09 · **Origin:** `docs/lectures/L4-6-retrieval-and-the-literature-loop.html` §6.2
> **Requires:** fund-manager approval. Constitution §5.4 — *breaking a `PG-n` rule ⇒ amend this
> file first, in its own change, with rationale.* An amendment deserves the same care.
>
> ⚠ **Re-check the number at merge time.** `PG-11` was free on 2026-09-09; the other session
> may have claimed it since.

---

## Paste from here

## ★ PG-11 — A method claim carries its source

**A design-tier proposal that adopts, adapts or rejects a quantitative method must record,
for each method it turns on:**

| | Required | Form |
|---|---|---|
| **1** | **The primary source** | DOI or stable identifier. ⚠ Not a survey that cites it, not a textbook, not a blog, and never the model's recollection |
| **2** | **The regime the result was established in** | Market, period, universe, and any cost, turnover or liquidity assumption the original made |
| **3** | **One limiting or dissenting work** | A paper that constrains, disputes, or fails to replicate it. ★ Where a real search locates none, record **"no dissent found"** — never *"undisputed"* |
| **4** | **The venue tier** | Per the venue policy. A Tier-3 source may be cited, but it is marked, and it may not be the *only* support for a method that reaches a spec |

**Scope.** `sdd/design/**` and `docs/lectures/**`.

⚠ **Specs carry no bibliography.** A spec states what must be true; the design note that
graduated into it carries the argument. This preserves the existing separation and is the
reason `PG-11` binds the design tier rather than the spec tier.

**Exempt.** Seat 9 experiment write-ups (`P7`). An experiment reports what *it* measured; it
is not making a claim about the literature. ★ The exemption ends at promotion — the moment an
experiment's method is proposed for production, the proposal is a design-tier proposal and
`PG-11` applies in full.

**Why this is a `PG` and not a style note.**

`PG-5` says *a demonstration must be measured, not merely shown*. `PG-11` is its mirror:
**a method must be sourced, not merely asserted.** `PG-5` governs claims about our system;
`PG-11` governs claims about the literature we borrow from. The failure they prevent is the
same one — a confident assertion that was never checked — arriving from two directions.

The specific hazard is that an LLM produces fluent, textbook-shaped method summaries that are
*approximately* the literature: real method names, plausible framing, and none of the
qualifications, regime limits or failed replications. That output is **memory, not
scholarship**, and it is indistinguishable in tone from the version that did the reading.
An uncited method claim in a design document is the design-tier form of a signal promoted
without a walk-forward — and this project already refuses the latter.

**What breaking it looks like.**

- A design note proposing HRP, CVaR sizing, or ensemble disagreement as an uncertainty proxy,
  with no DOI and no regime.
- A citation to a survey in place of the paper that established the result.
- ⛔ **"This is a well-established technique"** as the whole of the justification — the
  characteristic phrasing of a claim nobody checked.
- Recording *"undisputed"* where the truth is that no search was run.

**Enforcement.** ⚠ **Review-time, by the fund manager — there is no automated gate**, and this
must be stated rather than assumed. A hook could at most check that a design file touching a
method has a References section; it cannot check that the references are real, or read. The
rule works because a reviewer applies it, or it does not work.

**Cost, stated honestly.** Roughly 20–40 minutes per method, most of it in requirement 3.
That is the price, it is not trivial, and it is why the rule is scoped to methods a proposal
*turns on* rather than every method it mentions in passing.

## Paste to here

---

## Notes for the reviewer — not part of the amendment

**Why requirement 3 is the one that matters.** Requirements 1 and 2 are bookkeeping and an
LLM can satisfy them from memory often enough to be dangerous. Requirement 3 cannot be
satisfied without actually searching, because a dissenting paper is not something the model
reliably knows. ★ It is the requirement that forces the tool use — which is the whole point.

**Why "no dissent found" rather than "undisputed."** Absence of located evidence is not
evidence of absence. The two phrasings differ by whether a search happened, and a later
reader needs to know which. It also leaves an honest trail: a search that came up empty is
information, and it is different from a search that was never run.

**The obvious objection, and the answer.** *Is requirement 3 too strong for a genuinely
well-established method — CAPM, Black-Scholes, ordinary least squares?* Even there, dissent
exists and is exactly what you want to know: the CAPM has an enormous anomalies literature,
Black-Scholes has the volatility smile, OLS has its assumption violations. If a real search
finds nothing, "no dissent found" discharges the requirement in one line. The rule does not
demand that dissent exist; it demands that you looked.

**Alternative considered and rejected.** Putting this in the brainstorm template only. Weaker:
templates are edited around, and §5.4 means a `PG` can only be set aside by amending the
constitution in its own change with rationale. That friction is the enforcement.
