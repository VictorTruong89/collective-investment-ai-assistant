"""D-04 §9 — scoring. CT-4.4, MT-26…MT-29, MT-5.

★★ **MT-5: there is no inference-side feature builder.** Inference calls
**D-02's `build_panel()`** with the artifact's recorded contract version.
⚠ *A second code path **is** the INV-4 violation, whether or not it currently
agrees* — and `main_inference._build_inference_features` is that second path,
which INV-4 currently names as its own reference implementation.

★ **MT-28: `rank_score` is an ORDERING, not a verdict.** It carries no
BUY/HOLD/SELL and no conviction (L0 §3.1, INV-014).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd


@dataclass(frozen=True, slots=True)
class ScoreResult:
    """CT-4.4 — what an inference run records."""

    artifact_id: str
    panel_id: str
    as_of: date
    adj_as_of: date
    scores: dict
    calendar_check_id: str = ""
    parity_verdict: str = "PASS"
    excluded: tuple[str, ...] = ()

    def ranked(self) -> tuple[tuple[str, float], ...]:
        """★ An ordering. Ties break on ticker so the ranking is deterministic
        (MT-26, INV-2) — a ranking whose ties depend on dict order is not."""
        return tuple(sorted(self.scores.items(), key=lambda kv: (-kv[1], kv[0])))

    def to_json_obj(self) -> dict:
        return {"artifact_id": self.artifact_id, "panel_id": self.panel_id,
                "as_of": self.as_of.isoformat(),
                "adj_as_of": self.adj_as_of.isoformat(),
                "calendar_check_id": self.calendar_check_id,
                "parity_verdict": self.parity_verdict,
                "ranked": [{"ticker": t, "rank_score": s} for t, s in self.ranked()],
                "excluded": list(self.excluded)}


def score(artifact, panel: pd.DataFrame, *, contract, as_of: date,
          adj_as_of: date, run_anchor: str, panel_id: str = "",
          calendar_check_id: str = "") -> ScoreResult:
    """MT-8/MT-29 — ★ parity runs **once, before scoring**; it halts, never
    degrades to a partial score."""
    from src.models.governance.parity import (
        MIN_FEATURE_COVERAGE, check_parity,
    )

    artifact.assert_loadable_for_production()               # MT-33
    report = check_parity(artifact, panel, contract=contract, panel_id=panel_id,
                          run_anchor=run_anchor)            # raises on HALT

    features = list(artifact.feature_names)
    latest = (panel.sort_values("date").groupby("ticker", sort=True).tail(1)
              .set_index("ticker"))
    raw = artifact.estimator.predict(latest[features])
    scores = {t: float(v) for t, v in zip(latest.index, raw)}

    # ⚠ MT-11 — below-coverage names STAY in the ranking; they simply cannot be
    #   the actionable pick. Dropping them would change the cross-section the
    #   ranking is computed over.
    excluded = tuple(sorted(
        t for t, c in report.coverage_by_ticker.items()
        if c.get("coverage_fraction", 0.0) < MIN_FEATURE_COVERAGE))
    return ScoreResult(artifact_id=artifact.artifact_id, panel_id=panel_id,
                       as_of=as_of, adj_as_of=adj_as_of, scores=scores,
                       calendar_check_id=calendar_check_id,
                       parity_verdict=report.verdict, excluded=excluded)
