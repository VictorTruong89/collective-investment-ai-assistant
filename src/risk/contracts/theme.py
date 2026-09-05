"""D-05 CT-5.3 — the theme taxonomy. RK-6, RK-7, RK-37.

★ **The artifact `THEME_REPORT_THRESHOLD_PCT` is measured against.** ⚠ *A
threshold on an undefined set is unenforceable, and the one threshold M-2
explicitly calls out is the one with no definition behind it* (§5.1).

★ **RK-37: D-02 publishes SECTOR; D-05 resolves THEME.** For D-02 to label a
theme it would have to know this taxonomy, and **FE-21 forbids D-02 importing an
analytical domain**. Theme membership is *a judgement call about what counts* —
*is `ENB` in the AI theme because it powers datacentres?* — and a judgement
belongs on a seat, not on neutral ground.
"""

from __future__ import annotations

from dataclasses import dataclass

UNCLASSIFIED = "unclassified"


@dataclass(frozen=True, slots=True)
class Theme:
    """One theme: a sector rule plus the two ticker lists that are the judgement."""

    theme_id: str
    sectors: tuple[str, ...] = ()
    #: ★ The judgement, isolated and named. A reader must be able to see it
    #: answered rather than infer it from an aggregate.
    included: tuple[str, ...] = ()
    excluded: tuple[str, ...] = ()

    def covers(self, *, symbol: str, sector: str) -> bool:
        if symbol in self.excluded:
            return False
        return symbol in self.included or sector in self.sectors

    def to_json_obj(self) -> dict:
        return {"theme_id": self.theme_id, "sectors": list(self.sectors),
                "included": list(self.included), "excluded": list(self.excluded)}


@dataclass(frozen=True, slots=True)
class ThemeTaxonomy:
    """CT-5.3 — declared data, versioned, with a stated membership rule (RK-6)."""

    taxonomy_version: str
    membership_rule: str
    themes: tuple[Theme, ...]

    def __post_init__(self) -> None:
        from src.risk.errors import NoTaxonomyError

        if not self.taxonomy_version:
            raise NoTaxonomyError("a taxonomy with no version cannot be cited")
        if not self.membership_rule.strip():
            raise NoTaxonomyError(
                "a taxonomy with no stated membership rule is the free-text "
                "field RK-6 exists to replace")
        if not self.themes:
            raise NoTaxonomyError("a taxonomy with no themes classifies nothing")

    def resolve(self, *, symbol: str, sector: str) -> str:
        """RK-7 — ★ a position matching none is `unclassified`, **never dropped**.

        ⚠ Silently dropping it would understate the very concentration being
        tracked (DE-35's shape).
        """
        for theme in self.themes:
            if theme.covers(symbol=symbol, sector=sector):
                return theme.theme_id
        return UNCLASSIFIED

    def to_json_obj(self) -> dict:
        return {"taxonomy_version": self.taxonomy_version,
                "membership_rule": self.membership_rule,
                "themes": [t.to_json_obj() for t in self.themes]}


#: ★ **`themes.v1` — the declaration QK-2 asked for**, closed 2026-08-25.
#: ⚠ The ticker lists are the judgement and are reviewed as such; the sector
#: rule is only the mechanism. Bumping the version is required for **any**
#: membership change — adding a ticker to a theme is an analytical change,
#: exactly as adding a column to D-01's sector file is (RA-100, one domain over).
THEMES_V1 = ThemeTaxonomy(
    taxonomy_version="themes.v1",
    membership_rule=(
        "A position is in a theme when its D-02 sector is in the theme's "
        "`sectors` AND its analysis_symbol is not in `excluded`, OR its "
        "analysis_symbol is in `included`. Ticker lists are the JUDGEMENT and "
        "are reviewed as such; the sector rule is the mechanism."
    ),
    themes=(
        Theme(theme_id="ai_semiconductor",
              sectors=(),
              # ⚠ Deliberately NOT `sectors=("Information Technology",)`: that
              # would sweep in every software name and make the 40 % threshold
              # a measure of the sector rather than of M-2's actual bet.
              included=("NVDA", "MU", "AMD", "AVGO", "TSM", "ASML", "INTC",
                        "SNDK", "LRCX", "AMAT", "KLAC", "MRVL", "TER")),
    ),
)
