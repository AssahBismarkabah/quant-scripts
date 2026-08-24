# Probe Spec — Four Discretionary Swing Setups (visual volume-profile returns)

**Date:** 2026-08-24
**Status:** FROZEN DESIGN (mechanics demonstrated; the numeric gate below is the honest boundary of what this lane can and cannot claim)
**Type:** Pre-registered research + tooling spec for the visual-discretionary "four setups" (S1-S4). Written before any forward testing; the mechanics were demonstrated this session against the owned daily panel, which is what forced the contraction-scale correction below (SS1c).
**Purpose:** Turn the four eye-based setups into a reproducible detector, then define what that detector can honestly prove — and what it cannot prove with the owned data.

## 0. What this is, and what it is not

This is the user's discretionary volume-profile swing system, expressed as explicit rules. It is deliberately *not* a claim of tradable alpha. The four setups are long-entry, 10-20 session swing trades on liquid single-stock equities, built entirely from public daily OHLCV. There is no information advantage, no speed advantage, no capital advantage. Its only defensible benchmark, therefore, is buy-and-hold of the same names — and against that benchmark, at this horizon, public-data re-entry timing has *no reason to beat the market on a schedule*. The honest claims of this lane are:

1. **The detector demonstrably captures the user's described setups** (return-to-node, level-drawing, contraction/trend/rejection/failed-break) as explicit, frozen rules on daily bars.
2. **It is a decision tool, not an alpha machine.** Its value is converting an inconsistent discretionary eye into a repeatable screener that collapses thousands of bars into a short, high-conviction watchlist.
3. **Its edge, if any, is real only to the extent that the discretionary layer adds discipline** — the satellite caps, the "act only when a node is defended" rule. That layer cannot be validated on the owned panel.

The mathematical honesty boundary (SS8) is: the owned panel (1998-2021, liquid large caps, survivorship tail, one long-biased cycle ending mid-cycle) cannot distinguish "return-to-node timing adds value" from beta drift + noise. A positive backtest here is uninterpretable; a negative one is also uninterpretable. The only thing the panel *can* do is demonstrate the mechanics and sanity-check the frequency/level-plausibility of signals.

## 1. The four setups (user's words → rule)

| Setup | User's description | Rule (frozen) | Where the veto lives |
|---|---|---|---|
| S1 contraction | "look for contraction levels, draw fixed range volume profile at the range, wait for price to come back to the POC of that range" | 6-session high-low range ≤ 2.5 × ATR30 (squeeze); POC fixed over the full 30-session range; require price to LEAVE that POC (≥ 0.5 × ATR30) then RETURN into the node band | "is this a genuine squeeze or a flag" — SS4 |
| S2 trend cluster | "draw the volume profile of the trend leg, highlight the highest-volume cluster, wait for price to come to that cluster; same for down-trend" | Trend = net leg move ≥ 1.0 × ATR30 over the 30-session window; node = POC of the fixed (window-start) profile; require sub-window close to LEAVE the node then RETURN | "is this a trend or a range" — SS4 |
| S3 rejection | "mark where there was a strong rejection (candle/shot), wait for price to come back there, trade in the direction of the reaction" | Upper-wick bar: wick ≥ 1.0 × ATR30 with reaction ≥ 0.8 × ATR30; node = POC of the reaction-bar profile; price returns into node | "is this a rejection or a normal wick" — SS4 |
| S4 failed break | "if price broke through and went the other way then came back, and doesn't respect the original level, reverse" | Rolling range (30-session); breakout bar opens beyond it then closes back inside ≥ 0.3 × ATR30; node = range POC, return into node | "was the level actually defended" — SS4 |

All four are long entries. The "same node" dedup (SS5) collapses consecutive days at one node into a single watch event.

## SS1c — Contraction scale: the evidence that froze S1's definition

This is why the four setups *felt* uncodable, and it is now resolved with data. The contraction definition depends on which lookback "the range" is:

| Lookback | Median HL range / ATR30 | p10 | frac < 2.5 ATR | frac < 3.0 ATR |
|---|---|---|---|---|
| 5 | 2.18 | 1.38 | 63.6% | 79.0% |
| 6 | 2.43 | 1.55 | 53.0% | 70.9% |
| 10 | 3.26 | 2.13 | 21.9% | 40.4% |
| 20 | 4.81 | 3.32 | 1.0% | 4.9% |

Reading: on liquid large caps, a "30-day range narrower than 1.5 ATR" essentially never happens; the tightness that the eye calls a contraction lives at 5-6 sessions. A contraction therefore cannot be "a narrow 20-30 day range." It is a **6-session squeeze** whose *node* is drawn from the **full 30-session profile** (the level price is defending across the whole structure), with the trade being the return. Both the degenerate 30-day-wide definition (0 signals) and the 6-day self-POC definition (≈700 signals/yr, trivial returns) are recorded as failed definitions; the frozen one (SS above) is the one that yields ~100-160 events/yr across 8 liquid names — the frequency regime a high-conviction discretionary system lives in.

## 2. Mechanics demonstrated this session (evidence of codability)

Against `research/pead/cache/stock_prices_latest.csv` (split-adjusted OHLCV), the detector enumerated, with **zero outcome-fitting**:

- **S2:** 6 events over 1998-2021 — e.g. AMZN 2017-10-23 return to a ~991 node after trading to 966; MSFT 2020-02-27 return to ~166 from 158; NFLX 2020-08-26 return to ~492 from 547. Sparse because price must genuinely leave then return.
- **S3:** 55 events — e.g. NFLX 2017-04-18 rejection, node 144.6; NVDA 2017-05-11 rejection into 121.5; GOOGL 2019-07-26 into 1268. Every row has a level, band, stop, context price.
- **S4:** 50 events — e.g. AAPL 2016-01-20 failed break, node 94.0; AMZN 2018-07-27, node ~1836; GOOGL 2019-05-15, node ~1185.
- **S1:** ~100-160/yr under the frozen definition (example: AAPL 2015-08-03 return to ~116.9 after trading to 113; AAPL 2015-09-08 to ~107.5).

Sanity checks: every row has nonnull node/atr; POC is split-stable (AAPL 2014 7:1 handled); the level is a strict function of the frozen params — no parameter was moved to make any outcome look good.

## 3. Data

- **Source:** owned daily panel `research/pead/cache/stock_prices_latest.csv` (split-adjusted OHLCV) — the same source lineage as prior probes, no new data dependency.
- **Universe (frozen, for demonstration and any future run):** the 8 liquid names carried in the panel: AAPL, AMZN, FB/META, GOOGL, MSFT, NFLX, NVDA, TSLA. (Expandable; this is the demonstration universe.)
- **No new data required.** No L2, no speed, no alternative feed — this is the part that makes the lane *not* gated on capability.

## 4. The two judgment points (kept human, declared)

**SS4 — The `ruled_by` field.** The detector emits `ruled_by="spec"` or `ruled_by="human"`. The spec point is where a definition is a threshold (squeeze width, trend gain, wick size). The **human** point is where the eye/reality differs from a threshold: "is this actually a trend, or a range with noise" and "is this a fresh level the market respects, or a stale one." The tool does NOT silently tune these; they are explicit, and a human override is a decision logged against the watch list — not a silent backtest parameter.

**SS5 — Node dedup.** Consecutive days where price is parked at the same node are one event (first day), not N. Frozen to avoid inflating event counts with the same level printed repeatedly. A human may re-trigger only after a genuine re-departure + re-return, which the detector would catch as a new event anyway.

## 5. What this lane CANNOT claim (frozen honesty gate)

**SS6 — No alpha claim.** This is public-data, retail-scale, long-bias swing timing. Its benchmark is buy-and-hold of the same names. There is no hypothesis here that "returning to a node" reliably beats holding — the literature and every prior probe in this repo (buyback put NOT ADVANCED, IVAMR DISCONFIRMED, NQ-VWAP DISCONFIRMED, PEAD DISCONFIRMED) say free-data retail constructs do not clear friction against drift.

**SS7 — The panel cannot validate it.** 1998-2021, one long-biased cycle ending mid-cycle, no delisted names (survivorship tail), 8 names. A forward test on this panel that returns "positive" cannot be distinguished from beta drift; one that returns "negative" is also uninterpretable. **Therefore: no "probe with a PASS/FAIL gate" is run on this candidate.** That would be falsely scientific. The only honest numbers are (a) signal frequency, (b) level-plausibility, (c) the distribution of forward returns *reported as descriptive statistics, not as a gate*, and (d) the comparison to buy-and-hold reported as context, not as a verdict.

**SS8 — What "edge" means here.** The edge of this lane, if it has one, is behavioral: the discipline of "act only when a node is defended, otherwise sit," enforced across a decade by a screener the user builds and owns. That is not measurable on the owned panel and is not claimed to be. It is the reason this lane is a *tool the user runs*, not a strategy the repo certifies.

## 6. Deliverables (this session, all committed)

1. **Detector** — `src/quant_scripts/node_profile/` (frozen `SpecParams`, `detect_nodes`, `value_area`), split-stable, deterministic, no outcome fitting.
2. **Spec** — this document.
3. **Committed output** — the demonstration signal set for the 8-name universe.

## 7. Status

**Mechanics: demonstrated and committed.** The four setups are coded. The remaining step, if the user wants it, is the **watchlist tool** (a daily screener that emits the short list with levels drawn) — not a backtest. That tool is the actual product, and it is what a builder can own and iterate. No forward-validation probe will be run on this candidate, because the honest gate (SS7) says the panel cannot answer the question it would be asked.
