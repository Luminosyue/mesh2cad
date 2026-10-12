#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
F=$ROOT/ours3/final_test1000_v1
P=$F/freeze/EXACT9998_TEST_DECODER_INPUT.json
E=$F/freeze/final_test_runner.py
PY=/data/miniconda3/envs/spatiallm/bin/python
PYTHONPATH_VALUE=$ROOT:$ROOT/scripts:$ROOT/SpatialLM
mkdir -p "$F/a3/predictions" "$F/p1/predictions" "$F/runtime"
while true; do
  ready=1
  for arm in a0 a1 a2; do
    report="$F/$arm/predictions/report.json"
    if [ ! -f "$report" ]; then ready=0; continue; fi
    n=$("$PY" -c "import json; print(json.load(open('$report')).get('n_samples',0))")
    if [ "$n" != "1000" ]; then ready=0; fi
  done
  if [ "$ready" = "1" ]; then
    if [ ! -f "$F/runtime/a3.pid" ]; then
      nohup env FINAL_ARM=a3 PYTHONPATH="$PYTHONPATH_VALUE" CUDA_VISIBLE_DEVICES=0 "$PY" -u "$E" --checkpoint ours3/m2_exact9998_corrected_m2_train_v1/runs/m2/checkpoint-6000 --split-json "$P" --variant j2 --edge-source gt_sharp --media-dir cad_spatial_dataset --out "$F/a3/predictions" --dtype bfloat16 --max-new-tokens 4096 --resume > "$F/runtime/a3.log" 2>&1 < /dev/null &
      echo $! > "$F/runtime/a3.pid"
    fi
    if [ ! -f "$F/runtime/p1.pid" ]; then
      nohup env FINAL_ARM=p1 PYTHONPATH="$PYTHONPATH_VALUE" CUDA_VISIBLE_DEVICES=4 "$PY" -u "$E" --checkpoint ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000 --split-json "$P" --variant j2 --edge-source gt_sharp --media-dir cad_spatial_dataset --out "$F/p1/predictions" --dtype bfloat16 --max-new-tokens 4096 --resume > "$F/runtime/p1.log" 2>&1 < /dev/null &
      echo $! > "$F/runtime/p1.pid"
    fi
    "$PY" - <<PY
import json,time
from pathlib import Path
p=Path('$F/runtime/FINAL_TEST_LAUNCH.json')
d=json.loads(p.read_text())
d['arms']['A0']['status']='COMPLETE'; d['arms']['A1']['status']='COMPLETE'; d['arms']['A2']['status']='COMPLETE'
d['arms']['A3']={'status':'RUNNING','gpu':'0','pid':Path('$F/runtime/a3.pid').read_text().strip()}
d['arms']['P1']={'status':'RUNNING','gpu':'4','pid':Path('$F/runtime/p1.pid').read_text().strip()}
d['a0_a1_a2_complete_time_local']=time.strftime('%Y-%m-%d %H:%M:%S %z')
p.write_text(json.dumps(d,indent=2)+'\n')
PY
    exit 0
  fi
  sleep 120
done
