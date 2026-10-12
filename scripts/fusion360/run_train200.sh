#!/usr/bin/env bash
# Build Fusion360 Reconstruction train200 with QA gate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

MANIFEST="${MANIFEST:-cad_spatial_dataset/Fusion360/manifest_train200.json}"
CANDIDATES="${CANDIDATES:-400}"

echo "=== Fusion360 manifest (200 ids, scan ${CANDIDATES} candidates) ==="
python3 scripts/fusion360/create_fusion360_manifest.py \
  --num-samples "$CANDIDATES" \
  --manifest "$MANIFEST"

echo "=== Fusion360 batch build (target 200 QA-passed) ==="
conda run -n cadfit-env python3 scripts/fusion360/build_fusion360_dataset.py \
  --manifest "$MANIFEST" \
  --target-passed 200 \
  --skip-existing

echo "=== Done ==="
python3 - <<'PY'
import json
from pathlib import Path
summary = json.loads(Path("cad_spatial_dataset/Fusion360/build_summary.json").read_text())
print(json.dumps(summary, indent=2))
PY
