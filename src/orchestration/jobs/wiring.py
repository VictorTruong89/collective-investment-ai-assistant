"""D-08 — the adapters that connect the graph to the domains. OR-1, OR-40.

★★ **This is the one file where a domain is actually called**, and it lives at
the edge on purpose. `Orchestrator.run` takes `invoke` as an argument, so
**nothing inside the runner can return a value derived from market data** —
OR-1 stays greppable rather than reviewed.

⚠ **An adapter routes; it never computes.** Each one reads the pieces its job
needs from the context and hands them to the domain. The moment an adapter
starts *deriving* a value, D-08 has acquired analysis and OR-1 is broken —
`test_no_adapter_computes` is the guard.

★ Every adapter goes through `resolve(job)` first, so `Job.invokes` stays honest:
the declared target must exist, which is the check `assert_graph_resolves` pins
and which caught five wrong names when the graph was written.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.orchestration.jobs.graph import resolve, resolve_target


@dataclass
class RunContext:
    """What the graph accumulates. ⚠ **A bag of outputs, not a workspace.**

    Inputs are *supplied*; outputs are *stored*. No adapter derives a value that
    is not a domain's return, which is what keeps §4's `jobs/` "declared,
    inspectable, no logic".
    """

    as_of: date
    adj_as_of: date
    universe: tuple[str, ...]
    contract: object
    #: Supplied inputs — D-07 fetches these at the edge (DE-1: it holds the key).
    raw_prices: object = None
    #: ★ A SUPPLIED probed thesis (`.thesis`, `.stability`) for the nominated
    #: name, or `None`. ⚠ When it is `None` the gate falls back to the
    #: **declared stub** and the card is informational (BS-11/BS-33) — never
    #: actionable on a thesis that does not exist. ✏ 2026-10-05: no job in the
    #: daily graph produces one any more (the old `thesis` job was removed).
    probed_thesis: object = None
    events: tuple = ()
    event_store_root: str = ""
    books: tuple = ()
    taxonomy: object = None
    #: `{instrument_id: (price, currency)}` D-07 already fetched for the run.
    book_prices: dict = field(default_factory=dict)
    #: Where CT-11.7 run artifacts land. ⚠ Gitignored: a generated store in
    #: version control is a second source of truth that silently goes stale.
    artifact_root: object = None
    #: ⚠ **There is deliberately no `gateway` field.** ST-5 lets only D-01 reach
    #: the model, and a shim that can hold a gateway can make a call.
    #: ⊘ 2026-10-05: `engine`, `observation_ledger`, `fmp_client` removed with the
    #: old `observe` + `thesis` jobs that were their only readers.
    #: ★ The promoted artifact, or `None`. ⚠ Its presence is what switches D-03
    #: from the rule to the model — and MT-17 makes *promoted*, not *fitted*,
    #: the condition.
    incumbent: object = None
    #: `{"rows_by_ticker": …, "sectors": …}` for the `f_*` block.
    fundamentals: object = None
    #: ★ `{ticker: reason}` from D-07's event store — **supplied to D-03, never
    #: fetched by it** (QA-126). D-03 ranks D-02's numbers and computes none of
    #: its own; reaching into an event store would make it a data client.
    delisted: object = None
    #: ★ RP-50 — delivery is OFF unless asked for. ⚠ Sending is outward-facing,
    #: and a default-on switch mails somebody the first time it is wired.
    deliver: bool = False
    #: ★ RP-51 — from `REPORT_RECIPIENT`, never hardcoded and never defaulted to
    #: the SMTP user: mail to the wrong address is not recoverable.
    recipient: str = ""
    smtp_user: object = None
    smtp_password: object = None
    #: RP-24 — archived bytes are written **before** the send and verified after.
    archive_root: object = None
    #: ★ `fetch(symbol) -> (price, currency) | None`, a D-07 closure. D-11 calls
    #: it for the names IT holds — orchestration never learns the holdings.
    price_fetch: object = None
    #: ★ D-11's reason when no book could be valued. Carried, never composed
    #: here — OR-1 keeps adapters free of judgement.
    book_unavailable_reason: str = ""
    #: RA-71's answer for the nominated thesis, computed by D-01 upstream.
    thesis_stale: bool = False
    falsifier_fired: bool = False
    #: Accumulated outputs, keyed by job id.
    outputs: dict = field(default_factory=dict)

    def require(self, job_id: str):
        """★ A job that reads an absent upstream output **raises**, rather than
        substituting a default — the graph's own P5."""
        from src.orchestration.errors import OrchestrationError

        if job_id not in self.outputs:
            raise OrchestrationError(
                f"job output {job_id!r} is not in the context. ⚠ The graph "
                f"declares the dependency; an adapter that defaults instead of "
                f"raising would let a job run on data that was never produced")
        return self.outputs[job_id]


def _calendar_check(job, manifest, ctx: RunContext):
    """D-07 §6A — ★ DE-31: **before the first feature is built.**"""
    from src.orchestration.jobs.b3_run import _calendar

    return _calendar(universe=ctx.universe, as_of=ctx.as_of,
                     adj_as_of=ctx.adj_as_of, events=ctx.events,
                     root=ctx.event_store_root, run_id=manifest.run_id,
                     window=(ctx.raw_prices["date"].min(),
                             ctx.raw_prices["date"].max()))


def _prices(job, manifest, ctx: RunContext):
    """D-07 — the panel derived at the run's `adj_as_of` (DE-28)."""
    target = resolve(job) if ":" in job.invokes else None
    from src.data_engine import build_price_panel

    del target                    # the declared target is proven, not called
    return build_price_panel(ctx.raw_prices, ctx.events, ctx.adj_as_of)


def _features(job, manifest, ctx: RunContext):
    """D-02 — ★ FE-10 gates the panel build on D-07's calendar check."""
    from src.data_engine.calendar.check import require_check
    from src.feature_engineer.ml_features.assemble import build_panel

    report = ctx.require("calendar_check")
    return build_panel(
        contract=ctx.contract, price_panel=ctx.require("prices"),
        calendar_report=require_check(
            report, window=(report.window_start, report.window_end),
            what="D-02 panel build"),
        as_of=ctx.as_of, adj_as_of=ctx.adj_as_of,
        # ★ Supplied whenever the contract declares `f_*` features. ⚠ D-02
        #   REFUSES a null block rather than emitting 45 empty columns, so a
        #   contract needing fundamentals and a run without them fail loudly
        #   rather than training on nothing (FE-1).
        fundamentals=ctx.fundamentals)


def _rank(job, manifest, ctx: RunContext):
    """D-03 — CT-3.4. ⚠ The **only** nominating horizon is 1m (QA-120).

    ★★ **Scores with the promoted model when one exists**, and falls back to the
    rule otherwise. ⚠ *Until 2026-08-27 a model was promoted and the card was
    still ranked by `z(mom_21) × vol_21 × √21`* — `_incumbent_model()` loaded the
    artifact only so OR-44 could read its anchor, and nothing scored with it.
    """
    from src.orchestration.jobs.b3_run import _nominate, nomination_provenance

    provenance = nomination_provenance(ctx.contract, ctx.adj_as_of,
                                       ctx.require("calendar_check"))
    incumbent = ctx.incumbent
    if incumbent and incumbent.get("estimator") is not None:
        return _nominate_with_model(ctx, manifest, incumbent, provenance)
    return _nominate(ctx.require("features"), as_of=ctx.as_of,
                     run_id=manifest.run_id, universe_n=len(ctx.universe),
                     anchor=manifest.decision_anchor, provenance=provenance)


def _nominate_with_model(ctx: RunContext, manifest, incumbent, provenance):
    """★ D-03 consuming D-04's artifact — **parity first, then scoring.**

    ⚠ `check_parity` runs **once over the whole batch, before any score**
    (MT-6/MT-8): a check inside the scoring loop has already let the first rows
    through.
    """
    from src.quant.contracts.nomination import Candidate, Nomination
    from src.quant.horizons.horizon_set import PRODUCTION_V1
    from src.models.infer.rank import rank_by_model

    from src.models.infer.rank import assert_population_parity

    panel = ctx.require("features")
    # ★★ AB-4 — before scoring. `check_parity` compares the CONTRACT and cannot
    #   see the cross-section, but rank and sector-z features are defined by it.
    note = assert_population_parity(incumbent, panel)
    if note.startswith("UNCHECKED"):
        import sys as _sys
        print(f"  note: population parity {note}", file=_sys.stderr)

    horizon = PRODUCTION_V1.horizon(PRODUCTION_V1.arbitration.nominates)
    ranked = rank_by_model(
        panel, as_of=ctx.as_of, horizon_days=horizon.trading_days,
        estimator=incumbent["estimator"],
        feature_names=incumbent.get("features") or ())

    # ★★ QA-125 — an untradeable name never reaches D-12. ⚠ §6A cannot cover
    #   this: *"has any name stopped trading?"* is current-state and the
    #   calendar gate is window-scoped (AB-15).
    from src.quant.signals.tradeable import (
        apply_exclusions, assert_something_tradeable, untradeable,
    )

    barred = untradeable(panel, as_of=ctx.as_of, delisted=ctx.delisted)
    ranked, excluded = apply_exclusions(ranked, barred)
    assert_something_tradeable(ranked, excluded)
    return Nomination(
        as_of=ctx.as_of, run_id=manifest.run_id,
        decision_anchor=manifest.decision_anchor,
        horizon_set=(PRODUCTION_V1.name, PRODUCTION_V1.version),
        nominating_horizon=PRODUCTION_V1.arbitration.nominates,
        universe_n=len(ctx.universe),
        # ★ QA-121 — the ranker's identity is the ARTIFACT's content hash, so
        #   the card names the exact fitted thing rather than a family.
        model_artifact_id=incumbent["artifact_id"],
        candidates=tuple(Candidate(c["ticker"], c["rank"], c["ranked_quantity"],
                                   c["z"]) for c in ranked),
        excluded=excluded,
        # ★★ OR-58 / F12 D15 — a REFUSED informational ranker says so downstream.
        ranker_status=incumbent.get("status", "promoted"),
        refused_gates=tuple(incumbent.get("refused_gates") or ()),
        research_only=PRODUCTION_V1.arbitration.research_only,
        **provenance)


def _thesis_gate(job, manifest, ctx: RunContext):
    """D-01 — CT-1.4, from the **real thesis** when one exists.

    ★ `evaluate` maps §11.2's table over the thesis's own state (RA-49), and
    **the most conservative matching row wins** (RA-135). ⚠ With no thesis for
    the nominated name it falls back to the declared stub (BS-11/OR-43) and the
    card stays informational — a gate cannot PASS on a thesis nobody wrote.
    """
    from src.fundamental.thesis.gate import GateInputs, evaluate
    from src.fundamental.thesis.stub_gate import stub_gate_verdict

    ticker = ctx.require("rank").top.ticker
    probed = ctx.probed_thesis
    if probed is None or probed.thesis.ticker != ticker:
        return stub_gate_verdict(ticker, ctx.as_of)
    return evaluate(GateInputs(thesis=probed.thesis, stale=ctx.thesis_stale,
                               falsifier_fired=ctx.falsifier_fired),
                    as_of=ctx.as_of, ticker=ticker)


def _book(job, manifest, ctx: RunContext):
    """D-11 — ★ `resolve(job)`, **not** an import (OR-2, AC-8.2).

    Returns `(books, unavailable_reason)`. ⏸ Today the reason is always RC-58's:
    every account holds a CAD-venue or CDR position and the FMP plan quotes US
    listings only, so no account can be valued and none is returned.
    """
    from src.orchestration.jobs.graph import resolve

    return resolve(job)(as_of=ctx.as_of, prices=ctx.book_prices,
                        fetch=ctx.price_fetch)


def _risk(job, manifest, ctx: RunContext):
    """D-05 — the **full WF-R1 ladder** when a reconciled book exists.

    ⚠ **RK-29: it refuses on an unreconciled book**, and that refusal is the
    correct output, not a gap (DN-38). ★ With no book at all it is still the B3
    refusal — and **DN-39 then keeps the card informational**, because an
    `UNCHECKED` alert set reads as an all-clear the risk desk never made.
    """
    from src.risk.alerts.daily import daily_book_pass
    from src.risk.alerts.service import daily_pass

    books, why = ctx.outputs.get("book", ((), ctx.book_unavailable_reason))
    if not books or ctx.taxonomy is None:
        return daily_pass(as_of=ctx.as_of, book=None, why=why)
    _risk_report, alerts = daily_book_pass(
        as_of=ctx.as_of, books=books, taxonomy=ctx.taxonomy, history=books)
    return alerts


def _decide(job, manifest, ctx: RunContext):
    """D-12 — ★ it composes and **originates nothing** (DN-1)."""
    from src.decision.compose.service import compose, enforce_inv6

    alerts = ctx.require("risk")
    probed = ctx.probed_thesis
    stability = (probed.thesis.verdict_stability if probed else None)
    # ★★ DN-39 — actionable requires BOTH a complete risk pass and a stability
    #   figure. ⚠ Asking for it and being refused is the same defect as marking
    #   it true, so the claim is made only when both inputs are present.
    nomination = ctx.require("rank")
    refused = getattr(nomination, "ranker_status", "rule") == "refused_informational"
    actionable = (not refused) and bool(stability) and str(
        getattr(alerts, "status", "")).startswith("COMPLETE")

    recommendation = compose(
        nomination=nomination,
        gate_verdicts=[ctx.require("thesis_gate")],
        alert_set=alerts, run_id=manifest.run_id, as_of=ctx.as_of,
        gate_roster_declared=("thesis",),       # DN-11 — declared, not inferred
        manifest_anchor=manifest.decision_anchor,
        actionable=actionable,
        not_actionable_reason=None if actionable else _why_not(stability, alerts,
                                                               nomination=nomination),
        top_thesis_stability=stability,
        stubs=[s.to_json_obj() for s in manifest.stubs])
    enforce_inv6([recommendation])              # DN-22 / INV-6
    return recommendation


def _render(job, manifest, ctx: RunContext):
    """D-09 — ★ it **re-derives nothing** (RP-43)."""
    from src.reporting.render.card import build_card

    return build_card(ctx.require("decide"), as_of=ctx.as_of)


def _record(job, manifest, ctx: RunContext):
    """D-11 CT-11.7 — ★ `resolve(job)`, **not** an import (OR-2, OR-48).

    ⚠ The renderings go in as bytes exactly as D-09 produced them: D-11 stores
    what it is handed and normalises nothing, so a card read back tomorrow is
    byte-identical to the one that was sent.
    """
    from src.orchestration.jobs.b3_run import _render_all
    from src.orchestration.errors import OrchestrationError

    if ctx.artifact_root is None:
        # ⚠ NOT optional. RC-59 says every run persists an artifact, so a run
        #   with nowhere to persist is misconfigured — and P6 is constitutional.
        #   Degrading here would produce a run that looks complete and left no
        #   record, which is the exact absence RC-33 refuses.
        raise OrchestrationError(
            "no artifact_root on the run context, so CT-11.7 cannot be written. "
            "★ This is a configuration fault reported as one — a run that "
            "silently left no record is indistinguishable from one that never "
            "happened (RC-59, P6)")

    probed = ctx.probed_thesis
    return resolve(job)(
        run_id=manifest.run_id, root=ctx.artifact_root,
        manifest=manifest, recommendation=ctx.require("decide"),
        # ★★ RC-62 — the nomination travels with the recommendation, so the
        #   record can name the model, the universe and the barred names. ⚠ Up
        #   to 2026-08-27 a complete run directory could not answer *"what made
        #   this pick?"*, which QA-121 requires and INV-2 rests on.
        nomination=ctx.outputs.get("rank"),
        thesis=probed.thesis if probed else None,
        renderings=_render_all(ctx.require("render")),
        as_of=ctx.as_of)


def _deliver(job, manifest, ctx: RunContext):
    """D-09 sends, D-11 records the delivery, D-08 wires. **RP-50, RC-63.**

    ```text
    ╔══════════════════════════════════════════════════════════════════╗
    ║  ⚠⚠  THIS JOB USED TO REPORT SUCCESS IN 0.000278s HAVING SENT     ║
    ║  NOTHING.  It returned the renderings and never called send().    ║
    ║                                                                  ║
    ║  That is worse than a failure: the outcome record ASSERTED the    ║
    ║  artifact had reached the human, and P6 is the constitutional     ║
    ║  claim it was falsifying.                                        ║
    ╚══════════════════════════════════════════════════════════════════╝
    ```

    ⚠ **Not sending is reported as not sending** (RP-50). The disabled path
    returns a stated `{"sent": False, "why": …}` rather than something that
    looks like a delivery — DE-35's distinction, and the whole defect above.

    ★ A failure propagates (**OR-50**): the run ends `INCOMPLETE`, and the
    CT-11.7 record is already on disk because `record` precedes `deliver`.
    """
    from src.orchestration.jobs.b3_run import _render_all
    from src.orchestration.errors import OrchestrationError

    renderings = _render_all(ctx.require("render"))
    if not ctx.deliver:
        return {"sent": False, "renderings": renderings,
                "why": "delivery is off; pass --deliver to send (RP-50)"}

    if not ctx.recipient:
        # ★ RP-51 — raised, never defaulted to the SMTP user.
        raise OrchestrationError(
            "delivery was requested and REPORT_RECIPIENT is unset. ★ The "
            "recipient is never defaulted — mail to the wrong address is not "
            "recoverable, and falling back to the sending account would "
            "deliver to whoever holds it (RP-51)")

    deliver_fn = resolve_target("src.reporting.deliver.email:deliver")
    record_fn = resolve_target("src.recording.artifacts.store:record_delivery")
    receipt = deliver_fn(
        ctx.require("render"), renderings,
        sender=ctx.smtp_user.reveal(), recipient=ctx.recipient,
        user=ctx.smtp_user, password=ctx.smtp_password,
        archive_root=ctx.archive_root)
    # ★ RC-63 — recorded AFTER the send, by D-11, from what D-09 returned.
    record_fn(manifest.run_id, root=ctx.artifact_root, delivery=receipt)
    return {"sent": True, "renderings": renderings, "delivery": receipt}


#: ★ The wiring, declared. A job with no adapter is a job the graph cannot run,
#: which is louder than a job that silently does nothing.
ADAPTERS = {
    "calendar_check": _calendar_check, "prices": _prices, "features": _features,
    "rank": _rank,
    "thesis_gate": _thesis_gate,
    "book": _book, "risk": _risk,
    "decide": _decide, "render": _render,
    "record": _record, "deliver": _deliver,
}


def make_dispatch(ctx: RunContext):
    """Return the `invoke` the runner calls. ★ It stores; it does not transform."""
    def dispatch(job, manifest):
        from src.orchestration.errors import OrchestrationError

        adapter = ADAPTERS.get(job.job_id)
        if adapter is None:
            raise OrchestrationError(
                f"job {job.job_id!r} has no adapter. ⚠ A graph node nothing can "
                f"run is a declared step that silently does nothing (OR-40)")
        resolve(job)              # ★ the declared target must exist (MT-50's shape)
        ctx.outputs[job.job_id] = adapter(job, manifest, ctx)
        return ctx.outputs[job.job_id]
    return dispatch


def _why_not(stability, alerts, nomination=None) -> str:
    """DN-39 — ★ **name the missing input**, not a generic disclaimer.

    ⚠ *"Not actionable"* with no reason is the shape RA-30 and DE-35 both
    refuse: a reader cannot tell a deliberate hold from a broken pipeline.
    """
    missing = []
    if getattr(nomination, "ranker_status", "rule") == "refused_informational":
        # ★ DN-41 — the first reason, because it holds whatever else arrives.
        missing.append(f"ranked by a REFUSED model (failed: "
                       f"{', '.join(nomination.refused_gates)}) — informational only "
                       f"(OR-58, DN-41)")
    if not stability:
        missing.append(
            "no verdict stability — the nominated name has no k>=3 probed "
            "thesis (RA-20, AC-1.8)")
    status = str(getattr(alerts, "status", "")) or "absent"
    if not status.startswith("COMPLETE"):
        missing.append(f"the risk pass is {status} — silence from D-05 reads "
                       f"as an all-clear it never made (RK-30, DN-39)")
    return "; ".join(missing)
