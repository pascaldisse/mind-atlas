#!/usr/bin/env python3
"""Measure the lighthouse concept cosine-distance matrix with macOS NLEmbedding."""
import argparse
import datetime as dt
import json
import math
import subprocess
import tempfile
from pathlib import Path

CONCEPTS = {
    "灯台": "lighthouse", "灯": "lamp", "守": "guard", "孤": "solitude",
    "愛": "love", "無": "nothingness", "塔": "tower", "井戸": "well",
    "市場": "market", "道": "road", "船": "ship", "海": "sea", "境界": "boundary",
}
MODEL = "Apple NaturalLanguage NLEmbedding.wordEmbedding(for: .english)"


def fetch_vectors(concepts):
    payload = json.dumps(concepts, ensure_ascii=False)
    swift = f'''import Foundation
import NaturalLanguage
let json = #"{payload}"#
let concepts = try! JSONSerialization.jsonObject(with: json.data(using: .utf8)!) as! [String: String]
guard let embedding = NLEmbedding.wordEmbedding(for: .english) else {{
    fputs("NLEmbedding English word model unavailable\\n", stderr); exit(2)
}}
for label in concepts.keys.sorted() {{
    let term = concepts[label]!
    guard let vector = embedding.vector(for: term) else {{
        fputs("missing embedding: \\(label) -> \\(term)\\n", stderr); exit(3)
    }}
    print(label + "\\t" + term + "\\t" + vector.map {{ String($0) }}.joined(separator: "\\t"))
}}
'''
    with tempfile.NamedTemporaryFile("w", suffix=".swift", encoding="utf-8") as source:
        source.write(swift); source.flush()
        run = subprocess.run(["swift", source.name], text=True, capture_output=True, check=False)
    if run.returncode:
        raise RuntimeError(f"swift embedding probe failed ({run.returncode}): {run.stderr.strip()}")
    vectors = {}
    for line in run.stdout.splitlines():
        label, term, *values = line.split("\t")
        vectors[label] = (term, [float(x) for x in values])
    if set(vectors) != set(concepts):
        raise RuntimeError(f"incomplete vector response: {sorted(vectors)}")
    dimensions = {len(vector) for _, vector in vectors.values()}
    if len(dimensions) != 1:
        raise RuntimeError(f"inconsistent dimensions: {dimensions}")
    return vectors, dimensions.pop()


def cosine_distance(left, right):
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left))
    norm_right = math.sqrt(sum(b * b for b in right))
    if not norm_left or not norm_right:
        raise ValueError("zero vector")
    return 1.0 - dot / (norm_left * norm_right)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("lighthouse-invariant/results/distance-matrix.tsv"))
    parser.add_argument("--manifest", type=Path, default=Path("lighthouse-invariant/results/distance-manifest.json"))
    args = parser.parse_args()
    vectors, dimension = fetch_vectors(CONCEPTS)
    labels = list(CONCEPTS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out:
        out.write("# true embedding; cosine distance = 1 - cosine similarity\n")
        out.write("concept\t" + "\t".join(labels) + "\n")
        for left in labels:
            out.write(left + "\t" + "\t".join(
                f"{cosine_distance(vectors[left][1], vectors[right][1]):.6f}" for right in labels
            ) + "\n")
    manifest = {
        "measured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "method": "true embedding; deterministic cosine distance",
        "model": MODEL,
        "language": "English word embeddings; Japanese labels translated before lookup",
        "dimension": dimension,
        "concept_to_embedding_token": {key: vectors[key][0] for key in labels},
        "matrix": str(args.output),
        "uncertainty": "No sampling occurred; a 95% CI is not defined for this deterministic model lookup.",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"model={MODEL}\ndimension={dimension}\nmatrix={args.output}\nmanifest={args.manifest}")


if __name__ == "__main__":
    main()
