"""`T2` — base rates as an evidence-bundle part (`AC-F11.6`, `AC-F11.7`, `AC-F11.8`).

★ Returns `kind`, `pins`, `content` (the bundle type is D-01's; `AC-F11.8` forbids importing
it). `computed` is the kind the blind view withholds, so Stage A never sees a rate it could
anchor to (`RA-14`). Every rate is `hits/n`; `n = 0` reads *"no observations"* (`PG-10`).
"""

from __future__ import annotations

from collections import Counter

KIND = "computed"


def rate(c: dict) -> str:
    if not c["n"]:
        return "no observations"
    return f"{c['hits']}/{c['n']} ({100 * c['hits'] / c['n']:.1f} %)"


def _pct(text: str) -> str:
    return f"{100 * float(text):.1f} %"


def as_bundle_part(result) -> dict:
    c = result.reference_class
    years = Counter(y["member"] for y in result.member_years)
    lines = [
        f"REFERENCE-CLASS BASE RATES — {c['name']}@v{c['version']} {c['content_hash']}, "
        f"as of {result.as_of.isoformat()} (subject {result.subject})",
        "Every rate is hits/n. Each is shown for the whole class and excluding the subject. "
        "Thresholds are the subject's own F10 price requirements (D-02 implied_by_duration).",
        "",
        "MEMBERS (usable fiscal years in brackets):"]
    lines += [f"- {m['label']} — {m['name']} [{years.get(m['label'], 0)}], role {m['role']}: "
              f"{m['why']}" for m in result.members]
    if result.excluded_years:
        lines.append("  excluded years: " + "; ".join(
            f"{e['member']} FY{e['fiscal_year']} ({e['reason']})" for e in result.excluded_years))
    lines += ["", "FCFF MARGIN REACH — member-years at or above the share of revenue the price "
                  "requires in its final explicit year (at flat revenue):"]
    lines += [f"- ≥ {_pct(r['threshold'])} (the {r['periods']}-year requirement): all "
              f"{rate(r['all'])} · excluding the subject {rate(r['excluding_subject'])}"
              for r in result.margin_reach]
    lines += ["", "POSITIVE-FCFF RUNS — maximal runs of consecutive positive-FCFF fiscal years "
                  "(a loss or a missing year ends a run):"]
    lines += [f"- at least {r['at_least_years']} years: all {rate(r['all'])} · excluding the "
              f"subject {rate(r['excluding_subject'])}" for r in result.positive_runs]
    lines += ["", "REVENUE CAGR REACH — N-year windows whose revenue CAGR met the growth the "
                  "price requires (overlapping windows — observations are correlated):"]
    lines += [f"- {r['periods']} years at ≥ {_pct(r['required_growth'])}: all {rate(r['all'])} · "
              f"excluding the subject {rate(r['excluding_subject'])}"
              for r in result.revenue_cagr_reach]
    p = result.published
    if p:
        s = p["source"]
        lines += ["", f"PUBLISHED — {s['authors']}, \"{s['title']}\", {s['publisher']}, "
                      f"{s['date']}. {p['measure']}; class: {p['reference_class']}.",
                  "⚠ Caveats: these are inflation-adjusted sales growth rates (2015 dollars); the "
                  "requirement is NOMINAL FCFF growth — equal only at a constant margin and zero "
                  "inflation. The book bins growth in 5-point bands, so a rate inside a band is a "
                  "bracket, never interpolated."]
        for r in p["rows"]:
            b = r["bracket"]
            if b is None:
                lines.append(f"- {r['periods']} years at ≥ {_pct(r['required_growth'])}: the book "
                             f"has no {r['periods']}-year horizon")
                continue
            pg = r["pages"]
            hit = (f"{b['at_least']}/{b['n']}" if b["at_least"] == b["at_most"]
                   else f"between {b['at_least']}/{b['n']} and {b['at_most']}/{b['n']}")
            lines.append(f"- {r['periods']} years at ≥ {_pct(r['required_growth'])}: {hit} "
                         f"observations (rates p. {pg['rates']['printed']}, observations "
                         f"p. {pg['observations']['printed']})")
    return {"kind": KIND,
            "pins": {"contract_name": f"reference_class.{c['name']}",
                     "contract_version": c["version"]},
            "content": "\n".join(lines)}
