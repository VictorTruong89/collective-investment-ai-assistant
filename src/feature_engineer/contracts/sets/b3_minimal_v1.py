"""`b3_minimal@v1` — the walking skeleton's contract (L3 BS-10).

★ **One feature is a complete contract, not a placeholder for one.** BS-10 says
B3 exercises every domain boundary and nothing deep; a contract with one
FeatureSpec exercises FE-1…FE-6 exactly as a contract with sixty-one does, and
it does so while the seams are still cheap to move.

⚠ **Declared in Python, not YAML, and that is a departure from §5.1's
`contracts/sets/*.yaml`.** The reason is FE-2: immutability is enforced on the
CONTENT HASH, and a Python literal is diffed by git and typed by the dataclass,
where a YAML file adds a parser and a schema between the declaration and the
check. When the set grows past a handful, YAML earns its keep; at one feature it
would only add a way to be wrong. Recorded in the blueprint as a decision.
"""

from __future__ import annotations

from src.feature_engineer.contracts.spec import FeatureContract, FeatureSpec
from src.feature_engineer.technical.momentum import (
    FORMULA_ID,
    LOOKBACK_SESSIONS,
    VOL_FORMULA_ID,
    VOL_WINDOW_SESSIONS,
)

B3_MINIMAL_V1 = FeatureContract(
    name="b3_minimal",
    version=1,
    created="2026-08-23",
    note=(
        f"L3 B3 walking skeleton. One feature, {LOOKBACK_SESSIONS}-session lookback "
        f"chosen to match HorizonSet v1's h1m production horizon (CT-3.1)."
    ),
    features=(
        FeatureSpec(
            name="mom_21",
            formula_id=FORMULA_ID,
            dtype="float64",
            # ★ FE-33: these map to CT-7.1 columns explicitly. `price.adj_open` IS
            # `adj_open_minor` + `adj_open_currency` — the two contracts used
            # different names for the same column and neither said so until v0.3.0.
            inputs=("price.adj_open",),
            owner_module="technical.momentum",
            pit_class="C",          # adjusted prices are restated data (§5A.4)
            null_policy="allow",    # insufficient history is null, never 0.0
            # ⚠ No range. A 21-session return is unbounded above and bounded at
            # −1 only if a price can reach zero. Declaring [−1, 5] would be an
            # invented bound that fires on a real 6x move — CN-10: an admitted
            # absence beats a fabricated threshold.
            range=None,
            note="adj_open(t)/adj_open(t-21) - 1; both ends on the same field (QA-71)",
        ),
        FeatureSpec(
            name="vol_21",
            formula_id=VOL_FORMULA_ID,
            dtype="float64",
            inputs=("price.adj_open",),
            owner_module="technical.momentum",
            pit_class="C",
            null_policy="allow",
            # A standard deviation is non-negative by construction, and 5.0 daily
            # (500 %) is far outside anything a listed equity produces — so the
            # upper bound catches a units error rather than a market. ⚠ An
            # ADMITTED GUESS as a bound; the lower bound is arithmetic (CN-10).
            range=(0.0, 5.0),
            note=(
                f"sd of {VOL_WINDOW_SESSIONS} open-to-open log returns, ddof=1. "
                f"Present because D-03's ranked_quantity is DENORMALISED (QA-58) "
                f"and a volatility computed inside D-03 would be a derived number "
                f"outside D-02 (FE-4)."
            ),
        ),
    ),
)
