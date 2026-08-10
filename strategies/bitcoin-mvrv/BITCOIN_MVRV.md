# Bitcoin MVRV Smart DCA

**Version:** 0.1 (registered, 2026-08-09 — not yet tested)
**Status:** REGISTERED / NOT TESTED — pre-registration drafted in the research spec; awaiting reviewer scope + data (thresholds, allocation multiplier, benchmarks, IS/OOS split). No backtest has been run.
**Classification:** On-chain valuation/timing — dynamic accumulation vs static DCA and buy-and-hold (relative-allocation claim, not a novel alpha trade)
**Research spec:** `IA/bitcoin-mvrv-research-spec.md`
**Source:** `transcribe.txt` ("Five Structural Edges" transcript) — "MVRV Z-score standardizes the deviation of market value from realized value, flagging absolute capitulation and extreme euphoria; the dynamic MVRV DCA [vs] static DCA and buy-and-hold." Cites Grois/Grosjean/Nasman 2026 on-chain cycle research.

## 1. Executive Summary

MVRV Z-score measures how far Bitcoin's market value deviates from the aggregate cost basis (realized value), normalized by historical variance. Low values = capitulation (below aggregate cost), high values = euphoria. The transcript claims a dynamic MVRV DCA beats a static DCA and buy-and-hold.

**Honest prior:** the realistic win is **lower max drawdown**, not higher CAGR — MVRV timing trades return for valuation discipline across cycles. This is a relative-allocation/risk-timing tool. 2013+ gives only ~3-4 completed cycles, so OOS is a small number of independent regimes and verdicts must be tempered.

**Status:** REGISTERED only. Pre-registration drafted (frozen rules, IS/OOS, friction, gates); NOT tested. No probe has been run — awaiting reviewer scope + data acquisition.

## 2. Claimed vs. honest expectation

| Dimension | Claim | Honest prior |
|---|---|---|
| CAGR | dynamic DCA beats B&H | Not necessarily — timing trades return for drawdown |
| Max drawdown | dynamic DCA lower | **Primary claim** — likely real, needs test |
| Sharpe / vol | dynamic DCA better | Secondary — plausible |
| Cycles | several | ~3-4 completed (2013-14, 2017-18, 2020-22, 2023-26) — small OOS |

## 3. Proposed rule (draft — to be frozen)

- Signal: MVRV Z-score with low band (accumulate/overweight) and high band (trim/underweight).
- Dynamic DCA: baseline periodic allocation; low-Z multiplies the contribution, high-Z reduces/stops it, cash rerouted to low-Z regimes.
- Benchmarks: static DCA (same total capital) and buy-and-hold.
- Friction: on-chain/CEX spread + withdrawal, 10-25 bps/trade; cash-drag cost included.
- Primary metric: max drawdown of dynamic DCA vs buy-and-hold; secondary: CAGR/Sharpe.

## 4. Pre-registered gates (draft)

| Gate | Criterion |
|---|---|
| 1 | OOS max DD of dynamic DCA strictly below B&H (after friction) |
| 2 | DD improvement survives threshold perturbation (not a knife-edge) |
| 3 | OOS CAGR not materially worse than B&H (within tolerance) |
| 4 | Not driven by a single cycle (drop-best → direction holds) |
| 5 | IS reproduction of the DD improvement |
| 6 | Look-ahead clean (Z from data ≤ entry day only) |

Verdict: DISCONFIRMED if any gate fails; CLEARS-OOS only if a robust, non-knife-edge max-DD improvement over B&H on OOS without material CAGR sacrifice.

## 5. Status / Log

- **2026-08-09:** Research spec + strategy doc created (REGISTERED, NOT tested). Free data routes confirmed (Blockchain.com MVRV/RV chart, Coin Metrics realized-cap, 2013+). Awaiting reviewer scope. No probe run.

## 6. Conclusion & Next Steps

Gold-standard discipline from the prior probes applies: on reviewer go, freeze the rules, acquire free on-chain data (Blockchain.com/Coin Metrics realized-cap), run IS/OOS with the strict gates above, and report max drawdown + CAGR with the cycle-count caveat. Until then this remains registered, not tested — consistent with the umbrella decision of the Five Structural Edges register.
