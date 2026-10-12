# PHASE A — Original M2 split discovery

`CURRENT_GATE=BLOCKED_MISSING_ORIGINAL_SPLIT`

`TRAINING_STARTED=NO`

## Required pair

- TRAIN_CAD_COUNT == 800
- HELDOUT_CAD_COUNT == 25
- same original M2 experiment
- reuse frozen files only; no resampling

## Result

No frozen original M2 experiment contains both counts.

```
OLD_M2_TRAIN_MANIFEST=
OLD_M2_HELDOUT_MANIFEST=
TRAIN_CAD_COUNT=
HELDOUT_CAD_COUNT=
TRAIN_ID_SHA256=
HELDOUT_ID_SHA256=
```

## Closest frozen candidates (not adopted)

### 1. CADFS noisy M2-V1 lineage (placement canary actually used this)

This is the B0/M2 pair that the placement canary `M2_V1_REGRESSION` audited, and the held-out25 that the program-parameter diagnostic marked as frozen.

```
OLD_M2_TRAIN_MANIFEST=/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_overfit100_v1/CADFS_NOISY_OVERFIT100_MANIFEST.json
TRAIN_CAD_COUNT=100
TRAIN_ID_SHA256=46b71f35c57c5e8caef6df9bdc22bca092f1c89016a3d5dfb88b101682614285

OLD_M2_HELDOUT_MANIFEST=/data/home/cuiyuehan/project/mesh2cad/ours3/cadfs_noisy_heldout_pilot_v1/data/HOLDOUT_FINAL_MANIFEST.json
HELDOUT_CAD_COUNT=25
HELDOUT_ID_SHA256=2e1dc01bf4e7084b7066de986fdb37a650aa94f7069b72a6c48062c6959cdc0b

train ∩ heldout = 0
```

Fails the required TRAIN_CAD_COUNT == 800.

### 2. V3 formal SpatialLM train800 lineage

```
OLD_M2_TRAIN_MANIFEST=/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json
TRAIN_CAD_COUNT=800
TRAIN_ID_SHA256=8ffd1edba0140e7e57a58385b685d68db418063b9362383279ca0ee04c586766

DECODE_DEV50=/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_decode_dev_50.json
DECODE_DEV_COUNT=50
DECODE_DEV_ID_SHA256=8a9a8e951db8c64d483a3cbc9385d76c098375808e79dfd5085605d60438493d

PILOT_EVAL150=/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_pilot_eval_150.json
PILOT_EVAL_COUNT=150
```

Dora C2 train800 uses the same 800 CAD IDs (`ID_SHA256` match). Held-out is 50 or 150, not 25. Disjoint from CADFS heldout25.

Fails the required HELDOUT_CAD_COUNT == 25.

## Actions not taken

- no new random split
- no mix of V3 train800 with CADFS heldout25
- no subsample of decode-dev50/pilot-eval150 to 25
- no tank cases
- no descriptor generation
- no training
- no edits to frozen old experiment files

To ungate, confirm which frozen pair to reuse:

1. CADFS train100 + heldout25 (valid controlled placement vs old CADFS M2)
2. V3 train800 + decode-dev50 (valid controlled placement vs old V3 M2, but not 25)
