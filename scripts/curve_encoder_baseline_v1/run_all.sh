#!/usr/bin/env bash
# Run P0–T2 under identical training budget.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GPU="${1:-0}"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
LOG_DIR="$ROOT/ours3/curve_encoder_baseline_v1/runs"
mkdir -p "$LOG_DIR"

cd "$ROOT"
"$PYTHON" scripts/curve_encoder_baseline_v1/make_frozen_split_v1.py

for EXP in P0 P1 P2 T0 T1 T2; do
  echo "=== START $EXP $(date '+%F %T') ==="
  CUDA_VISIBLE_DEVICES="$GPU" PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    "$PYTHON" scripts/curve_encoder_baseline_v1/train.py --exp "$EXP" \
    2>&1 | tee "$LOG_DIR/${EXP}_frozen_v1.log"
  echo "=== DONE $EXP $(date '+%F %T') ==="
done

"$PYTHON" - <<'PY'
import json
from pathlib import Path
root = Path("ours3/curve_encoder_baseline_v1/runs")
rows = []
for exp in ["P0","P1","P2","T0","T1","T2"]:
    p = root / f"{exp}_frozen_v1" / "scorecard.json"
    if p.is_file():
        rows.append(json.loads(p.read_text()))
out = root / "summary_all.json"
out.write_text(json.dumps(rows, indent=2) + "\n")
print(f"wrote {out} n={len(rows)}")
for r in rows:
    t = r["test"]
    print(f"{r['exp']}: macroF1={t['macro_f1']:.4f} balAcc={t['balanced_accuracy']:.4f} "
          f"chamfer={t['recon_chamfer_mean']:.5f}")
PY
