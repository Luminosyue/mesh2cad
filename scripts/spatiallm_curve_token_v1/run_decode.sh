#!/usr/bin/env bash
# Decode B0 / B1 / M2 on the same 100-CAD overfit set.
# Usage: run_decode.sh <gpu_b0> <gpu_b1> <gpu_m2>   e.g. run_decode.sh 0 1 6
# Main budget: MAX_NEW_TOKENS=4096 (override via env). 2048 archive: decode_max2048/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PYTHON_BIN:-/data/miniconda3/envs/spatiallm/bin/python}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
LOG="$ROOT/ours3/spatiallm_curve_token_v1/runs"
OUT="$ROOT/ours3/spatiallm_curve_token_v1/decode"
mkdir -p "$LOG" "$OUT"

GPU_B0="${1:-0}"
GPU_B1="${2:-1}"
GPU_M2="${3:-6}"
LIMIT="${LIMIT:-}"
RESUME="${RESUME:---resume}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-4096}"

extra=(--max-new-tokens "$MAX_NEW_TOKENS")
[ -n "$LIMIT" ] && extra+=(--limit "$LIMIT")

launch() {
  local arm="$1" gpu="$2"
  echo "=== decode $arm on GPU $gpu (max_new_tokens=$MAX_NEW_TOKENS) ==="
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" \
    "$ROOT/scripts/spatiallm_curve_token_v1/decode_curve100.py" \
    --arm "$arm" $RESUME "${extra[@]}" \
    >"$LOG/decode_${arm}_m${MAX_NEW_TOKENS}.log" 2>&1 &
  echo "  pid $! log $LOG/decode_${arm}_m${MAX_NEW_TOKENS}.log"
}

cd "$ROOT"
launch B0 "$GPU_B0"
launch B1 "$GPU_B1"
launch M2 "$GPU_M2"
wait
"$PY" "$ROOT/scripts/spatiallm_curve_token_v1/make_decode_table.py"
echo "=== all decode done ==="
