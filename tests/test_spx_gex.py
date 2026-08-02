from __future__ import annotations

from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from pathlib import Path
import json
import sys

from quant_scripts.spx_gex import (
    GEXContract,
    GEXRegime,
    IntradayBar,
    SPXGEXBacktest,
    build_gex_data_point,
    calculate_dealer_gex,
    classify_regime,
)
from quant_scripts.spx_gex.io import load_gex_point, sample_csv_payload, sample_input_payload, summarize_input
from quant_scripts.spx_gex.cli import build_parser
from quant_scripts.spx_gex.backtest import run_walk_forward, write_backtest_report
from quant_scripts.spx_gex.cboe import load_cboe_export
from quant_scripts.spx_gex.databento import load_spy_intraday_bars
from quant_scripts.spx_gex.databento_options import load_optionsdx_chain, merge_optionsdx_with_open_interest


def test_calculate_dealer_gex_inverts_aggregate_sign() -> None:
    point = build_gex_data_point(
        snapshot_time=datetime(2026, 8, 1, 15, 45, tzinfo=timezone.utc),
        underlying_symbol="SPX",
        underlying_price=5000.0,
        contracts=[
            GEXContract("call", 5000.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 1000.0, 0.02),
            GEXContract("put", 4950.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 800.0, 0.018),
        ],
    )

    dealer_gex = calculate_dealer_gex(point)

    assert dealer_gex < 0
    assert classify_regime(dealer_gex) is GEXRegime.NEGATIVE


def test_calculate_dealer_gex_excludes_0dte() -> None:
    point = build_gex_data_point(
        snapshot_time=datetime(2026, 8, 1, 15, 45, tzinfo=timezone.utc),
        underlying_symbol="SPX",
        underlying_price=5000.0,
        contracts=[
            GEXContract("call", 5000.0, datetime(2026, 8, 1, 16, 0, tzinfo=timezone.utc), 1000.0, 0.02),
            GEXContract("put", 4950.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 800.0, 0.018),
        ],
    )

    dealer_gex = calculate_dealer_gex(point)

    assert dealer_gex == -(0.018 * 800.0 * 100.0 * (5000.0**2) * 0.01)


def test_backtest_uses_midday_window() -> None:
    point = build_gex_data_point(
        snapshot_time=datetime(2026, 8, 1, 15, 45, tzinfo=timezone.utc),
        underlying_symbol="SPX",
        underlying_price=5000.0,
        contracts=[
            GEXContract("put", 4950.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 1200.0, 0.02),
        ],
    )
    bars = [
        IntradayBar(datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc), 5000.0, 5010.0, 4990.0, 5000.0),
        IntradayBar(datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc), 5000.0, 5020.0, 4995.0, 5010.0),
        IntradayBar(datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc), 5010.0, 5025.0, 5005.0, 5020.0),
    ]

    backtest = SPXGEXBacktest()
    results = backtest.run(
        point=point,
        bars=bars,
        lookback_start_time=datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc),
        evaluation_time=datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
        entry_time=datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
        exit_time=datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc),
    )

    assert results
    assert results[0].accepted is True
    assert results[0].decision.regime is GEXRegime.POSITIVE


def test_load_gex_point_reads_json_fixture() -> None:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sample.json"
        path.write_text(
            json.dumps(
                {
                    "snapshot_time": "2026-08-01T15:45:00+00:00",
                    "underlying_symbol": "SPX",
                    "underlying_price": 5000.0,
                    "exclude_0dte": True,
                    "contracts": [
                        {
                            "option_type": "call",
                            "strike": 5000.0,
                            "expiration": "2026-08-02T00:00:00+00:00",
                            "open_interest": 1000.0,
                            "gamma": 0.02,
                        }
                    ],
                    "bars": [
                        {
                            "ts": "2026-08-01T11:30:00+00:00",
                            "open": 5000.0,
                            "high": 5010.0,
                            "low": 4990.0,
                            "close": 5000.0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        point, bars = load_gex_point(path)

    assert point.underlying_symbol == "SPX"
    assert len(point.contracts) == 1
    assert len(bars) == 1


def test_sample_input_payload_contains_expected_keys() -> None:
    payload = sample_input_payload()

    assert payload["underlying_symbol"] == "SPX"
    assert "contracts" in payload
    assert "bars" in payload


def test_summarize_input_reports_dealer_gex() -> None:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sample.json"
        path.write_text(json.dumps(sample_input_payload()), encoding="utf-8")

        summary = summarize_input(path)

    assert summary["underlying_symbol"] == "SPX"
    assert summary["contract_count"] == 1
    assert summary["bar_count"] == 3
    assert summary["regime"] in {"positive", "negative", "flat"}


def test_load_gex_point_supports_csv() -> None:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sample.csv"
        path.write_text(sample_csv_payload(), encoding="utf-8")

        point, bars = load_gex_point(path)

    assert point.underlying_symbol == "SPX"
    assert len(point.contracts) == 1
    assert len(bars) == 3


def test_load_cboe_export_normalizes_vendor_columns() -> None:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "cboe.csv"
        path.write_text(
            "Quote Date,Underlying Symbol,Active Underlying Price 1545,Option Type,Strike,Expiration,Open Interest,Gamma 1545\n"
            "2026-08-01,SPX,5000.0,call,5000.0,2026-08-02,1000,0.02\n",
            encoding="utf-8",
        )

        point = load_cboe_export(path)

    assert point.underlying_symbol == "SPX"
    assert point.underlying_price == 5000.0
    assert len(point.contracts) == 1


def test_load_spy_intraday_bars_supports_databento_shape() -> None:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "spy_bars.json"
        path.write_text(
            json.dumps(
                {
                    "symbol": "SPY",
                    "bars": [
                        {
                            "ts": "2026-08-01T13:30:00+00:00",
                            "open": 500.0,
                            "high": 501.0,
                            "low": 499.5,
                            "close": 500.5,
                        },
                        {
                            "ts": "2026-08-01T11:30:00+00:00",
                            "open": 499.0,
                            "high": 500.0,
                            "low": 498.0,
                            "close": 499.5,
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        bars = load_spy_intraday_bars(path)

    assert len(bars) == 2
    assert bars[0].ts.isoformat() == "2026-08-01T11:30:00+00:00"
    assert bars[1].close == 500.5


def test_merge_optionsdx_chain_with_open_interest() -> None:
    with TemporaryDirectory() as tmpdir:
        chain_path = Path(tmpdir) / "spx_eod_202301.txt"
        oi_path = Path(tmpdir) / "oi.csv"
        chain_path.write_text(
            "[QUOTE_UNIXTIME], [QUOTE_READTIME], [QUOTE_DATE], [QUOTE_TIME_HOURS], [UNDERLYING_LAST], [EXPIRE_DATE], [EXPIRE_UNIX], [DTE], [C_DELTA], [C_GAMMA], [C_VEGA], [C_THETA], [C_RHO], [C_IV], [C_VOLUME], [C_LAST], [C_SIZE], [C_BID], [C_ASK], [STRIKE], [P_BID], [P_ASK], [P_SIZE], [P_LAST], [P_DELTA], [P_GAMMA], [P_VEGA], [P_THETA], [P_RHO], [P_IV], [P_VOLUME], [STRIKE_DISTANCE], [STRIKE_DISTANCE_PCT]\n"
            "1672866000, 2023-01-04 16:00, 2023-01-04, 16.000000, 3853.390000, 2023-01-05, 1672952400, 1.000000, 0.100000, 0.020000, 0.000000, 0.000000, 0.000000, , 1.000000, 3041.370000, 7 x 7, 2846.800000, 2848.300000, 1000.000000, 0.000000, 0.050000, 0 x 272, 0.030000, 0.000000, 0.000000, 0.000230, -0.024810, -0.000330, 8.175360, 7.000000, 2853.400000, 0.740000\n",
            encoding="utf-8",
        )
        oi_path.write_text(
            "option_type,strike,expiration,open_interest\n"
            "call,1000,2023-01-05,250\n"
            "put,1000,2023-01-05,150\n",
            encoding="utf-8",
        )

        point = merge_optionsdx_with_open_interest(chain_path, oi_path)

    assert point.underlying_symbol == "SPX"
    assert len(point.contracts) == 2
    assert point.contracts[0].open_interest == 250.0
    assert point.contracts[1].open_interest == 150.0


def test_run_walk_forward_summarizes_multiple_sessions() -> None:
    session_payload = sample_input_payload()
    with TemporaryDirectory() as tmpdir:
        path1 = Path(tmpdir) / "sample1.json"
        path2 = Path(tmpdir) / "sample2.json"
        path1.write_text(json.dumps(session_payload), encoding="utf-8")
        path2.write_text(json.dumps(session_payload), encoding="utf-8")
        point1, bars1 = load_gex_point(path1)
        point2, bars2 = load_gex_point(path2)

        _, summary = run_walk_forward(
            [
                (
                    point1,
                    bars1,
                    datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc),
                    datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
                    datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
                    datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc),
                ),
                (
                    point2,
                    bars2,
                    datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc),
                    datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
                    datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
                    datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc),
                ),
            ]
        )

    assert summary.sessions == 2
    assert summary.trades == 2


def test_write_backtest_report_persists_json() -> None:
    point = build_gex_data_point(
        snapshot_time=datetime(2026, 8, 1, 15, 45, tzinfo=timezone.utc),
        underlying_symbol="SPX",
        underlying_price=5000.0,
        contracts=[
            GEXContract("put", 4950.0, datetime(2026, 8, 2, tzinfo=timezone.utc), 1200.0, 0.02),
        ],
    )
    bars = [
        IntradayBar(datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc), 5000.0, 5010.0, 4990.0, 5000.0),
        IntradayBar(datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc), 5000.0, 5020.0, 4995.0, 5010.0),
        IntradayBar(datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc), 5010.0, 5025.0, 5005.0, 5020.0),
    ]
    backtest = SPXGEXBacktest()
    backtest.run(
        point=point,
        bars=bars,
        lookback_start_time=datetime(2026, 8, 1, 11, 30, tzinfo=timezone.utc),
        evaluation_time=datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
        entry_time=datetime(2026, 8, 1, 13, 30, tzinfo=timezone.utc),
        exit_time=datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc),
    )

    with TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "report.json"
        write_backtest_report(output, backtest, backtest.summarize())
        payload = json.loads(output.read_text(encoding="utf-8"))

    assert "summary" in payload
    assert "results" in payload
