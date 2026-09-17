from quant_scripts.niche_etf_nav import conservative_basket_value, executable_gap
import pandas as pd
import pytest
from quant_scripts.niche_etf_nav.audit import build_observability_report


def test_uses_ask_to_buy_and_bid_to_sell():
    basket = conservative_basket_value(
        [{"symbol": "AAA", "quantity": 2}], {"AAA": {"bid": 9.0, "ask": 11.0}}
    )
    assert basket.buy_value == 22.0
    assert basket.sell_value == 18.0
    assert executable_gap(etf_bid=19, etf_ask=21, basket=basket, costs=1)["long_etf_gap"] == -4.0


def test_missing_quote_blocks_executable_gap():
    basket = conservative_basket_value(
        [{"symbol": "AAA", "quantity": 1}, {"symbol": "BBB", "quantity": 1}],
        {"AAA": {"bid": 9.0, "ask": 10.0}},
    )
    assert basket.missing_symbols == ("BBB",)
    assert executable_gap(etf_bid=20, etf_ask=20, basket=basket, costs=0) == {
        "long_etf_gap": None,
        "long_basket_gap": None,
    }


def test_invalid_quote_is_not_treated_as_coverage():
    basket = conservative_basket_value(
        [{"symbol": "AAA", "quantity": 1}], {"AAA": {"bid": 11.0, "ask": 10.0}}
    )
    assert basket.missing_symbols == ("AAA",)


def test_observability_report_preserves_timestamps_and_blocks_incomplete_basket():
    report = build_observability_report(
        pd.DataFrame([{"symbol": "AAA", "quantity": 1, "holdings_ts": "2026-01-01T00:00:00Z"}]),
        pd.DataFrame([{"symbol": "AAA", "bid": 9, "ask": 10, "quote_ts": "2026-01-01T14:30:00Z"}]),
        pd.DataFrame([{"etf_bid": 11, "etf_ask": 12, "quote_ts": "2026-01-01T14:30:01Z"}]),
        costs=1,
    )
    assert report.loc[0, "executable"]
    assert report.loc[0, "holdings_ts_min"] == "2026-01-01T00:00:00+00:00"
    assert report.loc[0, "underlying_quote_ts_max"] == "2026-01-01T14:30:00+00:00"
    assert report.loc[0, "etf_quote_ts"] == "2026-01-01T14:30:01+00:00"


def test_observability_report_rejects_missing_schema():
    with pytest.raises(ValueError, match="quotes"):
        build_observability_report(
            pd.DataFrame([{"symbol": "AAA", "quantity": 1, "holdings_ts": "2026-01-01"}]),
            pd.DataFrame([{"symbol": "AAA"}]),
            pd.DataFrame([{"etf_bid": 11, "etf_ask": 12, "quote_ts": "2026-01-01"}]),
        )
