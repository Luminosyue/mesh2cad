# Unresolved Config Fields

- `P1_CHECKPOINT_SELECTION_PROVENANCE`: Formal closure evaluates checkpoint-39980, while its trainer_state records best_model_checkpoint=checkpoint-8000 under the frozen MIN_VAL_BASE_CE rule; no checkpoint freeze record uniquely reconciles the conflict. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `LOGIT_ABS_TOL`: No formal bf16 real-model logit parity tolerance was found; existing 1e-7 is CPU loss-path parity only. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `LOSS_ABS_TOL`: No formal bf16 real-model loss parity tolerance was found; existing 1e-7 is CPU loss-path parity only. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `GRAD_ABS_TOL`: No formal real-model backward parity absolute tolerance was found. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `GRAD_REL_TOL`: No formal real-model backward parity relative tolerance was found. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `FORWARD_PARITY_BATCH_IDS`: No pre-registered batch/case IDs were found. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `BACKWARD_PARITY_BATCH_IDS`: No pre-registered batch/case IDs were found. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `BACKWARD_PARITY_LLM_PARAMETER_NAMES`: No pre-registered LLM tensor names were found. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `SIZE_GRADIENT_BATCH_IDS`: No pre-registered batch/case IDs were found. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `STAGE_COMMANDS`: No audited real-model stage backend commands/evidence contract exists. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `OPTIMIZER_BETAS`: Not explicit in P1 frozen YAML/config; framework defaults are not admissible. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `OPTIMIZER_EPS`: Not explicit in P1 frozen YAML/config; framework defaults are not admissible. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `DATALOADER_SHUFFLE`: Not explicitly frozen. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `DROP_LAST`: Not explicitly frozen. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `DROPOUT_RNG_RESTORE_POLICY`: Not explicitly frozen. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `CURVE_K_MAX`: No unique formal frozen source was found in the supplied P1 freeze record. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `SURFACE_INPUT_SHAPE`: No unique formal frozen source was found in the supplied P1 freeze record. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
- `SURFACE_POINT_COUNT`: No unique formal frozen source was found in the supplied P1 freeze record. Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.
