# Retail Edge Landscape — Post-Test Synthesis

**Date:** 2026-08-16
**Origin:** synthesis by the backtest agent following the short-term sector momentum test (see `strategies/short-term-sector/SHORT_TERM_SECTOR.md`); recorded here verbatim in substance, with probe annotations.
**Trigger:** our own sector-rotation test — a real, documented historical pattern, reproduced faithfully, still underperformed buy-and-hold once executed and benchmarked honestly.

## The short version

Edges still exist, but almost none of them survive as "retail-accessible, liquid, long-only rotation." The reason isn't that institutions have secret magic data — it's that the edges that survive tend to live where retail and liquid ETFs structurally can't reach.

## Is it "they have better data"?

Partly, but it's the wrong framing. The data advantage is real but specific:

- **Faster data:** order-level, tick-level, exchange proprietary feeds, and — big one — their own orders. They see the order flow as it forms; retail can't.
- **Broader/contingent data:** satellite, shipping, alternative datasets, and their own execution footprint.
- **But:** for the public signals we can compute (momentum, value, carry, seasonality, macro), we have the same underlying series. The bottleneck is rarely the dataset name — it's speed, latency, capacity, and cost of carry.

**The honest lesson from our own test is more damning than "missing data":** we found a real, documented historical pattern (sector momentum), reproduced it faithfully, and it still underperformed buy-and-hold once executed and benchmarked honestly. No missing data would have fixed that. The edge wasn't absent because of a data gap — it was absent because the edge was never a survivable alpha to begin with on that universe/benchmark.

## Where edge actually comes from

Edges that genuinely survive fall into a few categories — notice which ones retail can't play:

1. **Speed / microstructure edges.** Latency arb, market making, stale-signal arb. They decay in milliseconds and need co-location. Retail can't have them, full stop.
2. **Capacity-constrained edges not worth institutional overhead.** Some small or illiquid corners (small caps, certain derivatives) produce alpha but can't scale to billion-dollar AUM, so big funds skip them — a sliver is open to smaller players. **This is the one genuine, if small, gap available to retail.**
3. **Bearing cost/risk retail can't.** Shorting with high borrow costs, illiquid options with wide spreads, levered carry with funding — institutions can warehouse these and eat the cost; the "alpha" is compensation for risk/carry a small account shouldn't take.
4. **Data/processing at scale.** Hundreds of datasets combined, faster — but again, mostly informs 1-3.

## The uncomfortable truth our test proved

Most quant "edge" today is a race to be slightly ahead of the market microstructure and costs, not a discoverable public dataset pattern. Anything computable from public OHLCV on liquid ETFs has been arbitraged to death — which is precisely why our clean 2015-2022 sector pattern died when we did it properly. Big funds don't win because they know XLK was strong last month; they win because they can react to what moves prices before the monthly print is actionable, in corners we structurally pay more to trade.

## What this means for us

- If we want edge as a retail quant, the realistic domains are the **capacity-constrained / overlooked corners** (category 2 above) and strategies that **exploit smaller size** (turn faster, trade things funds ignore), not liquid-ETF rotation.
- The other honest lever is **regime/defensive positioning that cuts risk, not alpha** — accept tracking buy-and-hold but taking less drawdown. That's not "finding an edge," it's risk management, and it's the only thing our sector momentum genuinely delivered.

## Probe annotations (where our data agrees / adds color)

- **Agrees:** sector momentum delivered only risk reduction. Measured: full-window Oct 2015 → Aug 2026 MaxDD −32.3% vs SPY −34.1% (net of costs, point-in-time); 2022 calendar year +2.1% vs SPY −18.6% (+20.7pp dodge). The drawdown benefit is real but modest — smaller than the "beat SPY by 18pp" framing implied (that figure was 2022 alone; the multi-year net is negative).
- **Agrees:** public-OHLCV-on-liquid-ETFs being arbitraged is consistent with the strategy trailing SPY by ~4.2pp CAGR and QQQ by ~10pp CAGR over the full window.
- **Caveat to keep on file:** "less drawdown" was claimed as the genuine deliverable; our measurement shows the DD reduction (~2pp vs SPY over a decade, concentrated in 2022) is regime-dependent and small. Treat defensive/regime-timing as a *falsifiable hypothesis to probe*, not a confirmed benefit — same discipline as any alpha claim.

## Open fork (from the synthesis)

1. Explore the capacity-constrained / small-player corner (less-liquid small caps, or strategies exploiting faster turnover).
2. Dig into defensive/regime-timing as a drawdown-reducer rather than an alpha-chaser.

Neither is yet a registered research spec; both need one (and a pre-registered probe) before any capital decision.