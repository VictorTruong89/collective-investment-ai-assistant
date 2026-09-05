"""F4 `T1` — seat 6 assembles an explanation. ⚠ It never computes one.

★★ **D-13 composes already-published attributions.** It does not recompute them
(`AC-4.3`), does not rebuild gate binding (`AC-4.7` — `decision/attribute/binding.py`
owns it), and does not see in-progress analysis. That is what keeps seat 6 on the
legal side of `INV-014`/`ST-9`.

⚠⚠ **No self-explanation** (`AC-4.10`). Chain-of-thought is demonstrably
unfaithful: models shift answers under biasing cues while their stated reasoning
never mentions the cue. So the LLM half is explained by **constraint and
verification**, not introspection — every factual claim binds to a span and is
checked deterministically. **A model's account of its own reasoning is not
evidence and may not enter an `Explanation`.**
"""

from __future__ import annotations

from collections.abc import Sequence

from src.explain.models import Attribution, Counterfactual, Explanation

#: `AC-4.10` — field names that would smuggle self-reported reasoning in.
SELF_REPORT_KEYS = ("reasoning", "chain_of_thought", "cot", "rationale",
                    "model_explanation", "why_i", "thought_process", "self_critique")


class SelfExplanationRejected(Exception):
    """`AC-4.10` — a model's account of its own reasoning is not evidence."""


def _reject_self_report(obj: object, path: str = "gate_binding") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(bad in str(k).lower() for bad in SELF_REPORT_KEYS):
                raise SelfExplanationRejected(
                    f"{path}.{k} looks like model-generated reasoning. ⚠ AC-4.10: "
                    "chain-of-thought is demonstrably unfaithful — models shift "
                    "answers under biasing cues while their stated reasoning never "
                    "mentions the cue. Explain by constraint and verification, not "
                    "introspection."
                )
            _reject_self_report(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _reject_self_report(v, f"{path}[{i}]")


def explain(*, subject_id: str, as_of: str, universe_id: str,
            published_attributions: Sequence[Attribution],
            gate_binding: dict | None = None,
            counterfactual: Counterfactual | None = None,
            grounding: dict | None = None,
            confidence: dict | None = None) -> Explanation:
    """Assemble. ⚠ `published_attributions` are used **as given** (`AC-4.3`)."""
    _reject_self_report(gate_binding)
    return Explanation(
        subject_id=subject_id, as_of=as_of, universe_id=universe_id,
        attributions=tuple(published_attributions),
        gate_binding=gate_binding, counterfactual=counterfactual,
        **({"grounding": grounding} if grounding is not None else {}),
        **({"confidence": confidence} if confidence is not None else {}))
