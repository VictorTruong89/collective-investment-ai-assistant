"""CT-5.2 Flag and the alert envelope D-12 transports (RK-18, DN-38)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: RK-30 / RK-36 / DN-38 — the tri-state D-12's `alerts_status` carries.
COMPLETE = "COMPLETE"


def unchecked(reason: str) -> str:
    """★ `UNCHECKED: <why>` — a first-class result, distinct from "no risk found".

    ⚠ **An exposure that could not be computed must never render as zero**
    (RK-36). Zero theme exposure and unmeasured theme exposure are opposite
    findings and would look identical. Same shape as D-07 **DE-35**, which is
    where the pattern is argued at length.
    """
    if not reason:
        raise ValueError(
            "UNCHECKED requires a reason. In a domain whose whole value is that "
            "silence means 'nothing found', a reasonless UNCHECKED collapses back "
            "into an all-clear (RK-30)"
        )
    return f"UNCHECKED: {reason}"


@dataclass(frozen=True, slots=True)
class Alert:
    """One LEVEL-2 notification. Crossed a reporting threshold; never a veto."""

    source: str
    level: int
    text: str
    as_of: date
    #: ★ Constants, present so the contract states no other value exists.
    #: `blocking` is INV-026 / RK-2; `suppressible` is INV-021 / RK-18.
    blocking: bool = False
    suppressible: bool = False

    def __post_init__(self) -> None:
        if self.blocking or self.suppressible:
            raise ValueError(
                "alerts are never blocking and never suppressible. D-05 cannot be "
                "silenced and cannot stop anything — that combination is the whole "
                "character of the domain (INV-021, INV-026)"
            )

    def to_json_obj(self) -> dict:
        return {"source": self.source, "level": self.level, "text": self.text,
                "as_of": self.as_of.isoformat(),
                "blocking": self.blocking, "suppressible": self.suppressible}


@dataclass(frozen=True, slots=True)
class AlertSet:
    """What D-05 hands D-12: the alerts **and** whether a complete pass produced them.

    ★ **DN-38.** An empty `alerts` with no status is an all-clear the risk desk
    never made. `status` is `COMPLETE` only after WF-R1 finished (**RK-30**).
    """

    alerts: tuple[Alert, ...]
    status: str

    def __post_init__(self) -> None:
        if self.status != COMPLETE and not self.status.startswith("UNCHECKED: "):
            raise ValueError(
                f"alert status {self.status!r} is neither COMPLETE nor "
                f"'UNCHECKED: <reason>' (DN-38, RK-36)"
            )
        if self.alerts and self.status != COMPLETE:
            # RK-30: alerts are emitted ONLY from a complete pass. A partial set
            # reads as an all-clear on everything absent.
            raise ValueError(
                "alerts were emitted from an incomplete pass. A partial run that "
                "emits three of five alerts has told the reader the other two "
                "categories are clear (RK-30)"
            )
