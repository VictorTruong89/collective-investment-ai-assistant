"""D-01 §4B — the relay's contracts. CT-1.5, RA-114…RA-128, RA-143, RA-144.

```text
╔══════════════════════════════════════════════════════════════════╗
║  THE RELAY IS AN EXTERNAL PROVIDER WITH A HUMAN AS ITS           ║
║  TRANSPORT.                                                      ║
║                                                                  ║
║  It is not "D-01 running somewhere else". The request is         ║
║  D-01's — it composes it. The RESPONSE is an external            ║
║  artifact that must be ingested and validated before anything    ║
║  builds on it — exactly as an FMP figure is.                     ║
║                                                                  ║
║  ⚠ A number does not become trustworthy because a human          ║
║  carried it.                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **Under that framing the relay needs almost no new machinery** — an ingest, a
validator and a provenance label. What it does *not* get is the assumption that
a `Thesis` is a `Thesis` regardless of where it came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

#: RA-116 — D-09 RP-1's reliability classes gain a fourth. ⚠ *A reader must
#: never have to remember which reports came from a chat window.*
PROVENANCE_RELAYED = "relayed_judgement"

#: RA-117 — the only acceptable session state.
SESSION_FRESH = "fresh"

#: RA-118's per-claim outcomes (RA-143 records them one by one).
VERIFIED, CONTRADICTED, UNVERIFIABLE = "verified", "contradicted", "unverifiable"
RESULTS = (VERIFIED, CONTRADICTED, UNVERIFIABLE)

ASSISTANTS = ("claude_pro", "chatgpt_plus", "other")


@dataclass(frozen=True, slots=True)
class RelayEnvelope:
    """`CT-1.5.relay` — what is knowable about a chat-window response.

    ⚠ **RA-11/AP-6/CT-1.2 do not survive a paste**: a chat UI reports no model
    id, no decoding parameters, no token counts. ★ Record what is knowable and
    leave the rest `unknown` — **never fabricated**.
    """

    assistant: str
    model_stated: str            # ★ SELF-REPORTED by the relayer — never a fact
    relayed_by: str
    pasted_at: str
    prompt_blocks: tuple[str, ...]        # RA-122
    archetype_applied: str = ""           # RA-123 (J-01)
    session: str = SESSION_FRESH          # RA-117
    passes: int = 1                       # 1 or 2 — §4B.6

    def __post_init__(self) -> None:
        if self.assistant not in ASSISTANTS:
            raise ValueError(f"assistant {self.assistant!r} not in {ASSISTANTS}")
        if self.passes not in (1, 2):
            raise ValueError(
                f"passes={self.passes}: §4B.6 offers one paste or two. ★ Two is "
                f"the higher-assurance form because **Pass A never receives the "
                f"price** — RA-14 restored structurally rather than by instruction"
            )

    @property
    def anchor_strip_is_structural(self) -> bool:
        """RA-119 — ⚠ *staging inside a single prompt is ordering, not a freeze.*

        ★ With one paste the model sees price from the first token and RA-14 is
        **an instruction it can ignore**; the two-pass form restores the
        guarantee at the cost of a second paste.
        """
        return self.passes == 2

    def to_json_obj(self) -> dict:
        return {"assistant": self.assistant, "model_stated": self.model_stated,
                "session": self.session, "relayed_by": self.relayed_by,
                "pasted_at": self.pasted_at,
                "prompt_blocks": list(self.prompt_blocks),
                "archetype_applied": self.archetype_applied,
                "passes": self.passes,
                "anchor_strip": ("structural" if self.anchor_strip_is_structural
                                 else "instruction_only")}


@dataclass(frozen=True, slots=True)
class ClaimVerification:
    """★ RA-143 — one claim's result, and what it was checked against.

    ⚠ *RA-118 requires the result "recorded per claim" and `CT-1.5` stored three
    integers.* Two readers need the detail and neither can get it from a count:
    the ingest failure must name **which** claim contradicted, and a reader of a
    HOLD-capped report needs to know **which** claims were unverifiable — that
    set is precisely what the cap is about.
    """

    ordinal: int
    text: str
    result: str
    checked_against: str = ""
    ours: str = ""
    theirs: str = ""

    def __post_init__(self) -> None:
        if self.result not in RESULTS:
            raise ValueError(f"result {self.result!r} not in {RESULTS} (RA-118)")
        if self.result != UNVERIFIABLE and not self.checked_against:
            raise ValueError(
                f"claim #{self.ordinal}: {self.result!r} with no counterpart "
                f"named. ★ A verification that cannot say what it checked "
                f"against is not a verification (RA-118)"
            )

    def to_json_obj(self) -> dict:
        return {"ordinal": self.ordinal, "text": self.text, "result": self.result,
                "checked_against": self.checked_against,
                "ours": self.ours, "theirs": self.theirs}


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """`CT-1.5.verification`. ★ The counts are a **projection** of `claims`."""

    claims: tuple[ClaimVerification, ...]
    checked_against: tuple[str, ...] = ()

    def _count(self, result: str) -> int:
        return sum(1 for c in self.claims if c.result == result)

    @property
    def claims_total(self) -> int:
        return len(self.claims)

    @property
    def verified(self) -> int:
        return self._count(VERIFIED)

    @property
    def contradicted(self) -> int:
        return self._count(CONTRADICTED)

    @property
    def unverifiable(self) -> int:
        return self._count(UNVERIFIABLE)

    @property
    def contradictions(self) -> tuple[ClaimVerification, ...]:
        return tuple(c for c in self.claims if c.result == CONTRADICTED)

    @property
    def unverifiable_claims(self) -> tuple[ClaimVerification, ...]:
        return tuple(c for c in self.claims if c.result == UNVERIFIABLE)

    @property
    def coverage(self) -> float:
        """★★ RA-114 — **this is what caps the verdict, and no relay-specific
        rule anywhere does it.**

        Coverage counts items *successfully extracted and checked* (RA-66), and
        a relay report's claims are largely unverifiable against data we hold.
        So its coverage is low, INV-012/INV-013's floors fire **on their own**,
        and the verdict is capped at HOLD or forced to `INSUFFICIENT_DATA`.
        ★ *A mechanism built to stop a model inflating its own confidence turns
        out to price an untrusted transport correctly too.*
        """
        if not self.claims:
            return 0.0
        return self.verified / self.claims_total

    #: ⚠ RA-144 — the name `assess_confidence` reads. The floors take a coverage
    #: VALUE, so this object and a `CoverageReport` share one implementation
    #: while keeping different denominators (`claims_total` vs `required_union`).
    @property
    def aggregate(self) -> float:
        return self.coverage

    def to_json_obj(self) -> dict:
        return {"claims_total": self.claims_total, "verified": self.verified,
                "contradicted": self.contradicted,
                "unverifiable": self.unverifiable,
                "coverage": round(self.coverage, 6),
                "claims": [c.to_json_obj() for c in self.claims],
                "checked_against": list(self.checked_against)}


@dataclass(frozen=True, slots=True)
class RelayReport:
    """CT-1.5 — a relayed analysis and what could be checked."""

    ticker: str
    as_of: date
    relay: RelayEnvelope
    verification: VerificationResult
    verdict: str = ""
    conviction: str = ""
    narrative: str = ""
    #: ★★ RA-115 — **always `null`.** Kept as a field so that a report claiming
    #: one is a *visible* defect rather than an absent attribute nobody notices.
    verdict_stability: dict | None = None
    provenance_class: str = PROVENANCE_RELAYED
    degraded: bool = False

    def __post_init__(self) -> None:
        from src.fundamental.errors import RelayStabilityClaimedError

        if self.verdict_stability is not None:
            raise RelayStabilityClaimedError(self.ticker)
        if self.provenance_class != PROVENANCE_RELAYED:
            raise ValueError(
                f"provenance_class {self.provenance_class!r}: a relay report is "
                f"a distinct reliability class and carries it in every medium "
                f"(RA-116, RP-1)"
            )

    @property
    def can_be_actionable(self) -> bool:
        """★★ RA-115 / AC-1.78 — **no**, and not by policy: by construction.

        AC-1.8 requires the actionable pick to carry a `k ≥ 3` stability result.
        ⚠ *The relay can inform, gate and populate the card; it cannot be the one
        thing INV-6 lets you trade on* unless an API-side probe is run over the
        same name.
        """
        return False

    def to_json_obj(self) -> dict:
        return {
            "ticker": self.ticker, "as_of": self.as_of.isoformat(),
            "relay": self.relay.to_json_obj(),
            "verification": self.verification.to_json_obj(),
            "verdict": self.verdict, "conviction": self.conviction,
            "verdict_stability": None,
            "provenance_class": self.provenance_class,
            "degraded": self.degraded,
        }
