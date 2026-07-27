# market edge framework

### **core definition**

- An edge is a persistent statistical asymmetry in expected value derived from a market inefficiency that cannot be instantly arbitraged away.
- It is not a chart pattern, a Volume Profile level, or a moving average crossover.
- If the inefficiency can be removed immediately by capital, speed, or information, it is not a durable edge.

### **three parameters**

- Entry logic clearly defined with no ambiguity.
- Exit logic clearly defined with stop loss, take profit, or time-based exit.
- Position sizing clearly defined with explicit risk.

- The research process starts with the why.
- Who is on the other side of the trade?
- Why are they statistically giving you money?
- Without that answer, you are gambling.

### **simple bits complex**

- Every rule you add is a claim that the future will resemble the past.
- Three rules make three claims.
- Fifteen rules make fifteen claims.
- More rules and more parameters can make the past look better without making the strategy more real.
- Strategies that survive tend to be small, direct, and built around one clear economic reason to exist.

### **the three pillars**

- **Asymmetry of constraint**
  - One side of the trade must be acting for a reason other than maximizing immediate risk-adjusted profit.
  - If both sides are rational, well-capitalized, and equally informed, EV is zero before costs.
  - Real edges come from forced trade, hedging need, operational friction, or severe behavioral bias.

- **Barrier to arbitrage**
  - The inefficiency must survive long enough to matter.
  - The moat is usually one of three things:
    - Capacity
    - Regulatory or legal constraint
    - Technical or infrastructure constraint

- **Positive EV after friction**
  - The edge must remain positive after slippage, fees, and market impact.
  - Mid-price backtests are not enough.
  - If friction kills the edge, the edge was never real.

### **what to look for**

- Stop starting from price.
- Price is the output of the market, not the input.
- Look for the plumbing, the mandates, and the physics of the market.

- **Forced flows**
  - Who must buy or sell regardless of price?
  - Examples: index rebalancing, dealer hedging, corporate buybacks.

- **Frictions and settlement delays**
  - Where does capital move slowly?
  - Examples: tax inefficiencies, settlement lags, withdrawal limits, operational breaks.

- **Data asymmetries**
  - What can you observe, clean, or process better than the consensus?
  - Examples: SEC filing parsing, cleaner tick data, faster alternative data pipelines.

### **where ideas come from**

- Academic research
  - Decades of measurement already exist.
  - Start from what has been studied, then test it with your own pipeline.

- Structure and mechanics
  - Forced flows
  - Rebalances
  - Hedging
  - Participants who must trade

- Behavioral observation
  - Observe first, then interrogate the observation.
  - The observation is the beginning of the work, not the end.
  - Institutions ask why the behavior exists before they call it an edge.

### **how many edges exist**

- Very few true, durable structural edges exist.
- If there were many, they would already be arbitraged away.
- The universe of real mechanics is finite.
- Most retail “edges” fall into one of three buckets:
  - Derivatives of core mechanics
  - Temporary behavioral quirks
  - Pure noise from overfitting

- The universe of real structural mechanics is finite.
- The number is small enough that you can categorize it, but large enough that you should not pretend to know all of it.
- Roughly 10 to 15 core categories is a useful working estimate, not a law.

### **why you will not know all of them**

- The best edges are usually not published.
- Publication accelerates decay.
- Different edges require different capital structures, execution engines, and data pipelines.
- Trying to build for all edges at once creates engineering collapse.
- Extreme secrecy matters.
- The most profitable mechanics are usually guarded by firms that do not publish them.
- Alpha decays once the edge becomes public.
- Mutually exclusive infrastructure makes one universal system unrealistic.

### **the path forward**

- Do not catalog the entire market.
- Find one edge that fits your capital, data, and execution constraints.
- Build the pipeline, validate it, then monitor decay.

- The research process should answer:
  - What is the why?
  - Who is on the other side?
  - What is the moat?
  - Does it survive friction?
  - Does it survive out-of-sample?
  - Does it survive Monte Carlo?

### **data**

- High quality data is non-negotiable.
- Bad data does not announce itself.
- Missing trades, bad ticks, and bad settings corrupt the result.
- Before any test, interrogate the data.
- Ask whether it covers enough markets and whether the provider is reliable.

- Data to collect:
  - Net profit
  - Win rate
  - Average trade
  - Max drawdown
  - Return on drawdown

### **in code**

- The machine must replay the data bar by bar or day by day.
- The code is where the idea becomes executable.
- The machine executes without emotion and without improvisation.

### **analyze**

- Do not stop at whether it made money.
- Ask how it made money.
- Ask when it made money.
- Ask whether the profit is the result of an edge or just luck.

### **strategy families**

- Most ideas will fall into one of these families:
  - Trend following
  - Mean reversion
  - Intraday bias
  - Swing
  - Relative value

- The first question is not whether the idea makes money.
- The first question is which family it belongs to.

### **research pipeline**

- Entry logic must be machine-executable.
- Exit logic must be machine-executable.
- Position sizing must be explicit.
- Validate on unseen data.
- Add Monte Carlo reshuffle and bootstrap tests.
- Reject strategies that only work on one curve.

### **validate**

- The strategy must try to prove that what it found is real.
- Monte Carlo reshuffle reorders the same trades.
- Monte Carlo bootstrap resamples with replacement.
- Tight dispersion across many equity curves is better than one lucky path.
- Use the distribution to estimate:
  - Expected profit
  - Expected loss
  - Expected drawdown
  - Probability of ruin
- If it only looks good in one equity curve, it is probably luck.
- If it fails validation, it goes to the bin.

### **overfitting**

- Overfitting is too many conditions and too much fragility.
- Extra filters and extra parameters learn the past faster than they learn the market.
- The honest test is unseen data.
- Split the data into in-sample and out-of-sample.
- Tune only in-sample.
- Freeze the rules before out-of-sample.
- If it only works on seen data, it is not a real edge.

### **when to say no**

- Set thresholds before the strategy moves forward.
- Decide the maximum drawdown, the minimum profit, and the minimum average trade in advance.
- If the strategy does not meet the threshold, bin it.
- Binning a bad idea is money saved, not money lost.
- A research process that never says no is a permission machine.

### **practical filters**

- **Mandate filter**
  - Is the counterparty forced to trade?

- **Parameter robustness filter**
  - Does the edge survive across a range of values?

- **Friction filter**
  - Does the edge survive realistic trading costs?

- **Capacity filter**
  - Can the edge scale without collapsing?

### **automation**

- Once the strategy is validated, it becomes code.
- The code connects to the broker and executes.
- There is no reason to sit in front of the screen and trade manually.
- It does not question the strategy.
- It does not trade with emotion.

### **monitoring**

- After deployment, the job changes from execution to supervision.
- Compare live behavior to expected behavior.
- Track average trade, drawdown, and win rate against the backtest.
- If live drawdown exceeds the Monte Carlo expectation, pause the strategy.
- If average trade degrades slowly, treat that as possible edge decay.
- Do not wait for the equity curve to fully break before reacting.

### **why not one strategy**

- One strategy will have dead periods.
- Another strategy may work when the first is flat.
- Professionals run multiple models together.
- The goal is not one perfect system.
- The goal is a set of uncorrelated strategies that survive different regimes.

### **infrastructure vs process**

- Infrastructure matters, but it is not the edge itself.
- What transfers is the process.
- What transfers is the why and the pipeline.
- What transfers is the Monte Carlo discipline.
- What transfers is volatility-based sizing and automated execution.

### **working conclusion**

- A real edge is a constraint, a moat, and positive EV after friction.
- Behavioral patterns can be tradable, but they are not the same as forced-flow mechanics.
- The job is not to prove every edge exists.
- The job is to find one that survives reality.
