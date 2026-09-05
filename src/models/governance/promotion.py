"""D-04 §7 — the ONLY path to production. CT-4.3, MT-17…MT-20, MT-23, MT-46.

★ **MT-19: D-04 does not evaluate itself.** The gates are D-03's, run by D-03's
code, against D-03's protocol. This module *records* outcomes; it never produces
one.

⚠ **MT-23: a retrain is a promotion and passes the full gate.** *"It is only a
refresh" is how an unevaluated artifact reaches production.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from src.quant.gates.metric_gate import REQUIRED_GATES

PASS, FAIL, NOT_EVALUATED = "PASS", "FAIL", "NOT_EVALUATED"

#: ★ **Imported at the top, never re-declared.** MT-19 puts the gates in D-03;
#: a second list here is two owners for one idea, and it drifted the moment it
#: existed — D-04 required a `stability` gate D-03 never produced, and promotion
#: refused every artifact until the chain was run end to end. ⚠ **Absence is not
#: consent** (MT-18), and neither is disagreement about what was asked for.


@dataclass(frozen=True, slots=True)
class PromotionRecord:
    """CT-4.3 — append-only. ★ Every gate outcome is `PASS`."""

    artifact_id: str
    promoted_at: datetime
    promoted_by: str
    #: ★ MT-17 — **the D-03 `BacktestResult` id.** Production is reachable only
    #: through a record that carries one.
    backtest_result_id: str
    gate_outcomes: dict
    horizon_set_version: int
    contract_version: int
    supersedes: str = ""

    def to_json_obj(self) -> dict:
        return {"artifact_id": self.artifact_id,
                "promoted_at": self.promoted_at.isoformat(),
                "promoted_by": self.promoted_by,
                "backtest_result_id": self.backtest_result_id,
                "gate_outcomes": dict(self.gate_outcomes),
                "horizon_set_version": self.horizon_set_version,
                "contract_version": self.contract_version,
                "supersedes": self.supersedes}


def promote(artifact, *, backtest_result_id: str, gate_outcomes: dict,
            promoted_by: str, at: datetime, supersedes: str = "",
            required=REQUIRED_GATES) -> PromotionRecord:
    """MT-17/MT-18 — ★ **the only path**, and every required gate must say PASS.

    ⚠ **`NOT_EVALUATED` is not a pass** (D-03 QA-17). A gate that was never run
    is indistinguishable, from here, from one that was run and failed — and
    treating silence as consent is D-18(b)'s shape.
    """
    from src.models.errors import ModelError, NotEvaluatedError

    if not backtest_result_id:
        raise ModelError(
            f"{artifact.artifact_id}: promotion needs a D-03 BacktestResult id. "
            f"★ D-04 does not evaluate itself (MT-19); a promotion with no "
            f"evaluation is the gate skipped, not passed (MT-17)")

    not_passing = {g for g in required
                   if gate_outcomes.get(g, NOT_EVALUATED) != PASS}
    if not_passing:
        raise NotEvaluatedError(artifact.artifact_id, not_passing)

    return PromotionRecord(
        artifact_id=artifact.artifact_id, promoted_at=at,
        promoted_by=promoted_by, backtest_result_id=backtest_result_id,
        gate_outcomes=dict(gate_outcomes),
        horizon_set_version=artifact.manifest.horizon_set_version,
        contract_version=artifact.manifest.feature_contract.version,
        supersedes=supersedes)


@dataclass
class Registry:
    """§4 `governance/registry.py` — what is in production, and why.

    ⚠ **MT-25: the retrain cadence is stated HERE, not implicit in a cron
    entry.** *A model whose retrain is overdue is reported stale, never
    silently trusted.*
    """

    _production: dict = field(default_factory=dict)
    _records: list = field(default_factory=list)
    retrain_cadence: str = "first trading day of each month"

    def install(self, artifact, record: PromotionRecord) -> None:
        artifact.assert_loadable_for_production()          # MT-33
        key = (artifact.manifest.role, artifact.manifest.horizon_id)
        self._production[key] = artifact
        self._records.append(record)

    def production_artifact(self, role: str, horizon_id: str):
        """MT-33 — ★ a 1q artifact raises **at load**."""
        from src.models.errors import HorizonRoleError

        artifact = self._production.get((role, horizon_id))
        if artifact is None:
            raise HorizonRoleError(
                f"no production artifact for role={role!r} "
                f"horizon={horizon_id!r}. ⚠ There is no default model")
        artifact.assert_loadable_for_production()
        return artifact

    def incumbent_survives(self, role: str, horizon_id: str) -> bool:
        """MT-46 — ★ *a retrain that fails, or fails its gate, leaves the
        incumbent in place* and says so loudly. **Never a fallback to an
        ungated model.**"""
        return (role, horizon_id) in self._production

    def is_stale(self, role: str, horizon_id: str, *, as_of: date,
                 max_age_days: int = 45) -> bool:
        """MT-25 — overdue is **reported**, not silently trusted."""
        records = [r for r in self._records
                   if self._production.get((role, horizon_id))
                   and r.artifact_id == self._production[(role, horizon_id)].artifact_id]
        if not records:
            return True
        latest = max(r.promoted_at.date() for r in records)
        return (as_of - latest).days > max_age_days

    def to_json_obj(self) -> dict:
        return {"retrain_cadence": self.retrain_cadence,
                "production": {f"{r}:{h}": a.artifact_id
                               for (r, h), a in sorted(self._production.items())},
                "records": [r.to_json_obj() for r in self._records]}
