#!/usr/bin/env bash
set -euo pipefail

ROOT=/data/home/cuiyuehan/project/mesh2cad
EXP="$ROOT/ours3/p1_operation_aware_structure_loss_v1"
RUN="$EXP/runs/p1"

if [ -d "$RUN" ] && [ "$(find "$RUN" -mindepth 1 -maxdepth 1 | wc -l)" -ne 0 ]; then
  echo "P1 run directory is not empty: $RUN" >&2
  exit 2
fi

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-5}"
export PYTHONUNBUFFERED=1
export DISABLE_VERSION_CHECK=1
export CAD_SECOND_STREAM=curve_tokens
export CAD_USE_SEPARATE_EDGE_TOKENS=1
export CURVE_TOKEN_ROOT="$ROOT/ours3/exact9998_curve_tokens_c2_v1"
export CURVE_TOKEN_REGISTRY="$ROOT/ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"
export REQUIRE_CURVE_TOKEN_REGISTRY=1
export C2_CHECKPOINT_PATH="$ROOT/ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"
export ZERO_LR_AUDIT_PATH="$EXP/audits/P1_ZERO_LR_STEP1_AUDIT.json"
export EFFECTIVE_UPDATE_AUDIT_PATH="$EXP/audits/P1_FIRST_EFFECTIVE_UPDATE_AUDIT.json"
export P1_LAMBDA_OP=1.0
export P1_RUNTIME_STATS="$EXP/audits/P1_RUNTIME_STATS.json"

printf '%s\n' \
  'METHOD = P1_OPERATION_AWARE_STRUCTURE_LOSS' \
  'BASE = A3_GT_BREP_CURVE_ORACLE' \
  'MODEL_ARCHITECTURE_CHANGED = NO' \
  'EXTRA_TRAINABLE_PARAMS = 0' \
  'LAMBDA_OP = 1.0' \
  'BEST_CHECKPOINT_SELECTION = MIN_VAL_BASE_CE' \
  'TEST_TOUCHED = NO' \
  'GLOBAL_STEP_START = 0' \
  'AUTO_RESUME = NO'

cd "$ROOT"
exec python3 -u "$EXP/launch/train_p1_entrypoint.py" "$EXP/configs/p1_exact9998_train.yaml"
