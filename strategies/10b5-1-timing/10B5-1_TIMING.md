# 10b5-1 Adoption Timing / "Cooling-Off Watch"

**Version:** 0.1 (pre-registered mini-test drafted, not run)
**Status:** UNDER RESEARCH / Pre-registered probe (2026-08-07): bounded falsifiable mini-test of the real-time Rule 10b5-1 repurchase-plan adoption signal. NOT an edge. NOT advanced. Executing the pre-registered gates in `IA/10b5-1-adoption-timing-research-spec.md` will decide advance vs disconfirm.
**Classification:** Data asymmetry (SEC EDGAR real-time 8-K 10b5-1 adoption) + Structural forced-flow (corporate repurchase mandate overlap)
**Research spec:** `IA/10b5-1-adoption-timing-research-spec.md`
**Distinct from:** `strategies/buyback-timing/BUYBACK_TIMING.md` (broad repurchase-program signal, TESTED-NOT-ADVANCED). This is a narrower, real-time/forward event.

## 1. Executive Summary

Since the SEC 2022 amendments (effective Feb 2023), an issuer adopting a Rule 10b5-1 repurchase plan must observe a **30-day cooling-off period** before buyback trading may begin. The adoption is disclosed on Form 8-K, effectively **real-time** — unlike the lagged quarterly 10b-18 daily tables.

**The working hypothesis:** a company's 10b5-1 repurchase-plan adoption is a forward, scheduleable signal that (a) corporate buying is set to begin ~30 sessions later and continue on a formula, and (b) management is signaling an undervaluation belief. Buying the issuer — especially entering at **cooling-off expiry** when the buyback window actually opens — earns positive forward return after friction and after controlling for beta/momentum/size.

**Not an edge yet — an explicit falsification probe.** The broad buyback family already failed its bounded gate (short horizons underperform the index; primary 20d insignificant, bootstrap p5 negative). This spec isolates the *real-time* 10b5-1 adoption event that the broad study did not, and runs it under the same strict gate. If the short-horizon underperformance reproduces, the family is disconfirmed.

## 2. The Economic Edge / Why

- **Counterparty:** the repurchasing **corporation** — a constrained, schedule-driven buyer under Rule 10b5-1 that must execute its plan even in weak tape (Stephens & Weisbach 1998; Busch & Obernberger 2016; Cook et al. 2004). Its objective is not to maximize short-term profit against us.
- **The real-time forward angle (the actual edge candidate):** the 8-K 10b5-1 adoption is disclosed *before* buying begins (30-day issuer cooling-off). This is a genuinely non-lagged, scheduleable signal; most followers use the lagged quarterly tables or only react to large-cap buyback *news*. Acting at adoption, and entering at cooling-off expiry, is the data-asymmetry moat.
- **Moat:** EDGAR 8-K parsing — already built (free, `pdfplumber`/`requests`). Modest moat (large funds watch buybacks), so a real edge is not guaranteed; honesty of prior: partial-to-weak given the family's record.

### The Trade

| Leg | Entry | Direction | Notes |
|---|---|---|---|
| Long adopting issuer | Tier A: open of t+1 after 8-K adoption; **Tier B (primary): ~30 sessions after adoption (cooling-off expiry)** | Long | Tier B is the forward, non-lagged signal this probe isolates |
| Short weak/dilutive counterpart | N/A in this probe | Short excluded | report only |

## 3. Machine-Executable Rules (frozen in the spec before coding)

- **Universe:** US issuers with a 10b5-1 repurchase-plan adoption 8-K (Item 7.01/8.01 referencing a Rule 10b5-1 repurchase plan). Report full set + liquid subset (price ≥ $5, ADV filter).
- **Signal:** EDGAR-derived 10b5-1 adoption event; event date = 8-K filing date. Dedup to distinct issuer-announcements (90-day window per issuer).
- **Entry:** open of day t+1 (Tier A) / ~30 sessions after adoption (Tier B, primary).
- **Exit:** time exits at (+1,+5), (+1,+10), (+1,+20); (+1,+20) primary. No intraday.
- **Sizing:** equal-$(or equal-risk, vol-targeted per institutional approach) if n sufficient.
- **Control (mandatory):** rel-SPY at every horizon + matched non-adopting control (size/BM/momentum/beta).

## 4. Friction Model

| Cost | Base | Stress |
|---|---|---|
| Round trip | ~20 bps | ~40 bps |

Long only. No mid-price fills. Capacity not a gate at this scale.

## 5. Rejection Gates (this probe FAILS if ANY holds — pre-registered)

1. Bootstrap p5 negative at (+1,+20) primary horizon.
2. Short-horizon ((+1,+5) / (+1,+10)) rel-SPY **negative** — reproduces the family's documented failure signature.
3. Effect vanishes vs matched control / random-day after beta-momentum-size adjustment.
4. Fewer than ~30 distinct liquid events.
5. Entry not realistic (stale / unusable 30-day window).
6. Survivorship/look-ahead artifact (adoption date != true availability; or this is secretly the lagged program signal).

## 6. Research Scope / Exclusions

Free EDGAR + verified daily bars only. **No paid data, no intraday, no options, no leverage, no non-US.** Same cheap-data discipline that closed vol-fade and index-rebalancing with real answers.

## 7. Next Step

1. Harvest the 10b5-1-adoption 8-K event set over a bounded recent window (e.g. H1 2026 to match the buyback window for comparability), dedup to distinct issuer-events, verify bars.
2. Apply the pre-registered gates (bootstrap p5, short-horizon rel-SPY, matched-control, sparsity, entry-realism, artifact check).
3. Record the verdict here: **ADVANCE** (scale to full multi-year + persistence/decay gate) or **DISCONFIRMED** (family closed; no spend; no resurfacing).

## 8. Key References

- SEC Rule 10b5-1 (2022 amendments, final fact sheet 33-11138); SEC Share Repurchase Disclosure Modernization (2023).
- Stephens & Weisbach (1998) *Actual share reacquisitions in open-market repurchase programs*, JF 53.
- Busch & Obernberger (2016) *Actual share repurchases, price efficiency...*, RFS 30.
- Cook, Krigman & Leach (2004) *On the timing and execution of open market repurchases*, RFS 17.
- CFA Institute (2022) + 2019 JCF — post-2001 buyback decay (the reason this must be a strict falsification).
- See `strategies/buyback-timing/BUYBACK_TIMING.md` §9 for the full buyback literature.
