"""The plain-text rendering — diffable, greppable, permanent (RP-33).

★ **Retained, not replaced.** HTML is what a human reads; markdown is what
**diffs, greps and survives** — two days' cards compare as text, and it is the
format most likely to still open in ten years. Both are archived (RP-24).
"""

from __future__ import annotations

from src.reporting.render.classes import GLYPH, LABEL


def render_markdown(card) -> str:
    """Deterministic: same card, same bytes (RP-28)."""
    lines = [f"# {card.ticker} — discipline card", ""]
    lines.append(f"**as of {card.as_of.isoformat()}**")
    lines.append("")

    if not card.actionable:
        # RP-45's shape: a run that did not produce a recommendation renders as
        # itself. ⚠ Above the content, so it cannot be skimmed past.
        lines += [
            "> ## ⚠ NOT ACTIONABLE", ">",
            f"> {card.not_actionable_reason}", "",
        ]

    # RP-15 — the falsifier renders ABOVE the verdict. Ordering is an argument.
    lines += ["## What would prove this wrong", "", card.falsifier, ""]

    lines += ["## Fields", "",
              "| field | value | reliability | source | as of |",
              "|---|---|---|---|---|"]
    for f in card.fields:
        lines.append(
            f"| {f.field} | {_fmt(f.value)} | {GLYPH[f.reliability]} "
            f"{LABEL[f.reliability]} | {f.source} | {f.as_of.isoformat()} |"
        )
    lines.append("")

    # RP-17 — mandatory and non-collapsible.
    lines += ["## Data gaps", ""]
    lines += [f"- {g}" for g in card.data_gaps] or ["- none"]
    lines.append("")

    # RP-47 — the risk channel says whether anybody looked.
    lines += ["## Risk", "", f"- status: {card.alerts_status}", ""]
    # ★ RP-57 — the flag pass, under its own label, never merged into the status.
    lines += [f"- {ln}" for ln in card.flag_lines] + ([""] if card.flag_lines else [])

    if card.stubs:
        lines += ["## Stubs in this run", ""]
        lines += [f"- {s['domain']} `{s['job']}`: {s['behaviour']} "
                  f"(replaced at {s['replaced_at']}, {s['rule']})" for s in card.stubs]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _fmt(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "—"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)
