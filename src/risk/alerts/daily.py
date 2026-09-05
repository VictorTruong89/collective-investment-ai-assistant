"""D-05 §4A.2 — WF-R1, the daily book pass. RK-29…RK-36.

```text
  0  RECONCILED?   ⛔ ABORT      4  FLAGS      ║ parallel with 2 ║
  1  SNAPSHOT                    5  FACTORS    P and D for D-06
  2  EXPOSURE                    6  ALERTS     only from a COMPLETE pass
  3  METRICS                     7  PUBLISH    BookRisk · Flag[]
```

★ **There is no gate step, and its absence is deliberate** (RK-34, INV-026). A
reader who assumes a "risk pipeline" ends in a pass/fail will look for one, and
**stating that it does not exist is cheaper than having someone add it.**
"""

from __future__ import annotations

from datetime import date

from src.risk.alerts.service import emit
from src.risk.contracts.book_risk import BookRisk
from src.risk.contracts.theme import ThemeTaxonomy
from src.risk.errors import NoBookError
from src.risk.exposure.aggregate import (
    assert_aggregated, exposure, thresholds_crossed,
)
from src.risk.metrics.drawdown import drawdown, unmeasured_factor
from src.risk.contracts.alerts import Alert

#: Step 0's outcomes are binary and the ladder ends at the first one.
STEPS = ("reconciled", "snapshot", "exposure", "metrics", "flags", "factors",
         "alerts", "publish")


def daily_book_pass(*, as_of: date, books, taxonomy: ThemeTaxonomy,
                    history=(), flags=(), base_currency: str = "CAD",
                    marginal=None):
    """WF-R1, in the order §4A.2's table forces.

    ⚠ **RK-35: a failed step aborts the pass and publishes nothing** — no
    partial `BookRisk`, no stale fallback, no empty-but-valid object.
    """
    books = tuple(books)

    # ── 0 RECONCILED? ★★ RK-29 — the tempting alternative (compute on the last
    #    good book) produces a correct-looking report ABOUT YESTERDAY, and
    #    nothing on the artifact would say so.
    if not books:
        raise NoBookError(as_of, "no book states supplied")
    unreconciled = [b.account_id for b in books if b.reconciled != "ok"]
    if unreconciled:
        raise NoBookError(as_of, f"unreconciled accounts {sorted(unreconciled)!r}")

    # ── 2 EXPOSURE ── before 3, because marginal contribution is exposure-
    #    weighted and weights that do not exist yet compute against equal ones.
    view = exposure(books, as_of=as_of, taxonomy=taxonomy,
                    base_currency=base_currency)
    assert_aggregated(view, books)                     # RK-5
    crossings = thresholds_crossed(view)               # RK-2

    # ── 3 METRICS ── and ── 4 FLAGS ── which RK-33 keeps independent: the flags
    #    read the BOOK, not the aggregation, so sequencing them after exposure
    #    would invent a dependency that would then be maintained.
    state = drawdown(history or books, as_of=as_of)

    # ── 5 FACTORS ── after 3: D is the drawdown; an incomplete measure would
    #    hand D-06 a factor computed from one.
    factors = {"D": state.to_json_obj() if state.status == "ok"
               else unmeasured_factor("D", state.why)}
    factors["P"] = (marginal.to_json_obj() if marginal is not None
                    else unmeasured_factor(
                        "P", "no candidate supplied; P is WF-R2's, on request"))

    risk = BookRisk(as_of=as_of, base_currency=base_currency, exposure=view,
                    thresholds_crossed=crossings, drawdown=state,
                    factors_for_d06=factors, flags=tuple(flags))

    # ── 6 ALERTS ── ★★ RK-30, last, and only from a complete pass.
    alerts = emit(_alerts_from(crossings, flags, as_of), complete=True)
    return risk, alerts


def _alerts_from(crossings, flags, as_of: date):
    """★ Every crossing and every flag becomes a LEVEL 2 alert, unfiltered.

    ⚠ **RK-18: no severity threshold may quietly drop the tail.** The mapping is
    total on purpose — there is no branch here that decides an alert is not
    worth emitting.
    """
    out = [Alert(source=f"threshold:{c.name}", level=c.alert_level,
                 text=f"{c.subject}: {c.value:.1f}% against a "
                      f"{c.limit:.1f}% reporting limit (effect: {c.effect})",
                 as_of=as_of)
           for c in crossings]
    out += [Alert(source=f"flag:{f.kind}", level=2,
                  text=f"{f.ticker} in {f.account}: {f.kind}", as_of=as_of)
            for f in flags]
    return tuple(out)
