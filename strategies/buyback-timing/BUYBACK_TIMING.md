# Share Repurchase (Buyback) Timing / "Buyback Put"

**Version:** 0.1 (research spec stage)
**Status:** UNDER RESEARCH (2026-08-04) - not yet an edge, not approved. Research spec at `IA/buyback-timing-research-spec.md`. No code, no data, no backtest run yet. This record will be updated with test results and a verdict only after a pre-registered study runs.
**Classification:** Structural forced-flow (Corporate-repurchase mandate overlap) + Data asymmetry (mandate & legal-constraint / data-asymmetry category)
**Selected from:** `IA/structural-edge-survey-2025-2026.md` — the #1 testable candidate on free/cheap data.

## 1. Executive Summary

Companies repurchasing their own shares are price-insensitive, mandate-driven buyers. Academic work documents (a) that they execute heavily **after price declines** and in undervaluation windows (Stephens & Weisbach 1998; Peyer & Vermaelen 2009; Dittmar 2000), (b) that repurchase **execution** — not just announcement — precedes positive abnormal returns (Busch & Obernberger 2016), and (c) that execution **provides price support** (Cook et al. 2004; Li & Swanson 2016; Chee 2022). Since the SEC's 2022 rule amendments, an issuer adopting a Rule 10b5-1 repurchase plan must observe a **30-day cooling-off period** before buyback trading begins — giving a near-real-time, forward, scheduled signal we can trade, unlike the lagged quarterly 10b-18 disclosure tables.

**The working hypothesis:** buying the repurchasing issuer after a 10b5-1 adoption signal (Tiers A/B) or after a post-decline buyback-active window (Tier C) earns positive forward return after friction **and after controlling for beta/momentum/size** (matched control).

**Not an edge yet:** the two failure modes that killed prior candidates are explicitly pre-gated — (1) the beat-random/beta-confound test (vol-fade), and (2) persistence across years (index-rebalancing). Until the pre-registered study runs and passes those, this is a research hypothesis, not a trade.

## 2. The Economic Edge

### The Why

- **Asymmetry of constraint:** the counterparty is the **corporation**, whose repurchase objective (return capital, offset dilution, signal undervaluation, support price) is not to maximize short-term profit against us. Rule 10b-18 and Rule 10b5-1 make the buying schedule semi-committed.
- **Moat (barrier to arbitrage):** data asymmetry — the 10b5-1 adoption signal and the daily disclosure tables must be parsed from EDGAR; this is buildable and still under-exploited in the small-cap space, but the moat is modest (large funds already watch buybacks). Honest prior: partial.
- **Positive EV after friction:** to be proven. Single-stock friction 10-20 bps base; buyback demand ~$6B/day market-wide is large enough that capacity is rarely the constraint.

### The Counterparty

The repurchasing corporation and, indirectly, the passive/dilution ecosystem (issuers offsetting stock-comp dilution; capital-return programs). They buy regardless of the marginal price move because they are executing a committed program — especially in blackout windows under 10b5-1 plans (which can run through blackouts).

### The Trade

| Leg | Entry | Direction | Evidence |
|---|---|---|---|
| Long repurchasing issuer | After 10b5-1 buyback-plan adoption (Tier A), at ~30-day cooling-off expiry (Tier B), or in a post-decline buyback-active window (Tier C) | Long | ILV 1995; SW 1998; Busch & Obernberger 2016; Cook et al. 2004; Li & Swanson 2016; Chee 2022; Elm 2026 |
| (Reported, not base) Short the weak/dilutive counterpart | N/A in v1 | Short excluded in v1 | — |

### Decay Warning

Long-run announcement-return effects have **decayed** post-2001 (CFA review 2022; 2019 JCF). The execution/price-support mechanic is a different, less-decayed mechanism, but decay is a live risk that the persistence gate must catch. If the edge is just low-beta/value/momentum exposure, it is not an edge — the matched-control adjustment is mandatory.

## 3. Machine-Executable Rules (to be frozen in the spec before coding)

- **Universe:** S&P 500 + S&P 600 constituents; long only.
- **Signal:** EDGAR-derived 10b5-1 buyback-plan adoption (Form 8-K / 10-Q / 10-K exhibit) and/or new repurchase authorization; event date; 30-day cooling-off for Tier B.
- **Entry:** open of day t+1 after the signal (Tier A), or ~30 sessions after adoption at cooling-off expiry (Tier B), or after a pre-registered decline magnitude in an active-repurchaser (Tier C).
- **Exit:** pre-registered horizon windows; time exit; stop-loss reported.
- **Sizing:** equal-risk / volatility-targeted per the institutional approach; from the lower of risk budget, depth, and volatility target.
- **Control (mandatory):** matched non-repurchasing names on size/book-to-market/momentum/beta; the "beats matched control after beta adjustment" gate.

## 4. Friction Model (provisional)

| Cost | Base Case | Stress Case |
|---|---|---|
| Spread crossing | ~5-10 bps/side | ~20-30 bps/side (small-cap/high-vol) |
| Market impact | ~5 bps/side | ~20 bps/side |
| Round trip | **~10-20 bps** (large) / **~40-60 bps** (small-cap) | higher in stress |

Borrow: N/A (we are long). No mid-price fills. Capacity reported as notional sensitivity.

## 5. Research Scope

- Signal: EDGAR 10b5-1 / repurchase-program parsing + verified daily bars + corporate-action calendar.
- Horizon: event-window CARs (0,+1), (+1,+5), (+5,+20) and medium; reported-not-selected.
- Excluded: options, shorting, leverage, non-US, paid intraday data.
- Data route: EDGAR (free) + Yahoo/verified bars lineage (per the vol-fade/SPY work) — the same cheap-data discipline that closed the last candidates with real answers. Feasibility check (2026-08-04): EDGAR full-text search + retrieval confirmed working (8-K repurchase-program announcements parseable); build the event set from 8-K / 10b5-1 disclosures, NOT the uneven daily 10b-18 table (some top repurchasers report "None" in it, e.g. Alphabet Q2 2026).

## 6. Test Results

**Not yet run.** This section will record the pre-registered study output (event counts, CARs, matched-control excess, bootstrap p5, persistence across years, friction survival) and the gate verdict once the spec is frozen and the study executes.

## 7. Rejection Gates (provisional; to be finalized in the spec)

Reject if any of the following is true:
- Effect vanishes after beta/momentum/size adjustment or vs the matched control (vol-fade beat-random failure).
- Effect does not survive across years / depends on one year or quarter (index-rebal failure).
- Not tradable after realistic friction (breaks when entry is realistic, not at the exact disclosure timestamp).
- Signal too sparse; too few independent events.
- Apparent return is a data artifact (survivorship bias, look-ahead, lagged-table dates).
- Capacity not credible.

## 8. Next Step

1. Finalize the pre-registration spec (`IA/buyback-timing-research-spec.md`) — close the unresolved items (EDGAR 10b5-1 feed verification; 30-day cooling-off uniformity; friction; capital scale).
2. On approval, acquire/verify data (EDGAR parse + bars + delisted coverage) and implement the study.
3. Run the pre-registered study and record the verdict here.

## 9. Key References

- Ikenberry, Lakonishok & Vermaelen (1995), *Market underreaction to open market share repurchases*, JFE 39(2-3):181-208.
- Stephens & Weisbach (1998), *Actual share reacquisitions in open-market repurchase programs*, JF 53:313-333.
- Grullon & Michaely (2002), *Dividends, share repurchases, and the substitution hypothesis*, JF 57:1649-1684.
- Comment & Jarrell (1991), *The relative signalling power of ... open-market share repurchases*, JF 46(4):1243-1271.
- Peyer & Vermaelen (2009), *The nature and persistence of buyback anomalies*, RFS 22(4):1693-1745.
- Dittmar (2000), *Why do firms repurchase stock?*, J Business 73(3):331-355.
- Busch & Obernberger (2016), *Actual share repurchases, price efficiency, and the information content of stock prices*, RFS 30(1):324-362.
- Cook, Krigman & Leach (2004), *On the timing and execution of open market repurchases*, RFS 17(2):463-498.
- Li & Swanson (2016), *Is price support a motive for increasing share repurchases?*, JCF 38:77-91.
- Chee (2022), *Do share repurchases distort stock prices?*.
- Bonaimé et al. (2014); Ikenberry & Vermaelen (1996).
- CFA Institute (2022), *Stock buyback motivations and consequences* (lit review; documents post-2001 decay).
- 2019 JCF study on long-run returns 1994-2014 (decay evidence).
- Elm Wealth (2026), *The impact of US stock buybacks: theory vs practice* (~$6B/day buying).
- SEC Rule 10b-18; SEC Rule 10b5-1 (2022 amendments, final fact sheet 33-11138); SEC 2023 Share Repurchase Disclosure Modernization.
