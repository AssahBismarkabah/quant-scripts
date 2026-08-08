# NQ VWAP-Pullback ("Drift VWOP Pullback") — Research & Pre-Registration Specification

**Status:** Pre-research specification (bounded falsifiable probe, 2026-08-08)
**Classification:** Execution microstructure (VWAP-anchored intraday mean reversion in NQ futures) claimed to expose institutional execution-algorithm flow
**Source claim:** an interview strategy (M. Kanti, ex-market-maker/quant CIO) marketed as a "prop firm golden ticket" — the rules below are extracted verbatim from that interview and are frozen unchanged for the probe.
**Purpose:** Decide, with a pre-registered gate, whether the rule set earns a live, friction-adjusted edge over an explicit out-of-sample window — or should be cleanly disconfirmed — before any spend beyond the already-owned intraday data stack.

---

## 1. The research question

Does the **"Drift VWOP Pullback"** rule set — VWAP-anchored-at-open plus 15-min drift filter plus hourly-distance filter, entering at the first pullback candle and taking a fixed 2:1 (risk:reward) loser — produce a positive **friction-adjusted** expected edge on NQ (or /ES proxy) intraday bars, and does any such edge **survive an out-of-sample window that was never touched during rule selection**?

The prop-context claim (93.6% pass probability over 4 funded challenges) is a property of prop-contest pass/fail math and a high win rate, not of per-trade edge magnitude. We do **not** replicate the funded-account model; we test the underlying signal: is there real, exploitable drift-plus-pullback behavior, and does it survive out-of-sample?

---

## 2. The extracted rule set (FROZEN — do not tune during the probe)

These are the rules as stated in the interview. They are locked verbatim for the probe; no re-optimization of any parameter is permitted during the run. The only rule-set change allowed prior to running is choosing NQ vs /ES as the instrument, which is fixed in §7 (we test NQ).

Instrument: **NQ** (CME E-mini Nasdaq-100) futures, 5-min execution bars / 15-min trend bars, RTH only (09:30–16:00 ET).

**Anchored VWAP:** VWAP anchored at the RTH market open (09:30 ET) of the session. Session-reset each day; no carry-over across days.

**Trend conditions (evaluated once per 15-min bar; LONG shown, SHORT is the mirror):**
1. Price above anchored VWAP (price below VWAP for SHORT).
2. VWAP rising over the past 15 minutes (one prior 15-min bar → VWAP now > VWAP 15 min ago; falling for SHORT).
3. Over the past 1 hour (past four 15-min bars), NQ price increased >= +0.10% (decreased <= -0.10% for SHORT).

**Time-of-day guard:** no trades 09:30–10:30 ET (first hour excluded) — give VWAP time to establish.

**Entry trigger (once all three conditions are true):** enter on the open of the bar **after** the first pullback candle — the first candle counter to the trend direction that pulls toward the VWAP (first red 5-min candle for a LONG, first green 5-min candle for a SHORT). Entry is a market order at the **open of the bar following** the trigger candle.

**Exits / risk:** LONG risk 80 pts / target 40 pts (reward:risk 0.5). SHORT risk 80 pts / target 50 pts. Take-profit or stop-loss, whichever hits first.

**Guard rails:**
- One position at a time.
- Max 4 trades per day.
- Max 2 losing trades per day (stop trading after 2 losses in a session).
- No new trades after 15:30 ET.
- Close all open positions at 15:55 ET (flat before the close).

**Claimed performance to falsify:** ~64% win rate, avg win +866 pts / avg loss −1300 pts, 300%+ over ~4,000+ trades, developed in-sample 2020–2024, held out-of-sample 2024→2026.

---

## 3. Mechanism / why (per claim) and the honest prior

**Claimed mechanism:** inside banks/brokerages, execution traders execute ~90–95% of orders with VWAP-targeting algorithms. When price pulls back to the anchored VWAP, that algorithm flow intensifies and its side-specific imbalance (more sellers vs buyers) is revealed, producing a sharp continuation push. Buying the first pullback in the established drift direction captures that flow.

**Honest prior (caution):** this is, stripped of the microstructure story, an intraday **trend-follow-with-pullback-entry + strong mean-reversion-to-VWAP** hybrid. We have repeatedly disconfirmed the vol-fade / intraday mean-reversion family on daily/standard data. The distinct ingredients here are (a) the **anchored-at-open VWAP** reference, (b) the 15-min drift filter, and (c) the **prop-firm-framed negative reward:risk** — which flips profitability from per-trade edge onto a high win rate that is structurally vulnerable to a modest tail. Two of the three macro-reversal scenarios (mean reversion decay; high-frequency edge not capturable at these horizons) are plausible ways this fails out-of-sample. The probe exists precisely to test that, not to validate the marketing claim.

---

## 4. Pre-registered test design

**Data (owned — see §6):** Databento `ohlcv-1m` NQ orders (CME GLBX), 2020-08-01 → 2026-08-07 (or best available), resampled to 5-min and 15-min RTH bars; VWAP computed from the 1-min base within each RTH session, anchored to 09:30 ET.

**Split (immutable):**
- **In-sample (train):** 2020-08-01 → 2024-12-31. Only used to *verify* the extracted rules reproduce (not to select them — rules are taken from the interview as-is). The 0.10% and 80/40/50 and 4/2 guard values are all frozen from the claim; no grid search.
- **Out-of-sample (test, primary):** 2025-01-01 → 2026-08-07. This window is structurally unseen by the claimed development (they trained on ≤2024). The gate decision rests on OOS only.

**Series to report (both windows):** trade list (entry ts, side, trigger bar, entry price, exit ts, exit price, exit reason, px P/L), per-day summary, win rate, avg win/loss, profit factor, total return, max drawdown, trades/day, avg trades/day, distribution of trades by entry hour.

**Friction (futures, applied to OOS decision):** base 0.25 pts/trade round trip + 0.05 pts commission/slippage → use a conservative round-trip cost of **0.5 NQ pts** (≈ 1.5 bps at ~15,000; base) and **1.0 NQ pts** (stress). Report net-of-friction.

---

## 5. Pre-registered rejection gates (probe FAILS if ANY holds on OOS)

The OOS window is the decision window. The probe fails if any of the following holds:

1. **OOS net edge not positive:** OOS friction-adjusted total return per NQ point over the test window <= 0 (i.e., at or below breakeven net of friction).
2. **OOS bootstrap confidence interval straddles zero:** bootstrap (e.g. 5k resamples of OOS trades/days) 5th percentile of per-trade or per-day net return <= 0. Mirrors the p5 gate used across the repo.
3. **OOS win-rate collapse:** OOS win rate departs from the claimed ~64% such that the strategy's edge is no longer stat-relevant (e.g. OOS win rate < ~55%, or OOS profit factor < ~1.0 gross). Because the strategy is funded by negative-RR win rate, a modest win-rate decline kills it; this is the pre-listed failure mode.
4. **Per-trade tail fragility confirmed:** OOS max adverse excursion / largest single loss vs the fixed 80-pt stop shows the 2-loss-daily guard rail would be exhausted on many days (i.e., the "golden ticket" win-rate math does not materialize OOS; average days-to-2-losses is short enough to contradict a 49.8% pass claim).
5. **Not reproducible from claimed rules:** in-sample (≤2024) run cannot even approximately reproduce the claimed ~64% win / net positive result when the frozen rules are applied (signals a garbled or cherry-picked rule set or survivorship in the claim). This gate is checked first; if IS doesn't reproduce, we stop and record the claim as irreproducible rather than continue to OOS.
6. **Look-ahead / artifact:** VWAP anchoring, RTH session boundaries, bar resampling, or trigger timestamps are later discovered to leak future info (e.g., VWAP including the entry bar's close, or signals computed on already-closed future data). Any such artifact fails the probe and is fixed then re-run with the fix applied to both windows.

---

## 6. Data & tools (owned — cheap)

- **Databento** (`DATABENTO_API_KEY`, set in `.env`; client 0.82.0 installed): NQ (and /ES proxy) `ohlcv-1m` futures bars, resampled to 5-min/15-min RTH. Intraday OHLCV infra already exists in `src/quant_scripts/spx_gex/databento.py` and `index_rebalancing/databento.py`.
- **Caching:** parquet cache per instrument + per window under `research/nq-vwap-pullback/cache/`; resumable (reuse the 10b5-1 pattern).
- **No additional key/license needed.** yfinance 5-min is NOT a viable fallback (≈7-day lookback only) — Databento is the sole source.
- **Computing edge:** VWAP from the 1-min base, not from 5/15-min close — this is a correctness requirement (gate 6).

---

## 7. Instrument choice

Primary: **NQ** (matches the claim; tightest index-futures liquidity). /ES is an allowed cross-check proxy only. If NQ history is gapped/short, /ES may substitute and is reported as such. Fixed **before** the run; not a free parameter.

---

## 8. What we are deciding

This probe decides whether the **intraday VWAP-anchored pullback** family — the first true intraday/futures candidate we have run — earns a friction-adjusted, out-of-sample edge, or joins the growing list of clean disconfirmations. It is deliberately run with the exact same gate discipline (p5 bootstrap, IS-reproduction, look-ahead audit) as the daily-event studies, so the answer is comparable and trustworthy.

- **Clears all gates on OOS** ⇒ scale up: multi-year full-sample, separate live paper run, persistence/decay gate, shock/regime conditioning (the 2022 rate-hike and 2020/2022 vol regimes matter for futures), then a deploy decision.
- **Fails cleanly** ⇒ the VWAP-pullback/intraday-mean-reversion line is disconfirmed at this construction and we record it with a real answer.

**Gate discipline:** a falsification run. The rules and gates above are fixed before running; the OOS window is untouched during development except through gate 5 (IS reproduction).

---

## 9. Status

- **2026-08-08:** Spec created. Data confirmed owned (Databento intraday futures client + key already in repo `.env`; intraday OHLCV infra reused from the spx_gex/index_rebalancing stack). Rules and gates locked per §2 and §5. Next step: scaffold the probe in `research/nq-vwap-pullback/` + `src/quant_scripts/nq_vwap_pullback/`, fetch NQ 1-min, verify IS reproduction (gate 5), then run OOS (gates 1–4, 6).
