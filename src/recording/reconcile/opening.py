"""D-11 §8 — the opening snapshot. RC-47, with RC-45 as its reason.

★ **RC-9 derives the book from activity.** ⚠ **RC-45** showed what that costs
when the activity window starts after the lots were opened: the replay produces
a *negative* position, **the cash still balances**, and nothing notices.

★ A snapshot read off a broker statement supplies the starting balance so the
derivation has somewhere to start. ⚠ **It may not be back-computed as
`current − activity`** — that makes the holdings an input, the forward replay
reproduces them by construction, and the check becomes a tautology.

⚠ **UNUSED as of 2026-08-25, and kept deliberately.** Victor re-exported all
four accounts from inception (2022-01-01), so the book now derives from activity
alone and needs no snapshot. ★ A `template_for()` helper that *inferred* opening
quantities from the replay was **deleted at his instruction** — it produced
numbers nobody could check against a statement, which is the guessing this
domain exists to refuse.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

FROM_INCEPTION, FROM_SNAPSHOT = "activity_from_inception", "opening_snapshot"


@dataclass(frozen=True, slots=True)
class OpeningPosition:
    """One line off a statement. ★ `as_of` is the statement's date, not today's."""

    account_id: str
    symbol: str
    wrapper: str            # "COMMON" | "CDR" — RC-16's middle term
    currency: str
    quantity: float
    as_of: date
    source: str = ""        # ⚠ which statement this was read from (RC-47)

    def __post_init__(self) -> None:
        if self.quantity < 0:
            raise ValueError(
                f"{self.account_id}/{self.symbol}: an opening position of "
                f"{self.quantity} is a short, and this mandate holds none "
                f"(RC-47) — check the statement")
        if not self.source:
            raise ValueError(
                f"{self.account_id}/{self.symbol}: an opening position with no "
                f"stated source is not evidence. ★ RC-47 requires it to be read "
                f"off a statement, and the statement must be named")

    @property
    def instrument_id(self) -> str:
        return f"{self.symbol}|{self.wrapper}|{self.currency}"

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "symbol": self.symbol,
                "wrapper": self.wrapper, "currency": self.currency,
                "quantity": self.quantity, "as_of": self.as_of.isoformat(),
                "source": self.source}


@dataclass(frozen=True, slots=True)
class DerivedPositions:
    """The book's position side, and **which origin produced it** (RC-47)."""

    origin: str
    as_of: date | None
    quantities: dict

    def to_json_obj(self) -> dict:
        return {"origin": self.origin,
                "opening_as_of": self.as_of.isoformat() if self.as_of else None,
                "positions": {f"{a}|{i}": q
                              for (a, i), q in sorted(self.quantities.items())}}


def load_opening(path) -> tuple[OpeningPosition, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    as_of = date.fromisoformat(payload["as_of"])
    source = payload.get("source", "")
    return tuple(
        OpeningPosition(account_id=row["account_id"], symbol=row["symbol"],
                        wrapper=row.get("wrapper", "COMMON"),
                        currency=row.get("currency", "CAD"),
                        quantity=float(row["quantity"]), as_of=as_of,
                        source=row.get("source", source))
        for row in payload["positions"])


def derive_positions(orders, *, opening=()) -> DerivedPositions:
    """RC-9 + RC-47 — `opening + activity`, and RC-45's check still applies.

    ⚠ A snapshot that still leaves a position negative means **the snapshot or
    the window is wrong**, and neither is guessed.
    """
    from src.recording.errors import TruncatedWindowError

    quantities: dict = {}
    opening = tuple(opening)
    for row in opening:
        quantities[(row.account_id, row.instrument_id)] = row.quantity
    for order in orders:
        key = (order.account_id, order.instrument_id)
        quantities[key] = quantities.get(key, 0.0) + order.quantity

    negative = {k: v for k, v in quantities.items() if v < -1e-9}
    if negative:
        raise TruncatedWindowError(negative)
    return DerivedPositions(
        origin=FROM_SNAPSHOT if opening else FROM_INCEPTION,
        as_of=opening[0].as_of if opening else None,
        quantities={k: v for k, v in quantities.items() if abs(v) > 1e-9})
