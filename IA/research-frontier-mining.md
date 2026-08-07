# Research Frontier Mining (process)

**Date:** 2026-08-05
**Type:** Process / methodology document (how we discover the NEXT candidate from current academic research, rather than re-testing known/closed buckets)
**Purpose:** Funnel the recent research frontier (last ~6-12 months) into a shortlist of candidates that we can plausibly TEST, applying the market-edge framework's pillars. This replaces "investigate broadly" with "mine the newest evidence for testable mechanics."
**Audience:** self. Informs candidate selection; feeds each candidate's IA research spec + strategy doc.

---

## 1. Why this replaces broad investigation

Every candidate we've tested so far was either an already-published-and-decayed mechanism or a structural flow we measured as too-small / non-persistent. Broad investigation keeps returning to the same weak pool. The frontier-mining approach flips the direction: **start from freshly published academic evidence**, which is:
- less likely to have decayed (our biggest failure mode),
- precisely specified (construction + data + the "why"),
- and gives an explicit funnel from novelty -> testability.

For each paper the funnel surfaces, the gate is unchanged: real forced/mandate counterparty -> data obtainable free/cheap -> enough events -> survives friction. If a fresh paper fails, it bins like the rest — but it starts from new evidence.

---

## 2. The sources (and the accessibility reality)

| Source | Status | How we use it |
|---|---|---|
| **arXiv q-fin** (ST/TR/GN/RM/MF/CP/PM) | **Open API (free)** — category-scoped, clean | **Automated harvest.** No discipline gating needed (q-fin categories). |
| **SSRN** (`papers.ssrn.com`) | No public API; 403-blocks direct/plain-requests; **reached two ways** | (1) **OpenAlex** (indexes SSRN, topic `T10047`) — structured but lagged. (2) **ZenRows** (`ZENROW_API_KEY`) reads **SSRN's own search** (`searchresults.cfm?term=`) with real **Posted dates** — exhaustive + up-to-date. |
| **Crossref** (`api.crossref.org`) | **Open API (free); 429 rate-limits -> retry+backoff** | **Automated harvest**, gated to a finance-journal allowlist (~40 journals) because Crossref has no finance scope. |
| **OpenAlex** (`api.openalex.org`) | **Open API (free, no key)** — occasionally flaky (504/timeouts) | **Automated SSRN/journals coverage**, finance-gated via `primary_topic.id:T10047`. |
| **Google Scholar** (`scholar.google.com`) | No direct API; blocks bots — **reached via SerpApi** (`SERPA_API_KEY`) | **Automated harvest via SerpApi** (keyed, per-query cost). Gated to finance via title/journal filter. |
| **ZenRows (SSRN)** | **Paid anti-bot scraping API** (`ZENROW_API_KEY`); `js_render`+`premium_proxy`=50 credits/call | **Automated SSRN search** — reads SSRN's own results + Posted dates. Finance-gated via title regex. **Exhaustive/up-to-date SSRN.** |
| **ResearchGate** | No machine API; blocks bots (403) | **Manual/curated layer.** Browser-session only. The ONLY remaining manual source. |
| **Semantic Scholar** (`api.semanticscholar.org`) | Hard 429 without an API key; no obvious key-provisioning page | **DROPPED.** No marginal value over OpenAlex/Crossref/Scholar/ZenRows. |

**Honest note on automation:** arXiv exposes a usable API directly. **OpenAlex + Crossref** are the legitimate free route to SSRN/journal content; **SerpApi** automates Google Scholar; **ZenRows** reads SSRN's own search results yourself (with real Posted dates). SSRN's own pages 403 plain requests, so the ZenRows anti-bot route is what fully automates SSRN. Only **ResearchGate** remains browser-only (no machine API of any kind).

Finance discipline gates (native queries have no finance scope, so we gate):
- OpenAlex -> `primary_topic.id:T10047` (Financial Markets and Investment Strategies)
- Crossref -> finance-journal allowlist [~40 names]
- Scholar -> finance title/journal regex filter
- ZenRows-SSRN -> finance title regex (`SSRN_FINANCE`; avoids gas-liquid/tire/lava false positives)
(Only arXiv is intrinsically finance-scoped via its q-fin categories.)

**Manual scan link template (recent)** — for the one remaining manual layer and ad-hoc deep-dives:
- SSRN: `https://papers.ssrn.com/sol3/results.cfm?term=<topic>&date=last_12_months`
- Google Scholar (year-filtered): `https://scholar.google.com/scholar?q=<topic>+anomaly&as_ylo=2025`
- ResearchGate: `https://www.researchgate.net/search/publication?q=<topic>`

---

## 3. The harvest + scorecard (auto: arXiv + Crossref + SSRN-OpenAlex + Scholar-SerpApi + SSRN-ZenRows)

Script: `research/frontier-mining/harvest_frontier.py`. It:
1. Pulls recent q-fin/finance papers from the **arXiv API**, **Crossref**, **SSRN-via-OpenAlex**, **Google Scholar via SerpApi**, and **SSRN via ZenRows** (each finance-gated as described in section 2). Keys read from the repo `.env` (`SERPA_API_KEY`, `ZENROW_API_KEY`).
2. Scores each against the framework's pillars via auditable keyword heuristics:
   - `forced` — mechanism implies a counterparty who MUST trade (rebalance, hedging, dealer, index, buyback, margin/collateral, liquidation, expiry/roll...)
   - `documented` — a measurable mechanic is described (anomaly, return, premium, drift, arbitrage, reversal...)
   - `empirical` — an empirical/findings orientation (predictability, abnormal, event, out-of-sample...)
   - penalized for `method` (pure methods/ML/math — not a tradeable anomaly) and `data_heavy` (needs intraday/secret/proprietary data we can't get)
   - `recent` — within the window.
3. Tags true SSRN rows (`is_ssrn`), outputs a ranked CSV/parquet + a printed shortlist of (empirical, non-method, non-data-heavy) candidates.

Run (full; OpenAlex/Crossref can be flaky/rate-limited — the script retries with backoff; ZenRows consumes credits):
```
.venv/bin/python research/frontier-mining/harvest_frontier.py --max-arxiv 200 --openalex-pages 1 --crossref-rows 50 --scholar-results 30 --zenrows-results 100
```
To skip the credit-consuming ZenRows source, use `--sources arxiv,openalex,crossref,scholar`.
(the venv interpreter is required; `pandas`/`requests` are project deps; Scholar requires `SERPA_API_KEY` in `.env` — already set)

---

## 4. Read-out and decision

- The automated harvest is an **early-warning funnel**, not a verdict. Manual SSRN/Scholar/RG scanning complements it.
- For any surfaced candidate, before a full IA spec: does it clear (a) forced counterparty, (b) free/cheap data + enough events, (c) plausibly non-decayed? If yes, it advances to a full research spec + strategy doc (the buyback-timing treatment).
- If the frontier is method-heavy / thin on high-prior anomalies (as arXiv q-fin appears right now), that is a **honest result** — the funnel said "no strong free candidate is freshly available," which informs a deliberate pick-or-stop rather than forcing a weak idea.

---

## 6. Status

- **2026-08-04:** Process defined + scripted. Accessibility confirmed: arXiv = open API (automated primary); SSRN/Scholar/RG = blocked to scripts (manual layer planned). First harvest (arXiv q-fin, ~12 months, 400 papers) run.
- **2026-08-05:** Multi-source harvest (arXiv + Crossref + SSRN-via-OpenAlex) implemented and **verified end-to-end: 350 papers**. Crossref 429 handled with retry+backoff. **Semantic Scholar dropped** (no key value).
- **2026-08-05b (pipeline correctness fix):** Diagnosed that OpenAlex-SSRN and Crossref had **no finance discipline gate** — they surfaced multidisciplinary noise (concrete, genetics, menopause, ocean, etc.). Fixed by gating OpenAlex to finance topic `T10047` and Crossref to a ~40-journal finance allowlist; also fixed an OpenAlex bug that had been returning the *title* as the abstract. Re-run: noise gone, output finance-only.
- **2026-08-05c (Google Scholar added):** User provisioned a **SerpApi** key (`SERPA_API_KEY` in `.env`). Added `fetch_scholar_serpapi` — automated **Google Scholar** coverage, finance-gated via title/journal filter. Verified: returns high-quality papers other sources miss (e.g. "Business-Cycle Risk Exposure and the Cross-Sectional Returns in China's A-Share" — Emerging Markets Finance and Trade; "Market Structure and the Erosion of Informed Trade" — Journal of Portfolio Management; SSRN working papers). ResearchGate remains the only manual-only source.
- **2026-08-05d (SSRN coverage gap found + fixed):** The OpenAlex SSRN branch was under-covering recent output — OpenAlex indexes only ~25 finance-topic SSRN articles in the last 12 months (a lagging, partial subset of SSRN's real volume). Added **SSRN-scoped SerpApi Scholar queries** (`site:papers.ssrn.com ...`) so recent SSRN finance papers OpenAlex misses are recovered **via the licensed API (no SSRN scraping)**. Verified: now surfaces fresh SSRN papers e.g. "Passive Flows, Index Rebalancing, and Price Impact" (SSRN 5703304), "Explaining Anomalies" (Hollstein, Kowalke), "What Drives Anomaly Premia around the World?".
  - A direct SSRN scraper (`research/frontier-mining/scraper.py`, mass-scrape by abstract_id) exists in the repo but is **NOT run/recommended**: it is ToS-violating, unfiltered by discipline, and 403-flaky. SerpApi-SSRN does the same job legally.
- **2026-08-05e (SSRN gate):** Added a definitive **`is_ssrn`** detection (URL `papers.ssrn.com/sol3/papers.cfm?abstract_id=` OR DOI `10.2139/ssrn`) so true SSRN working papers are cleanly separated from published/publisher-paper versions that OpenAlex mis-tags as SSRN.
- **2026-08-05f (SSRN complete — ZenRows):** User provisioned a **ZenRows** key (`ZENROW_API_KEY` in `.env`). Added `fetch_ssrn_zenrows` which reads **SSRN's own search UI** (`searchresults.cfm?term=<finance query>`) via ZenRows (`js_render` + `premium_proxy`, 50x credits/call), parsing titles, abstract_id URLs and real **Posted dates**. This closes even the last **exhaustive/up-to-date SSRN** gap (SSRN has no API and 403-blocks direct/plain-requests; ZenRows is the anti-bot route). Finance-gated via a tight `SSRN_FINANCE` title regex (avoids gas-liquid/tire/lava/convection false positives). `ssrn(zenrows)` is now a 5th automated source; **no manual SSRN browse needed** for mining.
- **Cost note:** ZenRows `js_render`(5x)+`premium_proxy`(10x)=**50 credits/call**; reads ~20-50 SSRN papers per finance query. A full multi-query run is a handful of calls — small on a 5000-credit plan.
- **Upstream reliability note:** OpenAlex and Crossref are free APIs that intermittently 504/429 and time out; the script retries with backoff and connection-error handling. When they are flaky, arXiv + Scholar + SSRN(zenrows) carry the harvest.
- **Sources now (5 automated, all finance-gated):** arXiv q-fin (open API) · Crossref (finance-journal allowlist) · SSRN-via-OpenAlex (topic T10047) · Google Scholar via SerpApi (title/journal filter) · **SSRN via ZenRows (SSRN's own search + Posted dates)**. **ResearchGate is the only remaining manual-only source** (no machine API of any kind).
- **Verified outputs:** `research/frontier-mining/outputs/frontier_papers.csv` / `.parquet` (scored/ranked).
- **First-run honest result:** recent machine-accessible frontier is **method-heavy and thin on high-prior, free-data-testable structural anomalies**; the funnel's job is to surface the few fresh, testable theses from the noise (e.g. "AI and Exchange Rate Predictability" Sharpe>0.7; JFE "Index rebalancing ... Do indexes time the market?").
- Next: (a) pick a surfaced thesis, (b) assess whether it makes sense + is testable with free data, (c) decide advance-to-spec or bin, (d) if nothing clears, deliberately stop/regroup.
- **2026-08-07 (triage — HK passive-flow candidate CLOSED):** First candidate pulled from the CSV: Xu, "Passive Flows, Index Rebalancing, and Price Impact: Evidence from a Quasi-Experiment in Hong Kong" (SSRN 5703304, score 9.0). Note: surfaced twice in the CSV (once via `ssrn(zenrows)` with real posted date 2025-11-10, once via `scholar(serpapi)`) — a dedup wrinkle to watch. Full-text review: genuine, well-identified effect (Hang Seng weight-cap quarterly rebalancing; IV elasticity of demand ≈ -0.25, more inelastic than US mega-caps; -0.6% rebalance-day AR; two clean placebos). **But the paper's own Section 6.2 friction backtest closes it for us:** the long-short trade's annualized Sharpe falls **1.10 (frictionless) → 0.46 (+HK stamp duty 0.13% + broker) → 0.29 (+impact) → 0.28 (+borrow)**. HK stamp duty is charged on both legs, structurally unfavorable vs our single-leg US short-additions line; effect is concentrated in ~4-5 mega-caps (Tencent/Alibaba/HSBC/AIA) with tiny N (32 binding events, ~192 obs), plus capacity capped by ~$36B USD HSI-linked AUM. We cannot beat the paper's friction assumptions, so the line is **closed as not viable post-friction** — no new HK data/event-study line opened. Recorded here so it is not re-surfaced repeatedly.
- Next: (a) move down the 9.0/8.0 candidates (e.g. JBF 2025 "The stock market impact of volatility hedging: ... VIX ETPs", JRFM "Deep Hedging Under Market Frictions", "AI and Exchange Rate Predictability" Sharpe>0.7), (b) assess each on forced-counterparty / free-data / non-decayed before advance-to-spec or bin.
- **Dedup wrinkle found (pipeline note):** the CSV can carry the same paper twice across sources with different scores — "Passive Flows" (SSRN 5703304) appears via both `ssrn(zenrows)` (9.0) and `scholar(serpapi)` (8.0); the JBF 2025 VIX-ETP paper appears as two identical `crossref` rows. A post-harvest dedup on normalized title (or URL/abstract_id) would collapse these before ranking. Not yet implemented.

