#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
OUT=$ROOT/ours3/toaster_p1_edge_condition_ablation_v1
PY=/data/miniconda3/envs/spatiallm/bin/python
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-5}"
cd "$ROOT"
mkdir -p "$OUT/manifest" "$OUT/reports" "$OUT/eval" "$OUT/gallery" "$OUT/predictions"

echo "[guard] recording historical hashes (read-only)"
$PY - <<'PY'
from pathlib import Path
import hashlib, json
root = Path("/data/home/cuiyuehan/project/mesh2cad")
out = root/"ours3/toaster_p1_edge_condition_ablation_v1/manifest/historical_readonly_guard.json"
paths = [
  root/"ours3/toaster_p1_xpart_v1/reports/FINAL_REPORT.md",
  root/"ours3/toaster_p1_vs_cadfit_eval_v1/reports/FINAL_REPORT.md",
  root/"ours3/toaster_p3_xpart_cadfit_routea_v1/assembly/assembly_manifest.json",
  root/"ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000/config.json",
  root/"ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-39980/config.json",
]
h={}
for p in paths:
    h[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
out.write_text(json.dumps({"read_only_hashes": h}, indent=2)+"\n")
print("guard ok", len(h))
PY

echo "[prepare] mesh dihedral -> C2 tokens"
$PY -u "$OUT/scripts/prepare_mesh_curves.py"

for ARM in A B C D; do
  echo "[decode] arm $ARM"
  $PY -u "$OUT/scripts/decode_arm.py" --arm "$ARM"
done

echo "[eval]"
$PY -u "$OUT/scripts/evaluate.py"
echo DONE
