# P2 Size Formal Canary Runner Recovery V1

## Decision

`CURRENT_GATE = P2_REAL_MODEL_CANARY_BLOCKED`

The formal single-shot runner now exists and its static audit passes. `--help`, import/compile, explicit path resolution, and the no-model `preflight` were executed. Preflight correctly failed closed before GPU inspection or model loading because the existing frozen `P2_CANARY_CONFIG.json` does not bind all required hashes, tolerances, training hyperparameters, or per-stage execution commands.

## Required status

- CANARY_RUNNER_EXISTS = YES
- CANARY_RUNNER_STATIC_AUDIT = PASS
- PREFLIGHT = FAIL
- SAFE_GPU_FOUND = NOT_CHECKED_AFTER_PREFLIGHT_FAIL
- FORWARD_PARITY = NOT_RUN
- BACKWARD_PARITY = NOT_RUN
- SIZE_GRADIENT_EFFECT = NOT_RUN
- C2_FROZEN = NOT_RUN
- TRAIN100 = NOT_RUN
- VAL100 = NOT_RUN
- CHECKPOINT_RELOAD = NOT_RUN
- P1_CHANGED = NO
- HOLDOUT_CHANGED = NO
- HOLDOUT_PREDICTION_N = 0
- TEST_PARTIAL_METRICS_READ = NO
- FINAL_TEST_INTERFERENCE = NO
- P2_FULL_TRAIN_READY = NO

## Blocker

`FROZEN_CANARY_CONFIG_INCOMPLETE`

Missing bindings are recorded machine-readably in `runner_audit/CANARY_CONFIG_RESOLUTION.json`. They include checkpoint/C2/projector/tokenizer/manifest hashes, frozen tolerances, context length, size-field registry, safety threshold, seed and precision, TRAIN100 batch/accumulation/LR/scheduler values, and auditable stage commands/evidence paths. These values were not guessed or back-filled after inspection.

## Next allowed stage

`FREEZE_COMPLETE_P2_CANARY_CONFIG_V1`, followed by one manual `--mode preflight`. Only after PASS may a manual `--mode all` run perform its single GPU guard and enter real-model stages.
