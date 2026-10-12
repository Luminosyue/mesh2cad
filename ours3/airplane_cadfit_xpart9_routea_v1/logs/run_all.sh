#!/bin/bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
OUT=$ROOT/ours3/airplane_cadfit_xpart9_routea_v1
LOG=$OUT/logs/parallel_run.log
cd "$ROOT"
{
  echo "START $(date -Is)"
  python3 scripts/run_cadfit_routea_parallel.py \
    --output-dir "$OUT" \
    --jobs 3 \
    --inner-workers 8
  echo "CADFIT_DONE $(date -Is)"
  python3 scripts/cadfit_routea_export_step.py --output-dir "$OUT"
  echo "STEP_DONE $(date -Is)"
} >> "$LOG" 2>&1
