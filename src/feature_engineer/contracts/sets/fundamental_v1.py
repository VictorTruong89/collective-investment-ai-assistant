"""`fundamental@v1` — §5.3's 45 `f_*` features over D-07 fundamentals.

★ **Declared from the build tables rather than retyped.** `build.py` already
holds the authoritative lists — `POINTWISE`, `CHANGES`, `TRENDS`, `SECTOR_Z` —
and a second hand-maintained copy here is FE-4's defect in the declaration layer:
*two implementations of one concept*. §5.3 itself records that the legacy list
*"is maintained by hand"* and shows the scar (`f_f_net_margin_trend_4`).

⚠ **Coverage is filer-dependent and that is accounting, not a defect.** Measured
2026-08-27 over a 120-day panel: **NVDA 37 of 45, WMT 32, JPM 18.** A bank has no
gross profit and no current/non-current split, so `f_gross_margin` and
`f_current_ratio` are null for JPM *correctly* — see **FE-37** for what that
costs the consumer.
"""

from __future__ import annotations

from src.feature_engineer.contracts.spec import FeatureContract, FeatureSpec
from src.feature_engineer.fundamental.build import (
    FEATURE_NAMES,
    PRICED,
)

_OWNER = "fundamental.build"

#: ⚠ **Ratios of signed quantities are unbounded in both directions.** A margin
#: can exceed 1 on a one-off gain and go deeply negative on a write-down;
#: declaring `[-1, 1]` would fire on real filings. CN-10 — an admitted absence
#: beats a fabricated threshold.
_UNBOUNDED = None

#: ★ Bounded by their own algebra, not by judgement.
_RANGES = {
    # ★ Bounded by construction: a weighted sum of three [0,1] components.
    "f_moat_quant_score": (0.0, 1.0),
    "f_piotroski_f": (0.0, 7.0),
    "f_piotroski_profitability": (0.0, 4.0),
    "f_piotroski_leverage": (0.0, 2.0),
    "f_piotroski_efficiency": (0.0, 1.0),
}

#: Features that are **level, not ratio** — declared so a consumer chooses them
#: knowingly (**FE-34**). `f_size_log_assets` is a size factor on purpose;
#: `f_fcf` is dollars and `f_fcf_margin` is its scale-invariant sibling.
LEVEL_FEATURES = ("f_fcf", "f_size_log_assets", "f_eps")

#: ⚠⚠ **A valuation multiple — an ANCHOR.** RA-14/RA-151: D-01's blind passes
#: may never see it, and D-02 publishes different sets to the two seats (§6.2 vs
#: §6.3) for exactly this reason.
ANCHOR_FEATURES = PRICED


def _spec(name: str, note: str, *, inputs=("fundamentals.ct_7_2",)) -> FeatureSpec:
    return FeatureSpec(
        name=name, formula_id=f"fundamental.{name}.v1", dtype="float64",
        inputs=inputs, owner_module=_OWNER, pit_class="C",
        null_policy="allow", range=_RANGES.get(name, _UNBOUNDED), note=note)


def _notes(name: str) -> str:
    if name in LEVEL_FEATURES:
        return ("★ A LEVEL feature, not a ratio — declared under FE-34 so a "
                "cross-sectional consumer chooses it knowingly.")
    if name in ANCHOR_FEATURES:
        return ("⚠⚠ A valuation multiple. It carries the price by construction, "
                "so RA-14/RA-151 keep it out of D-01's blind passes.")
    if name.endswith("_sector_z"):
        return ("z within (date, sector). ⚠ Null when the cell has fewer than "
                "three names — a z over two observations is ±0.707 by "
                "construction and says nothing about the company.")
    if name in _RANGES:
        return ("Piotroski component. ⚠ Null — never 0 — when a signal could not "
                "be computed: *we could not tell* and *it failed* are different "
                "facts, and only one belongs in a ranking (FE-14).")
    return "See `fundamental/ratios.py` and `fundamental/growth.py`."


FUNDAMENTAL_V1 = FeatureContract(
    name="fundamental",
    # ★★ **v2 — FE-2.** ⚠ *"A contract version is immutable once published.
    #   Changing any `formula_id`, range, or membership produces a NEW
    #   version."* Group C added `f_moat_quant_score` and
    #   `f_graham_number_ratio`, taking membership from **45 to 47**, and the
    #   version stayed at 1 — so two different feature sets shared one identity
    #   and `check_parity` compared only name and version.
    # ★★ **v3 — `DX-103` (2026-09-14).** `CANONICAL` gained fallback tags for
    #   `interest_expense`, `long_term_debt` and `current_debt`, so `f_interest_coverage`,
    #   `f_roic` and every feature built on them take values where they were null (MU:
    #   a decade). Same names and formulas, different inputs ⇒ a new version, or an
    #   artifact trained on v2 would pass parity against different numbers.
    version=3,
    created="2026-08-27",
    note=("§5.3's 45 f_* features plus Group C's 2. ⚠ Computed PER FILING and joined as-of "
          "afterwards — the reverse order silently nulls every multi-period "
          "feature, because a 120-day panel window holds three filings."),
    # ★ Straight from `build.FEATURE_NAMES` — FE-4 in the declaration layer: a
    #   second hand-maintained list is two implementations of one concept, and
    #   §5.3 shows the scar of one (`f_f_net_margin_trend_4`).
    features=tuple(_spec(name, _notes(name)) for name in FEATURE_NAMES),
)
