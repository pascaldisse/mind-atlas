#!/usr/bin/env python3
"""
battery-v2 lane-prompt emitter. PREREG §3(問題セット)+§4(basis)を実装。
1lane=1問=1回答(清文脈)の原則を守るため、本scriptは「投げるべき全lane」の
manifestを1行=1laneのTSVとして書き出すだけで、実際の呼出は行わない
(呼出は各lane別に新規sessionで人が/harnessが実行する)。

Usage:
    python3 emit_prompts.py [--out manifest.tsv]

出力列: lane_id, question_id, basis_id, head, language, pf, group, rep,
        answer_format, system_prompt, prompt_text
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import get_template, SYSTEM_PROMPTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def load_json(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def translate(vocab, word_id, language):
    entry = vocab["words"].get(word_id)
    if entry is None:
        raise KeyError(f"vocab.json missing word_id={word_id!r}")
    val = entry.get(language)
    if val is None:
        raise KeyError(f"vocab.json word_id={word_id!r} missing language={language!r}")
    return val


def reps_for(question):
    if question["type"] == "axis":
        return question["reps_per_group"]
    return question["reps"]


def answer_format_for(question):
    return "numeric" if question["type"] in ("distance", "axis") else "word"


def build_prompt(question, basis, vocab, group=None):
    qtype = question["type"]
    lang = basis["language"]
    pf = basis["pf"]
    tmpl = get_template(qtype, lang, pf)

    if qtype == "distance":
        x = translate(vocab, question["pair"][0], lang)
        y = translate(vocab, question["pair"][1], lang)
        return tmpl.format(X=x, Y=y)

    if qtype == "axis":
        a = translate(vocab, question["axis"][0], lang)  # canonical pole A
        b = translate(vocab, question["axis"][1], lang)  # canonical pole B
        mid = translate(vocab, question["mid"], lang)
        if group == "fwd":
            pole0, pole10 = a, b
        elif group == "rev":
            pole0, pole10 = b, a
        else:
            raise ValueError(f"axis question requires group fwd/rev, got {group!r}")
        return tmpl.format(POLE0=pole0, POLE10=pole10, MID=mid)

    if qtype in ("order_top", "order_bottom", "order_bottom_v2"):
        target = translate(vocab, question["target"], lang)
        return tmpl.format(TARGET=target)

    if qtype == "analogy":
        a = translate(vocab, question["pair"][0], lang)
        b = translate(vocab, question["pair"][1], lang)
        target = translate(vocab, question["target"], lang)
        return tmpl.format(A=a, B=b, TARGET=target)

    raise ValueError(f"unknown question type {qtype!r}")


def emit_rows(questions, basis_list, vocab):
    rows = []
    for basis in basis_list:
        for q in questions:
            qtype = q["type"]
            fmt = answer_format_for(q)
            sys_prompt = SYSTEM_PROMPTS[basis["pf"]]
            if qtype == "axis":
                for group in q["groups"]:
                    n = reps_for(q)
                    prompt = build_prompt(q, basis, vocab, group=group)
                    for rep in range(1, n + 1):
                        lane_id = f"{basis['id']}__{q['id']}__{group}__rep{rep:02d}"
                        rows.append({
                            "lane_id": lane_id,
                            "question_id": q["id"],
                            "basis_id": basis["id"],
                            "head": basis["head"],
                            "language": basis["language"],
                            "pf": basis["pf"],
                            "group": group,
                            "rep": rep,
                            "answer_format": fmt,
                            "system_prompt": sys_prompt or "",
                            "prompt_text": prompt,
                        })
            else:
                n = reps_for(q)
                prompt = build_prompt(q, basis, vocab)
                for rep in range(1, n + 1):
                    lane_id = f"{basis['id']}__{q['id']}__na__rep{rep:02d}"
                    rows.append({
                        "lane_id": lane_id,
                        "question_id": q["id"],
                        "basis_id": basis["id"],
                        "head": basis["head"],
                        "language": basis["language"],
                        "pf": basis["pf"],
                        "group": "na",
                        "rep": rep,
                        "answer_format": fmt,
                        "system_prompt": sys_prompt or "",
                        "prompt_text": prompt,
                    })
    return rows


FIELDNAMES = [
    "lane_id", "question_id", "basis_id", "head", "language", "pf",
    "group", "rep", "answer_format", "system_prompt", "prompt_text",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="output TSV path (default: stdout)")
    ap.add_argument("--questions", default="questions.json")
    ap.add_argument("--basis", default="basis.json")
    ap.add_argument("--vocab", default="vocab.json")
    args = ap.parse_args()

    questions = load_json(args.questions)["questions"]
    basis_list = load_json(args.basis)["basis"]
    vocab = load_json(args.vocab)

    rows = emit_rows(questions, basis_list, vocab)

    out = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    try:
        w = csv.DictWriter(out, fieldnames=FIELDNAMES, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    finally:
        if args.out:
            out.close()

    print(f"emitted {len(rows)} lanes", file=sys.stderr)


if __name__ == "__main__":
    main()
