#!/usr/bin/env python3
"""
灶台不変量 lane C — 盲目採点器.
PREREG.md §4 規約に従い runs/<runid>/raw/**/*.txt を採点 -> runs/<runid>/coded.tsv.

設計原則 (条件盲目):
  code_text(text, lexicon) は本文 str のみを受理する。ファイル名・パス・セル情報は
  一切渡さない。メタ情報 (persona/lang/head/scope) は parse_meta(path) が
  「採点とは独立の」関数としてパスのみから抽出する — 採点結果には影響しない。

カテゴリ: H,F,T,S (PREREG本体) + W,B,M,L,G,R,D,Sh,Fl,Bo (対照10種)。
出現(0/1) + 初出順位(rank, 全カテゴリ中で最も早く出たものが1) + 首位カテゴリ P。
H,S は "context_needed" 語彙 (campfire/stove/lighthouse等) を持ち、
近傍窓内に context_words が無ければ H は F へ、lighthouse-без-context は
どのカテゴリにも属さず ambiguous='?' として原文引用とともに残す
(捏造せず、人間レビュー用に可視化する)。
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

CATS = ["H", "F", "T", "S", "W", "B", "M", "L", "G", "R", "D", "Sh", "Fl", "Bo"]
LANGS = ["en", "de", "ja"]


def load_lexicon(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _compile_terms(terms, lang):
    """en/de: \\b境界付き大小無視. ja: 単純部分一致 (分かち書き無しのため)."""
    pats = []
    for t in terms:
        if lang == "ja":
            pats.append((t, re.compile(re.escape(t))))
        else:
            pats.append((t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)))
    return pats


def build_matcher(lexicon):
    """カテゴリ毎に (strong_patterns, context_needed_patterns, context_word_patterns) を作る."""
    matcher = {}
    for cat, spec in lexicon["categories"].items():
        strong = []
        for lang in LANGS:
            strong += [(lang, term, pat) for term, pat in _compile_terms(spec.get("strong", {}).get(lang, []), lang)]
        ctx_needed = []
        for lang in LANGS:
            ctx_needed += [(lang, term, pat) for term, pat in _compile_terms(spec.get("context_needed", {}).get(lang, []), lang)]
        ctx_words = []
        for lang in LANGS:
            ctx_words += [(lang, term, pat) for term, pat in _compile_terms(spec.get("context_words", {}).get(lang, []), lang)]
        matcher[cat] = {"strong": strong, "context_needed": ctx_needed, "context_words": ctx_words}
    return matcher


def _snippet(text, pos, endpos, width=40):
    a = max(0, pos - width)
    b = min(len(text), endpos + width)
    s = text[a:b].replace("\t", " ").replace("\n", " ⏎ ").strip()
    return s


def _has_context(text, pos, endpos, ctx_words, window):
    a = max(0, pos - window)
    b = min(len(text), endpos + window)
    win = text[a:b]
    for lang, term, pat in ctx_words:
        if pat.search(win):
            return True
    return False


def code_text(text, lexicon, matcher):
    """本文のみを受理. カテゴリ毎の occ/pos/ambig/quote を返す + P(首位) を導出.
    ファイル名・パス・セル情報は一切参照しない (条件盲目)。"""
    window = lexicon.get("context_window_chars", 80)
    raw_hits = {c: [] for c in CATS}  # list of (pos, endpos, quote, tier)
    ambiguous_notes = []  # (cat_or_none, quote) — どのカテゴリにも属さない曖昧例

    for cat in CATS:
        m = matcher[cat]
        for lang, term, pat in m["strong"]:
            for mo in pat.finditer(text):
                raw_hits[cat].append((mo.start(), mo.end(), _snippet(text, mo.start(), mo.end())))
        for lang, term, pat in m["context_needed"]:
            for mo in pat.finditer(text):
                ok = _has_context(text, mo.start(), mo.end(), m["context_words"], window)
                q = _snippet(text, mo.start(), mo.end())
                if ok:
                    raw_hits[cat].append((mo.start(), mo.end(), q))
                else:
                    if cat == "H":
                        # 中心性の文脈が無い炎語 -> F (非中心の火) へ機械的に回す
                        raw_hits["F"].append((mo.start(), mo.end(), q))
                    elif cat == "S":
                        # lighthouse等が信号文脈を欠く -> どのカテゴリでもない、曖昧として残す
                        ambiguous_notes.append((None, q))
                    else:
                        ambiguous_notes.append((cat, q))

    result = {}
    for cat in CATS:
        hits = raw_hits[cat]
        if hits:
            hits.sort(key=lambda h: h[0])
            pos, endpos, quote = hits[0]
            result[cat] = {"occ": 1, "pos": pos, "quote": quote, "ambig": 0}
        else:
            result[cat] = {"occ": 0, "pos": None, "quote": "", "ambig": 0}

    # このテキストに関連する曖昧注記 (S-lighthouse等) を最も近い該当欄へ付記
    # (どのカテゴリにも属さないため、専用の "_unclassified_ambiguous" として別立て)
    result["_unclassified_ambiguous"] = ambiguous_notes

    # 首位カテゴリ P: 全カテゴリ中、最も早く出現した (pos最小) もの
    occurred = [(c, result[c]["pos"]) for c in CATS if result[c]["occ"] == 1]
    if not occurred:
        P, P_ambig = "NONE", 0
    else:
        min_pos = min(p for _, p in occurred)
        tied = sorted(c for c, p in occurred if p == min_pos)
        if len(tied) > 1:
            P, P_ambig = "TIE:" + ",".join(tied), 1
        else:
            P, P_ambig = tied[0], 0

    # ランク (occurredをposで昇順ソート、1が最速)
    ranks = {}
    for rank, (c, p) in enumerate(sorted(occurred, key=lambda x: x[1]), start=1):
        ranks[c] = rank
    for cat in CATS:
        result[cat]["rank"] = ranks.get(cat, None)

    result["P"] = P
    result["P_ambig"] = P_ambig
    return result


def parse_meta(relpath):
    """パス文字列のみからセル情報を推定する。採点(code_text)には一切使わない —
    表作成(tabulate.py)のグルーピング用メタデータに限定する。"""
    tokens = re.split(r"[^a-z0-9]+", relpath.lower())
    tokens = [t for t in tokens if t]

    if "neutral" in tokens and "engineer" in tokens:
        persona = "neutral-engineer"
    elif "nyari" in tokens:
        persona = "nyari"
    elif "lampas" in tokens:
        persona = "lampas"
    elif "none" in tokens:
        persona = "none"
    else:
        persona = "unknown"

    if "en" in tokens or "english" in tokens:
        lang = "en"
    elif "de" in tokens or "german" in tokens or "deutsch" in tokens:
        lang = "de"
    elif "ja" in tokens or "japanese" in tokens:
        lang = "ja"
    else:
        lang = "unknown"

    if "codex" in tokens or "openai" in tokens:
        head = "openai-codex"
    elif "sonnet" in tokens or "anthropic" in tokens or "claude" in tokens:
        head = "anthropic-sonnet"
    else:
        head = "unknown"

    if "world" in tokens or "p1" in tokens:
        scope = "P1-world"
    elif "game" in tokens or "p2" in tokens:
        scope = "P2-game"
    elif "open" in tokens or "p3" in tokens:
        scope = "P3-open"
    else:
        scope = "unknown"

    return {"persona": persona, "lang": lang, "head": head, "scope": scope}


def find_runid(relpath):
    parts = Path(relpath).parts
    if "runs" in parts:
        i = parts.index("runs")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "unknown"


HEADER = (
    ["file", "run_id", "persona", "lang", "head", "scope"]
    + sum([[f"{c}_occ", f"{c}_pos", f"{c}_rank", f"{c}_ambig", f"{c}_quote"] for c in CATS], [])
    + ["P", "P_ambig", "unclassified_ambiguous_n", "unclassified_ambiguous_quotes"]
)


def code_file(path, base_dir, lexicon, matcher):
    text = path.read_text(encoding="utf-8", errors="replace")
    relpath = str(path.relative_to(base_dir))
    res = code_text(text, lexicon, matcher)
    meta = parse_meta(relpath)
    run_id = find_runid(str(path))

    row = [relpath, run_id, meta["persona"], meta["lang"], meta["head"], meta["scope"]]
    for c in CATS:
        r = res[c]
        row += [
            r["occ"],
            r["pos"] if r["pos"] is not None else "",
            r["rank"] if r["rank"] is not None else "",
            r["ambig"],
            r["quote"],
        ]
    unclass = res["_unclassified_ambiguous"]
    row += [res["P"], res["P_ambig"], len(unclass), " | ".join(q for _, q in unclass)]
    return row


def main():
    ap = argparse.ArgumentParser(description="PREREG §4 盲目採点器: runs/<runid>/raw -> coded.tsv")
    ap.add_argument("run_id", help="runs/<run_id>/raw/**/*.txt を採点")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent), help="hearth-invariant root")
    ap.add_argument("--lexicon", default=None)
    args = ap.parse_args()

    root = Path(args.root)
    lexicon_path = args.lexicon or (root / "scripts" / "lexicon.json")
    lexicon = load_lexicon(lexicon_path)
    matcher = build_matcher(lexicon)

    raw_dir = root / "runs" / args.run_id / "raw"
    if not raw_dir.exists():
        print(f"UNVERIFIED: raw dir not found: {raw_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(raw_dir.rglob("*.txt"))
    if not files:
        print(f"UNVERIFIED: no .txt files under {raw_dir}", file=sys.stderr)
        sys.exit(1)

    out_path = root / "runs" / args.run_id / "coded.tsv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(HEADER)
        for p in files:
            w.writerow(code_file(p, root, lexicon, matcher))

    print(f"coded {len(files)} files -> {out_path}")


if __name__ == "__main__":
    main()
