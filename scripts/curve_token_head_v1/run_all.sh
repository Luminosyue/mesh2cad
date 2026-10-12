#!/usr/bin/env bash
# Step-4 key experiment: D0 (type only) vs D1 (type + recon + param) on frozen C2.
set -euo pipefail
GPU="${1:-0}"
cd "$(dirname "$0")/../.."
OUT="ours3/curve_token_head_v1/runs"
mkdir -p "$OUT"
for exp in D0 D1; do
  echo "=== $exp on GPU $GPU ==="
  CUDA_VISIBLE_DEVICES="$GPU" python3 scripts/curve_token_head_v1/train.py \
    --exp "$exp" 2>&1 | tee "$OUT/${exp}_train.log"
done
python3 scripts/curve_token_head_v1/make_table.py
