"""DE-68 — a combination is TWO findings, and the retired symbol keeps printing.

```text
╔══════════════════════════════════════════════════════════════════╗
║  MEASURED 2026-08-28.  EQR + AvalonBay -> VMRK, merger of equals. ║
║                                                                  ║
║    2026-08-17   EQR 63.66   AVB 65.90   <- still two companies    ║
║    2026-08-18   EQR 64.03   AVB 64.03   <- AVB now prints VMRK    ║
║    2026-08-24   EQR 68.14   AVB 68.14                             ║
║                                                                  ║
║  ★ VMRK's pre-merger closes equal EQR's 59/59 — the SURVIVOR is   ║
║    clean.  ⚠⚠ AVB's equal EQR's from the 18th — THE RETIRED SIDE  ║
║    IS NOT.  A dead ticker carrying a fabricated -2.8% return.     ║
╚══════════════════════════════════════════════════════════════════╝
```

⚠⚠ **The CIK diff cannot produce any of this.** A merger of equals and a rebrand
are the same shape in SEC's file — one CIK, new ticker — so `detect_changes`
reports *one* event where **two** names left the universe, and the retired side
never appears in the diff at all: its CIK did not change ticker, it simply stops
mattering. ★ The cause comes from a **search** (`.claude/skills/ticker-went-silent/`),
which is why every entry point here **demands its sources** and refuses without.
"""

from __future__ import annotations

from datetime import date

#: ★ The causes that retire a second ticker. ⚠ Not a taxonomy of corporate
#: actions — a rebrand is absent on purpose, because it retires nothing.
COMBINATION_CAUSES = ("merger_of_equals", "merger", "acquisition")

#: ⚠ **How many equal closes in a row stop being a coincidence.** Two REITs
#: printing the same close once is unremarkable; a run of them is the same
#: series arriving through two symbols. ★ An admitted choice (CN-10).
MIN_RUN = 2


def contaminated_from(retired, successor, *, effective: date | None = None,
                      min_run: int = MIN_RUN):
    """The first date the **retired** symbol stops carrying its own prices.

    `retired` and `successor` are `{date: close}` mappings, or anything with
    `date`/`close` columns. Returns the changeover date, or `None`.

    ★★ **This is the check with no substitute.** A retired symbol that goes
    quiet is caught by staleness (QA-125); one the vendor keeps back-filling
    with the successor's prices is caught by **nothing** — the bars are present,
    monotonic and in range, and the changeover carries a return that never
    happened. ⚠ DE-61's welding hazard with no ticker reuse involved.

    ⚠⚠ **Agreement alone is NOT contamination, and this is the trap.** *Measured
    2026-08-28:* `BK` and `BNY` agree over the **entire** window — because a
    rebrand is genuinely one series arriving through two symbols, and so is a
    merger survivor (`EQR`/`VMRK`). ★ **Contamination is a series that DIVERGES
    and then CONVERGES**; a series that never diverged is the same company.

    ⚠ A whole-overlap match is therefore **ambiguous** between *"one company"*
    and *"the window started after the changeover"*, and this returns `None`
    rather than guessing — pass `effective` (which comes from the search) to
    make the question decidable, and it **raises** when the window is too short
    to answer rather than reporting a clean `None` (P5).
    """
    from src.data_engine.errors import ContractViolationError

    left, right = _closes(retired), _closes(successor)
    shared = sorted(set(left) & set(right))
    if not shared:
        return None

    if effective is not None:
        before = [d for d in shared if d < effective]
        after = [d for d in shared if d >= effective]
        if not before:
            raise ContractViolationError(
                "combination.window",
                f"the window starts {shared[0]} — at or after the changeover "
                f"{effective} — so a contaminated symbol and a clean one look "
                f"identical. ⚠ Widen it to include bars from BEFORE the "
                f"effective date; a `None` from here would be a clean answer "
                f"to a question that was never asked (DE-68, P5)")
        if len(after) < min_run or any(left[d] != right[d] for d in after):
            return None
        # ★ The discriminator: it must have been its OWN series beforehand.
        if all(left[d] == right[d] for d in before):
            return None                    # one company throughout — a rebrand
        return after[0]

    # ★ No effective date: walk BACK from the most recent bar. Contamination,
    #   once it starts, does not stop — the vendor re-keyed the symbol.
    first = None
    for day in reversed(shared):
        if left[day] != right[day]:
            break
        first = day

    if first is None or first == shared[0]:
        # ⚠ `first == shared[0]` — the whole overlap agrees. One series, or a
        #   window that began too late to tell. Never a positive claim.
        return None
    run = sum(1 for day in shared if day >= first)
    return first if run >= min_run else None


def combination_findings(*, retired: str, successor: str, survivor_cik: str,
                         cause: str, effective: date, knowable_at: date,
                         sources, contaminated: date | None = None,
                         retired_company: str | None = None):
    """`(ticker_change, delisting)` — ★ **both, because two names left.**

    The survivor's `ticker_change` names the cause it could not derive; the
    retired side gets its own `delisting`, which **nothing else in the stack
    would ever produce** — it is invisible to the CIK diff by construction.

    ⚠ **`sources` is required and is not decoration.** The skill's rule is *do
    not write a cause into the event store without a source URL behind it*, and
    a cause is exactly what cannot be measured here.
    """
    from src.data_engine.calendar.classes import BY_NAME
    from src.data_engine.contracts import Finding
    from src.data_engine.errors import ContractViolationError

    urls = tuple(str(s) for s in (sources or ()) if str(s).strip())
    if not urls:
        raise ContractViolationError(
            "combination.sources",
            f"a {cause} for {retired}->{successor} needs its sources — the cause "
            f"is established by SEARCH, never derived (DE-68). ★ Recording it "
            f"unsourced makes a guess indistinguishable from a corroborated "
            f"finding, which is the error the ticker-went-silent skill exists "
            f"to prevent")
    if cause not in COMBINATION_CAUSES:
        raise ContractViolationError(
            "combination.cause",
            f"{cause!r} does not retire a second ticker — expected one of "
            f"{list(COMBINATION_CAUSES)}. ⚠ A rebrand retires nothing and must "
            f"not be recorded as a combination (DE-68)")

    retired, successor = retired.upper(), successor.upper()
    shared = {"cause": cause, "cik": survivor_cik, "counterparty": retired,
              "successor": successor, "sources": list(urls)}

    survivor = Finding(
        successor, "ticker_change", BY_NAME["ticker_change"].severity,
        effective, knowable_at,
        dict(shared, **{"from": retired, "to": successor}),
        f"search:{cause}")

    detail = dict(shared, retired=True)
    if retired_company:
        detail["company"] = retired_company
    if contaminated is not None:
        # ⚠⚠ The bars did not stop — they became someone else's. A consumer
        #   reading only `event_date` would trust everything after it.
        detail["contaminated_from"] = contaminated.isoformat()
    gone = Finding(
        retired, "delisting", BY_NAME["delisting"].severity,
        effective, knowable_at, detail, f"search:{cause}")

    return survivor, gone


def _closes(series) -> dict:
    """`{date: close}` from a mapping or a frame. ★ Tolerant on the way in.

    ★★ **`close_minor` is preferred over `close`** where the frame carries it
    (CT-7.1). ⚠ The whole check is an equality test, and minor units are
    **integers** — comparing floats for exact equality would make the answer
    depend on the vendor's rounding rather than on whether it is the same series.
    """
    if hasattr(series, "columns"):
        import pandas as pd
        column = "close_minor" if "close_minor" in series.columns else "close"
        return {d.date() if hasattr(d, "date") else d: c
                for d, c in zip(pd.to_datetime(series["date"]), series[column])}
    return {k.date() if hasattr(k, "date") else k: v for k, v in series.items()}


def contaminated_by(suspects: dict, successors: dict, *, min_run: int = MIN_RUN):
    """`{suspect: [(successor, changeover), …]}` — ★ **and this needs NO search.**

    `suspects` and `successors` are `{ticker: {date: close}}`. Every suspect is
    tested against every successor for the diverge-then-converge shape.

    ★★ **This is the detector the CIK diff cannot be.** `AVB` never appears in
    the diff — its CIK did not change ticker — so identity data alone can never
    surface it. ⚠ But the *prices* can: a retired name that has started printing
    another name's series is visible **from arithmetic**, with no vendor
    classification and no web search. *Measured: `AVB` → `VMRK` from 2026-08-18.*

    ★ The suspect set is small on purpose — the names the store already calls
    `delisting`, against the successors the diff already named. ⚠ It is not a
    universe-wide scan: two genuinely distinct names converging is a coincidence
    to investigate, not a finding, and the false-positive cost across 510 names
    would swamp the signal.

    ⚠ **Every match travels, never just the first.** A suspect matching two
    successors is *ambiguous* and must be visible as such — the same rule the
    rename detector follows with its `candidates`.
    """
    out = {}
    for suspect, series in sorted(suspects.items()):
        hits = []
        for successor, other in sorted(successors.items()):
            if successor == suspect:
                continue
            when = contaminated_from(series, other, min_run=min_run)
            if when is not None:
                hits.append((successor, when))
        if hits:
            out[suspect] = hits
    return out
