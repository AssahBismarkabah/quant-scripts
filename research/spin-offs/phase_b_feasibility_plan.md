# Spin-Offs: Feasibility and Observability Plan

## Scope

Candidate B15 from the deep-research reconciliation. The only permitted hypothesis is temporary post-distribution supply caused by a documented recipient constraint or predictable unwillingness to hold the distributed security.

## Event record

Each event must have primary-source evidence for:

`parent | spinco | CIK/CUSIP/tickers | filing timestamp | effectiveness | record date | distribution date | ex-date | first tradable timestamp | distribution ratio | fractional treatment | venue | price-source coverage`

## Evidence standards

- SEC filings and issuer information statements establish transaction terms.
- Exchange/DTCC notices establish trading and entitlement mechanics.
- No post-event price movement may be used to prove the mechanism.
- Recipient selling must be supported by a mandate, rule, documented policy, or an observable pre-trade process; “institutional investors may sell” is insufficient.

## Access and cost checks

The intended route is long-only US equity execution through the existing IBKR capability. The audit must separately verify listing, borrow is not required, orderability, spread, slippage, corporate-action booking, delisting/survivorship handling, and a conservative position-size ceiling.

## Stop conditions

Stop before return analysis if the event timestamps, recipient constraint, historical coverage, or executable costs cannot be established. A successful event inventory alone is not approval.

## Next artifact

If all gates pass, create a separate frozen pre-registration containing one entry rule, one exit rule, fixed event universe, benchmark, cost model, IS/OOS split, and falsification gates. Until then, no strategy code or P&L is permitted.

## Inventory implementation

`harvest_spin_off_filings.py` performs the first source-only census against the SEC EDGAR full-text index. It records filing identity and acceptance timestamps for candidate Form 10, Form 10-12B, and 8-K documents. The output is an evidence index, not a validated spin-off-event dataset. Each row requires manual/primary-document verification before it can become an event.

The initial 2025 Q1 pilot confirmed that the EDGAR query is capped and noisy: it returned 100 hits per month, including unrelated filing descriptions, with timestamps missing on many index rows. The implementation must therefore add underlying-document retrieval and deterministic classification before any event count can be trusted.

The completed pilot review queue is `outputs/filing_review_queue.csv`: 220 filing rows, not 220 events. The next pass must consolidate amendments and parent/spinco filings into one transaction ID and extract dates only from the governing information statement/Form 10 and exchange or DTCC notice.

The 25 likely rows have now been fetched into `outputs/primary_evidence_review.csv`. This is an evidence-extraction aid, not an approved event registry: it preserves source URLs and snippets while leaving transaction identity, dates, and seller-constraint decisions for primary-document verification.

`build_transaction_review.py` creates provisional issuer-level clusters from the review queue. These clusters are only a de-duplication aid: a genuine transaction may involve separate parent and spinco CIKs, while one issuer may mention multiple transactions. Each cluster therefore remains subject to primary-document review.

Example:

```text
python research/spin-offs/harvest_spin_off_filings.py --start 2010-01-01 --end 2026-09-17
```
