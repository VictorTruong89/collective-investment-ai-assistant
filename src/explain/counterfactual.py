"""F4 `CT-4.3` / `D4` — *"what would change this?"*, in observables.

★★ **Exhaustive over a small DECLARED set, returning the sparsest flip.**

Each domain declares its actionable observables (gross margin, revenue growth,
rank, a gate input) with the step sizes worth probing. The search tries every
single change, then every pair, and stops at the first depth that flips the
verdict — so the answer is the **fewest** changes that work.

⚠ **Why not optimisation in feature space.** It produces exactly what `AC-4.8`
forbids — `f_gross_margin_z + 0.4σ` — and needs a differentiable model, which a
GBDT is not. ★ Sparsity, not optimality, is what makes a counterfactual usable:
*"gross margin holds above 42 % for two more quarters"* is monitorable; a six-way
simultaneous move is not, however optimal.

⚠ **An empty result is not an answer.** If nothing in the declared set flips the
verdict, that is reported explicitly (`AC-4.14`) — silence would read as *"no
counterfactual was looked for"*.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations

from src.explain.models import Change, Counterfactual

#: `D4` — how deep the exhaustive search goes. ⚠ An admitted limit (`CN-10`):
#: beyond pairs the statement stops being monitorable, so depth is capped by
#: usefulness rather than by cost.
MAX_SPARSITY = 2


@dataclass(frozen=True, slots=True)
class Observable:
    """A declared, monitorable quantity and the values worth probing."""

    name: str
    candidates: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class NoCounterfactual:
    """⚠ `AC-4.14` — an honest refusal, not an empty result."""

    reason: str
    searched: int
    max_sparsity: int


def search(
    current: Mapping[str, object],
    observables: Sequence[Observable],
    verdict_of: Callable[[Mapping[str, object]], str],
    *,
    as_of: str,
    universe_id: str,
    max_sparsity: int = MAX_SPARSITY,
) -> Counterfactual | NoCounterfactual:
    """The sparsest change to `current` that alters `verdict_of(current)`."""
    base = verdict_of(current)
    tried = 0
    for depth in range(1, max_sparsity + 1):
        for combo in combinations(observables, depth):
            for values in _product(o.candidates for o in combo):
                probe = dict(current)
                for obs, val in zip(combo, values, strict=True):
                    probe[obs.name] = val
                tried += 1
                new = verdict_of(probe)
                if new != base:
                    changes = tuple(
                        Change(observable=obs.name, from_value=current.get(obs.name),
                               to_value=val)
                        for obs, val in zip(combo, values, strict=True))
                    return Counterfactual(
                        statement=_state(changes, new), changes=changes,
                        flips_to=new, as_of=as_of, universe_id=universe_id)
    return NoCounterfactual(
        reason=(f"no change of up to {max_sparsity} declared observable(s) flips "
                f"{base!r}. ⚠ This is a finding, not an absence of one."),
        searched=tried, max_sparsity=max_sparsity)


def _product(pools):
    out = [[]]
    for pool in pools:
        out = [row + [v] for row in out for v in pool]
    return out


def _state(changes: tuple[Change, ...], flips_to: str) -> str:
    parts = [f"{c.observable} moves from {c.from_value} to {c.to_value}"
             for c in changes]
    return f"if {' and '.join(parts)}, the verdict becomes {flips_to}"
