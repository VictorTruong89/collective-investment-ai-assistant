"""F6a — config-influence routing. A **pure function** (`PG-9`).

★★ **The control plane stays deterministic.** Routing decisions are made by pure
functions, are replayable, and record the reason for every choice. Three
independent grounds, from `PG-9`:

1. *"Why did this run use the one-week model?"* must have an answer better than
   *"the model chose it"* — otherwise `vision.md` §1.1's explainability claim is
   false.
2. `AP-5` — routing on a definable quantity is a computation, not a judgement.
3. ⚠ A stochastic control plane makes two runs on identical data take different
   paths, which **destroys `F7a`/`F7b`'s ability to attribute an outcome
   difference to deliberation**.

⚠ **`PG-7`: cross-configuration is recorded and never called agreement.** If one
seat's output shaped another's configuration, `influenced_by` says so — because
the firewall's value is that concurrence between *independent* views is
informative, and cross-configuration silently turns concurrence into an echo.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

#: ★ `D1` — the declared phase order, DERIVED not chosen.
#: `L2-signal-combination` (upstream): *"quant ranks → thesis gates → risk
#: alerts, derived from coverage economics"* — D-01's coverage is `O(1)/day` and
#: **conditioned on D-03's output**, so it carries zero cross-sectional ranking
#: information, and dense coverage costs **6.3–19 % of NAV per year**.
#: ⚠ Do NOT justify this by constitution `P3`: that was narrowed to *"verdicts
#: gate, never upgrade"* in Aug 2026 and the ordering mandate was removed.
PHASE_ORDER: tuple[str, ...] = ("quant", "fundamental", "risk", "decision")

#: `D2` — exactly ONE predicate at `MS-6`. ⚠ Every unexercised branch is a path
#: through the control plane that `PG-9`'s replay has never covered; a second
#: arrives when `F2`'s recorded `DecisionRecord.state` shows a measured need.
VOL_THRESHOLD = 0.45


class UnknownPort(Exception):
    """⚠ A port with no declared candidates cannot be routed (`P5`)."""


class PhaseOrderViolation(Exception):
    """`AC-6a.7` — influence must flow forward through `PHASE_ORDER`."""


@dataclass(frozen=True, slots=True)
class Routing:
    """`CT-6a.1`. ⚠ `reason` is never empty — *"default"* is a reason."""

    port: str
    variant: str
    reason: str
    candidates: tuple[str, ...]
    influenced_by: str | None = None

    def __post_init__(self) -> None:
        if not self.reason:
            raise ValueError(
                "reason is never empty (AC-6a.3) — a routing choice that cannot "
                "say which predicate fired is not explainable (PG-9)")
        if self.variant not in self.candidates:
            raise ValueError(
                f"{self.variant!r} is not among {self.candidates} — a Routing may "
                "only name a REGISTERED variant (F1 AC-F1.5, closed set)")


def phase_of(seat_domain: str) -> int:
    try:
        return PHASE_ORDER.index(seat_domain)
    except ValueError:
        raise PhaseOrderViolation(
            f"{seat_domain!r} is not in the declared phase order {PHASE_ORDER} "
            "(AC-6a.7)") from None


def assert_forward(influencer: str, influenced: str) -> None:
    """`AC-6a.7` — ★★ influence is acyclic because it flows FORWARD only.

    ⚠ A cycle would make two seats configure each other, and neither's output
    would be independent of the other's — the firewall's whole premise.
    """
    if phase_of(influencer) >= phase_of(influenced):
        raise PhaseOrderViolation(
            f"{influencer!r} may not configure {influenced!r}: influence flows "
            f"forward through {PHASE_ORDER} only. Backward or same-phase "
            "influence makes the two views mutually dependent, and their "
            "agreement stops being evidence (AC-6a.7, PG-7)")


def select(port: str, features: Mapping[str, object],
           candidates: Sequence[str] | None = None,
           peer: Mapping[str, object] | None = None) -> Routing:
    """`CT-6a.2` — **total**: every input yields a `Routing` (`AC-6a.11`).

    ⚠ Pure (`AC-6a.2`): no I/O, no clock, no randomness. Given identical inputs
    it returns an equal `Routing` (`AC-6a.1`), which is what makes a run
    replayable and an outcome difference attributable.
    """
    cands = tuple(candidates) if candidates is not None else DEFAULT_CANDIDATES.get(port, ())
    if not cands:
        raise UnknownPort(
            f"no candidates declared for port {port!r} — routing cannot invent one "
            "(F1 AC-F1.5: the variant set is closed)")

    influenced_by = None
    domain = PORT_DOMAIN.get(port)

    if peer is not None:
        # ⚠ PG-7 — another seat's output is shaping this choice. Record it, and
        # ★ check the direction FIRST: under D1's derived order, a later phase
        # may not configure an earlier one.
        influenced_by = str(peer.get("seat_domain", "unknown"))
        assert_forward(influenced_by, domain or "decision")

    # `D2` — the ONE predicate at MS-6. ⚠ Note which port it routes: the
    # volatility signal is QUANT's, so the port it may legitimately configure is
    # a LATER phase's. Routing quant's own model from quant's own feature is not
    # cross-configuration at all — it is just a predicate.
    vol = (peer or features).get("realised_vol_60d")
    if isinstance(vol, (int, float)) and vol > VOL_THRESHOLD:
        hot = _HOT_VARIANT.get(port)
        if hot in cands:
            return Routing(port, hot, f"realised_vol_60d > {VOL_THRESHOLD}",
                           cands, influenced_by)

    return Routing(port, cands[0], "default", cands, influenced_by)


#: Which seat's domain each port belongs to — ★ this is what makes `AC-6a.7`
#: checkable. ⚠ Found while writing `MS-6`'s tests: the worked example routed
#: `ranking_model` (a QUANT port, the FIRST phase) from a peer, which
#: `assert_forward` correctly refused — **nothing may configure the first
#: phase.** The cross-configuration case is quant's volatility shaping how deep
#: the FUNDAMENTAL analysis goes, which is forward and coherent.
PORT_DOMAIN: dict[str, str] = {
    "ranking_model": "quant",
    "thesis_depth": "fundamental",
}

#: Declared per port. ⚠ The first entry is the default (`CT-6a.2`).
DEFAULT_CANDIDATES: dict[str, tuple[str, ...]] = {
    "ranking_model": ("1m", "1w"),
    "thesis_depth": ("standard", "deep"),
}

#: The variant `D2`'s predicate selects when volatility is high.
_HOT_VARIANT: dict[str, str] = {"ranking_model": "1w", "thesis_depth": "deep"}
