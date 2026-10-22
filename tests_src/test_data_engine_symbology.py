"""D-07 §6B — identity. AC-7.78…7.83, DE-61…66."""
from datetime import date

import pytest

from src.data_engine.calendar.classes import BY_NAME
from src.data_engine.contracts import BLOCK
from src.data_engine.symbology.detect import (
    close_out, detect_changes, mappings_from, sec_snapshot,
)
from src.data_engine.symbology.master import (
    SymbolHistory, current_symbol, fetch_symbol_for, resolve,
)

TODAY = date(2026, 8, 28)
BNY_CIK, ECHO_CIK = "0001390777", "0001415404"


def _history(tmp_path, rows):
    history = SymbolHistory(tmp_path)
    history.append(rows)
    return history


# --------------------------------------------------------------------------- #
# ★★★ AC-7.78 / AC-7.79 — detection
# --------------------------------------------------------------------------- #

def test_a_ticker_moving_under_a_stable_cik_is_a_ticker_change():
    """AC-7.78 — same CIK, ticker no longer listed ⇒ `ticker_change` naming the
    successor. ★ Verified against the live SEC file: `BK`→`BNY` and
    `SATS`→`ECHO`, recovered from this repo's own stored universe."""
    findings, _ = detect_changes(
        {BNY_CIK: "BK", ECHO_CIK: "SATS"},
        {BNY_CIK: ["BNY", "BNY-PK"], ECHO_CIK: ["ECHO"]}, knowable_at=TODAY)

    assert [(f.detail["from"], f.detail["to"]) for f in findings] == [
        ("BK", "BNY"), ("SATS", "ECHO")]
    assert all(f.event_class == "ticker_change" for f in findings)


def test_a_registrants_other_securities_are_not_renames():
    """AC-7.78 — ⚠⚠ **the bug the first cut shipped with.** Testing equality
    instead of membership produced **79 false renames out of 507 names**: `WFC`
    "became" `WFC-PA`, `BRK-B` "became" `BRK-A`, `GOOGL` "became" `GOOGM`.

    ★ A CIK is a REGISTRANT — 1 443 of the 8 004 in the live file carry more
    than one security (preferred, warrants, share classes). That is QD-17, and
    it is fatal on the first run, not a future concern."""
    findings, _ = detect_changes(
        {"0000072971": "WFC", "0001067983": "BRK-B", "0001652044": "GOOGL"},
        {"0000072971": ["WFC", "WFC-PY", "WFC-PA"],
         "0001067983": ["BRK-B", "BRK-A"],
         "0001652044": ["GOOGL", "GOOG", "GOOGN", "GOOGM"]}, knowable_at=TODAY)
    assert findings == []


def test_an_ambiguous_successor_is_flagged_not_decided():
    """DE-62 — the primary is **SEC's own first listing**, and the whole
    candidate set travels with the finding so ambiguity is visible."""
    findings, _ = detect_changes({BNY_CIK: "BK"},
                                 {BNY_CIK: ["BNY", "BNY-PK"]}, knowable_at=TODAY)
    detail = findings[0].detail
    assert detail["to"] == "BNY"
    assert detail["candidates"] == ["BNY", "BNY-PK"] and detail["ambiguous"] is True


def test_a_vanished_cik_is_a_candidate_and_never_a_delisting():
    """AC-7.79 — ⚠⚠ *Measured 2026-08-28:* `XOM`'s CIK is absent from the SEC
    file **and Exxon Mobil prices normally, 41 bars to 2026-08-27**. Treating a
    vanished CIK as a delisting would have dropped the largest US oil company.

    ★ `AVB` makes the same point from the other side: delisted at FMP on the
    17th and still present in SEC's file on the 28th (DE-62, DE-35)."""
    findings, vanished = detect_changes({"0000034088": "XOM"}, {}, knowable_at=TODAY)

    assert findings == []                       # ★ NOT a finding
    assert vanished == {"0000034088": "XOM"}    # ⚠ a candidate, separately


def test_ticker_change_is_block_severity():
    """AC-7.83 / DE-66 — a run whose universe names a retired symbol fetches a
    truncated series and loses the name to staleness while universe_n counts
    it."""
    assert BY_NAME["ticker_change"].severity == BLOCK
    assert BY_NAME["ticker_change"].number == 18


# --------------------------------------------------------------------------- #
# ★★ AC-7.80 — point-in-time resolution, and ticker REUSE
# --------------------------------------------------------------------------- #

def test_resolve_returns_the_instrument_that_held_the_ticker_then(tmp_path):
    """AC-7.80 — ★★ the reuse case, which is why this cannot be a plain dict.

    ⚠ `S` was **Sears Roebuck**, became **Sprint** in 2005, and has been
    **SentinelOne** since 2021. Asking *"who was `S` in 2004?"* with today's map
    answers SentinelOne about a series that is Sears — look-ahead in the
    identity layer (DE-65, INV-1)."""
    history = _history(tmp_path, [
        {"cik": "0000319256", "ticker": "S", "valid_from": date(1990, 1, 1),
         "valid_to": date(2005, 8, 12), "knowable_at": date(1990, 1, 1),
         "source": "test"},
        {"cik": "0000101830", "ticker": "S", "valid_from": date(2005, 8, 13),
         "valid_to": date(2020, 4, 1), "knowable_at": date(2005, 8, 13),
         "source": "test"},
        {"cik": "0001583708", "ticker": "S", "valid_from": date(2021, 6, 30),
         "valid_to": None, "knowable_at": date(2021, 6, 30), "source": "test"},
    ])

    assert resolve(history, "S", as_of=date(2004, 1, 1)) == "0000319256"   # Sears
    assert resolve(history, "S", as_of=date(2010, 1, 1)) == "0000101830"   # Sprint
    assert resolve(history, "S", as_of=date(2026, 1, 1)) == "0001583708"   # SentinelOne


def test_a_mapping_not_yet_knowable_does_not_apply(tmp_path):
    """DE-65 — ⚠ knowability, not the effective date. A mapping we could not
    have had at `as_of` is look-ahead exactly as a fact would be."""
    history = _history(tmp_path, [
        {"cik": BNY_CIK, "ticker": "BNY", "valid_from": date(2026, 6, 30),
         "valid_to": None, "knowable_at": date(2026, 8, 28), "source": "test"}])
    assert resolve(history, "BNY", as_of=date(2026, 7, 1)) is None


def test_an_unknown_ticker_resolves_to_none_not_a_guess(tmp_path):
    """DE-65 / P5 — `None`, never the nearest plausible owner."""
    assert resolve(_history(tmp_path, []), "NOPE", as_of=TODAY) is None


# --------------------------------------------------------------------------- #
# ★ AC-7.81 / AC-7.82 — retrieval
# --------------------------------------------------------------------------- #

def test_the_fetch_symbol_is_the_current_one(tmp_path):
    """AC-7.81 / DE-63 — ★ *Measured over 2026-01-01…2026-08-27:* `BNY` returns
    **164 bars including the whole `BK` period**; `BK` returns 122 and stops at
    the changeover. The current symbol is one continuous series."""
    history = _history(tmp_path, [
        {"cik": BNY_CIK, "ticker": "BK", "valid_from": date(2007, 7, 1),
         "valid_to": date(2026, 6, 29), "knowable_at": date(2007, 7, 1),
         "source": "test"},
        {"cik": BNY_CIK, "ticker": "BNY", "valid_from": date(2026, 6, 30),
         "valid_to": None, "knowable_at": date(2026, 6, 30), "source": "test"},
    ])
    assert fetch_symbol_for(history, "BK", as_of=TODAY) == "BNY"
    assert current_symbol(history, BNY_CIK) == "BNY"


def test_an_unmapped_ticker_is_fetched_as_named(tmp_path):
    """DE-63 — ★ a name we hold no mapping for is fetched under its own symbol.
    An empty history is a no-op, not a behaviour change."""
    assert fetch_symbol_for(_history(tmp_path, []), "NVDA", as_of=TODAY) == "NVDA"


def test_ac_7_100_a_share_class_that_still_trades_is_fetched_as_named(tmp_path):
    """AC-7.100 / DE-82 — ★★ SEC lists GOOG and GOOGL under ONE CIK. *Found on the
    first live card (DX-170):* both were fetched as GOOGL — 138 duplicate rows per
    pair, refused by CT-7.1. A retired ticker still follows its CIK forward."""
    cik, opened = "0001652044", date(2026, 10, 7)
    history = _history(tmp_path, [
        {"cik": cik, "ticker": "GOOGL", "valid_from": opened, "valid_to": None,
         "knowable_at": opened, "source": "test"},
        {"cik": cik, "ticker": "GOOG", "valid_from": opened, "valid_to": None,
         "knowable_at": opened, "source": "test"},
        {"cik": BNY_CIK, "ticker": "BK", "valid_from": None,
         "valid_to": date(2026, 6, 29), "knowable_at": date(2026, 6, 30), "source": "test"},
        {"cik": BNY_CIK, "ticker": "BNY", "valid_from": date(2026, 6, 30),
         "valid_to": None, "knowable_at": date(2026, 6, 30), "source": "test"},
    ])
    as_of = date(2026, 10, 20)
    assert fetch_symbol_for(history, "GOOG", as_of=as_of) == "GOOG"
    assert fetch_symbol_for(history, "GOOGL", as_of=as_of) == "GOOGL"
    assert fetch_symbol_for(history, "BK", as_of=as_of) == "BNY"


def test_there_is_no_splice_function():
    """AC-7.82 / DE-64 — ⚠⚠ stated as a test because the obvious implementation
    is to concatenate old + new.

    *Measured:* the overlapping bars agree on OHLC and **disagree on volume**
    (`BK` 2 790 284 vs `BNY` 2 790 283; `ECHO` rounded to hundreds). A splice
    puts a volume step at the changeover into `volume.split_adjusted_zscore.v1`
    that reads as a liquidity event and is an artefact of the join."""
    import src.data_engine.symbology.master as master

    assert not [n for n in dir(master) if "splice" in n or "concat" in n]


# --------------------------------------------------------------------------- #
# CT-7.8 — the store
# --------------------------------------------------------------------------- #

def test_the_history_is_append_only(tmp_path):
    """CT-7.8 — a correction appends; ★ exact duplicates collapse, so a repeated
    snapshot does not grow the table without bound."""
    rows = mappings_from({BNY_CIK: ["BNY"]}, knowable_at=TODAY)
    history = SymbolHistory(tmp_path)
    history.append(rows)
    history.append(rows)
    assert len(history.read()) == 1


def test_a_snapshot_expands_every_ticker_a_registrant_lists(tmp_path):
    """CT-7.8 — ⚠ one row per (cik, ticker); a registrant's preferred shares are
    mappings too, and dropping them is what caused the 79 false renames."""
    rows = mappings_from({BNY_CIK: ["BNY", "BNY-PK"]}, knowable_at=TODAY)
    assert sorted(r["ticker"] for r in rows) == ["BNY", "BNY-PK"]


def test_close_out_stamps_the_retired_symbol(tmp_path):
    """CT-7.8 — ★ the retirement is appended, never edited in place."""
    history = _history(tmp_path, mappings_from({BNY_CIK: ["BNY"]}, knowable_at=TODAY))
    findings, _ = detect_changes({BNY_CIK: "BK"}, {BNY_CIK: ["BNY"]},
                                 knowable_at=TODAY)
    close_out(history, findings, on=TODAY)
    frame = history.read()
    retired = frame[frame["ticker"] == "BK"]
    assert len(retired) == 1 and str(retired.iloc[0]["valid_to"])[:10] == "2026-08-28"


def test_the_sec_fetch_refuses_an_unwrapped_contact():
    """DE-8 — ★ the SEC User-Agent email is in the same class as an API key."""
    with pytest.raises(TypeError, match="must be a Secret"):
        sec_snapshot("victor@example.com")


# --------------------------------------------------------------------------- #
# DE-68 — a combination is two findings, and the retired symbol keeps
# printing. AC-7.85
# --------------------------------------------------------------------------- #

# ★ The real EQR / AVB / VMRK closes, 2026-08-17…24 (measured 2026-08-28).
EQR_CLOSES = {date(2026, 8, 17): 63.66, date(2026, 8, 18): 64.03,
              date(2026, 8, 19): 64.35, date(2026, 8, 20): 65.14,
              date(2026, 8, 21): 66.79, date(2026, 8, 24): 68.14}
AVB_CLOSES = {**EQR_CLOSES, date(2026, 8, 17): 65.90}


def test_ac_7_85_a_retired_symbol_printing_the_successors_prices_is_found():
    """AC-7.85 / DE-68, DE-61 — ⚠⚠ *measured:* `AVB` 2026-08-17 is its own
    (65.90) and 2026-08-18 onward is `EQR`'s. ★ The bars never stopped, so
    staleness cannot catch it: the series changed companies mid-print and
    carries a **fabricated −2.8 % return** on the changeover date."""
    from src.data_engine.symbology.combination import contaminated_from

    assert contaminated_from(AVB_CLOSES, EQR_CLOSES) == date(2026, 8, 18)


def test_ac_7_85_two_distinct_series_are_not_contaminated():
    """AC-7.85 — ★ the check must not fire on names that merely correlate."""
    from src.data_engine.symbology.combination import contaminated_from

    other = {d: c + 1.25 for d, c in EQR_CLOSES.items()}
    assert contaminated_from(other, EQR_CLOSES) is None


def test_ac_7_85_a_single_equal_close_is_a_coincidence_not_a_merger():
    """AC-7.85 / CN-10 — ⚠ two REITs printing the same close **once** is
    unremarkable. `MIN_RUN` is an admitted choice, and it is not one."""
    from src.data_engine.symbology.combination import contaminated_from

    brushed = {d: c + 0.5 for d, c in EQR_CLOSES.items()}
    brushed[date(2026, 8, 24)] = EQR_CLOSES[date(2026, 8, 24)]
    assert contaminated_from(brushed, EQR_CLOSES) is None


def test_ac_7_85_a_combination_yields_two_findings_not_one():
    """AC-7.85 / DE-68 — ★★ **two names left the universe.** The CIK diff sees
    one event; the retired side is invisible to it by construction, because its
    CIK never changed ticker."""
    from src.data_engine.symbology.combination import combination_findings

    survivor, gone = combination_findings(
        retired="AVB", successor="VMRK", survivor_cik="0000906107",
        cause="merger_of_equals", effective=date(2026, 8, 18),
        knowable_at=date(2026, 8, 18), sources=["https://example.invalid/8-k"],
        contaminated=date(2026, 8, 18), retired_company="AvalonBay Communities")

    assert (survivor.ticker, survivor.event_class) == ("VMRK", "ticker_change")
    assert (gone.ticker, gone.event_class) == ("AVB", "delisting")
    # ⚠ The retired side must say the bars became someone else's, not that
    #   they stopped — a consumer reading only event_date would trust them.
    assert gone.detail["contaminated_from"] == "2026-08-18"
    assert gone.detail["successor"] == "VMRK"


def test_ac_7_85_a_cause_without_a_source_is_refused():
    """AC-7.85 / DE-68 — ⚠⚠ the cause is established by **search**, never
    derived. ★ Recording it unsourced makes a guess indistinguishable from a
    corroborated finding, which is the whole error the skill prevents."""
    import pytest

    from src.data_engine.errors import ContractViolationError
    from src.data_engine.symbology.combination import combination_findings

    with pytest.raises(ContractViolationError, match="sources"):
        combination_findings(
            retired="AVB", successor="VMRK", survivor_cik="0000906107",
            cause="merger_of_equals", effective=date(2026, 8, 18),
            knowable_at=date(2026, 8, 18), sources=[])


def test_ac_7_85_a_rebrand_is_not_a_combination():
    """AC-7.85 / DE-68 — ⚠ `BK`→`BNY` retires **no second ticker**. Recording a
    rebrand as a combination would invent a delisting for a name that never
    existed on the other side."""
    import pytest

    from src.data_engine.errors import ContractViolationError
    from src.data_engine.symbology.combination import combination_findings

    with pytest.raises(ContractViolationError, match="retires nothing"):
        combination_findings(
            retired="BK", successor="BNY", survivor_cik="0001390777",
            cause="ticker_change", effective=date(2026, 6, 30),
            knowable_at=date(2026, 6, 30), sources=["https://example.invalid/pr"])


def test_ac_7_85_a_rebrand_is_not_contamination_even_though_it_agrees():
    """AC-7.85 / DE-68 — ⚠⚠ **the trap.** *Measured 2026-08-28:* `BK` and `BNY`
    agree over the **whole** window, because a rebrand really is one series
    through two symbols — and so is a merger survivor. ★ Contamination is a
    series that **diverges then converges**; one that never diverged is the
    same company, and flagging it would fire on every rename."""
    from src.data_engine.symbology.combination import contaminated_from

    same = dict(EQR_CLOSES)                      # BK/BNY and EQR/VMRK shape
    assert contaminated_from(same, EQR_CLOSES) is None


def test_ac_7_85_a_window_that_cannot_answer_says_so_rather_than_none():
    """AC-7.85 / P5 — ⚠ a window starting at or after the changeover makes a
    contaminated symbol and a clean one **identical**. ★ Returning `None` there
    would be a clean answer to a question that was never asked."""
    import pytest

    from src.data_engine.errors import ContractViolationError
    from src.data_engine.symbology.combination import contaminated_from

    late = {d: c for d, c in AVB_CLOSES.items() if d >= date(2026, 8, 18)}
    with pytest.raises(ContractViolationError, match="at or after the changeover"):
        contaminated_from(late, EQR_CLOSES, effective=date(2026, 8, 18))


def test_ac_7_85_the_effective_date_makes_the_question_decidable():
    """AC-7.85 — ★ with the changeover supplied by the search, the two cases
    separate cleanly: `AVB` diverged before it, a rebrand never did."""
    from src.data_engine.symbology.combination import contaminated_from

    when = date(2026, 8, 18)
    assert contaminated_from(AVB_CLOSES, EQR_CLOSES, effective=when) == when
    assert contaminated_from(dict(EQR_CLOSES), EQR_CLOSES, effective=when) is None


def test_ac_7_85_the_retired_side_is_found_without_any_search():
    """AC-7.85 / DE-68 — ★★ **the detector the CIK diff cannot be.** `AVB` never
    appears in the diff (its CIK never changed ticker), so identity data alone
    can never surface it. ⚠ The *prices* can: a retired name printing another's
    series is visible from arithmetic alone."""
    from src.data_engine.symbology.combination import contaminated_by

    found = contaminated_by({"AVB": AVB_CLOSES, "HOLX": {}},
                            {"VMRK": EQR_CLOSES, "BNY": {}})

    assert found == {"AVB": [("VMRK", date(2026, 8, 18))]}


def test_ac_7_85_every_match_travels_never_just_the_first():
    """AC-7.85 — ⚠ a suspect matching two successors is **ambiguous** and must
    be visible as such, the same rule the rename detector follows."""
    from src.data_engine.symbology.combination import contaminated_by

    found = contaminated_by({"AVB": AVB_CLOSES},
                            {"VMRK": EQR_CLOSES, "ZZZZ": EQR_CLOSES})

    assert len(found["AVB"]) == 2, "an ambiguous match is shown, not decided"
