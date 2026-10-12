# Track A contamination audit

- files hashed (sha256): 85913
- files stat-checked: 48679

```text
TRACK_A_FILES_MODIFIED=0
TRACK_A_DATA_MODIFIED=0
TRACK_A_CONFIG_MODIFIED=0
TRACK_A_CHECKPOINT_MODIFIED=0
TRACK_A_FILES_DELETED=0
TRACK_A_FILES_ADDED=0
TRACK_A_EXTERNAL_LOG_APPENDS=0
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
