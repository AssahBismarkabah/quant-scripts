# Research Pipeline Review (post 5-candidate cycle)

**Date:** 2026-08-04
**Type:** Decision / portfolio-review document
**Purpose:** Classify why each tested candidate failed, separate *fixable* from *structural* failure, and decide whether/where the next free-data effort is worth it — rather than generating candidate #6 blindly.

## 1. The five adjudications by failure class

| Candidate | Verdict | Failure mechanism | Class |
|---|---|---|---|
| Vol Targeting Flow Fade | v1/v2 rejected; v3 **measured-but-marginal** | Effect real (bootstrap p5 > 0 at n~840) but ~1-2 bps over market drift; not tradable | **Structural (measured dead)** |
| Index Rebalancing | Rejected L1-2 | Surviving edge (S&P 600 short-additions @10td) is a single March 2025 batch; 2024 flat, 2026 negative; no OOS year split (data starts 2023-03-28) | **Data-window artifact + decayed** |
| SPX Dealer Gamma (GEX) | Rejected L1; L2 declined | Fails conservative friction; L2 needs intraday OI/flow (paid source) | **Friction + paid-data gated** |
| IVAMR | Not pursued | No pre-2023 intraday data for its own IS/OOS protocol; behavioral edge, finite half-life | **Paid-data gated** |
| Funding Basis Carry (BTC) | Rejected | Fails under conservative model | **Structural** |

This is the complete tested set (matches the roadmap's section-1 table).

## 2. What the failures actually tell us

Three distinct reasons a candidate died, with very different implications:

1. **Measured-dead (effect too small / absent).** Vol-fade, Funding Basis. No amount of data changes the answer; the effect itself, tested properly, is ~1 bp or fails conservative costs. These are *final*.

2. **Data-window artifact (insufficient history).** Index Rebalancing. Its 2023-onwards data gave only two reconstitution years and no OOS split; the one surviving cell is a single batch. This is the *same disease vol-fade had* — and we proved the cure works (free long history turned vol-fade's "unproven" into a definitive measured answer at ~zero cost).

3. **Paid-data / knowledge wall.** GEX-L2 and IVAMR both dead-end on intraday data (dealer OI/flow, or pre-2023 intraday history) that is not freely obtainable.

## 3. The key fork: is the next step free-data, paid-data, or stop?

- **The free-data phase is close to exhausted.** Of the two free-fixable near-misses (vol-fade, index-rebal), one is now measured-dead and the other (index-rebal) has **already-weakened priors**: the documented literature (Bennett, Stulz, Wang 2022) shows the S&P 500 additions reversal *decayed*, the Level-2 data shows the surviving cell is a *single* batch with 2024 flat and 2026 negative, and the Russell 2000 leg is a permanent inclusion effect (not temporary). Extending free history for index-rebal would be cheap (the same Yahoo/Stooq path) but plausibly returns "reconfirmation of decay" rather than a surprise.

- **The genuinely-untested space leans paid.** GEX-L2 (dealer-gamma intraday) and IVAMR (intraday value-area) both need intraday data that costs money. They remain blocked not by lack of ideas but by the roadmap's standing "no paid intraday purchase" rule.

## 4. Recommendation

**Do not generate candidate #6 yet, and treat the free-data near-misses with honest priors.**

The single most informative, lowest-cost free move left is a **short re-test of index rebalancing on extended free history** (index/reconstitution lists back several years), with the explicit prior that the most likely outcome is "the single-batch edge does not recur" — in which case the index-rebal line is closed for good, and we then have a definitive answer that free, structural, flow-driven ideas have been tested and are either measured-dead or decayed.

**Update (2026-08-04): this re-test has been superseded, not run.** Grounding showed (a) the historical reconstitution data the re-test needs is NOT freely retained pre-2022 (S&P DJI press archive ~2022+; Wikipedia/tickerleague are current snapshots only; FTSE Russell PDFs only 2023-25), so it is not the cheap one-download vol-fade had; and (b) the decisive persistence evidence is already in the existing output `level2_year_breakdown.parquet`. That file shows the S&P 600 short-additions reversal is NOT persistent: 2024 +139 bps (t=0.76), 2025 +1542 bps (t=3.93, the one batch), 2026 -786 bps (t=-3.54). **Index-rebalancing is therefore CLOSED on existing evidence** (see `../strategies/index-rebalancing/INDEX_REBALANCING.md` section 8). The free-daily-data line for this candidate is done; there is no untested "something there" left to hope for.

With index-rebal closed, the free-data near-misses are exhausted. That leaves only the buy-vs-stop decision below.

If the free-data re-tests all come back dead/decayed, the honest portfolio conclusion is:

> After five candidates, every *free and genuinely-testable* structural/flow idea we can construct from public daily data has been measured and found to lack a tradeable edge. The remaining untested hypotheses (dealer-gamma intraday, intraday value-area) require paid intraday data. The fork is therefore: **buy the intraday data to test the paid-data-gated candidates, or deliberately stop the research phase.**

This reframes the decision you face next from "which candidate do I test" to "**is it worth paying to unblock the intraday candidates, or is the free-daily-data phase done?**"

## 5. What I am not recommending

- Not a blind 6th candidate on free daily data (the free well is largely dry).
- Not re-opening closed vol-fade cells under any name.
- Not a paid intraday purchase until the free near-miss (index-rebal) has been given its cheap final test and the buy-vs-stop question is explicitly decided.

## 6. Status

- **2026-08-04:** Review written. No data acquired, no spec written, nothing run. Next concrete optional step: cheap free re-test of index-rebal on extended history (needs your go-ahead), or the explicit buy-vs-stop decision for intraday.
- **2026-08-04 (later):** **Index-rebalancing CLOSED on existing evidence.** The recommended free re-test was superseded: historical reconstitution data is not freely retained pre-2022, and the existing `level2_year_breakdown.parquet` already proves non-persistence (2024 +139 / 2025 +1542 / 2026 -786 bps). No further free re-test is warranted; the candidate is done, not "hoping to test something that isn't there". Recorded in `../strategies/index-rebalancing/INDEX_REBALANCING.md` section 8. All free-data structural/flow candidates are now adjudicated (measured-dead or decayed). The remaining real decision is the buy-vs-stop fork on paid intraday data (GEX-L2 / IVAMR) or deliberately stopping the research phase.
