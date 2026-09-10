# `docs/lectures/` — study material

> **Not SDD material. Governs nothing.** These are teaching documents written to
> understand the mathematics, design patterns and architecture rules behind the
> platform *as a scientist rather than a coder*. They carry academic citations by
> design. Nothing here binds an implementation — `sdd/specs/` does that.

Open the `.html` files in a browser.

| File | Covers | Feeds |
|---|---|---|
| [`L1-3-ports-debate-evidence.html`](L1-3-ports-debate-evidence.html) | **1** Plugin architecture — ports, adapters, registries, the substitution contract · **2** Interactive agents — config influence, deliberation, orchestration frameworks · **3** Explainable AI — attribution, evidence binding, counterfactuals, calibration | `F1` · `F2` · `F6a` · `F6b` · `F7a` · `F7b` · `F4` · `F5` |
| [`L4-6-retrieval-and-the-literature-loop.html`](L4-6-retrieval-and-the-literature-loop.html) | **4** Retrieval-augmented generation — the four stages, where each fails, classic vs agentic retrieval, the evaluation vocabulary · **5** The RAG this project already specified — `C3` as a faithfulness contract, span-level citation, ⚠ the corpus-boundary trap in the analyst firewall · **6** The literature loop — the citation rule, the scholarly-API directory, sanctioned institutional access, the tier ladder, and why not to chunk | `F4` · `F5` · `F9` · `sdd/design/_templates/` |

## Convention

- **Citations belong here**, not in specs. A spec states what must be true; it does
  not argue from literature. The exception is a brainstorm or design note that is
  genuinely *studying* a method — there, cite properly.
- Lectures may be revised. They are not append-only and carry no decision authority;
  a decision that comes out of one is recorded in `sdd/design/rel<N>_brainstorm.md`.
- ⚠ Where a lecture and a spec disagree, **the spec wins** — and the lecture is stale.

## Companion documents

Not lectures, but filed here because a lecture depends on them.

| File | Purpose |
|---|---|
| [`L6-librarian-enquiry.md`](L6-librarian-enquiry.md) | Enquiry to the university library — **sent and answered 2026-09-09**. Carries the verbatim licence snippets for Wiley, Elsevier, OUP and T&F, plus the WRDS and alerting answers. Source of the access policy in lecture 06 §6.4. |
- **[L7 — EDGAR extraction, as built](L7-edgar-extraction-as-built.md)** — the code path, the prompt, ★★ *why this is not just an FMP call*, how filings 1 and 2 were run, and where it is stuck. Written after 24 live calls ($15.31).
