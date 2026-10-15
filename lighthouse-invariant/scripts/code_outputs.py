#!/usr/bin/env python3
"""
灯台不変量 lane C — 盲目採点器 (PREREG r2 §4).
runs/<runid>/raw/<CELL>/<i>.txt を採点 -> runs/<runid>/coded.tsv.

条件盲目設計:
  code_text(text, ...) は本文 str のみを受理する。ファイル名・パス・manifest情報は
  一切渡さない。メタ情報 (persona/lang/scope/head) は parse_meta()/manifest.json
  読取りという「採点とは独立の」経路で決まる — 採点結果には影響しない。

標的 L 灯台 (複合): 塔+光+航行合図の三要素。
  - 文字通りの灯台語 (lighthouse, Leuchtturm, 灯台 等) は語自体が三要素を包含 -> L=1直接。
  - 文字通りの語が無くても、汎用の塔語(T)・光語(Li)・信号語(S)が近傍
    (composite_window_chars) で共起すれば L=1 (ambig=1, 合成検出である旨を明示)。
    この時、消費された T/Li/S の当該出現は単独カテゴリからは除外する
    (H0-decomp: T単独率・(Li+S)単独率を汚染しないため)。
  - 消費されなかった T/Li/S は単独カテゴリとしてそのまま記録する。
対照: H(旧標的,降格) · W · B · M · Lb(図書館) · G · R · D · Sh · Fl · Bo(舟/港)。
Bo は L との共起prime分析用 (PREREG §4 注)。
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

# 出力・ランキング対象の全カテゴリ順序 (target複合L, 部分一致T/Li/S, 対照11)
CATS = ["L", "T", "Li", "S", "H", "W", "B", "M", "Lb", "G", "R", "D", "Sh", "Fl", "Bo", "Sea"]
LANGS = ["en", "de", "ja"]


def load_lexicon(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _compile_terms(terms, lang):
    pats = []
    for t in terms:
        if lang == "ja":
            pats.append((t, re.compile(re.escape(t))))
        else:
            pats.append((t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)))
    return pats


def build_matcher(lexicon):
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

    tc = lexicon.get("target_composite", {}).get("strong", {})
    l_literal = []
    for lang in LANGS:
        l_literal += [(lang, term, pat) for term, pat in _compile_terms(tc.get(lang, []), lang)]
    matcher["_L_literal"] = {"strong": l_literal, "context_needed": [], "context_words": []}

    # r4: composite-L の maritime 要件 (陰根監査 FAIL-2)
    mar = lexicon.get("target_composite", {}).get("maritime", {})
    mar_pats = []
    for lang in LANGS:
        mar_pats += [(lang, term, pat) for term, pat in _compile_terms(mar.get(lang, []), lang)]
    matcher["_L_maritime"] = {"strong": mar_pats, "context_needed": [], "context_words": []}
    return matcher


def _snippet(text, pos, endpos, width=40):
    a = max(0, pos - width)
    b = min(len(text), endpos + width)
    s = text[a:b].replace("\t", " ").replace("\n", " ⏎ ").strip()
    return s


def _find_all(text, pats):
    """pats: list of (lang, term, compiled). -> list of (pos, end, quote) sorted."""
    out = []
    for lang, term, pat in pats:
        for mo in pat.finditer(text):
            out.append([mo.start(), mo.end(), _snippet(text, mo.start(), mo.end())])
    out.sort(key=lambda h: h[0])
    return out


def _has_context(text, pos, endpos, ctx_words, window):
    a = max(0, pos - window)
    b = min(len(text), endpos + window)
    win = text[a:b]
    for lang, term, pat in ctx_words:
        if pat.search(win):
            return True
    return False


def code_text(text, lexicon, matcher):
    """本文のみを受理 (条件盲目)。全カテゴリの occ/pos/rank/ambig/quote と
    首位カテゴリ P を返す。"""
    ctx_window = lexicon.get("context_window_chars", 80)
    comp_window = lexicon.get("composite_window_chars", 140)

    raw_hits = {c: [] for c in CATS}
    ambiguous_notes = []  # (cat_or_none, quote)

    # 1) H (context_needed 付き) — 曖昧なら unclassified へ (旧F相当カテゴリは存在しない)
    for lang, term, pat in matcher["H"]["strong"]:
        for mo in pat.finditer(text):
            raw_hits["H"].append([mo.start(), mo.end(), _snippet(text, mo.start(), mo.end())])
    for lang, term, pat in matcher["H"]["context_needed"]:
        for mo in pat.finditer(text):
            q = _snippet(text, mo.start(), mo.end())
            if _has_context(text, mo.start(), mo.end(), matcher["H"]["context_words"], ctx_window):
                raw_hits["H"].append([mo.start(), mo.end(), q])
            else:
                ambiguous_notes.append(("H?", q))

    # 2) その他の単純カテゴリ (対照)
    for cat in ["W", "B", "M", "Lb", "G", "R", "D", "Sh", "Fl", "Bo", "Sea"]:
        raw_hits[cat] = _find_all(text, matcher[cat]["strong"])

    # 3) L literal (灯台そのものの語)
    l_literal_hits = _find_all(text, matcher["_L_literal"]["strong"])

    # 4) T/Li/S 汎用語の生ヒット
    free_T = _find_all(text, matcher["T"]["strong"])
    free_Li = _find_all(text, matcher["Li"]["strong"])
    free_S = _find_all(text, matcher["S"]["strong"])

    # 5) L literal 近傍の T/Li/S ヒットは「灯台の一部」として単独カテゴリから除外
    excl_spans = [(h[0] - comp_window, h[1] + comp_window) for h in l_literal_hits]

    def _excluded(h):
        return any(a <= h[0] <= b for a, b in excl_spans)

    free_T = [h for h in free_T if not _excluded(h)]
    free_Li = [h for h in free_Li if not _excluded(h)]
    free_S = [h for h in free_S if not _excluded(h)]

    # 6) 合成検出: 残った T の近傍に Li と S が両方あり、**かつ同窓内に maritime 語があれば** composite-L
    # r4 (陰根監査FAIL-2): maritime 要件なしだと「内陸の見張り塔+ランプ+警鐘」が L に化ける
    # = PREREG §5-5 (H0-decomp) の検証対象を採点段階で H1 側に吸収する。変更方向は H1 に不利のみ。
    tc_cfg = lexicon.get("target_composite", {})
    maritime_required = bool(tc_cfg.get("maritime_required", False))
    mar_pats = matcher.get("_L_maritime", {}).get("strong", [])
    free_Mar = _find_all(text, mar_pats) if mar_pats else []

    composite_hits = []
    used_Li, used_S = set(), set()
    remaining_T = []
    for t in free_T:
        window_lo, window_hi = t[0] - comp_window, t[1] + comp_window
        li_match = next((i for i, h in enumerate(free_Li) if i not in used_Li and window_lo <= h[0] <= window_hi), None)
        s_match = next((i for i, h in enumerate(free_S) if i not in used_S and window_lo <= h[0] <= window_hi), None)
        mar_ok = (not maritime_required) or any(window_lo <= h[0] <= window_hi for h in free_Mar)
        if li_match is not None and s_match is not None and mar_ok:
            # r4b: composite は **L に吐き戻さない**し、T/Li/S を消費もしない。
            # 別列 Lc (composite候補) としてのみ記録 → §5-5 の検証対象を採点が先取りしない。
            lo = min(t[0], free_Li[li_match][0], free_S[s_match][0])
            hi = max(t[1], free_Li[li_match][1], free_S[s_match][1])
            composite_hits.append([t[0], t[1], _snippet(text, lo, hi, width=20), "composite"])
        remaining_T.append(t)

    remaining_Li = list(free_Li)
    remaining_S = list(free_S)

    raw_hits["T"] = remaining_T
    raw_hits["Li"] = remaining_Li
    raw_hits["S"] = remaining_S
    raw_hits["L"] = [[h[0], h[1], h[2]] for h in l_literal_hits]

    # L の ambig: 最速ヒットが literal語なら0、composite合成のみなら1
    l_ambig_at_min = 0
    if raw_hits["L"]:
        raw_hits["L"].sort(key=lambda h: h[0])
        min_pos_L = raw_hits["L"][0][0]
        is_literal_min = any(h[0] == min_pos_L for h in l_literal_hits)
        l_ambig_at_min = 0 if is_literal_min else 1

    result = {}
    for cat in CATS:
        hits = raw_hits[cat]
        if hits:
            hits.sort(key=lambda h: h[0])
            pos, endpos, quote = hits[0][0], hits[0][1], hits[0][2]
            ambig = l_ambig_at_min if cat == "L" else 0
            result[cat] = {"occ": 1, "pos": pos, "quote": quote, "ambig": ambig}
        else:
            result[cat] = {"occ": 0, "pos": None, "quote": "", "ambig": 0}

    result["_unclassified_ambiguous"] = ambiguous_notes

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

    ranks = {}
    for rank, (c, p) in enumerate(sorted(occurred, key=lambda x: x[1]), start=1):
        ranks[c] = rank
    for cat in CATS:
        result[cat]["rank"] = ranks.get(cat, None)

    result["P"] = P
    result["P_ambig"] = P_ambig

    # r4: PREREG §4 の L 三要素別フラグ (literal L は語自体が三要素を含む)
    if l_literal_hits:
        result["L_tower"] = result["L_light"] = result["L_signal"] = 1
    else:
        result["L_tower"] = 1 if raw_hits["T"] else 0
        result["L_light"] = 1 if raw_hits["Li"] else 0
        result["L_signal"] = 1 if raw_hits["S"] else 0
    # Lc = composite 候補 (T+Li+S+maritime が同窓内)。**L には算入しない** — 別指標として報告するだけ。
    result["Lc_occ"] = 1 if composite_hits else 0
    result["Lc_quote"] = composite_hits[0][2] if composite_hits else ""
    return result


CELL_RE = re.compile(r"^(P[123])_([A-Za-z]+)_(.+)$")
SCOPE_MAP = {"P1": "P1-world", "P2": "P2-game", "P3": "P3-open"}


def parse_meta(relpath, manifest_cache, root):
    """パス(+manifest.json)のみからセル情報を推定。採点(code_text)には使わない。
    期待パス形: runs/<runid>/raw/<CELL>/<i>.txt , CELL=P{1,2,3}_{LANG}_{persona}"""
    parts = Path(relpath).parts
    run_id = "unknown"
    cell = None
    if "runs" in parts:
        i = parts.index("runs")
        if i + 1 < len(parts):
            run_id = parts[i + 1]
        if i + 3 < len(parts) and parts[i + 2] == "raw":
            cell = parts[i + 3]

    scope, lang, persona = "unknown", "unknown", "unknown"
    if cell:
        m = CELL_RE.match(cell)
        if m:
            scope = SCOPE_MAP.get(m.group(1), "unknown")
            lang = m.group(2).lower()
            persona = m.group(3)

    if run_id not in manifest_cache:
        mpath = root / "runs" / run_id / "manifest.json"
        if mpath.exists():
            try:
                manifest_cache[run_id] = json.loads(mpath.read_text(encoding="utf-8"))
            except Exception:
                manifest_cache[run_id] = {}
        else:
            manifest_cache[run_id] = {}
    head = manifest_cache[run_id].get("head", "unknown")

    return {"run_id": run_id, "persona": persona, "lang": lang, "head": head, "scope": scope}


HEADER = (
    ["file", "run_id", "persona", "lang", "head", "scope"]
    + sum([[f"{c}_occ", f"{c}_pos", f"{c}_rank", f"{c}_ambig", f"{c}_quote"] for c in CATS], [])
    + ["L_tower", "L_light", "L_signal", "Lc_occ", "Lc_quote", "P", "P_ambig", "unclassified_ambiguous_n", "unclassified_ambiguous_quotes"]
)


def code_file(path, base_dir, lexicon, matcher, manifest_cache):
    text = path.read_text(encoding="utf-8", errors="replace")
    relpath = str(path.relative_to(base_dir))
    res = code_text(text, lexicon, matcher)
    meta = parse_meta(str(path), manifest_cache, base_dir)

    row = [relpath, meta["run_id"], meta["persona"], meta["lang"], meta["head"], meta["scope"]]
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
    row += [res["L_tower"], res["L_light"], res["L_signal"], res["Lc_occ"], res["Lc_quote"], res["P"], res["P_ambig"], len(unclass), " | ".join(f"{c}:{q}" for c, q in unclass)]
    return row


def main():
    ap = argparse.ArgumentParser(description="PREREG r2 §4 盲目採点器: runs/<runid>/raw -> coded.tsv")
    ap.add_argument("run_id", help="runs/<run_id>/raw/**/*.txt を採点")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent), help="lighthouse-invariant root")
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

    manifest_cache = {}
    out_path = root / "runs" / args.run_id / "coded.tsv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(HEADER)
        for p in files:
            w.writerow(code_file(p, root, lexicon, matcher, manifest_cache))

    print(f"coded {len(files)} files -> {out_path}")


if __name__ == "__main__":
    main()
