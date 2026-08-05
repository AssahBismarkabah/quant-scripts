import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_scripts.buyback_timing.edgar import classify
from quant_scripts.buyback_timing.event_study import dedup_programs


class TestClassify(unittest.TestCase):
    def test_new_authorization_with_cap(self):
        txt = (
            "On March 1, the board authorized a new share repurchase program "
            "of up to $20.0 million of the Company's common stock."
        )
        is_new, reason = classify(txt)
        self.assertTrue(is_new)
        self.assertEqual(reason, "auth+cap")

    def test_plain_authorization(self):
        txt = "The board approved the repurchase of common stock pursuant to a new program."
        is_new, _ = classify(txt)
        self.assertTrue(is_new)

    def test_credit_agreement_not_a_buyback(self):
        txt = "Entered into a new $500 million credit agreement to fund operations."
        is_new, _ = classify(txt)
        self.assertFalse(is_new)

    def test_empty(self):
        is_new, reason = classify("")
        self.assertFalse(is_new)
        self.assertEqual(reason, "empty")


class TestDedupPrograms(unittest.TestCase):
    def _frame(self, cik, dates):
        return pd.DataFrame(
            {
                "cik": [cik] * len(dates),
                "ticker": ["X"] * len(dates),
                "announcement_date": dates,
            }
        )

    def test_collapses_routine_restatements(self):
        base = date(2026, 1, 5)
        dates = [base, base + timedelta(days=20), base + timedelta(days=40), base + timedelta(days=130)]
        df = self._frame("0000000001", dates)
        out = dedup_programs(df, gap_days=90)
        self.assertEqual(len(out), 2)  # day0 and day130 (>=90 apart)

    def test_keeps_distinct_issuers(self):
        base = date(2026, 1, 5)
        df = pd.concat(
            [self._frame("0000000001", [base]), self._frame("0000000002", [base])]
        )
        out = dedup_programs(df, gap_days=90)
        self.assertEqual(len(out), 2)


if __name__ == "__main__":
    unittest.main()
