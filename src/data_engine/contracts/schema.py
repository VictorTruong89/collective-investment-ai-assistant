"""The contract mechanism — a declared schema, validated at the boundary (CA-8).

★ WHY A HELPER AND NOT SIX HAND-WRITTEN VALIDATORS.
L4 **CA-8** says a DataFrame crossing a domain boundary carries a declared
schema, dtypes and units, "validated at the boundary, not assumed". Six
hand-written validators drift: five of them check dtype and the sixth forgets,
and the one that forgets is the one that ships an ``object``-dtype price column
which arithmetically "works" and produces garbage (**PD-17**).

★ WHY THE CURRENCY SIBLING IS CHECKED BY THE MECHANISM AND NOT PER CONTRACT.
`CT-M.1` makes ``<name>_minor`` + ``<name>_currency`` one value in two columns.
A schema that can declare the first without the second lets a contract be
written that violates INV-001 — so the pairing is enforced by :class:`Schema`
itself, where it cannot be forgotten (AC-7.14).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.data_engine.errors import ContractViolationError, MissingCurrencyError


@dataclass(frozen=True, slots=True)
class Column:
    """One declared column.

    `unit` is not decoration. **CN-8**: a number carries its unit in its name,
    and a `_BPS`/`_PCT` mix-up has already produced a 3.2x error in this repo.
    Recording it on the contract is what lets a reader check the name.
    """

    name: str
    dtype: str
    unit: str = ""
    nullable: bool = False
    note: str = ""


@dataclass(frozen=True, slots=True)
class Schema:
    """A contract: an ordered column list plus the checks that are not per-column."""

    contract_id: str            # "CT-7.1"
    title: str
    columns: tuple[Column, ...]
    key: tuple[str, ...] = ()
    monetary: tuple[str, ...] = field(default=())   # base names, e.g. ("open", "close")

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.columns)

    def column(self, name: str) -> Column:
        for c in self.columns:
            if c.name == name:
                return c
        raise KeyError(name)

    # -- validation --------------------------------------------------------- #

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Raise unless `df` satisfies this contract; return it unchanged.

        Returns the frame so a caller can write ``df = schema.validate(df)`` and
        have the check be impossible to leave out by accident. It does not copy:
        validation is a check, and a silently-copied frame would make **PD-14**
        harder to reason about, not easier.
        """
        self._check_columns(df)
        self._check_dtypes(df)
        self._check_currency_siblings(df)
        self._check_nulls(df)
        self._check_key(df)
        return df

    def _check_columns(self, df: pd.DataFrame) -> None:
        missing = [n for n in self.names if n not in df.columns]
        if missing:
            # PD-18: a column that must exist is CHECKED, not filtered. Filtering
            # produces a smaller, silently different frame — the D-17 defect.
            raise ContractViolationError(
                self.contract_id,
                f"missing required column(s) {missing}; present: {sorted(df.columns)}",
            )
        extra = [c for c in df.columns if c not in self.names]
        if extra:
            raise ContractViolationError(
                self.contract_id,
                f"undeclared column(s) {extra}. An undeclared column crossing a "
                f"domain boundary is an untyped API field (CA-8)",
            )

    def _check_dtypes(self, df: pd.DataFrame) -> None:
        for col in self.columns:
            actual = str(df[col.name].dtype)
            if not _dtype_ok(actual, col.dtype):
                raise ContractViolationError(
                    self.contract_id,
                    f"column {col.name!r} has dtype {actual!r}, contract declares "
                    f"{col.dtype!r}. An object-dtype numeric column arithmetically "
                    f"'works' and produces garbage (PD-17)",
                )

    def _check_currency_siblings(self, df: pd.DataFrame) -> None:
        for base in self.monetary:
            if f"{base}_minor" in df.columns and f"{base}_currency" not in df.columns:
                raise MissingCurrencyError(self.contract_id, base)

    def _check_nulls(self, df: pd.DataFrame) -> None:
        for col in self.columns:
            if col.nullable:
                continue
            n = int(df[col.name].isna().sum())
            if n:
                raise ContractViolationError(
                    self.contract_id,
                    f"column {col.name!r} has {n} null value(s) and is not nullable. "
                    f"Missing is null and null is not permitted here — it is neither "
                    f"0 nor '' (DE-14)",
                )

    def _check_key(self, df: pd.DataFrame) -> None:
        if not self.key:
            return
        dupes = int(df.duplicated(subset=list(self.key)).sum())
        if dupes:
            raise ContractViolationError(
                self.contract_id,
                f"{dupes} duplicate row(s) on key {self.key}. A duplicate key "
                f"silently multiplies rows on the next merge and the result still "
                f"looks like a panel (PD-11)",
            )

    # -- construction ------------------------------------------------------- #

    def empty(self) -> pd.DataFrame:
        """An empty frame with the declared dtypes.

        ⚠ Used for *"nothing was knowable at that as_of"* — `DATA.PIT.EMPTY_AS_OF`
        is a WARNING, not an error (§10). An empty frame with the right dtypes is
        a correct answer; an empty frame with object columns is a landmine.
        """
        return pd.DataFrame({c.name: pd.Series(dtype=_pandas_dtype(c.dtype))
                             for c in self.columns})


#: Contract dtype -> the pandas dtype strings that satisfy it. Written out
#: rather than inferred because "int64 is close enough to float64" is exactly
#: the reasoning that lets a share count arrive as 2.458e9.
_ACCEPTED = {
    "int64":     {"int64", "Int64"},
    "float64":   {"float64", "Float64"},
    "bool":      {"bool", "boolean"},
    "string":    {"object", "string"},
    # date32 is datetime64[ns] and NOT object. A column of python `date`
    # objects is object-dtype, sorts by repr, and compares to a Timestamp
    # inconsistently — accepting it here would make PD-17 unenforceable on
    # the one dtype every PIT filter runs against.
    "date32":    {"datetime64[ns]"},
    "timestamp": {"datetime64[ns, UTC]", "datetime64[us, UTC]"},
}

_PANDAS = {
    "int64": "int64", "float64": "float64", "bool": "bool", "string": "object",
    "date32": "datetime64[ns]", "timestamp": "datetime64[ns, UTC]",
}


def _dtype_ok(actual: str, declared: str) -> bool:
    return actual in _ACCEPTED[declared]


def _pandas_dtype(declared: str) -> str:
    return _PANDAS[declared]


def as_date32(values) -> "pd.Series":
    """Coerce to the ONE datetime resolution `date32` accepts.

    ⚠ pandas 2 infers ``datetime64[s]`` from a scalar `datetime.date` and
    ``datetime64[ns]`` from a string, so a panel's dtype ends up depending on
    which shape the producer happened to build it from. That is not cosmetic:
    two panels over the same dates in different resolutions are different bytes
    on disk, and AC-7.19's "re-running ingest produces identical files" would
    fail for a reason that has nothing to do with the data (INV-2).
    """
    return pd.to_datetime(values).astype("datetime64[ns]")


def as_utc_timestamp(values) -> "pd.Series":
    """The same coercion for `timestamp` columns — DE-4, UTC at the boundary."""
    out = pd.to_datetime(values, utc=True)
    return out.astype("datetime64[ns, UTC]")
