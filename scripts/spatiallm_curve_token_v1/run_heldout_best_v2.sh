#!/usr/bin/env bash
# Formal held-out Gate (best_v2): B0 / B1-native / B1-budget-match / M2
#
# Does NOT touch runs/heldout/ or SpatialLM/saves/heldout_curve_*.
# All four arms init from SpatialLM1.1-Llama-1B, keep best-val, early-stop.
#
# Usage:
#   bash scripts/spatiallm_curve_token_v1/run_heldout_best_v2.sh 0 3 4 5
#   # args = GPU for B0  B1-native  B1-budget-match  M2
# Default GPUs avoid 1 and 2, which still host the old B1 last-ckpt diagnostic.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PYTHON_BIN:-/data/miniconda3/envs/spatiallm/bin/python}"
CFG="$ROOT/scripts/spatiallm_curve_token_v1/configs"
RUN="$ROOT/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2"
LAUNCHER="$PY $ROOT/scripts/spatiallm_curve_token_v1/train_heldout_arm.py"
CACHE="$RUN/surface_idx4096.npz"

mkdir -p "$RUN/logs"
# HF save_dir must start empty (or contain only dataset_dict). Do not write logs into it.

GPU_B0="${1:-0}"
GPU_B1N="${2:-3}"
GPU_B1B="${3:-4}"
GPU_M2="${4:-5}"

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export CAD_SURFACE_POINTS=4096
export CAD_HELDOUT_PROTOCOL=best_v2
export CAD_SURFACE_CACHE="$CACHE"
export CAD_ES_PATIENCE=4
export CAD_ES_THRESHOLD=0.0

if [ ! -f "$CACHE" ]; then
  echo "[$(date '+%F %T')] building shared surface index cache → $CACHE"
  "$PY" "$ROOT/scripts/spatiallm_curve_token_v1/build_surface_cache.py" --out "$CACHE"
fi

launch() {
  local name="$1" gpu="$2" cfg="$3" arm_dir="$4"
  shift 4
  local log="$RUN/logs/${name}.log"
  mkdir -p "$RUN/logs"
  if ls -d "$arm_dir"/checkpoint-* >/dev/null 2>&1; then
    echo "REFUSE: $arm_dir already has checkpoints. Formal Gate must start from base, not resume." >&2
    echo "Delete that arm dir only if you intentionally want a fresh run." >&2
    exit 1
  fi
  echo "[$(date '+%F %T')] launch $name on GPU $gpu -> $log"
  (
    cd "$ROOT/SpatialLM"
    unset CAD_USE_EDGE_SCORE CAD_USE_SEPARATE_EDGE_TOKENS CAD_EDGE_SOURCE \
          CAD_SECOND_STREAM CAD_EDGE_BUDGET_MATCH
    export CAD_SURFACE_POINTS=4096
    export CAD_HELDOUT_PROTOCOL=best_v2
    export CAD_SURFACE_CACHE="$CACHE"
    export CAD_ES_PATIENCE=4
    export CAD_ES_THRESHOLD=0.0
    for kv in "$@"; do
      export "$kv"
    done
    local save_dir="$arm_dir"
    local phases=(train)
    [ -f "$save_dir/dataset_dict.json" ] || phases=(preprocess train)
    for phase in "${phases[@]}"; do
      echo "--- $name $phase $(date '+%F %T') ---"
      CUDA_VISIBLE_DEVICES="$gpu" $LAUNCHER "$cfg"
    done
  ) >>"$log" 2>&1 &
  echo $! >"$RUN/logs/${name}.pid"
  echo "  pid $(cat "$RUN/logs/${name}.pid")"
}

launch B0 "$GPU_B0" "$CFG/heldout_best_v2_b0.yaml" "$RUN/b0"

launch B1n "$GPU_B1N" "$CFG/heldout_best_v2_b1_native.yaml" "$RUN/b1_native" \
  CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE=gt_sharp CAD_SECOND_STREAM=edge_points

launch B1b "$GPU_B1B" "$CFG/heldout_best_v2_b1_budget_match.yaml" "$RUN/b1_budget_match" \
  CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE=gt_sharp \
  CAD_SECOND_STREAM=edge_points CAD_EDGE_BUDGET_MATCH=1

launch M2 "$GPU_M2" "$CFG/heldout_best_v2_m2.yaml" "$RUN/m2" \
  CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_SECOND_STREAM=curve_tokens

echo "best_v2 four arms launched. Logs:"
echo "  tail -f $RUN/logs/B0.log"
echo "Old heldout last-ckpt diagnostic is untouched."
