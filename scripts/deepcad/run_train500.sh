#!/usr/bin/env bash
# Expand DeepCAD to 500 train samples with QA gate (clean subset for training).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

MANIFEST="${MANIFEST:-cad_spatial_dataset/DeepCAD/manifest_train500.json}"
NUM="${NUM:-500}"
TARGET="${TARGET:-300}"

echo "=== Download DeepCAD train subset (${NUM} json) ==="
python3 scripts/deepcad/download_deepcad_subset.py \
  --num-samples "$NUM" \
  --manifest "$MANIFEST"

echo "=== Batch build DeepCAD (target ${TARGET} QA-passed) ==="
conda run -n cadfit-env python3 scripts/deepcad/build_deepcad_dataset.py \
  --manifest "$MANIFEST" \
  --skip-existing \
  --target-passed "$TARGET"

echo "=== Done ==="
python3 - <<'PY'
import json
from pathlib import Path
summary = json.loads(Path("cad_spatial_dataset/DeepCAD/build_summary.json").read_text())
print(json.dumps(summary, indent=2))
passed = summary.get("passed", 0)
print(f"QA passed: {passed}")
PY
