#!/usr/bin/env bash
# Run C0–C3 under identical budget. Primary metric: LINE→CIRCLE FP.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GPU="${1:-0}"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
LOG_DIR="$ROOT/ours3/curve_encoder_scale_curvature_v1/runs"
mkdir -p "$LOG_DIR"
cd "$ROOT"

for EXP in C0 C1 C2 C3; do
  echo "=== START $EXP $(date '+%F %T') ==="
  CUDA_VISIBLE_DEVICES="$GPU" PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    "$PYTHON" scripts/curve_encoder_scale_curvature_v1/train.py --exp "$EXP" \
    2>&1 | tee "$LOG_DIR/${EXP}_frozen_v1.log"
  echo "=== DONE $EXP $(date '+%F %T') ==="
done

"$PYTHON" - <<'PY'
import json
from pathlib import Path
root = Path("ours3/curve_encoder_scale_curvature_v1/runs")
rows = []
for exp in ["C0","C1","C2","C3"]:
    p = root / f"{exp}_frozen_v1" / "scorecard.json"
    if p.is_file():
        rows.append(json.loads(p.read_text()))
# markdown table
headers = [
    "Exp","LINE→CIRCLE","rate","top90% FP","top90 rate","CIRCLE rec",
    "Macro F1","Bal Acc","LINE F1","CIRCLE F1","ELLIPSE F1","BSPLINE F1","Chamfer",
]
lines = [
    "# CURVE_ENCODER_SCALE_CURVATURE_V1 — test scorecard\n",
    "Primary: LINE→CIRCLE FP / top-decile FP. Guardrail: CIRCLE recall ≥ ~85%.\n",
    "P2 reference: L→C=1248 (7.3%), top90 FP=46%, CIRCLE rec=90.5%, MacroF1=0.487\n",
    "",
    "| " + " | ".join(headers) + " |",
    "| " + " | ".join(["---"] + ["---:"]*(len(headers)-1)) + " |",
]
for r in rows:
    t = r["test"]
    lines.append(
        f"| {r['exp']} | {t['line_to_circle_fp']} | {t['line_to_circle_rate']:.1%} | "
        f"{t['top_decile_line_to_circle_fp']} | {t['top_decile_line_to_circle_fp_rate']:.1%} | "
        f"{t['circle_recall']:.3f} | {t['macro_f1']:.3f} | {t['balanced_accuracy']:.3f} | "
        f"{t['LINE_f1']:.3f} | {t['CIRCLE_f1']:.3f} | {t['ELLIPSE_f1']:.3f} | "
        f"{t['BSPLINE_f1']:.3f} | {t['recon_chamfer_mean']:.3f} |"
    )
text = "\n".join(lines) + "\n"
(root / "TABLE_C0C3_TEST.md").write_text(text)
(root / "summary_all.json").write_text(json.dumps(rows, indent=2) + "\n")
print(text)
PY
