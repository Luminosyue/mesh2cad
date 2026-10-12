#!/usr/bin/env bash
# Canonical Train100: baseline then ours. Snatch GPU, OOM→换卡续训.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CADPY="${CADPY:-/data/miniconda3/envs/cadfit-env/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/DeepCAD"
SNATCH_LOG="$LOG_DIR/train100_canonical_snatch.log"
LOCK=/tmp/train100_canonical_snatch.lock
MIN_FREE="${MIN_FREE:-30000}"
POLL_SEC="${POLL_SEC:-3}"

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] train100 canonical snatch already running"; exit 0; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG" >&2; }

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
    # must not write to stdout — caller captures GPU id via $()
    echo "[$(date '+%F %T')] wait GPU… best=${GPU} free=${FREE}MB need>=${MIN_FREE}" >> "$SNATCH_LOG"
    sleep "$POLL_SEC"
  done
}

cd "$ROOT"
log "=== ensure canonical ShareGPT train100 ==="
"$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
  --variant ours --val-ratio 0.2 --name-suffix train100 --seed 42
"$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
  --variant baseline --val-ratio 0.2 --name-suffix train100 --seed 42

python3 - <<'PY'
import json
from pathlib import Path
for v in ("ours", "baseline"):
    for split in ("train", "val"):
        p = Path(f"cad_spatial_dataset/DeepCAD/deepcad_cad_{v}_train100_{split}.json")
        recs = json.loads(p.read_text())
        assert all("canonical" in r["point_clouds"][0] for r in recs), v
        print(v, split, len(recs), recs[0]["point_clouds"][0])
PY

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd "$ROOT/SpatialLM"

run_variant() {
  local cfg="$1"
  local tag="$2"
  local out_dir="$3"
  local edge_env="$4"
  local logfile="$LOG_DIR/train100_canonical_${tag}.log"

  mkdir -p "$out_dir"
  log "=== START variant=$tag cfg=$cfg ==="

  if [[ ! -f "$out_dir/dataset_dict.json" ]]; then
    GPU=$(wait_gpu)
    log "[$tag] preprocess on GPU=$GPU"
    python3 - <<PY
from pathlib import Path
import re
p = Path("$cfg")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: true", t, flags=re.M)
t = re.sub(r"^resume_from_checkpoint:.*\n?", "", t, flags=re.M)
p.write_text(t)
PY
    if [[ "$edge_env" == "1" ]]; then export CAD_USE_EDGE_SCORE=1; else unset CAD_USE_EDGE_SCORE; fi
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$cfg" >> "$logfile" 2>&1 || true
  fi

  python3 - <<PY
from pathlib import Path
import re
p = Path("$cfg")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", t, flags=re.M)
t = re.sub(r"^resume_from_checkpoint:.*\n?", "", t, flags=re.M)
p.write_text(t)
print("overwrite=false")
PY

  while true; do
    if [[ -f "$out_dir/all_results.json" || -f "$out_dir/train_results.json" ]]; then
      log "[$tag] DONE"
      return 0
    fi
    if pgrep -f "train.py ${cfg}" >/dev/null 2>&1; then
      sleep 30
      continue
    fi
    GPU=$(wait_gpu)
    log "[$tag] LAUNCH train on GPU=$GPU"
    if [[ "$edge_env" == "1" ]]; then export CAD_USE_EDGE_SCORE=1; else unset CAD_USE_EDGE_SCORE; fi
    set +e
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$cfg" >> "$logfile" 2>&1
    rc=$?
    set -e
    log "[$tag] train exit=$rc"
    if [[ -f "$out_dir/all_results.json" || -f "$out_dir/train_results.json" ]]; then
      log "[$tag] DONE"
      return 0
    fi
    if tail -80 "$logfile" | grep -qi "OutOfMemoryError\|CUDA out of memory"; then
      log "[$tag] OOM — re-snatch"
      sleep 2
      continue
    fi
    sleep 5
  done
}

log "train100 canonical pipeline start"
# Fresh dirs
rm -rf saves/deepcad_train100_canonical_baseline saves/deepcad_train100_canonical_ours
mkdir -p saves/deepcad_train100_canonical_baseline saves/deepcad_train100_canonical_ours

run_variant configs/spatiallm_cad_train100_canonical_baseline.yaml baseline \
  saves/deepcad_train100_canonical_baseline ""
run_variant configs/spatiallm_cad_train100_canonical_ours.yaml ours \
  saves/deepcad_train100_canonical_ours 1
log "ALL DONE: baseline + ours train100 canonical"
echo "Saves: SpatialLM/saves/deepcad_train100_canonical_{baseline,ours}/"
