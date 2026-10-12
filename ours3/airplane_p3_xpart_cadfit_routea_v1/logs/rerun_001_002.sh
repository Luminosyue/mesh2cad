#!/bin/bash
set -u
export PYTHONUNBUFFERED=1
export CADFIT_INNER_WORKERS=8
PY=/data/miniconda3/envs/cadfit-env/bin/python
PIPE=/data/home/cuiyuehan/project/mesh2cad/CADFit/run_pipeline.py
IN=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/_isolated_input
OUT=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw
cd /data/home/cuiyuehan/project/mesh2cad/CADFit
for pid in PART_001 PART_002; do
  echo "[$(date -Iseconds)] START $pid no-filter-sketches over-threshold=999"
  "$PY" -u "$PIPE" "$IN/$pid" \
    --output-folder "$OUT" \
    --max-iterations 1 \
    --limit 1 \
    --keep-history \
    --over-threshold 999 \
    --under-threshold 0.01
  rc=$?
  echo "[$(date -Iseconds)] DONE $pid rc=$rc"
  if [ -f "$OUT/$pid/final_iou.json" ]; then
    python3 -c "import json; d=json.load(open('$OUT/$pid/final_iou.json')); print('final_iou', d.get('final_iou'), 'dur', d.get('duration'))"
  fi
done
echo "[$(date -Iseconds)] ALL DONE"
