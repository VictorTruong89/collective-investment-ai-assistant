"""`RM-13` — what a thesis's own falsifiers have done since it was written.

★★ **What this settles and what it cannot.** `RM-13` asks for the ratio of theses that DIED BY
THEIR OWN STATED CONDITION to those quietly abandoned — *"a high abandonment rate means the
falsifiers were decorative"*. That ratio needs each condition RESOLVED, and resolving it needs
two things: the observable's values since the thesis was written, and a rule for reading them.

★ **The first half is arithmetic and lives here**: every `Falsifier` names an
`observable_field` and a `deadline` (`RA-35`), so the series D-07 has published since the
thesis's `as_of` can be pulled deterministically, per reported period, with no judgement.

⚠⚠ **The second half is NOT deterministic today, and this module says so rather than
guessing.** A condition is PROSE — *"…is positive in each of the four quarters reported after
2025-06-26, and the sum of the four exceeds $5bn"*. Deciding it needs a threshold, a
comparator and a window, and parsing them out of a sentence is exactly the *"plausible
default"* `P5` forbids. So a check returns `DECIDABLE_BY_READER` with the evidence laid out,
and only a `test` the thesis itself carries (a future `J-15` version, L3 `DX-125`) makes it
`FIRED` / `HELD` automatically.

★ The MU thesis's falsifiers #1 and #2 were resolved BY HAND on 2026-09-15 from exactly this
table; the point of this module is that the hand step is the reading, not the gathering.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: What a check can conclude. ★ `DECIDABLE_BY_READER` is a real outcome, not a failure: the
#: evidence is complete and the reading is a person's (or a later `J-15` `test`).
FIRED, HELD, DECIDABLE_BY_READER, NO_DATA = "FIRED", "HELD", "DECIDABLE_BY_READER", "NO_DATA"
#: ★ `DX-139` — the window has not finished reporting and the answer is not yet final.
#: ⚠ Neither FIRED nor HELD: a falsifier still waiting has not held, and has not fired.
PENDING = "PENDING"


@dataclass(frozen=True, slots=True)
class Observation:
    """One reported period's value of the observable, as D-07 published it."""

    period_end: date
    filing_date: date
    value: float | None

    def to_json_obj(self) -> dict:
        return {"period_end": self.period_end.isoformat(),
                "filing_date": self.filing_date.isoformat(), "value": self.value}


@dataclass(frozen=True, slots=True)
class FalsifierCheck:
    """One falsifier, its evidence since the thesis, and what that supports."""

    ordinal: int
    condition: str
    observable_field: str
    deadline: date
    status: str
    observations: tuple[Observation, ...]
    note: str = ""

    @property
    def past_deadline(self) -> bool:
        return self.as_of_check > self.deadline

    as_of_check: date = date.min

    def to_json_obj(self) -> dict:
        return {"ordinal": self.ordinal, "condition": self.condition,
                "observable": self.observable_field, "deadline": self.deadline.isoformat(),
                "status": self.status, "note": self.note,
                "checked_at": self.as_of_check.isoformat(),
                "observations": [o.to_json_obj() for o in self.observations]}


def observations_since(rows, field: str, *, after: date, until: date) -> tuple[Observation, ...]:
    """Every reported period of `field` published after the thesis and knowable at `until`.

    ⚠ `filing_date <= until` as well as `period_end > after`: a period the market could not
    have read yet is not evidence a falsifier has resolved (`INV-1`, one direction later).
    """
    if rows is None or not len(rows):
        return ()
    column = f"{field}_minor"
    out = []
    for _index, row in rows.iterrows():
        period_end, filed = _day(row["period_end"]), _day(row["filing_date"])
        if period_end <= after or filed > until:
            continue
        value = _value(row.get(column))
        out.append(Observation(period_end, filed, value))
    return tuple(sorted(out, key=lambda o: o.period_end))


def _value(raw) -> float | None:
    """Major units, or `None`. ⚠ `raw != raw` is the usual NaN idiom and it RAISES on pandas'
    `NA` ("boolean value of NA is ambiguous") — the trap `for_ticker._missing` already records,
    and it bit here on the first run."""
    if raw is None:
        return None
    try:
        if bool(raw != raw):
            return None
    except TypeError:                      # pandas NA — an ambiguous truth IS missing
        return None
    return float(raw) / 100.0


def _day(value) -> date:
    """⚠ `RA-45` — D-01 imports no pandas, not even for a timestamp. ★ An ISO prefix is all a
    date needs, and `str(...)` handles a `Timestamp`, a `date` and a string alike."""
    return value if type(value) is date else date.fromisoformat(str(value)[:10])


#: ★★ `DX-128` — the declared grammar a STRUCTURED test may use. Deliberately small: it covers
#: what `J-15`'s own four properties need (`RA-35`) and nothing more, because every operator
#: added here is one a reader must learn before they can trust a FIRED.
#:
#: ```text
#:   test    = {"window_periods": n, "clauses": [clause, ...]}      all clauses ⇒ FIRED
#:   clause  = {"mode": "each" | "any" | "consecutive" | "sum" | "rises_each",
#:              "per_period": [{"expr": [{"field": F, "sign": 1|-1}, ...],
#:                              "op": ">" "<" ">=" "<=", "value": <major units>}],
#:              "consecutive": n}              # mode "consecutive" only
#: ```
#: ⚠ `per_period` conditions are ANDed WITHIN one period, so *"debt above $22bn while cash is
#: below $6bn"* is one clause and cannot be satisfied by two different quarters.
OPERATORS = {">": lambda a, b: a > b, "<": lambda a, b: a < b,
             ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b}

#: The clause modes `evaluate_test` decides. ★ `J-15 v2`'s schema enumerates exactly these.
MODES = ("each", "any", "consecutive", "sum", "rises_each")
#: Modes that read ONE series, so they take exactly one per-period condition.
_SINGLE_SERIES = ("sum", "rises_each")
#: A window longer than this asks for years of filings no deadline can wait for.
MAX_WINDOW = 12


def validate_test(test: dict, *, observables=None) -> list[str]:
    """★ `J-15 v2` — every way a structured test can be undecidable, named. Empty means valid.

    ⚠ `evaluate_test` assumes a well-formed test and would raise mid-check (or silently
    unpack the wrong condition) on a bad one. A model-authored test is therefore checked
    HERE, at authoring time, so a test that cannot decide its condition stops the run
    before the verdict (`RA-16`) rather than on the day the falsifier is checked.
    `observables`, when given, is the field list the test may read (`RA-35`).
    """
    problems: list[str] = []
    window = test.get("window_periods")
    if not isinstance(window, int) or isinstance(window, bool) or not 1 <= window <= MAX_WINDOW:
        problems.append(f"window_periods {window!r} is not an integer in 1..{MAX_WINDOW}")
    clauses = test.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        return [*problems, "a test needs at least one clause"]
    for n, clause in enumerate(clauses, start=1):
        mode = clause.get("mode")
        conditions = clause.get("per_period") or []
        if mode not in MODES:
            problems.append(f"clause {n}: mode {mode!r} is not one of {MODES}")
        if not conditions:
            problems.append(f"clause {n}: no per-period condition")
        if mode in _SINGLE_SERIES and len(conditions) != 1:
            problems.append(f"clause {n}: mode {mode!r} reads one series, so it takes "
                            f"exactly one condition, not {len(conditions)}")
        if mode == "consecutive":
            run = clause.get("consecutive")
            if not isinstance(run, int) or isinstance(run, bool) or run < 2:
                problems.append(f"clause {n}: mode 'consecutive' needs `consecutive` >= 2, "
                                f"got {run!r}")
        for m, condition in enumerate(conditions, start=1):
            where = f"clause {n} condition {m}"
            if condition.get("op") not in OPERATORS:
                problems.append(f"{where}: op {condition.get('op')!r} is not one of "
                                f"{tuple(OPERATORS)}")
            value = condition.get("value")
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                problems.append(f"{where}: value {value!r} is not a number")
            terms = condition.get("expr") or []
            if not terms:
                problems.append(f"{where}: an empty expression reads nothing")
            for term in terms:
                if term.get("sign", 1) not in (1, -1):
                    problems.append(f"{where}: sign {term.get('sign')!r} is not 1 or -1")
                if observables is not None and term.get("field") not in observables:
                    problems.append(f"{where}: field {term.get('field')!r} is not a published "
                                    f"observable")
    return problems


def fields_in(test: dict) -> tuple[str, ...]:
    """Every field a test reads — what the checker must gather before it can decide."""
    out = []
    for clause in test.get("clauses", ()):
        for condition in clause.get("per_period", ()):
            out.extend(term["field"] for term in condition.get("expr", ()))
    return tuple(dict.fromkeys(out))


def _expr_value(period: dict, expr) -> float | None:
    total = 0.0
    for term in expr:
        value = period["values"].get(term["field"])
        if value is None:
            return None
        total += float(term.get("sign", 1)) * value
    return total


def _holds(period: dict, condition: dict) -> bool | None:
    value = _expr_value(period, condition["expr"])
    if value is None:
        return None
    return OPERATORS[condition["op"]](value, float(condition["value"]))


def evaluate_test(test: dict, periods: list[dict]) -> tuple[str, str]:
    """`(status, why)` — `FIRED` when every clause holds, `HELD` when one does not.

    ⚠ `NO_DATA` when a field the test names never reported: a condition that could not be
    evaluated has NOT held, and saying `HELD` there would count silence as evidence.

    ★★ `DX-139` — a window that has not finished reporting is decided only where the answer
    is ALREADY final. One failing period settles an `each`/`rises_each` clause; one
    satisfying period (or run) settles an `any`/`consecutive` clause; a `sum` waits. Every
    other case is `PENDING`. ⚠ Found by the first live `J-15 v2` call: "above $1bn in each
    of the next EIGHT quarters" was FIRED on four.
    """
    want = test.get("window_periods", len(periods))
    window = periods[:want] if periods else []
    if not window:
        return NO_DATA, "no reported period in the window"
    complete = len(window) >= want
    waiting = []
    for index, clause in enumerate(test.get("clauses", ()), start=1):
        verdict, why = _clause(clause, window, complete, index)
        if verdict in (NO_DATA, HELD):
            return verdict, why
        if verdict == PENDING:
            waiting.append(index)
    if waiting:
        return PENDING, (f"{len(window)} of {want} period(s) reported; clause(s) "
                         f"{waiting} cannot be decided until the window completes")
    return FIRED, f"every clause holds over {len(window)} reported period(s)"


def _clause(clause: dict, window: list[dict], complete: bool, index: int) -> tuple[str, str]:
    """One clause → `FIRED` (holds), `HELD` (fails), `PENDING` or `NO_DATA`."""
    mode = clause["mode"]
    if mode in ("rises_each", "sum"):
        (condition,) = clause["per_period"]
        values = [_expr_value(p, condition["expr"]) for p in window]
        if any(v is None for v in values):
            return NO_DATA, f"clause {index}: the series is incomplete"
        if mode == "rises_each":
            if len(values) < 2 and complete:
                return NO_DATA, f"clause {index}: the series is incomplete"
            if not all(b > a for a, b in zip(values, values[1:], strict=False)):
                return HELD, f"clause {index}: the series does not rise in every period"
            return (FIRED, "") if complete else (PENDING, "")
        if not complete:
            return PENDING, ""
        if not OPERATORS[condition["op"]](sum(values), float(condition["value"])):
            return HELD, f"clause {index}: the sum {sum(values):,.0f} fails the threshold"
        return FIRED, ""
    per_period = [all(_holds(p, c) for c in clause["per_period"])
                  if all(_holds(p, c) is not None for c in clause["per_period"]) else None
                  for p in window]
    if all(v is None for v in per_period):
        return NO_DATA, f"clause {index}: no period reported every field it names"
    truth = [bool(v) for v in per_period]
    if mode == "each":
        if not all(truth):
            return HELD, f"clause {index}: it does not hold in every period"
        return (FIRED, "") if complete else (PENDING, "")
    if mode == "any":
        if any(truth):
            return FIRED, ""
        return (HELD, f"clause {index}: it holds in no period") if complete else (PENDING, "")
    if mode == "consecutive":
        need = int(clause.get("consecutive", 2))
        runs = max((sum(1 for _ in group) for value, group in _runs(truth) if value), default=0)
        if runs >= need:
            return FIRED, ""
        return ((HELD, f"clause {index}: the longest run is {runs}, not {need}") if complete
                else (PENDING, ""))
    raise ValueError(f"clause {index}: mode {mode!r} is not one of {MODES}")


def _runs(values):
    from itertools import groupby
    return groupby(values)


def series(rows, fields, *, after: date, until: date) -> list[dict]:
    """One entry per reported period, carrying every field a test names."""
    by_period: dict[date, dict] = {}
    for field in fields:
        for observation in observations_since(rows, field, after=after, until=until):
            entry = by_period.setdefault(observation.period_end,
                                         {"period_end": observation.period_end,
                                          "filing_date": observation.filing_date, "values": {}})
            entry["values"][field] = observation.value
    return [by_period[k] for k in sorted(by_period)]


def check(thesis, rows, *, as_of: date, tests: dict | None = None) -> tuple[FalsifierCheck, ...]:
    """Every falsifier of `thesis`, with the evidence published since it was written.

    ★ Deterministic end to end: no model, no threshold guessed from prose. A falsifier whose
    observable has reported nothing new is `NO_DATA`; one with data is `DECIDABLE_BY_READER`
    until a structured `test` exists to decide it (`DX-125`).
    """
    tests = tests or {}
    out = []
    for falsifier in thesis.falsifiers:
        seen = observations_since(rows, falsifier.observable_field,
                                  after=thesis.as_of, until=as_of)
        test = tests.get(str(falsifier.ordinal)) or tests.get(falsifier.ordinal)
        if test:
            # ★ `DX-128` — a structured test decides; the prose stays the human statement.
            status, why = evaluate_test(test, series(rows, fields_in(test),
                                                after=thesis.as_of, until=as_of))
            note = f"{why} (structured test: {test.get('source', 'supplied')})"
            if as_of > falsifier.deadline:
                note += f" ⚠ past its {falsifier.deadline} deadline"
            out.append(FalsifierCheck(
                ordinal=falsifier.ordinal, condition=falsifier.condition,
                observable_field=falsifier.observable_field, deadline=falsifier.deadline,
                status=status, observations=seen, note=note, as_of_check=as_of))
            continue
        reported = [o for o in seen if o.value is not None]
        if not reported:
            status, note = NO_DATA, (
                f"{falsifier.observable_field} has reported no new period since "
                f"{thesis.as_of}")
        else:
            status, note = DECIDABLE_BY_READER, (
                f"{len(reported)} reported period(s); the condition states a threshold this "
                f"code does not parse — a reader (or a J-15 `test`) decides (DX-125)")
            if as_of > falsifier.deadline:
                note += f" ⚠ past its {falsifier.deadline} deadline"
        out.append(FalsifierCheck(
            ordinal=falsifier.ordinal, condition=falsifier.condition,
            observable_field=falsifier.observable_field, deadline=falsifier.deadline,
            status=status, observations=seen, note=note, as_of_check=as_of))
    return tuple(out)


def summary(checks) -> dict:
    """`RM-13`'s counters — ⚠ `decidable` is NOT `fired`, and is never reported as one."""
    counts: dict[str, int] = {}
    for c in checks:
        counts[c.status] = counts.get(c.status, 0) + 1
    return {"falsifiers": len(tuple(checks)), **counts,
            "note": ("RM-13's ratio needs FIRED vs quietly-abandoned; a DECIDABLE_BY_READER "
                     "count is the work remaining, not a result")}
