#!/usr/bin/env bash
set -euo pipefail

cd /data/home/cuiyuehan/project/mesh2cad
export CUDA_VISIBLE_DEVICES=6

while kill -0 3494270 2>/dev/null; do sleep 15; done

run_variant() {
  local output="$1"
  shift
  if [[ -f "$output/REPORT.json" ]] && grep -q '"status": "PASS"' "$output/REPORT.json"; then
    return
  fi
  python3 scripts/spatiallm_curve_token_c2_frozen_v2/decode_phase_d_variant.py \
    --arm b1 \
    --run ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/official_parent_v1/runs/b1_bm \
    --output "$output" --device cuda:0 "$@"
}

root=ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/phase_d_inference_diagnostic_v1/runs
run_variant "$root/b1_kcap_16" --k-cap 16
run_variant "$root/b1_kcap_32" --k-cap 32
run_variant "$root/b1_kcap_64" --k-cap 64
run_variant "$root/b1_zero_active" --mode zero_active
run_variant "$root/b1_drop" --mode drop

