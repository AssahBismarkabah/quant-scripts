from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_scripts.earnings_anchored_vwap.backtest import (  # noqa: E402
    EventSetup,
    filter_events_by_price_integrity,
    find_reaction_signal,
    paired_control_comparison,
    prepare_symbol_bars,
    resolve_anchor_index,
    simulate_reaction_trade,
)
from quant_scripts.earnings_anchored_vwap.config import StudyParams  # noqa: E402


def _bars(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-01", periods=len(rows))
    return pd.DataFrame(
        {
            "date": dates,
            "open": [r[0] for r in rows],
            "high": [r[1] for r in rows],
            "low": [r[2] for r in rows],
            "close": [r[3] for r in rows],
            "volume": [1_000_000] * len(rows),
            "split_coefficient": [1.0] * len(rows),
        }
    )


class TestEarningsAnchoredVwap(unittest.TestCase):
    def setUp(self) -> None:
        self.params = StudyParams(reaction_search_sessions=3, max_holding_sessions=3)

    def test_anchor_timing_maps_pre_to_same_session_and_post_to_next(self) -> None:
        bars = _bars([(100, 101, 99, 100), (101, 102, 100, 101), (102, 103, 101, 102)])
        assert resolve_anchor_index(bars, "2020-01-02", "pre") == 1
        assert resolve_anchor_index(bars, "2020-01-02", "post") == 2

    def test_lagged_atr_does_not_use_anchor_bar_range(self) -> None:
        rows = [(100, 101, 99, 100)] * 21
        rows[20] = (100, 500, 1, 100)
        prepared = prepare_symbol_bars(_bars(rows), StudyParams())
        # Prior 20 sessions all had a 2-point range; the anchor's huge range is excluded.
        self.assertEqual(prepared.iloc[20]["atr20"], 2.0)

    def test_price_integrity_drops_a_split_in_the_full_fixed_window(self) -> None:
        raw = _bars([(100, 101, 99, 100)] * 32)
        raw.loc[24, "split_coefficient"] = 2.0
        prepared = prepare_symbol_bars(raw, self.params)
        events = pd.DataFrame(
            {
                "symbol": ["TEST"],
                "release_date": [prepared.iloc[20]["date"]],
                "release_time": ["pre"],
                "eps": [2.0],
                "eps_est": [1.0],
            }
        )
        retained, audit = filter_events_by_price_integrity(
            events, {"TEST": prepared}, self.params
        )
        self.assertTrue(retained.empty)
        self.assertEqual(audit.iloc[0]["reason"], "invalid_raw_ohlcv_or_split_window")

    def test_reaction_enters_next_open_and_targets_one_r(self) -> None:
        raw = _bars(
            [
                (100, 102, 99, 101),  # anchor; typical price 100.67
                (102, 103, 100, 102.5),  # touches AVWAP and closes bullish above it
                (103, 107, 102, 106),  # entry at 103; target 106 reached
                (106, 107, 105, 106),
                (106, 107, 105, 106),
            ]
        )
        prepared = prepare_symbol_bars(raw, self.params)
        setup = EventSetup("TEST", prepared.iloc[0]["date"], "pre", 0, 1, 0.02, 1.0, 20_000_000.0)
        signal = find_reaction_signal(prepared, setup, self.params, "avwap")
        self.assertEqual(signal, 1)
        trade, reason = simulate_reaction_trade(prepared, setup, self.params, "avwap")
        self.assertEqual(reason, "trade")
        assert trade is not None
        self.assertEqual(trade["entry_date"], prepared.iloc[2]["date"])
        self.assertEqual(trade["exit_reason"], "target")
        self.assertAlmostEqual(trade["entry"], 103.0)
        self.assertAlmostEqual(trade["exit"], 106.0)

    def test_stop_is_chosen_when_stop_and_target_share_a_daily_bar(self) -> None:
        raw = _bars(
            [
                (100, 102, 99, 101),
                (102, 103, 100, 102.5),
                (103, 107, 99, 106),  # spans stop 100 and target 106
                (106, 107, 105, 106),
                (106, 107, 105, 106),
            ]
        )
        prepared = prepare_symbol_bars(raw, self.params)
        setup = EventSetup("TEST", prepared.iloc[0]["date"], "pre", 0, 1, 0.02, 1.0, 20_000_000.0)
        trade, reason = simulate_reaction_trade(prepared, setup, self.params, "avwap")
        self.assertEqual(reason, "trade")
        assert trade is not None
        self.assertEqual(trade["exit_reason"], "stop")
        self.assertAlmostEqual(trade["exit"], 100.0)

    def test_gap_through_stop_exits_at_open(self) -> None:
        raw = _bars(
            [
                (100, 102, 99, 101),
                (102, 103, 100, 102.5),
                (103, 104, 102, 103.5),  # entry day does not hit target
                (98, 100, 97, 99),  # next session opens through stop 100
                (99, 100, 98, 99),
            ]
        )
        prepared = prepare_symbol_bars(raw, self.params)
        setup = EventSetup("TEST", prepared.iloc[0]["date"], "pre", 0, 1, 0.02, 1.0, 20_000_000.0)
        trade, reason = simulate_reaction_trade(prepared, setup, self.params, "avwap")
        self.assertEqual(reason, "trade")
        assert trade is not None
        self.assertEqual(trade["exit_reason"], "gap_stop")
        self.assertAlmostEqual(trade["exit"], 98.0)

    def test_control_comparison_uses_only_matched_events(self) -> None:
        primary = pd.DataFrame(
            {
                "event_id": ["one", "unmatched"],
                "event_date": pd.to_datetime(["2020-01-02", "2020-01-03"]),
                "side": ["long", "long"],
                "net_base_bps": [10.0, 1_000.0],
            }
        )
        control = pd.DataFrame(
            {
                "event_id": ["one"],
                "event_date": pd.to_datetime(["2020-01-02"]),
                "side": ["long"],
                "net_base_bps": [3.0],
            }
        )
        result = paired_control_comparison(
            primary,
            control,
            "net_base_bps",
            StudyParams(bootstrap_simulations=100),
        )
        self.assertEqual(result["matched_trades"], 1)
        self.assertAlmostEqual(result["mean_difference_bps"], 7.0)


if __name__ == "__main__":
    unittest.main()
