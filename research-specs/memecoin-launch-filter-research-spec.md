# Memecoin Launch-Filter Edge — Research & Pre-Registration Specification

**Status:** Pre-research specification (analysis phase, no build started, 2026-09-21)
**Classification:** On-chain launchpad event data + two-layer token selection filter
**Lane novelty:** New family. The PROJECT_RECORD lane inventory (equity flow, options microstructure, sector rotation, risk-carry, market-making) does not cover on-chain token-launch selection. This spec is written *before* any data pull or code, in the same gate-discipline as every other spec in this repo.
**Method note:** The harness methodology (pre-registration, honest costs, correct benchmark, bootstrap gate, OOS sign-agreement) transfers directly from the existing probe stack. The data source, adversary set, and failure modes do not.

---

## 1. The research question

Can a **two-layer selection filter** — (A) rug-risk features computed from on-chain token/pool state, and (B) post-launch structure/momentum features — identify a subset of new token launches whose forward return distribution, traded with asymmetric exit rules and honest costs, is positive-EV at retail scale?

The claim is **conditional and falsifiable**: the filter must beat the naive baseline (buy every launch, exit on a fixed rule) by a pre-registered margin, net of fees/slippage/rugs, on out-of-sample data. If it fails the gate, the lane is disconfirmed and closed, same as every other family in this repo.

**Why this is worth one bounded probe (and only one):** the base rates are now sourced (Section 3). They are brutal for the naive game and *unmeasured* for the filtered game. The filtered game is the entire question.

---

## 2. Scope decisions (frozen before data)

- **Chain:** Solana first (dominant launchpad venue; pump.fun ~12.9M launches; richest public data ecosystem: Dune, Bitquery, Helius, Shyft).
- **Venue:** pump.fun bonding-curve launches, tracked through graduation to PumpSwap/Raydium. (Secondary venue four.meme/BSC only if the Solana probe passes its gate.)
- **Entry archetype:** NOT launch-second sniping. Entry is post-launch, into tokens passing both filter layers, on the first structure confirmation. This is a *selection* strategy competing on decisions, not a *latency* strategy competing on delivery.
- **Position sizing:** fixed fractional (1% of risk capital per position), no leverage, hard cap on concurrent positions.
---

## 3. Verified landscape (what the sources establish)

All claims below were verified via Tavily search on 2026-09-21. Sources listed in Section 8.

### 3.1 Base rates (the numbers any edge must beat)

| Metric | Value | Source |
|---|---|---|
| Tokens classified rug/pump-and-dump (pump.fun, Jan 2024–Mar 2025) | 98.6% of 7M+ launches | Solidus Labs via CryptoPotato |
| Tokens ever retaining liquidity > $1k | ~97,000 of 7M+ (~1.4%) | Solidus Labs |
| Wallets ever realizing > $10k profit | 55,296 of 13.55M (~0.4%) | Dune via Brave New Coin |
| Wallets ever realizing > $1M | 293 (0.002%) | Dune via BNC |
| Monthly loss rate among active traders | ~50.6%; 96% of "profitable" make < $500 | Dune via Protos/CryptoRank |
| Graduation rate (bonding curve to DEX) | < 2% (some days ~1%) | The Block / Dune via SolanaCompass |
| Median memecoin hold time (Solana) | ~100 seconds, down from ~300 | Galaxy Research (Oct 2025) |
| Concentration: 12 of 12.9M tokens = 56% of all FDMC | power-law lottery structure | Galaxy Research |

### 3.2 Who the adversaries are, and what their edges are

| Player | Game | Edge | Source |
|---|---|---|---|
| Insiders/deployers | Pre-fund, buy first minute, sell into launch demand | Perfect information (TRUMP case: wallet funded 4h pre-launch, $5.9M in first minute, $20M sold) | Bubblemaps via CryptoRank |
| MEV searchers/snipers | Buy within seconds via Jito bundles | Latency + tip auction (50–60% of expected profit paid in tips) | Dysnix/Helius, baransel.dev |
| Market makers | Contracted liquidity, quote both sides | A deal, not speed | Galaxy Research |
| KOL networks | Coordinated shill campaigns | Distribution (audience), often paid | Galaxy Research KOL layer |
| Wash traders | Fake volume to trigger filters/bots | $2B+ identified on DEXs; top 10% of washer accounts = 43% of wash volume | Chainalysis 2025 |

**Key structural fact:** celebrity/insider launches (TRUMP, YZY) now deliberately route through Meteora *specifically to defeat snipers* (Galaxy). The launch-side adversary is actively engineering against the speed game. This confirms the speed lane is closed at retail; it does not say anything about the selection lane.

### 3.3 What the profitable minority does (the profile to encode)

From the MemeScout wallet study (Baldwin, 3 months of early-stage launch data) and practitioner playbooks (Washed via fomo.family, Altrady):

1. **Entry timing:** 10–60 seconds after detection (human-fast, not bot-fast). Wallets buying < 3 seconds are scripts; wallets entering minutes late are followers.
2. **Selectivity:** 5–30 tokens touched per window. High-volume wallets (hundreds of tokens/week) are bots. The profitable minority is picky.
3. **Win rate 20–60%** (not higher; 80%+ = cherry-picked or fresh-wallet-per-play) with **long-tail multiplier distribution** (a few 5–10x+ among many small wins). Venture profile, not scalper profile.
4. **Exit asymmetry:** winners make 3–10x what losers cost. Incremental selling on green candles only; volatility-scaled trailing stop; time stop ~24h; no leverage.
5. **Filter quality dominates wallet quality:** raising one structural filter threshold (radar score 30 to 36) moved the 1.25x hit rate from 59% to 78.6% on the same data. This is the single most encouraging number for this lane: the filter, not the picker, carried the improvement.

### 3.4 Rug prediction is a solved-ish sub-problem (with two documented traps)

**Traps:** (a) a liquidity lock does not prevent a founder sell-down: 100% LP locked + 40% of supply in unlocked founder wallet is still a rug (Streamflow); (b) 12.8% of 2025 thefts were *fragmented* rugs (small repeated withdrawals), evading snapshot checks (shattered.io). Consequence: filter must monitor wallets *continuously*, not screen once at entry.

---

## 4. The hypothesis (pre-registered)

**H1 (primary):** Tokens passing Layer 1 (rug-risk) AND Layer 2 (structure/momentum) filters at entry, exited on asymmetric rules, generate positive mean forward return net of costs on out-of-sample data, with the gate margin defined in Section 7.

**H0 (null):** The filtered subset's forward returns are indistinguishable from the naive baseline (buy-everything) after costs, or negative.

**H2 (mechanism check, secondary):** Filter improvement moves hit-rate in the documented direction (more selective = higher per-trade expectancy at lower trade count). This mirrors the MemeScout 59-to-78.6 result and would explain *why* H1 passes if it does.

---

## 5. Filter definitions (frozen before backtest)

### Layer 1 — rug-risk screen (must all pass; any fail = skip)

Computed from on-chain state at candidate entry time. Feature set follows MDPI (Mazorra et al. 2022) plus Solana-specific additions.

| # | Feature | Threshold (frozen) | Source basis |
|---|---|---|---|
| 1a | LP status | 100% burned or permanently locked | Streamflow: lock alone insufficient but absence is disqualifying. MDPI: 90% of tokens using Unicrypt lock contracts became malicious (725 of 745 labeled) - lock usage is a POSITIVE predictor of malice in their data, not safety |
| 1b | Mint authority | Revoked | ChainAware/standard Solana checks |
| 1c | Freeze authority | Revoked | standard |
| 1d | Top-10 holder concentration (HHI) | HHI below threshold calibrated on training slice, then frozen | MDPI Herfindahl feature |
| 1e | Founder/dev wallet unlocked supply | below threshold (the trap in 3.4a) | Streamflow analysis |
| 1f | Clustering coefficient of tx graph (linked wallets buying together) | below threshold | MDPI clustering feature |
| 1g | Deployer history | no prior rug-linked deployments (check against known rug address sets) | ChainAware deployer-history feature |

### Layer 2 — structure/momentum screen (all must pass at entry)

| # | Feature | Threshold (frozen) | Source basis |
|---|---|---|---|
| 2a | Token age | 3–7 days from launch (or post-graduation equivalent window) | Washed "avoid new pairs" guidance; post-bot-chaos, pre-death |
| 2b | Market cap | $400k–$3M band | Washed "sweet spot" |
| 2c | Liquidity depth | pool depth supports exit of full position within X% price impact (X frozen pre-run) | Avalanche Culture Catalyst criteria analog |
| 2d | Organic volume share | share of volume from non-linked, non-repetitive wallets above threshold | Chainalysis wash heuristics |
| 2e | Momentum gate | price/volume structure consistent with consolidation or uptrend, not post-pump bleed | practitioner consensus; encoded as simple rule (e.g., 24h volume trend positive AND price above N-period mean) |

### Entry, exit, sizing (frozen)

- **Entry:** first point after both layers pass where 2e confirms (evaluated on 1-minute bars; one entry per token; no re-entry after exit).
- **Exits:** (i) volatility-scaled trailing stop (ATR-based, multiplier frozen pre-run); (ii) hard time stop at 24h; (iii) incremental take-profit schedule (e.g., sell 50% at +50%, trail rest) — exact schedule frozen before first run, one schedule, no tuning after seeing results.
- **Sizing:** 1% of risk capital per position; max 5 concurrent; no leverage.
- **Costs:** model both (a) taker fee + slippage from observed pool depth, and (b) failed-transaction cost allowance. Rugs that pass Layer 1 but fail afterward are INCLUDED as losses; no post-hoc exclusion.

---

## 6. Procedure (the movement, step by step)

**Step 0 — Open searches (Section 9) completed and recorded here before Step 1.** No code before this.

**Step 1 — Data pull.** Sample window: 3 months of pump.fun launches (target N: all launches with >= $5k peak liquidity; expected several thousand tokens). Sources: Dune (adam_tehc dashboards + API), Bitquery or Helius/Shyft for granular per-pool trade/holder history. Record pull date, exact query, row counts in this doc's addendum.

**Step 2 — Feature computation.** Compute Layer 1 + Layer 2 features per token per candidate entry bar. Pure functions over historical state; no lookahead: features at time t use only data <= t.

**Step 3 — Naive baseline.** Simulate: buy every token (that meets only minimum liquidity to be tradeable) at same entry archetype, same exit rules, same costs. This is the benchmark. Record its distribution.

**Step 4 — Filtered strategy sim.** Simulate H1 entry/exit/sizing on filtered subset. Same costs. Same period.

**Step 5 — Gate evaluation (Section 7).** Compute net expectancy, hit rate, multiplier distribution, max drawdown, and the bootstrap test. Verdict: PASS, DISCONFIRMED, or INSUFFICIENT-DATA (only if N < pre-registered minimum; this verdict requires a stated reason and either widens the window once or closes the lane).

**Step 6 — OOS confirmation.** If PASS in-sample window, re-run untouched on a later, non-overlapping window. OOS must agree in sign and pass the same gate. IS-pass + OOS-fail = DISCONFIRMED (curve-fit).

**Step 7 — Record.** Write results into this doc + PROJECT_RECORD row. No resurfacing without a new mechanism (Section 8 of PROJECT_RECORD applies).

---

## 7. Gate (pre-registered, before any data)

- **Minimum sample:** >= 300 filtered entries across the window (else INSUFFICIENT-DATA).
- **Primary gate:** mean net return per trade > 0 AND bootstrap p5 of mean per-trade return > 0 (10k resamples, same method as prior probes).
- **Dominance gate:** filtered strategy's expectancy per unit risk > naive baseline's, by a margin that survives dropping the single best trade (drop-best check; if the strategy only works because of one outlier, it fails).
- **OOS gate:** out-of-sample window agrees in sign and passes primary gate.
- **No-lookahead audit:** features recomputed with a 1-bar lag must not materially change the verdict; if they do, the result is tainted and DISCONFIRMED.

PASS requires ALL gates. Any fail = DISCONFIRMED. No "promising but" outcomes.

---

## 8. Failure modes (pre-listed)

1. **Survivorship in the data pull:** only tokens still tracked by aggregators get pulled; dead rugs drop out of some APIs. Must pull from launch-event records, not token-list records.
2. **Lookahead in feature state:** holder distribution "now" is not holder distribution at entry time. Use event-sourced state reconstruction, not snapshots.
3. **Wash-volume contamination of Layer 2e:** coordinated wallets look like momentum. Mitigation: 2d organic-share check; also treat suspiciously perfect volume as a negative signal.
4. **Cost realism:** Solana priority fees + slippage on shallow pools can exceed modeled estimates; failed-tx allowance is mandatory, not optional.
5. **Regime dependence:** a 3-month window may be a hot or dead regime; the OOS window must span a different regime or the result is regime-specific (record regime state, e.g., graduation rate, alongside results).
6. **The unfalsifiable trap:** "the filter needs tuning" after seeing results = curve-fitting. One frozen parameter set. If it fails, the honest answer is the lane is dead at these thresholds, and a *different mechanism* (not retuned thresholds) would be required to reopen.

---

## 9. Step 0 searches (COMPLETED 2026-09-21)

### 9.1 Full paper extraction (item 1) - CLOSED

Source: full text of Mazorra, Adan, Daza (2022), Mathematics 10(6):949, doi 10.3390/math10060949 (user-provided).

**Dataset:** 27,588 labeled Uniswap V2 tokens (26,957 malicious / 631 non-malicious), May 2020 - Sep 2021. Labels derived from inactivity (>30 days), max liquidity drawdown ~ 1, and no recovery (RC = 0); non-malicious seeded from externally audited tokens.

**Model results (5-fold CV, XGBoost > FT-Transformer):**
| Method | Accuracy | Recall | Precision | F1 |
|---|---|---|---|---|
| Activity-based (any-time eval, pre-rug) | 0.9936 | 0.9540 | 0.9838 | 0.9684 |
| 24h method, hour 1 (best recall for hour) | 0.990 | 0.714 | 0.810 | 0.758 |
| 24h method, hour 20 (best overall recall) | 0.992 | 0.789 | 0.853 | 0.819 |

**Honest-reading caveats we adopt:**
1. Accuracy is inflated by class imbalance (26,957:631). Predicting everything malicious scores 97.7%. Precision/recall are the real numbers.
2. Precision is the number that matters for OUR use: when the model says a token is non-malicious, it is right ~98% of the time (activity-based). Recall 0.954 means ~5% of malicious tokens slip through. For our filter: expect a nonzero residual rug rate in the ~2-5% band even with a perfect feature clone - the backtest must absorb it, as specified.
3. Predictive power grows with history: hour-1 recall 0.714 vs hour-20 recall 0.789; the activity-based method (any history) is best. Our 3-7 day entry window has MORE history than any 24h evaluation - favorable.
4. Rug pulls cluster early: 93% occur within 24h of pool creation. Our 3-7 day age filter (2a) therefore sits AFTER the rug-risk peak by construction - corroborating the archetype.

**Full feature table (Appendix A1 of the paper):** HHI of LP tokens (liq_curve), HHI of token balances (tx_curve), n_pool_syncs, WETH reserves, price, total liquidity, LP mints/burns/transfers, n_transfers, n_unique_addresses, clustering coefficient (clus_coeff), blocks between token and pool creation (difference_token_pool), lock flag, yield flag, burn flag. The SHAP analysis found n_transactions, n_unique_addresses, and difference_token_pool among the heaviest weights; small token-pool block gaps skew malicious (copycat speed runs).

**Trap corroboration:** 90% of Unicrypt-locking tokens turned malicious (Section 7.4.3). Lock contracts alone are misleading - already encoded in 1a/1e.

### 9.2 Data-source feasibility (items 2, 3, 7) - CLOSED

| Source | Free tier | Paid entry | Fit for our steps |
|---|---|---|---|
| Helius (RPC + indexed APIs) | 1M credits/mo, 10 RPS, 1 sendTx/s | $49/mo (10M credits, 50 RPS) | Backtest-era event reconstruction on free tier is plausible if pull is batched over weeks; live monitoring later on Developer tier. getSignaturesForAddress + getTransaction batch over the Pump program gives birth records (fixes failure mode 1). |
| Bitquery pump.fun API | No free tier; 7-day trial (1,000 API points, 2 streams) | $49/mo; streaming $99/mo | Fastest path to indexed launches/graduations/curve trades without decoding. 7-day trial can prototype the query shapes; paid month needed for a full 3-month pull. |
| Dune | 2,500 credits/mo, API 40 calls/min, export 20 credits/MB (expensive) | Plus ~$390/mo | Good for aggregate context (graduation rates, PnL curves via adam_tehc dashboards: "Pump.Fun Alpha Wallets", "Wallet Analysor", trader-profitability dashboards). Too credit-expensive for per-token event exports at our N. Use for aggregates, not the core dataset. |
| Shyft | Free tier exists | from $99/mo | Alternative; GraphQL + indexed tx history. Secondary. |

**Decision (recorded):** primary pull = raw program event/instruction reconstruction via Helius free tier (or public RPC batches), cross-checked against Bitquery during its trial for query validation. Dune reserved for aggregate/regime context. This keeps Step 1 at ~$0 cash cost, at the price of slower batching.

**Pump.fun on-chain schema (item 7) - captured:** Pump program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P; PumpSwap AMM pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA; fee program pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ. Bonding-curve PDA seeds ["bonding-curve", mint]; global PDA ["global"] = 4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf. Create instruction discriminator = [24, 30, 200, 40, 5, 28, 7, 119]; create accounts include mint (signer, writable), bonding_curve, associated_bonding_curve, global, user (creator), creator_vault. Bonding-curve account layout: 8-byte discriminator, then u64s incl. virtual_token_reserves, virtual_sol_reserves, real reserves, token_total_supply, complete flag, creator pubkey. Graduation = migration instruction to PumpSwap program (since Mar 20 2025); birth records reconstructable from program instruction history, not token-list snapshots.

### 9.3 Rug-check feature reuse (item 5) - CLOSED

RugCheck / Solana Tracker Data API / StakePoint all compute and expose exactly the Layer 1 family: mint authority active/revoked, freeze authority active/revoked, LP burned/locked percentage, top-10 holder concentration, single-holder dominance, dev holdings, bundler/insider flags (linked-wallet coordinated buys), mutable metadata, LP provider count. Solana Tracker returns a named risk list with severity scores as JSON - reusable directly for 1b/1c/1d/1e/1f and for cross-validating our own computed features. Decision: implement Layer 1 checks natively (pure on-chain reads) and use RugCheck/Tracker as an independent second opinion during the sim, not as the source of truth (their scores change over time; event-sourced state reconstruction is ours).

### 9.4 Fragmented/slow-rug detection (item 6) - CLOSED

Found the Solana-native academic work: SolRPDS (Alhaidari et al., Apr 2025) - the first public Solana rug-pull dataset: 3.69B transactions, 278M LP actions, 3.42M swaps (Feb 2021 - Nov 2024, Raydium/Jupiter era), 62,895 suspicious pools annotated for inactivity with liquidity add/remove histories. Its method explicitly handles gradual withdrawals: suspected = rapid withdrawals or volume collapse while still trading; confirmed = removal (at once OR gradual) followed by inactivity. This is the operational definition for our Layer 1 continuous monitoring: track cumulative net LP removal + dev-wallet sell share from entry until exit, flag "soft rug" trajectories (Solidus separately identified soft-rug patterns across 388k Raydium pools). Related anchor: 60% of Ethereum/BSC rug tokens die within 1 day ("1-day-tokens"), $240M extracted.

### 9.5 Independent backtests of the lane (item 4) - CLOSED (empty result, recorded)

No rigorous, public, independent backtest of a two-layer launch-filter strategy on Solana was found. Nearest artifacts are vendor-adjacent (MemeScout's filter-hit-rate claims; practitioner articles). A scan with zero independent survivors/rejections is a valid result: the lane is unmeasured publicly, which is exactly what makes the bounded probe informative - and which also means the burden-of-proof framing in Section 10 stands.

### 9.6 Deferred (item 8)

Jurisdiction tax/fee environment: remains deferred; not blocking Steps 1-5. Revisit at live-execution design, if the gate passes.

---

## 10. Honest prior

Written before any test, in the spirit of the repo: the naive game is measured dead (98.6% rug base rate; speed game owned by tip-auction searchers). The filtered game is the open question, and the one sourced data point on filter power (59-to-78.6 hit-rate move) is encouraging but comes from a vendor with a product to sell, not from our own replay. The prior is therefore: **plausible mechanism, unproven magnitude, and the burden of proof is entirely on the backtest.** If the gate fails, this lane joins the record as measured-dead like the others, which is a fine outcome for one week of analysis work.

---

## 11. Sources (all accessed 2026-09-21 via Tavily)

1. Galaxy Research, "The State of Memecoins: Culture, Trading, and Infrastructure" (Oct 2025) - https://www.galaxy.com/insights/research/memecoins-pump-fun-solana-kols
2. Brave New Coin, "Over 99% of Pump.fun Traders Miss the $10K Mark" (Jan 2025) - https://bravenewcoin.com/insights/over-99-of-pump-fun-traders-miss-the-10k-mark
3. CryptoRank/Protos, "Pump.fun Traders Face Stark Reality" - https://cryptorank.io/news/feed/60ff8-pump-fun-traders-losses-profits-data
4. CryptoPotato via CryptoRank, "98% of Tokens on Pump.fun Are Rug Pulls or Fraud" (Solidus Labs report, May 2025) - https://cryptorank.io/news/feed/9e964-98-of-tokens-on-pump-fun-are-rug-pulls-or-fraud-report
5. Mazorra et al., "Do Not Rug on Me: Leveraging Machine Learning Techniques for Automated Scam Detection" (MDPI Mathematics 2022) - https://www.mdpi.com/2227-7390/10/6/949
6. Streamflow, "Do Liquidity Locks Prevent Rug Pulls?" (2026) - https://streamflow.finance/blog/do-liquidity-locks-prevent-rug-pulls
7. Chainalysis, "Crypto Market Manipulation: Wash Trading and Pump-and-Dumps" (2025) - https://www.chainalysis.com/blog/crypto-market-manipulation-wash-trading-pump-and-dump-2025
8. CryptoRank, "Insider trading allegations trail TRUMP memecoin" (Bubblemaps analysis) - https://cryptorank.io/news/feed/beb2a-insider-trading-allegations-trump-btc
9. Dysnix, "What separates profitable MEV on Solana" (2026, cites Helius H1 2025 report) - https://dysnix.com/blog/solana-mev-infrastructure
10. baransel.dev, "I Built a Solana MEV Bot - Here's What I Learned" - https://baransel.dev/post/i-built-a-solana-mev-bot-heres-what-i-learned
11. Solana docs, "MEV Protection with Jito DontFront" - https://solana.com/docs/defi/mev-protection
12. Nathan Baldwin (MemeScout), "Copy Trading on Solana: How to Find Alpha Wallets Without Getting Faked Out by Bots" - https://medium.com/@nathan.baldwin_31153/copy-trading-on-solana-how-to-find-alpha-wallets-without-getting-faked-out-by-bots-0bc550f07290
13. fomo.family, "Memecoin Trading Strategies: Lessons from a Six-Figure Trader" (Washed, Jan 2026) - https://fomo.family/blog/learn/memecoin-trading-strategies-lessons-from-six-figure-trader
14. Altrady, "How to Trade Memecoins: Risk & Execution" - https://www.altrady.com/blog/crypto-trading-strategies/how-to-trade-memecoins
15. SolanaCompass, "Pump.fun 42,000 Token Launches in 24 Hours: The 2% Graduation Rate" (The Block data) - https://solanacompass.com/news/pumpfun-launched-42000-tokens-in-one-day-fewer-than-2-will-ever-reach-a-dex
16. The Vintage Rug Shop (archived), "The Pump.fun Graduation Problem" - https://archive.thevintagerugshop.com/2026/07/21/the-pump-fun-graduation-problem-what-happens-after-tokens-leave-the-bonding-curve-for-raydium
17. Yahoo Finance, "Avalanche Foundation Reveals Memecoin Selection Criteria" - https://finance.yahoo.com/news/avalanche-foundation-reveals-memecoin-selection-055655229.html
18. philarekt on X, "How I Built a Memecoin Filter That Pushed My Early Win Rate to 80%" - https://x.com/i/article/2099150538440913247
19. Mazorra, B.; Adan, V.; Daza, V. "Do Not Rug on Me" full text (user-provided) - https://doi.org/10.3390/math10060949 (code: https://github.com/T2Project/RugPullDetection)
20. SolRPDS: A Dataset for Analyzing Rug Pulls in Solana DeFi (Alhaidari et al., 2025) - https://par.nsf.gov/servlets/purl/10639152
21. Helius pricing - https://www.helius.dev/pricing
22. Bitquery pump.fun API product/docs - https://bitquery.io/products/pumpfun-api ; https://docs.bitquery.io/docs/blockchain/Solana/Pumpfun/Pump-Fun-API
23. Dune billing/FAQ docs - https://docs.dune.com/api-reference/overview/billing
24. Solana Tracker pump.fun program guide - https://docs.solanatracker.io/guides/pumpfun-program
25. AllenHark pump.fun create-instruction discriminator analysis - https://allenhark.com/blog/pumpfun-create-instruction-discriminator
26. Solidus Labs, Solana rug pulls and pump-and-dumps report - https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance

## Addendum A — Step 1 data-pull record (Dune pipeline)

**Pull date:** 2026-09-22. **Target day:** 2026-09-20 (UTC).

**Pivot rationale:** Helius RPC free tier cannot traverse a full day of pump.fun
signatures in feasible time (~1.1M signatures/day at 8 RPS; multi-week for 3 months).
Dune indexes pump.fun decoded calls and trades natively.

**Tables (discovered via information_schema on 2026-09-22):**
- `pumpdotfun_solana.pump_call_create` (legacy v1 path; ~60-250/day in Sep 2026)
- `pumpdotfun_solana.pump_call_create_v2` (live path; ~30k/day) — has creator, mint,
  bonding curve, name/symbol/uri, is_mayhem_mode, block time/slot/tx_id
- `pumpdotfun_solana.base_trades` (unified trades; block_month partition, uint256 raw amounts)
- `pumpdotfun_solana.pump_evt_completeevent` (graduation events) — not yet pulled

**Volume reality check (Sep 2026):** legacy create path collapsed to ~60-250/day while
`create_v2` carries ~30k/day. Any earlier pump.fun research based on v1 paths is not
directly comparable to current launch flow.

**2026-09-20 extraction (research/meme_launch_filter/2026-09-20/step1_launches.json):**
- 30,783 total creates: 30,535 v2 + 248 v1 (cross-checked COUNT query)
- 1,034 rows have NULL creator (keep for completeness; exclude from creator-level features)
- 8,262/30,535 v2 creates are `is_mayhem_mode = true`
- 8,460 unique creators; 2,776 creators launched >1 token the same day, covering 24,065
  launches (78%) — serial-launcher concentration is the dominant structural feature
- Top creator launched 350 tokens in one day; top 5: 350, 308, 218, 213, 194

**Infrastructure notes:** Dune ad-hoc SQL = POST /api/v1/sql/execute, poll
GET /api/v1/execution/{id}/status (free) then /results; `ILIKE` is not supported
(use LOWER(...) LIKE). `base_trades` has no block_date; filter on block_month or
block_time. Small queries consumed ~8 credits on the ad-hoc path.

## Addendum B — Step 1 outcome variables (2026-09-20)

**Graduation pull:** 1,125 unique mints with `pump_evt_completeevent` on the day
(research/.../step1_graduations.json). Merged with launches + day-of trade aggregates
(step1_merged.json, step1_summary.py) into a launch-day outcome picture.

**Outcome decomposition of 30,783 creates:**
- graduated: 1,048 (3.4%)
- died_zero (pool drained to <0.1 SOL same day, never graduated): 4,271 (13.9%)
- live_eod (never graduated, never fully drained, still tradeable at day end): 25,464 (82.7%)

**Graduation timing (1,039 with matchable create time):** under 1 min: 618 (59%),
1-60 min: 368 (35%), 1-6h: 36, over 6h: 17.

**Suspicious instant graduation signature:** of 618 sub-minute graduations, 379 (61%)
had the graduating `user` equal to the token's creator. 482 distinct creators,
475 distinct graduating users — this is not one bot wallet, it is a broad pattern of
self-funded instant graduations (spec: mayhem-mode creations include a funded initial
buy in the same tx).

**Key analyst readings:**
1. "Graduated" is NOT a clean quality outcome. The majority of graduations happen
   inside the first minute and 61% of those are self-graduations by the creator's own
   wallet. A filter keyed on 'graduation = success' would be gaming a manipulated signal.
2. The mayhem-mode cohort graduates LESS (2.7% vs 3.7% non-mayhem) despite mayhem
   creations self-funding their own first buy. Weak but directionally negative.
3. Concentration: 1,331 creators launched >3 tokens each on this single day,
   covering 20,751 tokens (67% of all creates).
4. Effective graduate base rate against creator-seriousness: roughly 1,048 grads
   spread over 8,460 creators = ~0.12 graduations per creator per day. Even for
   non-serial creators (5,684 with 1 launch/day) graduation is a low-probability
   event on a per-launch basis.

---

## Addendum C — Step 1 first-hour behavior analysis (2026-09-22)

**Data:** step1_firsthour.json (execution 01M34BX09M8MK26KRJZSK7S3AP, large
performance, ~7s server time). 29,539 tokens with first-hour (<=60 min post-create)
trade aggregates split creator vs non-creator: trade counts, SOL volumes, and
creator_first_sell_min. Merged with outcome buckets via
step1_firsthour_analysis.py -> step1_firsthour_summary.json. 1,244 tokens had no
first-hour trades at all (silent births).

**Hypothesis (a): self-fund-then-dump on instant graduations — CONFIRMED but
refined.** Of 620 sub-minute graduations, 386 (62%) were literally a single trade
in the first hour (creator's own graduation buy). Only 17/620 (2.7%) showed any
creator SELL within the first hour, so the play is not an immediate dump of the
curved token; the creator commits ~85 SOL to force the pool over the threshold
and holds. Median instant-grad creator net is +85.0 SOL spent (the forced buy
itself), not extracted. The value extraction, if any, happens post-migration on
PumpSwap, which our day-of curve window does not see.

**Hypothesis (b): non-creator demand as quality signal — CONFIRMED, this is the
strongest filter found in Step 1.** Share of tokens with positive net non-creator
SOL in the first hour, by outcome bucket:
- died_zero: 2.9% (p75 = p90 = 0; dead tokens are near-total creator-only books)
- graduated: 38.7%
- graduated, organic subset (grad >= 1 min or >2 trades, n=662): 60.4%, median
  net +0.39 SOL, median 25 distinct non-creator traders
- live_eod: 65.4%

fh_noncreator_traders distributions: graduated median 4.0 (organic subset 25),
died_zero median 4.0, live_eod median 3.0 — trader COUNT alone does not separate
outcomes; net directional demand does. died_zero tokens show zero real absorption
at p75 while live_eod shows +0.17 SOL at p75 and graduated organic shows +85 SOL
at p75 (the graduation buy crosses over into this cohort's window).

**Hypothesis (c): creator first-sell timing — DISCONFIRMED as a discriminator.**
Creators who sell within the first hour do so <=1 min after create at similar
rates across buckets: graduated 72.4%, died_zero 69.1%, live_eod 63.6%. Early
creator selling is the default behavior everywhere, not a scam marker by itself.

**Analyst reading:** the first-hour observable that actually separates outcomes
is net non-creator SOL demand (real absorption by wallets other than the
creator), and secondarily distinct non-creator trader count on the organic-grad
subset. Both are computable in real time from the bonding-curve trade stream.
The self-graduation signature (single trade, instant, creator-funded ~85 SOL)
identifies the 62% of graduations that are manufactured and can be excluded or
down-weighted rather than chased. Next data need: post-migration PumpSwap
outcomes for the 1,048 graduates (did the token survive or drain after
graduation), which is the true payoff variable for a post-grad entry strategy.

---

## Addendum D — Post-graduation PumpSwap outcomes (2026-09-22)

**Data:** step1_postgrad.json (execution 01M34E57C4DZQ6EHX91G391ZEA). Source
correction discovered here: pumpdotfun_solana.base_trades is bonding-curve-ONLY
(every row carries project_main_id = 6EF8... pump program, none carry the AMM
id pAMM...). Post-migration activity lives in pump_amm_evt_buyevent /
pump_amm_evt_sellevent, keyed by pool; pool -> mint mapping via
pump_amm_evt_createpoolevent (base_mint). Aggregate post-grad AMM stats pulled
for all 1,125 Sep-20 graduation mints (100% coverage, 0 missing).

**Post-graduation outcome of 1,125 graduates (min pool SOL as fraction of max
pool SOL after migration, plus buy/sell net):**
- drained (min < 10% of max): 942 (83.7%)
- weak (min >= 10% of max, not strong): 94 (8.4%)
- strong (min >= 50% of max AND net sells <= buys): 12 (1.1%)

Median min/max ratio across all graduates: 0.016 — the typical "graduated"
token loses ~98% of its AMM liquidity at some point post-migration. Graduation
is NOT a safe harbor; it is the START of the dump phase for most tokens.

**First-hour signal vs post-grad outcome:**
- Drained post-grad (n=567 with fh): 84.0% were instant self-grads; only 26.3%
  had any positive first-hour non-creator net; median 0 non-creator traders.
- Alive post-grad (n=72 with fh): 22.2% instant self-grads; 44.4% positive
  non-creator net; median 29 non-creator traders.
- Strong survivors (n=12): median 0 non-creator traders — these are almost
  all single-holder tokens where one wallet holds the entire supply and no one
  ever sells (no liquidity event = no drain). Not tradeable alpha; a survivor
  bias artifact of no-activity tokens.

**Refined analyst reading:** instant self-graduation is ANTI-predictive of
post-grad survival (84% of post-grad drains are instant self-grads, vs 22% of
tokens still alive). The organic-grad subset (>= 1 min, >2 trades) is where any
tradeable tail lives, and even there, only ~1-8% retain meaningful AMM
liquidity post-migration. The effective "tradeable success" funnel for the
day is: 30,783 creates -> 662 organic grads (2.1%) -> ~94 still holding 10%+
liquidity post-migration (0.3%) -> ~1% truly strong. Any filter strategy must
be priced against these nested base rates, and the strategy's payoff variable
is post-migration survival, not graduation itself.

---

## Addendum E — Timestamp verification and multi-day window (2026-09-22)

**Timestamp truncation caveat RESOLVED.** Helius block-level spot check
(helius_timestamp_check.py, 5 instant-grad mints, exact graduation tx ids from
Dune): Helius blockTime matches Dune evt_block_time to the second for all 5
(delta 0s). The ':00.000' pattern is 1.3% of grad times / 1.8% of create
times — uniform seconds distribution, genuinely round timestamps, NOT a
truncation artifact. Sub-minute grad timing from Dune is trustworthy at
second resolution. (Note: Solana blockTime is second-granularity by protocol;
sub-second ordering inside a block comes from tx_index, available in Dune
columns evt_tx_index / tx_index if ever needed.)

---

## Addendum F — 8-day cross-day stability (2026-09-22)

**Window:** 2026-09-13 .. 2026-09-20 (8 days, 260,980 launches, 8,194
graduations). Sep-15 postgrad was pulled last after two driver bugs (missing
`import json` crash; the 1-row stale file slipping the earlier zero-row-only
re-pull rule — driver now re-pulls any postgrad file under 5KB). All 8 days
have postgrad rows == graduations.

Per-day table (from step1_crossday.py; full JSON in
research/meme_launch_filter/step1_crossday_summary.json):

| day | launches | grads | died | live | grad% | instant-grad% | died net>0% | live net>0% | organic net>0% | drain% |
|---|---|---|---|---|---|---|---|---|---|---|
| 09-13 | 24,923 | 950 | 5,744 | 18,229 | 3.8 | 58.4 | 1.7 | 60.2 | 42.7 | 50.1 |
| 09-14 | 29,759 | 945 | 7,007 | 21,807 | 3.2 | 59.8 | 1.3 | 60.0 | 44.4 | 52.2 |
| 09-15 | 34,459 | 1,001 | 5,311 | 28,147 | 2.9 | 52.8 | 1.8 | 62.3 | 51.5 | 47.5 |
| 09-16 | 34,102 | 1,056 | 3,890 | 29,156 | 3.1 | 54.5 | 3.4 | 65.2 | 55.6 | 46.6 |
| 09-17 | 38,946 | 1,101 | 4,339 | 33,506 | 2.8 | 54.9 | 2.9 | 60.6 | 54.8 | 45.5 |
| 09-18 | 36,004 | 1,044 | 5,108 | 29,852 | 2.9 | 59.3 | 1.8 | 63.1 | 48.5 | 49.2 |
| 09-19 | 32,004 | 1,049 | 4,669 | 26,286 | 3.3 | 54.4 | 2.9 | 61.5 | 56.8 | 51.3 |
| 09-20 | 30,783 | 1,048 | 4,271 | 25,464 | 3.4 | 59.2 | 2.9 | 65.4 | 60.4 | 54.1 |

**Signal stability verdict: the pilot day was not a fluke.** Every headline
metric sits in a narrow band across 8 days:

- Graduation rate 2.8-3.8% (mean 3.2%).
- Instant self-grad share of graduations 52.8-59.8% (mean 56.7%).
- died_zero share with positive non-creator first-hour net: 1.3-3.4%
  (mean 2.3%) vs live_eod 60.0-65.4% (mean 62.3%) — the first-hour
  non-creator-net filter holds everywhere, with a gap of roughly 58-63
  percentage points every single day.
- Post-grad drain rate 45.5-54.1% (mean 49.6%); drained tokens are 79-87%
  instant grads (mean 82.4%) on every day — instant self-grad is
  anti-predictive of survival on every day, not just the pilot.
- Organic grads with positive non-creator net: 42.7-60.4% (mean 51.8%).

Pooled: 8,194 graduations, 4,056 drained (49.5%), 583 still holding >= 10%
max pool liquidity at last observation, ~503 partials. The tradeable
survivor pool is roughly 70/day, so the pre-registered gate (>= 300
filtered entries) needs ~4-5 days of survivors at minimum, but with
filtering losses it will likely need the full 3-month window.

---

## Addendum G — Full September month pulled (2026-09-23)

**Window:** 2026-09-01 .. 2026-09-22 (22 days, 683,835 launches, 22,494
graduations, 11,784 post-grad drains, 1,539 still holding >= 10% max pool
liquidity). Month-by-month approach chosen by user (full 2-3 months in one
run would be too slow).

**Pull incident:** step1_trades.sql / step1_firsthour.sql had a hardcoded
upper time bound '2026-09-21'. Effect: days 01-20 scanned trades day-of +
up to 20 follow-on days (harmless: non-graduates stop trading within hours;
graduates excluded post-grad); Sep-21 itself got an empty window. Fixed to
`block_time < day + 1 day` in templates; Sep-21 trades re-pulled (33,557
rows); one transient Dune DNS failure on the Sep-21 firsthour fetch repaired
by the resumable driver's new zero-row re-pull rule (now applies to all pull
kinds, not just postgrad). Sep-22 pulled as a complete day on 2026-09-23.

**22-day cross-day table** (step1_crossday.py, full JSON in
research/meme_launch_filter/step1_crossday_summary.json):

| day | launches | grads | died | live | grad% | inst% | died net>0% | live net>0% | org net>0% | drain% |
|---|---|---|---|---|---|---|---|---|---|---|
| 09-01 | 36,202 | 1,063 | 1,740 | 33,399 | 2.9 | 46.8 | 6.2 | 66.4 | 70.1 | 49.9 |
| 09-02 | 33,508 | 944 | 2,317 | 30,247 | 2.8 | 51.9 | 3.7 | 62.6 | 63.4 | 52.6 |
| 09-03 | 33,030 | 1,040 | 2,369 | 29,621 | 3.1 | 50.2 | 5.0 | 63.9 | 58.8 | 51.4 |
| 09-04 | 29,492 | 960 | 2,063 | 26,469 | 3.3 | 57.5 | 8.0 | 61.1 | 58.0 | 57.2 |
| 09-05 | 21,187 | 926 | 1,909 | 18,352 | 4.4 | 58.5 | 8.1 | 61.7 | 50.3 | 57.1 |
| 09-06 | 22,327 | 888 | 1,740 | 19,699 | 4.0 | 65.7 | 5.4 | 59.4 | 49.3 | 59.8 |
| 09-07 | 26,953 | 1,033 | 1,728 | 24,192 | 3.8 | 58.6 | 6.5 | 65.3 | 60.6 | 57.8 |
| 09-08 | 29,463 | 1,063 | 1,694 | 26,706 | 3.6 | 61.5 | 4.3 | 60.7 | 47.3 | 54.2 |
| 09-09 | 34,184 | 1,189 | 5,909 | 27,086 | 3.5 | 59.3 | 1.5 | 63.6 | 48.0 | 55.3 |
| 09-10 | 31,198 | 1,062 | 4,634 | 25,502 | 3.4 | 54.6 | 1.9 | 61.0 | 49.0 | 53.5 |
| 09-11 | 28,546 | 969 | 3,446 | 24,131 | 3.4 | 55.8 | 2.8 | 59.2 | 48.3 | 50.8 |
| 09-12 | 28,998 | 1,033 | 6,885 | 21,080 | 3.6 | 58.2 | 1.7 | 59.3 | 43.8 | 51.9 |
| 09-13 | 24,923 | 950 | 5,744 | 18,229 | 3.8 | 58.4 | 1.7 | 60.2 | 42.7 | 50.1 |
| 09-14 | 29,759 | 945 | 7,007 | 21,807 | 3.2 | 59.8 | 1.3 | 60.0 | 44.4 | 52.2 |
| 09-15 | 34,459 | 1,001 | 5,311 | 28,147 | 2.9 | 52.8 | 1.8 | 62.3 | 51.5 | 47.5 |
| 09-16 | 34,102 | 1,056 | 3,890 | 29,156 | 3.1 | 54.5 | 3.4 | 65.2 | 55.6 | 46.6 |
| 09-17 | 38,946 | 1,101 | 4,339 | 33,506 | 2.8 | 54.9 | 2.9 | 60.6 | 54.8 | 45.5 |
| 09-18 | 36,004 | 1,044 | 5,108 | 29,852 | 2.9 | 59.3 | 1.8 | 63.1 | 48.5 | 49.2 |
| 09-19 | 32,004 | 1,049 | 4,669 | 26,286 | 3.3 | 54.4 | 2.9 | 61.5 | 56.8 | 51.3 |
| 09-20 | 30,783 | 1,048 | 4,271 | 25,464 | 3.4 | 59.2 | 2.9 | 65.4 | 60.4 | 54.1 |
| 09-21 | 34,755 | 1,064 | 4,525 | 29,166 | 3.1 | 55.3 | 2.2 | 65.1 | 57.3 | 53.4 |
| 09-22 | 33,012 | 1,066 | 4,177 | 27,769 | 3.2 | 60.2 | 2.0 | 64.0 | 54.0 | 52.7 |

**New analyst observation — regime shift around Sep 9.** died_zero counts
jump from ~1,700-2,300/day (Sep 1-8) to ~3,400-7,000/day (Sep 9-22) at
similar launch volumes, and the died-token share with positive first-hour
non-creator net falls from 3.7-8.1% to 1.3-3.4%. Something in the launch
environment changed around Sep 9 (candidate hypotheses: pump.fun parameter
or UI change, mayhem-mode rollout, bot-population shift). Cohorts before and
after Sep 9 must not be pooled blindly in Step 3/4; treat the boundary as a
known split and check the filter on both sides of it.

**All other headline metrics remain stable across the full month:**
graduation rate 2.8-4.4% (mean 3.3%), instant-grad share 46.8-65.7%
(mean 56.7%), post-grad drain rate 45.5-59.8% (mean 52.5%), drained tokens
72.6-88.7% instant grads (mean 81.6%). The first-hour non-creator-net gap
(live vs died) holds every single day: minimum live share 59.2%, maximum
died share 8.1%.

---

## Addendum H — Step 2 pilot: entry-bar features at graduation (2026-09-23)

**Design.** Entry archetype = graduation. Features per graduate from curve
trades STRICTLY BEFORE grad_time (no lookahead). Query: step2_featbar.sql;
pilot pull 2026-09-20 (1,048 rows). Instant self-grads (549/1048) have
empty pre-grad history and drop out naturally (NULL fb_* columns).

**Features computed at entry bar:** fb_trades, fb_traders, fb_buys/sells,
fb_buy/sell_sol, fb_noncreator_buy/sell_sol, fb_max_reserves,
fb_first/last_trade_time, fb_max_trader_share (per-trader volume share
max — cheap concentration proxy; note: volume share, NOT holder balance
share, and it can be 'NaN' string for all-sell-only histories).

**Pilot single-day signal scan (n=475 with-history grads with outcome):**

| feature | split | n | drain rate (min pool < 10% of max) |
|---|---|---|---|
| fb_traders | <= 3 | 3 | 1.00 |
| fb_traders | > 3 | 496 | 0.82 |
| fb_traders quartiles | Q1 (<=24) | 119 | 0.74 |
| | Q2 (25-39) | 120 | 0.72 |
| | Q3 (40-373) | 118 | 0.92 |
| | Q4 (>373) | 118 | 0.91 |
| fb_max_trader_share | <= 0.02 | 143 | 0.87 |
| | 0.02-0.05 | 214 | 0.76 |
| | 0.05-0.15 | 72 | 0.81 |
| | > 0.15 | 46 | 1.00 |
| non-creator net at bar | > 0 | 321 | 0.83 |
| | <= 0 | 154 | 0.81 |

**Analyst reading (pilot day, NOT a gate test):**

1. **Drain is the norm (~81%) even for pre-grad-popular tokens.** No
   feature split gets drain below ~72% on this day. The 10%-of-max drain
   label may be too harsh: alive tokens' pools sit at tiny liquidity
   (median min_pool_sol ~ 0.04) — the definition conflates "drained" with
   "quiet" (no event = no reserves change).
2. **U-shape in traders:** the LOWEST-trader quartile (Q1/Q2) drains LESS
   (0.72-0.74) than Q3/Q4 (0.91-0.92). Low-attention organic grads
   "survive" (often because nobody trades them again, not because there is
   an ecosystem); high-attention grads attract the dumpers. Q4's 0.92
   includes the mooned tokens (drawdown ≠ rug).
3. **fb_max_trader_share > 0.15 is the cleanest bad signal on this day**
   (0% survival, n=46): one wallet dominating entry-bar volume = near-
   certain dump. As an exclusion filter it is cheap and no-lookahead.
4. **The winner structure is lottery-shaped.** Of 90 alive graduates, the
   min pool SOL p90 is ~17.7 and ONE token sits at ~14,700 SOL min (its
   pool peaked ~114,600 SOL). There is no middle class: pools are either
   tiny/quiet or enormous/mooned. Implication: any exit rule must harvest
   the moon tail (the 1% that goes huge), not the median survivor.
5. **Drain labels for mooned tokens are polluted:** min/max ratio < 0.1
   for a 100k-SOL pool is a drawdown, not a rug. Post-grad outcome labels
   need an absolute-size component (e.g., drained AND max_pool_sol <
   threshold) to separate rags from moons.

**Next:** run step2_featbar for the full month (driver loop), then Step 2
analysis script (per-day funnel + signal scan) and the same outcome-label
refinement (drained + absolute max size).

## Addendum I — Step 2 full-month results and label corrections (2026-09-23)

**Data.** step2_featbar pulled for all 22 days (2026-09-01..09-22), 22,494
graduation rows, 11,361 with pre-grad trade history (50.5%). Rows with
fb_max_trader_share = 'NaN' (1,217) are a DATA ARTIFACT: every curve
trade in their history has zero SOL amount in base_trades (verified:
1,615 trades, all zero amounts, zero reserves) — degenerate source rows,
not a real archetype. They are excluded from the clean scan (n=10,144).

**Outcome label correction 1 (absolute moon threshold).** MOON_THRESH
50 SOL was wrong: pumpfun graduations seed their PumpSwap pool with the
curve's reserves (~85 SOL), so >=50 SOL is the DEFAULT state of every
graduate, not a moon signal. Threshold scan on pooled pg_max_pool_sol:
seed default explains the pilot's bizarre "44-47% mooned per day".
Corrected: MOON_THRESH = 200 SOL (~2.4x seed; only 6.7% of graduates'
pools ever exceed 200 SOL). Monthly outcome funnel (clean rows):

| outcome | n | share |
|---|---|---|
| drained_small (min < 10% max, max < 200 SOL) | 8,834 | 77.8% |
| mooned (min < 10% max, max >= 200 SOL) | 692 | 6.1% |
| retained (min >= 10% max) | 1,835 | 16.2% |

**Outcome label correction 2 (drain definition unchanged but now safe).**
The 10%-of-min/max rule still conflates moons' drawdowns with rugs ONLY
for pools >= 200 SOL; those are now split into their own class, so
drained_small is a genuine "was small and died" label.

**Pilot signal reversal (fb_max_trader_share).** The pilot's "cleanest"
bad signal (share > 0.15 -> 0% survival, n=46) does NOT hold over the
month: monthly drain rate for share > 0.15 is 86.2% (n=1,122) vs 80.2%
base — only +6pts, and its moon rate (8.7%) is nearly double base (4.5%).
One dominant wallet at the entry bar is NOT a clean exclusion on the
month; it coexists with the moon tail. Do not use it as an exclusion.

**Monthly signal scan (clean n=10,144, pooled all 22 days):**

| split | n | drain | moon | retained |
|---|---|---|---|---|
| BASE | 10,144 | 0.802 | 0.045 | 0.152 |
| fb_traders < 25 (Q1) | 2,593 | 0.764 | 0.023 | 0.213 |
| fb_traders 25-40 (Q2) | 3,218 | 0.764 | 0.013 | 0.223 |
| fb_traders >= 40 (Q3/Q4) | 4,333 | 0.854 | 0.082 | 0.064 |
| noncreator_net > 0 | 6,400 | 0.797 | 0.067 | 0.136 |
| noncreator_net <= 0 | 3,744 | 0.812 | 0.007 | 0.180 |
| share > 0.15 | 1,122 | 0.862 | 0.087 | 0.051 |

**Analyst reading:**

1. **Nothing in the entry-bar feature set drops drain below ~74%** at any
   usable selectivity. The monthly picture is far more uniform than the
   pilot day suggested: ~80% of graduates get drained regardless of
   pre-grad popularity or demand balance. The "good" outcomes (moon +
   retained) are ~21% pooled.
2. **The U-shape DOES hold monthly, and it is a MOON shape, not a
   survival shape.** Q3/Q4 (>= 40 pre-grad traders): drain 85.4% but
   moon 8.2% vs 2.3-2.5% for Q1 — nearly 2x base moon rate, capturing
   357/459 moons (78%) at 42.7% selectivity. High pre-grad attention is
   the lottery-ticket class; low attention is the quiet-death class
   (Q1: moon only 2.3%, retained 21.3%).
3. **Noncreator net <= 0 is a genuine anti-moon exclusion:** moon rate
   0.7% vs 4.5% base (6x lower), n=3,744 (37% selectivity). Monthly it
   is consistent pre- and post-Sep-9 (0.3% and 1.3% respectively). But
   its drain rate (81.2%) equals base — it excludes losers AND winners,
   so it only prunes the lottery tail, it does not improve the median.
4. **Regime stability:** pre/post Sep-9 signal directions are consistent
   (Q4 moon 7.2% vs 12.8%; net<=0 moon 0.3% vs 1.3%) — the Sep-9 regime
   shift changed the level (died_zero counts, died-net-share) but not
   the direction of entry-bar signals.
5. **Top-of-month pool sizes** (pg_max_pool_sol): 475k, 355k, 182k,
   115k, 99k, 80k, 78k, 57k, 51k, 49k SOL. The moon tail is real,
   extreme, and the only economic reason to play this game.

**Verdict for Step 3 gating.** Entry-bar features alone are an
ATTENTION classifier (moon-rate modifier), not a rug filter: drain ~80%
everywhere. The tradeable edge, if any, must come from (a) position
structure that survives the 80% drain while harvesting the moon tail
(moon 6.1% of all grads; t>=40 + net>0 subset: 9.1%), plus (b) the
step-1 first-hour non-creator-net signal which operates at a DIFFERENT
bar (pre-grad) than these features (at-grad). Next: Step 3 naive
baseline sim (buy every with-history grad, fixed size/exit) to get the
loss-drift baseline, then Step 4 adds exclusions (net<=0, share>0.15,
t<25) as moon-rate modifiers and re-scores.

---

## Addendum J — Step 3 naive baseline sim, full September (2026-09-23)

**Data basis.** All 22 September days pulled as 1-min OHLC bars per
graduate pool, first 24h post-grad (`step2_paths.json`, ~150k-230k rows
per day, ~3.86M bars total). All 22 files verified parseable and
`QUERY_STATE_COMPLETED`. Data caveats carried from Addendum I: per-bar
volume figures implausible in absolute SOL but internally consistent;
exits depend on reserves/OHLC, not volume, so the sim is unaffected.

**Frozen sim parameters (spec Section 5, pre-registered):** 1 SOL
notional per graduate; fee 0.25%/side; slippage 0.5%/side; 0.02 SOL
failed-tx allowance; TP: sell 50% at +50% from entry then trail the
rest with peak minus 2.0 x ATR(15, 1-min true range); hard 24h time
stop at last bar close; exit fills capped at 0.9 x pool quote reserves
at the bar (rug realism). No entry filters (naive population = every
graduate with path data). Bootstrap 10k resamples, seed 20260923.

**Implementation.** `src/quant_scripts/meme_launch_filter/step3_sim.py`;
per-trade records in `research/meme_launch_filter/step3_sim_trades.jsonl`,
summary in `step3_sim_summary.json`.

**Results (24,793 trades):**

| metric | pooled | pre Sep-9 | post Sep-9 |
|---|---|---|---|
| n | 24,793 | 8,840 | 15,953 |
| mean net (SOL per 1 risked) | -0.245 | -0.289 | -0.221 |
| median net | -0.210 | -0.242 | -0.197 |
| bootstrap p5 of mean | -0.265 | -0.299 | -0.251 |
| hit rate | 0.368 | 0.352 | 0.377 |
| mean excl top 1% | -0.292 | -0.314 | -0.279 |

Exit-reason breakdown: trail_stop (n=12,252, mean -0.372),
trail_stop_after_tp (n=12,474, mean -0.119), time_stop (n=31, mean
-0.872), time_stop_after_tp (n=36, mean -0.222). Nearly all trades hit
the trailing stop; roughly half of those got there after the TP leg.

**Analyst reading:**

1. **The naive buy-every-graduate strategy loses -0.245 SOL per 1 SOL
   risked with tight bootstrap bounds.** This is not noise: the p5 of
   the mean is -0.265, and dropping the best 1% of trades makes it
   worse (-0.292), so the mean is not propped up by moon winners. The
   loss is broad-based across both regimes and essentially every day.
2. **The trailing stop is the binding constraint, not the rug.** Trades
   that hit TP first lose much less on average (-0.119) than
   never-TP trades (-0.372). The ATR(15) x 2.0 stop is being hit on
   noise within minutes on virtually every trade; the stop distance is
   far tighter than the 1-min volatility of these tokens.
3. **Cost drag is minor relative to signal.** Fees + slippage + failed-tx
   allowance total ~0.075 SOL of the ~0.245 loss; the rest is adverse
   selection (the ~80% drain base rate) expressing itself through the
   exit structure.
4. **Consistency with the label picture:** funnel said 80.2% drained /
   4.5% mooned / 15.2% retained. A strategy that buys everything and
   cuts at -2 ATR on 1-min noise converts the 80% drain base rate into
   a near-certain per-trade loss, with hit rate 36.8% coming from the
   short-lived bounces, not from survival to moon.

 **Verdict per Section 7 gate:** the naive baseline FAILS decisively
 (-0.245 mean, bootstrap p5 -0.265, both regimes negative). No amount of
 position-sizing fixes a -24.5% edge; only entry filtering that materially
 changes the outcome mix can. Step 4 (filtered sim) must show a mean net
 confidently above 0 with n large enough to matter; the candidate filters
 from Addendum I are noncreator_net > 0 (anti-moon exclusion), Q3/Q4
 pre-grad attention (moon-rate modifier), and drop of fb_max_trader_share
 > 0.15 exclusion (which monthly data REVERSED). Expected next search:
 whether the attention-class U-shape (t >= 40) plus net > 0 shifts the
 exit mix enough to cross zero, given the moon tail is the only payoff.
## Addendum K - Step 4 filtered entry sim, full September (2026-09-23)

**Design.** Identical exit engine and frozen params as Step 3
(Addendum J). Entry populations filtered by pre-registered Addendum I
signals. featbar exists only for grads with pre-grad history (~50%);
share=NaN artifact rows excluded (Addendum I data-artifact finding).
Implementation: `src/quant_scripts/meme_launch_filter/step4_filtered_sim.py`;
trades `step4_sim_trades.jsonl`, summary `step4_sim_summary.json`.

**Method note (bug caught):** first run produced impossible numbers
(A_base mean +3.93 SOL) because bars were not sorted by minute_ts
before simulating - the unsorted path let the trailing-stop logic
sell moon-era prices against early-entry token counts (look-ahead).
Fixed by sorting in the loader; results below are from the fixed run.
The bug was caught by a sanity bound: removing 14% of a population
whose per-trade loss is capped near -1.02 cannot move the mean from
-0.245 to +3.93.

**Results (mean net SOL per 1 risked; bootstrap p5 in parens):**

| variant | n | pooled | pre Sep-9 | post Sep-9 | hit |
|---|---|---|---|---|---|
| A base_clean (all with featbar) | 21,277 | -0.184 (-0.207) | -0.215 (-0.226) | -0.167 (-0.200) | 0.405 |
| B net > 0 | 6,400 | -0.251 (-0.321) | -0.321 (-0.344) | -0.211 (-0.318) | 0.290 |
| C attention t >= 40 | 4,333 | -0.114 (-0.132) | -0.097 (-0.126) | -0.124 (-0.146) | 0.405 |
| D t >= 40 AND net > 0 | 3,790 | -0.082 (-0.102) | -0.084 (-0.115) | -0.081 (-0.105) | 0.420 |

Exit-reason detail (D): trail_stop_after_tp n=2,205 mean +0.266;
trail_stop n=1,585 mean -0.565. For C: +0.202 / -0.571. For A:
-0.022 / -0.333.

**Analyst reading:**

1. **The anti-moon exclusion is confirmed harmful as a STANDALONE entry
   filter (B worse than A).** It removes the lottery tail: noncreator
   net <= 0 grads almost never moon (Addendum I), so excluding them
   sounds protective, but the sim shows the net>0 class carries the
   drain exposure without enough extra moon payoff to compensate at
   these exit rules.
2. **The attention filter (C) and combined (D) move expectancy strongly
   in the right direction** (from -0.184 to -0.114 / -0.082) and are
   regime-stable. The moon-tail capture works: within D, the 58% of
   trades that reach +50% TP average +0.27 net; the 42% that never TP
   average -0.57.
3. **The remaining loss lives in the EXIT, not the entry.** D's no-TP
   branch (-0.565) is worse than A's (-0.333): high-attention tokens
   that fail, fail violently. The trail after TP gives back too much
   on the winners' second leg. The entry filter finds the lottery
   class; the exit engine cannot yet harvest it.
4. **Paper-feature gap:** the Mazorra et al. (2022) discriminative
   features (HHI of LP/token distribution, average clustering
   coefficient of the transfer graph) are NOT in the current featbar -
   they need token Transfer-event pulls per graduate. That is the next
   data extension if filter search continues; the current entry bar
   only has attention/demand-balance features.

**Verdict per Section 7 gate:** entry filtering DIRECTION confirmed
but the gate still fails (D p5 -0.102 < 0). Next procedure, in order:
(1) small pre-registered exit-structure sensitivity on D only - no
grid search, three variants: current, TP-only-with-time-stop (no
trail), and TP-then-breakeven-stop; (2) if none cross zero, the moon
tail needs its own harvest path (longer horizon / wider stop) before
more entry filters are tried.
## Addendum M - exit sensitivity, the instant-grad class, and first positive config (2026-09-23)

**Exit-structure sensitivity on D population (n=3,790, pre-registered 3
variants, no grid search):** V1 current trail -0.074 (p5 -0.095, hit
0.421); V2 TP +50% then ride to 24h close -0.347 (hit 0.052); V3 TP
then breakeven stop -0.067 (hit 0.548). Wider-harvest variants: W1
ATR-mult 4.0 trail -0.160; W2 fixed -35% stop + TP +50% + breakeven
-0.043 (p5 -0.098); W3 same with TP +100% -0.069. No exit structure
crosses zero on D. V2's 5.2% hit rate shows the never-TP branch dies
to near-zero; the trail gives back the winners' second leg. Conclusion:
the remaining loss lives in the exit AND in the population - diagnosed
next.

**Moon-tail composition diagnostic.** NONE of the month's top-10 pools
(475k, 355k, 182k, 115k, 99k, 80k, 78k, 57k, 51k, 49k SOL) pass D.
Nine have fb_max_trader_share = NaN; the one decodable token (FH8dMyGZ,
475k SOL) has only 20 pre-grad traders. Direct probe of base_trades for
NaN mints: 272-832 real trade rows per mint, 100% with zero amounts and
zero reserves, bonding windows 2-6 minutes - a per-token amount-
decoding gap in Dune's base_trades for fast v2 curves, not phantom
data. Any feature-gated filter silently removes these tokens.

**Full-population label recount (canonical classify, 24,793 unique
graduates):** drained_small 13,819 (55.7%), mooned 8,529 (34.4%),
retained 2,445 (9.9%). Addendum I's funnel (77.8/6.1/16.2) describes
only the clean-with-history subset (n=10,144); it does not extrapolate.

**The decisive split.** featbar classes pooled:

| class | n | moon rate |
|---|---|---|
| fb_trades > 0, share clean | 11,361 | 6.1% |
| fb_trades = 0 (zero-amount decode gap) | 11,133 | 69.6% |
| (their labels) | | drained 13.0%, retained 4.6% |

The zero-trades class is 99.99% age_at_grad_s <= 60 (instant-grad
tokens: graduation within a minute of creation). Their moon rate is
69.6% with median peak pool 436 SOL; the clean class in the same age
bucket moons at 8.6%. The decode-gap class IS the moon tail.

**Step 5 sim - instant-grad class, naive Step 3 exit engine, no
filters (implementation step5_instantgrad_sim.py; trades
step5_instantgrad_trades.jsonl, summary step5_instantgrad_summary.json):**

| metric | pooled | pre Sep-9 | post Sep-9 |
|---|---|---|---|
| n | 11,133 | 3,858 | 7,275 |
| mean net (SOL per 1 risked) | +0.025 | +0.004 | +0.036 |
| median net | +0.020 | | |
| bootstrap p5 of mean | +0.017 | | |
| hit rate | 0.570 | | |
| mean excl top 1% | +0.000 | | |

Exit mix: trail_stop (no TP) n=7,578 mean -0.162; trail_stop_after_tp
n=3,543 mean +0.421; time_stop_after_tp n=10 mean +1.05.

**Analyst reading:**

1. **First positive pooled config of the study** (p5 +0.017 > 0), and
   direction-consistent across regimes, but weakly pre-regime.
2. **The expectancy is a lottery-tail harvest, not a smooth edge:**
   excluding the best 1% of trades collapses the mean to ~0. The
   strategy's profit is entirely the 113-trade tail. Expect high
   variance and long flat stretches; per-trade edge is small.
3. **Entry realism is the binding caveat.** The class graduates within
   60s of creation; the sim buys at the first 1-min bar open with 0.5%
   slippage and 0.02 SOL failure cost. Capturing that bar requires a
   bot watching PumpSwap graduations in real time, competing with
   snipers - this is not a manual-retail edge; it is a bot-infrastructure
   edge. Failed-tx and priority-fee costs at that contested bar are
   likely higher than modeled.
4. **Decode gap caveat:** for these tokens Dune's base_trades carries
   no amounts, so the sim runs on pool OHLC/reserves only (which decode
   fine). Features are not computable for this class, so no further
   entry filtering is possible until a Helius raw-log rebuild exists.
5. **Label sanity:** the 69.6% moon rate is not a labeling bug - the
   >=200 SOL threshold scan and pg_max_pool_sol are computed from pool
   reserves, independent of the trade-amount decode gap.

**Verdict per Section 7 gate:** the instant-grad naive config PASSES
the expectancy gate on-paper (p5 > 0, both regimes non-negative) but
the gate is not yet cleared honestly: (a) expectancy depends on the
top-1% tail; (b) entry realism (slippage/failure at the contested first
bar) is unvalidated; (c) the decode gap means we cannot yet filter
within the class. Pre-registered next: (1) Helius probe of one instant-
grad token's first-minute logs to measure real fill feasibility;
(2) sensitivity of the result to entry cost (slippage 1-3%, failure
0.05-0.2 SOL) - if it survives, this is the candidate edge; (3) only
then, live-size paper trading.

## Addendum N - cost-sensitivity sim and Helius fill probe (2026-09-23)

**Step 6 entry-cost sensitivity (implementation
step6_cost_sensitivity.py; summary step6_cost_sensitivity_summary.json).**
Instant-grad class (n=11,133), identical naive exit engine, grid
slippage {0.01, 0.02, 0.03} x failed-tx cost {0.05, 0.1, 0.2}:

| combo | mean net | p5 | hit |
|---|---|---|---|
| slip 1% fail 0.05 | -0.015 | -0.023 | 0.440 |
| slip 1% fail 0.10 | -0.065 | -0.073 | 0.338 |
| slip 1% fail 0.20 | -0.165 | -0.173 | 0.256 |
| slip 2% fail 0.05 | -0.035 | -0.043 | 0.389 |
| slip 2% fail 0.10 | -0.085 | -0.093 | 0.313 |
| slip 2% fail 0.20 | -0.185 | -0.193 | 0.239 |
| slip 3% fail 0.05 | -0.055 | -0.063 | 0.351 |
| slip 3% fail 0.10 | -0.105 | -0.113 | 0.297 |
| slip 3% fail 0.20 | -0.205 | -0.213 | 0.225 |

**Gate verdict: FAIL.** Every combo in the pre-registered grid is
negative; even the mildest harsher case (1% slippage, 0.05 SOL
failure) flips the mean to -0.015 with p5 -0.023. The +0.025 mean from
Addendum M was entirely an artifact of the optimistic 0.5% slippage +
0.02 SOL failure assumption. On per-trade Solana economics, the
instant-grad "edge" is +2.5% per 1 risked ONLY under entry costs at or
below the modeled 0.5%-slippage tier, and the 1% gridpoint at the same
failure tier would need ~+0.015 mean to break even; the measured
drop from 0.5% to 1% slippage (-0.04 per 1% of added slippage) is
consistent with a near-full pass-through of entry price into fills.
The strategy does not survive realistic entry costs. Combined with the
top-1%-tail dependence, the on-paper config is dead on both realism
and robustness grounds.

**Step 7 Helius raw-log probe (implementation step7_helius_probe.py;
raw summary step7_helius_probe.json).** Three largest instant-grad
tokens by pg_max_pool_sol (F2reRYPQ 19.7k SOL, VEY71Uj9 18.8k SOL,
QTw25puR 17.6k SOL). Method: getSignaturesForAddress on the MINT
address, paged back to create_time + 120s, then getTransaction
(jsonParsed) samples.

Findings:

1. **The mint address is nearly silent in the curve phase.** Only 4 /
   159 / 625 signatures in the first 120s despite 27k-142k total
   lifetime trades. Pump.fun bonding-curve trades hit the curve PDA,
   not the mint; a launch filter that subscribes to the mint via
   websocket would see almost nothing until migration.
2. **The sampled first-window txs are mostly wallet setup, not
   trades.** Dominant instruction mix: createIdempotent (ATA), token
   transfers, syncNative, closeAccount, plus SOL transfers. PumpSwap
   Buy/Sell instruction logs ARE present and parseable
   (Instruction: Buy under pAMMBay...), with full program logs.
3. **Some tokens migrate almost instantly.** QTw25puR trades at t+110s
   already execute on PumpSwap AMM, not the bonding curve - consistent
   with the instant-grad class definition (graduation <= 60s after
   creation).
4. **The signature history for a single mint is deep** (tens of
   thousands of txs), so full per-token raw rebuilds via
   getSignaturesForAddress/getTransaction would be API-cost-prohibitive
   at scale (11k tokens/month); viable only for targeted (dozens of
   tokens) verification, not the whole universe.

Implication for the decode gap: rebuilding trade amounts for the
zero-class would require subscribing to the bonding-curve PDA and
PumpSwap program logs in real time (websocket) or batch Geyser/grpc
streams - both are professional-infrastructure tier, not a retail
Dune-only path. The probe confirms the Dune base_trades gap is a real
decoding limitation of the Dune decomposition, not missing on-chain
activity.

**Study verdict at the September horizon:** no filter configuration
tested (naive, feature-gated A-D, exit variants V1-V3/W1-W3, or
instant-grad class) survives (a) realistic entry costs AND (b)
exclusion of the top-1% tail simultaneously. The remaining unexplored
directions, in decreasing priority: (1) August 2026 as an
out-of-sample month (month-by-month pulls, per Addendum L) to test
whether the instant-grad moon rate and the cost-gate failure replicate
on an earlier regime; (2)
PumpSwap-side (post-migration) entry sim for the instant-grad class at
the migration bar using OHLC (same cost-sensitivity caveat applies);
(3) raw-log rebuild for a targeted token subsample to enable true
within-class features. None of these changes the Section 7 gate: the
burden of proof is a config that survives cost sensitivity
pre-registered, and nothing has cleared it.

## Addendum O - August 2026 out-of-sample pull and replication (2026-09-24, COMPLETE)

**Purpose:** replicate the September findings (instant-grad moon rate
69.6%, cost-gate failure) on an earlier regime, per the month-by-month
pre-registration (Addendum L). Pipeline unchanged: per day the three
analysis-critical queries (step1_postgrad, step2_featbar, step2_paths)
generated from the 2026-09-13 SQL templates with the date literal
swapped (implementation step8_august_pull.py). Featbar fallback to a
v1-only launches CTE exists but was NOT needed - the v2 create table
covered August fine.

**Pull status:** first key exhausted datapoints mid-month (HTTP 402);
user replaced the key and the pull resumed cleanly (Aug-12 paths
recovered by polling the submitted execution, no re-submission). All
31 days complete: postgrad 941-1557 rows/day, featbar 785-1372, paths
132k-257k bars. Featbar v1-only fallback never needed.

**Replication results (implementation step9_august_replication.py;
summary step9_august_replication_summary.json), canonical labels:**

| class | n | moon rate | drained | retained |
|---|---|---|---|---|
| fb_trades = 0 (zero class) | 10,792 | 77.3% | 21.8% | 0.9% |
| fb_trades > 0 (clean) | 23,421 | 5.6% | 78.7% | 15.7% |

Zero class: 99.99% age_at_grad_s <= 60 (median 0s) - instant-grad
class replicates exactly. Its moon rate is HIGHER than September's
69.6% (77.3%); clean class matches (5.6% vs 6.1%).

**Cost-sensitivity grid on the August instant-grad class (n=10,792,
same naive exit engine):**

| combo | mean net | p5 | hit |
|---|---|---|---|
| Addendum M optimistic (0.5% slip, 0.02 fail) | +0.019 | +0.009 | 0.544 |
| slip 1% fail 0.05 | -0.021 | -0.031 | 0.467 |
| slip 1% fail 0.10 | -0.071 | -0.081 | 0.385 |
| slip 1% fail 0.20 | -0.171 | -0.181 | 0.293 |
| slip 2% fail 0.05 | -0.040 | -0.050 | 0.424 |
| slip 2% fail 0.10 | -0.090 | -0.100 | 0.364 |
| slip 2% fail 0.20 | -0.190 | -0.200 | 0.276 |
| slip 3% fail 0.05 | -0.059 | -0.069 | 0.395 |
| slip 3% fail 0.10 | -0.109 | -0.119 | 0.342 |
| slip 3% fail 0.20 | -0.209 | -0.219 | 0.258 |

**Two-regime verdict: the September cost-gate failure REPLICATES on
August.** The on-paper positive config is again positive only under
the optimistic cost tier (+0.019, p5 +0.009) and again dies at every
realistic combo, with the same ~-0.04-to--0.05 per-1% slippage
sensitivity. The class split itself is stable across two regimes
one month apart: instant-grad tokens are the moon tail in both.

**Study conclusion at the two-regime horizon:** launch-sniping /
graduation-bar entry on pump.fun is a bot-infrastructure lane whose
on-paper expectancy does not survive realistic entry costs in either
regime. No Dune-grade retail filter tested clears the Section 7 gate.
The finding is now structural, not regime-specific. Remaining
directions unchanged in priority: PumpSwap-side migration-bar entry
sim (expect same cost failure), targeted raw-log rebuild for
within-class features (professional tier), or pivoting the research
question to post-migration retention.

- COMPLETE: Aug 1-12 postgrad+featbar, and paths for Aug 1-11, Aug 31
  (12 days fully done).
- PARTIAL: Aug 12 (postgrad + featbar done; paths execution
  01M39BSETP4NHSH7QKWPRWG853 submitted, results fetch blocked by 402).
- NOT STARTED: Aug 13-30.

Resume rule: poll the submitted Aug-12 paths execution id (burns no new
datapoints); do NOT re-submit queries for completed/partial days. A
fresh key or raised datapoint limit resumes the remaining days.

Volume note: late August (25-29) ran hotter (1,100-1,550 grads/day),
converging toward September levels - the "regime" difference is mostly
calendar position, not market structure.

## Addendum P - study verdict, final pre-registration, and closure rule (2026-09-24)

**Study verdict (two regimes, pre-registered gates, no config
survived):** launch-sniping / graduation-bar entry on pump.fun is a
bot-infrastructure lane. The only on-paper positive configuration
(instant-grad class, optimistic entry costs) died under the
pre-registered cost grid in both September (Addendum N) and August
(Addendum O), and its expectancy was a top-1% lottery-tail harvest in
both. The class split replicating across regimes (69.6% / 77.3%
instant-grad moon rate; 6.1% / 5.6% clean moon rate) establishes the
structure as stable, not anomalous. Retail on Dune-grade data has no
tested edge in this lane; the Helius probe (Addendum N) shows the
contested bar requires professional real-time infrastructure.

**Final test pre-registration - post-migration retention study
(Addendum Q, below).** Rationale: the launch-sniping lane is closed on
data; the retained class (Sept 9.9% / Aug 15.7% of graduates) is the
slow-side population where a retail-suitable information edge could
still exist: no contested bar, holding horizon hours-to-days, features
computable from already-pulled data. This is the LAST test in this
study. Pre-registered BEFORE any test ran:

- Population: all graduates (both months, both classes) whose pool
  survives >= 60 min post-graduation (liquidity still > 10% of peak at
  t+60m). This excludes the instant-grad lottery class by construction
  and targets the slow lane.
- Entry: first bar AFTER t+60m (no lookahead, no contested bar). Exit
  engine: the SAME frozen naive engine (Section 5 params), unchanged.
- Edge hypothesis: among entry-bar observable features (pool SOL at
  t+60m, first-hour noncreator buy/sell balance, trader count,
  creator concentration), at least one pre-registered split separates
  a group with positive mean net AND positive p5 under the SAME
  cost-sensitivity grid as Addendum N (1-3% slippage, 0.05-0.2 fail).
- Gate: the SAME Section 7 gate. A config passes only if mean net > 0
  AND boot p5 > 0 at 1% slippage AND 0.05 SOL failure cost (the
  mildest realistic tier), pre- and post-Sep-9 regime consistent.
- Closure rule: if no pre-registered split passes, the study closes
  with the verdict "no retail edge found in pump.fun graduation-cycle
  trading at Dune-grade data on either the fast (sniping) or slow
  (retention) lane, two regimes tested". No further configurations
  will be tested - closing the door on result-driven gate-moving.

Multiple-split honesty: the features listed above are ALL splits that
will be tried; this is a small fixed family (<= 8), chosen before
looking at any outcome data on the filtered population. The best-of
family result must survive a Bonferroni-style correction (the p5 gate
applies to the best split with the family size as the effective
multiple) to count as a pass.

## Addendum Q - retention study results and STUDY CLOSED (2026-09-24)

**Implementation:** step10_retention_sim.py; summary
step10_retention_summary.json; trades step10_retention_trades.jsonl.
Population: 36,347 survivor trades (both months, t+60m survivors,
entry at first bar >= t+60m, no lookahead). Same frozen exit engine,
same cost tiers.

Full family at the optimistic tier (0.5% slip, 0.02 fail) and the
mildest realistic tier (1% slip, 0.05 fail):

| split | opt n | opt mean | opt p5 | mildest mean | mildest p5 |
|---|---|---|---|---|---|
| pool_ge_85 | 11,474 | +0.010 | +0.004 | -0.030 | -0.036 |
| pool_ge_200 | 9,415 | +0.027 | +0.020 | -0.013 | -0.020 |
| netflow_pos | 13,722 | -0.067 | -0.074 | -0.106 | -0.113 |
| netflow_pos_pool85 | 11,056 | +0.014 | +0.007 | -0.026 | -0.033 |
| price_up | 13,049 | -0.050 | -0.056 | -0.089 | -0.095 |
| trades_ge_40 | 33,609 | -0.382 | -0.387 | -0.418 | -0.423 |
| netflow_pos_price_up | 12,907 | -0.042 | -0.048 | -0.081 | -0.088 |
| pool200_netflow_pos | 9,171 | +0.029 | +0.022 | -0.011 | -0.018 |

**Gate verdict: FAIL for every split.** The best split
(pool200_netflow_pos) shows the familiar pattern: positive only at
the optimistic tier (+0.029, p5 +0.022) and negative at the mildest
realistic tier (-0.011, p5 -0.018), with BOTH regimes negative at the
mildest tier (pre -0.005/p5 -0.014, post -0.024/p5 -0.039). The
pre-registered gate (mean > 0 AND p5 > 0 at the mildest tier, both
regimes) fails with no family member close. Bonferroni correction is
moot: nothing survives even uncorrected.

The pool_ge_200 result is the clearest single summary of the whole
study: the same config flips sign between +0.027 and -0.013 on a
half-point of entry slippage. Every "positive" configuration in this
study - fast lane or slow lane - is a bet that you can enter at
sub-1% total cost. That bet is exactly what professional infrastructure
buys and retail cannot.

**STUDY CLOSED per the Addendum P closure rule.** Final verdict: no
retail edge found in pump.fun graduation-cycle trading at Dune-grade
data, on either the fast (sniping) or slow (retention) lane, across
two calendar regimes (August, September 2026), with pre-registered
filters, exits, cost grids, and gates. The honest retail takeaway:
the measurable edge in this market lives in entry-cost infrastructure
(sub-1% realized slippage at contested bars), not in information or
filters. Any future revisit needs either a materially different data
source (raw logs / Geyser) or a materially different market structure,
and should start from a NEW pre-registered spec, not this one.
