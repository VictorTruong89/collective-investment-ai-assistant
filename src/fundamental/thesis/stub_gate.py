"""The B3 stub gate — a REAL `CT-1.4` emitter, not a mock (L3 BS-11, BS-27, BS-34).

```
BS-11: The stubs are real implementations of the contracts, not mocks.
A D-01 gate that always returns PASS is a legitimate B3 stub; one that
returns None and is special-cased downstream has already broken DN-10 —
THE IDENTITY MUST NOT BE REACHABLE BY OMISSION.
```

★ **Why a constant `PASS` rather than `NO_THESIS`.** §11.2's table maps *"no
thesis at all"* to `NO_THESIS`, which would be the honest status if D-01 had been
asked and had nothing. **B3 is a different situation: D-01 has not been built.**
Reporting `NO_THESIS` would say the analyst looked and found nothing; reporting
`PASS` with `produced_by_stub` set says the gate is not yet real. **The second is
the true statement**, and BS-27 requires it to appear in the RunManifest as well
so the record and the artifact agree.

⚠ **BS-34 is what stops this becoming D-15.** The grade block stays EMPTY. Every
field is `None`, so the card renders absence as absence — no invented `k`, no
invented confidence, no `stability_fraction: 1.0` that is literally true and
completely misleading. Combined with **BS-33** (`actionable: false`), the card
walks the whole pipeline without claiming to be a recommendation.
"""

from __future__ import annotations

from datetime import date

from src.fundamental.contracts.gate import PASS, GateVerdict, Grade

#: What replaces this, carried into the manifest so `stubs[].replaced_at` is
#: sourced from the stub itself rather than typed twice and allowed to drift.
#: ✏ 2026-10-06 (L1-reporting RP-53, L9 §10 C2): was the milestone `"B4.4"`, long
#: passed — D-01 IS built. The placeholder now stands for a decision, not a gap:
#: the daily run writes no thesis (Victor 2026-10-05, DX-153).
REPLACED_AT = "never in the daily run — theses are authored on demand (DX-153)"

GATE_ID = "thesis"

STUB_REASON = (
    "Placeholder thesis gate: the daily run writes no thesis — theses are "
    "authored on demand, by the fund manager's command (Victor 2026-10-05, "
    "DX-153) — so no verdict was formed for this name. This gate is a contract "
    "emitter, not an analyst; it grades nothing (L3 BS-11/BS-34)."
)


def stub_gate_verdict(ticker: str, as_of: date) -> GateVerdict:
    """A real `CT-1.4` that always PASSes and grades nothing.

    ★ It exercises the D-01 -> D-12 seam while that seam is still cheap to move,
    which is the whole purpose of B3 (**BS-10**).
    """
    return GateVerdict(
        gate_id=GATE_ID,
        ticker=ticker.upper(),
        as_of=as_of,
        status=PASS,
        reason=STUB_REASON,
        # ⚠ BS-34: empty, and deliberately so. Populating any of these would
        # manufacture a graded value out of a placeholder.
        grade=Grade(),
        thesis_version=None,
        thesis_as_of=None,
        produced_by_stub=REPLACED_AT,
    )
