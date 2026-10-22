"""CT-7.8 — the point-in-time ticker map, anchored on CIK. **DE-61, DE-65.**

```text
╔══════════════════════════════════════════════════════════════════╗
║  A TICKER IS A LABEL WITH A VALIDITY INTERVAL, NOT AN IDENTITY.  ║
║                                                                  ║
║  `S` was SEARS ROEBUCK, became SPRINT in 2005, and has been      ║
║  SENTINELONE since 2021.  A ticker-keyed join over a long        ║
║  history welds three unrelated companies into one series — and   ║
║  no range check detects it, because every value is plausible.    ║
╚══════════════════════════════════════════════════════════════════╝
```

★ **CIK is the anchor** — permanent per SEC registrant, free, and
`load_cik_map()` already holds one for all 510 names. It is CRSP's **PERMCO**;
⚠ see **QD-17** for the limitation that it is not PERMNO.
"""

from __future__ import annotations

from datetime import date

#: CT-7.8's columns. ⚠ `knowable_at` is the SNAPSHOT date — DE-65's axis — and
#: is deliberately not `valid_from`: we learn about a rename when we next look,
#: not when it happened, and a map that conflates the two is look-ahead.
COLUMNS = ("cik", "ticker", "valid_from", "valid_to", "knowable_at", "source")

SEC_SOURCE = "sec:company_tickers.json"


def as_cik(value) -> str:
    """⚠ Zero-padded to 10. YAML reads `0001045810` as the int `1045810`, and a
    map that has already lost the zeros cannot tell a missing entry from a
    mangled one (the `load_cik_map` scar, one module over)."""
    return str(value).strip().zfill(10)


class SymbolHistory:
    """`.state/symbology/history.parquet` — ★ **append-only** (CT-7.8).

    ⚠ A correction appends a row; it never edits one. Overwriting a mapping
    would make a past decision's universe unreconstructable — and *the
    temptation is highest on the row that says we fetched the wrong symbol.*
    """

    __slots__ = ("root",)

    def __init__(self, root) -> None:
        from pathlib import Path

        self.root = Path(root)

    @property
    def path(self):
        return self.root / "history.parquet"

    def read(self):
        import pandas as pd

        if not self.path.is_file():
            return pd.DataFrame(columns=list(COLUMNS))
        return pd.read_parquet(self.path)

    def append(self, rows) -> int:
        """Add mappings. ⚠ Exact duplicates are dropped, **conflicts are not**:
        two rows disagreeing about the same `(cik, ticker, valid_from)` is a
        real finding and collapsing them silently would hide it."""
        import pandas as pd

        rows = [dict(r) for r in rows]
        if not rows:
            return 0
        frame = pd.concat([self.read(), pd.DataFrame(rows, columns=list(COLUMNS))],
                          ignore_index=True)
        frame = frame.drop_duplicates(subset=list(COLUMNS), keep="first")
        self.root.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(self.path, index=False)
        return len(rows)


def resolve(history, ticker: str, *, as_of: date) -> str | None:
    """★★ **DE-65 — the instrument that held `ticker` THEN, not now.**

    ⚠ With ticker reuse this is not merely a staleness question: asking *"who
    was `S` in 2004?"* with today's map answers **SentinelOne** about a series
    that is **Sears**. Using today's map to answer a historical question is
    look-ahead in the identity layer (INV-1).

    Returns the CIK, or `None` when the ticker was held by nobody we know of at
    `as_of` — ★ **`None`, never a guess at the nearest owner** (P5).
    """
    frame = history.read() if hasattr(history, "read") else history
    if frame is None or not len(frame):
        return None

    name = str(ticker).upper()
    best, best_from = None, None
    for row in frame.to_dict("records"):
        if str(row.get("ticker", "")).upper() != name:
            continue
        # ⚠ DE-65: a mapping we could not have known at as_of does not apply.
        if _as_date(row.get("knowable_at")) and _as_date(row["knowable_at"]) > as_of:
            continue
        start, end = _as_date(row.get("valid_from")), _as_date(row.get("valid_to"))
        if start and start > as_of:
            continue
        if end and end < as_of:
            continue
        if best_from is None or (start and start > best_from):
            best, best_from = as_cik(row["cik"]), start
    return best


def current_symbol(history, cik: str, *, as_of: date | None = None) -> str | None:
    """The symbol this CIK trades under — the open-ended mapping, or the latest."""
    frame = history.read() if hasattr(history, "read") else history
    if frame is None or not len(frame):
        return None

    wanted = as_cik(cik)
    rows = [r for r in frame.to_dict("records") if as_cik(r.get("cik")) == wanted]
    if as_of is not None:
        rows = [r for r in rows
                if not (_as_date(r.get("knowable_at")) and
                        _as_date(r["knowable_at"]) > as_of)]
    if not rows:
        return None
    open_ended = [r for r in rows if not _as_date(r.get("valid_to"))]
    pool = open_ended or rows
    latest = max(pool, key=lambda r: (_as_date(r.get("valid_from")) or date.min))
    return str(latest["ticker"]).upper()


def fetch_symbol_for(history, ticker: str, *, as_of: date) -> str:
    """★★ **DE-63 — the symbol to actually ASK THE VENDOR for.**

    ```text
    MEASURED 2026-08-28 over 2026-01-01…2026-08-27:
        BNY (current)  164 bars  2026-01-02 … 2026-08-27   ★ COMPLETE
        BK  (retired)  122 bars  2026-01-02 … 2026-06-29   ⚠ truncated
    ```

    ★ FMP re-keys history forward onto the current symbol, so the current symbol
    yields **one continuous series** and the retired one a truncated prefix.

    ⚠⚠ **This is why there is no splice function here.** DE-64: the overlapping
    bars agree on OHLC **and disagree on volume** (`BK` 2 790 284 vs `BNY`
    2 790 283; `ECHO` rounded to hundreds). Concatenating the two puts a volume
    step at the changeover into `volume.split_adjusted_zscore.v1` that reads as
    a liquidity event and is an artefact of the join.

    ⚠⚠ **This asks a DIFFERENT question from `resolve`, and conflating them is
    a bug I shipped once.** `resolve("BK", as_of=today)` correctly returns
    `None` — *nobody holds `BK` today*, because the mapping closed on
    2026-06-29. But the caller here is not asking who holds the symbol now; it
    is saying *"our universe still says `BK`, what do I ask the vendor for?"*
    and needs the chain followed **forward**:

    ```text
        "BK"  ──latest owner at-or-before as_of──►  cik 0001390777
              ──that instrument's current symbol──►  "BNY"
    ```

    ★ Falls back to the ticker itself when unknown — a name we hold no mapping
    for is fetched as named, so an empty history is a **no-op**, not a
    behaviour change.

    ★★ **DE-82 — a ticker that still trades is fetched under ITSELF.** SEC lists
    both share classes under one CIK (GOOG/GOOGL, FOX/FOXA, NWS/NWSA), so
    following every ticker to `current_symbol` fetched one class under the other
    — 414 duplicate rows on the first live card (`DX-170`). Only a RETIRED
    mapping is followed forward.
    """
    if resolve(history, ticker, as_of=as_of) is not None:
        return str(ticker).upper()
    cik = _latest_owner(history, ticker, as_of=as_of)
    if cik is None:
        return str(ticker).upper()
    return current_symbol(history, cik, as_of=as_of) or str(ticker).upper()


def _latest_owner(history, ticker: str, *, as_of: date) -> str | None:
    """The CIK that most recently held `ticker` **at or before** `as_of`.

    ⚠ Deliberately ignores `valid_to`, which is what separates it from
    `resolve`: a retired mapping still tells us *which instrument that symbol
    used to be*, and that is the whole point of following a rename forward.

    ★ Reuse is still handled: *most recent holder as of that date* is the right
    answer even when the symbol was later reassigned — the map is read
    point-in-time either way (DE-65).
    """
    frame = history.read() if hasattr(history, "read") else history
    if frame is None or not len(frame):
        return None

    name = str(ticker).upper()
    best, best_from = None, None
    for row in frame.to_dict("records"):
        if str(row.get("ticker", "")).upper() != name:
            continue
        knowable = _as_date(row.get("knowable_at"))
        if knowable and knowable > as_of:
            continue                       # ⚠ DE-65 — not knowable yet
        start = _as_date(row.get("valid_from"))
        if start and start > as_of:
            continue
        if best_from is None or (start or date.min) >= best_from:
            best, best_from = as_cik(row["cik"]), (start or date.min)
    return best


def _as_date(value):
    import pandas as pd

    if value is None or value == "" or (isinstance(value, float) and value != value):
        return None
    return pd.Timestamp(value).date()
