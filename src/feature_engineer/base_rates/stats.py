"""`CT-F11.2` — the three statistics, and the published bracket (`AC-F11.4`, `AC-F11.7`).

★ Pure counting over member-years `F10`'s `annual_history` already resolved. Every result
is `hits` and `n`, with and without the subject (§4). ⚠ No threshold is chosen here: each
arrives from the subject's own trail (`AC-F11.5`).
"""

from __future__ import annotations

from decimal import Decimal


def _split(rows, subject: str) -> dict:
    """`[(member, hit)]` → `{"all": {hits, n}, "excluding_subject": {hits, n}}`."""
    def count(sel):
        return {"hits": sum(1 for _, hit in sel if hit), "n": len(sel)}
    return {"all": count(rows), "excluding_subject": count([r for r in rows if r[0] != subject])}


def margin_reach(used: dict, thresholds, *, subject: str) -> list[dict]:
    """Member-years whose FCFF margin is at or above each required share of revenue."""
    out = []
    for periods, threshold in thresholds:
        rows = [(m, y.margin >= threshold) for m, years in used.items() for y in years]
        out.append({"threshold": str(threshold), "periods": periods, **_split(rows, subject)})
    return out


def _runs(years) -> list[int]:
    """Maximal runs of consecutive positive-FCFF fiscal years. ⚠ A loss OR a missing year
    ends a run: a gap is not evidence the run continued (`FE-14`)."""
    runs, length, last = [], 0, None
    for y in sorted(years, key=lambda y: y.fiscal_year):
        positive = y.basis.fcff.amount_minor > 0
        contiguous = last is not None and y.fiscal_year == last + 1
        if positive and (contiguous and length):
            length += 1
        elif positive:
            if length:
                runs.append(length)
            length = 1
        else:
            if length:
                runs.append(length)
            length = 0
        last = y.fiscal_year
    if length:
        runs.append(length)
    return runs


def positive_runs(used: dict, at_least, *, subject: str) -> list[dict]:
    per_member = {m: _runs(years) for m, years in used.items()}
    out = []
    for k in at_least:
        rows = [(m, run >= k) for m, runs in per_member.items() for run in runs]
        out.append({"at_least_years": k, **_split(rows, subject)})
    return out


def revenue_cagr_reach(used: dict, required, *, subject: str) -> list[dict]:
    """`periods`-year windows (every start, `D6`: overlapping) whose revenue CAGR ≥ the
    required growth — compared as `end ÷ start ≥ (1 + g)^N`, exact in `Decimal`."""
    out = []
    for periods, growth in required:
        rows = []
        for m, years in used.items():
            by_year = {y.fiscal_year: y for y in years}
            for start, y0 in by_year.items():
                y1 = by_year.get(start + periods)
                if y1 is None or y0.basis.revenue.amount_minor <= 0:
                    continue
                ratio = Decimal(y1.basis.revenue.amount_minor) / Decimal(
                    y0.basis.revenue.amount_minor)
                rows.append((m, ratio >= (1 + growth) ** periods))
        out.append({"periods": periods, "required_growth": str(growth), **_split(rows, subject),
                    "windows": "overlapping"})
    return out


def published_bracket(table, periods: int, growth: Decimal) -> dict | None:
    """Observations at or above `growth`, as `[at_least, at_most]` of `n` — never
    interpolated inside a 5-point bin (`CT-F11.3`). None when the book has no such horizon."""
    horizon = next((h for h in table.horizons if int(h["years"]) == periods), None)
    if horizon is None:
        return None

    def at_or_above(edge: Decimal) -> int:
        return sum(int(b["observations"]) for b in horizon["bins"]
                   if b["low"] is not None and Decimal(b["low"]) >= edge)

    holding = next(b for b in horizon["bins"]
                   if (b["low"] is None or Decimal(b["low"]) <= growth)
                   and (b["high"] is None or growth < Decimal(b["high"])))
    low = Decimal(holding["low"]) if holding["low"] is not None else None
    high = Decimal(holding["high"]) if holding["high"] is not None else None
    at_most = int(horizon["total"]) if low is None else at_or_above(low)
    at_least = 0 if high is None else at_or_above(high)
    if low is not None and low == growth:
        at_least = at_most                                   # exactly on an edge: exact
    return {"at_least": at_least, "at_most": at_most, "n": int(horizon["total"])}
