# B5 Niche-ETF NAV Dislocation Feasibility Audit

**Date:** 2026-09-17  
**Status:** `UNVERIFIABLE`

## Scope and boundary

US-listed ETFs only. Two mechanisms are evaluated independently: stale or difficult-to-price holdings creating a potentially executable secondary-market discrepancy, and impaired AP creation/redemption. This is a feasibility audit only: no returns, P&L, backtest, parameter search, strategy code, new account, or data purchase.

## Implementation

`src/quant_scripts/niche_etf_nav/valuation.py` implements coverage-aware valuation only:

```text
V_buy  = sum(quantity × underlying ask)
V_sell = sum(quantity × underlying bid)
```

Missing or invalid quotes block the gap calculation. ETF, holdings, NAV, and underlying-quote timestamps remain separate. Official NAV premium/discount is not treated as executable value.

The initial frozen universe is [`research/niche-etf-nav/frozen_universe.csv`](../research/niche-etf-nav/frozen_universe.csv). The command-line audit is documented in [`research/niche-etf-nav/Makefile`](../research/niche-etf-nav/Makefile). It requires actual synchronized input files; it does not fabricate missing historical quotes or holdings.

## Gate decisions

| Mechanism | Observability | Execution/friction | Distinctness/sample | Disposition |
|---|---|---|---|---|
| B5-01 stale underlying basket | Point-in-time executable basket history not established with owned data | Complete basket/hedge route and costs unresolved | Provisionally distinct; sample not established | `UNVERIFIABLE — NAV/TIMING` |
| B5-02 AP impairment | AP intent/capacity unavailable to retail | Retail cannot perform primary AP arbitrage | Overlaps A1 FF-04/FF-05 | `CLOSED FAMILY OVERLAP` |

## Terminal result

`UNVERIFIABLE`

B5-01 is plausible but not currently observable as an executable discrepancy. B5-02 is closed as an A1 overlap. No mechanism is approved for Phase B. See the [registry](../research/niche-etf-nav/phase_b5_candidate_registry.md) and [source evidence](../research/niche-etf-nav/phase_b5_source_evidence.md).
