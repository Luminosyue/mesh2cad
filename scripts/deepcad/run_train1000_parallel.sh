#!/usr/bin/env bash
# Parallel build 1000 QA-passed DeepCAD samples (fast path).
#
# Prerequisites:
#   conda activate cadfit-env
#   python3 scripts/deepcad/download_deepcad_subset.py --num-samples 2500 \
#       --start 0 --manifest cad_spatial_dataset/DeepCAD/manifest_train2500.json
#
# Speed tips:
#   - WORKERS=32~64 on this machine (180 cores)
#   - --no-vis skips PNG generation (~30% faster per sample)
#   - --timeout kills stuck samples (complex Fusion360 meshes)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

WORKERS="${WORKERS:-48}"
TARGET="${TARGET:-1000}"
MANIFEST="${MANIFEST:-cad_spatial_dataset/DeepCAD/manifest_train2500.json}"
PYTHON="${PYTHON:-/data/miniconda3/envs/cadfit-env/bin/python3}"

echo "=== Step 0: ensure manifest + raw JSON (${MANIFEST}) ==="
if [[ ! -f "$MANIFEST" ]]; then
  python3 scripts/deepcad/download_deepcad_subset.py \
    --num-samples 2500 \
    --start 0 \
    --manifest "$MANIFEST"
fi

echo "=== Step 1: stop old single-thread builders (if any) ==="
pkill -f "build_deepcad_dataset.py" 2>/dev/null || true
pkill -f "build_fusion360_dataset.py" 2>/dev/null || true
sleep 2

echo "=== Step 2: parallel build DeepCAD target=${TARGET} workers=${WORKERS} ==="
nohup "$PYTHON" scripts/cad_spatial/parallel_build.py \
  --dataset deepcad \
  --manifest "$MANIFEST" \
  --workers "$WORKERS" \
  --target-passed "$TARGET" \
  --skip-existing \
  --no-vis \
  --timeout 600 \
  > cad_spatial_dataset/DeepCAD/build_parallel.log 2>&1 &

echo "PID=$!  log=cad_spatial_dataset/DeepCAD/build_parallel.log"
echo "Monitor: tail -f cad_spatial_dataset/DeepCAD/build_parallel.log"
