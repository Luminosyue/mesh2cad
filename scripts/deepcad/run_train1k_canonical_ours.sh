#!/usr/bin/env bash
# DEEPCAD_1K_CANONICAL_V1 — Real Dora / Ours main model (vanilla 1K experiment).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CADPY="${CADPY:-/data/miniconda3/envs/cadfit-env/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/DeepCAD"
MANIFEST="$ROOT/cad_spatial_dataset/DeepCAD/manifest_train1k_v1.json"
SPLIT="$ROOT/cad_spatial_dataset/DeepCAD/split_train1k_complexity_seed42.json"
CFG="configs/spatiallm_cad_train1k_canonical_ours.yaml"
OUT="saves/deepcad_train1k_canonical_ours"
LOG="$LOG_DIR/train1k_canonical_ours.log"
SNATCH_LOG="$LOG_DIR/train1k_canonical_snatch.log"
LOCK=/tmp/train1k_canonical_snatch.lock
MIN_FREE="${MIN_FREE:-30000}"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] train1k snatch already running"; exit 0; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG" >&2; }

best_gpu() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1
}

wait_gpu() {
  while true; do
    read -r FREE GPU <<<"$(best_gpu)"
    FREE=${FREE:-0}; GPU=${GPU:--1}
    if (( FREE >= MIN_FREE )); then echo "$GPU"; return 0; fi
    echo "[$(date '+%F %T')] wait GPU free=${FREE}MB need>=${MIN_FREE}" >> "$SNATCH_LOG"
    sleep 3
  done
}

log "=== build manifest + split ==="
"$PYTHON" scripts/deepcad/build_train1k_complexity_split.py

log "=== ShareGPT JSON ==="
"$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
  --manifest "$MANIFEST" \
  --split-json "$SPLIT" \
  --variant ours \
  --name-suffix train1k

"$PYTHON" - <<PY
import json
from pathlib import Path
split = json.loads(Path("$SPLIT").read_text())
for name, key in [("train","train_ids"),("val","val_ids"),("test","test_ids")]:
    p = Path(f"cad_spatial_dataset/DeepCAD/deepcad_cad_ours_train1k_{name}.json")
    n = len(json.loads(p.read_text()))
    assert n == len(split[key]), (name, n, len(split[key]))
    print(name, n, "OK")
PY

log "=== label audit (must be 0 truncated) ==="
"$PYTHON" scripts/deepcad/audit_sequence_length_contract.py \
  --manifest "$MANIFEST" --cutoff-len 4096 --max-new-tokens 4096 \
  --skip-encoder \
  --out "$LOG_DIR/train1k_label_audit.json" | tee -a "$SNATCH_LOG"
TRUNC=$(python3 - <<PY
import json
s=json.load(open("$LOG_DIR/train1k_label_audit.json"))
print(s["training_summary"]["label_truncated_count"])
PY
)
if [[ "$TRUNC" != "0" ]]; then
  log "ABORT: label_truncated_count=$TRUNC"; exit 1
fi

export DISABLE_VERSION_CHECK=1
export CAD_USE_EDGE_SCORE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd "$ROOT/SpatialLM"
mkdir -p "$OUT"

log "=== train DEEPCAD_1K_CANONICAL_V1 ==="
while true; do
  if [[ -f "$OUT/all_results.json" || -f "$OUT/train_results.json" ]]; then
    log "DONE"; break
  fi
  if pgrep -f "train.py ${CFG}" >/dev/null 2>&1; then sleep 30; continue; fi
  GPU=$(wait_gpu)
  log "LAUNCH GPU=$GPU"
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$LOG" 2>&1 || true
  if tail -80 "$LOG" 2>/dev/null | grep -qi "OutOfMemoryError"; then sleep 2; continue; fi
  sleep 5
done

log "ALL DONE: $OUT"
