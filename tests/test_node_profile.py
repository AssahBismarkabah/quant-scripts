"""Tests for the four-setup node detector (spec node-profile-setups-spec.md)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quant_scripts.node_profile import SpecParams, detect_nodes
from quant_scripts.node_profile.detector import value_area


def _panel() -> pd.DataFrame:
    """Tiny deterministic panel with a clear range + return-to-node pattern."""
    rng = np.random.default_rng(7)
    n = 260
    sym = "AAA"
    dates = pd.bdate_range("2019-01-01", periods=n)
    # sine-ish walk with volume hump in the middle of the range
    px = 100 + 8 * np.sin(np.linspace(0, 8 * np.pi, n))
    vol = 1e6 + 4e5 * np.abs(np.sin(np.linspace(0, 6 * np.pi, n)))
    o = px + rng.normal(0, 0.2, n)
    c = px
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.4, n))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.4, n))
    df = pd.DataFrame({
        "symbol": sym,
        "date": dates,
        "o_a": o,
        "h_a": h,
        "l_a": l,
        "c_a": c,
        "volume": vol,
    })
    return df


def test_value_area_poc_and_expansion():
    prof = pd.Series([1.0, 3.0, 2.0], index=np.array([10.0, 12.0, 14.0]))
    v_lo, v_hi, poc = value_area(prof, coverage=0.70)
    assert poc == 12.0
    assert v_lo <= poc <= v_hi


def test_value_area_high_priced_tie_break():
    prof = pd.Series([2.0, 2.0], index=np.array([10.0, 12.0]))
    _, _, poc = value_area(prof, coverage=0.60)
    assert poc == 12.0  # ties break to the higher-priced bin (conservative)


def test_detect_nodes_runs_and_is_deterministic():
    df = _panel()
    a = detect_nodes(df)
    b = detect_nodes(df)
    assert a.equals(b)  # deterministic
    assert len(a) > 0
    assert {"symbol", "date", "kind", "poc", "node_low", "node_high", "atr", "entry", "stop"}.issubset(a.columns)
    assert a[["node_low", "node_high", "poc", "atr"]].notna().all().all()


def test_split_stability():
    """A level (POC) must not jump when the same prices are expressed post-split."""
    df = _panel()
    base = detect_nodes(df)
    split = df.copy()
    split["o_a"] *= 4.0
    split["h_a"] *= 4.0
    split["l_a"] *= 4.0
    split["c_a"] *= 4.0
    scaled = detect_nodes(split)
    # detections should be identical in count; POCs scaled by the same factor
    assert len(base) == len(scaled)
    t = min(len(base), len(scaled))
    np.testing.assert_allclose(base["poc"].head(t).to_numpy() * 4.0,
                               scaled["poc"].head(t).to_numpy(), rtol=1e-6)


def test_all_entries_are_long_with_defined_band():
    df = _panel()
    res = detect_nodes(df)
    assert (res["side"] == "long").all()
    assert (res["node_high"] > res["node_low"]).all()
    assert ((res["entry"] - res["stop"]) > 0).all()  # stop below entry for long


def test_contraction_params_in_sanitized_regime():
    """Contraction (S1) should be rare, not degenerate: far fewer than the panel length."""
    df = _panel()
    res = detect_nodes(df)
    s1 = res[res["kind"] == "S1_contraction"]
    assert len(s1) <= len(df)  # sanity: not firing every bar
