### **index rebalancing price pressure research specification**

**Status:** Pre-research specification (Level 1 not yet implemented)

**Classification:** Candidate mechanic / Regulatory & mandate constraints / Passive flow inelasticity

**Purpose:** Define the research question, evidence requirements, data, execution assumptions, and rejection gates before writing collection or backtest code.

---

### **the research question**

Can the forced, schedule-driven flow of index-tracking funds around index additions and deletions create a post-effective-date price reversal large enough to survive realistic friction (spread, slippage, borrow cost, commissions, capacity)?

This is a hypothesis. It is not yet an edge, strategy, or approval to trade.

The first implementation targets U.S. small- and mid-cap indices where the documented effect is largest and least decayed. The exact indices, historical window, and thresholds must be chosen only after data access and historical constituent coverage are verified.

---

### **the market and instruments**

- **Asset class:** U.S. equities
- **Primary underlying:** Index constituents of U.S. equity indices, primarily S&P SmallCap 600 and S&P MidCap 400, with Russell 2000 as a secondary venue
- **Signal source:** Publicly announced index additions and deletions (S&P DJI press releases, FTSE Russell reconstitution lists) with announcement and effective dates
- **Execution instrument:** The constituent stocks themselves
- **Strategy family:** Relative value / mean reversion / event-driven
- **Initial horizon:** 10 to 60 trading days after the effective date
- **Excluded initially:** S&P 500 (documented decay of the effect), Russell Microcap (liquidity), M&A/spin-off-driven changes (different mechanics), IPOs (insufficient price history), shorting where borrow is unavailable, and multi-strategy portfolios

The word rebalancing in this document refers to the scheduled, rules-based addition and deletion of constituents from widely tracked indices. It is not discretionary portfolio rebalancing.

---

### **the proposed mechanic**

Index-tracking funds, ETFs, and benchmarked active funds must align their holdings with the published index composition. When a stock is added to an index, index funds are forced to buy it; when it is deleted, they are forced to sell it — regardless of price. The academic literature (Gabaix and Koijen, 2021; Pavlova and Sikorskaya, 2023) shows this demand is highly inelastic, meaning the forced flow moves prices beyond fair value.

The candidate trades are:

- **Long deletions:** buy stocks deleted from an index shortly after the effective date, when the forced selling has stopped, and hold through the documented reversal period.
- **Short additions:** short stocks added to an index shortly after the effective date, when the forced buying has stopped, and cover through the documented reversal period.
- **Additions/deletions spread:** combine both legs where borrow is available and economical.

The position is not automatically profitable. It may still have directional beta risk, borrow cost risk, announcement-window slippage, event-specific noise, and capacity constraints.

---

### **research findings**

The literature and documentation pass produces the following conclusions:

- **The mechanism is real and heavily documented.** Shleifer (1986) documents a permanent +2.79% abnormal return for S&P 500 additions; Harris and Gurel (1986) find the price pressure is temporary and fully reverses. The two views anchor a forty-year debate: demand curves for stocks are downward-sloping (Shleifer, 1986; Kaul, Mehrotra, and Morck, 2000; Wurgler and Zhuravskaya, 2002) versus pure price pressure (Harris and Gurel, 1986).
- **The deletion side is the asymmetric opportunity.** Chen, Noronha, and Singal (2004) document that additions to the S&P 500 earn permanent positive abnormal returns while deletions suffer temporary negative returns: deletions lose about -14% on average, and the loss disappears completely within 60 days after the effective date. This asymmetry is the core of the trade.
- **The post-rebalance reversal is large.** Arnott, Brightman, Kalesnik, and Wu (2023) show additions outperform by 46.5% in the 12 months before the trade date while deletions lag by 36.3%; in the year after, deletions outperform additions by more than 20%, with the lion's share coming from the deletion side. Sui (2006) measures the short-horizon reversal: -2.3% for additions and +4.9% for deletions over 20 days after the effective date.
- **Modern micro evidence confirms the reversal is fast and mechanical.** A practitioner study covering 3,488 additions and 2,517 deletions across ten U.S. indices from 2014 to 2023 (including S&P 500, S&P 400, S&P 600, Russell 1000/2000) finds prices move adversely by more than 4% over the 20 trading days leading into reconstitution, with a reversal of -5.7% in the following month. On reconstitution day itself, additions are pushed up about 9 bps between 4:00 p.m. and the close and reverse -13 bps by the next open; deletions are pushed down 30 bps and reverse +63 bps by the next open.
- **The effect has decayed in the S&P 500 but persists in small caps.** Bennett, Stulz, and Wang (2022, "The Disappearing Index Effect") document that the S&P 500 inclusion effect has fallen from about +4.6% in the 1980s to roughly zero in the 2010s; deletions moved from -16.1% (1990s) and -12.4% (2000s) to -0.6% (2010s). S&P DJI's own research (Preston and Soe, 2021) reaches the same conclusion. The effect is most concentrated in indices with smaller, less liquid constituents: reconstitution-day volume pressure is about 112x normal for the S&P 600 and 120x for the Russell 2000 (2014-2023 sample).
- **The flow is inelastic and schedule-driven.** Pavlova and Sikorskaya (2023) build a benchmarking-intensity (BMI) measure and find a 1% increase in BMI raises June returns by 27 bps; the top BMI-change quartile earns about +80 bps in June while the bottom quartile earns about -110 bps. Chang, Hong, and Liskovich (2015) use the Russell 1000/2000 cutoff and find inclusion effects of roughly 20% in the reconstitution month at the margin. Gabaix and Koijen (2021) provide the theoretical foundation: one dollar of inelastic buying moves prices by about five dollars.
- **The timing of the effect has shifted earlier.** Arnott et al. (2023) and a recent event study (Aalto) both find that a large share of the impact has moved from the effective date to the announcement window as front-running has increased. This means the entry point must be defined relative to the effective date, and the announcement-to-effective drift must not be double-counted as post-reversal alpha.
- **Discretionary deletions are the right population.** Arnott et al. (2023) emphasize that the reversal is driven by discretionary deletions (market-cap-driven removals), not by deletions caused by M&A, bankruptcy, or delisting, which carry fundamentally different information. The study must filter on the reason for the change.
- **Borrow cost and liquidity are the binding constraints.** Mean loan fees are about 85 bps per year for the average stock, but the 90th percentile is 189 bps for micro caps and 20 bps for large caps, with the 99th percentile reaching 1,119 bps for micro caps (Reed, 2018). Small-cap additions can be expensive or impossible to borrow. The short side of the trade must therefore be filtered on borrow availability, and the long-deletions side is the cheaper and more robust direction.
- **Capacity is limited but non-trivial.** The Russell 2000 rebalance moved an estimated $114.7 billion in NYSE and $102.5 billion in Nasdaq volume in the closing moments of June 2025 (LSEG). The tradable edge is the reversal of that flow, which is spread across hundreds of small-cap names; capacity is bounded by each name's daily volume and borrow availability, not by index-level volume.

The research changes the working hypothesis from:

> Index additions are expensive and deletions are cheap.

to:

> The forced, inelastic flow around index changes creates temporary price pressure that partially reverses after the effective date, and the reversal in small-cap deletions may survive friction while the S&P 500 version has decayed to zero.

---

### **version-one research scope**

The evidence supports the following provisional scope:

- **Primary research venue:** S&P SmallCap 600 (SIPC) and S&P MidCap 400 (MID) additions and deletions, announced via S&P DJI press releases with free historical archives.
- **Secondary venue:** Russell 2000 additions and deletions via FTSE Russell reconstitution lists (annual, ~200-250 names per year, largest documented flow; requires verifying free historical list availability).
- **Signal source:** Publicly announced additions/deletions with announcement date and effective date, filtered to discretionary changes only.
- **Execution proxy:** The constituent stocks themselves (long deletions) and, where borrow is available, short additions.
- **Direction:** Long deletions primary; short additions and the combined spread tested separately and reported separately.
- **Excluded from version one:** S&P 500 changes (decayed effect), M&A/bankruptcy/spin-off-driven changes, IPOs with less than one year of price history, micro-cap names below a liquidity threshold, and any leg where borrow is unavailable.
- **Research objective:** Determine whether the post-effective-date reversal in small-cap index deletions (and additions) survives executable costs, borrow fees, and a frozen set of rules.
- **Event handling:** Entry is defined relative to the effective date, not the announcement date, so the announcement-to-effective drift is never captured as part of the trade.
- **First-pass design:** Daily event-study design with buy-and-hold windows of 10, 20, 40, and 60 trading days after the effective date.

This is a research scope, not a trading approval.

---

### **implementation status**

The index-rebalancing research scaffold is not yet implemented. This document is the pre-coding specification.

- The SPX GEX candidate was rejected at Level 1 (friction gate) and recorded separately.
- The funding-basis candidate was rejected under current assumptions and recorded separately.
- This document defines the next mechanic to investigate: index rebalancing price pressure.

The first study has two data-fidelity levels:

- **Level 1, event-study feasibility:** Use publicly announced addition/deletion lists, announcement/effective dates, daily OHLCV bars for constituents, and conservative friction assumptions. This tests whether the documented post-reversal survives current data and costs.
- **Level 2, executable replay:** Add intraday bars, borrow-cost data, short-availability data, and full capacity modeling. This is required before making claims about live executable capacity or deployment.

Level 1 cannot be described as a full executable backtest. Level 2 is the required standard for any final positive conclusion.

---

### **level-one data acquisition plan**

The search identified the following practical data routes:

1. **S&P DJI press releases (free, primary route)**
   - S&P Dow Jones Indices publishes a press release for every addition/deletion to the S&P 500, S&P MidCap 400, and S&P SmallCap 600, typically two weeks before the effective date, with the effective date, tickers, and GICS sector in the release.
   - Announcement and effective dates are recoverable from the press-release archive: https://press.spglobal.com and historical PRNewswire archives.
   - This is the primary route because announcement dates are needed to avoid look-ahead and because the small-cap effect is the documented survivor.

2. **Historical S&P change tables (free, secondary)**
   - Wikipedia's "List of S&P 500 companies" includes a full change history with effective dates and reasons; mirror tables exist for the S&P 400 and S&P 600.
   - Tickerleague maintains additions/removals tables with effective dates and reason categories (market cap, M&A, spin-off) for S&P 500; the S&P 400/600 equivalents require scraping.
   - These are acceptable for cross-validation of effective dates and reasons, not as the primary source, because announcement dates are not consistently recorded.

3. **FTSE Russell reconstitution lists (free, secondary venue)**
   - FTSE Russell publishes preliminary additions/deletions lists in late May and final lists in June for the Russell US Indexes, effective after the close of the fourth Friday of June.
   - Current-year lists are free on lseg.com; historical lists require archive retrieval (archive.org) or a licensed LSEG product.
   - Used for the Russell 2000 secondary venue only if historical lists can be verified.

4. **Databento US Equities Mini (EQUS.MINI)**
   - Provides historical top-of-book US equities data (ohlcv-1m schema) starting 2023-03-28, including small-cap symbols subject to coverage verification.
   - Coverage of S&P 600 / S&P 400 / Russell 2000 constituents must be verified by sampling before the study window is set.
   - If EQUS.MINI does not cover the required small-cap universe, Databento US Equities (EQUS) or another licensed daily-price source is required; this changes cost assumptions and must be resolved before coding.

5. **yfinance / free daily sources (rejected for the core study)**
   - Free daily price endpoints introduce survivorship and completeness risk for delisted names and do not meet the spec's data-integrity requirements. Acceptable only for pilot parsing tests, not for the result.

The acquisition sequence is:

- Verify EQUS.MINI coverage of S&P 600 and S&P 400 constituents for 2023-2026.
- Verify that the S&P DJI press-release archive provides announcement dates for the study window.
- Build the addition/deletion event table with announcement date, effective date, ticker, index, and reason category.
- Validate the event table against Wikipedia and tickerleague for the same window.
- Download constituent OHLCV bars for the event windows.
- If the Russell 2000 is included, verify historical reconstitution list availability; otherwise drop the secondary venue.

---

### **source register**

#### **Academic and research sources**

- [Shleifer, A. (1986). Do Demand Curves for Stocks Slope Down? The Journal of Finance, 41(3), 579-590](https://www.jstor.org/stable/2328497) — the founding study: permanent +2.79% on S&P 500 additions, downward-sloping demand curves.
- [Harris, L. and Gurel, E. (1986). Price and Volume Effects Associated with Changes in the S&P 500 List. The Journal of Finance, 41(4), 815-829](https://www.jstor.org/stable/2328230) — the price-pressure view: temporary effect that fully reverses.
- [Kaul, A., Mehrotra, V., and Morck, R. (2000). Demand Curves for Stocks Do Slope Down: New Evidence from an Index Weights Adjustment. The Journal of Finance, 55(2), 893-912](https://randallmorck.ca/wp-content/uploads/2020/02/69-demand-curves-for-stocks-do-slope-down.pdf) — TSE index-weights adjustment confirms permanent price impact.
- [Wurgler, J. and Zhuravskaya, E. (2002). Does Arbitrage Flatten Demand Curves for Stocks? The Journal of Finance, 57(2), 875-908](https://onlinelibrary.wiley.com/doi/abs/10.1111/1540-6261.00443) — arbitrage risk limits the flattening of demand curves.
- [Chen, H., Noronha, G., and Singal, V. (2004). The Price Response to S&P 500 Index Additions and Deletions: Evidence of Asymmetry and a New Explanation. The Journal of Finance, 59(4), 1901-1930](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2004.00683.x) — the asymmetry: additions permanent, deletions temporary (~-14%, gone within 60 days).
- [Beneish, M. and Whaley, R. (1996). An Anatomy of the "S&P Game": The Effects of Changing the Rules. The Journal of Finance, 51(5), 1909-1930](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1996.tb05227.x) — front-running around the switch from at-close to advance announcement.
- [Lynch, A. and Mendenhall, R. (1997). New Evidence on Stock Price Effects Associated with Changes in the S&P 500. Journal of Business, 70(3), 351-383](https://www.jstor.org/stable/2353224) — expectation effects around index changes.
- [Chang, Y., Hong, H., and Liskovich, I. (2015). Regression Discontinuity and the Price Effects of Stock Market Indexing. The Review of Financial Studies, 28(1), 212-246](https://ideas.repec.org/a/oup/rfinst/v28y2015i1p212-246..html) — Russell 1000/2000 cutoff, ~20% reconstitution-month inclusion effect at the margin, strong deletion effect.
- [Pavlova, A. and Sikorskaya, T. (2023). Benchmarking Intensity. The Review of Financial Studies, 36(3), 859-903](https://lbsresearch.london.edu/id/eprint/2495) — inelastic benchmarked demand: 1% BMI change -> 27 bps June return; top quartile +80 bps, bottom quartile -110 bps.
- [Gabaix, X. and Koijen, R. (2021). In Search of the Origins of Financial Fluctuations: The Inelastic Markets Hypothesis. Swiss Finance Institute / SSRN](https://www.nber.org/system/files/working_papers/w28967/w28967.pdf) — one dollar of inelastic buying moves prices by about five dollars.
- [Arnott, R., Brightman, C., Kalesnik, V., and Wu, L. (2023). Earning Alpha by Avoiding the Index Rebalancing Crowd. Financial Analysts Journal, 79(2), 76-97](https://www.tandfonline.com/doi/full/10.1080/0015198X.2023.2173506) — the reversal: deletions outperform additions by >20% in the year after; the effect has shifted to the announcement window; discretionary deletions drive the reversal.
- [Bennett, B., Stulz, R., and Wang, Z. (2022). The Disappearing Index Effect. Harvard Business School / NBER](https://www.hbs.edu/ris/Publication%20Files/23-025_563e45c6-df92-4d9c-ae05-608d4d0acab1.pdf) — the S&P 500 index effect has decayed to ~zero in the 2010s; deletion effect fell from -16.1% (1990s) to -0.6% (2010s).
- [Patel, N. and Welch, I. (2017). Extended Stock Returns in Response to S&P 500 Index Changes. The Review of Asset Pricing Studies, 7(2), 172-208](https://academic.oup.com/raps/article-abstract/7/2/172/3065557) — the addition effect moderated but stayed positive in later samples.
- [Preston, H. and Soe, A. (2021). What Happened to the Index Effect? A Look at Three Decades of S&P 500 Adds and Drops. S&P Dow Jones Indices](https://www.spglobal.com/spdji/en/documents/research/research-what-happened-to-the-index-effect.pdf) — index-provider evidence of the decaying effect.
- [Pavlova, A. and Sikorskaya, T. (2023). Benchmarking Intensity — Presentation, Q-Group](https://www.q-group.org/resources/Documents/Spring%202023%20Presentations/Anna%20Pavlova%20Presentation.pdf) — summary of the BMI methodology and magnitudes.
- [Greenwood, R. (2005). Short- and Long-Term Demand Curves for Stocks: Theory and Evidence on the Dynamics of Arbitrage. Journal of Financial Economics, 75(3), 607-649](https://www.sciencedirect.com/science/article/abs/pii/S0304405X04001583) — Nikkei 225 rebalancing, temporary price pressure and its reversal.
- [Madhavan, A., Ribando, J., and Udevbulu, N. (2022). Demystifying Index Rebalancing: An Analysis of the Costs of Liquidity Provision. Journal of Portfolio Management, 48(6), 171-184](https://www.pm-research.com/content/iijpormgmt/48/6/171) — liquidity-provision costs of index rebalancing.
- [Reed, A. (2018). Short-Selling Risk. UNC / SSRN](https://uncipc.org/wp-content/uploads/2017/06/Reed_2018-11wp.pdf) — loan-fee distribution: mean 85 bps; 90th percentile 189 bps micro / 20 bps large; 99th percentile 1,119 bps micro / 236 bps large.
- [Aalto University (2024). The Impact of Index Reconstitutions (event study)](https://aaltodoc.aalto.fi/bitstreams/f46535bc-1044-453b-8d99-b1ac977b1761/download) — modern sample: short-term effects have diminished and the timing shifted from effective date to announcement date; long-term deletion reversals emerge and intensify.

#### **Official venue and data sources**

- [S&P Dow Jones Indices press releases](https://press.spglobal.com) — official announcement and effective dates for S&P 500/400/600 changes.
- [S&P DJI: Marvell and Flex Set to Join S&P 500; Others to Join S&P MidCap 400 and S&P SmallCap 600 (June 2026)](https://www.prnewswire.com/news-releases/marvell-technology-and-flex-set-to-join-sp-500-others-to-join-sp-midcap-400-and-sp-smallcap-600-302793159.html) — example release format: effective date, ticker, GICS sector, index.
- [Wikipedia: List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) — full S&P 500 change history with effective dates and reasons.
- [Tickerleague: S&P 500 additions and removals](https://tickerleague.com/indices/stock/sp-500/additions-and-removals) — additions/removals with effective dates and reason categories.
- [LSEG: Russell Reconstitution](https://www.lseg.com/en/ftse-russell/russell-reconstitution) — official reconstitution process, preliminary/final list dates, effective date (fourth Friday of June), and reconstitution-day volume ($114.7B NYSE + $102.5B Nasdaq, June 2025).
- [LSEG: 2026 Russell US Indexes reconstitution summary](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/other/2026-russell-us-indexes-reconstitution-summary.pdf) — 2026 summary: 244 companies joining the Russell 2000, banding applied, effective after June 26 close.
- [Cboe: The 32nd Annual Russell Index Reconstitution Explained (2020)](https://www.cboe.com/insights/posts/the-32nd-annual-russell-index-reconstitution-explained) — process detail: ~12% annual turnover, ~235 stocks added/deleted since 2008, $2.4T benchmarked to the Russell 2000.
- [FTSE Russell: Russell US Indexes Construction and Methodology](https://www.lseg.com/en/ftse-russell/indices/russell-us) — official methodology for ranking, banding, and reconstitution.
- [Databento: US Equities Mini](https://databento.com/blog/databento-us-equities-mini-now-available) — EQUS.MINI dataset, historical data from 2023-03-28, top-of-book composite, ohlcv-1m support; small-cap coverage requires verification.
- [Databento: Equities market data](https://databento.com/equities) — EQUS.MINI vs full US Equities coverage and pricing.
- [Alpha Architect: Adverse Effects of Index Replication (2024)](https://alphaarchitect.com/cost-of-index-rebalancing) — 2014-2023 practitioner study of 3,488 additions and 2,517 deletions across ten indices: >4% adverse move in the 20 days before reconstitution, -5.7% reversal in the next month; 112x (S&P 600) and 120x (Russell 2000) reconstitution-day volume.

These sources support the research design but do not prove that the candidate is profitable.

---

### **the why and the counterparty**

The candidate source of return is not the direction of the market. The proposed source is the interaction between:

- index-tracking funds and ETFs that must align holdings with the published index composition;
- benchmarked active funds that rebalance toward the new composition for tracking-error reasons (Pavlova and Sikorskaya, 2023);
- the inelasticity of that flow: it is schedule-driven and price-blind (Gabaix and Koijen, 2021);
- the temporary nature of the price distortion: once the forced flow stops at the effective date, prices partially revert (Chen, Noronha, and Singal, 2004; Arnott et al., 2023; Alpha Architect, 2024).

The likely counterparties are passive index funds, ETFs, and benchmarked active funds that must transact on the schedule regardless of price. They give up the post-reversal return because their mandate requires tracking the new composition; the arbitrage barrier is capacity (small-cap liquidity), borrow availability on the short side, and the event cadence.

The hypothesis fails conceptually if the observed result is primarily look-ahead (using constituents before announcement), M&A-driven noise, a hidden size or value factor tilt, or the announcement-to-effective drift mislabeled as post-reversal alpha.

---

### **what must be established before coding**

1. Confirm the exact indices to test first: S&P SmallCap 600 and S&P MidCap 400, with Russell 2000 as a secondary venue pending list availability.
2. Confirm that announcement dates, effective dates, tickers, and reason categories can be recovered without look-ahead for the study window.
3. Confirm Databento EQUS.MINI coverage of the S&P 600 / S&P 400 / Russell 2000 constituents, including delisted names.
4. Confirm the friction model for small-cap execution: spreads, slippage, per-share commissions, SEC fee, and borrow cost for the short leg.
5. Define the entry rule precisely relative to the effective date (e.g., open of the first trading day after the effective date).
6. Define the holding windows (10, 20, 40, 60 trading days) and the benchmark for abnormal returns.
7. Identify survivorship, timestamp, and reason-classification risks in the event table.
8. Freeze the entry, exit, and sizing rules before any out-of-sample test.

---

### **required data**

#### **Event data**

- Index (S&P 600, S&P 400, Russell 2000, or control: S&P 500)
- Ticker and company name
- Announcement date
- Effective date
- Action (addition or deletion)
- Reason category (market-cap / discretionary vs M&A / bankruptcy / spin-off)
- Weight in the index if available

#### **Underlying market data**

- Timestamp in UTC or market-local trading time
- Open, high, low, close (daily minimum; intraday at Level 2)
- Volume
- Bid and ask where available
- Regular trading hours only
- Delisted, merged, and bankrupt names included (no survivorship bias)

#### **Cost and operational data**

- Fee schedule and spread assumptions per market-cap tier
- Borrow availability and loan-fee history for the short leg where available
- Liquidity and capacity metrics (ADV, float)
- Corporate actions during the holding window (splits, dividends, delistings)

#### **Friction model**

- Slippage per side, modeled conservatively and per market-cap tier
- Per-share commission assumption
- SEC Section 31 fee
- Borrow cost for short additions, with a hard-to-borrow filter
- A stress case with widened spreads and forced exits

---

### **data validation**

Before calculating a return:

- Normalize timestamps and verify ordering.
- Reconcile the event table against at least two independent sources (S&P DJI releases vs Wikipedia vs tickerleague).
- Verify that announcement dates are consistent with press-release history; drop any event without a verifiable announcement date from the core study.
- Detect missing, duplicated, stale, and out-of-order price observations.
- Verify that each trade uses only information available before the decision time (the effective date close).
- Keep raw data immutable and store cleaning decisions separately.
- Record the data source, retrieval time, version, and known limitations.

---

### **minimum machine-executable model**

The first model must be deliberately simple.

#### **Signal**

At the effective date close, build the event set from the publicly announced addition/deletion lists:

- additions to the S&P 600 / S&P 400 (short leg, borrow permitting)
- deletions from the S&P 600 / S&P 400 (long leg)
- reason category = discretionary / market-cap only; M&A, bankruptcy, and spin-off events are excluded
- minimum liquidity filter: average daily dollar volume above a pre-registered threshold
- minimum price history: one year of trading before the event

#### **Entry condition**

Enter at the open of the first trading day after the effective date, once the forced flow has stopped:

- Long deletions: buy the deleted stock at the first open after the effective date.
- Short additions: short the added stock at the first open after the effective date, only if borrow is available at a fee below the pre-registered cap.

#### **Exit conditions**

Exit when any of the following occurs:

- the planned holding window ends (10, 20, 40, or 60 trading days, tested as a parameter range);
- the stock is delisted or acquired during the window (force close and record the event);
- a pre-registered stop loss is hit.

#### **Position sizing**

Size from the lower of:

- predefined portfolio risk budget;
- a volatility target per event (equal-risk-weight across events);
- available executable depth in the stock.

Do not size from the expected reversal magnitude alone.

---

### **cost model**

The backtest must include:

- entry and exit spread crossing per name;
- per-share commission on both legs;
- SEC Section 31 fee;
- slippage modeled conservatively per market-cap tier (base case 1.5 bps per side per the registered model; stress case 10 bps per side for S&P 600 names);
- borrow cost for the short leg, annualized over the holding window, with a hard-to-borrow filter and a pre-registered fee cap;
- a capacity sweep at multiple notional sizes.

No result is valid if it uses mid-price fills while claiming an executable edge.

---

### **validation plan**

#### **Economic validation**

- Explain the return decomposition: reversal alpha vs size/value factor tilt vs announcement-drift contamination.
- Verify that the strategy is not profitable only because of a hidden size or value tilt; benchmark against size-matched controls.
- Compare long-deletions, short-additions, and the spread separately; never report a combined number that hides a weak leg.

#### **Statistical validation**

- Split data into in-sample and out-of-sample periods by year.
- Freeze the rules before out-of-sample evaluation.
- Use walk-forward testing across annual reconstitutions.
- Test multiple indices (S&P 600, S&P 400, and Russell 2000 if available) without selecting only successful examples.
- Test a reasonable range of holding windows and liquidity thresholds.
- Use Monte Carlo trade reshuffling to study sequence risk.
- Use bootstrap resampling to estimate drawdown, expected outcomes, and ruin probability.

#### **Robustness validation**

The result must not depend on:

- one index;
- one year;
- one holding window;
- one liquidity threshold;
- one fee assumption;
- one favorable execution assumption;
- one exceptional event (e.g., a single large deletion).

#### **Capacity validation**

- Replay the strategy at several notional sizes.
- Measure spread, depth, market impact, and fill degradation.
- Determine the capital level at which net return materially deteriorates.
- Treat that level as a capacity estimate, not as an optimization target.

---

### **rejection gates**

Reject the candidate if any of the following is true:

- the post-effective-date reversal does not survive the conservative friction model (registered base case);
- the reversal disappears or inverts out of sample;
- the result depends on S&P 500 changes only (the decayed venue) or on a single year;
- the event table cannot be reconstructed without look-ahead or with unverifiable announcement dates;
- borrow costs for the short leg exceed the short-side edge after the hard-to-borrow filter;
- the long-deletions leg alone is not profitable after friction (the primary direction);
- Monte Carlo or bootstrap results show unacceptable drawdown or ruin probability;
- capacity is too low for the intended capital;
- live paper trading cannot reproduce the expected fills and reversal.

A failed candidate is a successful research outcome. It prevents capital from being allocated to an unverified story.

---

### **tavily research questions**

Research should answer these questions before implementation:

1. What is the current magnitude of the post-rebalance reversal in S&P 600 / S&P 400 / Russell 2000 after the documented decay in the S&P 500?
2. Which academic papers measure the asymmetry between additions and deletions, and which mechanism explains it?
3. What is the exact timeline from announcement to effective date for each index, and how has it changed?
4. What is the role of borrow cost and short availability in the short-additions leg?
5. What data is required to reconstruct the event table without survivorship bias?
6. What is the evidence for capacity limits and venue concentration in this trade?
7. Which parts of the model are already crowded or likely to have decayed?
8. What alternative explanation could produce an apparent post-reversal return?
9. What minimum paper-trading period and live monitoring metrics are appropriate before any capital is considered?

Search results must be classified as:

- primary academic evidence;
- official index-provider documentation;
- reliable market-data documentation;
- practitioner evidence;
- anecdotal or promotional material.

Promotional material is not sufficient to validate the mechanic.

---

### **research status and unresolved questions**

The initial research pass is complete. The mechanism is heavily documented in the academic literature, the decay in the S&P 500 is documented, and the small-cap survivor venues are identified.

Still unresolved before final validation, and who resolves each item:

- **Research:** Verify Databento EQUS.MINI coverage of S&P 600 and S&P 400 constituents, including delisted names, for 2023-2026.
- **Research:** Verify that S&P DJI press-release archives provide announcement dates for the study window.
- **Research:** Verify FTSE Russell historical list availability for the Russell 2000 secondary venue; drop the venue if lists cannot be recovered.
- **Research:** Reconstruct historical borrow-fee data or, failing that, model borrow as a conservative stress assumption with a hard-to-borrow filter.
- **Research:** Determine whether the observed reversal is executable or only a mark-to-market artifact of the index effect literature.
- **Research:** Estimate capacity at multiple notional sizes for the long-deletions leg.

### **current known limitations**

- No historical borrow-fee dataset is confirmed for the short-additions leg; borrow cost will be modeled as a stress assumption until data is verified.
- Historical FTSE Russell list availability is unverified; the Russell 2000 venue may be dropped at Level 1.
- EQUS.MINI small-cap coverage is unverified; the study window and universe depend on this check.
- The effect has demonstrably decayed in the S&P 500; version one deliberately excludes it.

These assumptions are for backtesting only. They do not authorize live trading or imply that the strategy is suitable for any account.

The next research deliverable must resolve these questions with venue-specific evidence. Until then, no venue, index, threshold, or return target is approved.

---

### **definition of done before coding**

No collection or backtest code begins until:

- the research questions have been answered with cited sources;
- venues and indices have been selected with reasons;
- the event-table schema and historical availability are confirmed;
- the announcement-to-effective timeline is understood for each index;
- the cost model is specified, including borrow;
- entry, exit, and sizing rules are frozen in writing;
- rejection thresholds are registered;
- the known risks and failure modes are documented;
- the first paper-trading design is defined.

The outcome of this document may be approval to code, revision of the hypothesis, or rejection of the candidate.

### **current decision**

The index-rebalancing price-pressure candidate is approved for Level-1 research preparation, subject to the three data verifications above (EQUS.MINI small-cap coverage, S&P DJI announcement-date archive, FTSE Russell historical lists). The primary direction is long small-cap deletions after the effective date, with short additions tested separately under borrow constraints. The S&P 500 venue is excluded due to documented effect decay.
