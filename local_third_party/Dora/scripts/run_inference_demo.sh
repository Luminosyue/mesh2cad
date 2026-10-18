#!/usr/bin/env bash
# One-shot: download Dora-VAE-1.1 weights and run demo inference (no training).
# Uses a project-local venv (avoids shared conda pkgs + avoids polluting ~/.local).
set -euo pipefail

ROOT="/data/home/cuiyuehan/project/mesh2cad/Dora"
PL="$ROOT/pytorch_lightning"
VENV="$ROOT/.venv"
cd "$PL"

echo "== GPU check =="
if ! command -v nvidia-smi >/dev/null || ! nvidia-smi -L >/dev/null 2>&1; then
  echo "ERROR: nvidia devices not available in this shell."
  exit 1
fi
nvidia-smi -L
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

# System /usr/bin/nvcc is CUDA 11.5, but torch==2.4.0+cu121 needs CUDA 12.1 toolkit
# to compile extensions like diso. Prefer the matching toolkit.
if [ -x /usr/local/cuda-12.1/bin/nvcc ]; then
  export CUDA_HOME=/usr/local/cuda-12.1
elif [ -x /usr/local/cuda/bin/nvcc ]; then
  export CUDA_HOME=/usr/local/cuda
fi
if [ -n "${CUDA_HOME:-}" ]; then
  export PATH="$CUDA_HOME/bin:$PATH"
  export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
fi
echo "CUDA_HOME=${CUDA_HOME:-unset}  nvcc=$(nvcc --version 2>/dev/null | awk '/release/ {print $NF}')"

# Do NOT install into ~/.local
export PIP_USER=0
unset PYTHONUSERBASE || true

echo "== Python venv at $VENV =="
if [ ! -x "$VENV/bin/python" ]; then
  # Prefer system python3.10 (matches official Dora torch wheels better than 3.11)
  if [ -x /usr/bin/python3.10 ]; then
    PY_BASE=/usr/bin/python3.10
  elif command -v python3.10 >/dev/null 2>&1; then
    PY_BASE=$(command -v python3.10)
  else
    PY_BASE=$(command -v python3)
  fi
  echo "Creating venv with $PY_BASE"
  "$PY_BASE" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -V
python -c "import sys; print(sys.executable)"

pip install -U pip setuptools wheel ninja

export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
echo "HF_ENDPOINT=$HF_ENDPOINT"

echo "== Install torch 2.4.0+cu121 into venv =="
if ! python -c "import torch; assert torch.__version__.startswith('2.4') and torch.cuda.is_available()" 2>/dev/null; then
  pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121
fi
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.get_device_name(0))"

# Packages whose setup.py imports torch MUST use --no-build-isolation
install_torch_ext() {
  local pkg="$1"
  shift
  if python -c "import $pkg" 2>/dev/null; then
    echo "$pkg already importable"
    return 0
  fi
  echo "Installing $pkg (no build isolation) ..."
  if ! pip install --only-binary=:all: "$@" 2>/dev/null; then
    pip install --no-build-isolation "$@"
  fi
  python -c "import $pkg; print('$pkg ok')"
}

echo "== Install torch-cluster =="
install_torch_ext torch_cluster torch-cluster -f https://data.pyg.org/whl/torch-2.4.0+cu121.html

echo "== Install diso (needs CUDA_HOME matching torch, i.e. 12.1) =="
if ! python -c "import diso" 2>/dev/null; then
  # Force nvcc 12.1 into PATH for this build; skip if still mismatched
  CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.1}" \
  PATH="${CUDA_HOME}/bin:$PATH" \
  FORCE_CUDA=1 \
  TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-8.9}" \
    pip install --no-build-isolation diso
fi
python -c "import diso; from diso import DiffDMC; print('diso ok')"

echo "== Install huggingface_hub + Dora core deps =="
pip install huggingface_hub
pip install \
  datasets==2.19.0 diffusers==0.31.0 einops==0.8.0 huggingface-hub==0.26.2 \
  imageio==2.34.1 jaxtyping==0.2.28 joblib==1.4.0 lightning-utilities==0.11.2 \
  matplotlib==3.8.4 "numpy==1.26.4" omegaconf==2.3.0 opencv-python==4.9.0.80 \
  pandas==2.2.2 pillow==10.3.0 plyfile==1.0.3 PyMCubes==0.1.4 \
  pytorch-lightning==2.2.4 PyYAML==6.0.1 safetensors==0.4.3 \
  scikit-image==0.23.2 scipy==1.13.0 tensorboardX==2.6.2.2 \
  timm==0.9.16 tqdm==4.66.2 transformers==4.40.1 trimesh==4.3.2

echo "== Download checkpoint (Seed3D/Dora-VAE-1.1, ~2.2GB) =="
mkdir -p ckpts
if [ ! -f ckpts/Dora-VAE-1.1/dora_vae_1_1.ckpt ]; then
  python download.py
fi
ls -lh ckpts/Dora-VAE-1.1/
test -f ckpts/Dora-VAE-1.1/dora_vae_1_1.ckpt

echo "== Sample data =="
SAMPLE="../sharp_edge_sampling/sample/000-152/3d8d49802bea484bbd5040c68a1aa022.npz"
test -f "$SAMPLE"
echo "using $SAMPLE"

echo "== Run inference =="
export PATH="$VENV/bin:$PATH"
bash test_autoencoder_single_gpu.sh

echo "== Done. Outputs: =="
find outputs -type f \( -name '*.obj' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \) 2>/dev/null | head -80
echo
echo "Open meshes / slices under: $PL/outputs/"
