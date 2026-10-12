#!/usr/bin/env bash
# Parallel build 200 QA-passed Fusion360 samples.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

WORKERS="${WORKERS:-24}"
TARGET="${TARGET:-200}"
MANIFEST="${MANIFEST:-cad_spatial_dataset/Fusion360/manifest_train8625.json}"
PYTHON="${PYTHON:-/data/miniconda3/envs/cadfit-env/bin/python3}"

echo "=== Step 0: create full train+test manifest ==="
if [[ ! -f "$MANIFEST" ]]; then
  python3 - <<'PY'
import json
from pathlib import Path
ROOT = Path("cad_spatial_dataset/Fusion360")
split = json.loads((ROOT / "reconstruction/train_test.json").read_text())
recon = ROOT / "reconstruction/reconstruction"
ids = []
for part in ("train", "test"):
    for sid in split[part]:
        if (recon / f"{sid}.json").exists() and (recon / f"{sid}.step").exists() and (recon / f"{sid}.obj").exists():
            ids.append(sid)
manifest = {
    "split": "train+test",
    "requested": len(ids),
    "selected": len(ids),
    "sample_ids": ids,
    "recon_dir": str(recon),
}
out = ROOT / "manifest_train8625.json"
out.write_text(json.dumps(manifest, indent=2) + "\n")
print(f"manifest: {out}  ids={len(ids)}")
PY
fi

echo "=== Step 1: stop old single-thread Fusion360 builder ==="
pkill -f "build_fusion360_dataset.py" 2>/dev/null || true
sleep 2

echo "=== Step 2: parallel build Fusion360 target=${TARGET} workers=${WORKERS} ==="
nohup "$PYTHON" scripts/cad_spatial/parallel_build.py \
  --dataset fusion360 \
  --manifest "$MANIFEST" \
  --workers "$WORKERS" \
  --target-passed "$TARGET" \
  --skip-existing \
  --no-vis \
  --timeout 300 \
  > cad_spatial_dataset/Fusion360/build_parallel.log 2>&1 &

echo "PID=$!  log=cad_spatial_dataset/Fusion360/build_parallel.log"
