"""Deterministic bundle assembly — RA-3, RA-4, RA-19.

★ **RA-19 is the rule that shapes this module: the bundle is NOT curated by the
layer that judges.** Assembly is mechanical and as-of-driven. *If the judging
layer could choose its evidence, confirmation bias would have a supply chain* —
so nothing here takes a hint, a preference or a relevance score.

⚠ **RA-3 — internal consistency.** One `as_of` for the whole bundle, and no
mixing a fresh price with a stale filing. That is checked, not assumed: a part
whose pin carries a date later than the `as_of` is a look-ahead the hash would
otherwise happily record.
"""

from __future__ import annotations

import json
from datetime import date

from src.fundamental.bundle.models import BundlePart, EvidenceBundle
from src.fundamental.errors import BundleInconsistentError

_UNSET = object()

#: Pin fields that are dates and therefore subject to RA-3's as-of check. A pin
#: absent from here is an identifier (an accession id, a contract version) and
#: carries no time of its own.
_DATED_PINS = ("published_date", "as_of", "filing_date")


def assemble(*, ticker: str, as_of=_UNSET, parts) -> EvidenceBundle:
    """Build the bundle for one `(ticker, as_of)`.

    `as_of` is required and has no default — **DE-6.4's rule, one domain out**.
    A defaulted as-of here would pin the bundle to whenever it happened to be
    assembled, which is the one thing a *pinned* input set must not do.
    """
    if as_of is _UNSET or as_of is None:
        raise BundleInconsistentError(
            "assemble() requires an explicit as_of. A bundle pinned to 'now' is "
            "pinned to nothing — and RA-4's 'same as_of => same hash' has no "
            "meaning if the as_of is whatever the clock said (DE-6.4)"
        )
    if not isinstance(as_of, date):
        raise BundleInconsistentError(f"as_of must be a date, got {type(as_of).__name__}")

    ticker = ticker.upper()                       # DE-7, at the boundary
    parts = tuple(parts)
    _assert_internally_consistent(ticker, as_of, parts)
    return EvidenceBundle(ticker=ticker, as_of=as_of, parts=parts)


def _assert_internally_consistent(ticker: str, as_of: date, parts) -> None:
    """RA-3 — one as_of, and nothing in the bundle knows the future.

    ⚠ **This is INV-1 applied to the input set rather than to a query.** D-07
    guarantees each part was knowable at its own as_of; **only assembly can
    guarantee they were all knowable at the SAME one.**
    """
    for part in parts:
        for field in _DATED_PINS:
            value = part.pins.get(field)
            if value is None:
                continue
            when = value if isinstance(value, date) else date.fromisoformat(str(value)[:10])
            if when > as_of:
                raise BundleInconsistentError(
                    f"{ticker}: a {part.kind} part is pinned to {field}={when}, after "
                    f"the bundle's as_of {as_of}. A bundle mixing a fresh input with "
                    f"a stale one is not pinned to a date — it is pinned to two "
                    f"(RA-3, INV-1)"
                )


def filing(accession_id: str, text: str) -> BundlePart:
    """A filing, pinned by `accession_id` — immutable once published (CT-7.4)."""
    return BundlePart("filing", {"accession_id": accession_id}, text)


def news(source: str, external_id: str, published_date: date, text: str) -> BundlePart:
    """A news item, pinned by `(source, external_id)` + its publication date.

    ⚠ The publication date is part of the pin, not metadata: D-07 **DE-26** says
    news is captured forward and never re-fetched for history, so a re-fetch that
    returned a different body under the same id is a fact worth the hash noticing.
    """
    return BundlePart("news",
                      {"source": source, "external_id": external_id,
                       "published_date": published_date.isoformat()},
                      text)


def computed(contract_name: str, contract_version: int, text: str) -> BundlePart:
    """D-02 output, pinned by the **contract**, not by the values.

    ★ That is the point of D-02's FeatureContract: *"an analysis that differs
    from yesterday's may differ because D-02 changed a formula"* — pinning the
    contract version is what makes that distinguishable from model variance.
    """
    return BundlePart("computed",
                      {"contract_name": contract_name, "contract_version": int(contract_version)},
                      text)


def profile(as_of: date, text: str) -> BundlePart:
    """Company profile and sector. ⚠ Class-B data (D-07 §5A.4) — it has no
    publication axis of its own, so the `as_of` IS the pin."""
    return BundlePart("profile", {"as_of": as_of.isoformat()}, text)


def prior_thesis(thesis_version: int, text: str) -> BundlePart:
    """★ **Invalidation only** (RA-39). Fresh authoring never sees the prior verdict.

    ⚠ RA-18's exception, and it is deliberate: *re-deciding and re-checking are
    different tasks.* The part kind exists so that a fresh-authoring bundle
    containing one is a visible defect rather than an invisible anchor.
    """
    return BundlePart("prior_thesis", {"thesis_version": int(thesis_version)}, text)


def observables(fields, *, contract_name: str = "observables",
                contract_version: int = 1) -> BundlePart:
    """★★ The list **J-15 names and nothing supplied.**

    ⚠ *Found 2026-08-26 on the first live authoring run:* J-15 instructs the
    model to *"name the specific metric or field the check reads, **choosing
    from the supplied list of available observables**"* — and the payload
    carried no such list. The model wrote perfectly good prose (*"gross margin
    below 55% for two consecutive quarters"*) naming **no field at all**, every
    falsifier failed RA-35's observable test, and the thesis raised
    `NoFalsifierError`.

    ★ **It goes in the BUNDLE, not beside it.** RA-1 says every call takes an
    `EvidenceBundle` **and nothing else**, so a second payload key would be the
    ambient context RA-12 refuses — and the observable set is evidence about
    what this system can check, which is exactly what a bundle carries.
    """
    listed = ", ".join(sorted(fields))
    return BundlePart(
        "observables", {"contract_name": contract_name,
                        "contract_version": contract_version},
        f"AVAILABLE OBSERVABLES — a falsifier may name only these fields:\n"
        f"{listed}")


def sector_file(file) -> BundlePart:
    """★ RA-102 / AC-1.71 — the sector file as a pinned bundle part.

    ⚠ **It is shared across every thesis in the industry, so a defect in it is a
    correlated defect by construction** — and **RM-16** is the instrument that
    would see it. That is also why B4.7 lands *after* the monitors (BS-29).

    The content is the file's records rendered in their one permitted order
    (RA-99/RA-141); the pins are `industry · schema_version · file_version`, so
    a re-ingest that changes any record changes `bundle_hash`.
    """
    lines = [f"{r.date.isoformat()}  {r.kind}  {r.subject}  "
             f"{r.prior_status + ' -> ' if r.prior_status else ''}{r.status}  "
             f"[{r.source_id}] {r.quote}"
             for r in file.records]
    if file.omissions:
        lines.append("")
        lines.extend(f"OMITTED  {o.source_id}: {o.reason}" for o in file.omissions)
    return BundlePart("sector_file", file.pin(), "\n".join(lines))


def extractions(verified_pass, *, prompt_versions: dict, run_id: str) -> tuple[BundlePart, ...]:
    """★★★ `DX-85`ⓒ — a VERIFIED extraction pass as bundle parts, one per E-block.

    ⚠⚠ **Only a pass X-01 has checked may enter.** `run_extraction` returns an
    `ExtractionPass` only after `x01_verify_extraction` ran and did not abort, and
    its report counts every FOUND item. ★ That count is asserted here, so a pass
    assembled by hand from unverified items — the shape `RA-66` forbids, *"an
    item counts as extracted only if X-01 passed"* — refuses rather than handing
    a rubric evidence nobody checked.

    ★ `RA-19`: mechanical. Every result becomes a part, `not_found` items
    included in the content (where the model looked is evidence of absence), and
    nothing is filtered by relevance to the judgement about to read it.
    """
    results = tuple(verified_pass.results)
    found = sum(1 for r in results for i in r.items if i.status == "found")
    if verified_pass.report.checked != found:
        raise BundleInconsistentError(
            f"extraction pass for run {run_id}: X-01 checked "
            f"{verified_pass.report.checked} item(s) but the results carry {found} "
            f"found item(s). Only verified evidence may enter a bundle (RA-66)")
    parts = []
    for r in results:
        if r.block_id not in prompt_versions:
            raise BundleInconsistentError(
                f"no prompt_version given for {r.block_id} — an extraction part "
                f"that cannot say which prompt produced it is unpinned (RA-2, RA-13)")
        parts.append(BundlePart(
            "extraction",
            {"block_id": r.block_id, "prompt_version": prompt_versions[r.block_id],
             "source_bundle_hash": r.bundle_hash, "run_id": run_id,
             "evidence_ids": sorted(r.evidence_ids),
             # ★ `DX-99` — every id the block explicitly returned, found or not.
             "searched_ids": sorted({i.evidence_id for i in r.items})},
            json.dumps(r.to_json_obj(), sort_keys=True, ensure_ascii=False, indent=1)))
    return tuple(parts)
