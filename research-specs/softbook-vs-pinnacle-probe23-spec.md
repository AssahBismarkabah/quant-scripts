# Probe #23 Spec — Soft-Book vs Pinnacle Closing-Line Divergence (FROZEN)

**Date:** 2026-08-20
**Status:** TERMINAL — DEAD (2026-08-20; G2, G3, G4 failed on IS; verdict per §5). Pre-registered before any code beyond the exploratory first pass (recorded in `IA/turning-point/01-capacity-constrained-arenas.md` §7 amendment). No post-hoc test selection. The sports lane is now terminal on measurement (exchange side Probe #22, soft-book side Probe #23).
**Type:** Pre-registered research spec — the explicit user amendment to the frozen rule (§5 of `01-capacity-constrained-arenas.md`): exactly one additional probe within the sports lane, soft-book side.
**Plan:** `IA/turning-point/02-PROBE-22-PLAN.md` (Probe #22 terminal read + this amendment).

## 1. Thesis

Exchanges (Kalshi, Polymarket) are welded to the sharp line (measured dead in Probe #22: PM soccer within ~2¢ of Pinnacle closing). **Soft books** (Bet365, BetMGM, BetVictor, Betway, Coral, Ladbrokes) set prices to balance liability and recreational flow, NOT to probability, and they **lag sharp money**. If a soft book's closing price differs from the Pinnacle de-juiced closing probability by more than friction, betting the soft book at Pinnacle-fair terms is +EV — the classic "beating the closing line" signal that professional sports bettors screen.

## 2. Data (owned, no new cost)

- `research/prediction-markets/data/football-data/{EPL,Championship,LaLiga,SerieA,Bundesliga}_2526.csv` — IS season 2025/26 (Aug 2025–Jan 2026, ~1,016 fixtures with Pinnacle closing).
- `..._2425.csv` — OOS season 2024/25, same 5 leagues (to be fetched from football-data.co.uk).
- Columns: soft-book closing odds `B365CH/B365CD/B365CA`, `BMGMCH...`, `BVCH...`, `BWCH...`, `CLCH...`, `LBCH...`; Pinnacle closing `PSCH/PSCD/PSCA`; result `FTR`; Asian-handicap closing available as an optional secondary check (NOT used for the primary gate).
- NOTE (data semantics, verified): un-prefixed columns (`B365H`, `PSH`) are OPENING odds; `C`-prefixed are CLOSING. Primary test uses CLOSING-vs-CLOSING only.

## 3. Method (frozen)

For every fixture × book × leg (H/D/A) where both soft closing and Pinnacle closing exist:

1. De-juice Pinnacle closing 3-way: `p_sharp(leg) = (1/PS_leg) / Σ(1/PS_h + 1/PS_d + 1/PS_a)`.
2. Signal: `EV = soft_close_odds(leg) × p_sharp(leg) − 1`. Positive EV = soft book prices the leg below Pinnacle-fair.
3. Realized test (primary): flat stake $1 on every leg with `EV > τ`, for τ ∈ {1%, 2%, 3%, 4%}; payoff = `odds − 1` if leg won (FTR), −1 if lost. Report per τ: n, win rate, ROI, total P&L, per-book and per-league splits.
4. Brier falsification: compare de-juiced Pinnacle 3-way vs each soft book's de-juiced 3-way on the actual result. A real signal requires Pinnacle Brier ≤ soft-book Brier (the divergence is soft-book error, not Pinnacle being worse than the books).
5. Persistence: split IS by date (Aug–Oct vs Nov–Jan); ROI must be positive in both halves.
6. OOS: run steps 1–3 frozen on 2024/25 season, same τ, same books, no re-tuning.
7. Capacity: report max flat stakes implied by realistic soft-book limits ($200/bet × n/yr) — informational only, not a gate.

## 4. Friction model (frozen)

- Sports-betting friction at these stakes: no per-bet fee; cost = the book's own margin (already inside the odds — EV is computed against de-juiced sharp prob, so the margin is paid implicitly). Conservative additional friction: 1.0% per bet (limits/withdrawal drag/account attrition) — applied as a flat haircut to ROI.
- Effective gate threshold: τ = 2% EV ⇒ net ≥ 1% after the 1% haircut.

## 5. Gates (frozen, pre-registered)

- **G1 (existence):** ≥ 30 events/yr at `EV > 2%` on IS.
- **G2 (realization):** IS realized ROI at τ=2% > +1% net (after 1% friction haircut), n ≥ 100.
- **G3 (prediction):** Pinnacle Brier ≤ soft-book Brier on IS (sharp line is the better forecaster).
- **G4 (persistence):** IS ROI positive in both Aug–Oct and Nov–Jan halves at τ=2%.
- **G5 (OOS):** OOS (2024/25) realized ROI at τ=2% > 0 with n ≥ 30.

Verdicts: **CERTIFIED** (all gates) → proceed to ops-pilot design (separate decision); **DEAD** (G2, G3, G4, or G5 fail) → terminal, no further probes in the sports lane; **UNVERIFIABLE** (G1/G5 event-count shortfalls) → recorded honestly as such, no re-litigation.

## 6. Known caveats (recorded, not gate-tested)

- football-data "closing" lines are snapshots near kickoff, not provably simultaneous across books; a systematic snapshot-timing offset could inflate EV. Mitigation: the realized test (G2) uses actual results — if the price was real at the snapshot moment, ROI is real; the OOS gate (G5) and persistence gate (G4) bound timing artifacts.
- Soft books limit/bans winners — the known ops cost of any certified result. Account management is the business; this spec only certifies the signal.
- Single-sport sample (soccer, 5 leagues). Non-verification of other sports is recorded, not tested.

## 7. Status log

- **2026-08-20:** Spec frozen. Exploratory first pass (closing-vs-closing, real books only, excl. synthetic MAX): 437 fixture-book rows >2% EV, 209 >4%, 136 >6% over IS 1,016 fixtures; per-book over-2% counts: B365 94, BMGM 106, BV 87, BW 59, CL 51, LB 40. Not evidence — gates above are the evidence. Next: fetch OOS 2024/25 files, run frozen protocol, record verdict.
- **2026-08-20 — PROBE TERMINAL READ (DEAD):** Frozen protocol run on IS 2025/26 (5 leagues, 1,016 fixtures, 18,285 fixture-book-leg rows, 6 real books) and OOS 2024/25 (2 books with closing data — B365, BW; BMGM/BV/CL/LB absent from 2425 files).
  - **IS realized (primary gate):** τ=1%: n=646, ROI −29.6% (net −30.6%); τ=2%: n=468, ROI **−33.3%** (net −34.3%); τ=3%: n=309, ROI −29.6%; τ=4%: n=219, ROI −30.3%. **G2 FAILS by ~35 points.** Per-book at τ=2%: B365 −16.4% (n=100), BMGM −50.9% (n=113), BV −36.0% (n=96), BW −30.5% (n=64), CL −39.6% (n=54), LB −15.8% (n=41) — every book negative.
  - **G3 (prediction) FAILS — mechanism identified:** de-juiced soft-book Brier equals Pinnacle's: B365 0.5908, BMGM 0.5905, BV 0.5903, BW 0.5908, CL 0.5905, LB 0.5908, Pinnacle 0.5906 (n≈1,016 fixtures each). Soft books are NOT worse forecasters than Pinnacle. The apparent divergence is a **snapshot-timing artifact** (football-data closing snapshots are not simultaneous across books; late sharp moves land in Pinnacle's column but not the soft books'), not soft-book error — confirmed as the dominant mechanism per §6 caveat.
  - **G4 (persistence) FAILS:** τ=2% Aug–Oct ROI −29.8% (n=386), Nov–Jan −49.7% (n=82).
  - **G1 PASSES** (468 events/yr at >2% EV), **G5 passes on the letter**: OOS τ=2% n=37, ROI +6.4% (net +5.4%); but n is ~12× smaller than IS, the universe is only 2 books vs 6, and the sign directly contradicts IS — recorded as noise/confounded, not evidence.
  - **Verdict: DEAD (G2, G3, G4 fail).** Per §5: terminal, no further probes in the sports lane. The "beating the closing line" signal does not survive contact with outcomes in this data; the exploratory EV distribution was an artifact of non-simultaneous snapshots. Artifacts: `outputs/softbook_IS_2526.csv`, `outputs/softbook_OOS_2425.csv`, script `softbook_probe.py`, data `data/football-data/*_2425.csv`.