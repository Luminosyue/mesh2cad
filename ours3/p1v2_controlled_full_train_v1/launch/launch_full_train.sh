#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
EXP=$ROOT/ours3/p1v2_controlled_full_train_v1
export CUDA_VISIBLE_DEVICES=3
export PYTHONUNBUFFERED=1
export PYTHONNOUSERSITE=1
export DISABLE_VERSION_CHECK=1
export CAD_SECOND_STREAM=curve_tokens
export CAD_USE_SEPARATE_EDGE_TOKENS=1
export CURVE_TOKEN_ROOT=$ROOT/ours3/exact9998_curve_tokens_c2_v1
export CURVE_TOKEN_REGISTRY=$ROOT/ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl
export REQUIRE_CURVE_TOKEN_REGISTRY=1
export CURVE_ABLATION_ARM=line
export CURVE_ABLATION_VIEW=$ROOT/ours3/m2_exact9998_line_nonline_ablation_setup_v1/A1_LINE_CURVE_VIEW.jsonl
export C2_CHECKPOINT_PATH=$ROOT/ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt
export P1_LAMBDA_OP=0.5
export P1_RUNTIME_STATS=$EXP/audits/P1_RUNTIME_STATS.json
export ZERO_LR_AUDIT_PATH=$EXP/audits/ZERO_LR_STEP1_AUDIT.json
export EFFECTIVE_UPDATE_AUDIT_PATH=$EXP/audits/FIRST_EFFECTIVE_UPDATE_AUDIT.json
export EFFECTIVE_UPDATE_PENDING_PATH=$EXP/audits/FIRST_EFFECTIVE_UPDATE_PENDING.json
cd $ROOT
exec /data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python -u $EXP/launch/train_entrypoint.py $EXP/configs/p1v2_exact9998_train.yaml
