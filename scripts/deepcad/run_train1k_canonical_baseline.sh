#!/usr/bin/env bash
# DEEPCAD_1K_CANONICAL_V1 — 6ch baseline (same split as ours).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CADPY="${CADPY:-/data/miniconda3/envs/cadfit-env/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/DeepCAD"
MANIFEST="$ROOT/cad_spatial_dataset/DeepCAD/manifest_train1k_v1.json"
SPLIT="$ROOT/cad_spatial_dataset/DeepCAD/split_train1k_complexity_seed42.json"
CFG="configs/spatiallm_cad_train1k_canonical_baseline.yaml"
OUT="saves/deepcad_train1k_canonical_baseline"
LOG="$LOG_DIR/train1k_canonical_baseline.log"
SNATCH_LOG="$LOG_DIR/train1k_canonical_baseline_snatch.log"
LOCK=/tmp/train1k_canonical_baseline_snatch.lock
MIN_FREE="${MIN_FREE:-30000}"
PREFERRED_GPU="${PREFERRED_GPU:-}"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] train1k baseline snatch already running"; exit 0; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG" >&2; }

best_gpu() {
  nvidia-smi --query-gpu=index,memory.free,utilization.gpu --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' '{
        gsub(/ /,"",$2); gsub(/ /,"",$3);
        if ($2+0 >= '"$MIN_FREE"' && $3+0 <= 10) print $2,$1
      }' | sort -nr | head -1
}

wait_gpu() {
  if [[ -n "$PREFERRED_GPU" ]]; then
    read -r FREE _ <<<"$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i "$PREFERRED_GPU" 2>/dev/null | awk '{print $1}')"
    FREE=${FREE:-0}
    if (( FREE >= MIN_FREE )); then echo "$PREFERRED_GPU"; return 0; fi
  fi
  while true; do
    read -r FREE GPU <<<"$(best_gpu)"
    FREE=${FREE:-0}; GPU=${GPU:--1}
    if (( FREE >= MIN_FREE )); then echo "$GPU"; return 0; fi
    echo "[$(date '+%F %T')] wait GPU free=${FREE}MB need>=${MIN_FREE}" >> "$SNATCH_LOG"
    sleep 3
  done
}

[[ -f "$SPLIT" ]] || "$PYTHON" scripts/deepcad/build_train1k_complexity_split.py

log "=== ShareGPT JSON (baseline) ==="
"$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
  --manifest "$MANIFEST" \
  --split-json "$SPLIT" \
  --variant baseline \
  --name-suffix train1k

export DISABLE_VERSION_CHECK=1
unset CAD_USE_EDGE_SCORE
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd "$ROOT/SpatialLM"
mkdir -p "$OUT"

log "=== train DEEPCAD_1K baseline ==="
while true; do
  if [[ -f "$OUT/all_results.json" || -f "$OUT/train_results.json" ]]; then
    log "DONE"; break
  fi
  if pgrep -f "train.py ${CFG}" >/dev/null 2>&1; then sleep 30; continue; fi
  GPU=$(wait_gpu)
  log "LAUNCH GPU=$GPU"
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$LOG" 2>&1 || true
  if tail -80 "$LOG" 2>/dev/null | grep -qi "OutOfMemoryError"; then sleep 2; continue; fi
  sleep 5
done

log "ALL DONE: $OUT"
