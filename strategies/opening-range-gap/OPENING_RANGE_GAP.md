# Opening-Range / Gap Strategies (ORB, Gap Fill, Oops) — "Open & Range" Trio

**Version:** 0.3 (probe run, 2026-08-09)
**Status:** DISCONFIRMED (ORB, Oops) + Gap Fill NOT FALSIFIABLE AS A TRADE (raw fill-rate fails OOS). Pre-registered probe executed on owned Databento NQ RTH intraday.
**Classification:** Intraday opening-range / gap-reversion microstrategies from a trading-education transcript (Crabel/Patrick Neil/Larry Williams lineage)
**Research spec:** `IA/opening-range-gap-strategies-research-spec.md`
**Source:** single trading-education transcript (`transcribe.txt`) claiming all three are mechanically simple, "decades of data," and "back tested"; same speaker lineage as the earlier VWAP-pullback and IVAMR sources. Rules extracted verbatim and frozen.

## 1. Executive Summary

Three simple, claimed-validated intraday strategies — ORB (Crabel-style opening-range breakout), Gap Fill (Patrick Neil), Oops (Larry Williams) — tested independently on owned NQ RTH 1-min data 2013→2026 with a pre-registered IS/OOS split (2014-18 IS / 2019-26 OOS) and the house strict-gate discipline.

Result: **ORB DISCONFIRMED** (IS net-negative, OOS tail-fragile), **Oops DISCONFIRMED** (net-negative IS and OOS), **Gap Fill not falsifiable as a trade** (transcript gives no stop/exit) and its one objective claim — the raw gap-fill rate — **does not clear OOS** (IS 0.628 / OOS 0.5885 vs the claimed 65-70% "in the S&P 500"). This is the third clean disconfirmation from the same training lineage, matching VWAP-pullback and IVAMR.

## 2. Intent

Decide, with pre-registered gates and a clean out-of-sample holdout, whether each of the three named mechanical strategies produces a real, friction-adjusted edge on data we already own — or is another marketed-but-unfounded claim.

## 3. Rules (FROZEN — extracted from `transcribe.txt`, do not tune)

**Instrument/bars:** NQ futures, 5-min execution bars, RTH only (09:30–16:00 ET). One entry per day per strategy.

- **ORB** (Crabel/Fabio): first 15-min RTH range (09:30–09:45); after 09:45, enter on the first 5-min close beyond the range; stop at the opposite side of the range ("slightly below the other side"); target 1:2 RR.
- **Gap Fill** (Patrick Neil): day opens gapped vs prev-day close; enter in the fill direction on a break of structure after 09:45; target = full fill (prev-day close), flat at 15:55. *No stop/exit specified in source* → P&L not treated as falsifiable (see §7).
- **Oops** (Larry Williams): gap ≥20 pts beyond prev-day high/low; enter on a 5-min close breaking back through the level; fixed stop beyond the level; exit at the **next 5-min bar close** ("we sell until the next candle closes with a fixed stop-loss").

## 4. Claimed vs tested

| Claimed (transcript) | What we tested | Result |
|---|---|---|
| ORB "outperforms the S&P 500"; "great classic" | IS/OOS net, win-rate, PF, bootstrap, tail | DISCONFIRMED: IS −2,565; OOS tail-fragile |
| "65-70% of gaps are filled in the S&P 500; NASDAQ higher" | raw NQ gap-fill rate, IS/OOS | Rates IS 0.628 / OOS 0.5885 → OOS below 0.60 & below IS |
| Oops "validated on DAX 2012-2024"; gap min 20 pts | IS/OOS P&L on NQ | DISCONFIRMED: IS −14.5, OOS −44.0 |

## 5. Profit / loss driver (per claim)

ORB rides the day's directional continuation after the opening range is broken; Gap Fill captures the (claimed) statistical tendency of overnight gaps to fill; Oops fades a gap that has extended beyond the prior day's range, betting on a return inside that range.

## 6. Risk and Failure Modes

- **Look-ahead (gate 6):** opening range and prev-day levels must be complete before any trigger; fills at next-bar open; stops/targets from the actual fill price. Audited structural — PASS.
- **Friction:** 0.5 pts/turn base applied; tight stops are friction-sensitive.
- **Level non-invariance (Oops):** the literal fixed 20-pt gap is not invariant as NQ rose ~3500→20000 over 2014-2026 → near-empty IS (7 trades) vs active OOS (304). Footnote, not a rule change (kept faithful to the source).
- **Underspecification (Gap Fill):** no stop/exit in the source made the P&L unfalsifiable; a naive placeholder stop produced a phantom edge (871/1,244 "stop" exits were wins). Addressed by reporting only the fill-rate claim.

## 7. Probe Results (2026-08-09)

Combined owned NQ RTH 1-min (2013-11→2026-08), 5-min bars, one entry/day, 0.5 pts/turn friction, bootstrap p5 (n=5000, seed 42). Outputs in `research/opening-range-gap/outputs/`.

| Strategy | IS n / net (pts) | OOS n / net (pts) | OOS win% / PF | Verdict |
|---|---|---|---|---|
| ORB | 1,123 / **−2,565.5** | 1,801 / +9,473.3 | 47.4% / 1.14 | **DISCONFIRMED** |
| Gap Fill | 1,213 / n/a | 1,960 / n/a | n/a | **NOT FALSIFIABLE AS A TRADE** |
| Oops | 7 / **−14.5** | 304 / **−44.0** | 33.2% / 1.04 | **DISCONFIRMED** |

**ORB — DISCONFIRMED.** Gate 5 (IS net > 0) FAIL (IS −2,565.5); gate 4 (tail fragility) FAIL (52.2% of OOS days eat the kill-switch cap, > 30% limit). OOS is net-positive (+9,473) but the reproduction and tail gates fail, so the pre-registered verdict is DISCONFIRMED.

**Gap Fill — NOT FALSIFIABLE AS A TRADE, fill-rate fails OOS.** The transcript specifies no stop and no concrete exit. A placeholder stop was shown to be buggy (placed on the wrong side of entry when a gap-down opens below yesterday's low → 871 of 1,244 "stop" exits were wins), making the naive P&L an artifact. Per the house rule (falsify only what the source specifies), the P&L side is dropped. The only objective claim, the raw gap-fill rate, is **IS 0.628 / OOS 0.5885** — both near the claimed 65-70%, but OOS is below the 0.60 bound and below IS, so it does not clear on clean OOS.

**Oops — DISCONFIRMED.** Gate 1 (OOS net > 0) FAIL (−44.0); gate 3 (win-rate ≥0.50) FAIL (33.2%); gate 5 (IS net > 0) FAIL (−14.5). The fixed-20-pt threshold leaves IS nearly sample-empty (7 trades) — the verdict effectively rests on the 304-trade OOS, which is net-negative.

## 8. Status / Log

- **2026-08-09:** Spec §8 frozen; transcript details verified against `transcribe.txt` (one entry/day; Oops exit = next 5-min bar close; gap min 20 pts; gap-fill rate 65-70% S&P claim). Probe scaffolded (`src/quant_scripts/opening_range_gap/`, `research/opening-range-gap/`) and run. First run had a stop/target fill-alignment bug (inflated churn); fixed to fill-relative levels + one entry/day. Final verdicts recorded in §7. Candidate family closed.

## 9. Conclusion & Next Steps

Three more marketed claims from the same training lineage do not hold on owned data: ORB and Oops are clean disconfirmations; Gap Fill's only falsifiable claim (fill rate) fails OOS at the margin. Nothing warrants deployment. The strategy doc, spec, README, and docs/README should be updated (done) and the stage list handed off for commit/push.
