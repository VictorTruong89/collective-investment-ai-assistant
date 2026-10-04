"""`CT-F10.1` — the declared, versioned assumption set (`D4`, `AC-F10.12`).

★ **No assumption is a literal in code.** Every value lives in
`config/valuation/<name>_v<version>.yaml` with a content hash; changing a value
without changing the version refuses to load (`FE-2`'s rule). A valuation's
trail cites `(name, version, content_hash)`, so two valuations a month apart
can be told comparable or not by the trail alone.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass
from decimal import Decimal

import yaml

from src.feature_engineer.errors import AssumptionsMutatedError, NoFiniteValueError

REPO = pathlib.Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO / "config/valuation"

#: The fields the hash covers — everything but the hash itself.
_HASHED = ("name", "version", "discount_rate", "explicit_years", "stage1_growth",
           "terminal_growth", "band", "implied_bracket")
#: ✏ `D10` — hashed when present. `v1` predates it and is immutable, so its absence means
#: "no duration table declared", never a default table (`CT-F10.1`).
_OPTIONAL_HASHED = ("duration_table",)


def content_hash(doc: dict) -> str:
    """sha256 over the hashed fields, canonically serialised."""
    fields = {k: doc[k] for k in _HASHED}
    fields.update({k: doc[k] for k in _OPTIONAL_HASHED if k in doc})
    payload = json.dumps(fields, sort_keys=True,
                         separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Assumptions:
    name: str
    version: int
    content_hash: str
    discount_method: str
    discount_rate: Decimal
    discount_note: str
    explicit_years: int
    stage1_growth: Decimal
    terminal_growth: Decimal
    band_discount: tuple[Decimal, ...]
    band_terminal: tuple[Decimal, ...]
    implied_low: Decimal
    implied_high: Decimal
    implied_iterations: int
    #: `D10` — the explicit periods implied growth is re-solved at; `()` when not declared.
    duration_years: tuple[int, ...] = ()
    declares_duration_table: bool = False

    def cite(self) -> dict:
        """What a trail records: the identity, never a copy that could drift."""
        return {"name": self.name, "version": self.version, "content_hash": self.content_hash}

    def to_json_obj(self) -> dict:
        return {**self.cite(), "discount_method": self.discount_method,
                "discount_rate": str(self.discount_rate),
                "explicit_years": self.explicit_years,
                "stage1_growth": str(self.stage1_growth),
                "terminal_growth": str(self.terminal_growth),
                "band": {"discount_rate_steps": [str(x) for x in self.band_discount],
                         "terminal_growth_steps": [str(x) for x in self.band_terminal]},
                "implied_bracket": {"low": str(self.implied_low), "high": str(self.implied_high),
                                    "iterations": self.implied_iterations},
                **({"duration_table": {"explicit_years": list(self.duration_years)}}
                   if self.declares_duration_table else {})}


def _decimal(value, field: str) -> Decimal:
    if not isinstance(value, str):
        raise AssumptionsMutatedError(
            f"assumption {field} must be a quoted decimal string, got {type(value).__name__} "
            f"{value!r} — a float in YAML carries binary error into every present value (MO-3)")
    return Decimal(value)


def load(path: pathlib.Path) -> Assumptions:
    """Load one published set, refusing a changed value under an unchanged version."""
    doc = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    expected = content_hash(doc)
    if doc.get("content_hash") != expected:
        raise AssumptionsMutatedError(
            f"{path}: {doc.get('name')}@v{doc.get('version')} content hash "
            f"{doc.get('content_hash')!r} does not match its values ({expected}). A value "
            f"changed without a version change (F10 AC-F10.12, FE-2)")
    dr = doc["discount_rate"]
    if dr["method"] != "declared_constant":
        raise AssumptionsMutatedError(
            f"{path}: discount_rate.method {dr['method']!r} is not implemented — only "
            f"'declared_constant' (F10 D4); CAPM is a future version")
    a = Assumptions(
        name=doc["name"], version=int(doc["version"]), content_hash=expected,
        discount_method=dr["method"], discount_rate=_decimal(dr["value"], "discount_rate"),
        discount_note=dr["note"], explicit_years=int(doc["explicit_years"]),
        stage1_growth=_decimal(doc["stage1_growth"], "stage1_growth"),
        terminal_growth=_decimal(doc["terminal_growth"], "terminal_growth"),
        band_discount=tuple(_decimal(x, "band") for x in doc["band"]["discount_rate_steps"]),
        band_terminal=tuple(_decimal(x, "band") for x in doc["band"]["terminal_growth_steps"]),
        implied_low=_decimal(doc["implied_bracket"]["low"], "implied_bracket.low"),
        implied_high=_decimal(doc["implied_bracket"]["high"], "implied_bracket.high"),
        implied_iterations=int(doc["implied_bracket"]["iterations"]),
        duration_years=tuple(_years(doc["duration_table"]["explicit_years"]))
        if "duration_table" in doc else (),
        declares_duration_table="duration_table" in doc,
    )
    _check_finite(a, path)
    return a


def _years(values) -> list[int]:
    if not isinstance(values, list) or not all(isinstance(v, int) and not isinstance(v, bool)
                                               for v in values):
        raise AssumptionsMutatedError(
            f"duration_table.explicit_years must be a list of integers, got {values!r} (D10)")
    return values


def _check_finite(a: Assumptions, path) -> None:
    """`CT-F10.1` rule: terminal growth below the discount rate at EVERY grid point."""
    points = [(a.discount_rate, a.terminal_growth)] + [
        (r, g) for r in a.band_discount for g in a.band_terminal]
    bad = [(str(r), str(g)) for r, g in points if r <= g]
    if bad:
        raise NoFiniteValueError(
            f"{path}: discount rate ≤ terminal growth at {bad} — the terminal value has no "
            f"finite answer there (F10 AC-F10.3, CT-F10.1)")
    if a.explicit_years < 1 or a.implied_iterations < 1 or a.implied_low >= a.implied_high:
        raise NoFiniteValueError(f"{path}: explicit_years, iterations or bracket is empty")
    years = a.duration_years
    if a.declares_duration_table and (not years or min(years) < 1
                                      or len(set(years)) != len(years)):
        raise NoFiniteValueError(
            f"{path}: duration_table.explicit_years {list(years)} must be non-empty, distinct "
            f"and each ≥ 1 (F10 D10, CT-F10.1)")


def load_published(name: str, version: int) -> Assumptions:
    return load(CONFIG_DIR / f"{name}_v{version}.yaml")
