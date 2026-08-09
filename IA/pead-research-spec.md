# PEAD (Post-Earnings-Announcement Drift) — Research & Pre-Registration Spec

**Status:** PRE-REGISTERED — probe about to run (2026-08-09)
**Source claim:** from `transcribe.txt` (the "Five Structural Edges" transcript): positive (negative) earnings surprises drift for up to ~60 days after the announcement; cites Ball-Brown 1968, Bernard-Thomas 1989, recent ML PEAD work; claims "4% spread over 60 days in a single stock."
**Data:** Kaggle "US Historical Stock Prices With Earnings Data" (`tsaustin/...`, 486MB zip, downloaded 2026-08-09 into `research/pead/cache/`).

---

## 1. Data (owned, downloaded 2026-08-09)

- **Earnings** `earnings_latest.csv`: `symbol, date, qtr, eps_est, eps, release_time`. 168,603 rows / 5,569 symbols / **2009-04 → 2021-06**.
- **Prices** `stock_prices_latest.csv`: `symbol, date, open, high, low, close, close_adjusted, volume, split_coefficient`. 7,786 symbols / **1998-01 → 2021-06**.
- **Usable earnings pairs (both eps_est and eps):** 110,994 → concentrated **2012-2021** (~9-15K/yr), 5,075 symbols.

**Critical coverage fact:** data ends **mid-2021** ("updated 5 years ago"). The OOS window therefore cannot extend past 2021 — the pre-registered split is constrained to 2012-2021.

**Point-in-time qualification (agreed approach):** `eps_est` is the analyst-estimate field paired to each announcement. We use the **announcement-date surprise** and enter the drift trade **after** the announcement, so the estimate must be the pre-announcement consensus, not a restated post-announcement figure. We cannot fully audit this against IBES (proprietary); per the agreed method we **qualify the measure as "analyst-expectation-based surprise from public estimates, not IBES SUE"** and treat residual point-in-time risk as a gate-6 caveat.

---

## 2. Frozen rule set (pre-registered 2026-08-09)

**Universe:** all stocks with both `eps_est` and `eps` present, with a computable SUE and price data available for the hold period.

**Sample screen (pre-registration amendment, 2026-08-09):** exclude events whose entry price (`close_adjusted` just before announcement) < **$5.00** (penny-stock exclusion; required for data validity and tradability — the initial run showed sub-$1 names with adjusted-price split artifacts returning up to +19,800%). Winsorize the 60-day return at **±300%** as a residual-artifact guard. Documented transparently; not result-shopping.

**Surprise / SUE:**
- Unexpected earnings `UE = eps − eps_est` per announcement.
- `SUE = UE / σ_stock(UE)` where `σ_stock` is the rolling standard deviation of the stock's own prior `UE`s (min 4 prior announcements). If <4, use the cross-sectional `σ(UE)` within the same calendar quarter (min 50 stocks, else drop).

**Portfolio formation (per announcement period, cross-sectional):**
- Each quarter, rank all eligible announcements by SUE. Form **top-decile (long, highest SUE)** and **bottom-decile (short, lowest SUE)**.
- **Entry:** at the close of the **first trading day after** the announcement date (announcement day not traded — avoids same-day return / look-ahead). Equal-weighted.
- **Exit:** at the close of the **60th trading day** after entry, or the stock's last available price before delisting/window end.

**Holding / measurement:** 60-trading-day buy-and-hold per event; long-short decile spread is the primary series. Both legs hold 60 days; overlapping quarterly cohorts.

**Friction:** per-trade round-trip cost applied to both legs. Base = **20 bps per side (40 bps round trip)** to approximate a liquid-tick, low-commission stock execution; stress = **50 bps per side (100 bps round trip)**.

---

## 3. Split & windows (frozen — data-bounded)

- **IS:** 2013-01-01 → 2017-12-31 (announcements in window)
- **OOS:** 2018-01-01 → 2021-06-14 (announcements in window; last full hold ends ~2021-09)
- **Warm-up:** 2012 (used only to establish per-stock SUE history, not traded).

---

## 4. Pre-registered decision gates (mirror VWAP/IVAMR/ORG discipline)

| Gate | Criterion | FAIL if |
|---|---|---|
| 1 | OOS long-short **net** (after friction) > 0 | ≤ 0 |
| 2 | OOS per-event bootstrap p5 > 0 | p5 ≤ 0 |
| 3 | OOS consistency: long-short PF ≥ 1.0 AND ≥ 60% positive cohort-periods | PF < 1.0 |
| 4 | Tail/fragility: no single cohort-period drives the edge (drop-best) | drop-best ⇒ sign flip |
| 5 | IS reproduction: IS long-short **gross** > 0 | ≤ 0 |
| 6 | Look-ahead: entry at close of day AFTER announcement; SUE from pre-announcement estimate; no future prices. Structural by construction. | any violation |

Verdict: **DISCONFIRMED** if any gate fails; **CLEARS-OOS** only if all pass with the long-short spread surviving friction on OOS.

---

## 5. Mechanism / honest prior

Mechanism (claimed): slow information diffusion, limited attention, alpha-execution fractionalized accumulation → prices underreact for weeks; drift up to 60 days. Honest prior from independent evidence (FinLab 2016-26 large caps): PEAD is **now weak** (+2.75% ann. L/S, rank IC ~0.012; the avoid-the-miss side is stronger than ride-the-beat). Our test on ~5K symbols with a true SUE, both deciles, and friction will decide whether the structural drift survives on this broader 2012-2021 panel.

---

## 6. Outputs

`research/pead/outputs/` — `pead_summary.json` (metrics + all gates), `pead_events.parquet` (per-event rows with SUE, decile, leg, ret, net_ret). Strategy register: `strategies/five-structural-edges/FIVE_STRUCTURAL_EDGES.md` + `strategies/pead/PEAD.md`.

---

## 7. RESULTS — probe executed 2026-08-09

Implementation verified verbatim against `transcribe.txt` (high-**standardized**-UE → long, low/negative → short, 60-day hold, "4% spread"). Clean-sample run after the $5 penny-screen + ±300% return winsorize amendment.

| Window | n long / short | long ret | short ret | spread gross | spread net | spread mkt-adj | PF |
|---|---|---|---|---|---|---|---|
| **IS 2013-2017** | 5,790 / 5,771 | +3.69% | +1.62% | **+2.07%** | +1.27% | +1.98% | 1.11 |
| **OOS 2018-2021** | 4,159 / 4,146 | +3.89% | +4.16% | **−0.26%** | −1.06% | +0.03% | 0.94 |

**Gates:** Gate 5 IS gross>0 PASS (+2.07%); Gate 1 OOS net>0 FAIL (−1.06%); Gate 2 OOS bootstrap p5 FAIL (−98 bps); Gate 3 OOS PF≥1 FAIL (0.94); Gate 4 drop-best-cohort FAIL; Gate 6 look-ahead PASS (structural).

**Verdict: DISCONFIRMED.** The transcript's claimed 60-day drift reproduces in-sample (+2.07% IS, PF 1.11 — consistent with the academic PEAD prior and essentially the claimed ~2-4% spread) but **does not persist out-of-sample** (OOS spread ≈ 0 to slightly negative; market-adjusted +0.03%, PF 0.94, bootstrap p5 negative). This is the signature of a **decaying/alpha-decayed anomaly** over 2013-2021 — consistent with the independent FinLab finding that PEAD is now weak in large caps. No deployable OOS edge under the frozen rules. Gate-6 look-ahead clean (entry day-after announcement, SUE from pre-announcement estimate, no future prices).

- **2026-08-09:** Spec pre-registered; Kaggle data acquired + validated; probe built and run. Initial run contaminated by penny-stock adjusted-price artifacts (up to +19,800%); amended sample screen ($5 entry, ±300% winsorize) documented. Final clean-sample verdict recorded above. Candidate closed.

