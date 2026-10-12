# Track A contamination audit

- files hashed (sha256): 80613
- files stat-checked: 48679

```text
TRACK_A_FILES_MODIFIED=0
TRACK_A_DATA_MODIFIED=0
TRACK_A_CONFIG_MODIFIED=0
TRACK_A_CHECKPOINT_MODIFIED=0
TRACK_A_FILES_DELETED=0
TRACK_A_FILES_ADDED=0
TRACK_A_EXTERNAL_LOG_APPENDS=3
TRACK_A_MODIFIED=False
```

`TRACK_A_CHECKPOINT_MODIFIED` counts Track A checkpoint writes attributable to
Track B. Checkpoint trees (SpatialLM/output, SpatialLM/saves) are excluded from
hashing because a Track A training job is running concurrently and rewrites them;
Track B never imports SpatialLM, runs no training or inference, and writes only
under `ours3/curve_token_data_v1/`, so it cannot reach them. The configs and the
`spatiallm` package that produce those checkpoints *are* hashed.

Result: **CLEAN** -- every Track A file that Track B could reach is
byte-identical before and after the run.

## Concurrent Track A activity (not Track B)

3 Track A log file(s) grew during the run. Each was verified to be a
**pure append**: the pre-run bytes are still an exact prefix of the file, so no
existing Track A content was rewritten. Track B writes only under
`ours3/curve_token_data_v1/` and never emits `.log` files into Track A trees.

| file | bytes appended | prefix verified |
|---|---|---|
| `cad_spatial_dataset/joint_deepcad_fusion360_v1/joint_j0_surface_v1.log` | 12481 | 472610 |
| `cad_spatial_dataset/joint_deepcad_fusion360_v1/joint_j2_sepedge_v1.log` | 3894 | 346118 |
| `cad_spatial_dataset/joint_deepcad_fusion360_v1/joint_gpu_monitor.log` | 747 | 26040 |

Track A jobs already running when Track B started (these are the writers):

- pid `682678`, running for 660s: `/data/miniconda3/envs/spatiallm/bin/python train.py configs/spatiallm_cad_joint_j2_sepedge.yaml`
- pid `682679`, running for 660s: `/data/miniconda3/envs/spatiallm/bin/python train.py configs/spatiallm_cad_joint_j2_sepedge.yaml`
- pid `1110223`, running for 6289s: `/bin/bash -O extglob -c snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap" && { builtin set +u 2>/dev/null || true; builti`
- pid `1110226`, running for 6289s: `/data/miniconda3/envs/spatiallm/bin/python train.py configs/spatiallm_cad_joint_j0_surface.yaml`
- pid `1115300`, running for 122s: `/data/miniconda3/envs/spatiallm/bin/python -u /data/home/cuiyuehan/project/mesh2cad/SpatialLM/spatiallm/tuner/trainer.py configs/spatiallm_cad_joint_j`
- pid `1115301`, running for 122s: `/data/miniconda3/envs/spatiallm/bin/python -u /data/home/cuiyuehan/project/mesh2cad/SpatialLM/spatiallm/tuner/trainer.py configs/spatiallm_cad_joint_j`
- pid `1115302`, running for 122s: `/data/miniconda3/envs/spatiallm/bin/python -u /data/home/cuiyuehan/project/mesh2cad/SpatialLM/spatiallm/tuner/trainer.py configs/spatiallm_cad_joint_j`
- pid `1115549`, running for 122s: `/data/miniconda3/envs/spatiallm/bin/python -u /data/home/cuiyuehan/project/mesh2cad/SpatialLM/spatiallm/tuner/trainer.py configs/spatiallm_cad_joint_j`
- pid `1116491`, running for 6284s: `/data/miniconda3/envs/spatiallm/bin/python /data/miniconda3/envs/spatiallm/bin/torchrun --nnodes 1 --node_rank 0 --nproc_per_node 2 --master_addr 127.`
- pid `1117884`, running for 6283s: `/data/miniconda3/envs/spatiallm/bin/python -u /data/home/cuiyuehan/project/mesh2cad/SpatialLM/spatiallm/tuner/trainer.py configs/spatiallm_cad_joint_j`
