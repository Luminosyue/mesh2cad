#!/usr/bin/env bash
set -u
cd /data/home/cuiyuehan/project/mesh2cad || exit 1
base=ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2
mkdir -p "$base/interim" "$base/runtime"
for milestone in 100 250 500 750; do
  while true; do
    a0=$(find "$base/predictions/a0" -name row.json | wc -l)
    a3=$(find "$base/predictions/a3" -name row.json | wc -l)
    echo "$(date -Is) A0=$a0 A3=$a3 target=$milestone"
    if [ "$a0" -ge "$milestone" ] && [ "$a3" -ge "$milestone" ]; then
      /data/miniconda3/envs/spatiallm/bin/python "$base/launch/interim_snapshot_v2.py" --n "$milestone"
      break
    fi
    if ! kill -0 "$(cat "$base/runtime/a0.pid")" 2>/dev/null || ! kill -0 "$(cat "$base/runtime/a3.pid")" 2>/dev/null; then
      echo "decoder exited before milestone $milestone"; exit 2
    fi
    sleep 30
  done
done
while true; do
  a0=$(find "$base/predictions/a0" -name row.json | wc -l)
  a3=$(find "$base/predictions/a3" -name row.json | wc -l)
  echo "$(date -Is) A0=$a0 A3=$a3 target=1000"
  if [ "$a0" -ge 1000 ] && [ "$a3" -ge 1000 ]; then
    touch "$base/runtime/READY_FOR_FINAL_AGGREGATE"
    exit 0
  fi
  sleep 30
done
