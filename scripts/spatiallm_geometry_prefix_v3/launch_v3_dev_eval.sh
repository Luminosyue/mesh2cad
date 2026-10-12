#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
RUNROOT="$ROOT/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/runs_single_multieval_v1"
OUTROOT="$ROOT/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/dev_eval_sharded_v1"
SCRIPT="$ROOT/scripts/spatiallm_geometry_prefix_v3/evaluate_v3_checkpoint.py"
mkdir -p "$OUTROOT"
rm -f "$OUTROOT/jobs.txt"
for spec in 'b0 b0' 'b1 b1_v3' 'm2 m2_v3'; do
  set -- $spec; arm=$1; run=$2
  for ep in $(seq -w 1 10); do
    printf '%s %s %s\n' "$arm" "$RUNROOT/$run/checkpoint_epoch_$ep" "$OUTROOT/$run/epoch_$ep" >> "$OUTROOT/jobs.txt"
  done
done
worker() {
  local gpu=$1 worker_id=$2
  local n=0
  while read -r arm ckpt out; do
    if [ $((n % 7)) -eq "$worker_id" ]; then
      if [ ! -f "$out/SUMMARY.json" ]; then
        echo "START gpu=$gpu arm=$arm ckpt=$ckpt"
        CUDA_VISIBLE_DEVICES="$gpu" python3 "$SCRIPT" --arm "$arm" --checkpoint "$ckpt" --split v3_decode_dev_50.json --output "$out" --device cuda:0 --target-norm 1.9414176940917969 --max-new-tokens 4096
        echo "DONE gpu=$gpu arm=$arm ckpt=$ckpt"
      fi
    fi
    n=$((n+1))
  done < "$OUTROOT/jobs.txt"
}
for item in '0 0' '1 1' '2 2' '3 3' '4 4' '6 5' '7 6'; do
  set -- $item; worker "$1" "$2" &
done
wait
echo ALL_DEV_EVAL_DONE
