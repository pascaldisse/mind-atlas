#!/usr/bin/env python3
"""合成fixture(既知ラベル, tests/fixtures/labels.json)上で code_text() の
precision/recall/F1 (カテゴリ出現の多ラベル判定, micro平均) と P(首位)一致率、
L_ambig 一致率を実測する。独立検証: ラベルは code_outputs.py を見ずに人手で書いた
(tests/fixtures/labels.json の _comment 参照)。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from code_outputs import CATS, build_matcher, code_text, load_lexicon  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXDIR = ROOT / "tests" / "fixtures"


def main():
    lexicon = load_lexicon(ROOT / "scripts" / "lexicon.json")
    matcher = build_matcher(lexicon)
    labels = json.loads((FIXDIR / "labels.json").read_text(encoding="utf-8"))["fixtures"]

    tp = fp = fn = tn = 0
    p_correct = 0
    l_ambig_checked = 0
    l_ambig_correct = 0
    uncl_checked = 0
    uncl_correct = 0
    mismatches = []

    for fname, gold in sorted(labels.items()):
        path = FIXDIR / fname
        if not path.exists():
            print(f"MISSING FIXTURE FILE: {fname}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        res = code_text(text, lexicon, matcher)

        gold_occ = gold.get("occ", {})
        for cat in CATS:
            g = gold_occ.get(cat, 0)
            p = res[cat]["occ"]
            if g == 1 and p == 1:
                tp += 1
            elif g == 0 and p == 1:
                fp += 1
                mismatches.append((fname, cat, "FP", res[cat]["quote"]))
            elif g == 1 and p == 0:
                fn += 1
                mismatches.append((fname, cat, "FN", ""))
            else:
                tn += 1

        gold_P = gold.get("P")
        if gold_P is not None:
            ok = res["P"] == gold_P
            p_correct += int(ok)
            if not ok:
                mismatches.append((fname, "P", f"gold={gold_P} got={res['P']}", ""))

        if "L_ambig" in gold:
            l_ambig_checked += 1
            ok = res["L"]["ambig"] == gold["L_ambig"]
            l_ambig_correct += int(ok)
            if not ok:
                mismatches.append((fname, "L_ambig", f"gold={gold['L_ambig']} got={res['L']['ambig']}", ""))

        if "unclassified_ambiguous_n" in gold:
            uncl_checked += 1
            got_n = len(res["_unclassified_ambiguous"])
            ok = got_n == gold["unclassified_ambiguous_n"]
            uncl_correct += int(ok)
            if not ok:
                mismatches.append((fname, "unclassified_ambiguous_n", f"gold={gold['unclassified_ambiguous_n']} got={got_n}", ""))

    n_fixtures = len(labels)
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else float("nan")

    print(f"fixtures n={n_fixtures}")
    print(f"category-label confusion: TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"precision={precision:.3f} recall={recall:.3f} F1={f1:.3f}")
    print(f"P(top-category) exact-match accuracy = {p_correct}/{n_fixtures} = {p_correct/n_fixtures:.3f}")
    if l_ambig_checked:
        print(f"L_ambig accuracy = {l_ambig_correct}/{l_ambig_checked} = {l_ambig_correct/l_ambig_checked:.3f}")
    if uncl_checked:
        print(f"unclassified_ambiguous_n accuracy = {uncl_correct}/{uncl_checked} = {uncl_correct/uncl_checked:.3f}")

    if mismatches:
        print("\n--- mismatches ---")
        for fname, cat, kind, quote in mismatches:
            print(f"  {fname}: {cat} {kind} {quote}")
    else:
        print("\nno mismatches.")


if __name__ == "__main__":
    main()
