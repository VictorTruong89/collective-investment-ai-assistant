"""CT-3.4 — the Nomination, D-03's production output (QA-119…QA-122).

> ⚠ *"D-03's three contracts covered configuration, evaluation and provenance.
> **The thing D-03 actually produces every day had no contract at all.**"*

Four rules shape this type, and each rejects a shorter version of it:

  **QA-119** `ranked_quantity` is the DENORMALISED return, and `z` travels
  beside it — publishing only `z` invites ranking on the normalised quantity.
  **QA-120** `nominating_horizon` is always `h1m`; `h1q` may not appear at all.
  **QA-121** `universe_n` and `model_artifact_id` are required.
  **QA-122** `candidates` is a **list**, ordered by rank — a contract that emits
  only rank 1 makes `k_cov >= 2` unimplementable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.quant.errors import NominationContractError


@dataclass(frozen=True, slots=True)
class Candidate:
    ticker: str
    rank: int
    ranked_quantity: float
    z: float


@dataclass(frozen=True, slots=True)
class Nomination:
    as_of: date
    run_id: str
    decision_anchor: str
    horizon_set: tuple[str, int]          # (name, version)
    nominating_horizon: str
    universe_n: int
    model_artifact_id: str
    candidates: tuple[Candidate, ...]
    delayed_by: tuple[str, ...] = ()
    vetoed_by: tuple[str, ...] = ()
    research_only: tuple[str, ...] = ()
    #: ★★ QA-125 — names barred from nomination, **with their reasons**.
    #:
    #: ⚠ `delayed_by` and `vetoed_by` are about HORIZONS (CT-3.1's arbitration);
    #: this is about NAMES, and conflating them would put a ticker where a
    #: horizon id belongs. ★ Excluded rather than silently dropped, so a reader
    #: can tell a name that was **beaten** from one that was **barred** —
    #: DE-13's rule one domain over.
    excluded: tuple[dict, ...] = ()

    def __post_init__(self) -> None:
        if self.nominating_horizon != "h1m":
            # QA-120: h1m is the ONLY nominating horizon (CT-3.1's arbitration).
            raise NominationContractError(
                f"nominating_horizon is {self.nominating_horizon!r}; only 'h1m' may "
                f"produce the daily pick (QA-47, QA-120, INV-6)"
            )
        if "h1q" in (self.nominating_horizon, *self.delayed_by, *self.vetoed_by):
            # ★ Rejected, not ignored. h1q is research-only and must never reach a
            # human artifact — silently dropping it would let it back in later.
            raise NominationContractError(
                "h1q is research_only and may not appear in a Nomination consumed by "
                "D-12 at all (QA-120)"
            )
        if not self.model_artifact_id:
            raise NominationContractError(
                "model_artifact_id is required — a nomination that cannot be traced "
                "to what produced it cannot be re-run (QA-121, INV-2). Before D-04 "
                "exists it is the content hash of the declared ranking rule"
            )
        if self.universe_n < 1:
            raise NominationContractError(
                f"universe_n={self.universe_n}; n sets E[max z] and every downstream "
                f"power and cost figure depends on it (QA-121)"
            )
        if not isinstance(self.candidates, tuple):
            raise NominationContractError("candidates must be a tuple (QA-122)")
        ranks = [c.rank for c in self.candidates]
        if ranks != sorted(ranks) or ranks != list(range(1, len(ranks) + 1)):
            raise NominationContractError(
                f"candidates must be a dense list ordered by rank from 1; got {ranks} "
                f"(QA-122)"
            )

    @property
    def top(self) -> Candidate:
        if not self.candidates:
            raise NominationContractError(
                "an empty candidate list has no top pick. A run that could rank "
                "nothing produces no nomination, not a nomination of nothing (P5)"
            )
        return self.candidates[0]

    def to_json_obj(self) -> dict:
        return {
            "as_of": self.as_of.isoformat(), "run_id": self.run_id,
            "decision_anchor": self.decision_anchor,
            "horizon_set": {"name": self.horizon_set[0], "version": self.horizon_set[1]},
            "nominating_horizon": self.nominating_horizon,
            "universe_n": self.universe_n,
            "model_artifact_id": self.model_artifact_id,
            "candidates": [{"ticker": c.ticker, "rank": c.rank,
                            "ranked_quantity": c.ranked_quantity, "z": c.z}
                           for c in self.candidates],
            "excluded": [dict(e) for e in self.excluded],
            "arbitration": {"nominated_by": self.nominating_horizon,
                            "delayed_by": list(self.delayed_by),
                            "vetoed_by": list(self.vetoed_by),
                            "research_only": list(self.research_only)},
        }
