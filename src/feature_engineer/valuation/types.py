"""`CT-F10.2` / `CT-F10.3` — the valuation's shapes, and the `fv_model` ≠ `fv_analyst` wall.

★★ **`VS-1`: there are two fair values and they must never share a name.**
`ValuationResult` is D-02's `fv_model`, built on a judgement-free basis and
consumable by both analyst seats (`VS-2`). `AnalystValuation` is what the SAME
arithmetic returns on a basis a judgement chose (`D1`, `VS-4`) — `fv_analyst`,
readable by no analyst seat (`VS-3`). ⚠ They are distinct classes, neither a
subclass of the other, so nothing that requires one accepts the other.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from src.shared.money import Money

#: `CT-F10.3` — what a judgement basis must say about itself (`D5`).
#: ★ `computed_by` names the D-01 CODE that turned the judgement's choice into a
#: figure: no number in a basis was produced inside a prompt (`S-2`, `MP-6`).
JUDGEMENT_PROVENANCE = ("block", "prompt_version", "run_id", "stage_commit_hash",
                        "bundle_hash", "method", "window", "exclusions", "computed_by")

#: `CT-F10.2` — the omissions net debt CAN carry (`D8`, `PG-10`). ★ Which apply
#: to a given result is derived from the components it used (`basis.known_omissions`).
#: Operating leases are not here: they are excluded by design (`basis.EXCLUDED_BY_DESIGN`).
NET_DEBT_KNOWN_OMISSIONS = ("marketable_securities", "finance_leases")


@dataclass(frozen=True, slots=True)
class CashFlowBasis:
    """`CT-F10.3` — the one input shape the mechanics accept."""

    label: str
    base_fcff: Money
    origin: str                                   # "reported" | "judgement"
    provenance: dict = field(default_factory=dict)
    formula_id: str = ""
    tax_rate: Decimal | None = None
    tax_rule: str = "effective"                   # "effective" | "loss_year_zero" (`DX-104`)
    tax_inputs: dict = field(default_factory=dict)
    inputs: tuple = ()

    def __post_init__(self) -> None:
        if not isinstance(self.base_fcff, Money):
            raise TypeError("base_fcff must be Money (MO-1)")
        if self.origin not in ("reported", "judgement"):
            raise ValueError(f"origin {self.origin!r} is not 'reported' or 'judgement'")
        if self.origin == "judgement":
            missing = [k for k in JUDGEMENT_PROVENANCE if not self.provenance.get(k)
                       and k != "exclusions"]
            if "exclusions" not in self.provenance:
                missing.append("exclusions")
            if missing:
                raise ValueError(
                    f"a judgement basis must carry its provenance; missing {missing} "
                    f"(F10 CT-F10.3, D5, AC-F10.13)")

    def to_json_obj(self) -> dict:
        obj = {"label": self.label, "origin": self.origin,
               "base_fcff": self.base_fcff.to_json_obj()}
        if self.origin == "reported":
            obj.update({
                "formula_id": self.formula_id,
                "tax_rate": {"value": str(self.tax_rate), "rule": self.tax_rule,
                             **{k: v.to_json_obj() for k, v in self.tax_inputs.items()}},
                "inputs": [_input_json(i) for i in self.inputs]})
        else:
            obj["provenance"] = self.provenance
        return obj


def _input_json(i: dict) -> dict:
    out = {}
    for k, v in i.items():
        if isinstance(v, Money):
            out[k] = v.to_json_obj()
        elif isinstance(v, date):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


@dataclass(frozen=True, slots=True)
class BandPoint:
    discount_rate: Decimal
    terminal_growth: Decimal
    value_per_share: Money

    def to_json_obj(self) -> dict:
        return {"discount_rate": str(self.discount_rate),
                "terminal_growth": str(self.terminal_growth),
                "value_per_share": self.value_per_share.to_json_obj()}


@dataclass(frozen=True, slots=True)
class Band:
    grid: tuple[BandPoint, ...]
    low: Money
    high: Money

    def to_json_obj(self) -> dict:
        return {"grid": [p.to_json_obj() for p in self.grid],
                "low": self.low.to_json_obj(), "high": self.high.to_json_obj()}


@dataclass(frozen=True, slots=True)
class Implied:
    """`D7` — the stage-1 growth the price requires, or `NO_ROOT_IN_BRACKET`."""

    solves_for: str
    status: str
    value: Decimal | None
    residual: Money | None

    def __post_init__(self) -> None:
        if (self.value is None) != (self.status == "NO_ROOT_IN_BRACKET"):
            raise ValueError("implied.value is null exactly when there is no root (CT-F10.2)")

    def to_json_obj(self) -> dict:
        return {"solves_for": self.solves_for, "status": self.status,
                "value": None if self.value is None else str(self.value),
                "residual": None if self.residual is None else self.residual.to_json_obj()}


@dataclass(frozen=True, slots=True)
class DurationRow:
    """`D10` — the stage-1 growth the price requires over `explicit_years`."""

    explicit_years: int
    implied: Implied
    #: ✏ `D11` — the year-N flow at the solved growth, and it ÷ trailing revenue (FLAT revenue).
    #: Both None exactly when `implied` has no root.
    required_final_year_fcff: Money | None = None
    share_of_trailing_revenue: Decimal | None = None

    def __post_init__(self) -> None:
        solved = self.implied.value is not None
        if solved != (self.required_final_year_fcff is not None) or \
                solved != (self.share_of_trailing_revenue is not None):
            raise ValueError("D11 fields are null exactly when the row has no root (CT-F10.2)")

    def to_json_obj(self) -> dict:
        return {"explicit_years": self.explicit_years, **self.implied.to_json_obj(),
                "required_final_year_fcff": None if self.required_final_year_fcff is None
                else self.required_final_year_fcff.to_json_obj(),
                "share_of_trailing_revenue": None if self.share_of_trailing_revenue is None
                else str(self.share_of_trailing_revenue)}


def _known_limits() -> tuple[str, ...]:
    """`AC-F10.21` — what this valuation cannot compute, on the artifact (`PG-10`)."""
    from src.feature_engineer.valuation.basis import KNOWN_LIMITS
    return KNOWN_LIMITS


def _omissions(components) -> tuple[str, ...]:
    from src.feature_engineer.valuation.basis import known_omissions
    return known_omissions(components)


def _excluded_by_design() -> dict:
    from src.feature_engineer.valuation.basis import EXCLUDED_BY_DESIGN
    return dict(EXCLUDED_BY_DESIGN)


def _common_json(v) -> dict:
    return {
        "ticker": v.ticker, "as_of": v.as_of.isoformat(),
        "assumptions": v.assumptions_obj.cite(),
        "basis": v.basis.to_json_obj(),
        "flows": [f.to_json_obj() for f in v.trail.flows],
        "terminal": {"fcff_n_plus_1": v.trail.terminal_fcff.to_json_obj(),
                     "value": v.trail.terminal_value.to_json_obj(),
                     "present_value": v.trail.terminal_present_value.to_json_obj()},
        "enterprise_value": v.trail.enterprise_value.to_json_obj(),
        "net_debt": {"value": v.net_debt.to_json_obj(),
                     "components": [_input_json(c) for c in v.net_debt_components],
                     "known_omissions": list(_omissions(v.net_debt_components)),
                     "excluded_by_design": _excluded_by_design()},
        "known_limits": list(_known_limits()),
        "equity_value": v.equity_value.to_json_obj(),
        "diluted_shares": v.diluted_shares,
        "value_per_share": v.value_per_share.to_json_obj(),
        "price": {"value": v.price.to_json_obj(), "date": v.price_date.isoformat(),
                  "series": "raw"},
        "band": v.band.to_json_obj(),
        "implied": v.implied.to_json_obj(),
        "market_capitalisation": v.market_capitalisation.to_json_obj(),
        **({"implied_by_duration": [r.to_json_obj() for r in v.implied_by_duration],
            "trailing_revenue": {"value": v.trailing_revenue.to_json_obj(), "item": "revenue",
                                 "periods": "the four D6 quarters"}}
           if v.assumptions_obj.declares_duration_table else {}),
    }


@dataclass(frozen=True, slots=True)
class ValuationResult:
    """`CT-F10.2` — D-02's `fv_model`. Only `service.valuation()` builds one."""

    ticker: str
    as_of: date
    assumptions_obj: object
    basis: CashFlowBasis
    trail: object
    net_debt: Money
    net_debt_components: tuple
    equity_value: Money
    diluted_shares: int
    value_per_share: Money
    price: Money
    price_date: date
    band: Band
    implied: Implied
    market_capitalisation: Money
    implied_by_duration: tuple = ()
    trailing_revenue: Money | None = None                 # `D11`; set exactly with the table
    kind: str = "fv_model"

    def __post_init__(self) -> None:
        if self.kind != "fv_model" or self.basis.origin != "reported":
            raise ValueError(
                "a ValuationResult is fv_model on a REPORTED basis only — a judgement basis "
                "yields an AnalystValuation (F10 VS-1, AC-F10.13)")

    def to_json(self) -> str:
        return json.dumps({"kind": self.kind, **_common_json(self)}, sort_keys=True,
                          separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class AnalystValuation:
    """`fv_analyst` — the same arithmetic on a judgement's basis (`D1`, `VS-4`).

    ⚠ Owned by D-01 once returned: D-02 never stores it, never renders it into a
    bundle, and it never enters a panel (`VS-3`, `FE-21`).
    """

    ticker: str
    as_of: date
    assumptions_obj: object
    basis: CashFlowBasis
    trail: object
    net_debt: Money
    net_debt_components: tuple
    equity_value: Money
    diluted_shares: int
    value_per_share: Money
    price: Money
    price_date: date
    band: Band
    implied: Implied
    market_capitalisation: Money
    implied_by_duration: tuple = ()
    trailing_revenue: Money | None = None                 # `D11`; set exactly with the table
    kind: str = "fv_analyst"

    def __post_init__(self) -> None:
        if self.kind != "fv_analyst" or self.basis.origin != "judgement":
            raise ValueError("an AnalystValuation requires a judgement basis (F10 VS-1)")

    def to_json(self) -> str:
        return json.dumps({"kind": self.kind, **_common_json(self)}, sort_keys=True,
                          separators=(",", ":"))


def require_fv_model(value) -> ValuationResult:
    """`AC-F10.13` — the guard at every place that must receive `fv_model`."""
    if type(value) is not ValuationResult:
        raise TypeError(
            f"expected fv_model (ValuationResult), got {type(value).__name__} — fv_analyst is "
            f"a conclusion, not neutral arithmetic, and may not travel where fv_model does "
            f"(F10 VS-1, VS-3)")
    return value
