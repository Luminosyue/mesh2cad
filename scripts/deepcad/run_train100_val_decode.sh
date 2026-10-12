#!/usr/bin/env bash
# Decode train100 val for baseline + ours, then write comparison JSON/MD.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON=/data/miniconda3/envs/spatiallm/bin/python
LOG="$ROOT/cad_spatial_dataset/DeepCAD/train100_val_decode.log"
MIN_FREE="${MIN_FREE:-28000}"

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
    log "wait GPU free=${FREE}MB need>=${MIN_FREE}"
    sleep 5
  done
}

cd "$ROOT"
export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

OUT_ROOT="$ROOT/ours3/deepcad_train100_val_decode"
mkdir -p "$OUT_ROOT"

run_one() {
  local variant="$1"
  local ckpt="$2"
  local split="$3"
  local out="$OUT_ROOT/$variant"
  local edge_flag=""
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

# Prefer final weights dir; fall back to checkpoint-1000
BASE_CKPT="$ROOT/SpatialLM/saves/deepcad_train100_baseline"
OURS_CKPT="$ROOT/SpatialLM/saves/deepcad_train100_ours"
[[ -f "$BASE_CKPT/model.safetensors.index.json" ]] || BASE_CKPT="$BASE_CKPT/checkpoint-1000"
[[ -f "$OURS_CKPT/model.safetensors.index.json" ]] || OURS_CKPT="$OURS_CKPT/checkpoint-1000"

run_one baseline "$BASE_CKPT" \
  "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_train100_val.json"
run_one ours "$OURS_CKPT" \
  "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_ours_train100_val.json"

# Build comparison table
"$PYTHON" - <<'PY' | tee -a "$LOG"
import json
from pathlib import Path
ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
out = ROOT / "ours3/deepcad_train100_val_decode"
base = json.loads((out / "baseline/report.json").read_text())
ours = json.loads((out / "ours/report.json").read_text())

def row(r):
    return {
        "exact_match_n": r.get("exact_match_n"),
        "exact_match_rate": r.get("exact_match_rate"),
        "mean_op_recall": r.get("mean_op_recall"),
        "step_valid_rate": r.get("step_valid_rate"),
        "mean_chamfer_norm": r.get("mean_chamfer_norm"),
        "mean_hausdorff_95_norm": r.get("mean_hausdorff_95_norm"),
        "mean_volume_error": r.get("mean_volume_error"),
        "n_samples": r.get("n_samples"),
    }

cmp = {"baseline": row(base), "ours": row(ours), "per_sample": []}
bmap = {s["sample_id"]: s for s in base["samples"]}
omap = {s["sample_id"]: s for s in ours["samples"]}
for sid in sorted(set(bmap) | set(omap)):
    b, o = bmap.get(sid, {}), omap.get(sid, {})
    bg, og = b.get("geometry") or {}, o.get("geometry") or {}
    cmp["per_sample"].append({
        "sample_id": sid,
        "baseline": {
            "exact": b.get("exact_match"),
            "op_recall": b.get("op_recall"),
            "step_ok": b.get("step_ok"),
            "chamfer": bg.get("chamfer_norm"),
            "hausdorff95": bg.get("hausdorff_95_norm"),
            "vol_err": bg.get("volume_error"),
            "gt_ops": b.get("gt_ops"),
            "pred_ops": b.get("pred_ops"),
        },
        "ours": {
            "exact": o.get("exact_match"),
            "op_recall": o.get("op_recall"),
            "step_ok": o.get("step_ok"),
            "chamfer": og.get("chamfer_norm"),
            "hausdorff95": og.get("hausdorff_95_norm"),
            "vol_err": og.get("volume_error"),
            "gt_ops": o.get("gt_ops"),
            "pred_ops": o.get("pred_ops"),
        },
    })

(out / "comparison.json").write_text(json.dumps(cmp, indent=2) + "\n")

# Markdown table
lines = [
    "# Train100 Val Decode Comparison (n=19)",
    "",
    "## Summary",
    "",
    "| Metric | Baseline | Ours |",
    "|---|---:|---:|",
]
for k in ["exact_match_n", "exact_match_rate", "mean_op_recall", "step_valid_rate",
          "mean_chamfer_norm", "mean_hausdorff_95_norm", "mean_volume_error"]:
    bv, ov = cmp["baseline"].get(k), cmp["ours"].get(k)
    def fmt(x):
        if x is None: return "—"
        if isinstance(x, float): return f"{x:.4f}"
        return str(x)
    lines.append(f"| {k} | {fmt(bv)} | {fmt(ov)} |")

lines += ["", "## Per-sample", "",
          "| sample | B exact | O exact | B step | O step | B op | O op | B chamfer | O chamfer | B Haus95 | O Haus95 |",
          "|---|:-:|:-:|:-:|:-:|---:|---:|---:|---:|---:|---:|"]
for p in cmp["per_sample"]:
    b, o = p["baseline"], p["ours"]
    def f(x, nd=3):
        if x is None: return "—"
        if isinstance(x, float): return f"{x:.{nd}f}"
        if isinstance(x, bool): return "Y" if x else "N"
        return str(x)
    lines.append(
        f"| `{p['sample_id']}` | {f(b['exact'])} | {f(o['exact'])} | {f(b['step_ok'])} | {f(o['step_ok'])} | "
        f"{f(b['op_recall'])} | {f(o['op_recall'])} | {f(b['chamfer'],4)} | {f(o['chamfer'],4)} | "
        f"{f(b['hausdorff95'],4)} | {f(o['hausdorff95'],4)} |"
    )
md = "\n".join(lines) + "\n"
(out / "comparison.md").write_text(md)
print(md)
print(f"Wrote {out/'comparison.json'} and {out/'comparison.md'}")
PY

log "ALL DECODE DONE"
