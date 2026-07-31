### **spx dealer gamma exposure research specification**

**Status:** Pre-research specification

**Classification:** Candidate mechanic / Structural hedging flows / Regime filter

**Purpose:** Define the research question, evidence requirements, data, execution assumptions, and rejection gates before writing collection or backtest code.

---

### **the research question**

Can a daily dealer gamma exposure regime for SPX options explain and predict intraday index behavior well enough to survive fees, slippage, and model error?

This is a hypothesis. It is not yet an edge, strategy, or approval to trade.

The first implementation targets SPX. The exact historical window and thresholds must be chosen only after data access and historical options coverage are verified.

---

### **the market and instruments**

- **Asset class:** U.S. equities / index options
- **Primary underlying:** SPX
- **Signal source:** Listed equity index options with open interest and expiration structure
- **Execution instrument:** SPX intraday price action used as the research target
- **Strategy family:** Intraday bias / trend following / mean reversion regime filter
- **Initial horizon:** 5-minute to 15-minute intraday
- **Excluded initially:** Single-name options, overnight gap prediction, options market making, and multi-strategy portfolios

The word gamma in this document refers to dealer aggregate gamma exposure derived from options positioning and hedging assumptions. It is not a chart indicator.

---

### **the proposed mechanic**

Options market makers must hedge changes in delta exposure as the underlying moves, time passes, or implied volatility changes. When aggregate dealer positioning is net short gamma, hedging can amplify moves. When positioning is net long gamma, hedging can dampen moves and encourage mean reversion.

The candidate implementation is:

- **Negative gamma regime:** traders expect stronger intraday momentum or trend persistence.
- **Positive gamma regime:** traders expect stronger intraday mean reversion or pinning behavior.

The position is not automatically profitable. It may still have basis risk, model error, stale open-interest assumptions, and execution friction.

---

### **research findings**

The first literature and documentation pass produces the following conclusions:

- Recent empirical work supports the idea that dealer gamma matters for intraday behavior in S&P 500-related markets, but the effect is regime-dependent rather than universal.
- 0DTE growth makes same-day hedging effects more important in modern SPX behavior.
- Positive gamma tends to be associated with dampened volatility or reversal behavior, while negative gamma can be associated with amplified movement.
- The literature also shows that pooling regimes can erase predictive power, so a valid study must split by regime and test robustness out of sample.
- A daily gamma regime derived from end-of-day options data is a defensible first research design, but it is not sufficient proof of a live edge.

The research changes the working hypothesis from:

> Dealer gamma is a universal predictor.

to:

> Dealer gamma may be a regime filter that changes the distribution of intraday returns, and we need to test whether that survives current data and friction.

---

### **version-one research scope**

The venue research supports the following provisional scope:

- **Research venue:** SPX.
- **Signal source:** Daily end-of-day options chain and open interest.
- **Execution proxy:** Intraday price action on the underlying during regular trading hours.
- **Direction:** Regime-dependent.
- **Excluded from version one:** Overnight prediction, single-name options, multi-leg options trades, and discretionary interpretation of the gamma map.
- **Research objective:** Determine whether the sign and magnitude of dealer gamma exposure improves intraday return classification after executable costs and a frozen set of rules.
- **Regime handling:** Version one must test positive-gamma and negative-gamma regimes separately rather than pooling them into one average signal.

This is a research scope, not a trading approval.

Databento is the preferred starting point for a full intraday options replay if we later need a higher-fidelity chain workflow, because it supports historical options, option chains, expirations, strikes, greeks, and underlying prices in one normalized workflow. For the first pass, Cboe is the primary data route because the SPX option EOD summary includes gamma and open interest fields needed to construct a daily regime classifier without immediately requiring a paid intraday chain feed.

### **implementation status**

The gamma-flow research scaffold is not yet implemented.

- The funding-basis candidate has been formally rejected and recorded separately.
- This document defines the next mechanic to investigate.
- No gamma-flow code should be written until the research questions and data source are finalized.

The first study has two data-fidelity levels:

- **Level 1, daily regime feasibility:** Use EOD chain data, open interest, expirations, strikes, greeks, and underlying intraday bars. This tests whether the thesis survives a simple, reproducible regime classification.
- **Level 2, intraday options replay:** Add intraday options-chain data, quotes, and underlying prices. This is required before making claims about live executable capacity or deployment.

Level 1 cannot be described as a full executable backtest. Level 2 is the required standard for any final positive conclusion.

---

### **level-one data acquisition plan**

The search identified two practical starting routes:

1. **Cboe historical EOD options data**
   - Cboe offers historical options data downloads and a Cboe LiveVol option EOD summary with fields including strike, expiration, option type, bid/ask, delta, gamma, and open interest.
   - This is the primary first-pass route for SPX daily regime classification.
   - Documentation: https://www.cboe.com/us/options/market_statistics/historical_data/ and https://datashop.cboe.com/option-eod-summary

2. **Databento historical options**
   - Databento documents historical options support, including stock options, ETF options, index options, option chains, expirations, strikes, underlying prices, open interest, volume, implied volatility, and greeks.
   - This is the fallback route if the Cboe EOD sample is not sufficient and we need a deeper intraday chain workflow.
   - Documentation: https://databento.com/docs and https://databento.com/docs/examples/basics-historical-live/

The acquisition sequence is:

- Select the primary underlying: SPX.
- Confirm the historical date range and available chain depth.
- Confirm that open interest, strikes, expirations, and the underlying price series are available for the same historical window.
- Validate a short sample first before downloading the full window.
- If the chosen source cannot provide a usable chain and underlying pairing, revise the market or move to another vendor.

---

### **source register**

#### **Academic and research sources**

- [0DTEs: Trading, Gamma Risk and Volatility Propagation](https://papers.ssrn.com/sol3/Delivery.cfm/4692190.pdf?abstractid=4692190&mirid=1) — finds that market makers’ gamma inventory is related to future intraday volatility and that the sign of inventory gamma matters for reversal versus momentum.
- [Dealer Gamma Exposure and Overnight Gap Risk: Incremental Information in Low-Volatility Regimes](https://papers.ssrn.com/sol3/Delivery.cfm/6650858.pdf?abstractid=6650858&mirid=1) — finds regime-dependent predictive value and warns against pooling stressed and calm regimes.
- [Zero DTE Options Gamma Hedging](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5329719) — discusses the sensitivity of 0DTE option dynamics to gamma hedging.

#### **Official venue and data sources**

- [Databento docs](https://databento.com/docs) — documents historical options support, options chains, expirations, strikes, open interest, greeks, and underlying prices.
- [Databento options tutorials](https://databento.com/docs/examples/basics-historical-live/) — shows historical options workflows and underlying joins.
- [Cboe historical options data](https://www.cboe.com/us/options/market_statistics/historical_data/) — provides historical options volume and related data products.
- [Cboe option EOD summary](https://datashop.cboe.com/option-eod-summary) — provides daily chain fields including gamma, delta, open interest, and underlying price.
- [Cboe SPX options product page](https://www.cboe.com/tradable-products/sp-500/spx-options/) — confirms SPX as a large, liquid index options market.

These sources support the research design but do not prove that the candidate is profitable.

---

### **the why and the counterparty**

The candidate source of return is not the direction of the market by itself. The proposed source is the interaction between:

- options customers who buy or sell protection or leverage;
- dealers who must hedge changing delta exposure;
- short-dated expirations that make the hedging flow more concentrated;
- market structure that can amplify or dampen intraday volatility depending on the sign of aggregate gamma.

The likely counterparties are options market makers and hedging desks. The research must test whether the compensation is sufficient for the risk, noise, and execution cost.

The hypothesis fails conceptually if the observed result is primarily look-ahead, mismeasured open interest, stale chain data, or a hidden directional bias.

---

### **what must be established before coding**

1. Confirm the exact underlying to test first: SPX.
2. Confirm how the gamma regime will be calculated from historical data, including sign convention and aggregation rules.
3. Confirm whether the chosen data source provides options chain history, open interest, expirations, strikes, and the underlying price series on the same dates.
4. Confirm whether daily EOD chain data is enough for the first study or whether intraday chain replay is required immediately.
5. Confirm the regular trading hours window used for the intraday test.
6. Confirm the friction model: spread, fees, and any assumed slippage.
7. Identify survivorship, timestamp, and stale-chain risks.
8. Freeze the entry, exit, and sizing rules before any out-of-sample test.

---

### **required data**

#### **Underlying market data**

- Timestamp in UTC or market-local trading time
- Open, high, low, close
- Volume
- Bid and ask where available
- Regular trading hours only

#### **Options chain data**

- Underlying symbol
- Quote date
- Expiration
- Strike
- Option type
- Open interest
- Volume
- Bid, ask, and last where available
- Implied volatility where available
- Delta, gamma, theta, vega where available
- Underlying price at the chain snapshot
- Sign convention used for the aggregate gamma regime

#### **Venue and operational data**

- Fee schedule and spread assumptions
- Historical contract and listing changes
- Trading hours
- Data source coverage and timestamp conventions

---

### **data validation**

Before calculating a return:

- Normalize timestamps and verify ordering.
- Detect missing, duplicated, stale, and out-of-order observations.
- Verify that the options chain and underlying prices align on the same historical date.
- Verify that the regime calculation uses only information available at the chosen decision time.
- Keep raw data immutable and store cleaning decisions separately.
- Compare at least two independent sources where practical.

---

### **minimum machine-executable model**

The first model must be deliberately simple.

#### **Signal**

At decision time, calculate:

- aggregate dealer gamma regime;
- sign of the regime;
- intraday volatility context;
- expected friction.

For version one, the signal is evaluated once per day before the intraday trading window. The regime must be frozen before execution and cannot use future intraday information.

#### **Entry condition**

Enter only when the regime filter and the intraday trigger align:

- negative gamma regime may allow momentum-style entries;
- positive gamma regime may allow mean-reversion-style entries.

The exact trigger must be frozen before out-of-sample testing.

#### **Exit conditions**

Exit when any of the following occurs:

- the stop loss is hit;
- the take profit is hit;
- the session ends;
- the regime filter no longer applies for the next holding period;
- the market becomes illiquid or disconnected.

#### **Position sizing**

Size from the lower of:

- predefined portfolio risk budget;
- stop-loss distance;
- available executable depth;
- venue and instrument limits.

Do not size from gamma alone. A strong regime signal does not remove execution risk.

---

### **validation plan**

#### **Economic validation**

- Explain the return decomposition.
- Verify that the result is not profitable only because of look-ahead or a regime label that used future data.
- Compare regime-conditioned returns against an unconditioned benchmark.

#### **Statistical validation**

- Split data into in-sample and out-of-sample periods.
- Freeze the rules before out-of-sample evaluation.
- Use walk-forward testing across different volatility regimes.
- Use Monte Carlo trade reshuffling to study sequence risk.
- Use bootstrap resampling to estimate drawdown, expected outcomes, and ruin probability.

#### **Robustness validation**

The result must not depend on:

- one ticker only;
- one short window;
- one threshold;
- one fee tier;
- one favorable day;
- one specific 0DTE session;
- one model assumption.

---

### **rejection gates**

Reject the candidate if any of the following is true:

- the counterparty and economic mechanism cannot be explained;
- the result depends on unavailable or look-ahead data;
- the regime signal disappears after realistic friction;
- out-of-sample performance is materially worse than in-sample performance;
- the result works only on one window or one volatility state;
- data quality cannot support a stable regime label;
- Monte Carlo or bootstrap results show unacceptable drawdown or ruin probability.

A failed candidate is a successful research outcome. It prevents capital from being allocated to an unverified story.

---

### **tavily research questions**

Research should answer these questions before implementation:

1. What peer-reviewed or high-quality empirical evidence measures dealer gamma exposure and intraday behavior in SPY/SPX?
2. How should 0DTE and short-dated options be treated in the regime calculation?
3. What data fields are required to reconstruct a daily gamma regime from historical options data?
4. Which venue or data vendor provides the cleanest and most complete historical options chain for SPX?
5. What known risks make gamma-based intraday models fail during high-volatility regimes?
6. What evidence exists for regime dependence rather than a universal effect?
7. Which parts of the proposed model are already crowded or likely to have decayed?
8. What minimum paper-trading period and live monitoring metrics are appropriate before any capital is considered?

Search results must be classified as:

- primary academic evidence;
- official venue documentation;
- reliable market-data documentation;
- practitioner evidence;
- anecdotal or promotional material.

Promotional material is not sufficient to validate the mechanic.

---

### **research status and unresolved questions**

The funding-basis candidate is rejected and documented separately. This spec is now the next research target.

Still unresolved before coding, and who resolves each item:

- **Implemented:** Chosen underlying for the first pass is SPX.
- **Implemented:** Chosen data route for the first pass is Cboe EOD options data for SPX, with Databento reserved as the higher-fidelity fallback.
- **Research:** Confirm whether the first version should be daily EOD regime classification or intraday options replay.
- **Research:** Reconstruct one historical gamma regime from a short sample and verify that the label is stable.
- **Research:** Test whether the regime survives friction and out-of-sample splitting.

These assumptions are for research only. They do not authorize live trading or imply that the strategy is suitable for the user's account.

The next research deliverable must resolve these questions with source-backed evidence. Until then, no underlying, data vendor, threshold, or return target is approved.

---

### **definition of done before coding**

No collection or backtest code begins until:

- the research questions have been answered with cited sources;
- the underlying and data source have been selected with reasons;
- the data schema and historical availability are confirmed;
- the gamma regime formula and sign convention are understood;
- the cost model is specified;
- entry, exit, and sizing rules are frozen in writing;
- rejection thresholds are registered;
- the known risks and failure modes are documented;
- the first paper-trading design is defined.

The outcome of this document may be approval to code, revision of the hypothesis, or rejection of the candidate.
