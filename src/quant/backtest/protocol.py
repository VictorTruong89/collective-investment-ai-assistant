"""D-03 §7.3 — the CV protocol. QA-18, QA-19, QA-3, QA-37.

★ **QA-18: purge and embargo are DERIVED from the horizon set, never configured
independently.** ⚠ *Changing the horizon set changes them automatically, or they
will be wrong the first time someone forgets.*

★ **QA-19: CV groups on `(ticker, date)`**, so all copies of a row fall in the
same fold — otherwise a row replicated across horizons trains on one copy and
tests on another, which is leakage wearing a fold boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

FORMULA_PURGE = "cv.purge_embargo.derived.v1"

#: §5.6's HorizonSet v1 — `purge_days` is `max(trading_days)` across the set.
DEFAULT_EMBARGO_DAYS = 5


@dataclass(frozen=True, slots=True)
class CVProtocol:
    """What a fold split is pinned to. ★ Derived, then frozen onto the spec."""

    purge_days: int
    embargo_days: int
    horizon_set_name: str
    horizon_set_version: int
    n_folds: int = 5
    formula_id: str = FORMULA_PURGE

    def to_json_obj(self) -> dict:
        return {"purge_days": self.purge_days, "embargo_days": self.embargo_days,
                "horizon_set": {"name": self.horizon_set_name,
                                "version": self.horizon_set_version},
                "n_folds": self.n_folds, "formula_id": self.formula_id}


def derive_protocol(horizon_set, *, n_folds: int = 5,
                    embargo_days: int = DEFAULT_EMBARGO_DAYS) -> CVProtocol:
    """QA-18 — ★ `purge_days = max(trading_days)` over the whole set.

    ⚠ Not the horizon being evaluated: **the longest one**. A fold purged for
    21 days while a 63-day label is in the set leaks 42 days of overlap into
    every boundary.
    """
    from src.quant.errors import QuantError

    lengths = [h.trading_days for h in horizon_set.horizons]
    if not lengths:
        raise QuantError("a horizon set with no horizons derives no protocol")
    return CVProtocol(purge_days=max(lengths), embargo_days=embargo_days,
                      horizon_set_name=horizon_set.name,
                      horizon_set_version=horizon_set.version, n_folds=n_folds)


@dataclass(frozen=True, slots=True)
class Fold:
    index: int
    train_dates: tuple
    test_dates: tuple
    purged: int
    embargoed: int

    def to_json_obj(self) -> dict:
        return {"index": self.index, "n_train": len(self.train_dates),
                "n_test": len(self.test_dates), "purged": self.purged,
                "embargoed": self.embargoed,
                "test_start": self.test_dates[0].isoformat() if self.test_dates else None,
                "test_end": self.test_dates[-1].isoformat() if self.test_dates else None}


def make_folds(dates, protocol: CVProtocol) -> tuple[Fold, ...]:
    """Contiguous test blocks with purge on **both sides** and embargo after.

    ⚠ **Purging only before the test block is the common half-implementation.**
    A training row *after* the test block whose label window reaches back into
    it is exactly as leaky as one before — the overlap has no preferred
    direction.
    """
    ordered = sorted(set(dates))
    if not ordered:
        return ()
    size = max(1, len(ordered) // protocol.n_folds)
    folds = []
    for index in range(protocol.n_folds):
        start = index * size
        stop = len(ordered) if index == protocol.n_folds - 1 else start + size
        test = ordered[start:stop]
        if not test:
            continue
        lower = test[0] - timedelta(days=protocol.purge_days)
        upper = test[-1] + timedelta(days=protocol.purge_days
                                     + protocol.embargo_days)
        train = tuple(d for d in ordered if d < lower or d > upper)
        folds.append(Fold(index=index, train_dates=train, test_dates=tuple(test),
                          purged=len(ordered) - len(train) - len(test),
                          embargoed=protocol.embargo_days))
    return tuple(folds)


def group_key(row) -> tuple:
    """QA-19 — ★ **all copies of a row fall in the same fold.**"""
    return (row["ticker"], row["date"])


def assert_no_leakage(fold: Fold, *, purge_days: int) -> None:
    """The check the fold construction is supposed to make unnecessary.

    ⚠ It exists because *supposed to* is not a guarantee: a later change to
    `make_folds` would silently narrow the gap, and this fails when it does.
    """
    from src.quant.errors import QuantError

    if not fold.train_dates or not fold.test_dates:
        return
    lower, upper = fold.test_dates[0], fold.test_dates[-1]
    for day in fold.train_dates:
        gap = (lower - day).days if day < lower else (day - upper).days
        if gap < purge_days:
            raise QuantError(
                f"fold {fold.index}: training date {day} is {gap}d from the "
                f"test block, inside the {purge_days}d purge. An overlapping "
                f"label reaches across that boundary (QA-18, QA-3)")
