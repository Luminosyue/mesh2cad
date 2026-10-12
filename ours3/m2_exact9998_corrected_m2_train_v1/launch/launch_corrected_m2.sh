#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
EXP="$ROOT/ours3/m2_exact9998_corrected_m2_train_v1"
export CUDA_VISIBLE_DEVICES=5
export CAD_SECOND_STREAM=curve_tokens
export CAD_USE_SEPARATE_EDGE_TOKENS=1
export CURVE_TOKEN_ROOT="$ROOT/ours3/exact9998_curve_tokens_c2_v1"
export CURVE_TOKEN_REGISTRY="$ROOT/ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"
export REQUIRE_CURVE_TOKEN_REGISTRY=1
export PYTHONUNBUFFERED=1
export DISABLE_VERSION_CHECK=1
export C2_CHECKPOINT_PATH="$ROOT/ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"
export ZERO_LR_AUDIT_PATH="$EXP/audits/CORRECTED_M2_ZERO_LR_STEP1_AUDIT.json"
export EFFECTIVE_UPDATE_AUDIT_PATH="$EXP/audits/CORRECTED_M2_FIRST_EFFECTIVE_UPDATE_AUDIT.json"
printf '%s\n' \
  'METHOD = M2_GT_BREP_CURVE_ORACLE' \
  'CURVE_STREAM = ENABLED' \
  'PROJECTOR = 256->256->GELU->2048' \
  'PROJECTOR_PARAM_N = 592128' \
  'PROJECTOR_STATE_DICT_KEY_N = 4' \
  'C2 = FROZEN' \
  'VARIABLE_K = YES' \
  'K_CAP = 128' \
  'GEOMETRY_PREFIX_ADAPTER = DISABLED' \
  'GLOBAL_STEP_START = 0' \
  'AUTO_RESUME = NO'
cd "$ROOT"
exec python3 -u "$EXP/launch/train_corrected_m2_entrypoint.py" "$EXP/configs/m2_exact9998_train.yaml"
