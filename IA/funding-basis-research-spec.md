### **crypto perpetual funding and basis research specification**

**Status:** Pre-research specification

**Classification:** Candidate mechanic / Relative value / Operational and plumbing constraints

**Purpose:** Define the research question, evidence requirements, data, execution assumptions, and rejection gates before writing collection or backtest code.

---

### **the research question**

Can a hedged position involving a crypto perpetual contract and its corresponding spot market produce positive expected value after funding, fees, spread, slippage, borrow, transfer, execution, and operational risk?

This is a hypothesis. It is not yet an edge, strategy, or approval to trade.

The first implementation should target one liquid asset on one venue. The exact venue, research period, and thresholds must be chosen only after market access and data availability are verified.

---

### **the market and instruments**

- **Asset class:** Crypto
- **Primary derivative:** Linear USDT- or USDC-margined perpetual contract
- **Hedge instrument:** Spot asset on the same or another venue
- **Strategy family:** Relative value / carry
- **Initial horizon:** Funding interval to several days
- **Excluded initially:** Options, inverse contracts, illiquid altcoins, leveraged directional trades, and multi-strategy portfolios

The word futures in this document refers primarily to perpetual derivative contracts. A perpetual is not the same as an expiry-based traditional futures contract.

---

### **the proposed mechanic**

Perpetual contracts use periodic funding payments to help keep their price aligned with the underlying spot market. When positioning becomes one-sided, the funding rate and the perpetual-to-spot basis can become large enough to attract arbitrage activity.

The candidate trades are:

- **Positive funding:** buy spot and short the perpetual, collecting funding if the position remains properly hedged.
- **Negative funding:** short spot where borrow is available and long the perpetual, collecting the opposite funding direction if all costs permit.
- **Cross-venue basis:** take offsetting positions on venues when the executable price or funding difference exceeds all transfer, execution, and counterparty costs.

The position is not automatically market neutral. It may still have basis risk, index-price differences, liquidation risk, funding-rate changes, exchange risk, and execution mismatch.

---

### **research findings**

The first literature and documentation pass produces the following conclusions:

- Funding is an algorithmic feedback mechanism intended to anchor the perpetual to an index. It is not a guaranteed yield stream or a passive transfer that can be projected unchanged into the future.
- Academic work identifies persistent basis deviations and shows that funding-rule design, clamping, caps, funding intervals, leverage, and liquidation dynamics affect both convergence and tail risk.
- A perpetual contract is not guaranteed to converge to spot in the same way as an expiry-based futures contract. The hedge can therefore carry residual basis risk even when the spot and perpetual represent the same asset.
- Funding rules are venue-specific. Settlement intervals, mark and index prices, premium averaging, caps, floors, and the exact rate used at assessment can change by contract and over time.
- Official venue documentation confirms that a position may need to remain open at a precise assessment time to receive or pay funding. The displayed or estimated rate is not necessarily the rate ultimately applied.
- Existing empirical studies report potentially attractive results, but those results are not sufficient evidence of deployable profitability. They require independent reconstruction with current venue rules, executable prices, conservative costs, and out-of-sample testing.
- The most defensible first study is therefore a **single-venue, single-asset historical reconstruction** before attempting cross-venue transfer or capital movement.
- Tavily returned claims of positive net returns in selected historical windows, but the reported thresholds and annualized returns were not consistently traceable to strong primary sources. They are not adopted as assumptions, targets, or evidence of a live edge.
- The first falsifiable result must be generated from raw venue data and our own conservative execution model, not copied from published annualized yields.
- Binance's official API provides current order-book data and historical funding, mark/index, and related series, but a complete arbitrary historical full-depth order-book archive is not identified as a normal free public endpoint. Historical executable-cost reconstruction may therefore require a licensed dataset, a whitelisted historical-depth service, or conservative scenario modeling.

The research changes the working hypothesis from:

> Collect high funding and assume the hedge is neutral.

to:

> Reconstruct the exact venue funding payment and executable two-leg return, then determine whether any residual return survives current costs, basis risk, and operational constraints.

---

### **version-one research scope**

The venue research supports the following provisional scope:

- **Research venue:** Binance USDⓈ-M Futures. User-confirmed as available for the intended jurisdiction and use.
- **Perpetual contract:** BTCUSDT linear perpetual.
- **Spot hedge:** BTCUSDT spot on the same venue if the account and market access support both legs.
- **Direction:** Positive-funding carry only: long spot and short perpetual.
- **Excluded from version one:** Negative-funding carry, spot borrowing, cross-venue transfers, cross-venue basis, altcoins, leverage above the minimum required for operational margin, and prediction of unusually high future funding.
- **Research objective:** Reconstruct whether holding the two legs through funding assessments produced positive net return after executable entry and exit costs, funding payments, basis movement, margin, and operational reserves.

This is a research scope, not a trading approval. If same-venue spot and perpetual access is not available, the scope must be revised before coding rather than silently becoming a cross-venue strategy.

Binance is selected provisionally because its official USDⓈ-M documentation exposes funding history, mark price, index price, open interest, order-book, symbol information, and related market-data endpoints. Venue availability is confirmed by the user; regular-user fees are fixed as the research assumption and historical-data verification remains.

The first study has two data-fidelity levels:

- **Level 1, public-data feasibility:** Use historical trades, public candles, funding history, mark/index prices, open interest, symbol metadata, and conservative spread/slippage scenarios. This tests whether the hypothesis has enough gross economics to deserve deeper data.
- **Level 2, executable replay:** Add historical order-book snapshots or depth updates for both spot and perpetual. This is required before making claims about live executable capacity or deployment.

Level 1 cannot be described as a full executable backtest. Level 2 is the required standard for any final positive conclusion.

### **level-two data acquisition plan**

The search identified four acquisition routes:

1. **Binance historical-depth API: restricted/free if approved**
   - Binance documents a historical Futures order-book download route for snapshot (`S_DEPTH`) and tick-level depth (`T_DEPTH`) data.
   - This is separate from ordinary Futures trading access. A verified account can trade Futures and still lack permission for the historical-depth download service.
   - Access requires a Futures-enabled API key and Binance approval or whitelist status for the historical-data endpoint. A normal account should not be assumed to have this permission until the endpoint is tested.
   - This is the preferred route because it keeps the data on the selected venue and avoids vendor normalization uncertainty.

2. **Tardis historical replay: paid, with limited public samples**
   - Tardis provides Binance USDⓈ-M Futures depth channels, historical coverage, downloadable samples, and API replay.
   - The service requires an API key for general historical replay. Public sample files are useful for schema and pipeline validation but are not enough for a full performance conclusion.

3. **Amberdata historical order books: paid commercial source**
   - Amberdata advertises historical Binance spot and futures order-book snapshots and events, including one-minute snapshots and deeper data products.
   - Coverage, exact BTCUSDT spot/perpetual availability, retention, and pricing must be confirmed before purchase.

4. **Community/free archives: pilot only**
   - Kaggle, GitHub, and community archives may contain isolated BTCUSDT depth samples.
   - They are acceptable for parser and execution-engine tests only until provenance, completeness, timestamps, and both-leg coverage are independently verified.
   - Free Bybit order-book archives do not satisfy this Binance study. Using them would require changing the venue and restarting the venue-specific specification.

5. **Binance Vision: free public market data, but not the required Level 2 archive**
   - `data.binance.vision` provides free daily and monthly public files such as Futures klines, aggregate trades, and trades.
   - It is useful for Level 1 and for validating timestamps and trade reconstruction.
   - The public archive does not replace the historical BTCUSDT spot and Futures order-book snapshots or deltas required for Level 2.

6. **CryptoHFTData: free normalized Level 2 source with limited history**
   - CryptoHFTData advertises Binance spot and Futures snapshots plus deltas in Parquet/Zstandard format, with BTCUSDT Futures coverage beginning 2025-06-28.
   - Its public dashboard states that the research-grade dataset is available for $0.00 and that API access is provided through the dashboard.
   - The dataset is therefore the primary free Level 2 route for this project, subject to validating the actual API response, coverage, rate limits, and download terms.
   - The history begins in July 2025 and the files are organized hourly. “Hourly” describes file partitioning; it must not be interpreted as hourly order-book updates because the files contain tick-level L2 events.

The acquisition sequence is:

- Create or use a dedicated Binance API key with read-only permissions and Futures market-data access. Do not enable withdrawals, and do not share the key or secret.
- Submit Binance's historical Futures data access or whitelist request if the endpoint returns an authorization or whitelist error.
- Test the historical-depth endpoint with a short BTCUSDT Futures date range. Test spot depth separately because spot and Futures historical datasets are separate products.
- Confirm whether the response provides `S_DEPTH` snapshots or `T_DEPTH` incremental updates, and whether the selected dates and instruments are covered.
- If access is granted, validate reconstruction on a small period before downloading more data.
- Download and validate a CryptoHFTData sample first, because it is the stated free Level 2 route.
- If the CryptoHFTData sample is incomplete, inaccessible, or unsuitable for both spot and Futures, compare Tardis and Amberdata for the same date and instrument.
- Select a paid source only if its coverage, timestamps, depth format, and cost are acceptable.
- If neither paid source is viable, proceed with Level 1 feasibility analysis and explicitly stop before claiming executable profitability.

Level 2 is available through a stated free CryptoHFTData route beginning in July 2025, subject to validation. Binance's own historical-depth route may also be free if whitelist approval is granted, but existing Futures trading access is not the same as historical-depth access. Paid vendors remain fallbacks for older history or missing coverage.

---

### **source register**

#### **Academic and research sources**

- [A Primer on Perpetuals](https://arxiv.org/abs/2209.03307) — establishes the contract concept and distinguishes perpetual designs from ordinary expiry-based futures.
- [Arbitrage in Perpetual Contracts](https://papers.ssrn.com/sol3/Delivery.cfm/5262988.pdf?abstractid=5262988&mirid=1&type=2) — studies clamping, persistent price discrepancies, and no-arbitrage bounds using Binance data.
- [Funding Rate Mechanism in Perpetual Futures](https://papers.ssrn.com/sol3/Delivery.cfm/6185958.pdf?abstractid=6185958&mirid=1&type=2) — models funding as a feedback rule and discusses mean reversion, caps, intervals, and liquidation-driven crises.
- [Exploring Risk and Return Profiles of Funding Rate Arbitrage on CEX and DEX](https://doi.org/10.1016/j.bcra.2025.100354) — provides empirical funding-arbitrage analysis but still requires independent validation under our execution assumptions.
- [On the Quality of Cryptocurrency Markets: Centralized vs. Decentralized Exchanges](https://doi.org/10.1287/mnsc.2024.07703) — supports treating transaction costs, no-arbitrage deviations, and venue architecture as central research variables.

#### **Official venue and data sources**

- [OKX perpetual funding mechanism](https://www.okx.com/en-us/help/perps-funding-fee-mechanism) — documents funding direction, assessment timing, interval changes, caps, floors, mark/index mechanics, and the possibility that the applied rate differs from an earlier estimate.
- [Bybit funding-rate documentation](https://www.bybit.global/en/help-center/article/?id=000001123) — documents minute-level calculation, premium-index averaging, settlement intervals, and volatility-related limit changes.
- [Bybit funding-rate history API](https://bybit-exchange.github.io/docs/v5/market/history-fund-rate) — confirms a historical endpoint for USDT, USDC, and inverse perpetuals.
- [Binance futures market-data API](https://developers.binance.info/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Price-Ticker-v2) — documents funding-rate and funding-interval market-data endpoints.
- [Binance USDⓈ-M futures fees](https://www.binance.com/en/fee/futureFee) and [Binance spot fees](https://www.binance.com/en/fee/trading) — provide the regular-user maker/taker fee assumptions used for Level 1 research.
- [Binance historical-data backtesting guide](https://www.binance.com/en-NG/blog/futures/421499824684901131) — describes historical futures data and the whitelist requirement for order-book downloads.
- [Tardis Binance USDⓈ-M Futures coverage](https://docs.tardis.dev/historical-data-details/binance-futures) — documents Binance Futures depth coverage, downloadable samples, and API replay.
- [Amberdata Binance market data](https://www.amberdata.io/binance-market-data) — documents commercial historical Binance order-book snapshots and events.
- [Binance Public Data repository](https://github.com/binance/binance-public-data) — documents the free public archive available through [data.binance.vision](https://data.binance.vision/) for klines, trades, and aggregate trades; it does not establish free full-depth Level 2 coverage.
- [CryptoHFTData Binance orderbook dataset](https://www.cryptohftdata.com/datasets/binance-orderbook-data) and [dashboard](https://www.cryptohftdata.com/dashboard) — advertise normalized Binance spot and Futures snapshots plus deltas, free API access, Parquet files, and July 2025 coverage; these claims still require local sample validation.
- [CCXT funding-rate history documentation](https://docs.ccxt.com/docs/examples/ts/fetch-funding-rate-history) — confirms a unified interface for funding history, while exchange-specific parameters still require venue documentation.

These sources support the research design but do not prove that the candidate is profitable.

#### **Tavily research assessment**

- Tavily was restored and used for four focused queries covering profitability, venue formulas, convergence risk, and data requirements.
- The results were useful for locating relevant sources and recurring risks, but some generated summaries included exact return figures and thresholds without sufficiently strong primary-source support.
- Those figures are excluded from the model. We will use source documents for mechanics and our own reconstruction for performance.
- Research output is evidence discovery, not validation. Every material claim must be checked against the linked paper, official venue documentation, or raw data.

---

### **the why and the counterparty**

The candidate source of return is not that crypto prices rise or fall. The proposed source is the interaction between:

- leveraged traders demanding one-sided perpetual exposure;
- the perpetual funding mechanism;
- arbitrageurs who require compensation for capital, execution, venue, and liquidation risk;
- operational friction that prevents every participant from instantly equalizing prices and funding rates.

The likely counterparties are leveraged participants paying for directional exposure and traders who cannot or will not maintain a fully hedged position. This is weaker than a legal mandate or mathematical dealer hedge. The research must test whether the compensation is sufficient for the risks taken.

The hypothesis fails conceptually if the observed return is primarily unexplained directional exposure, stale pricing, exchange credit risk, or a data artifact.

---

### **what must be established before coding**

1. Confirm how each venue calculates funding, including rate formula, cap, floor, interval, mark price, index price, and payment timestamp.
2. Confirm whether historical funding data is complete, timestamped correctly, and available without look-ahead.
3. Confirm the exact spot and perpetual symbols, contract specifications, quote currency, tick size, lot size, leverage rules, mark price, index price, funding formula, cap, floor, interval, and historical rule changes.
4. Confirm whether spot shorting, margin borrowing, or an equivalent hedge is actually available for the negative-funding case.
5. Use the verified regular-user fee schedule as the base case: Binance USDⓈ-M Futures maker 0.0200% and taker 0.0500%; Binance spot maker and taker 0.1000% before any optional BNB discount. Do not assume maker fills without an order-placement and fill model.
6. Confirm whether positions can be opened, hedged, and closed within the required time at the intended capital size.
7. Confirm venue jurisdiction, custody, withdrawal, API, outage, and counterparty risks before treating a venue as usable.
8. Identify all known sources of survivorship, selection, timestamp, look-ahead, and stale-price bias.
9. Reconstruct at least one venue's historical funding payment independently from the venue's published history before using a unified API for the full study.
10. Confirm that Binance USDⓈ-M Futures and the corresponding spot market are available for our jurisdiction, account type, and intended paper-trading use.

---

### **required data**

#### **Instrument metadata**

- Venue and market identifier
- Contract type and settlement currency
- Base and quote asset
- Contract multiplier
- Tick size and quantity step
- Minimum order size and notional limits
- Margin mode and liquidation rules
- Funding interval and payment convention
- Mark-price and index-price definitions
- Listing, delisting, and contract-change dates

#### **Perpetual market data**

- Timestamp in UTC
- Bid price and ask price
- Bid and ask size where available
- Trade price and trade size where available
- OHLCV bars at the selected research frequency
- Mark price
- Index price
- Mid price
- Open interest
- Funding rate that was actually paid
- Funding-rate estimate, if published
- Funding payment timestamp
- Funding interval at the time of payment
- Funding cap and floor at the time of payment
- Premium-index and interest-rate components where available
- Liquidation data where available

#### **Spot market data**

- Timestamp in UTC
- Bid price and ask price
- Bid and ask size where available
- Trade price and trade size where available
- OHLCV bars at the selected research frequency
- Executable spread and depth
- Spot borrowing rate and availability for short-spot cases
- Spot borrow utilization and recall risk where available

#### **Venue and operational data**

- Trading fees and fee schedule history
- Funding and settlement history
- Deposit and withdrawal status history where available
- Transfer fees and transfer time estimates
- API outage and rejected-order records where available
- Rate limits and order throttling rules
- Insurance, auto-deleveraging, and liquidation policy
- Historical changes to contract rules and fee schedules

For version one, the minimum viable historical dataset is BTCUSDT spot and perpetual bid/ask or depth data, executed trades, mark price, index price, realized funding rate and timestamp, open interest, symbol metadata, and the applicable fee schedule. Liquidation and borrow data remain required risk inputs where available, but they are not reasons to expand the initial scope to negative-funding or cross-venue trades.

---

### **data validation**

Before calculating a return:

- Normalize all timestamps to UTC and verify ordering.
- Detect missing, duplicated, stale, and out-of-order observations.
- Reconcile funding payments against venue-published history.
- Verify that prices are executable rather than theoretical midpoints.
- Verify both legs against order-book depth at the intended notional, not only last trade prices.
- Verify symbol mappings through contract changes and delistings.
- Check that each signal uses only information available before the order decision.
- Keep raw data immutable and store cleaning decisions separately.
- Record the data source, retrieval time, version, and known limitations.
- Compare at least two independent sources where practical.
- Treat CCXT as a normalization layer, not as the source of truth for venue-specific formulas or historical rule changes.

---

### **minimum machine-executable model**

The first model must be deliberately simple.

#### **Signal**

At decision time, calculate:

- expected funding income over the planned holding period;
- executable basis between the two legs;
- all opening, holding, and closing costs;
- expected slippage at the intended notional;
- borrow or financing cost where applicable;
- a risk reserve for funding changes, leg divergence, and liquidation distance.

For version one, the signal is evaluated before each funding assessment. The next funding estimate is not treated as guaranteed. The research must compare at least three assumptions: zero future funding, the published estimate with a conservative haircut, and the realized funding rate after the assessment. Entry is allowed only when the conservative case clears the threshold.

#### **Entry condition**

Enter only when:

`expected net return = expected funding + expected basis capture - all costs - risk reserve`

is greater than a pre-registered minimum threshold.

The initial backtest must test the threshold as a parameter range and must not hard-code a funding-rate threshold from published research. The first version should enter only when the spot and perpetual hedge can be opened within the same decision window and the executable basis is within the pre-registered risk band.

The threshold, holding period, and sizing rule must be selected before out-of-sample testing. They must not be chosen to make the historical result pass.

#### **Exit conditions**

Exit when any of the following occurs:

- the planned holding period ends;
- expected net return falls below the exit threshold;
- the basis or funding relationship moves against the position beyond the risk limit;
- one leg cannot be maintained or rebalanced;
- liquidity falls below the minimum execution requirement;
- venue, custody, API, or settlement risk becomes unacceptable;
- the stop condition is reached.

For version one, the planned holding period ends after a pre-registered number of funding assessments or when the conservative expected carry no longer covers the estimated round-trip closing cost. The basis stop must be expressed as a loss in account currency or percentage of hedged notional, not as an undefined chart condition.

#### **Position sizing**

Size from the lower of:

- predefined portfolio risk budget;
- expected liquidation and basis risk;
- available executable depth;
- venue and instrument notional limits;
- capital available for both legs and operational reserves.

Do not size from funding yield alone. A high funding rate may represent high stress and high basis risk.

---

### **cost model**

The backtest must model both legs independently and include:

- entry spread crossing;
- exit spread crossing;
- maker or taker fees using a conservative assumption;
- market impact based on available depth;
- funding actually received or paid;
- spot borrow and financing costs;
- transfer fees and expected transfer delay;
- rebalance costs when the hedge ratio changes;
- conversion and stablecoin costs where applicable;
- failed, partial, or delayed fills;
- exchange outages and forced-unwind assumptions.

No result is valid if it uses mid-price fills while claiming executable arbitrage.

For the same-venue version-one model, transfer fees are excluded from each trade's PnL only when both legs are funded before the simulated entry. They remain part of the operational capital requirement. If capital must be transferred between venues, this is a different model and requires a separate specification.

---

### **validation plan**

#### **Economic validation**

- Explain the return decomposition: funding, basis, trading costs, financing, and residual price exposure.
- Verify that the strategy is not profitable only because of an incorrect funding timestamp or unmodeled leg movement.
- Compare hedged returns against an unhedged directional benchmark.

#### **Statistical validation**

- Split data into in-sample and out-of-sample periods.
- Freeze the rules before out-of-sample evaluation.
- Use walk-forward testing across different funding and volatility regimes.
- Test multiple liquid assets and venues without selecting only successful examples.
- Test a reasonable range of thresholds and holding periods.
- Use Monte Carlo trade reshuffling to study sequence risk.
- Use bootstrap resampling to estimate drawdown, expected outcomes, and ruin probability.

#### **Robustness validation**

The result must not depend on:

- one asset;
- one exchange;
- one short historical window;
- one funding interval;
- one threshold;
- one fee tier;
- one favorable execution assumption;
- one exceptional market event.

#### **Capacity validation**

- Replay the strategy at several notional sizes.
- Measure spread, depth, market impact, and fill degradation.
- Determine the capital level at which net return materially deteriorates.
- Treat that level as a capacity estimate, not as an optimization target.

---

### **rejection gates**

Reject the candidate if any of the following is true:

- the counterparty and economic mechanism cannot be explained;
- the return disappears after realistic fees, spreads, slippage, borrow, or transfer costs;
- the result depends on unavailable or look-ahead data;
- one leg cannot be executed or maintained reliably;
- out-of-sample performance is materially worse than in-sample performance;
- the result works only on one asset, venue, threshold, or short period;
- the strategy has unacceptable exchange, custody, liquidation, or operational risk;
- capacity is too low for the intended capital;
- Monte Carlo or bootstrap results show unacceptable drawdown or ruin probability;
- live paper trading cannot reproduce the expected fills and funding payments.

A failed candidate is a successful research outcome. It prevents capital from being allocated to an unverified story.

---

### **tavily research questions**

Research should answer these questions before implementation:

1. What academic evidence measures perpetual funding, basis, leverage, and arbitrage profitability?
2. How do major venues calculate and settle funding, and what historical changes matter?
3. What known risks make funding arbitrage fail during volatility, liquidation cascades, or exchange stress?
4. What data fields are required to reconstruct executable funding and basis returns?
5. What evidence exists for persistence after fees, slippage, borrow, and capital-transfer costs?
6. What are the documented capacity limits and venue concentration risks?
7. Which venues provide sufficiently complete public historical data for an independent study?
8. Which parts of the proposed model are already crowded or likely to have decayed?
9. What alternative explanation could produce an apparent funding-arbitrage return?
10. What minimum paper-trading period and live monitoring metrics are appropriate before any capital is considered?

The Tavily pass adds two explicit research controls:

- Do not use a published annualized funding yield as a return forecast.
- Do not treat a funding threshold as valid until it is independently tested across time, costs, and venue-rule changes.

Search results must be classified as:

- primary academic evidence;
- official venue documentation;
- reliable market-data documentation;
- practitioner evidence;
- anecdotal or promotional material.

Promotional material is not sufficient to validate the mechanic.

---

### **research status and unresolved questions**

The initial research pass is complete using Tavily and supporting source checks. Tavily was restored and four focused research queries were completed. Some generated summaries contained unsupported precision, so only claims traceable to primary papers, official venue documentation, or raw data have been incorporated.

Still unresolved before coding, and who resolves each item:

- **User:** Confirmed Binance Futures and spot availability.
- **Assumption:** Treat the account as a regular Binance user and use a conservative published retail fee assumption. The exact live account tier is not needed for the research pass.
- **Assumption:** Evaluate capacity as a notional sensitivity curve rather than against a personal deployment target.
- **Research:** Download a short BTCUSDT spot and Futures sample from CryptoHFTData and verify that snapshots and incremental updates replay into a continuous book.
- **Research:** Confirm the free API's rate limits, date coverage, file integrity, sequence continuity, and licensing terms.
- **Research:** Test Binance's historical-depth API in parallel, but do not block Level 2 feasibility on Binance whitelist approval.
- **Research:** If CryptoHFTData is incomplete or unsuitable, compare Tardis and Amberdata coverage and cost using the same sample window.
- **Research:** Reconstruct historical fee schedules, funding-interval changes, caps, floors, and contract-rule changes.
- **Research:** Test whether expected funding remains positive after four fills, funding uncertainty, and hedge rebalancing.
- **Research:** Test same-venue hedge, custody, margin, financing, and counterparty assumptions.
- **Research:** Determine whether the observed basis is executable or only a mark-price/index-price difference.
- **Research:** Estimate capacity at multiple notional sizes.

These assumptions are for backtesting only. They do not authorize live trading or imply that the strategy is suitable for the user's account.

The next research deliverable must resolve these questions with venue-specific evidence. Until then, no venue, asset, threshold, or return target is approved.

---

### **definition of done before coding**

No collection or backtest code begins until:

- the research questions have been answered with cited sources;
- venues and instruments have been selected with reasons;
- the data schema and historical availability are confirmed;
- funding formulas and timestamps are understood;
- the cost model is specified;
- entry, exit, and sizing rules are frozen in writing;
- rejection thresholds are registered;
- the known risks and failure modes are documented;
- the first paper-trading design is defined.

The outcome of this document may be approval to code, revision of the hypothesis, or rejection of the candidate.
