# Short Vol: Tail-Overlay Premium Capture (V3)

**Version:** 1.0
**Status:** DISCONFIRMED (2026-08-08) - pre-registered in `IA/vol-risk-premium-research-spec.md` §15; §16 records the result. The tail-overlay bounded the tail (max DD 95%→62%) but **destroyed the harvest**: total return went +452% (naive) to −26% (overlay), because the stress signals fled the premium-rich regimes (skipped +646% of the premium, kept −26%). NOT an edge; candidate closed.
**Classification:** Options / Variance Risk Premium with a tail-risk regime overlay.

## 1. Executive Summary

V1 confirmed the variance risk premium *level* is positive (+3.3 to +4.1 vol pts all eras). V2 showed the **naive** harvest — just being long short-vol (SVXY) — makes +452% but with a **−95% max drawdown** (a −83% single day in 2018 volmageddon, and the 2020 crash), i.e. ruin risk, not an edge. V3 is the natural next design: **keep collecting the premium (long short-vol core), but add a tail-risk overlay that exits to cash when a stress regime triggers.** This is how professional short-vol managers earn the premium while bounding the tail.

## 2. The Design

**Core (collect the glitch):** long the short-vol ETP (SVXY). In calm regimes this harvests the +3-4 vol-point premium most days.

**Overlay (dodge the tail):** when any crash-imminent signal is active, stand flat (cash). The signals are directional-risk indicators — deliberately NOT the premium level (V2 showed the premium is richest right before the crash, so "sell when rich" does not protect):
1. **Term-structure inversion:** `VIX − VIX3M > 0` (near-term implied above 3-month = stress).
2. **Elevated/rising VIX:** `VIX > 30` or 5-day VIX change > +10%.
3. **Equity stress:** SPY down >5% from its 60-day high.

Return to long short-vol only when all triggers clear.

## 3. Why it might work (and might not)
- **Might:** the overlay converts the −95% tail into a bounded one, keeping most of the premium captured in calm months. Crash regimes are usually preceded by term-structure/VIX stress, potentially detectable early.
- **Might not:** crashes (esp. 2018) are sudden; the overlay may fire only after giving back a chunk, and **whipsaw** (exit then vol falls, premium resumes) can cost more than it protects.

## 4. Frozen Tests / Gates (mirror spec §15.D)
1. **Tail bounded:** max drawdown must be < −40% (vs naive −95%). FAIL => DISCONFIRMED.
2. **Harvestable net:** total return > 0 over 2011-2026.
3. **Overlay adds value:** must beat naive buy-and-hold on risk-adjusted (lower max DD while keeping positive return).

## 5. Data (all free / owned)
- SVXY (short-vol ETP) — owned (Yahoo).
- VIX, VIX3M, VIX9D — free official CBOE CDN (cached).
- SPY daily (drawdown / realized stress) — owned.

## 6. Current Status
**DISCONFIRMED (2026-08-08).** The overlay bounded the tail (max DD −95% → −62%) but killed the edge: total return −26% vs +452% naive. Cause: the stress triggers (term inversion / elevated-rising VIX / equity drawdown) fire during elevated-vol premium-rich regimes, exactly where short-vol earns its best returns; exiting there skipped +646% of compounded premium and kept only −26%. An "elevated vol" exit is the opposite of what a short-vol strategy needs. Combined with V2 (naive ruin) and V1 (real level), the short-vol / VRP family is closed as untradeable.
