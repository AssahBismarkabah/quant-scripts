# "Five Structural Edges" — Extraction Register

**Version:** 0.1 (extraction / registration, 2026-08-09)
**Status:** EXTRACTION — no backtest run yet. 2 of 5 claims already closed elsewhere; 3 new candidates registered awaiting scope + data resolution.
**Classification:** Five independent structural/behavioral claims: PEAD, opening-range breakout, congressional trading, option VRP harvest, Bitcoin MVRV DCA.
**Research spec:** `IA/five-structural-edges-research-spec.md`
**Source:** trading-education transcript (`transcribe.txt`) — same speaker lineage as VWAP-pullback / IVAMR / opening-range-gap. Claims supported by named academic papers and "decades of data"; to be pre-registered and falsified on owned/free data like prior candidates.

## 1. Status by claim

| # | Claim | Status | Where documented |
|---|---|---|---|
| 1 | Earnings Surprise Drift (PEAD) | **REGISTERED — not advanced** (data decision pending: analyst-consensus EPS) | this doc, IA spec §3-4 |
| 2 | Opening Range Breakout ("IVB") | **CLOSED** — same family as ORB, DISCONFIRMED 2026-08-09 | `strategies/opening-range-gap/OPENING_RANGE_GAP.md` |
| 3 | Congressional trading | **REGISTERED — not advanced** (weak prior; free Quiver data) | this doc, IA spec §3-4 |
| 4 | Option harvest / VRP | **CLOSED** — short-vol/VRP family, V1/V2/V3 disconfirmed/ruin 2026-08-08 | `strategies/vol-risk-premium/VOL_RISK_PREMIUM.md`, `V3_TAIL_OVERLAY.md` |
| 5 | Bitcoin MVRV smart DCA | **REGISTERED — not advanced** (different asset class; free on-chain data) | this doc, IA spec §3-4 |

Two claims (ORB, VRP) duplicate families already falsified in this repo and are **not re-run**. This is consistent with the house pattern: marketed high-confidence claims from the same lineage repeatedly fail strict pre-registered tests.

## 2. The three new candidates (extraction)

**1. Earnings Surprise Drift (PEAD).** Positive/negative earnings surprises drift for ~60 days. Mechanism: slow information diffusion, alpha-execution/fractionalized orders (VWOP-style accumulation), short-sale/liquidity constraints. Claim: "4% spread over 60 days in a single stock." **Prior deflated** by independent large-cap evidence (FinLab 2016-2026: +2.75% ann. L/S, IC 0.012; miss-side stronger than beat-side). Needs SUE via historical analyst consensus — the hard data input.

**3. Congressional trading.** Copy powerful committee members. Stock Act 2012 = 45-day disclosure. Claim: Pelosi family "outperforms nearly every hedge fund." **Selection/survivorship risk** (most politicians underperform); the 45-day public lag means any testable alpha is not true insider timing.

**5. Bitcoin MVRV smart DCA.** Use MVRV Z-score (market value / realized value, z-scored by market-cap volatility) to size accumulation — heavy at capitulation, reduce at euphoria. Claim: lower max drawdown vs buy-and-hold. Expected win = **risk reduction**, not necessarily higher CAGR.

## 3. Data reality (confirmed via Tavily, 2026-08-09)

- **PEAD:** prices owned; earnings dates free (Investing.com/SEC 8-K); **historical analyst consensus EPS not free** (FactSet/Capital IQ paid) → the binding constraint. Options: acquire consensus (paid), or use a SUE proxy (actual vs prior-year / event-window surprise proxy).
- **Congressional:** free Quiver Quantitative congress-trades (2016+, ticker/buy-sell/amount/traded date) + InsiderFinance tracker. **Entry must use the filed/reported date** (45-day lag), not the traded date, or the test is look-ahead (gate 6).
- **Bitcoin MVRV:** free Blockchain.com MVRV/realized-value charts + Coin Metrics realized-cap history (2013+).

## 4. Status / Log

- **2026-08-09:** New transcript extracted into this register + IA spec. Tavily confirmed free-data routes for congressional (Quiver) and MVRV (Blockchain.com/Coin Metrics); confirmed PEAD's analyst-consensus gap. ORB/VRP flagged as already-closed. Awaiting reviewer scope + PEAD data decision before any probe.

## 5. Next steps

On reviewer go: pre-register rules + IS/OOS + friction + bootstrap p5 + look-ahead audit for the chosen candidate(s), then scaffold the probe under `research/` and update this doc + spec + README per house pattern. Recommended first candidate: **PEAD** (highest intrinsic merit) once the SUE-data route is chosen.
