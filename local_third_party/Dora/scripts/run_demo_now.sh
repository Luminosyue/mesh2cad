#!/usr/bin/env bash
# Install remaining deps (if needed) + run Dora-VAE demo inference. No training.
set -euo pipefail

ROOT="/data/home/cuiyuehan/project/mesh2cad/Dora"
PL="$ROOT/pytorch_lightning"
VENV="$ROOT/.venv"
CKPT="$PL/ckpts/Dora-VAE-1.1/dora_vae_1_1.ckpt"

export PIP_USER=0
export PIP_CACHE_DIR="$ROOT/.pip-cache"
mkdir -p "$PIP_CACHE_DIR"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.1}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

# shellcheck disable=SC1091
source "$VENV/bin/activate"
cd "$PL"

echo "== Checks =="
nvidia-smi -L
test -f "$CKPT"
ls -lh "$CKPT"
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'; print(torch.__version__, torch.cuda.get_device_name(0))"

echo "== Ensure inference deps =="
if ! python -c "import pytorch_lightning,skimage,cv2,timm,transformers,diffusers,matplotlib,pandas,mcubes,tensorboardX" 2>/dev/null; then
  pip install \
    pytorch-lightning==2.2.4 \
    scikit-image==0.23.2 matplotlib==3.8.4 pandas==2.2.2 \
    "numpy==1.26.4" opencv-python==4.9.0.80 PyMCubes==0.1.4 \
    tensorboardX==2.6.2.2 timm==0.9.16 transformers==4.40.1 \
    diffusers==0.31.0 datasets==2.19.0 "trimesh==4.3.2" \
    joblib==1.4.0
fi

echo "== Run inference =="
bash test_autoencoder_single_gpu.sh

echo "== Outputs =="
find outputs -type f \( -name '*.obj' -o -name '*.png' -o -name '*.jpg' \) 2>/dev/null | head -50
echo "Done. See: $PL/outputs/"
