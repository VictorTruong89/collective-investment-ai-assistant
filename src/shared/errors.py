"""Error hierarchy for D-00 (L4 §1.3 module skeleton).

Every error here RAISES. None is returned as a sentinel and none has a lenient
mode — constitution **P5**, fail loud, never silent. The two real incidents
behind that rule were a discipline card built from a *failed* LLM narrative and
one built from an *absent* narrative, both emailed as genuine recommendations
with no stop and no targets (**GW-22**).

Each money error carries BOTH operands in its message. An error reading only
"currency mismatch" costs a debugging session that "cannot add USD to CAD" does
not (L2-shared-money §6).

⚠ **SC-3 applies here too**: a secret must never reach an exception message.
That is enforced by the `Secret` wrapper's `__repr__`/`__str__` rather than by
care at each raise site — see `src/shared/secrets.py`.
"""

from __future__ import annotations


class PipelineError(Exception):
    """Root of every error this system raises deliberately.

    Catching this says "a declared rule fired", as distinct from "the
    interpreter broke". Nothing inside D-00 catches it broadly.
    """


# --------------------------------------------------------------------------- #
# Money — L2-shared-money.md §6
# --------------------------------------------------------------------------- #

class MoneyError(PipelineError):
    """Base for every monetary-value error."""


class CurrencyMismatchError(MoneyError):
    """Arithmetic, ordering, ratio or sum across two currencies (MO-2).

    There is no implicit conversion to base and no `allow_mixed` flag. The only
    path across a currency boundary is `Money.convert(FxRate)` (FX-1).
    """

    def __init__(self, left: str, right: str, operation: str = "combine") -> None:
        super().__init__(
            f"cannot {operation} {left} with {right} — cross-currency arithmetic "
            f"requires an explicit convert(FxRate) (INV-5, MO-2)"
        )
        self.left, self.right = left, right


class UnsupportedCurrencyError(MoneyError):
    """Currency not in SUPPORTED_CURRENCIES — never defaults to base (AC-M.2)."""

    def __init__(self, code: object, supported) -> None:
        super().__init__(
            f"unsupported currency {code!r}; supported: {sorted(supported)} — an "
            f"untagged or unknown amount is a defect, not a default-to-base (INV-001)"
        )
        self.code = code


class InvalidAmountError(MoneyError):
    """Amount unparseable, or not an `int` of minor units (MO-1)."""


class PrecisionLossError(MoneyError):
    """Input carries more fractional digits than the currency's minor unit.

    Silently rounding sub-cent input is how a reconciliation ends up a few cents
    out with no record of where. A caller that wants rounding asks by name.
    """

    def __init__(self, text: str, currency: str, exponent: int) -> None:
        super().__init__(
            f"{text!r} has more precision than {currency} supports ({exponent} dp) — "
            f"quantize explicitly if rounding is intended"
        )


class FxDirectionError(MoneyError):
    """`rate.from_currency` does not match the amount's currency (FR-005)."""

    def __init__(self, have: str, rate_pair: str) -> None:
        super().__init__(
            f"cannot convert {have} using rate {rate_pair} — that rate converts "
            f"from {rate_pair[:3]}, not from {have}"
        )


# --------------------------------------------------------------------------- #
# Config — L2-shared-infrastructure §6, error catalog §11
# --------------------------------------------------------------------------- #

class ConfigError(PipelineError):
    """Base for configuration errors. Code: SHR.CFG.*"""


class MissingConfigKeyError(ConfigError):
    """SHR.CFG.MISSING_KEY — a required key is absent (CF-1).

    There is no silent default for a value the system needs. A default supplied
    here would be a policy choice made by D-00, which §1.2 forbids it to hold.
    """

    def __init__(self, key: str, sources) -> None:
        super().__init__(
            f"required config key {key!r} is absent from {list(sources)} — "
            f"D-00 validates shape and never invents a value (CF-1, SI-2)"
        )
        self.key = key


class ConfigMutationError(ConfigError):
    """SHR.CFG.MUTATED — config changed after load (CF-4).

    A runtime mutation makes CF-3's manifest a lie about the second half of the
    run, which is worse than no manifest at all.
    """


# --------------------------------------------------------------------------- #
# Secrets — L2-shared-infrastructure §8
# --------------------------------------------------------------------------- #

class SecretError(PipelineError):
    """Base for secret-handling errors. Code: SHR.SEC.*"""


class SecretAbsentError(SecretError):
    """SHR.SEC.ABSENT — a required secret is missing (SC-2).

    Raised at STARTUP, not at first use. Failing at first use means a nightly
    run dies forty minutes in, having already spent tokens and produced half a
    panel.
    """

    def __init__(self, names) -> None:
        listed = ", ".join(sorted(names))
        super().__init__(
            f"required secret(s) absent from the environment: {listed} — "
            f"set them in .env (gitignored) and re-run. Failing now rather than "
            f"at first use is deliberate (SC-1, SC-2)"
        )
        self.names = tuple(sorted(names))


class SecretLeakError(SecretError):
    """SHR.SEC.LEAKED — a secret reached a log, error, manifest or artifact (SC-3).

    ⚠ Raised by the guards, not by discovery after the fact. A leaked key is
    ROTATED, not merely purged — repo history has been rewritten once for this,
    and purging removes the copy while rotation removes the risk (SC-4).
    """


# --------------------------------------------------------------------------- #
# Boundary — L2-shared-infrastructure §11
# --------------------------------------------------------------------------- #

class LLMError(PipelineError):
    """Base for gateway errors. Code: SHR.LLM.*"""


class DriftBlockedError(LLMError):
    """SHR.LLM.DRIFT_BLOCKED — prompt alignment failed; NO call runs (INV-9, GW-12).

    Surfaced to the caller, never swallowed. A drift check that logs and
    proceeds is the check not existing (GW-13).
    """


class TruncatedError(LLMError):
    """SHR.LLM.TRUNCATED — hit `max_tokens`. A failure, not a short answer (GW-23).

    ⚠ With adaptive thinking the response budget is `max_tokens` minus whatever
    thinking consumed, which is not knowable in advance — so truncation is
    CAUGHT, not predicted (GW-7b).
    """


class UnparseableError(LLMError):
    """SHR.LLM.UNPARSEABLE — response does not match the declared schema (GW-3)."""


class RefusedError(LLMError):
    """The model declined. A refusal is a real answer and is NEVER retried (GW-15)."""


class SemanticRetryError(LLMError):
    """SHR.LLM.SEMANTIC_RETRY — a retry was attempted on a non-transport failure.

    ★ EH-15 one layer down: retry the request that got no real answer; never
    the answer you disliked. This fires on the gateway's own bug, not the
    provider's.
    """


class BudgetExceededError(LLMError):
    """SHR.LLM.BUDGET_EXCEEDED — a declared budget was passed; the run fails (GW-20).

    ⚠ A budget that can be exceeded silently is not a budget — and at
    `k_cov x k_stab` the call count multiplies, so overspend arrives faster than
    intuition suggests.
    """


class TransportError(LLMError):
    """A transport-layer failure: 429, 5xx, timeout, connection reset.

    The ONLY class the gateway retries (GW-15, GW-17). `retryable=False` marks
    an unclassified transport error, which is not retried — EH-14's default.
    """

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class DecodingControlError(LLMError):
    """A decoding control was set that the tier's model does not accept (GW-8a/9a/9c).

    ★ Raised BEFORE the request leaves the gateway, so the failure names the
    rule rather than arriving as a provider 400 that a reader must decode
    (AC-0.4a).
    """


class DomainImportError(PipelineError):
    """SHR.BOUNDARY.DOMAIN_IMPORT — `src/shared/` imported a domain (SI-1).

    Enforced structurally by `tests_src/test_architecture.py`; this exists so a
    runtime guard can name the same rule.
    """
