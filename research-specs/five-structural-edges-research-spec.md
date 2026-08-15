# "Five Structural Edges" — Research & Extraction Spec

**Status:** **5 of 5 resolved/closed (2026-08-10).** PEAD + Bitcoin MVRV DISCONFIRMED by pre-registered probes; ORB + VRP DISCONFIRMED (duplicate families); Congressional CLOSED on judgment. No deployable edge from this transcript in this repo.
**Source:** trading-education transcript (`transcribe.txt`, 14KB) claiming five "structural edges" — repetitive, predictable behaviors "drastically documented by institutional-level academic research" and "persistent over the last decade." Same speaker lineage as the earlier VWAP-pullback / IVAMR / opening-range-gap sources (Robins Cup / CME equity cup / trading-floor workshop). Purpose: capture what the transcript claims, separate already-tested/closed claims from new ones, and record the free-data reality for the actionable candidates — for compact review before any backtest.

---

## 1. The five claimed edges

| # | Edge (name) | Mechanism claimed | Previously tested? |
|---|---|---|---|
| 1 | **Earnings Surprise Drift (PEAD)** | Positive (negative) earnings surprises drift up (down) for up to ~60 days after the announcement; SUE-standardized; "4% spread over 60 days in a single stock." Cites Ball-Brown 1968, Bernard-Thomas 1989, recent ML PEAD paper. | **YES — DISCONFIRMED (2026-08-09)** on Kaggle US panel: drift reproduces IS (+2.07%, PF 1.11) but fades OOS (≈0, PF 0.94). See `pead-research-spec.md` §7, `../strategies/pead/PEAD.md`. |
| 2 | **Initial Balance / Opening Range Breakout ("IVB")** | First 30-min range; breakout of it predicts rest of session; claims "13.5% upside skew; a 1:1 RR blind skew." Cites Toby Crabel, Barbon/Zarattini opening-range papers. | **YES — DISCONFIRMED as ORB** on NQ (opening-range-gap trio, 2026-08-09). Same family. **Do not re-run.** |
| 3 | **Congressional / politician trading** | Copy the most active powerful committee members; Stock Act 2012 (45-day disclosure). Claims Pelosi family "outperforms nearly every hedge fund." Cites 2011 US House abnormal-return paper, 2025 "Talking Stocks of Democracies." | **CLOSED (2026-08-09)** — weak prior/selection risk, not tested. **Do not pursue.** |
| 4 | **Option premium harvesting / VRP** | Systematic selling of OTM options to capture the volatility risk premium (IV > RV structurally). Cites Carr-Wu 2009, "Why are put options so expensive?" | **YES — CLOSED as short-vol/VRP** (V1/V2/V3, 2026-08-08; V2 naive harvest is ruin +452%/−95% DD/−83% single day, V3 overlay kills edge). Same family, same Carr-Wu paper. **Do not re-run.** |
| 5 | **Bitcoin smart DCA / MVRV Z-score** | Use market-value-to-realized-value Z-score to dynamically size Bitcoin accumulation; buy capitulation, trim euphoria; vs buy-and-hold. Cites Grosjean/Nasman 2026 on-chain cycle papers. | **YES — DISCONFIRMED (2026-08-10)**: DD gates pass only on sign (corrected comparison); not reproducible in-sample (IS dynamic −83.7% vs buyhold −84.5% DD, CAGR 76% vs 161%; OOS only shows the benefit −53% vs −77%). See `bitcoin-mvrv-research-spec.md` §7, `../strategies/bitcoin-mvrv/BITCOIN_MVRV.md`. |

**Bottom line:** **5 of 5 resolved and closed.** PEAD + Bitcoin MVRV DISCONFIRMED under pre-registered probes; ORB + VRP DISCONFIRMED (duplicate families); Congressional CLOSED on judgment. No deployable edge from this transcript in this repo.

---

## 2. Claimed vs. the honest prior

- **PEAD:** the transcript claims a "4% spread over 60 days in a single stock." Independent recent evidence (FinLab 2016-2026 liquid large-caps, found via Tavily) shows PEAD is **now weak**: only +2.75% annualized long-short and rank IC ~0.012; the *avoid-the-miss* side is far stronger than the *ride-the-beat* side (−1.63% vs +0.34% over 60d). This materially deflates the "single-stock 4% drift" framing and motivates a strict, SUE-based, large-sample test rather than a cherry-picked chart.
- **Congressional:** the speaker highlights Pelosi as the standout — textbook selection/survivorship bias; the same source shows most politicians underperform. The claim's own mechanic (45-day public lag) means any testable benefit is not true insider timing.
- **Bitcoin MVRV:** a legitimate relative-allocation (timing-a-better-DCA) claim; the expected win is lower max drawdown vs buy-and-hold, not necessarily higher CAGR. Different data ecosystem (on-chain) and daily/swing, not intraday.

---

## 3. Data reality (confirmed via Tavily, 2026-08-09)

| Candidate | Data needed | Free source available? | Reality |
|---|---|---|---|
| **PEAD** | Stock prices (HAVE: SPY/IWM + many per-ticker daily bars in caches) | Prices: yes (owned). **Earnings dates: yes (Investing.com / SEC 8-K scrape)**. **Analyst consensus EPS (to compute SUE): NO clean free long-history source** — FactSet/Capital IQ paid. | Partial. The *hard* input is point-in-time historical analyst consensus. Without it, SUE is not computable faithfully; a crude actual-vs-prior-year surprise proxy is possible but weaker. |
| **Congressional** | Transaction-level congress trades with traded + filed/reported dates | **YES — Quiver Quantitative congress-trades** (2016+, ticker/buy-sell/amount/traded date), free visitor export / API ($30/mo). InsiderFinance tracker also free. | Good. Critical modeling rule: entry uses the **filed/reported date** (45-day lag), NOT the traded date — else look-ahead. |
| **Bitcoin MVRV** | BTC price + realized cap → MVRV Z-score | **YES — Blockchain.com chart (MVRV/RV series), Coin Metrics** historical realized-cap/MVRV. | Good, free. Longer history 2013+ feasible. |

### PEAD data route — refined (2026-08-09, cross-checked with data research)

The binding constraint is **point-in-time analyst consensus EPS**. Ranked sources (best→worst for this repo):

| Source | History | Consensus | Free? | Suitability |
|---|---|---|---|---|
| IBES / WRDS | 1975+ | Excellent | No (institutional) | Gold standard, not open |
| Estimize | 2010+ | Excellent | Institutional access only | Very good but not open |
| **FMP** (Financial Modeling Prep) | long | Yes | **Limited free tier** (surprise/consensus behind premium) | Good — worth testing account limits |
| **Kaggle "US Historical Stock Prices With Earnings Data"** | ~20 yrs | estimate+actual | **YES** | Promising — needs validation |
| SEC EDGAR (XBRL) | 1994+ | No consensus | **YES** | Great for **actual** EPS leg only |

**Agreed approach (matches house discipline):** build an **analyst-expectation-based earnings surprise** from the free **Kaggle + FMP** combo (NOT IBES SUE), **standardize historically** to a SUE-like measure, and **explicitly qualify** the result as "analyst-expectation-based surprise from public estimates, not IBES SUE." The decisive methodological gate (mirrors gate-6 look-ahead): **the estimate must be the contemporaneous consensus available BEFORE the announcement date** — a retrospectively-recorded estimate is unusable. SEC EDGAR supplies the actual-EPS leg for validation.

---

## 4. Current state — all five resolved

Of the five claims, **all five are now resolved**: PEAD + Bitcoin MVRV DISCONFIRMED under pre-registered probes; ORB + VRP DISCONFIRMED (duplicate families); Congressional CLOSED on judgment.

**Congressional (#3) decided CLOSED (2026-08-09):** low prior (selection/survivorship — Pelosi is the highlighted standout, most politicians underperform), small sample, and the 45-day public lag means any testable benefit is not true insider timing. Not pursued.

**Bitcoin MVRV (#5) DISCONFIRMED (2026-08-10):** pre-registered probe on Coin Metrics `CapMVRVCur` (BTC 2013-2026). DD gates pass only on sign after a comparison-direction correction; the edge is not reproducible in-sample (IS dynamic −83.7% vs buyhold −84.5% DD with CAGR 76% vs 161%; only the single OOS window 2021-26 shows the benefit, −53% vs −77%). See `bitcoin-mvrv-research-spec.md` §7 and `../strategies/bitcoin-mvrv/BITCOIN_MVRV.md`.

House discipline applied throughout: **pre-registered rules + IS/OOS + friction + look-ahead audit**, same protocol as PEAD/VWAP-pullback / IVAMR / opening-range-gap.

---

## 5. Decision for the reviewer

All five structural-edge claims from the transcript are **closed**:
- PEAD — DISCONFIRMED (probe)
- ORB/IVB — DISCONFIRMED (duplicate family)
- VRP — closed (duplicate family, ruin)
- Congressional — closed on judgment
- Bitcoin MVRV — DISCONFIRMED (probe)

No further backtests are warranted on this family. Nothing remains open; all docs + register reflect the fully-closed state.

