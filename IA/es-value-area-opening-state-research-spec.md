# ES Previous-Day Value-Area Opening-State Study

**Status:** COMPLETED — DISCONFIRMED (2026-09-04)  
**Date:** 2026-08-31  
**Decision owner:** Research only; this is not authorization to trade MES, buy data, or open a prop position.

## 1. Decision being tested

Test one narrow proposition on the S&P 500 futures market:

> Does the relationship between the first hour of ES regular trading and the previous RTH value area produce a positive, friction-adjusted, out-of-sample expectancy when entries are made only on later rejection/retest confirmations?

This is a **Market Profile hypothesis**, not an established edge. A positive result would justify only a forward paper-trading phase. A failed gate closes this exact ES construction; it must not be rescued by discretionary overrides or an optimisation search.

## 2. What is new, and what is already closed

The previous NQ IVAMR probe is closed. It built the prior RTH 70% profile and traded four VAH/VAL breakout/fade plays on 15-minute NQ data; it was net negative after costs in both its pre-registered in-sample and out-of-sample windows. See [IVAMR](../strategies/ivamr/IVAMR.md) and [its research spec](../research-specs/ivamr-research-spec.md).

This study shares the profile vocabulary but is not a rerun of that strategy:

| Dimension | Closed NQ IVAMR | This ES study |
| --- | --- | --- |
| Instrument | NQ | ES historical proxy; MES is only the intended small-size execution vehicle |
| Session filter | No opening-state classification | First-hour acceptance outside/inside the prior value area |
| Entry logic | Four generic intraday plays | One of two mutually exclusive opening states, then one later confirmation type |
| Objective | Test the IVAMR blueprint | Test the source-derived opening/value hypothesis once |
| Status | Disconfirmed | Completed — disconfirmed |

Changing from NQ to ES alone would not create a new strategy. The only reason this deserves one bounded test is the source-derived opening-state rule. It has a weak prior because it remains public, chart-derived information and because nearby intraday futures families already failed.

## 3. What the sources do—and do not—support

### Source-supported concepts

*James F. Dalton, Eric T. Jones, and Robert B. Dalton, Mind Over Markets: Power Trading with Market Generated Information, Updated Edition (Wiley, 2013)* describes value area as the region containing roughly 70% of activity, the POC as the most-active price, and the use of prior value plus opening acceptance/rejection to describe auction context. The supplied text is retained at [Mind Over Markets notes](/Users/adorsys123/.codex/attachments/f8ac7903-b153-4dff-8f40-408f3d4867fa/pasted-text.txt).

The book is especially clear that Market Profile is not a mechanical black box that tells a trader when to buy or sell. It presents a framework for organizing information, not an audited ES/MES trading system. *Steidlmayer on Markets* is consistent with that distinction; its supplied notes are at [Steidlmayer on Markets notes](/Users/adorsys123/.codex/attachments/f2c324ff-0abe-422a-a3fb-5a52c4b60a87/pasted-text.txt).

The original [CBOT Six-Part Study Guide](/Users/adorsys123/Downloads/cbot-a-six-part-study-guide-to-market-profile.pdf) reinforces this on its printed pp. 334-335: it frames the practical question as whether price returns to old value or establishes new value, but explicitly says Market Profile is an analytical decision-support tool, not a buy/sell system with entry/exit signals or historical backtesting. It also uses Liquidity Data Bank (LDB) participant-category volume to distinguish strong from weak developments. We do not possess equivalent ES participant-category data, so this study is intentionally a reduced, testable price-and-bar-volume proxy—not a full implementation of the CBOT framework.

The guide also says that the initial-balance duration must be determined for the particular market: its historical examples vary from one hour in grain futures to one hour and forty minutes in then-current financial futures. It further treats a fixed session boundary as less important in 24-hour markets. Consequently, this study's 09:30–10:30 ES RTH classification and previous-RTH anchor are frozen research choices, not prescriptions validated by CBOT. They may be tested once; they must not be tuned to the ES result.

### Claims deliberately **not** treated as facts

No primary source found supports any of the following as a universal ES/MES result:

| Claim | Status in this study |
| --- | --- |
| ES/MES returns to prior POC about 67% of days after opening inside value | Untested heuristic; not used as a gate or expected win rate |
| A 40% wick ratio is optimal | Untested heuristic; used once as a frozen operational definition |
| 15-minute ES ATR is normally 3–6 points | Regime-dependent observation, not used |
| A one-point VAH/VAL tolerance avoids missing 40% of retests | Untested heuristic; used once as a frozen operational definition |
| A 70% value area proves a normal distribution or predictive mean reversion | False inference; 70% is a profile-construction convention only |

The numerical suggestions in [the supplied automated specification](/Users/adorsys123/.codex/attachments/0d202ced-967d-4e1a-9dc8-2cc05d948bef/pasted-text.txt) are therefore hypotheses to falsify, not evidence. There will be **no parameter grid** and no selection of the best result after viewing outcomes.

## 4. Data, profile construction, and scope

### Instrument and period

* Use the owned continuous ES one-minute cache at `research/relative-value/cache/ES_n_0_1m.parquet`.
* ES supplies the historical sample. MES tracks the same underlying market and is only the prospective retail contract; its 2019 launch makes it unsuitable for creating a longer independent sample.
* Use RTH only: 09:30:00 through 16:00:00 America/New_York, on exchange trading days. Overnight volume is excluded.
* The implementation must first write a coverage report: exact first and last complete RTH sessions, duplicate timestamps, missing expected bars, zero/negative volume rows, and early-close handling. The OOS terminal date is the last complete RTH session in the immutable local cache at that audit. This is a data boundary, not a selectable performance parameter.

### Frozen split

Subject only to the coverage audit above:

* In-sample: 2020-09-01 through 2023-12-29.
* Out-of-sample: 2024-01-02 through the final complete cached RTH session.

The Phase 0 audit completed on 2026-09-02 and found the current cache span is 2020-08-03 through 2026-08-06, with 1,551 RTH sessions and no duplicate timestamps, invalid OHLC rows, or non-positive-volume rows. Therefore the currently frozen OOS endpoint is **2026-08-06**. Shortened sessions are reported by the audit as exchange holidays/early closes and are not silently relabelled as full sessions.

The first available month is not traded because each signal needs a complete prior RTH profile. If the audit shows material missing coverage in either split, the study is **unverifiable** rather than silently repaired with a different date range.

### Profile approximation

True volume-at-price requires tick/trade data. The owned data are one-minute OHLCV, so this study explicitly uses the same proxy already used by IVAMR:

1. For each prior complete RTH session, assign each one-minute bar's entire reported volume to the 0.25-point bin containing that bar's **close**.
2. Sum volume by bin. The midpoint of the highest-volume bin is the POC.
3. Starting at the POC, expand upward or downward one adjacent bin at a time, taking the side with larger adjacent volume (up on a tie), until accumulated volume is at least 70% of that session's volume.
4. The lower edge is VAL and the upper edge is VAH. These levels remain fixed for the next RTH session.

This is not an assertion that the resulting levels are exact exchange volume profiles. It is a reproducible bar-close proxy. A pass may later justify a replication with trade-level volume-at-price; a failure is sufficient to reject the proxy construction.

## 5. Frozen trading rules

All prices are ES index points. A 15-minute signal bar is evaluated only after it closes; an eligible signal fills at the next 15-minute bar's open. Stops and targets are then simulated from one-minute bars, using conservative adverse ordering when both could be reached in the same minute.

### 5.1 First-hour state, set at 10:30 ET

Let `C1...C4` be the closes of the 09:30–09:45, 09:45–10:00, 10:00–10:15, and 10:15–10:30 ET bars.

* `IN_VALUE`: at least three of the four closes are inclusively between prior VAL and VAH.
* `OUT_ABOVE`: at least three closes are strictly above prior VAH.
* `OUT_BELOW`: at least three closes are strictly below prior VAL.
* Otherwise: `UNCLASSIFIED`; do not trade that day.

The three-of-four rule is an explicit implementation convention for the source's qualitative idea of first-hour acceptance. It is not claimed to be empirically optimal.

No signals before the 10:30–10:45 bar. Signals from bars closing after 15:00 ET are ignored. All open positions exit at the 15:55 one-minute bar open, regardless of unrealized P&L.

### 5.2 IN_VALUE: responsive rejection toward prior POC/opposite value

Only the following two plays are allowed:

* **Long at VAL:** a 15-minute bar has `low < VAL`, `close >= VAL`, and lower-wick ratio `(min(open, close) - low) / (high - low) >= 0.40`. Enter long at the next bar open. Stop at signal low minus 2.0 points. Exit 50% at prior POC and 50% at prior VAH. Skip if either target is not strictly above entry.
* **Short at VAH:** mirror image: `high > VAH`, `close <= VAH`, upper-wick ratio `(high - max(open, close)) / (high - low) >= 0.40`. Stop at signal high plus 2.0 points. Exit 50% at prior POC and 50% at prior VAL. Skip if either target is not strictly below entry.

Zero-range bars cannot signal. No engulfing-pattern alternative is added; adding an OR condition would create an untested second setup.

### 5.3 OUT_ABOVE / OUT_BELOW: initiative retest continuation

* **OUT_ABOVE long:** a later 15-minute bar has `low <= VAH + 1.0`, `close > VAH`, and `close > open`. Enter long next-bar open. Stop at `VAH - 2.5`. Exit 50% at entry +10.0 points and 50% at entry +20.0 points.
* **OUT_BELOW short:** mirror image: `high >= VAL - 1.0`, `close < VAL`, and `close < open`. Stop at `VAL + 2.5`. Exit 50% at entry -10.0 points and 50% at entry -20.0 points.

The fixed wick ratio, tolerance, stops, and targets are unvalidated operational choices. They remain fixed for the full run. A later paper-trading phase must not be approved by finding a better combination in this historical sample.

### 5.4 Position and conflict rules

* Maximum two completed entries per day; one open position at a time.
* If both sides could signal on the same 15-minute close, take neither.
* If a position closes, a later qualifying entry may be taken only while the daily cap remains.
* No averaging, reversal after stop, discretionary cancellation, news filter, overnight holding, or manual level adjustment.

## 6. Execution model

The test is reported as a MES-sized execution model even though its price history is ES:

* Base round-trip friction: **0.50 ES points** per complete position, allocated across its exits.
* Stress round-trip friction: **1.00 ES point** per complete position, allocated across its exits.
* These are conservative research assumptions, not a statement of a broker's actual commission or fill quality. Any later paper/live work must replace them with observed MES bid/ask and brokerage costs.

Every report must show gross, base-net, and stress-net results separately. No result may be called viable based on gross P&L.

## 7. Required implementation checks

Before outcomes are examined, the implementation must produce and retain:

1. A data-quality/coverage report described in section 4.
2. A per-session table containing prior-session POC/VAH/VAL, first-hour closes, state, every candidate signal, rejection reason, fill, stop, target, exit, and gross/base/stress P&L.
3. Unit tests for profile expansion, session boundaries in New York time, prior-day-only levels, all state classifications, wick calculations, target-direction skips, same-minute stop/target ordering, daily trade cap, and forced exit.
4. A no-look-ahead audit proving that a trade on date `D` uses only data available no later than its decision bar close on `D`, plus completed RTH data from `D-1`.
5. A manual audit of at least 20 randomly selected sessions against rendered charts/tables before aggregate performance metrics are run.

Implementation belongs in a new isolated research path, proposed as `src/quant_scripts/es_value_area/` and `research/es-value-area/`; the closed NQ IVAMR code and records must remain unchanged.

## 8. Pre-registered decision gates

The study advances only if **all** gates below pass on the untouched OOS sample. Otherwise verdict: **DISCONFIRMED** for this exact proxy, state definition, and execution model.

| Gate | Required OOS result |
| --- | --- |
| Data and causality | All required checks in section 7 pass |
| Sample adequacy | At least 100 completed OOS trades after rules and data exclusions |
| Net expectancy | Aggregate OOS P&L is positive at both base and stress friction |
| Resampling robustness | 5th percentile of 5,000 day-block bootstrap OOS P&L resamples is positive at both frictions |
| Profit factor | Base-net PF >= 1.05 and stress-net PF > 1.00 |
| Concentration | Removing the best OOS day leaves positive base-net P&L; no individual day contributes more than 20% of base-net OOS P&L |
| In-sample sanity | IS base-net P&L is positive; failure makes the outcome non-advancing even if OOS happens to be positive |

The report may show each of the four plays and opening states as diagnostics, but no component selection is permitted after seeing the results. The decision is made on the combined frozen strategy only.

## 9. Interpretation rules

* **All gates pass:** run a separately pre-registered, 60-session MES paper-trading replication using observed broker costs. It is still not proof of a durable edge or permission for meaningful capital.
* **Any performance gate fails:** close this ES construction. Do not claim that discretion would have selected the "good" examples unless a separate prospective discretionary-labeling study is designed before looking at more outcomes.
* **Data/causality gate fails:** verdict is **UNVERIFIABLE** on the current data. The only justified upgrade is trade-level ES/MES data that can construct a genuine volume-at-price profile; it is not justification to tune rules.

## 10. Explicit non-goals

This work does not establish that Market Profile predicts prices, that value areas represent institutional inventory, that most discretionary traders are profitable, or that the author should trade a prop account. It is one honest measurement attempt for one rule set under stated limitations.

## 11. Completed result

The frozen probe ran on 2026-09-04 using the Phase 0-passed ES cache. The implementation corrected an initial scale-out bug before accepting the result; all reported figures below are from the corrected 50%/50% target model.

| Window | Trades/legs | Base net points | Stress net points | Base PF | Stress PF |
| --- | ---: | ---: | ---: | ---: | ---: |
| IS 2020-09-01 to 2023-12-29 | 482 | -346.31 | -587.31 | 0.795 | 0.677 |
| OOS 2024-01-02 to 2026-08-06 | 364 | -464.63 | -646.63 | 0.691 | 0.595 |

The OOS sample-size gate passed, but both OOS net-P&L gates, both bootstrap-p5 gates, both profit-factor gates, and the IS-positive sanity gate failed. Verdict: **DISCONFIRMED** for this exact ES bar-close profile proxy, opening-state definition, and execution model. This does not prove that every discretionary Market Profile approach fails; it closes this mechanical candidate without a parameter search or paid-data purchase.
