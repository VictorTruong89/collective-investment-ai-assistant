"""D-11 §8 — lot history: average cost and round trips. RC-59, RC-60.

★ **What M-3 and M-4 actually read.** The flags are D-05's judgement (RK-12…
RK-17); the *bookkeeping* underneath them is D-11's, because it is a property of
the record rather than of the risk view.

⚠ **Average cost is weighted-average, not FIFO.** That is the Canadian
adjusted-cost-base convention, and M-3 is a rule about *average cost rising* —
FIFO would answer a different question and give a different flag.

⚠ **Round trips are FIFO.** *Which* shares came back out matters for a holding
period, and the earliest lot is the one a holding-period test is about.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class CostChange:
    """One buy, and what it did to the average cost (M-3's evidence)."""

    account_id: str
    instrument_id: str
    symbol: str
    trade_date: date
    added_quantity: float
    added_value: float
    held_before: float
    avg_cost_before: float
    avg_cost_after: float
    currency: str

    @property
    def raises_average_cost(self) -> bool:
        """RK-12 / INV-028 — ★ *pyramiding-up is the behaviour to curb.*

        ⚠ The **first** purchase of a name is not pyramiding: there is no prior
        average to raise. Adding to an existing lot at a higher price is.
        """
        return self.held_before > 0 and self.avg_cost_after > self.avg_cost_before

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "instrument_id": self.instrument_id,
                "symbol": self.symbol, "trade_date": self.trade_date.isoformat(),
                "added_quantity": self.added_quantity,
                "added_value": round(self.added_value, 2),
                "held_before": self.held_before,
                "avg_cost_before": round(self.avg_cost_before, 4),
                "avg_cost_after": round(self.avg_cost_after, 4),
                "raises_average_cost": self.raises_average_cost,
                "currency": self.currency}


@dataclass(frozen=True, slots=True)
class RoundTrip:
    """A closed buy→sell pair, FIFO-matched (M-4's evidence)."""

    account_id: str
    instrument_id: str
    symbol: str
    opened_on: date
    closed_on: date
    quantity: float
    buy_price: float
    sell_price: float
    currency: str

    @property
    def held_days(self) -> int:
        return (self.closed_on - self.opened_on).days

    @property
    def gain_pct(self) -> float:
        if not self.buy_price:
            return 0.0
        return round(100.0 * (self.sell_price - self.buy_price) / self.buy_price, 4)

    def to_json_obj(self) -> dict:
        return {"account_id": self.account_id, "symbol": self.symbol,
                "instrument_id": self.instrument_id,
                "opened_on": self.opened_on.isoformat(),
                "closed_on": self.closed_on.isoformat(),
                "held_days": self.held_days, "quantity": self.quantity,
                "buy_price": self.buy_price, "sell_price": self.sell_price,
                "gain_pct": self.gain_pct, "currency": self.currency}


def _unit_cost(order) -> float:
    """Cash actually paid per share, **commission included** (RC-15).

    ★ M-3 is about *what you paid*, and the fee is part of that — excluding it
    would understate the average cost of every small order by more than the
    price moves this rule cares about.
    """
    return abs(order.total_amount) / abs(order.quantity) if order.quantity else 0.0


def cost_changes(orders) -> tuple[CostChange, ...]:
    """RC-59 — the running weighted-average cost, one row per buy."""
    held: dict = {}
    out = []
    for order in sorted(orders, key=lambda o: (o.trade_date, o.instrument_id)):
        key = (order.account_id, order.instrument_id)
        quantity, book_value = held.get(key, (0.0, 0.0))
        if order.quantity > 0:
            before = book_value / quantity if quantity else 0.0
            spent = abs(order.total_amount)
            new_quantity = quantity + order.quantity
            new_value = book_value + spent
            out.append(CostChange(
                account_id=order.account_id, instrument_id=order.instrument_id,
                symbol=order.symbol, trade_date=order.trade_date,
                added_quantity=order.quantity, added_value=spent,
                held_before=quantity, avg_cost_before=before,
                avg_cost_after=new_value / new_quantity if new_quantity else 0.0,
                currency=order.currency))
            held[key] = (new_quantity, new_value)
        else:
            # ⚠ A sale removes shares at the AVERAGE cost, not at the sale
            #   price — otherwise the remaining average drifts with every exit.
            sold = min(abs(order.quantity), quantity)
            average = book_value / quantity if quantity else 0.0
            held[key] = (quantity - sold, book_value - sold * average)
    return tuple(out)


def round_trips(orders) -> tuple[RoundTrip, ...]:
    """RC-60 — FIFO-matched closed pairs, with their holding periods."""
    lots: dict = {}
    out = []
    for order in sorted(orders, key=lambda o: (o.trade_date, o.instrument_id)):
        key = (order.account_id, order.instrument_id)
        queue = lots.setdefault(key, deque())
        if order.quantity > 0:
            queue.append([order.trade_date, order.quantity, _unit_cost(order)])
            continue
        remaining = abs(order.quantity)
        sell_price = _unit_cost(order)
        while remaining > 1e-9 and queue:
            opened_on, quantity, buy_price = queue[0]
            matched = min(remaining, quantity)
            out.append(RoundTrip(
                account_id=order.account_id, instrument_id=order.instrument_id,
                symbol=order.symbol, opened_on=opened_on,
                closed_on=order.trade_date, quantity=matched,
                buy_price=round(buy_price, 4), sell_price=round(sell_price, 4),
                currency=order.currency))
            remaining -= matched
            if matched >= quantity - 1e-9:
                queue.popleft()
            else:
                queue[0][1] = quantity - matched
        # ⚠ `remaining > 0` here means shares were sold that no buy in the
        #   window opened — RC-45's condition, already checked upstream.
    return tuple(out)
