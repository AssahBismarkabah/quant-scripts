import csv
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_scripts.funding_basis import (
    FundingBasisBacktest,
    MarginAssumptions,
    MarginMode,
    SourceFormat,
    TradeDecision,
    build_funding_event,
    validate_dataset,
    validate_trade_window,
    wick_stress,
    FileMarketDataSource,
)


class FundingBasisTests(unittest.TestCase):
    def test_build_funding_event_converts_to_utc(self) -> None:
        event = build_funding_event(datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc))
        self.assertEqual(event.entry_window_end().isoformat(), "2026-07-29T07:50:00+00:00")
        self.assertEqual(event.exit_window_start().isoformat(), "2026-07-29T08:10:00+00:00")

    def test_validate_trade_window_rejects_exact_timestamp(self) -> None:
        event = build_funding_event(datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc))

        with self.assertRaisesRegex(ValueError, "exact funding timestamp"):
            validate_trade_window(
                event,
                datetime(2026, 7, 29, 7, 59, 55, tzinfo=timezone.utc),
                datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc),
            )

    def test_wick_stress_detects_liquidation_hit(self) -> None:
        result = wick_stress(
            long_liquidation_price=105.0,
            short_liquidation_price=95.0,
            observed_low=94.5,
            observed_high=104.0,
        )

        self.assertTrue(result.liquidation_hit)
        self.assertEqual(result.worst_mark_price, 94.5)

    def test_margin_multiplier_matches_assumption(self) -> None:
        self.assertEqual(MarginAssumptions(MarginMode.ISOLATED, False).capital_multiplier(), 2.0)
        self.assertEqual(MarginAssumptions(MarginMode.CROSS, True).capital_multiplier(), 1.0)
        self.assertEqual(MarginAssumptions(MarginMode.CROSS, False).capital_multiplier(), 1.5)

    def test_csv_loader_and_validation(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["ts", "venue", "symbol", "bid", "ask", "mark", "index", "funding_rate_bps"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "ts": "2026-07-29T07:49:00Z",
                        "venue": "binance",
                        "symbol": "BTCUSDT",
                        "bid": "100.0",
                        "ask": "100.5",
                        "mark": "100.2",
                        "index": "100.1",
                        "funding_rate_bps": "1.2",
                    }
                )
                writer.writerow(
                    {
                        "ts": "2026-07-29T07:50:00Z",
                        "venue": "binance",
                        "symbol": "BTCUSDT",
                        "bid": "100.1",
                        "ask": "100.6",
                        "mark": "100.3",
                        "index": "100.2",
                        "funding_rate_bps": "1.3",
                    }
                )

            dataset = FileMarketDataSource(
                path=path,
                venue="binance",
                symbol="BTCUSDT",
                source="sample",
                format=SourceFormat.CSV,
            ).load()
            report = validate_dataset(dataset)

            self.assertEqual(report.row_count, 2)
            self.assertTrue(report.is_valid)
            self.assertEqual(dataset.sorted_snapshots()[0].bid, 100.0)

    def test_backtest_accepts_windowed_trade(self) -> None:
        event = build_funding_event(datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc))
        decision = TradeDecision(
            event=event,
            entry_time=datetime(2026, 7, 29, 7, 50, tzinfo=timezone.utc),
            exit_time=datetime(2026, 7, 29, 8, 10, tzinfo=timezone.utc),
            notional=10_000.0,
            entry_spread_bps=0.5,
            exit_spread_bps=0.5,
            estimated_funding_bps=3.0,
            basis_capture_bps=0.5,
            fees_bps=0.2,
            slippage_bps=0.3,
            liquidation_risk_bps=0.0,
        )
        result = FundingBasisBacktest(minimum_net_edge_bps=1.0).run(dataset=None, decisions=[decision])[0]

        self.assertTrue(result.accepted)
        self.assertGreater(result.trade.net_pnl(), 0.0)


if __name__ == "__main__":
    unittest.main()
