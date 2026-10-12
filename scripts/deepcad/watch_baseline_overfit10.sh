#!/usr/bin/env bash
# Watch baseline overfit10 retrain: OOM→switch GPU; done→decode.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/SpatialLM"

PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CONFIG="configs/spatiallm_cad_overfit10_baseline.yaml"
OUT_DIR="saves/deepcad_overfit10_baseline"
LOG="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_retrain.log"
WATCH_LOG="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_watch.log"
TARGET_STEPS=2000
GPU_CANDIDATES=(5 4 1 3 0 2 6 7)
DECODE_PY="$ROOT/scripts/deepcad/decode_overfit10.py"

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
unset CAD_USE_EDGE_SCORE

pick_gpu() {
  local best=-1 best_free=0 free
  for g in "${GPU_CANDIDATES[@]}"; do
    free=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
      | awk -F', ' -v id="$g" '$1==id {gsub(/ /,"",$2); print $2; exit}')
    [[ -z "${free:-}" ]] && continue
    if (( free > best_free )); then
      best_free=$free
      best=$g
    fi
  done
  echo "${best:--1}"
}

latest_ckpt() {
  ls -d "$OUT_DIR"/checkpoint-* 2>/dev/null | sort -V | tail -1 || true
}

is_done() {
  [[ -f "$OUT_DIR/all_results.json" ]] && return 0
  [[ -d "$OUT_DIR/checkpoint-${TARGET_STEPS}" ]] || return 1
  [[ -f "$OUT_DIR/checkpoint-${TARGET_STEPS}/model.safetensors.index.json" \
     || -f "$OUT_DIR/checkpoint-${TARGET_STEPS}/model.safetensors" \
     || -f "$OUT_DIR/model.safetensors.index.json" ]]
}

train_pid_running() {
  pgrep -f "train.py ${CONFIG}" >/dev/null 2>&1
}

decode_baseline() {
  local ckpt="$OUT_DIR/checkpoint-${TARGET_STEPS}"
  [[ -d "$ckpt" ]] || ckpt="$OUT_DIR"
  local gpu
  gpu=$(pick_gpu)
  echo "[$(date '+%F %T')] Decode baseline on GPU $gpu from $ckpt" | tee -a "$WATCH_LOG"
  CUDA_VISIBLE_DEVICES="$gpu" "$PYTHON" "$DECODE_PY" \
    --checkpoint "$ckpt" \
    --variant baseline \
    --train-json "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_overfit10_train.json" \
    2>&1 | tee -a "$WATCH_LOG"
}

echo "[$(date '+%F %T')] Watcher started" >> "$WATCH_LOG"

# Single-instance lock
LOCK=/tmp/watch_baseline_overfit10.lock
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date '+%F %T')] Another watcher holds lock; exit" >> "$WATCH_LOG"
  exit 0
fi

echo "[$(date '+%F %T')] Watcher started (locked)" >> "$WATCH_LOG"

while true; do
  if is_done; then
    echo "[$(date '+%F %T')] Training complete." | tee -a "$WATCH_LOG"
    # restore overwrite for future runs
    decode_baseline
    exit 0
  fi

  if train_pid_running; then
    sleep 90
    continue
  fi

  sleep 20
  if train_pid_running || is_done; then
    continue
  fi

  if tail -80 "$LOG" 2>/dev/null | grep -qi "OutOfMemoryError\|CUDA out of memory"; then
    echo "[$(date '+%F %T')] Detected OOM; will resume on freer GPU" | tee -a "$WATCH_LOG"
  else
    echo "[$(date '+%F %T')] Train not running; resume attempt" | tee -a "$WATCH_LOG"
  fi

  gpu=$(pick_gpu)
  ckpt=$(latest_ckpt)
  if (( gpu < 0 )); then
    sleep 90
    continue
  fi
  free=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
    | awk -F', ' -v id="$gpu" '$1==id {gsub(/ /,"",$2); print $2; exit}')
  if (( free < 30000 )); then
    echo "[$(date '+%F %T')] GPU $gpu free=${free}MB < 30GB; wait" | tee -a "$WATCH_LOG"
    sleep 90
    continue
  fi

  # Update yaml resume pointer to latest ckpt
  if [[ -n "$ckpt" && -d "$ckpt" ]]; then
    python3 - <<PY
from pathlib import Path
p = Path("configs/spatiallm_cad_overfit10_baseline.yaml")
text = p.read_text()
import re
text = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", text, flags=re.M)
if "resume_from_checkpoint:" in text:
    text = re.sub(r"^resume_from_checkpoint:.*$", f"resume_from_checkpoint: {ckpt}", text, flags=re.M)
else:
    text = text.replace("overwrite_output_dir: false", f"overwrite_output_dir: false\nresume_from_checkpoint: {ckpt}")
p.write_text(text)
print("patched resume ->", ckpt)
PY
    echo "[$(date '+%F %T')] Resume $ckpt on GPU $gpu (free=${free}MB)" | tee -a "$WATCH_LOG"
  else
    echo "[$(date '+%F %T')] Fresh train on GPU $gpu" | tee -a "$WATCH_LOG"
  fi

  if train_pid_running; then
    continue
  fi

  set +e
  CUDA_VISIBLE_DEVICES="$gpu" "$PYTHON" train.py "$CONFIG" >> "$LOG" 2>&1
  rc=$?
  set -e
  echo "[$(date '+%F %T')] Train exit=$rc" | tee -a "$WATCH_LOG"
  sleep 20
done
