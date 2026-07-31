import csv
import hashlib
import hmac
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import os
from unittest.mock import patch, MagicMock
from urllib.request import Request

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_scripts.funding_basis import (
    BinanceFileMarketDataSource,
    BinanceRecordType,
    BinanceCredentials,
    BinanceIngestionService,
    BinanceRestClient,
    FundingBasisBacktest,
    MarginAssumptions,
    MarginMode,
    SourceFormat,
    TradeDecision,
    funding_rate_rows_to_dataset,
    build_funding_event,
    replay_fixture_set_many,
    replay_fixture_set,
    summarize_regimes,
    validate_dataset,
    validate_trade_window,
    wick_stress,
    FileMarketDataSource,
    mark_price_klines_to_dataset,
    spot_klines_to_dataset,
)
from quant_scripts.funding_basis.cli import build_parser


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

    def test_backtest_classifies_negative_basis_rejection(self) -> None:
        event = build_funding_event(datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc))
        decision = TradeDecision(
            event=event,
            entry_time=datetime(2026, 7, 29, 7, 50, tzinfo=timezone.utc),
            exit_time=datetime(2026, 7, 29, 8, 10, tzinfo=timezone.utc),
            notional=10_000.0,
            entry_spread_bps=0.5,
            exit_spread_bps=0.5,
            estimated_funding_bps=0.5,
            basis_capture_bps=-1.0,
            fees_bps=0.2,
            slippage_bps=0.3,
            liquidation_risk_bps=0.0,
        )
        result = FundingBasisBacktest(minimum_net_edge_bps=0.0).run(dataset=None, decisions=[decision])[0]

        self.assertFalse(result.accepted)
        self.assertEqual(result.rejection_reason, "basis capture below threshold (-1.000000 bps < 0.000000 bps)")

    def test_backtest_applies_basis_threshold(self) -> None:
        event = build_funding_event(datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc))
        decision = TradeDecision(
            event=event,
            entry_time=datetime(2026, 7, 29, 7, 50, tzinfo=timezone.utc),
            exit_time=datetime(2026, 7, 29, 8, 10, tzinfo=timezone.utc),
            notional=10_000.0,
            entry_spread_bps=0.5,
            exit_spread_bps=0.5,
            estimated_funding_bps=1.0,
            basis_capture_bps=0.4,
            fees_bps=0.2,
            slippage_bps=0.3,
            liquidation_risk_bps=0.0,
        )
        result = FundingBasisBacktest(minimum_net_edge_bps=0.0, minimum_basis_capture_bps=0.5).run(dataset=None, decisions=[decision])[0]

        self.assertFalse(result.accepted)
        self.assertEqual(result.rejection_reason, "basis capture below threshold (0.400000 bps < 0.500000 bps)")

    def test_binance_jsonl_loader_normalizes_agg_trade(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "binance.jsonl"
            path.write_text(
                "\n".join(
                    [
                        '{"T": 1722240000000, "s": "BTCUSDT", "p": "100.25"}',
                        '{"T": 1722240001000, "s": "BTCUSDT", "p": "100.35"}',
                    ]
                ),
                encoding="utf-8",
            )

            dataset = BinanceFileMarketDataSource(
                path=path,
                venue="binance",
                symbol="BTCUSDT",
                record_type=BinanceRecordType.AGG_TRADE,
                source="fixture",
            ).load()

            self.assertEqual(dataset.venue, "binance")
            self.assertEqual(dataset.symbol, "BTCUSDT")
            self.assertEqual(dataset.snapshots[0].last, 100.25)
            self.assertEqual(dataset.snapshots[1].last, 100.35)

    def test_binance_credentials_load_from_env(self) -> None:
        with patch.dict(os.environ, {"BINANCE_API_KEY": "abc", "BINANCE_API_SECRET": "def"}, clear=False):
            creds = BinanceCredentials.from_env()

        self.assertEqual(creds.api_key, "abc")
        self.assertEqual(creds.api_secret, "def")

    def test_binance_credentials_load_from_dotenv_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            env_path = repo_root / ".env"
            env_path.write_text(
                "BINANCE_API_KEY=file-key\nBINANCE_API_SECRET=file-secret\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                creds = BinanceCredentials.from_env(env_path)

        self.assertEqual(creds.api_key, "file-key")
        self.assertEqual(creds.api_secret, "file-secret")

    def test_binance_signed_request_builds_expected_url(self) -> None:
        creds = BinanceCredentials(api_key="key", api_secret="secret")
        client = BinanceRestClient(credentials=creds)

        fake_response = MagicMock()
        fake_response.__enter__.return_value.read.return_value = b"{}"
        fake_response.__exit__.return_value = False

        with patch("quant_scripts.funding_basis.client.urlopen", return_value=fake_response) as urlopen_mock, patch(
            "quant_scripts.funding_basis.client.time.time", return_value=1000.0
        ):
            client.get_futures_account()

        request = urlopen_mock.call_args.args[0]
        self.assertIsInstance(request, Request)
        self.assertIn("timestamp=1000000", request.full_url)
        expected_query = "timestamp=1000000&recvWindow=5000"
        expected_signature = hmac.new(
            b"secret",
            expected_query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self.assertIn(f"signature={expected_signature}", request.full_url)

    def test_binance_funding_rate_rows_normalize_to_dataset(self) -> None:
        dataset = funding_rate_rows_to_dataset(
            rows=[{"fundingTime": 1722240000000, "fundingRate": "0.0001"}],
            venue="binance",
            symbol="BTCUSDT",
            source="fixture",
        )

        self.assertEqual(dataset.snapshots[0].funding_rate_bps, 1.0)
        self.assertEqual(dataset.snapshots[0].ts.isoformat(), "2024-07-29T08:00:00+00:00")

    def test_binance_kline_rows_normalize_to_dataset(self) -> None:
        spot_dataset = spot_klines_to_dataset(
            rows=[[1722240000000, "1", "2", "0.5", "1.5", "100"]],
            venue="binance",
            symbol="BTCUSDT",
            source="fixture",
        )
        mark_dataset = mark_price_klines_to_dataset(
            rows=[[1722240000000, "1", "2", "0.5", "1.75", "100"]],
            venue="binance",
            symbol="BTCUSDT",
            source="fixture",
        )

        self.assertEqual(spot_dataset.snapshots[0].last, 1.5)
        self.assertEqual(mark_dataset.snapshots[0].mark, 1.75)

    def test_binance_ingestion_service_normalizes_client_payloads(self) -> None:
        client = MagicMock()
        client.get_futures_funding_rate_history.return_value = [
            {"fundingTime": 1722240000000, "fundingRate": "0.0001"}
        ]
        client.get_futures_mark_price_klines.return_value = [[1722240000000, "1", "2", "0.5", "1.75", "100"]]
        client.get_spot_klines.return_value = [[1722240000000, "1", "2", "0.5", "1.5", "100"]]
        service = BinanceIngestionService(client=client)

        funding_dataset = service.load_funding_history("BTCUSDT")
        mark_dataset = service.load_mark_price_klines("BTCUSDT", "1h")
        spot_dataset = service.load_spot_klines("BTCUSDT", "1h")

        self.assertEqual(funding_dataset.snapshots[0].funding_rate_bps, 1.0)
        self.assertEqual(mark_dataset.snapshots[0].mark, 1.75)
        self.assertEqual(spot_dataset.snapshots[0].last, 1.5)

    def test_cli_parser_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args([])

        self.assertEqual(args.symbol, "BTCUSDT")
        self.assertEqual(args.interval, "1h")
        self.assertEqual(args.mode, "smoke")

    def test_cli_parser_smoke_mode(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--mode", "smoke"])

        self.assertEqual(args.mode, "smoke")

    def test_cli_parser_dump_mode(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--mode", "dump", "--output-dir", "fixtures", "--start-time", "2026-07-29T00:00:00Z"])

        self.assertEqual(args.mode, "dump")
        self.assertEqual(str(args.output_dir), "fixtures")
        self.assertEqual(args.start_time, 1785283200000)

    def test_cli_parser_replay_mode(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--mode", "replay"])

        self.assertEqual(args.mode, "replay")

    def test_cli_parser_show_trades_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--mode", "replay", "--show-trades"])

        self.assertTrue(args.show_trades)

    def test_cli_parser_sweep_mode(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--mode", "sweep", "--basis-thresholds", "0.0,0.5,1.0", "--net-thresholds", "0.0,1.0,2.0"])

        self.assertEqual(args.mode, "sweep")
        self.assertEqual(args.basis_thresholds, "0.0,0.5,1.0")
        self.assertEqual(args.net_thresholds, "0.0,1.0,2.0")

    def test_fixture_replay_runs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        replay = replay_fixture_set(
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_funding.json",
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_mark.json",
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_spot.json",
        )

        self.assertEqual(replay.funding.symbol, "BTCUSDT")
        self.assertEqual(replay.mark.symbol, "BTCUSDT")
        self.assertEqual(replay.spot.symbol, "BTCUSDT")

    def test_fixture_replay_many_runs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        replay = replay_fixture_set_many(
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_funding.json",
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_mark.json",
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_spot.json",
        )

        self.assertGreaterEqual(len(replay.decisions), 1)
        self.assertEqual(len(replay.decisions), len(replay.results))

    def test_regime_summary_splits_results(self) -> None:
        root = Path(__file__).resolve().parents[1]
        replay = replay_fixture_set_many(
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_funding.json",
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_mark.json",
            root / "research" / "funding-basis" / "fixtures" / "btcusdt_spot.json",
        )

        first_half, second_half = summarize_regimes(replay)

        self.assertEqual(first_half.label, "first_half")
        self.assertEqual(second_half.label, "second_half")
        self.assertEqual(first_half.decisions + second_half.decisions, len(replay.decisions))


if __name__ == "__main__":
    unittest.main()
