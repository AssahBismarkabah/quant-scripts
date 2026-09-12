# Small-Trader Advantage Audit (Phase B)

**Executive Summary:** We define the goal as finding *specific market mechanisms* where a small, retail quant trader has a natural edge. This requires identifying **who** is constrained to trade, **why** mispricing persists, and what **observable signal** precedes the price pressure. We survey candidate environments (small‑cap equities, niche ETFs, microcaps, corporate events, etc.) focusing on cases where large institutions are limited by size, regulations, or structure. We derive 30 concrete mechanism hypotheses (each specifying participant, constraint, observable, directional effect, horizon, capacity). We then whittle these to the ~5 most credible by checking data availability, execution feasibility, friction and size limits, and falsifiability. For those top candidates, we outline pre-registered tests (signals, trades, costs, OOS split, failure criteria). Our recommendation is to proceed with disciplined testing of the strongest hypotheses **only if** the required data or execution is truly available; otherwise to acknowledge that, under current capabilities, systematic discovery is at a low-probability frontier.  

## 1. Research Objective and Methodology 

We change the question from “Which price indicator gives alpha?” to **“Where can being a small, flexible trader create an *economic* advantage?”**.  Phase B is a *mechanism audit*: each hypothesis must specify a constrained participant and explain **why** that constraint leads to a tradeable price distortion.  In particular, every candidate mechanism must clear the following gates (before any backtest):

- **Mechanism (Constraint):** *Who* is forced or constrained to trade (mandate, holding requirement, operational rule, etc.)? Why does this create predictable buying or selling pressure?
- **Observable:** Is the constraint signaled by a public, timestamped input available before the trade (e.g. regulatory filing, announced corporate action, scheduled rebalancing, etc.)?
- **Persistence (No Immediate Arbitrage):** Why won’t this distortion be instantly arbitraged away? (Limits on capacity, information delays, fragmented markets, calendar/legal constraints, etc.)
- **Execution:** Can a retail trader (e.g. via IBKR) actually trade the instrument at the needed time and size? Who is the counterparty taking the other side, and why would they accept the disadvantageous price?
- **Friction & Capacity:** What are the realistic costs (bid-ask, slippage, fees, borrow, financing)?  How much capital can we deploy before the opportunity is exhausted (market impact or limited supply)?
- **Sample Sufficiency:** Is there a sufficiently large number of independent events for out-of-sample testing?

If any gate fails, the hypothesis is rejected.  Only after passing all gates do we **pre-register** a detailed test (signal definition, trading rule, costs, OOS split).  

*This mechanistic discipline avoids blind indicator-mining. We prioritize **primary/official sources** and academic studies wherever possible to verify each component of a hypothesis.* 

## 2. Environments Favoring Small Traders

We survey classes of markets where **large institutions are hindered by size or regulation**, potentially leaving room for a nimble trader. For each environment we discuss why institutions may be disadvantaged, plausible mispricing mechanisms, required observables, execution path, friction, and sample size. A summary comparison (observability, execution, horizon, capacity, data, risk) is given in Table 1 and Figure 1 below. 

- **Small / Microcap Equities:**  *Disadvantage:* Very low liquidity, sparse analyst/institutional coverage.  Many microcap stocks trade <$1M/day; large funds cannot easily build positions without moving the market. *Mechanisms:* Misvalued microcaps, momentum or mean-reversion in tiny stocks, or flows from required portfolio rebalancing in tiny index constituents. *Observables:* Public data on index reconstitutions (e.g. Russell 2000 changes), filings (EDGAR), or analyst downgrades. *Execution:* Stocks are accessible via IBKR, but beware wide spreads and thin depth.  *Friction:* Bid-ask spreads often tens of basis points; market impact can be severe (OSAM notes a $5M trade in illiquid quintile costs ~2.8%). For a $10k trade, expected slippage may be only a few bps, but must be modeled. *Sample:* Thousands of microcaps exist, but true corporate events are infrequent per stock. Testing would require aggregating many tickers or using multi-year history.

- **Niche ETFs / ETPs:**  *Disadvantage:* Many ETFs (especially thematic or frontier-market funds) have small AUM and few Authorized Participants, so arbitrage can be sluggish.  A typical niche ETF might have *median* assets ~$87M, so even institutional owners are minor; market making can be thin. *Mechanisms:*  Deviation of ETF price from NAV when underlying trades infrequently, or predictable flows from reconstitution of specialized indexes. *Observables:*  ETF portfolio holdings (some disclosures delayed), index membership changes, or large market flows (e.g. flows into/out of commodity ETFs when inventories updated). *Execution:*  ETFs trade on exchanges via brokers (IBKR); liquidity often much better than underlying basket, but spreads can be large in stress.  *Friction:*  ETFs have management fees (0–1%), bid-ask spreads (especially for small funds), plus tracking error. Capacity is typically the fund’s ADV (often <$10M/day), so large players are limited. *Sample:*  Many ETFs exist (hundreds of “smart beta” or niche products). Quarterly rebalances (indices and fund holdings) provide repeatable events.

- **Obscure Futures Markets:**  *Disadvantage:* Some futures (e.g. exotic currency, interest-rate, or commodity contracts) have very low volume outside major centers. Large houses focus on main contracts (ES, GC, etc.); others see minimal flow. *Mechanisms:*  Price pressure when, say, an institutional hedger must use an obscure contract for local needs (e.g. currency futures, exotic commodity). *Observables:*  Published schedule of deliverable contracts, central bank interventions, or trade-able indices (e.g. futures settlement dates). *Execution:*  IBKR offers CME and some global futures, but liquidity may be scant and contract specs may have large min sizes. *Friction:*  Wide bid-ask spreads, potential for gapping if markets are closed. Capacity is small – maybe a few contracts without moving price. *Sample:* Many futures have daily data going back decades, but true constrained-flow episodes might be rare (e.g. monthly central-bank announcements). 

- **International Microcaps / Frontier Markets:**  *Disadvantage:*  Smaller foreign markets (EM/MENA/Asia) often have limited institutional participation, capital controls, and lower electronic trading capability. *Mechanisms:*  Local index fund rebalances, cross-border flow disconnects, or regulatory rules (e.g. foreign ownership limits) that create directional pressure. *Observables:*  Local stock exchange announcements, central bank policy, or index reconstitution lists. *Execution:*  Through IBKR via global exchanges or ADRs, but some stocks may only trade at odd hours or with high commissions. *Friction:*  High transaction costs (STT taxes, wide spreads), currency conversion costs, and settlement delays. *Sample:* Numerous countries to aggregate, but each with sporadic events (often quarterly or semiannual fiscal announcements).

- **Corporate Actions & Special Situations:**  *Disadvantage:*  Complex events (spin-offs, M&A, buybacks, tender offers, delistings) often require specialized knowledge or entail trading restrictions. Big funds may abstain from tiny secondary listings or liquidity drains. *Mechanisms:*  Well-known “spin-off effect” – separating a division typically unlocks value.  Or “ex-dividend drift” where stock does not drop fully by dividend amount (several studies document this anomaly). *Observables:*  SEC filings (Form 10, F5, F4 for M&A; Form 8-K for dividends); index provider announcements of spin-offs. *Execution:*  Trades must often be placed on event dates (ex-dates, record dates) via the normal market, or via forward contracts (e.g. for cash-settled spin-offs). *Friction:*  Some events entail special settlement (e.g. cash vs. stock settlement), tax considerations, or lock-ups. Capacity is usually very small (only the float of the spin-off plus existing shares). *Sample:* A few dozen spin-offs or large buybacks occur per year; ex-dividends happen weekly. Abundance of events is a mix of frequent (dividends) and sparse (spin-offs).

- **Operationally Inconvenient Markets:**  *Disadvantage:*  Certain markets are structurally awkward: e.g. evening/overnight sessions, non-standard auctions, or venues requiring heavy documentation (OTC brokerages, closed-end funds). Large firms avoid trivial-size trades or complex access. *Mechanisms:*  Mispricing in closing/opening auctions (due to imbalances) or stale prices in thinly-traded segments (e.g. municipal bonds, private equities ETFs). *Observables:*  Auction imbalance prints, or lists of scheduled large auctions (e.g. Fed/Treasury debt issuances). *Execution:*  Auctions often allow brokers to submit interest; retail typically can use limit orders around open/close. *Friction:*  Risk of partial fills or failed auctions; unusual trading hours. *Sample:* Regular daily auctions (e.g. stock market close), plus scheduled events (e.g. debt auctions). 

- **Long-Horizon Anomalies:**  *Disadvantage:*  Many known anomalies (momentum, reversal, seasonality) require holding positions for weeks–months. Large institutions may rebalance on fixed schedules or have performance constraints, whereas a small trader can hold out longer. *Mechanisms:*  Classic factor effects (12-month momentum, value premium) in under-followed segments. *Observables:*  Quantifiable factors (value ratios, past returns) available in public data. *Execution:*  Standard equity trades via IBKR. *Friction:* Spread/slippage manageable over long horizon; overnight risks. *Sample:* Nearly unlimited – factors can be tested on decades of daily data across universes. 

- **Cross-Sectional Relative-Value Universes:**  *Disadvantage:*  Strategies comparing one asset to another (e.g. pairs, spread trading, sector rotation) are often arbitraged out by quant firms; but specific spreads might be too low-volume for them. *Mechanisms:*  E.g. a small fixed-income basis trade across country bonds, or stock/ETF pair that is thinly linked. *Observables:*  Public prices and indices; market microstructure data. *Execution:*  Execution may involve simultaneous trades (e.g. buy one, short another), which can be done in retail accounts if borrowing is available. *Friction:* Complexity of multi-leg orders; financing/borrow costs for shorts. *Sample:* Varies widely (some pairs trade hourly, some only daily).

**Table 1.** *Comparison of candidate environments for small-trader advantage.* (Observability = ease of getting timely data; Execution = retail execution feasibility; Horizon = typical duration of expected anomaly; Capacity = relative size before opportunity closes; Data = availability of free public data; Risk = legal/regulatory complexity.) We rate each qualitatively (High/Med/Low):  

| Environment           | Observability | Execution | Horizon     | Capacity   | Data        | Regulatory Risk |
|-----------------------|:-------------:|:---------:|:-----------:|:----------:|:-----------:|:----------------|
| Small/Micro Equities  | Medium (moderate filings)     | Medium (stocks via IBKR) | Short–Medium (days-weeks) | Low–Med (small market cap) | Free (pricedata via Yahoo/IB) | Low (exchange-traded) |
| Niche ETFs/ETPs       | Medium (index changes) | High (ETF via IBKR) | Short (intraday to days) | Low (min creation unit)    | Free (ETF data public) | Medium (some tax/structural) |
| Obscure Futures       | Low (few signals) | Low (few brokers offer) | Medium (overnight flow)  | Low (tiny open interest)  | Free (CME releases)  | High (OTC rules)    |
| Intl. Microcaps       | Low (foreign info)  | Low (access via ADRs)  | Medium (news-based) | Low (capital controls)   | Mixed (public but fragmented) | High (foreign laws) |
| Corporate Actions     | High (filings) | High (stock trading) | Medium–Long (days–months) | Low (event-driven) | Free (EDGAR, exchanges) | Medium (SEC rules) |
| Operational Markets   | Medium (auction reports) | Medium (timing risk) | Short (auction cycles)  | Low (special participation) | Free (auction data) | Medium (market rules) |
| Long-Horizon Anomalies| High (factor data)   | High (normal trading) | Long (months) | Medium (tiltable exposure) | Free (factor data) | Low (well-known strategies) |
| Cross-Sectional      | High (prices) | High (standard trades) | Long (holding periods) | Medium (depends on spread) | Free | Medium (borrow, margin) |

 *Figure 1: Small‑cap equity inefficiency. OSAM research shows that U.S. large caps have ~27 analysts (blue bars) whereas the typical small cap has only ~6 (40% have ≤3, 20% none). This lack of coverage (and low liquidity) in microcaps suggests structural inefficiency that small traders might exploit. (Chart source: OSAM 2015.)*  

## 3. Candidate Mechanism Hypotheses (30 one-line ideas)

Below are 30 concrete hypotheses phrased as “Mechanism (Participant – Constraint – Observable – Effect – Horizon – Cap)”.  Each is a *specific* edge prospect.  (We mark in [brackets] which environment(s) they belong to.)

| ID  | Mechanism Hypothesis                                                                                          |
|-----|---------------------------------------------------------------------------------------------------------------|
| B1  | **Microcap No-Analyst Reversal:**  Many U.S. microcaps (Participant: microcap stock) have no analyst coverage and experience post-selloff mean-reversion (Constraint: price shock lasts days). Observable: cluster of down-move. Pressure: bounce up over ~5–20 trading days. Cap: ~$10k orders each. [Small Equities] |
| B2  | **Index Inclusion Demand:**  A small fund tracking an index must buy newly included small-cap stocks (Constraint: mandate buys at next open). Observable: index reconstitution announcement date. Pressure: price rise in target stock on inclusion day. Horizon: 1–3 days. Cap: ~$100k per trade. [Small Equities] |
| B3  | **Dirty Float Arbitrage:**  A low-float stock subject to public buyout offer (Constraint: mandatory tender). Observable: filing of tender offer (e.g. SEC S-4). Pressure: remaining float sells to arbitrageur, pushing price to offer. Horizon: days. Cap: float size (~$M). [Small Equities] |
| B4  | **Thin-Index Sell-off:**  An index-tracking ETF must sell a constituency stock after it’s deleted (Constraint: fund flows). Observable: index provider delete notice. Pressure: price drop leading up to rebalancing date. Horizon: days. Cap: leftover ETF trading volume. [Small Equities] |
| B5  | **Niche-ETF Premium:**  A thematic ETF (Participant: small ETF) trades at a discount because APs are few (Constraint: creation/redemption lags). Observable: NAV data divergence (some ETPs publish indicative NAV). Pressure: ETF price drifts toward NAV over days. Horizon: ~1–5 days. Cap: few % of ETF AUM (<$1M). [Niche ETFs] |
| B6  | **Commodity-ETF Rebalance:**  A commodity ETP must roll futures (Constraint: monthly futures roll). Observable: ETP holding disclosure or roll schedule. Pressure: small price jumps near roll date. Horizon: 1–3 days. Cap: few contracts. [Niche ETFs] |
| B7  | **Frontier-Market Premium:**  An emerging-market country ETF goes stale (Constraint: market closed or circuit). Observable: news-based price gap. Pressure: gap fill when market opens. Horizon: overnight. Cap: small (frontier ETF AUM). [Niche ETFs] |
| B8  | **Junk-ETF Discount:**  Junk-bond ETF trades cheap as underlying credit sells (Constraint: fund mandate sells fallen bonds). Observable: bond downgrade news. Pressure: ETF price falls and then recovers. Horizon: weeks. Cap: limited by ETF liquidity. [Niche ETFs] |
| B9  | **Exotic-FX Futures Mispricing:**  A thinly-traded currency futures contract must reflect central bank action (Constraint: known policy). Observable: CB announcement schedule. Pressure: futures price jumps on announcement. Horizon: minutes-hours. Cap: 1–5 contracts. [Obscure Futures] |
| B10 | **Local-Rate Futures Flow:**  A bank must trade local-bond futures due to funding (Constraint: daily cash needs). Observable: published funding needs (rare). Pressure: predictable buys/sells each morning. Horizon: intraday. Cap: limited by contract open interest. [Obscure Futures] |
| B11 | **ChiNext/MICEX Overreaction:**  A foreign stock listed only on a minor exchange (Participant: microcap ADR) lags price of major market counterpart. Observable: US/China market open. Pressure: small arbitrage trades when spreads widen. Horizon: hours. Cap: small ADR float. [Intl Microcaps] |
| B12 | **China Stock Connect Delay:**  A mainland China share’s Connect quota reopens (Constraint: quota rules). Observable: quota announcement (SSE website). Pressure: sudden buying/selling. Horizon: days. Cap: small (quota-limited flow). [Intl Microcaps] |
| B13 | **Emerging-Index Rebalance:**  MSCI or FTSE periodically adds a frontier stock, forcing fund flows. Observable: MSCI announcement date. Pressure: 1–2 days of buying pressure. Horizon: 1–3 days. Cap: few $M. [Intl Microcaps] |
| B14 | **Quarterly Dividend Drift:** Stocks paying dividend see smaller-than-expected drop (Constraint: tax-loss selling dislocations). Observable: announced ex-dividend date. Pressure: drift upward over 5–15 days post ex-date. Horizon: 10 days. Cap: maybe 1–5% of float. [Corp Actions] |
| B15 | **Spin-Off Release:** A spun-off subsidiary’s price is under-valued (Constraint: initial supply from parent issuance). Observable: SEC form 10 (distribution of new ticker). Pressure: post-distribution abnormal return (empirically positive). Horizon: 3–6 months. Cap: float of new shares. [Corp Actions] |
| B16 | **Tender Offer Retreat:** After a buyout offer withdrawal, holders may sell (Constraint: mandatory tender drop-out). Observable: news of withdrawal. Pressure: continued selling pressure. Horizon: days–weeks. Cap: remaining float. [Corp Actions] |
| B17 | **Index Reconstitution Peak-End:**  Stock returns spike at month-end due to window-dressing (Constraint: funds must hold benchmarks). Observable: known index membership. Pressure: buying in last days of quarter. Horizon: 2–5 days (quarter-end). Cap: small fraction of turnover. [Operational Markets] |
| B18 | **Closing Auction Imbalance:** On slow stocks, the closing auction often has a one-sided imbalance. Observable: published imbalance file (exchanges publish auction imbalances). Pressure: next-minute price jump. Horizon: 1 minute after close. Cap: small lots (max allowable auction volume). [Operational Markets] |
| B19 | **Open Auction Gap:** Some markets (e.g. Europe) have opening crosses that can gap. Observable: overnight news or futures vs index. Pressure: predictable jump at open. Horizon: first minute’s price move. Cap: limited by first-minute volume. [Operational Markets] |
| B20 | **January Effect:** Small stocks tend to outperform in January (Constraint: tax-loss trading, window dressing). Observable: calendar date. Pressure: drift upward in January. Horizon: 1 month. Cap: small ($10–50k per stock). [Long Anomalies] |
| B21 | **Momentum-Fading:** Stocks with huge intraday runs often mean-revert by next week (Constraint: retail herd sells winners quickly). Observable: large intraday jump (>5%). Pressure: decline over 1–3 days. Horizon: 3 days. Cap: fraction of recent volume. [Long Anomalies] |
| B22 | **Sector Rotation:** When a macro shock happens, some sectors oversell (Constraint: slow reallocation by big funds). Observable: macro announcement. Pressure: tradeable bounce in oversold sector. Horizon: 1–2 weeks. Cap: moderate. [Long Anomalies] |
| B23 | **Microcap Value Factor:** The cheapest decile of microcap stocks (Participant: value portfolio) outperforms the richest (Constraint: limited shorting by institutions). Observable: book/price data. Pressure: value stocks rise over 6–12 months. Horizon: 6 months. Cap: maybe $100k per basket. [Cross-Sectional] |
| B24 | **Microcap Momentum Factor:** High-momentum microcaps continue to run (Constraint: lack of short sellers). Observable: past 6-month returns. Pressure: continued outperformance for next 3 months. Horizon: 3 months. Cap: ~$50k. [Cross-Sectional] |
| B25 | **Forex Carry Spread:** Currencies with highest carry sometimes overshoot (Constraint: central bank hedge necessity). Observable: published interest rates. Pressure: currency return reversion over days. Horizon: 7–30 days. Cap: limited by account size. [Cross-Sectional] |
| B26 | **Commodity Basis (Backwardation):** Futures curve shapes signal returns (Constraint: storage/roll costs). Observable: futures term structure. Pressure: price drift predicted by futures slope over ~1 month. Horizon: 1 month. Cap: number of contracts. [Cross-Sectional] |
| B27 | **EDGAR Filing Drift:** After a quarterly 10-Q filing, small firms have predictable drift (Constraint: institutional delay in reacting to news). Observable: 10-Q date/time. Pressure: measured drift (up or down) over 3 trading days post-file. Horizon: 3 days. Cap: small fraction of volume. [Cross-Sectional] |
| B28 | **Exchange Change Pressure:** A stock moving into a major index (e.g. S&P 400 midcap) gets forced buying by index funds. Observable: index committee announcement. Pressure: pre-announcement run-up and buying on effective date. Horizon: 1–3 days. Cap: index flow size (~$few 100M). [Operational Markets] |
| B29 | **Retail Sector Sentiment:** Sectors popular with retail (e.g. meme stocks) overreact intra-day. Observable: social media buzz. Pressure: mean-reversion the next day. Horizon: 1–2 days. Cap: small (retail-sized). [Operational Markets] |
| B30 | **Liquidity Corridor Unwind:** Illiquid penny stocks sometimes run up then crash (Constraint: small float mania). Observable: jump in volume on pink sheets. Pressure: collapse within 1–5 days. Horizon: 3 days. Cap: a few thousand shares. [Small Equities] |

*(IDs B1–B30 list example hypotheses by environment. Each must now face the Phase B audit.)*  

## 4. Top 5 Feasibility Audits

We select five of the above as most promising and examine them in detail. For each, we outline:

- **Primary-source evidence:**  Official data or literature confirming the mechanism.
- **Data requirements:**  Which signals and prices (free vs paid) are needed.
- **Execution model:**  How to trade (entry, exit, order type), sizing, and estimated average half-spread (IS bps).
- **Capacity:**  Rough capital scale before slippage erodes returns.
- **Falsification tests:**  What would disprove the hypothesis (e.g. no effect OOS, insufficient edge vs cost).

### Hypothesis B2: Index Inclusion Demand (Small/Mid Equities)  
**Mechanism:** A broad index (e.g. Russell 2000 or S&P 400) announces that a stock will be **added** to the index as of a future date. Index funds must buy that stock, inducing a short-term rally. Retail traders could front-run this expected flow by buying just before the effective date.  
**Evidence:**  Index providers (FTSE/Russell/S&P) publish reconstitution announcements ~1–2 months in advance. Academic studies show additions often outperform in the days after inclusion (e.g. *UT Dallas Review* finds ~10bp/day effects).  For example, Wurgler and Zhuravskaya (2002) document index inclusion effects.  This is an established primary source: index committee press releases.  
**Observable:** The **announcement date** of the inclusion (from index websites or SEC 8-K of companies noting index changes). Also *Siblis Research* and others list impending index changes. This is public and timestamped (dates of press release).  
**Execution:**  On the effective addition date (or shortly before), buy the stock via IBKR at market or limit order.  Exit after the short-lived premium decays (typically 1–3 days after add).  Use a limit order at ask; expect to pay ~1–3 bps for an ordinary small/midcap order. Slippage: we assume participating at 10–20% of daily volume; e.g. if ADV = $10M, a $50k trade might move price ~5–10 bps.  
**Capacity:**  Indexed flows may be large (tens of millions), but as a small trader we only trade a tiny fraction.  This strategy scales up only to maybe $100k–$500k per position before our own impact hits 1–2%.  
**Falsification:**  If backtests (with realistic costs) show no positive post-inclusion return out-of-sample, we abandon.  Also, if an analysis shows enough existing arbitrage (e.g. APs already pre-buy) negating the edge, we stop.  We would require significance in 1–4 independent events.  

### Hypothesis B5: Niche-ETF Premium (Thin ETFs)  
**Mechanism:** Certain small, thematic ETFs trade persistently at a **NAV discount** because Authorized Participants (APs) are few, so arbitrage is slow. If we detect this (e.g. ETF price below indicative NAV by X%), we buy the ETF shares anticipating mean-reversion as APs step in or fund adjusts holdings.  
**Evidence:**  Financial press and FINRA notes that many ETFs have “efficient in-kind arbitrage,” but niche/synthetic funds can trade off NAV.  When discounts widen (e.g. >2–3%), ETF issuers may trigger redemption window. No single academic source, but SEC disclosures (e.g. small-allotment redemption rules) show retail can redeem in limited cases. Also, websites like ETF.com track premiums.  
**Observable:**  Real-time ETF price vs NAV. NAV may only be published end-of-day or every 15s for some funds (Cboe BZX “XBTO” data). We need either live NAV feeds or a high-frequency estimate of NAV (using basket quotes). We can approximate NAV using daily holdings (some ETFs disclose each day) and intraday underlying prices (IBKR API or Yahoo may have index price).  
**Execution:**  Trade the ETF on exchange via marketable limit order; frequently small ETFs have tiny spreads (0.1–0.5%). Expect a round-trip cost ~0.5–1.0% if we buy on wide discount. We hold till either NAV gap closes or a redemption is triggered (likely days to a week).  
**Capacity:**  Limited by ETF daily volume and creation unit size. For a ~$100M AUM ETF, maybe $100k trades per day are fine. Doing more than 1% of ADV could move the ETF price.  
**Falsification:**  We simulate historical scenarios of NAV discounts. If, after realistic 0.5% cost, the average profit is ≤0, drop it. Also test if the discount narrows only due to market moves, not execution. If all free-data NAV signals are stale, it fails observability (UNVERIFIABLE).  

### Hypothesis B15: Spin-Off Release (Corporate Actions)  
**Mechanism:** When a large company spins off a division, the new independent stock often **outperforms** post-spin (conglomerate discount). If small shareholders take newly-issued shares and hold them, they benefit from this drift. Large institutions often are restricted in selling the parent’s shares immediately (lock-ups) or slow to revalue.  
**Evidence:**  “Substantial scientific evidence confirms spin-offs achieve above-average returns”.  Historical data (Ikenberry 1995 etc.) shows spin-offs yield significant excess returns in months after distribution. Primary sources: SEC Form 10 filings detail spin-off terms and dates. S&P publishes spin-off lists (e.g. “spin-off candidates”).  
**Observable:**  SEC filings announce the spin-off and distribution date. We can scrape EDGAR (free) or Yahoo Finance corporate actions for spin-off info. Also, the effective date is on the prospectus.  
**Execution:**  On distribution date, we will have received stock automatically (if we held parent). But as a strategy, we must ensure we own parent pre-distribution (if doing buy-hold) or buy the new stock after listing. Then **hold 3–6 months**. Use limit orders to reduce spread cost (these can be thin; assume ~0.2–0.5% bid-ask).  
**Capacity:**  Very small – only shareholders of the parent get spin-off shares. This strategy is essentially buy-and-hold of a very small float. $10k orders on a micro spin-off could move price.  
**Falsification:**  We require multiple OOS spin-off examples to show consistent positive returns net of a realistic cost (e.g. 50bps). If any controlled backtest shows no alpha, or if spin-off yields are fully explained by market moves, discard.  Also check that the parent needed to trade at unnatural prices (if not, hypothesis fails).  

### Hypothesis B23: Microcap Value Factor (Cross-Section)  
**Mechanism:** The classic value factor (buy low P/B, sell high P/B) is **much stronger in microcaps** than large caps. The “spread” between cheap and expensive microcaps can be double that of large cap. Institutions struggle to short the expensive small caps (borrow issues), so a long-only value basket in microcaps might outperform.  
**Evidence:**  OSAM found the cheapest decile of microcaps outperformed the most expensive decile by **28.2% annualized**. This is a back-of-envelope signal of a strong effect, though it was a long-short spread. There’s academic literature on stronger small-stock value premium.  
**Observable:**  Public fundamentals (Price, Book, or other value ratios). We can compute a daily or monthly microcap value rank universe using IBKR or free data (Yahoo/AlphaVantage). Constituents (microcap list) can be built by filtering market cap via public data (e.g. finviz lists).  
**Execution:**  Every month, buy portfolio of cheapest microcaps (long basket of 50–100 names) and hold 3–6 months; avoid shorting the expensive side (do long-only strategy). Use limit orders spread out to avoid volatility spikes. Assume cost: microcaps average half-spread ~0.2–0.5%; slippage ~0.05% per day if held short.  
**Capacity:**  Very low – microcap float is tiny. Even $50k per position in a $100M cap stock (0.05% of market) might move price 0.1%. Probably practical up to ~$500k total capital (exposure) across the basket.  
**Falsification:**  If we backtest this long-only microcap value strategy with point-in-time data, realistic costs and it underperforms a benchmark (or is not stable OOS), drop it.  Test robustness: does it survive slight delays or sub-sampling of the universe? If not, it fails.  

### Hypothesis B28: Exchange Change Pressure (Operational)  
**Mechanism:** When a company **upgrades exchanges** (e.g. from NYSE American to Nasdaq), index inclusion may follow (e.g. MSCI, S&P), causing flows. Also, some funds can only hold NYSE main board stocks, forcing them to buy on listing change. *Mini-case:* a stock moving from the Canadian TSX to NYSE sees renewed US demand.  
**Evidence:**  Not heavily studied in literature, but indices publish new listings. Exchange notices (e.g. SEC Form 8-A or listing announcements) are primary data. Anecdotes: smaller stocks often get reclassified.  
**Observable:**  Exchange listing change announcement (company press release, SEC Form 8-A). Also watch index provider changes following a move.  
**Execution:**  Buy the stock on the listing-change effective date (or just prior) via IBKR. Exit after any post-listing run-up decays (say 1–2 weeks). Use market limit, cost ~0.5% round-trip.  
**Capacity:**  Size is miniscule – small stock float plus limited index fund AUM. Likely <$100k per trade without influence.  
**Falsification:**  Test all historical listing-change events (if ≥5 exist) for abnormal returns. If no edge appears net of costs, reject. If backtesting data shows heterogeneous effects, drop.  

## 5. Pre-Registration of Tests

From the above, the most feasible (given data and execution) appear to be: B2 (index inclusion), B5 (ETF premium), B15 (spin-off), B23 (microcap value), and possibly B14 (dividend drift) or B20 (January effect).  We will **choose up to 5** to preregister. Each test specification (one per hypothesis) will be pre-defined as follows:

```
**Hypothesis [ID]:** [One-line mechanism summary from above]. 

**Observable Signal:** [Exact data source and timestamp]. 
**Prediction:** [E.g. “Stock will rise by X% in H days after signal” or “ETF NAV gap will revert”]. 
**Entry Rule:** [E.g. “Buy at market (or limit) on next open after signal”]. 
**Exit Rule:** [E.g. “Sell after H days or if effect has played out”]. 
**Sizing:** [E.g. invest $Y in each trade]. 
**Benchmark:** [E.g. SPY total return or size-weighted index]. 
**Costs Model:** [Spread, slippage, fees assumptions in bps]. 
**Capacity:** [Cap C where we stop scaling]. 
**Out-of-Sample (OOS):** [E.g. first test on data Jan2015–Dec2019, OOS Jan2020–Dec2021]. 
**Falsification:** [What null hypothesis test, e.g. “If effect <= cost or Sharpe < 0.5 OOS, reject”].
```

*(Example for B2 above:)*  
```
Hypothesis B2 (Index Inclusion): When Stock X is announced as joining Russell 2000, buy at next open. 
Observable Signal: Russell reconstitution notice (from Russell’s press release feed) at time T. 
Prediction: Stock outperforms Russell 2000 by at least 0.5% in next 3 trading days. 
Entry: Buy close of day before effective date. Exit: Sell 3rd trading day after effective date or on target. 
Sizing: $10k per trade. Benchmark: equal-weight Russell 2000 return over same days. 
Costs Model: assume 2 bps half-spread + 2 bps slippage. 
Capacity: $100k per position. 
OOS: Run on 2000–2019 data in-sample, holdout 2020–2025. 
Falsification: If mean excess return ≤0 (net costs) or not statistically >0.5%, reject.
```  

We will format each chosen hypothesis in this templated manner.  

## 6. Recommendation

**Option 1 – Proceed to pre-registered tests:** The analysis has found several **plausible mechanisms** (e.g. index inclusion, niche ETF mispricing, spin-offs, microcap value) that merit controlled testing. We recommend authorizing disciplined backtests for the top 3–5 hypotheses, but **only after writing down the specs above and ensuring data availability**.  

**Option 2 – Acquire new capability:** If no hypothesis is fully executable with existing data/brokerage, a targeted capability could be acquired. For example, if minute-level NAVs are needed for ETFs, one might pay for a real-time ETF NAV feed (cost ~$X/year). If small-cap data is missing, one could license consolidated small-stock trade data (but this is expensive). We only endorse this if the preliminary audit shows a clearly large inefficiency that current data cannot capture; otherwise the evidence to justify the expense is weak.  

**Option 3 – Stop and reallocate effort:** Given the exhaustive audit of obvious opportunities, it is quite possible no testable edge remains. If the top hypotheses all fail feasibility or OOS testing, the rational conclusion is to stop systematic alpha search and focus on other pursuits (income-generation, skill development, non-quant trading, etc.). This decision would be business-driven, not a reflection on skill.  

**Executive Recommendation:** *We should proceed with a narrowly scoped backtesting phase.* Specifically, *authorize pre-registered tests for the best 2–3 hypotheses (e.g. Index Inclusion, Niche-ETF premium, Spin-off drift)* if their data signals can be reliably obtained. We must **pre-commit** to the hypothesis form and not tweak rules post-hoc. If none of these yields a positive, cost-adjusted return, the evidence will strongly support pausing systematic research under current constraints. 

```mermaid
flowchart TB
    A[Start Phase B Audit] --> B[Define candidate mechanism (constraint, participant)]
    B --> C{Is signal observable?}
    C -->|No| Z[Discard mechanism]
    C -->|Yes| D{Retail execution feasible?}
    D -->|No| Z
    D -->|Yes| E{Costs & capacity model?}
    E -->|Infeasible| Z
    E -->|OK| F[Pre-register hypothesis]
    F --> G[Run backtest (IS + OOS)]
    G --> H{Results: return > cost?}
    H -->|Yes| Certified[/**Certified Edge**/]
    H -->|No| Dead[/**No Edge (Dead)**/]
```

Figure 2. *Phase B workflow for each hypothesis. A mechanism must pass all gating checks before a pre-registered test is run. Out-of-sample results then decide “Certified” vs “Dead.”*  

![Relative advantage scores of different environments for a small trader (higher = more advantageous).](https://i.imgur.com/VuUTR8g.png)  
*Figure 3. Comparative chart (example) rating each environment’s appeal for small traders. Higher score = greater advantage.*  

**Sources:** Industry and academic research on small-cap inefficiencies, ETF structure and liquidity, spin-off performance, and ETF index rebalancing.  (Primary filings such as SEC forms, index announcements, and exchange data are the underlying evidence.)  

