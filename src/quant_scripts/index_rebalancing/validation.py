"""S10 statistical validation: bootstrap + Monte Carlo reshuffle.

Per spec section "Statistical validation":
- Monte Carlo trade reshuffling to study sequence risk.
- Bootstrap resampling to estimate drawdown, expected outcomes, and ruin probability.
- Robustness: result must not depend on a single exceptional event.

Input: per-event results parquet written by run_study (results_base.parquet).
Cells with n < 5 are skipped (a t-stat on 1-4 trades is not estimable).

Ruin is defined as a reshuffled path whose peak-to-trough drawdown exceeds
one full trade's notional (10,000 bps); P(ruin) is the fraction of paths
that hit it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

MIN_CELL_N = 5
DEFAULT_SIMS = 10_000


def _rng(seed: int | None) -> np.random.Generator:
    return np.random.default_rng(seed)


def bootstrap_mean(trades: np.ndarray, n_sims: int, rng: np.random.Generator) -> dict[str, float]:
    """Resample the cell's trades with replacement; distribution of the mean trade."""
    means = np.empty(n_sims)
    for i in range(n_sims):
        means[i] = rng.choice(trades, size=len(trades), replace=True).mean()
    return {
        "boot_mean_bps": float(means.mean()),
        "boot_std_bps": float(means.std(ddof=1)),
        "boot_p5_bps": float(np.percentile(means, 5)),
        "boot_p95_bps": float(np.percentile(means, 95)),
        "p_positive": float((means > 0).mean()),
    }


def reshuffle_sequences(trades: np.ndarray, n_sims: int, rng: np.random.Generator) -> dict[str, float]:
    """Permute the same trades into random orders; track drawdown along the path.

    All P&L in bps of per-trade notional (equal notional per trade).
    The terminal P&L is order-independent (sum of all trades) and reported as a
    deterministic number; what reshuffling measures is sequence risk:
    max peak-to-trough drawdown along the path. Ruin = a path whose drawdown
    exceeds one full trade's notional (10,000 bps).
    """
    n = len(trades)
    max_dd_bps = np.empty(n_sims)
    for i in range(n_sims):
        path = np.cumsum(rng.permutation(trades))
        peak = np.maximum.accumulate(path)
        max_dd_bps[i] = float((peak - path).max())
    return {
        "terminal_sum_bps": float(trades.sum()),
        "max_dd_p50_bps": float(np.median(max_dd_bps)),
        "max_dd_p95_bps": float(np.percentile(max_dd_bps, 95)),
        "p_ruin": float((max_dd_bps > 10_000.0).mean()),
    }


def drop_best_sensitivity(trades: np.ndarray) -> dict[str, float]:
    """Mean trade with the single best trade removed (robustness: no one-event dependence)."""
    best_idx = int(np.argmax(trades))
    rest = np.delete(trades, best_idx)
    return {
        "mean_without_best_bps": float(rest.mean()),
        "best_trade_bps": float(trades[best_idx]),
        "n_without_best": int(len(rest)),
    }


def validate_cells(
    results: pd.DataFrame,
    *,
    n_sims: int = DEFAULT_SIMS,
    seed: int | None = 42,
    metric: str = "abnormal_bps",
) -> pd.DataFrame:
    """Run bootstrap + reshuffle + drop-best on every venue x action x window cell."""
    completed = results[results["completed"]]
    rows: list[dict[str, object]] = []
    rng = _rng(seed)
    for (venue, action, window), group in completed.groupby(["venue", "action", "window_td"]):
        trades = group[metric].to_numpy(dtype=float)
        if len(trades) < MIN_CELL_N:
            rows.append(
                {
                    "venue": venue,
                    "action": action,
                    "window_td": window,
                    "n_events": len(trades),
                    "skipped": f"n < {MIN_CELL_N}",
                }
            )
            continue
        row: dict[str, object] = {
            "venue": venue,
            "action": action,
            "window_td": window,
            "n_events": len(trades),
            "mean_bps": float(trades.mean()),
        }
        row.update(bootstrap_mean(trades, n_sims, rng))
        row.update(reshuffle_sequences(trades, n_sims, rng))
        row.update(drop_best_sensitivity(trades))
        row["skipped"] = ""
        rows.append(row)
    return pd.DataFrame(rows)


def run_s10(
    results_path: Path,
    out_path: Path,
    *,
    n_sims: int = DEFAULT_SIMS,
    seed: int | None = 42,
    metric: str = "abnormal_bps",
) -> pd.DataFrame:
    """Validate both base and stress per-event results; write a single parquet."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for suffix in ("base", "stress"):
        df = pd.read_parquet(results_path.with_name(f"results_{suffix}.parquet"))
        frame = validate_cells(df, n_sims=n_sims, seed=seed, metric=metric)
        frame.insert(0, "case", suffix)
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True)
    out.to_parquet(out_path, index=False)
    return out


__all__ = ["run_s10", "validate_cells", "bootstrap_mean", "reshuffle_sequences"]
