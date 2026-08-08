# NQ VWAP-Pullback ("Drift VWOP Pullback" / Prop-Firm Golden Ticket)

**Version:** 0.1 (pre-registered probe — not yet run)
**Status:** UNDER RESEARCH — pre-registered bounded probe (2026-08-08); rules locked, data owned (Databento NQ intraday); gates decide advance vs disconfirm on an explicit out-of-sample window.
**Classification:** Execution microstructure — VWAP-anchored-at-open intraday pullback mean reversion in NQ futures, claimed to expose institutional execution-algorithm flow
**Research spec:** `IA/nq-vwap-pullback-research-spec.md`
**Source:** public interview strategy (M. Kanti, ex-market-maker / quant CIO, SQR Capital) marketed as a "prop firm golden ticket" for passing funded challenges. Rules below are extracted verbatim and frozen unchanged.

## 1. Executive Summary

A fully mechanical intraday long/short strategy on **NQ futures**: anchored-at-open VWAP gives the day's bias; a 15-min drift filter ("is there a trend?") and a 1-hour distance filter confirm the drift; entry is at the first pullback candle back toward the VWAP, in the drift direction. Exits are fixed 2:1 (risk:reward) losers with tight day/guard rails (1 position, max 4 trades, max 2 losses/day, no trades 09:30–10:30 ET, flat 15:55 ET).

The honest framing matters: this is a **negative reward:risk, high-win-rate** strategy — profitable because of a ~64% win rate, not because of per-trade edge. That makes it fit the mathematics of funded prop challenges (high pass probability despite low reward:risk) but structurally fragile to a modest win-rate or tail decline. The probe tests whether the underlying VWAP-pullback signal earns a real friction-adjusted, out-of-sample edge — the one thing the marketing claim does not demonstrate.

## 2. Intent

To decide, with a pre-registered gate and an explicit out-of-sample window (2025-01-01 → 2026-08-07, unseen by the claimed 2020–2024 development), whether the locked rule set produces a real edge or is another clean disconfirmation. Runs on the already-owned Databento intraday futures stack.

## 3. Rules (FROZEN — locked verbatim from the source, do not tune)

**Instrument / bars:** NQ futures, 5-min execution / 15-min trend bars, RTH only (09:30–16:00 ET).

- **Anchored VWAP:** VWAP anchored at 09:30 ET RTH open, session-reset daily, computed from the 1-min base.
- **Trend conditions (every 15-min bar; LONG shown, SHORT is mirror):**
  1. Price above anchored VWAP (below for SHORT).
  2. VWAP rising over the past 15 min (now > previous 15-min VWAP; falling for SHORT).
  3. Over the past 1 hour, price moved >= +0.10% (<= -0.10% for SHORT).
- **No-trade window:** 09:30–10:30 ET.
- **Trigger (after all 3 conditions true):** first pullback candle — first red 5-min candle for LONG (first green for SHORT); enter at **open of the following bar** (market order).
- **Exit / risk:** LONG risk 80 / target 40 pts; SHORT risk 80 / target 50 pts; whichever hits first.
- **Guard rails:** 1 position at a time; max 4 trades/day; max 2 losses/day; no new trades after 15:30 ET; flat at 15:55 ET.

## 4. Claimed vs tested

| Claimed (source) | What we test OOS |
|---|---|
| ~64% win rate | same, on OOS trades |
| avg win +866 / avg loss −1300 pts | same, net of friction |
| 300%+ over ~4,000+ trades (2021→2026) | OOS 2025→2026-08, net of friction |
| 49.8% pass per challenge / 93.6% in 4 attempts (prop-firm math) | NOT replicated — prop pass/fail math, not edge; out of scope |
| Developed IS 2020–2024, OOS 2024–2026 | we reproduce this exact discipline with a clean 2025+ OOS holdout |

## 5. Profit / loss driver

The edge (if real) is institutional execution-algorithm flow: when price pulls to the anchored VWAP, VWAP-targeting execution algorithms intensify, and their side-imbalance (more sellers than buyers) is revealed as a sharp continuation push. The pullback entry in the drift direction captures that continuation.

## 6. Risk and Failure Modes

- **Win-rate fragility (primary):** negative reward:risk means a modest OOS win-rate decline (64% → <55%) eliminates the edge. Explicit OOS gate.
- **Mean-reversion decay:** the intraday mean-reversion/vol-fade family has repeatedly failed daily-scale tests; microstructural decay could make this stale OOS.
- **Look-ahead:** VWAP must be computed from the 1-min base only up to the trigger bar's open; any leakage fails the probe (audit gate).
- **Slippage/commissions:** NQ 0.5–1.0 pt round-trip friction applied; a tight 2:1 stop is friction-sensitive.
- **Regime:** futures edge may be regime-dependent (2022 hikes, 2020/2022 vol); flagged for follow-up if it clears.
- **Not deployable with own capital as advertised:** the strategy is framed around funded-challenge pass math, not self-capital return; not an "own-capital deploy" without further work even if it clears the probe.

## 7. Status / Log

- **2026-08-08:** Spec + strategy doc created; rules locked; data confirmed owned (Databento NQ intraday, key+client in repo); intraday infra reused from the spx_gex/index_rebalancing stack. Probe not yet run.

## 8. Next Steps

1. Scaffold `research/nq-vwap-pullback/` (`Makefile`, fetch/resample/run scripts) + `src/quant_scripts/nq_vwap_pullback/` (bars, vwap, event/backtest engine).
2. Fetch NQ 1-min (Databento `GLBX.MDP3`), cache to `research/nq-vwap-pullback/cache/`.
3. Gate 5 first: in-sample (2020–2024) reproduction of the claimed ~64% win rate with frozen rules.
4. Run OOS (2025-01-01 → 2026-08-07) through gates 1–4, 6; write readout to `outputs/`.
5. Record advance vs disconfirm in both this doc and the spec.
