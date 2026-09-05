"""D-01 §10B.3 — what reaches the cheap-tier LLM at all. RA-84.

★ **Everything the SEC has already typed is routed by the table** (RA-82). The
model sees only `7.01`/`8.01` — Regulation FD and "other events", *where the
genuinely unexpected lands, unstructured by design* — and news.
"""

from __future__ import annotations

from src.fundamental.errors import ResearchError

#: RA-84 — the only 8-K items whose meaning is not already declared by the form.
CHEAP_TIER_ITEMS = frozenset({"7.01", "8.01"})


def cheap_tier_queue(items) -> tuple:
    """The subset of a day's evidence a cheap-tier call may read (RA-84).

    ⚠ Passing a typed item here is not merely wasteful — it asks a model to
    classify what the form declares, **the reverse of AP-5** (RA-82).
    """
    queue = []
    for item in items:
        if item.kind == "news":
            queue.append(item)
            continue
        if item.item_code and item.item_code not in CHEAP_TIER_ITEMS:
            raise ResearchError(
                f"8-K item {item.item_code} reached the cheap tier. The SEC has "
                f"already assigned the code — route it by the table, never by an "
                f"LLM (RA-82, RA-84)"
            )
        queue.append(item)
    return tuple(queue)
