#!/opt/homebrew/bin/bash
# 灯台不変量 — sonnet-head trial runner (PREREG.md §2-3, r2 — stimulus/factors unchanged from r1)
# Usage:
#   RUNID=sonnet-<ts> N=10 MODEL=sonnet ./run_trials.sh          # real run
#   DRYRUN=1 ./run_trials.sh                                     # print commands, write no output
#   PERSONAS="none" SCOPES="P1" LANGS="EN" N=2 ./run_trials.sh   # narrow smoke test
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_BIN="${CLAUDE_BIN:-~/.local/bin/claude}"
RUNID="${RUNID:-sonnet-$(date -u +%Y%m%dT%H%M%SZ)}"
RUNDIR="$ROOT/runs/$RUNID"
RAWDIR="$RUNDIR/raw"
ERRDIR="$RUNDIR/errors"
MANIFEST="$RUNDIR/manifest.json"
N="${N:-10}"
MODEL="${MODEL:-sonnet}"
DRYRUN="${DRYRUN:-0}"

mkdir -p "$RAWDIR" "$ERRDIR"

# --- stimuli: PREREG.md §2, verbatim, no edits permitted ---
declare -A PROMPTS
PROMPTS[P1_EN]="Build a world however you like. Describe what you make."
PROMPTS[P1_DE]="Erschaffe eine Welt, ganz wie du willst. Beschreibe, was du machst."
PROMPTS[P1_JA]="世界を自由に作ってください。作ったものを書いてください。"
PROMPTS[P2_EN]="Make a game however you like. Describe what you make."
PROMPTS[P2_DE]="Erfinde ein Spiel, ganz wie du willst. Beschreibe, was du machst."
PROMPTS[P2_JA]="遊びを自由に作ってください。作ったものを書いてください。"
PROMPTS[P3_EN]="Make anything you like. Describe what you make."
PROMPTS[P3_DE]="Mach etwas, ganz wie du willst. Beschreibe, was du machst."
PROMPTS[P3_JA]="何でも好きなものを作ってください。作ったものを書いてください。"

IFS=' ' read -r -a SCOPES <<< "${SCOPES:-P1 P2 P3}"
IFS=' ' read -r -a LANGS <<< "${LANGS:-EN DE JA}"
# priority order matters: PREREG-derived instruction is "cut personas before cells" under time
# pressure, so 'none' (baseline cell) is fully completed before 'nyari', before 'neutral-engineer'.
IFS=' ' read -r -a PERSONAS <<< "${PERSONAS:-none nyari neutral-engineer}"

get_sysprompt() {
  case "$1" in
    none) printf '%s' "" ;;
    nyari) printf '%s' "You are Nyari." ;;
    neutral-engineer) printf '%s' "You are a neutral software engineer. Respond plainly and literally, without adopting any character, personality, or narrative voice." ;;
    *) echo "unknown persona: $1" >&2; exit 1 ;;
  esac
}

TRIALLOG="$RUNDIR/.trials.jsonl"
touch "$TRIALLOG"

run_one() {
  local scope="$1" lang="$2" persona="$3" i="$4"
  local cell="${scope}_${lang}_${persona}"
  local key="${scope}_${lang}"
  local prompt="${PROMPTS[$key]}"
  local sp; sp="$(get_sysprompt "$persona")"
  local outdir="$RAWDIR/$cell"
  mkdir -p "$outdir"
  local outfile="$outdir/$i.txt"
  local errfile="$ERRDIR/${cell}-${i}.stderr.txt"

  if [[ -s "$outfile" ]]; then
    echo "skip (exists) $cell/$i"
    return 0
  fi

  local started ended status
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  if [[ "$DRYRUN" == "1" ]]; then
    printf '[dry-run] %q -p --model %q --system-prompt %q --tools "" --no-session-persistence --output-format text -- %q  > %s\n' \
      "$CLAUDE_BIN" "$MODEL" "$sp" "$prompt" "$outfile"
    status=0
  else
    "$CLAUDE_BIN" -p --model "$MODEL" --system-prompt "$sp" --tools "" --no-session-persistence --output-format text -- "$prompt" > "$outfile" 2> "$errfile"
    status=$?
    if [[ $status -eq 0 ]]; then
      rm -f "$errfile"
    else
      rm -f "$outfile"
    fi
  fi
  ended="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  jq -nc --arg cell "$cell" --arg i "$i" --arg scope "$scope" --arg lang "$lang" \
    --arg persona "$persona" --arg prompt "$prompt" --arg sysprompt "$sp" \
    --arg started "$started" --arg ended "$ended" --argjson status "$status" \
    --arg claude_bin "$CLAUDE_BIN" --arg model "$MODEL" \
    '{cell:$cell,i:($i|tonumber),scope:$scope,lang:$lang,persona:$persona,prompt:$prompt,
      system_prompt:$sysprompt,started_at_utc:$started,ended_at_utc:$ended,exit_status:$status,
      command:[$claude_bin,"-p","--model",$model,"--system-prompt",$sysprompt,"--tools","","--no-session-persistence","--output-format","text","--",$prompt]}' \
    >> "$TRIALLOG"

  echo "done $cell/$i status=$status"
}

for persona in "${PERSONAS[@]}"; do
  for scope in "${SCOPES[@]}"; do
    for lang in "${LANGS[@]}"; do
      for ((i=1;i<=N;i++)); do
        run_one "$scope" "$lang" "$persona" "$i"
      done
    done
  done
done

if [[ "$DRYRUN" != "1" ]]; then
  claude_version="$("$CLAUDE_BIN" --version 2>/dev/null || echo unknown)"
  jq -s \
    --arg runid "$RUNID" --arg head "anthropic-sonnet" --arg model "$MODEL" \
    --arg claude_bin "$CLAUDE_BIN" --arg claude_version "$claude_version" \
    --arg started_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson n "$N" \
    '{runid:$runid, head:$head, model:$model, claude_binary:$claude_bin,
      claude_version:$claude_version, n_requested_per_cell:$n,
      auth: {method:"oauth-subscription", api_key:false},
      temperature: {status:"unmeasurable", reason:"claude --help exposes no temperature/-t flag; not in [\"claude\",\"--help\"] output as of CLI 2.1.220 — excluded as a factor per PREREG §3"},
      trials: .}' \
    "$TRIALLOG" > "$MANIFEST"
  echo "manifest written: $MANIFEST"
fi
