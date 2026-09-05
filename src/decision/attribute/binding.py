"""Which gates bound, and why — §5.6 (DN-13, DN-14)."""

from __future__ import annotations

from src.decision.algebra.verdict import conservatism
from src.decision.contracts.recommendation import Attribution
from src.decision.errors import AttributionIncompleteError


def attribute(nominated: str, outcomes) -> Attribution:
    """Every gate whose own effect reached the binding level (DN-13).

    ★ **Order-independent by construction**, not by a separate assertion: it is
    a filter over a set, and DN-6's commutativity test is what guarantees the
    level itself does not depend on order (DN-14).
    """
    outcomes = tuple(outcomes)
    if not outcomes:
        raise AttributionIncompleteError(
            "no gate outcomes to attribute. A composition with no gates is the "
            "identity-by-omission case DN-10 forbids"
        )
    level = max((conservatism(o.verdict_after) for o in outcomes),
                default=conservatism(nominated))
    binding = tuple(sorted(o.gate_id for o in outcomes
                           if conservatism(o.verdict_after) == level))
    if conservatism(nominated) == level and not binding:
        # Nothing moved the verdict: the nomination itself is the binding level.
        return Attribution(binding=(), binding_level=nominated)
    if not binding:
        raise AttributionIncompleteError(
            f"binding level {level} reached but no gate claims it — the attribution "
            f"would omit whatever actually bound (DN-13)"
        )
    level_name = next(o.verdict_after for o in outcomes
                      if conservatism(o.verdict_after) == level)
    return Attribution(binding=binding, binding_level=level_name)
