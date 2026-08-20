# Probe #22 Spec — Phase 0 (FROZEN): Prediction-Markets Data Census & Friction

**Date:** 2026-08-17
**Status:** TERMINAL — probe returned to stop 2026-08-20. All pre-registered candidates (A/B/C) measured and DEAD on measurement (see §6).
**Type:** Pre-registered research spec — Phase 0 of Probe #22 (plan: `IA/turning-point/02-PROBE-22-PLAN.md`; thesis: `IA/turning-point/01-capacity-constrained-arenas.md`). Phase 0 is the only phase written today. Phases 1–3 exist only as frozen gates and placeholders below; they are not fleshed out until the Phase 0 gate is read. **Nothing else happens until the Phase 0 gate is read.**
**Purpose:** Characterize the data and the friction of prediction markets (Kalshi primary, Polymarket secondary) before any alpha work. Phase 0 is deliberately alpha-free: no signal testing, no divergence analysis, no candidate evaluation. Any interesting observation made during the census is logged to a parking list and NOT analyzed until Phase 1 completes.

## 0. Decisions recorded (made 2026-08-17, per plan §Corrections)

- **D1 — Execution vehicle / own cash:** Phases 0–2 proceed regardless of capital, because data is free and the harness transfers (plan's rationale). Own cash (≥$5k–$25k for a Kalshi/Polymarket account) gates **only Phase 3 (execution pilot)**. If a candidate certifies and no own cash has been committed, the honest verdict is **CERTIFIED-BUT-NOT-EXECUTABLE**, recorded as such — a stop, not a maybe.
- **D2 — Income honesty check:** per the plan's own expected-value ranking, income work remains the priority; this probe is the disciplined secondary (nights-and-weekends) effort with a hard budget: **8–13 weeks to a terminal verdict** (Phase 0–1: 2–3w; Phase 2: 3–4w; Phase 3 pilot if certified: 4–6w). If the budget is exceeded, that is an execution problem, not a market signal.
- **D3 — Phase 0 write-and-freeze:** executed by this document.

## 1. Method (frozen) — four deliverables, in order

### 1.1 Data census (no alpha analysis allowed)

1. **Kalshi:** pull official historical data (API + published CSVs; exact endpoints verified in this phase). Build the market metadata table with schema:
   `ticker, category, resolution_criteria (raw text), open_time, close_time, settlement_time, volume, open_interest, settlement_price, status`.
   Append trade history and book snapshot availability per market (which markets have books, what depth/timestamp granularity).
2. **Polymarket:** pull history via CLOB API + Gamma API + Polygon subgraphs (verify which is complete for trade history). Same metadata schema, plus `event_id` and resolution source/criteria raw text.
3. **Pinnacle closing lines (Candidate A's oracle):** census candidate sources (the-odds-api free tier; publicly available scraped Pinnacle archives) and verify coverage: which sports, which date range, which markets. **Pre-registered fallback rule: if no free/owned Pinnacle history is obtainable, Candidate A is DEAD on data access — recorded as such, not salvaged by substituting a non-sharp price.**
4. **Era markers:** every market gets an era flag (pre-2023 / 2024 / 2025–2026) because the pro-ization is recent and structural.

### 1.2 Overlap census (Kalshi × Polymarket)

Join on event identity. Brutal classification, three buckets only:
- **PROVABLY IDENTICAL** — resolution criteria identical in substance and source (same settlement source, same deadline, same edge-case handling).
- **PROBABLY IDENTICAL** — same event, wording differs in ways unlikely to diverge (flagged; used only for calibration, never for Candidate C).
- **NOT COMPARABLE** — resolution criteria differ in any material way.

Output: bucket counts by category. This count alone decides whether cross-platform convergence (Candidate C) is a candidate or a corpse.

### 1.3 Friction model (the wall every candidate must climb)

1. **Fee formula, verified:** Kalshi mechanical formula (claimed: fee ≈ 0.07 × P × (1−P) per contract, rounded up to the cent; maker fees/rebates differ by market class — verify current schedule). Polymarket fee schedule (claimed: zero on most markets historically; some categories changed 2025 — verify).
2. **Realized spreads and book depth** by category × liquidity tier, measured from book snapshots.
3. **Cost table, frozen as the Phase 0 friction model:** "to trade market category X at size Y, total round-trip friction is Z cents." Explicitly include the minimum lot size and the fee-on-settlement leg if any.

### 1.4 Adverse-selection measurement (LP probe autopsy, ported)

On thin-book markets: when passive resting orders fill, what does price do in the next 5/30/60 minutes? Same test as the perps LP probe that printed −9.42 bps/trade. Output: fill-context price change distribution by liquidity tier.
**Pre-registered consequence: if fills concentrate on adverse jumps, any passive-liquidity candidate (Candidate D) is pre-dead and does not consume a probe slot.**

## 2. Data sources (verified 2026-08-18; updates replace the candidates table)

| Platform | Source | Verified status | What it provides |
|---|---|---|---|
| Kalshi | Official API `https://external-api.kalshi.com/trade-api/v2` | Works; historical tier split at `/historical/cutoff` (2026-06-19). Pagination is slow at scale: ~1000 rows/page, rate collapses to ~20s/page after sustained pulls. Full archive too large for page-crawl (Kalshi settles ~1M markets/day; tens of millions total). | markets metadata (incl. `rules_primary` resolution text, volume, bids/asks), trades, books (live tier), candlesticks |
| Kalshi | kingsets.com mirror (`https://beta.kingsets.com/manifest.json`) | Works. Full markets catalog 2.8M rows (partial history, ingested since 2026-03; all markets with ≥1 trade in covered range guaranteed). Daily trades CSVs, 31 days free. Schemas: markets = ticker/event/title/subtitle/result/start/end/closed/ingestion; trades = dt, series, event, market, asset side, taker side, size, price, trade_id. One day ≈ 7.7M trades ≈ 285-400MB gz. | full catalog (results, dates — no volume/rules text), 31 days of trade-level data |
| Kalshi | predictiondata.dev | Paid; Kalshi key requires contacting vendor. Full orderbook (top-of-book and complete) per ticker per day. | book snapshots + updates (friction's depth dimension) |
| Polymarket | Gamma API `/markets` | DEPRECATED (sunset 2026-05-01; warning header). Offset capped at 2000. | — (use keyset) |
| Polymarket | Gamma API `/markets/keyset` (verified) | Works. `after_cursor` pagination, `limit` max 100, filters incl. `closed`, `volume_num_min/max`, `liquidity_num_min/max`, `uma_resolution_status`. Rich market objects: question/description (resolution text), category, fee schedule fields (`feesEnabled`, `takerBaseFee`, `orderMinSize`, `orderPriceMinTickSize`), `umaResolutionStatuses`. Full closed history from 2020. Archive ≈ 1.1M+ markets and counting (market factory era). | full metadata census |
| Polymarket | CLOB API + Polygon subgraphs | Not yet pulled in Phase 0 (pending keyset census completion). | trades, books |
| Pinnacle (oracle) | the-odds-api free tier; public scraped archives | NOT YET VERIFIED — Phase 0 deliverable. Candidate A dies on data access if unobtainable (pre-registered fallback rule stands). | closing lines with overround |

**Verified scale facts (feed the gate):** Kalshi settles ≈ 1M markets/day (2.6M settled in the last 2.5 days in the API live tier alone); 15.7% of settled markets have volume > 0; 429 families already clear ≥30 liquid resolved markets in a 2.5-day window (count condition trivially satisfiable — gate turns on friction, not counts). Kalshi's most liquid families: 15-minute crypto binaries (KXBTC15M ≈ 242k trades/day, KXETH15M, KXGOLD15M, KXXRP15M, KXSOL15M, KXDOGE15M), daily crypto direction (KXBTCD), MLB multigame combos (KXMLBGAME). Trade sizes median ≈ 15.6 contracts, mean ≈ 120 (long tail). Polymarket total market count ≈ 1.1M+ (exceeds common wisdom by 10x).

**Friction & fee verification (2026-08-19, completed):**
- **Fee schedule (official PDF, archived 2026-02-18, effective 2026-02-05):** taker fee = round up(0.07 × C × P × (1−P)) for all markets; maker fee = round up(0.0175 × C × P × (1−P)) where applicable (none currently listed for crypto; verify at Phase 3 before any live order); S&P500/Nasdaq-100 use 0.035 multiplier. Crypto 15m has NO special multiplier. Table: 1 contract at P=0.50 → 2c; P=0.20–0.30 → 2c; P=0.10 → 1c; P=0.99 → 1c. Per-contract RT at the money: taker ≈ 4c, maker ≈ 2c.
- **Adverse-selection read (32 days of trade data, 07-18 → 08-18, 113M fills, taker-side trade price → VWAP of trades in next 5/30/60 min, maker-perspective sign):** KXBTC15M ≈ −1.4c (maker-favored, 55M fills), KXBTCD ≈ 0, KXETH15M ≈ +0.0–0.5c, KXSOL15M ≈ +0.6–1.3c, KXXRP15M ≈ +1.5–2.8c (adverse), KXDOGE15M ≈ +2.1–3.7c (adverse). p95 tails 40–56c (binary-market mechanics).
- **Live book snapshot (BTC 15m window 05:30–05:45 EDT 2026-08-19):** 1-cent spread (0.67/0.68), top-level depth 1,150/2,940 contracts (~$0.8k/$2.0k per side); each market trades only during its own 15-min window (opens at window start, closes at expiry).
- **Oracle (Pinnacle) access verified:** the-odds-api free tier (historical endpoint; NHL 2020+, tennis, MLB, golf per coverage table — quota-limited); football-data.co.uk free CSVs (20+ years soccer incl. Pinnacle closing H/D/A columns, verified EPL 24-25). Crypto binaries additionally have a mechanical oracle: CF Benchmarks RTI 60s average (the settlement index itself) — free and exact.
- **Polymarket census (1.82M markets; 554k question-families):** structure is esports-dominated — top families by liquid market count: Spread (62k), Exact Score (50k), Counter-Strike (21.5k), Games Total (16.9k), Set 1 Winner (15.5k), Set Handicap, Game 1–3, Map Handicap, Dota 2, Valorant, LoL. 302k crypto price markets; 222.5k (73.5%) carry `takerBaseFee` (fee-enabled era), rest zero-fee legacy. Fee verified via official docs: 15m crypto markets charge a taker fee with the same dome as Kalshi — peak ≈ 1.25–1.75¢/contract at P=0.5 (schedule-version dependent; exact curve to be confirmed at Phase 3 against the `/fee-rate/{token_id}` endpoint), and PAY maker rebates funded by taker fees (mirror image of Kalshi). Tick size 0.1¢, order min size 5 shares. Note: Polymarket crypto settlement index (Chainlink reference/TWAP) ≠ Kalshi's CF Benchmarks RTI → cross-platform crypto comparisons are at most PROBABLY IDENTICAL (Candidate C caveat).

**Overlap census (2026-08-19, completed):**
- **Crypto 15m Up-or-Down windows (Candidate C core):** Kalshi (110,157 events across BTC/ETH/SOL/XRP/BNB/DOGE) vs Polymarket (448,159 range-format up/down markets, exact `[start,end] ET` window parse). Exact same-window match (same asset, same start, same end): **14,437 windows / 72,016 market pairs** (BTC 14,436, ETH 14,415, SOL 13,786, XRP 11,477, BNB/DOGE 8,951 each). Both platforms use the same convention (Up/Down vs price at window open) → contracts are semantically identical, settlement indices differ (CF Benchmarks RTI vs Chainlink) → classified **PROBABLY IDENTICAL** (not provably — Candidate C operates on this family with the settlement-mismatch caveat already on file). Kalshi-only windows 38,141 (mostly Jul 24 → Aug 19 not yet crawled on the Polymarket side; re-run overlap after crawl completes).
- **Sports/esports overlap (MLB, NBA, CS2, tennis):** same EVENTS trade on both platforms (Kalshi KXMLBGAME combos, KXNBA, KXCS2MAP, ATP Challenger ~25k events; Polymarket MLB/NBA/CS2 families), but contract structures differ (Kalshi multigame combos vs Polymarket single-game moneylines; Kalshi map-winner vs Polymarket match/map mixes; Kalshi ATP Challenger vs Polymarket Grand Slam/tour-level tennis) → **event-level overlap only, NO identical contracts outside crypto**. Candidate C is confined to crypto Up-or-Down; sports divergence (Candidate A) reads Pinnacle vs Polymarket/Kalshi prices directly.
- **Pinnacle census (2026-08-19, completed):** free Pinnacle closing-line history at scale — football-data.co.uk verified 7,814 matches across 4 seasons × 5 leagues (EPL, Championship, La Liga, Serie A, Bundesliga), all with Pinnacle closing H/D/A (`PSCH/PSCD/PSCA`) + totals (`P>2.5/P<2.5`); EPL files exist back to 1993/94 (30+ seasons). the-odds-api free tier covers NHL 2020+, tennis, MLB, golf (historical endpoint, quota-limited ≈ 500 req/mo). Pre-registered fallback rule NOT triggered — Candidate A's data access is satisfied (soccer at depth; MLB/NBA quota-limited but sufficient for a ≥30 events/yr divergence census).
- **Polymarket CLOB friction / adverse-selection (2026-08-19, completed):** 65,604 trades across 19 liquid crypto Up-or-Down markets (vol $5.5k–$638k; trade history via public data-api, no API key needed — clob.polymarket.com/trades requires an API key, data-api does not). Side-split drift after fills (positive = passive side run over): **passive BUY favored — +0.8¢ @1m, +4.0¢ @5m; passive SELL adversely selected — +5.3¢ @1m, +6.8¢ @5m**. The ≈5¢ buy/sell asymmetry is larger than the taker fee dome (1.25–1.75¢ at P=0.5): on Polymarket crypto binaries the passive-sell side carries real adverse selection, passive-buy is favored — same qualitative asymmetry as Kalshi's families (KXBTC15M −1.4¢ maker-favored overall; DOGE/RRP +2–4¢ adverse), consistent with the known maker/taker split on both venues.

## 3. Phase 0 gate (frozen)

**PASS** requires at least one market family with:
1. **≥30 liquid, resolved markets per quarter** (event-count discipline — the failure mode of 10b5-1 and MVRV confluence);
2. **honest round-trip friction < 2–3 cents** on that family;
3. **book data deep enough to model fills** (fills, not just marks).

**FAIL** = verdict **"dead on friction"** — the class is closed and the fork returns to stop. No salvage, no loosening of the gate.

## 4. Frozen gates for Phases 1–3 (placeholders, not to be expanded before Phase 0 gate reads)

- **Phase 1 — Calibration baseline:** for every resolved market: final price vs outcome, binned 0–5%, …, 95–100%, per platform per era, **net of the fee formula**. Output: calibration curve. Any later "edge" inconsistent with the curve is a backtest artifact by construction.
- **Phase 2 — One spec, candidates in priority order** (each: net-of-friction, OOS sign agreement, N ≥ 30):
  - **A. Sharp-line divergence** (Pinnacle closing line, overround removed multiplicatively: p\*_i = p_i / Σp_j; signal when platform price deviates > 2× modeled friction; divergence-distribution census first — <30 events/year ≥ 2× friction ⇒ unverifiable-dead pre-trade).
  - **B. Net calibration skew** (systematic buy of the mispriced bin, net of fees, liquidity-restricted).
  - **C. Cross-platform convergence** (only if 1.2 found meaningful PROVABLY IDENTICAL counts; hold to resolution; settlement-mismatch is the real killer).
  - **D. Passive market-making on thin books** — NOT-PROBED unless 1.4 is favorable.
  - **Excluded by construction:** UMA/oracle dispute "edge," wording-ambiguity sniping, any discretionary resolution judgment.
  - **IS/OOS split by calendar time** (OOS strictly later than IS — these markets structural-break).
- **Phase 3 — Execution pilot (only on CERTIFIED):** smallest live size, 30+ trades, single job = realized slippage vs modeled friction; pre-registered tolerance; hard-coded daily loss cap + total-pilot loss cap (harness logic); capacity ramp with hard stop at measured capacity (own fills moving book > 1 cent).
- **Verdicts:** CERTIFIED / DEAD / UNVERIFIABLE — **UNVERIFIABLE is terminal, never a reason to loosen N.**
- **Capacity pre-registration:** minimum viable capacity written down at certification; certified capacity below the number that matters = "real but insufficient" = stop.

## 5. Pre-mortem (frozen — the five ways this dies)

1. **Arb-compression death:** divergence distribution < 30 events/yr exceeding 2× friction (most likely for C).
2. **Fee-formula death:** skew exists gross, dies net of 0.07×P×(1−P) (plausible for B on Kalshi; Polymarket zero-fee is where B survives if anywhere).
3. **Sparsity death:** overlap or divergence census counts too low ⇒ UNVERIFIABLE, recorded honestly (as MVRV confluence was).
4. **Adverse-selection death:** fills on thin books concentrate on news jumps (the −9 bps mechanism; kills passive candidates).
5. **Capacity death:** edge certifies but book caps at $20–50k deployed = $5–15k/yr — "real but insufficient" = stop, not maybe.

## 6. Status

- **2026-08-20 — PROBE TERMINAL VERDICT: DEAD ON MEASUREMENT (all pre-registered candidates measured).** Full log in plan §Status. Per the plan's pre-registered stop rule (all candidates fail ⇒ class closed, no re-litigation), the probe returns to stop. Candidate verdicts:
  - **B (net calibration skew): DEAD on both platforms.** Kalshi: Phase 1 baseline clean (finals perfectly calibrated, tails exact, sure-thing frenzy +1.5¢ net top bin is capacity-limited). Polymarket (353 BTC 15m windows, Jun–Aug 2026; real entry-horizon refs at T−300/T−180/T−60 from data-api trades): curve mirrors Kalshi — mid-bin (10–90¢) 56.1¢ priced vs 56.3% realized at T−300, tails extreme-bimodal and exact; no longshot bias anywhere, zero-fee structure notwithstanding.
  - **C (cross-platform divergence): DEAD.** 1,198 identical Kalshi↔PM crypto windows: settle agreement 94.2%; all 70 disagreements are micro-move windows (median BTC move 0.025%, max 0.11%) — oracle boundary-sampling noise (RTI vs Chainlink stream), no ex-ante signal; direction agreement 87.9%; final-price divergence median ≈0¢ with a >10¢ tail that is gamma `lastTradePrice` staleness on illiquid PM markets (vol<10k, closing quotes agree with Kalshi). One genuine ~0.1% fragmentation case (Mar 5) is not exploitable.
  - **A (sharp-line divergence): DEAD on the representative family.** PM soccer moneylines vs Pinnacle closing lines (191 fixtures, 5 leagues, Aug 2025–Jan 2026): >1¢ 36%, >2¢ 7.3%, >4¢: 1 event (4.9¢), >6¢: 0, >10¢: 0. Pre-registered gate (≥30 events/yr > 2× friction) fails by an order of magnitude. Same MM engine prices all PM sports (MLB/NBA/CS2 prior identical; Pinnacle quota-limited — not measured, recorded as unmeasured-at-stop, not as a live candidate).
  - **Data-integrity addenda (on file):** data-api `/trades` ignores `before`/`after`/`conditionId` (offset pagination is the only correct method); PM sports markets trade post-kickoff until oracle resolution (ref prices must filter `ts < kickoff`); PM updown outcome labels are Up/Down not Yes/No.
  - **Unmeasured at stop (recorded, not live candidates):** A on MLB/NBA/CS2/tennis; Kalshi-side sports divergence (API finals only from Jun 13+, no sharp-line source at scale); the theoretical live oracle-boundary observation variant (sub-1¢/window EV, execution risk, capacity $1–10k — not an income surface by the plan's own EV ranking).
  - Artifacts: `candidate_a_*`, `pm_calib_*` (scripts + outputs), corrected `divergence_crossplatform.py` + re-run CSVs, `pm_calibration_btc15m.csv`. Polymarket crawl rebuild (atomic checkpoints) died at market id ~2.76M (~40% of full history); the dense 2025–26 slice the probe used is complete — not restarted (no step requires it).
- **2026-08-17:** Spec frozen (decisions D1–D3 recorded §0). Next action: **Kalshi historical data pull — the first script.** Nothing else until the Phase 0 gate is read. No alpha work permitted during this phase; observations go to the parking list.
- **2026-08-19 — Phase 0 gate READ (Kalshi).** All four census deliverables completed for Kalshi (+Polymarket census partial): data census (API + kingsets mirror + 32 days of trades, 113M focus-series fills), friction model (fee schedule verified from official archived PDF; adverse-selection read; live book snapshot), oracle access (Pinnacle free tier + football-data + mechanical crypto oracle), Polymarket census (1.82M markets, fees, families).
  **Gate verdict on Kalshi BTC 15m family: PASS**, with documented caveats:
  1. Count — PASS: ≈ 8,700 markets/quarter (94.7/day × 92).
  2. RT friction — PASS for the passive/maker execution style (adverse drift −1.4¢ favorable, maker fee 0–1¢ where applicable): ≈ 1–2¢ RT. Taker-at-the-money fails (≈4¢ RT; ~2¢ RT OTM) — taker style restricted to OTM prices. Recorded, not fatal for the gate (candidates A/B are passive).
  3. Book depth — PARTIAL: live top-level 1,150–2,940 contracts on BTC 15m (1¢ spread); fills modelable from 32 days of trade data; historical book snapshots not freely available (predictiondata.dev is paid).
  Caveats recorded for Phase 3: maker-fee applicability list re-verify before any live order; Polymarket crypto settlement index (Chainlink) ≠ Kalshi index (CF Benchmarks RTI) → cross-platform crypto comparisons are at most PROBABLY IDENTICAL.
  Polymarket side: count PASS trivially (esports families 10k–62k liquid); fee = taker dome ~1.25–1.75¢ at P=0.5 on 15m crypto + maker rebates; CLOB friction read (65,604 trades/19 markets): passive-buy favored +4.0¢/5m, passive-sell adverse +6.8¢/5m — asymmetry exceeds the taker dome.
  **Phase 0 deliverable set: COMPLETE** (data census, overlap census, Pinnacle census, friction model incl. Polymarket CLOB). Caveats on file: overlap census computed on the 1.87M-market Polymarket snapshot (through Jul 24) — re-run after the full crawl rebuild; Polymarket crawl was restarted from scratch with atomic checkpoint writes (checkpoint corruption incident 2026-08-19, cause: non-atomic rewrite raced reads; fixed, no data loss beyond 5k rows of the 1.87M snapshot; families/friction outputs unaffected).
  Next: Phase 1 calibration baseline (final price vs outcome, net of fee formula) on the Kalshi BTC 15m family — pre-registered in §4, no gate loosening.
- **2026-08-19 — Phase 1 calibration baseline DONE (Kalshi BTC 15m).** Final prices taken from the live API (`last_price_dollars` on the market object; `/markets/{ticker}` returns it for finalized markets; `result` authoritative), not from the kingsets trades files.
  **DATA-INTEGRITY FINDING (affects all trades-file analyses):** kingsets trades files are NOT complete records of each market. Real data ends at a market-specific cut point (observed T−2 s to T−10 min before expiry), then a synthetic terminal block is appended: a few all-BUY rows at the eventual settlement price (0.999 for winners / ~0.002 for losers), then a long all-BUY run of price 0.001 with backfilled timestamps (up to 279 rows, ~2–4 min). Evidence: (a) for result=yes markets the file's tail shows Up collapsing to 0.001 while the API final is 0.9990 (e.g., KXBTC15M-26AUG181800-00, KXBTC15M-26AUG181245-45 — verified live 2026-08-19); (b) sum(price×size) over the file = ~50% of the API's `volume_fp` (missing volume = the real last-second frenzy); (c) terminal rows are all-BUY regardless of outcome. The tapered deci-cent tick (0.001 steps in [0,0.1] and [0.9,1]) is real — 0.001/0.999 are valid prices; the marks are fake, not the ticks. Also: catalog (kingsets `kalshi-markets.csv.gz`) lags trades by ~1 day (96 Aug-18 KXBTC15M markets absent); catalog and API results agree where both present.
  **Final-price calibration (n=6,396 markets, 2026-06-13 → 08-19; API finals, net of taker fee 0.07×P×(1−P)):**
  | bucket | n | p(up) | gross err | buy net EV |
  |---|---|---|---|---|
  | 0–5¢ | 3,211 | 0.12% | −2.38¢ | −3.37¢ |
  | 5–10¢ | 1 | 0% | −7.50¢ | −8.50¢ |
  | 65–70¢ | 1 | 100% | +32.50¢ | +30.50¢ |
  | 70–75¢ | 1 | 100% | +27.50¢ | +25.50¢ |
  | 95–100¢ | 3,182 | 100.00% | +2.50¢ | +1.50¢ |
  Finals are extreme-bimodal by construction (6,393/6,396 at ≤5¢ or ≥95¢; the market converges in the last ~15 s); both populated bins are essentially perfectly calibrated. No systematic final-price skew: the top bin's +1.5¢ net is the last-second sure-thing frenzy (capacity-limited, bots compete at 0.1¢ ticks), the bottom bin is −3.4¢ net. Entry-horizon calibration (price at T−60/180/300 s vs outcome) is NOT usable from the trades files: synthetic tail rows contaminate the last minutes for a market-specific fraction of markets. Follow-up flagged: re-run the Kalshi friction model (Phase 0 §1.3) excluding synthetic tails (2.0% of KXBTC15M rows are ≤1¢, mixing real loser fills and marks).
  **Phase 1 baseline verdict: calibrated, no exploitable final-price skew; entry-horizon calibration requires real-time capture (live tier) or a filtered trades re-run — parked.**
  Next: reconcile this with §4 pre-registered Phase 2 candidates (B: net calibration skew — now restricted to intra-window prices; C: cross-platform divergence on overlap windows — unaffected by the kingsets finding since overlap uses both platforms' finals).
