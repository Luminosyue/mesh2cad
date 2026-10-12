#!/usr/bin/env bash
# Decode each best_v2 arm from its own best-val checkpoint only.
# Usage: bash scripts/spatiallm_curve_token_v1/run_decode_heldout_best_v2.sh B0 0
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PYTHON_BIN:-/data/miniconda3/envs/spatiallm/bin/python}"
ARM="${1:?arm B0|B1n|B1b|M2}"
GPU="${2:-0}"
export CAD_HELDOUT_PROTOCOL=best_v2
export CAD_SURFACE_CACHE="$ROOT/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/surface_idx4096.npz"
export CAD_SURFACE_POINTS=4096
export DISABLE_VERSION_CHECK=1
cd "$ROOT"
CUDA_VISIBLE_DEVICES="$GPU" "$PY" "$ROOT/scripts/spatiallm_curve_token_v1/decode_heldout.py" \
  --arm "$ARM" --protocol best_v2 --max-new-tokens 4096
