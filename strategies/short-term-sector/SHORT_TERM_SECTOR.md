# Short-Term Sector Momentum Rotation

**Version:** 2.0 (corrected probe, 2026-08-16)
**Status:** DISCONFIRMED — 1:1 reproduction of the QC algorithm `research/Short-term-sector/short-term-sector.py` (raw prices, point-in-time ROC, fees $0.005/sh + 5 bps slippage) Oct 2015 → Aug 2026: **CAGR 9.6%, Sharpe 0.58, MaxDD −32.3%** vs SPY **CAGR 13.8%, Sharpe 0.81** and QQQ **CAGR 19.5%, Sharpe 0.91**. Underperforms both benchmarks on return and Sharpe in every tested window; the only outperformance is a single bear-year dodge (2022: +2.1% vs SPY −18.6%, +20.7pp), which does not compound — the strategy gives it back in bull years.
**Classification:** Cross-sectional equity momentum rotation (monthly top-2 of 11 sector SPDRs + QQQ)
**Research spec:** none filed
**Source:** QC algorithm added to `research/Short-term-sector/short-term-sector.py` (docstring claims edge "validated Jan 2023 → present and back to Oct 2015")

## 1. Executive Summary

Monthly top-2 sector momentum rotation: score 11 sector SPDRs + QQQ by trailing 21-trading-day rate of change, hold the top 2 equal-weight, fully invested, rebalance on the first trading day of the month, 3% free-cash buffer.

**Verdict: the claimed edge does not reproduce in any window, net of costs.** A QC-cloud backtest of the same algorithm (Jan 2023 → Aug 2026, order log d274f46d) reported 62.6% total / Sharpe 0.46 — reproduced here as 61.4% with point-in-time ROC and raw prices, so those stats are real. But that window also shows QQQ at +33.4% CAGR: the rotation simply lags the benchmark it would rotate. Full-window (bear included) still trails SPY by ~4.2pp CAGR and QQQ by ~10pp.

## 2. Reproduction

- Universe/signal/rebalance replicated 1:1 from the QC algorithm. ROC uses closes through the previous trading day (point-in-time; matches the indicator state at the 10:30 ET scheduled event — a v1 probe that included the rebalance-day close inflated results ~2x and was fixed in v2).
- Data: yfinance daily closes, raw (non-dividend-reinvested, matching QC backtests), Oct 2015 → Aug 2026 (2,728 trading days).
- Costs: QC-style $0.005/share fee + 5 bps slippage per side.

| Window | Strategy | SPY | QQQ | EQW basket |
|---|---|---|---|---|
| Oct 2015 → Aug 2026 | CAGR 9.6%, Sharpe 0.58, DD −32.3% | **13.8% / 0.81 / −34.1%** | **19.5% / 0.91 / −35.6%** | 13.0% / 0.78 / −32.9% |
| Jan 2023 → Aug 2026 | CAGR 14.3%, Sharpe 0.90, DD −17.3% | n/a | **33.4% / 1.52 / −22.8%** | 22.4% / 1.43 |
| 2022 (bear, calendar) | **+2.1%** | −18.6% | n/a | n/a |
| Oct 2015 → Dec 2022 | CAGR 8.7%, Sharpe 0.52, DD −34.5% | **12.0% / 0.69 / −33.7%** | 14.5% / 0.70 | n/a |

## 3. Structural notes

- **The "2015-2022 beat SPY by 18pp" claim collapses to 2022 alone** (+20.7pp that year); net over 2015-2022 is −3.3pp CAGR vs SPY. Bear-market dodge, not compounding alpha.
- QQQ is included as a "sector", so top-2 momentum frequently picks QQQ + XLK — partly a disguised QQQ surrogate (explains similar drawdowns without the compounding).
- Average turnover per rebalance ≈ 147% of portfolio value (measured) — the whole book rotates ~1.5x monthly; ~4 orders/month consistent with the QC order log (143 orders, market-on-close fills, real rotation each month start).
- Code check (QC API): no lookahead, indicators warmed up, schedule/holdings calls valid. Docstring claims validation back to Oct 2015 but `set_start_date(2023, 1, 1)` only covers 3.6 years.
- QC-cloud "turnover ~5%" figure is not reproducible (measured 147%/rebalance) — metric is mislabeled or differently defined; does not change the verdict.

## 4. Replication

`research/Short-term-sector/run_probe.py` → `outputs/short_term_sector_summary.json`

## 5. Meta-lesson

Recorded in [Retail Edge Landscape — Post-Test Synthesis](../IA/retail-edge-landscape.md): this test is the repo's cleanest demonstration that a documented public-OHLCV pattern on liquid ETFs does not survive honest execution + benchmarking. The strategy's only genuine deliverable was modest, regime-dependent drawdown reduction.