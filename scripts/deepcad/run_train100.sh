#!/usr/bin/env bash
# Train100: baseline then ours. Snatch GPU, OOM→换卡续训.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/DeepCAD"
SNATCH_LOG="$LOG_DIR/train100_snatch.log"
LOCK=/tmp/train100_snatch.lock
MIN_FREE="${MIN_FREE:-28000}"
POLL_SEC="${POLL_SEC:-2}"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] train100 snatch already running"; exit 0; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG"; }

best_gpu() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1
}

wait_gpu() {
  while true; do
    read -r FREE GPU <<<"$(best_gpu)"
    FREE=${FREE:-0}; GPU=${GPU:--1}
    if (( FREE >= MIN_FREE )); then
      echo "$GPU"
      return 0
    fi
    log "wait GPU… best=${GPU} free=${FREE}MB need>=${MIN_FREE}"
    sleep "$POLL_SEC"
  done
}

# Ensure datasets exist
cd "$ROOT"
python3 scripts/deepcad/create_spatiallm_cad_dataset.py \
  --variant ours --val-ratio 0.2 --name-suffix train100 --seed 42
python3 scripts/deepcad/create_spatiallm_cad_dataset.py \
  --variant baseline --val-ratio 0.2 --name-suffix train100 --seed 42

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd "$ROOT/SpatialLM"

run_variant() {
  local cfg="$1"
  local tag="$2"
  local out_dir="$3"
  local logfile="$LOG_DIR/train100_${tag}.log"
  local edge_env="$4"  # 1 or empty

  mkdir -p "$out_dir"
  : > "$logfile"  # keep history? append instead
  log "=== START variant=$tag cfg=$cfg ==="

  # Pass 1: preprocess (exits after save_dir write if empty)
  if [[ ! -f "$out_dir/dataset_dict.json" ]]; then
    GPU=$(wait_gpu)
    log "[$tag] preprocess on GPU=$GPU"
    if [[ "$edge_env" == "1" ]]; then export CAD_USE_EDGE_SCORE=1; else unset CAD_USE_EDGE_SCORE; fi
    # ensure overwrite true for first preprocess
    python3 - <<PY
from pathlib import Path
import re
p = Path("$cfg")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: true", t, flags=re.M)
t = re.sub(r"^resume_from_checkpoint:.*\n?", "", t, flags=re.M)
p.write_text(t)
PY
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$cfg" >> "$logfile" 2>&1 || true
  fi

  # Switch to auto-resume mode
  python3 - <<PY
from pathlib import Path
import re
p = Path("$cfg")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", t, flags=re.M)
t = re.sub(r"^resume_from_checkpoint:.*\n?", "", t, flags=re.M)
p.write_text(t)
print("overwrite=false for auto-resume")
PY

  # Train until done
  while true; do
    if [[ -f "$out_dir/all_results.json" ]]; then
      log "[$tag] DONE"
      return 0
    fi
    # any last checkpoint exists and trainer finished?
    if [[ -f "$out_dir/train_results.json" ]]; then
      log "[$tag] DONE (train_results)"
      return 0
    fi

    if pgrep -f "train.py ${cfg}" >/dev/null 2>&1; then
      sleep 30
      continue
    fi

    GPU=$(wait_gpu)
    log "[$tag] LAUNCH train on GPU=$GPU"
    if [[ "$edge_env" == "1" ]]; then export CAD_USE_EDGE_SCORE=1; else unset CAD_USE_EDGE_SCORE; fi
    set +e
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$cfg" >> "$logfile" 2>&1
    rc=$?
    set -e
    log "[$tag] train exit=$rc"

    if [[ -f "$out_dir/all_results.json" || -f "$out_dir/train_results.json" ]]; then
      log "[$tag] DONE"
      return 0
    fi
    if tail -80 "$logfile" | grep -qi "OutOfMemoryError\|CUDA out of memory"; then
      log "[$tag] OOM — re-snatch"
      sleep 2
      continue
    fi
    sleep 5
  done
}

log "train100 pipeline start"
run_variant configs/spatiallm_cad_train100_baseline.yaml baseline \
  saves/deepcad_train100_baseline ""
run_variant configs/spatiallm_cad_train100_ours.yaml ours \
  saves/deepcad_train100_ours 1
log "ALL DONE: baseline + ours train100"
echo "Saves: SpatialLM/saves/deepcad_train100_{baseline,ours}/"
