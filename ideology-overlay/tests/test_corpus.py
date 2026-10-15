#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CorpusTest(unittest.TestCase):
    def test_schema_count_and_unique_ids(self):
        paths = sorted((ROOT / "corpus").glob("*.jsonl"))
        self.assertEqual({p.stem for p in paths}, {"left", "right_trad", "qanon", "ufo", "scripture"})
        for path in paths:
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 60, path)
            self.assertEqual(len({row["id"] for row in rows}), 60, path)
            for row in rows:
                self.assertEqual(set(row), {"id", "text", "source"})
                self.assertTrue(row["text"].strip())
                self.assertTrue(row["source"].startswith("http"))

if __name__ == "__main__":
    unittest.main()
