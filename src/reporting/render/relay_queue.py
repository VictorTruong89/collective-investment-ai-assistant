"""D-09 §8 — the `RELAY QUEUE` block. RP-49, and D-01's RA-127/RA-128.

★ **`overdue` and `stale` are SEPARATE counts.** ⚠ *Not yet run* and *no longer
trusted* are different states, and **collapsing them hides the moment one became
the other** (D-01 RA-128, AC-1.82).

⚠ **RA-127: the system reports; it does not chase.** No nagging, no
auto-escalation, no re-prioritising a name because it was skipped. ★ *Skipping
is a decision SEAT-1 is entitled to make*, and the obligation here is the
override obligation — **make it visible and let it stand** (`vision.md` §2).
"""

from __future__ import annotations

#: Language a chasing renderer would reach for. ⚠ RP-49/RA-127 — the block
#: states counts and ages; it does not tell SEAT-1 what to do about them.
CHASING_VOICE = ("please run", "you must", "urgent:", "overdue!", "action required",
                 "don't forget", "reminder:", "asap")

TITLE = "RELAY QUEUE"


def render_relay_queue(report) -> str:
    """One block, four counts, no imperative.

    `report` is D-01's `QueueReport`, read through its JSON projection so the
    renderer holds no D-01 object (ST-9's direction, RP-30).
    """
    obj = report.to_json_obj() if hasattr(report, "to_json_obj") else dict(report)
    counts = obj["counts"]
    lines = [
        TITLE,
        f"as of {obj['as_of']}",
        "",
        f"  queued today   {counts['queued']:>3}   "
        + ", ".join(e["ticker"] for e in obj["queued"]),
        f"  returned       {counts['returned']:>3}   "
        + ", ".join(obj["returned"]),
        # ⚠ two lines, never one — RA-128.
        f"  overdue        {counts['overdue']:>3}   "
        + ", ".join(f"{e['ticker']} ({e['age_days']}d)" for e in obj["overdue"]),
        f"  stale          {counts['stale']:>3}   " + ", ".join(obj["stale"]),
        "",
        "  overdue = not yet run.  stale = no longer trusted.",
    ]
    return "\n".join(lines)


def assert_does_not_chase(text: str) -> None:
    """RP-49 / RA-127 — ⚠ *a queue that pesters is a system asserting authority
    it does not hold.*"""
    low = text.casefold()
    for phrase in CHASING_VOICE:
        if phrase in low:
            from src.shared.errors import PipelineError

            raise PipelineError(
                f"the relay-queue block says {phrase!r}. The system reports and "
                f"does not chase — skipping is SEAT-1's decision to make, and "
                f"D-09's obligation is to make it visible and let it stand "
                f"(RP-49, D-01 RA-127)"
            )
