#!/usr/bin/env python3
"""Check whether each entry's `en` token has a real Apple NLEmbedding vector.

Mirrors the swift-subprocess pattern in
lighthouse-invariant/scripts/embed_distance.py. Never deletes entries; sets
`embed_en: true/false` in place on the domain JSON file(s) passed in (default:
vocab/*.json, excluding the generated vocab.json).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB_DIR = ROOT / "vocab"


def probe_tokens(tokens):
    """Return {token: bool} for whether NLEmbedding English word model has a vector."""
    unique = sorted(set(tokens))
    payload = json.dumps(unique, ensure_ascii=False)
    swift = f'''import Foundation
import NaturalLanguage
let json = #"{payload}"#
let tokens = try! JSONSerialization.jsonObject(with: json.data(using: .utf8)!) as! [String]
guard let embedding = NLEmbedding.wordEmbedding(for: .english) else {{
    fputs("NLEmbedding English word model unavailable\\n", stderr); exit(2)
}}
for token in tokens {{
    let has = embedding.vector(for: token) != nil
    print(token + "\\t" + (has ? "1" : "0"))
}}
'''
    with tempfile.NamedTemporaryFile("w", suffix=".swift", encoding="utf-8") as source:
        source.write(swift)
        source.flush()
        run = subprocess.run(["swift", source.name], text=True, capture_output=True, check=False)
    if run.returncode:
        raise RuntimeError(f"swift embedding probe failed ({run.returncode}): {run.stderr.strip()}")
    result = {}
    for line in run.stdout.splitlines():
        token, flag = line.rsplit("\t", 1)
        result[token] = flag == "1"
    missing = unique_missing = set(unique) - set(result)
    if missing:
        raise RuntimeError(f"probe returned no line for tokens: {missing}")
    return result


def first_token(en_gloss):
    """NLEmbedding is single-word; use the first whitespace token of `en`."""
    return en_gloss.strip().split()[0].lower() if en_gloss and en_gloss.strip() else en_gloss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="vocab domain json files to check (default: vocab/*.json)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report coverage without writing files"
    )
    args = parser.parse_args()
    paths = args.paths or sorted(
        p for p in VOCAB_DIR.glob("*.json") if p.name != "vocab.json"
    )
    if not paths:
        print(f"no vocab files found under {VOCAB_DIR}", file=sys.stderr)
        sys.exit(1)

    all_data = {}
    all_tokens = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        all_data[path] = data
        for e in data:
            all_tokens.append(first_token(e.get("en")))

    vectors = probe_tokens([t for t in all_tokens if t])

    hits = misses = 0
    miss_list = []
    for path, data in all_data.items():
        for e in data:
            token = first_token(e.get("en"))
            has = bool(vectors.get(token, False))
            e["embed_en"] = has
            if has:
                hits += 1
            else:
                misses += 1
                miss_list.append(f"{e.get('id')} ({e.get('en')!r} -> token {token!r})")
        if not args.dry_run:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    total = hits + misses
    coverage = (hits / total * 100) if total else 0.0
    print(f"checked {total} entries across {len(paths)} file(s)")
    print(f"embed_en=true: {hits} ({coverage:.1f}%)")
    print(f"embed_en=false: {misses}")
    if miss_list:
        print("misses:")
        for m in miss_list:
            print(f"  {m}")


if __name__ == "__main__":
    main()
