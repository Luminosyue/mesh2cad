#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
EXP=$ROOT/ours3/m2_exact9998_surface_nonline_ablation_v1
SETUP=$ROOT/ours3/m2_exact9998_line_nonline_ablation_setup_v1
export CUDA_VISIBLE_DEVICES=${1:-4}
export DISABLE_VERSION_CHECK=1
export CAD_SECOND_STREAM=curve_tokens CAD_USE_SEPARATE_EDGE_TOKENS=1 REQUIRE_CURVE_TOKEN_REGISTRY=1
export CURVE_TOKEN_ROOT=$ROOT/ours3/exact9998_curve_tokens_c2_v1
export CURVE_TOKEN_REGISTRY=$ROOT/ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl
export CURVE_ABLATION_ARM=nonline CURVE_ABLATION_VIEW=$SETUP/A2_NONLINE_CURVE_VIEW.jsonl
export C2_CHECKPOINT_PATH=$ROOT/ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt
export ZERO_LR_AUDIT_PATH=$EXP/audits/A2_ZERO_LR_STEP1_AUDIT.json
export EFFECTIVE_UPDATE_AUDIT_PATH=$EXP/audits/A2_FIRST_EFFECTIVE_UPDATE_AUDIT.json
export EFFECTIVE_UPDATE_PENDING_PATH=$EXP/audits/A2_FIRST_EFFECTIVE_UPDATE_PENDING.json
test -z "$(find "$EXP/runs/a2" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)"
nohup python3 -u "$EXP/launch/train_entrypoint.py" "$EXP/configs/a2_exact9998_train.yaml" > "$EXP/logs/a2_train.log" 2>&1 &
echo $! > "$EXP/launch/train.pid"
