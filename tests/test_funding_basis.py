import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_scripts.funding_basis import (
    MarginAssumptions,
    MarginMode,
    build_funding_event,
    validate_trade_window,
    wick_stress,
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


if __name__ == "__main__":
    unittest.main()
