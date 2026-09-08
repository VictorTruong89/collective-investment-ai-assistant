"""★★ `ticker + as_of` → a **probed** thesis. D-01's one entry point for WF-1.

The pieces all existed and nothing joined them: `bundle_for` assembles the
evidence, `author_once` performs one authoring pass, `author_thesis` runs k of
them and measures RM-1. ⚠ Between them sat a scratch script, which is why
`RunContext.probed_thesis` was `None` in every unattended run.

★ **RA-105 — D-01 sequences its own work.** A caller may invoke this; it may not
reorder, skip or re-enter a step. *A caller able to skip Stage A has removed
RA-14*, so the composition lives here rather than in the orchestrator.
"""

from __future__ import annotations

from datetime import date

#: RM-1 needs k ≥ 3 before an agreement figure means anything, and **AC-1.8
#: makes k < 3 unable to be the actionable pick** — so this is the floor, not a
#: default worth tuning down.
K_RUNS = 3

#: How far out a falsifier may be asked to resolve. ⚠ A deadline inside the
#: bundle's own window would be answerable before the thesis is even filed.
DEFAULT_HORIZON_DAYS = 210


def author_for(ticker: str, *, as_of: date, engine, gateway=None, panel=None,
               contract=None, k: int = K_RUNS, deadline: date | None = None,
               run_id: str | None = None, cache_root=None, reauthor: bool = False):
    """Assemble, author k times, and return the `ProbedThesis`.

    `gateway` is an `AnalysisGateway`, or `None` to build D-01's own. ★★ **ST-5
    — D-01 is the only domain permitted to import the LLM gateway**, so a caller
    outside D-01 must pass `None`: *a shim that can build a gateway can make a
    call*, and AC-1.38's grep is the only thing keeping that untrue.
    """
    from datetime import timedelta

    from src.fundamental.bundle.for_ticker import bundle_for, observable_fields
    from src.fundamental.thesis.author import AuthoringRun
    from src.fundamental.thesis.probe import author_thesis
    from src.fundamental.thesis.run import author_once

    ticker = ticker.upper()
    bundle = bundle_for(ticker, as_of=as_of, engine=engine, panel=panel,
                        contract=contract)

    # ★★ RC-61 — an unchanged bundle reuses its thesis. ⚠ The bundle is built
    #   FIRST and only then looked up: `bundle_hash` is the key, and computing
    #   it is the only way to know whether the evidence moved. Assembly is
    #   cheap; the three Opus passes are the $1.34.
    if cache_root is not None and not reauthor:
        cached = _cached(bundle.bundle_hash, cache_root)
        if cached is not None:
            return cached
    observables = observable_fields(engine, ticker, as_of, contract)
    resolve_by = deadline or (as_of + timedelta(days=DEFAULT_HORIZON_DAYS))
    stem = run_id or f"wf1-{ticker.lower()}-{as_of.isoformat()}"

    from src.fundamental.prompts.call import build_gateway
    gateway = gateway or build_gateway()

    def author(view, index: int):
        return author_once(bundle=view, gateway=gateway,
                           run=AuthoringRun(ticker=ticker, as_of=as_of),
                           index=index, observables=observables,
                           deadline=resolve_by, run_id=f"{stem}-{index}")

    return author_thesis(bundle, author=author, k=k, as_of=as_of)


def _cached(bundle_hash: str, cache_root):
    """A stored thesis for this exact evidence, rehydrated — or `None`.

    ★ **The lookup is invoked by dotted name, not imported.** D-01 depends on
    D-07, D-02 and D-00 (§3) and **not on D-11**; reaching into the record
    directly would add a dependency the spec does not grant, so this resolves
    the same way the orchestrator does (OR-48).

    ⚠ Returns `None` on any failure. A cache that raises turns a saving into an
    outage, and re-authoring is always correct — merely expensive.
    """
    import importlib

    try:
        module = importlib.import_module("src.recording.artifacts.store")
        payload = module.latest_thesis_for(bundle_hash, root=cache_root)
    except Exception:                          # noqa: BLE001 — see the docstring
        return None
    if payload is None:
        return None

    from src.fundamental.thesis.models import Thesis
    from src.fundamental.thesis.probe import ProbedThesis

    try:
        thesis = Thesis.from_json_obj(payload)
    except Exception:                          # noqa: BLE001 — a stale shape
        return None
    # ⚠ `runs=()` — ★ **the k runs are not replayed and must not be invented.**
    #   RM-1's figure travels on the thesis itself (`verdict_stability`); a
    #   fabricated run list would let a monitor count evidence that never
    #   happened.
    return ProbedThesis(thesis=thesis,
                        stability=_stability_of(thesis), runs=())


def _stability_of(thesis):
    """RM-1's result as it was stored. ⚠ Never recomputed — recomputing from a
    single stored verdict would report `agreement = 1.00` for every cached
    thesis, which is a measurement of nothing."""
    from src.fundamental.monitor.variance import StabilityResult

    payload = getattr(thesis, "verdict_stability", None)
    if not payload:
        return None
    try:
        return StabilityResult.from_json_obj(payload)
    except Exception:                          # noqa: BLE001
        return None
