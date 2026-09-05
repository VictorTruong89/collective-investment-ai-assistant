"""★ The composition root — where B3's walking skeleton is actually wired (CA-9).

```
CA-9: Adapters are wired in exactly ONE place per entry point — the
composition root — and passed inward as ports. For this system that root is
src/orchestration/, which creates a tension worth naming: D-08 must
CONSTRUCT adapters while COMPUTING nothing (OR-1).

Construction is not computation, so the two rules are compatible. But a
"composition root" that starts making choices about WHICH adapter based on
data has become a decision layer, and D-12 is the only domain allowed to be
one.
```

Every call below is an **invocation of a domain's public API** (ST-3). Nothing
here derives a number: the ranking is D-03's, the verdict is D-12's, the
rendering is D-09's, and this module only decides *what runs next*.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from src.data_engine import calendar_check, require_check
from src.data_engine.calendar import CachedEventFeed, EventStore
from src.decision import compose, enforce_inv6
from src.feature_engineer import B3_MINIMAL_V1, build_panel, coverage
from src.fundamental import stub_gate_verdict
from src.orchestration.contracts.manifest import RunManifest
from src.orchestration.jobs.skeleton import (
    _Recorder, b3_stubs, build_manifest, finish,
)
from src.orchestration.state.manifest_store import ManifestStore
from src.quant import PRODUCTION_V1, Candidate, Nomination, rank_candidates, rule_id
from src.reporting import (
    assert_content_equivalent, build_card, render_html, render_markdown,
)
from src.risk import daily_pass

#: L3 **QY-2** recommends NVDA: a long clean history, an EDGAR filer class, and a
#: split in-window to exercise QA-84/91. It is also the name B2's live probe
#: verified against §6A.5's known-answer set.
B3_TICKER = "NVDA"

#: BS-33 — the card is informational. Stated once, here, and carried onto the
#: artifact so the reason travels with the claim.
#: ⚠ **Both blockers this text used to name are gone** (2026-08-26): the thesis
#: gate is real and `author_thesis(k=3)` supplies RA-20's figure, and D-11's book
#: reconciles to the cent. ★ The live path is `wiring.py::_decide`, which decides
#: actionability from the two DN-39 inputs instead of asserting it here. This
#: constant is the **B3 slice's own** reason and stays scoped to it.
NOT_ACTIONABLE_REASON = (
    "B3 walking skeleton: this slice runs one hard-coded ticker with no thesis "
    "and no book, so neither DN-39 input exists. A verdict may not reach a human "
    "as actionable before RA-20's stability figure and a COMPLETE risk pass do "
    "— L3 BS-28/BS-33. The graph path (wiring.py) decides this per run."
)


@dataclass(frozen=True, slots=True)
class SkeletonResult:
    manifest: RunManifest
    outcome: object
    card: object
    renderings: dict
    nomination: object
    recommendation: object
    coverage: dict


def run_skeleton(
    *, as_of: date, adj_as_of: date, raw_prices: pd.DataFrame, events,
    event_store_root: str | Path, manifest_root: str | Path,
    ticker: str = B3_TICKER, universe=(B3_TICKER,), config: dict | None = None,
) -> SkeletonResult:
    """D-07 -> D-02 -> D-03 -> {D-01 stub, D-05} -> D-12 -> D-09.

    ★ **BS-10: exercises every domain boundary and nothing deep.** The purpose is
    to find the seams that are wrong while they are cheap to move.
    """
    from src.data_engine import build_price_panel

    started = datetime.now(timezone.utc)
    config = config or {"ticker": ticker, "horizon_set": "production@v1",
                        "contract": f"{B3_MINIMAL_V1.name}@v{B3_MINIMAL_V1.version}"}

    manifest = build_manifest(data_as_of=as_of, config=config, stubs=b3_stubs())
    ManifestStore(manifest_root).write(manifest)      # OR-9 — BEFORE any work
    rec = _Recorder()

    # 1 — D-07's calendar check. DE-31: before the first feature is built.
    report = rec.run("calendar_check", lambda: _calendar(
        universe=universe, as_of=as_of, adj_as_of=adj_as_of, events=events,
        root=event_store_root, run_id=manifest.run_id,
        window=(min(raw_prices["date"]), max(raw_prices["date"])),
    ))

    # 2 — D-07's price panel, derived at the run's adj_as_of (DE-28).
    prices = rec.run("prices", lambda: build_price_panel(raw_prices, events, adj_as_of))

    # 3 — D-02's contract-bound panel. FE-10 gates on the check above.
    window = (report.window_start, report.window_end)
    panel = rec.run("features", lambda: build_panel(
        contract=B3_MINIMAL_V1, price_panel=prices,
        calendar_report=require_check(report, window=window, what="D-02 panel build"),
        as_of=as_of, adj_as_of=adj_as_of,
    ))
    cov = coverage(panel, B3_MINIMAL_V1)

    # 4 — D-03's nomination (CT-3.4).
    nomination = rec.run("rank", lambda: _nominate(
        panel, as_of=as_of, run_id=manifest.run_id, universe_n=len(universe),
        anchor=manifest.decision_anchor,
    ))

    # 5 — D-01's gate. A real CT-1.4 emitter (BS-11), constant PASS, grade empty.
    gate = rec.run("gate", lambda: stub_gate_verdict(nomination.top.ticker, as_of))

    # 6 — D-05. It refuses: no reconciled book (RK-29), status UNCHECKED (DN-38).
    alerts = rec.run("risk", lambda: daily_pass(as_of=as_of, book=None))

    # 7 — D-12 composes. It originates nothing (DN-1).
    recommendation = rec.run("compose", lambda: compose(
        nomination=nomination, gate_verdicts=[gate], alert_set=alerts,
        run_id=manifest.run_id, as_of=as_of,
        gate_roster_declared=("thesis",),          # DN-11 — declared, not inferred
        manifest_anchor=manifest.decision_anchor,
        actionable=False, not_actionable_reason=NOT_ACTIONABLE_REASON,  # BS-33
        stubs=[s.to_json_obj() for s in manifest.stubs],
    ))
    enforce_inv6([recommendation])                 # DN-22 / INV-6

    # 8 — D-09 renders. It re-derives nothing (RP-43).
    card = rec.run("render", lambda: build_card(recommendation, as_of=as_of))
    renderings = rec.run("deliver", lambda: _render_all(card))

    return SkeletonResult(
        manifest=manifest, outcome=finish(manifest, rec, started,
                                          artifacts=tuple(sorted(renderings))),
        card=card, renderings=renderings, nomination=nomination,
        recommendation=recommendation, coverage=cov,
    )


def _calendar(*, universe, as_of, adj_as_of, events, root, run_id, window):
    """Populate D-07's event store from the run's events, then run the gate.

    ⚠ **Not a live sweep.** QD-16: 130 tickers x 8 classes is ~1,000 calls per run
    against a 300/min cap, so the gate reads an incrementally-maintained store.
    B3 seeds that store from the events it already has.
    """
    from src.data_engine.contracts import BLOCK, FLAG, Finding
    from src.data_engine.calendar.classes import BY_NAME

    store = EventStore(root)
    start, end = pd.Timestamp(window[0]).date(), pd.Timestamp(window[1]).date()
    findings = []
    for ev in events:
        name = "split" if ev.event_type == "split" else "dividend"
        if name == "split" and ev.detail["denominator"] > ev.detail["numerator"]:
            name = "reverse_split"
        findings.append(Finding(ev.ticker, name, BY_NAME[name].severity,
                                ev.event_date, ev.knowable_at, ev.detail, ev.source))
    store.upsert(findings)
    # ★★ **A refresh is recorded only for a class that was actually FETCHED.**
    #
    # ⚠ *Found 2026-08-27:* this loop recorded `split`, `reverse_split` and
    # `dividend` unconditionally — and the entrypoint passes `events=()`, so in
    # production **three classes reported `CHECKED` having fetched nothing**.
    # DE-35 exists to stop exactly that: *"absence of evidence and evidence of
    # absence are different results, and conflating them is how a false
    # assumption becomes a silent one."* The conflation was inside the code that
    # implements the rule.
    #
    # ★ With no events supplied every class now reports **UNCHECKED with its
    # reason**, which is the truth: the store was never refreshed.
    seeded = {f.event_class for f in findings}
    for cls in sorted(seeded):
        # ★ The refresh covers the universe this run seeded events for — ⚠ and
        #   says so, or a later gate over a WIDER universe would inherit a
        #   coverage this run never had (DE-56's defect one level up).
        store.record_refresh(cls, start, end, covers_tickers=universe)

    # ★★ **D-07 owns the gate and its handling** — one implementation (FE-4).
    #   ⚠ The handling used to be built from the events THIS RUN seeded, and the
    #   entrypoint seeds none; the moment `ingest/events.py` populates the store,
    #   every split in it would be unhandled and the daily run would **HALT**.
    #   `check_window` derives it from what the store holds instead.
    from src.data_engine.calendar.gate import check_window

    return check_window(
        store=store, universe=universe, start=start, end=end, as_of=as_of,
        adj_as_of=adj_as_of, run_id=run_id)


def _nominate(panel, *, as_of, run_id, universe_n, anchor):
    """D-03's CT-3.4. `model_artifact_id` is the ranker's content hash (QA-121)."""
    horizon = PRODUCTION_V1.horizon(PRODUCTION_V1.arbitration.nominates)
    ranked = rank_candidates(panel, as_of=as_of, horizon_days=horizon.trading_days)
    return Nomination(
        as_of=as_of, run_id=run_id, decision_anchor=anchor,
        horizon_set=(PRODUCTION_V1.name, PRODUCTION_V1.version),
        nominating_horizon=PRODUCTION_V1.arbitration.nominates,
        universe_n=universe_n,
        model_artifact_id=rule_id(),
        candidates=tuple(Candidate(c["ticker"], c["rank"], c["ranked_quantity"], c["z"])
                         for c in ranked),
        research_only=PRODUCTION_V1.arbitration.research_only,
    )


def _render_all(card) -> dict:
    """Both renderings, plus RP-32's content-equivalence check between them."""
    html_text, md_text = render_html(card), render_markdown(card)
    assert_content_equivalent(html_text, md_text)
    return {f"{card.ticker}_{card.as_of.isoformat()}.html": html_text.encode("utf-8"),
            f"{card.ticker}_{card.as_of.isoformat()}.md": md_text.encode("utf-8")}
