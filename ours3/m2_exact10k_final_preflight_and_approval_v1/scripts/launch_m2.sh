#!/usr/bin/env bash
set -euo pipefail
# PREFLIGHT ONLY. Formal training is not approved.
TRAIN_MANIFEST="/data/home/cuiyuehan/project/mesh2cad/ours3/clean10k_pool_merge_and_freeze_v1/EXACT10K_TRAIN.jsonl"
VAL_MANIFEST="/data/home/cuiyuehan/project/mesh2cad/ours3/clean10k_pool_merge_and_freeze_v1/EXACT10K_VAL.jsonl"
BASE_MODEL="/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1"
CONTEXT=8192
PROJECTOR_TYPE=original_m2
[[ -f "$TRAIN_MANIFEST" && -f "$VAL_MANIFEST" && -d "$BASE_MODEL" ]]
echo "preflight paths pass; no training launched"
