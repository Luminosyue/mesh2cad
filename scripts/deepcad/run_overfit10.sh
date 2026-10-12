#!/usr/bin/env bash
# Step 5: 10-sample overfit pipeline verification
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Step 2 check: ensure DeepCAD samples exist ==="
COMPLETE=$(find cad_spatial_dataset/DeepCAD/train -name features.npy 2>/dev/null | wc -l)
echo "Complete samples: $COMPLETE"
if [ "$COMPLETE" -lt 10 ]; then
  echo "Building remaining samples (need >=10)..."
  python3 scripts/deepcad/build_deepcad_dataset.py \
    --manifest cad_spatial_dataset/DeepCAD/manifest_train100.json \
    --skip-existing
fi

echo "=== Step 3: audit (quick, no consistency) ==="
python3 scripts/deepcad/audit_deepcad_dataset.py \
  --no-consistency \
  --out cad_spatial_dataset/DeepCAD/audit_quick.json || true

echo "=== Step 4: create overfit10 ShareGPT datasets ==="
python3 scripts/deepcad/create_spatiallm_cad_dataset.py \
  --limit 10 --name-suffix overfit10 --variant ours
python3 scripts/deepcad/create_spatiallm_cad_dataset.py \
  --limit 10 --name-suffix overfit10 --variant baseline

PYTHON="python3.10"
export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
GPU="${CUDA_VISIBLE_DEVICES:-4}"

echo "=== Step 5a: overfit OURS (xyz+normal+edge) via lite trainer ==="
CUDA_VISIBLE_DEVICES=$GPU "$PYTHON" scripts/deepcad/overfit10_lite.py \
  --variant ours --epochs 200 --log-every 5 --save-every 25

echo "=== Step 5b: overfit BASELINE (xyz+normal) ==="
CUDA_VISIBLE_DEVICES=$GPU "$PYTHON" scripts/deepcad/overfit10_lite.py \
  --variant baseline --epochs 200 --log-every 5 --save-every 25

echo "Done. Check loss → 0 and decode Extrude/Cut on training samples."
echo "Decode example:"
echo "  CUDA_VISIBLE_DEVICES=\$GPU $PYTHON scripts/deepcad/decode_overfit10.py \\"
echo "    --checkpoint ours3/deepcad_overfit10_lite/ours/epoch_XXX --variant ours --use-edge"
