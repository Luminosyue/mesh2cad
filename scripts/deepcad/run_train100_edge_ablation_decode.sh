#!/usr/bin/env bash
# Decode all 4 Dora ablation variants on canonical train100 val (n=19).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON=/data/miniconda3/envs/spatiallm/bin/python
CADPY=/data/miniconda3/envs/cadfit-env/bin/python
LOG="$ROOT/cad_spatial_dataset/DeepCAD/train100_edge_ablation_val_decode.log"
OUT_ROOT="$ROOT/ours3/deepcad_train100_edge_ablation_val_decode"
MIN_FREE="${MIN_FREE:-20000}"
SPLIT="$ROOT/cad_spatial_dataset/DeepCAD/split_train100_seed42.json"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

wait_gpu() {
  while true; do
    read -r FREE GPU <<<"$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
      | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1)"
    FREE=${FREE:-0}
    if (( FREE >= MIN_FREE )); then echo "$GPU"; return; fi
    echo "[$(date '+%F %T')] wait GPU free=${FREE}MB" >> "$LOG"
    sleep 5
  done
}

resolve_ckpt() {
  local d="$1"
  if [[ -f "$d/model.safetensors.index.json" ]]; then echo "$d"; return; fi
  local latest
  latest=$(ls -d "$d"/checkpoint-* 2>/dev/null | sort -V | tail -1)
  [[ -n "$latest" ]] && echo "$latest" || echo "$d"
}

run_one() {
  local variant="$1"
  local ckpt="$2"
  local split="$3"
  local out="$OUT_ROOT/$variant"
  if [[ "$variant" == "baseline" ]]; then unset CAD_USE_EDGE_SCORE; else export CAD_USE_EDGE_SCORE=1; fi
  GPU=$(wait_gpu)
  log "DECODE $variant GPU=$GPU ckpt=$ckpt"
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" scripts/deepcad/decode_eval_split.py \
    --checkpoint "$ckpt" --split-json "$split" --variant "$variant" --out "$out" \
    2>&1 | tee -a "$LOG"
}

cd "$ROOT"
export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$OUT_ROOT"
: > "$LOG"

if [[ ! -f "$SPLIT" ]]; then
  "$CADPY" - <<PY
import json
from pathlib import Path
root = Path("$ROOT/cad_spatial_dataset/DeepCAD")
tr = json.loads((root / "deepcad_cad_baseline_train100_train.json").read_text())
va = json.loads((root / "deepcad_cad_baseline_train100_val.json").read_text())
split = {"seed": 42, "val_ratio": 0.2, "train_ids": [r["id"] for r in tr], "val_ids": [r["id"] for r in va]}
(root / "split_train100_seed42.json").write_text(json.dumps(split, indent=2) + "\n")
print("wrote split", len(split["train_ids"]), len(split["val_ids"]))
PY
fi

BASE_CKPT=$(resolve_ckpt "$ROOT/SpatialLM/saves/deepcad_train100_canonical_baseline")
ZERO_CKPT=$(resolve_ckpt "$ROOT/SpatialLM/saves/deepcad_train100_canonical_edge_zero")
SHUF_CKPT=$(resolve_ckpt "$ROOT/SpatialLM/saves/deepcad_train100_canonical_edge_shuffle")
REAL_CKPT=$(resolve_ckpt "$ROOT/SpatialLM/saves/deepcad_train100_canonical_ours")

run_one baseline "$BASE_CKPT" "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_train100_val.json"
run_one edge_zero "$ZERO_CKPT" "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_edge_zero_train100_val.json"
run_one edge_shuffle "$SHUF_CKPT" "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_edge_shuffle_train100_val.json"
run_one ours "$REAL_CKPT" "$ROOT/cad_spatial_dataset/DeepCAD/deepcad_cad_ours_train100_val.json"

"$CADPY" scripts/deepcad/edge_ablation_compare.py --decode-root "$OUT_ROOT" | tee -a "$LOG"
log "ALL EDGE ABLATION DECODE DONE -> $OUT_ROOT"
