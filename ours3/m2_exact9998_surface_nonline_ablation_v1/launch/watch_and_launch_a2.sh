#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
A2=$ROOT/ours3/m2_exact9998_surface_nonline_ablation_v1
while true; do
  if [ -f "$A2/launch/train.pid" ] && kill -0 "$(cat "$A2/launch/train.pid")" 2>/dev/null; then exit 0; fi
  while IFS=, read -r gpu mem util; do
    gpu=${gpu// /}; mem=${mem%% *}; mem=${mem// /}; util=${util%%%}; util=${util// /}
    if [ "$gpu" = 5 ]; then
      A3_PID_FILE=$ROOT/ours3/m2_exact9998_corrected_m2_train_v1/launch/train.pid
      A3_RESULTS=$ROOT/ours3/m2_exact9998_corrected_m2_train_v1/runs/m2/train_results.json
      if [ -f "$A3_PID_FILE" ] && kill -0 "$(cat "$A3_PID_FILE")" 2>/dev/null; then continue; fi
      [ -f "$A3_RESULTS" ] || continue
    fi
    if [ "$mem" -lt 5000 ] && [ "$util" -lt 10 ]; then
      if [ -z "$(find "$A2/runs/a2" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
        echo "$(date -Is) launching A2 on physical GPU $gpu" >> "$A2/logs/resource_watcher.log"
        bash "$A2/launch/launch_a2.sh" "$gpu"
        exit 0
      fi
    fi
  done < <(nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits)
  sleep 20
done
