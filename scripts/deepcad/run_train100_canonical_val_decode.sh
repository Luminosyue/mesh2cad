#!/usr/bin/env bash
# Decode canonical train100 val for baseline + ours, comparison + vis.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON=/data/miniconda3/envs/spatiallm/bin/python
CADPY=/data/miniconda3/envs/cadfit-env/bin/python
LOG="$ROOT/cad_spatial_dataset/DeepCAD/train100_canonical_val_decode.log"
MIN_FREE="${MIN_FREE:-20000}"
OUT_ROOT="$ROOT/ours3/deepcad_train100_canonical_val_decode"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

wait_gpu() {
  while true; do
    read -r FREE GPU <<<"$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
      | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1)"
    FREE=${FREE:-0}
    if (( FREE >= MIN_FREE )); then
      echo "$GPU"
      return
    fi
    echo "[$(date '+%F %T')] wait GPU free=${FREE}MB need>=${MIN_FREE}" >> "$LOG"
    sleep 5
  done
}

cd "$ROOT"
export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$OUT_ROOT"
: > "$LOG"

run_one() {
  local variant="$1"
  local ckpt="$2"
  local split="$3"
  local out="$OUT_ROOT/$variant"
  if [[ "$variant" == "ours" ]]; then
    export CAD_USE_EDGE_SCORE=1
  else
    unset CAD_USE_EDGE_SCORE
  fi
  GPU=$(wait_gpu)
  log "DECODE $variant on GPU=$GPU ckpt=$ckpt"
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" scripts/deepcad/decode_eval_split.py \
    --checkpoint "$ckpt" \
    --split-json "$split" \
    --variant "$variant" \
    --out "$out" \
    2>&1 | tee -a "$LOG"
}

BASE_CKPT="$ROOT/SpatialLM/saves/deepcad_train100_canonical_baseline"
OURS_CKPT="$ROOT/SpatialLM/saves/deepcad_train100_canonical_ours"
[[ -f "$BASE_CKPT/model.safetensors.index.json" ]] || BASE_CKPT="$BASE_CKPT/checkpoint-1000"
[[ -f "$OURS_CKPT/model.safetensors.index.json" ]] || OURS_CKPT="$OURS_CKPT/checkpoint-1000"

run_one baseline "$BASE_CKPT" \
  "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_train100_val.json"
run_one ours "$OURS_CKPT" \
  "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_ours_train100_val.json"

"$CADPY" - <<'PY' | tee -a "$LOG"
import json
from pathlib import Path
ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
out = ROOT / "ours3/deepcad_train100_canonical_val_decode"
base = json.loads((out / "baseline/report.json").read_text())
ours = json.loads((out / "ours/report.json").read_text())

def row(r):
    keys = [
        "exact_match_n", "exact_match_rate", "mean_op_recall", "mean_op_f1",
        "dsl_parse_valid_rate", "step_valid_rate",
        "mean_chamfer_norm", "mean_hausdorff_95_norm", "mean_volume_error", "n_samples",
    ]
    return {k: r.get(k) for k in keys}

cmp = {"baseline": row(base), "ours": row(ours), "per_sample": []}
bmap = {s["sample_id"]: s for s in base["samples"]}
omap = {s["sample_id"]: s for s in ours["samples"]}
for sid in sorted(set(bmap) | set(omap)):
    b, o = bmap.get(sid, {}), omap.get(sid, {})
    bg, og = b.get("geometry") or {}, o.get("geometry") or {}
    cmp["per_sample"].append({
        "sample_id": sid,
        "baseline": {
            "exact": b.get("exact_match"), "op_recall": b.get("op_recall"), "op_f1": b.get("op_f1"),
            "parsed": b.get("parsed"), "step_ok": b.get("step_ok"),
            "chamfer": bg.get("chamfer_norm"), "hausdorff95": bg.get("hausdorff_95_norm"),
            "vol_err": bg.get("volume_error"),
        },
        "ours": {
            "exact": o.get("exact_match"), "op_recall": o.get("op_recall"), "op_f1": o.get("op_f1"),
            "parsed": o.get("parsed"), "step_ok": o.get("step_ok"),
            "chamfer": og.get("chamfer_norm"), "hausdorff95": og.get("hausdorff_95_norm"),
            "vol_err": og.get("volume_error"),
        },
    })
(out / "comparison.json").write_text(json.dumps(cmp, indent=2) + "\n")
lines = ["# Canonical Train100 Val Decode (n=19)", "", "## Summary", "",
         "| Metric | Baseline | Ours |", "|---|---:|---:|"]
for k in cmp["baseline"]:
    bv, ov = cmp["baseline"][k], cmp["ours"][k]
    def fmt(x):
        if x is None: return "—"
        if isinstance(x, float): return f"{x:.4f}"
        return str(x)
    lines.append(f"| {k} | {fmt(bv)} | {fmt(ov)} |")
(out / "comparison.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
PY

log "VIS"
DECODE="$OUT_ROOT" "$CADPY" scripts/deepcad/vis_train100_val.py \
  --decode-root "$OUT_ROOT" \
  --out "$OUT_ROOT/vis" 2>&1 | tee -a "$LOG" || \
"$CADPY" - <<'PY'
# fallback: monkey-patch paths via env if script lacks args
import os, runpy
os.environ["DECODE_ROOT"] = "/data/home/cuiyuehan/project/mesh2cad/ours3/deepcad_train100_canonical_val_decode"
print("run vis manually if needed")
PY

log "ALL CANONICAL VAL DECODE DONE"
