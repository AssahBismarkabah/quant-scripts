"""
Reproduction probe for the Short-term-sector momentum rotation algorithm
(research/Short-term-sector/short-term-sector.py).

Replicates the exact strategy mechanics outside the QuantConnect engine:
- Universe: 11 US sector SPDRs + QQQ
- Signal: trailing 21-trading-day rate of change (ROC)
- Rebalance: first trading day of month, equal-weight top-2, fully invested
- Cash buffer: 3% of portfolio value kept free
- Costs: QC-style per-share fee (~$0.005/sh) + 5 bps slippage per side

Outputs: JSON summary in outputs/short_term_sector_summary.json
"""
import json
import math
import sys
from datetime import date

import numpy as np
import pandas as pd

TICKERS = ["XLK", "XLF", "XLE", "XLV", "XLI",
           "XLB", "XLY", "XLP", "XLU", "XLRE", "QQQ"]
MOM_WINDOW = 21
TOP_K = 2
CASH_BUFFER = 0.03
FEE_PER_SHARE = 0.005
SLIPPAGE_BPS = 5
START = date(2015, 10, 1)
END = date(2026, 8, 15)


def load_prices() -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(TICKERS, start=START, end=END, interval="1d",
                     auto_adjust=True, progress=False, threads=True)
    close = df["Close"]
    close = close.ffill().dropna(how="any")
    return close


def simulate(close: pd.DataFrame) -> dict:
    prices = close  # rows = trading days, cols = tickers
    roc = prices.pct_change(MOM_WINDOW)  # 21-day rate of change
    month_first = prices.index.to_series().groupby(
        [prices.index.year, prices.index.month]).first()

    cash = 1.0  # start at $1, track portfolio value as fraction
    holdings = {}  # ticker -> shares (in $1-portfolio units)
    trades = 0
    fees_paid = 0.0
    values = []
    turnover = 0.0

    for i, (ts, row) in enumerate(prices.iterrows()):
        if ts in month_first.values and not math.isnan(roc.loc[ts].dropna().sum()):
            scores = roc.loc[ts].dropna()
            if len(scores) < len(TICKERS):
                continue
            winners = scores.sort_values(ascending=False).head(TOP_K).index.tolist()

            # --- liquidate all current holdings ---
            for tk, sh in holdings.items():
                px = row[tk]
                cash += sh * px
                fees_paid += abs(sh) * FEE_PER_SHARE
                trades += 1
            # --- buy top-k at equal weight (with 3% cash buffer) ---
            invest = cash * (1.0 - CASH_BUFFER)
            weight = invest / TOP_K
            new_holdings = {}
            for tk in winners:
                px = row[tk]
                slip = px * SLIPPAGE_BPS / 10_000
                shares = weight / (px + slip)
                cost = shares * (px + slip) + shares * FEE_PER_SHARE
                cash -= cost
                new_holdings[tk] = shares
            # track turnover: sum of |delta weight| / 2
            old_w = pd.Series({k: v * prices.loc[ts, k] for k, v in holdings.items()})
            new_w = pd.Series({k: v * prices.loc[ts, k] for k, v in new_holdings.items()})
            turnover += (old_w.abs().sum() + new_w.abs().sum()) / 2.0
            holdings = new_holdings

        # --- mark to market ---
        if holdings:
            mv = sum(sh * prices.loc[ts, tk] for tk, sh in holdings.items())
            values.append((ts, cash + mv))
        else:
            values.append((ts, cash))

    vals = pd.Series(dict(values), name="equity")
    rets = vals.pct_change().dropna()

    n = len(rets)
    cagr = (vals.iloc[-1] / vals.iloc[0]) ** (252.0 / n) - 1
    sharpe = rets.mean() / rets.std() * math.sqrt(252) if rets.std() > 0 else 0
    dd = (vals / vals.cummax() - 1.0).min()

    return {
        "window": str(START), "end": str(END),
        "final_value": round(float(vals.iloc[-1]), 4),
        "cagr_pct": round(cagr * 100, 2),
        "sharpe": round(sharpe, 2),
        "max_drawdown_pct": round(dd * 100, 2),
        "avg_turnover_per_rebalance_pct": round(float(turnover / len(month_first)) * 100, 1),
        "n_rebalances": int(len(month_first)),
        "fees_paid_units": round(fees_paid, 4),
    }


def main() -> None:
    print(f"Fetching daily closes for {TICKERS} ({START} -> {END})...")
    close = load_prices()
    print(f"  {len(close)} trading days, {close.shape[1]} tickers")

    print("Running strategy simulation...")
    strat = simulate(close)

    bench = close["QQQ"]
    bvals = bench / bench.iloc[0]
    brets = bvals.pct_change().dropna()
    print("Benchmarks (buy & hold, no costs):")
    for name, series in [
        ("QQQ", bvals),
        ("Equal-weight basket", close.mean(axis=1) / close.iloc[0].mean()),
    ]:
        r = series.pct_change().dropna()
        cagr = (series.iloc[-1]) ** (252.0 / len(r)) - 1
        dd = (series / series.cummax() - 1).min()
        print(f"  {name:22s} CAGR {cagr*100:6.2f}%  Sharpe {r.mean()/r.std()*math.sqrt(252):5.2f}  MaxDD {dd*100:6.2f}%")
        strat[f"bench_{name.lower().replace(' ', '_')}_cagr_pct"] = round(cagr * 100, 2)
        strat[f"bench_{name.lower().replace(' ', '_')}_sharpe"] = round(r.mean() / r.std() * math.sqrt(252), 2)
        strat[f"bench_{name.lower().replace(' ', '_')}_maxdd_pct"] = round(dd * 100, 2)

    print("\nStrategy (21d ROC, top-2, monthly, 3% buffer, fees+5bps slippage):")
    for k, v in strat.items():
        print(f"  {k}: {v}")

    import os
    out = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "short_term_sector_summary.json"), "w") as f:
        json.dump(strat, f, indent=2)
    print(f"\nSaved -> outputs/short_term_sector_summary.json")


if __name__ == "__main__":
    main()