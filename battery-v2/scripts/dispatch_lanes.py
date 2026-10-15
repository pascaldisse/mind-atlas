#!/usr/bin/env python3
"""
dispatch_lanes.py — battery-v2 段B: fire-and-forget batch summon dispatcher.

Reads a manifest.tsv slice (emit_prompts.py output, optionally pre-filtered to
a subset of lane_ids by the caller) and, for each row NOT already present in
dispatch-map.tsv, launches `gaia summon <agent> "<task>"` via subprocess (a
real dispatch, not a simulation), parses the returned sub-room id from the
CLI's own synchronous stdout (no need to wait for the worker to finish -- the
room id is printed the instant the summon is launched), and appends a
(sub_room_id, lane_id) row to dispatch-map.tsv immediately, flushed after
every single row. A batch that dies partway through still leaves every
already-dispatched row on disk (operator law: "途中で死んでも収集済が生き
残る形にしろ").

1 lane = 1 summon = 1 clean-context sub-room (PREREG DEFECT4 / 弾劾1 fix). A
lane_id already present in dispatch-map.tsv is skipped -- re-running this
script over the same manifest slice is idempotent and never double-dispatches
a lane or lets one room_id serve two lanes.

head -> summon agent id mapping (verified live, see
results/head-availability-20260807.md): claude-sonnet -> naru-sonnet,
claude-opus -> naru-opus, kimi -> naru-kimi, jareth -> jareth.

Task text sent to the worker = lane's system_prompt (if any) + prompt_text +
a minimal format-enforcement suffix (PREREG §9.2 wording, unchanged from the
pilot). No other content is added or altered -- prompt-pool contamination is
avoided by construction (emit_prompts.py already froze the wording).

Usage:
    python3 dispatch_lanes.py --manifest manifest.tsv --dispatch-map dispatch-map.tsv \
        [--limit N] [--sleep-between SECONDS] [--dry-run]
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import time

HEAD_TO_AGENT = {
    "claude-sonnet": "naru-sonnet",
    "claude-opus": "naru-opus",
    "kimi": "naru-kimi",
    "jareth": "jareth",
}

ROOM_ID_RE = re.compile(r"sub-room '([^']+)'")

FORMAT_SUFFIX = (
    "One-off isolated question. Return only the answer in the requested "
    "format, no explanation, no preamble."
)


def load_manifest_rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_dispatched_lane_ids(dispatch_map_path):
    if not os.path.exists(dispatch_map_path):
        return set()
    with open(dispatch_map_path, encoding="utf-8") as f:
        return {row["lane_id"] for row in csv.DictReader(f, delimiter="\t")}


def build_task_text(row):
    parts = []
    if row.get("system_prompt"):
        parts.append(row["system_prompt"].strip())
    parts.append(row["prompt_text"].strip())
    parts.append(FORMAT_SUFFIX)
    return " ".join(parts)


def parse_room_id(stdout):
    m = ROOM_ID_RE.search(stdout)
    return m.group(1) if m else None


def dispatch_one(row, runner=subprocess.run):
    agent = HEAD_TO_AGENT.get(row["head"])
    if agent is None:
        raise ValueError(f"unknown head {row['head']!r}, no agent mapping")
    task = build_task_text(row)
    proc = runner(["gaia", "summon", agent, task], capture_output=True, text=True, timeout=30)
    room_id = parse_room_id(proc.stdout)
    if room_id is None:
        raise RuntimeError(
            f"could not parse room id from summon stdout for lane {row['lane_id']}: "
            f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
        )
    return room_id


def run_batch(rows, dispatch_map_path, sleep_between=0.0, runner=subprocess.run, dry_run=False):
    """Returns (n_ok, n_fail). Appends to dispatch_map_path incrementally, flushing every row."""
    is_new_file = not os.path.exists(dispatch_map_path)
    n_ok, n_fail = 0, 0
    with open(dispatch_map_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        if is_new_file:
            w.writerow(["sub_room_id", "lane_id"])
            f.flush()
        for row in rows:
            if dry_run:
                print(f"DRY-RUN would dispatch {row['lane_id']} (agent={HEAD_TO_AGENT.get(row['head'])})",
                      file=sys.stderr)
                n_ok += 1
                continue
            try:
                room_id = dispatch_one(row, runner=runner)
            except Exception as e:
                print(f"FAIL dispatching {row['lane_id']}: {e}", file=sys.stderr)
                n_fail += 1
                continue
            w.writerow([room_id, row["lane_id"]])
            f.flush()
            n_ok += 1
            print(f"dispatched {row['lane_id']} -> {room_id}", file=sys.stderr)
            if sleep_between:
                time.sleep(sleep_between)
    return n_ok, n_fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--dispatch-map", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sleep-between", type=float, default=0.0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = load_manifest_rows(args.manifest)
    already = load_dispatched_lane_ids(args.dispatch_map)
    todo = [r for r in rows if r["lane_id"] not in already]
    if args.limit is not None:
        todo = todo[: args.limit]

    n_ok, n_fail = run_batch(todo, args.dispatch_map, sleep_between=args.sleep_between, dry_run=args.dry_run)

    print(
        f"dispatch batch done: {n_ok} dispatched, {n_fail} failed, "
        f"{len(already)} already in dispatch-map before this run, "
        f"{len(rows) - len(todo) - len(already)} manifest rows out-of-scope (--limit)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
