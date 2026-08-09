# PEAD (Post-Earnings-Announcement Drift)

**Version:** 1.0 (probe run, 2026-08-09)
**Status:** DISCONFIRMED — pre-registered probe executed on the Kaggle US equities panel; the 60-day drift reproduces in-sample (IS 2013-2017 +2.07%, PF 1.11) but does not persist out-of-sample (OOS 2018-2021 spread ≈ 0 to slightly negative, PF 0.94, bootstrap p5 < 0).
**Classification:** Equity cross-sectional behavioral anomaly (earnings surprise drift, SUE-based)
**Research spec:** `IA/pead-research-spec.md`
**Source:** `transcribe.txt` ("Five Structural Edges" transcript) — "stock with high standardized unanticipated earning continue to drift upward for up to 60 days while negative surprise stocks drift downwards... The spread is 4% for 60 days in a single stock." Cites Ball-Brown 1968, Bernard-Thomas 1989.

## 1. Executive Summary

PEAD is the oldest documented equity anomaly: after an earnings surprise, prices underreact and drift in the surprise direction for weeks. The transcript claims a tradeable ~4% / 60-day spread going long high-SUE (standardized unexpected earnings) and short negative-SUE names.

We tested exactly that: long top-SUE decile / short bottom-SUE decile, 60-trading-day hold, on a 2012-2021 panel of ~5,000 US stocks (Kaggle earnings estimate+actual + prices), with IS 2013-2017 / OOS 2018-2021, friction and strict pre-registered gates.

**Verdict: DISCONFIRMED.** The drift reproduces in-sample (IS spread +2.07%, PF 1.11 — consistent with the claim) but **fades out-of-sample** (OOS spread −0.26% gross / +0.03% market-adjusted, PF 0.94, bootstrap p5 negative). No deployable OOS edge under the frozen rules.

## 2. Implementation (verified against transcribe.txt)

- **SUE** = (eps − eps_est) / σ(UE), where σ(UE) is the stock's rolling std of prior unexpected-earnings; cross-sectional fallback within quarter.
- **Portfolios:** quarterly top/bottom SUE deciles → long top / short bottom, equal-weight.
- **Hold:** 60 trading days; **entry at close of the first day after the announcement** (no same-day return — look-ahead clean).
- **Friction:** 20 bps/side base (40 bps round trip per leg; ~80 bps full pair).
- **Sample screen (amendment):** entry price ≥ $5 (penny-stock exclusion; the raw run had sub-$1 names returning up to +19,800% from adjusted-price split artifacts) and 60-day return winsorized at ±300%.

## 3. Claimed vs tested (clean sample)

| Metric | IS 2013-2017 | OOS 2018-2021 | Claim |
|---|---|---|---|
| Long leg ret (60d) | +3.69% | +3.89% | high-SUE drifts up |
| Short leg ret (60d) | +1.62% | +4.16% | negative-SUE drifts down |
| **Spread (gross)** | **+2.07%** | **−0.26%** | ~4% |
| Spread (market-adj) | +1.98% | +0.03% | — |
| Profit factor | 1.11 | 0.94 | — |

## 4. Pre-registered gates (OOS)

| Gate | PASS/FAIL |
|---|---|
| 1 OOS net > 0 | FAIL (−1.06%) |
| 2 OOS bootstrap p5 > 0 | FAIL (−98 bps) |
| 3 OOS PF ≥ 1.0 | FAIL (0.94) |
| 4 drop best OOS cohort → still > 0 | FAIL |
| 5 IS gross > 0 | PASS (+2.07%) |
| 6 Look-ahead (entry day-after, SUE pre-announcement) | PASS |

## 5. Interpretation

The IS reproduces the drift (and PF 1.11 ≈ the claimed edge), but OOS it is statistically indistinguishable from zero and PF < 1. This is the textbook signature of **alpha decay**: the PEAD anomaly, robust in the 1968-2000s academic window and still present in-sample 2013-2017, has weakened substantially by 2018-2021 — consistent with independent large-cap evidence (FinLab 2016-26: only +2.75%/yr L/S, rank IC 0.012, miss-side only). On the 2012-2021 panel under frozen rules and friction, there is **no net OOS edge**.

## 6. Status / Log

- **2026-08-09:** Research spec + strategy doc created; Kaggle earnings+price dataset acquired (486MB zip) and validated (earnings 2009-2021, prices 1998-2021). Probe built, run against `transcribe.txt`-verified rules. Initial run contaminated by penny-stock adjusted-price artifacts; amended sample screen. Final clean verdict **DISCONFIRMED** (detailed in spec §7). Candidate closed.

## 7. Conclusion & Next Steps

The PEAD drift, as framed in the transcript, does not yield a deployable edge out-of-sample on this data. Consistent with the house pattern (VWAP-pullback, IVAMR, ORB/Oops), a marketed high-confidence claim fails a strict pre-registered test on owned/free data. No further work warranted on this form of the claim.
