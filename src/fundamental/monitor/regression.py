"""RM-4 / RM-5 — the release gates (AC-1.9, RA-60a, GW-9b).

```
RM-4  On any prompt edit, re-run a PINNED BUNDLE SET and diff the verdict
      distribution against the previous version. A WORDING CHANGE THAT FLIPS
      30 % OF VERDICTS IS A CHANGE OF POLICY.

RM-5  Any INV-8 tier change invalidates every baseline here. All of RM-1…RM-4
      re-measured BEFORE the new model is used in production.
```

★★ **RA-60a / GW-9b: `effort` re-baselines exactly as a model change does, and
today nothing fires.** RM-5 keys on an INV-8 *tier* change, and `high → xhigh` is
not one — *it would move every deep-tier output with nothing firing*, which is
**worse than the unset temperature GW-9 was written to fix**, because at least an
unset knob was visibly unset.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.fundamental.monitor.registry import (
    FAIL,
    OK,
    MonitorResult,
    not_yet_calibrated,
)

#: ⚠ **An ADMITTED GUESS** (CN-10). RM-4 names *"a wording change that flips 30 %
#: of verdicts"* as the example of a policy change, so 0.30 is the spec's own
#: illustration promoted to a threshold — never measured.
VERDICT_FLIP_CEILING = 0.30


@dataclass(frozen=True, slots=True)
class Baseline:
    """A pinned bundle set and the verdicts a prompt version produced on it.

    ★ **Pinned** is the load-bearing word: RM-4 compares two prompt versions, so
    everything else must be identical or the diff measures the bundles.
    """

    prompt_name: str
    prompt_version: str
    #: bundle_hash -> verdict
    verdicts: dict

    def __post_init__(self) -> None:
        if not self.verdicts:
            raise ValueError(
                f"{self.prompt_name}@{self.prompt_version}: an empty baseline "
                f"cannot be regressed against — RM-4 needs a pinned bundle SET"
            )


@dataclass(frozen=True, slots=True)
class RegressionResult:
    """What changed between two prompt versions on the same pinned bundles."""

    prompt_name: str
    from_version: str
    to_version: str
    compared: int
    flipped: int
    distribution_before: dict
    distribution_after: dict

    @property
    def flip_rate(self) -> float:
        return self.flipped / self.compared if self.compared else 0.0

    @property
    def blocks_release(self) -> bool:
        """AC-1.9 — ★ *a prompt change without an RM-4 regression run blocks release.*

        And a regression run that FOUND a policy change blocks it too: the point
        is not that the run happened, but that a wording edit did not silently
        become a change of method.
        """
        return self.flip_rate > VERDICT_FLIP_CEILING

    def to_json_obj(self) -> dict:
        return {"prompt_name": self.prompt_name, "from": self.from_version,
                "to": self.to_version, "compared": self.compared,
                "flipped": self.flipped, "flip_rate": round(self.flip_rate, 6),
                "before": dict(self.distribution_before),
                "after": dict(self.distribution_after),
                "blocks_release": self.blocks_release}


def rm4_regression(before: Baseline, after: Baseline) -> RegressionResult:
    """Diff two prompt versions over the bundles they share.

    ⚠ **Only the shared bundles are compared.** A bundle present in one baseline
    and not the other tells you nothing about the prompt, and including it would
    let a changed *sample* read as a changed *policy*.
    """
    if before.prompt_name != after.prompt_name:
        raise ValueError(
            f"RM-4 compares one prompt across versions, not "
            f"{before.prompt_name!r} against {after.prompt_name!r}"
        )
    if before.prompt_version == after.prompt_version:
        raise ValueError(
            f"{before.prompt_name}: both baselines are {before.prompt_version!r}. "
            f"A regression run against itself always passes and verifies nothing"
        )
    shared = sorted(set(before.verdicts) & set(after.verdicts))
    if not shared:
        raise ValueError(
            f"{before.prompt_name}: the two baselines share no bundle_hash. RM-4 "
            f"needs a PINNED set — a changed sample would read as a changed policy"
        )
    flipped = sum(1 for h in shared if before.verdicts[h] != after.verdicts[h])
    return RegressionResult(
        prompt_name=before.prompt_name, from_version=before.prompt_version,
        to_version=after.prompt_version, compared=len(shared), flipped=flipped,
        distribution_before=dict(Counter(before.verdicts[h] for h in shared)),
        distribution_after=dict(Counter(after.verdicts[h] for h in shared)),
    )


def rm4_result(result: RegressionResult | None) -> MonitorResult:
    """RM-4 as a monitor row. ★ `None` ⇒ no run happened, which BLOCKS release."""
    if result is None:
        return not_yet_calibrated("RM-4", n=0)
    return MonitorResult("RM-4", FAIL if result.blocks_release else OK,
                         value=result.to_json_obj(), n=result.compared)


def rm5_rebaseline_required(before: dict, after: dict) -> MonitorResult:
    """RM-5 — ★★ **extended to `effort`** (GW-9b, RA-60a).

    ⚠ RM-5 as written keys on an INV-8 **tier** change. `high → xhigh` is not
    one, *and it would move every deep-tier output with nothing firing.* This
    watches the whole decoding record, so a change to any control that alters the
    output distribution invalidates the baselines.
    """
    watched = ("model_id", "effort", "thinking_mode", "temperature")
    changed = [k for k in watched if before.get(k) != after.get(k)]
    return MonitorResult(
        "RM-5", FAIL if changed else OK, n=len(changed),
        value={"changed": changed,
               "note": ("every RM-1..RM-4 baseline is invalid until re-measured "
                        "(RM-5, GW-9b)") if changed else "no decoding change"},
    )
