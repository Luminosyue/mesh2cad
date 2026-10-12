#!/usr/bin/env bash
# Launch isolated Qwen V3-1k B0/B1/M2 on the emptiest GPUs. Does not touch Llama V3.
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
PY=/usr/bin/python3
export PYTHONPATH="$ROOT/SpatialLM:$ROOT/scripts:$ROOT/scripts/spatiallm_geometry_prefix_v3:$ROOT/scripts/spatiallm_geometry_prefix_v3_qwen"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1
RUN="$ROOT/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/qwen05_v3_1k"
LOG="$RUN/logs"
mkdir -p "$LOG"

free_gpus() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
    | awk -F',' '{gsub(/ /,"",$1); gsub(/ /,"",$2); print $2,$1}' \
    | sort -nr
}

pick_gpu() {
  local min_free=${1:-18000}
  free_gpus | awk -v m="$min_free" '$1+0>=m {print $2; exit}'
}

echo "[$(date '+%F %T')] init base" | tee -a "$LOG/pipeline.log"
if [ ! -f "$RUN/QWEN_GEOMETRY_BASE_V1/BASE_CONTRACT.json" ]; then
  "$PY" "$ROOT/scripts/spatiallm_geometry_prefix_v3_qwen/init_qwen_geometry_base.py"
fi

GPU=$(pick_gpu 12000)
if [ -z "${GPU:-}" ]; then
  echo "no GPU with >=12GB free" >&2
  nvidia-smi --query-gpu=index,memory.free --format=csv
  exit 1
fi
echo "[$(date '+%F %T')] prepare assets on GPU $GPU" | tee -a "$LOG/pipeline.log"
CUDA_VISIBLE_DEVICES="$GPU" "$PY" "$ROOT/scripts/spatiallm_geometry_prefix_v3_qwen/prepare_qwen_v3_assets.py" --device cuda:0

NORM=$(python3 -c "import json; print(json.load(open('$RUN/norm_reference_v1/SURFACE_REFERENCE_NORM.json'))['median'])")
echo "[$(date '+%F %T')] target_norm=$NORM" | tee -a "$LOG/pipeline.log"

launch_arm() {
  local arm=$1 gpu=$2
  local out="$RUN/runs/${arm}"
  if [ -f "$out/TRAINING_REPORT.json" ] && grep -q '"status": "PASS"' "$out/TRAINING_REPORT.json"; then
    echo "skip $arm already PASS"
    return 0
  fi
  rm -rf "$out"
  echo "[$(date '+%F %T')] train $arm on GPU $gpu" | tee -a "$LOG/pipeline.log"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/scripts/spatiallm_geometry_prefix_v3_qwen/train_v3_qwen_1k.py" \
    --arm "$arm" --output "$out" --device cuda:0 --epochs 10 --target-norm "$NORM" \
    >"$LOG/${arm}.log" 2>&1
}

# Sequential on one GPU if only one is free; otherwise one arm per GPU.
mkdir -p "$RUN/runs"
mapfile -t GPUS < <(free_gpus | awk '$1+0>=18000 {print $2}')
if [ "${#GPUS[@]}" -ge 3 ]; then
  launch_arm b0 "${GPUS[0]}" &
  launch_arm b1 "${GPUS[1]}" &
  launch_arm m2 "${GPUS[2]}" &
  wait
elif [ "${#GPUS[@]}" -ge 1 ]; then
  g="${GPUS[0]}"
  launch_arm b0 "$g"
  launch_arm b1 "$g"
  launch_arm m2 "$g"
else
  echo "no GPU with >=18GB free for training" >&2
  exit 1
fi
echo "[$(date '+%F %T')] ALL_QWEN_V3_DONE" | tee -a "$LOG/pipeline.log"
