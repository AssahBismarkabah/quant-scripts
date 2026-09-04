import pandas as pd

from quant_scripts.es_value_area.profile import compute_profile
from quant_scripts.es_value_area.backtest import classify_opening


def test_profile_expands_from_poc_to_seventy_percent():
    bars = pd.DataFrame({
        "close": [100.10, 100.10, 100.35, 99.85],
        "volume": [40, 40, 10, 10],
    })
    result = compute_profile(bars)
    assert result["poc"] == 100.125
    assert result["val"] == 100.0
    assert result["vah"] == 100.25


def test_empty_profile_is_nan():
    result = compute_profile(pd.DataFrame(columns=["close", "volume"]))
    assert pd.isna(result["poc"])
    assert pd.isna(result["vah"])
    assert pd.isna(result["val"])


def test_opening_state_requires_three_of_four_closes():
    assert classify_opening([100, 100.25, 100.4, 99], 99.5, 100.5) == "IN_VALUE"
    assert classify_opening([101, 101.25, 101.5, 100], 99.5, 100.5) == "OUT_ABOVE"
    assert classify_opening([99, 99.25, 99.4, 100], 99.5, 100.5) == "OUT_BELOW"
    assert classify_opening([99, 101, 100, 100], 99.5, 100.5) == "UNCLASSIFIED"
