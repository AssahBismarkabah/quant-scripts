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
