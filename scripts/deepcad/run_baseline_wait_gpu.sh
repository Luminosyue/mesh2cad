#!/usr/bin/env bash
# Wait for free GPU (>=32GB), fresh-train baseline overfit10 to r2, then decode.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_retrain.log"
WATCH="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_watch.log"
PYTHON=/data/miniconda3/envs/spatiallm/bin/python
OUT="$ROOT/SpatialLM/saves/deepcad_overfit10_baseline_r2"
CFG=configs/spatiallm_cad_overfit10_baseline.yaml
LOCK=/tmp/baseline_overfit10_r2.lock
MIN_FREE=36000

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] lock held; exit" >> "$WATCH"; exit 0; }
echo "[$(date '+%F %T')] wait-loop r2 start" | tee -a "$WATCH"

is_done() {
  [[ -f "$OUT/all_results.json" ]] && return 0
  [[ -d "$OUT/checkpoint-2000" && -f "$OUT/checkpoint-2000/model.safetensors.index.json" ]]
}

cd "$ROOT/SpatialLM"
if [[ ! -f "$OUT/dataset_dict.json" ]]; then
  BEST=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1)
  GPU=$(echo "$BEST" | awk '{print $2}')
  echo "[$(date '+%F %T')] preprocess on GPU $GPU" | tee -a "$WATCH"
  export DISABLE_VERSION_CHECK=1
  unset CAD_USE_EDGE_SCORE
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$LOG" 2>&1 || true
fi

# After preprocess, allow auto-resume on later OOM restarts
python3 - <<'PY'
from pathlib import Path
import re
p = Path("configs/spatiallm_cad_overfit10_baseline.yaml")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", t, flags=re.M)
# strip any stale resume_from_checkpoint so HF auto-picks last ckpt
t = re.sub(r"^resume_from_checkpoint:.*\n?", "", t, flags=re.M)
p.write_text(t)
print("overwrite_output_dir=false for auto-resume")
PY

while true; do
  if is_done; then
    echo "[$(date '+%F %T')] DONE — decode" | tee -a "$WATCH"
    GPU=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1 | awk '{print $2}')
    CKPT="$OUT/checkpoint-2000"; [[ -d "$CKPT" ]] || CKPT="$OUT"
    cd "$ROOT"
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" scripts/deepcad/decode_overfit10.py \
      --checkpoint "$CKPT" --variant baseline \
      --train-json cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_overfit10_train.json \
      2>&1 | tee -a "$WATCH"
    exit 0
  fi
  if pgrep -f "train.py configs/spatiallm_cad_overfit10_baseline" >/dev/null 2>&1; then
    sleep 60
    continue
  fi
  BEST=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' | sort -nr | head -1)
  FREE=$(echo "$BEST" | awk '{print $1}')
  GPU=$(echo "$BEST" | awk '{print $2}')
  if [[ -z "${FREE:-}" ]] || (( FREE < MIN_FREE )); then
    echo "[$(date '+%F %T')] wait GPU best=${GPU:-?} free=${FREE:-0} (<${MIN_FREE})" | tee -a "$WATCH"
    sleep 40
    continue
  fi
  echo "[$(date '+%F %T')] LAUNCH GPU=$GPU free=$FREE" | tee -a "$WATCH"
  cd "$ROOT/SpatialLM"
  export DISABLE_VERSION_CHECK=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
  unset CAD_USE_EDGE_SCORE
  set +e
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$LOG" 2>&1
  rc=$?
  set -e
  echo "[$(date '+%F %T')] train exit=$rc" | tee -a "$WATCH"
  sleep 15
done
