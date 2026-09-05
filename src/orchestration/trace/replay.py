"""F2 `CT-2.5` — replay, and what it does and does not prove (`D3`, `D5`).

★★ **What replay establishes:** given the **recorded external responses**, the
control flow and the deterministic computation reproduce.

⚠ **What it does NOT establish:** that a model would answer the same way again.
That is unknowable and is not what replay is for.

★ **`D3` — the verdict is named `REPRODUCED`, not `IDENTICAL`.** The verdict
travels into reports and the `MS-9` write-up, so its limit has to travel with it;
`PG-10` is the rule that a claim carries its subject's status, and a field named
*identical* is precisely the over-claim that rule exists to prevent.

⚠ **`D5` — the clock is the gap, not the RNG.** `RunManifest.seed` covers
`random.Random(seed)` (one module, explicitly seeded), and `uuid4()` only makes
`run_id` unique — which is recorded. But **43 wall-clock call sites across 8+
modules** are not covered. Those fields are excluded from comparison and
**listed in `excluded_fields`**: an invisible exclusion is a lie, and a blanket
"ignore all datetimes" would swallow a decision timestamped in the wrong ORDER,
which is a real bug.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.orchestration.trace.errors import IncompleteTrace, PayloadsExpired
from src.orchestration.trace.store import TraceStore

#: `D3` — stated on every report so a consumer cannot render the verdict alone.
SCOPE = "control flow and deterministic computation, given recorded external responses"

#: `D5` — wall-clock fields. ⚠ Explicit, never a pattern match on "looks like a date".
WALL_CLOCK_FIELDS = ("started_at", "ended_at", "written_at", "minted_at",
                     "latency_ms", "resolved_at", "_key")


@dataclass(frozen=True, slots=True)
class ReplayReport:
    """`CT-2.5`. ⚠ `verdict` is never rendered without `scope`."""

    run_id: str
    verdict: str                      # REPRODUCED | DIVERGED | UNREPLAYABLE
    scope: str = SCOPE
    excluded_fields: tuple[str, ...] = ()
    first_divergence: dict | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.verdict == "REPRODUCED" and self.first_divergence is not None:
            raise ValueError("first_divergence must be null when REPRODUCED (CT-2.5)")


class NetworkReachedError(Exception):
    """`AC-2.3` — ⚠ a replay that reaches the network has failed, by definition."""


def _comparable(record: dict, excluded: tuple[str, ...]) -> dict:
    return {k: v for k, v in record.items() if k not in excluded}


def replay(
    store: TraceStore,
    execute: Callable[[dict, Callable[[str], dict]], list[dict]],
    *,
    excluded_fields: tuple[str, ...] = WALL_CLOCK_FIELDS,
) -> ReplayReport:
    """Re-execute a recorded run, serving every external call from the recording.

    `execute` receives the recorded records and a `respond(call_id)` function; it
    must obtain **every** external result through `respond`. ⚠ A replay that
    reaches the network has failed — `respond` is the only door.
    """
    if store.status() == "INCOMPLETE":
        return ReplayReport(store.run_id, "UNREPLAYABLE",
                            reason="trace is INCOMPLETE — the run did not finish (AC-2.12)")
    try:
        recorded = list(store.read_all())
    except IncompleteTrace as exc:
        return ReplayReport(store.run_id, "UNREPLAYABLE", reason=str(exc))

    def respond(call_id: str) -> dict:
        return store.payload(call_id)

    try:
        produced = execute(recorded, respond)
    except PayloadsExpired as exc:
        # AC-2.15 — deleted, not lost. The reason names the date.
        return ReplayReport(store.run_id, "UNREPLAYABLE", reason=str(exc))

    # ⚠ strict=False deliberately: a LENGTH difference is itself a divergence
    # and is reported below with `field='record_count'`. Raising here would
    # turn a reportable DIVERGED into a crash.
    for i, (was, now) in enumerate(zip(recorded, produced, strict=False)):
        a, b = _comparable(was, excluded_fields), _comparable(now, excluded_fields)
        if a != b:
            field_name = next((k for k in a if a.get(k) != b.get(k)), "<missing>")
            return ReplayReport(
                store.run_id, "DIVERGED", excluded_fields=excluded_fields,
                first_divergence={"step_id": was.get("step_id"), "index": i,
                                  "field": field_name,
                                  "recorded": a.get(field_name),
                                  "replayed": b.get(field_name)})
    if len(produced) != len(recorded):
        return ReplayReport(
            store.run_id, "DIVERGED", excluded_fields=excluded_fields,
            first_divergence={"step_id": None, "index": min(len(produced), len(recorded)),
                              "field": "record_count",
                              "recorded": len(recorded), "replayed": len(produced)})
    return ReplayReport(store.run_id, "REPRODUCED", excluded_fields=excluded_fields)
