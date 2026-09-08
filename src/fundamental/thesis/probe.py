"""D-01 §7.1 — `author_thesis(bundle, k)`. RM-1, RA-20, RA-61, RA-62, AC-1.8.

★★ **`k > 1` runs the stability probe.** §12's API says so and nothing ran it:
the probe machinery measured verdicts a caller had to produce by hand, and the
authoring path produced one.

```text
   RM-1 asks: does this bundle produce THE SAME VERDICT when the INPUT is
   restructured in ways the answer should be invariant to?

     option_order       the enumerated verdicts, permuted   (RA-17)
     evidence_order     the bundle's parts, reordered       (RA-4 — the hash
                                                             is order-independent)
     prompt_paraphrase  ⚠ NOT APPLIED — see RA-61 below
```

⚠ **Only two of the three perturbations are real.** `prompt_paraphrase` would
change the prompt text, and **RA-13 hashes it** — a paraphrase is a different
prompt version, not a perturbation of one. ★ Declaring it and not applying it
would be worse than either: the probe would claim a robustness it never tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.fundamental.monitor.variance import (
    K_STAB,
    StabilityResult,
    rm1_perturbation_probe,
)

#: ★★ **What this probe actually varies — and the list is short for reasons.**
#:
#: | Perturbation | Applied | Why |
#: |---|---|---|
#: | `option_order` | ✅ | RA-17 shuffles the enumerated verdicts per call and records the permutation |
#: | `evidence_order` | ✅ | ⚠ **at the PAYLOAD, not the bundle** — see below |
#: | `prompt_paraphrase` | ❌ | RA-13 hashes the prompt text, so a paraphrase is a **new version**, not a perturbation of one |
#:
#: ⚠ **`evidence_order` was a NO-OP for its first hour of life.** The obvious
#: implementation rotates `bundle.parts` — and `EvidenceBundle.__post_init__`
#: **sorts them**, because RA-4 makes the hash independent of arrival order.
#: The rotation was undone before the bundle was returned, and the probe
#: **reported a perturbation it had never applied.** ★ That is precisely the
#: failure `prompt_paraphrase` is excluded to avoid, arriving through the other
#: door: *declaring a robustness you did not test is worse than testing
#: neither.* The order must be varied where it actually reaches the model —
#: **the composed payload** — which leaves the bundle, and its hash, untouched.
APPLIED_PERTURBATIONS = ("option_order", "evidence_order")


@dataclass(frozen=True, slots=True)
class ProbeRun:
    """One authoring pass, and what it cost."""

    index: int
    verdict: str
    conviction: str
    evidence_order: tuple[str, ...]
    option_permutation: tuple[str, ...]
    run_ids: tuple[str, ...] = ()
    tokens_in: int = 0
    tokens_out: int = 0

    def to_json_obj(self) -> dict:
        return {"index": self.index, "verdict": self.verdict,
                "conviction": self.conviction,
                "evidence_order": list(self.evidence_order),
                "option_permutation": list(self.option_permutation),
                "run_ids": list(self.run_ids), "tokens_in": self.tokens_in,
                "tokens_out": self.tokens_out}


@dataclass(frozen=True, slots=True)
class ProbedThesis:
    """The thesis, **and the spread that let it be published** (RA-20)."""

    thesis: object
    #: ⚠ **`None` below `K_STAB`, never a weak result.** `StabilityResult`
    #: refuses to exist at `k < 3` (AC-1.8) and that guard is right: *a single
    #: chat response has no distribution* (RA-115), and neither does a single
    #: authoring pass. ★ `CT-1.1.verdict_stability` is **`null`** for exactly
    #: this case — the absence is the contract, not a gap in it.
    stability: StabilityResult | None
    runs: tuple[ProbeRun, ...] = field(default_factory=tuple)

    @property
    def actionable(self) -> bool:
        """★★ AC-1.8 — the actionable pick carries a `k ≥ 3` stability result.

        ⚠ This is the property RA-115 uses to keep a relay report off the
        actionable slot, and BS-33 uses to keep the skeleton's card honest.
        """
        return self.stability is not None and self.stability.k >= K_STAB

    def to_json_obj(self) -> dict:
        return {"thesis": self.thesis.to_json_obj(),
                # ★ `null`, not an empty object — CT-1.1's own value.
                "verdict_stability": (self.stability.to_json_obj()
                                      if self.stability else None),
                "actionable": self.actionable,
                "runs": [r.to_json_obj() for r in self.runs]}


def evidence_rotation(bundle, index: int) -> int:
    """How far to rotate the evidence **in the composed payload** for run `index`.

    ★ **Not on the bundle.** `EvidenceBundle.__post_init__` sorts its parts so
    that RA-4's hash is order-independent — so rotating them there is undone
    immediately, and a probe built that way reports a perturbation it never
    applied. ⚠ Rotating the payload keeps `bundle_hash` identical across the
    `k` runs, which is what makes the runs **comparable at all** (RA-2).
    """
    parts = len(bundle.parts)
    return (index % parts) if parts else 0


def perturb_bundle(bundle, index: int):
    """⚠ **Deliberately the identity.** The bundle must be byte-identical across
    the `k` runs, or RM-1 measures two different questions.

    ★ Kept as a named no-op rather than deleted: a reader looking for *"where is
    the bundle perturbed?"* should find this and its reason, not silence.
    """
    return bundle


def author_thesis(bundle, *, author, k: int = 1, as_of: date | None = None):
    """§12 — ★ `k > 1` runs the stability probe (RM-1).

    `author(bundle, index)` performs **one full authoring pass** and returns a
    `ProbeRun` plus the `Thesis`. ⚠ *The caller supplies the verdicts, not the
    calls* — keeping the running separate from the measurement is what lets
    RM-2 and RM-3 read the same `k` outputs without a second `k×` spend.

    ★ **The published thesis is the FIRST run's**, not a vote. A modal verdict
    assembled from k runs is a thesis nobody wrote, and its falsifiers would
    belong to a different pass than its verdict (RA-16).
    """
    from src.fundamental.errors import ResearchError

    if k < 1:
        raise ResearchError("k must be at least 1")

    runs, theses = [], []
    for index in range(k):
        probe_run, thesis = author(bundle, index)
        runs.append(probe_run)
        theses.append(thesis)

    # ⚠ Below `K_STAB` there is NO stability result — `StabilityResult` refuses
    #   to be constructed (AC-1.8), and forcing one would manufacture a
    #   distribution from a single draw.
    stability = (rm1_perturbation_probe(
        [r.verdict for r in runs], perturbations=APPLIED_PERTURBATIONS)
        if k >= K_STAB else None)
    published = theses[0]
    if stability is not None:
        import dataclasses

        published = dataclasses.replace(
            published, verdict_stability=stability.to_json_obj())
    return ProbedThesis(thesis=published, stability=stability,
                        runs=tuple(runs))


def assert_publishable(probed: ProbedThesis) -> ProbedThesis:
    """RA-20 / AC-1.8 / BS-28 — ★ **a verdict cannot reach a human without its
    stability figure.**

    ⚠ *`k=1` is not a failure* — it is a legitimate cheap run whose output is
    **not actionable**. What is forbidden is publishing one as though it were.
    """
    from src.fundamental.errors import ResearchError

    if not probed.actionable:
        k = probed.stability.k if probed.stability else 1
        raise ResearchError(
            f"the thesis carries k={k} and the actionable pick "
            f"needs k>={K_STAB} (AC-1.8, RA-20). ★ It may still inform, gate "
            f"and populate the card — it may not be the one thing INV-6 lets "
            f"you trade on")
    return probed
