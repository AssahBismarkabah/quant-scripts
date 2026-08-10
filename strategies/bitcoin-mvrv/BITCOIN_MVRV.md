# Bitcoin MVRV Smart DCA

**Version:** 1.0 (probe run, 2026-08-10)
**Status:** DISCONFIRMED — pre-registered probe executed on Coin Metrics `CapMVRVCur` (MVRV ratio) + price, BTC 2013-2026. DD gates pass only on sign after a comparison-direction fix, but the claimed drawdown-reduction edge is not economically reproducible in-sample (IS dynamic −83.7% vs buyhold −84.5% with dynamic CAGR 76% vs 161%).
**Classification:** On-chain valuation/timing — dynamic accumulation vs static DCA and buy-and-hold (relative-allocation claim, not a novel alpha trade)
**Research spec:** `IA/bitcoin-mvrv-research-spec.md`
**Source:** `transcribe.txt` ("Five Structural Edges" transcript) — "MVRV Z-score standardizes the deviation of market value from realized value, flagging absolute capitulation and extreme euphoria; buy heavily at capitulation, reduce risk at euphoria; dynamic MVRV DCA [vs] static DCA and buy-and-hold." Cites Grois/Grosjean/Nasman 2026 on-chain cycle research.

## 1. Executive Summary

MVRV Z-score measures how far Bitcoin's market value deviates from the aggregate cost basis (realized value), normalized by historical variance. Low values = capitulation (below aggregate cost), high values = euphoria. The transcript claims a dynamic MVRV DCA — buying heavily at capitulation and trimming at euphoria — beats buy-and-hold on max drawdown (noting a plain buy-and-hold exposure "exceeding 80%" max drawdown).

**Verdict: DISCONFIRMED.** The dynamic DCA's drawdown reduction is **not reproducible in-sample**: in IS 2013-2020 it delivered essentially no drawdown benefit (−0.87pp) while roughly halving CAGR (76% vs 161%); the meaningful benefit appears only in the single OOS window (2021-26, −53% vs −77% with equal CAGR). That one-window outcome is the signature of regime-luck, not a structural edge. Consistent with the house pattern (PEAD / ORB / VRP).

## 2. Implementation (verified against transcribe.txt)

- **Signal:** MVRV Z-score = (MVRV − SMA365(MVRV)) / σ365(MVRV), trailing (look-ahead clean).
- **Regimes:** Z ≤ −1.0 ACCUMULATE (×3); −1.0 < Z < +2.0 NEUTRAL (×1); Z ≥ +2.0 TRIM (×0.25).
- **Schedule:** 30-calendar-day allocations; budget identical across strategies; unspent cash carried and redeployed at capitulation.
- **Benchmarks:** static DCA (×1) and buy-and-hold (lump T at window start).
- **Friction:** 10 bps/side + 25 bps spread/withdrawal per trade; cash earns 0.
- **Split:** IS 2013-2020, OOS 2021-2026.

## 3. Claimed vs tested

| Metric | Dynamic MVRV DCA | Buy-and-hold | Claim |
|---|---|---|---|
| Max drawdown IS 2013-20 | −83.7% | −84.5% | lower DD (≈ −0.87pp, negligible) |
| CAGR IS 2013-20 | 76% | **161%** | (~half the return) |
| Max drawdown OOS 2021-26 | **−53.1%** | −76.6% | lower DD → holds OOS |
| CAGR OOS 2021-26 | 14.7% | 15.1% | roughly equal |

## 4. Pre-registered gates

| Gate | Result |
|---|---|
| 1 OOS DD shallower than buy-and-hold | PASS on sign (−53% vs −77%) |
| 5 IS reproduction of DD improvement | PASS on sign only (−0.87pp) — economically negligible |
| 3 OOS CAGR not materially worse | PASS (14.7% vs 15.1%) |
| 2 Perturbation robustness | PASS (DD stable across 7 parameter sets; within-window) |
| 4 Drop-cycle | PASS by robustness |
| **Overall (economic significance)** | **DISCONFIRMED** — not reproducible in-sample |

## 5. Interpretation

The sign-level gates pass after a comparison-direction correction, but that is misleading. The honest reading:

- **IS (2013-20):** the dynamic DCA gives **~no drawdown protection** (−83.7% vs −84.5%) and **halves the return**. Trimming at the 2017 top and re-buying at the 2018 capitulation re-exposed the portfolio to the full ~84% drawdown, while the cash-discipline discipline suppressed the huge 2017 runup. Net: worse risk-adjusted outcome for the user's actual capital.
- **OOS (2021-26):** the mechanism appears to work (−53% vs −77% DD, equal CAGR). But this is a single out-of-sample window, and much of the "improvement" reflects holding cash (lower beta), not demonstrated timing alpha.

A "structural edge persistent over the last decade" must reproduce in-sample. It does not. The one-window OOS benefit is consistent with regime-luck, not a reproducible mechanism. **DISCONFIRMED** (reviewer decision 2026-08-10).

## 6. Status / Log

- **2026-08-09:** Research spec + strategy doc created (REGISTERED, not tested). Data routes under review.
- **2026-08-10:** Coin Metrics Community API verified keyless for `CapMVRVCur` + `CapMrktCurUSD` (2010-07-18 → 2026-08-09); realized cap recovered faithfully. Rules + IS/OOS frozen. Probe built, run, verified against `transcribe.txt`. Comparison-direction bug in the DD gate caught and fixed. Final verdict **DISCONFIRMED** (see spec §7). Candidate closed.

## 7. Conclusion & Next Steps

The MVRV dynamic-DCA drawdown-reduction claim, as framed in the transcript, does not yield a reproducible edge: it is not meaningful in-sample and only "works" in a single out-of-sample window, at the cost of halving return in the earlier window. With this, **all five of the transcript's structural edges are now resolved** (PEAD, ORB, VRP, Congressional, Bitcoin MVRV — all closed). No further work warranted on this family.
