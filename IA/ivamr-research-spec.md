# IVAMR (Intraday Value Area Momentum & Mean Reversion) — Research & Pre-Registration Specification

**Status:** Pre-research specification (bounded falsifiable probe, 2026-08-08). Reopened from a prior decline (see §10 of `strategies/ivamr/IVAMR.md`) because a genuine pre-2023 intraday out-of-sample window is now available (Databento NQ 1-min from 2013).
**Classification:** Intraday Volume Profile — Value Area breakout momentum + Value Area break-in mean reversion, on NQ futures, RTH only.
**Source claim:** the machine-executable blueprint in `strategies/ivamr/IVAMR.md` (Volume Profile / Auction Market Theory; explicitly NOT the Gao-Han-Li-Zhou "Market Intraday Momentum" paper — §8.A). Rules are extracted from that blueprint verbatim and frozen for the probe.
**Purpose:** Decide, with pre-registered gates and an explicit pre-2023 out-of-sample window, whether the volume-profile mechanic earns a live friction-adjusted edge on NQ — or should remain permanently binned.

---

## 1. Why now (reopen justification)

IVAMR was declined for testing on 2026-08-04 solely because our intraday feed (`EQUS.MINI`) began 2023-03-28, so the spec's own IS/OOS protocol was **unfalsifiable** (no out-of-sample period). The reopen condition was: *"new intraday data covering a genuine out-of-sample period (pre-2023)."*

**That condition is now met.** We own Databento `GLBX.MDP3` NQ 1-minute RTH data, verified clean and continuous for **2013 → present** (~1,100–1,380 rows per RTH day each weekday across 2013–2023; 2010–2012 too sparse/missing, pre-2010 unavailable). We therefore pre-register a faithful IS/OOS split using the available years:

- **In-sample (IS): 2014-01-01 → 2018-12-31** (5 years, pre-holdout)
- **Out-of-sample (OOS): 2019-01-01 → 2023-12-31** (5 years, the pre-2023 holdout that previously was impossible)

This preserves the spec's *intent*: a genuine multi-year out-of-sample window that was never touched during rule development, fully before 2023. It deviates only in that IS starts 2014 rather than 2010 (data limitation), which tightens the OOS/IS comparability rather than loosening it (2019–2023 vs 2014–2018 are adjacent, same regime mix).

---

## 2. Frozen rule set (extracted verbatim from IVAMR.md — do not tune)

Instrument: **NQ** futures (CME E-mini Nasdaq-100), 15-min entry bars, RTH only (09:30–16:00 ET).

**Daily inputs (computed from the PREVIOUS trading day's RTH session only):**
1. **70% Value Area** from a volume-at-price histogram of previous-day RTH 1-min data (bin size 0.25 index points; §8.B requires 1-min or tick, never 15-min OHLCV as-a-histogram):
   - **POC** = price level with highest traded volume.
   - **VAH** = top edge of the 70% value area.
   - **VAL** = bottom edge of the 70% value area.
2. **14-period 15-min ATR**, computed from previous-day RTH 15-min candles, ending 16:00 ET.

**Time / risk filters (§4.A):**
- No entries before 09:45 ET.
- No new setups evaluated after 14:15 ET; no entries after 14:30 ET.
- Hard time exit at 15:30 ET (market order; NOT MOC).
- Daily kill switch: halt for the day if realized loss reaches 3% of equity.
- One position at a time.

**Entry: market order at the OPEN of the bar AFTER the confirmation candle (Candle N+2).**

- **Play 1 — Bullish breakout & retest (long, trend):**
  1. 15-min close > prev VAH.
  2. Next 15-min low <= prev VAH (retest).
  3. That low >= prev VAH − (0.5 × ATR) (structural integrity).
  4. That next candle closes > prev VAH (confirmation).
  → queue long at next bar open.
- **Play 2 — Bearish breakout & retest (short, trend):** mirror of Play 1 on VAL.
- **Play 3 — Bullish break-in / fade breakdown (long, mean reversion):**
  1. 15-min low < prev VAL.
  2. 15-min close > prev VAL.
  3. (close − low)/(high − low) >= 0.60.
  → market buy at next bar open.
- **Play 4 — Bearish break-in / fade breakout (short, mean reversion):** mirror of Play 3 on VAH.

**Exits:**
- **Plays 1 & 2 (trend):** stop loss = entry ± (2.0 × ATR); no fixed target (trailing stop). Trailing: if intra-bar high >= entry + (1.5 × ATR) (long), move stop to breakeven immediately; thereafter trail the stop at the 2-period 15-min low (long) / high (short). **Intra-bar evaluation required (§8.D).**
- **Plays 3 & 4 (mean reversion):** stop loss = trigger-candle extreme ± (0.5 × ATR); take profit = previous-day POC. Pre-flight checks: (1) POC must be on the correct side of entry; (2) target distance >= 1.5 × stop distance, else abort.

**Friction:** NQ tick = 0.25 pts. Slippage + commission modeled as a per-round-trip cost applied at exit, symmetric for all plays.

**Claimed performance to falsify (from §6):** PF >= 1.3; avg trade (net) >= 0.2% of account; max DD <= 15%; trend win rate >= 40%; mean-reversion win rate >= 55%; OOS net >= 70% of IS net. We treat these as the candidate's own success thresholds and report each; the decision gates (§5) are the binding pre-registered tests.

---

## 3. Mechanism / why (per claim) and the honest prior

**Claimed edge:** a **price-location** anomaly (not a time anomaly). Value Area levels are institutional reference prices. Breaking VAH/VAL triggers cascades of stop orders from undercapitalized retail and overnight holders; institutional VWAP/TWAP algo flow absorbs the other side, generating momentum (Plays 1/2). When price pierces a value extreme but closes back inside, the breakout buyers are trapped and their stop-outs provide liquidity for a snap-back to POC (Plays 3/4).

**Honest prior (caution):** IVAMR is a **behavioral** edge (counterparties = retail traders), explicitly conceded in §8.A as having a "finite half-life." By our institutional framework we prefer structural (mandated-flow) edges; behavioral edges decay and need constant monitoring. It is also the **same intraday futures family** we just disconfirmed on the identical NQ feed (VWAP-pullback probe, 2026-08-08): the sight-of-claim win-rate economics did not survive costs. IVAMR differs in a genuinely material way — volatility-adjusted stops, a volume-profile (not VWAP) reference, and full intra-bar stop simulation — so it is not a clone; but the prior is weak and the burden is on the data. The probe exists to test the mechanic honestly, not to validate the blueprint.

---

## 4. Pre-registered test design

**Data:** Databento `ohlcv-1m` NQ (`GLBX.MDP3`, continuous lead contract `NQ.n.0`), RTH 09:30–16:00 ET, cached as 1-min parquet and resampled to 15-min bars.

**Split (immutable):** IS **2014-01-01 → 2018-12-31**; OOS **2019-01-01 → 2023-12-31**. Both unseen-with-respect-to-development; OOS is entirely pre-2023.

**Look-ahead discipline (audit gate):**
- VAH/VAL/POC computed from PREVIOUS-day RTH only; never the current day, never including the entry candle's own close.
- ATR computed from PREVIOUS-day RTH only.
- All entries execute at the open of Candle N+2 (signal known only after N+1 closes).
- Trailing stop and breakeven use **intra-bar** high/low, never the closing price ($8.D), so stops cannot be silently out-run.

---

## 5. Pre-registered decision gates (frozen, mirror VWAP strict discipline)

The probe FAILS (disconfirmed) if ANY of the following holds on the OOS window; the probe ADVANCES only if all OOS gates AND the IS reproduction gate pass.

1. **OOS net edge not positive:** OOS friction-adjusted total return (index points, notional-normalized) <= 0.
2. **OOS bootstrap p5 not positive:** per-day OOS net-return 5th percentile from >=5,000 bootstrap resamples <= 0.
3. **OOS economics collapse:** OOS profit factor < 1.0 OR overall win rate < 0.50 (regardless of the per-play split), OR (where reported) trend win rate < 0.40 or mean-reversion win rate < 0.55.
4. **Tail fragility:** fraction of active OOS days hitting the 3%-equity daily kill-switch cap >= 0.30, OR the strategy is net-negative in gross (pre-friction) terms on OOS — indicating the economics fail even before costs.
5. **IS reproduction failure:** the frozen rules cannot reproduce a net-positive IS result (gate 5 checked first; if IS is net-negative, record the claim as irreproducible and stop, do not proceed to OOS).
6. **Look-ahead / artifact:** any leak of future information (current-day profile mixing, entry-at-close, close-only stops) — fails the probe and is fixed, then re-run with the fix applied to both windows.

**Verdict rules:** clean pass = all gates pass → record as strong, scale up (persistence/decay, regime conditioning, then deploy decision). Any gate fail = **DISCONFIRMED**, candidate permanently closed.

---

## 6. Data & tools (owned — cheap)

- **Databento** (`DATABENTO_API_KEY` in repo `.env`; client installed): NQ `ohlcv-1m` futures, `GLBX.MDP3`, `NQ.n.0` continuous lead contract; RTH filter + session-anchored computations in-feed. Verified clean 2013→present.
- **Caching:** parquet cache under `research/ivamr/cache/`, resumable chunked fetch (reuse the NQ VWAP-pullback fetch pattern: 30-day chunks, per-chunk retry on transient Databento 504/stream drops, trailing boundary clamped to dataset availability).
- **No additional key/license needed.** yfinance is explicitly prohibited by the blueprint and is not viable intraday anyway.
- **Volume at price:** computed from the 1-min RTH base with a fixed 0.25-pt bin (§8.B); never from 15-min OHLCV as if it were a histogram.

---

## 7. Instrument choice

Primary: **NQ** (matches the blueprint; most liquid index future). /ES is a permitted cross-check only, reported separately if used. Fixed before the run; not a free parameter.

---

## 8. What we are deciding

This probe decides whether the **volume-profile Value Area breakout/fade family** — the specific mechanic the IVAMR blueprint was designed to trade — earns a friction-adjusted, out-of-sample edge on NQ, or joins the disconfirmation list. It deliberately reuses the exact gate discipline (net>0, p5 bootstrap, IS reproduction, look-ahead audit) as the VWAP-pullback probe so results are comparable.

- **Clears all gates on OOS** ⇒ scale up: persistence/decay test, regime conditioning, position-sizing/equity curve, then a deploy decision.
- **Fails cleanly** ⇒ the volume-profile intraday family is disconfirmed at this construction; record it and close permanently.

---

## 9. Status

- **2026-08-08:** Spec pre-registered. Reopen condition met (Databento NQ 1-min clean 2013→present verified). Rules frozen per §2, split per §4, gates per §5.
- **2026-08-08 (later):** Probe executed. Full 2013-2023 NQ 1-min cache built (973,224 rows); engine scaffolded (`src/quant_scripts/ivamr/`), verified on synthetic + real data. **Verdict: DISCONFIRMED** — all five gates failed (IS 2014-2018: 517 trades, wr 49.9%, PF 0.80, net -1,096.89; OOS 2019-2023: 576 trades, wr 47.9%, PF 0.78, net -3,695.53). Gate 6 look-ahead passed; all economic gates failed. Blueprint Go/No-Go gates also fail (PF 0.78<1.3, avg trade ~0.09% equity<0.2%, MR wr 39.5%<55%). Play breakdown, kill-switch, and interpretation recorded in `strategies/ivamr/IVAMR.md` §10. Candidate closed.
