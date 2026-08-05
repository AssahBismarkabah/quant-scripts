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
| **arXiv q-fin** (ST/TR/GN/RM/MF/CP/PM) | **Open API (free, machine-accessible)** — verified working | **Primary automated harvest.** Clean, dated, structured (title/abstract/date/URL). Fully scriptable. |
| **SSRN** (`papers.ssrn.com`) | No public API; blocks scripted fetch (403) | **Automated via OpenAlex** (indexes SSRN Electronic Journal, source `S4210172589`) + **manual/curated layer** with a real browser. |
| **Crossref** (`api.crossref.org`) | **Open API (free); 429 rate-limits -> retry with backoff** — verified working | **Automated harvest.** Bibliographic metadata for journals (title/DOI/container/date). |
| **OpenAlex** (`api.openalex.org`) | **Open API (free, no key)** — verified working | **Automated SSRN/journals coverage** via the `locations.source.id` filter. |
| **Google Scholar** (`scholar.google.com`) | No public API; blocks bots (429) | **Manual/curated layer.** Browser-session only. |
| **ResearchGate** | No public API; blocks bots (403) | **Manual/curated layer.** Browser-session only. |
| **Semantic Scholar** (`api.semanticscholar.org`) | Hard 429 without an API key; no obvious key-provisioning page for the free tier | **DROPPED.** OpenAlex + Crossref already cover indexed SSRN/journal content; the marginal value did not justify a key dependency none of us can find. |

**Honest note on automation:** arXiv exposes a usable API directly, and **OpenAlex + Crossref are the legitimate free, machine-accessible route to SSRN/journal content** (no scraping, no ToS risk). SSRN / Google Scholar / ResearchGate themselves remain browser-first and block `requests`-style scraping (403/429), so we do NOT scrape them directly. The harvest covers **arXiv + Crossref + SSRN-via-OpenAlex** automatically; Scholar/RG stay a **manual scan** pair with the link template below. This gives breadth without violating their access.

**Manual scan link template (recent):**
- SSRN: `https://papers.ssrn.com/sol3/results.cfm?term=<topic>&date=last_12_months`
- Google Scholar (year-filtered): `https://scholar.google.com/scholar?q=<topic>+anomaly&as_ylo=2025`
- ResearchGate: `https://www.researchgate.net/search/publication?q=<topic>`

---

## 3. The harvest + scorecard (auto: arXiv + Crossref + SSRN-via-OpenAlex)

Script: `research/frontier-mining/harvest_frontier.py`. It:
1. Pulls recent q-fin papers from the **arXiv API**, **Crossref**, and **SSRN-via-OpenAlex** (multi-source; Semantic Scholar removed — key-gated, no value over OpenAlex/Crossref).
2. Scores each against the framework's pillars via auditable keyword heuristics:
   - `forced` — mechanism implies a counterparty who MUST trade (rebalance, hedging, dealer, index, buyback, margin/collateral, liquidation, expiry/roll...)
   - `documented` — a measurable mechanic is described (anomaly, return, premium, drift, arbitrage, reversal...)
   - `empirical` — an empirical/findings orientation (predictability, abnormal, event, out-of-sample...)
   - penalized for `method` (pure methods/ML/math — not a tradeable anomaly) and `data_heavy` (needs intraday/secret/proprietary data we can't get)
   - `recent` — within the window.
3. Outputs a ranked CSV/parquet + a printed shortlist of (empirical, non-method, non-data-heavy) candidates.

Run:
```
.venv/bin/python research/frontier-mining/harvest_frontier.py --max-arxiv 200 --openalex-pages 1 --crossref-rows 50
```
(the venv interpreter is required; `pandas`/`requests` are project deps)

---

## 4. Read-out and decision

- The automated harvest is an **early-warning funnel**, not a verdict. Manual SSRN/Scholar/RG scanning complements it.
- For any surfaced candidate, before a full IA spec: does it clear (a) forced counterparty, (b) free/cheap data + enough events, (c) plausibly non-decayed? If yes, it advances to a full research spec + strategy doc (the buyback-timing treatment).
- If the frontier is method-heavy / thin on high-prior anomalies (as arXiv q-fin appears right now), that is a **honest result** — the funnel said "no strong free candidate is freshly available," which informs a deliberate pick-or-stop rather than forcing a weak idea.

---

## 6. Status

- **2026-08-04:** Process defined + scripted. Accessibility confirmed: arXiv = open API (automated primary); SSRN/Scholar/RG = blocked to scripts (manual layer planned). First harvest (arXiv q-fin, ~12 months, 400 papers) run.
- **2026-08-05:** Multi-source harvest (arXiv + Crossref + SSRN-via-OpenAlex) implemented and **verified end-to-end: 350 papers** from the three sources, ranked shortlist produced. Crossref 429 rate-limits handled with retry+backoff. **Semantic Scholar dropped** (hard 429 without an API key; no obvious free-tier key page; OpenAlex/Crossref already cover indexed SSRN/journal content).
- **Verified outputs:** `research/frontier-mining/outputs/frontier_papers.csv` / `.parquet` (350 papers, scored/ranked). Top empirical/non-method/non-data-heavy leads include e.g. Crossref "Anomaly flow and anomaly cancellation"; arXiv "Herding, Momentum, and Reversal in China's A-Share Market"; "A Spectral Generalisation of the Variance Ratio".
- **First-run honest result:** recent machine-accessible frontier is **method-heavy and thin on high-prior, free-data-testable structural anomalies**. A few empirical leads surfaced (e.g. anomaly flow / herding / long-horizon variance-ratio predictability) that are worth a **manual SSRN/Scholar/RG follow-up**, but none is an obvious high-prior free-data win on the machine pass alone.
- Next: (a) pick a surfaced lead and test whether our existing/free data aligns with the mechanism the paper describes (does the paper's predicted signal show up in our data?), then (b) decide advance-to-spec or bin, (c) if nothing clears, deliberately stop/regroup.
