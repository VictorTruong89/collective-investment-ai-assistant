"""RC-67 — check the dropped BMO exports without running the pipeline. AC-11.49…11.51.

    python -m src.recording.check            # read-only report
    python -m src.recording.check --record   # ALSO append to the ingest log (RC-68)

★ **Why.** The CSV drop is how D-11 is fed (§0: *"a manual CSV drop, no API"*), and until
2026-10-06 a bad file surfaced only inside a pipeline run. This reports every discovered
account — window, rows, orders, positions, cash per currency — and **names a refusal
instead of stopping at the first**, so one bad file never hides the state of the others.

⚠ **Read-only unless `--record`.** Recording is an explicit act, never a side effect of
looking (RC-68). A refused account is never recorded: a log entry is a statement that the
file was sound. Exit status is 1 when any account refused, else 0.

★ It reuses the ingest path the book uses (`parse_export`, `group_orders`,
`derive_quantities`, `derive_cash`) — a checker with its own parser would check a
different thing from the one the pipeline reads.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

#: RC-68 — beside the statements, git-ignored with them (RC-66, DX-5).
DEFAULT_LOG = ".state/broker/ingest_log.jsonl"


def check_account(root: str, account_id: str, *, log) -> tuple[dict, dict | None]:
    """One account's report, and the log entry it WOULD record (None when refused)."""
    from src.recording.book.from_activity import derive_cash, derive_quantities
    from src.recording.book.load import export_path
    from src.recording.orders.group import group_orders
    from src.recording.reconcile.ingest import file_hash, parse_export
    from src.recording.reconcile.ingest_log import compare, entry_for

    path = export_path(root, account_id)
    report = {"account_id": account_id, "file": str(path), "refusal": None,
              "window": None, "rows": 0, "orders": 0, "positions": {}, "cash": {},
              "log": None}
    try:
        activities = parse_export(path, account_id=account_id)
        orders = group_orders(activities)
        quantities = derive_quantities(activities, orders)
    except Exception as exc:                       # noqa: BLE001 — named, not hidden
        report["refusal"] = f"{type(exc).__name__}: {exc}"
        return report, None

    dates = sorted(a.trade_date.isoformat() for a in activities)
    report.update(window=[dates[0], dates[-1]] if dates else None,
                  rows=len(activities), orders=len(orders),
                  positions={k: round(v, 6) for k, v in sorted(quantities.items())},
                  cash=derive_cash(activities))
    short = {k: v for k, v in quantities.items() if v < -1e-9}
    if short:
        # ★ RC-45 — a negative position is a TRUNCATED WINDOW, not a short.
        report["refusal"] = (f"truncated activity window — negative positions "
                             f"{sorted(short)!r}: their buys are older than this file "
                             f"(RC-45). Download the full history, or supply an opening "
                             f"snapshot (RC-47)")
        return report, None

    entry = entry_for(account_id, file=path.name, file_hash=file_hash(path),
                      activities=activities)
    report["log"] = compare(log.last(account_id), entry)
    return report, entry


def check_exports(*, root: str | None = None, log_path=DEFAULT_LOG,
                  record: bool = False) -> dict:
    """Every discovered account, reported. ⚠ Writes only when `record=True`."""
    from src.recording.book.load import discover_accounts, resolve_export_dir
    from src.recording.reconcile.ingest_log import IngestLog

    root = resolve_export_dir(root)
    log = IngestLog(log_path)
    accounts, refused = [], []
    for account_id, _type in discover_accounts(root):
        report, entry = check_account(root, account_id, log=log)
        accounts.append(report)
        if report["refusal"]:
            refused.append(account_id)
        elif record:
            log.append(entry, report["log"])
    return {"root": root, "accounts": accounts, "refused": refused}


def _print(result: dict, *, recorded: bool) -> None:
    print(f"BMO exports in {result['root']}")
    for acc in result["accounts"]:
        print(f"\n{acc['account_id']}  ({Path(acc['file']).name})")
        if acc["refusal"]:
            print(f"  ⛔ REFUSED — {acc['refusal']}")
            continue
        print(f"  window {acc['window'][0]} → {acc['window'][1]} · {acc['rows']} rows · "
              f"{acc['orders']} orders")
        print("  cash: " + ", ".join(f"{v:,.2f} {k}" for k, v in acc["cash"].items()))
        for instrument, qty in acc["positions"].items():
            print(f"  {instrument:28s} {qty:>12,.4f}")
        log = acc["log"]
        line = f"  log: {log['status']}"
        if log["new_rows"] and log["status"] != "first":
            line += f" · {log['new_rows']} new row(s) after the last recorded window"
        if log["window_starts_later"]:
            line += " · ⚠ the window now starts LATER than before — older history dropped"
        print(line)
        if log["status"] == "restatement":
            print("  ⚠ RESTATEMENT — rows inside the previously recorded window changed:")
            for r in log["removed"]:
                print(f"    − {r}")
            for r in log["added"]:
                print(f"    + {r}")
    tail = ("recorded to the ingest log" if recorded
            else "nothing written (pass --record to append to the ingest log)")
    refused = result["refused"]
    print(f"\n{len(result['accounts'])} account(s) · "
          f"{len(refused)} refused{' (' + ', '.join(refused) + ')' if refused else ''} · {tail}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="src.recording.check",
        description="Check the dropped BMO InvestorLine exports (RC-67); "
                    "optionally record them in the ingest log (RC-68).")
    parser.add_argument("--root", default=None,
                        help="export directory (default: $BMO_STATEMENTS_DIR, then "
                             ".state/broker/bmo_investorline)")
    parser.add_argument("--log", default=DEFAULT_LOG, help="ingest log path")
    parser.add_argument("--record", action="store_true",
                        help="append each sound account to the ingest log (RC-68)")
    args = parser.parse_args(argv)
    from src.recording.errors import RecordingError

    try:
        result = check_exports(root=args.root, log_path=args.log, record=args.record)
    except RecordingError as exc:
        # ★ RC-65 / AC-11.48 — "no accounts found" is said plainly, not as a traceback.
        print(f"⛔ {exc}", file=sys.stderr)
        return 1
    _print(result, recorded=args.record)
    return 1 if result["refused"] else 0


if __name__ == "__main__":
    sys.exit(main())
