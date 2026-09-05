"""F3 `CT-3.2` — resolve what happened to a symbol. `MS-6.1`.

⚠⚠ **`AC-3.1`: search precedes classification, always.** The function refuses to
classify from zero evidence rather than producing a fluent guess — `PG-3`'s whole
justification is that *the answer is on the internet*, so an answer that did not
come from there is not the thing this agent exists to produce.

★ `D4` — **F3 writes the finding and never acts on it.** The universe rule reads
it. A resolver that also removed a name would be deciding, and an agent that acts
is one whose mistakes are executed rather than merely wrong.

★ `D1` — search runs through the **LLM gateway** (`ST-5`), so budget, `model_id`,
cost and the `F2` `ExternalCall` record all come for free.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from src.data_engine.corporate_actions.models import (
    Confidence,
    Evidence,
    Finding,
    Outcome,
)


class SearchNotRun(Exception):
    """`AC-3.1` — ⚠ classification was attempted before any search."""


def corroboration_of(sources: Sequence[Evidence]) -> Confidence:
    """`AC-3.2` — one source is a lead, two independent ones are a finding."""
    if not sources:
        return "undetermined"
    return "corroborated" if len({e.url for e in sources}) >= 2 else "single_source"


def classify(ticker: str, *, search: Callable[[str], Sequence[Evidence]],
             interpret: Callable[[str, Sequence[Evidence]], dict],
             vendor_claim: str | None = None,
             attempts: int = 1) -> tuple[Finding, ...]:
    """Search, then interpret. Returns **one finding per side** (`AC-3.3`)."""
    sources = tuple(search(ticker))
    if not sources:
        # ⚠ AC-3.6 — `undetermined` is EMITTED, never guessed around.
        return (Finding(ticker=ticker, outcome="undetermined",
                        confidence="undetermined", attempts=attempts),)

    verdict = interpret(ticker, sources)
    if verdict.get("outcome") is None:
        raise SearchNotRun(
            f"{ticker}: interpret() returned no outcome — a classifier that "
            "cannot say what it concluded has not concluded (P5)")

    conf = corroboration_of(sources)
    outcome: Outcome = verdict["outcome"]

    # ⚠ AC-3.9 — a vendor's delisting event is EVIDENCE, never the verdict.
    # ★ AC-3.5 — a name that stopped printing but still trades under a new symbol
    #   was RENAMED. Calling that a delisting deletes a live holding.
    if vendor_claim == "delisted" and outcome == "ticker_change":
        pass  # the search wins; the vendor claim is recorded in `sources`

    if conf == "single_source" and outcome != "undetermined":
        # AC-3.2 — one source is not enough to classify.
        return (Finding(ticker=ticker, outcome="undetermined", sources=sources,
                        confidence="single_source", attempts=attempts,
                        company=verdict.get("company", "")),)

    base = dict(sources=sources, confidence=conf, attempts=attempts,
                effective_date=verdict.get("effective_date"),
                company=verdict.get("company", ""),
                surviving_cik=verdict.get("surviving_cik"),
                provenance=verdict.get("provenance"),
                trace_ref=verdict.get("trace_ref"))

    if outcome == "merger_of_equals" and verdict.get("other_side"):
        # ★ AC-3.3 — a combination has TWO sides, and both are recorded.
        other = verdict["other_side"]
        return (
            Finding(ticker=ticker, outcome=outcome, retired_side=False,
                    successor_symbol=verdict.get("successor_symbol"), **base),
            Finding(ticker=other, outcome=outcome, retired_side=True,
                    successor_symbol=verdict.get("successor_symbol"),
                    series_contaminated_from=verdict.get("contaminated_from"), **base),
        )

    return (Finding(ticker=ticker, outcome=outcome,
                    successor_symbol=verdict.get("successor_symbol"),
                    retired_side=bool(verdict.get("retired_side")),
                    series_contaminated_from=verdict.get("contaminated_from"),
                    **base),)
