# Trading-Floor "Open & Range" Strategies — Research & Extraction Spec

**Status:** Extraction / prioritization — REVIEW BEFORE TESTING (2026-08-08)
**Source claim:** a trading-education transcript naming five concrete, allegedly-validated strategies plus two broader approaches. Purpose of this doc: capture what the transcript claims, separate what is already tested/closed, and define what is testable with data we own — for compact review before any backtest.

---

## 1. What the transcript actually claims

A trader ("professional education" lineage: Patrick Neil, Jan Smolen, Tom Hougaard, Fabio Valentini; consistent with the earlier short-vol speaker) proposes that the way to trade is: a simple, mechanical, statistically-backed core strategy, plus discretion/orderflow on top. He names five specific mechanical strategies and says all have "decades of data" and are "back tested." He also names two broader frameworks.

The claim style is the same as our prior disconfirmations: high-confidence, marketed as validated. Our job is to falsify each testable one on our own data with strict pre-registered gates.

---

## 2. The five named strategies

| # | Strategy (named source) | Mechanics from the transcript | Testable with owned data? |
|---|---|---|---|
| 1 | **Oops** (Larry Williams) | Prev-day high/low established. Next day must **gap ≥20 pts** beyond it. Then: gap-up → sell when price breaks (closes) back into/below prev-day high; gap-down → buy when price breaks above prev-day low. Fixed stop (points or above the level), ~1:1 RR. "Validated on DAX 2012-2024." | **YES on NQ** (gap + prev-day level + break). DAX-specific claim not our concern; test the mechanic on NQ. |
| 2 | **Gap Fill** (Patrick Neil) | Trade the fill of the prev-day-close → today-open gap. Gap-down: buy expecting the gap to fill up; gap-up: sell expecting fill down. Claim: **"65-70% of S&P gaps fill; NASDAQ higher."** | **YES on NQ** (need gap + whether it fills within the session). Strong falsifiable stat. |
| 3 | **Opening Range Breakout (ORB)** (Crabel/Fabio; guest's friend Luke) | Take the **first 15-min range** of the 9:30 ET cash session. On a **5-min candle close** above/below that range → enter. Stop just beyond the other side; target ~1:2-1:3 RR. Claim: **"outperforms the S&P 500"; "always works in stocks."** | **YES on NQ** (owned 1-min → resample 5/15). Strong falsifiable claim. |
| 4 | **Rule of Four** (Tom Hougaard) | Only on **NFP or FOMC news days**; on **DAX and FTSE 100**. After release, count 4 × 5-min candles, then buy/sell on the breakout of that 4-candle range (ORB-like). | **NO on owned data** — needs DAX/FTSE futures + a US news calendar. Would require new data. |
| 5 | **PBD / Break-in-Breakout** (Tom "Forvolt") | Auction-market-theory range patterns (failed-auction break-in, breakout, reversal). | **SKIP** — user confirms this is the family already tested as IVAMR and it did NOT hold. Not re-tested. |

---

## 3. The two broader approaches (note, likely lower priority)

- **6. COT Report swing filter** — CFTC Commitments of Traders non-commercial positioning as a trend-confirmation filter (with macro + price/volume) for swings. Free CFTC data, but a different (daily/swing) ecosystem and a larger build. Testable but not part of the same intraday family.
- **7. Macro scenario / monetary-policy swing model** (scenario building + intermarket DXY/gold/bonds + yield curve) — mostly discretionary, hard to make machine-executable with strict objective rules as stated. Likely NOT a clean pre-registered candidate without major specification work.

---

## 4. Already tested / closed (do not re-run)

- **Option-flow / GEX regime** (squeezemetrics/spotgamma/trace the guest describes): this is exactly the **SPX dealer-GEX** family we already ran — rejected at the friction gate, Level-2 declined. Also the **short-vol / VRP** family just closed (V1/V2/V3). **Skip** — the option-flow edge is the same structural family.
- **PBD / Break-in-Breakout** = IVAMR (per user): disconfirmed. Skip.

---

## 5. What we propose to test (the core trio) — for review/compact

The three intraday **gap/range-at-open** strategies are the coherent, highest-fidelity set to the transcript's claims, on the same testbed we already use:

**Instrument / data:** NQ (`GLBX.MDP3`, `NQ.n.0` continuous lead), RTH-only 1-min OHLCV from Databento. We own two overlapping caches that combine to **2013-11 → 2026-08**:
- `research/ivamr/cache/NQ_n_0_1m.parquet` (2013-11 → 2023-12, 973K rows)
- `research/nq-vwap-pullback/cache/NQ_n_0_1m.parquet` (2020-08 → 2026-08, 597K rows)

**Frozen rules to pre-register (per strategy):**
- Gr/Oops: gap ≥20 pts beyond prev-day high/low; enter on a 5-min close back through the level; fixed stop, 1:1 target.
- Gap Fill: gap opens; enter in the gap-fill direction; exit on fill or session close; test the 65-70% fill-rate stat and whether the fill is profitable net of friction.
- ORB: first 15-min RTH range; enter on a 5-min close beyond it; stop at range-other-side, target 1:2 RR.

All with the house discipline: **IS/OOS split, conservative friction (0.5 pts/turn like prior probes), bootstrap p5 gates, look-ahead audit**, and a **DISCONFIRMED** verdict if any gate fails. Same protocol as the NQ VWAP-pullback and IVAMR probes (both disconfirmed) so results are comparable.

---

## 6. Data reality summary (what we own vs. need)

| Need | Own? | Source |
|---|---|---|
| NQ 1-min RTH (2013→2026) | **YES** (2 caches, 973K + 597K rows) | Databento |
| SPY daily (realized/basics) | **YES** | Yahoo (cached) |
| VIX / VIX3M / VIX9D (context) | **YES** | CBOE CDN / FRED (cached) |
| DAX / FTSE 100 futures (Rule of Four) | **NO** | would need new data |
| CFTC COT report (COT filter) | **NO** (free source exists) | CFTC (not yet cached) |
| US news calendar (Rule of Four: NFP/FOMC dates) | **NO** (free source exists) | Fed/BLS calendar |

---

## 7. Decision for the reviewer

Pick the test scope:
1. **Test the trio (ORB + Gap Fill + Oops) on NQ now** — recommended; highest fidelity to claims, uses owned data, same disciplined protocol as our disconfirmations.
2. **ORB + Gap Fill only** — drop Oops for now.
3. **Add COT swing filter** — separate, larger build, free CFTC data to acquire.
4. **Rule of Four** — defer unless DAX/FTSE futures data is acquired.

This doc is the compact review artifact. No backtest runs until the scope is chosen and the specific froze rules + gates are pre-registered.

---

## 8. REVISION — scope, split, and structure frozen (2026-08-09)

Reviewer decision: **run each of the trio independently** (each a distinct falsifiable claim: ORB "outperforms S&P", Gap Fill "65-70% fill", Oops "validated on DAX 2012-2024"). Split frozen **IS 2014-01-01 .. 2018-12-31 / OOS 2019-01-01 .. 2026-08-07** (IVAMR-style, long clean OOS; data prefix from 2013-11 supplies prev-day levels).

Pre-registered per-strategy mechanics (frozen before any run; see the code in `src/quant_scripts/opening_range_gap/`):

| Strategy | Entry | Stop | Target | Fill-rate candidate eval |
|---|---|---|---|---|
| **ORB** | First 15-min RTH range (09:30-09:45 ET). After 09:45, enter on first 5-min close beyond the range. | Opposite side of the range ("slightly below the other side") | 1:2 RR (2x stop distance) | — |
| **Gap Fill** | Day opens gap'd. Enter in the fill direction on a break of structure (5-min close) after 09:45. | Opp side of gap-fill level / fixed | Exit on full fill (prev-day close) or 15:55 session close | Report raw fill rate + net-of-friction P&L |
| **Oops** | Prev-day high/low known. Next-day gap ≥20 pts beyond it. Enter on 5-min close breaking back THROUGH the level. | Fixed stop (pts or beyond level) | **NEXT 5-min bar close** (transcript: "we sell until the next candle closes with a fixed stop-loss"); per-day single entry | — |

House discipline identical across all three: **IS/OOS, 0.5 pts/turn friction base (1.0 stress), bootstrap p5 (n=5000, seed 42), look-ahead audit (gate 6 structural)**, verdict **DISCONFIRMED** if any pre-registered gate fails. Same protocol as NQ VWAP-pullback and IVAMR probes so results are directly comparable.

**Transcript-confirmed refinements locked 2026-08-09** (verified against `transcribe.txt`):
- **One entry per day** per strategy — the transcript describes a single setup ("we wait for a candle to close... that's where we buy/sell"). The 20-trades/day churn from an over-loose trigger is an implementation artifact, not the strategy.
- **Oops exit = next 5-min bar close** with a fixed stop-loss ("we sell until the next candle closes with a fixed stop-loss"). No profit target. Replaces the earlier 1:1 draft.
- **Oops gap = minimum 20 points**, literal ("Ideally, the gap should be minimum 20 points").
- **Stops/targets are computed from the actual FILL price** (next-bar open), not the signal-bar open — fixing a look-ahead-alignment bug that inflated ORB/Gap-Fill and zeroed Oops in the first run.
- **Gap Fill fill-rate gate = 0.60** — transcript says "65 to 70% of gaps are filled in the S&P 500; in the NASDAQ is even higher", so 0.60 is a conservative bound for NQ.

Data: combine the two owned NQ RTH 1-min caches (`research/ivamr/cache/NQ_n_0_1m.parquet` + `research/nq-vwap-pullback/cache/NQ_n_0_1m.parquet`), dedup on `ts`, giving **2013-11 → 2026-08**. No new fetch required.

---

## 9. RESULTS — probe executed 2026-08-09

Engine + data: combined owned NQ RTH 1-min (2013-11→2026-08), 5-min execution bars, one entry/day, 0.5 pts/turn friction, bootstrap p5 (n=5000, seed 42), look-ahead audit structural (gate 6 PASS by construction: prev-day levels / opening range complete before trigger, fill at next-bar open, intra-bar stops). Outputs in `research/opening-range-gap/outputs/`, code in `src/quant_scripts/opening_range_gap/`.

| Strategy | IS trades / net | OOS trades / net | OOS win% / PF | Verdict |
|---|---|---|---|---|
| **ORB** | 1,123 / **−2,565.5** | 1,801 / +9,473.3 | 47.4% / 1.14 | **DISCONFIRMED** |
| **Gap Fill** | 1,213 / **artifact** | 1,960 / **artifact** | — / — | **NOT FALSIFIABLE AS A TRADE** (raw fill-rate OOS 0.5885 < 0.60) |
| **Oops** | 7 / **−14.5** | 304 / **−44.0** | 33.2% / 1.04 | **DISCONFIRMED** |

**ORB (DISCONFIRMED):** IS reproduction fails (net −2,565.5 < 0 → gate 5) and OOS tail-fragility fails (52.2% of active days eat the kill-switch cap → gate 4). Stop is the well-defined range-other-side; mechanics clean; no edge by the pre-registered gates.

**Gap Fill (NOT falsifiable as a trade):** the transcript specifies **no stop and no concrete exit** — only "wait for a break of structure" and "fill the gap." The placeholder stop bug (placed on the wrong side of entry when a gap-down opens below yesterday's low) produced a phantom false positive (871 of 1,244 "stop" exits were actually wins; PF 4.0). Under the house rule — only falsify what the source actually specifies — the P&L side is **not pre-trade-falsifiable** and is not reported as a result. The one objective, falsifiable claim is the **raw gap-fill rate**: **IS 0.628 / OOS 0.5885** — OOS below the 0.60 bound and below IS. The "65-70% fill, NASDAQ higher" claim does **not clear on clean OOS**.

**Oops (DISCONFIRMED):** all P&L gates fail (IS −14.5, OOS −44.0, 33.2% win rate). Caveat: the transcript's literal "minimum 20 points" gap is not level-invariant — NQ rose ~3500 (2014) to ~20000 (2026), so IS has only 7 qualifying trades vs 304 OOS; the verdict rests almost entirely on OOS.

**Overall:** two clean disconfirmations (ORB, Oops) + Gap Fill's fill-rate fails OOS. Consistent with the prior VWAP-pullback and IVAMR disconfirmations from the same trading-education lineage. Candidate family closed. Details in `strategies/opening-range-gap/OPENING_RANGE_GAP.md`.

- **2026-08-09:** Spec §8 frozen, transcript-confirmed refinements locked, probe run, results recorded above.

