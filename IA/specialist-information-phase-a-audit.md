# Phase A3: Specialist Information Mechanism Audit

**Status:** COMPLETE — `NO VIABLE MECHANISM FOUND`

**Authorization:** Explicit third bounded cycle after Phase A1 and Phase A2.

**Run boundary:** 2026-09-06; 12 concrete mechanisms investigated; no paid data, historical returns, backtest, parameter search, or strategy implementation.

## Scope and governance amendment

Phase A1 covered forced-flow and settlement. Phase A2 covered capacity-constrained securities. This A3 cycle covered specialist information only. It did not reopen A1 or A2.

The following amendment is recorded:

1. A1 is complete with `NO VIABLE MECHANISM FOUND`.
2. A2 is complete with `NO VIABLE MECHANISM FOUND`.
3. A3 was authorized for one bounded specialist-information audit.
4. Ordinary public news, EDGAR, earnings timing, PEAD, analyst revisions, social sentiment, macro releases, chart signals, and faster parsing of public information remain closed.
5. Any Phase A4 requires a separate explicit project amendment.

## Terminal result

`NO VIABLE MECHANISM FOUND`.

The audit found specialized local and institutional information channels, but none that we currently possess or can lawfully access at zero additional data cost while also providing a timestamped pre-trade advantage, defined market impact, executable venue, and sufficient independent events.

This does not claim that specialist information never creates an edge. It records that no such capability is currently available to this project.

## Specialist-information standard

A candidate had to identify the information owner, why ordinary participants lack it, how we lawfully obtain it, when it becomes known, which instrument it affects, the expected decision impact and decay, the counterparty, execution path, friction, capacity, and primary source.

“Better chart reading,” “more discipline,” “using an LLM,” “following news faster,” or a public document that everyone can access at the same time does not qualify.

## Gate notation

- **G1 Information asymmetry:** primary evidence establishes a defined early-access or specialist-interpretation advantage.
- **G2 Lawful access:** we possess or can access the source without a paid feed, misrepresentation, or restricted access.
- **G3 Timestamped observability:** arrival and interpretation can be recorded before repricing with historical and prospective coverage.
- **G4 Decision impact:** the information has a defined causal impact on an instrument or market.
- **G5 Execution/friction:** venue, counterparty, latency, spread, slippage, operational, and legal constraints are modelable.
- **G6 Sample sufficiency:** enough independent events exist without broadening the definition.

## Candidate dispositions

The complete registry is [phase_a_candidate_registry.md](../research/specialist-information/phase_a_candidate_registry.md).

| ID | Mechanism | Disposition |
|---|---|---|
| SI-01 | BVMAC official bulletin available before wider global coverage | `REJECTED — NO SPECIALIST INFORMATION` |
| SI-02 | BVMAC issuer admission, suspension, or corporate-action notice | `REJECTED — NO SPECIALIST INFORMATION` |
| SI-03 | BVMAC broker order-flow or client-position information | `UNLAWFUL OR INACCESSIBLE` |
| SI-04 | BEAC CEMAC Treasury auction announcements/results | `REJECTED — NO SPECIALIST INFORMATION` |
| SI-05 | BEAC/primary-dealer auction allocation information | `UNLAWFUL OR INACCESSIBLE` |
| SI-06 | Local government procurement or project-award information | `UNVERIFIABLE — DATA OR TIMING` |
| SI-07 | Cameroon/CEMAC commodity supply-chain information | `UNLAWFUL OR INACCESSIBLE` |
| SI-08 | Local port, freight, or inventory information | `UNLAWFUL OR INACCESSIBLE` |
| SI-09 | Local bank, mobile-money, or payment-flow information | `UNLAWFUL OR INACCESSIBLE` |
| SI-10 | Specialized French-language regulatory interpretation | `CLOSED FAMILY OVERLAP` |
| SI-11 | Exchange-member technical or settlement notices before public release | `UNLAWFUL OR INACCESSIBLE` |
| SI-12 | Local professional/business-network information | `UNVERIFIABLE — DATA OR TIMING` |

## Primary-source conclusion

BVMAC publishes official bulletins, market notices, trading rules, and issuer announcements. Those are specialist local-market documents, but they are public market information rather than an information source uniquely available to us. [BVMAC official site](https://www.bvm-ac.org/), [BVMAC general rules](https://www.bvm-ac.org/wp-content/uploads/2025/04/LE-REGLEMENT-GENERAL-DE-LA-BVMAC.pdf)

BEAC publishes CEMAC Treasury auction schedules, announcements, results, and market statistics. The primary market is reserved for Specialists in Treasury Securities, while the secondary market is accessible through stated dealer channels. We are not a documented SVT and do not possess pre-allocation or client-order information. [BEAC public-securities market](https://www.beac.int/m-des-titres-publics/presentation-generale/), [BEAC announcements](https://www.beac.int/m-des-titres-publics/annonces-et-communiques/)

The other candidates require private operational access, participant data, or a verified professional network that has not been identified. They therefore cannot advance merely because such information might exist in principle.

## Phase B/C decision

No candidate passed all six gates. No candidate is approved for Phase B, and no Phase C trading test is authorized.

The specialist-information family is closed for this audit. A future A4 requires an explicit project amendment and a genuinely new capability, not another scan of public data.

