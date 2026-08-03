from __future__ import annotations

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
