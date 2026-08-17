# Liquidity Provision Probe — Pre-registered Spec

**Date:** 2026-08-17
**Type:** Pre-registered research program (lane: liquidity provision on crypto perps; the only remaining lane where small capital is not a handicap and infra already exists — `research/crypto-perps/`, `research/funding-basis/`).
**Purpose:** Answer, with the same harness discipline that produced every prior verdict: does passive (maker) liquidity provision at the mid capture more spread than it loses to adverse selection, net of maker fees, at retail scale? Ends with: surviving edge (live paper-quote next step), or a documented DISCONFIRMED verdict that closes the lane without L2 data (the paid variant).

## 1. Method (frozen)

Simulate maker quoting on historical 1-minute klines, one unit of inventory per symbol, one position at a time:

1. **Reference price:** minute `open` (point-in-time, no lookahead).
2. **Quote:** bid = open × (1 − s/2), ask = open × (1 + s/2), where `s` is the assumed full spread in bps. Primary assumption: s = 1 bp (BTC), 2 bps (ETH) — typical top-of-book perp spreads on Binance USDT-M. Robustness run (NOT a second search): s = 5 bps for both.
3. **Fill rule (trade-through test):** BUY bid fills at the first minute m ≥ t whose `low_m ≤ bid`; SELL ask fills at the first minute m ≥ t whose `high_m ≥ ask`. Quote valid for K = 60 minutes, then cancelled (no trade, no PnL).
4. **Exit:** at `mid` of the fill minute + k, k = 1 minute, executed as maker (maker fee applied). Inventory never exceeds 1 unit; no concurrent positions.
5. **Cost model:** maker fee 0.02% (2 bps) on fill and on exit → 4 bps round trip (Binance USDT-M standard maker rate).
6. **Edge per round trip (bps of notional):** buys: (exit_mid − entry_bid)/entry_bid; sells: (entry_ask − exit_mid)/entry_ask; minus 4 bps fees.
7. **Bias register (pre-registered, honest limits of kline data):**
   - Quoting at mid ≈ top-of-book only when the touch is symmetric around mid (usually true at 1–2 bps). Understates spread capture when the true spread is wider (conservative).
   - Fill priority: we assume first-in-queue at trade-through. Optimistic (real queue position unknown). Net bias approximately neutral vs real top-of-book quoting; recorded, not claimed exact.
   - Aggressive-side conditioning (taker_buy_volume), inventory skew management, and queue-position modeling are deferred axes — not needed for the primary gate, will be used only in the live-paper step if the probe passes.

## 2. Data (owned, frozen)

| Symbol | Source | Window | Rows |
|---|---|---|---|
| BTCUSDT 1m | `research/crypto-perps/cache/BTCUSDT_1m.parquet` | 2020-01-01 → 2026-07-31 | 3,461,760 |
| ETHUSDT 1m | `research/crypto-perps/cache/ETHUSDT_1m.parquet` | 2020-01-01 → 2026-07-31 | 3,461,760 |

## 3. Gate (frozen)

A pass requires **all** of:
1. **G1 (primary):** bootstrap 5th percentile of mean per-trade edge > 0 bps (10,000 resamples; per-trade iid; block-by-day robustness reported, not gated) on BTCUSDT.
2. **G2:** median per-trade edge > 0 and hit rate (positive trades) > 45% on BTCUSDT.
3. **G3:** mean edge positive on ETHUSDT too (not single-symbol).
4. **G4 (sub-window):** 2023-01-01 → 2026-07-31 p5 > 0 on BTCUSDT (OOS-style consistency, same sign).

**Stop rule (pre-registered):** if G1 fails (BTC p5 ≤ 0), the lane is closed at mid-quote passive fills without queue priority — verdict **DISCONFIRMED**, no further LP work without paid L2 data. If all gates pass, the next step is live paper-mode maker quoting (via `research/funding-basis/` CLI infra) with minimum size, gated again before real capital.

**Anti-result-hunting rules (pre-registered):**
- Spread assumption and K frozen before results are seen; s = 5 bps robustness run does not change the gate.
- No parameter is tuned to the outcome; the spec is the gate.
- A dead result is a valid result ("mid-quote LP without queue priority is toxic-flow food").

## 4. Status

- **2026-08-17:** Spec frozen. Implementation: `lp_probe.py` next (vectorized trade-through test on both symbols). Then run, then verdict.
- **2026-08-17b:** Run complete — **verdict DISCONFIRMED** (G1-G4 all FAIL). `outputs/lp_probe_summary.json`. BTCUSDT full window: mean −9.42 bps/trade, median −7.29, hit rate 7.0%, bootstrap p5 −9.50. ETHUSDT: mean −10.82 bps, p5 −10.91. Sub-window 2023+ and 5 bps robustness: same sign, all negative. Passive fills at the mid are toxic-flow food at retail queue position: fills concentrate on trade-throughs (buy fills 1.13M vs 580k sells on BTC — fills cluster when price dips through our level), the 1-minute continuation eats the exit, and 4 bps maker fees finish it. Per the pre-registered stop rule, the lane is closed at mid-quote passive fills without queue priority; no further LP work without paid L2 data.
- **Integrity note:** the first implementation run printed a PASS (+3.18 bps BTC) caused by a classification bug — trade side was inferred by comparing entry vs exit price (entry <= exit → "buy"), which flips every losing trade into a fake winner of the opposite type. Fixed by carrying the actual fill side from the quote logic; corrected run is the verdict above. This is the kind of harness-level error the positive-control program exists to catch.