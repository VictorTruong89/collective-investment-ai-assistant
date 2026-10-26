"""D-11 error hierarchy (L1-recording §13).

Every error raises. The two below carry the rules most likely to be eroded
under pressure, and each names its rule so a reader does not have to guess
which one fired.
"""

from __future__ import annotations

from src.shared.errors import PipelineError


class RecordingError(PipelineError):
    """Base for D-11. Code: REC.*"""


class AppendOnlyViolation(RecordingError):
    """INV-006 — an attempt to revise a record that is written once.

    ★ Two records in this system are append-only for the same reason and are
    tempting to edit for different ones:

      the JOURNAL (RC-24) — a rationale edited after the outcome is known is
          worthless as evidence, and the temptation arrives exactly when the
          outcome is known.

      the COUNTERFACTUAL (DN-21, BS-7) — "a rejected-name history that can be
          edited is the most tempting record in the system to edit", because
          nothing external reconciles it.
    """

    def __init__(self, what: str, key: object) -> None:
        super().__init__(
            f"{what} {key!r} is append-only and may not be revised (INV-006). "
            f"A record that can be edited after the outcome is known is not evidence "
            f"— append a correcting entry instead, so both are visible"
        )


class OutcomeBasisMismatch(RecordingError):
    """DN-20 / RC-32 — two arms marked on different horizons or anchors.

    ⚠ The failure this prevents is quiet: a vetoed name marked at 1w against an
    acted-on name at 1m produces a difference that is mostly horizon, and it
    reads as gate skill.
    """


class BookBreakError(RecordingError):
    """RC-10 / INV-025 — `sum(positions) + cash != NAV`.

    ⚠ **A break raises; it is never absorbed.** ★ D-05 **RK-29** then refuses to
    compute on it rather than falling back to the last good book — *the fallback
    produces a correct-looking report about YESTERDAY, and nothing on the
    artifact would say so.*
    """

    code = "REC.BOOK.BREAK"

    def __init__(self, account_id: str, as_of, breaks=()) -> None:
        detail = "; ".join(str(b) for b in breaks) or "unspecified"
        super().__init__(f"{account_id} on {as_of}: {detail} (RC-10, INV-025)")


class CapitalBaseUnavailableError(RecordingError):
    """RC-19 — the base is read from the book, and this book has none.

    ⚠ **Never configured, never hard-coded** (QA-107, BS-9). A percentage
    computed against a literal is a figure about a fund that does not exist.
    """

    code = "REC.CAPITAL.UNAVAILABLE"

    def __init__(self, account_id: str, as_of) -> None:
        super().__init__(
            f"{account_id} on {as_of}: no capital base — `nav_base` is null, so "
            f"no FX rate was available and the aggregate is unavailable rather "
            f"than estimated (RC-19, FX-3)"
        )


class UnclassifiableActivityError(RecordingError):
    """RC-13 / H-8 — ★ **an unclassifiable activity raises.**

    ⚠ *No neutral default, no silent drop.* A new BMO activity type that nobody
    has classified would otherwise vanish from a book that is required to
    balance (RC-10), and the break would surface later as a reconciliation
    failure with no cause attached.
    """

    code = "REC.ACTIVITY.UNCLASSIFIABLE"

    def __init__(self, where: str, detail: str) -> None:
        super().__init__(f"{where}: {detail} (RC-13, P5)")


class CommissionImplausibleError(RecordingError):
    """RC-15 — the derived commission is not a plausible fee.

    ★ *Commission is DERIVED, not assumed* — `Total Amount − (−Q×P)` per ORDER.
    ⚠ **A hard-coded fee constant is a modelling assumption wearing the word
    "reality"**, and a derived value far from BMO's flat rate usually means the
    tranches were not grouped (RC-14), not that the fee changed.
    """

    code = "REC.COMMISSION.IMPLAUSIBLE"

    def __init__(self, order_key: str, derived: float, detail: str = "") -> None:
        super().__init__(
            f"{order_key}: derived commission {derived:.2f} is implausible. "
            f"{detail} ★ The usual cause is ungrouped tranches — per tranche "
            f"the residual is meaningless; per order it is the flat fee "
            f"(RC-14, RC-15, H-1, H-7)")


class TruncatedWindowError(RecordingError):
    """RC-45 — a derived position went negative, so the export starts too late.

    ★ **Not a short.** The mandate holds no short positions, so a negative
    derived quantity means the lot was opened before the export's `From` date:
    its sells are in the file and its buys are not.

    ⚠ The dangerous property is that **the cash still balances** — RC-10 would
    pass — so nothing else in the system would notice.
    """

    code = "REC.WINDOW.TRUNCATED"

    def __init__(self, negatives: dict) -> None:
        detail = "; ".join(f"{acct} {inst} = {qty:g}"
                           for (acct, inst), qty in sorted(negatives.items()))
        super().__init__(
            f"derived quantities went negative: {detail}. Re-export with a "
            f"`From` date before the earliest open lot — a truncated window "
            f"derives the wrong position while the arithmetic looks healthy "
            f"(RC-45, RC-9)")


class ForeignAccountRowError(RecordingError):
    """RC-48 — the export contains a row belonging to a different account.

    ⚠ **Measured 2026-08-25:** `TransactionHistory_TFSA_2.csv` carries one
    `Joint` row (account `<Joint account no., redacted>`) among 146 TFSA rows (`<TFSA_2 account no., redacted>`).
    ★ Booking it into the TFSA attributes another account's cash to this one —
    **$0.50 here, and the principle is RC-1's**: there is no unattributed
    activity, and there is no *mis*-attributed activity either.
    """

    code = "REC.ACCOUNT.FOREIGN_ROW"

    def __init__(self, file_name: str, declared: str, rows) -> None:
        detail = "; ".join(f"line {n}: {num} ({typ})" for n, num, typ in rows)
        super().__init__(
            f"{file_name} is about account {declared!r} but contains "
            f"{len(rows)} row(s) from another: {detail}. Split the export by "
            f"account, or pass `strict_accounts=False` to skip them "
            f"deliberately (RC-48, RC-1)")


class HoldingsSelfCheckError(RecordingError):
    """RC-73 — the holdings export disagrees with its own totals.

    ★ *The export checks itself before anything reads it, and each check names what
    failed.* Every failing check is listed, not just the first, so one bad figure does
    not hide another.
    """

    code = "REC.HOLDINGS.SELF_CHECK"

    def __init__(self, file_name: str, failures) -> None:
        self.failures = tuple(failures)
        super().__init__(
            f"{file_name}: the holdings export fails its own totals — "
            + "; ".join(self.failures) + " (RC-73)")


class HoldingsUnrecognisedError(RecordingError):
    """RC-70/RC-71/RC-72/RC-74 — a line, layout, currency or date this parser does not know.

    ⚠ Raised rather than skipped (RC-13's shape): an unread line is a market value
    missing from a balance that must add up.
    """

    code = "REC.HOLDINGS.UNRECOGNISED"

    def __init__(self, where: str, detail: str) -> None:
        super().__init__(f"{where}: {detail}")


class HoldingsMissingError(RecordingError):
    """RC-77 — ★ **no holdings export ⇒ refused by name, never valued from a fallback.**

    ⚠ Not a derived book, not an older export, not vendor prices (P5). A book-wide
    request with any account missing is refused the same way: two valued accounts are
    not *the book* (RC-3, RK-5).
    """

    code = "REC.HOLDINGS.MISSING"

    def __init__(self, accounts, root) -> None:
        self.accounts = tuple(accounts)
        names = ", ".join(self.accounts)
        super().__init__(
            f"no holdings export for {names} (expected "
            + ", ".join(f"Holdings_{a}.csv" for a in self.accounts)
            + f" in {root}) — the account is unvalued, never valued from a "
            f"derived or older figure (RC-77, P5)")
