#!/usr/bin/env bash
# Held-out four-arm training (seed=0): B0 / B1-native / B1-budget-match / M2
#
# Prerequisites: full curve_tokens export under ours3/spatiallm_curve_token_v1/curve_tokens/
# Usage:
#   bash scripts/spatiallm_curve_token_v1/run_heldout.sh 0 5 7 3
#   # args = GPU for B0 B1n B1b M2
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PYTHON_BIN:-/data/miniconda3/envs/spatiallm/bin/python}"
CFG="$ROOT/scripts/spatiallm_curve_token_v1/configs"
LOG="$ROOT/ours3/spatiallm_curve_token_v1/runs/heldout"
LAUNCHER="$PY $ROOT/scripts/spatiallm_curve_token_v1/train_heldout_arm.py"
mkdir -p "$LOG" \
  "$ROOT/SpatialLM/saves/heldout_curve_b0_s0" \
  "$ROOT/SpatialLM/saves/heldout_curve_b1_native_s0" \
  "$ROOT/SpatialLM/saves/heldout_curve_b1_budget_s0" \
  "$ROOT/SpatialLM/saves/heldout_curve_m2_s0"

GPU_B0="${1:-0}"
GPU_B1N="${2:-5}"
GPU_B1B="${3:-7}"
GPU_M2="${4:-3}"

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export CAD_SURFACE_POINTS=4096

launch() {
  local name="$1" gpu="$2" cfg="$3"
  shift 3
  local log="$LOG/${name}_s0.log"
  echo "[$(date '+%F %T')] launch $name on GPU $gpu -> $log"
  (
    cd "$ROOT/SpatialLM"
    unset CAD_USE_EDGE_SCORE CAD_USE_SEPARATE_EDGE_TOKENS CAD_EDGE_SOURCE \
          CAD_SECOND_STREAM CAD_EDGE_BUDGET_MATCH
    export CAD_SURFACE_POINTS=4096
    # arm-specific env
    for kv in "$@"; do
      export "$kv"
    done
    # preprocess+train: SpatialLM exits after first preprocess pass
    local save_dir
    save_dir="$ROOT/SpatialLM/$(sed -n 's/^save_dir: *//p' "$cfg" | head -1)"
    local phases=(train)
    [ -f "$save_dir/dataset_dict.json" ] || phases=(preprocess train)
    for phase in "${phases[@]}"; do
      echo "--- $name $phase $(date '+%F %T') ---"
      CUDA_VISIBLE_DEVICES="$gpu" $LAUNCHER "$cfg"
    done
  ) >>"$log" 2>&1 &
  echo $! >"$LOG/${name}_s0.pid"
  echo "  pid $(cat "$LOG/${name}_s0.pid")"
}

launch B0 "$GPU_B0" "$CFG/heldout_b0_s0.yaml"

launch B1n "$GPU_B1N" "$CFG/heldout_b1_native_s0.yaml" \
  CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE=gt_sharp CAD_SECOND_STREAM=edge_points

launch B1b "$GPU_B1B" "$CFG/heldout_b1_budget_s0.yaml" \
  CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE=gt_sharp \
  CAD_SECOND_STREAM=edge_points CAD_EDGE_BUDGET_MATCH=1

launch M2 "$GPU_M2" "$CFG/heldout_m2_s0.yaml" \
  CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_SECOND_STREAM=curve_tokens

echo "All four arms launched. Logs under $LOG"
echo "Tail: tail -f $LOG/B0_s0.log"
