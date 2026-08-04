from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from quant_scripts.index_rebalancing.models import ReasonCategory, Venue
from quant_scripts.index_rebalancing.spdji import (
    classify_reason,
    parse_release_body,
    parse_release_page,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "spdji"

# Real release: https://press.spglobal.com/2024-11-21-Texas-Pacific-Land-Set-to-Join-S-P-500,-Mueller-Industries-to-Join-S-P-MidCap-400-and-Atlas-Energy-Solutions-to-Join-S-P-SmallCap-600
# Saved from the live archive on 2026-08-03. Chain: TPL->S&P500, MRO out;
# MLI->S&P MidCap 400, TPL out; AESI->S&P SmallCap 600, MLI out. Effective 2024-11-26.


def test_parse_release_body_extracts_effective_date() -> None:
    html = (FIXTURE_DIR / "tpl_2024-11-21.html").read_text(encoding="utf-8")
    parsed = parse_release_body(html)
    assert parsed["effective_date"] == date(2024, 11, 26)


def test_parse_release_body_extracts_full_chain() -> None:
    html = (FIXTURE_DIR / "tpl_2024-11-21.html").read_text(encoding="utf-8")
    chain = parse_release_body(html)["chain"]
    by_key = {(c["venue"], c["ticker"]) for c in chain}
    expected = {
        (Venue.SP500, "TPL"),
        (Venue.SP500, "MRO"),
        (Venue.SP400, "MLI"),
        (Venue.SP400, "TPL"),
        (Venue.SP600, "AESI"),
        (Venue.SP600, "MLI"),
    }
    assert by_key == expected
    actions = {(c["ticker"], c["action"]) for c in chain}
    assert ("TPL", "addition") in actions
    assert ("MRO", "deletion") in actions


def test_parse_release_page_extracts_links() -> None:
    html = """<html><a href="https://press.spglobal.com/2025-02-10-Acushnet-Holdings-Set-to-Join-S-P-SmallCap-600">Acushnet Holdings Set to Join S&P SmallCap 600</a>
    <a href="https://press.spglobal.com/2024-11-21-Texas-Pacific-Land-Set-to-Join-S-P-500-Mueller-Industries-to-Join-S-P-MidCap-400-and-Atlas-Energy-Solutions-to-Join-S-P-SmallCap-600">Texas Pacific Land Set to Join S&P 500</a></html>"""
    page = Path("/tmp/test_spdji_page.html")
    page.write_text(html, encoding="utf-8")
    links = parse_release_page(page)
    assert links[0]["announcement_date"] == date(2025, 2, 10)
    assert "Acushnet" in links[0]["title"]
    assert links[1]["announcement_date"] == date(2024, 11, 21)


def test_classify_reason_ma() -> None:
    assert classify_reason("ConocoPhillips is acquiring Marathon Oil in a deal expected to close") is ReasonCategory.M_A


def test_classify_reason_discretionary() -> None:
    assert (
        classify_reason(
            "Texas Pacific Land and Mueller Industries have company level market capitalizations more representative of the large-cap market space"
        )
        is ReasonCategory.DISCRETIONARY
    )


WIKI_CHANGES_FIXTURE = """<table>
<tr><th>Date</th><th>Added</th><th>Removed</th><th>Reason</th></tr>
<tr><th>Ticker</th><th>Security</th><th>Ticker</th><th>Security</th></tr>
<tr><td>November 26, 2024</td><td>MLI</td><td>Mueller Industries</td><td>TPL</td><td>Texas Pacific Land</td><td>S&amp;P 500 constituent Berkshire Hathaway acquired Taylor Morrison</td></tr>
<tr><td>June 24, 2024</td><td>TPL</td><td>Texas Pacific Land</td><td></td><td></td><td>Market cap</td></tr>
</table>"""


def test_reconcile_confirm_and_conflict() -> None:
    from tempfile import TemporaryDirectory

    from quant_scripts.index_rebalancing.models import EventAction, EventStatus, IndexEvent
    from quant_scripts.index_rebalancing.reconcile import reconcile

    events = [
        IndexEvent(
            venue=Venue.SP400,
            ticker="TPL",
            company_name="Texas Pacific Land",
            action=EventAction.DELETION,
            announcement_date=date(2024, 11, 21),
            effective_date=date(2024, 11, 26),
            reason_category=ReasonCategory.DISCRETIONARY,
            reason_source="spdji_text",
            source_primary="spdji_press",
            sources=("spdji_press",),
            status=EventStatus.UNVERIFIED,
        )
    ]
    cross_rows = [
        {"ticker": "TPL", "action": "deletion", "date": date(2024, 11, 26), "reason": ReasonCategory.DISCRETIONARY},
        {"ticker": "MRO", "action": "deletion", "date": date(2024, 11, 26), "reason": ReasonCategory.M_A},
    ]
    with TemporaryDirectory() as tmp:
        out = reconcile(events, cross_rows, log_path=Path(tmp) / "cleaning_log.jsonl")
        assert out[0].status is EventStatus.CONFIRMED
        assert "cross_sources" in out[0].sources

        # conflicting reason -> reconciled + excluded
        events2 = [
            IndexEvent(
                venue=Venue.SP500,
                ticker="MRO",
                company_name="Marathon Oil",
                action=EventAction.DELETION,
                announcement_date=date(2024, 11, 21),
                effective_date=date(2024, 11, 26),
                reason_category=ReasonCategory.DISCRETIONARY,
                reason_source="spdji_text",
                source_primary="spdji_press",
                sources=("spdji_press",),
                status=EventStatus.UNVERIFIED,
            )
        ]
        out2 = reconcile(events2, cross_rows, log_path=Path(tmp) / "cleaning_log.jsonl")
        assert out2[0].status is EventStatus.RECONCILED
        assert out2[0].reason_category is ReasonCategory.M_A


def test_parse_russell_pdf_2025_deletions() -> None:
    """Real weekly list (2025-06-20) parsed: 155 rows, correct header skip."""
    from quant_scripts.index_rebalancing.ftse import parse_russell_pdf

    rows = parse_russell_pdf(Path(__file__).parent / "fixtures" / "ftse" / "ru3000-dels-2025.pdf")
    assert len(rows) > 100
    assert {"ticker": "DIBS", "company_name": "1STDIBS.COM"} in rows
    assert all(re.match(r"^[A-Z0-9.\-]{1,6}$", r["ticker"]) for r in rows)


def test_validate_r2000_counts_2025_within_tolerance() -> None:
    from quant_scripts.index_rebalancing.ftse import validate_r2000_counts

    adds = [{"ticker": f"X{i}", "company_name": f"C{i}"} for i in range(228)]
    dels = [{"ticker": f"Y{i}", "company_name": f"D{i}"} for i in range(154)]
    result = validate_r2000_counts(adds, dels, 2025)
    assert result["within_tolerance"] is True
    assert result["add_diff_pct"] <= 2.0


def test_validate_r2000_counts_breaks_on_big_gap() -> None:
    from quant_scripts.index_rebalancing.ftse import validate_r2000_counts

    adds = [{"ticker": f"X{i}", "company_name": f"C{i}"} for i in range(10)]
    dels = [{"ticker": f"Y{i}", "company_name": f"D{i}"} for i in range(10)]
    result = validate_r2000_counts(adds, dels, 2025)
    assert result["within_tolerance"] is False


def test_friction_costs_are_monotonic_in_stress() -> None:
    from quant_scripts.index_rebalancing.config import FrictionSettings
    from quant_scripts.index_rebalancing.friction import total_cost_bps
    from quant_scripts.index_rebalancing.models import EventAction

    s = FrictionSettings()
    base = total_cost_bps(EventAction.DELETION, 100.0, 101.0, 20, stress=False, settings=s)
    stress = total_cost_bps(EventAction.DELETION, 100.0, 101.0, 20, stress=True, settings=s)
    assert stress > base
    # short leg adds borrow cost
    short = total_cost_bps(EventAction.ADDITION, 100.0, 99.0, 20, stress=False, settings=s)
    assert short > base


def test_friction_borrow_filter() -> None:
    from quant_scripts.index_rebalancing.config import FrictionSettings
    from quant_scripts.index_rebalancing.friction import is_hard_to_borrow

    s = FrictionSettings(borrow_fee_cap_bps=300.0)
    assert is_hard_to_borrow(500.0, settings=s)
    assert not is_hard_to_borrow(200.0, settings=s)


def test_event_study_window_returns_and_no_lookahead() -> None:
    from tempfile import TemporaryDirectory

    import pandas as pd

    from quant_scripts.index_rebalancing.config import FrictionSettings, StudySettings
    from quant_scripts.index_rebalancing.event_study import compute_window_returns
    from quant_scripts.index_rebalancing.models import EventAction, ExitReason

    cal = [date(2024, 11, 1) + __import__("datetime").timedelta(days=i) for i in range(100)]
    with TemporaryDirectory() as tmp:
        bars_dir = Path(tmp)
        # synthetic stock: flat at 100 through 2024-11-16, then drops 5% and
        # stays there (entry 11-06 at 100; 10d exit 11-16 at 100; 20d exit 11-26 at 95)
        n = 100
        closes = [100.0] * 16 + [95.0] * (n - 16)
        df = pd.DataFrame(
            {
                "open": closes,
                "high": [c * 1.01 for c in closes],
                "low": [c * 0.99 for c in closes],
                "close": closes,
                "volume": [1_000_000] * n,
            },
            index=pd.DatetimeIndex(cal),
        )
        df.index.name = "ts_date"
        df.to_parquet(bars_dir / "DELX.parquet")
        events = pd.DataFrame(
            [
                {
                    "event_id": "e1",
                    "venue": "sp600",
                    "ticker": "DELX",
                    "action": "deletion",
                    "effective_date": date(2024, 11, 5),
                    "announcement_date": date(2024, 11, 1),
                }
            ]
        )
        settings = StudySettings(data_end=date(2024, 12, 1))
        results = compute_window_returns(
            events, bars_dir, cal, settings, FrictionSettings()
        )
        # entry must be strictly after effective date (2024-11-05 -> 2024-11-06)
        assert all(r.entry_date > date(2024, 11, 5) for r in results)
        # 10-day window: entry 11-06, exit 11-16 (both flat at 100) -> gross 0
        r10 = [r for r in results if r.window_td == 10][0]
        assert r10.exit_reason is ExitReason.WINDOW_END
        assert r10.gross_bps == 0.0
        # 20-day window: exit 11-26 at 95 -> full 5% drop captured
        r20 = [r for r in results if r.window_td == 20][0]
        assert r20.gross_bps <= -300.0
        # 60-day window: exits after 2024-12-01 -> completed False (data_end)
        r60 = [r for r in results if r.window_td == 60]
        assert len(r60) == 1
        assert r60[0].completed is False


def test_parse_wikipedia_changes_extracts_additions_and_deletions() -> None:
    from quant_scripts.index_rebalancing.crossvalidate import parse_wikipedia_changes

    rows = parse_wikipedia_changes(WIKI_CHANGES_FIXTURE, Venue.SP400)
    by_key = {(r["ticker"], r["action"], r["date"]) for r in rows}
    assert ("MLI", "addition", date(2024, 11, 26)) in by_key
    assert ("TPL", "deletion", date(2024, 11, 26)) in by_key
    assert ("TPL", "addition", date(2024, 6, 24)) in by_key
    mli = [r for r in rows if r["ticker"] == "MLI"][0]
    assert mli["reason"] is ReasonCategory.M_A  # reason text mentions acquisition
    tpl_add = [r for r in rows if r["ticker"] == "TPL" and r["action"] == "addition"][0]
    assert tpl_add["reason"] is ReasonCategory.DISCRETIONARY  # 'Market cap'
