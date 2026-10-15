#!/usr/bin/env python3
"""Combine vocab/*.json (one file per domain) into a single vocab.json.

Generated file — do not hand-edit vocab.json. Edit vocab/<domain>.json and
re-run this script instead. Fails loudly on duplicate ids.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB_DIR = ROOT / "vocab"
OUTPUT = ROOT / "vocab.json"


def load_domain_files(vocab_dir=VOCAB_DIR):
    files = sorted(p for p in vocab_dir.glob("*.json") if p.name != "vocab.json")
    if not files:
        raise SystemExit(f"no domain files found under {vocab_dir}")
    return files


COLLISION_LANGS = ("ja", "en", "de", "zh")


def _is_blank(value):
    return value is None or (isinstance(value, str) and not value.strip())


def compute_token_collisions(entries, langs=COLLISION_LANGS):
    """Per-language token collision groups, keyed by entry id.

    A collision = two or more entries sharing the same non-null token in
    the same language column. This is a structural fact about the lexicon
    (a genuine lexical gap, or a design-split concept pair), NOT itself a
    defect -- see vocab/SCHEMA.md `token_collision` field law. null tokens
    never participate (excluded before grouping, never inflate a count).

    Returns {id: {lang: [sorted group ids...]}} for ids that participate in
    at least one collision. ids with zero collisions are absent from the
    returned dict (caller should treat missing == None).
    """
    by_id_lang = {}
    for lang in langs:
        groups = {}
        for e in entries:
            v = e.get(lang)
            if _is_blank(v):
                continue
            groups.setdefault(v, []).append(e.get("id"))
        for ids in groups.values():
            if len(ids) < 2:
                continue
            group_sorted = sorted(ids)
            for eid in ids:
                by_id_lang.setdefault(eid, {})[lang] = group_sorted
    return by_id_lang


def build_merged(vocab_dir=VOCAB_DIR):
    """Merge vocab/<domain>.json files the same way main() writes vocab.json.

    Returns (merged_entries, files). Does not touch disk. Reused by
    validate_vocab.py's staleness and token_collision-consistency checks so
    the merge/collision logic lives in one place only.

    Attaches `token_collision` to every merged entry: None if the entry
    shares no language-column token with any other entry, else
    {lang: [sorted sibling ids incl. self]} for each language where it
    does. This field is generated -- never hand-write it into
    vocab/<domain>.json source files.
    """
    files = load_domain_files(vocab_dir)
    merged = []
    seen_ids = {}
    for path in files:
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path}: invalid JSON: {e}")
        if not isinstance(entries, list):
            raise SystemExit(f"{path}: expected a JSON array of entries")
        for entry in entries:
            eid = entry.get("id")
            if not eid:
                raise SystemExit(f"{path}: entry missing id: {entry}")
            if eid in seen_ids:
                raise SystemExit(
                    f"duplicate id '{eid}' in {path} (first seen in {seen_ids[eid]})"
                )
            seen_ids[eid] = path.name
            merged.append(entry)

    merged.sort(key=lambda e: (e.get("domain", ""), e.get("id", "")))
    collisions = compute_token_collisions(merged)
    for entry in merged:
        entry["token_collision"] = collisions.get(entry.get("id"))
    return merged, files


def main():
    merged, files = build_merged()
    OUTPUT.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(merged)} entries from {len(files)} domain files -> {OUTPUT}")
    per_domain = {}
    for e in merged:
        per_domain[e.get("domain", "?")] = per_domain.get(e.get("domain", "?"), 0) + 1
    for domain, count in sorted(per_domain.items()):
        print(f"  {domain}: {count}")


if __name__ == "__main__":
    main()
