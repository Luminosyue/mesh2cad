#!/usr/bin/env bash
# Canonical overfit10 sanity: rebuild ShareGPT → train ours → decode+geom gate.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CADPY="${CADPY:-/data/miniconda3/envs/cadfit-env/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/DeepCAD"
SNATCH_LOG="$LOG_DIR/overfit10_canonical_snatch.log"
TRAIN_LOG="$LOG_DIR/overfit10_canonical_ours.log"
CFG=configs/spatiallm_cad_overfit10_canonical_ours.yaml
OUT="$ROOT/SpatialLM/saves/deepcad_overfit10_canonical_ours"
DECODE_OUT="$ROOT/ours3/deepcad_overfit10_canonical_decode"
LOCK=/tmp/overfit10_canonical_snatch.lock
MIN_FREE="${MIN_FREE:-28000}"
POLL_SEC="${POLL_SEC:-2}"
TARGET_STEPS="${TARGET_STEPS:-2000}"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] overfit10 canonical snatch already running"; exit 0; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG"; }

best_gpu() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1
}

wait_gpu() {
  while true; do
    read -r FREE GPU <<<"$(best_gpu)"
    FREE=${FREE:-0}; GPU=${GPU:--1}
    if (( FREE >= MIN_FREE )); then
      echo "$GPU"
      return 0
    fi
    log "wait GPU… best=${GPU} free=${FREE}MB need>=${MIN_FREE}"
    sleep "$POLL_SEC"
  done
}

is_done() {
  [[ -f "$OUT/all_results.json" || -f "$OUT/train_results.json" ]] && return 0
  [[ -d "$OUT/checkpoint-${TARGET_STEPS}" ]] && return 0
  return 1
}

cd "$ROOT"
log "=== rebuild canonical overfit10 ShareGPT ==="
"$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
  --limit 10 --name-suffix overfit10 --variant ours --seed 42
"$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
  --limit 10 --name-suffix overfit10 --variant baseline --seed 42

# sanity: must point at features_canonical
python3 - <<'PY'
import json
from pathlib import Path
p = Path("cad_spatial_dataset/DeepCAD/deepcad_cad_ours_overfit10_train.json")
recs = json.loads(p.read_text())
assert len(recs) == 10, len(recs)
for r in recs:
    pc = r["point_clouds"][0]
    assert "canonical" in pc, pc
    assert Path("cad_spatial_dataset/DeepCAD") / pc
print("ShareGPT OK:", [r["id"] for r in recs])
print("pc0:", recs[0]["point_clouds"][0])
print("label0 head:", recs[0]["conversations"][1]["value"][:120])
PY

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CAD_USE_EDGE_SCORE=1
cd "$ROOT/SpatialLM"
mkdir -p "$OUT"
: > "$TRAIN_LOG"

# Fresh save dir for canonical
if [[ -d "$OUT" && ! -f "$OUT/dataset_dict.json" ]]; then
  rm -rf "$OUT"
  mkdir -p "$OUT"
fi

# Pass 1 preprocess
if [[ ! -f "$OUT/dataset_dict.json" ]]; then
  GPU=$(wait_gpu)
  log "preprocess on GPU=$GPU"
  python3 - <<PY
from pathlib import Path
import re
p = Path("$CFG")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: true", t, flags=re.M)
p.write_text(t)
PY
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$TRAIN_LOG" 2>&1 || true
fi

python3 - <<PY
from pathlib import Path
import re
p = Path("$CFG")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", t, flags=re.M)
p.write_text(t)
print("overwrite=false")
PY

log "SNATCH START overfit10 canonical ours"
while true; do
  if is_done; then
    log "TRAIN DONE"
    break
  fi
  if pgrep -f "train.py ${CFG}" >/dev/null 2>&1; then
    sleep "$POLL_SEC"
    continue
  fi
  GPU=$(wait_gpu)
  log "LAUNCH train GPU=$GPU"
  set +e
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$TRAIN_LOG" 2>&1
  rc=$?
  set -e
  log "train exit=$rc"
  if is_done; then
    break
  fi
  if tail -80 "$TRAIN_LOG" | grep -qi "OutOfMemoryError\|CUDA out of memory"; then
    log "OOM — re-snatch"
    sleep 1
    continue
  fi
  sleep 3
done

# Decode + geometry gate
CKPT="$OUT/checkpoint-${TARGET_STEPS}"
[[ -d "$CKPT" ]] || CKPT="$OUT"
GPU=$(wait_gpu)
log "DECODE on GPU=$GPU ckpt=$CKPT"
cd "$ROOT"
CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" scripts/deepcad/decode_overfit10.py \
  --checkpoint "$CKPT" --variant ours --use-edge \
  --train-json cad_spatial_dataset/DeepCAD/deepcad_cad_ours_overfit10_train.json \
  --out "$DECODE_OUT" \
  2>&1 | tee -a "$SNATCH_LOG"

log "GEOM gate (inverse T → source STEP vs GT)"
"$CADPY" scripts/deepcad/overfit10_canonical_gate.py \
  --decode-dir "$DECODE_OUT/ours/$(basename "$CKPT")" \
  --train-dir cad_spatial_dataset/DeepCAD/train \
  --out "$DECODE_OUT/gate_report.json" \
  2>&1 | tee -a "$SNATCH_LOG"

log "ALL DONE overfit10 canonical"
