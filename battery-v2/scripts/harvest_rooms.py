#!/usr/bin/env python3
"""
harvest_rooms.py — battery-v2 段A: room-transcript harvester.

Mechanism (operator instruction 2026-08-07, memory `ledgers/ghoul-sonnet.md`):
room state lives on disk at ~/.gaia/rooms/<room_id>/transcript.jsonl regardless
of whether the summon-completion event has been delivered back into the caller's
own room. Firing many `gaia summon` calls fire-and-forget (their room_id is
printed synchronously to stdout the instant they are launched -- no need to wait
for completion to learn it), recording room_id<->lane_id to a dispatch-map, and
later reading transcript.jsonl straight from disk lets ONE lane-agent dispatch
an arbitrary number of lanes without funnelling every reply through its own
context window one re-invocation at a time.

For each dispatch-map row (sub_room_id, lane_id -- same 2-column schema consumed
by scripts/code_outputs.py --dispatch-map):
  - room dir or transcript.jsonl missing         -> status=room_missing (uncollected)
  - transcript.jsonl has no non-"user"-authored
    line yet (worker still running)              -> status=pending (uncollected)
  - transcript.jsonl has >=1 non-"user" line      -> status=collected, writes
    raw/<lane_id>.txt with the LAST such line's `text` verbatim (no fabrication;
    if the agent's reply is empty string, empty string is written, not skipped).

Never invents a missing answer. Always writes a harvest-report.tsv enumerating
every dispatch-map row's outcome, so "uncollected" is an explicit, auditable
status rather than a silent gap.

Usage:
    python3 harvest_rooms.py --dispatch-map DISPATCH.tsv --raw-dir RAWDIR \
        [--rooms-dir ~/.gaia/rooms] [--report harvest-report.tsv]
"""
import argparse
import csv
import json
import os
import sys


def default_rooms_dir():
    return os.path.expanduser("~/.gaia/rooms")


def load_dispatch_map(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return [(row["sub_room_id"], row["lane_id"]) for row in reader]


def last_agent_reply(transcript_path):
    """Read transcript.jsonl, return the `text` of the LAST line whose author is
    present and != 'user'. Returns None if no such line exists yet (still
    pending) -- lines that fail to parse as JSON are skipped, not fatal (a
    worker's transcript file can in principle be mid-write; a partial trailing
    line must not crash the harvest of every other room in the batch)."""
    reply = None
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            author = evt.get("author")
            if author and author != "user":
                text = evt.get("text")
                if text is not None:
                    reply = text
    return reply


def harvest(dispatch_rows, raw_dir, rooms_dir):
    """Returns list of dict rows: sub_room_id, lane_id, status, raw_path (or '')."""
    os.makedirs(raw_dir, exist_ok=True)
    results = []
    for room_id, lane_id in dispatch_rows:
        room_dir = os.path.join(rooms_dir, room_id)
        transcript_path = os.path.join(room_dir, "transcript.jsonl")
        if not os.path.isdir(room_dir) or not os.path.exists(transcript_path):
            results.append({"sub_room_id": room_id, "lane_id": lane_id,
                             "status": "room_missing", "raw_path": ""})
            continue
        reply = last_agent_reply(transcript_path)
        if reply is None:
            results.append({"sub_room_id": room_id, "lane_id": lane_id,
                             "status": "pending", "raw_path": ""})
            continue
        raw_path = os.path.join(raw_dir, f"{lane_id}.txt")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(reply)
        results.append({"sub_room_id": room_id, "lane_id": lane_id,
                         "status": "collected", "raw_path": raw_path})
    return results


REPORT_FIELDNAMES = ["sub_room_id", "lane_id", "status", "raw_path"]


def write_report(results, report_path):
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REPORT_FIELDNAMES, delimiter="\t")
        w.writeheader()
        for r in results:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dispatch-map", required=True)
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--rooms-dir", default=default_rooms_dir())
    ap.add_argument("--report", default=None,
                     help="default: <parent of raw-dir>/harvest-report.tsv")
    args = ap.parse_args()

    dispatch_rows = load_dispatch_map(args.dispatch_map)
    results = harvest(dispatch_rows, args.raw_dir, args.rooms_dir)

    report_path = args.report or os.path.join(
        os.path.dirname(args.raw_dir.rstrip("/")) or ".", "harvest-report.tsv"
    )
    write_report(results, report_path)

    n_collected = sum(1 for r in results if r["status"] == "collected")
    n_pending = sum(1 for r in results if r["status"] == "pending")
    n_missing = sum(1 for r in results if r["status"] == "room_missing")
    print(
        f"harvested {n_collected}/{len(results)} (pending={n_pending}, room_missing={n_missing}) "
        f"-> {args.raw_dir}, report -> {report_path}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
