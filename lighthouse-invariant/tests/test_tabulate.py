#!/usr/bin/env python3
"""Synthetic, hand-checkable audit for tabulate.py; no scipy and no results table generation."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tabulate  # noqa: E402


class TabulateAudit(unittest.TestCase):
    def test_hand_checked_rd_rr_ci(self):
        # Fixture groups are exactly 1/10 and 3/10 L occurrences.
        rows = tabulate.load_rows(ROOT / "tests/fixtures/tabulate-synthetic-coded.tsv")
        p1 = [r for r in rows if r["scope"] == "P1-world"]
        p3 = [r for r in rows if r["scope"] == "P3-open"]
        self.assertEqual(tabulate.count_occ(p1, "L"), (1, 10))
        self.assertEqual(tabulate.count_occ(p3, "L"), (3, 10))

        # Independently hand-calculated values (rounded from Newcombe Wilson and Katz+HA formula).
        rd, rd_lo, rd_hi = tabulate.risk_difference_ci(1, 10, 3, 10)
        rr, rr_lo, rr_hi = tabulate.risk_ratio_ci(1, 10, 3, 10)
        self.assertAlmostEqual(rd, -0.2, places=12)
        self.assertAlmostEqual(rd_lo, -0.585345640, places=8)
        self.assertAlmostEqual(rd_hi, 0.296358759, places=8)
        self.assertAlmostEqual(rr, 0.428571429, places=8)
        self.assertAlmostEqual(rr_lo, 0.076705055, places=8)
        self.assertAlmostEqual(rr_hi, 2.394541902, places=8)

    def test_input_set_digest_and_mismatch(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        raw = tmp / "runs/r/raw/P1_EN_none"
        raw.mkdir(parents=True)
        (raw / "1.txt").write_text("first", encoding="utf-8")
        (raw / "2.txt").write_text("second", encoding="utf-8")
        entries, digest = tabulate.raw_input_set(tmp, "r")
        tabulate.write_input_set(tmp, "r", entries, digest, "2026-08-06T00:00:00+00:00")
        tabulate.verify_input_set(tmp, "r")
        (raw / "2.txt").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "INPUT SET MISMATCH"):
            tabulate.verify_input_set(tmp, "r")


if __name__ == "__main__":
    unittest.main()
