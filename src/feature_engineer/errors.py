"""D-02 error family — §12's catalog made raisable (L4 §5.3, EH-13).

D-02's failures are all one shape: **a number that does not mean what the
contract says it means.** That is why every code here names either the contract
or the invariant it protects, and why none of them has a lenient mode.
"""

from __future__ import annotations

from src.shared.errors import PipelineError


class FeatureError(PipelineError):
    """Base for D-02. Code: ``FEAT.*``."""

    code = "FEAT.UNSPECIFIED"
    retryable = False


class ContractUnknownError(FeatureError):
    code = "FEAT.CONTRACT.UNKNOWN"

    def __init__(self, name: str, version) -> None:
        super().__init__(
            f"no feature contract {name!r} version {version!r}. A model scored against "
            f"a contract that does not resolve cannot be parity-checked (FE-3)"
        )


class ContractMutatedError(FeatureError):
    """FE-2 / AC-2.3 — a published version's content changed.

    ⚠ The whole point of a version is that it is a **fixed referent**. If v3 can
    mean two things, every model trained "on v3" is trained on an unknown, and
    INV-4 parity becomes an assertion about a name rather than about a formula.
    """

    code = "FEAT.CONTRACT.MUTATED"

    def __init__(self, name: str, version: int) -> None:
        super().__init__(
            f"{name}@v{version} is already published and its content differs. A "
            f"published version is immutable — changing a formula_id, a range or the "
            f"membership produces a NEW version (FE-2)"
        )


class UndeclaredColumnError(FeatureError):
    """FE-1 / AC-2.1 — a panel column with no FeatureSpec."""

    code = "FEAT.CONTRACT.UNDECLARED_COLUMN"

    def __init__(self, columns) -> None:
        super().__init__(
            f"panel carries undeclared column(s) {sorted(columns)}. A feature exists "
            f"only if a published contract specifies it — an unspecified column is a "
            f"defect, not a bonus feature (FE-1)"
        )


class MissingFeatureError(FeatureError):
    """FE-1 / AC-2.2 — a declared feature absent from the panel.

    ⚠ **Checked, never filtered** (PD-18). `model_bundle.py:80`'s
    ``[c for c in feature_names if c in df.columns]`` is one word away from
    correct, and that word is the whole of D-17.
    """

    code = "FEAT.CONTRACT.MISSING_FEATURE"

    def __init__(self, missing) -> None:
        super().__init__(
            f"declared feature(s) {sorted(missing)} absent from the panel. A missing "
            f"feature is an error, never a smaller model input (FE-1, D-17)"
        )


class RangeViolationError(FeatureError):
    """FE-5 / AC-2.5 — INV-3. A declared range is enforced at emit, not documented."""

    code = "FEAT.RANGE.VIOLATION"

    def __init__(self, feature: str, low, high, offenders) -> None:
        super().__init__(
            f"{feature} declares range [{low}, {high}] and emitted {offenders} outside "
            f"it. A range that is documented and not enforced is a comment (INV-3, FE-5)"
        )


class AsOfRequiredError(FeatureError):
    """FE-7 / FE-8 / AC-2.8 — as_of or adj_as_of omitted.

    Both, and with no default. `as_of` is DE-6.4 one layer out; `adj_as_of` is
    DE-45 one layer out. The two axes fail differently — one is INV-1, the other
    INV-2 — and neither is recoverable downstream.
    """

    code = "FEAT.PIT.AS_OF_REQUIRED"

    def __init__(self, method: str, which: str) -> None:
        super().__init__(
            f"{method} requires an explicit {which}. A defaulted {which} is right in "
            f"production and wrong in every backtest, and the numbers look right in "
            f"both cases (FE-7, FE-8)"
        )


class CalendarHaltError(FeatureError):
    """FE-10 / AC-2.12 — D-07's calendar check returned HALT.

    ★ It **propagates**. D-02 never computes "around" a blocking corporate
    action: a model trained across a window whose units changed partway through
    is not wrong at any single point, and nothing in the data says so.
    """

    code = "FEAT.PIT.CALENDAR_HALT"

    def __init__(self, blocked) -> None:
        super().__init__(
            f"D-07's calendar check returned HALT for {sorted(blocked)}; no panel is "
            f"built. The halt propagates rather than being worked around (FE-10)"
        )


class LabelInContractError(FeatureError):
    """FE-11 / AC-2.14 — a label appears in a FeatureContract.

    ★ The directory boundary is the guard: **one module is allowed to see the
    future and it is not the one models take inputs from.** This error is the
    guard's runtime half, for the case where the name sneaks in anyway.
    """

    code = "FEAT.LABEL.IN_CONTRACT"

    def __init__(self, names) -> None:
        super().__init__(
            f"{sorted(names)} name(s) look like labels and appear in a FeatureContract. "
            f"A label is forward-looking by construction; a model taking one as an "
            f"input is trained on its own answer (FE-11)"
        )


class AnalystDerivedInputError(FeatureError):
    """FE-21 / AC-2.22 — INV-014. A FeatureSpec input traces to an analytical domain.

    ⚠ **Including a deterministic transform of one.** `MoatScorer._llm_score` is
    deterministic and reads three fields an LLM in D-01 authored: *the
    determinism is in the transport, not the source.*
    """

    code = "FEAT.INPUT.ANALYST_DERIVED"

    def __init__(self, feature: str, bad_inputs) -> None:
        super().__init__(
            f"feature {feature!r} declares input(s) {sorted(bad_inputs)} produced by an "
            f"analytical domain. A FeatureSpec's inputs are D-07 fields and other D-02 "
            f"features, and nothing else — a deterministic function of an LLM's output "
            f"is still the LLM's judgement (FE-21, INV-014)"
        )


class DuplicateDefinitionError(FeatureError):
    """FE-4 / FE-25 / AC-2.25 — two modules computing one formula_id.

    The defect this domain exists to remove: `moat_score` (0-10, blended with an
    LLM read) and `f_moat_quant_score` (0-1, panel-native) are two computations
    of one concept, and **nothing says so**.
    """

    code = "FEAT.DUPLICATE_DEFINITION"

    def __init__(self, formula_id: str, modules) -> None:
        super().__init__(
            f"formula_id {formula_id!r} is computed in {sorted(modules)}. One feature, "
            f"one owning module — the second definition is always the one nobody tests "
            f"(FE-4, FE-25)"
        )
