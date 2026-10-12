#!/usr/bin/env bash
# Wait until N GPUs each have >= MIN_FREE MiB, then torchrun J2 on them.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
LOG="$ROOT/cad_spatial_dataset/joint_deepcad_fusion360_v1/joint_j2_sepedge_v1.log"
SNATCH_LOG="$ROOT/cad_spatial_dataset/joint_deepcad_fusion360_v1/joint_j2_ddp_snatch.log"
MIN_FREE="${MIN_FREE:-32000}"
N_GPU="${N_GPU:-2}"
LOCK=/tmp/joint_j2_ddp_snatch.lock

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] J2 snatch already running"; exit 0; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG" >&2; }

pick_gpus() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' -v m="$MIN_FREE" '{gsub(/ /,"",$2); if ($2+0>=m) print $2,$1}' \
    | sort -nr | head -n "$N_GPU" | awk '{print $2}' | paste -sd, -
}

OUT="$ROOT/SpatialLM/saves/joint_j2_sepedge_v1"
if [[ -f "$OUT/all_results.json" || -f "$OUT/train_results.json" ]]; then
  log "J2 already done"; exit 0
fi

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
unset CAD_USE_EDGE_SCORE
export CAD_USE_SEPARATE_EDGE_TOKENS=1
export CAD_EDGE_SOURCE=gt_sharp
export MASTER_PORT="${MASTER_PORT:-29531}"
export FORCE_TORCHRUN=1
export NPROC_PER_NODE="$N_GPU"

# Keep effective batch=4 with 2 GPUs
CFG_TMP=$(mktemp /tmp/joint_j2_ddp_XXXX.yaml)
cp "$ROOT/SpatialLM/configs/spatiallm_cad_joint_j2_sepedge.yaml" "$CFG_TMP"
sed -i 's/gradient_accumulation_steps: 4/gradient_accumulation_steps: 2/' "$CFG_TMP"

while true; do
  if pgrep -f "train.py .*joint_j2_sepedge" >/dev/null 2>&1; then
    sleep 60; continue
  fi
  if [[ -f "$OUT/all_results.json" || -f "$OUT/train_results.json" ]]; then
    log "DONE"; break
  fi
  GPUS=$(pick_gpus)
  NFOUND=$(echo "$GPUS" | awk -F, '{print NF}')
  if [[ -z "$GPUS" || "$NFOUND" -lt "$N_GPU" ]]; then
    log "wait ${N_GPU}x>=${MIN_FREE}MB free (got: ${GPUS:-none})"
    sleep 15
    continue
  fi
  log "LAUNCH J2 DDP GPUs=$GPUS"
  cd "$ROOT/SpatialLM"
  export PATH="$(dirname "$PYTHON"):$PATH"
  CUDA_VISIBLE_DEVICES="$GPUS" "$PYTHON" train.py "$CFG_TMP" >> "$LOG" 2>&1 &
  TRAIN_PID=$!
  sleep 90
  if ! kill -0 "$TRAIN_PID" 2>/dev/null; then
    log "J2 exited early; see log"
    if tail -80 "$LOG" 2>/dev/null | grep -qi "OutOfMemoryError\|FileNotFoundError\|Error"; then
      sleep 10
      continue
    fi
  fi
  wait "$TRAIN_PID" || true
  if [[ -f "$OUT/all_results.json" || -f "$OUT/train_results.json" ]]; then
    log "DONE"; break
  fi
  sleep 10
done
rm -f "$CFG_TMP"
log "ALL DONE"
