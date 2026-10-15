#!/usr/bin/env python3
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPORA = {"left", "right_trad", "qanon", "ufo", "scripture"}

class AlignmentArtifactTest(unittest.TestCase):
    def test_embedding_vectors_and_metrics(self):
        for name in CORPORA:
            rows = [json.loads(line) for line in (ROOT / "embeddings" / f"{name}.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), 60)
            for row in rows:
                self.assertEqual(len(row["vector"]), 300)
                self.assertTrue(math.isclose(sum(x * x for x in row["vector"]), 1.0, abs_tol=1e-9))
        metrics = json.loads((ROOT / "results" / "stage1-metrics.json").read_text())
        self.assertEqual(len(metrics["pairs"]), 10)
        self.assertEqual(set(metrics["personas"]), CORPORA)
        for pair in metrics["pairs"].values():
            self.assertEqual(len(pair["concordance"]), 10)
            self.assertGreaterEqual(pair["mean_anchor_cosine"], -1)
            self.assertLessEqual(pair["mean_anchor_cosine"], 1)

if __name__ == "__main__":
    unittest.main()
