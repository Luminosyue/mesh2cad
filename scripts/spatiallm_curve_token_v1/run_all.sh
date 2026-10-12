#!/usr/bin/env bash
# Step 3: the three-arm overfit probe on 100 CADs.
#
#   B0  surface only                 (existing J0 recipe)
#   B1  surface + edge POINT tokens  (existing J2 sepedge recipe)
#   M2  surface + CURVE tokens       (ours)
#
# SpatialLM's loader preprocesses, exits, and only trains on the second launch,
# so every arm is invoked twice.
#
# Usage: run_all.sh <gpu> [arms...]     e.g. run_all.sh 5 B0 B1 M2
set -euo pipefail
GPU="${1:-0}"
shift || true
# These GPUs are shared and a neighbour can appear mid-run; "auto" picks the one
# with the most free memory at launch time.
if [ "$GPU" = "auto" ]; then
  GPU=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
        | sort -t, -k2 -nr | head -1 | cut -d, -f1 | tr -d ' ')
  echo "auto-selected GPU $GPU"
fi
ARMS=("$@")
[ ${#ARMS[@]} -eq 0 ] && ARMS=(B0 B1 M2)

cd "$(dirname "$0")/../.."
REPO="$PWD"
PY="${PYTHON_BIN:-/data/miniconda3/envs/spatiallm/bin/python}"
# ~7600 surface voxel tokens per sample makes this run allocation-heavy; on a
# shared GPU fragmentation alone is enough to OOM. Run the arms sequentially.
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
CFG_DIR="$REPO/scripts/spatiallm_curve_token_v1/configs"
LOG_DIR="$REPO/ours3/spatiallm_curve_token_v1/runs"
mkdir -p "$LOG_DIR"

run_arm() {
  local arm="$1" cfg="$2" launcher="$3"
  local log="$LOG_DIR/${arm}.log"
  local save_dir
  save_dir="$REPO/SpatialLM/$(sed -n 's/^save_dir: *//p' "$cfg" | head -1)"
  echo "=== $arm on GPU $GPU (config $(basename "$cfg")) ==="
  # The loader preprocesses, then sys.exit(0); only a second launch trains. Skip
  # the preprocess launch when the cache is already there, otherwise the arm
  # would train twice.
  local phases=(train)
  [ -f "$save_dir/dataset_dict.json" ] || phases=(preprocess train)
  for phase in "${phases[@]}"; do
    echo "--- $arm $phase ---" >> "$log"
    ( cd "$REPO/SpatialLM" && CUDA_VISIBLE_DEVICES="$GPU" $launcher "$cfg" ) >> "$log" 2>&1
  done
  echo "=== $arm done, log $log ==="
}

for arm in "${ARMS[@]}"; do
  case "$arm" in
    B0)
      unset CAD_USE_EDGE_SCORE CAD_USE_SEPARATE_EDGE_TOKENS CAD_EDGE_SOURCE CAD_SECOND_STREAM
      run_arm B0 "$CFG_DIR/curve100_b0_surface.yaml" "$PY $REPO/SpatialLM/train.py"
      ;;
    B1)
      unset CAD_USE_EDGE_SCORE
      export CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_EDGE_SOURCE=gt_sharp CAD_SECOND_STREAM=edge_points
      run_arm B1 "$CFG_DIR/curve100_b1_edgepoints.yaml" "$PY $REPO/SpatialLM/train.py"
      ;;
    M2)
      unset CAD_USE_EDGE_SCORE
      export CAD_USE_SEPARATE_EDGE_TOKENS=1 CAD_SECOND_STREAM=curve_tokens
      run_arm M2 "$CFG_DIR/curve100_m2_curvetoken.yaml" \
        "$PY $REPO/scripts/spatiallm_curve_token_v1/train_curve_token_spatiallm.py"
      ;;
    *) echo "unknown arm $arm" >&2; exit 1 ;;
  esac
done
