"""D-01 §10B.1/§10B.2 — the sudden-move read. RA-78…RA-81, RA-88…RA-91.

★★ **The residual is computed BEFORE the trigger fires, not after it** (RA-88).
⚠ A trigger keyed on the **raw** return is measuring the sector, not the
company — for semiconductor names a market-plus-sector model explains a large
share of return variance, so a raw-return trigger fires on the days the whole
theme repriced, and those are exactly the days it fires on **every name at once**.

★ **D-01 never detects a price move** (RA-78). It receives a *decomposed* move
as an input with its arithmetic trail, exactly as it receives a fair value —
and the decomposition comes from **D-02**, not D-03, because D-02 is neutral
ground (L0 §4.2), so consuming it is not consuming SEAT-3's output.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from src.fundamental.errors import MoveRationalisedError, MoveUndecomposedError

#: RA-88 — the only basis a trigger may be keyed on.
BASIS_RESIDUAL, BASIS_RAW = "residual", "raw"

#: The identity `move = market + sector + fx + residual` must close. A trail
#: that does not add up is not a decomposition, it is four numbers.
IDENTITY_TOLERANCE = 1e-6

EXPLAINED, UNEXPLAINED = "explained", "unexplained"


@dataclass(frozen=True, slots=True)
class MoveDecomposition:
    """D-02's output, consumed. ★ D-01 computes none of these numbers (RA-45)."""

    ticker: str
    session: date
    total_return: float
    market: float
    sector: float
    residual: float
    #: ★ RA-90 — **FX is a NAMED TERM, not an entry on an observable list.** A
    #: CAD book holding USD names carries an identical currency exposure on
    #: *every* position, so it does not diversify away the way name-specific
    #: error does. ⚠ It is a systematic contributor **no thesis is about and no
    #: analysis will ever explain**, and leaving it inside the residual
    #: attributes it to the company (INV-5, L0 INV-001).
    fx: float | None = None
    quote_currency: str = "USD"
    book_currency: str = "USD"
    trail_ref: str = ""
    source: str = "D-02"

    def __post_init__(self) -> None:
        if self.source != "D-02":
            raise MoveUndecomposedError(
                self.ticker,
                f"decomposition sourced from {self.source!r}. ★ It comes from "
                f"D-02 — not because D-03 could not compute it, but because "
                f"D-02 is neutral ground (RA-78, L0 §4.2)",
            )
        if not self.trail_ref:
            raise MoveUndecomposedError(
                self.ticker,
                "no arithmetic trail. A decomposition without its trail is a "
                "number D-01 would have to take on faith (RA-45)",
            )
        if self.quote_currency != self.book_currency and self.fx is None:
            raise MoveUndecomposedError(
                self.ticker,
                f"{self.quote_currency}-quoted in a {self.book_currency} book "
                f"with no FX term — the currency move is sitting inside the "
                f"residual and would be attributed to the company (RA-90, INV-5)",
            )
        parts = self.market + self.sector + (self.fx or 0.0) + self.residual
        if abs(parts - self.total_return) > IDENTITY_TOLERANCE:
            raise MoveUndecomposedError(
                self.ticker,
                f"identity does not close: market+sector+fx+residual="
                f"{parts:.8f} vs total {self.total_return:.8f}",
            )

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "session": self.session.isoformat(),
                "total_return": self.total_return, "market": self.market,
                "sector": self.sector, "fx": self.fx, "residual": self.residual,
                "quote_currency": self.quote_currency,
                "book_currency": self.book_currency,
                "trail_ref": self.trail_ref, "source": self.source}


@dataclass(frozen=True, slots=True)
class MoveTrigger:
    """D-03's *"did the price move abnormally"* — against trailing volatility."""

    ticker: str
    session: date
    sigma: float
    basis: str = BASIS_RESIDUAL


@dataclass(frozen=True, slots=True)
class MoveReview:
    """★ RA-79/RA-80 — the finding, which may be that there is no finding.

    *"The market repriced this name by 3.1σ and our evidence does not say why"*
    is an **information gap with a direction**, not a failure.
    """

    ticker: str
    session: date
    status: str
    residual: float
    sigma: float
    #: Only ever set when `status == EXPLAINED`, and only from the bundle.
    explanation_refs: tuple[str, ...] = ()
    routed_to: str = ""
    data_gap: dict | None = None

    def to_json_obj(self) -> dict:
        return {"ticker": self.ticker, "session": self.session.isoformat(),
                "status": self.status, "residual": self.residual,
                "sigma": self.sigma,
                "explanation_refs": list(self.explanation_refs),
                "routed_to": self.routed_to, "data_gap": self.data_gap}


def review_move(trigger: MoveTrigger, decomposition: MoveDecomposition | None,
                *, explanations=(), cause: str | None = None,
                move_at: datetime | None = None) -> MoveReview:
    """The §10B.2 read. Residual first; the honest gap over the plausible story.

    ⚠ **RA-91**: acting on an undecomposed move is a top-down decision taken by
    accident — exiting a sound position because its sector repriced is an
    allocation call, **SEAT-1's authority exercised without the seat**. That is
    why RA-88 is a gate and not a refinement.
    """
    if decomposition is None:
        raise MoveUndecomposedError(trigger.ticker)
    if trigger.basis != BASIS_RESIDUAL:
        raise MoveUndecomposedError(
            trigger.ticker,
            f"trigger basis is {trigger.basis!r}. RA-89's clustering diagnostic "
            f"is a PARTIAL detector and may never displace this",
        )
    if trigger.session != decomposition.session or trigger.ticker != decomposition.ticker:
        raise MoveUndecomposedError(
            trigger.ticker,
            f"trigger {trigger.ticker}/{trigger.session} does not match the "
            f"decomposition {decomposition.ticker}/{decomposition.session}",
        )

    usable = tuple(_checked(e, move_at) for e in explanations)
    if usable:
        return MoveReview(
            ticker=trigger.ticker, session=trigger.session, status=EXPLAINED,
            residual=decomposition.residual, sigma=trigger.sigma,
            explanation_refs=usable, routed_to="V-01",
        )

    # ── RA-79: an LLM asked *"why did this stock fall"* will always produce a
    #    reason, and **a plausible reason attached to an unexplained move is
    #    strictly worse than the honest gap.**
    if cause:
        raise MoveRationalisedError(trigger.ticker, cause)

    return MoveReview(
        ticker=trigger.ticker, session=trigger.session, status=UNEXPLAINED,
        residual=decomposition.residual, sigma=trigger.sigma,
        # ★ RA-80 — a research instruction, which is S-4's `would_change`
        #   applied to price action.
        data_gap={
            "field": f"cause_of_{trigger.session.isoformat()}_residual",
            "obtainable": "fetchable",
            "note": (f"the market repriced {trigger.ticker} by "
                     f"{trigger.sigma:.1f}σ idiosyncratically and our evidence "
                     f"does not say why"),
        },
    )


def _checked(explanation, move_at):
    """RA-81 — direction is reported; causation is not inferred from it.

    *"Fell on the news"* requires the news timestamp to **precede** the move,
    and D-07 supplies both.
    """
    ref, published_at = explanation
    if move_at is not None and published_at is not None and published_at > move_at:
        raise MoveRationalisedError(
            ref, f"published {published_at.isoformat()}, after the move at "
                 f"{move_at.isoformat()}, so it cannot have caused it",
            rule="RA-81",
        )
    return ref


@dataclass(frozen=True, slots=True)
class ClusterDiagnostic:
    """RA-89 — deterministic, free, and it needs no factor model to run."""

    session: date
    tickers: tuple[str, ...]
    suspected_common_factor: bool

    def to_json_obj(self) -> dict:
        return {"session": self.session.isoformat(),
                "tickers": list(self.tickers),
                "suspected_common_factor": self.suspected_common_factor,
                "note": ("★ a system that fires thirteen invalidation triggers "
                         "in one day has already diagnosed itself, and should "
                         "say so rather than escalate thirteen times"
                         if self.suspected_common_factor else "")}


def cluster_check(triggers) -> tuple[ClusterDiagnostic, ...]:
    """★ If **two or more** book names trip in the same session, every one of
    those triggers is suspect until its residual says otherwise.

    ⚠ **A PARTIAL detector that may never displace RA-88.** It catches a sector
    dropping 5 % in a day; it is blind to one drifting 1 %/day for a fortnight —
    names trip on different sessions, no clustering signature, each looks
    idiosyncratic. ★ **That slow form is RA-85's weekly accumulation sweep.**
    """
    by_session: dict[date, list[str]] = {}
    for trigger in triggers:
        by_session.setdefault(trigger.session, []).append(trigger.ticker)
    return tuple(
        ClusterDiagnostic(session=session, tickers=tuple(sorted(set(names))),
                          suspected_common_factor=len(set(names)) >= 2)
        for session, names in sorted(by_session.items())
    )
