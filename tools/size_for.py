#!/usr/bin/env python3
"""F14 — size one trade in one account against BMO's reported balance.

    python tools/size_for.py DELL --account TFSA_2 --entry 450 --stop 410 --currency USD --dry-run
    python tools/size_for.py DELL --account TFSA_2 --entry 450 --stop 410 --currency USD
    python tools/size_for.py ENB  --account RESP_1 --entry 67.5 --currency CAD --sigma 0.012
    python tools/size_for.py BMO  --account TFSA_2 --entry 240 --stop 225 \\
        --held-stop ARM=180 --held-stop BMO=220 …        # every holding → committed risk measured

★ Capital, cash and the USD→CAD rate are READ from `Holdings_<ACCOUNT>.csv` (D-11 §8a,
RC-70…RC-77) and printed with its as-of date. An account with no holdings export is refused
by name. r_total, r_ceiling and target_positions are read from config/portfolio_policy.yaml
— Victor's numbers, no defaults (PS-43); an account not listed there is refused.

σ (only needed for a volatility stop, or to show a stated stop's implied k): for a USD
listing, realised over 21 sessions from FMP (standing-approved); a CAD listing or a CDR is
never fetched by its bare ticker (RC-53) — give `--sigma` or it is unavailable (F14 D8, D11).

$0 API: no LLM anywhere in D-06 (AC-F14.13). Writes nothing (AC-F14.14). `--dry-run` makes
no network call at all.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, timedelta

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.portfolio.errors import PortfolioError  # noqa: E402
from src.portfolio.on_demand.size_for import (  # noqa: E402
    POLICY_PATH, SIGMA_WINDOW, Sigma, load_policy, realised_sigma, size_on_demand,
)
from src.recording.book.holdings import discover_holdings, load_holdings  # noqa: E402
from src.recording.book.load import discover_accounts, resolve_export_dir  # noqa: E402
from src.recording.errors import RecordingError  # noqa: E402


def resolve_sigma(ticker: str, *, currency: str, stated, as_of: date, fetch_closes) -> Sigma:
    """F14 D8/D11 — stated, else realised for a USD listing, else unavailable (RC-53)."""
    if stated is not None:
        return Sigma(float(stated), "stated")
    if currency != "USD":
        return Sigma(None, "unavailable: a CAD listing or CDR is never fetched by its bare "
                           "ticker (RC-53, F14 D8/D11) — give --sigma")
    closes = fetch_closes(ticker, as_of - timedelta(days=60), as_of)
    if closes is None:
        return Sigma(None, "unavailable: FMP gave no usable closes")
    return realised_sigma(closes, source="FMP")


def fmp_closes(ticker: str, start: date, end: date):
    """Raw daily closes from FMP; ⚠ a split inside the window makes them unusable."""
    from src.data_engine.src.fmp.prices import raw_prices, splits
    from tools.fetch_consensus import _client

    client = _client()
    frame = raw_prices(client, ticker, start, end)
    for event in splits(client, ticker):
        if start <= event.event_date <= end:            # split: the effective date
            return None
    return [(ts.date(), minor / 100.0) for ts, minor in zip(frame["date"], frame["close_minor"])]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("--account", required=True)
    ap.add_argument("--entry", type=float, required=True)
    ap.add_argument("--stop", type=float)
    ap.add_argument("--currency", choices=("CAD", "USD"),
                    help="the entry's currency; required unless the account holds the ticker")
    ap.add_argument("--held-stop", action="append", default=[], metavar="SYM=PRICE")
    ap.add_argument("--sigma", type=float, help="stated daily σ (labelled `stated`)")
    ap.add_argument("--policy", default=str(REPO / POLICY_PATH))
    ap.add_argument("--root", help="the broker export directory (default: RC-66's)")
    ap.add_argument("--dry-run", action="store_true", help="no network; inputs only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = resolve_export_dir(args.root)
    ticker = args.ticker.upper()
    try:
        statement = load_holdings(args.account, root=root)
    except RecordingError as exc:
        print(f"✗ REFUSED — {exc}", file=sys.stderr)
        return 1

    held = {line.analysis_symbol: line for line in statement.lines}
    currency = args.currency or (held[ticker].price_currency if ticker in held else None)
    if currency is None:
        print(f"✗ REFUSED — {ticker} is not held in {args.account}; state --currency CAD|USD "
              f"(no default: it decides the FX and whether σ can be fetched)", file=sys.stderr)
        return 1
    try:
        held_stops = {k.upper(): float(v) for k, v in (s.split("=", 1) for s in args.held_stop)}
    except ValueError:
        print("✗ REFUSED — --held-stop takes SYM=PRICE", file=sys.stderr)
        return 1
    try:
        discovered = tuple(a for a, _t in discover_accounts(root))
    except RecordingError:
        discovered = ()
    discovered = tuple(sorted(set(discovered) | set(discover_holdings(root))))

    print(f"F14 size_for · {ticker} in {args.account} · transport: none (no LLM in D-06) · "
          f"holdings {statement.source_file} as of {statement.as_of}", file=sys.stderr)

    if args.dry_run:
        return _dry_run(args, ticker, currency, statement, held_stops, discovered)

    try:
        policy = load_policy(args.account, args.policy)
        sigma = resolve_sigma(ticker, currency=currency, stated=args.sigma,
                              as_of=statement.as_of, fetch_closes=fmp_closes)
        answer = size_on_demand(
            ticker=ticker, account_id=args.account, entry=args.entry, currency=currency,
            stop=args.stop, statement=statement, policy=policy, sigma=sigma,
            held_stops=held_stops, discovered_accounts=discovered,
            accounts_with_holdings=discover_holdings(root))
    except PortfolioError as exc:
        print(f"✗ REFUSED — {exc}", file=sys.stderr)
        return 1
    print(json.dumps(answer.to_json_obj(), indent=2) if args.json else answer.render())
    return 0


def _dry_run(args, ticker, currency, statement, held_stops, discovered) -> int:
    """AC-F14.17 — what would be read, and what would refuse. No network."""
    ok = True
    out = [f"DRY RUN — {ticker} in {args.account}, nothing fetched, nothing written",
           f"  ✓ capital   {statement.balance:,.2f} CAD  (holdings export as of {statement.as_of})",
           f"  ✓ cash      {statement.cash_total:,.2f} CAD"]
    if currency == "USD":
        if statement.usd_cad is None:
            ok = False
            out.append("  ✗ USD→CAD  no rate in the holdings export — a USD sizing is "
                       "unavailable (FX-3)")
        else:
            out.append(f"  ✓ USD→CAD  {statement.usd_cad}  (holdings export footer)")
    try:
        policy = load_policy(args.account, args.policy)
        out.append(f"  ✓ policy    r_total {policy.r_total} · r_ceiling {policy.r_ceiling} · "
                   f"target_positions {policy.target_positions}  ({policy.source})")
    except PortfolioError as exc:
        ok = False
        out.append(f"  ✗ policy    {exc}")
    if args.sigma is not None:
        out.append(f"  ✓ σ         {args.sigma}  (stated)")
        sigma_ok = True
    elif currency == "USD":
        out.append(f"  ⓘ σ         would be fetched: FMP raw closes, {SIGMA_WINDOW} sessions to "
                   f"{statement.as_of} (standing-approved)")
        sigma_ok = True
    else:
        out.append("  ⓘ σ         unavailable — a CAD listing or CDR is never fetched by its bare "
                   "ticker (RC-53); give --sigma")
        sigma_ok = False
    if args.stop is None and not sigma_ok:
        ok = False
        out.append("  ✗ stop      none stated and no σ for a volatility stop (PS-5)")
    elif args.stop is not None and args.stop >= args.entry:
        ok = False
        out.append(f"  ✗ stop      {args.stop} is at or above entry {args.entry}")
    else:
        out.append(f"  ✓ stop      {args.stop if args.stop is not None else 'volatility stop, k = 1.5 (default, QS-2 open)'}")
    held = sorted(line.analysis_symbol for line in statement.lines)
    missing = [s for s in held if s not in held_stops]
    unknown = sorted(set(held_stops) - set(held))
    if unknown:
        ok = False
        out.append(f"  ✗ held stop {', '.join(unknown)} not held in {args.account}")
    out.append(f"  ⓘ committed {'measured' if not missing else 'UNMEASURED — no held stop for ' + ', '.join(missing) + '; only r_ceiling binds'}")
    lacking = sorted(set(discovered) - set(discover_holdings(resolve_export_dir(args.root))))
    if lacking:
        out.append(f"  ⓘ book-wide UNCHECKED — no holdings export for {', '.join(lacking)} (RC-77)")
    out.append("  → would size" if ok else "  → would REFUSE")
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
