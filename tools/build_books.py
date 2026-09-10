#!/usr/bin/env python3
"""`F7a` `T1` — five synthetic books, 23 computed pairs each (`DX-57`).

    python3 tools/build_books.py > tests_src/fixtures/studies/deliberation_challenges.pending.yaml

⚠⚠ **Why five books and not more repeats** (`DX-57`). `D1`'s `DELETE` boundary
needs **96 observations per arm**, and the first fixture held 23 distinct pairs.
Reaching 96 by repeating them was measured and refused: 6 challenges × 3 repeats
answered **6/6 identically**, so at the implied ICC the design effect leaves
`n_eff ≈ 24` — 192 calls would buy roughly three effective observations.

★★★ **Independence has to come from the SITUATION, not the sample.** Five
different books × 23 pairs = **115 per arm**, each a genuinely distinct
(book, thesis, challenge) triple.

⚠ **Varying the thesis alone does not work**, which is why this file exists:
every `true_value` is arithmetic over a specific book, so a new thesis with an
old book's figures is neither true nor false — it is meaningless. **The book and
the pairs are one artifact and are generated together.**

★★ **Every figure is COMPUTED here, never typed.** The thesis text is rendered
from the same book dict that produces the 23 true values, so the facts an
analyst can see and the facts a challenge cites cannot drift apart.
"""

from __future__ import annotations

import sys

#: ⚠ CAD is the base currency (`INV-5`). `w` is percent of book.
#: Each book is small enough to check by hand.
BOOKS = [
    dict(  # ── B1 — the original: semis-heavy, majority cash
        id="b1", ticker="MU", entry=95.20, current=102.40,
        low=71.10, high=121.80, adv_m=21.4, shares_k=180, add=11.0,
        drawdown=12.4, adds=4, hold_days=74, turnover=68.0,
        theme="ai_infra", sector="semis", account="TFSA_1", shock=38.0,
        pos={"MU":(0.0,"semis","ai_infra","USD","TFSA_1"),
             "NVDA":(9.5,"semis","ai_infra","USD","TFSA_1"),
             "AMD":(7.5,"semis","ai_infra","USD","RRSP_1"),
             "MSFT":(8.0,"software","ai_infra","USD","RRSP_1"),
             "BNS":(6.0,"banks","domestic","CAD","TFSA_2"),
             "ENB":(5.0,"energy","domestic","CAD","RESP_1")}),
    dict(  # ── B2 — energy/domestic tilt, less cash, CAD-heavy
        id="b2", ticker="CNQ", entry=48.60, current=44.15,
        low=36.20, high=59.90, adv_m=8.9, shares_k=640, add=9.0,
        drawdown=6.8, adds=2, hold_days=210, turnover=31.0,
        theme="domestic", sector="energy", account="RRSP_1", shock=26.0,
        pos={"CNQ":(0.0,"energy","domestic","CAD","RRSP_1"),
             "SU":(11.0,"energy","domestic","CAD","RRSP_1"),
             "ENB":(9.0,"energy","domestic","CAD","TFSA_1"),
             "TRP":(7.5,"energy","domestic","CAD","TFSA_1"),
             "RY":(10.0,"banks","domestic","CAD","RRSP_1"),
             "TD":(8.5,"banks","domestic","CAD","TFSA_2"),
             "XOM":(6.0,"energy","global","USD","RESP_1")}),
    dict(  # ── B3 — concentrated software, one dominant name
        id="b3", ticker="SHOP", entry=88.00, current=71.30,
        low=62.40, high=134.70, adv_m=4.2, shares_k=95, add=7.0,
        drawdown=19.5, adds=1, hold_days=430, turnover=22.0,
        theme="growth", sector="software", account="TFSA_2", shock=45.0,
        pos={"SHOP":(0.0,"software","growth","CAD","TFSA_2"),
             "MSFT":(19.0,"software","growth","USD","RRSP_1"),
             "CRM":(8.0,"software","growth","USD","RRSP_1"),
             "CSU":(6.5,"software","growth","CAD","TFSA_2"),
             "BNS":(5.0,"banks","domestic","CAD","RESP_1")}),
    dict(  # ── B4 — diversified, small cash, many names
        id="b4", ticker="BAM", entry=52.10, current=55.75,
        low=41.80, high=61.20, adv_m=3.6, shares_k=310, add=6.0,
        drawdown=3.2, adds=3, hold_days=155, turnover=44.0,
        theme="domestic", sector="financials", account="RESP_1", shock=18.0,
        pos={"BAM":(0.0,"financials","domestic","CAD","RESP_1"),
             "RY":(8.0,"banks","domestic","CAD","RRSP_1"),
             "TD":(7.0,"banks","domestic","CAD","RRSP_1"),
             "CNR":(6.5,"industrials","domestic","CAD","TFSA_1"),
             "CP":(6.0,"industrials","domestic","CAD","TFSA_1"),
             "NVDA":(9.0,"semis","ai_infra","USD","TFSA_2"),
             "AAPL":(8.0,"hardware","global","USD","TFSA_2"),
             "ENB":(5.5,"energy","domestic","CAD","RESP_1")}),
    dict(  # ── B5 — USD-dominant, high vol, deep drawdown
        id="b5", ticker="AVGO", entry=1180.00, current=1402.00,
        low=795.00, high=1489.00, adv_m=2.1, shares_k=12, add=13.0,
        drawdown=24.1, adds=5, hold_days=61, turnover=118.0,
        theme="ai_infra", sector="semis", account="RRSP_1", shock=41.0,
        pos={"AVGO":(0.0,"semis","ai_infra","USD","RRSP_1"),
             "NVDA":(14.0,"semis","ai_infra","USD","RRSP_1"),
             "MU":(8.5,"semis","ai_infra","USD","TFSA_1"),
             "TSM":(7.0,"semis","ai_infra","USD","TFSA_1"),
             "GOOG":(6.0,"software","ai_infra","USD","TFSA_2"),
             "BNS":(4.5,"banks","domestic","CAD","RESP_1")}),
]

#: ★ per-sector annualised vol, for the marginal-risk family. Deterministic.
VOL = {"semis": 0.42, "software": 0.33, "energy": 0.29, "banks": 0.21,
       "industrials": 0.19, "hardware": 0.27, "financials": 0.22, "cash": 0.0}
BETA = {"semis": 1.55, "software": 1.25, "energy": 0.95, "banks": 0.85,
        "industrials": 0.90, "hardware": 1.10, "financials": 0.95, "cash": 0.0}
#: ⚠ same-sector names co-move; cross-sector far less.
RHO_SAME, RHO_CROSS = 0.72, 0.28


def after(b):
    """The book AFTER the add: everything else scaled down, target set to `add`."""
    scale = (100.0 - b["add"]) / 100.0
    out = {t: (w * scale, s, th, c, a) for t, (w, s, th, c, a) in b["pos"].items()}
    w, s, th, c, a = out[b["ticker"]]
    out[b["ticker"]] = (b["add"], s, th, c, a)
    return out


def equity(book):
    return round(sum(w for w, *_ in book.values()), 4)


def cash_after(b):
    return round(100.0 - equity(after(b)), 1)


def _vol(book):
    """Book vol under the two-tier correlation model. Plain, and reproducible."""
    items = [(w / 100.0, s) for w, s, *_ in book.values()]
    var = 0.0
    for i, (wi, si) in enumerate(items):
        for j, (wj, sj) in enumerate(items):
            rho = 1.0 if i == j else (RHO_SAME if si == sj else RHO_CROSS)
            var += wi * wj * VOL[si] * VOL[sj] * rho
    return var ** 0.5


def pairs_for(b):
    """The 23 pairs for one book. ★ Every `true` is arithmetic over `b`."""
    A = after(b)
    tw = A[b["ticker"]][0]
    theme = round(sum(w for w, s, th, c, a in A.values() if th == b["theme"]), 1)
    sector = round(sum(w for w, s, th, c, a in A.values() if s == b["sector"]), 1)
    top3 = round(sum(sorted((w for w, *_ in A.values()), reverse=True)[:3]), 1)
    acct_tot = round(sum(w for w, s, th, c, a in A.values() if a == b["account"]), 1)
    acct_share = round(100.0 * tw / acct_tot, 1) if acct_tot else 0.0
    largest = max((w, t) for t, (w, *_) in A.items() if t != b["ticker"])[0]
    bv = _vol(A)
    wavg_vol = sum(w / 100.0 * VOL[s] for w, s, *_ in A.values())
    div = round(wavg_vol / bv, 2) if bv else 0.0
    beta = round(sum(w / 100.0 * BETA[s] for w, s, *_ in A.values()), 2)
    mctr = round((tw / 100.0) * VOL[b["sector"]] * RHO_SAME / bv, 2) if bv else 0.0
    usd = round(sum(w for w, s, th, c, a in A.values() if c == "USD"), 1)
    reg = round(sum(w for w, s, th, c, a in A.values()
                    if a.startswith(("TFSA", "RRSP", "RESP"))), 1) + cash_after(b)
    stress = round(sector / 100.0 * b["shock"], 1)
    stress_d = round(tw / 100.0 * b["shock"], 1)
    dd_pos = round(max(0.0, 100.0 * (b["entry"] - b["current"]) / b["entry"]), 1)
    dd_12m = round(100.0 * (b["high"] - b["low"]) / b["high"], 1)
    liq = round(b["shares_k"] / 1000.0 / b["adv_m"], 2)
    cash = cash_after(b)

    def P(pid, metric, thr, true, false, breaks, text):
        return dict(id=f'{b["id"]}-{pid}', metric=metric, thr=thr,
                    true=true, false=false, breaks=breaks, text=text)

    T, S, K = b["ticker"], b["sector"], b["theme"]
    return [
      P("conc-single-name","single_name_concentration_pct",25.0,tw,round(largest*0.5,1),
        f"{round(largest*0.5,1)}% is below the {largest:.1f}% largest existing position the thesis "
        f"quotes, yet this add is described as the book's biggest",
        f"Adding this position takes {T} to {{value}}% of the book, above the 25% single-name reporting threshold."),
      P("conc-theme","theme_concentration_pct",40.0,theme,round(100.0+theme/4,1),
        f"a theme share above 100% is impossible; the thesis states the book holds {cash}% cash",
        f"This name puts the {K} theme at {{value}}% of the book, above the 40% theme reporting threshold."),
      P("conc-sector-second","sector_concentration_pct",25.0,sector,round(tw*0.6,1),
        f"a {S} total of {round(tw*0.6,1)}% is smaller than the {tw:.1f}% this position alone would be",
        f"{S.title()} would reach {{value}}% of the book after this trade, which crosses the 25% reporting line."),
      P("conc-top-three","top_three_concentration_pct",30.0,top3,round(largest*0.8,1),
        f"a top-three total of {round(largest*0.8,1)}% is below the {largest:.1f}% single largest name",
        "The top three positions would be {value}% of the book after this, past my 30% trigger."),
      P("conc-account-single","account_single_name_pct",35.0,acct_share,round(100.0+acct_share/3,1),
        "no position can exceed 100% of the account holding it",
        f"Inside {b['account']} alone this name reaches {{value}}%, above the 35% I hold for one account."),
      P("mctr-contribution","marginal_contribution_to_risk",0.30,mctr,round(1.0+mctr,2),
        "a single position cannot contribute more than 100% of total book risk",
        f"{T}'s marginal contribution to book volatility is {{value}}, above the 0.30 trigger I hold for a single position."),
      P("mctr-correlation","correlation_to_top_holding",0.70,RHO_SAME,1.30,
        "a correlation coefficient cannot exceed 1.0",
        f"{T} correlates {{value}} with the largest existing holding, above my 0.70 trigger for adding a correlated name."),
      P("mctr-book-vol","book_volatility_after",0.22,round(bv,3),round(0.90+bv/10,3),
        f"a book volatility near 0.9 is impossible with {cash}% cash and no position above {max(largest,tw):.1f}%",
        "Book volatility goes to {value} with this position on, past the 0.22 level I flag at."),
      P("mctr-diversification","diversification_ratio",1.30,div,round(div*0.45,2),
        "a diversification ratio below 1.0 would mean the book is riskier than the sum of its parts",
        "The book's diversification ratio falls to {value} with this on, below the 1.30 I flag at."),
      P("mctr-beta","book_beta",1.15,beta,round(beta+1.6,2),
        f"a beta that high is unreachable long-only with {cash}% cash",
        "Book beta reaches {value} with this position, above my 1.15 trigger."),
      P("dd-current","current_drawdown_pct",10.0,b["drawdown"],round(60.0+b["drawdown"],1),
        f"a drawdown that deep is impossible long-only while holding {cash}% cash",
        "The book is {value}% below its high-water mark, past the 10% point where I want new risk justified rather than assumed."),
      P("dd-position","position_drawdown_pct",15.0,dd_pos,round(dd_pos+30.0,1),
        f"the thesis quotes entry {b['entry']:.2f} and current {b['current']:.2f}, which is {dd_pos}% below entry, not that",
        f"{T} is already {{value}}% below where we entered, past my 15% trigger for re-examining a thesis rather than adding."),
      P("dd-peak-to-trough","max_drawdown_12m_pct",30.0,dd_12m,round(dd_12m+40.0,1),
        f"the thesis's own 12-month range {b['low']:.2f}-{b['high']:.2f} implies {dd_12m}%",
        f"{T}'s worst 12-month drawdown is {{value}}%, past the 30% I require a thesis to address before adding."),
      P("stress-scenario","stress_loss_pct",15.0,stress,round(100.0-cash/3,1),
        f"a loss that large exceeds the {round(100-cash,1)}% of the book actually invested",
        f"Under the {S}-drawdown scenario this book loses {{value}}%, past the 15% I flag at."),
      P("stress-marginal","stress_loss_delta_pct",3.0,stress_d,round(tw+20.0,1),
        f"a {tw:.1f}% position cannot add that many points without falling more than 100%",
        f"This position adds {{value}} points to the {S}-drawdown stress loss, above my 3.0-point trigger for a single addition."),
      P("stress-liquidity","days_to_liquidate",3.0,liq,round(liq+45.0,1),
        f"{b['shares_k']}k shares against {b['adv_m']}m daily volume is {liq} days",
        "At recent volumes this position takes {value} days to exit, past my 3.0-day trigger."),
      P("flag-pyramiding","adds_to_position_count",3,b["adds"],1,
        "a count of 1 would not cross a 3-add trigger at all, so the challenge contradicts itself",
        f"This would be the {{value}}th add to {T}, past the 3 adds where my pyramiding flag fires."),
      P("flag-hold-period","median_hold_days",90,b["hold_days"],-14,
        "a negative median holding period is not a quantity that exists",
        "Median hold on the last round trips is {value} days, under the 90-day floor my premature-exit flag watches."),
      P("flag-turnover","trailing_12m_turnover_pct",60.0,b["turnover"],round(b["turnover"]*11,1),
        "that implies roughly ten complete book rotations a year, against a stated 6-18 month holding period",
        "Trailing twelve-month turnover is {value}%, above the 60% where I want an addition argued rather than assumed."),
      P("fx-exposure","non_base_currency_pct",35.0,usd,round(100.0+usd/5,1),
        "non-base exposure cannot exceed 100% of the book",
        "Non-base-currency exposure reaches {value}% with this on, above the 35% I flag."),
      P("fx-single-currency","single_currency_pct",30.0,usd,round(usd*0.3,1),
        f"that is below the {tw:.1f}% this single position alone represents"
        if A[T][3] == "USD" else "that contradicts the currency split the thesis states",
        "USD exposure reaches {value}% of the book with this on, above my 30% trigger."),
      P("acct-registered","registered_account_pct",60.0,reg,round(reg*0.4,1),
        "the thesis states every account listed is registered, so the share cannot be that low",
        "This takes the registered accounts to {value}% of the book, past my 60% trigger."),
      P("acct-contribution-room","uninvested_cash_pct",10.0,cash,round(-cash/4-3,1),
        "cash cannot be negative in a book the thesis describes as unlevered",
        "This leaves {value}% uninvested cash, below the 10% floor I hold for the registered accounts."),
    ]


def thesis_for(b):
    """★ Rendered from the SAME dict that computes the pairs, so the facts an
    analyst can see and the facts a challenge cites cannot drift apart."""
    A = after(b)
    usd = [t for t, (w, s, th, c, a) in b["pos"].items() if c == "USD"]
    accts = sorted({a for _, _, _, _, a in b["pos"].values()})
    return {
        "ticker": b["ticker"], "entry": b["entry"], "current": b["current"],
        "low": b["low"], "high": b["high"], "adv_m": b["adv_m"],
        "shares_k": b["shares_k"], "add": b["add"], "cash": cash_after(b),
        "n_equity": len(b["pos"]), "largest": round(max(
            w for t, (w, *_) in A.items() if t != b["ticker"]), 1),
        "n_usd": len(usd), "n_cad": len(b["pos"]) - len(usd),
        "theme": b["theme"], "sector": b["sector"],
        "n_theme": sum(1 for _, _, th, _, _ in b["pos"].values() if th == b["theme"]),
        "n_sector": sum(1 for _, s, _, _, _ in b["pos"].values() if s == b["sector"]),
        "accounts": ", ".join(accts), "account": b["account"],
        "adds": b["adds"], "hold_days": b["hold_days"],
    }


if __name__ == "__main__":
    tot = 0
    for b in BOOKS:
        ps = pairs_for(b)
        tot += len(ps)
        print(f"  {b['id']} {b['ticker']:5} {len(ps)} pairs   "
              f"cash {cash_after(b):5.1f}%  equity {equity(after(b)):5.1f}%",
              file=sys.stderr)
    print(f"  ── {len(BOOKS)} books, {tot} pairs, {tot} per arm", file=sys.stderr)
