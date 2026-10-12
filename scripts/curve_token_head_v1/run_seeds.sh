#!/usr/bin/env bash
# Step-4 with seed replicates: the D0/D1 gap is small, so a single seed is not decisive.
set -euo pipefail
GPU="${1:-0}"
SEEDS="${2:-0 1 2}"
cd "$(dirname "$0")/../.."
OUT="ours3/curve_token_head_v1/runs"
mkdir -p "$OUT"
for seed in $SEEDS; do
  for exp in D0 D1; do
    echo "=== $exp seed=$seed on GPU $GPU ==="
    CUDA_VISIBLE_DEVICES="$GPU" python3 scripts/curve_token_head_v1/train.py \
      --exp "$exp" --seed "$seed" \
      --out-dir "$OUT/${exp}_frozen_v1_seed${seed}" 2>&1 \
      | tee "$OUT/${exp}_seed${seed}_train.log"
  done
done
python3 scripts/curve_token_head_v1/aggregate_seeds.py --seeds $SEEDS
