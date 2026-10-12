#!/usr/bin/env bash
set -euo pipefail
cd /data/home/cuiyuehan/project/mesh2cad
base=ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2
split=ours3/exact9998_v1/exact9998_val.json
media=cad_spatial_dataset
entry="$base/launch/unified_v2_entrypoint.py"
nohup env CUDA_VISIBLE_DEVICES=1 /data/miniconda3/envs/spatiallm/bin/python -u "$entry" \
 --checkpoint ours3/m2_exact9998_b0_m2_train_v1/runs/b0/checkpoint-6000 \
 --split-json "$split" --variant j0 --media-dir "$media" --out "$base/predictions/a0" \
 --dtype bfloat16 --max-new-tokens 4096 > "$base/runtime/a0.log" 2>&1 < /dev/null &
echo $! > "$base/runtime/a0.pid"
nohup env CUDA_VISIBLE_DEVICES=5 /data/miniconda3/envs/spatiallm/bin/python -u "$entry" \
 --checkpoint ours3/m2_exact9998_corrected_m2_train_v1/runs/m2/checkpoint-6000 \
 --split-json "$split" --variant j2 --edge-source gt_sharp --media-dir "$media" --out "$base/predictions/a3" \
 --dtype bfloat16 --max-new-tokens 4096 > "$base/runtime/a3.log" 2>&1 < /dev/null &
echo $! > "$base/runtime/a3.pid"
echo "A0_PID=$(cat "$base/runtime/a0.pid")"
echo "A3_PID=$(cat "$base/runtime/a3.pid")"
