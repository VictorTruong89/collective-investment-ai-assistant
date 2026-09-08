"""RM-6…RM-9 — the weekly bias monitors (§7.2's Monitor table, AC-1.16, AC-1.17).

★ **Bias is invisible to repeat-runs**: *a consistently biased analyst is
perfectly consistent.* These four are the only instruments that can see it, and
each needs aggregation rather than repetition.
"""

from __future__ import annotations

from collections import Counter

from src.fundamental.monitor.registry import (
    OK,
    WARN,
    MonitorResult,
    not_yet_calibrated,
)

#: ⚠ **ADMITTED GUESSES** (CN-10). None was measured; each is a level at which a
#: reader should look, not a level at which something is known to be wrong.
BUY_BASE_RATE_CEILING = 0.60      # RM-6 — *an analyst that says BUY most of the time*
DEGENERACY_SPREAD_FLOOR = 2       # RM-7 — a rubric using fewer than 2 levels
THEME_SKEW_CEILING = 0.25         # RM-9 — verdict skew vs the universe base rate
MIN_N = 20                        # below this, every one of them is noise


def rm6_verdict_base_rate(verdicts) -> MonitorResult:
    """RM-6 — ★ *an analyst that says BUY most of the time is not discriminating.*

    *Publish the distribution beside the verdict.*
    """
    verdicts = list(verdicts)
    if len(verdicts) < MIN_N:
        return not_yet_calibrated("RM-6", n=len(verdicts))
    counts = Counter(verdicts)
    fractions = {k: v / len(verdicts) for k, v in sorted(counts.items())}
    status = WARN if fractions.get("BUY", 0.0) > BUY_BASE_RATE_CEILING else OK
    return MonitorResult("RM-6", status,
                         value={k: round(v, 6) for k, v in fractions.items()},
                         n=len(verdicts))


def rm7_dimension_dispersion(scores_by_dimension) -> MonitorResult:
    """RM-7 — the degeneracy check. ★ **RA-34's instrument.**

    ⚠ *If moat clusters at 7–8 for everything, the rubric has no resolving power
    and the score is noise wearing a number* — and *the fix is by rewriting
    criteria, never by asking the model to "use the full range"*.
    """
    counts = {d: len(set(v)) for d, v in sorted(scores_by_dimension.items())}
    total = sum(len(v) for v in scores_by_dimension.values())
    if total < MIN_N:
        return not_yet_calibrated("RM-7", n=total)
    degenerate = [d for d, distinct in counts.items()
                  if distinct < DEGENERACY_SPREAD_FLOOR]
    return MonitorResult("RM-7", WARN if degenerate else OK,
                         value={"distinct_levels_used": counts,
                                "degenerate": degenerate}, n=total)


def rm8_seat_disagreement(pairs) -> MonitorResult:
    """RM-8 — ★★ **the INV-014 health check**, and it reads backwards.

    ```
    INV-014 makes the two seats independent, so HEALTHY DISAGREEMENT IS
    EVIDENCE THE INDEPENDENCE IS REAL. Agreement drifting toward 100 % means
    either leakage or a shared bias — both worth knowing.
    ```

    ⚠ **This diagnostic exists BECAUSE of the architecture**, so a low number is
    not a defect to be fixed — it is the property being verified.
    """
    pairs = list(pairs)
    if len(pairs) < MIN_N:
        return not_yet_calibrated("RM-8", n=len(pairs))
    disagreed = sum(1 for thesis_v, quant_v in pairs if thesis_v != quant_v)
    rate = disagreed / len(pairs)
    # ⚠ WARN at BOTH ends. Near-total agreement suggests leakage; near-total
    # disagreement suggests one seat is inverted, and neither is "good".
    status = WARN if rate < 0.05 or rate > 0.95 else OK
    return MonitorResult("RM-8", status, value=round(rate, 6), n=len(pairs))


def rm9_theme_skew(verdicts_by_theme, universe_base_rate: float) -> MonitorResult:
    """RM-9 — ★ *separates the PM's deliberate concentration (M-2, fine) from the
    analyst's unconscious enthusiasm (not fine).*

    ⚠ M-2 makes concentration **the PM's choice**; it does not license the
    analyst to add to it unconsciously.
    """
    total = sum(len(v) for v in verdicts_by_theme.values())
    if total < MIN_N:
        return not_yet_calibrated("RM-9", n=total)
    skew = {}
    for theme, verdicts in sorted(verdicts_by_theme.items()):
        verdicts = list(verdicts)
        if not verdicts:
            continue
        rate = sum(1 for v in verdicts if v == "BUY") / len(verdicts)
        skew[theme] = round(rate - universe_base_rate, 6)
    worst = max((abs(v) for v in skew.values()), default=0.0)
    return MonitorResult("RM-9", WARN if worst > THEME_SKEW_CEILING else OK,
                         value=skew, n=total)
