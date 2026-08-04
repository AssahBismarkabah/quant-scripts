### **share repurchase (buyback) timing research specification**

**Status:** Pre-research specification (deep dive in progress, 2026-08-04)
**Classification:** Candidate mechanic / Structural forced-flow + data asymmetry / Mandate & legal-constraint category (Category 4: behavioral/regulatory overlay on Category 2 mandate)
**Supersedes/extends:** Selected as the #1 testable candidate from `IA/structural-edge-survey-2025-2026.md`. This document is the research + pre-registration spec for that candidate, written before any collection or backtest code.
**Purpose:** Define the research question, the evidence, the data, the execution assumptions, and the rejection gates before writing code — exactly as the funding-basis spec did for its candidate.

---

### **the research question**

Can we identify, from public data, the windows and names where **open-market share-repurchase execution** provides predictable, positive expected-value demand support (the "buyback put"), and does that support produce a tradable positive return after friction and after adjusting for systematic market exposure?

This is a hypothesis. It is not yet an edge, strategy, or approval to trade.

The core claim is **conditional**: using the 10b5-1 plan signal (adopted in advance, disclosed near-real-time after the 2022 rule amendments) and the documented regularity that firms repurchase **after price declines** and **during undervaluation windows**, we can anticipate buyback-bid demand on specific names/periods, and that demand reduces downside and lifts forward returns beyond what beta/momentum would predict.

---

### **the market and instruments**

- **Asset class:** US single-stock equities (S&P 500 and S&P 600 / small-cap universe, where the effect is strongest per ILV 1995 and the CFA review).
- **Primary execution proxy:** the stock itself (we are long the repurchasing issuer; there is no separate derivative needed for the base case).
- **Signal inputs:** SEC EDGAR (Form 8-K / 10b5-1 adoption+termination; Form 10-Q/10-K daily buyback exhibits; Form 4 insider trades), corporate-action calendar, daily OHLCV bars.
- **Strategy family:** Mean reversion / price-support around a structural forced-flow (companies repurchasing for non-price reasons).
- **Initial horizon:** days-to-weeks (the documented repurchase program windows average ~16 months; the actionable horizon is event-driven from 10b5-1 cooling-off logic and post-decline clusters).
- **Excluded initially:** Options (except as noted for capacity), leveraged directional bets, shorting, non-US issuers, and any reliance on non-public or paid intraday data.

---

### **the proposed mechanic (the why)**

**Counterparty / who is on the other side:** The repurchasing **corporation itself**. A firm executing an open-market or 10b5-1 buyback is a price-insensitive, mandate-driven buyer: it has committed capital to reduce share count (pay out cash, offset dilution, signal undervaluation) and its execution desk is **not optimizing against us** — it is fulfilling a repurchase program. This satisfies the asymmetry-of-constraint pillar better than most: the counterparty's objective (return capital, support price, avoid EPS dilution) is not to maximize short-term profit against us.

Selective, evidence-based mechanics:

1. **Buyback execution is a genuine forced/constrained flow (Category 2 mandate overlap).** Rule 10b-18 gives a safe harbor for open-market repurchases if the issuer obeys volume/timing constraints (e.g. not the opening or closing 30 minutes; ≤25% of the trailing four-week average daily volume per day); Rule 10b5-1 plans commit the issuer to a schedule. The issuer *must* buy on its plan (10b5-1) or per its authorized program, and it buys even when the price is falling — because repurchasing after declines is exactly the documented behavior (Stephens & Weisbach 1998; Peyer & Vermaelen 2009; Dittmar 2000).

2. **The effect is strongest after price declines and in undervaluation windows.** ILV (1995): announcement CAR(-2,+2) ~3.5%, 4-yr BHAR ~+12.1%, concentrated in value firms. SW (1998): firms actually acquire 74-82% of announced targets within 3 years and repurchase more after negative returns. Busch & Obernberger (2016): average program ~16 months; repurchase *execution* (not just announcement) is followed by positive abnormal returns — the execution itself contains information.

3. **Execution provides price support ("buyback put").** Cook et al. (2004): OMR execution narrows spreads and reduces the price impact of order imbalances — i.e. it cushions downside. McNally et al.: repurchases offer price support in turbulence. Li & Swanson (2016, JCF): firms *increase* repurchases for price-support motives. Chee (2022): repurchase intensity affects price delay. Elm Wealth (2026) quantifies: ~$1.5T/yr buybacks ≈ ~$6B/day buying ≈ ~0.5% of daily volume.

4. **The 10b5-1 signal gives forward predictability with a documented lockout window.** Since the SEC 2022 amendments (finalized Dec 2022, effective Feb 2023), a company (issuer) adopting a 10b5-1 plan to repurchase its stock must observe a **cooling-off period of 30 days** (codified) before buyback trading may begin; directors/officers face a 120-day cooling-off and quarterly-report disclosures. The adoption/termination of 10b5-1 plans is now disclosed on Form 8-K/10-Q/10-K and in proxy/annual statements. **This is a near-real-time, non-lagged signal:** when a firm announces a 10b5-1 buyback plan, we know repurchase buying is scheduled to begin ~30 days later and continue on a formula (price/date) — a genuine forward predictor, unlike the lagged quarterly 10b-18 daily tables.

5. **The data asymmetry is cheap and already in our pipeline.** EDGAR parsing (Form 10b5-1 adoption via 8-K; daily buyback exhibits; Form 4) is free and machine-readable with our existing `requests`/`pdfplumber` stack.

**The hypothesis fails conceptually if** the measured support is just low-beta/value/momentum exposure (the beat-random confound that killed vol-fade), if the effect has fully decayed post-2001 (documented in the CFA lit review and a 2019 JCF study), if the 10b5-1 signal is too sparse/announced after the fact to trade, or if the repurchase support is a permanent repricing rather than temporary impact.

---

### **research findings (deep dive)**

**Academic–general (announcement returns and long-run):**
- Ikenberry, Lakonishok & Vermaelen (1995), *Market underreaction to open market share repurchases*, JFE 39(2-3):181-208 — 1980-90, 1,239 OMRs; CAR(-2,+2) ~3.5%; 4-yr BHAR ~+12.1%, concentrated in value/undervalued firms.
- Stephens & Weisbach (1998), *Actual share reacquisitions in open-market repurchase programs*, JF 53:313-333 — 1981-90, 450 programs; firms acquire 74-82% of target within 3 yrs; repurchase **increases after negative stock returns**; repurchase activity is negatively related to prior-quarter returns.
- Grullon & Michaely (2002), *Dividends, share repurchases, and the substitution hypothesis*, JF 57:1649-1684 — repurchases as payout; announcement returns.
- Comment & Jarrell (1991), *The relative signalling power of Dutch-auction and fixed-price self-tender offers and open-market share repurchases*, JF 46(4):1243-1271 — repurchase after price declines.
- Peyer & Vermaelen (2009), *The nature and persistence of buyback anomalies*, RFS 22(4):1693-1745 — 3,481 OMRs 1991-2001, prior ~-9% return; scaled-shares persistence.
- Dittmar (2000), *Why do firms repurchase stock?*, J Business 73(3):331-355 — undervaluation, excess cash, leverage, takeover defense, countering dilution.
- Ikenberry & Vermaelen (1996), *The option to repurchase stock*, FM 25(4):9-24 — the flexibility/option value in a program.
- Busch & Obernberger (2016), *Actual share repurchases, price efficiency, and the information content of stock prices*, RFS 30(1):324-362 — average program ~16 months; **repurchase execution precedes positive abnormal returns** (execution signals manager undervaluation belief).
- Bonaimé, Öztekin & Warr (2014) — capital structure effects of repurchase announcements.
- **Decay signal:** a 2019 JCF study (*Long-run abnormal returns following stock buyback announcements*, 11,795 OMRs 1994-2014) and the 2022 CFA Institute *Stock buyback motivations and consequences* literature review — post-2001 long-run abnormal returns are much smaller than 1980s-90s; buybacks are now less driven by undervaluation signalling.

**Price-support / execution evidence:**
- Cook, Krigman & Leach (2004), *On the timing and execution of open market repurchases*, RFS 17(2):463-498 — intraday execution; OMRs provide liquidity and price support (narrow spreads, reduced order-imbalance impact).
- McNally, Smith & Barnes (2005) — repurchases offer price support in market turbulence.
- Li & Swanson (2016), *Is price support a motive for increasing share repurchases?*, JCF 38:77-91 — repurchases increase for price-support motives.
- Chee (2022), *Do share repurchases distort stock prices?*, — repurchase intensity reduces price delay post-execution.
- Elm Wealth (2026), *The impact of US stock buybacks: theory vs practice* — ~$1.5T/yr, ~$6B/day buying (~0.5% of daily volume); theoretical ~7-20 bps/day impact (they argue overstated with realistic decay/impact models).
- Frontiers Appl. Math. Stat. (2023), *Examining share repurchase executions: insights and synthesis* — synthesis of OMR execution, price impact, and support.

**Regulatory/mechanics:**
- Rule 10b-18 (17 CFR 240.10b-18) — safe harbor for open-market repurchases; conditions on manner, timing (not opening/closing 30 min), price, and volume (≤25% of 4-week ADV).
- Rule 10b5-1 (17 CFR 240.10b5-1) — affirmative defense; plan must be adopted in good faith before MNPI; SEC 2022 amendments (final Rules 33-11138, adopted Dec 2022, effective Feb 2023) added issuer **30-day cooling-off** before buyback trading commences and director/officer **120-day** cooling-off + disclosure; plan adoption/termination disclosed on Form 8-K / 10-Q / 10-K / proxy.
- **2023 SEC Share Repurchase Disclosure Modernization** — daily repurchase activity disclosed quarterly in Form 10-Q/10-K exhibits (aggregated daily: open-market, 10b-18, 10b5-1 breakdown) + 10b5-1 plan adoption/termination disclosure. Machine-readable on EDGAR.
- SEC Rule 10b5-1 final fact sheet (Dec 2022) — cooling-off, single-trade limits, good-faith requirement, 10b5-1-related disclosures.

**Data-feasibility note:** the 2023 rule gives us **daily, machine-readable repurchase history for backtesting** (lagged quarterly) and the 2022 rule gives us **near-real-time 10b5-1 adoption signals** (the forward-looking, non-lagged edge we can actually trade). The lag in the daily tables is fine for backtesting; the 10b5-1 adoption date is the live signal.

---

### **version-one research scope**

- **Universe — TWO co-base cells (joint gate, no selection, execute long on each repurchasing issuer only):**
  - **Cell 1 (large-cap):** S&P 500 constituents.
  - **Cell 2 (small-cap):** S&P 600 constituents.
  - Both must pass the pre-registered gate set independently; the joint gate prevents the stronger cell from masking weakness in the other and directly tests whether the buyback effect survives in each size bucket (the literature says the effect is stronger but noisier/riskier in small-caps — exactly the cell where a beta/friction artifact would live).
- **Signal variants to test (pre-registered tiers, not selection):**
  - **Tier A (announcement/plan):** event = Form 8-K/10-Q disclosure of a new 10b5-1 buyback plan or a new open-market repurchase authorization. Entry after announcement.
  - **Tier B (cooling-off expiry):** use the 2022 rule's ~30-day issuer cooling-off to schedule entry ~30 days after 10b5-1 adoption, when buyback trading commences — a forward, date-scheduled entry.
  - **Tier C (post-decline clusters):** event = a repurchasing issuer that also recently declined (undervaluation window), combining the documented "repurchase after declines" behavior.
- **Primary hypothesis H1:** over a pre-registered horizon from the signal date, the repurchasing-issuer long earns positive forward return **after friction AND after controlling for market beta/momentum** (excess over a matched control), in BOTH co-base cells, for at least one pre-registered tier.
- **Benchmark/control (critical — the vol-fade lesson):** matched-control set of non-repurchasing or repurchase-inactive names matched on size, book-to-market, momentum, and beta — built **within each cell** (SPX-matched controls for Cell 1, S&P 600-matched controls for Cell 2); and a beta/momentum-adjusted excess. We pre-register the adjustment so the result cannot be a beta confound.
- **Horizon:** event-window CARs (e.g. 0,+1), (+1,+5), (+5,+20) and a medium window, reported-not-selected.
- **Friction:** single-stock round trip; Cell 1 base 10-20 bps (spread+impact), Cell 2 base 20-40 bps (small-cap); stress +30 bps each. No mid-price fills.
- **Capacity: reported, not a gate.** Buyback demand is ~$6B/day market-wide, far above any scale where we'd bind; report a per-name notional sensitivity curve (the funding-basis convention) rather than gate on a single capital figure. Deployment scale is a later decision, not a research blocker.

---

### **required data**

- **EDGAR (free):** Form 8-K (10b5-1 / repurchase-program disclosures), Form 10-Q/10-K daily repurchase exhibits (open-market / 10b-18 / 10b5-1 shares per day), Form 4 (insider + issuer-related), 10b5-1 plan adoption/termination items. Parse with existing stack.
- **Daily OHLCV bars** (verified lineage — Yahoo para the vol-fade/SPY work; or Databento EQUS.MINI) for all universe names, with **survivorship-bias control** (include delisted).
- **Corporate-action calendar** (earnings dates for blackout windows; spin-off/index dates) — free.
- **Benchmark/factor:** matching on B/M, momentum, beta — from free daily bars + computed proxies.

---

### **data validation**

- Verify EDGAR parse accuracy on a hand-checked sample (10b5-1 accounts vs 10-Q tables vs known announcements).
- Confirm no look-ahead: each signal uses only data available at decision time (note the 30-day cooling-off timing is our main timing assumption — verify against actual disclosures).
- Verify bars against a second source (the vol-fade SPY lesson).
- Exclude survivorship bias by including delisted/dissolved issuers in the universe/window.
- Keep raw EDGAR immutable; store parsed/derived tables separately with provenance.

---

### **validation plan**

- **Economic:** return decomposition (is the edge from beta, from the repurchase signal, or from a momentum confound?); compare repurchasing vs matched non-repurchasing names; verify the signal precedes (not follows) the return.
- **Statistical:** IS/OOS split (pre-2023-vs-post)[*note: the daily-disclosure data starts 2023; the 10b5-1 cooling-off rule effective 2023], bootstrap p5 > 0, reshuffle, drop-best-event, persistence/multi-cycle gate (the exact failure of index-rebal — a single strong quarter must not carry the result).
- **Robustness:** effect must survive across universe (large vs small), across 10b5-1 vs open-market vs post-decline variants, across horizons, across fee/friction assumptions, and across years.
- **Capacity:** notional sensitivity; buyback demand stays roughly constant regardless of our size.

---

### **rejection gates**

Reject if any of the following is true:
- the counterparty/mechanism cannot be explained (mandate filter fails);
- the effect vanishes after beta/momentum/size adjustment or vs the matched control (the vol-fade beats_random failure);
- the effect does not survive across years / depends on a single year or quarter (the index-rebal failure);
- the edge is not tradable after realistic friction (disappears when entry shifts from announced-date to a realistic fills/slippage model, or requires the exact disclosure timestamp);
- the signal is too sparse to generalize (too few independent events);
- the apparent return is a data artifact (survivorship bias, look-ahead, stale daily-disclosure dates);
- capacity is not credible.

A failed candidate is a successful research outcome. It prevents capital from being allocated to an unverified story.

---

### **research status and unresolved questions**

- **Complete:** survey selected this candidate (#1) from the 2025-2026 structural shortlist; literature pass done (see register); mechanic documented (forced flow + 10b5-1 cooling-off signal + price-support evidence); the two prior-candidate failure modes are explicitly gated (beta-confound control; persistence gate).

- **Feasibility check (2026-08-04, live EDGAR tests):**
  - **CONFIRMED - EDGAR full-text search + document retrieval works.** `repurchase program` returns ~90% Form 8-K; an item 8.01 8-K for Smart Sand (SND) was retrieved and parsed containing "board approved a new two-year repurchase program authorizing the repurchase of up to $20.0m" — the Tier A signal is reliably findable and machine-readable.
  - **CONFIRMED - 10b5-1 plan activity is discoverable** (8-K for issuer repurchase plans; Form 10-Q Item 5 / Reg S-K Item 408 for director/officer plan adoptions/terminations; e.g. Alphabet Q2 2026 Item 5 discloses a director plan termination).
  - **FINDING - the 30-day issuer cooling-off is rule-derived, not filing-verbatim.** Announcement 8-Ks describe buyback methods ("...may include open market purchases, ASRs, 10b5-1 plans...") but typically do not restate the cooling-off number. Tier B timing therefore comes from the SEC Rule 10b5-1(c) structure (30 days to buyback-commencement after plan adoption), a valid forward signal, but the model must source it from the rule, not a filing field.
  - **FINDING - the daily 10b-18 backtest table is uneven.** A top repurchaser (Alphabet, Q2 2026 10-Q) Item 2 reports "Issuer Purchases of Equity Securities - None", even though the firm is a large buyer (its buybacks run via ASRs/structured programs and different reporting). The daily open-market table is NOT uniformly populated and **cannot be the sole universe/history source for backtesting**.
  - **Design consequence:** build the backtest **event set from 8-K repurchase-program announcements (Tier A)** and 10b5-1 Item 5/408 disclosures (Tier B), and treat the daily 10b-18 table as supplementary/spot-check, not the universe builder. This removes reliance on the uneven quarterly table.
  - **CONFIRMED - daily-bar lineage** (Yahoo, per the vol-fade/SPY work) extends to a multi-name universe; EDGAR retains delisted issuers' filings, so survivorship-bias control is feasible.
  - **Sparsity test (2026-08-04): event count is NOT a constraint.** Harvesting EDGAR full-text `"repurchase program"` Form 8-Ks across 2024-2026 (24 months) returned ~1,953 unique (CIK,adsh) filings and **~879 distinct issuing companies**, with ~1,454 filings carrying item 8.01, and **~740-840 8-K events captured per full year** (a lower bound, since monthly hits truncate at the 100-result page cap). Even after conservative dedup for issuers with multiple 8-Ks per program (e.g. News Corp, ~544 filings over 2024-2026), this yields on the order of **hundreds of independent buyback-authorization events per year** — orders of magnitude beyond the ~80-event vol-fade sample and the single ~11-event batch that killed index-rebalancing. The "too few events" gate is cleared for Tier A.

- **Unresolved before coding, who resolves:**
  - **Research:** confirm the practical feed of 8-K repurchase-program announcements is comprehensive enough to build a large, independent event set (sparsity test) - **RESOLVED** (see above; hundreds of events/yr; the remaining work is the implementation-time dedup to distinct programs).
  - **Research:** verify whether 10b5-1 issuer repurchase plans are systematically announced via 8-K vs only in 10-Q/10-K, to size Tier B.
  - **Assumption (determined):** capacity is reported as a notional-sensitivity curve, not gated on a single capital figure (the funding-basis convention) — deployment scale is a later decision.
  - **Assumption (determined):** BOTH universes are tested as co-base cells (S&P 500 and S&P 600) with a joint gate, so the choice between large- and small-cap is made empirically, not by guess.

### **current known limitations**

- The 10b5-1 cooling-off (30-day issuer) is the linchpin of the forward signal; it is rule-derived and must be verified against real plan announcements, not a filing field.
- The daily repurchase tables are quarterly-lagged AND unevenly populated (some large repurchasers report via ASR/structured programs and show "None" in the open-market table) — so the backtest must not depend on them as the primary calendar.
- Post-2001 decay documented for *announcement/long-run* returns; the *execution/price-support* edge is a different, less-decayed mechanic, but decay is a live risk to gate on.
- The single-stock long is exposed to idiosyncratic and momentum/beta risk, which the matched-control/beta-adjustment must remove else the candidate is rejected.

---

### **definition of done before coding**

No collection or backtest code begins until:
- the research questions above are answered with cited sources;
- the signal tier (A/B/C) and horizon are frozen; the beta/momentum/matched control is specified in writing;
- data availability (EDGAR 10b5-1 + daily exhibits + verified bars + delisted coverage) is confirmed;
- entry/exit/sizing and friction are frozen;
- rejection thresholds and the persistence + beta-control gates are registered;
- known risks and failure modes are documented.

The outcome of this document may be approval to code, revision of the hypothesis, or rejection of the candidate.

### **current decision**

Under research, with the key data-feasibility and sparsity questions **answered (2026-08-04)** via live EDGAR tests and a harvest, and the two design choices frozen: **both universes (S&P 500 + S&P 600) are pre-registered as co-base cells with a joint gate**, and **capacity is reported as a notional-sensitivity curve, not a gate** (deployment scale is a later decision). Confirmed: Tier A 8-K feed works and is machine-readable; 10b5-1 signal discoverable; the 30-day cooling-off is rule-derived (not a filing field); the daily 10b-18 table is uneven and must not be the primary event source; **event sparsity is not a constraint (~hundreds of independent 8-K buyback-authorization events per year)**. The only remaining pre-build items are implementation-time program dedup and a Tier B (10b5-1) sizing check. No code has collected data or run a backtest; numeric rejection gates freeze once the implementation build begins. This document commits the framework, the confirmed data route, and the frozen design as the basis for the next step.
