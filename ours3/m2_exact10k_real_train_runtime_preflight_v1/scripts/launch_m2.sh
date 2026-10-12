#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
OUT="$ROOT/ours3/m2_exact10k_real_train_runtime_preflight_v1"
echo "M2 EXACT10K preflight contract: $OUT"
echo "dataset=$ROOT/ours3/clean10k_pool_merge_and_freeze_v1/EXACT10K_MANIFEST.jsonl"
echo "method=M2_ORIGINAL_CURVE context=8192 precision=bf16 micro_batch=1 grad_accum=4"
echo "curve_source=GT_BREP_ORACLE c2=FROZEN variable_k=YES k_cap=128 projector=256-256-GELU-2048"
echo "training launch is the next step; this script records the frozen launch contract"
