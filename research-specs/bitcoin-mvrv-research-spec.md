# Bitcoin MVRV Smart DCA — Research & Pre-Registration Spec

**Status:** DISCONFIRMED — probe executed 2026-08-10 (see §7)
**Source claim:** from `transcribe.txt` (the "Five Structural Edges" transcript): use the **market-value-to-realized-value (MVRV) Z-score** to dynamically size Bitcoin accumulation — "buy capitulation, trim euphoria" — versus a static DCA and buy-and-hold. Cites Grois (Grosjean Gangotena?) / Nasman 2026 on-chain cycle papers.
**Data (VERIFIED 2026-08-10):** **Coin Metrics Community API** (free, keyless) — `CapMVRVCur` (MVRV ratio) and `CapMrktCurUSD` (market cap) for BTC from **2010-07-18 → present**. Realized cap recovered faithfully as `CapRealUSD ≈ CapMrktCurUSD / CapMVRVCur` (recovers canonical values: 2017 top MVRV 4.25 / realized ~$76B; 2018 bottom MVRV 0.69; 2022 bottom 0.78). Full multi-cycle coverage (2013-14, 2017-18, 2020-22, 2023-26). No API key required.
**Ecosystem note:** different from the prior equity/intraday probes — on-chain daily/swing, not intraday; relative-allocation claim, not a clean alpha trade.

---

## 1. Claimed vs. honest prior

**Claim (verbatim, condensed):** "MVRV Z-score standardizes the deviation of market value from realized value, flagging absolute capitulation and extreme euphoria; the MVRV dynamic DCA outperforms static DCA and buy-and-hold [on max drawdown]."

**Honest prior:** this is a **relative-allocation / risk-timing** claim, not a novel-alpha claim:
- The expected (and realistic) win is **lower max drawdown / better entry sizing vs buy-and-hold**, not necessarily higher CAGR. MVRV timing trades total return for drawdown control in a volatile, cyclical asset.
- MVRV Z-score is a widely-known on-chain indicator (Checkmate/Glassnode lineage, popular since ~2019). The "edge," if any, is in **maintaining valuation discipline across cycles** (avoid buying at euphoric tops, accumulate at capitulation), not in an unknown signal.
- Bitcoin price / MVRV data is public and many have tested simple Z-score DCA; the marginal claim is dynamic sizing with an explicit buy-low / trim-high rule and a long backtest (2013+ multiple cycles).
- 2013+ gives only ~3-4 completed halving/cycle phases (2013-14, 2017-18, 2020-22, 2023-26) — small cycle count; OOS is genuinely few independent regimes. Verdicts must be tempered by this.

**Bottom line:** believable as a drawdown-reduction tool; unlikely to be a return-enhancing edge on its own. The test is primarily: does dynamic MVRV sizing beat buy-and-hold on max drawdown (and marginally on Sharpe) over 2013+ with friction, and does it survive on the later OOS cycle(s)?

---

## 2. Frozen rule set (pre-registered 2026-08-10)

**Universe:** BTC daily, 2010-07-18 → 2026-08-09 (Coin Metrics community API). Test window 2013 → present.

**Signal (MVRV Z-score):** `Z(t) = (MVRV(t) − SMA(MVRV, 365)(t)) / σ(MVRV, 365)(t)`, where MVRV = `CapMVRVCur` and the 365-day SMA/std are **trailing** (computed on data up to and including day t only). Look-ahead clean by construction: the regime at t uses only observations ≤ t.

**Regimes (frozen):**
- **ACCUMULATE (capitulation):** Z ≤ −1.0 → allocation multiplier **×3**
- **NEUTRAL:** −1.0 < Z < +2.0 → multiplier **×1**
- **TRIM (euphoria):** Z ≥ +2.0 → multiplier **×0.25**

**Allocation (identical total capital across strategies):**
- Schedule: allocate every **30 calendar days**; target total capital deployed over the window is equal for dynamic DCA, static DCA, and buy-and-hold.
- **Dynamic DCA:** per-period base allocation × regime multiplier. Unused cash in TRIM periods is held in zero-return cash and redeployed in ACCUMULATE/NEUTRAL periods (i.e. trim now, buy more at capitulation).
- **Static DCA:** same 30-day schedule, always ×1 (reference).
- **Buy-and-hold:** lump-sum the entire total at window start (worst-case timing reference per the transcript's "80%+ max drawdown" framing).

**Friction:** 10 bps/side execution cost on every buy and sell, plus 25 bps net spread/withdrawal per trade; cash held earns 0 (no lending).

**Metrics:** **max drawdown (primary)**, CAGR, Sharpe (0% rf), annualized vol, time-to-recover from max DD. Computed on total portfolio value (BTC holdings + cash).

**Data integrity:** `CapMVRVCur` and `CapMrktCurUSD` from Coin Metrics community API, keyless; realized cap recovered as `CapMrktCurUSD / CapMVRVCur` for sanity only (not used in the DCA). Verify continuity (no NaN gaps); document source. No relabeling or result-shopping after curves are seen.

---

## 3. Split & windows (frozen — data-bounded)

- **IS:** 2013-01-01 → 2020-12-31 (covers 2013/14 and 2017/18 cycles)
- **OOS:** 2021-01-01 → 2026-08-09 (2021 top, 2022 capitulation, 2023-26 accumulation/run)
- Caveat: cycle count is small; OOS is ~1.5 cycles. Report explicitly.

---

## 4. Pre-registered decision gates (mirror house discipline)

| Gate | Criterion | FAIL if |
|---|---|---|
| 1 | OOS max drawdown of dynamic DCA **strictly below** buy-and-hold (after friction) | dynamic DD ≥ B&H DD |
| 2 | OOS drawdown improvement survives parameter perturbation (±threshold bands) | improvement is a knife-edge |
| 3 | OOS CAGR not materially worse than buy-and-hold (within a tolerance, e.g. no more than X bps/yr worse) | CAGR degrade exceeds tolerance |
| 4 | No single cycle drives the result (drop best cycle → direction holds) | drop-best ⇒ sign flip |
| 5 | IS reproduction: IS max-DD improvement persists | no improvement IS |
| 6 | Look-ahead: Z-score computed from data up to and including entry day only; no future realized-cap; regime assigned on signal date | any violation |

Verdict: **DISCONFIRMED** if any gate fails; **CLEARS-OOS** only if dynamic DCA shows a robust, non-knife-edge max-DD improvement over B&H on OOS without material CAGR sacrifice.

---

## 5. Outputs

`../research/bitcoin-mvrv` — `bitcoin_mvrv_summary.json` (metrics + all gates), BTC/MVRV panel parquet (source-documented), regime/DCA series. Strategy register: `../strategies/five-structural-edges/FIVE_STRUCTURAL_EDGES.md` + `../strategies/bitcoin-mvrv/BITCOIN_MVRV.md`.

---

## 6. Status / Log

- **2026-08-09:** Spec + strategy doc created (REGISTERED, not tested). Free data routes confirmed (Blockchain.com MVRV/RV chart, Coin Metrics realized-cap, 2013+). Awaiting reviewer scope (thresholds, allocation multiplier, benchmarks, IS/OOS split) before any probe. No backtest has been run.
- **2026-08-10:** Data verified — Coin Metrics Community API keyless serves `CapMVRVCur` + `CapMrktCurUSD` 2010-07-18 → 2026-08-09 (full multi-cycle). Rules frozen (§2), IS/OOS frozen (§3). Probe about to run.
- **2026-08-10 (probe executed):** Dynamic MVRV DCA vs static DCA vs buy-and-hold on BTC 2013-2026. Verdict **DISCONFIRMED** (reviewer decision): DD gates pass only on sign after a comparison-direction correction, but the edge is not reproducible in-sample. See §7.

---

## 7. RESULTS — probe executed 2026-08-10

Implementation verified against `transcribe.txt`: MVRV **Z-score**, dynamic sizing "buy heavily at capitulation, reduce risk at euphoria," vs **static DCA** and **buy-and-hold**; primary metric **max drawdown** (claim notes standard buy-and-hold drawdown exceeds 80%). Coin Metrics data (verified faithful: `CapMVRVCur` = MVRV ratio; realized cap recovered as `CapMrktCurUSD/CapMVRVCur`, recovers canonical cycle values).

| Window | Strategy | Max drawdown | CAGR | Sharpe |
|---|---|---|---|---|
| **IS 2013-2020** | Dynamic MVRV DCA | −83.7% | 76% | 1.21 |
| IS 2013-2020 | Buy-and-hold | −84.5% | **161%** | 1.55 |
| **OOS 2021-2026** | Dynamic MVRV DCA | **−53.1%** | 14.7% | 0.56 |
| OOS 2021-2026 | Buy-and-hold | −76.6% | 15.1% | 0.53 |

**Gate ledger (sign):** G1 OOS DD shallower (PASS), G5 IS DD (PASS, but only −0.87pp), G3 OOS CAGR (PASS), G2 perturbation (PASS — DD stable across 7 parameter sets), G4 (PASS by robustness).

**Verdict: DISCONFIRMED.** Under the corrected sign comparison the DD gates pass, but the claimed drawdown-reduction edge is **not economically reproducible**: in-sample the dynamic DCA gives ~no drawdown benefit (−0.87pp) while ceding a large share of return (76% vs 161% CAGR); only the single OOS window shows the benefit (−53% vs −77% with equal CAGR). A "structural edge persistent over the last decade" must reproduce in-sample; it does not. The OOS benefit is substantially a cash-holding/beta-reduction effect rather than demonstrated timing alpha. Consistent with the house pattern (PEAD / ORB / VRP all DISCONFIRMED).

---

## 8. Follow-up 2026-08-11 — Bitcoin Cycle × MVRV-Z band confluence (CLOSED, not testable N=2)

**Question (asked during triage, not part of the original pre-registered spec):** does combining the "Bitcoin Cycle" indicator (1Y-MA ×2 vs 116D → CycleTop; 232D vs 2Y-MA → CycleBottom) with the MVRV-Z low/high bands give a valid buy-at-bottom / sell-at-top signal — i.e., does the confluence rescue / improve the MVRV signal?

**Script:** `../research/bitcoin-mvrv/cycle_confluence_probe.py` (faithful port of the two TradingView Pine indicators; rescale-Pine MVRV Z: `(MC−RCap)/σ(MC,730)` → rescale[−0.57,9.40]→[0,100]; lowB=EMA(lowest(Z,1500),900)+5; highB=EMA(highest(Z,1200),900)−20; cycle via crossunder only). Same data (Coin Metrics), same friction (10bp side + 25bp flat), same IS/OOS split.

**Key empirical findings:**

*Event counts (the decisive fact):* Cycle indicator fires only **4 CycleTops / 4 CycleBottoms over 2010-2026**. The strict **confluence** signal (cycle event AND band) fires **1 buy / 1 sell in IS and 1 buy / 0 sell in OOS — 2 trades in 16 years.** Not testable — anecdote, not an edge.

| Variant | IS CAGR | IS DD | OOS CAGR | OOS DD |
|---|---|---|---|---|
| buy-and-hold | 161.4% | −84.5% | 15.2% | −76.7% |
| confluence_longonly | 29.9% | −61.4% | 20.6% | −53.1% |
| either_longonly | 102.2% | −61.4% | 15.1% | −35.4% |
| mvrv_longonly (band only) | 23.7% | −61.4% | 20.0% | −35.4% |
| mvrv_longshort (band only) | 33.2% | −61.4% | 42.8% | **−129.4%** |

*Reading:*
- **MVRV band timing alone was already tested** (rows above): buying the low band / selling the high band cuts drawdown vs B&H (OOS −35% vs −77%) but gives up return badly in IS (24% vs 161%) and ~matches B&H OOS (20% vs 15%) — same profile as the original DISCONFIRMED MVRV DCA.
- **The cycle filter adds ~nothing over MVRV alone** (IS +6pp, OOS +0.6pp on long-only) — the two indicators select mostly overlapping days and the rare cycle crossunder contributes no independent, testable information.
- **Long-short is worse** — shorting BTC in this simple model is unreliable (DD −129%, unstable across IS/OOS).
- No variant beats buy-and-hold on return in-sample; the confluence's only OOS "win" is beta-avoidance/rent, not alpha, and it does not reproduce IS.

**Verdict: CLOSED (not testable — N=2 confluence events; relaxed variants neither beat B&H nor add value over MVRV alone).** Consistent with, and reinforcing, the original DISCONFIRMED MVRV result. Recorded here so the cycle-confluence idea is not re-surfaced as a candidate.
