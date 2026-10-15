#!/usr/bin/env python3
"""PREREG r3 §5–§6 tabulator: one immutable raw input set -> one results table."""
import argparse
import csv
import datetime as dt
import hashlib
import math
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

CATS = ["L", "Lc", "T", "Li", "S", "H", "W", "B", "M", "Lb", "G", "R", "D", "Sh", "Fl", "Bo", "Sea"]
CONTRAST_CATS = ["H", "W", "B", "M", "Lb", "G", "R", "D", "Sh", "Fl", "Bo", "Sea"]
MIN_N_PER_CELL = 10
Z_95 = 1.959963985


def wilson_ci(k, n, z=Z_95):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return (max(0.0, (center - margin) / denom), min(1.0, (center + margin) / denom))


def fmt_ci(k, n):
    if n == 0:
        return "n=0"
    lo, hi = wilson_ci(k, n)
    return f"{k}/{n}={k/n:.3f} [{lo:.3f},{hi:.3f}]"


def intervals_overlap(ci1, ci2):
    """参考表示のみ。§5 の検定/判定には絶対に使わない。"""
    lo1, hi1 = ci1
    lo2, hi2 = ci2
    if any(math.isnan(x) for x in (lo1, hi1, lo2, hi2)):
        return None
    return not (hi1 < lo2 or hi2 < lo1)


def risk_difference_ci(k1, n1, k2, n2):
    """Newcombe (1998) method 10: independent-proportion RD Wilson-score 95% CI."""
    if not n1 or not n2:
        return (float("nan"), float("nan"), float("nan"))
    p1, p2 = k1 / n1, k2 / n2
    lo1, hi1 = wilson_ci(k1, n1)
    lo2, hi2 = wilson_ci(k2, n2)
    return (p1 - p2, lo1 - hi2, hi1 - lo2)


def risk_ratio_ci(k1, n1, k2, n2, z=Z_95):
    """Katz log RR 95% CI; Haldane–Anscombe +0.5 to all 2×2 cells."""
    if not n1 or not n2:
        return (float("nan"), float("nan"), float("nan"))
    a, b, c, d = k1 + 0.5, n1 - k1 + 0.5, k2 + 0.5, n2 - k2 + 0.5
    n1c, n2c = a + b, c + d
    rr = (a / n1c) / (c / n2c)
    se = math.sqrt(1 / a - 1 / n1c + 1 / c - 1 / n2c)
    return (rr, math.exp(math.log(rr) - z * se), math.exp(math.log(rr) + z * se))


def comparison(k1, n1, k2, n2, rr_multiplier=1.0):
    """Both preregistered comparison scales; multiplier makes a ratio threshold equal 1."""
    rd, rd_lo, rd_hi = risk_difference_ci(k1, n1, k2, n2)
    rr, rr_lo, rr_hi = risk_ratio_ci(k1, n1, k2, n2)
    rr, rr_lo, rr_hi = (rr * rr_multiplier, rr_lo * rr_multiplier, rr_hi * rr_multiplier)
    if any(math.isnan(x) for x in (rd, rd_lo, rd_hi, rr, rr_lo, rr_hi)):
        status = "UNVERIFIED"
    elif rd_hi < 0 and rr_hi < 1:
        status = "BELOW"
    elif rd_lo > 0 and rr_lo > 1:
        status = "ABOVE"
    else:
        status = "CROSSES"
    return {"rd": (rd, rd_lo, rd_hi), "rr": (rr, rr_lo, rr_hi), "status": status}


def fmt_comparison(label, comp):
    rd, rr = comp["rd"], comp["rr"]
    return (f"{label}: RD={rd[0]:.3f} [{rd[1]:.3f},{rd[2]:.3f}] (0を{comp['status']}) | "
            f"RR={rr[0]:.3f} [{rr[1]:.3f},{rr[2]:.3f}] (1を{comp['status']})")


def load_rows(coded_path):
    with open(coded_path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def count_occ(rows, cat):
    return sum(r.get(f"{cat}_occ") == "1" for r in rows), len(rows)


def count_top(rows, cat):
    return sum(r.get("P") == cat for r in rows), len(rows)


def group_by(rows, keyfn):
    grouped = defaultdict(list)
    for row in rows:
        grouped[keyfn(row)].append(row)
    return grouped


def md_table_occ_top(rows_by_group, cat, group_label):
    top_label = "—" if cat == "Lc" else f"{cat}_首位率(P=={cat})"
    lines = [f"| {group_label} | n | {cat}_occ率 | {top_label} |", "|---|---|---|---|"]
    for name in sorted(rows_by_group):
        rows = rows_by_group[name]
        k_occ, n = count_occ(rows, cat)
        top = "—" if cat == "Lc" else fmt_ci(*count_top(rows, cat))
        lines.append(f"| {name} | {n} | {fmt_ci(k_occ, n)} | {top} |")
    return "\n".join(lines)


def raw_input_set(root, run_id):
    raw_dir = root / "runs" / run_id / "raw"
    files = sorted(p for p in raw_dir.rglob("*.txt") if p.is_file())
    entries = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        entries.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    payload = "".join(f"{path}\t{digest}\n" for path, digest in entries).encode()
    return entries, hashlib.sha256(payload).hexdigest()


def write_input_set(root, run_id, entries, digest, scored_at):
    path = root / "runs" / run_id / "input-set.tsv"
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(f"# run_id\t{run_id}\n# file_count\t{len(entries)}\n# set_digest_sha256\t{digest}\n# scored_at_utc\t{scored_at}\n")
        f.write("relative_path\tsha256\n")
        for relative, file_digest in entries:
            f.write(f"{relative}\t{file_digest}\n")
    return path


def saved_input_digest(path):
    if not path.exists():
        raise FileNotFoundError(path)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# set_digest_sha256\t"):
            return line.split("\t", 1)[1]
    raise ValueError(f"set_digest_sha256 missing: {path}")


def verify_input_set(root, run_id):
    entries, current = raw_input_set(root, run_id)
    path = root / "runs" / run_id / "input-set.tsv"
    saved = saved_input_digest(path)
    if current != saved:
        raise RuntimeError(f"INPUT SET MISMATCH: saved={saved} current={current} files={len(entries)}")
    print(f"input set verified: {path} files={len(entries)} digest={current}")


def unstable_input(root, run_id):
    raw_dir = root / "runs" / run_id / "raw"
    # 実測(00:26): pgrep -f "run_trials" は **自分の待機タイマーの command line 本文**にも当たり偽陽性を出した。
    # → 実際に走っている生成 script プロセスだけを見る (gaia resume / sleep を含む監視プロセスを除外)。
    proc_l = subprocess.run(["pgrep", "-fl", "run_trials"], capture_output=True, text=True)
    real = [ln for ln in proc_l.stdout.splitlines()
            if ("run_trials" in ln) and ("gaia resume" not in ln) and (" sleep " not in ln)]
    class _P:
        returncode = 0 if real else 1
    proc = _P()
    running = proc.returncode == 0
    now = dt.datetime.now().timestamp()
    recent = [p for p in raw_dir.rglob("*") if p.is_file() and now - p.stat().st_mtime < 60]
    return running, recent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--verify-input-set", action="store_true", help="saved input-set.tsv と現在の raw 集合を照合して終了")
    ap.add_argument("--force", action="store_true", help="run_trials/raw更新の安全弁を明示的に上書き")
    args = ap.parse_args()
    root = Path(args.root)

    if args.verify_input_set:
        try:
            verify_input_set(root, args.run_id)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            print(f"UNVERIFIED: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    coded_path = root / "runs" / args.run_id / "coded.tsv"
    if not coded_path.exists():
        print(f"UNVERIFIED: {coded_path} 無し。先に code_outputs.py を走らせろ。", file=sys.stderr)
        sys.exit(1)
    running, recent = unstable_input(root, args.run_id)
    unstable = running or bool(recent)
    if unstable and not args.force:
        print(f"UNVERIFIED: unstable raw input (run_trials={running}, raw更新<60秒={len(recent)}件)。--force のみ続行可。", file=sys.stderr)
        sys.exit(2)

    rows = load_rows(coded_path)
    n_total = len(rows)
    entries, digest = raw_input_set(root, args.run_id)
    scored_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    input_path = write_input_set(root, args.run_id, entries, digest, scored_at)

    out = [f"# 灯台不変量 — run {args.run_id} 採点表 (PREREG r3 §4–§6準拠, 自動生成 · 手集計禁)"]
    if unstable:
        out.append("\n> **UNSTABLE INPUT**: --force により走行中/直近更新の raw を採点。再現可能な確定表ではない。")
    out += ["\n## 入力集合固定", f"- rawファイル数: {len(entries)}", f"- 集合ダイジェスト (relative path + sha256一覧のSHA-256): `{digest}`", f"- 採点時刻 (UTC): {scored_at}", f"- 台帳: `runs/{args.run_id}/input-set.tsv`", f"\nn_total = {n_total} (このrunのみ。他run混ぜ禁)"]
    if n_total < MIN_N_PER_CELL:
        out.append(f"\n**⚠ UNVERIFIED: n_total={n_total} < PREREG最低ライン(N≥10/cell)。全数字は参考値、統計的主張の対象外。**")

    out += ["\n## 1. 標的L・Lcと部分一致の出現率・首位率 (全体)", "| カテゴリ | 出現率 (Wilson95%CI) | 首位率 (Wilson95%CI) |", "|---|---|---|"]
    for cat in ["L", "Lc", "T", "Li", "S"]:
        k, n = count_occ(rows, cat)
        top = "— (Lcは首位カテゴリに非算入)" if cat == "Lc" else fmt_ci(*count_top(rows, cat))
        out.append(f"| {cat} | {fmt_ci(k, n)} | {top} |")
    out += ["\n## 2. 対照カテゴリ (Seaを含む12種) 出現率・首位率 (全体)", "| カテゴリ | 出現率 | 首位率 |", "|---|---|---|"]
    for cat in CONTRAST_CATS:
        out.append(f"| {cat} | {fmt_ci(*count_occ(rows, cat))} | {fmt_ci(*count_top(rows, cat))} |")
    by_cell = group_by(rows, lambda r: f"{r.get('scope','unknown')}_{r.get('lang','unknown')}_{r.get('persona','unknown')}")
    out += ["\n## 3. セル別 (scope_lang_persona) — L", md_table_occ_top(by_cell, "L", "cell")]
    for section, title, key in [(4, "head", "head"), (5, "lang", "lang"), (6, "scope", "scope"), (7, "persona", "persona")]:
        out += [f"\n## {section}. {title}別 — L", md_table_occ_top(group_by(rows, lambda r, key=key: r.get(key, "unknown")), "L", title)]

    out.append("\n## 8. 海prime条件付きL率 (Bo ∪ Sea; Bo単独も併記)")
    for label, subset in [("Bo ∪ Sea", [r for r in rows if r.get("Bo_occ") == "1" or r.get("Sea_occ") == "1"]), ("Bo単独", [r for r in rows if r.get("Bo_occ") == "1"])]:
        k_occ, n = count_occ(subset, "L")
        k_top, _ = count_top(subset, "L")
        out.append(f"- {label}出現サブセット n={n}: L出現率 {fmt_ci(k_occ,n)}; L首位率 {fmt_ci(k_top,n)}")

    out.append("\n## 9. §5 反証基準 — RD/RR CI 自動判定")
    out.append("手法: RD=Newcombe (1998) method 10 (Wilson score): [L1−U2, U1−L2]。RR=Katz log risk ratio、全2×2セル Haldane–Anscombe +0.5、log(RR)±1.959964√(1/a−1/n1+1/c−1/n2)。Wilsons は率の記述用。**生CIの重なりは「重なり(参考、検定ではない)」のみで判定に不使用。**")
    verdicts = []

    ltop_k, ltop_n = count_top(rows, "L")
    contrasts = sorted((count_top(rows, cat)[0] / n_total if n_total else float("nan"), cat, count_top(rows, cat)[0]) for cat in CONTRAST_CATS)
    if n_total:
        middle = contrasts[len(contrasts)//2-1:len(contrasts)//2+1]
        comps = [comparison(ltop_k, n_total, k, n_total) for _, cat, k in middle]
        refs = "; ".join(fmt_comparison(f"L首位−{cat}", comp) for comp, (_, cat, _) in zip(comps, middle))
        ref_ci = [wilson_ci(k, n_total) for _, _, k in middle]
        reference = "; ".join(f"{cat}={rate:.3f}" for rate, cat, _ in middle)
        fail = any(c["status"] == "CROSSES" for c in comps)
        verdicts.append(f"条件1: 対照中央値境界({reference})。{refs} | L生CIと対照生CIの重なり(参考、検定ではない)={ [intervals_overlap(wilson_ci(ltop_k,n_total), x) for x in ref_ci] } -> {'FAIL(H1敗北)' if fail else 'PASS'}")
    else:
        verdicts.append("条件1: UNVERIFIED: n_total=0")

    def threshold_condition(number, label, left_rows, right_rows, fail_name):
        k1, n1 = count_occ(left_rows, "L"); k2, n2 = count_occ(right_rows, "L")
        comp = comparison(k1, n1, k2, n2, rr_multiplier=3.0)
        # RR*=3 means the preregistered one-third threshold is RR*=1.
        # The absolute RD remains descriptive here; the one-third null is RR*=1.
        rr_lo, rr_hi = comp["rr"][1:]
        state = "FAIL(" + fail_name + ")" if rr_hi < 1 else ("PASS" if rr_lo > 1 else "UNVERIFIED (RR CIが1を跨ぐ)")
        verdicts.append(f"条件{number}: {label}; {fmt_ci(k1,n1)} vs {fmt_ci(k2,n2)}; {fmt_comparison('閾値比較(3×左/右)', comp)} -> {state}")

    threshold_condition("2", "P3-open L率 < P1-world L率/3", [r for r in rows if r.get("scope") == "P3-open"], [r for r in rows if r.get("scope") == "P1-world"], "H0-trope")
    threshold_condition("3", "codex L率 < sonnet L率/3", [r for r in rows if r.get("head") == "openai-codex"], [r for r in rows if r.get("head") == "anthropic-sonnet"], "H0-house")
    threshold_condition("4", "none L率 < persona付き L率/3", [r for r in rows if r.get("persona") == "none"], [r for r in rows if r.get("persona") not in ("none", "unknown", "")], "persona由来")

    lk, ln = count_occ(rows, "L"); tk, tn = count_occ(rows, "T")
    lis_k = sum(r.get("Li_occ") == "1" or r.get("S_occ") == "1" for r in rows)
    comp_t, comp_lis = comparison(lk, ln, tk, tn), comparison(lk, ln, lis_k, n_total)
    fail5 = comp_t["status"] == "CROSSES" or comp_lis["status"] == "CROSSES"
    verdicts.append(f"条件5: {fmt_comparison('L−T単独', comp_t)}; {fmt_comparison('L−(Li∪S)', comp_lis)}; 生CI重なり(参考、検定ではない)=T:{intervals_overlap(wilson_ci(lk,ln), wilson_ci(tk,tn))}, Li∪S:{intervals_overlap(wilson_ci(lk,ln), wilson_ci(lis_k,n_total))} -> {'FAIL(H0-decomp)' if fail5 else 'PASS'}")
    out += [f"- **{v}**" for v in verdicts]
    if any("UNVERIFIED" in v for v in verdicts):
        overall = "UNVERIFIED (データ不足またはCIが閾値を跨ぐ)"
    elif any("FAIL" in v for v in verdicts):
        overall = "H1敗北 (上記いずれかの条件でFAIL)"
    else:
        overall = "生存 (今回runの範囲で全5条件をくぐった)"
    out.append(f"\n**総合判定**: {overall}")

    results_dir = root / "results"; results_dir.mkdir(exist_ok=True)
    out_path = results_dir / f"{args.run_id}-table.md"
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {out_path}; input set {input_path}")


if __name__ == "__main__":
    main()
