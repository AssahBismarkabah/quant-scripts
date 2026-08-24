# Earnings-Anchored VWAP Daily Proxy — Research Gate and Proposed Test

- **Date:** 2026-08-22
- **Status:** **PHASE 0 GATE FAILED (2026-08-24, second correction) — 96/100 verified, agreement 0.9375 below frozen bar on both count and agreement; DAILY PROBE BLOCKED**
- **Parent audit:** [VWAP Book Source Audit](vwap-book-source-audit.md)
- **Related closed family:** [PEAD](../strategies/pead/PEAD.md)
**Decision:** A bounded *daily historical falsification* is technically possible on owned data. It is **not** an intraday test and cannot, even if it passes, justify live capital deployment in 2026. **The Phase 0 release-timing audit failed on the free SEC EDGAR path (2026-08-24, second correction: 96 verified / 100, agreement 0.9375)**, so the probe is blocked before any outcome run regardless of design approval. The free path (Yahoo, then EDGAR, then three harness-bug fixes) is now spent; the only remaining unblocking path is a paid point-in-time earnings-time source such as Benzinga (explicit timestamp field, history from 2012); see §4 and §10. No purchase is justified by this result — a paid pass still would not authorize deployment because owned data ends 2021.

## 1. Question being tested

The book’s only potentially distinct idea is:

> After a material earnings release, anchor VWAP at the release and trade the first pullback that holds in the direction of the repricing.

The source does not define “material,” a pullback, a confirmation, a stop, or an exit. The design below is therefore **not claimed to be the book’s exact strategy**. It is a single, researcher-authored, source-inspired daily proxy. Its only purpose is to falsify one clear version without tuning.

The hypothesis is deliberately narrow:

```text
A material, directionally consistent earnings shock establishes a post-event
volume-weighted reference price. The first daily pullback that touches that
reference and closes back through it has better subsequent economics than an
unweighted reference or simple earnings-gap continuation.
```

If it cannot beat those controls after cost, then there is no evidence that the *VWAP* part adds anything beyond a generic earnings/gap story.

## 2. Why this is separate from, but cannot evade, PEAD

The closed PEAD probe ranked surprise stocks cross-sectionally and held them 60 trading days. This proposal instead uses an event-specific reference price, waits for a pullback, and has a fixed short holding/risk process. Those are mechanically different questions.

They are still adjacent. PEAD already failed OOS in the owned panel, so this candidate has a high prior burden:

- It must beat a same-event, directional earnings-gap hold baseline.
- It must beat the same rule using an **unweighted** anchored mean instead of AVWAP.
- Long and short results must be reported separately; unavailable short-borrow data means a short-side result cannot become a deployable claim.

Failure of any of those conditions means this is only PEAD/gap exposure with a visual overlay, not a new edge.

## 3. What the data can and cannot support

### 3.1 Owned daily data: enough for a historical proxy

`research/pead/cache/earnings_latest.csv` provides date, actual EPS, estimated EPS, and a `pre`/`post` release label. `stock_prices_latest.csv` provides raw daily OHLCV. A structural census on 2026-08-22 found:

| Measure | Result |
|---|---:|
| Earnings events with actual, estimate, and `pre`/`post` label, 2012-07-16 to 2021-06-14 | 80,446 |
| Symbols | 4,599 |
| Events with a designated anchor session, 20 prior sessions, and 25 following sessions | 79,068 |
| Price coverage | Daily bars only; most usable history ends in June 2021 |

This is enough observations for a **daily** OOS falsification if the data-integrity gate passes. It is not enough to claim a current 2026 edge.

### 3.2 What it cannot test

The book also presents 5–30 minute trading. The owned panel has neither minute bars nor actual release timestamps. It cannot establish:

- whether a release occurred at 08:00, 16:00, or during the regular session;
- extended-hours fills, spreads, and price discovery;
- intraday anchored VWAP or a footprint/order-flow confirmation; or
- a post-2021 OOS result.

This matters. Research using high-frequency after-hours data finds that most earnings are released outside regular hours and that the market reaction is highly sensitive to timing, liquidity, and spreads. More recent evidence reports post-announcement strategies consistent with efficient price formation after 2016. The daily proxy should therefore be treated as a harsh falsification exercise, not an expected source of alpha.

## 4. Data and capability gates before any code runs

All gates below must pass. A fail is a result, not a reason to relax a rule.

| Gate | Requirement | Verdict if it fails |
|---|---|---|
| Timing-label audit | Randomly verify at least 100 events, stratified by year and `pre`/`post`, against issuer releases or an independent earnings-time vendor. At least 95% must agree on date and pre/post session. | **UNVERIFIABLE**; do not run. |
| Event-price integrity | Event, prior 20 sessions, and maximum holding window have valid positive raw OHLCV; no split coefficient other than 1 within the trade window. | Drop affected event; fail if <90% of candidate events remain. |
| OOS sample | At least 300 valid long trades and 300 valid short diagnostics after all frozen screens. | **UNVERIFIABLE** for that side. |
| Execution model | Apply both base and stress round-trip costs. Do not use adjusted close for intraday-style stop/target arithmetic. | No economic verdict. |
| No parameter search | Exactly one construction below. No threshold, window, exit, or filter sweep. | Probe invalidated. |

The existing `pre`/`post` field is sufficient only after the timing-label audit. SEC EDGAR timestamps are useful for filing history but are not a substitute for the actual earnings-release timestamp: earnings releases can be furnished through an Item 2.02 Form 8-K after the release itself.

### 4.1 Actual state of the timing-label audit (2026-08-22)

The fixed random sample (`research/earnings-anchored-vwap/outputs/timing_audit_template.csv`, exactly 100 rows: 20 year × session strata × 5 rows) was checked against the free Yahoo Finance earnings-calendar archive (`yfinance.Ticker.get_earnings_dates`, the same endpoint the tooling can already reach without a paid account):

| Outcome | Count |
|---|---:|
| Verified: release date and BMO/AMC session both agree | 63 |
| Verified event present, session disagrees | 1 |
| No historical row for the ticker (delisted) | 31 |
| Historical rows exist but the event date is absent | 5 |
| Errors | 0 |

Agreement on the fixed full sample is 63 of 100, below the frozen 95% gate, not because covered rows conflict (98.4% of covered rows agree) but because 36 of 100 fixed rows have **no historical record in the free archive**. The gaps are concentrated in smaller or delisted names (CRAY, DNR, BCEI, PZN, WMGI, QTNT, SRRA, ...) that a year-stratified audit intentionally samples; the free vendor does not retain a complete historical earnings calendar for them.

Consequences, kept separate:

- The gate is legitimately **UNVERIFIABLE on free data**. The missing third is not noise to be discounted: a strategy whose release-timing labels are only as good as `pre`/`post` cannot be tested unless every sampled stratum is independently confirmed.
- Deliberately replacing the delisted rows with surviving names would re-sample the same "survivorship bias makes it partially verifiable" population and is a gate change, not a violation fix. It is not done silently.
- This is a **capability-census result, not a strategy verdict**. It does not say the earnings-anchored daily proxy wins or loses; it says the release-timing precondition of the test cannot be satisfied at the frozen confidence with free data.

**Superseded (2026-08-24, corrected):** the Yahoo-check row above was replaced by a CIK-anchored SEC EDGAR audit (`research/earnings-anchored-vwap/timing_audit.py`, run via `make phase0`). EDGAR covers the delisted stratum Yahoo dropped. A first EDGAR run reported 86 verified / 100 (agreement 0.9535); on inspection that undercounted because **two genuine parser bugs** were mislabeling valid rows:

1. Call-time pattern 1b returned `post` for *any* "H:MM p.m. ... Month Day, Year" without gating the date to the release day/morning, so a quarter-end date ("March 31, 2016") inside the financial narrative produced a false call date.
2. The 8-K "Date of Report (earliest event reported)" line was treated as an absolute release-date check, rejecting filings whose EX-99 press release clearly pinned the release date and session (ARDX: EX-99 "May 9, 2016 ... conference call today at 4:30 p.m. ET" = post, but DOR header read a prior "March 9, 2016" event).

Both were fixed (date-gate added to pattern 1b; DOR mismatch now blocks only when no release-text session signal pins the template date); the corrected audit was **91 verified / 100, agreement 0.956**. A second pass then found and fixed three further harness bugs (see §10 "Update (2026-08-24, second)") for a final **96 verified / 100, agreement 0.9375** (`outputs/phase0_summary.json`, `status: FAIL`). The row count remains below the frozen 100 and the agreement below the frozen 95%; the free-data ceiling is now known precisely, not overstated by parser defects.

**Second correction (2026-08-24):** three further harness bugs were found and fixed in the same CIK-anchored EDGAR audit:

1. `filing_documents()` read only the per-filing directory index, which for many older filings omits the EX-99 press-release exhibit entirely (verified PCMI, HIVE, CRNT, BMO, DY release 8-K, SEIC 10-Q). The free EDGAR full-text index keyed on the accession number (`https://efts.sec.gov/LATEST/search-index?q="<accn>"`, no token needed — the `.json` suffix is the only part that 403s) enumerates every file including exhibits, so the union of both sources now sees them.
2. `_audit_one()` picked only the first matching filing (`exact[0] else candidates[0]`), mis-resolving DY to its 11-27 transcript instead of the 11-26 release 8-K (which carries the same press-release text); it now scans every candidate and ranks them by release-text evidence plus Date-of-Report match.
3. The audit looked only at 8-K Item 2.02 filings. SEIC's Q1-2013 press release exists solely as an exhibit of the 10-Q (no Item 2.02 8-K in the window), so domestic 10-Q/10-K filings in the window are now scanned as fallback candidates too.

Effect: **PCMI and HIVE (previously ambiguous) and DY (previously not_found) now verify and match the template**; **SEIC and BMO (previously not_found / ambiguous) now verify as honest mismatches** (their EX-99 releases state a 2:00 p.m. call = post, template says pre). The audit therefore resolves 96 of 100 rows, with agreement **90/96 = 0.9375** — below the frozen 95% on both required dimensions. See §10 ("Update (2026-08-24, second)") for the full breakdown.

### 4.2 Sample-state: what the fixed 100 rows actually are

The 36 unverifiable rows are not arbitrary: the frozen audit is stratified by
year and `pre`/`post`, and it deliberately samples the small and delisted names
that the free archive drops. Intersecting the 100 fixed rows with the frozen
tradeability screens (`$5` price, `$10M` median dollar volume, integrity
window, at the anchor) gives:

| Verify status | Not tradeable | Tradeable | Total |
|---|---:|---:|---:|
| Match on free archive | 38 | 25 | 63 |
| Mismatch | 0 | 1 | 1 |
| Missing date | 3 | 2 | 5 |
| Missing ticker (delisted) | 21 | 10 | 31 |

Of the 100 sampled events, only 38 survive the frozen screens, and 12 of those
38 are among the 36 rows the free archive cannot verify. Only 25 of 100 are
positively verifiable on free data **and** tradeable. So a free-data redesign
that kept only verifiable rows would silently re-weight the sample toward a
survivor subset; that is a gate change, not a fix, and is not done silently.

This is separate from the full-panel census (see below), which shows the
strategy's *data* is adequate; the blocker is specific to independent
**release-time** verification of the fixed audit sample.

### 4.3 Full-panel census (no outcomes loaded)

`research/earnings-anchored-vwap/census_eligible.py` applies the frozen
pre-signal screens to the whole owned panel and counts candidates by side and
period, plus OOS AVWAP reaction-signal availability. It computes **no**
P&L/outcome; it only counts, so it does not violate the frozen gate.

| Census step | Long | Short |
|---|---:|---:|
| Eligible candidates (full panel, all years) | 7,848 | 3,795 |
| OOS candidates | 3,924 | 1,792 |
| OOS with a first-pullback reaction signal | 3,281 | 1,410 |
| Frozen minimum OOS trades per side | 300 | 300 |

The sample-size gate is **not** the binding constraint: even within the
tradeable, direction-consistent subset, OOS candidate counts far exceed the
minimum. The screen losses are dominated by `liquidity_below_minimum` (31,627),
`direction_or_gap_not_eligible` (26,120), and `price_below_minimum` (8,874)
out of 80,446 source events; 78,264 events clear the raw price-integrity
window. The single binding constraint on free data remains the independent
**release-time** audit of the fixed 100 rows.

Result of the Phase 0 free-source cross-check (`outputs/timing_crosscheck_yahoo.json`):
full-sample agreement 0.63 (frozen gate 0.95); among rows the free archive
covers, agreement 0.9844. The probe therefore remains blocked at the
release-timing precondition. The income-source search (web search, 2026-08-22):

- A **free** archive of historical US earnings release times does **not**
  exist for the full year-stratified universe. Yahoo's historical earnings
  calendar omits delisted small names; nothing else public covers them with
  BMO/AMC labels.
- **Benzinga** earnings calendar is the documented fit (explicit `time` field
  plus actuals/estimates/surprise, history from 2012), but pricing is
  sales-quoted (not published); a per-ticker Pro subscription is the typical
  entry point. No purchase is justified until a validated free-data path is
  exhausted or the user decides the daily falsification is worth the spend.
- **QuantQuote** earnings-release API documents a BMO/AMC/intraday field and
  per-ticker history, but its public plans cover roughly the last 10 years
  (~2016+) — it does **not** cover the frozen 2013–2016 IS years at the
  cheapest tier. Its Jan-2000 Pro plan is still "coming soon."
- **Issuer press releases / newswire archives** are independent but indexed
  names only, and manual per event — not a 100-event census.

Bottom line: the owned panel is sufficient for the daily *data*; the 
independent release-time *verification* of the fixed 100-row audit is what
requires a paid vendor, and only a purchase or an approved redesign of the
audit sample changes this.

## 5. Proposed frozen daily-proxy construction

These values are **design assumptions**, not hidden claims from the book. If approved, they are fixed before loading outcomes. Changing any one creates a different hypothesis.

### 5.1 Eligible event and anchor

1. Event must have non-null `eps`, `eps_est`, and `release_time ∈ {pre, post}`.
2. **Anchor session:**
   - `pre`: the first trading session on or after the stated release date;
   - `post`: the first trading session strictly after the stated release date.
3. Use the raw prior close and raw anchor-session open. Exclude an event unless 20 prior sessions exist.
4. Require price at prior close >= $5 and lagged 20-session median daily dollar volume >= $10 million.
5. Calculate the lagged 20-session ATR from raw OHLC. Let `gap = (anchor_open / prior_close) − 1`.
6. A long candidate requires `eps > eps_est` and `gap >= ATR20 / prior_close`. A short diagnostic requires `eps < eps_est` and `gap <= −ATR20 / prior_close`.

The gap-in-ATR condition is the one fixed definition of “material.” EPS direction and observed gap must agree, so the event is anchored to earnings information rather than a generic chart gap alone.

### 5.2 Daily anchored VWAP proxy

For each session `t` beginning at the anchor:

```text
typical_price_t = (high_t + low_t + close_t) / 3
AVWAP_t = sum(anchor..t, typical_price × volume) / sum(anchor..t, volume)
```

This is a daily OHLCV approximation of trade-level VWAP. It is not a claim about intraday VWAP precision.

### 5.3 Entry, risk, and exit

Search only sessions 1 through 10 after the anchor. Take at most one trade per event and one active trade per symbol.

| Side | First qualifying reaction (known at the session close) | Entry next session open | Initial stop | Target |
|---|---|---|---|---|
| Long | `low ≤ AVWAP ≤ high`, `close > AVWAP`, and `close > open` | Market buy at next daily open | Reaction-session low | Entry + 1R |
| Short diagnostic | `low ≤ AVWAP ≤ high`, `close < AVWAP`, and `close < open` | Market sell at next daily open | Reaction-session high | Entry − 1R |

`R` is entry minus stop for a long, or stop minus entry for a short. Reject a trade if `R <= 0`. Hold for at most 10 sessions after entry. If both stop and target occur within one daily bar, assume the **stop** occurred first. If the opening price gaps past either level, exit at that open. Exit any remaining position at the close of the tenth session.

### 5.4 Costs and reporting

- Base: 20 bps per side (40 bps round trip).
- Stress: 50 bps per side (100 bps round trip).
- Report long and short separately. Do not combine them into a long-short portfolio.
- Use event-date clustered bootstrap, not independent-trade bootstrap, because earnings shocks cluster by calendar day.

## 6. Mandatory controls: prove the AVWAP component earns its place

The core claim is not merely “earnings gaps may continue.” The following controls use the identical eligible event set, side, cost, and maximum holding window:

1. **Earnings-gap hold baseline:** enter in the event direction at the first eligible session open after the anchor and exit after 10 sessions. This asks whether the candidate is only a generic gap-continuation trade.
2. **Unweighted-anchor ablation:** replace AVWAP with the cumulative arithmetic mean of daily typical prices from the anchor. All reaction, entry, and exit rules remain unchanged. This asks whether volume weighting adds anything.

The AVWAP proxy may advance only if its OOS economics and clustered-bootstrap lower bound exceed **both** controls. Incremental comparisons use only the matched event intersection—an event must produce an AVWAP trade and the relevant control trade—to prevent sample-composition differences from being called VWAP value. Each matched OOS comparison also needs at least 300 trades per side. A positive raw AVWAP result alone is not enough.

## 7. Immutable windows and decision gates

The data ends in 2021. The proposed historical split is therefore intentionally old:

- Warm-up: 2012 (ATR history only; no trades).
- IS: 2013-01-01 to 2016-12-31.
- OOS: 2017-01-01 to 2021-06-14, subject to a full post-entry holding window.

The test fails for a side if **any** applicable gate fails:

| Gate | Requirement |
|---|---|
| 1 — OOS economics | Net average trade must be positive under **both** base and stress costs. |
| 2 — uncertainty | 5th-percentile event-date clustered-bootstrap mean net return must be positive under base costs. |
| 3 — basic quality | OOS profit factor >= 1.0 and no more than 40% of losses may be caused by stop-gap exits. |
| 4 — persistence | At least three of the four complete OOS years (2017–2020) must be net-positive under base costs. |
| 5 — incremental value | OOS AVWAP mean net return and its bootstrap lower bound must exceed both mandatory controls. |
| 6 — IS reproduction | IS gross mean return must be positive; an IS failure means the construction does not even reproduce its own premise. |
| 7 — data integrity | Every timing, split, next-open, and no-look-ahead audit must pass. |

**A pass does not authorize deployment.** It would only earn a separate, current-data feasibility stage. Any fail closes this construction permanently.

## 8. Why an intraday version is not authorized now

The real 5–30 minute setup requires a different capability stack:

```text
point-in-time earnings timestamp and surprise
        +
extended-hours / regular-session US equity minute bars and realistic spreads
        +
current OOS history and forward alert capture
        +
an execution model that handles earnings gaps
```

The owned panel has none of the first three at adequate fidelity. IBKR documents that API market data depends on live subscriptions and is subject to historical-data limitations and pacing; it is not an adequate cross-sectional, auditable historical archive for this study. A vendor such as Benzinga documents earnings time, estimates, actuals, and surprise fields, while a venue-grade data vendor can provide historical equity bars/quotes, but acquiring those inputs is a cost-bearing business decision. No data purchase is justified unless the daily falsification clears every gate above.

## 9. Research conclusion and next action

There are two honest paths, and this document deliberately keeps them separate:

1. **Run the bounded daily falsification.** This costs no new data and can decisively reject one mechanical daily interpretation. It cannot prove a current live edge because its OOS ends in 2021.
2. **Do not run it.** The higher-fidelity intraday claim remains capability-gated, and the current evidence gives it a weak prior: PEAD failed in our data, while modern high-frequency studies show very rapid price adjustment.

### 9.1 Free-data falsification (executed 2026-08-24, both variants recorded)

Because the Phase 0 timing audit cannot pass on free data, the bounded daily
falsification was executed on owned data under **two deliberately recorded
free-data allowances** (not a silent gate lift; the frozen gate still blocks
the default path):

- **label mode (run with what we have):** the frozen construction
  (`anchor_mode=label`) run over all eligible events, ignoring the Phase 0
  audit failure. All frozen parameters, controls, and gates unchanged.
- **next_open mode (label-free):** the identical construction but anchoring
  every event at the first session on/after the release date, so the disputed
  pre/post label is never used to time the anchor. This is the least
  assumption that still tests the book's VWAP-anchor pullback idea.

Both runs use the same owned raw daily OHLCV (PEAD cache), the same 20bps/40bps
base and 50bps/100bps stress friction, the same event-clustered bootstrap, and
the same six decision gates. Neither authorizes deployment (all data ends
2021). Results are preserved under `outputs/probe_summary.{label,next_open}.json`
and matching parquet files; the runner writes the latest into
`outputs/probe_summary.json`.

Both variants **fail every OOS gate for both sides** (gates 1-5 all false; IS
gross positive for long only, which is not enough). The VWAP-anchored pullback
reads as worse than a plain earnings-gap hold in OOS, and the volume-weighted
anchor adds nothing over an unweighted anchor (incremental p5 is negative).
Verdict recorded: **DISCONFIRMED** on this bounded daily construction,
independent of the timing-label disagreement.

Key OOS numbers (net mean bps at base cost; OOS is 2017-2021-06):

| Side | label net base | label net stress | label PF | next_open net base | next_open net stress | next_open PF |
|---|---:|---:|---:|---:|---:|---:|
| long | -29.8 | -89.8 | 0.79 | -36.4 | -96.4 | 0.74 |
| short | -45.3 | -105.3 | 0.74 | -29.2 | -89.2 | 0.82 |

No code or backtest is authorized by this document alone. The implementation that exists (engine, controls, metrics, and the Phase 0 gate) lives in the isolated `research/earnings-anchored-vwap/` probe with no outcome loaded. **The implementation is ready only when the Phase 0 release-timing audit passes (§4).** The twice-corrected CIK-anchored EDGAR audit (`research/earnings-anchored-vwap/outputs/timing_audit.csv`) confirms **96 of 100**, agreement **0.9375** among verified rows — the row count still falls short of the frozen 100 and the agreement falls short of the frozen 95%, so `research/earnings-anchored-vwap/outputs/phase0_summary.json` is `status: FAIL`. Running the daily OOS study now would violate the frozen gate.

**Executed 2026-08-24 (free-data allowance, recorded):** the bounded daily OOS
study was nonetheless run under two recorded free-data allowances — the frozen
`label` construction and a label-free `next_open` anchor — to get a real verdict
instead of a merely theoretical one (see §9.1). Both **DISCONFIRMED** on every
OOS gate for both sides. This does not pass Phase 0 and does not authorize
deployment; it closes the free, bounded daily falsification with an explicit
negative result, which is the informative outcome the gate was designed to
produce from this candidate.

## 10. What would unblock Phase 0

Holding the audit and the construction fixed, the only remaining variable is the
independent earnings-time source. Web research (2026-08-22, Tavily + direct SEC
EDGAR probes) splits the field into paid vendors and a **free SEC EDGAR path**:

**Paid vendors (what a purchase would actually buy):**

- **Benzinga Earnings calendar API** — explicit `time` (HH:MM:SS) field plus
  actuals/estimates/surprise, history back to ~2010. Direct docs list the
  standalone plan at **$99/month**. This is the cleanest "it has BMO/AMC +
  surprise in one call" option, but it is a monthly subscription and the data
  is not a point-in-time archive we would own.
- **QuantQuote Earnings Release API** — documented `release_time`
  (BMO/AMC/intraday) plus EPS estimate/actual per event. Free Starter tier is
  limited (3 years history); **Growth is $59/month** and covers ~10 years, but
  only ~2016 onward — it **does not** cover the frozen 2013–2016 IS years at
  the cheap tier. The Jan-2000 Pro tier is still marked "coming soon."
- **First Rate Data / FMP / intrinio** — similar BMO/AMC earnings calendars;
  pricing is subscription-based and history may be shallower than 2012 for
  delisted names.

For our exact need (independent date + BMO/AMC for 100 events spread over
**2012–2021**, including delisted small caps), the cheap tiers of these vendors
are either too shallow or monthly-subscription, and **none reliably covers the
delisted 2012–2016 stratum** that was the actual free-data failure.

**Update (2026-08-24, corrected) — the free EDGAR harness was run and two parser
bugs were fixed; it is still not a pass.**

**Update (2026-08-24, second) — three further harness bugs were fixed; the
audit now resolves 96 of 100 rows, agreement 90/96 = 0.9375, still FAIL.**

The direct EDGAR harness (`research/earnings-anchored-vwap/timing_audit.py`, driven by `run_probe.py`) resolved each of the fixed 100 symbols to a CIK, pulled Item 2.02 8-K / 6-K filings in the window, derived BMO/AMC from the acceptance timestamp and the attached EX-99 press release, and classified date + pre/post:

| Outcome | Count |
|---|---:|
| Verified: date and pre/post agree with template | 90 |
| not_found: no Item 2.02 / 6-K / periodic filing in window | 1 |
| ambiguous: no conclusive release or call time from free evidence | 3 |
| Verified rows where pre/post agrees with template | 90 |
| Verified rows where pre/post disagrees with template | 6 |

`verified_rows = 96 < 100` and agreement `90/96 = 0.9375 < 0.95`. The frozen gate requires **both**, so Phase 0 is **FAIL** (`research/earnings-anchored-vwap/outputs/phase0_summary.json`). After three harness fixes this reflects the honest free-data ceiling:

- The 5 rows freed by the first parser fixes (ARDX, MSM, SUI, DRH, HCKT) all verify **and match** the template — their EX-99 press releases pinned the release date and session (e.g. ARDX "May 9, 2016 ... conference call today at 4:30 p.m. ET" = post), which the over-strict Date-of-Report hygiene had discarded.
- The second set of fixes (exhibit enumeration via the free accession full-text index, all-candidate ranking, and 10-Q/10-K exhibit fallback) freed **PCMI, HIVE** (ambiguous -> verified, match) and **DY** (not_found -> verified, match). DY's release came in the 11-26 8-K carrying the 11-25 Date of Report and the same EX-99 text; the old first-candidate rule had resolved to its 11-27 transcript instead.
- The 1 remaining not_found is **SP** — its same-day 8-K is an IPO-related Item 1.01/9.01 filing, and there is no earnings release in the window at all. Per the frozen honesty rule "release date never moved to fit a filing," this is correctly not_found.
- The 3 ambiguous are foreign issuers whose 6-K acceptance time is not the release time and whose exhibit text carries no call time or dateline anchor (CRNT, CSTM, FCFS). These were never conclusively resolvable from free data.
- Six verified rows are genuine template-side session-label errors surfaced by the audit: the four previously reported (HOMB, TRIP, GPX, BSVN) plus **SEIC** (10-Q exhibit release 2013-04-24 "2:00 p.m. ET" = post; template says pre) and **BMO** (6-K exhibit release 2017-12-05 "2:00 p.m. Tuesday" = post; template says pre). The frozen gate may not rewrite the template to fit the audit, so these stand as mismatches. Caveat: BMO is a mid-session 2:00 p.m. call labeled post by the same PM-convention the template already applies to HOMB; either way it is not a template `pre`.

Net: the free EDGAR path removed the Yahoo archive limitation and three harness defects, but still cannot satisfy the frozen 100-row / 95% gate. The remaining unresolvable rows are genuinely impossible from free data (SP has no filing; CRNT/CSTM/FCFS never published a call time), and the six template-side mismatches cannot be rewritten under the frozen honesty rule. The probe stays blocked on independent release-time verification of the full stratified sample; the only documented unblocking path remains a paid point-in-time earnings-time source, and per the frozen rules **no purchase is justified** by this result (even a paid pass would not authorize deployment — owned data ends 2021).

**Free path that materially changes the decision — SEC EDGAR, verified directly:**

- EDGAR retains the **complete filing history of delisted registrants**, which
  is exactly the stratum Yahoo drops. Verified in a live probe: a delisted name
  from the fixed sample (**CRAY** CIK 9158) returned **10 Item 2.02 8-K
  filings in 2012–2013** (`0000949158-13-000037`, `...13-000026`,
  `...12-461680`, etc.) via the free, no-auth
  `https://data.sec.gov/submissions/CIK{cik}.json` endpoint. The `items` field
  flags `2.02` directly.
- Each filing index also exposes the **acceptance timestamp**
  (`/Archives/edgar/data/{cik}/{accession}/`), from which BMO/AMC can be
  derived relative to market hours. Combined with the attached EX-99 press
  release, this is an independent, point-in-time-adjacent source.
- **Caveat (kept honest):** the 8-K **acceptance time** is the SEC filing
  moment, which is not always the press-release moment (a release can be
  furnished after it goes out). For a date + BMO/AMC *audit*, this is a strong
  independent check, but a small minority of events may need the EX-99 press
  release text to disambiguate; that text is also free on EDGAR. EDGAR's
  full-text search API also needs no token on its plain endpoint
  (`https://efts.sec.gov/LATEST/search-index?q="<accn>"` returns 200; only the
  `.json` suffix 403s), so exhibits the per-filing directory index omits can
  still be enumerated. The per-CIK submissions + archive index route needs
  **no authentication** and worked for the delisted probe.

Concrete decision now:

1. **Do not buy anything yet.** The free EDGAR route appears to cover the exact
   stratum (delisted, 2012–2016) that Yahoo did not, and it costs nothing. The
   next step is to wire a small harness that, for each of the 36 uncovered
   rows, resolves the CIK, pulls Item 2.02 8-Ks in the ±5-day window, and marks
   `verified_date` + `verified_release_time` (BMO/AMC) plus a source URL. If
   this achieves ≥95% agreement across the fixed 100, Phase 0 passes **without
   any purchase**.
2. Only if the EDGAR route fails on a material number of rows (e.g., a name
   with no Item 2.02 filing in the window) should a purchase be considered —
   and then **Benzinga at $99/mo is the documented fit**, with the monthly cost
   and the fact that a pass still does not authorize deployment (data ends
   2021) both logged and weighed before anything is paid.

The full-panel census (§4.3) confirms the probe is **not** blocked on the
tradeability or sample-size gates: thousands of eligible OOS candidates per
side exist. The only blocker remains independent release-time verification of
the fixed 100 rows. **State of that path as of 2026-08-24 (second correction):** the free
EDGAR audit has now been executed (see the update in §10 above) and yields 96
verified / 4 unresolved of the fixed 100 — close but still below the frozen
gate on both the count and, after the six template-side mismatches, the
agreement. Three genuine harness bugs in the audit were found and fixed; the
remaining unresolvable rows are one absent-filing not_found (SP), three
foreign-issuer/call-time-less ambiguities (CSTM, CRNT, FCFS), and six
audit-confirmed template-side session-label errors that the frozen honesty
rule forbids rewriting. So the free path is **exhausted, not merely
hypothesized**, and Phase 0 remains blocked unless the gate or audit sample is
changed (not done silently) or a paid point-in-time earnings-time source is
purchased.

## Sources and evidence record

- Book source: `VWAP Book Final Jun 7 2024.pdf`, pp. 45–46 (earnings anchor) and pp. 76–110 (confirmation, stop, and 1:1 example). See [source audit](vwap-book-source-audit.md).
- Existing data and PEAD outcome: [PEAD research spec](../research-specs/pead-research-spec.md) and [strategy record](../strategies/pead/PEAD.md).
- [Christensen, Timmermann, and Veliyev, *Warp speed price moves: Jumps after earnings announcements* (2026)](https://arxiv.org/abs/2601.08962) — recent high-frequency evidence on the speed of post-earnings price adjustment.
- [Grégoire et al., *How Is Earnings News Transmitted to Stock Prices?* (2022)](https://doi.org/10.1111/1475-679X.12394) — price discovery, liquidity, and after-hours context.
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and [SEC Form 8-K rule release](https://www.sec.gov/files/rules/final/33-8400.pdf) — filing timestamps and the limitation of treating a later filing as the release moment.
- [Benzinga earnings calendar](https://docs.benzinga.com/api-reference/calendar-api/get-earnings) and [earnings stream](https://docs.benzinga.com/ws-reference/data-websocket/get-calendar-earnings-stream) — documented fields for timestamp, actuals, estimates, and surprise; standalone plan $99/mo with history to ~2010.
- [QuantQuote earnings-release API](https://quantquote.com/data/earnings-dates) — documented BMO/AMC/intraday release time; Growth $59/mo (~10 yr history), Pro (Jan-2000) marked "coming soon."
- [SEC EDGAR company submissions API](https://data.sec.gov/submissions/CIK0000949158.json) and [8-K filing index](https://www.sec.gov/Archives/edgar/data/) — verified free (no auth) Item 2.02 8-K lookups for delisted registrants, 2012-2013 included; acceptance timestamp available from the filing index.
- [IBKR historical-bars documentation](https://ibkrcampus.com/docs/tws-api/doc/market-data-historical/historical-bars/requesting-historical-bars) and [market-data requirements](https://ibkrcampus.com/campus/ibkr-api-page/webapi-doc/) — subscription and retrieval constraints.
- [Databento schema documentation](https://databento.com/docs/knowledge-base) — examples of the bar/quote granularity required for a future intraday study.
