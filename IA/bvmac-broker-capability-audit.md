# BVMAC Broker Capability Audit

**Date:** 2026-08-21  
**Scope:** Cameroon-relevant BVMAC broker access; active trading only  
**Relation to:** [BVMAC/CEMAC Retail-Scale Trading Feasibility](bvmac-cemac-feasibility.md)

## Decision

**No broker found in the published evidence moves BVMAC into a different active-trading class.**

The brokers are not identical. They differ in account opening, order submission, research, custody, published fees, and access to public offerings. Those differences can matter for a long-horizon investor. They do **not** change the features that make an independent active trading business infeasible: one BVMAC exchange-level venue for ordinary listed-security trading, a daily cash fixing, scarce actual transactions, a tiny equity universe, no demonstrated client-facing API/fill dataset, and no identified economic mechanism.

The correct conclusion is therefore:

```text
Do not open or fund multiple accounts to search for a hidden trading venue.
→ Verify only the four brokers with documented 2024 market activity.
→ Re-open the active-trading question only if written operational evidence clears every gate.
```

This is an audit of what is documented publicly. It does **not** claim that an unadvertised service is impossible; it treats it as **unknown**, not as an advantage.

## 1. What a broker can and cannot change

The published BVMAC rules make a Société de Bourse mandatory for trading listed instruments. Under those published rules, listed-security negotiations must be executed on BVMAC through a broker; trades are cash-only, and the process is a fixing. The official schedule presently shows pre-opening from 09:00 to 11:00 GMT+1 and one fixing at 11:00. The rulebook can change, so current operational terms must be confirmed with the broker and COSUMAF before any account decision. [BVMAC general rules](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf) · [trading schedule](https://www.bvm-ac.org/horaires-seances-de-cotation/)

| Capability | Can a broker change it? | Audit result |
|---|---|---|
| Client onboarding, custody, research, reporting, order transmission | Yes | Meaningful service differences exist. |
| Broker commission and administrative fees | Sometimes | Published tariffs differ, but no published **all-in** active-trading cost clears the gate. |
| Ordinary BVMAC matching conditions and public execution capacity | No | A broker cannot change the exchange-level fixing or create a reliable retail counterparty pool. It may arrange a permitted special transaction, but no such recurring retail route is documented. |
| Daily fixing / cash-only market structure | No | This is exchange/rulebook-level, not broker-level. |
| Number of listed shares or amount of real secondary-market flow | No | A broker can seek a counterparty; it cannot create reliable public capacity. |
| A client API, time-stamped fill export, or historical full order book | Possibly | None was documented in the reviewed first-party material. |
| A causal trading mechanism | No | A broker platform is plumbing, not an edge. |

The BVMAC describes its PAM module as the trading module made available to **Sociétés de Bourse**, which use it to enter their own and clients’ orders. A broker connecting its internal system to PAM is therefore not evidence that a retail customer receives an API or direct market access. [BVMAC description of PAM](https://www.bvm-ac.org/actualite/renforcement-de-capacites-de-lequipe-bvmac-pour-une-gestion-optimale-de-la-plateforme-de-cotation/)

## 2. Broker universe and why the shortlist is not random

At 31 December 2024, BVMAC listed 25 licensed broker firms, 19 headquartered in Cameroon. Its report says only about twelve actually performed transactions during 2024; it specifically identifies Afriland as handling the most equity transactions, Financia as active in bond placement/secondary trading, SG Capital as facilitating institutional exchanges, and CBC as gaining equity-brokerage share. [BVMAC 2024 annual report, pp. 36 and 44](https://www.bvm-ac.org/wp-content/uploads/2025/10/RA-2024_compressed.pdf) · [current broker roster](https://www.bvm-ac.org/societes-de-bourse-par-pays/)

This does not prove that the other firms cannot serve a client today. It does mean a retail researcher should not spend money opening accounts at every licensed name. The four documented-active firms are the appropriate first verification set:

1. **Afriland Bourse & Investissement** — equity activity and a public retail order-submission page.
2. **Financia Capital** — documented bond-market presence and a public subscription/account portal.
3. **SG Capital Securities Central Africa** — documented regional order-centralisation claim and public tariff.
4. **CBC Bourse** — documented 2024 equity-brokerage activity.

### 2.1 Different access classes are not different active-trading classes

There are CEMAC financial products and institutions that are genuinely different from an ordinary BVMAC brokerage account. They should not be collapsed into “all brokers are identical.” But none is a documented bypass around the market-capacity and edge requirements.

| Access class | What it is | Does it change the active-trading answer? |
|---|---|---|
| **Société de Bourse** | The regulated intermediary for orders in BVMAC-listed securities; this is the class audited in this document. | **No.** It changes service, cost, and workflow, not the exchange-level fixing or secondary-market capacity. |
| **Portfolio manager / OPCVM fund** | A separate licensed manager pools or manages investor capital. BVMAC’s 2024 report lists 15 portfolio-management firms and 36 approved collective funds. | **No.** This delegates or packages investment exposure; it is not a retail-owned active-trading execution advantage. |
| **BEAC public-securities route through an SVT** | Treasury bills/bonds are issued through approved Spécialistes en Valeurs du Trésor; individuals and legal entities may be investors, subject to the SVT’s terms. | **Different product, not an active-alpha route.** It may be worth separate fixed-income/investment research, not a substitute for a tradable secondary-market edge. |
| **Primary public offer / placement syndicate** | A broker collects subscriptions for a new issue or IPO. | **Different event, not a recurring trading venue.** A one-off allocation needs its own economics and cannot be assumed to generate a repeatable edge. |
| **Issuer liquidity contract** | An issuer hires a broker and supplies cash/securities so it can support a particular listing under BVMAC rules. | **No public retail access.** It is an issuer–broker mandate, not a trading account feature. |
| **Transaction sur dossier** | A broker files a pre-agreed eligible transfer for BVMAC approval. | **No.** It is a special approved transfer, not a venue for repeatedly trading signals. |

Sources: [BVMAC 2024 annual report](https://www.bvm-ac.org/wp-content/uploads/2025/10/RA-2024_compressed.pdf) · [BEAC public-securities market](https://www.beac.int/m-des-titres-publics/presentation-generale/) · [BVMAC general rules](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf).

## 3. Published broker differences

| Firm | What a first-party source actually documents | What it changes | Active-trading verdict |
|---|---|---|---|
| **Afriland Bourse & Investissement** | Individuals and institutions can deposit BVMAC/SVT orders electronically or physically. Its September 2025 public tariff lists 0.50% brokerage per transaction and FCFA 2,500 for order processing; it does not establish an all-in, tax-inclusive round-trip cost. BVMAC says it handled the most equity transactions in 2024. [client page](https://www.afrilandbourse.com/Espaceclient.php) · [tariff](https://www.afrilandbourse.com/assets/GRILLE%20TARIFAIRE%20AFRILAND%20BOURSE%20SEPTEMBRE%202025.pdf) | Better documented retail workflow and likely the strongest first broker to inspect. Electronic order deposit is not a client API, direct market access, or a different venue. | **Does not reopen.** Verify its complete cost and fill-data terms first. |
| **SG Capital Securities Central Africa** | It says a regional platform centralises and executes client orders “in real time.” Its public tariff effective 1 April 2025 shows visible BVMAC, depository-movement, and brokerage components totalling about 1.0155% per side (about 2.03% round trip) before spread, impact, custody, or other charges. [broker page](https://particuliers.societegenerale.cm/fr/banque-quotidien/une-expertise-marches-financiers/societe-generale-capital-securities-central-africa/) · [tariff](https://particuliers.societegenerale.cm/fileadmin/user_upload/Cameroun/PDF/2025/T2_-_2025/Tarification_operations_marche_financier_V_mai_2025_-_tarifaire_entreprises.pdf) | Demonstrates regional broker operations, not that BVMAC continuously matches client orders or that a client has an API. | **Does not reopen.** The published visible cost baseline is hostile to active turnover. |
| **Financia Capital** | Its public subscriber site describes a cash-and-securities account that must be fully funded before an order, and 0.10% annual custody. BVMAC identifies it as present in bond placement and the bond secondary market. [terms](https://www.financiacapital-subscribers.com/conditions-generales) | Shows an online subscription/account workflow and fully funded settlement discipline. It does not publish an active secondary-trading API, client order-book feed, or secondary commission schedule. | **Does not reopen.** It is a useful verification target for bonds and primary offers, not an evidenced active-alpha route. |
| **CBC Bourse** | BVMAC identifies CBC as having gained equity-brokerage share in 2024. [annual report](https://www.bvm-ac.org/wp-content/uploads/2025/10/RA-2024_compressed.pdf) | Gives a reason to ask about real client order flow, cost, and reporting. No public client platform/API/tariff was found in this audit. | **Unknown operational details; no reopen.** |
| **FedhEn Capital** | It publishes research, licensed securities brokerage, custody, portfolio management, and participation in public offerings. [services](https://fedhencapital.com/expertise?view=analyse-et-recherche) | This is a full-service broker offering, but the published material does not establish a retail API, direct market access, or a different execution venue. | **Does not reopen.** |
| **Elite Capital Securities Central Africa** | It publishes a retail securities-account process, states a FCFA 300,000 initial deposit, and provides displayed BVMAC data. [retail account page](https://elite-capitalgroup.com/exca/particuliers/) | Makes retail access legible. It does not publish exact fees, client API, or historical fill data. | **Does not reopen.** |
| **Beko Capital Advisory** | It says it brokers securities on BVMAC and the CEMAC monetary market, and handles primary placements. [brokerage page](https://bekocapital.com/brokerage-and-placement/) | This is the clearest published indication of a product outside BVMAC-listed secondary trading. It does not prove retail terms, continuous secondary liquidity, or an edge. | **Separate investment-access question; not an active-trading exception.** |
| **Africa Bright Securities** | Its public guide shows a signed order, pre-funded cash provision, and an after-the-fact trade notice/relevé. [guide](https://africabright.com/wp-content/uploads/2026/05/Guide-dintroduction-au-marche-financier.pdf) | Documents the conventional broker-mediated, fully funded workflow. | **Confirms the same class.** |
| **ESS Bourse** | It publishes current market data plus brokerage, custody, and advisory descriptions. Its “best market technologies” statement supplies no client API, tariff, or actual fill evidence. [ESS Bourse](https://emraldsecuritiesservices.com/page/ess-bourse) | Research/data presentation may help an investor monitor the market. | **Does not reopen.** |
| **CCA Bourse** | It describes intermediation, custody, and settlement via the DCU and a linked cash account. [services](https://cca-bourse.com/index.php/services/) | Confirms normal broker/custody mechanics. | **Does not reopen.** |
| **BEM Securities** | It presents an integrated advisory, brokerage, and securities-account offering. [site](https://www.bemsecurities.com/) | Generic service offering; no client trading interface, tariff, or raw fill-data evidence published. | **Does not reopen.** |
| **Almasi Capital & Advisory** | It presents negotiation, custody, and financial-advisory services. [site](https://www.almasicapital.com/) | Generic broker services; no material active-trading difference is documented. | **Does not reopen.** |
| **AFG Capital, ASCA, Contacturer, DigiCapital, EDC, Horus, USCA** | They appear on BVMAC’s licensed roster. The reviewed first-party material did not document a retail API, complete current tariff, time-stamped fill export, or alternative matching venue. | This is an evidence gap, not a claim that these firms have no such service. | **No evidence-based reason to open first.** |

The non-Cameroon firms on the 2024 BVMAC roster — BGFI Bourse, LCB Capital, CBT Bourse, L’Archer Capital Securities, Bange Sociedad de Valores, and Premium Capital Securities — are not a loophole. The same BVMAC market-level constraints apply, while Cameroon-resident onboarding, cross-border custody, tax, currency handling, and complete tariffs remain unverified. No reviewed first-party source documents a capability that clears the active-trading gates.

## 4. Things that look like exceptions but are not

### 4.1 A platform is not direct market access

Afriland’s electronic order submission, SG Capital’s regional platform, and FedhEn’s published research/brokerage workflow could make administration or investment research easier. None of the published sources establishes that a retail customer can:

- submit machine-generated orders through an API;
- see a complete historical order book or queue position;
- download time-stamped individual fill data;
- trade a continuous BVMAC order book; or
- receive execution priority over other public orders.

These are customer-service improvements, not an informational or execution moat.

### 4.2 Primary offers and the CEMAC monetary market are a different product

Some brokers mention primary placement, SVT intermediation, or the CEMAC monetary market. BEAC describes the public-treasury market as involving approved Spécialistes en Valeurs du Trésor and individual or corporate investors. That may be worth evaluating later as a conservative fixed-income or investment-access route. It is not a demonstrated active trading edge and is outside the BVMAC-secondary-market question. [BEAC public-securities market](https://www.beac.int/m-des-titres-publics/presentation-generale/)

### 4.3 A liquidity contract is not a retail market-making privilege

BVMAC requires certain issuers to appoint a broker under a liquidity contract. The broker is supplied with an issuer-funded cash and security envelope and must intervene at weekly frequency when no ordinary market exchange occurs. That is an issuer–broker arrangement intended to prevent complete inactivity; it is not a public customer right, a guarantee of size/price, or permission for us to market-make. [BVMAC liquidity-contract notice](https://www.bvm-ac.org/echos-du-marche/avis-n002-2022-bvmac-dg-relatif-aux-modalites-dapplication-du-contrat-de-liquidite-vise-par-lavis-n001-2022-bvmac-dg/)

### 4.4 A transaction sur dossier is not a private retail trading venue

The BVMAC rulebook permits a **transaction sur dossier** when the trade is pre-agreed and fits specified cases: merger/acquisition/restructuring, an eligible family transfer, a portage retrocession, or another operation approved by BVMAC. It must be introduced through a broker and approved by BVMAC. That is not a general method for a retail trader to discover counterparties and repeatedly trade a signal. [BVMAC general rules, Articles 46-51](https://www.bvm-ac.org/wp-content/uploads/2019/11/Reglement-BVMAC.pdf)

This distinction matters because BVMAC reported that one such pre-agreed transaction represented FCFA 13.28 billion, or 79% of the 2024 bond-market value traded. Large aggregate bond turnover therefore does not imply repeatable public retail capacity. [BVMAC 2024 annual report, p. 35](https://www.bvm-ac.org/wp-content/uploads/2025/10/RA-2024_compressed.pdf)

## 5. Gate-by-gate result

| Required to reopen active research | Public result after broker audit |
|---|---|
| A materially lower, complete all-in cost model | **Fail / unknown.** One current public broker schedule has about 2.03% visible round trip before spread/impact; another shows 0.50% brokerage each side plus per-order cost, without all-in disclosure. |
| A retail execution channel that is more than email/phone/portal order intake | **Not demonstrated.** |
| A client API or reproducible time-stamped fill/order dataset | **Not demonstrated.** |
| A different matching venue or reliable private counterparty pool | **Not demonstrated.** A special transaction may be arranged when BVMAC rules permit it, but that is not a recurring retail trading venue. |
| Enough executable capacity | **Fail.** Broker selection cannot change the documented exchange transaction scarcity. |
| A durable causal mechanism | **Fail.** No broker feature supplies one. |

**Overall broker-audit result: the firms differ in service layer, but remain in the same active-trading class.**

## 6. The only sensible next verification

Do **not** open an account yet. Send a written request for information to the four documented-active brokers: Afriland, Financia, SG Capital, and CBC. A call, sales pitch, or marketing brochure is not a pass. Ask each to answer in writing and attach the current governing documents.

1. Are you accepting Cameroon-resident individual accounts for BVMAC secondary-market trading today?
2. Provide the full tariff, including broker commission, BVMAC/DCU charges, VAT, custody, account, transfer, minimum-order, cancellation, settlement, and any fixed per-order fees.
3. Which exact client order channels are available: branch, signed email, phone, web portal, mobile app, FIX/API? Which are executable rather than informational?
4. Can an individual export all submitted orders, acknowledgements, cancellations, and fills with millisecond/second timestamps, order IDs, price, quantity, and fees? Provide a redacted sample.
5. Is there a client view or export of the full historical order book, or only the official daily bulletin?
6. What order types, validity periods, cancel/replace mechanics, and cutoff times apply to the daily fixing?
7. Provide a redacted recent execution report and client statement that distinguishes submitted, unfilled, partially filled, and filled orders.
8. What were the actual transaction counts and values by BVMAC instrument for the preceding 12 months that you can legally disclose? Displayed orders are not a substitute.
9. Are any securities-lending, margin, short-sale, repo, or financing features available to an individual? Cite the rule and terms.
10. Which BVMAC issuer liquidity/animation contracts do you currently manage, and how are conflicts handled for ordinary clients?
11. Can a customer access BEAC/SVT public securities through you? If yes, provide product terms separately from BVMAC listed-security terms.
12. Can an ordinary retail customer ever use a BVMAC transaction sur dossier or a broker-to-broker negotiated process? If so, provide the legal eligibility, approval process, minimum size, fees, actual 12-month count, and a redacted settlement record.

### Re-open rule

Only reopen research if written evidence establishes **all** of the following:

1. a legal, customer-level execution/data capability that materially improves measurement or implementation;
2. a complete cost model compatible with a named causal mechanism;
3. enough actual, independently observable transactions to model entry and exit; and
4. a defined legal public-information or forced-flow hypothesis before any backtest.

Even an excellent customer portal, a lower fee, or a broker’s research report alone is insufficient. It cannot repair the liquidity, breadth, and mechanism failures already documented in the main feasibility memo.

## 7. Source and method record

- **Primary source standard:** BVMAC, BEAC/COSUMAF, and each broker’s own published site or tariff. User-uploaded documents and third-party summaries were not used to establish a capability.
- **Licensing/status caution:** the BVMAC 2024 annual report and its public roster establish the audit universe, not a guarantee that each firm’s exact 2026 retail terms are unchanged. Confirm current status directly with COSUMAF and the selected broker.
- **Absence language:** “not demonstrated” means no reviewed primary source showed it. It does not mean the capability is impossible; the written RFI is the next test.
- **No contact or account activity:** no broker was contacted, no account was opened, and no order was sent for this audit.
