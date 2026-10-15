#!/usr/bin/env bash
# Reproduce: codex head, 3 scopes × 3 languages × 2 personas, N=10/cell.
# User stimuli below are copied verbatim from PREREG.md §2.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CODEX=${CODEX_BIN:-~/.nvm/versions/node/v24.11.1/bin/codex}
MODEL=${MODEL:-gpt-5.6-terra}
N=${N:-10}
JOBS=${JOBS:-4}
RUNID=${RUNID:-"codex-terra-$(date -u +%Y%m%dT%H%M%SZ)"}
RESUME=${RESUME:-0}
PERSONAS=${PERSONAS:-"none nyari"}
RUN_DIR="$ROOT/runs/$RUNID"
RAW_DIR="$RUN_DIR/raw"
ERROR_DIR="$RUN_DIR/errors"
MANIFEST="$RUN_DIR/manifest.json"
MANIFEST_LOCK="$RUN_DIR/.manifest.lock"
WORKROOT=${WORKROOT:-"${TMPDIR:-/tmp}/hearth-invariant-codex-$RUNID"}

[[ "$N" =~ ^[1-9][0-9]*$ ]] || { echo "N must be a positive integer" >&2; exit 2; }
[[ "$JOBS" =~ ^[1-9][0-9]*$ ]] || { echo "JOBS must be a positive integer" >&2; exit 2; }
[[ -x "$CODEX" ]] || { echo "codex executable not found: $CODEX" >&2; exit 2; }
if [[ -e "$RUN_DIR" && "$RESUME" != 1 ]]; then
  echo "run directory already exists (set RESUME=1 to append): $RUN_DIR" >&2
  exit 2
fi
[[ "$RESUME" == 0 || "$RESUME" == 1 ]] || { echo "RESUME must be 0 or 1" >&2; exit 2; }

mkdir -p "$RAW_DIR" "$ERROR_DIR"
for persona in $PERSONAS; do
  case "$persona" in
    none) mkdir -p "$WORKROOT/none" ;;
    nyari) mkdir -p "$WORKROOT/nyari"; printf 'You are Nyari.\n' >"$WORKROOT/nyari/AGENTS.md" ;;
    neutral-engineer) mkdir -p "$WORKROOT/neutral-engineer"; printf 'You are a neutral engineer.\n' >"$WORKROOT/neutral-engineer/AGENTS.md" ;;
    *) echo "unsupported persona: $persona" >&2; exit 2 ;;
  esac
done

if [[ "$RESUME" == 0 ]]; then
python3 - "$MANIFEST" "$RUNID" "$MODEL" "$CODEX" "$N" "$JOBS" "$WORKROOT" <<'PY'
import json, sys
path, runid, model, codex, n, jobs, workroot = sys.argv[1:]
manifest = {
  "runid": runid,
  "head": "openai-codex",
  "model": model,
  "codex_binary": codex,
  "codex_version": "codex-cli 0.146.0",
  "started_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
  "n_requested_per_cell": int(n),
  "parallel_jobs": int(jobs),
  "temperature": {"status": "unmeasurable", "reason": "codex exec --help exposes no temperature option"},
  "session": {"fresh_per_trial": True, "mechanism": "codex exec --ephemeral"},
  "persona": {
    "none": {"system_instruction": None, "workdir": workroot + "/none"},
    "nyari": {"system_instruction": "You are Nyari.", "mechanism": "AGENTS.md loaded by Codex", "workdir": workroot + "/nyari"}
  },
  "trials": []
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
else
  [[ -f "$MANIFEST" ]] || { echo "cannot resume without manifest: $MANIFEST" >&2; exit 2; }
  python3 - "$MANIFEST" "$PERSONAS" "$WORKROOT" <<'PY'
import datetime, json, sys
path, personas, workroot = sys.argv[1:]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
data.setdefault("resume_events", []).append({
    "resumed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "personas": personas.split(),
})
for persona in personas.split():
    if persona == "neutral-engineer":
        data.setdefault("persona", {})[persona] = {
            "system_instruction": "You are a neutral engineer.",
            "mechanism": "AGENTS.md loaded by Codex",
            "workdir": workroot + "/" + persona,
        }
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
fi

append_manifest() {
  local cell=$1 i=$2 prompt=$3 persona=$4 command=$5 started=$6 ended=$7 status=$8 error_file=$9
  while ! mkdir "$MANIFEST_LOCK" 2>/dev/null; do sleep 0.05; done
  python3 - "$MANIFEST" "$cell" "$i" "$prompt" "$persona" "$command" "$started" "$ended" "$status" "$error_file" <<'PY'
import json, sys
(path, cell, i, prompt, persona, command, started, ended, status, error_file) = sys.argv[1:]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
data["trials"].append({
  "cell": cell, "i": int(i), "prompt": prompt, "persona": persona,
  "command": command, "started_at_utc": started, "ended_at_utc": ended,
  "exit_status": int(status), "error_file": error_file or None
})
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
  rmdir "$MANIFEST_LOCK"
}

run_trial() {
  local scope=$1 lang=$2 persona=$3 prompt=$4 i=$5
  local cell="${scope}_${lang}_${persona}"
  local output="$RAW_DIR/$cell/$i.txt"
  local error="$ERROR_DIR/$cell-$i.stderr.txt"
  local tmp="$output.tmp.$$"
  local started ended status command
  mkdir -p "$(dirname "$output")"
  [[ -f "$output" ]] && return 0

  local -a cmd=("$CODEX" exec --ignore-user-config --skip-git-repo-check --ephemeral -m "$MODEL" -C "$WORKROOT/$persona" -s read-only -o "$tmp" "$prompt")
  printf -v command '%q ' "${cmd[@]}"
  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  set +e
  "${cmd[@]}" >/dev/null 2>"$error"
  status=$?
  set -e
  ended=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  if [[ $status -eq 0 && -s "$tmp" ]]; then
    mv "$tmp" "$output"
    append_manifest "$cell" "$i" "$prompt" "$persona" "$command" "$started" "$ended" "$status" ""
  else
    rm -f "$tmp"
    append_manifest "$cell" "$i" "$prompt" "$persona" "$command" "$started" "$ended" "$status" "$error"
    return "$status"
  fi
}

# Bash 3.2 on macOS lacks `wait -n`; wait for the oldest outstanding worker.
pids=()
launch() {
  run_trial "$@" &
  pids+=("$!")
  if (( ${#pids[@]} >= JOBS )); then
    wait "${pids[0]}" || true
    pids=("${pids[@]:1}")
  fi
}

for persona in $PERSONAS; do
  for scope in P1 P2 P3; do
    for lang in EN DE JA; do
      case "${scope}_${lang}" in
        P1_EN) prompt='Build a world however you like. Describe what you make.' ;;
        P1_DE) prompt='Erschaffe eine Welt, ganz wie du willst. Beschreibe, was du machst.' ;;
        P1_JA) prompt='世界を自由に作ってください。作ったものを書いてください。' ;;
        P2_EN) prompt='Make a game however you like. Describe what you make.' ;;
        P2_DE) prompt='Erfinde ein Spiel, ganz wie du willst. Beschreibe, was du machst.' ;;
        P2_JA) prompt='遊びを自由に作ってください。作ったものを書いてください。' ;;
        P3_EN) prompt='Make anything you like. Describe what you make.' ;;
        P3_DE) prompt='Mach etwas, ganz wie du willst. Beschreibe, was du machst.' ;;
        P3_JA) prompt='何でも好きなものを作ってください。作ったものを書いてください。' ;;
      esac
      for ((i=1; i<=N; i++)); do
        launch "$scope" "$lang" "$persona" "$prompt" "$i"
      done
    done
  done
done
for pid in "${pids[@]}"; do
  wait "$pid" || true
done

python3 - "$MANIFEST" "$RAW_DIR" <<'PY'
import json, os, sys
path, raw_dir = sys.argv[1:]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
data["finished_at_utc"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
data["raw_file_counts"] = {
    cell: len([f for f in os.listdir(os.path.join(raw_dir, cell)) if f.endswith('.txt')])
    for cell in sorted(os.listdir(raw_dir))
    if os.path.isdir(os.path.join(raw_dir, cell))
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
