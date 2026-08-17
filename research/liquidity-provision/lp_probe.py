import json
from pathlib import Path

import numpy as np
import pandas as pd

SPEC = Path(__file__).parent / 'LP_PROBE_SPEC.md'
OUT = Path(__file__).parent / 'outputs'
OUT.mkdir(exist_ok=True)

DATA = {
    'BTCUSDT': Path(__file__).parents[1] / 'crypto-perps/cache/BTCUSDT_1m.parquet',
    'ETHUSDT': Path(__file__).parents[1] / 'crypto-perps/cache/ETHUSDT_1m.parquet',
}

SPREAD_BPS = {'BTCUSDT': 1.0, 'ETHUSDT': 2.0}
ROBUST_SPREAD_BPS = 5.0
K = 60
MAKER_FEE_BPS = 2.0
RNG = np.random.default_rng(7)
BOOT_N = 10000
SUBSAMPLE_IID = 100000
SUBSAMPLE_DAY = 50000
DAY_BOOT_N = 1000


def load(path):
    df = pd.read_parquet(path)
    df['ts'] = pd.to_datetime(df['open_time'], unit='ms')
    return df.reset_index(drop=True)


def trade_through(df, spread_bps):
    open_ = df['open'].to_numpy(float).tolist()
    high = df['high'].to_numpy(float).tolist()
    low = df['low'].to_numpy(float).tolist()
    n = len(df)
    half = spread_bps / 2 / 10000
    trades = []  # (entry_px, exit_px, fill_index)
    t = 0
    while t < n - 2:
        bid = open_[t] * (1 - half)
        ask = open_[t] * (1 + half)
        end = min(t + K, n - 1)
        mb = ma = None
        for m in range(t + 1, end + 1):
            if mb is None and low[m] <= bid:
                mb = m
            if ma is None and high[m] >= ask:
                ma = m
            if mb is not None and ma is not None:
                break
        if mb is None and ma is None:
            t += 1
            continue
        if mb is not None and (ma is None or mb <= ma):
            entry = bid
            m = mb
            side = 0
        else:
            entry = ask
            m = ma
            side = 1
        if m + 1 >= n:
            break
        trades.append((entry, open_[m + 1], m, side))
        t = m + 1
    if not trades:
        return np.empty((0, 2)), np.empty(0, dtype='int64'), np.empty(0, dtype='int64')
    arr = np.array(trades)
    return arr[:, :2], arr[:, 2].astype('int64'), arr[:, 3].astype('int64')


def edges(trades, side):
    entry, exit_ = trades[:, 0], trades[:, 1]
    raw = np.where(side == 'buy', exit_ / entry - 1, entry / exit_ - 1)
    return raw * 10000 - 2 * MAKER_FEE_BPS


def boot_p5(x, n=BOOT_N):
    if len(x) == 0:
        return np.nan
    x = RNG.choice(x, size=min(SUBSAMPLE_IID, len(x)), replace=False)
    means = np.empty(n)
    for i in range(n):
        means[i] = RNG.choice(x, size=len(x), replace=True).mean()
    return float(np.percentile(means, 5))


def day_block_p5(x, idx_day):
    if len(x) == 0 or len(np.unique(idx_day)) < 2:
        return np.nan
    keep = RNG.choice(len(x), size=min(SUBSAMPLE_DAY, len(x)), replace=False)
    x = x[keep]
    idx_day = idx_day[keep]
    days = np.unique(idx_day)
    means = np.empty(DAY_BOOT_N)
    for i in range(DAY_BOOT_N):
        pick = RNG.choice(days, size=len(days), replace=True)
        means[i] = x[np.isin(idx_day, pick)].mean()
    return float(np.percentile(means, 5))


def run_symbol(name, df, spread_bps, window=None):
    if window:
        df = df[(df['ts'] >= window[0]) & (df['ts'] <= window[1])].reset_index(drop=True)
    trades, fill_idx, side = trade_through(df, spread_bps)
    if len(trades) == 0:
        return None
    e = edges(trades, np.where(side == 0, 'buy', 'sell'))
    day_of_trade = df['ts'].iloc[fill_idx].dt.normalize().astype('int64').to_numpy()
    n_days = max(1, df['ts'].dt.normalize().nunique())
    return {
        'n_trades': int(len(e)),
        'fills_per_day': round(len(e) / n_days, 2),
        'mean_edge_bps': float(e.mean()),
        'median_edge_bps': float(np.median(e)),
        'hit_rate': float((e > 0).mean()),
        'p5_bootstrap_mean_bps': boot_p5(e),
        'p5_day_block_mean_bps': day_block_p5(e, day_of_trade),
        'n_buys': int((side == 0).sum()),
        'n_sells': int((side == 1).sum()),
    }


def main():
    full = {}
    sub = {}
    robust = {}
    for sym, path in DATA.items():
        df = load(path)
        full[sym] = run_symbol(sym, df, SPREAD_BPS[sym])
        sub[sym] = run_symbol(sym, df, SPREAD_BPS[sym], window=('2023-01-01', '2026-07-31'))
        robust[sym] = run_symbol(sym, df, ROBUST_SPREAD_BPS)

    btc = full['BTCUSDT']
    verdict = 'PASS' if (btc and btc['p5_bootstrap_mean_bps'] > 0) else 'FAIL'
    summary = {
        'meta': {
            'pre_registered': '2026-08-17',
            'spec': str(SPEC),
            'spread_bps': SPREAD_BPS,
            'robust_spread_bps': ROBUST_SPREAD_BPS,
            'k_quote_validity_min': K,
            'maker_fee_bps_each_side': MAKER_FEE_BPS,
            'exit': 'open of minute after fill (maker, no-lookahead)',
            'bootstrap_note': 'iid p5 on 100k-trade subsample (conservative SE); day-block p5 on 50k subsample, 1000 resamples',
            'seed': 7,
        },
        'full_window': full,
        'sub_window_2023plus': sub,
        'robustness_5bps': robust,
        'gates': {
            'G1_btc_p5_gt_0': bool(btc['p5_bootstrap_mean_bps'] > 0),
            'G2_btc_median_gt_0_hitrate_gt_45': bool(btc['median_edge_bps'] > 0 and btc['hit_rate'] > 0.45),
            'G3_eth_mean_positive': bool(full['ETHUSDT']['mean_edge_bps'] > 0),
            'G4_2023plus_btc_p5_gt_0': bool(sub['BTCUSDT']['p5_bootstrap_mean_bps'] > 0),
        },
        'verdict': verdict,
    }
    (OUT / 'lp_probe_summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()