#!/usr/bin/env bash
# Baseline overfit10: auto-resume + switch GPU on OOM.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/SpatialLM"

PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CONFIG="configs/spatiallm_cad_overfit10_baseline.yaml"
OUT_DIR="saves/deepcad_overfit10_baseline"
LOG="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_train.log"
TARGET_STEPS=2000
# Prefer emptier GPUs first
GPU_CANDIDATES=(5 4 3 0 1 2 6 7)

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
unset CAD_USE_EDGE_SCORE

pick_gpu() {
  local best=-1 best_free=0 free
  for g in "${GPU_CANDIDATES[@]}"; do
    free=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
      | awk -F', ' -v id="$g" '$1==id {print $2; exit}')
    [[ -z "${free:-}" ]] && continue
    if (( free > best_free )); then
      best_free=$free
      best=$g
    fi
  done
  if (( best < 0 )); then
    echo "5"
  else
    echo "$best"
  fi
}

latest_ckpt() {
  ls -d "$OUT_DIR"/checkpoint-* 2>/dev/null | sort -V | tail -1 || true
}

is_done() {
  [[ -d "$OUT_DIR/checkpoint-${TARGET_STEPS}" ]] && return 0
  [[ -f "$OUT_DIR/trainer_state.json" ]] && \
    python3 - <<PY
import json
from pathlib import Path
st = json.loads(Path("$OUT_DIR/trainer_state.json").read_text())
print(st.get("global_step", 0) >= $TARGET_STEPS)
PY
}

train_once() {
  local gpu="$1"
  local ckpt="${2:-}"
  local extra=()
  if [[ -n "$ckpt" && -d "$ckpt" ]]; then
    extra+=(--resume_from_checkpoint "$ckpt")
    echo "[$(date '+%F %T')] Resume from $ckpt on GPU $gpu" | tee -a "$LOG"
  else
    echo "[$(date '+%F %T')] Fresh start on GPU $gpu" | tee -a "$LOG"
  fi
  CUDA_VISIBLE_DEVICES="$gpu" "$PYTHON" train.py "$CONFIG" "${extra[@]}" >> "$LOG" 2>&1
}

echo "[$(date '+%F %T')] Resilient baseline overfit10 watcher started" >> "$LOG"

while ! is_done | grep -q True; do
  if is_done | grep -q True; then
    break
  fi

  running=$(pgrep -f "train.py ${CONFIG}" || true)
  if [[ -n "$running" ]]; then
    echo "[$(date '+%F %T')] Training already running (pid $running), waiting..." >> "$LOG"
    while pgrep -f "train.py ${CONFIG}" >/dev/null 2>&1; do
      sleep 30
      if is_done | grep -q True; then
        echo "[$(date '+%F %T')] Training complete." >> "$LOG"
        exit 0
      fi
    done
    sleep 5
    continue
  fi

  gpu=$(pick_gpu)
  ckpt=$(latest_ckpt)
  set +e
  train_once "$gpu" "$ckpt"
  rc=$?
  set -e

  if is_done | grep -q True; then
    echo "[$(date '+%F %T')] Done at step >= $TARGET_STEPS" >> "$LOG"
    exit 0
  fi

  if tail -40 "$LOG" | grep -qi "OutOfMemoryError\|CUDA out of memory"; then
    echo "[$(date '+%F %T')] OOM on GPU $gpu (exit $rc), switching GPU..." >> "$LOG"
    sleep 10
    continue
  fi

  if [[ $rc -ne 0 ]]; then
    echo "[$(date '+%F %T')] Non-OOM failure (exit $rc), retry in 30s..." >> "$LOG"
    sleep 30
    continue
  fi

  echo "[$(date '+%F %T')] Train exited cleanly but not finished; retry..." >> "$LOG"
  sleep 5
done

echo "[$(date '+%F %T')] Baseline overfit10 finished." >> "$LOG"
