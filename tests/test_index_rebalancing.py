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
