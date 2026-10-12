#!/bin/bash
set -e
export CUDA_VISIBLE_DEVICES=7
export CAD_SECOND_STREAM=curve_tokens
export CAD_USE_SEPARATE_EDGE_TOKENS=1
export CURVE_TOKEN_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/exact9998_curve_tokens_c2_v1
export CURVE_TOKEN_REGISTRY=/data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl
export REQUIRE_CURVE_TOKEN_REGISTRY=1
export C2_CHECKPOINT_PATH=/data/home/cuiyuehan/project/mesh2cad/ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt
export P1_LAMBDA_OP=1.0
export P1V2_LAMBDA_SIZE=1.0
export P1_RUNTIME_STATS=/data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1/runs/size_place/runtime_stats.json
export ZERO_LR_AUDIT_PATH=/data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1/audits/ZERO_LR_size_place.json
cd /data/home/cuiyuehan/project/mesh2cad
exec /data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python /data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1/launch_size_place.py /data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1/configs_size_place.yaml
