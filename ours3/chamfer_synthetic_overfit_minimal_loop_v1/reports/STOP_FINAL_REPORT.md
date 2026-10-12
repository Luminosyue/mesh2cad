# CHAMFER_SYNTHETIC_OVERFIT_MINIMAL_LOOP_V1

## Status

`STOPPED_PROVENANCE_UNRESOLVED`

This task was intentionally stopped before dataset generation, checkpoint loading, or training.

## Evidence

- Existing selection decision resolves the formal P1 checkpoint path to `/data/home/cuiyuehan/project/mesh2cad/ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000`.
- Selected step: `8000`.
- Selection rule: `MIN_VAL_BASE_CE`.
- Existing P1 provenance report records checkpoint SHA256 `9c19c36455f7be6c81e6b6d84faafb446d4d68a09fb250c062b042fb47648e08`.
- Existing P2 reconciliation/selection records the same path and step but checkpoint SHA256 `d26ff68264be7c91d1e0c25a9739899a03e9e8e37bbdf07d5002df92205c54c8`.
- The records do not state a compatible hash calculation definition that explains the discrepancy.

## Hard gates

- `SYNTHETIC64_GENERATED = NO`
- `STRICT_RELOAD_ATTEMPTED = NO`
- `TRAINING_STARTED = NO`
- `ORIGINAL_P1_MODIFIED = NO`
- `EXACT9998_MODIFIED = NO`
- `TEST1000_USED = NO`
- `HOLDOUT958_USED = NO`

The task must be resumed only after the checkpoint provenance records are reconciled and a single auditable checkpoint SHA256 is established.
