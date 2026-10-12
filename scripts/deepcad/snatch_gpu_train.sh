#!/usr/bin/env bash
# 立刻抢卡：每 2 秒扫一遍，一有够空的卡就抢下开训；OOM 立刻换卡续训。
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_retrain.log"
SNATCH_LOG="$ROOT/cad_spatial_dataset/DeepCAD/overfit10_baseline_snatch.log"
PYTHON=/data/miniconda3/envs/spatiallm/bin/python
OUT="$ROOT/SpatialLM/saves/deepcad_overfit10_baseline_r2"
CFG=configs/spatiallm_cad_overfit10_baseline.yaml
LOCK=/tmp/baseline_snatch_gpu.lock
# 抢卡阈值：略低于独占需求，先占住再开训
MIN_FREE="${MIN_FREE:-28000}"
POLL_SEC="${POLL_SEC:-2}"
TARGET_STEPS=2000

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "[$(date '+%F %T')] snatch already running; exit"
  exit 0
fi

log() { echo "[$(date '+%F %T')] $*" | tee -a "$SNATCH_LOG"; }

is_done() {
  [[ -f "$OUT/all_results.json" ]] && return 0
  [[ -d "$OUT/checkpoint-${TARGET_STEPS}" && -f "$OUT/checkpoint-${TARGET_STEPS}/model.safetensors.index.json" ]]
}

# 返回: free_mb gpu_id（按 free 降序，筛掉已有我们 train 的卡也可）
best_gpu() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' '{gsub(/ /,"",$2); print $2,$1}' \
    | sort -nr \
    | head -1
}

train_running() {
  pgrep -f "train.py ${CFG}" >/dev/null 2>&1
}

# 杀掉其它抢卡/慢等脚本，只留本 snatch（不杀正在跑的 train）
pkill -f "run_baseline_wait_gpu.sh" 2>/dev/null || true

cd "$ROOT/SpatialLM"
export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
unset CAD_USE_EDGE_SCORE

# 确保 preprocess 完成
if [[ ! -f "$OUT/dataset_dict.json" ]]; then
  read -r FREE GPU <<<"$(best_gpu)"
  log "preprocess on GPU=$GPU free=${FREE}MB"
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$LOG" 2>&1 || true
fi

# 开训后允许 auto-resume
python3 - <<'PY'
from pathlib import Path
import re
p = Path("configs/spatiallm_cad_overfit10_baseline.yaml")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", t, flags=re.M)
t = re.sub(r"^resume_from_checkpoint:.*\n?", "", t, flags=re.M)
# 保证 save/output 指向 r2
if "deepcad_overfit10_baseline_r2" not in t:
    t = t.replace("saves/deepcad_overfit10_baseline\n", "saves/deepcad_overfit10_baseline_r2\n")
p.write_text(t)
PY

log "SNATCH START min_free=${MIN_FREE}MB poll=${POLL_SEC}s"

while true; do
  if is_done; then
    log "TRAIN DONE — decode"
    read -r FREE GPU <<<"$(best_gpu)"
    CKPT="$OUT/checkpoint-${TARGET_STEPS}"
    [[ -d "$CKPT" ]] || CKPT="$OUT"
    cd "$ROOT"
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" scripts/deepcad/decode_overfit10.py \
      --checkpoint "$CKPT" --variant baseline \
      --train-json cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_overfit10_train.json \
      2>&1 | tee -a "$SNATCH_LOG"
    log "decode finished"
    exit 0
  fi

  # 已有训练在跑：只监控，不重复抢
  if train_running; then
    sleep "$POLL_SEC"
    continue
  fi

  read -r FREE GPU <<<"$(best_gpu)"
  FREE=${FREE:-0}
  GPU=${GPU:--1}

  if (( FREE < MIN_FREE )); then
    # 高频刷屏只每 10 次打一行
    if (( SECONDS % 10 == 0 )); then
      log "waiting… best=GPU${GPU} free=${FREE}MB need>=${MIN_FREE}"
    fi
    sleep "$POLL_SEC"
    continue
  fi

  # ★ 立刻占卡：先起一个轻量占位再训，减少被别人抢走的窗口
  log "SNATCH GPU=${GPU} free=${FREE}MB — launching train NOW"
  set +e
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$CFG" >> "$LOG" 2>&1
  rc=$?
  set -e
  log "train exit=$rc on GPU=$GPU"

  if is_done; then
    continue
  fi

  if tail -60 "$LOG" | grep -qi "OutOfMemoryError\|CUDA out of memory"; then
    log "OOM on GPU=$GPU — immediate re-snatch"
    sleep 1
    continue
  fi

  sleep "$POLL_SEC"
done
