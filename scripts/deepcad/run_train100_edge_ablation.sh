#!/usr/bin/env bash
# Dora edge ablation: train 7ch Zero + Shuffle (Real/Baseline reuse prior runs).
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CADPY="${CADPY:-/data/miniconda3/envs/cadfit-env/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/DeepCAD"
SNATCH_LOG="$LOG_DIR/train100_edge_ablation_snatch.log"
LOCK=/tmp/train100_edge_ablation_snatch.lock
MIN_FREE="${MIN_FREE:-32000}"
POLL_SEC="${POLL_SEC:-5}"
SEED=42

exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] edge ablation snatch already running"; exit 0; }

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
    echo "[$(date '+%F %T')] wait GPU… best=${GPU} free=${FREE}MB need>=${MIN_FREE}" >> "$SNATCH_LOG"
    sleep "$POLL_SEC"
  done
}

cd "$ROOT"
log "=== build edge ablation features (zero / shuffle on disk) ==="
"$CADPY" scripts/deepcad/build_edge_ablation_features.py --seed "$SEED"

log "=== ShareGPT datasets (same 80/19 split seed=$SEED) ==="
# Lock split to existing baseline train/val IDs
SPLIT="$ROOT/cad_spatial_dataset/DeepCAD/split_train100_seed42.json"
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
for v in baseline edge_zero edge_shuffle ours; do
  "$CADPY" scripts/deepcad/create_spatiallm_cad_dataset.py \
    --variant "$v" --name-suffix train100 --val-ratio 0.2 --seed "$SEED" \
    --split-json "$SPLIT"
done

python3 - <<'PY'
import json
from pathlib import Path
root = Path("cad_spatial_dataset/DeepCAD")
split = json.loads((root / "split_train100_seed42.json").read_text())
for v in ["baseline", "edge_zero", "edge_shuffle", "ours"]:
    tr = json.loads((root / f"deepcad_cad_{v}_train100_train.json").read_text())
    va = json.loads((root / f"deepcad_cad_{v}_train100_val.json").read_text())
    assert [r["id"] for r in tr] == split["train_ids"], v
    assert [r["id"] for r in va] == split["val_ids"], v
    pc0 = tr[0]["point_clouds"][0]
    print(v, len(tr), len(va), pc0)
print("split OK", len(split["train_ids"]), len(split["val_ids"]))
PY

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CAD_USE_EDGE_SCORE=1
export CAD_STEM_EDGE_INIT=rgb_mean
export CAD_STEM_SEED=0
cd "$ROOT/SpatialLM"

run_variant() {
  local cfg="$1"
  local tag="$2"
  local out_dir="$3"
  local logfile="$LOG_DIR/train100_canonical_${tag}.log"

  if [[ -f "$out_dir/train_results.json" || -f "$out_dir/all_results.json" ]]; then
    log "[$tag] SKIP — already trained"
    return 0
  fi

  rm -rf "$out_dir"
  mkdir -p "$out_dir"
  log "=== START $tag cfg=$cfg ==="

  GPU=$(wait_gpu)
  log "[$tag] preprocess on GPU=$GPU"
  python3 - <<PY
from pathlib import Path
import re
p = Path("$cfg")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: true", t, flags=re.M)
p.write_text(t)
PY
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$cfg" >> "$logfile" 2>&1 || true

  python3 - <<PY
from pathlib import Path
import re
p = Path("$cfg")
t = p.read_text()
t = re.sub(r"^overwrite_output_dir:.*$", "overwrite_output_dir: false", t, flags=re.M)
p.write_text(t)
PY

  while true; do
    if [[ -f "$out_dir/train_results.json" || -f "$out_dir/all_results.json" ]]; then
      log "[$tag] DONE"
      return 0
    fi
    if pgrep -f "train.py ${cfg}" >/dev/null 2>&1; then
      sleep 30
      continue
    fi
    GPU=$(wait_gpu)
    log "[$tag] LAUNCH train GPU=$GPU"
    set +e
    CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" train.py "$cfg" >> "$logfile" 2>&1
    rc=$?
    set -e
    log "[$tag] train exit=$rc"
    if [[ -f "$out_dir/train_results.json" || -f "$out_dir/all_results.json" ]]; then
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

log "edge ablation train: Zero then Shuffle (Baseline+Real already done)"
run_variant configs/spatiallm_cad_train100_canonical_edge_zero.yaml edge_zero \
  saves/deepcad_train100_canonical_edge_zero
run_variant configs/spatiallm_cad_train100_canonical_edge_shuffle.yaml edge_shuffle \
  saves/deepcad_train100_canonical_edge_shuffle

log "ALL DONE edge ablation training"
