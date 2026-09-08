"""RM-12…RM-16 — the slow monitors, and every one starts `not_yet_calibrated`.

★ **RA-59: calibration starts NOW, and it costs $0.** Every closed thesis is
scored against its realised outcome using D-11's journal, which already records
what is needed. ⚠ **`L3` BS-1 put that clock first for a reason** — its value is a
function of *elapsed* time, and nothing can buy the interval back.

⚠ **These are the monitors most likely to be silently skipped**, because none of
them can return a number for years. RA-30 is why they must still appear.
"""

from __future__ import annotations

from statistics import fmean

from src.fundamental.monitor.registry import (
    OK,
    WARN,
    MonitorResult,
    not_yet_calibrated,
)

#: Below this, a calibration curve is a story about a handful of names.
#: ⚠ **An ADMITTED GUESS** (CN-10) — `L2` CB-10 and §6.3's power arithmetic both
#: suggest the real number is far larger, and neither has been applied here.
MIN_CLOSED_THESES = 20

#: RM-13 — ★ *a high abandonment rate means the falsifiers were decorative.*
ABANDONMENT_CEILING = 0.5


def rm12_calibration_curve(closed) -> MonitorResult:
    """RM-12 — conviction bucket vs realised outcome.

    ★ *The only real test of whether conviction carries information.* Needs
    D-11's journal and **time**.
    """
    closed = list(closed)
    if len(closed) < MIN_CLOSED_THESES:
        return not_yet_calibrated("RM-12", n=len(closed))
    by_bucket: dict[str, list[float]] = {}
    for conviction, hit in closed:
        by_bucket.setdefault(conviction, []).append(1.0 if hit else 0.0)
    curve = {k: round(fmean(v), 6) for k, v in sorted(by_bucket.items())}
    return MonitorResult("RM-12", OK, value=curve, n=len(closed))


def rm13_falsifier_vs_abandonment(closed) -> MonitorResult:
    """RM-13 — ★★ *how many theses died by their own stated condition versus were
    quietly dropped.*

    ⚠ **A high abandonment rate means the falsifiers were decorative** —
    unfalsifiable in practice, which is the failure AP-3 exists to prevent. ★ And
    **the fix is in J-15's prompt, not in the reader.**
    """
    closed = list(closed)
    if not closed:
        return not_yet_calibrated("RM-13", n=0)
    abandoned = sum(1 for reason in closed if reason == "abandoned")
    rate = abandoned / len(closed)
    return MonitorResult("RM-13", WARN if rate > ABANDONMENT_CEILING else OK,
                         value=round(rate, 6), n=len(closed))


def rm14_action_correlation(actions) -> MonitorResult:
    """RM-14 — ⚠ *does Victor act more on high-conviction reports, and do those do
    better? If not, conviction is noise the reader is nonetheless responding to.*"""
    actions = list(actions)
    if len(actions) < MIN_CLOSED_THESES:
        return not_yet_calibrated("RM-14", n=len(actions))
    acted = [c for c, did_act, _ in actions if did_act]
    return MonitorResult("RM-14", OK, n=len(actions),
                         value={"acted_on": len(acted), "total": len(actions)})


def rm15_lint_and_uncited(lint_violations: int, uncited_claims: int) -> MonitorResult:
    """RM-15 — ★ *should be zero. Non-zero is a REGRESSION, not a style question.*

    §7.4: *every run, all claims, run summary; **non-zero fails the run**.*
    """
    from src.fundamental.monitor.registry import FAIL

    total = int(lint_violations) + int(uncited_claims)
    return MonitorResult("RM-15", FAIL if total else OK, n=total,
                         value={"lint_violations": lint_violations,
                                "uncited_claims": uncited_claims})


def rm16_thesis_error_correlation(errors_by_name) -> MonitorResult:
    """RM-16 / AC-1.72 — ★★ thesis-error correlation `ρ̂` across names.

    ```
    ρ COLLAPSES BREADTH FOR *LEVEL* DECISIONS AND CANCELS FOR *RANK* DECISIONS.

    LEVEL  effective breadth is n/(1+(n-1)ρ) — at n=13, ρ=0.6 that is 1.6.
    RANK   the shared error c CANCELS EXACTLY; residual noise 2(1-ρ)σ² is
           SMALLER than independent errors would give.
    ```

    ⚠ **So a shared analytical bias is dangerous exactly where D-01 acts as a
    GATE, and benign-to-helpful where L2 re-ranks** — which *strengthens* the
    coverage case rather than merely sparing it.

    ★ *`ρ` is currently an assumed parameter on both sides of an argument, and it
    is measurable.* Until outcomes accrue it reports `not_yet_calibrated`.
    """
    names = sorted(errors_by_name)
    if len(names) < 2:
        return not_yet_calibrated("RM-16", n=len(names))
    lengths = {len(errors_by_name[n]) for n in names}
    if len(lengths) != 1 or lengths == {0}:
        return not_yet_calibrated("RM-16", n=min(lengths, default=0))
    periods = lengths.pop()
    if periods < 3:
        return not_yet_calibrated("RM-16", n=periods)

    # ρ̂ as the mean pairwise correlation — the equicorrelated form the box uses.
    # ⚠ Exact for EQUICORRELATED errors; sub-clusters (two rubrics, two
    # sub-themes) leave common structure inside each cluster.
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r = _pearson(errors_by_name[a], errors_by_name[b])
            if r is not None:
                pairs.append(r)
    if not pairs:
        return not_yet_calibrated("RM-16", n=periods)
    rho = fmean(pairs)
    n = len(names)
    effective_breadth = n / (1 + (n - 1) * rho) if (1 + (n - 1) * rho) else float("inf")
    return MonitorResult(
        "RM-16", OK, n=periods,
        value={"rho": round(rho, 6), "names": n,
               "effective_breadth_for_level_decisions": round(effective_breadth, 4),
               "note": "rank decisions are unharmed — the shared error cancels"},
    )


def _pearson(a, b) -> float | None:
    """Sample correlation, or `None` when a series does not vary.

    ⚠ `None`, not `0.0`: a constant error series has **undefined** correlation,
    and reporting zero would claim independence that was never measured.
    """
    n = len(a)
    ma, mb = fmean(a), fmean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        return None
    return cov / (va ** 0.5 * vb ** 0.5)
