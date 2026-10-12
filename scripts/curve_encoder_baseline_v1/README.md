# CURVE_ENCODER_BASELINE_V1

Track B / Method 2 — prove a 256-D Curve Token from 32 sampled points retains CAD geometry.

**Does not touch Track A.** Reads only `ours3/curve_token_data_v1`.

```text
curve_xyz_normalized [32,3]
curve_tangent        [32,3]   (optional)
normalized_s         [32,1]   (optional, arc-length ∈ [0,1])
        ↓
   Curve Encoder (PointNet | Transformer)
        ↓
   Curve Token [256]
        ├─ Type Head        LINE/CIRCLE/ELLIPSE/BSPLINE
        ├─ Reconstruction   → [32,3] xyz
        └─ Parameter Head   LINE/CIRCLE/ELLIPSE only (no BSPLINE CP regression)
```

## Experiments (fixed budget)

| id | encoder | features |
|----|---------|----------|
| P0 | PointNet | xyz |
| P1 | PointNet | xyz+tangent |
| P2 | PointNet | xyz+tangent+s |
| T0 | Transformer | xyz |
| T1 | Transformer | xyz+tangent |
| T2 | Transformer | xyz+tangent+s |

Contract: `points=32`, `token_dim=256`, `split=frozen_v1`, same sampler, same loss, same epochs/samples.

## Split `frozen_v1`

CAD-level freeze of `joint_deepcad_fusion360_v1` (train/val/test = 2236/280/280).

- Train: **type-aware** curve sampling (`samples_per_epoch=65536`)
- Val/Test: natural CAD curve mix (no rebalance)

## Primary metrics (NOT overall accuracy)

- Macro F1, Balanced Accuracy
- LINE / CIRCLE / ELLIPSE / BSPLINE F1
- Reconstruction Chamfer
- LINE direction error, CIRCLE normal/radius error, ELLIPSE axis error

## Run

```bash
# 1) freeze split
python3 scripts/curve_encoder_baseline_v1/make_frozen_split_v1.py

# 2) smoke (2 epochs)
CUDA_VISIBLE_DEVICES=0 /data/miniconda3/envs/spatiallm/bin/python \
  scripts/curve_encoder_baseline_v1/train.py --exp P0 --smoke

# 3) full single exp
CUDA_VISIBLE_DEVICES=0 /data/miniconda3/envs/spatiallm/bin/python \
  scripts/curve_encoder_baseline_v1/train.py --exp P1

# 4) all six
bash scripts/curve_encoder_baseline_v1/run_all.sh 0
```

Outputs: `ours3/curve_encoder_baseline_v1/runs/<EXP>_frozen_v1/{best.pt,metrics.json,scorecard.json}`
