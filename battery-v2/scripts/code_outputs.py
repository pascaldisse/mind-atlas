#!/usr/bin/env python3
"""
battery-v2 coder. 生回答(runs/<runid>/raw/<lane_id>.txt)をmanifest.tsv(emit_prompts.py出力)
と結合し、tidy TSVへcode化する。PREREG §4.3(keying)+§2.2(counterbalance正準化)を実装。

数字を作るのは本scriptのみ(PREREG §7)。パース不能・欠測は値を捏造せず NA を書く。

Usage:
    python3 code_outputs.py --manifest manifest.tsv --raw-dir runs/<runid>/raw \
        --out runs/<runid>/coded.tsv
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys


class DispatchIntegrityError(Exception):
    """Raised when dispatch-map provenance cannot guarantee 1 lane = 1 clean-context session."""


NUMERIC_RE = re.compile(r"-?\d+(?:\.\d+)?")
WORD_STRIP_CHARS = " \t\r\n'\"「」『』.,;:!?()（）。、"

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VOCAB_PATH = os.path.join(SCRIPTS_DIR, "vocab.json")
DEFAULT_QUESTIONS_PATH = os.path.join(SCRIPTS_DIR, "questions.json")


def parse_numeric(text):
    """最初に出現する0-10範囲の数を取る。範囲外はそのまま返し呼び出し側でNA判定させる余地を残す。"""
    m = NUMERIC_RE.search(text)
    if not m:
        return None
    try:
        val = float(m.group())
    except ValueError:
        return None
    return val


def parse_word(text):
    """最初の非空トークンを取り、周辺の引用符・句読点を剥ぐ。"""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        token = line.split()[0] if " " in line.strip() else line
        token = token.strip(WORD_STRIP_CHARS)
        if token:
            return token
    return None


def file_timestamp(path):
    ts = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return {row["lane_id"]: row for row in reader}


def load_vocab(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_questions(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["questions"]


def build_distance_pair_collision_ids(questions, vocab_words):
    """question_id -> (id_a, id_b, token_collision_a, token_collision_b) for type=='distance'
    questions only. Resolved via vocab.json's ja-keyed `words` -> canonical_id +
    token_collision (vocab/SCHEMA.md field, synced through by sync_vocab_from_canonical.py).
    Used only by pair_is_token_collision() (PREREG r4, consumer-side UNDEFINED guard).
    Silently skips a question if its pair words are not present in vocab_words (e.g. a
    synthetic/mini-battery manifest whose question_id happens to collide with a real one
    but was never meant to be checked against the real vocab).
    """
    out = {}
    for q in questions:
        if q.get("type") != "distance":
            continue
        pair = q.get("pair")
        if not pair or len(pair) != 2:
            continue
        entry_a = vocab_words.get(pair[0])
        entry_b = vocab_words.get(pair[1])
        if entry_a is None or entry_b is None:
            continue
        out[q["id"]] = (
            entry_a.get("canonical_id"), entry_b.get("canonical_id"),
            entry_a.get("token_collision"), entry_b.get("token_collision"),
        )
    return out


def pair_is_token_collision(id_a, id_b, lang, tc_a, tc_b):
    """vocab/SCHEMA.md token_collision field law (~/projects/semantic-map),
    consumer-side implementation per PREREG r4:

    \"Downstream code computing embedding distances between concepts MUST treat
    any pair of ids appearing together in the same token_collision[lang] list as
    UNDEFINED for that language, not 0.0 -- their distance is identically zero
    by construction (same input string), which is a fact about the tokenization,
    not a measurement.\"

    tc_a/tc_b: the token_collision dict of id_a/id_b respectively (None if that id
    has no collision at all in any language). Each present dict already includes
    its own id in the list for languages where it collides (schema guarantee), so
    checking either side's list for the other id's presence is sufficient.

    Case note: basis.json's `language` field is uppercase (EN/DE/JA/ZH, matching
    lane/manifest convention) while canonical vocab.json's token_collision keys are
    lowercase (ja/en/de/zh, matching the canonical schema's lang codes) -- `lang` is
    normalized to lowercase here so callers can pass either.
    """
    lang = lang.lower()
    for tc in (tc_a, tc_b):
        if tc and lang in tc and id_a in tc[lang] and id_b in tc[lang]:
            return True
    return False


def load_dispatch_map(path):
    """dispatch-map.tsv: columns sub_room_id, lane_id. Returns list of (room_id, lane_id) rows, order preserved."""
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return [(row["sub_room_id"], row["lane_id"]) for row in reader]


def validate_dispatch_map(dispatch_rows, lane_ids_to_code):
    """
    lane_ids_to_code: iterable of lane_id that have a raw file and are about to be coded.

    Enforces (陰根L5監査 DEFECT4, PREREG r3):
      1. every lane_id in lane_ids_to_code must appear in dispatch_rows exactly once
         (no provenance -> cannot verify clean-context independence -> refuse).
      2. no room_id may appear against more than one lane_id
         (shared context answering >1 lane = the exact v1 impeachment-1 failure mode).

    Returns dict lane_id -> room_id on success. Raises DispatchIntegrityError otherwise
    (collecting ALL violations before raising, so the error message is complete, not first-hit-only).
    """
    lane_to_room = {}
    room_to_lanes = {}
    dup_lane_rows = {}
    for room_id, lane_id in dispatch_rows:
        dup_lane_rows.setdefault(lane_id, []).append(room_id)
        room_to_lanes.setdefault(room_id, set()).add(lane_id)

    errors = []

    for lane_id, rooms in dup_lane_rows.items():
        if len(rooms) > 1:
            errors.append(f"lane_id {lane_id!r} has {len(rooms)} dispatch-map entries (ambiguous room_id): {rooms}")
        else:
            lane_to_room[lane_id] = rooms[0]

    shared = {room_id: lanes for room_id, lanes in room_to_lanes.items() if len(lanes) > 1}
    if shared:
        for room_id, lanes in shared.items():
            errors.append(
                f"room_id {room_id!r} is dispatch-mapped to {len(lanes)} different lanes {sorted(lanes)} "
                f"-- shared context answered multiple lanes, independence cannot be guaranteed"
            )

    missing = [lid for lid in lane_ids_to_code if lid not in lane_to_room]
    if missing:
        errors.append(
            f"{len(missing)} lane(s) have a raw file but no dispatch-map provenance entry, "
            f"cannot verify clean-context independence, refusing to code them: {sorted(missing)[:10]}"
            + (" ..." if len(missing) > 10 else "")
        )

    if errors:
        raise DispatchIntegrityError("; ".join(errors))

    return lane_to_room


CODED_FIELDNAMES = [
    "question_id", "basis_id", "head", "rep", "group",
    "raw_value", "canonical_value", "lane_id", "room_id", "timestamp", "note",
]


def code_lane(lane_row, raw_text, raw_path, room_id, token_collision_undefined=False):
    """token_collision_undefined: precomputed by the caller (see main()) via
    pair_is_token_collision() for this lane's (question_id, language). When True,
    a distance-type lane's canonical_value is forced to the UNDEFINED sentinel
    instead of whatever number was parsed -- PREREG r4 / vocab SCHEMA.md law: a
    distance between two ids that share a token in this language is identically
    zero by tokenization, not a measurement, and must never be reported as a
    measured 0. raw_value (what the model actually said) is kept, never fabricated
    away -- only canonical_value (the value aggregation code consumes) is excluded.
    """
    fmt = lane_row["answer_format"]
    group = lane_row["group"]
    note = ""

    if fmt == "numeric":
        raw_value = parse_numeric(raw_text)
        if raw_value is None:
            raw_value = "NA"
            canonical_value = "NA"
            note = "unparseable_numeric"
        else:
            if not (0 <= raw_value <= 10):
                note = "out_of_range_0_10"
            if group == "rev":
                canonical_value = 10 - raw_value
            else:
                canonical_value = raw_value
            if token_collision_undefined:
                canonical_value = "UNDEFINED_TOKEN_COLLISION"
                collision_note = ("token_collision_undefined (PREREG r4 / vocab SCHEMA.md: "
                                   "distance identically 0 by shared token, not a measurement, excluded)")
                note = f"{note};{collision_note}" if note else collision_note
    else:  # word
        raw_value = parse_word(raw_text)
        if raw_value is None:
            raw_value = "NA"
            canonical_value = "NA"
            note = "unparseable_word"
        else:
            canonical_value = raw_value  # no polarity flip for word-type answers

    return {
        "question_id": lane_row["question_id"],
        "basis_id": lane_row["basis_id"],
        "head": lane_row["head"],
        "rep": lane_row["rep"],
        "group": group,
        "raw_value": raw_value,
        "canonical_value": canonical_value,
        "lane_id": lane_row["lane_id"],
        "room_id": room_id,
        "timestamp": file_timestamp(raw_path),
        "note": note,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--dispatch-map", required=True,
                     help="lane_id<->room_id provenance TSV (required, PREREG r3 DEFECT4 fix). "
                          "Refuses to code without it.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--vocab", default=DEFAULT_VOCAB_PATH,
                     help="vocab.json for the token_collision UNDEFINED guard (PREREG r4). "
                          "Defaults to scripts/vocab.json next to this script (CWD-independent).")
    ap.add_argument("--questions", default=DEFAULT_QUESTIONS_PATH,
                     help="questions.json for the token_collision UNDEFINED guard (PREREG r4). "
                          "Defaults to scripts/questions.json next to this script (CWD-independent).")
    args = ap.parse_args()

    vocab = load_vocab(args.vocab)
    questions = load_questions(args.questions)
    distance_pair_collision_ids = build_distance_pair_collision_ids(questions, vocab["words"])

    manifest = load_manifest(args.manifest)
    missing = [lane_id for lane_id in manifest
               if not os.path.exists(os.path.join(args.raw_dir, f"{lane_id}.txt"))]
    lane_ids_to_code = [lane_id for lane_id in manifest if lane_id not in missing]

    dispatch_rows = load_dispatch_map(args.dispatch_map)
    try:
        lane_to_room = validate_dispatch_map(dispatch_rows, lane_ids_to_code)
    except DispatchIntegrityError as e:
        print(f"FAIL: dispatch-map integrity check failed, refusing to write {args.out}: {e}",
              file=sys.stderr)
        sys.exit(1)

    rows = []
    for lane_id in lane_ids_to_code:
        lane_row = manifest[lane_id]
        raw_path = os.path.join(args.raw_dir, f"{lane_id}.txt")
        with open(raw_path, encoding="utf-8") as f:
            raw_text = f.read()
        collision_ids = distance_pair_collision_ids.get(lane_row["question_id"])
        is_collision = False
        if collision_ids is not None:
            id_a, id_b, tc_a, tc_b = collision_ids
            is_collision = pair_is_token_collision(id_a, id_b, lane_row.get("language", ""), tc_a, tc_b)
        rows.append(code_lane(lane_row, raw_text, raw_path, lane_to_room[lane_id],
                               token_collision_undefined=is_collision))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CODED_FIELDNAMES, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"coded {len(rows)} lanes -> {args.out} (dispatch-map integrity OK, "
          f"{len(lane_to_room)} lane<->room bindings verified 1:1)", file=sys.stderr)
    if missing:
        print(
            f"WARNING: {len(missing)} lanes in manifest have no raw output yet "
            f"(not fabricated, simply not collected): {missing[:5]}"
            + (" ..." if len(missing) > 5 else ""),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
