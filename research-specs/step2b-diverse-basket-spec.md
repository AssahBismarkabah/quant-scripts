# Step 2b — Diverse Free-Data Basket (preregistered spec)

**Status:** PRE-REGISTERED 2026-08-12 — frozen before any run. No post-hoc member/parameter/data selection.
**Purpose:** The last free-data aggregation test (per `../IA/path-forward-decision-memo.md` §3 Step 2, corrected by the 2026-08-12e scoping audit). Tests whether a GENUINELY diverse book (multi-asset + cross-sectional, long/short — not all-long-equity) clears the pre-registered OOS gates. If it fails, "free-data portfolio alpha at our scale is measured-dead" is finally earned and the buy-data-vs-stop fork is decided.

## Data (all reliable, free, keyless; NO dependency on blocked Yahoo/Stooq)

| Leg | Data | Source | Freq | Range |
|---|---|---|---|---|
| XS momentum / reversal / low-vol | PEAD panel: `../research/pead/cache/prices_adj_long.parquet` (7,786 symbols, adj close) | local (Kaggle) | daily→monthly | 1998-01 → 2021-06 |
| Term premium | `DGS10` (10Y yield), `DGS2` (2Y) | FRED | daily | 1990+ |
| FX carry | `DEXUSAL` (US/AUD USD-per-AUD), `IR3TIB01USM156N` (US 3M), `IR3TIB01AUM156N` (AU 3M) | FRED | FX daily / rates monthly | 1990+ |
| Commodity seasonality | `DCOILWTICO` (WTI spot) | FRED | daily | 1990+ |

## Members (each a full mini-strategy: entry, exit, sizing, and a WHY)

### Cross-sectional members (monthly rebalance, long top quintile / short bottom quintile, equal-weight, market-neutral):
1. **mom12_1** — cross-sectional 12-month momentum (skip last month). Why: trend / behavioral underreaction.
2. **rev1m** — cross-sectional 1-month reversal (inverse). Why: mean-reversion / liquidity provision.
3. **lowvol** — cross-sectional trailing 1-year realized-vol (long low-vol / short high-vol). Why: risk-premium compensation.

### Multi-asset members:
4. **term** — term premium. Position in a 10Y-duration bond proxy; long when the 10Y-2Y slope is > its own trailing average, short when below. Why: duration/term-premium risk.
   - Bond return modeled by duration approximation from DGS10 changes: `r_b ≈ -Dur·ΔYield + carry` (no TLT price needed).
5. **fx_carry** — long AUDUSD (spot return leg from DEXUSAL) when AU 3M rate > US 3M rate, short when below; flat when equal. Monthly signal. Why: carry / UIP violation.
6. **commodity_season** — oil seasonality: long WTI spot (DCOILWTICO) during its historically-strong window, flat otherwise. Pre-registered window: Jun-Aug (summer driving season) — frozen, no in-sample selection.

## Combination rule (frozen)
- Convert each member to a daily position weight, z-score normalized within its OWN estimation window (IS-only where possible).
- Cross-sectional members are market-neutral L/S (zero beta by construction). Multi-asset members are also combined as z-scores.
- **Book = equal-weight mean of member z-scores**, THEN scaled to 10% annualized vol with the same trailing-realized-vol scaler as Step 2a.
- **Drag guard (auditor's warning):** each member is independently z-scored (units are comparable), and the book is LONG on net positive aggregate z; no single member's sign can dominate because all are treated symmetrically. A persistently-negative member (like a bad reversal leg) still drags the book — the test is whether the AGGREGATE clears, which is exactly the question. We do NOT drop members post-hoc.

## Short-leg honesty (borrow costs)
- Cross-sectional short legs: apply a **pre-registered flat 150bps/yr** borrow cost on the short notional (conservative for the small/illiquid names in bottom quintiles), in addition to the 10bp/side friction.
- Multi-asset legs: no borrow (spot/futures-style), apply 10bp/side friction.

## Friction model (corrected pre-run, 2026-08-12)
Costs are charged where positions actually change (per member), NOT as a global per-day cost (a per-day 10bp would overstate cost ~21x for a monthly-rebalanced book and is a bug):
- XS members: **20bp per monthly rebalance** (2 sides × 10bp) folded into each monthly L/S return; plus the 150bps/yr short-leg borrow.
- Multi-asset members: **10bp per signal flip** (infrequent for term/fx/commodity).
- No additional global daily friction on the book.

## Windows
- IS: 2000-01-01 → 2008-12-31 (panel XS needs 12m lookback; XS from 1999)
- OOS: 2010-01-01 → 2021-06-14 (panel end)
- Note: multi-asset members start earlier; XS panel bounds the common window to 2000-2021 (price data to 2021-06).

## Frozen OOS gates (per memo §3 / Step 2b)
1. Bootstrap p5 of the book's mean daily excess return > 0 (OOS)
2. Profit factor >= 1.0 (OOS)
3. Robustness to holdout split (direction positive in both halves)
Verdict: **CLEARS-OOS** only if all three pass; else **FAILS-OOS** → free-data portfolio alpha is measured-dead at our scale → fork to (a) buy data or (b) stop.

## Status
- **2026-08-12:** Spec frozen. Data verified: PEAD panel loaded (7,786 sym, 1998-06/2021); FRED keys confirmed (DGS10/DGS2/DTB3/IR3TIB/USM/DEXUSAL/DEXUSEU/DCOILWTICO all 200). Yahoo/Stooq blocked (429 / JS challenge) — explicitly excluded; FRED + local panel cover all legs. Next: build `../research/portfolio-book/step2b_diverse_basket.py`.
- **2026-08-12f (RESULT — FAILS-OOS under honest shorting costs):** Run complete. Risk-parity combination of the 6 members; three construction bugs (spike, per-day friction, z-score vol-scale blow-up) found and fixed during the build. **Key finding:** the book only clears OOS under an optimistic 1.5%/yr short-borrow cost; at a realistic **5%/yr hard-to-borrow cost it FAILS-OOS** (p5 = −0.78bps < 0, PF 1.006, holdout 2nd half negative). The apparent edge is carried by `rev1m` shorting unborrowable bottom-quintile small caps — a short-leg-cost illusion. **Verdict: FAILS-OOS.** This earns the memo's "free-data portfolio alpha at our scale is measured-dead" claim and closes the buy-data-vs-stop fork (a) vs (b).
  - Borrow-cost sensitivity (OOS p5 / PF): 0% → +2.55bps/1.37 ; 1.5% → +1.55bps/1.25 ; **5% → −0.78bps/1.006 (FAIL)** ; 10% → −4.12bps/0.74 ; 15% → −7.47bps/0.54.
