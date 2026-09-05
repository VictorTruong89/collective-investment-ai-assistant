"""F9 `CT-9.1` — `ThesisSourcePort`. ⚠ Typing only (`CA-3`, `F1` `AC-1.10`).

★★ **The contract is what makes the two adapters substitutable**, not the type
signature. `F1`'s `MU`-71 % lesson: two adapters shared a signature and differed
in a guarantee nobody had written down. So the guarantees are stated here and
checked by one contract suite (`AC-9.1`).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

#: The five guarantees EVERY implementation owes. ⚠ Stated as data so the
#: contract suite can enumerate them rather than a reader having to remember.
CONTRACT = (
    "C1 every factual claim is bound to an evidence span, or explicitly unbound",
    "C2 a claim contradicting the pipeline's own data RAISES; never returned de-rated",
    "C3 confidence comes from the shared assess_confidence, never from the adapter",
    "C4 the returned Thesis carries provenance",
    "C5 an unknown ticker RAISES; an empty thesis is never returned",
)


@runtime_checkable
class ThesisSourcePort(Protocol):
    def author(self, ticker: str, as_of: object, context: Mapping) -> object: ...
