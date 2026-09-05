"""The contract registry — published, versioned, immutable (FE-2, AC-2.3)."""

from __future__ import annotations

from src.feature_engineer.contracts.spec import FeatureContract
from src.feature_engineer.errors import ContractMutatedError, ContractUnknownError


class ContractRegistry:
    """In-memory publication. Immutability is enforced on CONTENT, not on trust.

    ⚠ **QF-3 is open** — "one contract or several?" Today `PRICE_FEATURES` /
    `ALL_FEATURES` / `ALL_FEATURES_V2` are three overlapping sets, and a model
    trained on one and scored against another is the D-17 hazard. So the registry
    keys on `(name, version)` and **refuses to mix**: there is no "the features",
    only a named contract at a version.
    """

    def __init__(self) -> None:
        self._by_key: dict[tuple[str, int], FeatureContract] = {}

    def publish(self, contract: FeatureContract) -> FeatureContract:
        key = (contract.name, contract.version)
        existing = self._by_key.get(key)
        if existing is not None:
            if existing.content_hash != contract.content_hash:
                raise ContractMutatedError(contract.name, contract.version)
            return existing            # idempotent republish of identical content
        self._by_key[key] = contract
        return contract

    def get(self, name: str, version: int | None = None) -> FeatureContract:
        """`version=None` resolves the latest PUBLISHED version (§10).

        Explicit rather than convenient: in production the version is required by
        the caller, and this default exists for tooling that legitimately wants
        "whatever is current".
        """
        if version is None:
            versions = [v for (n, v) in self._by_key if n == name]
            if not versions:
                raise ContractUnknownError(name, None)
            version = max(versions)
        hit = self._by_key.get((name, version))
        if hit is None:
            raise ContractUnknownError(name, version)
        return hit

    @property
    def published(self) -> list[tuple[str, int]]:
        return sorted(self._by_key)
