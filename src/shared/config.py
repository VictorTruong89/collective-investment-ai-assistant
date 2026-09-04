"""Configuration — load once, validate, freeze (L2-shared-infrastructure §6).

The four rules and what each prevents:

  CF-1  a missing required key RAISES. There is no silent default for a value
        the system needs, because a default chosen here is a policy choice made
        by D-00 — which §1.2 forbids it to hold (SI-2).
  CF-2  read once at the edge, passed inward. A value re-read deep in a call
        stack can resolve differently within one run.
  CF-3  every resolved value reaches the RunManifest. ★ A tuned number no
        manifest records makes the run irreproducible while looking
        deterministic.
  CF-4  immutable after load. A runtime mutation makes CF-3's record a lie
        about the second half of the run.
  CF-5  D-00 validates SHAPE and never interprets MEANING. That `δ = 2.19` is
        sane is D-03's judgement.

★ Secrets are excluded from the manifest BY CONSTRUCTION, not filtered on the
way out (CT-0.2, SC-3): a `Secret` never enters the config mapping in the first
place, so there is no filter to forget to apply.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from src.shared.errors import ConfigMutationError, MissingConfigKeyError
from src.shared.secrets import Secret


@dataclass(frozen=True, slots=True)
class ConfigSpec:
    """A declared schema (CF-1). Shape only — never meaning (CF-5)."""

    required: tuple[str, ...] = ()
    optional: Mapping[str, Any] = field(default_factory=dict)

    def validate(self, resolved: Mapping[str, Any], sources) -> dict:
        merged = dict(self.optional)
        merged.update(resolved)
        for key in self.required:
            if key not in merged or merged[key] is None:
                raise MissingConfigKeyError(key, sources)
        return merged


@dataclass(frozen=True, slots=True)
class ConfigManifest:
    """CT-0.2 — the input to D-08's RunManifest (CF-3)."""

    config_hash: str
    source_files: tuple[str, ...]
    resolved: Mapping[str, Any]
    loaded_at: str

    def to_json_obj(self) -> dict:
        return {
            "config_hash": self.config_hash,
            "source_files": list(self.source_files),
            "resolved": dict(self.resolved),
            "loaded_at": self.loaded_at,
        }


class Config:
    """An immutable, flattened view of the loaded configuration (CF-4).

    Keys are dotted paths (`llm.deep.model_id`) so a manifest entry names one
    value rather than a nested blob a reader has to search.
    """

    __slots__ = ("_values", "_sources", "_loaded_at")

    def __init__(self, values: Mapping[str, Any], sources: Iterable[str]) -> None:
        object.__setattr__(self, "_values", MappingProxyType(dict(values)))
        object.__setattr__(self, "_sources", tuple(sources))
        object.__setattr__(
            self, "_loaded_at", datetime.now(timezone.utc).isoformat(timespec="seconds")
        )

    def __setattr__(self, *_a) -> None:
        raise ConfigMutationError(
            "config is immutable after load — a runtime mutation makes the "
            "manifest a lie about the second half of the run (CF-4)"
        )

    def __setitem__(self, *_a) -> None:
        raise ConfigMutationError("config is immutable after load (CF-4)")

    def __contains__(self, key: str) -> bool:
        return key in self._values

    def get(self, key: str) -> Any:
        """Fetch a value the caller REQUIRES. Absent ⇒ raises (CF-1).

        Returning `None` here is how a silent default is born, so it never does.
        """
        if key not in self._values:
            raise MissingConfigKeyError(key, self._sources)
        return self._values[key]

    def get_optional(self, key: str, default: Any = None) -> Any:
        """Probe for a value that MAY legitimately be absent.

        ⚠ Distinct from `get()` on purpose. CF-1 governs keys the system needs;
        a probe asking *"did someone set this?"* is a different question, and
        the gateway asks it — `llm.deep.temperature` must be ABSENT in a correct
        config, and its presence is the error (GW-8a).

        Conflating the two, as an earlier draft did, made every such probe raise
        `MissingConfigKeyError` for the correct configuration.
        """
        return self._values.get(key, default)

    def manifest(self) -> ConfigManifest:
        """CF-3 — every resolved value, hashed so two runs are comparable.

        ★ Secrets cannot appear: `_flatten` refuses to place a `Secret` into the
        mapping at all (SC-3), so exclusion is structural rather than a filter
        applied here that someone could later forget.
        """
        payload = json.dumps(dict(self._values), sort_keys=True, default=str)
        return ConfigManifest(
            config_hash="sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16],
            source_files=self._sources,
            resolved=self._values,
            loaded_at=self._loaded_at,
        )


def _flatten(obj: Any, prefix: str = "") -> dict:
    out: dict[str, Any] = {}
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Secret):
            # SC-3, structural: a secret never enters the config mapping, so the
            # manifest has nothing to filter and nothing to leak.
            raise ConfigMutationError(
                f"a Secret was placed in config at {path!r} — secrets are read "
                f"from the environment at the edge (SC-1) and never travel in "
                f"the config mapping (SC-3, CT-0.2)"
            )
        if isinstance(value, dict):
            out.update(_flatten(value, path))
        else:
            out[path] = value
    return out


def load_config(paths: Iterable[str | Path], spec: ConfigSpec | None = None) -> Config:
    """Load, merge, validate and freeze (CF-1, CF-2, CF-4).

    Later files override earlier ones. Validation happens after the merge, so a
    key supplied by any source satisfies the requirement.
    """
    import yaml  # local: keeps the import cost off modules that never load config

    sources: list[str] = []
    merged: dict[str, Any] = {}
    for path in paths:
        p = Path(path)
        if not p.exists():
            raise MissingConfigKeyError(f"<file {p}>", sources or [str(p)])
        loaded = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        merged.update(_flatten(loaded))
        sources.append(str(p))

    values = (spec or ConfigSpec()).validate(merged, sources)
    return Config(values, sources)
