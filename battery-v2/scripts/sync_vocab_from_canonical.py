#!/usr/bin/env python3
"""
battery-v2 vocab canonical-sync. PREREG r3 §4.1 (vocab二重管理の解消)を実装。

法 (陰根L5監査 2026-08-06 20:30 CEST 判定、PREREG r3 に記録):
- 正典 = main の vocab.json (canonical concept list, id-keyed, ja/en/de/zh)。
- battery-v2 は並行 gloss 一覧を維持せず、正典を消費する。
- 食い違い: 正典に妥当な語がある → 正典を採る。旧gloss は notes に残す (両方記録)。
- 正典が null/欠落 → その言語basisからその概念を落とし、落としたことを記録する(黙って代替しない)。

Usage:
    python3 sync_vocab_from_canonical.py --canonical /path/to/main/vocab.json --out vocab.json
"""
import argparse
import hashlib
import json
import sys

# battery-v2の15概念: (JA表記, canonical id)。JA表記はquestions.json/basis表の参照キーとして維持。
CONCEPTS = [
    ("影", "shadow"),
    ("闇", "darkness"),
    ("光", "light"),
    ("愛", "love"),
    ("無", "nothingness"),
    ("棄", "abandonment"),
    ("月", "moon"),
    ("娘", "daughter"),
    ("夢", "dream"),
    ("生", "life"),
    ("死", "death"),
    ("王", "king"),
    ("女王", "queen"),
    ("母", "mother"),
    ("神", "god"),
]

OLD_GLOSS = {
    "影": {"EN": "shadow", "DE": "Schatten", "ZH": "影"},
    "闇": {"EN": "darkness", "DE": "Dunkelheit", "ZH": "黑暗"},
    "光": {"EN": "light", "DE": "Licht", "ZH": "光"},
    "愛": {"EN": "love", "DE": "Liebe", "ZH": "爱"},
    "無": {"EN": "nothingness", "DE": "Nichts", "ZH": "无"},
    "棄": {"EN": "abandonment", "DE": "Verlassenheit", "ZH": "抛弃"},
    "月": {"EN": "moon", "DE": "Mond", "ZH": "月亮"},
    "娘": {"EN": "daughter", "DE": "Tochter", "ZH": "女儿"},
    "夢": {"EN": "dream", "DE": "Traum", "ZH": "梦"},
    "生": {"EN": "life", "DE": "Leben", "ZH": "生"},
    "死": {"EN": "death", "DE": "Tod", "ZH": "死"},
    "王": {"EN": "king", "DE": "König", "ZH": "国王"},
    "女王": {"EN": "queen", "DE": "Königin", "ZH": "女王"},
    "母": {"EN": "mother", "DE": "Mutter", "ZH": "母亲"},
    "神": {"EN": "god", "DE": "Gott", "ZH": "神"},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True, help="path to main repo's canonical vocab.json")
    ap.add_argument("--canonical-sha", required=True, help="git commit sha of the canonical vocab.json being consumed")
    ap.add_argument("--out", default="vocab.json")
    args = ap.parse_args()

    with open(args.canonical, encoding="utf-8") as f:
        canonical_raw = f.read()
    canonical = json.loads(canonical_raw)
    canonical_sha256 = hashlib.sha256(canonical_raw.encode("utf-8")).hexdigest()
    by_id = {e["id"]: e for e in canonical}

    words = {}
    diff_log = []
    dropped = []

    for ja, cid in CONCEPTS:
        entry = by_id.get(cid)
        if entry is None:
            dropped.append({"ja": ja, "canonical_id": cid, "reason": "id not found in canonical vocab.json"})
            print(f"DROP {ja} ({cid}): not found in canonical", file=sys.stderr)
            continue

        record = {"canonical_id": cid, "token_collision": entry.get("token_collision")}
        old = OLD_GLOSS.get(ja, {})
        for lang_key, canon_key in (("EN", "en"), ("DE", "de"), ("ZH", "zh")):
            canon_val = entry.get(canon_key)
            if canon_val is None or canon_val == "":
                dropped.append({"ja": ja, "canonical_id": cid, "language": lang_key,
                                 "reason": "canonical value is null/empty for this language"})
                print(f"DROP {ja} ({cid}) [{lang_key}]: canonical null", file=sys.stderr)
                continue
            record[lang_key] = canon_val
            old_val = old.get(lang_key)
            if old_val is not None and old_val != canon_val:
                diff_log.append({
                    "ja": ja, "canonical_id": cid, "language": lang_key,
                    "old_gloss_ghoul_sonnet": old_val, "canonical": canon_val,
                })
        record["JA"] = entry.get("ja", ja)
        if entry.get("ja") and entry.get("ja") != ja:
            diff_log.append({
                "ja": ja, "canonical_id": cid, "language": "JA",
                "old_gloss_ghoul_sonnet": ja, "canonical": entry.get("ja"),
            })
        record["notes"] = f"old gloss (ghoul-sonnet, r1): EN={old.get('EN')} DE={old.get('DE')} ZH={old.get('ZH')}"
        words[ja] = record

    out = {
        "_comment": "battery-v2 vocab -- r3: consumes canonical main vocab.json (陰根L5監査 2026-08-06決定). No parallel gloss list maintained.",
        "_canonical_source": {
            "path": "~/projects/semantic-map/vocab.json (main branch)",
            "git_sha": args.canonical_sha,
            "file_sha256": canonical_sha256,
            "concept_count_in_canonical": len(canonical),
        },
        "_diff_log": diff_log,
        "_dropped": dropped,
        "_conflict_rule": "canonical wins when it has a valid value; old ghoul-sonnet gloss kept in notes for record, never used for measurement. canonical null/missing -> concept dropped from that language basis, recorded in _dropped, never silently substituted.",
        "words": words,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"wrote {args.out}: {len(words)} concepts, {len(diff_log)} diffs vs old gloss, {len(dropped)} dropped",
          file=sys.stderr)


if __name__ == "__main__":
    main()
