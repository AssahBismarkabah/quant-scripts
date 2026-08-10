# Bitcoin MVRV Smart DCA — Research & Pre-Registration Spec

**Status:** REGISTERED — pre-registration drafted, NOT yet tested; awaiting reviewer scope + data (2026-08-09)
**Source claim:** from `transcribe.txt` (the "Five Structural Edges" transcript): use the **market-value-to-realized-value (MVRV) Z-score** to dynamically size Bitcoin accumulation — "buy capitulation, trim euphoria" — versus a static DCA and buy-and-hold. Cites Grois (Grosjean Gangotena?) / Nasman 2026 on-chain cycle papers.
**Data:** free on-chain sources confirmed via Tavily (2026-08-09): Blockchain.com chart (MVRV/realized-value series), Coin Metrics historical realized-cap. History 2013+ feasible.
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

## 2. Pre-registered rule set (draft — to be frozen on reviewer go)

**Universe:** BTC daily price + MVRV Z-score, 2013-01-01 → present (data-bounded).

**Signal (MVRV Z-score):** `Z = (market_cap − realized_cap) / σ(market_cap − realized_cap)` over a trailing window (standard 2-year / ~730-day for the "Z-score" variant). Thresholds define regimes:
- **Accumulate (capitulation):** Z below a low threshold (e.g. ≤ −1.0 / ~bottom band) → deploy accumulated cash / overweight.
- **Neutral (hold):** between bands → maintain baseline DCA.
- **Trim (euphoria):** Z above a high threshold (e.g. ≥ +2.0 / top band) → reduce size / take cash.

**Dynamic DCA rules (candidate, to be fixed):** baseline periodic allocation (e.g. weekly $); low-Z regime multiplies the allocation (e.g. × 2-3), high-Z regime reduces it (e.g. × 0.25 or stops new buys). Cash rerouted to the low-Z regime.

**Benchmarks:** (a) **Static DCA** — fixed periodic purchase regardless of Z (same total capital contributed); (b) **Buy-and-hold** — lump-sum or first-period full allocation held.

**Metrics:** CAGR, max drawdown, calendar/vol, Sharpe. **Primary comparison: max drawdown (and time-to-recover) of dynamic DCA vs buy-and-hold signature; secondary: CAGR.** Friction: conservative on-chain/CEX buy-sell spread + withdrawal, e.g. 10-25 bps per trade, plus capital-cost on cash drag (opportunity cost from reduced euphoria-period exposure).

**Sample screen / data integrity:** realized_cap from Coin Metrics (or Blockchain.com RV) must match range and scale; drop any discontiguous months; document source + any gaps. No relabeling or result-shopping after seeing curves.

---

## 3. Split & windows (draft — data-bounded)

- **IS:** 2013-01-01 → 2020-12-31 (covers 2013/14 and 2017/18 cycles)
- **OOS:** 2021-01-01 → present (2021 top, 2022 capitulation, 2023-26 accumulation/run)
- Caveat: cycle count is small; OOS is ~1-2 cycles. Report explicitly.

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

`research/bitcoin-mvrv/` — `bitcoin_mvrv_summary.json` (metrics + all gates), BTC/MVRV panel parquet (source-documented), regime/DCA series. Strategy register: `strategies/five-structural-edges/FIVE_STRUCTURAL_EDGES.md` + `strategies/bitcoin-mvrv/BITCOIN_MVRV.md`.

---

## 6. Status / Log

- **2026-08-09:** Spec + strategy doc created (REGISTERED, not tested). Free data routes confirmed (Blockchain.com MVRV/RV chart, Coin Metrics realized-cap, 2013+). Awaiting reviewer scope (thresholds, allocation multiplier, benchmarks, IS/OOS split) before any probe. No backtest has been run.
