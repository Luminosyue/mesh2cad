#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/home/cuiyuehan/project/mesh2cad
EXP=$ROOT/ours3/m2_exact9998_surface_nonline_ablation_v1
CK=$EXP/runs/a2/checkpoint-250
while [ ! -f "$CK/model.safetensors.index.json" ] || [ ! -f "$CK/optimizer.pt" ] || [ ! -f "$CK/rng_state.pth" ]; do sleep 20; done
DISABLE_VERSION_CHECK=1 python3 "$EXP/launch/audit_checkpoint250.py" > "$EXP/logs/checkpoint250_audit.log" 2>&1
