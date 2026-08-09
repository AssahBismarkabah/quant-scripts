# "Five Structural Edges" — Research & Extraction Spec

**Status:** Extraction / prioritization — REVIEW (2026-08-09)
**Source:** trading-education transcript (`transcribe.txt`, 14KB) claiming five "structural edges" — repetitive, predictable behaviors "drastically documented by institutional-level academic research" and "persistent over the last decade." Same speaker lineage as the earlier VWAP-pullback / IVAMR / opening-range-gap sources (Robins Cup / CME equity cup / trading-floor workshop). Purpose: capture what the transcript claims, separate already-tested/closed claims from new ones, and record the free-data reality for the actionable candidates — for compact review before any backtest.

---

## 1. The five claimed edges

| # | Edge (name) | Mechanism claimed | Previously tested? |
|---|---|---|---|
| 1 | **Earnings Surprise Drift (PEAD)** | Positive (negative) earnings surprises drift up (down) for up to ~60 days after the announcement; SUE-standardized; "4% spread over 60 days in a single stock." Cites Ball-Brown 1968, Bernard-Thomas 1989, recent ML PEAD paper. | **NO — new candidate** |
| 2 | **Initial Balance / Opening Range Breakout ("IVB")** | First 30-min range; breakout of it predicts rest of session; claims "13.5% upside skew; a 1:1 RR blind skew." Cites Toby Crabel, Barbon/Zarattini opening-range papers. | **YES — DISCONFIRMED as ORB** on NQ (opening-range-gap trio, 2026-08-09). Same family. **Do not re-run.** |
| 3 | **Congressional / politician trading** | Copy the most active powerful committee members; Stock Act 2012 (45-day disclosure). Claims Pelosi family "outperforms nearly every hedge fund." Cites 2011 US House abnormal-return paper, 2025 "Talking Stocks of Democracies." | **NO — new candidate** (weak prior) |
| 4 | **Option premium harvesting / VRP** | Systematic selling of OTM options to capture the volatility risk premium (IV > RV structurally). Cites Carr-Wu 2009, "Why are put options so expensive?" | **YES — CLOSED as short-vol/VRP** (V1/V2/V3, 2026-08-08; V2 naive harvest is ruin +452%/−95% DD/−83% single day, V3 overlay kills edge). Same family, same Carr-Wu paper. **Do not re-run.** |
| 5 | **Bitcoin smart DCA / MVRV Z-score** | Use market-value-to-realized-value Z-score to dynamically size Bitcoin accumulation; buy capitulation, trim euphoria; vs buy-and-hold. Cites Grosjean/Nasman 2026 on-chain cycle papers. | **NO — new candidate** (different asset class) |

**Bottom line:** 2 of 5 (ORB, VRP) are already-tested and closed in this repo. The three genuinely-new candidates are **PEAD**, **Congressional**, and **Bitcoin MVRV**.

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

---

## 4. What we propose to test (recommended) — for review

Of the three new candidates, PEAD is the strongest academically-documented but has a **decision-cost on data** (consensus EPS). Congressional has clean free data but the weakest prior + 45-day lag. MVRV is a different-asset-class relative-timing claim.

Recommendation (pick scope):
1. **PEAD on owned/free data** — highest intrinsic merit;必须先 resolve whether to acquire consensus-EPS history (paid/free scrape) or accept a SUE proxy. Needs a data decision before pre-registration.
2. **Congressional copy-trade** — cleanest free dataset (Quiver), but weak prior; model with **filed-date entry** and a multi-politician basket to avoid Pelosi cherry-picking.
3. **Bitcoin MVRV smart DCA** — different asset class; free data; relative-timing claim (DD reduction), new scaffold.
4. **Skip (already closed):** ORB #2, VRP #4.

House discipline for each, once a candidate is chosen and data secured: **pre-registered rules + IS/OOS + friction + bootstrap p5 + look-ahead audit**, DISCONFIRMED on any gate fail — same protocol as VWAP-pullback / IVAMR / opening-range-gap.

---

## 5. Decision for the reviewer

Pick the test scope and, for PEAD, the data route:
1. **PEAD** — (a) try to source historical analyst consensus free/cheap, or (b) proceed with a SUE proxy (actual vs prior-year, or event-window signed return as surprise proxy).
2. **Congressional** — proceed with Quiver free data, filed-date entries, multi-member basket.
3. **Bitcoin MVRV** — proceed with Blockchain.com/Coin Metrics free realized-cap data.
4. Defer all — extraction-only documentation for now.

No backtest runs until scope + data are resolved and gates pre-registered. This doc is the compact review artifact.
