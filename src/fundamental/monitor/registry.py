"""CT-1.3 — the monitor report. ★ EVERY `RM-n` appears (RA-30, RA-136, AC-1.28).

```
A monitor that cannot yet be computed reports "not yet calibrated (N=…)",
never a placeholder value and never silence. This is DE-35 applied to
metrics: ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE.
```

★★ **RA-136 adds the third status this slice found missing.** `not_yet_calibrated`
**promises the number is coming**. RM-1's *sampling* half can never be computed on
this tier — `claude-opus-5` rejects `temperature` (GW-8a), so *the sampling probe
was never measuring a property anyone controlled* (GW-10) — and reporting it as
`not_yet_calibrated (N=0)` tells a reader to wait for a number that will not arrive.
"""

from __future__ import annotations

from dataclasses import dataclass

OK, WARN, FAIL = "ok", "warn", "fail"
NOT_YET_CALIBRATED = "not_yet_calibrated"
#: ★ RA-136 — structurally impossible, not merely absent. Carries **why**.
NOT_MEASURABLE = "not_measurable"
STATUSES = (OK, WARN, FAIL, NOT_YET_CALIBRATED, NOT_MEASURABLE)

#: §7.4's table. ⚠ **The set is closed and the report must cover all of it** —
#: a missing RM is a defect, not a pass, exactly as a missing class is in
#: `CT-7.7` (D-07 DE-35) and a missing dimension is in a scorecard (RA-52).
RM_IDS = tuple(f"RM-{n}" for n in range(1, 17))

#: Cadence, from §7.4. Recorded so a reader of a report can tell *"absent because
#: it runs weekly"* from *"absent because nobody wired it"* — which is the same
#: distinction RA-136 draws one level down.
CADENCE = {
    "RM-1": "every run", "RM-2": "every run", "RM-3": "every run",
    "RM-4": "on every prompt change", "RM-5": "on every model-tier change",
    "RM-6": "weekly", "RM-7": "weekly", "RM-8": "weekly", "RM-9": "weekly",
    "RM-10": "every run", "RM-11": "every run",
    "RM-12": "monthly", "RM-13": "monthly", "RM-14": "monthly",
    "RM-15": "every run", "RM-16": "monthly",
}


@dataclass(frozen=True, slots=True)
class MonitorResult:
    """One `RM-n`. ★ A value **or** a stated reason it has none — never silence."""

    rm_id: str
    status: str
    value: object = None
    n: int = 0
    reason: str = ""

    def __post_init__(self) -> None:
        if self.rm_id not in RM_IDS:
            raise ValueError(f"{self.rm_id!r} is not one of §7.4's {RM_IDS}")
        if self.status not in STATUSES:
            raise ValueError(
                f"status {self.status!r} is not one of {STATUSES}. ★ RA-136 makes "
                f"'never computable' distinct from 'not computed yet'"
            )
        if self.status == NOT_MEASURABLE and not self.reason:
            raise ValueError(
                f"{self.rm_id}: not_measurable requires a reason. ⚠ Without one it "
                f"is indistinguishable from not_yet_calibrated, and the difference "
                f"is whether a reader should ever expect a number (RA-136)"
            )
        if self.status in (OK, WARN, FAIL) and self.value is None:
            raise ValueError(
                f"{self.rm_id}: status {self.status!r} with no value is a "
                f"placeholder, which RA-30 forbids"
            )

    @property
    def renders_as(self) -> str:
        """What the monitor page shows — RA-21's shape, generalised to every RM."""
        if self.status == NOT_YET_CALIBRATED:
            return f"not yet calibrated (N={self.n})"
        if self.status == NOT_MEASURABLE:
            return f"not measurable — {self.reason}"
        return str(self.value)

    def to_json_obj(self) -> dict:
        return {"rm_id": self.rm_id, "status": self.status, "value": self.value,
                "n": self.n, "reason": self.reason,
                "cadence": CADENCE[self.rm_id], "renders_as": self.renders_as}


@dataclass(frozen=True, slots=True)
class MonitorReport:
    """CT-1.3. ⚠ **Every RM appears** — a missing one is a defect, not a pass."""

    run_id: str
    results: tuple[MonitorResult, ...]

    def __post_init__(self) -> None:
        seen = {r.rm_id for r in self.results}
        missing = [rm for rm in RM_IDS if rm not in seen]
        if missing:
            raise ValueError(
                f"monitor report omits {missing}. Every RM-n appears as a value or "
                f"an explicit decline — a missing monitor reads as a passing one, "
                f"which is DE-35's defect applied to metrics (RA-30, AC-1.28)"
            )
        if len(seen) != len(self.results):
            raise ValueError("duplicate RM ids in one report")
        object.__setattr__(self, "results",
                           tuple(sorted(self.results,
                                        key=lambda r: int(r.rm_id.split("-")[1]))))

    def get(self, rm_id: str) -> MonitorResult:
        for r in self.results:
            if r.rm_id == rm_id:
                return r
        raise KeyError(rm_id)

    @property
    def failing(self) -> tuple[MonitorResult, ...]:
        """§7.4 — *non-zero fails the run* for RM-10 and RM-15."""
        return tuple(r for r in self.results if r.status == FAIL)

    def to_json_obj(self) -> dict:
        return {"run_id": self.run_id,
                "monitors": [r.to_json_obj() for r in self.results]}


def not_yet_calibrated(rm_id: str, n: int = 0) -> MonitorResult:
    """RA-30 — *"ask again when N is larger"*."""
    return MonitorResult(rm_id, NOT_YET_CALIBRATED, n=n)


def not_measurable(rm_id: str, reason: str) -> MonitorResult:
    """★ RA-136 — *"never"*, with the reason. Distinct from the above."""
    return MonitorResult(rm_id, NOT_MEASURABLE, reason=reason)
