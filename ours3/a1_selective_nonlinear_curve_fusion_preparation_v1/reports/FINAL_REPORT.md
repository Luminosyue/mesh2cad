# A1 Selective Nonlinear Curve Fusion Preparation V1

CURRENT_GATE = A1_SELECTIVE_CURVE_CANARY_READY

A1 is frozen as the Surface + all-LINE backbone. Only projected nonlinear candidates participate in selection; selected curves are restored to original B-Rep order. The preparation implements learned, deterministic Random-K, and Longest-K selection plus K=0 exact-prefix parity.

This remains an ORACLE_CURVE_TRACK method because it uses GT B-Rep curves. No training, VAL1000 decode, TEST1000 reuse, or holdout958 prediction was performed. Real-model canary stages are implemented but not executed.

FULL_TRAIN_READY = NO

NEXT_ALLOWED_STAGE = A1_SELECTIVE_CURVE_REAL_MODEL_CANARY_V1
