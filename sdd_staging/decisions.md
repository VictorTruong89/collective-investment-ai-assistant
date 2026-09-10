# Decisions log entries — ready to paste

> **Destination:** `sdd/design/rel<N>_brainstorm.md` → *Decisions log* (append-only).
> **Drafted:** 2026-09-09. Renumber `S<k>` to the actual session number at merge time.
> ⚠ The Decisions-log convention: *"at release close, anything here that still binds must be
> promoted into a spec, a constitution amendment, or vision.md — otherwise it freezes."*
> **D-4 below is the promotion path for D-1.**

## Paste from here

- 2026-09-09 (S<k>): **The research-method layer gets no spec, and that is deliberate.** Constitution §5.5 exempts research/experiment tooling from the spec requirement (`P7`); the literature loop produces no output under `src/`, holds no seat, and nothing anyone trades on flows from it. An `F<n>` ID would claim a permanent spec number for something with no ACs and no governed globs. — *Rationale: `L4-6` §6.8. Rejected alternative: allocating `F10` to it, which would have required inventing acceptance criteria for a dev-time tool in order to satisfy a process that does not apply to it.*

- 2026-09-09 (S<k>): **Literature access follows a two-mode policy.** Mode A (reading through the Library, retention in a reference manager) is unrestricted across every licensed database. Mode B (publisher TDM APIs) is entered per publisher, on that publisher's terms, with harvested full text treated as working storage. — *Rationale: the TDM clauses the Library quoted attach to bulk mining, not to reading. Recorded in `L4-6` §6.4 with the project's non-commercial standing and its review trigger.*

- 2026-09-09 (S<k>): **Take Wiley + Elsevier + OUP for papers; add WRDS for data; defer Springer Nature; ask about Cambridge.** — *Rationale: `sdd_staging/source_evaluation.md` §2. Two of the top four finance journals (RFS at OUP, JFQA at Cambridge) were not reachable through the four databases originally discussed. Springer Nature carries only Tier-2 peripheral titles for our domains. ⚠ Rejected: requesting all available tokens — each carries an agreement to honour, and Mode B obligations attach the moment one is held.*

- 2026-09-09 (S<k>): **OpenAlex primary, Semantic Scholar secondary, Crossref as identity authority; records keyed on DOI only.** — *Rationale: OpenAlex leads reference coverage for Elsevier by +12.6M references, which is where our core journals live; Semantic Scholar's citation contexts are unique and are the dissent-finding mechanism `PG-11` req. 3 depends on. Cross-database author-name agreement is 29–39% while DOI agreement is 100%, so DOI is the only safe key.*

- 2026-09-09 (S<k>): **Venue whitelist adopted, not a "top journals only" filter.** The fund manager's stated preference — willing to miss a few good papers rather than study weak ones — is adopted as precision-over-recall. ⚠ Two refinements were required: *Science*/*Nature* are the wrong anchor for these domains and would return an almost empty set; and a journals-only rule would exclude the ML canon, whose premier venues are NeurIPS, ICML and ICLR. Working papers (NBER, SSRN, arXiv) are admitted when an author holds Tier-1 publications in the same area. — *Recorded in `sdd_staging/venue_policy.md`.*

- 2026-09-09 (S<k>): **`PG-11` drafted — a method claim carries its source.** Design-tier proposals must record primary source (DOI), the regime the result was established in, one limiting or dissenting work (or "no dissent found"), and the venue tier. Specs continue to carry no bibliography. Seat 9 experiment write-ups are exempt until promotion. — *Status: 🟡 draft in `sdd_staging/PG-11_citation_discipline.md`, awaiting fund-manager approval. Rejected alternative: the brainstorm template alone — templates get edited around, whereas §5.4 makes a `PG` cost a constitution amendment to set aside.*

- 2026-09-09 (S<k>): **No code is planned for this layer.** Phases A–E are markdown only. The one file ever contemplated, `tools/litsearch.py` (cross-source DOI dedup + result cache, ~200 lines), is gated by the `L4-6` §6.6 stop rule: build tier *n*+1 only when a *named* search that tier *n* could not perform has actually been wanted. ⚠ Tier 0 has not yet been run once.

## Paste to here
