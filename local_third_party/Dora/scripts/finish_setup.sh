#!/usr/bin/env bash
# Finish Dora inference setup: remaining pip deps + download weights (no training).
# Run this in YOUR interactive terminal (not Cursor agent sandbox).
set -euo pipefail

ROOT="/data/home/cuiyuehan/project/mesh2cad/Dora"
PL="$ROOT/pytorch_lightning"
VENV="$ROOT/.venv"

export PIP_USER=0
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$ROOT/.pip-cache}"
mkdir -p "$PIP_CACHE_DIR"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.1}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
# If you use clash/mihomo, uncomment:
# export http_proxy=http://127.0.0.1:7890 https_proxy=http://127.0.0.1:7890

# shellcheck disable=SC1091
source "$VENV/bin/activate"
cd "$PL"
python -V
echo "CUDA_HOME=$CUDA_HOME HF_ENDPOINT=$HF_ENDPOINT PIP_CACHE_DIR=$PIP_CACHE_DIR"

echo "== Install remaining inference deps =="
pip install \
  datasets==2.19.0 diffusers==0.31.0 einops==0.8.0 "huggingface-hub==0.26.2" \
  imageio==2.34.1 jaxtyping==0.2.28 joblib==1.4.0 lightning-utilities==0.11.2 \
  matplotlib==3.8.4 "numpy==1.26.4" omegaconf==2.3.0 opencv-python==4.9.0.80 \
  pandas==2.2.2 pillow==10.3.0 plyfile==1.0.3 PyMCubes==0.1.4 \
  pytorch-lightning==2.2.4 PyYAML==6.0.1 safetensors==0.4.3 \
  scikit-image==0.23.2 scipy==1.13.0 tensorboardX==2.6.2.2 \
  timm==0.9.16 tqdm==4.66.2 transformers==4.40.1 "trimesh==4.3.2"

echo "== Verify imports =="
python - <<'PY'
mods = ['torch','torch_cluster','diso','pytorch_lightning','einops','omegaconf',
        'skimage','numpy','huggingface_hub','diffusers','trimesh','cv2','timm']
bad=[]
for m in mods:
  try:
    __import__(m); print('OK', m)
  except Exception as e:
    print('MISS', m, e); bad.append(m)
import torch
print('torch', torch.__version__, 'cuda', torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')
if bad:
  raise SystemExit('missing: '+','.join(bad))
PY

echo "== Download Dora-VAE-1.1 weights (~2.2GB) =="
mkdir -p ckpts
if [ ! -f ckpts/Dora-VAE-1.1/dora_vae_1_1.ckpt ]; then
  python download.py
fi
ls -lh ckpts/Dora-VAE-1.1/
test -f ckpts/Dora-VAE-1.1/dora_vae_1_1.ckpt
echo
echo "SETUP DONE."
echo "Run inference with:"
echo "  export CUDA_VISIBLE_DEVICES=0"
echo "  source $VENV/bin/activate"
echo "  cd $PL && bash test_autoencoder_single_gpu.sh"
