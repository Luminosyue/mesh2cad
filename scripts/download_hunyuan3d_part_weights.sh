#!/usr/bin/env bash
# Download tencent/Hunyuan3D-Part weights for X-Part inference.
#
# Expected layout (HY3DGEN_MODELS defaults to ours3/.cache/xpart):
#   $HY3DGEN_MODELS/tencent/Hunyuan3D-Part/
#     model/model.safetensors
#     conditioner/conditioner.safetensors
#     shapevae/shapevae.safetensors
#     p3sam/p3sam.safetensors
#     */config.json
#
# Usage:
#   bash scripts/download_hunyuan3d_part_weights.sh
#   HF_ENDPOINT=https://hf-mirror.com bash scripts/download_hunyuan3d_part_weights.sh

set -euo pipefail

ROOT="/data/home/cuiyuehan/project/mesh2cad"
PY="/data/miniconda3/envs/hy3d/bin/python"
export HY3DGEN_MODELS="${HY3DGEN_MODELS:-$ROOT/ours3/.cache/xpart}"
LOCAL_DIR="$HY3DGEN_MODELS/tencent/Hunyuan3D-Part"
P3_LOCAL="$ROOT/Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors"

mkdir -p "$LOCAL_DIR"

echo "[download] HY3DGEN_MODELS=$HY3DGEN_MODELS"
echo "[download] target=$LOCAL_DIR"

"$PY" - <<'PY'
import os
from huggingface_hub import snapshot_download

local_dir = os.path.join(
    os.environ["HY3DGEN_MODELS"], "tencent", "Hunyuan3D-Part"
)
path = snapshot_download(
    repo_id="tencent/Hunyuan3D-Part",
    local_dir=local_dir,
)
print("snapshot_download ok:", path)
PY

if [[ -f "$P3_LOCAL" && ! -f "$LOCAL_DIR/p3sam/p3sam.safetensors" ]]; then
  mkdir -p "$LOCAL_DIR/p3sam"
  ln -sf "$P3_LOCAL" "$LOCAL_DIR/p3sam/p3sam.safetensors"
  echo "[download] linked local P3-SAM weights"
fi

echo "[download] done"
