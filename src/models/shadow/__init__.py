"""D-04 shadow trial — a refused model scored LIVE, never served (MT-64…MT-66).

★ After four fits on 2016–2026 the history is spent: every further change tuned on it
is one more draw. The only evidence that cannot be tuned is the future. A shadow trial
freezes one artifact, records its ranking every ≥ 21 trading days, grades each
snapshot 21 days later, and judges the pooled record by a criterion written down
before the first observation.

⚠ **Never on the card.** Nothing in D-08, D-09, D-12 or D-03 imports this package
(AC-4.46). Meeting the bar does not promote — `src.models.promote --approve` does.

    python -m src.models.shadow start <artifact_id>   # once
    python -m src.models.shadow record                # every ≥ 21 trading days
    python -m src.models.shadow score                 # any time
    python -m src.models.shadow status
"""
