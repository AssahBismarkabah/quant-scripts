# Short-Term Sector Momentum Rotation

**Version:** 1.0 (probe run, 2026-08-16)
**Status:** DISCONFIRMED (as claimed/validated) — local reproduction of the QC algorithm `research/Short-term-sector/short-term-sector.py` on daily closes (yfinance, auto-adjusted) Oct 2015 → Aug 2026 with fees ($0.005/sh) + 5 bps slippage: **CAGR 12.31%, Sharpe 0.71, MaxDD −34.5%** vs QQQ buy & hold **CAGR 20.39%, Sharpe 0.95** and equal-weight 12-ETF basket **CAGR 15.06%, Sharpe 0.88**. Underperforms both benchmarks on return and Sharpe in every tested window; only "wins" on drawdown vs QQQ in the 2023+ window (−15.8% vs −22.8%), which is risk reduction, not alpha.
**Classification:** Cross-sectional equity momentum rotation (monthly top-2 of 11 sector SPDRs + QQQ)
**Research spec:** none filed (no research-spec markdown exists for this family)
**Source:** QC algorithm added to `research/Short-term-sector/short-term-sector.py` (docstring claims edge "validated Jan 2023 → present and back to Oct 2015")

## 1. Executive Summary

Monthly top-2 sector momentum rotation: score 11 sector SPDRs + QQQ by trailing 21-trading-day rate of change, hold the top 2 equal-weight, fully invested, rebalance on the first trading day of the month (30 min after open), 3% free-cash buffer.

**Verdict: the claimed edge does not reproduce.** Full window Oct 2015 → Aug 2026 and the algorithm's actual window Jan 2023 → Aug 2026 both lag QQQ and an equal-weight basket on CAGR and Sharpe net of fees/slippage. Monthly turnover is extreme (~157% of portfolio per rebalance), so live impact would widen the gap further.

## 2. Reproduction

- Universe/signal/rebalance replicated 1:1 from the QC algorithm (21d ROC via `pct_change(21)`, top-2, first-trading-day-of-month rebalance, equal weight, 3% buffer).
- Data: yfinance daily closes, auto-adjusted (total return), Oct 2015 → Aug 2026 (2,728 trading days).
- Costs: QC-style $0.005/share fee + 5 bps slippage per side.

| Window | Strategy CAGR | Sharpe | MaxDD | QQQ CAGR | QQQ Sharpe | EQW basket CAGR |
|---|---|---|---|---|---|---|
| Oct 2015 → Aug 2026 | 12.31% | 0.71 | −34.5% | **20.39%** | **0.95** | **15.06%** |
| Jan 2023 → Aug 2026 | 21.97% | 1.27 | −15.8% | **33.43%** | **1.52** | 22.42% |

## 3. Structural notes

- QQQ is included as a "sector", so top-2 momentum frequently picks QQQ + XLK — the strategy is partly a disguised QQQ surrogate (explains the drawdown profile vs QQQ without the compounding).
- Average turnover per rebalance ≈ 157% of portfolio value (measured), i.e. the whole book rotates ~1.5x monthly.
- Code check (QC API): no lookahead, indicators warmed up, schedule/holdings calls valid. Docstring claims validation back to Oct 2015 but `set_start_date(2023, 1, 1)` only covers 3.6 years.

## 4. Replication

`research/Short-term-sector/run_probe.py` → `outputs/short_term_sector_summary.json`