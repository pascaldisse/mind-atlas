#!/usr/bin/env python3
"""
pass_gate.py -- battery-v2 段C: PREREG §8 pass-gate aggregation over a FIXED
input set (path + sha256 of every coded-*.tsv consumed, frozen in the same
commit as this report -- never aggregate a run dir still being written to).

Anchors checked (v1 reproduction claims), anchor x basis:
  D1  distance(影,闇)      v1 ~= 2      window [1,3]
  D3  distance(愛,無)      v1 in 7-9    window [7,9]
  A1  axis(生<->死, mid=夢) v1 = 5       window [4,6]  (fwd/rev both canonicalized)
  O2  order_bottom(愛)     v1 = 無      word-match against vocab id 'nothingness'
                                        translations (JA/DE/EN/ZH), casefold+strip

Pass gate (PREREG §8): an anchor "reproduces" if it falls in its v1 window in
>=2 basis. "Not supported" is reported as a normal, valid outcome, not hidden.

A1/A2 polarity check: fwd vs rev group canonical_value (already counterbalance-
corrected by code_outputs.py: canonical = 10-raw for rev) compared as two
distributions. If their ranges/means overlap -> instrument artifact (polarity
flip was a measurement defect, now corrected). If they stay apart even after
canonicalization -> real split, not an artifact.

Usage: python3 pass_gate.py --coded-dir DIR --out OUT.md
"""
import argparse
import csv
import glob
import hashlib
import os
import statistics
import sys

WORD_ANCHOR_ID = "無"  # nothingness, vocab.json key

ANCHOR_WINDOWS = {
    "D1": (1, 3, "distance(影,闇) v1~=2"),
    "D3": (7, 9, "distance(愛,無) v1 in 7-9"),
    "A1": (4, 6, "axis(生<->死,mid=夢) v1=5"),
}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_coded_files(coded_dir):
    files = sorted(glob.glob(os.path.join(coded_dir, "coded-*.tsv")))
    rows = []
    digests = []
    for fp in files:
        digests.append((fp, sha256_of(fp)))
        with open(fp, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                rows.append(r)
    return rows, digests


def numeric_values(rows, question_id, basis_id, group=None):
    out = []
    for r in rows:
        if r["question_id"] != question_id or r["basis_id"] != basis_id:
            continue
        if group is not None and r["group"] != group:
            continue
        cv = r["canonical_value"]
        try:
            out.append(float(cv))
        except (ValueError, TypeError):
            continue  # NA / UNDEFINED_TOKEN_COLLISION excluded, not fabricated as 0
    return out


def word_values(rows, question_id, basis_id):
    out = []
    for r in rows:
        if r["question_id"] != question_id or r["basis_id"] != basis_id:
            continue
        cv = r["canonical_value"]
        if cv and cv != "NA":
            out.append(cv)
    return out


def basis_ids_present(rows):
    return sorted({r["basis_id"] for r in rows})


def word_anchor_translations(vocab_path):
    import json
    with open(vocab_path, encoding="utf-8") as f:
        v = json.load(f)
    entry = v["words"][WORD_ANCHOR_ID]
    forms = set()
    for lang in ("EN", "DE", "JA", "ZH"):
        val = entry.get(lang)
        if val:
            forms.add(val.strip().casefold())
    return forms


def summarize_numeric(vals):
    if not vals:
        return None
    return {
        "n": len(vals),
        "mean": round(statistics.mean(vals), 3),
        "min": min(vals),
        "max": max(vals),
        "sd": round(statistics.pstdev(vals), 3) if len(vals) > 1 else 0.0,
    }


def in_window(mean, lo, hi):
    return lo <= mean <= hi


def build_report(rows, digests, vocab_path):
    lines = []
    lines.append("# battery-v2 段C pass-gate report (PREREG §8)")
    lines.append("")
    lines.append("## Input set (frozen, path + sha256)")
    for fp, dg in digests:
        lines.append(f"- `{fp}` {dg}")
    lines.append("")

    bases = basis_ids_present(rows)
    lines.append(f"## Basis present in this aggregation: {len(bases)}")
    for b in bases:
        lines.append(f"- {b}")
    lines.append("")

    lines.append("## Anchor x basis (D1, D3, A1 numeric anchors)")
    lines.append("")
    lines.append("| anchor | basis | n | mean | sd | min | max | window | reproduces? |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    anchor_pass_count = {aid: 0 for aid in ANCHOR_WINDOWS}
    for aid, (lo, hi, desc) in ANCHOR_WINDOWS.items():
        for b in bases:
            if aid == "A1":
                # fwd/rev both counterbalance-corrected already by code_outputs.py;
                # pool both groups for the headline reproduces-check, report separately below.
                vals = numeric_values(rows, aid, b)
            else:
                vals = numeric_values(rows, aid, b)
            s = summarize_numeric(vals)
            if s is None:
                lines.append(f"| {aid} | {b} | 0 | - | - | - | - | [{lo},{hi}] | NO_DATA |")
                continue
            reproduces = in_window(s["mean"], lo, hi)
            if reproduces:
                anchor_pass_count[aid] += 1
            lines.append(
                f"| {aid} | {b} | {s['n']} | {s['mean']} | {s['sd']} | {s['min']} | {s['max']} "
                f"| [{lo},{hi}] | {'YES' if reproduces else 'no'} |"
            )
    lines.append("")

    lines.append("## Anchor O2 (order_bottom(愛) = 無, word match) x basis")
    lines.append("")
    lines.append(f"vocab id `{WORD_ANCHOR_ID}` (nothingness) accepted surface forms (casefold): "
                  f"{sorted(word_anchor_translations(vocab_path))}")
    lines.append("")
    lines.append("| anchor | basis | n | matches(無-equivalent) | match_rate | reproduces? |")
    lines.append("|---|---|---|---|---|---|")
    forms = word_anchor_translations(vocab_path)
    o2_pass = 0
    o2_bases = 0
    for b in bases:
        wv = word_values(rows, "O2", b)
        if not wv:
            lines.append(f"| O2 | {b} | 0 | - | - | NO_DATA |")
            continue
        o2_bases += 1
        matches = sum(1 for w in wv if w.strip().casefold() in forms)
        rate = round(matches / len(wv), 3)
        reproduces = rate >= 0.5  # majority of reps name the anchor word
        if reproduces:
            o2_pass += 1
        lines.append(f"| O2 | {b} | {len(wv)} | {matches} | {rate} | {'YES' if reproduces else 'no'} |")
    lines.append("")

    lines.append("## PASS GATE verdicts (PREREG §8: reproduces in >=2 basis)")
    lines.append("")
    for aid in ("D1", "D3", "A1"):
        n_bases_with_data = sum(
            1 for b in bases if numeric_values(rows, aid, b)
        )
        verdict = "PASS" if anchor_pass_count[aid] >= 2 else "NOT SUPPORTED"
        lines.append(f"- **{aid}**: reproduces in {anchor_pass_count[aid]}/{n_bases_with_data} "
                      f"basis-with-data -> **{verdict}**")
    verdict_o2 = "PASS" if o2_pass >= 2 else "NOT SUPPORTED"
    lines.append(f"- **O2**: reproduces in {o2_pass}/{o2_bases} basis-with-data -> **{verdict_o2}**")
    lines.append("")
    lines.append("『支持されず』も有効な結果として明記 (not hidden, not spun as failure of method).")
    lines.append("")

    lines.append("## A1/A2 polarity check (fwd vs rev, post-canonicalization)")
    lines.append("")
    lines.append("| question | basis | group | n | mean | sd | min | max |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for qid in ("A1", "A2"):
        for b in bases:
            for grp in ("fwd", "rev"):
                vals = numeric_values(rows, qid, b, group=grp)
                s = summarize_numeric(vals)
                if s is None:
                    lines.append(f"| {qid} | {b} | {grp} | 0 | - | - | - | - |")
                    continue
                lines.append(f"| {qid} | {b} | {grp} | {s['n']} | {s['mean']} | {s['sd']} "
                              f"| {s['min']} | {s['max']} |")
    lines.append("")
    lines.append("Interpretation law (not auto-decided by this script, judged per-row above): "
                  "if fwd/rev canonicalized ranges overlap for a question x basis -> the pre-"
                  "canonicalization polarity flip was an instrument artifact (now corrected); "
                  "if they stay apart -> a real split survives counterbalance correction. "
                  "Both are valid, reported findings -- see table above per basis.")
    lines.append("")

    lines.append("## Boundary note (机械的オラクル不在)")
    lines.append("")
    lines.append("NLEmbedding (macOS on-device semantic distance oracle used for cross-checking "
                  "model-reported distances elsewhere in this project) has **no JA and no ZH "
                  "coverage** (confirmed NIL in prior verification). The ZH and JA basis results "
                  "above therefore carry **no independent machine-embedding cross-check** and "
                  "cannot be held to the same verification standard as the EN/DE basis results, "
                  "which do have that check available (elsewhere in the pipeline). This is a "
                  "structural gap in the oracle, not a defect in collection.")
    lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coded-dir", required=True)
    ap.add_argument("--vocab", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.json"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows, digests = load_coded_files(args.coded_dir)
    report = build_report(rows, digests, args.vocab)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"pass_gate report written -> {args.out} ({len(rows)} coded rows from {len(digests)} files)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
