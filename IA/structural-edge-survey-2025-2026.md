# 2025-2026 Structural Edge Survey (and testable shortlist)

**Date:** 2026-08-04
**Type:** Research / decision document (forward-looking market-structure survey, not a pre-registered spec)
**Purpose:** Research-first pivot. Survey what structural mechanics and forced flows look like *today* (2025-2026), what institutions are doing, and shortlist what we can **test definitively** with obtainable (free/cheap) data — filtered through the market-edge framework's practical filters (mandate, parameter-robustness, friction, capacity).
**Audience:** self. This informs the *next pre-registered research spec*; it is not an approval to trade and not code.

---

## 1. What this document is not

It does not guess a strategy and jump to code. It applies the institutional process: survey the mechanism landscape with a why, then pick a candidate to research into a pre-registration spec. It also does NOT re-open the proven-dead bucket (vol-fade: measured-marginal; index-rebal: closed; funding-basis: structural; and the free-daily-data structural/flow lane is adjudicated).

---

## 2. What the 2025-2026 market structure looks like (evidence)

### 2.1 Forced flows: buybacks are now the biggest, most persistent demand pool
- US corporate buybacks hit a **record ~$1.1-1.2T in 2025** (Birinyi reach $1T announced by Aug 20; Goldman ~$1.2T, +15% YoY; S&P DJI Q2 ~$235B). All-time high.
- **Top-heavy:** top 20 S&P 500 names = ~50% of authorizations (vs ~44% historical). Tech + financials dominate.
- Companies are forced-ish: open-market buybacks must obey **Rule 10b-18 daily limits** (e.g. <=25% of 4-week ADV per day), giving a **slow, persistent, price-insensitive daily demand** that supports single names near lows (the "buyback put"). Rule 10b5-1 plans are fully scheduled.
- **Regulatory data change (2023):** SEC now requires **daily** repurchase disclosure (Form 10-Q/10-K exhibits; FPI Form F-SR) + 10b5-1 plan adoptions/terminations. This is machine-readable on EDGAR (free). **Caveat:** it is disclosed *quarterly*, so per-day execution is **lagged** — the edge would be about corporate-calendar *predictability* of buyback windows (see JAE 2025 "Equity-based compensation and the timing of share repurchases"), not real-time observation.

### 2.2 Forced flows: 0DTE / dealer gamma hedging (dominant but data-heavy)
- 0DTE options are now **>61% of S&P 500 index option volume** (Numerix, May 2025); expiry every weekday.
- Dealers **must** delta-hedge (buy underlying when short puts, sell when short calls); in the final hours dealer flow can be 20-40% of SPX futures volume; pinning at high-OI strikes; gamma flip regimes.
- **This is the GEX-L2 candidate** we already surveyed. It is real and dominant, but testing a *tradeable* edge needs **intraday OI/flow** data (paid) and the Level-1 friction question already failed. Deferred unless we buy intraday data.

### 2.3 Frictions: T+1 and settlement
- US equities already on **T+1** since May 2024; the transition's one-time operational friction spike has normalized. EU/UK/Swiss T+1 targeted ~Oct 2027 — a *future* transition, not a current US edge.
- No current, persistent, testable settlement friction in US cash equities from T+1 itself.

### 2.4 Scheduled flows: quarter-end / index / monthly rebalance
- Passive is a majority of equity flows (~40% of S&P 500 cap in top 10 names; active-fixed-income ETF dominance). Index reconstitution and quarter-/month-end rebalancing exist and are schedulable — **but this lane is exactly index-rebalancing, which is CLOSED** (single-batch, not persistent). SPX quarterly options (quarter-end settlement) reinforce the quarter-end flow — already covered by the closed candidate.

### 2.5 Data asymmetries / cheap-observable inputs (framework's third pillar)
- **SEC EDGAR** (free): daily buyback tables (10b-18/10b5-1), insider Form 4 filings, 10b5-1 adoption/termination, corporate-action calendars. All parseable with the existing `pdfplumber`/`requests` stack.
- **Corporate-action / spin-off / M&A flows** and **index-calendar prediction** are schedulable from public data.
- The institutional-approach explicitly lists "SEC filing parsing, cleaner tick data, faster alternative-data pipelines" as the data-asymmetry category.

---

## 3. What's actually testable NOW with free/cheap data (shortlist)

Filter applied: real forced/constrained counterparty (why), durability of the mechanic (moat), positive EV after *our* friction, capacity, AND — the binding new constraint — **testable definitively with obtainable (free/cheap) data and enough events to pass the gates that killed the last five.**

| # | Candidate | Mechanism (why) | Counterparty MUST trade | Data (free/cheap?) | Honest prior / risk that killed prior candidates | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Buyback-timing support / "buyback put"** | Companies repurchase on a schedule (10b5-1, post-earnings windows); price-insensitive daily demand supports stock near lows for weeks | Yes — corporate mandate, Rule 10b-18/10b5-1 | **Free**: EDGAR daily buyback exhibits (lagged, quarterly) + 10b5-1 adoption dates (real-time 8-K) | Disclosure lag; effect may already be crowded; "buyback put" literature is mixed (Bonaime et al.); risk of being a momentum-beta confound. **But** identifiable via 10b5-1 plan *signals* (announced in advance) + corporate-calendar regularity | **TESTED - NOT ADVANCED (2026-08-04, bounded)**: 47 program events; primary 20d point positive but insignificant (bootstrap p5<0), drop-best->~0; short horizons underperform index. Full multi-year sample pending, but bounded signal does not justify that spend |
| 2 | **Quarter-end "balance-sheet / window-dressing" + index rebalance re-test on a *different* construction** | Funds window-dress top holdings at quarter end; schedule known | Yes — benchmarked funds | **Free**: calendar (known dates) + daily bars | This is index-rebal's family (closed); priors are that decayed edges don't return | **Testable, weak prior** |
| 3 | **0DTE expiry / dealer-gamma regime (GEX)** | Dealers must delta-hedge daily expiries; gamma state (flip / zero-gamma / walls) predicts the regime | Yes — options market makers | **Free for a daily-regime test**: Cboe delayed-quotes feed provides per-strike OI+gamma+delta for SPY/SPX (verified). **But see Verdict — data cost was never the blocker** | V1 (2023, real chain data) found the intraday gamma regime **non-predictive before costs**: positive regime +0.64 bps gross, negative regime **−5.02 bps gross** (hypothesis directionally wrong/absent at 1-3h). This is a signal failure, not friction/access. Our own reopen condition requires NEW predictive evidence, which the free-data finding does not provide | **CLOSED (V1). Free-data finding (2026-08-04) removes a future cost objection only; it does NOT reopen — signal non-predictive per V1.** |
| 4 | **Insider / 10b5-1 filing reaction** | Insider net buying + 10b5-1 adoptions predict near-term drift | Behavioral | **Free**: EDGAR Form 4 | Well-studied, largely arbitraged (post-2002 SOX); modest and decaying | Testable, weak |
| 5 | **Spin-off / corporate-action drift** | Forced portfolio moves after spin-offs / index deletions | Yes — index funds must sell | **Free**: corporate-action calendars + bars | Niche, low event count per year (the index-rebal disease: too few events) | Testable, low events |

---

## 4. Recommendation (next pre-registered spec)

**Update (2026-08-04): #1 (buyback-timing) has now been TESTED on a bounded sample and did NOT advance** (47 program events, H1 2026: primary 20d point positive but insignificant, bootstrap p5<0, drop-best collapse to ~0; short horizons underperform the index). The data feed works and events are dense (sparsity is not a constraint), but the signal does not demonstrate a tradeable edge after friction vs the index on this bounded sample; the full multi-year spend is not justified on this evidence. See `strategies/buyback-timing/BUYBACK_TIMING.md` and `IA/buyback-timing-research-spec.md`.

With #1 tested-and-not-advanced, the remaining candidates carry weaker priors:
- **#2 (quarter-end / index-rebalance re-test)** is in the already-CLOSED index-rebal family — priors are that decayed edges don't return; not recommended first.
- **#5 (spin-off / corporate-action drift)** is niche with low event count (the index-rebal disease) and higher operational complexity (corporate-action/survivorship data).
- **#4 (insider / 10b5-1 filing reaction)** is well-studied and largely arbitraged (post-SOX); modest, decaying.
- **#3 (GEX / dealer-gamma regime)** is CLOSED from V1: the free-data finding (2026-08-04) proved the data is not paid-walled, but our own V1 results showed the intraday gamma regime is **non-predictive before costs** (positive +0.64 bps gross; negative **−5.02 bps gross**). The free-data point removes a future cost objection only; it does **not** reopen — the reopen condition is new predictive evidence, which we do not have.

**Honest next decision:** the survey's earlier "buy-vs-stop on intraday" framing was partly based on a false premise (that GEX needed paid data) — now corrected: the data is free, but that does not resurrect GEX, because V1's blocker was the signal itself, not access. After #1 (tested, not-advanced) and #3 (closed from V1), the remaining shortlist entries (#2, #4, #5) all carry weak or already-disputed priors. The honest choices now are: **pick one of the weaker-prior free candidates (#2/#4/#5) with eyes open, or deliberately stop the research phase** — there is no strong free-data candidate left unmeasured.

## 5. Explicitly not recommended now

- Not re-opening vol-fade cells, index-rebal, funding-basis, or IVAMR under any name.
- Not #1 (buyback-timing) for a full multi-year build unless a new, materially different sub-hypothesis appears (the bounded evidence does not justify it).
- Not #3 (GEX) — closed from V1 (intraday gamma regime non-predictive before costs); the free-data finding removes a cost objection only, not the signal failure. Do not re-run the same intraday regime.
- Not a blind pre-registration of any candidate without the research pass (why + counterparty + friction + capacity) first.

---

## 6. Status

- **2026-08-04:** Survey written from current web research (Tavily) across forced flows (buybacks, 0DTE/gamma, index/quarter-end), frictions (T+1), and data asymmetries (EDGAR). Shortlist ranked; **#1 buyback/10b5-1 timing recommended as the next research target.**
- **2026-08-04 (later):** #1 researched, implemented, and **tested on a bounded sample — NOT ADVANCED**. The survey's free-data candidates are now all adjudicated (not-advanced or weak-decayed).
- **2026-08-04 (correction):** the "buy-vs-stop on intraday data" fork was partly a **false premise** — research + a live Cboe-API test show the GEX data IS free (Cboe delayed quotes give per-strike gamma+OI). **But reading our own V1 record shows that data cost was never the real blocker:** V1 measured the intraday gamma regime as **non-predictive before costs** (positive +0.64 bps gross, negative −5.02 bps gross). So GEX stays **CLOSED**; the free-data finding removes a cost objection only and does not meet the reopen condition. **Next step: pick a weaker-prior free candidate (#2/#4/#5) with eyes open, or deliberately stop the research phase.**
