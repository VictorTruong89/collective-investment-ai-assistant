"""D-04 §6 — INV-4 as a GATE. CT-4.2, MT-5…MT-11, MT-42, MT-44.

```text
╔══════════════════════════════════════════════════════════════════╗
║  A GUARD THAT FILTERS IS NOT A GUARD THAT CHECKS.                ║
║                                                                  ║
║  Filtering answers "what can I score with?"                      ║
║  Checking answers  "am I allowed to score at all?"               ║
║                                                                  ║
║  The first always succeeds. That is the entire problem —         ║
║  it cannot fail, so it cannot warn.                              ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠ **The defect this closes (D-17).** `_select_features` filtered where it must
check; its empty-`feature_names` branch scored on *every remaining column*; and
`main_inference` fell back to 14 of 61 features under a name that read like the
model's own. ★ And the half a column-name check **cannot see**: the `f_*` merge
is `how="left"`, so an unmatched name keeps its row with all 47 fundamental
columns **present and entirely NaN**. The columns exist. The filter passes. The
GBDTs consume the NaNs natively and return an ordinary-looking score.
**Measured 2026-08-10: 7 of the 13 `practice_watchlist` names.**
"""

from __future__ import annotations

from dataclasses import dataclass, field

PASS, HALT = "PASS", "HALT"

#: MT-11 — a ticker below this stays in the ranking and **cannot be the
#: actionable pick** (F1 AC-1.15, INV-6). ⚠ ADMITTED GUESS (CN-10): the spec
#: names the rule and no number.
MIN_FEATURE_COVERAGE = 0.80


@dataclass(frozen=True, slots=True)
class ParityReport:
    """CT-4.2 — ★ **the gate, not a log.**"""

    artifact_id: str
    panel_id: str
    contract_match: bool
    missing: tuple[str, ...] = ()
    extra: tuple[str, ...] = ()
    #: ★ **A first-class field.** Present-but-all-NaN is the D-17 case and must
    #: be visible **without inference** (MT-7).
    nan_only: tuple[str, ...] = ()
    coverage_by_ticker: dict = field(default_factory=dict)
    anchor_match: bool = True
    verdict: str = PASS
    reasons: tuple[str, ...] = ()

    @property
    def below_coverage(self) -> tuple[str, ...]:
        """MT-11 — names that may stay in the ranking but not be the pick."""
        return tuple(sorted(
            t for t, c in self.coverage_by_ticker.items()
            if c.get("coverage_fraction", 0.0) < MIN_FEATURE_COVERAGE))

    def to_json_obj(self) -> dict:
        return {"artifact_id": self.artifact_id, "panel_id": self.panel_id,
                "contract_match": self.contract_match,
                "missing": list(self.missing), "extra": list(self.extra),
                "nan_only": list(self.nan_only),
                "coverage_by_ticker": dict(self.coverage_by_ticker),
                "anchor_match": self.anchor_match, "verdict": self.verdict,
                "reasons": list(self.reasons),
                "below_coverage": list(self.below_coverage)}


def check_parity(artifact, panel, *, contract, panel_id: str = "",
                 run_anchor: str | None = None, raise_on_halt: bool = True
                 ) -> ParityReport:
    """MT-6/MT-8 — ★ **once, before scoring, over the whole batch.**

    ⚠ Never per-row and never warn-and-continue: a check that runs inside the
    scoring loop has already let the first rows through.
    """
    from src.feature_engineer.contracts.panel import coverage
    from src.models.errors import AnchorMismatchError, ParityError

    reasons = []
    manifest = artifact.manifest

    # ── MT-6: contract-version EQUALITY. Not subset, not intersection.
    contract_match = (manifest.feature_contract.name == contract.name
                      and manifest.feature_contract.version == contract.version)
    if not contract_match:
        reasons.append(
            f"contract {manifest.feature_contract.name}@"
            f"{manifest.feature_contract.version} != panel "
            f"{contract.name}@{contract.version}")

    # ★★ FE-2's mechanical check. ⚠ *Measured 2026-08-27:* two artifacts, one
    #   with 59 features and one with 61, both declared
    #   `price_and_fundamental@v1` after Group C landed without a version bump —
    #   and a name-and-version comparison **waved it through**. The hash cannot
    #   be talked round: *"republishing v3 with a changed formula_id produces a
    #   different hash and is refused, whatever the file says."*
    declared_hash = getattr(manifest.feature_contract, "content_hash", "")
    if declared_hash and declared_hash != contract.content_hash:
        reasons.append(
            f"contract CONTENT differs: the artifact was fitted against "
            f"{declared_hash[:23]}… and this panel is {contract.content_hash[:23]}… "
            f"— same name and version, different membership (FE-2)")

    declared = list(artifact.feature_names)
    present = [c for c in panel.columns]
    missing = tuple(sorted(set(declared) - set(present)))
    extra = tuple(sorted(c for c in present
                         if c.startswith("f_") and c not in declared))

    # ── MT-7: NaN-but-present counts as MISSING. The half §6.1 was blind to.
    nan_only = tuple(sorted(c for c in declared
                            if c in panel.columns and not panel[c].notna().any()))

    if missing:
        reasons.append(f"missing {list(missing)}")
    if nan_only:
        reasons.append(f"present but entirely NaN: {list(nan_only)}")
    if extra:
        # ★ MT-10 — extra features WARN, and escalate to halt when the contract
        #   versions differ, because an extra column means a different contract.
        reasons.append(f"extra {list(extra)}"
                       + ("" if contract_match else " (contract differs — halt)"))

    # ── MT-42/MT-44: the anchor is part of the contract, not a footnote.
    anchor_match = True
    if run_anchor is not None:
        anchor_match = manifest.decision_anchor == run_anchor
        if not anchor_match:
            reasons.append(
                f"anchor {manifest.decision_anchor!r} != run {run_anchor!r}")

    halt = bool(missing or nan_only or not contract_match or not anchor_match
                or (extra and not contract_match))
    report = ParityReport(
        artifact_id=artifact.artifact_id, panel_id=panel_id,
        contract_match=contract_match, missing=missing, extra=extra,
        nan_only=nan_only, coverage_by_ticker=coverage(panel, contract),
        anchor_match=anchor_match, verdict=HALT if halt else PASS,
        reasons=tuple(reasons))

    if halt and raise_on_halt:
        if not anchor_match:
            raise AnchorMismatchError(manifest.decision_anchor, run_anchor)
        raise ParityError(artifact.artifact_id, "; ".join(reasons))
    return report


def assert_some_name_is_actionable(report: ParityReport, curated) -> tuple:
    """MT-11 — ★ *if **every** curated name is excluded, the run **raises**
    rather than picking one anyway.*"""
    from src.models.errors import ParityError

    excluded = set(report.below_coverage)
    usable = tuple(sorted(t for t in curated if t not in excluded))
    if curated and not usable:
        raise ParityError(
            report.artifact_id,
            f"every curated name is below {MIN_FEATURE_COVERAGE:.0%} feature "
            f"coverage. A ranking with no eligible pick does not pick one "
            f"anyway (MT-11, F1 AC-1.15, INV-6)")
    return usable
