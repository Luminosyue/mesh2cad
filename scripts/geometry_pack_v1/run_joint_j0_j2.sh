#!/usr/bin/env bash
# Launch J0 (surface) and J2 (separate edge tokens) on two pinned GPUs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON="${PYTHON:-/data/miniconda3/envs/spatiallm/bin/python}"
CADPY="${CADPY:-/data/miniconda3/envs/cadfit-env/bin/python}"
LOG_DIR="$ROOT/cad_spatial_dataset/joint_deepcad_fusion360_v1"
GPU_J0="${GPU_J0:-5}"
GPU_J2="${GPU_J2:-7}"

"$CADPY" "$ROOT/scripts/geometry_pack_v1/export_joint_j0j2_sharegpt.py"

export DISABLE_VERSION_CHECK=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$ROOT/SpatialLM/saves/joint_j0_surface_v1" \
         "$ROOT/SpatialLM/saves/joint_j2_sepedge_v1"

echo "[$(date '+%F %T')] J0 GPU=$GPU_J0  J2 GPU=$GPU_J2"

(
  cd "$ROOT/SpatialLM"
  unset CAD_USE_EDGE_SCORE CAD_USE_SEPARATE_EDGE_TOKENS CAD_EDGE_SOURCE
  CUDA_VISIBLE_DEVICES="$GPU_J0" "$PYTHON" train.py configs/spatiallm_cad_joint_j0_surface.yaml
) >> "$LOG_DIR/joint_j0_surface_v1.log" 2>&1 &
echo $! > /tmp/joint_j0.pid

(
  cd "$ROOT/SpatialLM"
  unset CAD_USE_EDGE_SCORE
  export CAD_USE_SEPARATE_EDGE_TOKENS=1
  export CAD_EDGE_SOURCE=gt_sharp
  CUDA_VISIBLE_DEVICES="$GPU_J2" "$PYTHON" train.py configs/spatiallm_cad_joint_j2_sepedge.yaml
) >> "$LOG_DIR/joint_j2_sepedge_v1.log" 2>&1 &
echo $! > /tmp/joint_j2.pid

echo "J0 pid=$(cat /tmp/joint_j0.pid) log=$LOG_DIR/joint_j0_surface_v1.log"
echo "J2 pid=$(cat /tmp/joint_j2.pid) log=$LOG_DIR/joint_j2_sepedge_v1.log"
wait || true
