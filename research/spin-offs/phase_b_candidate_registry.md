# Spin-Off Feasibility Candidate Registry

This registry contains transaction-level candidates identified so far. It is not a return dataset.

| ID | Transaction | Event evidence | Pre-trade timing | Recipient constraint | Execution/friction | Sample | Disposition |
|---|---|---|---|---|---|---|---|
| S01 | Western Digital → SanDisk | Form 10 information statement and 8-K establish pro-rata distribution, record/distribution dates, and Nasdaq trading sequence | Available before event | **Not established**; holders receive shares automatically and choose whether to hold/dispose | WDC/SNDK venue exists; spread, corporate-action booking, and sizing not frozen | One event | `REJECTED — S04 NOT PRESENT` |
| S02 | Lennar → Millrose | 8-K establishes completion, approximately 80% distribution, NYSE listing, and 20% retained position | Available before/at event from issuer filings | **Not established**; shareholder elections and retained parent shares are not forced selling | Venue exists; final costs and historical event handling not frozen | One event | `UNVERIFIABLE — NO CONSTRAINT EVIDENCE` |
| S03 | MDU Resources → Everus | Official issuer filing confirms completion on 2024-10-31 | Retrospectively confirmable; pre-trade source still required | **Not established** | Venue and costs not yet frozen | One event | `UNVERIFIABLE — DATA OR TIMING` |
| S04 | Spin-off excluded from parent’s tracked index | S&P methodology documents that an ineligible spun-off company may be sold by index-tracking funds at the ex-date close | Potentially observable from index methodology and advance notice | **Mechanism supported in principle**; the 2003 study finds preference-driven rebalancing but generally no associated abnormal price movement | Requires point-in-time index membership, executable close orders, and full cost model | Unknown; must be counted transaction-by-transaction | `OPEN FEASIBILITY — FIND A QUALIFYING MODERN EVENT` |
| S05 | TechnipFMC → Technip Energies | S&P announced TechnipFMC’s removal ahead of the spin-off and stated Technip Energies was expected to trade in ADR form OTC | Announcement was public before the expected completion | Child’s index treatment and fund selling require separate verification | OTC ADR route and execution quality are not currently established through IBKR scope | One identified event; insufficient alone | `REJECTED — EXECUTION/FRICTION` |

S04 checkpoint: official policy evidence exists, but the reviewed modern SanDisk event was an index addition, not an exclusion. The registry therefore contains no qualifying modern S04 event yet.

## Registry rule

Search hits, amendments, parent/spinco duplicates, and post-event confirmations do not count as independent events. A candidate can advance only after a primary source identifies a defined participant constraint and the event can be reconstructed prospectively.

## Current result

No registry candidate currently passes all mechanism gates. No backtest is authorized.
