"""Running the rules — DE-12's classify-never-modify, in one place."""

from __future__ import annotations

import pandas as pd

from src.data_engine.validation.registry import (
    FLAG, REJECT, RuleRegistry, ValidationResult,
)


def run(df: pd.DataFrame, registry: RuleRegistry, *,
        flags_column: str = "quality_flags") -> ValidationResult:
    """Classify every row. The returned frames are new; `df` is untouched (PD-14).

    ⚠ A row that trips both a FLAG and a REJECT is **rejected**. The FLAG finding
    is still recorded, because "this row was also out of range" is information
    about the reject, and losing it would make the rejection look narrower than
    it was.
    """
    findings = []
    reject_mask = pd.Series(False, index=df.index)
    flag_ids: dict[int, list[str]] = {}

    for rule in registry.rules:
        fired = rule.predicate(df)
        if not isinstance(fired, pd.Series) or fired.dtype != bool:
            raise TypeError(
                f"rule {rule.rule_id} must return a boolean Series aligned to the "
                f"frame; got {type(fired).__name__}. A misaligned mask silently "
                f"validates the wrong rows (PD-12)"
            )
        fired = fired.fillna(False)          # PD-3: cosmetic only — a NaN comparison
                                             # is "did not fire", never a finding.
        if not fired.any():
            continue
        for idx in df.index[fired]:
            findings.append({"row": idx, "rule_id": rule.rule_id,
                             "severity": rule.severity,
                             "description": rule.description})
        if rule.severity == REJECT:
            reject_mask |= fired
        elif rule.severity == FLAG:
            for idx in df.index[fired]:
                flag_ids.setdefault(idx, []).append(rule.rule_id)

    accepted = df[~reject_mask].copy()
    accepted[flags_column] = [";".join(sorted(flag_ids.get(i, []))) for i in accepted.index]
    rejected = df[reject_mask].copy()
    return ValidationResult(
        accepted=accepted.reset_index(drop=True),
        rejected=rejected.reset_index(drop=True),
        findings=pd.DataFrame(findings, columns=["row", "rule_id", "severity",
                                                 "description"]),
    )
