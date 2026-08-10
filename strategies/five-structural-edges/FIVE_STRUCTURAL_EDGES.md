# "Five Structural Edges" — Extraction Register

**Version:** 0.3 (register updated, 2026-08-10)
**Status:** **5 of 5 claims RESOLVED/CLOSED.** PEAD + Bitcoin MVRV DISCONFIRMED under pre-registered probes; ORB + VRP DISCONFIRMED (duplicate families); Congressional CLOSED (weak prior). No deployable edge from this transcript in this repo.
**Classification:** Five independent structural/behavioral claims: PEAD, opening-range breakout, congressional trading, option VRP harvest, Bitcoin MVRV DCA.
**Research spec:** `IA/five-structural-edges-research-spec.md`
**Source:** trading-education transcript (`transcribe.txt`) — same speaker lineage as VWAP-pullback / IVAMR / opening-range-gap. Claims supported by named academic papers and "decades of data"; to be pre-registered and falsified on owned/free data like prior candidates.

## 1. Status by claim

| # | Claim | Status | Where documented |
|---|---|---|---|
| 1 | Earnings Surprise Drift (PEAD) | **DISCONFIRMED (2026-08-09)** — drift reproduces IS (+2.07%, PF 1.11) but fades OOS (≈0, PF 0.94); no OOS edge | `strategies/pead/PEAD.md`, `IA/pead-research-spec.md` |
| 2 | Opening Range Breakout ("IVB") | **CLOSED** — same family as ORB, DISCONFIRMED 2026-08-09 | `strategies/opening-range-gap/OPENING_RANGE_GAP.md` |
| 3 | Congressional trading | **CLOSED (2026-08-09)** — weak prior, selection/survivorship risk (Pelosi cherry-pick), 45-day lag removes true-insider timing; agrees with decision to not test | this doc, IA spec §2 |
| 4 | Option harvest / VRP | **CLOSED** — short-vol/VRP family, V1/V2/V3 disconfirmed/ruin 2026-08-08 | `strategies/vol-risk-premium/VOL_RISK_PREMIUM.md`, `V3_TAIL_OVERLAY.md` |
| 5 | Bitcoin MVRV smart DCA | **DISCONFIRMED (2026-08-10)** — DD gates pass only on sign (corrected comparison); not reproducible in-sample (IS dynamic −83.7% vs buyhold −84.5% DD with CAGR 76% vs 161%; only OOS 2021-26 shows the benefit −53% vs −77%) | `strategies/bitcoin-mvrv/BITCOIN_MVRV.md`, `IA/bitcoin-mvrv-research-spec.md` |

Two claims (ORB, VRP) duplicate families already falsified in this repo and are **not re-run**. This is consistent with the house pattern: marketed high-confidence claims from the same lineage repeatedly fail strict pre-registered tests. **All five claims from the transcript are now resolved** (PEAD, ORB, VRP, Congressional, Bitcoin MVRV — all closed).

## 2. The three new candidates (extraction)

**1. Earnings Surprise Drift (PEAD).** Positive/negative earnings surprises drift for ~60 days. Mechanism: slow information diffusion, alpha-execution/fractionalized orders (VWOP-style accumulation), short-sale/liquidity constraints. Claim: "4% spread over 60 days in a single stock." **Prior deflated** by independent large-cap evidence (FinLab 2016-2026: +2.75% ann. L/S, IC 0.012; miss-side stronger than beat-side). Needs SUE via historical analyst consensus — the hard data input.

**3. Congressional trading (CLOSED — not tested).** Copy powerful committee members. Stock Act 2012 = 45-day disclosure. Claim: Pelosi family "outperforms nearly every hedge fund." **Selected not to test**: selection/survivorship bias (most politicians underperform; Pelosi is the cherry-picked standout), small sample, and the 45-day public lag means any testable alpha is not true insider timing. Lowest-prior of the set; closed on judgment consistent with the reviewer decision.

**5. Bitcoin MVRV smart DCA.** Use MVRV Z-score (market value / realized value, z-scored by market-cap volatility) to size accumulation — heavy at capitulation, reduce at euphoria. Claim: lower max drawdown vs buy-and-hold. Expected win = **risk reduction**, not necessarily higher CAGR.

## 3. Data reality (confirmed via Tavily, 2026-08-09)

- **PEAD:** prices owned; earnings dates free (Investing.com/SEC 8-K); **historical analyst consensus EPS not cleanly free** (IBES/FactSet/Capital IQ paid) → the binding constraint. Refined route (2026-08-09): **free Kaggle "US Historical Stock Prices With Earnings Data" + FMP** for estimate+actual; standardize historically; **explicitly qualify as analyst-expectation-based surprise, NOT IBES SUE**. Decisive gate: the estimate must be contemporaneous point-in-time BEFORE the announcement (else look-ahead). SEC EDGAR validates the actual-EPS leg.
- **Congressional:** free Quiver Quantitative congress-trades (2016+, ticker/buy-sell/amount/traded date) + InsiderFinance tracker. **Entry must use the filed/reported date** (45-day lag), not the traded date, or the test is look-ahead (gate 6).
- **Bitcoin MVRV:** free Blockchain.com MVRV/realized-value charts + Coin Metrics realized-cap history (2013+).

## 4. Status / Log

- **2026-08-09:** New transcript extracted into this register + IA spec. Tavily confirmed free-data routes for congressional (Quiver) and MVRV (Blockchain.com/Coin Metrics); confirmed PEAD's analyst-consensus gap. PEAD data route refined (free Kaggle+FMP, qualified not-IBES-SUE, point-in-time gate). ORB/VRP flagged as already-closed.
- **2026-08-09 (later):** **PEAD DISCONFIRMED** (drift reproduces IS, fades OOS — see `strategies/pead/PEAD.md`). **Congressional CLOSED** (weak prior, not tested). **Bitcoin MVRV set as the active remaining candidate** — dedicated docs created (`strategies/bitcoin-mvrv/`, `IA/bitcoin-mvrv-research-spec.md`).
- **2026-08-10:** **Bitcoin MVRV DISCONFIRMED** under pre-registered probe (Coin Metrics `CapMVRVCur`, BTC 2013-2026) — DD gates pass only on sign after a comparison-direction fix; the edge is not reproducible in-sample and OOS shows it in one window only. With this, **all five claims are resolved**.

## 5. Next steps

All five structural-edge claims from the transcript are now closed (2 DISCONFIRMED by probes in this repo, 2 duplicate-family DISCONFIRMED, 1 CLOSED on judgment). No further backtests warranted on this family. The register + umbrella + strategy docs + `docs/README.md` reflect the fully-closed state.
