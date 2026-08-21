# BVMAC/CEMAC Retail-Scale Trading Feasibility

**Date:** 2026-08-21  
**Type:** primary-source feasibility study; not a trading strategy or investment recommendation  
**Status:** **NO-GO for active, systematic, discretionary, or prop-funded BVMAC trading under the evidence currently available.**

## 1. Decision in one paragraph

BVMAC is a real, regulated regional market that a Cameroon-based individual can access through a licensed Société de Bourse. It also publishes daily official quotation bulletins and issuer documents, so the market is not invisible. That does **not** make it a viable independent trading business. The current market is a once-daily cash fixing with a seven-equity universe, very low documented equity turnover, broker-mediated execution, unverified broker-specific all-in costs, and no identified forced-flow or information mechanism. Those facts rule out intraday trading, ordinary market making, a diversified cross-sectional book, and any claim of a currently testable active edge. No strategy should be written, backtested, or deployed from this memo.

This is a useful result: it distinguishes a real local market from a real local *trading opportunity*. They are not the same thing.

## 2. Scope and question

This study asks a narrow question:

> Can a Cameroon-based individual, using legal public information, retail-scale capital, broker-mediated execution, and no proprietary flow or co-location, build a testable active trading business on **BVMAC-listed CEMAC instruments**?

It does not assess whether a particular share or bond is a good long-term personal investment, direct participation in BEAC primary auctions, private/unlisted securities, or any non-BVMAC venue. It also does not authorize the use of non-public information, solicitation of confidential information, or any action that requires a regulated licence.

## 3. What was investigated

The assessment uses BVMAC, COSUMAF, and BEAC primary sources only:

- market organisation, investor access, broker roster, trading schedule, and published market rules;
- BVMAC's 2024 annual activity report and current official quotation bulletins;
- availability of historical BOC PDFs and issuer financial documents;
- the current CEMAC regulatory context.

No broker was contacted, no account was opened, no order was placed, and no capital was committed.

## 4. Confirmed market mechanics

### 4.1 It is accessible, but only through an intermediary

BVMAC states that an individual investor must choose a licensed Société de Bourse and open both a securities account and a cash account. Its official broker list includes multiple Cameroon-based firms. This is an **access pass**, not an execution-quality pass. The sources reviewed do not establish an API, a retail machine-execution interface, actual fill latency, or an export of complete individual order/fill records. One broker, SG Capital CEMAC, says it can centralise and execute client orders in real time and provides secure communication platforms; this confirms broker-mediated handling, not direct market access or an automated trading channel. [Investor access](https://www.bvm-ac.org/espace-investisseurs-fr/investisseurs-acces-aux-produits-boursiers/) · [licensed broker roster](https://www.bvm-ac.org/societes-de-bourse-par-pays/) · [SG Capital CEMAC](https://particuliers.societegenerale.cm/fr/banque-quotidien/une-expertise-marches-financiers/societe-generale-capital-securities-central-africa/)

BVMAC says investors pay no *direct* BVMAC transaction commission, but it explicitly tells investors to obtain the tariff terms applied by their broker. One public example is sufficient to show why this matters: Société Générale Cameroun's retail market-finance tariff, effective 1 April 2025, lists a 0.30% BVMAC transaction component, a 0.11925% TTC central-depository movement charge, and a 0.59625% TTC brokerage charge. Those visible components alone are about **1.02% of gross value per side**—about **2.03% round trip**—before bid/ask spread, market impact, annual custody, and any other broker-specific charge. This is not a universal tariff quote; other brokers and current client agreements must be confirmed in writing. It is enough to fail an active-trading cost gate under the observed liquidity. [BVMAC commission page](https://www.bvm-ac.org/espace-investisseurs-fr/investisseurs-commissions-de-transactions/) · [SG Cameroon tariff, effective 1 April 2025](https://particuliers.societegenerale.cm/fileadmin/user_upload/Cameroun/PDF/2025/T2_-_2025/Tarification_operations_marche_financier_V_mai_2025_-_tarifaire_entreprises.pdf)

### 4.2 The present equity market is a daily fixing, not an intraday venue

The published schedule has a pre-opening phase from 09:00 to 11:00 GMT+1 and one fixing at 11:00. The market rules describe a fixing process; they do not describe a continuous retail trading venue. [Trading schedule](https://www.bvm-ac.org/horaires-seances-de-cotation/) · [published general rules](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf)

The published rules also state that trades are cash-only: a buyer must have the full funds and a seller must already hold the securities when the order is submitted. Under that published framework, one cannot assume retail short selling, leverage, intraday turnover, or market-neutral relative-value implementation. Rules may have been amended under the newer COSUMAF framework, so a broker and COSUMAF must confirm the current operational rulebook before any real account decision. [BVMAC rules, Articles 29-31](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf) · [COSUMAF regulatory update](https://cosumaf.org/files/documents/01KTTX112ZGHEVHXG16TTS0VN2.pdf)

## 5. Liquidity and universe: the binding constraint

The case against active trading is empirical, not aesthetic.

| Measure | Primary-source observation | Implication |
|---|---:|---|
| Listed equities | 6 at 2024 year-end; 7 shown in the 21 August 2026 BOC | Too few names for a robust cross-sectional book or sector-neutral portfolio. |
| 2024 equity turnover | FCFA 622 million | Small annual secondary-market value, not a pool of daily executable capacity. |
| 2024 equity transactions | 358 | About 1.4 transactions per trading session on average; the implied FCFA 1.74 million per transaction is an aggregate average, **not** safe order capacity. |
| 2024 equity liquidity ratio | 1.05% | BVMAC itself describes this as weak overall liquidity and notes buy-and-hold behavior. |
| 21 Aug. 2026 official session | FCFA 100,000, two shares, one equity transaction; zero bond transactions | A current snapshot of intermittent executions, not a reliable trading surface. |
| 19 Aug. 2026 official session | FCFA 1.089 million, six equity transactions; zero bond transactions | Confirms that even active-looking days remain very small. |

Sources: [BVMAC 2024 annual report](https://www.bvm-ac.org/wp-content/uploads/2025/10/RA-2024_compressed.pdf), pp. 14-15 and 26; [BOC, 21 August 2026](https://www.bvm-ac.org/wp-content/uploads/2026/08/BOC-20260821.pdf); [BOC, 19 August 2026](https://www.bvm-ac.org/wp-content/uploads/2026/08/BOC-20260819.pdf).

The annual report is especially clear: it records FCFA 622 million of equity trades in 2024, down 84% from 2023, and a 1.05% equity liquidity ratio. It explicitly characterises overall listed-equity liquidity as weak. The bond compartment transacted far more value in 2024 (FCFA 16.897 billion), but the daily BOCs show repeated zero bond prints, and the accessible retail cash-only structure leaves no credible basis for a market-neutral bond or yield-curve strategy.

Low liquidity is not an edge. It can make a price appear slow or stale while making the position impossible to enter or exit at that price. The same constraint that might deter a large fund can also prevent a small trader from obtaining a fill, measuring a real execution price, or exiting after adverse news.

## 6. Data: enough to inspect the market, not enough to assert alpha

Two useful data assets do exist:

1. The BVMAC [BOC archive](https://www.bvm-ac.org/bulletin-officiel-de-la-cote-boc/) exposes daily PDFs back to 2019, including current close, displayed demand/supply, transacted volume, value, and transaction count.
2. The issuer pages publish financial statements and some reports. For example, the [SEMC issuer page](https://www.bvm-ac.org/espace-emetteurs/emetteurs-actions/) links annual OHADA and IFRS statements from 2019 through 2025.

This is sufficient to build a **data census**: a clean, point-in-time record of official prints, visible order quantities, corporate documents, and publication dates. It is not sufficient by itself to claim an information advantage.

Critical missing pieces remain:

- no validated historical intraday order book, queue position, trade-side, or retail fill dataset;
- no identified public API or machine-execution channel for an individual;
- no all-broker tariff, minimum-order, settlement, custody, transfer, and rejection dataset; one published broker tariff already implies a roughly 2.03% round trip before spread and impact;
- no verified timestamps for when every issuer document became actionable to a client;
- only a handful of equities and therefore too few independent events for a broad statistical search.

The exchange says it disseminates real-time and historical market information, but the available public interface is primarily a document archive. A paid data agreement or broker feed could improve measurement; it would not solve the liquidity or strategy-mechanism failures on its own. [BVMAC services](https://www.bvm-ac.org/la-bvmac/nos-produits-et-services/)

## 7. Candidate edge families and verdicts

| Family | Why it might sound plausible | What the evidence actually permits | Verdict |
|---|---|---|---|
| Intraday/discretionary trading | Local market, visible daily order quantities | One daily fixing; thin executions; no verified intraday/fill data | **NO-GO** |
| Market making/liquidity provision | Wide displayed gaps may look like spread income | A single fixing and scarce counterparty flow do not provide queue priority or reliable exits | **NO-GO** |
| Cross-sectional quant equity book | Seven listed names may be overlooked | Universe is too small and long-only; no diversification or robust sample | **NO-GO** |
| Event-driven public-information trading | Corporate disclosures may be fragmented or slow | No demonstrated delay, no timestamped event census, and no executable-capacity model | **NOT ADVANCED**; no strategy claim |
| Bond relative value/carry | Bond turnover is larger than equity turnover | Mostly institutional activity, no verified retail execution economics, and cash-only implementation | **NO-GO for active alpha** |
| Long-horizon local fundamental ownership | Local knowledge could improve research quality | This is investment research, not a currently demonstrated trading edge or income business | **Out of scope** |

The key point is that an untested event-driven idea is not a live candidate. Before it could become one, it would need a named public event, a precise source timestamp, a defined counterparty/constraint, a valid execution price, enough independent observations, and net performance after broker-specific costs. None is established here.

## 8. Feasibility-gate result

| Gate | Result | Reason |
|---|---|---|
| Legal retail account route | **Conditional pass** | Individual accounts are permitted through licensed brokers; operational terms must be confirmed. |
| Public end-of-day data route | **Pass** | Official BOC PDFs are publicly archived from 2019 onward. |
| Historical event-data route | **Partial pass** | Some issuer reports are published; completeness and timestamps are unverified. |
| Active execution capacity | **Fail** | Daily fixing plus documented weak equity liquidity and sparse current transactions. |
| Cost model | **Fail** | One published retail tariff implies roughly 2.03% round trip before spread and impact; other broker terms remain unverified. |
| Statistical breadth | **Fail** | Six-to-seven equities, limited events, no credible diversified book. |
| Economic mechanism | **Fail** | No forced flow, durable information delay, or tradeable counterparty asymmetry identified. |
| Regulatory/operational certainty | **Fail / needs confirmation** | The current regulatory framework is evolving; broker confirmation is necessary. |

**Overall result: NO-GO.** The access and raw-document data passes do not overcome the failures in capacity, cost certainty, sample size, and mechanism.

The companion [BVMAC Broker Capability Audit](bvmac-broker-capability-audit.md) compares the licensed brokers’ publicly documented customer capabilities. It finds service-level differences but no evidence that a broker changes this active-trading verdict.

## 9. What would have to change before reopening this lane

This memo is a terminal decision for the current active-trading idea. It may be reopened only if all of the following are available before a new research spec is written:

1. A licensed Cameroon broker provides, in writing, the complete retail tariff, custody/settlement terms, order channel, minimums, and an export of actual order/fill records. The replacement cost model must be materially lower than the published approximately 2.03% pre-spread round trip or an extremely infrequent long-horizon mechanism must justify it.
2. A reproducible data census demonstrates enough timestamped public events and independently executable observations to meet the repository's existing minimum-sample discipline.
3. A causal mechanism is identified before testing: who must trade, why the effect survives, and why a fully funded small investor can enter and exit without surrendering it to impact.
4. A realistic capacity model shows that intended order sizes can be both entered and exited across normal and stressed sessions using actual, not displayed, transaction history.
5. The idea is legally vetted as public-information research. This document is not legal, tax, or investment advice.

An increase in data volume alone, a new chart pattern, a prop account, or a belief that local traders are less sophisticated is **not** a reopen condition.

## 10. Consequence for the independent-trading goal

This research does not say that a Cameroon-based investor cannot participate in BVMAC or cannot study local companies. It says the proposed local-market route does not currently supply a credible path to an active, independent, retail-scale trading business.

The correct next state is therefore not a BVMAC strategy implementation. It is:

```text
No live BVMAC trading or prop deployment
→ retain the public BOC/issuer sources as a documented local data asset
→ wait for a genuine change in access, liquidity, or a testable legal information mechanism
→ otherwise keep the independent active-trading lane closed
```

That conclusion is deliberately narrower than “no one can ever make money in this market,” but it is strong enough to prevent another untestable strategy search.

## 11. Source record

- BVMAC, [2024 annual activity report](https://www.bvm-ac.org/wp-content/uploads/2025/10/RA-2024_compressed.pdf), accessed 2026-08-21.
- BVMAC, [official quotation-bulletin archive](https://www.bvm-ac.org/bulletin-officiel-de-la-cote-boc/), accessed 2026-08-21.
- BVMAC, [BOC 21 August 2026](https://www.bvm-ac.org/wp-content/uploads/2026/08/BOC-20260821.pdf) and [BOC 19 August 2026](https://www.bvm-ac.org/wp-content/uploads/2026/08/BOC-20260819.pdf), accessed 2026-08-21.
- BVMAC, [investor access](https://www.bvm-ac.org/espace-investisseurs-fr/investisseurs-acces-aux-produits-boursiers/), [broker roster](https://www.bvm-ac.org/societes-de-bourse-par-pays/), [trading schedule](https://www.bvm-ac.org/horaires-seances-de-cotation/), and [published general rules](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf), accessed 2026-08-21.
- BVMAC, [issuer financial-document portal](https://www.bvm-ac.org/espace-emetteurs/emetteurs-actions/) and [market-data services](https://www.bvm-ac.org/la-bvmac/nos-produits-et-services/), accessed 2026-08-21.
- Société Générale Cameroun, [retail financial-market tariff, effective 1 April 2025](https://particuliers.societegenerale.cm/fileadmin/user_upload/Cameroun/PDF/2025/T2_-_2025/Tarification_operations_marche_financier_V_mai_2025_-_tarifaire_entreprises.pdf), accessed 2026-08-21.
- Société Générale Cameroun, [SG Capital CEMAC brokerage and execution description](https://particuliers.societegenerale.cm/fr/banque-quotidien/une-expertise-marches-financiers/societe-generale-capital-securities-central-africa/), accessed 2026-08-21.
- COSUMAF, [L'Essentiel — second half 2025](https://cosumaf.org/files/documents/01KQRSJ4VRDZJ12Q805HTX1QYE.pdf) and [regulatory update](https://cosumaf.org/files/documents/01KTTX112ZGHEVHXG16TTS0VN2.pdf), accessed 2026-08-21.
